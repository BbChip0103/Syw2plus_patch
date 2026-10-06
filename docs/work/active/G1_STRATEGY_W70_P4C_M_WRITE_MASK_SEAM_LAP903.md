# G1 W70 P4c-M — 타일 경계 검은 격자의 귀속(write mask 누락)과 수리 범위 (lap903 strategy, 2026-10-03)

- 발행: lap903 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, 자동 폴백 아님).
  게임 실행0, 제품/하네스/validator source·binary 변경0, subagent0, 커밋0.
- 호출 사유: lap902 middle의 `HOLD_SEAM_ATTRIBUTION_UNPROVEN` 승격(`loop/ESCALATE_SOL`, 보존본
  `docs/history/20261003_lap903_prior_lap902_escalate_sol_archive.md`).
- 입력 근거(이 세션이 직접 읽고 재계산): lap901 P4c 캡처 3 pair×5 tag, lap854 P3c gate 3 pair×5 tag(원본·후보 PNG 60장),
  origin pair 후보 trace, 현재 `tools/inmm_stub/g1_mirror2x.c`·`g1_hd_asset.c`, 지형 blitter 주소 문서(lap858).
  재계산은 공유 temp `20261003_lap903_strategy_review/`(`recalculate.py`, `recalculation.json`).
- 이 카드는 P4c 카드(`G1_STRATEGY_W70_P4C_TERRAIN_BIND_VISUAL_GATE_LAP900.md`)를 **대체하지 않는다.** 그 카드 §4.1의 2번(수리)에
  두 번째 수리 범위를 더하고, gate V에 V2s를 더한다. V1·V2·V3와 기존 임계값은 한 글자도 바꾸지 않는다.

## 0. 판정 요약

1. **남은 가는 검은 격자는 렌더러 결함이고, 원인은 identity frame이 write mask를 잃는 것이다.** 귀속
   `RENDERER(write mask 누락 → Scale2x가 미기록 0을 색으로 읽음)` 확정. lap902가 "유력"으로 남긴 경로를 실제 캡처 30쌍으로 확인했다(§1).
2. **같은-call 관측 회차는 열지 않는다.** lap902가 요구한 "실제 타일 한 종의 같은-call 귀속"은 §1.2의 기하 예측 일치(96%)와
   §1.3의 수량 일치로 대신한다. 수리한 빌드의 fresh pair가 곧 실험이며, 반증 조건을 §5에 미리 적었다.
3. **수리 범위는 두 바인딩 경로 모두다.** 비클립 지형(RLE·SHADE·CHECKER)만 고치면 부족하다. 타일이 캐시 viewport에 걸치면 같은 타일이
   CLIP·CLIP_SHADE로 그려지고(origin pair 마지막 present 누적 529회 대 비클립 375회), 그 경로의 identity frame도 mask가 없다(§1.4).
4. **V2는 순증가만 세기 때문에 격자가 있어도 PASS할 수 있다.** minimap tag 2건의 PASS(634·742)는 격자가 그대로인 상태였다(§1.5).
   격자를 직접 세는 **V2s**를 추가한다(§3). 강화이며 기존 조건을 대체하지 않는다.
5. **다음 work 1 lap = P4c-M**: 단위 RED → mask 보존 수리 → fresh pair GREEN(V1·V2·V2s·V3용 PNG) → B' 2 pair → C 3 pair(§4).
6. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 검수·3단 사용자 승인은 그대로 남는다.

## 1. 근거

### 1.1 소스 경로 — mask가 사라지는 네 지점

- `mirror_reinvoke`는 타일 영역의 scratch A를 `0x00`, B를 `0xFF`로 채우고 원본 writer를 두 번 부른다(`g1_mirror2x.c:1015~1044`).
  writer가 쓴 픽셀은 `A==B`, 쓰지 않은 픽셀(RLE skip, 마름모 바깥)은 `A=0x00, B=0xFF`로 남는다. 이 시점에는 mask가 있다.
