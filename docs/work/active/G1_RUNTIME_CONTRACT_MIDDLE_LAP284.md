# lap284 middle — lap283 실행 계약 여섯 필수 입력 판정

2026-09-12. Claude Code `claude-opus-5` / high, middle tier(진단·계획·컨펌). 게임 구현 없음.
수신: `docs/work/active/G1_RUNTIME_G3_ASTRA_DECISION_LAP283.md`의 middle handoff 표와
`loop/ESCALATE_SOL`(lap283)의 승격 요청.
게임/Wine/Xvfb/Stage B/원본 재실행/PNG **0회**, 원본 트리 쓰기 0, comparator/producer/
회귀/테스트/PASS 규칙 **무변경**. 이 문서는 제품 G1 합격·runtime 예산 승인·마일스톤 종료가 **아니다**.

근거 probe(읽기 전용, 재실행 가능):
`docs/history/laps/probes/20260912_lap284_middle_runtime_contract_probe.py`
→ `logs/lap284/runtime_contract_probe.json`, exit0, **failures=[]**.

## 0. 판정 요약

| 필수 입력 | 판정 |
|---|---|
| 1 fixture 선택 | **REJECT** — 파일/SHA/복사 경로는 확정, 로드 메뉴·상태 전이 근거 없음 |
| 2 실제 하네스 연결 | **REJECT** — 하네스에 저장 로드 경로가 0줄. 수정 대상 미지정 |
| 3 측정식 | **ACCEPT** — lap277 §3 (A)+(B)를 변경 없이 그대로 유효화 |
| 4 tick | **REJECT** — 허용오차 근거 미제출. 순환 의존을 아래 §4에 명문화 |
| 5 실행 봉투 | **REJECT** — 복사/prefix/해시/시간 상한은 있으나 load 경로 명령·수집 절차 없음 |
| 6 실패 보존 | **ACCEPT-WITH-CONDITION** — 기존 기구가 충족, 신규 실패 모드 1건 선언 필요 |

**결론: runtime 예산 요청 불가.** 원본↔원본 1쌍도 요청하지 않는다. Stage B 0 유지.
work 인계는 §7의 **offline 조사 카드 한 장**이다. 이는 계약 표의 "fixture 미충족 시 → 좁은
work 조사 카드" 경로를 그대로 사용한 것이며 새 계열을 여는 것이 아니다.

## 1. 이전 바퀴(lap283) 독립 검수

- lap283 기록의 파일 fingerprint **9/9 전부 재계산 일치**: 결정문서
  `b231386b…0bd6a06d`, `docs/STATUS.md` `90871859…2075063d`, `loop/ESCALATE_SOL`
  `c5ca3e61…4a5a10ed`, `.omx/plans/lap283-astra-runtime-g3.md` `0c610778…63ee258b`,
  `logs/lap283/{unit_offset_review_recheck.json,make-check.log,safety.log,before_sha256.json,status_before.md}`.
- lap282 probe `cdfa7c3c…b42ae764`와 그 출력 `logs/lap282/unit_offset_review_probe.json`
  `e0f07f3a…46f4be08`이 lap283 recheck 출력과 **바이트 동일**하다. 재실행 결과가 보존됐다.
- **정정 1건(문서 인용 기준, 판정 불변):** lap283 기록 본문이 recheck 출력 SHA를
  `e0f07f3a4352c51959919fc0b5eb6bc1f907a09596ae3e5d5d8c5e46f4be08`(62자)로 적었다.
  실제 값이자 같은 기록의 fingerprint 절에 있는 값은
  `e0f07f3a4352c51959919fc0b5eb6bc1f907a09596ae3e5d5d8d8c5e46f4be08`이다. 본문 쪽이 오타다.
- G3 초과 `0x1B5A4`를 이 세션 probe의 자체 상수로 재계산해 일치를 확인했다.
- 재검증하지 **않은** 것: R17, R6-B-R2, M-d/M-e, 나머지 offline 8건, WM_CLOSE. 전부 주차 유지.
- lap 번호: 사용자 runtime 표기는 283이나 `loop/.lap_counter`는 **284**다. PROMPT 규칙대로
  284를 쓰고 counter에 쓰거나 복원하지 않았다(lap283도 같은 +1 차이를 기록했다).

## 2. 항목1 fixture 선택 — REJECT

**확정된 것(기계 확인).**

| 사실 | 값 | 출처 |
|---|---|---|
| `Syw2plus/save/save000.dat` | 3,093,902 B / `1c703551…629e719da` | probe `fixtures.fixture_dir` |
| `Syw2plus/save/save006.dat` | 3,437,942 B / `616b7997…9289a0d064` | 동일 |
| `prepare()` 복사 원본에도 **같은 SHA로 존재** | `Syw2plus_re/Syw2plus/save/` | probe `fixtures.prepare_copy_source` |

`tools/runtime_env.py:155`의 `DEFAULT_SOURCE`가 그 디렉터리이고 `prepare()`는
`shutil.copytree(source, game)`(:530)로 트리 전체를 복사한다. 따라서 **두 save는 별도 반입
절차 없이 이미 사설 복사본 안에 들어간다.** 동시에 두 개가 다 들어가므로 "어느 save를
쓰는가"는 파일 배치가 아니라 **게임 안 선택**으로 정해진다(사설 복사본에서 한쪽을 지우는
선택지는 남아 있으나 이 tier가 지정하지 않는다).

**내용 기반 선택 근거가 새로 가능해졌다(§2.1).** 그런데도 REJECT인 이유는 계약이 함께
요구한 **로드 메뉴/상태 전이 근거가 없기** 때문이다:

- `analysis/memory_maps/player_offsets.md:255`는 프로그램 상태 **PS=35 = 불러오기**를 적어
  둔다. 그러나 `tools/runtime_env.py`에는 **PS 35 참조가 0개**이고 대기하는 PS는
  `[3, 5, 7, 9]`뿐이다(probe `harness.ps_states_waited`).
- 타이틀에서 불러오기 항목을 누를 **좌표가 저장소 어디에도 없다.** 기록된 좌표는
  랜덤게임 진입 `(184,560)`(`tools/runtime_env.py` g1_baseline 본문)과
  `G1_SETUP_POINTS`의 `multiplayer_mode/solo_mode/connection_confirm/lobby_start` 4개뿐이다.
- `docs/history/20260910_EXPERIMENTS.md:16-17`의 save011/012 로드는 **역사적 관측**이며
  좌표·PS 전이를 남기지 않았다. lap277 §4는 "메뉴에 불러오기가 보인다"를 CONFIRMED로
  쓰지 못하게 했고 그 규칙은 유효하다.

**계약 열거 정정 1건.** 계약은 후보를 save000/save006 둘로 못박았지만 이 저장소에는
`local/fixtures/20260910/save011.dat`(1,982,062 B / `23dd24d5…be14dfa4`)와
`save012.dat`(1,985,822 B / `5a6863c1…819c28f1`)가 출처 기록과 함께 존재한다
(`docs/history/20260910_MIGRATION.md:37`). 이 tier는 후보를 넓히지 않고 **계약의 두 개를
유지**하되, 열거가 불완전했다는 사실을 기록한다. 판단 근거는 §2.1이다.

### 2.1 이번에 새로 얻은 내용 기반 근거 (정적, 게임 0회)

probe가 원본 save entry `0x440C20`의 페이로드 **호출 순서 50개**를 순서대로 뽑았다:
스택 헤더 `0x40` → literal 블록 17개 → **가변 map layer 28개** → literal 3개 →
bulk `fwrite(0x892410, 0xE397C)` → literal 1개 → 로스터 `0x40F4B0`.

- `map_bounds_precede_layers=true`, `bulk_follows_layers=true`, `layer_calls=28`.
- 첫 layer 앞의 **고정 바이트는 22,978**이고, 그 안에서 map block `0xB3DDA8`(176 B)은
  파일 오프셋 **70**에서 시작한다. 승인 주소 `0xB3DE34`/`0xB3DE36`은 그 블록의
  `+0x8C`/`+0x8E`이므로 폭/높이는 파일 오프셋 **210 / 212**로 유도된다.
- 그 유도된 오프셋을 네 fixture에 적용한 결과(2바이트씩만 읽음):
  save000 **180×180**, save006 **180×180**, save011 **100×100**, save012 **100×100**.
  전부 `runtime_env.py`의 선언된 가드 범위 `1..180` 안이다.
- 이는 독립적으로 얻은 크기 산술과 일치한다: 같은 지도 쌍의 파일 크기 차이가
  **유닛 레코드 `0x758`의 정수배**다 — `save006-save000 = 344,040 = 183×0x758`,
  `save012-save011 = 3,760 = 2×0x758`. 다른 지도 쌍은 정수배가 아니다(면적이 다르므로 정합).

