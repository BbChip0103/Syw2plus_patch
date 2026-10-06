# 2026-10-06 | lap1051 | G1 work W-S2 + H-X — `0x4689C0` 반전 목적지 리맵 RLE(6인자, 클립 없음) diff 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 모든 변경 uncommitted.
- 가설: lap1050 middle 사전등록(`20261006_lap1050_middle_g1_hw_acceptance_4689c0_hx.md` §다음 work) — 미후킹 `0x4689C0`(thiscall `ret 0x18`, old bytes `51 53 55 56 57`, 목적지 lut 리맵·좌우 반전·클립 없음·32비트)을 H-W `mirror_shade_rle` 구조 diff 미러로 hook하면 save000 표본 (783,377)의 실효 writer `0x468A28` stale present 3/run이 0이 된다. 선행으로 W-S2(`mirror_details` 두 번째 builder 최악 합 테스트 수리 + 크기 상향)를 먼저 한다.
- 변경 파일:
  - `tests/test_g1_rect_fill.py`: **W-S2** `_STRING_ALLOWANCE["mirror_details"] = (64, 63)`(`%s` 두 개를 순서대로 `panel_frame_sha256` 64 + `panel_asset_key` 63으로 계산, `_worst_format_length`가 단일 값 또는 순서 튜플을 받음)·lstrcat 리터럴을 C escape를 푼 길이로 계산. 신규 `test_shade_flip_hook_table_and_wrapper_contract`. 크기 pin 3곳(`char mirror_details[7200];` count 2→1, 첫 builder만 7200).
  - `tools/inmm_stub/g1_mirror2x.c`: `G1_SHADE_FLIP 0x004689C0u`·`_LEN 5u`, `expected_shade_flip {51 53 55 56 57}`, `g_original_shade_flip`(`G1Primitive6Fn`), `g_hook_shade_flip`, 전용 before 버퍼 `g_shade_flip_before`, 계수 10개, wrapper `mirror_shade_flip`(= `mirror_shade_rle` 본문을 이름·주소·before 버퍼만 바꿔 복제; 원 인자 6개 1회 전달, x·y·w·h int32, 화면 교집합 `g1_flip_rle_region`, drift `w` f=`4689C0`), install(shade_rle 바로 뒤)·reset·restore·installed 목록. 첫 명령 5개가 1바이트 push라 `install_one` trampoline 안전.
  - `tools/inmm_stub/g1_mirror2x.h` accessor 10개, `tools/inmm_stub/direct_draw_trace.c` 요약 `shade_4689C0_*` 10키(`shade_flip_details[480]`)와 **두 번째 `mirror_details` 7200→8192**.
- 원본 SHA / 후보: 원본 EXE `b56986e0…8ac`(pair-result source_unchanged true 전 run). source sha256: `g1_mirror2x.c` `e9620997…3513`, `g1_mirror2x.h` `35b5d76d…`, `direct_draw_trace.c` `9fa3390c…`, `test_g1_rect_fill.py` `ae6e9e66…`. 6 run 모두 설치 성공(`shade_4689C0_*` 출력, 설치 시 old bytes 검증). `i686-w64-mingw32-gcc -Wall -Wextra` 컴파일 경고 shade_flip 0(임시 `/tmp/lap1051_build`).
- 실행(공유 temp `20261006_lap1051_work_hx/`, 로그 `logs/gates/lap1051_hx_*`): `run_x.sh`(lap1049 `run_w.sh`에서 이름·표본 `783,377;786,220;718,452`만 변경, 순차·단일 인스턴스·run 직전 load 대기·run 뒤 `game` 사본 삭제). **launch 1회**(`&&` 체인을 통째로 background로 보내 pidfile 쓰기만 실패, 프로세스는 1개로 확인; 이중 기동 없음). load 대기 0(시작 load 2.38~5.03). save000 watch pair 2회, 성능 pair 2회, save006 pair 2회. exit: watch 2·2, s0 2·2(기존 save000 pair HOLD), s6 0·0. 분석 스크립트(`analyze_x_*.py`·`setdiff_x.py`·`isect_x.py`)는 lap1049 work 스크립트의 복사·표본 치환이며 middle이 쓰지 않는다.

