# 2026-10-06 | lap1047 | G1 work H-V — `0x466BE0` 클립 좌우반전 리맵 RLE(6인자) diff 미러 + 진단 버퍼 수리(V-S)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 모든 변경 uncommitted.
- 가설: lap1046 middle 사전등록(`20261006_lap1046_middle_g1_hu_acceptance_466be0_hv.md` §다음 work) — 미후킹 `0x466BE0`(thiscall `ret 0x18`, old bytes `83 EC 18 33 C0`, 32비트·클립 상자·좌우반전)을 H-R `mirror_flip_rle` 구조 diff 미러로 hook하면 save000 표본 (795,470)·(779,467)·(568,483)의 마지막 writer `0x466D15` stale present가 0이 되고 마지막40 중앙값 0이 유지된다. 재계획 없이 사전등록 그대로 구현했다.
- 변경 파일:
  - `tools/inmm_stub/g1_mirror2x.c`: `G1_FLIP_CLIP 0x00466BE0u`·`_LEN 5u`, `expected_flip_clip {83 EC 18 33 C0}`, `g_original_flip_clip`(`G1Primitive6Fn`), `g_hook_flip_clip`, 전용 before 버퍼 `g_flip_clip_before`, 계수 10개(`invocations·mirrored_calls·mirrored_pixels·changed_calls·clipped_calls·wrap_calls·reject_target/bounds/size/guard`), wrapper `mirror_flip_clip`(`mirror_flip_rle`과 이름·주소·`changed_calls` 외 동일: x·y·w·h 32비트, `g1_flip_rle_region` 화면 교집합, 원 인자 6개 그대로 1회 호출, `g1_overlay_blt_apply`, `layer_drift_write_end(... G1_FLIP_CLIP ...)`), install·restore·installed·reset·accessor. 클립 상자 쓰기 ⊆ rect∩clip ⊆ rect(lap1046 objdump)라 화면 교집합 diff가 원본의 화면 내 쓰기를 모두 덮는다.
  - `tools/inmm_stub/g1_mirror2x.h` accessor 10개, `tools/inmm_stub/direct_draw_trace.c` 요약 `flip_clip_466BE0_*` 10키(`flip_clip_details[480]`, 형식 최악 435).
  - **V-S(진단 버퍼 수리, 출력 내용·키·순서 불변):** `textout_details` 360→480(최악 430), `rect_fill_details`·`rect_border_details` 240→320(최악 262/274), `mirror_perf_details` 900→1100(최악 962 + `%s` 64). `mirror_details` 7,200은 유지: 두 번째 builder에 붙는 하위 형식 최악 합 6,848(NUL 포함, `%s` 64씩 허용) < 7,200.
  - `tests/test_g1_rect_fill.py`: 신규 `test_flip_clip_hook_table_and_wrapper_contract`·`test_trace_details_buffers_hold_worst_case_wsprintf_output`(둘 다 RED→GREEN: hook은 `G1_FLIP_CLIP` 부재로, 버퍼 테스트는 정확히 4건 `mirror_perf_details[900]`·`rect_fill_details[240]`·`rect_border_details[240]`·`textout_details[360]`로 FAIL), 기존 `test_flip_rle_hook_table_and_wrapper_contract`의 body 종료 앵커를 `0x466BE0` 주석으로 옮겼다(새 함수가 flip_rle 바로 뒤에 놓여서).
  - `tests/test_g1_mirror2x.py:299`: 제품 버퍼 크기 pin `mirror_perf_details[900]`→`[1100]` 갱신(V-S 의도된 변경, 안전 pin·golden 아님). 첫 `make check`가 이 pin 때문에 1 failed·1635 passed로 실패했고(로그 `logs/gates/lap1047-work-full-check-run1.log`), pin 갱신 뒤 재실행했다.
