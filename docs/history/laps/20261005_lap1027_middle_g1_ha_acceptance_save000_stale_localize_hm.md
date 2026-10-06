# 2026-10-05 | lap1027 | G1 middle — H-A 독립 검수(PASS(partial) 수용) → 남은 save000 stale 위치 확인·writer 귀속 → work H-M 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간 계획·컨펌) 1 lap. 게임 실행·source 변경·커밋 0.
- 가설: lap1026 work H-A v2(back buffer KEYSRC `Blt` diff 미러 + H-A2 present 재검증)의 A-0~A-4 수치가 raw로 재현되는가. heal 코드가 다른 writer의 정당한 갱신을 지우지 않는가.
- 예상 PASS / FAIL 조건: 새 스크립트로 재계산했을 때 판정에 영향을 주는 불일치가 0이어야 한다. diff는 BltFast overlay 미러와 같은 구조여야 하고, heal은 화면(1x)을 기준값으로 써야 한다.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제(원문은 아래 부록). 공유 temp `20261005_lap1027_middle_review/`(모두 uncommitted):
  - `recalc_lap1027.py` SHA256 `44f7e2b1eb0de277ed13fb872924bc3566a24927532cd520cc7a6d5855552a1d` → `recalc_lap1027.json` `590d2775d251537d6c648db1ae3f39e20869dd0f0e7e07b1a11dbf287167f4a0`·`recalc_stdout.txt` `2748cc986456f51c5fee4dec7ebb60a3479ec285ced095919c82cc89023f1e45`
- 원본 SHA / fixture: 모든 run pair-result의 `private_exe_sha256` = 원본 `b56986e0…8ac`. save000 `1c703551…19da`(index 1), save006 `616b7997…a064`. 활성8인 부하 증명은 아니다.
- 검수한 source: 현재 `g1_mirror2x.c` `0243f543…`, `g1_mirror2x.h` `633ff485…`, `direct_draw_trace.c` `c89df117…`, `tests/test_g1_rect_fill.py` `2300333d…`. 모두 work 기록과 같다. v2 run 5개의 bridge 사본도 현재 source와 같다.

## 1. 독립 재계산(`analyze_ha*.py`·제품 helper 미사용)

비교 기준은 lap1024 H-B4 save000 r1/r2와 save006 r1/r2다.

| 항목 | work | 재계산 r1 / r2 |
|---|---|---|
| A-0 scene | camera (39,53)·tick 50596/50596·50597/50595 | camera (39,53)→(39,53)·units 375·scene_state_equal true. `scene.snapshot.tick` 50596/50596(r1). `performance_window.tick_start`(원본/후보)는 50599/50601·50600/50600이다. work는 다른 tick 필드를 적었고, 판정에는 영향이 없다 |
| A-0 계수 | inv 5 = mirrored 5(keysrc 5)·reject 0·heal 44/559,476 | 같다(r1=r2). 항등식 inv = mirrored+bounds+size+lock+target+result 성립. changed 5·clipped 0·colorfill 0 |
| 안전·cleanup·source | 0·true·true | 0이 아닌 안전 키는 `panel_transfer_mismatch_cleared`뿐이다(판별력 없음, lap1013). cleanup [true,true]. source_unchanged [true,true,true] |
| A-1 표본 | A 0·B 0·C 0, u A5/B1/C1 | A 0·B 0·C 0(H-B4 기준 A 41 = [298]·[299]·[300]·[301..338]). u = A p298·299·300·301·339, B p168, C p339 |
| `b` 레코드 | p298..302 5회 | (86,94) 51×38 → (60,75) 102×76 → (35,56) 153×115 → (26,49) 170×128 ×2. ch 1405/5550/12668/15541/15541. bf 85 → af = ex 94/215/163/187/187 |
| 표본 A 궤적 | — | s 레코드 p298 94/94·p299 215/215·p300 163/163·p301 187/187·p339 85/85. scr = snap가 p301..338 동안 유지된다 |
| A-2 화면 stale | p298..338 858·656·316·591·414.5 | p298..338 **858**(H-B4 16,261)·p0..83 656·p84..297 316·p339..365 591·마지막40 414.5(r1=r2). p0..23 441·p24..58 3,444·p59..83 216 불변. 총합 895,111 → **290,397**(r2 290,301). p298..338 합 640,929 → 36,119 |
| A-3 성능 | p95 7·비 1.0000028/1.0000038 | pair p95 7/7(원본 1/1), 비 1.0000028/1.0000038 |
| A-4 save006 | r1∩r3 38프레임 24 px·39프레임 0·신규 0 | r1∩r3 38프레임 24 px(y515..520×x616..619), 51프레임(880 포함) 교집합 0. H-B4 s6 대비 신규 0·제거 0. r1 단독·r3 단독도 각각 24/0. PS3 elapsed p50/p95/max r1 5/8/17, r3 5/7/9, r2 23/50/116(ps3 396). layer_drift 파일은 미생성(env-off) |
| save006 rect_blt | r1 800 = 5 + target 795·heal 55/799,235, r3 792 target | 같다. r2 341 전부 target·mirrored 0·heal 0. 세 run 모두 항등식 성립 |

