# 2026-10-06 | lap1086 | G1 middle — H-W330·D-0′ 독립 검수 + 좌상단 소잔여 대조(H-ULc) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1085 work `loop/ESCALATE_SOL`(SHA256 `9da76f3b0088d77498a11d8f14ceb92ae8a7946ec6e142ee6e4502d4cb46726e`, 원문은 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1084 §5 — D-0′(여유 ≥ 20 GiB), H-W330(`0x467580`·`0x467B00` 폭 > 320 tiled 미러로 save006 UPLEFT,DOWNRIGHT hold stale 240,703 → 0).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293…` 직접 재계산 MATCH(읽기만). fixture: 비합성 save006. lap1085·lap1083·lap1081 산출물만 읽음.
- 검수한 source 해시: `tools/inmm_stub/g1_mirror2x.c` `a1f582fcc7e9b988`(= w1 `bridge/g1_mirror2x.c`), `tests/test_g1_rect_fill.py` `e8215bd1…`, `tests/test_g1_overlay_blt.py` `e1303732…`(work 기록과 일치), `g1_overlay_blt.h` `39e6e2e1…`·`tools/g1_saved_scene_probe.py` `1fa1e665…`(lap1084 값과 같음, 불변). w1 `bridge/supply_bridge_build.json`의 stub 입력 56개 SHA256이 현재 트리와 모두 같다 → **현재 트리 = w run bridge**.

## 1. 독립 재계산(work `analyze_hw.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1086_middle_review/`:
`recalc_lap1086.py` `96e3cfbd…238e`(새 스크립트. 좌상단 상자 x0..31·y0..21 stale 모양·커서 `GetCursorPos` 시계 대조·present sim tick 열 추가) → `recalc_lap1086.json` `9ff4638f…f747`, 표준 출력 `recalc_out.txt` `eb55c1ed…44b7`.
pair-result SHA 접두 9/9가 ESCALATE 기재와 같다. stale_mask SHA 9/9 = pair-result 기재 값, mask와 trace `stale_pixels` 불일치 0. layer_drift `p` = ps3 순번(w6·w8·w9 오프셋 0, 시계 차 최대 29 ms). 기준: lap1083 k1·k2·k3·k5·k6, lap1081 hl6. hold 창 정의는 lap1072~1084와 같다.

| 항목 | 사전등록(lap1084 §5) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| reject | w1·w2 `blend_467580/467B00_reject_size` 0 | 9 run 모두 0/0(k1·k2·k6 21/89, k3·k5·hl6 16/0) | 동일 | 일치 PASS |
| 수리 전 stale ord | ord 126~133·140~145·221~225 = 0 | 9 run 모두 합 0(k1·k2·k6 240,701) | 동일 | 일치 PASS |
| w1·w2 hold | 0 또는 ord 137 ≤ 2 px만 | w1 **2**(ord 137)·w7 **2**, **w2 64 = ord 124 62 + 137 2** | 동일 | 일치, **w2 기준 미충족** |
| 진단 run | – | w6 25 = ord 123 23 + 137 2, w8 530 = ord 122 139 + 136 2 + 242 389(+ hold 밖 ord 296 106, 총 636), w9 74 = ord 123 23 + 124 49 + 137 2 | 동일 | 일치 |
| 마지막40 | 0 | 9/9 0 | 동일 | 일치 PASS |
| E-0 | 24칸 왕복 (158,101) | UPLEFT (−2,0)×24 (158,101)→(110,101)·DOWNRIGHT (+2,0)×24, 두 lane 관측열 SHA 같음·k1과 같음(`9206a7d26c7e`/`7e1c2280aac8`); w3 UPRIGHT (0,−2)×24, w4 LEFT (−1,+1)×24 왕복 | 동일 | 일치 PASS |
| E-1 | elapsed p95 ≤ 고정+16·tps ≈ 20 | hold p95 7~11(고정 7~12), tps 19.917~20.041 | 동일 | 일치 PASS |
| w3·w4 | hold 0 | 0/0, 총합 0/0(k3 총합 291,639·k5 291,382) | 동일 | 일치 PASS |
| w5 | 300..848 0, 총합 ≤ 291,382 | 300..848 0, **총합 0**, `blend_467580_mirrored_pixels` 291,382 = hl6 stale 총합(같은 값) | 291,382→0 | 일치 PASS |
| 공통 | 안전 0·cleanup·source_unchanged·mirrored 감소 없음 | 안전 7종 최대 0, 18 lane `game_removed`·`cleanup.ok`·`source_unchanged` true·원본 접두 `b56986e018b4`, `blend_467580_mirrored_calls` 321→341~342·`467B00` 521→610~613 | 동일 | 일치 PASS |

