# 2026-09-23 | lap494 | 목표 G2 (W28-R 카드 발행 + lap491 원시 D1~D3 독립 재확인)

- **실제 provider/model/effort / 지정 역할:** Claude Code `claude-opus-5` / high / **middle(중간계획·컨펌)**.
  게임 실행 **0**, 게임 코드·제품 source 변경 **0**, 커밋 **0**. 산출물은 카드 1장 + 문서 + 재측정뿐이다.
  hands-on 구현은 하지 않았고 실행은 work(Sonnet5/high)로 명시 handoff했다.

- **가설 / 사용자 관찰:** 사용자 신규 지시 없음(INBOX 최신 미처리 항목은 lap471~491 W24~W28 계보).
  STATUS「다음 한 가지」= "middle이 `loop/ESCALATE_SOL` §57 R-1~R-6을 반영한 W28-R 카드를 발행한다".
  §57(lap493 strategy, Fable5)이 Q6를 **Q6-C**로 판정했다: 결함의 소재는 카드/스크립트이며 게임 1회
  비용으로 D1~D3를 수리하고 **관측 완주만** 다시 받는다.

- **예상 PASS / FAIL 조건:** (P1) lap492·lap493이 보고한 D1·D2·D3가 lap491 원시에서 그대로 재현되는가
  — 재현되지 않으면 카드를 발행하지 않고 strategy에 회부. (P2) R-1~R-6이 전부 문언화되고 R-4(완화 금지)를
  어기는 조항이 없는가. (P3) 활성 카드 ≤3, 같은 파일 단일 작성자, Fast 게이트 PASS.

- **변경 파일 / source fingerprint / 커밋:** 전부 **uncommitted**(이 저장소는 `unborn` HEAD).
  - 신규 `docs/work/active/G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_R_LAP494.md` (W28-R)
  - 수정 `docs/work/active/G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_LAP490.md`
    (상태 줄만 `READY_FOR_WORK` → `SUPERSEDED_BY_W28R`, **원래 표기 원문은 같은 줄에 보존**)
  - 수정 `docs/STATUS.md`, `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL`(§58 추가), 이 lap 기록
  - 신규 `temp/Syw2plus_patch/g2_capacity/20260923_lap494_middle_w28r_issue/`
    (`spotcheck_lap494.py`, `spotcheck_lap494_result.json`, `input_sha256.txt`)
  - **제품 source(`tools/`·`patches/`·`tests/`·`checks/`·원본 exe·브리지 C) 변경 0.**
  - **uncommitted 파일 해시(커밋 0이므로 이력은 해시로 보존):**
    W28-R `df901bb7617e3317…` / W28(상태줄만) `7f29153212d7d874…` /
    이 lap 기록(이 줄 추가 전) `9676a6b1869d7f9b…` / `docs/STATUS.md` `2750b7fcdde9394a…` /
    `docs/feedback/INBOX.md` `40b3b7d4646ea908…` /
    `docs/history/20260923_inbox_lap494_precompaction.md` `6f9643b8bbe52b45…`(=압축 직전 INBOX 원문,
    341줄, 동일 바이트) / `loop/ESCALATE_SOL` `c64b3d7a296dc344…`

- **원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:** 이번 회차는 게임을 띄우지
  않았으므로 실행 fixture 없음. 재측정 입력은 lap491 산출물이며 그 run의 fixture는
  후보 `fixed_supply_5000` `0a1da2263ff099b9…`, 원본 전후 `b56986e018b43293…`(불변),
  브리지 DLL `ce49e19edf7e70b8…`, `goal=_custom_game_chain_inject_g2_eight_seed42`, stock 1200-slot
  레이아웃, PS3, 8 owner, **의도된 장부 구성 fixture**(`used` desync, 안정성 증거 아님).

- **실행 명령 / 로그 / 캡처 경로 및 해시:**
  - `python3 temp/Syw2plus_patch/g2_capacity/20260923_lap494_middle_w28r_issue/spotcheck_lap494.py`
  - 입력 해시(`input_sha256.txt`): `window_samples.jsonl` `120d221afb43abeacec76d18fb75cbd19e7085051f69d4afc1947edfb0acae7a`,
    `supply_probe_call_log.json` `85c7aab9adb254341f98eb685e1c01cc6d3b33af9e5a6caa80d15105e32cb0d8`,
    `death_events.json` `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`,
    `events.jsonl` `6fbcb01d07830db9f5fcf1b877fc430fa6abbc7970600770cc1f5c65526808b7`,
    lap491 스크립트 `11c49ecbacdcab9040a25815e59a268803923818e00a1083b892afd81d9c8981`
  - Fast 게이트 로그: `/tmp/lap494_targeted.log`, `/tmp/lap494_safety.log`, `/tmp/lap494_context.log`
  - 캡처 없음(게임 실행 0).

