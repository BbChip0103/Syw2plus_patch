# G4 original mobile-unit movement outcomes (2026-09-16)

## 방법

`tools/g4_unit_movement_outcomes.py`가 seed1 원본 240초/0.25초 959 sample의
`(internal_id,type,owner,x,y,command)`를 추적했다. 이동 가능 type은 보호된 메인 연구 저장소의
원본 실측 unit template mirror `unit_template_raw_0703.h`에서 `flags_4c & 1`인 type으로
분류했다. 최소 300 tick 이상 관측된 mobile identity만 집계했다.

## 결과

| owner | eligible mobile | moved | stationary |
|---|---:|---:|---:|
| 0 (Joseon) | 26 | 17 | **9** |
| 1 (Japan) | 23 | 22 | **1** |

owner0 stationary 9기는 type2 2기, type4 5기, type10 2기였다. 가장 긴 type2 한 기는
3049 tick, type4 한 기는 2623 tick 동안 좌표가 한 칸도 바뀌지 않았다. 9기 전부 모든
관측 sample에서 `command=1`이었다. owner1 stationary type12 한 기 역시 769 tick 동안
`command=1`이었다.

## 판정

`IDLE_COMMAND_ISSUANCE_GAP_OBSERVED`.

이 유닛들은 이동 명령을 받고도 길찾기에 실패한 것이 아니다. 애초에 idle command만 유지해
pathfinder가 호출될 기회가 없었다. 따라서 현재 fixture에서 먼저 고칠 축은 A* 상수나
controller cooldown이 아니라 **idle mobile unit에 유효한 목표/명령을 발행하는 경로**다.

- report SHA: `ef6193f4bfaca04aa9961241f8c657a5354177436ef40be1392697fc3a543aba`.
- 한계: type mobility 분류는 captured template flag에 의존하고, 240초 한 seed의 국가/slot
  비대칭을 일반화하지 않는다. 다음 probe는 명령 발행 후 실제 이동/피해가 생기는지 대조한다.
