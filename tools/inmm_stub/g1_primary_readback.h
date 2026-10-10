#ifndef G1_PRIMARY_READBACK_H
#define G1_PRIMARY_READBACK_H

#include <stddef.h>
#include <stdint.h>

/* H-RS2: the game reads the primary surface back into an offscreen buffer
 * (PS26 banner prepare 0x4C7D00 -> BltFast(back buffer <- primary), also the
 * PS22 sibling 0x41C7E5).  With the 1600x1200 mirror the primary holds the HD
 * frame, so the readback pulled the HD image into the logical 800x600 buffer
 * (top-left quadrant 2x enlarged, HUD gone).  The repair hands the game the last
 * presented logical frame instead.  The helpers stay free of DirectDraw types. */
#define G1_PRIMARY_READBACK_WIDTH 800u
#define G1_PRIMARY_READBACK_HEIGHT 600u

static inline int g1_primary_readback_applies(int destination_is_primary,
                                              int source_is_primary)
{
    return !destination_is_primary && source_is_primary;
}

/* rect is left, top, right, bottom in logical coordinates or NULL (whole 800x600
 * frame).  Fails when the rectangle leaves the logical frame, is empty, or would
 * not fit the destination at (x, y), so the original call stays in charge. */
static inline int g1_primary_readback_rect(const int32_t *rect, size_t x, size_t y,
                                           size_t dest_width, size_t dest_height,
                                           size_t *sx, size_t *sy, size_t *width,
                                           size_t *height)
{
    size_t left = 0u, top = 0u, w = G1_PRIMARY_READBACK_WIDTH,
           h = G1_PRIMARY_READBACK_HEIGHT;
    if (!sx || !sy || !width || !height) return 0;
    if (rect) {
        if (rect[0] < 0 || rect[1] < 0 || rect[2] <= rect[0] || rect[3] <= rect[1] ||
            (size_t)rect[2] > G1_PRIMARY_READBACK_WIDTH ||
            (size_t)rect[3] > G1_PRIMARY_READBACK_HEIGHT) return 0;
        left = (size_t)rect[0];
        top = (size_t)rect[1];
        w = (size_t)(rect[2] - rect[0]);
        h = (size_t)(rect[3] - rect[1]);
    }
    if (x > dest_width || y > dest_height || w > dest_width - x ||
        h > dest_height - y) return 0;
    *sx = left; *sy = top; *width = w; *height = h;
    return 1;
}

/* frame is the packed logical 800x600 frame.  Returns the pixel count written,
 * 0 when nothing was copied. */
static inline size_t g1_primary_readback_copy(const uint8_t *frame, const int32_t *rect,
                                              size_t x, size_t y, uint8_t *dst,
                                              size_t pitch, size_t dest_width,
                                              size_t dest_height)
{
    size_t sx, sy, w, h, row, col;
    if (!frame || !dst ||
        !g1_primary_readback_rect(rect, x, y, dest_width, dest_height, &sx, &sy, &w, &h) ||
        pitch < dest_width) return 0u;
    for (row = 0u; row < h; ++row) {
        const uint8_t *in = frame + (sy + row) * G1_PRIMARY_READBACK_WIDTH + sx;
        uint8_t *out = dst + (y + row) * pitch + x;
        for (col = 0u; col < w; ++col) out[col] = in[col];
    }
    return w * h;
}

#endif
