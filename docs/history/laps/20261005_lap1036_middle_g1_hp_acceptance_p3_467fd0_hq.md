# 2026-10-05 | lap1036 | G1 middle — H-P 독립 검수(P-3 판정 포함) → work H-Q 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·source 변경·commit 0.
- 가설 / 검수 대상: lap1035 work H-P(`0x4678C0` diff 미러 `mirror_blend_clip7`)의 P-0~P-4 수치가 raw에서 재현되는가, P-3(성능 p95 ≤7ms) 미달이 미러 비용인가 호스트 환경인가.
- 예상 PASS / FAIL 조건: lap1034 §4.3 사전등록 그대로(기준·gate 무변경).
- 처리한 인계: `loop/ESCALATE_SOL`(lap1035 work, 1,142 B, SHA256 `9ebe3a9e1b9ba722662f6a8d40ec4381a5c02425d5bccecee8250fa233b10d87`) 원문은 아래 부록, 처리 뒤 삭제.
- 변경 파일: 이 기록, `docs/STATUS.md`(압축 포함), `docs/history/20261005_status_lap1036_precompaction.md`(STATUS 원문 보존). source/test 변경 0.
- 검수한 source(현재 = run bridge 사본): `g1_mirror2x.c` `c7f73d167f6d0f70`, `g1_mirror2x.h` `3af67c949b6e5871`, `direct_draw_trace.c` `6d296b9ba5bb7ce2`, `test_g1_rect_fill.py` `e7f48d01a3b38fd6`, `test_g1_panel_layer.py` `3184d7debb0918b4`(sha256 앞 16자, work 기록과 일치). 대조 r7·r8 bridge `17237d3f…`는 현재 source와 정확히 1줄(`return g_original_blend_clip7(...) /* CONTROL-TEMP */`) 차이만 있다.
- 원본 SHA / 환경 / fixture: 원본 EXE `b56986e0…8ac`(전 run baseline·candidate private EXE 앞 16자 일치), save000(index 1)·save006, 격리 prefix/display, 활성 인원 무관(G1).
- 재계산(공유 temp `20261005_lap1036_middle_review/`): `recalc_lap1036.py` `b284061c…dd88`(`analyze_p_s*.py`·제품 helper 미사용) → `recalc_lap1036.json` `70407b21…beec`. 입력 = lap1035 w r1/r2·s0 r1~r8·s6 r1/r2, 기준 lap1032 o_s0_r1/r2·lap1030 n_s0/n_s6 r1/r2. work와 다른 방법: p95·평균을 `perf_window_histogram` 400-present 분포에서 직접 재구성(nearest-rank)하고 ≤7ms 개수 여유를 셈, 표본 stale은 각 PS3 present에서 직전 `s` 상태·직전 watch hit로 판정, 마스크 교집합은 두 run 공통 덤프 순번에서 계산.

## 재계산 결과(불일치 0)

