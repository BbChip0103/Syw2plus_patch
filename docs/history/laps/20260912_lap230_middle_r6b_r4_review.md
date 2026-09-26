# 2026-09-12 | lap 230 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier
  (진단·계획·컨펌). 게임/제품 코드 hands-on 수정 없음. lap229 work(Luna/high) 결과의 독립 검수다.
- 가설 / 사용자 관찰: lap229의 R6-B-R4 수리가 (a) `selection_observation.status`를 매 poll의
  최종 관측으로 갱신하고, (b) 손상 이력을 유계로 보존하며, (c) R6-B-R2/R3 semantics와 PASS 조건을
  전혀 완화하지 않았는지. lap229 기록과 독립적으로 기대값을 먼저 적고 실행으로 대조한다.
- 예상 PASS / FAIL 조건: 자체 probe 25케이스에서 R4 계약 케이스 전부 AGREES면 범위 승인.
  R4가 새로 만든 회귀(기존 semantics 완화, 손상 세탁, 이력 소실)가 1건이라도 나오면 반려.
  R4 밖의 선재 결함은 반려 사유가 아니라 후속 등록 대상이다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품/도구 코드 변경 **0**.
  신규 검수 산출물만 추가 —
  `docs/history/laps/probes/20260912_lap230_r6b_r4_review_probe.py`,
  `docs/history/laps/probes/20260912_lap230_lap228probe_rerun_report.json`,
  `docs/history/laps/probes/20260912_lap228_r6b_r3_review_report.PROVENANCE.md`,
  본 기록, `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  `loop/ESCALATE_SOL`. 검수 대상 해시는 lap229 신고값과 일치함을 재계산으로 확인했다:
  `tools/runtime_env.py` `f39d26fc578c7a33379eb2556f588d4b56a5a24a9ae618ac590947cbfbc4c76e`,
  `tests/test_runtime_env.py` `d030b04d70d72bd86d15fee6abf6fa6ead15f56691d23f08f2950b3a748de397`.
  uncommitted (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: pinned original EXE SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`make check`의
  `tests/test_binary_contract.py` 13건으로 재확인). 후보/EXE/DLL/assets/baseline/golden 변경 0.
  **게임 실행 0회, PNG 0장.** fixture는 synthetic fake-clock selection observation과
  `_wait_state` 직접 구동뿐이며 실제 Stage B 입력 증거가 아니다. 활성 플레이어/지도/군대 해당 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap230_r6b_r4_review_probe.py`
  → 25케이스 **23 AGREES / 2 DEFECT**;
  `.venv/bin/python docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`
  → `wait_defects=[]`, `reachability_defects=[]`, `preservation_defects=[]`,
  `surgicality_verdict=AGREES`, grid 13,689 cases / 2,052 changes (출력 보존:
  `docs/history/laps/probes/20260912_lap230_lap228probe_rerun_report.json`);
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'g1_selection_response or
  g1_selection_sequence or g1_input_verdict or g1_selection_evidence or g1_selection_reader'`
  → **20 passed**; `make check` → **247 passed**, Ruff PASS, compileall PASS,
  mypy 10 source files Success, `CONTEXT_PASS`, exit 0;
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.

## 측정값 / 판정

**판정: R6-B-R4 범위 승인(scope approval) + 비차단/차단성 후속 2건 등록.**
R6-B 전체와 제품 G1은 계속 **미승인**이다. 이건 기계·정적 검수이고 Stage B 증거가 아니다.

- **C1 최종성 — R4의 핵심 주장은 성립한다(7/7 AGREES).** 손상 poll 뒤 온전한 poll이 오면
  `status`가 `CORRUPTED`→`SOUND`로 갱신되고(C1a), 반대로 온전 poll 뒤 손상 poll이 오면
  `SOUND`→`CORRUPTED`로 다시 내려간다(C1c). 즉 갱신은 단방향 세탁이 아니라 최종 관측을 따른다.
  손상/온전 교대 5회에서 `corrupted_poll_count`는 손상 poll 수(3)만 세고(C1d),
  first/last provenance가 각각 첫/마지막 손상 poll을 가리키며(C1e/C1f),
  `selection_observation` 키 집합은 8개로 고정돼 이력이 무한 증가하지 않는다(C1g).
- **C2 보존 — 기존 semantics는 하나도 완화되지 않았다(5/5 AGREES).** count 1→0은 여전히
  응답으로 센다(C2a, R6-B-R2 불변). 음수 count fail-close(C2b, R3 불변), `bool`/`float` count
  거부(C2c/C2d), 실제 identity 변화의 응답 판정(C2e) 모두 유지된다.
- **C3 대기 수준 W1~W3 — lap228이 등록한 노출이 실제로 닫혔다(8/8 AGREES).**
  영구 손상은 `UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`(C3a), 일시 손상 뒤 온전한 무반응은
  `FAIL_NO_EFFECT`(C3b)이며 이때도 `corrupted_poll_count=2`와 first provenance가 남고(C3c)
  최종 status는 `SOUND`다(C3d). 일시 손상 뒤 실제 응답은 timeout 없이 반환되며 status `SOUND`와
  손상 이력을 동시에 보존한다(C3e~C3g). 마지막 poll들이 손상되면 다시 `UNKNOWN`으로 간다(C3h).
  lap228 probe 재실행도 W1~W3 defect 0으로 독립 일치했다.
