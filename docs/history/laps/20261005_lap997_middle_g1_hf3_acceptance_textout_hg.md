# 2026-10-05 | lap997 | G1 middle: H-F3 독립 검수 수용 + 잔여 203 px = GDI TextOutA 글자 → H-G 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / 중간 계획·컨펌(middle) 1 lap. 게임 실행·source 수정·commit 0.
- 가설 / 사용자 관찰: lap996 work H-F3(`0x466B50` 좌우반전 리맵 RLE diff 미러)가 유닛 덩어리 961 px를 신규 stale 없이 제거했는지 제품 helper 없이 재계산한다. 수용 시 잔여 교집합 2,305(P6 로고 2,102 + 기타 203)에서 다음 가설을 고른다.
- 예상 PASS / FAIL 조건(lap995 사전등록): F3-1 유닛 961→≤96(3회), F3-2 신규 0·교집합 = 3,266−유닛 감소분, F3-3 invocations>0·mirrored>0·reject 보고, F3-4 안전 0·present≥850·p95≤12ms·cov p50≥98.4%·Scale2x/V2/V2q/input/minimap PASS(V2s raw 기록만).
- 변경 파일 / source fingerprint / 커밋: 이 lap은 문서만(이 기록·STATUS). lap996 source는 uncommitted 그대로이며 재확인 SHA256: `tools/inmm_stub/g1_mirror2x.c` `c2650f99dc2df8e3f162ed4da897c1153b9f04d95039fb229edeef276da5315c`, `g1_mirror2x.h` `0067b5441668cf7ec818537a33ea4ee0d0c5d711fb73ba412ac551d4f2dd2bce`, `direct_draw_trace.c` `88ee6b4ffb801a403f03f38de27f9715f48abccd83aba2d7cb335f9dffb177a9`, `tests/test_g1_rect_fill.py` `243c8bc0599644ce6b85646d2fffba2d7daf3ce42e406077d949be84229f406a` — work 기록과 일치. r1·r2·r3 `bridge/g1_mirror2x.c`가 현재 source와 byte 동일(`cmp`, bridge SHA `c2650f99…`; 기준 lap995 r4 bridge `93ee239c…`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE `b56986e0…08a8ac`(capstone 읽기 전용 역어셈블 시 SHA assert 통과). fresh save006 scale2x pair(lap996 raw), 활성8인 부하 증명 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시(공유 temp `20261005_lap997_middle_review/`):
  - `recalc_lap997.py`(numpy+stdlib, 새로 작성, `analyze_lap996.py` 미사용) `a74a3d84…864d` → `recalc_lap997.json` `0893a9ce…282`(stdout `878559…473451`). 입력: lap995 r4(H-F2 수용 기준), lap996 r1/r2/r3.
  - `census_text_attr_lap997.py` `882c3c25…5ed4` → `census_text_attr_lap997.json` `0bafc5fc…2b81`. 입력: lap992 census raw `cw_a`·`cw_b`(원본 코드, `--census-only --census-residual`), 읽기 전용.
  - `disasm_lap997.py`(lap995 복사, 원본 EXE SHA assert) `d675499a…8913`, `disasm_textout_404A40.txt` `f751ecec…11d0`.
- 측정값 / 판정:
  - **F3-1 PASS 재확인**: 공통 39덤프(300..880) 교집합 유닛 영역 `y215..254×x681..723` r4 961 → r1/r2/r3 **0/0/0**.
  - **F3-2 PASS 재확인**: r4 대비 신규 stale 0(전체·유닛 밖) 3/3, 제거 961 전부 유닛 영역, 교집합 3,266 → **2,305**(3회), r1=r2=r3 픽셀 동일. 영역: 로고 `y378..440×x700..799` 2,102·HP 0·HUD 상자 0·유닛 0.
  - **F3-3 PASS 재확인**: `mirror2x_metrics` 이벤트(각 run 1개) `flip_rle_466B50_invocations` 955/949/959 = mirrored_calls, mirrored_pixels 933,695/927,070/936,022, reject target·size·guard 0.
  - **F3-4 PASS(partial) 재확인**: 안전 7종(clip_replay·viewport mutation/restore·palette·hd_mask_outside·cache_clip_verify·identity_key) max 0 3/3, PS3 present 899/893/901, elapsed p50 5·p95 7/7/7ms·max 10/10/11, cov p50 98.804/98.801/98.793%, Scale2x/V2/V2q/input/minimap PASS, V2s FAIL(raw 기존 gate, 사용자 판단 큐) → pair HOLD(exit 2). work `recalc_lap996.json`(`0eb2af24…`)과 수치 불일치 0.
  - 코드 검토: hook 8바이트 `51 53 56 57 8B 7C 24 18`이 원본 `0x466B50` 역어셈블(lap995 `disasm_466B50.txt`)과 일치. wrapper는 `g1_overlay_blt_accepts`로 w≤320·h≤128·화면 안을 확인한 뒤에만 before 버퍼(320×128)에 복사하므로 범위 초과 쓰기 없음. 음수 x/y는 DWORD로 커져 reject. cache/panel 버퍼·높이≠600 reject.
  - **판정: H-F3 PASS(partial) 수용.** 제품 마감·사용자 승인 아님. 한계(변경 픽셀만 HD 갱신)는 H-T/H-F/H-F2와 동일.
  - **잔여 203 px 정체(새 근거)**: 로고 밖 교집합 203 = 8-연결 성분 3묶음 — A `y505..512×x226..238`(59), B `y13..18×x746..769`(57, 시계 숫자·콜론 모양), C `y583..590×x540..569`(87, 한글 글자 모양). lap992 census `cw_a`/`cw_b`의 TextOutA 표본(IAT 슬롯 `0x004E502C`)에서 매 present 같은 위치 호출: `(226,503) len4 extent 14×11` 154/153회, `(746,10) len7 24×11` 154/153회, `(540,581) len9 30×11` 74/71회 → 세 묶음이 각 TextOut 사각형 안에 정확히 들어간다. 같은 픽셀의 census last-writer map은 아래 hooked writer(A rle_plain·B rle_tinted/terrain·C dd_surface_blt)이고 residual map은 1(hook 밖 writer가 덮음)이 섞여 나온다 → **GDI TextOutA 글자**가 hook되지 않은 마지막 writer다. 호출 지점 59곳(`ff15 2C504E00` 등, 예 `0x404AC2`는 `SetTextColor`(`[0x4E5030]`, 0x010101) 뒤 x+1,y+1 그림자 TextOut → 본문). census는 이미 같은 슬롯을 `GetProcAddress(gdi32,"TextOutA")` 일치 확인 뒤 IAT 교체·복원(`slot_restored 1`)했으므로 lap968 §6의 "GDI 글자 경로 hook 불가" 조건은 **성립하지 않는다**(strategy 재호출 불필요). P6 로고 2,102는 lap952/954 명시 잔여 그대로 둔다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: H-F3 회귀 0. G1 pair HOLD(V2s raw 사용자 판단 큐)·burst UNKNOWN·PS35·P6/P7 HD·D-2·두 번째 장면·사용자 승인 미해결. G6/G7 사용자 합격(APPROVALS lap989) 대기, lap991 H-G6f probe-result 독립 재계산은 아직 별도 몫으로 남는다. 처리한 `loop/ESCALATE_SOL`(SHA256 `207cc20f40965d053e28e29a1bbc6cac9352dc417424f4ee66c9812d10c12240`) 원문은 아래 부록에 보존 후 삭제.
- 다음 한 가지: work H-G(TextOutA IAT diff 미러) — 아래 handoff.

## work handoff — H-G (TextOutA IAT 호출 전후 diff 미러)

- 변경 범위: `tools/inmm_stub/g1_mirror2x.c`(+`.h` accessor)·`direct_draw_trace.c` 요약 키 `textout_iat_*`·테스트 1개 이상(RED→GREEN). validator·gate·V2s·golden·covered 축소 금지, G2/G5/G3/G4 무접촉, 커밋 0.
- 설치: 슬롯 `0x004E502C` 값이 `GetProcAddress(GetModuleHandleA("gdi32.dll"),"TextOutA")`와 같을 때만 `VirtualProtect`로 교체(census `install_textout_slot` 패턴), detach에서 정확히 복원·복원 성공 계수. 불일치면 `textout_iat_install_mismatch`만 남기고 미설치(다른 hook 설치는 계속). census 모드(`--census-only`)와 동시 설치하지 않는다.
- wrapper `mirror_textout(hdc,x,y,text,len)`: guard/비활성/len≤0이면 원본만. `GetTextAlign(hdc)`이 `TA_LEFT|TA_TOP`(0, `TA_UPDATECP` 없음)이 아니면 reject_align. `GetTextExtentPoint32A`로 cx·cy를 구하고 사각형 `[x−1, x+cx+1) × [y−1, y+cy+1)`를 화면 800×600에 자른다(그림자 +1 포함). w>320·h>128이면 reject_size. 대상 버퍼는 화면 렌더 버퍼(pitch 832, 높이 600; 기존 wrapper가 쓰는 renderer `+G1_RENDERER_BUFFER/STRIDE`, cache·panel 버퍼 제외)를 기존 hook이 받은 renderer에서 기록해 두거나 렌더러 전역을 역어셈블로 확정해 쓴다 — 어느 쪽이든 근거 주소를 기록. 호출 전 사각형 사본 → 원본 TextOutA → `GdiFlush()` → `g1_overlay_blt_apply`(H-F3와 같은 인자). DC 좌표 = 화면 좌표(census 좌표가 묶음과 일치)로 둔다.
- 측정: fresh save006 scale2x pair 3회(lap996과 같은 명령, `--stale-mask 6-12,30-34,300-301,585-620,880`), 분석은 lap996 r1~r3 대비 공통 덤프 교집합.
- 사전등록 PASS: **G-1** 로고 밖 교집합 203 → ≤20(3/3), 묶음 A·B·C 각 ≤8. **G-2** lap996 r1~r3 대비 신규 stale 0, 교집합 2,305 → 2,102 + 로고 밖 잔여. **G-3** `textout_iat_invocations`>0·mirrored_calls>0·changed>0, reject align·size·target·guard·install_mismatch 보고, detach 복원 1. **G-4** 안전 0·present≥850·p95≤12ms·cov p50≥98.4%·Scale2x/V2/V2q/input/minimap PASS(V2s raw 기록만).
- 반증: (i) invocations>0인데 changed=0이고 묶음 그대로 → DC 대상이 화면 렌더 버퍼가 아니거나 쓰기가 지연됨 → hdc→surface(`GetDC`/`ReleaseDC`) 경로를 기록하고 middle로. (ii) invocations=0 → census와 경로 충돌, middle로. (iii) 안전>0·크래시·묶음 밖 신규 stale·p95>12ms 재현 → 되돌리고 원인 기록. 반증 2회면 BLOCKED로 결론.

## 부록 — 처리한 lap996 `loop/ESCALATE_SOL` 원문

```
lap996 work(Claude Code claude-sonnet-5-5) → middle(Opus) 독립 검수 요청: G1 H-F3 구현·실행 완료, 판정은 middle 몫.
기록: docs/history/laps/20261005_lap996_work_g1_flip_rle_diff_mirror_hf3.md (uncommitted)
결과: hook 0x466B50(8B 51 53 56 57 8B 7C 24 18) 좌우반전 리맵 RLE diff 미러. fresh save006 scale2x pair 3회(공유 temp 20261005_lap996_work_flip_rle/r1,r2,r3, 전부 exit 2 = V2s raw 기존 gate HOLD):
 F3-1 유닛 961→0 (3/3), F3-2 신규 stale 0·교집합 3,266→2,305(=−961), F3-3 flip_rle invocations 955/949/959=mirrored_calls·reject 0, F3-4 안전 0·present 899/893/901·p95 7ms·cov p50 98.8%.
middle이 확인할 것:
 1) r1·r2·r3 raw(mask/trace/pair-result)를 제품 helper 없이 재계산(analyze_lap996.py·recalc_lap996.json 대조) — 유닛 0·신규 0·계수(mirror2x_metrics 이벤트)·안전.
 2) source SHA(g1_mirror2x.c c2650f99…, .h 0067b544…, direct_draw_trace.c 88ee6b4f…, tests/test_g1_rect_fill.py 243c8bc0…)·bridge 사본 일치.
 3) 수용 시 다음 가설: 잔여 교집합 2,305 = P6 로고 2,102 + 기타 203. 203 px writer 지목(census --census-only)과 P6 로고 중 선택·사전등록.
```
