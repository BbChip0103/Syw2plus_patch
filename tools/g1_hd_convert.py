"""Check and convert HD pictures for the G1 HD picture path (H-HDX2).

Works against an extraction directory made by ``tools/g1_hd_extract.py`` (the
reference): ``<ref>/<rel>/<NNNN>.png`` (1x index, transparent 254),
``<NNNN>_mask.png`` (1 = opaque) and ``<NNNN>_2x.png`` (Scale2x draft).
HD pictures live at ``<hd>/<rel>/<NNNN>.png`` and must be 8-bit index PNGs with the
``imjin2.pal x4`` palette, exactly 2w x 2h, transparent index 254, silhouette equal to
the reference mask doubled, and team colours 236..239 only inside the 2x2 footprint
of the reference team pixels.

- ``check``: report violations per frame (RGB input is classified ``needs_convert``).
- ``convert``: RGB/RGBA PNGs (an upscaler result) -> nearest-palette index PNGs with
  the silhouette and team footprint forced from the reference.  Ties (the palette has
  equal-RGB entries) resolve to the reference draft index if it is among the nearest,
  else the smallest index.  Sizes are never resized.
- ``draft``: conforming 2x drafts (Scale2x with the team footprint made exact) as an ``hd/`` tree.
- ``panel-idx8``: headerless 2w x 2h byte file of one HD panel frame (key 0xFE); only the first 800 source columns
  are kept because the engine consumes 800 of the 831 (``g1_panel_fold_frame``), so the pack is 1600 x 2h.
- ``pack``: engine pointer-free pack ``h<digest8>_<w>x<h>.idx8`` (2w x 2h bytes, key 0xFE) for every RLE ``.spr`` frame;
  ``digest8`` = FNV-1a of the 128 bytes at the frame's stream start in the original file, the engine's ledger digest.
  A name two different pictures map to is written to ``digest_index.json`` ``conflicts`` and never to the pack.
- ``fullscreen``: whole-screen raw ``.spr`` (file size == header + fw*fh*frames, e.g. ``yfnt/title.spr``) -> ``f<digest8>_<w>x<h>.idx8``
  (2w x 2h bytes), ``digest8`` = FNV-1a of every 1x byte of the frame, the engine's menu block-copy hash.  The picture is
  opaque: every pixel is quantized to the nearest palette entry except the key 0xFE; an upscaler RGB result (``--rgb``) or,
  without one, a bicubic stand-in is used.
- ``logo``: the unframed single-picture RLE ``.spr`` (header frame count 0, e.g. ``fnt/imjin2plus.spr``, the HUD logo
  ``0x4672E0`` draws at 50 %) -> ``h<digest8>_<w>x<h>.idx8`` with the engine's name rule; the stream is read the way the
  writer reads it (a row ends when its column reaches the width) and must be consumed exactly.  The silhouette is forced
  from the stream; ``--rgb`` is an upscaler result, else a bicubic stand-in.
The game folder and the repository are read-only: outputs inside them are refused.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import g1_hd_extract as hx  # noqa: E402

TRANSPARENT = hx.TRANSPARENT
TEAM_LOW, TEAM_HIGH = hx.TEAM_LOW, hx.TEAM_HIGH
FRAME_RE = re.compile(r"^(\d{4})\.png$")
VIOLATION_KINDS = ("size", "palette", "transparency", "silhouette", "team_leak", "team_missing", "no_reference")
_ALL = np.arange(256)
_TEAM_IDX = np.arange(TEAM_LOW, TEAM_HIGH + 1)
_PLAIN_IDX = np.array([i for i in range(256) if not TEAM_LOW <= i <= TEAM_HIGH and i != TRANSPARENT])


class ConvertError(Exception):
    """A frame cannot be converted or compared (missing reference, wrong size)."""


@dataclass
class RefFrame:
    idx: np.ndarray       # (h, w) uint8 1x index
    opaque: np.ndarray    # (h, w) bool
    draft: np.ndarray     # (2h, 2w) uint8 Scale2x draft index

    @property
    def silhouette2x(self) -> np.ndarray:
        return _double(self.opaque)

    @property
    def footprint(self) -> np.ndarray:
        return _double(self.opaque & (self.idx >= TEAM_LOW) & (self.idx <= TEAM_HIGH))

    @property
    def team_safe_draft(self) -> np.ndarray:
        """Scale2x draft with the team footprint made exact.

        Plain Scale2x lets a team value leak onto neighbouring blocks and lets neighbours
        overwrite team blocks (12,191 of 37,905 extracted drafts break the footprint rule),
        so team blocks are filled with the source pixel and team values elsewhere are
        replaced by the source pixel of their own block.
        """
        nearest = _double(self.idx)
        team_value = (self.draft >= TEAM_LOW) & (self.draft <= TEAM_HIGH)
        fix = self.footprint | (team_value & ~self.footprint)
        return np.where(fix & self.silhouette2x, nearest, self.draft).astype(np.uint8)


def _double(arr: np.ndarray) -> np.ndarray:
    return np.repeat(np.repeat(arr, 2, axis=0), 2, axis=1)


def load_ref_png(path: Path) -> RefFrame:
    """Load a reference frame from its 1x index PNG and sibling ``_mask``/``_2x`` files."""
    stem = path.with_suffix("")
    for needed in (path, Path(f"{stem}_mask.png"), Path(f"{stem}_2x.png")):
        if not needed.is_file():
            raise ConvertError(f"missing reference file {needed}")
    with Image.open(path) as img:
        idx = np.array(img.convert("P") if img.mode != "P" else img, dtype=np.uint8)
    with Image.open(f"{stem}_mask.png") as img:
        opaque = np.array(img.convert("L")) > 0
    with Image.open(f"{stem}_2x.png") as img:
        draft = np.array(img.convert("P") if img.mode != "P" else img, dtype=np.uint8)
    if opaque.shape != idx.shape or draft.shape != (idx.shape[0] * 2, idx.shape[1] * 2):
        raise ConvertError(f"reference files disagree on size: {path}")
    return RefFrame(idx, opaque, draft)


def load_ref(ref_dir: Path, rel: str, frame: str) -> RefFrame:
    return load_ref_png(ref_dir / rel / f"{frame}.png")


# --- check -------------------------------------------------------------------

def _transparency_ok(info: dict[str, Any]) -> bool:
    """tRNS must make exactly index 254 fully transparent and nothing else."""
    trns = info.get("transparency")
    if trns is None:
        return False
    if isinstance(trns, int):
        return trns == TRANSPARENT
    alpha = bytes(trns)
    return len(alpha) > TRANSPARENT and alpha[TRANSPARENT] == 0 and all(
        a == 255 for i, a in enumerate(alpha) if i != TRANSPARENT)


def check_image(img: Image.Image, ref: RefFrame, palette: np.ndarray) -> dict[str, int]:
    """Violation counts for one opened HD picture (0 everywhere = conforming)."""
    found = dict.fromkeys(VIOLATION_KINDS, 0)
    h, w = ref.idx.shape
    if img.mode != "P":
        return {"needs_convert": 1, **found}
    if img.size != (2 * w, 2 * h):
        found["size"] = 1
    pal = img.getpalette() or []
    if np.array(pal[:768] + [0] * (768 - len(pal[:768])), dtype=np.uint8).tolist() != palette.ravel().tolist():
        found["palette"] = 1
    if not _transparency_ok(img.info):
        found["transparency"] = 1
    if found["size"]:
        return {"needs_convert": 0, **found}
    idx = np.array(img, dtype=np.uint8)
    opaque = idx != TRANSPARENT
    found["silhouette"] = int((opaque != ref.silhouette2x).sum())
    team = opaque & (idx >= TEAM_LOW) & (idx <= TEAM_HIGH)
    foot = ref.footprint
    found["team_leak"] = int((team & ~foot).sum())
    found["team_missing"] = int((foot & ~team).sum())
    return {"needs_convert": 0, **found}


def check_dir(hd_dir: Path, ref_dir: Path, palette: np.ndarray, fail_limit: int = 200) -> dict[str, Any]:
    totals = dict.fromkeys(VIOLATION_KINDS, 0)
    frames = ok = needs_convert = ignored = 0
    failing: list[dict[str, Any]] = []
    failing_frames = 0
    for path in sorted(p for p in hd_dir.rglob("*") if p.is_file()):
        match = FRAME_RE.match(path.name)
        if not match:
            ignored += 1
            continue
        rel = path.parent.relative_to(hd_dir).as_posix()
        frames += 1
        try:
            ref = load_ref(ref_dir, rel, match.group(1))
        except ConvertError:
            counts = {"needs_convert": 0, **dict.fromkeys(VIOLATION_KINDS, 0), "no_reference": 1}
        else:
            with Image.open(path) as img:
                counts = check_image(img, ref, palette)
        needs_convert += counts["needs_convert"]
        bad = {k: counts[k] for k in VIOLATION_KINDS if counts.get(k)}
        for kind, n in bad.items():
            totals[kind] += n
        if counts["needs_convert"]:
            if len(failing) < fail_limit:
                failing.append({"path": f"{rel}/{path.name}", "needs_convert": True})
        elif bad:
            failing_frames += 1
            if len(failing) < fail_limit:
                failing.append({"path": f"{rel}/{path.name}", **bad})
        else:
            ok += 1
    return {"tool": "g1_hd_convert", "cmd": "check", "frames": frames, "ok_frames": ok,
            "needs_convert_frames": needs_convert, "violating_frames": failing_frames,
            "violation_totals": totals, "violations": sum(totals.values()), "ignored_files": ignored,
            "failing_sample": failing, "pass": frames > 0 and ok == frames}


# --- convert -----------------------------------------------------------------

def _nearest_group(rgb: np.ndarray, cand: np.ndarray, palette: np.ndarray,
                   draft: np.ndarray) -> tuple[np.ndarray, int, int]:
    """Quantize pixels (n,3) to ``cand`` palette indices; returns (index, tie_pixels, tie_by_draft)."""
    packed = (rgb[:, 0].astype(np.uint32) << 16) | (rgb[:, 1].astype(np.uint32) << 8) | rgb[:, 2]
    uniq, first_pos, inverse = np.unique(packed, return_index=True, return_inverse=True)
    colors = rgb[first_pos].astype(np.int32)
    dist = ((colors[:, None, :] - palette[cand].astype(np.int32)[None, :, :]) ** 2).sum(axis=2)
    tie = dist == dist.min(axis=1)[:, None]
    smallest = cand[np.argmax(tie, axis=1)]
    lookup: np.ndarray = np.full(256, -1, dtype=np.int32)
    lookup[cand] = np.arange(cand.size)
    pos = lookup[draft]
    in_tie = (pos >= 0) & tie[inverse, np.where(pos >= 0, pos, 0)]
    out = np.where(in_tie, draft, smallest[inverse]).astype(np.uint8)
    multi = tie.sum(axis=1)[inverse] > 1
    return out, int(multi.sum()), int((multi & in_tie).sum())


def quantize(rgb: np.ndarray, ref: RefFrame, palette: np.ndarray) -> tuple[np.ndarray, dict[str, int]]:
    """RGB (2h,2w,3) -> index (2h,2w) honouring the reference silhouette and team footprint."""
    h, w = ref.idx.shape
    if rgb.shape != (2 * h, 2 * w, 3):
        raise ConvertError(f"size {rgb.shape[1]}x{rgb.shape[0]} != required {2 * w}x{2 * h}")
    sil, foot, safe = ref.silhouette2x, ref.footprint, ref.team_safe_draft
    out = np.full((2 * h, 2 * w), TRANSPARENT, dtype=np.uint8)
    stats = {"pixels": int(sil.sum()), "tie_pixels": 0, "tie_resolved_by_draft": 0}
    for sel, cand in ((foot, _TEAM_IDX), (sil & ~foot, _PLAIN_IDX)):
        if not sel.any():
            continue
        out[sel], ties, by_draft = _nearest_group(rgb[sel], cand, palette, safe[sel])
        stats["tie_pixels"] += ties
        stats["tie_resolved_by_draft"] += by_draft
    return out, stats


def load_rgb(path: Path) -> np.ndarray:
    with Image.open(path) as img:
        return np.array(img.convert("RGB"), dtype=np.uint8)


def _assert_outputs_safe(out: Path, game: Path, *others: Path) -> None:
    hx._assert_outside(out, game, REPO)
    out_r = out.resolve()
    for other in others:
        other_r = other.resolve()
        if out_r == other_r or other_r in out_r.parents:
            raise SystemExit(f"output {out_r} must not be inside input {other_r}")


def convert_dir(rgb_dir: Path, ref_dir: Path, out_dir: Path, palette: np.ndarray, game: Path) -> dict[str, Any]:
    _assert_outputs_safe(out_dir, game, rgb_dir, ref_dir)
    frames = converted = ignored = 0
    ties = by_draft = pixels = 0
    errors: list[dict[str, str]] = []
    for path in sorted(p for p in rgb_dir.rglob("*") if p.is_file()):
        match = FRAME_RE.match(path.name)
        if not match:
            ignored += 1
            continue
        rel = path.parent.relative_to(rgb_dir).as_posix()
        frames += 1
        try:
            ref = load_ref(ref_dir, rel, match.group(1))
            idx, stats = quantize(load_rgb(path), ref, palette)
        except ConvertError as exc:
            errors.append({"path": f"{rel}/{path.name}", "error": str(exc)})
            continue
        hx.save_index_png(out_dir / rel / path.name, idx, palette)
        converted += 1
        pixels += stats["pixels"]
        ties += stats["tie_pixels"]
        by_draft += stats["tie_resolved_by_draft"]
    return {"tool": "g1_hd_convert", "cmd": "convert", "frames": frames, "converted": converted,
            "errors": errors, "ignored_files": ignored, "opaque_pixels": pixels,
            "tie_pixels": ties, "tie_resolved_by_draft": by_draft, "pass": frames > 0 and not errors}


def draft_dir(ref_dir: Path, out_dir: Path, palette: np.ndarray, game: Path) -> dict[str, Any]:
    """Write the conforming team-safe 2x drafts as an ``hd/`` tree (a valid starting point per frame)."""
    _assert_outputs_safe(out_dir, game, ref_dir)
    frames = 0
    for path in sorted(p for p in ref_dir.rglob("*.png") if FRAME_RE.match(p.name)):
        ref = load_ref_png(path)
        hx.save_index_png(out_dir / path.parent.relative_to(ref_dir) / path.name, ref.team_safe_draft, palette)
        frames += 1
    return {"tool": "g1_hd_convert", "cmd": "draft", "frames": frames, "pass": frames > 0}


# --- panel .idx8 -------------------------------------------------------------

PANEL_ENGINE_WIDTH = 800   # G1_PANEL_WIDTH: the engine reads 800 of the 831 source columns

def panel_idx8(hd_png: Path, ref_png: Path, out: Path, palette: np.ndarray, game: Path) -> dict[str, Any]:
    _assert_outputs_safe(out, game)
    ref = load_ref_png(ref_png)
    with Image.open(hd_png) as img:
        counts = check_image(img, ref, palette)
        if counts["needs_convert"] or any(counts[k] for k in VIOLATION_KINDS):
            raise SystemExit(f"{hd_png} does not conform: {counts}")
        body = np.array(img, dtype=np.uint8)[:, : 2 * PANEL_ENGINE_WIDTH].tobytes()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body)
    h, w = ref.idx.shape
    return {"tool": "g1_hd_convert", "cmd": "panel-idx8", "width": 2 * min(w, PANEL_ENGINE_WIDTH), "height": 2 * h,
            "source_width": w, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), "key": TRANSPARENT, "pass": True}


# --- pointer-free pack (H-HDL1) -------------------------------------------------

DIGEST_BYTES = 128   # g1_hd_asset.c G1_HD_DIGEST_BYTES


def fnv1a_128(data: bytes, offset: int) -> int | None:
    """Engine ledger digest of the 128 bytes at ``offset``; None if they run past the end of the file."""
    window = data[offset:offset + DIGEST_BYTES]
    if len(window) < DIGEST_BYTES:
        return None
    value = 2166136261
    for byte in window:
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return value


PANEL_SOURCE_WIDTH = 831   # the HUD panels: own writer 0x4663E0, own key and 800-column pack (g1_panel_layer.h)


def pack_name(digest: int, width: int, height: int) -> str:
    """Same text as ``g1_hd_pack_name`` (g1_hd_pack.h); 831-wide panels use ``g1_panel_asset_key`` (g1_panel_layer.h)."""
    if width == PANEL_SOURCE_WIDTH:
        return f"w004663e0_h{digest:08x}_{width}x{height}.idx8"
    return f"h{digest:08x}_{width}x{height}.idx8"


EXT_MIN = 129          # g1_hd_pack.h G1_HD_PACK_EXT_MIN: a prefix longer than the 128 digest bytes
EXT_MAX = 65536        # G1_HD_PACK_EXT_MAX
EXT_START = 256


def ext_candidates(shortest: int) -> list[int]:
    """Prefix lengths tried in order: 256, 512, ... while they fit every member's stream, then the shortest range itself."""
    out = []
    length = EXT_START
    while length <= min(shortest, EXT_MAX):
        out.append(length)
        length *= 2
    if EXT_MIN <= shortest <= EXT_MAX and shortest not in out:
        out.append(shortest)
    return out


