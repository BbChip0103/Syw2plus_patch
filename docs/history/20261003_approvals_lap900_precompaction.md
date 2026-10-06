# APPROVALS — 검수/마일스톤 판정

lap828까지의 직전 전문은 `docs/history/20261001_approvals_lap828_precompaction.md`에 보존했다
(249줄, SHA256 `2e957c42c0057a0236306b6d8224326fda533606dd0c1c2e54ea19da12007e56`).
과거 G5/G2 및 G1 W60 판정 계보는 그 전문과 각 `docs/history/laps/` 기록을 함께 본다.

## 현재 판정

**2026-10-03 사용자 3단 판단: G2·G5 달성·종료.** 직접 플레이 확인에 따른 명시적 종료 승인이다.
기존 기술 검증 한계는 보존하며 G1 제품 승인·STOP 해제는 아니다.
[사용자 원문·검증 한계·문서 커밋/푸시 승인](G2_G5_USER_COMPLETION_20261003.md)

G5 v10은 2026-09-29 18:45 사용자 3단 승인·종료가 적용됐다. G1 제품 마일스톤 확정은 아직 없으며,
**G1 카드2 Stage B 실제 원본/후보 비교 실행만 승인됨**. 목표 문서 반영과 실행 승인은 기능/출시
승인이 아니다. 1단 자동 검사→2단 다음 새 세션 독립 검수→3단 사용자 마일스톤 확인으로 운영한다.

## 미해결·반려·판정 불명 색인

- [ ] **2026-10-02 lap877 일반 middle — P4b B' HOLD·tick-plan 기록/raw 충돌 확인, 승격 유지.** pair/raw·build42+bridge/DLL·원본/fixture SHA MATCH. r1 RIGHT24824 units5/FINAL24860 units3 차이, r2/r3 RIGHT24826/FINAL24862 diff0. 세 pair 간 absolute plan은 다르며 두PASS가 r1 같은tick 반증은 아니다. 완료phase·writer/quiescence 미증명; 게임/하네스 수리는 승격범위 확인 후work에 인계. G1/C/P5/사용자 승인 없음, 구현0·new runtime/full Fast SKIP(사용자충돌stop). 상세 `../history/laps/20261002_lap877_middle_g1_p4b_bprime_tick_plan_conflict_handoff.md`; 기존 ESCALATE_SOL 원문 archive 보존 후 보강.

- [x] **2026-10-02 lap875 일반 middle — lap874 bounded rice/phase diagnostic 2단 수용 / B' HOLD.** r9/r10/r11 raw·build43/DLL·원본/fixture SHA MATCH, target24862 full captured8player/573unit state 동등, writer195/thread1/0x43ED64·phase 밖0 확인. `230207→230607→231007`은 fresh update 중간값으로 phase artifact 설명을 지지하며 과거 read 위치는 미증명. `0x41C961` return/all-stop은 세 진단 snapshot 한정 수용, gdb-free B' 전체 gate·C/P5/G1·사람 승인 아님. 다음 work는 STATUS만 따른다. 상세 `../history/laps/20261002_lap875_middle_g1_p4b_rice_phase_controls_review.md`.

- [ ] **2026-10-02 lap869 일반 middle — P4b B' HOLD·승격:** raw/pair/DLL·원본/fixture·42build MATCH; action 동등/final owner6 rice Δ800 실제 captured 값 차이 확인. equal completed-update phase/atomicity 미증명, 지속 divergence·원인 UNKNOWN. 사용자 충돌 stop, 구현0·full Fast/runtime SKIP; 승격middle 확인→work tick/rice writer·동일 phase 대조 진단. G1/C/P5/사용자 승인 없음. 상세 `../history/laps/20261002_lap869_middle_g1_p4b_same_tick_rice_hold_handoff.md`, `loop/ESCALATE_SOL`.

