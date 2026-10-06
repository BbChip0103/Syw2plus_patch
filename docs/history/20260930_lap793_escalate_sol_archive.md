# lap793 승격 요청 — G2 Phase C raw/source 충돌

lap792의 집결·장수 UI 계약 미확정 자체는 후속 raw 3개와 일치하지만, “fresh 4회
모두 worker 생산 `2→3`”이라는 기록은 첫 raw와 충돌한다. 첫 raw `a8acdf47…9bf71`은
`count 2→2`, `worker_produced=false`, hero stage 없음이고, rally true도 HQ before/after가
없는 구형 판정이다. 후속 3개만 worker `2→3`과 rally 불변·hero `0→0`을 보인다.
현 probe 파일은 마지막 raw 뒤에 수정됐으므로 현재 source를 네 raw의 동일 계약으로
간주하지 않는다. Phase C·배포·승인은 HOLD한다.

승격 작업자가 이어서 검증할 것:

1. raw별 probe revision/source identity를 복원하거나, 첫 raw를 명시적 사전수리 실패로
   제외하는 판정과 근거를 남긴다. 단순히 4/4로 다시 적지 않는다.
2. work tier에 baseline EXE의 HQ `+0x654/+0x656` write xref를 먼저 추적시켜 명령 ID,
   버튼 셀/단축키, 마우스 버튼·유효 target 조건을 고정한다. 장수는 `+0x980` writer와
   command-panel enable/production 경로에서 실제 fixture·버튼 활성 조건을 고정한다.
3. 고정된 현 스키마로 normal baseline fresh 1회를 실행해 worker `2→3`, rally field 변화,
   hero count/type/cmd/도착을 한 raw에서 검증한다. 그 뒤에만 normal/fixed_start ×
   baseline/candidate 4-way Phase C로 진행한다.

근거: `docs/history/laps/20260930_lap793_middle_g2_phase_c_raw_conflict_escalate.md`.
lap792 ESCALATE 원문은 `docs/history/20260930_lap792_escalate_sol_archive.md`에 보존했다.
