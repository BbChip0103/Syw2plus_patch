# lap585 work — W49R receipt snapshot 수리

- 날짜/lap: 2026-09-25 / 585
- 목표: W49R fresh 실행 전 파생 runner의 `capture()` 순환 참조 제거
- 가설: `capture()`가 caller receipt를 그대로 보관한 뒤 `g0_h1["capture"]`가 같은 receipt를 다시 참조해 `json.dumps(run_summary)`가 실패했다.
- 변경파일: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260925_lap584_w49r_screen_camera/w49r_run.py`
- 원본/후보 SHA: 원본 게임 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변; runner old `aa92285c30f420192f165adaffd2dfe6bc913412bae198cda95379dfc9baecfa`, new `afe32fa44d61ad12d8da38fb15d9691ec3056f8566586b106abba619f13232b8`; W46 parent pin `82d08bd1a97737740ce1fe1559cc0a90a21ce2704b6dd188be3697e3985357d0` 확인 대상 불변.
- 변경: `capture()` 진입 시 `input_receipt`를 얕은 `dict` snapshot으로 복사. 제품 source/바이너리/원본/기존 raw/fixture/op는 변경하지 않았다.
- 실행명령: `python3 -m py_compile <runner>`; 합성 receipt→`g0_h1["capture"]`→`json.dumps(run_summary)` 회귀; 허용 op 정적 검사; `checks/safety.sh check`.
- 수치/결과: `SYNTHETIC_RUN_SUMMARY_JSON_PASS`, `ALLOWED_OP_STATIC_PASS`, `SAFETY_PASS`; py_compile exit 0. 추가로 `make check` **835 passed in 497.43s**, Ruff/compileall/mypy/`CONTEXT_PASS` 통과. 실제 게임 fresh 실행 0회, samples/raw 신규 0행.
- fixture: W49R 카드 고정 fixture(8 AI, map100×100, cap5000, mixed seed, ops `{5,6,7}`)를 실행하지 않고 serialization만 검증했다.
- 판정: **수리 PASS / 실행 BLOCKED(harness_contract 유지)**. 현재 회차는 §134의 fresh 재실행 금지와 승격 판정 대기를 따른다.
- 다음: middle/strategy가 얕은 snapshot, `g0_h1`·`g0_h2` 및 이후 receipt의 비순환성, 기존 보존 캡처/manifest, owned cleanup을 독립 검수한 뒤 fresh 실행 허용 여부와 예산을 판정한다. 이 회차에서 fresh 재실행·G2 PASS·사용자 승인을 주장하지 않는다.
