# 2026-09-20 KST — strategy Astra/Fable 명시적 전환

## 사용자 지시

큰 방향 모델을 Codex Astra와 Claude Code Fable 사이에서 전환할 수 있게 한다.

## 구현

- 단일 선택값: `LOOP_STRATEGY_PROVIDER=codex|claude`.
- `codex`는 `gpt-6-astra`, `claude`는 이동 별칭 대신 전체 ID `claude-fable-5`를 사용한다.
- 기존 내부 stage 이름 `astra`와 `loopctl strategy` 명령은 로그/호환성을 위해 유지한다.
- strategy effort는 기존 계약대로 medium 기본, 명시적 high만 허용한다.
- 실패 시 상대 provider로 자동 폴백하지 않고 잘못된 provider는 세션 실행 전에 거부한다.
- 실제 로컬 선택은 `loop/env.local.sh` 한 줄이다. 최초 배관 검증은 기존 기본 `codex`로 했고,
  이후 사용자 지시에 따라 18:45 KST에 현재 값을 `claude`(Fable)로 전환했다.

## CLI 근거와 검증 경계

- 로컬 Claude Code `2.1.278`의 `claude --help`는 `--model`에 `fable` 별칭과 전체 이름
  예시 `claude-fable-5`, `--effort`의 `medium`/`high`를 명시한다.
- 이는 argv 지원 근거이며 계정의 Fable 접근권한/쿼터를 입증하지 않는다. 유료 모델을 확인만을
  위해 호출하지 않았다. 실제 strategy 실행 실패도 Astra 자동 대체로 숨기지 않는다.
- 가짜 CLI enabled-dispatch 시험을 포함한 `tests/test_model_routing.py`와 기존 loop 제어 회귀를
  함께 실행해 Astra 기본, Fable 전환, 양쪽 high, invalid provider 차단, no-resume을 검증한다.

## 실행 결과

- 라우팅/loop 표적 회귀: `31 passed in 56.81s`.
- 전체 pytest: `779 passed in 451.27s`.
- 첫 전체 게이트의 pytest/ruff는 통과했고 mypy가 앞선 G2 변경의 혼합 profile tuple 추론 3건을
  검출했다. `runtime_driver.py`에 동작 변경 없는 `ExecutableProfile` 타입 별칭과 명시적 cast를
  추가한 뒤 관련 회귀 `55 passed in 105.39s`, Ruff/compileall/mypy/context 모두 PASS했다.
- 최종 `loop/loopctl.sh models`는
  `strategy -> claude/claude-fable-5 effort=medium`을 출력했다.
- 최종 `bash -n`, `CONTEXT_PASS`, `SAFETY_PASS`. 실제 유료 strategy 세션은 호출하지 않았다.
