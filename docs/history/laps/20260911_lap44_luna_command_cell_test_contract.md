# 2026-09-11 | lap 44 | 목표 G1-A command-cell 테스트 계약

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-luna` / high / hands-on work.
- 가설 / 사용자 관찰: lap43 Sol 검수에서 helper의 source/map/wiring은 확인됐지만 정상 네 cell의
  x 산술과 중복 group cell 거부를 직접 고정하는 회귀가 없어 test contract가 REVISE였다.
- 예상 PASS / FAIL 조건: 정상 fixture가 `x=baseX+N*Δ`를 `[600,740,880,1020]`으로 보존하고,
  유효 callback/group을 가진 duplicate group cell이 fail-closed로 거부되면 targeted/Fast/safety를
  PASS로 기록한다. 실패 시 현재 변경과 증거를 보존하고 Sol 검수로 넘기지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tests/test_runtime_env.py` fixture에 `base_x=600`, `delta_x=140`, duplicate group case 및
  x assertion 추가; SHA256 `0d02e81cc50e230813c63e0b2275aa1988a2237b6499a91501130dff41e0df84`.
  기록 파일은 `docs/STATUS.md`, 본 history, `loop/ESCALATE_SOL`; 커밋/푸시 없음.
  `tools/runtime_env.py` SHA는 `9e82a19e2888c04701dca40baf22fa5391c13775e7e60b531671829342d84845`,
  memory map SHA는 `b2897bdecbb6e86de76f649073c230334b471ac28a911559347e1f3e164b59e5`로 유지했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 binary N/A.
  게임/runtime 환경 N/A, 활성 플레이어·지도·군대 N/A. 가상 read-memory fixture만 사용했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 사전 독립 대조로 `sha256sum`, Python type58 산술,
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py` → 35 passed.
  변경 후 같은 targeted 명령 → 36 passed; `make check` → 106 passed, Ruff/compileall/mypy/context
  PASS; `bash checks/safety.sh check` → `SAFETY_PASS`. 게임/PNG/runtime manifest 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 정상 x `[600,740,880,1020]` 및 target `(670,490)`의
  strict group2 hit assertion PASS. slot5에 유효 group2 cell을 추가한 중복 fixture는
  `expected one command cell`로 거부 PASS. source/map/helper 변경 없음; targeted/Fast/safety PASS.
  테스트 계약 수리는 PASS, runtime cell·worker 의미와 G1-A 제품 결과 UNKNOWN, 게임/patch SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 SHA mismatch, invalid slot/type,
  multiple-hit, boundary 및 callback/type58 회귀는 유지했다. 새 Sol/high가 tests-only 변경과
  현재 SHA/gates를 독립 확인해야 하며 제품·마일스톤 사용자 승인은 없다.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high middle이 이 테스트 수리와 fresh gate를 독립 검수하고,
  PASS 뒤에만 별도 runtime-read 허용 여부를 판정한다. 그 전 helper/좌표/게임/patch는 변경·실행하지 않는다.
