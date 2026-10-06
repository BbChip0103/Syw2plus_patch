#ifndef G1_CENSUS_WATCH_H
#define G1_CENSUS_WATCH_H

/* Opt-in hardware write watchpoint on one present-source pixel
 * (SYW2_G1_CENSUS_WATCH=x,y, needs SYW2_G1_CENSUS_RESIDUAL=1).  Pure helpers
 * so host tests can compile them; no CRT calls. */
#define G1_CENSUS_WATCH_WIDTH 800u
#define G1_CENSUS_WATCH_HEIGHT 600u
/* DR7: local enable slot 0 (bit 0), RW0 = 01 break on data write, LEN0 = 00 one byte. */
#define G1_CENSUS_WATCH_DR7 0x00010001ul
/* Pinned original EXE .text: 0x401000 + 0xE3AE5 virtual bytes. */
#define G1_CENSUS_WATCH_TEXT_START 0x00401000ul
#define G1_CENSUS_WATCH_TEXT_END 0x004E4AE6ul

/* Parse "x,y" (decimal digits only, at most 4 per field) into a screen pixel.
 * Returns 0 for anything malformed or outside the 800x600 screen. */
static inline int g1_census_watch_parse(const char *text, unsigned long length,
                                        unsigned *x, unsigned *y)
{
    unsigned long i = 0ul;
    unsigned value[2] = {0u, 0u};
    unsigned field, digits;
    if (!text || !x || !y || length == 0ul) return 0;
    for (field = 0u; field < 2u; ++field) {
        digits = 0u;
        while (i < length && text[i] >= '0' && text[i] <= '9') {
            if (++digits > 4u) return 0;
            value[field] = value[field] * 10u + (unsigned)(text[i] - '0');
            ++i;
        }
        if (digits == 0u) return 0;
        if (field == 0u) {
            if (i >= length || text[i] != ',') return 0;
            ++i;
        }
    }
    if (i != length || value[0] >= G1_CENSUS_WATCH_WIDTH ||
        value[1] >= G1_CENSUS_WATCH_HEIGHT) return 0;
    *x = value[0];
    *y = value[1];
    return 1;
}

static inline unsigned long g1_census_watch_pixel_address(unsigned long buffer,
                                                          unsigned long pitch,
                                                          unsigned x, unsigned y)
{
    return buffer + (unsigned long)y * pitch + (unsigned long)x;
}

/* lap1014 H-S2w: SYW2_G1_CENSUS_WATCH_CACHE=1 watches the same (x,y) in the 1x terrain
 * cache that 0x466280 copies to the screen (static buffer, pitch 832) instead. */
#define G1_CENSUS_WATCH_CACHE_BASE 0x00BA3D30ul
#define G1_CENSUS_WATCH_CACHE_PITCH 832ul

static inline unsigned long g1_census_watch_cache_address(unsigned x, unsigned y)
{
    return g1_census_watch_pixel_address(G1_CENSUS_WATCH_CACHE_BASE,
                                         G1_CENSUS_WATCH_CACHE_PITCH, x, y);
}

static inline int g1_census_watch_is_exe_text(unsigned long value)
{
    return value >= G1_CENSUS_WATCH_TEXT_START && value < G1_CENSUS_WATCH_TEXT_END;
}

#endif
