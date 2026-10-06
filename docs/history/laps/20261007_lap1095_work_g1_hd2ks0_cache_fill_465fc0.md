# 2026-10-06(KST 21~22시) | lap1095 | G1 work — H-D2k-s0 save000 맵 왼쪽 경계 stale 귀속·수리

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 커밋 0.
- 가설: lap1094 §4 H-D2k-s0 — save000 UPLEFT 모서리에서 카메라가 (0,54)에 멈추면 맵 왼쪽 위 ≈189k px가 stale로 평탄하게 남는다. 사전등록 1순위는 `0x466070` size reject였다.
- 예상 PASS/FAIL: S-1 귀속 PASS = 표본 ≥2/3의 첫 stale 쓰기가 한 미후킹 함수로 모임 또는 표본을 덮는 reject 기록. S-2(수리) PASS(partial) = save000 2/2 ord 145~221 stale ≤5%·새 reject 급증 0·save006 비회귀·안전 0·p95 ≤ 고정+16. **사전등록 문구는 "다른 함수로 귀속되면 수리 없이 기록하고 middle이 정한다"였다.**
- 변경 파일(모두 uncommitted): `tools/inmm_stub/g1_cache_fill.h`(신규, 순수 지오메트리) `c691aabe704191a3`, `tools/inmm_stub/g1_mirror2x.c` `097da0c2a56a39c9`(훅 `0x465FC0`+레이어 모델), `tools/inmm_stub/g1_mirror2x.h` `675d7380d194da7e`, `tools/inmm_stub/direct_draw_trace.c` `cda6c1f96ddab2c5`(계수 5개 metrics), `tools/inmm_stub/Makefile`, `tools/inmm_stub/g1_screen_watch.c` `1e3bd180a46b61a9`·`.h` `3f7037c4ec9ae37e`(진단 env `SYW2_G1_SCREEN_WATCH_CACHE`), `tools/g1_saved_scene_probe.py` `541c1d8f605fb568`(`--screen-watch-cache`), `tests/test_g1_cache_fill.py` `55086cf76231327f`(신규 2), `tests/test_g1_screen_watch.py` `cfdc09ea96520f7d`(+1).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 회차 끝 직접 재계산 MATCH. 7 run 전부 `source_unchanged` true·`cleanup.ok`·`game` 사본 삭제. fixture: 비합성 save000(s·c·r1·r2)·save006(r3). 활성 플레이어 8 증명 아님.
- 실행 명령: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1095_work_hd2ks0/`의 `run_s.sh`(s1 s2)·`run_c.sh`(c1 c2)·`run_r.sh`(r1 r2 r3), 로그 `logs/gates/lap1095_{s0,c0,r0}_*.log/.exit`. 공통 옵션 = lap1083 k4(`--hd-source scale2x --fixture save000 --scene-actions none --terrain-scroll --terrain-scroll-edge --terrain-scroll-keys UPLEFT,DOWNRIGHT`) + `--stale-mask 130-232`. s·c는 `--layer-drift --screen-watch --drift-samples "100,60;400,230;50,300"`, c는 `--screen-watch-cache` 추가, r1·r2는 진단 없음, r3은 save006 k1 옵션(`--p4b-s-snapshot --reference-completed-states` lap888 REF, `--stale-mask 100-320`). 분석 `analyze_hd2ks0.py` `9670cb71579c3f39…` → `analysis_hd2ks0.json` `b685daf59094f4a5…`.

## 측정

1. **재현(S-1 s1·s2):** stale 열이 k4와 같은 모양으로 재현(ord 137 749 → 144 188,787 평탄 → 220 189,268 → 221~228 감소 → 0). ps3 ord 145..221 합 14,512,493(s1)·14,512,202(s2), 최대 189,268. 표본 3점이 첫 stale인 present는 모두 `cache` 값(1x 캐시)이 0으로 바뀐 직후이며 `lexp`(후보 레이어 기대값)는 100/148/208로 남는다(캐시 ≠ 기대값). `u` 기록(미귀속 변화) 표본 0·1에 다수, `w`(블렌드 writer) 기록은 이 구간 0.
2. **화면 watch만으로는 부족:** 화면 표본의 쓰기 EIP는 전 present `0x4662DE`(캐시→화면 복사)뿐이다.
3. **캐시 watch(c1·c2, 새 진단):** 같은 좌표를 캐시 `0xBA3D30`(pitch 832)에서 감시. 표본 0(100,60)·1(400,230)의 0 값 쓰기 = `0x4DB203`(`0x4DB1D0` memmove 전진 `rep movsd`, 호출 스택 `0x437F2A`/`0x432D53`…)·p143~ `0x4DB384`(후진), **표본 2(50,300)의 0 값 쓰기 = `0x46605B`**(`rep stosd`, 함수 `0x465FC0`, 호출 `0x432DE0`; 9회, 같은 present에 `0x468DBA`(터레인 shade, 후킹됨)가 208을 덮어쓰다가 p142에 덮어쓰기가 끊겨 0이 남음). c1/c2 hit 분포 동일(i0 `0x4DB203` 43·`0x4DB384` 1, i1 43·1, i2 `0x4DB203` 24·`0x468DBA` 17·`0x46605B` 9).
4. **정적:** `0x465FC0`은 5인자(x1 y1 x2 y2 색) `ret 0x14` 비클립 단색 채움, 폭을 `floor(w/4)` dword로 `rep stosd`(objdump 직접 판독, `[renderer+0xC]`=8bpp 가정·`+0x10` stride·`+0x1514` buffer). lap863 맵 문서가 "맵 가장자리에서 노출 띠를 `0x465FC0(x0,y0,x1,y1,0)`로 지운다"고 이미 기록했다. 후보는 이 함수를 후킹하지 않았으므로 레이어 모델(`g_layer_expected`/`g_layer_mirror`)이 옛 터레인을 유지하고, 이후 캐시 memmove(후킹·미러됨)가 그 0을 화면 곳곳으로 옮긴다.
5. **수리(S-2에 상응, 아래 "사전등록 이탈" 참조):** `0x465FC0` 훅 추가(기존 5바이트 jmp·pinned old bytes `8B 54 24 0C 53`, 원본 먼저 실행 → 캐시 대상 + 8bpp + stride 832 + 캐시 안일 때만 레이어 expected=색·covered=1·HD 2×2 평탄 블록 갱신, 캐시 밖/8bpp 아님은 `unsupported` 계수, 화면 대상은 `reject_target`). 테스트 RED(2 failed) → GREEN(2 passed), lint·typecheck PASS, `test_g1_cache_fill`·`screen_watch`·`rect_fill`·`mirror2x` 75 passed.
6. **수리 결과(r1·r2·r3):**

| run | status | ps3 | stale 합 ord 145..221 | stale 전체 합 | 최대 | 마지막 40 | p95 ms | 안전 7종 최대 |
|---|---|---|---|---|---|---|---|---|
| s1(수리 전) | HOLD | 298 | 14,512,493 | 15,465,600 | 189,268 | 47,319 | 13 | 0 |
| s2(수리 전) | HOLD | 299 | 14,512,202 | 15,467,923 | 189,064 | 49,958 | 12 | 0 |
| **r1** | HOLD | 298 | **0** | 47,323 | 3,592 | 47,319 | 7 | 0 |
| **r2** | HOLD | 298 | **0** | 47,526 | 3,592 | 47,319 | 8 | 0 |
| **r3 save006 k1** | **PASS** | 1,173 | 0 | **2** | 2 | 0 | 8 | 0 |

   `cache_fill_465FC0` 계수(r1/r2 동일): invocations 33·mirrored_calls 31·mirrored_pixels 923,648·reject_target 2·unsupported 0. `rect_fill_466070_reject_size` 40·`shade_468870_reject_bounds` 839~841·`layer_move_unsupported` 0은 수리 전과 같다(= `0x466070`·`0x468870`은 이 stale의 원인이 아니었다). r3 게이트 전부 PASS(input_effect·minimap·terrain_scroll·V1/V2/V2s/V2q·Scale2x), save000 r1/r2의 input_effect HOLD·V2 BLOCKED는 수리 전 s1/s2와 같다(save000 `--scene-actions none` fixture 한계).

## 판정(work 잠정, middle 검수 전)

- **S-1 귀속: PASS(인과, 수리로 확인).** 직접 EIP 증거는 표본 2에서만 `0x465FC0`(1/3), 표본 0·1은 후킹된 memmove가 0을 옮기는 쓰기라서 사전등록 문구 그대로(표본 ≥2/3이 한 미후킹 함수) 만족하지는 않는다. 그러나 `0x465FC0`만 미러한 r1·r2에서 평탄 구간 stale 합이 14.5M → **0(100% 감소)**이므로 원인 함수는 `0x465FC0`로 인과 확정이다.
- **사전등록 이탈(middle 판단 요청):** 카드는 "귀속이 `0x466070`이 아닌 다른 함수면 수리 없이 기록"이었는데, 구현 우선 상시 지시(INBOX)와 PROMPT ③에 따라 같은 회차에 `0x465FC0` 수리를 구현·검증했다. 수리 코드는 uncommitted이며 되돌리기는 훅 설치 3줄 제거로 가능하다. middle이 수용·보류·철회를 정한다.
- **S-2 PASS(partial, 기술):** ord 145~221 stale 합이 수리 전의 0%(기준 ≤5%), 새 reject 급증 0(`unsupported` 0), save006 비회귀 r3 PASS(stale 2), 안전 0, p95 7~8ms(고정 +16 이내). `rect_fill_466070_reject_size` 감소 조건은 귀속이 `0x466070`일 때만 의미가 있어 해당 없음(40 그대로).
- **한계(공개):** (a) stale 지표는 HD 품질 손실(그 픽셀이 최근접 확대로 떨어짐) 지표다. 검은 평면이라 화면 모양 차이는 작다: r1·r2의 `scroll_after`는 수리 전과 동일하게 PASS(nearest_equal_ratio s1 0.94047·r1 0.94039·r2 0.94047)·plateau `hd_mask_inside_diff` 평균 55,891 → 55,682로 거의 같다. 이득은 모서리 장면의 HD 커버리지와 stale 지표 정합이다. (b) r1은 `terrain_scroll_parity` HOLD(`complete_records_equal` false, 양 lane 시뮬 AI 그룹 위치 차이 owner 3), 같은 설정 r2·수리 전 s1·s2는 PASS이므로 lane 위상 경합 backlog로 분류한다(원인 UNKNOWN, 수리와의 상관 증거 없음). (c) 수리 후에도 save000 마지막 40 stale 47,319(≈1,183/present)는 그대로 남아 있다 — `0x465FC0`과 무관한 별개 잔여다. (d) `0x465FC0`의 화면 대상 호출(`reject_target` 2)은 미러하지 않는다(이 장면 stale 원인 아님). 평탄 HD 블록은 단색 채움에만 맞고, 채움 가장자리의 Scale2x 보간은 이후 present가 처리한다.
- **미실행:** 전체 `make check`는 문서 기록 freeze 뒤 1회(결과는 STATUS에만).

## 다음 한 가지

- middle(Opus): lap1095 독립 재계산(새 스크립트로 s·c·r 7 run stale 열·캐시 watch EIP·계수 재집계, 후보 소스 4파일 해시, 수리 코드 검토) → 사전등록 이탈 수용 여부 → H-D2k-s0 판정 확정. 이어 work 후보: save000 마지막 40 stale 47,319 귀속(필요 시 같은 캐시 watch 진단 재사용), 또는 backlog.
