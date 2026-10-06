# G1 W70 P5-H — HUD 패널 원천 확정과 패널 층 미러 (lap914 strategy, 2026-10-04)

- 발행: lap914 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, 자동 폴백 아님).
  게임 실행0, 제품/하네스/validator source·binary 변경0, subagent0, 커밋0.
- 호출 사유: lap913 middle의 `HOLD_PANEL_ORIGIN_UNPROVEN` 승격(`loop/ESCALATE_SOL`, 보존본
  `docs/history/20261004_lap914_prior_lap913_escalate_sol_archive.md`).
- 입력 근거(이 세션이 직접 읽고 재계산): 보호 원본 EXE 디스어셈블, `fnt/pannel{k,j,c}.spr`, lap912 census raw·map·trace·PNG 4장,
  현재 `tools/inmm_stub/g1_mirror2x.c`(SHA `e6f4d0ef…8aab`)·`direct_draw_trace.c`(SHA `ea09ed6c…7aef`).
  주소 문서 `analysis/memory_maps/g1_w70_p5h_panel_surface_writers_lap914.md`, 재계산은 공유 temp `20261004_lap914_strategy_review/`.
- 이 카드는 lap913 handoff(`G1_MIDDLE_W70_P5H_PANEL_ORIGIN_HOLD_LAP913.md`)를 **흡수한다.** 겹치는 항목은 이 카드가 우선한다.
  lap911 카드 §2(P5-H → P5-T)·§5(P5-T 범위)는 그대로다.

## 0. 판정 요약

1. **패널 원천은 확정됐다.** 패널 바닥 그림은 `fnt\pannel{k,j,c}.spr`(국가별 한 프레임, 831×h)이고, 렌더러 `0xE5BF18`의 프리미티브
   **`0x004663E0`**(키 채움 RLE)이 패널 표면 `[0x0104F814]`에 그린다. lap913의 "미분류 161,878픽셀"은 census의 9 pin에 이 함수가
   없어서 생긴 것이다. GDI·표면 간 blt가 아니다.
2. **P5-H `FEASIBLE`**(정적 + 기존 raw 대조, 미러 실행 미검증). 주 writer가 같은 렌더러의 프리미티브이므로 lap911 §2의 층 미러 가설로
   설명된다. lap911 §7의 재판정 조건("주 writer가 unknown이라 층 미러로 설명되지 않을 때")은 해당하지 않는다.
3. 패널에는 writer가 둘 더 있다: 미니맵 지형 `0x00451560`(버퍼에 **직접** 쓴다)과 미니맵 점 `0x00451730`(set_pixel).
   둘 다 원천 그림이 없다. P5-H에서는 hook하지 않고 **내용 대조**로 nearest에 남긴다(§2 H4).
4. lap913 handoff 3번의 두 선택지(패널 한정 관측 probe / P5-T 우선 fallback)는 **둘 다 고르지 않는다.**
   다음 work 1 lap이 P5-H를 바로 구현한다. 관측은 구현 안의 사전 등록 대조 PH-a·PH-b가 대신한다(§4).
5. census 계측 결함 두 건(lap913 기록)은 P5-H의 선행 조건이 아니다. census를 다시 돌리는 회차의 첫 작업으로 둔다(§6).
6. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 검수·3단 사용자 승인은 그대로 남는다.

## 1. 근거

### 1.1 정적 (원본 EXE SHA `b56986e0…a8ac`)

- 패널 표면 `[0x104F814]`를 잠그는 곳은 6곳뿐이다(표면 포인터 참조 16곳 전수). 쓰는 것은 5곳이다:
  `0x4663E0` 호출 4곳(`0x41B787` `0x41C5A0` `0x424965` `0x441533`)과 미니맵 한 곳(`0x41C524`·`0x41C52E`).
- `0x4663E0(x, y, w, h, src)`: 행마다 w칸을 채우고, src의 `0xFE n`은 **목적지에 `0xFE`를 n번 쓴다.** 클립·목적지 읽기 없음.
  인자는 `(·,·,[0xB92CE4],[0xB92CE8],[0xB938D4])` = `0x419B50(nation)`이 읽은 `fnt\pannel{k,j,c}.spr`.
- 색상키는 표면 생성 때 `0xFE`로 정해진다(`0x464DB3`). 전사는 `0x41C5C0`의 `BltFast(…, 0x11)`(반환 `0x41C60C`).
- 미니맵 지형 `0x451560`은 `[0xE5D42C]`(렌더러 버퍼)에 `mov [eax+…],dl`로 직접 쓴다. set_pixel `0x4658E0`의 호출자는 `0x451730`뿐이다.

### 1.2 기존 raw 대조 (사전 예측을 `recalculate.py` 머리에 적고 실행, 넷 다 성립)

