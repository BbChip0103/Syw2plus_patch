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
    bmp_keys: set[str] = set()
    for path in hx.iter_assets(game):
        rel = path.relative_to(game).as_posix()
        suffix = path.suffix.lower()
        if suffix not in (".spr", ".ytl", ".bmp") or rel.split("/", 1)[0].lower() not in roots:
            continue
        stats["files"] += 1
        data = path.read_bytes()
        try:
            dec = hx.decode_ytl(data) if suffix == ".ytl" else hx.decode_spr(data) if suffix == ".spr" else hx.decode_bmp(data)[0]
        except hx.AssetError:
            stats["unsupported"] += 1
            continue
        if suffix == ".bmp":
            if not dec.idx or len(dec.idx) != 1:
                stats["unsupported"] += 1
                continue
            pixels = dec.idx[0]
            digest = fnv1a_128(pixels.tobytes(), 0)
            if digest is None:
                stats["tail_short"] += 1
                continue
            h, w = pixels.shape
            name = pack_name(digest, w, h)
            entry = names.setdefault(name, {"sources": {}, "hd": {}, "refs": []})
            source = hashlib.sha256(np.where(dec.opaque[0], pixels, TRANSPARENT).astype(np.uint8).tobytes()).hexdigest()
            entry["sources"].setdefault(source, []).append([rel, 0])
            entry["refs"].append([rel, 0])
            bmp_keys.add(name)
            stats["frames"] += 1
            stats["named"] += 1
            if hd_dir is not None:
                hd_png = hd_dir / rel / "0000.png"
                if not hd_png.is_file():
                    stats["no_hd"] += 1
                    continue
                try:
                    ref = load_ref(ref_dir, rel, "0000") if ref_dir else None
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
                    body = np.array(img, dtype=np.uint8).tobytes()
                entry["hd"].setdefault(hashlib.sha256(body).hexdigest(), (body, []))[1].append([rel, 0])
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
            if name in bmp_keys:
                conflicts[name] = {c[:8]: refs for c, refs in entry["sources"].items()}
                continue
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


def _pack_palettes(pack_dir: Path) -> list[tuple[str, Path]]:
    if re.fullmatch(r"[0-9a-fA-F]{8}", pack_dir.name):
        return [(pack_dir.name.lower(), pack_dir)]
    return [(path.name.lower(), path) for path in sorted(pack_dir.iterdir())
            if path.is_dir() and re.fullmatch(r"[0-9a-fA-F]{8}", path.name)]


