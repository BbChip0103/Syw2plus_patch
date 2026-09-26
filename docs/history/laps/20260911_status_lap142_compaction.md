# STATUS pre-compaction snapshot — lap 142

fresh runtime 재실행 전 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `c51c4687fbb5297fd86a30df4fadde8028a7a3a3e6c0d424e5b5684252a92b44`
- line count: `169`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

2026-09-11 lap141 중간 tier 독립 검수는 lap140의 변경 SHA 두 개와 production source SHA를
재확인하고, 95-byte run_id가 실제 wsprintfA prefix 298 bytes에 조합되어 serializer JSONL
1103 bytes/NUL0/one-line/`}\n`을 만드는 native fixture를 재현했다. write/flush 전 event count
증가와 dropped/failed 역전 mutation도 각각 거부했다. targeted 12개, Fast 173개, fresh PE32/import,
doctor/safety가 PASS해 **MIDDLE CONFIRM PASS / FRESH RUNTIME READY**로 판정한다. 이는 runtime이나
G1/M1 PASS가 아니며, 게임 코드·제품·baseline/golden은 변경하지 않았다.

2026-09-11 lap140 Luna hands-on work는 제품/source 로직을 바꾸지 않고 native serializer fixture를
production과 같은 wsprintfA prefix 조합으로 확장했다. 95-byte ASCII run_id가 실제 prefix에
조합되고 prefix 298 bytes < 1024, serialized JSONL 1103 bytes/NUL0/one-line/}\n을 확인한다.
production trace writer의 성공 후 event count, 실패 후 dropped/failed/overflow 순서를 source
mutation 회귀로 고정했다. targeted 12개와 make check 173개, fresh PE32/import,
doctor/safety가 PASS했다. **LUNA IMPLEMENTATION PASS / MIDDLE CONFIRM PENDING / RUNTIME BLOCKED**다.

2026-09-11 lap139 Sol 독립 검수는 lap138의 source/test SHA 6개, 1046-byte native
serializer, 4095/4096 경계, old-1024 mutation 거부, exact write/flush source 순서, targeted 17개,
`make check` 172개, fresh PE32 build, doctor/safety를 재현했다. 그러나 lap138이 PASS로 기록한
max run_id는 fixture의 38 bytes로만 실행됐고 production 95-byte 경계가 아니며, writer 실패 후
event count 불변·dropped/failed 순서도 mutation 회귀로 고정되지 않았다. 새 구현 결함을 입증한
것은 아니지만 기록-테스트 근거가 충돌하므로 **MIDDLE CONFIRM BLOCKED / RUNTIME BLOCKED**다.

2026-09-11 lap138 실무 수리는 lap137의 writer 원인 진단을 bounded no-CRT serializer로 구현했다.
`trace_record_serialize()`가 prefix/details/`}\n`을 `line[4096]`에 terminator 포함 용량 검사로 결합하고,
production은 성공한 한 번의 `WriteFile`과 `written == requested` 및 flush만 event로 계수한다. summary
details는 serializer가 outer `}`를 붙이도록 정리했다. fresh native fixture는 prefix241 + detail fragment803
suffix2 = payload1046을 strict JSON/NUL0/one-line/method-count/detach/flush 보존으로 통과했고,
4095 boundary success·4096 overflow fail-closed 및 1024-byte mutation 거부도 통과했다. **RUNTIME BLOCKED**는
유지하며 새 Sol 독립 검수 전 게임 runtime은 금지한다.
lap135 Sol 중간 검수는 lap134의 세 source/test SHA, fixed-array aggregate key,
summary 산술, validator fail-closed와 fresh PE32 build를 독립 확인해 **MIDDLE CONFIRM PASS**했다.
정확히 256개 상세 경계 뒤 aggregate가 state/object/original/present identity와 first/last
call-sequence·tick을 보존하며, malformed duplicate key와 65-record capacity는 BLOCKED다.
**RUNTIME BLOCKED**는 유지한다: 실제 게임에서 overflow 없는 final summary와 process exit/DLL
detach는 아직 새 Luna runtime으로 확인하지 않았다.

현재 1600×1200 제품 패치는 없다. 실게임 캡처가 확인한 원본 content surface는 800×600이다.
G2~G4도 구현/승인되지 않았다.

