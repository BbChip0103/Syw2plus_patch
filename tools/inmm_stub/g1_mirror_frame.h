#ifndef G1_MIRROR_FRAME_H
#define G1_MIRROR_FRAME_H

#include "g1_scratch_bounds.h"

#define G1_MIRROR_SCREEN_WIDTH 800u
#define G1_MIRROR_CACHE_WIDTH 832u

static inline unsigned g1_mirror_frame_width(int cache_target) {
    return cache_target ? G1_MIRROR_CACHE_WIDTH : G1_MIRROR_SCREEN_WIDTH;
}

/* Clipped replay viewport: screen keeps the original 800x600 window, the
 * cache target spans its whole frame so edge tiles are not cut at x=799. */
static inline void g1_mirror_replay_viewport(int cache_target,
                                             unsigned surface_height,
                                             long viewport[4]) {
    viewport[0] = 0;
    viewport[1] = 0;
    viewport[2] = cache_target ? (long)g1_mirror_frame_width(1) - 1 : 799;
    viewport[3] = cache_target ? (long)surface_height - 1 : 599;
}

/* Unclipped bind: the whole sprite must sit inside the target frame, which is
 * 800 wide for the screen and 832 wide for the cache. */
static inline int g1_mirror_unclipped_bind_fits(long origin_x, long origin_y,
                                                unsigned width, unsigned height,
                                                int cache_target,
                                                unsigned surface_height) {
    unsigned frame_width = g1_mirror_frame_width(cache_target);
    return width <= frame_width && height <= surface_height &&
           origin_x >= 0 && origin_y >= 0 &&
           (unsigned long)origin_x <= frame_width - width &&
           (unsigned long)origin_y <= surface_height - height;
}

static inline int g1_mirror_scratch_bounds(int x, int y, unsigned width,
                                          unsigned height, int cache_target,
                                          unsigned surface_height,
                                          G1ScratchBounds *bounds) {
    return g1_scratch_intersection(x, y, width, height,
                                   g1_mirror_frame_width(cache_target),
                                   surface_height, bounds);
}

#endif
