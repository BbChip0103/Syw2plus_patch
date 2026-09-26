# lap337 middle — lap336 검수 재현과 R-a·R-b 수리 범위 확정 (work tier 핸드오프)

2026-09-12 / lap337 / Claude Code `claude-opus-5` / high / middle(진단·계획·확인).
상위 계약은 `G1_CANDIDATE_R1_MIDDLE_ENVELOPE_LAP334.md`, 직전 판정은
`G1_CANDIDATE_R1_MIDDLE_IMPLEMENTATION_REVIEW_LAP336.md`다.
middle은 게임 코드/하네스를 직접 고치지 않는다. 이 문서는 **수리 범위 확정과 핸드오프**이며
제품 G1 합격·Stage B 허가·마일스톤 종료/이동·사용자 승인이 아니다.
**후보 실행 예산은 이 문서로도 0회를 유지한다.**

## 0. 이번 바퀴 판정 요약

| 항목 | 판정 | 근거 |
|---|---|---|
| lap336 probe rc0·stdout SHA 재현 | **PASS(2회 byte-identical)** | §1.1 |
| `make check` 376 passed·SAFETY_PASS 재현 | **PASS** | §1.2 |
| 검수 기준선 두 SHA 재확인 | **PASS** | §1.3 |
| N13(15 passed, 기록은 16) | **CONFIRMED** | §1.4 |
| lap332·lap334 probe rc1 | **CONFIRMED, 원인 분해는 신규(§2)** | §2 |
| lap336 STATUS 보존 충실성 | **PASS** | §1.5 |
| R-a 결함 실재 | **CONFIRMED(독립 재유도)** | §3 |
| R-b 결함 실재 | **CONFIRMED(AST 재유도)** | §4 |
| R-a·R-b 수리 형태 | **확정(work tier로 이관)** | §3·§4·§5 |

검증 probe: `docs/history/laps/probes/20260912_lap337_middle_lap336_repair_scope_probe.py`
(`1dd47cd3ede36c03168ed5910ed71356488f227d18e3e78fe050c83cdcbbc545`), rc0, `failures=[]`,
stdout SHA256 `c38a73f1220faf992155bc5a98fe814e9e8ded316b0935e5eb3f22f0738cdf46`
(연속 2회 + `.venv/bin/python`/`/usr/bin/python3` 교차 실행 전부 byte-identical), Ruff PASS.
게임 실행 0회, 입력 0회, 메모리 읽기/쓰기 0회, PNG 0장, 커밋 0건, 후보 artifact 생성 0건.

**probe 설계(lap334 N12·lap336 §4 교훈 적용):** 이 probe는 살아 있는 파일의 SHA도,
"수리 전에만 참인 결함 상태"도 **단언하지 않는다.** 둘 다 정당한 편집 한 번으로 영구 실패가 되고
그것을 통과시키려 재pin하는 것은 금지다. 수리 전후로 모두 참이어야 하는 계약(이름 분리·시간 배분
상한·좌표/상태 상수·불변 압축본 본문 SHA)만 단언하고, 전이 상태는 `findings` **데이터로 보고만** 한다.

## 1. lap336 검수 재현 (④2 이전 바퀴 검수)

### 1.1 probe
`20260912_lap336_middle_lap335_candidate_implementation_probe.py`
(`2e1481b8…505f8e25d`, 살아 있는 파일 실측) → rc0, `failures=[]`,
stdout SHA256 `9295dfdfd9bee0b5dc298946f2348c2a7327961ce81cf4f78d43a6c7d1593a0f`.
lap336이 기록한 값과 **일치**하고 연속 2회 byte-identical이다.

### 1.2 게이트
`make check` rc0 · **376 passed (57.26s)** · Ruff/compileall/mypy `All checks passed!` · `CONTEXT_PASS`.
`bash checks/safety.sh check` → **SAFETY_PASS**. lap336 기록(376 passed, 57.16s)과 일치한다(초 단위 차이는 측정 잡음).

