# G1 W70 생산 입력 — queue witness 계약 정정과 control 분리 (lap944 strategy)

- 역할: strategy(Claude Code `claude-fable-5-1`). 범위 판정과 work 인계만 한다. 게임·하네스·test·validator 수정0, 게임 실행0.
- 대상 승격: lap943 work `loop/ESCALATE_SOL`(보존 `docs/history/20261004_lap944_prior_lap943_escalate_sol_byte_exact.txt`).
- 계획 승인·2단 수용·G1 마일스톤이 아니다. lap943 r4의 production은 **UNKNOWN/HOLD 그대로**이며 이 카드로 PASS가 되지 않는다.

## 0. 판정

1. **queue type31이 slot1199(타입58, owner0, 진영2)의 올바른 원본 witness다.** 사전 계약의 type7은 다른 진영 fixture의 상수다.
2. **`(668,540)`은 이 장면에서 일꾼(일본 농부) 생산 칸이다.**
3. 클릭 전 `+0x320 = 31 / progress 100`은 지난 생산의 잔류값이다. 그래서 "type이 7 아닌 값 → 7" 전이는 어떤 타입으로도 성립할 수 없다.
   발행 witness는 **command 15 + progress 되감김 + 발행 단계의 정확한 비용 차감**으로 바꾼다.
4. 무입력 control은 **생산 건물 자체 필드**로 판정하고, player 전체 자원 변화는 숨기지 않고 따로 기록한다.
   대신 효과 판정을 "자원이 아무거나 변함"에서 "발행 단계 비용이 정확히 일치"로 올린다.
5. 다음은 work 1 lap(§3). 재계획 회차 없음. production·G1 HOLD 유지, **G1 계속**.

## 1. 근거 (새 실행 없음)

주소·코드 전문은 `analysis/memory_maps/g1_production_issue_path_40df05_lap944.md`.

| 질문 | 근거 | 출처 |
|---|---|---|
| `+0x320`은 무엇인가 | 발행 코드가 `command=15`(`0x40DF05`), `progress=0`(`0x40DF0E`), `+0x320 = [descriptor*24 + 0x9E2F34]`(`0x40DF21`)를 한 번에 쓴다. 고정값이 아니라 눌린 칸의 유닛 타입이다 | 보호 원본 EXE 디스어셈블 |
| type7은 어디서 왔나 | r4 두 lane에서 command 15인 건물(34개·35개) 중 type7을 만드는 것은 **진영1 건물 타입49**뿐이다(owner5 slot628·1189). G2 ESL2608 Phase C fixture의 "owner0 신규 type7"을 lap815가 save006으로 옮겨 적었다 | r4 raw 재계산, lap792·815 기록 |
| 진영2 HQ는 무엇을 만드나 | owner0 타입58 건물 3개가 클릭 전 모두 `31/100/command 1`, owner0 타입31 유닛 14개 | r4 raw(두 lane 동일) |
| `(668,540)`은 무슨 칸인가 | candidate 캡처의 그 칸 툴팁 `일본 농부 800 / 300 / 10`, 생산 표시 `일본 농부 13%` | `candidate/production.png` 직접 확인 |
| 비용은 맞는가 | 쌀 96807→96007(−800), 나무 30031→29731(−300). 코드상 쌀=spec`+0x12`, 나무=spec`+0x14`, 인구=spec`+0x10` | r4 raw, `0x43F0C0` |
| `reserved`는 무엇인가 | `+0x1C`는 생산 대기 인구다(HUD 1893 = used 1470 + 423). 발행 때 **증가**(+10)한다. r4의 423→403은 5.09초 창에 다른 건물의 생산 완료가 섞인 값이다 | `0x43F118`, `baseline/production.png` |
| 원본 control은 왜 흔들렸나 | 1.0초 창에서 쌀 +640, 같은 창에서 slot1199의 command·`+0x320`·progress는 불변. owner0은 일꾼 14기와 생산 중 건물 여럿이 도는 살아 있는 경제다 | r4 baseline raw |

