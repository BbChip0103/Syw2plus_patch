# G1 W70 P4c-W — 스크롤 뒤 우측 검은 쐐기의 귀속(캐시 scratch clear 폭 800/832)과 수리 범위 (lap906 strategy, 2026-10-03)

- 발행: lap906 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, 자동 폴백 아님).
  게임 실행0, 제품/하네스/validator source·binary 변경0, subagent0, 커밋0.
- 호출 사유: lap905 middle의 `HOLD_VISUAL_ATTRIBUTION_UNPROVEN` 승격(`loop/ESCALATE_SOL`, 보존본
  `docs/history/20261003_lap906_prior_lap905_escalate_sol_archive.md`).
- 입력 근거(이 세션이 직접 읽고 재계산): lap904 GREEN r4·B′1·B′2의 원본·후보 PNG 30장, lap901 P4c 3 pair PNG 30장,
  현재 `tools/inmm_stub/g1_mirror2x.c`(SHA `d1052973…e855`, B′1 build 사본과 `cmp` 일치)·`g1_hd_asset.c`(SHA `7833f328…eedf`)·
  `g1_scratch_bounds.h`·`g1_scale2x_core.h`, 캐시 주소 문서(lap863). 재계산은 공유 temp `20261003_lap906_strategy_review/`.
- 이 카드는 P4c 카드(lap900)·P4c-M 카드(lap903)를 **대체하지 않는다.** P4c-M §4.1의 4번(B′)·5번(C) 앞에 수리 하나를 넣고,
  gate V에 V2q를 더한다. V1·V2·V2s·V3와 기존 임계값은 한 글자도 바꾸지 않는다.

## 0. 판정 요약

1. **B′의 우측 검은 쐐기는 렌더러 결함이다.** 귀속 `RENDERER(캐시 대상 scratch clear가 폭 800에서 멈춤 → 캐시 x800..831의 묵은 A==B를
   compose가 "쓴 픽셀"로 읽음)` 확정. lap905가 "미검증 좁은 가설"로 남긴 경로를 소스 정독(§1.1)과 기존 캡처 기하(§1.2)로 확인했다.
   캡처 시점 차이·입력 발산·게임 상태 손상으로는 §1.2의 모양이 나오지 않는다(§1.3).
2. **같은-present ROI 관측 회차는 열지 않는다.** lap905의 두 선택지 중 "확정 수리 + 경계 회귀"를 고른다.
   수리한 빌드의 fresh scroll pair가 실험이며, 반증 조건과 그때 열 진단을 §4.2에 미리 적었다.
3. **수리는 한 줄기다(W1).** `mirror_reinvoke`의 scratch 사전 clear가 compose와 같은 프레임 폭을 쓰게 한다(캐시 대상 832). §2.
4. **V2는 이 결함이 있어도 PASS할 수 있다.** B′2 drag는 쐐기 2288블록이 있는 채 V2 초과 1863으로 PASS였다(§1.4).
   네 subpixel 전부 검정인 블록을 직접 세는 **V2q**를 추가한다(§3). 강화이며 기존 조건을 대체하지 않는다.
5. **다음 work 1 lap = P4c-W**: 단위 RED → W1 수리 → fresh scroll pair GREEN(=B′ 1번째) → B′ 2번째 → C 3 pair(§4).
6. lap904 GREEN의 격자 수리(mask) 수용 범위는 그대로다. lap904 B′1·B′2는 `HOLD` 그대로 두고 raw를 고치지 않는다.
7. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 검수·3단 사용자 승인은 그대로 남는다.

## 1. 근거

### 1.1 소스 경로 — 캐시 x800..831의 scratch는 한 번도 지워지지 않는다

- 지형 writer가 불릴 때 렌더러는 캐시(`0xBA3D30`, 832×512, stride 832, clip `(0,0,831,511)`)에 묶여 있다(lap863 문서 1항).
- `mirror_reinvoke`는 writer를 부르기 전에 프리미티브 영역의 scratch A를 `0x00`, B를 `0xFF`로 채운다. 그 영역은
  `g1_scratch_intersection(origin_x, origin_y, width, height, 800u, surface_height, …)`로 구한다(`g1_mirror2x.c:1024~1032`).
  **프레임 폭이 800 고정**이라 x≥800은 채우지 않는다. 이 helper는 화면 밖 프리미티브에도 TRUE(빈 영역)를 돌려주므로
  (`g1_scratch_bounds.h:11~13`) 전체를 지우는 else 분기(`:1033~1037`)도 타지 않는다. origin 768인 타일은 x768..799만,
  origin 800인 타일은 아무것도 지우지 않는다.
