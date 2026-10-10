#ifndef G1_BRIEFING_COMPOSE_H
#define G1_BRIEFING_COMPOSE_H

#include <stdint.h>

/* H-SC2: the scenario briefing (program state 20) composes its body layer, portraits and
 * buttons onto the flip-chain back buffer with colorkey BltFast/Blt inside 0x4D4620, which
 * the DirectDraw surface hooks never see.  The mirror diffs the back buffer around the
 * 0x4B23B5 call; this gate keeps it to that one case.  In the menu states the flip-chain
 * back buffer is a 1600x1200 surface (BACKBUFFER caps, the present gate's "menu shape") whose
 * top-left 800x600 holds the game's logical frame; an 800+ x 600 offscreen is also accepted.
 * Free of game types. */
#define G1_BRIEFING_PROGRAM_STATE 20u
#define G1_BRIEFING_MIN_WIDTH 800u
#define G1_BRIEFING_HEIGHT 600u
#define G1_BRIEFING_MAX_PITCH 2048u
#define G1_BRIEFING_HD_WIDTH 1600u
#define G1_BRIEFING_HD_HEIGHT 1200u

static inline int g1_briefing_compose_accepts(uint32_t program_state, uint32_t dest,
                                              uint32_t back_buffer, uint32_t width,
                                              uint32_t height, uint32_t pitch,
                                              uint32_t bits_per_pixel)
{
    return program_state == G1_BRIEFING_PROGRAM_STATE && dest != 0u && dest == back_buffer &&
           width >= G1_BRIEFING_MIN_WIDTH &&
           (height == G1_BRIEFING_HEIGHT ||
            (width == G1_BRIEFING_HD_WIDTH && height == G1_BRIEFING_HD_HEIGHT)) &&
           pitch >= G1_BRIEFING_MIN_WIDTH && pitch <= G1_BRIEFING_MAX_PITCH &&
           bits_per_pixel == 8u;
}

#endif
