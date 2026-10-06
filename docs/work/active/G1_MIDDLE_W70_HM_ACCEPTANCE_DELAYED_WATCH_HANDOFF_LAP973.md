# G1 middle lap973 — lap972 H-M 수용 · r2 +24 = 덤프 시점 차이 · 다음 work = 지연 census watch(H-W)

- 작성: Claude Code `claude-opus-5-5`, high, Fast OFF / middle(중간계획·독립 검수). 게임/source/실행/commit 0.
- 입력(읽기 전용): 공유 temp `20261005_lap972_work_minimap_settle/{r1,r2}`, 비교 기준 `20261005_lap969_work_tooltip_bltfast/{r1,r2}`.
- 산출(공유 temp `20261005_lap973_middle_review/`, 제품·lap972 분석 helper import 없음): `recalc_lap973.py` SHA256 `be897a467d86d9efa92a39d37119fd791bec27e813ee31bdeac49208bd24dc55` → `recalc_lap973.json` `e6720831799b0a0f66939f88342118fa45f543ce4ec02222ec5713558cb32939`; minimap lane 비교 `minimap_lanes_lap973.txt` `0bf0e683…099b`; 원본/후보/stale 크롭 `unit_hp_crops_lap973.png` `bf2a82e3…b9c9`.

## 1. 독립 재계산 (lap972 주장 대비 불일치 0)

| 항목 | lap969 r1 | lap969 r2 | lap972 r1 | lap972 r2 |
|---|---|---|---|---|
| 덤프 / steady / 880 덤프 | 51 / 39 / 있음 | 51 / 39 / 있음 | 51 / 39 / 있음 | **50 / 38 / 없음** |
| PS3 present / 마지막 덤프 서수 | 899 / 880 | 891 / 880 | 897 / 880 | **876 / 620** |
| steady 교집합 (자기 덤프 전부) | 3,689 | 3,689 | 3,689 | 3,713 |
| HUD 상자 / 유닛 / HP / 가장자리 | 0/961/423/813 | 같음 | 같음 | 12/961/423/813 |
| **공통 38 덤프(300·301·585~620) 교집합** | **3,713** | **3,713** | **3,713** | **3,713** |
| 공통 38 덤프 기준 lap972 r2와 픽셀 동일 | True | True | True | True |
| p50 / p95 ms, cov p50 | 5/9, 98.51% | 5/10, 98.49% | 5/9, 98.50% | 5/9, 98.49% |
| 안전 최대 7종 | 0 | 0 | 0 | 0 |
| V1/V2/V2q/input | PASS | PASS | PASS | PASS |
| minimap parity / V2s / pair | HOLD/FAIL/HOLD | HOLD/FAIL/HOLD | **PASS**/FAIL/HOLD | **PASS**/FAIL/HOLD |

- 파일 SHA(mask/trace/pair)는 lap972 기록 prefix와 일치(r1 pair `1b62c562…25a9`, r2 pair `8cae2674…3c`). 하네스 source `tools/g1_saved_scene_probe.py` `883ee52c…f044`, `tests/test_g1_saved_scene_probe.py` `aff0aad5…bab`도 기록과 일치(uncommitted).

## 2. 판정

- **M-2 r2 +24 = 덤프 시점 차이(비회귀).** r2는 PS3 present가 876개라 서수 880 덤프가 만들어지지 않았다. 공통 38 덤프로 맞추면 네 run(lap969 r1·r2, lap972 r1·r2) 교집합이 모두 3,713으로 **픽셀 동일**하다. r2에만 있는 24px(bbox x616~619·y515~520, 4×6, 그중 HUD 상자 안 12px)은 r1에서 **880 덤프에서만** 지워지는 픽셀이다(`r2_extra_cleared_only_at_880_in_r1`=True), r2에서 사라진 픽셀 0. H-T 회귀 아님 → 반증 (iii) 해당 없음, r3 불필요.
- **M-1 PASS 수용.** r1·r2 모두 4 lane wait PASS(samples 2, 0.157~0.161s), `unit_after` 4유닛 전원 command 3·pending 16777217·pending_xy 5767258/5767259/5832794/5963864·x,y 불변, lane 간 완전 동일, camera [158,101] 동일. 반증 (i)(ii) 해당 없음.
- **H-M PASS 수용(하네스).** 제품 source·validator·비교식 불변. 사용자 마일스톤 승인 아님. pair HOLD는 V2s raw production FAIL(기존 사용자 판단 큐) 하나만 남는다.
- 기록 한계: stale-mask 일정의 880 덤프는 present 수(876~899) 경계에 걸려 있어 run마다 빠질 수 있다. 이후 교집합 비교는 **공통 덤프 집합**으로 하고, 덤프 누락은 결과에 명시한다(일정·validator 변경 없음).

## 3. 다음 후보 근거 — census 분류는 이 두 덩어리에 유효하지 않다

