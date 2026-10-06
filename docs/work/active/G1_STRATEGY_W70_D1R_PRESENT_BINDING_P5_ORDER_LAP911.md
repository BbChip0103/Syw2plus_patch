# G1 W70 D-1R — PS3 present 버퍼 결합 수리와 P5 순서 확정 (lap911 strategy, 2026-10-03)

- 발행: lap911 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, 자동 폴백 아님).
  게임 실행0, 제품/하네스/validator source·binary 변경0, subagent0, 커밋0.
- 호출 사유: lap910 middle의 `HOLD_PRESENT_BUFFER_IDENTITY` 승격(`loop/ESCALATE_SOL`, 보존본
  `docs/history/20261003_lap911_prior_lap910_escalate_sol_archive.md`).
- 입력 근거(이 세션이 직접 읽고 재계산): lap909 final census raw·map·PNG, lap909 r2 후보 trace, lap907 5 pair의 후보 trace와 원본 PNG,
  현재 `tools/inmm_stub/g1_census.c`(SHA `7b448e19…7905`)·`direct_draw_trace.c`(SHA `e0690d8c…ec75`)·
  `tools/g1_saved_scene_probe.py`(SHA `a5357765…06ae`). 재계산은 공유 temp `20261003_lap911_strategy_review/`.
- 이 카드는 lap910 handoff(`G1_MIDDLE_W70_D1_PRESENT_BUFFER_HOLD_LAP910.md`)를 **흡수한다.** 겹치는 항목은 이 카드가 우선한다.
  lap858 P4 카드 §6·lap863 P4b 카드 §4의 "P5는 D-1 뒤에만, 순서는 D-1 수치가 큰 순서"는 §2로 바꾼다. 그 밖의 기준·임계값은 그대로다.

## 0. 판정 요약

1. **lap910 HOLD를 확인한다.** lap909의 "PS3 last-writer 맵" 64장은 PS3 화면이 아니라 **메인 메뉴(PS9) 화면의 맵**이다(§1.1).
   화면 비율 `block_copy 94.03% / rle_clip 5.97%`, 월드 `block_copy 100%`, "전사 뒤 block_copy가 덮는다"는 문장을 수용하지 않는다.
   lap909에서 수용하는 것은 9 hook 설치, PS3 present 64개의 경계, 전사 호출 수(469/469, present당 1), PS3 표본의 버퍼·인자,
   `surface_write` 표본뿐이다.
2. **P5 순서는 지금 정한다(§2).** P5-H(HUD 패널 표면) → P5-T(tinted RLE 2종). D-1의 순서 결정 기능은 여기서 끝난다.
   D-1R의 용도는 (a) HUD 패널 표면이 무엇으로 그려지는지(P5-H 설계 입력), (b) W70 §3.1 writer 분류표의 비율이다.
3. **수리는 결합 규칙 B1~B5와 gate G1~G4다(§3).** 맵은 present source 표면을 잠가 얻은 포인터·pitch와 같은 버퍼의 것만 쓴다.
   면적·순서·폭으로 고르는 추정 선택은 없앤다.
4. **lap910 handoff 2번(전사→후속 block_copy 순서 관측)은 열지 않는다.** 그 의문은 메뉴 맵에서 나왔다. 올바른 맵이 범주 9의 면적을 직접 준다.
   올바른 맵에서도 월드의 범주 9가 0일 때만 연다(§4.2 P-c).
5. **다음 work 1 lap = D-1R**(§4): 단위 RED → 수리 → 원본 census-only fresh 실행 → 표.
6. **계측기가 제품 진행을 막지 않는다(§5).** D-1R이 수리 3회 뒤에도 gate를 못 넘기거나 middle이 계측기 사유로 HOLD하면,
   strategy로 올리지 않고 다음 work가 P5-T를 먼저 한다(census와 무관한 제품 단계).
7. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 검수·3단 사용자 승인은 그대로 남는다.

## 1. 근거

### 1.1 맵 64장은 메인 메뉴 화면이다

- 64개 present의 map payload는 **한 가지**다(SHA256 `e40210e0…45c9`). 게임 화면이면 유닛·효과가 움직여 64장이 같을 수 없다.
- 64개 전부 `selected_buffer=0x0236BEA0`, header stride 800. raw의 primitive 표본 중 이 버퍼에 쓴 59개는 전부 PS9다.
  PS3 표본 128개는 `0x0223DC20`/stride 832(96개: `rle_tinted_clip`·`rect_fill`·`rect_border`)와 `0x020D0CD0`/stride 800(32개: `set_pixel`)이다.
  present source 폭은 64개 전부 832다.