## 수치

| 항목 | 기준 | lap1051 |
|---|---|---|
| **X-S** W-S2 테스트 | RED(현재 source 7,288>7,200) → GREEN | **RED 확인**: `(7287, 7200)`, 최악 7,287 + NUL = 7,288. GREEN: builder 8,192 + H-X 블록 포함 최악 **7,683 ≤ 8,192**(H-X 블록 +395). 새 H-X 계약 테스트 포함 `test_g1_rect_fill`·`test_g1_panel_layer` 24 passed |
| **X-0** 안전 7종·cleanup·source_unchanged | 0 / true / true | 6 run 전부 0 / true / true |
| X-0 항등식 `shade_4689C0` | invocations = mirrored + reject_* | watch r1 87 = 76 + reject_bounds 11, r2 86 = 75 + 11, 성능 r1·r2 87 = 76 + 11(target/size/guard 0, clipped 22/21, changed 67). 기존 `shade_4687F0` 190 = 183 + 7 유지(4 run). save006 invocations 0 |
| 무장·selftest | PASS·fail 0 | selftest PASS·무장 52라운드 fail 0·좌표 (783,377)(786,220)(718,452)·dropped/overflow 0 |
| **X-1** (783,377) 마지막 writer stale present | lap1049 w: 3/run (`0x468A28`) | **0 / 0**(u 5/5, hit 729/728) |
| X-1 (786,220) | H-W 비회귀 0 | **0 / 0**(u 4/4, hit 452) |
| X-1 (718,452) | 이번 측정 | **0 / 0**(u 5/5, hit 447/449). stale_present A·B·C(고정 표본)도 0 |
| X-1 미러 작동 | — | drift `w` f=4689C0 17/18건(mirrored 15/16·clipped 2/2), 그중 표본 값 변화 기록 4/4 → 함수가 표본을 실제로 바꾸는데도 stale 0 |
| **X-2** 마지막40 중앙값 | 0 | **0 / 0**(watch), 성능 r1·r2도 0. p24..58·p84..365·p366~ 중앙값 0, p298..338 303/303(watch)·412/412(성능) |
| X-2 새 r1∩r2 ∖ 기준 A(lap1049 w r1∪r2) | — | **308 px / 4 프레임**(298·308·318·328 각 77, y218..226×x240..299 팝업 상자). 합 r1∩r2 1,212(r1 합 1,515·r2 1,212) |
| X-2 새 r1∩r2 ∖ 기준 B(A ∪ lap1047 s0 r1∪r2) | 0이 아니면 위치 기록 | **172 px / 4 프레임**(298·308·318·328 각 43, y218..224×x240..299) — 같은 팝업 상자 안. 둘째 기준으로도 0이 아니다 |
| X-2 제거(기준 A r1∩r2 ∖ 새 r1∪r2) | — | 1,495 px(308 287·298 271·338/328/318 186·294 144 등) |
| X-2 성능 pair 새 r1∩r2 ∖ 기준(lap1049 s0 r1∪r2) | — | **0 / 0**(두 기준 모두), 제거 565 |
| **X-3** 성능 pair | p95 ≤8, tick 비 0.99~1.01 | **7 / 7**(baseline 0/0), tick delta 후보 400·400 vs 기준 400·400 → 비 1.000. 시작 load 4.09/4.37 |
| **X-4** save006 | steady 38 + 880 신규 0 | **r1∩r2 0**(공통 38프레임 ≥300 + 880 제외·포함 모두 0), 기준(lap1049 s6 r1·r2) 대비 신규 0/0·제거 0/0, safety 0, pair status **PASS(exit 0)** 2회, cov p50 99.31%. 초기 프레임(6..34) 표 생략(기준 대비 변화 0) |
| X-4 보조(환경) | 기준 아님 | save006 현재 분석 p95 16/13 대 lap1049 8/7(같은 스크립트·같은 지표 재계산 8/7). **`shade_4689C0` invocations = 0**(save006에서 미호출)이므로 H-X 비용 0, 종료 시점 load 상승(9.9~17.8, 다른 저장소 `Syw2plus_re_loop` 세션 프로세스 114136·169018)·ps3 843/893 → UNKNOWN-환경(기준 무변경) |
| **X-5** 경계 | wrap, x<0 또는 x+w>stride | `shade_4689C0_wrap_calls` **0**, drift `w` 기하 중 범위 이탈 **0/35**(x 703..712·y 434..451·w=h=25), 화면 밖 호출 `reject_bounds` 11/run은 사각형이 화면 밖인 호출 |

