# 2026-09-11 | lap 77 이후 | STATUS compaction 기록

`docs/STATUS.md`가 정확히 180줄에 도달해 다음 검수 기록의 안전 여유가 없었다. 현재 판정과 lap73 이후 최신 이력은 유지하고 아래 lap66~72 상세를 이 파일로 이동했다.

- 이동 전 `docs/STATUS.md` SHA256: `20de16f4710ba91d0baaa90f44cc9a1a7a826fca40aa994a5764b12d6b51c0fb`
- 각 lap 원문은 `docs/history/laps/`에도 보존된다.
- 코드, 하네스, 게임, EXE, DLL, 자산, runtime artifact는 변경하지 않았다.

## 이동한 원문

- lap66은 `tools/runtime_env.py` SHA `fb19ae214f2d57f285d061019217ed618e3a200727e94ec94f44cb6fb01e464c`,
  `tests/test_runtime_env.py` SHA `c2b8ff3a1d59d779d8ceee79e03896896eadcb61da67ab3d11d7efa3ef7436fb`,
  guards unchanged SHA `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`다.
  targeted **52 passed**, 전체 `make check` **122 passed**, Ruff/compileall/mypy/context PASS,
  safety **SAFETY_PASS**, `make doctor` top `ok=true`/original verified다. 원본과 보존 private EXE는
  모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이며 후보 EXE·새
  runtime·PNG·게임 실행은 없다. 이는 1단 기계 PASS이지 middle/제품/사용자 승인 아님이다.

- lap67은 위 source SHA와 원본/private EXE SHA를 재계산 일치시키고 원본 count0/count1/count>1
  dispatch 및 count1 전용 fill을 재추출했다. targeted runtime/guards **52 passed**는 재현했지만,
  count=0 비변경 probe가 selection count DWORD 한 번만 읽은 뒤 `_CommandCellSnapshotError`를 내면서
  `branch_evidence=null`, `primary_snapshot=null`, primary read=false를 보였다. count evidence 계약
  **FAIL / MIDDLE REVISE**이며 중단 규칙에 따라 전체 Fast/safety/doctor와 game run은 SKIP이다.

- lap68은 `tools/runtime_env.py` SHA `815e90e2e2ffe342eb24ad64135c7be802848a6197bb4ec766b53c023970bbad`,
  `tests/test_runtime_env.py` SHA `cc30931e4279ac25310eefa8c443cf260df4d21ffc1a147a3fcc78115d4dc5ad`,
  guards unchanged SHA `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`다.
  count0/count2 targeted **54 passed**, 전체 `make check` **124 passed**, Ruff/compileall/mypy/context
  PASS, safety **SAFETY_PASS**, `make doctor` original verified다. 원본 SHA는
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`로 일치한다. 후보 EXE·새
  runtime·PNG·게임 실행은 없고, middle 독립 검수와 제품/사용자 승인은 남았다.

- lap69는 위 source/test SHA와 원본/private EXE SHA를 재계산 일치시키고 원본 `0x498FBA`의
  count0/count1/count>1 분기, count1 전용 `0x499201..0x49929E` fill, 공통 `0x499583` consumer,
  writer old bytes를 재추출했다. 독립 count0/count2 probe는 각각 selection count DWORD 1회만 읽고
  `required=1`, 관측 count, `before={count}`, `primary_read=false`, `retryable=false`를 보존했다.
  targeted **54 passed**, 전체 `make check` **124 passed**, Ruff/compileall/mypy/context PASS,
  safety **SAFETY_PASS**, doctor `ok=true`/original verified다. count 수리는 **MIDDLE CONFIRM PASS**다.
  다만 production 호출부의 primary evidence 유실/미승인 click 간극으로 game run은 계속 BLOCKED다.

- lap70은 `tools/runtime_env.py` SHA `89fddce79899fc8cd7b6f1472ab4aefc775605031439726695d45713701d8813`,
  `tests/test_runtime_env.py` SHA `ab344efc0925ac8a67de4ea9bf8292c4c37cf82cc65e22a342ee341d5492ea6b`,
  guards unchanged SHA `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`다.
  stable-ineligible primary output 보존과 eligible/ineligible production callback 미호출 회귀를 포함한
  targeted **57 passed**, 전체 `make check` **127 passed**, Ruff/compileall/mypy/context PASS,
  safety **SAFETY_PASS**, `make doctor` `ok=true`/original verified다. 후보 EXE·PNG·새 game run은 없고,
  새 middle 독립 검수와 primary field/action·worker 의미 승인은 남았다.

- lap71은 위 source/test/guards SHA와 원본·참고 EXE SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 재계산 일치시켰다.
  원본 `0x498FBA` count dispatch, count1 전용 `0x499201..0x49929E` fill, 공통 `0x499583`
  consumer와 `0x4A3B5B` writer old bytes를 재확인했다. no-click/output evidence 직접 3 PASS,
  targeted **57 passed**, 전체 `make check` **127 passed**, Ruff/compileall/mypy/context PASS, safety
  **SAFETY_PASS**, doctor `ok=true`/original verified다. 그러나 문서 기록 후 재실행한 `make check`는
  STATUS 183줄 제한 위반으로 **13 failed, 114 passed**했다. 필수 gate 실패이므로 lap70
  middle 판정·game run 허용은 미완료/BLOCKED로 되돌렸고 승격 재검수가 필요하다.

- lap72는 compaction 결과 STATUS 141줄과 이동 history를 확인하고 source/test/guards 및 원본·참고
  EXE SHA, count dispatch/fill/consumer/writer old bytes를 재대조했다. 직접 **3 passed**, targeted
  **57 passed**, 전체 `make check` **127 passed**, Ruff/compileall/mypy/context PASS, safety
  **SAFETY_PASS**, doctor `ok=true`/original verified로 lap70 source 계약을 **MIDDLE CONFIRM PASS**했다.
  binary patch와 새 runtime/PNG/game run은 없고 제품 G1~G4 및 사용자 승인은 미완료다.

