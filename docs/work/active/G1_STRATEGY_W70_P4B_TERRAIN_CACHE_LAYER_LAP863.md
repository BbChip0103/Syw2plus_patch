# G1 W70 P4b — 지형 귀속은 유지, 스크롤 결손은 캐시 이동(memmove)이 원인: 캐시 층 미러로 수리 (lap863 strategy, 2026-10-02)

- 발행: lap863 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, effort 세션 비노출, 자동 폴백 아님).
  게임 실행0, 제품/하네스/validator source·binary 변경0, subagent0, 커밋0.
- 호출 사유: lap862 work가 P4 카드 §5.1(`<30%` 반증 분기)에 따라 `loop/ESCALATE_SOL`로 승격했다
  (보존본 `docs/history/20261002_lap863_prior_lap862_escalate_sol_archive.md`).
- 입력 근거(이 세션이 직접 읽고 재계산): lap859~862 기록, P4·W70 카드, 공유 temp
  `20261002_lap862_p4_scroll_down_fix_{r3,r4}/`의 pair·lane별 probe-result·candidate `trace_raw.jsonl`·gdb `writer-events.jsonl`,
  `20261002_lap862_p4_ps3_census/`, 현재 `tools/inmm_stub/g1_mirror2x.c`·`g1_census.c`·`tools/g1_saved_scene_probe.py`,
  보호 원본 EXE read-only disassembly. 주소·old bytes는 `analysis/memory_maps/g1_w70_p4b_terrain_cache_scroll_lap863.md`.
- 이 카드는 P4 카드(`G1_STRATEGY_W70_P4_TERRAIN_BLITTER_HD_LAP858.md`)의 **§5.1을 정정**하고 **B-5(스크롤)를 구체화**한다.
  P4 카드의 A·B-1~4·C·D와 임계값은 그대로 유효하다.

## 0. 판정 요약

1. **P4 `<30%`는 §3 귀속의 반증이 아니다. P4 `FEASIBLE` 유지.** 같은 r3/r4 raw에서 키 입력 전 고정 카메라 유효 coverage는
   68.4~70.6%(B-3 기준 55% 초과, lap859 R4 400 present p50 66.53%와 같은 수준)다. `<30%`는 카메라가 움직인 뒤에만 나온다.
   §5.1은 고정 창을 전제로 쓴 문장이었고 스크롤 창에 그대로 적용하면 결론이 틀린다. §5.1의 "다음 후보 `0x466280` 경로"도 정정한다(§2).
2. **스크롤 결손의 writer = `0x4324E0` 안의 캐시 이동 `memmove`(`0x4DB1D0`, 호출 8곳).** 지형 blitter는 화면이 아니라 고정
   캐시 `0xBA3D30`(832×512)에 그리고, 카메라가 한 칸 움직이면 원본은 캐시를 통째로 밀고 새로 드러난 띠만 다시 그린다.
   밀린 픽셀은 hook을 지나지 않으므로 미러가 따라가지 못한다. 캐시→화면은 매 프레임 `0x41BF20`의 `0x466280(0,0,832,512,캐시)`가
   복사한다. 정적 근거와 raw 대조는 §1.
3. **현 구조의 두 번째 결함: 캐시에 그린 것을 화면 평면에 즉시 적용한다.** 캐시 갱신과 캐시→화면 복사는 같은 호출에
   묶여 있지 않아(phase gate `[0xB93E00]`), 새 띠의 미러 적용이 화면 반영보다 한 present 앞선다(r3/r4 전환 present의 stale
   ≈3만 = 800×32 띠). 따라서 "화면 평면을 그 자리에서 미는" 수리와 "카메라 이동 시 전체 재그리기 강제"는 **기각**한다(§3).
4. **수리 경로 = 캐시 층 미러(P4b).** 원본의 실제 데이터 흐름을 그대로 따른다: ⓐ 캐시를 대상으로 한 blitter 결과는 캐시 층
   평면에 합성 ⓑ 캐시 `memmove`는 캐시 층 평면에 같은 이동을 적용 ⓒ `0x466280(src=캐시)` 시점에 캐시 층을 화면 평면으로 전사.
   그리기·클립·LUT 재구현 없음, 게임 메모리 쓰기 없음, EXE 파일 불변. 범위는 §4.
