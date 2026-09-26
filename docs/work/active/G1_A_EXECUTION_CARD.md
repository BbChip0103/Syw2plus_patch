# G1-A 실행 카드 — 무패치 기준 장면·입력·출력 경계

2026-09-10 lap3, Codex `gpt-5.6-sol` / high / middle 사전 컨펌.
판정: **APPROVE FOR WORK EXECUTION**. 이는 실행 범위 승인이지 G1-A 결과나 제품 승인 아님.

2026-09-11 lap5 middle 독립 검수에서 setup 경로를 **REVISE DRAFT**로 바꿨다.
lap4 실패 원인은 confirm 좌표 자체가 아니라 기본 `여럿하기` 상태에서 `혼자하기`를 선택하지 않은
카드 전제였다. 다만 같은 lap의 필수 `make check`가 loop controller 회귀로 FAIL했으므로 work 실행
승인은 보류했다. 이 controller 보류는 lap14 수리와 lap15 독립 확인으로 해소됐다.

2026-09-11 lap17 middle 독립 검수에서 lap16의 PS5 정체 판정을 **HARNESS DEFECT CONFIRMED**로
수정했다. 원본 dispatcher는 PS4 전처리 뒤 PS5 로비를 정상 endpoint로 사용하며, PS7 복귀 기대는
틀렸다. 또한 `0x004ED848`은 WORD이고 lap16은 클릭 전부터 1이어서 solo 입력 효과를 입증하지 못했다.
아래 개정은 **APPROVE FOR WORK REPAIR**이며, G1-A 실행이나 제품 승인은 아니다.

2026-09-11 lap18 work에서 위 수리를 적용했다. selector WORD 2바이트 read, 조건부
`1→0→1`, 중립 커서 캡처, confirm/ready PS5 endpoint와 관련 회귀가 `make check`/safety를
통과했다. 새 middle 독립 확인 전에는 G1-A 게임 실행을 허용하지 않는다.

2026-09-11 lap19 middle 독립 검수 판정은 **REVISE**다. 후보/원본 SHA와 기계 gate는 PASS지만
테스트는 좌표 상수와 WORD reader만 직접 검증해 조건부 흐름·중립 캡처·PS5 endpoint를 고정하지
못한다. 또한 start 입력의 evidence 기대값은 아래 계약의 `PS5→PS3`가 아니라 코드에
`PS7→PS3`로 기록된다. work tier는 허용된 runtime/test 파일만 최소 수리하고, ready 효과가
전체 화면의 무관한 SHA 변화가 아님을 구분하는 검증도 고정한다. 새 middle 확인 전 게임 실행 금지.

2026-09-11 lap20 work가 위 반려 범위를 수리했고, lap21 middle이 두 후보 SHA·
실제 호출 경로·targeted18/Fast88/safety를 독립 확인해 **CONFIRMED**했다.
이 판정은 하네스 2단 기술 확인이며, 아래 고정 계약의 새 G1-A 원본 run 1회만 허용한다.
G1-A/G1 결과나 제품·사용자 승인은 아니다.

2026-09-11 lap22의 허용된 새 원본 run은 selector 진입에서 callback `TypeError`로 실패했고,
lap23 middle이 보존 SHA/manifest/runtime evidence와 순수 재현을 대조해 **HARNESS DEFECT
CONFIRMED**했다. `_wait_state`는 reader에 bool을 전달하지만 production selector adapter만
무인자였고 기존 targeted18은 이 결선을 실행하지 않았다. 다음 work는 기존 `state(False)` 의미를
보존하는 명시적 bool adapter, `_wait_state`의 좁은 reader type, 관련 회귀만 최소 수리한다.
`TypeError` catch/무인자 fallback과 게임 재실행은 금지하며 새 middle 확인 전 실행 승인은 보류한다.

2026-09-11 lap24 work는 위 범위만 수리했다. production selector의 기존 `state(False)` 호출은
보존하고 `_wait_state`용 bool adapter를 추가했으며, selection/camera reader도 명시적 bool
parameter로 고정했다. `True` 전달 회귀와 기존 양쪽 selector flow 회귀를 유지한 채 targeted19,
Fast89, mypy, safety가 PASS했다. 새 Sol 독립 확인 전에는 새 G1-A 게임 실행을 보류한다.

2026-09-11 lap25 middle은 두 후보 SHA와 실제 bool 호출 경로를 독립 확인하고 targeted19,
Fast89, mypy, safety의 fresh PASS로 lap24 수리를 **CONFIRMED**했다. 이는 하네스 2단 기술
판정이며, 아래 고정 계약의 새 격리 원본 G1-A run을 work tier에 정확히 1회 허용한다.
G1-A/G1 제품 판정이나 사용자 마일스톤 승인은 아니다.

2026-09-11 lap26의 허용된 1회 run은 `(344,169)` 클릭 뒤 `0x004ED848` WORD `1→0`을
관측하지 못해 FAIL했다. lap27 middle은 보존 run·PNG·원본 xref와 테스트를 독립 대조하여,
WORD 폭만 확인됐을 뿐 PS7 두 버튼과 `혼자=1/여럿=0` 의미의 직접 연결이 없고 테스트가 click
stub에서 그 전이를 합성한다고 판정했다. 따라서 **HARNESS CONTRACT REVISE / GAME RUN
BLOCKED**다. 입력 전달 자체는 클릭 직후 증거가 없어 UNKNOWN이며 원본 결함으로 판정하지 않는다.

2026-09-11 lap30 work가 아래 selector contract 수리를 적용했고, lap31 middle이 고정 원본
raw bytes·source/test 결선과 targeted24/Fast94/safety를 독립 재확인해 **CONFIRMED**했다.
이는 하네스 2단 기술 판정일 뿐 G1-A/G1 또는 사용자 승인이 아니다. lap27의 game-run block은
해소됐으며, 현재 다음 한 가지와 정확한 1회 실행 권한은 `docs/STATUS.md`만 따른다.

