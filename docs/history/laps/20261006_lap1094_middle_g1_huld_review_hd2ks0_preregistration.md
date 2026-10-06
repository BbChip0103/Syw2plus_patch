# 2026-10-06 | lap1094 | G1 middle — H-ULd 독립 검수 + save000 맵 경계 stale 귀속(H-D2k-s0) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1089 work 기록 `20261007_lap1089_work_g1_huld_diag_ct_control.md`, 그 ESCALATE_SOL 원문 `20261007_lap1090_preserved_lap1089_escalate_sol_g1_huld.txt`, 사전등록 `20261006_lap1088_middle_g1_hulc_review_huld_preregistration.md` §4.
- 시작 시 `loop/ESCALATE_SOL` = lap1093 middle → root 전달 요청(G7 시험판·사용자 재시험). root 몫이라 이 회차는 내용을 바꾸지 않고 끝에 lap1094 한 줄만 덧붙였다. INBOX·APPROVALS에 lap1093 뒤 새 사용자 판단은 없다.
- 가설(검수 대상): H-ULd — UL 소잔여(x0..31·y0..22)는 진단 옵션이 바꾼 present 시간에서 나는 기존 잔여이고 H-W330과 무관하다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만). fixture: 비합성 save006(H-ULd), save000(k4 읽기만).
- 현재 트리 source 해시(직접 계산): `tools/inmm_stub/g1_mirror2x.c` `d66a3afdd9ba30e3`, `tools/g1_saved_scene_probe.py` `77d4ec093eed8031`(= 8 run pair-result `execution_source.host_probe_sha256`), `tests/test_g1_mirror2x.py` `bc97ce6326518850` → lap1088 검수 트리와 같다(work 기록 (g) 일치).

## 1. 독립 재계산(work `analyze_huld.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1094_middle_review/`:
`recalc_lap1094.py` `f523ca30…00a3`(새 스크립트: 게이트 상태·두 lane 카메라 고유 위치 수·ord별 UL 모양 SHA·수리 전 ord 열 k6 값 대조·tick 점프·watch EIP 직접 집계) → `recalc_lap1094.json` `53a83497…5975`, 출력 `recalc_out.txt` `08181bbc…c8f`. 기준: lap1083 k6, lap1087 d1, lap1085 w2·w6.
pair-result SHA 접두 8/8이 ESCALATE 기재와 같다. stale_mask SHA 8/8 = pair-result 기재 값, mask와 trace `stale_pixels` 불일치 0.

| 항목 | work 기재 | middle 재계산 | 판정 |
|---|---|---|---|
| (a) 충실도 | cd1·cd2·cd4 21/89·수리 전 합 240,701, cd3 21/87·230,565 | 같다. cd1·cd2·cd4 수리 전 ord 19개 값 열이 k6와 **값까지 같음**(3/3), cd3 다름 | 일치 |
| (b) td | reject 0/0, UL 72 4/4 | 같다. ord 123 23 px(x5..15·y0..4)+ord 124 49 px(x6..25·y13..21) 4/4 | 일치 |
| (c) cd UL | 72·62·0·62 | 같다. cd2·cd4 = ord 124 62 px(x6..26·y13..22) | 일치 |
| (d) 위상 | 8/8 tick 건너뜀 | tick 점프 ord 123(cd1·td1~td4·cd3) 또는 124(cd2·cd4), 카메라 첫 이동 ord 123(tick 24693, cd2·cd4는 24692), 커서 (0,0) 첫 present 123 또는 124 | 일치 |
| (e) 공통 | 안전 0·p95 ≤12 | 안전 7종 최대 0, p95 hold 11~12/고정 10~12, 두 lane `cleanup.ok`·`game_removed`·`source_unchanged` true, 원본 접두 `b56986e018b4` 16/16, `game` 사본 0개 | 일치 PASS |
| cd3·td4 HOLD | candidate 관측 24 vs 25 | candidate lane 고유 카메라 위치 수: cd3 UPLEFT 23칸(끝 x 112 vs 110), td4 DOWNRIGHT 23칸(끝 156 vs 158). baseline은 24칸. 게이트 input_effect·minimap·terrain_scroll HOLD, cd3 v2·v2q FAIL·td4 v2q FAIL | 일치(같은 사실, 다른 셈법) |
| (f) D-0 | 23 prefix, 12.43→22.42 GiB | report `15dd94f6…0586` 일치, 23/23 `prefix` 부재·`manifest.json` 23/23 존재·`removed_private_prefix_only` 23/23, 첫·끝 archive SHA 재계산 일치, full restore 3개(000/010/020) `full_content_metadata_match` true, free_before/after 13,342,240,768/24,076,836,864 B | 일치 PASS |