### 1.3 검수 기준선
`tools/runtime_env.py` = `922a267c27f51fe47d7db69962dadbfdbbded9ff04c6350e8cb7a4c44f8a2575`,
`tests/test_lap326_r1_load_origin.py` = `c04a6265229f7e37cb9d4434f0e150c76e1e56d26f0e1c990cb938a06d769823`.
lap336 §4가 지정한 "다음 검수 기준선"과 **일치**한다. 이 두 값이 다음 검수자의 대조 기준이다.
lap330 값 `997ff15b…cc46eed`는 더 이상 디스크에 없다(§2).

### 1.4 N13
`tests/test_lap326_r1_load_origin.py`는 `make check` 출력에서 점 **15개**다(`...............`).
lap335 기록의 "16 passed"는 부정확하고 lap336의 N13이 옳다. 전부 통과이므로 수치 영향 0.

### 1.5 STATUS 보존
`docs/history/laps/20260912_status_lap335_compaction.md`의 fenced body SHA256을 독립 계산하면
`bba77d09fa70de0c80c67510819b528b19e02caadc6c1e558b85cefbc0fc1954`, **130줄** — lap336 기록과 일치한다.
lap336의 보존은 충실하다(probe 단언 항목).

### 1.6 artifact 건수
전 저장소 실측: `local/runtime/*/output/r1_load_origin.json` **1건**
(`20260912_172722_2210599_0`, lap331 run), `r1_load_origin_candidate.json` **0건**.
**후보 실행 예산은 아직 한 번도 쓰이지 않았다.**

## 2. lap332·lap334 probe 무효화 — 재현 + 신규 원인 분해

두 probe를 재실행해 **둘 다 rc1**임을 확인했다(lap336 §4 CONFIRMED). 신규 사실은 **실패의 분해**다:

| probe | rc | `failures` 전량 |
|---|---|---|
| `…lap332_middle_lap331_r1_artifact_probe.py` | 1 | `live harness SHA differs from the reviewed SHA`, `live R1 test SHA differs from the reviewed SHA` |
| `…lap334_middle_candidate_r1_envelope_probe.py` | 1 | `runtime_env.py drifted from the lap330-reviewed harness SHA` |

**두 probe의 실패 항목은 살아 있는 SHA 단언이 전부다.** 그 밖의 모든 단언(lap332의 artifact
exact-once·표본 12건 WORD==DWORD·단조·`pending` 0→34·사슬 7지점, lap334의 압축본 대조·130줄
·C1 재유도)은 **지금도 통과한다.** 즉 손실 범위는 lap336이 적은 것보다 **좁다**:

- 기계적으로 **복구 불가**인 것은 "lap331 run의 실행 SHA `997ff15b…`가 검수된 원문과 같다"는
  **동일성 재확인 한 가지**뿐이다. 그 원문은 커밋 0·스냅샷 0이라 디스크에 없다.
- 두 probe의 **실질 내용은 살아 있다.** 따라서 §6의 승격 질문 1은 "두 probe를 버릴 것인가"가
  아니라 **"죽은 SHA 단언 2~3줄을 어떻게 처리할 것인가"** 로 좁혀진다. 이 좁힘은 결정을 대신하지
  않는다. 재pin은 여전히 금지이고 middle/work 단독으로 하지 않는다.

## 3. R-a — 수리 형태 확정 (프로덕션 코드 변경 없음)

**결함 재유도:** 후보 세 이름 문자열 `r1_load_origin_candidate.json` /
`.r1-load-origin-candidate.lock` / `r1_load_origin_candidate.log` 중 **어느 것도**
`tests/test_lap326_r1_load_origin.py`에 없다(probe `r_a_name_assertions_present` 3항 전부 `false`).
`test_candidate_cli_forwards_separate_artifact_lane`은 **CLI 디스패치만** 단언하고 이름은 보지 않는다.
lap336 §3.1이 옳다.

**확정한 수리 형태 — 오프라인 단언만 추가하고 `tools/runtime_env.py`는 건드리지 않는다.**

