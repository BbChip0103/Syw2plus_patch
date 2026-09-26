# G2 work 카드 W30 — F4(B) 전비 장부 `+0x200c` 32-bit 확장 (1단계: 구멍 확정 + 패처 구현)

- 발행: lap509 middle (Claude Code `claude-opus-5` / high), 2026-09-23 KST
- 수행: **work tier** (`claude-sonnet-5` / high 또는 Luna/high), **다음 work 회차**
- 사용자 승인: 2026-09-23 04:13 KST "32비트도 괜찮아" ⇒ **F4 = (B) 확정**(`docs/feedback/APPROVALS.md`).
  착수 지시: 2026-09-23 12:55 KST "1 2 바로 ㄱㄱ" ⇒ ① F4(B) 먼저, ② 건설 선택 로직 분석 다음.
- 근거 문서: `analysis/memory_maps/g2_supply_ledger_200c_site_inventory_lap509_20260923.md`
  (재현 probe `docs/history/laps/probes/20260923_lap509_middle_supply_ledger_site_inventory.py`, exit 0, 단언 7/7)
- 상한: **한 work 회차 또는 90분 중 먼저 도달하는 시점**, 실패 가설 2개.
- 활성 카드: W29(`G2_Q8_USED_CEILING_QUANTIFICATION_LAP505.md`)는 lap508 ACCEPT 로 `CLOSED`.
  **이 카드가 유일한 활성 카드다**(활성 최대 3개 규칙 준수).

---

## 0. 이 카드가 전제를 두 군데 고친다 (먼저 읽는다)

lap509 가 원본을 직접 전수 스캔해 확인한 정정 2건이다. **이전 범위 서술대로 착수하면 안 된다.**

1. **⚠ 범위는 5곳이 아니라 9곳이다.** STATUS/INBOX 가 `+0x200c` reader 로 적은
   `0x43EE03`/`0x43F0F3`/`0x43F43F` 는 실제로는 **`+0x2012`(supply_limit) 읽기**다
   (전사 과정에서 필드가 뒤바뀌었다). 진짜 `+0x200c` 사이트는 §1 의 9곳이며, 그중
   **절대주소 별칭 형태 4곳은 기존 범위에 아예 없었다.**
2. **⚠ "저장포맷 변경 동반"은 전제가 아니다.** bulk save/load 는 고정 길이 raw span
   `[0x892410, 0x975D8C)` = 932,220B 를 통째로 읽고 쓰며 PlayerStruct 배열이 그 안에 있다.
   **stride `0x3ABC` 와 span 길이를 보존하면 저장 파일 길이·레이아웃은 불변**이고, 호환 문제는
   *포맷* 이 아니라 **2바이트의 값 해석** 문제로 축소된다. 이 축소가 성립하는지가 §2 의 분기다.

이 두 정정 때문에 이 카드는 lap393 D절("work tier 단독 착수 금지")의 근거를 **부분적으로 해소**한다.
단독 착수 금지의 이유였던 "bulk save/load blob 포맷 변경"이 **stride 보존 경로에서는 불필요**하기
때문이다. 그러나 stride 를 바꾸는 경로는 여전히 lap385 통합 blocker 아래에 있다 ⇒ §2-C 는 금지다.

## 1. 범위 — `+0x200c` 전수 9곳 (이 표가 유일한 진실)

### base+disp 형태 (5곳)

| # | VA | 원본 명령 | 원본 바이트 | 역할 |
|---|---|---|---|---|
| 1 | `0x0043EDFC` | `movsx edx, word [ecx+0x200c]` | `0f bf 91 0c 20 00 00` | 핵심 생산 게이트 read |
| 2 | `0x0043EE9B` | `add word [ecx+0x200c], dx` | `66 01 91 0c 20 00 00` | **writer(+)** roster_add |
| 3 | `0x0043EF8B` | `sub word [ecx+0x200c], dx` | `66 29 91 0c 20 00 00` | **writer(−)** roster_remove |
| 4 | `0x0043F0E9` | `movsx eax, word [esi+0x200c]` | `0f bf 86 0c 20 00 00` | 2차 게이트 read |
| 5 | `0x0043F3B3` | `movsx eax, word [ebp+0x200c]` | `0f bf 85 0c 20 00 00` | HUD 10진 문자열 read |

