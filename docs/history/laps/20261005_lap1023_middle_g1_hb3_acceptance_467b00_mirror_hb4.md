# 2026-10-05 | lap1023 | G1 middle — H-B3 독립 검수(B3-0·B3-1·B3-3 PASS 수용) → work H-B4(`0x467B00` diff 미러) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간 계획·컨펌) 1 lap. 게임 실행·source 변경·커밋 0.
- 가설: lap1022 work H-B3의 귀속(B·C 미설명 변화 = 미후킹 `0x467B00`, A = `wined3d.dll` 비-present 스레드)이 raw와 source로 재현되는가. 재현되면 다음 work를 정한다.
- 예상 PASS / FAIL 조건: 새 스크립트로 재계산한 불일치가 0이어야 한다. diff는 env 없을 때 불변이어야 한다. `0x467B00` 정적 구조(인자·ret·hook 가능 prologue·호출처)가 work 기록과 같아야 한다.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제(원문은 아래 부록). 공유 temp `20261005_lap1023_middle_review/`:
  - `recalc_lap1023.py` SHA256 `902fab56f29e6286e3670ae2eb1fba84df2ea473a0dda40955b31539335cd514` → `recalc_lap1023.json` `d113e12d71bfbdc50a4c57f30a1e5e7255d46576e9a6762e43ef3ea3a3a5302e`·`recalc_stdout.txt` `5058aefa…27ab`
  - `recalc2_lap1023.py` `0c82841b11576dc8de36520023e49d02d1743ba847d80b1f376522e89a8f3b7b` → `recalc2_lap1023.json` `a6738e06b6661e77bfe9c774a57da2dcb99460e2a9dda8831dfa2770fe3629c4`
  - 모두 uncommitted.
- 원본 SHA / fixture: 원본 EXE `b56986e0…8ac`(`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`)를 재계산해 일치를 확인했다. objdump는 read-only(`/tmp/lap1023_467b00.asm`·`/tmp/lap1023_full.asm`)로만 실행했다. save000 `1c703551…19da`(index 1), save006 `616b7997…a064`. 활성8인 부하 증명 아님.
- 검수한 source: 현재 `g1_mirror2x.c` `46ef3979…9588`·`g1_screen_watch.c` `78c924ab…d885c`·`.h` `4a811419…f95`·`g1_mirror2x.h` `c33252a5…c9cc`·Makefile `cd42b565…dc9`·probe `1dd5a051…e2be`·test `9a79692b…31d1`. 모두 work 기록과 같다. 4 run(s0_r1/r2·s6_r1/r2) bridge 사본의 `g1_mirror2x.c`·`g1_screen_watch.c`도 현재 source와 같다.

## 1. 독립 재계산(`analyze_hb3.py`·`analyze_hb3_s6.py`·제품 helper 미사용)

present 규약(source로 확인): `g1_mirror2x.c:1330-1333`에서 `layer_drift_present`가 ordinal k(`g_drift_present++`)를 쓴 뒤 watch에 k+1을 넘긴다. 따라서 `x` hit의 p=k는 present k−1과 k 사이 쓰기이고, `u`/`s` 레코드 p=k에 보이는 값이다. work의 "같은 present 구간" 정의와 같다.

