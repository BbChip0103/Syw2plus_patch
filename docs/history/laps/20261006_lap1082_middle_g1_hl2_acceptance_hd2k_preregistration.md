# 2026-10-06 | lap1082 | G1 middle — H-L2 독립 검수 + D-0 디스크·H-D2k 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1081 work `loop/ESCALATE_SOL`(SHA256 `759e6d984165c836c2e5b9ea851aec7f6f4ea4f20d799d4db98ab7d06052c03b`, 원문은 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1080 §5 H-L2 — 미후킹 `0x467E60`(클립 없는 좌우 반전 반투명 RLE, `ret 0x1c`, 7 인자)을 diff 미러하면 throttle 재현 stale ord 171..182가 0이 된다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 직접 재계산해 MATCH(읽기만). fixture: 비합성 save006·save000. lap1081 산출물만 읽음.
- 검수한 source 해시 접두: `tools/inmm_stub/g1_mirror2x.c` `fd66ba276ced9cef`, `g1_mirror2x.h` `6788f63f273d9158`, `direct_draw_trace.c` `8f4047823ae4f5d5`, `tests/test_g1_rect_fill.py` `61f301934256bdfe`. work 기록과 일치한다. hl1~hl6 각 `bridge/supply_bridge_build.json`의 stub 입력 56개 SHA256이 현재 트리와 모두 같고(불일치 0), 각 `_inmm.dll` SHA도 build json 값과 같다 → **현재 트리 = 6 run bridge**.

## 1. 독립 재계산(work `analyze_hl.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1082_middle_review/`:
`recalc_lap1082.py` `93b7fdf1…cc0a`(lap1080 middle 스크립트 기반, 고정 장면 ord 구간·ord 표·기준 대비 증가 검사 추가) → `recalc_lap1082.json` `8b8dbc9f…177a`, 표준 출력 `recalc_out.txt` `795bb290…24a7`, objdump `objdump_467e60_467fd0.txt` `e2c6ae32…a8ba`.
pair-result SHA 접두 6개는 ESCALATE 기재와 모두 일치한다(hl1 `6159fcc42d84`·hl2 `6d00bd7d4a3f`·hl3 `3dbcf93d5d56`·hl4 `6e8fe1978834`·hl5 `36606480b76f`·hl6 `b856388b47e9`). stale_mask SHA는 6/6 pair-result 기재 값과 같고, mask와 trace `stale_pixels` 불일치는 0이다. 기준: lap1079 ld7·ld8(throttle 40:30, 수리 전), lap1077 lb1~lb6(정상 속도, `0x467E60` hook 전). hold 창 정의는 lap1072~1080과 같다.

| 항목 | 사전등록(lap1080 §5) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| (a) ord 171..182 | 2/2에서 0 | hl1·hl2 **0/0**(ld7·ld8 각 9,802 = 746..974 ×12) | 0/0 | 일치 PASS |
| (a) hold 합·≥100 px | 다른 ord 증가 없음 | hl1 **640**(ord 123 199 (157,102) tick 24693·ord 140 257 (141,118) tick 24717·ord 191 184 (142,117) tick 24789), hl2 **199**(ord 123만). 마스크: hl1 ord 123 x0..31·y285..303, ord 140 x400..427·y310..328, hl2 ord 123만. 기준 max(ld7,ld8)보다 큰 present = hl1 ord 191 하나 | 640/199, 같은 ord | 일치(ord 191은 §3 정정 2) |
| (a) throttle | PID 1·정지 잔존 0 | hl1 pid 1·stop 120회·4,845.4 ms·최종 `D`, hl2 pid 1·120회·4,831.5 ms·최종 `R`, 둘 다 `final_state_not_stopped` true. hold 간격 p50 70/70·p95 75/74(고정 50), tps 20.03/19.96, elapsed p95 8/8. candidate 17/17칸(ld7·ld8과 같음, `terrain_scroll_parity` HOLD 예상대로), baseline 24/24, 최종 (158,101) | 동일(hl2 R만 서술) | 일치 |
| (a) 계수 | reject 0 | `blend_467E60` hl1 11/11/8,833 px/11, hl2 12/12/9,802 px/12, reject_* 4종 0 | 동일 | 일치 |
| (b) 정상 속도 | hold 0, 계수로 H-pos 판별 | hl3 PASS, hold 0·마지막40 0, **invocations 0** → H-pos 판별 불가. 두 lane 24/24칸·(158,101), 간격 p50 50·p95 53, elapsed p95 7, tps 20.0, 총합 291,382 = lb1·lb2 | 동일 | 일치 |
| (c) UP/DOWN edge | hold 0 | hl4 PASS, hold 0, UP/DOWN 24/24, elapsed p95 7(lb3 6·lb4 7), invocations 0 | 동일 | 일치 |
| (c) save000 키 hold | hold 0·gate = lb5 | hl5 hold 0·마지막40 0, DOWN/UP 24/24·(39,53), invocations 0. pair HOLD는 lb5와 같지만 **gate 구성은 다르다**(§3 정정 1) | "lb5와 동일 HOLD" | 정정 |
| (c) save006 고정 | 300..848 0 | hl6 총합 291,382·6..299 183,290·300..848 0·마지막40 0, stale 열 SHA `112d3f1d8936` = lb6 그대로 | 동일 | 일치 PASS |
| 공통 | 안전 7종 0·cleanup·source_unchanged | 6 run 안전 7종 최대 0, 12 lane `game_removed`·`source_unchanged` true | 동일 | 일치 PASS |

