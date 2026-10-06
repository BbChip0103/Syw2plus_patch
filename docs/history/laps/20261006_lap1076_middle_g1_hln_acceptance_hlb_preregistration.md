# 2026-10-06 | lap1076 | G1 middle — H-LN 독립 검수 + H-LB 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1075 work `loop/ESCALATE_SOL`(SHA256 `5907a8035a8b6b1322a01cf584f2457f6f32ae7ba8179606a9240c76729693a7`, 3,511 B, 원문 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1074 §4 H-LN — save006 좌우 edge hold 창 ord 231~233 stale(728 px)은 미후킹 `0x4659B0` 클립 직선이 그린 선이고, diff 미러로 감싸면 사라진다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기·objdump만). fixture: 비합성 save006·save000. lap1075 산출물만 읽음.
- 검수한 source 해시(현재 트리 = 7 run `bridge/` byte 동일, `cmp` 불일치 0): `g1_rect_fill.h` `ab18eb5d…06c2`, `g1_mirror2x.c` `28143d61…ef44`, `g1_mirror2x.h` `4ce14511…bd`, `direct_draw_trace.c` `409e11e0…a358`, `tests/test_g1_rect_fill.py` `fe253acc…e2a` — work 기록 접두와 일치.

## 1. 독립 재계산(work `analyze_ln.py`·`mask_ln.py`·`attr_ln.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1076_middle_review/`:
`recalc_lap1076.py` `3103268a…a4dc`(lap1074 middle 스크립트 기반, 계수·고정 카메라·EIP census 추가) → `recalc_lap1076.json` `2793ade1…adf6`.
pair-result SHA 접두 6개(ln1 `cbf36e5cb610`·ln2 `483923cdfc19`·ln3 `9afebfd0cb9f`·ln4 `2e2b3e374fdd`·ln5 `7c67943eea3b`·ln6 `f307b40cccc8`) = ESCALATE 기재와 일치, ln7 `20f07cc9307a`. stale_mask SHA = pair-result 기재 값 7/7, mask 픽셀 수 = trace `stale_pixels`(불일치 0). 대조: lap1073 x2·m1(H-LN 이전).
hold 창 = tick 계획 `down_input_tick..final_observation_tick`에 드는 ps3 present(lap1072·1074와 같은 정의).

| 항목 | 사전등록(lap1074 §4) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| L-0 hold 합 | 좌우 2/2 ≤10·ord 231~233 0·마지막40 0 | ln1·ln2 **3/3**(ord 226 = 3 px만, tick 24795, 카메라 (142,117)), ord 124·125·231·232·233 = 0, 마지막40 0/0; 기준 x2·m1 822/822 | 3/3 | 일치 PASS |
| L-0 계수 | mirrored_calls >0·reject 0 | ln1·ln2·ln7 `line_4659B0` invocations 1258·mirrored_calls 286·mirrored_pixels 966·reject target/size/guard 0/0/0 | 동일 | 일치 PASS |
| L-0 결정론 | — | ln1 = ln2 ps3 stale 열 전체 동일(SHA `189f5aa0aa61`), ln7 진단 hold 비영 = ord 226 3 px(tick 24796, 1 tick 차) | 동일 | 일치 |
| L-1 | 124/125/226 기록 | 124·125 → 0(같은 writer `0x4659B0` 귀속 성립), 226 3 px x799·y48..50 잔존 | 동일 | 일치 |
| L-1 귀속 | — | ln7 표본 (799,48)/(799,49)/(799,50) 3/3 마지막 writer tid 280 EIP `0x00465C71` 값 246 = scr(snap 85/92/92), stack `0x47933A`→`0x478E39`→`0x433B8C`, mod 0; 같은 present 쓰기 열 (799,48) `0x4662DE`→`0x465C1A`→`0x465C71`, (799,50) `0x4662DE`→`0x465C4A`→`0x465C71`; watch dropped/overflow 0, `0x465942` 0 | 동일(열은 미기재) | 일치 + 보강 |
| L-2 E-0 | 24칸 왕복·관측열 동일·clamp 없음·(158,101) | ln1·ln2·ln7 LEFT 24((−1,+1)×24)·RIGHT 24, ln3·ln4 UP 24·DOWN 24, 두 lane 관측열 동일·clamp_free·최종 (158,101), 입력 tick 목표 = 관측 | 동일 | 일치 PASS |
| L-2 E-1 | p95 ≤ 고정+16·tps 비 ≥0.95 | hold elapsed p95 7/7/7/7(ln1~4, 고정 7/6/7/6), ln7 11(고정 11, 진단), hold 창 tick 속도 20.00~20.03/s, present 간격 p50 50(hold 창 50) → 부하 변형 run 없음 | 7/7·6/7·비 ≥1.0029 | 일치 PASS |
| L-2 pair·안전 | PASS·0·cleanup·source_unchanged | ln1~4·6·7 pair PASS(gate 전부 PASS), 안전 7종 최대 0 ×7, 두 lane game_removed·source_unchanged true(source `b56986e0…`) | 동일 | 일치 PASS |
| L-3 UP/DOWN edge | ≤ 기준 1 | ln3 **0** | 0 | PASS |
| L-3 키 hold | ≤ 기준 1 | ln4 **0** | 0 | PASS |
| L-3 save000 | hold 0·gate = lap1071 e | ln5 hold 0·마지막40 0, status HOLD = input_effect HOLD·V2/V2s/V2q BLOCKED·나머지 PASS(기존 사유), 두 lane DOWN 24·UP 24·최종 (39,53) | 동일 | PASS |
| L-3 save006 고정 | 300..848 0 | ln6 867 present, 300..848 합 0·최대 0·마지막40 0 | 0 | PASS |

