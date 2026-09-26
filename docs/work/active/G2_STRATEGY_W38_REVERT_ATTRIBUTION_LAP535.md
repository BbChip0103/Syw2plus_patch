# G2 strategy — §88 회부 판정: W38 표 밖 결과 처리, 철회 writer는 **런타임 하드웨어 watchpoint로 귀속**(W39) (lap535)

- 발행: lap535 strategy (Claude Code `claude-opus-5-5` / high, INBOX 2026-09-23 strategy 모델 교체 지시), 2026-09-23 KST.
- 입력: `loop/ESCALATE_SOL` §88, `docs/history/laps/20260923_lap534_middle_w38_independent_review.md`,
  lap532 판정 문서 `G2_STRATEGY_N192_APPROACH_PATH_LAP532.md` §2·§3, W18 선례(lap437 카드·lap438 실행·lap439 검수).
- 성격: 방향·범위·검증 기준 문서다. 게임 실행 0, 제품 source·브리지·테스트·하네스 변경 0, 커밋 0.
  **G2 제품 합격도 3단 마일스톤 승인도 아니다.** 사용자가 번복할 수 있다.

## 0. 이번 회차가 독립 확인한 것 (읽기만)

- 원본 `b56986e0…c9c08a8ac`, W38 원시 5종(`trace` `a2ff394e…`·`t0_positions` `04653a7c…`·`waves` `7e4ad317…`·`control_wave` `0247d1a9…`·`events` `99e9dbcd…`),
  `w38_run.py` `40882756…`, `runtime_bridge.c` `3555848d…` SHA가 lap533·534 기록과 같다.
- lap534 `recompute_w38.py`를 다시 돌려 `recompute_w38.json`이 바이트 단위로 같다(SHA `4b1e350d…04768096`, 같은 폴더에 같은 내용으로 다시 쓰임).
- **결정성:** 파동 1~3이 같은 소스 슬롯을 고른다(예: owner0 `3800`은 세 파동 모두 `+0x290` 1→4→1, owner3 `3185~3190`은 세 파동 모두 움직였다가 돌아옴).
  그래서 표본 144는 실제로 독립 소스 48개다. 같은 슬롯에서 같은 현상이 반복되므로 **특정 슬롯을 미리 지정해 관측할 수 있다.**
- op8은 파동당 48건이 약 1.7 tick 간격으로 순차 발행된다(한 tick 일괄 발행 아님).
- **W18 선례:** lap438이 gdb 하드웨어 write watchpoint로 Wine 게임 프로세스의 writer pc를 1회 실행에 잡았다(`watch_summary.json` pc `0x40efcb`,
  명령 시작 `0x40EFC5`는 lap439가 역산). lap439는 그 명령이 **후보 빌드의 즉시값 재배치 오탐**임을 밝혔다.
  도구: `temp/Syw2plus_patch/g2_capacity/20260921_lap438_unit_700_watchpoint_eip_run2/{orchestrator.py,gdb_watch.py}`
  (SHA `8f2611d4…b902`, `5fd409e7…a506`). 이 머신은 `ptrace_scope`=0, `/usr/bin/gdb` 있음(이번 회차 확인).

## 1. 판정

- **J1 분기표를 확장하지 않는다.** `CONTROL_NA`는 §3 표 밖이다. 전열 배치(W39안)는 발행하지 않는다.
  middle 비권고에 동의한다. N198로 "유닛 점유가 경로를 막는다"는 전제가 지지되지 않았다. 게임 1회를 해석 불능 결과에 쓸 위험이 크다.
- **J2 R1을 채택하되, 정적 추적 문서 회차가 아니라 런타임 귀속 probe로 바꾼다(W39, §2).**
  - 이유 1: 철회(N196)는 결정적이고 슬롯이 정해져 있다. "누가 `+0x290`을 4에서 1로 되돌리는가"는 watchpoint 1회로 바로 답이 나온다.
    정적 추적은 `0x4AEE10→…→0x40C640`와 이동·경로 루틴의 writer 후보를 전부 읽어야 한다.
  - 이유 2: W18이 같은 질문을 같은 도구로 1회에 풀었고, 원인은 후보 빌드 결함이었다. 이번에도 G4(stock)에서는 type2가 거리 63을 걸었는데 후보에서는 못 걷는다.
    같은 계열(재배치/fixup 오탐)일 가능성이 있다. 이 가능성은 writer pc를 잡은 뒤 **그 함수 하나만** 원본·후보 바이트로 대조하면 확정된다.
  - 이유 3(streak): lap534·535가 연속 문서 회차다. 세 번째 문서 회차는 만들지 않는다. **다음 회차는 W39 게임 실행이다.**
