# 2026-09-12 | lap 228 | 목표 G1 Stage B — R6-B-R3 middle 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier
  (진단·계획·확인). 프로젝트 라우팅상 Sol 또는 Opus5 자리다. 게임 코드 hands-on 수정 0.
- 가설 / 사용자 관찰: lap227 work가 `observation_is_sound`에 넣은 `count < 0` 거부가
  (a) 실제 리더가 낼 수 있는 관측에 도달하며, (b) 음수 인코딩 전체를 덮고, (c) 음수 외
  동작을 바꾸지 않고, (d) 미결 R6-B-R2(count 1→0)를 건드리지 않고, (e) 대기 창을 조기
  종료시키지 않는지 독립적으로 확인한다.
- 예상 PASS / FAIL 조건: 위 5개가 모두 성립하면 R6-B-R3 **범위 승인**. 음수 외 판정이
  하나라도 바뀌거나, 리더가 음수 관측을 낼 수 없어 수리가 사문(死文)이거나, count 0
  semantics가 흔들리면 반려.
- 변경 파일 / source fingerprint / 커밋: 이번 바퀴 제품/도구 코드 변경 **0**.
  신규 probe `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`와 보고서
  `..._report.json`, `docs/STATUS.md`, 이 기록, `loop/ESCALATE_SOL`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`만 갱신했다.
  검수 대상 해시는 lap227 기록과 일치: `tools/runtime_env.py`
  `9896090d25b1525077e52dc69146840216779b77379d47eefa3f76d8e0892c37`,
  `tests/test_runtime_env.py`
  `50f09bd1296bfc2ca30f126f60b48a3e356f383b0b802883454958f96ec50d08`.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 재확인.
  후보 EXE/DLL/assets/baseline/golden 변경 0. **게임 실행 0회, Wine/Xvfb 0회, PNG 0장.**
  fixture는 probe가 합성한 프로세스 메모리(`read_memory` 스텁)와 그것을 실제 리더
  `_read_g1_selection_evidence`에 통과시켜 얻은 관측이다. 활성 플레이어/지도/군대는 해당 없음.
  이 검수는 기계·정적 수준이며 실제 Stage B 입력 증거가 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`;
  targeted `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'g1_selection_response or
  g1_selection_sequence or g1_input_verdict or g1_selection_evidence or g1_selection_reader'`
  → 18 passed; `make check` → **245 passed**; Ruff PASS, compileall PASS,
  mypy 10 source files Success, `CONTEXT_PASS`;
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
  보고서: `docs/history/laps/probes/20260912_lap228_r6b_r3_review_report.json`.

## 측정값 / 판정

**판정: R6-B-R3 범위 승인(scope approval) + 비차단 후속 1건 증거 보강.**
R6-B 전체와 제품 G1은 계속 미승인이다.

- **Q1 도달성 — 수리는 사문이 아니다.** lap227은 reachability 미증명으로 남겼다. probe는
  `_read_selection`이 `struct.unpack("<i", ...)`로 **부호 있는** dword를 읽고
  (`tools/runtime_env.py:1340`), 음수면 `_read_g1_command_selection_identity`가
  `_CommandCellSnapshotError`를 던지지만 `_read_g1_selection_evidence`의 `except`가 이를
  삼켜(`:1361~1366`) `count=<음수>, selected_slot=None, selected_type="UNKNOWN"` 관측을
  **예외 없이 반환**함을 실행으로 확인했다. 즉 수리 전에는 이 관측이 `count <= 0`에 걸려
  "빈 선택"으로 온전 판정됐다. 수리 대상 경로는 살아 있다.
- **Q2 커버리지 — 음수 인코딩 5종 + 양측 조합 모두 fail-close.** N1 `0xFFFFFFFF`(-1),
  N2 `0x80000000`(INT_MIN), N3 torn dword(-16777215), N4 -2, N5 문자/포인터 바이트
  (-1002917822)를 모두 실제 리더로 만들어 before/after 양쪽에 넣었다. 7/7 AGREES:
  `responded=False`, `status=CORRUPTED`, `before_sound`/`after_sound`가 손상된 쪽만 False.
  N7(음수 count에 그럴듯한 slot/type을 손으로 붙인 경우)도 거부돼, 술어가 "리더가 미리
  slot/type을 지워줬을 것"에 의존하지 않음을 확인했다.