- 마스크 초기 프레임(ln2·ln3 frame 0 16,985 px, ln6 frame 6..12 ≈18~19k)은 로드 과도 구간이다: lap1063 nd1/nd2/diag1/diag2/s6·lap1065 nd1/nd2/t0/t1/s6의 ps3 첫 16 present stale 열과 값이 같다(lap1063 s6 frame 10..12만 +1, lap1065 s6 frame 10만 +236) → 회귀 아님·hold 창 밖.

## 2. objdump 재전사(원본 읽기만)

- `0x4659B0`(`objdump_4659b0_465a92.txt` `3a0ef6a5…5857`): 프레임 R = 반환 주소, args R+4 x0·+8 y0·+0xC x1·+0x10 y1·+0x14 색. dx = x1−x0·dy = y1−y0(int32), sx/sy = 부호(`neg; sbb`)를 x1/y1 인자 슬롯에 덮어씀, |dx|·|dy|(`cdq; xor; sub`), m = max → 반복 수 `lea eax,[esi+1]; inc eax` = **m+2**. 루프: plot(x,y,색) → ex += |dx|, ey += |dy| → ex > m이면 ex −= m·x += sx, ey > m이면 ey −= m·y += sy. 오차는 0에서 시작.
- 독립 Python 모델(`line_model_lap1076.py` `17cc75a9…fd76` → `.out` `2e82bce1…3e95`) |dx|,|dy| ≤20 전수 26,322 plot: **bbox 밖 최대 0, 마지막 plot ≠ 끝점 0건**. 예 (0,0)→(5,0) = (0,0)(0,0)(1,0)…(5,0), (0,0)→(5,2) = (0,0)(0,0)(1,0)(2,1)(3,1)(4,1)(5,2). 해석: 첫 반복 뒤 주축 누산 = m(초과 아님) → 진행 없음 → 첫 점 두 번, 이후 매 반복 1칸 → 마지막 plot = x0 + m = x1; 부축 진행 수 = (m+1)·|d|/m의 ceil − 1 = |d|.
- **lap1074 정정 1 철회(work 정정 확인):** "끝점을 주축으로 1칸 넘는다"는 틀렸다(오차 0 시작·첫 반복 무진행을 놓침). 영역 bbox ±1 여유는 diff 미러라 무해하므로 코드 변경 불필요. work 테스트 C 모델(`plot_outside_region`)은 이 전사와 같다.
- `0x465B30`(`objdump_465b30_465ca0.txt` `4c6f0381…50a1`): 두 꼭짓점 정렬 → 클립 `[ecx+0x4D0..0x4DC]` 밖이면 종료 → 각 변이 클립 밖이면 해당 변 플래그 0·좌표 클램프 → 위 가로줄(쓰기 `0x465C17`, 다음 `0x465C1A`)·아래 가로줄(`0x465C47`→`0x465C4A`)·**왼쪽 세로줄(`0x465C6E mov [edi+ebx],dl`→`0x465C71`)**·오른쪽 세로줄(`0x465C85`→`0x465C88`), `ret 0x14`. → ord 226 표본 writer `0x465C71`은 **기존 hook `0x465B30`(H-F2) 안 왼쪽 세로줄**이고, 쓰기 열상 한 호출이 (799,48) 위 줄·(799,48..50) 왼쪽 줄·(799,50) 아래 줄을 그렸다 = 왼쪽 변 x=799·y48..50 사각형.