## 2. 코드·디스어셈블 검토

- 원본 `0x467E60`(독립 objdump, 위 파일): `83 ec 08 55 56` 5 B 경계, x·y·w·h `movsx` 16비트, 행 기준 `[ecx+0x1514]` + y×`[ecx+0x10]` + x, 목적지 읽기 `0x467ECC mov dl,[esi+ebp]` = 열 x+k, 쓰기 `0x467F93 mov [eax+esi-1],bl`(eax = w−k) = 열 x+w−1−k, `0xFE n` = k += n, 클립 필드(+0x4D0..) 접근 0건, `0x467FC6 ret 0x1c`. work 전사와 일치한다.
- `mirror_flip_blend7`: 인자 `(int16_t)` 부호 확장, 대상 검사(renderer `0xE5BF18`·캐시·panel 제외·stride·높이 600)·guard·`layer_drift_write_*`가 형제 `mirror_flip_blend`와 같다. 영역 = `g1_flip_rle_region`(사각형∩800×600). before 버퍼 800×600 ≥ 영역 최대, `g1_overlay_blt_apply_tiled` 인자 순서는 H-LB `mirror_rect_border` 호출과 같다. 원본은 7 인자 그대로 정확히 1회 부른다. install(old bytes `{0x83,0xEC,0x08,0x55,0x56}`)·restore·`g_original_flip_blend7 = NULL`·installed 검사·계수 8개 reset이 모두 있다. 결함은 없다.
- `direct_draw_trace.c`: `blend_467E60_*` 블록 최악 319 B < 버퍼 400. `mirror_details` 9,728은 테스트 최악 9,471을 담고, `trace_event_raw`는 `trace_record_serialize(line, 10240, …)` 경계 검사로 넘치면 기록을 버린다(메모리 넘침 없음). 6 run 모두 metrics 이벤트가 기록됐다.
- 테스트: C 모델 20,000회는 쓰기·읽기 열 ⊆ [x,x+w)와 화면 안 쓰기 ⊆ 영역을 검사하고, hook 계약 테스트는 1회 호출·순서·계수·bridge 문자열을 검사한다. 한계(비차단): 모델은 x+w > stride인 쓰기의 **다음 행 wrap 물리 위치**를 모델링하지 않는다. 코드 주석대로 wrap 행은 미러하지 않으며, `region.wrap`을 계산하지만 이 hook에는 `wrap_calls` 계수가 없어 런타임 발생 여부는 UNKNOWN이다(기존 backlog "wrap 쓰기 미추적"과 같은 범주).

## 3. 정정·관찰

