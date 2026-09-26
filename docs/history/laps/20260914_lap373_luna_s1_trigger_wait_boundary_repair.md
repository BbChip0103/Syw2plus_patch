# 2026-09-14 | lap 373 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션, 정확한 모델 ID 미노출·미주장 / 사용자 지정 high / Luna 실무 작업.
- 가설 / 사용자 관찰: lap372 REJECT의 PS3 wait 계측이 trigger 시작부터 측정되어 trigger 5초를 wait cap에 중복 포함한다. trigger 완료 시각을 PS3 wait 시작점으로 분리하면 개별 cap과 total150 경계를 함께 닫을 수 있다.
- 예상 PASS / FAIL 조건: trigger stage 5초와 PS3 wait 10초가 분리되고, 합계 149.998초 fake-clock command가 PASS, total 초과 command가 rc=2·PASS artifact 없음, 기존 cleanup/exact-once 계약과 Fast/safety가 PASS여야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/runtime_env.py`와 `tests/test_s1_load_evidence.py`만 수정. runtime=`2d4e478f073f1e4c981b42c39e0cff6a8ba0f058217a5d8e1aec0377b1ca790e`, s1=`44e8c1a70372d0748b19497f3d7c91249807ff3600701ba238aa6e3fac2c4861`, test=`69e714045a464f6c047099c479929ba8bec4f64108b102a0036252d2558b755d`; commit 없음, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보·게임 없음. Linux `.venv` fake clock/process/input/cleanup 합성 fixture, save000 fixture `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`; 활성 인원·지도·군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor` `ok=true`, 보호 원본 verified, runtime manifest absent/side_effects=false; 사전 targeted `tests/test_s1_load_evidence.py` 51 passed; 편집 후 targeted 52 passed; repo-root import 고정 lap354 probe 정확히 1회 rc0/`failures=[]`; `make check` 430 passed/67.07s, Ruff/compileall/mypy/CONTEXT_PASS; `.venv/bin/python checks/safety.py` 및 `bash checks/safety.sh check` 각각 `SAFETY_PASS`. 로그·PNG 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): trigger 종료 시각을 저장해 PS3 wait stage를 그 이후부터 계산하도록 변경. near-boundary fake clock `60+40+20+2+5+9.999+3+9.999=149.998`초 PASS 및 clock assertion PASS. 같은 구성 cleanup `10.001`초는 실제 `runtime_main` rc=2이며 artifact 미설치 PASS. work 범위 **PASS**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 실제 original S1 load, 두 run 결정성, S1 (A)+(B), Stage B, WM_CLOSE, G1~G4, 사용자 마일스톤 승인은 UNKNOWN. 원본/후보/Wine/Xvfb/input/PNG/patch bytes 변경·실행 0.
- 다음 한 가지: 새 Sol/Opus5 middle이 lap373 전후 SHA/diff와 trigger/wait·total150 회귀, lap354 probe, Fast, safety를 fresh 독립 검수한다. 그 전 원본 n=1·Stage B·마일스톤 이동 금지.
