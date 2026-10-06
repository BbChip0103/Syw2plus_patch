# 2026-10-06 | lap1040 | G1 middle — H-R 독립 검수(R-2·R-4 판정 포함) → work H-S(남은 유닛 크기 stale 덩어리 writer 귀속) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·source 변경·commit 0.
- 검수 대상: lap1039 work H-R(`0x466B50` `mirror_flip_rle` 화면 가장자리 교집합 diff 미러). R-0~R-4 수치가 raw에서 재현되는지 확인하고, R-2 문자 미달과 R-4 p95 9를 판정한다.
- 예상 PASS / FAIL 조건: lap1038 §H-R 사전등록 그대로 쓴다(기준·gate 무변경).
- 처리한 인계: `loop/ESCALATE_SOL`(lap1039 work, 1,800 B, SHA256 `0e87eb1ced6753c072454a86799c650a12fc550e049a28e519bce73dafddda21`). 원문은 아래 부록에 두고, 처리 뒤 삭제했다.
- 변경 파일: 이 기록, `docs/STATUS.md`. source/test 변경 0.
- 검수한 source(현재 = run bridge 사본, `cmp` 일치 w r1·s0 r2·s6 r2): `g1_mirror2x.c` `4c4a41529d76ae1b`, `g1_rect_fill.h` `dbd3e2f8c2188c0d`, `direct_draw_trace.c` `b8fa55a2a95d151b`, `g1_mirror2x.h` `8521fc27e9d475b6`, `test_g1_rect_fill.py` `22605564777c93b4`(sha256 앞 16자, work 기록과 일치). 대조 `r_ctl_r1` bridge `13c486cb…`는 현재 source와 정확히 3줄 다르다(세 wrapper 첫 반환 `/* CONTROL-TEMP */`). 현재 source의 `CONTROL-TEMP`는 0건이고, restore 기록 2회 모두 product sha 일치·0건이다.
- 원본 SHA / 환경 / fixture: 원본 EXE `b56986e0…8ac`(전 run baseline·candidate private EXE 앞 16자 일치), save000(index 1)·save006, 격리 prefix/display.
- 재계산(공유 temp `20261006_lap1040_middle_review/`): `recalc_lap1040.py` `05fe036c…25cc` → `recalc_lap1040.json` `e8756f0e…48fc1`, diff `diff_g1_mirror2x_lap1037_to_now.txt` `383625f5…7f75`.
  - `analyze_r_*.py`·`isect_r.py`·제품 helper를 쓰지 않았다. lap1038 middle 재계산 코드(middle 소유)를 바탕으로 `flip_rle_466B50` 항등식·신규 계수, 466B50 `w` 레코드 기하, 덤프 프레임별 "새 stale ∖ 기준 두 run 합집합", 연결 성분, 무효 launch 분리 검사를 더했다.
  - 입력: lap1039 r_w r1/r2·r_s0 r1/r2·r_ctl r1/r2·r_s6 r1/r2. 기준: lap1037 q_w r1/r2·q_s0 r1/r2·q_ctl_r1·q_s6 r1/r2.

## 재계산 결과(판정 불일치 0, 전사 정정 2건)

