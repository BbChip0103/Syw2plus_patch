# 전비 장부 `+0x200c`(used) 전수 사이트 인벤토리 — F4(B) 32-bit 확장 범위 확정

- 작성: 2026-09-23, lap509, middle(Claude Code `claude-opus-5` / high)
- 근거: 원본 EXE **직접 디스어셈블**(Capstone 5.0.7, `.text` 전수 선형 스윕 + 미디코드 바이트 재시도).
  재현 probe: `docs/history/laps/probes/20260923_lap509_middle_supply_ledger_site_inventory.py` (exit 0, 단언 7/7 PASS)
  산출물: `…/temp/Syw2plus_patch/g2_capacity/20260923_lap509_f4b_site_inventory/site_inventory.json`
  (SHA256 `f9d05771666c379696553b98fa9137edb12efe76b04829123c6f59dc53e303e0`)
- 범위: **읽기 전용 정적 분석.** 원본/후보 바이트 변경 0 · 메모리 쓰기 0 · 게임 실행 0.
- 대상 원본 `Syw2plus/syw2plus_original.exe`
  SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 1,032,192B,
  `.text` VA `0x401000` / 0xE3AE5B, 디코드 명령 306,187개.

프로세스 exit 0 은 제품 검증이 아니다. 이 문서는 **게임 실행 증거가 아니라 정적 주소 근거**다.

## 0. 이 문서가 정정하는 것 (⚠ 이전 카드 범위 서술이 틀렸다)

`docs/STATUS.md`(lap508 시점)와 `docs/feedback/INBOX.md` 2026-09-23 12:55 항목은 F4(B) 범위를
> writer 2곳(`0x43EE9B` add / `0x43EF8B` sub) · **reader 3곳(`0x43EE03`/`0x43F0F3`/`0x43F43F`, 전부 `movsx`)**

으로 적었다. 전수 스캔 결과 **reader 3곳은 `+0x200c`(used)가 아니라 `+0x2012`(supply_limit) 읽기**다.

```
0x0043ee03  movsx ecx, word ptr [ecx + 0x2012]   [0fbf8912200000]   ← +0x2012, +0x200c 아님
0x0043f0f3  movsx edx, word ptr [esi + 0x2012]   [0fbf9612200000]   ← +0x2012
0x0043f43f  movsx edx, word ptr [ebp + 0x2012]   [0fbf9512200000]   ← +0x2012
```

출처 추정: `analysis/memory_maps/hero_limit_supply_patch_sites_20260921.md`의
"`+0x2012`에 쓰는 명령은 `0043FFD9` 하나뿐이고 **나머지 3곳(`0043EE03`, `0043F0F3`, `0043F43F`)은
모두 `movsx` 읽기**" 문장이 STATUS로 옮겨지면서 필드가 `+0x2012` → `+0x200c`로 뒤바뀌었다.
그 원문은 정확했고, **전사 과정에서 필드가 바뀐 것**이다.

⇒ **F4(B) 실제 범위는 5곳이 아니라 9곳이다.** 아래 §1이 전수다.

## 1. `+0x200c` 를 만지는 명령 전수 — **9곳**

### 1-A. `base + disp` 형태 (5곳)

| # | VA | 명령 | 원본 바이트 | 역할 |
|---|---|---|---|---|
| 1 | `0x0043EDFC` | `movsx edx, word [ecx+0x200c]` | `0f bf 91 0c 20 00 00` | **핵심 생산 게이트** `FUN_0043EDA0` 의 used 읽기 |
| 2 | `0x0043EE9B` | `add word [ecx+0x200c], dx` | `66 01 91 0c 20 00 00` | **writer(+)** — roster_add `FUN_0043EE30` |
| 3 | `0x0043EF8B` | `sub word [ecx+0x200c], dx` | `66 29 91 0c 20 00 00` | **writer(−)** — roster_remove |
| 4 | `0x0043F0E9` | `movsx eax, word [esi+0x200c]` | `0f bf 86 0c 20 00 00` | 2차 게이트 읽기(`0x43F0F3` limit 읽기와 짝) |
| 5 | `0x0043F3B3` | `movsx eax, word [ebp+0x200c]` | `0f bf 85 0c 20 00 00` | **HUD 문자열** — `+= [ebp+0x1c]` 후 `push 0xA; call 0x4E4146`(10진 변환) |

### 1-B. 절대주소 별칭 `0x95877C` = PlayerStruct[0]+0x200c 형태 (4곳) — **기존 범위에 아예 없었다**