- **C4 `before` 오염 — fail-closed 유지(1/1 AGREES).** before 관측이 손상이면 after가 아무리
  온전해도 모든 poll이 손상으로 계수되고 분류는 `UNKNOWN`이다. 하드 FAIL로 새지 않는다.
- **C6 오염된 이전 진단 — 방어됨(2/2 AGREES).** 이전 `corrupted_poll_count`가 음수나 `bool`이면
  0으로 리셋한 뒤 증가하므로, 조작된 누적값이 이력으로 승격되지 않는다.

### 새로 확인한 결함 2건 (둘 다 R4 회귀가 아니라 **선재** 결함)

- **[C5 → R6-B-R6, 차단성 검토 필요] 읽기 예외 poll은 관측 없이 사라지고 hard FAIL로 귀속된다.**
  `_wait_state`는 `read_state` 예외를 `except (OSError, ValueError, struct.error): pass`로
  삼킨다(`tools/runtime_env.py:2990`). 술어가 호출되지 않으므로 `selection_observation`이 갱신되지
  않는다. 실행으로 확인한 두 경로:
  - **C5a**: 모든 poll이 `OSError`면 `selection_observation` 키 자체가 **부재**한데도 분류는
    `FAIL_NO_EFFECT`다. 관측을 한 번도 못 한 run이 "입력이 무반응이었다"는 하드 FAIL이 된다.
  - **C5b**: 온전 poll 2회 뒤 tail이 전부 `OSError`면 stale `SOUND`가 최종 상태로 남아 역시
    `FAIL_NO_EFFECT`다. R4가 세운 "status = 최종 관측" 불변식이 이 경로에서 깨진다.
  `poll_count`는 읽기 실패 poll도 세므로(C5b에서 성공 2 / poll_count 4) 증거가 관측 범위를
  과대표시한다. 도달성은 사문이 아니다: `read_selection`은
  `_read_g1_selection_evidence(read_for_process)`이고 그 안의 `_read_selection`은 예외를 잡지
  않으므로, 후보가 죽거나 메모리가 언맵되면 정확히 이 경로다. lap214 Opus 재결이 기각한
  "관측 없이 하드 FAIL 상속"과 같은 계열이므로 R6-B 전체 승인 전에 닫아야 한다.
  **R4 자체의 결함은 아니다** — 술어가 아예 호출되지 않는 경로라 술어 수리로는 도달할 수 없고,
  `FAIL_NO_EFFECT` 폴백은 lap223 계약부터 있었다.
- **[R6-B-R7, 경미] 검수 probe가 과거 lap 증거 JSON을 덮어쓴다.**
  `20260912_lap228_r6b_r3_review_probe.py`는 출력 경로를 하드코딩해서, 재실행하면 lap228 원본
  보고서를 같은 자리에 덮어쓴다. lap230의 재실행에서 실제로 발생했다. 현재 파일의
  `source_sha256`이 R4 수리 후 값이라 자기식별은 되지만 lap228 기록이 그 경로를 인용한다.
  원본 JSON은 복구 불가이며 **재구성하지 않았다**. 고지와 재실행본을
  `..._report.PROVENANCE.md` / `20260912_lap230_lap228probe_rerun_report.json`으로 보존했다.
  lap228의 실질 판정(W3 DEFECT → R6-B-R4 등록)은 lap228 마크다운 본문에 온전히 남아 있다.

### 범위 밖으로 관찰만 기록 (이번 바퀴에 손대지 않음)

`unit_select` 대기 술어는 `int(item.get("count", 0)) >= 1`뿐이라 slot/type 온전성을 보지 않고
(`tools/runtime_env.py:2481`), 비정수 count에서 `TypeError`는 위 `except`에 잡히지 않는다.
이는 R6-A 계열이며 STATUS가 상위 재결 전 금지한 영역이다. 등록만 하고 진행하지 않는다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 자체 probe 25케이스 중 R4 계약 23건 전부
  AGREES, DEFECT 2건은 모두 선재 결함으로 후속 등록했다. 제품 코드 변경 0, 게임 실행 0,
  보호 자산 변경 0, PASS 조건 완화 0. R6-B 전체·제품 G1·마일스톤은 사용자 미승인이며,
  S1/F2-R2 결정성과 R6-B-R2는 여전히 상위/사용자 재결 대상이다.
- 다음 한 가지: 다음 work tier(Luna/Sonnet5/high)가 **R6-B-R6**(읽기 예외 poll을 관측으로
  계수하고 `FAIL_NO_EFFECT` 대신 `UNKNOWN_*`로 fail-close)을 한 건으로 수리한다.
  그 뒤 R6-B-R5 → R6-B-R7 → F2-R1 → F3-R1 → F3-R2 → F6-R2 순서다.
