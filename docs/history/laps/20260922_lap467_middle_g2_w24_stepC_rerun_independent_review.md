# 2026-09-22 | lap 467 | 목표 G2

**판정 한 단어: `STEP_C_INCONCLUSIVE` — lap466의 `RIDER_REPRO`를 ACCEPT하지 않는다(REJECT).**
W24 CLOSED·144k 금지 해제·lap404(가) 재심 종결은 **전부 판정하지 않는다.**

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(진단·계획·확인)**.
  게임 코드 hands-on 수정 0, 게임 실행 0, 커밋 0, source 변경 0(문서만).
- 가설 / 사용자 관찰: INBOX 2026-09-22 12:55 **N96**("lap466 `RIDER_REPRO`는 관찰창 부족으로
  성립하지 않을 수 있다")을 원시로 재확인하고, 확인되면 ACCEPT 대신 관찰창을 늘린 Step C
  재실행을 요구한다(새 카드 금지, W24 §5 유지).
- 예상 PASS / FAIL 조건 (재계산 **전에** 고정, `recheck467.py`에 그대로 구현):
  `RIDER_REPRO_SUPPORTED` ⟺ (관찰창 W ≥ 양성대조 해소지연 L) **그리고** (창 끝에서 producer가
  생산 중이 아님). 둘 중 하나라도 깨지면 `STEP_C_INCONCLUSIVE`.
- 변경 파일 / source fingerprint / 커밋: `docs/STATUS.md`, `docs/feedback/INBOX.md`,
  `loop/ESCALATE_SOL`(§41 추가), 이 lap 기록. 제품 코드/패치/테스트 **변경 0**. 커밋 0(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 직접 재해시
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(pin 일치, 1,032,192B).
  lap466 후보는 **내가 재유도**했다 — 원본에 `patches/population/fixed_supply_5000.py`의
  `patched_bytes()`를 메모리에서 적용해 `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`
  = run summary의 `candidate_sha256`와 **일치**, 바이트 차이는 `0x1B576~7`·`0x3FFD4~6`의 **5바이트뿐**
  ⇒ 차량이 **stock 1200 레이아웃 + cap 5000**임이 파일로 확정된다(§2-3 요구 충족).
- 실행 명령 / 로그 / 산출물 해시:
  `python3 recheck467.py` (비참조 재계산; lap466 서술 `w24_step_c_rerun.md`와 STATUS/INBOX 요약을
  입력에서 제외). 산출물 `temp/Syw2plus_patch/g2_capacity/20260922_lap467_middle_stepC_recheck/`
  (`recheck467.py`, `recheck467_output.json`). 판정 입력 3종 SHA256:
  `positive_control_samples.json` `afca96ca2429aeded347fa5bc82106f1d13308881f39dd7ddc1fbf48272e0a06`,
  `step_c_samples.json` `da39a97c12832ceeffd43145f3178eb2794fd06b5e79c1cdadde0ec0aad3ddc2`,
  `step_c_run_summary.json` `5beb90edfeb8fd91039311730a1f2962eea75378038456aa27c0aee192c9b81b`.
  Fast: `checks/safety.sh check`=`SAFETY_PASS`, `checks/context_limits.py`=`CONTEXT_PASS`,
  표적 `pytest -k "population or supply or fixed_supply or context_limits"` **11 passed**
  (이번 회차 source 변경 0이므로 INBOX 2026-09-20 21:58 규칙의 전체 게이트 면제 조건 충족).

## 측정값 / 판정

### 1. lap466이 실제로 고친 것은 고쳤다 (그 부분은 ACCEPT)

§40-2가 요구한 두 필수조건은 원시로 확인된다.

- **(a) producer가 진짜 생산 건물이고 성공한 호출로 생겼다.** `op6_building_result`는
  `ok:true`/`fixture_added:1`, producer는 slot1182·id132254·**type46**. lap462의 결함(실패한 op6가
  남긴 type7 잔여 슬롯)은 **재발하지 않았다.**
- **(b) 양성 대조가 진짜 발화하고 진짜 해소됐다.** 주문 직전(tick10) `reserved=0` → 첫 표본
  (tick11) `reserved=10` ⇒ **발화**. 417표본의 상태전이는 **정확히 1건**뿐이며 tick708에
  `(10,75,4) → (0,85,5)` ⇒ **해소**(`used`+10, `count`+1). producer는 같은 tick에
  `production_type:0→7, progress:0→100` ⇒ 독립 확증.
- **(추가, 내가 새로 확인) cap 근접 주문도 진짜 큐에 들어갔다.** 주문 직전 rice 999,200 → 첫 표본
  998,400 = **-800 rice 과금**, `reserved` 0→10, producer `production_type=7`. lap462 VOID의 사유
  ("주문이 애초에 안 걸렸을 가능성")는 이번 run에서 **배제된다.**

⇒ **방법론 결함 계열 중 producer·발화 축은 닫혔다.** 무효인 것은 아래 한 축뿐이다.

### 2. N96은 원시로 **확인된다** (그리고 수치가 조금 다르다)

| 항목 | 값 | 출처 |
|---|---|---|
| 양성대조 주문 tick | **10** | `op1_positive_control_result.tick_before` |
| 양성대조 해소 tick | **708** | 417표본의 유일한 전이 |
| **해소 지연 L** | **698 tick** | 708−10 |
| cap 근접 주문 tick | **713** | `op1_cap_adjacent_result.tick_before` |
| 마지막 관측 tick | **1,035** | `producer_query_final.tick_before` |
| **관찰창 W** | **322 tick** | 1,035−713 |
| **W / L** | **0.461** | — |

**W(322) < L(698)** 이므로 "65표본 내내 `reserved`가 10이었다"는 **고착의 증거가 아니다** —
정상 생산이 아직 끝나지 않은 상태와 **구분되지 않는다.** N96이 쓴 697은 첫 *표본*(tick11)
기준이고 주문 *발행*(tick10) 기준으로는 **698**이다(결론 불변, 오히려 1 tick 더 부족).

카드 W24 §5-4의 `≥300 tick` 요구는 **lap461이 L을 모르는 상태에서 쓴 수치**다. lap466은 그
문자를 지켰다(322≥300). 즉 **lap466의 절차는 옳고, 무효인 것은 카드의 창 길이 기준**이다
(lap465 §40-2가 lap462에 대해 내린 판단과 같은 구조, N77 선례와도 같은 부류).

### 3. **신규 N97 — 이 run은 "창이 모자랐다"를 넘어, 생산이 정상 진행 중이었음을 직접 보여준다 (결정적)**

`producer_query_final`(tick1,035)의 producer는
**`command:15, progress:46, production_type:7`** 이다.

- 이 run에서 관측된 `progress`의 의미는 같은 producer로 고정돼 있다: 유휴=**0**(tick8, 주문 전),
  완료=**100**(tick708, 해소 시점), cap 주문 직전에도 100(직전 생산의 종단값).
- tick1,035의 **46은 0도 100도 아니다** ⇒ 그 producer는 창이 끝나는 순간 **생산을 진행 중**이었다.
- **속도가 양성대조와 같다.** L=698 tick에 0→100이므로 0.143266 progress/tick. cap 주문 후
  경과 322 tick × 0.143266 = **46.13**, 실측 **46**. 같은 속도라면 완료 예정 tick은
  713+698=**1,411**이고 관측은 그보다 **376 tick 일찍 끝났다.**

⇒ 원시 산출물은 `RIDER_REPRO`(cap에 붙어 예약이 고착)를 **지지하지 않는다.** 보이는 것은
**저부하 때와 같은 속도로 정상 진행 중이던 생산**이며, 관측이 그 절반쯤(0.461)에서 끊긴 것이다.
동시에 이것은 `RIDER_NO_REPRO`(카드 §5의 "0 유지 또는 즉시 해소")**도 아니다** — 어느 라벨도
성립하지 않으므로 Step C는 **다시 판정 불가**다.

**한계 명시:** 양성대조 구간의 중간 producer 표본이 없어 progress의 **선형성은 가정**이다.
그러나 결론은 선형성에 의존하지 않는다 — `0 < 46 < 100`이라는 사실 하나로 "창 끝에서
생산이 진행 중이었다"가 성립하고, 그것만으로 고착 주장은 무너진다. 선형 일치(46 vs 46.13)는
독립적인 정황 보강일 뿐이다.

### 4. 판정

- **Step C = `STEP_C_INCONCLUSIVE`** — lap466의 `RIDER_REPRO` 라벨을 **판정 근거로 채택하지 않는다.**
- **W24 카드 = CLOSED 아님.** A 충족 / B 충족 / **C 미충족(2회 연속)** / D 충족·ACCEPT(lap465).
- **144k 발행 금지 = 유지.** §38 판정5의 해제 조건("카드 실행 + 독립검수 ACCEPT")이 성립하지 않았고
  이는 마일스톤 경계 판정이므로 middle이 단독으로 풀지 않는다.
- **lap404 (가)** — §38의 **잠정 채택을 번복하지도, 확정하지도 않는다.** 이번 run은 (가)에 대한
  **증거를 주지 않는다**(N83과 같은 이유: 판별에 필요한 관측이 성립하지 않았다). 되물음은
  **사용자 판단 대기 그대로**이며 모델이 대신 고르지 않는다.
- **N93 가설**(`reserved`가 주문 타입 단가를 따른다)은 이번 run에서 `reserved=10`·cost10 주문
  1건뿐이라 **판별되지 않는다**(관측만 보존).

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- **절차 위험(반복 3회째):** Step C는 lap462(producer 무효) → lap466(관찰창 무효)로 **연속 2회**
  방법론 결함으로 무효가 됐다. 세 번째 재실행은 아래 §다음 한 가지의 **사전 고정 조건**을
  실행 전에 코드로 박고 착수한다. 실패하면 같은 추측을 반복하지 말고 `RIDER_BLOCKED`로 정직 종료한다.
- **PROMPT ③ 제품 증거 회차 규칙:** lap465(middle)·lap467(middle)이 제품 코드 0회차이고 그 사이
  lap466은 게임 실행 1회차였다. 다음 회차는 **반드시 work(게임 실행 1회)** 이며, 그 다음에도
  제품 증거가 늘지 않으면 strategy 판정이 선행돼야 한다.
- **문서 예산:** 이번 갱신 후 `docs/feedback/INBOX.md` **393/400줄**, `docs/STATUS.md` **125/130**.
  다음 회차는 INBOX에 긴 항목을 추가하기 전에 원문 보존 압축(스냅샷 SHA·줄 수 기록)이 필요하다.
- 원본 SHA 불변, 참고/원본 저장소 쓰기 0, 잔류 wine/Xvfb 0(이번 회차 게임 실행 없음), 커밋 0.
  **uncommitted 파일 해시(`LOOP_ALLOW_COMMITS=0`):**
  `docs/STATUS.md` `be8070ca2b55ebd89869d04e1d2cfeb3dc0fea53d5dbde3d4a8327001177d679`,
  `docs/feedback/INBOX.md` `02fa663cd262a6c6a9e71fda9a6cc5e9f49de2910fd33b7a8bdff4df4d291a35`,
  `loop/ESCALATE_SOL` `b637f746f7a6cbfd0438651718c7319d42fe43d5314d98cfd71d5b913697f0c8`.
- 사용자 마일스톤 승인(3단)은 여전히 미착수 — 이 판정은 기술 컨펌이며 제품 승인이 아니다.

## 다음 한 가지 (work tier로의 명시 handoff)

**W24 §5 Step C 재실행 1건(3회차). 새 카드 금지, W24 §5 판정 라벨 유지.**
착수 전에 실행기에 아래를 **코드로 고정**하고, 실행 후 사후 조정하지 않는다.

1. **관찰창 ≥ 3×L = 2,094 tick** (cap 근접 주문 tick 기준). L은 **그 run의 양성대조로 다시 측정**하고
   (환경마다 달라질 수 있다) 창은 그 run의 L의 3배 이상으로 잡는다 — 2,094를 상수로 박지 않는다.
2. **producer를 주기적으로 질의**(op0)해 `(command, progress, production_type)` 시계열을 남긴다.
   장부(`used`,`reserved`)만으로는 고착과 진행을 구분할 수 없음이 이번에 확인됐다.
   **판별식(실행 전 고정 권고):** 창 안에서 `progress`가 **단조 증가하다 100에 도달하고 `reserved`가
   해소되면 `RIDER_NO_REPRO`**; `progress`가 **≥L tick 동안 증가하지 않은 채** `reserved`가 남으면
   **`RIDER_REPRO`**; 창이 끝났는데 `progress`가 0과 100 사이에서 **여전히 증가 중**이면
   **판정하지 말고 창 부족으로 정직 보고**한다(이번 lap466이 여기에 해당한다).
3. 방법론 조건 (a)(성공한 op6 type46 생산 건물) · (b)(양성 대조 선행 발화·해소)는 lap466대로 **유지**.
4. 부수로 N93 관측만 남긴다. 우회 패치·AI/생산 정책 변경 **금지**((ㄴ) 미승인).

**strategy/사용자에게 남는 것:** Step C 재실행이 독립검수 ACCEPT된 **뒤에야** W24 CLOSED·144k 해제를
판정한다. **(ㄴ)** G2 한정 최소 AI/설정 변경 허용 여부, lap404 **(가)/(나)**, F4 **(B)/(C)** 는
사용자 전권 대기 그대로이며 이번 회차는 어느 것도 대신 고르지 않았다.
