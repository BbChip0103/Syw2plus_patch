# G2 전비 cap vs 16-bit 장부 — middle 판정과 분기별 work handoff (lap393)

발행: lap393 middle (Claude Code `claude-opus-5` / high), 2026-09-20 KST
근거 원문: `docs/history/laps/20260920_lap393_middle_g2_supply_ledger_invariant.md`
probe: `docs/history/laps/probes/20260919_lap393_middle_g2_supply_ledger_invariant_probe.py` (rc0, `failures=[]`)

## A. 이번 lap이 닫은 것

1. **lap391 V2 → UNKNOWN 정정.** `FUN_00444EF0`은 패배 핸들러가 아니라 하드코딩 owner를 쓰는
   캠페인 스크립트 로직이다(본문 `+0x200A/+0x200C/+0x2012` 참조 0건, caller 8개 전부
   `0x4BE000~0x4C2000`, arg1이 즉치 `4/6/7` 또는 `word[0xB63FC4]`). "패배 0건 ⇒ 발화 불가"는 비약.
   lap391의 **수치는 유효**하고 **gap-proof 추론만 철회**한다. lap392 Astra 이의 인용.
2. **cap1500 주장 → 불변식으로 승격(증명).** `+0x200C` writer는 전 `.text`에 정확히 2개
   (`add`@`0x43EE9B` / `sub`@`0x43EF8B`)이고 둘의 비용 유도 산술 골격이 동일하므로 이전은
   전역합을 보존하며, 생산 gate `0x43EDA0`이 `used+cost<=cap`을 강제한다.
   ⇒ `max_o U_o ≤ Σ_o cap_o`가 매 순간 성립.

## B. 결정 수치 — 사용자/Astra 판정 필요

`8 × cap ≤ 32,767` ⇔ **`cap ≤ 4,095`**.

| cap | 전역 상한 | 부호16 랩 |
|---|---|---|
| 1,500 (원본) | 12,000 | **불가능(증명)** |
| **4,095** | 32,760 | **불가능(증명)** |
| 5,000 (목표) | 40,000 | **배제 불가** — 한 owner가 전역 전비의 81.92% 이상 보유 시 랩 |

**"8인 각 5000"은 원본 16-bit 부호 장부와 양립하지 않는다.** 분기는 둘뿐이다.

## C. 분기 A — cap ≤ 4,095 채택 (승인 시 **즉시 착수 가능**, FEASIBLE)

담당: work tier (Sonnet5/high). 범위가 작고 기존 모듈 패턴을 그대로 쓴다.

- 산출물: `patches/population/fixed_supply_4095.py` + `test_fixed_supply_4095.py`.
  기존 `fixed_supply_5000.py`와 **동일한 hash-guard/exclusive-create/restore 계약**을 따른다.
- 고칠 즉치는 2개뿐이며 원본 바이트는 lap393 probe가 재확인했다:
  | 파일 오프셋 | VA | 원본 | 교체 후(4095=`0x0FFF`) |
  |---|---|---|---|
  | `0x3FFD4` | `0x43FFD4` | `05 dc 05 00 00` (`add eax,0x5DC`) | `b8 ff 0f 00 00` (`mov eax,0xFFF`) |
  | `0x1B576` | `0x41B576` | `66 c7 00 dc 05` | `66 c7 00 ff 0f` |
  길이 동일(5바이트/5바이트)이라 비중첩·범위 확인이 기존 모듈 로직 그대로 성립한다.
  **위 교체 바이트는 middle이 종이 위에서 유도한 값이다. work tier가 디스어셈블로 재확인한 뒤 쓴다.**
- 측정식(먼저 고정): 8인 로드 후 모든 sample에서 (M-a) `used` 음수 **0건**,
  (M-b) 전역 `used` 합 최대 **≤ 32,760**, (M-c) 8인 cap이 균일 **4095**,
  (M-d) 기존 9/19 관측과 같은 24k 구간에서 오류/cleanup 잔류 0.
- 시간 상한: 한 work 회차 또는 60분 중 먼저 도달한 시점.

## D. 분기 B — cap 5,000 유지

**work tier 단독 착수 금지.** `+0x200C`를 32-bit로 넓히려면 5개 명령 사이트 + PlayerStruct 필드 폭
+ **bulk save/load blob 포맷**을 함께 바꿔야 한다 ⇒ lap385/388이 굳힌 **저장포맷·즉치 fixup 통합
blocker와 동일 성격**이고 현행 NO_GO 아래에 있다. 분기 B를 고르려면 Astra/사용자가 그 NO_GO를
먼저 다시 판정해야 한다.

## E. 하지 말아야 할 것

- **랩 트리거 fixture를 만들지 않는다**(lap391 §5 질문에 대한 middle 권고 = 불필요).
  분기 A는 불가능이 증명돼 잴 것이 없고, 분기 B는 음성 관측이 상한 40,000을 바꾸지 못한다.
  `FUN_00444EF0` 반복 유도는 캠페인 스크립트 경로라 8인 자유대전 재현 자체가 의심스럽다.
- `0x476ED0`/`0x43EE30`/`0x43EEC0`/`0x43EDA0`에 바이트를 쓰지 않는다(lap389 A의 NO_GO 유지).
- ledger clamp·비용 미반영 이전·baseline/pin 자가 갱신 금지.
- 9/19 trace 재분석을 반복하지 않는다(W1 소비 완료).

## F. 소비 규칙

B의 cap 결정이 내려오기 전에는 합격 기준을 바꾸지 않는다. 결정 후 해당 분기 카드를 다음 work
회차가 소비하고, 그 결과를 다음 middle 회차가 독립 검수한다.