**코드 검토(독립 diff, lap1083 k1 bridge `fd66ba27…` ↔ 현재 `a1f582fc…`):** 바뀐 것은 before 버퍼 크기(screen), hook별 tile 버퍼, 두 크기 검사 분기 제거, `apply`/`apply_banded` → `apply_tiled`, `bands` → `tiles` 이름뿐이다. `g1_overlay_blt_apply_tiled`는 폭 ≤ 320·높이 ≤ 160이면 타일 1개로 `g1_overlay_blt_apply`와 같고, 폭 ≤ 320에서는 `apply_banded`와 같은 160행 band 열이다(halo는 실제 post 프레임에서 읽음). 따라서 **수리 전에 받아들이던 호출은 화소 단위로 같은 결과**이고, 행동이 달라지는 것은 수리 전 `reject_size` 호출뿐이다. 테스트 단언 교체 5종(W-0 목록)은 새 계약 교체이고 완화가 아니다(clip==skip 동등 단언 삭제는 두 본문이 실제로 갈라졌으므로 필요, skip에 tiled 없음 단언 추가). 결함 없음.

**D-0′(독립):** `report.json` `e3125322…`·`plan.json` `c6b73fd8…`·`archive.py` `bae6faf3…`. 21 항목 모두 `prefix` 부재·같은 run `manifest.json` 존재·`removed_private_prefix_only` true. 첫·마지막 archive SHA 재계산 일치. `restore_verification_000/010/020.json` 모두 `full_content_metadata_match` true(1,072/1,072/1,073 entries). 보고 여유 12.15→22.81 GB(= 11.32→21.25 GiB). **현재 여유 8 GiB** → 다음 work는 D-0를 다시 해야 한다. **D-0′ PASS.**

## 2. 좌상단 소잔여(UL) 독립 분석

- 위치·시점: UL stale은 모두 hold 첫 present 셋(ord 122~124, sim tick 24692~24694) 안에서만, 한 run에 1~2 present, 크기 23~139 px이다. 모양은 run마다 다르다(모양 해시 4종, w6·w9 ord 123만 같음). 대각선 줄무늬 모양이며 고정 스프라이트 복사가 아니다.
- **커서·위상 상관(새 근거):** 각 run에서 present 직전 마지막 `GetCursorPos`가 처음 (0,0)인 present와 sim tick 열을 대조했다.

| run | 첫 (0,0) present | 그 주변 sim tick·카메라 | UL stale |
|---|---|---|---|
| w1·w7·k1 | 124 | 123=24692(156)·124=24693(154), 건너뜀 없음 | 0 |
| k2 | 123 | 123=24692(156), 건너뜀 없음 | 0 |
| k6 | 123 | 122=24692(158)·123=24693(156), 건너뜀 없음 | 0 |
| **w2** | 124 | 123=24692 → **124=24694(tick 건너뜀)** | ord 124 62 |
| **w9** | 123 | 122=24691 → **123=24693(tick 건너뜀)**·124=24694 | ord 123 23·124 49 |
| **w6** | **122(카메라 이동 전)** | 122=24692(158)·123=24693(156) | ord 123 23 |
| **w8** | 122 | **122=24692에서 커서 (0,0)과 카메라 첫 이동이 같은 present** | ord 122 139 |

  깨끗한 run(w1·w7·k1·k2·k6)은 모두 "커서 (0,0) 첫 present = 카메라 이동 present, tick 건너뜀 없음" 위상이다. stale run 4개는 모두 그 밖의 위상(tick 건너뜀 또는 커서가 카메라보다 앞섬)이다. **수리 전 3 run은 우연히 모두 깨끗한 위상**이었다. 따라서 "수리 전 0/3 vs 후 4/7"은 위상 표본 차이로 설명될 수 있고, 수리 효과로 볼 근거가 아니다(인과 미확정).
