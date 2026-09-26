# STATUS pre-compaction snapshot — lap 237

R6-B-R8 work 후 safety line-limit 위반 시점의 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `0801908b982340289112436cabab0e5de6978d2da410120dd08085c7c7e7a3c0`
- line count: `188`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. G1은 원본 800×600 논리 구도/UI를 유지한 1600×1200
정수 2배 출력, G2는 8인 전비 5000과 실제 개체 풀/메모리 확장, G3은 최대 16인, G4는
길찾기·자유대전 AI 개선이다.

DxWrapper 후보는 fresh runtime에서 1600×1200 client/capture, 800×600 logical, 2×2 scale,
선변환 없는 입력, PS9→PS7→PS3와 30초 지속 렌더를 확인했다. WM_CLOSE 후 teardown 미완료는
builtin ddraw 대조로 DxWrapper native 경로에 귀속했다. P6 Lock 계측은 주차 상태다.

사용자는 2026-09-12 01:03 KST “승인. 루프 계속 돌아”로 Stage B evidence가 성립할 때까지
bounded repair→fresh validation을 승인했다. blind retry, 같은 run 재사용, 보호 자산 변경은 금지다.

Stage A A-1~A-16과 R1~R5-C/N1~N3은 공용 입력, production fail-closed, 단일 최종 evidence,
선택 slot/type 관측, 비교기 입력 손상 fail-closed를 구현·독립 승인했다. F6 후보 untagged
selector recorder는 lap212 수리, lap213 Opus 승인, lap216 producer guard, lap217 Opus 승인으로 닫았다.

lap204 fresh 원본은 unit_select count 0→1, slot/type 1199/70 뒤 drag count 1→1이었지만
identity는 1199/70→1198/21로 실제 변경됐다. lap205는 `FAIL_NO_EFFECT`와 `count>=2`를 판정식
결함으로 확정했고 후보는 실행하지 않았다.

lap214 Astra/medium은 F2/F3/R6-B 근거 충돌을 Opus 재결로 승격했다. Opus는 절대 slot id와
`count>=2`, 결과 문자열만으로 `FAIL_NO_EFFECT`를 상속하는 규칙을 기각했다. F3는 `after.last`
관측과 분쟁 상태를 사용하도록 lap218 수리·lap219 Opus 승인했다. F2는 `(owner,type,장면 상대
world offset)` 비교로 lap220~221 수리·lap222 Opus 승인했다. lap223은 R6-B를 selection
count/identity 변화 술어로 수리했고, lap224 middle은 손상 관측이 응답으로 세탁되는 조건부 반려를
남겼다. lap225 work는 R6-B-R1을 수리해 양수 count의 slot/type 손상을 fail-close하고, 손상 timeout
provenance를 보존하도록 했다. lap227 work는 R6-B-R3을 수리해 음수 count도 손상으로 fail-close했으며,
count 0 의미는 유지했다.

lap229 work는 R6-B-R4를 수리해 매 selection poll의 최종 온전성으로
`selection_observation.status`를 갱신하고, 손상 poll의 횟수와 첫/마지막 provenance를 보존한다.
lap230 middle이 게임 없이 독립 검수해 **범위 승인**했다(25케이스 23 AGREES/2 DEFECT). 최종성은
양방향이고(온전→손상도 되돌아감), 손상 이력은 8개 키로 유계이며, count 1→0·음수·비정수 semantics와
PASS 조건은 전혀 완화되지 않았다. DEFECT 2건은 R4 회귀가 아닌 선재 결함으로 R6-B-R6/R7에 등록했다.