- 원본 SHA / 후보: 원본 EXE `b56986e0…8ac`(pair-result source_unchanged true 전 run). source sha256 앞 16자: `g1_mirror2x.c` `32ca11fd01620d2d`, `g1_mirror2x.h` `441fd5b976009a90`, `direct_draw_trace.c` `24ed0d587963e87b`, `test_g1_rect_fill.py` `a11799aa35e86996`. 6 run 모두 설치 성공(`mirror_details` 정상 출력, 설치 시 old bytes 검증). `-Wall -Wextra`로 `/tmp/hv_build`에 별도 컴파일해 `g1_mirror2x.c`·`direct_draw_trace.c` 경고 0 확인(`asset_hook.c`의 기존 경고만 남음).
- 실행(공유 temp `20261006_lap1047_work_hv/`, 로그 `logs/gates/lap1047_hv_*`): `run_v.sh` `29edbb12…`(lap1045 `run_u.sh`에서 이름·표본만 변경: 순차·단일 인스턴스·run 직전 load 대기·run 뒤 `game` 사본 삭제). load 대기 0(시작 load 2.97~5.0). save000 watch pair 2회(`--fixture save000 --scene-actions none --performance-window --layer-drift --screen-watch --drift-samples "795,470;779,467;568,483" --stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`), save000 성능 pair 2회(watch 없음), save006 pair 2회(`--stale-mask 6-12,30-34,300-301,585-620,880`). 분석: `analyze_v_attr.py`·`analyze_v_s0.py`·`analyze_v_s6.py`·`isect_v.py`·`setdiff_v.py`(lap1045 스크립트 복사 후 표본·경로·계수 키만 변경). 산출: `attr_v.json`·`s0_v.json`·`s6_v.json`.
- **절차 이탈(수치 미사용):** 첫 launch 명령이 `diff` exit 1로 사슬이 끊긴 것처럼 보여 한 번 더 launch했고, 결과적으로 `run_v.sh` 두 인스턴스가 동시에 돌았다(lap1039와 같은 유형). 둘 다 시작 직후(약 14초) 해당 process group만 TERM으로 종료했다(다른 세션의 Xvfb·wine 비접촉). 그 run의 산출물은 `local/runtime/invalid_concurrent_lap1047_hv_w_r{1,2}`(`game` 사본만 삭제)·`logs/gates/invalid_concurrent_lap1047_hv_w_r*`·공유 temp `invalid_concurrent*`로 격리 보존했고, 이 기록의 수치에는 쓰지 않았다. 이후 단일 인스턴스로 6 run을 처음부터 다시 돌렸다.

## 수치

| 항목 | 기준(lap1045 w·lap1041 s2/s3·lap1039) | lap1047 |
|---|---|---|
| **V-0** 안전 7종·cleanup·source_unchanged | 0 / true / true | 6 run 전부 0 / true / true, trace JSONL 손상 0, ps3 w 409/412·s0 412/412·s6 886/887 |
| V-0 항등식 `invocations = mirrored + reject_*` | — | `flip_clip_466BE0`: w r1 1414 = 530 + 884(reject_bounds), r2 1415 = 526 + 889, s0 1420 = 530 + 890 / 1422 = 530 + 892, s6 3099 = 327 + 2772 / 3105 = 327 + 2778. reject_target/size/guard 전부 0, clipped 146/145/146/146/327/327, changed 283/281/283/283/235/235. 기존 hook 항등식(`466B50`·`4678C0`·`467FD0`·`467B00`·`467580`·`468360` 등 12 family)도 save000 4 run 성립. save006의 `rect_fill_466070`·`rect_border_465B30` 불일치(31868 대 31310 등)는 lap1045 s6 run에도 있는 기존 구조(두 hook은 reject_bounds 계수 없음)이며 이번 변경과 무관 |
| 무장·selftest | PASS·fail 0 | watch 2 run selftest PASS·무장 52라운드 fail 0·좌표 3/3 = 표본 3점·dropped/overflow 0 |
| **V-1** (795,470) stale present·마지막 writer | 15 (`0x466D15` 12·`0x46884E` 2·`0x467CCF` 1; 실효 `0x466D15` 13) | **2 (`0x46884E` 2)**, r1·r2 동일(구간 p140..141), 값 일치 2/2. `0x466D15`·`0x467CCF` 0 |
| V-1 (779,467) | lap1041 s2 `0x466D15` 6 + `0x46884E` 2 | **2 (`0x46884E` 2, 구간 p143..144)**, 값 일치 2/2. `0x466D15` 0 |
| V-1 (568,483) | lap1041 s3 `0x466D15` 3 | **0** (u 3, hit 412~415) |
| **V-2** 마지막40 중앙값 | 0 | **0 / 0**(watch r1·r2), 성능 r1·r2도 0. p24..58 0·p366~ 0·A/B/C 표본 stale 0 |
| V-2 새 r1∩r2 ∖ 기준(lap1045 w_r1∪w_r2) | — | **0**(39프레임) |
| V-2 기준 r1∩r2 ∖ 새 r1∪r2 (제거) | — | **572 px**: 프레임 298 247·프레임 234 221·프레임 6 104, 나머지 0 |
| V-2 r1∩r2 합(참고, 지표 불안정) | 1,749 | 2,338(r1 합 3,657→2,554, r2 합 3,232→2,544로 오히려 감소). 새 ∖ 기준 0이므로 증가분은 run 변동(교집합 지표의 알려진 불안정)이다. 이 합으로 결론 내지 않는다 |
| **V-3** 성능 pair p95 | 7/7, tick 비 1.0025 | **7 / 8**(≤8), 히스토그램 재구성 p95 7/8·평균 5.098/5.245(lap1045 s0 5.147/5.035)·10ms 이상 0/9. tick delta 400 vs 기준 400/400 → 비 1.000. 시작 load 3.95/4.09. watch run p95 12/12는 watch 계측 run이라 판정 외(기준 hs·hu watch 11~12) |
| **V-4** save006 steady 38 + 880 | 신규 0 | **r1∩r2 0**, 기준(lap1045 s6 r1·r2) 대비 신규 0/0·제거 0/0, 덤프 39 공통, p95 7/8·cov p50 99.31%, 안전 0, pair status **PASS(exit 0)** 2회(V2/V2s/V2q·scale2x 포함 9 gate 전부 PASS) |
| V-4 초기 프레임 6..34(판정 제외, 표) | 6..12: 21.5~22.3k / 30..34: 3.1~4.1k(lap1045) | 6..12: 18.2~19.1k(r1=r2) / 30..34: **0**. 새 ∖ 기준 합집합 0 — H-V 미러가 save006의 `0x466BE0` 쓰기(mirrored 327·changed 235)를 반영해 전환 구간 stale이 줄었다 |
| **V-S** | — | 버퍼 테스트 GREEN, 6 run `textout_iat_metrics`·`rect_*` 출력 키 20종 존재·JSONL 파싱 손상 0 |

