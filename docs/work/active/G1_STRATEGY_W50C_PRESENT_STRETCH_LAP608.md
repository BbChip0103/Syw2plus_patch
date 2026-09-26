# G1 W50C — 실제 PS3 present 개별 보존 + primary 2배 stretch 전사 (lap608 strategy 발행, 2026-09-25 KST)

- 발행: lap608 strategy. 실제 모델은 Claude Code `claude-opus-5-5`(effort 세션 비노출)이며 계약 모델 Fable/Astra를 대신한다. 게임 실행0, 제품/하네스 source·binary·raw 변경0.
- 근거: `loop/ESCALATE_SOL` §156·§157, lap607 기록, W50B 카드 `G1_W50B_NATIVE_1600_BLIT_FEASIBILITY_LAP605.md`, W50 카드 §6, DESIGN §2 G1.
- 수행 역할: **work**(Codex `gpt-5.6-luna` 또는 Claude Code `claude-sonnet-5`, high). 계획 회차를 끼우지 않는다. 그다음 새 middle이 raw를 독립 검수한다.
- 중단점: **60분 또는 실패 가설 2회 중 먼저 오는 쪽.** W50B 계보는 H1에서 가설 1회를 이미 소비했다. 그래서 이 카드의 H3가 이 계보의 **마지막 가설**이다.

## 0. strategy 판정 — §157 (B) 선택

1. **이미 성립한 것(lap606 raw, lap607 ACCEPT, lap608 probe 3번째 재실행 canonical `6a6e0998…f739` 동일):** exact 800×600×8 요청을 1600×1200×8로 전달한 건수는 7이다(skip 5). final primary는 1600×1200×8이고 PS3 offscreen은 832×600이다. renderer 800계열이 유지된 채 primary만 분리됐다. W50B의 앞 절반은 성립했다.
2. **실패한 것:** 화면은 1600 primary 좌상단에 800×600이 1:1로만 찍혔다(비검정 quadrant `[375756,0,0,0]`, nearest 2× `0.8880`). 원인은 present 경로 하나다. 카드가 고정한 `0x0041C3E4` Blt는 0건이었다. Flip도 0건이다. 실제 PS3 primary←832×600 offscreen 전사는 **BltFast**(집계 8건)였다. BltFast는 늘려 그리기(stretch)를 할 수 없다. 따라서 H1은 "native 1600 + 2배"를 구조적으로 반증하지 않았다. 반증된 것은 카드의 present 전제다. H2(`0x0041C3E4` dst rect)는 실행되지 않는 호출이라 의미가 없다.
3. **남은 질문은 하나다:** 실제 present BltFast를 같은 인자에서 2배 목적 사각형의 Blt 한 번으로 바꾸면 whole-frame 2배가 되는가. 1 work 회차·fresh 1회로 답할 수 있다.
4. **(A)를 고르지 않는 이유:** 지금 닫으면 G1에 모델 권한 경로가 하나도 남지 않는다. D3D9 acquisition은 R4로 종료됐고, native1600 EXE patch는 구도 FAIL이며, DxWrapper 2배는 DESIGN상 프리뷰다. G4도 `BLOCKED_MODE_EXCLUSION_AND_POSTLOAD_CONTRACT`라 전환하려면 별도 scoping이 필요하다. 싸게 결론 낼 수 있는 가지를 버릴 이유가 없다.
5. **무증거 회차 규칙:** lap607(middle)·lap608(strategy)로 제품/실행 증거 없는 회차가 2연속이다. 다음 회차는 반드시 구현과 실제 실행을 포함하는 work다. 사이에 계획·검토 회차를 끼우지 않는다.
6. **DESIGN 경계:** whole-frame 2배는 G1 완료가 아니다(DESIGN §2 G1 18~23행). 이 카드의 `FEASIBLE`은 "모델이 통제하는 native 1600 최종 표면에 원본 프레임이 2배로 올라간다"는 뜻뿐이다. 그 표면 위에 HD 그림을 800 버퍼를 거치지 않고 합성하는 W51N의 전제 조건이다.

## 1. 고정 사실 (read-only, lap607 probe `d2a72c14…ecdd` 재현)

