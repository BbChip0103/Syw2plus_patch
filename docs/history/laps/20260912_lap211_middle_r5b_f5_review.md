# 2026-09-12 | lap 211 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier
  (진단·계획·컨펌). 게임 코드/런타임 hands-on 수정 없음. `LOOP_PERMISSION_MODE=auto` 1회.
- 가설 / 사용자 관찰: lap210 work의 R5-B **F5 bounded repair**(누락/비문자열 `tag`를
  `input_errors`로 기록)가 실제로 fail-open을 닫고, 정상 pair를 과잉 차단하지 않으며,
  F1/F4 수리와 F2/F3 판정 의미를 바꾸지 않는지 저장소 테스트와 독립적으로 검증한다.
- 예상 PASS / FAIL 조건: PASS = 누락/비문자열 `tag` 레코드가 정확한 index와 문구로
  `input_errors`에 기록되고 overall이 `PASS`가 아니며, 정상 평행이동 pair는 여전히 `PASS`,
  실제 발산은 여전히 `FAIL`, 보존 pair 판정은 불변. FAIL = 손상 레코드가 있어도 overall `PASS`,
  또는 정상 pair가 차단되거나 실제 `FAIL`이 `INCONCLUSIVE`로 완화됨.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`,
  이 기록, `docs/history/laps/probes/20260912_lap211_*` — **문서/증거만**.
  코드·EXE·DLL·assets·baseline·golden 변경 0. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
  검수 대상 해시:
  `tools/compare_g1_stage_b.py` sha256 `7730170e610b2e4a39bb02119dd3ec73ad606b6b034d8c43f255f8a07c729ca4`
  `tests/test_compare_g1_stage_b.py` sha256 `0f1ba54794aef7f9999c61093410438b19009df05a33a41c50955b3239d68b52`
  `Makefile` sha256 `789f0c8ff7f24abe402ff504023cf80837028378bf1cebe72c130e4112419c92`
  `tools/runtime_env.py` sha256 `3add9254f8df892292619940310a40cd38a95b1fd15605da5fd2c9d1f1f2f2c1`
  probe 원본:
  `docs/history/laps/probes/20260912_lap211_r5b_f5_probe.py` sha256 `5e383c1c439672f6e750b0ef10d2fe60d7bc6cc1a0265e0fe8ab717325e6526f`
  `docs/history/laps/probes/20260912_lap211_f6_producer_conflict_probe.py` sha256 `c03415619716deff05a05779ff9caceb55efa991987dd0c1ec1b4112ead52cfd`
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  **게임 실행 0회, PNG 0장.** 원본·후보 바이너리, 보존 evidence 변경 없음.
  probe fixture는 저장소 테스트를 import하지 않고 새로 작성했다(slot 1401/1402/1403,
  type 70/33/12, world_bounds 256×256 — 저장소 테스트의 1199/1198/1197/1196·180×180과 다름).
  보존 pair: baseline `local/runtime/20260912_022912_3830565_0/output/g1_a/evidence.json`,
  candidate `local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/evidence.json`.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap211_r5b_f5_probe.py` → 25/25 PASS, exit 0.
  보고서 `docs/history/laps/probes/20260912_lap211_r5b_f5_probe_report.json`.
  `.venv/bin/python docs/history/laps/probes/20260912_lap211_f6_producer_conflict_probe.py`
  → `verdict=CONFIRMED`. 보고서 `..._f6_producer_conflict_report.json`.
  `.venv/bin/python tools/compare_g1_stage_b.py <baseline> <candidate>` → `INCONCLUSIVE`,
  scene `INCONCLUSIVE`, 3 stage `INCONCLUSIVE`, production `NOT_COMPARED`, exit 2.
  보고서 `docs/history/laps/probes/20260912_lap211_preserved_pair_report.json`.
  `make check` → 231 passed in 38.21s, Ruff PASS, compileall PASS, mypy 10 files PASS, `CONTEXT_PASS`.
  `bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **F5 = 독립 승인(ACCEPT).** 25 probe 내역:
  후보측 손상 9종(`tag` 키 누락 / int 7 / None / True / False / float 3.5 / list / dict / bytes)
  전부 `inputs[4].tag is missing or is not a string` 1건과 overall `INCONCLUSIVE`.
  원본측 2종(키 누락 / None)도 `input_errors.baseline`에 기록되고 overall `INCONCLUSIVE`.
  index 보고 정확: 손상 레코드를 맨 앞에 넣으면 `inputs[0]`, 2건이면 `inputs[4]`+`inputs[5]`.
  필수 stage(`unit_select`)의 tag를 훼손하면 오류 기록 + 해당 stage `INCONCLUSIVE`.
  과잉 차단 없음: 정상 평행이동 pair `PASS`, 미지의 문자열 tag(`debug_note`)·빈 문자열 tag는
  오류가 아니며 `PASS` 유지. F1(후보 `before.camera` 삭제), F4(중복 tag, 비객체 엔트리)는 여전히
  `INCONCLUSIVE`. 실제 발산은 여전히 `FAIL`: camera 목적지 불일치, 후보 camera 부동,
  selection delta 불일치. 손상 레코드가 `FAIL`을 `INCONCLUSIVE`로 세탁하지 않는다(P24).
  **신규 F6 = 확정된 차단 결함(CONFIRMED).** 아래 별도 절.
  제품 G1은 미완료이며 후보 증거 승격 0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  F2(절대 slot identity), F3(`FAIL_NO_EFFECT` 오라클 상속 + `after.last` 미판독),
  R6-B(`count>=2`)는 재결 전이라 승격 유지. 후보 Stage B run, 원본 재실행, R6-A/R6-C 금지.
  이 검수는 제품 G1 PASS나 출시 승인이 아니다.
- 다음 한 가지: work tier가 **F6**(후보 selector flow의 untagged `record_input`)을 수리한다.

## 신규 F6 — 실제 후보 run에서 overall `PASS`가 구조적으로 도달 불가

F5 수리를 보존 pair에 적용하자 lap209에서 비어 있던 `input_errors.candidate`가
`["inputs[1].tag is missing or is not a string", "inputs[2].tag is missing or is not a string"]`로
바뀌었다. 원인은 comparator가 아니라 **후보 evidence 생산자**다.

- 후보 evidence `inputs`는 3건이고 `tag`는 `['menu', None, None]`이다. index 1~2는
  `{"args": [...], "result": "OBSERVED"}` 형태로 `tag` 키 자체가 없다.
- `tools/runtime_env.py:3500-3502`의 `record_input()`이 `{"args": list(args), "result": "OBSERVED"}`를
  그대로 `inputs`에 append하고, `:3529`에서 그 stub을 `_g1_selector_flow(...)`에 넘긴다.
- 원본(baseline) 경로는 `:3091`에서 같은 `_g1_selector_flow`에 **tagged** `input_record`
  (`_g1_record_input`)를 넘긴다. 그래서 baseline `inputs` 9건은 모두 문자열 tag를 갖는다.
- 후보 경로는 selector flow 뒤 `g1_input_sequence`가 켜졌을 때만 tagged
  `unit_select`/`production`/`drag_select`/`minimap`을 추가한다.

결과: 앞으로의 후보 Stage B run은 항상 untagged `OBSERVED` 레코드를 포함하므로, F5가 이를
`input_errors`로 기록하고 F4가 "input 오류가 있으면 overall `PASS` 금지"를 적용해 **세 stage가
모두 PASS이고 scene도 일치해도 overall은 `INCONCLUSIVE`**가 된다. 생산자 형태를 그대로 본뜬
probe에서 `overall_status_with_observed_records=INCONCLUSIVE`,
동일 pair에서 untagged 2건만 제거한 대조군은 `overall_status_without_observed_records=PASS`로
확인했다(`verdict=CONFIRMED`).

이는 fail-open이 아니라 **항상 닫히는 fail-closed**이며, 사용자가 승인한
"bounded repair → fresh validation"에서 후보 run 1회를 확정적으로 낭비시킨다. F5 자체는 옳고
되돌릴 이유가 없다. 고쳐야 할 쪽은 생산자의 비대칭이다.
