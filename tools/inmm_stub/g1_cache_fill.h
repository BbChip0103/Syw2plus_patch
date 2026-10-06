#ifndef G1_CACHE_FILL_H
#define G1_CACHE_FILL_H

#include <stdint.h>

#include "g1_rect_fill.h"

/* Unclipped solid block fill at 0x465FC0 (thiscall, ret 0x14, args x1 y1 x2 y2
 * colour).  Each axis pair is sorted, the row is filled with floor(width / 4)
 * dwords of the replicated colour (so the width is floored to whole 4-pixel
 * dwords at 8 bpp) starting at xmin, and nothing is clipped: a rectangle that
 * leaves [0, row_width) x [0, rows) writes outside the cache (or wraps into the
 * next row).  Returns 1 with the written region, 0 when nothing is written, -1
 * when the write cannot be mirrored (outside the cache or not 8 bpp). */
static inline int g1_cache_fill_region(int32_t x1, int32_t y1, int32_t x2,
                                       int32_t y2, int32_t bits_per_pixel,
                                       int32_t row_width, int32_t rows,
                                       G1RectFill *out)
{
    int32_t xmin = x1 < x2 ? x1 : x2, xmax = x1 < x2 ? x2 : x1;
    int32_t ymin = y1 < y2 ? y1 : y2, ymax = y1 < y2 ? y2 : y1;
    int64_t width = (int64_t)xmax - xmin + 1;
    int64_t written = (width / 4) * 4;
    if (bits_per_pixel != 8) return -1;
    if (written <= 0) return 0;
    if (xmin < 0 || ymin < 0 || ymax >= rows || xmin + written > row_width)
        return -1;
    out->x = xmin;
    out->y = ymin;
    out->width = (uint32_t)written;
    out->height = (uint32_t)((int64_t)ymax - ymin + 1);
    return 1;
}

#endif