수용하지 않는 것: candidate 한 lane의 자원 감소를 생산 PASS로 보는 것, 원본 lane 결과 추정(원본은 클릭한 적이 없다).

## 2. 계약 K1~K6 (`tools/g1_saved_scene_probe.py`와 해당 test만)

- **K1 대상.** 선택 count 1·slot1199·owner0·**타입58**. 타입은 "양수"가 아니라 58로 고정한다.
- **K2 control.** 창 ≥ 1.0초, 전후 두 표본 OBSERVED. 판정 필드는 slot1199의 `command`·`+0x320`·`progress`와 정체(slot/owner/type)다.
  하나라도 다르거나 command가 이미 15면 UNKNOWN이고 누르지 않는다. 쌀·나무·`+0x1C`·used의 창 내 변화는
  `control_global_delta`로 **항상 기록**하고 판정에는 넣지 않는다. 표본의 sim tick도 함께 적는다.
- **K3 발행.** 클릭 전에 타입31 spec의 세 단어(`0x9B5228 + 31*0x394 + 0x10/0x12/0x14`, signed word)를 읽어 적는다.
  클릭 뒤 표본열에서 command가 처음 15가 된 표본 `a`, 그 직전 표본 `prev`, 다음 표본 `b`를 raw에 남긴다.
  요구: `a.+0x320 == 31`, `a.progress < prev.progress`, 정체 불변.
- **K4 비용.** `prev→a` 또는 `prev→b`의 (Δ쌀, Δ나무, Δ`+0x1C`)가 (−spec쌀, −spec나무, +spec인구)와 **정확히** 같아야 한다
  (어느 쪽이 맞았는지 기록). 둘 다 아니면 `issue_step_cost = INEXACT`, 그 lane은 UNKNOWN이다. 원값은 지우지 않는다.
  `b`를 허용하는 이유는 host 읽기가 update 도중을 읽는 경우(lap892)다. 그보다 넓은 창은 허용하지 않는다.
- **K5 pair.** 두 lane 모두 K1~K4 PASS이고 queue 타입·spec 세 단어·비용 벡터·slot이 같을 때만 `production_effect = true`.
  기대 타입은 fixture 상수 `31`로 고정한다(근거 주석은 이 카드). 한 lane만의 성공, 타입 불일치, INEXACT는 false다.
- **K6 완료.** 캡처는 지금처럼 발행 직후에 찍는다. 그 뒤 최대 120초(벽시계) 동안 slot1199가 command 15에서 벗어나고
  owner0 타입31 유닛이 클릭 전보다 1 늘어난 것(새 slot)을 본다. 두 lane 모두 보이면 `completion = PASS`,
  시간 안에 못 보면 `UNKNOWN`(발행 판정은 유지), 한 lane만 보이면 HOLD다.

witness 표본은 slot1199 한 칸과 player0 앞부분만 읽어도 된다(전체 장면 읽기는 표본 간격을 넓힌다). 선택 사항이다.

## 3. work 순서 (1 lap)

1. 회귀 RED 먼저: (a) `31/100/cmd1 → 31/13/cmd15`·비용 정확 → 효과 true(지금은 false), (b) 같은 건물에서 after type7 → false,
   (c) control 쌀 +640·건물 필드 불변 → PASS이고 `control_global_delta.rice == 640`, (d) control 중 progress 또는 command 변화 → UNKNOWN·미클릭,
   (e) 발행 단계 Δ쌀 −160 → INEXACT·UNKNOWN, (f) command 15인데 progress 미감소 → false, (g) 쌀만 변하고 command 1 → false,
   (h) pair에서 lane 간 타입 또는 비용 불일치 → `production_effect` false.
2. K1~K6 구현. type7을 고정한 기존 test는 지우지 말고 31과 이 카드 근거로 고친다. 그 밖의 172개는 그대로 통과해야 한다.
3. fresh save006 pair(원본 800×600 / Scale2x 1600×1200, 새 사본·prefix·display). 재중심은 lap943 r4 방식 그대로
   (live LUT → `(129,571)`, 진단 gate는 try/finally exact 복원).
