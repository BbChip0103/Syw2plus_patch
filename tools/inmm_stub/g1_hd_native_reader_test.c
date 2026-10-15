#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "g1_hd_asset.h"
#include "g1_perf_sections.h"

ULONGLONG g1_perf_sections_start(void) { return 0u; }
void g1_perf_sections_end(G1PerfSection section, ULONGLONG started, ULONGLONG bytes)
{ (void)section; (void)started; (void)bytes; }
void g1_perf_sections_reset(void) { }

#include "g1_hd_asset.c"

int main(int argc, char **argv)
{
    FILE *expected_file;
    unsigned long width, height, expected_success;
    DWORD bytes, read_bytes = 0u;
    BYTE *actual, *expected;
    BOOL loaded;
    if (argc != 6) return 2;
    width = strtoul(argv[2], NULL, 10);
    height = strtoul(argv[3], NULL, 10);
    expected_success = strtoul(argv[5], NULL, 10);
    if (!width || !height || width > 0xFFFFFFFFu / height || width * height > 0xFFFFFFFFu / 4u) return 3;
    bytes = (DWORD)(width * height * 4u);
    actual = (BYTE *)malloc(bytes);
    expected = (BYTE *)malloc(bytes);
    if (!actual || !expected) return 4;
    loaded = g1_hd_asset_load_named_frame(argv[1], 0u, actual, bytes);
    if ((loaded ? 1u : 0u) != expected_success) {
        DWORD index;
        DWORD found = native_find(argv[1]);
        fprintf(stderr, "load mismatch: enabled=%u duplicates=%lu expected=%lu\n",
                (unsigned)g1_hd_asset_pack_enabled(), (unsigned long)g1_hd_asset_sibling_duplicates(), expected_success);
        if (found) {
            G1HdSidecarEntry *entry = &g_sidecar_entries[found - 1u];
            fprintf(stderr, "found frame=%lu file=%lu decode=%u\n", (unsigned long)entry->frame,
                    (unsigned long)entry->directory,
                    (unsigned)native_decode_frame(g_hd_single_files[entry->directory], entry->frame,
                                                  entry->width, entry->height, actual, bytes));
        }
        for (index = 0u; index < g_sidecar_count; ++index)
            if (g_sidecar_entries[index].native)
                fprintf(stderr, "native[%lu]=%s frame=%lu %lux%lu\n", (unsigned long)index,
                        g_sidecar_entries[index].name, (unsigned long)g_sidecar_entries[index].frame,
                        (unsigned long)g_sidecar_entries[index].width, (unsigned long)g_sidecar_entries[index].height);
        return 5;
    }
    if (loaded) {
        expected_file = fopen(argv[4], "rb");
        if (!expected_file) return 6;
        read_bytes = (DWORD)fread(expected, 1u, bytes, expected_file);
        fclose(expected_file);
        if (read_bytes != bytes || memcmp(actual, expected, bytes) != 0) return 7;
    }
    free(expected);
    free(actual);
    return 0;
}
