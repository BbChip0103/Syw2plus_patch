# STATUS pre-compaction snapshot — lap 203

R5-A/R5-C 독립 승인 및 Stage B 페어 run 인가 직후 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `3c990dcc49c0ef16e85186fcdf151a38217d49810ae1404304690f3cd24ad9e2`
- line count: `145`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. 최우선 G1은 원본 800×600 논리 구도/UI를 유지한
1600×1200 정수 2배 출력이다. G2는 전비 5000 숫자 패치만 있고 8인 부하·개체 풀/메모리
확장 증명이 없다. G3 16인과 G4 길찾기·AI는 구현 전이다.

DxWrapper 후보는 반복 fresh runtime에서 1600×1200 client/capture, 800×600 logical, scale 2×2,
선변환 없는 입력, PS9→PS7→PS3와 30초 지속 렌더를 확인했다. WM_CLOSE 후 teardown 미완료는
builtin ddraw 대조로 DxWrapper native 경로에 귀속했다. P6 Lock 계측은 2순위다.

Astra/medium은 약 10회의 work/middle 뒤 큰 분기 lap170에서 한 번만 호출됐다. 방향은 소스 없는
DxWrapper 수리를 추측하지 않고 **G1 실제 표시·입력 합격 증거를 먼저 완성**하는 것이다.

카드2 Stage A A-1~A-16은 원본/후보 공용 입력, production fail-closed, menu 대칭, 즉시 flush,
필수 verdict, off-mode 비개입, 좌표·예산·원인 evidence를 구현했다. Opus/auto가 `make check`와
safety를 독립 재현했다. 25% 잘림 임계값은 첫 실제 run으로 재평가할 설계 가정이다.

**lap199 정정:** `docs/feedback/APPROVALS.md`(mtime 01:56:57, lap198 종료 01:56:11 이후·lap199
시작 01:57:08 이전 = 사람 편집)의 현재 문면은 승인 범위를 "증거가 성립할 때까지 bounded
repair → fresh validation으로 **계속**"으로 적고 **R5류 조이는 변경을 포함**한다. 회차 상한이
아니므로 lap190~198이 8바퀴 이월한 "원본 1회 소진 / R5는 승인 경계" 블로커는 **해소**됐다.
lap190 baseline은 PS3와 unit_select `0→1`까지 PASS했지만 production provenance 예외로 중단돼
drag/minimap과 후보 run은 미실행이다. 금지로 남는 것은 무변경 blind retry와 fresh/exact-once
위반뿐이다. 제품 G1 합격·출시, P6, G2~G4는 여전히 미승인이다.

lap191 Opus는 `49B6D0 ineligible`이 원본 정상 분기임을 과거 메모리맵과 현물로 재확인했다.
실제 하네스 결함은 정상 비활성 production을 BLOCKED로 보존하지 못하고 무관한 후속 입력까지
중단한 것이다. lap192 work가 R1~R4를 구현했고 lap193 Opus/auto가 source 2/2, `make check`
210 passed, safety와 독립 probe 25단언으로 승인했다.

현재 production provenance 예외는 BLOCKED 진단으로 남고 클릭/대기는 실행하지 않으며
unit_select 뒤 drag/minimap까지 계속한다. 후보도 동일 진단 캐시·예외 기록을 쓰고 두 경로 모두
최종 evidence를 flush한다. HQ type은 추측하지 않고 UNKNOWN이다. required_inputs/overall의
fail-closed 불변식은 유지된다. lap195 work가 continue 경로의 실제 production 진단을 top-level
evidence에도 승격했고 후보 finally의 중복 evidence write를 단일 final write로 정리했다.
lap196 Opus/auto가 source 2/2 일치, `make check` 211 passed, safety, 자체 드라이버 probe
30단언으로 N1/N2를 독립 승인하고 R1~R4 회귀 없음·R5 미수행을 확인했다. lap197 work가
`production_provenance_error` 구조화 표식과 fatal/비치명 회귀 테스트를 추가했다. lap198 Opus/auto가
source 2/2 일치, `make check` 213 passed, safety, 자체 드라이버 probe 35단언으로 N3를 독립 승인하고
N1/N2/R1~R4 무회귀·R5 미수행을 확인했다. lap202 work가 R5-C를 구현해 원시 선택 reader의
`OSError`/`struct.error`를 UNKNOWN+provenance로 보존하고 실제 flush 시퀀스 회귀를 추가했다.
**lap203 Opus/auto가 R5-A+R5-C를 독립 승인했다**(probe 63단언, `make check` 221 passed).
사전 게이트를 재집행해 전부 PASS했고 **Stage B 페어 run(원본1+후보1)을 인가**했다.
G1~G4 제품 완료·출시는 여전히 아니다.

