# 2026-10-06 | lap1050 | G1 middle — H-W 독립 검수 → work H-X(`0x4689C0`) + W-S2 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·source 변경·commit은 0이다.
- 검수 대상: lap1049 work H-W(`0x4687F0` 목적지 리맵 RLE 6인자 diff 미러 `mirror_shade_rle`)와 새 테스트 2개. lap1048 §다음 work의 사전등록 W-0~W-5와 대조했다.
- 처리한 인계: `loop/ESCALATE_SOL`(lap1049 work, 1,094 B, SHA256 `d0df8730272dba834ba84b7a8c84f9fb6bf65896e2fb022748d627218f728220`). 원문은 아래 부록에 두고, 처리한 뒤 파일을 삭제했다.
- 변경 파일: 이 기록, `docs/STATUS.md`. source/test 변경은 0이다.
- 원본 SHA / 환경 / fixture: 원본 EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` sha256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 다시 확인했다. 새 6 run과 기준 10 run 모두 private EXE 앞 16자가 일치한다. fixture는 save000(index 1)과 save006, 격리 prefix/display. 현재 source `g1_mirror2x.c` `185b7098…14da`·`g1_mirror2x.h` `1e6c0a1f…1d8c`·`direct_draw_trace.c` `b23b5afe…bcb`·`test_g1_rect_fill.py` `73e3429f…9054`는 work 기록과 같고, 6 run bridge 사본과 byte 일치한다(`cmp`).
- 재계산: 공유 temp `20261006_lap1050_middle_review/`. work의 `analyze_w_*.py`·`isect_w.py`·`setdiff_w.py`·`newloc_w.py`와 제품 helper는 쓰지 않았다. middle 소유 lap1048 재계산 코드를 문자열 치환으로 옮겨(run 집합·표본 좌표·H-W family/함수 범위) 새로 만들었다.
  - `recalc_lap1050.py` `9f3ef32c…3f28` → `recalc_lap1050.json` `4c8ecb13…66bb`. 대상은 새 6 run(lap1049 w r1/r2·s0 r1/r2·s6 r1/r2)과 기준 10 run(lap1047 w·s0·s6 각 r1/r2, lap1041 s2·s3 각 r1/r2)이다.
  - `variant_lap1050.py` `7a40b124…fbffd` → `variant_lap1050.json` `b505b5dd…58c3`: W-2 새∖기준 픽셀을 H-W 이전 save000 run 21개(lap1039 w·s0·ctl, lap1041 s1 r2/r3·s2·s3, lap1045 w·s0, lap1047 w·s0; lap1041 s1_r1은 무효 run이라 제외)와 프레임별로 대조했다.
  - `details_worst_lap1050.py` `e7458714…4e43`(lap1048 스크립트 복사, docstring 1줄 외 로직 동일) → `details_worst_builder2_lap1050.json` `09a80b09…58c9`·lap1047 bridge 판 `details_worst_builder2_lap1047src.json` `acb1927b…63d5`, 합 `details_sum_lap1050.py` `c731293b…d819` → `details_sum_lap1050.txt` `25695cb8…cf5a`.
  - objdump 직접 재생성: `od_4687F0_lap1050.txt` `2944c081…64b7`(lap1048 판과 같은 범위에서 내용 동일), `od_4689C0_lap1050.txt` `edaccbb9…dcec`. wrapper diff `diff_wrapper_lap1050.txt`(빈 파일).

## 재계산 결과(판정 불일치 0, 정정 3건)

| 항목 | lap1049 work 보고 | lap1050 재계산 |
|---|---|---|
| W-0 안전·cleanup·source_unchanged | 0 / true / true | 6 run 모두 안전 7종 max 0, cleanup·source_unchanged [true,true], trace JSONL 손상 0, ps3 410/410/411/411/884/887 |
| W-0 항등식 | 190 = 183 + 7 | **같음.** `shade_4687F0` save000 4 run 모두 190 = 183 + reject_bounds 7(target/size/guard 0), clipped 22, changed 176, mirrored_pixels 22,598. save006은 invocations 0(이 장면에서 미호출). 기존 7 family도 6 run 모두 성립(`flip_clip_466BE0` w 1416 = 530 + 886, s0 1418 = 530 + 888, s6 3090 = 326 + 2764 / 3105 = 327 + 2778) |
| 무장·selftest | PASS·fail 0 | selftest PASS, 무장 52 round, fail 0, 모든 round 좌표 = 표본 3점, dropped/overflow 0 |
| **W-1** (795,470) | 2/run → 0 | **같음.** 기준 lap1047 w r1/r2: 2(`0x46884E`, p140..141, 값 일치 2/2). 새: 0, `u` 22, hit 570 |
| W-1 (788,391) | 실효 2/run → 0 | **같음.** 기준 lap1041 s2 r1/r2: 마지막 기록 `0x467692` 2, 실효 `0x46884E` 2(p202..204). 새: 0, `u` 3, hit 521 |
| W-1 (783,377) 분리 | `0x468A28` 3/run 유지, `0x46884E` 0 | **같음.** 기준 lap1041 s3: 5 = 실효 `0x468A28` 3 + `0x46884E` 2. 새: 3 = `0x468A28` 3(구간 p304..305·p366, 값 일치 3/3), `0x46884E` 0 |
| W-1 미러 작동 | — | `0x46884E` watch hit는 새 run에도 점별 2/2/4회 남는다(함수는 계속 그 점을 쓴다). stale이 사라진 이유는 쓰기 제거가 아니라 diff 미러 반영이다 |
| **W-2** 마지막40 | 0/0 | **0/0**(watch), 성능 run도 0/0 |
| W-2 새 r1∩r2 ∖ 기준(lap1047 w r1∪r2) | 1,795 px / 9 프레임 | **같음.** 174 62·294 108·298 297·308 331·318 246·328 246·338 412·352 7·366 86. 새 w r1 = r2(마스크 합 2,625/2,625, 교집합 2,625) |
| W-2 제거 | 1,508 px | **같음**(6 36·12 36·144 126·174 92·204 72·234 121·294 75·298 221·308 135·318 115·328 115·352 110·366 109·399 145) |
| **W-2 변형 판정(독립)** | 변형 A/B, H-W 효과 아님 | **확인.** H-W 이전 run **lap1047 s0_r2(H-V 제품, H-W만 없음)의 마스크가 9 프레임 모두 새 w r1과 픽셀 단위로 완전히 같다.** lap1039 s0 r1/r2·lap1045 s0 r1도 새∖기준 1,795 px를 9 프레임 전부 포함한다. H-W 이전 run 합집합이 1,795/1,795를 덮는다. 기준을 lap1047 s0 r1∪r2로 바꾸면 새 w·성능 r1∩r2 ∖ 기준 = **0**. 즉 lap1047 w 두 run이 우연히 작은 변형(B)이었을 뿐이다 |
| **W-3** 성능 pair | p95 8/8, tick 비 1.0025 | **같음.** 히스토그램 nearest-rank p95 8/8, 평균 5.409/5.315(기준 lap1047 s0 5.098/5.245), 10ms 이상 4/6(기준 0/9), tick delta 후보 401/400·pair 기준 400/399 → 비 1.00249/1.00251. 시작 load 4.07/4.23. watch run p95 10/11(기준 lap1047 w 12/12) |
| **W-4** save006 | steady + 880 신규 0, pair PASS | **같음.** 공통 51 프레임(steady 38 + 880 포함), 새 r1∩r2 비0 프레임은 6..12뿐(18,236~19,052, r1 = r2), steady·880 신규 0. pair status PASS(exit 0) 2회 |
| **W-5** 경계 | wrap 0 | **같음.** `shade_4687F0_wrap_calls` 0, drift `w` f=4687F0 15건(mirrored 9·clipped 6) 중 x<0 또는 x+w>stride(832) 0 |

**정정 1 — `mirror_details` 두 번째 builder 최악 합(코드 결함, 비차단·필수 수리).** work 기록은 "7,114(+NUL) < 7,200이라 크기 유지"라고 적었다. 이번 계산은 **7,288 B(NUL 포함)로 선언 7,200을 88 B 넘는다.** 같은 방식으로 lap1047 bridge를 계산하면 lap1048 값 6,893과 정확히 일치한다(검산). 증가분 395 = `shade_rle_details` 형식 최악. 새 테스트 `test_mirror_details_builder_holds_worst_case_concatenation`가 이 초과를 놓친 이유는 두 가지다. (a) `mirror_details` 자체 wsprintf의 `%s` 2개(`panel_frame_sha256` 64자·`panel_asset_key` 63자, lap1048 정정 1과 같은 상한)에 `_STRING_ALLOWANCE` 0을 써서 127 B를 빠뜨린다. (b) lstrcat 리터럴을 escape된 원문 길이로 세서 2 B를 더 센다. 테스트 자체 합은 7,164 + NUL이다(work 기록 7,114와도 다르다). 실제 run의 metrics 줄 최대는 6,110 B(JSON 외피 포함)이고 모든 계수가 10자리가 되는 최악은 현실에서 도달하지 않는다. 그래서 런타임 판정에는 영향이 없다. 하지만 lap1048 사전등록 "7,200을 넘으면 크기를 올린다"를 어겼고, 다음 hook family(약 +395)가 붙으면 7,683이 된다. → 다음 work의 **선행 수리 W-S2**로 지정한다(아래).

**정정 2 — W-2 변형 서술.** work는 lap1039 s0 r1·r2를 "변형 A `[88,144,497,412,20,122]`"에 넣었다. 프레임 전체 합으로 보면 lap1039 s0의 프레임 298은 974로 새 run(497)의 상위집합이고, 프레임 352의 합은 25다(work의 20은 상자 한정 값으로 보인다). 마스크 완전 일치는 lap1047 s0_r2뿐이다. 결론(H-W 이전 run 변형)은 같다.

**정정 3 — W-4 "제거 0/0" 범위.** 판정 범위(steady + 880)에서는 맞다. 초기 프레임까지 보면 12에서 신규 1 px, 10에서 제거 1 px가 있다. save006에서 `shade_4687F0` 호출은 0이므로 H-W와 무관한 run 변동이다.

## 코드 검수

- `mirror_shade_rle`(`g1_mirror2x.c:3462`) 본문은 `mirror_flip_clip`(`:3376`)에서 `flip_clip→shade_rle`·`FLIP_CLIP→SHADE_RLE`·`466BE0→4687F0`만 치환한 것과 **diff 0**이다(77줄). 원 인자 6개를 한 번 그대로 넘기고, x·y·w·h는 int32, 화면 교집합 `g1_flip_rle_region` → 전용 before 버퍼 `g_shade_rle_before`(`:240`, 크기 `G1_OVERLAY_MAX_WIDTH*HEIGHT`) → `g1_overlay_blt_apply` → drift `w` f=`4687F0`.
- 연결: `G1_SHADE_RLE 0x004687F0u`(`:51`)·`_LEN 5u`(`:82`), `expected_shade_rle = {51 8B 54 24 0C}`(`:4236`), install은 flip_clip 바로 뒤(`:4324`), restore `:4583`·`:4603`, NULL 초기화 `:4623`, installed `:4708`. 참조 수 c 60/h 10/ddt 14로 flip_clip과 같다.
- objdump(원본 SHA 재확인): `0x4687F0` `51`·`8B 54 24 0C` 명령 경계 5 B, 두 번째 명령이 esp 상대라 trampoline은 같은 frame에서 call 1회로 실행돼야 하며 기존 `install_one` + `G1Primitive6Fn` 경로가 그 조건이다. 쓰기 `0x46884A`(`mov [eax+edx-1],cl`) → watch EIP `0x46884E`, `ret 0x18`(`0x46886B`). lap1048 판과 같은 범위에서 내용이 같다.
- 런타임: `local/runtime/lap1049_hw_*` 6개 모두 `game` 사본 삭제, manifest/output 보존. 남은 probe 프로세스 0. exit 파일 w 2·2, s0 2·2(기존 save000 pair HOLD), s6 0·0. 무효 run 디렉터리 없음(launch 1회).

## 판정

**H-W PASS(partial) 수용.** W-0, W-1(`0x46884E` 실효 2/run → 0, `0x468A28` 3/run 분리 유지), W-2(마지막40 0 유지, 새∖기준 1,795 px는 H-W 이전 run 변형과 픽셀 단위로 일치), W-3(p95 8/8, tick 비 1.0025), W-4(steady + 880 신규 0, pair PASS), W-5(wrap 0)가 모두 PASS이다. 정정 1은 실제 코드 결함이지만 현실 도달 불가 최악이라 런타임 판정을 바꾸지 않는다. 다음 work의 선행 수리로 지정한다. 기술 부분수용이며 G1 마일스톤 승인이 아니다.

## `0x4689C0` 독립 objdump(원본 SHA 재확인, H-X 사전등록 근거)

- 시작 바이트 `51 53 55 56 57`(push ecx/ebx/ebp/esi/edi) = 1 B 명령 5개, 경계 5 B(`0x4689C5`). 내부 분기 목표(`0x4689FB`·`0x468A01`·`0x468A12`·`0x468A2C`·`0x468A34`·`0x468A44`)와 .text 전체에서 `0x4689C1..C4`로 오는 분기는 0이다. 호출처는 `0x41A250` 1곳(`call 0x4689c0`)이다.
- `ret 0x18`(`0x468A49`) → stack 인자 6개, thiscall(ecx = 렌더러, ebx에 보관). push 5개 뒤 `[esp+0x18]`=x·`[esp+0x1C]`=y·`[esp+0x20]`=w·`[esp+0x24]`=h·`[esp+0x28]`=rle·`[esp+0x2C]`=lut, 모두 32비트 `mov`/`imul`. 목적지 행 = `[ebx+0x1514] + y·[ebx+0x10] + x`.
- **클립 없음.** h ≤ 0이면 끝, w ≤ 0이면 행마다 쓰기 없이 stride만 더한다.
- RLE 규칙은 `0x4687F0`과 같다(`0xFE` 다음 바이트 = 건너뛰기 수, 그 밖의 바이트는 값을 쓰지 않음). 차이는 **좌우 반전**이다: 열 위치 = `movsx(w − 1 − k)`(16비트 부호 확장)이고, 목적지의 현재 픽셀을 읽어 `lut`로 바꿔 같은 자리에 다시 쓴다(`mov [eax],bl` @`0x468A26`, 다음 명령 `0x468A28` = watch EIP). 쓰기 열은 여전히 `[x, x+w)`뿐이다(w ≤ 32,767 전제, 화면 크기 범위 안).
- 결론: 클립 없는 32비트 사각형이라 H-R `mirror_flip_rle`/H-W `mirror_shade_rle`과 같은 경계 처리(화면 교집합만 diff, 이탈은 `wrap_calls`)가 맞다. 반전이어도 쓰기 집합은 같은 사각형이라 before/after diff가 결과를 그대로 잡는다. 첫 5 B가 push뿐이라 trampoline 복사도 안전하다(esp 상대 피연산자 없음).

## 다음 work — W-S2(선행 수리) + H-X `0x4689C0` 반전 목적지 리맵 RLE diff 미러 사전등록

- **W-S2(먼저, RED→GREEN):** `tests/test_g1_rect_fill.py::test_mirror_details_builder_holds_worst_case_concatenation`을 고친다. (a) `mirror_details` 자체 wsprintf의 `%s` 상한을 64 + 63으로 센다(인자 `g1_mirror2x_panel_frame_sha256()`·`g1_mirror2x_panel_asset_key()`). (b) lstrcat 리터럴은 C escape를 푼 길이로 센다. 고친 테스트가 현재 source에서 **RED(7,288 > 7,200)**인 것을 먼저 확인하고, `direct_draw_trace.c` 두 번째 builder의 `char mirror_details[7200]`을 H-X 블록까지 들어가는 크기(권장 8,192)로 올려 GREEN으로 만든다. 첫 builder(최악 6,043)는 바꾸지 않는다. 크기를 pin하는 다른 테스트가 있으면 같이 갱신하고 기록한다.
- **H-X 변경**(`tools/inmm_stub/g1_mirror2x.c`·`.h`·`direct_draw_trace.c`): hook `0x4689C0`(old bytes `51 53 55 56 57`, len 5, thiscall, 6 stack args, `ret 0x18`). wrapper는 `mirror_shade_rle` 구조를 그대로 쓴다(이름·주소·before 버퍼만 다름). 이름 `mirror_shade_flip`, 계수 `shade_flip_4689C0_*`(invocations·mirrored_calls·mirrored_pixels·changed_calls·clipped_calls·wrap_calls·reject_target/bounds/size/guard), drift `w` f=`4689C0`, install(shade_rle 바로 뒤)·restore·installed·reset 목록. 새 `shade_flip_details` 블록을 붙인 뒤 W-S2 테스트가 GREEN이어야 한다.
- 테스트 RED→GREEN: hook 표(주소·old bytes·인자 6)·wrapper 계약(H-W 테스트 변형)·계수 노출·builder 최악 합.
- 실행(순차, run 직전 `/proc/loadavg` 기록·1분 load > 8이면 대기, 단일 인스턴스를 `pgrep`으로 확인한 뒤 **launch 명령은 한 번만**, run 뒤 `game` 사본만 삭제). `run_w.sh` 형식을 따르고 바꾸는 것만 적는다.
  1. save000 watch pair 2회: `--drift-samples "783,377;786,220;718,452"`. mask 인자는 lap1049와 같다.
  2. save000 성능 pair 2회(lap1049 s0 인자).
  3. save006 pair 2회(lap1049 s6 인자).
- PASS / FAIL:
  - **X-0:** 안전 7종 0, cleanup·source_unchanged true, `shade_flip_4689C0` invocations = mirrored + reject_* 성립, invocations > 0. 기존 항등식 8종(`4687F0` 포함) 유지.
  - **X-1(가설 지표):** 실효 writer `0x468A28`인 stale present가 두 run 모두 **0**. 기준: (783,377) 3/run(lap1049 w, p304..305·p366). (718,452)은 lap1041 s2 실효 `0x468A28` 1 + `0x46884E` 2였으므로 H-W 뒤 기준은 이번 run이 처음 측정한다(이번 결과를 표로 적고, `0x468A28` 0이면 PASS). (786,220)은 lap1041 s3 `0x46884E` 1(p399)이었으므로 H-W 비회귀(0) 확인용이다. 남는 stale이 있으면 실효 writer EIP를 표로 적는다.
  - **X-2(집계):** 마지막40 중앙값 0 유지. 덤프는 "새 r1∩r2 ∖ 기준" 두 가지를 함께 적는다: 기준 = lap1049 w r1∪r2, 그리고 기준 = lap1049 w r1∪r2 ∪ lap1047 s0 r1∪r2(이번 lap에서 확인한 run 변형 포함). 둘째가 0이 아니면 그 프레임·위치를 적고, H-W 이전 run 합집합과 대조한다. 합계만으로 결론 내지 않는다.
  - **X-3(성능):** 성능 pair p95 ≤ 8ms, tick 비 0.99~1.01. 미달이면 load·히스토그램으로 UNKNOWN-환경 여부를 따로 적는다(기준 무변경).
  - **X-4(비회귀):** save006 steady 38 프레임과 880의 r1∩r2 신규 0. 초기 프레임(6..34)은 표로만 적는다.
  - **X-5(경계 계측):** `wrap_calls`와 drift `w` 기하 중 x<0 또는 x+w>stride 수. 0이 아니면 기하를 기록한다(미추적 한계 공개, 판정 실패 아님).
  - **X-S:** W-S2 테스트 RED(현재 source) → GREEN(크기 상향 + H-X 블록 포함). 최악 합과 선언 크기를 기록한다.
  - 반증: X-1이 0이 되지 않으면 같은 lap에서 `w` f=4689C0 기하와 `why`를 표로 남기고 HOLD로 middle에 넘긴다. reject_size가 생기면 크기를 기록한다.
- 금지: gate·validator·기준·`G1_OVERLAY_MAX_*` 변경, 원본/raw 수정, 다른 wrapper 동작 변경.
- 그다음 후보: 표본 밖 잔여는 X-2 결과로 다시 고른다. backlog 미후킹 `0x467E60`(호출 `0x41A887`, 미관측)은 관측될 때만 다룬다.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서 작성, 재계산, read-only objdump만 했다. 게임/source/commit은 0이다. focused 검사와 SAFETY 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1049 full PASS 1638 `logs/gates/lap1049-work-full-check.log`).
- 남은 위험: 표본은 3점뿐이고 `0x4687F0` save000 호출은 190회(mirrored 183)다. 변형 A/B의 결정 원인은 미조사(UNKNOWN)이며 판정은 마스크 일치로만 닫았다. `mirror_details` 최악 초과(정정 1)는 다음 work에서 수리될 때까지 남는다(현실 도달 불가).
- backlog: `0x467E60`, save006 초기 프레임 6..12 잔여 약 18k, 팝업 p298..338 run 변동(변형 A/B), hold keydown 위상, 가장자리 마우스 스크롤, overlay BltFast rejects, 다중 팝업 heal.
- 사용자 승인 상태: 기술 부분수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 루프를 막지 않는다.
- 다음 한 가지: work W-S2 + H-X(위 사전등록) → middle H-X 검수.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1049 work, 1,094 B, SHA256 `d0df8730272dba834ba84b7a8c84f9fb6bf65896e2fb022748d627218f728220`)

```
lap1049 work(Claude Code claude-sonnet-5-5) H-W 구현·측정 완료, 독립 검수 필요(자가 승인 금지).
기록: docs/history/laps/20261006_lap1049_work_g1_hw_shade_rle_4687f0_diff_mirror.md · 공유 temp 20261006_lap1049_work_hw/.
결과: W-0·W-1·W-2(마지막40 0)·W-3·W-4·W-5 PASS(partial) — 표본 (795,470)·(788,391)의 0x46884E stale present 2/run→0, (783,377)의 0x468A28 3/run 유지(분리 확인), 성능 p95 8/8·tick 비 1.0025, save006 steady+880 신규 0·pair PASS, shade_4687F0 190=183+7·wrap 0. 변경 uncommitted. 절차 이탈 없음(launch 1회).
승격 작업자가 이어서 할 일: (1) watch r1·r2·성능 r1·r2·save006 r1·r2를 새 스크립트로 재계산(항등식 190=183+7, 0x46884E 분포, 마지막40, setdiff), (2) W-2 "새∖기준 1,795 px"가 H-W 이전 lap(1039~1047)에도 나타나는 run 변형(상자 합 조합 일치)이라는 work 판정을 독립 확인, (3) mirror_shade_rle이 mirror_flip_clip과 이름·주소·before 버퍼 외 동일한지·objdump 0x4687F0 재확인, (4) 수용 시 work H-X 사전등록(0x4689C0).
```