## 해석
- 가설 확정: 표본 3점의 `0x466D15` writer stale present(13+6+3 = 22/run)가 전부 사라졌고(r1·r2 동일), 분리 확인 대상 `0x46884E`(각 2)는 그대로 남았다. 남은 표본 stale = `0x46884E`(hook 대상 `0x4687F0`, 사전등록된 다음 단계) 4건뿐이다. 마지막40 중앙값 0 유지, 새 stale 0, 제거는 프레임 298/234/6(572 px)이다.
- save006 효과는 H-U와 달랐다: `0x466BE0`이 save006에서 327회 실제 화면 안 쓰기(mirrored)라 초기 전환 프레임 6..12가 약 3k, 30..34가 3~4k→0으로 줄었다. 판정 범위(steady + 880)는 이미 0이었다.
- 성능: 미러 비용은 p95 7/8·평균 5.1~5.2ms로 H-U 기준과 구분되지 않는다. 대조(미러 off)는 V-3 미달이 없어 실행하지 않았다.
- V-S: 형식 최악 길이 테스트가 추가돼 같은 종류의 stack 넘침이 다시 생기면 호스트에서 잡힌다. `%s` 허용치는 `mirror_perf_details`의 자산 source 이름(64)만 표에 두었고 다른 `%s` 호출은 `%s`를 0으로 센다(그 문자열은 자체 버퍼로 제한됨).

## 회귀 / 남은 위험 / 독립 검수
- 호스트 테스트: `tests/test_g1_rect_fill.py`·`test_g1_panel_layer.py` 21 passed, `make lint`·`make typecheck` PASS. 전체 `make check`는 기록 freeze 뒤 1회 실행(결과는 STATUS 보강).
- 남은 위험: 표본 3점뿐이라 `0x466BE0` 전체 호출을 대표하지 않는다(save000 호출 1414 중 mirrored 530, 화면 밖 884). 호출처 `0x419FB0`·`0x41A54A` 중 관측된 것만 검증했다. 버퍼 테스트는 `wsprintfA`별 형식 최악만 검사하고 `lstrcatA`로 합쳐지는 `mirror_details` 합은 이 lap에서 스크립트로 계산했다(6,848, 호스트 테스트 미포함).
- 사용자 승인 상태: 기술 부분수용 요청일 뿐 G1 마일스톤 승인이 아니다.
- 독립 검수(middle)가 확인할 것: (1) 새 스크립트로 watch r1·r2·성능 r1·r2·save006 r1·r2와 기준(lap1045 w·s6, lap1041 s2/s3) 재계산(항등식·`0x466D15` 22→0·`0x46884E` 4 불변·마지막40 0·새 ∖ 기준 0·제거 572·save006 steady 0·초기 프레임 표·p95·tick 비), (2) `mirror_flip_clip` 코드가 `mirror_flip_rle`과 이름·주소·`changed_calls` 외 동일한지·원 인자 6개 1회 전달·objdump 재확인, (3) V-S: 버퍼 4개 크기·`mirror_details` 합 최악 길이(6,848 < 7,200), (4) 다음 work `0x4687F0`(`0x46884E`, 클립 없음·`ret 0x18`) 사전등록 → 이후 `0x4689C0`(`0x468A28`).
- 다음 한 가지: middle H-V 독립 검수 → work H-W(`0x4687F0`).