def _pack_records(game: Path, pack_dir: Path) -> tuple[dict[str, list[tuple[dict[str, Any], Path]]], int, int]:
    """Resolve the existing digest pack into source-relative frame records."""
    if not (pack_dir / "digest_index.json").is_file():
        roots = [path for _, path in _pack_palettes(pack_dir) if (path / "digest_index.json").is_file()]
        if len(roots) != 1:
            raise ConvertError(f"expected digest_index.json in pack root or one palette child: {pack_dir}")
        pack_dir = roots[0]
    manifest = json.loads((pack_dir / "digest_index.json").read_text(encoding="utf-8"))
    records: dict[str, list[tuple[dict[str, Any], Path]]] = {}
    duplicate_frames = conflicts = 0
    palettes = _pack_palettes(pack_dir)

    def add(pal8: str, file_name: str, refs: list[list[Any]], *, length: int = 0, p8: str = "") -> None:
        nonlocal duplicate_frames, conflicts
        source_file = pack_dir / file_name if pack_dir.name.lower() == pal8 else pack_dir / pal8 / file_name
        for rel, frame in refs:
            rel_path = Path(str(rel))
            if rel_path.is_absolute() or ".." in rel_path.parts:
                raise ConvertError(f"unsafe source path in pack index: {rel}")
            try:
                (game / rel_path).resolve().relative_to(game.resolve())
            except ValueError as exc:
                raise ConvertError(f"source path escapes game tree: {rel}") from exc
            if not source_file.is_file():
                conflicts += 1
                continue
            name_match = re.fullmatch(r"(?:w[0-9a-f]{8}_)?h([0-9a-f]{8})_(\d+)x(\d+)(?:_\d+_[0-9a-f]{8})?\.idx8", file_name)
            if not name_match:
                conflicts += 1
                continue
            key_name = file_name.encode("ascii")
            if len(key_name) >= 48:
                conflicts += 1
                continue
            row = {"frame": int(frame), "width": int(name_match.group(2)), "height": int(name_match.group(3)),
                   "pal8": pal8, "digest": name_match.group(1), "length": int(length),
                   "p8": int(p8, 16) if p8 else 0, "key": key_name}
            key = str(rel_path).replace("\\", "/")
            rows = records.setdefault(key, [])
            if any(existing[0]["frame"] == row["frame"] for existing in rows):
                duplicate_frames += 1
                continue
            rows.append((row, source_file))

    for pal8, pal_dir in palettes:
        for digest_name, refs in manifest.get("index", {}).items():
            if (pal_dir / digest_name).is_file():
                add(pal8, digest_name, refs)
        for digest_name, item in manifest.get("extended", {}).items():
            length = int(item["length"])
            for p8, group in item.get("pictures", {}).items():
                data_name = ext_pack_name_from_manifest(digest_name, length, p8)
                if (pal_dir / data_name).is_file():
                    add(pal8, data_name, group, length=length, p8=p8)
    return records, duplicate_frames, conflicts


def sibling_layout(game: Path, pack_dir: Path, out_dir: Path) -> dict[str, Any]:
    """Materialize a pointer-free pack beside each source asset as ``<asset>.hd``.

    ``game`` and ``pack_dir`` are read-only inputs.  ``out_dir`` is a fresh tree
    mirroring the game-relative source paths; each sidecar index records the
    frame number and the pack key needed by the runtime loader.
    """
    _assert_outputs_safe(out_dir, game, pack_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise ConvertError(f"sibling output must be empty: {out_dir}")
    if not (pack_dir / "digest_index.json").is_file():
        pal_roots = [path for path in pack_dir.iterdir()
                     if path.is_dir() and re.fullmatch(r"[0-9a-fA-F]{8}", path.name)
                     and (path / "digest_index.json").is_file()]
        if len(pal_roots) != 1:
            raise ConvertError(f"expected digest_index.json in pack root or one palette child: {pack_dir}")
        pack_dir = pal_roots[0]
    manifest = json.loads((pack_dir / "digest_index.json").read_text(encoding="utf-8"))
    records: dict[tuple[str, str], dict[str, Any]] = {}
    duplicate_frames = 0
    conflicts = 0

    def add(name: str, refs: list[list[Any]], *, length: int = 0, p8: str = "") -> None:
        nonlocal duplicate_frames, conflicts
        if "/" not in name:
            conflicts += len(refs)
            return
        pal8, file_name = name.split("/", 1)
        for rel, frame in refs:
            rel_path = Path(str(rel))
            if rel_path.is_absolute() or ".." in rel_path.parts:
                raise ConvertError(f"unsafe source path in pack index: {rel}")
            frame_id = int(frame)
            sidecar = out_dir / (str(rel_path) + ".hd")
            destination = sidecar / f"{frame_id:04d}.idx8"
            key = (str(rel_path).replace("\\", "/"), f"{frame_id:04d}")
            source_file = pack_dir / file_name if pack_dir.name.lower() == pal8 else pack_dir / pal8 / file_name
            if not source_file.is_file():
                conflicts += 1
                continue
            existing = records.get(key)
            record = {"frame": frame_id, "digest": file_name, "pal8": pal8,
                      "length": length, "p8": p8}
            if existing is not None:
                duplicate_frames += 1
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source_file.read_bytes())
            records[key] = {"record": record, "sidecar": sidecar}

    pal8_dirs = sorted(p for p in pack_dir.iterdir() if p.is_dir() and re.fullmatch(r"[0-9a-fA-F]{8}", p.name))
    palettes = [(pack_dir.name.lower(), pack_dir)] if re.fullmatch(r"[0-9a-fA-F]{8}", pack_dir.name) else [
        (pal_dir.name.lower(), pal_dir) for pal_dir in pal8_dirs]
    if not palettes:
        raise ConvertError(f"pack root has no palette identity: {pack_dir}")
    for pal8, pal8_dir in palettes:
        for digest_name, refs in manifest.get("index", {}).items():
            if (pal8_dir / digest_name).is_file():
                add(f"{pal8}/{digest_name}", refs)
        for digest_name, item in manifest.get("extended", {}).items():
            length = int(item["length"])
            for p8, group in item.get("pictures", {}).items():
                data_name = ext_pack_name_from_manifest(digest_name, length, p8)
                if (pal8_dir / data_name).is_file():
                    add(f"{pal8}/{data_name}", group, length=length, p8=p8)

    by_sidecar: dict[Path, list[dict[str, Any]]] = {}
    for item in records.values():
        by_sidecar.setdefault(item["sidecar"], []).append(item["record"])
    for sidecar, entries in by_sidecar.items():
        entries.sort(key=lambda entry: entry["frame"])
        (sidecar / "index.json").write_text(
            json.dumps({"version": 1, "frames": entries}, sort_keys=False, separators=(",", ":")),
            encoding="utf-8")
    return {"tool": "g1_hd_convert", "cmd": "sibling-layout", "files": len(records),
            "folders": len(by_sidecar), "duplicate_frames": duplicate_frames,
            "unavailable_or_conflict_frames": conflicts,
            "bytes": sum((sidecar / f"{entry['frame']:04d}.idx8").stat().st_size
                         for sidecar, entries in by_sidecar.items() for entry in entries),
            "pass": bool(records)}