- [ ] **2026-10-02 lap868 work — P4b same-tick capture PASS / final player-state HOLD·Sol 검수 요청.** 공통 절대 sim tick 입력24694/24790, coherent scene 24730/24826·final24862가 두 lane에 일치했고 snapshot read는1.3~3.2ms. action unit/player record는 일치; final owner6 rice만 baseline230207/candidate231007. 원인 UNKNOWN. raw SHA·전체 player diff를 보존하고 B' PASS 승격 금지. 다음 middle은 차이를 독립 계산해 실제 상태차인지 계측 의미인지 판정한다. 상세 `../history/laps/20261002_lap868_work_g1_p4b_common_tick_observation_hold.md`, `loop/ESCALATE_SOL`.
- [ ] **2026-10-02 lap867 일반 middle — P4b B' HOLD / 동simulation 시점 미증명·승격.**
  r4/r5 raw·42build 원입력·DLL·보호 원본/fixture SHA 일치. r5 RIGHT wait end24692/24710(18tick 차이), 후보-only slot32/33;
  r4 DOWN만 불일치. scene tick 삭제·순차read 종료tick 부재와 lane 로컬+36 결함 확인; 신규unit 직접원인UNKNOWN.
  coverage/Scale2x partial PASS, full Fast/runtime SKIP(사용자 stop), 구현0. 승격middle 확인 후 work probe/tests common-tick/coherence 수리.
  사용자 승인·B' 마감·C/P5 없음. 상세 `../history/laps/20261002_lap867_middle_g1_p4b_scene_time_hold_handoff.md`, `loop/ESCALATE_SOL`.

- [ ] **2026-10-02 lap865 일반 middle — P4b B' HOLD / 입력 직접 원인·키 뒤 scene 충돌 승격.**
  r4 pair/raw/DLL/build42 입력을 재해시 확인, 후보 DOWN/RIGHT30-present coverage365,324/352,704·Scale2x1203 PASS partial 수용.
  receiver-ready ack 누락·receipt를 기다리는 release·keyup 전 camera 사용은 하네스 결함 확정. baseline13칸 직접 원인은
  emission/ready/camera 시간열 부재로 UNKNOWN. 키 뒤 scene은 unit560/563·owner2 cap2100/2300으로 불일치. 고정14표본 지속성 미증명.
  사용자 즉시 승격 지시로 ESCALATE_SOL 보존, work 수리·fresh pair 조건 구체화. focused36·doctor/lint/typecheck PASS,
  full Fast/new runtime SKIP, 게임 구현0·C/P5/G1 승인 없음. 사용자 판정이 아닌 중간 기술 검수다.
  상세 `../history/laps/20261002_lap865_middle_g1_p4b_input_parity_hold_handoff.md`.

- [ ] **2026-10-02 lap863 strategy — G1 W70 P4 `<30%` 승격 판정: 귀속 반증 아님 / P4 `FEASIBLE` 유지 / P4b 캐시 층 카드 / G1 HOLD.**
  lap862 pair·raw·source·기록 SHA와 30 present p50(21.60%/12.70%)을 재계산해 일치 확인. 같은 raw의 키 전 고정 카메라 유효
  coverage는 68.4~70.6%라 blitter 5종 귀속은 유지한다. 스크롤 뒤 결손은 `0x4324E0`이 지형 캐시 `0xBA3D30`을 `memmove` 8곳으로
  밀기 때문이고(한 칸에 blitter 128회뿐, 한 present 뒤 stale 21만), 캐시→화면은 `0x41BF20`의 `0x466280`이 복사한다(보호 원본
  정적 판독). 수리는 캐시 층 미러(층 평면·이동 미러·전사)이며 화면 평면 직접 이동과 전체 재그리기 강제는 기각했다.
  DOWN lane 불일치는 gdb에 묶인 스크롤 하네스 귀속이 유력(가설)하고 lane별 RIGHT fallback은 결함 확정 — gdb 없는 pair로 먼저 잰다.
  PS3 census는 P4b 선행 조건이 아니다. 기준·validator 불변. 이것은 strategy 범위 판정이며 실행 미검증, 2단 검수·3단 사용자
  승인이 아니다. lap860·861 항목의 "정확한 stale writer"는 이 판정으로 귀속했고 입력 원인은 work 측정 대기다.
  상세 `../work/active/G1_STRATEGY_W70_P4B_TERRAIN_CACHE_LAYER_LAP863.md`,
  `../history/laps/20261002_lap863_strategy_g1_w70_p4b_terrain_cache_layer.md`.

- [ ] **2026-10-02 lap861 일반 middle — P4 HOLD·입력 전환 handoff 구체화.**
  lap860 pair/raw/source9 SHA·DOWN 불일치·coverage57,136/47,778.5 독립 재확인. 입력 전 cursor의 barrier 오용은 하네스 결함 확정.
  DOWN 수신/타이밍과 정확한 stale writer는 UNKNOWN; 승격 Sol이 계측 수리 범위를 확인하고 다음 work에 즉시 넘긴다.
  구현0, fresh doctor PASS, full Fast/runtime SKIP(사용자 stop). G1 승인·P5/C gate 없음.
  상세 `../history/laps/20261002_lap861_middle_g1_p4_transition_handoff_hold.md`, `loop/ESCALATE_SOL`.

