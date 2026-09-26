# G2 strategy — §91 회부 판정: 정지 명령 발행자 **런타임 귀속 W40** 채택, J4 후속 work 1회로 계산 (lap538)

- 발행: lap538 strategy (Claude Code `claude-opus-5-5` / high, INBOX 2026-09-23 strategy 모델 교체 지시), 2026-09-23 KST.
- 입력: `loop/ESCALATE_SOL` §91, `docs/history/laps/20260923_lap537_middle_w39_review_erev_static.md`,
  lap535 판정 문서 `G2_STRATEGY_W38_REVERT_ATTRIBUTION_LAP535.md` §2·§3·§5(J4), W39 하네스(lap536).
- 성격: 방향·범위·검증 기준 문서다. 게임 실행 0, 제품 source·브리지·테스트·하네스 변경 0, 커밋 0.
  **G2 제품 합격도 3단 마일스톤 승인도 아니다.** 사용자가 번복할 수 있다.

## 0. 이번 회차가 독립 확인한 것 (읽기만)

- 원본 `b56986e0…c9c08a8ac` 불변. W39 원시 `triggers.jsonl` `8f4735fa…`·`trace.jsonl` `7017daa0…`, lap537 재계산 6파일 SHA가 lap537 기록과 같다.
- W39 하네스 SHA: `w39_run.py` `64a86d2117ee558bcf0678663968b0293fe0590c96de73a8db3cf55f4b454f41`,
  `gdb_watch.py` `f8a0ba33b8115547b127230deea1d243db852134d5ee785c4baa8008aa3db8bb`. W39는 hw watchpoint 3개 무장·26 트리거·정상 detach였다.
- lap537 `text_orig.objdump`에서 다시 셌다. `call 0x4aeda0`(CmdStop) **127곳**, `call 0x4aede0`(CmdMove) **44곳**으로 같다.
  `0x40c727`~`0x40c73c`(cmd2 case) → `jmp 0x40d53a` → `mov (%edi),%ax` → `0x40d53d` store로 가는 경로에 조건 분기가 없다. lap537 판독과 같다.
- CmdStop 127곳을 호출 대상 시작점으로 묶었다. 56개 함수에 분포한다. 주소대별로 `0x40`17·`0x41`24·`0x42`1·`0x44`4·**`0x47`74**·`0x48`4·`0x4b`3이다.
  `0x47` 대역에는 알려진 AI 자동시전 dispatcher `FUN_004755D0`(owner별 게이트 `DAT_00959AF0`)가 있다. **정황일 뿐 귀속 근거는 아니다.**
  CmdStop과 CmdMove를 둘 다 부르는 함수는 `0x4407e0`·`0x47f400`·`0x4bd700` 3개뿐이다(B의 "정지 → 출발점 복귀 이동" 후보).
- fixture의 owner0~7은 전부 AI 차례를 받는다(lap529). 따라서 A(owner0)·B(owner3) 모두 AI 소유 유닛이다.

## 1. 판정

- **K1 W40 채택.** middle 권고 1을 받는다. 대안(J4 즉시 적용)은 기각한다.
  - 이유: 즉시 `BLOCKED`로 닫으면 사용자에게 가져갈 선택지가 "AI 충돌인지 유닛 로직인지 모름" 상태가 된다.
    W40 1회는 검증된 도구(W39)에서 watch 주소만 바꾸면 되고, 발행 함수를 결정적으로 특정한다. 결과가 사용자 질문의 모양을 정한다.
  - streak: lap537(middle)·lap538(strategy) 연속 문서 2회째다. **다음 회차는 W40 게임 실행이어야 한다.** middle 카드 회차를 끼우지 않는다(사양은 §2).