| 항목 | 기준 | lap1035 work 보고 | lap1036 재계산 |
|---|---|---|---|
| P-0 항등식 `blend_4678C0` | — | 8 run 성립 | 성립 12/12(w 263=184+79·261=182+79, s0 263/261/192 동형, 대조 r7·r8 0=0, s6 50·48 = bounds) |
| P-0 안전 7종·cleanup·source_unchanged·scene·camera·units·tick | — | 0/true/true/true/(39,53)/375/400 | 동일(s0 r2만 tick 394·PS3 293 = 짧은 run) |
| P-1 표본 A stale present | 78 (`0x467ABA` 77·`0x46884E` 1) | 1 (`0x46884E`) | **1/1 (`0x46884E` 1, 값 일치 1)**, 무장 52 라운드 fail 0·좌표 3/3·selftest PASS·dropped/overflow 0 |
| 표본 B / C | 21/22 | 21/22 | 21 (`0x4680F5` 17·`0x466BB3` 4) / 22 (`0x466BB3` 21·`0x467CCF` 1), 값 일치 100% |
| u A/B/C | 33/37/50 | 13/37/50 | 13/37/50 |
| P-2 마지막40 중앙값 | 246.5/246.5 | 40/40 | w 40/40, s0 r1·r3·r4·r5·r6 40, r2 144.5(짧은 run), 대조 r7·r8 246.5 |
| P-2 고정 군 y455..475×x686..721 r1∩r2 39덤프 합 | 1,375 | 18 | w 18, s0 r1∩r3 50·r3∩r4 50·r5∩r6 0, 대조 r7∩r8 1,375(=기준) |
| 덤프 교집합 전체 합 | 7,532 | 2,954 | w 2,954(덤프 중앙값 29→0), 대조 6,136·lap1030 6,602 |
| P-4 save006 38프레임 r1∩r2 | 0(lap1030) | 0·신규 0 | 0·신규 0·제거 0, r1 단독 38프레임 0. r1에 프레임 880 부재(짧은 run 879 present·마지막40 1,179.5 꼬리 = 기존 backlog 변형)라 39프레임은 38로 계산 |
| `0x466B50` reject_size | 75/76 | 75/76 | w 75/75, s0 76(r2 54) |

## P-3 판정

perf_window 히스토그램 재구성(400 present, nearest-rank p95; ≤7 개수 = 380 이상이면 p95 ≤7):

| run | 미러 | 시작 1분 load | p95 | 평균 ms | ≤7 개수 | ≥10 개수 |
|---|---|---|---|---|---|---|
| lap1030 n r1 / r2 | 없음(H-P 전) | 2.56 / 4.11 | 7 / 7 | 5.055 / 5.025 | 387 / 393 | 1 / 1 |
| lap1035 s0 r1 | on | 3.67 | 8 | 5.173 | **379** | 2 |
| s0 r3 | on | 4.40 | 7 | 5.260 | 380 | 6 |
| s0 r4 | on | 4.14 | 11 | 6.248 | 324 | 31 |
| s0 r5 | on | 5.73 | 13 | 6.844 | 294 | 56 |
| s0 r6 | on | 11.98 | 8 | 5.365 | 370 | 3 |
| s0 r2 | on | 4.13 | 29 | 14.343 | 101/280 | 164 (load outlier) |
| 대조 r7 / r8 | **off(같은 hook)** | 8.63 / 7.83 | 8 / 8 | 5.277 / 5.525 | 377 / 365 | 4 / 5 |
| watch 기준 lap1032 o r1 / r2 | 없음 | 2.95 / 3.02 | 11 / 11 | 6.420 / 5.973 | 308 / 327 | 51 / 49 |
| watch lap1035 w r1 / r2 | on | 3.53 / 3.32 | 11 / 12 | 5.925 / 6.410 | 333 / 307 | 50 / 52 |

- 판정: **P-3 문자 기준(≤7) 미달은 미러 비용이 아니라 측정 환경 한계로 판정, 비차단(UNKNOWN-환경)으로 수용.** 근거: (1) 같은 hook에서 미러만 끈 대조 r7·r8도 p95 8/8이다. 이 시간대 호스트에서는 미러 유무와 상관없이 ≤7을 못 맞춘다. (2) 미러 on 최선 3회(r1·r3·r6)의 평균 5.17~5.37은 대조 평균 5.28~5.53보다 낮거나 같다. (3) 부하가 lap1032 기준과 가장 비슷한 watch pair 비교(load 3.3~3.5 vs 2.95~3.0)에서 평균 5.93/6.41 vs 6.42/5.97, p95 11/12 vs 11/11로 차이를 검출하지 못했다. (4) p95=7 경계는 400개 중 1개 차이다(lap1030 여유 7~13개, r1은 1개 부족). (5) ticks 비는 r2 외 전부 0.99998~1.000005다.
- 그래도 **기준을 바꾸지 않는다**. ≤7 재확인은 다음 work H-Q의 성능 pair에 포함한다(§H-Q Q-3). 저부하 조건을 충족하는 시점에 누적 후보(H-P+H-Q)로 측정한다.
- 절차 이탈(정정 기록): lap1034 §4.2는 "1분 load > 8이면 대기"였다. 그런데 r6(11.98)·r7(8.63)은 대기 없이 시작했다. 결론은 바뀌지 않는다(r6 p95 8·평균 5.37). 다음 work는 이 규칙을 지킨다.

