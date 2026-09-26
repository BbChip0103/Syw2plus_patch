# G4 controller opcode outcome windows (2026-09-16)

## 목적

threshold를 더 낮추기 전에 원본 opcode가 선택된 뒤 오래 막혀 있는지 확인했다.
`tools/g4_controller_outcomes.py`는 dense sample에서 controller opcode의 시작/종료, 점유 tick,
0 복귀 여부, 같은 창의 자원·유닛 delta를 추출한다.

## 결과

### seed7 초기 30초 / 0.1초 sample

- owner0/1 모두 관측된 opcode `0x01`, `0x03`, `0x12`가 전부 0으로 복귀했다.
- 최대 점유: 건설 `0x01` 13 tick, 채집 `0x03` 6 tick, 집결 `0x12` 7 tick.
- 즉 초기 약점은 opcode가 완료되지 못하고 고착되는 현상이 아니다.

### seed1 전투 포함 240초 / 0.25초 sample

- 959 sample, 실제 피해/소멸이 있는 구간까지 포함했다.
- owner0/1 건설 `0x01`은 각각 26/14회, 최대 9 tick 뒤 전부 0 복귀했다.
- 짧은 `0x03`, `0x0B`, `0x12`는 대부분 한 sample 안에 끝났고 열린 채 끝난 창은 0개였다.
- 0.25초보다 짧은 opcode는 정확한 duration을 0 tick으로 보므로 호출 전수 trace가 아니다.
  다만 장기 점유/고착이 없다는 판정에는 충분하다.

## 판정

`NO_STUCK_CONTROLLER_WINDOW_OBSERVED`.

단일 cooldown을 더 낮추는 방향은 병목과 맞지 않는다. 두 실제 후보가 이미 selector 위상을
진영별로 다르게 재배열해 `NO_GO`였으므로, 다음 후보는 원본 명령의 결과 품질(목표 선택,
이동 성공, 교전 성과)을 직접 계량해야 한다.

- seed7 report SHA: `7dfe39742bf17690f89c29241403413910b1af0c367e8f6b71fce396046be9f5`.
- seed1 240초 report SHA: `f69c46704b21a86e938f810ea25ed9b6271a8c6d5ec1039a337235ef811560b3`.