2026-09-11 lap32의 허용된 새 원본 run은 solo PS5에서 수동 ready click의 화면 변화가 없어
FAIL했다. lap33 middle은 고정 원본 raw control flow를 독립 대조해 committed solo mode=1이면
수동 ready control poll을 건너뛰고 local slot ready DWORD를 자동 설정함을 확인했다. 따라서
판정은 **HARNESS CONTRACT REVISE CONFIRMED / GAME RUN BLOCKED**다. 입력 미전달이나 원본 게임
결함으로 승격하지 않으며, 아래 lap33 수리와 새 middle 확인 전 새 게임 실행을 허용하지 않는다.

2026-09-11 lap36의 허용된 새 원본 run은 HQ 선택 뒤 content `(670,490)` 클릭에서 player0
생산 상태 변화가 없어 FAIL했다. lap38 middle은 보존 SHA/PNG/reader 결선을 독립 대조해 slot1199
type58 owner0 선택은 지지되지만, 해당 좌표를 활성 생산 아이콘에 묶는 원본 hit-test/callback
provenance가 없고 테스트도 production 경로를 실행하지 않음을 확인했다. 또한 `_wait_state`가 먼저
예외를 내 production 입력 행과 after 캡처를 남기지 않는다. 판정은 **HARNESS CONTRACT REVISE /
GAME RUN BLOCKED**이며, 아래 정적 provenance와 새 middle 확인 전 좌표 변경·하네스 수리·게임
재실행을 허용하지 않는다.

2026-09-11 lap40 middle은 lap39 raw chain을 독립 재추출했고 정적 골격은 지지되지만
type58 command-record base는 `0x00686878`로 lap39의 `0x006868B8`과 충돌함을 확인했다.
또한 `0x0041FBC0`은 hit 후 `object+0x58=0x0049B640`을 호출하고, 별도 click gate에서
`object+0x54=0x0049B530`을 호출해 action record를 만든다. 판정은 **STATIC CHAIN
REVISE / GAME RUN BLOCKED**이며, 아래 lap40 수리와 새 middle 확인 전에는 실행하지 않는다.

2026-09-11 lap43 middle은 lap42의 고정 원본 SHA, type58 주소, 두 callback field,
source/map와 production 직전 helper 호출 결선 및 fresh doctor/targeted35/Fast105/safety를
**CONFIRMED**했다. 그러나 아래 계약의 직접 회귀 중 `x=baseX+N*Δ` 배열과 중복 group cell 거부가
없어 전체 판정은 **TEST CONTRACT REVISE / GAME RUN BLOCKED**다. 새 Luna/high work는
`tests/test_runtime_env.py`의 가상 fixture와 두 회귀만 최소 보강하고 helper/좌표/click 순서/timeout/
게임/EXE/DLL/assets는 바꾸지 않는다. 새 Sol/high가 다시 확인하기 전 runtime-read도 실행하지 않는다.

2026-09-11 lap45 middle은 lap44 tests-only SHA와 두 직접 회귀, 원본 SHA,
doctor/targeted36/Fast106/safety의 fresh PASS를 독립 확인해 **TEST CONTRACT CONFIRMED**로
판정했다. 새 Luna/high work에 기존 `prepare`→`check`→`g1-baseline --screen 1600x1200x24
--timeout 90`을 새 private copy에서 정확히 1회 허용한다. helper/좌표/click flow/timeout/
원본/EXE/DLL/assets는 변경하지 않고, live `production_cell`의 four-cell geometry/callback/
flag/type record, strict target group과 production before/after 효과를 같은 run에서 보존한다.
읽기·필수 gate·cleanup 중 하나라도 실패하거나 worker 의미가 남으면 재시도/좌표 보정 없이
FAIL/UNKNOWN 증거와 `loop/ESCALATE_SOL`을 보존해 새 Sol/high에 돌려보낸다.

2026-09-11 lap61 middle은 lap60의 stable `49B6D0 ineligible`과 raw/cleanup을 독립 확인했지만,
원본 `0x499201..0x499297`이 별도 primary 12-slot command table을 먼저 채우고 `0x49B6D0`은
type flag `0x08`에만 붙는 추가 group2..5 경로임을 재추출했다. 따라서 group2..5를 HQ 생산의
필수 gate로 둔 현재 계약은 **HARNESS CONTRACT REVISE / GAME RUN BLOCKED**다. primary table의
field/action 의미는 UNKNOWN이며 아래 source-only 수리 범위를 승격 검수하기 전에는 구현도 시작하지 않는다.

2026-09-11 lap62 middle 승격 검수는 lap61의 reset/fill/네 배열/조건부 group2..5 경계를 확인했지만,
`0x499583` consume은 predicate 전이 아니라 참·거짓 분기 합류 뒤임을 재추출했다. 또한 아래 lap61
계약은 stable-ineligible의 반환/예외를 고정하지 않아 UNKNOWN인 primary 의미로 production click을
열 위험이 있다. 판정은 **HANDOFF CONTRACT REVISE / GAME RUN BLOCKED**이며, 아래 lap62 좁힌 계약을
새 Sol/Opus5가 확인하기 전 work 구현도 시작하지 않는다.

2026-09-11 lap69 middle은 lap68의 count0/count2 선행 guard와 source/original SHA,
targeted54/Fast124/safety/doctor를 독립 재현해 **SELECTION COUNT REPAIR CONFIRMED**로 판정했다.
그러나 `g1-baseline` 호출부는 stable-ineligible 예외의 primary snapshot을 결과에 보존하지 않고,
eligible이면 의미 미확정 `(670,490)` click으로 진행한다. 따라서 **GAME RUN BLOCKED**이며 아래
lap69 work handoff와 새 middle 확인 전에는 실행하지 않는다.

## lap29 수리 계약 (lap30 적용·lap31 확인으로 소진)

- 확인된 원인: lap26 FAIL은 `0x004ED848`을 PS7 버튼의 즉시 상태로 사용한 하네스 계약 결함이다.
  원본은 selector object `[+0xA4]`를 즉시 바꾸고, global WORD는 연결 `확인` callback 뒤에 쓴다.