- per-dump stale: 유닛 덩어리(x681~723·y215~254)와 HP 바(x401~494·y153~159)는 서수 6~34 덤프에서 **0px**, 300부터 997~1,020 / 423(고정)이다. 입력 trace로 보면 서수 34 직후 drag 종료, 그 뒤 minimap 우클릭·minimap 이동·HQ 선택(450,195)·생산 버튼(668,540)이 이어진다. HP 바는 **HQ 선택 뒤 나타나는 선택 HP 바**(크롭에서 HQ 위 녹색 칸 바), 유닛 덩어리는 카메라 이동 뒤 화면 안의 수레 유닛 한 개다(크롭 확인, 원본/후보 모두 내용 정상·후보는 nearest).
- census는 첫 PS3 present부터 **64개만** 기록한다(`g1_census.c` `CENSUS_PRESENT_LIMIT 64u`, 서수 64 ≈ HQ 선택 0.4s 전). lap968의 "terrain 833·rle_tinted_clip 128 / rect_border 67·…" 분류는 **다른 run(lap951 r6)의 64 present 창 지도**로 근사한 것이라 두 덩어리가 생기기 전 값이다. 따라서 이 두 덩어리의 writer는 **미확인**이며, 기존 `--census-watch`도 같은 64 창이라 잡을 수 없다.
- mirror hook 대상(`g1_mirror2x.c`): rle_clip·rle_plain·panel RLE·tinted RLE·tinted clip RLE·cache copy·terrain 5개. census 표에 있는 rect_fill `0x465E80`·rect_border `0x465B30`·set_pixel `0x4658E0`은 mirror가 다루지 않는다(HP 바 후보). census lane은 같은 action 7개를 수행한다(lap953 w2 probe-result `actions` 7개 PASS).

## 4. 다음 work 가설 H-W (Sonnet work 1 lap, FEASIBLE — 진단 하네스 + fresh census 실행)

- 변경(진단 opt-in만, 기본 동작 byte-동일, 제품 mirror·validator·gate 불변): `g1_census.c`에 `SYW2_G1_CENSUS_SKIP_PRESENTS=N`(기본 0) — 대상 state의 처음 N개 present는 세기만 하고 map/residual/watch 창 시작을 N 뒤로 미룬다(64 창 길이 유지). probe `--census-skip-presents N`(`--census-only` 필수). 기록 서수(`g_present_sequence`)는 실제 PS3 서수로 남겨 stale-mask 서수와 대조 가능하게 한다.
- 회귀 테스트(먼저 작성): env 없음 = 기존 경로(skip 0) 정적 계약, N>0이면 N 이전 present에서 map/watch 미기록, probe 옵션 검증(`--census-only` 없으면 parser error).
- 실행: `--census-only --census-residual --census-skip-presents 300 --census-watch 442,155`(HP 바) 1회, `--census-watch 701,237`(유닛 덩어리) 1회. 두 픽셀 모두 lap969 r1·lap972 r1·r2 교집합 안. 끝나면 `game` 사본만 정리.
- PASS(사전등록): 두 run 모두 `watch_armed` present ≥301·selftest PASS, 각 픽셀 hit ≥1이고 hook 밖(`in_hook`=0) EIP가 창 안에서 반복(같은 EIP가 ≥50% hit)되면 그 EIP와 함수 entry(스택 `.text` 주소)를 `analysis/memory_maps/`에 기록. 또는 hit 전부가 census 표의 mirror 미대상 writer(rect_border/rect_fill/set_pixel) 안이면 그 writer를 기록한다. 둘 다 "다음 수리 대상 확정"으로 친다.
- FAIL/반증: (i) arm 뒤 hit 0 → 그 픽셀은 창 안에서 다시 쓰이지 않음 = 쓰기 누락이 아니라 mirror 쪽 보존/무효화 문제 → middle이 stale 정의 재검토. (ii) hit가 전부 mirror 대상 writer(rle_*·tinted·terrain·cache copy) 안 → mirror 경로 내부 결함, 해당 writer의 bind 조건 조사로 넘김. (iii) census lane에 HQ 선택 action이 없거나 실패 → BLOCKED(fixture/action 정렬), 기준 완화 금지.
- 위험: present 300 이후 present 간격·스크롤 차이로 픽셀이 다른 개체를 가리킬 수 있다 → hit EIP와 함께 그 present의 census map 해당 픽셀 class를 같이 남긴다. HP 바는 고정 423px이라 위험이 낮고, 유닛은 애니메이션이라 한 개 픽셀 결과를 덩어리 전체로 일반화하지 않는다.

## 5. 그 뒤

- writer가 확정되면 다음 work는 H-T와 같은 "호출 전후 대상 사각형 비교 → 바뀐 픽셀만 Scale2x 미러" 방식을 그 writer에 적용(사전등록은 다음 middle이 정함). P6 로고 2,102는 명시 잔여 유지. strategy 재호출 조건 추가 없음.
