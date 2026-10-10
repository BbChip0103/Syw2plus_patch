# 2026-10-07 | lap1105 | G1 middle — 기준2 HD coverage 현행 소스 재집계 + H-P35(불러오기 화면 HD 경로) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: STATUS "다음 한 가지"(G1 다음 work 가설 1개 사전등록), lap1104 기록 §다음, lap819 G1 합격 기준안 §3, lap954 기준2 첫 집계. INBOX 새 지시 없음, APPROVALS 새 반려 없음, `loop/STOP` 없음.
- `loop/ESCALATE_SOL`: lap1104 middle → **root** 전달문(G1 사용자 시험판 전달)이다. middle 대상이 아니므로 이번 회차는 내용을 바꾸지도 지우지도 않았다. root 처리 대기로 남는다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: lap1097 v1·v2 = 비합성 save000(index 1), v3·v4 = 비합성 save006(index 7). 활성 8인 증명 아님.

## 1. 기준2·3 재집계 (기존 raw, 새 실행 아님)

- 근거 raw는 lap1097 v1~v4 후보 lane `trace_raw.jsonl`이다(SHA16 `7b4989ed`·`7a52851f`·`31b8adad`·`4ee92aa6`). 네 run의 bridge `g1_mirror2x.c`가 모두 `2dc25e1b64606554`이고 현재 트리와 같다. 즉 미러 source-matched다. 그 뒤 바뀐 `direct_draw_trace.c`(lap1101)·`inmm_stub.c`(lap1103)는 로그 경로와 unit tick 기록만 건드리므로 coverage 계산에는 영향이 없다.
- 식은 lap954와 같다. present별 HD = `(covered_pixels − stale_pixels) / 480,000`. 분모에서 아무것도 빼지 않으므로 보수적이다.
- 스크립트: 공유 temp `20261007_lap1105_middle_review/crit2_lap1105.py`(`709b33a6…4458`) → `crit2_lap1105.json`(`85a604c6…96e0`). 새로 작성했고 work·제품 helper는 쓰지 않았다.

| run(fixture) | 상태 | present | HD min | p50 | ≥90% 비율 | V1 outside max | stale max | 경과 p95 |
|---|---|---|---|---|---|---|---|---|
| v1 (save000) | PS9 메뉴 | 68 | 100.0% | 100.0% | 1.0 | 0 | 0 | 15ms |
| | **PS35 불러오기** | 96 | **9.375%** | 9.419% | **0** | 0 | 434,787(첫 present) | 10ms |
| | PS3 게임 | 299 | 98.604% | 98.623% | 1.0 | 0 | 2 | 8ms |
| v2 (save000) | PS9 / PS35 / PS3 | 74 / 101 / 299 | 100.0 / **9.375** / 98.604% | 100.0 / 9.419 / 98.623% | 1 / **0** / 1 | 0 | 0 / 434,787 / 2 | 13 / 10 / 7ms |
| v3 (save006) | PS9 / PS35 / PS3 | 66 / 312 / 1,178 | 100.0 / **9.433** / 99.263% | 100.0 / 9.491 / 99.318% | 1 / **0** / 1 | 0 | 0 / 434,720 / 293 | 16 / 9 / 7ms |
| v4 (save006) | PS9 / PS35 / PS3 | 70 / 348 / 1,179 | 100.0 / **9.433** / 99.289% | 100.0 / 9.491 / 99.319% | 1 / **0** / 1 | 0 | 0 / 434,720 / 2 | 14 / 8 / 7ms |