- [ ] **2026-10-02 lap860 middle — P4 HOLD / DOWN 입력 parity 근거 충돌 승격.**
  baseline DOWN `[158,101]→[159,102]`, candidate 불변을 pair에서 독립 확인. RIGHT raw30 median57,136·다음30 47,778.5,
  키 전 표본창의 첫318,138은 이동 후 회복 증거로 인증 불가. 정확한 stale writer/입력 원인 미확정, C gate·G1 승인 없음.
  `loop/ESCALATE_SOL`에 승격 확인 항목과 work tier handoff 보존. fresh doctor PASS, Fast/runtime SKIP(사용자 stop).
  상세 `../history/laps/20261002_lap860_middle_g1_p4_scroll_input_conflict_escalate.md`.

- [ ] **2026-10-02 lap858 strategy — G1 W70 P3 2단 통합 수용 `PASS(partial)` / P4 `FEASIBLE`(정적) / G1 HOLD.**
  lap855(성능·latch·build 입력·입력·구도)와 lap857(validator 수리) middle 검수의 합이 P3c 카드 §3을 채운다고 판정했다.
  strategy 재계산: pair/raw/source SHA 일치, 반례 2건 `BLOCKED`·raw 4개 `PASS`, 5049 present 위반 0, ratio 0.99999~1.00000,
  p95 +5ms, 입력 3항목 true. 범위는 hook 2종 위의 Scale2x 배관·성능·입력 parity이며 유효 HD coverage는 p50 6.23%다.
  W70 P단계 전환은 마일스톤 경계가 아니고 middle이 직접 판정한다. P4는 지형 blitter 5종 hook 확장으로 다음 work가 구현하며
  coverage p50 <30%면 반증이다. 이것은 strategy 범위 판정이며 P4의 2단 검수·3단 사용자 승인이 아니다. 아래 lap857·855 항목은
  이 판정으로 닫는다. 상세 `../work/active/G1_STRATEGY_W70_P4_TERRAIN_BLITTER_HD_LAP858.md`,
  `../history/laps/20261002_lap858_strategy_g1_w70_p3_accept_p4_terrain_card.md`.

- [x] lap857 validator 수리 확인·P3 경계 승격의 종결 계보 원문은 `../history/20261003_approvals_lap895_precompaction.md`에 byte-exact 보존(전체248줄, SHA·압축 범위는 lap895 기록). lap858 통합 수용으로 종결했으며 새 승인 아님.

- [x] **2026-10-02 lap855 일반 middle — P3c 성능/raw 수용, 필수 validator 누락으로 P3 HOLD·경계 승격.**
  lap854 4 pair 성능·42개 build 입력·DLL·raw/capture 독립 확인. raw 부등식 위반0이나 validator가
  하한/상한을 검사하지 않아 synthetic 위반2건도 PASS. 승격→좁은 work validator 수리 인계,
  P3 마감·P4 전환·G1 사용자 승인 없음. 활성 unit0은 경량 snapshot 생략값으로 정정(상세558 records).
  상세 `../history/laps/20261002_lap855_middle_g1_p3c_validator_gap_escalate.md`, `loop/ESCALATE_SOL`.

- [ ] **2026-10-02 lap853 strategy — G1 W70 P3b 구조 비용 승격 판정: `BLOCKED(structure)` 불수용 / `FEASIBLE` 지속 / G1 HOLD / P4 금지.**
  lap852의 Scale2x validator PASS·full-frame call 0·rate FAIL(ratio 0.5350) raw는 수용한다. 그러나 compose 17.65초는 픽셀
  루프의 `GetEnvironmentVariableA`(쓰인 픽셀당 2~3회, 호출당 ≈1.61µs가 두 실행에서 일치) 구현 결함으로 귀속했고 구조
  재설계는 승인하지 않았다. scale2x 모드 P3 gate는 W70 §2대로 전용 Scale2x validator를 쓰며(legacy nearest-oracle·임계값 수정
  금지, 부등식 추가 검사로 강화), viewport 예외 경로 원복은 gate에서 제외하고 mutation/restore failure 0·crash 0으로 대체한다.
  기준 §3.5는 완화하지 않는다. 다음 work는 P3c 카드. 이것은 strategy 범위 판정이며 2단 middle 수용·3단 사용자 승인이 아니다.
  상세 `../work/active/G1_STRATEGY_W70_P3C_ENV_LATCH_COMPOSE_LAP853.md`,
  `../history/laps/20261002_lap853_strategy_g1_w70_p3_compose_env_lookup_defect.md`.