- 맵을 범주별 색으로 그려 직접 봤다(`lap909_map_present1_writers.png`). `rle_clip` 28,654px은 y 488..577의 4×2 사각형 여덟 개이고
  나머지 451,346px이 `block_copy`다. 같은 실행의 `menu.png`에 있는 메뉴 버튼 여덟 개(시나리오·사용자변경·불러오기·…)의 자리와 같다.
  같은 실행의 `selection.png`(월드 + 하단 HUD)와는 닮은 데가 없다.

### 1.2 소스 — 왜 메뉴 맵이 PS3 present에 붙었나

- `selected_present_buffer()`(`g1_census.c:507~519`)는 버퍼별 누적 `assigned_pixels`·`changed_pixels`가 가장 큰 것을 고른다.
  메뉴 버퍼가 480,000을 먼저 채웠고 동률에서는 먼저 온 쪽이 남는다.
- `emit_present_boundary()`(`:535~541`)의 `state != 3` 검사는 present를 거를 뿐, 고른 맵이 그 present의 source인지는 보지 않는다.
- `direct_draw_trace.c:1349`는 census에 source의 폭·높이만 넘긴다. source 표면 포인터를 넘기지 않으므로 census는 결합할 재료가 없다.

### 1.3 gate — JSON과 header가 달라도 PASS

- `_validate_census_lane`(`tools/g1_saved_scene_probe.py:3610~3656`)은 hook·범주 수·PS3 상태·파일 크기만 본다. binary header를 읽지 않는다.
- 이 세션 재현: raw 사본의 `selected_buffer`를 전부 `0xDEADBEEF`로 바꾸고 map은 그대로 두어도 `PASS`다(원본 raw·map은 읽기만 했다).

### 1.4 PS3에서 실제로 보인 것 (lap909 raw 표본, 수용 범위)

- present: `BltFast(primary 0x01E75F60 ← 0x01E758F8 832×600)`, caller `0x00469379`.
- HUD: `BltFast(0x01E758F8 ← 0x01E757C8 800×203)`, caller `0x0041C60C`. PS3 표본 9개에서 present와 번갈아 나온다(HUD 5, present 4).
  **프리미티브 밖의 writer다.** 지금 census의 9 범주에는 이 writer가 없다. 결합만 고치면 HUD 패널 픽셀은 unknown이나 앞선 writer로 남는다 → B4.
- `set_pixel` 표본의 버퍼 `0x020D0CD0`/stride 800은 present 버퍼가 아니다. 패널 표면(800×203)일 가능성이 있다(미검증, §4.2 P-f).
- writer별 호출 수(전 상태 합): `rle_tinted` 37,169 · `rle_plain` 18,579 · `rle_tinted_clip` 6,478 · `set_pixel` 6,473 · `rle_clip` 5,123 ·
  `rect_fill` 3,113 · `rect_border` 1,217 · `block_copy` 601. PS3만의 호출 수는 raw에 없다(§3 B5에서 추가).

### 1.5 P5 순서의 근거 — 레이아웃 상한

- 후보의 PS3 유효 coverage `(covered − stale) / 480000` p50: lap907 B′1·B′2 0.6920, C1~C3 0.6923, lap909 r2 0.6908
  (present 981·974·904·903·899·498개). 미충족은 147.7k~148.4k 픽셀이다.
- 화면은 월드 384,000(y<480, 80%)과 HUD 행 96,000(y≥480, 20%)이다. 패널 표면은 800×203이라 y<480에도 걸친다
  (`selection.png`에서 좌측 깃발·미니맵 틀이 y≈430부터 시작).
- **월드를 전부 덮어도 80%다.** W70 §3.2의 90%는 HUD 패널 경로 없이는 어떤 순서로도 못 넘는다.
- HUD 행만 전부 더해도 `332k + 96k = 428k`(89.2%)라 여유가 없다. tinted RLE도 필요할 가능성이 높다. 둘 다 한다. 순서만 정하면 된다.

### 1.6 한계

- 1.5의 20%는 화면 배치에서 나온 상한이지 HUD 패널이 실제로 쓰는 픽셀 수가 아니다. 그 수는 D-1R이 잰다.
- tinted RLE가 PS3 월드에서 차지하는 면적은 모른다(`rle_tinted` 표본 32개는 PS35에서 소진됐다). `rle_tinted_clip`은 PS3 표본이 있다.
- 원본 PNG의 스크롤 전후 정적 비율(월드 0.205, HUD 행 0.70~0.71)도 계산했으나 선택·미니맵이 HUD 내용을 바꿔 경계가 선명하지 않다.
  순서 근거로 쓰지 않았다.