**결정적 근거(새로 계산):** ord별 UL 마스크 모양 SHA가 수리 ON/OFF에 무관하게 같다.
- ord 123 모양 `0d02ee1d7d55`: cd1·td1·td2·td3·td4·d1·w6 전부 같음.
- ord 124 모양 두 종류: `236a0eda173d`(49 px) = cd1·td1~td4, `5b987a718b90`(62 px) = cd2·cd4·**w2**.
- 62 px 모양은 tick 점프 ord 124·카메라 첫 이동 tick 24692인 run(cd2·cd4·w2)에만 나온다. 즉 UL 모양은 **위상**이 정하고, H-W330(수리)의 켜짐/꺼짐은 바꾸지 않는다. cd1(수리 OFF)과 td1~td4(수리 ON)의 UL 마스크는 픽셀까지 같다.

## 2. 정정·관찰

1. **정정(td3 서술):** work 표의 "hold 밖 ord 219 233"은 틀렸다. ord 219는 hold 안(hold = ord 123..291)이고 hold 합 307 = 23+49+2+233에 들어 있다. hold 밖 값은 **ord 315 291 px**이다(work 분석 JSON이 hold 밖을 출력하지 않아 생긴 전사 오류). k6 ord 316/317 290·291 px와 같은 종류의 진단 동반 일시 잔여이며 판정과 무관하다.
2. 관찰: candidate lane 한 칸 손실 run(cd3·td4)만 watch에 `0x466D15`(5·8회)가 있고 `0x4662DE` 쓰기가 4,632/4,446회로 다른 run(3,531~3,549)보다 많다. lane 위상 경합 backlog의 새 공변량이다(원인 UNKNOWN, 비차단).

## 3. 판정

- **D-0 PASS 수용.**
- **H-ULd 사전등록 (a) 충족 수용.** 충실도는 cd run마다 정의되어 있으므로 cd3만 무효이고(원인: candidate lane 한 칸 손실), 유효 cd 3/3에서 UL > 0이다. 해석 (ii)(cd 전체 BLOCKED)는 사전등록 문구("cd run마다…아니면 대조 무효")와 맞지 않아 채택하지 않는다. cd3을 넣어도 (a) 조건("cd 중 1 run 이상 UL > 0")은 바뀌지 않는다.
- **H-W330 PASS(partial) 확정**(lap1086 핵심 효과: 330×200 reject 0, hold 240,703 → 2, 고정 291,382 → 0). uncommitted 유지. 제품 G1 마감·사용자 승인 아님.
- **UL → backlog H-UL**: 위상(진단 부하로 생긴 tick 점프 ord 123/124 또는 커서 선행 ord 122)에서 나는 일시 잔여(마지막40 0). writer 1순위 후보 미후킹 `0x466130`(d1 표본 첫 쓰기 `0x46624F`), 미입증.

## 4. 다음 work 사전등록(Sonnet) — H-D2k-s0: save000 맵 왼쪽 경계 stale ≈189k 귀속 → 조건부 수리

**사전 근거(이 회차 k4 raw 읽기만, `20261007_lap1083_work_hd2k/k4`):**
- stale은 카메라 x 15 → 11(ord 138, 749 px, x0..94·y0..47) → 7(ord 140, 26,868 px, x0..350·y0..173) → 0(ord 145, 188,787 px, x0..799·y0..458)으로 **화면 왼쪽 위에서 대각으로 자라고**, 카메라가 (0,54)에 멈춘 ord 145~221 동안 ≈189,0xx로 평탄하며, 복귀(카메라 x 8 이상) ord 222~228에서 0으로 내려간다. ord 145..163 공통 stale 188,707 px.
- 평탄 구간에서 `hd_mask_inside_diff_subpixels`가 ≈105k → ≈56k로 줄고 `nearest_matches`가 늘어난다(후보 화면이 Scale2x 기준과 덜 다르게 됨 = 맵 밖 단색 영역 추정, 미확인). `layer_move_unsupported` 0.
- 끝 계수(save000 k4 vs save006 k1): `rect_fill_466070_reject_size` **40** vs 7, `shade_468870_reject_bounds` **843** vs 51, `shade_4687F0_reject_bounds` 2 vs 0. 그 밖 reject는 save000이 더 적다. present별 계수는 trace에 없다(metrics 1행).

