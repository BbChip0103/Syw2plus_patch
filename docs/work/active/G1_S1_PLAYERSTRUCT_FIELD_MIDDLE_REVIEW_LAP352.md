# lap352 middle — PlayerStruct `+0x00..+0x04` 필드 재유도와 work handoff

2026-09-12 / Codex 현재 세션 / 정확한 모델 ID 미주장 / high / middle(진단·계획·확인).
게임 코드·하네스·제품 테스트 hands-on 수정과 게임/Wine/Xvfb/입력/PNG는 0이다.
범위는 M1/G1 내부 S1 load-completion 근거이며 Stage B·제품·마일스톤 승인이 아니다.

## 0. 판정

**필드 배치 ACCEPT, 기존 라벨 두 곳 REJECT.** 보호 원본의 생성자와 세 개의 8-slot
초기화 루프, 현재 save000/save006의 8×6 raw bytes가 같은 배치로 수렴한다.

| offset | 폭 | 재유도한 의미 | 핵심 원본 근거 |
|---|---:|---|---|
| `+0x00` | 1B | nation/race code | `0x41BB83`, `0x41F109`, `0x41F149`에서 1/2/3/5/6 계열 분기 |
| `+0x01` | 1B | player number/index | `0x43EBC9`, `0x41BB17`: 인자 저장 뒤 bit shift count로 사용 |
| `+0x02` | 1B | is_cpu boolean | `0x43EBD7` 기본 1, `0x41BBF2`가 CPU 초기화 gate로 검사 |
| `+0x03` | 1B | self-bit mask `1 << player_num` | `0x43EBD2..0x43EBDB`, `0x41BB17..0x41BB25` |
| `+0x04` | 1B | different-team/opponent bitmask | `0x41BB2C..0x41BB3C`: `+0x05` team이 다를 때 상대 bit를 OR |

`0x41BADE..0x41BB06`, `0x41BDB7..0x41BDDF`, `0x4C3F82..0x4C3F9A`는
6-byte lobby record를 DWORD+WORD로 PlayerStruct에 복사하므로 `+0x00..+0x05` 사이 padding은 없다.
`+0x05`는 team number이며 현재 판정의 경계 확인에만 사용했다.

따라서 lap284/lap286의 `<BBBB>`가 읽은 `+0x00..+0x03` **위치는 맞다.** 앞의
nation/player_num/is_cpu와 player/roster offset도 살아남는다. 다만 네 번째 값을
`alliance`라고 부른 것은 정확하지 않다. `analysis/memory_maps/player_offsets.md`의
`+0x04=alliance`도 틀렸고, 그 자리는 원본 루프가 만든 opponent mask다. 역사 probe와
과거 report는 수정하지 않고 당시 라벨 오류로 보존한다.

## 1. fixture 교차검증

lap351 probe를 수정 없이 독립 재실행해 rc0, `failures=[]`, stdout SHA
`1a4359cb5027fd8a96e005529611099dca9c6ac104109c1318f0b8be15565e35`를 재현했다.
그 probe가 확정한 player0 file offset `2,259,634`에서 stride `0x3ABC`로 6바이트씩 읽었다.

- save000 player0=`02 00 00 01 fe 00`; player1..7의 `+0x03`은
  `02,04,08,10,20,40,80`, `+0x04`는 모두 `01`, team은 모두 `01`.
- save006도 player0=`02 00 00 01 fe 00`; player1..7의 self/opponent/team 패턴은 동일하다.
- 두 파일 모두 8/8 slot에서 `self_mask == 1 << player_num`이고,
  `opponent_mask == OR(1 << other.player_num)` for different `team_num`이다.

fixture가 원본 xref 공식을 정확히 만족하므로 `+0x03/+0x04` 충돌은 해소됐다. 단 이 정적
일치는 실제 load 완료, save/load 동일성, 일반 동맹 변경 semantics, 9~16번 확장을 증명하지 않는다.

## 2. work tier 봉투 — 실행 예산 0회

다음 Luna/high work는 게임 실행 없이 한 가지 최소 변경만 한다.

1. `analysis/memory_maps/player_offsets.md`의 앞 6바이트 표를 위 배치로 정정하고 근거 주소를 붙인다.
   이름은 `+0x03=self_bit_mask`, `+0x04=opponent_mask`, `+0x05=team_num`으로 고정한다.
2. 과거 lap284/lap286 probe/report는 수정·재pin하지 않는다. `tools/runtime_env.py`에 기존 R1과
   분리된 S1 load-evidence reader/CLI를 추가하고 별도 `s1_load_evidence.json`만 쓴다.
3. reader는 group WORD·선택 index·예상 fixture SHA와 PlayerStruct 8×6 raw bytes를 기록한다.
   post-PS3에서 `+0x00..+0x05`를 폭 그대로 읽고 self/opponent mask 공식을 검사한다.
4. 합성 회귀는 정상 8-slot, fopen/open-failure PS3, 잘못된 slot/SHA, reader 결측·부분 read를 덮는다.
   open-failure·불일치·결측은 PASS 금지, `UNKNOWN`/`FAIL`을 보존한다.
5. targeted tests → `make check` → `checks/safety.sh check`를 fresh 실행한다. 실제 클릭·게임 run,
   EXE/DLL/save/fixture/pin/baseline/golden 변경은 금지한다.

work 산출물은 다음 새 middle이 소스 SHA·허용 diff·targeted/Fast/safety와 실패 분류를 독립 검수한다.
그 뒤에도 실행 횟수·시간·좌표·fixture 선택은 Astra의 별도 봉투 전 0회다. S1 (A)+(B),
F2-R2, WM_CLOSE, fresh 원본/후보 pair와 사용자 승인은 그대로 미검증이다.

이번 판정 기록 뒤 fresh `make check`는 378 passed(63.21s), Ruff/compileall/mypy와
`CONTEXT_PASS`까지 rc0였고 `checks/safety.sh check`도 `SAFETY_PASS`였다. 이것은 정적 필드
판정과 저장소 Fast만 검증하며 실제 load·앱 실행·제품 G1을 검증하지 않는다.
