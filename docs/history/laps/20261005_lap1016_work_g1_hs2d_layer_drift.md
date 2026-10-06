# 2026-10-05 | lap1016 | G1 H-S2d 캐시 레이어 표류 진단 → 표류 0, H-S2w 추론 반증(stale는 화면 쪽 비추적 writer)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 게임 실행 = save000 pair 순차 2회, 커밋 0.
- 가설 / 사용자 관찰: lap1015 §3–4 — save000 stale(고정 카메라 마지막 40 중앙값 7,675)는 candidate 내부 `g_layer_expected` ≠ 캐시(HD 품질 손실)이고, 원인은 compose skip(H2) 또는 candidate-only 캐시 변화다. 이를 표본 3점(A `112,126`·B `437,463`·C `302,9`)과 사각형 3개(A `x38..186×y64..168`·B `x371..502×y427..491`·C `x259..337×y0..25`)의 present별 6값으로 직접 관측한다.
- 예상 PASS / FAIL 조건(lap1015 §4): L-0 유효(scene 동일·stale 마지막 40 중앙값 7,675±10%·안전 0·cleanup ok·loaded PNG 비단색), L-1 표본별 첫 stale present와 6값, L-2 사각형 표류 계수·compose 결과 계수, L-3 분기 (i)~(v). FAIL/BLOCKED = 무장·로드 무효·L-0 재현 실패.
- 변경 파일 / source fingerprint / 커밋: 제품 mirror 동작 변경 0(env 없으면 `layer_drift_on()` false, compose 픽셀 로직·저장 동일). uncommitted.
  - `tools/inmm_stub/g1_layer_drift.h`(신규, `e3206f2f5f0a…`): 사각형·표본 상수, `g1_layer_drift_overlap`·`_contains`·`_count`(캐시/레이어/화면/snapshot 4계수) 순수 helper. 호스트 gcc 단위 테스트.
  - `tools/inmm_stub/g1_mirror2x.c`(`41ac7befc905…`): `SYW2_G1_LAYER_DRIFT=1` opt-in. `mirror_reinvoke` 조기 반환 4종(args/buffer/panel_foreign/range, 캐시 대상일 때만)·NOT_READY·COMPOSE_RAN, `compose_cache_layer` 경계 거부와 픽셀 결과 4종(a≠b / 미기록 a=0·b=FF / lookup miss / composed; 원래 `a != b` skip 판정은 동일, 분류만 추가), 표본 점별 마지막 compose 이벤트(writer·origin·w·h·present·결과), 10개 hook wrapper 중첩 guard 우회 계수(캐시 대상), PS3 present마다 `layer_drift_present`(stale loop가 `g_covered`를 바꾸기 전, 값이 바뀐 present만 `C:\inmm_g1_layer_drift.jsonl`에 기록, 50 present 하트비트).
  - `tools/inmm_stub/Makefile`(`8d7c3bd3713c…`): 의존 헤더에 `g1_layer_drift.h`.
  - `tools/g1_saved_scene_probe.py`(`8ae64edf51c7…`): `--layer-drift`(`--hd-source scale2x` 필요·census-only 불가, env는 candidate lane만, 산출물 `layer_drift.jsonl` 복사·SHA).
  - `tests/test_g1_mirror2x.py`(`88e72ef054ba…`): helper 호스트 gcc 테스트·소스 계약 2개, `tests/test_g1_saved_scene_probe.py`(`1118c70777f8…`): 옵션 계약 1개. 3개 RED→GREEN. `make lint`·`make typecheck` PASS, 관련 테스트 260 passed.
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 EXE `b56986e0…08a8ac` read-only(하네스 pin 검사 `source_unchanged` true 2/2), save000 `1c703551…19da`(index 1), 활성8인 부하 증명 아님, 후보 DLL = 프로브가 `artifact_root/bridge`에 빌드한 사본.
- 실행 명령 / 로그 / 캡처 경로: 공유 temp `20261005_lap1016_work_s2d/`(runner `run.sh` `ae2b9c557536…`) — 순차 2회 `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1016_s2d_r$N --artifact-root …/20261005_lap1016_work_s2d/r$N --hd-source scale2x --fixture save000 --scene-actions none --performance-window --layer-drift`. 전부 exit 2(pair HOLD = non-loaded capture tag BLOCKED, `--scene-actions none` 예상 결과, lap1010 동일). 로그 `logs/gates/lap1016_s2d_r{1,2}.log` SHA `e4410683d0bc…`/`79f486179bdb…`, pair-result `36450ed8a5b6…`/`6b7d30233a82…`, `layer_drift.jsonl` `4646ab6758a6…`/`bb62cff67b8e…`(tick만 다르고 값 동일), 분석 `analyze_s2d.py`(`a670ddba1e65…`)→`analysis_s2d.json`(`b5c087434aff…`). game 사본은 프로브 cleanup으로 삭제(`cleanup.ok` true 4/4), prefix·로그·output 보존.

## 측정값 / 판정