| 예측 | 결과 | 반증 기준 |
|---|---|---|
| Q1 범주 10 픽셀은 y≥457에만 있고 pannelj 불투명 칸 위가 ≥0.98 | 64장 4,449,556픽셀 중 4,449,556(1.000), y<457에 0 | <0.90 (무관하면 0.823) |
| Q2 PNG에서 pannelj의 인덱스별 최빈 RGB 일치율 ≥0.70, 다른 그림·어긋난 대조군보다 뚜렷이 높음 | pannelj 0.735 / 0.796 / 0.784 / 0.793, pannelk 0.256~0.267, pannelc 0.266~0.281, 어긋난 pannelj 0.307~0.353 | pannelj가 최고가 아니거나 <0.5 |
| Q3 pannelj **키** 칸 위의 범주 10은 미니맵 구역 안 | 0픽셀(미니맵 자리는 그림에서 불투명한 검정이다) | 구역 밖에 있음 |
| Q4 마지막 맵의 unknown은 전부 y≥512 | 7,251픽셀 전부 y 512..599, 전부 pannelj 불투명 칸 | y<512에 있음 |

- 전사 표본 19개는 전부 `(0,457) ← [0,0,800,143]`, flags 17. 143은 `pannelj.spr` header의 높이다. 세 파일 모두
  `0x4663E0` 알고리즘으로 831×h를 풀면 파일 끝과 정확히 맞는다.
- 풀어 그린 pannelj와 `selection.png`의 y457..599를 나란히 직접 봤다(`pannelj_decoded_vs_selection_hud.png`).
  미니맵 마름모·초상화 원·F1~F11 칸·명령 4×3 칸의 자리가 같다. 캡처에는 그 위에 깃발·초상화·버튼·글자가 얹혀 있다.
- Q4의 뜻: y≥512는 지형 전사(캐시 높이 512)가 다시 덮지 않아 패널 픽셀이 프레임 사이에 그대로 남는다. census는 **바뀐** 픽셀만
  범주 10으로 적으므로 그 칸은 unknown으로 남았다. 쓰는 writer가 없다는 뜻이 아니다.

### 1.3 한계

- `0x4663E0`이 패널에 쓰는 순간을 hook으로 본 적은 없다. 1.2는 결과 픽셀의 대조다. PH-b(§4.2)가 실행에서 확인한다.
- save006은 일본이다. 조선·명 패널(높이 163·160)은 전사 y와 rect가 다르다. 두 번째 장면에서 다룬다.
- gate `0x41C450`이 save006에서 열려 있다는 것은 set_pixel 6,473회가 `0x451730`에서만 올 수 있다는 정적 사실로 추정했다.

## 2. 패널 층 계약 (규범)

- **H1. 결합.** 패널 버퍼는 크기로 고르지 않는다. `0x4663E0` hook에서 **반환 주소가 `0x41B78C`·`0x41C5A5`·`0x42496A`·`0x441538`**이면
  그 순간의 렌더러 버퍼(`+0x1514`)·pitch(`+0x10`)·높이(`+0x08`)를 패널로 기록한다. 전사 때(H4) source 표면을 읽기 전용으로 잠가
  얻은 `lpSurface`·`lPitch`가 그 값과 같아야 한다. 다르거나 Lock이 실패하면 그 present의 패널은 `unbound`(패널 HD 없음, nearest)다.
- **H2. 바닥 그림 미러.** `0x4663E0`을 hook한다(5인자 `ret 0x14`, 첫 6바이트 `51 53 8b 5c 24 10`, old-byte pin·rollback은 기존 hook과 같은 형식).
  패널 호출이면 원본을 부른 뒤 identity frame을 만든다. 이 writer는 rect 전체를 쓰므로 mask는 전부 1이다.
  - **폭 831 > pitch 800.** 행은 800에서 접힌다. frame은 **800×h**(호출 뒤 버퍼의 행 0..h−1, 그림의 앞 800열)로 잡는다.
    기존 `mirror_reinvoke`의 비클립 결합은 `width <= 800`을 요구하고 screen 합성으로 가므로 그대로 쓰면 안 된다. 패널 전용 경로를 둔다.
  - 자산 키는 기존과 같은 형식이다(writer, src 포인터, w, h, 원천 바이트 digest). `SYW2_G1_HD_PACK` 슬롯도 같은 키를 쓴다.
  - 패널이 아닌 세 호출(`0x45ED41`·`0x4925C8`·`0x492268` 반환)은 원본만 부른다. 미러하지 않는다.
  - hook은 program_state와 무관하게 동작한다. 바닥 그림은 로드 때(`0x441533`) 한 번 그려지고 PS3 동안 유지된다.
