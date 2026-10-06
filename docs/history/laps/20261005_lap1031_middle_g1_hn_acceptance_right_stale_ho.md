# 2026-10-05 | lap1031 | G1 middle — H-N 독립 검수(바닥 조각 수리 PASS(partial) 수용, N-1 기준 오류 정정) → work H-O(우측 잔여 stale 표본 귀속) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간 계획·컨펌) 1 lap. 게임 실행·source 변경·커밋은 0이다.
- 가설: lap1030 work H-N의 수치가 raw에서 재현되는가. 특히 N-1 "마지막40 ≤100 미달"이 수리 결함인지, 사전등록(lap1029 §5.3) 분해 오류인지 판정한다.
- 예상 PASS / FAIL 조건: 새 스크립트로 재계산했을 때 판정에 영향을 주는 불일치가 0이어야 한다. bridge 사본은 현재 source와 같아야 한다. 미러가 바닥 조각만 지우고 다른 stale 픽셀을 바꾸지 않아야 한다.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제(원문은 아래 부록). 공유 temp `20261005_lap1031_middle_review/`(모두 uncommitted):
  - `recalc_lap1031.py` `ca3eb5d5…d5c0` → `recalc_lap1031.json` `bc66c89b…1493`·`recalc_stdout.txt` `a29b326d…3777`
  - `recalc2_lap1031.py` `00d77373…bec` → `recalc2_lap1031.json` `0aae4433…4052`(바닥 프레임 분해·신규 픽셀 위치)
  - `recalc3_lap1031.py` `4d69d6a6…b897` → `recalc3_lap1031.json` `37ef9d6c…7175`(팝업 상자 run 변동)
  - `recalc4_lap1031.py` `f0777295…b58` → `recalc4_lap1031.json` `69f887cf…a52`(잔여 위치·표본 후보)
  - `base_loaded_full.png`·`crop_base_right.png`(n_s0_r1 baseline loaded 화면, 위치 확인용)
- 원본 SHA / fixture: 8 run(기준 lap1028 m3 4 + lap1030 n 4) 모두 `private_exe_sha256` = 원본 `b56986e0…8ac`. save000 `1c703551888f`(index 1), save006 `616b79978917`(index 7). 활성8인 부하 증명은 아니다.
- 검수한 source: 현재 `g1_mirror2x.c` `23667cc8…`, `g1_rect_fill.h` `1b22db0a…`, `g1_mirror2x.h` `7dae0faa…`, `direct_draw_trace.c` `4823d1cc…` = n run 4개 bridge 사본과 같다(`supply_bridge_build.json` 입력 SHA도 일치). bridge `_inmm.dll`은 run마다 다시 빌드돼 SHA가 다르다(lap1028도 같음). work 기록의 `6b7bfca1…`는 `tools/inmm_stub/_inmm.dll`(make 산출물)이다.

## 1. 독립 재계산(`analyze_n_*.py`·제품 helper 미사용)

| 항목 | work | 재계산(r1 / r2) |
|---|---|---|
| N-0 계수 | inv 3296 = 3292+2+2 | r1 3296 = 3292+target 2+size 2, r2 3304 = 3300+2+2(bounds·guard 0), 항등식 4/4 run 성립. ybound 600. save006 3673/3664 전부 mirrored |
| N-0 안전·scene | 안전 0 | 0이 아닌 안전 키는 `panel_transfer_mismatch_cleared`뿐(판별력 없음, lap1013). cleanup·source_unchanged true, scene_state_equal, camera (39,53), units 375, trace 손상 0, mask=trace 불일치 0 |
| N-1 39덤프 공통 | 168→0 | 168 → **0**(r1 단독·r2 단독도 0) |
| 바닥 4×6 조각 | 덤프당 9→0·총 7,872→0 | 기준 r1·r2 중앙값 9·최대 9·총 7,872 px → **0/0**. y515..549 띠 중앙값 216→0 |
| 바닥 프레임(16) 교집합 중앙값 | (미기재) | 408 → **232**(사전등록 ≤40 미달 — 아래 §2) |
| 마지막40 중앙값 | 414.5→246.5 | 414.5 → **246.5/246.5**. 같은 ordinal 차이의 중앙값 168/168 |
| 창 중앙값 | 모든 창 감소 | p0..83 216→0, p24..58 216→0, p84..297 316→124, p298..338 858/727→667/558, p339..365 591→423, p84..365 356→164, p366.. 399.5→246.5/246, 합 190,379/185,008→111,275/106,806 |
| 표본 A/B/C | 0 | 0/0/0, `drift_unattributed` [5,1,1] 불변 |
| N-3 성능 | p95 7/7·비 1.0000 | pair perf PASS, p95 7/7, tick 비 1.0000035/1.0000031, PS3 elapsed p50/p95/max 5/7/11 |
| N-4 save006 | 38프레임 24→0·39 0·신규 0 | r1∩r2 38프레임 **0**(기준 24 = 성분 D y515..520×x616..619), 39·51프레임 0, 신규 0·제거 24. r1·r2 단독도 0. PS3 p95 7/7 |
| 신규 stale | r1 0·r2 755 | 기준 r1∪r2 대비 r1 0, r2 **215**(p298..338 5덤프×43, 상자 y218..224×x240..299). work 755는 집계 방식 차이로 보이며 판정 무관 |

