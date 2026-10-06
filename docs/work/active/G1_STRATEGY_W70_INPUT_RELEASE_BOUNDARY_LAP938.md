# G1 W70 입력 캡처 — release 경계를 게임 프로세스 안 WM_LBUTTONUP 행으로 (lap938 strategy, 2026-10-04)

- 발행: lap938 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, 자동 폴백 아님).
  게임 실행0, 제품/하네스/test/validator source·binary 변경0, subagent0, 커밋0.
- 호출 사유: lap937 ordinary middle의 `HOLD_POST_RELEASE_PRESENT_UNPROVEN` 승격(`loop/ESCALATE_SOL`, 보존본
  `docs/history/20261004_lap938_prior_lap937_escalate_sol_byte_exact.txt`, SHA256 `67dd81b0…7e50`)과 13:30 운영자 메모
  (strategy가 caller/binding 결함과 반례만 좁게 확인하고 work 최소수리 계약을 확정해 바로 넘긴다).
- 입력 근거(이 세션이 직접 읽고 다시 센 것): 현재 `tools/g1_saved_scene_probe.py`(SHA `28ef2dea…3164`),
  `tests/test_g1_saved_scene_probe.py`(SHA `d7a879d2…c3d4`), `tools/x11_mouse_click.py`, `tools/inmm_stub/direct_draw_trace.c`,
  `tools/inmm_stub/g1_mirror2x.c`, lap936 r3 산출물 73개, 그리고 lap936·937이 읽지 않은 같은 실행의
  `local/runtime/lap936_input_pair_r3/candidate/20261004_130230_2981400_0/prefix/drive_c/inmm_g1_input_trace.jsonl`
  (512행, SHA256 `e639b5257c73f8e5069702c604a23208fe2e7c43f4a3ae64c6128f5ec2d4fc64`).
  재계산은 공유 temp `20261004_lap938_strategy_review/`(`recount.py`, `recalculation.json` SHA `a4b49c27…3163`, 입력 81개 변화0).
- 이 카드는 lap937 인계(`G1_MIDDLE_W70_INPUT_CAPTURE_BOUNDARY_HOLD_LAP937.md`)의 **1번(경계)을 바꾼다.** 2·3번은 그대로 쓴다.

## 0. 판정 요약

1. **lap937이 짚은 source 결함 두 건은 사실이다.** `g1_saved_scene_probe.py:3484~3488`이 드래그 주입 **전**의 마지막 present seq를 구하고
   3491이 그것을 "release 뒤 present" helper(2227)의 `after_seq`로 넘긴다. 3516의 candidate binding `PASS`는
   `post_input_presents.status`를 보지 않는다(3510~3514의 네 조건뿐). 정착 선택과 캡처 전 선택이 같은지도 보지 않는다.
2. **lap936의 "button-up 뒤 primary present 2건(seq1052/1056)"은 미입증이 아니라 반증이다.** 후보 DLL은 게임 창 WndProc이 받은 마우스 버튼
   메시지를 따로 기록한다(`g1_mirror2x.c:455~471` → `direct_draw_trace.c:444~468`). 드래그의 `WM_LBUTTONUP`은 `ts_ms 2460854538`에 왔고
   두 present는 `2460854450`·`2460854499`다. **88ms·39ms 전이다.** 둘 다 같은 pid 276·같은 thread 280·같은 `GetTickCount`라 순서는 확정이다.
3. **gate는 아무것도 기다리지 않았다.** helper `elapsed`가 0.0107초다. 첫 읽기에 `seq > 1028`인 present가 이미 7개 있었고(1032~1056)
   그중 마지막 둘을 돌려줬다. 7개 전부 release 전이다(§1 표).
4. **캡처 자체는 release 뒤다.** release 뒤 present 5개(seq1060~1076)가 캡처 시작 하한보다 앞에 있다(§1.3, 대조 재계산).
   그래서 lap937이 수용한 선택 의미(선택151·빈0·drag `[124,140,151,170]`·캡처 전후 동일)는 그대로 둔다.
   r3 raw의 binding `PASS` 기록은 수용하지 않는다. raw는 고치지 않는다.
