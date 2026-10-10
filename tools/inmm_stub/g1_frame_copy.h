#ifndef G1_FRAME_COPY_H
#define G1_FRAME_COPY_H

#include <stddef.h>
#include <stdint.h>

#include "g1_scale2x_core.h"

/* H-P35: a packed (stride == width) rectangle copied into the 800x600 screen
 * buffer by 0x466280 (partial menu/panel blocks) or by the full-frame offscreen
 * BltFast the load-slot screen issues every frame.  Unlike the overlay diff
 * mirror, every pixel of the rectangle is mirrored: a copy that rewrites the
 * same value (a black backdrop over black) still has to cover that pixel. */
#define G1_FRAME_COPY_SCREEN_WIDTH 800u
#define G1_FRAME_COPY_SCREEN_HEIGHT 600u

static inline int g1_frame_copy_accepts(size_t x, size_t y, size_t width, size_t height)
{
    return width && height &&
           x <= G1_FRAME_COPY_SCREEN_WIDTH && y <= G1_FRAME_COPY_SCREEN_HEIGHT &&
           width <= G1_FRAME_COPY_SCREEN_WIDTH - x &&
           height <= G1_FRAME_COPY_SCREEN_HEIGHT - y;
}

/* src is width*height packed bytes.  mask is width*height bytes the caller
 * filled with 1 (the bridge links without a C runtime, so the fill stays out of
 * this header) and hd is width*height*4 bytes of scratch; both are unused for
 * nearest.  Neighbours beyond the
 * rectangle replicate its edge, so a partial rectangle differs from a
 * whole-frame Scale2x only on its outer ring. */
static inline int g1_frame_copy_apply(
    const uint8_t *src, size_t x, size_t y, size_t width, size_t height,
    int use_scale2x, uint8_t *mask, uint8_t *hd, uint8_t *screen_expected,
    uint8_t *screen_covered, uint8_t *screen_hd, size_t screen_hd_stride)
{
    size_t row, col;
    if (!src || !screen_expected || !screen_covered || !screen_hd ||
        !g1_frame_copy_accepts(x, y, width, height) ||
        screen_hd_stride < G1_FRAME_COPY_SCREEN_WIDTH * 2u) return 0;
    if (use_scale2x) {
        if (!mask || !hd) return 0;
        if (!g1_scale2x_build_masked(src, width, mask, width, width, height,
                                     hd, width * 2u)) return 0;
    }
    for (row = 0u; row < height; ++row) {
        for (col = 0u; col < width; ++col) {
            size_t logical = (y + row) * G1_FRAME_COPY_SCREEN_WIDTH + x + col;
            uint8_t *out = screen_hd + (y + row) * 2u * screen_hd_stride + (x + col) * 2u;
            if (use_scale2x) {
                const uint8_t *in = hd + row * 2u * width * 2u + col * 2u;
                out[0] = in[0]; out[1] = in[1];
                out[screen_hd_stride] = in[width * 2u];
                out[screen_hd_stride + 1u] = in[width * 2u + 1u];
            } else {
                out[0] = out[1] = src[row * width + col];
                out[screen_hd_stride] = out[screen_hd_stride + 1u] = src[row * width + col];
            }
            screen_covered[logical] = 1u;
            screen_expected[logical] = src[row * width + col];
        }
    }
    return 1;
}

#endif
