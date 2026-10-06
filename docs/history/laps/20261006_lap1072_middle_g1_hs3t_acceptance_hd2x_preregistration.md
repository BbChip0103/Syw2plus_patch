# 2026-10-06 | lap1072 | G1 middle — H-S3t 독립 검수 + H-D2x 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1071 work `loop/ESCALATE_SOL`(SHA256 `d0039fbc59a0393e1f25fcfadff26b90f4444f091ff8a90996c71e9dbd052dbe`, 3,268 B, 원문 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1070 §4 H-S3t — save000 키 hold `DOWN,UP`의 UP+10 tick 단발 stale(윗줄 x702..704)은 미후킹 게임 writer 하나가 그린 것이고, 그 writer를 미러하면 사라진다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기·objdump만). fixture: 비합성 save000(a..f·h)·save006(g). lap1071 산출물만 읽음.
- 검수한 source 해시(work 기록과 일치): `tools/inmm_stub/g1_mirror2x.c` `10c98ad9…6819`, `g1_mirror2x.h` `1dc289d2…31c1`, `direct_draw_trace.c` `c0f0cffe…c32`, `tests/test_g1_rect_fill.py` `1bc85bbc…dcf`, 하네스 `tools/g1_saved_scene_probe.py` `8816512f…08a8a` 불변.

## 1. 독립 재계산(work `mask_t0.py`·`run_t*.sh` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1072_middle_review/`:
`recalc_lap1072.py` `9db40675…17db` → `recalc_lap1072.json` `36fd997d…6375`, `i1_lap1072.txt` `1018a410…b738`(I-1 고정/hold 창).
pair-result SHA 접두 8개(a `83441532` b `c741f116` c `8e5595f1` d `0c46953c` e `51fab299` f `24394b05` g `38d9b8f8` h `dbf05e3b`)는 ESCALATE 기재와 일치. stale_mask SHA = pair-result 기재 값(a·b·d·e·g·h 6/6), mask 픽셀 수 = trace `stale_pixels`(불일치 0). 대조: lap1069 nd1·d2·s1.
hold 창 = tick 계획 `down_input_tick..final_observation_tick`에 드는 ps3 present(lap1070과 같은 정의).

| 항목 | 사전등록(lap1070 §4) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| T-0 위치 | ≥1 run에서 UP+10 tick 부근 위치 확보 | a: ord 228·tick 50820·카메라 (53,67)·**3 px (702,0)(703,0)(704,0)**, hold 합 3·전체 3. b: 0. 두 run 모두 두 lane DOWN 24·UP 24칸·대각 1칸·clamp 없음·관측열 동일·최종 (39,53)·parity PASS | 동일 | 일치·PASS |
| T-1 귀속 | 표본 stale present ≥1의 마지막 writer | d: 표본 3점 = (703,0)(702,0)(704,0)(watch 주소 역산), p228에서 3/3 stale(scr 71/88/90 ≠ snap 59/64/83). 쓰기 열: `0x466FCB`(=snap 값) → **`0x468992`**(71/88/90, stack `0x41A1F5`) → `0x467CCF`(같은 값, tid 280, stack `0x41A072`). watch dropped/overflow 0. drift `w` p228 = `466BE0`·`467B00` clipped만(`468870` 기록 없음 = 미후킹) | 동일 | 일치·PASS |
| objdump `0x468870` | 경계·호출처 | `83 EC 14`(sub esp,0x14)·`8B 54 24 1C`(mov edx,[esp+0x1c]) = 7 B 경계, 다음 `53`. 목적지 `[ebx+0x1514]`·`imul [ebx+0x10]`, 클립 `+0x4D0/0x4D4/0x4D8/0x4DC`, 쓰기 `0x46898F mov [edx+eax],cl`, `0x4689B7 ret 0x18`. 전체 .text에서 `0x468870..0x468876`로 가는 call/jmp = `0x41A1F0 call` 1곳뿐(앞 `mov ecx,0xE5BF18`, 반환 `0x41A1F5` = watch stack), 즉시값 참조 0. 저장소에 lap1071 전 언급 0 | 동일 | 일치 |
| T-2 hold 창 | 비진단 2/2 합 ≤10·UP+10 위치 0 | **e 0·h 0**(hold ord 124..291 / 125..293), 전체 0·0, 마지막40 0·0 | 동일 | 일치·PASS |
| T-2 I-0/I-1 | 관측열 동일·p95 ≤ 고정+16·tps 비 ≥0.95 | e·h 두 lane 24·24칸·관측열 동일·최종 (39,53). elapsed p95 고정/hold e 8/9·h 7/7, tps 비 1.008·1.0043. present 간격 p95 e 55·h 53(수리 전 a 52·b 54·d 56) | p95 55/53(간격 지표) | 일치·PASS |
| 계수 | — | e `shade_468870` 1035/mirrored 101/px 1141/changed 18/clipped 8/wrap 934/reject_bounds 934/target·size·guard 0. h 1041/102/1284/19/9/940/939/0. wrap≥reject_bounds이고 화면 밖 호출이 전부 reject_bounds | 동일(e) | 일치 |
| 비회귀 save006 | g nd hold 합 1·pair PASS·ps3 stale 열 비회귀 | g pair PASS(gate 전부 PASS)·UP/DOWN 24칸·최종 (158,101)·hold 합 **1**(ord 125, tick 24694)·마지막40 0·**ps3 stale 열 해시 `8052cfdb4afd` = lap1069 nd1과 동일**(0..15 로드 과도 + 125)·`shade_468870` 50 호출 전부 reject_bounds | 동일 | 일치·PASS |
| 안전·정리 | 안전 7종 0·cleanup·source_unchanged | 8 run 안전 max 0, 두 lane `game_removed` true·`source_unchanged` true·source SHA `b56986e0…` | 동일 | 일치 |

