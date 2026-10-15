"""Extract original game pictures (.spr/.ytl/8-bit .bmp) for the HD picture path (H-HDX1).

Read-only on the game folder.  Per frame it writes a 1x index PNG (palette
``imjin2.pal``, transparent index 254), a 1-bit silhouette mask (1 = opaque),
and a mask-aware Scale2x 2x draft (exactly 2w x 2h, silhouette 2x2 identical).

Layout facts (census over the ESL game folder, see lap1157 record):
- ``.spr`` RLE: every frame is its own stream starting at the offset table
  (0x4C4, frame 0 at 0); ``FE n`` = n transparent pixels, ``FE 00`` = literal 0xFE.
  The "sheet" record is metadata only; frames are NOT cut from a sheet grid.
- ``.spr`` raw (pixel bytes == sheet w*h): frames are consecutive fw*fh blocks.
- ``.ytl``: offset table at 0x4C0; each frame is fh scanline records
  ``[skip u8][count u8][count bytes]``; the rest of the row is transparent.
Silhouette = RLE transparent runs / record gaps only; an index value is never
used to infer transparency.  Exception (lap1158 decision): 8-bit portrait BMPs,
whose 170x128 surface uses the engine colour key 0xFE, treat index 254 as transparent.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import random
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

TRANSPARENT = 254
RLE_MARKER = 0xFE
TEAM_LOW, TEAM_HIGH = 236, 239
SPR_FIXED_HEADER = 0xBF4
SPR_OFFSET_TABLE = 0x4C4
SPR_SHEET_RECORD = 0xBC8
YTL_OFFSET_TABLE = 0x4C0
PAL_RULE = "6bit_x4"
DEFAULT_IMAGE_DIRS = ("char", "tile", "BattleSpr", "portrait")
EXTENSIONS = (".spr", ".ytl", ".bmp")
DEFAULT_GAME = Path(__file__).resolve().parents[2] / "[ESL]Syw2plus"


@dataclass
class Decoded:
    kind: str                      # rle | raw | ytl | bmp
    fw: int
    fh: int
    idx: list[np.ndarray]          # per frame (fh, fw) uint8, raw index values
    opaque: list[np.ndarray]       # per frame (fh, fw) bool
    exact: list[bool]
    mask_source: str
    sheet_record: str = ""
    warnings: list[str] = field(default_factory=list)


class AssetError(Exception):
    """File cannot be classified into a supported layout."""


# --- palette -----------------------------------------------------------------

def load_palette(path: Path) -> np.ndarray:
    raw = path.read_bytes()
    if len(raw) != 768 or max(raw) > 63:
        raise AssetError(f"not a 6-bit VGA palette: {path}")
    return (np.frombuffer(raw, dtype=np.uint8).reshape(256, 3).astype(np.uint16) * 4).astype(np.uint8)


def fe_replacement(palette: np.ndarray) -> int:
    """Nearest opaque palette index to the colour of 254 (never 254 itself)."""
    target: np.ndarray = palette[TRANSPARENT].astype(np.int32)
    dist = ((palette.astype(np.int32) - target) ** 2).sum(axis=1)
    dist[TRANSPARENT] = 1 << 30
    return int(np.argmin(dist))


# --- decoders ----------------------------------------------------------------

def rle_decode(seg: bytes, total: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Decode one RLE stream to (index, opaque, bytes consumed) of ``total`` pixels."""
    idx: np.ndarray = np.zeros(total, dtype=np.uint8)
    opq: np.ndarray = np.zeros(total, dtype=bool)
    out = pos = 0
    n = len(seg)
    while pos < n and out < total:
        b = seg[pos]
        if b == RLE_MARKER and pos + 1 < n:
            c = seg[pos + 1]
            if c == 0:
                idx[out] = RLE_MARKER
                opq[out] = True
                out += 1
            else:
                out += min(c, total - out)
            pos += 2
        else:
            idx[out] = b
            opq[out] = True
            out += 1
            pos += 1
    return idx, opq, pos


def rle_encode(idx: np.ndarray, opq: np.ndarray) -> bytes:
    """Encode like the original data: runs stop at row ends and at 255."""
    out = bytearray()
    for row_i, row_o in zip(idx, opq, strict=True):
        i, n = 0, row_i.size
        while i < n:
            if not row_o[i]:
                run = 1
                while i + run < n and not row_o[i + run] and run < 255:
                    run += 1
                out += bytes((RLE_MARKER, run))
                i += run
            else:
                v = int(row_i[i])
                out += bytes((RLE_MARKER, 0)) if v == RLE_MARKER else bytes((v,))
                i += 1
    return bytes(out)


