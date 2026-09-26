# 2026-09-11 | lap 13 | model-routing 게이트 실패 원인 판정 (middle/컨펌)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, 중간 tier(진단·계획·확인).
  `AGENTS.md` 모델 역할의 "중간 계획/컨펌" 자리다. 게임/하네스 hands-on 구현은 하지 않았다.

- 가설 / 사용자 관찰: lap12 targeted 게이트의 1 FAIL은 (A) 호출 환경이
  `LOOP_MIDDLE_PROVIDER=claude`를 상속시킨 것만이 원인인지, (B) 저장소 테스트 격리 계약 결함인지
  `loop/ESCALATE_SOL`이 물었다. 가설: 두 진술은 같은 하나의 결함을 다르게 부른 것이고,
  결함의 소재는 `loop/loop.sh`가 아니라 테스트 하네스다.

- 예상 PASS / FAIL 조건: 결함이 하네스에 있다면 (1) 상속되는 변수 집합이 `export` 표로 결정되고,
  (2) 실패한 파라미터가 정확히 그 집합으로만 설명되며, (3) 설명되지 않는 잔여 실패가 0이어야 한다.
  하나라도 어긋나면 구현 결함 가능성으로 재분류한다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 코드 변경 없음. 이번 바퀴는 문서만 갱신했다
  (`docs/STATUS.md`, `docs/work/active/LOOP_ESCALATION_RETURN_CODE_REPAIR.md`, 이 기록).
  커밋 없음/unborn HEAD, `LOOP_ALLOW_COMMITS=0`.

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 원본/후보 EXE 미실행.
  재해시로 lap12 기록과 **일치 확인**: `tests/test_model_routing.py`=
  `abbcd69cea46336751592b9b9cc8508802b2ec4faf991aebc81d6c649b43d137`,
  `loop/loop.sh`=`c272af40b02b8fede480d52baa22cf790fcf8d21cf3a1cb8e630b1c60bb4d974`.
  진단 대상 참조 파일: `loop/env.sh`=`9529f8267dc3a90f5749ed96ef44df76efd5c519668737571ba9c35efad5d0e4`,
  `loop/env.local.sh`=`5e9f13adc1497fc895d222376175f5feeec8df6fe9e96075485246417829c089`.
  가드 fixture `Syw2plus/syw2plus_original.exe`는 존재한다(1,032,192 bytes). 활성 플레이어/지도/군대 없음.

- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `grep`, `ls`만 실행했다. 캡처 없음.
  `.venv/bin/python -m pytest ...`와 `make check`, `checks/safety.sh check`는 이 비대화형 세션의
  명령 승인 정책이 거부해 **실행하지 못했다(SKIP)**. lap9·lap10의 83 PASS를 이번 증거로 승격하지 않는다.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **원인 CONFIRMED — 테스트 격리 결함(정적)**.
  `loop/loop.sh:16-18`과 `loop/loopctl.sh:23-24`는 `env.sh` 다음에 `env.local.sh`를 source한다.
  `env.sh`의 `export` 표는 정확히 다음만 자식 프로세스로 내보낸다(`loop/env.sh:33,65-69,77,95,149,154`):
  `LOOP_JUDGE`, `LOOP_CODEX_JUDGE_MODEL`, `LOOP_CLAUDE_JUDGE_MODEL`,
  `LOOP_CODEX_ESCALATION_MODEL`, `LOOP_CLAUDE_ESCALATION_MODEL`, `LOOP_ESCALATION_FILE`,
  `LOOP_ROLE`, `LOOP_MIDDLE_PROVIDER`, `LOOP_CODEX_WORK_MODEL`, `LOOP_CODEX_MIDDLE_MODEL`,
  `LOOP_CODEX_ASTRA_MODEL`, `LOOP_CLAUDE_WORK_MODEL`, `LOOP_CLAUDE_MIDDLE_MODEL`,
  `LOOP_EFFORT`, `PATH`, `LOOP_ENABLE_AGENT`, `LOOP_ALLOW_COMMITS`.
  `env.local.sh:4`가 이미 export된 `LOOP_MIDDLE_PROVIDER`에 `claude`를 재대입하므로 export 속성이 유지된 채
  pytest까지 상속된다. `tests/test_model_routing.py:40`의 `dry()`는 `dict(os.environ, ...)`로 이를 다시 들여오고
  `LOOP_MIDDLE_PROVIDER`를 덮지 않는다. `loop/env.sh:24`의 `: "${LOOP_MIDDLE_PROVIDER:=codex}"`는
  상속값이 있으면 기본값을 적용하지 않는다. 그래서
  `test_codex_roles_have_fixed_model_and_high_effort[middle]`만 Claude 명령을 관측한다.
  **신호 일치(잔여 0)**: `LOOP_WORKER`는 `env.sh`의 어떤 export 줄에도 없어 상속되지 않으므로
  `work`/`astra` 파라미터와 `test_conflicting_codex_extra_is_rejected_before_session` 6개는 영향이 없다.
  나머지 claude 경로 테스트(`:87`, `:180`)는 원래 claude를 기대하고, `:98`, `:146`, `:213`, `:253`은
  `LOOP_MIDDLE_PROVIDER`를 명시 고정한다. 상속 집합으로 실패 1개가 정확히 설명되고 설명되지 않는 실패는 없다.
  → (A)와 (B)는 대립 가설이 아니다. 상속은 방아쇠이고, 결함은 **기본 라우팅 계약을 주장하는 테스트가
  주변 환경을 읽는다**는 것이다. fixture가 `env.local.sh`를 복사 제외(`tests/test_model_routing.py:24`)해
  격리 의도를 명시해 놓고 `os.environ`으로 같은 override를 되들여오는 자기모순이 증거다.
  **구현 결함 아님**: `loop/loop.sh`/`loop/env.sh`의 기본값은 `codex`로 계약대로다.
  **lap12 신규 회귀 자체는 PASS로 연역된다(측정 아님)**: 수집 항목은 3+1+1+1+6+1+1+1+1+1=17개이고
  가드 fixture가 있어 skip이 0인데 lap12는 `1 failed, 16 passed`(skip 표기 없음)를 보고했다.
  따라서 실패 1개는 기존 파라미터 테스트이고 신규
  `test_raw_worker_exit75_without_marker_hits_fail_streak_stop`은 통과 집합에 속한다.
  이는 산술 연역이므로 판정은 **DEDUCED-PASS / 독립 실측 미확인**으로 남긴다.
  **결함 범위는 이 파일 하나가 아니다**: `tests/test_patch_loop.py:32-40,148-156`도 같은
  `dict(os.environ, ...)` 패턴이며 `LOOP_MIDDLE_PROVIDER`를 고정하지 않는다. `tests/conftest.py`는 없다.
  현재 값이 우연히 기본값과 같은 상속 변수(`LOOP_EFFORT`, `LOOP_CODEX_*_MODEL`, `LOOP_ALLOW_COMMITS`)는
  지금은 실패를 만들지 않지만 **거짓 PASS** 위험이라 거짓 FAIL보다 나쁘다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기대값을 낮추지 않았고 후보 파일을 건드리지 않았다.
  이번 판정은 정적 근거와 실패 신호 일치에 기반하며 이번 세션의 실측은 없다(SKIP).
  work tier가 아래 handoff를 수행해 실측을 만들기 전까지 게이트는 GREEN이 아니다.
  게임/G1-A는 실행하지 않았고 G1~G4 판정 변화 없음, 사용자 마일스톤 승인 없음.
  `loop/ESCALATE_SOL`이 요청한 진단은 이번 바퀴로 소진되어 원문을 아래에 보존하고 표식을 제거했다(routing→work).

