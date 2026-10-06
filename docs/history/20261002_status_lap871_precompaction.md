# STATUS — 매 바퀴 갱신하는 기억

lap858 압축 전 STATUS 전문은 `docs/history/20261002_status_lap858_precompaction.md`에 보존했다
(126줄, SHA256 `08a5644d3dd713d5a07a054369550ea7c111feb5e1073825b2463563f12f8886`). 그 이전 전문은
`docs/history/20261001_status_lap844_precompaction.md`(129줄, SHA256 `765e8d18af86901cc2851d076610dbf5e7ed11d3e4fd2f8de6261f77feb07cf5`)와
`docs/history/`·`docs/history/laps/`에 있다. G5 v10은 사용자 3단 승인·종료, G2 ESL2608 점검은 lap806에서
마감했고 현재 최우선은 G1이다.

## 지금 상태

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | lap869 middle: raw·captured rice 차이 독립 확인, 완료 update phase 미증명으로 B' HOLD·승격 | same-tick player difference diagnosis; C gate, D-1 PS3 census, HUD/tinted/GDI, 전체 HD coverage ≥90%, 두 번째 장면, 사용자 승인 |
| G2 | ESL2608 체크리스트 종료(제품 결함 미발견), 일부 `UNKNOWN/BLOCKED(env)` | hero runtime, DxWnd·멀티, 미니맵 runtime, middle/사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 사용자 지시로 보류 | candidate AI 정책 없음 |
| G5 | v10 종료·사용자 3단 승인 | 멀티 env 제한 수용 |

## 지금 막힌 것 (Blockers)

lap869 independent: action24730/24826 records equal; final24862 owner6 rice230207/231007(Δ800), 나머지 captured fields·573units 일치.
raw·원본·fixture·DLL·42build 입력 MATCH. live bulk-read의 stable tick은 atomic/equal completed-update phase 증거가 아님.
실제 captured 값 차이는 확인했으나 지속 simulation divergence·직접원인 UNKNOWN; B' HOLD·사용자 충돌 stop·승격. lap870은 STATUS work 지시와 보존 인계의 elevated-middle 선행 승인 요구가 충돌해 정적 writer 조사를 시작하지 않고 재승격.

## 다음 한 가지

- **다음 한 가지 = elevated middle이 lap869의 captured rice 차이와 completed-phase 미확인 구분을 독립 판정하고, lap870 work의 read-only writer 진단 권한/범위를 명시한다.** STATUS의 work 지시 및 `loop/ESCALATE_SOL` 참조와 달리 현재 marker는 없고 보존 인계(`docs/history/20261002_lap869_rice_phase_handoff_operator_archive.md`)는 middle 선행 승인을 요구한다. lap870 기록 `docs/history/laps/20261002_lap870_work_g1_p4b_authority_conflict_escalate.md`. 이 확인 전 writer 조사·probe/tests 변경·runtime 금지.
- B' 전체 독립PASS 전 C fresh3 금지, D-1 전 P5 금지. EXE/HD/DLL/validator/임계값/G2/G5/기존raw/원본 변경·커밋 금지. G1 milestone 경계 아님.

## 검증 상태

- 기준 입력: 보호 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 비합성 save006 SHA
  `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`(상세 558 unit records·8 player records, 활성 8인 부하 증명 아님).
- lap854 work(P3c): env latch 후 QPC 예측 pair + 계측 OFF fresh 3 pair PASS — ratio `0.9999920/0.9999970/1.0000019`, p95 delta
  `+5/+5/+5ms`, present 400, Scale2x validator PASS, 선택·빈 클릭·drag_exact true. 전체 Fast 1219 passed·5 skipped, exit0
  (`logs/gates/lap854-work-fast-r2.log`). pair/raw SHA는 lap854 기록.
- lap855 middle: 4 pair 성능·build 입력 42개·DLL·raw/capture 독립 확인, validator 부등식 누락 반례 2건 재현(HOLD).
- lap856 work: validator/test 2파일 수리. 반례 `BLOCKED`, 경계 `PASS`, raw 4개 `PASS`. 최종 `make check` **1220 passed, 5 skipped
  in 772.27s**, Ruff/compileall/mypy·CONTEXT_PASS, exit0(`logs/gates/lap856-work-fast.log`/`.exit`). 신규 runtime 0.
