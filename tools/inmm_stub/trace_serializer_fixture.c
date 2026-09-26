#include <windows.h>

#include "trace_record_serializer.h"

#define OUTPUT_PATH "C:\\trace_serializer_fixture.jsonl"

static const char MAX_RUN_ID[] =
    "20260911_172631_3142585_0-"
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_abcde";

static DWORD text_length(const char *text)
{
    int length = lstrlenA(text);
    return length < 0 ? 0u : (DWORD)length;
}

static BOOL build_record(char *line, DWORD capacity, DWORD *length_out)
{
    char prefix[1024];
    static const char details[] =
        ",\"event_count\":650,\"dropped_count\":0,\"source_call_count\":17837,\"aggregate_record_count\":35,\"method_counts\":{\"set_display_mode\":{\"detailed_count\":0,\"aggregated_count\":0,\"dropped_count\":0,\"total_count\":0},\"create_surface\":{\"detailed_count\":0,\"aggregated_count\":0,\"dropped_count\":0,\"total_count\":0},\"get_surface_desc\":{\"detailed_count\":0,\"aggregated_count\":0,\"dropped_count\":0,\"total_count\":0},\"blt\":{\"detailed_count\":0,\"aggregated_count\":0,\"dropped_count\":0,\"total_count\":0},\"blt_fast\":{\"detailed_count\":256,\"aggregated_count\":2542,\"dropped_count\":0,\"total_count\":2798},\"flip\":{\"detailed_count\":0,\"aggregated_count\":0,\"dropped_count\":0,\"total_count\":0},\"surface_release\":{\"detailed_count\":256,\"aggregated_count\":14645,\"dropped_count\":0,\"total_count\":14901}},\"p\":\"xx\",\"detach\":\"complete\",\"flush\":\"complete\"";
    int prefix_length;
    DWORD details_length = text_length(details);

    if (text_length(MAX_RUN_ID) != 95u || details_length != 803u) return FALSE;
    prefix_length = wsprintfA(prefix,
        "{\"schema\":\"g1-directdraw-trace-v1\",\"run_id\":\"%s\",\"seq\":651,"
        "\"call_seq\":17838,\"ts_ms\":489580973,\"pid\":276,\"thread_id\":280,"
        "\"program_state\":3,\"game_tick\":489578903,\"event\":\"summary\","
        "\"install_status\":\"detached\"",
        MAX_RUN_ID);
    if (prefix_length != 298 || (DWORD)prefix_length >= sizeof(prefix)) return FALSE;
    if (!trace_record_serialize(line, capacity, prefix, details, length_out)) return FALSE;
    if (*length_out != 1103u || line[*length_out - 2u] != '}' || line[*length_out - 1u] != '\n') return FALSE;
    if (line[1103u] != '\0') return FALSE;
    return TRUE;
}

static BOOL check_capacity_boundaries(void)
{
    char line[4096];
    char details[4094];
    DWORD i;
    DWORD length = 0u;

    for (i = 0u; i < 4092u; ++i) details[i] = 'x';
    details[4092] = '\0';
    if (!trace_record_serialize(line, sizeof(line), "X", details, &length) || length != 4095u || line[4095] != '\0') return FALSE;
    details[4092] = 'y';
    details[4093] = '\0';
    if (trace_record_serialize(line, sizeof(line), "X", details, &length)) return FALSE;
    return TRUE;
}

static BOOL write_one_record(const char *line, DWORD length)
{
    HANDLE file;
    DWORD written = 0u;
    BOOL ok;

    file = CreateFileA(OUTPUT_PATH, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                       CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return FALSE;
    ok = WriteFile(file, line, length, &written, NULL) && written == length;
    if (ok) ok = FlushFileBuffers(file);
    CloseHandle(file);
    return ok;
}

int WINAPI WinMain(HINSTANCE instance, HINSTANCE previous, LPSTR command_line, int show)
{
    char line[4096];
    DWORD length = 0u;
    (void)instance;
    (void)previous;
    (void)command_line;
    (void)show;
    if (!build_record(line, sizeof(line), &length)) return 10;
    if (!check_capacity_boundaries()) return 11;
    if (!write_one_record(line, length)) return 12;
    return 0;
}
