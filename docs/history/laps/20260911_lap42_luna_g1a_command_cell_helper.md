# 2026-09-11 | lap 42 | 목표 G1-A

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-luna`/high work. 현재 세션의 실제
  모델 식별자는 별도 노출되지 않았으며, Sol/high 독립 검수는 다음 세션으로 남겼다.
- 가설 / 사용자 관찰: lap40 middle이 지적한 type58 base 오기와 hit/click callback 혼선을
  고정 원본 근거대로 read-only helper와 회귀로 닫으면, 다음 runtime-read에서 좌표 의미를
  측정할 수 있다. helper는 다른 SHA를 즉시 거부해야 한다.
- 예상 PASS / FAIL 조건: selection count/slot, active unit/type, type table 4 DWORD, pool
  group 2..5의 네 callback cell과 `(670,490)` strict 단일 hit를 읽고, invalid SHA/slot/type/
  0개·다중 hit를 거부하면 PASS. 필수 targeted runtime tests, `make check`, safety가 모두
  PASS해야 한다. 게임/패치 실행은 이 바퀴에 포함하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA256
  `9e82a19e2888c04701dca40baf22fa5391c13775e7e60b531671829342d84845`,
  `tests/test_runtime_env.py` SHA256
  `cc4ab409af4c6ac23c906cc52414f9072c2c64c96739e15dd8a201f4421b2060`,
  `analysis/memory_maps/player_offsets.md` SHA256
  `b2897bdecbb6e86de76f649073c230334b471ac28a911559347e1f3e164b59e5`.
  `docs/STATUS.md`와 이 기록도 갱신했다. Git unborn/uncommitted, `LOOP_ALLOW_COMMITS=0`,
  commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본
  `../Syw2plus/syw2plus_original.exe` SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 EXE/DLL/assets
  없음. 활성 플레이어/지도/군대는 N/A. 가상 read-memory fixture만 사용했고 원본/게임 실행은
  하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 원본 `sha256sum`, `objdump -d -Mintel`로
  `0x0041F630/0x0041FA60/0x0041FBC0/0x0049B6D0`를 읽기 전용 재확인;
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py`;
  `make check`; `bash checks/safety.sh check`; `wc -l docs/STATUS.md`. 새 로그/PNG/game run/
  patch/restore 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 사전 targeted **35 passed**; 사전 `make check`
  **105 passed**, Ruff/compileall/mypy/context PASS; safety **SAFETY_PASS**. bookkeeping 뒤
  최종 `make check`는 **92 passed/13 failed**였고, 모두 임시 loop fixture가 복사한
  `docs/STATUS.md: 181 lines exceeds 180` startup safety 차단 파생 실패였다. 지시대로 최종
  safety는 SKIP했으며, 현재 원 저장소 STATUS는 180줄로 정리했지만 이를 재검증하지 않았다.
  type58 base는 `0x0066BE88 + 58*0x758 = 0x00686878`로 고쳤고, pool slot1~30에서 active,
  group, geometry, category, flag, `+0x54=0x0049B530`, `+0x58=0x0049B640`를 기록하며
  strict hit가 정확히 하나인지 검사한다. 0개·다중 hit 및 invalid selection/type를 회귀했다.
  **1단 하네스 수리 PASS**. 실제 runtime cell 값/worker 의미, `(670,490)`의 원본 실행 hit,
  G1-A/G1~G4 제품 결과는 UNKNOWN/미완료.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 최초 targeted 실행의 2개 실패는 fixture
  비대상 cell 좌표가 겹친 테스트 작성 오류였고, 좌표를 수정한 뒤 35 PASS로 확인했다. 구현
  오류로 판정하지 않는다. 최종 Fast 실패는 별도 Sol/high recovery가 필요하다. 실제 새
  runtime-read/game run은 새 Sol/high 독립 검수 전 금지; 제품 마일스톤 사용자 승인 없음.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high middle이 세 변경 파일, 원본 SHA, type58 산술,
  callback 경계와 105 PASS/safety PASS를 독립 검수하고, 그 뒤 runtime-read 1회 허용 여부를
  판정한다.