- lap857 middle: 수리 독립 확인(반례 2 `BLOCKED`, 경계 2 `PASS`, per-present/overmatched 거부, 5049 present 위반 0), pytest 4 PASS.
- lap858 strategy(문서만, 새 runtime 0): 위 SHA·validator 6회·pytest 4·5049 present 부등식·tick ratio/p95·입력 checks를 직접
  재계산해 기록과 일치 확인. QPC compose 수치는 lap855 값 인용(재계산 안 함). P4 귀속은 보호 원본 정적 판독이며 실행 미검증.
  `make lint`/`make typecheck`/`checks/safety.sh check`(SAFETY_PASS)/CONTEXT_PASS/scoped `git diff --check` PASS. 기록 작성 후
  최종 `make check` 1회: **1220 passed, 5 skipped in 789.00s**, Ruff/compileall/mypy(10 files)/CONTEXT_PASS, exit0
  (`logs/gates/lap858-strategy-fast.log`/`.exit`). G1 source 8파일 SHA 전후 불변, lap counter858 읽기만. 이 Fast는 P4 귀속이나
  P3 성능의 검증이 아니다. uncommitted SHA: lap858 기록 `20c87b564bbd692ed7a56af09daefd2404493130aa46305e6b0277784dee964b`,
  P4 카드 `9310ee2abac94516d9a8ac02d32eaf91576fdbf689172d332990765d64a39da6`, memory map
  `1588775093e720e122652d26e64a2e9776c07fa1ba148452bad4d4c734daafe3`. STATUS70/INBOX267/APPROVALS180줄, Blockers 1개.