**따라서 save000과 save006은 같은 180×180 지도이고 save006이 유닛 레코드 183개만큼 크다.**
이 두 사실(오프셋 유도 + 크기 산술)이 서로를 교차검증한다. 다만 **두 값 모두 절대 유닛 수가
아니라 차이**이며, 이것만으로 fixture를 CONFIRMED 선택했다고 쓰지 않는다.

이 tier의 **잠정 선호는 save000**(같은 지도에서 레코드 183개 적음 → 장면 서명과 로드 시간이
작음)이지만, §7 카드가 절대 수치를 내기 전에는 선택을 확정하지 않는다.

## 3. 항목2 실제 하네스 연결 — REJECT

기계 사실: `tools/runtime_env.py`에 **save 파일 참조 0개, PS35 참조 0개**
(probe `harness.save_load_references=0`, `ps35_references=0`).
현재 경로는 `fixture.kind = "new private copy; default two-player random game"`
한 가지뿐이고, 실제 입력 체인은 과거 evidence의 9개 input에서
`menu → multiplayer_mode_normalize → solo_mode_setup → connection_confirm_setup →
player0_ready_auto → lobby_start_setup` 순이다
(`local/runtime/20260912_022912_3830565_0/output/g1_a/evidence.json`).

저장 로드 경로는 이 체인을 **대체**한다: PS9 → 불러오기 → PS35 → 슬롯 선택 → PS3.
즉 PS7(임의게임)과 PS5(로비)를 거치지 않는다. 그 결과 다음이 **그대로는 성립하지 않는다**:

- `_g1_start_endpoint_pass`(`tools/runtime_env.py:3032-3036`)의 `before_ps == 5 and after ps == 3`
  선언 PASS 규칙 — 로드 경로에는 PS5가 없다(probe `harness.start_endpoint_rule=true`로 현행 확인).
- `G1_SETUP_POINTS` 4개 좌표와 `G1_SELECTOR_STATE_ADDRESSES`, `G1_COMMITTED_MODE_ADDRESS`,
  `G1_READY_STATE_BASE_ADDRESS` 기반의 selector/ready 검사 전부.
- `g1_baseline`/`g1_presentation_trace`의 `_wait_state(... ps == 7 / == 5 ...)` 단계들.

계약이 요구한 "수정할 함수/테스트와 승인 읽기 주소 명시"는 **어디에도 제출되지 않았다.**
게다가 위 PASS 규칙은 선언된 계약이므로, 로드 경로를 넣으려면 **PASS 규칙 계열을 건드리게
된다** — 그것은 work tier가 임의로 할 수 없고 middle로 반환해야 하는 항목이다
(lap283 계약 work handoff의 명시 조건). 이 순서 문제 때문에 지금 하네스 구현을 열지 않는다.

## 4. 항목4 tick — REJECT, 그리고 순환 의존의 명문화

**사실.** tick 주소 `0x008924B8`은 bulk 블록 `0x892410 + 0xE397C` 안의 `+0xA8`이다
(probe `tick.inside_bulk_block=true`). 따라서 **저장 파일은 tick을 보존하고, 같은 save에서
출발한 두 run은 load 직후 같은 tick을 가져야 한다** — 랜덤 새 게임 경로보다 강한 조건이다.

**관측.** PS3에 도달한 과거 run 8건의 `scene.tick`은 **6이 7건, 7이 1건**
(probe `tick.observed_ps3_ticks`). 이 값은 게임의 결정성이 아니라 `_wait_state`가
`tick > 0`을 처음 관측한 폴링 시점의 산물이다. **그러므로 이 분포에서 허용오차 숫자를
끌어내면 안 된다.** lap277 §3.1이 delta 규칙만 두고 숫자를 유보한 판단은 옳았다.

**순환 의존(이번에 명문화).** 계약은 "tick 오차 근거 없으면 runtime 예산 요청 불가"라고
쓰는데, 로드 경로의 tick 근거는 **로드 경로를 한 번 실행해야만** 얻어진다. 현재 문서군은
이 순환을 풀 규칙을 갖고 있지 않다.

**이 tier의 제안(집행 아님, 상위 Astra 결재 대상).** 원본↔원본 **연구 쌍은 PASS 게이트가
아니므로**, 그 쌍에 한해 tick을 **허용오차 없는 report-only**로 기록한다: 두 run의
scene snapshot/각 stage before·after tick을 그대로 적고 delta를 계산해 보고만 한다.
허용오차 확정은 그 데이터가 생긴 **뒤에** 상위가 한다. 이 제안은 lap277 §3.1의 delta 규칙도
comparator PASS 규칙도 바꾸지 않는다. 상위가 거부하면 항목4는 blocker로 남는다.

## 5. 항목5 실행 봉투 — REJECT

**이미 고정된 것.** `prepare()`가 원본 SHA 검증(:534)·사설 전체 복사(:530)·전용 win32
prefix(:551)·전용 Xvfb(:563)·지원 DLL 해시(:537)·manifest를 만든다. `g1_baseline`은
timeout을 **1~90초로 강제**하고(:3283, probe `harness.g1_baseline_timeout_cap=90`),
화면을 `1600x1200x24`로 고정하며, 사용하지 않은 prefix/output만 받는다(:3292-3293).
과거 성공 run의 실제 소요는 **8.4 / 8.4 / 8.5 / 8.5 / 8.9 / 19.1 초**이고 실패 run은 90초
상한에 걸렸다(probe `tick.observed_ps3_ticks`의 `elapsed_seconds`).

**빠진 것.** (a) 로드 경로의 실제 명령과 클릭 시퀀스, (b) 180×180·3MB save의 로드가 90초
상한 안에 드는지, (c) 사설 복사본에 두 save가 모두 있을 때 어느 것을 고르는 절차,
(d) PS5에 도달하지 않는 run의 수집/flush/종료 절차(현 flush는 stage 단위로 묶여 있다),
(e) run별/총 wall-clock 예산. 다섯 항목 전부 미제출이므로 봉투는 성립하지 않는다.

## 6. 항목6 실패 보존 — ACCEPT-WITH-CONDITION

기존 기구가 계약의 네 요구를 이미 만족한다: `_new_run`이 run별 고유 디렉터리를 만들고
(`tools/runtime_env.py:370`), `prepare()`는 실패해도 `prepare_failure.json`을 남기고 실행
디렉터리를 지우지 않으며(:614-622), `g1_baseline`은 재사용된 prefix/output을 거부하고(:3292-3293),
`_prefix_pids`/`_owned_runtime_process_pids`(:820, :711)는 자기 소유 PID만 다루며,
manifest가 원본·지원 DLL 해시를 전후 대조 가능하게 남긴다.

**조건 1건:** 로드 경로는 **PS35에 도달했으나 PS3에 이르지 못하는** 새 실패 모드를 만든다.
현재 evidence 스키마에는 그 상태의 보존 형태가 없다. 실행 전에 이 실패 모드의 기록 필드를
선언해야 한다. 선언 없이 실행하면 실패가 "결측"으로 흘러 (B)의 UNKNOWN 규칙을 오염시킨다.

## 7. work 인계 — 카드 한 장 (offline, 실행 예산 0)

**제목: 저장 파일 바이트 레이아웃 모델의 정적 유도와 네 fixture 대조 검증.**
수행 tier는 work(Luna/high 또는 Sonnet5/high) **새 세션**. middle/상위가 대신 구현하지 않는다.

**할 일.**
1. 원본에서 28개 layer serializer 각각의 **원소 바이트 폭**을 정적으로 읽는다
   (첫 serializer `0x42A920`이 `WORD[ecx+0x8C] × WORD[ecx+0x8E]`를 `imul`해 원소 수를 만드는
   것은 lap280이 이미 확인했다). 폭을 읽을 수 없는 layer는 UNKNOWN으로 남긴다.
2. 순서 모델을 만든다: 헤더 `0x40` → literal 17 → layer 28(폭×면적) → literal 3 → bulk
   `0xE397C` → literal 1 → 로스터(존재 슬롯당 `0x758`).
3. **검증식(이 카드의 합격 기준):** 모델이 예측한 파일 크기가
   save000=3,093,902 / save006=3,437,942 / save011=1,982,062 / save012=1,985,822와
   **네 개 모두 정확히 일치**하는가. 일치하면 로스터 개수 n이 각 파일마다 유일하게 풀린다.
4. 일치할 때만, bulk 블록 안의 PlayerStruct 8개(`0x956770 + owner*0x3ABC`, nation=`+0x00`)를
   파일 오프셋으로 환산해 save000/save006의 **nation/활성 구성과 절대 유닛 수**를 기록한다.
   그 수치가 §2의 fixture 선택 근거가 된다.