| 목표 | 판정 | 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | trace 경계 접근은 성공, content는 800×600; 2배 출력·final summary 미검증 |
| G2 8인 전비5000 안정성 | 미완료 | 8인 실제 부하·유닛 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 상태/로비/통신/시뮬레이션 검증 없음 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

새 Luna/high work tier가 `docs/plans/20260911_lap141_g1_fresh_runtime_handoff.md`대로 새 bridge,
전체 game copy, Win32 prefix, 빈 Xvfb display를 준비하고 G1 presentation trace를 정확히 1회 실행한다.
실패 뒤 재시도하지 않으며 raw/final summary/process exit/DLL detach/validator/cleanup을 보존한다.

## 지금 막힌 것 (Blockers)

- 같은 run 재실행, 임의 prefix/display 반복, 116행 raw 성공/최종 trace 승격, 자동 vtable rebind/49 추정 금지.
- raw 보존 수리는 targeted/Fast에서 PASS했지만 실제 close transport나 overflow 없는 runtime 증거로 승격하지 않는다.
- 종료 transport fixture는 lap133 middle confirmation PASS지만, 실제 게임의 owned Win32 HWND/PID와
  WM_CLOSE→process exit→DLL detach는 새 runtime에서 아직 미검증이다. X11 window destroy 성공을
  process 정상 종료로 쓰지 않는다.
- trace capacity는 PS3 전 overflow를 숨기거나 근거 없이 limit만 키우지 않고 별도 계약으로 수리했다.
  실제 게임에서 aggregate dropped=0과 overflow 없는 final summary는 아직 미검증이다.
- lap136 failure 원인은 완성 record 1046 bytes를 최대1024-byte `wsprintfA`로 조합한 writer 결함이며,
  lap138 source repair/native fixture로 수리 범위를 검증했다. 실제 게임의 overflow 없는 final summary와
  process exit/DLL detach는 여전히 미검증이다.
- 제품 EXE/DLL/assets/baseline/golden은 변경하지 않았다. out-of-tree 후보 DLL만 만들었고 원본 SHA256은
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다.
- Surface7 typed vtable은 49 entries, Blt/BltFast/Flip/GetSurfaceDesc indices는 5/7/11/22다.
- DirectDrawCreateEx ABI는 `(GUID*, LPVOID*, REFIID, IUnknown*)`, IAT slot은 `0x004E5018`이다.
- Release wrapper는 original call 후 refcount 0에서 record를 retire하고 private clone만 해제한다.
- finalization 계약은 owned close → process exit → exactly one final summary → raw copy → validator다.
- G1의 실제 2배 출력/입력, G2 8인5000, G3 16인, G4 AI/pathfinding 및 사용자 승인은 모두 미검증이다.

## 검증 상태

- lap141은 lap140 fixture/test SHA `0bda53ee...`/`d87617e1...`와 production trace source
  `533478e0...`를 확인했다. source 순서 및 mutation 두 건, 95-byte run_id/prefix 298/JSONL 1103,
  targeted **12 passed**, 전체 pytest **173 passed**, Ruff/compileall/mypy/context/shell syntax PASS다.
  fresh out-of-tree PE32 DLL SHA는 `e39f336f8683b259c0f49f581c66a11d5d55f489a422f171143b1f76493e7616`,
  CRT import 없음, doctor original verified/no-side-effect, safety PASS다. 게임 runtime/PNG/final summary/
  process exit/DLL detach는 SKIP이며 사용자 승인은 없다. 판정은 **MIDDLE CONFIRM PASS**다.
- lap140 changed tools/inmm_stub/trace_serializer_fixture.c와
  tests/test_g1_presentation_trace.py는 history에 SHA를 기록했다. native fixture는 95-byte
  ASCII run_id를 production-format prefix로 조합해 prefix 298 bytes, JSONL 1103 bytes,
  strict JSON/NUL 0/one-line/closure를 PASS했고, production writer의 write/count 및
  dropped/failed/overflow 순서 두 mutation을 거부했다. targeted **12 passed**, make check
  **173 passed**, Ruff/compileall/mypy/context PASS, fresh out-of-tree PE32 DLL
  8ec1cfd6c744b434ca63e2ae72bfcfa48f821ae061fbfcb09fbe9489b9632e44, CRT import 없음,
  make doctor original SHA/no-side-effect PASS, safety PASS다. source/product/EXE/assets/
  baseline/golden은 변경하지 않았다. 게임 runtime/PNG/final summary/process exit/DLL detach는
  SKIP이며 새 Sol 독립 검수와 runtime이 남았다.
