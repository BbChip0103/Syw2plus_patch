# APPROVALS — 검수/마일스톤 판정

lap828까지의 직전 전문은 `docs/history/20261001_approvals_lap828_precompaction.md`에 보존했다
(249줄, SHA256 `2e957c42c0057a0236306b6d8224326fda533606dd0c1c2e54ea19da12007e56`).
과거 G5/G2 및 G1 W60 판정 계보는 그 전문과 각 `docs/history/laps/` 기록을 함께 본다.

## 현재 판정

lap940 middle: lap939 source/build48/raw·PNG 독립 `PASS(partial input binding)`. release45→fresh1162/1166·선택/캡처일치·V1/V2/s/q 수용, baseline PASS_WITH_LIMITS·minimap/production UNKNOWN·G1 HOLD 유지. 제품/사용자/마일스톤 승인 없음. 상세 `../history/laps/20261004_lap940_middle_g1_input_release_binding_review_partial.md`, 현재큐는 STATUS만.

lap938 strategy: lap937 HOLD 확인 — lap936 r3의 seq1052/1056은 게임 `WM_LBUTTONUP` 수신보다 88·39ms 앞(반증), r3 capture binding 불수용. 선택 의미(151·빈0·drag4)와 lap934 P5-T-V/B′2/C3 부분수용은 유지. 입력 캡처·G1 HOLD, G1/사용자/마일스톤 승인 없음. 상세 `../work/active/G1_STRATEGY_W70_INPUT_RELEASE_BOUNDARY_LAP938.md`, 현재큐는 STATUS만.

**2026-10-03 사용자 3단 판단: G2·G5 달성·종료.** 직접 플레이 확인에 따른 명시적 종료 승인이다.
기존 기술 검증 한계는 보존하며 G1 제품 승인·STOP 해제는 아니다.
[사용자 원문·검증 한계·문서 커밋/푸시 승인](G2_G5_USER_COMPLETION_20261003.md)

G5 v10은 2026-09-29 18:45 사용자 3단 승인·종료가 적용됐다. G1 제품 마일스톤 확정은 아직 없으며,
**G1 카드2 Stage B 실제 원본/후보 비교 실행만 승인됨**. 목표 문서 반영과 실행 승인은 기능/출시
승인이 아니다. 1단 자동 검사→2단 다음 새 세션 독립 검수→3단 사용자 마일스톤 확인으로 운영한다.

## 미해결·반려·판정 불명 색인

- [x] lap865·867·868·869·875·877(P4b B′ 같은-tick/phase HOLD 계보, lap892 P4b-S 판정과 lap896·897 current-source pair 수용으로 해소) 원문은
  `../history/20261004_approvals_lap925_precompaction.md`에 byte-exact 보존(전체250줄, SHA256 `f50876a6e0289f105bee5be314a4b8a7c2ebcd9e86812bff8f77d8aef3b386ec`).
  종결 계보이며 새 판정 아님. 각 lap 기록은 `../history/laps/20261002_lap8{65,67,68,69,75,77}_*.md`.

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

- [x] lap861·lap860(P4 HOLD·DOWN 입력 parity 승격 2건, lap863 strategy 판정과 이후 P4b~P4c-W current-source pair 수용으로 해소) 원문은
  `../history/20261004_approvals_lap938_precompaction.md`에 byte-exact 보존(전체249줄, SHA256 `7b20a743485a9b60269da8fb3d0d2090350c86116e12325b15df0779c3a91af5`).
  종결 계보이며 새 판정 아님. 각 lap 기록은 `../history/laps/20261002_lap86{0,1}_*.md`.

