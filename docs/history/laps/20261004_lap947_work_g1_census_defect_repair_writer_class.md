# 2026-10-04 | lap 947 | G1 W70 census 계측 결함 수리 + writer 분류표

- 실제 provider/model/effort / 지정 역할: work(Claude Code `claude-sonnet-5-5`, 최신 Sonnet 별칭), 실무 구현/실행. 컨펌·마일스톤 승인 권한 없음.
- 가설 / 사용자 관찰: lap913 census 계측 결함 둘을 고치면 PS3 present의 `present_source_surface`가 실제 COM surface 포인터가 되고 `surface_blt_captured`가 완료된 캡처만 센다. 그 계측으로 lap819 §3 기준1 writer 분류표를 낼 수 있다(lap946 카드).
- 예상 PASS / FAIL 조건: PASS = RED 회귀 2건이 GREEN, fresh save006 `--census-only` exit0·census_gate PASS(9 hook, 64 PS3 locked_source, map/header 일치, dropped0, captured==calls_ps3), `present_source_surface != present_source_buffer`, 독립 재계산이 JSON과 일치. FAIL = 게이트 실패·재계산 불일치. 새 임계값/gate 완화 없음.
- 변경 파일 / source fingerprint / 커밋: 모두 uncommitted, commit0. `tools/inmm_stub/g1_census.c` `285d59db3b08cc34083b3eaf2e2f7c0d5fbeea7b1b0375fb0f444d1594693cf8`; `g1_census.h` `ef0e3cc8256f9e96d0feb3f1ac2f6fcb95f18d22a10d57e8a107ed7971f1079d`; `direct_draw_trace.c` `4f3e88148e4dfe30217d783ef62d1218985988f5e9c06ab5449ad2460e829f71`; `tests/test_g1_census.py` `1fc3523edc441f77e0d3b70a04a2edf346ea77410c35264814ba9f9ae964d1fa`; 빌드 `_inmm.dll` `64bec74c2c097cd5f630f58751141875cd45ffd85f7ad1b368aa56575c61c9cb`. 기존 다른 미커밋 변경은 보존.
- 수리: (a) `g1_census_present_boundary`/`emit_present_boundary`에 `source_surface` 인자를 추가하고 `direct_draw_trace.c` 호출부가 `(DWORD)(ULONG_PTR)source`를 넘겨 `present_source_surface`를 COM 포인터로 직렬화(`present_source_buffer`와 분리). (b) `++g_surface_blt_captured`를 `g1_census_surface_blt_begin`에서 `g1_census_surface_blt_end` 비교 루프 완료 뒤로 이동: begin 뒤 post-Blt Lock 실패·불일치는 `capture_missed`로 남는다. 기존 raw 수정 없음, validator/gate/임계값 변경 없음.
- RED→GREEN: `tests/test_g1_census.py`에 `test_present_boundary_serializes_surface_pointer_not_backing_buffer`, `test_surface_blt_captured_counts_completed_captures_only` 추가. 수리 전 2 failed, 수리 후 census 9 passed.
- 원본 SHA / 후보 SHA / 환경 / fixture: 보호 원본 EXE `b56986e0…a8ac`·비합성 save006 `616b7997…0d064`는 probe `source_unchanged=true`(read-only). 새 private runtime `local/runtime/lap947_census_r1`·prefix·Xvfb, Wine ddraw=b, census-only(mirror/HD 병용 없음), 원본 800×600 logical frame, 8 player records는 활성8인 부하증명 아님.
- 실행 명령 / 로그: `make -C tools/inmm_stub`; `make lint`·`make typecheck` PASS; `.venv/bin/python tools/g1_saved_scene_probe.py --census-only --runtime-root local/runtime/lap947_census_r1/runtime --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap947_census_r1/artifacts` (exit0), 로그 `logs/gates/lap947-census-r1.output` SHA `10c28b189c305cefe6a95171e6fbbc638f823790c7f328ed26111063a815dff5`. census raw SHA `e3f6bb892485de0e9f46689e4590c32d1ee529125ec462befdc293fdf70a318b`, map SHA `f7cc54324dec4317497185f925a04b8a61a1d8ae0b1b0a2c6ca5915a22728f7b`.
- 실행 판정: probe PASS, census_gate PASS(10개 check 전부 true), 9/9 hook active, 64/64 PS3 `locked_source` pitch832, `buffer_context_dropped=0`, `surface_blt_summary calls_ps3=64/captured=64/missed=0`, **`present_source_surface=0x01E75FD0` ≠ `present_source_buffer=0x0233C7B0`**(64개 모두; lap913의 buffer 직렬화 결함 해소). cleanup game_removed·prefix processes after `[]`.
- 독립 재계산: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap947_census_r1/recalculate.py` SHA `af92b7452db16a62fcfee252fa8539cc42405c8fec85a85ac1136a06bc6728d6`, `recalculation.json` SHA `824f43741f9d05112160275c56afd51286da43176db4d747f276225a775a7858`(binary map만 읽음, 제품 helper 미사용). 64 present의 map 카운트가 JSON `writer_pixels`/`unknown_pixels`와 전부 일치.

## writer 분류표 (PS3 last-writer map, 800×600=480000)

측정은 "각 논리 픽셀의 **마지막 writer**"이다. HD 미러가 실제로 덮은 비율(coverage)이 아니다. last = present 64, p50 = 64프레임 중앙값.

| writer | last px | last % | p50 % | world(y<480) % | HUD(y≥480, 96000) % | 분류 |
|---|---:|---:|---:|---:|---:|---|
| terrain_cache_transfer | 283931 | 59.15 | 59.16 | 73.10 | 3.36 | HD 가능 후보(P4b/P4c 지형 층, lap908·935 부분수용) |
| rle_tinted_clip | 68824 | 14.34 | 14.31 | 16.33 | 6.37 | HD 가능 후보(P5-T, lap934·935 부분수용) |
| dd_surface_blt | 65898 | 13.73 | 13.81 | 0.43 | 66.91 | HD 가능 후보(P5-H 패널 층, lap921 부분수용; 패널 내부 writer 원천은 lap913 UNKNOWN) |
| rle_tinted | 32618 | 6.79 | 6.79 | 8.49 | 0.02 | HD 가능 후보(P5-T) |
| rle_plain | 20281 | 4.23 | 4.23 | 1.61 | 14.69 | HD 가능 후보(W60/W70 마스크 미러) |
| rle_clip | 1067 | 0.22 | 0.16 | 0.02 | 1.03 | HD 가능 후보(W60/W70 마스크 미러) |
| rect_fill | 135 | 0.03 | 0.03 | 0 | 0.14 | 원천 그림 없음 |
| rect_border | 86 | 0.02 | 0.02 | 0.02 | 0.02 | 원천 그림 없음 |
| set_pixel / block_copy | 0 / 0 | 0 | 0 | 0 | 0 | 원천 그림 없음(PS3 최종 map 비어 있음) |
| unknown(어떤 writer도 못 잡음) | 7160 | 1.49 | 1.50 | 0 | 7.46 | unknown(아래) |
| 명시 잔여(GDI 텍스트 P7·P6) | 측정 대상 아님 | — | — | — | — | DD 8bpp 버퍼 밖이라 이 map에 안 잡힘. 비율 미측정(두 번째 장면·GDI 작업 몫) |

- 합계(last): HD 가능 후보 6개 writer 472,619 = **98.46%**, 원천 그림 없음 221 = **0.046%**, unknown 7,160 = **1.49%**. 분모에서 원천 없음을 빼면 HD 후보 98.51%. **이 숫자는 writer 능력 분류이지 coverage 합격 근거가 아니다**: 각 후보 writer의 실제 미러 coverage, identity 오라클, Scale2x 차이 증명은 기존 부분수용 증거만 있고 이번 lap에서 새로 재지 않았다.
- unknown 7,160px: 전부 y512..599·x0..798(하단 HUD 띠)이며 월드 0. 같은 장면 `selection.png`의 같은 위치 7,160px는 **전부 (0,0,0) 검정**이다(다른 프레임 PNG라 가설 지지일 뿐 증명 아님). 가설: dd_surface_blt 계측은 blt 전후 **바뀐 픽셀만** 배정하므로, 초기 검정 위에 검정을 복사한 픽셀은 "변화 없음"이라 미배정으로 남는다. 따라서 unknown은 미지의 writer가 아니라 미변경 검정일 가능성이 크다. 이 가설은 이 raw로 증명되지 않았다. unknown 1.49% < PS3 화면 5%이므로 lap946 카드의 strategy 재호출 조건(unknown > 5%)에 해당하지 않는다.
- 측정식 대조(카드 §3): 명시 잔여(GDI/P6)는 이 map에서 0으로 보이지만 GDI는 다른 경로라 비율을 확정하지 않는다 → 명시 잔여 ≤5% 판정은 하지 않고 UNKNOWN. unknown은 7,251(lap912 p50, 구 계측) → 7,160/p50 7,182로 거의 같고 분류 근거(미변경 검정 가설)가 붙었다.
- 판정: 두 계측 결함 수리 PASS(work, partial: 일반 post-Lock 실패 경로를 강제로 일으킨 실행은 없음, 정적 회귀+정상 실행 captured=calls만 확인). writer 분류표는 이 save006 장면 한정이며 G1 HD coverage·제품 합격 아님. G1 HOLD 유지.
- 남은 위험 / 독립 검수 / 사용자 승인: 후보 writer별 HD 증거 재측정과 두 번째 장면 census(메뉴 PS9)는 미수행. unknown=미변경 검정 가설의 직접 검증(예: before/after 동일 픽셀 계수)과 GDI(P7) 잔여 비율은 다음 단계. 사용자 승인 없음, G2/G5 종료 유지.
- 다음 한 가지: 새 middle(Opus)이 `recalculation.json`·source diff·표를 독립 검수하고, 분류표를 기준1 입력으로 수용할지와 다음 work(두 번째 장면 census 또는 unknown=미변경 검정 직접 검증)를 정한다.
