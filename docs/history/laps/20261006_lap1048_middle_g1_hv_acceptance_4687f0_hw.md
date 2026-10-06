# 2026-10-06 | lap1048 | G1 middle — H-V 독립 검수 → work H-W(`0x4687F0`) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·source 변경·commit은 0이다.
- 검수 대상: lap1047 work H-V(`0x466BE0` 클립 좌우반전 리맵 RLE 6인자 diff 미러 `mirror_flip_clip`)와 V-S(진단 stack 버퍼 4개 수리). lap1046 §다음 work의 사전등록 V-0~V-4·V-S와 대조했다.
- 처리한 인계: `loop/ESCALATE_SOL`(lap1047 work, 1,167 B, SHA256 `aa1858b37ead8588986e0bf8eb8b50c0397dc98c19af87b475f9ea4d8ad0e67e`). 원문은 아래 부록에 두고, 처리한 뒤 파일을 삭제했다.
- 변경 파일: 이 기록, `docs/STATUS.md`. source/test 변경은 0이다.
- 원본 SHA / 환경 / fixture: 원본 EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` sha256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 다시 확인했고, 새 6 run과 기준 8 run 모두 private EXE 앞 16자가 일치한다. fixture는 save000(index 1)과 save006, 격리 prefix/display. 현재 source `g1_mirror2x.c` `32ca11fd…`·`direct_draw_trace.c` `24ed0d58…`·`g1_mirror2x.h` `441fd5b9…`는 work 기록과 같고, 6 run bridge 사본과도 같다(sha256 전체 일치).
- 재계산: 공유 temp `20261006_lap1048_middle_review/`. work의 `analyze_v_*.py`·`isect_v.py`·`setdiff_v.py`와 제품 helper는 쓰지 않았다. middle 소유 lap1046 재계산 코드를 바탕으로 run별 표본 좌표를 받도록 고쳐 새로 썼다.
  - `recalc_lap1048.py` `98185439…3cab` → `recalc_lap1048.json` `53e00f88…2453`. 대상은 새 6 run(w r1/r2·s0 r1/r2·s6 r1/r2)과 기준 8 run(lap1045 w r1/r2·s0 r1/r2·s6 r1/r2, lap1041 s2 r1/r2·s3 r1/r2)이다.
  - `details_worst_lap1048.py` `9864180f…3259`(lap1046 스크립트 복사, docstring 1줄 외 로직 동일) → `details_worst_builder2_lap1048.json` `24e0093d…3c91`·`details_worst_builder1_lap1048.json` `42f4901f…03c6`·합 `details_sum_lap1048.json` `007b97ba…55be`.
  - objdump 직접 재생성: `od_466BE0_lap1048.txt` `85402f06…e46a`, `od_4687F0_lap1048.txt` `7e1a8faa…9797`. diff 사본: `diff_g1_mirror2x_lap1045_to_now.txt`, `diff_ddt_lap1045_to_now.txt`.

## 재계산 결과(판정 불일치 0, 정정 3건)

| 항목 | lap1047 work 보고 | lap1048 재계산 |
|---|---|---|
| V-0 안전·cleanup·source_unchanged | 0 / true / true | 6 run 모두 안전 7종 max 0, cleanup·source_unchanged [true,true], trace JSONL 손상 0, ps3 409/412/412/412/886/887 |
| V-0 항등식 | 1414 = 530 + 884 등 | **같음.** `flip_clip_466BE0` w 1414 = 530 + 884 / 1415 = 526 + 889, s0 1420 = 530 + 890 / 1422 = 530 + 892, s6 3099 = 327 + 2772 / 3105 = 327 + 2778. reject_target/size/guard 0. clipped 146/145/146/146/327/327, changed 283/281/283/283/235/235. 기존 6 family(`466B50`·`4678C0`·`467FD0`·`467B00`·`467580`·`468360`)도 6 run 모두 성립 |
| 무장·selftest | PASS·fail 0·좌표 3/3 | selftest PASS, 무장 52 round, fail 0, 모든 round 좌표 = 표본 3점, dropped/overflow 0 |
| **V-1** (795,470) | 15 → 2(`0x46884E` 2) | **같음.** 기준 lap1045 w r1/r2: 15 = `0x466D15` 12 + `0x46884E` 2 + `0x467CCF` 1(실효 `0x466D15` 13 + `0x46884E` 2). 새 r1/r2: 2 = `0x46884E` 2, 구간 p140..141, 값 일치 2/2 |
| V-1 (779,467) | 8 → 2 | **같음.** 기준 lap1041 s2 r1/r2: 8 = `0x466D15` 6 + `0x46884E` 2. 새: 2(`0x46884E`, p143..144) |
| V-1 (568,483) | 3 → 0 | **같음.** 기준 lap1041 s3 r1/r2: 3 = `0x466D15` 3(p4..6). 새: 0, `u` 3 |
| V-1 미러 작동 | — | `0x466D15` watch hit는 새 run에도 점별 13/6/3회 남는다(함수는 계속 그 점을 쓴다). `w` f=466BE0은 148/147건(mirrored 117/116·clipped 31/31). 즉 stale이 사라진 이유는 쓰기 제거가 아니라 diff 미러 반영이다 |
| **V-2** 마지막40 | 0/0 | **0/0**(watch), 성능 run도 0/0 |
| V-2 새 r1∩r2 ∖ 기준(lap1045 w r1∪r2) | 0 | **0**(39 프레임) |
| V-2 제거 | 572 px(298 247·234 221·6 104) | **같음.** r1∩r2 합 1,749 → 2,338, run 합 3,657/3,232 → 2,554/2,544. 성능 pair 대 lap1045 s0: 새∖기준 0, 제거 873 px(6 104·234 292·298 477) |
| **V-3** 성능 pair p95 | 7/8, tick 비 1.000 | **7/8.** 히스토그램 nearest-rank p95 7/8, 평균 5.098/5.245(기준 5.147/5.035), 10ms 이상 0/9, tick delta 400/400, tick 비 1.00006/1.00000. 시작 load 3.95/4.09. watch run p95 12/12(기준 hu watch 11/11, hs watch 11~12) |
| **V-4** save006 | steady + 880 신규 0, pair PASS | **같음.** 공통 51 프레임(steady 38 + 880 포함), 새 r1∩r2 비0 프레임은 6..12뿐(18,236~19,052, r1 = r2). 기준 대비 새∖기준 0(교집합·합집합 둘 다), 제거 6..12 3,169~3,312·30..34 3,070~3,482 전부. pair status PASS(exit 0) 2회 |
| **V-S** | 버퍼 4개 수리·테스트 GREEN | **같음.** 새 테스트 포함 `tests/test_g1_rect_fill.py -k "flip_clip or worst_case or flip_rle"` 4 passed. 형식 최악(NUL 전): `textout` 430/480, `rect_fill` 262/320, `rect_border` 274/320, `mirror_perf` 962 + `hd_source`(최대 `identity` 8)/1100, 새 `flip_clip` 435/480. 하위 버퍼 20개 전부 최악 + 1 ≤ 크기 |

**정정 1 — `mirror_details` 두 번째 builder 최악 합.** work는 6,848이라 적었다. 이번 계산은 **6,893 B(NUL 포함)**이다. 차이 45 = s3 lstrcat 리터럴 2개(`,"s3_pattern_enabled":` + 1, `,"s3_pattern_applied":` + 1, 합 46) 누락 − `%s` 상한 차 1(sha256 64 + asset key 63). 7,200 미만이므로 판정은 같다(여유 307). 첫 builder는 `%s` 상한(rect json 159×2·dump ≤259·`hd_source` 64·`window_id` 95)을 넉넉히 잡아도 6,043 B다. 다음에 hook family를 하나 더 붙이면(약 +450) 여유가 줄어드므로 H-W에서 다시 계산한다.

**정정 2 — `wrap_calls` 미보고.** work 표는 `flip_clip_466BE0_wrap_calls`를 적지 않았다. 값은 save000 1022/1026/1028/1030, save006 3099/3105(= invocations)이다. `g1_flip_rle_region`의 `wrap`은 "사각형이 [0,stride)×[0,600)을 벗어남"이라는 기하 표지일 뿐이다. `0x466BE0` 원본은 클립하므로(쓰기 ⊆ rect ∩ clip) 실제 행 넘김 쓰기는 없다. 수 관계도 맞다: save000 wrap 1022 = reject_bounds 884 + 미러 중 기하 이탈 138(≤ clipped 146), save006 3099 = 2772 + 327(미러 327 전부 clipped). 결함 아님.

**정정 3 — V-4 "초기 6..12 −3k".** 프레임 6..12는 기준 21,419~22,329 → 18,236~19,052(−3,169~−3,312)이고 30..34는 3,070~3,482 → 0이다. 새∖기준이 0이므로 순수 제거다. 판정 범위 밖이며 work 서술과 같다.

## 코드 검수

- `mirror_flip_clip`(`g1_mirror2x.c:3351`) 본문에서 `flip_clip/FLIP_CLIP`을 `flip_rle/FLIP_RLE`로 바꾸면 `mirror_flip_rle`(`:3266`)과의 diff는 `if (stats.changed) ++g_X_changed_calls;` 1줄뿐이다(H-R과 공유하는 `g1_flip_rle_region` 호출은 이름 치환 때문에 표시만 다름). 원 인자 6개를 한 번 그대로 넘기고, x·y·w·h는 int32, 화면 교집합 → 전용 before 버퍼 → `g1_overlay_blt_apply`다.
- 연결: `G1_FLIP_CLIP 0x00466BE0u`·`_LEN 5u`, `expected_flip_clip = {83 EC 18 33 C0}`, install 목록 `:4208`(flip_rle 바로 뒤), restore `:4456`·집계 `:4475`, installed `:4578`. 참조 수 c 57/h 10/ddt 14로 flip_rle(56/9/13)보다 각 1 많다(`changed_calls`).
- objdump(원본 SHA 재확인): `0x466BE0` `83 EC 18`·`33 C0` 명령 경계 5 B, `ret 0x18`(`0x466D40`), 쓰기 `0x466D11` → watch EIP `0x466D15`. 호출처는 `0x419FB0`·`0x41A54A` 2곳뿐이다(.text 전체 grep).
- `direct_draw_trace.c` diff(lap1045 bridge 대비)는 버퍼 크기 4줄과 `flip_clip_details[480]` 블록 하나뿐이다. 출력 키·순서는 기존과 같다.
- 절차 이탈(첫 launch 이중 기동)은 `invalid_concurrent_*`로 격리돼 있고, 재계산 입력 run 이름과 겹치지 않는다. runtime `game` 사본은 8개 디렉터리 모두 삭제돼 있고 manifest/output은 남아 있다. 남은 probe 프로세스 0. save000 pair HOLD 사유 구조(selection/drag BLOCKED·input_effect HOLD)는 lap1045 기준과 같다.

## 판정

**H-V PASS(partial) 수용.** V-0, V-1(`0x466D15` 실효 22/run → 0, `0x46884E` 각 2 불변), V-2(마지막40 0 유지, 새∖기준 0, 제거 572 px), V-3(p95 7/8, tick 비 1.000), V-4(steady + 880 신규 0), V-S(버퍼 4개 최악 이상, 테스트 GREEN) 모두 PASS이고 코드 결함은 0이다. 정정 1~3은 판정에 영향이 없다. 기술 부분수용이며 G1 마일스톤 승인이 아니다.

## `0x4687F0` 독립 objdump(원본 SHA 재확인, H-W 사전등록 근거)

- 시작 바이트 `51`(push ecx)·`8B 54 24 0C`(mov edx,[esp+0xC]) = 명령 경계 5 B. 내부 분기 목표(`0x468829`·`0x46882F`·`0x468840`·`0x46884E`·`0x468856`·`0x468867`)와 .text 전체에 `0x4687F1..F4`로 오는 분기는 0이다. 두 번째 명령이 **esp 상대**이므로 trampoline은 원 함수와 같은 stack frame(call 1회로 진입)에서 실행돼야 한다. 기존 `install_one` + `G1Primitive6Fn` 호출이 그 조건이다(work가 테스트로 확인).
- `ret 0x18`(`0x46886B`) → stack 인자 6개, thiscall(ecx = 렌더러). 인자: x=arg1·y=arg2·w=arg3·h=arg4·rle=arg5·lut=arg6, 모두 32비트 `mov`/`imul`, `movsx` 없음. 목적지 = `[ecx+0x1514] + y·[ecx+0x10] + x`.
- **클립 없음.** h ≤ 0이면 바로 끝, w ≤ 0이면 행마다 쓰기 없이 stride만 더한다.
- RLE 규칙: `0xFE` 다음 바이트 = 투명 건너뛰기 수. 그 밖의 바이트는 **값을 쓰지 않고** 목적지의 현재 픽셀을 `lut`로 바꿔 다시 쓴다(`mov cl,[eax+edx]` → `mov cl,[ecx+ebp]` → `mov [eax+edx-1],cl` @`0x46884A`, 다음 명령 `0x46884E` = watch EIP). 즉 **목적지 의존 그림자/틴트 리맵**, 좌우 반전 없음. RLE 포인터는 행마다 초기화하지 않고 이어진다. 쓰기 열은 `[x, x+w)`뿐이다.
- 호출처는 `0x41A190` 1곳(`ecx = 0xE5BF18` 뒤 call)이다.
- 결론: 클립 없는 32비트 사각형이라 H-R `mirror_flip_rle`(`0x466B50`)과 같은 경계 처리(화면 교집합만 diff, 이탈은 `wrap_calls`)가 맞다. 목적지 의존 리맵이어도 before/after diff가 결과를 그대로 잡는다. 화면 밖 행 넘김 쓰기(x + w > stride)는 H-R과 같이 미추적 한계로 남고 계수로 보고한다.

## 다음 work — H-W `0x4687F0` 목적지 리맵 RLE diff 미러 사전등록

- 변경(`tools/inmm_stub/g1_mirror2x.c`·`.h`·`direct_draw_trace.c`): hook `0x4687F0`(old bytes `51 8B 54 24 0C`, len 5, thiscall, 6 stack args, `ret 0x18`). wrapper는 **`mirror_flip_rle`(H-R) 구조를 그대로** 쓴다(이름·주소·`changed_calls` 외 동일, H-V `mirror_flip_clip`과 같은 방식). 이름 `mirror_shade_rle`, 계수 `shade_4687F0_*`(invocations·mirrored_calls·mirrored_pixels·changed_calls·clipped_calls·wrap_calls·reject_target/bounds/size/guard), drift `w` f=`4687F0`. install·restore·installed·reset 목록에 넣는다. 새 `shade_details` 블록을 붙인 뒤 `mirror_details` 두 번째 builder 최악 합을 다시 계산하고(현재 6,893 + 새 블록), 7,200을 넘으면 크기를 올린다. 가능하면 V-S 호스트 테스트에 lstrcat 합 검사를 더한다(이번 정정 1과 같은 누락 방지).
- 테스트 RED→GREEN: hook 표(주소·old bytes·인자 6)·wrapper 계약(H-V 테스트 변형)·계수 노출·버퍼 최악.
- 실행(순차, run 직전 `/proc/loadavg` 기록·1분 load > 8이면 대기, 단일 인스턴스를 `pgrep`으로 확인한 뒤 **launch 명령은 한 번만**(lap1039·lap1047 이중 기동 재발 금지), run 뒤 `game` 사본만 삭제). `run_v.sh` 형식을 따르고 바꾸는 것만 적는다.
  1. save000 watch pair 2회: `--drift-samples "795,470;788,391;783,377"`. mask 인자는 lap1047과 같다.
  2. save000 성능 pair 2회(lap1047 s0 인자).
  3. save006 pair 2회(lap1047 s6 인자).
- PASS / FAIL:
  - **W-0:** 안전 7종 0, cleanup·source_unchanged true, `shade_4687F0` invocations = mirrored + reject_* 성립, invocations > 0. 기존 항등식 7종(`466BE0` 포함) 유지.
  - **W-1(가설 지표):** 실효 writer `0x46884E`인 stale present가 두 run 모두 **0**. 기준: (795,470) 2/run(lap1047 w, p140..141), (788,391) 실효 2/run(lap1041 s2, p202..204, 마지막 기록 EIP는 같은 값 덮어쓰기 `0x467692`), (783,377) 실효 2/run(lap1041 s3). 분리 확인: (783,377)의 실효 `0x468A28` 3/run은 그대로 남아야 한다. (795,470)의 `0x466D15`는 0으로 유지(H-V 비회귀).
  - **W-2(집계):** 마지막40 중앙값 0 유지. 덤프는 "새 r1∩r2 ∖ 기준(lap1047 w r1∪r2) = 0"과 "기준 r1∩r2 ∖ 새 r1∪r2(제거)"를 함께 적는다. 합계만으로 결론 내지 않는다.
  - **W-3(성능):** 성능 pair p95 ≤ 8ms, tick 비 0.99~1.01. 미달이면 load·히스토그램으로 UNKNOWN-환경 여부를 따로 적는다(기준 무변경).
  - **W-4(비회귀):** save006 steady 38 프레임과 880의 r1∩r2 신규 0. 초기 프레임(6..34)은 표로만 적는다.
  - **W-5(경계 계측):** `wrap_calls`와 함께, 원본이 실제로 행을 넘겨 쓰는 경우(x + w > stride 또는 x < 0)의 호출 수를 drift `w` 기하로 따로 센다. 0이 아니면 그 기하를 기록한다(미추적 한계 공개, 판정 실패 아님).
  - 반증: W-1이 0이 되지 않으면 같은 lap에서 `w` f=4687F0 기하와 `why`를 표로 남기고 HOLD로 middle에 넘긴다. reject_size가 생기면 크기를 기록한다.
- 금지: gate·validator·기준·`G1_OVERLAY_MAX_*` 변경, 원본/raw 수정, 다른 wrapper 동작 변경.
- 그다음 순서는 `0x4689C0`(`0x468A28`, 클립 없음·`ret 0x18`·호출처 `0x41A250`)이다.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서 작성, 재계산, read-only objdump만 했다. 게임/source/commit은 0이다. focused 검사와 SAFETY 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1047 full PASS 1636 `logs/gates/lap1047-work-full-check.log`).
- 남은 위험: 표본은 3점뿐이고 `0x466BE0` save000 호출 약 1,414회 중 mirrored는 530회다(화면 밖 884회). 미러 off 대조 run은 없다(V-3 미달이 없어서). `mirror_details` 합 검사는 아직 호스트 테스트 밖이다.
- backlog: `0x467E60`(같은 호출 블록, 미관측), save006 초기 프레임 6..12 잔여 약 18k(H-V 뒤), 팝업 p298..338 run 변동, hold keydown 위상, 가장자리 마우스 스크롤, overlay BltFast rejects, 다중 팝업 heal.
- 사용자 승인 상태: 기술 부분수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 루프를 막지 않는다.
- 다음 한 가지: work H-W(위 사전등록) → middle H-W 검수.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1047 work, 1,167 B, SHA256 `aa1858b37ead8588986e0bf8eb8b50c0397dc98c19af87b475f9ea4d8ad0e67e`)

```
lap1047 work(Claude Code claude-sonnet-5-5) H-V 구현·측정 완료, 독립 검수 필요(자가 승인 금지).
기록: docs/history/laps/20261006_lap1047_work_g1_hv_flip_clip_466be0_diff_mirror.md · 공유 temp 20261006_lap1047_work_hv/.
결과: V-0~V-4·V-S 전부 PASS(partial) — 표본 3점 0x466D15 stale present 22/run→0(0x46884E 각 2 불변), 마지막40 중앙값 0 유지·새∖기준 0·제거 572px, 성능 p95 7/8·tick 비 1.000, save006 steady+880 신규 0·pair PASS, 진단 버퍼 4개 수리+wsprintfA 형식 최악 테스트. 변경 uncommitted. 절차 이탈 1건: 첫 launch 이중 기동→즉시 종료·invalid_concurrent_*로 격리(수치 미사용).
승격 작업자가 이어서 할 일: (1) watch r1·r2·성능 r1·r2·save006 r1·r2를 새 스크립트로 재계산(항등식 1414=530+884 등, EIP 분포, 마지막40, setdiff, save006 초기 프레임 표, 성능·tick 비), (2) mirror_flip_clip이 mirror_flip_rle과 이름·주소·changed_calls 외 동일한지·objdump 0x466BE0 재확인, (3) V-S 버퍼 4개와 mirror_details 합 최악(6,848<7,200) 점검, (4) 수용 시 work H-W 사전등록(0x4687F0 → 0x4689C0).
```
