# STATUS pre-compaction snapshot — lap 129

다음 Sol/high 검수 전에 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `8928346e730c9d9783bbfaf21a1ad7ab96c67312b8a703408e402b72289224b6`
- line count: `169`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

2026-09-11 lap128 work는 lap127 handoff대로 fresh PE32 diagnostic bridge와 새 전체 게임
복사본/Win32 prefix/빈 Xvfb에서 presentation trace를 정확히 1회 실행했다. PS9→PS3, 실제
입력, 800×600 content와 PNG 5장, install trace gate는 PASS했지만 최종화가
`summary_count=0`, `event_count=617`, `process_exited=False`로 90초 timeout되어
**RUNTIME BLOCKED**다. owned process/Xvfb/prefix cleanup은 PASS이며 raw/evidence/verdict는
보존했다. 필수 런타임 검증 실패로 `loop/ESCALATE_SOL`을 만들고 재실행하지 않는다.

lap113~118의 ABI/trace/runtime 상세는 `docs/history/laps/20260911_status_lap122_compaction.md`와 각 lap 원문에 보존한다.

lap110~112의 ABI root-cause와 STATUS gate 복구 상세는 `docs/history/laps/20260911_status_lap115_compaction.md`와 각 lap 원문에 보존한다.

| 목표 | 판정 | 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | OS input origin static path는 lap102 확인; 실제 2배 출력/필수5입력·field/action 의미는 미검증 |
| G2 8인 전비5000 안정성 | 미완료 | 과거1명4990→5000/2진영뿐; 활성8인 스트레스 아님 |
| G3 최대16인 | 미완료 | 9~16인 실제 동작/통신 검증 없음 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 반복 측정·개선 구현 없음 |

## 다음 한 가지

**다음 한 가지는 새 work-tier 세션이 lap127 handoff대로 fresh out-of-tree bridge를 만들고 격리된
전체 게임 복사본/prefix/display에서 G1 presentation trace를 정확히 1회 실행하는 것이다.**
Release==0 retire 뒤 같은 주소 fresh install 또는 재발 실패의 raw/evidence/verdict를 보존한다.

## 지금 막힌 것 (Blockers)

- lap103의 `.venv/bin/pytest` exit127은 lap104에서 지원 경로와 Fast PASS로 해소됐다. 실패 명령과
  첫 수동 길이 정정은 lap103 원문에 보존한다. 정적 mouse-coordinate origin은 컨펌됐지만
  `0x00437E90` 이후 gameplay command/action 의미와 G1 2배 presentation boundary는 별개 blocker다.
- lap69~96의 해소·정정·static blocker 상세는 기존 compaction 파일, `docs/history/laps/20260911_status_lap100_compaction.md`, 각 lap 원문에 보존한다. primary worker/production direct edge 미증명과 구현 금지는 유지한다.
- group10 `0x498F65`, primary 12-slot table, `0x49B6D0` group2..5는 별개다. 화면 icon이나
  `(670,490)`만으로 동일시하지 않는다.
- lap60 live selection은 slot1199/type70, unit `0x00891CB8`, type flags `0x009C4CC4=0`이다.
  selected state `0x00891D4C=0`은 stable하지만 type predicate가 false라 group2..5 생성 경로는
  관측되지 않았다. alternate count `0`, 첫10 record/flags `0`, geometry `445,545,30,30`은
  before/after 동일하며 UI-list raw 관측일 뿐 production 의미가 아니다.
- G1 실제 2배 출력/입력, G2 8인5000, G3 9~16인, G4 비교 지표 및 사용자 승인은 모두 미검증이다.
- lap128 runtime은 실제 PS3까지 도달했지만 trace finalization이 summary 없이 timeout되어
  G1/M1을 통과시키지 못했다. 새 Sol/high 승격 작업자가 raw/provenance/evidence/verdict와
  `runtime_env.py` finalization 경로를 독립 진단하고 최소 수리·회귀 범위를 정해야 한다.
- lap113~118의 ABI·pointer·Surface7·finalization blocker 상세는 `docs/history/laps/20260911_status_lap122_compaction.md`와 각 lap 원문에 보존한다.
- lap120은 runner 결함은 해소됐음을 CONFIRMED했지만 surface 회귀가 token-only임을 의미 반전
  반례로 확인했다. lap122 work는 이를 shared C decision contract와 native branch harness로
  수리했고 lap123 middle 검수가 CONFIRMED해 fresh isolated runtime 정확히1회만 허용했다.
