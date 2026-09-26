# G4 원본 길찾기 비교 fixture preflight (2026-09-16)

## 판정

- **원본 A* 코드 변경은 아직 NO-GO.** G4 전체가 불가능하다는 뜻은 아니며, 비교 fixture의 네 필수 조건이 아직 없다.
- 원본 EXE·두 Ghidra 입력의 SHA와 PE `0x004E5FF4 -> 0x0046B840`은 다시 PASS했다.
- 기존 하네스에는 UnitStruct `x=+0x2A2`, `y=+0x2A4` reader와 XTest button 3 입력기가 있다. 따라서 좌표를 읽거나 우클릭을 보내는 저수준 수단 자체가 장애는 아니다.
- 그러나 현재 실제 PS3 하네스는 기본 랜덤 게임의 **맵 이름/seed를 관측하지 못한다**. 같은 장애물 배치를 두 실행에서 재현했다는 증거가 없다.
- A*가 소비하는 passability/collision grid snapshot, 선택 유닛의 고정 우클릭 명령과 tick별 경로 trace, 원본 2회 결과 동일성도 없다. 이 상태에서 반복상한 `0x78`, 검색창 `±0x1E`, 휴리스틱만 바꾸면 개선/퇴행/동기화를 판정할 수 없다.

## 산출물과 기계 결과

- `tools/g4_path_fixture_preflight.py`: 게임을 실행·수정하지 않는 fail-closed preflight.
- `analysis/g4_path_fixture_preflight.json`: `verdict=BLOCKED`, `activation_allowed=false`.
- 현행 evidence SHA-256: `c655ebf0aa61a66ddf006cdd80c786c1fa42195404aa017b1720552bd18890a3`.
- targeted: `tests/test_g4_path_fixture_preflight.py` **2 passed**, Ruff PASS, mypy PASS.

## 막힌 네 조건

1. SHA가 고정된 동일 save/map 또는 관측된 seed의 deterministic scene.
2. 원본 A*가 실제 소비하는 장애물/passability oracle.
3. 고정 selected slot/start/destination과 tick·slot·x·y·command 상태 trace.
4. 후보 비교 전에 원본 두 번이 동일 결과라는 repeatability gate.

## 다음 안전 분기

기존 diagnostic bridge의 scenario-1 진입과 좌표 제어 코드는 재사용 후보지만, 그것은 stock UI 실행과 같지 않고 현재 이동 경로 oracle도 아니다. 다음 G4 작업은 private runtime 한정 fixture로 위 네 조건을 먼저 닫는다. 두 원본 trace가 일치하기 전에는 원본 바이너리 writer나 알고리즘 패치를 만들지 않는다.