4. 귀속 가능한 결함(좌표·표본 시점·INEXACT)은 같은 회차에서 고쳐 다시 실행한다(PROMPT ③, 3회까지).
5. 기록 freeze → `make lint`·`make typecheck` → `make check` 1회 → STATUS 보강 → 새 middle.

디스크 여유 22GB(2026-10-04). 실행 전 20GB 미만이면 자기 회차의 옛 `game` 사본부터 지운다.

## 4. 사전 등록 예측 (fresh pair에서 틀릴 수 있어야 한다)

- **P-1** 두 lane: camera `[158,101]→[165,87]`, 선택 slot1199/타입58/owner0, gate `00000000→01000000→00000000`.
- **P-2** 두 lane control 전 표본: slot1199 `command 1 / +0x320 31 / progress 100`.
- **P-3** 두 lane: 타입31 spec = 인구 10 / 쌀 800 / 나무 300.
- **P-4** 두 lane: 발행 표본 `command 15 / +0x320 31 / progress < 100`, 비용 벡터 `(−800, −300, +10)` EXACT.
- **P-5** 두 lane: 120초 안에 owner0 타입31 유닛 14→15(그 사이 다른 증감이 없을 때), slot1199 command 15 해제.
- **P-6** 두 lane production 캡처에 같은 생산 표시, V1·V2·V2s·V2q PASS.

P-3이 틀리면 이 카드의 비용 필드 귀속이 틀린 것이다(§6). P-4가 원본 lane에서 틀리면 §5로 간다.

## 5. 판정 분기

| 결과 | 판정 | 다음 |
|---|---|---|
| P-1~P-4 두 lane 성립, P-5 성립 | production `PASS(partial)` 후보 | 새 middle 독립 검수(§7) |
| P-1~P-4 성립, P-5 한쪽 이상 시간 초과 | 발행 parity만 후보, completion UNKNOWN | middle이 raw로 진행률 확인 |
| 원본 lane에서 command 15 불성립(3회 수리 뒤에도) | production `UNKNOWN(original parity)`, candidate 단독 성공은 PASS 아님 | middle. 원본 lane의 X11 주입 증거와 선택 유지 여부를 먼저 본다 |
| 두 lane 타입 또는 비용이 다름 | HOLD — 입력 대응 결함 후보 | work가 candidate WndProc logical 좌표와 원본 주입 좌표를 대조 |
| INEXACT 반복(3회) | UNKNOWN, 원 표본열 보존 | middle이 표본 간격·오염 사건을 raw로 판정 |

## 6. strategy 재호출 조건 (이것 하나를 더한다)

원본 lane이 안정 control 뒤 같은 칸에서 command 15를 내면서 **queue 타입이 31이 아니거나 spec이 `10/800/300`이 아닐 때**만 이 카드를 다시 연다.
그 밖의 HOLD·수리는 work ↔ middle로 처리한다. 기존 조건(lap933 §6, lap938 §7)은 그대로다.

## 7. middle 검수 항목

- raw에서 `prev`/`a`/`b` 세 표본과 spec 세 단어를 직접 다시 계산하고, `control_global_delta`가 0이 아닌 창이 숨겨지지 않았는지 본다.
- 두 lane production PNG를 나란히 본다(생산 표시·툴팁·HUD 인구 표시).
- r4와 fresh pair의 camera 이동은 **진단 gate=1 아래의 parity**다. 정상 gate=0 미니맵은 원본 parity N/A 그대로다.
- 이 카드의 type31 정정이 r4를 소급 PASS로 만들지 않았는지 확인한다.

## 8. 범위 밖

게임 EXE·bridge·mirror·validator·임계값·golden 변경, G2/G5 파일, 새 관측기·gdb 진단, tick 동기 lane 비교(P4b의 torn read 문제를 다시 연다),
정상 gate=0 미니맵 재조사. 생산이 닫힌 뒤 남는 G1 항목(GDI·두 번째 장면·전체 HD coverage ≥ 90%·D-2 scroll 성능·사용자 승인)은
STATUS 목록 그대로이며 이 카드가 순서를 바꾸지 않는다.
