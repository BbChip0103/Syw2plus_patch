# 2026-09-12 | lap 363 | 목표 G1

- 실제 역할/모델: hands-on work 구현자. 현재 세션 모델 ID는 노출되지 않아 특정 모델을 주장하지 않음; 외부 provider 호출 0.
- 목표/가설: `G1_S1_MIDDLE_EXECUTION_ENVELOPE_LAP362.md` §3만 발효한다. 기존 오프라인/`--pid` lane은 보존하고, 원본 save000 단일-load command가 private copy부터 owned cleanup까지 한 번만 소유하도록 한다.
- 변경 파일: `tools/runtime_env.py`, `tools/s1_load_evidence.py`, `tests/test_s1_load_evidence.py`; `docs/STATUS.md`와 이 기록. 새 의존성·EXE/DLL/save/pin/reference/golden 변경·커밋 0.
- 원본/후보 SHA: 보호 원본 EXE 1,032,192 B / `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; save000 3,093,902 B / `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`; 이번 바퀴 후보 실행 없음.
- 구현: `g1-s1-original-load-evidence --source --runtime-root` 추가. prepare 기반 새 private copy/prefix, EXE/save000 size·SHA gate, PS9→PS35 1회 입력, direct pre PS35/group0/slot1·origin·8×6 gate, crop+(400,131) 무배율 load trigger 1회, PS3 10초 wait, 150초 hard/10초 cleanup reserve, Python 2개+input helper snapshot, 새 artifact와 owned child/prefix/Xvfb cleanup을 기록한다. `collect_load_event_boundary`는 pre snapshot 재사용·precondition·절대 event deadline·post 3초 cap을 지원하며 offline/`--pid` 의미는 유지한다.
- 검증 명령/결과: `python3 -m pytest -q tests/test_s1_load_evidence.py` 24 passed; `make check` 402 passed, Ruff/compileall/mypy/CONTEXT_PASS; `python3 checks/safety.py` 및 `bash checks/safety.sh check` 모두 `SAFETY_PASS`; `.venv/bin/python docs/history/laps/probes/20260912_lap354_middle_lap353_s1_reader_review_probe.py` rc0, `failures=[]`. fixture SHA는 pinned 값과 일치하고 current-repo `runtime_env`/reader 결선 F1~F4가 통과했다. 실제 게임/Wine/Xvfb/클릭/PNG 실행 0회.
- 변경 후 SHA: `tools/runtime_env.py`=`ce873c731cca05391352d2451d9b876cf553e8e2cbe12020555a61955ab0990f`; `tools/s1_load_evidence.py`=`3ea94dde52e185ba15ca11cbb1433f029b6d58dae383493dd83694a9d503f1ca`; `tests/test_s1_load_evidence.py`=`9b1319c50546da3235b9fbfae578b3448381dfcba545c2b6c6f70c75145e667b`.
- 판정/한계: 기계 검증 PASS. 제품 G1, S1 두 run 결정성, 실제 open/load, WM_CLOSE, Stage B, G2~G4와 사용자 마일스톤은 UNKNOWN이며 이 work가 승인/출시를 의미하지 않는다. 기존 `loop/ESCALATE_SOL` 및 W3/N14/영구 probe 반려는 수정하지 않았다.
- 다음 한 가지: 새 middle/Sol 세션이 세 허용 파일의 §3 구현, 전후 SHA, targeted·lap354·Fast·safety 결과와 no-game 범위를 독립 검수한다.