| # | VA | 명령 | 원본 바이트 | 역할 |
|---|---|---|---|---|
| 6 | `0x0040DD12` | `movsx edx, word [eax+0x95877c]` | `0f bf 90 7c 87 95 00` | 게이트 읽기 |
| 7 | `0x0040E03B` | `movsx edx, word [eax+0x95877c]` | `0f bf 90 7c 87 95 00` | 게이트 읽기 |
| 8 | `0x00499767` | `movsx ecx, word [eax+0x95877c]` | `0f bf 88 7c 87 95 00` | 게이트 읽기 |
| 9 | `0x00499A0E` | `movsx ecx, word [eax+0x95877c]` | `0f bf 88 7c 87 95 00` | 게이트 읽기 |

`eax` 는 직전 `lea`/`shl` 사슬로 만든 `player_index * 0x3ABC` 다(예 `0x40DD00`~`0x40DD0F`).

## 2. 짝을 이루는 `+0x2012`(limit) 사이트 — 8곳 (widening 대상 아님, 일관성 대상)

| 형태 | VA | 명령 |
|---|---|---|
| disp | `0x0043EE03` · `0x0043F0F3` · `0x0043F43F` | `movsx r32, word [reg+0x2012]` |
| disp | `0x0043FFD9` | `mov word [ebp+0x2012], ax` — **유일한 writer** (`1500 + 200×장수`) |
| abs | `0x0040DD1F` · `0x0040E048` · `0x00499774` · `0x00499A1D` | `movsx r32, word [eax+0x958782]` |

`limit` 최대치는 `기본치 + 장수당 × 장수상한` 파생이라 목표 5,000 에서도 int16 범위 안이다
⇒ **이번 확장 대상은 `used` 뿐**이고 `limit` 은 16-bit 로 둔다. 단, 두 값을 비교하는 게이트가
같은 32-bit 레지스터 공간에서 만나므로 **부호 확장 방식이 바뀌면 비교 의미가 바뀐다**(§4).

## 3. 게이트 산술 — 확장이 무엇을 고치는지

핵심 게이트 `FUN_0043EDA0` (`0x43EDFC`~`0x43EE11`):

```
edx = movsx(used   @ +0x200c)      ; 16-bit 부호 → 32-bit
ecx = movsx(limit  @ +0x2012)
eax = movsx(cost   @ 0x9B5238[kind])
edx = edx + eax                    ; used + cost
cmp edx, ecx ; jle pass            ; used + cost <= limit 이면 통과
```

절대주소 게이트(`0x40DD12`·`0x499767` 계열)는 항 하나가 더 있다:

```
used(+0x200c, 16b) + supply_in_production(+0x001C, **이미 32-bit dword**) + cost  <=  limit(+0x2012, 16b)
```

⇒ 같은 장부의 짝인 `+0x001C` 는 **이미 32-bit** 다. `used` 만 16-bit 인 비대칭 구조다.

### 랩이 실제로 가능한가 — 상한을 숫자로 닫는다

- `used` 증가 경로 `roster_add`(`0x43EE30`)는 **cap 을 보지 않는다**. 거는 검사는
  `cmp ax, 0x4b0; jl`(로스터 배열 1,200칸) 하나뿐이다(`0x43EE37`).
- 단위 보급비 최대 `c_max = 65`(kind103) — lap507 W29 가 읽은 `type_specs.json` 기준.
- ⇒ **구조적 최대 `used` = 1,200 × 65 = 78,000 > 32,767(int16 상한)**.

**F4 의 "안전상한 UNKNOWN"(lap395)은 이로써 숫자로 닫힌다: 16-bit 부호 장부에서 랩은
구조적으로 가능하고, lap395 가 실측한 32,785 도달은 이 상한 78,000 과 정합한다.**
32-bit 로 넓히면 78,000 ≪ 2^31 이므로 **랩이 구조적으로 불가능해진다.**
(이것은 산술 상한이지 "게임에서 실제 도달한다"는 주장이 아니다 — 도달성은 여전히 UNKNOWN.)

## 4. 저장 포맷 — **"포맷 변경 동반"은 전제가 아니다** (두 번째 정정)

bulk save/load 는 **고정 길이 raw 메모리 span 하나**를 통째로 쓰고 읽는다:

| 경로 | 사이트 | 즉시값 |
|---|---|---|
| save | `0x00440F02` `push 0xE397C` / `0x00440F07` `push 0x892410` → `call 0x4DA39F` | |
| load | `0x004412D2` `push 0xE397C` / `0x004412D7` `push 0x892410` → `call 0x4DA4A9` | |
| span | `[0x00892410, 0x00975D8C)` = **932,220B** | save/load **동일** |

PlayerStruct 배열 `[0x956770, 0x973D50)`(base `0x956770`, stride `0x3ABC`, 8인)은 이 span
**안에 완전히 포함**된다(probe 단언 `bulk_contains_player_struct`).

⇒ **결과:** 저장 파일은 필드 스키마가 아니라 메모리 이미지다. 따라서
**stride `0x3ABC` 와 span 길이를 그대로 두는 한 `+0x200c` 폭을 넓혀도 저장 파일 길이·레이아웃은
한 바이트도 바뀌지 않는다.** 바뀌는 것은 그 span 안 2바이트의 *해석*뿐이다.

lap393 D절의 "`bulk save/load blob 포맷`을 함께 바꿔야 한다"와 APPROVALS 04:13 의
"(저장포맷 변경 동반)"은 **stride 를 바꾸는 경우에만** 참이다. stride 를 보존하는 경로에서는
저장 호환 문제가 *포맷* 문제에서 ***값 해석*** 문제로 축소된다. 이것이 W30 이 확인할 핵심 분기다.

## 5. 남은 미지수 (W30 이 측정한다)

1. **32-bit `used` 를 어디에 둘 것인가.** `+0x200c` 를 제자리에서 4바이트로 넓히면
   `+0x200e`(building_count)를 덮는다 — `+0x200a`/`+0x200c`/`+0x200e`/`+0x2010`/`+0x2012` 는
   2바이트씩 빈틈없이 붙어 있다(`analysis/memory_maps/player_offsets.md`).
   ⇒ PlayerStruct `[0, 0x3ABC)` 안에서 **`.text` 가 한 번도 참조하지 않는 4바이트 구멍**을 찾아야 한다.
   힌트(확정 아님): `.text` 전체에서 disp 값 `0x2001~0x2007`·`0x2009`·`0x200b`·`0x200d`·
   `0x2016~0x2017`·`0x2019~0x2024` 는 **어떤 명령의 displacement 로도 등장하지 않는다**.
   이는 필요조건이지 충분조건이 아니다 — 다른 base 로의 접근·`memcpy`/`memset` 경유를
   배제하지 못하므로 **런타임 상수성 확인이 필요**하다.
2. **기존 세이브 호환 규칙.** 구멍으로 옮기면 구 세이브는 그 자리에 0(또는 쓰레기)을 담고 있다.
   후보: 로드 후 로스터(`+0xd4a`, 길이 `+0x200a`)를 순회해 `used` 를 **재계산**한다 —
   두 필드 모두 같은 blob 안에 있으므로 자족적이다. 재계산 규칙 자체는
   `supply_200c_accumulation_rule_0726.md` 가 원본 실측으로 확정해 두었다.
3. **부호 확장 교체 후 게이트 의미 동일성.** reader 7곳은 `movsx r32, word`(7B)에서
   `mov r32, dword`(6B)로 **1바이트 짧아진다** ⇒ 제자리 교체 + `nop` 1개로 길이 보존 가능.
   writer 2곳은 `66 01/29 …`(7B) → `01/29 …`(6B) + `nop`, 단 `dx` 를 실어 오는
   `mov dx, word [edx*4+0x9b5238]`(`66 8b …`, 8B)을 `movzx edx, word [...]`(`0f b7 …`, **8B 동일**)로
   바꿔 상위 16비트를 0으로 만들어야 한다. **위 바이트는 middle 이 종이 위에서 유도한 값이다 —
   work tier 가 디스어셈블로 재확인한 뒤 쓴다**(lap393 §C 와 같은 규칙).

## 관련

- [[supply-200c-accumulation-rule-0726]] — `+0x200c = Σ cost[type]` 누적 규칙(원본 런타임 실측)
- [[player-offsets]] — PlayerStruct 필드 표(`+0x200a`~`+0x2012` 2바이트 연속)
- [[hero-limit-supply-patch-sites-20260921]] — `+0x2012` 공식과 그 사이트(§0 정정의 원출처)
- [[g2-kind-supply-cost-table-lap507-20260923]] — kind별 보급비, `c_max=65`
- [[g2-capacity-boundaries]] — 전비/개수 상한의 G2 제약
