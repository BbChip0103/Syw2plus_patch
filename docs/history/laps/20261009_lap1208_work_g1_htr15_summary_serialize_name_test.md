# 2026-10-09 | lap 1208 | G1 work — H-TR15 (i15: summary 직렬화 실패 overflow 이름 고정 테스트)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 게임 run 0·C 제품 소스 변경 0·커밋 0.
- 가설: `g_event_count == TRACE_MAX_EVENTS − TRACE_RESERVED_EVENTS`(8190)에서 `summary` 이벤트의 `trace_event_raw`가 실패하면 overflow 마커 scope는 `serialize`다. 이 경계는 lap1201 변이 i15(`direct_draw_trace.c` 578줄 비교를 `< TRACE_MAX_EVENTS − TRACE_RESERVED_EVENTS`로)가 잡지 못한 테스트 공백이었다.
- 예상 PASS: T15-1 새 단언 GREEN, T15-2 변이 i15에서 RED·원복 뒤 GREEN, T15-3 C 소스 변경 0·`make check` PASS.
- 변경 파일: `tests/test_g1_presentation_trace.py`(`_OVERFLOW_FIXTURE` main에 summary 경우 4줄 추가, 기존 테스트 함수 재사용). C 소스 `tools/inmm_stub/direct_draw_trace.c` SHA256 `27c8ee2289a4b115e1bfe211708e73ef23d3dc72b0c99678b789787762d19edb`(전후 동일). 테스트 파일 SHA256 `d6370d709898fa7741a088ae6683f2fd0e8a55c349001d36c8b7f5181880ae4e`. uncommitted.
- 원본 SHA / fixture: 게임 run 0이라 원본 EXE 비접촉. 호스트 gcc 픽스처(실제 `trace_event`/`trace_overflow` 텍스트를 추출해 컴파일).
- 실행: `.venv/bin/python -m pytest tests/test_g1_presentation_trace.py -q -k overflow`.
- 측정값:
  - T15-1 PASS: 새 경우 = `g_event_count = MAX−RESERVED`, `raw_ok=0`, `trace_event("summary")` → `raw_calls == 2`(summary 시도 + overflow 마커)·scope `serialize`·`g_overflow_emitted == 1`. 현재 소스 GREEN(2 passed).
  - T15-2 PASS: 변이 i15(`sed`로 578줄을 `g_event_count < TRACE_MAX_EVENTS - TRACE_RESERVED_EVENTS`) → 새 테스트 FAIL(`test_g1_presentation_trace.py:596 AssertionError`, 1 failed·1 passed). 바이트 백업 복원 뒤 SHA 위 값과 동일, 파일 전체 19 passed.
- 판정: **H-TR15 `PASS(partial, 기술·호스트)`** 후보 — 제품 동작 변경이 없는 테스트 공백 해소다. 실게임 증거 아님.
- 회귀 / 남은 위험: 변이는 임시 in-place 수정 후 복원(`cp -p` 백업)이라 동시 다른 작성자가 없는 단일 writer 전제. `g_event_count == MAX−1`에서 summary 직렬화 실패는 `trace_overflow`가 마커를 내지 않고 반환(요약 슬롯 보호)하는 기존 설계라 별도 단언 안 함.
- 독립 검수: 미수행(역할 경계, `loop/ESCALATE_SOL`로 middle 요청). 사용자 업스케일 결과가 오면 그것이 최우선(H-HDU3 사전등록 middle).
- 다음 한 가지: middle이 변이 i15 RED/GREEN을 독립 재현하고 H-TR15를 수용한 뒤, 사용자 업스케일 결과 대기 동안 다음 backlog(예: `key_wrap_mismatches`·`mirror_blend_clip` 검사 순서)를 사전등록하거나 STOP 판단.
