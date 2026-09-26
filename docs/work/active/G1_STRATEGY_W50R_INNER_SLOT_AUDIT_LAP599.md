# G1 W50R — DxWrapper inner D3D9 slot audit-only 1회 (lap599 strategy 판정, 2026-09-25 KST)

- 발행: lap599 strategy. 실제 모델은 Claude Code `claude-opus-5-5`(effort 세션 비노출)이며 계약 모델 Fable/Astra를 대신한다. 게임 실행0, 제품 source·도구 변경0.
- 근거: `loop/ESCALATE_SOL` §147·§148, `analysis/memory_maps/g1_w50_d3d9_wrapper_chain_20260925.md`, W50 카드 `docs/work/active/G1_STRATEGY_W50_HD_FINAL_OUTPUT_ACQUISITION_LAP596.md` §3~§6, 이 회차 정적 확인 N220.
- 수행 역할: **work**(Sonnet5 또는 Luna, high). 계획 회차를 끼우지 않는다. 그다음 middle이 독립 검수한다.

## 1. 판정

- §148에 동의한다. **G1을 계속하고 W50R audit-only fresh 정확히 1회를 허용한다.** G1 대안 경로(native 1600 표면 2배 blit)와 G4 전환은 W50R 결과가 §4 R3이 될 때만 다시 판정한다.
- 이유 세 가지:
  1. lap597의 `BLOCKED`는 가설 실패가 아니라 잘못 고른 호출 계층에서 생긴 `plan_contract` 결함이다(§148). 올바른 계층은 아직 한 번도 관측하지 않았다.
  2. W50 §3 fresh 예산은 최대 3회이고 A1·A3로 2회를 썼다. W50R은 그 **3번째이자 마지막** acquisition 관측이다. 새 예산을 열지 않는다.
  3. 제품/실행 증거가 늘지 않은 회차가 lap598·lap599로 2회 연속이다(PROMPT ③). 다음 회차는 실제 실행이 있는 work여야 하며, W50R이 그것이다.

## 2. N220 — inner chain 초기화 규칙 (strategy 정적 확인, 런타임 미증명)

원본 DxWrapper `96c44319…e8fe`를 `i686-w64-mingw32-objdump -d`로 읽기만 했다.

- `0x100DE65E..0x100DE66D`: `push 0x101BAC60`(inner source 주소) · `push 0x1000A750`(redirector) · `push 0x101B6654` · `call 0x10136110`. 정적 초기화 때 redirector와 inner source를 등록한다. §148과 일치한다.
- `0x1000A86C..0x1000A877`: inner guard `0x101BACC4`를 TLS epoch와 비교하고, 미초기화면 `0x1000A94F`로 간다.
- `0x1000A94F..0x1000A99D`: `_Init_thread_header(0x101BACC4)` 뒤 `validate(*0x101BAC60)`(`call 0x10136180`) 결과가 참이면 **inner cache := inner source**, 거짓이면 0을 쓴다. 이어서 footer를 부른다.
- `0x10136180` validator는 값이 0이거나 stub `0x1011A180`/`0x100506F0`이면 거짓이다. 등록 목록(`0x101F3BB4..0x101F3BB8`)에 있는 값은 그 대상이 stub이 아닐 때만 참이다. 목록에 없는 0이 아닌 주소는 참이다.
- `0x1000A87D..0x1000A8FE`: inner cache가 0이면 실패 경로(`0x1000A930`), 아니면 `call *0x101BACC0`.

**뜻:** inner guard는 redirector가 **처음 호출될 때**(= DxWrapper가 `Direct3DCreate9`를 처음 부를 때) 초기화된다. A3처럼 factory/device가 0인 early 창에서는 inner guard=0, inner cache=0일 가능성이 높다. 그러면 그 창에서 의미 있는 slot은 **inner source**다. inner cache는 첫 호출 때 inner source에서 다시 계산되므로 덮어써진다.

§148 handoff의 "inner source == inner cache == native export" 조건은 guard=0 창에서는 성립할 수 없다. 그대로 두면 다음 middle이 또 `plan_contract`로 막힐 수 있어서, 아래 §4처럼 guard 상태별 조건으로 정정한다. 같은 계층을 정확히 가리키므로 §148의 판정 방향은 바꾸지 않는다.

## 3. W50R 실행 계약