## 2. P5 순서 (확정)

1. **P5-H — HUD 패널 표면.** 필요조건이고(§1.5) 구조 위험이 가장 크다. 먼저 한다. 설계 가설: 패널 표면을 지형 캐시(P4b)와 같은
   **층**으로 미러한다(층 평면 + 색상키 전사). 패널 표면에 무엇이 쓰는지는 D-1R이 준다. middle이 그 표로 work 범위를 정한다.
   strategy를 다시 부르는 것은 패널 표면의 주 writer가 unknown(프리미티브·DD blt 밖)이라 층 미러로 설명되지 않을 때뿐이다.
2. **P5-T — tinted RLE 2종(`0x00466EA0`·`0x00466540`).** 기존 미러 방식의 확장이다(§5).
3. 그 뒤: `rect_fill`·`rect_border`·`set_pixel`의 "원천 그림 없음" 분류 확정, GDI 텍스트(P7), D-2 스크롤 성능, 두 번째 장면, 최종 입력.

## 3. 수리 규칙 (규범)

- **B1. present 결합.** present 경계에서 source 표면을 `DDLOCK_WAIT | DDLOCK_READONLY`로 잠가 `lpSurface`·`lPitch`를 얻고 바로 푼다
  (후보 lane이 present마다 하는 호출과 같다, `g1_mirror2x.c:709`). 원본 `BltFast`가 돌아온 뒤에 한다. 맵은 **버퍼 포인터와 stride가
  그 값과 같은** CensusBuffer의 것만 쓴다. 없거나 Lock이 실패하면 맵을 쓰지 않고 `binding`을 `unbound`로 남긴다.
  `selected_present_buffer()`의 면적 선택은 지운다. 첫 832 버퍼·최근 버퍼 같은 다른 추정도 넣지 않는다.
- **B2. 세대.** CensusBuffer는 마지막으로 쓴 `program_state`를 기억한다. 다른 상태에서 쓰면 그 버퍼의 map·context map·카운터·bbox를 비우고
  세대를 올린다. PS3 맵에는 PS3에서 쓴 픽셀만 남는다. 같은 세대 안에서는 바뀌지 않은 픽셀의 last-writer를 유지한다(기존 원칙).
- **B3. JSON과 header.** `present_boundary`에 `present_source_surface`·`present_source_buffer`·`present_source_pitch`·`binding`·
  `map_generation`·`map_generation_state`·`map_write_calls`(이 세대에 그 버퍼로 온 writer 호출 수)를 넣는다. binary header는 같은
  sequence·stride·buffer·state를 담는다. header 크기나 뜻을 바꾸면 magic도 바꾼다.
- **B4. DD 표면 writer.** PS3에서 destination이 primary가 아닌 `BltFast`/`Blt`는 원본 호출 앞뒤로 destination을 읽기 전용으로 잠가
  rect의 바이트를 비교하고, **바뀐 픽셀만** 범주 10 `dd_surface_blt`로 표시한다(색상키 때문에 rect 전체가 쓰이지 않는다).
  이때 얻은 destination 포인터로 맵 버퍼를 찾는다. source 표면도 읽기 전용으로 잠가 포인터·pitch·크기를 `surface_buffer` 행으로 남긴다
  (표면당 처음 한 번과 값이 바뀔 때). 이 추가 Lock은 census present 창(64개) 안에서만 한다.
- **B5. 버퍼 요약.** detach 때 CensusBuffer마다 `buffer_summary`(buffer·stride·세대 상태·assigned·범주별 픽셀 10개·bbox·writer 호출 수)를
  남긴다. 패널 표면 버퍼의 구성은 이 행으로 읽는다. writer `summary` 행에 `calls_ps3`를 더한다.
  버퍼 slot이 모자라 context를 못 만든 횟수(`buffer_context_dropped`)를 남긴다. slot 수는 work가 늘려도 된다.
- 지키는 것: opt-in·측정 전용, `CENSUS_PRESENT_LIMIT 64`, writer별 표본 cap 32, old-byte pin 9개, 원본 함수 무변경 호출,
  후보(mirror2x)와의 병용 금지.
- 범위 밖: 게임 로직·HD 렌더러(`g1_mirror2x.c`·`g1_hd_asset.c`)·화면 gate(V1·V2·V2s·V2q)·Scale2x validator·임계값.

### gate (`_validate_census_lane` 강화, 기존 조건은 그대로)

- **G1.** 모든 `present_boundary`: `binding == "locked_source"`, `present_source_buffer != 0`, `selected_buffer == present_source_buffer`,
  `map_generation_state == 3`, `map_write_calls > 0`.