- 원본 SHA-256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. lap606 bridge `983c82a9…a579`.
- `0x0049272C..0x0049273E` = `8b1538d4e500 6a10 6a00 52 6a00 6a00 50 ff511c`, 다음 `c3`. 해석: `BltFast(this=eax, x=0, y=0, src=[0x00E5D438], srcRect=NULL, trans=0x10 DDBLTFAST_WAIT)`(vtable `+0x1C`), return VA `0x0049273F`. 런타임 PS3 primary `0x01E6D198`←offscreen `0x01E6D948` BltFast 8건이 이 site인지는 **집계 때문에 UNKNOWN**이다(강한 정황).
- `0x0041C3C4..E3`(Blt, return `0x0041C3E4`)와 `0x004D1050..66`(NULL-source clear Blt, flags `0x01000400`, return `0x004D1066`)은 다른 site다.
- lap606 provenance는 개입 실행인데 `observational_only=true`였다(계약 위반). legacy `_presentation_logical_surface_contract`는 primary800을 요구한다.

## 2. 허용 변경 (work, 게임 실행 전)

### (a) provenance 계약
`--native-2x-blit` 또는 (d)의 새 플래그가 켜진 실행은 provenance에 `observational_only=false`를 기록한다. `intervention_scope`에는 실제 켜진 개입만 정확히 나열한다(`set_display_mode_exact_800x600x8_to_1600x1200x8`, `ps3_present_bltfast_to_blt_2x`). 회귀 테스트로 잠근다. 개입 없는 실행은 기존 `true`를 유지한다.

### (b) W50B/W50C 전용 validator
legacy `_presentation_logical_surface_contract`는 **수정하지 않는다.** 별도 함수(예: `_presentation_native_split_contract`)를 추가하고, provenance의 명시 opt-in이 있을 때만 선택한다. 요구 조건: exact SetDisplayMode event(requested 800×600×8, forwarded 1600×1200×8, HRESULT0, return `0x0046457D`), renderer 800×600×8, final primary 1600×1200. 회귀 테스트: opt-in 없는 primary≠800은 legacy가 계속 거부한다. ambient env만으로는 새 validator가 선택되지 않는다.

### (c) primary 대상 present 개별 기록(집계 금지)
`direct_draw_trace.c`에서 **destination이 primary surface**(PRIMARYSURFACE caps로 생성된 identity)인 모든 `Blt`/`BltFast` 호출을 집계하지 않고 개별 event로 남긴다. 필드: seq, game ps/tick, return VA, dest/src identity, BltFast x·y 또는 Blt dst rect, src rect(NULL 여부와 유효 사각형), trans/flags, src desc width·height, HRESULT, `converted`. 상한은 run당 primary 대상 2048건 + 총계이며, 초과분은 dropped 카운터로 남긴다(lap606 run 전체 BltFast 총계는 1,345건이었다: 개별 256 + 집계 1,089, Flip 0). primary가 아닌 대상의 기존 집계는 바꾸지 않는다.

### (d) H3 — PS3 present BltFast→2배 Blt 전환(이 계보의 마지막 가설)
새 opt-in `SYW2_G1_NATIVE_2X_STRETCH=1`과 CLI `g1-presentation-trace --native-2x-stretch`를 추가한다. 이 CLI는 `--native-2x-blit` 없이 쓰면 거부한다. `--dxwrapper-2x`·`--native-2x-dstrect`와 함께 쓰는 것도 거부한다.

전환은 아래를 **모두** 만족하는 `BltFast` 한 호출에만 적용한다.
1. 같은 프로세스에서 H1 split이 적용됐고, primary desc가 1600×1200이다.
2. destination == primary이다.
3. source desc가 width≥800, height==600이다(논리 offscreen).
4. return VA ∈ **P**. P는 work가 게임 실행 전에 원본 bytes로 핀한 primary 대상 present call site 집합이다. 최소 `0x0049273F`(§1 bytes)를 포함한다. 다른 site를 넣으려면 실행 전에 그 old bytes를 기록해야 한다. P 밖 caller는 전환하지 않고 (c)에만 기록한다.

