# lap354 middle — lap353 S1 load-evidence reader 독립 검수

2026-09-12 / Codex 현재 세션 / 정확한 모델 ID 미주장 / high / middle(진단·계획·확인).
게임 코드·하네스 hands-on 수정과 게임/Wine/Xvfb/입력/PNG 실행은 0이다.
범위는 lap352가 발행한 M1/G1 내부 S1 reader/CLI 봉투이며 Stage B·제품·마일스톤 승인이 아니다.

## 0. 판정

**REJECT — REQUIRED WORK REPAIR.** PlayerStruct 앞 6바이트 라벨과 fixture parser, 실패 분류의
부분 구현은 현행 SHA에서 재현됐다. 그러나 새 CLI는 S1 load-evidence **collector**에 결선되지
않았다. `read_post_player_structs`의 생산 호출자는 없고, CLI/evaluator는 group WORD와 PS를
주소에서 읽지 않는다. 호출자가 제공한 `ps=3`, `open_succeeded=true`, fixture에서 복사한
`raw_hex` 문자열만으로 실제 reader provenance와 pre/post 변화 없이
`PASS/LOAD_RESTORED_PLAYER_STRUCTS`를 낸다. 이는 lap350 §4와 lap352 §2.3의 “post-PS3에서
읽는다” 및 PS3/open-failure 단독 PASS 금지 계약을 충족하지 않는다.

필수 구현 근거가 현행 코드의 실제 결선과 충돌하므로 사용자 중단 규칙에 따라 현물을 보존하고
`loop/ESCALATE_SOL`에 반환한다. targeted rc0과 과거 Fast rc0은 이 결손의 승인이 아니다.

## 1. 입력·독립 검수

- lap353 기록의 네 SHA를 재계산했고 모두 일치했다:
  `player_offsets.md=d1170aba…e9dfc`, `runtime_env.py=6eb291ed…b16`,
  `s1_load_evidence.py=a9704cd0…f53c`, test=`4a5cf5e8…2d94`.
- 보호 fixture `local/runtime/20260912_191422_3558862_0/game/save/save000.dat`는
  3,093,902 bytes, SHA `1c703551…719da`; player0 offset `2,259,634`, stride `0x3ABC`의
  8×6 raw bytes가 lap352 배치와 일치했다.
- 작업자 targeted test를 fresh 실행해 `11 passed`; Ruff/compileall/mypy도 PASS했다. 이는
  구현된 합성 사례만 재현하며 생산 collector 결선을 검사하지 않는다.
- 독립 probe `docs/history/laps/probes/20260912_lap354_middle_lap353_s1_reader_review_probe.py`
  (`b08d0c7b…07a4`)는 work 테스트를 import하지 않고 현행 함수와 보호 fixture를 직접 읽었다.
  rc1, F1~F4: collector/group/PS reader 결선 0, 무근거 payload 거부 0. 문제 payload의 실제
  판정은 `PASS/LOAD_RESTORED_PLAYER_STRUCTS`였다.
- `rg` 생산 범위 결과: `read_post_player_structs`는 정의 1·테스트 1 외 호출 0;
  `open_succeeded`는 evaluator 입력과 합성 테스트에서만 나타난다.

## 2. Luna/high work 수리 handoff

한 바퀴에서 다음 하나만 수리한다.

1. 기존 R1과 offline fixture parser를 보존하되, `runtime_driver.read`를 주입받는 별도 S1
   collector를 실제 CLI 경로에 결선한다. collector가 PS WORD, group WORD, 선택 index의
   근거와 PlayerStruct 8×6 raw bytes를 직접 수집하며 모든 read 주소·폭을 artifact에 남긴다.
2. caller가 임의로 준 `open_succeeded=true`는 load 완료 근거로 수용하지 않는다. 금지된
   hook/쓰기 없이 open 성공을 직접 읽을 수 없다면, 클릭 전 raw와 post-PS3 raw의 변화 및
   `post==pinned fixture`를 함께 요구한다. `pre==post`, pre 결측, PS/group/slot/read provenance
   결측은 UNKNOWN이어야 한다.
3. post record는 owner 0..7 순서, 계산된 memory address, 정확한 6-byte raw를 collector가
   생성한 형태로만 평가한다. raw 문자열만 복사한 외부 JSON은 PASS를 만들 수 없어야 한다.
4. 회귀에 lap354 F1~F4, pre==post, PS/group/slot read 실패와 부분 read를 추가한다. 기존
   정상 fixture parser, 잘못된 slot/SHA, open-failure 분류는 보존한다.
5. targeted → `make check` → `checks/safety.sh check`를 fresh 실행해 다음 새 middle에 넘긴다.

실제 실행 횟수·시간·좌표·fixture 선택은 Astra 봉투 전 0회다. 게임/클릭/PNG, EXE/DLL/save,
과거 probe/pin/baseline/golden, Stage B/P6/WM_CLOSE/G2~G4, 새 의존성 및 커밋은 금지한다.

## 3. 검사와 미검증

독립 계약 probe rc1에서 중단했으므로 전체 `make check`와 safety는 SKIP했다. 이것은 회귀 실패를
숨기는 것이 아니라 필수 검증 실패 뒤 억지 마감을 금지한 사용자 조건을 따른 것이다. 실제 load,
S1 (A)+(B), F2-R2, fresh 원본/후보 pair, WM_CLOSE와 제품 G1~G4는 모두 미검증이다.
