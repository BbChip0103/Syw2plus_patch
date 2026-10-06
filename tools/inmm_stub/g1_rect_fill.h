#ifndef G1_RECT_FILL_H
#define G1_RECT_FILL_H

#include <stdint.h>

/* Clipped solid rectangle fill at 0x466070 (thiscall, ret 0x14).  Arguments
 * are two inclusive corners; each axis pair is sorted, then intersected with
 * the renderer clip (xmin, ymin, xmax, ymax, inclusive) exactly like the
 * original before it writes bytes row by row. */
typedef struct {
    int32_t x, y;
    uint32_t width, height;
} G1RectFill;

static inline int g1_rect_fill_region(int32_t x1, int32_t y1, int32_t x2,
                                      int32_t y2, const int32_t clip[4],
                                      G1RectFill *out)
{
    int32_t xmin = x1 < x2 ? x1 : x2, xmax = x1 < x2 ? x2 : x1;
    int32_t ymin = y1 < y2 ? y1 : y2, ymax = y1 < y2 ? y2 : y1;
    if (xmax < clip[0] || xmin > clip[2] || ymax < clip[1] || ymin > clip[3])
        return 0;
    if (xmin < clip[0]) xmin = clip[0];
    if (ymin < clip[1]) ymin = clip[1];
    if (xmax > clip[2]) xmax = clip[2];
    if (ymax > clip[3]) ymax = clip[3];
    if (xmin > xmax || ymin > ymax) return 0;
    out->x = xmin;
    out->y = ymin;
    out->width = (uint32_t)((int64_t)xmax - xmin + 1);
    out->height = (uint32_t)((int64_t)ymax - ymin + 1);
    return 1;
}

/* Same sorted+clipped rectangle as g1_rect_fill_region, limited to the visible screen
 * [0, screen_w) x [0, screen_h).  The renderer clip can open into the stride padding
 * (xmax = stride - 1), where the original draws but nothing is mirrored. */
static inline int g1_rect_screen_region(int32_t x1, int32_t y1, int32_t x2,
                                        int32_t y2, const int32_t clip[4],
                                        int32_t screen_w, int32_t screen_h,
                                        G1RectFill *out)
{
    int32_t visible[4];
    visible[0] = clip[0] > 0 ? clip[0] : 0;
    visible[1] = clip[1] > 0 ? clip[1] : 0;
    visible[2] = clip[2] < screen_w - 1 ? clip[2] : screen_w - 1;
    visible[3] = clip[3] < screen_h - 1 ? clip[3] : screen_h - 1;
    return g1_rect_fill_region(x1, y1, x2, y2, visible, out);
}

/* Clipped line at 0x4659B0 (thiscall, ret 0x14, args x0 y0 x1 y1 colour).  The original
 * plots max(|dx|,|dy|)+2 points through the 0x465900 clip (renderer xmin, ymin, xmax,
 * ymax inclusive) and only ever steps from (x0,y0) toward (x1,y1), so every written pixel
 * lies inside the end-point bounding box.  The region grows that box by 1 px on every
 * side (cheap margin, the diff mirror ignores unchanged pixels) before the clip.  The
 * original does its differences in int32; a pair whose difference overflows is not
 * mirrored. */
static inline int g1_line_region(int32_t x0, int32_t y0, int32_t x1, int32_t y1,
                                 const int32_t clip[4], G1RectFill *out)
{
    int64_t xmin, xmax, ymin, ymax;
    int64_t dx = (int64_t)x1 - x0, dy = (int64_t)y1 - y0;
    if (dx < INT32_MIN || dx > INT32_MAX || dy < INT32_MIN || dy > INT32_MAX) return 0;
    xmin = (x0 < x1 ? x0 : x1) - (int64_t)1;
    xmax = (x0 < x1 ? x1 : x0) + (int64_t)1;
    ymin = (y0 < y1 ? y0 : y1) - (int64_t)1;
    ymax = (y0 < y1 ? y1 : y0) + (int64_t)1;
    if (xmax < clip[0] || xmin > clip[2] || ymax < clip[1] || ymin > clip[3]) return 0;
    if (xmin < clip[0]) xmin = clip[0];
    if (ymin < clip[1]) ymin = clip[1];
    if (xmax > clip[2]) xmax = clip[2];
    if (ymax > clip[3]) ymax = clip[3];
    if (xmin > xmax || ymin > ymax) return 0;
    out->x = (int32_t)xmin;
    out->y = (int32_t)ymin;
    out->width = (uint32_t)(xmax - xmin + 1);
    out->height = (uint32_t)(ymax - ymin + 1);
    return 1;
}