def _spr_header(data: bytes) -> tuple[int, int, int, int, int, int]:
    if len(data) < SPR_FIXED_HEADER:
        raise AssetError("shorter than the 0xBF4 header")
    version, fw, fh, fc = struct.unpack_from("<4I", data, 0)
    if version != 9 or fw == 0 or fh == 0 or not 0 < fc <= 300:
        raise AssetError(f"unsupported header version={version} {fw}x{fh} fc={fc}")
    tds, sw, sh = struct.unpack_from("<3I", data, SPR_SHEET_RECORD)
    return fw, fh, fc, tds, sw, sh


def decode_spr(data: bytes) -> Decoded:
    fw, fh, fc, tds, sw, sh = _spr_header(data)
    pix = data[SPR_FIXED_HEADER:]
    offs = [0] + list(struct.unpack_from("<299I", data, SPR_OFFSET_TABLE))[: fc - 1]
    total = fw * fh
    raw = sw > 0 and tds == sw * sh
    warnings: list[str] = []
    idxs: list[np.ndarray] = []
    opqs: list[np.ndarray] = []
    exact: list[bool] = []
    if raw:
        if offs != [i * total for i in range(fc)]:
            warnings.append("raw offset table differs from consecutive fw*fh blocks; blocks used")
        for i in range(fc):
            block = np.frombuffer(pix[i * total:(i + 1) * total], dtype=np.uint8)
            ok = block.size == total
            if not ok:
                block = np.pad(block, (0, total - block.size))
                warnings.append(f"raw frame {i} truncated")
            idxs.append(block.reshape(fh, fw).copy())
            opqs.append(np.ones((fh, fw), dtype=bool))
            exact.append(ok)
        warnings.append("raw .spr has no transparent runs: silhouette is all opaque (engine transparency UNKNOWN)")
        return Decoded("raw", fw, fh, idxs, opqs, exact, "raw_all_opaque", f"{sw}x{sh}", warnings)
    mono = all(offs[i] <= offs[i + 1] for i in range(fc - 1))
    if not mono:
        warnings.append("offset table not monotonic; frame streams decoded sequentially")
    limit = min(tds, len(pix)) if tds else len(pix)
    for i in range(fc):
        start = offs[i]
        end = offs[i + 1] if i + 1 < fc and mono else limit
        i_arr, o_arr, used = rle_decode(pix[start:end] if start <= len(pix) else b"", total)
        ok = used == end - start and _rle_len(pix[start:end]) == total
        idxs.append(i_arr.reshape(fh, fw))
        opqs.append(o_arr.reshape(fh, fw))
        exact.append(ok)
    bad = [i for i, ok in enumerate(exact) if not ok]
    if bad:
        warnings.append(f"frames not exactly consumed: {bad[:8]}{'...' if len(bad) > 8 else ''}")
    sheet = "ok" if sw >= fw and sh >= fh else "zero_or_undersized"
    return Decoded("rle", fw, fh, idxs, opqs, exact, "rle_runs", f"{sheet}:{sw}x{sh}", warnings)


def decode_spr_sheet(data: bytes) -> Decoded:
    """Decode a `.spr` pixel sheet whose dimensions differ from its frame header.

    Some native assets declare one small frame while storing a larger RLE sheet.
    Keep the regular frame decoder's contract unchanged; this explicit view lets
    conversion and round-trip checks inspect the complete native payload.
    """
    fw, fh, fc, encoded_bytes, sw, sh = _spr_header(data)
    if sw < fw or sh < fh or sw * sh <= fw * fh * fc:
        raise AssetError(".spr sheet record does not describe a larger pixel sheet")
    payload = data[SPR_FIXED_HEADER:SPR_FIXED_HEADER + encoded_bytes]
    if len(payload) != encoded_bytes:
        raise AssetError(".spr sheet payload is truncated")
    idx, opaque, used = rle_decode(payload, sw * sh)
    if used != encoded_bytes or _rle_len(payload) != sw * sh:
        raise AssetError(".spr sheet RLE payload is incomplete or overlong")
    return Decoded("sheet", sw, sh, [idx.reshape(sh, sw)], [opaque.reshape(sh, sw)], [True],
                   "rle_runs", f"sheet:{sw}x{sh}", [])