lap231 work는 G1-R6-B-R6을 수리했다. `_wait_state`는 읽기 성공 poll과 전체 시도를 분리하고,
`read_error_count` 및 첫/마지막 읽기 오류 provenance를 보존한다. 관측이 전혀 없거나 마지막 성공
관측 뒤 읽기 실패로 창 끝이 닫히면 `UNKNOWN_STATE_READ_FAILURE`로 fail-close하며, 선택 진단의
stale `SOUND`는 `UNAVAILABLE`로 바뀐다. 기존 예산·잘림·손상·PASS semantics는 유지했다.
lap232 middle이 게임 없이 독립 검수해 **범위 승인**했다(자체 probe 18케이스 18 AGREES/0 DEFECT).
C5a/C5b가 닫혔고, 분류 우선순위 상위 3개는 모두 UNKNOWN이며, poll 시도 0회도 hard FAIL이 아니고,
R6-B-R2/R3/R4 semantics와 PASS 경로는 불변이다. 비교기도 읽기 실패 stage를 stale `last`가
변화처럼 보여도 `UNKNOWN_DISPUTED_ORACLE`로 닫는다. 비차단 후속 R6-B-R8을 새로 등록했다.

lap233 work는 R6-B-R5 회귀를 보강했다. 저장소 테스트가 실제
`_read_g1_selection_evidence` reader로 C4(OSError), C5(비활성 slot), C7(손상 기준선 회복),
D1(음수 count) 관측을 만들고, 모두 `_g1_selection_responded=False`와
`selection_observation.status=CORRUPTED`로 닫히는 것을 고정한다. 구현·게임·PNG는 변경하지 않았다.
lap234 middle이 게임 없이 독립 검수해 **범위 승인**했다(자체 probe 31케이스 31 AGREES/0 DEFECT).
도달성 12종이 실제 reader에서 나오고, 가드를 약화한 변이 3종에서 lap233 테스트가 실제로 실패하므로
회귀는 비공허하다. count 0·count 1→0·식별자 변화 PASS 경로는 완화되지 않았다. 비차단 후속
R6-B-R9를 신규 등록했다.

lap235 work가 R6-B-R7을 수리했다. lap228 review probe는 `--output` 경로를 받고 기존 파일을
거부하며, 실제 파일 생성도 `open("x")`로 원자적 배타 생성한다.
lap236 middle이 게임 없이 독립 검수해 **범위 승인**했다(자체 probe 13케이스 11 AGREES/2 DEFECT,
변이 5케이스). 기존 파일·0바이트 파일·디렉터리·심볼릭 링크·dangling 링크·기본 경로·import 실행
7종이 모두 exit 2로 fail-close하고 바이트가 보존된다. dangling 링크와 import 실행은 사전 검사가
아니라 배타 생성 분기로만 막히므로 경쟁 보호의 도달성이 실증됐다. 새 경로 보고서는 보존된 lap230
재실행본과 `source_sha256`만 다르고 판정은 전부 동일하다. 가드 2개 동시 제거와 `--output` 무시
변이에서 lap235 테스트가 실제로 실패해 회귀는 비공허하다. DEFECT 2건은 보존 결함이 아니라 쓰기
불가 경로의 미분류 실패이며 신규 비차단 R6-B-R10/R11로 등록했다.

lap237 work는 R6-B-R8을 수리했다. `_wait_state`는 성공 poll/전체 시도 대비 읽기 오류 비율을
증거로 남기고, 오류 비율이 25%를 초과하면 마지막 성공 poll이 있어도
`UNKNOWN_STATE_READ_COVERAGE`로 fail-close한다. 전체 읽기 실패·읽기 tail은 기존
`UNKNOWN_STATE_READ_FAILURE` 우선순위를 유지하고, 정확히 임계인 25%와 오류 없는 무반응은
기존 `FAIL_NO_EFFECT`로 남겼다. 게임·PNG·EXE/DLL/assets/baseline/golden 변경은 없다.

lap224 middle은 R6-B를 **조건부 반려**(상세 `20260912_lap224_middle_r6b_review.md`), lap225가
R1을 수리, lap226 middle이 **범위 승인**하며 R6-B-R3~R5를 등록했다. R6-B 전체는 미승인이다.

