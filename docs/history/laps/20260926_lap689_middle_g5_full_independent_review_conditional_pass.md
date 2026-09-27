# 2026-09-26 | lap 689 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code claude-opus-5-5 / high / middle(중간계획·컨펌). 게임 코드·제품 EXE 수정 없음.
- 가설 / 사용자 관찰: 20:15 운영자 판정 — lap688 N=5(후보 `ever_command4` 5/5회 20 초과)를 공격 브로드캐스트 50 근거로 삼고
  G5 전체(드래그50·51번째 거부, 그룹/호출/저장로드, 이동 paired, 공격, v3 크래시 수정, make check)를 새 middle이 독립 재검수.
- 예상 PASS / FAIL 조건: DESIGN G5 합격문(드래그1회 50 선택, 이동/공격 명령 50 전달, 51번째 미선택, UI·부대지정·저장/로드
  크래시/오염 없음, 원본 대비 근거, 멀티 영향 별도 표시)의 각 항목이 **보존된 raw artifact**로 독립 재확인되면 2단 승인.
- 변경 파일 / source fingerprint / 커밋: 이 파일, `docs/STATUS.md`, `docs/feedback/{INBOX,APPROVALS}.md`, `loop/ESCALATE_SOL`(추가).
  검수 대상 source: `tools/g5_worker_relative_move_attack_probe.py` sha256 `e9c28c47168f8d1b…`(lap688 uncommitted diff),
  `patches/selection/g5_selection_cap50_v3.py` `05abb2db5b5bf40f…`. uncommitted(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `game.exe` `b56986e0…c9c08a8ac`(참고 저장소에서 재해시, 불변).
  후보 v3 `e5004764…de6977`(lap688 candidate-1..5 artifact exe 5개 재해시 일치). 솔로 로비, owner0 type2 55기 op5 합성 fixture
  (+ 가시 일꾼 1), 공격 표적 owner1 type2 1기. 멀티 미실행.

## 독립 재확인 (raw artifact 직접 파싱)

| 항목 | 근거 artifact | 원본 | 후보 v3 | 판정 |
|---|---|---|---|---|
| 드래그 선택 / 51번째 거부 | lap684 `..._roundtrip_{original,candidate}/run1/probe-result.json` (d1ab2899 / ee439e0e) | 20 (55기 중) | 50 unique (55기 중 5기 미선택) | PASS |
| 부대지정 저장·호출 | 같은 파일 `ui_roundtrip` | 20/20 | 50/50, checks 7/7 True, `group_stored_stock20_plus_overflow49` | PASS |
| 저장/로드 후 호출 | 같은 파일 | 20 | 50 unique, crash/error 없음 | PASS |
| 이동 전달 | lap682 `..._original_v2_064916` / `..._candidate_v2_065023` | ever 20/20 | ever 50/50 | PASS |
| 공격 전달 | lap688 `20260926_lap688_g5_repeat/{original,candidate}-{1..5}` | 아래 | 아래 | PASS(근거 교체) |
| v3 크래시 수정 | lap683 승인 + lap684 roundtrip + lap688 10회 모두 status 완주·cleanup ok | — | fault 0 | PASS |
| UI 표시 | lap688 `after-drag.png` 원본-1/후보-1 나란히 육안 대조 | 20기 선택 괄호, 명령 패널 | 약50기 선택 괄호, 동일 패널, 깨짐 없음 | PASS(스크린샷 수준) |
| Fast 검사 | `logs/gates/20260926_lap688_make_check_run1.log` 1003 passed / ruff / `CONTEXT_PASS`; 이번 lap targeted 7 passed, `SAFETY_PASS` | | | PASS |

### 공격 — `ever_command4`는 근거로 쓸 수 없고, 같은 raw의 pending-word가 근거다

- **`ever_command4_count` 반려:** probe(`sample_attack_window`)는 선택 슬롯의 `command==4`를 표적과 무관하게 센다.
  `observed_target_uids`에 스폰 표적 handle이 아닌 uid(459945, 394410, 525480)가 원본-1/3·후보-3/5에 나타난다 —
  즉 다른 적에 대한 자동교전도 command4로 계수된다. 표적은 아군 격자 2칸 밖에 스폰되므로 명령을 못 받은 유닛도
  자동교전으로 command4가 될 수 있어, "매회 20 초과"는 브로드캐스트가 20을 넘었다는 증명이 아니다. 20:15 판정의 근거 문구를 이것으로 정정한다.
- **채택 근거 1 — t=0 스냅샷 pending-word:** 후보-1/2 첫 샘플(elapsed 0.0)에 선택 49기 **동시에**
  `pending_command==0x1000004`, `pending_xy`=클릭 목적지 (18,98) 49/49. 슬롯 1146~1195로 3개 청크(20/20/10) 전부 포함.
  자동교전은 클릭 목적지 좌표로 공격 pending을 쓰지 않으므로 명시적 공격 명령이 49기 전원에 전달된 직접 증거다. 원본-4/5 같은 조건 19/19.
- **채택 근거 2 — 표적 uid:** 후보-3 `rows_at_max` 49/49가 `pending_target_uid==1136`(스폰 표적 handle), 원본-1/2 19/19가 표적 handle.
- **나머지 회차가 낮은 이유:** pending 값은 약 0.8초 안에 소비되며(0.0초 49 → 0.1초 22~24), 첫 샘플이 0.1초에 잡힌 회차
  (후보-3/4/5 18/12/23, 원본-1/2/3 7/11/8)는 소비가 시작된 뒤를 본 것이다. 원본도 같은 패턴이므로 후보 결함이 아니라 샘플링 지연이다.
  `attack_pass`(=max_pending==capable) 불리언이 회차마다 흔들리는 것도 이 때문이다.

## 멀티 영향 메모 (v3 소스 확인, 실행 증거 없음 → `UNKNOWN`)

- 60바이트 명령 레코드 형식·하위 소비자(네트워크 relay 큐, 50슬롯 dispatch 큐)는 불변. >20 선택의 실제 명령(type {1,3,4,7,8,9})만
  같은 레코드를 20기 단위로 최대 3회 발행 → 명령당 패킷/레코드 수 최대 3배, ≤20 선택과 비명령 호출은 원본과 비트 동일 경로.
- 미확인 위험: (a) 3개 레코드가 같은 lockstep 틱에 묶여 전 피어에 도달하는지, (b) 연속 명령 시 50슬롯 dispatch 큐를 3배 속도로 소모하는지,
  (c) 비패치 피어와의 혼합 세션. 멀티 동기화는 사람 승인으로 바꾸지 않고 `UNKNOWN` 별도 표시.

## 측정값 / 판정

- **G5 2단(단일플레이) middle 독립 검수: 조건부 PASS.** DESIGN 합격문의 선택50·51번째 거부·이동/공격 50 전달·UI·부대지정·저장/로드·
  크래시 항목을 원본 대비 raw로 재확인했다. 공격은 `ever_command4`가 아니라 pending-word(0x1000004+클릭 xy, 표적 uid) 근거로 승인한다.
- 조건: 멀티 동기화 `UNKNOWN`(별도), 사용자 milestone 3단 승인 없음. 제품 G5 최종 PASS는 사용자 판단 후에만 선언한다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 비차단 결함(work handoff): `tools/g5_worker_relative_move_attack_probe.py` 82~97행·127~128행 주석이 lap688 lap 기록에서 **반증된** "스폰 위치 혼잡"
  가설을 POLL_TIMEOUT 확대의 근거로 적고 있다. 실제 원인(표적 스폰 시점, 484~498행 주석)과 모순되므로 주석만 정정한다.
- 선택적 하드닝(비차단): 공격 판정을 순간 최대치 대신 슬롯별 누적 `ever_pending_exact`(0x1000004) 합집합 + 표적 handle 일치 집합으로 기록하면
  샘플링 지연 흔들림이 사라진다. 게이트 조건이 아니며 사용자 판단을 막지 않는다.
- 이 lap은 마일스톤 경계(2단 → 사용자 3단)이므로 `loop/ESCALATE_SOL`에 승격 항목을 추가했다.

## 다음 한 가지

사용자 milestone 판단: G5 단일플레이 50 선택/명령/부대/저장로드를 승인할지(멀티는 `UNKNOWN` 별도). 판단 대기 중 독립 작업은
위 probe 주석 정정(work, 1파일) 한 가지뿐이며, G5 제품 변경은 하지 않는다. 승인 후 우선순위는 STATUS 목표표(G2 전비10000, G1, G4)에서 정한다.
