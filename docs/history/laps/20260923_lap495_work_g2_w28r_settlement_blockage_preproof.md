# 2026-09-23 | lap 495 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5 / high / **work** (카드
  `docs/work/active/G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_R_LAP494.md`, W28-R,
  `READY_FOR_WORK`, lap494 middle 발행, `ESCALATE_SOL`§57 Q6-C).
- 가설 / 사용자 관찰: W28(lap491)이 관측한 재개는 실재하지만(lap492/493/494가 원시로 3중 재현),
  자동화 자체에 결함 3건(D1 완주 기준선 오적용/D2 "읽기" 정의 미확정+콜 주변 표집 위반/D3 무결성
  분류기가 정산 직후 조용히 꺼짐, N135)이 있어 라벨을 확정할 수 없었다. R-1·R-2·R-3만 고쳐 게임
  1회로 **관측 완주만** 다시 받는다(파라미터·판정식·라벨은 W28과 동일, R-4).
- 예상 PASS / FAIL 조건: `CALL2_ENGINE_TICK`(콜#2 자신의 `tick_after`) 기준 ≥600tick(610까지 여유)
  완주 + `reads.jsonl` 병합 읽기열에서 콜 인접 ±10tick 구간 간격 ≤3tick + 사망/reverted가 주문
  종결 후에도 검사됨(N135 회귀 테스트) ⇒ 라벨 산출. 미달/위반이면 `PRECONDITION_NOT_MET`이고
  §57 R-5에 따라 **재실행 없이 Q6-B로 자동 종결**.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 저장소 source **변경 0**(before/after
  SHA 일치, 아래). 새 스크립트 1개만 `temp/`에 추가:
  `temp/Syw2plus_patch/g2_capacity/20260923_lap495_w28r_settlement_blockage_preproof/w28r_settlement_blockage_preproof_counterfactual.py`
  (lap491 스크립트의 복사본에 R-1·R-2·R-3만 반영, sha256
  `df535d937c1f2f31f0c6e2cc4731871cce380ee0af975b4c432a53b8b68fc56a`). uncommitted(이 저장소는
  `unborn` HEAD, `LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본exe before/after
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(일치) / 후보(fixed_supply_5000)
  `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3` / bridge dll
  `17facbd3555029e0ecb3cacad7594d13ee06233f8fb1e969786601f4059493eb` / `runtime_bridge.c`
  before/after `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`(일치) /
  `control_executor.c` before/after `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`
  (일치, lap494가 기록한 값과도 일치 — 지난 3바퀴 동안 source drift 0). 격리 Xvfb `:210`(카드가
  기록한 점유 목록 `:0 :1 :11 :77 :78 :99 :100~105 :107 :186 :187 :256`과 겹치지 않음, 실행 전/후
  lock 미존재 확인). 활성 플레이어: owner0 1인 fixture(`_custom_game_chain_inject_g2_eight_seed42`
  체인, cap=5000). fixture: 장부 구성(op4) — cap 근접 안정성/G2 완료 근거 아님(R2′ 승계).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 w28r_settlement_blockage_preproof_counterfactual.py
  --display :210` (foreground, 동기, background 미사용, 1회, exit=0). 산출물 디렉토리
  `temp/Syw2plus_patch/g2_capacity/20260923_lap495_w28r_settlement_blockage_preproof/`:
  `run_summary.json`(sha `992fcf4c914a79a6a24709e444f46be61cb87f4f605b4d7df99a72837a5d3ce9`),
  `reads.jsonl`(신규 1급 산출물, R-2, sha
  `24da5adf34a47f2366e675b61637f1e77486bb5a1bcd5c20d9e5fa482d7c91b0`, 546건),
  `window_samples.jsonl`(sha `a466cbb01b447063c2c614a3f3d649e00913d2d6505b1ea6be2054cb27f22434`,
  542건), `events.jsonl`, `death_events.json`, `finalization_events.json`,
  `unbalanced_termination_events.json`, `supply_probe_call_log.json`, `positive_control_samples.jsonl`,
  스크립트 사본. orchestrator.log에 전체 타임라인.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **op4 정확히 2콜**(R2′ 준수, id263 tick711/711
  구성·id585 tick1610/1610 counterfactual, 둘 다 `tick_before==tick_after`). 차단 선입증
  `t0=1406→firing_sample_tick=1607`(streak=201≥200), `CALL2_ENGINE_TICK=1610`(D1 수리 —
  `firing_sample_tick`과 스큐 -3, 더 이상 혼용하지 않음). AND-3 전이 1건: `reads.jsonl`상
  콜#2 after(`used=4980,reserved=10,count=5`, tick1610) → 표본(`used=4990,reserved=0,count=6`,
  tick1612) = **resume_delay=2tick(강귀속)**. **관측 완주 610/610**
  (`full_600_window_observed=True`, D1 수리). **사망 1건을 정산 이후에도 포착**
  (tick1943, `order_was_open=False`) — D3/N135의 정확한 회귀 테스트이며 lap491이 놓쳤던 것과
  같은 사건이 이번엔 `death_events.json`에 실제로 기록됨. `event_crosscheck` 불일치 **0**
  (death/resume_balanced/unbalanced/reverted 배열=재계산 전부 일치, D2/D3 수리 확인).
  `reads.jsonl` 콜#2 ±10tick(1600~1620) 구간 `sampling_gap_violation=None`(간격 전부 ≤3, D2 수리
  확인); 창 전체 간격 min1/max4/mean2.78. 무결성: 음수·wrap 0, `ledger_reverted_by_engine`=False,
  안전위반0. `settled_unit_slot=1148` 특정, 사후 생존 폴링 실패 없음(보고 의무, 판정 무영향).
  **work 산출 라벨(미확정, §7): `SETTLEMENT_RESUMED_AFTER_HEADROOM`**
  (attribution=strong, resume_delay_ticks=2). op4 배제 핀 3종 현존 확인(그ep 코드 grep). source
  변경 0이므로 표적만 실행: `test_runtime_env`/`test_g2_eight_owner_setup`/`test_g2_stock_stress`/
  `test_g2_stock_lifecycle`/`test_g2_official_creation` **186 passed**. `checks/safety.sh check`
  → `SAFETY_PASS`. `checks/context_limits.py` → `CONTEXT_PASS`. 잔류 프로세스 0(Xvfb/wine/wineserver
  전부 종료 확인, `:210` lock 해제). 게임실행1·source변경0·커밋0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **이 lap(work)은 라벨을 확정하지 않는다(§7).**
  다음 middle이 `run_summary`의 `verdict`/`reason`/파생 필드를 참조하지 않고 `reads.jsonl`·
  `window_samples.jsonl`·`events.jsonl` 원시만으로 재계산해 ACCEPT/REJECT와 라벨을 확정해야 한다.
  §57 R-5: 이 실행에서 관측이 미달했다면 재재실행 없이 Q6-B 자동 종결이었을 것이나, 이번 실행은
  610/610 완주했으므로 그 경로는 해당하지 않는다(재실행 사유 없음, 카드는 1회 한정이라 이 결과가
  최종 실행분). §8: W26(144k) 재개방은 이 결과에 대한 middle ACCEPT + 무결성 위반 0에 종속되며
  그 전 금지 유지. (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 여전히 사용자 전권 대기.
- 다음 한 가지: **middle(Opus5/high)이 이 lap495 산출물을 원시(`reads.jsonl`/`window_samples.jsonl`/
  `events.jsonl`/`supply_probe_call_log.json`)만으로 독립 재계산**해 W28-R §7 종결 조건(라벨 확정
  또는 `CLOSED`)을 판정한다. ACCEPT 시 §8 조건에 따라 W26(144k) 재개방 여부를 middle이 판단한다.