lap227 work는 R6-B-R3을 구현·회귀 검증했고, lap228 middle이 게임 없이 독립 검수해 **범위 승인**했다.
음수 count는 실제 리더가 예외 없이 낼 수 있는 관측(도달성 확인)이고, 인코딩 5종·양측 조합 7/7이
fail-close된다. 13,689 케이스 차분에서 동작 변화 2,052건은 전부 "음수 포함 + True→False"뿐이라
수술성이 확인됐고, count 1→0(R6-B-R2)과 비정수 거부는 불변이다. R6-B 전체와 제품 G1은 미승인이다.

새 최상위 증거 차단 S1은 원본↔원본도 nation/player spawn이 달라 scene mismatch가 나는
비결정성이다. F2-R2 때문에 장면 통제는 slot 대응 결정성도 함께 풀어야 한다. 상위 재결 전에는
fresh Stage B를 실행하지 않고, 게임 없는 회귀 수리만 한 바퀴 한 건씩 진행한다.

모델 라우팅: Luna/high(work), Claude Opus5/high(middle), Astra/medium(strategy). Astra는 큰
분기·교착에서만 약 10 lap당 1회 이하이며 마지막 호출은 runtime lap214였다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 표시·논리 좌표 증거 있음; R6-B-R9, R2/S1 결정성, fresh pair, WM_CLOSE 필요 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

lap237이 R6-B-R8을 수리·회귀 검증했다. 다음 새 middle tier(Sol/Opus5/high)가 R6-B-R8을
독립 검수한 뒤, 새 work tier가 **R6-B-R9**(selection reader 직접 읽기 실패의 단계별
진단성)를 한 건으로 다룬다. 그 뒤 R6-B-R10 → R6-B-R11 → F2-R1 → F3-R1 → F3-R2 →
F6-R2 순으로 한 바퀴 한 건이다.
R6-B-R2(count 1→0의 의미)는 Astra/사용자 재결 전 아무도 건드리지 않는다.
S1/F2-R2 재결 전 게임 실행과 Stage B 원본/후보 run은 계속 금지다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- **S1/F2-R2:** random seed가 노출되지 않아 scene과 slot 대응 결정성을 보장하지 못한다.
  상위 재결 전 후보 Stage B run·원본 재실행·R6-A/R6-C는 금지다.
- **R6-B-R8**(lap232 신규, lap237 수리): 읽기 오류가 관측 창의 25%를 초과하면
  `UNKNOWN_STATE_READ_COVERAGE`로 닫도록 임계와 비공허 회귀를 추가했다. 다음 middle의
  독립 검수 전에는 범위 승인으로 승격하지 않는다.
- 비차단 **R6-B-R9**(lap234 신규): `_read_selection`이 reader의 try 앞에 있어 selection
  count/first-slot 읽기 실패는 예외로 reader를 빠져나간다. `_wait_state`와 `g1_baseline`이
  fail-close하므로 정확성 구멍은 아니지만, `_g1_run_input_sequence`가 `_wait_state` 밖에서
  직접 읽는 5곳은 단계 분류 없이 run 전체 error로만 남아 진단성이 떨어진다.
- R6-B-R7은 lap235 수리·lap236 범위 승인으로 닫혔다. 기존 lap228 JSON은 이미 lap230 재실행으로
  소실됐고 고지·재실행본만 보존한다. 기본 경로 파일의 `source_sha256`은 lap229 시점이라
  재실행본과 다르다는 고지가 계속 필요하다.
- 비차단 **R6-B-R10**(lap236 신규): `--output`은 존재만 검사하고 쓰기 가능성은 검사하지 않는다.
  부모 디렉터리가 없거나 쓰기 불가면 exit 2 거부가 아니라 probe 전체 계산 뒤 미분류 traceback과
  exit 1로 끝난다. 증거는 보존되지만 실패 분류·비용이 나쁘다.