5. **lap937 인계 1번(주입이 끝난 뒤 호스트가 읽은 seq를 경계로)만으로는 구조상 증명이 안 된다.** 호스트의 XTest button-up과 게임의 수신 사이에
   지연이 있다. r3에서 helper가 trace를 읽은 시점은 present 1056(…499)과 1060(…559) 사이이고 게임 수신은 …538이라, 호스트가 주입 반환을
   확인한 때 게임이 아직 release를 못 받았을 수 있다. 정확한 경계(게임이 받은 `WM_LBUTTONUP` 행)가 **이미 기록되고 있으므로** 그것을 쓴다. DLL 변경 없음.
6. 다음 work 1 lap = **입력 경계 수리 + fresh unscrolled pair**(§2~§4). 이어서 기존 minimap 유효좌표 pair(§6). **G1 계속.**

## 1. 근거

### 1.1 드래그 구간의 present와 버튼 메시지 (r3 candidate, 같은 프로세스 시계)

| 행 | seq | ts_ms(끝 6자리) | release 대비 |
|---|---|---|---|
| 드래그 전 마지막 present (`after_seq`) | 1028 | — | — |
| `WM_LBUTTONDOWN` logical `[100,40]` (input seq 41) | — | 854263 | −275 ms |
| present | 1032 / 1036 | 854185 / 854248 | −353 / −290 |
| present | 1040 / 1044 / 1048 | 854285 / 854348 / 854382 | −253 / −190 / −156 |
| present (**gate가 고른 둘**) | **1052 / 1056** | **854450 / 854499** | **−88 / −39** |
| `WM_LBUTTONUP` logical `[400,220]` (input seq 47) | — | **854538** | 0 |
| present (release 뒤 첫 둘) | 1060 / 1064 | 854559 / 854603 | +21 / +65 |
| present | 1068 / 1072 / 1076 | 854653 / 854702 / 854752 | +115 / +164 / +214 |

- 버튼 down→up 사이 present 5개, release와 ts가 같은 present 0개. 드래그 구간의 WndProc 버튼 행은 down 1·up 1뿐이다.
- present 행은 `WriteFile` 뒤 `FlushFileBuffers`로 한 줄씩 쓴다(`direct_draw_trace.c:427~433`). input trace도 같다(465~467).
- candidate trace 사본과 prefix 원본은 같은 SHA `81f7e8b7…17a6`이다.

### 1.2 gate가 실제로 한 일

- `after_seq 1028`은 주입 전 값이다. 주입은 322.28ms 걸렸고(이동 뒤 50ms + hold 150ms + 12 step × 10ms), 그동안 present가 약 50ms마다 나왔다.
- helper는 주입 반환 뒤 불렸고 10.7ms 만에 `PASS`를 돌려줬다. 고른 행은 `matching[-2:]`, 곧 그 시점 trace의 마지막 두 present다.
- 기존 회귀 `test_post_input_capture_barrier_requires_fresh_primary_presents`는 `after_seq=10`·행 11/12로 `PASS`만 확인한다. 경계가 어디서 오는지는 보지 않는다.

### 1.3 캡처 시점 (대조값, gate 아님)

- 정착 대기(`drag_wait`)는 helper 반환 뒤에 시작해 300.6ms 걸렸다. helper가 본 마지막 행이 …499이므로 캡처 시작은 **…798 이후**다
  (같은 0.3초 동안 두 시계가 같은 속도로 간다는 가정뿐, epoch 가정 없음). release 뒤이고 …798 이전인 present는 1060·1064·1068·1072·1076 **5개**다.
- 대조: 캡처 파일 이름의 epoch ns를 `CLOCK_MONOTONIC_RAW`로 옮기면 …785.7(release +247.7ms)이고 같은 5개가 나온다.
  이 호스트의 Wine `GetTickCount`는 RAW를 따른다(보정된 MONOTONIC으로 옮기면 78초 어긋나 프로그램 순서와 안 맞는다). 30분 드리프트는 재지 않았다.
- candidate `drag.png`를 직접 봤다. 드래그 사각형 없음, 상단 유닛 네 기에 선택 표시, 구도 정상. 같은 프레임 동일성은 주장하지 않는다.

### 1.4 baseline lane

- baseline은 미러 hook이 없어 input trace 파일이 없고(`baseline_input_trace_exists=false`) frame 단위 present 행도 없다(`blt` 15행).
  `NOT_INSTRUMENTED` / `PASS_WITH_LIMITS`는 사실 그대로다. 이번 수리로 baseline에 관측 장치를 더하지 않는다.

## 2. 수리 계약 (work, `tools/g1_saved_scene_probe.py`와 그 test만)