- **기준2(lap819 §3-2) — 현행 소스 기술 PASS(partial).** "PS3 save006 장면과 두 번째 장면(메뉴 PS9 또는 다른 save)"에서 HD coverage가 ≥90%다. PS3 save006은 모든 present에서 99.26% 이상, PS9 메뉴는 4/4 run 100%, 다른 save인 save000 PS3은 98.60% 이상이다. lap954가 남긴 통계량 해석 문제("모든 present" 대 p50)는 이번 값에서는 생기지 않는다. 가장 엄격한 해석(모든 present)으로도 통과한다. 명시 잔여 ≤5%는 lap1001 이후 고정 카메라 steady stale 0으로 유지된다. 사용자 합격이 아니다.
- **기준3(V1) PASS(기술):** `hd_mask_outside_diff_subpixels`가 네 run, 모든 상태에서 0이다.
- **새 근거 — PS35(불러오기 슬롯 화면)는 HD 경로가 없다.** 모든 run에서 HD가 9.4%이고, 화면 약 90.6%가 800 버퍼의 nearest 확대로 그려진다. PS35 동안 `menu_copy_calls`는 늘지 않는다(v3 66, v1 68 고정). 미러가 HD로 덮는 메뉴 경로는 `transfer_block_copy_to_screen`(`g1_mirror2x.c:1394`)뿐인데, 이 경로는 `0x466280`이 정확히 `(0,0,800,600)`이고 캐시·패널이 아닌 source일 때만 동작한다. 첫 PS35 present의 stale 434.7k는 PS9 메뉴 배경이 덮여 있던 화면이 바뀐 결과다. 그다음 present부터 covered는 45k(버튼·글자 primitive)로 떨어진다. 틀린 픽셀은 없다(V1 0). 다만 사용자가 세이브를 불러올 때 반드시 지나는 화면이고, DESIGN G1의 "교체한 그림이 800×600 최종 버퍼로 축소됐다 다시 확대되는 구조는 합격 경로로 보지 않는다"에 걸린다. 기준2 원문은 이 화면을 요구하지 않는다. 그러나 "전체 HD coverage" 항목의 첫 미달 화면이다.
- 부수 관측(판정 밖): save006 PS35에는 약 35 present 간격으로 6.3k px stale이 6회 생긴다(v3 ord 69·104·139·172·210·244). save000에서는 282·19뿐이다. 깜빡이는 요소로 추정하며 UNKNOWN으로 둔다.
- 기준5(성능) 메모: trace의 `game_tick`은 ms 단위라 tick rate로 쓸 수 없다(≈1000/s). sim tick 비교는 baseline lane과 짝지어야 하므로 이번 회차에서는 새로 판정하지 않는다. lap1002·1006의 비 1.003·1.0036은 과거 소스 기준이다. 현행 PS3 경과 p95는 7~8ms다.

## 2. 판정

- 기준2·3: 현행 미러 소스로 **기술 PASS(partial)**. 근거는 기존 raw 4 run이다. 새 fresh run이 아니며 G1 마감이나 사용자 합격이 아니다.
- 다음 G1 기계 결함은 **PS35 불러오기 화면 HD 경로 부재**(HD 9.4%)로 정한다. HUD/GDI는 H-G(TextOutA 미러)와 명시 잔여로 이미 정리돼 있다. 두 번째 장면은 save000으로 충족됐다. 따라서 이 항목이 측정 가능한 남은 1순위다.

## 3. 다음 work 사전등록(Sonnet) — H-P35: 불러오기 화면(PS35) 배경 writer 귀속 → HD 미러

**가설:** PS35 배경(화면 약 434.7k px)은 `0x466280` 전체 프레임 복사가 아닌 writer가 그린다. 후보는 셋이다. (a) `0x466280`의 부분 사각형 또는 다른 source, (b) 기존 hook 밖의 다른 blitter, (c) DirectDraw `Blt`/`BltFast`. 이 writer를 귀속하고 기존 미러 패턴으로 옮기면 PS35 HD가 ≥90%가 된다.

