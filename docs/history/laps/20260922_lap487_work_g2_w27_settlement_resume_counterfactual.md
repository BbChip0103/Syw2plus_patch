# 2026-09-22 | lap487 | 목표 G2 (W27)

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5 / high, work(실무·실행) 역할.
- 가설 / 사용자 관찰: 카드 `docs/work/active/G2_SETTLEMENT_RESUME_COUNTERFACTUAL_LAP486.md` §4 —
  W25에서 관측된 "progress100 대기 중 미정산" 상태가 H-gate(정산이 cap을 재검사하고 대기)인지
  H-place(배치/스폰 실패 타임아웃)인지, `used`를 `cap-비용` 아래로 되돌리는 counterfactual op4
  2번째 콜로 판별한다. 사전 고정 라벨 3종(§51/§52 승계): `SETTLEMENT_RESUMED_AFTER_HEADROOM`
  (AND 3조건: `reserved`10→0 ∧ `used`+비용 ∧ `count`+1) / `NO_RESUME_WITHIN_WINDOW`(T_block=200tick
  이상 미해소 또는 비균형 종결) / `PRECONDITION_NOT_MET`.
- 예상 PASS / FAIL 조건: 위 3라벨 중 정확히 하나로 1회 종결(재시도 없음). op4는 정확히 2콜
  (구성 `used=4995` + counterfactual `used=4980`)만 사용.

## 실행 요약

카드 §4 절차를 그대로 구현한 신규 스크립트
`temp/Syw2plus_patch/g2_capacity/20260922_lap487_w27_settlement_resume_counterfactual/w27_settlement_resume_counterfactual.py`
(lap482 W25 스크립트의 환경/goal/안전 골격을 복사, source 미수정)를 **게임 1회, 동기, foreground로
완주**했다(background 미사용, PROMPT③·2026-09-21 01:01 지시 준수).

1. 후보 기동 → PS3(`cap=5000` 확인) → op7로 rice/wood 1,000,000.
2. 양성 대조(PC producer, op6 type46 + op1 type7): `L=696tick`, progress100→정산 지연 **1tick**
   (이번 run 자체의 §3 임계 재확인, N124 해상도 한계값 논리와 일치).
3. 표적 producer A(op6 type46)에 낮은 `used`(headroom 4930)에서 op1 주문, N107 5중 신호로
   수락 확인(tick708, `reserved`0→10 ∧ rice −800).
4. **op4 콜 #1(구성)**: tick710(주문 후 3tick, 데드라인174tick 이내) `used=4995`(rice/wood 보존)
   ⇒ `used+reserved=5005>cap`(W25와 동일 구성) 확인.
5. **≤3tick 조밀 표집**(poll 0.03s)으로 진행 — 259표본, tick710~1408. producer A는 tick1408에
   `progress=100` 최초 도달, 그 시점 표본이 `alive=true, hp=3600, command=15, reserved=10,
   used=4995, order_open=true`로 R3 전제 5종을 전부 충족한 상태를 직접 기록했다(사전 확인 없이
   즉시 발행 조건 성립).
6. **op4 콜 #2(counterfactual)**: progress100 최초 확인과 **동일 tick(+0tick, 50tick 창 이내)**에
   즉시 발행, `used=4980`(`used+비용=4990≤cap`). 엔진 자체 원장 문자열(before/after, 확률·재시도
   없이 op4 호출 트랜잭션 내부에서 동기 기록)은 `before={reserved:10,used:4995}` →
   `after={reserved:10,used:4980}`로 **쓰기 자체는 요청대로 정확히 반영**됐다.

## 스크립트 결함과 원시 증거의 실제 판독 (중요)

호출 직후 스크립트 자체의 사후검증 코드가 `read_owner()`로 다시 읽은 값
(`owner0_after_op4_call2` = `{reserved:0, count:6, used:4990}`)을 콜 #2가 쓴 값(4980)과
**단순 불일치로 취급해 `RuntimeError`를 던졌다** — "정산이 콜 #2와 같은 트랜잭션 창 안에서
즉시 재개될 수 있다"는 가능성을 예견하지 못한 **스크립트 버그**다(카드가 요구한 실험 조건의
실패가 아니라 사후검증 단언문의 설계 결함). 이 예외 때문에 스크립트 자신의 `run_summary.json`
자동 `verdict`는 `PRECONDITION_NOT_MET`(사유 `"op4 call #2 wrote used=4990, expected 4980"`)로
**잘못** 기록됐다.

