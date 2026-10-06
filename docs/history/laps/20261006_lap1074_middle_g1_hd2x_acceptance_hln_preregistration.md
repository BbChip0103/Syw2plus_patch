# 2026-10-06 | lap1074 | G1 middle — H-D2x 독립 검수 + H-LN 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1073 work `loop/ESCALATE_SOL`(SHA256 `709ebddef98b852626890bb62fecf388ce36ad18255cdf5448d07ad17a6198fd`, 3,675 B, 원문 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1072 §4 H-D2x — 현재 후보는 좌우 가장자리 포인터 hold 스크롤에서도 위/아래(H-D2e)와 같은 수준(hold 창 stale 합 ≤10)이다. 아니면 좌우에서만 드러나는 미후킹 writer가 나온다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기·objdump만). fixture: 비합성 save006. lap1073 산출물만 읽음.
- 검수한 source 해시: `tools/inmm_stub/g1_mirror2x.c` `10c98ad9…6819`(lap1072와 같음 = 제품 불변), 4 run `bridge/g1_mirror2x.c`·`g1_rect_fill.h`·`control_input_bridge.c` = 현재 트리 byte 동일. 하네스 `tools/g1_saved_scene_probe.py` `2930898d…e871`·`tests/test_g1_saved_scene_probe.py` `ab0f71af…2e53`(work 기록과 일치, 둘 다 git 미추적).

## 1. 독립 재계산(work `analyze_d2x.py`·`mask_x.py`·`attr_x.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1074_middle_review/`:
`recalc_lap1074.py` `9e880661…97da` → `recalc_lap1074.json` `708cf6ad…0f4d`, `objdump_465900_465a92.txt` `74b22313…62cf1`.
pair-result SHA 접두 4개(x1 `3e789a0b230f` x2 `7cb53244c47c` m1 `c43a86437c25` d1 `96aec052305c`) = ESCALATE 기재와 일치. stale_mask SHA = pair-result 기재 값 4/4, mask 픽셀 수 = trace `stale_pixels`(불일치 0). 대조: lap1067 e1·e2(UP/DOWN edge).
hold 창 = tick 계획 `down_input_tick..final_observation_tick`에 드는 ps3 present(lap1072와 같은 정의, 키 이름과 무관하게 첫/둘째 action tick).

| 항목 | 사전등록(lap1072 §4) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| E-0 칸 수 | 두 lane ≥20칸·같은 칸 수 복귀 | x2·m1·d1 두 lane LEFT 24(델타 (−1,+1)×24)·RIGHT 24((+1,−1)×24), `scroll_steps` 필드 동일 | 24/24 | 일치 |
| E-0 clamp·관측열·최종 | 없음·동일·(158,101) | clamp_free true 전부, cams_equal [T,T] ×3, 두 lane 최종 (158,101) | 동일 | 일치 |
| E-0 포인터 | GetCursorPos x 0/799·WM_KEYDOWN 0 | candidate input trace logical (0,300) 25/25/23·(799,300) 23/24/24(x2/m1/d1), WM_KEYDOWN 0, receiver_waived true | 미기재 | 충족(추가 확인) |
| E-1 | hold p95 ≤ 고정+16·tps 비 ≥0.95 | candidate hold elapsed p95 7/8/12(고정 7/8/11), hold 창 tick 속도 20.01/20.01/19.98 tick/s | 7/7·8/8·12/11·비 1.0028 | 일치 |
| E-2 | hold 합 ≤10(2/2)·마지막40 0 | **x2 822·m1 822**(ord 124=14·125=77·226=3·231=235·232=222·233=271, x2·m1 값까지 동일), d1 1,518(+123 199·219 179·242 253·243 65), 마지막40 0 ×3 | 822/822/1,518 | **FAIL 일치** |
| pair·안전·정리 | PASS·0·ok·source_unchanged | x2·m1·d1 pair PASS(gate 9개 PASS), 안전 7종 최대 0, cleanup game_removed true·source_unchanged true(두 lane, source SHA `b56986e0…`) | 동일 | 일치 |
| m1 마스크 bbox | — | 124 x0..10·y0..5 / 125 x0..74·y0..31 / 226 x799·y48..50 / 231 x460..590·y0..40 / 232 x395..516·y0..46 / 233 x329..454·y0..48, 쌍별 교집합 0(15쌍) | 동일 | 일치 |
| d1 귀속 | 표본 마지막 writer | 표본 (544,19)/(460,15)/(373,18)(watch addr − buffer `0x03412B40`, pitch 832) = p231/232/233, 3/3 마지막 writer EIP `0x00465942` tid 280 mod 0 값 255 = scr(snap 92/71/92), 직전 writer `0x004662DE`(캐시→화면), stack `0x465A3E`→`0x4D32E3`; watch dropped/overflow 0 | 동일 | 일치 |
| x2 대 m1 | 결정론 | ps3 열 공통 1,180 present 값 전부 동일(x2만 1개 더 김), hold 창 비영 목록 동일 | 동일 | 일치 |
| UP/DOWN 대조 | — | lap1067 e1·e2 hold 합 1/1(ord 125 1 px) | — | 기준 유지 |

