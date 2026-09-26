# HANDOFF lap381 middle(Opus5) → work tier(Sonnet5/high) — G2 base-preserving storage layout

> **소비됨 (lap383, 2026-09-18).** lap382가 이 카드를 수행했고 lap383 middle이 독립 검수해
> **REJECT — scoped 수리 1회**로 판정했다. 후속 범위는
> `G2_STORAGE_LAYOUT_REPAIR_HANDOFF_LAP383.md`다. 이 문서는 이력으로 보존하며 재발행하지 않는다.

발행: 2026-09-18 18:12 KST. 발행자 역할: 중간 tier 진단/계획/확인. **구현은 하지 않았다.**

## 선행조건 상태 — 전부 충족

lap380 `loop/ESCALATE_SOL`이 착수 전 요구한 4항 중 1~3이 닫혔다.

| # | 선행조건 | 상태 | 근거 |
|---|---|---|---|
| 1 | 세 게이트 실측 | **PASS** | `make check` rc0/633 passed, `SAFETY_PASS`, tail probe rc0 |
| 2 | C1을 원본 바이트로 종결 | **CLOSED** | count는 WORD, 겹침 없음 (lap381 기록 §5) |
| 3 | H1 확인/기각 | **CONFIRMED (shape)** | 8×200 WORD matrix, 의미는 UNKNOWN (§6) |
| 4 | work tier 착수 | **→ 이 카드** | |

## 착수할 것 (한 가지)

새 파일 2개만. **`patches/population/offline_storage_v1.py`는 frozen — 수정 금지.**

- `patches/population/base_preserving_storage_layout_v1.py`
- `patches/population/test_base_preserving_storage_layout_v1.py`

전체 계약·회귀·중단조건은 `docs/work/active/G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md`
§3~§5. 그 문서는 lap381이 정정한 상태이며 **정정본을 따른다.**

## lap381이 확정해 넘기는 사실 (재조사 금지 — 이미 원본 바이트로 닫힘)

1. **count alias는 WORD다.** `0x0089C2C8`(catA end/count), `0x0089D58A`(catB end/count),
   `0x00975908`(active_slot end/count) 전부 WORD. 4바이트 접근 0건.
   manifest의 "dword count field" 라벨은 **오기**다. catA end와 catB base(`0x0089C2CA`) 사이
   2 B 간극이 **바로 그 count**이고 **두 영역은 겹치지 않는다.**
   원소 폭은 별개다: catA/catB 원소는 DWORD(`mov dword ptr [reg*4 + base]`).

2. **`0x0089A388`의 `0xC80` 간극은 8×200 WORD matrix다.**
   주소 = `0x89a388 + 2*(200*row + col)`, row 8개. **크기는 N과 무관하다.**
   ⇒ 확장 시 **크기 불변, 주소만 이동**. 의미는 UNKNOWN이니 의미에 의존하는 코드를 쓰지 말 것.

3. **여섯 영역과 간극은 전부 `.data` BSS다** (`.data` raw_end VA `0x4f9000`).
   ⇒ 영역 확장에 **옮길 raw 바이트가 없다**. `.data` VirtualSize만 커진다.
   tail 위 섹션은 **`.rsrc` 하나뿐**이라 raw 이동 대상도 `.rsrc`뿐이다.
   SectionAlignment = FileAlignment = `0x1000`, SizeOfImage = `0xc8f000`,
   **base relocation directory 부재**.

4. **`0x66B790 + 0x758*1200 == 0x892410`** — unit_pool 끝 = bulk save 시작 = live state base,
   세 이름이 한 주소. 이 3중 alias가 base-preserving 분기의 근거이자 최대 위험이다.

## 반드시 지킬 정정 2건 (lap380 계획의 오류)

- **"외래 블록 delta 0"은 틀렸다.** 외래 블록은 **크기**가 불변이지 delta가 0이 아니다.
  새 주소 = 원래 주소 + **자신보다 낮은 주소의 누적 삽입량**. delta 0으로 짜면 확장 영역이
  외래 블록을 덮는다. delta가 0인 구간은 최하위 영역 아래뿐이다.
- **private non-launchable PE-layout artifact는 필수다.** 단순 JSON 계산기로 축소 금지.
  격리 temp에만 두고 배포/실행하지 않는다.

## 최상위 회귀 앵커

`layout(1200)`이 §1 표와 **바이트 단위로 동일**하고, 표의 모든 경계와 그 **±1**에서
`map_va(v, 1200) == v`. 이것이 깨지면 다른 결과는 보지 않는다.
추가 회귀: 겹침 부재/순서 보존/단조성, 32비트 overflow 부재, 정렬 불변식,
외래 블록 크기·상대 순서 불변, SHA 불일치 원본 거부, launcher가 **프로세스 시작 전** 거부.

## 범위 밖 (STOP)

게임 실행, code operand fixup, 후보 EXE 생성/배포, `offline_storage_v1` 변경, frozen pin 갱신,
커밋/push, 새 의존성, slot>=1200 lifecycle/save smoke, LAN, 주소 추론 generator,
전면 linear fixup generator. 기존 STOP 카드(getter fault PC, partial typed generator, op7,
organic 243)를 새 provider로 재시도하지 않는다.
`4001 / 9601 / 9904`는 **공학 테스트 값**이며 최종 용량이 아니다 — 모듈에 기본값으로 박지 않는다.

## streak 경고 (다음 세션이 먼저 볼 것)

진입 시 `implementation-unchanged-streak=1`이었고 **lap381도 제품 코드 0**이라 streak는 **2**다.
PROMPT ③상 **세 번째 무변경 회차는 Astra/Sol의 계속/중단 판정이 먼저 필요하다.**
따라서 다음 lap은 **실제 제품 코드(위 두 파일)를 산출해야 한다.** 산출하지 못할 사정이 생기면
또 문서 lap을 쌓지 말고 `loop/ESCALATE_SOL`로 구체 blocker를 올린다.

## 중단 조건

60분 또는 실패 가설 2회에서 `FEASIBLE` / `NOT_FEASIBLE` / `BLOCKED` 중 하나로 닫는다.
새 주소 추론 엔진을 만들려는 순간 STOP(Astra 범위 밖).

## 이 카드가 완료돼도 남는 것

lap379 Sol의 **integration / automatic broad patcher / runtime NO-GO는 유효**하다.
이 카드는 그것을 뒤집지 않으며 **G2는 여전히 미완료**다.
tail 참조 이전 부채(lap379 재집계 **17,584 linear 후보**)도 그대로 남는다.
