# 2026-10-06 | lap1052 | G1 middle — W-S2 + H-X 독립 검수 → work H-Y(save006 늦은 stale 블록 재현·위치) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·source 변경·commit은 0이다.
- 검수 대상: lap1051 work W-S2(`mirror_details` 두 번째 builder 최악 합 테스트 수리·크기 7200→8192)와 H-X(`0x4689C0` 반전 목적지 리맵 RLE 6인자 diff 미러 `mirror_shade_flip`). lap1050 §다음 work의 사전등록 X-S·X-0~X-5와 대조했다.
- 처리한 인계: `loop/ESCALATE_SOL`(lap1051 work, 1,452 B, SHA256 `44f03a1e22653bb4a514eb97645a262a023a4b682b9e6e965f8e2ceb3bfaf985`). 원문은 아래 부록에 두고, 처리한 뒤 파일을 삭제했다.
- 변경 파일: 이 기록, `docs/STATUS.md`(압축 포함), `docs/history/20261006_status_lap1052_precompaction.md`(압축 전 STATUS 원문). source/test 변경은 0이다.
- 원본 SHA / 환경 / fixture: 원본 EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` sha256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 다시 확인했다. 새 6 run과 기준 8 run 모두 private EXE 앞 16자가 일치한다. fixture는 save000(index 1)과 save006, 격리 prefix/display. 현재 source `g1_mirror2x.c` `e9620997…3513`·`g1_mirror2x.h` `35b5d76d…5be5`·`direct_draw_trace.c` `9fa3390c…0c9a`·`test_g1_rect_fill.py` `ae6e9e66…de29`는 work 기록과 같고, 6 run bridge 사본 3개 파일과 byte 일치한다(`cmp`).
- 재계산: 공유 temp `20261006_lap1052_middle_review/`. work의 `analyze_x_*.py`·`isect_x.py`·`setdiff_x.py`와 제품 helper는 쓰지 않았다. middle 소유 lap1050 재계산 코드를 문자열 치환으로 옮겨(run 집합·표본 좌표·H-X family/함수 범위·기준 B 합집합 추가) 새로 만들었다.
  - `recalc_lap1052.py` `3d4b6cae…b5ef` → `recalc_lap1052.json` `4af6d3aa…2e96`(출력 `recalc_lap1052.txt` `61092843…f291`). 대상은 새 6 run(lap1051 w r1/r2·s0 r1/r2·s6 r1/r2)과 기준 8 run(lap1049 w·s0·s6 각 r1/r2, lap1047 s0 r1/r2)이다.
  - `variant_lap1052.py` `2af28867…226b` → `variant_lap1052.json` `fe0e4625…1e9a`: X-2 기준 B 잔여 픽셀을 H-X 이전 save000 run 25개(lap1039 w·s0·ctl, lap1041 s1 r2/r3·s2·s3, lap1045 w·s0, lap1047 w·s0, lap1049 w·s0; lap1041 s1_r1 무효 run 제외)와 프레임별로 대조했다.
  - `tail_s6_lap1052.py` `24116abb…3687` → `tail_s6_lap1052.json` `99d3bc19…952a`: save006 run 10개(lap1039·1045·1047·1049·1051)의 present별 `stale_pixels` 늦은 구간과 save000 창별 합.
  - `details_worst_lap1052.py`(lap1050 스크립트 복사, 로직 동일) → `details_worst_builder2_lap1052.json` `b7a2e0b9…25ac`, 합 `details_sum_lap1052.txt` `1f1430fb…6549`.
  - objdump 직접 재생성 `od_4689C0_lap1052.txt` `6559bf0b…44b9`(lap1050 판과 비교 범위 끝 nop 4줄 외 동일). wrapper diff `diff_wrapper_lap1052.txt`(빈 파일).

## 재계산 결과(판정 불일치 0, 정정 3건)

| 항목 | lap1051 work 보고 | lap1052 재계산 |
|---|---|---|
| X-S W-S2 | RED 7,288 > 7,200 → 8,192 GREEN, 최악 7,683 | **같음.** 고친 테스트 함수를 lap1049 bridge `direct_draw_trace.c` 사본에 그대로 돌리면 `(7287, 7200)` FAIL, 현재 source에서 PASS. 독립 스크립트 합: own 683 + sub 6,953(20 블록) + 리터럴 46 + NUL = **7,683 ≤ 8,192**(여유 509 B, `shade_flip_details` 최악 395 ≤ 480). 첫 builder `[7200]` 불변 |
| X-0 안전·cleanup·source_unchanged | 0 / true / true | 6 run 모두 안전 7종 max 0, cleanup·source_unchanged [true,true], trace JSONL 손상 0, ps3 410/411/410/412/843/893 |
| X-0 항등식 | 87 = 76 + 11, 86 = 75 + 11 | **같음.** `shade_4689C0` w r1 87 = 76 + reject_bounds 11, w r2 86 = 75 + 11, s0 r1·r2 87 = 76 + 11(target/size/guard 0, clipped 22/21/22/22, changed 67, mirrored_pixels 8,219/8,169). save006 invocations 0. 기존 8 family 6 run 모두 성립(`shade_4687F0` save000 190 = 183 + 7 유지) |
| 무장·selftest | PASS·fail 0 | selftest PASS, 무장 52 round, fail 0, 모든 round 좌표 = 표본 3점, dropped/overflow 0 |
| **X-1** (783,377) | 3/run → 0/0 | **같음.** 기준 lap1049 w r1/r2: 3(`0x468A28`, p304..305·p366, 값 일치 3/3). 새: 0/0, `u` 5, hit 729/728 |
| X-1 (786,220)·(718,452) | 0/0·0/0 | **같음.** `u` 4·5, hit 452·447/449 |
| X-1 미러 작동 | `w` 17/18 | **같음.** `0x468A28` watch hit은 새 run에도 pt0 3·pt2 1/run 남는다. drift `w` f=4689C0 17/18건(mirrored 15/16·clipped 2/2). stale이 사라진 이유는 쓰기 제거가 아니라 diff 미러 반영이다 |
| **X-2** 마지막40 | 0/0 | **0/0**(watch), 성능 0/0 |
| X-2 새 r1∩r2 ∖ 기준 A(lap1049 w r1∪r2) | 308 px / 4 프레임 | **같음.** 298·308·318·328 각 77. 제거 1,495(174 88·294 144·298 271·308 287·318/328/338 186·352 25·366 122) |
| X-2 새 r1∩r2 ∖ 기준 B | 172 px / 4 프레임 | **같음.** 각 43 px, bbox y218..224×x240..299 |
| **X-2 기준 B 변형 판정(독립)** | UNKNOWN(대조 안 함) | **run 변형으로 닫음.** H-X 이전 run 합집합이 4 프레임 모두 43/43을 덮는다. 개별로 4 프레임 전부 덮는 H-X 이전 run이 5개다: lap1039 w_r1, lap1041 s1_r2·s3_r1, lap1045 w_r1, **lap1049 s0_r2(H-W 제품, H-X만 없음)**. 이 5 run은 프레임 318·328에서 새 w r1·r2와 마스크가 픽셀 단위로 같다(합 303 변형). 새 w 두 run은 4 프레임 모두 303 변형이다 |
| X-2 성능 pair | 새∖기준 0 | **같음**(기준 lap1049 s0, 기준 B 모두 0). 새 s0 r1·r2는 4 프레임 모두 412 변형 |
| **X-3** 성능 pair | p95 7/7, tick 비 1.000 | **같음.** 히스토그램 nearest-rank p95 7/7, 평균 5.093/5.095(기준 lap1049 s0 5.409/5.315), 10ms 이상 1/8, pair tick 비 1.0000/1.0000(lap1049 1.0025는 기준 쪽 tick 차이). 시작 load 4.09/4.37. watch run p95 11/12(기준 lap1049 w 10/11, 비gate) |
| **X-4** save006 | steady 38 + 880 신규 0, pair PASS | 사전등록 지표는 **같음**(공통 50 프레임, 새 r1∩r2 비0 = 6..12뿐, steady 38 신규 0, 기준 대비 초기 프레임 ±1 px). pair PASS(exit 0) 2회. **단 정정 2·3 참조** |
| X-5 경계 | wrap 0, 범위 이탈 0/35 | **같음.** `shade_4689C0_wrap_calls` 0, drift `w` 35건 중 x<0 또는 x+w>stride(832) 0 |

**정정 1 — 이름(비차단).** 사전등록은 계수 접두사를 `shade_flip_4689C0_*`로 적었으나 구현은 `shade_4689C0_*`다. H-W의 `shade_4687F0_*`와 같은 규칙이고 테스트·요약·분석이 일관되므로 그대로 둔다.

**정정 2 — X-4 "880 포함" 범위.** save006 r1은 ps3 843 present에서 끝나 880 덤프가 없다(마스크 50개). r1∩r2 공통은 50 프레임이고 880 포함 판정은 r1에서 불가능하다(lap1040 정정과 같은 유형).

**정정 3 — save006 늦은 stale 블록(새 관측, work 미보고, 원인 UNKNOWN).** 마스크 덤프 ordinal은 ps3 present 순번이다(`g1_mirror2x.c:1467`). 그런데 present별 `stale_pixels`를 보면 덤프 사이 구간에 work가 보고하지 않은 일정 크기 블록이 있다.
- lap1051 s6 r1: p782..834(53 present) **434 px 고정**, p835에서 0. 이 때문에 **마지막40 중앙값이 434**다(기준 lap1049 s6 0/0).
- lap1051 s6 r2: p433..474(42 present) **360 px 고정**, p67 243 px 1회.
- 같은 판정 방식의 이전 run: H-V/H-W 제품 save006 4 run(lap1047·1049 각 r1/r2)은 p65..67의 1 px 외에 늦은 stale이 **0**이다. H-V 이전(lap1039·1045) 4 run은 p40부터 길게 이어지는 꼬리(769~3,101 px, 증가형)가 있었다. 이번 블록은 크기 고정·구간 한정이라 모양이 다르다.
- 두 블록 모두 덤프 프레임(300·301·585..620·880) 사이에 있어 위치는 마스크로 알 수 없다. pair gate는 이 지표를 보지 않아 PASS다.
- 귀속: save006에서 `shade_4689C0` 호출은 0이다. 그러니 H-X wrapper 자체가 이 픽셀을 쓰거나 놓칠 수 없다. 이번 lap의 다른 source 변경은 metrics 문자열 버퍼 크기(8192)와 테스트뿐이다. 그래서 H-X 인과는 낮게 본다. 하지만 H-X 제품 2/2 run 발생, 직전 제품 0/4 run이라 우연이라고 단정하지도 않는다. **UNKNOWN**으로 두고 다음 work H-Y에서 재현·위치를 먼저 확인한다. run 끝 무렵 load가 높았다(work 기록 9.9~17.8, 다른 저장소 세션).

## 코드 검수

- `mirror_shade_flip`(`g1_mirror2x.c:3573`, 77줄)은 `mirror_shade_rle`(`:3487`)에서 `shade_rle→shade_flip`·`SHADE_RLE→SHADE_FLIP`·`4687F0→4689C0`만 치환한 것과 **diff 0**이다. 원 인자 6개를 한 번 넘기고, x·y·w·h는 int32, 화면 교집합 `g1_flip_rle_region`, 전용 before 버퍼 `g_shade_flip_before`(`:254`), `g1_overlay_blt_apply`, drift `w` f=`4689C0`.
- 연결: `G1_SHADE_FLIP 0x004689C0u`(`:52`)·`_LEN 5u`(`:84`), `expected_shade_flip = {51 53 55 56 57}`(`:4349`), install은 shade_rle 바로 뒤(`:4440`). shade_rle과 shade_flip의 모든 참조를 이름 정규화해 비교하면 차이는 shade_flip 설명 주석 2줄뿐이다(c 58/57, h 10/10, ddt 13/13).
- objdump(원본 SHA 재확인): `0x4689C0` 1 B push 5개 = 경계 5 B, 쓰기 `mov [eax],bl` @`0x468A26` → watch EIP `0x468A28`, `ret 0x18` @`0x468A49`, `.text` 전체 호출 `call 0x4689c0` 1곳. lap1050 판과 같다.
- 테스트 순서: W-S2 RED(7,287 > 7,200)는 이번 재현으로 확인했다. H-X 계약 테스트는 구현 뒤 작성됐다(work가 정직 표기). 계약 내용은 H-W 테스트 변형과 같다.
- 런타임: `local/runtime/lap1051_hx_*` 6개 모두 `game` 사본이 없고 baseline/candidate는 남아 있다. exit 파일 w 2·2, s0 2·2(기존 save000 pair HOLD), s6 0·0, all done. 남은 lap1051 probe 프로세스 0. launch 1회.

## save000 잔여 분포(H-X 뒤)

`tail_s6_lap1052.json`: lap1051 s0 r1·r2와 w r1의 stale 합은 **전부 p298..338 팝업 상자 구간**(16,480·16,892·12,423)이고 p0..297·p339~는 0이다(w r2만 p297 303 1회). 직전 H-W 제품 lap1049 s0 r1은 p59..297 1,929·p339~ 1,899가 더 있었다. 즉 save000 고정 카메라에서 남은 stale은 팝업 상자 변형(present당 303 또는 412 px, y218..226×x240..323 부근) 하나다.

## 판정

**W-S2 PASS, H-X PASS(partial) 수용.** X-S, X-0, X-1(`0x468A28` 3/run → 0, 새 표본 2점 0), X-2(마지막40 0, 기준 B 172 px는 H-X 이전 run 변형과 픽셀 단위로 일치), X-3(p95 7/7, tick 비 1.000), X-4(사전등록 마스크 지표), X-5(wrap 0)가 모두 PASS다. 단 정정 3의 save006 늦은 블록은 수용 범위 밖의 새 관측이다. 다음 work가 이것을 먼저 재현·위치 확인한다. 회귀로 확인되면 이 수용을 다시 연다. 기술 부분수용이며 G1 마일스톤 승인이 아니다.

## 다음 work — H-Y save006 늦은 stale 블록 재현·위치(진단 전용, 제품 source 변경 0) 사전등록

- 가설: 정정 3의 블록은 (a) 특정 present 구간에서 반복되는 미후킹 writer의 일정 영역이거나, (b) 부하 의존 run 변형이다. 위치와 반복 여부를 먼저 정한다.
- 실행(순차, run 직전 `/proc/loadavg` 기록·1분 load > 8이면 대기, 단일 인스턴스 `pgrep` 확인 뒤 **launch 명령 한 번**, run 뒤 `game` 사본만 삭제). `run_x.sh` save006 줄 형식을 따르고 `--stale-mask`만 바꾼다.
  1. save006 pair 3회(현재 제품, 인자 lap1051 s6와 같음), `--stale-mask 6-12,300,420-480/3,585,620,770-850/3,880`(범위 7개 ≤ 8, 덤프 7+1+21+1+1+27+1 = 59 ≤ 한도 64 `G1_STALE_MASK_DUMP_LIMIT`).
- 측정·판정:
  - **Y-0:** 안전 7종 0, cleanup·source_unchanged true, pair PASS, 항등식 9 family 유지.
  - **Y-1(재현):** run마다 p≥40 구간의 `stale_pixels` 비0 구간(시작·끝·크기)을 표로 적는다. lap1051 두 블록 구간(p433..474·p782..834)과 겹치는지 적는다.
  - **Y-2(위치):** 비0 구간 안 덤프 마스크의 bbox·픽셀 수·run 간 교집합을 적는다. 화면 좌표가 정해지면 같은 lap에서 save006 watch pair 2회(`--layer-drift --screen-watch --drift-samples` = bbox 안 3점, 다른 인자 동일)로 마지막 writer EIP를 귀속한다(lap1041 H-S 방식, `w` sb==sa 같은 값 덮어쓰기는 실효 writer에서 뺀다).
  - 결론: 3 run 모두 블록 0이면 "부하 의존 run 변형, 재현 0/3"으로 닫고 다음은 save000 팝업 상자(아래). 블록이 있고 writer가 미후킹 함수면 FEASIBLE로 다음 hook 후보를 적는다. writer가 기후킹 함수(특히 `0x4689C0`)면 HOLD로 middle에 넘긴다.
- 금지: gate·validator·기준·`G1_OVERLAY_MAX_*`·제품 source 변경, 원본/raw 수정.
- 그다음 후보: save000 남은 stale = p298..338 팝업 상자(303/412 px) writer 귀속(표본은 y218..226×x240..323 안). backlog 미후킹 `0x467E60`(호출 `0x41A887`, 미관측).

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서 작성, 재계산, read-only objdump, 테스트 함수 재현(임시 디렉터리, 삭제)만 했다. 게임/source/commit은 0이다. focused 검사와 SAFETY 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1051 full PASS 1639 `logs/gates/lap1051-work-full-check.log`).
- 남은 위험: save006 늦은 블록(정정 3) 원인 UNKNOWN. 표본은 3점뿐이다. 팝업 상자 변형 A/B의 결정 원인은 미조사다.
- 사용자 승인 상태: 기술 부분수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 루프를 막지 않는다.
- 다음 한 가지: work H-Y(위 사전등록) → middle H-Y 검수.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1051 work, 1,452 B, SHA256 `44f03a1e22653bb4a514eb97645a262a023a4b682b9e6e965f8e2ceb3bfaf985`)

```
lap1051 work(Claude Code claude-sonnet-5-5) W-S2 + H-X 구현·측정 완료, 독립 검수 필요(자가 승인 금지).
기록: docs/history/laps/20261006_lap1051_work_g1_hx_shade_flip_4689c0_diff_mirror.md · 공유 temp 20261006_lap1051_work_hx/.
결과: X-S(W-S2 테스트 RED 7,288>7,200 → 8,192 GREEN 최악 7,683)·X-0·X-1(표본 3점 stale present 0/0, (783,377) 0x468A28 3/run→0)·X-2 마지막40 0·X-3 p95 7/7 tick 비 1.000·X-4 save006 신규 0·pair PASS·X-5 wrap 0/범위 이탈 0. 변경 uncommitted. launch 1회.
미해결: X-2 둘째 기준(lap1049 w ∪ lap1047 s0) 대비 새 r1∩r2 172 px(프레임 298·308·318·328 y218..224×x240..299 팝업 상자 43 px/프레임, 성능 pair는 0) — H-X 이전 run과 대조 안 함(UNKNOWN). save006 분석 p95 16/13(lap1049 8/7)은 shade_4689C0 호출 0·다른 저장소 부하로 환경 판정(UNKNOWN).
승격 작업자가 이어서 할 일: (1) watch r1·r2·성능 r1·r2·save006 r1·r2를 새 스크립트로 재계산(항등식 87=76+11·86=75+11, 표본 stale 0, 마지막40, setdiff), (2) X-2 기준 B 172 px를 H-X 이전 save000 run 마스크 합집합과 프레임별 대조해 run 변형 여부 판정, (3) mirror_shade_flip이 mirror_shade_rle과 이름·주소·before 버퍼 외 동일한지·objdump 0x4689C0·mirror_details 최악 합 재확인, (4) 수용 시 X-2 결과로 다음 work(표본 밖 잔여 writer 귀속 또는 미후킹 0x467E60) 사전등록.
```
