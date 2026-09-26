# G2 owner-transfer cap — middle 판정과 work handoff (lap389)

발행: lap389 middle (Claude Code claude-opus-5 / high), 2026-09-19 KST
근거 원문: `docs/history/laps/20260919_lap389_middle_g2_owner_transfer_cap_judgment.md`

## A. 닫는 카드 — NO_GO

STATUS「다음 한 가지」가 예고했던 **0x476ED0 transfer 사전거부 최소패치**는 **NO_GO**다.
Sonnet5/high는 이 패치를 착수하지 않는다. 근거는 셋이며 모두 원본 바이트다:

1. `0x476ED0`은 단일 exit(`ret` 1개 @`0x477016`)로 **항상 `mov eax,1`**(@`0x477010`)을 반환하고,
   직접 caller **5개 전부가 반환값을 소비하지 않는다**(`0x4082E5 0x40F8AC 0x47716E 0x477295 0x47795D`).
   거부 반환 패치는 동작상 no-op이다. → STATUS가 지정한 NO_GO 조건에 해당.
2. `0x43EE30`(신 owner roster 등록 + `add word [ecx+0x200C]`)에 cap 비교를 넣는 안은
   이 함수가 비-transfer caller `0x48BCFE`와 공유되므로 **금지**다. 조용한 거부는
   "월드에는 있는데 roster/장부에는 없는" 불일치를 만든다.
3. caller 5곳 사전검사 후 skip은 **정상 game semantics를 깬다**. 다섯 곳 모두 되돌릴 수 없는
   부작용(상태기계 진행·자원 차감·이펙트) 뒤에 호출하며, `FUN_00444EF0`(패배 owner의 전 유닛 일괄
   흡수)를 건너뛰면 더 나쁜 상태가 된다.

추가로: `used > cap`은 **원본 설계상 허용 상태**다. cap `+0x2012`는 생산 admission gate
(`0x43EDA0`)의 입력일 뿐이고 transfer 경로에는 cap 참조가 0건이다. 강제하면 그것은
버그 수정이 아니라 **정책 변경**(점령이 cap 근처에서 실패)이며 숨기지 않고 기록했다.

## B. 승격 판정 대기 (`loop/ESCALATE_SOL`, Astra/사용자)

**F4:** 전비 장부 `+0x200C`는 16-bit이고(`0043EE9B add word ptr [ecx+0x200C], dx`)
생산 gate가 **부호있게** 읽는다(`0043EDFC movsx` / `0043EE03 movsx`, `cmp/jle` @`0x43EE0F`).
도달 범위는 `[-32768, 32767]`인데 **9/19 run의 실측 전역 used 합은 첫 sample 40,000**(=8×5000)이다.
`32767 − 40000 = −7233`. 한 owner에 충분히 집중되면 word가 음수로 랩하고,
그 순간 생산 gate가 항상 참이 되어 전비 제한이 사실상 해제된다.
원본 cap 1500에서는 `8×1500=12000`, 여유 `+20767`이라 도달 불가였다.

⇒ **"8인 각 5000"이라는 숫자 자체가 원본 장부 폭과 충돌한다.** 합격 기준을
`used<=cap`으로 둘지 `생산 gate 무결성 + 장부 랩 없음`으로 둘지는 middle 권한 밖이다.

## C. 지금 착수 가능한 work 카드 (승인 불필요, 관측 전용)

**카드 W1 — F4 랩 도달성 실측. CLOSED(lap390 work, NOT_FEASIBLE, 이 fixture 한정).**
담당: Sonnet5/high (work tier). 결과: M1 음수0, M2 단일owner used 최대5,003(32,767까지
여유27,764), M3(roster0-전환+타owner used점프) 0건, M4 전역합 40,000→35,427(lap389와 일치).
**F4 산술 가능성(lap389)은 그대로 유효**하나 이 자연 시뮬레이션 24k tick 구간에서는 랩이
관측되지 않았다. 랩을 실제 트리거하려면 `FUN_00444EF0`(패배 owner 일괄흡수) 반복 유도
fixture가 별도로 필요하다(이번 카드 범위 밖). 상세 `docs/history/laps/20260920_lap390_work_g2_ledger_wrap_reachability.md`,
산출물 `…/temp/Syw2plus_patch/g2_capacity/20260919_owner_transfer_cap/lap390_work_ledger_wrap_reachability/`.
B의 F4 합격기준 판정(Astra/사용자)은 대체되지 않는다 — `loop/ESCALATE_SOL` 유지.

<details><summary>원문 카드 정의(참고용, 보존)</summary>

- 목적: F4가 산술상 가능함은 확정됐다. **실제로 한 owner의 used가 32,767을 넘을 수 있는가**를
  측정해 `FEASIBLE`(랩 재현) / `NOT_FEASIBLE`(도달 불가) / `BLOCKED`로 닫는다.
- **바이너리·제품코드 변경 0.** 기존 관측 하네스만 쓴다. 새 patch builder 금지,
  기존 frozen builder 수정 금지, 원본/reference/shared 쓰기 금지, global kill/서비스/커밋 금지.
- 입력 fixture: 9/19와 **같은** 8×used5000 load
  (`…/g2_capacity/20260919_eight_owner_5000_stability_actual_v1/approved_inputs`, 핀 재해시 필수).
- 측정식(성공/실패를 먼저 고정한다):
  - M1. 매 sample 8인의 `used`를 **부호있는 16-bit로 해석**해 기록하고, 음수가 1회라도 나오면 랩 **재현**.
  - M2. 관측 구간 전체의 **단일 owner used 최대치**와 그 tick. 9/19 기준선은 5,003이다.
  - M3. `FUN_00444EF0`(일괄 흡수) 도달 여부의 **간접 증거**: 한 sample에서 다음 sample 사이에
    어떤 owner의 roster count가 0이 되고 다른 owner의 `used`가 그만큼 뛰는 사건의 유무·횟수.
  - M4. 대조: 전역 used 합이 40,000에서 어떻게 움직이는지(9/19는 40,000→35,427).
- 판정:
  - M1이 음수를 보이면 → **랩 CONFIRMED**. 즉시 중단하고 기록만 남긴다(수리 착수 금지, B의 판정 대기).
  - M1 음수 0 & M2가 32,767에 크게 못 미치며 M3 사건 0 → **현재 fixture에서 NOT_FEASIBLE**로 기록하고
    "어떤 시나리오라야 집중이 일어나는지"를 한 문단으로 남긴다.
  - 관측 수단이 부족하면 **BLOCKED**로 즉시 보고한다. 추정 패치 금지.
- 시간 상한: 한 work 회차 또는 60분 중 먼저 도달한 시점.
- 산출물: 외부 temp
  `…/temp/Syw2plus_patch/g2_capacity/20260919_owner_transfer_cap/lap<N>_work_ledger_wrap_reachability/`
  + `docs/history/laps/` lap 기록. cleanup 잔류 0, owned PID만 정리.

</details>

## D. work tier가 **하지 말아야 할 것**

- `0x476ED0`/`0x43EE30`/`0x43EEC0`/`0x43EDA0` 어디에도 바이트를 쓰지 않는다.
- ledger clamp, 비용 미반영 이전, cap 상향, baseline/pin 자가 갱신 금지.
- A의 NO_GO를 다른 형태로 재시도하지 않는다(같은 추측 반복 금지).

## E. 소비 규칙

이 handoff는 다음 work 회차가 소비하고, 그 결과를 다음 middle 회차가 독립 검수한다.
B의 판정이 내려오기 전에는 합격 기준을 바꾸지 않는다.
