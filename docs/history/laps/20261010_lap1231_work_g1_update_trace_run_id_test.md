# 2026-10-10 | lap 1231 | G1 work — no-present-trace 회귀 계약 갱신

- 역할: hands-on work. Codex App native-hook; 이 surface에서 실제 resolved model ID/effort 확인 불가, provider 폴백 주장 없음.
- 입력: `loop/PROMPT.md` ①~⑥, 최신 INBOX/APPROVALS/STATUS, DESIGN G1, lap1230 middle 기록. counter=1231 읽기만, STOP·기존 ESCALATE_SOL 없음.
- 가설/합격식: 전체 Fast의 유일 실패는 lap1229 수리 뒤 낡은 테스트가 제거된 TRACE_RUN_ID pop을 요구하기 때문. 테스트는 PRESENT_TRACE 제거와 owned close용 TRACE_RUN_ID 보존을 고정하고, 기존 user-trial 옵션/후보 lane 제한 및 trace 설치 계약을 유지한다.
- 변경: `tests/test_g1_mirror2x.py` 한 함수의 이름·주석·단언만 변경. 제품 코드·원본/참고/raw/golden/pin·게임 하네스·다른 세션 소유 파일 변경 0. 커밋/게시/deploy 0.
- 근거 대조: `tools/g1_saved_scene_probe.py`는 `_disable_present_trace()`에서 `SYW2_G1_PRESENT_TRACE`만 제거하고 후보 lane에서 해당 helper를 호출한다. `SYW2_G1_TRACE_RUN_ID`는 보존된다. 이는 lap1229 소유권 수리 계약 및 lap1230 독립 검수와 일치한다.
- 검사: `.venv/bin/python -m pytest -q tests/test_g1_mirror2x.py::test_ua0_candidate_no_present_trace_flag_preserves_owned_run_id` → 1 passed/0.16s; `make lint` PASS(Ruff·compileall); `make typecheck` PASS(12 files). 기록/STATUS 갱신 뒤 전체 `make check`를 실행하며 결과는 STATUS에만 덧붙인다.
- 원본 EXE/save/후보 SHA·게임 fixture: 사용 안 함. 실제 런타임/24k/144k/Windows/사용자 플레이 증거 없음.
- 상태/다음 한 가지: targeted 수리 GREEN. 전체 `make check`를 완주한다. PASS·fingerprint MATCH면 H-TR2612 fresh candidate pair 2회 + new-game 1회가 다음 work; 시험판 전달 전 fresh middle 검수와 root 사용자 전달 경계는 유지.