def fnv1a_prefixes(data: bytes, offset: int, lengths: list[int]) -> dict[int, int]:
    """FNV-1a of the first ``length`` stream bytes for each requested length (one pass over the longest)."""
    wanted = set(lengths)
    value = 2166136261
    out: dict[int, int] = {}
    for count, byte in enumerate(data[offset:offset + max(lengths)], 1):
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
        if count in wanted:
            out[count] = value
    return out


def stream_ranges(offsets: list[int], size: int) -> dict[int, int]:
    """Bytes from each stream start to the next distinct start (or the end of the file)."""
    ordered = sorted(set(offsets))
    return {start: (ordered[k + 1] if k + 1 < len(ordered) else size) - start for k, start in enumerate(ordered)}


def marker_name(digest: int, width: int, height: int) -> str:
    """Same text as ``g1_hd_pack_marker_name`` (g1_hd_pack.h)."""
    return pack_name(digest, width, height)[:-len(".idx8")] + ".amb"


def ext_pack_name(digest: int, width: int, height: int, length: int, prefix_hash: int) -> str:
    """Same text as ``g1_hd_pack_ext_name`` (g1_hd_pack.h)."""
    return f"{pack_name(digest, width, height)[:-len('.idx8')]}_{length}_{prefix_hash:08x}.idx8"