def _rle_len(seg: bytes) -> int:
    out = pos = 0
    n = len(seg)
    while pos < n:
        b = seg[pos]
        if b == RLE_MARKER and pos + 1 < n:
            out += 1 if seg[pos + 1] == 0 else seg[pos + 1]
            pos += 2
        else:
            out += 1
            pos += 1
    return out


def ytl_decode_frame(pix: bytes, start: int, fw: int, fh: int) -> tuple[np.ndarray, np.ndarray, int, bool]:
    idx: np.ndarray = np.zeros((fh, fw), dtype=np.uint8)
    opq: np.ndarray = np.zeros((fh, fw), dtype=bool)
    pos = start
    ok = True
    for row in range(fh):
        if pos + 2 > len(pix):
            ok = False
            break
        skip, count = pix[pos], pix[pos + 1]
        pos += 2
        if skip + count > fw or pos + count > len(pix):
            ok = False
        take = max(0, min(count, fw - skip, len(pix) - pos)) if skip < fw else 0
        if take:
            idx[row, skip:skip + take] = np.frombuffer(pix[pos:pos + take], dtype=np.uint8)
            opq[row, skip:skip + take] = True
        pos += count
    return idx, opq, pos, ok


def ytl_encode_frame(idx: np.ndarray, opq: np.ndarray) -> bytes:
    out = bytearray()
    for row in range(idx.shape[0]):
        cols = np.flatnonzero(opq[row])
        if cols.size == 0:
            out += bytes((idx.shape[1], 0))      # original: empty row = skip full width
            continue
        skip, last = int(cols[0]), int(cols[-1])
        out += bytes((skip, last - skip + 1)) + idx[row, skip:last + 1].tobytes()
    return bytes(out)


def decode_ytl(data: bytes) -> Decoded:
    if len(data) < SPR_FIXED_HEADER:
        raise AssetError("shorter than the 0xBF4 header")
    version, fw, fh, fc = struct.unpack_from("<4I", data, 0)
    if version != 9 or fw == 0 or fh == 0 or fc == 0:
        raise AssetError(f"unsupported header version={version} {fw}x{fh} fc={fc}")
    table_end = YTL_OFFSET_TABLE + 4 * fc
    if table_end > SPR_SHEET_RECORD:
        raise AssetError(f"offset table of {fc} frames overlaps the sheet record")
    offs = list(struct.unpack_from(f"<{fc}I", data, YTL_OFFSET_TABLE))
    pix = data[SPR_FIXED_HEADER:]
    warnings: list[str] = []
    if fc > 300:
        warnings.append(f"fc={fc}>300: offset table read through 0x{table_end:X}")
    idxs, opqs, exact = [], [], []
    for i in range(fc):
        i_arr, o_arr, pos, ok = ytl_decode_frame(pix, offs[i], fw, fh)
        nxt = offs[i + 1] if i + 1 < fc else None
        idxs.append(i_arr)
        opqs.append(o_arr)
        exact.append(ok and (nxt is None or nxt == pos))
    bad = [i for i, ok in enumerate(exact) if not ok]
    if bad:
        warnings.append(f"frames not exactly consumed: {bad[:8]}{'...' if len(bad) > 8 else ''}")
    return Decoded("ytl", fw, fh, idxs, opqs, exact, "ytl_records", "", warnings)


def decode_bmp(data: bytes) -> tuple[Decoded, bytes]:
    if len(data) < 54 or data[:2] != b"BM":
        raise AssetError("not a BMP")
    pixel_off = struct.unpack_from("<I", data, 10)[0]
    hdr, width, height, planes, bpp, comp, _, _, _, colors, _ = struct.unpack_from("<IiiHHIIiiII", data, 14)
    if bpp != 8 or comp != 0 or hdr < 40 or width <= 0 or height == 0:
        raise AssetError(f"not an uncompressed 8-bit BMP (bpp={bpp} comp={comp})")
    rows = abs(height)
    stride = (width + 3) & ~3
    if pixel_off + stride * rows > len(data):
        raise AssetError("BMP pixel data truncated")
    block = np.frombuffer(data[pixel_off:pixel_off + stride * rows], dtype=np.uint8).reshape(rows, stride)[:, :width]
    if height > 0:
        block = block[::-1]
    pal_bytes = data[14 + hdr:14 + hdr + 4 * (colors or 256)]
    # Portrait surfaces are created with SetColorKey(0xFE) and blitted SRCCOLORKEY: index 254 is transparent.
    dec = Decoded("bmp", width, rows, [block.copy()], [block != TRANSPARENT], [True],
                  "bmp_colorkey_fe", "", [])
    return dec, pal_bytes


