# 2026-09-12 | lap 196 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 지정 middle(진단·계획·확인); Claude Code `claude-opus-5`/high.
  hands-on 게임 구현 없음. 문서만 변경.
- 가설 / 사용자 관찰: lap195 work가 구현한 N1(continue 경로 top-level 진단 승격)과 N2(후보
  evidence.json 중복 write 제거)가 (a) 실제로 진단을 보존하고, (b) `required_inputs`/`overall`
  판정식을 바꾸지 않으며, (c) lap193이 승인한 R1~R4와 R5 경계를 회귀시키지 않았는가.
- 예상 PASS / FAIL 조건:
  PASS = lap195 기록 해시 2/2 일치 + `make check`/safety 독립 재현 + 자체 드라이버 probe에서
  4개 입력 태그 생성·production BLOCKED·(670,490) 미전송·top-level과 입력 레코드의 진단 키집합 일치·
  `required_inputs=False`·`overall=BLOCKED`·후보 final evidence write 1회·R5 술어 무변경.
  FAIL = 위 중 하나라도 불일치하거나 N1이 판정 입력으로 흘러 들어감.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`, 본 기록.
  **source/tests 변경 없음** — 검수 전후 `tools/runtime_env.py`
  `e511ef39748098c8a21ae95255130c92c9355a72e39221f1b1adfe8c80736162`,
  `tests/test_runtime_env.py` `7ff0bcd8add7ee02ae690e5daa9e1c27a81f9947b5498c57b77d646fdb15fbcd`
  동일(= lap195 기록값과 2/2 일치). `LOOP_ALLOW_COMMITS=0`, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE 무변경.
  **게임 run 0회**, 후보 run 0회, Stage B 재실행 0회, PNG 0장. fixture는 probe가 자체 구성한
  command-cell 메모리 이미지(stable-ineligible = `branch_type_flags=0`, eligible =
  `G1_COMMAND_BRANCH_REQUIRED_MASK`)이며 활성 플레이어/지도/군대는 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `make check` → **211 passed / exit 0**, Ruff·compileall·mypy(9 files)·`CONTEXT_PASS`;
  `bash checks/safety.sh check` → **SAFETY_PASS / exit 0**;
  독립 probe `temp/20260912_014338_lap196_probe_n1n2.py`
  (SHA256 `8bbf6c4e2768df7b2287cd5a3266b6316e1a4d5e06a5f05eb550c2d549c55548`)
  → **30 단언 / 실패 0**. probe는 lap192/lap195 테스트 본문을 import·재사용하지 않은 자체
  드라이버이며 실제 `_g1_flush_input_stage` 배선으로 tmpdir에 evidence를 쓰고 디스크에서 되읽는다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **N1 승인.** stable-ineligible fixture에서 top-level `error`+`command_branch`+
  `alternate_ui_snapshot`+`primary_command_table`이 디스크 evidence.json에 보존되고, 같은 키가
  production 입력 레코드에도 그대로 남는다(키집합 동일 — 이동/삭제 없음). top-level `error`는
  production 레코드의 `provenance_error`와 문자열이 같다(날조 없음). 기존 fatal `error`를
  seed하면 `setdefault`가 덮지 않고 진단만 추가된다. provenance가 성공하는 eligible fixture에서는
  `error`와 진단 키가 **생성되지 않는다**(허위 오류 없음).
  **N1이 판정 입력이 아님을 확인:** 실제 생성된 inputs로 `required_inputs=False`,
  cleanup·validator가 모두 PASS인 상태에서도 `_g1_presentation_verdict` → `overall=BLOCKED`,
  verdict `error=None`.
  **N2 승인.** `_write_json(trace_dir / "evidence.json", evidence)` 1회(cleanup·provenance 이후
  최종 write), baseline `g1_dir` 최종 write도 1회로 유지 → R3 회귀 없음.
  **R1~R4 회귀 없음.** 4개 태그 `unit_select/production/drag_select/minimap` 전부 생성,
  production `BLOCKED`/`waited=False`, `(670,490)` 클릭 미전송, 예외 뒤 drag 실제 실행,
  `_CommandCellSnapshotError`가 아닌 예외(ValueError)는 여전히 run을 중단(catch 과대 아님),
  eligible 경로에서도 production BLOCKED, `owner0_hq_type`은 UNKNOWN provenance 유지, 추측 type
  하드코딩 없음. **R5 미수행 확인:** `count>=1`/`count>=2` 술어 그대로, 게임 실행 0회.
  **제품 판정: G1은 미완료.** 이것은 모델 기술 컨펌이며 사용자 마일스톤 승인이 아니다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  신규 비블로킹 카드 **N3** 발행 — N1이 비치명 진단을 fatal except 블록과 **같은** top-level
  `error` 키에 넣는다. `evidence.json["error"]`가 non-null인데 `verdict.json["error"]`는 null인
  상태가 정상적으로 발생하므로, evidence만 읽는 보고자는 중단되지 않은 run을 fatal로 오독할 수
  있다(방향은 과대보고이므로 세탁 위험은 아님). 현재 유일한 구분자는 문자열 접두사
  (`_CommandCellSnapshotError: ...` vs. fatal 경로의 `str(exc)`)뿐이다. 단독 바퀴 불필요.
  기록 정정: lap193/lap195가 말한 "진단 4필드"는 `provenance_error`+3개 스냅샷이다.
  `command_cell_diagnostics`는 ineligible 예외가 보유하지 않아 top-level과 입력 레코드 **양쪽 모두**
  없다 — N1의 누락이 아니다(키집합 동일로 확인).
  미검증으로 남는 것: 실제 원본/후보 Stage B 비교, WM_CLOSE teardown 결함, random seed,
  minimap 카메라 절대 목적지, G2~G4 제품 증거.
- 다음 한 가지: **새 사용자 승인 대기.** R5와 Stage B 원본/후보 재실행은 모델이 결정하지 않는다.
  승인 전 진행 가능한 안전 작업은 N3(top-level 진단과 fatal error의 구분자 추가)뿐이며
  `tools/runtime_env.py`와 해당 `tests/`로 제한한다.