- 이름을 모듈 상수로 승격하는 대안은 **채택하지 않는다.** 값 보존 리팩터링이라도 원본 함수 줄을
  다시 건드리면, 커밋 0 때문에 이미 바이트 diff가 불가능한 원본 경로(§11.1, lap336 §2.7의 명시적
  한계)의 검수 부담이 또 늘어난다. R-a는 **회귀 잠금이 없다**는 결함이지 코드 결함이 아니다.
- 이름 추출은 `inspect.getsource` + `ast` 리터럴 수집으로 한다(probe §3 구현이 동작하는 형태를
  그대로 쓸 수 있다). 정규식 문자열 매칭도 허용하지만 AST가 오탐이 적다.
- 필수 단언 네 가지:
  1. 후보 함수의 (json, lock, log) == `("r1_load_origin_candidate.json",
     ".r1-load-origin-candidate.lock", "r1_load_origin_candidate.log")`.
  2. 원본 함수의 (json, lock, log) == `("r1_load_origin.json", ".r1-load-origin.lock",
     "r1_load_origin.log")` — §11.1 원본 불변의 회귀 잠금이다.
  3. 두 집합의 교집합이 **공집합**.
  4. 후보 함수의 exact-once 가드가 **후보 artifact 경로**를 본다는 단언(현재 구현은
     `artifact_path.exists()`이며 원본은 `(output / "r1_load_origin.json").exists()`다).
- **금지:** 살아 있는 파일 SHA 단언, artifact 건수 기대값 단언, "수리 전에만 참"인 단언.
  이 테스트는 이름 **계약**만 본다. 계약이 바뀌지 않는 한 정당한 편집으로 깨지지 않는다.

**이유(장식이 아니다):** 이름이 원본과 같아지는 드리프트는 lap332의 전 저장소 exact-once 단언을
깨고, 그 기대 건수를 고쳐 통과시키는 것은 금지(봉투 §12)다. 그러면 후보 레인은 복구 경로가 없다.

## 4. R-b — 수리 형태 확정 (한 인자)

**결함 재유도(AST):** `_wait_state` 호출의 stage 결합을 소스에서 직접 읽으면

| 함수 | stage | `stage_budget` | `stage_started` |
|---|---|---|---|
| `g1_r1_load_origin` | `r1_ps9` | `G1_R1_PS9_STAGE_BUDGET` | **`started`** |
| `g1_r1_candidate_load_origin` | `candidate_ps9` | `G1_R1_PS9_STAGE_BUDGET` | **`launch_started`** |

`launch_started = stage_start("launch_and_ps9")`는 `dxwrapper_config.install_private(game)` **뒤**에
찍힌다. 따라서 후보의 40초 창은 설치 구간을 제외한다. lap336 §3.2가 옳다.

**확정: 수리안 (a) — `stage_started=started`로 되돌린다. (b)는 기각한다.**

- 봉투 §8의 문구는 "**준비**/PS9 40초"다. dxwrapper 설치는 후보 레인의 **준비**이므로 40초 창 안에
  들어가는 것이 계약의 문자 그대로다.
- (b) "설치 구간을 별도 상한으로 선언"은 준비 합계 상한을 40초 위로 올리는 것이고, 봉투 §12의
  **예산 확대 금지**에 저촉된다. 총 90초 deadline이 따로 있다는 사실은 배분 상한의 면제가 아니다.
- (a)는 원본 경로와 **같은 결합**이 되어 §11.1 대칭성을 회복한다. 두 레인이 같은 의미의 40초를 쓴다.
- 비용 근거: `install_private`는 단일 `dxwrapper.ini`의 read/sha256/write와 sidecar 2개 쓰기뿐이다
  (`patches/resolution/dxwrapper_config.py:115-153`). 40초 예산에서 이 구간이 차지할 몫은 무시할
  수준이고, lap331 원본 run 전체가 4.278초였다. **(a)로 인한 예산 압박은 실질적으로 없다.**