- [ ] **2026-10-02 lap851 strategy — G1 W70 P3 성능 FAIL 재판정: `FEASIBLE` 지속 / G1 HOLD / P4 금지.**
  lap849 3 pair FAIL(ratio 0.505~0.517)과 lap850 독립 확인을 수용한다. raw 산술 blocks÷refresh≈511k로 지배 비용을
  클립 프리미티브 full-frame 캐시 경로(W70 §0.3 설계 불일치)에 귀속했고, 기준 §3.5는 완화하지 않는다. 다음 work는
  P3b 카드(배타 계측+클립 키 설계 복귀+fresh 3 pair). 이것은 strategy 범위 판정이며 2단 middle 수용·3단 사용자 승인이 아니다.
  상세 `../work/active/G1_STRATEGY_W70_P3B_CLIPPED_KEY_COST_LAP851.md`,
  `../history/laps/20261002_lap851_strategy_g1_w70_p3_continue_bounded_repair.md`.

- [ ] **2026-10-02 lap847 middle — G1 W70 P3 gate HOLD / 성능 raw 충돌로 승격.**
  lap844 perf4/5/6 build 입력39개·원본/fixture/DLL/raw/capture SHA와 Scale2x·구도·입력 partial 근거는 수용한다.
  그러나 trace game_tick 주소0x9B5210은 원본 _imeGetTime 시간값이며 실제 sim tick0x8924B8과 다르다.
  기존 PS3 action snapshot의 실제 tick rate delta는 −38.87/−38.50/−39.71%다(통제된 fixed-window 측정은 아님).
  이전 tick span으로 성능 PASS를 수용할 수 없어 loop/ESCALATE_SOL로 이관한다. P4 전환·G1 마감/승인 없음.
  상세 `../history/laps/20261002_lap847_middle_g1_w70_p3_performance_conflict_escalate.md`.

- [ ] **2026-10-01 lap843 middle — G1 W70 P3 배관 `PASS(partial)` 2단 수용 / P3 gate `HOLD`.**
  lap842 build 입력 39개·DLL/raw/pair SHA와 raw 1288행을 독립 재계산해 230 present, mask 내부
  diff `946079`, 외부 `0`, palette/miss/invalid `0/0/0`, scene/source/cleanup·selection/empty/drag PASS를
  수용했다. 그러나 candidate loaded/menu는 동일한 전체 검정 PNG이므로 pair JSON의 capture
  `PASS`를 visual verdict로 쓸 수 없고, 성능도 1회 candidate-only present 시간이다. 다음 work는
  valid post-present paired capture + 3회 fresh baseline 대비 tick/p95 + minimap gate parity를 완주한다.
  상세 `../history/laps/20261001_lap843_middle_g1_w70_p3_scale2x_review_hold.md`.

- [ ] **2026-10-01 lap842 work — G1 W70 P3 Scale2x `PASS(partial)` / middle 검수 대기.** P2 key-bound
  원천 frame cache에서 palette-index Scale2x를 생성하고 compositor 2x2 four-way write를 수리했다.
  save006 fresh pair candidate 230 present에서 mask 내부 diff `946079`, 외부 `0`, palette 위반 `0`,
  key miss/invalid `0/0`, scene/source/cleanup PASS를 기록했다. selection/empty/drag parity PASS,
  minimap/production HOLD이며 baseline 성능·visual verdict·전체 coverage·GDI/P4와 사용자 승인은 미충족.
  상세 `../history/laps/20261001_lap842_work_g1_w70_p3_scale2x.md`; 다음 새 middle 독립 검수.

- [ ] **2026-10-01 lap841 middle — G1 W70 P2 `PASS(partial)` / G1 HOLD.** lap840 artifact/current
  source 전 입력과 candidate DLL manifest SHA를 대조하고 raw 2241행을 독립 재집계했다. shared exact
  full-key search를 begin/negative probe가 함께 쓰며 NULL-frame 강제는 없다. normal miss0, altered
  attempt/miss/mismatch `58867/58867/58867`, nearest1.0, invalid/drop0, scene/source/cleanup 및 관련
  pytest20·validator·doctor/lint/typecheck PASS로 P2를 2단 수용한다. P3 Scale2x/GDI/전체 HD coverage와
  G1 사용자 3단 승인은 미충족이다. 상세
  `../history/laps/20261001_lap841_middle_g1_w70_p2_fullkey_review_pass.md`.

