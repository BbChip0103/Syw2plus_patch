# 2026-09-12 | lap 355 | G1 / S1 load-evidence reader wiring

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션 / 정확한 모델 ID 미주장 / high / work.
- 목표 / 가설: lap354 middle의 F1~F4 REJECT를 한 가지 수리한다. private
  `runtime_driver.read`가 group WORD, selected index, PS WORD, PlayerStruct 8×6을 pre/post 직접
  읽고, 그 provenance와 변화 및 고정 fixture 일치 없이는 load 완료 PASS를 만들 수 없게 한다.
- 예상 PASS / FAIL 조건: production wrapper가 `read_post_player_structs()`를 실제 호출하고
  `GROUP_WORD_ADDRESS`/`PROGRAM_STATE_ADDRESS`를 읽으면 PASS. caller가 JSON으로 복사한
  `ps=3/open_succeeded=true/raw_hex`만 주면 UNKNOWN. pre==post·부분 read·reader 오류도 PASS 금지.
- 변경 파일 / source fingerprint / 커밋: `tools/s1_load_evidence.py`, `tools/runtime_env.py`,
  `tests/test_s1_load_evidence.py`, `docs/STATUS.md`, 이 기록. 커밋 없음(`LOOP_ALLOW_COMMITS=0`);
  working tree의 기존 untracked 상태는 보존했다.
- 구현: S1 snapshot이 group `0x0066966C`, selected index `0x01086C16`(dialog object
  `0x01086278 + 0xF9E`), PS `0x004ED818`, PlayerStruct base `0x00956770`/stride
  `0x3ABC`를 exact-width로 읽고 read points를 기록한다. in-process collector token으로
  외부 JSON을 분리하고 pre/post raw 및 PS 변화를 요구한다. `--pid` CLI는 `--manifest`와
  private Wine-prefix PID 소유 확인 없이는 읽지 않는다. 기존 offline evaluator와 R1은 분리했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보·게임 실행 없음;
  Linux/Python 합성 fixture; 실제 활성 플레이어·지도·군대 N/A. 보호 save000 fixture
  3,093,902 bytes, SHA `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `./.venv/bin/python -m pytest -q
  tests/test_s1_load_evidence.py` → 15 passed; lap354 독립 probe
  `docs/history/laps/probes/20260912_lap354_middle_lap353_s1_reader_review_probe.py` → rc0,
  F1~F4 모두 통과, stdout은 보존하지 않은 콘솔 결과. `make check` → 393 passed in 62.54s,
  Ruff/compileall/mypy/`CONTEXT_PASS` PASS; `checks/safety.sh check` → `SAFETY_PASS`.
  PNG·클릭·Wine·Xvfb·실제 게임 실행 0회.
- 측정값 / 판정: 정상 direct pre PS35→post PS3, 8개 post raw fixture 일치 합성은 PASS;
  copied caller payload는 UNKNOWN/`UNTRUSTED_READER_EVIDENCE`; pre==post는 UNKNOWN/
  `PRE_POST_NO_CHANGE`; direct read failure는 UNKNOWN/`READER_READ_FAILURE`. 독립 F1~F4 rc0.
  최종 파일 SHA: `tools/runtime_env.py`=`77aaf0deb142520ac11e6381894a1cbc60ec13b5149230875792dd1eed12a38b`,
  `tools/s1_load_evidence.py`=`157778e62ea61efd40ed58df96c9be9661e3ac0eab9adeb57e56c0aaa83c0924`,
  `tests/test_s1_load_evidence.py`=`91bc905995e146f9f094ecce17f4ec6c20e71bfbdd554058f57cd42423e1c30e`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap354 REJECT는 이력에 보존했다. 실제
  private load/open 성공·slot input·두 run 결정성·S1 (A)+(B)·WM_CLOSE·Stage B·제품 G1 및
  G2~G4는 UNKNOWN. 다음 새 Sol/Opus5 middle이 변경 SHA, 직접 reader 결선, 회귀·Fast·safety를
  독립 검수해야 한다. 사용자 마일스톤 승인 0.
- 다음 한 가지: 새 middle 독립 검수 전 게임/Wine/Xvfb/클릭/PNG/추가 실행 0회를 유지한다.