| 항목 | 기준(lap1037) | lap1039 work 보고 | lap1040 재계산 |
|---|---|---|---|
| R-0 항등식 `flip_rle_466B50` | 783=707+76 등 | 전 run 성립 | 성립 8/8: w 781=770+bounds 11, 778=767+11, s0 780=769+11 ×2, 대조 0=0 ×2, s6 945=945·950=950. target/size/guard 0. `blend_4678C0`·`blend_467FD0` 항등식도 전 run 성립 |
| R-0 안전 7종·cleanup·source_unchanged·scene·camera·units | — | 0/true/true/true | 동일. camera (39,53), units 375(save006 558), tick delta 400 전 run. trace JSONL 손상 0 |
| R-0 관측 | — | clipped 65·wrap 0·bounds 11 | 동일(w·s0 4 run). save006 clipped/bounds/wrap 0 |
| 466B50 `w` 레코드 | — | 42/41건, clipped 36/35·mirrored 6 | 동일. 최다 기하 `clipped 789,306 26×25` 21회, 80×80 @x=688..752. **x+w 최대 832 = stride**, 음수·넘김 0 |
| **R-1** `reject_size` | 76/75 | 0 | **0**(전 run) |
| **R-1** 표본 B / C stale present | 4 / 22 (`0x466BB3` 4 / 21+`0x467CCF` 1) | 0 / 0 | **0 / 0**. 무장 52·fail 0·좌표 3/3·selftest PASS·dropped/overflow 0. A 1(`0x46884E`) 불변 |
| **R-2** 마지막40 중앙값 | 26/26 | 26/26 | **26/26**, s0 26/26, 대조 596/624.5 |
| **R-2** w r1∩r2 39덤프 합 | 2,064 | 2,776 | **2,776**(기준 2,064 재현) |
| R-3 성능(히스토그램 재구성, nearest-rank) | — | 후보 7/7, 대조 9/13 | 후보 p95 **7/7**(≤7 개수 384/381, 필요 380, 평균 5.18/5.28), 대조 9/13(평균 5.66/6.67), ticks 비 1.000003/1.000008 |
| R-4 save006 r1∩r2 | 38프레임 0 | 38/39프레임 0·신규 0 | 38프레임 0·신규 0·제거 0. 공통 덤프 50(r1에 880 없음 → 39프레임 아님, 아래 정정) |
| R-4 save006 p95(present 경과, nearest-rank) | 8/8 | 9/7 | **9/7** |
| `mirror_details[6600]` 최악 | — | ≈6,276 | 최장 metrics 줄 5,151자 + uint 149개 10자리 +1,116 = **6,267** < 6,600. `flip_rle_details[400]` 최악 382+NUL |

**전사 정정 1 — load:** loadavg 파일 기준으로 w r1 7.66·w r2 5.24, s0 3.09/4.04, **대조 4.37/3.96**, **save006 4.98/5.30**이다. work 기록의 "대조 4.98·5.30", "save006 r1 시작 load 7.66"은 파일을 잘못 짝지은 것이다(7.66은 w r1). 판정에는 아래처럼 반영했다.

**전사 정정 2 — "프레임별 신규 stale 0":** 새 run 한쪽 기준으로 보면 w r1은 0이지만 **w r2는 p338에 281 px**가 기준 두 run 어디에도 없다. 이것은 팝업 상자가 한 덤프 더 남은 것이다(같은 값 281이 p318·p328 팝업 상자에 있고, s0 r1∩r2·기준 qs0 r1∩r2·대조에도 p338 팝업이 있다). lap1031 판정과 같은 팝업 run 변동이다. **두 새 run의 공통(r1∩r2) 중 기준 합집합 밖은 0**이다. work가 직접 확인한 4프레임(234·294·366·399)은 맞다.

**save006 r1 꼬리:** s6 r1은 present 880개로 짧고, p779..879에 stale 최대 1,805가 남았다(마지막40 1,181). lap1035 p_s6_r1(879개·p779..878 최대 1,690)과 같은 짧은 run 변형이며 backlog "save006 짧은 run 꼬리"에 해당한다. s6에서 466B50 호출은 전부 화면 안(clipped/bounds 0)이라 H-R 경로 변화는 없다. 880 덤프가 r1에 없어서 r1∩r2는 38프레임까지만 판정된다. work 기록의 "39프레임 0"은 "38프레임 0(880 부재)"으로 정정한다.

## R-2 판정