- 비클립 바인딩은 scratch A의 origin 프레임만 넘긴다(`:1090~1097`). 클립 바인딩은 0으로 채운 버퍼에 한 번만 다시 그린 것을 넘긴다
  (`:1056~1087`). 둘 다 미기록 픽셀이 값 0으로 들어간다.
- `g1_hd_asset_bind_identity_frame`은 그 바이트를 그대로 저장한다(`g1_hd_asset.c:524~529`). mask 필드가 없다.
- `build_scale2x`는 네 이웃 B·D·F·H를 전부 색으로 비교한다(`:391~409`). 합성은 **중심 픽셀**의 `A==B`만 확인하고 HD 블록 4 subpixel을
  모두 복사한다(`g1_mirror2x.c:546~555`, `:497~513`).
- 결과: 마름모 왼쪽 위 변의 첫 픽셀 E는 위(B)와 왼쪽(D)이 미기록 0이다. `B≠H, D≠F, D==B`가 성립해 왼쪽 위 subpixel이 0(검정)이 된다.
  다른 세 변도 같은 식으로 바깥을 향한 subpixel **하나**만 0이 된다. 블록당 1개이므로 V1(블록당 ≤2)은 어기지 않는다.

### 1.2 사전 예측과 실제 캡처 — 검은 subpixel이 타일 격자선 위에 있다

위 경로가 맞다면, 원본이 검정이 아닌 픽셀 위에서 "2×2 블록 중 정확히 1개만 검정"인 블록은 다음을 만족해야 한다.
왼쪽 위(TL)·오른쪽 아래(BR)는 `x+2y = 상수`, 오른쪽 위(TR)·왼쪽 아래(BL)는 `x−2y = 상수`인 선 위에 있고, 타일 격자 주기로 반복된다.

월드 영역(논리 `[0,0,800,480)`), 5 tag × 3 pair = 15쌍의 최솟값~최댓값.

| 계열 | 단일 검정 블록 수 | 예측 축의 mod 64 인접 2칸 점유율 | 반대 축 점유율 | 돌바닥 ROI 잔차 | 2개 검정 블록 |
|---|---|---|---|---|---|
| lap854 P3c gate 1~3 (지형 미러 없음) | 476~614 | 0.07~0.16 | 0.06~0.10 | 0~1 | ≤3 |
| lap901 P4c 3 pair | 18,882~20,056 | **0.956~0.974** | 0.063~0.068 | 1367(15쌍 동일) | 0 |

- 균등 분포면 점유율은 2/64=0.031이다. P4c는 예측 축에서만 0.96이고 반대 축은 균등 수준이다.
- origin pair loaded: TL 4566개 중 4370개가 `(x+2y) mod 64 = 31` 한 칸에, TR 4621개 중 4425개가 `(x−2y) mod 64 = 32` 한 칸에 있다.
  주기는 64다(mod 16·32·64 점유율이 0.96으로 같고 mod 128에서 0.48로 반). 가로 64·세로 32 마름모 격자와 맞는다.
- 네 위치의 수가 고르다(TL 4566·TR 4621·BL 4867·BR 4828). 마름모 네 변에 하나씩이라는 설명과 맞는다.
- 한계: 캡처는 서로 다른 프로세스의 것이고, 프로세스 안에서 타일 한 장의 A/B·mask·HD 블록을 직접 본 것은 아니다. 고친 빌드는 아직 없다.

### 1.3 수량 정합

- 블록 histogram(검정 subpixel 0~4개)은 origin loaded에서 `355689/18884/0/59/9368`이다. 추가분 전부가 "1개" 칸이다.
  경로 1.1은 변 픽셀마다 정확히 1개를 만든다. 대면적 결손(4개)이나 2개 블록은 늘지 않았다.
- 논리 800×480에 64×32 마름모는 약 375장, 변 하나에 약 16행이므로 변 하나당 약 6000개가 상한이다. 실측 4566~5150(건물·유닛이 가린 만큼 적다).
- V2가 세는 것은 TL뿐이다. V2 초과 4.4k~4.9k는 TL 수 4.6k~4.9k와 같은 양이다.