- [ ] **2026-10-02 lap858 strategy — G1 W70 P3 2단 통합 수용 `PASS(partial)` / P4 `FEASIBLE`(정적) / G1 HOLD.**
  lap855(성능·latch·build 입력·입력·구도)와 lap857(validator 수리) middle 검수의 합이 P3c 카드 §3을 채운다고 판정했다.
  strategy 재계산: pair/raw/source SHA 일치, 반례 2건 `BLOCKED`·raw 4개 `PASS`, 5049 present 위반 0, ratio 0.99999~1.00000,
  p95 +5ms, 입력 3항목 true. 범위는 hook 2종 위의 Scale2x 배관·성능·입력 parity이며 유효 HD coverage는 p50 6.23%다.
  W70 P단계 전환은 마일스톤 경계가 아니고 middle이 직접 판정한다. P4는 지형 blitter 5종 hook 확장으로 다음 work가 구현하며
  coverage p50 <30%면 반증이다. 이것은 strategy 범위 판정이며 P4의 2단 검수·3단 사용자 승인이 아니다. 아래 lap857·855 항목은
  이 판정으로 닫는다. 상세 `../work/active/G1_STRATEGY_W70_P4_TERRAIN_BLITTER_HD_LAP858.md`,
  `../history/laps/20261002_lap858_strategy_g1_w70_p3_accept_p4_terrain_card.md`.

- [x] lap857 validator 수리 확인·P3 경계 승격의 종결 계보 원문은 `../history/20261003_approvals_lap895_precompaction.md`에 byte-exact 보존(전체248줄, SHA·압축 범위는 lap895 기록). lap858 통합 수용으로 종결했으며 새 승인 아님.
- [x] lap855(P3c validator 누락 HOLD)·lap839(P2 negative lookup HOLD, lap840/841로 해소)·lap832(P2 identity 검수 완료) 체크 완료 항목 원문은
  `../history/20261003_approvals_lap900_precompaction.md`에 byte-exact 보존(전체250줄, SHA256
  `8f71aaf8c83a595e50fcfd949726eec5919de4672f9525257f91ee2a7b58e421`). 종결 계보이며 새 승인 아님.

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

- [x] lap847·lap848(P3 gate HOLD·성능 raw 충돌 승격 2건, 위 lap851·853·858 strategy 판정으로 해소) 원문은 `../history/20261004_approvals_lap938_precompaction.md`에
  byte-exact 보존(전체249줄, SHA256 `7b20a743485a9b60269da8fb3d0d2090350c86116e12325b15df0779c3a91af5`). 종결 계보이며 새 판정 아님.

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

- [x] lap837·lap835·lap833(P2 gate HOLD 3건, lap840 수리와 위 lap841 `PASS(partial)`로 해소) 원문은
  `../history/20261003_approvals_lap911_precompaction.md`에 byte-exact 보존(전체250줄, SHA256
  `74589f54175c57e539e198a60cc7b5f4206744abb5958c3923d5a1671551d931`). 종결 계보이며 새 승인 아님.

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

- [ ] **2026-10-02 lap879 middle 기술검수(사용자 승인 아님):** raw24788 phase0·host stale pause 재사용 및 unmatched 판정 결함을 offline 재현, B'/G1 HOLD. 승격 검수 후 관측 probe/tests 수리안을 work에 이관, 추가runtime 금지. 제품/단계/마일스톤 승인 없음. 상세 `../history/laps/20261002_lap879_middle_g1_p4b_scroll_pause_race_handoff.md`.

- [ ] **2026-10-02 lap881 middle 기술검수(사람 승인 아님):** lap880 captured state/phase/ack 재계산 일치이나 baselineA/B 수용 전 candidate 실행이 승격 조건과 충돌. 실제 main AST의 INVALID phase/state mismatch2반례에서 candidate 호출 확인, bounded 독립수용 거부·B'/G1 HOLD·ESCALATE_SOL. 승격 확인→관측 probe/tests 수리를 work에 이관. 추가runtime/full Fast SKIP(사용자충돌stop), 단계/제품 승인 없음. 상세 `../history/laps/20261002_lap881_middle_g1_p4b_control_acceptance_order_hold.md`.