- 가설 지표는 충족했다. 표본 B·C가 0이 됐고 reject_size도 0이다.
- 화면 집계 효과는 작다. 덤프 프레임별로 기준 r1∩r2에서 빠진 것은 p26·p44·p71의 29 px ×3과 p308의 34 px뿐이다. 마지막40 present의 stale 계열은 w r1과 기준 qw r2가 사실상 같다(0 ×16 → 26·28·37·40·40·40·35·26·37·83·154 → 145 ×9 → 125 → 0 ×3, 기준만 앞쪽에 5 ×2). 0이 19개뿐이라 중앙값(20·21번째)은 **오른쪽 가장자리 덩어리**(덤프 p388에서 y468..473×x791..799, 26 px)의 첫 값 26이 정한다. 그 뒤 145는 p399 덩어리(y214..226×x780..793)다. 이 두 덩어리는 H-R 뒤에도 그대로라 466B50 거부 경로가 원인이 아니다. 둘 중 하나라도 줄이면 중앙값이 내려간다.
- **r1∩r2 합은 판정 지표로 불안정하다.** 어떤 run을 짝짓는지에 따라 1,943~3,292로 흔들린다: w r1∩기준 qw r1 = **2,776**(= w r1∩r2와 같음), w r2∩qw r2 = 1,943, w r1∩qw r2 = 2,547, w r2∩qw r1 = 3,292. 기준 2,064가 낮았던 것은 qw r2의 run 변동(p234 402·p294 111·p298 736 등) 때문이다. 새 run 둘은 서로, 그리고 qw r1과 같은 값을 낸다.
- **판정: R-2는 문자 기준 FAIL로 기록한다(PASS로 바꾸지 않음).** 다만 회귀는 아니다. 두 새 run의 공통 stale 중 기준 합집합 밖은 0이고, 기준 공통 stale 중 4프레임 121 px가 제거됐다. 그래서 H-R 수용을 막지 않는다. 남은 집계 목표(마지막40 26 이하)는 다음 가설로 넘긴다.
- 측정 방법 보강(gate 완화 아님): 앞으로 덤프 교집합 비교는 "새 r1∩r2 ∖ 기준 r1∪r2 = 0(신규)"과 "기준 r1∩r2 ∖ 새 r1∪r2(제거)"를 같이 적는다. 합계 비교만으로 결론 내지 않는다.

## R-4 p95 판정

- 문자 기준(≤8)으로는 r1이 9라 미달이다. **환경·run 변동(UNKNOWN-환경)으로 보고 비차단 처리한다.**
  1. s6에서 H-R 경로는 바뀌지 않았다. 466B50 호출 945/950이 전부 화면 안이라 교집합 = 원 사각형이다.
  2. 같은 바이너리의 r2는 p95 7(평균 5.20)이다.
  3. r1은 위 짧은 run 변형이다(평균 5.67). lap1020~1037의 s6 run 19개 p95는 7~8이었고, 이상치 v2_s6_r2(50)도 있었다.
- 시작 load는 4.98이다(7.66 아님). 따라서 "고부하 때문"이라는 work 설명은 쓰지 않는다.

## 코드 검수

- diff(lap1037 product → 현재)는 `mirror_flip_rle` 재작성, 계수 3개 선언·accessor·reset뿐이다. 다른 wrapper는 바뀌지 않았다.
- 원 인자 6개(`a_x..a_h, rle, lut`)를 그대로 1회 전달한다. x/y/w/h는 `(int32_t)`로 해석하고 `g1_flip_rle_region`이 int64로 합한다.
- `wrap` 계측은 `inside` 판정 **앞**에서 센다. 그래서 reject_bounds 호출의 넘김도 잡힌다(lap1038 범위 정정 반영). 조건은 `x<0 || x+w>stride || y<0 || y+h>600`이다. x+w ∈ (800, 832]은 padding 쓰기라 wrap이 아니다. 이것은 원본 기하와 맞는다.
- before 복사·`g1_overlay_blt_apply`는 교집합 좌표만 쓴다. 버퍼 `g_flip_rle_before[320×160]`과 교집합 크기 검사가 짝이 맞는다. `region`은 `active`일 때만 읽는다.
- 알려진 한계(비차단): wrap 호출이 생기면 다음 행 화면 픽셀은 원본이 쓰지만 미러되지 않는다. 이 장면에서 wrap은 0이므로 관측된 결함은 아니다. 잘린 뒤 apply가 실패하면 `clipped_calls`와 `reject_size`가 둘 다 오르지만, clipped는 관측 계수라 항등식과 무관하다(이번 run에서 apply 실패 0).
- 테스트 `test_flip_rle_region_intersects_screen_like_unclipped_original`(경계 801/832/833·음수·16비트 아님·INT32_MAX)와 wrapper 계약 테스트가 위 계약을 고정한다. 결함은 없다.
- 절차: 구현이 테스트보다 먼저였다(work 자진 기록). 경계 테스트는 GREEN이고 계약을 고정하므로 재작업은 요구하지 않는다.

