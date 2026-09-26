# 2026-09-12 | lap254 STATUS 압축 전 원문 보존

압축 직전 `docs/STATUS.md` 원문이다. sha256=`ed3fe77de435e80935922731c6b34f8c9bcc6f7032a6f1c459841a98cc81eea5`, 줄 수=126.
lap254 middle이 130줄 게이트를 지키려고 R1~R14 승인 목록을 요약하기 전에 전문을 여기 보존했다.
승인·반려·미결 근거는 삭제하지 않았고, 각 항목의 전체 근거는 `docs/history/laps/`의 해당 lap 기록에 있다.

```markdown
# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. G1은 원본 800×600 논리 구도/UI를 유지한 1600×1200
정수 2배 출력, G2는 8인 전비 5000과 실제 개체 풀/메모리 확장, G3은 최대 16인, G4는
길찾기·자유대전 AI 개선이다.

DxWrapper 후보는 fresh runtime에서 1600×1200 client/capture, 800×600 logical, 2×2 scale,
선변환 없는 입력, PS9→PS7→PS3와 30초 지속 렌더를 확인했다. WM_CLOSE teardown 결함은
builtin ddraw 대조로 DxWrapper native 경로에 귀속했고 P6 Lock 계측은 주차했다.

사용자는 2026-09-12 01:03 KST “승인. 루프 계속 돌아”로 Stage B evidence가 성립할 때까지
bounded repair→fresh validation을 승인했다. blind retry, run 재사용, 보호 자산 변경은 금지다.

Stage A A-1~A-16과 R1~R5-C/N1~N3, comparator F1/F4/F5, 후보 producer F6은 구현 후
Opus 독립 승인을 받았다. lap204 fresh 원본 drag는 count 1→1이지만 slot/type
1199/70→1198/21로 실제 선택 효과가 있었다. 이에 `FAIL_NO_EFFECT`, 절대 slot id, `count>=2`
규칙을 기각했다. lap214 Astra/medium 이후 Opus가 판정 계약을 재결했고, F3는 `after.last`, F2는
`(owner,type,장면 상대 world offset)` parity를 사용하도록 수리·독립 승인했다.

R6-B는 선택 count 또는 identity의 비퇴행 변화를 응답으로 삼는다. 후속 수리 상태:
- R1: 손상 slot/type 관측 fail-close — lap226 Opus 범위 승인.
- R3: 음수 count fail-close — lap228 Opus 13,689-case 범위 승인.
- R4: 최종 관측 상태 갱신+손상 provenance 보존 — lap230 Opus 범위 승인.
- R6: 읽기 실패 0관측/tail을 UNKNOWN으로 닫음 — lap232 Opus 18-case 범위 승인.
- R5: 실제 reader 손상 회귀 — lap234 Opus 31-case 범위 승인.
- R7: review probe 기존 보고서 덮어쓰기 방지 — lap236 Opus 범위 승인.
- R8: 읽기 오류율 25% 초과를 `UNKNOWN_STATE_READ_COVERAGE`로 닫음 — lap238 Opus 16-case
  전수 행렬 + 5개 변이 범위 승인. lap237 STATUS 길이 게이트 실패도 해소를 확인했다.
- R9: `_g1_run_input_sequence`의 직접 selection reader 실패를 단계/지점/provenance와 함께
  `UNKNOWN_STATE_READ_FAILURE`로 flush — lap239 work 구현, lap240 middle이 독립 하네스로
  call-site 6개 전수 + raising 15-case + production 3-case + 변이 5/5 검출로 범위 승인.
- R10: review probe 쓰기 불가 부모를 본문 실행 전에 `exit 2`로 분류 — lap241 work 구현,
  lap242 middle 검수 **FAIL**, lap243 work가 R16 `OSError` fail-close와 R17 조기 거부 회귀를
  수리했고 lap244 middle이 독립 하네스로 재검수해 **범위 승인**했다.

- R11: review probe 배타 생성(open("x")) 단독 가드의 dangling symlink 회귀 — lap245 work 구현,
  lap246 middle이 깊이를 맞춘 미러에서 변이가 R11 **하나만** 죽이는 것을 실측해 **범위 승인**했다.
  단, lap245가 제출한 비공허성 증거는 **무효**다(아래 lap246). 제품 G1 증거는 여전히 없다.

- R12: 읽기 오류/커버리지 부족이 이미 관측한 selection `CORRUPTED`를 `UNAVAILABLE`로 덮지 않게
  보존 — lap247 work 구현, lap248 middle이 81-case 전수 + M0 대조군 + 변이 3종으로 **범위 승인**.
- R13: PASS 입력 stage의 poll/read-error coverage를 stage record와 input verdict에 노출 — lap249
  work 구현, lap250 middle이 15-case 성공 행렬 + 16-case timeout 대조 + M0 대조군 + 변이 4종
  (각 1건 사살, 범위 밖 0건)으로 **범위 승인**했다.
- R14: production 직접 selection read 실패가 초기 미관측 상태와 구별되도록 nested selection에
  `status=UNAVAILABLE`, `count=null`, `read_failure=true`를 기록 — lap251 work 구현, lap252
  middle이 독립 하네스 9-case 행렬 + M0 대조군 + 변이 5종으로 **범위 승인**. production은 계속
  BLOCKED이며 클릭/대기·후속 입력은 불변이다.
- R15: 직접 selection reader 실패가 run/stage budget 소진보다 우선하는 `UNKNOWN_STATE_READ_FAILURE`와
  `finished_elapsed`/`remaining_budget_after` provenance를 기록 — lap253 work 구현, middle 독립 검수 대기.

최상위 증거 차단 S1은 원본↔원본도 nation/player spawn이 달라 scene mismatch가 나는
비결정성이다. F2-R2 때문에 장면 통제는 slot 대응 결정성도 함께 풀어야 한다. 상위 재결 전에는
fresh Stage B를 실행하지 않고 게임 없는 수리만 한 바퀴 한 건씩 진행한다.

모델 라우팅: Luna/high(work), Claude Opus5/high(middle), Astra/medium(strategy). Astra는 큰
분기·교착에서만 약 10 lap당 1회 이하이며 마지막 호출은 runtime lap214였다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 표시·논리 좌표 증거 있음; R15 독립 검수, R2/S1, fresh pair, WM_CLOSE 필요 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

새 middle tier(Opus5/high)가 게임 없이 **R15**를 독립 검수한다 — 직접 reader 실패가 run/stage budget
소진보다 우선 분류되고 timing provenance가 남는지 확인한다. 이후 큐는 R19 → R20 → R21 → R22 →
R23 → R24 → F2-R1 → F3-R1 → F3-R2 → F6-R2다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- **S1/F2-R2:** random seed·scene·slot 대응 결정성이 없다. 상위 재결 전 Stage B 양쪽 run,
  원본 재실행, R6-A/R6-C 금지.
- **R6-B-R2:** count 1→0 선택 상실을 응답으로 볼지는 Astra/사용자 재결 전 수정 금지.
- offline 큐: **R19**(R17 회귀가 함수명 `drive_wait`
  하나에만 걸려 있어 개명 시 조기-거부 삭제를 놓친다 — lap244 실측), **R20**(저장소 밖 미러
  변이 하네스에 M0 대조군이 없어 재배치 실패를 "검출"로 오독 — lap246 실측), **R21**(probe 출력이
  직렬화 전에 `open("x")`로 파일을 만들어 쓰기 실패가 절단 증거를 남기고 R7이 재시도를 막는다 —
  lap248 실측), **R22**(R13의 세 성질이 단일 테스트 하나에만 걸려 있어 그 테스트 삭제 시 동시에
  미검증 — lap250 실측), **R23**(`read_coverage` 소비자가 runtime_env 밖에 0개라 증거 게이트가
  아직 이 필드를 읽지 않음 — lap250 실측), **R24**(R14의 `read_failure` 소비자도 runtime_env 밖에
  0개이고 record 최상위 `selection_count`는 실패/미관측 모두 null이라 표식을 읽지 않는 소비자에게는
  여전히 구별 불가 — lap252 실측), F2-R1/F3-R1/F3-R2/F6-R2.
- 후보 WM_CLOSE teardown 결함과 실제 후보 scene/input evidence는 미해결이다.
- G2~G4는 제품 증거가 없다.

## 검증 상태

- lap146~236: Stage A/R1~R8과 F2/F3 수리·독립 승인, Fast 255/safety PASS.
- lap237~238: R8 구현·독립 검수, 16-case 불일치 0·변이 5/5, Fast 257/safety PASS.
- lap239~244: R9/R10 구현·수리·독립 승인. R10 middle의 lap242 FAIL과 하네스 결함은
  lap243/244에서 보정·재검수했으며 Fast 268/safety PASS.
- lap245~246: R11 회귀 범위 승인. lap245의 얕은 미러 증거는 무효이고, lap246의 깊이 일치
  M0 대조군에서 변이 1건만 검출됨을 확인했다. Fast 269/safety PASS.
- lap247~248: R12 구현·독립 범위 승인. 81-case 불일치 0, M0 136 passed, 변이 3종 대조,
  Fast 271/safety PASS. R21 하네스 규약 결함을 큐에 올렸다.
- lap249: R13 work — PASS stage의 `read_coverage`를 stage record와 `input_checks` verdict에
  투영하고, transient read error 성공 반환의 기존 비대칭을 유지. 신규 회귀 1건 포함 21 targeted,
  `make check` 272 passed, `CONTEXT_PASS`, safety PASS, 게임/Wine/Xvfb/PNG 0회(lap250이 독립 검수함).
- lap250: R13 독립 범위 승인. 성공 15-case/timeout 16-case 불일치 0, M0 137 passed, 변이 4종이
  각 1건만 사살(범위 밖 0건), Fast 272/safety PASS. R22/R23을 큐에 올렸다.
- lap251: R14 work — production direct selection read failure가 nested before/after selection에
  `read_failure=true`와 `UNAVAILABLE` 상태를 남기는 회귀 2건 추가. targeted 4 passed, `make check`
  274 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, safety PASS, 게임/Wine/Xvfb/PNG 0회.
- lap252: R14 독립 범위 승인. C0 4 passed/135 deselected, C1 9-case 행렬 불일치 0(production
  지점에서만 표식, 나머지 8 case 표식 0), M0 미러 139 = 실제 139, 변이 5종이 각 1~2건 사살·범위 밖
  0건. Fast 274/safety PASS, 게임/Wine/Xvfb/PNG 0회. R24를 큐에 올렸다.
- lap253: R15 work — 직접 reader 실패의 `UNKNOWN_STATE_READ_FAILURE` 우선순위와
  `finished_elapsed`/`remaining_budget_after`/budget exhaustion provenance를 추가했다. 새 deadline
  회귀 포함 targeted 11 passed, `make check` 275 passed, Ruff/compileall/mypy 10 files,
  `CONTEXT_PASS`, safety PASS; 게임/Wine/Xvfb/PNG 0회. middle 독립 검수 전이다.
- latest work: `docs/history/laps/20260912_lap253_work_r15.md`.
- latest middle: `docs/history/laps/20260912_lap252_middle_r14_review.md`; probe/report
  `...probes/20260912_lap252_r14_review_probe.py`, `..._report.json`.
- pre-compaction 원문: `docs/history/laps/20260912_status_lap237_compaction.md`.

## 바퀴 기록

- lap2~250과 STATUS 원문: `docs/history/laps/`; probe는 `docs/history/laps/probes/`.
- current escalation: `loop/ESCALATE_SOL`; handoff: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md` (lap252 R14 middle 승인 및 R15 지시; lap253 work 기록, middle 독립 검수 대기).
```
