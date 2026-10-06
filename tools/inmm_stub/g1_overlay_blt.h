#ifndef G1_OVERLAY_BLT_H
#define G1_OVERLAY_BLT_H

#include <stddef.h>
#include <stdint.h>

#include "g1_scale2x_core.h"

/* Small colorkey BltFast overlays (hover tooltips) land on the back buffer
 * after the panel transfer.  Only pixels the blit changed are mirrored. */
#define G1_OVERLAY_MAX_WIDTH 320u
#define G1_OVERLAY_MAX_HEIGHT 160u
#define G1_OVERLAY_SCREEN_WIDTH 800u
#define G1_OVERLAY_SCREEN_HEIGHT 600u
#define G1_OVERLAY_REGION_PIXELS \
    ((G1_OVERLAY_MAX_WIDTH + 2u) * (G1_OVERLAY_MAX_HEIGHT + 2u))
/* post frame + all-ones mask + 2x2 scale buffer */
#define G1_OVERLAY_SCRATCH_BYTES (G1_OVERLAY_REGION_PIXELS * 6u)

static inline int g1_overlay_blt_accepts(int destination_is_primary,
                                         int source_is_panel,
                                         int colorkey, int source_rect_present,
                                         size_t destination_width,
                                         size_t destination_height,
                                         size_t x, size_t y,
                                         size_t width, size_t height)
{
    return !destination_is_primary && !source_is_panel && colorkey &&
           source_rect_present && width && height &&
           width <= G1_OVERLAY_MAX_WIDTH && height <= G1_OVERLAY_MAX_HEIGHT &&
           destination_width >= G1_OVERLAY_SCREEN_WIDTH &&
           destination_height == G1_OVERLAY_SCREEN_HEIGHT &&
           x <= G1_OVERLAY_SCREEN_WIDTH && y <= G1_OVERLAY_SCREEN_HEIGHT &&
           width <= G1_OVERLAY_SCREEN_WIDTH - x &&
           height <= G1_OVERLAY_SCREEN_HEIGHT - y;
}

typedef struct {
    size_t changed;
    size_t unchanged;
} G1OverlayStats;

/* before: width*height rect copy taken ahead of the blit (stride = width).
 * after: the whole post-blit back buffer.  For every changed pixel the
 * screen mirror gets the post value, covered=1 and either the Scale2x block
 * (neighbours read from the post frame, like a whole-frame Scale2x) or a
 * nearest 2x2 block.  Unchanged (colorkey/same-value) pixels keep their
 * existing coverage. */
static inline int g1_overlay_blt_apply(
    const uint8_t *before, const uint8_t *after, size_t after_stride,
    size_t x, size_t y, size_t width, size_t height, int use_scale2x,
    uint8_t *scratch, uint8_t *screen_expected, uint8_t *screen_covered,
    uint8_t *screen_hd, size_t screen_hd_stride, G1OverlayStats *stats)
{
    size_t x0, y0, x1, y1, rw, rh, row, col;
    uint8_t *post, *mask, *hd;
    G1OverlayStats result = {0u, 0u};
    if (!before || !after || !scratch || !screen_expected || !screen_covered ||
        !screen_hd || !stats || after_stride < G1_OVERLAY_SCREEN_WIDTH ||
        screen_hd_stride < G1_OVERLAY_SCREEN_WIDTH * 2u ||
        !g1_overlay_blt_accepts(0, 0, 1, 1, G1_OVERLAY_SCREEN_WIDTH,
                                G1_OVERLAY_SCREEN_HEIGHT, x, y, width, height))
        return 0;
    x0 = x ? x - 1u : 0u;
    y0 = y ? y - 1u : 0u;
    x1 = x + width < G1_OVERLAY_SCREEN_WIDTH ? x + width + 1u : x + width;
    y1 = y + height < G1_OVERLAY_SCREEN_HEIGHT ? y + height + 1u : y + height;
    rw = x1 - x0;
    rh = y1 - y0;
    post = scratch;
    mask = post + G1_OVERLAY_REGION_PIXELS;
    hd = mask + G1_OVERLAY_REGION_PIXELS;
    for (row = 0u; row < rh; ++row)
        for (col = 0u; col < rw; ++col) {
            post[row * rw + col] = after[(y0 + row) * after_stride + x0 + col];
            mask[row * rw + col] = 1u;
        }
    if (use_scale2x &&
        !g1_scale2x_build_masked(post, rw, mask, rw, rw, rh, hd, rw * 2u))
        return 0;
    for (row = 0u; row < height; ++row) {
        for (col = 0u; col < width; ++col) {
            size_t sx = x + col, sy = y + row;
            size_t px = sx - x0, py = sy - y0;
            uint8_t value = post[py * rw + px];
            size_t logical = sy * G1_OVERLAY_SCREEN_WIDTH + sx;
            uint8_t *out = screen_hd + sy * 2u * screen_hd_stride + sx * 2u;
            if (value == before[row * width + col]) {
                ++result.unchanged;
                continue;
            }
            if (use_scale2x) {
                const uint8_t *in = hd + py * 2u * rw * 2u + px * 2u;
                out[0] = in[0]; out[1] = in[1];
                out[screen_hd_stride] = in[rw * 2u];
                out[screen_hd_stride + 1u] = in[rw * 2u + 1u];
            } else {
                out[0] = out[1] = value;
                out[screen_hd_stride] = out[screen_hd_stride + 1u] = value;
            }
            screen_expected[logical] = value;
            screen_covered[logical] = 1u;
            ++result.changed;
        }
    }
    *stats = result;
    return 1;
}

