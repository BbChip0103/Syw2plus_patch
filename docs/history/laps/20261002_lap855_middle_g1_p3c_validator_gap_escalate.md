# 2026-10-02 KST | lap 855 | G1 W70 P3c independent review — validator gap / boundary escalation

- 실제 provider/model/effort / 지정 역할: Codex native 새 세션, 사용자 지정 일반 middle(진단·계획·확인). 서비스 model ID/effort는 도구 미노출이므로 Sol 실행/모델 전환을 주장하지 않는다. lap counter855는 읽기만 했다. Solo 검수, subagent·유료 CLI 실행0.
- 목표/가설: lap854 환경 latch가 compose≤50ns/pixel·창의≤2%, lookup≤2.5µs/call 및 계측 OFF fresh3 pair 각각 tick ratio≥0.95·p95 delta≤16ms, source/scene/cleanup·Scale2x·선택/빈 클릭/드래그를 만족하는지 확인. P3 마감 경계에서는 사용자 stop 지시대로 승격, P4 금지.
- 문서 순서: PROMPT→AGENTS/INBOX/APPROVALS→STATUS→DESIGN §1~4→lap854/P3c 카드. 최신 사용자 결정대로 G1 최우선, G2 5000 유지·10000 종료, G3 중단, G4 보류, G5 종료. 기록 전 STATUS105/INBOX259/APPROVALS160줄로 소프트 한도 내였다.
- 변경 파일: 이 기록, docs/history/20261002_lap855_prior_lap854_escalate_sol_archive.md, docs/STATUS.md, docs/feedback/APPROVALS.md, loop/ESCALATE_SOL. 문서/인계만 변경, 게임/하네스 source·binary 수정0, 신규 게임 실행0, 커밋0(uncommitted). 원본/참고·기존 raw/capture·다른 세션 산출물 무변경, runtime 정리0.
- source identity: 4 pair마다 bridge build 입력42개 current SHA MATCH. 생성 snapshot도 builder의 inmm_stub.c poll 삽입·Makefile SRCS 추가를 재현한 뒤42개 MATCH. bridge source/DLL manifest MATCH. 검수 source SHA 목록은 review.json에 보존. 최종 문서 fingerprint 전체 Fast 미검증, 과거 결과 재사용 없음.
- 원본 SHA: [ESL]Syw2plus/[HQ]Syw2plus 2002.exe 직접 재해시 b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac. 비합성 save006 직접 재해시 616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064. 과거 실행 환경은 private game/prefix/Xvfb/Wine, 이번은 저장 증거 독립 검수다.
- fixture 정정: lap854의 “실제 활성 unit0” 서술은 수용하지 않는다. 성능 창의 state(pid,False)는 unit 상세를 생략하므로 scene_start/end.units=[]가 개체0을 뜻하지 않는다. 상세 scene.state.units는 양쪽558개, player records8개다. 활성8인/G2 부하 증거 아님. 과거 원문을 보존하고 STATUS에 정정했다.
- 후보 DLL SHA: latch=0e53d2b0417babc743b0000856df067a74905eb3fa319e61f91c1330758a864f; gate1=701eaf7e85a3b48757235360d74902351c17f584729e40ac467f3cc9085d5560; gate2=5e3d40fc4723c6be389384b5d58bfce176159ec3d9d3ed94db2506b148497fa6; gate3=2fa9ceb279c89f18449a00d89ea420c72cbad675ffe2135e3cf4df50ffd06cad.
- 실행 명령: .venv/bin/python heredoc로 JSON/SHA/Pillow 독립 집계(기존 validator helper 없이 histogram nearest-rank p95·tick endpoints·부등식 재계산), rg/sed로 latch/probe/validator 열람. 반례 재현에만 validate_trace 호출. view_image로 gate1 원본800×600/후보1600×1200 loaded를 비교: 구도/HUD 위치 육안 일치, 전체 HD coverage·새 입력 실행 PASS 아님. PNG 생성0.
- artifact root: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap855_middle_review/. review.json SHA 598466f9417002d5e29c70638746ed531d03bab9b6608d5909057c6ad82ec80c; identity_and_negative.json SHA 0e4d0960053528b2f7c988c1b9ccda2aadb2081b60bed4fb0ef4717cb0f5df75. pair/raw/capture·source SHA, 수치, synthetic 반례 경로/결과를 보존했다.

## 독립 확인 결과

| run | rate ratio 재계산 | p95 delta | 후보 primary present | 전체 Scale2x present | mask 내부 diff 합 |
|---|---:|---:|---:|---:|---:|
| latch | 0.9999997655 | +5ms | 400 | 1013 | 6951145 |
| gate1 | 0.9999920427 | +5ms | 400 | 1350 | 7291586 |
| gate2 | 0.9999969883 | +5ms | 400 | 1324 | 7274739 |
| gate3 | 1.0000019160 | +5ms | 400 | 1362 | 7335666 |

