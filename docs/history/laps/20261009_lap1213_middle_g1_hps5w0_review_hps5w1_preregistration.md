# 2026-10-09 | lap 1213 | G1 middle — H-PS5W0 검수(불일치 0·정정 2) + 정적 귀속 + H-PS5W1 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`/high, 중간 계획·컨펌(middle). 게임 코드·하네스 수정 0.
- 가설 / 사용자 관찰: (검수 대상) lap1212 work H-PS5W0 — PS5 영구 stale 5,044 px는 지도 목록 띠에 있고, 표본 3점 writer는 게임 block_copy `0x466280`(A)과 `wined3d.dll` 스레드(B)다. lap1211 가설("기존 hook 밖 writer")은 반증이다. 사용자 관찰 없음.
- 예상 PASS / FAIL 조건: lap1212 raw를 새 스크립트로 다시 계산해 수치 불일치 0이면 수용한다. ESCALATE_SOL 질문(반증 판정·다음 work 사전등록)에 답한다.
- 변경 파일 / source fingerprint / 커밋: 문서만 바꿨다(이 기록, ESCALATE_SOL 보존본, STATUS, INBOX 메모). 공유 temp에 재계산 스크립트와 역어셈블 발췌를 뒀다. 제품 C·하네스·테스트 변경 0. 커밋 없음(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…` read-only MATCH(직접 재계산). 역어셈블은 공유 temp의 읽기 전용 사본으로 했고 사본은 끝나고 지웠다. lap1212 DLL M1 `7bcae344…`·W1 `caf18b69…`, 팩 끔, 새 게임 대기실, fixture 없음.
- 실행 명령 / 로그: 게임 run 0. 공유 temp `20261009_lap1213_middle_review/`:
  - `recalc_lap1213.py`(`ab15a75c…`) → `recalc_lap1213.json`(`b03e0bf0…`). work의 `mask_ana.py`를 쓰지 않고 새로 썼다.
  - `orig_4b6380.asm`(`16f0424d…`) = 원본 `0x4B6380..0x4B6700`(PS5 프레임 함수) 발췌.
- ESCALATE_SOL: 원문을 byte 일치로 보존했다(`docs/history/laps/20261009_lap1213_preserved_lap1212_escalate_sol.txt` `913301c7…`). 보존 뒤 원본은 삭제했다.

## 1. 독립 재계산 — 불일치 0

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| M1 `stale_mask.bin` | 4,800,320 B·10 dump·`3486936a…` | 같음 | 일치 |
| dump ord 300~309 mask 값2 = header stale = trace `stale_pixels` | 5,044 ×10 | 5,044 ×10(trace는 `mirror2x_present` 0-based 순번 509~518, PS5) | 일치 |
| 10 dump 교집합 = 합집합 | 5,044 | 5,044 / 5,044 | 일치 |
| lap1156 띠(x445..593·y118..287) 안 | 4,685 = 92.9% | 4,685 = 92.88% | 일치 |
| 연결 성분(8-연결) | 62 | 62 | 일치 |
| 표본 3점이 성분 안(3×3 전부 stale) | 예 | 3/3 | 일치 |
| W1 `screen_watch.jsonl` | `648fb900…`·x 3,954줄 | 같음, present 묶음 659개 | 일치 |
| 묶음마다 쓰기 순서 | A 직후 B | `AAABBB` 659/659 | 일치 |
| A = EIP `0x4662DE` tid 280(present 스레드) | 3×659 | 1,977, 값 121·217·163 고정 | 일치 |
| B = `wined3d.dll` EIP `0x73A399CF` tid 288 | 3×659 | 1,977 | 일치 |

추가로 확인한 것(work 기록에 없던 값):
- PS5 present 693개 전부에서 `menu_copy_calls`가 present마다 +1, `menu_copy_pixels`가 +480,000이다. 복사 블록 해시 `menu_copy_hash_last` = 269350933로 693/693 같다. covered는 693/693이 480,000이다. 즉 PS5 block copy는 **x=y=0 800×600 전면 복사이고, 매 present 미러에 채택된다**. work의 UNKNOWN (1)("`transfer_block_copy_to_screen` 채택 여부")은 이것으로 닫는다. 진입 인자 계측은 필요 없다.
- PS5 전 구간 stale 분포: 5,044 567개·5,043 125개·4,684 1개.
- 캡처: 후보 `ps5.png`(1600×1200)의 2×2 좌상 화소와 원본 `ps5.png`(800×600)를 stale 5,044 화소에서 비교했다. **5,044/5,044가 같은 색이다.** 표본 세 점도 같다((549,219)·(521,140) 검정, (458,281) (152,168,168)).

## 2. 정정 2

**정정 1 — work의 W0-1 "= trace `stale_pixels`(10/10)"는 work 스크립트로는 확인되지 않았다.** `mask_ana.py`는 trace를 `present_count` 키로 묶는다. 그런데 `mirror2x_present` 이벤트에는 그 키가 없다. 그래서 모든 이벤트가 키 `None` 하나로 모이고, trace 값은 `None`으로 찍힌다. 다만 값 자체는 맞다. mask header의 present는 이벤트의 0-based 순번이다. 이 순번으로 묶으면 10/10이 5,044다(§1). 판정 영향은 0이다. 다음 work 스크립트는 순번으로 묶는다.

**정정 2 — B는 "쓰기 전 값으로 되돌리기"가 아니라 글자를 쓰는 writer다.** work는 B가 A가 쓰기 전 값(0·100·0)으로 되돌린다고 적었다. 실제 값은 이렇다:
- B는 점 0·2에 0(검정 = 글자 그림자), 점 1에 30을 쓴다. 점 1은 앞 117묶음에서 100이었다가 그 뒤 30이 된다(글자색이 바뀜, 예: 선택/hover).
- 다음 묶음에서 A가 쓰기 전 값은 직전 묶음 B 값과 1,316/1,316 같다. 즉 "A 이전 값"이 원래 배경이 아니라, 직전 present에서 B가 쓴 글자다.
- 원본 캡처도 이 화소들에서 B 값(글자)을 보인다.

결론: A = 배경 그림 전면 복사, B = 그 위에 얹히는 **글자**다. 후보 stale = "미러가 A(배경)를 expected로 기록했는데, present 시점 화면에는 B(글자)가 있다".

## 3. 정적 귀속 — B의 유발 호출은 기존 훅에 안 잡히는 글자 스크래치 BltFast다

원본 PS5 프레임 함수(`0x4B6380~`, `orig_4b6380.asm`)의 순서:
1. `0x464E20` 잠금.
2. `0x4B6486 call 0x466280` = A: `0xE5BF18` 캐시에서 x=y=0 전면 복사.
3. `0x4B6496 call 0x465080` = 화면 표면 `[0xE5D438]` Unlock. 근거: vtable `+0x80`은 IDirectDrawSurface 슬롯 32 Unlock이다.
4. `0x4B6609 call 0x4B6C70([0xE5D438])` — 좌측 이름 8줄. `0x4B6D63 call [vtbl+0x1C]`는 BltFast다. 목적지 `[0xE5D438]`, 원본 = 글자 스크래치 `[0x104F810]`, 플래그 `0x11`(SRCCOLORKEY|WAIT), 좌표 x=20·y=44..462다. 이것이 work가 적은 띠 밖 좌측 글자 둘(x36..63·y46..54, x21..41·y106..114)과 맞다.
5. `0x4B661D call 0x4B6E50([0xE5D438])` — 화면 표면 `GetDC`(`+0x44`)와 TextOutA(x=240) 경로. 이 경로는 lap1155의 `dc_screen` 수리 대상이다.
6. `0x4B663D call 0x4B71A0([0xE5D438])` — 가운데 정렬 글자. `0x4B7366`에서 같은 스크래치 `[0x104F810]`를 BltFast `0x11`로 붙인다.
7. 그 밖의 UI는 `0x4CB790` 등을 거친다. 같은 스크래치를 원본으로 쓰는 BltFast 호출 지점은 바이너리 전체에서 7곳이다: `0x4048CF`·`0x405A03`·`0x4B6D63`·`0x4B7366`·`0x4D1335`·`0x4D1E24`·`0x4D77E7`. 지도 목록이 이 중 어느 지점을 거치는지는 정적으로 확정하지 못했다.

W1 screen watch의 표면 호출 표(`t:q`)에는 PS5 present마다 호출이 **1건뿐**이다. caller `0x49273F`, kind 2(BltFast), 목적지 primary로, present 자체다. 위 4·6의 BltFast는 표에 없다. 표에 들어가는 것은 trace가 vtable을 복제한 표면(record)의 Blt/BltFast뿐이다. 그러니 `[0xE5D438]` 인터페이스는 **복제되지 않은 vtable**이다. lap1148 PS20 브리핑과 같은 계열이다.

Wine에서는 이 BltFast가 wined3d CS 스레드에서 비동기로 실행된다. 그래서 tid 288, `wined3d.dll`, 스택 반환 0으로 보인다. 실제 Windows에서는 드라이버가 동기로 실행한다. 미러가 이 호출을 못 보는 것은 같으므로 stale은 Windows에서도 생긴다. work UNKNOWN (2)("B가 Wine 전용인지")는 이렇게 답한다: **시점은 Wine 고유이지만 결함(미후킹)은 제품 결함이다.**

TextOutA 거부 계수도 같은 그림이다. M1 trace 집계 `textout_iat_reject_target_ps5` 15,242는 전부 `dc_buffer`다. 즉 글자는 스크래치 DC에 그려진 뒤 위 BltFast로 화면에 붙는다(lap1156 "줄마다 스크래치 너비 대응" 정황과 맞음).

## 4. 판정

- **H-PS5W0 `PASS(partial, 귀속)` 수용.** W0-0·W0-1·W0-2·W0-3 수치는 불일치 0이다. 정정은 2건이고 판정 영향은 0이다.
- lap1211 가설("기존 미러 hook 밖 writer")은 **절반만 반증**이다. A(block copy)는 기존 hook이고 정상 채택된다. stale을 만드는 B는 hook 밖 writer다. 다만 그 실체는 "스크래치→화면 복사 함수"가 아니라 복제되지 않은 화면 인터페이스의 BltFast다. lap1156 backlog의 "(ii) 스크래치→화면 복사 경로" 정황은 정적으로 맞았다.
- **가시 효과:** 내용은 원본과 같다(5,044/5,044). stale 화소는 present 경로에서 source nearest 2배로 나간다. 그러니 차이는 글자 1,600×1,200 확대 화질(nearest vs Scale2x)과 글자 주변 Scale2x 이웃 링뿐이다. 깨짐·누락은 없다.
- 이 수리를 이어가는 이유가 있다. 이 화면 인터페이스의 BltFast는 PS5만의 경로가 아니다(호출 지점 7곳). PS7 1,398 px와 일부 게임 안 글자의 같은 계열 잔여를 한 수리로 줄일 수 있다. V1(HD 마스크 밖 출력 = nearest) 같은 validator 의미는 바꾸지 않는다. 미러가 글자를 덮으면 그 화소가 마스크 안으로 들어올 뿐이다.
- 검토 후 버린 대안: "stale 화소를 nearest 대신 source Scale2x로 내보내기". V1 `hd_mask_outside_diff_subpixels`=0 gate의 의미를 바꾸는 변경이다. 기준/validator 무완화 규칙과 W-1 선례(gate 의미 변경 = 사용자 결정)에 걸리므로 하지 않는다.

## 5. 다음 work 사전등록 — H-PS5W1: 복제되지 않은 화면 인터페이스 BltFast(글자 스크래치) diff 미러

**가설:** PS5 영구 stale(지도 목록 92.9% + 좌측 이름)은 화면 표면 `[0xE5D438]`의 복제되지 않은 vtable BltFast(원본 `[0x104F810]`, `0x11`)가 미러 밖에서 글자를 쓰기 때문이다. 이 BltFast 슬롯을 기존 BltFast overlay/diff 미러 경로로 보내면 stale이 사라지고 글자가 HD(Scale2x)로 나온다.

**구성:** 현재 트리 DLL, 팩 끔, 기본 env. 명령 기반은 lap1212 M1(`--new-game-path --new-game-start --hd-source scale2x --stale-mask 300-309 --stale-mask-state 5`)이다. 템플릿은 공유 temp `20261009_lap1212_work_hps5w0/scripts/`다. 격리 game 사본·prefix·빈 Xvfb를 쓰고, run마다 `game` 사본만 지운다. trace 묶기는 `mirror2x_present` 0-based 순번으로 한다(§2 정정 1).

| 단계 | 할 일 | PASS 조건 |
|---|---|---|
| W1-0 확인(옵트인 진단) | PS5에서 `[0xE5D438]` 인터페이스 vtable 포인터를 읽는다. trace record들의 원래/복제 vtable과 같은지 기록한다. 그 BltFast 슬롯을 거치는 호출의 반환 주소·원본 표면·x,y·src rect·flags를 present당 집계한다. | vtable이 record 밖이다. PS5 present당 호출 ≥1이고 반환 주소 ⊂ {`0x4048D2`·`0x405A06`·`0x4B6D66`·`0x4B7369`·`0x4D1338`·`0x4D1E27`·`0x4D77EA`}다. 목적 사각형 합집합이 M1 stale mask 5,044의 ≥90%를 덮는다. |
| W1-1 수리 | 그 vtable 슬롯 BltFast를 기존 BltFast overlay/diff 미러 경로(lap969 H-T 계열)로 보낸다. 원본 호출 뒤 바뀐 화소만 expected/covered/HD로 옮긴다. Wine 비동기 실행을 고려해 비교 전에 실제 결과가 반영됐는지 보장한다(예: Lock). 기본 켬, 끔 env `SYW2_G1_SCRATCH_BLTFAST_MIRROR=0`. 설치·원복·버전 불일치 거부를 기존 vtable hook 규약대로 한다. 호스트 테스트로 경로 연결·끔 env를 RED→GREEN한다. | 테스트 RED→GREEN. 끔이면 바이트 동작이 현행과 같다. |
| W1-2 PS5 측정 | 켬 2 run·끔 1 run(M1 명령). | 켬: PS5 ord 300~309 trace stale ≤504(5,044 대비 ≥90% 감소), 2/2. 끔: 5,044±1 재현. 이전 stale 화소에서 후보 2×2 좌상 = 원본 캡처 ≥99%(내용 불변). 안전 7종 0. PS5 p95(켬−끔) ≤ +2 ms. PS7 stale(현재 1,398)은 보고만 한다(gate 아님). |
| W1-3 비회귀 | save006 full pair 1회. NG5(`--new-game-act --new-game-play`) 1회. | pair PASS(입력효과 7/7·V1/V2/V2s(W-1)/V2q/Scale2x·minimap parity). NG5 PS3 안전 0·p95 비회귀(끔 대비 ≤ +2 ms). 게임 안 호출 지점(`0x4048D2`·`0x405A06` 등)이 켬에서 잡히면 그 수와 stale 변화를 기록한다. |

**결론 규칙:**
- W1-0에서 그 vtable 호출이 0이면 §3 정적 귀속은 반증이다. vtable이 record와 같아도 반증이다. 이 경우 수리 없이 근거를 기록하고 middle로 넘긴다.
- W1-2 감소가 50% 미만이면 `FAIL`이다. 기본값은 끔으로 두고 귀속을 middle로 돌려보낸다.
- 50~90% 감소면 `PASS(partial)`이다. 남은 stale 위치를 mask로 기록한다.
- Wine 비동기 때문에 diff 비교가 비면(바뀐 화소 0인데 stale 불변) 동기화 방법을 바꿔 최대 3 cycle 수리→재실행한다. 그래도 안 되면 `BLOCKED`로 둔다.

**하지 않는 것:** V1 등 validator·gate 의미 변경, stale 출력 방식 변경, 팩 켬, 시험판 재스테이징(가시 효과가 작다; 다음 묶음 때 함께), G2~G5 접촉.

**검사:** 테스트 RED→GREEN, `make lint`·`make typecheck` 뒤 `make check` 1회, SAFETY. 장기 run은 세션이 끝까지 기다린다(PID·`.exit` 파일 대기, `pgrep -f` 자기 일치 금지).

**우선순위 예외:** 사용자 업스케일 결과나 G1 시험 결과가 INBOX에 오면 그것이 최우선이다(H-HDU3는 middle이 사전등록).

## 6. 검증

- 이번 회차 변경: 문서(STATUS·INBOX 메모·이 기록·ESCALATE_SOL 보존본)와 공유 temp 재계산 스크립트·역어셈블 발췌뿐이다.
- 전체 `make check`는 SKIP했다. source는 lap1212 full PASS 2117 그대로이고, 그 뒤 바뀐 source는 0이다.
- SAFETY·CONTEXT 결과는 STATUS에 보강한다.
- 원본 SHA MATCH. 게임 run 0. 커밋 0.

## 7. 다음 한 가지

work H-PS5W1(§5). 사용자 업스케일·G1 시험 결과가 오면 그것이 최우선이다.
