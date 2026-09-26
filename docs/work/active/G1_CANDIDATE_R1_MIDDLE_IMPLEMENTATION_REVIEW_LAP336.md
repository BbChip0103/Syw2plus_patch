# lap336 middle — lap335 후보 R1 구현 독립 검수 (ACCEPT-WITH-REQUIRED-REPAIR)

2026-09-12 / lap336 / Claude Code `claude-opus-5` / high / middle(진단·계획·확인).
검수 대상은 lap335 work의 후보 R1 구현이며 계약은 `G1_CANDIDATE_R1_MIDDLE_ENVELOPE_LAP334.md` §11이다.
middle은 게임 코드/하네스를 직접 고치지 않는다. 이 문서는 제품 G1 합격·Stage B 허가·마일스톤
종료/이동·사용자 승인이 아니다. **실행 예산은 이 문서로도 0회를 유지한다.**

## 0. 판정 요약

| 항목 | 판정 | 근거 |
|---|---|---|
| 후보 artifact/lock/log 이름 분리 (봉투 §10) | **PASS** | §2.1 |
| 무배율 클릭 `content_crop+(296,505)` (§5·N11) | **PASS** | §2.2 |
| 기하 게이트 (§5) | **PASS** | §2.3 |
| 모듈 게이트 private ddraw/금지 syw2x (§4.4) | **PASS(fail-closed 6종)** | §2.4 |
| 다섯 실패 분류와 비-PASS 유지 (§9) | **PASS** | §2.5 |
| cleanup·dxwrapper 원복 계약 (§7) | **PASS** | §2.6 |
| 원본 R1 경로 불변 (§11.1) | **PASS(정적)** | §2.7 |
| 클릭 1회·게이트 선행 (§9·§12) | **PASS** | §2.8 |
| 봉투 §11.3 필수 테스트 완비 | **FAIL(수리 R-a)** | §3.1 |
| 봉투 §8 준비/PS9 40초 상한 | **부분 FAIL(수리 R-b)** | §3.2 |
| lap332/lap334 probe 생존 | **FAIL(middle 권한 밖 → 승격)** | §4 |

**판정: ACCEPT-WITH-REQUIRED-REPAIR.** 후보 레인의 코드 계약은 독립적으로 재현했고 결함은 없다.
그러나 봉투가 **필수로 요구한 회귀 테스트 1건이 없고**(§3.1) 시간 봉투 상한이 한 구간에서 느슨하다(§3.2).
§12 발효 순서상 "다음 새 middle 독립 검수"는 이 두 수리와 §4 결정 전까지 **완료로 치지 않는다.**
후보 fresh 1 run은 **아직 발효하지 않는다.**

## 1. 검수 방법과 재현

- 검수한 현물: `tools/runtime_env.py` `922a267c27f51fe47d7db69962dadbfdbbded9ff04c6350e8cb7a4c44f8a2575`,
  `tests/test_lap326_r1_load_origin.py` `c04a6265229f7e37cb9d4434f0e150c76e1e56d26f0e1c990cb938a06d769823`.
  둘 다 lap335 기록값과 **일치**한다(1차 출처 대조).
- 신규 probe `docs/history/laps/probes/20260912_lap336_middle_lap335_candidate_implementation_probe.py`
  (`2e1481b845e787fe1bd228c247d4dfa992d2dd2bf00b29b1db2f3e1505f8e25d`), rc0, `failures=[]`,
  stdout SHA256 `9295dfdfd9bee0b5dc298946f2348c2a7327961ce81cf4f78d43a6c7d1593a0f`(연속 2회 byte-identical), Ruff PASS.
- 독립 재실행: `make check` **376 passed**(57.16s)·Ruff/compileall/mypy/`CONTEXT_PASS`·rc0,
  `bash checks/safety.sh check` **SAFETY_PASS**.
- **N13(수치 영향 0):** lap335 기록은 대상 테스트 파일을 "16 passed"로 적었으나 같은 SHA의 파일을
  재실행하면 **15 passed**다(전체 376은 일치). 전부 통과이므로 판정 영향은 없고, 기록 숫자만 부정확하다.
