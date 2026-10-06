# 2026-10-06 | lap1078 | G1 middle — H-LB 독립 검수 + H-LD 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1077 work `loop/ESCALATE_SOL`(SHA256 `47945b51af15d9f9a9a80f4f9127e3845b083833c9f6f4f7e27a7568cb06957c`, 2,823 B, 원문은 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1076 §5 H-LB — save006 좌우 edge ord 226 3 px(x799 y48..50)는 `mirror_rect_border`가 reject한 `0x465B30` 호출이다. 원인은 renderer 클립이 stride 패딩(x≥800)까지 열려 x+폭>800이 되는 것이고, 화면과 교차한 영역을 타일로 미러하면 사라진다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 직접 재계산해 MATCH(읽기만). fixture: 비합성 save006·save000. lap1077 산출물만 읽음.
- 검수한 source 해시: 현재 트리가 lb1~lb6 `bridge/`와 byte 단위로 같다(`cmp` 불일치 0). `g1_rect_fill.h` `8443b983…6a2e`, `g1_mirror2x.c` `59ad70ca…3518`, `g1_mirror2x.h` `4ce14511…bbd`, `direct_draw_trace.c` `409e11e0…e358`, `tests/test_g1_rect_fill.py` `cb7fb89a…5f99`이고 work 기록의 접두와 일치한다. lb7(수리 전 진단) bridge와 현재 트리의 `diff`는 `g1_rect_screen_region` 추가와 `mirror_rect_border` 영역·버퍼·타일 전환뿐이다. reject 로그 `rect_border_reject_log`는 lb7에도 이미 있다. 따라서 lb7은 수리 직전 코드와 같다.

## 1. 독립 재계산(work `analyze_lb.py`·`mask_lb.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1078_middle_review/`:
`recalc_lap1078.py` `00222466…5086`은 lap1076 middle 스크립트를 바탕으로 B-0 type g 재집계, lb7 ps3 순번 보정, 로드 과도 마스크 대조를 추가했다. 출력은 `recalc_lap1078.json` `9deca69a…691d`, 표준 출력 `recalc_out.txt` `45366b5b…bb7`이다.
pair-result SHA 접두 7개는 ESCALATE 기재와 일치한다(lb1 `88cd4924b1c8`·lb2 `442d676d0ec7`·lb3 `31f6b448c3a2`·lb4 `875c524a45b2`·lb5 `f407219b9269`·lb6 `0aacf8a818b6`·lb7 `4446ac950d3b`). stale_mask SHA는 7/7 모두 pair-result 기재 값과 같고, mask 픽셀 수와 trace `stale_pixels`의 불일치는 0이다. 대조 run은 lap1075 ln1·ln2·ln5·ln6·ln7(H-LB 이전)이다. hold 창 정의는 lap1072~1076과 같다(`down_input_tick..final_observation_tick`에 드는 ps3 present).