## 코드 검수

- `mirror_blend_clip7`는 수용된 `mirror_blend_clip`(H-B4)과 줄 단위로 비교했을 때 차이가 다음뿐이다: 이름, 인자 2개(`remap`·`level`) 추가, 원본 호출 인자 7개. 거르기 순서(guard → renderer/대상 → bounds → size → 전용 before 복사), 16비트 부호 확장 4개, 원본 1회 호출, `g1_overlay_blt_apply`, 실패 시 reject_size 처리는 동일하다. thiscall 7 DWORD = `ret 0x1c`와 일치한다(`G1Primitive7Fn` 기존 typedef, `0x467410` 관측 hook과 공유). install은 old bytes `83 EC 18 33 C0`를 검증하고 restore·installed·reset 목록에 포함된다. diff 전문 `diff_g1_mirror2x_lap1032_to_now.txt` `909748d2…6b96b`.
- `mirror_details[6000]`: 최장 metrics 줄 4,734자, uint 136개가 모두 10자리가 되는 최악 증가는 +1,012자, 합계 5,746 < 6,000이다(여유 254). **다음 hook 9키(약 420자)를 더하면 최악 길이가 6,000을 넘는다** → H-Q에서 `[6000]→[6600]`(2곳)과 pin을 같이 올린다.
- 테스트 `test_blend_clip7_hook_table_and_wrapper_contract`: 주소·old bytes·원 인자 1회·before→원본→apply 순서·분리 버퍼·계수 9키·reset을 계약으로 고정한다. 확인 결과 결함은 없다.

## 판정

**H-P PASS(partial) 수용.** P-0·P-1·P-2·P-4는 PASS(재계산 불일치 0)이고, P-3은 환경 한계에 따른 UNKNOWN이며 미러 비용은 검출되지 않았다. Q-3에서 다시 확인한다. 기술 부분수용이며 G1 마일스톤 승인이 아니다.

## 다음 work H-Q 사전등록(Sonnet work 1 lap, 제품 변경 + 격리 실행)

목표: 미후킹 `0x467FD0`을 diff 미러해서 표본 B(766,139)의 stale을 없앤다. 대상은 마지막 writer `0x4680F5` 17/21이다.

### 정적 근거(read-only objdump, lap1034 `od_467FD0.txt` `4fbaa954…`, 이번 재독해)
- thiscall `ret 0x14`, 인자는 entry 기준 `[esp+4]`=x, `[esp+8]`=y, `[esp+0xC]`=w, `[esp+0x10]`=h, `[esp+0x14]`=rle다. x·y·h는 `movsx` 16비트로 읽는다. w는 DWORD로 적재한 뒤 `movsx bp`로 16비트로 쓴다.
- 목적지 = `[ecx+0x1514]` + y·`[ecx+0x10]` + x. 행마다 열 esi 0..w−1에 대해 `edi = 행시작 + (w−1−esi)`에 쓴다(좌우 반전, `0x4680F3 mov [edi],dl`). RLE `0xFE`는 skip, 목적지 의존 룩업 혼합, h행이다.
- **클립이 없다.** 그래서 쓰기 범위는 정확히 [x, x+w)×[y, y+h)다. 화면 stride는 832(`screen_watch` m 레코드)라서, x+w가 800~832 사이면 화면 밖 padding에 쓰고, x<0 또는 x+w>832이면 이웃 행으로 넘어간다(wrap).
- 시작 5바이트는 `83 EC 08 53 56`(sub esp,8 / push ebx / push esi)로 명령 경계가 맞고 상대 분기가 없다. 호출처는 `0x41A0CD`·`0x41AC95` 2곳이다(lap1034 `od_callers_B1/B2`).