- 비차단 **R6-B-R11**(lap236 신규): `tests/test_review_probe_output.py`는 사전 존재 검사와
  배타 생성 중 **하나만** 제거한 변이를 잡지 못한다. 경쟁 보호 분기에 독립 회귀가 없다.
- **R6-B-R2(상위 재결):** count 1→0 선택 상실을 응답으로 셀지 STATUS 기준과 lap223 계약이 충돌한다.
  Astra/사용자 재결 전까지 work tier는 손대지 않는다.
- 비차단 offline 큐: F2-R1(폴백 절대 slot), F3-R1(PASS+timeout/s손상 last),
  F3-R2(hard FAIL을 disputed로 흡수), F6-R2(flush 제거 변이 미검출).
- 후보 WM_CLOSE teardown 결함은 출시 전 미해결이며 실제 후보 scene/input evidence도 아직 없다.
- G2~G4는 제품 증거가 없다.

## 검증 상태

- lap146~170: 2배 표시·입력·지속 렌더 확인, close 결함 귀속, G1 증거 우선 결정.
- lap171~213: Stage A/R1~R5/F1~F6 구현·독립 승인, Fast 232/safety PASS.
- lap214~219: Astra 승격, Opus 재결, F6 guard와 F3 수리·독립 승인, Fast 236/safety PASS.
- lap220~222: F2 수리·mypy 복구·Opus 12-case+400 sweep 승인, Fast 238/safety PASS.
- lap223: R6-B work; targeted 6, Fast 239, Ruff/compileall/mypy/CONTEXT PASS, 게임 0회.
  종료 safety만 STATUS 184줄로 FAIL하여 원문 snapshot 후 압축했다.
- lap224: middle R6-B 독립 검수 = 조건부 반려. probe 7케이스 중 3 AGREES / 4 DEFECT,
  targeted 6, Fast 239, Ruff/compileall/mypy 10/CONTEXT_PASS, SAFETY_PASS, 게임 0회, 코드 변경 0.
- lap225~228: R6-B-R1/R3 work 수리와 middle 범위 승인. targeted 13~18, `make check` 243→245
  passed, Ruff/compileall/mypy 10/CONTEXT_PASS, SAFETY_PASS, 원본 SHA 일치, 게임 0회, PNG 0장.
  lap226이 후속 3건(R6-B-R3~R5), lap228이 13,689케이스 수술성 PASS를 남겼다. 상세는 laps/.
- lap229: work R6-B-R4; targeted 10, `make check` 247 passed, 전체 `pytest -q` 247 passed,
  Ruff/compileall/mypy 10/CONTEXT_PASS, SAFETY_PASS, W1~W3 probe wait defects 0, 게임 0회,
  PNG 0장, EXE/DLL/assets/baseline/golden 변경 0.
- lap230: middle R6-B-R4 독립 검수 = 범위 승인 + 후속 2건(R6-B-R6/R7). 자체 probe 25케이스
  23 AGREES/2 DEFECT, lap228 probe 재실행 wait/reachability/preservation defects 0,
  targeted 20, `make check` 247 passed, Ruff/compileall/mypy 10/CONTEXT_PASS, SAFETY_PASS,
  원본 EXE SHA 일치, 게임 0회, PNG 0장, 제품 코드 변경 0.
- lap231: work R6-B-R6; C5a/C5b 회귀 포함 targeted 34 passed, 전체 pytest 249 passed,
  `make check` 249 passed + Ruff/compileall/mypy 10/CONTEXT_PASS, `SAFETY_PASS`, lap230 probe
  25 AGREES/0 DEFECT, 게임 0회, PNG 0장, EXE/DLL/assets/baseline/golden 변경 0.
