# lap439 middle — W18 독립검수: **(M1) ACCEPT + 근본원인 확정**, 범인은 게임 코드가 아니라 **후보 빌드의 immediate 재배치 오탐**

- 날짜: 2026-09-21 KST
- lap: 439 (`loop/.lap_counter` = 439)
- 역할/모델: **middle(진단·중간계획·컨펌)** — Claude Code `claude-opus-5` / high
- 검수 대상: lap438 W18 실행 결과(Root 동기 복구 run2, INBOX 2026-09-21 06:38)
- 목표: G2 P2 — 원본 생산/AI 경로에서 N=4001 후보가 tick11,928 `0x00414133`에서 죽는 원인
- 게임 실행 **0회**, 제품 코드 수정 **0**, probe 작성 0, 커밋 **0**, 이번 회차 **source 미변경**

---

## 1. 가설과 판정

카드 `G2_UNIT_700_WATCHPOINT_EIP_ATTRIBUTION_LAP437.md`(W18) §5 판정식:

**(M1) 귀속 성공 — `E = 0x0040EFC5`, 후보 `.text` 범위 안(`0x401000 ≤ E < 0x4F9000`).**
정적 귀속까지 마쳤고, 그 결과 **인과 사슬의 최상류가 닫혔다**. 다음은 **수리 카드**이며
strategy 판정을 거치지 않는다(카드 §5 규정).

추가로 W18이 예상하지 않았던 결과가 나왔다: **범인은 "누가 잘못된 주소에 쓰는가"가 아니라
"왜 올바른 주소에 쓰레기 값이 들어가는가"였다.** 주소는 처음부터 정상이었다.

---

## 2. lap438 산출물 독립 재계산 (비참조)

`temp/Syw2plus_patch/g2_capacity/20260921_lap439_middle_review/recheck439.py`
(lap438 `orchestrator.py`/`gdb_watch.py` **비참조**, 카드 §3-A/§3-C 정의만으로 재작성).
출력 `recheck439.json`. 입력은 핀된 `original.bin`(`b56986e0…`)·`candidate.bin`(`4331d9cd…`)뿐.

| 항목 | lap438 보고 | lap439 재계산 | 일치 |
|---|---|---|---|
| 감시 주소 산술 `0x0108C000+3565*0x758+0x6f8` | `0x016F0B70` | `0x016F0B70` | ✓ |
| 트리거 `$pc` | `0x40efcb` | 명령 경계임을 5 anchor 수렴으로 확인 | ✓ |
| 직전 store `E` | `0x40efc5` | `0x0040EFC5`, 길이 6, `E+6 == $pc` | ✓ |
| store 형태 | `mov %edx,0x6f8(%esi)` | `89 96 f8 06 00 00` = `mov [esi+0x6f8],edx` | ✓ |
| `esi` | `0x016F0478` | `= unit3565` 정확 일치 | ✓ |
| `edx` | `17` | `= new value 17` 정확 일치 | ✓ |
| 원본 대비 store 바이트 | 동일 | 동일 | ✓ |

**불일치 0.** lap438의 (M1) 형식 판정과 함정 2건 회피(정방향 디스어셈블)는 모두 올바르다.

---

## 3. 근본 원인 (신규, 결정적) — N51

### 3-A. 세 필드는 **한 루프의 세 형제 store**다

`0x0040EF5C`~`0x0040F05B`가 한 루프다. 정방향 디스어셈블 실측:

```
0040ef3b: mov eax, ds:0x8924b8      ; 전역 tick
0040ef42: mov ecx, 0xc8 ; div ecx   ; edx = tick % 200
0040ef4b: jne 0x40f068              ; 200 tick 마다만 진입 ⇒ 이후 edx == 0
0040ef52: mov ebx, 0x669c58         ; 표 시작 (immediate, 후보에서 **불변**)
0040ef5c: <루프 머리>               ; edx = 반복 인덱스
   ...   ; bp = word[edi*2+0x959a8c] ; 0 이면 tail
   ...   ; test [eax*4+0x9b528c], ebx ; 요구 마스크, 불일치면 tail
0040efaa: mov eax,[esi+0x6f8] ; test ; jne  -> 0x40efcb
0040efc5: mov [esi+0x6f8], edx      ; ★ lap438 watchpoint 가 잡은 store
0040efcb: mov eax,[esi+0x6fc] ; test ; jne  -> 0x40f008
0040f002: mov [esi+0x6fc], edx      ; ★ 같은 edx
0040f008: mov eax,[esi+0x700] ; test ; jne  -> 0x40f046
0040f040: mov [esi+0x700], edx      ; ★ 같은 edx  (= K, 사슬의 최상류)
0040f046: <tail> mov ebx,[esp+0x10] ; inc edx ; add ebx,0x8c
0040f051: cmp ebx, <BOUND>          ; ★ 종료 즉치
0040f05b: jl  0x40ef5c
```