**경계.**
- 게임/Wine/Xvfb/Stage B/원본 재실행/PNG **0**. 원본 트리 쓰기 0. 메모리 쓰기 0.
- comparator/producer/회귀/테스트/PASS 규칙/slot 강등 규칙 **변경 금지**. 하네스 수정 금지.
- lap277 §4의 "저장 포맷 **추측** 파싱 금지"는 유효하다. 이 카드가 허용하는 것은
  열거된 serializer에서 **유도하고 파일 크기로 반증 가능한** 파싱뿐이다.
  **예측이 한 파일이라도 틀리면 상수를 맞추지 말고 모델을 버리고 blocker로 반환한다.**
  이것이 baseline을 고쳐 통과시키지 않는다는 계약의 이 카드 버전이다.
- 최대 60분 또는 실패 가설 2회. **research blocker도 합격 산출물이다.**
- 결과는 다음 새 middle이 독립 검수한다. 자기 승인 금지.

**이 카드 다음(지금 열지 않음).** 타이틀 화면의 불러오기 좌표. 좌표가 없으면 하네스 로드
경로를 쓸 수 없는데, 좌표 확보는 게임 실행 또는 과거 타이틀 스크린샷 분석을 요구한다.
후자는 offline이지만 이번 카드와 다른 가설이므로 한 바퀴 한 가지 규칙에 따라 분리한다.

## 8. 상위(Astra) 큐 — 이 tier의 권한 밖

1. §4의 tick report-only 제안 승인 여부. 거부 시 항목4는 blocker로 유지된다.
2. 로드 경로가 PS5→PS3 선언 endpoint 규칙을 우회한다는 §3의 구조 문제. 규칙을 로드
   경로용으로 확장할지, 로드 경로를 별도 evidence 종류로 둘지는 상위 설계 결정이다.
3. 계약의 fixture 열거에 save011/012가 빠진 것(§2)의 처리.

## 9. 이 판정이 아닌 것

제품 G1 합격, Stage B 허가, runtime 쌍 예산 승인, 마일스톤 종료, G2~G4 전환이 **아니다**.
`make check` 292 passed와 probe exit0은 계획 승인도 제품 검증도 아니다.
R17/R31 금지, R29 범위 승인 거부, R30 M11 생존, R6-B-R2 미결, WM_CLOSE 결함,
나머지 offline 8건 주차, G3 저장 포맷 블로커는 전부 이전 판정 그대로 유효하다.

---

## 10. lap298 middle — lap297 Astra 세 결정 판정과 load UI 근거

2026-09-12 / Claude Code claude-opus-5 / high / 중간계획·컨펌. 게임 실행 0, 구현 0.
근거 probe `docs/history/laps/probes/20260912_lap298_middle_title_load_ui_probe.py`
(`1d4f5d7b…6e996e5c`), 보고 `logs/lap298/title_load_ui_probe.json`
(`584e06e6…443e909a`, exit0, `failures` 0, stderr 0 B).
이 절은 §7의 "이 카드 다음(지금 열지 않음) — 과거 타이틀 스크린샷 분석" 가설을 연 것이며
새 문서 계보를 만들지 않는다(lap297 Astra 요구).

### 10.1 lap297 상위 결정 세 가지 — 판정

| 결정 | 판정 | 이유 |
|---|---|---|
| 1 tick report-only 채택 | **ACCEPT** | §4가 제안한 문안과 일치하고 제품 규칙을 건드리지 않는다 |
| 2 load 연구를 별도 evidence 종류로 | **ACCEPT** | §3이 지목한 endpoint 우회 문제를 확장 대신 분리로 푼다 |
| 3 fixture 후보 save000/save006 유지 | **ACCEPT-WITH-CORRECTION** | 유지는 옳으나 "하나를 확정"은 아직 불가 |

**결정1 근거.** Astra 문안은 §4의 제안(허용오차 없는 원시 tick·delta report-only, 확정은
데이터 이후 상위가)을 축소·확대 없이 채택했다. lap277 §3.1의 delta 규칙도 comparator PASS도
바뀌지 않는다. §4가 명문화한 순환 의존은 **연구 관측을 제품 게이트에서 뺀 것으로 해소**되며,
이는 tick 숫자를 추측한 것이 아니다. 따라서 §0 표의 항목4 REJECT는 이 결정으로 **철회**한다.
단 철회 범위는 "연구 쌍에 한한 tick 입력 요구"뿐이고, 제품 S1의 (A)+(B)는 그대로다.

**결정2 근거.** §3은 로드 경로가 선언된 PS5→PS3 endpoint를 우회한다는 구조 문제를 남겼다.
기존 endpoint/producer/comparator/overall PASS를 넓히면 제품 판정의 의미가 오염된다.
별도 evidence 종류는 그 오염을 만들지 않는 유일한 선택지다. ACCEPT.
**조건(§6의 조건 1건을 여기로 승계):** PS35 도달 후 PS3 미도달 실패 모드의 기록 필드를
실행 전에 선언해야 한다. 이번 probe가 `runtime_env.py`의 PS 대기값이 여전히
**{3,5,7,9}뿐이고 PS35 참조 0건**임을 재측정했다(`harness_load_path`). 선언은 미완료다.

**결정3 정정.** save000/save006 유지에 동의한다(두 파일 모두 `prepare()` 복사 원본에 있고
SHA가 §2 표와 재계산 일치: `1c703551…629e719da` / `616b7997…9289a0d064`). 그러나
"middle이 하나를 확정한다"는 **이번에 불가**다. 선택 근거가 되기로 한 §7 카드 4항의
nation/활성 구성/절대 유닛 수는 lap286~289에서 산출되지 않았고, 네 fixture 공통 사실은
"owner id ≥8 record 0개"뿐이다. **선택을 미확정으로 남기는 것이 근거 없는 확정보다 옳다.**

### 10.2 새로 확보한 근거 — 타이틀 메뉴의 불러오기 좌표

§7이 "게임 실행 또는 과거 타이틀 스크린샷 분석"을 요구한 좌표를 **후자로 얻었다.**

- **좌표계가 동일함을 먼저 증명.** `_capture_screenshot`은 `scrot -a content_crop`으로
  잘라 저장하고(`capture_uses_crop=true`), 모든 클릭은 `content_crop + (x, y)`다
  (`harness_click_literal_present=true`). content 창은 정확히 800×600으로 게이트된다
  (`content_crop_gate_800x600=true`). 따라서 **캡처 픽셀 좌표 = 클릭 좌표**다.
- **결정성.** 공유 캡처의 `title_before_menu` **14장 전부 단일 SHA**
  `277a0b23…9ce5b252`, 800×600. 타이틀 화면은 14 run에 걸쳐 바이트 동일하다.
- **격자.** 메뉴는 4열×2행, 셀 100×36, 열 좌변 21/134/247/360, 행 상변 488/542로 완전 규칙적.
- **앵커(반증 가능).** 하네스의 유일한 타이틀 클릭 `(184,560)`이 **정확히 한 셀**
  row2/col3이 아닌 **row2/col2**에 들어간다. `runtime_env.py:606`은 같은 클릭을
  `"title random-game click (184,560)"`라고 부르고, 그 셀을 4배 확대한
  `20260912_133000_lap298_title_r2c2_random.png`(`185869c1…f01cbd174`)의 라벨은 **임의게임**이다.
  즉 격자↔라벨 대응이 하네스 문자열로 독립 확인된다.
- **결과.** row1/col3 = **불러오기**(`20260912_133000_lap298_title_r1c3_load.png`,
  `5580e229…4da333b390`), bbox `[247,488,346,523]`, **중심 (296,505)**.
  이 좌표는 하네스가 이미 PASS로 검증한 것과 **같은 기구·같은 프레임**의 이웃 셀이다.
- **탐지기 반증력.** 셀 중심 8개가 각자 자기 셀로만 해석되고, 열 사이 간극 `(127,560)`과
  격자 위 `(184,400)`은 어느 셀에도 안 들어간다. 한 덩어리로 뭉친 탐지는 이 검사를 통과 못 한다.

### 10.3 함정 하나를 봉인한다 — 800×600 `load_screen` 캡처는 원본이 아니다

공유 캡처에 800×600짜리 로드 대화상자 PNG
`20260910_032210_d1app2r3_21_load_screen.png`(`5e95ed92…d17e5879`)가 있다. 슬롯 7칸과
`불러오기`/`돌아가기` 버튼이 보여 다음 단계 좌표처럼 읽힌다. **원본 증거가 아니다.**
그 화면의 문자열은 전부 Plan C 재현 엔진의 UI 모듈
`Syw2plus_re/plan_c/src/ui/save_load_screen.cpp`(`f2232e91…90ff41ec`)가 만든다:
`"[PLNC] "`·`"[ORIG] "` 접두와 `"저장된 정보가 없습니다."`가 그 소스에 있다(probe가 확인).
AGENTS의 "전체 재현 엔진을 이 프로젝트 지시로 가져오지 않는다"에 따라 **좌표 출처로 금지**한다.
work tier가 같은 PNG를 다시 발견할 것이므로 이 봉인을 카드에 명시해 인계한다.

