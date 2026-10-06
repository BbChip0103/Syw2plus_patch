# G1 W70 P5-T-R — observation tick 경계 확정과 P5-T 스크롤 뒤 재호출 비용 (lap925 strategy, 2026-10-04)

- 발행: lap925 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, 자동 폴백 아님).
  게임 실행0, 제품/하네스/validator source·binary 변경0, subagent0, 커밋0.
- 호출 사유: lap924 middle의 `HOLD_OBSERVATION_WINDOW_CONFLICT` 승격(`loop/ESCALATE_SOL`, 보존본
  `docs/history/20261004_lap925_prior_lap924_escalate_sol_archive.md`)과 07:14 운영자 연결 지시(충돌 근거 확인·최소 경계 수리 확정).
- 입력 근거(이 세션이 직접 읽고 재계산): lap923 final GREEN/B′1/B′2 pair·trace·snapshot 12개, lap923 C1·C2, lap907 pair 2개,
  lap915 pair 3개, lap920 pair 3개·C1의 trace, 현재 `tools/g1_saved_scene_probe.py`(SHA `15b0e0f7…9434`),
  `tools/inmm_stub/direct_draw_trace.c`(SHA `20b86b25…b1f5`), `g1_state_snapshot.c`(SHA `6f40eee0…7658`).
  재계산은 공유 temp `20261004_lap925_strategy_review/`.
- 이 카드는 lap924 handoff(`G1_MIDDLE_W70_P5T_OBSERVATION_WINDOW_HOLD_LAP924.md`)를 **흡수한다.** 겹치는 항목은 이 카드가 우선한다.
  lap911 카드 §2·§5(P5-H → P5-T 범위)와 lap918 handoff §4(관측 연장 금지)는 그대로다.

## 0. 판정 요약

1. **충돌은 사실이다.** lap923 B′1이 30개로 센 표본 중 DOWN 4개·RIGHT 12개는 observation snapshot 뒤에 만들어진 present다.
   두 시계의 epoch를 가정하지 않는 상한으로도 그렇다. lap923 B′1의 raw PASS는 수용하지 않는다(GREEN·B′2는 30개 전부 경계 안).
   "B′ 연속 2회"는 미충족, **P5-T HOLD·G1 HOLD 유지.** 기존 raw는 고치지 않는다.
2. **경계는 sim tick으로 센다.** 표본은 카메라 전환 뒤 present 중 `sim_tick ≤ observation tick`인 것만이다.
   30개·tick 일정(+36)·264000·key-before×0.9·층 조건은 그대로다. lap918의 "observation tick 뒤의 표본"을 글자 그대로 옮긴 것이다.
3. **기존 필드로는 이 경계를 정확히 못 긋는다**(§1.3). 그래서 `mirror2x_present` 행에 `sim_tick` 한 필드를 더한다(§2 O1). 그 외 계측 추가는 없다.
4. **새로 확인한 것: P5-T는 스크롤 뒤 present가 느려졌다.** 전환 뒤 30 present의 간격이 P4c-W·P5-H 16회 전부 48.97~49.83ms였는데
   P5-T는 깨끗한 실행에서도 56.0~58.5ms다. 그래서 36 tick 창에 들어가는 present가 35~36개에서 30~31개로 줄었고, gate 여유가 0~1개다.
   B′1의 26/18은 여기에 유지보수 I/O 정지(간격 최대 713ms)가 겹친 결과다. 하네스만 고치면 같은 HOLD가 다시 난다.
5. 다음 work 1 lap = **P5-T-R**: 경계 수리(R1) → fresh GREEN으로 수치 확인(R2) → 스크롤 뒤 비용 수리(R3) → GREEN→B′ 연속 2→C 3(R4) → Fast → 새 middle.
6. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 검수·3단 사용자 승인은 그대로 남는다.

## 1. 근거

### 1.1 경계 뒤 표본 (lap923 final, candidate lane)

