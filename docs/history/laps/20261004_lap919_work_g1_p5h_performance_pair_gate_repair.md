# 2026-10-04 | lap919 | G1 P5-H performance pair gate repair

- 실제 provider/model/effort / 지정 역할: hands-on work (Luna/high 지정; 실제 API metadata는 미노출, 다른 역할 승인 주장 없음).
- 목표/가설: lap918가 확정한 누락을 최소 수리한다. `--performance-window` 요청 시 `performance_comparison.status != PASS` 또는 누락은 pair `PASS`와 exit0을 막고, 옵션 미요청은 종전 동작을 유지한다.
- 변경 파일: `tools/g1_saved_scene_probe.py`, `tests/test_g1_saved_scene_probe.py`, 본 기록, `docs/STATUS.md`. source SHA256 `09b2862ccb24406b2b96ac9931da7f8c37a0e3abbc2a2070c382b16ef197f397`; tests SHA256 `ee2fca2f5df1603828a6cd75d3baf5dc5a214da2ce2a8d76fd9da41adb99b3f7`. Uncommitted; commit 없음.
- 원본/fixture: `make doctor`에서 원본 EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` verified. 읽기 전용 C2 `pair-result.json` SHA256 `6578c16122ee1b26dfe9a351fd36333b9fd76ea037f35095aeaeabb1720ca673`; 기존 raw는 변경하지 않았다. 파일의 기존 pair status `PASS`, 성능 비교 `FAIL`; 수정 코드로 재판정 `HOLD`.
- 구현/회귀: 기존 최종 gate를 `_pair_status`로 모으고 requested flag를 반영했다. FAIL, INVALID, missing은 HOLD, PASS는 기존 pair gates 모두 PASS일 때 PASS, performance 미요청·comparison 부재는 PASS하는 단위 테스트를 추가했다.
- 실행/검증: `.venv/bin/python -m pytest -q tests/test_g1_saved_scene_probe.py` — **146 passed / 5.40s**; `make lint` PASS; `make typecheck` PASS; `make doctor` 원본 verified, 그러나 `local/runtime/manifest.json` absent와 `RuntimeSafetyError`로 runtime manifest rejected; `.venv/bin/python checks/safety.py check` `SAFETY_PASS`; `.venv/bin/python checks/context_limits.py` `CONTEXT_PASS`.
- runtime: fresh GREEN→연속 B′2→C3은 SKIP. isolated runtime manifest가 없고 `make doctor`가 전용 run manifest를 안전하지 않은 상태로 거부했다. 기존 Wine/Xvfb 세션에는 연결하지 않았다. 관측상 free disk 22 GB. 이는 새 runtime 결과가 아니다.
- 예상 PASS/FAIL 판정: 성능 consumer gate 회귀 PASS, 실제 historical C2 성능 결과는 `FAIL` 그대로이며 pair 결과는 새 판정 `HOLD`; C2 원인·새 source의 B′/C 반복성·P5-H acceptance/G1은 미검증·HOLD.
- 다음 한 가지: 격리 runtime manifest가 유효하고 안전할 때 같은 H2/PH-a–d/V1/V2/V2s/V2q/snapshot/input/30-present/C20s 조건으로 fresh GREEN→연속 B′2→C3 실행; C2 성능 임계값을 유지한다.