def _double_pixels(frame: np.ndarray) -> np.ndarray:
    return np.repeat(np.repeat(frame, 2, axis=0), 2, axis=1)


def _pack_pixels(row: dict[str, Any], source: Path, fallback: np.ndarray) -> np.ndarray:
    """Read a packed 2x frame, extending the 800-column panel crop with source pixels."""
    body = source.read_bytes()
    width, height = int(row["width"]), int(row["height"])
    key = row["key"]
    packed_width = 800 if width == PANEL_SOURCE_WIDTH and key.startswith(b"w004663e0_") else width
    if len(body) != packed_width * height * 4:
        raise ConvertError(f"{source}: {len(body)} bytes does not match {packed_width}x{height} at 2x")
    pixels = np.frombuffer(body, dtype=np.uint8).reshape(2 * height, 2 * packed_width)
    if packed_width == width:
        return pixels.copy()
    result = fallback.copy()
    result[:, :pixels.shape[1]] = pixels
    return result


def _encode_spr_native(source_data: bytes, frames: list[np.ndarray], masks: list[np.ndarray], kind: str) -> bytes:
    version, width, height, count = struct.unpack_from("<4I", source_data, 0)
    if len(frames) != count or len(masks) != count or any(frame.shape != (height * 2, width * 2) for frame in frames):
        raise ConvertError(".spr frame count or 2x dimensions do not match its source")
    header = bytearray(source_data[:hx.SPR_FIXED_HEADER])
    struct.pack_into("<4I", header, 0, version, width * 2, height * 2, count)
    if kind == "raw":
        body = b"".join(frame.tobytes() for frame in frames)
        _old_size, old_w, old_h = struct.unpack_from("<3I", source_data, hx.SPR_SHEET_RECORD)
        struct.pack_into("<3I", header, hx.SPR_SHEET_RECORD,
                         len(body), old_w * 2 if old_w else 0, old_h * 2 if old_h else 0)
        total = width * height * 4
        for i in range(1, 300):
            struct.pack_into("<I", header, hx.SPR_OFFSET_TABLE + 4 * (i - 1), i * total if i < count else 0)
        return bytes(header) + body
    streams = [hx.rle_encode(frame, mask) for frame, mask in zip(frames, masks, strict=True)]
    _old_size, old_w, old_h = struct.unpack_from("<3I", source_data, hx.SPR_SHEET_RECORD)
    if old_w and old_h:
        streams = _avoid_spr_raw_collision(streams, old_w * 2 * old_h * 2)
    offsets, cursor = [], 0
    for stream in streams:
        offsets.append(cursor)
        cursor += len(stream)
    for i in range(1, 300):
        struct.pack_into("<I", header, hx.SPR_OFFSET_TABLE + 4 * (i - 1), offsets[i] if i < count else 0)
    _old_size, old_w, old_h = struct.unpack_from("<3I", source_data, hx.SPR_SHEET_RECORD)
    struct.pack_into("<3I", header, hx.SPR_SHEET_RECORD, cursor,
                     old_w * 2 if old_w else 0, old_h * 2 if old_h else 0)
    return bytes(header) + b"".join(streams)