**판정 영향 불일치는 0이다.** 전사 차이는 tick 필드 선택 1건뿐이다.

## 2. diff 검수(lap1024 bridge `0fb12c3b…`·`a6c28fe2…`·`c3e80bf5…` 대비)

- `hook_blt`: `g1_mirror2x_enabled() && state==3 && !is_primary`일 때만 begin을 부른다. end는 `rect_blt.active`가 아니면 바로 돌아간다. 원본 Blt는 원 인자로 한 번만 호출된다. present 자체 Blt(primary)는 제외된다.
- `begin`의 거르기 순서: invocations 증가 → 레코드 크기(≥800·==600, 아니면 target) → dst NULL(size) → 화면 교집합(비면 bounds) → 320×128 초과(size) → READONLY Lock 실패(lock) → lpSurface·pitch·desc 크기·캐시/패널 버퍼(target). before 복사는 크기 검사 뒤에만 하고, 전용 버퍼 `g_rect_blt_before`(BltFast `g_overlay_before`와 분리)를 쓴다. overflow 경로는 없다.
- `end`: 원본 결과가 FAILED면 result로 센다. 다시 Lock해서 `g1_overlay_blt_apply`(BltFast와 같은 diff 함수)를 부르고, 실패하면 size로 센다. 수락된 begin은 end에서 정확히 하나의 계수로 끝나므로 항등식이 구조적으로 성립한다.
- **heal(H-A2)**: 마지막으로 바뀐 Blt 사각형(≤320×128)에서 present 직전에 before=`expected`, after=화면으로 같은 diff를 적용한다.
  - 화면과 expected가 같은 픽셀은 건드리지 않는다. 그래서 다른 hooked writer가 화면과 expected를 함께 갱신한 픽셀은 지우지 않는다.
  - 다른 픽셀은 1x 화면 값의 Scale2x로 HD를 고치고 expected를 화면 값으로 맞춘다. 즉 HD 화면을 실제 1x 화면에 다시 맞추는 것이다. 측정값만 바꾸는 것이 아니다(`g_mirror`에 쓴다).
  - 해제 조건은 3 present 연속 차이 0, state≠3, mirror/expected 부재다.
  - save000 heal 44 present = 표본 A stale 41(p298..338) + 해제 전 무차이 3이다. heal 픽셀 559,476/44 ≈ 12.7k/present다. 캐시 전송 hook이 매 present 팝업 영역을 지형(85)으로 되돌리고, heal이 다시 팝업을 미러한다는 설명과 맞는다.
  - 비용은 p95 7 ms로 영향이 없다. scratch 버퍼를 BltFast와 공유하지만 둘 다 게임 스레드에서만 쓰이고 동시에 쓰이지 않는다.
