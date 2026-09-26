# G2 W49S — 정상 로비 시작 화면 증거 1회 (lap589 strategy, 2026-09-25 KST)

- 입력: INBOX 2026-09-25 08:05 Q12 위임 결정(**A · 나 · iv · "화면 1회"**, 번복 가능), S5′ 제출문 `docs/reports/20260925_G2_S5P_MILESTONE_RESUBMISSION_LAP589.md` §3·§5, `loop/ESCALATE_SOL` §139.
- **G2 PASS·마일스톤 마감·G1/G4 재개가 아니다.** 결과는 S5′ 부록으로만 붙인다.
- **lap591 strategy 정정(§140 부분 동의, `ESCALATE_SOL` §141):** 원문 카드 SHA256 `9eed66d5…2976`. 이 카드는 "8 AI"만 허용해 Q12-2 `(나)`("사람 1명+AI 또는 AI 8명")를 좁혔다. 아래 §2·§3.3·§3.5를 **활성 8명(두 역할 구성 중 하나)** 기준으로 고쳤다. 나머지 조건은 그대로다. 이 정정 뒤 이 카드에 대한 계획/검수 회차는 더 두지 않는다(N216).

## 1. 왜 이 실행인가

- W49/W49R은 goal chain `_custom_game_chain_inject_g2_eight_ai_seed42`로 게임을 시작했다. 월드가 처음부터 검정이었고 카메라를 맞춰도 같았다(H-cam 약화).
- 2026-09-20 양성 캡처 `…scene_after_lobby_start…png`(V1 0.7953)는 `tools/runtime_env.py` `g1_baseline`의 **UI 로비 클릭 시작**에서 나왔다. 같은 실행의 캡처 이름 순서가 `title_before_menu`→`lobby_after_menu`→`solo_mode_selected`→`local_lobby_ready`→`scene_after_lobby_start`다. 브리지 `_inmm.dll`은 두 경로 모두 프로세스 시작 때 로드된다.
- 따라서 가를 변수는 **시작 경로** 하나다(H-path). 같은 runner를 다시 돌리는 blind retry가 아니다.

## 2. 고정 입력과 허용 변경

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 SHA 동일해야 함), 결합 후보 `dfdc91adb88a732d96dff96f78648f03406003bffce1b22a7e5836317f963883`. **활성 8명**(owners 0..7, 아래 §3.5의 역할 구성 R-AI8 또는 R-1L7 중 하나), 지도 100×100, cap `[5000]*8`, W46~W49 혼합 fixture, op `{5,6,7}`만. 교전·저장/로드·AI 변경 없음.
- 새 파생 runner는 공유 temp의 새 lap 디렉터리에 둔다. 기존 runner·raw·캡처는 덮어쓰지 않는다. 제품 source(`patches/`)와 카메라·시야·렌더 메모리 쓰기는 금지한다.
- 허용 diff는 다음뿐이다. (a) 게임 시작을 goal chain 대신 게임 자신의 UI 로비 시작 버튼으로 한다. 클릭 순서는 `g1_baseline` 경로를 재사용하고 활성 8명·100×100 설정 입력을 더한다(`g1_baseline` 자체는 default two-player이므로 8명 설정 근거가 아니다). (b) 미니맵 클릭 좌표를 N214대로 고친다. (c) 캡처 접두사를 새 lap으로 바꾼다.

## 3. 게임 전 확인 (하나라도 FAIL이면 게임 없이 `BLOCKED(gate)`)

