# G4 build-intent cooldown 100→50 probe (2026-09-16)

## 의미 정정

`0x0043F880`의 `cmp eax,100`은 controller 전체 실행 주기가 아니다. Ghidra
`FUN_0043F5D0.c:140-148`에서 selector case 2가 controller별 `+0x33AC` 마지막 실행 tick과
비교한 뒤 opcode `0x01`/argument `1`을 설정하고, 후반 dispatch가 `FUN_0043E0E0` 건설 발주
상태기를 호출한다. 따라서 정확한 의미는 **건설 의도 발주 cooldown 100→50**이다. 기존
파일명 `controller_cadence_probe.py`는 evidence 경로 호환 때문에 유지하지만 범용 controller
cadence로 해석하지 않는다.

## 후보

원본을 수정하지 않고 private copy 한 개의 instruction만 바꿨다.

- VA/file offset: `0x0043F880` / `0x3F880`.
- before: `83 F8 64` (`cmp eax,100`).
- after: `83 F8 32` (`cmp eax,50`).
- candidate SHA: `2309331aa857ac2242b12d235cb2a21b530ea00f1f12414f3774c78290d4c492`.
- 생성/원복: `patches/ai/controller_cadence_probe.py`; exact hash/byte guard, in-place 금지.

## 30초 seed7 결과

baseline endpoint는 total 7(owner0=4, owner1=3), 최소 진영 거리 81이었다.
독립 candidate 두 런은 모두 total 8(owner0=5, owner1=3), 최소 거리 78이었다.
후보 두 런의 마지막 유닛 구성과 양 player 자원/used도 일치했다. owner1은 unit 수는 같지만
생산 unit type과 잔여 자원이 baseline과 달라 selector cadence가 실제 전략 상태에 영향을
준다는 것이 확인됐다.

후속 0.1초 dense capture 두 런은 각 299 sample을 얻었다. opcode episode의
`(opcode, 최초 argument)` 순서는 owner0 10개, owner1 14개가 각각 완전히 같았고 episode
시작 tick 차이는 최대 3이었다. 판정은 `CONTROLLER_TRACE_REPEATABLE`이다. report SHA는
`dd9e2aaec8c8eab6b088dc9a9dc2834f8da9104038a5a1f10bd68a49e98bae3c`다.

두 번째 fixture인 seed42에서도 30초 baseline은 total 6(owner0=3, owner1=3)이었고,
독립 candidate 두 런은 모두 total 7(owner0=4, owner1=3)이었다. 두 candidate endpoint의
player 자원, unit 구성/좌표/명령, 마지막 tick까지 정확히 같았다. 판정은
`SECOND_SEED_EFFECT_REPEATABLE`, report SHA는
`d7baa9113ec0bd00160165b5822c7c6b0814c151806586ad6a8c4361277debc2`다.

seed1 240초 대조에서는 양쪽 모두 실제 전투에 진입했다. baseline 첫 피해는 198.043초,
candidate는 146.030초로 후보가 약 52초 먼저 접촉했다. baseline endpoint는 owner0/1이
34/25, candidate는 39/19였고, 받은 피해 event는 baseline 11/11 대 candidate 6/18이었다.
후보가 조선(owner0)에 유리한 비대칭을 만들었지만 한 경기만으로 보편적 AI 향상이나 승률을
말할 수 없다. 판정은 `COMBAT_EFFECT_OBSERVED_NOT_QUALITY_PROVEN`, report SHA는
`0236ad5d624c87051d5863d0620952435b46f47afd1fa5903a176b79c63d4eac`다.

candidate seed1 240초를 독립 실행으로 한 번 더 반복했다. 두 런 모두 endpoint 39/19,
피해 event 6/18, 피해량 400/1180, 소멸 1/0, 최소 거리 1이 같았고 첫 피해 tick 차이는
1이었다. outcome 판정은 `COMBAT_OUTCOME_METRICS_REPEATABLE`, report SHA는
`3411a6013941f24161180aac2cb262a5fda23a654be81517c53ff3276b01b3bd`다. 다만 2초 표본의
transient 전체 series는 sample phase 영향으로 strict comparator에서 `FIXED_FIXTURE_DRIFT`라
exact state repeatability로 승격하지 않는다.

고정 seed와 국가 조합을 함께 쓰지 못하던 diagnostic bridge의 exact-string 버그를 고쳐
Ming(owner0)/Joseon(owner1) seed1 fixture를 만들었다. 이 대조에서 baseline 47/33이던
endpoint는 candidate 41/33으로 바뀌었다. 앞의 Joseon/Japan은 candidate가 +5/-6이었지만
Ming/Joseon은 -6/0이므로 효과는 owner나 nation 어느 하나를 일관되게 강화하지 않고
matchup/slot에 의존한다. 판정은 `NATION_SWAP_REVEALS_CONTEXT_DEPENDENT_BIAS`, report SHA는
`55b9d68fe3435f11d80b98bb2709658f5353b784ebb97b63b607f950ddd2cdec`다.

## 판정

`NO_GO_GENERIC_AI_IMPROVEMENT`.

- 단일 byte 변경으로 측정 가능한 생산/구성 변화와 조기 접촉은 재현됐다.
- 그러나 국가 교환 대조에서 이 변화가 matchup/slot 의존 편향임이 확인됐다. 범용 AI 강화
  후보로는 기각하며 배포·활성화하지 않는다.
- LAN에서는 모든 peer가 같은 EXE면 원리상 같은 cadence를 실행하지만, LCG 소비 순서와 네트워크
  결정론은 별도 장기 검증이 필요하다.
- 실제 원본 사본에 후보를 생성한 뒤 `restore`한 결과 SHA가 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`로 정확히 돌아왔다.
  판정은 `REAL_BINARY_RESTORE_PASS`, evidence SHA는
  `e147d1c4e6c2d04be2a2f7e814a2f42a61985e2f9c4eef3b9565bc6f2711cd0d`다.
- 이 후보의 LAN 검증은 중단한다. 다음 연구는 global cadence가 아니라 controller opcode별
  의사결정 의미를 겨냥한 균형 후보를 찾는 것이다.

preliminary verdict SHA:
`da5df029a84fe8eaec91ff9941cd8d0eb171a258c77e6a4db425430bf511ea54`.
