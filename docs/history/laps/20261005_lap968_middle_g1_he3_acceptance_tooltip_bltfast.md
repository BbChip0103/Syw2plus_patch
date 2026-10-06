# 2026-10-05 | lap 968 | G1 middle — lap966 H-E3 독립 검수 · 다음 가설 H-T 정의

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / middle(중간계획·독립 검수). `loop/.lap_counter` 968 읽기만. lap967 work의 `loop/ESCALATE_SOL`을 입력으로 처리했다(원문 요지: (a) F-1/F-2 근소 미달 수용 여부, (b) 다음 가설, (c) r1 minimap HOLD 처리). 처리 뒤 삭제.
- 가설 / 사용자 관찰: 검수 대상 = lap966 H-E3(비클립 바인드 폭 게이트) 수리 결과. 새 사용자 관찰 없음.
- 예상 PASS / FAIL 조건: lap966 수치를 제품 helper 없이 재계산했을 때 불일치 0이면 검수 PASS. 수용 기준 = 마름모 stale 제거·바인드 누락 0·안전 0, F-1/F-2 미달이 명시 잔여로 설명될 것.
- 변경 파일 / source fingerprint / 커밋: 문서만 — 이 기록, 카드 `docs/work/active/G1_MIDDLE_W70_HE3_ACCEPTANCE_TOOLTIP_BLTFAST_HANDOFF_LAP968.md`, STATUS, `loop/ESCALATE_SOL` 삭제. 제품 source 불변(lap966 uncommitted 그대로). 커밋 0.
- 원본 SHA / 환경 / fixture: 게임 실행 0. 입력은 lap966 r1/r2(fresh save006 scale2x pair)·lap963 r1·lap951 r6 census map(공유 temp, 읽기만). 활성8인 부하증명 아님.
- 실행 명령 / 산출 해시: `.venv/bin/python recalc_lap968.py`(`c32262d4…fe9f`) → `recalc_lap968.json`(`e8fbcf5a…20a`); `residual_class_lap968.py`(`401577c5…1267`) → `residual_class_lap968.json`(`d35a3717…a265`). 위치 공유 temp `20261005_lap968_middle_review/`. 입력 SHA: mask r1 `113e2a75…3943`·r2 `0bb664a5…5d72`, trace r1 `5fb5a9b7…2978`·r2 `7a97f38a…2aed`, pair r1 `cb94d306…53ac`·r2 `8632ed48…ea66`(lap966 기록과 일치).
- 측정값 / 판정:
  - 재계산 불일치 0: 교집합 7,181/7,181(r1=r2 픽셀 동일), F-1 813, 가장자리 마름모 행 288~379 1,438→0, 로고 행 792, y≥480 3,637, keys−inserts 0/0, 바인드 8/8, 안전 계수 0. lap963 대비 제거 2,703·신규 4px(로고 내부).
  - **(a) H-E3 PASS(partial) 수용.** F-1(63)·F-2(31) 수치 FAIL은 기록 유지, 사후 임계 변경 없음. 원인 = P6 로고 잔여 예측 과소(643 vs 792+21). compose lookup 가설·strategy 재호출 조건 불충족.
  - **(c) r1 minimap HOLD = 비제품 관측 경쟁.** r1 baseline `unit_after`가 command=1·pending 16777219(목표 좌표는 이미 설정)인 소비 전 tick 관측. 나머지 세 관측은 command=3. effect/result/camera/restore PASS. 누적 2회 재발 시 하네스 관측 수리 lap.
  - **(b) 남은 7,181 분해:** HUD 툴팁 상자 3,492(48.6%, dd_surface_blt 100%) · P6 로고 2,102 · 유닛 덩어리 961 · 선택 HP 바 423 · 기타 203. "x700~760 1,895"는 로고 1,310+유닛 548+37이라 독립 덩어리가 아님(정정).
  - 다음 가설 **H-T:** candidate trace PS3 `blt_fast` caller `0x004960A5`, 300×100 source, rect 101×40, SRCCOLORKEY, 비primary 832×600 back buffer (618,500), `mirror_gate_reject=not_primary` → 패널 전송 뒤 미러되지 않는 툴팁 BltFast가 픽셀을 바꿔 매 프레임 stale. 커서는 끝까지 (668,540). FEASIBLE.
- 회귀 / 남은 위험 / 독립 검수·승인: lap966 결과는 이번 독립 검수로 기술 수용(partial). 사용자 마일스톤 승인 아님. V2s raw HOLD는 APPROVALS 사용자 판단 대기 그대로. 미검증: production.png에 툴팁이 보이지 않는 이유(캡처 시점이 hover 지연 전일 가능성, UNKNOWN — 판정은 stale mask로 한다).
- 다음 한 가지: Sonnet work 1 lap — 카드 §5 H-T 최소 구현(툴팁 BltFast 바뀐 픽셀 Scale2x 미러) + fresh save006 pair, 사전등록 T-1~T-3.