| 항목 | work | 재계산(r1 = r2) |
|---|---|---|
| JSONL 파싱 | 손상 0(v0 수리 후) | 두 파일 전부 `json.loads` 통과. sw x 1,773/1,769·a 52·k 8·e 39, ld u 49 |
| selftest | armed 1·hits 1·PASS | 같음 |
| 무장 | 10스레드·52라운드·fail 0·present 스레드 무장 | 52라운드 전부 fail 0·present 스레드 무장 1·주소 집합 1개(`0x08B16000`·`0x08B5A885`·`0x08AFE47E`) |
| watch 주소 = present source | match 7 | match 7, buffer = surface `0x08AFC610`, stride = pitch 832. 주소 = buffer + y·832 + x를 A/B/C 3점 모두 손으로 확인 |
| raw 상한 | dropped 0 | 마지막 heartbeat dropped 0·overflow 0 |
| stale 마지막40 중앙값 | 424.5 | 424.5(r1 p372..411·r2 p371..410) |
| 안전 7종·cleanup·source_unchanged | 0·true·true | 0(`panel_transfer_mismatch_cleared`는 lap1013 판별력 없음 계수)·[true,true]·[true,true] |
| perf | p95 cand 11 ms | PASS, p95 11/11, tick 비 1.0000039/1.0000053 |
| 양성 대조 B p366..410 | 45/45 | 45/45(EIP ∈ `0x467580..0x4676D0`) |
| B 89 리셋 hit | 268/267 | `0x4662DE` 244/243 + `0x467CCF` 24/24 |
| B3-1 u 귀속 | A 5/5·B 19/19·C 25/25 | 같음. hit 없는 u 0 |
| u 귀속 EIP | B 18·C 25 `0x467CCF`, A 4 wined3d, 2 `0x4662DE` | `B:0x467CCF` 18·`C:0x467CCF` 25·`A:0x746099CF`(tid 288) 4·`A`/`B:0x4662DE` 각 1 |
| `0x467CCF` hit 범위 | B 207..365·C 84..377 | B 159 hit = 159 present(연속)·C 294 hit = 294 present(연속), 전부 tid 280·호출 스택 `0x41A072>0x434025` 453/453 |
| A 비-EXE 쓰기 | 41건·p298..338 | 41건·`0x746099CF` 하나·tid 288·pt 0·값 187×38, 94·215·163 각 1 |
| `_inmm.dll` EIP·guard | 0·0 | 0·0 |
| save006 env-off | 파일 미생성·계수 0 | `screen_watch.jsonl`·`layer_drift.jsonl` 미생성, drift 계수 `drift_unattributed` [0,0,0]만. s6_r1 꼬리 16,652는 lap1000 r1·lap1019 보강과 같은 짧은 run 변형 |

**판정 영향 불일치는 0이다.** 정정 1건(경미): work는 A의 wined3d hit를 "스택 .text 복귀 0"이라 적었다. raw로는 41건 중 39건 스택에 EXE 범위 값이 있다(`0x004D0000` 38·`0x004DE9A0` 1). `0x004D0000`은 64 KiB 정렬값이라 복귀 주소로 보기 어렵다. 결론(present 스레드 밖 wined3d 쓰기)은 바뀌지 않는다.

### 1.1 새 근거 — 표본 stale은 미후킹 writer의 덮어쓰기와 present 단위로 일치한다
각 present에서 표본의 마지막 hit가 캐시 복사(`0x4662DE`)가 아니고 그 값이 캐시 복사 값과 다른 present를 "덮어쓰기"로 셌다. 이 집합을 lap1019 정의의 표본 stale present 집합(`cov==1 && scr!=snap`)과 비교했다.

| 표본 | stale present | 덮어쓰기 present | 일치 |
|---|---|---|---|
| A | 41 | 41(전부 wined3d `0x746099CF`) | 집합 동일 |
| B | 135 | 135(`0x467CCF`) + 46/45(`0x467692` = H-B 미러됨) | `0x467CCF` 부분이 stale 집합과 동일, `0x467692` 부분은 stale 0 |
| C | 210 | 210(`0x467CCF`) | 집합 동일 |

- 즉 lap1018 이후 남은 표본 stale(A 41·B 135·C 210)은 **전부** 이 두 writer로 설명된다. `0x467CCF`가 캐시 복사와 같은 값을 쓴 present(B 24·C 84)는 stale이 아니다.
- `0x467CCF`는 범위 안에서 **매 present** 캐시 복사 뒤에 다시 칠한다(B 159/159·C 294/294 순서 `0x4662DE>0x467CCF`). lap1021 §1.1의 "매 present 재도색" 추론이 직접 확인됐다.
- 화면 전체 stale(trace `stale_pixels`, PS3 present별) 분포: p0..83 중앙값 4,661, p84..206 6,215, p207..365 6,944, p366..377 431.5, p378.. 390/392. 큰 덩어리는 p365 직후 끝난다. 이는 B의 `0x467CCF` 종료(p365)와 시기가 같다. 단 p0..83(`0x467CCF` 표본 hit 이전)의 4,661은 표본 3점으로 귀속되지 않았다. `0x467B00`이 표본 밖에서 더 일찍 그렸는지는 미측정이다.

