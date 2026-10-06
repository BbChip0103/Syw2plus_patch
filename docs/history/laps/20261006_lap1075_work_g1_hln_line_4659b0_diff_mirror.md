# 2026-10-06 | lap1075 | G1 H-LN (`0x4659B0` 클립 직선 diff 미러)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 승인·수용 판정은 하지 않는다(독립 검수는 다음 middle).
- 가설 / 사용자 관찰: lap1074 §4 H-LN — save006 좌우 edge hold 창 ord 231~233 stale(728 px)은 미후킹 `0x4659B0`이 그린 255색 선이며, 그 함수를 `mirror_rect_border7` 형제 diff 미러로 감싸면 사라진다. ord 124/125/226이 같이 사라지면 같은 writer.
- 예상 PASS / FAIL 조건: lap1074 §4 L-0(좌우 edge 2/2 hold 합 ≤10·ord 231~233 0·마지막40 0·`line_4659B0_mirrored_calls`>0·reject 0)·L-1(124/125/226 기록)·L-2(E-0·E-1 유지·pair PASS·안전 0)·L-3(UP/DOWN edge ≤1·키 hold ≤1·save000 hold 0·gate가 lap1071 e와 동일·save006 300..848 0). FAIL = 크래시·안전 위반·원본 이중 호출·기존 경로 회귀.
- 변경 파일 / source fingerprint / 커밋: uncommitted. `tools/inmm_stub/g1_rect_fill.h`(`g1_line_region`) `ab18eb5d…`, `tools/inmm_stub/g1_mirror2x.c`(`G1_LINE`/`G1_LINE_LEN 7`/`expected_line`/`mirror_line`/`g_hook_line`/계수 6개·install·restore·installed) `28143d61…`, `tools/inmm_stub/g1_mirror2x.h`(accessor 6) `4ce14511…`, `tools/inmm_stub/direct_draw_trace.c`(`line_4659B0_*` 6개, 둘째 builder `line_details[320]`) `409e11e0…`, `tests/test_g1_rect_fill.py`(새 테스트 2) `fe253acc…`. 하네스·기타 제품 파일 불변.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac`(읽기·objdump만, 각 run `source_unchanged` true). 비합성 save006(`616b7997…`)·save000(키 hold 비회귀 1회). scale2x HD, load 2.0~3.4(≤8), run마다 대기 0 s, 순차.

## N-0 테스트 먼저 (RED → GREEN)

- RED: `test_line_region_covers_every_plot_of_original_clipped_line`(gcc 컴파일 실패 = `g1_line_region` 없음), `test_line_hook_table_and_wrapper_contract`(`G1_LINE` 없음) 둘 다 FAIL 확인 → 구현 뒤 GREEN. `tests/test_g1_rect_fill.py`+mirror2x+overlay_blt+saved_scene_probe **273 passed/12.60s**, `make lint`·`make typecheck` PASS. 둘째 builder 최악 합 테스트(`test_trace_details_buffers_hold_worst_case_wsprintf_output`)도 새 `line_details[320]` 포함 PASS(builder 9,216 유지).
- C 테스트는 `0x4659B0` objdump를 그대로 옮긴 모델(부호는 차이로, 오차 누산 0에서 시작, plot→누산→주축 span 초과 시 진행, max+2회)로 start 126점(x0 −6..46 step 4 × y0 −6..36 step 5)×dx −14..14×dy −14..14(수평·수직·대각·역방향·한 점·클립 경계 걸침·클립 밖)의 plot 전부가 `g1_line_region`(끝점 bbox 사방 +1 ∩ 클립) 안임을 확인(plots >100,000, 밖 0).
- **정정(lap1074 정정 1 대비):** 같은 모델로 실제 초과량을 재면 **0**이다 — 첫 점이 두 번 찍히고(첫 반복은 누산이 span을 못 넘겨 진행 없음) 마지막 plot이 정확히 끝점이라 "끝점을 주축으로 1칸 넘는다"는 재현되지 않는다(Python 모델 |dx|,|dy|≤15 전수 초과 0, 예 (0,0)→(5,0) plots (0,0)(0,0)(1,0)…(5,0)). 사전등록 계약대로 영역은 사방 +1 px 여유를 유지했다(diff 미러라 여유는 무해, 테스트는 초과 ≤1만 요구). 이 정정은 `objdump 0x465A1A..0x465A85` 전사에 근거하므로 middle이 독립 재전사로 확인해야 한다.

## N-1 구현 (`mirror_line`)

hook `0x4659B0`, old bytes `83 EC 0C 8B 44 24 18`(7 B, 상대 주소 없음), thiscall 5인자 `ret 0x14`, `G1PrimitiveFn` 재사용. `mirror_rect_border7`와 같은 규칙: guard/target/size reject → before 복사(영역 최대 800×600) → 원본 trampoline **정확히 1회** → `g1_overlay_blt_apply_tiled`(≤320×160 타일)로 영역만 미러. 좌표·색 하드코딩 0. 계수 `line_4659B0_{invocations,mirrored_calls,mirrored_pixels,reject_target,reject_size,reject_guard}`. `0x465900`은 별도 hook하지 않음. `i686-w64-mingw32-gcc`로 `_inmm.dll` 전체 컴파일 성공(신규 경고 0).

## N-2 실행(순차, 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1075_work_hln/`, 로그 `logs/gates/lap1075_ln_ln{1..7}.{log,exit}`, game 사본 각 run 뒤 삭제)