## 2. objdump 재확인(원본 읽기만)

- `0x465900`: `8B 54 24 04 | 8B 81 D0 04 00 00 | 3B D0 | 56 …` — x = [esp+4]가 `[ecx+0x4D0]..[ecx+0x4D8]`, y = [esp+0xC](push esi 뒤)가 `[ecx+0x4D4]..[ecx+0x4DC]` 안일 때만 `[ecx+0x1514] + y·[ecx+0x10] + x`에 색 바이트를 쓴다(`0x46593F mov [esi+edx],al`, 다음 명령 `0x465942` = watch EIP), `ret 0xc`. 전체 .text에서 이 함수로 가는 call/jmp = **`0x465A39` 한 곳**, 즉시값 참조 0.
- `0x4659B0`: `83 EC 0C | 8B 44 24 18 | 53 …` = 3 + 4 = **7 B 명령 경계**(둘 다 상대 주소 없음, esp 상대 읽기는 같은 인자 배치 trampoline이면 동일), 인자 (x0, y0, x1, y1, 색) — `eax = arg3 − arg1`(dx), `ecx = arg4 − arg2`(dy). 내부 루프가 `0x465900`을 `0x465A39`에서 호출하고 `ret 0x14`(`0x465A8E`). 이 함수로 가는 call/jmp = **`0x4D32DE` 한 곳**(앞 `mov ecx,0xE5BF18`·`push 0xFF`·`0x436920` 두 번으로 월드→화면 두 점), 즉시값 참조 0. 저장소 `tools/inmm_stub/*.c|h`에 `4659B0`/`465900` 언급 0 = 미후킹.
- **정정 1(새 사실, 구현 필수):** 반복 횟수 = `lea eax,[esi+1]` → `inc eax` → **max(|dx|,|dy|) + 2회** plot. 첫 점이 (x0,y0)이고 매 반복 뒤 주축이 한 칸 진행하므로 마지막 점은 **끝점을 주축 방향으로 1칸 넘는다**(부축도 누적 오차로 최대 1칸). 따라서 미러 diff 영역을 두 끝점 bbox로만 잡으면 마지막 1 px이 영역 밖에 남는다 → H-LN은 bbox를 사방 1 px 넓힌 뒤 클립 사각형과 교차해야 한다. work 기록의 "두 점 사이 선"은 이 1 px을 빠뜨렸다.

## 3. 판정

