# 2026-09-12 | lap 371 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션, 정확한 모델 ID 미노출·미주장 / 사용자 지정 high / Luna 실무 작업.
- 가설 / 사용자 관찰: cleanup 실패가 evidence를 UNKNOWN으로 강등해도 내부 `error`가 없어 direct function과 원본 S1 CLI가 성공 rc를 반환하던 lap370 결함을, cleanup 오류 전파와 command 상태 rc 게이트로 닫을 수 있다.
- 예상 PASS / FAIL 조건: cleanup 실패 direct call nonzero, artifact top-level UNKNOWN 보존, `g1-s1-original-load-evidence` non-PASS rc=2, prepare60/launch40/input20/pre2/post3/total150 near-boundary PASS, targeted→lap354→Fast→safety PASS.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/runtime_env.py`, `tests/test_s1_load_evidence.py`; pre-edit snapshot은 `docs/history/laps/snapshots/20260912_lap371_pre_edit/`에 보존. pre SHA `runtime_env.py=5e7c769c…d37d185`, `test_s1_load_evidence.py=cf919a73…d71fa`; post SHA `runtime_env.py=2d957c43…f2ac5ce`, `test_s1_load_evidence.py=d53e5cde…dc2958f`; 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE/save와 후보는 접근·실행하지 않음. Linux `.venv`, fake clock/process/input/cleanup 합성 fixture; 활성 플레이어·지도·군대 N/A; game/Wine/Xvfb/input/PNG 0회.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 편집 전 SHA 및 snapshot; `.venv/bin/python -m pytest -q tests/test_s1_load_evidence.py` → **51 passed**; repo-root `env -u PYTHONPATH .venv/bin/python -c 'import tools.runtime_env as m; print(m.__file__)'` → 현재 저장소 경로; lap354 probe 정확히 1회 → rc0/`failures=[]`; `make check` → **429 passed**, Ruff/compileall/mypy/CONTEXT_PASS; `.venv/bin/python checks/safety.py` 및 `bash checks/safety.sh check` → `SAFETY_PASS`; pre/post `git diff --no-index` 실측.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): cleanup failure artifact `status=UNKNOWN`, `classification=CLEANUP_FAILURE`, direct function `RuntimeSafetyError`, mocked original command rc=2; 5개 stage near-boundary와 total near-boundary PASS; **work PASS**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: cleanup 실패 artifact 원문 보존·non-overwrite·exact-once를 유지했다. 실제 원본 S1 load, 두 run 결정성, Stage B, WM_CLOSE, G1~G4와 사용자 마일스톤 승인은 여전히 UNKNOWN. 다음 새 Sol/Opus5 middle이 세 SHA·snapshot diff·targeted·lap354·Fast·safety를 독립 검수해야 한다.
- 다음 한 가지: 새 middle이 lap371 work의 SHA/diff와 cleanup-failure rc 및 여섯 cap 경계 회귀를 fresh 독립 검수한다. 그 전 실제 원본 n=1·Stage B·마일스톤 이동은 금지.