1. **hl5 gate 구성:** work의 "gate = lap1077 lb5와 동일 HOLD"는 pair 상태만 맞다. lb5는 `terrain_scroll_parity` PASS이고, hl5는 HOLD다. 원인은 `complete_records_equal` false 하나다. 같은 sim tick 50753(`state_sim_tick` = before = after)에서 candidate lane이 wood 163,471·slot 66 x 65를 읽었고, baseline은 163,571·x 64를 읽었다. `final_full_state_diff`는 비었고 `end_game_state_equal` true다. 이것은 lap1072 정정 3(lap1071 h, tick 50753에서 원본 lane이 수입 전 값을 읽음)과 같은 tick 안 중간 읽기 경합이고, 이번에는 candidate 쪽에서 나왔다. hl5에서 `0x467E60` 호출은 0이었으므로 새 hook 쓰기와 무관하다. 비차단. 이로써 경합이 두 lane 모두에서 관측됐다 → 하네스 snapshot 원자성 문제로 backlog "lane 위상 경합"에 합친다.
2. **ord 140·191은 present 위상 잔여:** ord 140 = 257 px는 그 present의 sim tick이 24717일 때만(ld8·ld9·ld10·hl1) 나타나고, 24716이면(ld7·hl2) 0이다. ord 191 = 184 px는 tick 24789일 때만(ld10·hl1), 24788이면 0이다. 값과 위치는 수리 전·후 같다. hl1의 ord 191은 hook 회귀가 아니다(work 서술 "기준 ld10에도 있음"과 일치).
3. **보강 근거:** hl2 `blend_467E60_mirrored_pixels` 9,802는 수리 전 ld7·ld8 ord 171..182 stale 합 9,802와 정확히 같다(12 호출 ↔ 12 present). 미후킹 시 그 호출이 바꾼 화소가 그대로 stale였다는 것과 맞는다. hl1(11 호출, 8,833)은 분해하지 않았다.
4. 정상 속도에서 `0x467E60` 호출은 lb·hl 정상 run 전부 0이다. 수리 효과는 throttle 조건에서만 입증됐다(work 한계 ①). 사용자 환경 부하 동일성은 UNKNOWN이다.

## 4. 판정

**H-L2 PASS(partial) 수용.** (a) 2/2 ord 171..182 = 0, (b) hold 0(H-pos 판별 불가), (c) 비회귀 PASS다. 정정 1~2는 비차단이다. 이로써 정상 속도 run(좌우·위아래 edge·키 hold·save000·고정)과 throttle 재현 유닛 덩어리 모두 hold 창 stale 0이다. 남은 throttle 전용 잔여는 ord 123(199)·140(257, 위상)·191(184, 위상)이다. 제품 G1 마감이나 사용자 승인이 아니다.

## 5. 다음 work 사전등록(Sonnet) — D-0 디스크 회수 → H-D2k 모서리(대각) edge 스크롤

**D-0 (필수 선행, 게임 실행 전):** 현재 디스크 여유는 **6.4 GiB**다(`local/runtime` 273 GiB·1,227 dir, lap105x~108x 91 dir 122 GiB). 한 run은 game 사본 약 2.7 GiB와 prefix 잔여 약 1.3 GiB를 쓰므로 이 상태로는 실행하지 않는다. PROMPT 디스크 위생·provenance 규칙에 따라 이 루프가 만든 **종료된** private prefix만 회수해 여유 ≥ 20 GiB를 만든다.
1. 새 디렉터리 `local/maintenance/<KST날짜>_lap<N>_prefix_archive/`를 만든다. 기존 `local/maintenance/20261005_disk_cleanup_closed_prefixes_resume/archive.py` 절차를 **복사**해 쓴다(원본 스크립트는 고치지 않는다). 대상 root는 명시 목록으로 둔다(예: 오래된 `local/runtime/lap10[5-7]*`부터, 이번·직전 lap1081 run은 마지막).
2. prefix마다: 그 run의 pair-result에서 `source_unchanged`·원본 SHA·`cleanup.ok`·`prefix_processes_after` 비어 있음·`game_removed`를 확인한다. probe 프로세스·`lsof +D`·Wine `WINEPREFIX` 환경 참조가 0이어야 한다. 그 뒤 `tar.zst`로 묶고 tar 비교를 한다. batch마다 1개 이상은 실제 전체 restore로 파일 목록·크기·mode·SHA를 비교한다. 이 모두가 MATCH일 때만 해당 `prefix` 디렉터리를 지운다. `manifest.json`·`output`·로그·raw·PNG·공유 temp는 건드리지 않는다.
3. `report.tsv`·`summary.json`(SHA)을 남기고, 회수량과 여유를 기록한다. 압축 작업 공간이 모자라면 작은 batch로 나눈다. 다른 세션·다른 저장소 경로는 대상이 아니다. ≥ 20 GiB에 못 미치면 게임은 시작하지 않고 BLOCKED(수치·남은 후보)로 기록한다.

