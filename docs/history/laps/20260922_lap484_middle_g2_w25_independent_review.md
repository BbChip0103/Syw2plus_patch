# 2026-09-22 | lap484 | 목표 G2 (W25 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code claude-opus-5 / high, 중간계획·컨펌(middle).
  게임 실행 0(§47(iii)·§49 "재시도 없음" 준수), 제품 코드 0, source 변경 0, 커밋 0. 산출물은 문서와
  temp 재계산 스크립트뿐이다.
- 가설 / 검수 대상: lap483(work, Sonnet5)이 카드 `G2_SETTLEMENT_GATE_SEPARATION_PROBE_LAP480.md`
  §4+§8을 1회 실행해 얻은 라벨 `PRECONDITION_NOT_MET`과, 그 회차가 "사전 고정 3라벨 어느 쪽도 포섭하지
  못한다"며 middle로 넘긴 **tick1943 제4 패턴**(`used 4995→4985`·`reserved 10→0`·`count` 불변).
  검수 원칙: `run_summary.json`과 lap483 서술을 **판정 입력으로 쓰지 않고** 원시
  `window_samples.json` / `positive_control_samples.json` / `supply_probe_call_log.json` /
  `death_events.json` / `finalization_events.json`만으로 전수 재계산한다.

## 입력 원시 파일 SHA256 (재계산으로 직접 확인)

- `window_samples.json` `420dfe5eaa8d34b11715d60ed65cd524f0ea9607dbc57cf7e0cf4265fb469c52` (350표본, tick 719~3052)
- `positive_control_samples.json` `acca6f12c951fb46c3b769ee122e2b2efa6b090a7f0a6b4000541faced8fb500` (210표본, tick 8~709)
- `supply_probe_call_log.json` `aecd00949bcff30ed4c990f6f68232196a93d49dfcb0da1ed884a7044f15a7ae` (568건)
- `death_events.json` `fb6ea9d8e844b8f9f332e9e34afe19705f85cfe005b3e4c6ee39e057d3c664a7` (1건)
- `finalization_events.json` `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` (0건)
- `w25_settlement_gate_probe.py` `46f8da26be5221d7c19f8d31928b2fe97c828f3dda7a667ff9e520156bee4265`
- (대조 전용) `run_summary.json` `da8c026fa102da61531fa2b6c1daa7b46ad913dfa9e41c3d4b1df6c52e414442`
- source 불변 확인: `patches/population/runtime_bridge.c`
  `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`,
  `tools/inmm_stub/control_executor.c` `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`
  — 둘 다 lap483 기재값과 일치. 원본 exe `ORIGINAL_SHA256`
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변(`checks/safety.sh check`).

## 1. 측정 재계산 = **ACCEPT (불일치 0)**

원시만으로 재계산해 lap483이 적은 수치 전부가 일치했다.

| 항목 | lap483 기재 | lap484 재계산 | 판정 |
|---|---|---|---|
| 양성대조 L | 702 | op1 tick7 → 해소 tick709 = **702** | 일치 |
| window budget / stuck 임계 / op4 데드라인 | 5616 / 3510 / ≈175 | max(300,8L)=5616 / 5L=3510 / 0.25L=175.5 | 일치 |
| Order A 수락 | tick714 발행, +2tick 확인 | op1 tick714, 표본상 `reserved 0→10`·rice −800 | 일치 |
| op4 1콜 | tick717, `{70,10}`→`{4995,10}` | 호출 로그 그대로 | 일치 |
| 구성 상태 | `used+reserved=5005>cap5000` | 4995+10=5005 | 일치 |
| tick1943 전이 | used −10, reserved 10→0, count 불변 | 동일(350표본 전수 주사에서 전이 2건뿐) | 일치 |
| tick2270 사망 | count 5→4, producer A 생존 | used −10·count −1, A hp3600/alive | 일치 |
| 종료 | tick3052 A `hp=0` | 동일 | 일치 |
| finalization / death / safety | 0 / 1 / 0 | 0 / 1 / 0, 음수·랩 표본 0 | 일치 |
| 표적 테스트 | 167 passed | 재실행 **167 passed** | 일치 |

`SAFETY_PASS`, `CONTEXT_PASS` 재확인. 이번 회차 source 변경 0이므로 전체 `make check` 면제
(2026-09-20 21:58 지시 + N22).

