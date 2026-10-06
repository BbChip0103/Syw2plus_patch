#ifndef G1_PERF_SECTIONS_H
#define G1_PERF_SECTIONS_H

#include <windows.h>

typedef enum {
    G1_PERF_SCRATCH_CLEAR = 0,
    G1_PERF_ORIGINAL_A,
    G1_PERF_ORIGINAL_B,
    G1_PERF_HASH_LOOKUP,
    G1_PERF_BIND_COMPARE,
    G1_PERF_BIND_COPY_ALLOC,
    G1_PERF_SCALE2X_BUILD,
    G1_PERF_COMPOSE,
    G1_PERF_NEGATIVE_PROBE,
    G1_PERF_WHOLE_TINTED,
    G1_PERF_WHOLE_TINTED_CLIP,
    G1_PERF_WHOLE_OTHER,
    G1_PERF_CLIP_PREPARE,
    G1_PERF_CLIP_TEMP_ALLOC_FREE,
    G1_PERF_CLIP_BUFFER_FILL,
    G1_PERF_CLIP_MASK_PREPARE,
    G1_PERF_SECTION_COUNT
} G1PerfSection;

typedef struct {
    ULONGLONG count;
    ULONGLONG total_qpc_ticks;
    ULONGLONG max_qpc_ticks;
    ULONGLONG bytes;
} G1PerfSectionStat;
ULONGLONG g1_perf_sections_frequency(void);

BOOL g1_perf_sections_enabled(void);
ULONGLONG g1_perf_sections_start(void);
void g1_perf_sections_end(G1PerfSection section, ULONGLONG started,
                          ULONGLONG bytes);
ULONGLONG g1_perf_sections_elapsed(ULONGLONG started);
void g1_perf_sections_accumulate(G1PerfSection section, ULONGLONG ticks,
                                 ULONGLONG bytes);
void g1_perf_sections_reset(void);
void g1_perf_sections_snapshot(G1PerfSectionStat stats[G1_PERF_SECTION_COUNT]);

#endif
