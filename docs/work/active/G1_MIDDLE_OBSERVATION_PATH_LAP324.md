# lap324 middle — lap323 실행 경로 양립성 판정

2026-09-12 / Claude Code claude-opus-5 / high / 중간계획·컨펌. 게임 구현·실행 0.
이 문서는 middle 기술 판정이며 사용자 마일스톤 승인도 제품 증거도 아니다. 현재 큐는 docs/STATUS.md만 따른다.

입력: `G1_OBSERVATION_DIRECTION_LAP323.md`(`9539d0c5…`), `G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §14,
`loop/ESCALATE_SOL`(lap323), AGENTS/PROMPT 안전 규칙, APPROVALS 2026-09-12 01:03.
증거: 본 lap 신규 probe `docs/history/laps/probes/20260912_lap324_middle_observation_path_probe.py`
(`0ed6692b…`), report `c00eed09…`(연속 2회 stdout byte-identical, rc0, failures=[]).
probe는 이전 lap probe를 import하지 않고 하네스 사실(AST)과 바이너리 사실(PE 바이트 + objdump 1회)을 재유도한다.

## 판정: 제출 봉투(§14.7 형태) **BLOCKED**, 개정안 R1을 상위로 반환

제출 봉투는 "입력 0 + exact-site 계측 + 하네스 수정 금지"를 동시에 요구한다. 이 세 조건은
근거 부재가 아니라 **현재 증거와 충돌**한다(§2). 다만 관측 대상을 바꾸면 성립하는 경로가 하나
있으며(R1), 그 경로가 요구하는 금지 변경은 **1개가 아니라 3개**다(§3). 권한 결정은 상위 몫이다.

## 표 — lap323 인계 여섯 행

| 항목 | 판정 | 근거 (이번 lap 재유도) |
|---|---|---|
| 격리 시작 | **ACCEPT** | 아래 §1. 새로 만들 것 없음 |
| 도달과 계측 | **BLOCKED(제출 형태) / 개정 가능(R1)** | 아래 §2 |
| 변경할 금지 | **"한 줄만" 반증** — 최소 3건 | 아래 §3 |
| 예산·보존 | **ACCEPT-WITH-CONDITION** | 아래 §4 |
| 판정 | **개정 필요** — 관측 대상 교체 | 아래 §5 |
| work 경계 | **카드 0** (허가 미확정) | 아래 §6 |

## 1. 격리 시작 — ACCEPT

- 입력 EXE: `Syw2plus/syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (probe가 직접 해시). `validate_original_source`/`prepare`가 복사 전후로 이 SHA를 대조하고
  `_assert_private_copy`가 사본이 원본/보호 경로가 아님을 강제한다. 개인 원본 경로 실행 아님.
- 새 run/prefix/display: `_new_run`이 run별 고유 디렉터리를 만들고, `g1-*`는 manifest의
  `wine.created_new is True`를 요구하며 `_prefix_pids`/`_existing_state`/기존 output이 있으면 거부한다.
  `_xvfb`가 `_display_busy`로 비어 있는 display만 잡는다. 기존 세션 접속 경로 없음.
- 시작 명령 후보(AST 리터럴 재유도): `["Xvfb","-nolisten","tcp","-screen","0",…]` →
  `["wine","explorer","/desktop=Default,1600x1200"]` → `["wine", <사본>/syw2plus_original.exe]`.
- 소유 PID 확인/종료 경계: `_owned_runtime_process_pids`(자기 root PID 하위만), `_request_owned_game_close`,
  `_wait_for_clean_trace_close`. 전역 종료/다른 프로세스 정리 경로 없음.
- 한계: 이 행은 **기구의 존재**만 증명한다. 실제 run의 성립은 실행 증거이며 이번 바퀴에 없다.

## 2. 도달과 계측 — 제출 형태 BLOCKED, 개정안 R1은 성립

### 2.1 계측: exact-site를 증명할 기구가 **존재하지 않는다**

하네스의 읽기 수단은 `patches/population/runtime_driver.py:read`의 `process_vm_readv` **폴링뿐**이다.
`runtime_env.py`+`runtime_driver.py` 전체 토큰 계수: `process_vm_readv` 2, **`process_vm_writev` 0,
`ptrace` 0, `PTRACE` 0, `int3` 0, `0xCC`/`0xcc` 0, `winedbg` 0, `gdb` 0.**
즉 breakpoint·단일 스텝·메모리 쓰기가 하나도 없다. 폴링은 "0x4D6312가 읽는 **순간**"을 증명할 수 없고,
Astra는 "polling만으로 exact-site 주장 금지"를 명시했다. **제출 형태는 자기모순이다** —
exact-site 기구를 만드는 것 자체가 §14.7이 유지하겠다고 한 "하네스 수정 금지"의 위반이며,
프로세스 코드에 INT3를 쓰는 형태라면 원본 실행 이미지 변경 승인까지 별도로 필요하다.