- 작업자: Codex `gpt-5.6-luna` / high / work 조사 세션. 자기 결과를 최종 승인하지 않는다.
- 한 카드의 변경: `tools/runtime_env.py`와 관련 `tests/test_runtime_env.py` 또는
  `tests/test_runtime_guards.py`만 최소 수정한다. PS7 selector는 DWORD
  `0x0106A6A4`(왼쪽/여럿)와 `0x0106A86C`(오른쪽/혼자)의 one-hot state를 읽어 검증하고,
  `0x004ED848`은 연결 `확인` 뒤 solo committed mode=1을 확인하는 데만 사용한다.
  테스트가 click stub로 global WORD `1→0→1`을 합성하지 않게 하고, 양쪽 초기 one-hot 분기,
  비 one-hot 거부, 정확한 주소/폭, confirm 뒤 mode 검사를 직접 실행한다. 게임/EXE/DLL/assets,
  좌표, timeout, fixture는 바꾸지 않고 `g1-baseline`도 실행하지 않는다.
- 수리 성공식: targeted runtime tests, `make check`, `bash checks/safety.sh check`가 PASS하고
  static-confirmed 주소/폭 및 fail-closed 의미가 코드와 회귀에 연결되어야 한다. 이후 새 Sol/high가
  독립 확인할 때까지 게임 실행은 금지한다. 이 gate는 lap31에서 충족됐다.

## lap33 수리 계약

- 확인된 원인: lap32 FAIL은 solo PS5에서도 `(134,79)` 수동 ready click과 보이는 control SHA
  변화를 요구한 하네스 계약 결함이다. 원본 `V 1.100KR`은 committed mode WORD=1일 때
  `0x004B7C14`에서 수동 ready poll을 건너뛰고 `0x004B7C68`의 자동 ready 산출로 간다.
- 작업자: Codex `gpt-5.6-luna` / high / work. 자기 결과를 최종 승인하지 않는다.
- 허용 변경: `tools/runtime_env.py`와 관련 `tests/test_runtime_env.py` 또는
  `tests/test_runtime_guards.py`만 최소 수정한다. 원본/좌표/timeout/fixture/EXE/DLL/assets는
  변경하지 않고 `g1-baseline`도 실행하지 않는다.
- 구현 계약: local index DWORD `0x00B63FC4`를 읽어 `0..7`이 아니면 fail-closed하고,
  `DWORD [0x00632CF0 + local_index*4]`를 정확히 4byte로 읽는다. connection confirm 뒤
  `committed_mode=1`, `PS=5`, local ready=1을 함께 요구하고 `player0_ready_setup` 수동 click 및
  ready-control crop 변화 gate를 제거한다. setup evidence에는 수동 입력이 없었다는 사실과 주소·폭·
  local index·ready 값을 기록한다. start `PS5→PS3/tick>0` 및 기존 selector/필수 입력 gate는 유지한다.