| 실행 | 키 | 창(ms, QPC) | 경계 안 | 확실히 뒤 | 30번째 − 경계 |
|---|---|---|---|---|---|
| GREEN | DOWN / RIGHT | 1821.9 / 1789.6 | 30 / 30 | 0 / 0 | −47.5 / −50.4 ms |
| B′1 | DOWN / RIGHT | 1794.5 / **3053.3** | **26 / 18** | **4 / 12** | +329.4 / +724.2 ms |
| B′2 | DOWN / RIGHT | 1818.3 / 1784.3 | 30 / 30 | 0 / 0 | −113.0 / −51.3 ms |

- "확실히 뒤"는 `ts_ms > keydown 수신 ts_ms + (observation QPC − input QPC)/10000 + 16`인 표본이다. 입력 tick의 update가 끝난 뒤에야
  창 스레드가 WM_KEYDOWN을 받으므로 이 값은 경계의 상한이고, 두 시계의 epoch가 같다는 가정이 필요 없다. lap924의 4/12·311.5/699.7ms와 같다.
- "경계 안"은 `ts_ms ≤ QPC/10000`(같은 epoch 전제)이다. B′1 DOWN의 26번째는 경계 8.6ms 앞이라 16ms 여유를 두면 25개다. 어느 쪽이든 30 미만이다.
- 30개 값·p50(406778/395928, 406739/395963, 406778/395924)·trace·snapshot SHA는 기록과 일치한다. 표본과 snapshot은 전부 같은 스레드다.
- B′1 RIGHT는 36 tick에 3053ms가 걸렸다(정상 1784~1822ms). present 간격 최대 713ms — 프로세스가 멈췄다 따라잡은 것이다.

### 1.2 시계

- trace `ts_ms`는 `GetTickCount()`(`direct_draw_trace.c:520`), snapshot은 `QueryPerformanceCounter`(`g1_state_snapshot.c:202`, 10MHz는 lap924 확인).
- `ts_ms` 분해능은 1ms다(연속 present 간격의 최빈값 47~53ms가 고르게 나온다).
- keydown 수신 − input snapshot은 6회 모두 15.4~24.4ms다. 두 시계가 같은 epoch라는 것과 맞지만, 한쪽으로만 묶이는 증거다(§1.3).
- trace 행은 줄마다 `WriteFile` + `FlushFileBuffers`로 쓴다(`direct_draw_trace.c:431~432`). present와 snapshot이 같은 스레드이므로,
  snapshot 파일이 보이면 경계 앞 행은 이미 전부 파일에 있다. "늦게 flush된 경계 앞 표본"은 host가 파일을 늦게 보는 경우뿐이다.

### 1.3 기존 필드로 안 되는 이유

- 경계 시각은 QPC에만, present 시각은 GetTickCount에만 있다. epoch 가정 없이 얻는 것은 경계의 **상한**뿐이라 "뒤"는 증명되지만 "안"은 증명되지 않는다.
- 파일 순서로도 못 가른다. host가 snapshot을 읽는 동안(파일 대기 + 2.3MB 읽기 + live 읽기) 경계 뒤 행이 먼저 들어온다.
- lap918 규범의 단위는 tick인데 present 행에 sim tick이 없다(`game_tick`은 `0x9B5210`의 ms 값이다).
- 지금까지의 30/30 PASS도 "snapshot 읽기가 끝난 시점에 파일에 있던 행"으로 센 것이라 경계 뒤 present 한두 개가 섞일 수 있었다.
  P4c-W·P5-H는 여유가 5~6개라 판정에 영향이 없다(§1.4). 그 판정들은 다시 열지 않는다.

### 1.4 스크롤 뒤 present 간격 (전환 뒤 30 present, candidate lane)