- **변경 범위는 인자 하나**다: `stage_started=launch_started` → `stage_started=started`.
  `stage_start("prepare_and_install")`/`stage_start("launch_and_ps9")`와 `stage_timeline` 기록은
  **그대로 둔다**(봉투 §10의 구간별 monotonic 기록 필수 항목). `stage_end("launch_and_ps9",
  launch_started)`도 그대로다 — 그것은 구간 duration 기록이지 예산 창이 아니다.
- **회귀 잠금(필수):** §3과 같은 AST 단언으로 두 함수의 PS9 `stage_started`가 **둘 다 `started`** 임을
  오프라인 단언한다. 잠금 없는 수리는 R-a와 같은 결함을 다시 만든다.
- **범위 밖(유지):** lap336 §3.2 말미의 "관측 15초/종료 15초 확보가 구조적으로 강제되지 않는다"는
  원본 R1에서 물려받은 성질이다. 이번 수리에 포함하지 않는다. 후보/원본 공통 사안이므로 원본 경로를
  함께 건드려야 하고, 그것은 §11.1 불변 요구와 충돌한다. 별도 카드로 남긴다.

## 5. work tier 핸드오프 (Luna/Sonnet5 high, 실행 0회)

허용 파일: `tests/test_lap326_r1_load_origin.py`(R-a·R-b 잠금),
`tools/runtime_env.py`(**R-b 인자 한 곳만**). 그 밖의 파일은 건드리지 않는다.
`patches/resolution/dxwrapper_config.py`의 pin은 건드리지 않는다.

1. R-b: `g1_r1_candidate_load_origin`의 `stage="candidate_ps9"` `_wait_state` 호출에서
   `stage_started=launch_started` → `stage_started=started`. **이 한 줄 외의 후보/원본 본문 수정 0.**
2. R-a: §3의 필수 단언 네 가지를 오프라인 테스트로 추가한다. 프로덕션 코드 변경 없음.
3. R-b 잠금: 두 함수의 PS9 `stage_started` 심볼이 둘 다 `started`임을 오프라인 단언한다.
4. `make check` 전체 통과 + `checks/safety.sh check` SAFETY_PASS + Ruff/mypy 통과.
   테스트 수는 15 → 17~18이 될 것이다(정확한 수를 기록에 적는다. N13 재발 금지).
5. **실행 0회.** 게임 실행·입력·메모리 접근·PNG·후보 artifact 생성 전부 0을 유지한다.
6. 자기 결과를 자기가 승인하지 않는다. 기록은 `docs/history/LAP_TEMPLATE.md` 형식으로 남긴다.
7. §2·§6의 승격 질문(재pin 정책)은 **건드리지 않는다.** 두 stale probe를 수정하지 않는다.

## 6. middle 권한 밖 — 승격 유지 (`loop/ESCALATE_SOL`)

lap336이 올린 세 질문은 그대로 유효하고 이 바퀴가 답하지 않는다. §2의 분해는 질문 1의 범위를
좁힐 뿐이다. 재pin 금지·W3 선례·안전 pin 자동 갱신 금지는 유지된다.
lap337 부록은 `loop/ESCALATE_SOL`에 **lap336 원문을 지우지 않고 덧붙였다.**

## 7. 다음 발효 순서 (변경 없음)

**이 문서(수리 범위 확정) → work가 R-a·R-b 수리(실행 0) → 다음 새 middle이 수리 재검수 →
그때 후보 fresh 1 run 발효 → 다음 새 middle이 artifact 판정.** 승격 질문은 별도 레인이다.
금지 목록(봉투 §12)은 전부 유지된다.

## 8. 이 문서가 아닌 것

제품 G1 합격, Stage B 허가, 마일스톤 종료/이동, 사용자 승인이 아니다. G2~G4 증거는 0이다.
`make check` 376 passed·SAFETY_PASS·probe rc0은 제품 검증이 아니며 프로세스 exit0은 어떤 승인도 아니다.
후보가 실제로 1600×1200에서 원본과 같이 동작한다는 증거는 여전히 **0건**이다.
