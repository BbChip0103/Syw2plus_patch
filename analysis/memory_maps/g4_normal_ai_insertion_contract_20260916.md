# G4 정상 simulation→AI 삽입 경계 조사 (discovery-only)

- 조사일: 2026-09-16 KST
- 상태: **BLOCKED — 정적 경계는 충분히 좁혀졌지만 제품 삽입/활성화 계약은 미확정**
- 목적: Astra/medium의 bounded idle-combat reinforcement 후보를 구현하기 전, 정상 simulation tick에서 원본 AI 선택기가 호출되는 경계·호출 규약·주기·모드·저장 경계를 읽기 전용으로 정리한다.
- 금지/비범위: 원본 EXE/DLL/게임 데이터/세이브 쓰기, Ghidra 전체 재생성, 게임/런타임 실행, CHB·`imeGetTime` wall-clock 반복, 후보 구현/패치.

## Provenance

| 자료 | SHA256 / 방법 |
|---|---|
| `Syw2plus/syw2plus_original.exe` | `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` |
| PE | PE32, image base `0x00400000`; `.text` VA `0x00401000`, raw `0x1000`; therefore VA `0x004xxxxx` byte offset = `VA - 0x00400000` |
| Ghidra reference `FUN_0041cb40.c` (sibling read-only repo) | `f5ecaa576bb48d25a556a073931b011101a013a92d22875ecc782f11a619e4fe` |
| Ghidra reference `FUN_0043f5d0.c` (sibling read-only repo) | `5f56ade20bc8fa0b5e2993e940a3c6f63c25d393dc2455b562be7271a6858774` |
| Ghidra callgraph reference | `81e2443e1da681bf98470d845f7eae0c7711fc9bf7d71c2894a242708990fa49` |
| Existing G4 original-order diagnostic contract | `docs/history/laps/20260916_g4_original_order_issuer_probe.md`, SHA `f5e5a3155446320888edc9ab1c44cba328ea1a5c6d6c78a368c049bf32e3dda8` |

원본 bytes는 `objdump -Mintel -D --start-address ... --stop-address ...`로 직접 읽고,
Ghidra 출력은 보조 교차확인으로만 취급했다. 아래 `확정`은 이 SHA의 동일 PE에만 적용한다.

## Hypothesis gate

| 가설 | 조사 결과 | 판정 |
|---|---|---|
| H1. 정상 게임 simulation 경계는 `FUN_0041C770 → FUN_0041CB40 → FUN_0043F5D0`이다. | `0x41C770`에서 타이밍 통과 뒤 `0x41CB40`을 호출하고, `0x41CB40` 정상 블록에서 `0x43F5D0`을 한 번 호출하는 exact branch/call bytes가 확인됨. | **FEASIBLE (static only)** |
| H2. owner/cadence/mode/save 경계를 stateless하게 구현할 수 있다. | owner 선택과 호출 ABI, Unit pending 위치는 닫혔지만 allowlist-to-call edge·pause/replay/재진입·load 직후 first-step 및 duplicate guard가 추가 증명을 요구한다. | **BLOCKED** |

### Narrow follow-up gate (two hypotheses, read-only)

| 가설 | 이번 bounded 확인 | 판정 |
|---|---|---|
| H3. local free-battle allowlist를 candidate call에서 양성 판별할 수 있다. | `PS==3`, committed solo/local `4ED848==1`, scenario selector `9E1DD8==0`, network/modal zero, supplementary AI raw gates zero라는 fail-closed 후보를 만들 수 있다. 기존 양성 분류기 `FUN_0041B440()==2`의 caller는 확인했지만 `41C770→41CB40`에서 그 getter가 실제 실행된다는 edge는 찾지 않았다. | **BLOCKED — concrete missing getter-to-call edge** |
| H4. load 후 첫 normal step이 pending/preexisting guard와 연결된다. | `40FF0→40F4F0` bulk/Unit restore와 `412540→40C640` pending issuer/consumer guard는 확인했다. 그러나 load state machine 이후 첫 accepted tick increment→`41CB40` 및 preexisting pending duplicate suppression을 한 정적 edge로 닫지 못했다. | **BLOCKED — concrete missing first-postload edge** |

이 follow-up은 원본 PE와 기존 export/Ghidra 산출물의 읽기 전용 확인만으로 60–90분/실패 가설 2회
한도를 적용했다. 위 두 concrete edge가 닫히지 않은 상태에서 추가 전수 graph/decomp, 런타임 실행,
CHB/`imeGetTime` wall-clock 우회, 제품 구현으로 확장하지 않는다.