- 버전/원복: 수리 전 source SHA는 `tools/runtime_env.py`
  `e06c73a9d9602d1f036ab3f8ebcf306a3ee01e21945fd27b54daab502f6e5e49`,
  `tests/test_runtime_env.py` `5ea8ea87672577bde15dc67cf647a84e382fb1fe2c8f54e9645738546ea1f9fd`,
  `tests/test_runtime_guards.py` `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`다.
  원본 EXE SHA가 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`가 아니거나
  raw old bytes가 주소 문서의 lap33 값과 다르면 거부한다. 바이너리 patch old→new/restore는 N/A이며,
  source 변경은 위 세 SHA의 내용으로 byte-exact 복원 가능해야 한다.
- 수리 성공식: local index 범위/주소/4byte 폭, ready 0 거부·1 허용, solo confirm→auto-ready→start
  production 결선을 회귀가 직접 실행하고 targeted runtime tests, `make check`, safety가 모두 PASS해야
  한다. 새 Sol/high 독립 확인 전까지 게임 실행은 금지한다.

## lap38 정적 provenance 계약

- 확인된 원인 범위: lap36은 원본 생산 실패를 입증하지 않는다. 카드가 요구한 “선택된 HQ의 보이는
  활성 생산 아이콘 중심”과 hard-coded `(670,490)` 사이 의미 연결이 없고, 실패 경로는 production
  입력 행/after state/after PNG도 보존하지 않아 좌표 의미와 실제 delivery를 사후 구분할 수 없다.
- 작업자: 새 Codex `gpt-5.6-luna` / high / work 조사 세션. 자기 결과를 최종 승인하지 않는다.
- 한 가지 probe: SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  원본을 읽기 전용으로 두고, PS3에서 selected slot1199/type58의 command panel 생성과 content
  `(670,490)` hit-test부터 cell/action table 및 callback까지 정적으로 추적한다. 이 점이 실제로
  가리키는 동작과 worker 생산 cell을 VA·raw old bytes·row/column·table/callback 관계로
  `analysis/memory_maps/player_offsets.md`에 기록한다. 확인 불가하면 마지막 검증 주소와 이유를 남긴다.
- 금지/종료: `tools/runtime_env.py`, tests, game/EXE/DLL/assets를 수정하지 않고 `g1-baseline`이나
  다른 게임 run을 실행하지 않는다. 결과는 새 Sol/high가 독립 확인해야 하며, 그 전에는 좌표 수정이나
  실패 증거 보존 수리를 승인하지 않는다.

## lap40 read-only command-cell 증거 수리 계약

- 확인된 수리 원인: type stride는 `0x758`이므로 `0x0066BE88 + 58*0x758` base는
  `0x00686878`이다. `0x0041FBC0` 내 `0x0041FC38`의 `+0x58` 호출과
  `0x0041FC6F`의 `+0x54` click/action 호출을 하나의 callback 의미로 합치지 않는다.
- 작업자/한 가지 변경: 새 Codex `gpt-5.6-luna`/high work가
  `analysis/memory_maps/player_offsets.md`, `tools/runtime_env.py`, 관련 runtime tests만 수리한다.
  원본 SHA/EXE/DLL/assets, 좌표, click 순서, timeout은 변경하지 않고 새 game run은 하지 않는다.
- helper 계약: SHA fail-closed 후 selected count/slot `0..1199`와 unit active/type을 확인하고
  `0x0066BE88 + type*0x758`의 DWORD 4개를 읽는다. object pool에서 active, group `2..5`,
  `+0x54=0x0049B530`, `+0x58=0x0049B640`인 네 cell을 스캔해 `x/y/w/h`, category,
  flag, callbacks, type command value를 기록한다. `(670,490)` membership은 원본
  `0x0041FA60`과 같이 경계를 제외한 strict rectangle로 계산하고 0개/다중 hit를 거부한다.
- 회귀/종료: 가상 read-memory fixture가 type base 산술, 네 group/callback, x=`baseX+N*Δ`,
  strict hit, invalid slot/type/non-unique cell 거부를 직접 검사하고 targeted runtime tests,
  `make check`, safety가 PASS해야 한다. 새 Sol/high가 source SHA·결선·회귀를 독립 확인한
  뒤에만 별도 새 runtime-read run을 허용할지 판정한다.

## lap61 primary 12-slot table 수리 계약 (승격 검수 전 보류)

- 확인된 원인: lap60의 ineligible FAIL은 정확하지만 `0x49B6D0` group2..5는 primary command
  table 뒤의 조건부 추가 경로다. 이를 HQ 생산 provenance의 필수 gate로 둔 것이 하네스 계약 결함이다.
- work handoff: 승격 Sol/Opus5가 아래 범위를 독립 승인하면 새 Luna/Sonnet5/high가
  `tools/runtime_env.py`와 관련 `tests/test_runtime_env.py`/`tests/test_runtime_guards.py`만 수정한다.
  게임/EXE/DLL/assets, 좌표, timeout, fixture는 바꾸지 않고 `g1-baseline`도 실행하지 않는다.
- helper 계약: SHA fail-closed 뒤 selection identity와 함께 12 WORD씩인 네 raw block
  `0x008930A6`, `0x008930D6`, `0x008930BE`, `0x008930EE`를 before/after로 보존한다.
  block은 field0..3/index0..11처럼 의미 중립적으로 기록하고, 크기·선택 identity·raw value 변화는
  fail-closed한다. 기존 `0x49B6D0` predicate/group2..5와 alternate snapshot은 진단 정보로 유지하되
  stable-ineligible만으로 primary table 관측을 중단하거나 production FAIL/PASS로 승격하지 않는다.
- 회귀/버전/원복: zero/nonzero 네 배열, 12-slot 경계, 각 field 단독 변화, selection 변화,
  stable-ineligible에서도 primary snapshot 보존을 직접 검사한다. 고정 원본 SHA는
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; writer
  `0x004A3B5B` old bytes는 `66 8b 54 24 08 0f bf c0 66 89 94 41 96 0c 00 00`이다.
  binary patch/restore는 N/A이고 source는 수리 전 SHA로 byte-exact 복원 가능해야 한다.
  targeted tests, `make check`, safety PASS 뒤 새 middle 확인 전에는 game run을 허용하지 않는다.

## lap62 primary raw snapshot 좁힌 계약 (lap63에서 추가 수리 필요)

- 정정된 제어흐름: index `0..11` primary fill은 `0x004992BE` 전에 끝나지만 consumer
  `0x00499583`은 true `0x004992DF→0x0049B6D0→jmp`와 false/alternate 경로가 합류한 뒤 실행된다.
  primary field/action 및 worker click 연결은 계속 UNKNOWN이다.
- 다음 승인 후보: `tools/runtime_env.py`와 관련 runtime/guards tests만 대상으로, SHA fail-closed 뒤
  `0x008930A6..0x00893105`를 phase마다 **한 번의 contiguous 96-byte read**로 읽는다. 물리 주소 순서
  `A6/BE/D6/EE`의 네 24-byte block을 각 12 WORD로 분리하되, writer 인자 순서
  `A6/D6/BE/EE`와 주소를 함께 기록하고 field 의미는 붙이지 않는다.
- coherence/종료: selection identity와 primary raw 값의 before/after가 모두 같아야 한다. 크기나 값이
  다르면 두 snapshot을 예외/diagnostics에 붙여 fail-closed한다. zero/nonzero는 모두 raw 관측이며
  production 판정이 아니다. stable `49B6D0 ineligible`도 primary before/after를 보존한 뒤 현재처럼
  production click 전에 예외로 중단한다. 성공 반환이나 좌표 click 허용으로 바꾸지 않는다.
- 필수 회귀: SHA mismatch 무-read 거부, 정확한 주소/96-byte 단일 read/12-WORD 경계, zero/nonzero 네
  block, 각 block 단독 변화, selection 변화, stable-ineligible 예외의 primary evidence 보존을 직접
  검사한다. 좌표/timeout/fixture/game/EXE/DLL/assets는 변경하지 않고 `g1-baseline`도 실행하지 않는다.
  targeted tests/Fast/safety 뒤 새 middle 확인 전 game run은 계속 금지한다.

## lap63 exact-single-selection 수리 계약 (lap65 middle PASS / work 대기)

- 새 정적 경계: 원본 `0x00498FBA`의 count DWORD `0x00899024` dispatch에서 count `1`만
  `0x00499201..0x0049929E` primary fill로 들어간다. count `0`은 `0x00498FC3`, count `>1`은
  `0x00498FD2→0x00499336`으로 우회하고 나중에 공통 consumer `0x00499583`에 합류한다.
  따라서 lap62의 단순 identity 안정성은 stable multi-selection의 reset/stale raw 귀속을 막지 못한다.
- work handoff 후보: 새 Sol/Opus5가 승인한 뒤에만 Luna/Sonnet5/high가 `tools/runtime_env.py`와
  관련 `tests/test_runtime_env.py`/`tests/test_runtime_guards.py`를 수정한다. SHA fail-closed 다음,
  before selection count가 정확히 `1`인지 primary read 전에 검사한다. 다른 count는 count evidence를
  보존하고 96-byte primary read 및 production click 전에 즉시 fail-closed한다.
- exact single selection일 때만 lap62 계약을 적용한다. phase마다 `0x008930A6..0x00893105`를 한 번의
  96-byte read로 읽고 물리 block `A6/BE/D6/EE`를 12 WORD씩 의미 중립 보존한다. before/after selection
  identity 또는 raw가 달라지면 양쪽 evidence와 함께 중단하며 stable-ineligible도 evidence 보존 뒤
  성공 반환 없이 click 전에 중단한다. field/action/worker 의미는 계속 UNKNOWN이다.
- 필수 회귀는 stable `selected_count=2`의 primary 무-read 조기 거부, `1→2` 전이의 before/after
  identity와 두 raw snapshot 보존, SHA mismatch 무-read, 정확한 주소/96-byte 단일 read/12-WORD 경계,
  zero/nonzero 및 각 block 단독 변화, stable-ineligible primary evidence 보존이다. 게임/EXE/DLL/assets,
  좌표/timeout/fixture는 변경하지 않고 새 game run도 하지 않는다. targeted/Fast/safety 후 새 middle
  독립 확인 전 game run은 계속 금지한다.

## lap65 middle 승인과 work handoff

- `.venv/bin/pytest` 부재는 환경 재설치 필요가 아니라 Makefile의 정식 entrypoint
  `.venv/bin/python -m pytest`를 사용해야 하는 invocation 문제였다. lap65 fresh targeted
  46 PASS, 전체 Fast 116 PASS, safety PASS, doctor ok=true로 gate를 회복했다.
- 고정 원본/private SHA, count0/count1/count>1 dispatch, count1 전용 primary fill, 분기 뒤
  공통 consumer, reset/writer old bytes가 일치한다. 위 lap63 범위는 **MIDDLE CONFIRM PASS /
  WORK READY**다.
- Luna/Sonnet5 work는 위에 적힌 helper/tests 수리와 회귀만 구현한다. primary field/action
  의미, worker click, game/binary/coordinate/timeout/fixture를 추정·변경하지 않고, targeted/Fast/safety
  후 새 middle 독립 검수 전 game run을 시작하지 않는다.

## lap67 middle 반려와 work handoff

- lap66 SHA와 targeted 52 PASS, 고정 원본 count dispatch는 독립 재현됐지만 count=0은
  `_read_g1_command_selection_identity`에서 먼저 `unsupported selected-unit count`로 끝나
  `branch_evidence`에 required/observed/before/primary_read를 남기지 않는다. primary 96-byte read가
  없다는 안전성은 유지되지만 lap65의 모든 count!=1 evidence 계약은 **REVISE**다.
- 새 Luna/Sonnet5/high work는 `tools/runtime_env.py`와 관련 runtime tests만 최소 수정한다.
  selection count DWORD를 먼저 읽어 count!=1이면 identity의 slot/unit reads와 primary read 전에
  `required=1`, `observed=<count>`, `before={count:<count>}`, `primary_read=false`를 보존해 non-retryable
  fail-closed하고, count0과 count2 직접 회귀를 둔다. count1의 기존 identity/primary/predicate 경로와
  `1→2`, raw-change, stable-ineligible evidence는 유지한다.
- targeted runtime/guards, `make check`, safety가 모두 PASS한 뒤 새 middle이 독립 확인하기 전까지
  game run, primary field/action 의미 추정, 좌표/click/timeout/fixture/EXE/DLL/assets 변경은 금지한다.

## lap68 work 수리 결과 — 새 middle 재검수 대기

- lap67 handoff대로 `tools/runtime_env.py`와 관련 runtime test만 수정했다. selection count DWORD를
  identity slot/unit read보다 먼저 단독 관측하고 count0/count2를 `required=1`, `observed`,
  `before={count}`, `primary_read=false`와 함께 non-retryable 거부한다. count1의 기존 96-byte
  primary/identity/predicate 경로와 `1→2`, raw-change, stable-ineligible evidence는 유지했다.
- source SHA는 `tools/runtime_env.py=815e90e2e2ffe342eb24ad64135c7be802848a6197bb4ec766b53c023970bbad`,
  `tests/test_runtime_env.py=cc30931e4279ac25310eefa8c443cf260df4d21ffc1a147a3fcc78115d4dc5ad`,
  guards unchanged SHA는 `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`다.
- targeted **54 passed**, `make check` **124 passed**, Ruff/compileall/mypy/context/safety PASS,
  `make doctor` original verified. 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`와
  일치하며 후보 EXE/게임 run은 없다. 새 Sol/Opus5 middle이 독립 검수하기 전 game run은 금지한다.

