# PlayerStruct `+0x2010`은 전비(supply)가 아니라 **유닛 개수 상한**

작성: 2026-07-26 (#334, 라운드4 반복4)

## 정정 대상

`plan_c/src/game/economy.h`:

> every PlayerStruct slot inits **supply_current(+0x2010)=250**, supply_limit(+0x2012)=1500

`+0x2010`은 supply_current가 아니다.  **유닛 개수 상한**이다.

## 근거 — 원본 두 함수가 필드 의미를 확정한다

### `FUN_0043EE30` — 소유자 로스터에 유닛을 push

```c
if (0x4af < *(short *)(param_1 + 0x200a)) { /* overflow */ return; }
*(undefined4 *)(param_1 + 0xd4a + *(short *)(param_1 + 0x200a) * 4) = param_2;  // 유닛 id 배열
*(short *)(param_1 + 0x200a) = *(short *)(param_1 + 0x200a) + 1;                // 개수 +1
iVar1 = (short)param_2 * 0x758;                                                 // 유닛 stride
*(short *)(param_1 + 0x200c) =
     *(short *)(param_1 + 0x200c) + *(short *)(&DAT_009b5238 + type * 0x394);   // 전비 누적
if (((&DAT_0066b968)[iVar1] & 2) != 0) *(short *)(param_1 + 0x200e) += 1;       // 특수 클래스 수
```

- `+0xd4a` = 유닛 id 배열, `+0x200a`가 그 **인덱스이자 개수** (상한 0x4af = 1199)
- `+0x200c` = 유닛 타입별 비용(`DAT_009b5238`, 테이블 `+0x10`)의 **누적 합** = 현재 전비
- `+0x200e` = 유닛 플래그 `&2` 인 특수 클래스의 개수

### `FUN_0043EDA0` — 스폰 직전 용량 게이트

```c
if (param_3 == 1) { if (*(short*)(p1+0x2010) <= *(short*)(p1+0x200a)) return 0; }
else              { if (*(short*)(p1+0x2010) - 8 <= *(short*)(p1+0x200a)) return 0; }
if (cost != 0 && *(short*)(p1+0x2012) < *(short*)(p1+0x200c) + cost) return 0;
return FUN_00442fa0(type);
```

`+0x2010`은 **개수(`+0x200a`)와 비교**되고, `+0x2012`는 **전비(`+0x200c`)와 비교**된다.
flag8이 아닌 타입은 상한에서 **8칸을 예약**한다(`-8`).

### 먼저 확인한 것 — 이 함수들이 정말 **PlayerStruct**를 보는가

`+0xd4a`/`+0x200a`는 plan_c 쪽에서 "race-AI owner unit list"로도 불린다
(`runner.cpp:5113`).  그래서 `FUN_0043EDA0`이 PlayerStruct가 아닌 다른 구조체를
보는 것이라면 이 정정 전체가 무효가 된다 — 먼저 그것부터 확인했다.

두 함수 모두 `__thiscall`이라 Ghidra 호출부에는 `this`가 안 보인다
(스탯 테이블에서 썼던 것과 같은 함정).  디스어셈블로 ECX를 읽으면:

```asm
movsx  ecx, BYTE PTR [esi+0x8e]      ; ecx = owner (유닛의 소유자 바이트)
lea    eax, [ecx+ecx*2]              ; 3*owner
shl    eax, 0x4                      ; 48*owner
sub    eax, ecx                      ; 47*owner
lea    edx, [eax+eax*4]              ; 235*owner
shl    edx, 0x4                      ; 3760*owner
sub    edx, ecx                      ; 3759*owner
lea    ecx, [edx*4+0x956770]         ; 15036*owner + 0x956770
call   0x43eda0
```

`15036 = 0x3ABC` = **PlayerStruct stride**, base `0x956770`.
(교차 확인: 이미 알려진 `DAT_00956772` = PlayerStruct `+0x02` is_cpu →
`0x956770 + 2` 와 일치.)

→ `FUN_0043EDA0`은 확실히 PlayerStruct를 읽는다.  정정은 유효하다.

### 바이너리 전체 확인

디컴파일 전체에서 `+0x2010`이 등장하는 곳은 셋뿐이고 **전부 개수와의 비교**다:

```
*(short *)(param_1 + 0x2010) <= *(short *)(param_1 + 0x200a)
*(short *)(param_1 + 0x2010) + -8 <= (int)*(short *)(param_1 + 0x200a)
(int)*(short *)(param_1 + 0x2010) / 5 <= (int)*(short *)(param_1 + 0x200e)
```

소비되는(감소하는) 값으로 쓰이는 자리는 **하나도 없다**.
(`/5`는 특수 클래스가 전체 상한의 20%를 넘지 못하게 하는 하위 상한이다.)

따라서 캡처가 보여준 `+0x2010 = 250`은 "현재 전비 250"이 아니라 **"유닛 250기 상한"**이다.
`+0x2012 = 1500`(전비 상한)은 기존 라벨이 맞다.

## ⭐ 살아있는 원본 프로세스 실측 (2026-07-26 반복8)

디컴파일 논증만으로 끝내지 않고 **원본을 gdb로 돌려 실제 값을 읽었다**
(seed13, frame 4681, `0x406D15` 브레이크포인트, PlayerStruct `0x956770 + p*0x3ABC`):

| player | `+0x200a` count | `+0x2010` | `+0x200c` | `+0x2012` | `+0x200e` |
|---|---|---|---|---|---|
| 0 | 2 | **250** | **20** | 1500 | 1 |
| 1 | 9 | **250** | **95** | 1500 | 5 |

이 한 장이 라벨 논쟁을 끝낸다:

- `+0x2010 = 250`이 **유닛 개수(`+0x200a` = 9, 2)와 비교되는 상한**이라는 것이 실측으로 확인된다.
  250이 "현재 전비"라면 유닛 9기와 비교될 이유가 없다.
- **실제로 누적되는 전비는 `+0x200c`다** — player0은 유닛 2기에 20, player1은 9기에 95.
  유닛 수에 비례해 늘어난다(타입별 비용 누적).  `+0x2012 = 1500`이 그 상한이다.

### 같은 캡처가 드러낸 plan_c 결함 (측정값 대조)

| | 원본 @f4681 | plan_c @tick4680 |
|---|---|---|
| `+0x200c` 누적 전비 | player0 **20** / player1 **95** | `player_supply_produced` = **전부 0** |
| `+0x2010` 유닛 상한 | 250 | `player_supply_current` = 250 (이름만 틀림) |

plan_c는 전비를 **한 번도 누적하지 않는다**.  원본은 유닛이 로스터에 들어갈 때마다
`FUN_0043EE30`에서 타입별 비용을 더한다.  이건 이제 추론이 아니라 **측정된 차이**다.

⚠ 다만 이 차이가 seed13 f6242 잉여 스폰을 설명하지는 **않는다**.  원본 값으로
`FUN_0043EDA0`을 평가해도 게이트는 통과한다(`250-8=242 <= 9` 거짓,
`1500 < 95+10` 거짓).  전비 회계 갭은 그 자체로 고칠 가치가 있는 별개 결함이다.

캡처 보존: `temp/seed13_capacity_fields_0726/`

## 파급 — plan_c 쪽 실제 상태

1. **이름만 틀렸고 값은 맞다.**  `kInitialSupplyCurrent`/`Economy::supply_current`/
   JSON `player_supply_current`가 33곳에서 참조되고 save/load 필드명까지 걸려 있어
   이번에는 **개명하지 않았다**.  라벨과 경고만 정확히 했다 (라운드3의
   `attack_range`/`move_speed`, 라운드4의 `instant_kill_threshold`와 같은 판단).
2. **전비 회계 자체는 충실히 모델링돼 있다** — 처음에 "plan_c는 `+0x200c` 누적을
   하지 않는다"고 적었는데 부정확했다.  `Economy::try_spend`가 `FUN_0043F0C0`을
   (`+0x200c + +0x1c + cost <= +0x2012`, 예약분 `+0x1c` 포함까지) 포팅했고
   `production_phase.cpp:435`, `command_dispatcher.cpp:7810` 등 여러 경로가 쓴다.
   `FUN_0043EDA0`의 검사(`+0x2012 < +0x200c + cost`)에 `+0x1c`가 없는 것도 불일치가
   아니다 — 예약을 만드는 함수와 스폰 직전 게이트는 원본에서도 서로 다른 사이트다.
3. **진짜 갭은 한 곳으로 모인다: AI 생산 파이프라인이 이 둘을 모두 우회한다.**
   `tick_scheduler.cpp:23691-23718`은 `try_spend`도, `FUN_0043EDA0` 게이트
   (`unit_ai.cpp:2885`에 충실히 포팅돼 있다)도 부르지 않고 타일 탐색 → 스폰으로
   직행한다.  그래서 이 경로로 생산된 유닛은 전비를 소비하지도, 용량 검사를 받지도
   않는다 (무입력 seed13에서 `player_supply_produced`가 끝까지 0인 이유).
   → [[seed13-f6242-spurious-production-0726]]

⚠ 단, 이 셋 중 어느 것도 seed13 f6242 잉여 스폰을 설명하지 못한다.
개수 상한 250(−8=242)은 유닛 14기 앞에서 멀고, 전비 상한 1500은 16기×비용≈160 앞에서 멀다.
**과대주장 금지** — 이 문서는 라벨과 누락을 바로잡을 뿐 f6242를 닫지 않는다.

## 같은 패턴의 세 번째 사례

이 레포에서 "한 오프셋에 두 라벨"이 이번이 세 번째다:

| 라운드 | 오프셋 | 잘못된 라벨 | 실제 |
|---|---|---|---|
| 3 | +0x30 / +0x36 | attack_range / move_speed (뒤바뀜) | move_speed / attack_range |
| 4 | +0x32 | instant_kill_threshold | AI 생산 비율 상한 |
| 4 | +0x2010 | supply_current | 유닛 개수 상한 |

셋 다 "값은 맞고 이름이 틀린" 형태라 테스트가 잡지 못했다.

## 출처

- `analysis/ghidra_output/FUN_0043ee30.c`, `FUN_0043eda0.c`, `FUN_0043e7f0.c`
- `plan_c/src/game/economy.h`, `plan_c/src/game/unit_ai.cpp:2885`
- 잠금: `plan_c/tests/test_player_struct_field_labels_0726.py`