5. **입력 parity(DOWN lane 불일치)는 제품 비대칭으로 확정되지 않았다. 하네스 귀속이 유력하다(§5).** 스크롤 측정이 gdb
   `--terrain-trace`에 묶여 있어 두 lane 모두 gdb breakpoint 정지 아래에서 키를 받았고, baseline은 DOWN이 안 먹은 뒤 RIGHT로
   **한 lane만** 대체돼 최종 카메라가 달라졌다. 다음 work는 gdb 없는 스크롤 pair로 parity를 먼저 잰다.
6. **PS3 census(D-1)는 P4b의 선행 조건이 아니다.** 스크롤 결손 원인은 위 근거로 정해졌다. D-1은 P5 순서를 정하는 자료이며
   P4 카드 D-1 문구대로 present 맵 수집을 `program_state==3`으로 한정하는 opt-in만 허용한다(§6). PS9 맵으로 대체하지 않는다.
7. 성능 기준 W70 §3.5·Scale2x validator·legacy validator·coverage 임계값(55%/30%/0.9) **불변**.
8. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 검수·3단 사용자 승인은 그대로 남는다.

## 1. 근거

### 1.1 raw 재계산 (candidate `trace_raw.jsonl`, PS3 present, 480,000 대비)

| run | 구간 | camera | terrain 호출 증가 | covered−stale |
|---|---|---|---|---|
| r3·r4 | 키 전 6~7 present | [158,101] | 0 | 328,298~338,716 (68.4~70.6%) |
| r3 | 전환 present seq1565 | [159,102] | +128 | 314,244 (65.5%), stale 30,313 |
| r3 | 다음 present seq1566 | [159,102] | 0 | 104,266 (21.7%), **stale 210,468** |
| r3 | 전환 뒤 30 present p50 | | | 103,669 (21.60%) — 기록과 일치 |
| r4 | seq1583 → 1584 → 1585 | [159,102]→[160,103] | +128, +134 | 315,087 → 103,513(stale 240,644) → 61,286(stale 42,632) |
| r4 | 전환 뒤 30 present p50 | | | 60,971 (12.70%) — 기록과 일치 |

- 한 칸 이동에 blitter 호출은 128회뿐이다(전체 재그리기는 709회). 그런데 한 present 뒤 21만 픽셀이 한꺼번에 값이 달라진다.
  → 화면의 지형 대부분이 hook 밖 경로로 바뀌었다.
- 그 사이 `hd_mask_outside_diff_subpixels`는 계속 0이다. 틀린 HD는 없고, 무효화된 픽셀은 nearest로 안전하게 떨어졌다.
- 이후 coverage가 회복되지 않는다(약 1,900 present 동안 r3 19~25%, r4 11~20%). 원본이 스크롤 뒤 전체를 다시 그리지 않기 때문이다.
- p50은 probe 집계값(30개 중 아래쪽 가운데 값)이다. 두 가운데 값의 평균으로는 103,669.5 / 60,972.5로 판정은 같다.
- pair/raw SHA는 lap862 기록·ESCALATE와 일치(이번 lap 재해시).

### 1.2 정적 (보호 원본 `b56986e0…`, 이번 lap objdump)

- `0x4324E0`: `0x464E00(0xBA3D30,832,512)`로 렌더러를 캐시에 묶고 clip `(0,0,831,511)`. `[this+0x597D]`(카메라 이동) 경로에서
  이전 카메라 `[0x1057968]`/`[0x105796A]`와 비교해 8가지 이동마다 `call 0x4DB1D0`(memmove)로 캐시를 민다.
  DOWN=(+1,+1)은 `0x432A2D`: `memmove(0xBA3D30, 0xBAA530, 0x61800)` = 32행 위로. 이후 dirty 블록 한 줄만 표시·재그리기.
- `0x41BF20`(`0x424622`에서 호출): `0x41BF57`에서 `0x466280(0,0,832,512,0xBA3D30)`. 캐시→전장 surface (0,0) 복사.
- `0x4245D0`: `0x41C770`(캐시 갱신 포함)을 먼저 부르고, `[0xB93E00]==0`일 때만 `0x41BF20`을 부른 뒤 phase를 올리고 반환.
- gdb trace: `asset_blitter_call` 전부(r3 1061·969, r4 1186·1040) renderer buffer `0xba3d30`·stride 832.

## 2. P4 카드 §5.1 정정