## 2. 신규 실측 N119~N123

- **N119 (장부 의미론 원시 확정).** 세 경로의 장부 연산을 원시에서 직접 분리했다.
  · **수락**: `op1` before/after가 `used` 동일(tick7 40→40, tick714 70→70)이고 +2tick 뒤 표본에서
    `reserved 0→10`·rice −800. ⇒ **수락은 `used`를 올리지 않는다.**
  · **정산**(대조군 tick709): `reserved 10→0`, `used 40→50(+10)`, `count 3→4`, `cmd 15→1`.
  · **사망**(tick2270): `used −10`, `count −1`.
  · 비용: `op6` type46 건물이 `used +20`, type7 주문이 10.
  ⇒ `used`와 `reserved`는 **서로 독립 계정**이며, N112의 수락 규칙 `used+reserved+cost≤cap`은
  이중계상이 아니다. N68의 `used+reserved=5010`은 실제로 5,010 약정 상태다(N112 강화, 반증 아님).
- **N120 (비균형 차감).** tick1943 종결은 `reserved 10→0`과 동시에 `used −10`인데, **수락이 `used`에
  올린 적이 없는 비용**이다(N119). 같은 표본에서 `count` 불변·`finalization_events` 0건이므로 유닛은
  생산되지 않았다. ⇒ 종결 경로가 유닛 제거 경로와 같은 차감을 수행한 **비균형 연산**이며, 자연
  경로에서 같은 일이 일어나면 종결 1건당 **유령 headroom 10**이 생겨 `used`가 실제 구성보다 낮아진다.
  **이 run은 op4 desync fixture이므로 자연 경로 발생 여부는 UNKNOWN**이고, R2에 따라 수치를 안정성
  주장에 재사용하지 않는다.
- **N121 (정산 단계 국소화 + 임계 교정 결함).** 대조군은 `progress` 99→100과 정산이 **같은 표본
  (≤3tick)**에서 일어난다. 표적 arm은 tick1414에 `progress=100`에 도달한 뒤 `cmd=15`·`reserved=10`인
  채 **529tick 체류**하고 끝내 생산 없이 종결됐다(**≥176×**). 생산 속도 자체는 정상이다
  (0→100 소요 695tick vs 대조군 701tick). ⇒ 이상은 **생산이 아니라 정산 단계에 국소**하다.
  그런데 카드 §5의 `SETTLEMENT_BLOCK_REPRO` 임계 `5L=3510tick`은 "주문→해소" 지연 L로 잡은 값이고,
  옳은 대조 기준은 "progress100→정산" 지연(대조군 ≤3tick)이었다. **임계가 한 자릿수 이상 과대
  설정돼, 대조군 대비 176배 초과 신호가 null 라벨로 떨어졌다.** 사후 재라벨은 하지 않는다(사전 고정
  판정식 원칙). 다음 카드가 임계를 재교정한다.
- **N122 (사유 오귀속 정정).** lap483의 라벨 `PRECONDITION_NOT_MET`은 사전 고정 결정규칙을 문자
  그대로 적용한 결과로서 **유지**되지만, 기록된 사유 "producer A가 정산 전 사망(tick3052)"은
  **오귀속**이다. 주문은 tick1943에 이미 종결됐고 그 시점 A는 `hp=3600`·`alive=True`로 만전이었으며
  사망은 **1,109tick 뒤** 사건이다. 정정 사유 = `order_terminated_without_production_at_tick1943`.
  (N115 생존 계측 의무가 이 정정을 가능하게 했다 — 의무 자체는 이행 확인.)
