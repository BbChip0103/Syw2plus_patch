# 2026-10-05 | lap1034 | G1 middle — H-O 귀속 독립 검수(FEASIBLE 수용) → work H-P(`0x4678C0` diff 미러) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간 계획·컨펌) 1 lap. 게임 실행·source 변경·커밋은 0이다. lap1033 work(Sonnet)가 만든 `loop/ESCALATE_SOL`을 처리하고 삭제했다(원문은 부록).
- 가설: lap1032 work H-O 귀속(표본 A `0x4678C0` 77/78, B `0x467FD0` 17/21, C 기후킹 `0x466B50` 21/22)이 raw와 원본 역어셈블에서 재현되는가.
- 예상 PASS / FAIL 조건: 새 스크립트로 재계산했을 때 판정에 영향을 주는 불일치가 0이어야 한다. 두 함수는 원본 objdump로 hook 가능(시작 5바이트 명령 경계, 내부 분기 대상 아님)해야 한다. bridge 사본은 현재 source와 같아야 한다.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제. 공유 temp `20261005_lap1034_middle_review/`(모두 uncommitted):
  - `recalc_lap1034.py` `66f049c6…b557` → `recalc_lap1034.json` `02216fac…03e5`(입력 JSONL 6개 SHA 포함)
  - objdump(read-only 원본): `od_4678C0.txt` `29d91f18…`, `od_467FD0.txt` `4fbaa954…`, `od_46884E.txt` `915b3434…`, `od_callers_A.txt` `a90dcc9e…`, `od_callers_B1.txt` `ab45ef78…`, `od_callers_B2.txt` `1e30e6e1…`
