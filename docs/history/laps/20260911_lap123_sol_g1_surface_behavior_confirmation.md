# 2026-09-11 | lap 123 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier 진단·계획·확인 역할이다. 저장소의
  기본 라우팅은 Codex `gpt-5.6-sol`/high이나 현재 대화 표면은 실제 model ID/effort attestation을
  제공하지 않아 exit 0에서 추정하지 않았다. 게임 코드·원본·후보는 수정하지 않았다.
- 가설 / 사용자 관찰: lap122의 production wrapper와 native harness가 동일 shared C decision을
  사용하고 성공 49, 각 단일 불일치와 stale 상태를 failed·0·reason으로 고정하면 surface behavior
  수리를 확인하고 fresh isolated runtime 1회를 work tier에 허용할 수 있다.
- 예상 PASS / FAIL 조건: 입력은 lap120 handoff, lap122 이력, 세 source fingerprint, 기록 bridge와
  보호 원본이다. production input wiring, 성공 `reusable=1/method_count=49/reason=OK`, 재사용 분기의
  모든 도달 가능 실패 `reusable=0/method_count=0/해당 reason`, mutation 검출, doctor/Fast/safety와
  fresh out-of-tree PE32 build가 모두 일치해야 PASS다. token-only이거나 하나라도 실패하면 REVISE다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현 변경 없음. 검수 SHA는
  `surface_reuse_contract.h=24cef29a881c21d4b462e7be3fd631ca46d8b2e1dc0948f8259e899b51e9a3d4`,
  `direct_draw_trace.c=cf9bc6e5b7fca3a66b58ed3dc0411ea1f3265e0dab1c9a53d3a2ff3ed0c40724`,
  `test_direct_draw_abi.py=7fc3d4784f5dd9ee041b13975b10098e57eb3d899307095dbb27108eb5ac1abb`로
  lap122와 일치한다. 본 이력·STATUS·work handoff만 문서 변경; `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 PE32 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, doctor `verified`, 검수 후
  불변이다. 제품 후보·게임·활성 플레이어·지도·군대는 SKIP/N/A. 기록된 lap122 diagnostic bridge
  `/tmp/syw2_g1_lap122_bridge.uQRVl2/bridge/_inmm.dll`은 SHA `0683156b...`/PE32 i386으로 일치했다.
  새 fixture는 `/tmp/syw2_g1_lap123_bridge.C7Y08P/bridge/_inmm.dll`, SHA
  `1b7295145c5f4b9dc641c1a5f104759a89b2b926855fc2c20744ef62f5e0d3b9`, PE32 i386이다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sed`/`rg`/`sha256sum`/`file` 정적 대조; `make doctor`;
  `make check`; `.venv/bin/python -m pytest -q tests/test_direct_draw_abi.py tests/test_runtime_env.py
  tests/test_g1_presentation_trace.py`; 저장소 밖 `build_runtime_bridge.py`; `bash checks/safety.sh check`.
  PNG/runtime trace/game capture는 만들지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): production adapter의 모든 decision input과 소비 분기를
  정적 확인했다. native harness는 성공 49와 stale 포함 도달 가능한 16개 실패 reason을 실행하며
  shared reusable mutation을 거부한다. `NOT_INSTALLED`는 빈 slot의 신규 설치 경로라 reuse helper에서
  도달하지 않는다. targeted **75 passed**, fresh bridge PASS, doctor top `ok=true`/original verified,
  `make check` **162 passed**, Ruff/compileall/mypy/context PASS, safety `SAFETY_PASS`다. 판정은
  **LAP122 SURFACE BEHAVIOR MIDDLE CONFIRM PASS / ONE FRESH RUNTIME ALLOWED**다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: actual Wine DirectDraw present, 1600×1200
  2배 출력·필수 입력, G1/M1은 여전히 미검증이다. binary patch가 없어 old/new bytes,
  unsupported-version, copy-only, non-overlap, exact restore는 SKIP/N/A다. 새 runtime 결과도 다음
  Sol/high 독립 검수와 사용자 판단 전 제품 PASS가 아니다. G2~G4 및 사용자 승인은 미검증/미승인이다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work tier가
  `docs/plans/20260911_lap123_g1_fresh_runtime_handoff.md`대로 새 전체 복사본/prefix/display에서
  G1 presentation trace를 정확히 1회 실행하고 결과와 raw SHA를 보존한다.