- 캐시 대상 compose는 `G1_CACHE_WIDTH`(832)로 영역을 구하고(`compose_cache_layer`, `:548~549`), `A==B`인 픽셀을 이번 호출이 쓴
  픽셀로 본다(`:558`). x800..831에는 앞선 타일이 써 둔 `A==B`가 남아 있으므로, 이번 타일의 마름모 **바깥** 픽셀도 쓴 픽셀로 읽힌다.
- 그 픽셀의 HD 블록은 이번 타일의 identity frame에서 가져온다. lookup은 mask를 보지 않고 블록을 돌려주고(`g1_hd_asset.c:606~614`),
  미기록 중심의 블록은 네 subpixel 모두 E, 곧 identity frame의 미기록 값 `0x00`이다(`g1_scale2x_core.h:27~43`). **네 subpixel 전부 검정.**
- 같은 자리에서 `g_layer_expected`에는 실제 캐시 값이 들어간다(`:567`). present의 값 검사는 통과하고 블록은 covered로 남는다.
  V1(present당 합계 상한)은 이 블록을 가려내지 못한다(lap905 8항과 같은 결론).
- 화면 전송은 x<800만 옮긴다(`transfer_cache_to_screen`, `:640~643`). 그래서 스크롤 전에는 보이지 않는다. 캐시가 왼쪽으로 64px 밀리면
  (`0x432BD4`, 행마다 x64..831 → x0..767, lap863 표) 미러도 HD·covered·expected를 같이 옮기고(`:574~617`), x800..831이 화면 x736..767로 들어온다.
  새로 드러난 열(x768..831)만 다시 그려지므로 x736..767은 그대로 남는다.

### 1.2 사전 예측과 실제 캡처

위 경로가 맞다면 "원본 픽셀이 검정이 아니고 후보 2×2 블록이 전부 검정"인 블록은 (a) 가로 64 이동 뒤에만, (b) 화면 x736..767에만,
(c) 타일 마름모 변의 기울기(2:1)와 32행 주기를 가진 쐐기 모양으로 나타나야 한다. 예측을 `recalculate.py` 머리에 적고 돌렸다.

월드 영역 논리 `[0,0,800,480)`. 값은 `전체 / x736..767`.

| pair | loaded | selection | drag | minimap | production |
|---|---|---|---|---|---|
| lap904 GREEN r4 (스크롤 없음) | 0 / 0 | 94 / 0 | 636 / 0 | 1348 / 0 | 825 / 0 |
| lap904 B′1 (loaded 뒤 DOWN·RIGHT) | 120 / 0 | 2434 / **2207** | 2402 / **2225** | 2708 / **2316** | 2580 / **2261** |
| lap904 B′2 (같음) | 308 / 0 | 2179 / **2164** | 2555 / **2288** | 2950 / **2370** | 2851 / **2330** |
| lap901 P4c green·green_r2·origin (스크롤 없음) | 43~381 / 0 | 107~593 / 0 | 670~815 / 0 | 663~1361 / 0 | 826~886 / 0 |

- (a)(b): 가로 이동이 없는 캡처 22장(스크롤 없는 4 pair×5 tag + B′ loaded 2장)은 x736..767이 **전부 0**이다. RIGHT 뒤 캡처 8장은 2164~2370이다.
  바로 옆 x768..799는 0~64, x720..735는 0~65다. 띠의 왼쪽 끝은 정확히 x=736(=800−64)이다.
- (c): B′2 selection의 띠 2164블록은 전부 `y mod 32 ∈ [16,31]`에 있고 행별 수는 `206,208,213,209,202,191,178,169,147,125,99,82,62,41,24,8`이다.
  B′1은 2207 중 2194가 같은 구간이고 분포도 같다(`206,208,215,210,204,…,8`). 한 쐐기 안에서 행 폭은 x=736에 붙은 채 한 행에 2px씩 줄어든다
  (y=82..95: `22,22,23,21,19,17,15,13,11,9,7,5,3,1`).
