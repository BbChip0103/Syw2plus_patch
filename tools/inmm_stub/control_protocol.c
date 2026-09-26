/* control_protocol.c — control plane request/result 파일 프로토콜 (Win32 전용)
 *
 * R2 확장: params 파싱, result 확장 필드 직렬화, 누락 필드 진단.
 * Win32 API만 사용. CRT 함수(fopen/sscanf/atoi 등) 금지.
 */

#include "control_protocol.h"

/* ------------------------------------------------------------------ */
/* 내부 헬퍼: 최소 JSON 스캐너                                        */
/* ------------------------------------------------------------------ */

static int cp_find_str(const char *json, const char *key,
                       char *out, int maxout)
{
    char pat[80];
    int ki = 0;
    pat[ki++] = '"';
    {
        const char *k = key;
        while (*k && ki < 76) pat[ki++] = *k++;
    }
    pat[ki++] = '"';
    pat[ki++] = ':';
    pat[ki]   = '\0';

    int plen = ki;
    const char *p = json;
    while (*p) {
        int match = 1;
        for (int i = 0; i < plen; i++) {
            if (p[i] == '\0' || p[i] != pat[i]) { match = 0; break; }
        }
        if (match) {
            const char *v = p + plen;
            while (*v == ' ' || *v == '\t') v++;
            if (*v != '"') { p++; continue; }
            v++;
            int n = 0;
            while (*v && *v != '"' && n < maxout - 1)
                out[n++] = *v++;
            out[n] = '\0';
            return 1;
        }
        p++;
    }
    return 0;
}

static int cp_find_u32(const char *json, const char *key, DWORD *out)
{
    char pat[80];
    int ki = 0;
    pat[ki++] = '"';
    {
        const char *k = key;
        while (*k && ki < 76) pat[ki++] = *k++;
    }
    pat[ki++] = '"';
    pat[ki++] = ':';
    pat[ki]   = '\0';

    int plen = ki;
    const char *p = json;
    while (*p) {
        int match = 1;
        for (int i = 0; i < plen; i++) {
            if (p[i] == '\0' || p[i] != pat[i]) { match = 0; break; }
        }
        if (match) {
            const char *v = p + plen;
            while (*v == ' ' || *v == '\t') v++;
            if (*v >= '0' && *v <= '9') {
                DWORD val = 0;
                while (*v >= '0' && *v <= '9') {
                    val = val * 10 + (DWORD)(*v - '0');
                    v++;
                }
                *out = val;
                return 1;
            }
            return 0;
        }
        p++;
    }
    return 0;
}

/* cp_find_int — signed int 지원 (-1 unset 인식) */
static int cp_find_int(const char *json, const char *key, int *out)
{
    char pat[80];
    int ki = 0;
    pat[ki++] = '"';
    {
        const char *k = key;
        while (*k && ki < 76) pat[ki++] = *k++;
    }
    pat[ki++] = '"';
    pat[ki++] = ':';
    pat[ki]   = '\0';

    int plen = ki;
    const char *p = json;
    while (*p) {
        int match = 1;
        for (int i = 0; i < plen; i++) {
            if (p[i] == '\0' || p[i] != pat[i]) { match = 0; break; }
        }
        if (match) {
            const char *v = p + plen;
            while (*v == ' ' || *v == '\t') v++;
            int sign = 1;
            if (*v == '-') { sign = -1; v++; }
            if (*v >= '0' && *v <= '9') {
                int val = 0;
                while (*v >= '0' && *v <= '9') {
                    val = val * 10 + (*v - '0');
                    v++;
                }
                *out = sign * val;
                return 1;
            }
            return 0;
        }
        p++;
    }
    return 0;
}

/* cp_find_bool — "key":true|false 인식 */
static int cp_find_bool(const char *json, const char *key, BOOL *out)
{
    char pat[80];
    int ki = 0;
    pat[ki++] = '"';
    {
        const char *k = key;
        while (*k && ki < 76) pat[ki++] = *k++;
    }
    pat[ki++] = '"';
    pat[ki++] = ':';
    pat[ki]   = '\0';

    int plen = ki;
    const char *p = json;
    while (*p) {
        int match = 1;
        for (int i = 0; i < plen; i++) {
            if (p[i] == '\0' || p[i] != pat[i]) { match = 0; break; }
        }
        if (match) {
            const char *v = p + plen;
            while (*v == ' ' || *v == '\t') v++;
            if (v[0] == 't' && v[1] == 'r' && v[2] == 'u' && v[3] == 'e') {
                *out = TRUE; return 1;
            }
            if (v[0] == 'f' && v[1] == 'a' && v[2] == 'l' &&
                v[3] == 's' && v[4] == 'e') {
                *out = FALSE; return 1;
            }
            return 0;
        }
        p++;
    }
    return 0;
}

/* 누락 필드 누적기 */
static void append_missing(char *dst, int cap, const char *name)
{
    int len = lstrlenA(dst);
    int add = lstrlenA(name);
    if (len + add + 2 >= cap) return; /* 버퍼 한계 — 무시 */
    if (len > 0) {
        dst[len++] = ',';
        dst[len]   = '\0';
    }
    lstrcatA(dst, name);
}

/* ------------------------------------------------------------------ */
/* 공개 API                                                            */
/* ------------------------------------------------------------------ */

