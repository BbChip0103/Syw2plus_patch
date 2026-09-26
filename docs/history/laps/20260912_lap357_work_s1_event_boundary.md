# 2026-09-12 | lap 357 | G1 / S1 load event-boundary adapter

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션 / 정확한 모델 ID 미주장 / high / work.
- 목표 / 가설: lap356 middle이 지적한 N15를 한 가지 수리한다. live S1은 pre PS35 직접 read 뒤
  승인된 trigger를 정확히 한 번 호출하고, 단일 bounded PS3 wait가 성공한 뒤에만 post snapshot을
  읽어야 한다. trigger가 없거나 count/대기/read가 불완전하면 PASS가 아니어야 한다.
- 예상 PASS / FAIL 조건: 정상 합성 순서가 `pre → trigger(1) → PS3 wait → post`이고 evaluator가
  기존 8×6 raw/fixture·pre/post 변화 조건을 유지하면 PASS. trigger 보고 0/2회, PS3 timeout,
  wait 부분 read, trigger 부재, 즉시 pre→post 경로는 모두 UNKNOWN/비-PASS.
- 변경 파일 / source fingerprint / 커밋: `tools/s1_load_evidence.py`, `tools/runtime_env.py`,
  `tests/test_s1_load_evidence.py`, `docs/STATUS.md`, 이 기록. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
  최종 SHA: `runtime_env.py=357ba0a7beb657ce6c7a174d9323c4254f2d696b74277a974e15a5216d272b7372c`,
  `s1_load_evidence.py=fffc644495b442627a8166125365caa6270999ff06bead52d2b1e1a8ad90fa65`,
  `test_s1_load_evidence.py=7508e5c1fe3b6110336d3b1457381f4d208d632f361ff8c842309b18ad6cb8c7`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보·게임 실행 없음;
  Linux/Python 합성 fixture; 실제 활성 플레이어·지도·군대 N/A. 보호 save000 fixture
  3,093,902 bytes, SHA `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`.
- 구현: `collect_load_event_boundary()`가 direct pre PS35를 확인하고 trigger를 한 번만 호출한다.
  trigger가 보고한 invocation count가 있으면 1인지 확인하며, PS WORD만 기존
  `PROGRAM_STATE_ADDRESS`에서 단일 deadline으로 기다린다. PS3 관측 전 post PlayerStruct를 읽지
  않으며, 기존 `runtime_driver.read`·reader·evaluator·offline `--post-json` 분리는 보존했다.
  trigger가 없는 live `--pid` 호출은 읽기 없이 UNKNOWN으로 닫힌다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `./.venv/bin/python -m pytest -q
  tests/test_s1_load_evidence.py` → 21 passed; `./.venv/bin/python
  docs/history/laps/probes/20260912_lap354_middle_lap353_s1_reader_review_probe.py` → rc0,
  `failures=[]`; `make check` → 399 passed in 63.37s, Ruff/compileall/mypy/`CONTEXT_PASS`;
  `bash checks/safety.sh check` → `SAFETY_PASS`; `make doctor` → original `verified`,
  `Syw2plus/syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  PNG·클릭·Wine·Xvfb·실제 게임/load 실행 0회; binary patch 생성/원복 대상도 없었다.
- 측정값 / 판정: synthetic 정상 boundary는 trigger 1회와 pre/wait/post 순서를 통과하며 기존
  evaluator PASS를 유지한다. trigger 0/2 보고, PS3 timeout, wait 부분 read는
  `S1EventBoundaryError`로 fail-closed; trigger 없는 runtime wrapper는 `READER_READ_FAILURE`와
  `event_boundary=EVENT_TRIGGER_MISSING`을 남기고 memory read 0회. 기계/합성 범위 PASS.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap354 F1~F4 독립 probe와 Fast/safety는
  fresh PASS. 다음 새 middle(Sol/Opus5)이 변경 SHA·adapter 순서·회귀·Fast/safety를 독립 검수해야
  한다. 실제 approved load trigger/좌표, private load/open, 두 run 결정성, S1 (A)+(B), WM_CLOSE,
  Stage B, 제품 G1 및 G2~G4는 UNKNOWN. 사용자 마일스톤 승인 0.
- 다음 한 가지: 새 middle의 독립 검수 전까지 게임/Wine/Xvfb/클릭/PNG/실제 run을 실행하지 않는다.

## Erratum — lap359 provenance correction

lap357의 변경 파일 목록에 적힌 `tools/runtime_env.py` SHA는 앞에 lap 번호 `357`이
잘못 붙은 67-hex 문자열이었다. 원문과 기존 검수 기록은 보존하며, 현행 파일의 정확한
64-hex SHA는 `ba0a7beb657ce6c7a174d9323c4254f2d696b74277a974e15a5216d272b7372c`이다.
`s1_load_evidence.py`와 `test_s1_load_evidence.py`의 SHA는 lap357 기록과 변함없이
각각 `fffc644495b442627a8166125365caa6270999ff06bead52d2b1e1a8ad90fa65`,
`7508e5c1fe3b6110336d3b1457381f4d208d632f361ff8c842309b18ad6cb8c7`이다.
이 정정은 provenance만 고치며, lap357의 독립 검수 ACCEPT나 실제 실행 증거를
승격하지 않는다.