- [x] **2026-10-01 lap839 middle — G1 W70 P2 gate `HOLD`(lap840/841로 해소).** lap838 source snapshot,
  raw/pair/DLL SHA와 2363행을 재검산해 normal miss0, refresh2735, nearest1.0, invalid/drop0,
  scene/source/cleanup은 수용했다. 그러나 negative probe는 altered writer를 table에서 찾지 않고
  `identity_frame=NULL`인 임시 key를 block reader에 넘겨 실패를 강제하며, reader는 writer를 읽지 않는다.
  따라서 negative miss/mismatch 64810/64810은 actual full-key rejection 증거가 아니다. begin과 probe가
  full-key search helper를 공유하고 fresh pair를 남기기 전 P3 금지였으며 lap840 work와 lap841 middle이 충족했다. 상세
  `../history/laps/20261001_lap839_middle_g1_w70_p2_negative_lookup_review_hold.md`.

- [ ] **2026-10-01 lap837 middle — G1 W70 P2 gate `HOLD`(work 수리 필요).** lap836 pair/raw/DLL
  SHA와 drop0·scene/source/cleanup은 수용했지만, mismatch `66824` 중 synthetic negative 증가
  `64374`를 제외한 실제 cached-frame 내용 충돌이 2450회다. negative helper는 altered key lookup을
  시도하지 않고 counter만 올리며, bind 충돌 뒤 current key를 무효화하지 않아 stale cached frame을
  합성한다. legacy mirror validator도 exact same-frame oracle 0인 present 1138개를 `BLOCKED`로
  잡았다. real mismatch 0·실제 negative fail-closed fresh pair 전 P3 금지. 상세
  `../history/laps/20261001_lap837_middle_g1_w70_p2_keycache_review_hold.md`.

- [ ] **2026-10-01 lap835 middle — G1 W70 P2 gate `HOLD`(work 수리 필요).** lap834의 artifact
  SHA, identity 962/962·nearest 1.0, `176/47004/182643`, block read `25559164/0`, camera
  `[158,101]→[159,102]`, changed-input stale `+4032`, scene/source/cleanup은 독립 재계산과 일치한다.
  그러나 모든 key가 동일한 재사용 `scratch_a`를 current call마다 다시 bind하며, source/digest key가 frame
  값을 선택하지 않는다. hit/miss도 key cache가 아니라 강제 bind 뒤 픽셀 read 카운터다. trace summary도
  failed·drop304인데 validator가 PASS했다. 실제 keyed owned frame/cache + negative mismatch + drop0 fresh pair
  전 P3 금지. 상세 `../history/laps/20261001_lap835_middle_g1_w70_p2_keybound_review_hold.md`.

- [ ] **2026-10-01 lap833 middle — G1 W70 P2 gate `HOLD`(수리 범위 명확).** final-source raw의
  651/651 identity present, nearest min 1.0, ledger `189/25839/182244`, invalid 0, core-state
  parity, source/cleanup은 독립 재계산 PASS다. 그러나 현 구현은 `g1_hd_asset_begin()`
  반환을 버리고 기존 sentinel pixel을 key와 무관하게 mirror에 쓰므로 key-bound asset
  치환을 증명하지 못했다. 실제 camera scroll도 0회여서 stale 750265는 scroll 전후
  지표가 아니다. work가 key lookup을 실제 2x block 공급 경로로 연결하고 camera가
  변하는 fresh pair를 남기기 전 P3 확장 금지. 상세 `../history/laps/
  20261001_lap833_middle_g1_w70_p2_identity_review_hold.md`.

- [x] **2026-10-01 lap832 work — G1 W70 P2 identity asset mapping `PASS(partial)` 검수 완료.** 새
  `SYW2_G1_HD_SOURCE=identity` ledger가 원본 primitive source를 writer·pointer·크기·digest
  key로 묶고, 같은 프레임 nearest oracle을 candidate raw에 남겼다. save006 fresh pair에서
  candidate mirror 684건, nearest 최저 1.0, key 188개, event 25,442건, identity pixel
  182,650/480,000, invalid 0, stale 누적 775,141, scene parity/source unchanged/cleanup
  PASS를 확인했다. Minimap/production은 양쪽 UNKNOWN이며 cross-process screenshot ratio
  0.939704는 same-frame oracle이 아니다. P3 Scale2x·GDI·전체 HD coverage와 G1 승인은 없다.
  상세 `../history/laps/20261001_lap832_work_g1_w70_p2_identity_asset_mapping.md`. lap833이 raw
  수치는 수용했으나 key-bound output·scroll stale 미증명으로 P2 gate는 HOLD했다.

