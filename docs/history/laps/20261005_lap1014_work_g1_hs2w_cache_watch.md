# 2026-10-05 | lap1014 | G1 H-S2w — 원본 lane 지형 캐시(0xBA3D30) 쓰기 watch(측정 전용)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 제품 mirror·gate·validator 변경 0(census 측정 DLL·하네스만).
- 가설 / 사용자 관찰: lap1013 사전등록 — save000 stale 성분 A/B/C 원인은 H1(미후킹 캐시 writer가 1x 캐시에 씀) 또는 H2(hook된 캐시 writer가 쓰지만 compose가 건너뜀/레이어 표류).
- 예상 PASS / FAIL 조건(lap1013 §4): K-0 유효(watch_armed 주소=캐시 주소·selftest hit 1·cleanup ok·C-0), K-1 hit 수·EIP·값·present 분포, K-2 EIP가 mirror hook 함수 범위 안/밖. hook 밖 EIP=H1, 전부 안 또는 hit 0=H2.
- 변경 파일 / 커밋(전부 uncommitted):
  - `tools/inmm_stub/g1_census_watch.h`(SHA `8f65f1b4…`): `G1_CENSUS_WATCH_CACHE_BASE 0xBA3D30`·`PITCH 832`·`g1_census_watch_cache_address(x,y)`.
  - `tools/inmm_stub/g1_census.c`(`5765503e…`): opt-in `SYW2_G1_CENSUS_WATCH_CACHE=1`(watch 주소를 캐시로)·`SYW2_G1_CENSUS_WATCH_PRESENTS=N`(watch 전용 present 계수 `g_watch_present_ticks`, `g1_census_present_boundary` 래퍼가 armed 동안 목표 상태 primary present마다 증가, N 도달 시 `watch_finish("watch_window_end")`), N>0이면 기존 64-present `window_end`로 끊지 않음. watch_hit에 `watch_present`, watch_armed/summary에 `cache`·`watch_presents`(·`watch_present_ticks`) 필드 추가. 기본(옵션 없음)은 기존 동작 불변. watch_hit 최악 길이 610B < wsprintfA 1024 한도.
  - `tools/g1_saved_scene_probe.py`(`9f4eedf4…`): `--census-watch-cache`·`--census-watch-presents N`(둘 다 `--census-watch` 필요, N 0–9999), `_census_watch_wait_timeout(N)`=60+N/5 s, loaded-only 대기에서 64-present 창 뒤 `watch_summary`까지 추가 대기(`census_watch_wait`).
  - `tests/test_g1_census.py`(`5f5019ee…`): 호스트 gcc 주소 계산 3건·소스 계약·하네스 옵션 테스트 2개 신규 RED→GREEN, 기존 arm 순서 단언을 `watch_arm_address(g_watch_address)`로 갱신. `tests/test_g1_census.py`+`test_g1_saved_scene_probe.py` 223 passed, `make lint`·`make typecheck` PASS.
- 원본 SHA / fixture: 원본 EXE `b56986e0…08a8ac`(`[HQ]Syw2plus 2002.exe`, read-only objdump), save000 `1c703551…19da`(index 1), 세 run probe-result `source_unchanged` true. 활성8인 부하 증명 아님.
- 실행 명령(공유 temp `20261005_lap1014_work_s2w/`, runner `run.sh` SHA `50508e12…6da3`, 순차·fresh runtime-root `local/runtime/lap1014_s2w_{wa,wb,wc}`, game 사본 삭제): `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --census-only --fixture save000 --scene-actions none --census-residual --census-skip-presents 20 --census-watch X,Y --census-watch-cache --census-watch-presents 700` — W-A `112,126`·W-B `437,463`·W-C `302,9`. 전부 exit 0. 로그 `logs/gates/lap1014_s2w_w{a,b,c}.log` SHA `010579b6…`/`89ab25f3…`/`ae2c9f85…`, census_raw `f4f6f51c…`/`56de361b…`/`c9532386…`, trace_raw `e218105d…`/`6c2d98f1…`/`a6f91a16…`. 분석 `analyze_s2w.py`(`ee11e9e6…`)→`analysis_s2w.txt`(`db509007…`).
- **r0 FAIL 보존(수리 후 재실행)**: 첫 W-A(`wa_r0_windowend64`, census_raw `db0d2f0e…`)는 watch가 기존 `watch_on_present`의 64-present `window_end`에서 present 21~84만 보고 hit 0으로 끝났다(watch_present_ticks 63). N>0이면 그 종료를 막도록 수리(테스트 추가)한 뒤 재실행 — 위 결과는 모두 수리 뒤 run.