## 3. 코드 검토

- `g1_line_region`: 차이를 int64로 계산해 int32 범위 밖이면 0(원본 int32 차와 다른 경우는 미러 안 함), bbox ±1 → 클립 교차 → 빈 교차 0, 결과 폭·높이 int64. 결함 없음.
- `mirror_line`: `mirror_rect_border7`와 같은 순서(guard → target(캐시·panel·stride·높이) → region → 크기 검사 → before 복사(800×600 버퍼) → 원본 정확히 1회 → `g1_overlay_blt_apply_tiled`(타일 320×160)). install `expected_line` = `83 EC 0C 8B 44 24 18`(objdump 7 B 경계 일치, 상대 주소 없음), restore 결과가 반환 조건(`!restored_line`)에 포함, `g_original_line = NULL`, `g_hook_line.installed`가 primitives_installed에 포함, 계수 6개 reset. `direct_draw_trace.c` `line_details[320]` 최악 233 B. 결함 없음.
- **ord 226 관계(새 근거):** `rect_border_465B30_reject_size`는 좌우 edge run에서만 34(lap1073 x2·m1, ln1·ln2·ln7)이고 UP/DOWN·키 hold·고정 카메라·save000 run은 0(lap1067 e1·lap1065 nd1/s6·ln3~ln6). `mirror_rect_border`는 비타일 `g1_overlay_blt_accepts`(폭 ≤320·높이 ≤160·**x + 폭 ≤ 800**)를 쓰지만, 형제 `mirror_rect_border7`·`mirror_line`은 화면 전체 + 타일이다. 화면 pitch 832(lap1074)·클립 `[ecx+0x4D8]`이 799보다 크면 왼쪽 변 x=799 사각형의 클립 결과가 x+폭 > 800이 되어 reject되고, 보이는 열 x799만 stale로 남는다 — **가설(미확인)**: 클립 값·reject 인자는 기록되지 않았다.

## 4. 판정

**H-LN PASS(partial) 수용.** L-0·L-2·L-3 PASS, L-1 ord 124·125 = `0x4659B0` 귀속, ord 226 3 px = 기존 hook `0x465B30` 미러 누락(writer 확인, reject 원인 미확인). 좌우 edge hold 창 822 → 3. 정정 1(lap1074 정정 1 철회)은 위 §2. 비차단 관찰: ln7 ord 226 tick 24796(ln1 24795, 진단 동반 1 tick). 제품 G1 마감·사용자 승인 아님.

## 5. work H-LB 사전등록(다음 work, Sonnet) — `0x465B30` reject 귀속 + 화면 클램프 미러

가설: ord 226 3 px(x799·y48..50)는 좌우 edge에서만 나오는 `0x465B30` 호출 34개 중 하나를 `mirror_rect_border`가 reject해 생긴다. 원인은 renderer 클립이 x 800 이상(stride 패딩)까지 열려 클립 사각형이 x+폭 > 800이 되는 것이다. 보이는 화면 [0,800)×[0,600)과 교차한 부분만 타일 미러하면(`g1_rect_solid_region`의 "stride 패딩은 미러하지 않음"과 같은 규칙) 사라진다.

