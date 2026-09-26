# G4 idle attack intervention (2026-09-16)

## 질문

원본 seed1 자유대전에서 장시간 `command=1`로 정지한 이동·전투 유닛에 공격 명령을
발행하면 실제 이동 파이프라인이 시작되는가?

이 probe는 진단 전용이다. 출시 패치가 아니며 유닛 생성, type 변경, pathfinder 변경은
하지 않았다.

## 방법

- 원본 EXE SHA-256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- fixture: seed1, 원본 EXE, 180초, 0.25초 표본
- 150.245초에 owner0의 `command=1`인 mobile combat 유닛을 최대 16기 탐색
- 각 유닛에 가장 가까운 생존 owner1 유닛의 UID low16을 `Unit+0x64A`에 기록하고
  `command=4`를 `Unit+0x290`에 기록
- 실제 발행: 4기
- 진단 bridge SHA-256:
  `094bcaf9e49e35f3b5effc83ed43271e23c60cebd798c2dd0829b8e9b4d3604d`

## 결과

| internal id | 개입 직전 | 개입 후 명령 | 이후 서로 다른 좌표 수 | 마지막 좌표 | 이동 |
|---:|---|---:|---:|---|---|
| 1173 | cmd1 @(11,12) | 4 | 1 | (11,12) | 아니오 |
| 328848 | cmd1 @(9,14) | 4 | 1 | (9,14) | 아니오 |
| 591003 | cmd1 @(9,10) | 4 | 1 | (9,10) | 아니오 |
| 787609 | cmd1 @(7,12) | 4 | 1 | (7,12) | 아니오 |

4기 모두 마지막 표본(179.911초)까지 `command=4`를 유지했지만 좌표 변화는 없었다.
전체 실행에서도 HP 감소는 0건이었다.

보존 산출물:

- `temp/Syw2plus_patch/g4_ai/20260916_seed1_idle_attack_probe180/`
- compact report SHA-256:
  `02ac73db1b0f6b378c6e1d2685d753c458e6175127e566e13e475effc7580163`
- full runtime JSON SHA-256:
  `148104da94f5627d6c5d14c4159c330ff0f84195e75c89e946d5e3ca99c18740`

## 판정

`DIRECT_COMMAND_FIELDS_INSUFFICIENT`.

`target UID + command=4` 직접 기록만으로는 이동 상태가 시작되지 않았다. 이 결과는
**pathfinder 실패를 증명하지 않는다**. 원본 명령 발행 경로가 함께 초기화하는 추가 상태,
큐, 좌표, 또는 함수 호출이 빠졌을 수 있다. 따라서 직접 필드 쓰기 방식은 여기서 중단하고,
다음 단계는 원본 command 발행 함수와 그 상태 전이를 정적으로 추적한 뒤 그 함수를 이용하는
단일 bounded probe로 제한한다.

