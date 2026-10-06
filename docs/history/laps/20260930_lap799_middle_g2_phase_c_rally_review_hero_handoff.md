# 2026-09-30 | lap 799 | G2 ESL2608 Phase-C lap798 독립 검수

- 실제 provider/model/effort / 지정 역할: Codex native 세션(정확한 모델 ID·effort는 표면 미노출) /
  middle 진단·컨펌 / high 지정. 게임 코드·probe·EXE·runtime은 수정하거나 실행하지 않았다.
- 가설 / 사용자 관찰: lap798의 rally/worker 4-way PASS를 raw에서 독립 재계산하고, hero `0→0`이
  환경 한계인지 검증 가능한 하네스 결함인지 판정한다.
- 예상 PASS / FAIL 조건: 네 raw 모두 pinned EXE SHA, live descriptor `0x11`→action `0x15`, HQ writer,
  rally 필드 변화, worker `2→3`, source/cleanup을 보존하면 rally/worker를 2단 PASS한다. hero는 올바른
  생산 셀·hero flag·counter·실제 생성이 함께 없으면 PASS하지 않으며, 원인이 추적 가능하면 work 수리로 넘긴다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 이 기록,
  `docs/work/active/G2_ESL2608_PAIRED_CHECKLIST_REPAIR_LAP787.md`, `docs/STATUS.md`; 문서/handoff만
  uncommitted. 세션 시작 validation fingerprint `2282358d8300268238950641c0d9452f3beabd35`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: normal baseline/candidate
  `cade60b2…b176a3`/`83c7df80…fad60`, fixed baseline/candidate `f5f816ee…e1973`/`1bdcadf9…9262f`를
  원본 파일과 raw provenance에서 재해시해 일치했다. lap798은 private Wine/Xvfb, owner0 두 유닛,
  synthetic unit 없음; 이번 middle은 저장된 raw만 읽었다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`과 `jq`로
  `temp/Syw2plus_patch/g2_esl2608_lap798/{normal,fixed}_{baseline,candidate}/probe-result.json`을
  재계산했다. SHA는 `dc60c2ee…d590`/`d2394b1d…a07`/`59511504…06a`/`b32d8c65…036`로 lap798과 일치.
  `tools/g4_ai_production_table.py` read-only decode에서 HQ49/58/70의 생산표를 독립 확인했다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **rally/worker 2단 PASS.** 4/4 raw가 descriptor17 slot3,
  action21, queue/writer hits `1/1/2/2`, rally `(94,57)→(94,52)`, worker `2→3`, source unchanged,
  prefix residue0, private game removed를 동일하게 기록한다. 종료코드 `-15`는 probe cleanup의 terminate이며
  crash/timeout 증거가 아니다. **hero는 `HOLD(harness contract)`**: nation1 두 raw는 live slot7 descriptor가
  `0`인데 하드코딩 `(776,540)`을 클릭했고, nation3 두 raw의 descriptor24도 주문/자원 변화가 없다.
  static production table상 HQ hero 후보는 kind94(prereq37), 102(prereq45), 98(prereq46), 100(prereq53)인데
  현 2-unit fixture는 prerequisites를 제공하지 않는다. lap796 nation2가 만든 kind75는 prereq 없는 별도
  생산물이며 hero counter `0→0`; 이를 자연 장수 증거로 쓰지 않는다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap798 probe 전체 status `FAIL`은 hero legacy
  all-checks 때문이므로 rally/worker PASS를 뒤집지 않는다. 반대로 hero UNKNOWN을 환경 제한으로 닫을
  근거도 없다. Phase C hero, DxWnd, 24k/144k, 멀티, 새 이름 두 배포본, 사용자 승인은 미완료다.
- 다음 한 가지: work tier가 fixed nation 좌표와 `HERO_TYPES` 범위 추측을 제거한다. HQ 생산표와 live
  TypeSpec flag `0x8`로 hero kind를 고르고, 필요한 prereq 건물만 명시적 gate-legal fixture로 제공하되
  hero 자체는 실제 HQ UI로 생산한다. live command slot에서 주문 acceptance(HQ production_type·자원/
  reserved), 새 unit type의 hero flag, nation-indexed `+0x980` `0→1`, 초상화 캡처를 먼저 baseline fresh로
  확인하고 성공 시 normal/fixed_start × baseline/candidate 4-way를 완주한다. 성립 실패 시 raw와 정확한
  gate를 남겨 hero를 `UNKNOWN(fixture contract)`로 닫고 DxWnd로 이동한다.