**H-D2k (D-0 PASS 뒤):** 아직 측정하지 않은 마우스 **모서리(대각)** edge 스크롤의 stale·입력 효과·성능을 잰다.
1. **K-0 하네스(테스트 먼저 RED→GREEN, 제품 C/bridge 불변):** `--terrain-scroll-edge`가 `--terrain-scroll-keys UPLEFT,DOWNRIGHT`·`UPRIGHT,DOWNLEFT`(역순 포함)를 받게 한다. `_scroll_edge_point` 모서리 = 창 꼭짓점(예: UPLEFT = origin, DOWNRIGHT = origin+(800s−1, 600s−1)), release는 중앙이다. 기존 UP/DOWN·LEFT/RIGHT 기본·검증 문구는 바꾸지 않는다. 한 칸 기대 이동은 두 변 부호의 합(UPLEFT = (−2,0), DOWNRIGHT = (+2,0), UPRIGHT = (0,−2), DOWNLEFT = (0,+2))을 **가설**로 둔다. 원본 lane 관측이 다르면 관측값을 기록하고 lane parity로만 판정한다. 하네스 기대값을 고쳐 통과시키지 않는다. `_scroll_clamp_free`는 모서리 키에 맞는 판정(관측 이동이 기대 방향과 같고 왕복 복귀)을 따로 두고 테스트한다.
2. **실행(순차, load ≤ 8, run마다 game 사본 삭제, 매 launch 전 여유 ≥ 10 GiB 확인):** save006 `UPLEFT,DOWNRIGHT` 2회, save006 `UPRIGHT,DOWNLEFT` 1회, save000(`--scene-actions none`) `UPLEFT,DOWNRIGHT` 1회, 비회귀 save006 `LEFT,RIGHT` edge 1회(= hl3). stale mask는 hold 창(ord ≈120..300) 범위로 둔다.
3. **측정·PASS/FAIL:** E-0 두 lane 같은 칸 수·같은 최종 카메라·왕복 복귀, 맵 경계 clamp 여부 기록. E-1 elapsed p95 ≤ 고정+16·tps ≈ 20. E-2 hold 창 stale 합 0·마지막40 0. 안전 7종 0·cleanup·source_unchanged, 새 reject 계수 급증 없음. 모든 모서리 run이 E-0~E-2 PASS이면(parity HOLD가 정정 1의 tick 안 읽기 경합뿐이고 최종 상태가 같으면 허용) **H-D2k PASS(partial)**다. stale > 0이면 같은 옵션에 `--stale-mask <해당 ord>` `--layer-drift --screen-watch` 진단 1회로 writer를 귀속하고 FAIL(귀속)로 기록한다. 안전 위반·크래시는 FAIL이다. 실패 가설 2회면 BLOCKED다.

그다음 후보: HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: throttle 전용 ord 123 writer 귀속(ord 140·191은 위상 잔여), `0x467E60` wrap 계수, lane 위상 경합(정정 1, 두 lane 관측), lap1069 s2 117 px UNKNOWN, 진단 동반 영역 x301..334·y357..398, save000 overlay BltFast rejects, 다중 팝업 heal, lap1072 c·f·lap1056 r1 UNKNOWN.

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT와 focused 테스트(`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`·`test_g1_saved_scene_probe`)를 돌린다. 결과는 STATUS에만 보강한다.
- 전체 `make check`는 SKIP한다. 문서만 변경했고 source·하네스는 lap1081 그대로이며, lap1081 full PASS 1663이 있다. 다음 work가 하네스를 바꾼 뒤 실행한다.

