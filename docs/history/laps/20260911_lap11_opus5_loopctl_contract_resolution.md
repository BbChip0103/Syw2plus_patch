# 2026-09-11 | lap 11 | loop escalation raw exit75 합격 계약 provenance 해소

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high (세션 헤더가 노출한 실제 모델 ID) / 사용자 지정 middle 역할(진단·계획·확인). hands-on 구현·테스트 수정은 하지 않았다.
- 가설 / 사용자 관찰: lap10이 승격한 두 acceptance source 중 하나만 권한 있는 원문이며, 나머지는 work tier가 자기 결과를 스스로 완화한 것이므로 문서 권한 규칙만으로 판정할 수 있다. 구현(`loop/loop.sh`)에는 별도 결함이 없고 빠진 것은 회귀 하나라는 것이 가설이다.
- 예상 PASS / FAIL 조건: (a) APPROVALS/INBOX/`docs/work/active/`/git 이력 어디에도 카드 조건을 대체하는 더 최신 명시 승인이 없으면 활성 카드가 유효하다. (b) `loop/loop.sh`의 정적 제어흐름이 카드가 요구한 `LOOP_MAX_FAIL_STREAK=2`·STOP·최종 nonzero를 실제로 만족시킬 수 있으면 이 충돌은 구현 결함이 아니라 테스트 공백이다. 둘 중 하나라도 어긋나면 다시 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현·게임·테스트 변경 없음. 판정 기록으로 `docs/history/laps/20260911_lap11_opus5_loopctl_contract_resolution.md`(신규), `docs/work/active/LOOP_ESCALATION_RETURN_CODE_REPAIR.md`, `docs/STATUS.md`만 갱신하고 `loop/ESCALATE_SOL`은 아래에 원문을 보존한 뒤 제거했다. 검수 시작 시점 SHA256: `loop/loop.sh` `c272af40b02b8fede480d52baa22cf790fcf8d21cf3a1cb8e630b1c60bb4d974`, `tests/test_model_routing.py` `01ea5d3fa43d348d87bfcf243787aeb663678e86327db769eee328ec36388d1e`, `loop/ESCALATE_SOL` `1ccad0b94de5fb2d62af95c12fec1a3311405ea1c419215b54344f0e54bbea58`, 수리 카드 `43c8964ff9af44aa4826d9b229d51d3d3f196da110d2f6a48f22220602ea7a1e`, `docs/STATUS.md` `1e0431e03e2c57368fb8da588a79832cb94a91719de439f309b9d91c7b08b491`. 커밋 없음/unborn HEAD(`git log` = "does not have any commits yet"). 갱신 후 SHA256: `docs/STATUS.md` `53fb8d41fcde0c23c82c169d0184341564888a6f1f4458c47c531a21c7ad014e`, 수리 카드 `c2a6eda7032205602bc36b52dfa2ec4729bb37ba19798d8360a81b1b1c14d9e2`; `loop/loop.sh`와 `tests/test_model_routing.py`는 재해시 결과가 검수 시작 시점과 동일해 무변경이 확인된다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본/후보 EXE는 열지도 실행하지도 않았다. lap9 후보 두 파일의 SHA는 lap9·lap10 기록과 이번 재해시가 모두 일치한다. 실제 게임·플레이어·지도·군대·fixture 없음(전면 SKIP).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum loop/loop.sh tests/test_model_routing.py loop/ESCALATE_SOL docs/work/active/LOOP_ESCALATION_RETURN_CODE_REPAIR.md docs/STATUS.md`; `grep -n` 로 `loop/loop.sh` 780-830·595-624, `loop/env.sh:106,113`, `tests/test_model_routing.py:213-288` 정독; `git log`/`git status --short --branch`; `ls -R docs/work`. **`make check`, `checks/safety.sh check`, targeted pytest는 이번 세션에서 실행하지 못했다** — 이 헤드리스 세션의 명령 승인 정책이 `make`/`pytest`/`bash checks/*.sh` 실행과 작업 디렉토리 밖 쓰기를 거부했다(격리 임시 프로젝트 probe도 같은 이유로 불가). 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **계약 provenance: RESOLVED — 활성 수리 카드(lap8 보완 조건)가 유효하다.** 근거: ① `docs/feedback/APPROVALS.md`의 "확정"은 여전히 "없음"이고 ② `docs/feedback/INBOX.md`에 카드 이후 새 지시가 없으며 ③ `docs/work/active/`에 개정 카드가 없고 ④ 커밋이 하나도 없어 다른 provenance 경로가 존재하지 않는다. lap9 기록의 `max-laps(2)`·exit0 조건은 work tier가 같은 바퀴에 스스로 적은 기대값이며, `AGENTS.md`의 "실무 모델이 자기 결과를 최종 승인하지 않는다"에 따라 컨펌 tier가 적은 합격 조건을 대체할 권한이 없다. 두 원문은 모두 보존한다.
  - **구현 결함 여부: 없음(정적 PASS).** `loop/loop.sh:796`의 terminal 분기는 `rc=75 && -f ESCALATE_SOL`을 함께 요구하므로 marker 없는 raw exit75는 그대로 통과하고, `:802-809`의 generic fail-streak에서 세어진다. fail-streak 분기는 `:819`의 `max-laps` exit0보다 앞이며 `loop/env.sh:113`의 `: "${LOOP_MAX_FAIL_STREAK:=5}"`는 환경 override를 허용한다. 따라서 `LOOP_MAX_FAIL_STREAK=2` + `run 2`면 lap1에서 `연속 실패 1/2`, lap2에서 `연속 실패 2/2` 뒤 `loop/STOP` 생성과 `exit 1`이 나야 한다. **이는 정적 도출 예측이며 이번 세션에서 실행 확인하지 않았다(UNKNOWN→work tier가 측정).**
  - **결론: 남은 것은 구현 수리가 아니라 `tests/test_model_routing.py` 회귀 하나의 공백이다.** lap9의 `test_raw_worker_exit75_without_marker_uses_generic_failure_retry`는 기본 threshold 5에서 재시도 계수만 확인해 카드의 STOP·nonzero 조건을 검증하지 않는다.
  - Fast/targeted/safety 게이트: **SKIP(미실행, 환경 권한)**. lap9·lap10이 기록한 83 PASS를 이번 세션의 증거로 승격하지 않는다. G1~G4 판정 변화 없음, 실제 게임 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이 바퀴는 문서 판정만 바꿨으므로 코드 회귀 위험은 없다. 남은 위험은 ① 위 정적 예측이 실측과 어긋날 가능성(그 경우 구현 결함으로 재분류해야 한다)과 ② 이번 세션이 Fast를 재실행하지 못해 후보 승인의 기계 근거가 lap9·lap10 기록에만 있다는 점이다. 그래서 이번 판정은 **계약 판정에 한정된 CONFIRM**이며 lap9 후보의 최종 승인이 아니다. 사용자 마일스톤 승인 없음, G1-A 차단 유지.
- 다음 한 가지: 아래 work tier handoff(테스트 1개 추가) → targeted·인접·`make check` → 새 middle 세션의 독립 확인. 그 전에는 G1-A를 재개하지 않는다.

## work tier handoff (Luna/high 또는 Claude `claude-sonnet-5`/high)

- 허용 변경 파일: **`tests/test_model_routing.py` 하나뿐.** `loop/loop.sh`는 이번 판정에서 정적 PASS이므로 건드리지 않는다. 게임 코드/EXE/asset/`tools/runtime_env.py`/`tests/test_runtime_env.py`/G1-A draft도 그대로 둔다.
- 추가할 회귀(예: `test_raw_worker_exit75_without_marker_hits_fail_streak_stop`)는 lap9 테스트와 같은 fixture·fake worker(`exit 75`, marker 생성 없음)를 쓰되 환경만 `LOOP_MAX_FAIL_STREAK="2"`, `LOOP_MAX_LAPS="2"`로 두고 `loopctl.sh run 2`를 실행한다. 확인할 것:
  1. 최종 반환이 **nonzero(예상 1)** 이고 75가 아니다.
  2. worker 호출이 정확히 2회이고 middle provider 호출이 0회다.
  3. `loop/ESCALATE_SOL`이 생성되지 않고 stdout에 `middle-review-pending`이 없다.
  4. stdout에 `연속 실패 1/2`, `연속 실패 2/2`, `이유=fail-streak`가 있고 `max-laps(2)`로 끝나지 않는다.
  5. `loop/STOP`이 생성된다.
- 기존 두 테스트(`test_worker_escalation_stops_for_explicit_middle_review`, `test_raw_worker_exit75_without_marker_uses_generic_failure_retry`)는 **삭제하지 말고 유지**한다. 새 회귀는 대체가 아니라 추가다.
- 실제 반환/로그가 위 1~5와 다르면 테스트를 기대값에 맞춰 고치지 말고, 출력을 보존한 채 구현 결함으로 재분류해 다시 승격한다.
- 검사: `.venv/bin/python -m pytest -q tests/test_model_routing.py` (targeted 3), `.venv/bin/python -m pytest -q tests/test_model_routing.py tests/test_patch_loop.py` (인접), `make check`. 하나라도 실패하면 재시도·게임 실행 없이 보존하고 승격한다.

## 제거 전 `loop/ESCALATE_SOL` 원문 보존 (SHA256 `1ccad0b94de5fb2d62af95c12fec1a3311405ea1c419215b54344f0e54bbea58`)

```
lap=10
reason=middle_confirmation_blocked_by_conflicting_raw_exit75_acceptance_contracts
role_requested=Fresh Codex gpt-5.6-sol/high or Claude Code claude-opus-5/high middle contract resolution; any hands-on test change must be handed to Luna/Sonnet5 work tier
required=Resolve whether the active repair card's LOOP_MAX_FAIL_STREAK=2, fail-streak STOP, final-nonzero regression remains authoritative or whether a newer explicit approval replaced it with lap9's default-5, max-laps(2), exit0 regression. Preserve both sources until provenance is established. If the active card stands, hand off a tests/test_model_routing.py-only regression correction to work tier, then require a fresh independent middle confirmation. Do not run the game or resume G1-A.
evidence=docs/work/active/LOOP_ESCALATION_RETURN_CODE_REPAIR.md:12-13; tests/test_model_routing.py:254-288; docs/history/laps/20260911_lap9_luna_loopctl_escalation_repair.md; docs/history/laps/20260911_lap10_sol_loopctl_escalation_review.md
observed=lap9 candidate hashes match; bash syntax and targeted 2 PASS, adjacent 25 PASS, make check 83 PASS with Ruff/compileall/mypy/context all PASS. Static code correctly gates terminal rc75 on ESCALATE_SOL, but the new raw-exit75 test does not exercise the active card's explicit STOP/nonzero condition.
preserve=Keep ESCALATE_SOL and the G1-A block. Do not alter game assets/code, loop/loop.sh, tools/runtime_env.py, tests/test_runtime_env.py, or the G1-A draft while the contract conflict is unresolved.
```

`required=`의 provenance 해소와 handoff 작성이 이번 바퀴에 끝났으므로 marker를 제거한다.
marker는 "middle review pending" 라우팅 신호라서 남겨두면 다음 바퀴가 다시 middle로 돌아 work 수리가 진행되지 않는다.
`preserve=`의 G1-A 차단과 파일 보호 범위는 STATUS의 blocker와 위 handoff에 그대로 이어진다.