- lap859 work P4: `make -C tools/inmm_stub clean all`, focused suites 32+4 passed, Ruff/lint/typecheck PASS. R4 candidate Scale2x PASS; 400 present, effective coverage p50 `319,357.5` (66.53%), persistence `0.9773`, tick ratio `1.00000186`, p95 `+5ms`, source/scene/cleanup PASS. R5/R6 scroll pair logs and SHA are in `docs/history/laps/20261002_lap859_work_g1_w70_p4_terrain_hooks.md` (run path suffixes remain lap858). R6 recorded DOWN no camera change then RIGHT `[158,101]→[160,99]`; 30-present coverage p50 `57,136` (11.90%), so B-5 fails/unresolved. First full check exposed a stale `256u` test guard; after updating it to the card's 4096, final `make check` passed: **1224 passed, 5 skipped in 793.44s**, Ruff/compileall/mypy/CONTEXT_PASS, exit0 (`logs/gates/lap858-work-p4-fast-r3.log`/`.exit`).
- 현재 lap869 (`loop/.lap_counter` 읽기만). lap859 artifact/log의 `lap858_` suffix는 과거 provenance로 보존한다.
- Uncommitted source/test SHA256: `g1_mirror2x.c` `e5b3c1953234da358652cdc4eb05e0287246b2c68d99be144d51ca5ebacb5c44`; `.h` `e94ea2a1c52fd1297f99dfe5fc0294972064c14e1232e84ab0911675f926320d`; `g1_hd_asset.c` `7bdbc4b3f0dd93c111fe17d6280e179a4fcd6fbc1e7c85efe60057aea5405602`; `.h` `76476ba6c926f2e27d1263ce80c081ff1fcc5eb110b2ff56677a89a051678899`; `direct_draw_trace.c` `c5e4f2d48d8ebbe768ae7e9fc7ac5a4c953c38d45d4d0232817042bd0b5612b0`.
- Remaining source/test SHA256: `g1_saved_scene_probe.py` `2616ed30e5d3e3e3a0aff604a4700c62d871ca16bbed165e579496103b572f3f`; `test_g1_mirror2x.py` `1272c3aca1f785f502c56ec2e2989002185a0d876e674bbf5c0dd43774ee6856`; `test_g1_hd_identity_probe.py` `baf67c58b81ef28644bc1b2b097487004a901ba65e72cb06e88cf310c90d8a0b`; `test_g1_saved_scene_probe.py` `73820787b20b6a829a65185d8b44a6f11f10cf9490cd4b30c45272aebf84547b`. lap862 history/ESCALATE SHA는 make check 뒤 이 블록에 추가한다. Commit 0.
- `make doctor`: protected original verified at expected SHA; tools present, no side effects. Its optional runtime manifest is absent (`runtime.ok=false`); paired game probes themselves completed with cleanup PASS.
- lap862 work: receiver/camera 계측 수정; focused pytest14·lint·typecheck·DLL build PASS. r3/r4 fresh pair scene equal·cleanup PASS이나 DOWN lane parity 불일치 및 P4 coverage FAIL(21.60%/12.70%). census-only는 exit0이나 PS3 map 0/64, PS9 64/64. Full Fast 최종 실행 `logs/gates/lap862-work-fast-r3.log`/`.exit`: **1226 passed, 5 skipped in 775.57s**, Ruff/compileall/mypy(10 files)/CONTEXT_PASS, exit0. 앞선 두 full-run 실패는 입력 계측의 env latch / 단순 검사 parser 전방선언 충돌로 추적·수리했으며 final source-contract 2 tests PASS. Original SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 확인; `tools/check_setup.py` optional runtime manifest 없음(격리 pair 자체는 cleanup PASS). 상세 `docs/history/laps/20261002_lap862_work_g1_p4_scroll_instrumentation_escalate.md` SHA `281320836da4d873b3ec3aeb24c1c9edfffdde62ef679bc22132abc904bc97b5`; strategy handoff `loop/ESCALATE_SOL` SHA `f2284cd480c7bf8ad8ca78898aaa2a4e898dae6ffc96875cae2634908efaf45d`.
- skip 5는 pinned 참고 사본 부재이며 제품 PASS가 아니다. 과거 Fast를 이후 fingerprint의 PASS로 쓰지 않는다.
- lap863 strategy(문서만, 새 runtime 0): lap862 pair 2·candidate raw 2·census raw·source 10·기록·ESCALATE SHA 재해시 일치, 30 present
  p50·writer 호출 수 재계산 일치, 보호 원본 SHA 재해시 일치. lap862 기록의 전사 오류 2건(r3 전환 seq1565, probe SHA)은 기록 끝에 정정
  (기록 SHA `8ab1e86891062565a1e67a00c47b3918a883ef6ccaf11af1f806056712f3adaa`). 캐시 이동·복사 귀속은 정적 판독+기존 raw이며 실행 미검증.
  `make lint`/`make typecheck`/`checks/safety.sh check`(SAFETY_PASS)/CONTEXT_PASS/scoped `git diff --check` PASS. 기록 작성 후 최종
  `make check` 1회: **1226 passed, 5 skipped in 806.01s**, Ruff/compileall/mypy(10 files)/CONTEXT_PASS, exit0
  (`logs/gates/lap863-strategy-fast.log`/`.exit`). G1 source SHA 전후 불변, lap counter863 읽기만. 이 Fast는 P4b 귀속·설계의 검증이
  아니다. uncommitted SHA: lap863 기록 `0d701a62b6fca9ef71145dab3dd1f3f3ea4aaee5360d2806cc138eb6ac98ddb8`, P4b 카드
  `41d02e4c0d31d12d0bc77febbc935154577da1daf08e76611aa40618147e01ef`, memory map
  `e76890d5ffcd43893f878eb000e6dc07c9ed05d029c37e6f1cf30f103ac5d012`. STATUS108/INBOX276/APPROVALS203줄, Blockers 1개.
- 미검증: P4b 전체 gate(입력/scene parity·고정 지속성·성능), PS3 census(현재 capture PS9뿐), C fresh 3 pairs,
  스크롤 중 성능, 두 번째 장면, HUD/tinted/GDI, G1 사용자 승인.

## 바퀴 기록