### 2.2 개정 R1: 입력 두 값 대신 **유일 산출물**을 읽는다

0x4D6312의 중심식은 결과를 휘발시키지 않고 **영속 전역에 저장**한다(이번 lap 바이트 재유도):

```
0x4D6312  a11cbfe500      mov   eax,ds:0xe5bf1c      ; 화면 폭
0x4D631C  a120bfe500      mov   eax,ds:0xe5bf20      ; 화면 높이
0x4D632A  66890d5c8b0801  mov   WORD PTR ds:0x1088b5c,cx   ; origin_x 저장
0x4D6348  66893d5e8b0801  mov   WORD PTR ds:0x1088b5e,di   ; origin_y 저장
```

`.text`(0x401000–0x4E4AE5) 전수 절대 operand 스캔 결과:

| 전역 | operand 출현 | 직접 store | 읽기 | 미분류 |
|---|---|---|---|---|
| `ds:0x1088B5C` | 10 | **1** (`0x4D632A`) | 9 (전부 `movsx`) | 0 |
| `ds:0x1088B5E` | 11 | **1** (`0x4D6348`) | 10 (전부 `movsx`) | 0 |

직접 writer가 **각각 하나**이므로, 폴링으로 읽은 값의 출처는 (직접 writer 범위 안에서)
0x4D6312 계산으로 결정된다. 즉 **A/B 질문은 exact-site 없이도 관측 가능**하다.
같은 스캔이 화면 전역 직접 store를 `{0x431B79, 0x431B7F, 0x4324B8, 0x4324C2}` 4건으로 재유도해
lap301~lap320 수치와 일치한다(독립 재유도이며 과거 결과 승격 아님).

**잔여 fail-open(명시):** 이 스캔은 절대 operand 직접 형태만 본다. 계산 포인터/간접 writer는
배제되지 않는다(N2와 같은 종류). 따라서 R1의 결론은 "직접 writer 범위에서 유일"이라고만 쓴다.

### 2.3 도달: 입력 0으로는 **도달하지 못한다**

- 하네스가 기다릴 수 있는 상태는 형태 무관 AST 스캔으로 `ps ∈ {3,4,5,6,7,9}`뿐이고,
  `35` 리터럴은 형태 무관 스캔으로 **0회**, `save` 토큰 **0회**다(§14.4를 본 lap이 독립 재유도).
  `ds:0x1088B5C/0x1088B5E`는 `runtime_env.py`에 **한 번도 등장하지 않는다**.
- PS9(타이틀/메뉴)는 입력 0으로 도달하지만 그것은 다이얼로그가 아니다.
  `FUN_004D60B0`의 직접 caller는 `0x4D69E5`, `0x4D6A05` **2개뿐**이고, 그 상위 체인이 입력 없이
  실행된다는 근거는 **0건**이다. 타이틀 "불러오기" 후보 `(296,505)`는 위치·라벨만 확정이고
  **클릭 결과는 여전히 미관측**이다.
- 결론: 다이얼로그 구성은 **최소 1클릭**을 요구한다. "입력 0으로 구성 시점 도달"은 근거 부재를
  넘어 현재 증거와 **충돌**한다. 타이틀 시점 전역값을 구성 시점 값으로 바꾸는 우회는
  lap323이 이미 금지했고 이 tier도 그대로 유지한다.

## 3. 변경할 금지 — "한 줄만"은 반증됐다 (최소 3건)

| 금지 | 유지/변경 | 근거 |
|---|---|---|
| runtime 예산 0 | **변경 필요** (fresh run 1회, ≤90초) | §14.7 원 요청 |
| 하네스 수정 금지 | **변경 필요** | 임의 주소 읽기 진입점이 없다(서브커맨드 `{prepare,check,smoke,g1-baseline,g1-presentation-trace}`), 대상 전역 미참조, PS 대기 형태 미선언 |
| 입력 0 | **변경 필요** (클릭 정확히 1회, `(296,505)`) | §2.3 |
| Stage B·원본/후보 쌍·PNG 비교 | 유지 | R1은 쌍을 만들지 않는다 |
| W3 재pin, baseline/golden 갱신 | 유지 | lap322 §14.8 그대로 |
| 원본 실행 이미지 변경(INT3 등) | 유지(금지) | R1은 이것을 필요로 하지 않는다 — exact-site를 포기한 이유 |