# --- image products ----------------------------------------------------------

def scale2x_masked(index: np.ndarray, written: np.ndarray) -> np.ndarray:
    """Mask-aware Scale2x identical to tools/inmm_stub/g1_scale2x_core.h."""
    h, w = index.shape
    w_pad = np.pad(written, 1, mode="edge")
    s_pad = np.pad(index, 1, mode="edge")
    e = index
    top = np.where(w_pad[:-2, 1:-1], s_pad[:-2, 1:-1], e)
    left = np.where(w_pad[1:-1, :-2], s_pad[1:-1, :-2], e)
    right = np.where(w_pad[1:-1, 2:], s_pad[1:-1, 2:], e)
    bottom = np.where(w_pad[2:, 1:-1], s_pad[2:, 1:-1], e)
    cond = written & (top != bottom) & (left != right)
    p0 = np.where(cond & (left == top), left, e)
    p1 = np.where(cond & (top == right), right, e)
    p2 = np.where(cond & (left == bottom), left, e)
    p3 = np.where(cond & (bottom == right), right, e)
    out = np.empty((h * 2, w * 2), dtype=np.uint8)
    out[0::2, 0::2], out[0::2, 1::2], out[1::2, 0::2], out[1::2, 1::2] = p0, p1, p2, p3
    return out