- 다음 한 가지: work tier(Luna/high 또는 Claude `claude-sonnet-5`/high)가 `tests/conftest.py`를 새로 추가해
  상속된 `LOOP_*`를 제거하는 autouse fixture를 만들고, 승인된 clean 환경에서 targeted·인접·전체 Fast를 실측한다.
  `loop/loop.sh`, `loop/env.sh`, `loop/env.local.sh`와 기존 기대값은 건드리지 않는다.

## 보존: 제거 전 `loop/ESCALATE_SOL` 원문 (lap12 작성)

```
lap=12
reason=targeted_model_routing_gate_failed_under_inherited_middle_provider
role_requested=Fresh Codex gpt-5.6-sol/high or Claude Code claude-opus-5/high middle independent diagnosis; do not implement until the gate provenance is resolved
required=Verify whether the existing test failure is caused only by the caller environment inheriting LOOP_MIDDLE_PROVIDER=claude and LOOP_JUDGE=claude, or exposes a repository/test isolation defect. Re-run only under an explicitly documented clean routing environment after the middle tier decides the safe validation contract. Preserve the new tests/test_model_routing.py regression and do not change its expectations merely to make the gate green. Do not run the game or resume G1-A.
evidence=targeted command `.venv/bin/python -m pytest -q tests/test_model_routing.py`; result 1 failed, 16 passed in 5.98s. Failing test `test_codex_roles_have_fixed_model_and_high_effort[middle--m gpt-5.6-sol -c model_reasoning_effort=high]` observed Claude middle command. Current inherited environment has LOOP_MIDDLE_PROVIDER=claude, LOOP_JUDGE=claude, LOOP_ENABLE_AGENT=1; test helper inherits os.environ and does not override LOOP_MIDDLE_PROVIDER for the default Codex parameterized case.
preserve=Keep the uncommitted tests/test_model_routing.py change (SHA256 abbcd69cea46336751592b9b9cc8508802b2ec4faf991aebc81d6c649b43d137), unchanged loop/loop.sh (SHA256 c272af40b02b8fede480d52baa22cf790fcf8d21cf3a1cb8e630b1c60bb4d974), this marker, and the lap12 history/STATUS evidence. No adjacent or full Fast gate was run after the required targeted failure.
```

제거 전 원문 파일 SHA256: `93a24f65feee78685e3ddef71d5ed0578e61ba511c5141fee593dfc0ec8c3d90`.
위 코드블록이 표식 전문이며, lap12 기록(`20260911_lap12_luna_model_routing_gate_escalation.md`)에
같은 사실이 독립적으로 남아 있다.
