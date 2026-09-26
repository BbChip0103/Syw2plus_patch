# lap351 middle — fixture offset 불변성 판정과 후속 필드 충돌

2026-09-12 / Codex 현재 세션 / 정확한 모델 ID는 주장하지 않음 / high / middle
(진단·계획·확인). 게임 코드·하네스·제품 테스트 hands-on 수정과 게임 실행은 0이다.
이 판정은 M1/G1 내부 S1 연구 근거만 다루며 Stage B·제품·마일스톤 승인이 아니다.

## 0. 판정

lap350이 넘긴 **현재 네 fixture의 파일 offset 불변성은 ACCEPT**다. offset 210/212의
width/height 배정 2개와 halving 식 2개를 곱한 네 조합을 파일별로 모두 계산했으며,
각 파일의 `(bulk, player0, roster)` 결과 집합은 정확히 하나다.

따라서 lap322 §14.1의 “정사각·짝수 ambiguity 때문에 현재 fixture의 PlayerStruct 파일
offset으로 환산할 수 없다”는 결론은 **현재 fixture 범위에서는 반려**한다. 그 ambiguity는
width/height의 일반 의미와 비정사각·홀수 fixture로의 외삽을 막지만, 현재 네 파일의 offset은
바꾸지 않는다. lap322 원문은 이력으로 고쳐 쓰지 않는다.

그러나 load-completion sentinel을 정하는 과정에서 **별도 필드 해석 충돌**을 발견했다.
lap284/lap286 probe는 PlayerStruct 시작에서 연속 4바이트를 읽고 네 번째 `+0x03`을
`alliance`로 표기하지만, `analysis/memory_maps/player_offsets.md`는 alliance를 `+0x04`로
정의한다. 필수 구현 근거 충돌 중단 규칙에 따라 전체 S1 load work 봉투는 **BLOCKED**다.

## 1. 단일 불변성 검사

- probe: `docs/history/laps/probes/20260912_lap351_middle_fixture_offset_invariance_probe.py`
- 입력 pin: lap286 probe `604e7f8c…80c9fd`, lap322 계약 `b5b54f56…df1e95`,
  lap350 판정 `c8576fdc…afed8`, 원본 `b56986e0…c08a8ac`, fixture SHA 4개.
- 열거: dimension 배정 2 × halving 식 2 = fixture별 4조합.
- 결과: rc0, `failures=[]`, output `logs/lap351/fixture_offset_invariance.json`.

| fixture | raw WORD@210/212 | 서로 다른 offset tuple |
|---|---:|---|
| save000 | 180/180 | `(1455954,2259634,2388902)` |
| save006 | 180/180 | `(1455954,2259634,2388902)` |
| save011 | 100/100 | `(772754,1576434,1705702)` |
| save012 | 100/100 | `(772754,1576434,1705702)` |

probe SHA `e4f26428…49b240`, output SHA `1a4359cb…65e35`. `py_compile`과
Ruff 단일 파일 검사는 rc0다. 기존 lap286 probe도 수정 없이 재실행해 rc0/`failures=[]`와
위 원래 offset을 재현했다. 게임/Wine/Xvfb/클릭/PNG는 0회다.

## 2. 새 충돌의 정확한 범위

- 기준 문서 SHA `8ac8a45…fe79c`는 nation `+0x00`, player_num `+0x01`, is_cpu
  `+0x02`, alliance `+0x04`라고 적는다.
- lap284와 lap286 probe는 둘 다 `struct.unpack_from("<BBBB", data, player_offset)`로
  `+0x00..+0x03`을 읽고 네 번째 값을 alliance로 기록한다.
- save000/save006 player0의 원시 5바이트는 둘 다 `02 00 00 01 fe`다. 따라서 기존 report의
  alliance=`1`은 `+0x03` 값이고, 문서 위치 `+0x04`의 값은 `254`다.
- 영향 없음: 이번 offset 불변성, nation/player_num/is_cpu 세 필드, roster 총 record 수.
- 영향 있음/UNKNOWN: 기존 `player_slots[*].alliance`, 이를 인용하는 fixture 구성 판정,
  alliance를 포함할 load-completion sentinel. roster owner `+0x8E`도 lap286이 상속한 가정이므로
  이번 sentinel 근거로 승격하지 않는다.

## 3. 중단과 다음 검수

다음 새 Sol/high middle은 한 가지를 독립 검수한다: 원본 xref와 현재 fixture 바이트로
PlayerStruct `+0x00..+0x04`의 폭·padding/필드 배치를 재유도하고, lap284/lap286의 alliance
라벨 오류 범위가 alliance 한 필드에만 한정되는지 판정한다. 기대값을 맞추거나 과거 probe를
재pin/수정하지 않는다.

그 판정 뒤에만 work tier handoff를 발행한다. sentinel 후보는 owner `+0x8E`와 alliance를
제외하고, 정적으로 재확인된 PlayerStruct 원시 필드·map dimensions·pre/post 변화와 PS3를
결합해야 한다. PS3 단독 또는 open-failure 경로는 PASS가 될 수 없다. 기존 R1 함수와 제품
evidence는 분리하고 게임 실행 예산은 Astra의 별도 결정 전 0이다.

새 충돌 발견 즉시 중단했으므로 `make check`와 safety는 SKIP이다. targeted probe rc0을
전체 봉투 승인으로 사용하지 않는다. 변경·근거는 lap351 history와 `loop/ESCALATE_SOL`에 보존한다.