전환 규칙:
- 유효 src rect = 원래 srcRect가 있으면 그 값, NULL이면 `{0,0,800,600}`(renderer 논리 크기)이다. 800~831열 guard band는 전사하지 않으며, 그 사실을 event에 기록한다.
- dst rect = `{2x, 2y, 2x+2w, 2y+2h}`. primary 범위를 넘으면 전환하지 않는다(structured skip 후 원래 BltFast를 전달).
- 원본 `Blt(dest, &dst, src, &effSrc, DDBLT_WAIT | (trans & DDBLTFAST_SRCCOLORKEY ? DDBLT_KEYSRC : 0), NULL)`를 **정확히 한 번** 호출한다. 전환된 호출에서는 원래 BltFast를 부르지 않는다. 반환값은 Blt HRESULT다.
- 조건 불일치는 원래 BltFast를 인자 그대로 한 번 전달한다. surface·refcount·vtable·renderer 필드·offscreen 크기·pixel은 바꾸지 않는다.

## 3. 실행 전 회귀 (하나라도 실패하면 게임을 띄우지 않는다)

1. 기본 OFF, `--native-2x-blit`만 켠 경우, 비대상 dest/source/caller: BltFast/Blt 인자가 byte-for-byte 그대로 한 번 전달된다.
2. 합성 입력 `BltFast(primary1600, 0, 0, src832×600, NULL, 0x10)` → `Blt(dst {0,0,1600,1200}, src {0,0,800,600}, DDBLT_WAIT)` 한 번. 원래 BltFast 호출 0회.
3. srcRect 비NULL·x/y≠0 산식, 범위 초과 skip, P 밖 caller skip, colorkey flag 대응.
4. CLI 거부 3종, provenance false/scope, legacy validator 불변과 새 validator 선택 조건.
5. PE32 bridge build, targeted tests, `bash checks/safety.sh check` PASS.

게임 실행 전 자기 새 코드의 실패는 같은 회차 안에서 고치고 테스트로 잠근 뒤 진행해도 된다(관측 소비 0). 기존 pin/baseline을 갱신해 통과시키는 것은 금지다.

## 4. fresh 실행 — 동기 foreground **정확히 1회**

- 읽기 전용 원본에서 새 전체 게임 사본·새 win32 prefix·빈 Xvfb display를 만든다. runtime root는 lap606처럼 `local/runtime/<run>/game` direct-child다. lap606·W50R·W50RX 산출물은 재사용하지 않는다.
- 원본 EXE를 `ddraw=b`로 실행하고 새 bridge만 private 사본에 설치한다. `--native-2x-blit --native-2x-stretch`를 쓴다. 입력은 stock UI PS9→PS7→PS5→PS3, PS3 tick>0 capture(lap606과 같은 절차)다. 한 실행 ≤15분, 셸 background 금지. 시간이 부족하면 시작하지 않고 기록한다.
- 게임이 한 번 뜬 뒤에는 **어떤 이유로도 두 번째 실행을 하지 않는다.**
- 캡처는 공유 `temp/Syw2plus_patch/captures/`에 `YYYYMMDD_HHMMSS_` 접두사로 두고, manifest/raw/evidence/provenance/verdict/capture SHA와 cleanup을 기록한다.

## 5. 실행 전 판정식

### `FEASIBLE(native_1600_stretch_2x)` — 같은 run에서 모두 성립
1. exact SetDisplayMode event가 W50B §5-1과 같다(requested 800×600×8, forwarded 1600×1200×8, HRESULT0, return `0x0046457D`).
2. PS3 renderer 800×600×8, offscreen 832×600, primary 1600×1200.
3. PS3 개별 기록에 return VA ∈ P, HRESULT0, dst `{0,0,1600,1200}`, src `{0,0,800,600}`인 converted 호출이 ≥1건 있다. PS3에서 primary←논리 offscreen 호출 중 미전환은 0건이다. 그 밖의 primary 쓰기(예: 커서)는 caller/rect와 함께 목록으로 낸다.
4. PS3 tick>0 capture: 네 800×600 quadrant 모두 비검정>0이다. lap607 probe와 같은 정의로 nearest 2× pixel equality ≥0.999, 2×2 block all-equal ≥0.999다. 3의 "그 밖의 primary 쓰기" 사각형만 지표에서 제외할 수 있고, 제외 픽셀 수(프레임의 ≤1%)를 공개한다.
5. provenance `observational_only=false`와 정확한 scope, 새 validator PASS, legacy validator 불변. 원본 EXE SHA 전후 동일, private bridge/manifest SHA 일치, DxWrapper 미로드, owned prefix/display 잔류0.