- 원본 SHA / fixture: 원본 EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` sha256 `b56986e0…8ac` 직접 재확인. save000 `1c703551…`(index 1) pair 2회(lap1032 o_s0_r1/r2). 활성8인 부하 증명은 아니다.
- 검수한 source: 현재 `g1_mirror2x.c` `23667cc8…`, `direct_draw_trace.c` `d7b33b84…`, `g1_screen_watch.c` `df2a2360…` = o_s0_r1/r2 bridge 사본과 같다. 현재 source에 `0x4678C0`·`0x467FD0` hook 정의는 없다(`G1_FLIP_RLE 0x466B50`·`G1_BLEND_CLIP 0x467B00`은 있음).

## 1. 독립 재계산(`analyze_o.py`·제품 helper 미사용)

work 분석과 다르게 계산했다.
- stale present는 trace PS3 present 수 N으로 0..N−1을 만들고 `s` 레코드를 앞으로 채워 셌다. 최대 drift p(409/410)와 맞는지도 확인했다. `e` 레코드는 50 present마다 찍히는 heartbeat라서 present 목록으로 쓰지 않았다.
- 마지막 writer는 "값이 맞는 마지막 hit"(work 방식)가 아니라 **그 present 이전의 마지막 hit 자체**로 잡았다. 그 뒤 값이 화면 값과 같은지 따로 확인했다(더 엄격함).
- 무장 주소를 `m` 레코드의 buffer·stride로 화면 좌표로 되돌렸다. `k` 레코드의 dropped·overflow 합도 확인했다.

| 항목 | work | 재계산(r1 / r2) |
|---|---|---|
| JSONL 손상 | 0 | screen_watch·layer_drift·trace 0/0/0 |
| selftest·무장 | PASS·52라운드 fail 0 | PASS·52/52 fail 0·주소 집합 1개 → (695,468)(766,139)(799,315) 3/3 |
| watch 손실 | (미기재) | dropped 0·overflow 0 |
| 마지막40 stale 중앙값 | 246.5/246.5 | 246.5/246.5 (PS3 present 410/411) |
| 안전 7종 | 0 | 0, pair HOLD(기존 V2s), scene_state_equal true |
| `u` 귀속 | 33/37/50 = 100% | 같은 present의 hit 값 일치 33/33·37/37·50/50, **마지막 hit만 봐도 100%** |
| A stale present | 78, 77 `0x467ABA` + 1 `0x46884E` | 78(p203..395), **77 `0x467ABA`(복귀 `0x41A9A4`) + 1 `0x46884E`(복귀 `0x41A195`)**, 값 일치 78/78 |
| B stale present | 21, 17 `0x4680F5` + 4 `0x466BB3` | 21(p185..378), **17 `0x4680F5`(복귀 `0x41A0D2`) + 4 `0x466BB3`(복귀 `0x41A4FF`)**, 값 일치 21/21 |
| C stale present | 22, 21 `0x466BB3` + 1 `0x467CCF` | 22(p8..369), **21 `0x466BB3`(복귀 `0x419F55`) + 1 `0x467CCF`(복귀 `0x41A072`)**, 값 일치 22/22 |
| `0x466B50` 계수 | inv 777·mirrored 702·reject_size 75 | r1 777/702/**75**·r2 780/704/**76**, target·guard 0 |

**판정에 영향을 주는 불일치는 0이다.** 전사 보정: work는 reject_size를 r1 값 75로만 적었다. r2는 76이다(lap1011 "save000 신규 76"과 같은 수준). 보강: B의 `0x466BB3` 4건은 C와 다른 호출처 `0x41A4FF`(= `call 0x466b50` @`0x41A4FA`)에서 왔다. 즉 `0x466B50` 호출처 2곳이 모두 stale에 관여한다.

## 2. 정적 검수(read-only objdump, 원본 SHA 일치)

- **`0x4678C0`(표본 A)**
  - 시작 `83 EC 18`(sub esp,0x18) + `33 C0`(xor eax,eax) = 정확히 5바이트·명령 경계다. 전체 .text에서 `0x4678C1..C4`로 가는 분기는 0이다.
  - `ret 0x1c`(`0x467AFC`), thiscall이다. 인자 7개 = x(+4)·y(+8)·w(+0xC)·h(+0x10)를 16비트 movsx로 읽고, rle(+0x14)·remap 표(+0x18)·level(+0x1C, 16비트, `shl 6`)을 받는다.
  - 목적지 = `[ecx+0x1514] + y*[ecx+0x10] + x` = `G1_RENDERER_BUFFER`/`STRIDE`다. 클립은 `[ecx+0x4D0]`(좌)·`+0x4D4`(상)·`+0x4D8`(우)·`+0x4DC`(하)이고, 사각형이 클립 밖이면 쓰기 없이 반환한다. 행·열 skip으로 클립 안만 쓴다.
  - RLE `0xFE n` = n픽셀 건너뛰기다. 쓰기는 `0x467AB7 mov [edi+esi],dl` 1곳뿐이며 목적지 픽셀을 읽어(`0x467A00`) 팔레트 혼합 표로 섞는다(목적지 의존).
  - 호출은 2곳(`0x41A827`·`0x41A99F`)이고 둘 다 `mov ecx,0xE5BF18`(= `G1_RENDERER_VA`)이다. 형제 `0x467410`(관측 hook, 7인자 `ret 0x1C`)과 인자 모양이 같고, `0x467B00`(H-B4)과는 클립·혼합 구조가 같다.
- **`0x467FD0`(표본 B)**
  - 시작 `83 EC 08`·`53`·`56` = 5바이트·명령 경계다. `0x467FD1..D4`로 가는 분기는 0이다.
  - `ret 0x14`(`0x468131`), 인자 5개 x·y·w·h(16비트)·rle다.
  - **클립이 없다.** 열 위치 `w−1−col`로 좌우를 뒤집어 그린다. RLE `0xFE` 건너뛰기가 있고, 쓰기는 `0x4680F3 mov [edi],dl` 1곳이며 목적지 의존 혼합이다.
  - 호출은 2곳(`0x41A0CD`·`0x41AC95`)이고 ecx = `0xE5BF18`이다.
- **`0x46884E`**: `0x468800` 앞에서 시작하는 다른 RLE 재매핑 writer다(목적지 `[ecx+0x1514]`, `mov [eax+edx-1],cl` @`0x46884A`). A의 1건뿐이라 backlog로 둔다.
- 결론: **H-O FEASIBLE 수용.** 두 함수 모두 hook할 수 있다. A가 stale present 98.7%를 단일 함수로 설명하므로 먼저 수리한다.

## 3. 판정

**H-O O-0·O-1 PASS·O-2 FEASIBLE 수용(진단, 제품 동작 불변).** `rect_solid_details[340]→[360]` 부수 수리는 lap1031 §3 허가 범위 그대로다(지역 스택 문자열, 동작 불변). 그래서 save006 비회귀 run을 생략한 판단도 수용한다.

## 4. 다음 work H-P 사전등록(Sonnet work 1 lap, 제품 변경 + 격리 실행)

목표: 미후킹 `0x4678C0`을 diff 미러해서 표본 A의 stale을 없앤다. 한 바퀴 한 가설이므로 `0x467FD0`(B)과 `0x466B50` reject는 다음으로 미룬다.

### 4.1 구현(`mirror_blend_clip` 동형)
- `#define G1_BLEND_CLIP7 0x004678C0u`, old bytes `83 EC 18 33 C0` 검증 install/restore를 추가하고, installed·reset 목록에 넣는다. 원본 포인터는 `G1Primitive7Fn`이다.
- wrapper `mirror_blend_clip7(renderer, a_x, a_y, a_w, a_h, rle, remap, level)`:
  - x·y·w·h는 `(int16_t)`로 부호 확장한다.
  - 거르기 순서는 `renderer == G1_RENDERER_VA` → guard → 대상 버퍼(`mirror_blend_clip`과 같은 조건) → bounds(화면 [0,800)×[0,600) 교집합, 비면 reject_bounds) → 크기(교집합 > `G1_OVERLAY_MAX_WIDTH`×`HEIGHT`면 reject_size) → 전용 before 버퍼 `g_blend_clip7_before` 복사다.
  - 원본은 **원 인자 7개 그대로** 1회만 호출한다. 그 뒤 `g1_overlay_blt_apply`를 실행하고, 실패하면 reject_size로 센다.
  - 화면 교집합은 원본 클립 사각형보다 넓은 상위집합이다(H-B4와 같은 논리). 클립을 다시 구현하지 않는다.