- lap869 middle: raw/pair/DLL·원본/fixture·42build SHA MATCH; action 동일/final owner6 rice Δ800 독립 확인. stable tick의 완료 phase 미증명으로 HOLD·승격; 구현0. doctor/focused25/lint/typecheck PASS, full Fast/new runtime SKIP(사용자 충돌 stop). 상세 lap869 기록·temp recalculation·ESCALATE_SOL. 종료 수치 아래 보강.
  종료 확인: SAFETY_PASS·CONTEXT_PASS·scoped diff/new문서 whitespace PASS; source47 SHA 전후불변, lap869 읽기만·Blockers1. STATUS124/INBOX278/APPROVALS220줄.
  uncommitted 기록SHA `6d32b50d31cc82e72ffb1189959bef338ebec1738b8859cfabadd9c0857cabde`, ESCALATE SHA `511ff4060fae61d9aa002d295408047ec8cf53c04dc5d391cee7fe3f21ed50cb`; 현fingerprint full Fast PASS 없음.

- lap870 work: 최신 STATUS와 lap869 보존 인계가 work 진단 권한 순서에서 충돌하고 참조된 `loop/ESCALATE_SOL`은 부재함을 확인. 주소·완료 phase 조사, 코드·테스트·runtime 0; middle의 권한/범위 판정을 요청. 상세 `docs/history/laps/20261002_lap870_work_g1_p4b_authority_conflict_escalate.md`.

- lap868 work: common absolute tick plan·bulk coherent scene/player read를 probe/tests에 구현. focused25/lint/typecheck PASS; fresh gdb-free private save006 pair 양 lane cleanup PASS. input/observation/final tick·camera bracket 일치, scene read1.3~3.2ms, unit states 동등. final owner6 rice 230207/231007 차이로 B' HOLD·Sol handoff. candidate Scale2x validator·coverage PASS. 기록 후 `make check` 1238 passed·5 skipped/887.08s, Ruff·compileall·mypy·CONTEXT_PASS, exit0 (`logs/gates/lap868-work-fast.log`). 상세/raw SHA `docs/history/laps/20261002_lap868_work_g1_p4b_common_tick_observation_hold.md`.
- lap867 middle: r4/r5 raw·scene diff·42build 입력·DLL·원본/fixture SHA 독립 일치. r5 RIGHT24692/24710 wait end 차이와 snapshot tick/coherence 누락 확인, 직접원인UNKNOWN·HOLD·승격. 수정은 문서/marker만; 게임/하네스/build/runtime/커밋0. doctor/lint/typecheck·focused26 PASS; full Fast SKIP(사용자 충돌 stop), 현fingerprint PASS 없음. 상세 lap867 기록·temp 재계산artifact, 다음은 승격middle 확인→work.
  종료 확인: SAFETY_PASS·CONTEXT_PASS·scoped diff-check/new문서 whitespace PASS; source47개 SHA 전후불변, Blockers1, lap867 읽기만.
  uncommitted 기록SHA `9bef4b142042ffff67670038f0b73e7e0ff5001191d3d91a1850bd7c13398fc2`, ESCALATE SHA `dedd29496ad3c10b64c66d54abcbbdff16d4ad4e9f7f18042c76e7bc05660a8d`.
  직전marker archiveSHA `3885c7f29fc478fd1f64780d729bc1908b62b6380416d3ecb160e272c352eca7`; STATUS121/INBOX276/APPROVALS217줄. Full Fast는 SKIP이며 승인 없음.

