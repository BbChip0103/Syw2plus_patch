# G2 base-preserving non-uniform storage layout — Opus5/high middle plan (lap380)

역할: 중간계획/컨펌(Opus5/high). 게임 구현 없음, 게임 실행 없음, 바이너리 편집 없음.
권한 근거: Astra/medium `GO_BOUNDED_BASE_PRESERVING_NONUNIFORM_STORAGE_LAYOUT_IMPLEMENTATION_ONLY`
(decision SHA256 `2298916088f2735fd8b7495c4e598c155b0b3c65d5aed875cd1897cafa72b93c`,
외부 temp `g2_capacity/20260918_claude_resume_major_decision.json`). 전체 가능성 승인도 런타임 승인도 아니다.

> **lap381 상태 (2026-09-18 18:12 KST, middle Opus5/high).** §0의 실행 한계는 **해소됐다**.
> `make check` rc0(633 passed), `checks/safety.sh check` `SAFETY_PASS`, tail probe rc0, 신규
> C1/H1 probe rc0 전부 실측. **C1 = CLOSED**(count는 WORD, 겹침 없음), **H1 = CONFIRMED shape**
> (8×200 WORD matrix, 의미는 UNKNOWN). §4의 선행조건 1~3이 충족돼 **work tier 착수 가능**하다.
> §2 C3의 "외래 블록 delta 0"과 §3의 산출물 범위는 lap381이 정정했다(각 절 인용 참조).
> 기록: `docs/history/laps/20260918_lap381_middle_g2_c1_h1_closed.md`.

## 0. 이번 lap의 검증 한계 (먼저 읽는다 — lap380 시점 기록, 위 배너가 우선한다)

이 세션은 **Bash 실행 권한이 없다.** `make check`, `checks/safety.sh check`, `python3 <probe>` 모두
승인 대기로 거부됐다(비대화형이라 승인 불가). 따라서 이 문서에는 다음이 **없다**:

- ④-2 이전 바퀴 증거의 **실행 기반** 독립 재검증
- ④-4 목표별 Fast 게이트 결과 (`make check` / safety 2종)
- 원본 EXE 바이트에서의 **fresh** PE 헤더/섹션/리소스 재유도

대신 이번 lap이 실제로 한 것은 (a) 저장소 기록 원문 정독, (b) 여섯 저장영역 반개구간의
**산술 자기정합성 수검**, (c) 그 결과 드러난 설계 제약 3건의 확정이다. (b)는 손계산이며
바이트 재유도가 아니다. 읽기 전용 재유도 probe는 작성해 두었으나 **미실행**이다:
`docs/history/laps/probes/20260918_lap380_middle_g2_tail_layout_facts_probe.py`.
이 probe의 rc0는 다음 실행 가능한 세션이 반드시 먼저 확보해야 하는 입력이다.

## 1. 구조 지반 (기록 원문에서 읽은 값)

출처: `tools/g2_relocation_manifest_evidence.json` (`source.original_sha256` =
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 보호 pin과 동일 문자열),
`analysis/memory_maps/g2_capacity_boundaries.md`, lap379 feasibility 기록.

여섯 저장영역(전부 N=1200)과 **그 사이의 비균일 간극**:

| # | 영역 | start | end | elem | span | 다음 영역까지 간극 |
|---|---|---|---|---|---|---|
| 1 | unit_pool | `0x0066B790` | `0x00892410` | 0x758 | 0x226C80 | `0x6CB8` (27,832 B) |
| 2 | unit_existence | `0x008990C8` | `0x00899A28` | 2 | 0x960 | `0` (age와 연속·alias) |
| 3 | unit_age | `0x00899A28` | `0x0089A388` | 2 | 0x960 | `0xC80` (3,200 B) |
| 4 | category_slot_list_a | `0x0089B008` | `0x0089C2C8` | 4 | 0x12C0 | `0x2` (2 B, count alias) |
| 5 | category_slot_list_b | `0x0089C2CA` | `0x0089D58A` | 4 | 0x12C0 | `0xD7A1E` (883,742 B) |
| 6 | active_slot_list | `0x00974FA8` | `0x00975908` | 2 | 0x960 | — |

