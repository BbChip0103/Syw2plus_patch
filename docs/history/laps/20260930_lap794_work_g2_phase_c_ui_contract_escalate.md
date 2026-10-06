# 2026-09-30 | lap 794 | G2 ESL2608 Phase-C UI 계약 수리 후 승격

- 실제 provider/model/effort / 지정 역할: Codex 실무 작업자 / native Codex 세션 / high.
- 가설 / 사용자 관찰: lap793 handoff대로 baseline EXE에서 rally writer와 hero 활성 경로를 고정하고,
  normal baseline fresh 1회에서 worker/rally/hero를 함께 검증한다. 첫 raw는 사전수리 실패로 제외한다.
- 예상 PASS / FAIL 조건: worker `2→3`, `+0x654/+0x656` rally 변화, nation-indexed hero count 증가와 새
  hero unit, source unchanged, cleanup PASS. 하나라도 없으면 제품 결함으로 승격하지 않고 원인을 분리한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `analysis/memory_maps/g2_esl2608_phase_c_ui_contract_lap794.md`,
  `tools/g2_esl2608_phase_c_production_probe.py`,
  `tests/test_g2_esl2608_phase_c_production_probe.py`, `loop/ESCALATE_SOL`; 모두 uncommitted.
  원본 source SHA `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: normal baseline SHA 위와 같음;
  private game copy + Wine prefix + Xvfb 1600x1200, synthetic unit spawn 없음, live nation 2/3 startup,
  HQ slot 1199. r2/r3/r4 모두 worker UI production fixture를 사용했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `pytest -q tests/test_g2_esl2608_phase_c_production_probe.py` → 3 passed (r3/r4 선행).
  `python3 tools/g2_esl2608_phase_c_production_probe.py --lane normal --variant baseline`을
  `local/runtime/lap794_phase_c_normal_baseline_{r2,r3,r4}`와 대응 temp artifact에서 실행했다.
  raw: r2 `bf53ae1991e3ad6478f638f4da824fe8082a429ead797f81be7ec6d3cd6c0834`, r3
  `9e15c7bd1483f80f1e1f7f668d9cd0721ca0ce01d306d87fca698d62bfe2e84c`, r4
  `366d52bc342eaa534b5c136c2b2338c1f6a7e30bbd669271b8c4f25509e40fe3`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 정적 scan은 `0x4125A5/0x4125AF` rally writer,
  command `0x15`, `0x43E7F0` hero eligibility와 callers `0x406B68/0x48D1B7`를 고정했다.
  r2는 잘못된 좌클릭으로 selection 0·rally unchanged. r3는 R+우클릭에서 selection 1·rally
  unchanged, nation2 `(740,540)` no order. r4는 direct 우클릭·rally unchanged, nation2 `(704,540)`
  resource reserve 및 count `3→4`, 그러나 fixed counter read로 hero check false. **Phase C HOLD/ESCALATE**.
  세 raw 모두 source unchanged, game removed, prefix residual 0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted pytest PASS. 제품 EXE 변경 없음.
  Phase-C paired, fixed_start/candidate, rally UI input path, nation-indexed hero fresh rerun, DxWnd,
  저장/부하/멀티 및 사용자 승인은 미검증. G1/G5는 HOLD. Final `make check`: 1163 passed, 5 skipped
  in 726.76s, Ruff/compileall/mypy/CONTEXT_PASS, `checks/safety.py` `SAFETY_PASS`, exit0.
- 다음 한 가지: `loop/ESCALATE_SOL` 지시대로 live UI event→`0x412540` argument/this trace로 rally 입력
  계약을 독립 고정한 뒤 nation-indexed hero counter를 포함해 normal baseline 1회를 재검증한다.
