# 2026-10-07 | lap1147 | G1 work — H-SC1: PS20 브리핑 stale 위치·writer 귀속 → 수리 시도 반증 → BLOCKED

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 하네스·C 진단 옵트인·테스트 변경 있음, 제품 동작 변경 0(수리 시도는 되돌림), 커밋 0.
- 입력: STATUS "다음 한 가지"(work H-SC1), lap1146 기록 §4 사양. INBOX 새 사용자 지시 없음(마지막 = lap1146 처리 메모), APPROVALS 새 반려·사용자 시험 결과 없음(lap1136 재요청 대기), `loop/STOP`·`loop/ESCALATE_SOL` 없음(시작 시 확인).
- 가설: PS20 stale은 단일 미후킹 writer(또는 기존 미러 계열 DDraw 호출)라서 diff 미러로 PS20 정착 HD min ≥98.6·<90 0%를 만들 수 있다.
- 사전등록 PASS/FAIL: SC1-1 위치·SC1-2 writer 귀속·SC1-3 켬2/끔1 수리. 귀속 불가·wined3d 스레드·writer 여러 개 = BLOCKED(수리 없음).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945…`(직접 재계산 MATCH, 읽기만), 모든 run `source_unchanged` true·cleanup ok.
- fixture: 없음(타이틀에서 시작, 비합성): `--hd-source scale2x --title-button scenario --scenario-start --scenario-play --scenario-briefing-dwell 65`.

## 0. 변경 파일(최종 트리, 모두 uncommitted; 같은 파일들에 lap1099~1146 미커밋 변경이 이미 있다)

- `tools/inmm_stub/g1_stale_mask.h`(`d2e017bfdcb9`)·`tools/inmm_stub/g1_screen_watch.h`(`8146afe12eaf`): SC1-0 파서에 정확한 값 `"20"`→PS20 추가(그 밖 값은 PS3 그대로), 그 밖에 `g1_screen_watch_call_from_parse`(SC1-2).
- `tools/inmm_stub/g1_screen_watch.c`(`66bd2908915a`): `SYW2_G1_SCREEN_WATCH_CALL_FROM=<present>` — 그 watch present 이전의 ddraw 호출 표 기록 생략(진단 옵트인, 기본 0 = 기존 동작). 사유: 호출 표는 48칸인데 PS20 글자줄 BltFast(행마다 키가 다름)가 먼저 채워 overflow 45,240이 됐다.
- `tools/g1_saved_scene_probe.py`(`000badc1e9f6`): `--stale-mask-state`·`--screen-watch-state` choices에 20, `--screen-watch-call-from N`, `--title-button` 분기가 `stale_mask`·`stale_mask_state`·`screen_watch_call_from`을 후보 lane에 전달하고 요약에 `stale_mask` 포함.
- 테스트: `tests/test_g1_screen_watch.py`(`68c5dde2fb75`)·`test_g1_mirror2x.py`(`e284b0fb4be1`)·`test_g1_result_screen.py`(`be6c4989f894`) — 파서 `20`/`200`/`02`, choices, title-button 분기 stale-mask 배선, call-from 파서·게이트·CLI 배선(RED→GREEN, `.venv` 기준 g1 관련 6개 파일 326 passed).
- 되돌린 수리 시도(최종 트리에 없음): PS20 BltFast overlay 미러. `direct_draw_trace.c` `0de218aa84d6`·`g1_mirror2x.c` `1b056280f662`·`g1_mirror2x.h` `0fc9cc4b1edf`·`test_g1_rect_fill.py` `d8e4430db905`가 lap1141 기록 해시와 일치(정확한 되돌림 확인), 되돌린 뒤 mingw 빌드 성공.

## 1. SC1-1 위치 (run `m1`, 켬 기본, `--stale-mask 700,1750,2650,3350,4350 --stale-mask-state 20`)

PS20 정착 present 4,643: HD min 89.43·p50 98.217·<98.6 66.6%·<90 7.3%(lap1145 r1과 같은 값 = 결정적). 새 스크립트 `scripts/locate_sc1.py`로 stale 연결 성분 분석(5 dump, 정착 present 모두 covered 480,000):

| ordinal(≈시각) | stale | 성분 |
|---|---|---|
| 700 (≈10초) | 7,784 | 글자 크기 소성분 522개(≤187 px, 높이 ≈9)·bbox x240..555·y77..462 — 본문 글자줄 |
| 1750 (≈25초) | 8,861 | 같은 글자줄 500개 |
| 2650 (≈38초) | 1,286 | 글자줄 아래쪽(y389..462) 소성분만 |
| 3350 (≈48초) | 18,087 | **초상화 1 상자 15,941**(x29..193·y49..174) + 글자 |
| 4350 (≈62초) | 50,735 | **초상화 3 상자 16,132(x630..797·y57..173)·15,949(왼쪽 위)·15,577(x29..193·y211..334)** + 글자 195 이하 |

- 90초 전체 stale의 약 94%(48k/50.7k)는 초상화 3칸(스택: 열릴 때마다 한 칸씩 추가, 한 번 stale이 되면 끝까지 유지), 나머지는 본문 글자 소성분.
- 캡처 열람: r3와 같은 구도(제1장 노량해전 브리핑 정상). 내용·색 오류 없음, 화질(nearest)만.

## 2. SC1-2 writer 귀속 (run `w1`·`w2`·`w3`·`w4`, 표본 3개 = 초상화 안 (111,111)·(713,115)·(111,272))

- **w1(call-from 없음):** screen watch 15,515 hit. EIP 두 종류뿐. ① `0x004662DE`(캐시→화면 `0x466280`, **게임 스레드 tid 280**, 매 present, 값 249 = 배경색) ② **`0x741B99CF` = `wined3d.dll`(base `0x740E0000`), 별도 스레드 tid 288** — 표본별 첫 hit present: 초상화 1 약 2,740~2,885·초상화 2 약 2,927~3,114·초상화 3 약 3,756~3,935(= 초상화 상자가 stale이 되는 시점), 이후 **매 present** 표본 한 칸씩 값 118/66(초상화 화소)을 다시 쓴다. 호출 스택은 비어 있다(스레드 시작부, `st` 상단 0).
- w1 호출 표는 overflow 45,240(글자줄 BltFast `0x4D4025`가 칸을 다 채움).
- **w2(`--screen-watch-call-from 2800`):** overflow 0, 새 5행: 매 present 주 `BltFast`(호출처 `0x0049273F`, 뒤 버퍼 `[0xE5D438]` → primary) 외에 **`BltFast(dest=800×600 시스템메모리 표면, 호출처 `0x004D41E6` 초상화 xy (26,49)·(630,49), 소스 사각형 NULL, flags 0x11=SRCCOLORKEY|WAIT)`와 `0x004D3BFA`(본문 패널 xy (240,216/207))**, 각 초상화당 2~3회뿐. 목적지 표면 `[0x104F824]`(호출처 `0x4D41D5`~`0x4D41E3`에서 `mov eax,ds:0x104f824` 전역 확인).
- **w3(`--screen-watch-cache`, 지형 캐시 0xBA3D30 감시):** PS20 동안 캐시 표본 쓰기 0(PS3 진입 present 4,303에서만) → 캐시 레이어 경유 아님.
- **w4(진단 임시 코드):** BltFast 목적지 `[0x104F824]`의 잠금 포인터 `0x03028F40`·pitch 800 ≠ 감시한 렌더러 버퍼 `0x04470030`(pitch 1600) → **목적지는 렌더러 버퍼와 별개 표면**. 초상화 BltFast(170×128)·본문 패널(357×248)이 그 표면에 그려지고, 화면(뒤 버퍼)에는 wined3d 스레드가 매 present 초상화 화소를 써 준다.
- 정적: 브리핑 그리기 구간 `0x4D3A00..0x4D4C00`은 `IDirectDrawSurface7` vtable `+0x44`(**GetDC**)·`+0x68`(**ReleaseDC**)를 사용(+0x1c BltFast 5회, +0x14 Blt 1회) → 글자·일부 합성이 GDI DC 경로일 가능성(UNKNOWN, 호출 미계측).
- **귀속 판정: BLOCKED(귀속 불가).** 화면 stale writer = `wined3d.dll` CS 스레드이며, 그 쓰기를 유발하는 게임 쪽 호출(매 present 재실행)을 계측으로 특정하지 못했다. BltFast 목적지 표면은 렌더러 버퍼와 다르고, 그 표면 → 뒤 버퍼 이동 경로가 hook한 ddraw 호출에 보이지 않는다(GetDC/ReleaseDC·GDI 경로 미계측).

## 3. SC1-3 수리 시도 — BltFast overlay 미러 PS20 확장 (반증)

가설: PS20 초상화 BltFast(NULL 소스 사각형)를 기존 overlay diff 미러(PS3 한정 게이트)로 PS20에도 적용하면 stale이 풀린다. 구현: 게이트에 PS20 허용(env `SYW2_G1_BRIEFING_OVERLAY=0`으로 끔)·NULL 소스 사각형은 소스 표면 전체로 대체(PS20 한정). 실행 `on1`(켬):
- overlay 계수 mirrored_calls **5**·mirrored_pixels **48,032**(= 초상화 3개 변경 화소 합과 일치)·rejects 45,902(글자줄 폭 326>320 상한 등), 즉 **미러는 동작**.
- 그러나 PS20 정착 HD **min 89.43 불변·p50 98.220·<98.6 64.8%·<90 6.7%**(m1: 66.6%/7.3%), ordinal 4350 stale 50,735 **동일**, 초상화 3 상자 성분 크기도 동일 → **stale 미해소 = 가설 반증**. 목적지 표면의 변경 화소를 expected로 넣어도 실제 화면 화소와 어긋나므로 화면 쪽 값은 그 표면 내용이 아니다(경로 불명).
- 조치: 이득 없이 글자줄 BltFast 약 4.5만 건에 잠금 비용만 더하므로 **코드·테스트·진단(overlay dest 노트) 전부 되돌림**(위 해시 일치). 제품 동작 변경 0.

## 4. 판정·한계

- **H-SC1 = `BLOCKED`**(SC1-0 PASS·SC1-1 위치 PASS·SC1-2 귀속 BLOCKED·SC1-3 수리 시도 반증·되돌림). 사전등록 판정표대로 위치·후보만 남기고 수리 없음.
- PS20 브리핑 stale은 내용·색 오류 없는 nearest 화질(저하 부분 면적 ≈10%, 초상화 3칸 + 본문 글자)이고 H-SC0의 `FAIL(화질, 내용 정상)`은 그대로다. PS9·PS15 100·PS3 99.686 비회귀(최종 트리 변경은 진단 옵트인만이므로 동작 비교 불필요, `on1`·`m1` PS3 99.686·PS15 100 동일).
- 위험 공개: 스크립트의 재계산은 candidate trace(`mirror2x_present` 행의 covered/stale)이며 캡처 비교는 하지 않았다. 8192 trace 상한: 체류 65초로 dropped 0.
- 안전 7종·fallback 0·success min 1·cleanup ok·`source_unchanged` true(m1·on1·w2). run 종료 상태 열은 lap1145와 같은 PS150 1홉 표본 차(`state_sequences_match` false), 두 lane 모두 마지막 PS 일치.

## 5. 산출물

공유 temp `20261007_lap1147_work_hsc1/`: `m1`(`title-button-result.json` `5ae297b4932c`, `candidate/stale_mask.bin` `339043311ba2`), `w1`(`ac0baae09f94`)·`w2`(`2f015c7d46c6`, `screen_watch.jsonl` `2e29090e5e98`)·`w3`(`42a093207cc8`)·`w4`(`ea2b367dc821`, `screen_watch.jsonl` `91a7c9a39f20`, 임시 진단 포함)·`on1`(`ec1f2e2fa07b`, `stale_mask.bin` `cb87e07c78e6`), `scripts/`(`run_sc1.sh` `da3cc2f53b3d`·`locate_sc1.py` `90db9a262d79`·`sc1_recalc.py` `22e342e3128e`·`sc1_summary.py` `69db5060657e`). 로그 `logs/gates/lap1147-sc1-<run>.{log,exit}`(exit 전부 0). 각 run 뒤 `game` 사본 삭제(디스크 79GiB 여유).

## 다음 행동

middle(Opus): ① raw 독립 재계산(m1 stale 위치·w2 호출 표·w4 목적지 포인터·on1 반증) ② 결정: (A) PS20 브리핑 stale을 명시 잔여(화질 범주, 시각 심각도 낮음)로 두고 다른 G1 장면으로 진행, 또는 (B) work로 **GetDC/ReleaseDC·GDI(BitBlt 계열) 호출 계측**(vtable `+0x44/+0x68` 호출 표, 목적지 표면 구분)을 한 회차 더 — writer가 GDI DC 경로인지 확인. 권고: B를 한 회차만(FEASIBLE/NOT_FEASIBLE 판정), 실패 시 A. 재스테이징은 계속 보류. 사용자 G1 시험 결과가 오면 최우선.