**다만 연구 단서는 남는다(증거 아님).** 그 모듈은 원본 함수 `FUN_004D60B0`과
`DAT_01088B5C/5E`, 모드 코드 `0x3ED`(load)/`0x3EB`(save), 슬롯 top 오프셋
`{-0x1A,0x08,0x2A,0x4C,0x6E,0x90,0xB2}`, OK `title+0x24/+0xD7`, Cancel `title+0xBA/+0xD7`을
**인용**한다. 이는 우리 원본 EXE(`b56986e0…c9c08a8ac`)에서 **독립 재유도 가능한 주장**이며,
lap277~282가 유닛 오프셋에 쓴 경로와 같다. 주의: `0x4D60B0`은 이미지 안이지만
`0x519A0C`/`0xB3AD74`/`0x1088B5C`는 raw 파일 크기 밖이라 섹션 virtual size 또는 다른 모듈
확인이 선행돼야 한다. 재유도에 실패하면 그 값은 UNKNOWN으로 남긴다.

### 10.4 lap297 handoff 표 — 행별 판정

| 행 | 판정 | 근거 |
|---|---|---|
| 세 결정 | ACCEPT / ACCEPT / ACCEPT-WITH-CORRECTION | §10.1 |
| fixture·UI | **부분 ACCEPT** — 1차 클릭 확정, 슬롯 선택 UNKNOWN | §10.2 확정, §10.3 봉인 |
| 연구 하네스 | **REJECT** — 수정 대상 함수/기록 위치 미확정 | `save` 참조 0, PS 대기 {3,5,7,9} |
| tick | **ACCEPT** | 결정1이 §4 문안 그대로 |
| 실행 봉투 | **REJECT** | §5 (a)~(e) 중 (a)만 1단계 전진, (b)~(e) 미제출 |
| 안전·회귀 | **ACCEPT-WITH-CONDITION** | 기존 기구 충족, PS35→PS3 미도달 필드 선언 미완 |

**결론: runtime 예산 요청 없음. Stage B 0 유지.** 표 전체를 "하나의 실행 가능한 패키지"로
수용할 수 없다. 그러나 이번 바퀴는 봉투의 **첫 결측(a)을 근거 있는 값으로 줄였고**, 남은
결측을 게임 실행 없이 좁힐 수 있는 경로를 특정했다. 상위 반환이 아니라 work 카드 한 장이다.

### 10.5 work 인계 — 카드 한 장 (offline, 실행 예산 0)

**제목: 원본 EXE에서 저장/불러오기 대화상자 레이아웃의 정적 재유도.**
수행 tier는 work(Luna/high 또는 Sonnet5/high) **새 세션**. middle/상위가 대신 구현하지 않는다.

**선행 수리(먼저, 그리고 별도 검수).** lap296 §4.7.6의 두 scrape 가드 인계를 먼저 끝낸다.
lap297 Astra가 철회하지 않았고 이 카드도 철회하지 않는다.

**할 일.**
1. 우리 원본 EXE에서 `FUN_004D60B0`을 **직접** 디스어셈블해 대화상자 레이아웃을 유도한다:
   슬롯 레코드 시작 오프셋, 슬롯 수, 슬롯 rect, OK/Cancel 좌표, 모드 코드.
   Plan C 소스는 **어디를 볼지 가리키는 단서로만** 쓰고 값의 출처로 인용하지 않는다.
2. `title_x/title_y`가 스프라이트 크기에 의존하면 `yfnt/saveloadtitle.spr`(102,260 B) 헤더에서
   폭·높이를 읽어 800×600 화면 중심식에 대입한다. 읽을 수 없으면 UNKNOWN.
3. **검증식(이 카드의 합격 기준):** 유도한 좌표가 **어떤 원본 캡처와도 대조되지 않았음**을
   명시한 채, (i) 7개 슬롯 rect가 서로 겹치지 않고 (ii) 전부 800×600 안에 들고
   (iii) OK/Cancel이 어느 슬롯 rect와도 겹치지 않는지를 검사한다. 하나라도 어긋나면
   **상수를 맞추지 말고 모델을 버리고 blocker로 반환한다.**
4. §10.2의 `(296,505)`와 위 결과를 합쳐 "클릭 시퀀스 초안"을 **문서로만** 남긴다.
   하네스 수정 0. 실행 0.

**경계.**
- 게임/Wine/Xvfb/Stage B/원본 재실행/PNG **0**. 원본·참고 트리 쓰기 0.
- comparator/producer/endpoint/PASS 규칙·하네스 **변경 금지**. 새 의존성 금지.
- Plan C 값을 그대로 베껴 적으면 이 카드는 **실패**다. 독립 재유도만 산출물이다.
- 최대 60분 또는 실패 가설 2회. **research blocker도 합격 산출물이다.**
- 결과는 다음 새 middle이 독립 검수한다. 자기 승인 금지.

### 10.5.1 lap299 work 결과 — 정적 재유도 PASS, 실행·클릭은 UNKNOWN

