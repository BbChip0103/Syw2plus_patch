# 2026-09-11 | lap 65 | 목표 G1-A exact-single-selection gate 회복 및 계약 확인

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier / diagnosis·plan·confirmation. 현재 세션 표면은 실제 provider/model ID/effort를 노출하지 않으므로 `gpt-5.6-sol` 실행으로 주장하지 않는다.
- 가설 / 사용자 관찰: lap64의 exit127은 pytest 의존성 부재가 아니라 console-script를 직접 호출한 invocation 오류이며, Makefile의 정식 module entrypoint로 필수 gate를 새로 통과하고 고정 원본 count dispatch가 lap63과 일치하면 exact-single-selection 계약을 work tier에 승인한다.
- 예상 PASS / FAIL 조건: `.venv/bin/python -m pytest` targeted runtime/guards, `make check`, safety, doctor가 모두 PASS하고 원본/private SHA, count1-only fill, count0/count>1 bypass, 공통 consumer, writer old bytes가 일치해야 PASS다. 하나라도 실패·충돌하면 재시도 없이 UNKNOWN/ESCALATE한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/helper/tests/binary/좌표/timeout/fixture 변경 없음. 판정 문서 `docs/STATUS.md`, `docs/work/active/G1_A_EXECUTION_CARD.md`, `analysis/memory_maps/player_offsets.md`, 본 이력만 갱신하고 소진 marker `loop/ESCALATE_SOL` SHA `7f9fe562b1f4afdf98d1680aa51a196a0bcbd0e052ef47824d6b1ed19c24ad40`을 아래 원문 보존 후 제거한다. 검수 source SHA는 `tools/runtime_env.py=e605e041816856bc88458df8bfad85e2e77cdac40f4ba6cab1e6e7d4e3d32dd5`, `tests/test_runtime_env.py=58ea272f06d78f1edc672d4f569d7a7e3bd6ea0d644f3b68d6a6bd06931e024c`, `tests/test_runtime_guards.py=93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`다. Git unborn/uncommitted, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본과 lap60 private EXE SHA가 모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`다. 후보 EXE, 새 Wine/Xvfb/game run, 활성 인원/지도/군대 측정은 없음. 관련 단위 테스트는 synthetic memory fixture이며 과거 lap60 artifact를 fresh runtime으로 승격하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -c 'import pytest'`, `make doctor`, `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py`, `make check`, `bash checks/safety.sh check`, `sha256sum`, `file`, `objdump -d -Mintel`, `objdump -s`를 실행했다. 새 로그/PNG/runtime은 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): pytest 9.0.2 module import PASS, doctor top `ok=true`/original verified, targeted **46 passed**, 전체 **116 passed**, Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**. 원본 `0x498FBA` count dispatch에서 count0은 `0x498FC3`, count1만 `0x498FDB→0x499201..0x49929E`, count>1은 `0x498FD2→0x499336`, 모두 `0x499583` consumer에 합류함을 재확인했다. writer `0x4A3B5B` old bytes `66 8b 54 24 08 0f bf c0 66 89 94 41 96 0c 00 00`도 일치한다. lap63 계약은 **MIDDLE CONFIRM PASS / WORK READY**다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 PASS는 구현 전 source/test 계약 판정이지 helper 수리, 새 runtime, 제품/ 마일스톤 PASS가 아니다. primary field/action·worker click, G1 실제 2배 출력/입력/생산/drag/minimap, G2~G4, 사용자 승인은 UNKNOWN/미완료다. binary patch가 없어 expected new bytes, unsupported-version rejection, copy-only/non-overlap/byte-exact restore는 N/A/SKIP이고 원본 쓰기·배포·커밋은 없었다. 사용자 runtime 입력의 implementation-unchanged-streak=1에서 이 document-only lap 후 2가 되므로 다음 측정 가능 변경을 아래 helper/tests 구현으로 고정한다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high 또는 Claude Code `claude-sonnet-5`/high work가 승인된 범위로 `tools/runtime_env.py`/관련 tests만 수정해 exact count1 pre-read guard, phase당 단일 96-byte primary snapshot, stable count2 무-read, `1→2` before/after raw evidence, stable-ineligible no-click 예외를 구현·회귀한다. targeted/Fast/safety 후 새 middle 독립 검수 전 game run은 금지한다.

## 소진 전 `loop/ESCALATE_SOL` 원문

제거 전 SHA256: `7f9fe562b1f4afdf98d1680aa51a196a0bcbd0e052ef47824d6b1ed19c24ad40`.

```text
# lap64 승격 요청 — targeted 검증 entrypoint 실패로 계약 승인 중단

## 사유

고정 원본에서 lap63의 `selected_count==1` 전제와 count0/count1/count>1 분기, 공통
`0x499583` consumer는 독립 재확인됐다. 그러나 필수 targeted runtime/guards 검증을 위해 실행한
`.venv/bin/pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py`가
`No such file or directory`로 테스트 수집 전에 exit 127이었다. 사용자 중단 조건에 따라
`python -m pytest` 같은 대체 명령으로 재시도하거나 Fast/계약 승인을 마감하지 않았다.

## 이어서 검증할 것

1. 새 바퀴에서 `.venv/bin/python`은 존재하지만 `.venv/bin/pytest`가 없는 원인과 이 저장소의 정식
   targeted 테스트 invocation을 먼저 확인한다. 환경을 임의 재설치하거나 새 의존성을 추가하지 않는다.
2. 정식 invocation으로 runtime/guards targeted tests를 실행하고, 이어 `make check`와
   `bash checks/safety.sh check`를 모두 새로 통과시킨다. 또 실패하면 변경과 로그를 보존하고 멈춘다.
3. 전부 PASS한 경우에만 lap63의 stable count2 primary 무-read 조기 거부, `1→2` before/after identity와
   두 primary raw snapshot, lap62의 phase당 단일 96-byte read/fail-closed 계약을 최종 승인한다.
   승인 전 helper/tests와 game/binary/좌표/timeout/fixture는 변경하지 않는다.

## 보존된 근거

- original/private EXE SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- source SHA: `tools/runtime_env.py=e605e041816856bc88458df8bfad85e2e77cdac40f4ba6cab1e6e7d4e3d32dd5`,
  `tests/test_runtime_env.py=58ea272f06d78f1edc672d4f569d7a7e3bd6ea0d644f3b68d6a6bd06931e024c`,
  `tests/test_runtime_guards.py=93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`.
- lap60 historical manifest/baseline/verdict/provenance SHA는 lap63/STATUS에 보존됐고 lap64에서도 일치했다.
- lap64 fresh evidence: static count dispatch/reset/writer CONFIRMED, `make doctor` top `ok=true`,
  explicit-manifest doctor-runtime `ok=true`; targeted tests NOT RUN (entrypoint exit127), Fast/safety SKIP.

제품 G1~G4 완료/사용자 승인 및 work handoff 승인은 없으며 새 runtime 실행도 없다.
```