## 2. 코드 검토

- `mirror_shade_clip`(g1_mirror2x.c 3894..3970)은 `mirror_shade_flip`(3806..3882)과 이름(`shade_flip`→`shade_clip`, `SHADE_FLIP`→`SHADE_CLIP`)만 다르고 본문 동일(직접 대조). 원본은 `g_original_shade_clip` 정확히 1회·인자 6개 그대로, before 버퍼는 원본 호출 전에 채움, 실패 시 `reject_size` 계수.
- `g1_flip_rle_region`(g1_rect_fill.h 76..98)은 사각형과 화면 [0,800)×[0,600)의 교집합. 원본 `0x468870`의 쓰기 = 사각형 ∩ 렌더러 클립 사각형 ⊆ 사각형이므로 화면 안 쓰기는 미러 영역의 부분집합 → 상위집합 조건 충족. `wrap`은 계수일 뿐 reject 사유가 아니다(교집합 공집합만 reject_bounds).
- install: `expected_shade_clip` = `83 EC 14 8B 54 24 1C`, `G1_SHADE_CLIP_LEN 7`(≤ `G1HookState.original` 16 B), `install_one`은 7 B를 trampoline에 복사 뒤 `jmp 0x468877`; 두 명령 모두 상대 주소가 없고 esp 상대 읽기는 wrapper가 같은 인자 배치로 trampoline을 호출하므로 같은 오프셋을 읽는다. 중간 진입 분기 없음(§1 objdump).
- restore/원복: `restore_hook(&g_hook_shade_clip)`·실패 시 전체 restore 거부 목록 포함·`g_original_shade_clip = NULL`·installed 체크 포함·계수 10개 리셋(5008..5017). accessor 10개(g1_mirror2x.h 200..209)·`shade_clip_details[480]` 포맷 리터럴 315 B·`%u` 10개 → 최대 395 B < 480.
- 판정: 결함 없음. 테스트 실행은 §5.

## 3. 판정과 정정

- **정정 1(work 수치 오류, 비차단):** f(수리 후, 부하 변형)의 hold 창 합은 work 보고 "15"가 아니라 **9,014**다 — ord 107..120(tick 50762..50777, 카메라 (54,68) 정지, DOWN release 50740 뒤) 72→**1,295**→…→13 감쇠 덩어리 + ord 132 15. work가 나열한 72·13·15도 합 15가 아니다. f는 candidate lane만 DOWN 15·UP 15칸(baseline 24·24)이라 parity HOLD(`same_camera_after_each_key` false), present 간격 p50 68·p95 132, tps는 19.8~19.9로 정상(프레임 생략형 부하). ps3가 204개라 요청 마스크 구간 220..240이 존재하지 않아 마스크 파일이 없다(c도 211개라 같음) → 위치 미수집.
- **정정 2(work 미보고, 비차단):** c(수리 전 진단, 부하 변형)는 candidate lane이 DOWN 17칸 1 action만 기록하고 UP action이 없다(최종 (56,70)); stale 139는 ord 113·tick 50765·카메라 (56,70) 정지 구간. → c·f 둘 다 **DOWN 정지 직후 tick ≈50762..50777, 느린 lane의 정지 카메라**에서 stale이 나왔다. 수리 전 c에도 있으므로 `0x468870` hook 탓으로 볼 근거는 없지만, 크기 차(139 vs 9,014)는 카메라가 달라 비교 불가.
  → backlog "부하 동반 일시 stale"의 **재개방 조건(2회 재현)이 충족됐다**(lap1056 r1 save006 + lap1071 c·f save000). 정상 간격 run 재현은 여전히 0.