- lap121은 같은 의미 반전 반례를 독립 재현해 token contract=True/native syntax exit0을 확인했고
  lap120 handoff를 승인했다. diagnostic-only seam은 production과 동일 판정 함수/결정값을 공유해야 하며,
  성공·16개 단일 불일치·stale-uninstalled의 status/count/reason을 직접 검사해야 한다.
- lap125는 lap123의 coherent same-lifetime reuse 검사가 실제 주소 수명 재사용을 포괄하지 못했음을
  확인했다. `surface_record()`는 pointer만 key로 삼고 Release=0 폐기가 없어 stale lifetime을 같은
  object로 오인할 수 있다. raw는 current vtable 이탈 정황까지만 증명하므로 자동 rebind/49 추정은
  금지하고, Release 수명 추적과 exact reason/pointer 계측을 함께 수리해야 한다.
- lap126의 lifetime 수리는 lap127 middle이 source와 native evidence로 독립 컨펌했다. 다만 실제
  runtime에서 Release==0 retire 뒤 같은 주소의 fresh install은 아직 관측되지 않았다. 다음 work-tier
  1회 실행에서도 lap124 failure가 재발하면 raw를 보존하고 자동 rebind/49 추정 없이 승격한다.
- lap105~111의 DirectDraw 후보·trace 설치·ABI 결함 상세는 `docs/history/laps/20260911_status_lap115_compaction.md`와 각 lap 원문에 보존한다. unique present/2배 출력 미증명은 유지한다.
- lap97~102의 static input/dispatch provenance 상세는 `docs/history/laps/20260911_status_lap112_overflow_recovery.md`와 각 lap 원문에 보존한다. production 의미와 G1 구현 근거 미증명은 유지한다.


## 검증 상태

- lap109~112의 중간 검증·runtime block·gate 복구 수치는 `docs/history/laps/20260911_status_lap115_compaction.md`와 각 lap 원문에 보존한다.

- lap101~107의 정적 계약·계획·gate 검증 상세는 `docs/history/laps/20260911_status_lap112_overflow_recovery.md`와 각 lap 원문에 보존한다.

- lap92~97의 binary-contract 및 middle 검증 수치 상세는 `docs/history/laps/20260911_status_lap100_compaction.md`와 각 lap 원문에 보존한다.

- lap57~65의 원본 분기·alternate/primary table 진단, runtime SHA, 테스트 결과 상세는
  `docs/history/laps/20260911_status_lap71_overflow_recovery.md`와 각 lap 원문에 보존한다.

- lap66~72의 exact-single-selection, count evidence, production no-click 및 overflow 복구 상세는
  `docs/history/laps/20260911_status_lap77_compaction.md`와 각 lap 원문에 보존한다.

- lap73~80의 private evidence run, primary-panel/dataflow, render-helper 및 IAT 검수 상세는
  `docs/history/laps/20260911_status_lap82_compaction.md`와 각 lap 원문에 보존한다.

- lap81~85의 record xref, STATUS gate recovery, input chain과 semantic-label 검수 상세는
  `docs/history/laps/20260911_status_lap86_compaction.md`와 각 lap 원문에 보존한다.

- lap87~91의 xref 정정, dequeue probe 및 guard truth-table REVISE 상세는
  `docs/history/laps/20260911_status_lap92_compaction.md`와 각 lap 원문에 보존한다.

- lap92는 두 고정 원본 SHA/cmp/PE 매핑과 `0x004AC420` caller/callee를 재확인하고,
  `0x004AC47F..0x004AC4DF` guard bytes·5개 branch target·call/skip truth table 계약을 추가했다.
  `make check` **134 passed**, Ruff/compileall/mypy/context와 safety PASS, doctor top `ok=true`/original
  verified다. 후보·game·fixture는 SKIP이며 상세는 lap92 원문이다.

- lap56·58·60의 runtime manifest/verdict/source SHA 상세는 `docs/history/laps/20260911_status_lap94_prework_compaction.md`와 각 lap 원문에 보존한다.
- lap94는 generic ring producer/consumer chain conflict와 read-only contract 상세를
  `docs/history/laps/20260911_lap94_luna_g1a_generic_ring_boundary_probe.md`에 보존한다.

