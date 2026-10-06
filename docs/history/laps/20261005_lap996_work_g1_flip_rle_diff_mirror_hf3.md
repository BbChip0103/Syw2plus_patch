# 2026-10-05 | lap996 | G1 H-F3 (`0x466B50` 좌우반전 리맵 RLE 호출 전후 diff 미러)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high, Fast OFF / 실무(work) 1 lap.
- 가설 / 사용자 관찰: lap995 사전등록 — 유닛 덩어리 steady stale 961px(`y 215..254 × x 681..723`)은 `0x466B50`(thiscall 6인자 x·y·width·height·rle·lut, `ret 0x18`, 클립 없음, 대상 `[x,x+w)×[y,y+h)`)이 block_copy 뒤에 써서 남는다. 호출 전 사각형 사본 → 원본 → 바뀐 픽셀만 Scale2x 미러하면 제거된다. 역어셈블 재확인: 인자 `[esp+0x14]=x`·`+0x18=y`(pitch `[ecx+0x10]` 곱)·`+0x1c=width`·`+0x20=height`·`+0x24=rle`·`+0x28=lut`, 행 안 쓰기 주소 `edi+width-1-edx`(edx 0..width-1) → 사각형 안.
- 예상 PASS / FAIL 조건(사전등록 `20261005_lap995_middle_g1_hf2_acceptance_flip_rle_hf3.md`): F3-1 유닛 961→≤96(3회), F3-2 신규 stale 0·교집합 = 3,266−유닛 감소분, F3-3 invocations>0·mirrored_calls>0·reject 3종 보고, F3-4 안전 0·present≥850·p95≤12ms·cov p50≥98.4%·Scale2x/V2/V2q/input/minimap PASS(V2s raw는 기록만). 반증 (i) 호출>0인데 유닛>865(유력 대안 `0x466BE0`), (ii) 화면 대상 호출 0, (iii) 안전>0/크래시/유닛 밖 신규 stale/p95>12ms 재현.
- 변경 파일 / source fingerprint / 커밋: uncommitted. `tools/inmm_stub/g1_mirror2x.c`(hook `0x466B50` 8바이트 `51 53 56 57 8B 7C 24 18`, wrapper `mirror_flip_rle` = 클립 없는 사각형이라 `g1_rect_fill_region` 대신 화면 경계 검사+`g1_overlay_blt_accepts`, 별도 before 버퍼·계수 6개, install/detach/installed 목록 갱신) `c2650f99…315c`, `g1_mirror2x.h`(accessor 6) `0067b544…2bce`, `direct_draw_trace.c`(요약 키 `flip_rle_466B50_*`; `mirror_details[4096]` 안에서 여유 유지) `88ee6b4f…77a9`, `tests/test_g1_rect_fill.py`(테스트 1개 추가, RED→GREEN, 4 passed) `243c8bc0…406a`. 빌드 성공(새 경고 0, 기존 mingw 경고만). r1·r2·r3 `bridge/g1_mirror2x.c`가 현재 source와 byte 동일(`cmp`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE `b56986e0…08a8ac`(보호, 불변). fresh save006(비합성) scale2x pair, 격리 prefix/display, 활성8인 부하 증명 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시(공유 temp `20261005_lap996_work_flip_rle/`):
  - pair ×3(순차, `run3.sh`): `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap996_flip_rle_r{1,2,3} --artifact-root <공유temp>/20261005_lap996_work_flip_rle/r{1,2,3} --hd-source scale2x --stale-mask 6-12,30-34,300-301,585-620,880` 셋 다 exit 2(= pair HOLD, V2s production raw 기존 gate). 로그 `logs/gates/lap996_flip_rle_r{1,2,3}.log` `39bdf962…`·`28dd0b2a…`·`1f9f25a7…`, pair-result `fad0135a…`·`a366babe…`·`6bb688cb…`, trace `2a138966…`·`24aca487…`·`be4c118a…`, mask `6f2bc520…`·`13491aa9…`·`da5a692a…`.
  - 분석: `analyze_lap996.py`(lap994 분석 복사 + 유닛 영역·flip_rle 계수·기준 lap995 r4/lap994 r3) `645d76d9…` → `recalc_lap996.json` `0eb2af24…`.
- 측정값 / 판정:
  - **F3-1 PASS**: 유닛 영역 961 → **0**(r1·r2·r3 전부). 반증 (i) 아님.
  - **F3-2 PASS**: lap995 r4·lap994 r3 대비 공통 39덤프 신규 stale 0(전체·유닛 밖) 3회, 교집합 3,266 → **2,305**(=−961 정확, 제거 961 전부 유닛 영역).
  - **F3-3 PASS**: `flip_rle_466B50_invocations` 955/949/959 = mirrored_calls 동일(reject target·size·guard 전부 0), mirrored_pixels 933,695/927,070/936,022. 반증 (ii) 해당 없음. (계수는 `mirror2x_metrics` 이벤트에 있고 ps3 present 레코드에는 없다.)
  - **F3-4 PASS(partial)**: 안전 5종 max 0·`cache_clip_verify_failures` 0 3/3, cov p50 98.804/98.801/98.793%, present 899/893/901(≥850), p95 7/7/7ms, minimap PASS·Scale2x/V2/V2q PASS, V2s production raw 2,886/2,827/2,819(기존 gate HOLD, 사용자 판단 큐). 성능 outlier 없음(추가 pair 불필요).
  - 잔여(교집합 2,305): P6 로고 2,102(명시 잔여) + 기타 203. HP·HUD 상자·유닛 0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 회귀 0(F3-2·안전 0). 한계: 바뀐 픽셀만 HD로 갱신(H-T/H-F/H-F2와 같은 한계). census는 `0x465B30` 등을 hook하므로 계속 `--census-only`. 독립 검수 대기(middle), 사용자 승인 아님. `game` 사본 없음(runner 정리), prefix 보존, 디스크 여유 약 92GiB.
- 다음 한 가지: middle 독립 검수(r1·r2·r3 raw 재계산) 후 남은 203 px의 writer 지목(census `--census-only`) 또는 P6 로고 2,102 가설 선택.