- lap866 work: receiver-ready ACK/keyup 안정·exact one-step 하네스 수정. focused22/lint/typecheck/DLL build PASS. r5 fixed window·DOWN/RIGHT coverage·Scale2x·cleanup PASS; RIGHT action/final scene mismatch로 pair HOLD·Sol 독립검수 승격. 상세/raw SHA `docs/history/laps/20261002_lap866_work_g1_p4b_scroll_ack_scene_parity_hold.md`, `loop/ESCALATE_SOL`. 최종 `make check`: **1235 passed, 5 skipped in 896.35s**, Ruff/compileall/mypy(10 files)/CONTEXT_PASS, exit0 (`logs/gates/lap866-work-fast.log`/`.exit`).
- lap865 일반 middle: r4 pair/raw/DLL·build42 원 입력 SHA 독립 일치(생성 변환2개도 재생 확인), 두30-present p50·Scale2x1203 PASS 재확인.
  receiver-ready/release/keyup후 안정검사 결함을 확인했으나 DOWN13칸 직접 원인·키뒤 scene은 UNKNOWN으로 HOLD·승격했다.
  `make doctor`/lint/typecheck·focused36 PASS; full Fast/build/runtime SKIP(사용자 충돌 즉시 승격 지시), 원본/구현/커밋0.
  상세 `docs/history/laps/20261002_lap865_middle_g1_p4b_input_parity_hold_handoff.md`; 종료 문서·source 검사는 아래에 보강한다.
  종료 검증: SAFETY_PASS·CONTEXT_PASS·scoped diff-check/new-file whitespace PASS, build 원 입력42개 및 G1 probe/test/validator SHA 전후 불변.
  uncommitted 기록 SHA `85df2fc7595e9654c5b364761aea1a80fb5668889b6aa031dd24ecce64f02636`, ESCALATE SHA
  `afd752cc8d6d0a6d292a71b326930fb6bed9633ef4a7ad8d5757c3d3da2cbf5d`; 직전 marker archive SHA
  `58cefbcc964a7410ac17cfeea18eed43acedcf65658b9287d3d83dc633d6a5b5`. STATUS118/INBOX276/APPROVALS211줄, Blockers1.
  전체 Fast는 SKIP이며 이번 문서 포함 fingerprint에 PASS 없음; lap counter865 읽기만, C/P5/사용자 승인 없음.

- lap864 work: P4b 캐시 층 구현, CALL-site 의미 보존, terrain-scroll 계측·X11 수명 결함 수리. focused 32 PASS, lint/typecheck, safety/context/diff-check PASS. 격리 r4 pair scene/cleanup PASS, candidate Scale2x 및 DOWN/RIGHT coverage gate PASS; baseline DOWN 13칸·candidate 1칸으로 B' parity HOLD, 원인 미확정. `make check` exit0: **1228 passed, 5 skipped in 885.60s**, Ruff/compileall/mypy(10 files)/CONTEXT_PASS (`logs/gates/lap864-work-fast-r1.log`/`.exit`). 상세·raw SHA와 한계 `docs/history/laps/20261002_lap864_work_g1_p4b_cache_layer_input_parity_hold.md`; 독립 판정은 `loop/ESCALATE_SOL`. C gate 미착수, 사용자 승인 없음.

- lap863 strategy(Claude Code `claude-fable-5-1`): lap862 승격 해소. P4 `<30%`는 귀속 반증 아님(키 전 68.4~70.6%), 스크롤 결손 writer는
  `0x4324E0`의 캐시 memmove 8곳, 캐시→화면은 `0x466280` 복사로 판정. P4b 캐시 층 카드·memory map 발행, P4 카드 §5.1 정정,
  입력 parity는 gdb 없는 pair로 재측정 지시, PS3 census는 선행 조건에서 제외. 문서만 변경, 게임 실행 0, 커밋 0.
  `loop/ESCALATE_SOL`은 `docs/history/20261002_lap863_prior_lap862_escalate_sol_archive.md`에 보존 후 제거.
  `docs/history/laps/20261002_lap863_strategy_g1_w70_p4b_terrain_cache_layer.md`.

- lap862 work: receiver/key timing 및 present-camera barrier 추가; focused14/lint/typecheck/DLL PASS. r3/r4 fresh pair에서 scene/cleanup PASS이나 DOWN 도착 간격·카메라 이동 불일치와 candidate coverage p50 21.60%/12.70%. writer hooks active, P4 카드 `<30%` strategy 분기. census-only map64개 PS9, PS3 map0. 최종 Fast 1226 passed/5 skipped, exit0; 두 full-run source-contract 실패는 수정 완료. P4/PS3 census 판정은 strategy에 승격; 상세·hash 위 참조.

