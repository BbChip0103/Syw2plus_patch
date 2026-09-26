# loop escalation 반환코드 수리 카드

2026-09-11 lap6, Codex middle 진단. 판정: **APPROVE FOR WORK REPAIR**.
게임/G1-A 실행 승인이 아니며, 아래 Fast가 모두 PASS한 뒤 새 middle 세션이 독립 확인한다.

2026-09-11 lap8, 새 middle 독립 검수 판정: **CONFIRM FAIL / REVISE**.
lap7 후보의 기존 marker N=2 회귀와 전체 Fast는 PASS했지만 `main`이 marker 확인 없이 모든
`rc=75`를 terminal로 처리한다. marker 없는 worker 자체 exit75까지 일반 nonzero fail-streak/retry를
우회하므로 아래 보완을 같은 허용 파일 범위에서 Luna/high가 수행하고 다시 독립 확인받는다.

- 명시적 terminal 판정은 `ESCALATE_SOL` marker와 결합되어야 한다.
- marker 없이 exit75를 반환하는 fake worker 회귀를 추가한다. `LOOP_MAX_FAIL_STREAK=2`, `run 2`에서
  worker 2회, marker/middle 호출 없음, fail-streak STOP 및 최종 nonzero를 확인한다.
- 기존 marker 생성 N=2 회귀, STOP/dry/FULL_TEST, 아래 targeted·인접·전체 Fast 조건은 그대로 유지한다.

2026-09-11 lap10, 새 middle 독립 검수 판정: **CONFIRM BLOCKED / ESCALATE**.
lap9 후보 SHA와 marker 결합 분기, syntax, targeted 2 PASS, 인접 25 PASS, 전체 Fast 83 PASS는
재현했다. 그러나 lap9 raw exit75 회귀는 기본 fail-streak 5에서 `max-laps(2)`·exit0을 기대해,
바로 위의 `LOOP_MAX_FAIL_STREAK=2`·fail-streak STOP·최종 nonzero 계약을 검증하지 않는다.
더 최신의 명시적 승인 근거 없이 이 조건을 완화하거나 후보를 승인하지 않는다. 승격된 middle이
계약 provenance를 해소한 뒤 필요한 경우 Luna/high에 테스트 보완만 명시적으로 넘겨야 한다.

2026-09-11 lap11, 승격된 middle(Claude `claude-opus-5`/high) 계약 판정: **CONTRACT RESOLVED — 위 lap8 조건 유효**.
APPROVALS 확정 없음, INBOX 새 지시 없음, 개정 카드 없음, 커밋 0개로 lap8 조건을 대체하는 더 최신 명시
승인이 존재하지 않는다. lap9 기록의 `max-laps(2)`·exit0 기대값은 work tier의 자기 기대이며
`AGENTS.md`의 "실무 모델이 자기 결과를 최종 승인하지 않는다"에 따라 컨펌 조건을 대체하지 못한다.
정적 검토상 `loop/loop.sh`는 이미 이 조건을 만족할 수 있으므로(`:796` marker 결합, `:802-809`
fail-streak가 `:819` max-laps보다 앞, `loop/env.sh:113` 환경 override 가능) 남은 공백은
`tests/test_model_routing.py`의 회귀 하나뿐이다. 구현은 재수리하지 않는다.

- work tier는 `tests/test_model_routing.py`만 수정한다. `loop/loop.sh`는 건드리지 않는다.
- 새 회귀는 lap9 fixture + `LOOP_MAX_FAIL_STREAK=2`/`LOOP_MAX_LAPS=2`/`run 2`로, 최종 nonzero(예상 1),
  worker 2회·middle 0회, marker 미생성, `연속 실패 1/2`·`연속 실패 2/2`·`이유=fail-streak`,
  `loop/STOP` 생성, `max-laps(2)` 종료 아님을 확인한다.
- 기존 두 테스트는 유지한다. 새 회귀는 추가이지 대체가 아니다.
- 실측이 위와 다르면 기대값을 낮추지 말고 구현 결함으로 재분류해 승격한다.
- 상세 판정: `docs/history/laps/20260911_lap11_opus5_loopctl_contract_resolution.md`.

2026-09-11 lap13, 승격된 middle(Claude `claude-opus-5`/high) 게이트 판정:
**GATE FAILURE DIAGNOSED — 테스트 격리 결함, 구현 결함 아님**.
lap12의 1 FAIL은 `loop/env.sh:67`이 export한 `LOOP_MIDDLE_PROVIDER`에 `loop/env.local.sh:4`가 `claude`를
재대입해 pytest까지 상속되고, `tests/test_model_routing.py:40`의 `dry()`가 `dict(os.environ, ...)`로 이를
되들여오면서 `loop/env.sh:24`의 `codex` 기본값이 적용되지 않아 발생한다. `LOOP_WORKER`는 export되지 않으므로
`work`/`astra` 파라미터는 영향이 없고, 상속 집합이 실패 1개를 정확히 설명하며 잔여 실패는 0이다.
따라서 위 lap8/lap11 조건과 lap12 후보는 유효하고, **기대값을 낮추지 않는다**.
lap12 신규 회귀는 수집 17개·skip 0·`1 failed, 16 passed` 산술로 **DEDUCED-PASS**이나 실측은 아직 없다.
상세 판정: `docs/history/laps/20260911_lap13_opus5_test_isolation_diagnosis.md`.