def _encode_spr_sheet_native(source_data: bytes, pixels: np.ndarray, mask: np.ndarray, kind: str) -> bytes:
    """Write a header-sized frame and its separately declared pixel sheet at 2x."""
    version, width, height, count = struct.unpack_from("<4I", source_data, 0)
    _size, sheet_width, sheet_height = struct.unpack_from("<3I", source_data, hx.SPR_SHEET_RECORD)
    if not sheet_width or not sheet_height or pixels.shape != (sheet_height * 2, sheet_width * 2) or mask.shape != pixels.shape:
        raise ConvertError(".spr sheet dimensions do not match its source record")
    if kind == "raw":
        payload = pixels.tobytes()
    else:
        payload = _avoid_spr_raw_collision([hx.rle_encode(pixels, mask)], (sheet_width * 2) * (sheet_height * 2))[0]
    header = bytearray(source_data[:hx.SPR_FIXED_HEADER])
    struct.pack_into("<4I", header, 0, version, width * 2, height * 2, count)
    struct.pack_into("<3I", header, hx.SPR_SHEET_RECORD, len(payload), sheet_width * 2, sheet_height * 2)
    for index in range(1, 300):
        struct.pack_into("<I", header, hx.SPR_OFFSET_TABLE + 4 * (index - 1), 0)
    return bytes(header) + payload


def _avoid_spr_raw_collision(streams: list[bytes], raw_size: int) -> list[bytes]:
    """Keep an RLE payload distinct from the SPR raw-size sentinel.

    The native format infers raw pixels when its payload byte count equals the
    declared sheet area. Splitting one transparent run into two legal runs adds
    two bytes without changing any decoded pixels or masks.
    """
    if sum(map(len, streams)) != raw_size:
        return streams
    for stream_index, stream in enumerate(streams):
        pos = 0
        while pos + 1 < len(stream):
            if stream[pos] == hx.RLE_MARKER and stream[pos + 1] > 1:
                count = stream[pos + 1]
                streams = list(streams)
                streams[stream_index] = stream[:pos] + bytes((hx.RLE_MARKER, 1, hx.RLE_MARKER, count - 1)) + stream[pos + 2:]
                return streams
            pos += 2 if stream[pos] == hx.RLE_MARKER else 1
    raise ConvertError(".spr RLE payload collides with the declared raw sheet size and has no splittable transparent run")


