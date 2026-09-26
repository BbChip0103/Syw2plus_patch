# lap105 escalation — G1 presentation boundary blocker

## 상태

이번 바퀴의 G1 2배 presentation-boundary 정적 probe는 concrete blocker다. 구현, 테스트,
binary, dependency, fixture, baseline, runtime은 변경하지 않았다. 현재 G1 PASS나 milestone
승인을 만들지 않는다.

## 고정 근거

- 읽기 전용 source `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus/syw2plus_original.exe`와
  lap73 private copy `local/runtime/20260911_082430_2926029_0/game/syw2plus_original.exe`가
  SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp=0`, PE32 GUI Intel 80386이다.
- DirectDrawCreateEx IAT thunk `0x004d7938`의 old bytes는 `ff 25 18 50 4e 00`, 유일한 direct
  caller `0x00464374`의 old bytes는 `e8 bf 35 07 00`이다.
- mode3 source setup은 `0x00464502: c7 46 04 20 03 00 00` (800) 및
  `0x00464509: c7 46 08 58 02 00 00` (600)이다.
- DirectDraw surface vtable slot과 일관된 후보는 `+0x14` 49개, `+0x2c` 14개다. 대표 old
  bytes는 `0x0046ca30: ff 52 14`, `0x0046cb34: ff 51 2c`, `0x0046d73b: ff 51 2c`,
  `0x0046d903: ff 51 2c`다.
- 후보들은 generic surface/array 포인터와 계산된 stack 인자를 사용한다. 어떤 후보도 800×600
  source에서 1600×1200 destination rectangle으로 가는 unique writer와 실제 Flip 선택을 함께
  증명하지 못한다. 전체 바이너리의 1600/1200 상수 존재만으로 presentation 의미를 추론하지 않는다.

## 승격 작업자가 이어서 검증할 것

1. Astra/high architecture가 위 주소와 lap73 manifest/surface evidence를 출발점으로 surface
   ownership의 생성·보관 writer를 호출 그래프로 분리한다.
2. rectangle 구조체의 생성/기록 지점을 찾아 source `(0,0,800,600)`와 destination
   `(0,0,1600,1200)` 또는 동등한 정수 2배 관계가 실제로 동일 Flip/Blit 경계에 전달되는지
   old bytes와 isolated runtime trace로 확인한다.
3. unique boundary가 증명될 때만 중간 tier가 patch 설계/범위/회귀 검토를 하고, 그 전에는
   코드·binary·fixture·baseline을 수정하지 않는다. 검증 실패나 경계 복수이면 blocker를
   유지하고 G1을 미완료로 둔다.

## 세션 종료 조건

현재 문서·근거를 보존했으며, 이 blocker는 구현 작업자가 추측으로 해결할 수 없고
Astra/high architecture 확인이 필요한 경계다. 다음 세션은 위 검증부터 시작한다.
