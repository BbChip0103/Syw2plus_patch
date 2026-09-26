# 2026-09-25 | lap 590 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Codex native middle(모델 ID·effort 비노출) / 진단·계획·확인. 게임 코드·바이너리·runner·공유 temp는 수정하지 않았다.
- 가설 / 사용자 관찰: lap589 W49S 카드가 Q12-2 `(나)`의 “AI 포함 활성 8명”과 기존 8-owner runtime 계약을 같은 뜻으로 구현 가능한지 확인한다.
- 예상 PASS / FAIL 조건: 카드의 S0·고정 입력·종료 라벨이 Q12 원문 및 현행 `_g2_initial_creation_gate`의 owner/AI 역할과 일치하면 `ACCEPT / W49S_WORK_READY`; 활성 8명을 AI 8명으로 좁히거나 정상 로비의 로컬 사람 슬롯을 누락하면 `REJECT / BLOCKED(plan_contract)`.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 이 기록, `docs/STATUS.md`, `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL` §140. 제품 source·게임 코드·바이너리·runner·raw·캡처 변경 0, 커밋 0. 최종 fingerprint와 Fast 결과는 STATUS에 기록한다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 실행 0. 문서가 고정한 원본 `b56986e0…a8ac`, 결합 후보 `dfdc91ad…3883`, 지도100×100·cap5000·혼합 fixture는 변경하지 않았다. 올바른 활성 구성은 현행 creation gate 기준 owner0 로컬 사람(`ai=0`) + owner1~7 AI(`ai=1`) = 총 8명이다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sed`/`rg`로 `loop/PROMPT.md`, INBOX/APPROVALS/STATUS/DESIGN, W49S 카드, lap589 제출문·기록·§139, `tools/runtime_env.py`의 `_g2_initial_creation_gate`와 UI lobby 경로를 대조했다. 새 게임·probe·캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **`REJECT / BLOCKED(plan_contract)`**. Q12 최신 기록은 “활성 8명(AI 포함)”이고 제출문 Q12-2 `(나)`는 “사람 1명 + AI 또는 AI 8명”을 허용한다. 반면 카드 §2·§3.3은 “8 AI”를 고정하고 UI가 AI 8명을 채우지 못하면 `NOT_FEASIBLE(ui_8ai)`로 닫는다. 현행 `_g2_initial_creation_gate`는 정확히 owners0..7과 AI vector `[0,1,1,1,1,1,1,1]`을 요구한다. 또한 양성 `g1_baseline` UI 경로는 코드상 “default two-player random game”이므로 정상 로비 렌더 가능성만 지지하며 8-active UI 설정 가능성은 아직 증명하지 않는다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap589의 §138 재계산·S5′ 게시·Q12 A/나/iv 결정 자체는 이번 판정 범위에서 유지한다. W49S 게임 예산은 소비하지 않았고 화면·G2 PASS·사용자 마일스톤 승인은 없다. source가 lap589 이후 달라 기존 Fast 결과는 현재 검증으로 승격하지 않는다.
- 다음 한 가지: strategy 승격 작업자가 §140의 의미 충돌을 확인하고, 동의하면 W49S S0를 “owner0 로컬 사람 + owner1~7 AI = 활성8명”으로 고쳐 `NOT_FEASIBLE(ui_8active)` 조건과 PS3 role gate를 명시한다. 양성 2-player 캡처는 H-path 대조에만 쓴다. 그 뒤 work가 카드 §3→§4를 계획 회차 없이 실행한다.