모델 라우팅은 Luna/high(work), Claude Opus5/high(middle/judge), Astra/medium(strategy)이다.
Opus 검수는 독립 게이트 실행을 위해 `LOOP_PERMISSION_MODE=auto`를 일회 적용한다. Astra는
큰 분기·반복 교착에서만 약 10 lap당 1회 이하로 쓴다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 후보 2배 표시·지속 렌더 PASS; R5-A+R5-C **middle 독립 승인**·Stage B 인가; 실제 원본↔후보 비교는 아직 0회; 비교기 없음; WM_CLOSE 결함 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

**다음 work(Codex Luna/high 또는 Claude Sonnet5/high): G1 카드2 Stage B 페어 run 정확히 2회.**
① 원본 1회 `g1-baseline --screen 1600x1200x24 --timeout 90`,
② 후보 1회 `g1-presentation-trace --screen 1600x1200x24 --timeout 90 --win32-close-helper
<fresh>/helper/win32_close_helper.exe --dxwrapper-2x --g1-input-sequence`.
각각 **별도의 새 private copy / 새 prefix / 새 빈 display**, exact-once, `prepare`/`check` RC0 확인 후.
판정식은 카드 「Stage B 성공/실패 측정식」: `unit_select`/`drag_select`/`minimap` 세 단계에서
같은 논리 좌표에 대한 `selection_count` 델타와 `camera` 결과가 원본과 일치하는지.
실패해도 **그 자리에서 고치지 말고** 수치·캡처·evidence를 보존해 승격한다. 무변경 retry 금지.
기록에 manifest/evidence/verdict 해시, 단계별 델타, `selected_slot`/`selected_type`,
입력 구간 벽시계, production BLOCKED 사유를 남긴다. 추가 사용자 승인을 기다리지 않는다.

## 지금 막힌 것 (Blockers)

- ~~R5와 Stage B 재실행은 새 사용자 승인 필요~~ → **lap199에서 해소.** 현재 APPROVALS 문면이
  둘 다 덮는다. 남은 미승인은 제품 G1 합격·출시, P6, G2~G4다.
- ~~Stage B 인가는 middle의 R5-A+R5-C 독립 검수까지 보류~~ → **lap203에서 해소.**
  R5-A+R5-C 독립 승인, 사전 게이트 재집행 전부 PASS, 페어 run 인가 완료.
- **R5-D(비블로킹).** baseline/후보 주입 지점 대칭을 저장소 테스트가 아직 단언하지 않는다
  (lap203 probe가 소스 수준으로만 확인). Stage B를 막지 않으며 run과 같은 바퀴에 넣지 않는다.
- **원본↔후보 비교기가 없다.** `tools/`에 Stage B 측정식(델타 일치)을 계산하는 도구가 없어
  지금 run하면 판정이 눈대중이 된다. evidence는 디스크에 남으므로 소급 적용 가능 → run을
  막지는 않는다(R5-B, 비블로킹).
- 원본/제품 EXE·DLL/assets/baseline/golden 변경, 실패 run 재사용, 임의 retry, PASS 완화 금지.
- production 클릭 실행 금지; 정상 비활성은 BLOCKED이며 후속 입력은 계속되어야 한다.
- random seed 미노출로 동일 시작 상태는 미증명; Tier-1/Tier-2로 분리한다.
- minimap은 camera 절대 목적지 비교가 필요하다.
- G1 실제 비교/입력 증거와 G2~G4 제품 증거는 아직 없다.

## 검증 상태

- lap146~169: 후보 2배 표시·입력·지속 렌더 PASS, DxWrapper close 결함 귀속.
- lap170 Astra/medium: G1 합격 증거 우선, P6 주차.
- lap171~189: Stage A A-1~A-16 구현·독립 승인, Fast 209/safety.
- lap190 work: 첫 baseline 1회, PS3/unit_select PASS 후 provenance 예외 BLOCKED, cleanup PASS.
- lap191 middle: 원본 정상 분기 재확증, R1~R4 계약.
- lap192 work: R1~R4 구현, Fast 210/safety, game 0.
- lap193 middle: R1~R4 독립 승인, Fast 210/safety·probe 25단언 PASS, game 0.
- lap195 work: N1 top-level 진단 승격·N2 후보 final write 중복 제거, targeted 6 PASS, Fast 211/safety, game 0.
- lap196 middle: N1/N2 독립 승인, source 2/2, Fast 211/safety·자체 probe 30단언 PASS, game 0, 카드 N3 발행.
- lap197 work: N3 구조화 provenance 표식, targeted 7 PASS, Fast 213/safety, game 0; middle 검수 대기.
- lap198 middle: N3 독립 승인, source 2/2, Fast 213/safety·자체 probe 35단언 PASS, game 0,
  새 카드 없음, 안전 작업 큐 소진 → STOP.