- **x1 부하 변형 판정(정정 2):** work는 전체 run present 간격 p50 50 ms라 제외 기준(>60 ms)에 해당하지 않는다고 했다. 재계산하면 전체 p50은 50이지만 **hold 창 present 간격 p50 73 ms·최대 223 ms**(x2 50/57·m1 50/54·d1 50/73)이고, candidate 고정 구간 elapsed 중앙값 10.5 ms(다른 run 5.0)·hold 14→13.5 ms다. 게임은 포인터를 24/24회 가장자리로 받았는데(GetCursorPos (0,300) 24·(799,300) 24) candidate 카메라만 16/15칸 움직였다 = present 단위 가장자리 스크롤이 프레임 생략으로 줄어든 것. 기준의 목적(부하로 present가 늦어진 run 제외)에 맞게 **hold 창 기준으로 x1 = 부하 변형, 판정 제외**로 정한다. 앞으로 부하 변형 기준은 "전체 또는 hold 창 present 간격 p50 >60 ms"로 읽는다. 판정에는 영향 없음(x2·m1이 결정론 FAIL).
- **x1은 H-LD 증거로 편입:** x1 stale 10,291 중 ord 134..144(11 present, 798~1,047 px)는 카메라 (142,117) **LEFT 정지 직후 정지 카메라** 구간이다 — lap1072 c(DOWN 정지 직후 139)·f(9,014)와 같은 "느린 lane의 정지 카메라" 모양이 세 번째로 나왔다(마스크 덤프 구간 밖이라 위치는 미수집).
- **H-D2x E-0·E-1 PASS, E-2 FAIL 수용 → 결과 = 미후킹 writer 발견(사전등록의 두 번째 분기).** 귀속(`0x4659B0` 클립 직선 → `0x465900` plot, 색 255)은 writer EIP·호출처 1곳·값 = 화면 값으로 독립 확인. ord 124/125(91 px, 좌상단, LEFT 시작 직후)·226(3 px, x799, RIGHT 시작 직후)은 표본이 덮지 않아 **writer 미귀속 유지**(같은 선일 가능성은 추정일 뿐). 하네스 X-0 코드 검토(`_scroll_edge_point` LEFT x=origin.x·RIGHT x=origin.x+800·scale−1·y 중앙·놓음 중앙·잘못된 키 ValueError, `_scroll_edge_keys` 기본 `DOWN,RIGHT`→`UP,DOWN`, `_scroll_edge_option_error` 비기본 키는 `LEFT,RIGHT`/`RIGHT,LEFT`만, main 배선) 결함 없음, `tests/test_g1_saved_scene_probe.py` **205 passed/11.81s** 재실행. 제품 G1 마감·사용자 승인 아님.

## 4. work H-LN 사전등록(다음 work, Sonnet) — `0x4659B0` 클립 직선 diff 미러

가설: save006 좌우 edge hold 창 ord 231~233 stale(728 px)은 미후킹 `0x4659B0`이 그린 255색 선이며, 그 함수를 `mirror_rect_border7`와 같은 diff 미러로 감싸면 사라진다. ord 124/125/226이 같이 사라지면 같은 writer로 귀속한다.

1. **N-0 테스트 먼저(RED→GREEN):** (a) C 단위 테스트 — 원본과 같은 Bresenham(max+2회 plot·`0x465900` 클립)을 테스트 안에서 재현해, 수평·수직·대각·역방향·클립 경계 걸침·한 점(x0=x1,y0=y1) 선의 **모든 plot 픽셀이 미러 영역(끝점 bbox 사방 +1 px ∩ 클립) 안**임을 확인. (b) 영역 계산 helper가 화면 밖/빈 교차를 reject하는지. (c) `mirror_details`/계수 serializer 길이 테스트가 새 계수 포함 최악 합에서도 한도 이하인지(lap1051 W-S2 교훈).
2. **N-1 구현:** hook `0x4659B0`, old bytes `83 EC 0C 8B 44 24 18`(7 B, `G1HookState.original` 16 B 이하), thiscall 5인자 `(renderer, x0, y0, x1, y1, color)`·`ret 0x14`. `mirror_rect_border7`의 형제로: guard/target/size reject 동일 규칙, before 복사 → 원본 trampoline **정확히 1회** 호출 → `g1_overlay_blt_apply_tiled`로 영역만 미러. 색·좌표 하드코딩 금지. 계수 `line_4659B0_{invocations,mirrored_calls,mirrored_pixels,reject_target,reject_size,reject_guard}`. `0x465900`은 호출처가 `0x4659B0` 안 한 곳뿐이라 별도 hook하지 않는다.
3. **N-2 실행(순차, load ≤8, 부하 변형 = 전체 또는 hold 창 present 간격 p50 >60 ms → 제외·1회 재실행):** save006 `LEFT,RIGHT` edge 비진단 pair 2회(x2 옵션 그대로) + `UP,DOWN` edge 1회 + 키 hold(lap1065 nd 옵션) 1회 + save000 lap1071 e 옵션 1회.

