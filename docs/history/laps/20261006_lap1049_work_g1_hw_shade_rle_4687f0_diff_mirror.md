# 2026-10-06 | lap1049 | G1 work H-W — `0x4687F0` 목적지 리맵 RLE(6인자, 클립 없음) diff 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 모든 변경 uncommitted.
- 가설: lap1048 middle 사전등록(`20261006_lap1048_middle_g1_hv_acceptance_4687f0_hw.md` §다음 work) — 미후킹 `0x4687F0`(thiscall `ret 0x18`, old bytes `51 8B 54 24 0C`, 목적지 의존 lut 리맵·반전 없음·클립 없음·32비트)을 H-R `mirror_flip_rle` 구조(H-V `mirror_flip_clip`과 같은 방식) diff 미러로 hook하면 save000 표본 (795,470)·(788,391)의 마지막 writer `0x46884E` stale present가 0이 되고, (783,377)의 `0x468A28` 3/run은 그대로 남는다.
- 변경 파일:
  - `tools/inmm_stub/g1_mirror2x.c`: `G1_SHADE_RLE 0x004687F0u`·`_LEN 5u`, `expected_shade_rle {51 8B 54 24 0C}`, `g_original_shade_rle`(`G1Primitive6Fn`), `g_hook_shade_rle`, 전용 before 버퍼 `g_shade_rle_before`, 계수 10개(`invocations·mirrored_calls·mirrored_pixels·changed_calls·clipped_calls·wrap_calls·reject_target/bounds/size/guard`), wrapper `mirror_shade_rle`(= `mirror_flip_clip`을 이름·주소·before 버퍼만 바꿔 복제한 본문; 원 인자 6개 1회 전달, x·y·w·h int32, 화면 교집합 `g1_flip_rle_region`, drift `w` f=`4687F0`), install·reset·restore·installed 목록 연결. 두 번째 명령이 esp 상대이므로 기존 `install_one` trampoline 호출을 그대로 썼다.
  - `tools/inmm_stub/g1_mirror2x.h` accessor 10개, `tools/inmm_stub/direct_draw_trace.c` 요약 `shade_4687F0_*` 10키(`shade_rle_details[480]`).
  - `tests/test_g1_rect_fill.py`: 신규 `test_shade_rle_hook_table_and_wrapper_contract`(RED: `G1_SHADE_RLE` 부재 → GREEN)·`test_mirror_details_builder_holds_worst_case_concatenation`(두 번째 builder에 붙는 하위 블록 형식 최악 합 + 리터럴 합 ≤ 선언 크기; 현재 7,114+NUL < 7,200이라 `mirror_details` 크기는 7,200 유지, lap1048 정정 1의 누락 방지).
- 원본 SHA / 후보: 원본 EXE `b56986e0…8ac`(pair-result source_unchanged true 전 run). source sha256: `g1_mirror2x.c` `185b7098…14da`, `g1_mirror2x.h` `1e6c0a1f…1d8c`, `direct_draw_trace.c` `b23b5afe…bcb`, `test_g1_rect_fill.py` `73e3429f…9054`. 6 run 모두 설치 성공(`shade_4687F0_*` 출력, 설치 시 old bytes 검증).
- 실행(공유 temp `20261006_lap1049_work_hw/`, 로그 `logs/gates/lap1049_hw_*`): `run_w.sh`(lap1047 `run_v.sh`에서 이름·표본만 변경, 순차·단일 인스턴스·run 직전 load 대기·run 뒤 `game` 사본 삭제). **launch 1회**(이중 기동 없음, `pgrep`으로 단일 인스턴스 확인). load 대기 0(시작 load 3.5~5.9). save000 watch pair 2회(`--drift-samples "795,470;788,391;783,377"`, mask 인자 lap1047과 동일), save000 성능 pair 2회, save006 pair 2회. exit: watch 2·2, s0 2·2(기존 pair HOLD), s6 0·0.

## 수치