## 2. 정적 검수 — `0x467B00`(read-only objdump, 원본 SHA 일치)

- prologue `83 EC 14 | 33 C0 | 53 89 44 24 04`: 앞 5바이트가 명령 경계(`sub esp,0x14` 3 B + `xor eax,eax` 2 B)다. exact 5-byte hook이 가능하다. `0x4676D0`과 같은 old bytes다.
- 종료 `0x467D02..0x467D09`: `pop edi/esi/ebp/ebx; add esp,0x14; ret 0x14`. 다음 `0x467D0C`부터는 nop이다. **스택 인자 5개, thiscall(ecx = renderer)**.
- 인자(스택 오프셋 직접 계산): arg1 x(`[esp+0x28]`, 16비트 `movsx`)·arg2 y(`[esp+0x24]` 시점 push 2개)·arg3 w·arg4 h(모두 `movsx` WORD)·arg5 src 포인터(DWORD). 목적지 = `[ecx+0x1514] + y·[ecx+0x10] + x`.
- **클립한다**: renderer 클립 사각형 `[ecx+0x4D0/0x4D4/0x4D8/0x4DC]`(left/top/right/bottom)로 완전 바깥이면 즉시 반환하고, 부분이면 위·왼쪽 건너뛰기·오른쪽·아래 한계를 계산한다. 이 점이 무클립 `0x467580`/`0x4672E0`과 다르다.
- 픽셀 처리: src 바이트 `0xFE` = 다음 바이트만큼 투명 건너뛰기. 그 밖의 바이트는 **목적지 픽셀 dst를 읽고** 두 팔레트 색(`[ecx+idx*3+0x419A1..]`)을 64×64 표 `[ecx+0x41CA0]`로 혼합한 뒤 3D LUT `[ecx+0x19A0]`로 팔레트 인덱스로 되돌려 `0x467CCC: mov [edi+ebp],dl`로 쓴다(`0x467CCF` = 그 다음 명령). 즉 목적지 의존 반투명 혼합이다.
- 호출처는 전체 objdump에서 **2곳뿐**이다: `0x41A06D`·`0x41AC45`. 둘 다 `push`로 16비트 필드(`ax`/`dx`, 위 16비트 쓰레기)와 sprite 포인터(`[0x51F350]+[0x51FA84]` 표)를 넘기고 `mov ecx,0xE5BF18; call 0x467B00; ret`인 thin wrapper다. 그래서 H-L/H-B처럼 하위 16비트 부호 확장이 필요하다.
- 현재 tools/analysis/history(lap1022 제외)에 `0x467B00` hook·언급이 없다. mirror hook 대상(`G1_*`)이 아니다.

## 3. diff 검수(lap1020 bridge `22818f41…` 대비)

- `g1_mirror2x.c` diff는 3곳뿐이다: `#include "g1_screen_watch.h"`, `copy_present`의 `layer_drift_present` 직후 `g1_screen_watch_on_present(...)` 호출, `g1_mirror2x_primitive_guard()` getter. 기존 mirror·gate·계수 줄 변경은 0이다.
- env 없을 때 불변인 근거:
  - `g1_screen_watch_on_present` 첫 줄이 `if (!screen_watch_on()) return;`이다. `screen_watch_on`은 env를 1회 읽고 캐시한다(Interlocked 상태 0→1→2).
  - VEH 등록(`AddVectoredExceptionHandler`)·selftest·스레드 열거·파일 생성은 모두 그 뒤에만 있다. 따라서 env 없이는 VEH도 DR 무장도 없다.
  - save006 env-off 2 run에서 `screen_watch.jsonl` 미생성을 raw로 확인했다.
- VEH: `EXCEPTION_SINGLE_STEP`이 아니면 `CONTINUE_SEARCH`, 미무장이면 `CONTINUE_SEARCH`이다. 처리하면 Dr6를 0으로 하고 `CONTINUE_EXECUTION`이다. 게임 buffer는 읽기만 한다. selftest는 Dr3 비공개 바이트만 쓰고 해제한다. 진단 전용으로 수용한다.
- 한계(work 기록에 있음, 수용): 새 스레드는 최대 7 present 늦게 무장된다. `v`는 hit 시점 읽기다. `guard` 판별력은 낮다.