- lap905의 "우측 80px 2225/2164"는 위 표의 x720..799 합과 같다(B′1 2207+18, B′2 2164+0).
- 스크롤 없는 캡처의 전체 값 0~1361은 띠와 무관한 자리에 있다(유닛·효과의 캡처 시점 차이로 보이나 분리하지 않았다).

### 1.3 다른 설명의 배제

- 캡처 시점·입력 차이: 두 pair에서 행별 분포가 거의 같은 결정적 모양이고, 왼쪽 끝이 캐시 폭 상수(800−64)에 붙어 있다. 시점 차이는 이런 모양을 만들지 않는다.
- 게임 상태 손상: 원본 쪽 캡처의 같은 자리는 정상 지형이고, 5개 snapshot 전 필드가 두 lane에서 같다(lap905 3항).
- 스크롤 뒤 다시 그린 열의 결함: 그렇다면 x768..799에 나와야 한다. 그 구간은 0~64다.
- 미러의 이동(move) 결함: 이동은 행의 연속 구간을 그대로 옮긴다. 쐐기 모양은 이동 전부터 x800..831에 있어야 설명된다.

### 1.4 V2의 공백(두 번째)

- B′2 drag: 원본 쪽 검정 변동 때문에 V2 초과가 1863으로 PASS였다. 같은 캡처의 띠는 2288블록이다. V2s(블록당 1개)는 이 결함을 세지 않는다(97~131).
- V2는 대면적 결손 경보선으로 그대로 둔다. 네 개 전부 검정인 블록은 V2q가 직접 센다.

### 1.5 한계

- 프로세스 안에서 해당 호출의 scratch·mask·HD 블록을 직접 본 것은 아니다. 소스 정독과 캡처 기하의 일치로 판정했다. 고친 빌드는 아직 없다.
- 쐐기가 32행 주기의 아래 절반에만 생기는 이유(타일 그리기 순서와 마지막 writer)와 블록 수 2164~2370의 정확한 모형은 유도하지 않았다.
- lap854 P3c gate 폴더에는 `pair-result.json`이 없어 이 계산에 넣지 않았다.

## 2. 수리 규칙 (규범)

- **W1. scratch 사전 clear와 compose는 같은 프레임 크기를 쓴다.** 렌더러가 캐시에 묶인 호출(`expected == G1_CACHE_BASE`)은
  `G1_CACHE_WIDTH × surface_height`, 그 밖은 지금처럼 `800 × surface_height`다. 두 곳(`:1024~1025`, 성능 계수 `:1040~1041`)과 compose 호출이
  **한 정의**에서 폭을 받게 해서 다시 갈라지지 않게 한다. 방법(helper·지역 변수)은 work가 정한다.
- **W2. 불변식(회귀 테스트로 고정).** writer를 부르기 직전, `프리미티브 영역 ∩ compose 프레임`의 모든 scratch 픽셀은 `A=0x00, B=0xFF`다.
  화면 대상(폭 800) 동작은 수리 전과 같다.
- **이번 수리에 넣지 않는 것(같은 계열, 기록만).** ① 비클립 bind 조건 `origin_x <= 800u − width`(`:1141`): 캐시 x768..831에 걸친 타일은 직접 bind하지
  못한다. ② `compare_visible_frame`·`verify_unclipped_frame_in_viewport`의 800/600 상한(`g1_hd_asset.c:463~468, 349~350`): 캐시 x≥800은 검증 없이 지나간다.
  ③ lookup이 mask 미기록 자리에도 블록을 돌려주는 것. 셋 다 정독으로는 검정을 만들지 않고(①② bind/검증 범위, ③ W1 뒤에는 닿지 않음)
  coverage·방어 항목이다. D-1/coverage 단계에서 본다. W1만으로 쐐기가 남을 때만 §4.2에 따라 앞당긴다.
- 범위 밖: 캐시 미러 구조 변경, scratch 전체 clear로 바꾸는 것(성능 회귀), 값 0 일괄 제거, x≥800 compose를 꺼서 covered를 줄이는 것.

## 3. gate — V2q 추가

- V1·V2·V2s·V3는 그대로다. 임계값 2000 불변.
- **V2q (캡처, 네 개 전부 검정인 블록 직접 계수)**: 5 tag 각각에서, 월드 영역의 원본 픽셀 (x,y)가 검정이 아니고 후보 블록
  `(2x..2x+1, 2y..2y+1)`의 **네 subpixel 전부** 검정인 블록 수 ≤ 2000. V2·V2s와 같은 PNG·같은 루프에서 계산하고
  `capture_visual_comparisons`에 수와 `v2q_status`를 남긴다. aggregate 규칙은 V2s와 같고, pair 합격은 기존 조건 **그리고** V2q PASS다.
