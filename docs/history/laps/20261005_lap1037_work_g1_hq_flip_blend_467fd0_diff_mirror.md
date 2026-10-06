# 2026-10-05 | lap1037 | G1 work H-Q — `0x467FD0` 좌우 반전 반투명 RLE(5인자, 클립 없음) diff 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 모든 변경 uncommitted.
- 가설: lap1036 middle 사전등록(§H-Q) — 미후킹 `0x467FD0`(thiscall `ret 0x14`, old bytes `83 EC 08 53 56`)을 `mirror_blend_clip`(H-B4) 동형 diff 미러로 hook하면 save000 표본 B(766,139)의 마지막 writer `0x4680F5` stale 17이 0이 되고 마지막40 중앙값이 40 아래로 내려간다.
- 변경 파일:
  - `tools/inmm_stub/g1_mirror2x.c`: `G1_FLIP_BLEND 0x00467FD0u`·`_LEN 5u`, `expected_flip_blend`, `g_original_flip_blend`(기존 5인자 `G1PrimitiveFn`), `g_hook_flip_blend`, 전용 before 버퍼 `g_flip_blend_before`, 계수 10개(`wrap_calls` 포함), wrapper `mirror_flip_blend`(x·y·w·h 16비트 부호 확장, 원 인자 5개 그대로 1회 호출, 화면 교집합 diff 미러, 클립 없는 원본이라 x<0·x+w>stride·y<0·y+h>600이면 `wrap_calls` 계수, `layer_drift_write_end(... G1_FLIP_BLEND ...)`), install/restore/installed/reset
  - `tools/inmm_stub/g1_mirror2x.h` accessor 10개, `tools/inmm_stub/direct_draw_trace.c` 요약 `blend_467FD0_*` 10키 + `mirror_details` 6000→6600(2곳, 최악 ≈5,746+395=6,141 < 6,600)
  - `tests/test_g1_rect_fill.py` 신규 `test_flip_blend_hook_table_and_wrapper_contract`(RED→GREEN) + 기존 pin 갱신, `tests/test_g1_panel_layer.py:115` pin 6000→6600(제품 자체 버퍼 크기 계약, 안전 pin·golden 아님)
- 원본 SHA / 후보: 원본 EXE `b56986e0…8ac`(pair-result `source_exe_sha256`·`private_exe_sha256` 일치, source_unchanged true 전 run). source sha256 앞 16자: `g1_mirror2x.c` `c891909579e48ca5`, `g1_mirror2x.h` `9a519ca64c11befe`, `direct_draw_trace.c` `72ca5455a2cc50f9`, `test_g1_rect_fill.py` `1e45cdc307b37cc0`, `test_g1_panel_layer.py` `e25682da2fcf5528`. old bytes `83 EC 08 53 56`은 lap1034 middle objdump 검수를 그대로 쓰고 설치 시점에도 `install_one`이 검증한다.
- 실행(공유 temp `20261005_lap1037_work_hq/`, 로그 `logs/gates/lap1037_hq_*`):
  - `run_q.sh` `2f6fef0a…`: save000 watch pair 2회(`--layer-drift --screen-watch --drift-samples "695,468;766,139;799,315" --stale-mask …`, lap1035 w와 동일 인자), save000 성능 pair 2회(watch 없음, 1분 load ≤4.5 대기 최대 30분 → 실제 대기 40초·40초, 시작 load 4.22/4.47), save006 env-off pair 2회. 각 run 직전 1분 load ≤8 조건 확인(대기 0초). 6 run 전부 pair exit 2 = 기존 pair HOLD(V2s raw)이며 이번 변경과 무관.
  - 대조 `run_q_ctl.sh` `e15b43f3…`: Q-3 미달이라 wrapper 첫 줄에 `return g_original_…(...)`(CONTROL-TEMP)를 H-P·H-Q 두 wrapper에 임시로 넣어 미러만 끈 같은 hook으로 성능 run 1회 → 실행 뒤 `/tmp`가 아닌 공유 temp 사본(`g1_mirror2x.c.product`)으로 복원, sha `c8919095…` 일치·`CONTROL-TEMP` 0건 확인. 대조 수치는 대조 증거일 뿐 제품 수치가 아니다.
  - 분석: `analyze_q_s0.py` `a254807d`(lap1035 `analyze_p_s0.py` + `blend_467FD0` 키), `analyze_q_s6.py` `b3a95c3e`(lap1035 s6 기준, 작업 디렉터리만 변경), `isect_q.py` `90534742`(r1∩r2 마스크 합, 마스크값 2 = stale; lap1035 p_w_r1/r2에 먼저 돌려 2,954를 재현해 방식을 검증). 실행 뒤 `game` 사본 없음(확인).

## 수치