## 4. 판정
**H-B3를 수용한다: B3-0 PASS, B3-1 PASS(A 5/5·B 19/19·C 25/25), B3-3 비회귀 PASS.** B3-2 분류는 다음과 같다.
- (a) EXE 미후킹 primitive `0x467B00`: 표본 B·C stale 전부(135/135·210/210)와 u 43/49를 설명한다.
- (b)/(d) `wined3d.dll` present 스레드 밖 tid 288: 표본 A stale 41/41과 u 4/49를 설명한다.
진단 코드는 env 게이트 안에서만 동작하고 제품 동작은 불변이다.

### 4.1 다음 경로 결정 — H-B4(`0x467B00` diff 미러) 채택, A는 분리 backlog
- `0x467B00`은 H-B(`0x467580`)와 같은 형태다: 같은 renderer, 5인자, 16비트 인자, `ret 0x14`, thin wrapper 2곳, hook 가능 prologue. 같은 diff 미러 패턴(before 스냅샷 → 원본 → `g1_overlay_blt_apply`)으로 바로 구현할 수 있다. 목적지 의존 혼합이지만 diff 미러는 원본의 1x 결과를 비교하므로 그대로 맞다. → **FEASIBLE, 다음 work에서 즉시 구현·실행.**
- A(wined3d tid 288)는 다른 범주다(ddraw/wined3d 경로). 추론: 게임의 ddraw Blt/BltFast가 wined3d CS 스레드에서 sysmem surface에 실행된 것일 수 있다. 참고로 save000 후보는 overlay BltFast `mirrored 0·rejects 453/452`이다(save006 mirrored 792). 미확인이며 원본 lane의 같은 쓰기 여부도 미측정이다. H-B4 뒤 별도 진단(BltFast/Blt 호출별 목적지·사각형·reject 이유를 p298..338에서 기록)으로 둔다.

## 5. 다음 work H-B4 사전등록(Sonnet work 1 lap, 제품 변경)

목표: `0x467B00` 출력을 HD 화면에 diff 미러해 save000 후보의 표본 B·C stale을 없애고 화면 stale 덩어리(p84..365)를 줄인다.

### 5.1 구현 범위(최소, H-B `mirror_blend_wrle` 동형)
- `g1_mirror2x.c`:
  - `#define G1_BLEND_CLIP 0x00467B00u`, old bytes `83 EC 14 33 C0`(5 B)를 `install_one` 체인에 추가한다(all-or-nothing, `restore_hook`·`installed`·`g_original_* = NULL` 원복 포함). 이름은 work가 정하되 기존 규칙을 따른다.
  - wrapper `mirror_blend_clip(renderer, a_x, a_y, a_w, a_h, src)` thiscall:
    - 인자는 하위 16비트 부호 확장(`(int16_t)`)한다.
    - renderer == `G1_RENDERER_VA`, buffer·stride·높이 600·캐시/패널 buffer 아님 검사는 `mirror_blend_wrle`와 같다.
    - 화면 교집합 `[x0,x1)×[y0,y1)`만 before 스냅샷을 뜬다. 원본은 자체 클립(renderer `0x4D0..0x4DC`)을 하므로 화면 교집합 diff는 상위집합으로 안전하다. 부분 교집합은 `clipped`로 센다.
    - 원본 호출은 원래 인자 그대로 한다. 그 뒤 `g1_overlay_blt_apply`로 바뀐 픽셀만 미러한다.
    - `G1DriftWrite` begin/end로 감싸 `w` 레코드(f `467B00`)를 남긴다. 이것으로 `u` 귀속이 갱신된다.
  - 계수 `blend_467B00_{invocations, mirrored_calls, mirrored_pixels, changed_calls, clipped_calls, reject_target, reject_bounds, reject_size, reject_guard}`를 metrics에 추가한다(`direct_draw_trace.c` getter 포함).