- **L-0 PASS(2/2)**: scene_state_equal true, stale 마지막 40 중앙값 **7,694.5**(r1=r2; lap1010 7,675 대비 +0.25%), 안전 7종 0, 두 lane cleanup ok, source_unchanged, loaded PNG 226색(비단색), loaded V1/V2/V2q/Scale2x PASS(V2s 629/635), PS3 present 411, ticks/s 비 1.0000, 후보 p95 7ms(진단 on, gate 아님). 레코드: header 1·표본 59·사각형 221·하트비트 9.
- **L-1/L-2 핵심 — 레이어 표류 0**: 세 사각형 모두 모든 present에서 `layer_covered && 캐시≠layer_expected` = **0**, 미커버 = **0**. 표본 3점의 `cache == lexp`, `lcov == 1`이 410 present 내내 유지(B만 present 168에서 캐시 83→89로 바뀌고 같은 present에 `terrain_shade 0x468CC0` compose(composed)로 `lexp`가 따라감). A·C는 present 0 이후 캐시 변화·compose 호출이 **0**(사각형 compose 호출 증분 [0…0]), B는 호출 66·composed 20,430픽셀.
- **스냅샷/화면 관측(stale의 실제 위치)**: 표본 3점 모두 `snap == lexp == cache`인데 **화면 픽셀(`scr`)이 일시적으로 다른 값**이다 — A: present 298부터 94/215/163/187 → 339에서 85 복귀, B: 231부터 244→253 램프·55·211 → 끝까지 지속, C: 129부터 247→253 램프·88·55·211 → 336 이후 92 복귀. 사각형 계수 `screen≠cache` 최대 A 13,315/B 6,848/C 1,982, `snapshot≠layer_expected`(covered) 최대 A 4/B 2,495/C 159는 present 0의 값(= 그 위치 기존 덮어쓰기)과 같아 증가 없음. 즉 stale = 캐시→화면 전송 뒤 **화면을 덮어쓴 writer가 snapshot을 갱신하지 않은 것**이다.
- **L-3 분류**: (i) 캐시 변화+compose skip 0건 · (ii) 캐시 변화+compose 없음 0건 · (iii) 캐시 그대로+expected/covered 변화 0건 · (v) snapshot≠layer 증가 0건. 사전등록 분기 중 가장 가깝지만 정의와 다른 것은 (iv) "화면≠캐시"이며, 원인은 전송/좌표가 아니라 **전송 뒤 화면 쪽 비추적(unmirrored 또는 reject) writer**다. 따라서 **lap1014/1015의 가설 "stale = candidate 내부 `g_layer_expected` ≠ 캐시"는 반증**(H-S2w 계수·EIP 자체는 유효, 그로부터의 추론이 틀림). H2(compose skip) 지지 0, 원본 lane의 "A·C 캐시 쓰기 0"과 candidate의 "A·C 캐시 변화 0"은 일치해 긴장점은 해소(candidate-only 캐시 writer 없음, O-1 불필요).
- 참고: candidate 누계 reject — `overlay_blt_rejects` 452, `flip_rle_466B50_reject_size` 76(save000 신규, save006 0), `textout` 등 기존. 이것이 화면 쪽 비추적 write의 후보이지만 위치(A/B/C 사각형)와의 교차는 **측정하지 않았다**(UNKNOWN). lap1012 census(baseline lane, skip 250·64 present 창)는 이 구간의 변화 값(244~253 램프)을 보지 못했을 가능성이 있으나 이것도 미확인.

## 회귀 / 남은 위험 / 상태

- 제품 동작 불변(env 없으면 추가 스캔·출력 0). 진단 on 실행 p95 7ms는 gate 아님. pair HOLD는 기존 non-loaded tag BLOCKED뿐. `make check` 결과는 STATUS 검증 줄에 보강한다.
- 표본 점 3개와 사각형 3개 한정; 사각형 내부 다른 위치의 개별 writer는 미식별. 램프 값(244~253)이 어떤 스프라이트인지(구름/연기·메시지 글자·HUD 효과 등)도 미식별 — 육안 단서만 있음(loaded 화면 상단 중앙 구름 스프라이트, 하단 중앙 "집결지가 설정되었습니다" 글자).
- 독립 검수·사용자 승인: 미실시(다음 middle). 기술 부분 결과이며 G1 마일스톤 아님.

## 다음 한 가지(제안, middle이 확정)

work H-S2r — 화면 쪽 writer 지목: candidate 진단에 reject 기록을 추가한다(`flip_rle`·overlay blt·textout reject마다 writer·x·y·w·h·reason·present를 같은 JSONL에 기록, 사각형 교집합 계수). 같은 `--layer-drift` save000 pair로 reject가 A/B/C 사각형의 first-stale present(A 298·B 231·C 129)와 겹치는지 본다. 겹치지 않으면 baseline lane에서 화면 버퍼 쓰기 watch(`--census-watch`, 기존 DR0, 캐시 아님)를 `--census-skip-presents 130~300`으로 늦춰 램프 값 writer EIP를 지목한다.