def _encode_ytl_native(source_data: bytes, frames: list[np.ndarray], masks: list[np.ndarray]) -> bytes:
    version, width, height, count = struct.unpack_from("<4I", source_data, 0)
    if len(frames) != count or len(masks) != count or any(frame.shape != (height * 2, width * 2) for frame in frames):
        raise ConvertError(".ytl frame count or 2x dimensions do not match its source")
    packed_frames = []
    for frame, mask in zip(frames, masks, strict=True):
        records = bytearray()
        for row, opaque in zip(frame, mask, strict=True):
            cols = np.flatnonzero(opaque)
            if not cols.size:
                records += bytes((min(width * 2, 255), 0))
                continue
            start, end = int(cols[0]), int(cols[-1]) + 1
            if start > 255 or end - start > 255:
                raise ConvertError(".ytl 2x row cannot fit one [skip][count][bytes] record")
            records += bytes((start, end - start)) + row[start:end].tobytes()
        packed_frames.append(bytes(records))
    header = bytearray(source_data[:hx.SPR_FIXED_HEADER])
    struct.pack_into("<4I", header, 0, version, width * 2, height * 2, count)
    cursor = 0
    for i, frame_stream in enumerate(packed_frames):
        struct.pack_into("<I", header, hx.YTL_OFFSET_TABLE + 4 * i, cursor)
        cursor += len(frame_stream)
    struct.pack_into("<I", header, hx.SPR_SHEET_RECORD, cursor)
    return bytes(header) + b"".join(packed_frames)


def _encode_bmp_native(source_data: bytes, pixels: np.ndarray) -> bytes:
    pixel_offset = struct.unpack_from("<I", source_data, 10)[0]
    _dib_size, _width, signed_height, _planes, _bpp, _compression, *_ = struct.unpack_from("<IiiHHIIiiII", source_data, 14)
    height, width = pixels.shape
    stride = (width + 3) & ~3
    rows = pixels if signed_height < 0 else pixels[::-1]
    body = b"".join(row.tobytes() + bytes(stride - width) for row in rows)
    header = bytearray(source_data[:pixel_offset])
    struct.pack_into("<I", header, 2, pixel_offset + len(body))
    struct.pack_into("<ii", header, 18, width, -height if signed_height < 0 else height)
    struct.pack_into("<I", header, 34, len(body))
    return bytes(header) + body