- 테스트: `tests/test_g1_rect_fill.py`의 H-B 계약 테스트와 같은 형식으로 RED→GREEN(주소·old bytes·install/restore·16비트 인자·before→original→apply 순서·reject 분기).
- `G1_OVERLAY_MAX_WIDTH/HEIGHT`(320×128) 초과는 `reject_size`로 센다. reject_size가 invocations의 10%를 넘으면 (w,h) 최대값을 기록한다. 그 값이 800×600 이하이면 같은 lap에서 before 버퍼만 키워 재실행한다(③ 반복 원칙, 추적 가능한 구현 결함).

### 5.2 실행(순차)
- save000 pair 2회: `--hd-source scale2x --fixture save000 --scene-actions none --performance-window --layer-drift`(screen watch 끔 — perf 비교 오염 방지).
- save006 env-off 비회귀 pair 2회: lap1022 `run_s6.sh`와 같은 인자.
- 실행 후 `game` 사본은 삭제하고 prefix·manifest·output·로그는 보존한다. 디스크 여유는 현재 73G다.

### 5.3 사전등록 판정
- **B4-0 유효**: 안전 7종 0, cleanup·source_unchanged true, hook 설치 성공, `blend_467B00_invocations` > 0, `reject_target`·`reject_guard` 0, invocations = mirrored + reject_bounds + reject_size. scene/tick/카메라는 lap1022와 같아야 한다(카메라 (39,53)·units 375).
- **B4-1 표본(주 판정)**: lap1019 정의(`cov==1 && scr!=snap`, s 레코드 구간 전개)로 센 표본 stale present가 B 135→**≤7**·C 210→**≤11**(각 ≤5%)이어야 한다. 두 run 모두 충족해야 PASS다. A 41은 범위 밖이며 증가하지 않아야 한다(≤43).
- **B4-2 귀속**: `drift_unattributed` B ≤2·C ≤1이어야 한다(A 5는 유지 예상). `w` 레코드에 f `467B00`이 나타나야 한다.
- **B4-3 화면 stale(보고 + 하한)**: trace `stale_pixels` 중앙값을 창별(p0..83·p84..206·p207..365·p366..·마지막40)로 보고한다. p84..365 합산 창 중앙값이 lap1022 기준(6,215/6,944) 대비 **≥50% 감소**하면 PASS다. 미달이면 PASS(partial)로 기록하고 남은 덩어리의 정체를 다음 middle이 정한다(표본 밖 writer 또는 p0..83 성분). 마지막40 중앙값은 ≤445(424.5+5%)여야 한다.
- **B4-4 성능**: p95 ≤16 ms, ticks/s 비 ≥0.95.
- **B4-5 비회귀(save006 env-off)**: 300..620 공통 38프레임 r1∩r2 = 24 px(y515..520×x616..619, 성분 D)·신규 0이어야 한다. 프레임 880이 두 run에 있으면 39프레임 0이어야 한다. p95 ≤16 ms·안전 0이어야 한다. `blend_467B00` 계수는 공개한다(이 장면 호출 여부 무관).
- 하나라도 FAIL이면 수리 없이 원인(인자 해석·클립·reject 분포)을 기록하고 1회 수리 후 재실행한다. 그래도 FAIL이면 인계한다.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산·read-only 정적 분석만 했다. 게임/source/commit은 0이다. 전체 `make check`는 SKIP했다. source가 불변이고 lap1022 full PASS 1620이 유효하다. 다음 work가 DLL 변경 뒤 실행한다. focused 검사 결과는 STATUS에 보강한다.
- 남은 위험:
  - `0x467B00`은 목적지 의존 혼합이다. diff 미러는 1x 결과를 그대로 확대하므로 그 영역의 HD 디테일은 잃는다(H-B와 같은 수준, P6 화질 잔여 범주).
  - 원본은 클립 사각형을 쓰지만 wrapper는 화면 교집합만 본다. 클립 밖 쓰기는 원본이 하지 않으므로 diff로 안전하나, 클립 사각형이 화면보다 넓은 경우(관측 안 됨)는 B4-0 reject_bounds로 감시한다.
  - p0..83 stale 4,661은 이번 근거로 귀속되지 않았다.
