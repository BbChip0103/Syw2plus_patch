#ifndef G1_BLEND_KEY_H
#define G1_BLEND_KEY_H

#include <stddef.h>
#include <stdint.h>

/* H-HDB0: 0x4672E0 (50% translucent RLE, the HUD logo) as an identity key.  The original reads the destination:
 * per channel (d >> 1) + (s >> 1) over renderer + 0x419A0 (R,G,B per palette index), then the inverse LUT
 * renderer + 0x19A0 [((c0 << 6) + c1) << 6 + c2].  Stream: a row consumes tokens until its column reaches
 * the width; 0xFE n skips n columns (n may be 0), any other byte is a source index.  Pure functions, no engine state. */
#define G1_BLEND_KEY_SKIP 0xFEu
#define G1_BLEND_INVERSE_BYTES 0x40000u
/* H-HDB1: 0x467580 combines the channels through a 64 x 64 signed 16-bit weight table (renderer + 0x41CA0) instead of
 * averaging: t = (int16)T[(dest channel << 6) + source channel], offset = (((t0 << 6) + t1) << 6) + t2.  Every pure
 * function below takes `weights`; NULL keeps the 0x4672E0 average. */
#define G1_BLEND_WEIGHT_ENTRIES 4096u

/* idx/mask are width*height (row-major).  Returns the stream bytes consumed, 0 when the stream is longer than limit. */
static inline size_t g1_blend_decode_rle(const uint8_t *rle, size_t limit, size_t width, size_t height,
                                         uint8_t *idx, uint8_t *mask)
{
    size_t pos = 0u, row, col;
    if (!rle || !idx || !mask || !width || !height) return 0u;
    for (row = 0u; row < height; ++row) {
        col = 0u;
        while (col < width) {
            if (pos >= limit) return 0u;
            if (rle[pos] == G1_BLEND_KEY_SKIP) {
                if (pos + 1u >= limit) return 0u;
                col += rle[pos + 1u];
                pos += 2u;
                continue;
            }
            idx[row * width + col] = rle[pos];
            mask[row * width + col] = 1u;
            ++col;
            ++pos;
        }
    }
    return pos;
}

/* H-HDB3: 0x467FD0 and 0x4685C0 draw the same stream right to left: the token at stream column c lands on screen column
 * x + (width - c - 1).  Reversing every row of the decoded planes gives the screen-direction planes, which the rest of the
 * key path (crop, self check, identity bind) then treats like the unflipped writers' planes.  The DLL links without a C
 * runtime, so the swap loop must not be turned into a memcpy call. */
static inline __attribute__((optimize("no-tree-loop-distribute-patterns"))) void g1_blend_flip_rows(uint8_t *plane,
                                                                                                      size_t width, size_t height)
{
    size_t row, left;
    for (row = 0u; row < height; ++row)
        for (left = 0u; left < width / 2u; ++left) {
            uint8_t swap = plane[row * width + left];
            plane[row * width + left] = plane[row * width + width - 1u - left];
            plane[row * width + width - 1u - left] = swap;
        }
}

/* H-HDB4: 0x4678C0 and 0x468360 (7 stack args: x y width height rle remap level) combine the channels through the
 * DWORD table renderer + 0x43CA0: t = T[((level << 6) + d channel) << 6) + s channel], s = remap[token].  The table is
 * built once by 0x4654D0 with `level` slices 0..9 of 64 x 64 DWORDs (outer loop 0, 10 .. 90 below 0x64), every entry in
 * 0..63.  A slice has the shape of the 0x467580 int16 table, so one call copies its slice into an int16 table and the
 * shared weighted functions above do the rest.  A level outside the 10 slices (the original would read other renderer
 * memory) or an entry that does not survive the int16 round trip is refused (returns 0). */
#define G1_BLEND_LEVEL_SLICES 10u

static inline __attribute__((optimize("no-tree-loop-distribute-patterns"))) int g1_blend_level_weights(
    const uint32_t *table, int32_t level, int16_t *out)
{
    size_t index;
    if (!table || !out || level < 0 || (uint32_t)level >= G1_BLEND_LEVEL_SLICES) return 0;
    table += (size_t)level * G1_BLEND_WEIGHT_ENTRIES;
    for (index = 0u; index < G1_BLEND_WEIGHT_ENTRIES; ++index) {
        int32_t value = (int32_t)table[index];
        if (value != (int32_t)(int16_t)value) return 0;
        out[index] = (int16_t)value;
    }
    return 1;
}