### 절대주소 별칭 `0x95877C` 형태 (4곳)

| # | VA | 원본 명령 | 원본 바이트 |
|---|---|---|---|
| 6 | `0x0040DD12` | `movsx edx, word [eax+0x95877c]` | `0f bf 90 7c 87 95 00` |
| 7 | `0x0040E03B` | `movsx edx, word [eax+0x95877c]` | `0f bf 90 7c 87 95 00` |
| 8 | `0x00499767` | `movsx ecx, word [eax+0x95877c]` | `0f bf 88 7c 87 95 00` |
| 9 | `0x00499A0E` | `movsx ecx, word [eax+0x95877c]` | `0f bf 88 7c 87 95 00` |

**범위 밖(건드리지 않는다):** `+0x2012` 사이트 8곳, `+0x200a` 55곳, `+0x200e` 4곳, `+0x2010` 3곳.
`limit` 은 16-bit 로 남긴다(`1500+200×장수` 파생이라 5,000 에서도 int16 안).

## 2. 먼저 고를 것 — 32-bit `used` 를 어디에 두는가

`+0x200a`/`+0x200c`/`+0x200e`/`+0x2010`/`+0x2012` 는 2바이트씩 빈틈없이 붙어 있다.
제자리 4바이트 확장은 `+0x200e`(building_count)를 덮는다 ⇒ 다음 중 하나를 **측정으로 고른다**.

| 안 | 내용 | stride | 저장길이 | 판정 |
|---|---|---|---|---|
| **A** | PlayerStruct `[0,0x3ABC)` 안의 **미참조 4바이트 구멍**으로 `used` 이전 | 불변 | 불변 | **우선 시도** |
| **B** | `+0x200e` building_count 를 구멍으로 옮기고 `+0x200c` 를 제자리 확장 | 불변 | 불변 | A 실패 시 |
| **C** | stride/span 확장 | **변경** | 변경 | **금지** — lap385 통합 blocker 아래 |

### M-0 (먼저 끝낸다) — 구멍 맵 측정

- **정적 필요조건:** `.text` 전수에서 PlayerStruct 를 base 로 하는 disp 사용 집합을 뽑아
  `[0, 0x3ABC)` 안의 미사용 구간을 낸다. lap509 힌트(확정 아님): disp `0x2001~0x2007`·`0x2009`·
  `0x200b`·`0x200d`·`0x2016~0x2017`·`0x2019~0x2024` 는 **어떤 명령의 displacement 로도 등장하지 않는다**.
- **런타임 충분조건:** 미사용 후보 구간이 8 owner × 장시간 표본에서 **상수(전 표본 동일)** 임을
  읽기 전용으로 확인한다. `memcpy`/`memset` 경유 접근을 정적으로 배제할 수 없으므로 이 확인이 필수다.
- **A 채택 조건:** 4바이트 연속 · 정렬 가능 · 정적 미참조 · 런타임 상수 = 4개 모두 충족.
  하나라도 실패하면 A 기각, B 로 간다. **둘 다 실패하면 `BLOCKED` 로 보고하고 C 로 넘어가지 않는다.**

## 3. 합격/실패 측정식 (착수 전에 고정한다 — 사후 변경 금지)

| ID | 측정 | PASS | FAIL / UNKNOWN |
|---|---|---|---|
| M-a | 구멍 후보의 정적 미참조 + 런타임 상수성(8 owner) | 4바이트 확보, 위반 0 | 위반 ≥1 → A 기각 → B |
| M-b | 9개 사이트 원본 old-bytes 가 §1 표와 **바이트 단위 일치** | 9/9 일치 | 1곳이라도 불일치 → **즉시 STOP**(전제 붕괴) |
| M-c | 패치 후보 생성 → **정확한 원복** → 원본 SHA 재일치 | `b56986e0…` 재현 | 불일치 → STOP |
| M-d | 후보 `.text` diff 가 §1 9곳 + 선택한 구멍 관련 사이트로 **한정** | 범위 밖 변경 0 | 범위 밖 ≥1 → FAIL |
| M-e | 장부 산술 등가성 단위 테스트: `used ≤ 32,767` 구간에서 원본과 **동일 값** | 전 표본 일치 | 불일치 → FAIL |
| M-f | 랩 부재: 합성 입력 `used = 78,000`(=1200×`c_max`65)에서 음수·랩 **0건** | 0건 | ≥1 → FAIL |
| M-g | 구 세이브 호환 규칙(§4)이 blob 길이를 **바꾸지 않음** | 932,220B 불변 | 변하면 FAIL |
| M-h | `make check` + `checks/safety.sh check` + 원본 재해시 불변 | 전부 PASS | 하나라도 FAIL → 수리 우선 |