- lap113~118 검증 수치와 runtime artifact SHA는 `docs/history/laps/20260911_status_lap122_compaction.md`와 각 lap 원문에 보존한다.
- lap119는 lap118 handoff대로 `tools/runtime_env.py`와 두 테스트만 변경했다. finalization pipeline은
  owned close → process exit → final summary → trace copy → validator 순서를 `close, exit, summary,
  copy, validator`로 관측하며, summary 0/2·비최종·미종료 fixture는 validator 미호출/raw 보존으로
  BLOCKED다. surface reuse 16개 조건과 각 단일 mutation 검출도 PASS다. targeted **90 passed**,
  저장소 밖 fresh bridge `_inmm.dll` SHA `e4e10cba...`, `make doctor` top `ok=true`/original
  verified, `make check` **177 passed**, Ruff/compileall/mypy/context와 safety PASS다. 실제
  runtime/trace/G1/M1·사용자 승인은 SKIP/미승인이고 새 Sol/high 독립 검수 대기다.
- lap120은 runner pipeline은 CONFIRMED했지만 surface 테스트가 production 분기를 실행하지
  않고 의미 반전 `return FALSE→TRUE`를 놓침을 입증했다. SURFACE REGRESSION REVISE,
  fresh runtime/G1/M1 BLOCKED다.
- lap121은 source/test fingerprint 일치, 반례 token contract=True/native syntax exit0, targeted
  **90 passed**, fresh out-of-tree PE32 bridge build PASS, doctor top `ok=true`/original verified를
  확인했다. `make check` **177 passed**, Ruff/compileall/mypy/context와 safety PASS다. 처리한
  `loop/ESCALATE_SOL`은 lap121 이력에 원문 보존 후 소진했다.
- lap122는 `surface_reuse_contract.h`의 shared C decision을 production wrapper와 native harness에
  연결했다. success=49, 16개 단일 mismatch와 stale-uninstalled=failed·0·reason을 실행하고
  shared reusable mutation도 검출했다. targeted **75 passed**, fresh bridge SHA
  `0683156b...`, doctor top `ok=true`/original verified, `make check` **162 passed**,
  Ruff/compileall/mypy/context와 safety `SAFETY_PASS`다. 실제 게임/runtime/G1/M1·사용자 승인은
  SKIP/미승인이고 새 Sol/high 독립 검수 대기다.
- lap123은 lap122의 세 source SHA와 production input wiring, 성공49/stale 포함16개 실패 branch,
  기록 bridge `0683156b...`, 새 PE32 bridge `1b729514...`, 보호 원본 SHA를 독립 대조했다. targeted
  **75 passed**, doctor top `ok=true`/original verified, `make check` **162 passed**, safety
  `SAFETY_PASS`; **SURFACE BEHAVIOR MIDDLE CONFIRM PASS**다. actual runtime/G1/M1은 SKIP/미승인이다.
- lap124는 새 bridge build, prepare, manifest check, `make doctor-runtime`과 preflight를 PASS했다.
  정확히1회 fresh trace는 exit2 `presentation trace install failed before first input`이다. raw 79건에서
  seq2 install active/complete 뒤 seq54 첫 `surface_vtable/reused_surface_identity_or_clone_mismatch`,
  failed 18건, active `blt` 2건만 관측됐다. PS3/input/capture/final summary/validator PASS는 없고
  cleanup `ok=true`, prefix 잔류 0이다. raw/evidence/verdict와 SHA는
  lap124 이력에, 소진한 escalation marker 원문은 lap125 이력에 보존한다.
- lap125는 lap124 artifact 네 SHA와 raw 79 events를 독립 대조했다. seq50 active·49 → seq51/52
  wrapper active → seq54 첫 failure, 같은 pointer failed CreateSurface·0 9회를 확인했고 failed-status는
  install 9 + create 9 = 18이다. 기존 ABI targeted **5 passed**, `make check` **162 passed**,
  Ruff/compileall/mypy/context PASS, doctor top `ok=true`/original verified, safety `SAFETY_PASS`다.
  게임/runtime은 SKIP했다. 판정은
  **LAP124 FAILURE CONFIRMED / SURFACE LIFETIME CONTRACT REVISE / GAME RUN BLOCKED**다.
