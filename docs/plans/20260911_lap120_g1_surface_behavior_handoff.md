# 2026-09-11 lap120 — G1 surface reuse 행동 회귀 수리 handoff

## 중간 판정

Codex `gpt-5.6-sol`/high 중간 검수 판정은 **RUNNER PIPELINE CONFIRMED / SURFACE
REGRESSION REVISE / FRESH GAME RUN BLOCKED**다. lap119의 finalization 테스트는 owned window
close → process exit → 유일한 final summary → trace copy → validator 순서와 실패 시
raw 보존/validator 미호출을 실행 경로에서 직접 고정한다.

반면 surface 테스트는 `surface_record_reusable` 본문에 16개 토큰이 존재하는지와
각 토큰을 지운 문자열이 목록 검사에 걸리는지만 본다. 첫 실패 `return FALSE` 를
`return TRUE`로 바꾸어 실제 의미를 뒤집은 소스도 현재 토큰 계약이 수락하고 native
문법 검사가 통과했다. lap118이 금지한 단순 토큰 assertion에 해당하므로 fresh
runtime은 허용하지 않는다.

## Luna/high work 한 가지

게임을 실행하지 말고 **production에서 쓰는 동일 C 판정 경로를 실행하는 surface
reuse 회귀**만 추가한다.

- 허용 파일: `tools/inmm_stub/direct_draw_trace.c`, `tests/test_direct_draw_abi.py`와 테스트
  seam에 꼭 필요한 최소 헤더/테스트 파일. runner, validator 상수, 좌표, timeout,
  fixture 값은 바꾸지 않는다.
- native 테스트가 실제 `surface_record_reusable` 또는 production hook이 공유하는 동일
  결정 helper를 호출해 installed/object/clone-vtable/4 wrapper/4 original method 전부가
  일치할 때만 reuse 성공·49를 반환함을 증명한다.
- 각 단일 조건 불일치와 stale-uninstalled record에서 failed status, method count 0,
  해당 install failure reason을 직접 검사한다. 소스 토큰 존재만을 검사하거나
  독립 Python model로 production 판정을 대체하지 않는다.
- production 분기와 테스트 seam이 다른 논리를 복제하지 않도록 한 함수/결정값을
  공유하고, 테스트용 진입점은 diagnostic build에만 노출한다.

## 검증과 중단

targeted native/runtime tests, 저장소 밖 fresh bridge build, `make doctor`, `make check`,
`bash checks/safety.sh check`가 모두 PASS해야 한다. 원본 SHA
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 유지하고
원본/게임 복사본을 쓰지 않는다. 예상 밖 실패나 근거 충돌은 재시도 없이
보존한다. 모두 통과해도 다음 새 Sol/high 독립 검수 전 fresh runtime/G1/M1
승격은 금지한다.
