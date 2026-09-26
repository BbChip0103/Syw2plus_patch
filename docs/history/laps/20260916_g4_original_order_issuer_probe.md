# G4 original order issuer probe (2026-09-16)

## 목적

직접 `target/command` 필드를 쓴 선행 probe가 이동을 시작하지 못한 이유를 분리한다.
동일한 seed1 장면에서 장시간 idle인 유닛 한 기에 원본의 고수준 target-order 발행 함수
`FUN_00415480 @ 0x00415480`를 호출해 pending order부터 정상 경로로 처리시켰다.

## 정적 근거와 안전 경계

원본 경로는 다음과 같다.

`0x415480 → 0x4AEE10 → 0x4AED20 → 0x40FF90 → 0x412540 → 0x40C640`

`0x412540`은 `Unit+0x380/+0x384/+0x388/+0x38C`에 pending-order 상태를
기록하고, `0x40C640`이 이를 소비해 active command로 승격한다. 선행 probe의
`Unit+0x290/+0x64A` 직접 기록은 이 경로를 우회했다.

- 진단 전용 bridge는 함수 첫 12바이트
  `53 56 8B F1 57 8A 86 1C 03 00 00 84`를 fail-closed로 확인한다.
- owner0, idle, mobile combat 유닛 **정확히 한 기**만 대상으로 한다.
- 유닛 생성/type 변경/pathfinder 변경/원본 EXE 변경은 없다.
- 호출은 선행 control worker에서 실행했다. 실제 이동 관측은 유효하지만, simulation과의
  동시성 안전성은 입증되지 않았다. 다음 probe는 기존 `chb_call_handler` main-loop slot을
  사용해 main thread에서 identity 재검증과 원본 함수를 실행한다. 이 worker 호출 형태를
  제품 통합으로 재사용하지 않는다.
- bridge SHA-256:
  `0ca44efc64075e39f656be8d9ca600ecb818017ad5d93cec31b0b25a0dbf6677`

## 실행 결과

- fixture: 원본 EXE, seed1, 180초, 0.25초 표본
- 개입: 150.016초
- 원본 함수 반환: `1` (`original_target_order_admitted`)
- source slot/id/type: `1168 / 328848 / 2`
- target slot/id/type: `1176 / 853144 / 31`
- pending 변화:
  - command: `00000001 → 00010004`
  - packed xy: `004D000B`
  - full target id: `000D0498`

| 시점 | source command | source 좌표 | target HP |
|---|---:|---|---:|
| 개입 직전 149.766초 | 1 | (9,14) | 500 |
| 첫 개입 후 표본 150.067초 | 4 | (9,14) | 500 |
| 최초 target HP 감소 170.871초 | 4 | 근접 이동 중 | 473 |
| 마지막 179.911초 | 3 | (15,71) | 0 |

source는 개입 후 서로 다른 좌표 **69개**를 거쳤다. source-target Chebyshev 거리는
63에서 최소 1까지 줄었고, target은 179.410초에 처음 HP 0이 되었다. 다만 주변의 다른
유닛도 교전할 수 있으므로 target 피해 전부를 이 source 한 기의 공격으로 귀속하지 않는다.

실행 말미 고정 minimap 클릭 검사는 기존의 별도 `FAIL_NO_EFFECT`로 끝났지만, 개입·표본은
그 전에 정상 수집됐고 cleanup도 수행됐다. 이 UI tail 실패를 G4 결과 PASS로 바꾸지 않는다.

보존 산출물:

- `temp/Syw2plus_patch/g4_ai/20260916_seed1_original_order_issuer180/`
- compact report SHA-256:
  `ac65600e117c67c9f141de193bcf5e36b5bb59c9fba3b0fcdb76c2e09186c7be`
- full runtime JSON SHA-256:
  `56392aa4b7b62602bfdf3b7b39ecaa436d1240727ac61e1c3462cb12163c2316`

## 판정

`ORIGINAL_ORDER_PATH_MOVEMENT_PASS`.

이 fixture의 해당 유닛은 원본 order 발행 경로를 거치면 즉시 이동한다. 따라서 현재 증거는
**pathfinder 자체의 전면 고장보다 AI order-issuance gap**을 지지한다. 이는 seed1의 한 유닛에
대한 국소 증거이며 전체 맵의 길찾기 품질이나 범용 AI 패치 완료를 뜻하지 않는다.

다음 구현 축은 pathfinder 상수 변경이 아니라, 원본 AI가 idle mobile combat 유닛에 목표를
선택·발행하는 정책을 bounded하게 보완하는 것이다. 지원 조건, 명령 빈도, 결정론, 국가/slot
편향을 먼저 고정하지 않으면 제품 패치로 승격하지 않는다.

## 검증

- bridge build: PE32 DLL 생성 성공
- targeted: **150 passed**, Ruff/mypy PASS
- full: **482 passed**, Ruff/compileall/mypy/CONTEXT PASS
- safety: `SAFETY_PASS`
- runtime cleanup: owned launchers/Xvfb 종료, prefix 잔류 process 0, global kill 미사용

## Main-thread 재현과 진단 결과 문자열 수리

후속 bridge는 원본 함수 호출을 `chb_call_handler` main-loop slot으로 옮겼다. one-shot
static payload로 timeout 후 worker stack pointer가 남지 않게 했고, `bridge_used[16]`에
20자 label을 복사하던 진단 metadata 결함을 `g4_order_probe` bounded copy로 수리했다.
이전 원시 artifact의 `bridge_downgraded_from="robe"`는 label overflow 부산물이며 보존한다.

seed1 180초 main-thread 재현:

- 개입 150.071초, source1168/id328848, target1176/id853144, 함수 ret1
- pending `00000001→00010004`, 첫 다음 표본 command4
- distinct positions **68**, `(9,14)→(22,62)`
- target 최초 HP 감소170.925초, HP0 177.486초
- source는 endpoint AI group roster `[591003,787609,1173,132243]`에 없었다.
- bounded label 정상, mainthread 처리5ms, cleanup prefix process0

`MAINTHREAD_ORIGINAL_ORDER_MOVEMENT_PASS`.

이동 성공은 재현됐으나 worker 실행과 endpoint/target 사망 시점은 다르다. wall-clock
intervention 두 실행을 deterministic equality로 승격하지 않는다. 제품 통합은 별도
simulation-tick boundary와 repeat equality가 필요하다.

보존: `temp/Syw2plus_patch/g4_ai/20260916_seed1_mainthread_order_issuer180/`

- bridge SHA `5697a32c5d79169d0ba7da015823beb0aba83266e6507cdf2f910fe4c92f98d1`
- runtime SHA `f84ab412222a925807e225fe1c67f776150c2d4fb16ef1076b205333771e7ca8`
- compact SHA `fdb3d2943ab5c871ad169462f755952b9725cd2a1cf8cbb117e0ae572c61c717`
- mainthread/label regression+runtime targeted **153 passed**, build/Ruff PASS
