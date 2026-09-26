# 2026-09-11 | lap 54 | 목표 G1-A selection identity coherence 수리

- 실제 provider/model/effort / 지정 역할: 사용자 지정 Codex `gpt-5.6-luna` / high / hands-on work.
  현재 세션 표면은 실제 model ID/effort를 별도 노출하지 않아 이를 실행 증거로 주장하지 않는다.
- 가설 / 사용자 관찰: lap53에서 selected slot/type을 한 번만 읽어 안정 predicate만으로 coherent
  snapshot을 승인한 것이 원인이다. pool read 전후에 selection count/slot, active, unit type과 두
  `0x0049B6D0` predicate를 독립 snapshot으로 재읽고 identity/value를 비교하면 선택 변경을 놓치지 않는다.
- 예상 PASS / FAIL 조건: stable eligible fixture는 before/after identity와 predicate가 같고 PASS한다.
  count/slot/active/type 또는 predicate가 바뀌면 pool raw summary와 before/after evidence를 가진
  명시적 FAIL이 되어야 하며, stable ineligible predicate는 polling 없이 기존 required-gate FAIL이어야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/runtime_env.py` SHA
  `c43b20ccbd7bad3da4fa2d704bb36e73388ed9b2cb50709d8cc96f0aa321b2d4`,
  `tests/test_runtime_env.py` SHA `6a38c6b8b304edc31e23c71c65b8f8c3dc8b5042a97f93397ce671cea0d4bb4f`,
  `tests/test_runtime_guards.py` unchanged SHA
  `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`. Git unborn,
  `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본/private EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 EXE N/A. Python
  synthetic read-memory fixture만 사용했다. before `(count=1, slot=7, active=1, type=58)`에서
  after `(count=2, slot=8, active=2, type=59)`로 바꾸고 raw pool groups 2..5를 보존했다.
  활성 플레이어/지도/군대 N/A; Wine/Xvfb/game/runtime manifest/PNG 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 이전 결과를 `sha256sum`, `make doctor`, targeted pytest로
  독립 대조한 뒤 targeted `pytest tests/test_runtime_env.py tests/test_runtime_guards.py` → **44 passed**;
  `make check` → **114 passed**, Ruff/compileall/mypy/context PASS; `bash checks/safety.sh check` →
  **SAFETY_PASS**. 캡처 없음. `make doctor`는 original verified/top-level ok=true와 runtime manifest
  absent를 확인했으며 새 runtime 실행은 하지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): helper는 stable path에서 count/slot/active/type과
  predicate를 각각 before/after 읽고, identity tuple 변화 시 `selection identity changed`로
  fail-closed한다. 변경 fixture는 before/after selection/unit 및 raw group `[2,3,4,5]`를 예외에
  보존해 **PASS**. 기존 predicate-change/stable-ineligible/empty-pool/duplicate/cell-hit 회귀도 PASS.
  G1 실제 1600x1200 출력·입력·production/drag/minimap, G2~G4 실제 증거는 **UNKNOWN/SKIP**.
  binary patch/version/restore는 후보가 없어 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 전체 Fast와 safety는 PASS했으나 이는 source/
  synthetic contract 검증이며 live predicate/group2..5 생성이나 제품 G1 승인이 아니다. 새 Sol/high가
  helper semantics, raw map, hashes, call-site와 stable-ineligible 즉시 FAIL을 독립 검수해야 한다.
  사용자 milestone approval 없음.
- 다음 한 가지: fresh Codex `gpt-5.6-sol`/high가 lap54 구현과 fixture/evidence를 독립 검수한다.
  검수 전 새 game/Wine/Xvfb, 좌표·timeout 변경, binary patch는 금지한다.