- writer 근거: w9 ord 124 표본 (20,19)이 stale을 잡았다(`scr` 93 ≠ `snap` 228). 그 present의 쓰기 열은 `0x4662DE`(24) → `0x466FCB`(255, `0x466EA0` hook) → `0x46651E`(93, 스택 `0x41635F`, 매 present 같은 값)이고, `0x467CCF`/`0x467692` 쓰기는 없다. 같은 present에 이 표본을 덮는 `467B00`/`467580` 호출 기록도 없다(유일한 호출 (−88,−190,330,200)은 y ≤ 9). 커서 위치의 새 쓰기 `0x466E67`(∈ `0x466D50`, 스택 `0x419E30`)는 표본 (10,2)에서 첫 (0,0) present부터 나타난다(w8 p122·w9 p123).
- UL 구간의 `467B00` 330×200 호출(w8 p123 (−88,−190)·p124 (−27,−158))은 클립 뒤 폭 242·303 ≤ 320이다. 즉 수리 전에도 받아들이던 호출이며 §1 코드 검토상 결과가 같다. w8 ord 122 stale은 그 첫 호출보다 한 present 앞이다.
- 결론: UL 소잔여를 H-W330 변경에 귀속할 직접 근거는 없다. 반대 근거(코드 동치·writer 열·위상 상관)가 셋 있다. 다만 sample-filtered drift라 UL present의 모든 호출을 열거하지 못했으므로 **인과는 UNKNOWN**이다. 사전등록 기준을 사후에 완화하지 않는다.

## 3. 정정·관찰

1. w8 ESCALATE 표의 "ord 296 106"은 hold 창(ord 122..290) 밖이다. hold 합 530 = 139 + 2 + 389이고 총합은 636이다. 수치는 맞고 서술 위치만 바로잡는다.
2. w1 총합은 259이다. hold 밖 ord 352 257 px가 있다(마지막40 밖). lap1084 §1 k3 ord 353 257 px와 같은 종류의 일시 사건이며, w2·w7에는 없다. 비차단 관찰이다.
3. w1과 w7은 stale 열이 다르다(w1 ord 352). `467B00_mirrored_pixels`도 479,989 vs 479,624로 다르다. 같은 옵션 반복도 비결정 성분이 있다.
4. `rect_fill_466070_reject_size` 7~12·`rect_solid_465E80_reject_size` 4는 수리 전과 같다(변경 무관).

## 4. 판정

- **D-0′ PASS 수용.**
- **H-W330 핵심 효과 수용:** 330×200 reject 0, 수리 전 stale 집합 0, hold 240,703 → 2(깨끗한 위상 run), 고정 장면 총합 291,382 → 0, w3·w4·w5 비회귀, 코드 결함 없음.
- **H-W330 사전등록 PASS(partial)은 HOLD:** w2가 "ord 137 외 증가 0"을 어겼다. 이것이 변경과 무관한 위상 잔여인지 H-ULc 대조로 판정한다. 대조 결과 전에는 PASS(partial)로 적지 않는다. 변경은 uncommitted로 유지한다(되돌리지 않음: 핵심 효과가 크고 반대 근거가 우세).
- 제품 G1 마감이나 사용자 승인이 아니다.

## 5. 다음 work 사전등록(Sonnet) — D-0 → H-ULc(수리 전 동작 대조)

**D-0 (필수 선행):** 현재 여유 8 GiB. lap1085 `archive.py` 복사본 절차로 lap1057~lap1079(그다음 lap1081·lap1083) 종료 prefix를 처리해 **여유 ≥ 22 GiB**를 만든다(이번 회차는 11 run 예정). 조건·`prefix`만 삭제·batch마다 full restore 규칙은 같다. 회차 중 여유가 10 GiB 밑으로 내려가면 이 회차의 끝난 run prefix를 같은 절차로 처리한 뒤 계속하고, 불가하면 남은 run을 시작하지 않고 기록한다.

**가설 H-ULc:** UL 소잔여(ord 122~124, x0..31·y0..22)는 H-W330과 무관하다. 커서가 (0,0)에 처음 그려지는 present와 카메라 이동·sim tick 위상이 어긋날 때 나는 기존 잔여다(§2).

