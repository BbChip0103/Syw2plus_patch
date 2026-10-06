# 2026-10-05 | lap995 | G1 middle — H-F2 독립 검수(수용) + H-F3(`0x466B50` 좌우반전 리맵 RLE diff 미러) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / 중간(middle) 1 lap. 게임 코드·source 변경 0, 커밋 0.
- 입력: lap994 work `loop/ESCALATE_SOL`(원문 아래 §원문) — r1·r2·r3 raw 재계산, r2 성능 outlier 판정, source/bridge SHA, H-F3 사전등록.
- 가설(검수 대상): lap993 사전등록 H-F2 — HP 바 잔여 279px은 `0x465B30` 사각형 테두리가 block_copy 뒤에 쓴 것이며, 호출 전후 diff 미러로 제거된다.
- 변경 파일: 이 기록, `docs/STATUS.md`. `loop/ESCALATE_SOL`은 처리 후 삭제(원문은 아래 보존). source/테스트/바이너리 변경 0.
- 원본·후보 SHA / 환경 / fixture: 원본 EXE `b56986e0…08a8ac`(보호, 읽기만). source(현재 working tree, uncommitted) `g1_mirror2x.c` `93ee239c…4978`·`g1_mirror2x.h` `164ab29b…48bd`·`direct_draw_trace.c` `ebe9037e…f07d`·`tests/test_g1_rect_fill.py` `e9708163…a664`·`g1_rect_fill.h` `5c9d47a8…faf` — lap994 기록과 일치, r1·r2·r3·r4 `bridge/` 사본과 `cmp` 동일. fresh save006(비합성) scale2x pair, 격리 runtime/prefix/display, 활성8인 부하 증명 아님.

## 실행 명령 / 산출(공유 temp `20261005_lap995_middle_review/`)

- 독립 재계산: `.venv/bin/python recalc_lap995.py`(새로 작성, numpy+stdlib만, 제품 helper·`analyze_lap994.py` 미사용, SHA `db46232f…054e`) → `recalc_lap995.json`(`ce6d1cf9…2d14`). 입력 lap972 r1·lap992 r1·lap994 r1/r2/r3·lap995 r4.
- 확인 pair r4(코드 변경 없음, 같은 바이너리·같은 명령; r2 성능 outlier 판정용): `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap995_middle_r4 --artifact-root <공유temp>/20261005_lap995_middle_review/r4 --hd-source scale2x --stale-mask 6-12,30-34,300-301,585-620,880` → exit 2(= pair HOLD, V2s raw 기존 gate). 로그 `logs/gates/lap995_middle_r4.log` `4d09c0a7…02a2`, pair-result `32d2122c…489e`, mask `d6cdd703…bc68`, trace `293a6ad0…d843`. 실행 시 load avg 1.9~3.2. runtime에 `game` 사본 없음(manifest·output·prefix만, runner 정리).
- 정적: `disasm_lap995.py`(lap993 스크립트 복사, 보호 EXE SHA assert) `2a0f310e…40e7` → `disasm_466B50.txt` `311083c6…1545`.

## 측정값 / 판정

| run | ps3 present | p50/p95/max ms | >12ms | 4구간 p95 | cov p50 | 자기 steady 교집합 | HP | 유닛 | 안전 max |
|---|---|---|---|---|---|---|---|---|---|
| lap992 r1(기준) | 886 | 5/7/10 | 0 | 7,7,7,7 | 98.535% | 3,545 | 279 | 961 | 0 |
| lap994 r1 | 867 | 5/7/12 | 0 | 7,7,8,7 | 98.593% | 3,290(38덤프) | 0 | 961 | 0 |
| lap994 r2 | **762** | 6/**22**/66 | 161 | **7**,23,25,27 | 98.575% | 3,266(38덤프) | 0 | 961 | 0 |
| lap994 r3 | 889 | 5/8/13 | 1 | 7,7,8,7 | 98.591% | 3,266(39덤프) | 0 | 961 | 0 |
| **lap995 r4** | **886** | 5/**7**/11 | 0 | 7,7,7,6 | 98.600% | **3,266**(39덤프) | **0** | 961 | 0 |