| 단계 | 실행 | ms/present | 창 안 present | 재호출 시간/present |
|---|---|---|---|---|
| P4c-W lap907 | pair1·pair2 | 49.07~49.76 | 35~36 | — |
| P5-H lap915 | pair2·B′1·B′2 | 48.97~49.83 | (snapshot 없음) | — |
| P5-H lap920 | GREEN·B′1·B′2 | 49.24~49.66 | (snapshot 없음) | GREEN·B′2: 고정 4.0~4.9, DOWN 뒤 4.0~6.1, RIGHT 뒤 10.6~12.7ms |
| **P5-T lap923** | GREEN·B′2 | **56.0~58.5** | **30~31** | 고정 6.3~6.8, DOWN 뒤 **26.1~27.1**, RIGHT 뒤 **26.1~27.5ms** |
| P5-T lap923 | B′1 | 70.0 / 126.6 | 26 / 18 | (I/O 정지 겹침) |

- 재호출 시간은 `primitive_reinvoke_elapsed_ms_total`의 present당 증가분이다. present 호출 자체(`elapsed_ms` 중앙값 5~9ms)는 그대로다.
- 고정 카메라 간격은 P5-T도 50.3ms다. DOWN 뒤에는 80 present가 지나도 53.7~61.5ms다(10개 묶음 평균). RIGHT 뒤는 60.6ms에서 50.3ms까지 내려오고,
  GREEN의 실행 끝 25 present(같은 카메라)는 50.0ms·재호출 1~16ms다.
- 스크롤이 없는 C1·C2에서도 재호출 시간이 4~9ms에서 13~19ms로 올라 끝까지 유지된다(40 present 묶음, P5-H C1은 2.9~6.1ms). 50ms 안에 들어가 tick ratio·p95에는 안 보였다.
- 파일 시각으로 C1~C3(06:30~06:35 종료)과 GREEN(06:39:08 종료)은 prefix 보관 작업(06:39:48 시작, 06:40~ 쓰기) 전에 끝났고 B′1(06:41:59 종료)이 겹쳤다.
  재호출 시간은 GREEN과 B′2가 같으므로 느려짐 자체는 I/O 탓이 아니다.
- lap923 work의 첫 시도 26/30·29/30과 "snapshot 뒤 최대 8초 대기" 수리는 이 느려짐을 flush 지연으로 읽은 것이다.

### 1.5 단서 (원인 미확정, R3의 출발점)

- L1: tinted 호출이 거의 전부 매 프레임 identity cache miss다. miss/present가 59.1(P5-H) → 145.8(P5-T), 차이 86.7 대 tinted 호출 94.7(79.4 + 15.3).
- L2: `tinted_clip`은 호출마다 clip replay mismatch로 끝난다. mismatch/present 59.0 → 74.3, 차이 15.3 = `tinted_clip` 호출 15.3.
  DOWN 뒤 13.2 대 13.3, RIGHT 뒤 13.7 대 13.9. lap923의 `rle_tinted_clip covered 0`과 같은 사실이다.
- L3: 호출 수는 스크롤 전후로 비슷한데(179.6 → 198.1/166.4) 시간만 4배다. 무엇이 호출당 비용을 올리는지는 counter로는 안 보인다.

### 1.6 한계

- "창 안 present"의 tick 기준 값(§2)은 추정이다(경계 + 창/36): 깨끗한 4회 31/31/32/31, B′1 26/19. 실측은 O1 뒤에 나온다.
- lap915·lap920은 snapshot bin을 지금 읽을 수 없어(prefix 보관) 간격만 trace로 쟀다. 재호출 시간은 lap920 GREEN·B′2·C1, lap923 GREEN·B′2·C1·C2만 쟀다.
- epoch가 같다는 것은 Wine 구현과 6회 관측에 기대는 전제다. 그래서 판정에는 쓰지 않고 대조값으로만 남긴다(O5).
- 느려진 원인과 C 창에서 재호출 시간이 오르는 계기는 모른다.

## 2. 경계 계약 (규범)

- **O1 (DLL, 한 필드):** `mirror2x_present` 행의 `camera`를 붙이는 자리(`direct_draw_trace.c:1676~1677`, `scroll_trace_enabled()`일 때만)에
  `"sim_tick":<0x008924B8의 DWORD>`를 같이 쓴다. 읽기는 기존 `read_state`를 쓴다. R1에서 DLL의 다른 곳은 건드리지 않는다.
