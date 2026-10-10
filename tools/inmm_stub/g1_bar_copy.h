#ifndef G1_BAR_COPY_H
#define G1_BAR_COPY_H

#include <stddef.h>
#include <stdint.h>

#include "g1_frame_copy.h"

/* H-RS3: the result table's gradient bars (PS29) are drawn by 0x468BB0, a keyless
 * strided rectangle copy `dst + dy*dst_pitch + dx <- src + sy0*src_pitch + sx0`
 * with an inclusive source rectangle [sx0..sx1] x [sy0..sy1].  The mirror packs
 * the source rows and hands them to the existing block copy.  These helpers stay
 * free of game types. */

/* Width/height of the inclusive source rectangle, only when the source origin is
 * valid and the destination rectangle lies inside the 800x600 screen. */
static inline int g1_bar_copy_rect(int32_t sx0, int32_t sy0, int32_t sx1, int32_t sy1,
                                   int32_t dx, int32_t dy, size_t *width, size_t *height)
{
    size_t w, h;
    if (!width || !height || sx0 < 0 || sy0 < 0 || dx < 0 || dy < 0 ||
        sx1 < sx0 || sy1 < sy0) return 0;
    w = (size_t)((int64_t)sx1 - sx0 + 1);
    h = (size_t)((int64_t)sy1 - sy0 + 1);
    if (!g1_frame_copy_accepts((size_t)dx, (size_t)dy, w, h)) return 0;
    *width = w;
    *height = h;
    return 1;
}

/* Byte offset of the source rectangle's first pixel and the span a reader must be
 * able to read (last row ends at its width, not at the pitch). */
static inline int g1_bar_copy_source_span(size_t sx0, size_t sy0, size_t src_pitch,
                                          size_t width, size_t height,
                                          size_t *offset, size_t *span)
{
    if (!offset || !span || !width || !height || src_pitch < sx0 + width) return 0;
    *offset = sy0 * src_pitch + sx0;
    *span = (height - 1u) * src_pitch + width;
    return 1;
}

/* Packs the source rectangle into out (width*height bytes, stride == width).
 * Returns the pixel count, 0 when nothing was written. */
static inline size_t g1_bar_copy_pack(const uint8_t *src, size_t src_pitch, size_t sx0,
                                      size_t sy0, size_t width, size_t height, uint8_t *out)
{
    size_t offset, span, row, col;
    if (!src || !out ||
        !g1_bar_copy_source_span(sx0, sy0, src_pitch, width, height, &offset, &span))
        return 0u;
    for (row = 0u; row < height; ++row) {
        const uint8_t *in = src + offset + row * src_pitch;
        for (col = 0u; col < width; ++col) out[row * width + col] = in[col];
    }
    return width * height;
}

#endif