- 한계(수용): heal은 사각형 하나만 감시한다. 팝업이 둘 이상 겹치면 앞의 것은 감시하지 않는다. 화질은 1x 결과의 Scale2x다(P6 범주).

## 3. 판정

**H-A를 PASS(partial, 기술 부분 — 제품/마일스톤 마감 아님)로 수용한다.**
- 표본 A 41→0, p298..338 16,261→858(−94.7%), save000 화면 stale 총합 −67.6%다.
- 성능 영향이 없다. save006은 비회귀이고, r1에서는 KEYSRC Blt 5회와 heal 55 present가 실제로 실행된 상태로 24 px/0이다. lap1025는 "save006 KEYSRC 0"이라고 적었지만 이것은 run마다 다르다(r1 5·r3 0).
- 절차 편차(수용): A-4는 r1∩r2로 사전등록했지만 r2(load 28 환경 outlier)를 r3로 대체했다. r2의 계수(mirrored 0·heal 0)로 보면 이 변경의 경로가 비활성일 때도 outlier가 났다. r1·r3 단독도 각각 기준을 충족한다. lap995 선례와 같다.
- **wined3d 재기록 경로 UNKNOWN 정리**: 게임이 호출한 non-primary Blt는 5회뿐이다(계수 inv 5, target 0). 그런데 1x 화면은 p301..338 동안 187을 유지한다(s 레코드 scr = snap 187). lap1022 watch로는 같은 41 present에 wined3d 스레드가 쓴다. 원본 lane에도 같은 Blt 5회가 있다. 즉 이것은 원본 게임의 wined3d 동작이며, 후보는 그 결과를 화면 diff로 따라간다. 추가 진단은 하지 않는다. 기술 근거가 제품 판정에 더 필요하지 않고, heal이 화면 기준 재동기화라서 호출 경로와 관계없이 안전하기 때문이다. 이 UNKNOWN은 기록만 하고 닫는다.

## 4. 남은 save000 stale 분해(recalc, r1)

| 창 | 중앙값 | 합 | 비율 |
|---|---|---|---|
| p24..58(일시 덩어리) | 3,444 | 103,203 | **35.5%** |
| p298..338(팝업, H-A 뒤 잔여) | 858 | 36,119 | 12.4% |
| 나머지(바닥: p0..23 441·p59..83 216·p84..297 316·p339..365 591·p366.. 414) | — | 151,075 | **52.0%** |

- p24..58 덩어리는 p23부터 올라가 p30..33에 정점 약 4,160을 찍고, p46 1,301, p59 이후 수백으로 내려간다. writer는 미확인이다.
- 바닥 성분은 present당 수백 px이지만 410 present 전체에 걸쳐 합이 가장 크다.
- 두 성분 모두 **위치 정보가 없다**. save000 run은 `--stale-mask`를 쓴 적이 없다(하네스·DLL은 PS3 순번 기준이라 그대로 쓸 수 있다). 표본 watch 좌표 3점(A/B/C)은 `g1_layer_drift.h:55`에 고정돼 있다.

## 5. 다음 work H-M 사전등록(Sonnet work 1 lap, 진단 + 필요 시 최소 수리)

목표: 남은 save000 stale(p24..58 덩어리와 바닥)의 위치를 stale mask로 찾고, 대표 좌표의 writer를 기존 screen watch로 귀속한다. 귀속된 writer가 이미 확립된 미러 패턴(diff 미러/heal)으로 처리 가능하면 FEASIBLE로 판정하고 다음 work에서 수리한다.