**부수 효과(감축 아님):** R1의 1클릭은 §5(a)에서 위치·라벨만 부분 ACCEPT됐던 `(296,505)`의
**첫 실관측**이 된다. 그렇다고 hitbox·슬롯 선택·로드 성공을 얻는 것은 아니며 그 셋은 UNKNOWN으로 남는다.

## 4. 예산·보존 — ACCEPT-WITH-CONDITION (§14.6 승계)

기구는 이미 있다: `0 < timeout <= 90` 강제, 화면 `1600x1200x24` 고정, `_new_run` run별 보존,
실패해도 디렉터리 미삭제 + `prepare_failure.json`, `record_timeout`의
`timeout_cause`/`predicate_observed`/`finished_elapsed`/`remaining_budget_after`/`finished_tick`/`wait_observation`.

**제안 배분 — 전부 측정이 아니라 설계 가정이며 첫 run이 실측해 재평가한다**
(`runtime_env.py:2202-2205`가 25% 임계에 대해 이미 쓴 자기 선언을 그대로 승계):
준비·시작→PS9 ≤40초, 클릭→구성 확인 ≤20초, 관측·수집 ≤15초, 종료 ≤15초 = 합 90초 이내.
자동 연장·무변경 blind 재시도 금지(APPROVALS 2026-09-12 01:03과 같은 취지).

**실패 보존 4모드(실행 전 선언 필수):** ① 다이얼로그 미도달, ② 도달했으나 전역 미변화,
③ timeout, ④ 수집 실패. 각각에 원시 PS·tick 시계열, 경과 시간, run ID, 소유 PID 집합,
입력 태그·좌표, 오류 분류, flush 산출물 경로, 종료 방식을 남긴다.
실패를 결측/skip/PASS로 바꾸지 않고, 다른 세션을 정리하지 않으며, 로그를 덮어쓰지 않는다.

## 5. 판정식 — 관측 대상을 교체한다

1. 클릭 **전** PS9에서 `ds:0x1088B5C`/`ds:0x1088B5E` 원시 16-bit 값을 기록한다(pre).
2. 클릭 **후** 구성 확인 시점에 같은 두 값을 기록한다(post).
3. `post == (240,145)` → 후보 **A**. `post == (160,85)` → 후보 **B**.
   그 외 값 → **두 후보를 모두 버리고** blocker 반환(상수를 맞추지 않는다).
   `post == pre` 이거나 수집 실패 → **UNKNOWN**(초기값과 미기록을 구분할 수 없다).
4. 유효 범위: **해당 run·해당 진입 경로 1회 관측**. 모든 로드 경로의 결정성·hitbox·슬롯 선택·
   로드 성공을 증명하지 않는다. §2.2의 간접 writer fail-open을 보고서에 같이 적는다.
5. 연구 evidence는 제품 소비 경로(`evidence["inputs"]`/`_g1_flush_input_stage` 계열)와
   **파일 수준으로 분리**한다(§14.4 해소 조건 (ii)). 기존 `PS5→PS3` PASS에 편입 금지.

## 6. work 경계 — 이번 바퀴 카드 0

허가가 확정되지 않았으므로 구현/실행 카드를 열지 않는다. 허가 시의 **후보만** 적는다:

- 수정 대상 후보: `tools/runtime_env.py`에 연구 전용 서브커맨드 1개와 연구 전용 evidence 파일 경로,
  그리고 §14.4 (iii)이 요구한 **PS 대기 형태 선언**(집합 소속 형태를 가드가 검사하게 한다 — N6).
- 검증 파일 후보: 합성 실패 검사 3종(미도달/미변화/수집 실패)을 새 `tests/` 파일에 둔다.
- **선행 조건 발동:** 이 evidence 스키마가 lap319/320 probe의 `main()` 선평가 형태를 재사용하면
  §14.8 단서에 따라 **N4 수리가 선행 조건**이 된다. 재사용하지 않으면 발동하지 않는다.
- §14.1 fixture 모델 반증은 실행 예산 0으로 가능한 별도 연구안이며 이번에 두 번째 카드로 열지 않는다.

## 7. 이 판정이 아닌 것

제품 G1 합격, Stage B 허가, runtime 예산 승인, 클릭 승인, 마일스톤 종료/이동이 **아니다**.
후보 A는 여전히 정적 후보이고 `(296,505)` 클릭 결과는 여전히 미관측이다.
S1 종결 REJECT, R17/R31 금지, R29 범위 승인 거부, R30 M11 생존, R6-B-R2 미결, WM_CLOSE 결함,
offline 8건 주차, G3 저장 포맷 블로커, N1~N6·W2·W3는 전부 이전 판정 그대로 유효하다.
`make check` 통과와 probe rc0은 계획 승인도 제품 검증도 아니다.