- backlog(변경 없음 + 추가 1):
  - 추가: A wined3d tid 288 쓰기(값 187 유지 38 present) 정체와 원본 lane 동일 여부, save000 overlay BltFast mirrored 0·rejects 453
  - save000 `--stale-mask` 부재
  - save006 짧은 run 꼬리 16,652
  - 성분 D
  - hold keydown 위상 경합
  - 가장자리 마우스 스크롤
  - wrap 쓰기 미추적
  - 프레임 880 부재 run의 39프레임 검증
- 사용자 승인 상태: 기술 검수일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-B4(위 §5).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1022 work, SHA256 `445e0995644209e70d2accbcf8ab164b540039a4761ec90b2a74196b3f28c63a`)

```
lap1022 work(Claude Code claude-sonnet-5-5) G1 H-B3 인계 (마일스톤 경계 아님; 사전등록 B3-0/B3-1/B3-3 PASS, 다음 가설(H-B4) 사전등록·독립 검수 요청).
- 한 일: 진단 전용 구현. 신규 tools/inmm_stub/g1_screen_watch.c/.h(opt-in SYW2_G1_SCREEN_WATCH=1): 첫 유효 PS3 present에서 화면 buffer(renderer+0x1514)+y*stride+x 표본 A(112,126)·B(437,463)·C(302,9)에 DR0..2 쓰기 watch를 Toolhelp32로 프로세스 모든 스레드에 무장(8 present마다 재무장), VEH가 EIP·tid·값·모듈·mirror guard·.text 복귀주소를 C:\inmm_g1_screen_watch.jsonl 기록(selftest·match·arm·heartbeat 포함). g1_mirror2x.c는 getter+present 호출만 추가, 하네스 --screen-watch(--layer-drift 필수), tests/test_g1_screen_watch.py RED→GREEN. 제품 mirror·gate·기준 불변(env 없으면 hook·VEH·파일 0). 수리 1건: v0 run의 e 레코드 모듈 이름 버퍼 NUL 미종결로 JSONL 67줄 손상 → 버퍼·NUL 수리 후 pair 재실행(v0 보존).
- 실행: save000 pair 2회(--layer-drift --screen-watch) + save006 env-off pair 2회, 전부 exit 2(기존 pair HOLD). 공유 temp 20261005_lap1022_work_hb3/.
- 결과: B3-0 PASS(selftest hit·무장 10스레드 fail 0·watch 주소=present source 3/3·stale 424.5·안전0·양성 대조 B p366..410 0x467580 본체 EIP 45/45·89 리셋 hit 268/267). B3-1 PASS: 미설명 변화 A 5/5·B 19/19·C 25/25가 직전 구간 마지막 hit val==u.scr. B3-2: B 18+C 25 = EXE EIP 0x467CCF(복귀 0x41A072, present 스레드, 미후킹 함수 0x467B00 `83 EC 14 33 C0`·ret 0x14·인자 5·호출처 0x41A06D/0x41AC45); A 4(p298..338 임시값 94·215·163·187)는 wined3d.dll EIP 0x746099CF·present 스레드 밖 tid 288(41건); 나머지 2는 0x4662DE(캐시 복사). _inmm.dll EIP 0. B3-3 PASS: save006 공통 38프레임 r1∩r2 = 24 px(성분 D)·신규 0·p95 7/7·안전0·계수 0(프레임 880은 두 run 모두 부재라 39프레임 0은 검증 불가).
- middle이 확인할 것: (1) screen_watch.jsonl·layer_drift.jsonl·trace_raw를 analyze_hb3.py·제품 helper 없이 새 스크립트로 재계산(B3-0 항목, u 49건 귀속, 0x467CCF hit p 범위 B 207..365·C 84..377), (2) 0x467B00 objdump(prologue·인자 x,y,w,h,rle·호출처)와 g1_screen_watch.c diff(env 없을 때 불변, VEH 처리), (3) 다음 경로: H-B4 = 0x467B00 diff 미러(H-L/H-B 패턴) 사전등록 vs A의 wined3d 4건·값 187 유지 38 present 분리 조사(원본 lane 동일 쓰기 여부 미측정).
- 기록: docs/history/laps/20261005_lap1022_work_g1_hb3_screen_sample_write_watch.md. 변경 uncommitted.
```
