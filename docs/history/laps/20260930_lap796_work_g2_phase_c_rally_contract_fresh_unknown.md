# 2026-09-30 | lap 796 | G2 ESL2608 Phase-C rally contract fresh run

- 실제 provider/model/effort / 지정 역할: Codex native 세션 / hands-on work / high.
- 가설 / 사용자 관찰: lap795 static contract대로 live command slot `0x11`을 찾아 좌클릭하고,
  action `0x15` 상태에서 다른 유효 지면을 좌클릭하면 HQ rally writer가 좌표를 갱신한다. 같은
  fresh run에서 worker 생산과 nation-indexed hero counter도 확인한다.
- 예상 PASS / FAIL 조건: PASS는 slot/action/queue path/writer/selected HQ `ecx`/`+0x654/+0x656`
  변화, worker `2→3`, hero counter 증가와 hero 생산이다. 입력 계약 또는 유효 지면이 성립하지 않으면
  제품 PASS로 승격하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/g2_esl2608_phase_c_production_probe.py`, 새 read-only trace
  `tools/g2_esl2608_rally_trace.py`, `tests/test_g2_esl2608_phase_c_production_probe.py`.
  모두 uncommitted; 제품 EXE/원본/`../260921_temp`는 변경하지 않았다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: normal baseline
  `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`, 재생성 후보
  `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60`; private game copy,
  별도 Wine prefix/Xvfb 1600x1200, nation2, HQ slot1199, synthetic spawn 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: targeted pytest 4 passed, compileall/ruff PASS.
  `PYTHONPATH=. .venv/bin/python tools/g2_esl2608_phase_c_production_probe.py --lane normal
  --variant baseline --runtime-root local/runtime/esl2608_lap796_phase_c_normal_baseline
  --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/
  g2_esl2608_lap796_phase_c_normal_baseline` → exit2/FAIL.
  Raw `probe-result.json` SHA `95a67252d2cd0a82083a9bbfa5f6bb1a2ac14eb4f25e26029eb38c6a2fb273e7`,
  trace `rally_trace/events.jsonl` SHA `07e7c65f0a4837c69f261eb28d905684cc87c831b7608a3b9ba059acc0112f6f`,
  capture `20260930_074936_final.png` SHA `d7c195c72bffe98309138de5b4e16c16e3460593aac8bf4dd3a6609f462b7540`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): live slots were `[1,10,14,17,115,190,328,329,0,0,0,0]`;
  descriptor `0x11`=slot3/cell `(776,503)`, action after panel click `0x15`. Trace hit
  `0x4AE550→0x4AEC60→0x40FF90→0x412540`; writer `ecx=0x891CB8`, exactly
  `0x0066B790+1199*0x758` (HQ). Packed target `0x36005C` decoded to world `(92,54)`,
  overlapping the HQ at `(91,54)` rather than empty ground, so rally fields stayed `-1,-1`.
  Contract entry/writer is **PASS**, rally effect is **UNKNOWN(input target invalid; no product defect claim)**.
  Worker production is **PASS** (`count 2→3`, resource reservation and new unit). Nation2 hero cell
  `(704,540)` reserved and completed (`count 3→4`, new type75 unit), but indexed counter stayed `0→0`;
  hero-counter validation is **FAIL/UNRESOLVED**, not a product completion claim.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: source unchanged and private game copy was
  removed; prefix residuals were zero. No candidate/fixed_start paired Phase-C evidence, valid rally
  target, DxWnd, save/load, load-bearing stress, multiplayer, or user approval. No retry in this lap.
- 다음 한 가지: Phase D fresh work — retain Phase A/B four-way parity and test the next checklist item
  (normal/fixed_start × baseline/candidate save/load or DxWnd, whichever the next handoff selects),
  while carrying rally as `UNKNOWN(input target not established)` and hero counter as unresolved.
