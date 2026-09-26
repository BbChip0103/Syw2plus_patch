# 2026-09-12 | lap 213 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier
  (진단·계획·컨펌). 게임 코드 hands-on 수정 없음. lap212 work(Codex work tier) 결과의 독립 검수다.
- 가설 / 사용자 관찰: lap212의 F6 bounded repair가 후보 selector producer의 untagged
  `OBSERVED` 비대칭을 실제로 제거했다면, 후보 flow의 **원본 소스**로 구동한 selector 기록은
  문자열 tag·공용 geometry·즉시 flush를 가지며 comparator `_inputs_by_tag`가 input_error 0을
  보고해야 한다. 보존 evidence는 손대지 않는다.
- 예상 PASS / FAIL 조건: PASS = (a) lap212가 기록한 source fingerprint 재현, (b) 후보 recorder
  closure가 원본 recorder와 이름을 제외하고 동일, (c) 두 초기 selector 분기 모두 untagged 0 /
  input_errors 0 / 기록당 flush 1회, (d) 사전 수리 stub 형태는 여전히 error로 잡힘(음성 대조),
  (e) Fast/safety 재현. FAIL = 어느 하나라도 어긋나거나 새 fail-closed-always 경로가 생김.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 이번 바퀴는 **문서/probe만**
  변경했다 — `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  `docs/history/laps/probes/20260912_lap213_f6_producer_review_probe.py`,
  `docs/history/laps/probes/20260912_lap213_f6_producer_review_report.json`, 이 기록,
  `loop/ESCALATE_SOL`. 검수 대상은 무변경으로 확인:
  `tools/runtime_env.py` sha256 `398c2b8ae4980a5c2ddd44bffba2e5330701341a575b5ad4cc519e8ad790322f`,
  `tests/test_runtime_env.py` sha256 `97d8ee154391a533677fe37dc04ee868bef39b2f6244ee3508fdac9d25818def`
  — 둘 다 lap212 기록과 일치(재현 PASS). `tools/compare_g1_stage_b.py` sha256
  `7730170e610b2e4a39bb02119dd3ec73ad606b6b034d8c43f255f8a07c729ca4`.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`). EXE/DLL/assets/baseline/golden/보존 evidence 변경 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: **게임 실행 0회, PNG 0장**,
  Wine/Xvfb 미사용. 원본·후보 바이너리 SHA 해당 없음. probe fixture는 in-memory selector 상태
  (one-hot `multiplayer/solo`, PS7 고정), crop `(37,41,1600,1200)`, scale `(2.0,2.0)`,
  neutral-cursor 캡처 stub이며 실제 플레이어·지도·군대는 해당 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `sha256sum tools/runtime_env.py tests/test_runtime_env.py tools/compare_g1_stage_b.py`(위 값).
  `.venv/bin/python docs/history/laps/probes/20260912_lap213_f6_producer_review_probe.py`
  → `docs/history/laps/probes/20260912_lap213_f6_producer_review_report.json`.
  `make check` → **232 passed in 35.88s**, Ruff PASS, compileall PASS, mypy 10 files PASS,
  `CONTEXT_PASS`; `bash checks/safety.sh check` → `SAFETY_PASS`. 모두 lap212 수치와 일치.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **F6 bounded repair 독립 검수 = PASS(승인)**.
  - 후보 `g1_presentation_trace.record_input`과 원본 `g1_baseline.input_record`의 소스 본문이
    closure 이름을 제외하고 **동일**(`recorder_bodies_identical_modulo_name: true`). 둘 다
    `_g1_record_selector_input(inputs, tag=…, content_crop=…, scale=input_scale, flush=flush_input_stage)`.
  - 후보 closure **원본 소스를 그대로 실행**해 실제 `_g1_selector_flow`를 구동한 결과:
    초기 solo 분기 tags `['multiplayer_mode_normalize','solo_mode_setup']` results `['PASS','PASS']`,
    초기 multiplayer 분기 같은 tags results `['SKIP','PASS']`. 두 분기 모두 untagged 0,
    `comparator input_errors []`, flush 호출 `[1,2]`(기록당 1회 즉시 flush),
    record keys `tag/content/x11/content_crop/scale/before/after/expected/actual/result`,
    geometry `content=[462,169] x11=[499,210] scale=[2.0,2.0]`(논리 800×600 좌표 + crop + 2× 유지).
  - 음성 대조: 수리 전 stub 형태 `{"args":[…],"result":"OBSERVED"}`는 여전히
    `inputs[0].tag is missing or is not a string`로 잡힌다 → probe가 F6을 판별할 수 있음.
  - 신규 가설 1건을 **반증**: `begin_stage`가 append한 stage 레코드가 같은 tag의 입력 레코드와
    중복돼 F4를 상시 발동시키는가? 아니다. `_g1_run_input_sequence.record()`는 `stage_entry`가
    있으면 같은 dict를 in-place `update`할 뿐 재append하지 않으며, 기존 회귀
    (`tests/test_runtime_env.py:1321`)가 flush된 tags를 정확히 4개로 고정한다. duplicate tag 위험 없음.
  - 제품 판정은 변하지 않는다: G1~G4 미완료, 후보 Stage B 실제 scene/input evidence 여전히 0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **발견 G1-F6-R1(중간, 비차단):** lap212가 추가한 회귀
    `test_g1_selector_input_recorder_writes_tagged_schema_and_flushes`는 **공용 helper만** 검증한다.
    F6의 실제 결함은 helper가 아니라 helper를 우회한 **후보 producer closure**였다. 지금 그 결함
    유형을 막는 테스트가 없어, 누군가 후보 closure를 다시 untagged stub으로 되돌려도 232개 테스트가
    모두 통과한다. 저장소에는 이미 소스 수준 가드 선례가 있다
    (`tests/test_runtime_env.py:1334`의 `inspect.getsource(_g1_run_input_sequence)`).
    → work tier bounded 작업으로 인계(아래 handoff). 판정 의미 변경 없음, 게임 실행 불필요.
  - **관찰(비차단, 기록용):** 원본 경로는 `tools/runtime_env.py:3154`에서 `player0_ready_auto`
    입력 레코드를 남기지만 후보 경로에는 대응 레코드가 없다. comparator `STAGES`는
    `(unit_select, drag_select, minimap)`뿐이라 stage 판정에 영향이 없고 input_error도 아니다.
    fresh pair 바퀴에서 "원본에만 있는 준비 상태 증거"로 인지하고 필요하면 그때 대칭화한다.
  - F2/F3/R6-B 재결, 원본 재실행, R6-A/R6-C, WM_CLOSE teardown은 여전히 별도 승인 경계이며
    이번 승인으로 후보 Stage B run이 열리지 않는다. 마일스톤 사용자 승인도 아니다.
- 사고/정정 기록(숨기지 않음): 검수 중 `loop/.lap_counter`를 `lap=213`으로 덮어썼다. 이 파일은
  loop runner 소유이며 `loop/loop.sh:288-291`이 **개행 없는 정수**만 파싱한다(비정수면 0으로 초기화).
  즉시 원래 바이트 `212`(3 bytes, 개행 없음)로 복원했고 `od -c`로 확인했다. 루프 상태는 원복됐다.
  이번 바퀴가 이 파일을 변경할 이유는 없었다; 다음 세션은 counter가 212에서 증가하는지 확인하라.
- 다음 한 가지: work tier가 **G1-F6-R1 회귀 가드**를 추가한다 — 후보/원본 selector recorder가
  공용 `_g1_record_selector_input`을 쓰고 untagged 레코드를 만들지 않음을 소스/구동 수준에서
  고정하는 테스트. 그 뒤 F2/F3/R6-B 재결(승격 필요)까지 게임 실행은 계속 0회다.