- lap139 source/test SHA 6개는 lap138과 일치했고 targeted **17 passed**, `make check`
  **172 passed**, Ruff/compileall/mypy/context PASS다. fresh out-of-tree PE32 DLL SHA는
  `ab55d3ab7578bef800928aaff63ebe0e279103d879294e4fd3b5fb4cfdfdd7f2`, CRT import 없음,
  doctor original SHA/no-side-effect 및 safety PASS다. 38-byte fixture run_id만 실행되어
  max-95 주장은 미입증, failure-order mutation 회귀도 미구현이므로 판정은 BLOCKED다.
- lap126 Luna repair: targeted 11 passed, full 163 passed, PE32 build/doctor/safety PASS.
- lap127 Sol confirmation: source SHA 일치, targeted 11 passed, full 163 passed, fresh PE32
  build/doctor/safety PASS; Surface7 lifetime contract CONFIRMED, runtime은 SKIP.
- lap128 fresh runtime: bridge SHA
  `16df8ffd2e4ca455f86e9e7c589a3f49f7896249041cd7be091eaec1361bb4fe`; preflight PASS;
  PS9→PS3/input/capture PASS; final summary 0/process 미종료로 exit2 BLOCKED; cleanup PASS.
- lap128 artifacts: `local/runtime/20260911_160804_2519243_0/output/g1_presentation_trace/`.
- lap129 independent diagnosis: artifact SHA 전부 일치; live trace 617행 SHA
  `b105fc3452dc1650aab58cd7c66aa79e97656964a121ab18d80713f6469d8539`, output raw는 live의
  첫 116행과 byte-identical; live validator는 schema errors 0/capture true지만 overflow+summary로 BLOCKED.
- lap129 targeted finalization **7 passed**, DirectDraw/validator **11 passed**, `make check` **163 passed**;
  Ruff/compileall/mypy/context, doctor original verified, safety PASS. runtime은 재실행하지 않았다.
- lap130 targeted runtime **71 passed**, `make check` **164 passed**, Ruff/compileall/mypy/context PASS;
  `make doctor` original verified, `bash checks/safety.sh check` SAFETY_PASS. 새 runtime/PNG는 실행하지 않았다.
- lap131 source/test SHA 3개 일치; targeted **71 passed**, 핵심 116→617 회귀 별도 **1 passed**,
  `make check` **164 passed**, Ruff/compileall/mypy/context PASS; doctor original verified, safety PASS.
  판정은 RAW SEPARATION MIDDLE CONFIRM PASS이며 새 runtime/PNG는 실행하지 않았다.
- lap132 source/test SHA는 `docs/history/laps/20260911_lap132_luna_g1_owned_win32_close_transport.md`에
  기록했다. targeted **68 passed**, fresh PE32 helper/target build는 `file` PE32 PASS, fixture는
  positive `requested_pid=32/match_count=1/post_result=true/wm_close=1/final_marker=true`, negative
  wrong PID·0개·복수는 모두 `returncode=2/post_result=false/wm_close=0/final_marker=true` PASS.
  `make check` **166 passed**, Ruff/compileall/mypy/context PASS, `make doctor` original SHA PASS
  (runtime manifest 없음/side-effect 없음), `bash checks/safety.sh check` SAFETY_PASS; 게임 runtime/PNG는
  실행하지 않았다.
- lap133 source/test SHA 7개가 lap132와 일치했다. targeted **68 passed**, `make check` **166 passed**,
  Ruff/compileall/mypy/context, doctor original SHA/no-side-effect, safety PASS. fresh PE32 fixture report SHA는
  `715677421e2e5748f9f21db38769c39c75a1c4566ed61addb9c52af455836c89`; positive exact single
  PID/HWND/WM_CLOSE/exit와 negative wrong PID·0창·복수창 fail-closed를 재현했다. helper-failure 직접
  probe는 raw exact 보존/validator 0회 PASS. 판정은 MIDDLE CONFIRM PASS, 게임 runtime/PNG는 SKIP.