그러나 예외 발생 **이전에 이미 원시 파일에 동기 기록된** 두 값(`op4_call2_result`의
엔진 자체 before/after 원장 + `owner0_after_op4_call2`의 독립 재읽기)만으로 카드 §5의
사전 고정 AND-판정을 기계적으로 재계산하면 명확하다:

| | reserved | used | count |
|---|---|---|---|
| 콜#2 쓰기 직후(엔진 자체 기록) | 10 | 4980 | 5 |
| 그 직후 독립 재읽기 | **0** | **4990** | **6** |

`reserved` 10→0 **그리고** `used` 4980→**4990(+10=주문비용)** **그리고** `count` 5→**6(+1)** —
카드 §5 `SETTLEMENT_RESUMED_AFTER_HEADROOM`의 AND 3조건을 **동일 트랜잭션 창 안에서 전부**
충족한다. 재계산 스크립트
`temp/Syw2plus_patch/g2_capacity/20260922_lap487_w27_settlement_resume_counterfactual/verify_lap487.py`
가 `run_summary.json`의 `verdict`/`reason` 필드를 전혀 참조하지 않고 이 두 원시 기록 + 콜#2
직전 마지막 `window_samples.json` 표본(R3 전제 확인용)만으로 동일 결론을 재현한다
(`verify_lap487_result.json`).

**이 work 회차의 읽기 제안(확정 아님, middle 독립검수 대상):** 원시 증거는
`SETTLEMENT_RESUMED_AFTER_HEADROOM`을 가리킨다 — **H-gate 지지**: 정산은 `used+비용≤cap`을
재검사하며, headroom이 회복되는 순간(다음 tick 경계를 기다리지 않고 같은 처리 창 안에서)
즉시 재개된다. 스크립트 자신의 `verdict` 필드는 **틀렸다**(사후검증 버그) — middle은
`run_summary.json`의 `verdict` 문자열을 그대로 승격하지 말고 `verify_lap487.py`의 재계산을
독립적으로 재현해야 한다.

## 변경 파일 / source fingerprint / 커밋

- 저장소 source 파일 변경 0: `source_sha_before == source_sha_after` (`b56986e0…8a8ac`),
  `runtime_bridge.c` sha `2a3ad84b…d04df` before/after 일치, `control_executor.c` sha
  `40003d06…3701f5f` before/after 일치, `tools/runtime_env.py` op4 배제 핀 확인 유지
  (`"op4_used": False`), `tests/test_g2_stock_stress.py:19`·`tests/test_g2_eight_owner_setup.py:166`
  핀 문자열 그대로.
- 새 파일은 전부 `temp/Syw2plus_patch/g2_capacity/20260922_lap487_w27_settlement_resume_counterfactual/`
  (repo 밖): `w27_settlement_resume_counterfactual.py`, `verify_lap487.py`, `run_summary.json`,
  `window_samples.json`, `positive_control_samples.json`, `death_events.json`(빈 배열),
  `finalization_events.json`(빈 배열 — 정산 전이가 예외로 인해 루프의 정상 append 경로를
  타지 못했다, 위 표 참고), `unbalanced_termination_events.json`(빈 배열),
  `supply_probe_call_log.json`, `orchestrator.log`, `verify_lap487_result.json`, `bridge_build/`.
- 커밋: 없음(uncommitted, `LOOP_ALLOW_COMMITS` 기본0).

## 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture

- 원본 `syw2plus_original.exe` sha256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (실행 전후 일치). 후보 `fixed_supply_5000` sha256 `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`.
  bridge dll sha256 `0c59d964aabeb96da1577eebab33467ea5dee2c028574e032e296a64988aba63`.
- goal `_custom_game_chain_inject_g2_eight_seed42`(8인 비-AI 체인), 격리 Wine prefix, Xvfb `:180`
  (실행 후 정상 정리 확인, 잔류 프로세스/락 0).
- fixture 라벨: `ledger_construction_fixture_op4_R2prime_exactly_2_calls_mechanism_probe_not_g2_stability_proof`
  — 카드 §1·§6 요구대로 이 결과를 G2 cap-근접 안정성/제품 완료/W26 정량 근거로 재사용하지 않는다.

## 실행 명령 / 로그 / 캡처 경로 및 해시