## 1. Exact normal path and call shape

### `FUN_0041C770 @ 0x0041C770`

- prologue bytes (file offset `0x1c770`): `83 EC 08` — 8-byte stack reservation.
- `0x0041C770`의 정적 본문에서 `0x008924B8`을 읽고, 타이밍 통과 경로에서:
  - `0x0041C8C0`: `A1 B8 24 89 00 40 83 F8 14 A3 B8 24 89 00` — simulation tick increment/store (초기/특수 early-return 경로는 별도).
  - `0x0041C8F3`: `E8 48 02 00 00` — `call 0x0041CB40`.
- `0x004245D0`에는 `E8 99 81 FF FF` (`call 0x41C770`)가 무조건 있고, `0x004250F7`에는 조건부 `E8 74 76 FF FF`가 있다. 따라서 “프로세스 frame당 정확히 한 번”을 정적으로 단정하지 않는다. 정상 accepted call의 실제 횟수는 두 caller의 상태/분기 조합으로 확인해야 한다.

### `FUN_0041CB40 @ 0x0041CB40`

- prologue/기초 상태 bytes (file offset `0x1cb40`):
  `A1 C8 24 89 00 33 D2 A3 CC 24 89 00 A1 C4 24 89 00 8B C8 83 EC 08`.
- `0x8924C4`를 `0xFF83` multiplier, modulus `0xFFFB`로 갱신하고 `0x8924C8`에 저장한다. 이 RNG update는 AI target order의 admission proof가 아니다.
- `0x41CB6F`의 raw mode gates:
  - `66 39 1D 82 39 B9 00` → `WORD [0x00B93982]`가 `0`이 아니면 `0x41CE98`로 우회.
  - `66 39 1D 88 39 B9 00` → `WORD [0x00B93988]`가 `0`이 아니면 `0x41CC03`로 우회.
  - 두 값 모두 0인 branch에서만 `0x4C6F90`, `0x4A86B0`, 8×`0x43FDD0`, 그리고 아래 `0x43F5D0`이 실행된다.
- `0x41CBE5` exact call bytes: `E8 E6 29 02 00` → `call 0x0043F5D0`.
- direct caller의 호출 직전 `ECX` 계산은 다음과 같다.

```text
owner = [DWORD 0x008924B8] & 7
ECX = 0x00956770 + owner * 0x3ABC
```

실제 bytes `0x41CBC6..0x41CBE5`:
`A1 B8 24 89 00 83 E0 07 8D 0C 40 C1 E1 04 2B C8 8D 14 89 C1 E2 04 2B D0 8D 0C 95 70 67 95 00 E8 E6 29 02 00`.
산술은 `3*owner`, `47*owner`, `235*owner`, `3759*owner`, 최종 `4*3759=15036=0x3ABC`로 풀린다.

### `FUN_0043F5D0 @ 0x0043F5D0`

- entry bytes: `53 55 56 8B F1 BB 01 00 00 00 57`.
- raw ABI: caller는 `ECX=controller`만 전달하고 stack argument를 push하지 않는다. 이 zero-argument ECX-only 모양만으로 `__thiscall`과 `__fastcall`을 고유하게 구별할 수 없으므로, 여기서는 “ECX-only raw ABI”로만 기록한다. callee가 `EBX`, `EBP`, `ESI`, `EDI`를 보존한다; `EAX/ECX/EDX`는 보존 계약으로 사용할 수 없다.
- early return은 `EAX=0`; dispatched handler return들은 `EAX=1` 뒤 epilogue로 간다. `FUN_0041CB40`은 이 반환값을 제품 verdict로 소비하지 않는다.
- controller raw guards:
  - `+0x3020/+0x3034/+0x303C` 중 하나가 `1`이면 `+0x3386=1`, 아니면 0.
  - `+0x308A/+0x308C/+0x308E` 중 하나가 `1`이면 `+0x3148=1`, 아니면 0.
  - `0x008924B8 < 10` 또는 `((tick >> 3) % 10)==0`에서 census-like 100-entry preparation이 수행된다.
  - 그 뒤 `controller+0x00 == 0` 또는 `controller+0x02 != 1`이면 RNG/intent selection 전에 반환한다. `+0x00`, `+0x02`의 이 조사에서의 의미 라벨은 raw field로 보존하며, upstream writer/meaning proof 없이 새 이름을 부여하지 않는다.
  - intent RNG는 `(old 0x8924C4 * 0xFF83) % 0xFFFB`; selection value `%20`; `tick<20`이면 selection value를 0으로 강제한다. `+0x0D32==0`일 때만 20-way jump table `0x0043FD10`로 들어간다.