def spr_stream_offsets(data: bytes, frame_count: int) -> list[int]:
    """File offset of each frame's stream (the pointer the engine passes to the RLE writers)."""
    table = list(struct.unpack_from("<299I", data, hx.SPR_OFFSET_TABLE))[: frame_count - 1]
    return [hx.SPR_FIXED_HEADER + o for o in [0, *table]]


def ytl_stream_offsets(data: bytes, frame_count: int) -> list[int]:
    """File offset of each ``.ytl`` frame's scanline records (the pointer the terrain writers receive)."""
    return [hx.SPR_FIXED_HEADER + o for o in struct.unpack_from(f"<{frame_count}I", data, hx.YTL_OFFSET_TABLE)]


def ytl_widest(data: bytes, offset: int, rows: int) -> int | None:
    """Width ``rle_dimensions`` (g1_mirror2x.c) derives for ``0x468C30``: the widest ``skip + count`` over ``rows`` records."""
    widest = 0
    for _ in range(rows):
        if offset + 2 > len(data):
            return None
        end = data[offset] + data[offset + 1]
        widest = max(widest, end)
        offset += 2 + data[offset + 1]
    return widest


# --- whole-screen raw pictures (H-HDF0) -----------------------------------------

def fnv1a_all(data: bytes) -> int:
    """Engine menu block-copy hash (``transfer_block_copy_to_screen``): FNV-1a over every 1x byte of the frame."""
    value = 2166136261
    for byte in data:
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return value