```
python3 temp/.../w27_settlement_resume_counterfactual.py --display :180
python3 temp/.../verify_lap487.py
```
로그: `temp/Syw2plus_patch/g2_capacity/20260922_lap487_w27_settlement_resume_counterfactual/orchestrator.log`.
raw SHA256: run_summary.json `e316b219…a012e386`, window_samples.json `75a1cb83…9ade0011`,
positive_control_samples.json `26ebcd7e…d0684f`, supply_probe_call_log.json `422020612…dffa7d4d`,
death/finalization/unbalanced_termination_events.json 전부 `4f53cda1…161202b945`(빈 배열 공통),
스크립트 자체 `a5182ac3…191f25f1a`.

## 측정값 / 판정

- **스크립트 자동 verdict(그대로 기록, 신뢰 금지): `PRECONDITION_NOT_MET`** — 사후검증 버그로 오판정.
- **원시 재계산(`verify_lap487.py`) 결과: `SETTLEMENT_RESUMED_AFTER_HEADROOM`** — AND 3조건
  전부 충족(`reserved`10→0, `used`+10, `count`+1), R3 전제 5종 전부 콜#2 직전 표본에서 확인,
  안전(음수·랩) 위반 0.
- targeted `test_g2_stock_stress.py`+`test_g2_eight_owner_setup.py` **16 passed**, `checks/safety.sh check`
  → `SAFETY_PASS`, `checks/context_limits.py` → `CONTEXT_PASS`. source 미변경이라 전체
  `make check`는 면제(2026-09-20 21:58 + N22, 이번 회차 source 변경 없음 명시).
- death_events/finalization_events(정상 루프 경로)/unbalanced_termination_events는 전부 빈
  배열 — 정산 전이 자체는 위 표처럼 원시 필드에서 직접 확인했지만, 루프의 정상 표본-append
  경로(다음 반복에서 비교) 이전에 예외로 종료됐기 때문에 이벤트 목록에는 별도로 기록되지
  못했다. **이 공백은 middle 재현 시 명시할 결함이다.**

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- **스크립트 자체 버그(재사용 시 반드시 수리):** op4 콜 #2 직후의 `if call2_after_read["used"]
  != OP4_COUNTERFACTUAL_USED: raise`가 "쓴 값이 즉시 다른 값으로 바뀔 수 있다(=정산 재개 자체가
  응답)"는 이 카드의 핵심 가설을 스스로 배제하는 설계였다. 향후 유사 카드는 콜 직후 검증을
  "쓴 값 그대로"가 아니라 "쓴 값 **또는** 정산-후 AND-조건을 만족하는 값"으로 완화해야 한다.
- **이 work 회차는 라벨을 확정하지 않는다.** `SETTLEMENT_RESUMED_AFTER_HEADROOM` 읽기는 원시
  기록 2건(엔진 자체 before/after + 독립 재읽기)의 기계적 AND-판정 재현이며, 카드 §7이 요구하는
  **middle 독립 검수**(원시만 재계산, `verify_lap487.py` 독립 재현 포함)를 거쳐야 `CLOSED`다.
- W26(144k) 재개방은 §51/§52(Q2=E2, 카드 §8) 조건 그대로 — 이번 회차 스스로는 발행하지 않는다.
  N120·N121·N123·N124·N125 미결 위험 명시 의무는 다음 W26 발행 시 그대로 승계된다.
- (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 여전히 사용자 전권 대기, 이번
  회차 착수 없음.

## 다음 한 가지

**middle(중간계획·컨펌, Opus5/Fable5)이 이 lap487 원시 산출물만으로 독립 재검수**한다:
(1) `verify_lap487.py`를 원시 파일(run_summary.json의 verdict 필드 미사용)로 독립 재현,
(2) 스크립트 버그로 인한 `finalization_events.json` 공백을 원시 필드(`op4_call2_result`+
`owner0_after_op4_call2`)로 보완 확인, (3) R3 전제 5종·AND 3조건·안전 위반 0을 재확인,
(4) 라벨 확정 시 카드 §7대로 `CLOSED`, (5) `H-gate` 확정이면 §8(W26 재개방 조건 = 이번 실행 +
측정 ACCEPT + 무결성 위반 0, 이미 충족) 적용 여부와 N120/N121/N123/N124/N125 "부분 증거" 라벨
의무를 실은 W26 발행 여부를 strategy 없이 §51 위임 범위 내에서 판단.