**판정에 영향을 주는 불일치는 0이다.** r2 신규 픽셀은 팝업 상자(y218..226×x240..302) 안이다. 그 상자의 stale은 기준 317/281, 이번 317/303으로 기준 run 변동 범위 안이다(`recalc3`).

## 2. N-1 미달의 원인 = lap1029 middle 분해 오류(정정)

- **픽셀 정확 분해**:
  - 바닥 프레임 16개 전부에서 `새 r1∩r2 = 기준 r1∩r2 − 4×6 조각`이 정확히 성립한다(16/16).
  - p352..399 5덤프에서는 run별 마스크도 정확히 같다(10/10).
  - 즉 H-N은 바닥 조각만 지웠고, 다른 stale 픽셀은 하나도 바꾸지 않았다.
- **오류의 위치**: lap1029 §4는 "바닥 17조각×24 px = 408/present"라고 적었다. 실제로는 다르다.
  - 덤프당 조각은 7~9개(168~216 px)다. 앞쪽은 9개, p114..294는 8개, p338~는 7개다.
  - 바닥 프레임 교집합 408은 조각 중앙값 192와 비조각 중앙값 232가 섞인 값이다.
  - 따라서 N-1의 ≤40(바닥 프레임)·≤100(마지막40)은 잘못된 분해에서 나온 기준이다. 마지막40 414.5 = 조각 168 + 비조각 246.5다.
- **H-N 가설 판정**: H-N의 실제 가설은 "`0x465E80`이 바닥 조각의 writer이고 미러가 그것을 지운다"이다. 그 기준(조각 → 0, 비조각 불변)은 충족했다. 그래서 N-1을 **기준 오류로 재분류**하고 수리는 PASS로 본다. work의 "사전등록 분해 오류" 판단이 맞다.

## 3. diff 검수(현재 source = n bridge, 기준 = lap1028 m3 bridge)

- `g1_rect_solid_region`:
  - 부호 비교로 x0,x1 ∈ [0,stride), y0,y1 ∈ [0,ybound)를 검사하고, 하나라도 밖이면 0(쓰기 없음)이다. lap1029 §3 역어셈블(`jge`/`jl`)과 같다.
  - 축별 정렬 뒤 양끝을 포함하고, 화면 [0,800)×[0,600)에 자른다. stride 패딩 x 800..831은 미러하지 않는다(화면 밖).
  - viewport 교집합은 없다(§3 (a) 반영).
- `mirror_rect_solid`:
  - 거르기 순서는 guard → 대상 버퍼(H-F2 동형 조건) → 범위 복제 → `g1_overlay_blt_accepts` 크기 상한 → 전용 before 버퍼(`G1_OVERLAY_MAX_WIDTH*HEIGHT`, 사각형 ≤320×160만 복사) → 원본 1회(원 인자) → `g1_overlay_blt_apply` 순이다.
  - apply 실패는 reject_size로 센다. install(old bytes `8B 41 10 53 55` 검증)·restore·installed·reset 목록도 갱신했다.
  - `ybound`는 첫 비0 값만 기록한다(사양대로).