PASS 기준:
- L-0: 좌우 edge 2/2 hold 창 stale 합 ≤10, **ord 231~233 각 0**, 마지막40 0, `line_4659B0_mirrored_calls` >0, reject 0(아니면 이유 공개).
- L-1: ord 124/125/226 결과를 기록(0이면 같은 writer 귀속, 남으면 UNKNOWN 유지 — 이 항목만으로 FAIL 아님).
- L-2: E-0·E-1 유지(24칸 왕복·관측열 동일·최종 (158,101)·p95 ≤ 고정+16·tps 비 ≥0.95), pair PASS·안전 7종 0·cleanup·source_unchanged.
- L-3 비회귀: UP/DOWN edge hold 합 ≤ 기준(lap1067 1), 키 hold 합 ≤ 기준(lap1065 nd 1), save000 hold 합 0·gate가 lap1071 e와 gate별 동일, save006 고정 카메라 300..848 0.
- FAIL: 크래시·안전 위반·원본 이중 호출·기존 경로 회귀. 실패 가설 2회면 BLOCKED로 결론.

그다음 후보(우선순): **H-LD 부하 동반 stale 재현**(candidate 게임 프로세스만 SIGSTOP/SIGCONT 듀티; save000 DOWN 정지 직후 tick ≈50762..50777 또는 save006 LEFT 정지 직후 카메라 (142,117) 구간, 마스크를 그 구간에 두고 진단 표본 귀속; 다른 프로세스 부하 주입 금지), 모서리(대각) 스크롤, HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT, focused(`test_g1_saved_scene_probe`·`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`). 결과는 STATUS에만 보강한다.
- 전체 `make check` SKIP(문서만 변경, source·하네스는 lap1073 full PASS 1650과 같은 해시; 다음 work H-LN이 변경 뒤 실행).

## 다음 한 가지

work(Sonnet) H-LN: §4 N-0 → N-1 → N-2. 그다음 H-LD. backlog: lane 위상 경합, lap1069 s2 117 px UNKNOWN, ord 124/125/226(H-LN에서 확인), 미후킹 `0x467E60`, 진단 동반 영역, save000 overlay BltFast rejects, 다중 팝업 heal, 모서리 스크롤. G6/G7은 사용자 합격(APPROVALS lap989) 대기, 루프를 막지 않는다.

