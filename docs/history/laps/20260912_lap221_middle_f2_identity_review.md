# 2026-09-12 | lap 221 | 목표 G1 Stage B — F2 identity 독립 검수 (middle tier)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle tier
  (진단·계획·컨펌). 구현하지 않았고 게임을 실행하지 않았다.
- 검수 대상: lap219 F2 identity bounded repair + lap220 타입 경계 수리
  (`docs/history/laps/20260912_lap219_work_f2_identity.md`,
  `docs/history/laps/20260912_lap220_work_f2_gate_repair.md`).
- 가설 / 검수 질문: (a) lap214가 재결한 대로 **절대 slot 동일성이 FAIL 술어에서 제거**됐는가,
  (b) 수리가 **새 PASS 경로를 만들지 않았는가**, (c) 정규화 identity가 실제로 anchor 상대이며
  해소 실패에 fail-closed인가, (d) lap220의 `cast(int, slot)`이 의미 중립인가.
- 예상 PASS / FAIL 조건: 저장소 fixture·테스트 helper를 쓰지 않는 독립 probe 12건이 사전
  예측과 전부 일치하고, 무작위 sweep의 모든 overall `PASS`가 불변식을 만족하며, fresh
  `make check`/safety/targeted/보존 pair 수치가 lap220 기록과 재현되면 범위 한정 PASS.

## 변경 파일 / source fingerprint / 커밋

- 신규: `docs/history/laps/probes/20260912_lap221_f2_identity_review_probe.py`
  (`bac043d1580b0a2a7c88f632859dfadf19bfe3c742562223bd93d6a19f2f8538`),
  `docs/history/laps/probes/20260912_lap221_f2_identity_review_report.json`
  (`e3f63556626ab7e88e17c3849c1d25f51b3518d2fe2c773360f787a94891de40`).
- 문서 갱신: `docs/STATUS.md`, 본 기록, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  `loop/ESCALATE_SOL`(lap221 절 추가, 기존 lap207 원문 보존).
- **코드 변경 0.** 검수 시작·종료 시 해시 동일:
  `tools/compare_g1_stage_b.py` = `f57f5513b00262c0284a60be30b010575a81bc34be3f01eda89b3bc48f09b727`
  (lap220 기록과 일치),
  `tests/test_compare_g1_stage_b.py` = `f7b6add02484eda9f1acf0d24bccec519a1b89fe6977ec85579d0899698fe437`,
  `docs/history/laps/probes/20260912_lap220_f2_identity_probe.py` =
  `0d907af0a9f94a94b069c289f036c319fef17f90913dfd5c4dbd7457a378e778`.
- 커밋 없음(`LOOP_ALLOW_COMMITS=0`). EXE/DLL/assets/baseline/golden/evidence 변경 0.

## 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture

게임 실행 0회, Wine/Xvfb/PNG 미사용, PNG 0장. 독립 probe fixture는 이 검수에서 새로 작성한
synthetic scene이며 lap220 fixture와 수치가 다르다: owner0 = slot 501/502 (**둘 다 type 70**,
world (200,300)/(240,300)) + slot 503 type 12 (210,340), owner1 = slot 601 type 49 (500,700) +
slot 602 type 7 (520,720), `world_bounds` 1024×1024. owner0에 동일 type 2기를 일부러 둬서
**slot↔위치 교환이 scene signature에 보이지 않게** 만들었다. 저장소 `tests/` helper는 import
하지 않았다.

## 실행 명령 / 로그 / 수치

- `.venv/bin/python docs/history/laps/probes/20260912_lap221_f2_identity_review_probe.py`
  → 12/12 예측 일치, `status=PASS`, exit 0.
- `.venv/bin/python docs/history/laps/probes/20260912_lap220_f2_identity_probe.py`
  → 4/4 PASS, exit 0 (lap220 주장 재현).
- `.venv/bin/python -m pytest -q tests/test_compare_g1_stage_b.py` → **14 passed**.
- `make check` → **238 passed** / Ruff `All checks passed!` / compileall /
  mypy `Success: no issues found in 10 source files` / `CONTEXT_PASS`, exit 0.