**U-0 구현(테스트 먼저 RED→GREEN):** 진단 전용 대조 스위치를 둔다.
- `g1_mirror2x.c`: 기존 `G1_*_ENV` 명명 규칙을 따르는 환경 변수 1개(기본 off)를 둔다. on이면 `mirror_blend_wrle`·`mirror_blend_clip`이 lap1083 크기 검사(`wrle`: 클립 뒤 폭 > 320 또는 높이 > 160, `clip`: 폭 > 320 → `reject_size`, 원본 호출은 그대로)를 그대로 재현한다. off 경로는 지금 코드와 같아야 한다.
- 하네스: candidate에만 그 env를 넣는 옵션 1개.
- 테스트: off 기본·on 분기 문자열·계수 증가 위치·하네스 env 전달·기존 H-W330 계약 단언 불변.
- 이 스위치는 대조 전용이다. 기본 동작을 바꾸지 않는다.

**U-1 실행(순차, load ≤ 8, run마다 game 사본 삭제):** save006 `--terrain-scroll-edge --terrain-scroll-keys UPLEFT,DOWNRIGHT --stale-mask 118-130`. 대조(c, 스위치 on)·후보(t, off)를 **c1,t1,c2,t2,…,c5,t5 교대로 10 run** 돌린다. 여유가 되면 t 진단 1 run을 더한다: `--layer-drift --screen-watch --drift-samples "1,1;13,1;20,19" --stale-mask 118-130`.

**측정(run마다 기록):** UL 상자 stale 합(hold ord, x0..31·y0..22), hold 합·ord별 값, `blend_*_reject_size`, 위상 분류(첫 `GetCursorPos` (0,0) present, 카메라 첫 이동 present, ord 121..125 sim tick 건너뜀 여부), E-0·E-1·안전 7종·cleanup·source_unchanged.

**PASS / FAIL(사전등록):**
- **U-0 충실도:** c run마다 reject_size가 k1과 같은 21/89이고, ord 126~133·140~145·221~225 stale 열이 k1 값과 같아야 한다. 아니면 대조 무효(BLOCKED, 원인 기록).
- **U-1 판정(충실도 성립 시):**
  - (a) c 중 1 run 이상에서 UL stale > 0 → UL은 H-W330과 무관 → **H-W330 PASS(partial) 확정**. UL은 별도 backlog H-UL(커서 위상 잔여)로 옮긴다.
  - (b) c 5/5 UL 0이고 t 3/5 이상 UL > 0 → H-W330 부작용 의심 → H-W330 HOLD 유지. 다음은 UL present의 `467B00`/`467580` 전체 호출 열거(sample 무관 기록) 진단이다.
  - (c) 그 밖(양쪽 모두 드묾) → INCONCLUSIVE. 위상 분류별 표를 남기고 middle이 판정한다. 같은 대조를 반복 연장하지 않는다.
- 공통 FAIL: 안전 위반·크래시·성능 초과(elapsed p95 > 고정+16).
- 변경은 uncommitted로 두고, 기록 freeze 뒤 `make check`(lint·typecheck 먼저)를 1회 돌린다.

그다음 후보: (a)면 save000 UPLEFT 맵 경계 stale ≈189k 귀속(H-D2k-s0, 첫 후보 `rect_fill_466070` reject 40), HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: ord 137 (799,408..409) 2 px, ord 352/353 257 px 일시 사건, throttle 전용 ord 123 writer, `0x467E60` wrap 계수, lane 위상 경합, 진단 동반 영역(w8 ord 242·296, k6 ord 147·219·296~318).

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT와 focused 테스트(`test_g1_saved_scene_probe`·`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`)를 돌린다. 결과는 STATUS에만 보강한다.
- 전체 `make check`는 SKIP한다. 문서만 변경했고 source·하네스는 lap1085 그대로이며, lap1085 full PASS 1667이 있다. 다음 work가 변경 뒤 실행한다.

## 다음 한 가지

work(Sonnet): §5 D-0(여유 ≥ 22 GiB) → H-ULc U-0 → U-1. G6/G7은 사용자 합격(APPROVALS lap989) 대기이며 루프를 막지 않는다.

