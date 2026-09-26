# 2026-09-15 | product-first G1 original S1 load

- 사용자 지시: 짧게 가능성을 판정하고 가능하면 즉시 구현, 불가능/차단이면 즉시 보고한다. 과거 provenance 반복은 제품 차단 조건에서 제외했다.
- 원인/변경: `(400,131)`은 저장 슬롯 행이라 선택값 1을 바꾸지 못했다. 실제 원본 화면의 불러오기 버튼을 fresh runtime으로 확인해 logical `(316,372)`로 `tools/runtime_env.py`와 test fixture를 수정했다.
- 검증: `tests/test_s1_load_evidence.py` 52 passed, 전체 `make check` 430 passed, Ruff/compileall/mypy/CONTEXT PASS, safety 2종 PASS.
- 실제 실행: `local/runtime/20260915_124523_1526738_0`, 원본 EXE SHA `b56986e…a8ac`, save000 SHA `1c703551…19da`, PS35→PS3 0.25초, 로드 후 8개 PlayerStruct가 fixture와 8/8 일치. cleanup ok, residue 0, 원본/메모리 write 0.
- 증거: `output/s1_original_load_evidence.json` SHA `626be550e403714bad89f97e4e090b875a347a2d7dd67eb49a24c88006f925fc`, 판정 `PASS/LOAD_RESTORED_PLAYER_STRUCTS`. 제품 G1 전체 PASS는 아니며 다음은 동일 입력의 1600×1200 후보 실행·화면/입력 비교다.