원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`의
`FUN_004D60B0` (`0x004D60B0..0x004D656F`)을 `objdump -d -Mintel`로 직접 읽었다.
`this+0x408`이 16-byte rect 배열 시작이고, `this+0xF9C=7`, rect 폭/높이는
`0x118/0x18`, 상대 top은 `{-0x1A,0x08,0x2A,0x4C,0x6E,0x90,0xB2}`다. 같은
함수의 호출 인자는 OK `title+(0x24,0xD7)`, Cancel `title+(0xBA,0xD7)`로 재유도했다.
`0x004D6930`은 `0x3ED`와 `0x3EB`를 분기하고, `0x004D69E0`/`0x004D6A00`의
직접 호출에서 각각 `0x3EB`/`0x3ED`가 전달된다. Plan C 값은 출처로 사용하지 않았다.

읽기 전용 sprite `yfnt/saveloadtitle.spr` SHA
`7d154cdbf37dbea78c162ada870e656a039a224c5aa63ee52d86d8123c08a5c5`, 102,260 B의
첫 4개 little-endian DWORD는 `[9,320,310,1]`이다. 카드가 요구한 800×600 중심식에
대입한 title origin은 `(240,145)`이며, 산출된 7 rect는
`[260,119,540,143]`, `[260,153,540,177]`, `[260,187,540,211]`,
`[260,221,540,245]`, `[260,255,540,279]`, `[260,289,540,313]`,
`[260,323,540,347]`; OK/Cancel call point는 `(276,360)`/`(426,360)`이다.
신규 probe `docs/history/laps/probes/20260912_lap299_work_save_load_layout_probe.py`
(`5c4bbc1a…86037b77`)가 세 검증식(상호 비겹침/800×600 내/버튼-슬롯 비겹침)을
`failures=[]`로 통과시켰다. 이는 원본 캡처와 대조하지 않은 정적 후보이며, 버튼 hitbox,
슬롯 선택 결과, 로드 후 전이는 여전히 UNKNOWN이다.

실행: probe report `logs/lap299/save_load_layout_probe.json`
(`8e735a9a…76d2bb0b`), `make check` 292 passed, Ruff/compileall/mypy/CONTEXT_PASS,
`checks/safety.sh check` `SAFETY_PASS`. 게임/Wine/Xvfb/Stage B/PNG/runtime 예산 0.
lap296 review 재실행의 유일한 failure는 target probe의 stale EXPECTED_SHA
(`88d86211…` → `8a5eee47…`)이며 §4.7.6 4항이 예상한 결과다. 다음 새 middle이 이
정적 probe와 stale provenance를 독립 검수한다.

### 10.6 상위(Astra) 큐 — 이 tier의 권한 밖

1. fixture 하나를 확정할 근거(nation/활성 구성)를 얻으려면 §7 카드 4항이 미완이다.
   그 항목을 다시 열지, save000 잠정 선호를 근거 없이 유지할지는 상위 결정이다.
2. 로드 경로 별도 evidence 스키마의 승인. 필드 선언은 middle이 쓸 수 있으나 제품 evidence
   소비 경로와의 분리 규칙 확정은 상위다.
3. `0x519A0C`/`0xB3AD74`/`0x1088B5C`가 EXE 밖일 경우 어느 모듈까지 정적 조사를 허용할지.

### 10.7 이 판정이 아닌 것

제품 G1 합격, Stage B 허가, runtime 쌍 예산 승인, 마일스톤 종료, G2~G4 전환이 **아니다**.
`(296,505)`는 **클릭하면 무슨 일이 일어나는지 관측된 바 없다.** 버튼의 위치와 라벨만 확정했다.
probe exit0과 `make check`는 계획 승인도 제품 검증도 아니다. §9의 기존 금지·미결은 전부 유효하다.

## §11 lap300 middle → work handoff (저장/불러오기 레이아웃 probe 수리)

lap300 middle(Opus5/high)이 lap299 work 결과를 독립 검수한 뒤 남기는 **명시적 handoff**다.
근거 원문은 `docs/history/laps/20260912_lap300_middle_lap299_layout_review.md`,
재현 probe는 `docs/history/laps/probes/20260912_lap300_middle_lap299_layout_review_probe.py`
(SHA `718b1e4e4e99a7597dc470c4b9f980eee48d67e087397701894864bd17ea63cf`, exit0).
middle은 진단·계획·확인만 하고 아래 수정을 직접 하지 않는다. 수행 주체는 work tier
(Luna/Sonnet5/high)다. probe exit0은 계획 승인도 제품 검증도 아니다.

### 판정 요약 (상세는 lap300 기록 §1~§5)

- 결정성 ACCEPT. 상대 레이아웃 모델 ACCEPT-WITH-CORRECTION. lap296 §4.7.6 가드 ACCEPT.
- `candidate_800x600` 단일 절대 좌표표 **REJECT**. 이유는 T3 참조.

### work가 수행할 것 — `…/20260912_lap299_work_save_load_layout_probe.py` 한정

- **T1 (앵커 구멍 C1):** 슬롯0 오프셋 `-0x1A`가 어떤 disasm 앵커에도 안 걸린다. 실제 명령
  `sub    ecx,0x1a @ 0x004D6358`을 앵커 튜플에 추가한다. 슬롯 높이 `+0x18` 앵커도 함께 추가.
- **T2 (fixture 미pin C2):** `EXPECTED_SPRITE_SHA = ""`라 SHA 검사가 통째로 skip된다.
  `7d154cdbf37dbea78c162ada870e656a039a224c5aa63ee52d86d8123c08a5c5`로 pin하고, 읽기 경로를
  참조 저장소 `Syw2plus_re/Syw2plus/yfnt/`가 아니라 원본 입력 `Syw2plus/yfnt/`로 바꾼다
  (두 사본은 현재 바이트 동일이므로 수치 변화 0).
- **T3 (절대 좌표 REJECT):** 하드코딩 `SCREEN = (800, 600)`을 제거한다. 함수가 실제로 읽는 값은
  `ds:0xE5BF1C`/`ds:0xE5BF20`(그래픽 객체 `0xE5BF18`의 필드 +4/+8)이고 .text 전수 writer는
  `FUN_00431AB0`의 지도 표면 덮어쓰기(0x431B79/0x431B7F)와 그 성공 exit의 무조건 640×480 복원
  (0x4324B8/0x4324C2) 두 곳뿐이다. 모드 표 `FUN_004644A0`은 디스플레이 초기화에서만 불린다.
  probe는 (a) writer를 보고서에 열거하고 (b) 후보 A(타이틀 진입, 800×600)와 후보 B(인게임 진입,
  640×480)를 **각각 전제와 함께** 출력해야 한다. 단일 좌표표를 다시 내지 않는다.
- **T4:** `logs/lap299/save_load_layout_probe.json`은 삭제하지 않고 새 경로에 새 report를 낸다.
  기존 lap299 기록의 수치와 문구는 정정하지 않고 보존한다(provenance).

### work가 하지 않을 것

게임/Wine/Xvfb 실행, 800×600 또는 640×480 슬롯 클릭, save/load 실행, Stage B, runtime 예산 요청,
PNG 신규 생성, 원본/참고 저장소 쓰기, `tools/runtime_env.py`·`patches/` 수정, 상수 신규 승격,
lap296 review probe의 `EXPECTED_SHA` 재pin(= W3, Astra/사용자 결정 대기), G1 PASS 승격.

### 미결로 남기는 것

- 어느 후보가 클릭 시점에 성립하는지는 **offline 결정 불가**. `0xE5BF1C`/`0xE5BF20`의 관측값이
  필요하며 실행을 요구한다. 이 handoff는 그 실행을 허가하지 않는다.
- **W3:** lap296 review probe는 자기 stale pin 때문에 영구 exit1이라 회귀 게이트로 쓸 수 없다.
- **알려진 사각(유지):** `type`/`owner` 가드는 리터럴 소멸/개명만 잡고 값 드리프트는 못 잡는다.

## §12 lap302 middle → work handoff (writer 범위·후보 집합 교정)

lap302 middle(Claude Code `claude-opus-5`/high)이 lap301 work 결과를 독립 검수한 뒤 남기는
**명시적 handoff**다. 근거 원문은 `docs/history/laps/20260912_lap302_middle_lap301_writer_scope_review.md`,
재현 probe는 `docs/history/laps/probes/20260912_lap302_middle_lap301_writer_scope_review_probe.py`
(SHA `b5343ec41713e14ecf4e2b99ebe2903786d350367b86daf6411cb7d487ebd0a6`, exit0, `failures=[]`),
report는 `logs/lap302/middle_writer_scope_review.json`(SHA `5190920f…8940d2`).
middle은 진단·계획·확인만 하고 아래 수정을 직접 하지 않는다. 수행 주체는 work tier
(Luna/Sonnet5/high)다. probe exit0은 계획 승인도 제품 검증도 아니다.

### 판정 요약 (상세는 lap302 기록 §1~§9)

- T1/T2/T4(로그 보존) **ACCEPT**. 상대 레이아웃 모델 **ACCEPT**(중심식 정정 2건, 수치 영향 0).
- T3 **REVISE** 2건: writer "전수 4개"는 절대주소 쓰기만 센 것이고, 후보를 A/B 2개로 좁힐 수 없다.
- T4 소스 provenance **ACCEPT-WITH-CORRECTION**: 수리 전 소스 소실 + report의 lap 라벨 오기.
- 절대 좌표표는 lap300에 이어 **REJECT 유지**이며, 이제 lap301의 2후보 쌍에도 확장 적용된다.

### work가 수행할 것 — lap301 probe 한정, 실행 예산 0

- **U1 (writer 열거 확장):** 정규식을 절대주소 `ds:0xE5BF1C/20` 쓰기에 한정하지 말고,
  `FUN_004644A0`의 `this` 상대 쓰기도 포함해 열거한다. 최소 대상: `0x4644C8`/`0x4644DB`/
  `0x4644EB`/`0x464502`/`0x464512`/`0x464529`/`0x464539`/`0x464550`의 `[esi+0x4]`와 짝이 되는
  `[esi+0x8]`. `this=0xE5BF18` 근거는 호출 사슬 `0x423D52 → 0x423D63 → 0x4643BE → 0x4643C0`을
  앵커로 박아 넣는다. `unexpected screen global writer count` 게이트가 간접 경로에 대해
  fail-open이라는 사실을 report 필드로 남긴다.
- **U2 (후보 집합 교정):** `candidates`를 A/B 2개에서 도달 가능한 **5해상도**
  (320×200, 640×480, 800×600, 1024×768, 1280×1024) + `0x4324B8` 사후 640×480 복원 +
  `0x431B79` 지도 표면 쓰기로 넓히고, 각각 전제를 붙인다. `320x200`에서
  `slot_rects_inside_screen`이 **false**(origin `(0,-55)`, 슬롯0 `[20,-81,300,-57]`)라는 결과를
  삭제하거나 검사에서 빼지 말고 그대로 보고한다.
- **U3 (중심식 충실도):** `(screen-dialog)//2` 대신 실제 명령 열
  `sar(screen,1) - sar(dialog,1)`을 구현하고, 두 식이 현재 5해상도에서 동일함을 report에 기록한다.
  앵커는 구간 내 문자열 존재가 아니라 **주소 고정**으로 단언한다(`add eax,0x18`은 3회,
  `add ecx,0x18`은 2회 등장하므로 문자열 존재만으로는 드리프트를 못 잡는다).
- **U4 (provenance 표기):** 새 report의 `"lap"`/`"probe"` 필드가 실제 lap과 파일명을 가리키게
  고친다. **과거 lap299/lap300/lap301 기록의 문구와 수치는 정정하지 않는다.** 앞으로는 probe를
  제자리에서 덮어쓰지 말고 새 lap 이름의 파일로 복사한 뒤 고쳐 수리 전 소스를 남긴다.
- **U5 (새 stale pin 금지):** lap302 probe의 방식을 따른다 — 뒤 바퀴가 고칠 산출물의 SHA를
  단언하지 말고 기록만 하며, 결정성은 같은 세션 2회 실행 비교로 단언한다.

### work가 하지 않을 것

