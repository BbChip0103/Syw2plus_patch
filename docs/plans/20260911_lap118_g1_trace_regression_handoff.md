# 2026-09-11 lap118 — G1 trace regression hardening handoff

## 중간 판정

Codex `gpt-5.6-sol`/high 중간 검수 판정은 **SOURCE INTENT CONFIRMED / REGRESSION REVISE /
GAME RUN BLOCKED**다. lap117의 현재 source fingerprint는 기록과 일치하고, 재사용 surface에서
installed/object/clone-vtable/wrapper identity를 모두 확인한 뒤에만 method count 49를 기록하며
불일치는 failed trace로 남긴다. runner도 source상 owned window close, process exit와 bridge final
summary 확인, trace copy, validator 순서다.

그러나 lap116 카드가 요구한 행동 회귀는 아직 직접 고정되지 않았다. 현재
`test_reused_surface_requires_identity_and_preserved_clone_before_49_methods`는 C source 문자열만
검사하며 같은 surface 재반환 결과나 stale-uninstalled 분기를 실행하지 않는다. finalization PASS
테스트는 summary가 미리 존재하고 process가 이미 종료된 fixture라 실제 close 이후 summary 관측
순서를 검증하지 않으며, summary 부재 테스트는 helper만 호출해 최종 runner의 raw 보존 및 validator
미호출을 고정하지 않는다. 따라서 fresh runtime은 허용하지 않는다.

## 새 Luna/high 실무 한 가지

한 가지 변경은 **게임을 실행하지 않고 lap116의 trace-contract 행동 회귀를 직접 고정하는 것**이다.

- 허용 파일: `tests/test_direct_draw_abi.py`, `tests/test_runtime_env.py`와 테스트 seam에 꼭 필요한
  `tools/inmm_stub/direct_draw_trace.c`, `tools/runtime_env.py`의 최소 변경. 게임 EXE/DLL/assets,
  validator 30/49 상수, 좌표, timeout, fixture 값은 변경하지 않는다.
- surface 회귀는 (a) installed+동일 object+동일 clone vtable+4개 wrapper+4개 original method가 모두
  맞을 때만 재사용 성공/49 기록, (b) object, clone vtable, 각 wrapper, stale-uninstalled 중 하나라도
  어긋나면 failed status이고 49가 아님을 실행 가능한 seam 또는 동등한 mutation-resistant 검사로
  각각 증명한다. 단순 토큰 존재 assertion만 추가하지 않는다.
- runner 회귀는 호출 순서를 `owned windowclose -> owned process exit -> 정확히 하나의 bridge summary
  (final event) -> trace copy -> validator`로 관측한다. summary 0/2개, summary-not-final, process 미종료
  각각에서 validator가 호출되지 않고 raw가 보존되며 BLOCKED가 되는지 확인한다.
- cleanup 대상이 기존 private display/prefix의 owned process/window에만 한정되고 전역 kill이 없음을
  유지한다. 테스트를 통과시키기 위해 summary를 합성하거나 validator 요구를 완화하지 않는다.

## 검증과 중단

관련 targeted tests, 저장소 밖 fresh bridge build, `make doctor`, `make check`,
`bash checks/safety.sh check`가 모두 PASS해야 한다. 원본 SHA
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 유지하고 원본/게임
복사본을 쓰지 않는다. 예상 밖 실패나 구현 근거 충돌은 변경과 출력을 보존해 새 Sol/high에
승격한다. 모두 통과해도 다음 새 Sol/high 독립 확인 전 fresh runtime과 G1/M1 승격은 금지한다.