- 근거와 여유: 결함 없는 22장 최대 1361, 결함 있는 8장 최소 2179(§1.2). 여유가 크지 않다. 서로 다른 프로세스 캡처의 경보선이며
  동일 프레임 oracle이 아니다. 수리 뒤 정상 pair가 이 선에 걸리면 임계값을 올리지 말고 검정 블록의 위치를 기록해 middle에 넘긴다.
- 진단값(gate 아님, pair-result에 기록): tag별 x736..767 블록 수.

## 4. work P4c-W — 다음 work 1 lap

### 4.1 순서

1. **RED 먼저(게임 실행 없음).**
   - W2를 host gcc로 시험한다(`tests/test_g1_mirror2x.py`·`tests/test_g1_scale2x_mask.py`의 gcc fixture 방식. clear 영역 계산을
     `windows.h` 없이 컴파일되는 helper로 빼는 방법은 work가 정한다).
   - 필수 사례: ① 캐시 대상 `(768, y, 64, 32)` → clear가 x768..831을 덮는다(현재 식은 x768..799, RED). ② 캐시 대상 `(800, y, 64, 32)` → x800..831
     (현재 식은 빈 영역, RED). ③ 캐시 대상 `(−32, y, 64, 32)`·화면 대상 `(768, y, 64, 32)`는 수리 전과 같다.
     ④ x800..831에 `A==B`를 미리 채운 scratch에 clear를 적용하면 compose 영역 안에 `A==B`가 남지 않는다.
   - V2q 함수·gate 단위 테스트(경계 2000/2001, FAIL 집계의 JSON 왕복). 기존 raw로 확인: §1.2 표의 `전체` 값과 **같은 수**가 나와야 하고,
     lap904 B′1·B′2의 RIGHT 뒤 8 tag는 **FAIL**, GREEN r4 5 tag와 B′ loaded 2장은 **PASS**여야 한다. 다르면 식·구현을 먼저 바로잡는다.
     기존 raw·PNG는 읽기만 한다. 과거 pair-result는 고치지 않는다.
2. **수리.** §2의 W1 하나.
3. **GREEN = B′ 1번째.** 결함이 가로 이동 뒤에만 보이므로 GREEN은 lap904 B′과 같은 명령(`--hd-source scale2x --terrain-scroll --p4b-s-snapshot
   --reference-completed-states …lap888…`)의 새 격리 pair다. P4b-S gate 그대로 + V1 위반 0 + V2·V2s·V2q 5 tag + 기존 validator PASS를 확인하고,
   `selection.png` 두 장의 우측을 직접 연다. FAIL이면 원인 추적→수정→재실행을 3회까지 반복한다(PROMPT ③).
4. **B′ 2번째.** 같은 명령의 새 pair. 3·4가 연속 PASS여야 한다.
5. **C 재측정.** P4c 카드 §4.1의 5번 그대로 + V2s·V2q. 좋은 pair 고르기 금지. 모든 후보 캡처 보존.
6. lap 기록 → `make lint`·`make typecheck` → `make check` 1회. 시간이 모자라면 끝낸 단계까지 기록하고, 다음 work가 **재계획 없이**
   남은 실행만 잇는다. 끝까지 기다리지 못할 실행은 시작하지 않는다. 실행한 회차의 `local/runtime/<run>/game` 사본은 지운다.

### 4.2 사전 등록 예측 (수리가 맞다면)

- P-a: V1 위반 0(유지). V2s 5 tag ≤ 2000(유지, 현재 97~133).
- P-b: RIGHT 뒤 4 tag의 x736..767 블록 수가 2164~2370에서 **100 이하**로 떨어진다(이웃 구간 0~65 수준).
- P-c: V2q 5 tag 모두 ≤ 2000. 예상 범위 0~1400(스크롤 없는 캡처와 같은 수준).
- P-d: V2 초과 5 tag 모두 ≤ 2000. RIGHT 뒤 tag는 지금보다 약 2200 줄어든다.
- **반증**: 수리 뒤에도 RIGHT 뒤 tag의 x736..767 블록 수가 1500 이상이면, clear 폭이 원인이 아니거나 수리가 compose까지 닿지 않은 것이다.
  그때에만 진단 카운터 하나를 넣는다 — `compose_cache_layer`가 합성한 픽셀 중 identity mask가 미기록인 것의 수(전체·x≥800 구분, present trace에 기록).
  0이 아니면 §2의 ③(lookup이 mask를 존중)을 같은 lap에서 수리로 올린다. 0인데 쐐기가 남으면 HOLD·승격한다. 3회 안에 설명하지 못해도 같다.