## 2. Cadence and owner round-robin contract

| 항목 | 정적 사실 | 구현 전 남은 확인 |
|---|---|---|
| 호출당 owner | 정상 원본 식은 계속 `tick & 7`, controller base `0x956770 + owner*0x3ABC` | call이 skipped/duplicated되는 outer state에서 logical tick과 call count의 관계 |
| one-shot per accepted simulation tick | `0x41CB40` 정상 branch의 `0x43F5D0` call은 branch당 1회이며 accepted tick 증가가 그 앞에 있다 | 두 outer caller(`0x4245D0`, 조건부 `0x4250E0`)가 같은 logical tick에 중복 진입하는지; frame-count 주장은 하지 않음 |
| uninterrupted round-robin | accepted tick이 증가하면 원본 owner 0..7이 `tick&7`로 순환 | pause/replay/load/reset에서 tick freeze/restore 및 gate words 전환 |
| pause/replay | `B93982/B93988 != 0`이면 정상 AI block을 건너뜀 | 두 word의 의미·모든 writer·재진입 순서. 의미를 pause/replay로 추측 금지 |
| 후보 stateless cadence | 원본 owner selector는 반드시 `tick & 7`로 유지한다. 별도 `round_index = saved_tick >> 3`는 8개 phase 전체에 동일 periodic eligibility를 적용할 때만 보조 cadence로 고려한다. 이를 두 번째 owner selector나 round-boundary 단일 owner로 쓰지 않는다. `tick % 300`을 owner selector로 쓰지 않는다. | eligibility period와 first-owner phase를 fresh static Sol review 및 정상 simulation evidence로 확인 |

`tick % 300`은 owner를 선택하는 식으로 사용하면 owner 0/4 등 일부 owner만 방문하는 starvation 가능성이 있다.
위 eligibility 제안은 원본 대체 사실이 아니라 상태 없는 후보 cadence이며, owner 선택은 원본처럼
`tick&7`로 남긴다. persistent counter/DLL wall-clock/`imeGetTime`을 사용하지 않는다.

## 3. Mode boundary: local free battle only (not yet closed)

### Confirmed raw predicates and positive allowlist candidate

1. `FUN_0041C770` 정상 path is reached from the two `FUN_004245D0`/`FUN_004250E0` call sites above.
2. `FUN_0041CB40`'s normal AI selection block requires `[0x00B93982] == 0` and `[0x00B93988] == 0`.
3. The surrounding `FUN_0041C770` logic also reads program-state `WORD [0x004ED818]`, but `FUN_0041CB40` itself does not use it as the shown AI-block predicate.
4. `FUN_0041B440` is an existing positive mode classifier. Its exact raw return-2 branch requires `DAT_009E1DD8 == 0` (first branch not taken) and `DAT_004ED848 == 1`; the return-2 path is then selected before the raw `B93960/B93964` fallback. Callers are `FUN_00493FF0` and `FUN_004D2D20` (callgraph reference above). Existing selector contract records `0x004ED848` as the post-confirm committed solo-mode WORD; this is a candidate discriminator, not proof that the getter is executed at the AI call.
5. Therefore the narrow **positive allowlist candidate at a candidate call** is `PS WORD [0x004ED818] == 3`, committed solo/local `WORD [0x004ED848] == 1`, scenario selector `[0x009E1DD8] == 0`, both network/modal words `[0x00B93960] == 0` and `[0x00B93964] == 0`, plus supplementary AI gates `[0x00B93982] == 0` and `[0x00B93988] == 0`. Any unknown/nonzero value is rejected; this is not an activation approval because the exact getter-to-call edge is absent.
6. `0x00B93982` has direct stores at `0x0041B4C7` (0), `0x00441467` (register value), `0x00444E93` (1), `0x00444EE6` (0). A direct absolute store for `0x00B93988` was not found in the scanned objdump output; indirect/callee writers remain open. These remain supplementary raw gates, not mode labels.

### Fail-closed mode table