- 게임 실행 0회, 입력 0회, 메모리 읽기/쓰기 0회, PNG 0장, 커밋 0건, 후보 artifact 생성 0건.
- **probe 설계(lap334 N12 적용):** 이 probe는 살아 있는 파일의 SHA 일치를 **단언하지 않는다.**
  그런 단언은 정당한 편집 한 번으로 영구 실패가 되며(§4), 그것을 통과시키려 재pin하는 것은 금지다.
  살아 있는 SHA와 미결 사항은 `findings` **데이터로 보고**만 하므로 수리 뒤에도 재pin이 필요 없다.

## 2. 통과한 계약 (probe로 독립 재유도)

### 2.1 이름 분리 — 봉투 §10의 실제 이유를 지킨다
후보는 `output/r1_load_origin_candidate.json`, lock `.r1-load-origin-candidate.lock`,
log `r1_load_origin_candidate.log`를 쓰고 원본 함수는 `r1_load_origin.json`/`.r1-load-origin.lock`를
그대로 유지한다. 전 저장소 실측 원본 artifact **1건**, 후보 **0건** — lap332의 exact-once 단언은 깨지지 않았다.

### 2.2 무배율 클릭 — lap148의 ×2 FAIL 재발 없음
`_g1_input_geometry((100,200,1600,1200),(2.0,2.0),296,505)["x11"] == [396,705]`,
`_g1_r1_candidate_click_geometry` 동일값 + `scale_applied=[1.0,1.0]`. 배율은 기록용 `scale`로만 남는다(N11).
`G1_R1_CLICK_POINT=(296,505)`, `G1_R1_WAIT_PS_STATES=(9,35)` 드리프트 없음.

### 2.3 기하 게이트
root/content 둘 다 1600×1200일 때만 통과하고 `logical_size=[800,600]`·`scale=[2.0,2.0]`을 단언한다.
content 800×600(프로필 미적용, lap152 선례)과 root 800×600 둘 다 `BLOCKED_PRECONDITION`·`status=UNKNOWN`.

### 2.4 모듈 게이트 — 6종 fail-closed를 실측
통과: private `game/ddraw.dll` 1건 + manifest 실측 해시 일치 + `syw2x` 부재.
거부(전부 `BLOCKED_PRECONDITION`): syw2x 적재 / ddraw 모듈 2건(빌트인 폴백) / 해시 불일치 /
기대 해시 부재(`{}` → None 비교로 닫힘) / 사본 밖 ddraw 경로 / `modules` 리스트 부재.
`_module_evidence`가 `modules`를 EXE·ddraw로 **걸러내므로** syw2x 판정은 전체 `maps_raw`를 봐야 맞고, 구현이 그렇게 한다.

### 2.5 다섯 실패 분류
`FAIL_NO_EFFECT→NOT_REACHED`, `UNKNOWN_BUDGET_EXHAUSTED→TIMEOUT`, `*READ*→COLLECTION_ERROR`,
`pre==post→NO_CHANGE`, 게이트→`BLOCKED_PRECONDITION`. 다섯 모두 `status="UNKNOWN"`으로 고정되어
**실패가 PASS로 승격되지 않는다.** 변화가 있을 때만 `OBSERVED/REACHED_CHANGED`.
CLI는 `RuntimeSafetyError`를 rc2로 바꾸므로 실패 run이 exit0으로 끝나지 않는다.

### 2.6 cleanup·원복
`ok`는 소유 자식 종료 ∧ Xvfb 종료 ∧ `prefix_processes_after==[]` ∧ wineserver 오류 없음 ∧
`dxwrapper_config_restored` ∧ 원복 오류 없음의 논리곱이다. 네 가지 위반(원복 미수행/원복 오류/
잔존 PID/wineserver 오류) 각각에서 `ok=False`를 실측했다. `uninstall_private`는 복원본이
`918e7043…a5a2`가 아니면 `ValueError`를 내고 구현은 그것을 `cleanup.error`로 드러낸다(은폐 없음).
원복은 `finally`에 있고 `install_private`가 성공했을 때만 시도한다.