- [ ] **2026-10-01 lap831 middle — G1 W70 P1 asset-key `PASS(partial)` / G1 HOLD.** lap830의
  writer/census/probe raw SHA와 protected-original disassembly를 독립 재검수했다. key 256·blit
  1061의 table 산식 위반 0, equality false/unknown 0, digest 변형 0, asset event 전부 PS3·renderer
  `0xBA3D30/832/600`, fixed-buffer write 3/3을 재현했다. lap830 기록의 probe SHA는 raw 재계산으로
  단순 전사 오류를 정정했다. `RIGHT` camera no-change와 missing `writer-summary.json`은 명시한
  한계이며 핵심 mapping을 반증하지 않는다. 다음 work는 P2 identity asset mapping이고, G1 제품
  승인·W70/Scale2x/GDI 완료는 아니다. 상세
  `../history/laps/20261001_lap831_middle_g1_w70_p1_asset_key_review_pass.md`.
- [ ] **2026-10-01 lap829 middle — G1 W70 P1 asset-key `FEASIBLE` / G1 HOLD.** lap828 raw SHA와
  entry181/watch1/write3을 독립 재계산했고, 원본 `0x435400`의 arg1/arg2가 `(tile file,frame)`이며
  `0x435593` source가 `base[file*0x2FE]+offset[file*0x2FE+frame]`임을 확인했다. 다음 work는 제품
  구현 없이 이 equality를 fresh runtime raw로 증명한다. 통과 전 W70/Scale2x/GDI 구현과 G1 PASS 금지.
  상세 `../history/laps/20261001_lap829_middle_g1_w70_p1_asset_key_feasibility.md`.
- [ ] **G1 W70 P1 현재 경계:** lap828 work가 fixed terrain buffer writer를
  `0x468C93/0x468C9C`까지 실측했으나 stable asset/tile/resource key를 찾지 못해
  `BLOCKED/strategy`로 승격했다. 이 승격은 위 lap829가 `FEASIBLE`로 해소했으며, 남은 것은 exact
  runtime key trace다. 상세 `../history/laps/20261001_lap828_work_g1_w70_p1_fixed_terrain_writer.md`.
- [ ] lap827 middle은 lap826의 `0x403B20→0x403C10` terrain 분기를 object string-copy로 반증하고
  기존 fixed buffer/cache/composite route만 유지했다. census SHA 전사 오류는 raw 재계산으로 정정됐다.
  상세 `../history/laps/20261001_lap827_middle_g1_w70_p1_terrain_route_review.md`.
- [ ] lap815까지의 W60 production/input HOLD 계보는 lap816의 `UNKNOWN(original parity)`와
  lap817~818 primitive measurement 독립검수로 정리됐다. current blocker가 아니며 전문은 위 archive 참조.
- [!] 기존 QHD 시야 확장 후보는 G1 요구 미충족이다. 1600×1200 동일 구도와 HD detail 보존 경로로
  다시 판정해야 한다(`../history/20260910_VISUAL_GOAL_CORRECTION.md`).

## 사용자 결정 — 현재 유지

- [ ] **2026-09-30 22:2x G1 범위:** nearest 2배만으로 완료하지 않는다. 지형·타일·HUD 등 화면
  전체 경로가 1600×1200에서 2배 해상도 그림을 보존해야 한다. 기본 HD 출처는 원본 frame 단위
  deterministic palette-index Scale2x, 대안은 사용자 HD asset 슬롯이다. 원본 파일은 읽기 전용이다.
- [x] **2026-09-30 G2 ESL2608 점검 우선 지시:** lap806 보고서로 종료했고 제품 결함 미발견,
  EXE 재생성 없음, DxWnd 안내만 남겼다. 현재 G1을 재개했다.
- [x] **2026-09-29 18:45 G5 v10 승인·종료:** 후보 SHA
  `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`.
  수용 제한은 멀티 `BLOCKED(env)`, 미니맵 정상 UI 경로 미증명, 체력바 조건부, N/A·edge다.
- [x] **2026-09-27:** G2 전비10000 트랙 종료, 전비5000 단계 달성 유지. G4는 보류, G3는 중단.

## 실행 승인 (사람 판정)