def fullscreen_name(digest: int, width: int, height: int) -> str:
    """Same text as ``g1_hd_pack_fullscreen_name`` (g1_hd_pack.h)."""
    return f"f{digest:08x}_{width}x{height}.idx8"


def _nearest_opaque(rgb: np.ndarray, palette: np.ndarray, chunk: int = 16384) -> np.ndarray:
    """Nearest palette index per RGB pixel (n,3), never the transparent key; ties take the smallest index."""
    cand = np.array([i for i in range(256) if i != TRANSPARENT])
    pal = palette[cand].astype(np.int32)
    out: np.ndarray = np.empty(len(rgb), dtype=np.uint8)
    for start in range(0, len(rgb), chunk):
        part: np.ndarray = rgb[start:start + chunk].astype(np.int32)
        dist = ((part[:, None, :] - pal[None, :, :]) ** 2).sum(axis=2)
        out[start:start + chunk] = cand[dist.argmin(axis=1)]
    return out


def palette_pal8(palette: np.ndarray) -> str:
    """``pal8`` of ``g1_hd_pack_format_pal``: FNV-1a over the 768 R,G,B bytes of the 256 PALETTEENTRYs (6-bit file value << 2)."""
    value = 2166136261
    for byte in palette.astype(np.uint8).tobytes():
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return f"{value:08x}"


