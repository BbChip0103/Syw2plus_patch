# 2026-10-06 | lap1061 | G1 work — H-D2w 스크롤 일시 stale writer 귀속(진단 전용)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 제품 source·테스트 변경 0.
- 가설: lap1060 §2(스크롤 일시 stale은 world 고정·결정론)이므로 같은 명령에서 같은 present의 같은 화면점이 stale이 되고, 화면 write watch(`--layer-drift --screen-watch`)로 마지막 writer를 귀속할 수 있다.
- 사전등록(lap1060 §4): W-0 pair PASS·안전 7종 0·cleanup/source_unchanged·I-0·hold 창 stale 열이 lap1058과 동일(다르면 공개) / W-1 표본 stale present 마지막 writer EIP 귀속 ≥90% / W-2 캐시 이동 누락(H1) vs 화면 직접 writer(H2) 판별 / FAIL 크래시·안전 위반·hold p95 > 고정+16.
- 변경 파일: 없음(uncommitted 기존 변경 그대로, `tools/inmm_stub/g1_mirror2x.c` SHA256 `b87e2f7d…`). 원본 EXE SHA `b56986e0…08a8ac` 읽기만(objdump), 비합성 save006.
- 실행(공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1061_work_d2w/`, 로그 `logs/gates/lap1061_d2w_{r1,r2}.log`): `run_d2w.sh` = lap1058 `run_d2z_mask.sh` 옵션(`--hd-source scale2x --terrain-scroll --terrain-scroll-hold --terrain-scroll-keys UP,DOWN --p4b-s-snapshot --reference-completed-states <lap888 …json> --stale-mask 129-143,227-230`)에 `--layer-drift --screen-watch --drift-samples "3,157;5,341;465,6"` 추가, save006 순차 2회(load ≤ 8 대기, exit 0·0, 옵션 조합 하네스 수리 불필요). 분석 `analyze_d2w.py`(표본 `s` 기록의 scr≠snap = stale, 같은 (present,표본)의 마지막 `x`(watch hit) = writer) → `analysis_d2w.json`.
- 산출물 SHA256 접두: r1 pair-result `63e36128…`·r2 `0186e212…`, layer_drift r1 `5cb481d7…`·r2 `cd8f52b1…`, screen_watch r1 `4e00f0d3…`·r2 `64cb93bd…`, analysis_d2w.json `cbdcd7a2…`, analyze_d2w.py `c403db8c…`, run_d2w.sh `ff4b882b…`.

## 측정(work 자체 계산, 판정 아님 — middle 독립 검수 필요)

| 항목 | 결과 |
|---|---|
| W-0 pair·안전·cleanup | pair PASS×2·terrain_scroll_parity PASS·V2s W-1 PASS·안전 7종 0/0·cleanup ok(game_removed, prefix 프로세스 0)·source_unchanged true/true·screen_watch status PASS(armed, k dropped 0·overflow 0) |
| W-0 I-0 | UP·DOWN 각 24칸·clamp_free·최종 카메라 (158,101)×2 lane |
| W-0 hold 창 stale 열 | lap1058과 **완전 동일하지 않음**: 169 present 중 주요 덩어리(5,602·6,484·4,357·7,367·12,976·7,941·2,732·…)는 같고, 일부 present가 ±수백 px 다름(4,357→4,611, 2,326→2,375, 2,569→2,777, 1,379→1,628, 1,012→1,220 등)·r1 끝에 246(>100) 1개 추가, r2에 131 1개 추가·>100 present 19→20. 진단 옵션이 장면을 소폭 바꿨을 가능성(원인 UNKNOWN) → 귀속은 이 run 기준. 두 run 사이도 r1/r2 일부 present(2,777 vs 2,569)가 다름 |
| W-0 I-1 | p95 고정/hold 10/11·12/12(≤ 고정+16), ticks/s 비 0.9965/0.9947(≥0.95) |
| W-1 귀속 | 표본 3점 × stale present 6개 = **18/18 귀속(100%)**, 마지막 writer val == 덤프 scr 18/18, r1·r2 동일. (0,·)(1,·) 표본 p129..134 / p135..140 = EIP **`0x00467CCF`**(게임 스레드 tid 280, 호출 복귀 `0x41A072` = `0x41A06D call 0x467B00`), (2,·) 표본 p135..137·p228..230 = EIP **`0x004687A3`**(tid 280, 호출 복귀 `0x41A132` = `0x41A12D call 0x4685C0`) |
| `0x467B00` | **hook(H-B4 `mirror_blend_clip`) 있음**. 그러나 `w` 레코드 12개(p129..140, 두 run 동일): 인자 (x −167, y −30…322 step 32, w 330, h 200), `why=reject_size`, `sb`→`sa`로 표본 값이 원본 호출 때문에 바뀜(예 p130 66→240). 사유 = 화면 교차 사각형이 `G1_OVERLAY_MAX_HEIGHT 160`(`g1_overlay_blt.h`, 버퍼 320×160) 초과(교차 163×≥161) → mirror 건너뜀. metrics `blend_467B00_reject_size` 15, reject_bounds 69,264 |
| `0x4685C0` | **hook 없음**(`g1_mirror2x.c`·tools 전체에 주소 없음, objdump: 함수 `0x4685C0..0x4687EB ret 0x14` = 5 스택 인자, 호출처 `0x41A12D`·`0x41ACE5`; `0x467B00`의 호출처 `0x41A06D`·`0x41AC45`와 같은 블록의 형제). 표본 (465,6) stale p135..137(UP)·p228..230(DOWN) 전부 이 함수 |
| W-2 | **H2(화면 직접 writer)**: 캐시 이동 누락(H1) 아님 — writer는 game 스레드가 화면 렌더러 버퍼에 직접 쓰는 `0x467B00`(hook이 size로 반려)과 `0x4685C0`(미후킹). wined3d 스레드 writer 0. UP 구간(좌측 띠+하단)은 `0x467B00` reject_size, 우상단 (465,6) 덩어리는 UP·DOWN 둘 다 `0x4685C0` |
| 표본 밖 | 이 귀속은 표본 3점 한정. 전체 stale 면적의 writer 분포(예: DOWN p227..230 상단 우측 x401..665 전체가 `0x4685C0` 하나인지)는 미측정 |

## 판정(work 자체 — middle 독립 검수 필요)

- W-1 **PASS(표본 한정)**, W-2 **H2 확정(표본 한정)**, FAIL 조건 해당 없음. W-0 중 "stale 열 동일"은 부분 불일치(공개). 제품 source 변경 0·수리 없음.
- 수리 후보(middle 판단 대기, work가 추측 구현 안 함): (R-1) `0x467B00` 반려 조건을 clipped 교차 높이 160 초과(실측 200)까지 처리(버퍼·`G1_OVERLAY_MAX_HEIGHT`/scratch 확대 또는 행 분할 미러) — 단 `g1_overlay_blt_apply`는 같은 상수를 공유하므로 영향 범위 점검 필요; (R-2) `0x4685C0`(5 스택 인자 RLE, `mirror_blend_clip`·`mirror_shade_rle`와 같은 형제) diff 미러 hook 신설(old bytes 확인 필요, 호출처 `0x41A12D`·`0x41ACE5`).
- 다음 한 가지: middle(Opus) 독립 재계산(새 스크립트) + H-D2r 사전등록(R-1/R-2 순서·PASS 기준·`0x4685C0` 인자 의미 objdump). `ESCALATE_SOL` 생성.

## 검사

- 기록·인계 freeze 뒤 `checks/safety.sh check`·CONTEXT 확인. 전체 `make check` SKIP(제품 source·테스트 불변, lap1056 full PASS 1639 유효; 이번 증거는 게임 2회 launch 분석, Fast 아님).