- 원문: "5종 hook이 활성인데 B-3 coverage p50 < 30%면 §3의 귀속이 틀린 것 … 다음 후보 `0x466280` block_copy 경로".
- 정정: 이 반증 조건은 **고정 카메라 창(B-3)에만** 적용한다. 스크롤 창(B-5)의 미달은 §7의 규칙을 따른다.
  `0x466280`은 지형을 "그리는" 후보가 아니라 캐시→화면 **전사 지점**이다. 지형 픽셀의 생성 writer는 그대로 blitter 5종이다.

## 3. 기각한 대안

| 대안 | 기각 사유 |
|---|---|
| 화면 평면(`g_mirror`/`g_covered`/`g_expected_snapshot`)을 memmove 시점에 그대로 이동 | 복사 지연 때문에 이동 직후 present는 아직 옛 화면이다 → 평면 전체가 불일치로 무효화된다 |
| 카메라 이동 시 `+0x597C`를 써서 전체 재그리기 강제 | 게임 메모리 쓰기이고, 같은 지연으로 재그린 결과가 그 present에서 무효화된다. 스크롤마다 709회 재그리기 비용도 든다 |
| `0x4DB1D0` 진입 hook 없이 카메라 차이에서 이동량을 계산 | 원본 분기표를 재구현하게 된다. 인자 `(dst,src,n)`를 그대로 따르는 쪽이 관측만으로 끝난다 |
| PS3 census를 먼저 하고 판단 | 원인이 이미 raw+정적으로 정해졌다. 문서 회차만 늘린다(PROMPT ③) |

## 4. P4b work 범위 (한 lap, 구현→빌드→격리 실행→원인 수리 반복 최대 3회)

공통: 기본 OFF opt-in(기존 mirror/HD env 아래에서만 동작, env는 `initialize_environment`에서 latch), EXE 파일 불변, old bytes
대조 후 설치·불일치 시 전체 rollback, save006 same-save fresh pair, private 사본·prefix·Xvfb, 실행 후 game 사본 삭제,
기존 raw 덮어쓰기 금지. 새 코드는 새 파일 권장(`g1_mirror2x.c` 1364줄).

### A. 캐시 층 미러 (수리 본체)
1. **층 평면:** 캐시 논리 832×512에 대응하는 HD 1664×1024, covered 832×512, expected 832×512. 폭은 800이 아니라 **832**다
   (좌우 64px 이동이 800~831열을 화면 안으로 들여온다).
2. **blitter 경로 분기:** 지형 hook 진입 시 렌더러 원래 버퍼(`+0x1514`)가 `0xBA3D30`이면 합성 대상을 층 평면으로 한다
   (bounds 832×512). 다른 버퍼면 기존 경로 그대로. sentinel 재호출·키·Scale2x·clip replay는 손대지 않는다.
3. **이동 미러:** memory map의 8개 호출 지점(`E8 rel32`, old bytes 표 참조)을 wrapper로 돌린다. wrapper는 원본 `0x4DB1D0`을
   호출한 뒤, `dst`·`src`가 모두 캐시 범위 `[0xBA3D30, 0xC0BD30)`일 때 층 평면 셋에 같은 이동을 적용한다.
   지원 형태는 두 가지뿐이다: ⓐ 행 전체 단위(`dx=0`, 시작·길이가 832의 배수) ⓑ 한 행 안에서 시작·끝나는 run.
   그 밖의 인자는 **dst 범위의 층 covered를 지우고**(→nearest) `layer_move_unsupported`로 센다. 틀린 HD를 만들지 않는다.
   (대안: `0x4DB1D0` 진입 hook + 범위 필터. 호출 지점 방식이 막히면 허용하되 어느 쪽을 썼는지 기록한다.)
4. **전사:** `0x466280` hook(5인자, `ret 0x14`, old bytes는 `g1_census.c`에 고정된 값)에서 `src==0xBA3D30`일 때만, 원본 호출
   **뒤에** 목적지 사각형과 화면 평면의 교집합(x<800, y<512)에 대해 층 → 화면 평면으로 HD·covered·expected를 복사한다.
   층 covered가 0인 픽셀은 화면 covered도 0으로 만든다. 값 검증은 기존 present 검사(`expected==800[p]`)가 그대로 맡는다
   (캐시의 hook 밖 writer — `0x465FC0` 띠 지우기 등 — 는 여기서 걸러진다). `src`가 캐시가 아니면 원본만 호출한다.