- **F2-1 PASS(4/4)**: HP 영역 279→0. lap992 r1 대비 공통 덤프(r1·r2 38개 300~620, r3·r4 39개 300~880) 제거 279가 전부 HP 안쪽(r2만 HP 밖 24 추가 제거 = HUD 상자 12 + 기타 12, 증가 아님).
- **F2-2 PASS(4/4)**: 신규 stale 0(전체·HP 밖). r3·r4 교집합 3,545→**3,266**(=−279 정확). 5개 run 공통 38덤프에서도 lap994/995 신규 0.
- **F2-3 PASS**: `rect_border_465B30_invocations` r1 31,830·r2 26,973·r3 31,751·r4 31,868, mirrored_calls 31,288/26,431/31,193/31,310, mirrored_pixels 272,801/231,017/272,061/273,120, reject target·size·guard 전부 0. work 주장 수치와 일치.
- **F2-4 PASS(partial)**: 안전 7종(clip_replay·viewport mutation/restore·palette·mask outside·cache_clip_verify·identity_key) max 0 4/4, Scale2x/V2/V2q/input/minimap PASS 4/4, V2s FAIL(raw 기존 gate, 사용자 판단 큐) 4/4. 성능 r1·r3·r4 PASS, r2 FAIL.
  - **r2 판정 = 환경 변동(hook 비용 결함 아님)**. 근거 3개: (a) `elapsed_ms`는 present hook 안의 mirror 처리 시간(`g1_mirror2x.c:911`→`:1055`)이고 `0x465B30` wrapper(`:2329`)는 게임 그리기 중 호출 시점에 실행되므로 이 값에 들어가지 않는다; (b) r2의 첫 1/4 구간 p95는 7ms로 r1·r3와 같고 초과 161개가 present 142 이후 구간에 몰려 있다(hook 비용이면 전 구간 균일); r2는 present 간격 p95도 125ms(r1·r3·r4 53ms)라 프레임 진행 자체가 막혔다; (c) 같은 바이너리·명령의 r4가 present 886·p95 7ms로 r1·r3를 재현. 외부 부하의 정확한 출처는 입증하지 않았다(정황: work 기록의 다른 저장소 루프·chrome 동시 가동).
- **H-F2 판정: PASS(partial) 수용.** 제품 마감 아님. 한계(H-T/H-F와 동일): 바뀐 픽셀만 HD 갱신. census는 `0x465B30`을 같이 hook하므로 계속 `--census-only`로만.
- 잔여(r3·r4 교집합 3,266): 유닛 덩어리 961(`0x466B50`), P6 로고 2,102(명시 잔여, 가장자리 영역 813과 일부 겹침), V2s는 r3·r4 모두 production tag만 FAIL(loaded·selection·drag·minimap PASS, 기존 gate HOLD; raw 수치 재집계는 이번 범위 밖).

## H-F3 사전등록(다음 work, Sonnet)

- 근거: lap974 census(유닛 픽셀 (701,237) hook 밖 EIP `0x466BB3` 63/126 = 50%, 소속 `0x466B50`), lap975 middle 정정(`ret 0x18`), 이번 lap 재역어셈블(`disasm_466B50.txt`): `0x466B50` thiscall, 인자 x·y·width·height·RLE·LUT(6개, `ret 0x18` at `0x466BD4`), **클립 없음**, 대상 `[x, x+width) × [y, y+height)`(base `[ecx+0x1514]` + y·`[ecx+0x10]` + x), 각 행 오른쪽→왼쪽, `0xFE`=건너뛰기. prologue 8B `51 53 56 57 8B 7C 24 18`(명령 경계 1+1+1+1+4, 상대 분기 없음, 5바이트는 명령 중간이라 8바이트 steal). census hook 목록(`g1_census.c:1305~1311`)과 mirror hook 목록에 없음 → 주소 겹침 없음.
- 구현(최소 변경, H-F2 패턴 복사): `g1_mirror2x.c`에 hook `0x466B50`(old bytes 검증 후 8바이트 steal)+wrapper `mirror_flip_rle(renderer, x, y, w, h, src, lut)`: guard면 reject_guard, 대상 버퍼 검사(H-F2와 동일 조건)면 reject_target, `w==0||h==0||x<0||y<0||x+w>800||y+h>600||w*h>before 버퍼`면 reject_size(원본은 항상 그대로 호출), 통과 시 사각형 사본 → 원본 → `g1_overlay_blt_apply` diff 미러. 계수 `flip_rle_466B50_{invocations,mirrored_calls,mirrored_pixels,reject_target,reject_size,reject_guard}`를 `g1_mirror2x.h` accessor·`direct_draw_trace.c` 요약에 추가, install/detach/installed 목록 갱신. 클립 함수가 아니므로 viewport 교집합을 쓰지 않는다(`g1_rect_fill_region` 대신 화면 경계 검사). 테스트(RED→GREEN): hook 주소·old bytes·`ret 0x18` 인자 수, 화면 밖 사각형 reject.
- 실행: fresh save006 scale2x pair 3회(위 r4와 같은 명령, runtime `local/runtime/lap996_flip_rle_r{1,2,3}`), 기준 = lap995 r4(교집합 3,266, 39덤프)·lap994 r3.
- PASS: **F3-1** 유닛 영역(`y 215..254 × x 681..723`) 961→**≤96**(3회 모두); **F3-2** 기준 대비 신규 stale 0(전체·유닛 밖), 교집합 = 3,266 − 유닛 감소분; **F3-3** invocations>0·mirrored_calls>0·reject 3종 보고; **F3-4** 안전 7종 0·present≥850·p95≤12ms·cov p50≥98.4%·Scale2x/V2/V2q/input/minimap PASS(V2s raw는 기록만). 성능이 1회만 갈리면 이번 lap처럼 같은 명령 1회를 추가하고 구간 p95·present 간격으로 판정한다.
- 반증: (i) invocations>0·mirrored_calls>0인데 유닛 >865(감소 <10%) → 덩어리 대부분이 다른 writer(유력: 클립판 좌우반전 리맵 RLE `0x466BE0`, `ret 0x18` at `0x466D40`, prologue `83 EC 18 33 C0` 5바이트 경계 정확, 쓰기 `0x466D11`, 미hook) → census 재지목 후 H-F4; (ii) 화면 대상 호출 0 → 호출 경로 오인(`0x419F50`·`0x41A4FA` 재확인); (iii) 안전>0·크래시·유닛 밖 신규 stale·재현되는 p95>12ms → FAIL, 원복.
- 부분 결과(감소했지만 >96): 잔여 픽셀의 census를 `--census-only`로 1회 돌려 `0x466BE0` 여부를 확정하고 H-F4로 넘긴다.

