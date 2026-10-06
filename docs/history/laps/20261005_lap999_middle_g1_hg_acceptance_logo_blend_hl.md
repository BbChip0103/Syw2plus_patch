# 2026-10-05 | lap999 | G1 middle: H-G 독립 검수 수용 + 남은 교집합 2,102 = P6 로고 `0x4672E0` → H-L 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / 중간 계획·컨펌(middle) 1 lap. 게임 실행·source 수정·commit 0.
- 가설 / 사용자 관찰: lap998 work H-G(gdi32 `TextOutA` IAT 슬롯 `0x004E502C` 호출 전후 diff 미러)가 로고 밖 잔여 203 px(GDI 글자 A·B·C)를 신규 stale 없이 제거했는지 제품 helper 없이 재계산한다. r3의 프레임 880 부재·성분 D(24 px)가 H-G와 무관한지 판정한다. 수용 시 남은 교집합에서 다음 가설을 고른다.
- 예상 PASS / FAIL 조건(lap997 사전등록): G-1 로고 밖 교집합 203→≤20(3/3)·A/B/C 각 ≤8, G-2 신규 stale 0·교집합 2,305→2,102+로고 밖 잔여, G-3 invocations>0·mirrored>0·changed>0·reject 보고·detach 복원 1, G-4 안전 0·present≥850·p95≤12ms·cov p50≥98.4%·Scale2x/V2/V2q/input/minimap PASS(V2s raw 기록만).
- 변경 파일 / source fingerprint / 커밋: 이 lap은 문서만(이 기록·STATUS), `loop/ESCALATE_SOL` 처리 후 삭제. lap998 source는 uncommitted 그대로이며 재확인 SHA256: `tools/inmm_stub/g1_mirror2x.c` `a1bde2b0f8bb0ce7edc2129c54cde2a62b7f2e70e695906efc78fa520a47a77e`, `g1_mirror2x.h` `96131f21d150bcc4a7f28ebc055370e04818143886f28ba722c972354f0e07ba`, `direct_draw_trace.c` `fc99e3822023d183ae910d94c82773e7ba4bf97f628f43fe713cb4194cb51c59`, `tests/test_g1_rect_fill.py` `e86327af8ad50dfec64aa85752dcbc297fbc89a0617f1c507c957428ee9e2b83` — work 기록과 일치. r1~r4 `bridge/`의 `g1_mirror2x.c`·`.h`·`direct_draw_trace.c`가 현재 source와 byte 동일(`cmp`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE `b56986e0…08a8ac`(읽기 전용 import 표·역어셈블 시 SHA assert 통과). fresh save006 scale2x pair(lap998 raw, 기준 lap996 raw), 활성8인 부하 증명 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시(공유 temp `20261005_lap999_middle_review/`):
  - `recalc_lap999.py`(numpy+stdlib, 새로 작성, `analyze_lap998.py` 미사용) `b4fe19e0214c59b553991de9e5c7fdf89c06f21baa80e132431d660818a9090c` → `recalc_lap999.json` `47e8a0319d1e18965412a26c3094e4d158e1283406ba56864850fd1cbe9fe7d7`(stdout `8aede14137cb5ac53f8a34ac1e5c6efe32e9044fe6a162b1e12b46029b3902d2`). 입력: lap996 r1/r2/r3(H-F3 수용 기준 b1~b3), lap998 r1~r4(n1~n4). 비교 두 가지: 7개 run 공통 프레임(300..620, 38개)과 r3 제외 공통 프레임(300..880, 39개).
  - `xref_4672E0.py` `6f87d7a4b0d8f15814b31a06c8a73d40875c3c6d434c00dbfb9e86ad00c5ef12` → `xref_4672E0.txt` `3175a0a33b2bc89f992c38603b24fb3337e9abdfefee7776290ceb7bec37ac0c`; `disasm_4672E0.txt` `7b55d9c4c0eb326ba5e9e96f46823147b697e7ac2a9866c0dc987cb96f6fe3c5`·`disasm_callers_4672E0.txt` `326d1d7012942204e39dd3834e9adfeaa1780139dcb9f1be140f9a244c67fb2f`(lap997 `disasm_lap997.py`를 인자만 바꿔 실행).
  - work 산출물 해시 재확인: pair-result `e9af2f09`·`79a6b821`·`ebf2d4b0`·`7da7aaa5`, trace `adf05480`·`65a4a039`·`80b148fa`·`ed2c001d`, mask `648746ea`·`b6c01df5`·`5d11b05a`·`8b47c3b3`, 로그 `logs/gates/lap998_textout_r{1..4}.log` `24bca0d2`·`e881ec5d`·`f6851c3b`·`c349fd6b`, `analyze_lap998.py` `495884c0`·`recalc_lap998.json` `c0e36f4e` — 기록과 전부 일치.
- 측정값 / 판정:
  - **G-1 PASS 재확인**: r3 제외 39프레임 기준 로고 밖 교집합 b1~b3 203 → n1/n2/n4 **0/0/0**, 자체 steady(각 run ≥300 전 프레임)도 n1/n2/n4 0. 텍스트 사각형(census 표본 extent±1) A `y502..514×x225..240`·B `y9..21×x745..770`·C `y580..592×x539..570`은 기준 49/58/96(합 203) → 4/4 전부 **0**. (work의 59/57/87은 성분 단위 분할이라 칸 배정만 다르고 합 203은 같다.)
  - **r3·성분 D 판정**: n3 덤프 50개(프레임 300..620, 880 없음; PS3 present 868로 창 안 present 수가 적음, probe 정상 종료 HOLD·scene_state_equal true). 7개 run 공통 38프레임에서 로고 밖은 b1~b3 **227**, n1~n4 **24**(4개 모두 같은 성분 D `y515..520×x616..619`). D는 7개 run 모두 프레임 300..620 38개에서 24 px 전부 stale, 프레임 880이 있는 6개 run에서는 880에서 0 → **기존 일시 stale, H-G 무관, 신규 아님**. HUD 상자 영역(x618..719)에 걸친 4열 조각이며 정체는 미조사(별개 항목).
  - **G-2 PASS 재확인**: 두 비교 모두 n1~n4가 어느 기준 run에도 없던 stale **0**(new_vs_any_base 0), 모든 기준에 있던 stale 중 제거 203 전부 A·B·C 사각형 안(elsewhere 0). 교집합 39프레임 2,305 → **2,102**(n1=n2=n4 픽셀 동일), 38프레임 2,329 → 2,126(n1~n4 동일). b1=b2=b3 픽셀 동일.
  - **G-3 PASS 재확인**: `textout_iat_metrics` 이벤트 각 1개 — invocations 16,209/16,526/16,406/15,869, mirrored_calls 10,556/10,866/10,782/10,262, changed 10,283/10,588/10,503/9,999, reject_target 5,587/5,588/5,558/5,537, align·size·guard 0, install_mismatch 0, slot_installed 1; `textout_iat_restore` 이벤트 slot_restored 1 4/4. flip_rle 957/959/946/947 = mirrored(H-F3 유지).
  - **G-4 PASS(partial) 재확인**: 안전 7종 max 0 4/4, PS3 present 900/901/868/886, elapsed p50 5·p95 7ms 4/4(max 11/21/9/9), cov p50 98.86%, Scale2x/V2/V2q/input/minimap PASS, V2s FAIL(raw 기존 gate, 사용자 판단 큐) → pair HOLD(exit 2). work `recalc_lap998.json` 수치와 불일치 0.
  - 코드 검토: 원본 import 표에서 gdi32 IAT `0x4E502C` = `TextOutA` 확인. 설치는 슬롯 값=실제 TextOutA·보조 API 3개 해석 시에만, 복원은 슬롯이 wrapper일 때만. before 버퍼 320×128, `g1_overlay_blt_accepts`가 w≤320·h≤128·화면 안을 확인한 뒤에만 복사 → 범위 초과 쓰기 없음. 정렬≠0·cache/panel·높이≠600 reject. apply 실패도 `reject_size`로 합산되는 점은 계수 해석 한계(현재 0이라 무영향).
  - **판정: H-G PASS(partial) 수용.** 제품 마감·사용자 승인 아님. 한계(변경 픽셀만 HD 갱신)는 H-T/H-F 계열과 동일.
- 남은 교집합 2,102 = P6 로고 전부 → **H-L FEASIBLE**(정적 근거, 원본 읽기 전용):
  - `0x4672E0` 역어셈블: 프롤로그 6B `51 53 56 8B F1 57`(push ecx/ebx/esi, mov esi,ecx, push edi — 위치 독립), thiscall, 인자 5개 word `movsx`(x `[esp+4]`, y `+8`, w `+0xC`, h `+0x10`, RLE `+0x14`), `ret 0x14`. 목적지 = `[ecx+0x1514] + y*[ecx+0x10] + x`, 쓰기 `mov [edi+ecx-1],dl`(`0x4673CF`)은 열 `[x, x+w)`·행 `[y, y+h)` 안. **클립 없음**.
  - xref(rel32/rel8·절대값 전수 바이트 스캔): 호출 2곳 `0x41A59D`·`0x41A715`, 둘 다 직전 `mov ecx,0xE5BF18`(H-G·H-F 계열과 같은 렌더러 전역). 프롤로그 `0x4672E1..E5`로 들어오는 분기·절대 참조 0.
  - lap954의 "명시 잔여 P6" 분류는 HD 혼합(HD 해상도에서 50% 평균) 구현을 뒤로 미룬 것이다. H-T~H-G가 수용한 방식(원본 8비트 결과의 변경 픽셀만 Scale2x 미러)을 쓰면 stale(=nearest 출력)은 없앨 수 있다. HD 혼합 화질 자체는 여전히 P6 잔여로 남긴다(scale2x 출처에서는 결과가 완벽 Scale2x 기준과 같다).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: H-G 회귀 0. G1 pair HOLD(V2s raw 사용자 판단 큐)·성분 D(일시)·burst UNKNOWN·PS35·P6/P7 HD 화질·D-2·두 번째 장면·사용자 승인 미해결. G6/G7 사용자 합격(APPROVALS lap989) 대기, lap991 H-G6f probe-result 독립 재계산은 별도 몫으로 남는다. 처리한 `loop/ESCALATE_SOL`(SHA256 `08f8586f635638a0e7b4bf0a16e9672bb156d64fa8f9300712d2ec78e296da45`) 원문은 아래 부록에 보존 후 삭제. 디스크 여유 87G.
- 다음 한 가지: work H-L(로고 반투명 RLE `0x4672E0` diff 미러) — 아래 handoff.

## work handoff — H-L (반투명 RLE `0x4672E0` 호출 전후 diff 미러)

- 변경 범위: `tools/inmm_stub/g1_mirror2x.c`(+`.h` accessor)·`direct_draw_trace.c` 요약 키 `blend_4672E0_*`·테스트 1개 이상(RED→GREEN). validator·gate·V2s·golden·covered 축소 금지, G2/G5/G3/G4/G6/G7 무접촉, 커밋 0.
- 설치: H-F3와 같은 `install_one` 패턴, 주소 `0x004672E0`, 기대 바이트 6개 `51 53 56 8B F1 57`(불일치면 설치 실패로 기존 규칙대로 처리). detach 원복 포함.
- wrapper(thiscall, `ret 0x14`, 인자 5개): **인자는 반드시 하위 16비트 부호확장**(호출자가 상위 word를 0으로 두지 않음: lap953 실측 w `0x90064`→100, h `0x47B0040`→64). guard/비활성이면 원본만. `ecx != 0xE5BF18`·buffer 없음/cache/panel·stride 범위 밖·높이≠600이면 `reject_target`. w≤0·h≤0·x<0·y<0·x+w>800·y+h>600이면 `reject_bounds`(원본은 클립 없음 — 자르지 말고 미러만 생략). w>320·h>128이면 `reject_size`. 통과 시 `[x, x+w)×[y, y+h)` before 사본 → 원본 호출 → `g1_overlay_blt_apply`(H-G와 같은 인자)로 변경 픽셀 미러, 계수 invocations·mirrored_calls·mirrored_pixels·changed_calls·reject 4종.
- 측정: fresh save006 scale2x pair 3회(lap998과 같은 명령, `--stale-mask 6-12,30-34,300-301,585-620,880`). 분석 기준 = lap998 n1/n2/n4(39프레임). **모든 run이 같은 프레임 집합을 갖는지 먼저 보고**하고, 프레임 880이 빠진 run이 있으면 39프레임·공통 프레임 두 비교를 모두 낸다(성분 D는 880에서만 사라지는 기존 항목).
- 사전등록 PASS: **L-1** 로고 영역 `y378..440×x700..799` 교집합 2,102 → ≤210(3/3). **L-2** 기준 대비 신규 stale 0, 로고 밖 교집합 0 유지(39프레임). **L-3** invocations>0(present당 약 1회 예상)·mirrored>0·changed>0, reject 4종 보고. **L-4** 안전 0·present≥850·p95≤12ms·cov p50≥98.4%·Scale2x/V2/V2q/input/minimap PASS(V2s raw 기록만).
- 반증: (i) invocations=0 → hook 미도달·설치 실패 원인 기록 후 middle로. (ii) changed>0인데 로고 stale 그대로 → 블렌드 뒤 다른 미후킹 writer가 덮는다는 뜻, census `--census-only` watch `782,380`으로 마지막 writer 기록 후 middle로. (iii) 안전>0·크래시·로고 밖 신규 stale·p95>12ms 재현 → 되돌리고 원인 기록. 반증 2회면 BLOCKED로 결론.
- 범위 밖: 같은 계열 `0x467580`(PS3 present 2~6 초기 효과만, steady 마스크 프레임 밖)·`0x467410`·`0x4676D0`(hit 없음)은 이번에 hook하지 않는다. 성분 D 정체 조사는 별개.

## 부록 — 처리한 lap998 `loop/ESCALATE_SOL` 원문

```
lap998 work(Claude Code claude-sonnet-5-5) → middle(Opus) 독립 검수 요청: G1 H-G(TextOutA IAT diff 미러) 구현·실행 완료, 판정은 middle 몫(마일스톤 경계 아님, 일반 work→middle 인계).
기록: docs/history/laps/20261005_lap998_work_g1_textout_iat_diff_mirror_hg.md (uncommitted)
결과: IAT 슬롯 0x4E502C 교체(슬롯 값=gdi32!TextOutA 일 때만, detach 복원) TextOut 사각형 diff 미러. fresh save006 scale2x pair 4회(공유 temp 20261005_lap998_work_textout/r1..r4, 전부 exit 2 = V2s raw 기존 gate HOLD):
 G-1 로고 밖 교집합 203→0(r1,r2,r4)·A/B/C 4/4 전부 0, r3만 24(프레임 880 덤프 없음→공통 38프레임, 같은 프레임에서 기준 lap996도 227이라 신규 0, 성분 D y515..520×x616..619),
 G-2 신규 stale 0·교집합 2,305→2,102(=로고 전부), G-3 invocations ~16k·changed_calls ~10k·install_mismatch 0·slot_restored 1, G-4 안전 0·present 900/901/868/886·p95 7ms·cov p50 98.86%.
middle이 확인할 것:
 1) r1~r4 raw(mask/trace/pair-result)를 제품 helper 없이 재계산(analyze_lap998.py·recalc_lap998.json 대조) — 로고 밖 0·신규 0·textout 계수·안전.
 2) r3 프레임 880 부재와 성분 D(24px)가 H-G 무관임을 판정(기준 lap996 r1~r3 동일 프레임 집합 대조).
 3) source SHA(g1_mirror2x.c a1bde2b0…, .h 96131f21…, direct_draw_trace.c fc99e382…, tests/test_g1_rect_fill.py e86327af…)·bridge 사본 일치.
 4) 수용 시 다음 가설: 남은 교집합 2,102=P6 로고 `0x4672E0`(명시 잔여) 재검토 또는 두 번째 장면·성분 D.
```