| Mode / state | Current static decision | Evidence / limitation |
|---|---|---|
| Free-battle local normal | **Candidate allowlist only**: `PS==3`, committed solo/local `4ED848==1`, scenario selector `9E1DD8==0`, `B93960==0`, `B93964==0`, and supplementary `B93982==B93988==0` | `FUN_0041B440` return-2 is the positive static classifier candidate; it is not called on the shown AI edge, so activation remains blocked. |
| Paused / transition | **Disabled** | Any unknown/nonzero allowlist value rejects; `B93982/B93988` remain supplementary suppression gates, not semantic labels. |
| Replay | **Disabled** | No positive replay-exclusion predicate at the candidate call is proven beyond the allowlist. |
| Scenario/script | **Disabled** | `9E1DD8!=0` rejects the candidate; `FUN_0041E220` can alter frame progression, and the full scenario edge is not closed. |
| Editor / lobby / unknown | **Disabled** | `PS!=3` or any unknown allowlist field rejects. |
| LAN | **Disabled** | `4ED848!=1`, network/modal nonzero, or any unknown state rejects; no network serialization/determinism proof exists. |

The proposed candidate must call an exact already-approved original issuer only after this raw-mode predicate and must not infer support from a one-shot DLL bridge or from `EAX=1`.

## 4. Save/reset/load boundary

### Exact serializer facts

| VA | Exact bytes / call shape | Fact |
|---|---|---|
| `FUN_00440C20(slot)` save | `8B 4C 24 04 81 EC 00 01 00 00` | cdecl slot argument at `[ESP+4]`; private save path setup. |
| save bulk | at `0x440F02`: `68 7C 39 0E 00` (length `0xE397C`), `68 10 24 89 00` (source `0x892410`), call `0x4DA39F` | one bulk write to `[0x892410, 0x892410+0xE397C)` is statically present. |
| `FUN_00440FF0(slot)` load | `8B 4C 24 04 81 EC 04 01 00 00` | cdecl slot argument and 0x104-byte local frame. |
| load bulk | at `0x4412D2`: `68 7C 39 0E 00`, `68 10 24 89 00`, call `0x4DA4A9` | matching bulk read is statically present. |
| logical tick | `0x008924B8 = 0x00892410 + 0xA8` | tick is inside the serialized bulk, not a wall-clock substitute. |
| player array | base `0x00956770`, stride `0x3ABC`, 8 entries end `0x973D50` | eight PlayerStruct spans fit inside bulk; raw `+0x00`/`+0x02` values are present in these structures. |
| unit records | save after bulk calls `0x0040F4B0`; load after bulk calls `0x0040F4F0` | each existing roster slot is serialized/restored as a `0x758`-byte Unit record; absent load slots are zeroed. Unit pending fields `+0x384`/`+0x388` therefore belong to this Unit-record phase, not the bulk's semantic field map. |

The save/load bulk contains the simulation tick, group/roster state, and other global state, but it is not evidence that Unit pending `+0x384/+0x388` are bulk fields. The existing G4 diagnostic contract identifies `FUN_00412540` as writing Unit `+0x380/+0x384/+0x388/+0x38C` and `FUN_0040C640` as consuming that pending order. Do not reopen or relabel those semantics here; candidate probe constants must not be promoted to a patch contract.

### Reset, load, and first ordinary step

| Boundary | Static evidence | Closed / gap |
|---|---|---|
| Normal-game initialization latches | Existing `FUN_0041B480` writes `B93982=0`; `FUN_0041B560` resets nearby runtime latches including `B9396C`, `B93970`, `B93978`, `B9397A`, `B939A8`, and `B939B0`. | These are concrete initialization writes for observed gates/latches, not an exhaustive semantic writer inventory; `B93988` remains raw/unknown. |
| Rejected Unit reset attribution | `0x452270` initializes +0x388 and +0x1388 with 0x400 DWORDs each and touches +0x44A0/+0x54A0/+0x64A4. | This object is larger than 0x758 UnitStruct; coincident +0x380/+0x384 offsets do not prove Unit pending reset. Do not use this as Unit reset evidence. |
| Original order issue/consume | Existing diagnostic contract (`20260916_g4_original_order_issuer_probe.md`) records `0x415480→…→0x412540→0x40C640`; `0x412540` writes `+0x380/+0x384/+0x388/+0x38C`, and `0x40C640` checks current Unit state before promotion to active command. | This closes the existing pending/preexisting-order guard boundary for the diagnostic path only; no new issuer is authorized. |
| Save/load roster | `FUN_00440FF0` bulk-loads then calls `FUN_0040F4F0`; that loader restores existing `0x758` Unit records and zeroes absent slots. `FUN_00440C20`/`FUN_0040F4B0` are the matching save path. | Unit pending restoration location is closed; full identity/reuse proof and duplicate order after load remain open. |
| First post-load normal simulation | `FUN_00440FF0` itself does not call `41C770`; it returns through the save/load state machine (`FUN_004D6A40`/`FUN_00493CA0`), after which a normal dispatcher path can resume. | First post-load accepted tick and duplicate/preexisting-order behavior are not yet validated as a candidate execution contract. Runtime evidence is outside this discovery card. |

