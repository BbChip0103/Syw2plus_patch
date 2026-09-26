# 2026-09-11 | lap 109 | G1 DirectDraw trace 독립 검수

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-sol`/high, 중간 tier 진단·계획·확인.
  게임 코드 hands-on 수정과 runtime 재실행은 수행하지 않았다.
- 가설 / 사용자 관찰: lap108의 `runtime_contract` 실패는 code thunk `0x004D7938`을 실제 IAT
  slot로 잘못 취급한 계약에서 발생하며, Sol은 원시 증거를 독립 확인해 수리 범위를 고정한다.
- 예상 PASS / FAIL 조건: 두 고정 원본 SHA/old bytes/import map과 raw artifact 해시가 재현되고
  충분 원인이 코드와 일치하면 확인 PASS. 주소가 다르거나 원인이 설명되지 않으면 UNKNOWN.
- 변경 파일 / source fingerprint / 커밋: `analysis/memory_maps/g1_directdraw_presentation.md`,
  `docs/plans/20260911_lap109_g1_presentation_trace_repair_card.md`, `docs/STATUS.md`,
  `loop/ESCALATE_SOL`, 본 기록. 모두 uncommitted. 코드/원본/후보/baseline/golden 변경 없음.
  검수 전 `direct_draw_trace.c` SHA `11128ccbae3c7d8bdaaf98232ea71404e000215bb0ea2a3565408c0d22d0f49c`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: source와 lap108 private EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp=0`, PE32.
  후보 없음. 과거 fixture는 diagnostic bridge=true/default two-player이고 새 game run은 SKIP.
- 실행 명령 / 로그 / 캡처: `objdump -p/-d/-s/-h`, `xxd`, `sha256sum`, `cmp`, raw validator,
  targeted pytest, `make check`, safety, 저장소 밖 `/tmp/syw2_g1_sol_review.WJRkS9` build.
  새 캡처 없음. lap108 manifest/trace/evidence/verdict SHA는 각각 `0ba4f51d...`, `5ad33358...`,
  `f3a64695...`, `8b8de37...`로 일치했다.
- 측정값 / 판정: import table은 DDRAW `FirstThunk RVA=0xE5018`; thunk `0x4D7938`은
  `[0x4E5018]`로 jump한다. 현재 상수는 `0x4D7938`이므로 충분한 deterministic failure를 확인했다.
  raw validator BLOCKED(2 events), targeted **67 passed**, `make check` **143 passed**,
  Ruff/compileall/mypy/context/safety PASS. private build PASS, DLL SHA
  `80a80627f4bf9977da57c7e9e7dde9000f8a902aa45e89cfdd559de41f29f582`(기존 경고 유지).
- 추가 REVISE 근거: `g_original_create_ex` 미대입, Surface7 index 6/8/12/23 사용(정답
  5/7/11/22), DD/Surface vtable 32/64 copy(헤더 30/49), `g_trace_guard`와 method 256 상한 미사용,
  event별 validator 계약·install-fail-before-input 미구현을 확인했다. IAT만 고친 live는 금지한다.
- 판정: **CONFIRM FAIL / REVISE / ESCALATE_SOL**. lap108 구현은 컴파일/Fast는 통과하지만 승인된
  runtime 관측 계약을 충족하지 않는다. G1/M1/제품/사용자 승인 없음.
- 다음 한 가지: Luna/high가 repair card의 instrumentation·runner·validator를 최소 수리하고 모든
  선행 gate PASS 뒤 새 private scene을 1회만 실행한다. 새 Sol/high가 그 결과를 독립 검수한다.
