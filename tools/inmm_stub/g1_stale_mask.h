#ifndef G1_STALE_MASK_H
#define G1_STALE_MASK_H

/* Opt-in PS3 stale-mask dump (SYW2_G1_STALE_MASK=6-12,300,579-630, mirror
 * candidate only).  Pure helpers so host tests can compile them; no CRT calls.
 * A spec is a comma list of PS3 present ordinals (0-based, counted over
 * program_state 3 presents only), inclusive a-b ranges, or a-b/step ranges
 * that keep every step-th ordinal starting at a. */
#define G1_STALE_MASK_PIXELS 480000u
#define G1_STALE_MASK_MAGIC 0x314B3153u /* "S1K1" */
#define G1_STALE_MASK_MAX_RANGES 8u
#define G1_STALE_MASK_DUMP_LIMIT 64u
#define G1_STALE_MASK_UNCOVERED 0u
#define G1_STALE_MASK_MATCH 1u
#define G1_STALE_MASK_STALE 2u

typedef struct {
    unsigned count;
    unsigned first[G1_STALE_MASK_MAX_RANGES];
    unsigned last[G1_STALE_MASK_MAX_RANGES];
    unsigned step[G1_STALE_MASK_MAX_RANGES];
} G1StaleMaskSpec;

/* Returns 0 for anything malformed (empty field, >4 digits, reversed range,
 * a step without a range or of 0, more than G1_STALE_MASK_MAX_RANGES
 * entries); *spec is then left empty. */
static inline int g1_stale_mask_parse(const char *text, unsigned long length,
                                      G1StaleMaskSpec *spec)
{
    unsigned long i = 0ul;
    unsigned digits, value, first, last, step;
    if (!spec) return 0;
    spec->count = 0u;
    if (!text || length == 0ul) return 0;
    for (;;) {
        digits = 0u;
        value = 0u;
        while (i < length && text[i] >= '0' && text[i] <= '9') {
            if (++digits > 4u) goto fail;
            value = value * 10u + (unsigned)(text[i] - '0');
            ++i;
        }
        if (digits == 0u) goto fail;
        first = last = value;
        step = 1u;
        if (i < length && text[i] == '-') {
            ++i;
            digits = 0u;
            value = 0u;
            while (i < length && text[i] >= '0' && text[i] <= '9') {
                if (++digits > 4u) goto fail;
                value = value * 10u + (unsigned)(text[i] - '0');
                ++i;
            }
            if (digits == 0u || value < first) goto fail;
            last = value;
            if (i < length && text[i] == '/') {
                ++i;
                digits = 0u;
                value = 0u;
                while (i < length && text[i] >= '0' && text[i] <= '9') {
                    if (++digits > 4u) goto fail;
                    value = value * 10u + (unsigned)(text[i] - '0');
                    ++i;
                }
                if (digits == 0u || value == 0u) goto fail;
                step = value;
            }
        }
        if (spec->count >= G1_STALE_MASK_MAX_RANGES) goto fail;
        spec->first[spec->count] = first;
        spec->last[spec->count] = last;
        spec->step[spec->count] = step;
        ++spec->count;
        if (i == length) return 1;
        if (text[i] != ',') goto fail;
        ++i;
    }
fail:
    spec->count = 0u;
    return 0;
}

static inline int g1_stale_mask_selected(const G1StaleMaskSpec *spec, unsigned ordinal)
{
    unsigned i;
    if (!spec) return 0;
    for (i = 0u; i < spec->count; ++i)
        if (ordinal >= spec->first[i] && ordinal <= spec->last[i] &&
            (ordinal - spec->first[i]) % spec->step[i] == 0u) return 1;
    return 0;
}

/* lap1127 H-RS1 RS1-0: SYW2_G1_STALE_MASK_STATE picks the program state whose presents the dump
 * counts and follows (ordinals then count that state only).  Only the exact values "23", "27" and
 * "29" select them (lap1147 H-SC1 SC1-0: and "20" = the scenario briefing; lap1212 H-PS5W0 W0-0:
 * and "5" = the solo lobby, "7" = the title protocol screen); absent or anything else
 * keeps PS3 (current behaviour). */
static inline unsigned long g1_stale_mask_state_parse(const char *value, unsigned long length)
{
    if (length == 1ul) {
        if (value[0] == '5') return 5ul;
        if (value[0] == '7') return 7ul;
    }
    if (length == 2ul && value[0] == '2') {
        if (value[1] == '0') return 20ul;
        if (value[1] == '3') return 23ul;
        if (value[1] == '7') return 27ul;
        if (value[1] == '9') return 29ul;
    }
    return 3ul;
}

/* Map value for one logical pixel: 0 uncovered, 1 covered and snapshot-equal
 * (HD), 2 covered but the screen no longer matches the snapshot (stale). */
static inline unsigned char g1_stale_mask_value(int covered, int snapshot_equal)
{
    if (!covered) return (unsigned char)G1_STALE_MASK_UNCOVERED;
    return (unsigned char)(snapshot_equal ? G1_STALE_MASK_MATCH : G1_STALE_MASK_STALE);
}

/* 8 DWORD little-endian header preceding each 800x600 byte map. */
static inline void g1_stale_mask_header(unsigned long header[8], unsigned ordinal,
                                        unsigned long program_state,
                                        unsigned long game_tick,
                                        unsigned long present_count,
                                        unsigned long covered, unsigned long stale)
{
    header[0] = G1_STALE_MASK_MAGIC;
    header[1] = ordinal;
    header[2] = program_state;
    header[3] = game_tick;
    header[4] = present_count;
    header[5] = covered;
    header[6] = stale;
    header[7] = G1_STALE_MASK_PIXELS;
}

#endif