즉 "세 슬롯 중 비어 있는 첫 칸에 **현재 반복 인덱스 `edx`** 를 넣는다". 세 store 모두
`esi`(= 유닛 자기 base)를 쓰므로 **주소는 정상**이고, 바이트도 **원본과 동일**하다.

### 3-B. 후보는 그 루프의 **종료 즉치**를 망가뜨렸다

`0x0040EE00`~`0x0040F070` 전 구간에서 원본↔후보가 다른 바이트는 **정확히 4개**뿐이다:

| 파일 오프셋 VA | 원본 | 후보 |
|---|---|---|
| `0x0040F053`..`0x0040F056` | `cmp ebx, 0x0066B7B0` | `cmp ebx, 0x0108C020` |

표 시작 `0x00669C58`은 **불변**이다. 따라서 반복 횟수가 바뀐다:

| | 원본 | 후보 |
|---|---|---|
| 표 범위 | `[0x669C58, 0x66B7B0)` = 정확히 **50개** × `0x8C` | `[0x669C58, 0x108C020)` |
| 반복 횟수 | **50** | **75,900** |
| `edx` 최대값 | **49** | **75,899** |

실측 오염값 `{17, 16538, 22432}`를 이 사거리에 대보면:

- `17` → 원본 사거리 **안**(정상 값). 그래서 watchpoint 가 잡은 첫 전이는 **정상 동작**이었다.
- `16538`, `22432` → 원본 사거리 **밖**, 후보 사거리 **안**. ⇒ 두 값은 **후보가 만든 초과
  반복에서만 생성될 수 있다.**

`0x66B7B0 + 0xA20870 = 0x108C020`이고 `0xA20870 = 0x0108C000 − 0x0066B790`(= unit pool
재배치 delta)다. 즉 이 4바이트는 **후보 빌드의 풀 재배치 fixup이 쓴 것**이다.

### 3-C. 왜 fixup 이 이 즉치를 건드렸나 — 오탐

원본 unit pool = `[0x0066B790, 0x00892410)`. 종료 즉치 `0x0066B7B0`은 **수치상**
`POOL_BASE + 0x20`이라 그 구간 안에 들어간다. fixup 은 이것을 "슬롯0의 `+0x20` 필드를
가리키는 주소"로 **오분류**하고 delta 를 더했다. 실제로는 **무관한 50항목 표의 exclusive
end bound**이며, 주소가 아니라 경계값이다.

### 3-D. 오탐은 1건이 아니다 — 후보 imm 사이트 28개 중 최소 25개가 쓰레기

`patches/population/g2_unit_pool_expansion_v1.collect_fixup_sites()`를 핀된 원본에 돌려
`unit_pool` 의 **immediate** 사이트를 전수 재스캔하고, 후보 바이트와 대조했다.
**28개 전부 `+0xA20870` 재배치됨.** 값별 집계:

| 원본 즉치 | 건수 | 정체 | 실측 디스어셈블 |
|---|---|---|---|
| `0x0066B790` | 3 | 진짜 pool base | (정당해 보임) |
| `0x0066B7B0` | **8** | 50항목 표 end bound | `cmp edx,0x66b7b0`(`0x420582`), `cmp eax,0x66b7b0`(`0x4A3FAF`), `cmp ebx,…`(`0x40F051`) |
| `0x00800000` | **11** | **비트마스크(bit 23)** | `test eax,0x800000`(`0x401BC2`), `test esi,0x800000`(`0x4A8385`) |
| `0x00800807` / `0x00801007` / `0x00800010` | 3 | 상수 | — |
| `0x00870087` / `0x00878700` | 2 | 상수 | `push 0x870087` / `push 0x878700`(`0x4A9F8C`/`0x4A9F98`) |
| `0x0067F6F8` | 1 | 미분류 | `push 0x67f6f8`(`0x491723`) |

