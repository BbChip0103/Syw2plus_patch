# 2026-09-12 | lap 250 | 목표 G1 Stage B — R6-B-R13 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high; middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음. `loop/.lap_counter`=250을 lap 번호로 쓴다
  (루프 런타임 evidence 블록은 `lap=249`로 한 칸 차이가 있으나 PROMPT.md ⑤에 따라 카운터
  파일 값을 쓴다. 카운터는 읽기만 했다).
- 가설 / 사용자 관찰: lap249 work가 `_wait_state`의 성공 반환 경로에서 read coverage를
  확정하고 그 9개 필드를 stage record와 `input_checks` verdict에 투영했다고 주장한다. 제시된
  증거는 "targeted 21 passed"와 Fast 전체뿐이라 (a) 새 호출이 실제로 load-bearing인지,
  (b) 반대로 성공 응답을 coverage로 gate하는 부작용이 없는지, (c) 투영 경로(스테이지 레코드
  /`wait_observation` 폴백)가 각각 assert되어 있는지를 보여주지 못한다. 이 셋을 독립 하네스로
  따로 측정한다.
- 예상 PASS / FAIL 조건: **PASS**는 (C0) 출하 회귀가 실제 저장소에서 통과하고, (C1) 구현을
  보지 않고 계약에서 직접 쓴 기대 모델과 성공 시퀀스 전수 행렬이 불일치 0이며, (C1b) R13이
  건드리지 않겠다고 한 timeout 분류 행렬도 불일치 0이고, (C2) 깊이 일치 무변이 미러가 실제
  저장소와 같은 결과를 내며(M0 대조군), (C3) M1~M4 각 변이가 최소 1개의 출하 테스트를
  죽이되 R13 범위 밖 테스트는 죽이지 않을 때다. 하나라도 어긋나면 FAIL로 적고 범위 승인을
  하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): SUT 무변경. 이번 lap 신규 파일은
  `docs/history/laps/probes/20260912_lap250_r13_review_probe.py` sha256
  `c226752f17c10885598f5cee8b7c067ee085e91dd9a589cf658965dc6347b3e2`,
  `...20260912_lap250_r13_review_report.json` sha256
  `20daf15a6c70754266dbf98aa0152b51216344a1b1f36e28aac11a75d15dcb32`,
  이 기록, 그리고 STATUS/handoff/ESCALATE_SOL 갱신. 모두 uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 검수 시점
  `tools/runtime_env.py` sha256 `302c246e3637959c03a32b349befa0640cff72b1f1b5f1a349ad274b88421817`,
  `tests/test_runtime_env.py` sha256
  `9a120a1ce1783bb605e21dc856cf64cdb4d289d5174bc9cbe328ba61735c8f8d` — lap249 기록/ESCALATE_SOL
  지문과 일치하며 검수 전후로 변하지 않았다. 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 제품 EXE/DLL/
  assets/baseline/golden 변경 0. Python 3.13.5/.venv, fake-clock + fake-reader fixture;
  실제 게임/Wine/Xvfb/PNG 실행 0, 플레이어·지도·군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python
  docs/history/laps/probes/20260912_lap250_r13_review_probe.py --output
  docs/history/laps/probes/20260912_lap250_r13_review_report.json` → `exit 0`, verdict 전부 PASS.
  `make check` = **272 passed**, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`.
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` = **SAFETY_PASS**. probe 자체의 R7/R10/R11 가드도
  실측했다: 기존 출력 경로 재지정 → `exit 2` "refusing to overwrite existing evidence",
  `/proc/nope/x.json` → `exit 2` "output parent is not a directory".
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **C0 BASELINE PASS** — 실제 저장소에서 R13 2건 + 인접 read-failure/coverage/R12 회귀 3건 =
    **6 passed, 131 deselected**.
  - **C1 SUCCESS MATRIX PASS** — `{read-error, 미일치 성공}^0..3` + 일치 poll = **15 케이스
    전수**, 불일치 0. 매 케이스에서 반환값, 9개 coverage 필드, `attempts = poll + error` 합계
    정합, `_g1_read_coverage` 투영, verdict의 stage-record/`wait_observation` 두 경로를 모두
    대조했다. 그중 **8 케이스**는 `read_error_ratio > 0.25`인데도 성공 응답을 그대로 돌려주고
    `required_inputs`도 True로 유지했다 — R13이 약속한 "보고만 하고 gate하지 않는다"가 성립한다.
  - **C1b TIMEOUT MATRIX PASS** — `{error, 미일치}^4` = **16 케이스 전수**, 분류 우선순위
    (read failure > coverage > no effect)와 poll 수가 기대 모델과 불일치 0. R13이 timeout 경로를
    건드리지 않았음을 독립 확인했다.
  - **C2 MIRROR CONTROL (M0) PASS** — 깊이 일치(루트 아래 5구성요소) 무변이 미러에서
    `tests/test_runtime_env.py` **137 passed**, 실제 저장소와 동일. lap246 R20 교훈대로 대조군을
    먼저 세웠다.
  - **C3 MUTATIONS PASS** — 같은 미러에서 M1 `성공 경로 coverage 미확정(호출 삭제)` → **1
    failed**, M2 `성공 경로를 coverage로 gate(break)` → **1 failed**, M3 `stage record 투영 삭제`
    → **1 failed**, M4 `verdict의 wait_observation 폴백 삭제` → **1 failed**. 네 변이 모두
    R13 범위 밖 테스트는 0건 죽였다. 죽은 테스트: M1/M2/M4는
    `test_g1_wait_state_pass_exposes_read_coverage_without_gating_response`, M3는
    `test_g1_shared_input_sequence_blocks_production_but_reaches_later_stages`.
  - 판정: R6-B-R13 **PASS / 범위 승인**. 승인 범위는 성공 경로 coverage 확정과 그 보고 투영
    두 곳뿐이며, R6-B-R2 semantics·timeout 분류·제품 G1~G4 증거는 승인 대상이 아니다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: Fast/safety 회귀 없음. 이번 검수는 기계
  1단이며 사용자 마일스톤 승인이 아니다. 남은 위험 두 가지를 기록한다.
  1) **신규 R22(테스트 취약성, 제품 영향 없음)**: M1·M2·M4 세 변이가 모두 **같은 한 개**
     테스트에만 걸린다. 즉 성공 경로 coverage 확정, 비-gate 보장, verdict 폴백 세 성질이
     단일 테스트에 얹혀 있어 그 테스트 하나가 지워지면 셋이 동시에 미검증이 된다. R19와 같은
     종류의 결함이며, 성질별로 독립 assert를 분리하면 해소된다.
  2) **신규 R23(소비자 부재, 제품 영향 없음)**: `read_coverage`를 읽는 코드는
     `tools/runtime_env.py` 밖에 **0개**임을 grep으로 확인했다.
     `tools/check_runtime_evidence.py`와 `tools/compare_g1_stage_b.py`는 아직 이 필드를 보지
     않으므로, R13은 현재 "증거 파일에 적히는" 단계이지 "증거 게이트가 읽는" 단계가 아니다.
     Stage B 증거를 판정에 쓰려면 소비자 쪽 작업이 따로 필요하다.
  S1/F2-R2, R6-B-R2, R14/R15/R19/R20/R21 및 제품 G1~G4는 그대로 미해결이다.
- 다음 한 가지: work tier(Luna/Sonnet5, high)가 게임 없이 **R14**(production 레코드가 읽기
  실패를 UNAVAILABLE로 표기)를 구현한다. Stage B·게임/Wine/Xvfb 실행은 S1/F2-R2 상위 재결
  전까지 계속 금지.
