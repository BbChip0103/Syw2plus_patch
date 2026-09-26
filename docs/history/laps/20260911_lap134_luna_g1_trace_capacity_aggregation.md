# 2026-09-11 | lap 134 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex 실무 작업자 / Luna/high.
- 가설 / 사용자 관찰: lap128 보존 trace의 `surface_release=256`, `blt_fast=256`, overflow 2건은
  method별 상세 이벤트 상한이 PS3 전에 호출을 잘랐다는 증거다. 고정 메모리 안에서 stable key별
  aggregate를 보존하면 정상 stress는 dropped=0으로 검산할 수 있고, key/state가 바뀌거나 용량이
  고갈되면 validator가 숨김없이 BLOCKED해야 한다.
- 예상 PASS / FAIL 조건: 정확히 256 상세 경계와 그 이후 aggregate, object/interface/original/
  present identity, program state, first/last call sequence·tick, method 산술이 synthetic validator를
  통과한다. malformed key·65 aggregate capacity는 BLOCKED다. Fast/PE32/doctor/safety가 PASS하고
  실제 게임 runtime은 실행하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/inmm_stub/direct_draw_trace.c` → `412315b1f5c1199d97a63d9bdee3a580fb12bed95cc6bcccb336c67466c4a121`,
  `tools/check_g1_presentation_trace.py` → `a58a8aa13bd3affb25aaf7355ef5bf803c6fea0efb1320a6c27557f308ef4c1a`,
  `tests/test_g1_presentation_trace.py` → `5d68f12e4d1ed071d27c5418d18519419f6e43af1ca1732bc5791537a36ec13d`,
  `docs/STATUS.md` 및 본 기록. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` verified. 제품 EXE/DLL/assets
  미변경. lap128 historical live trace `local/runtime/20260911_160804_2519243_0/prefix/drive_c/inmm_g1_present_trace.jsonl`
  SHA256 `b105fc3452dc1650aab58cd7c66aa79e97656964a121ab18d80713f6469d8539`, 617행, synthetic 입력이
  아닌 과거 실패 fixture. 새 synthetic JSONL은 256+aggregate/state transition/malformed/65-record
  capacity를 사용했고 플레이어·지도·군대는 N/A다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: historical `wc -l`, `sha256sum`, event counter와 기존
  validator 재실행에서 617행/overflow 2개/validator rc2를 독립 재현했다. targeted
  `.venv/bin/python -m pytest -q tests/test_g1_presentation_trace.py tests/test_direct_draw_abi.py`
  **14 passed**. `make check` **169 passed**, Ruff/compileall/mypy/context PASS. 새 out-of-tree
  i686 PE32 build는 `/tmp/syw2plus_trace_build.DiC2UX/_inmm.dll` file PASS, SHA256
  `f70289e5617faecfa23e3bff340e3813657da60760c2f3e72cf56682a461639b`. `make doctor` 원본/side-effect
  PASS, `bash checks/safety.sh check` `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): fixed `TRACE_MAX_AGGREGATES=64`; method total은
  `detailed_count + aggregated_count + dropped_count`로 summary에 기록한다. aggregate key는
  method/object/interface/original/present/program_state이고 count>0 및 sequence/tick monotonic을
  validator가 확인한다. 256 경계·state transition PASS, malformed duplicate key BLOCKED,
  65-record capacity BLOCKED, full Fast/PE32/doctor/safety PASS. 실제 게임 runtime, 새 PNG, G1
  1600×1200 제품 합격은 **SKIP/미완료**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 첫 `make check`는 새 validator의 mypy
  Optional narrowing 7건으로 중단됐고 해당 코드만 수정한 뒤 재실행 169 passed 및 mypy PASS다.
  실제 게임의 overflow 없는 final summary, process exit/DLL detach, 1600×1200 출력/입력은 미검증.
  lap133 Sol의 close transport MIDDLE CONFIRM PASS와 이번 Luna 구현은 별도이며 사용자 마일스톤
  승인은 없음.
- 다음 한 가지: 새 Sol/high 세션이 이 lap의 세 source/test SHA, aggregate key·summary arithmetic,
  fresh PE32 build와 capacity fail-closed를 독립 검수한다. 검수 전 게임 runtime은 실행하지 않는다.