BOOL control_protocol_poll(control_request_t *out, BOOL *parse_ok)
{
    *parse_ok = FALSE;

    if (GetFileAttributesA(CONTROL_REQUEST_JSON) == INVALID_FILE_ATTRIBUTES)
        return FALSE;

    HANDLE h = CreateFileA(CONTROL_REQUEST_JSON,
                           GENERIC_READ, FILE_SHARE_READ,
                           NULL, OPEN_EXISTING,
                           FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) return FALSE;

    char buf[2048];
    DWORD nread = 0;
    BOOL rd_ok = ReadFile(h, buf, (DWORD)(sizeof(buf) - 1), &nread, NULL);
    CloseHandle(h);
    DeleteFileA(CONTROL_REQUEST_JSON);

    if (!rd_ok || nread == 0) return TRUE;
    buf[nread] = '\0';

    /* 원본 JSON 버퍼 보존 — goal별 추가 파라미터 파싱용 */
    lstrcpynA(out->raw_json, buf, sizeof(out->raw_json));

    /* 기본값으로 초기화 */
    out->version[0] = '\0';
    out->request_id[0] = '\0';
    out->goal[0] = '\0';
    out->timeout_ms = 0;
    out->strategy[0] = '\0';
    out->constraints[0] = '\0';
    out->missing_fields[0] = '\0';
    out->params.scenario_index        = CP_PARAM_UNSET;
    out->params.custom_game_slot      = CP_PARAM_UNSET;
    out->params.load_slot             = CP_PARAM_UNSET;
    out->params.allow_input_bridge    = TRUE;
    out->params.allow_handler_bridge  = TRUE;
    out->params.preprocess_only       = FALSE;

    /* 필수 필드 */
    BOOL has_ver  = (BOOL)cp_find_str(buf, "version",    out->version,    sizeof(out->version));
    BOOL has_rid  = (BOOL)cp_find_str(buf, "request_id", out->request_id, sizeof(out->request_id));
    BOOL has_goal = (BOOL)cp_find_str(buf, "goal",       out->goal,       sizeof(out->goal));
    BOOL has_tmo  = (BOOL)cp_find_u32(buf, "timeout_ms", &out->timeout_ms);

    if (!has_ver)  append_missing(out->missing_fields, sizeof(out->missing_fields), "version");
    if (!has_rid)  append_missing(out->missing_fields, sizeof(out->missing_fields), "request_id");
    if (!has_goal) append_missing(out->missing_fields, sizeof(out->missing_fields), "goal");
    if (!has_tmo)  append_missing(out->missing_fields, sizeof(out->missing_fields), "timeout_ms");

    /* 선택 필드 */
    cp_find_str(buf,  "strategy",    out->strategy,    sizeof(out->strategy));
    cp_find_str(buf,  "constraints", out->constraints, sizeof(out->constraints));
    cp_find_int(buf,  "scenario_index",       &out->params.scenario_index);
    cp_find_int(buf,  "custom_game_slot",     &out->params.custom_game_slot);
    cp_find_int(buf,  "load_slot",            &out->params.load_slot);
    cp_find_bool(buf, "allow_input_bridge",   &out->params.allow_input_bridge);
    cp_find_bool(buf, "allow_handler_bridge", &out->params.allow_handler_bridge);
    cp_find_bool(buf, "preprocess_only",      &out->params.preprocess_only);

    *parse_ok = (has_ver && has_rid && has_goal && has_tmo);
    return TRUE;
}

static void u32_to_signed(DWORD v, char *out)
{
    if (v == 0xFFFFFFFFu) {
        lstrcpyA(out, "-1");
    } else {
        wsprintfA(out, "%u", (unsigned)v);
    }
}

void control_protocol_write_result(const control_result_t *r)
{
    char sr[12], ss[12], es[12];
    u32_to_signed(r->state_reached, sr);
    u32_to_signed(r->start_state,  ss);
    u32_to_signed(r->end_state,    es);

    char buf[1024];
    wsprintfA(buf,
        "{\"request_id\":\"%s\","
        "\"ok\":%s,"
        "\"reason\":\"%s\","
        "\"reason_axis\":\"%s\","
        "\"state_reached\":%s,"
        "\"event_count\":%u,"
        "\"goal\":\"%s\","
        "\"start_state\":%s,"
        "\"end_state\":%s,"
        "\"bridge_used\":\"%s\","
        "\"bridge_downgraded_from\":\"%s\","
        "\"fallback_chain\":\"%s\","
        "\"fallback_count\":%u,"
        "\"elapsed_ms\":%u,"
        "\"rollback_attempted\":%s,"
        "\"rollback_ok\":%s}\n",
        r->request_id,
        r->ok ? "true" : "false",
        r->reason,
        r->reason_axis,
        sr,
        (unsigned)r->event_count,
        r->goal,
        ss, es,
        r->bridge_used,
        r->bridge_downgraded_from,
        r->fallback_chain,
        (unsigned)r->fallback_count,
        (unsigned)r->elapsed_ms,
        r->rollback_attempted ? "true" : "false",
        r->rollback_ok        ? "true" : "false");

    HANDLE h = CreateFileA(CONTROL_RESULT_JSON,
                           GENERIC_WRITE, 0,
                           NULL, CREATE_ALWAYS,
                           FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) return;
    DWORD written;
    WriteFile(h, buf, (DWORD)lstrlenA(buf), &written, NULL);
    CloseHandle(h);
}
