# 2026-09-11 | lap 52 | 목표 G1-A command branch contract

- 실제 provider/model/effort / 지정 역할: 사용자 지정 Codex `gpt-5.6-luna` / high / hands-on work.
  현재 세션 표면은 실제 model ID를 별도 노출하지 않아 이를 실행 증거로 주장하지 않는다.
- 가설 / 사용자 관찰: lap51의 helper가 group2..5를 무조건 요구해 원본의 `0x0049B6D0`
  조건부 분기를 잃고 있었다. selected type과 두 predicate를 pool 전후에 보존하면 reset 창,
  eligible branch, 명시적 ineligible gate를 구분할 수 있다.
- 예상 PASS / FAIL 조건: 원본 SHA를 먼저 검사하고 selected slot/type, BYTE
  `[0x009B524C+type*0x394]&0x08`, DWORD `selected_unit+0x94`를 pool 전후 읽는다.
  값이 안정적이고 둘 다 참인 synthetic fixture만 group2..5 strict hit를 PASS한다. stable false는
  changed diagnostic으로 재시도 가능하고 stable false predicate는 `49B6D0 ineligible`로 즉시 FAIL한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA `4d342899a70da505886a9c563baa063a991128ece794c908d1a56a0e024861a6`;
  `tests/test_runtime_env.py` SHA `3d52693a1c7891a2854dd48912edc622a6750896b45f61a647645493ec27df4b`;
  `tests/test_runtime_guards.py` unchanged SHA `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`;
  `docs/STATUS.md`, this lap record, and current handoff are uncommitted. Commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본/private EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` verified by `make doctor`;
  후보 EXE N/A. Python synthetic read-memory fixtures only: eligible bit/state, false type bit,
  nonzero selected state, before/after predicate change, empty pool and existing strict-hit cases.
  활성 플레이어/지도/군대 N/A; Wine/Xvfb/game/runtime manifest/PNG 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q
  tests/test_runtime_env.py tests/test_runtime_guards.py` → **43 passed**; `make check` →
  **113 passed**, Ruff/compileall/mypy/context PASS; `bash checks/safety.sh check` → `SAFETY_PASS`;
  `make doctor` top-level `ok=true`, original verified, runtime manifest absent (새 실행 금지).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): helper now records call `0x0049B6D0`, raw values,
  addresses, selected slot/type, before/after stability and eligibility. stable ineligible does not
  poll beyond one pool read; changed predicate is rejected with bounded diagnostic. Contract/fixture
  **PASS**. Live predicate values, group2..5 runtime creation, actual 1600x1200 output/input,
  production/drag/minimap and G1 product result **UNKNOWN/SKIP**. No binary patch attempted.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: existing SHA fail-closed, pool bounds,
  empty/reset polling, duplicate group and strict target-hit tests remain passing. New Sol/high must
  independently verify map raw bytes, helper semantics, fingerprints and gates. User milestone approval
  absent; G1~G4 remain incomplete.
- 다음 한 가지: fresh Codex `gpt-5.6-sol`/high middle independently confirm this source-only
  contract and decide whether a separately authorized live probe can proceed. Do not run game/Wine/Xvfb,
  alter coordinates/timeout, accept group10 as group2..5, or patch binary before that confirmation.