게임/Wine/Xvfb 실행, 어떤 해상도에서든 슬롯/버튼 클릭, save/load 실행, Stage B, runtime 예산 요청,
PNG 신규 생성, 원본/참고 저장소 쓰기, `tools/runtime_env.py`·`patches/` 수정, 상수 신규 승격,
lap296 review probe의 `EXPECTED_SHA` 재pin(= W3, Astra/사용자 결정 대기), 과거 lap 기록 수정,
어느 한 해상도를 제품 좌표로 승격, G1 PASS 승격.

### 미결로 남기는 것 (이 tier의 권한 밖)

- 다이얼로그 구성 시점(`0x4D6312`)에 어느 해상도가 살아 있는지는 **offline 결정 불가**. 관측
  대상은 화면 전역보다 `ds:0x1088B5C`/`0x1088B5E`의 origin 두 워드가 더 직접적이다. 이 handoff는
  그 관측을 허가하지 않는다 — 실행 예산은 Astra/사용자 결정이다.
- `FUN_004644A0`에 도달하는 모드 인자의 **저장 출처**(`0x00423D4x`에서 흘러드는 값, 입력 중 하나가
  `ds:0x4ED810`)는 이번에 확정하지 않았다. 좁은 다음 정적 probe 후보.
- **W3:** lap296 review probe의 자기 stale pin은 여전히 영구 exit1이라 회귀 게이트로 쓸 수 없다.
- **알려진 사각(유지):** `type`/`owner` 가드는 리터럴 소멸/개명만 잡고 값 드리프트는 못 잡는다.


## §13 lap321 Astra — F1 이후 실행 봉투 문서 검토로 복귀

상태: 상위 방향 RECORDED, middle 수용 PENDING. 실제 역할 Codex gpt-6-astra/high.
사용자 표기 lap320과 달리 읽기 전용 `loop/.lap_counter`는 321이다. 마일스톤 종료/이동 없음.
근거: lap317 결정4, lap320 middle F1 ACCEPT, lap321 fresh 재실행(stdout SHA
`3d0022b88d694fd1a17c76073d47622c796bab2be188a90d83d325f0a24f60da`, failures=[]).
재실행은 기존 검수의 재현 확인이며 새 독립 알고리즘 검수나 제품 실행이 아니다.

### 상위 선택과 범위

1. M1/G1 안에서 §5(a)~(e)와 §10.4의 미제출 입력을 **문서로 심사하는 분기**를 선택한다.
   F1 종료 조건이 충족됐으므로 같은 R2 수치의 추가 증명은 새 반증 없이는 열지 않는다.
2. N4는 FAIL JSON이 빠지는 알려진 진단 결함으로 보존한다. 현재 정상 입력의 F1 수치에는
   영향이 없고 선택한 문서 심사의 선행 실행기도 아니므로 별도 수리 카드를 지금 열지 않는다.
   그 probe를 새 입력 처리/실행 게이트로 채택하려면 middle이 N4 수리를 선행 조건으로 지정한다.
3. W3 재pin은 승인하지 않는다. stale pin 실패는 역사 근거로 유지하고 현행 게이트로 재사용하지
   않는다. 이것은 필수 실패를 면제하거나 기존 pin을 바꿔 통과시키는 결정이 아니다.
4. runtime/load 연구는 §10.1의 별도 evidence 종류와 tick report-only를 유지한다.
   제품 endpoint PS5→PS3, S1 (A)+(B), comparator/producer/PASS 규칙은 그대로다.
   연구 문서의 수용도 runtime 실행 허가와 별개다. 이번 runtime/Stage B 예산은 **0**이다.

### middle 인계 — 문서 심사 한 건

입력은 이 문서 §2~§7·§10.1~§10.4, lap320 검수 기록과 STATUS의 미결이다.
각 행에 **근거 파일/절·확정 사실·UNKNOWN·수용/반려·반려 해소 조건**을 적는다.
아래는 제출 요구이며 측정됐다고 주장하는 값이 아니다.

| 제출 행 | middle이 결정할 내용 | 거부 조건 |
|---|---|---|
| fixture | save000/save006의 SHA·복사 출처와 §7.4 nation/활성 구성/절대 수의 산출 여부를 구분; 하나 선택의 충분 근거 판정 | 낮은 파일 크기 또는 owner≥8 부재만으로 활성 구성 확정 |
| §5(a),(c) 입력 | 타이틀 (296,505)의 위치 근거와 미관측 클릭 결과를 분리; 대화상자 origin·슬롯 선택·로드 전이의 필요한 관측값과 순서 명시 | 후보 A/B를 실제 절대 좌표로 승격, Plan C 캡처 사용, 추측 클릭 |
| 하네스 경계 | 별도 연구 evidence 생산 위치와 기존 제품 소비 경로의 분리, 수정할 함수·테스트 후보를 문서로 특정 | 기존 PS5→PS3를 PS35→PS3로 넓혀 같은 PASS에 편입 |
| §5(b),(e) 예산 | 기존 90초 상한을 보존하는 run별 단계/총 wall-clock 제안; 준비·수집·종료 시간을 구분 | 과거 새 게임 소요를 save 로드 실측으로 사용, 자동 연장/무변경 재시도 |
| §5(d),§6 실패 | PS35 미도달 및 PS35 도달/PS3 미도달, timeout, 수집 실패별 원시 PS/tick·시간·run ID·소유 PID·입력·오류·flush 산출물 필드와 종료 방식 | 실패를 결측/skip/PASS로 바꿈, 다른 세션 정리, 로그 덮어쓰기 |
| 수용 패키지 | 위 행별 판정과 정확한 후속 work 파일 범위·반증 가능한 검사·중단 조건 | exit0/Fast PASS만으로 계획 승인, 구현/실행 자동 착수 |

정적 원문만으로 해소할 수 없는 것은 UNKNOWN과 **최소 필요한 관측**을 적고 상위 반환한다.
특히 map↔dialog 실제 순서·구성 시점 전역값·hitbox·로드 성공은 현재 미관측이다.
이 미확정을 정적 CFG 연구의 무기한 재개 사유로 쓰지 않는다. 실행이 꼭 필요하면 middle은
관측만 수행할 최소 봉투와 기존 금지 중 변경이 필요한 항목을 제출하며, 허가 전 집행하지 않는다.

### work 분리·검증·중단

이번에는 work 실행 카드를 활성화하지 않는다. middle 수용 후에만 별도 새 Luna/Sonnet5/high
세션에 한 가지 변경과 정확한 파일 범위를 인계하고, 결과는 다음 새 middle이 독립 검수한다.
기존 tools/patches/probe/test/EXE/DLL/assets/pin/baseline/golden 수정과 게임/Wine/Xvfb/PNG/클릭은 0.
문서 검증: 기존 lap320 보고서 재현·입력 SHA 확인, make check, safety, STATUS≤130줄·Blockers 1개.
필수 게이트 예상 밖 실패, 구현 근거 불명확/충돌, 마일스톤 경계면 보존 후 ESCALATE_SOL로 종료한다.
이번에는 로드 절차/실행 근거 미확정 때문에 **문서 인계와 ESCALATE_SOL만 남기고 종료**한다.
표식 이름은 provider 지정이 아니다. MODEL_ROUTING의 현재 middle=Opus5/high와 상위 지시의
Sol/Opus5 허용 차이는 인계 세션이 유효 지시·실제 모델을 기록하며 조용히 폴백하지 않는다.
현재 다음 작업은 STATUS에만 둔다. 본 절은 lap321 결정·수용 기준의 영구 기록이다.

## §14 lap322 middle — §13 제출 여섯 행의 문서 심사 판정

2026-09-12 / Claude Code `claude-opus-5` / high / middle tier(진단·계획·컨펌). 게임 구현 0.
수신: §13(lap321 Astra)의 middle 인계 표와 `loop/ESCALATE_SOL`(lap321, `761275fb…f01297dd`).
게임/Wine/Xvfb/Stage B/원본 재실행/PNG/클릭 **0회**, 원본·참고 트리 쓰기 0,
comparator/producer/endpoint/회귀/테스트/PASS 규칙·하네스·pin·baseline·golden **무변경**.
이 절은 제품 G1 합격·runtime 예산 승인·Stage B 허가·마일스톤 종료가 **아니다**.

근거 probe(신규, 읽기 전용, 재실행 가능):
`docs/history/laps/probes/20260912_lap322_middle_runtime_envelope_review_probe.py`
(`14dd9768…94b051a3`) → `logs/lap322/runtime_envelope_review.json`
(`bcf4f0a9…6f7f3c3674`, exit0, **failures=[]**, stderr 0 B, 연속 2회 stdout 동일).
이 probe는 이전 lap probe를 import하지 않고 전부 재유도한다. 따라서 아래 정정 2건은
표기 차이가 아니라 **독립 측정과 기존 측정의 실제 불일치**다.

### 14.0 판정 요약

