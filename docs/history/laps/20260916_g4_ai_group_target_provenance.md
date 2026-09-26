# G4 original AI group target provenance (2026-09-16)

## 목적과 방법

idle-order 보완 후보가 전역 적 위치를 몰래 사용하는 것을 피하기 위해, 원본 AI가 이미
선택한 group waypoint를 read-only로 관측했다. `runtime_driver.state()`는 private spawned
game의 PlayerStruct 전체 `0x3ABC`를 읽고, 아래 범위만 추가 해석한다.

| 필드 | PlayerStruct 기준 |
|---|---|
| group count | `+0x348A` SHORT, 지원 0..2 |
| group record | `+0x3490 + index*0x2E0` |
| current x/y | record `+0/+2` SHORT |
| route id/state | record `+4/+6` SHORT |
| waypoint count/index/tick | record `+0x2D8/+0x2DA/+0x2DC` |
| route member count | `+0xCBA + route*2` |
| route member IDs | `+0x99A + route*20*4` |

정적 근거는 `FUN_0043CF30/FUN_0043D450`이 같은 target과 member list를 읽고
`FUN_004AEDE0` 원본 이동 order를 발행하는 경로다. route는 0..9, member count는 0..20만
해석한다. route=-1은 member table로 취급하지 않는다.

## 실측

seed7 30초에서는 AI 두 owner 모두 group count 0→2였으나 target(0,0), route-1,
state0으로 끝나 사용 가능한 group waypoint가 없었다.

원본 seed1 180초에서는 다음과 같이 실제 AI-selected waypoint가 나타났다.

| owner | 첫 populated group | target | route/state | members | waypoints |
|---:|---:|---|---|---:|---:|
| 0 | 154.051초 / tick5147 | (9,31) | 0 / 1 | 4 | 71 |
| 1 | 160.317초 / tick5356 | (10,75) | 0 / 1 | 1 | 84 |

둘 다 PlayerStruct `+2 == 1`인 AI owner였다. 180초 endpoint에 각각 같은 target/state를
유지했고 waypoint index가 0→20으로 진행했다. 이 실행에는 intervention이 없었다.

## 판정과 다음 경계

`ORIGINAL_AI_GROUP_TARGETS_OBSERVED`.

원본 AI가 선택한 전략 이동 좌표의 provenance가 생겼다. 이는 hidden enemy entity를 안다고
주장하는 근거가 아니며, 좌표 자체의 path validity도 보증하지 않는다. 다음 private
reinforcement probe는 이 좌표만 원본 movement order로 재사용하고 적 ID는 조회하지 않는다.

지원 AI owner만, pending order 없는 idle mobile combat만, 기존 group member 제외,
owner당 한 기/한 번, map bounds 안의 populated state1 group만 허용하는 중간 검수를 기다린다.
조건이 안 맞으면 개입 없이 끝내며, tick hook/지속 정책/제품 패치는 아직 없다.

보존:

- `temp/Syw2plus_patch/g4_ai/20260916_seed7_group_targets30/`
  - runtime SHA `eb9962e717a014d4ce6278c0c451da7b3efd5cf6316303b1851b38e973076b1a`
- `temp/Syw2plus_patch/g4_ai/20260916_seed1_group_targets180/`
  - runtime SHA `19bf214b4c27c009b0190810a9a43531d95ba2dcd166a6f888069f52414badee`
  - compact report SHA `096f3f1899484d8e57837405b5a4e248273cc4580b2499f35f4a03bc3b7e4af9`
- targeted decoder/runtime tests: **150 passed**, Ruff/mypy PASS
