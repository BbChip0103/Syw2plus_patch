# lap162 승격 — P3 runtime 실행 진입 실패

## 현재 상태

P3 tick 관측 코드는 구현됐고 단위/Fast 검증은 통과했지만, 승인된 fresh runtime 1회가
게임 실행 전에 `ModuleNotFoundError: No module named 'patches'`로 중단됐다. 따라서
finalization `tick` 표본, PS3 렌더, close 의미론은 관측하지 못했다. 재시도하지 않았다.

## 보존된 근거

- 변경 source: `tools/runtime_env.py` SHA `f05b4c1c8e77f07a2b90a8fb6c833444ca090691531c2f6d7a91fb9cbc1750c8`;
  `tests/test_runtime_env.py` SHA `9de4d1e68f0e68e503474446c0a38575d963034136e164ae4eacd5830c616ebd`.
- helper build RC0: `/tmp/syw2plus_lap162_build.OHHsLU/helper/`, helper
  `110a2872afb6f11eb27007d3408554a038699ed5c2aad1f822a349d9ec224cd9`, target
  `be6f75b5db76e16036c1bf5d431b7eb916b81b432b3372069ce43f2849a8231e`.
- bridge build RC0: `/tmp/syw2plus_lap162_build.OHHsLU/bridge/_inmm.dll`, SHA
  `191814a24ba4e9ce79a1f1525a73e67daf541418f21c845b09eb2957dade0621`.
- `make check`: `190 passed`, Ruff/compileall/mypy/CONTEXT_PASS; safety: `SAFETY_PASS`.
- prepare/check/doctor: PASS. Fresh run: `local/runtime/20260911_210036_823051_0`.
- attempted exactly once:
  `python3 tools/runtime_env.py g1-presentation-trace --manifest local/runtime/20260911_210036_823051_0/manifest.json --screen 1600x1200x24 --timeout 90 --win32-close-helper /tmp/syw2plus_lap162_build.OHHsLU/helper/win32_close_helper.exe --dxwrapper-2x`
- preserved output: `local/runtime/20260911_210036_823051_0/output/g1_presentation_trace/`;
  `verdict.json` SHA `0d500d6c301e48377bc69e131d72736665619aa629f50a088f9eea0050ed7a41`,
  `evidence.json` SHA `f8255c664e55d6151da26b37a2d339ce0d67b092da777ce54ee1b8aa44cacf13`,
  `provenance.json` SHA `ca0683c2fdc4d03729dc6fd908ef08620439340673a55e27f97b954d0d9749d1`.
  Verdict records `prefix_processes_after=[]`, but `wineserver -k` failed and
  `dxwrapper_config_restored=false`; no owned process residue was reported. Existing unrelated
  Xvfb processes were observed and were not touched.

## 승격 작업자가 이어서 검증할 것

1. `tools/runtime_env.py:2602`의 package import가 현재 고정 실행 표면에서 왜 `patches`를
   찾지 못했는지, 그리고 handoff가 허용하는 실행 형식(`.venv/bin/python`/module invocation)
   중 어느 것이 계약에 맞는지 middle tier가 독립 판정한다.
2. cleanup `wineserver -k` 실패의 원인을 소유 범위 내에서 확인한다. 전역 프로세스 정리나
   기존 Xvfb 종료는 금지한다.
3. 위 판정과 새 승인 이후에만 새 parent/prefix/display에서 P3 fresh runtime을 정확히
   1회 재개하고, 기존 run은 재사용하지 않는다. tick 표본 없음을 P3 결과로 승격하지 않는다.

원본/참고/제품 binary·assets·baseline·golden은 수정하지 않았고 커밋하지 않았다.