def fullscreen_pack(spr: Path, rgb_png: Path | None, out_dir: Path, palette: np.ndarray, game: Path) -> dict[str, Any]:
    _assert_outputs_safe(out_dir, game, *([rgb_png] if rgb_png else []))
    data = spr.read_bytes()
    try:
        fw, fh, fc, _, _, _ = hx._spr_header(data)
    except hx.AssetError as error:
        raise SystemExit(f"{spr}: {error}") from error
    total = fw * fh
    if len(data) != hx.SPR_FIXED_HEADER + total * fc:
        raise SystemExit(f"{spr} is not a raw whole-screen picture (size {len(data)} != header + {fw}x{fh}x{fc})")
    if fw > 800 or fh > 600:
        raise SystemExit(f"{spr}: {fw}x{fh} is larger than the engine screen")
    if rgb_png is not None and fc != 1:
        raise SystemExit("--rgb replaces one frame; the file has several")
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for i in range(fc):
        pixels = data[hx.SPR_FIXED_HEADER + i * total:hx.SPR_FIXED_HEADER + (i + 1) * total]
        idx = np.frombuffer(pixels, dtype=np.uint8).reshape(fh, fw)
        if rgb_png is not None:
            hd_rgb = load_rgb(rgb_png)
            if hd_rgb.shape[:2] != (2 * fh, 2 * fw):
                raise SystemExit(f"{rgb_png} is {hd_rgb.shape[1]}x{hd_rgb.shape[0]}, expected {2 * fw}x{2 * fh}")
        else:
            big = Image.fromarray(palette[idx], "RGB").resize((2 * fw, 2 * fh), Image.BICUBIC)
            hd_rgb = np.array(big, dtype=np.uint8)
        body = _nearest_opaque(hd_rgb.reshape(-1, 3), palette).tobytes()
        name = fullscreen_name(fnv1a_all(pixels), fw, fh)
        (out_dir / name).write_bytes(body)
        frames.append({"name": name, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                       "source": "rgb" if rgb_png is not None else "bicubic"})
    return {"tool": "g1_hd_convert", "cmd": "fullscreen", "file": spr.name, "width": 2 * fw, "height": 2 * fh,
            "frames": frames, "key": TRANSPARENT, "pass": True}


def decode_unframed_rle(data: bytes) -> tuple[int, int, np.ndarray, np.ndarray]:
    """Header frame count 0 + one RLE stream at 0xBF4, read like ``0x4672E0``: rows end by width, ``FE n`` skips n columns."""
    if len(data) <= hx.SPR_FIXED_HEADER:
        raise SystemExit("no stream behind the header")
    version, fw, fh, fc = struct.unpack_from("<4I", data, 0)
    if version != 9 or fc != 0 or not 0 < fw <= 800 or not 0 < fh <= 600:
        raise SystemExit(f"not an unframed RLE picture: version={version} {fw}x{fh} fc={fc}")
    stream = data[hx.SPR_FIXED_HEADER:]
    idx: np.ndarray = np.zeros((fh, fw), dtype=np.uint8)
    opaque: np.ndarray = np.zeros((fh, fw), dtype=bool)
    pos = 0
    for row in range(fh):
        col = 0
        while col < fw:
            if pos >= len(stream) or (stream[pos] == hx.RLE_MARKER and pos + 1 >= len(stream)):
                raise SystemExit("stream ends before the last row")
            if stream[pos] == hx.RLE_MARKER:
                col += stream[pos + 1]
                pos += 2
            else:
                idx[row, col] = stream[pos]
                opaque[row, col] = True
                col += 1
                pos += 1
    if pos != len(stream):
        raise SystemExit(f"{len(stream) - pos} stream bytes left after the last row")
    return fw, fh, idx, opaque