- **R1 경계 읽기(candidate만).** 드래그 `_inject` 전에 input trace(`input_trace_path`, 2607행에서 이미 정의)의 마지막 `g1-input-trace-v1` seq를 적는다.
  `_inject` 반환 뒤 (a) 그 시점의 마지막 primary present seq를 `host_return_present_seq`로 적고, (b) release 행을 기다린다:
  `kind == "WndProc"`, `message == 0x202`, `seq >` 주입 전 input seq, `logical == DRAG_TO`. 같은 구간에 `0x201`·`logical == DRAG_FROM` 행이 정확히 하나 앞서고
  release 행도 정확히 하나여야 한다. 없거나 둘 이상이거나 좌표가 다르면 `UNKNOWN`(사유 기록)이다.
- **R2 fresh present.** `_primary_present_records(candidate=True)` 중 **`ts_ms > release.ts_ms`(같으면 제외)이고 `seq > host_return_present_seq`**인 행이
  2개 모이면 `PASS`이고 **앞에서부터 두 행**을 기록한다(지금처럼 마지막 둘이 아니다). timeout이면 `UNKNOWN`.
  기록 필드: release 행(seq·ts_ms·thread_id·logical), 주입 전 present seq, `host_return_present_seq`, 두 present(seq·ts_ms·thread_id), 첫 행의 release 대비 ms, elapsed.
  `GetTickCount`가 돌아 넘어가면(부팅 49.7일, 지금 28.5일) 조건을 만족하는 행이 없어 `UNKNOWN`이 된다. 따로 처리하지 않는다.
- **R3 binding.** candidate `PASS` = button-up 전달 ∧ `post_input_presents.status == "PASS"` ∧ 정착 `PASS`·stable ≥ 2 ∧
  **정착 선택 == 캡처 전 선택 == 캡처 후 선택**. 하나라도 아니면 `HOLD`. baseline은 present 조건만 빼고 같은 식으로 `PASS_WITH_LIMITS`/`HOLD`.
  gate → 정착 → 캡처 순서는 지금 그대로다. 판정식은 테스트할 수 있게 작은 순수 함수로 꺼내도 된다.
- **R4 전파.** `_compare_input_effects`에 check `drag_capture_binding`을 더한다: candidate `PASS`이고 baseline이 `PASS` 또는 `PASS_WITH_LIMITS`일 때만 true.
  `drag_exact`(선택 ID 의미)는 그대로 따로 둔다. `_pair_status`는 바꾸지 않는다 — 스크롤 pair의 기존 수용 의미가 달라지기 때문이다.
- **R5 보존.** candidate input trace를 `trace_raw.jsonl` 옆에 복사하고 경로·SHA256을 결과에 적는다. r3에서는 prefix 안에만 남아 있었고 prefix는 보관 압축 대상이다.
- 바꾸지 않는 것: DLL, `x11_mouse_click.py`, 게임 로직, validator, 임계값, 기대 선택 ID, 주입 timing, baseline 계측.

## 3. 회귀 (RED 먼저, `tests/test_g1_saved_scene_probe.py`)

1. r3 수치 재현: present seq 1032~1064(§1.1의 ts), release ts 854538, 주입 전 seq 1028, host 반환 seq 1056 → 기록 행이 `[1060, 1064]`.
   1056까지만 있는 trace면 `UNKNOWN`. **지금 코드는 `[1052, 1056]`으로 `PASS`한다(RED).**
2. release 행 없음 / 둘 / `logical` 불일치 / down 행 없음 → `UNKNOWN`.
3. `ts_ms == release.ts_ms`인 present는 세지 않는다.
4. `ts_ms`는 크지만 `seq ≤ host_return_present_seq`인 present는 세지 않는다.
5. binding: gate `UNKNOWN` → `HOLD`. **지금 코드는 `PASS`(RED).**
6. binding: 정착 ≠ 캡처 전, 또는 캡처 전 ≠ 캡처 후 → `HOLD`(두 lane). 정상 baseline → `PASS_WITH_LIMITS`.
7. `_compare_input_effects`: candidate binding `HOLD` → `drag_capture_binding` false·전체 `HOLD`, `drag_exact`는 true 유지.

fixture는 위 숫자로 만든 작은 합성 행이다. r3 raw 파일을 저장소에 복사하지 않는다.

## 4. fresh pair와 사전 등록 예측