- **측정값 / 판정:**
  - **§7 준수:** `run_summary`의 `verdict`/`reason`/`resume_delay_ticks`/`call2_tick`과 work 파생 보조
    필드 8종(`streak_ticks`/`transition`/`order_a_finalized`/`headroom`/`phase`/`call2_fired`/
    `order_a_unbalanced_terminated`/`ledger_reverted_so_far`)을 **입력에서 배제**하고 원시 1차 필드 +
    원시 콜 로그로만 재계산했다. lap492·lap493 산출물도 경유하지 않았다.
  - **차단 선입증 재현 PASS:** `t0`=tick**1414** → 발사 직전 표본 tick**1615**, **streak 201tick ≥ 200**,
    그 구간 **75표본** 전수 5중 신호, 위반 표본 **0**.
  - **op4 정확히 2콜** PASS(816콜 중 2). 콜#2 `id 596`, `r7=4980`, `ok/executed`,
    `before {4995,10,5}` → `after {4980,10,5}`.
  - **D1 재현 PASS(라벨 뒤집음):** `tick_before=tick_after=`**1618**, 마지막 표본 tick**2216**
    ⇒ 엔진 기준 완주 **598 < 600**(2tick 부족). 표본 기준(1615)이면 601. `run_summary`의
    `call2_tick=1615`·`resume_delay_ticks=5`는 같은 오적용의 파생값이고 정답은 **1618 / 2tick**.
    **소재 확정:** lap491 스크립트 `:815 call2_tick = tick`(표본 tick) → `:845` 종료 판정 →
    `:848` 로그가 그것을 "engine tick"으로 오라벨.
  - **D2 재현 PASS:** `used==4980` 표본 **0/550**, 표본만으로 AND-3 **0건**. 콜#2 after 블록을 읽기로
    인정하면 **1건**(1618→1620, 지연 **2tick**). 표본 간격 min**2**/max**5**이고 **>3tick 구간은
    `1615→1620` 단 1건** — 재개가 일어난 바로 그 구간. **원인 확정:** 콜 자체가 엔진 tick 3개
    (1615→1618)를 소비하므로 **표본만으로는 콜 구간 ≤3tick이 물리적으로 불가능**하다.
  - **D3 재현 PASS:** 표본 tick**1944** `count`6→5 ∧ `used`4990→4970(−20) ∧ `reserved`0→0 **사망 1건**인데
    `death_events.json`=`[]`, `events.jsonl`은 `finalization_balanced` **1건만**.
    **소재 확정:** `:694 order_open = not order_a_finalized and not order_a_unbalanced_terminated` +
    `:695~696 transition = classify_transition(...) if order_open else "none"` — tick1620 정산으로
    `order_a_finalized=True`가 되는 순간 **R1′ 분류기 전체가 꺼진다.**
  - **신규 N135:** 그 게이트는 사망뿐 아니라 **R1′ 4번(`ledger_reverted_by_engine`)까지** 끈다.
    lap491은 재개 직후부터 마지막 표본까지 **596tick 동안 스크립트 자체의 무결성 채널이 무력**했고,
    `ledger_reverted_by_engine=False`는 그 구간에 대해 **검사된 적이 없다**. lap492가 표본 재계산으로
    위반 0을 확인해 결과는 무사했지만 **fail-closed 장치가 조용히 꺼진 것 자체가 결함**이다.
  - **판정: lap492 검수와 lap493 §57 판정을 ACCEPT**(D1·D2·D3 전부 독립 재현, 불일치 0).
    W28은 `SUPERSEDED_BY_W28R`이고 **라벨은 확정하지 않는다.**
  - **발행물 = W28-R**(`READY_FOR_WORK`). R-1~R-6 전부 문언화:
    **R-1** 완주 기준선을 `CALL2_ENGINE_TICK := 콜#2 결과의 tick_after`로 유일 정의 + 발사표본 tick
    사용 금지 + 완주는 그 tick+600 이상의 **기록된 읽기** 존재 + `+610`까지 overshoot 표집
    (경계 건너뜀 방지, 벽시계 0.3초) + `resume_delay`도 엔진 기준.
    **R-2** `READS`(표본 ∪ op4 콜 before/after 블록, 엔진 tick 부착, tick 정렬)를 정의해 AND-3의
    "연속 두 읽기"를 그 위에서 판정(콜 after 블록을 읽기로 **인정** — 문언 확정) + `CALL2_ENGINE_TICK
    ±10tick`에서 `READS` 간격 **≤3tick 강제**(위반 시 `sampling_gap_violation`으로 재실행 무효) +
    콜 직전 `pre_call2_immediate` 표본 강제 + `reads.jsonl`을 1급 산출물로.
    **R-3** `classify_transition`을 모든 읽기에서 무조건 실행(`order_open`은 주문 종결 여부만 게이트),
    사망·R1′4번은 창 끝까지 검사 + 존재배열(`0x8990C8`, 2,400B 단일 스냅샷) 2회로 정산 유닛 slot 특정
    후 `settled_unit_survival` 폴링(보고 의무, 판정 조건 아님) + `event_crosscheck`(배열 vs 읽기열
    재계산) 의무 + "빈 배열=0건" 금지 재확인.
    **R-4** `T_block`200·`T_attrib`50·`used=4980`·op4 정확 2콜·배제 핀 3종·라벨 3종·700tick 지평 **동일 유지**
    (§9에 "파라미터·판정식 변경은 범위 밖" 명문화).
    **R-5** 1회 한정 — 재미달 시 `observation_incomplete` 확정 후 **Q6-B 자동 종결**(판정식 표에 명기).
    **R-6** §8 W26(144k) 재개방은 W28-R ≥600tick 완주 + middle ACCEPT + 무결성 위반 0에 종속.
  - **Fast 게이트:** 표적 **186 passed**, `checks/safety.sh check` = `SAFETY_PASS`,
    `checks/context_limits.py` = `CONTEXT_PASS`. op4 배제 핀 3종 현존 확인
    (`tools/runtime_env.py:5837`, `tests/test_g2_stock_stress.py:20`, `tests/test_g2_eight_owner_setup.py:166`).
    동일 source 면제(2026-09-20 21:58 지시 + N22) — **이번 회차 제품 source를 바꾸지 않았다.**
    이것은 `make check`이며 **실제 앱/24k/144k 증거가 아니다.**