## lap69 middle 확인 및 production 호출부 work handoff

- lap68 count evidence 수리는 **MIDDLE CONFIRM PASS**다. count0/count2 모두 selection count DWORD만
  1회 읽고 identity detail/primary read 전에 `required=1`, `observed`, `before={count}`,
  `primary_read=false`, non-retryable로 중단한다. 원본 count dispatch와 count1 회귀도 유지됐다.
- 새로 확인한 실행 간극: `_read_g1_command_cell_provenance`의 stable-ineligible 예외는
  `primary_snapshot`을 갖지만 `g1-baseline` catch는 command branch와 alternate snapshot만 output에
  복사한다. 반대로 helper가 eligible evidence를 반환하면 호출부는 primary field/action과 worker
  mapping이 UNKNOWN인데도 hard-coded `(670,490)` production click으로 바로 진행한다.
- 새 Luna/Sonnet5/high work는 `tools/runtime_env.py`와 관련 runtime tests만 최소 수정한다.
  예외의 primary before/after snapshot을 결과 evidence에 보존하고, 의미 연결이 별도 middle에서
  승인되기 전에는 eligible snapshot도 production click 권한으로 쓰지 않는 명시적 fail-closed gate를
  둔다. 두 경로 모두 production mouse subprocess가 호출되지 않음을 직접 회귀한다.
- helper의 count guard/phase당 단일 96-byte read/`1→2`/raw-change/stable-ineligible evidence,
  좌표·timeout·fixture·EXE/DLL/assets는 바꾸지 않는다. targeted/Fast/safety/doctor PASS와 새 middle
  독립 확인 전에는 새 game run을 실행하지 않는다.

## lap71 middle 부분 확인 후 필수 gate FAIL

- lap70 source/test/guard SHA, 고정 원본´참고 EXE SHA, `0x00498FBA` count dispatch,
  count1 전용 fill, 공통 consumer, `0x004A3B5B` writer old bytes가 모두 일치했다.
- stable-ineligible primary snapshot이 output evidence에 복사되고, eligible은 명시 gate에서
  `RuntimeSafetyError`로 중단하여 mouse callback이 0회이며, ineligible도 reader 예외에서 callback
  0회로 중단한다. 직접 3 PASS, targeted 57 PASS, 전체 Fast 127 PASS,
  Ruff/compileall/mypy/context/safety PASS, doctor original verified로 source 계약은 부분 확인했다.