- **K2 J4 예산 해석(고정).** W40을 lap535 §5의 **"후속 work 1회"로 계산한다.** W40 뒤 `hit` 짝 <2는 확정적이다(W39와 같은 fixture).
  그래서 W40 결과로 S1은 원칙상 `BLOCKED` 보고로 간다. 예외는 §3의 **E2 하나**뿐이다.
  - E2(fixture 원인 확정): 발행자가 유닛 자체 로직이고, middle이 그 분기의 **주소·비교 필드·뒤집는 fixture 값**을 정적으로 특정했을 때만 적용한다.
    이때 work 1회(H7' + 그 fixture 변경, 1파동)를 허가한다. 그 1회 뒤에도 `hit` 짝 <2이면 예외 없이 `BLOCKED`로 닫는다.
  - E2는 lap535 §5의 `REVERT_CANDIDATE_DIFF` 예외와 같은 성격이다. 원인이 주소 수준으로 확정되었을 때만 쓴다. 추측으로 probe를 더 쌓는 것은 아니다.
- **K3 합격 기준 불변.** A1~A8'·A3'/A3r·A6a/A6b, 허용목록 {5,7,46,2}, 편 byte·가드, AI/생산 코드 0 변경은 모두 그대로다. 144k는 닫힌 채다.

## 2. W40 — CmdStop/CmdMove 발행자 런타임 귀속 (실행 사양, middle 카드 없이 work가 바로 실행)

W39와 같은 후보·fixture·시딩·파동 1개·H10·H11·H9 추적을 쓴다. **바뀌는 것은 watch 대상, 기록 필터, 스택 깊이뿐이다.**

**경계** — lap535 §2 경계 1~6을 그대로 쓴다(3파일 SHA 핀·`SAFETY_PASS`·표적 테스트 2개·원본 불변·foreground 동기 완주·gdb 읽기/debug register만·최대 2회·**45분 상자**).
추가 경계: 복사 전에 `w39_run.py`·`gdb_watch.py` SHA가 §0 값과 같은지 확인한다. 다르면 게임을 시작하지 않고 `BLOCKED(gate)`로 둔다.

**하네스** — 두 파일을 `temp/Syw2plus_patch/g2_capacity/<YYYYMMDD>_lap<실행lap>_w40_stop_issuer/`에 `w40_run.py`·`gdb_watch.py`로 복사한다. 아래 외에는 바꾸지 않는다.
- **H14 watch 대상:** `WA'` = `A`의 `+0x384`(2바이트), `WB'` = `B`의 `+0x384`(2바이트). 주소는 W39와 같은 풀 기준·stride로 계산한다(W39 `+0x290` 주소 + 0xF4).
  `WC'` = `B`의 `+0x388`(4바이트, 대기 목표 xy). 네 번째 레지스터는 비워 둔다. 무장 시점은 W39와 같이 op8 **전**이다.
- **H15 기록:** 모든 트리거는 `name, old, new, pc, tick`을 한 줄씩 남긴다. `WA'`·`WB'`에서 `new`∈{2,3,4}이면 전체 기록을 남긴다.
  전체 기록은 레지스터와 **`[esp]`부터 DWORD 128개**, `ebp` 사슬 8단이다. `WC'`는 전체 기록 없이 값만 남긴다. 이름당 상한 200, flush는 매 줄마다다.
- **H16 반환주소 대조(실행 뒤, 게임 없이):** 원본 `.text`에서 CmdStop 127곳·CmdMove 44곳의 `call+5` 집합을 만든다.
  `new`==2 트리거마다 스택 128 DWORD 안에서 CmdStop `call+5`와 같은 값 중 **esp에 가장 가까운 것**을 `ISSUER_SITE`로 둔다. `new`==3이면 CmdMove 집합으로 같은 일을 한다.
  둘러싼 함수 시작점(`ISSUER_FN`)과 그 위 반환주소 사슬(유효한 `call+5`인 값만, 최대 8개)을 적는다.
  후보 바이트는 원본과 같은 오프셋이므로 원본 `.text`로 대조한다. 단 `ISSUER_FN` 창을 원본·후보로 대조한 결과(H13 방식)도 함께 적는다.

**판정식 (실행 전 고정 — 사후 재채점 금지, middle은 강화만 가능)**
- `M0'`(도구 작동): `WA'`에 `new`==4 트리거(op8 대기 명령 기록)가 있거나, W39와 같이 추적에서 A `+0x290`이 4가 된다.
  추적에 4→2 철회가 있는데 `WA'`에 `new`==2 트리거가 0이면 watch 실패로 보고 `BLOCKED(harness)`로 둔다.
- `I_A` = `WA'`의 op8 뒤 **첫** `new`==2 트리거의 `ISSUER_FN`이다. `I_B`도 `WB'`에서 같은 방식으로 정한다. `R_B` = `WB'`에서 그 정지 뒤 첫 `new`==3 트리거의 `ISSUER_FN`(복귀 이동)이다.
- 분류(발행 함수마다):
  - `UNIT_SELF` — `ISSUER_FN`이 lap537 후보 c1 `FUN_0040C390` 또는 c2 이동 실행 함수(`0x40b276` CmdStop 지점을 품은 함수)다.
  - `OWNER_AI` / `UNIT_OTHER` / `UNCLASSIFIED` — 그 밖의 함수다. middle이 `ISSUER_FN`과 바로 위 호출자 1단을 **한 번** 읽고 정한다(문서 1회, 60분).
    `OWNER_AI`는 owner 인덱스 AI 상태를 읽거나(`DAT_00959AF0`류 owner 표, PlayerStruct AI 필드) owner 루프에서 불리는 경우다.
    `UNIT_OTHER`는 유닛 필드·지형·목표 조건만 보는 경우다. 60분 안에 못 가르면 `UNCLASSIFIED`로 둔다.

| 라벨 | 조건 (우선순위 위에서 아래) |
|---|---|
| `BLOCKED` | gate·timebox·하네스 결함(`M0'` 실패, `ISSUER_SITE` 미발견 포함)·게임 fault |
| `PROBE_VOID` | 무장 실패(`ARM_FAIL`) |
| `NO_STOP` | 600 tick 안에 `WA'`·`WB'` 모두 `new`==2가 없다(W39와 다른 거동) |
| `ISSUER_FOUND` | `I_A`·`I_B` 중 하나 이상이 특정됐다. 라벨 뒤에 분류를 붙인다(예: `ISSUER_FOUND(A=OWNER_AI,B=UNIT_SELF)`) |

- 보고 의무: 트리거 이름별 개수·`old→new`·pc 분포, `I_A`·`I_B`·`R_B`의 `ISSUER_SITE`/`ISSUER_FN`/반환 사슬, `WC'`로 본 B의 대기 목표 변화(복귀 좌표가 (56,17)인가), H11 결정성, 원본↔후보 창 대조.
- 이 probe는 A1~A8'를 판정하지 않는다. 라벨은 합격 라벨이 아니다.

## 3. 결과 분기 (미리 고정 — 이 표 안의 경로는 strategy 재판정 없이 진행)

| W40 결과 | 다음 한 가지 |
|---|---|
| A 또는 B가 `OWNER_AI` | **S1 교전 입력 경로 `BLOCKED`**(J4). middle 검수 뒤 사용자에게 보고한다(§4 선택지). 같은 계열 probe는 더 없다 |
| A·B 모두 `UNIT_SELF`/`UNIT_OTHER` | middle이 그 `ISSUER_SITE`로 가는 분기 하나만 읽는다(문서 1회, 60분). 주소·필드·fixture 값이 특정되면 **E2**로 work 1회(H7' + 그 fixture). 특정 못 하면 `BLOCKED`, 사용자 보고 |
| `UNCLASSIFIED`(어느 하나라도, `OWNER_AI` 없음) | `BLOCKED`, 사용자 보고. 근거는 발행 함수와 읽은 범위다 |
| `NO_STOP` | 결정성이 깨졌다. middle이 W39·W40 원시를 대조하고 strategy에 회부한다 |
| `PROBE_VOID`·`BLOCKED` | lap535 §2 경계 5대로 1회 더 한다(하네스 결함일 때만). 두 번째도 같으면 S1 `BLOCKED`, 사용자 보고 |

- 후보 결함 예외는 그대로다. `ISSUER_FN` 창에 알려진 fixup 밖 차이가 있으면 `REVERT_CANDIDATE_DIFF`와 같이 수리 카드 계보로 간다.

## 4. `BLOCKED` 시 사용자 보고의 선택지 (미리 정리 — 모델은 고르지 않는다)

S1이 닫히면 G2 "움직이는 상태의 안정"에 필요한 교전·사망·재생산 순환(A2·A3')을 스크립트 입력만으로 만들 수 없다는 뜻이다. 보고에 아래를 적는다.
- **(가) (ㄴ) 예외 승인** — 시딩 유닛에 한해 AI 정지/복귀 발행을 막는 최소 AI 변경이다. 2026-09-21 00:20 G4 잠정 중단의 명시 예외가 필요하다.
- **(나) "8인" = 사람 해석** — 시딩 owner를 AI가 아닌 사람 슬롯으로 두는 fixture다. 이게 가능한지는 아직 조사하지 않았다(S4 멀티 영향).
- **(다) S1 교전 트랙 중단** — G2 증거를 정지 생존(W26 144k 등)과 무장·저장 축으로 제한한다. 이것은 lap522 "움직이는 상태"의 해석을 약화하므로 사용자만 고를 수 있다.
- 질문 아님: S1이 닫히면 strategy가 G2의 다른 축(STATUS의 구조통합 blocker, F4 계보 등)에서 다음 한 가지를 고른다.

## 5. streak·불변·사용자 통지

- **streak:** lap537·538 연속 문서다. 다음 회차가 W40 게임 실행 없이 끝나면 더 쌓지 말고 STOP하고 사용자에게 보고한다.
- 불변: AI/생산/건설 패치 0, op4 0, 편 byte·가드 완화 0, 허용목록 {5,7,46,2}, 원본 명령 경로만 사용. 게임 메모리 쓰기는 기존 브리지 op만, gdb는 읽기·debug register만.
- **사용자 통지(질문 아님):** 명령 취소는 원본 게임 로직이 따로 거는 "정지" 명령 때문이다. 누가 거는지를 실행 1회로 잡는다.
  AI 쪽이면 이 교전 경로를 닫고 §4 선택지로 묻는다. 합격 기준은 바뀌지 않았다.
- 미결 그대로: Q9 · Q7-B · "8인"이 사람인지 AI인지 · 스크립트 교전 (ㄱ) 범위.

## 6. 다음 한 가지

**work(Sonnet5):** §2 W40을 실행한다. 순서는 3파일·W39 하네스 SHA 확인 → `checks/safety.sh check`·표적 테스트 2개 → `w40_run.py`(H14~H16) → 게임+gdb 1회 foreground 완주 → H16 대조 → 자기 라벨이다.
그다음 middle(Opus5.5)이 `triggers.jsonl` 원시로 재계산·분류하고 §3 분기의 다음 한 가지를 발행한다.