- **N123 (N68 미재현 + 경쟁 가설 2).** 이 run은 **N68을 재현하지 못했다.** N68은 24k tick 내내
  `reserved`가 미해소인데 여기서는 529tick 뒤 종결됐다. 따라서 "정산이 cap을 재검사한다"만으로는
  N68을 설명할 수 없고, 최소 두 가설이 남는다.
  · **H-gate**: 정산이 `used+cost≤cap`을 재검사해 거부하고, 일정 시간 뒤 주문을 포기한다.
    지지 — 대조군과의 유일한 조작 변수가 장부(`used` 40 vs 4995, 실효 headroom 5 < 비용 10)이고
    이상이 정산 단계에만 국소(N121). 반대 — N68의 무기한 유지와 어긋나고, 순수 차단이라면 장부를
    건드리지 않아야 하는데 `used −10`이 실제로 일어났다(N120).
  · **H-place**: 배치/스폰 실패 타임아웃(주변 셀 부족 등)으로 주문이 포기됐다.
    반대 — 동일 type46 건물·동일 type7 주문이 대조군 anchor(10,10)에서는 즉시 성공했다.
    배제 불가 — 이 run에 배치 여유 계측이 없다(A anchor (20,10) 주변에 시드 유닛 5기).
  · 부수 미결: 수락 시 징수한 rice 800의 환급이 관측되지 않았다(창 전체 rice가 1,000,000 고정이라
    환급 없음인지 관측 불가인지 분해되지 않는다).
  · **결정적 판별자**는 값싸다 — 주문이 대기 중일 때 `used`를 cap 아래로 되돌리고 정산이 재개되는지
    보는 counterfactual. 다만 이는 **op4 2콜**이라 §49 R2(1콜 한정)를 넘으므로 strategy 판정 사항이다.

## 3. middle 판정

- **측정 ACCEPT (불일치 0).**
- **라벨: `PRECONDITION_NOT_MET` 유지**, 사유만 N122대로 정정. 사전 고정 판정식을 사후에 바꾸지 않는다.
- **해석 REJECT:** tick1943 전이를 §1("정산이 cap을 재검사하는가")의 **답으로 승격하지 않는다.**
  경쟁 가설이 2개 살아 있고(N123), 이 run은 N68을 재현하지 못했다.
- **확정된 것은 두 가지다:** (i) 수락/정산/사망의 장부 연산 분리(N119), (ii) 정산 단계에 국소한
  176배 지연과 미생산 종결, 그리고 그 종결의 비균형 `used` 차감(N120·N121).
- 카드 `G2_SETTLEMENT_GATE_SEPARATION_PROBE_LAP480.md`는 §7("라벨 확정 시 CLOSED")대로 **CLOSED**.
- **strategy 회부 2건**(`loop/ESCALATE_SOL`§50): Q2 = 144k(W26) 조건이 문자상 충족됐으나 N121
  임계 결함 위에서 여는 것이 맞는가. Q3 = 결정적 counterfactual을 위해 op4 2콜을 허용할 것인가.
  **middle은 둘 다 고르지 않는다.**

## 산출물

- `temp/Syw2plus_patch/g2_capacity/20260922_lap484_middle_w25_independent_review/`
  · `verify_lap483.py` SHA256 `4bb90903c2d61b37be5c99e4a586b4b1b492945b2985f5f4d631a27bcd0be4a8`
  · `recompute_report.md` SHA256 `acf3b08fef152168429b8daaaaed655a37ac85442e223557d7079c0a2af6ce92`
- 게임실행 0 · 제품코드 0 · source변경 0 · 커밋 0. 이 회차는 Wine/Xvfb를 기동하지 않았으므로 잔류
  프로세스 0(호스트에 남아 있는 다른 세션 소유 Xvfb는 AGENTS.md대로 건드리지 않았고 display `:211`은 없다).
- 커밋 없음(`LOOP_ALLOW_COMMITS` 기본0, 레포 unborn HEAD) ⇒ 변경 파일 SHA256으로 이력을 남긴다:
  · `docs/STATUS.md` `596e008c05eaa0443bfa0cac62ce8cf9749b3d4d68cfe9d2bde55b317a75f11d` (130줄)
  · `docs/feedback/INBOX.md` `1a5033eed7814239c37e482e2f1791b3c906ca0aaf06a03bc2de31212438b408` (400줄)
  · `loop/ESCALATE_SOL` `a8af9e62b4d8bfef9b9ea0a9ac892af0dafad267e00a8b63c4e19488302ef32a` (§50 추가)
  · `docs/work/active/G2_SETTLEMENT_GATE_SEPARATION_PROBE_LAP480.md`
    `5f205d98f36b576d29bba797cab3b90360a1a5248d62d088e392c9ff465aedb4` (상태만 CLOSED로, 본문 보존)

## 다음 한 가지

**strategy(Fable5 또는 Astra)가 `ESCALATE_SOL`§50의 Q2·Q3를 판정한다.** 그 전까지 work는
새 게임 실행에 착수하지 않는다. (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은
여전히 사용자 전권 대기다.
