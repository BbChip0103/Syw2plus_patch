# 2026-09-11 | lap 7 | loop escalation 반환코드 terminal 수리

- 실제 provider/model/effort / 지정 역할: Codex; 런타임이 현재 대화 모델의 실제 ID를 노출하지 않음 / 지정 역할 Luna/high hands-on work.
- 가설 / 사용자 관찰: `run_lap`의 명시적 `rc=75`가 `main`의 일반 실패·max-laps 경로를 거치지 않고 호출자에게 terminal로 전파되어야 한다.
- 예상 PASS / FAIL 조건: N=2 실행에서도 worker 1회, middle 자동호출 0회, `ESCALATE_SOL` 보존, 최종 exit75; generic worker failure/STOP/dry/FULL_TEST 의미는 기존 회귀가 유지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `loop/loop.sh`, `tests/test_model_routing.py`만 코드 변경; `loop/ESCALATE_SOL`, `docs/STATUS.md`, 이 기록은 상태/이력 기록; uncommitted/unborn HEAD. `loop/loop.sh` 후보 SHA `08fe918a2b5a2bda5b7b1564b6af27503704c70adde9ba4b70579d94b1cfcfec`, `tests/test_model_routing.py` 후보 SHA `449f5459edef7ef72b8b61f59d655031ea1db61b81598ada52e434eb85441013`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 코드 원본 SHA는 수리 카드의 `loop/loop.sh` `d25baa1da48597bb521fa0977e65558776b708daa1a6dda9fadd76e9e897e8e9`, `tests/test_model_routing.py` `0e9f2736d8b64394dcd99f62d60c2643f7b091fbbf07267b9d9246c696fe7c9d`; 후보 SHA는 위와 같음. `.venv` pytest, 임시 복사 프로젝트, local original guard fixture 사용; 실제 게임/플레이어/지도/군대 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_model_routing.py::test_worker_escalation_stops_for_explicit_middle_review`; `.venv/bin/python -m pytest -q tests/test_model_routing.py tests/test_patch_loop.py`; `make check`. 게임 실행·캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): targeted **1 PASS**; 인접 **24 PASS**; 전체 pytest **82 PASS**, Ruff PASS, compileall PASS, mypy 8 files PASS, `CONTEXT_PASS`; 전체 Fast **PASS**. 강화 회귀는 `LOOP_MAX_LAPS=2`/`run 2`에서 codex 호출 1회, claude 호출 0회, marker 유지, subprocess exit75를 확인.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `main`의 lap 후 safety check 직후 `rc=75` terminal 분기를 추가하고 기존 generic failure 경로는 건드리지 않았다. 새 Sol/Opus5 middle 독립 검수와 사용자 마일스톤 승인은 없음. G1~G4, 실제 앱/24k/144k, 멀티, 원본/후보 시각·입력은 미검증.
- 다음 한 가지: 새 Sol/Opus5/high middle 세션이 수리 diff와 targeted/N=2 및 전체 Fast 결과를 독립 재실행·판정하고, 통과 기록 후에만 G1-A 재개 여부를 결정한다.
