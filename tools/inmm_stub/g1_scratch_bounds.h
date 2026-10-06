#ifndef G1_SCRATCH_BOUNDS_H
#define G1_SCRATCH_BOUNDS_H

typedef struct {
    unsigned int x;
    unsigned int y;
    unsigned int width;
    unsigned int height;
} G1ScratchBounds;

/* Compute the part of a signed-position primitive that overlaps the logical
 * frame.  A valid off-screen primitive returns TRUE with an empty rectangle;
 * malformed dimensions or signed addition overflow return FALSE. */
static int g1_scratch_intersection(long x, long y,
                                   unsigned int width, unsigned int height,
                                   unsigned int frame_width,
                                   unsigned int frame_height,
                                   G1ScratchBounds *bounds)
{
    long right, bottom, left_clip, top_clip, right_clip, bottom_clip;
    if (!bounds || width == 0u || height == 0u ||
        width > 0x7fffffffu || height > 0x7fffffffu) return 0;
    if (x > 0x7fffffffL - (long)width ||
        y > 0x7fffffffL - (long)height) return 0;
    right = x + (long)width;
    bottom = y + (long)height;
    left_clip = x > 0 ? x : 0;
    top_clip = y > 0 ? y : 0;
    right_clip = right < (long)frame_width ? right : (long)frame_width;
    bottom_clip = bottom < (long)frame_height ? bottom : (long)frame_height;
    if (left_clip > (long)frame_width) left_clip = (long)frame_width;
    if (top_clip > (long)frame_height) top_clip = (long)frame_height;
    bounds->x = (unsigned int)left_clip;
    bounds->y = (unsigned int)top_clip;
    bounds->width = right_clip > left_clip
        ? (unsigned int)(right_clip - left_clip) : 0u;
    bounds->height = bottom_clip > top_clip
        ? (unsigned int)(bottom_clip - top_clip) : 0u;
    return 1;
}

#endif