| 제출 행 | 판정 | 한 줄 이유 |
|---|---|---|
| fixture | **REJECT** | §7 카드 4항(nation/활성 구성/절대 수) 미산출. 남은 공통 사실은 §13이 금지한 근거뿐 |
| §5(a),(c) 입력 | **(a) 부분 ACCEPT / (c) REJECT** | 위치·라벨은 재현됐고 클릭 결과는 미관측. 슬롯·전이는 정적 지렛대 소진 |
| 하네스 경계 | **REJECT** | 수정 대상 함수·연구 evidence 기록 위치 미지정. 측정 가드 fail-open 1건 동반 |
| §5(b),(e) 예산 | **REJECT** | 3 MB 로드 소요 측정치 0. 단, 예산 기구는 이미 있고 새로 만들 것이 아니다 |
| §5(d),§6 실패 | **ACCEPT-WITH-CONDITION** | 기구 충분, 필드 선언 미완. §5(d)의 flush 서술은 과소 표기 |
| 수용 패키지 | **REJECT(패키지)** | 입력 3행이 REJECT인 동안 패키지 수용 불가. runtime/Stage B 예산 요청 **없음** |

**결론: runtime 예산 요청 없음. Stage B 0 유지. work 실행 카드 활성화 0.**
상위 반환은 §14.7의 **관측 1건짜리 최소 봉투**뿐이며 허가 전 집행하지 않는다.

### 14.1 fixture — REJECT

**이 바퀴가 직접 재계산한 확정 사실.**

| 파일 | 크기 | SHA256 |
|---|---|---|
| `Syw2plus/save/save000.dat` | 3,093,902 B | `1c703551…629e719da` |
| `Syw2plus/save/save006.dat` | 3,437,942 B | `616b7997…9289a0d064` |
| `local/fixtures/20260910/save011.dat` | 1,982,062 B | probe `fixtures.save011` |
| `local/fixtures/20260910/save012.dat` | 1,985,822 B | probe `fixtures.save012` |

§2 표와 일치한다. 두 후보가 `prepare()` 복사 원본에 함께 들어간다는 §2 결론도 유지한다.

**UNKNOWN.** §7 카드 4항이 요구한 nation/활성 구성/절대 유닛 수는 lap286~289에서 **산출되지
않았다.** STATUS가 보존하는 lap286 한계가 그 이유를 설명한다: 네 fixture가 전부 정사각·짝수
변이라 오프셋 210/212 배정과 halving layer `((w/2)*h)/2` 대 `(w*h)//4`를 구분하지 못한다.
그 구분이 서기 전에는 PlayerStruct를 파일 오프셋으로 환산할 수 없고, 환산 없이는 4항이 성립하지 않는다.

**판정 REJECT.** 지금 하나를 고르려면 파일 크기 또는 "owner id ≥8 record 0개"에 기대야 하는데,
그 둘은 §13이 명시한 **거부 조건 그 자체**다. 근거 없는 확정보다 미확정 유지가 옳다(§10.1 결정3 재확인).

**반려 해소 조건.** (i) 비정사각 또는 홀수 변 fixture 하나로 layer 폭 배정을 반증 가능하게
가른 뒤 4항을 산출하거나, (ii) 모델이 예측한 파일 오프셋에서 네 fixture 전부의 nation을 읽어
크기 예측과 동시에 맞힌다. 한 파일이라도 틀리면 상수를 맞추지 말고 모델을 버린다(§7 경계 유지).

### 14.2 §5(a) 1차 클릭 — 부분 ACCEPT (위치·라벨 한정)

**이 바퀴가 재현한 것.** 공유 캡처 `*title_before_menu*.png` **14장**, 단일 SHA
`277a0b23…9ce5b252`, PNG IHDR 직접 파싱으로 **전부 800×600**. 타이틀 화면의 run 간 결정성은
독립 재현됐다. 하네스 앵커 `(184,560)`은 `tools/runtime_env.py`(`dd2ad043…2ac8500190`)의
**7개 줄**(606, 3416, 3428, 3890, 4121, 4206, 4208)에 있고 3416/3882는 `content_crop` 오프셋을
더해 클릭한다 → §10.2의 "캡처 픽셀 = 클릭 좌표" 전제가 현재 트리에서 성립한다.

**하네스 미배선 확인.** `(296,505)`는 `runtime_env.py`에 **0회** 등장한다(probe
`load_click_296_505_present=false`). 이 좌표는 지금도 **문서 전용 후보**이며 제품 경로에
들어가 있지 않다. probe는 이것이 배선되면 FAIL하도록 단언을 걸어 두었다.

**ACCEPT 범위는 §10.7 그대로다.** 위치와 라벨만 확정이고 **클릭하면 무슨 일이 일어나는지는
관측된 바 없다.** 이 부분 ACCEPT는 클릭 허가가 아니다.

### 14.3 §5(c) 대화상자 origin·슬롯 선택·로드 전이 — REJECT

**이 바퀴의 새 확정(정적, 게임 0회).** 읽기 전용 `Syw2plus/yfnt/saveloadtitle.spr`
102,260 B `7d154cdb…c08a5c5`, 선두 4 DWORD `[9, 320, 310, 1]`을 직접 읽었다. 같은 중심식을
두 화면 전역 쌍에 대입하면:

- `((800-320)//2, (600-310)//2)` = **(240,145)** = lap301 후보 **A**
- `((640-320)//2, (480-310)//2)` = **(160,85)** = lap301 후보 **B**

**따라서 후보 A/B는 서로 다른 두 가설이 아니라 하나의 식을 두 전역값에 대입한 결과다.**
A/B 선택은 곧 **구성 시점 `ds:0xE5BF1C/0xE5BF20`의 값**을 묻는 것이고, 그 값은 lap312가
성공 경로의 **마지막 직접 쓰기를 640×480 reset**으로 확정한 바로 그 미결과 같은 대상이다
(읽는 시점은 클릭이 아니라 구성 `0x4D6312`). lap308~316이 map↔dialog 실제 순서를 좁히지
못했으므로 이 값은 실행 없이 결정되지 않는다.

**판정 REJECT.** 슬롯 선택 UI·로드 전이는 UNKNOWN을 유지하고, 후보 A의 정적 우세를 절대
좌표로 승격하지 않는다(§13 거부 조건). Plan C 캡처·소스를 좌표 출처로 쓰는 것은 §10.3 봉인 유지.

**정적 지렛대 소진 선언.** 이 tier는 이 질문을 더 좁힐 **남은 정적 수단을 특정하지 못했다.**
호출 31개를 fall-through로 두는 한(N2) cross-function writer와 실행 순서는 원리적으로 미증명이고,
lap310의 절대 dword 스캔은 포인터 테이블 경유 근거를 이미 0건으로 닫았다. 이것은 정적 CFG 연구를
무기한 재개할 사유가 **아니라**, §14.7 관측을 상위에 올리는 사유다(§13 말미 지시 준수).

### 14.4 하네스 경계 — REJECT, 그리고 측정 가드 정정 1건(N6)

**확정.** `tools/runtime_env.py`에 save 파일 참조 **0**, 리터럴 `35` **0회**
(`(?<![\w.])35(?![\w.])` 형태 무관 스캔, probe `bare_35_occurrences=0`), 90초 상한 강제 유지.
즉 **하네스에 로드 경로가 없다**는 §3/§10.4의 결론은 이 바퀴의 더 강한 방법으로 재확인된다.

**정정 N6 (수치 영향 0, 판정 불변, 규칙 완화 아님).** lap284 probe의 두 가드가 **fail-open**이다.

1. `ps_states_waited`는 `get\("ps"\)\s*==\s*(\d+)` 정규식이라 **집합 소속 대기 형태를 못 본다.**
   하네스는 실제로 line **3466**과 **3902**에서 `item.get("ps") in {4, 5, 6}`으로 **대기한다**
   (`_wait_state`). 따라서 "PS 대기값 `{3,5,7,9}`뿐"은 **불완전한 서술**이고, 형태 무관 AST
   스캔의 실제 비교 집합은 `{3,4,5,6,7,9}`다.
2. 같은 이유로 `ps35_references` 정규식은 `item.get("ps") in {35, ...}` 형태를 **잡지 못한다.**
   probe `guard_fail_open`이 실제 3466 줄과 가상 PS35 줄 두 형태로 이를 시연한다:
   등호 형태만 탐지(`true`), 집합 형태는 두 가드 모두 미탐지(`false`).

**결론이 살아남는 이유.** "PS35 참조 0건"은 이제 정규식이 아니라 위의 형태 무관 스캔으로
성립한다. 즉 **값은 옳았고 근거가 약했다.** 이 정정은 과거 판정을 뒤집지 않으며 lap284/lap298
원문도 고치지 않는다. 다만 장차 로드 경로가 집합 소속 형태로 PS35를 대기하면 그 두 가드는
**조용히 통과**하므로, 아래 해소 조건에 가드 형태를 명시 요구로 넣는다.

