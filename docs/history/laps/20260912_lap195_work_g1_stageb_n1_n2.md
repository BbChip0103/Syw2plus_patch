# 2026-09-12 | lap 195 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 지정 work; Codex `gpt-5.6-luna`/high 설정. hands-on 하네스 구현.
- 가설 / 사용자 관찰: production provenance 예외가 후속 입력을 계속하게 된 뒤 top-level evidence에는
  진단이 비어 있어 lap190과 같은 보고 착시가 남고, 후보 finally가 같은 evidence를 두 번 쓴다.
- 예상 PASS / FAIL 조건: 실제 production 입력 레코드의 진단이 top-level evidence에도 보존되고,
  production BLOCKED·required_inputs FAIL·overall non-PASS가 유지되며, 후보 final evidence write가
  하나이고 게임 실행은 0회.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA256 `e511ef39748098c8a21ae95255130c92c9355a72e39221f1b1adfe8c80736162`,
  `tests/test_runtime_env.py` SHA256 `7ff0bcd8add7ee02ae690e5daa9e1c27a81f9947b5498c57b77d646fdb15fbcd`.
  `docs/STATUS.md`, `loop/ESCALATE_SOL`, 본 기록도 변경. `LOOP_ALLOW_COMMITS=0`, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 무변경; 후보/게임 run 없음;
  fixture는 stable-ineligible command-cell reader와 production BLOCKED 입력 레코드, 활성 플레이어/
  지도/군대는 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: targeted
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'g1_flush_input_stage or g1_shared_input_sequence or g1_input_verdict'`
  → **6 passed**; `make check` → **211 passed**, Ruff/compileall/mypy/`CONTEXT_PASS`; `bash checks/safety.sh check`
  → **SAFETY_PASS**; `rg -n '_write_json\(trace_dir / "evidence.json", evidence\)' tools/runtime_env.py | wc -l`
  → `1`. 새 PNG/로그/game runtime 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): N1 PASS — provenance error와 command-cell diagnostics/
  branch/alternate/primary snapshot을 flush 시 top-level에 승격. N2 PASS — 후보 final evidence write
  중복 제거. production 클릭, verdict 식, R5, Stage B 재실행은 변경하지 않음. 제품 G1은 미완료.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 입력 레코드와 top-level 모두 보존되며 기존
  fatal `evidence["error"]`는 setdefault로 덮지 않는다. 새 middle의 독립 검수가 필요하다. 실제
  원본/후보 비교, WM_CLOSE 종료 결함, random seed, minimap 절대 목적지, G2~G4 증거는 미검증.
  R5와 Stage B 재실행은 새 사용자 승인 없이는 금지.
- 다음 한 가지: 새 middle이 N1/N2와 R1~R4를 독립 검수하고, 사용자 승인 전에는 R5/Stage B를 실행하지 않는다.