- 100~1500 사이면 PASS/FAIL은 gate(V2·V2q)로 정하고, 남은 블록의 위치(열·`y mod 32`)를 기록해 middle이 판단하게 한다.

### 4.3 성공·실패 판정

- `PASS(work)`: 4.1의 3·4·5가 전부 PASS. 다음은 새 middle의 독립 검수(V3 포함).
- `HOLD`: 수리 3회 뒤에도 V1·V2·V2s·V2q 중 하나가 FAIL이고 원인을 설명하지 못할 때. raw·PNG·시도한 수리를 보존하고 승격한다.
- 화면 gate는 PASS인데 C 성능이 FAIL이면 화면 수리는 수용하고 성능만 별도 항목으로 남긴다.
- **입력 효과 UNKNOWN의 취급**: lap904 B′에서 selection·production·minimap 효과가 두 lane 모두 UNKNOWN이었다(스크롤 전 좌표를 스크롤 뒤에 쓴
  하네스 문제 유력, lap905 7항). pair 합격식에는 들어 있지 않다(`tools/g1_saved_scene_probe.py:4136~4145`). 이번 lap의 PASS 전제로 추가하지 않고,
  PASS로 바꿔 적지도 않는다. 두 lane이 다르게 나오면 그것은 새 발견이므로 기록하고 HOLD한다. 스크롤 뒤 좌표 수리는 화면 gate가 닫힌 뒤의 별도 work다.

## 5. 범위 밖·금지

- 기준·임계값·비교 필드 완화, validator 조건 삭제, 기존 raw/PNG/golden/안전핀 수정, 원본·참고 저장소 쓰기, EXE 파일 패치, 커밋.
- V2·V2q를 맞추려고 covered를 줄이는 것, 캡처 시점·영역·스크롤 순서를 바꿔 수를 맞추는 것, RIGHT를 일정에서 빼는 것.
- D-1 PS3 census, P5 HUD, 두 번째 장면. P4c 수용 뒤 순서대로 한다. G2/G5·G3/G4 재개, 개인 세션 runtime 접촉.

## 6. middle 검수 항목 (P4c-W work 뒤)

1. P4c 카드 §6의 1~5, P4c-M 카드 §6의 2~3.
2. V2q와 x736..767 블록 수를 실행된 전 쌍에서 직접 다시 계산하고 §1.2 표·§4.2 예측과 대조한다.
3. W2 테스트가 실제 clear 영역 계산을 컴파일해 돌리는지(소스 문자열 검사만이 아닌지) 확인한다.
4. V3: RIGHT 뒤 후보 캡처의 우측 지면을 원본과 나란히 보고 본 내용을 적는다. loaded도 본다.
- P단계 전환은 마일스톤 경계가 아니다(lap858 판정 유지). middle이 직접 PASS/HOLD를 낸다.

## 7. 재판정 조건

- §4.2의 반증이 성립하고 진단 카운터로도 설명되지 않으면 strategy가 캐시 층 미러 모형(P4b 카드)을 다시 본다.
- 제품 코드·실행 증거가 늘지 않은 회차가 lap905·906으로 연속 2회다. 다음 회차는 반드시 work 구현이다.

## 8. 재현

- `cd /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch && <repo>/.venv/bin/python 20261003_lap906_strategy_review/recalculate.py`
- `recalculate.py` SHA256 `1424125459dbf662c257ce85596a8a242da06d19a35db2209d72964865230a69`,
  `recalculation.json` SHA256 `f1af6b0688a68f7eb889ef38763f6bdac0ed495e9604b99282b30d8b1308419f`.
- 입력 66개(PNG 60장·pair-result 6개)의 SHA256은 `recalculation.json`의 `input_sha256`, 계산 전후 변화 0(`read_audit_changed: []`).