- **Q3 수술성 — 음수 외 동작 변화 0.** lap225 규칙(`count <= 0`을 온전로 취급)을 probe 안에
  독립 재구현하고, count 13종 × slot 3종 × type 3종을 양쪽에 곱한 **13,689 케이스**를
  차분 비교했다. 동작이 달라진 케이스는 **2,052건이며 전부 "음수 count가 포함 + 이전 True →
  현재 False"** 형태다. 그 외 변화는 0건(`changes_all_negative_true_to_false=true`).
  bool `True/False`, `1.0`, `None`, `"1"` 같은 비정수 count의 기존 거부도 불변이다.
- **Q4 보존 — R6-B-R2는 손대지 않았다.** P1(count 1→0, 리더 경유) `True`, P2(count 0 +
  낡은 slot 바이트) `True`, P3(0→0) `False`, P4(0→1) `True`, P5(identity만 변화) `True`,
  P6(무변화) `False`. 6/6 AGREES. 미결 의미 결정이 몰래 바뀌지 않았다.
- **Q5 대기 창 통합 — 조기 종료 없음.** W1(모든 poll이 음수) → `TIMEOUT` +
  `UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`, poll 4회로 창을 끝까지 사용. W2(음수 2회 후
  실제 응답) → `RESPONDED`, 손상 poll이 창을 소모하지 않는다. 둘 다 AGREES.

### 새로 확인한 비차단 사실 (R6-B-R4 노출 확대)

W3(음수 poll 1회 → 이후 전부 온전·무변화)은 `FAIL_NO_EFFECT`가 아니라
`UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`로 분류된다(**DEFECT 1/3**). 이는 **이미 등록된
R6-B-R4**(손상 진단이 온전한 poll에서 지워지지 않아 hard FAIL을 UNKNOWN으로 흡수, probe W3)의
그대로의 재현이며 새 결함 유형이 아니다. 다만 R3이 손상으로 판정되는 관측 집합을 넓혔으므로
**R4의 발동 경로가 하나 늘었다**(이제 일시적 음수 count 1회로도 hard FAIL이 UNKNOWN으로
세탁된다). 이 확대는 fail-safe 방향(FAIL을 PASS로 바꾸지 않음)이므로 R3 승인을 막지 않지만,
R4의 우선순위 근거로 기록한다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 이 검수는 게임 없이 수행한 정적·기계 검수다. 실제 Stage B 원본/후보 run, 실제 입력 대응,
  scene 결정성(S1/F2-R2)은 전혀 다루지 않았고 여전히 상위 재결 대기다.
- R6-B-R2(count 1→0을 응답으로 셀지)는 이번에도 판단하지 않았다. 상위 tier/사용자 결정 대상이다.
- R6-B 전체 승인 아님. 남은 항목은 R6-B-R4, R6-B-R5다.
- 3단 사용자 마일스톤 승인은 별개이며 이번 바퀴로 진행되지 않았다.

## 다음 한 가지

다음 새 work tier(Sonnet5/high 또는 Luna/high)가 **G1-R6-B-R4**를 구현한다: 최종 관측 기준으로
`selection_observation.status`를 갱신하되 `corrupted_poll_count`와 첫/마지막 손상 provenance를
보존한다. 회귀는 W1 분류 유지, **W3 → `FAIL_NO_EFFECT`**, W2 성공 반환 시 `status=SOUND` +
손상 이력 보존이며, 이번 lap228 probe의 W1~W3를 그대로 대조 장면으로 쓸 수 있다.
이후 R6-B-R5 → F2-R1 → F3-R1 → F3-R2 → F6-R2 순서로 한 바퀴 한 건.

## 미커밋 파일 해시 (LOOP_ALLOW_COMMITS=0)

- `docs/STATUS.md` `59b99fd4ad8e3aef1d323b27f0eac8db7f453484693c8dc4bcd91bb6eb805f5c`
- `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`
  `477b9c0bacca43593905a513a323fc88abf2bec54ce7d932d197a32c08436468`
- `docs/history/laps/probes/20260912_lap228_r6b_r3_review_report.json`
  `5ed74a1aeaf57e427a410e0e4b76b51e8ca800c1de8de68c34f5e881e7d10361`
- `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`
  `67c0df3d1a642f2eb61613ff7240faba8506f3aa1c5febe368d0202e7dc65a5d`
- `loop/ESCALATE_SOL` `a6b27a2ee5a679dd98cf2fd95ec082b1f8817f1d5f22bf5a5fc5d425a590c450`
- 검수 대상(미변경): `tools/runtime_env.py`
  `9896090d25b1525077e52dc69146840216779b77379d47eefa3f76d8e0892c37`,
  `tests/test_runtime_env.py`
  `50f09bd1296bfc2ca30f126f60b48a3e356f383b0b802883454958f96ec50d08`.
