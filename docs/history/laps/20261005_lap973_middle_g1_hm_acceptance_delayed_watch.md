# 2026-10-05 | lap 973 | G1 middle — lap972 H-M 독립 검수 · 다음 가설 H-W(지연 census watch) 정의

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / middle(중간계획·독립 검수). `loop/.lap_counter` 973 읽기만. lap972 work의 `loop/ESCALATE_SOL`(요지: r1/r2 재계산, r2 +24 판정·필요 시 r3, M-1 수용, 다음 후보 (b)/(c) 정의)을 입력으로 처리하고 삭제했다.
- 가설 / 사용자 관찰: 검수 대상 = lap972 H-M(minimap 대기 종료 조건에 명령 소비 추가). 새 사용자 관찰 없음.
- 예상 PASS / FAIL 조건: lap971 카드 §4 M-1/M-2와 반증 (i)~(iii). 제품 helper 없이 재계산해 불일치 0이면 검수 PASS.
- 변경 파일 / source fingerprint / 커밋: 문서만 — 이 기록, 카드 `docs/work/active/G1_MIDDLE_W70_HM_ACCEPTANCE_DELAYED_WATCH_HANDOFF_LAP973.md`, STATUS, `loop/ESCALATE_SOL` 삭제. 제품·하네스 source 불변(lap972 uncommitted 그대로, `tools/g1_saved_scene_probe.py` `883ee52c…f044`·`tests/test_g1_saved_scene_probe.py` `aff0aad5…bab` 기록과 일치). 커밋 0.
- 원본 SHA / 환경 / fixture: 게임 실행 0. 입력은 lap972 r1/r2·lap969 r1/r2(fresh save006 scale2x pair, 공유 temp 읽기만). 활성8인 부하증명 아님.
- 실행 명령 / 산출 해시: 공유 temp `20261005_lap973_middle_review/`에서 `python3 recalc_lap973.py`(`be897a46…dc55`) → `recalc_lap973.json`(`e6720831…2939`), minimap lane 비교 `minimap_lanes_lap973.txt`(`0bf0e683…099b`), 크롭 `unit_hp_crops_lap973.png`(`bf2a82e3…b9c9`).
- 측정값 / 판정:
  - 재계산 불일치 0: lap972 r1 교집합 3,689·r2 3,713(+24, HUD 상자 12), present 897/876, p95 9/9ms, 안전 0, V1/V2/V2q/input PASS, minimap parity PASS 2/2, V2s FAIL·pair HOLD.
  - **r2 +24 = 덤프 시점 차이:** r2는 PS3 present 876개라 서수 880 덤프가 없다(50/38). 공통 38 덤프로 맞추면 lap969 r1·r2·lap972 r1·r2 교집합이 모두 3,713으로 픽셀 동일. 추가 24px(x616~619·y515~520)는 r1에서 880 덤프에서만 지워지는 픽셀, r2에서 사라진 픽셀 0. 반증 (iii) 해당 없음, r3 불필요.
  - **M-1 PASS·H-M PASS 수용(하네스):** 4 lane 전원 command 3·pending_xy 동일·camera 동일.
  - 다음 후보 근거: 유닛 덩어리·HP 바 stale은 서수 34까지 0, 300부터 존재(HQ 선택·카메라 이동 뒤 생김). census는 첫 64 PS3 present만 기록하므로 lap968의 두 덩어리 writer 분류(다른 run lap951 r6 근사)는 덩어리 생성 전 값 → writer 미확인. 다음 가설 **H-W:** census 창 시작 지연 opt-in(`SYW2_G1_CENSUS_SKIP_PRESENTS`, probe `--census-skip-presents`) + watch (442,155)·(701,237). FEASIBLE. 사전등록은 카드 §4.
- 회귀 / 남은 위험 / 독립 검수·승인: lap972 결과는 이번 독립 검수로 기술 수용(하네스). 사용자 마일스톤 승인 아님. V2s raw HOLD는 APPROVALS 사용자 판단 대기 그대로. 880 덤프 누락 가능성은 이후 교집합 비교를 공통 덤프 집합으로 하라는 기록 한계로 남긴다. 이번 lap은 문서만이며 직전 lap972는 실제 실행이 있었으므로 연속 1회다.
- 다음 한 가지: Sonnet work 1 lap — 카드 §4 H-W(census 지연 창 opt-in + 회귀 테스트 + fresh census-only watch 2회), 사전등록 PASS/FAIL 그대로.
