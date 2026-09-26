# PlayerStruct `+0x200c` 전비 누적 규칙 — 원본 실측으로 **정확히** 검증됨

작성: 2026-07-26 (#334, 라운드4 반복9)

## 규칙

```
+0x200c  =  Σ  cost[unit_type]     (그 소유자의 로스터 +0xd4a 에 등록된 유닛 전부)
cost     =  DAT_009b5238[unit_type]  =  유닛 타입 테이블 byte +0x10  =  args[4]
```

원본 `FUN_0043EE30`(로스터 push)이 유닛마다 `+0x200c += DAT_009b5238[type]` 하는 것과 일치한다.

## 검증 — 원본 런타임 실측과 자릿수까지 일치

seed13 frame 4681, gdb로 원본 PlayerStruct(`0x956770 + p*0x3ABC`)를 직접 읽은 값:

| player | `+0x200a` (개수) | `+0x200c` (전비) |
|---|---|---|
| 0 | 2 | **20** |
| 1 | 9 | **95** |

같은 시점 plan_c의 로스터(`race_ai_owner_unit_list_count`)는 **`[2, 9, ...]`로 원본과 동일**하고,
그 유닛들의 타입에 위 cost를 적용하면:

```
owner0: type21=10, type70=10                                        합 20  == 원본 20  ✅
owner1: 31=10, 60=15, 62=10, 31=10, 106=10, 31=10, 57=10, 31=10, 58=10
                                                                    합 95  == 원본 95  ✅
```

두 소유자 모두 **정확히 일치**한다.  cost 값 자체도 원시 프로세스 메모리 캡처
(`unit_templates_9b5228_394x152.raw` byte `+0x10`)에서 읽은 것이라 순환이 아니다.

## plan_c 현황 — 누적을 전혀 하지 않는다

| | 원본 @f4681 | plan_c @tick4680 |
|---|---|---|
| `+0x200c` | 20 / 95 | `player_supply_produced` = **[0]×8** |

`Economy::try_spend`(`FUN_0043F0C0` 포팅)는 있지만 AI 생산 경로가 부르지 않고,
`FUN_0043EE30`에 해당하는 **로스터 등록 시 누적**은 어디에도 없다.

## ⚠ 구현하지 않은 이유 (init 시점 모순 미해결)

규칙은 f4681에서 정확하지만, **초기 틱에서 앞뒤가 맞지 않는다**:

- `plan_c/tests/test_noinput_player_supply_0204.py`는 **첫 틱**의
  `player_supply_produced == [0]*8`을 잠근다.  이 테스트는 자신을 "NON-CIRCULAR,
  원본 L2 gdb 캡처(`sandbox_0204_player_resources_noinput_seed42`)에서 온 값"이라고 밝힌다.
- 그런데 plan_c의 첫 틱 로스터는 이미 `[2, 2, ...]`다.  위 규칙을 그대로 구현하면
  첫 틱에 0이 아니라 ~20이 나와 그 테스트와 충돌한다.
- ⚠ **그 캡처 디렉토리가 레포에 없다** —
  `plan_c/verification/captures/original/sandbox_0204_player_resources_noinput_seed42` 부재.
  따라서 "원본도 init에 0이었는가"를 내가 확인할 방법이 지금 없다.

가능한 해석 두 가지 (미결):

1. 원본도 init 시점엔 로스터가 비어 있고(시작 유닛이 아직 `FUN_0043EE30`을 통과하지 않음)
   나중에 등록되면서 `+0x200c`가 채워진다 → 그렇다면 plan_c의 **로스터 채우는 시점**이
   원본보다 이르다는 뜻이고, 고칠 곳은 누적이 아니라 등록 타이밍이다.
2. 테스트의 `[0]*8` 기대값이 로스터 등록 **이전** 시점을 캡처한 것이다 → 그렇다면
   기대값 자체가 특정 시점에만 유효한 스냅샷이다.

**어느 쪽인지 모르는 채로 구현하면 fit이거나 비순환 락을 깨뜨리는 것 중 하나가 된다.**
그래서 규칙만 확정해 두고 구현은 보류한다.

## 다음 착수점 (구현 전에 반드시)

원본에서 **초기 프레임의 `+0x200a`와 `+0x200c`를 함께** 캡처해 둘이 어떻게 같이 자라는지 본다.
- 캡처 도구는 이미 준비됨: `gdb_capture_tick_draw_attribution.py`의
  `_read_race_ai_context`가 이번에 `unit_cap_2010 / supply_used_200c / supply_limit_2012 /
  special_count_200e`를 읽도록 확장됐다(순수 추가).
- 다만 현재는 `production_pick_context`(0x406D15) 히트에서만 덤프된다 —
  **초기 프레임에는 픽이 없으므로** frame_units 이벤트 쪽에도 같은 덤프를 붙여야 한다.
- 그 결과로 위 해석 1/2 중 하나가 정해지면 그때 구현한다.

## 출처

- 원본 실측: `temp/seed13_capacity_fields_0726/tick_draw_noinput.jsonl` (seed13 f4681)
- cost 테이블: `plan_c/verification/captures/original/ai_static_tables_0703/tables/
  unit_templates_9b5228_394x152.raw` byte `+0x10`
- `analysis/ghidra_output/FUN_0043ee30.c`
- 관련: [[player-struct-2010-is-unit-cap-not-supply-0726]]