- lap861 일반 middle: lap860 pair/raw/source9 SHA 독립 일치, DOWN 불일치와 coverage57,136/47,778.5 재확인.
  입력 전 cursor 결함 확정, 수신/전환 seq 계측·회귀 조건 work handoff 구체화. 정확한 DOWN/stale 원인은 UNKNOWN으로 승격.
  fresh doctor PASS; full Fast/runtime SKIP(사용자 stop), 구현/빌드/커밋0. 현재까지 구현 무변경 연속2회; 재요약 세 번째 회차 금지.
  상세 `docs/history/laps/20261002_lap861_middle_g1_p4_transition_handoff_hold.md`; review SHA `592f2dc3dba9d993049accd2fa9099ce6831a3577b2a83037b1ed4062b89d53e`.

  종료 확인: SAFETY_PASS·CONTEXT_PASS·scoped diff-check PASS, source9개 SHA 전후 불변·lap861 읽기만.
  uncommitted 기록 SHA `0df4a9f75ca2aabe96dede93dc86c56a326f9433510044a91d1a1cc336c51b48`, ESCALATE SHA `e281cc397d89c2eabd9fab2a03f74ca9db4891d81facec11d9076568924814c2`.
- lap860 middle: 입력 근거 충돌 확인·P4 HOLD·승격. source9개 SHA 불변, fresh doctor PASS, full Fast/runtime SKIP(사용자 stop).
  종료 문서검사 CONTEXT_PASS·scoped diff-check PASS, STATUS77/INBOX267/APPROVALS186줄·Blockers1.
  uncommitted 기록 SHA `4d592a5d117b6093aaf5986ea879ead734b7bd205fd95eaa8d108e6278978126`, ESCALATE SHA `e308355a8aaacf6fffd2c48236e2529441178afeac0a085bce8beaba3baa41af`.
  raw 재계산 JSON SHA `1bef2ccc278312ad2282ea1c076e9c84bc02d0a966c5fc0b18e471bd0f469684`; 상세 `docs/history/laps/20261002_lap860_middle_g1_p4_scroll_input_conflict_escalate.md`.
- lap859 work: W70 P4 hooks와 fixed-window gate 일부 통과, scroll gate 원인/입력 불일치로 Sol에 검수 요청. 상세 `docs/history/laps/20261002_lap859_work_g1_w70_p4_terrain_hooks.md`, `loop/ESCALATE_SOL`.
- lap844~853: P3 Scale2x 배관 → 성능 counter 충돌(lap847/848) → fixed-window FAIL(lap849/850) → strategy 2회(lap851 클립 키,
  lap853 픽셀당 env 조회 결함 귀속). 상세는 각 `docs/history/laps/20261001_lap84*`·`20261002_lap84*~85*` 기록과 보존본.
- lap854 work: env latch·DLL 빌드·격리 save006 QPC+fresh 3 pair, P3c 1단 PASS 주장.
  `docs/history/laps/20261002_lap854_work_g1_w70_p3c_env_latch_gate_pass.md`.
- lap855 일반 middle: 성능·source·출력 근거 수용, validator 누락으로 P3 HOLD·승격.
  `docs/history/laps/20261002_lap855_middle_g1_p3c_validator_gap_escalate.md`.
- lap856 work: Scale2x validator nearest-deficit 부등식 추가. `docs/history/laps/20261002_lap856_work_g1_p3c_scale2x_validator_bounds.md`.
- lap857 일반 middle: 수리 확인, 마감 경계로 재승격·종료.
  `docs/history/laps/20261002_lap857_middle_g1_p3c_validator_repair_confirmation_escalate.md`.
- lap858 strategy(Claude Code `claude-fable-5-1`): P3 2단 통합 수용, P단계 판정 절차 정리, 지형 blitter 5종 정적 귀속으로 P4
  `FEASIBLE`·카드 발행, W70 P1 공백·P6 가정 정정. 문서만 변경, 게임 실행 0, 커밋 0. `loop/ESCALATE_SOL`은 보존 후 제거.
  `docs/history/laps/20261002_lap858_strategy_g1_w70_p3_accept_p4_terrain_card.md`.