- 다만 이 판정을 문서에 기록한 후 재실행한 필수 `make check`는 STATUS 183줄과 180줄
  제한의 충돌로 13 FAIL/114 PASS했다. 지시서의 중단 규칙에 따라 문서를 즉시 압축하거나
  gate를 재시도하지 않았다. lap70은 **MIDDLE CONFIRM 미완료 / GAME RUN BLOCKED**다.
- `loop/ESCALATE_SOL`의 승격 작업자가 상세 provenance를 lap71 이력에 보존한 채 STATUS를
  180줄 이하로 정리하고, 전체 필수 gate를 새로 통과한 뒤에만 evidence-only run 허용을
  재판정한다. primary field/action·worker 의미와 production click은 계속 UNKNOWN/미승인이다.

## lap72 middle overflow 복구 및 fail-closed 확인

- lap71 overflow 원문은 `docs/history/laps/20260911_status_lap71_overflow_recovery.md`와 lap71
  이력에 보존됐고, 검수 시작 STATUS는 141줄이었다. source/test/guard와 원본·참고 EXE SHA,
  count dispatch/fill/consumer 및 writer old bytes는 고정값과 일치했다.
- `make doctor` top `ok=true`/original verified, 직접 no-click/output 3 PASS, targeted 57 PASS,
  전체 Fast 127 PASS, Ruff/compileall/mypy/context 및 safety PASS다. lap70의 output evidence 보존과
  eligible/ineligible callback 0회 source 계약은 **MIDDLE CONFIRM PASS**다.
- 다음 Luna/Sonnet5/high work는 새 private manifest를 `prepare --timeout 60`→`check`한 뒤
  `g1-baseline --screen 1600x1200x24 --timeout 90`을 정확히 1회 실행한다. 코드/tests/binary/fixture/
  좌표/timeout을 변경하거나 실패 뒤 재시도하지 않는다.
- 기대 stop은 live primary evidence를 기록한 뒤 `production click blocked: primary field/action and
  worker mapping are not approved`로 production mouse 입력 전에 fail-closed하는 것이다. 전체 process
  exit가 아니라 original/private SHA, manifest, 1600×1200 root·800×600 crop, live evidence, callback
  미호출, owned cleanup과 artifact SHA를 판정한다. 더 이른 실패도 그대로 보존해 `ESCALATE_SOL`로
  새 middle에 넘긴다. 제품 G1과 primary field/action·worker 의미는 계속 UNKNOWN이다.

## lap74 middle fresh evidence 확인과 다음 work 조사 계약

- lap73 manifest/baseline/verdict/provenance/harness, 원본/private EXE와 8개 PNG SHA는 재계산
  일치했다. 1600x1200 root 안의 원본 800x600 game/content, PS9/PS3 surface, setup·선택 입력,
  `49B6D0` stable-ineligible, production callback 미호출과 owned cleanup은 **MIDDLE CONFIRM PASS**다.
- 이는 narrow evidence 판정이다. `verdict.overall=FAIL`/`required_inputs=false`를 유지하며 실제 2배
  출력, production/drag/minimap, primary field/action·worker 의미, G1-A/G1과 사용자 승인은 미완료다.
- 다음 Luna/Sonnet5/high work는 게임을 재실행하거나 source를 고치지 않고 고정 원본을 정적으로 읽어
  `0x00499583→0x004A3A40` 이후 primary 12-slot의 cell 생성 call까지 추적한다. 각 call의 index,
  `A6/BE/D6/EE` 인자 provenance, callback/action, strict rectangle과 old bytes를 표로 남기고,
  HQ worker 생산 후보가 유일한지 판정한다. 유일 연결이 불가능하면 추측하지 말고 concrete blocker로 끝낸다.
- game run, production click, harness/tests/binary/fixture/좌표/timeout 변경은 다음 middle 승인 전 금지한다.

## lap76 middle primary-cell 독립 확인과 dispatch probe 계약

- 고정 원본 SHA와 lap75의 8개 entry old bytes가 일치했다. direct xref상 `0x0049B6D0` call은
  조건부 `0x004992DF` 하나뿐이며 primary consumer `0x00499583..0x00499BCF`에는 확인 대상
  constructor/callback direct call이 없다. lap75의 단절/UNKNOWN 판정은 **MIDDLE CONFIRM PASS**다.
- 다음 Luna/Sonnet5/high work는 원본만 읽어 `0x00499583..0x00499BB8`과
  `0x0049AD33..0x0049AFB8`의 A6/BE/D6/EE read→branch/callee/input/action dataflow 표를 만든다.
  unique production dispatch를 old bytes로 증명하면 PASS, render/state-only 또는 복수 의미면 UNKNOWN이다.
- game run, production click, harness/tests/binary/fixture/좌표/timeout 변경은 금지한다. 결과는 다음
  새 Sol/Opus5/high가 독립 검수하며 G1-A/G1과 사용자 승인은 계속 미완료다.

## 고정 입력과 명령 계약

기준 manifest는
`local/runtime/20260910_222434_2612938_0/manifest.json`이고 SHA256은
`8e75369d9dedf77263bc71630fc8e2c94a31c987437f45c93fe4206b1ef4b5d4`다.
원본/격리 EXE의 기대 SHA256은
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`다.

작업자는 아래 인터페이스를 `tools/runtime_env.py`에 `g1-baseline` 하위 명령으로 구현한다.
기존 `prepare/check/smoke` 의미와 90초 상한은 바꾸지 않는다. 새 명령도 한 실행당 90초 상한이다.

```sh
.venv/bin/python tools/runtime_env.py prepare --timeout 60
# 위 JSON의 output.run_dir에서 새 MANIFEST를 정하고 값을 기록한다.
.venv/bin/python tools/runtime_env.py check --manifest "$MANIFEST"
.venv/bin/python tools/runtime_env.py g1-baseline \
  --manifest "$MANIFEST" --screen 1600x1200x24 --timeout 90
