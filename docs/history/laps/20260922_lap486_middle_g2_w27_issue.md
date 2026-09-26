# 2026-09-22 | lap 486 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(중간계획·컨펌)**.
  게임 실행 0 · 제품 코드 0 · source 변경 0 · 커밋 0. 문서 + temp 재계산 산출물만.
- 가설 / 사용자 관찰: 가설 검증 회차가 아니다. `loop/ESCALATE_SOL`§51(lap485 strategy)이 지정한
  **W27 카드 발행 1회**와 PROMPT④-2 이전 바퀴 검수를 수행했다.
- 예상 PASS / FAIL 조건: (i) lap485 spot-check 주장이 원시에서 불일치 0으로 재현되면 ACCEPT,
  (ii) §51 경계(R2′·R3·임계 재교정·라벨 3종)를 빠짐없이 담은 W27 카드 1장 발행.

## 1. 이전 바퀴 검수 (PROMPT④-2) = ACCEPT (불일치 0)

lap485는 strategy 문서 회차(게임 실행 0)이므로, 그 판정이 딛고 선 lap483 원시 산출물을
**직접 재계산**했다. 입력은 원시 파일만이며 `run_summary.json`·lap483/484/485 서술은 쓰지 않았다.

- 재계산 스크립트 `recheck_lap485_spotcheck.py`, 산출물
  `temp/Syw2plus_patch/g2_capacity/20260922_lap486_middle_w27_issue/`.
- **원시 6종 SHA256 재계산 전부 일치:** `window_samples` `420dfe5e…`, `positive_control_samples`
  `acca6f12…`, `supply_probe_call_log` `aecd0094…`, `death_events` `fb6ea9d8…`,
  `finalization_events` `4f53cda1…`, 스크립트 `46f8da26…`.
- 창 350표본 tick 719~3052. **전수 주사 결과 장부 전이 정확히 2건** —
  tick1943 `{used4995,reserved10,count5}→{4985,0,5}`, tick2270 `{4985,0,5}→{4975,0,4}`(사망).
- op4 1콜 tick717 `{used70,reserved10}→{used4995,reserved10}`(`r7=4995`, `ok=true`).
- 표적 arm progress100 최초 tick1414 → 종결 tick1943 = **체류 529tick**.
- 대조군 progress100 표본과 정산이 **같은 tick709**(지연 0), L=702.
- 음수·랩 0표본, finalization 0건, death 1건.

⇒ **lap485 spot-check 주장은 전부 재현된다. §51 판정(Q2=E2 / Q3=F1)의 사실 기반은 성립한다.**

## 2. 신규 실측 2건 (임계 재교정 의무 수행 중 발견)

- **N124 — 대조군 지연 "0tick"은 표집 해상도 한계값이다.** 대조군 표집 간격이 3~4tick이므로
  참 지연은 `[0,4)`에서만 알 수 있고 0으로 확정된 값이 아니다. 따라서 §51이 예시한
  `max(32×대조지연, 절대200tick)`의 **곱셈항은 0으로 퇴화**하며 절대 하한이 임계를 지배한다.
  곱셈항을 해상도 상한 4tick으로 읽어도 `32×4=128<200`이라 결론 동일.
  ⇒ **확정 임계 `T_block = 200tick`**(W27 §3에 고정).
- **N125 — N121(임계 교정 결함) 확증.** `T_block=200`을 W25에 소급 적용하면 lap483 표적 arm은
  **tick1414~1936의 79표본 전부** `alive=true`·`hp=3600`·`progress==100`·`command==15`·
  `reserved==10`·`used==4995`·`order_a_finalized=false`를 유지했고(lap486 신규 전수 확인),
  체류 522tick은 임계를 **2.6배 초과**한다. ⇒ W25가 null(`PRECONDITION_NOT_MET`)로 떨어진 것은
  정산 차단이 없어서가 아니라 **임계 `5L=3510`이 과대했기 때문**임이 원시로 확증된다.
  이는 §51 Q2=E2(144k 계속 닫음)의 근거를 **강화**한다 — 문언 충족만으로 W26을 열었다면
  교정 결함을 통과 근거로 바꾸는 것이었다.

두 건 모두 §51이 middle에게 위임한 "임계 재교정" 범위 안이며 strategy 판정을 뒤집지 않는다.
⇒ **새 strategy 회부 없음.**

## 3. 발행물 — W27 카드

`docs/work/active/G2_SETTLEMENT_RESUME_COUNTERFACTUAL_LAP486.md`, 상태 `READY_FOR_WORK`.

§51 경계를 카드에 고정한 방식:
- **R2′**: op4 **정확히 2콜**(§4-4 구성 1 + §4-6 counterfactual 1), 스크립트 temp 전용,
  source 변경 0, 핀 3종 유지, "장부 구성 fixture" 라벨·재사용 금지.
- **R3**: counterfactual은 A `alive`·`progress==100`·`reserved==10`·`command==15`·주문 미정산일 때만,
  **progress100 최초 확인 +50tick 이내** 발행. 놓치거나 이미 종결이면
  `PRECONDITION_NOT_MET` 1회 종결(사유 `counterfactual_window_missed` /
  `order_terminated_before_counterfactual`), 재시도 없음.
