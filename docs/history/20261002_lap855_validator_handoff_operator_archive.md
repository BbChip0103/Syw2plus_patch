# lap855 일반 middle → 승격 검수자: P3c 필수 validator 누락 / 마감 경계

- 판정: PERFORMANCE_EVIDENCE_ACCEPTED / P3 HOLD_REQUIRED_VALIDATOR_GAP / G1 HOLD / P4 금지. 일반 middle 진단·계획·확인만 수행, 게임/하네스 수정·신규 runtime·커밋0. 사용자 경계 stop으로 종료.
- 상세 기록: docs/history/laps/20261002_lap855_middle_g1_p3c_validator_gap_escalate.md.
- 독립 artifact root: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap855_middle_review/. review.json SHA598466f9417002d5e29c70638746ed531d03bab9b6608d5909057c6ad82ec80c; identity_and_negative.json SHA0e4d0960053528b2f7c988c1b9ccda2aadb2081b60bed4fb0ef4717cb0f5df75.
- 4 pair/build42개/DLL/raw/capture/source MATCH. fresh3 gate ratio0.9999920427/0.9999969883/1.0000019160, p95 delta+5ms. QPC compose6.064623ns/pixel·창0.934623%, lookup1.223141µs/call. raw 부등식 위반0.
- 결함: P3c §1.4/§2-B의 mismatch_blocks≤inside_diff≤4*mismatch_blocks를 Scale2x validator가 검사하지 않음. deficit17384에서 inside1/17385인 synthetic2건도 PASS. runtime 회귀가 아니라 필수 검사 구현 누락.
- fixture 정정: performance units=[]는 state(pid,False)의 생략값. 상세 scene558 unit records·8 player records, 활성8인/G2 부하 증명 아님. 원본/save 직접 재해시 확인.
- 승격 작업자가 이어서 검증: 두 반례·카드 필수 검사 계약·source-matched4 raw 부등식/성능·fixture 정정. 일반 middle 재요약 회차 없이 아래 work handoff를 확인.
- work handoff: tools/g1_hd_scale2x_probe.py와 tests/test_g1_hd_scale2x_probe.py만 수정. present별 deficit 비음수·deficit/4≤inside≤deficit 검사 및 정상 경계/양쪽 위반 회귀 추가. 게임 C/EXE/G2/G5/legacy validator/임계값/P4/pin/golden/기존 raw 변경 금지.
- work 검증: 반례2건 BLOCKED, 정상 fixture 및 기존4 raw 강화 validator PASS. C/build42개 일치 확인 후 lint/typecheck→기록→최종 make check 완주. 게임 source 불변이면 기존 source-matched raw 사용 가능. 최종 P3 수용 판정은 승격 컨펌, P4/사용자 승인 포함 안 함.
- 이번 전체 Fast/runtime SKIP(사용자 경계 stop). lap854 Fast1219 passed/5 skipped는 정확한 로그를 읽은 과거 결과, 이번 fingerprint PASS 아님. 문서/안전 결과는 STATUS.
- 이전 marker byte-exact archive: docs/history/20261002_lap855_prior_lap854_escalate_sol_archive.md, SHA96b53ed20bd84a015982cce9d43b1c38703d4426b18611b909eae906ec407270.