5. 스프라이트 hook 2종(`0x466D50`,`0x4664D0`)과 present 합성·validator 입력 필드의 의미는 바꾸지 않는다. 전사 뒤 hook 밖
   writer가 덮은 지형 픽셀은 매 present stale로 세어질 수 있다. 유효 coverage는 계속 `covered−stale`이다.
6. raw 계수 추가: `layer_compose_calls`, `layer_move_calls`/`layer_move_bytes`/`layer_move_unsupported`,
   `layer_transfer_calls`, 층 covered 픽셀 수. 기존 필드는 이름·의미 유지.
7. Fast 회귀 가드: 8개 호출 지점 주소·old bytes, `0x466280` 인자 수, 이동 함수의 순수 로직 단위 테스트(행 전체/행 내부/
   미지원→covered 지움, 겹침 방향 양쪽).
8. 금지: EXE 패치, 게임 메모리 쓰기(dirty flag 포함), validator·임계값 변경, 그리기/클립/LUT/이동량 분기표 재구현, 새 의존성,
   G2/G5 source·`local/runtime/g2_*`·`*g5_esl2608*` 접촉, P5(HUD/tinted) 코드, 커밋.

### B'. 배관 pair (`--hd-source scale2x`, **gdb 없음**) — 사전 등록 기대값
1. 설치: 기존 7 hook + 이동 8지점 + `0x466280`. crash 0, `scene_state_equal`, source unchanged, cleanup.
2. Scale2x validator `PASS`(무수정). outside diff 0, palette 위반 0, per-present 부등식, lookup miss/invalid 0.
3. 고정 카메라: 유효 coverage p50 ≥ 55%(264,000), 지속성 마지막 20 ≥ 첫 20 × 0.9 (P4 카드 B-3·B-4 그대로).
4. **스크롤 DOWN 1칸**(whole-buffer 이동 경로): 카메라 변화 뒤 30 present p50 ≥ 264,000 **그리고** ≥ 키 전 p50 × 0.9,
   그 사이 outside diff 0. `layer_move_calls ≥ 1`, `layer_move_unsupported = 0`, `layer_transfer_calls > 0`.
5. **스크롤 RIGHT 1칸**(행 단위 이동 경로, 512회 호출): 4와 같은 기준. 두 경로는 코드가 다르므로 둘 다 필요하다.
6. 입력 parity(§5)가 같은 pair에서 PASS.

### C·D
P4 카드 C(fresh 3 pair, 계측 OFF, ratio ≥0.95·p95 ≤ baseline+16ms)와 D-1·D-2 그대로. C는 B' PASS 뒤에만, P5는 D-1 뒤에만 시작한다.

## 5. 입력 parity — 판정과 하네스 수리 범위

- 관측(lane별 probe-result 직접 열람): baseline DOWN은 r3 keydown→keyup 1ms·카메라 불변, r4 keyup만 수신·카메라 불변.
  같은 baseline lane의 두 번째 키 RIGHT는 정상 스크롤(r3 한 칸, r4 204ms·세 칸). candidate DOWN은 127ms·한 칸 / 250ms·두 칸.
  요청 hold는 60ms / 150ms였다.
- 해석: baseline도 키 스크롤이 된다. 실패한 것은 **장면 로드 직후 첫 키**이고, 이동량은 게임이 본 hold 시간에 비례한다.
  스크롤 경로가 `terrain_trace`(gdb 20개 target + asset breakpoint)에 묶여 있어 두 lane 모두 정지 구간에서 키를 받았다
  (로드 직후 blitter breakpoint cluster: baseline 709건 0.5초, candidate 837~971건 1.0~1.1초). 원인 확정은 아니다(가설).
- 하네스 결함 1건은 확정이다: DOWN 실패 시 RIGHT로 대체하는 fallback이 **한 lane에서만** 발동해 r3 최종 카메라가
  baseline `[159,100]` / candidate `[159,102]`로 갈렸다.
- 수리 범위(work, `tools/g1_saved_scene_probe.py`·테스트만):
  1. 스크롤 측정을 gdb `--terrain-trace`와 분리한다. 스크롤 pair는 gdb 없이 DLL receiver 계측만 쓴다.
  2. 키는 로드 뒤 정착 barrier(연속 PS3 present에서 terrain 호출 수 불변) 뒤에 보낸다.
  3. hold는 폐루프: keydown → 카메라가 목표 칸에 도달하면 keyup(시간 상한 있음). 벽시계 hold 고정 금지.
  4. lane별 fallback 금지. 같은 키 순서를 두 lane에 쓰고, 한 lane이라도 키가 안 먹으면 그 pair는 `INVALID`.
