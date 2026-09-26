/* control_protocol.h — control plane request/result 파일 프로토콜 (Win32 전용)
 *
 * R2 확장: request의 strategy/constraints/params, result의 path/bridge 메타데이터,
 *         rollback/fallback 필드 추가. reason은 env_blocked / logic_blocked 축으로 분류.
 */
#ifndef CONTROL_PROTOCOL_H
#define CONTROL_PROTOCOL_H

#include <windows.h>

#define CONTROL_REQUEST_JSON  "C:\\inmm_control_request.json"
#define CONTROL_RESULT_JSON   "C:\\inmm_control_result.json"
#define CONTROL_PROTOCOL_VER  "1"

#define CP_PARAM_UNSET  (-1)

/* reason 축 (문자열로 직렬화됨) */
#define CP_REASON_AXIS_ENV    "env_blocked"
#define CP_REASON_AXIS_LOGIC  "logic_blocked"

typedef struct {
    int  scenario_index;     /* CP_PARAM_UNSET(-1)이면 미지정 */
    int  custom_game_slot;
    int  load_slot;
    BOOL allow_input_bridge;
    BOOL allow_handler_bridge;
    BOOL preprocess_only;
} control_params_t;

typedef struct {
    char             version[16];
    char             request_id[64];
    char             goal[64];
    DWORD            timeout_ms;

    /* R2 확장 */
    char             strategy[32];     /* 선택 — 비어있으면 "" */
    char             constraints[64];  /* 선택 — 비어있으면 "" */
    control_params_t params;

    /* 파서 진단: 누락 필드 목록 (콤마 구분, 최대 5개) */
    char             missing_fields[128];

    /* 원본 JSON 버퍼 — goal별 추가 파라미터 파싱용 (raw_dump 등) */
    char             raw_json[2048];
} control_request_t;

typedef struct {
    /* 기존 필드 (레거시 호환) */
    char  request_id[64];
    BOOL  ok;
    char  reason[96];       /* 예: "ok" | "state_wait_timeout" */
    DWORD state_reached;
    DWORD event_count;

    /* R2 확장 */
    char  goal[64];
    char  reason_axis[16];  /* "env_blocked" | "logic_blocked" | "" */
    DWORD start_state;
    DWORD end_state;        /* state_reached alias (직렬화 중복) */
    char  bridge_used[16];  /* "state" | "input_A" | "input_B" | "handler" | "" */
    char  bridge_downgraded_from[8]; /* "A"/"B"/"" */
    char  fallback_chain[96];        /* "state,input_A" 등 콤마 나열 */
    DWORD fallback_count;
    DWORD elapsed_ms;
    BOOL  rollback_attempted;
    BOOL  rollback_ok;
} control_result_t;

BOOL control_protocol_poll(control_request_t *out, BOOL *parse_ok);
void control_protocol_write_result(const control_result_t *r);

#endif /* CONTROL_PROTOCOL_H */
