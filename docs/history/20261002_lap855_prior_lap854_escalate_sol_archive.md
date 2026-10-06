# lap854 work → middle 독립 검수 요청 (G1 W70 P3c)

## 결과

P3c 환경값 latch를 구현하고, QPC 예측 pair와 계측 OFF fresh 3 pair 성능 gate를 완료했다. work 1단 판정은 PASS이며, 이 결과는 P3 마감 경계다. 이 파일을 읽는 middle은 구현·raw를 독립 재검산하고 P3 수용/보류만 판정한다. G1 마일스톤 완료나 P4 착수 승인은 포함되지 않는다.

## 검수 입력

- 상세 work 기록: `docs/history/laps/20261002_lap854_work_g1_w70_p3c_env_latch_gate_pass.md`
- 변경 코드: `tools/inmm_stub/{direct_draw_trace.c,g1_census.c,g1_hd_asset.c,g1_mirror2x.c,g1_perf_sections.c}`; 회귀 가드 `tests/test_g1_mirror2x.py`, `tests/test_g1_hd_scale2x_probe.py`(기존 내부 helper 명 assertion을 cached mode assertion으로 갱신).
- 격리 artifact root: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap854_p3c_latch_probe` 및 `lap854_p3c_gate{1,2,3}`. 각 pair-result 안에 trace/capture/raw path·SHA가 있다.
- QPC pair: pair SHA `a09b843efbb4937ae3ae069a086f488158e586609e6d823bf0b343478e51c1de`; candidate raw SHA `d93b4b4719c335e97d12c193df99f89b4eea43efcd0c9fca78aa0ca9ead49ff7`.
- Gate pair SHA: 1=`26630ba58fc345dc641d54a2654eeeb11ae2e55476124be8649f7aec933068b6`, 2=`7de758e00bf8fcf99b7a1256d907e6c9d9fdd29688def127c4b0b5935f6f2537`, 3=`4509e4e90c778af0f10d8a1b71541a04adf67da08137e5c9f7ee121fb78225a9`.
- 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 비합성 save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`; private game/prefix/Xvfb 격리 및 원본 불변.

## Work 측정 요약

- QPC 10MHz, 400 active rows: compose `1,869,281 ticks / 30,822,706 pixels = 6.065ns/pixel`, window `0.935%`; hash lookup `1.223µs/call`. 예측 기준 ≤50ns/pixel, ≤2%, ≤2.5µs/call 충족.
- Fresh 3 pair: rate ratio `0.9999920 / 0.9999970 / 1.0000019`; p95 delta `+5 / +5 / +5ms`; candidate present `400/400/400`. Scale2x validator, scene/source/cleanup, loaded 1600×1200 non-black, selection/empty/drag_exact PASS. Minimap/production은 기존 `UNKNOWN(original parity)`.
- Fast 첫 실행은 1,218 passed·5 skipped·1 failed in 784.54s였으며, 실패는 삭제된 내부 helper `scale2x_env` 이름을 기대한 stale source-scan assertion이었다. 이를 `g_hd_source_mode == 2u`로 갱신하고 관련 targeted pytest 17 PASS·ruff PASS를 확인했다. 갱신된 source를 포함하는 전체 Fast 재실행 결과는 STATUS에 기록한다.
- Middle은 C 파일 내 `GetEnvironmentVariableA`가 각 `initialize_environment()` 안에만 있는지, compose loop가 `_env`/`_enabled` 호출을 하지 않는지, process-start 환경 주입 가정과 trace/raw 계산을 확인한다. Fast 결과는 STATUS에 있다.

## 경계

판정이 P3 HOLD/FAIL이면 원인과 좁은 다음 조치를 적고 P4로 전환하지 않는다. P3 PASS여도 다음 작업은 strategy가 정할 P4 판정이며, G1 사용자 승인이나 미해결 minimap/production을 PASS로 바꾸지 않는다.