**M-f 의 근거:** `roster_add`(`0x43EE30`)는 cap 을 보지 않고 `cmp ax,0x4b0`(로스터 1,200칸)만 건다.
`c_max=65`(kind103, lap507 W29) ⇒ 구조적 최대 `used` = **78,000 > 32,767** ⇒ 16-bit 랩은
구조적으로 가능하고, 32-bit 에서는 78,000 ≪ 2^31 이라 **구조적으로 불가능**해진다.
이것이 F4 의 "안전상한 UNKNOWN"(lap395)을 닫는 숫자다. **도달성(실제 게임에서 78,000 에 가는가)은
여전히 UNKNOWN 이며 이 카드가 주장하지 않는다.**

## 4. 기존 세이브 호환 방침 (work 가 착수 전에 하나로 고정해 적는다)

blob 이 raw 메모리 이미지이므로 **파일 길이는 어느 안에서도 불변**(M-g). 남는 것은 값 해석이다.

- **권고안 — 로드 후 재계산:** 로드 직후 로스터(`+0xd4a`, 길이 `+0x200a`)를 순회해
  `used = Σ cost[type]` 로 다시 채운다. 두 입력 모두 **같은 blob 안**에 있어 자족적이고,
  누적 규칙은 `supply_200c_accumulation_rule_0726.md` 가 원본 실측으로 확정해 두었다.
  ⇒ 구/신 세이브 모두 정확한 값으로 수렴하고 저장 버전 마커가 필요 없다.
- **대안 — 버전 마커:** 구멍 1바이트에 마커를 두고 신규 세이브만 새 해석을 쓴다.
  구 세이브는 `used` 를 0으로 읽으므로 **재계산이 없으면 게이트가 잘못 열린다** ⇒ 단독 채택 금지.
- work 는 둘 중 하나를 고르고 **고른 이유와 실패 시 관측 형태를 카드 소비 기록에 적는다.**

## 5. 범위 경계 (반드시 지킨다)

- **원본은 읽기 전용.** 새 복사본에만 패치하고 정확한 원복을 함께 구현한다(M-c).
  기존 `patches/population/fixed_supply_5000.py` 의 hash-guard / exclusive-create / restore 계약을 그대로 따른다.
- **§1 표의 old-bytes 를 먼저 확인하고 쓴다.** 불일치면 쓰지 말고 STOP(M-b).
  §1·§6 의 교체 바이트는 **middle 이 종이 위에서 유도한 값**이다 — work 가 디스어셈블로
  재확인한 뒤 쓴다(lap393 §C 와 동일 규칙).
- **stride/span 을 바꾸지 않는다**(§2-C 금지). `0x476ED0`/`0x43EE30`/`0x43EEC0`/`0x43EDA0` 에
  바이트를 쓰지 않는다(lap389 A NO_GO 유지 — 단 `0x43EDFC` 는 `0x43EDA0` **함수 안**이고
  이번 범위이므로, 금지 대상은 **함수 진입점/로스터 경계 즉치**이지 §1 의 9곳이 아니다).
- **AI/생산 정책 로직은 건드리지 않는다.** (ㄴ) 는 여전히 사용자 전권 대기다.
- baseline/golden/안전 pin 을 고쳐 통과시키지 않는다. 실패는 보존한다.
- **이 카드의 PASS 범위는 정적 + 단위 테스트 + 원복까지다.** 후보 EXE 의 실제 게임 실행 검증은
  이 카드가 요구하지도 제안하지도 않는다 — 2026-09-23 12:55 사용자 지시 ③(패치본 실행 검증 제외)의
  적용 범위가 커뮤니티 배포본(2601·2606)인지 F4 후보까지인지 **문서상 불명확**하므로,
  work 는 실행 검증을 임의로 추가하지 말고 §7 의 미결로 올린다.

