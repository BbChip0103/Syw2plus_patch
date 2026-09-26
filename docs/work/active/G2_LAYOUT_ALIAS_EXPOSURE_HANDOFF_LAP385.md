# HANDOFF lap385 middle(Opus5/high) → work tier(Sonnet5/high) — §3-5 Part A: `0x892410` alias 노출

발행: 2026-09-18 KST. 발행자 역할: 중간 tier 진단/검수/확인. **구현은 하지 않았다.**
선행 판정: lap384의 R1~R6 수리는 lap385가 독립 재유도로 **ACCEPT**했다
(`docs/history/laps/20260918_lap385_middle_g2_layout_r1_r6_acceptance.md`).
`G2_STORAGE_LAYOUT_REPAIR_HANDOFF_LAP383.md`는 **소비됨** — 재작업 금지.

대상: `patches/population/base_preserving_storage_layout_v1.py`
(현행 SHA256 `7ae85ef50ae324a42a16f8cb251b05498f22f18a7d9f84d20cd361bf1a136cb2`)
및 `patches/population/test_base_preserving_storage_layout_v1.py`
(현행 SHA256 `88672c65a91185526296a81e25008b352756eda2bf6569ba8d3a4b3fc8ccee9a`).

`patches/population/offline_storage_v1.py`는 **frozen — 수정 금지**
(`e9d84513f6a53e27135a7e19a546a8a72165804d1041f9a23719fc7cb249f8cc`).

## 이번 회차에 할 일 (이것만. 범위 확대 금지)

계획 `G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md` **§3-5 Part A**를 구현한다.
`0x892410` 3중 alias를 layout 결과의 **유도 속성으로 노출**한다.

### A1 — alias를 이름 있는 유도 속성으로 노출

`LayoutResult`에 `unit_pool` 반개구간 끝을 돌려주는 접근자(예: `bulk_state_base` 또는
`triple_alias_va`)를 더한다. **새 상수로 `0x892410`을 박지 말 것** — 반드시
`unit_pool.new_end`에서 유도한다. docstring에 세 이름을 명시한다:

1. `unit_pool` 반개구간 끝 (`base + 0x758*N`)
2. bulk save 블록 시작 (save `0x440F02` source 즉시값 / load `0x4412DC` `fread` 대상)
3. live game-state base

### A2 — 회귀 (신규 pytest)

- N=1200에서 그 속성이 **정확히 `0x892410`** 이다(§1 표의 핀된 alias 앵커).
- 확장 N에서 `0x892410 + 0x758*(N-1200)`이다(`ENGINEERING_TEST_CAPACITIES` 전수).
- 그 값이 언제나 `layout(n).regions[0].new_end`와 같다(유도임을 고정, 상수 재입력 방지).

### A3 — 모형화하지 **않은 것**을 소스에 명시

A1의 docstring 또는 모듈 docstring에 다음을 **경고로 남긴다**(구현하지 말 것):

> 이 주소는 고정길이 bulk 블록 `[0x892410, +0xE397C)`의 시작이기도 하다. 그 blob은
> existence/age/catA/catB/active_slot_list **5개 영역을 내부에 품고** 있으므로, 확장은
> 이 주소를 `0x758*(N-1200)`만큼 밀어 올리는 동시에 blob 내부를 `14*(N-1200)`만큼
> 불린다. 두 값 모두 하드코딩 push 즉시값이며 **이 모듈은 둘 다 모형화하지 않는다.**

(lap385 실측: N=4001 → 새 bulk start `0xD97DE8`, 필요 길이 `0xED2AA`.)

## 필수 게이트

`make check` rc0 + `bash checks/safety.sh check` `SAFETY_PASS` + 원본
`b56986e0…c9c08a8ac` 불변 + frozen `offline_storage_v1.py` 무변경.
targeted 먼저, 통합 Fast는 **1회**. 문서 편집 뒤 전체 Fast 반복 금지.
기존 48건이 전부 계속 통과해야 한다(회귀 0).

## 범위 밖 (STOP)

- **Part B 착수 금지.** PlayerStruct span(base `0x956770`, stride `0x3ABC`)·bulk span의
  기준점 상대 유도는 **별도 카드**로 분리됐다. 이번 회차에 끌어오지 않는다.
- bulk 길이/주소 즉시값 fixup, 저장 포맷 변경, code operand fixup, 후보 EXE 생성/배포.
- 게임 실행, 커밋/push, 새 의존성, frozen pin 갱신, 주소 추론 generator,
  전면 linear fixup generator, slot>=1200 lifecycle/save smoke, LAN.
- 기존 STOP 카드(getter fault PC 2회, partial typed generator 2회, op7 fixture 2회,
  organic 243) 재시도 금지.

## 이 회차가 끝나도 남는 것

§3 계약 5번은 **Part B 미이행으로 여전히 OPEN**이다. Part A 완료를 계약 5번 완료로
적지 말 것. lap379 Sol의 integration / automatic broad patcher / runtime NO-GO는 유효하고,
**G2 8인5000은 미완료**다(lifecycle/economy/save/LAN 없음). 이 카드 ACCEPT는 제품 승인도
런타임 승인도 아니다. `4001/9601/9904`는 공학 테스트 값이며 최종 용량이 아니다.