### 1.4 비클립 경로만 고치면 부족한 이유

- 타일 dispatcher `0x435400`은 타일이 viewport 안에 온전히 있으면 `0x468C30`/`0x468CC0`, 걸치면 `0x468F00`/`0x4690A0`을 부른다
  (`analysis/memory_maps/g1_w70_p4_terrain_blitter_family_lap858.md`). 같은 타일 원천이 두 경로로 그려진다.
- origin pair 후보 마지막 PS3 present 누적: RLE 346 + SHADE 29 = 375, CLIP 173 + CLIP_SHADE 356 = 529, CHECKER 0.
- 클립 경로의 identity frame은 0으로 채운 버퍼에 한 번만 그린 것이라 한 버퍼로는 "쓴 0"과 "안 쓴 0"을 가를 수 없다. 두 번째 replay가 필요하다(§2 M1).
- 스프라이트 A·B도 클립 경로를 쓴다. 지형 미러 이전 15쌍의 단일 검정 블록 476~614에는 스프라이트 윤곽의 같은 유입이 섞여 있을 수 있다(미분리).

### 1.5 V2의 공백

- origin pair minimap tag: 원본 검정 14042(다른 tag는 9413~9937), 후보 TL 검정 14676, 초과 634로 PASS. 같은 캡처의 단일 검정 블록은 19,714개다.
  원본 쪽 화면에 검정이 늘면 순증가가 줄어든다. r2 pair의 742도 같다. 이 두 PASS는 격자가 없다는 뜻이 아니다.
- V2는 대면적 결손 경보선으로 그대로 둔다. 가는 격자는 V2s가 직접 센다.

## 2. 수리 규칙 (규범)

- **M1. 모든 identity frame은 write mask를 함께 가진다**(폭×높이, 1=writer가 쓴 픽셀).
  - 비클립 경로: scratch A·B의 origin 프레임에서 `mask = (A==B)`. 추가 호출 없음.
  - 클립 경로: (0,0) replay를 `0x00` 채움 버퍼와 `0xFF` 채움 버퍼에 한 번씩, `mask = (A==B)`. 기존 verify(`verify_unclipped_frame_in_viewport`)는 그대로 둔다.
    bind는 cache miss 때만 일어난다(origin pair 전체 inserts 363회). 호출당 비용이 아니다.
- **M2. `build_scale2x`는 미기록 이웃을 E로 본다.** 프레임 밖 이웃을 E로 보는 기존 규칙(`source_pixel` clamp)과 같은 규칙이다.
  중심 E가 미기록이면 그 블록은 합성에 쓰이지 않으므로 값은 무엇이든 되고, 차이·팔레트 통계에 넣지 않는다.
- **M3. 불변식(회귀 테스트로 고정).**
  (a) 전 픽셀이 written인 프레임은 수리 전 출력과 byte 동일. (b) 출력 subpixel은 E 또는 **written** 이웃의 값뿐.
  (c) writer가 실제로 쓴 팔레트 0은 색이다 — 보존되고 이웃으로 선택될 수 있다. (d) 블록당 변경 subpixel ≤ 2(V1 식 유지).
- **M4. scale2x 모드에서 mask 없는 bind는 하지 않는다.** mask를 만들지 못한 호출(할당 실패 등)은 bind하지 않고 기존 nearest fallback으로 둔다.
- **M5. mask 바이트를 cache 바이트 한도·통계에 포함한다.** `compare_visible_frame`의 값 비교와 refresh 규칙은 바꾸지 않는다.
- 범위 밖: subpixel 단위 투명(윤곽 smoothing), 타일 경계를 넘는 지형 층 단위 Scale2x, P4c 카드 §4.4 관찰 3건, 값 0 일괄 제거,
  nearest 강제, 지형 writer를 미러에서 빼는 것. 타일 경계가 nearest처럼 각지는 것은 DESIGN §2의 허용 화질 저하에 든다.