2026-09-11 lap15, 새 middle(Codex `gpt-5.6-sol`/high) 독립 검수 판정:
**CONFIRMED — controller 반환코드 및 pytest 환경 격리 수리 완료**.
lap14 source SHA가 모두 일치했고 부모 `LOOP_*`가 존재하는 조건에서 targeted 17, combined 26,
전체 Fast 84 및 safety를 재실행해 모두 PASS했다. 최신 raw fixture는 worker 2회·middle 0회,
marker 없음·STOP 생성·최종 exit1·fail-streak 종료를 만족했다. 이 카드는 기술적으로 닫혔으며
G1-A 재개는 `docs/STATUS.md`의 다음 한 가지와 기존 G1-A 카드 범위만 따른다.

## work tier 보완 요구 (lap13 middle이 승인한 범위)

1. `tests/conftest.py`를 새로 추가하고, 상속된 `LOOP_*` 환경변수를 전부 제거하는 autouse fixture를 둔다
   (`monkeypatch.delenv(..., raising=False)` 등). `PATH`는 유지한다. 각 테스트가 명시적으로 넘기는
   `LOOP_*` override는 그대로 살아야 한다.
2. 기대값·기존 테스트·`loop/loop.sh`·`loop/env.sh`·`loop/env.local.sh`는 건드리지 않는다.
   `env.local.sh`의 실제 루프 라우팅(`middle=claude`)은 사용자 설정이므로 바꾸지 않는다.
3. 안전 확인: 제거해도 되는 이유는 `loop/env.sh`의 모든 `LOOP_*`가 `: "${X:=기본값}"` 형태라 제거 시
   저장소 기본값으로 복귀하기 때문이다. 상속에 의존하는 테스트가 없음을 grep으로 확인하고 기록한다.
4. `tests/test_patch_loop.py:32-40,148-156`도 같은 패턴이다. 1번 conftest로 함께 해소되는지 확인하고,
   해소되면 그 파일은 수정하지 않는다.
5. 아래를 이 순서로 실측하고 수치를 그대로 기록한다. 하나라도 실패하면 재시도하지 말고 승격한다.

```sh
.venv/bin/python -m pytest -q tests/test_model_routing.py
.venv/bin/python -m pytest -q tests/test_model_routing.py tests/test_patch_loop.py
make check
```

6. 특히 `test_raw_worker_exit75_without_marker_hits_fail_streak_stop`의 최종 nonzero(예상 1),
   worker 2회·middle 0회, marker 미생성, `연속 실패 1/2`·`연속 실패 2/2`·`이유=fail-streak`,
   `loop/STOP` 생성, `max-laps(2)` 아님을 **실측 출력으로** 남긴다. 연역 PASS를 실측으로 쓰지 않는다.
7. 게임/G1-A는 재개하지 않는다. 커밋하지 않는다(`LOOP_ALLOW_COMMITS=0`).

## 한 가지 원인과 범위

- 재현 계약: work 세션이 exit 0이더라도 `loop/ESCALATE_SOL`을 만들면 현재 lap은 `rc=75`가 되고,
  같은 `loopctl run N`에서 work를 재호출하지 않은 채 nonzero로 종료해야 한다.
- 확정 원인: `run_lap`은 표식을 보고 `rc=75`로 바꾸지만 `main`은 이를 일반 재시도 실패로만 센다.
  `N=1`에서는 뒤의 `max-laps` 분기가 `exit 0`으로 덮어쓰고, `N>1`에서는 다음 work lap을 실행할 수 있다.
- 허용 변경: `loop/loop.sh`, `tests/test_model_routing.py`만. 게임 코드, EXE/DLL/asset,
  `tools/runtime_env.py`, `tests/test_runtime_env.py`, G1-A draft는 건드리지 않는다.

## Luna/high 구현 요구

1. `run_lap` 뒤 안전 검사가 끝난 직후 `rc=75`를 명시적 terminal 상태로 처리한다.
   `ESCALATE_SOL`은 삭제하지 않고, middle review 대기 이유를 기록한 뒤 exit 75로 종료한다.
2. 일반 worker nonzero의 기존 fail-streak/retry 정책, STOP, dry run, FULL_TEST 의미는 바꾸지 않는다.
3. 기존 회귀를 `N=2`로 강화하거나 동등한 별도 검사를 추가해 work 호출이 정확히 1회이고,
   middle provider는 자동 호출되지 않으며, 표식이 남고, 최종 반환이 75임을 확인한다.
4. 아래 검사가 하나라도 실패하면 재시도/게임 실행 없이 변경과 출력을 보존하고 다시 승격한다.

```sh
.venv/bin/python -m pytest -q \
  tests/test_model_routing.py::test_worker_escalation_stops_for_explicit_middle_review
.venv/bin/python -m pytest -q tests/test_model_routing.py tests/test_patch_loop.py
make check
```

## 현재 증거

- 수정 전 SHA256: `loop/loop.sh`
  `d25baa1da48597bb521fa0977e65558776b708daa1a6dda9fadd76e9e897e8e9`,
  `tests/test_model_routing.py`
  `0e9f2736d8b64394dcd99f62d60c2643f7b091fbbf07267b9d9246c696fe7c9d`.
- lap6 targeted: 1 FAIL, 반환 1. 내부 stdout은 `연속 실패 1/5` 뒤 `max-laps(1)`을 보였고
  subprocess 반환은 0이었다.
- lap6 `make check`: 82 collected, 81 PASS/1 FAIL, make exit 2. 실패는 같은 테스트 하나뿐이다.
- 실제 게임/유료 agent/서비스/커밋/푸시는 실행하지 않았다.