- **J3 R2(대조 재정의)는 정의만 하고 W39에는 넣지 않는다(§4).** 한 바퀴 한 가설이다. W39 결과가 "원본 로직"으로 나오면 그때 H7'을 쓴다.
- **J4 가설 예산.** N192 계열에서 실패한 가설이 2개다(W37 "수락=교전", W38 "밀집 막힘"). PROMPT ③의 2회 경계에 해당한다.
  strategy는 **계속**으로 판정한다. 근거: W38이 새 관측(N196, 결정적 철회)을 만들었고, W39는 추측이 아니라 검증된 도구로 그 writer를 직접 잰다.
  단 **종결 조건을 미리 고정한다(§5).**
- 144k는 닫힌 채다. lap532 §4의 A3'·A3r·A6a·A6b와 전열 배치 사전 허가(§3.1)는 그대로 둔다. 전열 배치는 §3 표의 원래 조건일 때만 쓴다.

## 2. W39 — `+0x290` 철회 writer 런타임 귀속 (실행 사양, middle 카드 없이 work가 바로 실행)

W38과 같은 후보·fixture·시딩·파동 규칙을 쓴다. 바뀌는 것은 **파동 수(1개)와 watchpoint 추가**뿐이다. 입력은 늘리지 않는다.

**경계**
1. repo source 변경 0. 3파일 SHA가 W38 §2와 같아야 한다(`runtime_bridge.c` `3555848d…`, 핀 테스트 `2a8aa4f7…`, op8 계약 테스트 `0939f5b6…`). 다르면 게임을 시작하지 않고 `BLOCKED(gate)`.
2. source가 lap530 `make check`(828 passed) 때와 같으므로 전체 `make check`는 생략한다(N22). `checks/safety.sh check`와 표적 테스트 2개는 돌린다.
   work가 repo 비문서 파일을 하나라도 바꾸면 `make check` 전체 1회가 필요하다. 하네스·gdb 스크립트는 temp에만 둔다.
3. 원본 SHA 전후 불변. 격리 복사본·prefix·새 Xvfb display만 쓴다. 게임과 gdb는 **foreground 동기로 완주**한다(셸 background 후 회차 종료 금지).
4. gdb는 **debug register 설정과 메모리 읽기만** 한다. `set var`·`jump`·`call`·소프트웨어 breakpoint 금지(W18 규칙 그대로). 자기 PID·다른 세션 프로세스에 붙지 않는다.
   게임 PID는 기존 `tools.runtime_env`/하네스의 Windows PID 발견 방식만 쓴다(INBOX 2026-09-21 00:51 교훈).
5. 실행은 최대 2회다. 2회째는 1회째가 하네스 결함(gdb attach 실패·watch 미무장·deadlock)으로 `BLOCKED`됐고 하네스만 고쳤을 때만 허용한다. 게임 fault는 EIP를 기록하고 재시도하지 않는다.
6. **45분 상자**(빌드·게임·gdb). 넘으면 그 시점 원시를 보존하고 `BLOCKED(timebox)`.

**하네스** — `temp/Syw2plus_patch/g2_capacity/20260923_lap533_w38_approach_probe/w38_run.py`(SHA `408827562867dde2a9d81d4b3d8eca8a993ea245d19acc6cb390965bc20364aa`)를
새 폴더 `temp/Syw2plus_patch/g2_capacity/<YYYYMMDD>_lap<실행lap>_w39_revert_watch/`에 `w39_run.py`로 복사한다. gdb 부분은 lap438 `gdb_watch.py`/`orchestrator.py`를 본떠 새로 쓴다. 아래 외에는 바꾸지 않는다.
- **H10 실행 길이:** 창 B(1,000 tick) → 파동 **1개**(W38 파동 규칙 그대로: op1 → X 보충 → op8 48건) → 마지막 op8 +600 tick에 멈춘다. H7 대조·저장/로드 없음.
- **H11 관측 슬롯 사전 선택:** 파동의 op8 전에, W38 `do_wave_traced`의 선택 규칙을 **op8 없이 읽기만으로** 한 번 돌려 owner0의 첫 소스 `A`와 owner3의 첫 소스 `B`를 정한다.
  W38 값(`A`=3800, `B`=3185)과 같은지 적는다(결정성 재확인). 다르면 새 값을 쓰고 그 사실을 적는다. 파동 안에서 실제로 `A`·`B`에 op8이 가지 않으면 `BLOCKED(harness)`.