### `NOT_FEASIBLE(native_1600_stretch_2x)` — 구조적 반증만
- 규칙대로 전환된 PS3 Blt(dest=primary)가 전부 HRESULT≠0이다(예: primary stretch 미지원). 또는
- 전환 Blt는 HRESULT0인데, raw가 그 뒤 primary를 Blt/BltFast가 아닌 경로(Lock/GetDC/Flip 등)로 다시 덮어 4가 실패함을 보인다.

하네스·입력·시간 실패를 불가능으로 쓰지 않는다.

### `BLOCKED(<이유>)`
preflight·private 실행·PS3 입력·trace finalization·cleanup 실패. 또는 PS3 primary←offscreen caller가 P 밖이라 전환이 0건인 경우(`BLOCKED(attribution)`, 실제 caller는 기록). 그 밖에 판별력 없는 결과. 보존하고 재시도하지 않는다.

## 6. 금지

W50B §6 금지 목록 전부를 유지한다. 추가로 H1/H2 재실행, lap606 runtime 재사용, legacy validator 완화, primary pixel 직접 쓰기, overlay/HD SPR 합성, EXE patch, renderer 필드/offscreen 크기 변경, 두 번째 fresh, 커밋, G1 PASS 주장을 금지한다.

## 7. 그다음 (사전 결정 — 사이에 strategy 회차를 두지 않는다, 사용자 번복 가능)

- 결과와 무관하게 다음은 새 **middle 독립 검수**다. summary가 아니라 per-call raw와 capture로 §5를 재계산한다.
- **FEASIBLE ACCEPT:** middle이 **W51N** 카드 1장을 낸다. 대상은 W50 §6 W51과 같다(HUD 자원 SPR `0x24` frame0, `0x0043F270` call, x=10·y=3, 20×24 → 40×48 교체본). 이것을 converted present 직후 native 1600 primary의 (20,6)에 직접 합성한다. ON/OFF 캡처 한 쌍으로 판정하며, 합격선은 W51의 세 조건에 N222 입력 확인 한 가지를 더한 것이다.
- **NOT_FEASIBLE 또는 BLOCKED ACCEPT:** native DirectDraw 2배 계보를 예외 없이 닫는다. G1은 "모델 권한 경로 소진"으로 사용자 보고 대상이 된다. 남은 선택지는 새 renderer/wrapper 같은 새 의존성이라 사용자 판단 몫이다. 같은 middle이 DESIGN §3 순서대로 **G4를 재개**하고, precompaction G4 blocker `BLOCKED_MODE_EXCLUSION_AND_POSTLOAD_CONTRACT`에서 출발하는 read-only re-entry scoping 카드 1장을 발행한다. 이 전환에는 strategy 회차가 필요 없다.

## 8. 보고 전용 위험 (판정 조건 아님)

- **N221:** 원본 PS3 present는 Flip이 아니라 primary 직접 BltFast다(lap606 Flip 0건, primary backbuffer_count=1). 전환이 성공해도 tearing 여부는 판정하지 않는다.
- **N222:** primary가 1600이면 창 좌표와 게임 800 논리 좌표의 대응이 바뀔 수 있다. lap606은 stock UI로 PS3까지 도달했지만 클릭 좌표 대응은 측정하지 않았다. W50C는 판정하지 않고, W51N이 HUD 클릭 한 번으로 확인한다.
- **N223:** 최종 단계 합성은 최상위 층(HUD·커서)에만 painter order가 맞는다. 월드 스프라이트의 HD 디테일에는 offscreen 안에서 2배로 그리는 경로가 필요하고, 이 계보로는 닿지 않는다. G1 완전 합격에 필요한지는 W51N 뒤에 판정한다.