| 항목 | 사전등록(lap1076 §5) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| B-0 reject 기록 | 34개·클립 공개 | lb7 type g **34줄**, 전부 why `size`·p225·색 246·클립 `[0,0,831,511]`·stride 832. 독립 영역(정렬→renderer 클립) = 로그 rx/ry/rw/rh 34/34, 34/34 모두 x+폭>800. 33개는 rx≥800(패딩 전용), 마지막 1개 (799,48)–(850,50) → 영역 x799 y48 폭33 높이3이고 화면 부분은 x799·y48..50뿐 | 동일 | 일치 PASS |
| B-0 덮음 | (799,48..50) 덮는 reject 여부 | lb7 수리 전 stale 3 px (799,48)(799,49)(799,50)이 모두 위 화면 부분 안(3/3) | 덮음 | 일치 PASS(가설 확인) |
| B-0 귀속 보강 | — | lb7 표본 3/3 마지막 writer tid 280 EIP `0x00465C71` 값 246 = scr(snap 85/92/92), 쓰기 열 `0x4662DE`→(`0x465C1A`/`0x465C4A`)→`0x465C71` = lap1076 ln7과 같다. watch dropped/overflow 0 | — | 일치 |
| B-1 hold 합 | 좌우 2/2 = 0·ord 226 0 | lb1·lb2 hold 창 ps3 123..291(169)에서 stale 합 **0/0**, 마지막40 0/0. 기준 lap1075 ln1·ln2·ln7은 3/3/3(ord 226, tick 24795/24795/24796, 카메라 (142,117)) | 0/0 | 일치 PASS |
| B-1 계수 | reject_size 34→0·`line_4659B0` 동일 | lb1·lb2 `rect_border_465B30_reject_size` **0/0**(기준 ln1·ln2·ln7·lb7 34). target/guard 0, `line_4659B0` 1258/286/966, reject 0/0/0 = ln1·ln2·ln7 | 동일 | 일치 PASS |
| 결정론 | — | lb1·lb2 ps3 stale 열이 공통 길이(1,177)에서 전부 같다(길이 1,181/1,177만 다름). hold 창 비영 0/0 | "결정론 동일값" | 일치 |
| E-0 | 24칸 왕복·관측열 동일·(158,101) | lb1·lb2 LEFT 24((−1,+1)×24)·RIGHT 24, lb3·lb4 UP 24·DOWN 24, lb5 DOWN 24·UP 24, 두 lane 관측열 동일·clamp_free, 최종 (158,101)·save000 (39,53) | 동일 | 일치 PASS |
| E-1 | p95 ≤ 고정+16 | hold elapsed p95/고정 p95: lb1 7/7·lb2 7/7·lb3 6/6·lb4 7/6·lb5 7/7·lb7 10/10(진단). hold 창 tick 속도 20.01/20.01/20.01/20.01/20.01/19.99 per s → 부하 변형 run 없음 | 동일 | 일치 PASS |
| pair·안전 | PASS·0·cleanup·source_unchanged | lb1~4·6·7 pair PASS, lb5 HOLD(아래). 안전 7종 최대 0 ×7, 두 lane game_removed·source_unchanged true | 동일 | 일치 PASS |
| UP/DOWN edge·키 hold | hold 합 0 | lb3 **0**·lb4 **0**, 마지막40 0 | 0 | PASS |
| save000 | hold 0·gate = ln5 | lb5 hold 0·마지막40 0, gate 11개가 lap1075 ln5와 gate별 동일(input_effect HOLD·V2/V2s/V2q BLOCKED·나머지 PASS = 기존 사유) | 동일 | PASS |
| save006 고정 | 300..848 0 | lb6 300..848 합 0·최대 0·마지막40 0 | 0 | PASS |
| mirrored_pixels | 급증 시 이유 | lb1·lb2 286,593/285,798, lb7 283,990, lap1075 ln1·ln2·ln7(수리 전) 285,952/286,433/286,080 | +~0.9%(새 x799 열) | 급증 없음(정정 2) |

- 로드 과도 마스크: lb2·lb3 frame 0 16,985 px와 lb6 frame 6..12(18,236~19,052 px)는 lap1075 ln2·ln3·ln6의 같은 frame 값과 7/7·1/1·1/1 일치한다. hold 창 밖이고 회귀가 아니다.

## 2. 코드 검토