### 구현(`mirror_blend_clip` 동형, 5인자)
- `#define G1_FLIP_BLEND 0x00467FD0u`, `_LEN 5u`, old bytes `{0x83, 0xEC, 0x08, 0x53, 0x56}`. install/restore/installed/reset을 추가한다. 원본 포인터는 기존 5인자 `G1PrimitiveFn`을 쓴다.
- wrapper `mirror_flip_blend(renderer, a_x, a_y, a_w, a_h, rle)`: x·y·w·h를 `(int16_t)`로 부호 확장한다. 거르기 순서는 H-P와 같다. 화면 [0,800)×[0,600) 교집합 diff를 미러하고, 전용 before 버퍼 `g_flip_blend_before`를 쓴다. 원 인자 5개를 그대로 1회 전달하고 `layer_drift_write_begin/end(…, G1_FLIP_BLEND, why, x, y, w, h)`를 넣는다.
- **wrap 계측**: x<0 또는 x+w>stride인 호출은 `flip_blend_wrap_calls`로 센다. 미러는 화면 교집합만 하고, 넘어간 픽셀은 이번 범위 밖이다(현재보다 나빠지지 않음). y<0 또는 y+h>600도 같은 계수에 포함한다.
- 계수 10개는 `blend_467FD0_{invocations,mirrored_calls,mirrored_pixels,changed_calls,clipped_calls,reject_target,reject_bounds,reject_size,reject_guard,wrap_calls}`다. getter와 `direct_draw_trace.c` 출력을 추가한다.
- **`mirror_details[6000]`(2곳) → `[6600]`**, `tests/test_g1_panel_layer.py` pin도 같이 바꾼다(위 최악 길이 계산 근거).
- 테스트 RED→GREEN:
  - 주소·old bytes·5인자
  - 원 인자 그대로 1회 전달
  - 16비트 부호 확장
  - 분리 버퍼
  - 계수 10키
  - wrap 계수 조건
  - details pin
- 실행 전 `make lint`·`make typecheck`를 통과시킨다.

### 실행(순차. 각 run 직전 `/proc/loadavg` 기록, **1분 load > 8이면 대기**)
- save000 watch pair 2회: lap1035 `run_p.sh`의 w와 같은 인자(`--layer-drift --screen-watch --drift-samples "695,468;766,139;799,315" --stale-mask …`).
- save000 성능 pair 2회: lap1035 s0와 같은 인자(`--layer-drift`, screen-watch 없음). **Q-3용으로 1분 load ≤ 4.5까지 최대 30분 대기한 뒤 시작**하고, 대기 결과와 load를 기록한다.
- save006 env-off pair 2회: lap1035 s6와 같은 인자.
- 각 run 뒤 `game` 사본만 삭제한다.

### PASS / FAIL(기준값 = lap1035 w r1/r2·s0·s6, lap1036 재계산)
- **Q-0**:
  - 항등식 `inv = mirrored + reject_target + reject_bounds + reject_size + reject_guard`(전 run)가 성립해야 한다.
  - 안전 7종 0, cleanup·source_unchanged, scene_state_equal, camera (39,53), units 375여야 한다.
  - save000 `blend_467FD0_invocations > 0`이어야 한다.
  - `wrap_calls` 값을 기록한다(판정이 아니라 관측).
- **Q-1(주 가설)**: 표본 B stale present 중 마지막 writer `0x4680F5` 17 → **0**이어야 한다(2 run). B 전체는 ≤ 4여야 한다(`0x466BB3` 몫).
  - 미달이면 `w` 레코드 `why`로 분류한다(wrap/size/bounds/target). 1회 수리 후 재실행을 허용한다.
