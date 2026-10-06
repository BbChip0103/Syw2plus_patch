# 2026-10-04 | lap 960 | G1 strategy — lap959 승격 판정: V2s Scale2x 기준 재정의 · refresh churn 수리 인계

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / strategy(큰 방향·검증 구조 분기). `loop/.lap_counter` 960 읽기만.
- 목표: G1. 입력 = `loop/ESCALATE_SOL`(lap959 work, SHA256 `7243937b…bc40`, 14줄) — byte-exact 보존 `docs/history/20261004_lap960_prior_lap959_escalate_sol_byte_exact.txt` 뒤 제거.
- 가설: (1) V2s raw 한도는 정상 Scale2x 모서리를 세므로 coverage와 구조적으로 충돌한다. (2) 성능 저하는 hit 비교 evict → 재바인드 churn이다. (3) minimap HOLD는 클릭 전 상태 분기다.
- 변경 파일(문서만): `docs/work/active/G1_STRATEGY_W70_V2S_REFERENCE_REFRESH_LAP960.md`(SHA256 `45f5bade…8606`), 이 기록, `docs/history/20261004_lap960_prior_lap959_escalate_sol_byte_exact.txt`, `docs/feedback/APPROVALS.md`(strategy 판정 1줄), `docs/STATUS.md`. 게임·하네스·source·test·validator 변경0, 실행0, commit0.
- 원본·후보 SHA: 원본 `game.exe` `b56986e0…a8ac`·`save006.dat` `616b7997…d064` read-only MATCH. 검토 source `g1_mirror2x.c` `531f1a4b…9bf59`·`test_g1_mirror2x.py` `321a9322…2e7d8` = lap959 기록(uncommitted 보존).
- 실행 명령(공유 temp `20261004_lap960_strategy_review/`, 제품 helper 미사용):
  - `.venv/bin/python v2s_scale2x_reference.py` → `v2s_scale2x_reference.json` `ba3584f6…e96`(lap957 r1~r3·lap959 r1)
  - 같은 스크립트 + lap901 3 pair·lap854 3 pair 인자 → `v2s_control_fixtures.json` `829a7de1…b5`; 스크립트 SHA256 `30e8c24a0274ddf19672f1084f2be72d651bb14c9fa8829692a094b0e88e0241`
  - `python3 perf_replay_timeline.py` (`34936a31…2552`) → `perf_replay_timeline.json` `32e55767…80ed`
- 수치:
  - V2s raw 재계산 = lap959 pair-result(1,732/1,667/1,670/1,675/2,813) 정확 일치, lap903 표(476~614 / 18,882~20,056) 정확 재현.
  - Scale2x(원본) 기준 단일 흑색 블록: 35/35 tag 2,166~3,547(>2,000). unexplained: lap901 결함 18,712~19,901, lap854 456~587, lap957 8~158, lap959 22~220.
  - 성능: PS3 서수≥150 refresh lap957 0 → lap959 641, steady replay 0.03~0.09 → 2.37~2.55/present; PS3 0~50 replay 20.7/present·p95 53ms(lap957 4.0·10ms); inserts 1,757 vs keys 781.
  - minimap: 후보 slot170 클릭 전 command4·(146,100) vs 원본 command1·(147,99); lap957 r1~r3 parity PASS.
- 판정: D1 V2s를 "Scale2x(원본)로 설명되지 않는 단일 흑색 ≤2,000"으로 재정의(한도·tag·집계 불변, raw 계속 기록, strategy 판정·사용자 번복 가능). D2 hit 비교를 viewport 안으로 제한하는 최소 수리 FEASIBLE. D3 minimap HOLD 유지·클릭 전 분기 귀속(가설), D2 뒤 재판정. lap959 pair-result는 재작성하지 않음. G1 HOLD·마감 아님.
- PASS/FAIL/SKIP: 판정 문서 PASS(raw 재계산 근거). 게임 실행 SKIP(strategy). 전체 `make check` SKIP(문서만 변경, source 불변·lap959 full PASS 1515 passed; 다음 work가 source 변경 뒤 실행). focused 검사 결과는 STATUS에 보강.
- fixture: save006 비합성, 활성8인 부하증명 아님.
- 다음 행동: Sonnet work 1 lap — 카드 §4 W-1(V2s 재정의 구현·오프라인 회귀) → W-2(hit 비교 viewport 제한) → fresh save006 scale2x pair, 예측 R-1~R-5.