- **H12 watchpoint:** 파동 op8 발행 **전에** gdb를 붙이고 하드웨어 write watchpoint를 건다. 슬롯 주소는 W38 `read_pool_snapshot`과 같은 풀 기준·stride로 계산한다.
  - `WA` = `A`의 `+0x290`(2바이트), `WB` = `B`의 `+0x290`(2바이트), `WC` = `B`의 `+0x2A2`(x, 2바이트). 네 번째 레지스터는 비워 둔다.
  - `stop()`은 기록만 하고 **항상 계속**한다(False 반환). 트리거마다 한 줄 `triggers.jsonl`에 append+flush:
    `name, addr, old, new, pc, thread, tick, eax..edi, esp, ebp`, 그리고 `[esp]`부터 DWORD 16개와 `ebp` 사슬 4단(각 `[ebp+4]`).
  - 이름당 트리거 상한 200. 상한에 닿으면 그 watch만 해제하고 적는다.
  - 마지막 op8 +600 tick에 watch를 지우고 detach한다. 그다음 게임을 정상 종료한다.
- **H9 추적 유지:** W38의 소스·목표 추적(필드·checkpoint 시점)을 이 파동 48건에 그대로 남긴다. `A`·`B`는 추가로 op8 뒤 +1~+30 tick을 매 poll 읽는다(가능한 만큼, 실제 tick 기록).
- **H13 바이트 대조(실행 뒤, 게임 없이):** 아래 `E_rev`가 속한 함수를 후보 `a10024de…`와 원본 `b56986e0…`에서 각각 디스어셈블해 대조한다.
  차이가 있으면 차이마다 "알려진 풀/존재배열 fixup 목록에 있는가"를 적는다. 목록은 현재 source의 `build_candidate(orig, 4001)` 결과로 만든다(lap523 §3 방식).
  **pc는 쓰기 명령의 다음 주소다**(W18: pc `0x40efcb` ↔ 명령 `0x40EFC5`). 명령 시작은 직전 명령 경계로 역산해 둘 다 적는다.

**판정식 (실행 전 고정 — 사후 재채점 금지, middle은 강화만 가능)**
- `M0`(도구 작동): `WA` 트리거 중 `new`==4인 것이 있다(op8 자신의 승격 쓰기). 없으면 H9 추적에 4가 보이는지 본다. 추적에 4가 있는데 트리거가 0이면 watch 실패 ⇒ `BLOCKED(harness)`.
- `E_rev` = `WA`에서 `old`==4이고 `new`≠4인 **첫** 트리거의 pc. `E_mv` = `WB`의 4→3 또는 3→1 첫 트리거 pc, `E_x` = `WC` 첫 트리거 pc(이동 writer).

| 라벨 | 조건 (우선순위 위에서 아래) |
|---|---|
| `BLOCKED` | gate·timebox·하네스 결함(`M0` 실패 포함)·main thread 미도달·게임 fault |
| `PROBE_VOID` | 무장 실패(W36 §5 `ARM_FAIL` 조건) |
| `NO_REVERT` | `WA`에 4→(≠4) 트리거가 600 tick 안에 없다(W38과 다른 거동 — 추적 원시와 함께 보고) |
| `REVERT_CANDIDATE_DIFF` | `E_rev` 함수에 원본과 다른 바이트가 있고, 그중 하나라도 알려진 fixup 목록 밖이거나 풀/존재배열이 아닌 상수를 바꾼 것 |
| `REVERT_ORIGINAL_LOGIC` | `E_rev` 함수 바이트가 원본과 같거나, 차이가 전부 알려진 풀/존재배열 fixup이다 |

- 보고 의무: 트리거 전량 요약(이름별 개수·`old→new`·pc 분포), `E_rev`·`E_mv`·`E_x`의 pc와 명령 시작, 호출 사슬 반환주소, H13 대조표, H11 결정성.
- 이 probe는 A1~A8'를 판정하지 않는다. 라벨은 합격 라벨이 아니다.

## 3. 결과 분기 (미리 고정 — 이 표 안의 경로는 strategy 재판정 없이 진행)

