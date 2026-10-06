# 2026-10-06 | lap1066 | G1 middle — H-D2t 독립 검수 + H-D2e 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·테스트 변경 0, commit 0.
- 입력: lap1065 work `loop/ESCALATE_SOL`(2,119 B, SHA256 `34984bd54a286b4a4262eb082d89ef5e86ed9549f83d35bf6f006d8b37f8b39b`, 원문 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1064 §4 H-D2t — hold 뒤 p313..315 3-present 일시 stale은 미미러 writer 하나. lap1065 work가 미후킹 `0x465CA0`(선택 드래그 1 px 윤곽)으로 귀속·diff 미러로 수리했다고 보고.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac` 직접 재계산 MATCH. fixture: 비합성 save006(D-2 hold·고정 카메라)·save000, lap1065 7 run 산출물만 읽음.

## 1. 독립 재계산(work `analyze_d2t.py`·`analyze_s0_copy.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1066_middle_review/`:
`recalc_lap1066.py` `4fc422fa…f8fb` → `recalc_lap1066.json` `b61defb6…120e`, objdump `od_465CA0_lap1066.txt` `ee561b78…04b7`.
입력 pair-result SHA 접두 7개(t0_run1 `a5a47837`·t0 `2079024e`·t1 `33e67a20`·nd1 `b74b0c65`·nd2 `4453237d`·s6 `24109e5b`·s0 `9573268d`) ESCALATE 기재와 일치.
run별 `bridge/` 소스: t0·t0_run1·t1 = lap1063 제품(`g1_mirror2x.c` `dc8c6ede`, 수리 전 진단), nd1·nd2·s6·s0 = 현재 작업 트리(`g1_mirror2x.c` `12512b4d`·`g1_mirror2x.h` `b2cd0bf9`·`g1_overlay_blt.h` `39e6e2e1`·`direct_draw_trace.c` `c213243c`). `inmm_stub.c`·`Makefile`은 builder 생성본(lap1063 bridge와 같은 `b66313d2`·`4cf2908f`) → 측정한 제품 = 검토한 코드.

| 항목 | 사전등록(lap1064 §4) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| T-0 위치(t0) | bbox·픽셀 기록 | p313 **319** px (100,40)-(200,100)·p314 **719** px (100,40)-(325,175), 둘 다 **bbox 1 px 테두리 위 100%·내부 0**(둘레 320/720 중 319/719), trace tick 24882/24883 | 동일 | 일치 |
| t0_run1 무효 | — | pair HOLD·hold 창 카메라 y 77..100·최종 (149,92)(DOWN 15칸)·hold p95 28 → 입력 위상 경합 | 동일 | 일치(무효 보존) |
| T-1 귀속(t1) | ≥90% | 표본 좌표 (150,40)/(100,70)/(200,70)(watch 주소 역산)·stale present p316 3/3 마지막 writer EIP `0x465DB3`/`0x465E3C`/`0x465E6C` ∈ `0x465CA0..0x465E7C`, tid 284, val==scr(68≠snap 66) 3/3, stack 첫 칸 `0x434133`(= `call 0x465CA0` 다음 주소) → **100%** | 3/3 | 일치·PASS |
| T-1 watch 손실 | — | dropped 0·overflow 0 | — | 일치 |
| T-2 p313..315(nd 기준 trace 1,677/1,438 직접 확인) | 2 run ≤1%/0 | nd1·nd2 마스크 308..322 합 **0**, trace stale ps3 idx 300..330 전부 0 | 0/0 | 일치·PASS |
| `rect_border7_465CA0` | invocations>0·reject 0 | nd1·nd2 12/12·1,689 px, s6 14/14·1,451 px, s0 0, reject_target/size/guard 0(4 run) | 동일 | 일치·PASS |
| hold 창 stale 합(down_input..final_observation) | ≤10 | nd1·nd2 **1**(idx 125 단발, 123..291) | 1/1 | 일치·PASS |
| pair·안전 7종·cleanup·source_unchanged | PASS·0·true | t0·t1·nd1·nd2·s6 gate 전부 PASS, 안전 max 0(7 run), cleanup ok·game_removed·source_unchanged true(7 run) | 동일 | 일치·PASS |
| I-0 | 24칸×2·clamp 없음·최종 (158,101) | nd1·nd2 카메라 y 101→77→101 범위 24·final_scene_snapshot (158,101) | 동일 | 일치·PASS |
| I-1 hold p95 / tps 비 | ≤고정+16 / ≥0.95 | nd1 7(고정 6)/1.0029·nd2 7(고정 7)/1.0024 | 동일 | 일치·PASS |
| 마지막40 | 0 | 7 run 중앙값 0·합 0 | 0 | 일치·PASS |
| s6 마스크 | 300..848 0 | 300..848 **0**·**frame 880 마스크 존재·0 px**(ps3 899) | 0 | 일치·PASS(정정 2) |
| s0 | p298..338 0·HOLD 사유 동일 | 마스크 39 프레임(6..399) 합 0·gate 9개가 lap1063 s0·lap1056 r_s0_r1·r_s0_r2와 **gate별 동일**(input_effect HOLD·V2/V2s/V2q BLOCKED·나머지 PASS) | 동일 | 일치·PASS |

**정정 1(비차단):** work는 s6 초기 6..12를 "lap1063 s6과 ±1 px"라고 적었으나 frame 10은 18,386 → **18,621(+235)**다. 차이 236 px(새 쪽만)는 bbox (255,33)-(286,52)의 대각선 스프라이트 모양 덩어리(테두리 14·내부 222)이고 1 px 윤곽이 아니다. 같은 frame이 lap1056 r_s6_r1/r2·lap1063 s6에서 18,385/18,385/18,386이고 프레임 0..15 전체가 로드 과도 stale(~17k~19k, p16에서 0)이다. `mirror_rect_border7`의 diff 쓰기는 정의상 원본이 바꾼 윤곽 픽셀뿐이라 이 모양을 만들 수 없다 → 로드 구간 run 변동, H-D2t 무관.
**정정 2(종결):** lap1064 정정 1의 "s6 frame 880 미측정"은 이번 s6(ps3 899)에서 측정됐고 0이다.
참고: t1 p316 610 px는 순수 윤곽이 아니다(bbox 테두리 167·내부 443, 진단 동반 +4 tick 위상에서 잇따른 윤곽 겹침으로 추정). 귀속 판정은 표본 3점으로 하므로 영향 없음.

## 2. 코드 검토

- **objdump `0x465CA0`(직접, 읽기만):** `83 EC 10`(sub esp,0x10)·`53`(push ebx)·`B8 01 00 00 00`(mov eax,1) = **9 B 명령 경계**, 상대 주소 없음, 함수 안에서 `0x465CA1..0x465CA8`로 가는 분기 0. `ret 0x1c`(7 인자×4). buffer `[ecx+0x1514]`, viewport `[ecx+0x4D0/4D4/4D8/4DC]` 비교·클립, 색 LUT `[edx+ecx+0x19A0]` 4곳. 호출처 `0x43412E`(`mov ecx,0xE5BF18`) — t1 stack `0x434133`과 일치.
- **`install_one` 9 B 경로:** `length > sizeof(hook->original)` 검사(이제 16), trampoline = 원래 9 B 복사 + `jmp address+9`, 대상은 `E9 rel32` + NOP 4개, `patched`에 9 B 기록 → `restore_hook`은 `hook->length` 9 B를 patched 확인 뒤 original로 되돌린다. `G1HookState` 8→16 B 확장은 구조체 내부 배열 크기만 바꾸고, 다른 파일에서 이 구조체나 배열 크기를 쓰는 곳 0(grep). 5 B 전용 경로(`length = 5u`)는 불변.
- **`mirror_rect_border7`:** 원본 호출 1회·7 인자 그대로·반환값 그대로. guard/target(cache·panel buffer·stride·높이 600) 거부 → 원본만 호출. `g1_rect_fill_region`(정렬·inclusive·viewport 클립) 사각형이 화면 밖이면 reject_size. before 복사 stride = rect.width = `apply_tiled`의 before 색인과 같음, 버퍼 800×600 = 최대 복사량. 원본이 쓰는 픽셀은 모두 이 사각형 안(objdump 계약)이라 diff가 누락 없이 잡는다(nd 2 run 0으로 실측 확인).
- **`g1_overlay_blt_apply_tiled`:** 크기·화면 경계·`g1_overlay_blt_accepts`(첫 타일 크기)를 타일 적용 전에 검증, 타일 ≤320×160, 각 타일이 `g1_overlay_blt_apply`(halo = 실제 post frame)를 호출 → banded와 같은 구조. 검증 뒤 타일 실패는 경계상 일어나지 않는다(실패 시 0 반환·reject_size 계수, 원본 출력은 이미 반영).
- **`direct_draw_trace.c`:** `rect_border7_details[320]` 최악 = 리터럴 220 + `%u` 6×10 = **280 B(+NUL 281) ≤ 320**. 두 번째 builder 9,216은 `test_mirror_details_builder_holds_worst_case_concatenation`(섹션 전체 합 계산)이 border7 블록을 포함해 검사.
- 판정: 결함 없음.

판정: **H-D2t PASS(partial) 수용** — T-1·T-2·비회귀 사전등록 기준 전부 충족, 정정 1·2 비차단. 키 hold 스크롤 시나리오(save006 D-2 왕복 + 선택 드래그)의 비진단 stale은 idx 125 1 px만 남는다. 한계: 새 hook 실제 호출은 드래그 장면 12~14회뿐이고 윤곽이 viewport 경계에 걸리는 경우·타일 2개 이상 경로는 호스트 C 테스트로만 보장. 제품 G1 마감·사용자 승인은 아니다.

## 3. work H-D2e 사전등록(다음 work, Sonnet)

가설: 가장자리 마우스 스크롤(사용자가 실제로 쓰는 두 번째 스크롤 입력)도 키 hold와 같은 화면 경로를 타므로, 현재 후보에서 hold 창 stale·성능이 키 hold와 같은 수준이다. 하네스에 입력 경로가 없으므로 이번 회차는 **하네스 입력 경로 추가 + 측정**이다(제품 source 변경 없음이 기본, 새 stale이 나오면 귀속까지).

1. **E-0 하네스(테스트 먼저 RED→GREEN):** `tools/g1_saved_scene_probe.py`에 `--terrain-scroll-edge`(기존 `--terrain-scroll-hold`와 배타). hold 창에서 키 대신 XTest pointer motion으로 화면 위 가장자리(y=0, x=화면 가운데)로 옮겨 기존 hold와 같은 tick 수만큼 머문 뒤 아래 가장자리(y=마지막 행)로 같은 tick 수, 그다음 가운데로 복귀. baseline 800×600·candidate 1600×1200 각자 창 좌표로 환산(기존 클릭 좌표 매핑 재사용). 입력 위상 경합이면 기존 규칙처럼 run INVALID·보존 후 재실행.
2. **실행:** save006 비진단 pair 2(순차, load ≤8). 새 stale이 hold 창 합 >10이면 진단 1회(`--layer-drift --screen-watch --drift-samples` 3점)로 writer 귀속까지(수리는 다음 회차).

PASS 기준:
- E-0: baseline·candidate 모두 카메라가 위로 ≥1칸 이동 후 원래 행으로 복귀, 두 lane의 이동 칸 수 같음, 최종 카메라 = 시작 카메라, clamp 기록.
- E-1: hold 창 p95 ≤ 고정+16·tps 비 ≥0.95.
- E-2: hold 창 stale 합 ≤10(키 hold nd 기준 1). 초과면 FAIL이 아니라 새 잔여로 기록하고 귀속 표본까지.
- 비회귀: pair gate(edge 모드에서 비교 불가 gate는 사유 공개)·안전 7종 0·cleanup·source_unchanged·마지막40 0, 기존 `--terrain-scroll-hold` 테스트 불변.
- BLOCKED: baseline에서도 카메라가 움직이지 않으면(포인터가 게임 창 가장자리에 닿지 않음 등) 제품 판정 없이 하네스 원인과 좌표 근거를 기록해 인계.
- FAIL: 크래시·안전 위반·pair 비교 lane 불일치(이동 칸 수 차이)가 2 run 재현.

## 4. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT, focused(`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`). 결과는 STATUS에만 보강한다.
- 전체 `make check` SKIP(문서만 변경, source는 lap1065 full PASS 1643과 같은 해시; 다음 work H-D2e가 하네스 변경 뒤 실행).

## 다음 한 가지

work(Sonnet) H-D2e: §3 E-0 하네스 → save006 pair 2 → (필요 시 진단 1) → `make check`. 그다음 후보: HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: save006 lap1056 r1 부하 동반 stale, 미후킹 `0x467E60`, 진단 동반 영역 x301..334·y357..398, save000 overlay BltFast rejects, 다중 팝업 heal, hold keydown 위상 경합. G6/G7은 사용자 합격(APPROVALS lap989) 대기, 루프를 막지 않는다.

## 부록: lap1065 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1065 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-D2t 구현·실행 완료, 사전등록 기준 work 자체 계산상 충족. work는 자기 결과를 승인하지 않으므로 fresh Opus middle 독립 검수가 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1065_work_d2t/ 의 {t0,t1,nd1,nd2,s6,s0}/pair-result.json·candidate/{trace_raw,layer_drift,screen_watch}.jsonl·stale_mask.bin 을 work 스크립트(analyze_d2t.py·analyze_s0_copy.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: t0 2079024e, t0_run1_input_race a5a47837(무효·DOWN 15칸 입력 경합), t1 33e67a20, nd1 b74b0c65, nd2 4453237d, s6 24109e5b, s0 9573268d.
2. 검증 항목: t0 p313 319·p314 719 px 윤곽 모양/bbox; t1 표본 stale 3/3 마지막 writer EIP 0x465DB3/0x465E3C/0x465E6C ∈ 0x465CA0..0x465E7C(objdump 직접 확인: old bytes 83 EC 10 53 B8 01 00 00 00 = 9 B 도둑질, ret 0x1c, 인자 x0 y0 x1 y1+LUT 3, viewport 0x4D0..0x4DC 클립); nd1/nd2 마스크 308..322 합 0·hold 창 합 1(p125)·rect_border7 invocations 12/mirrored 12/reject 0·pair PASS·안전 7종 0·I-0·I-1 p95·마지막40 0; s6 마스크 300..848 0·rect_border7 14/14; s0 gate가 lap1063 s0와 gate별 동일.
3. 코드 검토: tools/inmm_stub/g1_overlay_blt.h g1_overlay_blt_apply_tiled(검증 선행·≤320x160 타일·halo=실제 post frame), tools/inmm_stub/g1_mirror2x.c mirror_rect_border7(정렬+viewport 클립 사각형 before 복사→원본 1회→타일 diff; 800x600 before 버퍼), install_one 9 B 경로와 G1HookState original/patched 8→16 B 확장 영향(restore_hook), direct_draw_trace.c rect_border7_details[320] 최악 길이·mirror_details 9216 합. 수용 시 다음 work(가장자리 마우스 스크롤·HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비 중 선택) 사전등록.
기록 docs/history/laps/20261006_lap1065_work_g1_hd2t_rect_border7_465ca0_diff_mirror.md. 변경은 전부 uncommitted(g1_mirror2x.c·g1_mirror2x.h·g1_overlay_blt.h·direct_draw_trace.c·두 테스트).
```