스크립트 `run_ln.sh` `db567706…`·`run_ln2.sh` `aef1367f…`, 분석 `analyze_ln.py` `89217edb…`·`mask_ln.py`·`attr_ln.py`(lap1073 스크립트 복제+계수 추출). 모든 run exit 0(ln5 pair status HOLD는 기존 사유), 안전 7종 최대 0, `source_unchanged` true.

| run | 구성 | pair-result SHA | hold 창(ps3 ord 123..291) stale 합 | 마지막40 | `line_4659B0` invocations / mirrored_calls / mirrored_pixels / reject | p95 fixed/hold · tps 비 |
|---|---|---|---|---|---|---|
| ln1 | save006 LEFT,RIGHT edge(마스크 `123-126,130-146,224-235`) | `cbf36e5cb610` | **3** (ord 226 만, 124/125/231/232/233 = **0**) | 0 | 1258 / 286 / 966 / 0·0·0 | 7/7 · 1.0029 |
| ln2 | save006 LEFT,RIGHT edge(비진단 `0-1600/30`) | `483923cdfc19` | **3**(ln1과 동일, ord 226) | 0 | 1258 / 286 / 966 / 0·0·0 | 6/7 · 1.0037 |
| ln3 | save006 UP,DOWN edge | `9afebfd0cb9f` | **0**(기준 lap1067 1) | 0 | 1371 / 2 / 1 / 0·0·0 | 7/7 · 1.0034 |
| ln4 | save006 키 hold UP,DOWN(lap1065 nd 옵션) | `2e2b3e374fdd` | **0**(기준 lap1065 nd 1) | 0 | 1371 / 2 / 1 / 0·0·0 | 6/7 · 1.0029 |
| ln5 | save000 DOWN,UP 키 hold(lap1071 e 옵션) | `7c67943eea3b` | **0** | 0 | 0 / 0 / 0 / 0 | 6/7 · 1.0044 |
| ln6 | save006 고정 카메라(`MASK6`) | `f307b40cccc8` | — (300..848 합 0·최대 0, 867 present) | 0 | 0 | — |
| ln7 | ln1 + `--layer-drift --screen-watch --drift-samples "799,48;799,49;799,50"` 진단 | (pair PASS) | 3(ln1과 동일) | — | 1258 / 286 / 966 | — |

- **E-0**: ln1·ln2·ln3·ln4 두 lane 24칸(왕복 24+24)·관측열 동일·clamp 없음·최종 (158,101)·입력 tick 정상. **E-1**: p95 위표, tps 비 ≥1.0029.
- **ln5 gate별 비교**: lap1071 e와 `status`/`input_effect_comparison` HOLD·V2·V2s·V2q BLOCKED·minimap/terrain/loaded/scroll_after/scale2x PASS 전부 동일(기존 HOLD 사유 불변, 이번 변경 무관).
- **L-0 PASS**(좌우 2/2 합 3 ≤ 10, ord 231~233 각 0, 마지막40 0, mirrored_calls 286>0, reject 0). 합 822(ord 124=14·125=77·226=3·231=235·232=222·233=271) → 3.
- **L-1**: ord 124·125 → **0**(같은 writer `0x4659B0`로 귀속). **ord 226(x799,y48..50 3 px)은 남는다 — 선 hook과 무관한 별개 writer**: ln7 진단 표본 3/3 마지막 writer = tid 280 EIP **`0x00465C71`**, 값 246 = 화면 값, 스택 `0x0047933A`→`0x00478E39`, mod 0. objdump(원본 읽기만): `0x465C6E 88 14 1F mov [edi+ebx],dl` 바로 다음 명령 = **기존 hook `0x465B30`(H-F2 사각형 테두리) 안 조건부 가장자리 plot**, 같은 run `rect_border_465B30_reject_size` 34(ln1 34). 따라서 미후킹 함수가 아니라 hook된 `0x465B30`이 미러하지 못한 호출 3 px(원인은 UNKNOWN; 후보: reject_size 34 중 하나 또는 mirror 영역 밖 plot). 이 항목만으로 FAIL 아님(사전등록 L-1).
- **L-2·L-3 PASS**: pair PASS(ln1~4·6)·안전 0·cleanup·source_unchanged·UP/DOWN edge 0≤1·키 hold 0≤1·save000 hold 0·save006 300..848 0·ln5 gate 동일. 부하 변형 판정 제외 run 없음(load ≤3.4, hold 창 p95 ≤7).

판정(work 후보): **H-LN PASS(partial)** — `0x4659B0` 미후킹 writer 해소(822 → 3), 잔여 3 px는 `0x465B30` 미러 누락으로 귀속. 승인은 middle.

## 검사 / 한계

- Fast: focused 273 passed·lint·typecheck PASS, mingw `_inmm.dll` 컴파일 PASS. 전체 `make check`는 기록 freeze 뒤 1회(결과는 STATUS 보강).
- 한계: ord 226 3 px 원인 UNKNOWN(`0x465B30` reject_size 34 미조사); 좌우 edge는 save006만; 모서리(대각) edge·H-LD 부하 동반 재현 미착수; 좌우 edge 2 run은 결정론 동일값이라 통계 독립성 약함(이전 x2=m1과 같은 모양). 변경은 uncommitted.

## 다음 한 가지

middle(Opus): lap1075 work 독립 재계산(ln1~ln7 pair/mask/trace)·`0x4659B0` 전사(정정 반영)·`mirror_line` 코드 검토·`0x465C71` ∈ `0x465B30` objdump 재확인 후 수용 판정. 이어 work: ord 226 3 px = `0x465B30` reject_size 34 귀속(H-LB, 진단 모드 `rect_solid_reject_log` 방식 재사용) 또는 H-LD 부하 동반 stale 재현.