1. lap583 criterion probe를 재실행한다. canonical `82024e73…5a03`이어야 한다.
2. **N214 좌표 회귀:** 새 미니맵 점을 lap587 `g0_before` PNG에 대 본다. 점이 마름모 검정 내부 안에 있어야 한다(y545 기준 x1~161 범위 안쪽). "설정" 버튼(x199~275, y500~517)과 겹치면 안 된다. 좌표식과 근거를 기록한다.
3. **S0 경로 가능성(≤60분, 게임 없음 또는 로비까지만):** UI로 **활성 8명**과 100×100을 고른 뒤 시작할 수 있는지 확인한다. 우선순위는 R-AI8(W45R~W49R 안정성 raw와 같은 구성)이고, 로비가 로컬 사람 슬롯을 비울 수 없으면 R-1L7을 쓴다. 두 구성 모두 UI로 만들 수 없을 때만 `NOT_FEASIBLE(ui_8active)`로 끝낸다. 활성 인원을 8명 미만으로 줄여 대체하지 않는다. 고른 구성과 그 이유를 기록한다.
4. `py_compile`, op 정적 검사 `{5,6,7}`, `checks/safety.sh check`=`SAFETY_PASS`, 원본 pin, 빈 private display.
5. **PS3 역할 gate(게임 중, S1 캡처 직후·시딩 전; FAIL이면 시딩 없이 `BLOCKED(active8_gate)`로 종료):** owners가 정확히 0..7이다. 각 owner에 nation, 살아 있는 HQ49와 worker7이 있다. `cap==5000`, `reserved==0`, 지도 `MAP_W/H`=100×100, 시작점 8개가 서로 다르다. AI 역할 vector는 둘 중 하나와 정확히 같아야 한다.
   - **R-AI8:** `[1,1,1,1,1,1,1,1]`.
   - **R-1L7:** `ai==0`인 owner가 정확히 1명이고 그 owner가 `local_index`와 같다. 나머지 7명은 `ai==1`이다. `local_index==0`이면 `[0,1,1,1,1,1,1,1]`이다.
   - `tools/runtime_env.py` `_g2_initial_creation_gate`의 config/seed 검사(`d42/d44/d48/d4a/d92`, seed42)는 goal chain 전용이다. UI 시작에는 적용하지 않고 값만 raw로 남긴다.
   - R-1L7이면 기록에 적는다. 이 run은 화면 증거이고, 안정성 raw(W46/W47, R-AI8)를 대체하거나 R-1L7의 144k 안정성을 증명하지 않는다.

## 4. 실행 (fresh foreground 정확히 1회, ≤45분; 남은 시간이 부족하면 시작하지 않음)

| 단계 | 캡처 | gate |
|---|---|---|
| S1 로비 시작 직후, 시딩 전 | `start` | **V1≥0.30** (FAIL이면 시딩 없이 `BLOCKED(capture_contract)`로 종료. 화면 축은 영구 종료) |
| T0 시딩 완료 | `t0` | V1≥0.30, 8 owner `used`≥4900·≤5000 |
| +2000 tick | `plus2000` | V1≥0.30 |
| 수정 좌표 미니맵 클릭 직후 | `minimap` | V3: 클릭 receipt 존재, 이미지가 `plus2000`과 다름 |

- V1 정의는 lap583 probe와 같다. 박스 (0,30)~(800,470), RGB max 채널>24, 비율≥0.30이다.
- V2: `start`·`t0`·`plus2000`·`minimap` SHA가 서로 모두 달라야 한다.
- R: raw 전 구간에서 tick 역행 0, `live==Σcount`, 라이브 `used`≤5000, 할당 실패 0, 원본 SHA 전후 동일, 실행 후 owned display·process 잔류 0.
- 보고 전용(사람 판정): T0 월드에 시딩 유닛이 보이는지, 미니맵 내용(N213).
- 라벨: 모두 통과하면 `W49S_SCREEN_PASS`, 아니면 실패한 첫 gate 이름. **결과와 무관하게 재실행은 없다.**

## 5. 그 다음

1. 다음 middle은 summary 없이 PNG·manifest·samples로 V1~V3·R을 재계산한다. PNG를 직접 보고 월드·유닛이 보이는지 기록한다.
2. strategy는 S5′ 제출문에 부록을 붙인다. PASS면 캡처를 첨부하고, 아니면 "화면 미검증 확정"으로 적는다. G2 PASS 확정은 여전히 사용자만 한다.
3. **N216 제품 증거 무증가 판정(lap591 strategy):** lap588~591은 네 회차 연속 새 실행 증거가 없다. strategy는 화면 축을 **정확히 한 번 더 계속**하기로 판정한다. 다음 회차는 반드시 이 카드의 work(S0→§3.5→§4)다. S0가 `NOT_FEASIBLE(ui_8active)`이거나 어떤 gate가 FAIL이면 화면 축은 "미검증 확정"으로 닫는다. 카드 재정정이나 재계획 회차는 두지 않는다.
4. 금지: 새 Wine/DLL 설치(Q12-3=(iv)), W48 재실행, 교전 재개, fixture/op 변경, 카메라 메모리 쓰기, G2 PASS·사용자 승인 대리.