- **parity PASS:** 두 lane 모두 같은 키의 WM_KEYDOWN·WM_KEYUP 수신, 같은 키 순서 뒤 최종 카메라 동일, 스크롤 뒤
  `scene_state_equal`. gdb 없는 pair에서 3회 수리 뒤에도 lane이 갈리고 원인을 설명 못 하면 그때 승격한다(제품 입력 결함 후보).

## 6. PS3 census(D-1) 범위

- 허용: present 맵 snapshot을 `program_state==3`일 때만 찍는 opt-in(초기화에서 latch). `CENSUS_PRESENT_LIMIT 64`와 writer별
  event cap 32는 그대로 둔다(비율은 last-writer 맵에서 나온다).
- census 표에 blitter 5종을 넣고, `0x466280(src=캐시)`는 **"지형 캐시 전사"**로 따로 센다. PS3 화면에서 지형 영역의 마지막
  writer는 blitter가 아니라 이 전사이므로, 따로 세지 않으면 지형이 block_copy로만 보인다.
- 기존 raw에서 PS3 last-writer를 뽑을 합법적 경로는 없다(candidate trace에는 writer별 픽셀 맵이 없다). PS9 맵 대체 금지 유지.

## 7. 판정·정지 규칙

1. B'-3(고정) p50 < 30%: P4 카드 §5.1 그대로 귀속 반증 → strategy.
2. B'-4/5(스크롤)에서 층 이동·전사가 실제로 돌았는데(`layer_move_calls≥1`, `unsupported=0`, `layer_transfer_calls>0`)
   30 present p50 < 30%: 이 카드의 모델(§0-2~4)이 틀린 것이다. 수리를 더 하지 말고 계수와 present 열을 남겨 strategy로.
3. 30% ≤ p50 < 55% 또는 `unsupported>0`: 원인을 raw로 적고 같은 카드로 work 1회 추가(총 2 work lap). 그래도 미달이면 strategy.
4. 성능 FAIL: P4 카드 §5-3 순서 그대로. 추가로 전사는 행 단위 복사로 한정한다(픽셀당 분기 금지).
5. state/scene hash 불일치·크래시: 즉시 승격.
6. B' PASS → middle이 직접 PASS/HOLD 판정(P단계는 마일스톤 경계가 아니다, lap858 §0-2). PASS면 다음 work가 C → D.

### middle 검수 조건 (work PASS 주장 시)
- 8개 호출 지점·`0x466280` old bytes와 rollback 열람, wrapper가 `(dst,src,n)`만 따르는지, 미지원 인자→covered 지움 경로,
  층 폭 832, 전사가 원본 호출 뒤인지, gdb 없는 pair인지, lane별 키 순서 동일·최종 카메라 동일, DOWN·RIGHT 30 present p50과
  키 전 p50 독립 재계산, validator 무수정, source unchanged·cleanup, DLL/raw/pair SHA·build 입력.

## 8. 남은 위험

- §1.2는 정적 판독이고 복사 지연의 정확한 phase 순서는 읽지 않았다. 층 모델은 지연 길이에 의존하지 않도록 설계했지만
  전사 시점(`0x466280` 뒤)이 스프라이트 그리기보다 항상 앞선다는 것은 실행으로 확인해야 한다(뒤바뀌면 스프라이트 HD가 지워진다).
- 8개 외의 카메라 변화(미니맵 점프·큰 이동, `0x432F82` 이하)와 지도 가장자리 분기는 읽지 않았다. 전체 재그리기로 가면
  blitter hook이 층을 다시 채우므로 안전하지만 미확인이다.
- 전사는 매 프레임 약 2.4MB 복사다. 현재 p95 여유는 +5ms/한도 +16ms(고정 카메라). 스크롤 중 성능은 측정된 적이 없다(D-2).
- 현재 고정 카메라 coverage 일부는 "같은 값이 우연히 다시 보인 픽셀"을 포함할 수 있다. 층 전사는 이 의존을 없애지만 그만큼
  고정 coverage가 내려갈 수 있다. 55% 아래로 가면 §7-3이다.
- 측정은 Xvfb/Wine·save006 한 장면이다. 두 번째 장면, HUD/tinted/GDI, 전체 HD coverage ≥90%, 사용자 3단 승인은 미충족이다.
- minimap/production `UNKNOWN(original parity)` 유지.