- [ ] **2026-10-02 lap883 middle 기술검수(사람 승인 아님):** lap882 사전 control 기록 순서는 수리됨, 그러나 pause/phase identity·census inferior·bridge SHA·release nonce 누락으로 synthetic5/historical3 불일치 반례 모두 control PASS/candidate stub1. 역사raw 재계산도 call mismatch PASS. bounded수용 거부·B'/G1 HOLD·ESCALATE_SOL, 승격 확인→두 파일 관측 수리 work 이관. focused88/doctor/lint/typecheck PASS, fullFast/runtime SKIP(사용자충돌stop), 제품/마일스톤승인 없음. 상세 `../history/laps/20261002_lap883_middle_g1_p4b_control_identity_hold.md`.

- [ ] **2026-10-02 lap885 middle 기술검수(사람 승인 아님):** lap884 completed-phase/pause·nonce/hash 수리 확인·focused115 PASS. 단 historical baselineB raw seq2 삭제(gap) 및 seq15 no-update return PTID substitution 각각 parser/live check/control PASS·candidate stub1회로 Astra normative gate 충돌. **HOLD_RAW_IDENTITY_CLOSURE·bounded/B'/G1 HOLD·ESCALATE_SOL**. 추가runtime/fullFast SKIP(사용자conflict-stop), 승격 작업자가 반례 확인 및 소비된1work 예산의 continue/stop을 명시한 뒤 조건부 두 파일 work 수리handoff. source/tests/원본/save/기존raw 불변, 제품/마일스톤승인 없음. 상세 `../history/laps/20261002_lap885_middle_g1_p4b_raw_identity_closure_hold.md`.

- [ ] **2026-10-03 lap891 middle 기술검수(사용자/제품 승인 아님):** lap890 final24861 player2명/unit1개 차이 독립 확인, 완료phase 미증명·과거PASS와 schedule 상이. `HOLD_PHASE_ATTRIBUTION_UNPROVEN`·B'/G1 HOLD·ESCALATE_SOL; 승격 작업자가 동일 lap890 schedule 관측 진단 범위 확인→work 최소 하네스 handoff. 기존r1/validator/임계값 보존, 구현/runtime0·fullFast SKIP(사용자 근거불명 stop), current fullFast 미검증. 상세 `../history/laps/20261003_lap891_middle_g1_p4b_bprime_phase_attribution_hold.md`.

- [ ] **2026-10-03 lap892 strategy 범위 판정(사용자/제품 승인 아님):** lap890 candidate final snapshot은 찢어진 live 읽기로 확정
  (owner2 count95/유닛96, 완료-phase 22개 위반0). lap890 pair HOLD 유지, 시뮬레이션 발산 증거로는 불사용. lap891 제안(GDB 일정 진단) 불채택,
  다음 work=P4b-S in-process 완료-phase snapshot·fresh pair 연속 2회. 기준·validator·임계값·비교 필드 불변, B'/G1 HOLD·C/D/P5 전환 없음.
  실행 미검증. 상세 `../work/active/G1_STRATEGY_W70_P4B_S_INPROCESS_SNAPSHOT_LAP892.md`,
  `../history/laps/20261003_lap892_strategy_g1_p4b_torn_live_read_inprocess_snapshot.md`.

- [ ] **2026-10-03 lap895 middle 기술검수(사용자/제품 승인 아님):** pair3/4 raw20 snapshot·기준/양lane 상태·coverage/Scale2x 독립 재계산 수용. 그러나 build44개 중 `direct_draw_trace.c`만 현재와 불일치(원본검사/설치 순서 변경), 추가 test focused127→128. **HOLD_RUNTIME_SOURCE_IDENTITY·B'/G1 HOLD·ESCALATE_SOL**; 승격 확인→current-source build/연속2 pair work 인계. 구현/새runtime/fullFast0(SKIP 사용자충돌stop), doctor/focused128/lint/typecheck PASS. 상세 `../history/laps/20261003_lap895_middle_g1_p4bs_runtime_source_identity_hold.md`.

