# 2026-09-29 | lap 768 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Codex hands-on work session; runtime role `work`.
- 가설 / 사용자 관찰: 진단 조건 `0x97597c=1`에서 원본20/v10 50이 미니맵 좌클릭을 이동·공격·순찰 모드별로 선택 전원에게 전달한다.
- 예상 PASS / FAIL 조건: 각 모드에서 선택 전원의 `pending_xy`가 변하고, 원본과 후보의 명령 신호가 대응하며, 크래시·원본 변경이 없어야 PASS.
- 변경 파일 / source fingerprint / 커밋: `tools/g5_minimap_click_hittest_probe.py`, `tests/test_g5_minimap_click_hittest_probe.py`; 각각 `be74e7554908b620d2db44304db04d513e1098bdaf49f85534b19e3a72d6b415`, `0af118ee47d29f9ed2c308f2de2745e525b2fe452679ce8b9a6ae6222394d198`; uncommitted, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; v10 `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`; 새 game copy/prefix/1600x1200 Xvfb, 1인 solo, 기존 맵, owner0/type2 55기 fixture(원본 선택20, 후보 선택50).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. .venv/bin/python -m tools.g5_minimap_click_hittest_probe --variant {original,candidate} --force-gate-flag ...`; 로그 `logs/gates/lap768-minimap-modes-{original-r2,candidate}.log`, 결과 JSON `.../20260929_lap768_minimap_modes_{original_r2,candidate}/probe-result.json`, JSON SHA 각각 `af44986f629c78fcfe6b7819bd711c533afeeec1dd22deefcc099dd0e2baf88d`, `145e281f0a7abc9c77b51782025ac875ad0b0d166f1fb365ac6341f7460e5c0d`.
- 측정값 / 판정: 원본 이동/공격/순찰 `pending_xy` 20/20·20/20·20/20; v10 50/50·50/50·50/50. 양쪽 gate 0→1, LUT non-FF 16200, trace fatal 없음, alive/cleanup/source unchanged PASS. 원시 명령 신호는 move command3, attack pending4 관측, patrol command35로 양쪽 대응. probe 상태는 각각 `PASS_MINIMAP_MODES_ORIGINAL/CANDIDATE`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 집중 pytest 5 passed, `make check` 1136 passed·5 skipped, ruff/compileall/mypy/context/`SAFETY_PASS`; 실행 game 사본은 삭제하고 prefix/manifest/log/capture/JSON 보존. `0x97597c=1`은 진단 write라 정상 game_type UI 경로·멀티·G5 A~H 독립 검수·사용자 3단 승인은 미검증.
- 다음 한 가지: middle/승격 작업자가 lap768 raw와 v10 2단 `PASS_WITH_LIMITS` 제한을 독립 재검수한 뒤 사용자 G5 3단 판단에 재상정한다. G1 재개·G5 종료는 사용자 판단 전 금지.