## 해석
- 가설 확정: (783,377) `0x468A28` stale present 3/run → 0/run, 새 표본 2점 모두 0, 마지막40 중앙값 0 유지. X-1~X-5 PASS.
- **X-2 둘째 기준 B가 0이 아니다(172 px, 프레임 298·308·318·328의 y218..224×x240..299 팝업 상자 43 px/프레임).** 위치가 H-W 때 확인한 팝업 상자 영역(y218..226×x240..323)과 같고 성능 pair에서는 두 기준 모두 0이므로 `0x4689C0` 쓰기 영역(x 703..~737, y 434..~476 우측 군)과 겹치지 않는다. 그러나 합계만으로 결론 내지 않는다: 이 43 px가 H-X 이전 run 합집합에 있는지는 이번 lap에서 대조하지 않았다(중간 검수 몫, H-W 이전 save000 run 마스크와 프레임별 대조 요청). 제거 1,495 px는 이전 판의 변형 B류 상자(프레임 298·308·318·328·338·294) 쪽이라 run 변형 가능성이 높지만 UNKNOWN.
- 성능 p95 7/7(H-W 8/8)·tick 비 1.000. save006 p95 상승은 호출 0 hook 때문이 아니라 환경이다(근거 위 표).
- 테스트 순서 정직 표기: W-S2는 RED(7,288)를 먼저 확인한 뒤 GREEN으로 만들었다. H-X 계약 테스트 `test_shade_flip_hook_table_and_wrapper_contract`는 구현을 먼저 복제한 뒤 작성했다(RED 선행 증명 없음; `G1_SHADE_FLIP` 부재 상태에서는 `mirror.index` 등이 즉시 실패하는 구조).

## 회귀 / 남은 위험 / 독립 검수
- 변경 uncommitted. 게임 사본 `local/runtime/lap1051_hx_*/game` 6개는 run 직후 삭제(manifest/output/prefix·로그 보존). 이 lap의 probe 프로세스 잔여 0(남은 2개는 `Syw2plus_re_loop` 다른 저장소 세션).
- 남은 위험: 표본은 3점뿐이고 `0x4689C0` save000 호출은 87회(mirrored 76)다. X-2 기준 B 잔여 43 px/프레임 상자는 H-X 이전 run과의 대조가 필요하다(UNKNOWN). save000 stale 총합에 남는 다른 미후킹 writer는 이번 lap에서 새로 귀속하지 않았다.
- 독립 검수는 다음 middle(Opus)이 새 스크립트로 6 run을 재계산하고 `mirror_shade_flip` = `mirror_shade_rle` 이름 치환 diff 0·objdump `0x4689C0` 재확인·`mirror_details` 최악 합(7,683<8,192) 재계산·X-2 기준 B 172 px를 H-X 이전 run 합집합과 대조한다. 이 work는 자가 승인하지 않는다.
- 다음 한 가지: middle H-X 검수 → work(표본 밖 잔여 재선정, X-2 결과 기반).