- `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
- 보존 pair `local/runtime/20260912_022912_3830565_0/output/g1_a/evidence.json` ↔
  `local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/evidence.json`
  → `INCONCLUSIVE`, scene `INCONCLUSIVE`, 세 stage 전부 `INCONCLUSIVE`,
  `production=NOT_COMPARED`, candidate `input_errors` 2건(historical untagged), exit 2.
  **불변이며 제품 증거로 승격하지 않는다.**

## 독립 probe 12건 (예상 → 실제, 전부 일치)

| case | 내용 | 예상 | 실제 |
|---|---|---|---|
| A | 동일 pair | PASS | PASS |
| B | 후보 scene 전체 (+1000,+1000) 평행이동 | PASS | PASS |
| C | **slot·type 동일, 같은 type 2기의 world 위치 교환** | FAIL | FAIL |
| D | scene·선택 slot 일괄 재번호(+400) | INCONCLUSIVE | INCONCLUSIVE |
| E | 선택 slot이 자기 scene에 없음 | INCONCLUSIVE | INCONCLUSIVE |
| F | scene 내 slot 중복(모호) | INCONCLUSIVE | INCONCLUSIVE |
| G | `selected_type`이 scene type과 불일치 | INCONCLUSIVE | INCONCLUSIVE |
| H | identity 동일, count delta 발산 | FAIL | FAIL |
| I | owner1 위치 변경(장면 불일치) | UNKNOWN_SCENE_MISMATCH | UNKNOWN_SCENE_MISMATCH |
| J | `selected_slot` 키 누락 | INCONCLUSIVE | INCONCLUSIVE |
| K | `_stage_report`를 evidence 없이 직접 호출 | PASS(결함 문서화) | PASS |
| L | 무작위 400 sample PASS 불변식 sweep | 위반 0 | 위반 0 |

- **C가 이번 검수의 핵심 새 증거다.** slot과 type이 같은데 정규화 identity가 갈리는 배치는
  수리 전 절대-slot 술어로는 `PASS`였고 지금은 `FAIL`이다. 즉 이 수리는 FAIL 판정력을
  **넓혔지** 좁히지 않았다.
- **D**: stage 2건 모두 `UNKNOWN_SLOT_CORRESPONDENCE`, overall `INCONCLUSIVE`,
  `selected_identity` baseline==candidate. 절대 slot 동일성은 FAIL 술어에서 빠졌다.
- **L**: 400 sample 중 overall `PASS` 74건, 전부 scene `PASS` + `input_errors` 0 +
  두 선택 stage의 slot 동일 + 정규화 identity 동일 + count delta 동일 + 양측 stage
  `result == "PASS"`를 만족했다. 새 PASS 경로 증거 0건.

## 판정

**F2 = PASS (범위 한정).** 승인 범위는 `tools/compare_g1_stage_b.py`의 comparator semantics와
lap220 gate 수치 재현뿐이다. 제품 G1 PASS도, 마일스톤 승인도, 후보/원본 새 run 인가도 아니다.

- lap220의 `cast(int, slot)`은 바로 위 `_is_int(slot)` 가드 뒤에 있고 `cast`는 런타임 무연산이므로
  **의미 중립**이 맞다(`tools/compare_g1_stage_b.py:267~270`). mypy 10 files 통과를 재현했다.
- lap220이 보고한 targeted 14 / Fast 238 / mypy 10 / `CONTEXT_PASS` / `SAFETY_PASS` /
  보존 pair `INCONCLUSIVE`·`NOT_COMPARED`·exit 2 수치는 전부 재현됐다.

## 신규 발견 (둘 다 비차단, 이번 승인에 포함되지 않음)

### G1-F2-R1 — evidence 없는 `_stage_report` 폴백이 절대 slot 술어를 되살린다 (비차단)

`tools/compare_g1_stage_b.py:271~281`에서 `baseline_evidence`/`candidate_evidence`가 `None`이면
identity가 `[slot, unit_type]`로 되돌아간다. probe K에서 이 경로가 절대 slot/type만으로 `PASS`를
낸다. 현재 `_stage_report`의 유일한 호출자는 `compare_evidence`(`:357`)이며 항상 evidence 4개를
넘기므로 **오늘 도달 불가**다. 그러나 코드 주석이 근거로 든 "timeout-oracle probe 직접 호출자"는
저장소 전체 grep에서 **존재하지 않는다**(probe 5종·tests 모두 `compare_evidence`만 호출). 이는
G1-F3-R1과 같은 부류다 — comparator는 호출자 결합에 판정을 기대면 안 된다. 수리 범위는 evidence
인자를 필수로 만들거나 없을 때 `INCONCLUSIVE`로 닫는 것이며, **새 PASS 경로를 만들지 않는다.**

### G1-F2-R2 — slot 강등이 카드 PASS를 "slot id 결정성" 위에 올려놨다 (비차단, 상위 tier 재결 사항)

`UNKNOWN_SLOT_CORRESPONDENCE`는 stage를 PASS에서 끌어내리고 overall을 `INCONCLUSIVE`로 만든다
(`:335~341`, `:369~372`, probe D). 따라서 **카드 overall PASS는 원본 run과 후보 run이 동일한 엔진
slot id를 낼 때만 가능하다.** lap214는 run마다 nation/스폰이 랜덤이고 `replay_seed_observed=false`임을
재현했으므로, S1 "장면 통제"를 장면 일치만으로 푸는 해법은 **카드 PASS에 충분하지 않다**. S1 해법은
slot id 결정성까지 주거나, slot 강등 자체가 상위 tier에서 재결돼야 한다.
middle은 여기서 완화하지 않는다 — lap214 재결의 "PASS 경로를 절대 만들지 않는다"가 우선한다.
이는 판정 술어가 아니라 실험 설계·승인 경계 문제이며 Astra/사용자 소관이다.

## 회귀 / 남은 위험 / 승인 상태

S1 장면 통제(최상위 차단), G1-F3-R1, G1-F3-R2, G1-F2-R1, G1-F2-R2, R6-B 구현 미착수,
WM_CLOSE teardown, G2~G4 제품 증거 0은 모두 미해결이다. 사용자 제품/마일스톤 승인 없음.
후보 Stage B run·원본 재실행·R6-A/R6-C 착수 금지는 그대로다.

## 다음 한 가지

work tier가 **R6-B 런타임 술어 재정의**(`count>=2` 기각 → "선택 상태가 응답했다")를 게임 실행 없이
구현한다. 그 뒤 순서는 G1-F2-R1 → G1-F3-R1 → G1-F3-R2 → G1-F6-R2이며 각 건은 다음 middle이
독립 검수한다. **S1과 G1-F2-R2는 상위 tier(Astra/사용자) 재결 대기이고 그 전에는 어떤 게임 run도
열지 않는다.**

## 최종 파일 해시 (uncommitted, `LOOP_ALLOW_COMMITS=0`)

```
db6660b9af9c9eb25ff04101d91949d2903e679f36a47da7f4dd21c88ea03c41  docs/STATUS.md
(본 기록 자신은 자기참조라 해시를 적지 않는다)
b9f2c106806c1565b42be748bff3b1fea653e7120e0b0cc78208a935e75c22b8  docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md
d8986ab2c22c9b100adb8f12ef2bab020f6bff6a2a395d514cc61ad2983ee30d  loop/ESCALATE_SOL
bac043d1580b0a2a7c88f632859dfadf19bfe3c742562223bd93d6a19f2f8538  docs/history/laps/probes/20260912_lap221_f2_identity_review_probe.py
e3f63556626ab7e88e17c3849c1d25f51b3518d2fe2c773360f787a94891de40  docs/history/laps/probes/20260912_lap221_f2_identity_review_report.json
```

문서 갱신 후 재실행: `make check` 238 passed/Ruff/compileall/mypy 10 files/`CONTEXT_PASS`, `SAFETY_PASS`.