## 회귀 / 남은 위험 / 상태

- 제품 회귀 0(4 run 신규 stale 0·안전 0). 독립 검수 수용은 사용자 승인 아님. G1 pair HOLD 사유(V2s raw)·D-2·P6/P7·두 번째 장면·사용자 승인은 그대로.
- G6/G7은 APPROVALS lap989 사용자 합격 대기(비차단). lap991 H-G6f probe-result 독립 재계산은 아직 middle 몫으로 남는다.
- 다음 한 가지: **work(Sonnet) H-F3** — 위 사전등록대로 `0x466B50` diff 미러 구현·pair 3회.

## 원문: lap994 `loop/ESCALATE_SOL`(처리 후 삭제)

```
lap994 work(Claude Code claude-sonnet-5-5) → middle(Opus) 독립 검수 요청: G1 H-F2 구현·실행 완료, 판정은 middle 몫.
기록: docs/history/laps/20261005_lap994_work_g1_rect_border_diff_mirror_hf2.md (uncommitted)
결과: hook 0x465B30(8B 83 EC 10 53 8B 5C 24 18) 사각형 테두리 diff 미러. fresh save006 scale2x pair 3회(공유 temp 20261005_lap994_work_rect_border/r1,r2,r3):
 F2-1 HP 279→0 (3/3), F2-2 신규 stale 0 (r3 교집합 3,545→3,266 = HP 감소분 279), F2-3 테두리 호출 31.8k/27.0k·reject 0.
 F2-4 r1(present 867·p95 7ms)·r3(889·8ms) PASS, r2 FAIL(present 762·p95 22ms; 외부 루프/chrome 동시 부하 정황, 입증 아님). 안전 0·V1/V2/V2q/Scale2x/minimap PASS, V2s raw 기존 gate HOLD.
middle이 확인할 것:
 1) r1·r2·r3 raw(mask/trace/pair-result)를 제품 helper 없이 재계산(analyze_lap994.py·recalc_lap994.json 대조) — HP 0·신규 0·계수·안전.
 2) r2 성능 outlier 판정(환경 변동 vs hook 비용). 필요하면 동일 pair 1회 추가를 work에 지시. F2-4를 PASS(partial)로 수용할지 결정.
 3) source SHA(g1_mirror2x.c 93ee239c…, .h 164ab29b…, direct_draw_trace.c ebe9037e…, tests/test_g1_rect_fill.py e9708163…)·bridge 사본 일치.
 4) 수용 시 다음 work H-F3: 유닛 덩어리 961(0x466B50, ret 0x18 6인자) 사전등록.
```