**손계산 수검 결과 (이번 lap, PASS):** 여섯 행 모두 `start + elem*1200 == end`가 성립한다.
`0x66B790 + 0x758*1200 = 0x892410`도 성립하며, 이 주소는 manifest의 alias 정의대로
unit_pool 반개구간 끝 · bulk save 시작 · live game-state base **세 이름이 같은 한 주소**다.
이것이 base-preserving 분기가 성립할 수 있는 유일한 이유이자 동시에 최대 위험이다.

## 2. mapper가 반드시 만족해야 하는 제약 3건

### C1 — **lap381에서 종결(CLOSED). 겹침 없음 — count는 WORD다.**

> **lap381 갱신(원본 바이트 근거).** 이 주소들은 전부 `.data` BSS라 파일에 바이트가 없다.
> 판정 근거는 접근 코드의 operand size다. `0x48bca1..0x48bcd2` 선형 디스어셈블에서
> `0fbf0d c8c28900` = `movsx ecx, word ptr [0x89c2c8]`, `66ff05 c8c28900` = `inc word ptr
> [0x89c2c8]`(raw에 `66` prefix 존재), list-B도 동형. 세 alias(`0x89c2c8`/`0x89d58a`/`0x975908`)
> 전 참조의 operand size는 **{2}뿐이고 4바이트 접근은 0건**이다.
> ⇒ manifest의 "live **dword** count field" 라벨이 **오기**다. 2 B 간극이 곧 WORD count이고
> **두 영역은 겹치지 않는다.** 아래 원문은 이력으로 보존한다.
> 근거: `docs/history/laps/20260918_lap381_middle_g2_c1_h1_closed.md` §5,
> probe `20260918_lap381_middle_g2_c1_h1_access_width_probe.py` rc0.

#### (원문 보존) catA end/count와 catB base의 2바이트 겹침 — lap380 시점 미결

manifest는 `0x0089C2C8`을 "list-A exclusive end **이자 live dword count field**"로 기술한다.
그런데 catB base는 `0x0089C2CA` = `0x0089C2C8 + 2`다. count가 **정말 dword라면**
`0x89C2C8..0x89C2CC`는 catB의 첫 원소 하위 2바이트를 덮는다. 둘 중 하나가 참이다:

1. count는 실제로 **WORD**이고 manifest의 "dword" 라벨이 오기다 → 간극 2 B가 정확히 count다.
2. 두 영역이 진짜로 겹친다 → 확장 시 **어느 쪽을 먼저 옮기든 상대를 손상**시킨다.

**이것은 mapper를 쓰기 전에 원본 바이트로 닫아야 하는 선행 질문이다.** 추정으로 어느 한쪽을
고르고 진행하면 조용한 손상이 나온다(lap379가 경고한 `8990C8` alias 유형과 같은 계열).
list-B의 `0x0089D58A` end/count alias도 동일한 형태이므로 같은 방법으로 함께 판정한다.

### C2 — 영역 사이의 외래 전역을 보존해야 한다

간극 `0x6CB8`(bulk/live-state 머리), `0xC80`, `0xD7A1E`는 빈 패딩이 아니다.
특히 catB와 active_slot_list 사이 **883,742 B**는 이 여섯 영역과 무관한 전역들이다.
mapper는 "영역을 늘린다"가 아니라 **"영역과 외래 블록이 교대로 놓인 tail 전체를 재배치한다"**를
수행한다. 외래 블록은 크기·상대 순서·내부 정렬이 모두 불변이어야 한다.