### 5.1 단계 M-1: 위치 찾기(제품 변경 0)
- save000 pair 2회. lap1026 `run2.sh` s0 인자에 `--stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`을 더한다(51자·8항목·39덤프). `--layer-drift`는 유지하고 screen watch는 끈다.
  - **주의(middle 확인):** DLL은 env 값을 64바이트 버퍼로 읽는다(`g1_mirror2x.c` `initialize_environment`, `size < sizeof(stale_mask)`). 63자를 넘는 spec은 오류 없이 무시되어 덤프가 0개가 된다. 처음 구상한 7범위 spec은 66자라 이 함정에 걸렸다. 위 spec은 `g1_stale_mask_parse` host 컴파일로 ok=1·8항목·39덤프(6·12·24..58 짝수·71·84..294/30·298..338/10·352·366..399/11)를 확인했다. 실행 뒤 `stale_mask.bin` 레코드가 39개인지 먼저 확인한다.
- 분석은 r1∩r2 프레임별 stale mask다. 덩어리(p24..58)와 바닥(나머지)을 따로 연결 성분(8-이웃)으로 나눈다. 각 성분의 bbox·픽셀 수·존재 프레임 수와, 존재 프레임 기준 상위 성분을 낸다.
- **M-1 PASS**: 덤프 39개가 있어야 하고, 각 프레임 mask의 stale 픽셀 수가 같은 run trace의 `stale_pixels`와 같아야 한다(mask 정합). 이 등식은 lap1026 save006 r3 기존 산출물에서 51/51 프레임 일치로 이미 성립함을 확인했다. r1∩r2가 덩어리 창 중앙값의 ≥80%, 바닥 프레임 중앙값의 ≥80%를 설명해야 한다(재현성). 이 둘이 아니면 위치가 run마다 달라진 것이므로 그 사실을 기록하고 M-2로 가지 않는다.

### 5.2 단계 M-2: writer 귀속(진단 DLL 변경, env 게이트)
- `g1_layer_drift.h`의 표본 좌표에 opt-in env override `SYW2_G1_DRIFT_SAMPLES=x,y;x,y;x,y`(정확히 3점, 범위 [0,800)×[0,600), 파싱 실패 시 기존 A/B/C 유지)를 추가한다. 하네스에는 `--drift-samples`를 둔다. env가 없으면 동작은 바이트 수준에서 기존과 같아야 한다. 테스트: 파서(정상·3점 아님·범위 밖·빈 값) RED→GREEN.
- 표본은 M-1에서 고른 덩어리 최대 성분 1점, 바닥 최대 성분 1점, 바닥 2순위 또는 덩어리 2순위 1점이다. 성분 안에서 r1∩r2 존재 프레임이 가장 많은 픽셀을 고른다.
- save000 pair 2회: `--layer-drift --screen-watch --drift-samples …`. lap1022 H-B3과 같은 판정을 쓴다(selftest hit·무장 fail 0·주소 일치 3/3·양성 대조).
- **M-2 PASS**: 세 표본 각각의 stale present ≥1이어야 한다. 미설명 변화 `u`의 ≥80%가 EIP/모듈로 귀속돼야 한다. 결과를 writer별로 {미후킹 EXE 함수 주소·hook된 미러의 표류·wined3d/외부 모듈} 중 하나로 분류한다.
- **판정 출력**: writer가 미후킹 EXE 함수면 objdump 근거(prolog·ret·호출처)와 함께 FEASIBLE/NOT_FEASIBLE을 쓴다. hook된 미러의 표류면 해당 미러 이름을 쓴다. 외부 모듈이면 heal 일반화 가능성을 쓴다. **이번 work에서 제품 수리는 하지 않는다.** 단, 귀속이 단일 기존 패턴(예: 다른 KEYSRC Blt 사각형)이고 변경이 10줄 이하면 work 판단으로 수리 후 save000 pair 2회 + save006 env-off pair 2회로 A-2/A-4 같은 기준을 재측정해도 된다(구현 우선).

