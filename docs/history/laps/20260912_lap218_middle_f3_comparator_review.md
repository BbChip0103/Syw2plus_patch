# 2026-09-12 | lap 218 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high / middle tier
  (진단·계획·컨펌). 게임 코드 hands-on 수정 없음, 구현은 work tier로 넘긴다.
- 가설 / 사용자 관찰: lap217이 구현한 F3 수리(비PASS stage result를 카드 `FAIL`로 상속하지 않고
  `UNKNOWN_DISPUTED_ORACLE`로 닫고, timeout shape `after.last`를 관측으로 읽는다)가 (a) 주장대로
  동작하고 (b) 새로운 PASS 세탁 경로를 만들지 않는지를 저장소 테스트와 독립으로 검증한다.
- 예상 PASS / FAIL 조건:
  PASS = (1) 보고된 해시·수치(targeted 12, Fast 236, `SAFETY_PASS`, 보존 pair `INCONCLUSIVE`)가
  재현되고, (2) 저장소 fixture를 쓰지 않고 새로 만든 probe에서 disputed stage가 절대 overall
  PASS를 만들지 않으며, (3) 기존 scene gate / F1 / F4 / F5 fail-closed 동작이 유지된다.
  FAIL = disputed 경로로 PASS가 나오거나, 보고 수치·해시가 재현되지 않는 경우.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap218_f3_comparator_review_probe.py`
  sha256 `0ba588ab3e905e3d2bf28c496c4ca0f2adf3941454252cc468f8445dfb298170`,
  신규 `docs/history/laps/probes/20260912_lap218_f3_comparator_review_report.json`
  sha256 `34ece30634e779427d6fd23dacdbac676631c6b29a470d3de5a9bbb9f07d7d43`,
  본 기록, `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  `loop/ESCALATE_SOL`. 코드/테스트/EXE/DLL/assets/baseline/golden/evidence 변경 0.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`), uncommitted 보존.
  재현한 소스 해시:
  `tools/compare_g1_stage_b.py` `fa83f781269d70db2bcca10f12c866e20be45ab7c48d2c38527d14686e453d1f`
  (lap217 기록과 일치; lap216의 `7730170e…`에서 F3 수리로 변경),
  `tests/test_compare_g1_stage_b.py`
  `d66f901a48d7e867723119199962e44e3808f84dc538b766882b1e4f83b4ab87` (lap217 기록과 일치),
  `tools/runtime_env.py` `398c2b8ae4980a5c2ddd44bffba2e5330701341a575b5ad4cc519e8ad790322f`
  와 `tests/test_runtime_env.py`
  `601ebfc821cf98804741c07bc07780019708d799632ab9a839947f75ea010528`는 lap216과 동일
  = lap217이 런타임 producer를 건드리지 않았다는 주장 확인.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  **게임 실행 0회, PNG 0장, Wine/Xvfb 미사용.** fixture는 (1) probe가 저장소 테스트 helper를
  import하지 않고 새로 만든 synthetic evidence 18종(다른 좌표계·slot·type·bounds), (2) 보존
  pair 원문 `local/runtime/20260912_022912_3830565_0/output/g1_a/evidence.json`
  sha256 `ec6ef7e00ca7c2e33d0fdb9f056dcf905425b57c7f559d05edb3b3349a7bbc12`,
  `local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/evidence.json`
  sha256 `309028386476de06ced251686444e04b7c8e7d9c282f7f52e7ed1dbcf7fc7e59`(둘 다 읽기만 했다).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap218_f3_comparator_review_probe.py`
  → 위 report.json, `unexpected: []`, `disputed_pass_violations: []`;
  `.venv/bin/python tools/compare_g1_stage_b.py <baseline> <candidate>` → `INCONCLUSIVE`,
  scene `INCONCLUSIVE`, 3 stage 모두 `INCONCLUSIVE`, production `NOT_COMPARED`,
  candidate `input_errors` 2건(historical untagged), exit 2;
  `.venv/bin/python -m pytest -q tests/test_compare_g1_stage_b.py` → 12 passed;
  `make check` → 236 passed, Ruff, compileall, mypy 10 files, CONTEXT_PASS;
  `bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **F3 독립 검수 = PASS(범위 한정).** 18 case 전부 사전 예측과 일치했고 disputed 경로로 나온
  overall PASS는 0이다. 재현한 것:
  A1 양쪽 `FAIL_NO_EFFECT`+`after.last` → stage `UNKNOWN_DISPUTED_ORACLE`, overall
  `INCONCLUSIVE`, identity를 `last`에서 [812,44]로 읽음. A2 `after.last` 부재 → `INCONCLUSIVE`.
  A3 minimap `after.last.camera` → `UNKNOWN_DISPUTED_ORACLE`. A4 정상 pair는 여전히 PASS.
  A5 한쪽만 disputed여도 disputed. A6 관측이 서로 달라도 FAIL이 아니라 `UNKNOWN_DISPUTED_ORACLE`.
  A7 `result` 키 누락 → PASS 아님. A8 scene gate가 dispute보다 우선. A9 F4·A10 F1 유지.
  A11 disputed라도 논리 geometry 불일치는 여전히 카드 `FAIL`. A12 `UNKNOWN_BUDGET_EXHAUSTED`도
  disputed. 판정 범위는 comparator 오프라인 semantics뿐이며 제품 G1 PASS가 아니다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  **신규 G1-F3-R1(비차단, 잠재 PASS 세탁):** `_selection`/`_camera`의 `after.last` 폴백이
  source result와 무관하게 항상 켜진다. probe B1(result `PASS` + timeout shape `after`)과
  B2(result `PASS` + `after.selection`이 Mapping이 아닌 손상값 + 정상 `after.last`)는 둘 다
  overall `PASS`가 됐다. 현재 producer는 `after.last`를 `record_timeout` 한 곳
  (`tools/runtime_env.py:2371`)에서만 쓰고 그때 result는 항상 timeout 분류라서 **지금은 도달
  불가**지만, comparator는 오프라인 fail-closed 판정기이므로 producer 결합에 의존하면 안 된다.
  **신규 G1-F3-R2(비차단, 판정력 침식):** `disputed = any(result != "PASS")`가 timeout이 아닌
  하드 `FAIL`(예: `tools/runtime_env.py:2556`의 minimap `"PASS" if minimap_pass else "FAIL"`)까지
  `UNKNOWN_DISPUTED_ORACLE`로 흡수한다. probe B3에서 camera가 안 움직인 후보가 카드 FAIL이 아니라
  overall `INCONCLUSIVE`가 됐다. PASS 세탁은 아니지만 실제 parity 실패를 영원히 UNKNOWN으로
  돌려 루프가 닫히지 않는다. lap214의 재결 대상은 `FAIL_NO_EFFECT`였지 모든 비PASS가 아니었다.
  B4(`before`에는 폴백 없음)·B5(손상된 `last.count`)·B6(3 stage 전부 disputed)는 모두 fail-closed다.
  미해결: S1 장면 통제(최상위, 상위 tier), F2 identity, R6-B, G1-F6-R2, WM_CLOSE teardown.
  사용자 마일스톤 승인 없음. 후보 Stage B run·원본 재실행·R6-A/R6-C는 계속 금지.
- 다음 한 가지: work tier는 lap214/lap217이 정한 대로 **F2 identity 재정의**
  (`(owner, type, 상대 world offset)`)를 게임 실행 없이 구현하고 다음 middle이 독립 검수한다.
  그 뒤 순서는 R6-B → **G1-F3-R1** → **G1-F3-R2** → G1-F6-R2다. F3-R1을 F6-R2보다 앞에 둔
  이유는 F3-R1만이 잠재 PASS 경로이고 F6-R2는 유실 stage를 `INCONCLUSIVE`로 닫기 때문이다.

## lap218 종료 시 파일 해시 (uncommitted 보존, `LOOP_ALLOW_COMMITS=0`)

- `dc5f9ec63cef5d46aa2a3f20d70054715088de61fa64e2233122a2db58181372` `docs/STATUS.md`
- `02b4a2db5f1fd0bc19d70f7b8aa5191f0fbd878e03168f0e504503f9ea5772c2` `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`
- `d114412ddabf0f314d983653ea4e18562445d6bb7315f9282714612e29e7a1c3` `loop/ESCALATE_SOL`
- `0ba588ab3e905e3d2bf28c496c4ca0f2adf3941454252cc468f8445dfb298170` `docs/history/laps/probes/20260912_lap218_f3_comparator_review_probe.py`
- `34ece30634e779427d6fd23dacdbac676631c6b29a470d3de5a9bbb9f07d7d43` `docs/history/laps/probes/20260912_lap218_f3_comparator_review_report.json`
- `fa83f781269d70db2bcca10f12c866e20be45ab7c48d2c38527d14686e453d1f` `tools/compare_g1_stage_b.py`
- `d66f901a48d7e867723119199962e44e3808f84dc538b766882b1e4f83b4ab87` `tests/test_compare_g1_stage_b.py`
- `398c2b8ae4980a5c2ddd44bffba2e5330701341a575b5ad4cc519e8ad790322f` `tools/runtime_env.py`
