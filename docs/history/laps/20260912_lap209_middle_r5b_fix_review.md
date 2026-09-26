# 2026-09-12 | lap 209 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier(진단·계획·컨펌).
  게임 코드 hands-on 수정 없음. 이번 바퀴의 한 가지 = lap208 work의 R5-B F1/F4 bounded repair 독립 검수.
- 가설 / 사용자 관찰: lap208이 주장한 대로 (a) 원본·후보 어느 쪽이든 minimap before/after camera가
  정수쌍으로 관측되지 않으면 해당 stage와 overall이 `INCONCLUSIVE`가 되고, (b) `input_errors`가 하나라도
  있으면 모든 stage가 PASS여도 overall이 `PASS`가 되지 않는다. 동시에 (c) 이 엄격화가 실제 발산 FAIL을
  가리거나 정상 pair를 무조건 차단하지 않는다.
- 예상 PASS / FAIL 조건: PASS = F1/F4 probe 전부 non-PASS + 정상 translated pair는 여전히 PASS 가능 +
  실제 camera 발산은 여전히 FAIL + 보존 pair 판정 불변 + 기계 게이트 재현. FAIL = 하나라도 fail-open 잔존
  또는 lap208 기록과 수치 불일치.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 코드 변경 0. 문서/증거만 추가·갱신 —
  `docs/STATUS.md`, `docs/history/laps/20260912_lap209_middle_r5b_fix_review.md`,
  `docs/history/laps/probes/20260912_lap209_r5b_fix_probe.py`
  sha256 `b736226400947bae62fd4486d51dc0cbeec0b61529d07f312868af2393f95ae6`,
  `docs/history/laps/probes/20260912_lap209_preserved_pair_report.json`
  sha256 `bc7918f7b36708b3b3d4ebd18affaedad807422df01bcec57f0aa9d468a234a3`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`.
  검수 대상 파일은 lap208 기록과 해시 일치: `tools/compare_g1_stage_b.py`
  `b6c78e2064cf6376f5473153623c3e6d5716905ac8ce5add3583f13107b56f6b`,
  `tests/test_compare_g1_stage_b.py`
  `0bfa5fcfd61a144e418e5fbe5d74e723f670a6ef77ce4f9eb41cf16d28c06c8f`,
  `Makefile` `789f0c8ff7f24abe402ff504023cf80837028378bf1cebe72c130e4112419c92`.
  uncommitted (LOOP_ALLOW_COMMITS=0, 저장소에 커밋 없음).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0회, EXE/DLL/assets/
  baseline/golden 변경 0, PNG 0장. 활성 플레이어·지도·군대 해당 없음. fixture는 저장소 테스트를
  import하지 않고 이 바퀴에서 새로 작성한 오프라인 evidence(원본 owner0 type70/21, owner1 type49,
  world_bounds 256×256, 후보는 (dx,dy)=(30,-11) 평행이동)와 보존 pair
  baseline `local/runtime/20260912_022912_3830565_0/output/g1_a/evidence.json`,
  candidate `local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/evidence.json`.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `sha256sum tools/compare_g1_stage_b.py tests/test_compare_g1_stage_b.py Makefile` → lap208 기록과 3종 일치.
  2. `.venv/bin/python docs/history/laps/probes/20260912_lap209_r5b_fix_probe.py` (독립 fixture 21 probe).
  3. `.venv/bin/python tools/compare_g1_stage_b.py <보존 baseline> <보존 candidate>` → exit 2,
     보고서 사본 `docs/history/laps/probes/20260912_lap209_preserved_pair_report.json`.
  4. `make check` → 229 passed in 40.49s, Ruff PASS, compileall PASS, mypy 10 files PASS, `CONTEXT_PASS`.
  5. `bash checks/safety.sh check` → `SAFETY_PASS`.
  6. `.venv/bin/python -m pytest -q tests/test_compare_g1_stage_b.py` → 8 passed.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):

  **F1 수리 = 승인(PASS).** 9종 probe 전부 `INCONCLUSIVE`이며 overall `PASS` 없음:
  후보 `before.camera` 삭제(`missing=['candidate_before']`), 후보 `after.camera` 삭제,
  후보 camera `None`, float쌍 `[55.0,60.0]`, 문자열 `"UNKNOWN"`, bool쌍 `[True,False]`,
  3원소 `[55,60,0]`, dict `{"x":..,"y":..}`, 원본측 `before.camera` 삭제.
  bool을 int로 오인하지 않는 점(`_is_int`)과 원본측 누락도 닫히는 점을 각각 확인했다.

  **과잉 차단 없음(PASS).** 평행이동된 정상 pair는 여전히 overall `PASS`(P0)이므로 위 결과는
  "전부 INCONCLUSIVE로 막는 하네스"가 아니라 실제 판별이다. 실제 발산은 그대로 `FAIL`:
  camera 목적지 불일치(P2a), 후보 camera 부동(P2b) 모두 `stages.minimap=FAIL`, overall `FAIL`.

  **F4 수리 = 승인(PASS).** 후보 중복 `unit_select` tag, 원본 중복 `minimap` tag, 비객체 input 엔트리,
  `inputs`가 list가 아닌 경우 모두 overall `INCONCLUSIVE`. 모든 stage가 PASS여도 `PASS`로 닫히지 않는다.

  **F2/F3 = 미변경 확인(의도된 승격 상태).** slot id만 1199→1100 다른 pair는 여전히 overall `FAIL`(F2),
  후보 `drag_select.result="FAIL_NO_EFFECT"`는 여전히 카드 `FAIL`로 상속(F3). lap207 판정대로 재결 대기다.

  **보존 pair 판정 불변(PASS).** overall `INCONCLUSIVE`, scene `INCONCLUSIVE`, 세 stage 모두
  `required input stage is missing`, `production=NOT_COMPARED`, `input_errors` 양쪽 빈 배열, exit 2.
  즉 이번 수리로 기존 증거가 승격되거나 강등되지 않았다.

  **새 결함 F5(경미, fail-open 잔존, 미수리).** `_inputs_by_tag`는 `tag`가 문자열이 아닌 input 레코드를
  오류로 기록하지 않고 조용히 버린다(`tools/compare_g1_stage_b.py:42-44`). probe P4a(`tag` 키 없는 추가
  레코드)와 P4b(`tag: 7`)에서 `input_errors`가 빈 채 overall `PASS`가 나왔다. 필수 3개 stage의 tag가
  사라진 경우(P4c)는 stage 누락으로 `INCONCLUSIVE`가 되므로 영향은 "필수 3종 외의 손상된 레코드가
  조용히 무시된다"에 한정된다. F4와 같은 부류(관측/기록 손상을 PASS로 닫음)이고 실패를 닫는
  엄격화라 기존 bounded repair 승인 범위 안이며, 판정 의미를 바꾸지 않는다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `tests/test_compare_g1_stage_b.py` 8건 본문을 읽어
  fake wait/주입 없이 실제 `compare_evidence` 결과를 검사함을 확인했다. lap206 이후 comparator는 게임을
  실행하지 않으므로 이 검수도 게임 증거가 아니다. 제품 G1 PASS 아님: 실제 후보 Stage B run이 없고,
  R6-B(`count>=2`)·F2·F3 재결이 남아 있어 카드 PASS를 산출할 수 없다. 사용자 승인 범위는 bounded
  repair → fresh validation까지이며 제품 합격·출시 승인은 없다.
- 다음 한 가지: work tier가 F5 bounded repair(비문자열/누락 tag input 레코드를 `input_errors`에 기록)를
  적용하고 회귀 fixture를 추가한다. F2/F3/R6-B는 재결 전 구현 금지, 후보 Stage B run·원본 재실행·
  R6-A/R6-C도 그대로 금지다.