- 4 pair SHA는 lap854 marker/history MATCH. 양 lane raw/capture·공유 원본 PNG SHA·dimensions/non-black MATCH. scene 상세 state 직접 비교 true, source unchanged/cleanup 기록 true, private game 실제 부재 확인. 과거 prefix 무프로세스 기록을 이번 프로세스 전수 검사로 과장하지 않는다.
- 성능은 실제 sim tick0x8924B8 endpoint 차÷Python monotonic20초 창으로 재계산. histogram count400/drop0/중복 bin0, p95 baseline1ms/candidate6ms. lane별 보존된20개 state samples PS3·camera 일정·tick/monotonic 증가 확인. 모든0.2초 samples 전체는 미보존이므로 전 구간 연속성 독립 재구성 주장은 없다.
- QPC10MHz, first-to-last active present cumulative delta: compose1869281ticks/30822706pixels=6.064623ns/pixel, 20.000376초 창의0.934623%. hash lookup411587ticks/33650calls=1.223141µs/call. lap854의409639ticks/33486calls와 endpoint 선택 수치는 다르나 비용 기준 판정 동일. 첫 present 이전 일을 제외한 차분이다.
- 전체5049 present에서 mismatch_blocks=(nearest_total-nearest_matches)/4, mismatch_blocks≤inside_diff≤4*mismatch_blocks 위반0. mask 밖 diff·palette violation·key miss·invalid·full-frame call·replay mismatch·viewport mutation/restore failure 전부0. OFF gate에는 perf active row가 없어 window400 present는 primary histogram으로 확인.
- latch5개 C 모듈 환경 조회는 initialize_environment 내부에만 있으며 compose는 HD 활성값을 루프 밖에서 읽음. 하네스는 subprocess 시작 전 env 주입, 성능 창은 파일 표식. 실행 중 env 변경 지원 주장은 없다.
- 선택·빈 클릭·drag_exact raw checks true. minimap/production은 UNKNOWN(original parity) 유지. 신규 입력 재실행0, GDI/P4/전체 HD coverage·사용자3단 승인 미충족.

## 필수 validator 구현 누락 — 승격 및 work handoff

- P3c §1.4/§2-B는 부등식을 validator에 추가 검사로 넣도록 명시한다. tools/g1_hd_scale2x_probe.py의 validate_trace에는 denominator 양수·inside 합 양수·outside0만 있고 이 관계 검사가 없다. 게임 출력 회귀가 아닌 필수 검증 구현 누락이다.
- 실제 첫 present의 복사본(deficit17384=mismatch_blocks4346)에 inside1 또는17385를 넣은 synthetic validator-only fixture 모두 현 validator PASS. 원본 raw 무변경, 게임 실행 증거 아님. 각각 synthetic_below_lower_bound.jsonl SHA184533e724f5f818def0417a2363f9c8eefdc40cf99b40921131804f29c831eb, synthetic_above_upper_bound.jsonl SHAc5c1b263f668a69280d8a3a597b977997452de88dd6991c0e48b380a6d10a970.
- 재현: PYTHONPATH=. .venv/bin/python tools/g1_hd_scale2x_probe.py --trace <artifact root>/synthetic_below_lower_bound.jsonl (above도 동일). 현재 PASS, 요구 결과 BLOCKED. exit0 자체를 검증 통과로 쓰지 않는다.
- 판정: PERFORMANCE_EVIDENCE_ACCEPTED / P3 HOLD_REQUIRED_VALIDATOR_GAP / G1 HOLD / P4 금지. raw는 부등식을 만족하므로 성능 FAIL·Scale2x runtime 오류로 왜곡하지 않는다. 일반 middle은 수리/마감 대신 승격 인계 후 종료한다.
- 승격 검수자는 반례2건·필수 검사 계약·source-matched4 raw·fixture 정정을 확인하고 좁은 수리를 work tier에 넘긴다. work 파일은 tools/g1_hd_scale2x_probe.py와 tests/test_g1_hd_scale2x_probe.py만: present별 nearest_matches≤nearest_total 및 deficit/4≤inside≤deficit(정수 교차곱 가능)을 검사, 상/하한 위반·정상 경계 회귀 추가. 임계값/legacy validator/게임 C·EXE/G2/G5/P4/pin/golden/기존 raw 변경 금지.
- work 검증: 반례2건 BLOCKED·정상 fixture PASS·기존4 raw 강화 validator PASS, lint/typecheck→기록 작성→최종 make check 끝까지 기다림. C/build 입력42개 동일하면 source-matched runtime raw 사용 가능, 신규 게임 실행을 불필요하게 요구하지 않는다. 게임/입력 source 변경 시 해당 fresh pair 필요. work는 최종 P3 승인하지 않고 승격 컨펌에 넘긴다. 일반 middle 재요약 회차는 추가하지 않는다.
- Fast/runtime: SKIP_THIS_LAP. 사용자 마감 경계 stop이 PROMPT 일반 Fast 실행보다 우선. doctor/lint/typecheck/targeted/full Fast·game·24k/144k 새로 시작하지 않음. 정확한 logs/gates/lap854-work-fast-r2.log/.exit에서1219 passed·5 skipped·exit0를 읽었으나 이번 문서 fingerprint PASS로 승격하지 않는다. 문서 한도/안전/scoped diff만 확인하고 결과는 STATUS에 보강한다.
- 이전 ESCALATE_SOL25줄·SHA96b53ed20bd84a015982cce9d43b1c38703d4426b18611b909eae906ec407270를 byte-exact archive에 보존. 현재 다음 한 가지는 STATUS만 따른다. 필수 검사3회 반복 실패 없음, stop 사유는 마감 경계다.