### 5.3 공통
- 성능 gate run 전에 `/proc/loadavg`를 기록한다. 1분 load >8이면 낮아질 때까지 기다린 뒤 실행한다(lap1026 r2 outlier 재발 방지).
- 안전 0(`panel_transfer_mismatch_cleared` 제외), cleanup·source_unchanged true, camera (39,53)·units 375여야 한다. 실행 후 `game` 사본만 삭제한다. 디스크 여유는 현재 53G다.
- FAIL이면 원인(mask 정합·watch 무장·좌표 변환)을 기록하고 1회 수리 후 재실행한다. 그래도 FAIL이면 인계한다.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산·read-only 검수만 했다. 게임/source/commit은 0이다. 전체 `make check`는 SKIP했다. source가 불변이고 lap1026 full PASS 1622가 유효하다. focused 검사 결과는 STATUS에 보강한다.
- 남은 위험: heal은 사각형 하나만 감시한다. 다른 save·장면에서 여러 팝업이 연속되는 경우는 미검증이다. save006 KEYSRC Blt 유무는 run마다 다르다.
- backlog:
  - 갱신: "표본 A wined3d 재기록 UNKNOWN"은 원본 동작으로 정리해 닫는다. p24..58·바닥은 H-M으로 진행한다.
  - 유지: save006 짧은 run 꼬리, 성분 D, hold keydown 위상, 가장자리 마우스 스크롤, wrap 쓰기 미추적, save000 overlay BltFast rejects 451, 다중 팝업 heal
- 사용자 승인 상태: 기술 검수일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-M(위 §5).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1026 work, SHA256 `0d42e3d6d08ea04d0d81afeb44c44b22a25e3aabca7a1710f05dc464ee0e4f1c`)

```
lap1026 work(Claude Code claude-sonnet-5-5) G1 H-A 인계 (마일스톤 경계 아님; 사전등록 A-0~A-4 v2 기준 PASS, 독립 검수 요청).
- 한 일: g1_mirror2x.c에 g1_mirror2x_overlay_rect_blt_begin/end(back buffer non-primary IDirectDrawSurface7::Blt, 전용 before 버퍼, 계수 14개)·rect_blt_heal_at_present(H-A2), direct_draw_trace.c hook_blt begin→원본→end, 계약 테스트. v1(Blt 미러만)은 A-1/A-2 FAIL(A 41→36, p298..338 16,391)이라 진단 b 레코드로 원인(p303부터 expected 85 되돌림: 캐시 전송 hook + wined3d 매 present 재기록) 확인 뒤 H-A2 1회 수리.
- 실행: v1 save000 pair 2회+진단 2회, v2 save000 pair 2회+save006 pair 2회+save006 r3 재실행. 공유 temp 20261005_lap1026_work_ha/(analysis_s0_v2.json·analysis_s6_v2_r13.json·run.sh·run2.sh). 전부 exit 2 = 기존 pair HOLD.
- 결과(v2): 표본 A 41→0·B/C 0, p298..338 중앙값 16,261→858, 다른 창 656/316/591/414.5, p95 7 ms·ticks 비 1.000003, 안전 0, heal 44 present/559,476 px. save006 r1∩r3 38프레임 24 px(성분 D)·880 포함 39프레임 0·신규 0. save006 r2는 load average 28(다른 프로젝트) outlier(p95 50 ms)라 보존만 하고 r3로 대체.
- middle이 확인할 것: (1) v2 4 run layer_drift/trace_raw/stale_mask를 analyze_ha*.py 없이 새 스크립트로 재계산, (2) g1_mirror2x.c diff 검수(rect_blt begin/end: NULL dst·교집합·reject 계수 항등식, heal: 사각형 수명·expected 덮어쓰기가 다른 writer 갱신을 지우지 않는지), (3) wined3d 재기록 경로는 UNKNOWN(hook_blt 호출 5회뿐) — 정리 또는 추가 진단 필요 여부, (4) 남은 save000 stale(p24..58 3,444 등) 중 다음 work 사전등록.
- 기록: docs/history/laps/20261005_lap1026_work_g1_ha_rect_blt_diff_mirror.md. 변경 uncommitted.
```
