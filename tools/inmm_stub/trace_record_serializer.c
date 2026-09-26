#include "trace_record_serializer.h"

static BOOL append_fragment(char *line, DWORD capacity, DWORD *used,
                            const char *fragment)
{
    int fragment_length;
    DWORD available;
    DWORD i;

    if (!line || !used || !fragment || capacity == 0u || *used >= capacity) return FALSE;
    fragment_length = lstrlenA(fragment);
    if (fragment_length < 0) return FALSE;
    available = capacity - 1u - *used;
    if ((DWORD)fragment_length > available) return FALSE;
    for (i = 0; i < (DWORD)fragment_length; ++i) {
        line[*used + i] = fragment[i];
    }
    *used += (DWORD)fragment_length;
    return TRUE;
}

BOOL trace_record_serialize(char *line, DWORD capacity, const char *prefix,
                            const char *details, DWORD *length_out)
{
    DWORD used = 0u;

    if (!line || !length_out || capacity == 0u || !prefix) return FALSE;
    if (!append_fragment(line, capacity, &used, prefix)) return FALSE;
    if (details && !append_fragment(line, capacity, &used, details)) return FALSE;
    if (!append_fragment(line, capacity, &used, "}\n")) return FALSE;
    line[used] = '\0';
    *length_out = used;
    return TRUE;
}