- `g1_rect_screen_region`: 클립을 [0,screen_w−1]×[0,screen_h−1]로 줄인 뒤 `g1_rect_fill_region`(정렬·교차·빈 교차 0·폭 int64)을 그대로 쓴다. 클립이 화면 밖으로 완전히 나가면(예: xmin 810 > xmax 799) fill_region의 `xmin > xmax`에서 0이 된다. 원본이 쓰는 화면 픽셀은 정렬 사각형∩renderer 클립 안에 있고, 그 화면 부분은 영역에 모두 들어간다. 패딩(x≥800)만 빠진다. 결함 없음.
- `mirror_rect_border`: guard → target(캐시·panel·stride·높이) → screen region → before(800×600, 영역 폭 packed) → 원본 정확히 1회 → `g1_overlay_blt_apply_tiled`(타일 320×160, `g_rect_border_tile`). `mirror_rect_border7`·`mirror_line`과 같은 형태다. 영역이 화면 안으로 제한되므로 크기 검사 분기는 이제 도달할 수 없는 방어 분기다. `reject_size`는 실질적으로 tiled 적용 실패만 센다. 비차단이며 수정할 필요는 없다.
- 부수 효과: 수리 전에는 비타일 `accepts` 때문에 폭 >320 또는 높이 >160인 화면 안 테두리도 reject됐다. 이제는 타일로 수용한다. 이번 7 run의 비 edge reject_size는 원래 0이었으므로 관측 범위에서 행동 차이는 x799 열뿐이다.
- `rect_border_reject_log`: `layer_drift_on()`일 때만 기록하고 run당 64줄이 상한이다(`g_rect_border_reject_logged`는 run reset 블록에서 0). 줄 최악 길이는 약 280 B < 320 B다. type `g`는 lb7 기존 type(r/s/u/z/w/e/b/q/h)과 충돌하지 않는다.
- 테스트: `test_rect_screen_region_intersects_clip_with_visible_screen`은 x799 폭1·꼭짓점 교환·화면 안 동일·패딩 전용 0·클립 우선 reject·INT32 극단 전체 화면을 다룬다. `test_rect_border_hook_table_and_wrapper_contract`는 tiled·screen_region·tile 버퍼 계약을 확인한다. 사전등록 B-1 (c)(320×160보다 큰 사각형 타일 수용)는 INT32 극단 → 800×600 영역과 기존 `apply_tiled` Scale2x 동등 테스트(lap1065)로 충족한다.

## 3. 정정(비차단)

1. **ord 표기:** lb7에서 stale은 ps3 순번 **225**(mask key 225, hold 창 122..290)이다. lap1075 ln1·ln2·ln7은 226(창 123..291)이다. 같은 사건(tick 24795, 카메라 (142,117))이지만 lb7은 창 앞 ps3 present가 1개 적다. work의 "p225(ps3 ord 226)"는 lap1075 기준 이름이고 판정과 무관하다.
2. **mirrored_pixels 증가 해석:** work는 lb7 283,990 → 286,593/285,798(+~0.9%)을 "새로 미러된 x799 열·화면 교차분"으로 설명했다. 그러나 수리 전 ln1·ln2·ln7도 285,952~286,433이다. 차이는 run 변동 범위 안이며, 새로 미러된 픽셀은 수 px 수준이다. 급증이 없다는 결론은 같다.

## 4. 판정

**H-LB PASS(partial) 수용.** B-0은 가설을 확인했다(클립 xmax 831 = stride 832 − 1, 패딩까지 열린 renderer 클립 → x+폭>800 reject 34, 마지막 1개가 x799·y48..50을 덮음). B-1에서 좌우 edge hold 창 3 → **0**, reject_size 34 → 0이 됐고 비회귀 전부 PASS다. 이로써 save006 좌우·위아래 edge, 키 hold, save000 키 hold, save006 고정 카메라 모두 정상 속도 run에서 hold 창 stale 0이다. 제품 G1 마감이나 사용자 승인이 아니다. 남은 G1 항목은 부하 동반 stale(H-LD)·모서리 스크롤·HUD/GDI·전체 HD coverage·두 번째 장면·사용자 승인이다.

## 5. work H-LD 사전등록(다음 work, Sonnet) — 부하 동반 stale 재현·귀속

배경: 정상 속도 run에서는 0이지만 느린 lane에서만 정지 카메라 stale이 세 번 나왔다(lap1056 r1 save006 p651..664, lap1072 c 139·f 9,014 save000 DOWN 정지 직후 tick ≈50762..50777·f ord 107..120, lap1074 x1 save006 LEFT 정지 카메라 (142,117) ord 134..144 798~1,047 px/present). 모두 present 간격 p50 68~73 ms(정상 50)였다.
가설: present 간격이 늘어나면(게임 프레임 하나에 여러 sim tick) 카메라 정지 직후 화면에 남는 world 영역을 미러가 놓친다. candidate 게임 프로세스만 주기적으로 멈춰 재현할 수 있고, 재현되면 진단 표본으로 writer를 귀속한다.

