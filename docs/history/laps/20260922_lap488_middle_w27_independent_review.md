# lap488 (middle, Claude Code claude-opus-5 / high) — W27 lap487 원시 독립 검수

- 날짜: 2026-09-22 KST
- lap: 488 (`loop/.lap_counter` 기준 runtime lap)
- 역할: middle(진단·계획·확인). 게임 코드 hands-on 수정 없음. 게임 실행 0.
- 목표: G2 — W27(`docs/work/active/G2_SETTLEMENT_RESUME_COUNTERFACTUAL_LAP486.md`)
  lap487 실행 산출물을 **원시만으로** 재계산해 라벨을 확정한다.
- 검수 대상 원시:
  `temp/Syw2plus_patch/g2_capacity/20260922_lap487_w27_settlement_resume_counterfactual/`
- 이번 회차 산출물:
  `temp/Syw2plus_patch/g2_capacity/20260922_lap488_middle_w27_review/`
  (`recompute_lap488.py`, `recompute_lap488_result.json`)

## 1. 검수 방법 (독립성 경계)

`recompute_lap488.py`는 다음만 읽는다:
`window_samples.json`, `positive_control_samples.json`, `supply_probe_call_log.json`,
세 이벤트 배열, 그리고 `run_summary.json` 중 **동기 기록된 원시 필드 블록**
(`op4_call1_result`/`op4_call2_result`/`owner0_after_op4_call*`/`source_sha_*`/`producer_a`)뿐이다.

**읽지 않은 것:** `run_summary.json`의 `verdict`·`reason`·`exception`,
work가 만든 `verify_lap487.py`·`verify_lap487_result.json`, lap487/484/485 서술.

원시 SHA256(이번 회차 재계산):
`window_samples` `75a1cb83…0011`, `positive_control_samples` `26ebcd7e…684f`,
`supply_probe_call_log` `42202061…7d4f`, 세 이벤트 배열 전부 `4f53cda1…2945`(= `[]`의 해시),
`run_summary` `e316b219…e386`, 실행 스크립트 `a5182ac3…5f1a`.

## 2. 측정 판정 — **ACCEPT**(재계산 불일치 1건, 판정 무영향)

카드 §5 AND 3조건을 원시만으로 재계산했다.

| 항목 | 출처(원시) | 값 |
|---|---|---|
| 전이 **전** 상태 | 엔진 자체 `op4_call2_result.after` @tick**1410** | `used 4980 · reserved 10 · count 5` |
| 전이 **후** 상태 | 독립 재읽기 `owner0_after_op4_call2` @tick **미기록** | `used 4990 · reserved 0 · count 6` |
| ① `reserved` 10→0 | 위 두 블록 | **충족** |
| ② `used` +비용(=10) | 4980→4990 | **충족** |
| ③ `count` +1 | 5→6 | **충족** |

⇒ **AND 3조건 전부 충족.** 값은 lap487 보고와 **일치**한다.

기타 재확인(전부 일치):
- **R2′ — op4 정확히 2콜.** 477콜 전수 op 히스토그램 `{0:470, 6:2, 1:2, 4:2, 7:1}`.
  콜#1 tick710 `{used70,reserved10}→{4995,10}`(`r7=4995`), 콜#2 tick1410 `{4995,10}→{4980,10}`(`r7=4980`).
- **R3 전제 5종**이 마지막 pre-call2 표본(tick1408)에서 동시 성립: `alive` · `progress==100` ·
  `reserved==10` · `command==15` · 주문 미정산. **충족.**
- **무결성 위반 0** — 260 window 표본 + 208 대조군 표본 + 477콜 before/after 전수:
  음수 0, int16 wrap 0, `reserved`는 `{0,10}`만, 라이브 `used` 최대 **4995 ≤ cap**,
  `used+reserved` 최대 **5005**(카드 §6이 사전 허가한 의도된 fixture).
- **producer A 생존(N115 의무)** — 260 표본 전부 `alive` · `hp 3600` · `owner 0` · `type 46`.
- **source 변경 0** — 원본 exe `b56986e0…a8ac` before==after, `runtime_bridge.c`
  `2a3ad84b…04df` before==after, `control_executor.c` `40003d06…1f5f` before==after.
- **op4 배제 핀 3종 현존** — `tools/runtime_env.py:5837` · `tests/test_g2_stock_stress.py:19` ·
  `tests/test_g2_eight_owner_setup.py:166`.
- 표적 **16 passed** · `SAFETY_PASS` · `CONTEXT_PASS`. 잔류 0(lap487의 display `:180`·wine 프로세스
  모두 부재. 남아 있는 Xvfb `:103`/`:77`·`test_build.sh`는 **형제 저장소 Syw2plus_re_loop** 소유라
  AGENTS.md대로 건드리지 않았다).

