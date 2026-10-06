# 2026-10-05 | lap1029 | G1 middle — H-M 독립 검수(M-1·M-2 PASS·덩어리 수리 PASS(partial) 수용, 상한 160 수용) → work H-N(`0x465E80` diff 미러) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간 계획·컨펌) 1 lap. 게임 실행·source 변경·커밋은 0이다.
- 가설: lap1028 work H-M의 수치가 raw에서 재현되는가. (1) M-1 위치·정합·재현성, (2) M-2 표본 귀속, (3) 상한 128→160 수리 전후 창 중앙값, (4) save006 비회귀. 또 `0x465E80`이 바닥 조각의 writer인지 원본 역어셈블로 확인한다.
- 예상 PASS / FAIL 조건: 새 스크립트로 재계산했을 때 판정에 영향을 주는 불일치가 0이어야 한다. bridge 사본은 현재 source와 같아야 한다. 상한 변경은 매크로 1줄이어야 하고, 크기에 의존하는 버퍼가 모두 매크로를 따라가야 한다.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제(원문은 아래 부록). 공유 temp `20261005_lap1029_middle_review/`(모두 uncommitted):
  - `recalc_lap1029.py` `f670232f…816a` → `recalc_lap1029.json` `92b21253…c36b`·`recalc_stdout.txt` `2409fb85…2c17`
  - `recalc2_lap1029.py` `16748db5…19f8` → `recalc2_lap1029.json` `6ca50508…35a5`
  - `objdump_465E80.txt` `6595cf2f…064b`(원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` read-only, SHA `b56986e0…8ac` 직접 확인)
- 원본 SHA / fixture: 8 run 모두 `private_exe_sha256` = 원본 `b56986e0…8ac`이다. save000 `1c703551888f`(index 1), save006 `616b79978917`(index 7). 활성8인 부하 증명은 아니다.
- 검수한 source: 현재 `g1_overlay_blt.h` `5a076c16…`, `g1_mirror2x.c` `f463bc3e…`, `g1_layer_drift.h` `44ce4f24…`, `g1_screen_watch.c` `df2a2360…`. m3 run 4개의 bridge 사본과 같다. m2 bridge는 상한만 128이고 나머지는 같다. m1 bridge는 lap1026 source(`0243f543…`)다. `direct_draw_trace.c` `c89df117…`는 8 run 모두 같다.

## 1. 독립 재계산(`analyze_m*.py`·제품 helper 미사용)

| 항목 | work | 재계산(r1 / r2) |
|---|---|---|
| M-1 덤프·정합 | 39개·불일치 0 | 39/39, ordinal 집합 r1=r2, mask 픽셀 수 = trace `stale_pixels` 불일치 **0**/39 |
| M-1 재현성 | 덩어리 3,206 100%·바닥 408 100%·팝업 80.4% | 덩어리 중앙값 r1 3,206·r2 3,206·교집합 3,206(1.00), 바닥 408/408/408(1.00), 팝업 704/726/575(0.817; r1 기준) |
| M-1 덩어리 성분 | y300..364×x542..608 2,756 px·보조 80 px | 같다(≥½ 프레임 기준 8-이웃). (583,306) stale 프레임 = 24..44 짝수 11개 |
| M-1 바닥 | 24 px 조각 군, (480,515)·(656,544) 39덤프 전부 | ≥½ 성분 8개 전부 24 px(6행×4열). 39덤프 공통 168 px = 조각 7개. 그중 성분 D 좌표(y515..520×x616..619) 24 px |
| M-2 무장 | selftest PASS·fail 0·match 7 | selftest PASS, `a` 52라운드 fail 합 0, match 7. 무장 주소를 화면 좌표로 바꾸면 (583,306)·(480,515)·(656,544)이고 env 값과 같다 |
| M-2 표본 stale | 22·403/404·411/412 | 22/22(첫 p24)·403/404·411/412 |
| M-2 `u` 귀속 | 5/5·1/1·0/0 | 6/6 값 일치(같은/직전 present 마지막 `x` 쓰기 값 = `u.scr`). `drift_unattributed` [5,1,0] |
| M-2 덩어리 writer | `0x467580` 130×130 reject_size | `w` 레코드 `0x467580` 84건 = mirrored 56 + reject_size 28. reject 28건 전부 (511,267) 130×130이고 present 18..45다 |
| M-2 바닥 writer | wined3d → `0x46659F`/`0x46651E` → `0x465F01`(68) | 표본1: 순서 `0x745E99CF`→`0x46659F`→`0x465F01`이 401/402 present, 마지막 writer `0x465F01`(값 68, guard 0)이 402/403. 표본2: `0x745E99CF`→`0x46651E`→`0x465F01` 410/411 전부. `s` 레코드 scr 68·snap 241/242·cov 1. 복귀 주소는 `0x49B195`(표본1)·`0x49AF08`(표본2)다 |
| M-3 save000 창 | p24..58 3,444→216/216 | m1 기준 p24..58 3,444 → **216/216**. 덩어리 박스(y300..364×x542..608) p24..44 stale 0/11. p0..23 441→437, p84..297 316, p298..338 858/727, p339..365 591, 마지막40 414.5(r1=r2). 합 285,026→190,379 |
| M-3 계수 | reject_size 28·56→0 | `0x467580` inv 3,589 = mirrored 3,589, `0x467B00` reject_size 0. 다른 hook reject_size 불변(`0x466B50` 76) |
| M-3 표본·rect_blt | A/B/C 0·[5,1,1]·inv5/heal 44 | 같다. heal 559,476 px |
| M-3 성능·안전 | p95 7/7·안전 0 | pair perf PASS, p95 7/7, tick 비 0.99751/1.00000. 0이 아닌 안전 키는 `panel_transfer_mismatch_cleared`뿐(판별력 없음, lap1013). cleanup·source_unchanged true, camera (39,53), units 375 |
| M-3 바닥 | (미기재) | 바닥 교집합 중앙값 408 → **408**(불변), 39덤프 공통 168 → 168·신규 0 |
| save006 env-off | 38프레임 24 px·39프레임 0·신규 0·p95 7/7 | r1∩r2 38프레임 **24 px**(y515..520×x616..619), 300..620+880 39프레임 **0**, 51덤프 전체 0. lap1026 r1∩r3 대비 신규 0·제거 0. r1·r2 단독도 각각 24/0. PS3 elapsed p50/p95/max 5/7/17·5/7/16. layer_drift·screen_watch 파일 미생성 |
| save006 계수 | `0x467580` reject 16 | 16/16 reject_size. lap1026 s6 r1·r3도 16/16이다(상한 160에서도 거부되므로 크기 >160 또는 >320). overlay BltFast mirrored 791/798(lap1026 795/792) |

**판정에 영향을 주는 불일치는 0이다.** work 기록의 "save006 39프레임"은 mask 스펙상 51덤프 중 300..620+880 39프레임을 뜻한다. 재계산으로 39·51 모두 0임을 확인했다.

## 2. diff·상한 160 검수

- m2→m3 bridge diff는 `g1_overlay_blt.h:12` `128u → 160u` 한 줄뿐이다. 이 매크로에 의존하는 것은 다음과 같고 모두 매크로로 크기가 정해진다. 따라서 overflow 경로가 없다.
  - before 버퍼 10개(`g1_mirror2x.c:156..227`): 각 320×160 = 51,200 B, +10,240 B씩
  - `G1_OVERLAY_SCRATCH_BYTES`: (322×162)×6 = 313,064 B, 기존 251,160 B
  - 거르기 검사 4곳(`g1_overlay_blt_accepts`·`1719`·`3156`·`3235`·`3320`)
  - 하드코딩된 128은 패널 digest(`2529`·`2577`, 무관)뿐이다.
- m1→m2 diff(진단 파서)는 env `SYW2_G1_DRIFT_SAMPLES`가 64바이트 안에서 파싱에 성공할 때만 표본 좌표를 바꾼다. 기본 표 값은 이전 상수와 같다. 문법은 정확히 3점, 숫자 1..4자리, 범위 [0,800)×[0,600), 끝 잔여 0이다. 실패하면 기존 좌표를 유지한다.
- **상한 160 수용(PASS(partial))**:
  - save000에서 새로 수락된 것은 `0x467580` 28·`0x467B00` 56뿐이다. save006은 거부·수락 계수가 lap1026 run 변동 범위 안이라 새 수락이 없다.
  - p95는 두 장면 모두 7 ms로 불변이다. 정적 메모리 증가는 약 160 KB다.
  - diff 미러는 크기와 무관하게 바뀐 픽셀만 쓰므로 정확도 위험이 늘지 않는다. 비용 상한은 호출당 51,200 px다.
  - 남은 위험: 129..160 높이 호출이 많은 다른 장면의 성능은 미측정이다. 다음 성능 측정 장면에서 같이 본다. 테스트 pin 변경(`test_g1_overlay_blt.py` 129 거부 → 130·160 수락/161 거부)은 제품 자체 상수의 계약 테스트다. 안전 pin·golden이 아니다.

## 3. `0x465E80` 원본 역어셈블(read-only)

```
465e80: 8b 41 10      mov eax,[ecx+0x10]     ; 폭 검사 기준 = 렌더러 stride(+0x10, G1_RENDERER_STRIDE)
465e83: 53            push ebx
465e84: 55            push ebp               ; ← 5바이트 명령 경계(8B 41 10 | 53 | 55)
465e85: 8b 6c 24 0c   mov ebp,[esp+0xc]      ; arg1 x0
...     x0,x1 ∈ [0,[ecx+0x10]), y0,y1 ∈ [0,[ecx+0x14]) 하나라도 밖이면 바로 ret(쓰기 0, 클립 없음)
...     x·y 쌍 정렬 → for y=ymin..ymax, x=xmin..xmax(양끝 포함): [[ecx+0x1514] + y*[ecx+0x10] + x] = color(dl)
465efd: 88 54 28 ff   mov [eax+ebp-1],dl     ; 표본 EIP 0x465F01 = 이 쓰기 다음 명령
465f10: c2 14 00      ret 0x14               ; thiscall 5인자(x0,y0,x1,y1,color), call 없음 = leaf
```

- 호출 33곳은 모두 `call 0x465e80`이다. 첫 5바이트(`0x465E81..84`)로 들어오는 분기는 0이다.
- 관측 복귀 주소 `0x49B195`·`0x49AF08`은 각각 `call 0x465e80`(`0x49B190`·`0x49AF03`) 바로 다음이다. 두 곳 모두 `push 0x44`(색 68)·x0=base·x1=base+3·y0=v−12·y1=v−7이다. 즉 **4열×6행 = 24 px 색 68 블록**이고, 바닥 조각의 크기·값과 정확히 같다. `ecx=0xE5BF18` = 화면 렌더러다.
- census DLL은 이미 같은 주소를 `rect_fill`(9바이트 `8B 41 10 53 55 8B 6C 24 0C`)로 hook한다. 그래서 H-N 뒤에도 census는 `--census-only`로만 쓴다(기존 규칙).
- **H-F2 `mirror_rect_border`와 다른 점(H-N 필수 반영)**:
  - (a) `0x465E80`은 viewport(`+0x4D0`) 교집합을 하지 **않는다**. `rect_fill_clip`/`g1_rect_fill_region`을 쓰면 viewport 밖 쓰기(하단 패널 y515..549 포함 가능)를 놓친다. 대신 H-F3 `mirror_flip_rle`처럼 원본 범위 검사를 그대로 복제한다. 범위 밖이면 원본도 쓰지 않으므로 reject_bounds로 센다.
  - (b) x 상한은 화면 폭 800이 아니라 stride(832)다. 미러 사각형은 화면 [0,800)×[0,600)와 교집합한다.
  - (c) 좌표는 양끝 포함이다(폭 = xmax−xmin+1).
- 판정: **FEASIBLE**(work 판정 확인).

## 4. 판정

**H-M을 수용한다.** M-1 PASS, M-2 PASS. 덩어리 수리(상한 128→160)는 PASS(partial, 기술 부분 — 제품/마일스톤 마감 아님)다.
- save000 p24..58 3,444→216(−93.7%), 화면 stale 합 −33%다. 다른 창·표본·성능·안전은 불변이고, save006은 비회귀다.
- 남은 save000 stale의 대부분은 바닥 조각 17개 × 24 px = 408 px/present다. writer는 미후킹 `0x465E80`으로 확정했다.
- 덧붙임: save006 성분 D(y515..520×x616..619)는 save000 바닥 조각과 같은 좌표·같은 크기다. 같은 writer일 가능성이 높으므로 H-N에서 함께 관측한다(예측일 뿐 판정 조건은 아니다).

## 5. 다음 work H-N 사전등록(Sonnet work 1 lap, 최소 구현 + 격리 실행)

목표: `0x465E80`(단색 사각형 채움, 클립 없음)을 diff 미러로 hook해 save000 바닥 조각을 없앤다.

### 5.1 구현
- `g1_mirror2x.c`에 `G1_RECT_SOLID 0x00465E80u`를 둔다. old bytes 5바이트 `8B 41 10 53 55`를 `install_one`으로 검증한 뒤 hook한다(불일치 시 설치 거부). wrapper는 `mirror_rect_solid(renderer, x0, y0, x1, y1, color)` thiscall `ret 0x14`다.
- 거르기 순서(H-F2/H-F3 동형):
  1. guard면 reject_guard.
  2. 대상 버퍼 검사(H-F2와 같은 조건)면 reject_target.
  3. **원본 범위 검사 복제**: `x0,x1 ∈ [0, stride)`, `y0,y1 ∈ [0, [renderer+0x14])`. 하나라도 밖이면 reject_bounds(원본도 쓰지 않음). `[renderer+0x14]` 값은 첫 호출 때 계수/trace에 한 번 기록한다.
  4. 정렬 후 양끝 포함 사각형을 화면 [0,800)×[0,600)과 교집합한다. 비면 reject_bounds다.
  5. `g1_overlay_blt_accepts` 크기 상한을 넘으면 reject_size.
  6. 통과하면 before 사본(전용 버퍼 `g_rect_solid_before`) → 원본 호출(원 인자 그대로, 항상 1회) → `g1_overlay_blt_apply`.
- 계수 `rect_solid_465E80_{invocations,mirrored_calls,mirrored_pixels,reject_target,reject_bounds,reject_size,reject_guard}`를 accessor·`direct_draw_trace.c` 요약에 추가한다. install/detach/installed 목록도 갱신한다. 항등식은 inv = mirrored + reject_* 전부다(apply 실패는 reject_size).
- 테스트(RED→GREEN):
  - hook 주소·old bytes·5바이트 명령 경계·`ret 0x14`
  - 범위 밖 좌표(음수·x=stride·y=[+0x14]) → 미러 0
  - 뒤집힌 좌표 정렬·양끝 포함 폭
  - x 800..831 부분은 화면 교집합만 미러
  - 계수 항등식

### 5.2 실행(성능 gate 전 `/proc/loadavg`, 1분 load >8이면 대기)
- save000 pair 2회: lap1028 `run_m3.sh` s0 인자를 그대로 쓴다(`--layer-drift --stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`).
- save006 env-off pair 2회: `--stale-mask 6-12,30-34,300-301,585-620,880`.
- 실행 뒤 `game` 사본만 삭제한다.

### 5.3 PASS / FAIL(기준 = lap1028 m3 r1/r2, 이번 재계산 값)
- **N-0**:
  - save000에서 `rect_solid_465E80` inv > 0이고 항등식이 성립해야 한다.
  - mirrored_calls > 0이어야 하고, 바닥 조각 호출(24 px)이 reject되지 않아야 한다.
  - 안전 0(`panel_transfer_mismatch_cleared` 제외), cleanup·source_unchanged true, camera (39,53), units 375여야 한다.
- **N-1(핵심)**: 다음을 모두 충족해야 한다.
  - save000 r1∩r2 39덤프 공통 168 px → **0**
  - 바닥 프레임(16) 교집합 중앙값 408 → **≤40**
  - 마지막40 중앙값 414.5 → **≤100**
- **N-2**:
  - 다른 창 중앙값이 기준보다 5% 넘게 증가하면 안 된다(p24..58 216·p84..297 316·p298..338 858/727·p339..365 591). 바닥이 섞인 창은 감소가 예상된다.
  - 표본 A/B/C stale 0을 유지해야 한다.
  - 화면 stale 합이 감소해야 한다.
- **N-3**: pair p95 ≤8 ms, tick 비 0.995..1.005.
- **N-4**: save006 env-off r1∩r2 38프레임 ≤24 px(성분 D가 0이 되면 함께 기록), 39프레임 0, lap1028 대비 신규 0, PS3 p95 ≤8.
- FAIL 처리:
  - N-1이 일부만 줄면 남은 조각을 `--drift-samples`로 재귀속한다. wined3d 선기록이 마지막이면 heal 일반화를 판단한다. 수리는 1회 후 재실행한다.
  - N-0 설치 실패면 old bytes를 대조하고 인계한다.
- 전체 `make check`는 기록 freeze 뒤 1회만 실행한다(lint·typecheck 먼저).

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산·read-only 역어셈블만 했다. 게임/source/commit은 0이다. 전체 `make check`는 SKIP했다. source가 불변이고 lap1028 full PASS 1624(`logs/gates/lap1028-work-full-check.log` `bee1b4cd…`, exit 0)가 유효하다. focused 검사 결과는 STATUS에 보강한다.
- 남은 위험:
  - 상한 160의 다른 장면 성능은 미측정이다.
  - `0x465E80` 호출처는 33곳이다. 미러 비용은 호출당 작은 사각형이 대부분이라 낮을 것으로 예상하지만 미측정이다.
  - heal은 사각형 하나만 감시한다(기존).
- 참고: `tools/inmm_stub/.omc/`(OMC state 디렉터리, untracked)가 생겨 있다. 이번 lap이 만든 것이 아니고 손대지 않았다.
- backlog 유지: save006 짧은 run 꼬리, 성분 D(H-N에서 관측), hold keydown 위상, 가장자리 마우스 스크롤, wrap 쓰기 미추적, save000 overlay BltFast rejects 452/453, 다중 팝업 heal.
- 사용자 승인 상태: 기술 검수일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-N(위 §5).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1028 work, SHA256 `a64b818b250feb6b8302a2178b815938b884226be0f85ecb0ac950585c468b3c`)

```
lap1028 work(Claude Code claude-sonnet-5-5) G1 H-M 인계 (마일스톤 경계 아님; 사전등록 M-1/M-2 PASS + 덩어리 수리 PASS, 독립 검수 요청).
- 한 일: M-1 save000 pair 2회 `--stale-mask`(51자·39덤프·mask 정합 불일치 0·r1∩r2 덩어리/바닥 100%) → 덩어리 y300..364×x542..608 2,756px(p24..44), 바닥 6×4 px 조각 군(y515..520·y544..549, 전 프레임 고정). M-2 `SYW2_G1_DRIFT_SAMPLES`/`--drift-samples`(opt-in, env 없으면 기본 A/B/C) + screen watch pair 2회: 덩어리 writer = `0x467580` 호출 130×130(511,267) `reject_size`(MAX_HEIGHT 128), 바닥 writer = 미후킹 `0x465E80`(`0x465F01`, 5인자 ret 0x14 leaf) + wined3d 선기록. 수리 1줄: `g1_overlay_blt.h` G1_OVERLAY_MAX_HEIGHT 128→160.
- 실행: 공유 temp 20261005_lap1028_work_hm/ (run_m1/m2/m3.sh, m1_s0_r1|r2·m2_s0_r1|r2·m3_s0_r1|r2·m3_s6_r1|r2, analyze_m1/m2/m3_s0/m3_s6.py·analysis_*.json). 전부 pair exit 2 = 기존 pair HOLD(V2s raw).
- 결과: save000 p24..58 중앙값 3,444→216/216, `0x467580`/`0x467B00` reject_size 28·56→0, 다른 창 불변(p84..297 316·p339..365 591·마지막40 414.5·p298..338 858/727), p95 7/7, 안전 0, 표본 A/B/C stale 0. save006 env-off pair 2회: r1∩r2 38프레임 24 px(성분 D)·39프레임 0·신규 0·p95 7/7·안전 0.
- middle이 확인할 것: (1) `analyze_m*.py`·제품 helper 없이 새 스크립트로 M-1 성분/정합·M-2 귀속·수리 전후 창 중앙값·save006 비회귀 재계산, (2) `0x465E80` 함수 경계·5인자·leaf 판정(objdump)과 바닥 24px 조각이 그 호출인지, (3) MAX_HEIGHT 160 일괄 상향의 위험(다른 장면·메모리·성능) 수용 여부, (4) 다음 work H-N(`0x465E80` diff 미러, 5바이트 `8B 41 10 53 55`) 사전등록.
- 기록: docs/history/laps/20261005_lap1028_work_g1_hm_save000_stale_localize_lump_repair.md. 변경 uncommitted.
```
