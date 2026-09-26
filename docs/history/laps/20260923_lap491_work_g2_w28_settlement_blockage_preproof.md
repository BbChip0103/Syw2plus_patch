# 2026-09-23 | lap491 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5 / 실무(work). 카드 `docs/work/active/G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_LAP490.md`(W28) §4를 게임 1회·동기·foreground로 완주(background 미사용, 재시도 없음).
- 가설 / 사용자 관찰: W27(lap486~488)은 재개를 관측했지만 개입 전 체류가 2tick뿐이라 "정산이 cap을 재검사하는가"(H-gate)를 입증하지 못했다(N127). W28은 **개입 전에 먼저 차단을 `T_block=200tick` 이상 연속 관측으로 입증한 뒤** op4 콜#2로 headroom을 복원해, 그래도 재개되면 H-gate가 (W27보다 강하게) 지지되고, 재개 전건 자체가 성립하지 않으면(정산이 200tick 이전에 자연히 끝나면) H-gate에 대한 반대 증거가 된다는 가설.
- 예상 PASS / FAIL 조건: 사전 고정 라벨 3종(카드 §5)만 사용. `SETTLEMENT_RESUMED_AFTER_HEADROOM`=AND-3 전이(`reserved`10→0 ∧ `used`+10 ∧ `count`+1)가 600tick 관측 완주 안에서 관측; `NO_RESUME_WITHIN_WINDOW`=완주했으나 AND-3 0건; `PRECONDITION_NOT_MET`=차단 선입증 불성립 등(사유 표 §5). 라벨 확정은 work가 하지 않고 다음 middle이 원시만으로 재계산한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 저장소 source 파일 변경 0. 새 스크립트는 저장소 밖 `temp/Syw2plus_patch/g2_capacity/20260923_lap491_w28_settlement_blockage_preproof/w28_settlement_blockage_preproof_counterfactual.py`(W27 스크립트를 복사해 카드 §4의 교정 5건 적용; SHA 아래)에만 있다. 커밋 0(LOOP_ALLOW_COMMITS 미설정, 기본0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 exe SHA256 실행 전 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` = 실행 후 동일(`source_unchanged=true`).
  - `patches/population/runtime_bridge.c` SHA256 실행 전/후 동일 `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`.
  - `tools/inmm_stub/control_executor.c` SHA256 실행 전/후 동일 `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`.
  - 후보(fixed_supply_5000 패치본) SHA256 `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`. 진단 브리지 dll SHA256 `ce49e19edf7e70b8425a257c5592f552e39221acec0acd8b6c42149d76d269fc`.
  - 이 저장소는 아직 git 커밋이 없어(`current_head=unborn`) "3자(before/after/git) 일치"의 git 항목은 성립하지 않는다 — before/after SHA 일치만으로 source 변경 0을 증명했다(위 3개 파일).
  - 환경: 격리 Wine prefix(`runtime_env.prepare()`가 매 실행 신규 생성, 기존 `.wine_syw2_baseline`/`:2`와 겹치지 않음), Xvfb `:199`(실행 전 lock 없음 확인, 실행 후 lock 제거 확인), `WINEARCH=win32`, `SYW2_SUPPLY_PROBE=1`.
  - 활성 플레이어: owner0 1인(비-AI, op4/op1/op6/op7 직접 호출). cap=5000 확인(`owner0 at PS3` cap=5000). 지도/군대: goal `_custom_game_chain_inject_g2_eight_seed42`(Step C v2 이후 불변, non-AI 8인 체인). building_type=46(cost20), order_type=7(cost10).
  - fixture: op4로 만든 "장부 구성" 상태(`used=4995` 뒤 `used+reserved=5005>cap`) — 실제 유닛 구성과 어긋난 **의도적 장부 desync**이며 cap 근접 안정성·G2 완료·W26 정량 근거로 재사용하지 않는다(카드 §6 명시 승계).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 w28_settlement_blockage_preproof_counterfactual.py --display :199`(cwd=산출물 디렉터리). 전체 산출물:
  `temp/Syw2plus_patch/g2_capacity/20260923_lap491_w28_settlement_blockage_preproof/`
  (`orchestrator.log`, `run_summary.json`, `window_samples.json`/`.jsonl`, `events.jsonl`, `death_events.json`, `finalization_events.json`, `unbalanced_termination_events.json`, `positive_control_samples.json`/`.jsonl`, `supply_probe_call_log.json`, 스크립트 사본, `bridge_build/`). SHA256은 `run_summary.json` 안에 원본/브리지/후보 값으로 기록됨(위 절 참조). 새 캡처 PNG는 없음(이 카드는 화면 캡처를 요구하지 않음).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - 양성 대조(PC): op1 수락→정산까지 **L=703tick**(주문 tick7→정산 표본tick710), progress100 표본tick707, 정산표본tick710, **표본 tick 기준 지연=3tick**(대조군 표집 간격 CONTROL_POLL_S=0.03s, 실측 poll당 대략 1~수tick). 차단 predicate(progress100∧reserved==10∧command==15) 히트 **1건**(N132 기대값 0과 다름 — progress100 관측과 정산 사이 3tick 창 안의 과도상태 1표본, 해석은 middle 판단).
  - 주문 A: 5중 신호 수락 확인(tick716, `reserved=10`, `rice_delta=-800`).
  - op4 콜#1(구성): tick718, `used=4995`, `used+reserved=5005>cap`(구성 전제 충족).
  - progress100 최초 관측(t0) = **tick1414**.
  - 5중 신호 연속 스트릭이 t0부터 끊기지 않고 유지되어 **tick1615에서 streak_ticks=201(≥T_block=200)** 로 선입증 성립 → 그 직후 **op4 콜#2(counterfactual) `used=4980`** 발사(tick1615).
  - **tick1620**(콜#2로부터 **+5tick**)에 AND-3 전이 관측: `reserved`10→0 ∧ `used`4980→4990(+10) ∧ `count`5→6(+1). 귀속 구간 `T_attrib=50tick` 이내(+5) ⇒ 귀속 강도 **strong**.
  - 콜#2 엔진 tick(1615)부터 **600tick 관측 완주**(중단 없이 tick2216까지, 정산/사망에서 break하지 않음, 카드 §4-8 준수). 사망 0건, 안전 위반 0건, `ledger_reverted_by_engine` 0건.
  - 산출 라벨(work의 사전고정식 기계 계산, **middle 원시 독립검수 전이므로 미확정**): **`SETTLEMENT_RESUMED_AFTER_HEADROOM`**(H-gate 지지, attribution=strong, resume_delay_ticks=5). 이 라벨은 카드 §7대로 middle이 원시만으로 재계산해야 확정된다.
  - window_samples 550건, positive_control_samples 257건. 무결성: 음수/int16wrap 0, `used+reserved` 최대 5005(의도된 fixture, F4 §6 예외), source 3자 중 before/after 일치 2/2(git 항목은 unborn HEAD라 해당 없음).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 회귀: `tests/test_runtime_env.py`, `tests/test_g2_eight_owner_setup.py`, `tests/test_g2_stock_stress.py`, `tests/test_g2_stock_lifecycle.py`, `tests/test_g2_official_creation.py` = **186 passed**(이번 카드와 직접 관련된 op4 배제 핀·vehicle·fixture를 덮는 다섯 파일; 전체 784는 이번 회차 source 변경 0이므로 2026-09-20 21:58 지시+N22에 따라 재실행하지 않음 — 이번 회차 source를 바꾸지 않았음을 여기 명시한다). `bash checks/safety.sh check` = `SAFETY_PASS`. `python3 checks/context_limits.py` = `CONTEXT_PASS`.
  - op4 배제 핀 3종 실행 전/후 모두 현존 확인(`tools/runtime_env.py:5837 "op4_used": False`, `tests/test_g2_stock_stress.py:20 assert "request(4" not in SOURCE`, `tests/test_g2_eight_owner_setup.py:166 assert "op4" not in block.lower()`).
  - 잔류: 실행 후 wine 프로세스 0건, `/tmp/.X199-lock` 제거 확인.
  - 남은 위험: (1) N132 기대와 달리 PC 대조군에서 predicate 히트 1건 관측 — 특이도 해석은 middle 판단 필요. (2) 이 결과가 "지지"하는 H-gate 귀결은 work가 확정하지 않는다(카드 §7). (3) (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 이번 회차와 무관하게 계속 사용자 전권 대기.
  - 독립 검수: **아직 없음** — 다음 middle이 `run_summary.json`의 `verdict`/`reason`을 참조하지 않고 `window_samples.json`/`positive_control_samples.json`/`events.jsonl` 원시만으로 재계산해야 한다(카드 §7).
- 다음 한 가지: middle(Opus5/high 또는 Sol)이 이 산출물을 원시만으로 독립 재계산해 라벨을 확정하고, 카드 §7/§8(W26 재개방 조건: 완결적 1회 종결 + 측정 ACCEPT + 무결성 위반0)을 판정한다.