### 2.7 원본 경로 불변 (정적 근거)
후보는 공용 헬퍼를 **재작성하지 않고 별도 함수로 복제**했다. 공유 지점 실측:
`_game_window_ids`의 기본 `allowed_sizes=((800,600),)` 유지, 원본은 여전히 `_game_window_ids(tree)`
기본 호출, 원본 `WINEDLLOVERRIDES="ddraw=b"` vs 후보 `"ddraw=n,b"`, 원본 800×600 게이트 문구 유지.
`_g1_r1_compare_origin`은 원본이 쓰는 그대로이고 후보는 **반환 사본만** `NO_CHANGE`로 재라벨한다.
**한계:** 커밋이 0이라 lap330 시점 원본 함수 본문과의 바이트 diff는 불가능하다(§4 참조). 이 판정은
"현재 소스가 원본 계약을 만족한다"이지 "편집 중 원본 줄이 한 줄도 안 바뀌었다"의 증명이 아니다.

### 2.8 클릭 1회와 게이트 선행
후보 본문에 `x11_mouse_click.py` 호출은 **정확히 1곳**이고, 모듈 게이트·기하 게이트·PS9 origin
`(0,0,0)` 사전조건·무배율 좌표 계산이 **전부 그 앞**에 온다. `input.count`는 주입 성공 뒤에만 1이 된다.

## 3. 필수 수리 (work tier, 실행 0회 유지)

### 3.1 R-a — 봉투 §11.3이 요구한 artifact 이름 분리 테스트가 없다 (FAIL)
§11.3은 "artifact 이름 분리 단언"을 **필수 테스트로 열거**했다. 현재 테스트 파일 어디에도
`r1_load_origin_candidate.json` / `.r1-load-origin-candidate.lock` 문자열이 없다. 코드는 옳지만
**회귀 잠금이 없다.** 이름이 원본과 같아지는 드리프트는 lap332의 전 저장소 exact-once 단언을 깨고,
그 단언을 고쳐 통과시키는 것은 금지이므로 이 테스트는 장식이 아니라 계약 보호 장치다.
수리: 후보 artifact/lock/log 이름과 원본 이름이 **서로 다르다**는 오프라인 단언을 추가한다(실행 불필요).

### 3.2 R-b — 준비 구간이 §8의 40초 상한 밖에 있다 (부분 FAIL)
후보 PS9 대기는 `stage_started=launch_started`를 쓰는데 `launch_started`는 **dxwrapper 설치 뒤**에
찍힌다(원본은 `stage_started=started`). 따라서 §8의 "준비/PS9 40초"는 설치 시간을 포함하지 못하고,
준비+PS9 실측 상한이 40초를 넘을 수 있다. 총 90초 단일 deadline은 `_wait_state(started, timeout)`가
계속 강제하므로 **예산 초과는 아니지만**, 배분 상한은 봉투가 명시한 계약이다.
수리: PS9 stage 기준을 `started`로 되돌리거나, 설치 구간을 별도 상한으로 선언하고 근거를 기록한다.
자동 연장·재시도는 그대로 금지다. (관측 15초/종료 15초 "확보"도 구조적으로 강제되지 않는다 —
이것은 원본 R1에서 물려받은 성질이며 이번 수리 범위 밖으로 남긴다.)

## 4. middle 권한 밖 — 승격할 결정 (lap332·lap334 probe 무효화)

lap335의 편집은 봉투 §11이 **허가한** 파일에 대한 것이다. 그러나 그 편집으로
`20260912_lap332_middle_lap331_r1_artifact_probe.py`와
`20260912_lap334_middle_candidate_r1_envelope_probe.py`가 **둘 다 rc1로 영구 실패**한다.
실패 사유는 결함이 아니라 **살아 있는 `tools/runtime_env.py`의 SHA를 lap330 값으로 고정**했기 때문이다
(`"live harness SHA differs from the reviewed SHA"`, `"runtime_env.py drifted from the lap330-reviewed harness SHA"`).