- lap134 source SHA는 `tools/inmm_stub/direct_draw_trace.c=412315b1f5c1199d97a63d9bdee3a580fb12bed95cc6bcccb336c67466c4a121`,
  `tools/check_g1_presentation_trace.py=a58a8aa13bd3affb25aaf7355ef5bf803c6fea0efb1320a6c27557f308ef4c1a`,
  `tests/test_g1_presentation_trace.py=5d68f12e4d1ed071d27c5418d18519419f6e43af1ca1732bc5791537a36ec13d`다.
  targeted **14 passed**, `make check` **169 passed**, Ruff/compileall/mypy/context PASS, out-of-tree
  PE32 DLL `f70289e5617faecfa23e3bff340e3813657da60760c2f3e72cf56682a461639b` PASS, `make doctor`
  original SHA/side-effect PASS, safety PASS. synthetic 256+aggregate/state-transition/malformed/65-record
  capacity fixtures만 사용했으며 게임 runtime/PNG는 handoff대로 SKIP했다.
- lap135 source/test SHA 3개는 lap134와 일치했다. aggregate key·method total 산술을 source와
  validator에서 독립 대조했고 targeted **14 passed**, `make check` **169 passed**,
  Ruff/compileall/mypy/context PASS, fresh out-of-tree PE32 DLL SHA
  `2688994d771bd392041802cd8fc3c2927ce77a51ef4f6ec35dae5922964d114b`, `make doctor`
  original SHA/no-side-effect 및 safety PASS다. synthetic fixture만 재검수했고 게임 runtime/PNG는 SKIP했다.
- lap136 fresh runtime: new private run `local/runtime/20260911_172631_3142585_0`, manifest/check PASS,
  fresh bridge/close helper PE32 PASS. Runtime command was run exactly once and returned RC2 with
  `trace malformed: Invalid control character at line 1 column 1024`; install gate 205 events,
  raw 651 lines/372031 bytes, PS3 PNG and WM_CLOSE evidence preserved, cleanup PASS, final summary/
  validator PASS unavailable. No Fast rerun after the required runtime failure.
- lap137 middle diagnosis: preserved artifact SHA exact; raw last line 1024 bytes/NUL@1023/no newline,
  prior max628/NUL0; prefix241 + details805 = expected1046. Source outer `wsprintfA` and official 1024-byte
  limit explain the bytes exactly. targeted **14 passed**, `make check` **169 passed**,
  Ruff/compileall/mypy/context, fresh out-of-tree PE32 DLL
  `ec318c8d00edfff736444b8e765c830a2f2a165572d13d756f017804fc04a272`, doctor original verified/no-side-effect,
  safety PASS. 판정은 MIDDLE DIAGNOSIS CONFIRMED; source repair/game runtime/G1은 SKIP.
- lap138 source repair: changed source/test SHA and out-of-tree PE32 DLL SHA are recorded in
  `docs/history/laps/20260911_lap138_luna_g1_trace_record_serialization_repair.md`. Native serializer fixture
  passed 1046-byte strict JSON/NUL0/final `}\n`, max run_id, 4095 success/4096 fail-closed, and old-1024
  mutation rejection. `make check` **172 passed**, Ruff/compileall/mypy/context PASS, `make doctor` original
  SHA/no-side-effect PASS, safety PASS. Game runtime/PNG/final summary/process exit/DLL detach are SKIP;
  판정은 **LUNA IMPLEMENTATION PASS / RUNTIME BLOCKED**, next Sol independent review.
- 상세 수치와 이전 blocker는 각 lap 원문 및 아래 compaction 파일에 보존한다.

## 바퀴 기록

- lap2~51: `docs/history/laps/` 각 원문.
- lap52~86: `docs/history/laps/20260911_status_lap94_prework_compaction.md` 및 각 원문.
- lap87~95: `docs/history/laps/20260911_status_lap100_compaction.md` 및 각 원문.
- lap96~107: `docs/history/laps/20260911_status_lap112_overflow_recovery.md` 및 각 원문.
- lap108~112: `docs/history/laps/20260911_status_lap115_compaction.md` 및 각 원문.
- lap113~118: `docs/history/laps/20260911_status_lap122_compaction.md` 및 각 원문.
- lap119~139: `docs/history/laps/20260911_lap119_luna_g1_trace_regression_hardening.md`부터
  `docs/history/laps/20260911_lap139_sol_g1_trace_record_serialization_confirmation.md`까지.
- pre-compaction current status: `docs/history/laps/20260911_status_lap129_compaction.md`.