## 6. 예상 인코딩 (work 가 재확인 후 사용 — 그대로 믿지 않는다)

| 원본 | 길이 | 32-bit 대응 | 길이 | 비고 |
|---|---|---|---|---|
| `0f bf …` `movsx r32, word [m]` | 7B | `8b …` `mov r32, dword [m]` | 6B | **1B 남음 → `nop` 1개**로 길이 보존 |
| `66 01 …` `add word [m], dx` | 7B | `01 …` `add dword [m], edx` | 6B | 동일 |
| `66 29 …` `sub word [m], dx` | 7B | `29 …` `sub dword [m], edx` | 6B | 동일 |
| `66 8b 14 95 38 52 9b 00` `mov dx, word [edx*4+0x9b5238]` | 8B | `0f b7 14 95 38 52 9b 00` `movzx edx, word […]` | **8B 동일** | writer 의 `edx` 상위 16비트 0 보장에 **필수** |

마지막 줄이 없으면 `add dword` 가 `lea` 사슬 잔여 쓰레기를 더한다 ⇒ **writer 2곳 각각에 대해
그 앞의 cost 적재 명령(`0x43EE93`, `0x43EF83`)을 함께 바꿔야 한다.** 길이가 같아 비중첩 확인이 쉽다.

## 7. 산출물 / 소비 규칙

- 산출물: `patches/population/supply_ledger_32bit.py` + `tests/test_supply_ledger_32bit.py`
  (M-b~M-g 를 기계 회귀로 고정), 구멍 맵 근거는 `analysis/memory_maps/` 에 새 문서 1건.
  probe/원시 산출물은 공유 temp
  `…/temp/Syw2plus_patch/g2_capacity/20260923_lap<N>_f4b_ledger_32bit/` 에 두고 SHA256 을 기록한다.
- lap 기록은 `docs/history/LAP_TEMPLATE.md` 필드 전부. fixture SHA 는 **기계 산출물 필드를 인용**한다(손 전사 금지).
- **work 는 자기 결과를 최종 승인하지 않는다** — 다음 새 middle(Opus5)이 원시에서 독립 재계산해야 2단이 선다.
- work 가 cap 숫자·합격 기준·범위를 바꾸지 않는다. 바꿔야 할 사유가 생기면 그 자리에서 멈추고
  근거를 적어 middle/strategy 로 올린다.
- **§7 미결(모델이 고르지 않는다):** F4 후보 EXE 의 실제 게임 실행 검증이 12:55 지시 ③ 의
  제외 범위에 들어가는가. 들어가면 F4 는 정적·단위 증거까지만으로 종료되고 G2 제품 합격 근거로는
  쓸 수 없다(DESIGN 4절이 실행 증거를 요구). 들어가지 않으면 별도 실행 카드가 필요하다.

---

## 8. lap511 middle 검수 결과 + 수리 범위 (Claude Code `claude-opus-5-5` / high, 2026-09-23)

근거 `analysis/memory_maps/g2_supply_ledger_hole_rejection_lap511_20260923.md`,
probe `docs/history/laps/probes/20260923_lap511_middle_w30_independent_review.py`(exit 0).

**판정: lap510 소비 = `REJECT`(구멍 선택) · 패치 기계부 `ACCEPT`.**
- M-a **FAIL**: `+0x2100` 은 `+0x2014` count / `+0x2018` dword 원소, **용량 1,000칸**(`0x43F4C7
  cmp ax,0x3e8`) 리스트 `[0x2018,0x2FB8)` 의 **58번 칸**이다. 시도1 `+0x201c` 도 같은 리스트 1번 칸.
  런타임 상수(tick 6,018)는 리스트가 9칸까지만 찼기 때문이다. ⇒ **안 A 기각**(실패 가설 2/2 소진).
- M-b/M-c/M-d **PASS**(11/11 old-bytes, 후보 SHA `7cb0faf3…` 재현, diff 62B 사이트 밖 0, 원복 SHA 재현).
- 절차 편차 기록: §2 "하나라도 실패하면 A 기각, B 로" 인데 lap510 은 시도1 실패 후 A 안에서 다른
  구멍을 골랐다. 결과적으로 같은 리스트였으므로 이 편차가 기각 원인이 됐다.

**다음 work 회차 수리 범위 = 안 B (이 절이 §2·§6 을 대체, §3 측정식·§5 경계는 그대로):**