- 이것은 **W3(lap300)과 같은 형태의 함정**이고, lap334가 STATUS에 대해 스스로 진단한 **N12와 같은 결함**이
  한 바퀴 뒤 하네스에 대해 재발한 것이다. lap334는 STATUS 비교를 불변 압축본으로 옮겼지만 하네스 SHA
  단언에는 같은 교훈을 적용하지 않았다.
- **재pin은 금지다.** 안전 pin/기대값을 통과시키려 갱신하지 않는다(AGENTS.md), W3 재pin은 Astra/사용자
  결정 대기 항목이다. middle/work 단독으로 두 probe의 기대 SHA를 현재 값으로 바꾸지 않는다.
- **회복 불가 손실:** `LOOP_ALLOW_COMMITS=0`이고 스냅샷도 없었으므로 lap330~334가 검수한 하네스 원문
  (`997ff15b13115ccebd9d8832b3b066add589b755d9cc6e8a77d987696cc46eed`)은 **디스크에 남아 있지 않다.**
  `tools/__pycache__/runtime_env.cpython-312.pyc`는 194,028바이트 원문(더 이전 판)의 바이트코드라 대체물이 아니다.
  lap331 artifact의 `provenance.harness_sha256`은 여전히 `997ff15b…`를 가리키므로, 그 run의 "검수 SHA ==
  실행 SHA" 재확인은 이제 **기계적으로 재현할 수 없다.** lap332 ACCEPT는 당시 판정으로 이력에 남되,
  재실행으로 다시 세울 수는 없다.
- 후보 run이 발효하면 그 artifact의 하네스 SHA는 `922a267c…f8a2575`가 된다. **다음 검수자는 lap330 값이
  아니라 이 값과 대조해야 한다.** 이 문서가 그 검수 기준선을 기록한다.

승격 질문(셋 다 middle 권한 밖):
1. 두 probe를 "범위 만료(scope-expired)"로 선언해 이력으로만 보존할 것인가, 재pin을 허가할 것인가,
   아니면 하네스 원문 스냅샷 정책(예: 검수 시점 원문을 `docs/history/`에 보존)을 도입할 것인가.
2. 검수된 레인을 편집 허가할 때, 결합된 과거 probe 재실행을 봉투의 **필수 항목**으로 넣을 것인가
   (STATUS의 "프로세스 사각"이 lap294·lap296에 이어 세 번째로 실현됐다).
3. 커밋 금지 상태에서 검수 기준 원문을 어떻게 보존할 것인가.

## 5. 다음 발효 순서 (변경 없음)

**이 ACCEPT-WITH-REQUIRED-REPAIR → work가 R-a·R-b 수리(실행 0) → 다음 새 middle이 수리 재검수 →
그때 후보 fresh 1 run 발효 → 다음 새 middle이 artifact 판정.** §4 결정은 별도 레인으로 승격한다.
금지 목록(봉투 §12)은 전부 유지된다: W3 재pin, 원본 n>1, 재클릭, 예산 확대, Stage B, PNG,
baseline/golden/안전 pin 갱신, ptrace/int3/디버거, 새 의존성, G2~G4 확대, WM_CLOSE/P6 착수, 커밋.

## 6. 이 문서가 아닌 것

제품 G1 합격, Stage B 허가, 마일스톤 종료/이동, 사용자 승인이 아니다. G2~G4 증거는 0이다.
`make check` 376 passed·SAFETY_PASS·probe rc0은 제품 검증이 아니며 프로세스 exit0은 어떤 승인도 아니다.
후보 구현이 정적으로 옳다는 것과 후보가 실제로 1600×1200에서 원본과 같이 동작한다는 것은 다른 명제다.
후보 실행 증거는 여전히 **0건**이다.