1. **LD-0 하네스(테스트 먼저 RED→GREEN):** `tools/g1_saved_scene_probe.py`에 `--candidate-throttle STOP_MS:RUN_MS`(기본 꺼짐)를 추가한다. 대상은 **candidate lane의 private game 사본 EXE 프로세스 하나**뿐이다. PID는 그 lane이 띄운 프로세스 트리와 `/proc/<pid>/exe`·cmdline의 private 사본 경로가 둘 다 일치할 때만 고른다. baseline·wineserver·다른 프로세스와 전역 이름 매칭은 금지한다. 창은 `down_input_tick` 관측부터 `final_observation_tick`까지다. `finally`에서 SIGCONT를 반드시 보내고, 종료 시 상태가 `T`가 아님을 검증한다. 실제 stop 횟수·누적 ms를 pair-result에 기록한다. 테스트는 PID 선택 거부(경로 불일치·baseline·wineserver), finally SIGCONT, 옵션 파싱, 기본 꺼짐 시 기존 경로 불변을 다룬다.
2. **LD-1 재현(순차, load ≤8):** 듀티 20:30 ms(목표 present 간격 p50 ≈70 ms) 기준이다. (a) save000 DOWN,UP 키 hold(lap1071 e 옵션)는 마스크 ord 95..140, (b) save006 LEFT,RIGHT edge는 마스크 ord 120..150으로 각 2회. 재현이 0이면 듀티 40:30으로 한 번 더 시도한다.
3. **LD-2 귀속(재현 시):** 재현된 run과 같은 옵션에 `--layer-drift --screen-watch --drift-samples`(재현 마스크에서 고른 stale 좌표 3점)를 더해 1회 실행한다. 표본의 마지막 writer EIP·tid·값을 보고, 기존 hook 안인지 미후킹인지와 hook reject 계수를 함께 기록한다.

PASS / FAIL 기준:
- LD-0: 테스트 GREEN, throttle 끈 run의 행동 불변(기존 테스트 전부 PASS), 실제 run에서 stop 대상 PID가 candidate 사본 1개, 종료 뒤 정지 프로세스 0.
- LD-1: 실제 candidate present 간격 p50 ≥60 ms를 달성하고 정지 카메라 구간 stale(present당 ≥100 px)을 fixture 하나 이상에서 2회 중 1회 이상 재현하면 **REPRODUCED**다. 두 듀티 모두 0이면 **NOT_REPRODUCED**로 판정하고 backlog "부하 동반 stale"을 환경 전용 관찰로 닫는다(제품 수리 없음, 근거 공개).
- LD-2: 표본 3/3 writer 귀속(val==scr)이면 다음 수리 hook 후보를 정한다(수리는 별도 회차).
- 공통: 안전 7종 0·cleanup·source_unchanged. 다른 프로세스 신호·부하 주입이 0이어야 한다. baseline lane에는 throttle을 쓰지 않는다. lane parity·E-0 칸 수 차이는 기록만 하고 gate로 쓰지 않는다(candidate만 느리므로).
- FAIL: 정지된 프로세스 잔존·다른 PID 신호·크래시·안전 위반. 실패 가설 2회면 BLOCKED.

그다음 후보: 모서리(대각) 스크롤(`--terrain-scroll-edge` 대각 확장), HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비.

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT, focused 테스트(`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`·`test_g1_saved_scene_probe`)를 돌린다. 결과는 STATUS에만 보강한다.
- 전체 `make check`는 SKIP한다. 문서만 변경했고 source·하네스가 그대로이며 lap1077 full PASS 1653이 있다. 다음 work H-LD가 하네스 변경 뒤 실행한다.

## 다음 한 가지