- **정정 3(h 귀속 확정):** h의 `complete_records_equal` false = action 0 owner 0 wood. 두 lane 모두 `state_sim_tick` 50753인데 **baseline(원본) lane이 163,471, candidate가 163,571**. lap1069 s2(같은 tick 50753)는 두 lane 모두 163,571, 50751/50752 관측 run(a·b·d·e·lap1069 s1·d1·d2, 두 lane)은 모두 163,471 → tick 50753 안에서 수입(+100) 적용 전후를 읽은 **원본 lane의 스냅샷 읽기 위상 경합**이고 hook 무관(최종 상태 diff 빈, end_game_state_equal true). 76개 scroll parity 기록 중 자원 차이 첫 사례.
- **H-S3t PASS(partial) 수용** — T-0·T-1·T-2(비진단 2/2 hold 합 0·UP+10 위치 0, I-0/I-1, save006 비회귀 동일 열, 안전 0) 전부 사전등록 충족. 수리 전 정상 속도 재현 4/7(lap1069 d1·d2, lap1071 a·d)에 비해 수리 후 2/2 = 0은 통계상 약하나, 귀속은 writer EIP·호출처·값 열로 독립 확인. lap1069 s2 117 px는 UNKNOWN 유지. 제품 G1 마감·사용자 승인 아님.

## 4. work H-D2x 사전등록(다음 work, Sonnet) — save006 좌우 가장자리 포인터 스크롤

가설: 현재 후보(H-S3t 포함)는 좌우 가장자리 포인터 hold 스크롤에서도 위/아래 가장자리(H-D2e)와 같은 수준(hold 창 stale 합 ≤10)이다. 아니면 좌우 이동에서만 드러나는 미후킹/분할 경계 writer가 나온다.

1. **X-0 하네스(테스트 먼저):** `_scroll_edge_point`에 LEFT/RIGHT(누름: x = origin.x 또는 origin.x+800·scale−1, y = 화면 중앙; 놓음: 중앙)를 추가하고 `--terrain-scroll-edge`가 `--terrain-scroll-keys LEFT,RIGHT`(또는 RIGHT,LEFT)를 허용하게 한다. 기존 UP,DOWN 기본 경로 불변(기존 edge 테스트 그대로 통과), 키 receiver 면제 범위 동일. RED→GREEN.
2. **X-1 실행(비진단 pair 2회, 순차, load ≤8):** lap1067 edge 옵션 + 키 `LEFT,RIGHT`, save006. 첫 run에서 clamp가 나면 순서를 `RIGHT,LEFT`로 바꿔 2회를 다시 채운다(clamp run은 보존·판정 제외).
3. 진단은 hold 창 합 >10일 때만 1~2회(`--layer-drift --screen-watch`, 표본은 stale bbox 안).

PASS 기준:
- E-0: 두 lane 첫 키 ≥20칸·둘째 키 같은 칸 수로 복귀·clamp 없음·관측열 동일·최종 (158,101)·게임 `GetCursorPos` x = 0/799(logical) 관측·WM_KEYDOWN 0.
- E-1: hold p95 ≤ 고정+16·tps 비 ≥0.95.
- E-2: hold 창 stale 합 ≤10(2/2)·마지막40 0·pair PASS·안전 7종 0·cleanup·source_unchanged.
- FAIL: 크래시·안전 위반·기존 UP/DOWN edge 경로 회귀.
- 한도: 부하 변형 run(present 간격 p50 >60 ms)은 판정에서 빼고 공개 기록, 대신 1회 재실행.

그다음 후보(우선순): **H-LD 부하 동반 stale 재현**(재개방 — candidate 게임 프로세스만 SIGSTOP/SIGCONT 듀티로 느리게 해 save000 DOWN 정지 직후 tick ≈50762..50777을 재현, stale 마스크를 그 구간에 두고 진단 표본 귀속; 다른 프로세스 부하 주입 금지), 모서리 스크롤, HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT, focused(`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`). 결과는 STATUS에만 보강한다.
- 전체 `make check` SKIP(문서만 변경, source는 lap1071 full PASS 1649와 같은 해시; 다음 work H-D2x가 하네스 변경 뒤 실행).

## 다음 한 가지