**불일치 1건(정정):** `run_summary`의 `positive_control_progress100_to_settlement_delay_ticks = 1`은
원시와 맞지 않는다. 대조군 원시 표본 207(tick **702**)은 `producer_progress==100` · `reserved 10→0` ·
`used 40→50` · `count 3→4`를 **같은 표본 안에서** 보여준다 ⇒ 측정된 지연은 **0 tick**이다.
스크립트가 표본 tick이 아니라 루프 종료 후 재읽기 tick(`pc_end_tick=703`)에서 뺀 정의 결함
(`w27_…py:454`)이다. **판정에는 영향이 없다**(0이든 1이든 `32×지연 < 200`이라 N124의
`T_block=200`이 그대로 지배한다). 오히려 아래 N127을 강화한다.

## 3. 해석 판정 — 라벨은 확정, **귀결(⇒H-gate 확정)은 REJECT**

### N126 — "동일 트랜잭션 창" 서술은 원시와 어긋난다(값은 불변, 문구만 정정)

lap487 기록·STATUS·INBOX는 3조건이 "동일 트랜잭션 창에서 전부 충족"됐다고 적었다.
원시는 그렇지 않다. **엔진이 op4 콜#2 안에서 스스로 읽은 사후 블록**(`op4_call2_result.after`,
tick1410)은 `{used 4980, reserved 10, count 5}` — **아직 재개 전**이다.
재개는 그 **다음**에 실행된 별도 `read_owner()`(`owner0_after_op4_call2`)에서만 보이고,
**그 재읽기의 tick은 기록되지 않았다**.
⇒ 정확한 서술: 전이의 전 상태는 엔진 사후 블록(tick1410), 후 상태는 **tick 미상의 단일 재읽기**이며,
**재개 지연은 UNKNOWN**이다. "트랜잭션 창 내부"라는 주장은 철회한다.

### N127 (결정적) — counterfactual이 풀어 줄 "막힌 주문"이 애초에 없었다

- 주문 A가 `progress==100`으로 관측된 window 표본은 **정확히 1건**(tick **1408**)뿐이다.
- op4 콜#2는 tick **1410**에 실행됐다 ⇒ **개입 전 체류 = 2 tick**.
- 카드가 §3에서 스스로 확정한 차단 임계는 **`T_block = 200 tick`**(N124) — 관측된 체류는 그 **1/100**이다.
- 게다가 이번 run의 대조군 progress100→정산 지연은 위 정정대로 **0 tick**이고, 대조군 표집 간격은
  평균 **3.35** / 최대 **4** tick이다 ⇒ **대조군은 ~4tick 미만의 지연을 원리적으로 분해하지 못한다.**
  A의 2 tick 미정산 구간은 **그 맹점 안에 통째로 들어간다.**

⇒ **이 run에는 "주문 A가 개입 전에 막혀 있었다"를 입증하는 측정이 없다.**
따라서 op4 이후의 정산은 (i) H-gate가 진짜 막힌 주문을 풀어 준 것과,
(ii) 애초에 막히지 않았고 정상 일정(0~4tick)대로 정산됐을 뿐인 것을 **구분하지 못한다.**
카드 §5의 "`SETTLEMENT_RESUMED_AFTER_HEADROOM` ⇒ **H-gate 확정**"은 전제 하나
(**발사 전 ≥`T_block` 차단 입증**)가 빠진 **불완전 추론**이다.

**이것은 lap487(work)의 잘못이 아니다.** work는 §4-6의 "progress100 +50tick 이내 발사"를
정확히 지켰다. 결함은 **lap486 middle이 발행한 카드 자체**(=이 역할의 자기 산출물)에 있다.
+50tick 창은 "주문이 종결되기 전에 발사한다"만 보장하고, 정산 정상 지연이 0~4tick인 이상
**차단이 드러나기 전에 개입하도록 강제**한다.

**정직하게 남기는 반대 방향 신호(약함):** tick **1409**의 op0 질의(id 476)에서 A는
`progress=100 · reserved=10 · used=4995 · count=5`로 **미정산**이었다. 대조군은
progress100-미정산 상태로 표집된 적이 없다. 다만 대조군 표집이 3~4tick이라 ≤2tick의
미정산 구간은 어차피 놓쳤을 것이므로, 이 1표본은 **차이를 입증하지 못한다.**

