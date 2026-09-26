# 2026-09-12 | lap 226 | 목표 G1 Stage B — R6-B-R1 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  middle tier(진단·계획·컨펌). 게임 코드 hands-on 수정 0건.
- 가설 / 사용자 관찰: lap225(work)가 `_g1_selection_responded`를 "양쪽 관측이 온전할 때만
  변화를 응답으로 인정"하도록 수리했다고 보고했다. 검수 질문은 lap224 handoff가 사전 등록한
  (a) C4·C5·C7이 `responded=False`인가, (b) C1~C3 판정이 불변인가, (c) 손상 timeout이
  provenance를 남기는가, (d) 새 PASS 경로가 생기지 않았는가, 그리고 middle이 추가한
  (e) **새 온전성 정의가 리더가 실제로 낼 수 있는 모든 관측을 덮는가**,
  (f) **손상 관측이 대기 창을 자르지 않는가**이다.
- 예상 PASS / FAIL 조건: (a)~(d) 재현 = R6-B-R1 범위 승인. (e)/(f)에서 손상이 응답으로
  인정되거나 판정이 최종 관측을 왜곡하면 후속 수리 항목으로 등록한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap226_r6b_r1_review_probe.py`
  sha256 `11b7c62c140e01d513b1c6989368daede1426d17bfd6b9a6c8378bce892dc5f0`,
  생성물 `..._review_report.json`
  sha256 `1d8faf16d29f35318bf58c195d1469db515a442a02aa10c8f7b4273839b02444`.
  문서 `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  `loop/ESCALATE_SOL`, 이 기록 파일.
  **`tools/`·`tests/`·EXE/DLL/assets/baseline/golden 변경 0건.** 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0회,
  Wine/Xvfb/PNG 0장. 검수 대상 `tools/runtime_env.py` sha256
  `b01802703898b8d3435d93bb752ffb2e710fa08b5a85fe82c6ba89caf7603d78`,
  `tests/test_runtime_env.py` sha256
  `befb64f5ef9ef0c92de120b0b9b36a47199a9d3d675a71c026c1173c781bc64a` — 둘 다 lap225
  기록과 **일치(재현 PASS)**. `LOOP_DRY_RUN=0 bash checks/safety.sh check`가 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 재확인했다.
  probe fixture는 lap224/lap225 fixture 객체를 재사용하지 않고 합성 프로세스 메모리를
  실제 리더 `_read_g1_selection_evidence`에 흘려 만든 관측이며, wait 케이스는 가짜 시계로
  실제 `_wait_state`를 구동했다. 활성 플레이어/지도/군대는 해당 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap226_r6b_r1_review_probe.py`
  → 보고서 `docs/history/laps/probes/20260912_lap226_r6b_r1_review_report.json`.
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'g1_selection_response or
  g1_selection_sequence or g1_input_verdict or g1_selection_evidence or g1_selection_reader'`
  → **16 passed**. `make check` → **243 passed**, Ruff `All checks passed`, compileall,
  mypy 10 source files, `CONTEXT_PASS`.
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`. 캡처 없음.

## 판정 — R6-B-R1 범위는 승인. R6-B 전체와 제품 G1은 계속 미승인

### 사전 등록 질문 (a)~(d): 4건 모두 재현 승인

| probe | 관측 | 판정 |
|---|---|---|
| C1 | count 1→3, identity 불변 → `responded=True` | AGREES |
| C2 | count 1→1, identity `1199/70→1198/21`(lap204형) → `responded=True` | AGREES |
| C3 | count·identity 불변 → `responded=False` | AGREES |
| C4 | drag 후 type 읽기 `OSError` → `responded=False`, diagnostics `CORRUPTED` | AGREES(수리됨) |
| C5 | 선택 slot 비활성(풀 손상) → `responded=False`, diagnostics `CORRUPTED` | AGREES(수리됨) |
| C7 | 기준선이 이미 손상, 리더 회복만 → `responded=False`, diagnostics `CORRUPTED` | AGREES(수리됨) |
| C6 | count 1→0 → `responded=True` | 의도대로 **불변**(R6-B-R2 상위 재결 대기) |

(f) 대기 창도 수리됐다. W1(전 poll 손상)은 조기 종료하지 않고 poll 4회를 모두 소진한 뒤
`UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`로 timeout했고, W2(손상 2회 뒤 실제 응답)는 손상
때문에 창이 잘리지 않고 뒤늦은 실제 응답(`1198/21`)을 관측해 반환했다. lap224가 지적한
"첫 손상에서 대기가 끊기고 stage가 UNKNOWN evidence로 PASS 기록" 경로는 닫혔다.
새 PASS 경로는 없다: 술어는 어느 방향으로도 PASS를 추가하지 않고 `False`만 늘린다.

### 새로 확인한 결함 2건 (lap224 handoff 명세 자체의 공백)

lap225는 lap224가 준 온전성 정의(`count`가 int, `count>0`이면 slot int·type≠UNKNOWN)를
문자 그대로 구현했다. 아래 두 건은 lap225의 이탈이 아니라 그 정의의 공백이다.

- **D1/D2 (중대) — 음수 count가 "온전"으로 통과한다.** `_read_selection`은 `0x00899024`를
  **부호 있는** `<i`로 읽는다(`tools/runtime_env.py:1338`). 손상/torn read로 `count=-1`이
  나오면 `_read_g1_command_selection_identity`가 `unsupported selected-unit count`로 막혀
  `selected_slot=None`, `selected_type="UNKNOWN"`이 되는데, `observation_is_sound`는
  `count <= 0`을 무조건 sound로 판단해(`:2050`) identity 변화만 남는다. probe에서
  after 손상(D1)·before 손상(D2) 모두 `responded=True`였다. 엔진이 낼 수 없는 값이 응답으로
  세탁되는 것이므로 C4/C5와 같은 부류이고, 이번에는 count 필드를 통해 들어온다.
  실제 게임에서 음수 count가 관측된 적은 없다(**reachability 미증명**). 다만 C4/C5도 합성
  관측으로 반려한 전례가 있으므로 같은 기준을 적용한다.
- **W3 (중대) — 손상 진단이 누적되어 최종 관측을 덮어쓴다.** `diagnostics`는 poll마다 같은
  `drag_wait_observation` dict이며 손상 시에만 쓰이고 온전한 poll에서 **지워지지 않는다**
  (`:2058~2066`). 그래서 poll1만 일시 손상이고 이후 poll이 전부 온전·무변화이면 실제로는
  `FAIL_NO_EFFECT`인데 timeout 분류가 `UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`가 된다
  (probe W3). 방향은 보수적이지만 **진짜 hard FAIL을 disputed로 흡수**하는 미결 항목
  G1-F3-R2와 같은 부류이고, lap218~219가 승인한 "`after.last` 최종 관측으로 판정한다"는
  선례와도 어긋난다. W2에서는 성공 반환 뒤에도 `selection_observation`이 `CORRUPTED`로 남아
  성공 기록에까지 낡은 손상 딱지가 붙었다.

### 회귀 검사 공백 (경미, 재지적)

lap225가 추가한 `test_g1_selection_response_rejects_corrupted_observations`
(`tests/test_runtime_env.py:1386`)는 여전히 **손으로 쓴 dict** 3케이스다. lap224가 지적한
"실제 리더를 통과한 손상 관측을 고정하라"는 공백은 남아 있다. 이번 probe로 리더→술어 결합이
현재 옳다는 것은 확인했지만, 리더가 손상 표현을 바꾸면 기존 테스트는 잡지 못한다.

## 후속 수리 항목 (work tier 한 바퀴 한 건)

- **G1-R6-B-R3 (차단, R6-B 종결 전 필수):** `observation_is_sound`가 `count < 0`을 손상으로
  거부하도록 좁게 고친다. `count == 0`의 의미(빈 선택)는 **건드리지 않는다** — 그것은
  R6-B-R2 재결 대상이다. 회귀: D1/D2가 `responded=False`이고 diagnostics가 `CORRUPTED`,
  C1~C7 기존 판정 불변. 새 PASS 경로 금지.
- **G1-R6-B-R4 (비차단):** 손상 진단을 poll마다 최종 관측 기준으로 갱신한다. 온전한 poll에서는
  `status`를 `SOUND`로 되돌리되 `corrupted_poll_count`와 첫/마지막 손상 provenance는 보존해,
  timeout 분류가 마지막 관측을 반영하게 한다(F3의 `after.last` 선례와 정합). 회귀: W1은
  `UNKNOWN_SELECTION_OBSERVATION_CORRUPTED` 유지, W3는 `FAIL_NO_EFFECT`, W2는 성공 기록에
  손상 이력만 남기고 상태는 `SOUND`.
- **G1-R6-B-R5 (비차단):** C4·C5·C7·D1을 `_read_g1_selection_evidence`로 만든 관측으로
  고정하는 회귀 테스트를 추가한다. 손으로 쓴 dict 케이스는 유지한다.

## 측정값 / 판정

probe 술어 11케이스 중 9 AGREES / 2 DEFECT(D1·D2), wait 3케이스 중 2 AGREES / 1 DEFECT(W3).
targeted 16 passed, `make check` 243 passed, Ruff/compileall/mypy 10 files/`CONTEXT_PASS`,
`SAFETY_PASS`, 게임 실행 0회, PNG 0장. **R6-B-R1 = 범위 승인**(lap224가 준 명세를 정확히
이행했고 C4/C5/C7과 대기 창 절단을 닫았다). **R6-B 전체 = 미승인** — R6-B-R3이 닫히기 전까지
술어에 손상→응답 경로가 하나 남아 있다. 제품/카드 G1 PASS 아님.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

하류 `tools/compare_g1_stage_b.py:266~268`은 D1 관측에서도 `selected_slot=None`이므로
`INCONCLUSIVE`로 fail-close한다. 따라서 D1/W3는 **카드 overall PASS로 직결되지 않고**,
in-run gate와 stage 단위 기록의 정확도 문제다. S1 장면 비결정성, G1-F2-R2 slot 대응,
F2-R1/F3-R1/F3-R2/F6-R2, WM_CLOSE teardown, G2~G4는 그대로 미해결이다. 후보 Stage B run·
원본 재실행·R6-A/R6-C는 계속 금지다. 사용자 제품/마일스톤 승인 없음.

## 다음 한 가지

work tier(Luna 또는 Sonnet5/high)가 **G1-R6-B-R3만** 수리한다. 그 다음 middle이 독립 검수하고,
승인 뒤 offline 큐는 R6-B-R4 → R6-B-R5 → F2-R1 → F3-R1 → F3-R2 → F6-R2 순으로 한 바퀴 한 건이다.
R6-B-R2(count 1→0의 의미)는 Astra/사용자 재결 전까지 누구도 건드리지 않는다.