| 항목 | 기준 | lap1049 |
|---|---|---|
| **W-0** 안전 7종·cleanup·source_unchanged | 0 / true / true | 6 run 전부 0 / true / true |
| W-0 항등식 `shade_4687F0` | — | invocations 190 = mirrored 183 + reject_bounds 7 (reject_target/size/guard 0, clipped 22, changed 176), watch r1·r2·s0 r1·r2 동일. `flip_clip_466BE0` 1416 = 530 + 886 등 기존 항등식 유지 |
| 무장·selftest | PASS·fail 0 | selftest PASS·무장 52라운드 fail 0·좌표 (795,470)(788,391)(783,377)·dropped/overflow 0 |
| **W-1** (795,470) 마지막 writer stale present | lap1047 w: 2/run (`0x46884E`, p140..141) | **0**/run (u 22, hit 570). `0x466D15` 0 유지 |
| W-1 (788,391) | lap1041 s2: 실효 2/run (`0x46884E`) | **0**/run (u 3, hit 521) |
| W-1 (783,377) | lap1041 s3: `0x46884E` 실효 2 + `0x468A28` 3 | **`0x468A28` 3/run 그대로**(p304..366, 값 일치 3/3, 스택 `0x41A255<0x402859`), `0x46884E` 0 → 분리 확인 |
| **W-2** 마지막40 중앙값 | 0 | **0 / 0**(watch r1·r2), 성능 r1·r2도 0. p24..58·p84..365·p366~ 중앙값 0, p298..338 412/412·303(성능 r2) |
| W-2 새 r1∩r2 ∖ 기준(lap1047 w r1∪r2) | — | **1,795 px / 9프레임**(r1·r2 동일 마스크): 프레임 298 297·308 331·318 246·328 246·338 412(y218..226×x240..323 팝업 상자), 174 62·294 108·352 7·366 86(y372..476×x686..790 우측 군) |
| W-2 기준 r1∩r2 ∖ 새 r1∪r2 (제거) | — | 1,508 px(프레임 298 221·6 145 등) |
| W-2 r1∩r2 합(참고, 지표 불안정) | 2,338 | 2,625(r1·r2 각 2,625). 이 합으로 결론 내지 않는다 |
| **W-3** 성능 pair p95 | ≤8, tick 비 0.99~1.01 | **8 / 8**, tick delta 후보 401·400 vs 기준 400·399 → 비 1.0025·1.0025. 시작 load 3.5~5.9. watch run p95 10/11(watch 계측 run, 판정 외) |
| **W-4** save006 steady 38 + 880 | 신규 0 | **r1∩r2 0**(39프레임 공통), 기준(lap1047 s6 r1·r2) 대비 신규 0/0·제거 0/0, p95 8/7·cov p50 99.31%, 안전 0, pair status **PASS(exit 0)** 2회(V2/V2s/V2q·scale2x 포함 9 gate 전부 PASS) |
| **W-5** 경계 계측 | — | `shade_4687F0_wrap_calls` **0**(행을 넘겨 쓰거나 x<0인 호출 없음), 화면 밖 호출 `reject_bounds` 7(전부 사각형이 화면 밖), clipped 22. 미추적 한계 해당 0 |

## 해석
- 가설 확정: 표본 2점의 `0x46884E` stale present가 0이 되었고(r1·r2 동일), 분리 확인 대상 `0x468A28` 3/run은 그대로 남았다. 마지막40 중앙값 0 유지.
- **W-2 새 ∖ 기준 1,795 px는 H-W 효과가 아니다(근거 3):** (a) 이 9프레임의 stale 마스크가 r1·r2에서 완전히 같고(결정적), 그 위치의 stale 개수 조합이 H-W 이전 lap들(lap1039 hr, lap1041 hs, lap1045 hu, lap1047 hv)에서도 run 변형으로 나타난다(그 밖에 `[88,144,366,281,20,122]`·`[88,144,388,303,20,122]` 등 다른 조합도 25 run 중 존재, 전부 H-W 이전 run 포함): 변형 A `[88,144,497,412,20,122]`(lap1039 s0 r1·r2, lap1045 s0 r1, lap1047 s0 r2, lap1049 w r1·r2·s0 r1)와 변형 B `[37,46,377,0,16,46]`(lap1045 w r2, lap1047 w r1·r2, lap1041 s2 r2 등)(프레임 174·294·298·338·352·366 상자 합). lap1047 w 두 run이 변형 B였고 이번 w 두 run이 변형 A라 기준 합집합 대비 "새"로 보일 뿐이다. (b) 해당 위치 직전 3 present의 `w` 기록 중 `0x4687F0` 사각형과 겹치는 것이 없다(프레임 366의 `0x467580` 4건만 겹침, 이미 수용된 hook). (c) 이 hook은 `0x4687F0`이 쓴 사각형만 diff 미러하므로 다른 위치에 새 stale을 만들 수 없다. 이 판정의 한계: 변형 A/B 결정 원인은 미조사(UNKNOWN), 기준을 바꾸지 않았다.
- 성능: p95 8/8·tick 비 1.0025로 H-U(7/7)와 구분되는 변화가 없고 watch/성능 외 대조(미러 off)는 W-3 미달이 없어 실행하지 않았다.
- `mirror_details` 최악 합은 새 블록 포함 7,114(+NUL) < 7,200이라 크기 유지.

## 회귀 / 남은 위험 / 독립 검수
- 변경 uncommitted. 게임 사본 `local/runtime/lap1049_hw_*/game` 6개는 run 직후 삭제(manifest/output/prefix·로그 보존). 잔여 probe 프로세스 0.
- 남은 위험: 표본은 3점뿐이고 `0x4687F0` save000 호출은 190회(mirrored 183)다. 변형 A/B 원인 미조사. 다음 단계 `0x4689C0`(`0x468A28`, 클립 없음·`ret 0x18`·호출처 `0x41A250`) — 표본 (783,377) 3/run.
- 독립 검수는 다음 middle(Opus)이 새 스크립트로 6 run을 재계산하고 변형 A/B 판정과 코드 diff(`mirror_shade_rle` = `mirror_flip_clip` 이름 치환)·objdump `0x4687F0`을 확인한다. 이 work는 자가 승인하지 않는다.
- 다음 한 가지: middle H-W 검수 → work `0x4689C0`.
