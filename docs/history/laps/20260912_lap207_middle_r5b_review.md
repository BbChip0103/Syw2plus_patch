# 2026-09-12 | lap 207 | 목표 G1 Stage B — R5-B comparator 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle tier
  (진단·계획·컨펌). 게임 코드·comparator 구현 수정 0줄. 승인 판정은 사람 마일스톤과 구분한다.
- 가설 / 사용자 관찰: lap206 work가 만든 `tools/compare_g1_stage_b.py`가 (a) 절대 slot id를 장면
  키로 쓰지 않는지, (b) `INCONCLUSIVE`/`UNKNOWN_SCENE_MISMATCH`가 PASS로 세탁되지 않는지,
  (c) 실제 보존 pair의 INCONCLUSIVE 판정이 재현되는지를 본문 재사용 없이 독립 확인한다.
- 예상 PASS / FAIL 조건: fail-closed 계약을 우회해 PASS가 나오는 입력이 하나라도 실행으로
  구성되면 검수 결과는 반려다. 재현 해시·`make check`·safety가 모두 맞고 PASS 세탁 경로가
  없을 때만 승인한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 이번 바퀴 **코드 변경 0**.
  검수 대상 파일 SHA256는 lap206 기록과 일치했다 —
  `tools/compare_g1_stage_b.py` `7bb7d89c24326e0de5cf2d35eee308169b7dc05bad7d82d935c28623ec837c26`,
  `tests/test_compare_g1_stage_b.py` `dcd8eacdee2e8ede8c8c8a676ac1ce06b0df820ff832aa7c187f53b7db3ac5ab`,
  `Makefile` `789f0c8ff7f24abe402ff504023cf80837028378bf1cebe72c130e4112419c92`.
  검수 후에도 세 해시는 동일하다(검수가 대상을 건드리지 않음). 문서만 갱신했고 모두 uncommitted
  (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: **게임 실행 0회, PNG 0장.**
  오프라인 read-only 비교만 수행했다. baseline evidence
  `local/runtime/20260912_022912_3830565_0/output/g1_a/evidence.json`, 후보
  `local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/evidence.json`.
  probe fixture는 `tests/test_compare_g1_stage_b.py`의 synthetic scene을 in-memory로 변형한 것이며
  저장소 fixture를 수정하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 -m pytest -q tests/test_compare_g1_stage_b.py` → **6 passed**
  (lap206 기록의 "5 passed"와 불일치. 현재 파일의 테스트 함수는 6개이며 6이 맞다).
  `make check` → **227 passed**, Ruff PASS, compileall PASS, mypy **10 files Success**, `CONTEXT_PASS`.
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → **SAFETY_PASS**.
  `python3 tools/compare_g1_stage_b.py <baseline> <candidate>` →
  `status=INCONCLUSIVE`, scene `candidate: scene is missing or is not an object`,
  세 단계 모두 `required input stage is missing`, `production=NOT_COMPARED`, **exit 2**.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **검수 결과 = 조건부 반려(REJECT-with-repairs).**
  재현은 PASS이나, 실행으로 구성한 PASS 세탁 경로가 존재한다.

  재현 PASS 항목:
  - 파일 SHA256 3종 일치.
  - 실제 보존 pair의 `INCONCLUSIVE` + `production=NOT_COMPARED` 재현.
  - scene signature는 `slot`을 쓰지 않고 owner0/1 type 집합, min(type,x,y) 앵커 기준 상대 오프셋,
    `world_bounds`만 쓴다. 후보 slot을 1199→900으로 바꿔도 장면 판정이 불변임을 확인했다.
  - `STAGES`에 production이 없고 결과에 `NOT_COMPARED`로 명시된다.
  - `content`는 `_g1_input_geometry`의 **논리(800×600) 좌표**이고 물리 좌표는 `x11`에 따로 있으므로,
    2× 후보라도 logical geometry 비교가 항상 FAIL로 기울지 않는다.

  결함 F1 (치명, PASS 세탁) — `_stage_report` minimap 분기의
  `camera_changed_*` 술어가 `_camera(before) != _camera(after)`이고 `_camera`는 누락 시 `None`을
  반환한다. 후보 evidence에서 `minimap.before.camera`를 **삭제**한 probe에서 comparator는
  `camera_changed_candidate=True`로 통과시키고 **overall `PASS`**를 산출했다. 관측 누락은
  `INCONCLUSIVE`여야 한다는 자체 계약과 정면 충돌한다. camera 이동 관측이 아예 없는 후보 run이
  카드 PASS를 받을 수 있다.

  결함 F2 (중대, 근거 없는 FAIL) — `selected_identity`가 `[selected_slot, selected_type]`을
  **절대 slot id 포함**으로 원본↔후보 직접 비교한다. 장면이 같고 count delta가 같고 type도 같은데
  engine slot id만 1199→1100인 probe에서 `selected_identity=False` → 단계 FAIL → **overall FAIL**.
  같은 도구가 장면 키에서는 slot id를 "run 간 비교 불가"로 배제해 놓고 판정 술어에서는 동일성을
  요구한다. slot id가 프로세스 간 안정하다는 역어셈블/관측 근거는 저장소에 없다. `count>=2`와
  같은 "근거 없는 절대 상수" 부류다.

  결함 F3 (중대, 분쟁 오라클 상속) — `_stage_report`가 `result != "PASS"`를 **최초** 검사해 `FAIL`을
  낸다. 보존 baseline의 `drag_select.result`는 `FAIL_NO_EFFECT`이고, lap205 middle이 이를
  **판정식 결함(오라벨)**로 확정했다. 따라서 후보 evidence가 생기는 즉시 comparator는 비교를 한 번도
  하지 않은 단계에 대해 카드 수준 `FAIL`을 낸다. 게다가 timeout 단계의 실제 관측은
  `after.last`(slot 1198/type 21)에 들어 있는데 `_selection`은 `after.selection`만 읽으므로,
  분쟁 중인 바로 그 단계의 델타를 comparator는 **구조적으로 읽을 수 없다**. R6-B 미결 상태가
  카드 FAIL로 세탁된다.

  결함 F4 (경미, fail-open) — `_inputs_by_tag`의 `duplicate input tag` 등 `input_errors`가 결과에
  기록만 되고 `status` 산정에 전혀 반영되지 않는다. 후보 `inputs`에 `unit_select`를 중복 추가한
  probe에서 `input_errors`가 채워진 채로 **overall `PASS`**가 나왔다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 바퀴는 읽기 전용이라 회귀 없음
  (`make check` 227/Ruff/mypy/safety 모두 PASS, 대상 해시 불변). R5-B는 **승인하지 않는다**.
  F1/F4는 실패를 닫는 방향(엄격화)이라 사용자 실행 승인 범위의 bounded repair로 work tier에
  넘길 수 있다. F2/F3은 FAIL→UNKNOWN 판정 의미를 바꾸는 변경이라 R6-B와 같은 승인 경계로 보고
  **승격**한다. 승격 재결 전 구현 금지. 제품 G1 합격·G2~G4 승인은 여전히 없다.
- 다음 한 가지: work tier가 F1과 F4만 bounded repair로 고치고 각각 회귀 fixture를 추가한다
  (F1: 후보 `minimap.before.camera` 누락 → `INCONCLUSIVE`; F4: 중복/불량 input 엔트리 →
  PASS 금지). F2/F3은 Sol/Astra 또는 사용자 재결 전까지 착수 금지이며, 후보 Stage B run도
  R6-B 재결 전까지 계속 금지다.