## 부록: lap1073 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1073 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-D2x(save006 좌우 가장자리 포인터 스크롤) X-0·X-1·진단 실행 완료, E-2 FAIL 후 writer 귀속까지. work는 자기 결과를 승인하지 않으며 fresh Opus middle 독립 재계산과 수용 판정이 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1073_work_d2x/ 의 {x1,x2,m1,d1}/pair-result.json·candidate/trace_raw.jsonl·(m1,d1) candidate/stale_mask.bin·d1 candidate/{screen_watch,layer_drift}.jsonl 를 work 스크립트(analyze_d2x.py·mask_x.py·attr_x.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: x1 3e789a0b230f x2 7cb53244c47c m1 c43a86437c25 d1 96aec052305c.
2. 검증 항목: (E-0) x2·m1·d1 두 lane LEFT 24칸·RIGHT 24칸·clamp 없음·관측열 동일·최종 (158,101); x1은 candidate만 16/15칸·최종 (157,102)·hold 합 10,291·candidate present elapsed 중앙값 hold 창 14 ms(최대 32) — x1을 부하 변형으로 제외할지(present 간격 p50 50 ms라 사전등록 제외 기준 >60 ms에는 해당 안 함) 판정. (E-1) x2 p95 7/7 비 1.0028·m1 8/8·d1 12/11. (E-2) x2·m1 hold 창(ps3 ord 123..291) stale 합 822(ord 124=14·125=77·226=3·231=235·232=222·233=271, m1이 x2와 값까지 동일)·마지막40 0·안전 0; d1 1,518(진단 동반 소덩어리 ord 123 199·219 179·242 253·243 65). m1 마스크 bbox: 124 x0..10 y0..5, 125 x0..74 y0..31, 226 x799 y48..50, 231 x460..590 y0..40, 232 x395..516 y0..46, 233 x329..454 y0..48(서로 교집합 0, ≈65 px/present 이동). 귀속: d1 표본 (544,19)/(460,15)/(373,18) = ord 231/232/233 stale 픽셀, 마지막 writer 3/3 = tid 280 EIP 0x465942 값 255=화면 값, 스택 0x465A3E→0x4D32E3. 원본 objdump(읽기만, SHA b56986e0…08a8ac, 파일 오프셋 = VA−0x400000): 0x465900 = 8B 54 24 04 8B 81 D0 04 00 00 클립 1픽셀 plot(3인자·ret 0xc·쓰기 0x46593F·호출처 0x465A39 한 곳), 0x4659B0 = 83 EC 0C 8B 44 24 18 53 클립 직선(5인자 x0 y0 x1 y1 색·ret 0x14 @0x465A8E·호출처 0x4D32DE 한 곳, push 0xFF·0x436920 두 번), 저장소 g1_mirror2x.c에 둘 다 hook 없음.
3. 코드 검토: tools/g1_saved_scene_probe.py `_scroll_edge_point`(LEFT x=origin.x·RIGHT x=origin.x+800·scale−1·y 중앙·release 중앙, 잘못된 키 ValueError)·`_scroll_edge_keys`·`_EDGE_HORIZONTAL_KEYS`·`_scroll_edge_option_error`(기본 DOWN,RIGHT → UP,DOWN 불변, LEFT,RIGHT·RIGHT,LEFT만 추가 허용)·main 배선(`scroll_keys = _scroll_edge_keys(...) if edge else _parse_scroll_keys(...)`), tests/test_g1_saved_scene_probe.py 신규·수정 4건(`.venv/bin/python -m pytest tests/test_g1_saved_scene_probe.py` 205 passed). 제품 C/bridge 불변.
4. 수용 시 다음 work 사전등록: hook 0x4659B0(old bytes 83 EC 0C 8B 44 24 18 = 3+4 = 7 B 경계, thiscall ecx=0xE5BF18, ret 0x14) diff 미러(rect_border7 형제: 원본 정확히 1회 호출·before 버퍼 선행·직선 bbox 타일 미러) + x2 재실행(합 ≤10·ord 231~233 0·ord 124/125/226 귀속 확인)·save006 UP/DOWN edge·키 hold 비회귀·save000 비회귀. 그 뒤 H-LD(SIGSTOP/SIGCONT 듀티로 candidate 프로세스만 느리게 해 x1류 부하 동반 stale 재현). backlog: lane 위상 경합, lap1069 s2 117 px UNKNOWN, 0x467E60, 진단 동반 영역, save000 overlay BltFast rejects, 다중 팝업 heal, 모서리(대각) 스크롤.
기록 docs/history/laps/20261006_lap1073_work_g1_hd2x_left_right_edge_scroll_stale_4659b0_line.md. 변경(uncommitted): tools/g1_saved_scene_probe.py·tests/test_g1_saved_scene_probe.py(둘 다 git 미추적). 제품 C/bridge 불변.
```