- **O2 (표본):** `_terrain_scroll_coverage`가 `observation_tick`을 받는다. 카메라 전환 present부터 세되 `sim_tick`이 정수이고
  `≤ observation_tick`인 행만 표본이다. `sim_tick > observation_tick`인 첫 행에서 창을 닫는다(`boundary_reached`).
  전환 뒤 행에 `sim_tick`이 없으면 `INVALID`다. 시계 비교로 대신하지 않는다.
- **O3 (대기):** `_wait_for_terrain_scroll_coverage`는 표본 30개가 찼거나 창이 닫히면 바로 돌아온다. 최대 8초 polling은 경계 앞 행이
  파일에 보이기를 기다리는 용도뿐이다. 창이 안 닫힌 채 시간이 다 되면 `INCOMPLETE`(사유 기록)다.
- **O4 (판정):** 경계 안 표본이 30개 미만이면 `INCOMPLETE` → `scroll_gate` HOLD → pair PASS 불가. 다시 돌려 30개가 나온 실행만 골라 쓰지 않는다.
  모든 시도를 남기고, "B′ 연속 2회"는 연속으로 센다.
- **O5 (raw):** `observation_tick`, 경계 안 개수, `boundary_reached`, 마지막 경계 안 `seq`, 첫 경계 뒤 `seq`·`sim_tick`, 표본별 `sim_tick`을 남긴다.
  대조값으로 `ts_ms ≤ observation QPC/10000`인 개수를 같이 남긴다(판정에 쓰지 않는다).
- **O6:** `terrain_redraw` 경로(`g1_saved_scene_probe.py:3011`)는 observation tick이 없는 진단이다. 동작을 바꾸지 않는다.
- **O7:** lap923의 "정확한 input tick 전에 진단 읽기·arm을 끝낸다" 수리는 보존한다.
- 불변: tick 일정, 30개, 임계값, validator, 기존 raw·golden·안전 pin, 원본. observation tick과 같은 tick의 present는 표본이다
  (update 반환 뒤 그 상태를 그린 프레임). lap924의 QPC 기준과는 깨끗한 실행에서 행 하나 이내로 다르고, B′1은 두 기준 모두 30 미만이다.

## 3. 회귀 테스트 (work, R1)

1. 경계 안 30개 → 기존과 같은 값·p50으로 PASS/FAIL.
2. B′1 형태: 경계 안 26 + 뒤 4, 경계 안 18 + 뒤 12 → `INCOMPLETE`, 개수 26/18, `boundary_reached` true, p50 없음.
3. 늦게 보이는 경계 앞 표본: 첫 읽기에는 경계 안 20개만 있고 경계 행이 없다 → 파일에 10개와 경계 행이 더 붙는다 → PASS, 표본은 전부 경계 안.
4. 경계 뒤에만 새 행이 생김: 경계 안 26개와 경계 행이 이미 보인다 → 8초를 기다리지 않고 바로 `INCOMPLETE`.
5. `sim_tick` 없는 행(기존 raw 형태) → `INVALID`, gate HOLD.
6. 경계 안이 31개 이상이어도 표본은 전환 뒤 처음 30개다.
7. DLL source가 `camera`와 같은 조건에서 `sim_tick`을 쓴다(기존 source 고정 테스트 방식).
8. coverage가 `INCOMPLETE`/`INVALID`면 pair status가 PASS가 아니다.
9. lap923의 pre-arm 순서 테스트는 그대로 통과한다.

## 4. P5-T 스크롤 뒤 비용 (R3)

- 사전 예측(R2에서 확인): **PT-a** 비용 수리 전 깨끗한 실행의 경계 안 개수는 키마다 30~32. **PT-b** 전환 뒤 30 present의 재호출 시간은 26~27ms/present.
  PT-a가 34 이상이거나 PT-b가 13ms 이하로 나오면 §1.4가 틀린 것이다 — 그 수치를 기록하고 R3을 건너뛴다.