def make_products(idx: np.ndarray, opq: np.ndarray, fe_to: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Return (1x index with 254 transparent, 2x draft, literal-FE remap count)."""
    remapped = int(((idx == TRANSPARENT) & opq).sum())
    base = np.where(opq, np.where(idx == TRANSPARENT, fe_to, idx), TRANSPARENT).astype(np.uint8)
    return base, scale2x_masked(base, opq), remapped


def save_index_png(path: Path, arr: np.ndarray, palette: np.ndarray) -> None:
    img = Image.fromarray(arr, mode="P")
    img.putpalette(palette.astype(np.uint8).ravel().tolist())
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", transparency=TRANSPARENT, compress_level=6)


def save_mask_png(path: Path, opq: np.ndarray) -> None:
    img = Image.fromarray(opq.astype(np.uint8) * 255, mode="L").convert("1")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", compress_level=6)


# --- census / extraction -----------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def listing_digest(root: Path) -> str:
    """Digest of every file's relative path, size and mtime under ``root``."""
    h = hashlib.sha256()
    for base, dirs, files in os.walk(root):
        dirs.sort()
        for name in sorted(files):
            p = Path(base) / name
            st = p.stat()
            h.update(f"{p.relative_to(root).as_posix()}|{st.st_size}|{st.st_mtime_ns}\n".encode())
    return h.hexdigest()


def iter_assets(game: Path) -> list[Path]:
    found = []
    for base, dirs, files in os.walk(game):
        dirs.sort()
        for name in sorted(files):
            if name.lower().endswith(EXTENSIONS):
                found.append(Path(base) / name)
    return found


def decode_file(path: Path) -> tuple[Decoded, bytes]:
    data = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix == ".spr":
        return decode_spr(data), b""
    if suffix == ".ytl":
        return decode_ytl(data), b""
    return decode_bmp(data)


def _assert_outside(out: Path, *roots: Path) -> None:
    out_r = out.resolve()
    for root in roots:
        root_r = root.resolve()
        if out_r == root_r or root_r in out_r.parents:
            raise SystemExit(f"output {out_r} must not be inside {root_r}")


def extract(game: Path, out: Path, image_dirs: tuple[str, ...], only: tuple[str, ...],
            census_only: bool, repo: Path) -> dict[str, Any]:
    _assert_outside(out, game, repo)
    palette = load_palette(game / "pal" / "imjin2.pal")
    fe_to = fe_replacement(palette)
    before = listing_digest(game)
    files = []
    summary: dict[str, int] = {}
    unclassified: list[dict[str, str]] = []
    image_roots = tuple(d.lower() for d in image_dirs)
    for path in iter_assets(game):
        rel = path.relative_to(game).as_posix()
        if only and not any(o in rel for o in only):
            continue
        entry: dict[str, Any] = {"path": rel, "size": path.stat().st_size, "sha256": sha256_file(path)}
        try:
            dec, bmp_pal = decode_file(path)
        except AssetError as exc:
            entry.update(kind="unsupported", reason=str(exc))
            unclassified.append({"path": rel, "reason": str(exc)})
            summary["unsupported"] = summary.get("unsupported", 0) + 1
            files.append(entry)
            continue
        summary[dec.kind] = summary.get(dec.kind, 0) + 1
        entry.update(kind=dec.kind, fw=dec.fw, fh=dec.fh, fc=len(dec.idx), mask_source=dec.mask_source,
                     sheet_record=dec.sheet_record, warnings=dec.warnings)
        if bmp_pal:
            entry["bmp_palette_sha256"] = hashlib.sha256(bmp_pal).hexdigest()
        render = (not census_only) and rel.split("/", 1)[0].lower() in image_roots
        frames = []
        for i, (idx, opq) in enumerate(zip(dec.idx, dec.opaque, strict=True)):
            base, doubled, remapped = make_products(idx, opq, fe_to)
            frames.append({"i": i, "opaque": int(opq.sum()),
                           "team": int(((base >= TEAM_LOW) & (base <= TEAM_HIGH) & opq).sum()),
                           "literal_fe": remapped, "exact": dec.exact[i]})
            if render:
                stem = out / rel / f"{i:04d}"
                save_index_png(Path(f"{stem}.png"), base, palette)
                save_mask_png(Path(f"{stem}_mask.png"), opq)
                save_index_png(Path(f"{stem}_2x.png"), doubled, palette)
        entry["frames"] = frames
        entry["rendered"] = render
        if render:
            (out / rel).mkdir(parents=True, exist_ok=True)
            (out / rel / "manifest.json").write_text(json.dumps(entry, indent=1, sort_keys=True), encoding="utf-8")
        entry["frames"] = f"{len(frames)} frames" if render else frames
        files.append(entry)
    after = listing_digest(game)
    manifest = {
        "tool": "g1_hd_extract", "palette": {"file": "pal/imjin2.pal", "rule": PAL_RULE,
                                             "sha256": sha256_file(game / "pal" / "imjin2.pal"),
                                             "literal_fe_replacement_index": fe_to},
        "transparent_index": TRANSPARENT, "team_colors": [TEAM_LOW, TEAM_HIGH],
        "image_dirs": list(image_dirs), "summary": summary, "unclassified": unclassified,
        "source_listing_before": before, "source_listing_after": after,
        "source_unchanged": before == after, "files": files,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")
    return manifest


# --- cross checks ------------------------------------------------------------

def roundtrip(game: Path, count: int, seed: int) -> dict[str, Any]:
    """X-3: re-encode decoded frames and compare with the original frame bytes."""
    rng = random.Random(seed)
    spr = [p for p in iter_assets(game) if p.suffix.lower() == ".spr"]
    ytl = [p for p in iter_assets(game) if p.suffix.lower() == ".ytl"]
    picks = rng.sample(spr, min(count, len(spr))) + rng.sample(ytl, min(count, len(ytl)))
    result: dict[str, Any] = {"files": 0, "frames": 0, "identical": 0, "different": [], "skipped": []}
    for path in picks:
        data = path.read_bytes()
        try:
            dec = decode_ytl(data) if path.suffix.lower() == ".ytl" else decode_spr(data)
        except AssetError as exc:
            result["skipped"].append({"path": path.name, "reason": str(exc)})
            continue
        if dec.kind == "raw":
            result["skipped"].append({"path": path.name, "reason": "raw has no RLE"})
            continue
        pix = data[SPR_FIXED_HEADER:]
        fc = len(dec.idx)
        base = YTL_OFFSET_TABLE if dec.kind == "ytl" else SPR_OFFSET_TABLE
        offs = list(struct.unpack_from(f"<{fc}I", data, YTL_OFFSET_TABLE)) if dec.kind == "ytl" else (
            [0] + list(struct.unpack_from("<299I", data, base))[: fc - 1])
        limit = len(pix)
        result["files"] += 1
        for i in range(fc):
            end = offs[i + 1] if i + 1 < fc else limit
            original = pix[offs[i]:end]
            enc = ytl_encode_frame(dec.idx[i], dec.opaque[i]) if dec.kind == "ytl" else rle_encode(dec.idx[i], dec.opaque[i])
            result["frames"] += 1
            if enc == original:
                result["identical"] += 1
            elif len(result["different"]) < 20:
                result["different"].append({"path": path.name, "frame": i, "orig": len(original), "enc": len(enc)})
    return result


def xcheck(game: Path, re_parsers: Path, count: int, seed: int) -> dict[str, Any]:
    """X-2: compare with the RE python parsers (transparent mapped to their convention)."""
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(re_parsers))
    try:
        spr_mod = importlib.import_module("spr_parser")
        ytl_mod = importlib.import_module("ytl_parser")
    finally:
        sys.path.remove(str(re_parsers))
    rng = random.Random(seed)
    buckets: dict[str, list[Path]] = {}
    for path in iter_assets(game):
        suffix = path.suffix.lower()
        if suffix == ".bmp":
            continue
        try:
            dec, _ = decode_file(path)
        except AssetError:
            continue
        if suffix == ".ytl":
            key = "ytl"
        else:
            key = "raw" if dec.kind == "raw" else ("fallback" if dec.sheet_record.startswith("zero") else "rle")
        buckets.setdefault(f"{key}_{'single' if len(dec.idx) == 1 else 'multi'}", []).append(path)
    report: dict[str, Any] = {}
    for key, paths in sorted(buckets.items()):
        picked = rng.sample(paths, min(count, len(paths)))
        rows = []
        for path in picked:
            dec, _ = decode_file(path)
            ref = (ytl_mod.YtlFile if key.startswith("ytl") else spr_mod.SprFile).from_file(path)
            transparent = 0xFE if key.startswith("ytl") else 0
            equal = nontrivial = 0
            for i in range(len(dec.idx)):
                mine = np.where(dec.opaque[i], dec.idx[i], transparent).ravel()
                theirs = np.array(ref.get_frame(i), dtype=np.uint8)
                same = mine.size == theirs.size and np.array_equal(mine, theirs)
                equal += int(same)
                nontrivial += int(same and bool(dec.opaque[i].any()))
            rows.append({"path": path.relative_to(game).as_posix(), "frames": len(dec.idx),
                         "equal": equal, "equal_with_opaque_pixels": nontrivial})
        report[key] = {"population": len(paths), "sampled": len(rows),
                       "files_fully_equal": sum(r["frames"] == r["equal"] for r in rows), "rows": rows}
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("extract")
    ex.add_argument("--game", type=Path, default=DEFAULT_GAME)
    ex.add_argument("--out", type=Path, required=True)
    ex.add_argument("--image-dirs", default=",".join(DEFAULT_IMAGE_DIRS))
    ex.add_argument("--only", action="append", default=[])
    ex.add_argument("--census-only", action="store_true")
    rt = sub.add_parser("roundtrip")
    rt.add_argument("--game", type=Path, default=DEFAULT_GAME)
    rt.add_argument("--count", type=int, default=10)
    rt.add_argument("--seed", type=int, default=1157)
    xc = sub.add_parser("xcheck")
    xc.add_argument("--game", type=Path, default=DEFAULT_GAME)
    xc.add_argument("--re-parsers", type=Path, required=True)
    xc.add_argument("--count", type=int, default=10)
    xc.add_argument("--seed", type=int, default=1157)
    args = parser.parse_args(argv)
    if args.cmd == "extract":
        repo = Path(__file__).resolve().parents[1]
        manifest = extract(args.game, args.out, tuple(d for d in args.image_dirs.split(",") if d),
                           tuple(args.only), args.census_only, repo)
        print(json.dumps({"summary": manifest["summary"], "unclassified": manifest["unclassified"],
                          "source_unchanged": manifest["source_unchanged"]}, ensure_ascii=False, indent=1))
        return 0 if manifest["source_unchanged"] else 2
    if args.cmd == "roundtrip":
        print(json.dumps(roundtrip(args.game, args.count, args.seed), ensure_ascii=False, indent=1))
        return 0
    print(json.dumps(xcheck(args.game, args.re_parsers, args.count, args.seed), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