## 무효 launch 분리

- `invalid_concurrent_launch/` 파일 16개와 유효 run 파일 24개(`trace_raw`·`stale_mask`·`pair-result`) 사이에 공통 해시가 0이다. pair-result mtime도 무효 run 쪽(…4654~4815)이 유효 run 전체(…4945~5910)보다 앞선다. **수치 혼입은 없다.**

## 판정

**H-R PASS(partial) 수용.** R-0·R-1·R-3 PASS, R-4 stale PASS(38프레임 0·신규 0), R-4 p95는 UNKNOWN-환경(비차단), **R-2는 문자 FAIL로 기록하되 신규 stale 0이라 수용을 막지 않는다.** 전사 정정 2건(load 짝, 신규 stale 범위)과 save006 39→38프레임 정정이 있다. 기술 부분수용이며 G1 마일스톤 승인이 아니다.

## 다음 work H-S 사전등록(Sonnet work 1 lap, 진단 전용 — 제품 동작 불변)

목표: 8 run(기준 포함)에서 같은 덤프 프레임에 결정적으로 재현되는 유닛 크기(약 13×14) stale 덩어리와 p388 가장자리 26 px의 마지막 writer를 귀속한다. 마지막40 중앙값 26은 p388 가장자리 덩어리가 정하고, 그 뒤 145 구간은 p399 덩어리다(위 R-2 판정).

### 표본(lap1040 재계산: 아래 점은 lap1039 w/s0 4 run과 lap1037 qw/qs0 4 run의 해당 덤프에서 stale)
- 세트 S1: `--drift-samples "795,470;628,409;599,367"` — p388 가장자리(8/8), p6 덩어리(8/8), p12 덩어리(8/8).
- 세트 S2: `--drift-samples "779,467;718,452;788,391"` — p144(8/8), p174(8/8), p204 가장자리(8/8).
- 세트 S3: `--drift-samples "786,220;783,377;568,483"` — p399(7/8), p366(7/8), p6 둘째 덩어리(8/8).

### 실행(순차, 각 run 직전 `/proc/loadavg` 기록, 1분 load >8이면 대기)
- 세트마다 save000 watch pair 2회(총 6 run). 인자는 lap1039 `run_r.sh` w와 같고 `--drift-samples`만 바꾼다(`--layer-drift --screen-watch --stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`).
- 제품 source 변경은 0이다. run 뒤 `game` 사본만 삭제한다. 스크립트는 단일 인스턴스로 띄우고 pid 파일로 확인한다(lap1039 이중 기동 재발 방지: 띄우기 전에 `pgrep -f run_s.sh` 결과가 비어 있는지 본다).