/* The source plane of the 7-arg writers: the stream token goes through the 256 B remap table (opaque pixels only). */
static inline __attribute__((optimize("no-tree-loop-distribute-patterns"))) void g1_blend_remap_plane(
    const uint8_t *remap, const uint8_t *idx, const uint8_t *mask, size_t count, uint8_t *out)
{
    size_t index;
    for (index = 0u; index < count; ++index) out[index] = mask[index] ? remap[idx[index]] : 0u;
}

/* Same arithmetic as the original (32-bit, unmasked).  Returns the inverse LUT offset. */
static inline uint32_t g1_blend_lut_offset(const uint8_t *palette, uint8_t d, uint8_t s)
{
    uint32_t c0 = (uint32_t)(palette[d * 3u] >> 1) + (uint32_t)(palette[s * 3u] >> 1);
    uint32_t c1 = (uint32_t)(palette[d * 3u + 1u] >> 1) + (uint32_t)(palette[s * 3u + 1u] >> 1);
    uint32_t c2 = (uint32_t)(palette[d * 3u + 2u] >> 1) + (uint32_t)(palette[s * 3u + 2u] >> 1);
    return (((c0 << 6) + c1) << 6) + c2;
}

/* 0x467580: inverse LUT offset through the weight table.  Returns 0 when a channel pair indexes outside the 64 x 64
 * table or the offset leaves the inverse LUT (the original would read other renderer memory; the pixel is refused). */
static inline int g1_blend_weighted_offset(const uint8_t *palette, const int16_t *weights, uint8_t d, uint8_t s,
                                           uint32_t *offset)
{
    uint32_t t[3], channel, index, value;
    for (channel = 0u; channel < 3u; ++channel) {
        index = ((uint32_t)palette[d * 3u + channel] << 6) + (uint32_t)palette[s * 3u + channel];
        if (index >= G1_BLEND_WEIGHT_ENTRIES) return 0;
        t[channel] = (uint32_t)(int32_t)weights[index];
    }
    value = (((t[0] << 6) + t[1]) << 6) + t[2];
    if (value >= G1_BLEND_INVERSE_BYTES) return 0;     /* unsigned compare also refuses a negative offset */
    *offset = value;
    return 1;
}

/* 1 when the blended index is computable: the offset is inside the 64x64x64 table. */
static inline int g1_blend_pixel(const uint8_t *palette, const uint8_t *inverse, const int16_t *weights,
                                 uint8_t d, uint8_t s, uint8_t *out)
{
    uint32_t offset;
    if (weights) {
        if (!g1_blend_weighted_offset(palette, weights, d, s, &offset)) return 0;
    } else {
        offset = g1_blend_lut_offset(palette, d, s);
        if (offset >= G1_BLEND_INVERSE_BYTES) return 0;
    }
    *out = inverse[offset];
    return 1;
}

/* H-HDB2: 0x467B00 is 0x467580 plus a clip to the renderer rectangle [left, right] x [top, bottom] (renderer + 0x4D0,
 * 0x4D4, 0x4D8, 0x4DC): right and bottom are INCLUSIVE.  The key checks and draws the screen intersection
 * [x0, x1) x [y0, y1) of the stream rectangle cut by that clip; rows above the clip are parsed but never written, so
 * the cropped window keeps the stream's own row order.  Returns 0 when nothing is left to draw. */
static inline int g1_blend_clip_window(int x0, int y0, int x1, int y1, int32_t left, int32_t top, int32_t right,
                                       int32_t bottom, int *wx0, int *wy0, int *wx1, int *wy1)
{
    int64_t cx0 = left > x0 ? (int64_t)left : (int64_t)x0, cy0 = top > y0 ? (int64_t)top : (int64_t)y0;
    int64_t cx1 = (int64_t)right + 1 < (int64_t)x1 ? (int64_t)right + 1 : (int64_t)x1;
    int64_t cy1 = (int64_t)bottom + 1 < (int64_t)y1 ? (int64_t)bottom + 1 : (int64_t)y1;
    if (cx0 >= cx1 || cy0 >= cy1) return 0;
    *wx0 = (int)cx0;
    *wy0 = (int)cy0;
    *wx1 = (int)cx1;
    *wy1 = (int)cy1;
    return 1;
}

