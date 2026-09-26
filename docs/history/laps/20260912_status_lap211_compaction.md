# STATUS pre-compaction snapshot — lap 211

F5 승인과 F6 생산자 비대칭 확정 직후 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `92a717ee6d06b0def8efb92310ae4eedd3c4a3318983ac4767991306fcda1bff`
- line count: `160`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. 최우선 G1은 원본 800×600 논리 구도/UI를 유지한
1600×1200 정수 2배 출력이다. G2는 전비 5000 숫자 패치만 있고 8인 부하·개체 풀/메모리
확장 증명이 없다. G3 16인과 G4 길찾기·AI는 구현 전이다.

DxWrapper 후보는 반복 fresh runtime에서 1600×1200 client/capture, 800×600 logical, scale 2×2,
선변환 없는 입력, PS9→PS7→PS3와 30초 지속 렌더를 확인했다. WM_CLOSE 후 teardown 미완료는
builtin ddraw 대조로 DxWrapper native 경로에 귀속했다. P6 Lock 계측은 2순위다.

Astra/medium은 약 10회의 work/middle 뒤 큰 분기 lap170에서 한 번만 호출됐다. 현재 방향은
G1 실제 표시·입력 합격 증거를 먼저 완성하는 것이다.

Stage A A-1~A-16과 Stage B-R/N1~N3은 공용 입력 시퀀스, production fail-closed, menu 대칭,
즉시/최종 flush, verdict, 좌표·예산·원인·진단 evidence를 구현했고 Opus/auto가 독립 승인했다.

사용자는 2026-09-12 01:03 KST “승인. 루프 계속 돌아”로 Stage B 완료까지 bounded repair→fresh
validation을 승인했다. blind retry는 금지하고 각 수리 뒤 exact-once/fresh 규칙을 지킨다.

lap190 첫 baseline은 PS3와 unit_select `0→1` 뒤 정상 production 비활성 분기를 예외로 중단했다.
R1~R4 수리 후 production은 BLOCKED로 보존되고 클릭/대기는 미실행이며 drag/minimap은 계속한다.
진단은 baseline/후보 양쪽에 대칭 보존되고 HQ type은 추측 없이 UNKNOWN이다.

R5-A/R5-C는 기존 검증 주소로 selected slot/type을 evidence에 기록한다. 절대 type 술어는 없고
원본↔후보 parity로만 판정한다. 읽기 실패는 `_CommandCellSnapshotError`/`OSError`/`struct.error`
세 종류만 UNKNOWN 비치명 처리하며 `TypeError` 등은 전파한다. wait 술어, 예산, overall 불변식은
그대로다.

lap203은 R5-A/R5-C를 독립 승인하고 Stage B fresh pair run을 인가했다. lap204 work의 새 원본 run은
`drag_select`에서 count 1→2를 못 봐 중단됐다. lap205 middle이 그 run을 독립 검수(해시 5종 재현)해
**원인을 판정식 결함으로 확정**했다: 선택 identity가 1199/type70→1198/type21로 **실제로 바뀌었고**,
`FAIL_NO_EFFECT`는 분류기가 모든 술어 미충족에 찍는 오라벨이다. 캡처상 본영과 이동 유닛 **둘 다
드래그 사각형 내부**라 장면 의존성 가설은 기각됐다. `count>=2`는 역어셈블/관측 근거가 없고
저장소 테스트는 가짜 `wait`로 count=2를 주입해 실거동을 검증한 적이 없다.

별건 상위 발견: 카드 PASS는 원본↔후보 **델타 일치**인데 비교기가 없다(R5-B 미구현). 현 하네스는
단일 원본 run은 과잉 구속하고 페어는 미구속이라, 두 run이 완주해도 카드 PASS를 산출할 수 없다.

lap206 work가 R5-B 오프라인 비교기와 6개 fixture 회귀를 추가했다. 비교기는 장면 동등성(0·1번
owner type 집합/상대 world 오프셋/world_bounds)을 먼저 검사하고, 통과할 때만 세 입력 단계의
delta·identity·camera를 비교한다. 실제 보존 run pair에 적용한 결과는 후보 scene/input 증거 부재로
INCONCLUSIVE이며, production은 NOT_COMPARED로 남았다. 게임 재실행과 기존 evidence 승격은 없었다.

