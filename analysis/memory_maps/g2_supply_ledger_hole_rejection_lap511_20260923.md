# 전비 장부 `used` 32-bit — lap510 구멍 `+0x2100` 기각 + 안 B 입력 (lap511 middle)

- 작성: 2026-09-23, lap511, middle(Claude Code `claude-opus-5-5` / high). 게임 실행 0·제품 source 변경 0.
- 검수 대상: lap510 work(W30 소비) — `analysis/memory_maps/g2_supply_ledger_used_hole_relocation_lap510_20260923.md`,
  `patches/population/supply_ledger_32bit.py`.
- 재현 probe: `docs/history/laps/probes/20260923_lap511_middle_w30_independent_review.py`
  (원본 읽기 전용, exit 0, 산출물 `/tmp/lap511/w30_independent_review.json`
  SHA256 `f3e9dcbd07eae83c069b905c19c158521e9455bdb47863ce3f195bac3a7b84ee`, probe 자체 SHA256
  `56b7e2a7961894d8f3abeea7efd43df33722b885d844b5a034d75210260050a5`).
- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 전후 불변.

## 1. `+0x2014`/`+0x2018` 는 용량 1,000칸 dword 리스트다 — `+0x2100` 은 그 58번 칸

원본 `0x43F4C0`(추가) · `0x43F4F0`(중복 없이 추가) · `0x43F550`(맨 앞 제거) 세 thiscall 함수:

```
0x43F4C0  mov  ax, word [ecx+0x2014]      ; count(word)
0x43F4C7  cmp  ax, 0x3e8                  ; 66 3d e8 03 — 용량 1,000
0x43F4D9  mov  dword [ecx+eax*4+0x2018], edx
0x43F4E0  inc  word [ecx+0x2014]
0x43F4F9  cmp  dx, 0x3e8                  ; 66 81 fa e8 03
0x43F532  mov  dword [ecx+edx*4+0x2018], eax
0x43F578  mov  edi, dword [ecx+esi*4+0x2018]   ; esi 는 1 부터
0x43F57F  mov  dword [ecx+esi*4+0x2014], edi   ; 한 칸 앞으로 당김
```

⇒ 원소 영역 `[0x2018, 0x2018+1000×4) = [0x2018, 0x2FB8)`. 끝 `0x2FB8` 은 다음 인덱스 배열의
시작 disp 와 정확히 맞물린다(9개 명령, `0x41233D` 등) — 로스터 `[0xD4A,0x200A)`=1,200×4 와 같은 패턴.
런타임도 일치: lap510 원시 window 에서 `+0x2014` 는 최대 9, `+0x2018…` 은 dword 원소로 증가.

- `+0x2100` = 원소 **58번**((0x2100−0x2018)/4). 리스트에 59개 이상 쌓이면 새 `used` 를 덮어쓴다.
- lap510 시도1 `+0x201c` = 같은 리스트의 원소 **1번** — 시도1/2 는 **같은 구조체**에서 실패한 것이다.
- lap510 런타임 상수(0/1,448, tick 6,018)는 이 표본에서 리스트가 9칸까지만 찼기 때문이며,
  24k~144k 에서 58칸 도달 여부는 UNKNOWN 이다. **정적 용량이 닿으므로 "정적 미참조" 조건 FAIL.**
- lap510 정적 스캔은 disp..disp+size 만 "사용됨"으로 쳐서 레지스터 인덱스 배열의 **범위**를 못 봤다
  (lap510 근거 문서 §1(b)가 스스로 적은 한계 그대로).

## 2. 패치 기계 부분은 독립 재계산 PASS

| 항목 | 결과 |
|---|---|
| 카드 §1·§6 11곳 old-bytes (카드 원문에서 옮긴 기대값) | 11/11 일치, `EDITS` VA 집합 = 카드 집합 |
| 후보 SHA | `7cb0faf3…` lap510 주장과 일치 |
| diff | 62바이트, 사이트 밖 0 |
| 패치 후 역디스어셈블 | 11곳 전부 의도(`mov r32,dword`/`add·sub dword`/`movzx edx,word`)+`nop` |
| create-copy → restore | 원본 SHA 재현 (`/tmp` 복사본, `Syw2plus/` 미접촉) |
| `+0x200c` 전수 (abs+base 별칭 포함) | 9곳 + `0x444C63 lea [ecx*4+0x95877a]`(=`+0x200a` count 포인터, `[ecx]` 만 읽음) ⇒ **N154 9곳 독립 재확인** |

## 3. 안 B 입력 — `+0x2016` 은 리스트 count 워드와 dword 배열 사이 2바이트 정렬 패딩

- 정적: `+0x2016` 을 덮는 메모리 오퍼랜드는 `.text` 전체에서 `0x43F57F mov dword [ecx+esi*4+0x2014]`
  하나뿐이고 `esi` 는 1 부터 시작(`0x43F569 mov edx,1` → `0x43F574 movsx esi,dx`)이라 `+0x2016` 에 닿지 않는다.
- 런타임(lap510 원시 재사용): attempt1·attempt2 **2,896 owner-표본 전부 `+0x2016`=0**.
- `+0x200e`(building_count) 접근 전수 **4곳, 별칭 없음**: `0x43DB24 movsx ecx,word[esi+0x200e]`·
  `0x43E204 cmp word[edi+0x200e],5`·`0x43EEAD inc word[ecx+0x200e]`·`0x43EF9D dec word[ecx+0x200e]`.
- 안 B = building_count 를 `+0x2016` 으로 옮기고(4곳 disp 만 교체, 같은 길이) `used` 를 `[0x200c,0x2010)`
  제자리 dword 로 확장(9곳 opcode 만 교체, disp 불변) + cost-load 2곳 `movzx`.
- 한계: 포인터 산술(`lea` 후 `[reg+k]`) 경유 접근은 정적 disp 스캔으로 완전 배제되지 않는다 —
  런타임 상수성은 **리스트 count 가 58 을 넘는 긴 창**에서도 다시 확인해야 한다(아래 handoff).

## 4. 구세이브 호환 — 안 B 에서는 재계산이 선택이 아니라 필수

구세이브 blob 에서 `[0x200c,0x2010)` 은 `used(16) | building(16)<<16` 이므로 안 B 후보로 로드하면
`used` 가 쓰레기 값이 되고 building_count(`+0x2016`)는 0 이 된다. ⇒ 로드 직후 로스터로 `used`
와 building_count **둘 다** 재계산하는 훅이 없으면 구세이브 로드는 금지다(신규 게임은 영향 없음).

## 관련

- [[g2-supply-ledger-used-hole-relocation-lap510-20260923]] — 기각된 구멍 선정 근거
- [[g2-supply-ledger-200c-site-inventory-lap509-20260923]] — 9곳 범위 원출처