- `layer_drift_write_begin/end(…, G1_BLEND_CLIP7, why, x, y, w, h)` 호출을 넣어 `w` 레코드에 크기·사유가 남게 한다. 그래야 reject 사각형 크기가 UNKNOWN으로 남지 않는다.
- 계수 9개 `blend_4678C0_{invocations,mirrored_calls,mirrored_pixels,changed_calls,clipped_calls,reject_target,reject_bounds,reject_size,reject_guard}`의 getter와 `direct_draw_trace.c` 출력을 추가한다.
- **`mirror_details[5400]`(2곳) → `[6000]`**: lap1031 §3에서 최악 5,386자로 여유가 얇다고 했다. 이번에 9키(약 420자, 10자리 최악)를 더하면 약 5,806자가 된다. `tests/test_g1_panel_layer.py:115` pin 기대값도 같이 고친다.
- 테스트 RED→GREEN:
  - 주소·old bytes·`ret 0x1c` 인자 수 계약
  - 16비트 부호 확장
  - 원 인자 그대로 전달
  - 계수 키 9개 출력
  - details 버퍼 크기 pin
- `make lint`·`make typecheck` → focused 테스트를 실행한다. lap 기록을 먼저 쓰고, 그다음 `make check` 1회를 돌린다.

### 4.2 실행(성능 gate 전 `/proc/loadavg`, 1분 load > 8이면 대기, 순차)
- save000 pair 2회. lap1032 `run_o.sh`와 같은 인자를 쓴다: `--fixture save000 --scene-actions none --performance-window --layer-drift --screen-watch --drift-samples "695,468;766,139;799,315" --stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`
- save000 성능 pair 2회는 watch 없이 돌린다(`--layer-drift`·`--screen-watch` 없음). watch run의 p95(11ms)는 gate가 아니기 때문이다.
- save006 env-off 비회귀 pair 2회를 기존 lap1030 형식으로 돌린다.
- 실행 뒤 `game` 사본만 삭제한다.

### 4.3 PASS / FAIL(기준값 = lap1032 o_s0_r1/r2, 이번 재계산)
- **P-0**:
  - 계수 항등식 `inv = mirrored + reject_target + reject_bounds + reject_size + reject_guard`가 성립해야 한다(4 run).
  - 안전 7종 0, cleanup·source_unchanged true, scene_state_equal, camera (39,53), units 375여야 한다.
  - `blend_4678C0_invocations > 0`이어야 한다(save000).
- **P-1(주 가설)**: 표본 A stale present 중 마지막 writer가 `0x467ABA`인 것이 77 → **0**이어야 한다(2 run 모두). A 전체 stale present는 ≤ 1이어야 한다(남는 1은 `0x46884E` 몫).
  - 미달이면 A 쪽 `w` 레코드의 `why`로 원인을 분류한다(reject_size/bounds/target). 1회 수리 후 재실행을 허용한다.