## 3. gate — V2s 추가

- V1·V2·V3는 P4c 카드 §3 그대로다. 임계값 2000 불변.
- **V2s (캡처, 격자 직접 계수)**: 5 tag 각각에서, 월드 영역의 원본 픽셀 (x,y)가 검정이 아니고 후보 블록 `(2x..2x+1, 2y..2y+1)` 중
  **정확히 1개** subpixel만 검정인 블록 수 ≤ 2000. 근거는 §1.2 표(정상 15쌍 최대 614, 격자 15쌍 최소 18,882).
  V2와 같은 PNG·같은 루프에서 계산하고 `capture_visual_comparisons`에 수와 `v2s_status`를 남긴다. aggregate는 V2와 같은 규칙(전부 PASS / 하나라도 FAIL / 그 외 BLOCKED).
- pair 합격은 기존 조건 **그리고** V2s PASS다. V2s도 서로 다른 프로세스 캡처의 경보선이며 동일 프레임 oracle은 아니다.
- 진단값(gate 아님, pair-result에 기록): 예측 축 mod 64 인접 2칸 점유율(위치 4종), 돌바닥 ROI `[400,260,620,360)` 잔차.

## 4. work P4c-M — 다음 work 1 lap

### 4.1 순서

1. **RED 먼저(게임 실행 없음).**
   - Scale2x 커널을 host gcc로 시험한다(기존 `tests/test_g1_mirror2x.py`의 gcc fixture 방식. `windows.h` 없이 컴파일되도록 커널을
     분리하는 방법은 work가 정한다. `g1_scratch_bounds.h`가 선례다).
   - 필수 사례: ① 마름모 mask(행마다 skip이 2씩 줄었다 느는 RLE 모양)에 단색 7 — 현재 커널은 0 subpixel을 낸다(RED), 수리 뒤 0개.
     ② lap902 반례 `[[7,0,7],[0,7,7],[7,7,7]]`: 위·왼쪽 미기록이면 `[7,7,7,7]`, 전부 written이면 `[0,7,7,7]` 유지.
     ③ 전부 written인 임의 프레임: 수리 전후 byte 동일. ④ written 0 이웃이 선택되는 사례. ⑤ 클립 경로 mask(두 버퍼) 생성.
   - V2s 함수 단위 테스트와, `_v2_capture_gate`가 FAIL tag를 `FAIL`로 집계해 JSON 왕복 뒤에도 유지하는 회귀(lap902 지적).
   - 기존 raw로 확인: V2s는 `20261003_1955_lap901_p4c_origin_pair` 5 tag **FAIL**, `lap854_p3c_gate1` 5 tag **PASS**여야 한다.
     다르면 식·구현을 먼저 바로잡는다. 기존 raw·PNG는 읽기만 한다. 과거 `BLOCKED` 기록은 고치지 않는다.
2. **수리.** §2의 M1~M5. 두 경로를 한 번에 고친다.
3. **GREEN.** lap901과 같은 명령으로 새 격리 pair 1회. V1 위반 0·V2 5 tag·V2s 5 tag·기존 validator PASS를 확인하고 `loaded.png` 두 장을
   직접 연다. FAIL이면 원인 추적→수정→재실행을 3회까지 반복한다(PROMPT ③).
4. **B' 재측정.** P4c 카드 §4.1의 4번 그대로 + V2s.
5. **C 재측정.** P4c 카드 §4.1의 5번 그대로 + V2s. 좋은 pair 고르기 금지. 모든 후보 캡처 보존.
6. lap 기록 → `make lint`·`make typecheck` → `make check` 1회. 시간이 모자라면 끝낸 단계까지 기록하고, 다음 work가 **재계획 없이**
   남은 실행만 잇는다. 끝까지 기다리지 못할 실행은 시작하지 않는다. 실행한 회차의 `local/runtime/<run>/game` 사본은 지운다.

### 4.2 사전 등록 예측 (수리가 맞다면)

