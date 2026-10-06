# 2026-10-05 | lap1035 | G1 work H-P — `0x4678C0` 클립 반투명 RLE(7인자) diff 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 모든 변경 uncommitted.
- 가설: lap1034 middle 사전등록(§4) — 미후킹 `0x4678C0`(thiscall `ret 0x1c`, old bytes `83 EC 18 33 C0`)을 `mirror_blend_clip`(H-B4) 동형 diff 미러로 hook하면 save000 표본 A(695,468) stale(마지막 writer `0x467ABA` 77/78)이 사라지고 마지막40 stale 중앙값이 246.5 아래로 내려간다.
- 변경 파일:
  - `tools/inmm_stub/g1_mirror2x.c`: `G1_BLEND_CLIP7 0x004678C0u`·`_LEN 5u`, `expected_blend_clip7`, `g_original_blend_clip7`(`G1Primitive7Fn`), `g_hook_blend_clip7`, 전용 before 버퍼 `g_blend_clip7_before`, 계수 9개, wrapper `mirror_blend_clip7`(x·y·w·h 16비트 부호 확장, 원 인자 7개 그대로 1회 호출, 화면 교집합 diff 미러, `layer_drift_write_end(... G1_BLEND_CLIP7 ...)`), install/restore/installed/reset
  - `tools/inmm_stub/g1_mirror2x.h` accessor 9개, `tools/inmm_stub/direct_draw_trace.c` 요약 `blend_4678C0_*` 9키 + `mirror_details` 5400→6000(2곳)
  - `tests/test_g1_rect_fill.py` 신규 1개(`test_blend_clip7_hook_table_and_wrapper_contract`, RED→GREEN), `tests/test_g1_panel_layer.py:115` pin 5400→6000(제품 자체 버퍼 크기 계약, 안전 pin·golden 아님)
- 원본 SHA / 후보: 원본 EXE `b56986e0…8ac`(pair-result `source_exe_sha256`·`private_exe_sha256` 일치, source_unchanged true 전 run). source sha256 앞 16자: `g1_mirror2x.c` `c7f73d167f6d0f70`, `g1_mirror2x.h` `3af67c949b6e5871`, `direct_draw_trace.c` `6d296b9ba5bb7ce2`, `test_g1_rect_fill.py` `e7f48d01a3b38fd6`, `test_g1_panel_layer.py` `3184d7debb0918b4`. 원본 old bytes `83 EC 18 33 C0`·명령 경계는 lap1034 middle objdump 검수를 그대로 쓰고, 설치 시점에도 `install_one`이 검증한다(`primitive_install_success 1`).
- 실행(공유 temp `20261005_lap1035_work_hp/`, 로그 `logs/gates/lap1035_hp_*`):
  - `run_p.sh` `12c500e6…`: save000 watch pair 2회(`--fixture save000 --scene-actions none --performance-window --layer-drift --screen-watch --drift-samples "695,468;766,139;799,315" --stale-mask …`, 기준 = lap1032 o_s0_r1/r2), save000 성능 pair 2회(watch 없음), save006 env-off pair 2회. 6 run 전부 pair exit 2 = 기존 pair HOLD(V2s raw)이며 이번 변경과 무관.
  - 성능 pair 재실행: `run_p2.sh`(r3·r4)·`run_p3.sh`(r5·r6), **대조 `run_p4_control.sh`(r7·r8)**: wrapper 첫 줄에 `return g_original_blend_clip7(...)`(CONTROL-TEMP)를 임시로 넣어 미러만 끈 같은 hook으로 2회 → 실행 뒤 source를 `/tmp` 사본으로 복원, sha `c7f73d16…` 일치·`CONTROL-TEMP` 0건 확인. r7·r8 결과는 대조 증거일 뿐 제품 수치가 아니다.
  - 분석: `analyze_p_s0.py` `1cf303df…`(lap1030 `analyze_n_s0.py` + `blend_4678C0`·표본 마지막 writer 분류), `analyze_p_s6.py` `30bd293a…`(lap1030 s6 기준), 마스크 교집합은 즉석 스크립트(출력은 본문). 실행 뒤 `game` 사본 없음(확인).

## 수치

| 항목 | 기준(lap1032 o_s0_r1/r2) | lap1035 |
|---|---|---|
| P-0 항등식 `inv = mirrored + reject_*` | — | 8 run(w 2·s0 6) 전부 성립. watch r1 263 = 184 + bounds 79, r2 261 = 182 + 79, reject_target/size/guard 0 |
| P-0 안전 7종·cleanup·source_unchanged | 0 | 전 run 0 / true / true, scene_state_equal true, camera (39,53), tick delta 400 |
| P-1 표본 A stale present | 78 (77 `0x467ABA` + 1 `0x46884E`) | **1 (`0x46884E` 1)** r1·r2 — `0x467ABA` 77→**0** |
| 표본 B / C stale present | 21 / 22 | 21 / 22 (불변, 증가 0). B 마지막 writer `0x4680F5` 17 + `0x466BB3` 4, C `0x466BB3` 21 + `0x467CCF` 1 |
| P-2 마지막40 stale 중앙값 | 246.5 / 246.5 | **40 / 40** watch r1·r2, s0 r1·r3·r4·r5·r6 40(r2 = 짧은 run 293 present 144.5). 대조 r7·r8 246.5 |
| P-2 고정 군 y455..475×x686..721, 39덤프 r1∩r2 합 | 1,375 | **18** (덤프당 중앙값 0) |
| 덤프 r1∩r2 전체 합 | 7,532 | 2,954 (덤프당 중앙값 29→0), 마지막 40덤프 전부 stale 픽셀 0 |
| u(미설명 변화) A/B/C (watch) | 33/37/50 | 13/37/50 |
| P-4 save006 env-off r1∩r2 | 38프레임 0 | 38프레임 0·신규 0, 공통 39프레임은 r1에 프레임 880 부재(알려진 짧은 run 변형)라 38 — r1 대 기준(lap1030) 신규 0·제거 0, p95 7/8, cov p50 99.31%, 안전 0, `blend_4678C0` 50·48 호출 전부 reject_bounds(화면 밖) |
| `0x466B50` reject_size | 75/76 | 75(w r1·r2), s0 r1 76 (불변) |