- **Q-2**:
  - 마지막40 중앙값 ≤ 40이어야 한다(감소량을 기록한다).
  - w r1∩r2 덤프 합이 2,954 이하여야 한다.
  - 표본 A ≤ 1, C ≤ 22를 유지해야 한다.
- **Q-3**: 성능 pair candidate p95 ≤ 7ms·ticks 비 0.999~1.001이어야 한다(H-P P-3 재확인 포함).
  - 미달이면 같은 세션에서 H-P·H-Q 미러를 함께 끈 대조 1회를 바로 이어 측정한다(lap1035 대조 방식: 임시 1줄, 실행 뒤 source sha 복원 확인).
  - 대조도 >7이면 환경 UNKNOWN으로 기록한다.
- **Q-4**: save006 env-off r1∩r2 38(39)프레임 교집합 0·신규 0·p95 ≤ 8ms여야 한다.
- 금지: gate·validator·기준·`G1_OVERLAY_MAX_*` 변경, 원본/raw 수정, 다른 hook 동작 변경.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산·read-only 검수만 했다. 게임/source/commit은 0이다. focused 검사·SAFETY 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1035 full PASS 1627 `logs/gates/lap1035-work-full-check.log`).
- 남은 위험:
  - 표본이 3점뿐이다.
  - `0x4678C0`의 두 번째 호출처 `0x41A99F` 경로는 관측으로만 확인했다.
  - `0x467FD0`의 wrap 빈도를 모른다(Q-0에서 계측).
  - save006 짧은 run 꼬리(r1 879 present)가 반복된다(기존 backlog).
- backlog:
  - `0x466B50` reject_size 75/76(B 4·C 21의 writer, 사각형 크기는 `w` 레코드로 계측)
  - `0x46884E`(A 1)
  - 기존 항목: save006 짧은 run 꼬리·hold keydown 위상·가장자리 마우스 스크롤·wrap 쓰기·overlay BltFast rejects·다중 팝업 heal
- 사용자 승인 상태: 기술 부분수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-Q(위 사전등록).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1035 work, 1,142 B, SHA256 `9ebe3a9e1b9ba722662f6a8d40ec4381a5c02425d5bccecee8250fa233b10d87`)

```
lap1035 (Claude Code claude-sonnet-5-5, work) — H-P 구현·실행 완료, 독립 검수(middle) 필요. 자가 승인 금지.

한 일: 미후킹 0x4678C0(old bytes 83 EC 18 33 C0, ret 0x1c) diff 미러 mirror_blend_clip7 + 계수 blend_4678C0_* 9개 + mirror_details 5400→6000. 계약 테스트 RED→GREEN.
결과(기록 docs/history/laps/20261005_lap1035_work_g1_hp_blend4678c0_diff_mirror.md): 표본 A stale present 78→1(0x467ABA 77→0), 마지막40 중앙값 246.5→40, 고정 군 y455..475×x686..721 1,375→18, B/C 21/22 불변, save006 r1∩r2 0·신규 0, 항등식·안전 0.
미결(P-3 성능): 성능 pair p95 8/29(outlier)/7/11/13/8, 미러 off 대조 8/8, 호스트 load 4~12(chrome 등) — 문자 그대로 ≤7 미달, 미러 비용 분리 불가(UNKNOWN).
승격 작업자가 이어서 할 일: (1) 공유 temp 20261005_lap1035_work_hp/ 의 pair-result·trace_raw·layer_drift·screen_watch·stale_mask를 analyze_p_s*.py 없이 새 스크립트로 재계산, (2) P-3 판정(수용/낮은 부하 재측정), (3) 코드 검수, (4) 수용 시 work H-Q(0x467FD0, 클립 없음·wrap 범위 선확인) 사전등록.
```