work(Sonnet) H-D2x: §4 X-0 → X-1. 그다음 H-LD(부하 동반 stale 재현·귀속). backlog: lane 위상 경합(d2 baseline 23칸·h 원본 lane 수입 tick 읽기), lap1069 s2 117 px UNKNOWN, 미후킹 `0x467E60`, 진단 동반 영역 x301..334·y357..398, save000 overlay BltFast rejects, 다중 팝업 heal. G6/G7은 사용자 합격(APPROVALS lap989) 대기, 루프를 막지 않는다.

## 부록: lap1071 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1071 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-S3t(save000 UP+10 tick 단발 stale 귀속·수리) T-0~T-2 실행 완료. work는 자기 결과를 승인하지 않으며 fresh Opus middle 독립 재계산과 수용 판정이 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1071_work_hs3t/ 의 {a,b,c,d,e,f,g,h}/pair-result.json·candidate/trace_raw.jsonl·(a,b,d,e,g,h) candidate/stale_mask.bin·(c,d) candidate/{screen_watch,layer_drift}.jsonl 를 work 스크립트(mask_t0.py·run_t*.sh) 없이 새 스크립트로 재계산. pair-result SHA 접두: a 83441532 b c741f116 c 8e5595f1 d 0c46953c e 51fab299 f 24394b05 g 38d9b8f8 h dbf05e3b.
2. 검증 항목: (T-0) a ps3 ord 228 tick 50820 카메라 (53,67) 3 px (702..704,0)·b 0. (T-1) d watch p228 표본 (703,0)/(702,0)/(704,0) 마지막 writer = tid 280 EIP 0x467CCF 이며 값이 앞 writer EIP 0x468992(71/88/90)와 같고 snap=59/64/83에 머묾; 원본 objdump(읽기만, SHA b56986e0…08a8ac) `0x468870` = 83 EC 14 8B 54 24 1C 7 B 경계·thiscall 6인자·클립 +0x4D0..0x4DC·쓰기 0x46898F(watch EIP 0x468992)·ret 0x18(0x4689B7)·호출처 0x41A1F0 한 곳(ecx=0xE5BF18), 저장소에 이전 hook 없음. (T-2) e·h hold 창(ps3 ord 124..292) stale 합 0·마지막40 0·p95 55/53·안전 0·cleanup·source_unchanged, shade_468870 계수(e: 1035/101/18/8/reject_bounds 934). f = 부하 변형(p50 68·p95 131·ps3 204, 합 15, 수리 전 c도 p50 67에서 stale 139) 판정 확인. h terrain_scroll_parity HOLD = complete_records_equal false 하나(action0 owner0 wood +100 수입 tick 위상, 최종 diff 빈) → 화면 hook 무관 위상 경합인지 확인. g(save006 nd) exit 0·pair PASS·hold 합 1(ord 125)·ps3 stale 열 17개가 lap1069 nd1과 값까지 동일.
3. 코드 검토: tools/inmm_stub/g1_mirror2x.c `mirror_shade_clip`(mirror_shade_flip 이름 치환 복제 여부, 원본 정확히 1회 호출·before 버퍼 선행·g1_flip_rle_region 화면 교집합이 클립 쓰기의 상위집합인지), install `G1_SHADE_CLIP 0x00468870u` LEN 7 old bytes 83 EC 14 8B 54 24 1C(esp 상대 둘째 명령은 trampoline이 같은 스택 프레임에서 실행), restore/원복/installed 체크·계수 리셋, g1_mirror2x.h accessor 10개, direct_draw_trace.c shade_clip_details(mirror_details 9216 worst-case 테스트 통과), tests/test_g1_rect_fill.py `test_shade_clip_hook_table_and_wrapper_contract`. `.venv/bin/python -m pytest tests/test_g1_rect_fill.py tests/test_g1_mirror2x.py tests/test_g1_overlay_blt.py` 66 passed.
4. 수용 시 다음 work 사전등록: ① 좌우 가장자리·모서리 스크롤(H-D2e `--terrain-scroll-edge` 확장), ② HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비 중 선택. backlog: lane 위상 경합(d2 baseline 23칸·h wood +100), 부하 동반 stale(c·f·lap1056 r1), lap1069 s2 117 px UNKNOWN, 0x467E60, 진단 동반 영역, save000 overlay BltFast rejects, 다중 팝업 heal.
기록 docs/history/laps/20261006_lap1071_work_g1_hs3t_save000_up10_unhooked_468870_shade_clip_mirror.md. 변경(uncommitted): tools/inmm_stub/g1_mirror2x.c·g1_mirror2x.h·direct_draw_trace.c, tests/test_g1_rect_fill.py. 하네스 불변.
```