**교차 run 정황(측정 아님, 승격 금지):** lap483(W25)은 **동일 구성**(`used=4995, reserved=10`,
합 5005>cap)에서 표적이 progress100으로 **529tick 체류 후 생산 없이 종결**했다(N122).
동일 구성이 529tick 막혔다면 이번 A도 막혔을 개연성이 높고, headroom 복원 직후 생산이
성사된 것은 **H-place에 불리**하다(배치 실패가 원인이라면 장부 복원으로 유닛이 나올 이유가 없다).
그러나 이는 n=1 대 n=1의 **교차 run 추론**이고, 두 arm의 종결 양상이 실제로 달랐으며
(lap483=미생산 비균형 종결 / lap487=생산 성사), 루프 규칙상 과거 증거를 현재 확정으로
승격하지 않는다.

⇒ **종합: `H-gate 지지(약~중), 확정 아님.` 카드 §1의 질문은 여전히 OPEN이다.**

### N128 — R1 승계는 §5와 자기모순이며, "스크립트 버그"는 절반이 카드 결함이다

§5 R1 승계: op4 기록값에서 `used`가 엔진에 의해 이탈하면 `PRECONDITION_NOT_MET`
(`ledger_reverted_by_engine`). 그런데 §5의 재개 라벨은 **`used`가 정확히 비용만큼 증가**하는 것으로
정의된다. 즉 **재개 신호 자체가 R1 위반**이며, 카드 문언을 글자 그대로 읽으면
**재개 라벨은 도달 불가능**하다.
스크립트는 이 모순을 두 곳에 충실히 구현했다 — 즉시 사후 단언(`w27_…py:749`, 실제로 던진 곳)과
루프 내 R1′ 검사(:670-679, 예외가 없었어도 다음 표본에서 run을 끝냈을 것이다).
⇒ lap487 서술("스크립트 자체의 사후검증 버그")은 **절반만 맞다**: :749가 "어떤 변화도 금지"로
과도하게 엄격한 것은 사실이나, 모순의 뿌리는 **카드에 적혀 있었다**. 값 변화 없음, 귀속만 정정한다.

### N129 — 세 이벤트 배열은 증거가 아니다

`death_events` · `finalization_events` · `unbalanced_termination_events`는 전부 `[]`이며
SHA도 동일(`4f53cda1…` = `[]`의 해시)하다. 이들은 루프 **뒤**(:799-802)에서 기록되는데
:754의 `RuntimeError`가 append 경로 자체를 건너뛰었다. `window_samples`가 이를 뒷받침한다 —
`call2_fired=true`인 표본 **0건**, 마지막 표본 tick 1408.
⇒ **"빈 배열"을 "사건 0건"으로 읽으면 안 된다.** 정산 자체는 위 장부 원시로 확인되므로
`finalization_events` 공백은 모순이 아니라 **기록 누락**이다. 다만 §6의 **N120 관측 의무는
post-call2 구간에서 미이행**이다.

### N130 — §4-7의 ≥600tick 관측 창은 실행되지 않았다

`window_samples`: n=**260**, tick 712→1408, `call2_fired=true` 표본 **0건**, 평균 간격 2.687tick
(≤3tick 요건은 pre-call2 구간에서 충족). 카드가 요구한 **counterfactual 이후 ≥600tick 관측은
표본 0**으로 끝났다.
⇒ (a) 개입 후 주장은 **tick 미상의 단일 재읽기 1건**에 전적으로 의존한다.
(b) `NO_RESUME_WITHIN_WINDOW`는 평가 자체가 불가능했다.
(c) 이후의 비균형 종결·되돌림 가능성을 **배제하지 못한다**.
⇒ 엄밀히 말해 **§4는 1~6단계까지만 실행됐고 7단계는 미실행**이다.

## 4. 카드 처분

- **W27 → `CLOSED`.** 사전 고정 라벨 `SETTLEMENT_RESUMED_AFTER_HEADROOM`을 확정한다
  (§5 문언의 AND 3조건이 원시로 충족되므로 사후 완화·사후 강화 모두 하지 않는다).
- **단, 라벨에 붙은 귀결 "⇒ H-gate 확정"은 채택하지 않는다**(N127). 기록에 남기는 귀결은
  **"H-gate 지지, 확정 아님 / §1 OPEN"** 이다.
- `used`·`reserved` 기반 수치는 §51대로 계속 **"부분 증거"** 라벨을 강제한다.
- 이 결과를 cap 근접 안정성·G2 완료·W26 정량 근거로 **재사용 금지**(§51 R2′) — 그대로 유지.

## 5. strategy 회부 (`loop/ESCALATE_SOL` §53) — 이 회차가 판정하지 않는 2건

