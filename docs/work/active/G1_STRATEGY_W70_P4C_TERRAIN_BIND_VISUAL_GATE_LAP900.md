# G1 W70 P4c — 지형 HD 화면 결손 귀속과 화면 정합 gate V (lap900 strategy, 2026-10-03)

- 발행: lap900 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, 자동 폴백 아님).
  게임 실행0, 제품/하네스/validator source·binary 변경0, subagent0, 커밋0.
- 호출 사유: lap899 middle의 `HOLD_VISUAL_OUTPUT_ATTRIBUTION` 승격(`loop/ESCALATE_SOL`, 보존본
  `docs/history/20261003_lap900_prior_lap899_escalate_sol_archive.md`).
- 입력 근거(이 세션이 직접 읽고 재계산): 공유 temp의 후보 `loaded.png` 93개, lap844·854·858·866·896·898 후보 trace 13개,
  lap898 C1~3 캡처 15쌍, 현재 `tools/inmm_stub/g1_mirror2x.c`·`g1_hd_asset.c`·`tools/g1_hd_scale2x_probe.py`.
  재계산은 공유 temp `20261003_lap900_strategy_review/`(`recalculate.py`, `recalculation.json`, 확대 대조 PNG 1장).
- 이 카드는 P4 카드(`G1_STRATEGY_W70_P4_TERRAIN_BLITTER_HD_LAP858.md`)와 P4b 카드(`..._P4B_TERRAIN_CACHE_LAYER_LAP863.md`)의
  **합격 조건에 화면 정합 gate V를 추가**하고, 그 gate가 지금 FAIL인 원인의 수리(P4c)를 work에 넘긴다.
  기존 임계값(W70 카드 §3.5 성능, coverage 264000/0.9, B' 완전 일치)은 한 글자도 바꾸지 않는다. 조건은 늘어나기만 한다.

## 0. 판정 요약

1. **검은 마름모 격자는 캡처 문제가 아니다. 후보 렌더러의 지형 HD 합성이 틀린 그림을 쓴다.** 귀속 `RENDERER(HD compose)` 확정.
   프로세스 안에서 같은 프레임의 800 원본과 1600 출력을 비교한 기존 raw 수치만으로 판정된다(§1.2). 새 실행은 필요 없었다.
2. **결손은 lap898이 아니라 lap858, 즉 P4 지형 blitter를 처음 미러한 실행부터 있었다.** 그 뒤 후보 캡처 44개 전부가 같은 상태다(§1.1).
   lap858~898의 P4·P4b·B'·C 판정은 이 화면을 보지 않은 채 내려졌다.
3. **기존 gate가 놓친 이유는 두 가지다.** Scale2x validator는 HD 영역 안쪽 차이에 상한이 없고(`inside > 0`만 요구),
   캡처 검사는 "1600×1200이고 전부 검정은 아님"만 본다(§1.4). 2단 검수에서 PNG를 실제로 열어 본 것은 lap899가 처음이다.
4. **원인 후보는 한 지점으로 좁혀졌다(가설, 실행 미검증).** 지형 writer 3종(`0x468C30`·`0x468CC0`·`0x468E10`)은 identity frame을
   타일이 그려진 자리가 아니라 scratch 버퍼의 (0,0)에서 복사한다. 카운터가 이 설명과 맞는다(§1.3).
5. **다음 work 1 lap = P4c**: validator에 V1을 넣어 기존 trace에서 RED를 확인 → 바인딩 수리 → fresh pair에서 V1·V2 GREEN →
   같은 소스로 B' 2 pair·C 3 pair 재측정. 수리→재실행은 PROMPT ③대로 추적 가능한 결함이면 3회까지 반복한다(§4).
6. **과거 판정의 효력을 나눈다(§2).** 시뮬레이션 비간섭·입력·성능 수치는 그 값을 잰 사실로 남는다. "HD coverage"와
   "Scale2x validator PASS"는 그림이 맞다는 증거로 쓸 수 없다. C·B'는 수리된 소스로 다시 잰다.
7. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 검수·3단 사용자 승인은 그대로 남는다.

## 1. 근거

### 1.1 캡처 계열 — 결손은 P4 도입 시점에 계단처럼 생겼다

월드 영역(논리 `[0,0,800,480]`, 384000 표본)에서 RGB가 (0,0,0)인 표본 수. 후보는 (2x,2y), 원본은 (x,y)에서 읽었다.

| 구간 | 후보 `loaded.png` 수 | 후보 검정 | 원본 검정 |
|---|---|---|---|
| lap812~854 (W60·P2·P3·P3c, 지형 미러 없음) | 40 | 9417~9751 | 9411~9427 |
| lap834~840 (원본·후보 둘 다 전부 검정인 캡처, 원인 미조사·이 판정과 무관) | 9 | 384000 | 384000 |
| lap858~898 (P4 지형 blitter 미러 이후) | 44 | 191950~195864 | 9411~9427 (30개. 원본 캡처가 전부 검정 6개, 원본 캡처 없음 8개) |

- 캡처 경로(Xvfb, 캡처 도구, present 경로)는 lap854와 lap858 사이에 바뀌지 않았다. 바뀐 것은 지형 writer 5종의 미러 hook뿐이다.
- 계열 첫 실행은 `lap858_p4_blitter_pair`(2026-10-02 05:56, 후보 검정 193306)이다.
- 한계: PNG는 서로 다른 프로세스·시점의 캡처다. 이 표만으로는 동일 프레임 증명이 아니다. 동일 프레임 증명은 §1.2다.

### 1.2 프로세스 안 동일 프레임 수치 — 수학적으로 불가능한 값

present 시점에 DLL은 같은 프레임의 800 원본 픽셀과 1600 출력 2×2 블록을 비교해 `hd_mask_inside_diff_subpixels`(HD 영역 안에서
원본 픽셀 값과 다른 subpixel 수)를 남긴다(`g1_mirror2x.c:729~754`). HD로 쓰인 픽셀 수는 `covered_pixels − stale_pixels`다.

Scale2x는 한 픽셀 E의 2×2 블록에서 **최대 2개** subpixel만 이웃 값으로 바꾼다. 왼쪽 위가 바뀌려면 `B==D, B≠F, D≠H`,
오른쪽 위는 `B==F`가 필요해 둘은 동시에 성립하지 않고, 왼쪽 위와 왼쪽 아래(`D==H` 필요)도 그렇다. 대각 한 쌍만 함께 바뀔 수 있다.
따라서 올바른 합성이면 모든 present에서 다음이 성립한다.

> **V1: `hd_mask_inside_diff_subpixels ≤ 2 × (covered_pixels − stale_pixels)`** (비율로는 ≤ 0.5)

| 실행 | scale2x present | V1 위반 | PS3 안쪽 차이 비율 min / p50 / max | PS3 nearest 일치율 p50 |
|---|---|---|---|---|
| lap844 P3 perf6 | 248 | 0 | 0.060 / 0.062 / 0.069 | 0.988 |
| lap854 P3c gate1·2·3·latch | 1350·1324·1362·1013 | 0 | 0.059 / 0.062 / 0.068 | 0.986 |
| lap858 P4 pair·r4 | 1354·1373 | 888·889 (PS3 전부) | 0.833 / 0.880·0.852 / 0.887 | 0.448·0.446 |
| lap866 P4b r5 | 1017 | 813 (PS3 전부) | 0.835 / 0.893 / 0.900 | 0.339 |
| lap896 B' pair1·2 | 1173·1169 | 972·978 (PS3 전부) | 0.835 / 0.891 / 0.900 | 0.339 |
| lap898 C1·C2·C3 | 1092·1069·1087 | 894·888·890 (PS3 전부) | 0.835 / 0.850 / 0.859 | 0.352 |

- P4 이후 PS3 present는 **한 장도 빠짐없이** V1을 어긴다. HD로 쓴 subpixel의 83~90%가 그 자리 원본 픽셀과 다르다. 지형 미러가
  없던 P3는 6%대이고 위반 0이다. 메뉴 상태(PS9·PS35)는 P4 이후에도 위반 0이다.
- C1 마지막 PS3 present: covered 424405, stale 71653, 안쪽 차이 1,198,772(상한 705,504), nearest 일치 677,472/1,920,000.
  같은 시점 자산 단위 Scale2x 차이율은 272,423/(4×2,279,488)=3.0%다. 자산은 3%만 바뀌는데 화면은 85%가 다르다. 합성이 틀린 블록을 쓴다.
- 이것은 present 직전 표면의 값이다. X11 캡처·팔레트·표시 경로는 관여하지 않는다.

### 1.3 원인 후보 H1 — 비클립 writer의 identity frame을 (0,0)에서 복사 (정적 + 카운터 정합, 실행 미검증)

- `mirror_reinvoke`는 원본 writer를 scratch 버퍼에 다시 호출한 뒤 identity frame을 바인딩한다. `clipped=TRUE` 경로는 (0,0)에
  다시 그린 `unclipped` 버퍼를 넘기고(`g1_mirror2x.c:1055~1089`), `clipped=FALSE` 경로는 **타일이 `(origin_x, origin_y)`에 그려진
  `scratch_a`를 그대로** 넘긴다(`:1090~1092`).
- `g1_hd_asset_bind_identity_frame`은 넘겨받은 버퍼의 **행 0·열 0부터** `width×height`를 복사한다(`g1_hd_asset.c:524~528`).
  origin을 쓰지 않는다. (0,0) 재호출 버퍼에는 맞고, origin에 그려진 scratch에는 틀리다.
- `clipped=FALSE`로 부르는 곳은 지형 RLE `0x468C30`(`:1316`), SHADE `0x468CC0`(`:1345`), CHECKER `0x468E10`(`:1372`) 셋뿐이다.
  스프라이트 A/B(`:1242`,`:1270`)와 지형 CLIP·CLIP_SHADE(`:1399`,`:1428`)는 `TRUE`다. P3까지 이 분기는 실행된 적이 없다.
- 결과 예측과 실제 화면이 맞는다. scratch 왼쪽 위 `width×height`에는 그 자리에 걸친 다른 타일 조각이나 0이 있다. 그래서 모든 타일이
  같은 삼각 조각 + 검정으로 나오고, 원본이 회색 돌바닥인 곳에도 갈색 흙 무늬 조각이 보인다(확대 대조 PNG, §8).
- 카운터: C1 마지막 PS3 present에서 `identity_cache_refreshes=376`, RLE 346 + SHADE 29 = 375. `inserts 716 = misses 340 + refreshes 376`.
  캐시 hit 때 `g1_hd_asset_compare_visible_frame`은 origin을 올바로 써서 비교하므로(`g1_hd_asset.c:461~472`) 틀린 frame을 매번
  버리고, 곧바로 같은 분기에서 다시 (0,0)으로 바인딩한다. 비클립 지형 호출마다 refresh 1회라는 설명과 1 차이로 맞는다.
- 한계: 고친 빌드를 돌려 보지 않았다. CLIP 계열(578회)에 다른 결함이 겹쳐 있는지는 이 근거로 알 수 없다(§4.4 관찰 목록).

### 1.4 gate 공백

- `tools/g1_hd_scale2x_probe.py::validate_trace`는 `outside == 0`, `inside > 0`, palette violation 0, lookup miss 0만 본다(`:66~86`).
  안쪽 차이의 상한이 없어 "팔레트 안의 틀린 그림"은 통과한다. 세 C pair의 `PASS`는 이 검사의 PASS다.
- C 조건 "loaded 후보 캡처 non-black 1600×1200"은 전부 검정만 거른다. 월드의 48%가 검정이어도 통과한다.
- coverage(`covered − stale`)는 "HD 블록을 쓴 픽셀 수"다. 블록 내용이 맞는지는 세지 않는다.

## 2. 과거 판정의 효력

| 판정 | 유지되는 것 | 더 이상 근거가 못 되는 것 |
|---|---|---|
| lap858~864 P4, lap863 P4b coverage 수치 | writer 귀속·호출 수·캐시 층 이동 계측 | "유효 HD coverage 68~70%"를 올바른 HD 그림의 면적으로 읽는 것 |
| lap897 B' `PASS(partial)` | 시뮬레이션 상태 parity(E1~E4), 입력 parity, cleanup, source identity | 그 판정에 포함된 coverage·Scale2x validator 항목 |
| lap898 C 수치 3/3 | 그 빌드의 tick ratio·p95 측정값 | C 수용. 렌더러가 바뀌면 캐시 hit 양상이 달라지므로 수리 뒤 다시 잰다 |
| P2·P3·P3c (lap841·843·858 통합 수용) | 전부 유지 — V1 위반 0, 캡처 정상(§1.1·1.2) | 없음 |

- 과거 기록·raw·PNG는 고치지 않는다. 위 표는 앞으로 어떤 근거로 쓸 수 있는지의 판정이다.
- P4·P4b의 단계 상태는 `HOLD(화면 정합)`로 되돌린다. D-1·P5 전환은 P4c 수용 뒤다.

## 3. 화면 정합 gate V (신규, 강화)

P4c부터 G1의 모든 HD 단계(B'·C·D·P5 이후 포함) 합격에 아래 셋을 **추가**한다. 기존 조건을 대체하지 않는다.

- **V1 (프로세스 안, 정확식)**: 후보 trace의 모든 scale2x `mirror2x_present`에서
  `0 ≤ stale_pixels ≤ covered_pixels`이고 `hd_mask_inside_diff_subpixels ≤ 2 × (covered_pixels − stale_pixels)`. 위반 0건.
  이미 trace에 있는 필드만 쓴다. DLL 계측 추가는 필요 없다. `validate_trace`에 넣고 errors에 present index와 세 값을 남긴다.
- **V2 (캡처 tripwire)**: 캡처 tag 5개(loaded·selection·drag·minimap·production) 각각에서 월드 영역 검정 표본이
  `후보(2x,2y) − 원본(x,y) ≤ 2000`. 지형 미러 이전 lap854 gate1~3의 캡처 15쌍에서 최대 초과는 652, 결손 상태 15쌍의 최소 초과는 185,824다.
  서로 다른 프로세스의 캡처이므로 동일 프레임 oracle이 아니다. 육안으로 보이는 대면적 결손을 기계가 놓치지 않게 하는 경보선이다.
- **V3 (2단 검수 필수 항목)**: middle은 후보·원본 `loaded.png`를 직접 열어 나란히 보고, 본 내용(지형·건물·HUD가 같은 자리에
  같은 그림으로 있는지, 대면적 결손·색 이상 유무)을 판정문에 한 줄로 적는다. PROMPT ⑥의 기존 요구를 생략 불가 항목으로 고정한다.
- V1은 필요조건이다(블록의 절반이 우연히 맞는 틀린 그림은 통과할 수 있다). V1·V2가 PASS인데 V3에서 이상이 보이면 middle은 HOLD하고,
  그때에만 strategy가 화면 단위 exact oracle(동일 프레임 지형 층 Scale2x 대조) 추가를 판단한다. 지금 선행 조건으로 만들지 않는다.

## 4. work P4c — 다음 work 1 lap

### 4.1 순서

1. **RED 먼저.** `validate_trace`에 V1을, `g1_saved_scene_probe`의 캡처 판정에 V2를 넣고 단위 테스트를 쓴다(위반 행·경계값 `inside == 2×eff`·
   `stale > covered`·필드 누락). 기존 raw로 확인한다: lap898 C1 후보 trace는 **FAIL**, lap854 `p3c_gate1` 후보 trace는 **PASS**여야 한다.
   둘 중 하나라도 다르면 수리로 넘어가지 말고 식·구현을 먼저 바로잡는다. 기존 raw 파일은 읽기만 한다.
2. **수리.** H1의 바인딩을 고친다. 권장은 세 writer를 스프라이트와 같은 (0,0) 재호출 경로로 보내는 것이다(`clipped=TRUE`).
   P2부터 검증된 경로이고 캐시 가장자리에 걸친 타일도 잘리지 않은 frame으로 바인딩한다. 대안은 origin 오프셋에서 복사하되 타일이
   버퍼 안에 온전히 있을 때만 바인딩하는 것이다. 어느 쪽이든 work가 실측으로 고른다. 선택 근거를 기록한다.
3. **GREEN.** 새 격리 pair 1회(`--hd-source scale2x`, save006, 기존 명령)에서 V1 위반 0·V2 5 tag PASS·기존 validator PASS를 확인하고,
   `loaded.png` 두 장을 직접 열어 본다. FAIL이면 원인 추적→수정→재실행을 3회까지 반복한다.
4. **B' 재측정.** P4b-S gate 그대로 current-source fresh pair 연속 2회(비교 필드·완전 일치·r1 일정 불변) + V1·V2.
5. **C 재측정.** 계측 OFF fresh 3 pair, W70 카드 §3.5 기준 그대로(ratio ≥ 0.95, p95 Δ ≤ 16ms, coverage first20 ≥ 264000, last20 ≥ first20×0.9) + V1·V2.
   좋은 pair 고르기 금지. 3·4·5의 모든 후보 캡처는 보존한다.
6. lap 기록 → `make lint`·`make typecheck` → `make check` 1회. 시간이 모자라면 끝낸 단계까지 기록하고, 다음 work가 **재계획 없이**
   남은 실행만 이어서 한다. 시작해 놓고 끝까지 기다리지 못할 실행은 시작하지 않는다.

### 4.2 사전 등록 예측 (수리가 맞다면)

- P-a: V1 위반 0건(현재 PS3 100% 위반).
- P-b: 마지막 PS3 present의 `identity_cache_refreshes`가 RLE+SHADE 호출 수를 따라가지 않는다(현재 376 대 375). 값 자체는 gate가 아니다.
- P-c: V2 5 tag 전부 PASS, 육안으로 지형이 원본과 같은 그림.
- P-a는 성립하는데 P-c가 깨지면 H1만으로는 부족하다는 뜻이다. §4.4를 차례로 본다.

### 4.3 성공·실패 판정

- `PASS(work)`: 4.1의 3·4·5가 전부 PASS. 다음은 새 middle의 독립 검수(V3 포함)다.
- `HOLD`: 수리 3회 뒤에도 V1 또는 V2가 FAIL이고 원인을 설명하지 못할 때. raw·PNG·시도한 수리를 보존하고 승격한다.
- V1·V2는 PASS인데 C 성능이 FAIL이면 화면 수리는 수용하고 성능만 별도 항목으로 남긴다. 화면 수리를 되돌려 성능을 맞추지 않는다.

### 4.4 같은 구역의 관찰 (미검증, H1 수리 뒤에도 FAIL일 때만 본다)

- `mirror_reinvoke`의 scratch 초기화 범위가 폭 800 기준이다(`g1_mirror2x.c:1015~1016`). 캐시는 폭 832다. 열 800~831은 지워지지 않아
  이전 primitive의 값이 "이번에 쓴 픽셀"로 읽힐 수 있다.
- `g1_hd_asset_begin_with_aux`의 clipped 판정과 `compare_visible_frame`의 가시 범위가 800×600 기준이다(`g1_hd_asset.c:236~238`, `:461~462`).
  캐시(832×512)를 대상으로 할 때 범위가 맞는지 확인한다.
- CLIP 계열의 (0,0) 재호출은 viewport를 `{0,0,799,599}`로 강제한다(`g1_mirror2x.c:1061`). 캐시 대상 호출에서의 동작은 실측하지 않았다.

## 5. 범위 밖·금지

- 기준·임계값·비교 필드 완화, validator 조건 삭제, 기존 raw/PNG/golden/안전핀 수정, 원본·참고 저장소 쓰기, EXE 파일 패치, 커밋.
- V1·V2를 맞추려고 covered를 줄이는 것(지형 writer를 미러에서 빼서 nearest로 되돌리는 것). coverage 기준이 함께 걸려 있다.
- D-1 PS3 census, P5 HUD, 두 번째 장면, 새 관측 장치. P4c 수용 뒤 순서대로 한다.
- G2/G5 재개, G3/G4 재개, 개인 세션 runtime 접촉.

## 6. middle 검수 항목 (P4c work 뒤)

1. V1을 trace에서 직접 다시 계산(전 present, 위반 0)하고 validator 결과와 대조한다.
2. V2를 15쌍(또는 실행된 전 쌍)에서 직접 다시 계산한다.
3. V3: `loaded.png` 원본·후보를 열어 본 내용을 적는다.
4. RED 확인이 실제로 기존 raw에서 이뤄졌는지(lap898 C1 FAIL, lap854 gate1 PASS) 재현한다.
5. B' E1~E4·C 수치·source identity·cleanup은 기존 방식대로 독립 재계산한다.
- P단계 전환은 마일스톤 경계가 아니다(lap858 판정 유지). middle이 직접 PASS/HOLD를 낸다.

## 7. 재판정 조건

- P4c가 `HOLD`로 끝나고 다음 work 1회에서도 V1이 FAIL이면 strategy가 캐시 층 미러 설계(W70 카드 §0.3의 identity 바인딩 모델이
  지형 타일에 맞는지)를 다시 본다. 그 전에는 구조 재설계를 열지 않는다.
- 제품 코드·실행 증거가 늘지 않은 회차가 lap899·900으로 연속 2회다. 다음 회차는 반드시 work 구현이다.

## 8. 재현

- `cd /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch && <repo>/.venv/bin/python 20261003_lap900_strategy_review/recalculate.py`
- `recalculate.py` SHA256 `9b2aa077792d4917e0e569be315468f2d0e06bac81dcc0c6fad5074b794c7c2b`,
  `recalculation.json` SHA256 `de3a82b6991ac6885c6da89b4eae25d8d4b3b196324ae532a0fe4028e32eb307`.
- 확대 대조 PNG(위 원본·아래 후보, 논리 `[200,280]~[360,380]`, lap898 C1 loaded)
  `20261003_lap900_strategy_review/20261003_lap900_c1_loaded_crop_baseline_top_candidate_bottom.png`,
  SHA256 `d2f9970ac50446c5d5b8766a8d6667b2cac627f6c8e6bfb252610f50c221b08e`.
- trace별 SHA256·전 수치는 `recalculation.json`의 `v1_runs`·`v2_runs`·`loaded_capture_history`.