```

`g1-baseline`은 새 manifest의 전용 prefix가 비어 있고 ownership/해시 검사가 통과한 뒤에만 실행한다.
충돌 없는 `:90..:199` display를 잡고 Wine virtual desktop도 정확히1600×1200으로 만든다.
`LANG/LC_ALL=ko_KR.UTF-8`, `WINEARCH=win32`, `WINEDLLOVERRIDES=ddraw=b`를 유지한다.
기존 run/prefix/display에 붙지 않으며 종료 시 자신이 만든 자식·prefix wineserver·Xvfb만 정리한다.

허용 변경 파일은 `tools/runtime_env.py`, 관련 `tests/test_runtime_env.py` 또는
`tests/test_runtime_guards.py`뿐이다. 다른 파일이 필수라면 실행하지 말고 REVISE 근거를 남긴다.
필수 회귀는 다음이다.

```sh
.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py
make check
bash checks/safety.sh check
```

## fixture와 장면

lap29 개정: 아래 selector 의미는 global WORD `1→0→1`이 아니라 두 object `[+0xA4]`의
one-hot state로 검증한다. `0x004ED848`은 연결 `확인` 뒤 committed mode로만 읽는다.
lap33 수리와 새 Sol/high 확인 전에는 아래 setup을 재실행하거나 임의 화면 SHA만으로 대체하지 않는다.

- fixture: 새로 복사한 무수정 원본의 기본 2인 임의게임. 제목에서 content `(184,560)`을 눌러
  PS9→PS7로 들어간다. 두 object state가 정확히 one-hot인지 확인하고, 왼쪽/여럿 state가 1이면
  content `(462,169)`의 보이는 `혼자하기`를 눌러 `(left,right)=(1,0)→(0,1)`을 확인한다.
  이미 `(0,1)`이면 click을 SKIP하고 사유를 기록한다. 그 뒤 content `(608,564)`의 `확인`을
  누르고 PS4/5/6→PS5 endpoint와 `0x004ED848` WORD=1을 함께 확인한다.
- setup에서 사용한 모든 X11/content 좌표와 전후 PS를 기록한다. 숨은 메모리 쓰기, control bridge,
  save011/012, QHD 후보, 진단 DLL, 생성/자원 지급은 사용하지 않는다.
- `확인` 뒤 최종 `PS=5`와 8개 슬롯·지도·설정이 보이는 새 로비 화면을 endpoint로 판정한다.
  원본의 PS4→PS5 정적 전이는 주소 문서에 기록하되 런타임이 순간 PS4를 놓친 것만으로 실패시키지
  않는다. PS7 복귀를 기다리지 않는다. solo mode에서는 준비 control을 누르지 않고 local index
  `0..7` 및 `DWORD [0x00632CF0 + local*4] == 1`을 읽어 원본의 자동-ready 상태를 확인한다.
- 선택 전후 화면은 커서를 두 버튼 밖 중립 좌표로 옮기고 짧게 안정화한 뒤 캡처한다. PNG SHA
  변화만으로 선택 효과를 PASS하지 않으며, 커서/hover 차이는 selector 변화로 세지 않는다.
- PS3와 tick 증가, owner0/1의 nation 비0 및 각 1개 이상 실제 active unit을 함께 확인해야
  전투 장면으로 인정한다. 지도/세력/카메라/선택 대상과 관측 가능한 seed를 기록한다.
- 지도 또는 장면을 같은 입력으로 재현할 식별자가 전혀 없으면 G1-A FAIL이다. 결과를 보고
  다른 fixture로 바꾸지 않는다.

## 사전에 고정한 setup 입력과 기대값

창 테두리를 제외한 content 좌표를 기준으로 하고 X11 좌표는
`window_content_origin + content`로 계산한다. 입력 직전 계산값을 먼저 증거 JSON에 기록한 뒤 주입한다.

| 입력 | content 기준 | PASS 효과 |
|---|---:|---|
| 메뉴 | `(184,560)` | PS9→PS7, 화면 SHA 변화 |
| 혼자하기 선택 | `(462,169)` | PS7 유지, selector object state `(1,0)→(0,1)`; 이미 `(0,1)`이면 SKIP 사유 기록; 중립 커서 캡처 변화 |
| 연결 확인 | `(608,564)` | 최종 PS5, committed WORD=1, 8개 슬롯·지도·설정 로비 화면 SHA 변화 |
| solo 자동 준비 | 입력 없음 | PS5 유지, local index `0..7`, 해당 ready DWORD=1; 수동 준비 버튼 변화 요구 금지 |
| 게임 시작 | `(608,564)` | PS5→PS3, tick>0, 전투 화면 SHA 변화 |

lap16 `혼자하기` 전후 PNG 차이는 커서/hover를 포함하고 object state를 읽지 않았으므로 입력 효과로
승인하지 않는다. 연결 확인 이후 자동-ready 값과 시작은 새 run의 전후 상태·캡처로 다시 검증한다.
selector object 주소와 `0x004ED848`의 confirm-time 의미는
`analysis/memory_maps/player_offsets.md`의 lap28~29 근거를 따른다.

2026-09-11 lap28 work는 SHA 고정 원본에서 PS7 두 control object의 생성 old bytes, `0x004B91E0`
poll → `0x00405560` → `0x00404C20` vtable `+0x54` callback, object `[+0xA4]` state
reader/writer, 그리고 `0x004B9341/0x004B9390`의 `0x004ED848` WORD branch/write를
정적으로 확인해 `analysis/memory_maps/player_offsets.md`에 기록했다. object 순서와 한국어
label 대응은 정적으로 확정되지 않았으므로 selector gate는 여전히 UNKNOWN/REVISE다. 새
Sol/high 독립 확인 전에는 게임 재실행·하네스 수정·새 `g1-baseline`을 허용하지 않는다.

2026-09-11 lap29 middle은 같은 SHA와 raw bytes를 독립 재확인해 lap28의 정적 chain을
**CONFIRMED**했다. 동시에 `0x004ED848` write가 selector click 직후가 아니라 연결 `확인`
control `0x01071F18`의 callback gate 뒤에 있음을 확인했다. 두 selector anchor와 lap26 보존 PNG를
결합하면 첫/왼쪽 object는 `여럿이하기`, 둘째/오른쪽 object는 `혼자하기`에 대응하지만 이는
과거 캡처를 결합한 위치 근거이며 새 runtime 성공이 아니다. 현재 판정은 **HARNESS CONTRACT
REVISE / GAME RUN BLOCKED**다. 위 work repair와 새 Sol 확인 전 새 실행을 허용하지 않는다.

## 전투 장면 필수 입력과 기대값

setup을 통과한 같은 run에서 아래 다섯 입력을 수행한다.

| 입력 | content 기준 | PASS 효과 |
|---|---:|---|
| 메뉴 | 위 setup의 `(184,560)` | PS9→PS7, 화면 SHA 변화 |
| 유닛 선택 | 실제 장면에서 보이는 owner0 HQ 중심을 캡처에 표시하고 주입 전 좌표 고정 | selection count `0→>=1`, 첫 선택 slot/owner 기록, 패널 변화 |
| 드래그 선택 | owner0의 보이는 HQ와 일꾼을 함께 감싸는 사각형; 주입 전 네 좌표 고정 | selection count `>=2`; 불가능하면 FAIL |
| 미니맵 이동 | 미니맵 원 안에서 현재 카메라와 다른 지점; 주입 전 좌표 고정 | camera `(x,y)` 중 하나 이상 변화 |
| 생산 | HQ 선택 뒤 보이는 활성 생산 아이콘 중심; 주입 전 좌표 고정 | selected HQ의 production/progress 또는 owner0 reserved/count 중 하나가 기대 방향으로 변화 |

각 행은 before/after 상태와 PNG를 모두 갖는다. 좌표를 결과에 맞춰 재주입하거나 기대값을
완화하지 않는다. 첫 장면에서 해당 조작이 불가능하면 장면 선택 실패로 판정한다.

## 필수 관측과 산출 경로

모든 기계 증거는 새 run의 `output/g1_a/` 아래, PNG는 공유 temp에
`YYYYMMDD_HHMMSS_<run_id>_g1a_<tag>.png`로 저장한다.

1. `provenance.json`: 기준/새 manifest SHA, 원본·실행 EXE와 support DLL 실제 재해시,
   명령/환경/display/prefix/game root, 변경 전후 하네스 파일 SHA.
2. `window.json`: root/virtual desktop/game window/content child의 id·x·y·width·height·border,
   content crop 규칙. 메뉴와 전투 crop은 정확히800×600이어야 한다.
3. `surface.json`: 같은 SHA에 문서화된 renderer `0x00E5BF18`의
   mode/width/height/bpp/stride/current-height raw bytes와 해석, viewport `0x00B3AC80` 4개 값.
   PS9와 PS3에서 각각 읽고 주소 근거를 함께 적는다.
4. `modules.json`: 실제 게임 PID의 `/proc/<pid>/maps` 원문 SHA와 로드된 EXE/DirectDraw 관련
   모듈의 해석된 경로·파일 SHA. builtin 경로를 해시할 수 없으면 이유를 적고 FAIL한다.
5. `scene.json`: PS/tick, 지도·세력·seed 또는 재현 식별자, owner0/1 active unit 수,
   카메라와 입력 대상. 합성/생성 fixture가 아님을 명시한다.
6. `inputs.jsonl`: setup 입력과 위 필수5입력 각각의 X11/content 좌표, before/after 상태,
   기대/실제/PASS·FAIL, 대응 PNG 경로·SHA.
7. `boundary.md`: `게임 render surface → 표시/스케일 경계 → X11 content → 입력 역변환 → 게임 입력`
   행별 evidence pointer와 관측/추론 구분.
8. `verdict.json`: 항목별 PASS·FAIL·SKIP, cleanup, 남은 위험, 후속 최소 가역 probe **하나**.
   probe에는 변경 지점·old bytes·정확 버전 거부·원복 또는 불가능 근거가 있어야 한다.

## PASS / FAIL / 중단

위 8종이 같은 새 run/장면을 가리키고, 원본SHA·격리·800×600 crop·surface/module·필수5입력·
cleanup이 모두 PASS일 때만 G1-A PASS다. exit0이나 PNG 존재만으로 PASS하지 않는다.

원본SHA 불일치, 전용 prefix/display 미확보, 원본/참고 경로 쓰기, PS3/동일 장면 재현 실패,
module/surface 불명, 입력 효과 미관측, 잔류 프로세스가 있으면 즉시 FAIL하고 패치하지 않는다.
lap31 확인 뒤 승인된 새 실행은 최대1회다. 실패 run은 지우거나 덮어쓰지 않으며 총60~90분에서
중단하고 manifest·로그·PNG·verdict를 보존해 Sol/high에 돌려보낸다.

lap4와 lap16의 통제된 FAIL, 역할 위반으로 중단된 미완성 run은 모두 실패 자료로 보존한다.
lap18은 `tools/runtime_env.py`와 관련 runtime tests에 selector 2byte read, 위 1→0→1 정규화,
중립 커서 캡처, confirm/ready PS5 endpoint를 적용했다. lap19 REVISE 후 lap20이
setup evidence 의미 회귀, ready-control local crop, `PS5→PS3` 기대값을 수리했고
lap21이 독립 CONFIRMED했다. lap26이 그 뒤 허용된 1회를 사용해 selector gate에서 FAIL했고,
lap27은 WORD의 UI 의미가 미입증임을 확인했다. lap30이 정적 provenance에 맞게 수리하고 lap31이
독립 확인했다. lap32 run 뒤 lap33은 solo ready가 수동 click이 아니라 자동 상태임을 확인했으므로
현재 실행은 다시 차단됐다. lap33 수리와 새 middle 확인 뒤에만 `docs/STATUS.md`가 새 1회를 허용한다.

## middle 사전 컨펌 근거와 한계

- 이전 lap의 소스8개, 원본/격리 EXE, MASTER_PLAN/STATUS/lap2 및 Fast 로그 해시는 재계산 일치.
  기존 manifest `check`도 PASS했다.
- 현재 하네스는 화면1024×768, 제목 입력1회에 고정되어 G1-A를 직접 만족하지 못한다.
  따라서 위 보강은 게임 패치가 아니라 명시된 관측 간극을 메우는 선행 조건이다.
- 과거 QHD의 renderer 주소와 입력 사례는 같은 원본SHA의 주소 근거로만 사용한다.
  과거 장면/캡처/성공 판정을 새 G1-A 증거로 승격하지 않는다.
- 실제 PS5→PS3 UI 경로와 다섯 입력의 성공은 아직 미검증이다. 실패 시 Luna가 우회·패치하지 않고
  증거를 보존해야 하며, 다음 Sol/Opus5가 결과를 독립 컨펌한다.
