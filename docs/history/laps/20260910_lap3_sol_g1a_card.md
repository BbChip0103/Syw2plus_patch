# 2026-09-10 | lap 3 | G1-A 중간 실행 카드

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-sol` / high / middle.
- 가설 / 사용자 관찰: 원본800×600 surface와1600×1200 display의 출력·입력 경계를 무패치로
  관측하면 후속 2배 출력 probe를 결정할 수 있다. 현재 하네스는1024×768/제목 클릭1회로 제한됨.
- 예상 PASS / FAIL: Luna가 추가 범위 결정 없이 실행할 명령·fixture·측정식·산출물·중단 조건이
  고정되면 카드 사전 컨펌 PASS. 상위 범위 변경이나 판정 불가능이면 REVISE/승격.
- 변경 파일 / source fingerprint / 커밋: `docs/work/active/G1_A_EXECUTION_CARD.md`,
  `docs/STATUS.md`, 이 기록. uncommitted / unborn HEAD. 게임 코드·EXE/DLL·asset 변경 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본과 기존 격리 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음.
  새 게임 미실행. 카드 fixture는 무수정 원본 기본2인 임의게임이며 실제 성공은 UNKNOWN.
- 이전 바퀴 독립 검수: source hash JSON의8개 파일과 원본/격리 EXE2개, lap2 final_hashes의
  MASTER_PLAN/STATUS/lap2/log를 재해시해 모두 일치. 기존 manifest `check` PASS.
  과거 캡처 시각 재판정과 게임 재실행은 SKIP; G1 증거로 승격하지 않음.
- 실행 명령 / 로그 / 캡처: 읽기 검사 `sha256sum ...`,
  `.venv/bin/python tools/runtime_env.py check --manifest local/runtime/20260910_222434_2612938_0/manifest.json`.
  `make check 2>&1 | tee local/plan/20260910_lap3/make_check.log`.
  새 PNG/24k/144k/멀티는 SKIP.
- 측정값 / 판정: middle 카드 **APPROVE FOR WORK EXECUTION**. 구현/제품 판정은 UNKNOWN.
  구현 무변경 streak=2이므로 다음 바퀴를 반복 계획으로 두지 않고 하네스+실제 G1-A 증거로 고정.
- Fast: pytest **77 PASS** in8.46s, Ruff PASS, compileall PASS, mypy8파일 PASS,
  context PASS. exit0만이 아니라 각 검사 항목을 확인했으며 실제 G1-A 실행 증거는 아님.
- 미커밋 파일 해시: `local/plan/20260910_lap3/final_hashes.json`에 보존.
- 회귀 / 남은 위험 / 승인: PS7→PS3 자연 UI와 입력5종은 미검증. 다음 새 Sol/Opus5 기술 컨펌과
  APPROVALS의 사람 마일스톤 승인은 모두 대기.
- 다음 한 가지: 새 Luna/high가 `G1_A_EXECUTION_CARD.md`만 실행하고, 최대2회 실패/90분에서
  보존·중단한 뒤 결과를 Sol/high에 넘긴다.
