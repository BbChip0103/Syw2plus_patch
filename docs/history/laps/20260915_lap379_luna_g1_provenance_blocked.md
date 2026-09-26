# 2026-09-15 | lap 379 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션, 정확한 모델 ID 미노출·미주장 / 사용자 지정 high / Luna 실무 구현 작업자.
- 목표 / 가설: lap378 §3대로 lap373 raw log에서 lap372 exact pre-image와 endpoint diff를 물질화하면 다음 middle의 독립 검수 입력을 만들 수 있다. expected SHA와 실제 역복원 SHA가 모두 일치해야 PASS다.
- 변경 파일 / 원본·후보 SHA / 커밋: 새 provenance artifact만 추가했다. production `tools/runtime_env.py=2d4e478f073f1e4c981b42c39e0cff6a8ba0f058217a5d8e1aec0377b1ca790e`, `tools/s1_load_evidence.py=44e8c1a70372d0748b19497f3d7c91249807ff3600701ba238aa6e3fac2c4861`, `tests/test_s1_load_evidence.py=69e714045a464f6c047099c479929ba8bec4f64108b102a0036252d2558b755d`는 불변. 커밋 0.
- artifact: `docs/history/laps/snapshots/20260915_lap379_lap372_preimage_recovery/`에 두 pre-image, `runtime_endpoint.diff`, `test_endpoint.diff`, `manifest.json`을 보존했다. source log는 `logs/laps/2026-09-14/lap-0373.log`, SHA `3ee03b31f1fbf96797e0b5c8a38573c0888b660590c8afd131c3a3b203d7fb0c`다.
- 실행 / 측정: 현행 endpoint와 artifact를 `diff -u`로 비교했다. runtime pre-image `2d957c43...f2ac5ce`는 lap372 기대값과 일치(PASS), 5 hunks/+9/-8. test pre-image는 `3ee382ed70a260ec5797e37d27df747238af6b88db0f52322537ab17c7497af1`로 관측되어 기대 `d53e5cde...dc2958f`와 불일치(FAIL), 2 hunks/+25/-2.
- 판정: **BLOCKED/ESCALATE**. diff 내용은 raw log의 lap373 patch와 일치하지만 test expected SHA와 충돌한다. 재핀·추측 수정·production 변경을 하지 않았다. 필수 targeted/lap354/doctor/Fast/safety와 게임/Wine/Xvfb/input/PNG 실행은 SKIP.
- 다음 작업자: Sol/Opus5가 raw log의 test pre-image 원문·line 714 주변 내용·SHA 계산을 독립 재검수하고 `d53e5cde`와 `3ee382ed` 중 어느 provenance가 유효한지 판정하라. 판정 전 원본 n=1·Stage B·마일스톤 이동 금지.