- **H3. 층 평면.** 논리 800×203 → HD 1600×406. `panel_expected`(합성 때의 800 값)와 `panel_covered`를 논리 픽셀마다 둔다.
  H2가 [0,0,800,h)의 모든 칸을 Scale2x 블록으로 채우고 covered=1, expected=frame 값으로 둔다. `0xFE`는 Scale2x에서 보통 인덱스로 다룬다.
  - **키 규칙.** 논리 값 E가 키가 아닌데 블록의 subpixel이 키(`0xFE`)면 그 subpixel을 E로 바꾼다. 패널 HD는 키 subpixel을 내지 않는다.
- **H4. 전사.** `BltFast`의 source가 `*(0x0104F814)`이고 destination이 primary가 아닐 때, 원본 호출이 성공한 뒤 그 호출의 실제
  rect·좌표로 한다(상수 143·457을 쓰지 않는다). rect 안의 논리 픽셀마다 v = 잠근 패널의 800 값:
  - v == `0xFE` → screen 미러 상태를 건드리지 않는다(800 backbuffer도 그 칸은 안 바뀌었다).
  - `panel_covered` 이고 `panel_expected == v` → screen 미러에 패널 HD 블록을 복사, screen covered=1, expected=v.
  - 그 밖(미니맵 지형·점, 모르는 writer) → screen covered=0. present가 nearest로 그린다.
  present 합성(`g1_mirror2x_copy_present`)은 바꾸지 않는다. 전사 뒤 backbuffer에 얹히는 버튼·초상화는 기존 writer 미러가 그대로 덮는다.
- **H5. 패널을 대상으로 한 다른 writer.** 렌더러 버퍼가 결합된 패널 버퍼일 때 기존 A/B·지형 hook은 screen 합성을 하지 않는다
  (지금은 캐시가 아니면 screen으로 본다). 호출 수만 `panel_foreign_writer_calls`로 센다. 그 픽셀은 H4의 내용 대조가 nearest로 보낸다.
- 지키는 것: opt-in(`SYW2_G1_MIRROR2X`), 원본 함수 무변경 호출, EXE 파일 무변경, 기존 gate·임계값·validator.
- 범위 밖: 미니맵 writer hook, tinted RLE(P5-T), 다른 UI 표면(`[0x104F81C]`·`[0x104F824]`), 메뉴 화면, census 수리, GDI 텍스트.

## 3. 원천 단위에 대한 판정

lap913 handoff의 "초기화된 완성 800 화면 확대를 HD asset 구현으로 바꾸어 부르지 않는다"는 지킨다. 패널 HD의 단위는 화면이 아니라
**자산 프레임**(`fnt/pannel*.spr` 한 장)이다. 합성 전에 그 프레임을 Scale2x하고, 자산 키로 HD 팩 교체가 된다. 그 위의 버튼·초상화·깃발은
각자의 writer 미러로 따로 간다. 미니맵은 원천 그림이 없는 부류다(W70 §3-1의 "원천 그림 없음", 분류 확정은 lap911 §2-3 그대로 뒤).

## 4. work P5-H — 다음 work 1 lap

### 4.1 순서

1. **RED 먼저(게임 실행 없음, host gcc — `tests/test_g1_mirror2x.py` fixture 방식).**
   ① 831×h RLE를 pitch 800 버퍼에 그린 뒤 frame 800×h가 디코드의 앞 800열과 같다. ② 키 규칙: E가 키가 아닌 블록에 키 subpixel이 없다.
   ③ 전사: v가 키인 칸은 screen 상태 불변, expected와 다른 칸은 covered=0, 같은 칸은 HD 블록. ④ 반환 주소가 패널 4곳이 아니면 층을 건드리지 않는다.
   ⑤ 결합 불일치(포인터나 pitch가 다름) → `unbound`, screen 상태 불변.
2. **구현.** §2 H1~H5.
3. **fresh pair GREEN → B′ 2 pair → C 3 pair.** 순서와 합격식은 P4c-W(lap907)와 같다. FAIL이면 원인 추적 → 수정 → 재실행을 3회까지(PROMPT ③).
4. lap 기록 → `make lint`·`make typecheck` → `make check` 1회. 끝까지 기다리지 못할 실행은 시작하지 않는다.

### 4.2 사전 등록 대조 (trace에 남길 값)

- **PH-a.** HUD 전사가 있은 PS3 present 전부에서 패널 `bound`. `unbound` 0.
- **PH-b.** save006에서 패널 `0x4663E0` 호출의 `(w,h)` = `(831,143)`이고 frame 800×143의 SHA256이
  `f649fe68a8f9a71b9e451c01cb5b0a1d79fbb06607cc8d566d3d30d108b66000`(오프라인 pannelj 디코드)이다.
  **다르면 HOLD** — 귀속이나 접힘 처리가 틀린 것이다. (조선 800×163 `c7aaf198…9927`, 명 800×160 `0137064a…bd50`.)