- **G2.** map·context map의 모든 레코드: magic, sequence == `present`, stride == `present_source_pitch`, buffer == `selected_buffer`,
  state == 3, 파일 offset == `map_offset`. 하나라도 다르면 FAIL.
- **G3.** `writer_category` 10개, payload의 범주 id는 0..10뿐.
- **G4.** `buffer_context_dropped == 0`.

## 4. work D-1R — 다음 work 1 lap

### 4.1 순서

1. **RED 먼저(게임 실행 없음).**
   - 선택·세대 로직을 host gcc로 시험한다(`tests/test_g1_mirror2x.py`의 gcc fixture 방식. `windows.h` 없이 컴파일되는 helper로 빼는
     방법은 work가 정한다). 필수 사례: ① PS9에서 480,000을 채운 버퍼 A와 PS3에서 일부만 쓴 버퍼 B가 있고 present source가 B → B의 맵
     (현재 식은 A, RED). ② present source가 등록되지 않은 포인터 → `unbound`. ③ A와 같은 포인터가 PS3에서 다시 쓰이면 PS9 픽셀이 0.
     ④ 같은 세대의 두 present 사이에 쓰이지 않은 픽셀은 writer를 유지.
   - gate: lap909 raw·map의 **사본**으로 시험한다(원본은 읽기만). 원본 그대로 → FAIL(결합 필드가 없다. 과거 raw가 새 gate에서 떨어지는 것이
     맞다). `selected_buffer` 변이 → FAIL. header의 sequence·stride·buffer·state를 하나씩 바꾼 것 → 각각 FAIL. 합성한 정상 사례 → PASS.
2. **수리.** §3 B1~B5와 G1~G4.
3. **실행.** 원본 census-only fresh 1회(lap909 final과 같은 명령, 새 runtime·artifact 경로, 보호 원본·save006 SHA 확인, 실행 뒤 자기
   game 사본 삭제). FAIL이면 원인 추적 → 수정 → 재실행을 3회까지 반복한다(PROMPT ③).
4. **표.** 분모 셋(화면 480,000 · 월드 384,000 · HUD 행 96,000)에서 범주 0..10의 p50, unknown의 bbox와 행 분포, 패널 표면 버퍼의
   범주별 픽셀, writer별 `calls_ps3`. 맵 한 장을 §1.1처럼 색으로 그려 같은 실행의 PS3 PNG와 나란히 직접 본다.
5. lap 기록 → `make lint`·`make typecheck` → `make check` 1회. 끝까지 기다리지 못할 실행은 시작하지 않는다.

### 4.2 사전 등록 예측 (수리가 맞다면)

- P-a: 64 present 전부 `locked_source`. `selected_buffer`는 pitch 832인 버퍼다. lap909의 메뉴 버퍼가 아니다.
- P-b: map payload가 두 가지 이상이다. **64장이 전부 같으면 HOLD**(§1.1과 같은 증상).
- P-c: 월드에서 범주 9(지형 캐시 전사)가 가장 큰 범주다. 범주 9가 0이면 lap909의 "전사 뒤 덮임"이 실제라는 뜻이므로, 같은 lap에서
  전사 호출의 인자 표본을 PS3 창에 한정해 남기고 원인을 적는다(이것이 lap910 handoff 2번을 여는 유일한 조건).
- P-d: HUD 행에서 범주 10(`dd_surface_blt`)이 가장 큰 범주다. 그 위에 `rle_plain`·`rect_fill`·`rect_border`가 적게 얹힌다.
- P-e: unknown은 예측하지 않고 보고한다. PS3 세대의 unknown은 프리미티브도 DD blt도 아닌 쓰기(GDI 텍스트·직접 메모리 쓰기)이거나
  세대가 시작된 뒤 한 번도 쓰이지 않은 픽셀이다.
- P-f: PS3 `set_pixel` 표본의 버퍼가 HUD blt source(패널 표면)의 `lpSurface`와 같다. 다르면 그 버퍼가 무엇인지 `buffer_summary`와
  `surface_buffer` 행으로 적는다.

### 4.3 성공·실패 판정

- `PASS(work)`: RED→GREEN, gate G1~G4 PASS, P-a·P-b 성립, 4.1의 표 완성. P-c~P-f는 맞든 틀리든 **결과를 적으면 된다**(P-c의 0만 추가 작업).
  다음은 새 middle의 독립 검수다.