work(Sonnet) H-LD: §5 LD-0 → LD-1 → (재현 시) LD-2. backlog: lane 위상 경합, lap1069 s2 117 px UNKNOWN, 미후킹 `0x467E60`, 진단 동반 영역 x301..334·y357..398, save000 overlay BltFast rejects, 다중 팝업 heal, 모서리 스크롤. G6/G7은 사용자 합격(APPROVALS lap989) 대기이며 루프를 막지 않는다.

## 부록: lap1077 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1077 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-LB(`0x465B30` reject 귀속 + 화면 클램프 타일 미러) B-0 진단·B-1 테스트·구현·실행 완료. work는 자기 결과를 승인하지 않으며 fresh Opus middle 독립 재계산과 수용 판정이 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1077_work_hlb 의 {lb1..lb7}/pair-result.json·candidate/trace_raw.jsonl·(lb1) candidate/stale_mask.bin·lb7 candidate/layer_drift.jsonl 을 work 스크립트(analyze_lb.py·mask_lb.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: lb1 88cd4924b1c8 lb2 442d676d0ec7 lb3 31f6b448c3a2 lb4 875c524a45b2 lb5 f407219b9269 lb6 0aacf8a818b6 lb7 4446ac950d3b.
2. 검증 항목: (B-0) lb7 layer_drift.jsonl type g 34줄 = rect_border_465B30_reject_size 34, 전부 p225·클립 [0,0,831,511]·stride 832, 33줄 x≥800 패딩 전용·마지막 (799,48)-(850,50) → 영역 x799 y48 폭33 높이3 이 ord 226 (799,48..50) 3 px 를 덮는지. (B-1) lb1·lb2 hold 창(ps3 ord 123..291) stale 합 0·마지막40 0·rect_border_465B30_reject_size 0·line_4659B0 invocations 1258/mirrored_calls 286/mirrored_pixels 966/reject 0. (비회귀) lb1~lb4 두 lane 24칸 왕복·관측열 동일·clamp 없음·최종 (158,101)·p95 ≤ 고정+16·pair PASS·안전 0·cleanup·source_unchanged, lb3 UP/DOWN edge·lb4 키 hold hold 합 0, lb5 save000 hold 0 + gate가 lap1075 ln5와 gate별 동일(HOLD input_effect·V2/V2s/V2q BLOCKED), lb6 save006 고정 300..848 합 0·마지막40 0, rect_border_465B30_mirrored_pixels 283,990(수리 전 lb7)→286,593/285,798 급증 없음.
3. 코드 검토: tools/inmm_stub/g1_rect_fill.h g1_rect_screen_region(클립을 화면으로 줄인 g1_rect_fill_region)·tools/inmm_stub/g1_mirror2x.c mirror_rect_border(guard→target→screen region→before 800×600 복사→원본 정확히 1회→g1_overlay_blt_apply_tiled)·rect_border_reject_log type g(64줄 상한·run마다 reset·layer_drift 켜졌을 때만)·tests/test_g1_rect_fill.py 새 테스트 1건+rect_border 계약 갱신(test_g1_rect_fill+mirror2x+overlay_blt 69 passed).
4. 수용 시 다음 work 사전등록: H-LD(candidate 게임 프로세스만 SIGSTOP/SIGCONT 듀티로 느리게 해 save000 DOWN 정지 직후 tick ≈50762..50777 또는 save006 LEFT 정지 카메라 (142,117) stale 재현) 또는 모서리(대각) 스크롤. backlog: lane 위상 경합, lap1069 s2 117 px UNKNOWN, 0x467E60, 진단 동반 영역, save000 overlay BltFast rejects, 다중 팝업 heal.
기록 docs/history/laps/20261006_lap1077_work_g1_hlb_rect_border_465b30_screen_clip_tiled.md. 변경(uncommitted): tools/inmm_stub/{g1_rect_fill.h,g1_mirror2x.c}·tests/test_g1_rect_fill.py. 원본 EXE b56986e0…08a8ac 불변.
```