- [ ] **2026-10-03 lap900 strategy 범위 판정(사용자/제품 승인 아님):** lap899 시각 HOLD의 귀속을 **렌더러(HD compose)**로 확정.
  후보 `loaded.png` 93개 중 P4 첫 실행(lap858)부터 44개 전부 월드 검정 19만대(이전 40개는 9천대), 프로세스 안 동일 프레임 수치로
  P4 이후 PS3 present 전부가 정확식 `inside_diff ≤ 2×(covered−stale)` 위반(P3·P3c는 위반0). Scale2x validator에 안쪽 상한이 없어 놓쳤다.
  P4·P4b는 `HOLD(화면 정합)`로 환원, lap898 C 수용 없음, lap897 B'의 상태·입력 parity만 유지. 화면 정합 gate V1·V2·V3 추가(강화).
  다음 work=P4c(지형 비클립 writer identity frame 바인딩 수리 → B' 2 pair·C 3 pair 재측정). 원인 후보는 실행 미검증. 기준 완화0.
  상세 `../work/active/G1_STRATEGY_W70_P4C_TERRAIN_BIND_VISUAL_GATE_LAP900.md`,
  `../history/laps/20261003_lap900_strategy_g1_p4_terrain_bind_defect_visual_gate.md`.

- [ ] **2026-10-03 lap902 middle 기술검수(사용자/제품 승인 아님):** lap901 V1 1085/696/705present 위반0·origin V2 4FAIL/1PASS·PNG10장 V3 HOLD. 후보 thin tile-grid 및 static ROI1367black 잔차3pair동일 확인. 미기록0/write-mask누락 경로 유력·actual같은call귀속UNKNOWN, `HOLD_SEAM_ATTRIBUTION_UNPROVEN`·ESCALATE. 기준불변·B'/C/G1승인0. 승격확인→work tile/mask귀속 후 최소수리 handoff. doctor/lint/typecheck·focused155PASS; fullFast/runtimeSKIP(사용자근거불명stop). 상세 `../history/laps/20261003_lap902_middle_g1_p4c_v2_seam_attribution_hold.md`.

- [ ] **2026-10-03 lap903 strategy 범위 판정(사용자/제품 승인 아님):** lap902 격자 HOLD의 귀속을 **렌더러(write mask 누락 → Scale2x)**로 확정.
  P4c 15쌍 단일 검정 블록 18,882~20,056·타일 변 예측 축 점유율 0.956~0.974, 지형 미러 이전 15쌍 476~614·0.07~0.16. 고친 빌드는 미실행.
  수리 범위 M1~M5(비클립·클립 두 경로)와 V2s(≤2000) 추가, V1·V2·V3·기준 완화0. P4c·P4b는 `HOLD(화면 정합)` 유지, B'/C/G1 승인0.
  상세 `../work/active/G1_STRATEGY_W70_P4C_M_WRITE_MASK_SEAM_LAP903.md`,
  `../history/laps/20261003_lap903_strategy_g1_p4c_write_mask_seam_attribution.md`.

- [x] lap887(두 raw 결함 한정 offline 수리 PASS)·lap889(GDB scroll phase 진단 독립 PASS)·lap897(B' `PASS(partial)`) 체크 완료 항목 원문은
  `../history/20261003_approvals_lap906_precompaction.md`에 byte-exact 보존(전체245줄, SHA256
  `7eb1be76a4131f50c546c6f663c93de2d07deaf92c1257a16eae36c924cd8ecd`). 종결 계보이며 새 승인 아님.

- [ ] **2026-10-03 lap906 strategy 범위 판정(사용자/제품 승인 아님):** lap905 B′ 화면 HOLD의 귀속을 **렌더러(캐시 scratch clear 폭 800/832)**로 확정.
  네-검정 블록이 RIGHT 뒤 8장에서만 화면 x736..767에 2164~2370개(가로 이동 없는 22장은 0), `y mod 32 ∈ [16,31]`·기울기 2:1 쐐기. 고친 빌드는 미실행.
  수리 W1(clear와 compose가 같은 프레임 폭)과 V2q(네-검정 블록 ≤2000) 추가, V1·V2·V2s·V3·기준 완화0. lap904 B′1·B′2 HOLD 유지, B'/C/G1 승인0.
  상세 `../work/active/G1_STRATEGY_W70_P4C_W_CACHE_SCRATCH_WIDTH_LAP906.md`,
  `../history/laps/20261003_lap906_strategy_g1_p4c_cache_scratch_width_attribution.md`.

- [ ] **2026-10-03 lap908 middle 기술검수(사용자/제품 승인 아님):** lap907 build45×5/current source·snapshot20·V1 5623위반0·25tag V2/V2s/V2q·B′2/C3/V3 독립 PASS(partial), G1 HOLD. ROI144/136 관찰구간·입력UNKNOWN 유지, 다음work D-1. 실제 model/effort 미노출을 기록, 게임/runtime/commit0·ESCALATE조건없음. 상세 `../history/laps/20261003_lap908_middle_g1_p4cw_visual_raw_review_pass.md`; 마지막 fresh Fast 결과는 STATUS.

- [ ] **2026-10-03 lap910 middle 기술검수(사용자/제품 승인 아님):** lap909 build46/current source·raw/map SHA·64 header/payload 산술 MATCH. 그러나 맵은 PS9-associated `0x0236BEA0`/stride800을 누적면적으로 고른 것이고 actual present source(폭832)와 결합이 없다. `selected_buffer` 변이 사본도 gate PASS. `HOLD_PRESENT_BUFFER_IDENTITY`·ESCALATE, D-1/G1 HOLD. 상세 `../history/laps/20261003_lap910_middle_g1_d1_present_buffer_identity_hold.md`.

- [ ] **2026-10-03 lap911 strategy 범위 판정(사용자/제품 승인 아님):** lap910 HOLD 확인 — lap909 맵 64장은 **메인 메뉴 화면의 맵**(payload 1종, 버튼 여덟 개 자리).
  lap909에서 수용하는 것은 hook 설치·present 경계·전사 호출 수·PS3 표본뿐이고 화면 비율과 전사 덮임 문장은 불수용. P5 순서 확정: P5-H(HUD 패널 표면) → P5-T(tinted RLE).
  근거는 후보 유효 coverage p50 0.692와 HUD 행 20%(월드 전부 덮어도 80%). 수리 B1~B5·gate G1~G4, 다음 work=D-1R. 고친 census는 미실행. 기준 완화0, D-1/G1 HOLD 유지.
  상세 `../work/active/G1_STRATEGY_W70_D1R_PRESENT_BINDING_P5_ORDER_LAP911.md`,
  `../history/laps/20261003_lap911_strategy_g1_d1_present_binding_p5_order.md`.

- [ ] **2026-10-04 lap913 middle 기술검수(사용자/제품 승인 아님):** D-1R build47/current·DLL/raw64/header·P-a~P-f·같은실행 시각 독립 `PASS(partial)`. 단 panel800×203 중161878(99.68%) 원천writerunknown, 최종HUD category10은 전사결과여서 P5-H 구현근거 미확인. `HOLD_PANEL_ORIGIN_UNPROVEN`·ESCALATE_SOL/G1 HOLD; 승격범위확인→work 최소probe 또는 lap911 fallback, 게임수정0. doctor/lint/typecheck·focused149/safety/contextPASS, fullFast/runtimeSKIP(user 근거불명stop). 상세 `../history/laps/20261004_lap913_middle_g1_d1r_panel_origin_hold.md`.

- [ ] **2026-10-04 lap914 strategy 범위 판정(사용자/제품 승인 아님):** lap913 패널 원천 HOLD 해소 — 패널 바닥은 `fnt\pannel{k,j,c}.spr` 한 프레임을
  렌더러 프리미티브 `0x4663E0`이 패널 표면 `[0x104F814]`에 그린 것(census 9 pin 밖). 기존 raw 대조: 범주 10 픽셀 4,449,556개 전부 pannelj 불투명 칸 위,
  PNG 일치율 pannelj 0.735~0.796(다른 그림 0.26~0.28). P5-H `FEASIBLE`(미러 실행 미검증), 계약 H1~H5와 사전 등록 대조 PH-a~PH-d, 다음 work=P5-H.
  기준 완화0, D-1R `PASS(partial)`·G1 HOLD 유지. 상세 `../work/active/G1_STRATEGY_W70_P5H_PANEL_LAYER_LAP914.md`,
  `../history/laps/20261004_lap914_strategy_g1_p5h_panel_origin_layer_contract.md`.

- [ ] **2026-10-04 lap916 middle 기술검수(사용자/제품 승인 아님):** build48×6/DLL/raw/SHA·PH-a–d·V1/V2/s/q·B′/C·HUD 독립 PASS(partial). H2 자산 key/HD 교체 경로 구현 누락으로 **P5-H HOLD_IMPLEMENTATION_MISSING_PANEL_ASSET_KEY·G1 HOLD**, 명확한 work 수리 인계·ESCALATE 조건없음. 입력/coverage90%/제품승인 없음; 상세 `../history/laps/20261004_lap916_middle_g1_p5h_review_h2_key_handoff.md`. 다음 한 가지는 STATUS만 따른다.

- [ ] **2026-10-04 lap918 middle 기술검수(사용자/제품 승인 아님):** H2 key/pack·build48×7·raw/PH/V1/V2계열 독립PASS(partial), B′1 HOLD·C2 유효FAIL을 유지해 P5-H HOLD/G1 HOLD. pair 성능gate 누락은 work 수리로 인계, ESCALATE조건없음·제품/단계마감0.
  상세 `../history/laps/20261004_lap918_middle_g1_p5h_h2_review_gate_performance_hold.md`; 실제 다음 한 가지는 STATUS만 따른다.

- [ ] **2026-10-04 lap925 strategy 범위 판정(사용자/제품 승인 아님):** lap924 observation-window HOLD 확인 — lap923 B′1의 DOWN 4·RIGHT 12 표본은 경계 뒤 present,
  B′1 raw PASS 불수용·"B′ 연속 2회" 미충족·P5-T/G1 HOLD. 경계를 sim tick(`sim_tick ≤ observation tick`)으로 확정하고 present 행에 `sim_tick` 한 필드 추가(O1~O7).
  P5-T 스크롤 뒤 present 간격 56.0~58.5ms(P4c-W·P5-H 48.97~49.83ms)·재호출 26~27ms/present 확인, 2단 수용 조건에 PT-c(≤ 52.0ms) 추가. 기준 완화0, 다음 work=P5-T-R.
  상세 `../work/active/G1_STRATEGY_W70_P5T_R_OBSERVATION_TICK_BOUND_LAP925.md`,
  `../history/laps/20261004_lap925_strategy_g1_p5t_observation_tick_bound_scroll_cost.md`.

- [ ] **2026-10-04 lap933 strategy 범위 판정(사용자/제품 승인 아님):** lap931·932 timer 범위 HOLD 확인(잔차 승인 보류 유지). 스크롤 뒤 비용의 뿌리를
  **클립 바인딩 두 번째 검증의 lane 불일치**(`g1_mirror2x.c:1381~1383`, 00 배경 `scratch_a` 대 FF 배경 `unclipped_ff`)로 귀속 — 9회 실행 마지막 mismatch 값 전부 `[0,255]`,
  replay ÷ mismatch 2.008~2.010, 고정 late20 mismatch 74.1·replay 148.7/present. 같은 fill 단가가 창에 따라 28.5~32.2배 다르다. 고친 빌드는 미실행.
  다음 work=P5-T-V(V1 FF lane 검증 → 예측 P-1~P-5 → 조건부 capacity 재사용). PT-d 절대 하한 11439는 PS3 첫 present 전에 정해지는 누적값이라 폐기하고
  PT-d′(tinted 호출 유지 + late20 coverage·stale 악화 금지)로 대체 — 과거 미달 값은 "지표 무효"이며 PASS 아님. 임계값·미러 범위·sentinel fill·validator 완화0, P5-T/G1 HOLD 유지.
  상세 `../work/active/G1_STRATEGY_W70_P5T_V_CLIP_VERIFY_LANE_LAP933.md`,
  `../history/laps/20261004_lap933_strategy_g1_p5t_clip_verify_lane_attribution.md`.

- [ ] **2026-10-04 lap937 middle 기술검수(사용자/제품 승인 아님):** lap936 r3 73입력·build48/current SHA MATCH, 선택151·빈0·drag `[124,140,151,170]`·캡처 전후 동일 PASS(partial).
  candidate present 경계가 주입 전 값이고 binding이 present `UNKNOWN`도 통과시키는 source 결함 확인 → `HOLD_POST_RELEASE_PRESENT_UNPROVEN`·ESCALATE_SOL. 상세 `../history/laps/20261004_lap937_middle_g1_input_capture_boundary_hold.md`.

- [ ] **2026-10-04 lap938 strategy 범위 판정(사용자/제품 승인 아님):** lap937 HOLD 확인. 같은 실행의 프로세스 안 input trace로 r3 gate의 두 present가 release **전**(−88/−39ms)임을 확정,
  lap936의 "button-up 뒤 2건" 문장 불수용. release 뒤·캡처 전 present는 5개(대조값)라 선택 의미 부분수용은 유지. 경계 = 게임 WndProc `WM_LBUTTONUP` 행(R1~R5),
  회귀 7건, 사전 등록 예측 P-1~P-6. 고친 gate는 미실행. 기준·임계값·기대 ID 완화0, 입력 캡처·G1 HOLD 유지, 다음 work=입력 경계 수리+fresh pair.
  상세 `../work/active/G1_STRATEGY_W70_INPUT_RELEASE_BOUNDARY_LAP938.md`,
  `../history/laps/20261004_lap938_strategy_g1_input_release_boundary_inprocess.md`.

- [ ] **2026-10-04 lap942 middle 기술검수(사용자/제품승인 아님):** lap941 final 진단minimap 선택4·pending 변화·WndProc 입력·build48/current·EXE/save·PNG12·gate원복·cleanup 독립 PASS(partial), G1 HOLD. 생산 재중심x182는原본bounds밖, UNKNOWNcontrol→PASS는 명확한하네스결함이라 work최소수리+fresh pair로 직접인계. 정상gate0/arrival/camera/production未검증·ESCALATE조건없음. 상세 `../history/laps/20261004_lap942_middle_g1_minimap_command_review_production_handoff.md`; 현재큐는 STATUS만.

- [ ] **2026-10-04 lap944 strategy 범위 판정(사용자/제품 승인 아님):** lap943 승격 해소 — queue type31이 원본 witness(발행 코드 `0x40DF05`·`0x40DF21`, 클릭 전 HQ 3개 `31/100`, 툴팁 `일본 농부 800/300/10`), 사전 type7은 진영1 fixture 상수의 오전사. witness를 command 15 + progress 되감김 + 발행 단계 비용 정확 일치로, control을 건물 필드 판정 + 자원 변화 공개로 바꾼다(K1~K6, 예측 P-1~P-6). lap943 r4 production UNKNOWN/HOLD·G1 HOLD 유지, 고친 하네스 미실행, 다음 work=수리+fresh pair.
  상세 `../work/active/G1_STRATEGY_W70_PRODUCTION_QUEUE_WITNESS_LAP944.md`, `../history/laps/20261004_lap944_strategy_g1_production_queue_witness_contract.md`.