- lap126은 `surface_reuse_contract.h`에 Release wrapper/original coherence와 keep/retire shared
  decision을 추가하고, production `Release` wrapper가 0 refcount에서 record를 zero-retire 후 clone만
  해제하도록 수정했다. 실패 trace는 reason code/name과 actual·clone·original vtable을 기록하며
  `surface_release`는 256 method limit과 keep/retire 일관성을 validator가 검사한다. targeted **11
  passed**, `make check` **163 passed**, PE32 syntax/build PASS, `make doctor` top `ok=true`/original
  verified, `SAFETY_PASS`다. fresh runtime/G1/M1·사용자 승인은 SKIP/미승인이고 새 Sol/high 독립
  검수 대기다. 상세와 source/bridge SHA는 lap126 이력에 기록했다.
- lap127은 lap126의 5개 source/test SHA가 기록값과 일치함을 확인하고, production Release wrapper의
  original call→shared decision→zero-retire→clone free 순서와 failure reason/vtable 계측을 독립
  대조했다. targeted **11 passed**, fresh out-of-tree PE32 bridge `ff99944a...`, doctor top
  `ok=true`/original verified, safety `SAFETY_PASS`, `make check` **163 passed**와 Ruff/compileall/mypy/
  context PASS다. **SURFACE LIFETIME MIDDLE CONFIRM PASS**지만 실제 game/runtime/G1/M1·사용자 승인은
  SKIP/미승인이다.
- lap128은 source/원본 SHA와 targeted **11 passed**, `make check` **163 passed`, Ruff/compileall/
  mypy/context, doctor, safety, fresh bridge PE32 build, manifest check/doctor-runtime을 PASS했다.
  정확히1회 실제 trace는 PS9→PS3/input/capture까지 PASS했으나 final summary 0·event_count 617·
  process_exited false로 exit2/validator BLOCKED였다. raw 116 events SHA
  `adede3a0f007839cf92ebf32c9c382409b336a824806c9c31b13a596a9f3b323`, evidence/verdict/provenance와
  PNG 5장은 run output에 보존했고 cleanup은 `ok=true`, prefix 잔류 0이다. **G1/M1 BLOCKED**.

## 바퀴 기록

- lap2~51 상세는 `docs/history/laps/`에 보존한다.
- lap52~86 상세 목록은 `docs/history/laps/20260911_status_lap94_prework_compaction.md`와 각 lap 원문에 보존한다.
- lap87~95 상세 목록은 `docs/history/laps/20260911_status_lap100_compaction.md`와 각 lap 원문에 보존한다.
- lap96~107 상세 목록은 `docs/history/laps/20260911_status_lap112_overflow_recovery.md`와 각 lap 원문에 보존한다.
- lap108~112 상세 목록은 `docs/history/laps/20260911_status_lap115_compaction.md`와 각 lap 원문에 보존한다.
- lap113~118 상세 목록은 `docs/history/laps/20260911_status_lap122_compaction.md`와 각 lap 원문에 보존한다.
- lap119: `docs/history/laps/20260911_lap119_luna_g1_trace_regression_hardening.md`.
- lap120: `docs/history/laps/20260911_lap120_sol_g1_surface_regression_review.md`.
- lap121: `docs/history/laps/20260911_lap121_sol_g1_surface_regression_confirmation.md`.
- lap122: `docs/history/laps/20260911_lap122_luna_g1_surface_behavior_implementation.md`.
- lap123: `docs/history/laps/20260911_lap123_sol_g1_surface_behavior_confirmation.md`.
- lap124: `docs/history/laps/20260911_lap124_luna_g1_fresh_runtime_fail.md`.
- lap125: `docs/history/laps/20260911_lap125_sol_g1_surface_lifetime_review.md`.
- lap126: `docs/history/laps/20260911_lap126_luna_g1_surface_lifetime_repair.md`.
- lap127: `docs/history/laps/20260911_lap127_middle_g1_surface_lifetime_confirmation.md`.
- lap128: `docs/history/laps/20260911_lap128_luna_g1_presentation_trace_runtime_block.md`.