- P-a: V1 위반 0(유지).
- P-b: V2 초과 5 tag 모두 ≤ 2000. 예상 범위 100~900(지형 미러 이전 105~652에 타일 안쪽의 정상 Scale2x 변화가 더해진다).
- P-c: 단일 검정 블록 5 tag 모두 ≤ 2000, 예측 축 점유율 < 0.5(현재 0.96).
- P-d: 돌바닥 ROI 잔차 1367 → 200 이하(진단값).
- **반증**: 수리 뒤에도 단일 검정 블록이 1만 이상이고 점유율이 0.9 이상이면, mask 누락이 원인이 아니거나 mask가 합성까지 닿지 않은 것이다.
  그때에만 타일 한 장의 같은-call dump(A·B·mask·HD 블록)를 진단으로 넣어 어느 쪽인지 가른다. 3회 안에 설명하지 못하면 HOLD·승격.
- 스프라이트 윤곽의 subpixel이 바뀌는 것은 예상된 결과다. P3·P3c 수용은 픽셀 값을 고정한 것이 아니며, 성능은 5번에서 다시 잰다.

### 4.3 성공·실패 판정

- `PASS(work)`: 4.1의 3·4·5가 전부 PASS. 다음은 새 middle의 독립 검수(V3 포함).
- `HOLD`: 수리 3회 뒤에도 V1·V2·V2s 중 하나가 FAIL이고 원인을 설명하지 못할 때. raw·PNG·시도한 수리를 보존하고 승격한다.
- 화면 gate는 PASS인데 C 성능이 FAIL이면 화면 수리는 수용하고 성능만 별도 항목으로 남긴다. 화면 수리를 되돌려 성능을 맞추지 않는다.

## 5. 범위 밖·금지

- 기준·임계값·비교 필드 완화, validator 조건 삭제, 기존 raw/PNG/golden/안전핀 수정, 원본·참고 저장소 쓰기, EXE 파일 패치, 커밋.
- V2·V2s를 맞추려고 covered를 줄이는 것, 값 0을 일괄로 지우는 것, 캡처 시점·영역을 바꿔 수를 맞추는 것.
- D-1 PS3 census, P5 HUD, 두 번째 장면. P4c 수용 뒤 순서대로 한다. G2/G5·G3/G4 재개, 개인 세션 runtime 접촉.

## 6. middle 검수 항목 (P4c-M work 뒤)

1. P4c 카드 §6의 1~5 전부.
2. V2s를 실행된 전 쌍에서 직접 다시 계산하고, 예측 축 점유율·돌바닥 ROI를 §1.2 표와 대조한다.
3. 불변식 M3 (a)~(d)의 테스트가 실제 커널을 컴파일해 돌리는지(소스 문자열 검사만이 아닌지) 확인한다.
4. V3: 후보 돌바닥·타일 경계·스프라이트 윤곽을 원본과 나란히 보고 본 내용을 적는다.
- P단계 전환은 마일스톤 경계가 아니다(lap858 판정 유지). middle이 직접 PASS/HOLD를 낸다.

## 7. 재판정 조건

- §4.2의 반증이 성립하고 같은-call dump로도 설명되지 않으면 strategy가 identity 바인딩 모델(W70 카드 §0.3)이 지형 타일에 맞는지 다시 본다.
- 제품 코드·실행 증거가 늘지 않은 회차가 lap902·903으로 연속 2회다. 다음 회차는 반드시 work 구현이다.

## 8. 재현

- `cd /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch && <repo>/.venv/bin/python 20261003_lap903_strategy_review/recalculate.py`
- `recalculate.py` SHA256 `049a41b128cbd1a73aa2be3e966b5e36124fb82a503b602d872450b61b7883b0`,
  `recalculation.json` SHA256 `2bfdfb259ad4460d28808a41f6194af19bbd6c6956f2f9a94bc0a166692ce378`.
- 입력 PNG 60장의 SHA256은 `recalculation.json`의 `input_sha256`, 계산 전후 변화 0(`read_audit_changed: []`).