- **P35-0 하네스(TDD):** `--census-state`의 choices에 35를 넣는다. PS35 census 창(64 present, 기존 skip 규약)이 찰 때까지 슬롯 클릭 전에 기다리는 분기를 PS9 분기(`g1_saved_scene_probe.py:3581`)와 같은 형태로 추가한다. 스텁 파서(`g1_census_contract.h:46`)는 이미 0..99를 받으므로 C 변경은 없어야 한다. 테스트 RED→GREEN, 기존 3/9 경로는 불변.
- **P35-1 귀속(census-only, save006 1회):** PS35 창에서 미러가 덮지 않은 픽셀을 writer별로 분류한다(EIP/hook 주소). **PASS = PS35 미커버 픽셀의 ≥95%가 이름 있는 writer에 귀속.** (a)이면 `transfer_block_copy_to_screen`의 전체 프레임 조건을 부분 사각형으로 최소 확장한다(캐시·패널 제외와 masked Scale2x 유지). (b)·(c)이면 기존 diff 미러 패턴(`mirror_blend_410` 등)을 따른다. 원본 old bytes 핀·원복·reject 계수를 포함한다.
- **P35-2 수리 측정:** 현행 트리 bridge, `--hd-source scale2x`로 fresh save006 full pair 2회와 save000 pair 1회를 돈다. 디스크 ≥20GiB를 확인하고, 끝나면 game 사본을 삭제한다. 식은 §1과 같고 새 임계값은 없다.
  - **PASS:** ① PS35 HD — 전환 present(PS35 index 0, 앞 화면 stale)는 따로 공개하고, index 1 이후 모든 present ≥90%(3/3 run). ② 비회귀 — PS9 min ≥99.4%, PS3 min ≥99.2%(save006)·≥98.5%(save000), PS3 마지막 40 stale 합 ≤307. ③ 모든 상태 V1 outside 0. ④ pair gate(input_effect·minimap·V2/V2s(W-1)/V2q·Scale2x·loaded) save006 2/2 PASS(save000은 fixture 한계로 기존 HOLD 허용). ⑤ 안전 7종 0, PS3 경과 p95 ≤12ms, PS35 경과 p95 ≤26ms(현재 10 + 16).
  - **FAIL:** PS35 <90% → 미달 픽셀의 writer를 공개한다. 같은 추측을 반복하지 않는다.
  - **BLOCKED / NOT_FEASIBLE:** 배경이 매 present 합성 scratch라 identity 오라클이 성립하지 않거나, 수리에 여러 모듈 재구성이 필요하면 근거·대안을 기록하고 middle로 넘긴다. 60분 또는 실패 가설 2회 규칙(PROMPT ③)을 따른다.
- 판정 밖으로 기록만 할 것: PS35 주기 stale 6.3k의 writer(census에 나오면), sim tick 비(baseline 짝).
- 공통: source를 바꾸면 lint·typecheck → 기록 freeze → `make check` 1회. 원본/참고 쓰기 금지, 커밋 금지.
- 사용자 시험판(`_inmm.dll` `94213374…`)은 다시 스테이징하지 않는다. H-P35 결과와 사용자 시험 피드백을 본 뒤 다음 middle이 재스테이징 여부를 정한다.

backlog(유지): 다른 화면 상태(타이틀·혼자하기 대기실·옵션·게임 중 저장 창·승패 화면)의 HD coverage 미측정, v3 ord 350 단발 UNKNOWN, `0x4676D0` 미러 여부, 화면 밖 `0x467410` 쓰기, throttle ord 123 writer, `0x467E60` wrap, lane 위상 경합, 진단 동반 영역.

## 4. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`·focused G1 테스트를 돌린다. 결과는 STATUS에만 쓴다.
- 전체 `make check`는 SKIP한다. 이번 변경은 문서뿐이고, source·하네스·테스트는 lap1103 full PASS(1698) 때와 같다(`g1_mirror2x.c` `2dc25e1b…`, 하네스 `0f5ab722…`).

## 다음 한 가지

work(Sonnet): §3 H-P35 — P35-0 하네스 census 35 → P35-1 귀속 → 수리 → P35-2 측정. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.