- 수리 목표 **PT-c:** GREEN·B′1·B′2의 두 키 모두 전환 뒤 30 present 간격 ≤ 52.0ms/present. 기준선은 P4c-W·P5-H 16회의 48.97~49.83ms다.
  기존 필드(`ts_ms`)로 계산하며 새 계측이 필요 없다. P5-T의 2단 수용 조건에 넣는다 — P5-T가 스크롤 뒤 present 간격을 P5-H보다 악화시키지 않는다.
- **PT-d:** 비용을 tinted 미러를 끄는 것으로 줄이지 않는다. `rle_tinted` covered는 lap923 범위(고정 창 11,439~12,969) 이상,
  V1·V2·V2s·V2q·Scale2x PASS 유지. `tinted_clip`이 계속 covered 0이면 그 사실과 이유를 기록한다(L2).
- 방법: 구현 우선. L1·L2부터 본다. 구간이 안 갈리면 기존 opt-in perf section으로 진단 실행을 한다(진단 실행은 합격 증거가 아니다. 합격 측정은 비계측).
  수리 → GREEN 재실행을 3회까지 반복한다.
- 3회 뒤에도 PT-c 미달이면 `HOLD_P5T_SCROLL_COST`로 수치·구간 자료를 남기고 다음 work가 잇는다. strategy로 올리지 않는다(§6 제외).

## 5. 다음 work 한 가지 — P5-T-R

1. **R1** §3 테스트 RED → O1~O7 구현(`tools/inmm_stub/direct_draw_trace.c` 한 필드, `tools/g1_saved_scene_probe.py`, 관련 tests, 단일 writer)
   → focused tests·lint·typecheck·DLL build.
2. **R2** fresh GREEN 1회(현재 P5-T 논리 + `sim_tick`). 키별 경계 안 개수·간격·재호출 시간을 기록하고 PT-a·PT-b와 대조한다.
   `INCOMPLETE`면 HOLD로 남기고 R3으로 간다.
3. **R3** §4.
4. **R4** 같은 source identity로 GREEN → B′1 → B′2 → C1~C3. 기존 gate 전부(V1/V2/V2s/V2q/Scale2x, snapshot 5/5, tick·입력·카메라 parity,
   C ratio ≥ 0.95·p95Δ ≤ 16ms)와 PT-c·PT-d.
5. 실행 중에는 루프가 소유한 유지보수 I/O(보관·압축)를 겹치지 않는다. pair마다 시작 전 `/proc/loadavg`와 `/proc/pressure/io`를 lap 기록에 적는다(gate 아님).
   디스크 여유 20GiB 규칙과 실행 뒤 game 사본 삭제는 PROMPT대로다.
6. lap 기록·handoff 작성 → `make lint`·`make typecheck` → `make check` 1회 → STATUS 보강 → 새 middle 독립 검수.
   middle은 lap924가 stop으로 못 끝낸 항목(p95 histogram, 전체 V1/V2/시각, snapshot 전체 상태, stale 귀속)을 새 raw로 본다.

## 6. strategy 재호출 조건

- `sim_tick`이 snapshot tick과 어긋난다(present 행의 `sim_tick`이 감소하거나, observation snapshot이 있는데 8초 안에 그 tick 이상의 행이 없다).
- PT-c를 맞추려면 tinted 미러 범위를 줄여야 한다(P5-T 범위 변경).
- 새 안전 위험.
- 그 밖의 HOLD·수리는 work ↔ middle로 처리한다. P단계 전환은 마일스톤 경계가 아니다(lap858).

## 7. 남는 것

`rle_tinted_clip` covered 0, stale 감소 미입증, 유효 HD coverage ≈ 82.5% < 90%, input-effect HOLD, GDI, 두 번째 장면, 최종 입력, D-2 스크롤 성능,
census 계측 결함 두 건(lap913), G1 사용자 승인. G2·G5 종료, G3 중단, G4 보류, 커밋 금지는 그대로다.