- **Q4. 교정된 counterfactual 재실행(W28)을 재승인할 것인가?**
  §51 Q3=F1은 "op4 **정확히 2콜**·재사용 금지"로 W27 **1장**에만 권한을 줬다. 재실행은 그 경계를 넘는다.
  교정 내용은 셋뿐이다: (1) 발사 조건을 "progress100 +50tick 이내"에서
  **"progress100 · 미정산 상태가 `T_block=200tick` 이상 지속됨을 관측한 직후"**로 바꾼다
  (=차단을 먼저 입증), (2) R1을 "**비용 +10 이외의** `used` 이탈만 `ledger_reverted_by_engine`"으로
  정정한다(N128), (3) 재읽기에 **tick을 기록**하고 §4-7의 ≥600tick 관측을 실제로 끝낸다(N126·N130).
  비용은 게임 1회이며, 성공 시 H-gate/H-place가 **결정적으로** 갈린다.
- **Q5. §8의 "W27 실행"이 충족됐는가?**
  §8(W26/144k 재개방)의 조건은 "W27 실행 + middle 측정 ACCEPT + 새 무결성 위반 0"이다.
  **측정 ACCEPT ✓ · 무결성 위반 0 ✓**이고 게임은 실제로 1회 돌았다. 그러나 §4는 **7단계가
  미실행**(N130)이라 "실행"의 해석이 갈린다. 144k 개방은 마일스톤급 경계이므로
  middle이 단독으로 열지 않고 회부한다. **Q5=예**이면 다음 middle 회차가 즉시 W26을 발행한다
  (§8이 요구하는 N120/N121/N123/N124/N125 명시 기재 + `used` "부분 증거" 라벨 강제를 그대로 싣는다).

## 6. 이번 회차 계수

- 게임 실행 **0** · 제품 코드 변경 **0** · source 변경 **0**(3자 일치) · 커밋 **0** ·
  새 의존성 **0** · 원본/참고 저장소 쓰기 **0**.
- 표적 테스트 **16 passed** · `SAFETY_PASS` · `CONTEXT_PASS` ·
  전체 `make check` **면제**(동일 source, 2026-09-20 21:58 지시 + N22 — 이번 회차 source 미변경).
- 새 발행 카드 **0**(Q5 회부 대기). 활성 카드 수 변화 없음(W27 CLOSED로 1 감소).

## 7. 다음 한 가지

**strategy(Astra/Fable5)가 §53 Q4·Q5를 판정한다.** Q4=승인이면 middle이 W28(교정 counterfactual)을
발행하고 다음 work가 게임 1회로 §1을 닫는다. Q5=예이면 middle이 W26(144k)을 함께 발행한다.
둘 다 부결이면 H-gate/H-place 병존(N123)을 미결로 고정한 채 G2 다른 축으로 회귀한다.

**(ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 여전히 사용자 전권 대기이며
모델은 착수하지 않는다.**

## 8. 변경 파일 해시 (LOOP_ALLOW_COMMITS=0 — 커밋 없음, uncommitted 보존)

| 파일 | SHA256 |
|---|---|
| `docs/STATUS.md` (98줄) | `1f3ee01b4d51102e03e64875214d3db4cfa6b1528515dc3364e98853e1690991` |
| `docs/feedback/INBOX.md` (400줄) | `d9ec8ac257d353370346c5ee20ceddf5fb423db4459e977e91d2a8df8e437ebd` |
| `loop/ESCALATE_SOL` (§53 추가) | `b22054320295c917cdce80fa306b23211d923fe37564102a5f1b254525e8cee3` |
| `docs/work/active/G2_SETTLEMENT_RESUME_COUNTERFACTUAL_LAP486.md` (→`CLOSED`) | `11f360751317f7a39008640addd9a5aff1be0c0ffec0c6e9aaa1367a845c77c8` |
| `docs/history/20260922_inbox_lap488_precompaction.md` (419줄) | `4ab21ca1ec058bbc04c71ce5a36e1e62d282e37985b7b0e99eebb282025f82c7` |
| `temp/.../20260922_lap488_middle_w27_review/recompute_lap488.py` | `b2de8a107c0935930a553b85961006732d50b68dc02d74cfade089f06cfa6ed9` |
| `temp/.../20260922_lap488_middle_w27_review/recompute_lap488_result.json` | `1d3744b458ae8f8fccc56c8a09bf0f47bdb5584ae795c6511bc3a0943ecac129` |

INBOX는 이번 추기로 408줄이 되어 400줄 상한을 넘었다. **삭제 없이** 압축 직전 전문을 위
precompaction 파일에 보존한 뒤, 이미 포인터화돼 있던 두 블록(lap425·427·428 계보,
lap423·429·438·440·442 운영 회수 계보)과 이번 lap488 추기 자체를 줄여 **400줄**로 맞췄다.
두 블록의 원문은 `20260921_inbox_lap449_precompaction.md`·`20260921_inbox_lap462_precompaction.md`와
위 lap488 스냅샷에 그대로 있다. 최종 게이트: `CONTEXT_PASS` · `SAFETY_PASS` · 표적 16 passed.