/* H-D2r: same contract as g1_overlay_blt_apply for a rect taller than
 * G1_OVERLAY_MAX_HEIGHT (up to the screen height).  before is width*height
 * rows with stride = width; the rect is applied in row bands of at most
 * G1_OVERLAY_MAX_HEIGHT rows.  Every band reads its halo from the real post
 * frame, so the bands together equal one whole-frame Scale2x.  The geometry is
 * validated before any band is applied; *bands is the number of bands applied
 * (0 on reject). */
static inline int g1_overlay_blt_apply_banded(
    const uint8_t *before, const uint8_t *after, size_t after_stride,
    size_t x, size_t y, size_t width, size_t height, int use_scale2x,
    uint8_t *scratch, uint8_t *screen_expected, uint8_t *screen_covered,
    uint8_t *screen_hd, size_t screen_hd_stride, G1OverlayStats *stats,
    size_t *bands)
{
    G1OverlayStats total = {0u, 0u};
    size_t row = 0u, count = 0u;
    if (bands) *bands = 0u;
    if (!before || !bands || !stats || !height || height > G1_OVERLAY_SCREEN_HEIGHT ||
        !g1_overlay_blt_accepts(0, 0, 1, 1, G1_OVERLAY_SCREEN_WIDTH,
                                G1_OVERLAY_SCREEN_HEIGHT, x, y, width,
                                height < G1_OVERLAY_MAX_HEIGHT
                                    ? height : G1_OVERLAY_MAX_HEIGHT) ||
        y > G1_OVERLAY_SCREEN_HEIGHT - height)
        return 0;
    while (row < height) {
        G1OverlayStats band;
        size_t rows = height - row < G1_OVERLAY_MAX_HEIGHT
                          ? height - row : G1_OVERLAY_MAX_HEIGHT;
        if (!g1_overlay_blt_apply(before + row * width, after, after_stride, x,
                                  y + row, width, rows, use_scale2x, scratch,
                                  screen_expected, screen_covered, screen_hd,
                                  screen_hd_stride, &band))
            return 0;
        total.changed += band.changed;
        total.unchanged += band.unchanged;
        row += rows;
        ++count;
    }
    *stats = total;
    *bands = count;
    return 1;
}

/* H-D2t: rects wider than G1_OVERLAY_MAX_WIDTH (a selection outline can span the
 * screen).  before: the whole width*height rect copy (stride = width); it is
 * applied in tiles of at most MAX_WIDTH x MAX_HEIGHT, each copied into the
 * caller's tile buffer (MAX_WIDTH * MAX_HEIGHT bytes).  The halo is read from
 * the real post frame, so the tiles together equal one whole-frame Scale2x.
 * The geometry is validated before any tile is applied; *tiles is the number
 * of tiles applied (0 on reject). */
static inline int g1_overlay_blt_apply_tiled(
    const uint8_t *before, const uint8_t *after, size_t after_stride,
    size_t x, size_t y, size_t width, size_t height, int use_scale2x,
    uint8_t *scratch, uint8_t *tile, uint8_t *screen_expected,
    uint8_t *screen_covered, uint8_t *screen_hd, size_t screen_hd_stride,
    G1OverlayStats *stats, size_t *tiles)
{
    G1OverlayStats total = {0u, 0u};
    size_t row = 0u, col, count = 0u, line;
    if (tiles) *tiles = 0u;
    if (!before || !tile || !tiles || !stats || !width || !height ||
        width > G1_OVERLAY_SCREEN_WIDTH || height > G1_OVERLAY_SCREEN_HEIGHT ||
        !g1_overlay_blt_accepts(0, 0, 1, 1, G1_OVERLAY_SCREEN_WIDTH,
                                G1_OVERLAY_SCREEN_HEIGHT, x, y,
                                width < G1_OVERLAY_MAX_WIDTH
                                    ? width : G1_OVERLAY_MAX_WIDTH,
                                height < G1_OVERLAY_MAX_HEIGHT
                                    ? height : G1_OVERLAY_MAX_HEIGHT) ||
        width > G1_OVERLAY_SCREEN_WIDTH - x || height > G1_OVERLAY_SCREEN_HEIGHT - y)
        return 0;
    while (row < height) {
        size_t rows = height - row < G1_OVERLAY_MAX_HEIGHT
                          ? height - row : G1_OVERLAY_MAX_HEIGHT;
        col = 0u;
        while (col < width) {
            G1OverlayStats part;
            size_t cols = width - col < G1_OVERLAY_MAX_WIDTH
                              ? width - col : G1_OVERLAY_MAX_WIDTH;
            for (line = 0u; line < rows; ++line) {
                size_t k;
                for (k = 0u; k < cols; ++k)
                    tile[line * cols + k] = before[(row + line) * width + col + k];
            }
            if (!g1_overlay_blt_apply(tile, after, after_stride, x + col, y + row,
                                      cols, rows, use_scale2x, scratch,
                                      screen_expected, screen_covered, screen_hd,
                                      screen_hd_stride, &part))
                return 0;
            total.changed += part.changed;
            total.unchanged += part.unchanged;
            col += cols;
            ++count;
        }
        row += rows;
    }
    *stats = total;
    *tiles = count;
    return 1;
}

#endif