- `direct_draw_trace.c`:
  - `rect_solid_details[340]`: 값 8개가 모두 10자리면 NUL 포함 **352 B로 12 B 넘친다**(정적 계산).
    - 넘치려면 reject 계수까지 10억 단위여야 해서 실제로는 도달할 수 없다. 현실적인 최대는 약 310 B다.
    - 그래도 계약상 결함이다. 다음에 이 파일을 건드리는 work가 360으로 키운다(비차단).
  - `mirror_details` 5000→5400: 실제 metrics 줄 4,440자에 uint 127개가 모두 10자리가 되는 최악을 더해도 5,386자다(줄 전체가 버퍼라고 가정한 상한).
  - 여유가 얇다. **다음에 계수를 더 추가하면 버퍼를 같이 키워야 한다**(work 후속 주의, 이번 판정 무관).
- 남은 위험(work 기록과 동일):
  - save000의 reject_target 2·reject_size 2는 호출 인자가 기록되지 않았다. 잔여 stale에 대응하는 흔적은 없다.
  - 호출처 33곳 중 관측된 것은 두 장면뿐이다.

## 4. 판정

**H-N 수용: 바닥 조각 수리 PASS(partial, 기술 부분 — 제품/마일스톤 마감 아님).**
- save000 바닥 4×6 조각 7,872→0, 39덤프 공통 168→0, 화면 stale 합 −41%다.
- save006 성분 D(24 px)도 같은 writer로 확인됐다(24→0). 신규·성능·안전 회귀는 0이다.
- N-1 수치 미달은 §2 기준 오류로 정정한다.
- 남은 save000 stale(마지막40 246.5)은 H-N 이전부터 같은 픽셀로 있던 비조각 stale이다.
  - 팝업 밖 r1∩r2 3,615 px 중 86%가 x≥686이고, p352~에서는 100%다(`recalc4`).
  - 고정 위치 군: y455..475×x686..721(5덤프 204·264·294·352·388).
  - 이동 군: y134..155×x748..793, y372..383×x777..790, y214..226×x780..793.
  - 가장자리 군: x792..799×y315..321(p26·44·71).
  - 기준 화면 우측(x≥686)은 전투 유닛·효과가 있는 맵 영역이다. writer는 미귀속(UNKNOWN)이다.

## 5. 다음 work H-O 사전등록(Sonnet work 1 lap, 진단 실행 — 제품 동작 불변)

목표: 남은 우측 stale 표본 3점의 writer를 귀속하고, 수리 가능성(FEASIBLE/NOT_FEASIBLE/BLOCKED)을 판정한다. 기존 하네스만 사용한다(코드 변경이 필요 없을 것으로 예상).

### 5.1 실행(성능 gate 전 `/proc/loadavg`, 1분 load >8이면 대기)
- save000 pair 2회. 인자는 다음과 같다.
  - lap1028 `run_m2.sh`와 같은 형식: `--fixture save000 --scene-actions none --performance-window --layer-drift --screen-watch`
  - `--drift-samples "695,468;766,139;799,315"`
  - 마스크 대조용: `--stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`
- 표본 선택 근거(`recalc4`):
  - A (695,468): 고정 군, r1∩r2 5덤프(204·264·294·352·388)
  - B (766,139): 이동 군, 352·377
  - C (799,315): 가장자리, 26·44·71
- 실행 뒤 `game` 사본만 삭제한다. 하네스를 바꿔야 하면 테스트 RED→GREEN을 거치고, save006 env-off pair 1회로 비회귀를 확인한다.

### 5.2 PASS / FAIL
- **O-0**:
  - selftest PASS, 무장 fail 합 0, 무장 주소 → 화면 좌표 3/3 = 지정값이어야 한다.
  - 마지막40 중앙값 246.5±5%여야 한다(watch 부하 영향 확인).
  - 안전 0(`panel_transfer_mismatch_cleared` 제외), cleanup·source_unchanged true, camera (39,53), units 375여야 한다.