| 항목 | 내용 |
|---|---|
| 변경 허용 | `tools/inmm_stub/final_d3d9_trace.c`의 audit-only 기록 확장, `tests/test_final_d3d9_trace.py` 회귀 |
| 관측 시점 | 두 곳 모두 **읽기만**: (E) A3와 같은 early 관측 시점, (L) A1과 같은 지연 설치 시점 |
| 기록 값 | 각 시점의 top source/cache, **inner source `base+0x1BAC60` / inner cache `base+0x1BACC0` / inner guard `base+0x1BACC4`**, factory, device |
| owner | 기록한 각 포인터의 module base·path(`GetModuleHandleExA(FROM_ADDRESS)` 등 읽기 API) |
| native 기준값 | `GetModuleHandleA("d3d9.dll")`가 NULL이 아니면 `GetProcAddress(…, "Direct3DCreate9")`. NULL이면 `d3d9_not_loaded`로 기록. **`LoadLibrary` 호출 금지**(로드 순서가 바뀐다) |
| old bytes gate | 읽기 전에 rebased 명령 바이트를 확인한다: RVA `0xA969` = `FF 35 <base+0x1BAC60>`, RVA `0xA992` = `89 0D <base+0x1BACC0>`. 불일치면 inner 값을 읽지 않고 `inner_header_mismatch`로 기록 |
| 쓰기 | 0. CAS 0, guard/slot 쓰기 0. `INMM_FINAL_D3D9_CACHE_CAS`는 켜지 않는다 |
| 기본 경로 | 플래그 없음 경로의 guard≠0 skip과 기존 CAS 경로는 바꾸지 않는다. 테스트로 잠근다 |
| 실행 | fresh **정확히 1회**, 게임 ≤15분, 회차 ≤60분, 동기 실행. stock UI PS9→PS7→PS5→PS3 입력만. 시간이 부족하면 시작하지 않고 기록 |
| 보존 | final trace·modules/evidence·PS3 캡처 1장(공유 temp `captures/`)과 각 SHA, 원본 `b56986e0…a8ac`·DxWrapper `96c44319…e8fe`·ini `918e7043…a5a2` 전후 일치, owned prefix/display 잔류0 |

## 4. 결과 분류 (실행 전 고정)

- **R1 `INNER_SOURCE_NATIVE_EARLY`**: (E)에서 factory=device=0, inner guard=0, inner source=native 기준값≠0, owner=Wine `d3d9.dll`.
- **R2 `INNER_CACHE_NATIVE_EARLY`**: (E)에서 factory=device=0, inner guard 초기화됨, inner cache=inner source=native 기준값, owner=`d3d9.dll`.
- **R3 `INNER_NOT_NATIVE`**: inner source/cache가 0이 아닌데 owner가 `d3d9.dll`이 아니거나 native 기준값과 다르다(다른 wrapper 층). 또는 (E)·(L) 모두에서 native 기준값을 얻지 못했다.
- **R4 `WINDOW_OR_HARNESS`**: (E) 창을 못 잡았거나, header gate가 불일치했거나, 실행 오류가 났다.

(L) 값은 모든 분류에서 보조 증거로 기록한다. 예: (L)에서 inner cache가 native와 같으면 체인이 d3d9로 끝난다는 확인이다.

## 5. 그다음

- 결과와 무관하게 다음 회차는 **middle 독립 검수**다. raw로 §4 분류를 summary 없이 재계산한다.
- **사전 허가 W50S (middle이 R1 또는 R2를 ACCEPT할 때만):** 새 opt-in 플래그로 R1이면 **inner source**, R2면 **inner cache**를 (E) 창에서 native 기준값→hook으로 CAS한다. fresh 정확히 1회. 성공 판정은 W50 카드 §4 `FEASIBLE(acquisition)` 1~5를 **그대로** 쓴다. hook은 native owner로 전달해야 하며, top redirector를 native로 인정하는 완화는 계속 금지다. W50S가 `FEASIBLE`이면 W50 §6의 W51을 middle이 발행한다.
- **R3:** acquisition 분기를 `BLOCKED(acquisition:inner_not_native)`로 닫는다. 더 깊은 wrapper 층 추적은 하지 않는다. strategy가 G1 대안 경로와 G4 전환 중 하나를 판정한다.
- **R4:** 재시도하지 않는다. middle이 원인을 판정하고 strategy에 승격한다.

## 6. 금지

W50 카드 §5 금지를 전부 유지한다. 추가 금지는 다음과 같다: W50R 안에서 CAS/쓰기, `LoadLibrary`, top-owner gate 완화, 기존 A1/A3 raw 재해석으로 분류 대체, W51, G1 PASS 주장, 사용자 승인 대리, 커밋.
