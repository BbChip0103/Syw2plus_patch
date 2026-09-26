# 2026-09-11 | lap 6 | loop escalation 반환코드 middle 진단

- 실제 provider/model/effort / 지정 역할: Codex; 런타임이 정확한 모델 ID/effort를 노출하지 않아
  `gpt-5.6-sol/high` 실제값은 미확인 / 사용자 지정 middle 진단·계획·확인 역할만 수행.
- 가설 / 사용자 관찰: `run_lap`에서 생성한 escalation `rc=75`가 `main`의 bounded-loop 종료에서
  exit 0으로 덮이며, 명시적 middle review 요청이 호출자에게 실패로 전파되지 않는다.
- 예상 PASS / FAIL 조건: 현재 테스트로 동일 exit0을 재현하고 제어흐름에서 단일 원인을 확정해
  Luna가 구현할 최소 파일·동작·회귀식을 정하면 진단 PASS; 증거가 충돌하면 UNKNOWN으로 재승격한다.
- 변경 파일 / source fingerprint / 커밋: `docs/work/active/LOOP_ESCALATION_RETURN_CODE_REPAIR.md`,
  `docs/STATUS.md`, 이 기록, `loop/ESCALATE_SOL`; 게임/tools/tests/loop 코드 수정 없음;
  uncommitted/unborn HEAD. 검사 전 SHA: `loop/loop.sh`
  `d25baa1da48597bb521fa0977e65558776b708daa1a6dda9fadd76e9e897e8e9`,
  `tests/test_model_routing.py` `0e9f2736d8b64394dcd99f62d60c2643f7b091fbbf07267b9d9246c696fe7c9d`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 후보 없음;
  pytest 임시 Git 복사본과 로컬 original guard fixture만 사용; 실제 게임/플레이어/지도/군대 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: lap5 기록·표식·현재 source SHA 대조;
  `.venv/bin/python -m pytest -q tests/test_model_routing.py::test_worker_escalation_stops_for_explicit_middle_review`;
  `make check`. 캡처 없음, 게임 실행 없음.
- 측정값 / 판정: lap5 기록 해시 7개 모두 현재 파일과 일치. targeted **1 FAIL**(pytest exit1)은
  내부 `rc=75`의 `연속 실패 1/5` 뒤 `max-laps(1)` 종료와 subprocess exit0을 재현했다.
  제어흐름상 원인은 **CONFIRMED**: `run_lap`은 marker를 보고 75를 반환하지만 `main`은 이를
  terminal escalation으로 분기하지 않고 max-laps에서 exit0으로 덮는다. N>1 work 재호출 위험도 있다.
  진단/수리 범위는 **PASS**, 제품/Fast는 FAIL.
- Fast: `make check` **81 PASS, 1 FAIL**, make exit2. 유일 실패는 위 escalation 테스트다.
  예상된 기존 필수 gate 실패를 재현한 것이며 통과로 승격하지 않는다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: Luna는 `rc=75`만 안전 검사 직후 terminal로
  전파하고 generic worker failure retry·STOP·dry/FULL_TEST 의미를 유지해야 한다. N=2 work 1회,
  middle 자동호출 없음, marker 보존, exit75를 검증해야 한다. 이후 새 Sol 독립 확인과 사용자
  마일스톤 판단은 별도다. G1-A/G1 및 실제 앱은 미검증.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high가 수리 카드의 `loop/loop.sh`와 관련 테스트만
  최소 수정하고 targeted·인접·전체 Fast를 실행한다. 실패 시 재시도/게임 실행 없이 다시 승격한다.
