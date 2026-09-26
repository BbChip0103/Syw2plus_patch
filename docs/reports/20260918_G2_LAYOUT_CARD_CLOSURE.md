# G2 base-preserving storage layout 카드 — 종결 리포트

작성: 2026-09-18 lap388 middle(Claude Code `claude-opus-5`/high).
근거: Astra `GO_FINISH_CURRENT_LAYOUT_CONTRACT_ONCE`
(`g2_capacity/20260918_post_layout_major_decision.json`) — "재수리 체인 없이 요약 리포트로
이 카드를 종결한다".

## 1. 이 카드가 실제로 산출한 것

lap380(계획) → lap382(구현) → lap383(REJECT) → lap384(수리) → lap385(ACCEPT + Part A/B 분할
확정) → lap386(Part A) → lap387(Part B) → **lap388(독립 검수 ACCEPT·종결)**.

산출물은 **순수 기하 계산기 1개**다: `patches/population/base_preserving_storage_layout_v1.py`
(SHA `1469752c…f0c1bd`) + 테스트(SHA `5c220a73…f0bd70c70`, 82건) + 비실행 PE 레이아웃 artifact
(`.pelayout` `38a7148e…36cbc808`, mapping JSON `010224184bc9…7d02987f6d`, 외부 temp).

기계로 확정된 값(N=4001 기준, 전부 lap388이 독립 재유도로 일치 확인):

| 항목 | N=1200 | N=4001 | slot당 |
|---|---|---|---|
| BULK start (`0x892410` 3중 alias) | `0x892410` | `0xD97DE8` | +1,880 B |
| BULK length | `0xE397C` | `0xED2AA` | +14 B |
| BULK end | `0x975D8C` | `0xE85092` | +1,894 B |
| PlayerStruct base | `0x956770` | `0xE64494` | +1,892 B |
| PlayerStruct span | `8×0x3ABC` | `8×0x3ABC` | 불변 |
| bulk-relative PlayerStruct offset | `0xC4360` | `0xCC6AC` | +12 B |

## 2. 이 카드가 **증명한 것**과 **증명하지 않은 것**

증명한 것 — 모두 계산기 단위:
- 6개 저장 영역의 조각선형 재배치가 겹침 없이·단조로·32비트 안에서 성립한다.
- `0x892410`이 unit_pool 반개구간 끝 / bulk save 시작 / live state base 세 이름의 **한 주소**이고,
  그 즉시값 `0x892410`과 길이 즉시값 `0xE397C`가 save `0x440F02`·load `0x4412DC` **양 사이트의
  바이트 창에 실재**한다(lap388 실측, 4/4).
- 확장은 이 주소를 밀어 올리는 **동시에** 고정길이 blob 내부를 14 B/slot 불린다.
- PE 헤더/리소스 기하는 원본을 바이트 단위로 재기술 가능하며 N=1200에서 항등이다.

증명하지 **않은** 것 — 제품에 필요한 전부:
- code operand fixup 0건. 저장 포맷 변경 0건. 후보 EXE 0개. 게임 실행 0회.
- 확장 용량에서의 생성/수명주기/경제/저장/LAN 증거 0건.
- `4001/9601/9904`는 **공학 테스트 값**이며 제품 용량이 아니다.

## 3. Astra `native_route_judgment`와의 관계 — **뒤집지 않고 강화**

이 ACCEPT는 "현재 artifact에서 bounded native slot≥1200 lifecycle/save 마일스톤을 낼 수 없다"는
판정을 **유지**한다. 계약 5번이 닫혔다는 사실 자체가 그 판정의 근거를 수치로 굳힌다:
저장 호환 확장은 **길이 즉시값과 주소 즉시값 두 하드코딩 push의 fixup + 저장 포맷 변경**을
반드시 요구하며, layout mapper만으로는 원리적으로 불가능하다. lap379 Sol의
integration / broad-patcher / runtime NO-GO도 그대로 유효하다.

**이것은 새 불가능 증명이 아니다.** 현재의 빠른-패치 전달 루프가 이 경로로는 안 된다는
것이지, 원본 게임을 결코 확장할 수 없다는 증명도, 32비트/OOM 판정도 아니다.

## 4. 남은 사각 (수치 영향 0, 수리 카드 미발행)

N15 STATUS 문구 드리프트(정정 완료) / N16 순환 테스트 1건 / N17 `mapped_offset` 테스트 공백 /
N18 artifact JSON에 bulk-relative offset 명시 필드 부재(유도 가능) / N19 `regions[1:]` 인덱스
선택의 장래 취약성. 상세는 `docs/history/laps/20260918_lap388_middle_g2_layout_part_ab_acceptance.md`.

## 5. 결정이 필요한 것 (middle 권한 밖)

G2 8인5000을 **이 native 확장 경로로 계속할지**가 미결이다. Astra 결정 JSON이 alias별 후속
카드를 `not_allowed`로 막았고 다음 runtime을 `None authorized`로 두었으므로, 이 레인에는
middle이 정당하게 발행할 수 있는 다음 work 카드가 없다. `loop/ESCALATE_SOL` 참조.
