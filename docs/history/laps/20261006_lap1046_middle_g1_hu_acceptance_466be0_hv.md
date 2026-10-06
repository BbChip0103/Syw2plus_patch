# 2026-10-06 | lap1046 | G1 middle — H-U 독립 검수 → work H-V(`0x466BE0`) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·source 변경·commit은 0이다.
- 검수 대상: lap1045 work H-U(`0x468360` 클립 좌우반전 반투명 RLE 7인자 diff 미러). lap1042 §다음 work 2의 사전등록 U-0~U-4와 대조했다.
- 처리한 인계: `loop/ESCALATE_SOL`(lap1045 work, 844 B, SHA256 `7b9b0e42cf8efe49adf7fccf57ee4b058f1633bdc63593ba0a8794286d370963`). 원문은 아래 부록에 두고, 처리한 뒤 파일을 삭제했다.
- 변경 파일: 이 기록, `docs/STATUS.md`. source/test 변경은 0이다.
- 원본 SHA / 환경 / fixture: 원본 EXE `b56986e0…8ac`. objdump 대상 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`의 sha256을 다시 확인했고, 12 run 모두 private EXE 앞 16자가 일치한다. fixture는 save000(index 1)과 save006, 격리 prefix/display. 현재 source `g1_mirror2x.c` `f20c6aec…`·`direct_draw_trace.c` `4615f2f9…`·`g1_mirror2x.h` `37f0aa49…`는 work 기록과 같고, 6 run bridge 사본(`f20c6aecf974132c`)과도 같다.
- 재계산: 공유 temp `20261006_lap1046_middle_review/`. work의 `analyze_u_*.py`·`isect_u.py`·`setdiff_u.py`·`hooked_w.py`와 제품 helper는 쓰지 않았다. middle 소유 lap1040/lap1042 재계산 코드를 바탕으로 새로 썼다.
  - `recalc_lap1046.py` `e0addc70…18752a96` → `recalc_lap1046.json` `439cf71e…b38603b4`. 대상은 새 6 run(w r1/r2·s0 r1/r2·s6 r1/r2)과 기준 6 run(lap1041 s1_r2/r3, lap1039 s0 r1/r2, lap1039 s6 r1/r2)이다.
  - `details_worst_lap1046.py` `a36a9267…62d1451e` → `details_worst_lap1046.json` `5cea7056…fefd4d05`(두 번째 builder 2015..2290)·`details_worst_builder1_lap1046.json` `9837de81…f851c4f3`(첫 builder 1540..1760). wsprintfA 형식 문자열의 최악 출력 길이를 계산한다.
  - `s6_early_lap1046.py` `b13aa851…bfc264cf` → `s6_early_lap1046.json` `9e0b58b3…6ae0b363`. lap1018~1045의 save006 run 27개에서 초기 덤프 프레임 8·30·31의 stale 값을 모았다.
  - objdump 직접 재생성: `od_466BE0_lap1046.txt` `f82cab67…dfce0c8f`. diff 사본: `diff_g1_mirror2x_lap1041_to_now.txt`, `diff_ddt_lap1041_to_now.txt`.

## 재계산 결과(판정 불일치 0, 정정 3건)

| 항목 | lap1045 work 보고 | lap1046 재계산 |
|---|---|---|
| U-0 안전·cleanup·source_unchanged | 0 / true / true | 6 run 모두 안전 7종 max 0, cleanup·source_unchanged [true,true], trace JSONL 손상 0, ps3 410/410/411/411/900/898 |
| U-0 항등식 | save000 62 = 8 + 54, save006 32 = 0 + 32 | 같음. save000 4 run 모두 `blend_468360` 62 = 8 + reject_bounds 54이고 clipped 8, mirrored_pixels 3,013(watch)이다. save006은 32 = 0 + 32. 기존 항등식 5종(`466B50`·`4678C0`·`467FD0`·`467B00`·`467580`)도 6 run 모두 성립 |
| 무장·selftest | PASS·fail 0·좌표 3/3 | selftest PASS, 무장 52 round, fail 0, 모든 round 좌표 = S1 3점, dropped/overflow 0 |
| **U-1** S1 (795,470) | 20 → 15, `0x468571` 5 → 0 | **같음.** 기준 hs_r2/r3: 20 = `0x466D15` 12 + `0x468571` 5 + `0x46884E` 2 + `0x467CCF` 1. 구간 p388–392 / p386–390. 새 w_r1/r2: 15 = 12 + 0 + 2 + 1이고 p388 구간은 사라졌다. 나머지 구간 [141–142, 239–250, 396] / [140–141, 238–249, 395]는 그대로다. 값 일치 15/15. 실효 writer = `0x466D15` 13 + `0x46884E` 2(`0x467CCF` 1건은 같은 값 덮어쓰기, lap1042 정정 1과 같은 패턴) |
| U-1 미러 작동 확인 | — | `0x468571` watch hit는 새 run에도 run마다 7회 남아 있다(함수는 계속 그 점을 쓴다). `w` 레코드 f=468360은 8건이고 전부 `clipped`이다. 즉 stale이 사라진 이유는 쓰기가 없어진 것이 아니라 diff 미러가 반영했기 때문이다 |
| S1 (628,409)·(599,367) | 1·1 불변 | 1·1(`0x46884E`, p6·p12) 불변 |
| **U-2** 마지막40 중앙값 | 26 → 0/0 | **0/0**(watch). 성능 run도 0/0이다. 기준 hs·lap1039 s0는 26 |
| U-2 새 r1∩r2 ∖ 기준 합집합 | 0 | **0**(39 프레임, 기준 = lap1041 s1_r2∪s1_r3) |
| U-2 제거 | 24 px(프레임 388) | **24 px(프레임 388)**만 |
| **U-3** 성능 pair p95 | 7/7, tick 비 1.0025 | **7/7.** 히스토그램 재구성 nearest-rank p95 7/7, 평균 5.147/5.035(lap1039 s0 기준 5.18/5.28), 10ms 이상 0/1. tick 비 1.0025/1.0000. 시작 load 2.78/2.43 |
| watch run p95 | 11(판정 외) | 11/11. 기준 hs watch run도 11/12라 watch 계측 비용이다 |
| **U-4** save006 | 38 공통 덤프 신규 0, pair PASS | **steady 38 프레임(300..620)과 880 모두 r1∩r2 0, 기준 대비 신규 0.** pair status PASS(exit 0) 2회. V2s unexplained 20~237(gate PASS), production raw 2,820/2,815(공개 진단). save006에서 `0x468360`은 32회 모두 reject_bounds이고 mirrored 0이다. 즉 H-U 미러는 save006에서 쓴 픽셀이 없다 |

**정정 1 — U-1 숫자 표기.** 사전등록은 "10 → 0"(두 run 합계)이고 work는 "5 → 0"(run당)이다. 같은 값이다(5 × 2 = 10). 판정에는 영향이 없다.

**정정 2 — U-4 "기준 대비 신규 0/0"의 범위.** 이 문장은 steady 38 프레임과 880에만 맞다. 공통 50 프레임 전체로 보면 초기 프레임에 신규가 있다.
- 프레임 8의 +75 px: 기준 lap1039 r1이 21,517로 낮아서 생긴 차이다. 역사적으로 이 프레임 값은 21,517·21,558·21,592로 흔들린다.
- 프레임 30의 +408 px: 이 프레임은 run 하나에서 일시적으로 커지는 일이 lap1018~1039의 25 run 중 6 run에서 있었다(예: 3,700 → 4,346·4,557·4,637, 3,290 → 4,307·4,227·4,147. lap1026 v2_s6_r2는 반대로 1,729로 낮았다). 이번에는 두 run이 모두 커져서(3,720/4,091) 교집합에 남았다.
- 이 프레임들은 steady 이전 전환 구간이고, save006에서 H-U 미러는 픽셀을 쓰지 않았다(mirrored 0). 따라서 H-U에 귀속하지 않는다. U-4 판정 범위(steady + 880)는 그대로 PASS이다.

**정정 3 — 성능 pair 덤프.** work는 성능 pair를 r1∩r2 합 2,972로만 적었다. 새 계산 결과는 다음과 같다. lap1041 watch 기준과 비교하면 프레임 338에 신규 48 px가 있다. 같은 설정인 lap1039 성능 기준과 비교하면 신규 0, 제거 26 px(프레임 388)이다. 프레임 338은 이미 알려진 팝업 p298..338 run 변동 구간이므로 H-U와 무관하다. U-2 판정(watch 쌍)에는 영향이 없다.

## 코드 검수

- `mirror_blend_flip7`(`g1_mirror2x.c:3643`)에서 `flip7/FLIP7/468360`을 `clip7/CLIP7/4678C0`으로 이름만 바꾸면 `mirror_blend_clip7`(`:3558`) 본문과 줄 단위로 같다(diff = 주석 블록뿐). 원 인자 7개를 한 번 그대로 넘기고, x·y·w·h는 16비트 부호 확장, 화면 교집합 → 전용 before 버퍼 → `g1_overlay_blt_apply` 순서다.
- 그 밖의 연결도 확인했다. 참조 수는 hook 4, 계수 40, 헤더 9, `direct_draw_trace.c` 12로 clip7과 같다. install 목록 `:4110`, `expected_blend_flip7 = {83 EC 1C 53 55}`. 원본 EXE `0x468360`의 바이트는 objdump로 다시 확인해 `83 EC 1C`(sub esp,0x1c)·`53`·`55`, 즉 명령 경계 5 B다.
- lap1041 bridge 이후 `direct_draw_trace.c` diff는 `mirror_details` 6600 → 7200(2곳)과 `blend_flip7_details[400]` 블록 하나뿐이다.
- **`mirror_details` 최악 길이:** 두 번째 builder 전체는 NUL 포함 6,458 B(`%s`는 sha256 64 + asset key 63)이고 7,200 미만이다. 새 블록은 최악 358 < 400이다. 첫 builder는 `mirror_details` 본체 최악 582 + `%s`이고 하위 버퍼를 따로 보아야 한다(아래). → **(3) PASS.**
- **새 발견(기존 결함, H-U 무관, 비차단이지만 G1 사용자 전달 전 수리 필요):** detach 때 1회 출력하는 하위 stack 버퍼 몇 개가 최악 형식 길이보다 작다. `wsprintfA`는 대상 크기를 모르므로, 카운터 자릿수가 늘면 stack을 넘어 쓴다.

| 버퍼 | 크기 | 형식 최악(+NUL 전) | 실측(lap1045) | 비고 |
|---|---|---|---|---|
| `textout_details` (H-G 이후) | 360 | 430 | **save006 900 present run에서 350**(여유 9 B) | 고정 320 + 자릿수 합. 자릿수 합이 40이 되면 넘친다(현재 30). 카운터가 run 길이에 비례한다고 보면 약 100배(present 약 9만) 세션이다 |
| `rect_border_details` | 240 | 274 | save006 233 | 여유 6 B |
| `rect_fill_details` | 240 | 262 | save006 221 | |
| `mirror_perf_details`(첫 builder) | 900 | 962 + `perf_window_id` | 이번 run에는 출력 없음 | performance window 경로 |

  출력은 `g_trace_enabled`일 때만 한다(`g1_direct_draw_trace_detach`). 하지만 G1 미러가 이 trace DLL 안에서 동작하므로, 긴 사용자 세션에서는 종료 시 stack 손상이 생길 수 있다. lap1031/1032 `rect_solid_details` 수리와 같은 종류다. → work H-V에서 함께 수리한다(아래 V-S).

## `0x466BE0` 독립 objdump(원본 SHA 재확인, H-V 사전등록 근거)

- 시작 바이트는 `83 EC 18`(sub esp,0x18)·`33 C0`(xor eax,eax)로, 명령 경계 5 B다. lap1042 표에 따르면 앞 5 B 안으로 들어오는 분기와 절대 포인터는 0이다. `ret 0x18`(`0x466D40`)이므로 stack 인자는 6개다.
- 인자는 `x=[esp+0x2C]`·`y=[esp+0x30]`·`w=[esp+0x34]`·`h=[esp+0x38]`·`rle=[esp+0x3C]`·`remap=[esp+0x40]`이다(push 4개 뒤 기준). 모두 32비트 `mov`이고 `movsx`가 없다. 목적지 = `[ecx+0x1514] + y·[ecx+0x10] + x`.
- 클립은 `[+0x4D0,+0x4D8]×[+0x4D4,+0x4DC]` 양끝 포함이다. 사각형이 클립 밖이면 쓰기 없이 끝난다. 왼쪽·오른쪽 건너뛰기 수(`[esp+0x1C]`, `[esp+0x18]`)와 위쪽 건너뛰기 행 수(`[esp+0x14]`)를 계산한다.
- RLE 규칙: `0xFE` 다음 바이트는 투명 건너뛰기 수이고, 그 밖의 값은 `remap[val]`로 쓴다. 쓰기 명령은 `0x466D11`(`mov [edi+ebp-1],al`, edi = 행 시작 − col)이므로 **목적지 열 = x + w − 1 − col(좌우 반전)**이다. watch EIP `0x466D15`는 그 다음 명령이다.
- 쓰기 열 범위는 `[max(x, clip_left), min(x+w−1, clip_right)]`이고 행도 같은 방식이다. 따라서 **쓰기 범위 ⊆ rect ∩ clip ⊆ rect**이다. 화면 교집합 diff는 원본의 화면 내 쓰기를 모두 덮는다.
- 호출처는 `0x419FB0`·`0x41A54A`이고, 둘 다 `ecx = 0xE5BF18`(`G1_RENDERER_VA`) 뒤 call이다. 즉 `0x466B50`(H-R `mirror_flip_rle`, 6인자·32비트·반전)의 클립 형제다.

## 판정

**H-U PASS(partial) 수용.** U-0, U-1(5 → 0/run, 분리 확인 대상 불변), U-2(마지막40 26 → 0, 새 ∖ 기준 0, 제거 24 px), U-3(p95 7/7, tick 비 1.0025/1.0000), U-4(steady + 880 신규 0) 모두 PASS이고 코드 결함은 0이다. 정정 1~3은 판정에 영향이 없다. `mirror_details` 7,200은 충분하다. 이것은 기술 부분수용이며 G1 마일스톤 승인이 아니다. save006 pair PASS는 W-1(사용자 결정) 효과이고 H-U의 제품 수치가 아니다.

## 다음 work — H-V `0x466BE0` 클립 반전 RLE diff 미러 + 진단 버퍼 크기 수리(V-S) 사전등록

- 변경 1 (H-V, `tools/inmm_stub/g1_mirror2x.c`): hook `0x466BE0`(old bytes `83 EC 18 33 C0`, len 5, thiscall, 6 stack args, `ret 0x18`). wrapper는 수용된 **`mirror_flip_rle`(H-R) 구조를 그대로** 쓴다: int32 인자, `g1_flip_rle_region` 화면 교집합, 전용 before 버퍼, 원 인자 6개 1회, `g1_overlay_blt_apply`. 원본이 클립을 하므로 wrap 쓰기는 없지만 `region.wrap` 집계는 진단용으로 남긴다. 계수는 `flip_clip_466BE0_*`(invocations·mirrored_calls·mirrored_pixels·changed_calls·clipped_calls·wrap_calls·reject_target/bounds/size/guard), drift `w` f=`466BE0`이다. install·restore·installed·reset 목록에 넣는다.
- 변경 2 (V-S, `tools/inmm_stub/direct_draw_trace.c`): 형식 최악 길이 + 1 이상으로 키운다. `textout_details` 360 → ≥ 440, `rect_fill_details`·`rect_border_details` 240 → ≥ 280, `mirror_perf_details` 900 → ≥ 962 + `window_id` 최대 + 1. 새 `flip_clip` 블록과 합친 `mirror_details` 전체 최악도 다시 계산하고 필요하면 올린다.
  - 호스트 테스트를 새로 둔다: `direct_draw_trace.c`의 `wsprintfA(<buf>, "<fmt>"…)`마다 최악 길이를 계산한다(`%u` 10, `%d`/`%ld` 11, `%X` 8, `%I64u` 20, `%s`는 인자 버퍼 크기 − 1). 이 값이 `char <buf>[N]`의 N − 1 이하인지 검사한다. lstrcat 대상 `mirror_details`는 하위 최악의 합으로 검사한다. RED(현재 4건 FAIL) → GREEN.
  - 이것은 제품 진단 버퍼 크기이며 안전 pin/golden이 아니다. 출력 내용·키·순서는 바꾸지 않는다.
- 테스트 RED→GREEN: hook 표(주소·old bytes·인자 6)·wrapper 계약(H-R 테스트 변형)·계수 노출·위 버퍼 테스트.
- 실행: 순차로 돌린다. run 직전 `/proc/loadavg`를 기록하고, 1분 load > 8이면 대기한다. 단일 인스턴스와 run 뒤 `game` 사본 삭제를 확인한다. `run_u.sh` 형식을 따르고 바꾸는 것만 적는다.
  1. save000 watch pair 2회: `--drift-samples "795,470;779,467;568,483"`(`0x466BE0` 실효 점 3곳: lap1042 실효 13·6·3/run). mask 인자는 lap1045와 같다.
  2. save000 성능 pair 2회(lap1045 s0 인자).
  3. save006 pair 2회(lap1045 s6 인자).
- PASS / FAIL:
  - **V-0:** 안전 7종 0, cleanup·source_unchanged true, `flip_clip_466BE0` invocations = mirrored + reject_* 성립, invocations > 0. 기존 항등식 6종 유지.
  - **V-1(가설 지표):** 실효 writer `0x466D15`인 stale present가 두 run 모두 **0**이어야 한다. 기준은 (795,470) 13/run(lap1045 w), (779,467) 6/run, (568,483) 3/run(lap1041 s2/s3). `0x46884E` 구간((795,470) 2·(779,467) 2/run)은 그대로 남아야 한다(분리 확인).
  - **V-2(집계):** 마지막40 중앙값 0 유지. 덤프는 "새 r1∩r2 ∖ 기준(lap1045 w r1∪r2) = 0"과 "기준 r1∩r2 ∖ 새 r1∪r2(제거)"를 함께 적는다. 합계만으로 결론 내지 않는다.
  - **V-3(성능):** 성능 pair p95 ≤ 8ms, tick 비 0.99~1.01. 미달이면 load·히스토그램으로 UNKNOWN-환경 여부를 따로 적는다(기준 무변경).
  - **V-4(비회귀):** save006 steady 38 프레임과 880의 r1∩r2 신규 0. 초기 프레임(6..34)은 정정 2에 따라 따로 표로 적고 판정에서 뺀다.
  - **V-S:** 버퍼 테스트 GREEN이고, 실제 run의 `textout`·`rect_*` 출력 키와 값이 이전과 같은 형식이다(JSON 파싱 손상 0).
  - 반증: V-1이 0이 되지 않으면 같은 lap에서 `w` f=466BE0의 기하와 `why`를 표로 남기고 HOLD로 middle에 넘긴다. reject_size가 생기면 크기를 기록한다.
- 금지: gate·validator·기준·`G1_OVERLAY_MAX_*` 변경, 원본/raw 수정, 다른 wrapper 동작 변경. run 뒤에는 `game` 사본만 삭제한다.
- 그다음 순서는 `0x4687F0`(`0x46884E`, 클립 없음·`ret 0x18`)이고, 그다음 `0x4689C0`(`0x468A28`)이다.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서 작성, 재계산, read-only objdump만 했다. 게임/source/commit은 0이다. focused 검사와 SAFETY 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1045 full PASS 1634 `logs/gates/lap1045-work-full-check.log`).
- 남은 위험: 표본은 3점뿐이고 `0x468360` 호출 62회 중 mirrored는 8회다(화면 밖 54회). 호출처 `0x41A8E7`·`0x41AA5F` 중 관측된 것만 검증했다. 미러 off 대조 run은 없다(U-3 미달이 없어서). 진단 버퍼 넘침(V-S)은 아직 수리 전이다.
- backlog: `0x467E60`(같은 호출 블록, 미관측), save006 초기 프레임 30 일시 stale, 팝업 p298..338 run 변동, hold keydown 위상, 가장자리 마우스 스크롤, overlay BltFast rejects, 다중 팝업 heal.
- 사용자 승인 상태: 기술 부분수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 루프를 막지 않는다.
- 다음 한 가지: work H-V(위 사전등록, V-S 포함) → middle H-V 검수.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1045 work, 844 B, SHA256 `7b9b0e42cf8efe49adf7fccf57ee4b058f1633bdc63593ba0a8794286d370963`)

```
lap1045 work(Claude Code claude-sonnet-5-5) H-U 구현·측정 완료, 독립 검수 필요(자가 승인 금지).
기록: docs/history/laps/20261006_lap1045_work_g1_hu_blend_flip7_468360_diff_mirror.md · 공유 temp 20261006_lap1045_work_hu/.
결과: U-0~U-4 전부 PASS(partial) — S1 (795,470) `0x468571` 5→0, 마지막40 중앙값 26→0, 새∖기준 0·제거 24px, 성능 p95 7/7, save006 신규 0·pair PASS(W-1 효과). 변경 uncommitted.
승격 작업자가 이어서 할 일: (1) watch r1·r2·성능 r1·r2·save006 r1·r2를 새 스크립트로 재계산(항등식 62=8+54, EIP 분포, 마지막40, setdiff, 성능·tick 비), (2) mirror_blend_flip7 코드가 mirror_blend_clip7과 동일 구조인지·mirror_details 7200 최악 길이, (3) 수용 시 work H-V 사전등록(0x466BE0 실효44 → 0x4687F0 26 → 0x4689C0 8).
```