- **PH-c.** 유효 coverage `(covered − stale)/480000` p50이 0.692에서 **0.82~0.86**으로 오른다
  (원본 lane 범주 10 p50 70,637.5 + unknown 7,251 ≈ +0.162). 0.80 미만이면 단계별 수(패널 covered·전사된 블록·내용 불일치 칸)를 적고 middle로 넘긴다.
- **PH-d.** `panel_key_subpixels_emitted == 0`, `panel_foreign_writer_calls`는 보고만 한다.

### 4.3 합격

- `PASS(work)`: RED→GREEN, PH-a·PH-b 성립, V1 위반 0, V2·V2s·V2q 5 tag, Scale2x validator, B′ 2 pair(상태·입력 parity),
  C 3 pair(ratio ≥ 0.95, p95 ≤ baseline + 16ms), PH-c·PH-d 수치 기록, HUD 영역 1600 캡처를 직접 보고 적는다
  (키 색 얼룩 없음, 패널 구멍으로 월드가 보임, 미니맵·버튼 자리 그대로).
- 성능 FAIL이면 전사 비용부터 줄인다: 내용 대조와 결과가 같은 범위에서만(예: 행 단위 비교로 안 바뀐 행 건너뛰기). V1·내용 대조는 유지한다.
- `HOLD`: 수리 3회 뒤에도 PH-a·PH-b·화면 gate가 안 되고 원인을 설명하지 못할 때. 다음 work는 lap911 §5의 P5-T로 간다(strategy로 올리지 않는다).
- P5-H PASS는 G1 완료가 아니다. coverage 90%에는 P5-T가 더 필요하다(원본 lane 범주 6·7 p50 합 54,588.5 = 11.4%).

## 5. middle 검수 항목 (P5-H work 뒤)

1. build 입력·DLL·raw SHA, 보호 원본·save SHA, cleanup, hook pin(old bytes `51 53 8b 5c 24 10`).
2. PH-a~PH-d를 trace에서 다시 계산한다. PH-b의 SHA는 `fnt/pannelj.spr`에서 독립으로 다시 만든다.
3. V1·V2·V2s·V2q·B′·C를 raw에서 다시 계산한다. HUD 1600 캡처를 원본 캡처와 나란히 본다.
4. **승격 기준은 lap911 §6 그대로다.** 수리 대상이 분명한 구현 결함은 work로 돌린다. P단계 전환은 마일스톤 경계가 아니다.

## 6. census 계측 결함 (lap913 기록, 보류)

- `present_source_surface`가 버퍼 값을 적는 것, `surface_blt_captured`가 begin에서 오르는 것 — 둘 다 수리 대상이 분명하고 lap912 수치에 영향이 없다.
- 다음에 census를 돌리는 회차가 **먼저** 고친다. 그때 `0x4663E0`을 범주 11로 pin에 더한다. P5-H·P5-T는 census를 쓰지 않으므로 지금 고치지 않는다.

## 7. 재판정 조건

- PH-b가 수리 3회 뒤에도 다를 때(패널 그림 귀속이 틀렸다는 뜻).
- P5-H·P5-T를 다 한 뒤에도 유효 coverage가 90%에 못 미칠 때(남은 면적의 분류와 함께).
- 제품 코드·실행 증거가 늘지 않은 회차가 lap913·914로 연속 2회다. 다음 회차는 반드시 work 실행이다.

## 8. 범위 밖·금지

- 기준·임계값·비교 필드 완화, validator 조건 삭제, 기존 raw·map·PNG·golden·안전핀 수정, 원본·참고 저장소 쓰기, EXE 파일 패치, 커밋.
- 패널 버퍼를 크기(800×203)·순서로 고르는 것. 전사 rect를 상수로 박는 것.
- G2/G5·G3/G4 재개, 개인 세션 runtime 접촉.

## 9. 재현

- `cd /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap914_strategy_review && <repo>/.venv/bin/python recalculate.py`
- `recalculate.py` SHA256 `17c88e573368319b45b28425146ec980cffc8302b82e0d5ae1efccd57a91cc71`,
  `recalculation.json` SHA256 `f9d51b0857ba0e0d7b43095d1e61c17acaeb0147d8c142e8eb888d428ff458d7`,
  `render_panel.py` SHA256 `4bd00730b1e033df78212ce7aae9e55363f73cdfeabffeee4fed5c222b1a612a`,
  `pannelj_decoded_vs_selection_hud.png` SHA256 `5df1df081e5c3899c2b2626363395d7a8130ef4fa9bde17c846998794620e188`.
- 입력 13개(census map·raw·trace·probe-result·PNG 4장, `pannel{k,j,c}.spr`, 원본 EXE, lap counter)의 SHA256은 `recalculation.json`의
  `input_sha256`, 계산 전후 변화 0(`read_audit_changed: []`). 디스어셈블은 `exe_disasm.txt`(objdump 출력, 원본은 읽기만).