def logo_pack(spr: Path, rgb_png: Path | None, out_dir: Path, palette: np.ndarray, game: Path) -> dict[str, Any]:
    _assert_outputs_safe(out_dir, game, *([rgb_png] if rgb_png else []))
    data = spr.read_bytes()
    fw, fh, idx, opaque = decode_unframed_rle(data)
    digest = fnv1a_128(data, hx.SPR_FIXED_HEADER)
    if digest is None:
        raise SystemExit(f"{spr}: the stream is shorter than the {DIGEST_BYTES} digest bytes")
    if rgb_png is not None:
        hd_rgb = load_rgb(rgb_png)
        if hd_rgb.shape[:2] != (2 * fh, 2 * fw):
            raise SystemExit(f"{rgb_png} is {hd_rgb.shape[1]}x{hd_rgb.shape[0]}, expected {2 * fw}x{2 * fh}")
    else:
        hd_rgb = np.array(Image.fromarray(palette[idx], "RGB").resize((2 * fw, 2 * fh), Image.BICUBIC), dtype=np.uint8)
    hd_idx = _nearest_opaque(hd_rgb.reshape(-1, 3), palette).reshape(2 * fh, 2 * fw)
    body = np.where(_double(opaque), hd_idx, TRANSPARENT).astype(np.uint8).tobytes()
    name = pack_name(digest, fw, fh)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / name).write_bytes(body)
    return {"tool": "g1_hd_convert", "cmd": "logo", "file": spr.name, "name": name, "digest": f"{digest:08x}",
            "width": fw, "height": fh, "opaque_pixels": int(opaque.sum()), "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(), "source": "rgb" if rgb_png is not None else "bicubic",
            "key": TRANSPARENT, "pass": True}


def _split_by_prefix(game: Path, names: dict[str, dict[str, Any]], members: dict[str, list[tuple[str, int, int, int, str]]]
                     ) -> dict[str, tuple[int, dict[str, tuple[str, list[list[Any]]]]]]:
    """For every 1x-picture conflict name the smallest prefix length that gives each picture its own FNV-1a, with the
    members of each hash as ``{p8: (picture, [[rel, frame], ...])}``.  Names no length separates are left out."""
    wanted: dict[str, list[int]] = {}
    for name, entry in names.items():
        if len(entry["sources"]) < 2 or name.startswith("w"):
            continue                                       # 831-wide panels keep their own key
        shortest = min(m[3] for m in members[name])
        if ext_candidates(shortest):
            wanted[name] = ext_candidates(shortest)
    by_file: dict[str, list[tuple[str, tuple[str, int, int, int, str]]]] = {}
    for name in wanted:
        for member in members[name]:
            by_file.setdefault(member[0], []).append((name, member))
    hashes: dict[tuple[str, str, int], dict[int, int]] = {}
    for rel, items in by_file.items():
        data = (game / rel).read_bytes()
        for name, member in items:
            hashes[(name, rel, member[1])] = fnv1a_prefixes(data, member[2], wanted[name])
    out: dict[str, tuple[int, dict[str, tuple[str, list[list[Any]]]]]] = {}
    for name, lengths in wanted.items():
        for length in lengths:
            groups: dict[int, dict[str, list[list[Any]]]] = {}
            for rel, frame, _, _, picture in members[name]:
                groups.setdefault(hashes[(name, rel, frame)][length], {}).setdefault(picture, []).append([rel, frame])
            if all(len(pictures) == 1 for pictures in groups.values()):
                out[name] = (length, {f"{h:08x}": next(iter(p.items())) for h, p in groups.items()})
                break
    return out