## 다음 한 가지

work(Sonnet): §5 D-0(디스크 ≥ 20 GiB, archive·restore 검증 뒤 prefix만 회수) → H-D2k K-0 → 실행. G6/G7은 사용자 합격(APPROVALS lap989) 대기이며 루프를 막지 않는다.

## 부록: lap1081 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1081 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-L2(`0x467E60` diff 미러) L2-0 테스트·L2-1 구현·실행 (a)(b)(c) 완료. work는 자기 결과를 승인하지 않으며 fresh Opus middle 독립 재계산과 수용 판정이 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1081_work_hl2 의 {hl1,hl2,hl3,hl4,hl5,hl6}/pair-result.json·candidate/trace_raw.jsonl·(hl1,hl2) candidate/stale_mask.bin 을 work 스크립트(analyze_hl.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: hl1 6159fcc42d84 hl2 6d00bd7d4a3f hl3 3dbcf93d5d56 hl4 6e8fe1978834 hl5 36606480b76f hl6 b856388b47e9. 기준: lap1079 ld7·ld8(throttle 40:30 hold 합 10,001/10,258, ord 171..182 746~974 px), lap1077 lb1·lb6.
2. 검증 항목: (a) hl1·hl2(save006 LEFT,RIGHT edge, --candidate-throttle 40:30, p50 70 ms) ord 171..182 stale = 0/0, hold 합 640/199(남은 것 = ord 123 199 px·hl1만 ord 140 257·191 184, 기준 값 이하), throttle PID 1개·final_state not T, 계수 blend_467E60 invocations 11/12·mirrored 전부·reject 0. (b) hl3 정상 속도 hold 0·blend_467E60_invocations 0(→ H-pos 판별 불가). (c) hl4 UP/DOWN edge 0, hl5 save000 DOWN,UP 키 hold 0(gate = lap1077 lb5 동일 HOLD), hl6 고정 300..848 0·총합 291,382=lb6. 공통: E-0 24칸 왕복·p95 elapsed ≤ 고정+16·안전 7종 0·cleanup·source_unchanged.
3. 코드·디스어셈블 검토: tools/inmm_stub/g1_mirror2x.c `mirror_flip_blend7`(g1_flip_rle_region 영역·int16 인자·before[800×600]+tile·g1_overlay_blt_apply_tiled·원본 1회·7 인자 전달·reject 계수)·install_one(old bytes 83 EC 08 55 56)·restore/reset·installed 검사, direct_draw_trace.c `blend_467E60_*` 8계수+mirror_details 9216→9728(trace_event_raw line[10240] 여유 확인), tests/test_g1_rect_fill.py 새 테스트 2(원본 objdump 전사 C 모델 20,000회·hook 계약). 원본 EXE `objdump -d -M intel --start-address=0x467E50 --stop-address=0x467FD0`: 0x467E60 83 ec 08 55 56, movsx word 인자 4개, 0x467F93 88 5c 30 ff mov [eax+esi-1],bl, 0x467FC6 ret 0x1c, 클립 접근 없음.
4. 수용 시 다음 work 사전등록 후보: 모서리(대각) 스크롤, throttle 전용 소잔여 ord 123(x0..31·y285..303)·140(x400..427·y310..328)·191 writer 귀속, HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: lane 위상 경합, lap1069 s2 117 px UNKNOWN, 진단 동반 영역 x301..334·y357..398, save000 overlay BltFast rejects, 다중 팝업 heal, 정상 속도에서 `0x467E60` 호출 조건(H-pos). 디스크 여유 7.4 GiB(local/runtime/lap1081_hl_* 각 1.2~1.4 GiB 보존) 확인 필요.
기록 docs/history/laps/20261007_lap1081_work_g1_hl2_467e60_flip_blend7_diff_mirror.md. 변경(uncommitted): tools/inmm_stub/g1_mirror2x.c·g1_mirror2x.h·direct_draw_trace.c·tests/test_g1_rect_fill.py. 하네스 불변. 원본 EXE b56986e0…08a8ac 불변.
```
