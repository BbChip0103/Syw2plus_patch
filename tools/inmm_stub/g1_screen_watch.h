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

/* lap1119 H-PM1 PM1-0: SYW2_G1_SCREEN_WATCH_STATE=23 makes the watch follow the
 * Esc pause-menu state (PS23) instead of PS3 so the writer of the menu<->save
 * window transition can be named.  Only the exact value "23" selects it; absent
 * or any other value keeps PS3 (current behaviour). */
#define G1_SCREEN_WATCH_STATE_PS3 3ul
#define G1_SCREEN_WATCH_STATE_PS5 5ul
#define G1_SCREEN_WATCH_STATE_PS7 7ul
#define G1_SCREEN_WATCH_STATE_PS9 9ul
#define G1_SCREEN_WATCH_STATE_PS20 20ul
#define G1_SCREEN_WATCH_STATE_PS23 23ul
#define G1_SCREEN_WATCH_STATE_PS27 27ul
#define G1_SCREEN_WATCH_STATE_PS29 29ul

/* lap1127 H-RS1 RS1-0: "27" / "29" follow the defeat result screen's PS27 / PS29.
 * lap1141 H-TM1 TM1-0: "9" follows the title menu's PS9 (user-registration popup).
 * lap1147 H-SC1 SC1-0: "20" follows the scenario briefing's PS20.
 * lap1153 H-OS1 OS1-0: "5" / "7" follow the solo lobby's PS5 / the connection-method PS7. */
static inline unsigned long g1_screen_watch_state_parse(const char *value, unsigned long length)
{
    if (length == 1ul && value[0] == '9') return G1_SCREEN_WATCH_STATE_PS9;
    if (length == 1ul && value[0] == '5') return G1_SCREEN_WATCH_STATE_PS5;
    if (length == 1ul && value[0] == '7') return G1_SCREEN_WATCH_STATE_PS7;
    if (length == 2ul && value[0] == '2') {
        if (value[1] == '0') return G1_SCREEN_WATCH_STATE_PS20;
        if (value[1] == '3') return G1_SCREEN_WATCH_STATE_PS23;
        if (value[1] == '7') return G1_SCREEN_WATCH_STATE_PS27;
        if (value[1] == '9') return G1_SCREEN_WATCH_STATE_PS29;
    }
    return G1_SCREEN_WATCH_STATE_PS3;
}

/* lap1147 H-SC1 SC1-2: SYW2_G1_SCREEN_WATCH_CALL_FROM=<present> keeps the 48-row ddraw call table
 * from filling with early rows (PS20's typed text lines) by skipping calls made before that watch
 * present ordinal.  1..5 decimal digits; absent or anything else = 0 (record from the start). */
static inline unsigned long g1_screen_watch_call_from_parse(const char *value, unsigned long length)
{
    unsigned long i, result = 0ul;
    if (length == 0ul || length > 5ul) return 0ul;
    for (i = 0ul; i < length; ++i) {
        if (value[i] < '0' || value[i] > '9') return 0ul;
        result = result * 10ul + (unsigned long)(value[i] - '0');
    }
    return result;
}

/* Present ordinal logged in watch records: the drift counter only advances in
 * PS3, so other states use the watch's own present counter. */
static inline unsigned long g1_screen_watch_present_ordinal(unsigned long state,
                                                            unsigned long drift_present,
                                                            unsigned long watch_present)
{
    return state == G1_SCREEN_WATCH_STATE_PS3 ? drift_present : watch_present;
}

/* H-PM1 PM1-1b (H-RS1: any non-PS3 watched state): with SYW2_G1_SCREEN_WATCH_STATE=9|23|27|29
 * every ddraw Blt (kind 1) / BltFast (kind 2) call made in the watched state is folded into a small table keyed by
 * (kind, caller EIP, destination/source surface, rects, x/y, flags) with the
 * first/last watch present ordinal and a call count, published as {"t":"q"} rows
 * with the heartbeat.  rects are RECT-shaped {left,top,right,bottom} or NULL.
 * Read-only; returns at once unless the PS23 watch is armed. */
void g1_screen_watch_on_surface_call(unsigned long kind, unsigned long caller,
                                     unsigned long dest_this, unsigned long dest_primary,
                                     unsigned long source, const long *dst_rect,
                                     const long *src_rect, unsigned long x, unsigned long y,
                                     unsigned long flags);

/* Called at each present boundary of the watched state (PS3 by default) with the
 * locked source surface and the ordinal of the next present (the drift present counter).  No-op unless the
 * env gate is on. */
void g1_screen_watch_on_present(const unsigned char *surface, unsigned long pitch,
                                unsigned long next_present);

#endif
