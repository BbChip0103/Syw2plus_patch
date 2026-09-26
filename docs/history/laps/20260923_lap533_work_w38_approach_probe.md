# 2026-09-23 | lap 533 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, work(실무).
- 가설 / 사용자 관찰: lap532 strategy 판정(§86 회부 (a) 채택)의 W38 접근 진단 probe.
  N192(op8 1,872/1,872 수락되지만 4짝 중 3짝이 39파동 내내 거리4 고정·사망0)가
  "승격 안 됨/승격됐지만 못 움직임/움직였지만 못 때림/실제로는 교전함" 중 어느 것인지를
  게임 1회로 가른다. 카드 `docs/work/active/G2_STRATEGY_N192_APPROACH_PATH_LAP532.md` §2.
- 예상 PASS / FAIL 조건: 카드 §2 판정식(BLOCKED > PROBE_VOID > ENGAGED > MOVED_NO_HIT >
  PROMOTED_NO_MOVE > NOT_PROMOTED, 대조 CONTROL_MOVED/CONTROL_STILL/CONTROL_NA 별도 표기).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): repo source 변경 0(3파일 SHA
  게이트 확인 후 진입, 아래). 신규 하네스
  `temp/Syw2plus_patch/g2_capacity/20260923_lap533_w38_approach_probe/w38_run.py`
  (SHA `408827562867dde2a9d81d4b3d8eca8a993ea245d19acc6cb390965bc20364aa`, W37
  `w37_run.py`의 파생, 카드 H6~H9만 추가). 커밋 0(LOOP_ALLOW_COMMITS 기본0, uncommitted).
  게이트 SHA 확인: `patches/population/runtime_bridge.c`=`3555848d5389dc44699967cc7e44428f67d1e90be587e114c26fd907127f96b0`,
  `tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py`=`2a8aa4f788ae35c869300726da65907ae0d82f28b69868c15c6212ae27605478`,
  `tests/test_g2_runtime_bridge_op8_order_engagement_contract.py`=`0939f5b6a1aecbaf07479d53bdf40044ae550f7b97284f38779da655478f9fc7`
  — 카드 §2 경계1 핀과 전부 일치, 게임 시작 전 게이트 통과.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(전후 불변, 확인).
  후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(W26/W35~W37 핀과
  일치). 격리 Xvfb `:6533`, prefix
  `local/runtime/20260923_214111_3333625_0/prefix`(gitignored). 8인 seed42, cap5000,
  시딩(op5 type5×100 → op6 type7×25 → op5 type2×60 → op6 type46×20, producer 마지막,
  W37과 동일). A1 8/8 owner `used`=4,950(범위 4,900~5,000 내), A8' 전항목 PASS.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 w38_run.py`(foreground, 동기 대기,
  wall 2,700s 상자 — 실제 소요 약 128초). bridge SHA
  `00e17da47b938e1a701b1baf99ead44460a6f1ad90db3ee54ae666e0282f8020`. 산출물
  `temp/Syw2plus_patch/g2_capacity/20260923_lap533_w38_approach_probe/`(`run_summary.json`
  `f9a48142f1d896ea93311081569539f747f27bdca869958e1261ee19a849ee4f`, `trace.jsonl`
  `a2ff394ea18980b04fb08ab2b0af8f1509031a89626e78418493caa84ca4d4b4`(2,592줄), `t0_positions.json`
  `04653a7c418a2edf7a8ac424a7d7e73d9bbc4201ed92c1670cf79fb06815e014`(1,656슬롯), `waves.jsonl`
  `7e4ad317f7d29951529516cbe5cb22806f9b3a381ef4b517d2cfa2646e769c51`, `control_wave.json`
  `0247d1a9035312cdb9a5af5d533577c62523e1f2e25ac3e37f4647f782fb9c8b`). 잔류 프로세스 0,
  원본 SHA 전후 일치, `w38_orchestrator.log`에 전체 타임스탬프 기록.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 전처리 PASS(issuer 서명 일치, type2 행 preflight
  PASS, cap5000 확인). 파동1~3 실행: T0_tick=70, baseline_end=1074(1000tick 완주),
  파동 스케줄 [1070,1670,2270], 실제 시작 [1074,1760,2446] — 시간당 tick 진행 정상.
  op8 요청 144/수락 144(=|S|, 전부 선택시점 거리≥2). **자기 판정 `PROMOTED_NO_MOVE`**
  (promoted_share 142/144=98.6% ≥50%, moved_share 22/144=15.3% <50%, hit 0/144, ENGAGED
  대상 짝 0). **H7 양성 대조는 `CONTROL_NA`** — owner0→1, owner4→5 두 쌍 모두
  "no_living_type110"(owner0 type110 생존0/owner1 대상 후보2, owner4·5 둘 다 0).
  **신규 사실(N195, 읽기만): H8 T0 위치표(1,656 living slot) 전체에 type110이 0기다.**
  T0에 존재하는 타입은 {2,5,7,46,49}뿐이다 — seed42 커스텀 게임 체인 goal
  (`_custom_game_chain_inject_g2_eight_ai_seed42`)이 stock 시작유닛 type110을 주지 않거나
  이 시점 전에 이미 소모됐다는 뜻이다(원인 미조사). 카드 §2 H7은 "type110이 없으면
  CONTROL_NA로 적고 대체하지 않는다"를 그대로 따랐고 대체를 하지 않았다(경계 준수).
  A5류 무결성 샘플(파동 시작 시점 스팟체크, 연속 감시 아님)에서 `used>5000`·`live≠sum(count)`·
  tick 역행 이상 0건. `fault_or_crash=False`, `verdict=PROBE_OK`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **work self-verdict이며 middle 미검수.**
  카드 §3 분기표는 CONTROL_MOVED 또는 CONTROL_STILL만 전제했고 **CONTROL_NA와
  PROMOTED_NO_MOVE 조합은 표에 없다** — type110 부재라는 fixture 성질이 §2 H7 설계 당시
  가정(G4 probe 환경처럼 stock 시작유닛이 있다)과 다르다는 뜻이다. middle이 원시(trace.jsonl/
  t0_positions.json/waves.jsonl/control_wave.json)로 라벨을 재계산하고, 표에 없는 이
  조합을 strategy에 회부할지 판단해야 한다. 게임실행1(카드 §2 경계4의 "최대2회" 중 1회
  소진, 하네스 결함 아니므로 재시도 없음)·source변경0·커밋0.
- 다음 한 가지: middle(Opus5.5)이 `trace.jsonl`·`t0_positions.json`·`waves.jsonl`·
  `control_wave.json` 원시만으로 카드 §2 판정식을 독립 재계산하고, CONTROL_NA×
  PROMOTED_NO_MOVE 조합(카드 §3 표 밖)에 대해 다음 한 가지(§3 표 재적용 또는 strategy 회부)를
  정한다. N195(T0 type110 부재)도 함께 전달한다.