- 2026-09-12 01:03 사용자는 G1 카드2 Stage B의 격리된 원본/1600×1200 비교를 bounded repair와
  fresh validation으로 계속하도록 승인했다. 원본/참고 저장소 쓰기·제품 G1 합격·출시·다른 목표
  재개·커밋/푸시는 승인 범위가 아니다.
- 2026-09-23 사용자는 G2에서 라이브 `used≤5000`이면 일시 `used+reserved` 초과 표시를 허용하고
  32-bit 전비 장부를 채택했다. 이것은 G2 제품 합격/마일스톤 승인이 아니다.

## 반려

QHD 해석 반려는 최신 1600×1200/HD-detail 목표에 반영했다. 새로운 사람 반려는 없다.

## 제출 양식

마일스톤/목표, 후보SHA, 기준·후보 캡처, 실제 입력·부하조건, 1단 결과, 2단 판정자와 실제 모델,
허용 오차, 남은 위험, 사용자 판정을 기록한다. PNG는 공유 temp에 두고 해시/경로를 남긴다.

- [ ] **2026-10-02 lap848 일반 middle:** lap847 counter/성능 raw 충돌 독립 확인·HOLD 유지.
  ESCALATE_SOL에 승격 검증 항목과 work 계측 수리안을 보존했다. 계획 승인·P4 전환·G1 마감 없음.
  상세 `docs/history/laps/20261002_lap848_middle_g1_p3_conflict_confirmation_handoff.md`. 사용자 stop 조건으로 fresh Fast/runtime SKIP.

- [ ] **2026-10-02 lap879 middle 기술검수(사용자 승인 아님):** raw24788 phase0·host stale pause 재사용 및 unmatched 판정 결함을 offline 재현, B'/G1 HOLD. 승격 검수 후 관측 probe/tests 수리안을 work에 이관, 추가runtime 금지. 제품/단계/마일스톤 승인 없음. 상세 `../history/laps/20261002_lap879_middle_g1_p4b_scroll_pause_race_handoff.md`.

- [ ] **2026-10-02 lap881 middle 기술검수(사람 승인 아님):** lap880 captured state/phase/ack 재계산 일치이나 baselineA/B 수용 전 candidate 실행이 승격 조건과 충돌. 실제 main AST의 INVALID phase/state mismatch2반례에서 candidate 호출 확인, bounded 독립수용 거부·B'/G1 HOLD·ESCALATE_SOL. 승격 확인→관측 probe/tests 수리를 work에 이관. 추가runtime/full Fast SKIP(사용자충돌stop), 단계/제품 승인 없음. 상세 `../history/laps/20261002_lap881_middle_g1_p4b_control_acceptance_order_hold.md`.

- [ ] **2026-10-02 lap883 middle 기술검수(사람 승인 아님):** lap882 사전 control 기록 순서는 수리됨, 그러나 pause/phase identity·census inferior·bridge SHA·release nonce 누락으로 synthetic5/historical3 불일치 반례 모두 control PASS/candidate stub1. 역사raw 재계산도 call mismatch PASS. bounded수용 거부·B'/G1 HOLD·ESCALATE_SOL, 승격 확인→두 파일 관측 수리 work 이관. focused88/doctor/lint/typecheck PASS, fullFast/runtime SKIP(사용자충돌stop), 제품/마일스톤승인 없음. 상세 `../history/laps/20261002_lap883_middle_g1_p4b_control_identity_hold.md`.

- [ ] **2026-10-02 lap885 middle 기술검수(사람 승인 아님):** lap884 completed-phase/pause·nonce/hash 수리 확인·focused115 PASS. 단 historical baselineB raw seq2 삭제(gap) 및 seq15 no-update return PTID substitution 각각 parser/live check/control PASS·candidate stub1회로 Astra normative gate 충돌. **HOLD_RAW_IDENTITY_CLOSURE·bounded/B'/G1 HOLD·ESCALATE_SOL**. 추가runtime/fullFast SKIP(사용자conflict-stop), 승격 작업자가 반례 확인 및 소비된1work 예산의 continue/stop을 명시한 뒤 조건부 두 파일 work 수리handoff. source/tests/원본/save/기존raw 불변, 제품/마일스톤승인 없음. 상세 `../history/laps/20261002_lap885_middle_g1_p4b_raw_identity_closure_hold.md`.