- lap199 middle: 새 APPROVALS 문면 확인으로 STOP 해제(mtime 귀속). 사전 게이트 전부 PASS —
  원본 SHA `b56986e0...a8ac` 핀 일치, `LOOP_DRY_RUN=0` safety `SAFETY_PASS`, Fast **213 passed**,
  `check_setup --require-game` `ok:true`/`original_status:verified`/도구 전부 present,
  free 277G(run≈2.7G), 입력 예산 30.0≤31.5 무변경. R5가 새 오프셋 없이 구현 가능함을 현물
  확인하고 R5-A(블로킹)/R5-B(비블로킹) 계약 발행. 문서만 변경, game 0, Stage B 0.
- lap200 work: R5-A 구현(`_read_g1_selection_evidence`, baseline/후보 대칭 주입), targeted 4 PASS;
  첫 `make check`가 mypy 오류로 FAIL → 수정 후 재시도 없이 계약대로 중단.
- lap201 middle: 게이트 재현 PASS(Fast **216 passed**/mypy Success/`SAFETY_PASS`)로 lap200의
  mypy FAIL 해소 확인. 자체 probe **30단언 PASS**로 새 오프셋 0·절대 type 술어 0·예산 불변·
  양쪽 대칭·비치명 UNKNOWN·`overall` 세탁 없음 확증. 그러나 D1(원시 `OSError` 치명)과
  D2(카드 필수 회귀테스트 1·2·4 누락)로 **R5-A 미승인**, Stage B 인가 이월, R5-C 발행.
  문서만 변경, source/tests 0, game 0, Stage B 0.
- lap202 work: R5-C 구현, runtime targeted **108 passed**, `make check` **221 passed**,
  Ruff/compileall/mypy/`CONTEXT_PASS`, `SAFETY_PASS`; 초회 새 테스트의 비결정적 시간 전체비교
  실패를 원인 기록 후 필드 비교로 수리했다. game 0, Stage B 0, PNG 0.
- lap203 middle: R5-A+R5-C **독립 승인**. 자체 probe **63단언 PASS**(AST로 catch 집합 =
  `_CommandCellSnapshotError`/`OSError`/`struct.error` 확정, `TypeError` 전파, 기존 예외 계약
  무회귀; 주입 reader end-to-end 4단계·디스크 evidence·실패 3종 계속 진행·`required_inputs=False`;
  새 오프셋 0, 술어·예산 불변, 주입 지점 2/2 동일). 사전 게이트 재집행: 원본 SHA 핀 일치,
  `SAFETY_PASS`, `make check` **221 passed**/mypy Success, `check_setup --require-game` `ok:true`/
  `verified`/누락 0, free 276G. **Stage B 페어 run 인가**, 비블로킹 R5-D 발행.
  문서만 변경, source/tests 0, game 0, Stage B 0.
- latest snapshot: `docs/history/laps/20260912_status_lap194_compaction.md`; latest middle:
  `docs/history/laps/20260912_lap203_middle_r5ac_verification.md`.

## 바퀴 기록

- lap2~190 및 이전 STATUS 원문: `docs/history/laps/`.
- lap190: `docs/history/laps/20260912_lap190_work_g1_stageb_baseline_block.md`.
- lap191: `docs/history/laps/20260912_lap191_middle_g1_stageb_root_cause.md`.
- lap192: `docs/history/laps/20260912_lap192_work_g1_stageb_repair.md`.
- lap193: `docs/history/laps/20260912_lap193_middle_stagebr_verification.md`.
- lap195: `docs/history/laps/20260912_lap195_work_g1_stageb_n1_n2.md`.
- lap196: `docs/history/laps/20260912_lap196_middle_n1n2_verification.md`.
- lap197: `docs/history/laps/20260912_lap197_work_g1_n3_error_marker.md`.
- lap198: `docs/history/laps/20260912_lap198_middle_n3_verification.md`.
- lap199: `docs/history/laps/20260912_lap199_middle_approval_scope_r5_contract.md`.
- lap201: `docs/history/laps/20260912_lap201_middle_r5a_verification.md`
  (probe `docs/history/laps/probes/20260912_lap201_r5a_probe.py`).
- lap202: `docs/history/laps/20260912_lap202_work_g1_r5c.md`.
- lap203: `docs/history/laps/20260912_lap203_middle_r5ac_verification.md`
  (probe `docs/history/laps/probes/20260912_lap203_r5c_probe.py`).
- current escalation: `loop/ESCALATE_SOL`; handoff: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`.