**H1 — lap381에서 형태 확정(CONFIRMED, shape only).** 간극 `0xC80` = 3,200 B는 실제로
**8행 × 200열 WORD matrix**다. 참조 5개(`0x43e887`/`0x47f447`/`0x47f8de`/`0x49b373`/`0x4a7f3f`)가
전부 WORD·index scale 2이고, 인덱스 산술이 `lea r,[x+x*4]` → `lea r,[r+r*4]` → `lea r,[col+r*8]`로
`200*row + col`을 만든다(`0x49b36a`, `0x47f8d2` 독립 2곳). 주소 = `0x89a388 + 2*(200*row + col)`,
span 3,200 B ⇒ row 8개. **의미(row 축의 정체)는 여전히 UNKNOWN**이며 8이 owner 수와 같다는 것은
강한 읽기지 증명이 아니다. lap380의 반대 근거(owner roster = PlayerStruct `+0xd4a` 4바이트 목록,
상한 250)는 이 블록이 owner roster가 **아님**을 보일 뿐이다.

**mapper 영향:** 이 블록은 "외래 블록"이 아니라 저장 계열의 일부지만 크기가 `8*200*2`로
**N과 무관**하다. 따라서 N을 올려도 **크기 불변**이고, 아래쪽 누적 삽입량만큼 **주소만 이동**한다.
근거: `docs/history/laps/20260918_lap381_middle_g2_c1_h1_closed.md` §6.

### C3 — 단일 delta 금지

여섯 영역은 원소 크기가 2/4/0x758로 다르고 간극도 다르다. 용량을 N으로 올리면 영역별 증가분이
`(N-1200)*elem`으로 전부 다르다. 따라서 **하나의 delta를 tail 전체에 더하는 구현은 금지**다
(STATUS 명시). mapper는 **구간별 조각 선형 사상(piecewise-linear map)**이어야 한다.

> **lap381 정정 — "외래 블록 delta 0"은 틀렸다.** 외래 블록에서 불변인 것은 **크기**이지
> **delta**가 아니다. 외래 블록의 새 주소는 **자신보다 낮은 주소에서 발생한 누적 삽입량**만큼
> 이동한다. delta 0으로 구현하면 확장된 영역이 외래 블록을 덮는다. 정확한 계약은:
>
> - 각 저장영역 i: `size' = size + (N-1200)*elem_i`, `base' = base + cumulative_insert_below(base)`
> - 각 외래 블록: `size' = size` (불변), `base' = base + cumulative_insert_below(base)`
> - `cumulative_insert_below(a)` = `a`보다 낮은 주소의 모든 저장영역 증가분 합
> - 따라서 tail 전체에서 delta가 0인 구간은 **최하위 영역 아래뿐**이다.
>
> H1 블록(`0x89a388`, 8×200 WORD)도 이 "크기 불변 + 주소 이동" 부류다(§2 C2 참조).

## 3. Sonnet5/high work tier 산출물 정의

새 파일 2개만 만든다. **기존 `patches/population/offline_storage_v1.py`는 frozen, 수정 금지.**

- `patches/population/base_preserving_storage_layout_v1.py`
- `patches/population/test_base_preserving_storage_layout_v1.py`

모듈은 **순수 레이아웃/기하 계산기**다. 원본을 읽어 SHA를 확인하고, 용량 N을 받아
결정적 사상을 산출한다. **코드 operand fixup을 하지 않고, 후보 EXE를 쓰지 않는다.**

> **lap381 정정 — 산출물 범위.** Astra 원문 범위상 **private non-launchable PE-layout artifact는
> 필수**다. "단순 JSON 계산기"로 축소하지 않는다. 즉 모듈은 사상 계산에 더해 §3.6 기하를 적용한
> **비실행 private artifact를 산출**해야 하며, 그 artifact는 격리 temp에만 두고 배포/실행하지 않는다.
> (실행 금지는 유지된다 — artifact를 만드는 것과 게임을 띄우는 것은 다른 문제다.)

> **lap381 새 사실(§3.6 단순화).** 여섯 영역과 그 사이 간극은 **전부 `.data`의 BSS**다
> (`.data` raw_end VA = `0x4f9000`, 최하위 영역 base `0x66b790`이 그보다 높다).
> 따라서 영역 확장에는 **옮길 raw 파일 바이트가 없다** — `.data`의 VirtualSize만 커진다.
> tail 위에 있는 섹션은 **`.rsrc` 하나뿐**이므로 raw 이동 대상도 `.rsrc`뿐이다.
> SectionAlignment = FileAlignment = `0x1000`, SizeOfImage = `0xc8f000`, base relocation
> directory **부재**(절대 VA 수동 fixup이 필요한 이유). 근거: lap380 tail probe rc0 실측.