- [x] **2026-10-02 lap887 middle 두 결함 한정 기술검수(사람/제품 승인 아님):** lap886 raw seq gap 및 no-update return PTID 수리 `PASS_SCOPED_OFFLINE_REPAIR`. 정상 historical3lane 수용, 양 baseline 변이4건 durable HOLD/candidate0, 실제 host AST prefix 변이20건 snapshot/input0·정상10건 정상 입력 경로 확인(mock). focused123/doctor/lint/typecheck PASS, 마지막 full Fast 대기. 기존 lap885 marker byte-exact archive 후 해소; 사용자 한정승인 소진·STOP, bounded/B'/G1 HOLD. 추가 runtime/제품 허가 없음. 상세 `../history/laps/20261002_lap887_middle_g1_p4b_two_raw_defects_review_pass.md`.

- [x] **2026-10-03 lap889 middle 기술검수(사용자/제품 승인 아님):** 완료된 lap888 GDB scroll phase triplet raw·동일 완료phase/census/nonce·5checkpoint full state/input parity·사전baseline barrier·source/build42/DLL/cleanup 독립 확인, **PASS_BOUNDED_SCROLL_DIAGNOSTIC_INDEPENDENT**. candidate input hash는316행prefix MATCH·후행cursor3행 한계 설명. B'/G1 HOLD·다음 work gdb-free B' 실제 전체gate, C/D/P5 순서 불변. 구현/새runtime/commit0, ESCALATE조건 없음. 상세 `../history/laps/20261003_lap889_middle_g1_p4b_scroll_phase_review_pass.md`.

- [ ] **2026-10-03 lap891 middle 기술검수(사용자/제품 승인 아님):** lap890 final24861 player2명/unit1개 차이 독립 확인, 완료phase 미증명·과거PASS와 schedule 상이. `HOLD_PHASE_ATTRIBUTION_UNPROVEN`·B'/G1 HOLD·ESCALATE_SOL; 승격 작업자가 동일 lap890 schedule 관측 진단 범위 확인→work 최소 하네스 handoff. 기존r1/validator/임계값 보존, 구현/runtime0·fullFast SKIP(사용자 근거불명 stop), current fullFast 미검증. 상세 `../history/laps/20261003_lap891_middle_g1_p4b_bprime_phase_attribution_hold.md`.

- [ ] **2026-10-03 lap892 strategy 범위 판정(사용자/제품 승인 아님):** lap890 candidate final snapshot은 찢어진 live 읽기로 확정
  (owner2 count95/유닛96, 완료-phase 22개 위반0). lap890 pair HOLD 유지, 시뮬레이션 발산 증거로는 불사용. lap891 제안(GDB 일정 진단) 불채택,
  다음 work=P4b-S in-process 완료-phase snapshot·fresh pair 연속 2회. 기준·validator·임계값·비교 필드 불변, B'/G1 HOLD·C/D/P5 전환 없음.
  실행 미검증. 상세 `../work/active/G1_STRATEGY_W70_P4B_S_INPROCESS_SNAPSHOT_LAP892.md`,
  `../history/laps/20261003_lap892_strategy_g1_p4b_torn_live_read_inprocess_snapshot.md`.

- [ ] **2026-10-03 lap895 middle 기술검수(사용자/제품 승인 아님):** pair3/4 raw20 snapshot·기준/양lane 상태·coverage/Scale2x 독립 재계산 수용. 그러나 build44개 중 `direct_draw_trace.c`만 현재와 불일치(원본검사/설치 순서 변경), 추가 test focused127→128. **HOLD_RUNTIME_SOURCE_IDENTITY·B'/G1 HOLD·ESCALATE_SOL**; 승격 확인→current-source build/연속2 pair work 인계. 구현/새runtime/fullFast0(SKIP 사용자충돌stop), doctor/focused128/lint/typecheck PASS. 상세 `../history/laps/20261003_lap895_middle_g1_p4bs_runtime_source_identity_hold.md`.

- [x] **2026-10-03 lap897 middle 기술검수(사용자/제품 승인 아님):** lap896 current-source pair1/2 build44×2 MATCH·binary20/E1~E4·coverage/Scale2x/input/cleanup 독립 재계산 PASS. **B' `PASS(partial)`**, lap895 source HOLD 해소; G1 HOLD·다음 C 계측OFF fresh3 work. 구현/새runtime/commit0·승격조건 없음.
  상세 `../history/laps/20261003_lap897_middle_g1_p4bs_current_source_review_pass.md`. C/D-1/P5·전체 HD/사용자 마일스톤은 미검증; 최종 Fast 결과는 STATUS.
