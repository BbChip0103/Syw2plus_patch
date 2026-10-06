# 2026-10-07 | lap1085 | G1 work — D-0′ 디스크 회수 + H-W330 (`0x467580`·`0x467B00` 폭>320 tiled 미러)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 자기 결과를 승인하지 않는다. 독립 검수는 `loop/ESCALATE_SOL`로 middle(Opus)에 인계.
- 가설: lap1084 사전등록 H-W330 — `mirror_blend_wrle`(`0x467580`)·`mirror_blend_clip`(`0x467B00`)이 클립 뒤 폭 > 320(실측 330×200)을 `reject_size`로 버려 save006 UPLEFT,DOWNRIGHT hold 창 stale 240,703(ord 126~133·140~145·221~225)이 생긴다. 이미 검증된 `g1_overlay_blt_apply_tiled`로 바꾸면 그 stale은 0이 된다.
- 예상 PASS / FAIL: lap1084 §5 사전등록(아래 판정표).
- 변경 파일(uncommitted): `tools/inmm_stub/g1_mirror2x.c` `a1f582fc…`, `tests/test_g1_rect_fill.py` `e8215bd1…`, `tests/test_g1_overlay_blt.py` `e1303732…`. 하네스·bridge·헤더·공유 상수(`G1_OVERLAY_MAX_*`)·scratch 불변. 신규 계수 0(헤더·bridge·`mirror_details` 크기 불변).
- 원본 SHA / fixture: 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac` MATCH(모든 run `source_unchanged` true). 비합성 save006(`--p4b-s-snapshot`), scale2x HD, load ≤ 8. 활성 인원은 G1 save006 기준(G2 8인 증거 아님).

## D-0′ 디스크 회수 (게임 실행 전)

- 시작 여유 11.3 GiB(< 20). `local/maintenance/20261007_lap1083_prefix_archive/archive.py`를 새 디렉터리 `local/maintenance/20261007_lap1085_prefix_archive/archive.py`로 **복사**(출력 경로 한 줄만 변경, 원본 불변)해 같은 절차로 실행: `lap10[5-7]*` 종료 prefix를 오름차순, 목표 21 GiB, 경계 `lap1080`.
- prefix마다 pair-result `source_unchanged`·`cleanup.ok`·`prefix_processes_after` 비어 있음·`game_removed`, manifest/`prefix` 일치, 프로세스·`lsof`·`WINEPREFIX` 참조 0, 전체 inventory, tar 전 멤버 SHA/mode/symlink 대조 뒤에만 `prefix` 삭제. 0·10·20번째는 **실제 전체 restore** 후 inventory 완전 일치(`restore_verification_000/010/020.json` 모두 `full_content_metadata_match` true).
- 결과: 21 prefix 처리(`lap1056_hz_d4`~), 여유 **11.32 → 21.25 GiB**(≥ 20 PASS). `report.json` `e3125322…`·`plan.json` `c6b73fd8…`. manifest·output·로그 보존, `game` 사본은 run마다 삭제.
- **종료 시 여유 7.9 GiB**(W-1 9 run이 prefix 약 1.3 GiB씩 남김). 다음 work는 게임 실행 전 D-0를 다시 해야 한다(다음 대상 = lap1057~lap1079 미처리 prefix, plan에서 `lap1056` 이후).

## W-0 구현 (테스트 먼저 RED→GREEN)

- RED: `tests/test_g1_rect_fill.py` 계약을 새 계약으로 바꿔 `test_blend_weighted_rle_hook_table_and_wrapper_contract` 실패 확인(`g_blend_wrle_before` 선언이 screen 크기가 아님).
- GREEN `tools/inmm_stub/g1_mirror2x.c`:
  - `g_blend_wrle_before`·`g_blend_clip_before` = `G1_OVERLAY_SCREEN_WIDTH × G1_OVERLAY_SCREEN_HEIGHT`, hook별 `g_blend_wrle_tile`·`g_blend_clip_tile` = `MAX_WIDTH × MAX_HEIGHT`(H-L2 `g_flip_blend7_*` 패턴).
  - 두 hook의 `> MAX_WIDTH`/`> MAX_HEIGHT` 크기 검사 분기 제거. 화면 교집합 [x0,x1)×[y0,y1)·대상 검사·guard·`layer_drift_write_*`·원본 1회 호출·인자 전달은 그대로. 적용은 `g1_overlay_blt_apply_tiled`(wrle는 기존 `g1_overlay_blt_apply`, clip은 기존 `apply_banded` 대체). `reject_size`는 이제 apply 실패일 때만 증가한다.
  - 계수 이름 유지. `blend_467B00_band_calls`는 **"타일 > 1 호출 수"**로 뜻을 바꿔 유지(`if (tiles > 1u) ++g_blend_clip_band_calls;`).
  - `0x4685C0`(`mirror_blend_skip`)은 사전등록 범위 밖이라 banded 그대로 둔다.
- 바꾼 테스트 단언(완화 아님, 새 계약으로 교체):
  1. wrle 계약: 적용 위치 인덱스를 `g1_overlay_blt_apply(` → `g1_overlay_blt_apply_tiled(`로, 새 `_assert_tiled_blend_wrapper("blend_wrle", …)` 추가.
  2. clip 계약: 같은 인덱스 교체, `_assert_banded_blend_wrapper("blend_clip", …)` → `_assert_tiled_blend_wrapper("blend_clip", …)`, `if (tiles > 1u) ++g_blend_clip_band_calls;` 단언 추가.
  3. skip 계약: "clip과 skip 본문이 이름만 다른 같은 코드" 동등 단언 삭제(clip이 tiled로 갈라졌으므로), 대신 skip 본문에 `g1_overlay_blt_apply_tiled(` 없음 단언 추가(`_assert_banded_blend_wrapper("blend_skip")`는 그대로).
  4. 새 `_assert_tiled_blend_wrapper`: screen 크기 before·MAX 크기 tile 선언, 본문에 `apply_tiled` 정확히 1회·`apply(`/`apply_banded(` 없음·`MAX_WIDTH`/`MAX_HEIGHT` 문자열 없음(크기 사전검사 제거)·원본 정확히 1회·`reject_size` 증가 1곳·`layer_drift_write_end(&drift, <define>, why`.
  5. `tests/test_g1_overlay_blt.py` tiled C 모델 전수에 사전등록 (a) 3케이스 추가: 330×200 at (34,−126)→화면부분 (34,0,330,74)=2타일, (473,98)→(473,98,327,200)=4타일, (9,294)=4타일 — 전체 프레임 Scale2x 기준과 동일.
- 검사: `test_g1_rect_fill`·`test_g1_overlay_blt`·`test_g1_mirror2x`·`test_g1_saved_scene_probe` `.venv/bin/python` **288 passed**, `i686-w64-mingw32-gcc -Wall -Wextra -c g1_mirror2x.c` 경고 0, `make lint`·`make typecheck` PASS.

## W-1 실행 (순차, load ≤ 8, run마다 `game` 사본 삭제, 안전 7종 0·cleanup ok·`source_unchanged` true 전부)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1085_work_hw330`(`run_w.sh` `de2f2c88…`·`analyze_hw.py` `8f2f142e…`·`analysis_hw.json` `dfae09d0…`·`analysis_out.txt`), 로그 `logs/gates/lap1085_hw_w{1..8}.log/.exit`·`lap1085_hw_w9.log`. 모두 pair PASS(gate 전부 PASS).

| run | 옵션 | hold 합 | 남은 ord | 마지막40 | `467580`/`467B00` reject_size | mirrored 호출 | p95 elapsed |
|---|---|---|---|---|---|---|---|
| w1 `7cb2db78dba3` | save006 UPLEFT,DOWNRIGHT(= k1) | **2** | ord 137 (799,408..409) 2 px | 0 | 0/0 | 342/612 | 8 |
| w2 `93b88d1f9836` | 동일 | **64** | **ord 124 62 px(x6..26 y13..22)** + ord 137 2 | 0 | 0/0 | 342/611 | 9 |
| w3 `81f39201d284` | save006 UPRIGHT,DOWNLEFT(= k3) | **0** | – | 0 | 0/0 | 16/358 | 8 |
| w4 `939c246abdea` | save006 LEFT,RIGHT edge(= k5/hl3) | **0** | – | 0 | 0/0 | 287/595 | 8 |
| w5 `e5448c346b44` | save006 고정(= hl6) | 총합 **0**, 300..848 **0** | – | 0 | 0/0 | 16/80 | – |
| w6 `cc72a33639ff` | 진단: w1 + `--layer-drift --screen-watch --drift-samples "12,17;20,19;16,21" --stale-mask 120-130` | 25 | ord 123 23 px(x5..15 y0..4) + ord 137 2 | 0 | 0/0 | 341/611 | 11 |
| w7 `d6d1d33280f1` | w1 반복 | **2** | ord 137 2 px | 0 | 0/0 | 342/611 | 7 |
| w8 `87e447867997` | 진단: 샘플 `14,17;20,19;10,2` | 530 | ord 122 139 px(x0..31 y0..17)·ord 242 389·ord 296 106(진단 동반)·ord 136 2 | 0 | 0/0 | 341/613 | 11 |
| w9 `857d88a635e3` | 진단: w8 반복 | 74 | ord 123 23·ord 124 49(x5..25 y0..21)·ord 137 2 | 0 | 0/0 | 342/610 | 11 |

- **E-0:** w1·w2·w6~w9 UPLEFT 24칸 (158,101)→(110,101)·DOWNRIGHT 복귀(두 lane 같음), w3 UPRIGHT 24칸 왕복, w4 LEFT,RIGHT 24칸 왕복. **E-1:** hold elapsed p95 7~11(고정+16 이내), tps 19.92~20.04.
- **H-W330 핵심 PASS 근거:** 9 run 모두 `blend_467580_reject_size`·`blend_467B00_reject_size` = 0(수리 전 k1 21/89), k1의 stale 집합 ord 126~133·140~145·221~225 = **전 run 0**(w1·w2·w7 및 진단 run), hold 합 240,703 → w1·w7 **2**(허용 소잔여 ord 137 2 px). 진단 동반 ord 242·296(w8)은 lap1083 k6 진단 전용 잔여와 같은 종류(비진단 w1·w2·w7엔 없음). `mirrored_calls` 감소 없음.
- **w5 부수 효과(§3-3):** 고정 장면 load 과도 stale **총합 291,382(ord 0..15, hl6) → 0**(887 present 전부 0, `blend_467580_reject_size` 16→0). 수리 전 hl6 값은 lap1081 hl6 trace에서 직접 재계산.
- **사전등록 기준 미충족(정직한 기록):** §5 PASS(partial)는 "w1·w2: 남은 것은 ord 137 ≤ 2 px뿐, 그 밖 ord 증가 0"을 요구한다. **w2는 ord 124 62 px로 불충족**이고, 진단 run(w6·w8·w9)에서도 같은 **좌상단 소잔여**가 첫 hold present 부근(ord 122~124, bbox x0..31·y0..21)에 나온다. UPLEFT 계열 post-change 7 run 중 4(w2·w6·w8·w9)에서 발생, w1·w7은 깨끗, 수리 전 k1·k2·k6 UPLEFT 3 run은 이 영역 0. 한두 프레임 일시 잔여(마지막40 0, 이후 ord 0)이며 reject 사각형과 무관(reject 0). 샘플 watch(n_stale_samples 0)는 stale 화소를 잡지 못해 **writer 귀속 UNKNOWN**. 가설: 모서리 키가 포인터를 창 (0,0)으로 옮기는 present의 커서 스프라이트(크기 ≈ 32×18)와 일치하나 미검증. 수리 때문에 생겼는지(수리 전 0/3 vs 후 4/7, Fisher p≈0.2) 판별 불가 → 대조 run 필요.
- 하네스 사고 기록: w8/w9 launcher를 `pkill`로 멈추려다 w9가 이미 시작돼 launcher만 죽고 probe python은 단독 완주했다(`w9.exit` 없음, `pair-result.json`·cleanup `game_removed` true·`source_unchanged` true 확인, `game` 사본 없음). 다른 PID 신호 0, 다른 저장소 프로세스 비접촉.

## 판정

- **H-W330 핵심 효과 PASS**(reject_size 0, 330×200 stale 집합 0, hold 240,703→2, 고정 장면 291,382→0, w3·w4·w5 비회귀 0).
- **사전등록 PASS(partial) 기준은 w2 한 건 때문에 불충족**: 새 좌상단 일시 소잔여(4/7 UPLEFT run). 수용·귀속·대조 설계는 middle 판단. 이 work는 진단 1회(w6) + 반복 2회(w7·w8·w9)까지 했고 귀속은 못 했다(첫 판정 후 "같은 옵션 진단 1회" 규칙 소진 → 추측 반복 금지).
- 안전 위반·크래시·성능 초과 0.

## 남은 위험 / 다음

- 좌상단 소잔여가 이번 수리의 부작용인지 기존 간헐 현상인지 UNKNOWN. 판별 제안(middle 결정): (i) 수리 전 hook(`git`에 없는 파일이므로 현 소스에서 두 hook만 되돌린 대조 빌드 또는 환경 변수 off) UPLEFT 반복 ≥ 5회, (ii) 표본 점을 좌상단 커서 후보 영역에 더 촘촘히(샘플은 정확히 3점) 하거나 DR watch를 stale present 한 장만 덮게 좁히기, (iii) 포인터 위치 로그(모서리 이동 present)와 대조.
- 별개 backlog 유지: ord 137 (799,408..409) 2 px writer, save000 UPLEFT 맵 경계 stale ≈189k(H-D2k-s0 선택 진단은 미실행: 디스크·시간), `rect_fill_466070_reject_size` 7·`rect_solid_465E80_reject_size` 4(수리 전 k1과 동일, 이번 변경과 무관).
- 다음 한 가지(제안): middle 독립 재계산 → 좌상단 소잔여 귀속·대조 설계 사전등록.