- **회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:**
  - 게임 실행 0인 회차가 lap492·493·494로 **3연속**이다. PROMPT③의 "제품 증거 무증가 연속 최대 2회"
    경계를 형식상 넘으나, §57이 Q6-C로 **이번 발행을 명시 허용**하고 그 판정 자체가 계속/중단 판단을
    겸했으므로 범위 위반은 아니다. **다음 work 회차의 게임 1회 실행은 의무**이며, 또 무실행이면
    strategy가 이 목표의 계속/중단을 먼저 판정해야 한다.
  - W28-R 실패 시 출구는 이미 닫혀 있다(R-5: Q6-B 자동 종결). 이번 카드로 §1 기전 질문이 열린 채
    종결될 위험이 남아 있음을 명시한다.
  - N135는 lap491 결과를 뒤집지 않지만, **fail-closed 장치가 꺼진 구간을 표본 재계산이 우연히 덮은
    것**이므로 W28-R에서 반드시 수리한다.
  - **미검증:** 정산 유닛의 사후 생존(tick1944 사망은 `used`−20이라 비용10 정산 유닛이 아니다),
    실제 게임 24k/144k 안정성, G2 제품 완료. **이 회차 자체는 다음 새 middle 세션의 독립 검수 대상이다.**
  - **환경 관찰(조작·정리 없음):** 게임 exe·wine 프로세스는 **0건**(이 회차 게임 실행 0). 살아 있는
    Xvfb는 `:77 :78 :103 :186 :187`이고 `/tmp/.X*-lock`은 `0 1 11 77 78 99 100 101 102 103 104 105
    107 186 187 256`이 점유 중이다. 기원은 이 루프 밖이며 AGENTS.md대로 붙거나 pkill 하지 않았다.
    lap491이 쓴 `:199`는 lock 해제 상태다. W28-R §6에 이 목록을 박아 다음 work가 충돌을 피하게 했다.
  - **source 변경 0 확인:** `patches/population/runtime_bridge.c` `2a3ad84bcd04a028…`,
    `tools/inmm_stub/control_executor.c` `40003d06f43a3c14…`, `tools/runtime_env.py` `7418dcdfd4391ad4…`
    — 전부 lap492가 기록한 값과 일치. git 항목은 `unborn` HEAD라 해당 없음.
  - (ㄴ)·lap404 (가)/(나)·F4 (B)/(C)·3단 사용자 마일스톤 승인은 전부 **사용자 전권 대기**. 모델 착수 금지.
  - 활성 카드: W28-R **1장**(W28은 승계 처리) ⇒ 최대 3개 규칙 충족.

- **다음 한 가지:** **work(Sonnet5/high)가 W28-R §4를 게임 1회·동기·foreground로 실행**한다
  (background 금지, 재시도 없음, 라벨 확정 금지). 그 뒤 middle이 원시만으로 재계산해 라벨을 확정하고,
  §8 조건을 충족하면 W26을 발행한다.