| W39 결과 | 다음 한 가지 |
|---|---|
| `REVERT_CANDIDATE_DIFF` | middle이 원시·바이트로 재계산한다. 확인되면 **G2 후보 결함**이다. 사용자에게 알리고(통지), middle이 W19식 **수리 카드**를 발행한다. 수리 뒤 W38과 같은 1파동 재관측 1회로 이동·교전을 확인한다 |
| `REVERT_ORIGINAL_LOGIC` | 원본 게임 로직이 명령을 버린다. middle이 **`E_rev` 직전 분기 조건 하나만** 정적으로 읽는다(문서 1회, 60분 또는 후보 2개 반증 뒤 `BLOCKED`). 조건이 fixture로 바꿀 수 있는 것이면 그 fixture 변경 + §4 H7' 대조로 work 1회 |
| `NO_REVERT` | 결정성이 깨졌다. middle이 W38·W39 원시를 대조해 차이를 적고 strategy에 회부한다 |
| `PROBE_VOID`·`BLOCKED` | §2 경계 5대로 1회 더(하네스 결함일 때만). 두 번째도 같으면 strategy 회부 |

## 4. H7' — AI 생산에 기대지 않는 양성 대조 (정의만, 사용은 §3이 지정할 때)

- 폐기: lap532 H7("시작 유닛 type110")은 전제가 틀렸다(N195: type110은 AI 생산분이고 시딩으로 cap이 차면 거의 생기지 않는다).
- **H7' 정의:** owner0과 owner1에 **시딩 type2 1기씩**을 본 블록들과 떨어진 개방 구역에 둔다. 두 유닛의 Chebyshev 거리는 10~20이다.
  T0 위치표(H8)로 두 유닛 사이 직선 띠(폭 3)에 다른 유닛이 0임을 확인한다. owner0 → owner1 op8 1건.
  - `CONTROL_MOVED` = 600 tick 안에 소스 변위 ≥2. `CONTROL_STILL` = 수락됐지만 변위 ≤1. `CONTROL_NA` = 배치·수락 실패(대체하지 않는다).
  - 전비: type2 1기 비용 13을 gate 안에서 쓴다(`used+13 ≤ 5000`). 무장 기준(owner마다 `used` ≥4,900)과 가드·허용목록은 바꾸지 않는다.
    배치 순서와 좌표는 그때 middle 또는 work 카드가 H8과 N187(시딩 순서) 교훈을 보고 정한다.
- 해석: `CONTROL_STILL`이면 개방 구역에서도 못 걷는다 ⇒ 밀집·목표 문제가 아니다. `CONTROL_MOVED`이면 문제는 블록 배치나 목표 조건 쪽이다.

## 5. 종결 조건·streak·사용자 통지

- **S1 교전 트랙 종결 조건(고정):** W39와 §3이 지정한 후속 work 1회(수리 뒤 재관측 또는 fixture 변경 + H7')가 끝났는데도
  S에서 `hit` 짝 <2이면, S1 교전 입력 경로를 `BLOCKED`로 닫고 **사용자에게 보고한다**(근거·대안·G2 영향). 같은 계열 probe를 더 쌓지 않는다.
  예외는 `REVERT_CANDIDATE_DIFF`가 확정된 경우다. 그때는 후보 결함 수리가 G2 전체의 선결 과제이므로 수리 카드 계보로 넘긴다.
- **streak:** lap534(middle)·lap535(strategy) 연속 문서다. **다음 회차는 W39 게임 실행이어야 한다.** W39 사양이 §2에 있으므로 middle 카드 회차를 끼우지 않는다.
  W39가 게임 실행 없이 끝나면 더 쌓지 말고 STOP하고 사용자에게 보고한다.
- 불변: AI/생산/건설 패치 0, op4 0, 편 byte·가드 완화 0, 허용목록 {5,7,46,2}, 원본 명령 경로만 사용. 게임 메모리 쓰기는 기존 브리지 op만, gdb는 읽기·debug register만.
- **사용자 통지(질문 아님):** 전열 배치는 보류했다. 대신 명령이 취소되는 지점을 실행 중에 직접 잡는다. "안정 동작"의 뜻과 합격 기준은 바뀌지 않았다.
- 미결 그대로: Q9 · Q7-B · "8인"이 사람인지 AI인지 · 스크립트 교전 (ㄱ) 범위.

## 6. 다음 한 가지

**work(Sonnet5):** §2 W39를 실행한다. 순서는 3파일 SHA 확인 → `checks/safety.sh check`·표적 테스트 2개 → `w39_run.py`(H10~H13) → 게임+gdb 1회 foreground 완주 → H13 바이트 대조 → 자기 라벨이다.
그다음 middle(Opus5.5)이 `triggers.jsonl`·`trace.jsonl`·바이트 대조를 원시로 재계산하고 §3 분기의 다음 한 가지를 발행한다.
