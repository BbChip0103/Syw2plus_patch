#ifndef G1_SCRATCH_BLTFAST_H
#define G1_SCRATCH_BLTFAST_H

#include <stdint.h>

/* H-PS5W1: the menu list screens (program states 5 and 7) write their text with colorkey
 * BltFast calls from the glyph scratch surface onto the flip-chain back buffer through an
 * interface whose vtable the DirectDraw trace never cloned, so the mirror never sees the
 * text.  A wrapper on that vtable slot records each destination rectangle; the present then
 * diffs those rectangles against the mirror's expected frame.  Free of game types. */
#define G1_SCRATCH_BLTFAST_SCREEN_WIDTH 800u
#define G1_SCRATCH_BLTFAST_SCREEN_HEIGHT 600u
#define G1_SCRATCH_BLTFAST_MAX_RECTS 64u
#define G1_SCRATCH_BLTFAST_SITE_COUNT 7u

/* Return addresses of the seven BltFast calls that use the glyph scratch as source. */
static const uint32_t g1_scratch_bltfast_sites[G1_SCRATCH_BLTFAST_SITE_COUNT] = {
    0x004048D2u, 0x00405A06u, 0x004B6D66u, 0x004B7369u,
    0x004D1338u, 0x004D1E27u, 0x004D77EAu,
};

typedef struct {
    int32_t x, y, w, h;
} G1ScratchRect;

typedef struct {
    uint32_t count;
    uint32_t overflow;
    G1ScratchRect rects[G1_SCRATCH_BLTFAST_MAX_RECTS];
} G1ScratchQueue;

static inline int g1_scratch_bltfast_state_accepts(uint32_t program_state)
{
    return program_state == 5u || program_state == 7u;
}

/* 0..6 for a known call site, G1_SCRATCH_BLTFAST_SITE_COUNT for any other return address. */
static inline unsigned g1_scratch_bltfast_site_index(uint32_t return_address)
{
    unsigned index;
    for (index = 0u; index < G1_SCRATCH_BLTFAST_SITE_COUNT; ++index)
        if (g1_scratch_bltfast_sites[index] == return_address) return index;
    return G1_SCRATCH_BLTFAST_SITE_COUNT;
}

/* Destination rectangle of BltFast(x, y, source, src): the source size placed at (x, y),
 * clipped to the 800x600 logical frame.  A missing or empty source rectangle and an origin
 * outside the frame are refused. */
static inline int g1_scratch_bltfast_rect(uint32_t x, uint32_t y, int has_src, int32_t left,
                                          int32_t top, int32_t right, int32_t bottom,
                                          G1ScratchRect *out)
{
    int32_t width, height;
    if (!out || !has_src || left < 0 || top < 0 || right <= left || bottom <= top ||
        x >= G1_SCRATCH_BLTFAST_SCREEN_WIDTH || y >= G1_SCRATCH_BLTFAST_SCREEN_HEIGHT)
        return 0;
    width = right - left;
    height = bottom - top;
    if ((uint32_t)width > G1_SCRATCH_BLTFAST_SCREEN_WIDTH - x)
        width = (int32_t)(G1_SCRATCH_BLTFAST_SCREEN_WIDTH - x);
    if ((uint32_t)height > G1_SCRATCH_BLTFAST_SCREEN_HEIGHT - y)
        height = (int32_t)(G1_SCRATCH_BLTFAST_SCREEN_HEIGHT - y);
    out->x = (int32_t)x;
    out->y = (int32_t)y;
    out->w = width;
    out->h = height;
    return 1;
}

/* The overflow total survives a reset: it is a run-wide diagnostic. */
static inline void g1_scratch_queue_reset(G1ScratchQueue *queue)
{
    if (queue) queue->count = 0u;
}

static inline int g1_scratch_queue_push(G1ScratchQueue *queue, const G1ScratchRect *rect)
{
    if (!queue || !rect) return 0;
    if (queue->count >= G1_SCRATCH_BLTFAST_MAX_RECTS) {
        ++queue->overflow;
        return 0;
    }
    queue->rects[queue->count++] = *rect;
    return 1;
}

#endif