- lap232: middle R6-B-R6 독립 검수 = 범위 승인 + 후속 1건(R6-B-R8). 자체 probe 18케이스
  18 AGREES/0 DEFECT, lap230 probe 재실행 25 AGREES/0 DEFECT, 전체 pytest 249 passed,
  `make check` 249 passed + Ruff/compileall/mypy 10/CONTEXT_PASS, `SAFETY_PASS`, 원본 EXE SHA
  핀 불변, 게임 0회, PNG 0장, 제품 코드 변경 0. lap231 ESCALATE_SOL의 테스트 파일 sha256은
  2자 누락된 오기이며 실제 파일은 lap231 설명과 일치한다.
- lap233: work R6-B-R5 reader 기반 손상 회귀 추가, targeted 18 passed, 전체 `make check` 253
  passed, Ruff/compileall/mypy 10/CONTEXT_PASS, `SAFETY_PASS`, 원본 EXE SHA 핀 불변,
  `tools/runtime_env.py` 불변, 게임 0회, PNG 0장, EXE/DLL/assets/baseline/golden 변경 0.
- lap234: middle R6-B-R5 독립 검수 = 범위 승인 + 후속 1건(R6-B-R9). 자체 probe 31케이스
  31 AGREES/0 DEFECT(도달성 12, fail-close 15, 변이 4), lap232 probe 재실행 18 AGREES/0 DEFECT,
  targeted 18 passed, `make check` 253 passed + Ruff/compileall/mypy 10/CONTEXT_PASS,
  `SAFETY_PASS`, 원본 EXE SHA 핀 4파일 불변, `tools/runtime_env.py`/`tests/test_runtime_env.py`
  sha256이 lap233 기록과 일치, 게임 0회, PNG 0장, 제품/도구 코드 변경 0.
- lap235: work R6-B-R7 수리; 기존 보고서 sentinel 보존/exit 2 및 새 `--output` 생성 targeted
  2 passed, `make check` 255 passed, Ruff/compileall/mypy 10/CONTEXT_PASS, `SAFETY_PASS`,
  원본 EXE SHA pin과 `tools/runtime_env.py` 불변, 게임 0회, PNG 0장.
- lap236: middle R6-B-R7 독립 검수 = 범위 승인 + 후속 2건(R6-B-R10/R11). 자체 probe 13케이스
  11 AGREES/2 DEFECT(보존 7/7, 생성·충실도 4/4, 진단성 0/2), 변이 5케이스에서 M0 pass·
  M3/M4 실제 실패·M1/M2 미검출, `make check` 255 passed + Ruff/compileall/mypy 10/CONTEXT_PASS,
  `SAFETY_PASS`, 원본 EXE SHA pin 4파일 불변, lap235가 적은 probe/테스트/`runtime_env.py`
  sha256 3건이 실제 파일과 일치, 보존된 lap228/lap230 보고서 sha256 실행 전후 불변,
  게임 0회, PNG 0장, 제품/도구 코드 변경 0.
- lap237: work R6-B-R8 수리; targeted 13 passed, `make check` 257 passed +
  Ruff/compileall/mypy 10/`CONTEXT_PASS`, `SAFETY_PASS`, 원본 EXE SHA pin 4파일 불변,
  게임 0회, PNG 0장, EXE/DLL/assets/baseline/golden 변경 0. 오류 3/4는
  `UNKNOWN_STATE_READ_COVERAGE`, 경계 오류 1/4는 `FAIL_NO_EFFECT`로 확인했다.
- latest work: `docs/history/laps/20260912_lap237_work_r6b_r8.md`;
  latest middle: `docs/history/laps/20260912_lap236_middle_r6b_r7_review.md`.
- pre-compaction 원문: `docs/history/laps/20260912_status_lap223_compaction.md`.

## 바퀴 기록

- lap2~223 및 STATUS 원문: `docs/history/laps/`; probe 원본은 `docs/history/laps/probes/`.
- current escalation: `loop/ESCALATE_SOL`; handoff: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`.