- **임계**: `T_block = 200tick` 확정(N124 근거 명기).
- **라벨 3종 고정**: `SETTLEMENT_RESUMED_AFTER_HEADROOM` / `NO_RESUME_WITHIN_WINDOW` /
  `PRECONDITION_NOT_MET`. 1회 종결.
- **N114 수리·N115 생존 계측·N120 관측 의무** 승계, **R1**(`ledger_reverted_by_engine`) 승계.
- §8에 **W26 재개방 조건**(W27 실행 + 측정 ACCEPT + 무결성 위반 0 ⇒ 라벨 무관 발행 가능,
  N120/N121/N123/N124/N125 명시 + `used` 수치 "부분 증거" 라벨 강제)을 운반.

middle이 카드에서 새로 확정한 실행 세부 3건:
1. **counterfactual 목표값 `used = 4980`** (`used+비용 = 4990 ≤ cap`, 여유 10).
2. **재개 판별자는 AND 3조건** — `reserved` 10→0 **그리고** `used` +비용 **그리고** `count` +1.
   `reserved`만 0으로 내려가고 `count`가 불변인 전이는 재개가 아니라 W25 tick1943과 같은
   **비균형 종결**(N120)이므로 `NO_RESUME_WITHIN_WINDOW`로 보낸다. 이 구분이 없으면 H-place
   결과가 H-gate로 위양성 판정될 수 있다(W25에서 실제로 그 모양의 전이가 나왔다).
3. **pending 구간 표집 간격 ≤3tick**(W25 창은 6~7tick), counterfactual 이후 **≥600tick**
   (=3×`T_block`, W25 종결 시점 tick1943을 덮는다) 관측.

- 변경 파일 / source fingerprint / 커밋: 신규 `docs/work/active/G2_SETTLEMENT_RESUME_COUNTERFACTUAL_LAP486.md`,
  본 lap 기록, `loop/ESCALATE_SOL`§52, `docs/STATUS.md`, `docs/feedback/INBOX.md`.
  **제품/실행 source 변경 0**(문서 + temp 재계산 산출물만) — `tools/`·`patches/`·`tests/`·`checks/`·
  `Makefile`·`pyproject.toml`에 이번 회차 수정 파일 0건으로 확인. 커밋 0(`LOOP_ALLOW_COMMITS` 미설정)
  이므로 **uncommitted 파일 해시**를 남긴다:
  · 카드 `47995dbb8645b2853c8bab9bf59acfd901668f8f0659b2e6bd11e2d7028d1d83`
  · 본 lap 기록(이 줄 기재 전 상태) `c4f78e2aac1f21aaa8dc048e8bca2dc246fa642a7c3cbf971890783c0271b442`
  · `docs/STATUS.md` `bead7bb0f95b0a09f62cdf9a3ee77170b4c8ba9e79f9979973e06a1270223d12`
  · `docs/feedback/INBOX.md` `6f7c1223c5d4a68990a784c4d1a9f7c5a242d212186ec5c56e0878daa9b348b3`
  · `loop/ESCALATE_SOL` `a00a9b1596d916a01ee06f8dd84d419d49fbd63fcceb766198575d58e7931014`
  · 재계산 스크립트 `49cc469aca3ae53655b3665a7622e9f2a5b0989893717c3f8f87a547c2408d46`
  · INBOX 400줄 상한 초과(404)로 압축하며 압축 직전 전문을
    `docs/history/20260922_inbox_lap486_precompaction.md`
    (SHA `f1054f354b7953536a6c0a416c6ab8d45ade4c3a8c0ced418e11ff41632ad4c9`, 404줄)에 보존했다.
    줄인 것은 lap469~471 계보 서술뿐이며 원문은 그 스냅샷과 각 원 lap 기록에 그대로 있다.
- 원본 SHA / 후보 SHA / 환경 / fixture: 이번 회차 게임 미실행이므로 해당 없음.
  검수 대상 run의 fixture·SHA는 위 §1 원시 6종에 그대로.
- 실행 명령 / 로그: `python3 recheck_lap485_spotcheck.py`(temp),
  `./checks/safety.sh check` → `SAFETY_PASS`, `python3 checks/context_limits.py` → `CONTEXT_PASS`,
  `python3 -m pytest tests/test_g2_stock_stress.py tests/test_g2_eight_owner_setup.py -q` → **16 passed**
  (op4 배제 핀 3종을 grep이 아니라 테스트로 현존 확인).
  동일 source이므로 전체 `make check` 면제(2026-09-20 21:58 지시 + N22, **이번 회차 source 변경 없음**).
- 측정값 / 판정: 이전 바퀴 검수 **ACCEPT(불일치 0)**. W27 발행 **완료**. 신규 N124·N125.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  · **제품 미완료.** 이 회차는 게임 실행 0이며 G2 증거를 늘리지 않았다.
  · lap484·485·486 **3회 연속 무실행** ⇒ §51 처분대로 **다음 work는 W27 게임 1회 실행이 필수**다
    (PROMPT③ 연속 무증거 회차 상한). 발행은 이 1회로 끝이며 재계획으로 되돌리지 않는다.
  · H-gate/H-place는 여전히 병존(N123). N120 비균형 차감의 자연 발생 여부 UNKNOWN.
  · (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 마일스톤 승인은 전부 **사용자 전권 대기**.
- 다음 한 가지: **work(Sonnet5)가 W27 §4를 게임 1회 실행**한다(background 금지, 동기 완주).