def pack_dir(game: Path, out_dir: Path, image_dirs: tuple[str, ...], hd_dir: Path | None, ref_dir: Path | None,
             palette: np.ndarray, dry_run: bool) -> dict[str, Any]:
    """Name every RLE ``.spr`` and ``.ytl`` frame; with ``hd_dir`` also write the conflict-free HD frames into ``out_dir``.

    A name is a conflict when its frames disagree in 1x picture (all frames take part, with or without an HD
    picture) or in HD picture (frames that have one).  Conflict names are only listed in ``digest_index.json``,
    except a 1x-picture conflict some prefix length L (H-HDN0) tells apart: that name gets the marker
    ``h<d8>_<w>x<h>.amb`` (L, 4 bytes LE) and each picture's HD frame as ``h<d8>_<w>x<h>_<L>_<p8>.idx8``,
    p8 = FNV-1a of the first L stream bytes.  L is the smallest of 256, 512, ... and the shortest member stream.
    """
    _assert_outputs_safe(out_dir, game, *([hd_dir] if hd_dir else []), *([ref_dir] if ref_dir else []))
    names: dict[str, dict[str, Any]] = {}
    stats = {"files": 0, "frames": 0, "named": 0, "not_rle": 0, "unsupported": 0, "tail_short": 0, "no_hd": 0,
             "no_reference": 0, "nonconforming": 0, "ytl_frames": 0, "ytl_narrow": 0}
    roots = tuple(d.lower() for d in image_dirs)
    members: dict[str, list[tuple[str, int, int, int, str]]] = {}   # name -> (rel, frame, stream offset, range, picture)
    for path in hx.iter_assets(game):
        rel = path.relative_to(game).as_posix()
        suffix = path.suffix.lower()
        if suffix not in (".spr", ".ytl") or rel.split("/", 1)[0].lower() not in roots:
            continue
        stats["files"] += 1
        data = path.read_bytes()
        try:
            dec = hx.decode_ytl(data) if suffix == ".ytl" else hx.decode_spr(data)
        except hx.AssetError:
            stats["unsupported"] += 1
            continue
        if dec.kind not in ("rle", "ytl"):
            stats["not_rle"] += len(dec.idx)
            continue
        offsets = (ytl_stream_offsets if dec.kind == "ytl" else spr_stream_offsets)(data, len(dec.idx))
        ranges = stream_ranges(offsets, len(data))
        for i, offset in enumerate(offsets):
            stats["frames"] += 1
            digest = fnv1a_128(data, offset)
            if digest is None:
                stats["tail_short"] += 1
                continue
            h, w = dec.idx[i].shape
            if dec.kind == "ytl":
                stats["ytl_frames"] += 1
                stats["ytl_narrow"] += ytl_widest(data, offset, h) != w   # 0x468C30 would key these at a narrower width
            name = pack_name(digest, w, h)
            entry = names.setdefault(name, {"sources": {}, "hd": {}, "refs": []})
            source = hashlib.sha256(np.where(dec.opaque[i], dec.idx[i], TRANSPARENT).astype(np.uint8).tobytes()).hexdigest()
            entry["sources"].setdefault(source, []).append([rel, i])
            members.setdefault(name, []).append((rel, i, offset, ranges[offset], source))
            stats["named"] += 1
            if hd_dir is None:
                continue
            hd_png = hd_dir / rel / f"{i:04d}.png"
            if not hd_png.is_file():
                stats["no_hd"] += 1
                continue
            try:
                ref = load_ref(ref_dir, rel, f"{i:04d}") if ref_dir else None
            except ConvertError:
                ref = None
            if ref is None:
                stats["no_reference"] += 1
                continue
            with Image.open(hd_png) as img:
                counts = check_image(img, ref, palette)
                if counts["needs_convert"] or any(counts[k] for k in VIOLATION_KINDS):
                    stats["nonconforming"] += 1
                    continue
                pixels = np.array(img, dtype=np.uint8)
                body = (pixels[:, : 2 * PANEL_ENGINE_WIDTH] if w == PANEL_SOURCE_WIDTH else pixels).tobytes()
            entry["hd"].setdefault(hashlib.sha256(body).hexdigest(), (body, []))[1].append([rel, i])
    index: dict[str, list[list[Any]]] = {}
    conflicts: dict[str, dict[str, list[list[Any]]]] = {}
    extended: dict[str, dict[str, Any]] = {}
    ext_frames = ext_files = 0
    written = 0
    ext_split = _split_by_prefix(game, names, members)
    for name, entry in sorted(names.items()):
        if len(entry["sources"]) > 1:
            split = ext_split.get(name)
            if split is None:
                conflicts[name] = {c[:8]: refs for c, refs in entry["sources"].items()}
                continue
            length, groups = split
            hd_of = {(r, f): (body, h) for h, (body, refs) in entry["hd"].items() for r, f in refs}
            record: dict[str, Any] = {"length": length, "pictures": {}}
            wrote_marker = False
            for p8, (_, refs) in sorted(groups.items()):
                record["pictures"][p8] = refs
                ext_frames += len(refs)
                bodies = {hd_of[(r, f)][1]: hd_of[(r, f)][0] for r, f in refs if (r, f) in hd_of}
                if len(bodies) > 1:
                    record.setdefault("hd_conflicts", []).append(p8)        # same picture and prefix, different HD: not written
                elif bodies and not dry_run:
                    (body,) = bodies.values()
                    digest_text, size_text = name[1:].split(".")[0].split("_", 1)
                    width_text, height_text = size_text.split("x")
                    file_name = ext_pack_name(int(digest_text, 16), int(width_text), int(height_text), length, int(p8, 16))
                    (out_dir / file_name).parent.mkdir(parents=True, exist_ok=True)
                    (out_dir / file_name).write_bytes(body)
                    ext_files += 1
                    wrote_marker = True
            if wrote_marker:
                (out_dir / (name[:-len(".idx8")] + ".amb")).write_bytes(struct.pack("<I", length))
            extended[name] = record
            continue
        if len(entry["hd"]) > 1:
            conflicts[name] = {c[:8]: refs for c, (_, refs) in entry["hd"].items()}
            continue
        ((_, refs),) = entry["sources"].items()
        index[name] = refs
        if entry["hd"] and not dry_run:
            ((body, _),) = entry["hd"].values()
            (out_dir / name).parent.mkdir(parents=True, exist_ok=True)
            (out_dir / name).write_bytes(body)
            written += 1
    conflict_frames = sum(len(r) for refs in conflicts.values() for r in refs.values())
    out_dir.mkdir(parents=True, exist_ok=True)
    lengths: dict[str, int] = {}
    for record in extended.values():
        lengths[str(record["length"])] = lengths.get(str(record["length"]), 0) + 1
    report = {"tool": "g1_hd_convert", "cmd": "pack", "dry_run": dry_run or hd_dir is None, **stats,
              "unique_names": len(names), "conflict_names": len(conflicts), "conflict_frames": conflict_frames,
              "extended_names": len(extended), "extended_frames": ext_frames, "extended_lengths": lengths,
              "extended_files": ext_files, "pack_files": written, "pass": stats["named"] > 0}
    (out_dir / "digest_index.json").write_text(
        json.dumps({"index": index, "conflicts": conflicts, "extended": extended, "report": report}, sort_keys=True),
        encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    pk = sub.add_parser("pack")
    pk.add_argument("--pal", type=Path, required=True, help="the screen palette the frames are quantised to (out/<pal8>/)")
    pk.add_argument("--game", type=Path, default=hx.DEFAULT_GAME)
    pk.add_argument("--ref", type=Path, help="extraction run (needed with --hd-dir)")
    pk.add_argument("--hd-dir", type=Path, help="HD index PNG tree; without it only names are computed")
    pk.add_argument("--out", type=Path, required=True)
    pk.add_argument("--image-dirs", default=",".join(hx.DEFAULT_IMAGE_DIRS))
    pk.add_argument("--dry-run", action="store_true", help="write digest_index.json only")
    fs = sub.add_parser("fullscreen")
    fs.add_argument("--pal", type=Path, required=True, help="the screen palette the picture is quantised to (out/<pal8>/)")
    fs.add_argument("--game", type=Path, default=hx.DEFAULT_GAME)
    fs.add_argument("spr", type=Path)
    fs.add_argument("--rgb", type=Path, help="upscaler result (RGB, 2w x 2h); default is a bicubic stand-in")
    fs.add_argument("--out", type=Path, required=True)
    lg = sub.add_parser("logo")
    lg.add_argument("--pal", type=Path, required=True, help="the screen palette the picture is quantised to (out/<pal8>/)")
    lg.add_argument("--game", type=Path, default=hx.DEFAULT_GAME)
    lg.add_argument("spr", type=Path)
    lg.add_argument("--rgb", type=Path, help="upscaler result (RGB, 2w x 2h); default is a bicubic stand-in")
    lg.add_argument("--out", type=Path, required=True)
    for name in ("check", "convert", "draft", "panel-idx8"):
        p = sub.add_parser(name)
        p.add_argument("--pal", type=Path, default=hx.DEFAULT_GAME / "pal" / "imjin2.pal")
        p.add_argument("--game", type=Path, default=hx.DEFAULT_GAME)
        p.add_argument("--ref", type=Path, required=True)
        if name == "check":
            p.add_argument("hd_dir", type=Path)
            p.add_argument("--json", type=Path, help="also write the full report here")
        elif name == "convert":
            p.add_argument("rgb_dir", type=Path)
            p.add_argument("--out", type=Path, required=True)
        elif name == "draft":
            p.add_argument("--out", type=Path, required=True)
        else:
            p.add_argument("hd_png", type=Path)
            p.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    palette = hx.load_palette(args.pal)
    if args.cmd in ("pack", "fullscreen", "logo"):
        args.out = args.out / palette_pal8(palette)        # H-HDPAL: <pack>\<pal8>\<name>
    if args.cmd == "pack":
        if args.hd_dir is not None and args.ref is None:
            parser.error("--hd-dir needs --ref")
        report = pack_dir(args.game, args.out, tuple(d for d in args.image_dirs.split(",") if d), args.hd_dir,
                          args.ref, palette, args.dry_run)
    elif args.cmd == "fullscreen":
        report = fullscreen_pack(args.spr, args.rgb, args.out, palette, args.game)
    elif args.cmd == "logo":
        report = logo_pack(args.spr, args.rgb, args.out, palette, args.game)
    elif args.cmd == "check":
        report = check_dir(args.hd_dir, args.ref, palette)
    elif args.cmd == "convert":
        report = convert_dir(args.rgb_dir, args.ref, args.out, palette, args.game)
    elif args.cmd == "draft":
        report = draft_dir(args.ref, args.out, palette, args.game)
    else:
        report = panel_idx8(args.hd_png, args.ref, args.out, palette, args.game)
    text = json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False)
    if args.cmd == "check" and args.json:
        args.json.write_text(text, encoding="utf-8")
    print(text)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
