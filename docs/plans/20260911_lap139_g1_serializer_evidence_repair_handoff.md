# 2026-09-11 lap139 — G1 serializer 검증 공백 수리 handoff

## 중간 판정

lap138의 source/test SHA 6개, bounded serializer 구현, 1046-byte native output, 4095/4096 경계,
old-1024 mutation 거부, exact `WriteFile`/flush 순서, `make check` 172개, fresh PE32 build,
doctor 원본 SHA, safety는 lap139에서 독립 재현했다. 구현 결함이 새로 입증된 것은
아니다.

다만 lap138 이력의 `max run_id ... PASS` 주장은 현재 native fixture로 재현되지 않는다.
fixture run_id는 38 bytes이고 production `g_run_id[96]`은 최대 95-byte payload를 받는다.
또한 production test는 `written != length`는 고정하지만 serializer/write/flush 실패 뒤
`g_event_count`를 증가시키지 않고 dropped/failed로 이어지는 control-flow를 회귀로 고정하지
않는다. source 독립 대조로 현재 순서는 맞지만, 전 lap이 주장한 필수 회귀 근거는
충족하지 않았다. 따라서 **MIDDLE CONFIRM BLOCKED / RUNTIME BLOCKED**다.

## 다음 Luna/high work 한 가지

제품/source 로직은 바꾸지 말고, 현재 native fixture/test를 최소 확장해 누락된 증거를
회귀로 고정한다.

1. production 허용 최대인 95-byte ASCII run_id를 사용한 prefix를 실제로 조합하고,
   prefix가 1024-byte formatter 경계 미만이며 serializer의 strict JSON/NUL 0/one-line/`}`+LF를
   통과함을 검사한다. 38-byte lap136 run_id만 다시 쓰면 안 된다.
2. production source 계약을 regression으로 고정한다: `trace_record_serialize` 또는
   `write_line` 실패 뒤 `g_event_count` 증가가 없고 caller가 dropped/`g_trace_failed` 상태로
   이어지며, 성공은 단 한 `WriteFile`, `written == requested`, flush 이후에만 계수한다.
   소스 문자열 확인을 유지한다면 순서를 깨는 mutation이 반드시 FAIL하게 한다.
3. lap136 보존 raw/SHA나 validator를 완화하지 않는다. 새 dependency, `TRACE_MAX_*`
   변경, summary 축소, 게임 runtime은 금지한다.
4. targeted, `make check`, fresh out-of-tree PE32 build/import, `make doctor`, safety를 실행하고
   새 source/test/DLL SHA를 남긴다. 그 다음 새 Sol/high가 독립 검수하기 전에는
   runtime을 승인하지 않는다.