def native_layout(game: Path, pack_dir: Path, out_dir: Path, palette: np.ndarray | None = None) -> dict[str, Any]:
    """Write native ``<source>_hd.<ext>`` siblings and their original-file SHA-256 index."""
    _assert_outputs_safe(out_dir, game, pack_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise ConvertError(f"native output must be empty: {out_dir}")
    records, duplicate_frames, conflicts = _pack_records(game, pack_dir)
    by_source = {Path(rel): items for rel, items in records.items()}
    out_dir.mkdir(parents=True, exist_ok=True)
    files_written = frames_written = byte_count = defaults = 0
    errors: list[str] = []
    unmapped_assets: list[str] = []
    source_hashes: list[tuple[str, str]] = []
    fe_replacement = int(hx.fe_replacement(palette)) if palette is not None else 253
    for source_path in hx.iter_assets(game):
        source_rel = source_path.relative_to(game)
        mapped = {int(row["frame"]): (row, packed) for row, packed in by_source.get(source_rel, [])}
        # A native sibling is meaningful only when the accepted pack contains at
        # least one authored HD frame for this asset. Missing images stay on the
        # runtime Scale2x path instead of becoming another copy of the source.
        if not mapped:
            continue
        data = source_path.read_bytes()
        try:
            decoded, _palette_bytes = hx.decode_file(source_path)
        except hx.AssetError:
            continue
        sheet_size = sheet_width = sheet_height = 0
        sheet_candidate = False
        if source_path.suffix.lower() == ".spr" and decoded.kind == "rle":
            sheet_size, sheet_width, sheet_height = struct.unpack_from("<3I", data, hx.SPR_SHEET_RECORD)
            declared_pixels = decoded.fw * decoded.fh * len(decoded.idx)
            sheet_candidate = (not all(decoded.exact) and sheet_width >= decoded.fw and sheet_height >= decoded.fh and
                               sheet_width * sheet_height > declared_pixels and
                               sheet_size <= len(data) - hx.SPR_FIXED_HEADER)
        if not decoded.idx or (not all(decoded.exact) and not sheet_candidate):
            errors.append(f"{source_rel}: source frame decode is incomplete")
            continue
        hd_frames, hd_masks = [], []
        for frame_index, (idx, opaque) in enumerate(zip(decoded.idx, decoded.opaque, strict=True)):
            doubled_mask = _double_pixels(opaque)
            doubled = np.where(doubled_mask, _double_pixels(idx), TRANSPARENT).astype(np.uint8)
            doubled[doubled_mask & (doubled == TRANSPARENT)] = fe_replacement
            if frame_index in mapped:
                row, packed = mapped[frame_index]
                try:
                    doubled = _pack_pixels(row, packed, doubled)
                except ConvertError as error:
                    errors.append(str(error))
                    continue
            else:
                defaults += 1
            hd_frames.append(doubled)
            hd_masks.append(doubled_mask)
        if len(hd_frames) != len(decoded.idx):
            continue
        suffix = source_path.suffix.lower()
        try:
            if suffix == ".spr":
                if sheet_candidate:
                    if sheet_width % decoded.fw or sheet_height % decoded.fh:
                        unmapped_assets.append(source_rel.as_posix())
                        continue
                    sheet_idx, sheet_mask, used = hx.rle_decode(
                        data[hx.SPR_FIXED_HEADER:hx.SPR_FIXED_HEADER + sheet_size], sheet_width * sheet_height)
                    if used != sheet_size:
                        raise ConvertError(".spr sheet RLE payload is not consumed exactly")
                    source_sheet = sheet_idx.reshape(sheet_height, sheet_width)
                    source_mask = sheet_mask.reshape(sheet_height, sheet_width)
                    hd_sheet_mask = _double_pixels(source_mask)
                    hd_sheet = np.where(hd_sheet_mask, _double_pixels(source_sheet), TRANSPARENT).astype(np.uint8)
                    hd_sheet[hd_sheet_mask & (hd_sheet == TRANSPARENT)] = fe_replacement
                    cells_x, cells_y = sheet_width // decoded.fw, sheet_height // decoded.fh
                    for cell, (row, packed) in mapped.items():
                        if cell >= cells_x * cells_y:
                            raise ConvertError(f".spr sheet frame {cell} is outside the declared cell grid")
                        y, x = divmod(cell, cells_x)
                        src_x, src_y = x * decoded.fw, y * decoded.fh
                        crop = hd_sheet[2 * src_y:2 * (src_y + decoded.fh), 2 * src_x:2 * (src_x + decoded.fw)]
                        fallback = crop.copy()
                        replacement = _pack_pixels(row, packed, fallback)
                        crop[:, :] = replacement
                    payload = _encode_spr_sheet_native(data, hd_sheet, hd_sheet_mask, decoded.kind)
                else:
                    payload = _encode_spr_native(data, hd_frames, hd_masks, decoded.kind)
            elif suffix == ".ytl":
                payload = _encode_ytl_native(data, hd_frames, hd_masks)
            else:
                payload = _encode_bmp_native(data, hd_frames[0])
        except (ConvertError, struct.error) as error:
            errors.append(f"{source_rel}: {error}")
            continue
        output_rel = source_rel.with_name(source_rel.stem + "_hd" + source_rel.suffix)
        destination = out_dir / output_rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        source_hashes.append((output_rel.as_posix(), hashlib.sha256(data).hexdigest()))
        files_written += 1
        frames_written += len(hd_frames)
        byte_count += len(payload)
    manifest_path = out_dir / "g1_hd_sources.sha256"
    if source_hashes:
        manifest_path.write_text("".join(f"{digest}  {path}\n" for path, digest in sorted(source_hashes)),
                                 encoding="ascii", newline="\n")
    return {"tool": "g1_hd_convert", "cmd": "native-layout", "files": files_written,
            "frames": frames_written, "default_scale_frames": defaults,
            "duplicate_frames": duplicate_frames, "unavailable_or_conflict_frames": conflicts,
            "bytes": byte_count, "errors": errors[:20], "error_count": len(errors),
            "source_manifest": manifest_path.name if source_hashes else None,
            "source_manifest_entries": len(source_hashes),
            "unmapped_assets": unmapped_assets,
            "pass": files_written > 0 and not errors}


def ext_pack_name_from_manifest(base_name: str, length: int, p8: str) -> str:
    match = re.fullmatch(r"h([0-9a-f]{8})_(\d+)x(\d+)\.idx8", base_name)
    if not match:
        raise ConvertError(f"invalid extended pack key: {base_name}")
    return f"h{match.group(1)}_{match.group(2)}x{match.group(3)}_{length}_{p8}.idx8"


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
    sl = sub.add_parser("sibling-layout", help="copy a pack beside source assets as <asset>.hd folders")
    sl.add_argument("pack_dir", type=Path, help="read-only pack directory containing digest_index.json")
    sl.add_argument("--game", type=Path, default=hx.DEFAULT_GAME)
    sl.add_argument("--pal", type=Path, default=hx.DEFAULT_GAME / "pal" / "imjin2.pal")
    sl.add_argument("--out", type=Path, required=True, help="new output tree; must be empty")
    sf = sub.add_parser("native-layout", help="write native-format sibling <asset>_hd.<ext> files from an existing pack")
    sf.add_argument("pack_dir", type=Path, help="read-only pack directory containing digest_index.json")
    sf.add_argument("--game", type=Path, default=hx.DEFAULT_GAME)
    sf.add_argument("--pal", type=Path, default=hx.DEFAULT_GAME / "pal" / "imjin2.pal")
    sf.add_argument("--out", type=Path, required=True, help="new output tree mirroring the game paths")
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
    palette = hx.load_palette(args.pal) if hasattr(args, "pal") else None
    if args.cmd in ("pack", "fullscreen", "logo"):
        assert palette is not None
        args.out = args.out / palette_pal8(palette)        # H-HDPAL: <pack>\<pal8>\<name>
    if args.cmd == "pack":
        assert palette is not None
        if args.hd_dir is not None and args.ref is None:
            parser.error("--hd-dir needs --ref")
        report = pack_dir(args.game, args.out, tuple(d for d in args.image_dirs.split(",") if d), args.hd_dir,
                          args.ref, palette, args.dry_run)
    elif args.cmd == "fullscreen":
        assert palette is not None
        report = fullscreen_pack(args.spr, args.rgb, args.out, palette, args.game)
    elif args.cmd == "logo":
        assert palette is not None
        report = logo_pack(args.spr, args.rgb, args.out, palette, args.game)
    elif args.cmd == "sibling-layout":
        report = sibling_layout(args.game, args.pack_dir, args.out)
    elif args.cmd == "native-layout":
        report = native_layout(args.game, args.pack_dir, args.out, hx.load_palette(args.pal))
    elif args.cmd == "check":
        assert palette is not None
        report = check_dir(args.hd_dir, args.ref, palette)
    elif args.cmd == "convert":
        assert palette is not None
        report = convert_dir(args.rgb_dir, args.ref, args.out, palette, args.game)
    elif args.cmd == "draft":
        assert palette is not None
        report = draft_dir(args.ref, args.out, palette, args.game)
    else:
        assert palette is not None
        report = panel_idx8(args.hd_png, args.ref, args.out, palette, args.game)
    text = json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False)
    if args.cmd == "check" and args.json:
        args.json.write_text(text, encoding="utf-8")
    print(text)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
