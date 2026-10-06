#include "g1_perf_sections.h"

static volatile LONG g_init = 0;
static BOOL g_enabled = FALSE;
static LARGE_INTEGER g_frequency;
static G1PerfSectionStat g_stats[G1_PERF_SECTION_COUNT];

static void initialize_environment(void)
{
    LONG state = InterlockedCompareExchange(&g_init, 1, 0);
    if (state == 0) {
        char value[8];
        DWORD size = GetEnvironmentVariableA("SYW2_G1_PERF_SECTIONS", value,
                                             sizeof(value));
        g_enabled = size == 1u && value[0] == '1';
        QueryPerformanceFrequency(&g_frequency);
        InterlockedExchange(&g_init, 2);
    } else {
        while (InterlockedCompareExchange(&g_init, 2, 2) != 2) Sleep(0);
    }
}

BOOL g1_perf_sections_enabled(void)
{
    initialize_environment();
    return g_enabled;
}

ULONGLONG g1_perf_sections_start(void)
{
    LARGE_INTEGER now;
    if (!g1_perf_sections_enabled() || !QueryPerformanceCounter(&now)) return 0u;
    return (ULONGLONG)now.QuadPart;
}

void g1_perf_sections_end(G1PerfSection section, ULONGLONG started,
                          ULONGLONG bytes)
{
    g1_perf_sections_accumulate(section, g1_perf_sections_elapsed(started), bytes);
}

ULONGLONG g1_perf_sections_elapsed(ULONGLONG started)
{
    LARGE_INTEGER now;
    if (started == 0u || !QueryPerformanceCounter(&now) ||
        g_frequency.QuadPart <= 0 || (ULONGLONG)now.QuadPart < started) return 0u;
    return (ULONGLONG)now.QuadPart - started;
}

void g1_perf_sections_accumulate(G1PerfSection section, ULONGLONG ticks,
                                 ULONGLONG bytes)
{
    G1PerfSectionStat *stat;
    if (ticks == 0u || section >= G1_PERF_SECTION_COUNT ||
        !g1_perf_sections_enabled()) return;
    stat = &g_stats[section];
    ++stat->count;
    stat->total_qpc_ticks += ticks;
    if (ticks > stat->max_qpc_ticks) stat->max_qpc_ticks = ticks;
    stat->bytes += bytes;
}

void g1_perf_sections_reset(void)
{
    DWORD i;
    for (i = 0u; i < G1_PERF_SECTION_COUNT; ++i) {
        g_stats[i].count = 0u;
        g_stats[i].total_qpc_ticks = 0u;
        g_stats[i].max_qpc_ticks = 0u;
        g_stats[i].bytes = 0u;
    }
}

ULONGLONG g1_perf_sections_frequency(void)
{
    (void)g1_perf_sections_enabled();
    return (ULONGLONG)g_frequency.QuadPart;
}

void g1_perf_sections_snapshot(G1PerfSectionStat stats[G1_PERF_SECTION_COUNT])
{
    DWORD i;
    if (!stats) return;
    for (i = 0u; i < G1_PERF_SECTION_COUNT; ++i) stats[i] = g_stats[i];
}