### PASS / FAIL
- **S-0**: 전 run selftest PASS, 무장 fail 0, 좌표 3/3, dropped/overflow 0, 안전 7종 0, 항등식(`flip_rle_466B50`·`blend_4678C0`·`blend_467FD0`) 성립. 마지막40 중앙값 26이 재현되어야 한다(동작 불변 확인).
- **S-1(귀속)**: 표본 9점 중 해당 덤프 프레임에서 stale인 점마다 stale present 마지막 writer EIP와 값 일치율을 낸다. 점마다 2 run에서 같은 EIP여야 `귀속`이다. 귀속된 점이 6/9 이상이면 PASS다.
- **S-2(분류)**: 귀속 EIP마다 기후킹(`0x466B50`·`0x467B00`·`0x4678C0`·`0x467FD0`·`0x465E80`·`0x466070`·`0x465B30`·`0x4672E0`·`0x467580` 등)인지 미후킹인지 나눈다. 기후킹이면 해당 계수(reject_*)와 `w` 레코드 기하로 거부 이유를 적는다. 미후킹이면 함수 시작 주소·인자 수·클립 유무를 objdump(원본 SHA 확인)로 적는다. → 다음 수리 가설이 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED` 중 무엇인지 결론낸다.
- 귀속 실패(`none`·EIP 불일치)가 4/9를 넘으면 FAIL이다. 이때 watch 범위(무장 시점·스레드)를 원인 후보로 적는다.
- 금지: gate·validator·기준·`G1_OVERLAY_MAX_*` 변경, 원본/raw 수정, 제품 미러 동작 변경.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산·read-only 검수만 했다. 게임/source/commit은 0이다. focused 검사·SAFETY 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1039 full PASS 1629 `logs/gates/lap1039-work-full-check.log`).
- 남은 위험: wrap 경로는 실장 0회라 호스트 테스트로만 검증됐다. save006 짧은 run 꼬리는 원인을 모른다(backlog). 성능 p95는 대조가 후보보다 높게 나오는 환경 변동이 계속된다.
- backlog: `0x46884E`(A 1), save006 짧은 run 꼬리, 팝업 p298..338 run 변동, hold keydown 위상, 가장자리 마우스 스크롤, overlay BltFast rejects, 다중 팝업 heal.
- 사용자 승인 상태: 기술 부분수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-S(위 사전등록).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1039 work, 1,800 B, SHA256 `0e87eb1ced6753c072454a86799c650a12fc550e049a28e519bce73dafddda21`)

```
lap1039 (Claude Code claude-sonnet-5-5, work) — H-R 구현·실행 완료, 독립 검수(middle) 필요. 자가 승인 금지.

한 일: 기후킹 0x466B50(mirror_flip_rle)을 화면 교집합 diff 미러로 확장(int32 해석·교집합·원 인자 6개 1회·drift w 기록) + 순수 함수 g1_flip_rle_region(g1_rect_fill.h) + 계수 reject_bounds/clipped_calls/wrap_calls. 계약·경계 테스트 GREEN(18 passed), lint·typecheck PASS.
결과(기록 docs/history/laps/20261006_lap1039_work_g1_hr_flip_rle_edge_intersection_466b50.md): R-0 항등식 전 run 성립·안전0·wrap_calls 0, R-1 reject_size 75/76→0·표본 B 4→0·C 22→0(PASS), R-3 성능 p95 7/7(대조 9/13), R-4 save006 38/39프레임 0·신규 0(p95 9/7, r1은 load 7.66).
미결(R-2 미달): 마지막40 중앙값 26 불변(<26 필요), r1∩r2 합 2,064→2,776(<2,064 필요). 프레임별로 보면 신규 stale 0이고 증가분은 기준 r2의 run 변동이 빠진 효과(p26·44·71 29→0, p377 5→0). 남은 stale = 유닛 크기 덩어리(좌표는 기록 §R-2 해석)와 팝업 p298..328.
절차 이탈: 첫 launch pid 확인 실패로 run_r.sh가 동시에 2개 돌아 중단·격리(invalid_concurrent_*), 수치는 단일 인스턴스 재실행분만 사용. 구현을 테스트보다 먼저 작성(RED 선행 없음).
승격 작업자가 이어서 할 일: (1) 공유 temp 20261006_lap1039_work_hr/ 의 pair-result·trace_raw·layer_drift·screen_watch·stale_mask를 analyze_r_*.py·isect_r.py 없이 새 스크립트로 재계산, (2) R-2 판정(문자 미달을 가설 지표 충족·신규 stale 0·교집합 지표 불안정으로 수용할지), (3) mirror_flip_rle 코드 검수, (4) R-4 p95 9 판정, (5) 수용 시 다음 work 사전등록: 남은 유닛 크기 stale 덩어리 writer 귀속.
```
