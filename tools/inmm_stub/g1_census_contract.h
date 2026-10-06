#ifndef G1_CENSUS_CONTRACT_H
#define G1_CENSUS_CONTRACT_H

/* Platform independent rules shared by the diagnostic DLL and host tests. */
typedef struct {
    unsigned long buffer;
    unsigned long stride;
} G1CensusBufferKey;

static int g1_census_find_source_buffer(const G1CensusBufferKey *buffers,
                                        unsigned long count,
                                        unsigned long source_buffer,
                                        unsigned long source_pitch)
{
    unsigned long i;
    if (!buffers || source_buffer == 0u || source_pitch == 0u) return -1;
    for (i = 0; i < count; ++i)
        if (buffers[i].buffer == source_buffer && buffers[i].stride == source_pitch)
            return (int)i;
    return -1;
}

static int g1_census_buffer_key_matches(unsigned long buffer, unsigned long stride,
                                        unsigned long source_buffer,
                                        unsigned long source_pitch)
{
    return source_buffer != 0u && source_pitch != 0u &&
           buffer == source_buffer && stride == source_pitch;
}

/* Returns nonzero when the caller must clear the generation's attribution. */
static int g1_census_generation_changed(unsigned previous_state,
                                        unsigned next_state,
                                        unsigned long *generation)
{
    if (previous_state == next_state) return 0;
    if (generation) {
        ++*generation;
        if (*generation == 0u) ++*generation;
    }
    return 1;
}

/* Program state the census measures.  Unset/invalid keeps the original PS3
 * behaviour; a one- or two-digit decimal selects another state (e.g. 9). */
static inline unsigned g1_census_parse_target_state(const char *value, unsigned long size)
{
    unsigned parsed = 0u;
    unsigned long i;
    if (!value || size == 0u || size > 2u) return 3u;
    for (i = 0; i < size; ++i) {
        if (value[i] < '0' || value[i] > '9') return 3u;
        parsed = parsed * 10u + (unsigned)(value[i] - '0');
    }
    return parsed;
}

/* Opt-in count of target-state presents to pass over before the 64-present
 * census window starts.  Unset/invalid/zero keeps the original window. */
static inline unsigned g1_census_parse_skip_presents(const char *value, unsigned long size)
{
    unsigned parsed = 0u;
    unsigned long i;
    if (!value || size == 0u || size > 4u) return 0u;
    for (i = 0; i < size; ++i) {
        if (value[i] < '0' || value[i] > '9') return 0u;
        parsed = parsed * 10u + (unsigned)(value[i] - '0');
    }
    return parsed;
}

typedef struct {
    unsigned index;
    unsigned long count;
} G1CensusIndexCount;

/* Four most frequent 8bpp indices (ties -> lower index); unused slots are 0.
 * Selection passes instead of an insertion shift keep this free of memmove,
 * which the CRT-less diagnostic DLL cannot link. */
static inline void g1_census_index_top(const unsigned long histogram[256],
                                G1CensusIndexCount top[4])
{
    unsigned slot, index;
    unsigned char taken[256];
    for (index = 0; index < 256u; ++index) taken[index] = 0u;
    for (slot = 0; slot < 4u; ++slot) {
        unsigned best = 0u;
        unsigned long best_count = 0u;
        for (index = 0; index < 256u; ++index) {
            if (!taken[index] && histogram[index] > best_count) {
                best = index;
                best_count = histogram[index];
            }
        }
        top[slot].index = best_count ? best : 0u;
        top[slot].count = best_count;
        if (best_count) taken[best] = 1u;
    }
}

#endif