/* Copy the (ox, oy, width, height) window of a src_width wide plane into a compact width wide plane.  The DLL links
 * without a C runtime, so the loop must not be turned into a memcpy call. */
static inline __attribute__((optimize("no-tree-loop-distribute-patterns"))) void g1_blend_crop(const uint8_t *src, size_t src_width, size_t ox, size_t oy, size_t width,
                                 size_t height, uint8_t *dst)
{
    size_t row, col;
    for (row = 0u; row < height; ++row)
        for (col = 0u; col < width; ++col) dst[row * width + col] = src[(oy + row) * src_width + ox + col];
}

/* Self check: the original's output for the rectangle (after, stride after_stride at (x, y)) must equal the formula
 * over the pre-draw copy (before, stride = width) and the decoded stream; pixels outside the mask must be untouched.
 * Returns 1 when all width*height pixels agree; *checked counts the opaque pixels compared. */
static inline int g1_blend_selfcheck(const uint8_t *palette, const uint8_t *inverse, const int16_t *weights,
                                     const uint8_t *before,
                                     const uint8_t *idx, const uint8_t *mask, size_t width, size_t height,
                                     const uint8_t *after, size_t after_stride, size_t *checked)
{
    size_t row, col, count = 0u;
    int agree = 1;
    for (row = 0u; row < height; ++row)
        for (col = 0u; col < width; ++col) {
            uint8_t expected = before[row * width + col];
            if (mask[row * width + col]) {
                ++count;
                if (!g1_blend_pixel(palette, inverse, weights, expected, idx[row * width + col], &expected)) agree = 0;
            }
            if (after[row * after_stride + col] != expected) agree = 0;
        }
    if (checked) *checked = count;
    return agree;
}

/* HD result for the opaque pixels whose destination the screen mirror trusted (covered != 0): each 2x2 block is
 * inverse[avg(hd destination, pack frame)].  hd_before is the 2*width x 2*height destination copy taken ahead of
 * the draw, pack the 2*width x 2*height frame (pack_stride bytes per row), screen the 1600 wide mirror.  A
 * subpixel the pack leaves transparent (key) keeps the screen value.  A caller that draws only a window of a larger
 * stream passes the cropped planes and `pack` advanced to that window (pack_stride unchanged).  Returns the number
 * of pixels written. */
static inline size_t g1_blend_apply_hd(const uint8_t *palette, const uint8_t *inverse, const int16_t *weights,
                                       const uint8_t *mask,
                                       const uint8_t *covered, size_t width, size_t height,
                                       const uint8_t *hd_before, const uint8_t *pack, size_t pack_stride,
                                       uint8_t *screen, size_t screen_stride, size_t x, size_t y,
                                       uint8_t key)
{
    size_t row, col, sub, written = 0u;
    for (row = 0u; row < height; ++row)
        for (col = 0u; col < width; ++col) {
            int whole = 1;
            uint8_t value[4];
            if (!mask[row * width + col] || !covered[row * width + col]) continue;
            for (sub = 0u; sub < 4u; ++sub) {
                size_t hx = col * 2u + (sub & 1u), hy = row * 2u + (sub >> 1);
                uint8_t source = pack[hy * pack_stride + hx];
                if (source == key ||
                    !g1_blend_pixel(palette, inverse, weights, hd_before[hy * width * 2u + hx], source, &value[sub])) {
                    whole = 0;
                    break;
                }
            }
            if (!whole) continue;
            for (sub = 0u; sub < 4u; ++sub)
                screen[(y * 2u + row * 2u + (sub >> 1)) * screen_stride + x * 2u + col * 2u + (sub & 1u)] = value[sub];
            ++written;
        }
    return written;
}

#endif /* G1_BLEND_KEY_H */
