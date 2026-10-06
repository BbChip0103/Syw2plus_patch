#ifndef G1_SCREEN_WATCH_H
#define G1_SCREEN_WATCH_H

#include "g1_layer_drift.h"

/* lap1022 H-B3: opt-in (SYW2_G1_SCREEN_WATCH=1, needs SYW2_G1_LAYER_DRIFT=1,
 * mirror candidate only) hardware write watch on the three screen sample
 * points A/B/C of g1_layer_drift.h.  It names the instruction/thread/module
 * that writes them.  Pure helpers so host tests can compile them; no CRT. */
#define G1_SCREEN_WATCH_SAMPLES G1_LAYER_DRIFT_RECTS
#define G1_SCREEN_WATCH_SELFTEST_SLOT 3u
/* Pinned original EXE .text: 0x401000 + 0xE3AE5 virtual bytes. */
#define G1_SCREEN_WATCH_TEXT_START 0x00401000ul
#define G1_SCREEN_WATCH_TEXT_END 0x004E4AE6ul

/* DR7: local enable bit 2*i, RW(i)=01 (break on write) at bit 16+4*i, LEN=00 (1 byte). */
static inline unsigned long g1_screen_watch_dr7(unsigned slots, int selftest)
{
    unsigned long dr7 = 0ul;
    unsigned i;
    for (i = 0u; i < slots && i < G1_SCREEN_WATCH_SELFTEST_SLOT; ++i)
        dr7 |= (1ul << (2u * i)) | (1ul << (16u + 4u * i));
    if (selftest)
        dr7 |= (1ul << (2u * G1_SCREEN_WATCH_SELFTEST_SLOT)) |
               (1ul << (16u + 4u * G1_SCREEN_WATCH_SELFTEST_SLOT));
    return dr7;
}

static inline unsigned long g1_screen_watch_address(unsigned long buffer,
                                                    unsigned long stride,
                                                    unsigned x, unsigned y)
{
    return buffer + (unsigned long)y * stride + (unsigned long)x;
}

/* lap1095 H-D2k-s0: SYW2_G1_SCREEN_WATCH_CACHE=1 watches the same sample
 * coordinates in the 1x terrain cache (0xBA3D30, pitch 832) instead of the
 * screen buffer, to name the writer that drifts the cache layer. */
#define G1_SCREEN_WATCH_CACHE_BASE 0x00BA3D30ul
#define G1_SCREEN_WATCH_CACHE_PITCH 832ul

/* Lowest triggered slot of Dr6 bits 0..3; 4 when none is set. */
static inline unsigned g1_screen_watch_slot(unsigned long dr6)
{
    unsigned i;
    for (i = 0u; i <= G1_SCREEN_WATCH_SELFTEST_SLOT; ++i)
        if (dr6 & (1ul << i)) return i;
    return G1_SCREEN_WATCH_SELFTEST_SLOT + 1u;
}

static inline int g1_screen_watch_in_exe_text(unsigned long value)
{
    return value >= G1_SCREEN_WATCH_TEXT_START && value < G1_SCREEN_WATCH_TEXT_END;
}

/* 0 = game EXE image, 1 = our _inmm.dll, 2 = any other module, 3 = unmapped. */
static inline unsigned g1_screen_watch_module_class(unsigned long base,
                                                    unsigned long exe_base,
                                                    unsigned long dll_base)
{
    if (base == 0ul) return 3u;
    if (base == exe_base) return 0u;
    if (base == dll_base) return 1u;
    return 2u;
}

/* Called at each PS3 present boundary with the locked source surface and the
 * ordinal of the next present (the drift present counter).  No-op unless the
 * env gate is on. */
void g1_screen_watch_on_present(const unsigned char *surface, unsigned long pitch,
                                unsigned long next_present);

#endif