1. **B-0 진단(env-gated, `rect_solid_reject_log` 방식 재사용):** `mirror_rect_border`가 reject할 때 이유·원 인자 4개·색·renderer 클립 4개·stride를 `layer_drift` 줄(type 새 문자, 기존 `s`/`z`/`q`/`w`와 충돌 금지 — lap1056 교훈)로 run당 최대 64줄. save006 LEFT,RIGHT edge 진단 1회로 34개 reject 인자·클립을 기록하고, (799,48..50)을 덮는 reject가 있는지 확인한다.
2. **B-1 테스트 먼저(RED→GREEN):** (a) 클립 xmax ≥800·사각형이 x=799에서 시작하는 경우 영역이 x 799 폭 1(화면 교차)로 나오고 reject되지 않음, (b) 화면 밖으로 완전히 나간 사각형은 0, (c) 320×160보다 큰 화면 안 사각형도 타일로 수용(rect_border7과 같은 전체 프레임 Scale2x 동등). 기존 `test_g1_rect_fill` 계약 유지.
3. **B-1 구현:** `mirror_rect_border` 영역 = `g1_rect_fill_region` 결과 ∩ [0,800)×[0,600), before 버퍼 800×600, `g1_overlay_blt_apply_tiled` + 타일 버퍼(`mirror_rect_border7`와 같은 형태). 원본 정확히 1회·좌표/색 하드코딩 0. B-0 결과가 가설과 다르면(reject 사각형이 화면 안 큰 사각형 등) 구현은 같은 타일 전환으로 하되 원인을 그대로 기록한다.
4. **실행(순차, load ≤8, 부하 변형 = 전체 또는 hold 창 present 간격 p50 >60 ms → 제외·1회 재실행):** save006 LEFT,RIGHT edge 비진단 2회 + UP,DOWN edge 1회 + 키 hold 1회 + save000 lap1071 e 옵션 1회 + save006 고정 카메라 1회.

PASS 기준:
- B-0: reject 34개 기록·(799,48..50) 덮는 reject 존재 여부와 클립 값 공개(가설 확인/반증 둘 다 기록).
- B-1: 좌우 edge 2/2 hold 창 stale 합 **0**(ord 226 = 0), `rect_border_465B30_reject_size` 34 → 0(아니면 이유 공개), 마지막40 0, `line_4659B0` 계수 lap1075와 같은 크기.
- 비회귀: E-0 24칸 왕복·관측열 동일·최종 (158,101), p95 ≤ 고정+16, pair PASS·안전 7종 0·cleanup·source_unchanged, UP/DOWN edge·키 hold hold 합 0, save000 hold 0·gate가 ln5와 gate별 동일, save006 고정 300..848 0, `rect_border_465B30_mirrored_pixels` 급증 시 이유 공개.
- FAIL: 크래시·안전 위반·원본 이중 호출·기존 경로 회귀. 실패 가설 2회면 BLOCKED.

그다음 후보: **H-LD 부하 동반 stale 재현**(candidate 게임 프로세스만 SIGSTOP/SIGCONT 듀티; save000 DOWN 정지 직후 tick ≈50762..50777 또는 save006 LEFT 정지 카메라 (142,117), 다른 프로세스 부하 주입 금지), 모서리(대각) 스크롤, HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비.

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT, focused(`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`·`test_g1_saved_scene_probe`). 결과는 STATUS에만 보강한다.
- 전체 `make check` SKIP(문서만 변경, source·하네스 불변·lap1075 full PASS 1652; 다음 work H-LB가 변경 뒤 실행).

## 다음 한 가지

work(Sonnet) H-LB: §5 B-0 → B-1 테스트 → 구현 → 실행. 그다음 H-LD. backlog: lane 위상 경합, lap1069 s2 117 px UNKNOWN, 미후킹 `0x467E60`, 진단 동반 영역, save000 overlay BltFast rejects, 다중 팝업 heal, 모서리 스크롤. G6/G7은 사용자 합격(APPROVALS lap989) 대기, 루프를 막지 않는다.