lap207 middle이 R5-B를 독립 검수해 **조건부 반려**했다. 재현은 맞다(해시 3종 일치, 보존 pair
INCONCLUSIVE/NOT_COMPARED 재현, scene 키에 slot id 미사용 확인, `content`는 논리 800×600 좌표라
2× 후보가 자동 FAIL되지 않음). 그러나 실행으로 구성한 PASS 세탁 경로가 있다.
F1(치명): 후보 `minimap.before.camera`를 삭제하면 `camera_changed_candidate`가 `None != [x,y]`로
참이 되어 **overall PASS**가 나온다. F2: `selected_identity`가 절대 slot id를 원본↔후보 동일성으로
요구해 type·delta가 같아도 FAIL(장면 키에서는 같은 slot id를 배제해 놓고 판정에서는 요구).
F3: `result != PASS`를 최초 검사해 FAIL을 내므로, lap205가 오라벨로 확정한 `FAIL_NO_EFFECT`가
카드 FAIL로 상속되고, 실제 관측이 담긴 `after.last`는 `_selection`이 읽지 못한다.
F4: `input_errors`(중복 tag 등)가 status에 반영되지 않아 PASS가 가능하다.

lap208 work가 승인 범위의 F1/F4 bounded repair를 적용했다. 양쪽 minimap의 before/after camera가
모두 정수쌍으로 관측되지 않으면 해당 stage를 `INCONCLUSIVE`로 닫고, 중복·비객체 input 오류가
있으면 모든 stage가 PASS여도 전체를 `INCONCLUSIVE`로 닫는다. F2/F3, runtime/evidence, 게임 실행은
건드리지 않았다. 회귀 8개와 전체 Fast 229개가 통과했고 Ruff/compileall/mypy 10 files 및 safety도
통과했다. 게임 0회, PNG 0장이다.

lap209 middle이 lap208 수리를 독립 검수해 **F1/F4를 승인**했다. 저장소 테스트를 import하지 않은 새
fixture 21 probe에서 minimap camera 누락/None/float/bool/문자열/3원소/dict 및 원본측 누락 9종이 모두
`INCONCLUSIVE`였고, 중복 tag·비객체 엔트리·비list `inputs` 4종은 모두 overall `PASS`를 막았다. 동시에
평행이동된 정상 pair는 여전히 `PASS`, camera 목적지 불일치와 후보 camera 부동은 여전히 `FAIL`이라
과잉 차단이 아니다. 보존 pair는 `INCONCLUSIVE`/`NOT_COMPARED`/exit 2로 불변이며 증거 승격은 없다.
새 경미 결함 **F5**를 찾았다: `_inputs_by_tag`가 `tag`가 문자열이 아닌 input 레코드를 오류로 남기지
않고 버려서, 손상된 추가 레코드가 있어도 overall `PASS`가 가능하다(probe P4a/P4b). F4와 같은 부류의
fail-open이고 실패를 닫는 엄격화라 기존 bounded repair 범위 안이다.

lap210 work가 F5 bounded repair를 적용했다. 누락/비문자열 `tag` input 레코드는
`inputs[index].tag is missing or is not a string`으로 `input_errors`에 기록된다.

lap211 middle이 F5를 독립 검수해 **승인**했다. 저장소 테스트를 import하지 않은 새 fixture 25 probe에서
후보측 손상 tag 9종(키 누락/int/None/True/False/float/list/dict/bytes)과 원본측 2종이 모두 정확한
index·문구로 기록되고 overall `INCONCLUSIVE`였다. 과잉 차단은 없다(정상 평행이동 pair `PASS`,
미지·빈 문자열 tag는 오류 아님). F1/F4 회귀와 실제 발산 3종의 `FAIL`은 불변이고, 손상 레코드가
`FAIL`을 `INCONCLUSIVE`로 세탁하지 않는다.

