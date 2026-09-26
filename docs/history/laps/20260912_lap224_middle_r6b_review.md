# 2026-09-12 | lap 224 | 목표 G1 Stage B — R6-B 선택 응답 술어 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  middle tier(진단·계획·컨펌). 게임 코드 hands-on 수정 0건.
- 가설 / 사용자 관찰: lap223(work, 기록 파일명 lap222)이 `drag_select`의 절대 `count>=2`
  게이트를 공용 `_g1_selection_responded`로 교체했다. 검수 질문은 (a) 실행 경로에서
  `count>=2`가 사라졌는가, (b) lap204형 identity-only 응답을 인정하는가, (c) 무반응이
  계속 FAIL/timeout인가, 그리고 STATUS가 사전 등록한 (d) **감소·손상 evidence가 PASS로
  세탁되지 않는가**이다.
- 예상 PASS / FAIL 조건: (a)~(c) 재현 + (d) 손상/감소 관측이 응답으로 인정되지 않음 =
  승인. (d)가 깨지면 조건부 반려 후 work tier 수리 handoff.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap224_r6b_selection_response_review_probe.py`
  sha256 `713e15faab03c2aa3ff5add1ddd85868c380d7012691779ce44aa116a33e6705`,
  생성물 `..._review_report.json`. 문서 `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`,
  이 기록 파일. **`tools/`·`tests/`·EXE/DLL/assets/baseline/golden 변경 0건.**
  커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0회,
  Wine/Xvfb/PNG 0. 검수 대상 `tools/runtime_env.py` sha256
  `9e607407b10b593710406b4beb250386640c118e4655a5de46a7a1954d8c5e80`,
  `tests/test_runtime_env.py` sha256
  `12f1a2f31ad3437e5234bef9912883781ddb4275f6999a3ef47c21e75a5befc4` — 둘 다 lap223
  기록과 **일치(재현 PASS)**. probe fixture는 lap222/223 fixture를 재사용하지 않고
  합성 프로세스 메모리(count/first_slot/exists/type 주소)를 직접 공급해 실제 리더
  `_read_g1_selection_evidence`를 통과시킨 관측이다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap224_r6b_selection_response_review_probe.py`
  → 보고서 `docs/history/laps/probes/20260912_lap224_r6b_selection_response_review_report.json`.
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'g1_selection_response or
  g1_selection_sequence or g1_input_verdict'` → **6 passed**(lap223 수치 재현).
  `make check` → **239 passed**, Ruff `All checks passed`, compileall, mypy 10 files,
  `CONTEXT_PASS`. `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.

## 판정 — 조건부 반려 (REJECT-with-repairs). 제품/카드 G1 PASS 아님

### 재현되어 승인하는 부분 (work tier 요청 (a)~(d) 중 3건)

| probe | 관측 | 판정 |
|---|---|---|
| 정적 | 실행 경로에 `int(item.get("count",0)) >= 2` 없음, wait/최종 gate 모두 `_g1_selection_responded` | PASS |
| C1 | count 1→3, identity 불변 → responded=True | PASS |
| C2 | count 1→1, identity `1199/70→1198/21`(lap204형) → responded=True | PASS |
| C3 | count·identity 모두 불변 → responded=False (FAIL/timeout 유지) | PASS |

`unit_select`의 `count>=1` 게이트는 불변이고, R6-B는 새 comparator PASS 경로를 만들지 않는다.

### 반려 사유 — 손상/감소 관측이 in-run 응답으로 인정된다 (probe C4~C7, 4건 모두 DEFECT)

`_read_g1_selection_evidence`(`tools/runtime_env.py:1344`)는 읽기 실패와
`_CommandCellSnapshotError`를 **삼켜서** `selected_type="UNKNOWN"`(+provenance)로 되돌린다.
`_g1_selection_responded`(`:2039`)는 그 `UNKNOWN`을 **값의 변화**로 보기 때문에:

- **C4 (치명)** drag 이후 type 읽기가 일시 실패(`OSError`)하면 `70→"UNKNOWN"`이 변화로 잡혀
  `responded=True`. 관측 손실이 응답으로 세탁된다. lap207 F1과 동일한 부류다.
- **C5 (치명)** 선택 slot이 비활성이 되는 풀/상태 손상(`selected unit slot is not active`)도
  `UNKNOWN`으로 접혀 `responded=True`. 손상이 "엔진 응답"이 된다.
- **C6 (중대)** count 1→0(선택 상실)은 identity가 `None/UNKNOWN`이 되어 `responded=True`.
  STATUS가 사전 등록한 "**비퇴행** 변화만 효과로 인정"을 만족하지 않는다.
- **C7 (중대)** `drag_before`가 이미 손상(`UNKNOWN`)이면 리더가 **회복**하는 것만으로
  `responded=True`. 비교 기준선 자체가 손상인데 PASS가 된다.

파급은 최종 `drag_pass`뿐이 아니다. 같은 술어가 `stage_wait` 조건이므로(`:2496~2500`)
10초 창 안의 **첫 손상 관측에서 대기가 즉시 종료**된다. 실제 응답이 그 뒤에 왔더라도 관측되지
않고, stage는 `UNKNOWN` evidence로 `PASS` 기록된다.

완화(수위 조정용 사실): 하류 `tools/compare_g1_stage_b.py:266~268`은 `selected_slot/type`이
없거나 `UNKNOWN`이면 `INCONCLUSIVE`로 fail-close한다. 따라서 C4~C7이 **카드 overall PASS**로
직결되지는 않는다. 그러나 (1) in-run gate가 `RuntimeSafetyError`로 나쁜 run을 세우지 못하고,
(2) 대기 창이 잘려 정상 응답을 놓치며, (3) run 단위 stage 판정이 `PASS`로 기록된다. 세 가지
모두 "관측 없음/손상은 PASS가 아니다"라는 이미 승인된 원칙에 어긋난다.

### 회귀 검사 공백

`tests/test_runtime_env.py:1342` `test_g1_selection_response_accepts_count_or_identity_change_only`는
손으로 만든 dict 3케이스(증가·identity변화·무변화)뿐이다. 실제 리더를 통과한 손상 관측,
count 감소, 손상 기준선은 고정되어 있지 않다.

## work tier handoff — G1-R6-B-R1 (차단, 수리 필요)

범위: `_g1_selection_responded`가 **양쪽 관측이 온전할 때만** 변화를 응답으로 인정하도록
fail-close 한다. 온전성 정의는 기존 comparator와 같게 `count`가 int이고,
`count>0`이면 `selected_slot`이 int이며 `selected_type`이 `"UNKNOWN"`이 아닐 것.
어느 한쪽이라도 손상이면 응답이 아니며, `stage_wait`는 계속 폴링하고 timeout 분류는
"무반응"이 아니라 **관측 손상(provenance 포함)**으로 기록한다.
회귀: (a) C4·C5·C7이 `responded=False`, (b) C1~C3 판정 불변, (c) 손상 timeout이
provenance를 evidence에 남김. **새 PASS 경로를 만들지 않는다.** middle이 다시 독립 검수한다.

## 상위 tier 재결 — G1-R6-B-R2 (비차단, work tier 범위 아님)

count 1→0(선택 상실)을 "엔진 응답"으로 볼 것인가. 근거가 충돌한다: STATUS 사전 기준은
비퇴행 변화만 인정하라고 하고, lap223 구현 계약은 모든 변화를 인정한다. band drag가 빈 영역을
잡아 기존 선택을 해제하는 것도 실제 엔진 반응일 수 있다. middle 권고는 **이 고정 drag
(350,180→550,350, owner0 HQ/worker 대상)에서는 빈 선택을 응답으로 세지 않는 것**이다.
선택 상실은 "입력 무시"와 "무관한 상태 변화"와 구분되지 않기 때문이다. 다만 판정 의미 변경이라
Astra/high 또는 사용자 재결 전까지 work tier는 이 항목을 건드리지 않는다.

## 측정값 / 판정

targeted 6 passed, `make check` 239 passed, Ruff/compileall/mypy 10 files/`CONTEXT_PASS`,
`SAFETY_PASS`, 게임 실행 0회, PNG 0장. probe 7케이스 중 3 AGREES / 4 DEFECT.
R6-B = **조건부 반려**. lap223이 승격한 "첫 필수 gate 실패 후 bounded repair" 이력은 재현
확인했고(현재 트리에서 재실행 시 전량 통과) 숨기지 않는다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

S1 장면 비결정성, G1-F2-R2 slot 대응, F2-R1/F3-R1/F3-R2/F6-R2, WM_CLOSE teardown, G2~G4는
그대로 미해결이다. 후보 Stage B run·원본 재실행·R6-A/R6-C는 계속 금지다. 사용자 제품/마일스톤
승인 없음.

## 다음 한 가지

work tier(Luna 또는 Sonnet5/high)가 **G1-R6-B-R1만** 수리한다. 그 다음 middle이 독립 검수하고,
승인 뒤 offline 큐는 F2-R1 → F3-R1 → F3-R2 → F6-R2 순으로 한 바퀴 한 건이다.