- **O-1(귀속)**: 표본별 `u` 레코드의 ≥90%가 같은/직전 present의 마지막 `x` 쓰기 값과 일치해야 한다. 각 표본 stale present(`s` cov=1·scr≠snap)의 마지막 writer EIP 분포를 기록한다.
- **O-2(분류·판정)**: 표본별 stale present의 마지막 writer를 셋으로 분류한다.
  - (i) 이미 hook된 EXE 함수: EIP가 hook 함수 범위 안. 미러 reject/누락 원인을 계수·`w` 레코드로 확인한다.
  - (ii) 미후킹 EXE 함수: objdump로 함수 시작·`ret n`·인자·클립을 확인한다.
  - (iii) 다른 모듈(wined3d 등)
  - 한 표본이라도 stale present의 ≥80%가 (ii) 단일 함수이고 hook 가능(5바이트 이상 명령 경계)하면 **FEASIBLE** → 다음 work에서 그 함수 diff 미러를 구현한다. (i)이면 해당 hook 수리 경로를 적는다. 셋 다 (iii)이거나 표본이 stale 0이면 표본을 재선정(1회)하고, 그래도 안 되면 **BLOCKED**로 근거를 남긴다.
- 금지: 미러 동작 변경, gate·validator·기준 변경, 원본/raw 수정.
- 허용 부수 수리(1줄): `direct_draw_trace.c` `rect_solid_details[340]` → `[360]`(§3). 계약 테스트가 있으면 같이 고친다.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산만 했다. 게임/source/commit은 0이다.
- 전체 `make check`는 SKIP했다. source가 불변이고 lap1030 full PASS 1626(`logs/gates/lap1030-work-full-check.log`, exit 0)이 유효하다. focused 검사 결과는 STATUS에 보강한다.
- 남은 위험:
  - `mirror_details` 여유가 얇다(§3).
  - 표본 B·C는 stale 덤프가 2~3개뿐이라 귀속 표본 수가 적을 수 있다.
  - 잔여 stale 일부는 이동 스프라이트라서 고정 3점으로 전부 덮을 수 없다.
- backlog 유지: save006 짧은 run 꼬리, hold keydown 위상, 가장자리 마우스 스크롤, wrap 쓰기 미추적, save000 overlay BltFast rejects, 다중 팝업 heal. 성분 D는 H-N으로 해소됐다.
- 사용자 승인 상태: 기술 검수일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-O(위 §5).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1030 work, SHA256 `7d1723c3034625a155cf9b7805e5ff54d5d04eb1144cf4d02ba2849c603ae3b4`)

```
lap1030 work(Claude Code claude-sonnet-5-5) G1 H-N 인계 (마일스톤 경계 아님; 구현 PASS(partial), 독립 검수 요청).
- 한 일: 미후킹 `0x465E80`(단색 사각형, 5바이트 `8B 41 10 53 55`) diff 미러 `mirror_rect_solid` + 호스트 테스트 가능한 `g1_rect_solid_region()` + 계수 8개(ybound 포함). 원본 범위 검사(x∈[0,stride)·y∈[0,[r+0x14])) 복제, 정렬·양끝 포함, 화면 800×600 교집합, viewport 교집합 없음. `mirror_details` 5000→5400.
- 실행: 공유 temp 20261005_lap1030_work_hn/(run_n.sh, n_s0_r1|r2, n_s6_r1|r2, analyze_n_*.py, analysis_n_s0.json·analysis_n_s6.json). 4 run 전부 pair exit 2 = 기존 pair HOLD.
- 결과: N-0 PASS(inv 3296 = 3292+2+2). save000 39덤프 공통 168→0, 바닥 4×6 조각 덤프당 9→0(총합 7,872→0), p24..58 216→0, 모든 창 감소·표본 A/B/C 0·p95 7/7·tick 비 1.0000. save006 env-off 성분 D 24→0·39프레임 0·신규 0. **N-1 마지막40 414.5→246.5로 ≤100 미달**: 감소분이 정확히 바닥 몫(168)이고 남은 246.5는 바닥 아닌 우측(x≥686) 이동 덩어리(예: y134..155×x748..768 258 px)로 미귀속 — 사전등록 분해 오류.
- middle이 확인할 것: (1) 새 스크립트 재계산(공통 168→0·조각 9→0·마지막40 246.5·save006 D 0), (2) 마지막40 미달 분해 수용·기준 정정, (3) mirror_rect_solid/g1_rect_solid_region 코드 검수, (4) 다음 work H-O(우측 stale 덩어리 `--drift-samples` 귀속) 사전등록.
- 기록: docs/history/laps/20261005_lap1030_work_g1_hn_rect_solid_465e80_diff_mirror.md. 변경 uncommitted.
```
