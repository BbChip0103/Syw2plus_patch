# 2026-09-12 | lap 190 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex 세션 / hands-on work tier / high 지정. 이번 바퀴는
  승인된 G1 카드2 Stage B의 첫 실제 원본 run만 수행했다.
- 가설 / 사용자 관찰: fresh private 원본 run은 PS3 이후 공용 입력 시퀀스를 수행하고,
  production은 click 없이 `BLOCKED`로 기록한 뒤 `drag_select`와 `minimap`까지 진행해야 한다.
  실제로는 `_read_g1_command_cell_provenance()`가 `49B6D0 ineligible` 예외를 던져 production
  레코드 없이 run이 중단됐다. 이는 예상된 production BLOCKED 관측이 아니라 하네스 계약 불일치다.
- 예상 PASS / FAIL 조건: setup/PS3/`unit_select` PASS 후 production BLOCKED 레코드, 이후
  drag/minimap 증거와 전체 입력 verdict가 남으면 관측 가능; 예외로 후속 단계가 누락되면
  필수 Stage B 검증 FAIL 및 즉시 승격. 실패 후 retry 금지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): source/tests/EXE/DLL/assets/
  baseline/golden 변경 없음. 실행 산출물은 Git 제외 `local/runtime/20260912_010714_2914723_0/`와
  공유 temp에 생성. 하네스 SHA `tools/runtime_env.py=db2113a7f1cf0fbe41f5c4ccb187a71bb9e7adbae371dd8486db46c8dabc4226`,
  `tests/test_runtime_env.py=0ea2788b99220f66d7c3341b4f39a3f6dcfa09b2bd937ba8810e2a6494b1c61a`.
  문서 이력만 uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호·private 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 SHA N/A.
  새 private copy/prefix, private Xvfb 1600x1200x24, `ddraw=b`, diagnostic bridge/control
  bridge/resource grant/memory write 없음. 기본 two-player random game, owner0/1 nation=2,
  active units 각 2, map/seed 비노출, scene fingerprint은 same-run 전용.
- 실행 명령 / 로그 / 캡처 경로 및 해시: fresh helper PE32 build과 fresh bridge PE32 build은 RC0;
  bridge DLL SHA `cd248cf499e0ec743f941e35daa699b3cf9301cbfc0483a0654bcdf08b486fa5`.
  `make check` → 209 passed, Ruff/compileall/mypy/context PASS; `bash checks/safety.sh check`
  → `SAFETY_PASS`; prepare/check → RC0; 정확히 1회
  `.venv/bin/python tools/runtime_env.py g1-baseline --manifest local/runtime/20260912_010714_2914723_0/manifest.json --screen 1600x1200x24 --timeout 90`
  → RC2, `49B6D0 ineligible: original command-cell creation predicates are false`.
  `manifest.json=1368053078b01dc3aef290319aa4d8e2cee476cf7b36bf222228eb4716a4a6f9`,
  `g1_a/evidence.json=b266c2293422e7ef5181814078d6f07519639b7b7a1da857fb3f60cd6a16b4e2`,
  `g1_a/verdict.json=6d1a47f451c1b5c86e647b5d7acfaa9a2399d55089641e0453dac8069603199c`,
  `g1_a/inputs.jsonl=fbbed345b24610e556072fc364aa99f0297b98d259fb08a74c1c96ae13fd6e45`.
  Captures are in `/home/dev_00/sharedfolder/260320_Syw2plus/temp/` and are listed in inputs/evidence.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): root `[1600,1200]`, game/content `[800,600]`,
  PS9→PS7→PS5→PS3, PS3 tick=7, unit selection count `0→1` PASS. production record absent,
  `required_inputs=false`, `drag_select`/`minimap` absent: Stage B baseline **FAIL/BLOCKED**.
  cleanup `ok=true`, owned launchers/Xvfb stopped, prefix processes `[]`. Candidate run and
  원본/후보 comparison **SKIP** because mandatory first run failed; G1 product remains incomplete.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: pre-run machine gates PASS, but actual
  production fail-closed/continue contract failed in runtime. No code fix or retry was attempted.
  User approval remains limited to one fresh original + one fresh candidate comparison and is not
  product approval. Middle/Opus5 must independently diagnose the exception-to-BLOCKED contract
  and define the smallest repair before a new work run; this candidate run is not authorized by
  the failed prerequisite in this lap.
- 다음 한 가지: 새 middle 세션이 this artifact and source path independently verifies the
  production provenance failure, issues a bounded repair/test contract, and keeps Stage B candidate
  execution closed until the repaired baseline contract is independently confirmed.
