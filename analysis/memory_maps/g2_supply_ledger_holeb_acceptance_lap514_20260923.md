# G2 F4(B) 안 B — `+0x2016` 이사 + `used` 제자리 dword 독립 수용 근거 (lap514 middle, 2026-09-23)

- 판정자: Claude Code `claude-opus-5-5` / high, 지정 역할 middle(컨펌). 읽기 전용, 게임 실행 0.
- 원본: `Syw2plus/syw2plus_original.exe` SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(전후 불변).
- probe: `docs/history/laps/probes/20260923_lap514_middle_w30_holeb_independent_recompute.py`(exit 0),
  산출 `…/temp/Syw2plus_patch/g2_capacity/20260923_lap514_middle_w30_holeb_review/w30_holeb_independent_recompute.json`
  SHA256 `0c0ed0d22b9e522e2f97ef4f87212b4fbb961010b5389132b5bcb3d1c1712359`(2회 실행 동일).
- 선행: 사이트 인벤토리 `g2_supply_ledger_200c_site_inventory_lap509_20260923.md`, 안 A 기각 `g2_supply_ledger_hole_rejection_lap511_20260923.md`.

## 1. 겹침 기준 전수 스캔 (정확 disp 일치가 아니라 `[disp, disp+size)` 겹침)

`.text` 선형 디스어셈블 306,187 명령(lap509와 같은 수). base/index가 있는 피연산자 전부와,
PlayerStruct 배열 `0x956770 + k·0x3ABC` 안에 떨어지는 절대 disp 전부를 필드 상대 오프셋으로 환산했다.

| 범위 | 겹치는 접근 | 판정 |
|---|---|---|
| `[0x200c,0x2010)` (used+구 building) | 13곳 = §1 used 9곳 + building 4곳(`0x43DB24`·`0x43E204`·`0x43EEAD`·`0x43EF9D`) + `lea` 1곳 | 인벤토리와 일치. 누락 0 |
| `[0x2016,0x2018)` (새 building) | `0x43F57F mov dword [ecx+esi*4+0x2014], edi` 1곳 | 비도달(§2) |

- `0x444C63 lea ecx,[ecx*4+0x95877a]`: `ecx = owner·0xEAF`(=stride/4) ⇒ `&PS[owner].count(+0x200a)`.
  같은 함수의 실제 접근은 `0x444C5B cmp word [..],bx`·`0x444CC9 cmp bx, word [ecx]` 둘 다 **word @`+0x200a`**
  ⇒ `used`/building을 건드리지 않는다(스캔이 `lea`를 4B로 잡아 생긴 오탐).
- `lea` disp∈`[0x1ff0,0x2030)` 전수 5곳 중 나머지: `0x40B923 lea ecx,[edi+0x2000]`(플래그 산술 `|0x2000`),
  `0x48FDD7`/`0x48FDE8`(esp 상대 스택), `0x4B1EE0 lea eax,[esi+edx*4+0x2018]`(리스트 원소 ≥`+0x2018`). 전부 무관.
- 배열 밖 별칭 4곳(`0x4BBBC9`·`0x4BBBDF`·`0x4C2824`·`0x4C282A`, 절대 `0x975D5C`/`0x975D64`)은
  PS[8] 자리(`0x973D50`+)로 환산될 뿐 PlayerStruct는 8개(`0x973D50`에서 끝)다 — 배열 밖 전역(`0x8925E0`/`0x8925E8`과 dword 비교)이라 패치 사이트와 무관(용도 미해독).

## 2. `0x43F57F`가 `+0x2016`에 닿지 않는 이유 (원본 바이트)

```
0043f569 mov edx, 1
0043f56e cmp si, dx ; jle 0x43f590
0043f574 movsx esi, dx        ; esi = 1, 2, ...
0043f577 inc edx
0043f578 mov edi, [ecx+esi*4+0x2018]
0043f57f mov [ecx+esi*4+0x2014], edi   ; esi>=1 ⇒ 쓰기 주소 >= +0x2018
```
리스트 앞당김 루프다. `esi` 최솟값 1 ⇒ 가장 낮은 쓰기는 `+0x2018`. `+0x2014..+0x2017` 을 dword로 덮는 경로는 없다.

## 3. 9개 used 사이트 뒤 소비 폭 (dword 확장이 의미를 바꾸지 않는가)

| 사이트 | 뒤따르는 소비 | 결론 |
|---|---|---|
| `0x43EDFC` | `add edx,eax(movsx cost)` → `cmp edx,ecx(movsx limit)` → `jle` | 32-bit 부호 비교 |
| `0x43F0E9` | `add eax,[esi+0x1c]` → `add eax,edi` → `cmp eax,edx` → `jg` | 32-bit |
| `0x43F3B3` | `add eax,[ebp+0x1c]` → `push eax` → `call 0x4E4146`(radix 10 문자열) | 32-bit |
| `0x40DD12`·`0x40E03B`·`0x499767`·`0x499A0E` | `add r,[+0x1c]` → `add r,ebp/edx` → `cmp r,(movsx limit +0x2012)` | 32-bit |
| `0x43EE9B`/`0x43EF8B`(writer) | 직전 `movzx edx, word cost`(패치) → dword add/sub → 뒤 `mov dl,[eax+0x66b968]`는 add/sub **이후** | 상위 16bit 쓰레기 없음 |

16-bit로 값을 다시 자르는 소비(`cmp dx,…`, `mov [..],dx` 등)는 0건이다. 따라서 `used ≤ 32,767`에서 원본과 같은 비교 결과,
`used = 78,000`(구조적 최대)에서 부호 반전 없음 — 이것이 M-e/M-f의 **기계어 수준** 근거다
(`test_supply_ledger_32bit.py`의 M-e/M-f는 Python 산술 모델이라 패치 바이트와 독립이다).

## 4. 런타임 (원본 EXE, lap513 24k soak 원시 재계산)

`samples.jsonl` 721줄 × 8 owner = 5,768 owner-표본의 `window_hex` 원시 바이트에서 `+0x2016..+0x2018` 재추출:
위반 0, 비영 0, 기준값 전 owner `0000`, tick 16→24,019 단조. 이웃 필드가 살아 있음: 리스트 count `+0x2014`
최대 [9,9,11,55,9,9,9,11], `used` 최대 1,615, building 최대 20, 원소 창 비영 5,752/5,768.

## 5. 남는 한계

- 후보 EXE(`1893ff50…`) 실제 게임 실행 0 — Q9 미결 그대로. 이 문서는 G2 제품 합격 근거가 아니다.
- `memcpy`/`rep movs` 경유 필드 접근은 정적으로 배제하지 못했다(전체 블록 복사는 바이트 보존이라 무해, 필드별 직렬화는 disp 스캔에 잡힌다).
- 구세이브: `[0x200c,0x2010)`=`used|building<<16` 해석 ⇒ 재계산 훅 전까지 후보는 신규 게임 전용.