| 항목 | 기준(lap1035 w r1/r2·s0·s6) | lap1037 |
|---|---|---|
| Q-0 항등식 `inv = mirrored + reject_*` | — | 6 run 전부 성립: w r1·r2·s0 r1 115 = 103 + bounds 12, s0 r2 114, save006 0 = 0. reject_target/size/guard 0 |
| Q-0 안전 7종·cleanup·source_unchanged·scene_state_equal | 0 / true / true / true | 전 run 0 / true / true / true, camera (39,53), tick delta 400 |
| Q-0 `wrap_calls` (관측) | — | **0 (전 run)** — 이 장면에서 `0x467FD0`은 화면 밖/행 넘김 호출 없음. clipped_calls 28(화면 가장자리 걸침), mirrored_pixels 22,171(r1)/21,912(r2) |
| **Q-1** 표본 B stale present / 마지막 writer | 21 (`0x4680F5` 17 + `0x466BB3` 4) | **4 (`0x466BB3` 4)** r1·r2 — `0x4680F5` 17→**0**, B ≤4 충족 |
| 표본 A / C stale present | 1 / 22 | 1 (`0x46884E`) / 22 (`0x466BB3` 21 + `0x467CCF` 1) — 불변 |
| u(미설명 변화) A/B/C (watch) | 13/37/50 | 13/**20**/50 |
| **Q-2** 마지막40 stale 중앙값 | 40 | **26 / 26** (watch r1·r2), s0 r1 26·r2 27. 대조(미러 둘 다 off) **246.5** |
| **Q-2** w r1∩r2 39덤프 합 | 2,954 | **2,064** (덤프당 중앙값 0, 최대 618→433) |
| Q-2 구간 중앙값 | p84..206 45 · p207..365 135/133 · p298..338 281~412 · p366.. 28~31.5 | 불변 구간 p84..206 45, p207..365 133~135로 큰 변화 없음(대조는 418) |
| **Q-3** 성능 pair candidate p95 / ticks | ≤7ms·비 0.999~1.001 | **8 / 10** ms(문자 기준 미달). ticks 비 20.0 Hz 기준 1.0000(candidate 19.9996·19.9996 vs baseline 19.99955·19.99966) |
| Q-3 대조(미러 off, load 6.67) | — | p95 **8**, 히스토그램 [4ms 100 · 5ms 148 · 6ms 74 · 7ms 39 · 8ms 26 …] vs 후보 r1 [129·141·50·45·18 …]·r2 [83·156·69·39·20 …] |
| **Q-4** save006 env-off r1∩r2 | 38(39)프레임 0·신규 0·p95 ≤8 | **39프레임 0·38프레임(880 제외) 0**·기준 대비 신규 0·제거 0·p95 8/8·cov p50 99.31%·안전 0·`blend_467FD0` invocations 0 |

- **Q-3 판정 의견: UNKNOWN-환경(문자 그대로는 미달).** 같은 hook에서 H-P·H-Q 미러를 모두 끈 대조도 p95 8이다(load 6.67로 후보보다 높음). 후보 r1 8·r2 10은 load 4.2~4.5에서 측정했으므로 미러 비용 분리를 단정하지 못한다. 평균 시간은 아직 재계산하지 않았다(middle 검수 항목). 기준값은 바꾸지 않았다.

## 해석

- 가설 확정: 표본 B의 마지막 writer `0x4680F5`는 미후킹 `0x467FD0`이었고, diff 미러로 B 17건이 전부 사라졌다(B stale 21→4, 남은 4 = 사전등록대로 `0x466BB3`). 마지막40 중앙값 40→26, 대조 246.5에서 감소하므로 미러 때문이다(H-P 40, H-Q 26). 덤프 교집합 합 2,954→2,064.
- `wrap_calls` 0: 이 장면에서는 클립이 없다는 원본 특성이 실제로 발현되지 않았다. 다른 장면에서는 UNKNOWN(계수는 남아 있다).
- 남은 stale(마지막40 26, p207..365 133 등)은 표본 3점 밖이며 C(`0x466B50` reject_size 75/76)·`0x46884E`(A 1)·표본 밖 writer가 남는다.
- save006 비회귀: 이 장면은 `0x467FD0` 호출 0이라 영향이 없음을 계수(0)와 39프레임 0으로 확인했다.

## 회귀 / 남은 위험 / 독립 검수

- 호스트 테스트: `tests/test_g1_rect_fill.py`·`test_g1_panel_layer.py` 17 passed(RED 확인 후), `make lint`·`make typecheck` PASS. 전체 `make check`는 기록 freeze 뒤 1회 실행하고 결과는 STATUS에만 보강한다.
- 남은 위험: 표본 3점뿐. `0x467FD0` 호출 2곳(`0x41A0CD`·`0x41AC95`) 중 관측으로만 검증했다. 클립 없는 원본이 화면 밖으로 쓰는 경우(wrap)는 이 장면에서 0회라 미러가 다루지 않는 부분(화면 교집합만)은 미검증이다. Q-3 성능은 환경 한계 UNKNOWN.
- 사용자 승인 상태: 기술 부분수용 요청일 뿐 G1 마일스톤 승인이 아니다.
- 독립 검수(middle)가 확인할 것: (1) 새 스크립트로 watch r1·r2·s0 r1·r2·대조·save006 r1·r2 재계산(항등식·B 21→4·마지막40·r1∩r2 2,954→2,064·Q-4), (2) **Q-3 판정**: p95 8/10 vs 대조 8, 히스토그램 평균 비교로 미러 비용 유무와 저부하 재측정 필요 여부, (3) `mirror_flip_blend` 코드 검수(원 인자 5개 그대로 1회, 16비트 부호 확장, 분리 버퍼, wrap 조건이 `stride` 기준임), (4) `mirror_details[6600]` 최악 길이.
- 다음 한 가지: middle H-Q 독립 검수(Q-3 판정 포함) → work `0x466B50` reject_size 75/76·`0x46884E`(표본 B 4·C 21의 writer, 거부 사각형 크기는 `w` 레코드로 계측).