The first ordinary step must be proven as `accepted tick increment → 41CB40 → raw gates → Unit pending/preexisting-order guard`, with no duplicate issue and no slot identity substitution. Until that edge is closed, post-load activation remains blocked.

### Required but unresolved post-load guards

Before any product activation, a fresh static/runtime boundary must show:

- tick/group/roster restored by bulk, Unit pending restored separately by Unit-record phase, then consumed by an ordinary accepted `41C770 → 41CB40` step;
- no duplicate order when a preexisting pending/active order is present;
- no identity substitution after slot reuse;
- reset/new-game clears candidate latches without leaving a persistent DLL counter;
- first post-load normal step is deterministic and mode-gated.

No candidate activation follows from the serializer call alone.

## 5. Exact boundary summary and blocker

| Fact / evidence | Unknown or disqualifying gap |
|---|---|
| `0x41C770 → 0x41CB40` exact call bytes; accepted tick increment precedes AI; `0x41CB40 → 0x43F5D0` exact E8; `ECX=0x956770+(tick&7)*0x3ABC`; `FUN_0043F5D0` saves EBX/EBP/ESI/EDI. | Two outer callers prevent a static frame-count claim; logical-tick one-shot still needs an accepted-call trace or stronger static edge. |
| Positive candidate allowlist is `PS3 + committed local/solo mode + scenario selector zero + network/modal zero`, with B93982/88 only supplementary raw-zero gates. | Exact getter-to-candidate-call edge and exhaustive writer semantics are not closed; unknown values remain rejected. |
| Saved tick is bulk offset +0xA8; save/load bulk and post-bulk `0x758` Unit-record phases are exact; Unit pending +0x384/+0x388 are in Unit records. | Group/roster restore is mapped, but first post-load accepted tick→AI edge, duplicate/preexisting-order guards, and full identity/reuse proof remain unresolved. |
| Owner remains original `tick&7`; `saved_tick>>3` is only a possible all-phase periodic eligibility index, not a second owner selector. | Proposal is not original behavior or product approval; needs fresh Sol/high review before any implementation. |

**Final feasibility:** static insertion site is **FEASIBLE as a bounded research candidate**, but the actionable product contract is **BLOCKED** until the positive local allowlist is tied to the candidate call and save/reset/load first-step/duplicate guards are closed. `B93982/B93988` remain supplementary raw gates; exhaustive writer/label closure is not required for this discovery and must not be inferred. This document is not an implementation authorization, AI-quality proof, LAN proof, or user milestone approval.

## Final Sol/high stop audit / corrected blocker

**BLOCKED_MODE_EXCLUSION_AND_POSTLOAD_CONTRACT — product activation STOP.** Original getter need not already execute at the chosen AI call: a candidate can read proven raw predicates there. Missing original getter→AI edge itself is not a fundamental blocker. Actual unresolved obligations are unsupported-mode overlap/exclusion, first post-load accepted step/duplicate behavior, and exact candidate trampoline review.

Raw widths confirmed: scenario selector9E1DD8 WORD, committed4ED848 WORD, B93960/64 DWORD, classifier return AX. FUN4C3DA0 writes scenario WORD9E1DD8 and adjacent WORD9E1DDA=1. Preserve raw classifier/zero predicates without claiming exclusive LAN/replay/scenario semantics.

The earlier FUN452270 Unit-reset attribution is rejected as offset coincidence on a much larger object. Earlier initial artifact SHA511c55f304e57d19e2e2ea29c7611e1a6e189dc54211954b124d38bd84ec4628 is the reviewed pre-correction document, not current bytes. No further one-shot or discovery-document iteration is authorized by this stop audit. Reopen only with new concrete mode/load evidence or a separately reviewed bounded executable candidate contract; original/source/runtime unchanged.
