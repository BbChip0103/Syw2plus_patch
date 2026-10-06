# 2026-10-06 | lap1077 | G1 H-LB (`0x465B30` reject 귀속 + 화면 클램프 타일 미러)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 승인·수용 판정은 하지 않는다(독립 검수는 다음 middle).
- 가설: lap1076 §5 — save006 좌우 edge ord 226 3 px(x799 y48..50)는 `mirror_rect_border`가 reject한 호출이며 원인은 renderer 클립이 stride 패딩(x≥800)까지 열려 x+폭>800이 되는 것이다. 영역을 화면 [0,800)×[0,600)와 교차하고 타일로 미러하면 사라진다.
- 예상 PASS / FAIL: lap1076 §5(B-0 reject 인자·클립 공개 / B-1 좌우 hold 합 0·`rect_border_465B30_reject_size` 34→0·마지막40 0·`line_4659B0` 계수 동일 / 비회귀 E-0·p95·pair·안전·UP/DOWN·키 hold 0·save000 gate 동일·save006 고정 300..848 0). FAIL = 크래시·안전 위반·원본 이중 호출·기존 경로 회귀.
- 변경 파일 / source fingerprint / 커밋: uncommitted. `tools/inmm_stub/g1_rect_fill.h`(`g1_rect_screen_region`) `8443b983f8d0…`, `tools/inmm_stub/g1_mirror2x.c`(`mirror_rect_border` 전환·`g_rect_border_tile`·`g_rect_border_before` 800×600·`rect_border_reject_log` type `g`·`g_rect_border_reject_logged`) `59ad70caeca3…`, `tests/test_g1_rect_fill.py`(새 테스트 1·기존 rect_border 계약 갱신) `cb7fb89a3166…`. 하네스·bridge(`direct_draw_trace.c`)·기타 불변(계수 6개는 기존 그대로).
- 원본 SHA / 환경 / fixture: 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac`(읽기만, 각 run `source_unchanged` true). 비합성 save006·save000. scale2x HD, load 3.5~7.2(≤8)·run마다 대기 0 s, 순차. 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1077_work_hlb`, 로그 `logs/gates/lap1077_lb_lb{1..7}.{log,exit}`, game 사본 run 뒤 삭제.

## B-0 진단 (수리 전 코드 + env-gated 로그, run lb7 = lap1075 ln7 옵션)

`mirror_rect_border` size-reject 시 `{"t":"g",...}`(원 인자·색·클립·stride·결과 영역) 최대 64줄. lb7: **34줄 = `rect_border_465B30_reject_size` 34**, 전부 present p225(ps3 ord 226), 클립 **[0,0,831,511]**·stride 832. reject 사각형: (800..830, y39..48)을 3 px 간격으로 자른 4×4(·끝 2×4) 조각 33개 — 전부 x≥800(패딩 전용) — 와 마지막 1개 **(799,48)–(850,50) 영역 x799 y48 폭33 높이3**(색 246) = ord 226 stale (799,48..50)을 덮는다. **가설 확인**: 클립 xmax=831이 패딩까지 열려 있고 비타일 `g1_overlay_blt_accepts`(x+폭≤800)가 거부한다. reject 33개는 화면 밖(패딩만)이라 미러할 픽셀 0.

## B-1 테스트 먼저(RED→GREEN)·구현

- RED: `test_rect_screen_region_intersects_clip_with_visible_screen`(`g1_rect_screen_region` 없음 → gcc 실패)·`test_rect_border_hook_table_and_wrapper_contract`(갱신: tiled·screen_region·tile 버퍼·로그 type g) 둘 다 FAIL 확인 → 구현 뒤 GREEN. `test_g1_rect_fill`+`mirror2x`+`overlay_blt` **69 passed/0.91s**, `make lint`·`make typecheck` PASS.
- 구현: `g1_rect_screen_region` = `g1_rect_fill_region`에 클립을 [0,screen_w)×[0,screen_h)로 줄여 적용(x799 폭1, 패딩 전용 사각형은 0). `mirror_rect_border`: 영역 = 그 결과, before 버퍼 800×600, `g1_overlay_blt_apply_tiled`(타일 320×160) — `mirror_rect_border7`와 같은 형태. 원본 정확히 1회·좌표/색 하드코딩 0, 계수 6개 이름 불변.