`test eax, 0x800000` → 후보에서는 `test eax, 0x1220870` 이다. **비트 테스트의 의미가 통째로
바뀐다.** 이런 사이트가 11곳이다. 디스어셈블로 **확인한 오탐 8건**, 값 분류상 **오탐 강력
의심 17건 추가**, 정당해 보이는 것은 `0x0066B790` 3건뿐이다.

`unit_existence`(2건)·`unit_age`(2건) 의 imm 은 배열 base(`0x8990C8`/`0x899A28`) 자체이고
성장 보정 delta(`0xF1F590`/`0xF20B72`)를 썼다 — 이쪽은 의도된 것으로 보인다.

### 3-E. 코드 상의 결함 위치

`patches/population/g2_unit_pool_expansion_v1.py::_region_sites` (L180–226):

- **disp 분기**는 가드가 둘 있다 — base/index 레지스터 없으면 `BuildAbortedError`(L210–214),
  `disp - base >= elem_size`(버킷0 이탈)면 `BuildAbortedError`(L215–220). 그래서 `unit_pool`
  disp 986건은 전부 `[0x66B790, 0x66BEE8)` 안이고 안전하다.
- **imm 분기**(L222–225)는 **가드가 하나도 없다.** `base <= value < old_end` 이기만 하면
  무조건 사이트로 채택한다. 근거는 docstring L196–199의 전제
  *"an imm **is** the final literal address of one specific slot"* — 이 전제가 **거짓**이다.
  즉치는 마스크·경계값·패킹 상수일 수 있다.
- 유일한 방어는 `FO4_EXCLUDED_VAS = {0x00421349, 0x0048F4B4}`(L97–99) — lap398이 손으로 찾은
  **"즉치가 POOL_BASE와 정확히 같은 cmp 2곳"** 이다. **같은 결함 계열을 이미 한 번 만났으면서
  규칙이 아니라 VA 2개짜리 denylist로 막았다.** `POOL_BASE + 0x20`은 그 그물을 통과했다.

후보 `4331d9cd…` 의 빌드 사슬:
`runtime_driver` → `g2_full_capacity_persistence_compat_v1` → `g2_full_capacity_persistence_v1`
→ `g2_full_capacity_supply5000_owner1200_v1` → `g2_full_unit_capacity_supply5000_v1`
→ `g2_full_unit_capacity_v1.build_candidate`.
`g2_full_unit_capacity_v1.py`는 자체 `_list_region_sites`(L104–129)를 쓰는데 **imm 분기
(L120–122)에 같은 결함**이 있고, L145에서 교차검증용으로 부르는 `_region_sites`는 위 모듈에서
import 한 **같은 결함을 가진 함수**다 ⇒ **두 스캐너가 같은 실수를 해서 교차검증이 성립하지 않는다.**

---

## 4. 뒤집히는 이전 결론 (정정)

| 결론 | 출처 | 이번 판정 |
|---|---|---|
| **(J2) "외부 write 확정"** | lap427 → lap428 ACCEPT | **REJECT.** 범인은 `0x40efc5`/`0x40f002`/`0x40f040` — 전부 이미지 내 **알려진 게임 코드**이고 lap424 스캔에 있던 4곳 중 하나다. 외부 모듈/힙 아니다. |
| `0x40f040` 배제 근거 = "`+0x388`을 복사하므로 `src`가 0이면 무죄" | lap427, lap428 L98·L102 "유효" | **전제가 사실이 아니다.** lap424 자신의 `scan424_sites_700.json`이 `0x40f040 : mov dword ptr [esi+0x700], **edx**` 로 기록해 두었다. `+0x388` 복사 site가 아니다. 이 한 줄의 오독이 lap427~438 **12바퀴**를 범인을 배제한 채로 돌게 했다. |
| **(J3)/(K2) "블록/OOB write"** | lap427 확정 → lap428 N40·lap431 N44로 SUPPORTED 강등 | **REJECT.** 세 store 는 각각 독립 분기의 스칼라 store 다. lap438 watchpoint 가 `+0x6f8`만 17로 바뀌고 `+0x6fc`/`+0x700`은 **아직 0**인 순간을 직접 잡았다 ⇒ 원자적 블록 복사가 아니다. lap428/431이 강등해 둔 판단이 옳았고, 이번에 완전히 닫힌다. |
| **(L2) 단발형 / 순회 루프 계열 소거** | lap436 §23 | **유지.** 오염 루프는 **풀 순회가 아니라** 유닛 1기 처리 중 도는 **정적 표 루프**다. lap437 **N50**이 예고한 "잘못된 stride/사거리 루프는 (L2)로 소거되지 않는다"가 바로 이 경우다. (L2)는 참이었고 오도하지 않았다. |
| **N43** "1200 순회는 `0x16F0B78`에 사거리 미달" | lap428 | **유지·재해석.** 사거리 논증은 옳았다. 애초에 **주소가 잘못된 적이 없기 때문**이다 — `esi`는 언제나 정확한 유닛 base 였다. 손상된 것은 **값**이다. W14~W18이 통째로 "누가 잘못된 주소에 쓰는가"를 물었는데, 물어야 했던 것은 "왜 값이 사거리를 벗어나는가"였다. |