필수 공개 계약:

1. `ORIGINAL_SHA256` pin과 불일치 시 **거부**(예외). 원본 파일에 쓰지 않는다.
2. `layout(n)` → 여섯 영역의 새 start/end/span + 각 영역의 delta + 외래 블록 목록.
   외래 블록은 **크기 불변이되 delta는 0이 아니다**(§2 C3 lap381 정정). 각 블록의 delta는
   자신보다 낮은 주소의 누적 삽입량이다.
3. `map_va(old_va, n)` → 구간별 조각 선형 사상. 영역 내부/외래 블록/사상 불가 주소를
   **세 가지로 구분해 반환**한다. 사상 불가를 0이나 항등으로 조용히 흘리지 않는다.
4. **N=1200 identity**: `layout(1200)`의 모든 start/end/span이 §1 표와 바이트 단위로 같고,
   `map_va(v, 1200) == v`가 표의 모든 경계와 그 ±1에서 성립한다. 이것이 최상위 회귀 앵커다.
5. bulk-relative span·count/endpoint alias·PlayerStruct span은 **절대 주소로 재계산하지 말고
   기준점 상대값으로 유도**한다(§2 C1이 닫히기 전에는 alias 주소를 새로 발급하지 않는다).
6. PE 기하: SectionAlignment/FileAlignment 정렬, 새 SizeOfImage, 리소스 섹션 이동과
   resource directory + 9개 payload RVA의 **일관 재기술**. raw/BSS 구분과 zero-fill 보존.
7. `4001 / 9601 / 9904`는 **공학 테스트 값**이다. 최종 용량이 아니며 모듈에 기본값으로
   박지 않는다. N은 호출자가 넘긴다.

필수 테스트(회귀):

- N=1200 항등(§3.4) — 경계·경계±1 전수.
- 확장 시 여섯 영역이 서로/외래 블록과 **겹치지 않음**, 순서 보존, 오름차순 단조.
- 32비트 overflow 부재(모든 새 VA와 SizeOfImage < 2^32), 정렬 불변식.
- 외래 블록 크기·상대 순서 불변.
- SHA 불일치 원본 거부, 원본/공유 파일 무변경.
- canonical/legacy launcher가 **프로세스 시작 전에** 이 산출물을 거부하는지.

## 3-5. 계약 5번의 범위 판정 — **lap385 middle(Opus5/high) 확정**

lap383이 "work tier가 임의로 정하지 말고 계획 문서에 명시하라"고 남긴 미결이다.
lap384가 의도적으로 미착수했고, lap385가 아래로 **확정한다. descope가 아니다 —
계약 5번은 여전히 필수이며, 이행 전까지 §3 전체 계약은 OPEN이다.**

### 판정 근거 (lap385 실측, probe `20260918_lap385_middle_g2_layout_r1_r6_acceptance_probe.py` rc0)

핀된 바이트가 이미 확정한 사실: save `0x440F02`는 length `0xE397C`·source `0x892410`을
push하고, load `0x4412DC`는 같은 쌍으로 `fread` 한다 ⇒ bulk 블록 `[0x892410, 0x975D8C)`.
이번 lap이 여섯 영역을 그 구간과 대조한 결과:

| | 영역 | bulk 블록과의 관계 | 추가 slot 1개당 |
|---|---|---|---|
| 1 | unit_pool | bulk **아래** (별도 roster 저장, load `0x441305`) | 1,880 B |
| 2~6 | existence/age/catA/catB/active_slot_list | bulk **안쪽** | 합계 14 B |

