# 2026-09-23 | lap 545 | 목표 G2 (S1 교전 경로)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, strategy(major direction). `ESCALATE_SOL` §98 회부 처리.
- 가설 / 사용자 관찰: W41 1·2차 `PROBE_VOID`는 배치 결함(N200': owner2 anchor 행 지형 차단으로 47/46칸 + 행 우선 줄바꿈 스필)이며, N199(전열이면 교전)는 미시험이다.
  원본 배치 검사기 `FUN_0042ecb0`의 칸 판정식(N201)으로 시딩 전 읽기 전용 사전 스캔이 가능하다.
- 예상 PASS / FAIL 조건: 이 회차는 판정 문서다. 판정은 §98 (A)/(B) 중 하나를 근거와 함께 고정하고, 다음 work 회차가 바로 실행할 수 있는 사양(gate·선택 규칙·분기)을 남기면 완료.
- 변경 파일 / source fingerprint / 커밋: `docs/work/active/G2_STRATEGY_W41R_PRESCAN_LAP545.md`(신규), 이 기록(신규), `loop/ESCALATE_SOL` §99 추가, `docs/STATUS.md`, `docs/feedback/INBOX.md`. 제품 source·브리지·하네스 변경 0. 커밋 0(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본·후보 불변(게임 실행 0). fixture는 W41과 동일(8 owner, seed42, 100×100, type5 100·type7 25·type2 60·type46 20).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 temp/Syw2plus_patch/g2_capacity/20260923_lap544_middle_w41_review/recompute_w41_h20.py | sha256sum` → `f9f805faf651f265a54b4aef71f72ef724ce2de743a4adc519cd647fd67abb42`(lap544 산출과 일치).
  - 입력 SHA 확인: `w41_run.py` `a6ea50fb…`, 시도1 `t0_positions.json` `ffdb070e…`, 시도2 `064681fb…`, 재계산 스크립트 `57298919…`.
  - 행 점유 재집계(인라인 python, 산출 저장 없음): owner2 row40 47+row41 13(x0~15) / row42 46(x22~99)+row43 14(x0~13); 60기 단일 행 수용: 24·48·50·76·84; front 밖 배치 두 시도 동일(결정적).
  - 읽기: `Syw2plus_re/analysis/ghidra_output/FUN_0042ecb0.c`(참고 저장소, 읽기 전용) — 판정식 N201.
- 측정값 / 판정: §98 **(B) 채택**, (A) 기각. W41R 1회(사전 스캔 H21·해독기 자기검증 H21a·짝 (2,3) 행 선택 규칙 H22), 이후 재시도 0회. `ENGAGED_FRONT` 외 모든 결과는 S1 op8 경로 `BLOCKED` 확정·사용자 보고.
  N200 기각·N200' 동의. 신규 N201(칸 판정식: 색인 `(rowoff[y]+x)*2`, 점유 `map+0x5980`, 지형 `map+0x598c` & `0x236A`).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 위험 — 해독기 오독(→ H21a가 두 시도 원시 8 anchor 정확 일치로 차단), y34~42 전 행 불가(→ `no_front_row` gate, 시딩 없이 종료).
  문서 연속 2회(lap544·545) ⇒ 다음은 실행 필수. 사용자 번복 가능 통지(질문 아님). 제품 마일스톤 승인 없음.
- 산출 해시(uncommitted): 카드 SHA256 `f7c37f624c1c2297…`. 검사: `CONTEXT_PASS`, `SAFETY_PASS`(문서 변경뿐이라 `make check` 생략).
- 다음 한 가지: work(Sonnet5) W41R 게임 1회 foreground 완주(카드 §2·§6). middle 카드 없음.
