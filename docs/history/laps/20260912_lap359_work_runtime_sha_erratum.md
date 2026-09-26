# 2026-09-12 | lap 359 | G1 / runtime provenance erratum

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션 / 정확한 모델 ID 미주장 / high / work.
- 가설 / 사용자 관찰: lap357의 `runtime_env.py` SHA는 lap 번호가 앞에 붙은 기록 오기이며,
  현행 파일은 lap358이 관측한 64-hex SHA와 일치한다.
- 예상 PASS / FAIL 조건: lap357 원문을 삭제하지 않고 erratum을 추가하며 STATUS의 현재 SHA가
  세 현행 파일과 일치하면 PASS. 원문 소실·SHA 불일치·필수 Fast/safety 실패면 STOP/UNKNOWN.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/history/laps/20260912_lap357_work_s1_event_boundary.md`에 삭제 없는 Erratum 추가,
  `docs/STATUS.md`의 현행 SHA/N16·검증·바퀴 기록 정정, 이 기록, `loop/ESCALATE_SOL` handoff 갱신.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`). 제품 코드/tests/EXE/DLL/save/pin/baseline/golden 변경 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (`make doctor`, verified).
  현행 `runtime_env.py` `ba0a7beb657ce6c7a174d9323c4254f2d696b74277a974e15a5216d272b7372c`,
  `s1_load_evidence.py` `fffc644495b442627a8166125365caa6270999ff06bead52d2b1e1a8ad90fa65`,
  `test_s1_load_evidence.py` `7508e5c1fe3b6110336d3b1457381f4d208d632f361ff8c842309b18ad6cb8c7`.
  Linux 정적 문서/바이트 검증; 게임 실행·활성 플레이어·지도·군대·fixture N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: SHA/원문 보존 assertion 및 `git diff --check` PASS;
  `make check` rc0, 399 passed(62.43s), Ruff/compileall/mypy/CONTEXT_PASS;
  `bash checks/safety.sh check` rc0 `SAFETY_PASS`; `make doctor` rc0, original verified,
  runtime manifest absent로 runtime `ok=false`를 보고했으나 side effects=false. Wine/Xvfb/입력/PNG/
  실제 private load/open/후보 run 0회.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): provenance erratum과 STATUS 정정 **PASS**;
  lap357 원문 오기 줄은 보존됨, STATUS 126줄(130 이하). lap357 구현의 독립 검수 ACCEPT 및
  제품 G1/Stage B/S1 결정성은 아직 **UNKNOWN**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 코드 회귀 없음; 새 middle이 세 SHA 선행
  대조 후 adapter 순서, trigger 0/2회·timeout·부분 read fail-closed, targeted/Fast/safety를
  fresh 독립 검수해야 한다. 실제 load/open·두 run 결정성·WM_CLOSE·G1~G4·사용자 승인 0.
- 다음 한 가지: 새 middle의 fresh 독립 검수 전까지 게임/Wine/Xvfb/클릭/PNG/실제 run을 실행하지 않는다.
