# G2 strategy lap583 — §132 처분: (B) W49R 카메라·캡처 경로 수리 + fresh 정확히 1회

- 작성: lap583 strategy. 실제 모델 Claude Code `claude-opus-5-5`(effort 세션 비노출). 라우팅 계약의 strategy 모델(`claude-fable-5`/Astra)이 아니며 lap567·572·577·580과 같은 대체다. 게임 실행 0, 제품 source·하네스·후보·raw 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL` §132(lap582 middle: W49 raw `ACCEPT`, 화면 `REJECT / BLOCKED(capture_contract)`, N211 `ACCEPT`), 카드 `G2_STRATEGY_S4_TRANSPORT_W48_LAP577.md` §5, INBOX 2026-09-24 23:05 상시 지시(절차·예산은 묻지 말고 결정).
- **이 문서는 G2 PASS·마일스톤 마감·다음 목표 전환이 아니다.** 번복 가능한 strategy 결정이다.

## 1. §132 확인 (이전 바퀴 검수)

- lap582 probe `docs/history/laps/probes/20260925_lap582_middle_w49_independent_review.py`를 이번 세션에서 세 번째로 다시 돌렸다. exit0, canonical SHA `5073c7dd219b2c4a645394e3d203ac7efb333e3da0d7367c848525cd463dd6fc`로 lap582 두 번과 같다. raw 269행, tick75→10027, 역행0, live-count 불일치0, used4950~5000, VM `3,463,732`KB 고정.
- Wine `dpwsockx.dll` SHA `3b4f6a9d355114fb78f1e2a3961f48324b654c7e246a1bcd0925f3cdbe7986c9`를 다시 확인했다(N211 대상 동일).
- PNG를 직접 봤다. HUD(자원 996700/996700, 전비 `4995/5000`, “전비가 부족합니다” 알림, F1~F11, 명령 패널)는 렌더된다. 그러나 월드 영역과 미니맵은 검정이다. 시딩 전(tick15)부터 이미 검정이므로 fixture 때문은 아니다.
- **§132의 세 판정(raw ACCEPT / 화면 REJECT / N211 ACCEPT)에 동의한다.**

## 2. 신규 근거

### N212 — 캡처 경로 자체는 월드를 찍는다 (§132 handoff 2의 전제 반박)

§132는 “검정 월드가 DirectDraw 캡처 한계인지”를 먼저 좁히라고 했다. 기존 증거로 이미 답이 나온다. 같은 Xvfb 1600×1200 + Wine + `ddraw=b` + scrot 경로의 2026-09-20 캡처에는 지형·건물·유닛이 보인다.

읽기 전용 probe `docs/history/laps/probes/20260925_lap583_strategy_w49r_capture_criterion.py`(SHA `dd24b445…585a`)를 2회 실행했다. 두 번 모두 canonical SHA `82024e73c20eb01433793660df9cdf1ccd889be9ec5143329a5bf1fb20665a03`, A1/A2/A3 true였다.

| 대조 | 파일 | 월드 비검정 비율 (0,30)~(800,470), 밝기>24 |
|---|---|---|
| 양성 | `20260920_024748_supply5000_shot-slot1200-scene.png`(1600×1200) | 0.8102 |
| 양성 | `…_scene_after_lobby_start_…png`, `…_minimap_before_…png`(800×600) | 0.7953, 0.7946 |
| 음성 | lap581 W49 preseed / t0 / +2000 / +10000 / minimap | 0.0092 / 0.0096 / 0.0096 / 0.0096 / 0.0096 |

따라서 원인은 캡처 도구가 아니라 W49 실행 경로 쪽이다. 차이는 두 가지다. W49는 로비를 거치지 않고 bridge `send_goal(NEW_GOAL)`로 PS7→PS3에 들어간다. 그리고 카메라 입력을 한 번도 주지 않는다(`w49_run.py`에는 타이틀 클릭 하나와 `scrot`만 있다).
가설(미증명): **H-cam** 카메라 타일(`0x00B42D7C`/`0x00B42D80`, `analysis/memory_maps/original_qhd_probe_0910.md`, 원본 SHA `b56986e0…` 동일 빌드)이 local owner의 드러난 영역 밖에 있다. **H-fog** goal 시작 경로에서 local owner 시야가 비어 있다. W49R은 G0 preflight로 두 가설을 가린다.

### N213 — 미니맵 내부는 이 환경에서 항상 검정 (보고 전용으로 강등)

미니맵 마름모 내부 (60,545)~(120,580)의 비검정 비율을 쟀다. 2026-09-17·09-20의 정상 로비 시작 캡처를 포함한 **모든** 대조 파일에서 0.0이다(probe A3, 추가로 `*minimap*` 6장도 0.0). 미니맵 내용 미표시는 W49만의 문제가 아니라 이 환경에서 공통이다. 원인은 미확인(렌더 경로 또는 탐색 상태)이다. 그래서 W49R에서 미니맵 **내용**은 합격 조건이 아니다. 실제 미니맵 입력 receipt와 서로 다른 이미지만 요구하고, 내용 비율은 보고만 한다. 제출문에는 “미니맵 내용 미검증(환경 공통, N213)”으로 적는다.

## 3. 결정 = (B)

- **(A)를 고르지 않는 이유.** (1) APPROVALS 제출 양식과 PROMPT ⑥이 기준·후보 캡처를 요구한다. 지금 제출하면 lap567 제출문 §4-7 “화면 증거 없음”이 그대로 남는다. (2) 결함은 runner의 카메라 입력 누락이다. N212 양성 대조로 렌더·캡처가 되는 환경임이 확인됐고, 수리 범위도 작다. (3) lap579~583은 게임 실행이 lap581 1회뿐이다. (B)는 다음 work가 실제 실행 증거를 늘린다.
- **lap581 “실패 시 재실행 없음”과의 관계.** 그 규칙은 같은 runner를 그대로 다시 돌리는 blind retry를 막는 것이다. W49R은 새 근거(N212/N213), 실행 전에 오프라인으로 참/거짓이 갈림을 확인한 판정식(N208 재발 방지), 카메라 receipt를 갖춘 새 카드다. 같은 추측을 반복하는 것이 아니다.
- **종료 규칙(사전 고정).** W49R은 모델 권한으로 도는 화면 축의 **마지막** 실행이다. 결과가 PASS가 아니면 원인과 무관하게 다시 돌리지 않는다. 화면을 “미검증”으로 적어 S5′를 제출한다.

## 4. W49R work 계약 (계획 회차 없이 다음 work가 착수)

### 4.1 고정 입력과 허용 변경
- 파생 원본: lap581 `temp/Syw2plus_patch/g2_capacity/20260925_lap581_w49_screen_evidence/w49_run.py` SHA `c7455e2e63d66a74638aaf3a1819fbcc3f98851e4508afedd85c01cc98b0c0f7`. 새 디렉터리 `g2_capacity/<YYYYMMDD>_lap<N>_w49r_screen_camera/`. 기존 lap581 raw는 읽기만 한다.
- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(전후 불변), 결합 후보 `dfdc91adb88a732d96dff96f78648f03406003bffce1b22a7e5836317f963883`(역적용=`a10024de…2d68`). 8 AI, map100×100, cap5000, 혼합 fixture·시딩 순서·표본 수집은 lap581과 같다. fresh prefix와 사용 중이 아닌 새 Xvfb display를 쓴다.
- **허용 diff는 다음뿐이다:** (a) `capture()`에 V1 비율·카메라 raw·local index 기록 추가. (b) local owner 카메라 맞춤 루틴. 원본 입력(X11 키/마우스, 기존 `click` 헬퍼 또는 xdotool)만 쓴다. (c) 미니맵 클릭 입력과 receipt. (d) G0 preflight gate. (e) 캡처 파일 접두사를 새 lap으로 변경.
- **금지:** 카메라·시야(fog)·렌더러 메모리 쓰기, bridge op `{5,6,7}`·goal 밖의 새 op, fixture 변경, 교전·저장/로드·재생산 명령, 새 의존성, G1 1600 후보/렌더 패치, 기존 raw 덮어쓰기, 제품 source 변경.

### 4.2 카메라·local owner 판독 (receipt 전용)
- local index는 DWORD `0x00B63FC4`다(`analysis/memory_maps/player_offsets.md` 383행 근거). `0..7`이 아니면 `RUN_ERROR(local_index)`로 멈춘다.
- 카메라 타일은 int32 `0x00B42D7C`/`0x00B42D80`이다. 결합 후보에서 이 주소가 유효한지는 G0에서 방향키 입력 전후 값이 바뀌는지로 확인한다. 바뀌지 않으면 카메라 raw는 `UNKNOWN`으로 기록한다. 이 경우에도 V1이 gate이므로 실행은 계속할 수 있다.

### 4.3 G0 preflight (같은 게임 안, PS3 직후·시딩 전, 가설 최대 2개)
1. `g0_before`를 캡처하고 V1을 기록한다.
2. **H1:** local owner의 시작 유닛(pool snapshot에서 owner=local, live) 쪽으로 방향키 폐루프 이동. 최대 300회 누름, 10회마다 카메라 raw를 읽는다. 그 뒤 `g0_h1`을 캡처한다. V1 PASS면 3으로 간다.
3. H1이 FAIL이면 **H2:** 목표 타일의 map 비례 위치로 미니맵을 클릭하고 `g0_h2`를 캡처한다. V1 PASS면 계속한다. 둘 다 FAIL이면 **`BLOCKED(capture_contract)`로 즉시 종료**한다. 시딩·10k 없음, 재시도 없음.
4. 시딩 뒤 T0 캡처 전에는 G0에서 성공한 방법으로 local owner의 시딩 anchor 군집(t0 positions의 local owner 좌표 중심)에 카메라를 다시 맞춘다. +2000·+10000 캡처 직전에도 같은 목표로 맞춘다(receipt 기록).

### 4.4 캡처 지점과 기록
- `g0_*`, `t0`, `plus2000`, `plus10000`, `minimap`(+10000 직후 실제 미니맵 클릭 입력 뒤, 다른 map 위치). 선택으로 로컬 anchor가 아닌 다른 owner 방향 1장을 추가할 수 있다(보고 전용).
- 각 캡처마다 PNG 경로·SHA·tick·owner별 `used/count`·local index·입력 receipt(키/좌표/횟수)·카메라 raw 전후·V1 비율·미니맵 내부 비율을 manifest에 기록한다. PNG는 `temp/Syw2plus_patch/captures/`에 `YYYYMMDD_HHMMSS_` 접두사로 저장한다.

### 4.5 실행 전 고정 판정식
| ID | 식 | 성격 |
|---|---|---|
| V1 | `t0`·`plus2000`·`plus10000` 각각 월드 영역 (0,30)~(800,470)에서 `max(R,G,B)>24` 픽셀 비율 ≥ **0.30** | gate |
| V2 | `t0`·`plus2000`·`plus10000`·`minimap` SHA가 서로 모두 다름 | gate |
| V3 | `minimap` 캡처 직전에 실제 미니맵 클릭 receipt가 있고, 카메라 raw가 바뀌었거나(주소 유효 시) 이미지가 `plus10000`과 다름 | gate |
| V4 | 미니맵 내부 비율(N213), T0 월드에 시딩 유닛이 보이는지 | 보고 전용(사람 판정) |
| R | tick≥10000, tick 역행0, live-count 불일치0, T0 `used` 8/8 ∈[4900,5000], over-cap0, used 음수0, VM 증가 보고 | gate |

라벨: `W49R_SCREEN_PASS`(V1·V2·V3·R 모두 PASS) / `BLOCKED(capture_contract)`(G0 실패 또는 이후 V1·V2·V3 실패) / `RAW_FAIL`(R 실패) / `RUN_ERROR`.

### 4.6 게임 전 확인 (하나라도 FAIL이면 게임 없이 `BLOCKED(gate)`)
- lap583 probe 재실행 A1·A2 true. 파생 하네스의 V1 함수를 같은 양성·음성 PNG에 적용하는 오프라인 회귀(양성 PASS·음성 FAIL). 같은 SHA 두 장을 V2가 FAIL로 잡는 합성 회귀.
- `py_compile`, 허용 op 정적 검사(`{5,6,7}`+goal만), `checks/safety.sh check`=`SAFETY_PASS`, 원본 SHA pin, 대상 display/포트 미사용 확인.
- 남은 세션 시간이 45분 미만이면 시작하지 않고 그 사실을 기록한다.

### 4.7 예산·종료
- fresh foreground 게임 정확히 1회, wall ≤45분, background 금지. 결과와 무관하게 재실행 없음. 자기 PID만 정리한다.
- 제품 source를 바꾸지 않으므로 `make check` 재실행은 선택이다(INBOX 2026-09-20 21:58 규칙). 대신 “이번 회차 제품 source 변경 없음”을 명시한다.

## 5. 그 다음 (strategy 재판정 없이 이어짐)

1. 다음 middle: summary를 쓰지 않고 PNG·manifest·samples로 V1·V2·V3·R을 다시 계산한다. PNG를 직접 보고 월드·유닛이 보이는지 기록한다. 라벨과 무관하게 추가 실행 없이 strategy로 승격한다.
2. strategy: S5′ 3단 재제출문을 쓴다. 넣을 내용: W21·W26·W45R·W46·W47, W49 raw ACCEPT, W49R 화면(PASS면 첨부, 아니면 “미검증”), S4 = W48 `UNKNOWN(harness_contract)` + N211 환경 blocker ACCEPT + 대안 (i)~(iv), N213, 제외 항목(교전·사망·재생산, N141).
3. 사용자 전권 유지: Q7-B 3단 판정, “8인”이 사람인지 AI인지, (ㄴ) AI 변경 예외, Q10 `(다)` 번복, S4 대안 (i)~(iv).