## 부록: lap1075 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1075 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-LN(`0x4659B0` 클립 직선 diff 미러) N-0 테스트·N-1 구현·N-2 실행 완료. work는 자기 결과를 승인하지 않으며 fresh Opus middle 독립 재계산과 수용 판정이 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1075_work_hln/ 의 {ln1..ln7}/pair-result.json·candidate/trace_raw.jsonl·(ln1,ln7) candidate/stale_mask.bin·ln7 candidate/{screen_watch,layer_drift}.jsonl 을 work 스크립트(analyze_ln.py·mask_ln.py·attr_ln.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: ln1 cbf36e5cb610 ln2 483923cdfc19 ln3 9afebfd0cb9f ln4 2e2b3e374fdd ln5 7c67943eea3b ln6 f307b40cccc8.
2. 검증 항목: (L-0) ln1·ln2 hold 창(ps3 ord 123..291) stale 합 3(822에서 감소; ord 124·125·231·232·233 = 0, ord 226 3 px x799 y48..50 만 남음)·마지막40 0·line_4659B0 invocations 1258·mirrored_calls 286·mirrored_pixels 966·reject 0/0/0. (L-1) ord 124/125 = 0 → 같은 writer(0x4659B0)로 귀속, ord 226은 ln7 진단 표본 3/3 마지막 writer tid 280 EIP 0x465C71 값 246=화면 값·스택 0x47933A→0x478E39 — objdump로 0x465C6E `88 14 1F mov [edi+ebx],dl` 다음 명령 = 기존 hook 0x465B30(H-F2) 안 조건부 가장자리 plot임을 재확인하고 rect_border_465B30_reject_size 34(ln1·ln7)와의 관계 판단. (L-2) ln1~ln4 두 lane 24칸 왕복·관측열 동일·clamp 없음·최종 (158,101)·p95 ≤ 고정+16·tps 비 ≥1.0029·pair PASS·안전 0·cleanup·source_unchanged. (L-3) ln3 UP/DOWN edge hold 합 0(기준 1)·ln4 키 hold 합 0(기준 1)·ln5 save000 hold 합 0 + gate가 lap1071 e와 gate별 동일(HOLD input_effect·V2 BLOCKED 기존 사유)·ln6 save006 고정 카메라 300..848 합 0·마지막40 0.
3. 코드 검토: tools/inmm_stub/g1_rect_fill.h `g1_line_region`(int64 bbox ±1 ∩ clip, int32 차이 overflow 시 미미러)·tools/inmm_stub/g1_mirror2x.c `mirror_line`(mirror_rect_border7 형제: guard→target→region→before 복사→원본 정확히 1회→g1_overlay_blt_apply_tiled)·install/restore/계수 reset·installed 플래그·`expected_line` 7 B `83 EC 0C 8B 44 24 18`(objdump 0x4659B0 재확인)·direct_draw_trace.c `line_details[320]`(둘째 builder 9,216, worst-case 테스트 PASS)·tests/test_g1_rect_fill.py 새 테스트 2건(`tests/test_g1_rect_fill.py`+mirror2x+overlay_blt+saved_scene_probe 273 passed). 정정 사항 확인: lap1074 정정 1("끝점을 주축으로 1칸 넘는다")은 objdump 0x465A1A..0x465A85를 옮긴 모델에서 재현되지 않음(실제 초과 0, 첫 점이 두 번 찍히고 마지막 plot이 끝점; 영역은 계약대로 +1 여유 유지) — 독립 재전사로 확인 필요.
4. 수용 시 다음 work 사전등록: ord 226 3 px = 0x465B30(rect_border) 미러 누락 귀속(reject_size 34 호출의 인자·좌표 기록, rect_solid_reject_log 방식 진단 전용) 또는 H-LD(SIGSTOP/SIGCONT 듀티로 candidate 프로세스만 느리게 해 x1류 부하 동반 stale 재현). backlog: lane 위상 경합, lap1069 s2 117 px UNKNOWN, 0x467E60, 진단 동반 영역, save000 overlay BltFast rejects, 다중 팝업 heal, 모서리(대각) 스크롤.
기록 docs/history/laps/20261006_lap1075_work_g1_hln_line_4659b0_diff_mirror.md. 변경(uncommitted): tools/inmm_stub/{g1_rect_fill.h,g1_mirror2x.c,g1_mirror2x.h,direct_draw_trace.c}·tests/test_g1_rect_fill.py. 원본 EXE b56986e0…08a8ac 불변.
```