lap936 r3와 같은 구성(save006, `--hd-source scale2x`, `--terrain-scroll`·snapshot·performance 없음, 카메라 `[158,101]`)으로 새 private runtime/artifact root에서
original/candidate pair를 끝까지 돌린다. 실행 전 여유 20GiB 확인, 끝나면 이 회차의 game 사본만 지운다.

- **P-1** candidate release 행 정확히 1개, `logical [400,220]`, down→up 250~300ms(r3 275ms).
- **P-2** gate `PASS`. 두 행 모두 `ts_ms > release.ts_ms`. 첫 행 여유 1~70ms(r3 재계산 +21ms), 두 행 간격 30~70ms(r3 present 간격 32~69ms).
- **P-3** `주입 전 seq < host_return_present_seq < 첫 fresh seq`.
- **P-4** 두 lane 선택151·빈0·drag `[124,140,151,170]`, 정착 == 캡처 전 == 캡처 후. candidate binding `PASS`, baseline `PASS_WITH_LIMITS`.
- **P-5** drag PNG 두 장에 드래그 사각형 없음(middle이 직접 본다). V1 위반0·V2/V2s/V2q·활성 Scale2x는 r3와 같이 `PASS`.
- **P-6** present thread == WndProc thread(r3 280/280). 기록만 하고 gate로 쓰지 않는다.

P-1이 깨지면(선택은 바뀌는데 release 행이 없다) 이 경계는 못 쓴다 — §7 재호출 조건이다. 나머지가 깨지면 귀속 가능한 하네스 결함이므로
같은 회차에서 고쳐 다시 돌린다(PROMPT ③, 3회까지).

## 5. 2단 수용 조건 (다음 middle)

- §3 회귀가 수리 전 RED·수리 뒤 PASS였다는 기록, 현재 source·build 입력·DLL·원본 EXE·save006 SHA 대조.
- fresh raw를 다른 스크립트로 다시 세어 **gate가 기록한 두 present의 ts가 보존된 input trace의 release 행보다 크다**는 것과 P-1~P-6 확인.
- drag PNG 직접 확인. r3 raw·lap936/937 기록은 그대로 두고, lap936의 "button-up 뒤 2건" 문장은 이 카드 §0.2로 정정됐다고만 적는다.
- 이것은 입력 캡처 binding의 부분 수용이다. minimap·production·GDI·두 번째 장면·전체 HD 계약·G1 사용자 승인은 그대로 남는다.

## 6. 이어지는 일 — minimap 유효좌표 pair (이미 인계된 작업)

- r3 사실: 두 lane 모두 gate `00000000 → 01000000 → 00000000` 복원, `(182,548)` 클릭은 게임에 도달했고(input seq 61/64, logical `[182,548]`)
  카메라는 `[158,101]` 그대로다. 원본도 같으므로 2배 경로의 회귀 증거는 아니다.
- 가설(실행 미검증): `(182,548)`은 candidate PNG에서 미니맵 마름모의 오른쪽 꼭짓점 근처(물리 `(364,1096)`)라 hit-test 밖일 수 있다.
  새 좌표를 추측하지 말고 G5 lap764·768이 원본에서 실제로 통과시킨 미니맵 클릭 조건(진단 gate + 그 probe의 좌표)을 그대로 가져와 두 lane에 같이 쓴다.
- §4가 한 번에 GREEN이고 시간이 남으면 같은 work 회차에서 이어서 해도 된다. 아니면 다음 work다. production은 minimap이 실제로 카메라를 옮긴 장면에서 본다.

## 7. 하지 않는 것 / strategy 재호출 조건

- 하지 않는 것: 새 관측 장치·새 gate, baseline 계측 추가, 임계값·기대 ID·validator 변경, 과거 raw 수정, r3 binding을 사후에 `PASS`로 읽기,
  G2/G5/G3/G4 재개, 커밋.
- strategy를 다시 부르는 조건은 둘뿐이다: (a) fresh candidate 실행에서 선택은 바뀌는데 WndProc release 행이 없다, (b) 새 안전 위험.
  gate `PASS`인데 drag PNG에 사각형이 남는 경우를 포함한 나머지 HOLD·수리는 work ↔ middle로 처리한다. lap933 카드 §6 조건은 그대로 유효하다.
- lap937·938은 제품·실행 증거가 늘지 않은 연속 2회다. 다음은 반드시 work다.