**가설 H-D2k-s0:** 카메라가 맵 왼쪽 경계에 닿을 때 게임이 맵 밖 영역을 칠하는 호출이 mirror에서 거부되거나 hook 밖이라 HD 화면이 갱신되지 않고, 카메라가 멈추면 다시 그려지지 않아 평탄 stale로 남는다. 1순위 = `0x466070` 큰 사각형 fill의 size reject(폭 > `G1_OVERLAY_MAX_WIDTH` 또는 높이 > `G1_OVERLAY_MAX_HEIGHT`), 2순위 = `0x468870` shade bounds reject, 3순위 = 미후킹 writer.

**S-0 디스크:** 현재 여유 123 GiB. 회차 중 10 GiB 밑이면 lap1089 D-0 절차로 처리한다.

**S-1 귀속(필수, 2 run, 순차, load ≤ 8, run마다 `game` 사본 삭제):** lap1083 `run_k.sh`의 k4 옵션 그대로(`--hd-source scale2x --fixture save000 --scene-actions none --terrain-scroll --terrain-scroll-edge --terrain-scroll-keys UPLEFT,DOWNRIGHT`)에 `--stale-mask 130-232 --layer-drift --screen-watch --drift-samples "100,60;400,230;50,300"`(세 점 모두 k4 ord 145..163 공통 stale 안, 직접 확인)을 더한다. 이름 s1·s2.
- 필요하면 진단만 추가한다: `0x466070`·`0x468870`의 reject 호출을 `layer_drift.jsonl` `w` 기록(f·p·x·y·w·h·why)으로 남기는 env 게이트 진단(기본 off, 기존 `--blend-size-reject-diag`와 같은 방식, 테스트 +1, 기존 단언 불변). 제품 동작은 바꾸지 않는다.
- 측정: 표본 세 점이 처음 stale이 되는 present(`s` scr≠snap)와 그 present의 watch 쓰기 EIP·값·스레드, 같은 present의 `w` reject 기록(f·사각형이 표본을 덮는지), ord 136..230 stale 열, 끝 계수, k4와의 stale 열 일치(재현), 안전 7종·cleanup·source_unchanged·p95.
- **귀속 PASS:** s1·s2 모두 표본 ≥ 2/3의 첫 stale present에 표본을 덮는 reject 기록(같은 함수)이 있거나, 표본 첫 stale 쓰기 EIP가 한 미후킹 함수로 모인다. **UNKNOWN:** 둘 다 아님 → 표본 좌표·watch 범위와 함께 기록하고 수리하지 않는다. **무효:** stale 열이 k4와 다르게 평탄 구간이 없으면(재현 실패) 원인 기록.

**S-2 조건부 수리(S-1 귀속이 `0x466070` size reject일 때만, 같은 회차):** H-W330과 같은 방식으로 `0x466070` fill mirror를 overlay 상한 이하 타일로 나눠 처리한다(C 모델 테스트로 타일 경계·클립 확인 RED→GREEN). 다른 함수로 귀속되면 수리 없이 기록하고 다음 middle이 정한다.
- 수리 검증: S-1 옵션(진단 없음) save000 2 run + save006 k1 옵션 비회귀 1 run.
- **PASS(partial):** save000 2/2에서 ord 145~221 stale 합이 수리 전의 5% 이하(≈189k × 77 present 기준), `rect_fill_466070_reject_size` 감소, 새 reject 급증 0, save006 비회귀(hold 합·고정 합이 lap1085/1089 td 수준 이하, 안전 0). 공통 FAIL: 안전 위반·크래시·p95 > 고정+16.
- 바꾼 source가 있으면 lint·typecheck 뒤 기록 freeze 후 `make check` 1회.

그다음 후보(middle이 정함): HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: H-UL(위 §3), ord 137 2 px, ord 352/353 일시 사건, throttle 전용 ord 123 writer, `0x467E60` wrap 계수, lane 위상 경합(§2-2 공변량 추가), 진단 동반 영역(ord 219·243·296~318).

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`와 focused 테스트(`test_g1_saved_scene_probe`·`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`)를 돌린다. 결과는 STATUS에만 보강한다.
- 전체 `make check`는 SKIP한다. 문서만 변경했고 source·하네스·테스트는 lap1091 full PASS 1688 때와 같다.

## 다음 한 가지

work(Sonnet): §4 H-D2k-s0 S-1(save000 진단 2 run) → 귀속이 `0x466070` size reject면 S-2 수리·검증. G7은 사용자 재시험 대기(APPROVALS lap1093, 비차단), root 전달은 `loop/ESCALATE_SOL`.
