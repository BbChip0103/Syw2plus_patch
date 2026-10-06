# 2026-10-06 | lap1038 | G1 middle — H-Q 독립 검수(Q-3 판정 포함) → work H-R(`0x466B50` 화면 가장자리 교집합 미러) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·source 변경·commit 0.
- 가설 / 검수 대상: lap1037 work H-Q(`0x467FD0` diff 미러 `mirror_flip_blend`)의 Q-0~Q-4 수치가 raw에서 재현되는지 본다. Q-3(성능 p95 ≤7ms) 미달이 미러 비용 때문인지 호스트 환경 때문인지 판정한다.
- 예상 PASS / FAIL 조건: lap1036 §H-Q 사전등록 그대로(기준·gate 무변경).
- 처리한 인계: `loop/ESCALATE_SOL`(lap1037 work, 1,322 B, SHA256 `f5293f899a82b93011a0511405b4f4966c2ca42ddab44e70471e58b1f7854458`). 원문은 아래 부록에 두고, 처리 뒤 삭제했다.
- 변경 파일: 이 기록, `docs/STATUS.md`. source/test 변경 0.
- 검수한 source(현재 = run bridge 사본, `cmp` 일치 w r1·s0 r1·s6 r2): `g1_mirror2x.c` `c891909579e48ca5`, `g1_mirror2x.h` `9a519ca64c11befe`, `direct_draw_trace.c` `72ca5455a2cc50f9`, `test_g1_rect_fill.py` `1e45cdc307b37cc0`, `test_g1_panel_layer.py` `e25682da2fcf5528`(sha256 앞 16자, work 기록과 일치). 대조 `q_ctl_r1` bridge `52e6c948…`는 현재 source와 정확히 2줄만 다르다. 두 wrapper(`mirror_blend_clip7`·`mirror_flip_blend`)의 `if (!g_original_…) return 0u;` 바로 뒤에 `return g_original_…(…); /* CONTROL-TEMP */`가 들어 있다. `direct_draw_trace.c`는 같고, 현재 source의 `CONTROL-TEMP`는 0건이다.
- 원본 SHA / 환경 / fixture: 원본 EXE `b56986e0…8ac`(전 run baseline·candidate private EXE 앞 16자 일치, objdump 대상 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` sha 재확인). save000(index 1)·save006, 격리 prefix/display. 활성 인원은 G1과 무관하다.
- 재계산(공유 temp `20261005_lap1038_middle_review/`): `recalc_lap1038.py` `2af55894…ecd4` → `recalc_lap1038.json` `a9524a3b…5b757`.
  - `analyze_q_*.py`·`isect_q.py`·제품 helper를 쓰지 않았다. lap1036 middle 재계산 코드(middle 소유)에서 입력만 바꾸고 `blend_467FD0` 항등식·wrap 계수를 더했다.
  - 입력: lap1037 q_w r1/r2·q_s0 r1/r2·q_ctl_r1·q_s6 r1/r2. 기준은 lap1035 p_w r1/r2·p_s0 r1/r3/r6·대조 p_s0 r7/r8·p_s6 r1/r2.

## 재계산 결과(판정 불일치 0)

| 항목 | 기준(lap1035) | lap1037 work 보고 | lap1038 재계산 |
|---|---|---|---|
| Q-0 항등식 `blend_467FD0` | — | 6 run 성립 | 성립 7/7: w r1·r2·s0 r1 115=103+bounds 12, s0 r2 114=103+11, 대조·s6 0=0. target/size/guard 0. `blend_4678C0` 항등식도 전 run 성립 |
| Q-0 안전 7종·cleanup·source_unchanged·scene·camera·units | — | 0/true/true/true/(39,53)/375 | 동일(save006 units 558). trace JSONL 손상 0 |
| Q-0 tick delta | — | "전 run 400" | w r2·s0·대조 400, **w r1 399**(전사 정정). 판정 영향 없음. w r1 ticks 비 0.9975는 이 1 tick 때문이다. Q-3 대상인 s0 비는 1.000006/0.999999 |
| Q-0 `wrap_calls` | — | 0 | 0(전 run). **범위 정정은 아래 코드 검수 참고** |
| **Q-1** 표본 B stale present | 21 (`0x4680F5` 17·`0x466BB3` 4) | 4 (`0x466BB3`) | **4/4 (`0x466BB3` 4, 값 일치 4)**. 무장 52 라운드·fail 0·좌표 3/3·selftest PASS·dropped/overflow 0 |
| 표본 A / C | 1 / 22 | 1 / 22 | A 1 (`0x46884E`) / C 22 (`0x466BB3` 21·`0x467CCF` 1), 값 일치 100% |
| u A/B/C | 13/37/50 | 13/20/50 | 13/20/50 |
| **Q-2** 마지막40 중앙값 | 40 | 26/26, s0 26/27, 대조 246.5 | w 26/26, s0 26/27, 대조 246.5 |
| **Q-2** 덤프 교집합 r1∩r2 합(39덤프) | 2,954 | 2,064 | w **2,064**(기준 pw 2,954 재현). s0 r1∩r2 3,191 vs 기준 ps0 r1∩r3 5,276. 대조 ctl∩ps0 r7 6,596·∩r8 6,302 vs 기준 대조 r7∩r8 6,136. 고정 군 y455..475×x686..721은 대조 1,375(=기준 대조)이고 w 44·s0 50 |
| **Q-4** save006 r1∩r2 | 38프레임 0 | 39프레임 0·신규 0 | 38프레임 0·39프레임(880 포함, 이번엔 두 run 모두 880 있음) 0·기준 대비 신규 0·제거 0. `blend_467FD0` invocations 0, 마지막40 0/0 |
| `0x466B50` reject_size | 75/76 | 75/76 | w 76/75, s0 76/76, 대조 76 |
| `mirror_details[6600]` 최악 | — | ≈6,141 | 최장 metrics 줄 5,051자 + uint 146개 모두 10자리일 때 +1,090 = **6,141**(s6: 5,023+1,115 = 6,138) < 6,600, 여유 459 |

## Q-3 판정

perf_window 히스토그램 재구성(400 present, nearest-rank):

| run | 미러 | 시작 1분 load | p95 | 평균 ms | ≤7 개수(380 필요) | ≥10 |
|---|---|---|---|---|---|---|
| lap1037 s0 r1 | H-P+H-Q on | 4.22 | 8 | 5.447 | 365 | 12 |
| lap1037 s0 r2 | H-P+H-Q on | 4.47 | 10 | 5.875 | 347 | 25 |
| lap1037 대조 ctl r1 | **둘 다 off(같은 hook)** | 6.67 | 8 | 5.548 | 361 | 11 |
| lap1035 ps0 r1 / r3 / r6 | H-P on | 3.67 / 4.40 / 11.98 | 8 / 7 / 8 | 5.173 / 5.260 / 5.365 | 379 / 380 / 370 | 2 / 6 / 3 |
| lap1035 대조 r7 / r8 | H-P off | 8.63 / 7.83 | 8 / 8 | 5.277 / 5.525 | 377 / 365 | 4 / 5 |
| watch lap1037 w r1 / r2 | on | 3.90 / 5.32 | 12 / 12 | 6.522 / 6.584 | 307 / 302 | 54 / 60 |
| watch lap1035 pw r1 / r2 | H-P on | 3.53 / 3.32 | 11 / 12 | 5.925 / 6.410 | 333 / 307 | 50 / 52 |

- 판정: **Q-3 문자 기준(≤7)은 미달이다. 미러 비용은 검출되지 않았고 원인은 환경 한계(UNKNOWN-환경)로 보아 비차단으로 수용한다.** 근거는 다음과 같다.
  1. 같은 hook에서 미러를 모두 끈 대조가 이번에도 p95 8이다. lap1035 대조 2회와 합쳐 3/3이 8이다. 이 시기 호스트에서는 미러가 없어도 ≤7을 맞추지 못한다.
  2. 후보 s0 r1의 평균 5.447은 대조 5.548보다 낮다. r2의 5.875는 같은 바이너리를 반복 실행할 때의 퍼짐(lap1035 H-P on 6회 평균 5.17~6.84) 안에 있다.
  3. 해석상 비용 상한도 작다. H-Q 호출은 run 전체에서 115회(present당 약 0.28회), 미러 픽셀은 약 22k다. 호출당 50µs로 넉넉히 잡아도 present당 평균 약 0.014ms이므로, 관측된 run 간 평균 차(0.1~0.6ms)보다 한 자릿수 작다.
  4. watch pair의 차이(6.52/6.58 vs 6.0/6.4)는 시작 load 차이(3.9/5.3 vs 3.5/3.3)와 방향이 같고, 위 상한으로는 설명되지 않는다.
- **기준은 바꾸지 않는다.** 다음 work는 후보와 대조를 번갈아(A/B/A/B) 같은 load 구간에서 측정한다. 대조도 >7이면 다시 UNKNOWN-환경으로 기록한다. 이것은 측정 방법 보강이며 gate 완화가 아니다.

## 코드 검수

- `mirror_flip_blend`와 수용된 `mirror_blend_clip7`(H-P)을 이름만 맞춰 줄 단위로 비교했다. 차이는 다음뿐이다: 인자 5개(`remap`·`level` 없음), 원본 호출 인자 5개, `layer_drift_write_end`의 주소 `G1_FLIP_BLEND`, wrap 계수 3줄. 거르기 순서(guard → renderer/대상 → bounds → size → 전용 before 복사), 16비트 부호 확장 4개(lap1036 objdump: x·y·h `movsx`, w는 `movsx bp`), 원본 1회 호출, `g1_overlay_blt_apply`, 실패 시 reject_size 처리는 동일하다. install은 old bytes `83 EC 08 53 56`을 검증하고 restore·installed·reset 목록에 포함된다.
- **범위 정정(비차단):** `wrap_calls`는 mirrored/clipped 분기 **안에서만** 센다. 그래서 reject_bounds(전부 화면 밖이거나 w/h ≤0) 12/11회의 기하는 계측 밖이다. work 기록의 "이 장면에서 화면 밖/행 넘김 호출 없음"은 "**미러 대상 103회 안에서는** 넘김 0"으로 정정한다. 원본은 클립하지 않으므로 그 12회가 넘김을 일으켜도 원본 동작이고, 후보가 더 나빠지지는 않는다. 계수를 bounds 검사 앞으로 옮기는 것은 동작과 무관한 계측 수리이며 H-R에서 함께 해도 된다(선택).
- 테스트 `test_flip_blend_hook_table_and_wrapper_contract`·details pin 6600이 위 계약을 고정한다. 결함은 없다.

## 판정

**H-Q PASS(partial) 수용.** Q-0·Q-1·Q-2·Q-4는 PASS(재계산 불일치 0, 전사 정정 1건 w r1 tick 399)다. Q-3은 환경 한계에 따른 UNKNOWN이며 미러 비용은 검출되지 않았다. 기술 부분수용이고 G1 마일스톤 승인이 아니다.

## 다음 work H-R 사전등록(Sonnet work 1 lap, 제품 변경 + 격리 실행)

목표: 표본 B 4·C 21의 마지막 writer `0x466BB3`(기후킹 `0x466B50`, H-F3 `mirror_flip_rle`)의 reject_size 75/76을 없애서 오른쪽 가장자리 stale을 제거한다.

### 근거(read-only objdump, 원본 SHA 재확인, `od_466B50.txt` `72f57afe…`, 호출처 `od_caller_419F50.txt` `a0f60684…`·`od_caller_41A4FA.txt` `8d6b0140…`)
- `0x466B50`은 x(`[esp+0x14]`)·y(`[esp+0x18]`)·width(`[esp+0x1C]`)·height(`[esp+0x20]`)를 **32비트 DWORD 그대로** 쓴다(`movsx` 없음). 목적지는 `[ecx+0x1514] + y·[ecx+0x10] + x`이고 클립이 없다. 행마다 `x+width-1`부터 왼쪽으로 쓴다. 호출처 2곳은 표에서 읽은 w/h와 호출자 인자 x/y를 그대로 전달한다.
- 현재 `mirror_flip_rle`은 `g1_overlay_blt_accepts`로 **사각형 전체가 [0,800)×[0,600) 안이고 w≤320·h≤160일 때만** 미러한다. 그 밖은 통째로 `reject_size`다. 따라서 오른쪽 가장자리에 걸친 스프라이트(x+w>800, 원본은 800..831 padding에 씀)나 음수 x/y는 화면 안 부분까지 미러되지 않는다.
- 표본 B(766,139)·C(799,315)가 둘 다 오른쪽 가장자리 근처이고, lap1031의 "p352~ 잔여 100% x≥686"과도 맞는다. 가설: **reject_size 75/76의 대부분이 가장자리 걸침이다.** 사각형 크기 초과(>320×160)는 UNKNOWN이다.

### 구현(H-Q 교집합 방식을 `mirror_flip_rle`에 적용, 원본 인자·호출 불변)
- x·y·width·height를 **`(int32_t)` 부호 해석**한다(원본이 32비트이므로 16비트 확장을 쓰지 않는다). 교집합 [max(x,0), min(x+w,800)) × [max(y,0), min(y+h,600))을 계산하고 전용 before 버퍼 `g_flip_rle_before`에 교집합만 복사한 뒤, `g1_overlay_blt_apply`에 교집합 좌표를 넘긴다. 오버플로를 피하려면 64비트로 계산하거나 범위를 먼저 검사한다.
- 교집합이 비면 `reject_bounds`(신규 계수), 교집합이 320×160을 넘으면 `reject_size`, 잘렸으면 `clipped_calls`(신규), x<0·x+w>stride·y<0·y+h>600이면 `wrap_calls`(신규, **모든 유효 대상 호출에서 계측**)로 센다.
- `layer_drift_write_begin/end(…, G1_FLIP_RLE 주소, why, x, y, w, h)`를 추가해서 거부·잘림 기하가 `w` 레코드에 남게 한다(H-Q와 같은 형식).
- 원본 호출은 인자 6개 그대로 1회다. `mirror_details` 길이는 새 키 수 × 약 45자로 재계산한다(현재 여유 459자). 넘으면 `[6600]→[7200]`과 pin을 같이 올린다.
- (선택, 동작 무관) `mirror_flip_blend`의 `wrap_calls` 계측을 bounds 검사 앞으로 옮긴다.
- 테스트 RED→GREEN: 교집합 경계(x+w=801·832·833, x=-1, y+h=601), int32 해석, 원 인자 1회, 신규 계수, details pin.
- 실행 전 `make lint`·`make typecheck`.

### 실행(순차. 각 run 직전 `/proc/loadavg` 기록, 1분 load >8이면 대기)
- save000 watch pair 2회: lap1037 `run_q.sh`의 w와 같은 인자.
- save000 성능: **후보와 대조를 번갈아 2쌍**(A/B/A/B). 대조는 H-P·H-Q·H-R 세 wrapper 미러를 끈 임시 1줄 방식이고, 실행 뒤 source sha 복원과 `CONTROL-TEMP` 0건을 확인한다. 첫 run 전에 1분 load ≤4.5까지 최대 30분 대기한다.
- save006 env-off pair 2회: lap1037 s6와 같은 인자.
- 각 run 뒤 `game` 사본만 삭제한다.

### PASS / FAIL(기준 = lap1037 w r1/r2·s0·s6, lap1038 재계산)
- **R-0**:
  - 항등식 `inv = mirrored + reject_target + reject_bounds + reject_size + reject_guard`(`flip_rle_466B50`, 전 run)가 성립해야 한다.
  - 안전 7종 0, cleanup·source_unchanged, scene_state_equal, camera (39,53), units 375여야 한다.
  - `clipped_calls`·`wrap_calls`·`reject_bounds`와 `w` 레코드 기하를 기록한다(관측).
- **R-1(주 가설)**: `flip_rle_466B50_reject_size` 75/76 → **≤ 5**(남는 몫은 `w` 레코드로 크기 초과임을 보여야 한다). 표본 C stale 22 → **≤ 1**(`0x467CCF` 몫), B 4 → **0**.
  - 미달이면 `w` 레코드의 why/기하로 분류하고, 1회 수리 후 재실행을 허용한다.
- **R-2**: 마지막40 중앙값 < 26, w r1∩r2 덤프 합 < 2,064, 표본 A ≤ 1이어야 한다.
- **R-3**: 성능 후보 p95 ≤7ms·ticks 비 0.999~1.001이어야 한다. 대조도 >7이면 UNKNOWN-환경으로 기록하고, 후보−대조 평균 차를 같이 적는다.
- **R-4**: save006 env-off r1∩r2 38/39프레임 교집합 0·신규 0·p95 ≤8ms. save006 `flip_rle_466B50` 계수 변화도 기록한다(기존 H-F3 수용 장면).
- 금지: gate·validator·기준·`G1_OVERLAY_MAX_*` 변경, 원본/raw 수정, H-R 대상 밖 hook의 동작 변경.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산·read-only 검수만 했다. 게임/source/commit은 0이다. focused 검사·SAFETY 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1037 full PASS 1628 `logs/gates/lap1037-work-full-check.log`).
- 남은 위험:
  - 표본이 3점뿐이다.
  - `0x467FD0` reject_bounds 12/11회의 기하를 모른다(위 범위 정정).
  - H-R은 기존 수용 hook(H-F3)의 거르기를 넓히므로 save006(H-F3 961→0 장면) 비회귀가 필수다.
  - Q-3은 환경 UNKNOWN이 3 lap 연속이다(대조도 8).
- backlog: `0x46884E`(A 1), save006 짧은 run 꼬리, hold keydown 위상, 가장자리 마우스 스크롤, wrap 쓰기, overlay BltFast rejects, 다중 팝업 heal.
- 사용자 승인 상태: 기술 부분수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-R(위 사전등록).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1037 work, 1,322 B, SHA256 `f5293f899a82b93011a0511405b4f4966c2ca42ddab44e70471e58b1f7854458`)

```
lap1037 (Claude Code claude-sonnet-5-5, work) — H-Q 구현·실행 완료, 독립 검수(middle) 필요. 자가 승인 금지.

한 일: 미후킹 0x467FD0(old bytes 83 EC 08 53 56, ret 0x14, 클립 없음·좌우 반전 혼합 RLE) diff 미러 mirror_flip_blend + 계수 blend_467FD0_* 10개(wrap_calls 포함) + mirror_details 6000→6600. 계약 테스트 RED→GREEN, lint·typecheck PASS.
결과(기록 docs/history/laps/20261005_lap1037_work_g1_hq_flip_blend_467fd0_diff_mirror.md): Q-0 항등식 6/6·안전0·wrap_calls 0, Q-1 표본 B stale 21→4(0x4680F5 17→0, 남은 4=0x466BB3), Q-2 마지막40 중앙값 40→26·r1∩r2 합 2,954→2,064(대조 246.5), Q-4 save006 39프레임 0·신규 0·p95 8/8.
미결(Q-3 성능): 성능 pair p95 8/10(load 4.2~4.5), 미러 둘 다 끈 대조 p95 8(load 6.7) — 문자 그대로 ≤7 미달, 미러 비용 분리 불가(UNKNOWN-환경).
승격 작업자가 이어서 할 일: (1) 공유 temp 20261005_lap1037_work_hq/ 의 pair-result·trace_raw·layer_drift·screen_watch·stale_mask를 analyze_q_*.py·isect_q.py 없이 새 스크립트로 재계산, (2) Q-3 판정(히스토그램 평균 비교·수용/저부하 재측정), (3) mirror_flip_blend 코드 검수, (4) 수용 시 다음 work 사전등록(0x466B50 reject_size 75/76 → B 4·C 21 writer, 0x46884E).
```
