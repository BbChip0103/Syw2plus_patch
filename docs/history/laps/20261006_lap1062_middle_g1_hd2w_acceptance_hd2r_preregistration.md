# 2026-10-06 | lap1062 | G1 middle — H-D2w 독립 검수 + H-D2r 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·테스트 변경 0, commit 0.
- 입력: lap1061 work `loop/ESCALATE_SOL`(1,508 B, SHA256 `c04cb24c37e4c248e912432d022695dbeb195838aeae1961328b642b40c92254`, 원문 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1061 W-1 "스크롤 일시 stale 표본 18/18 마지막 writer = 게임 스레드 직접 쓰기 `0x467B00`(hook `reject_size`)·`0x4685C0`(미후킹)", W-2 = H2(화면 직접 writer).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac` 직접 재계산 MATCH(objdump 읽기만). fixture: 비합성 save006, lap1061 r1·r2 산출물만 읽음.

## 1. 독립 재계산(work `analyze_d2w.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1062_middle_review/`:
`recalc_lap1062.py` `c7ff4bc5…d07a` → `recalc_lap1062.json` `7c9d4a34…bd2`, `recalc2_lap1062.py` `b4463f41…cf0` → `recalc2_lap1062.json` `607e6ce6…6540`,
objdump `od_4685C0_lap1062.txt` `b28ee72a…1e49`·`od_41A000_lap1062.txt` `d2a053dc…43e4`·`od_41AC00_lap1062.txt` `f7b9aefc…53d9`·`od_41A54F_lap1062.txt` `458d35aa…1a17`.
입력 해시 6개(pair-result r1 `63e36128…`·r2 `0186e212…`, layer_drift `5cb481d7…`·`cd8f52b1…`, screen_watch `4e00f0d3…`·`64cb93bd…`) 전부 ESCALATE 기재와 일치.

| 항목 | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|
| 표본 좌표(watch `a` 주소 − `m` buffer, pitch 832) | (3,157)·(5,341)·(465,6) | 동일 | 일치 |
| stale 표본(`s` scr≠snap) | r1 18·r2 18, 전부 마지막 `x` hit 있음, val==scr 18/18 | 18/18 | 일치 |
| writer | i0 p129..134·i1 p135..140 = EIP `0x467CCF` tid 280, i2 p135..137·p228..230 = EIP `0x4687A3` tid 280 (r1=r2) | 동일 | 일치 |
| `w` 레코드 | 467B00 reject_size 12(p129..140, x −167·y −30+32k·w330·h200, sb→sa 표본 값 변경 r1=r2), 466BE0 clipped 11, 466B50 mirrored 2 | 12 reject_size | 일치 |
| watch 손실 | dropped 0·overflow 0 (r1·r2) | 0 | 일치 |
| W-0 pair·안전·I-1 | status PASS×2, 안전 7종 max 0, p95 고정/hold 10/11·12/13, tps 비 0.9965/0.9947, 마지막40 중앙값 0 | 10/11·12/12 | 정정 2 |
| objdump `0x4685C0` | `83 EC 18 \| 53 \| 55`(5 B 명령 경계, 상대주소 없음)… `ret 0x14`(`0x4687EB`), thiscall 5 인자(x·y·w·h 16비트 movsx, arg5 = 소스 바이트열), 클립 `[ecx+0x4D0..0x4DC]`, 목적지 `[ecx+0x1514]+y·[ecx+0x10]+x`, 소스 `0xFE n` = n 칸 건너뛰기·그 외 = 색 → 목적지 값 의존 혼합 표(`+0x419A1/0x41CA0/0x19A0`) 결과를 `0x4687A1 mov [edi],dl`로 쓰기 → watch EIP `0x4687A3` 일치. 호출 2곳 `0x41A12D`·`0x41ACE5`, 둘 다 `mov ecx,0xE5BF18`(= `G1_RENDERER_VA`) | 동일(인자 의미 미기술) | 일치 |
| `0x467B00` 호출처 | `0x41A06D`·`0x41AC45`(`mov ecx,0xE5BF18`), 구조는 `0x4685C0`과 같은 형제 블록 | 동일 | 일치 |

**정정 1(비차단):** i0 p129 표본의 stack 첫 항목은 `0x41A072`가 아니라 `0x41A54F`(r1·r2 동일). `0x41A54F`는 `0x41A54A call 0x466BE0` 다음 `ret`이며, `g1_screen_watch.c`의 stack은 esp 위 EXE .text 범위 값을 훑는 휴리스틱(`sp[i]` 필터)이라 이전 호출의 잔존 slot이다. EIP `0x467CCF`(=`0x467B00` 내부)와 같은 present의 `w` 467B00 reject_size(표본 114→101, scr 101)가 귀속을 직접 뒷받침하므로 판정 무관.
**정정 2(비차단):** r2 hold 창은 ps3 122..290(r1 123..291), hold p95 12/13(work 12/12). stale 덩어리는 두 run 모두 **같은 절대 ps3 순번**(129..143·227..230)에 있다.
**W-0 stale 열(work 공개 확인):** 절대 ps3 순번 120..299에서 lap1058 r1 대비 r1 10·r2 10 present 차이, 큰 덩어리(129 5,602·130 6,484·131 4,357·134 2,330·136 7,367·137 12,976·138 7,941·139 2,732·140 2,492·141 3,301·142 2,158·227 6,207·228 11,372·229 6,026)는 동일. 차이는 +49~+254 px 소덩어리(132·133·135·143·230)와 0→56~249 단발. r1·r2 사이도 9 present 같은 크기 차이 → 진단 옵션(drift observe hook·DR watch) 동반 소변동, 귀속 판정 무관.

## 2. 새 근거: hold 창 stale 마스크 분할(`stale_mask.bin` × `w` reject 사각형)

r1 hold 창 stale 합 93,956 px(r2 93,748). `0x467B00` reject 사각형(x0..163 × y..y+200 화면 교차) 안 = **37,523 px(39.9%)**, r1=r2.

| 구간 | px(r1) | 위치 | 귀속 |
|---|---|---|---|
| p129..140 reject 사각형 안 | 37,523 | 좌측 x0..64 띠(32 px/present 하강) | `0x467B00` reject_size (표본 12/12) |
| p132..138 사각형 밖 | ≈24.5k | 우상단 x≤665·y≤449 | 표본 (465,6) `0x4685C0` 3/3, 나머지 면적 미표본 |
| p141..143 | 7,087 | 좌하단 x0..47·y370..489(띠가 계속 32 px 하강) | **UNKNOWN**: `w` 레코드 없음(467B00 미호출), 표본 밖 |
| p227..230 | 24,825 | 상단 우측 x401..648·y0..100 | 표본 (465,6) `0x4685C0` 3/3, 나머지 면적 미표본 |

판정: **H-D2w PASS(진단) 수용**. W-1 표본 18/18 귀속·W-2 H2 확정, 정정 1·2 비차단. 표본 밖 면적의 writer 분포(우상단 전체가 `0x4685C0` 하나인지, p141..143 꼬리)는 미측정으로 남기고 수리 run에서 잔여로 측정한다.

## 3. work H-D2r 사전등록(다음 work, Sonnet)

같은 가설("스크롤 hold 일시 stale = 화면 직접 writer `0x467B00`(size 반려)·`0x4685C0`(미후킹)의 미미러")의 두 writer를 한 회차에서 고친다. 계수로 writer별 효과를 분리하므로 한 가지 가설 원칙과 충돌하지 않는다.

**R-1 (`mirror_blend_clip`, `0x467B00`) 행 분할 미러:**
- 공유 상수 `G1_OVERLAY_MAX_WIDTH/HEIGHT`·`g1_overlay_blt_accepts`·`g1_overlay_blt_apply`·다른 hook 버퍼는 **변경 금지**.
- 이 hook 전용 before 버퍼를 `G1_OVERLAY_MAX_WIDTH × G1_OVERLAY_SCREEN_HEIGHT`(320×600)로 키우고, 높이 한도는 화면 높이(clip 결과 자체), 폭 한도 320은 유지.
- 원본 호출 뒤 `g1_overlay_blt_apply`를 `G1_OVERLAY_MAX_HEIGHT` 이하 행 띠로 반복 호출(`before + band_row × width`, y0 + band_row). apply의 halo는 실제 post frame에서 읽으므로 띠 경계 Scale2x 결과가 단일 패스와 같아야 한다 → 단위 테스트로 증명.
- 계수 추가: `blend_467B00_band_calls`(띠 2개 이상 호출 수). 기존 `reject_size`는 폭 >320·apply 실패에만 증가.
**R-2 (`0x4685C0`) diff 미러 hook 신설:**
- `G1_BLEND_SKIP 0x004685C0u`, old bytes `83 EC 18 53 55`, LEN 5, `install_one` + restore 경로, wrapper `mirror_blend_skip` = `mirror_blend_clip`(R-1 반영판) 이름 치환 복제(인자 x·y·w·h 16비트, arg5 소스 그대로 전달), 계수 접두사 `blend_4685C0_*`(invocations·mirrored_calls·mirrored_pixels·changed_calls·clipped_calls·reject_target·reject_bounds·reject_size·reject_guard·band_calls), `layer_drift_write_end(&drift, G1_BLEND_SKIP, …)`.
- `mirror_details` 두 builder 최악 합 테스트(lap1050 정정 1·lap1051 W-S2)에 새 계수를 포함해 ≤ builder 크기 확인. 넘으면 builder 크기를 키우고 RED→GREEN 기록.
**R-0 사전 조건:** 테스트 먼저(RED): 띠 분할 = 단일 패스 동등(높이 200·600, 폭 163·320, scale2x on/off), 높이 160 이하(단일 띠, 기존 결과와 byte 동일)·높이 161·폭 >320(reject_size 유지) 경계, `0x4685C0` hook 표·old bytes·restore 계약(`test_g1_rect_fill.py` `test_blend_clip_hook_table_and_wrapper_contract` 형식). 빌드·old bytes 일치.

**실행(격리, 순차, load ≤8 대기):**
1. 진단 pair ×2: lap1061 `run_d2w.sh`와 같은 옵션(save006 D-2 hold UP/DOWN 24, `--layer-drift --screen-watch --drift-samples "3,157;5,341;465,6"`, `--stale-mask 129-143,227-230`).
2. 비진단 pair ×2: lap1058 `run_d2z_mask.sh` 옵션 그대로(진단 소변동 없는 stale 열 비교용).
3. 비회귀: save006 고정 카메라 pair ×1, save000 pair ×1(기존 pair HOLD 사유 동일 여부).

**PASS 기준(비교는 같은 모드끼리: 진단 = lap1061, 비진단 = lap1058):**
- D2r-1(R-1): 표본 (3,157)·(5,341) stale present 0/12(각 진단 run), `w` 467B00 reject_size 0, 마스크 p129..140 reject 사각형 안 stale 37,523 → ≤ 375(1%).
- D2r-2(R-2): 표본 (465,6) stale present 0/6, `blend_4685C0_invocations` > 0·hold 중 reject 0, p227..230 stale 24,825 → ≤ 250.
- D2r-3(전체): hold 창 stale 합 ≥ 80% 감소(r1 93,956 → ≤ 18,791), 최대 present 값 기록. p141..143 꼬리는 별도 기록(남으면 UNKNOWN writer 잔여로 다음 middle 판단; 이 기준 단독 FAIL 사유 아님).
- D2r-4(비회귀): pair PASS·안전 7종 0·cleanup·source_unchanged, I-0 24칸×2·clamp 없음·최종 (158,101), I-1 hold p95 ≤ 고정+16·tps 비 ≥ 0.95, 마지막40 0, save006 고정 카메라 steady 교집합 0(880 포함), save000 p298..338 0·HOLD 사유가 lap1056과 gate별 동일, `make check` PASS.
- FAIL: 크래시·안전 위반·install 실패·hook이 게임 메모리 값을 바꿈(원본 호출 인자/반환 변경)·p95 > 고정+16.
- R-1과 R-2 중 하나만 PASS면 PASS(partial)로 기록하고 남은 쪽 원인을 계수·표본으로 보고한다.

## 4. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT, focused(`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`). 결과는 STATUS에만 보강한다.
- 전체 `make check` SKIP(문서만 변경, source 불변·lap1056 full PASS 1639; 다음 work H-D2r가 변경 뒤 실행).

## 다음 한 가지

work(Sonnet) H-D2r: §3 R-0 → R-1 + R-2 구현 → 진단 pair 2·비진단 pair 2·비회귀 2 → `make check`.

## 부록: lap1061 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1061 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-D2w 진단 완료, 제품 source 변경 0.
사유: 결과가 수리 사전등록(H-D2r)을 요구하는 마일스톤 경계이고, work는 자기 결과를 승인하지 않는다.
승격 작업자(fresh Opus middle)가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1061_work_d2w/ 의 r1·r2 candidate/{layer_drift,screen_watch}.jsonl·pair-result.json 을 work 스크립트(analyze_d2w.py) 없이 새 스크립트로 재계산.
   해시 접두: r1 pair-result 63e36128, r2 0186e212, layer_drift r1 5cb481d7·r2 cd8f52b1, screen_watch r1 4e00f0d3·r2 64cb93bd.
2. 검증 항목: 표본 3점 stale 18/18(각 run) 마지막 writer = (3,157)·(5,341) p129..134/p135..140 EIP 0x467CCF(복귀 0x41A072 = call 0x467B00), (465,6) p135..137·p228..230 EIP 0x4687A3(복귀 0x41A132 = call 0x4685C0); val == scr; `w` 레코드 12개 0x467B00 reject_size(교차 높이 >G1_OVERLAY_MAX_HEIGHT 160, 인자 w330 h200 x−167); 0x4685C0 미후킹(objdump 0x4685C0..0x4687EB ret 0x14, 호출처 0x41A12D·0x41ACE5); W-0 stale 열이 lap1058과 부분 불일치(주요 덩어리 동일·일부 present ±수백 px).
3. 수용 시 work H-D2r 사전등록: R-1 0x467B00 size 한도(버퍼 320×160·g1_overlay_blt_apply 공유 상수 영향) / R-2 0x4685C0 diff 미러 hook 신설 중 순서·PASS 기준 결정. 기록 docs/history/laps/20261006_lap1061_work_g1_hd2w_scroll_stale_writer_attribution.md.
```