- `HOLD`: 수리 3회 뒤에도 G1~G4나 P-a·P-b가 안 되고 원인을 설명하지 못할 때. raw와 시도한 수리를 보존한다. 다음 work는 §5로 간다.
- census 수치는 HD coverage도 제품 PASS도 아니다.

## 5. P5-T 범위 (D-1R이 막히면 먼저, 아니면 P5-H 뒤)

- 대상: `0x00466EA0`(`rle_tinted`, 6인자 `ret 0x18`)·`0x00466540`(`rle_tinted_clip`, 6인자). dest probe는 둘 다 `no_dest_read`다
  (lap821, lap909 raw에서 다시 확인).
- 방식: 기존 writer A/B와 같은 sentinel 재호출·identity frame·Scale2x. 6인자 전용 wrapper를 쓰고, 캐시 키에 6번째 인자(색조 LUT 포인터)와
  그 LUT 내용의 digest를 넣는다. old-byte pin·rollback은 기존 hook과 같은 형식이다.
- 합격: 기존 P4c 순서 그대로 — 단위 RED → fresh pair GREEN(V1 위반 0, V2·V2s·V2q 5 tag, Scale2x validator) → B′ 2 pair → C 3 pair
  (ratio ≥ 0.95, p95 ≤ baseline + 16ms). 유효 coverage p50이 0.692보다 오르고 stale p50(74.1k~80.6k)이 준다.
  오르지 않으면 귀속이 틀린 것이므로 writer별 호출·covered 수를 적고 middle로 넘긴다.
- 성능 위험: 재호출 수가 지금의 약 3배가 될 수 있다(전 상태 호출 수 기준). 현재 p95 여유는 +8~9ms/한도 +16ms다. FAIL이면 P4 카드
  §5-3의 허용 수리(구간 표 → 순회 병합 → 비클립 cache-hit 빠른 경로)를 그대로 쓴다.

## 6. middle 검수 항목 (D-1R work 뒤)

1. build 입력·DLL·raw·map SHA, 보호 원본·save SHA, cleanup.
2. G1~G4를 raw·binary에서 직접 다시 계산한다. `present_source_buffer`가 PS3 primitive 표본의 버퍼와 같은지 본다.
3. 맵 한 장을 색으로 그려 같은 실행의 PS3 PNG와 나란히 보고 본 내용을 적는다(월드·HUD 경계, 패널 윤곽).
4. 4.1의 표를 다시 계산하고 P-a~P-f와 대조한다. 패널 표면의 주 writer를 근거로 P5-H work 범위를 정해 넘긴다.
- **승격 기준.** 계측기의 수리 대상이 분명한 구현 결함은 근거 충돌이 아니다. 수리 범위를 적어 work로 돌린다(lap773·lap858 규칙).
  `ESCALATE_SOL`은 설명되지 않는 실패, 서로 어긋나는 실제 실행 근거, G1 사용자 제출 경계에만 쓴다. P단계 전환은 마일스톤 경계가 아니다.

## 7. 재판정 조건

- 패널 표면의 주 writer가 unknown이라 층 미러로 설명되지 않을 때.
- P5-H·P5-T를 다 한 뒤에도 유효 coverage가 90%에 못 미칠 때(남은 면적의 분류와 함께).
- 제품 코드·실행 증거가 늘지 않은 회차가 lap910·911로 연속 2회다. 다음 회차는 반드시 work 실행이다.

## 8. 범위 밖·금지

- 기준·임계값·비교 필드 완화, validator 조건 삭제, 기존 raw·map·PNG·golden·안전핀 수정, 원본·참고 저장소 쓰기, EXE 파일 패치, 커밋.
- lap909 맵 수치를 PS3 근거로 다시 쓰는 것. PS9·PS35 맵으로 PS3 맵을 대신하는 것.
- G2/G5·G3/G4 재개, 개인 세션 runtime 접촉.

## 9. 재현

- `cd /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch && <repo>/.venv/bin/python 20261003_lap911_strategy_review/recalculate.py`
- `recalculate.py` SHA256 `5a3c8052f7571776acc06f012a8c7817b1f117123dd0a1f71d1d9e42a49eaf24`,
  `recalculation.json` SHA256 `e1d259c82761b58c1bc63f6140de1537f27b88aa317e251351605170594249e9`,
  `lap909_map_present1_writers.png` SHA256 `34d6138f39a4590d3d81c4d3459b07203db61d9fb24a18c331d968b1db6fc56a`.
- 입력 37개(census raw·map·context·probe-result·PNG 2장, 후보 trace 6개, 원본 PNG 25장)의 SHA256은 `recalculation.json`의
  `input_sha256`, 계산 전후 변화 0(`read_audit_changed: []`).