같은 검수에서 **신규 F6(차단)**을 확정했다. F5를 보존 pair에 적용하니 lap209에서 비어 있던
`input_errors.candidate`가 `inputs[1]`/`inputs[2]`의 tag 누락 2건으로 바뀌었다. 원인은 comparator가
아니라 후보 생산자다: `tools/runtime_env.py:3500-3502`의 `record_input()`이
`{"args": [...], "result": "OBSERVED"}`를 tag 없이 `inputs`에 넣고 `:3529`에서 `_g1_selector_flow`에
넘어가는 반면, 원본 경로 `:3091`은 같은 함수에 tagged `input_record`를 넘긴다. 그래서 앞으로의 후보
run은 세 stage가 모두 PASS이고 scene이 일치해도 F5+F4로 overall `INCONCLUSIVE`가 된다(생산자 형태를
본뜬 probe로 CONFIRMED; untagged 2건만 제거한 대조군은 `PASS`). fail-open이 아니라 항상 닫히는
fail-closed이며 승인된 fresh validation run 1회를 확정 낭비시킨다. F5는 되돌리지 않고 생산자
비대칭을 고친다.

모델 라우팅은 Luna/high(work), Claude Opus5/high(middle/judge), Astra/medium(strategy)이다.
Opus 검수는 `LOOP_PERMISSION_MODE=auto`를 일회 적용한다. Astra는 큰 분기·반복 교착에서만 약
10 lap당 1회 이하로 쓴다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 원본 pair 절반이 근거 없는 `count>=2` 게이트로 중단; R5-B F1/F4/F5 수리는 lap209·lap211 middle이 독립 승인; 신규 F6로 후보 run의 카드 PASS가 구조적으로 불가(work tier 수리 대기); F2/F3/R6-B는 승인 경계 재결 대기; 실제 후보 scene/input evidence 없음; WM_CLOSE 결함 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

다음은 **work tier의 F6 bounded repair**다. `tools/runtime_env.py`의 후보 selector flow가 원본과
대칭으로 고유 문자열 `tag`를 남기게 해서(`:3529`가 untagged `record_input` stub 대신 tagged recorder를
쓰도록), 후보 run evidence에 untagged 레코드가 남지 않게 한다. 회귀는 "후보 형태 evidence에 untagged
레코드 0건"과 "원본과 tag 충돌 없음"을 기계로 확인한다. comparator를 느슨하게 만드는 방향은 금지다
(F5 fail-open 재개방). 범위는 후보 기록 경로와 그 테스트뿐이며 좌표·예산·입력 시퀀스·판정식·
comparator·보존 evidence·바이너리는 건드리지 않는다. F6 수리와 다음 middle 검수 전까지 후보 Stage B
run·원본 재실행·R6-A/R6-C는 금지하고, F2/F3/R6-B는 재결 전 구현 금지다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, run 재사용, 무변경 blind retry, PASS 완화 금지.
- production 클릭 금지; 정상 비활성은 BLOCKED이며 후속 입력은 계속되어야 한다.
- random seed 미노출로 scene 불일치는 Tier-2 UNKNOWN이며 FAIL/PASS로 세탁하지 않는다.
- minimap은 camera 절대 목적지 비교가 필요하다.
- 후보 WM_CLOSE teardown 결함은 제품 출시 전 미해결이다.
- `drag_select` 게이트 `count>=2`는 근거 없는 절대 상수다. 재정의(R6-B)는 승인 경계라 **승격**했고,
  Sol/Astra 또는 사용자 재결 전까지 구현·후보 run 금지. 좌표 변경은 실험 전제 위반이라 금지다.
- 본영(type70)이 band-select 대상인지는 UNKNOWN이다. 결정적 probe(R6-C)는 추가 run 예산이 필요하다.
- R5-B F1/F4 수리는 lap209 middle이 독립 승인했다. 그래도 실제 pair가 없으므로 제품 G1 PASS가
  아니며, comparator의 어떤 PASS 산출도 제품 합격으로 신뢰하지 않는다.