- **P-3 성능(`p95 ≤ 7ms`·ticks 비 0.999~1.001): 문자 그대로는 미달, 원인은 호스트 부하로 추정(미확정).** 성능 pair(watch 없음) 후보 p95 = r1 **8**·r2 **29(load outlier: 짧은 run, ps3 293, ticks 비 0.985, 직전 load 4.1에 다른 프로세스 급증)**·r3 **7**·r4 **11**·r5 **13**·r6 **8**, ticks 비 전부 0.99998~1.000001(r2 제외). 같은 hook에서 미러를 끈 대조 r7·r8 = **8/8**, 비 0.99998/1.000002. 시작 load: r1 3.7·r3 4.4·r4 4.1·r5 5.7·r6 12.0·r7 8.6·r8 7.8(host 상시 부하원 = 다른 사용자의 chrome renderer 100%+·다른 프로젝트 node). 직전 수용 lap1030/1032는 load 2.6~3.5에서 7/7이었다. 미러 비용이 p95에 얼마나 더하는지는 부하가 같은 대조(8/8)와 후보(7·8·8·11·13)가 겹쳐 **분리 못 한다**(UNKNOWN). 비용 규모는 작다(호출 263/411 present, ≤320×160 복사·diff).

## 해석
- 가설 확정: 표본 A의 마지막 writer `0x467ABA`는 미후킹 `0x4678C0`이었고, diff 미러로 77건 전부 사라졌다(A stale present 78→1, 남은 1 = 사전등록대로 `0x46884E`). 마지막40 중앙값 246.5→40, 고정 군 1,375→18, 덤프당 전체 stale 중앙값 29→0. 대조 r7·r8(미러 off, 같은 hook)에서 246.5가 그대로라 감소는 미러 때문이다. B·C 표본과 save006 비회귀는 불변이다.
- 남은 stale(마지막40 40, 유지 구간 `p84..206` 45~141 등)은 이번 표본 3점 밖이다. B(`0x467FD0`)·C(`0x466B50` reject_size 75/76)는 그대로이고 다음 H-Q 대상이다.
- `reject_bounds` 79/263은 화면 밖(교집합 없음) 호출이다. `reject_size` 0이라 `G1_OVERLAY_MAX_*` 상한을 건드릴 필요가 없다.
- P-3은 위처럼 부하 노이즈와 구분되지 않았다. 사전등록 FAIL 처리(원인 분류 후 1회 수리 재실행)에 맞춰 재실행 4회·대조 2회를 했으나 호스트 부하를 통제할 수 없어 결론을 못 냈다. 임의로 gate를 바꾸지 않는다.

## 회귀 / 남은 위험 / 독립 검수
- 호스트 테스트: `tests/test_g1_rect_fill.py`·`test_g1_panel_layer.py` 포함 focused 89 passed, lint·typecheck PASS. 전체 `make check`는 기록 freeze 뒤 1회 실행(결과는 STATUS 보강).
- 남은 위험: 표본 3점뿐이라 이동 스프라이트 전체를 대표하지 않는다. `0x4678C0` 호출 2곳(`0x41A827`·`0x41A99F`) 중 관측만 검증. `0x46884E`(A 1건)·B/C writer는 미수리.
- 사용자 승인 상태: 기술 부분수용 요청일 뿐 G1 마일스톤 승인이 아니다.
- 독립 검수(middle)가 확인할 것: (1) 새 스크립트로 watch r1·r2·s0 r1~r6·대조 r7·r8·save006 r1·r2 재계산(항등식·A 78→1·마지막40·고정 군 18·P-4), (2) **P-3 판정**: 문자 그대로 ≤7 미달(1/5)·대조 8/8·부하 상관을 수용할지, 부하 낮은 시간대 재측정 필요 여부, (3) `mirror_blend_clip7` 코드 검수(원 인자 7개 그대로 1회, 16비트 부호 확장, 분리 버퍼), (4) 사양의 "`mirror_details` 5400→6000" 최악 길이 점검.
- 다음 한 가지: middle H-P 독립 검수(P-3 판정 포함) → work H-Q(`0x467FD0` B, 클립 없음이라 화면 오른쪽 wrap 범위 확인 선행).