| 묶음 | VA | 원본 | 교체(같은 길이) |
|---|---|---|---|
| building_count 이사 4곳 | `0x43DB24`·`0x43E204`·`0x43EEAD`·`0x43EF9D` | disp `0x200e` | disp **`0x2016`** (다른 바이트 불변) |
| `used` 제자리 dword 9곳 | §1 표 9곳 | `0f bf`/`66 01`/`66 29` word | `8b`/`01`/`29` dword + `nop`, **disp 불변**(`0x200c`·`0x95877c`) |
| cost-load 2곳 | `0x43EE93`·`0x43EF83` | `66 8b` | `0f b7` (lap510 과 동일) |

- `+0x2016` 근거: 리스트 count 워드(`+0x2014`)와 dword 배열(`+0x2018`) 사이 정렬 패딩. 덮는
  명령은 `0x43F57F` 하나뿐이고 esi≥1 이라 닿지 않음. lap510 원시 2,896 owner-표본 전부 0.
- `supply_ledger_32bit.py` 는 **안 B 로 교체**(A 코드는 남기지 않는다 — 같은 파일 단일 작성자).
  테스트에 추가: (i) `+0x2014` 리스트 용량 1,000 → 원소 영역 `[0x2018,0x2FB8)` 과 새 필드가 **겹치지
  않음**을 원본 바이트(`66 3d e8 03`)에서 단언, (ii) building 4곳 전수 = 원본 스캔 결과와 동일.
- **M-a 런타임 재확인(필수, 원본 패치 0):** lap510 `attempt2_hole2100/hole_constancy_run.py` 를
  복사해 `HOLE_OFF=0x2016`·`HOLE_LEN=2`·`STOP_TICK=24000` **세 상수만** 바꿔 실행한다(tick 6,018 은
  짧다는 것이 이번 기각의 교훈). 위반 ≥1 이면 B 기각 → `BLOCKED`. 시간이 부족하면 **시작하지 말고**
  기록한다. 시작했으면 Monitor/동기로 **완주까지** 기다린다(background 후 세션 종료 금지).
- **§4 구세이브:** 안 B 에서는 로드 후 `used`·building_count **둘 다** 재계산이 필수다(구 blob 의
  `[0x200c,0x2010)` 은 `used|building<<16`). 재계산 훅 구현 전까지 후보는 **신규 게임 전용**이며
  구세이브 로드 시험은 FAIL 로 기록한다.
- 안 B 도 실패하면 `BLOCKED` 보고, **C(stride 변경) 금지 유지**. 구멍을 PlayerStruct 밖(.data 확장 등)에
  두는 대안은 이 카드 범위 밖이며 middle/strategy 판정 없이 착수하지 않는다.

---

## 9. lap514 middle 독립 재계산 = 안 B `ACCEPT` ⇒ **W30 `CLOSED`** (Claude Code `claude-opus-5-5` / high, 2026-09-23)

근거 `analysis/memory_maps/g2_supply_ledger_holeb_acceptance_lap514_20260923.md`, 전문
`docs/history/laps/20260923_lap514_middle_w30_holeb_independent_recompute.md`, probe 산출 SHA `0c0ed0d2…`.

- M-a PASS: lap513 원시 5,768 owner-표본 재추출 위반 0(tick 24,019) + 겹침 전수 스캔에서 `+0x2016` 접근은 비도달 `0x43F57F` 1곳뿐.
- M-b/M-c/M-d PASS: 15/15 old-bytes, 후보 SHA `1893ff50…`, diff 66B 사이트 밖 0, 원복 원본 SHA.
- M-e/M-f PASS(기계어 수준): 9개 used 소비 전부 32-bit, writer 앞 `movzx`. 단위 M-e/M-f는 산술 모델이라 보조 증거.
- M-g PASS: stride/span 사이트 변경 0. M-h: `make check`·safety는 lap514 기록.
- **범위 한계 그대로:** 후보 EXE 실제 실행 0(Q9 미결) ⇒ G2 제품 합격 근거 아님. 구세이브 미지원(신규 게임 전용).
- 이 카드는 닫혔다. 다음 트랙은 12:55 지시 ②(건설 선택 로직 분석) — 새 카드 W31로 발행한다.