**UNKNOWN.** 수정 대상 함수, 연구 evidence 기록 위치, 로드 경로가 쓸 PS 대기 형태.

**반려 해소 조건.** (i) 수정할 함수 이름과 새 진입점을 문서로 특정하고, (ii) 연구 evidence의
출력 경로를 제품 소비 경로(`evidence["inputs"]` / `_g1_flush_input_stage` 계열)와 **파일 수준으로
분리**해 지정하며, (iii) 로드 경로가 쓸 PS 대기 형태를 선언해 가드가 그 형태를 검사하게 한다.
**금지 유지:** 기존 `PS5→PS3`를 `PS35→PS3`로 넓혀 같은 PASS에 편입하는 것(§10.1 결정2, §13 거부 조건).

### 14.5 §5(b),(e) 예산 — REJECT, 단 기구는 이미 존재한다

**확정.** `g1_baseline`/`g1_presentation_trace`가 `0 < timeout <= 90`을 강제하고(3283, 3702, 4100)
화면을 `1600x1200x24`로 고정한다. 그리고 **단계 예산 기구가 이미 있다**:
`G1_INPUT_STAGE_BUDGETS = {unit_select: 10.0, drag_select: 10.0, minimap: 10.0}`,
4값 `stage_budget_state`(`WITHIN_STAGE_BUDGET`/`STAGE_BUDGET_EXHAUSTED`/`STAGE_START_UNKNOWN`/
`STAGE_BUDGET_UNAVAILABLE`), `G1_INPUT_MAX_TRUNCATION_RATIO = 0.25`.

**트리 안의 자기 선언을 그대로 승계한다.** `runtime_env.py:2202-2205`는 그 25%가
"**측정이 아니라 설계 가정**이며 실제 게임 pre-poll 타이밍은 미측정이고 첫 Stage B run이 이를
기록해 임계를 재평가해야 한다"고 이미 적어 두었다. 로드 경로 예산도 **똑같이 가정**이며
같은 재평가 의무를 진다. 따라서 §5(e)는 "새 wall-clock 예산을 발명"이 아니라
"**기존 표에 로드 단계 키를 더하고 그 값이 가정임을 선언**"으로 다시 써야 한다.

**판정 REJECT.** (b)의 3 MB save 로드 소요는 **어떤 종류의 측정치도 없다.** 과거 8.4/8.4/8.5/
8.5/8.9/19.1초는 **새 게임** run이며, 이를 save 로드 실측으로 쓰는 것은 §13의 거부 조건이다.
이 tier는 그 금지를 유지하고 숫자를 추정해 채우지 않는다.

**반려 해소 조건.** (i) 로드 단계 키와 예산값을 제안하되 **가정으로 라벨**하고 첫 run이 실측을
기록해 재평가하는 의무를 함께 적는다, (ii) 준비/수집/종료 시간을 분리 계상한다, (iii) 총합은
기존 90초 상한 **안**에 들며 자동 연장·무변경 재시도는 금지다(§13 거부 조건, APPROVALS
2026-09-12 01:03의 blind retry 금지와 같은 취지).

### 14.6 §5(d),§6 실패 보존 — ACCEPT-WITH-CONDITION

**확정.** `_new_run`이 run별 고유 디렉터리를 만들고(:370), `prepare()`는 실패해도
`prepare_failure.json`을 남기며 실행 디렉터리를 지우지 않고(:618), 재사용 prefix/output은
거부되며(3292-3293), PID 취급은 자기 소유로 한정된다. `record_timeout`은 이미
`timeout_cause`/`predicate_observed`/`finished_elapsed`/`remaining_budget_after`/
`finished_tick`/`wait_observation`을 남긴다.

**정정 1건(수치 영향 0).** §5(d)의 괄호 서술 "현 flush는 stage 단위로 묶여 있다"는 **과소
표기**다. `_g1_flush_input_stage`는 **9개 호출 지점**(2024, 2523, 2545, 3383, 3392, 3562, 3874,
3895, 3930)에서 불리고, 그 docstring은 "Persist each stage before any later input or teardown
can block the run"이며 실제 호출은 `begin_stage`와 **매 입력 기록마다**다. 즉 flush 주기는
**레코드 단위**다. 이 정정은 만들 것을 바꾼다: 새 flush 주기가 아니라 **새 필드**가 필요하다.

**판정 ACCEPT-WITH-CONDITION.** 기구는 충분하고, §6이 요구한 **선언이 아직 없다.**

**선언해야 할 필드(실행 전, 네 실패 모드 각각).** ① PS35 미도달, ② PS35 도달·PS3 미도달,
③ timeout, ④ 수집 실패. 각각에 대해 **원시 PS와 tick의 시계열, 경과 시간, run ID, 소유 PID
집합, 입력 태그와 좌표, 오류 분류, flush 산출물 경로, 종료 방식**을 남긴다.
**금지 유지:** 실패를 결측/skip/PASS로 바꾸는 것, 다른 세션 정리, 로그 덮어쓰기(§13 거부 조건).

### 14.7 수용 패키지 — REJECT(패키지), 상위 반환 최소 봉투 1건

입력 여섯 행 중 셋이 REJECT(14.1·14.4·14.5)이고 §5(c)도 REJECT다. 열린 입력 위에 실행
패키지를 수용할 수 없다. **runtime/Stage B 예산 요청 없음. Stage B 0 유지.**
`make check` 361 passed와 probe exit0은 계획 승인도 제품 검증도 아니다.

**상위(Astra/사용자)로 올리는 최소 봉투 — 허가 전 집행하지 않는다.**

- **관측 대상 1건:** 구성 시점 `0x4D6312`가 읽는 순간의 `ds:0xE5BF1C`와 `ds:0xE5BF20` 값.
- **입력 0.** 클릭 없음, 슬롯 선택 없음, 로드 없음, 원본/후보 쌍 없음, PNG 비교 없음.
- **판정식:** 읽힌 쌍이 `800×600`이면 후보 **A(240,145)**, `640×480`이면 후보 **B(160,85)**.
  둘 다 아니면 두 후보를 **모두 버리고** blocker로 반환한다(상수를 맞추지 않는다).
- **이 관측이 최소인 이유:** A/B 분기와 map↔dialog 순서 UNKNOWN의 첫 실행 자료를 동시에 주면서
  입력 이벤트를 하나도 쓰지 않는 **유일한** 항목이다. 나머지 UNKNOWN(hitbox, 슬롯, 로드 성공)은
  전부 클릭을 요구하므로 이 봉투에 넣지 않았다.
- **변경이 필요한 기존 금지:** "runtime 예산 0" 한 줄뿐이다. Stage B 금지, 클릭 금지, 원본
  재실행 금지, 하네스 수정 금지, W3 재pin 금지는 **그대로 유지**를 요청한다.
- **거부될 경우:** §5(c)와 A/B는 UNKNOWN으로 남는다. 그 경우에도 정적 CFG 재개를 요청하지
  않는다(§14.3 지렛대 소진 선언). 남는 진행 가능한 독립 작업은 §14.1의 fixture 모델 반증
  경로뿐이며, 그것은 실행 예산 0으로 수행 가능하다.

### 14.8 N4·W3 처리 (§13.2·§13.3에 대한 middle 응답)

- **N4:** 이 바퀴는 lap319/320 probe를 **새 입력 처리·실행 게이트로 채택하지 않는다.** 따라서
  §13.2의 조건에 따라 N4 수리를 선행 조건으로 **지정하지 않고**, 알려진 진단 결함으로 보존한다.
  **단서:** 로드 경로 evidence 스키마가 그 probe의 `main()` 선평가 형태를 재사용하면 그 시점에
  N4 수리가 선행 조건이 된다. 그때 다시 지정한다.
- **W3:** 재pin 승인하지 않는다. §13.3 그대로 유지한다. 이 절은 어떤 pin/baseline/golden도 건드리지 않았다.

### 14.9 이 판정이 아닌 것

제품 G1 합격, Stage B 허가, runtime 쌍 예산 승인, 마일스톤 종료, G2~G4 전환이 **아니다**.
`(296,505)`의 클릭 결과는 여전히 미관측이고 후보 A는 여전히 정적 후보다.
S1 종결 REJECT, R17/R31 금지, R29 범위 승인 거부, R30 M11 생존, R6-B-R2 미결, WM_CLOSE 결함,
offline 8건 주차, G3 저장 포맷 블로커는 전부 이전 판정 그대로 유효하다.
이 절은 기술 컨펌이며 **사용자 마일스톤 승인이 아니다.** work 실행 카드는 이번에 열지 않았다.