/* Unclipped solid rectangle at 0x465E80 (thiscall, ret 0x14).  The original
 * writes nothing unless both x corners are in [0, stride) and both y corners
 * are in [0, ybound) (signed compares, no clipping), then sorts each axis pair
 * and fills both ends inclusive.  The mirror covers only the part inside the
 * logical screen; the stride padding (x >= screen_w) is never mirrored. */
static inline int g1_rect_solid_region(int32_t x0, int32_t y0, int32_t x1,
                                       int32_t y1, int32_t stride,
                                       int32_t ybound, int32_t screen_w,
                                       int32_t screen_h, G1RectFill *out)
{
    int32_t xmin, xmax, ymin, ymax;
    if (x0 < 0 || x0 >= stride || x1 < 0 || x1 >= stride) return 0;
    if (y0 < 0 || y0 >= ybound || y1 < 0 || y1 >= ybound) return 0;
    xmin = x0 < x1 ? x0 : x1;
    xmax = x0 < x1 ? x1 : x0;
    ymin = y0 < y1 ? y0 : y1;
    ymax = y0 < y1 ? y1 : y0;
    if (xmin >= screen_w || ymin >= screen_h) return 0;
    if (xmax >= screen_w) xmax = screen_w - 1;
    if (ymax >= screen_h) ymax = screen_h - 1;
    out->x = xmin;
    out->y = ymin;
    out->width = (uint32_t)(xmax - xmin + 1);
    out->height = (uint32_t)(ymax - ymin + 1);
    return 1;
}

/* Unclipped flipped remap RLE at 0x466B50 (thiscall, ret 0x18).  x, y, width
 * and height are full signed 32-bit values and the original never clips, so a
 * rectangle past the screen edge writes into the stride padding or wraps into
 * the next row.  The mirror covers only the intersection with the logical
 * screen.  `wrap` is set for every positive-size rectangle that leaves
 * [0, stride) x [0, screen_h), `clipped` when the intersection is smaller than
 * the rectangle.  Returns 0 for non-positive sizes (wrap untouched) or an empty
 * intersection (wrap valid). */
typedef struct {
    int32_t x, y;
    uint32_t width, height;
    int clipped, wrap;
} G1FlipRleRegion;

static inline int g1_flip_rle_region(int32_t x, int32_t y, int32_t width,
                                     int32_t height, int32_t stride,
                                     int32_t screen_w, int32_t screen_h,
                                     G1FlipRleRegion *out)
{
    int64_t x1, y1, x0c, y0c, x1c, y1c;
    out->clipped = out->wrap = 0;
    if (width <= 0 || height <= 0) return 0;
    x1 = (int64_t)x + width;
    y1 = (int64_t)y + height;
    out->wrap = x < 0 || x1 > stride || y < 0 || y1 > screen_h;
    x0c = x < 0 ? 0 : x;
    y0c = y < 0 ? 0 : y;
    x1c = x1 > screen_w ? screen_w : x1;
    y1c = y1 > screen_h ? screen_h : y1;
    if (x0c >= x1c || y0c >= y1c) return 0;
    out->clipped = x0c != x || y0c != y || x1c != x1 || y1c != y1;
    out->x = (int32_t)x0c;
    out->y = (int32_t)y0c;
    out->width = (uint32_t)(x1c - x0c);
    out->height = (uint32_t)(y1c - y0c);
    return 1;
}

#endif