---

## 5. 확정된 인과 사슬 (전 구간 폐쇄)

```
빌드: g2_full_unit_capacity_v1 imm fixup 오탐
      └ 0x0040F053: cmp ebx,0x0066B7B0  →  cmp ebx,0x0108C020   (+0xA20870)
런타임: 0x40ef5c 루프가 50회 대신 75,900회 반복
      └ edx(반복 인덱스)가 49를 넘어 무제한 증가
      └ 0x40f002 / 0x40f040 이 그 값을 유닛 필드에 저장
         (정상 주소·정상 명령·원본과 동일한 바이트)
      └ 슬롯3565: +0x6f8=17(정상), +0x6fc=16538, +0x700=22432(K)  [tick 10400]
사슬: K(+0x700) → m(+0x68c)=347349 → f688(+0x688)=(10+347349) mod 65536 = 19679
      (lap425/426 확정, lap434 재현 — 산술 그대로 성립)
크래시: 0x00414133 이 100칸 stack 배열을 ((경로점수-1)×|+0x692|)/100 로 인덱싱
      → read 0x00338400 page fault @ tick 11,928  (lap413/414, 4회 재현)
```

stock-layout 대조군이 같은 tick 을 fault 없이 통과한 것(lap413)과 정확히 일치한다 —
대조군은 이 imm 을 재배치하지 않았다.

---

## 6. 수치·산출물

- `recheck439.py` / `recheck439.json` — 위 모든 수치의 기계 재생성.
- 5 anchor 정방향 디스어셈블 수렴으로 `0x40EFC5`·`0x40EFCB` 명령 경계 확인.
- 루프 구간 diff = **4바이트**(`0x40F053..56`)뿐.
- imm 사이트 32건(unit_pool 28 / existence 2 / age 2) 전수 대조, 재배치 32/32.
- 원본 `b56986e0…c9c08a8ac` **직접 재해시** 불변(`/home/dev_00/sharedfolder/260320_Syw2plus/syw2plus_original.exe`).

## 7. 검사

- 표적: `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` → **6 passed (50.43s)**.
- `checks/safety.sh check` → **SAFETY_PASS**.
- 통합 `make check` **생략** — 이번 회차 **source 를 바꾸지 않았다**(INBOX 2026-09-20 21:58 규칙,
  N22 정정 준수).

## 8. fixture

lap438 run2 = op7 resource-only / 8 owner / N=4001 / seed42, display 격리, 후보 `4331d9cd…`.
이번 회차는 그 **원시 산출물과 핀된 두 바이너리만** 입력으로 썼다(게임 실행 0).

## 9. PASS / FAIL / SKIP

- W18 (M1) 형식 판정: **ACCEPT**
- lap438 측정 재계산: **ACCEPT (불일치 0)**
- 근본 원인 귀속: **확정 (N51)** — 게임 코드 결함 아님, 후보 빌드 fixup 결함
- (J2)/(J3): **REJECT** (정정)
- 제품 완료: **아님.** 수리 미착수, 실행 재검증 없음.

## 10. 다음 행동

**수리 카드 W19** `docs/work/active/G2_IMM_FIXUP_FALSE_POSITIVE_REPAIR_LAP439.md` 발행.
다음은 **work 회차(Sonnet5/high)** 이며 진단 카드가 아니라 수리다. 상세는 그 카드와
`loop/ESCALATE_SOL` §25.

## 11. 역할 경계

middle 은 검수·귀속·카드 정의만 했다. **게임 코드/빌드 코드 수정 0**, 게임 실행 0, 커밋 0.
`0x40efc5` 및 어떤 즉치도 이번 회차에서 고치지 않았다(INBOX 06:38의 "추측 패치 금지" 준수).
자기 결과를 자기가 최종 승인하지 않는다 — 수리 후 독립 검수는 다음 middle 회차다.