## 측정

- **K-0 PASS ×3**: `watch_selftest` hit 1 PASS, `watch_armed` present 21(skip 20) address = `0x00BBD720`/`0x00C01FA5`/`0x00BA5B9E`(= `0xBA3D30+y*832+x`, 카드 값과 일치)·`cache` 1·`watch_presents` 700, `census_gate` PASS(10 checks·64 PS3 present·9 hook active)·`census_wait` 64 PASS, `save_navigation [1]`, `watch_summary` reason `watch_window_end`·**watch_present_ticks 700/700**, cleanup ok.
- **K-1**: W-A **hit 0**, W-C **hit 0**(700 present 전부, 성분 A·C 캐시 바이트는 한 번도 안 쓰임), W-B **hit 1**: watch_present 76(present ~97), EIP `0x00468DBA`, 값 89, in_hook 0·in_terrain 0(census 내부 hook 아님), 스택 text `0x4355DC`(`0x4355D7` 호출 뒤)·`0x43327C`….
- **K-2**: 원본 objdump(read-only)에서 `0x468DB6: mov [eax+edi-1],dl` 직후 = EIP `0x468DBA`, 함수 `0x468CC0`(`ret 0x18` @`0x468DFE`, = 터레인 shade 블리터, 이미 `g1_mirror2x.c` `G1_TERRAIN_SHADE` hook 대상) **안**. 즉 hook 밖 writer 0.
- 판정(결론 규칙): hook 밖 EIP 없음, A·C는 hit 0 → **H2**(캐시는 안 바뀌는데 candidate 화면이 어긋남 = 레이어 expected 자체 표류/compose 건너뜀). H1은 이 장면 A·C·B 어느 점에서도 지지되지 않았다. **FEASIBLE**(측정 완료·다음 단계 명확).
- 한계: watch는 DR0 하나·present 스레드(thread_id 280) 한정이라 다른 스레드의 캐시 쓰기는 못 본다(원본은 단일 렌더 스레드 정황이나 입증 아님). 창은 present 21~720, 원본 lane 속도라 candidate present 300과 정확히 대응하지 않는다. B는 1점 1건뿐이라 B 전체 5,442 px의 쓰기 분포는 모른다.

## 회귀 / 남은 위험 / 다음 한 가지

- 옵션 없는 census·기존 watch는 불변(소스 계약 테스트·기본 경로 동일). 제품 mirror 변경 0.
- 다음 work **H-S2d**(candidate lane 진단, opt-in·경량 계수만): `compose_cache_layer`가 A `(38..186,64..168)`·C `(259..337,0..25)`·B `(371..502,427..491)` 안 픽셀을 건너뛴 사유(scratch a≠b / identity lookup miss) 계수와, 표류 첫 ordinal(캐시 바이트 ≠ `g_layer_expected` 첫 present)을 save000 candidate pair에서 기록한다. B의 `0x468CC0` 쓰기 1건(present ~97)이 compose를 건너뛰었는지도 같은 계수로 본다. 그 전에 middle이 이 기록을 새 스크립트로 독립 재계산한다.
- 독립 검수 / 사용자 승인: work 결과일 뿐 마일스톤 승인 아님. 인계 `loop/ESCALATE_SOL`(일상 middle 검수 요청).