- R5-B F5는 lap211 middle이 독립 승인했다. 그래도 comparator의 어떤 PASS 산출도 제품 합격이 아니다.
- **F6(차단)**: 후보 selector flow가 untagged `OBSERVED` 레코드를 남겨 F5+F4가 후보 run의 overall을
  항상 `INCONCLUSIVE`로 닫는다. 수리와 독립 검수 전에는 후보 Stage B run을 쓰지 않는다.
- R5-B F2(절대 slot id 동일성 요구)와 F3(`FAIL_NO_EFFECT` 오라클 상속 + `after.last` 미판독)은
  FAIL→UNKNOWN 판정 의미를 바꾸므로 R6-B와 같은 **승인 경계로 승격**했다. 재결 전 구현 금지.
- 실제 후보 scene/input evidence가 없어 카드 PASS는 여전히 산출할 수 없다.
- G1 실제 후보 증거와 G2~G4 제품 증거는 아직 없다.

## 검증 상태

- lap146~169: 후보 2배 표시·입력·지속 렌더 PASS, DxWrapper close 결함 귀속.
- lap170 Astra/medium: G1 합격 증거 우선, P6 주차.
- lap171~189: Stage A A-1~A-16 독립 승인, Fast 209/safety.
- lap190~198: baseline blocker 진단·R1~R4/N1~N3 구현·승인, Fast 213/safety.
- lap199 middle: 지속 승인 범위 확인, R5-A 계약, 사전 게이트 PASS.
- lap200~202: R5-A/R5-C 구현, Fast 221/runtime108/safety, game 0.
- lap203 middle: R5 자체 probe63 + Fast221/safety/setup PASS, pair run 인가.
- lap204 work: fresh 원본 Stage B `FAIL_NO_EFFECT` 보존, 후보 run SKIP, 승격 요청.
- lap205 middle: lap204 해시 5종 재현 PASS, 원인=판정식 결함 확정, `make check` 221/safety PASS, 게임 0회.
- lap206 work: R5-B comparator + offline fixture 6건 구현, `make check` 227/safety PASS, 게임 0회; 실제 pair 비교는 INCONCLUSIVE.
- lap207 middle: 해시 3종 재현 PASS, 보존 pair INCONCLUSIVE/NOT_COMPARED 재현, comparator
  probe로 F1~F4 확인 → R5-B 조건부 반려, `make check` 227/safety PASS, 게임 0회, 코드 변경 0.
- lap208 work: F1/F4 bounded repair + 회귀 2개, `make check` 229/Ruff/compileall/mypy/CONTEXT_PASS,
  `SAFETY_PASS`, 게임 0회. F2/F3은 승격 유지, 다음 middle 독립 검수 대기.
- lap209 middle: 독립 fixture 21 probe로 F1/F4 승인, F5 신규 발견, 보존 pair 판정 불변 재현,
  `make check` 229/Ruff/compileall/mypy 10 files/CONTEXT_PASS, `SAFETY_PASS`, 게임 0회, 코드 변경 0.
- lap210 work: F5 bounded repair + 회귀 2개, `make check` 231/Ruff/compileall/mypy/CONTEXT_PASS,
  `SAFETY_PASS`, 게임 0회. F2/F3/R6-B는 승격 유지, 다음 middle 독립 검수 대기.
- lap211 middle: 독립 fixture 25 probe로 F5 승인, 신규 F6(후보 생산자 untagged 레코드) CONFIRMED,
  보존 pair 판정 불변(INCONCLUSIVE/NOT_COMPARED/exit 2), `make check` 231/Ruff/compileall/
  mypy 10 files/CONTEXT_PASS, `SAFETY_PASS`, 게임 0회, 코드 변경 0.
- latest snapshot: `docs/history/laps/20260912_lap211_middle_r5b_f5_review.md`.

## 바퀴 기록

- lap2~199 및 이전 STATUS 원문: `docs/history/laps/`.
- lap200~211: `docs/history/laps/20260912_lap2*.md`; probe 원본: `docs/history/laps/probes/`.
- current escalation: `loop/ESCALATE_SOL`; handoff: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`.