## 부록: lap1085 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1085 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — D-0′ 디스크 회수 PASS + H-W330(0x467580·0x467B00 폭>320 tiled 미러) 구현·실행 완료, 단 사전등록 PASS(partial) 기준 1건 불충족(w2 좌상단 일시 소잔여). work는 자기 결과를 승인하지 않으며 fresh Opus middle 독립 재계산과 수용/귀속 설계가 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1085_work_hw330 의 {w1..w9}/pair-result.json·candidate/trace_raw.jsonl·stale_mask.bin·(w6,w8,w9) layer_drift.jsonl·screen_watch.jsonl 을 work 스크립트(analyze_hw.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: w1 7cb2db78dba3 w2 93b88d1f9836 w3 81f39201d284 w4 939c246abdea w5 e5448c346b44 w6 cc72a33639ff w7 d6d1d33280f1 w8 87e447867997 w9 857d88a635e3. 기준: lap1083 k1·k3·k5(수리 전), lap1081 hl6(고정).
2. 검증 항목: (a) 핵심: w1·w2·w6~w9 blend_467580_reject_size·blend_467B00_reject_size = 0(수리 전 k1 21/89), 수리 전 k1 stale ord 126~133·140~145·221~225 가 전 run 0, hold 합 w1·w7 = 2(ord 137 (799,408..409) 소잔여만, 허용). (b) w3·w4 hold 0, w5 고정 총합 291,382(hl6 ord 0..15) → 0·300..848 0. (c) E-0 UPLEFT 24칸 (158,101)→(110,101) 왕복 두 lane 같음·E-1 p95 7~11·안전 0·cleanup·source_unchanged. (d) **불충족 항목:** w2 hold 합 64 = ord 124 62 px(x6..26,y13..22) + ord 137 2; 진단 run w6 ord 123 23 px(x5..15,y0..4)·w8 ord 122 139 px(x0..31,y0..17)·w9 ord 123 23+ord 124 49(x5..25,y0..21). UPLEFT post-change 7 run 중 4 발생(w1·w7 깨끗), 수리 전 k1·k2·k6 0/3. 마지막40 0, reject 0. 귀속 UNKNOWN(샘플 3점 watch가 stale 화소를 못 잡음). 포인터가 창 (0,0)으로 가는 present의 커서 스프라이트 가설은 미검증. (e) 코드: tools/inmm_stub/g1_mirror2x.c mirror_blend_wrle·mirror_blend_clip 이 screen 크기 before + g1_overlay_blt_apply_tiled(tile 320x160) 로 바뀌었는지, 크기 사전검사 분기 제거·reject_size = apply 실패만·원본 1회 호출·blend_467B00_band_calls = 타일>1 호출 수. 테스트 단언 교체 목록은 lap 기록 W-0절(clip==skip 동등 단언 삭제 포함) — 완화인지 확인. (f) D-0′: local/maintenance/20261007_lap1085_prefix_archive/ (report.json e3125322…, plan.json c6b73fd8…, restore_verification_000/010/020.json), 21 prefix, 여유 11.32→21.25 GiB, 현재 여유 ≈7.9 GiB.
3. 수용/다음 사전등록 후보: 좌상단 소잔여 귀속·대조(수리 전 hook 대조 UPLEFT ≥5회 또는 두 hook만 우회한 대조 빌드, 샘플을 좌상단 커서 후보 영역에 맞추기·DR watch를 stale present에 한정, 포인터 위치 로그 대조), 그다음 save000 UPLEFT 맵 경계 stale ≈189k 귀속(H-D2k-s0), HUD/GDI·전체 HD coverage·G1 사용자 승인 준비. 게임 실행 전 D-0 재실행 필요(여유 < 10 GiB; archive.py 복사본은 lap1085 디렉터리 사용, 대상 lap1057~lap1079 미처리 prefix).
기록 docs/history/laps/20261007_lap1085_work_g1_hw330_blend_330x200_tiled_mirror.md. 변경(uncommitted): tools/inmm_stub/g1_mirror2x.c·tests/test_g1_rect_fill.py·tests/test_g1_overlay_blt.py. 원본 EXE b56986e0…08a8ac 불변. w9는 launcher pkill 뒤 probe 단독 완주(pair-result·cleanup 확인, .exit 파일 없음).
```