- **P-2**:
  - 마지막40 stale 중앙값 < 246.5여야 한다(감소량을 기록한다).
  - stale-mask 고정 군 y455..475×x686..721의 r1∩r2 덤프 합이 기준보다 줄어야 한다.
  - 표본 B·C stale은 늘지 않아야 한다(21/22 이하).
- **P-3**: 성능 pair에서 candidate p95 ≤ 7ms(기준 7/7)·ticks 비 0.999~1.001이어야 한다.
- **P-4**: save006 env-off r1∩r2에서 38·39프레임 교집합 0을 유지해야 하고, 신규 stale 0·p95 ≤ 8ms여야 한다.
- 금지: gate·validator·기준·`G1_OVERLAY_MAX_*` 변경, 원본/raw 수정, 다른 hook 동작 변경.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산·read-only objdump만 했다. 게임/source/commit은 0이다.
- 전체 `make check`는 SKIP했다. source가 불변이고 lap1032 full PASS 1626(`logs/gates/lap1032-work-full-check.log`, exit 0)이 유효하다. focused 검사 결과는 STATUS에 보강한다.
- 남은 위험:
  - 표본은 3점뿐이다. 이동 스프라이트 stale 전체를 대표하지 않는다.
  - `0x4678C0` 사각형 크기 분포는 미관측이다. 320×160을 넘는 호출이 많으면 P-1이 reject_size로 미달할 수 있고, 그래서 `w` 레코드 계측을 넣는다.
  - `0x467FD0`은 클립이 없다. 화면 오른쪽 밖 wrap 쓰기 가능성이 있어 다음 H-Q에서 범위를 확인해야 한다.
- backlog:
  - H-Q `0x467FD0`(B 17/21)
  - `0x466B50` reject_size 75/76(호출처 `0x419F50`·`0x41A4FA` 모두 관여, 사각형 크기 계측 필요)
  - `0x46884E`
  - 기존 backlog(save006 짧은 run 꼬리·hold keydown 위상·가장자리 마우스 스크롤·wrap 쓰기·overlay BltFast rejects·다중 팝업 heal)
- 사용자 승인 상태: 기술 검수일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-P(위 §4).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1033 work, 1,464 B, SHA256 `f9f299e616c890e2b14fbeb8ff91428feeefe38b979b6273707f3022ca33ceec`)

```
lap1033 (Claude Code claude-sonnet-5-5, work 역할) — 중간 tier 검수 필요로 승격, 코드·게임 변경 0.

사유: STATUS "다음 한 가지"가 lap1033 = middle 검수 → 그 뒤 work H-P로 못 박혀 있다.
lap1032 H-O 귀속(A 0x4678C0 77/78, B 0x467FD0 17/21, C 기후킹 0x466B50 reject_size 75)은
같은 work 계열이 만든 결과라 독립 검수 전에 H-P(0x4678C0 diff 미러 구현)를 시작하면
작성자 자가 승인이 된다. 작업자는 중간 확인을 추측하지 않는다(PROMPT ④-3, 새 세션 지시).

승격 작업자(Opus middle)가 이어서 할 일:
1. docs/history/laps/20261005_lap1032_work_g1_ho_right_stale_writer_attribution.md의 귀속 수치를
   제품 helper·analyze_o.py 없이 새 스크립트로 재계산(공유 temp 20261005_lap1032_work_ho/ 의
   analysis_o.json SHA 1f223710…, run_o.sh SHA 0198dfbe…, logs/gates/lap1032_ho_s0_r{1,2}.log).
2. 원본 EXE(b56986e0…8ac, read-only) objdump로 0x4678C0(ret 0x1c, 클립 [ecx+0x4D0/0x4D4], 시작 5바이트
   83 EC 18 33 C0)·0x467FD0(ret 0x14, 시작 5바이트 83 EC 08 53 56) 검수, hook 순서(A 우선) 확정.
3. 수용 시 work H-P 사양 확정: 0x4678C0 diff 미러(mirror_blend_clip 동형) + reject 계측, save000 pair +
   save006 비회귀로 표본 A stale 78→0·마지막40 중앙값 감소 측정.
기억할 한계: 표본 3점뿐, A의 1건 0x46884E·B/C 소수 writer는 미조사, 변경 전부 uncommitted 보존.
```
