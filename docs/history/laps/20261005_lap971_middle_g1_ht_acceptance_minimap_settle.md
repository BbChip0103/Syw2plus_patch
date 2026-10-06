# 2026-10-05 | lap 971 | G1 middle — lap969 H-T 독립 검수 · 다음 가설 H-M(minimap 관측 settle) 정의

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / middle(중간계획·독립 검수). `loop/.lap_counter` 971 읽기만. lap970 work의 `loop/ESCALATE_SOL`(요지: H-T 재계산, 수용 판정·minimap 누적3회 처리, 다음 가설 (a)/(b)/(c) 선택)을 입력으로 처리하고 삭제했다.
- 가설 / 사용자 관찰: 검수 대상 = lap969 H-T(툴팁 colorkey BltFast 바뀐 픽셀 Scale2x 미러). 새 사용자 관찰 없음.
- 예상 PASS / FAIL 조건: lap969 r1/r2를 제품 helper 없이 재계산해 불일치 0이면 검수 PASS. 수용 기준 = 사전등록 T-1~T-3 충족·반증 조건 미해당·안전 0.
- 변경 파일 / source fingerprint / 커밋: 문서만 — 이 기록, 카드 `docs/work/active/G1_MIDDLE_W70_HT_ACCEPTANCE_MINIMAP_SETTLE_HANDOFF_LAP971.md`, STATUS, `loop/ESCALATE_SOL` 삭제. 제품 source 불변(lap969 uncommitted 그대로, SHA 일치 확인). 커밋 0.
- 원본 SHA / 환경 / fixture: 게임 실행 0. 입력은 lap969 r1/r2·lap966 r1/r2(fresh save006 scale2x pair, 공유 temp 읽기만). 활성8인 부하증명 아님.
- 실행 명령 / 산출 해시: `python3 recalc_lap971.py`(`9e793cb5…62a8`) → `recalc_lap971.json`(`a24ad448…dfc6`), 공유 temp `20261005_lap971_middle_review/`. minimap 4 pair×2 lane raw는 같은 세션에서 probe-result.json을 직접 읽어 비교(카드 §3).
- 측정값 / 판정:
  - 재계산 불일치 0: 교집합 3,689/3,689(r1=r2 픽셀 동일), HUD 상자 0/0, 유닛 961·HP 423·가장자리 813·기타 1,492 불변, lap966 대비 제거 3,492 전부 상자 안·신규 0, present 899/891·p95 9/10ms·cov p50 98.51/98.49%, overlay calls 794/793, 안전 0, V1/V2/V2q/input PASS, V2s FAIL·pair HOLD.
  - **H-T PASS(partial) 수용.** 한계 기록: 바뀌지 않은 경계 픽셀의 Scale2x 블록은 갱신 안 됨(V1 PASS·outside diff 0 범위 안), 두 번째 장면 미검증.
  - **minimap HOLD 원인 확정:** 3회 모두 baseline lane이 첫 샘플(samples=1, 0.0s)에서 소비 전 중간 상태(command=1·pending 16777219)를 `unit_after`로 기록. PASS 관측은 0.16s 소비 후(command=3). 목표 xy·camera는 8관측 동일. 하네스 폴링 종료 조건 문제이며 제품 결함 아님.
  - 다음 가설 **H-M:** minimap 대기 종료 조건에 명령 소비(command 전이)를 추가, 비교식·timeout·판정식 불변. FEASIBLE. 사전등록 M-1/M-2·반증 조건은 카드 §4.
- 회귀 / 남은 위험 / 독립 검수·승인: lap969 결과는 이번 독립 검수로 기술 수용(partial). 사용자 마일스톤 승인 아님. V2s raw HOLD는 APPROVALS 사용자 판단 대기 그대로. 이번 lap은 문서만이고 lap970도 문서만이어서 연속 2회다 — 다음 lap은 반드시 실제 변경·fresh 실행이 있어야 한다(H-M이 그렇다).
- 다음 한 가지: Sonnet work 1 lap — 카드 §4 H-M(minimap settle 하네스 수리 + 회귀 테스트 + fresh save006 pair 2회), 사전등록 M-1/M-2.