## 실행 결과 (순차)

| run | 구성 | pair-result SHA | hold 창(ps3 ord 123..291) stale 합 | 마지막40 | reject_size / mirrored_calls | p95 fixed/hold · tps 비 |
|---|---|---|---|---|---|---|
| lb1 | save006 LEFT,RIGHT edge(마스크 `123-126,130-146,224-235`) | `88cd4924b1c8` | **0**(ord 226 = 0) | 0 | **0** / 32,014 (px 286,593) | 7/7 · 1.0034 |
| lb2 | save006 LEFT,RIGHT edge(`0-1600/30`) | `442d676d0ec7` | **0** | 0 | **0** / 31,929 | 7/7 · 1.0049 |
| lb3 | save006 UP,DOWN edge | `31f6b448c3a2` | **0**(기준 0) | 0 | 0 | 6/6 · 1.0027 |
| lb4 | save006 키 hold UP,DOWN | `875c524a45b2` | **0**(기준 0) | 0 | 0 | 6/7 · 1.0026 |
| lb5 | save000 DOWN,UP 키 hold(lap1071 e 옵션) | `f407219b9269` | **0** | 0 | 0 / 300 | 7/7 · 1.0035 |
| lb6 | save006 고정 카메라 | `0aacf8a818b6` | — 887 present, 300..848 합 0·최대 0 | 0 | — | — |
| lb7 | B-0 진단(수리 전) | `4446ac950d3b` | — | — | 34 / — | — |

- **B-0 PASS**(34 reject·클립·덮는 reject 공개, 가설 확인). **B-1 PASS**: 좌우 edge 2/2 hold 합 3→**0**·reject_size 34→**0**·마지막40 0·`line_4659B0` invocations 1258·mirrored_calls 286·mirrored_pixels 966·reject 0/0/0(lap1075와 동일). `rect_border_465B30_mirrored_pixels`: 수리 전 283,990(lb7)·후 286,593/285,798(+~0.9%, 새로 미러된 x799 열·화면 교차분; 급증 아님).
- **비회귀**: E-0 lb1~lb4 두 lane 48칸(24+24)·관측열 동일·clamp 없음·최종 (158,101)/save000 (39,53), p95 ≤ 고정+16·tps 비 ≥1.0026, pair PASS(lb1~4·6), 안전 7종 최대 0, cleanup·`source_unchanged` true. lb5 gate = lap1075 ln5와 gate별 동일(status·input_effect HOLD, V2/V2s/V2q BLOCKED, 나머지 PASS; 기존 사유). 부하 변형 제외 run 없음.
- 한계: 좌우 edge는 save006만·결정론 동일값이라 lb1=lb2 통계 독립성 약함; 모서리(대각) 스크롤·H-LD 부하 동반 재현 미착수; `rect_border_reject_log`는 진단 전용(비진단 0); 진단 동반 영역 x301..334·y357..398·`0x467E60` 미귀속은 backlog 그대로.

판정(work 후보): **H-LB PASS** — ord 226 해소(합 0), `0x465B30` reject 34→0. 승인은 middle.

## 검사

`make check`는 기록·인계 freeze 뒤 1회(결과는 STATUS 보강).

## 다음 한 가지

middle(Opus): lap1077 work 독립 재계산(lb1~lb7 pair/mask/trace)·`g1_rect_screen_region`·`mirror_rect_border` 코드 검토·B-0 reject 34줄 재집계 후 수용 판정. 이어 work H-LD(SIGSTOP/SIGCONT 듀티 부하 동반 stale 재현) 또는 모서리 스크롤.