즉 `0x892410`은 §1이 적은 대로 세 이름이 같은 한 주소이고, 확장은 그 주소를
**1,880×(N-1200)만큼 밀어 올리는 동시에** 고정길이 `0xE397C` 블록 **내부 내용을
14×(N-1200)만큼 불린다**. N=4001이면 새 bulk start `0xD97DE8`, 필요 길이 `0xED2AA`.
두 값 모두 **하드코딩 push 즉시값**이며 현재 layout 모듈은 **둘 다 모형화하지 않는다.**

### 확정 범위

- **Part A — 이 카드에 남긴다(다음 Sonnet work 1회분).** `0x892410` 3중 alias를
  layout 결과의 **유도 속성으로 노출**한다: N=1200에서 `unit_pool.new_end == 0x892410`,
  확장 시 `0x892410 + 0x758*(N-1200)`. 세 이름(unit_pool 반개구간 끝 / bulk save 시작 /
  live state base)을 docstring에 명시하고 회귀를 붙인다. 새 주소 추론 0건 —
  이 모듈이 이미 소유·검증한 값의 명명과 노출뿐이다.
- **Part B — 신규 별도 카드로 뺀다.** PlayerStruct span(base `0x956770`, stride `0x3ABC`)과
  bulk span의 기준점 상대 유도. 이유: 이것은 이름 붙이기가 아니라 여섯 영역과 **겹치는
  두 번째 좌표계**(고정길이 저장 blob)를 새로 모형화하는 일이고, 저장 포맷 변경·
  길이 즉시값 fixup·save/load 호환성이라는 **layout 계산기 범위 밖 계약**을 끌고 온다.
  ③의 "한 바퀴 한 가지"와 활성 카드 3개 상한에도 걸린다.

### Astra 큐에 올릴 것 (승인 대기, 이번 lap은 독립 작업을 계속했다)

고정길이 bulk blob이 확장 대상 영역 5개를 품고 있다는 것은 **layout mapper만으로는
저장 호환 확장이 원리적으로 불가능**하다는 뜻이다(길이/주소 즉시값 fixup + 저장 포맷
변경이 필수). lap379 Sol의 integration/broad-patcher NO-GO를 **뒤집지 않고 강화**한다.
G2 8인5000을 이 경로로 계속할지는 Astra 판정 사항이다. 새 불가능 증명은 아니다.

## 4. 다음 중간 lap이 이 결과를 검수하는 방법 (독립 검증)

1. `20260918_lap380_middle_g2_tail_layout_facts_probe.py` rc0 (§1 표의 바이트 재유도).
2. C1을 닫은 원본 바이트 증거(그 2바이트가 count의 일부인가 catB[0]인가).
3. 새 모듈/테스트의 현행 SHA 3종 일치 + targeted 테스트 실측 개수.
4. `make check`(Fast) + `checks/safety.sh check` 2종 PASS, 보호 8 pin 불변.
5. 원본·공유 파일 무변경, residue 0.

**exit 0은 계획 승인도 검증 통과도 아니다.** 위 5개 중 하나라도 비면 REJECT로 적는다.

## 5. 중단 조건 (60분 / 실패 2회)

- C1을 바이트로 닫지 못하면 **거기서 멈춘다**. mapper를 추정 위에 쌓지 않는다.
- 새 주소 추론 엔진·전면 linear fixup 생성기를 만들려는 순간 STOP (Astra 범위 밖).
- 기존 STOP 카드(getter fault PC 2회, partial typed generator 2회, op7 fixture 2회,
  organic 243)를 새 provider로 재시도하지 않는다.
- 60분 또는 실패 가설 2회에서 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED` 중 하나로 닫는다.

## 6. 범위 밖 (명시)

게임 실행, code operand fixup, 후보 EXE 생성/배포, `offline_storage_v1` 변경,
frozen pin 갱신, 커밋/push, 새 의존성, slot>=1200 lifecycle/save smoke, LAN.
lap379 Sol의 **integration/automatic broad patcher/runtime NO-GO**는 유효하며
이번 카드는 그것을 뒤집지 않는다. 이 카드가 완료돼도 **G2는 미완료**이고,
tail 참조 이전 부채(lap379 재집계 17,584 linear 후보)는 **그대로 남는다**.
