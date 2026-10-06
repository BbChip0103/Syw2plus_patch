# 2026-10-07 | lap1084 | G1 middle — H-D2k·D-0 독립 검수 + H-W330 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1083 work `loop/ESCALATE_SOL`(SHA256 `02a6eb2144c833b9a789a770a803ee60533c7fd7e41b7a7a876ef2f72678817c`, 원문은 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1082 §5 — D-0(종료 prefix archive·restore 검증 뒤 회수, 여유 ≥ 20 GiB), H-D2k(모서리 edge 스크롤 E-0~E-2).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만). fixture: 비합성 save006·save000. lap1083 산출물만 읽음.
- 검수한 source 해시 접두: `tools/inmm_stub/g1_mirror2x.c` `fd66ba276ced9cef`(lap1082 검수 값과 같음, 제품 C 불변), `g1_overlay_blt.h` `39e6e2e1227dc70f`, `tools/g1_saved_scene_probe.py` `1fa1e665605b43f9`, `tests/test_g1_saved_scene_probe.py` `9ee0fd6fcade4977`(work 기록과 일치). k1·k6 `bridge/supply_bridge_build.json`의 stub 입력 56개 SHA256이 현재 트리와 모두 같다(불일치 0) → **현재 트리 = k run bridge**.

## 1. 독립 재계산(work `analyze_hk.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1084_middle_review/`:
`recalc_lap1084.py` `965d8c9c…3aba`(새 스크립트. 카메라 관측열 변화·칸당 이동 분포, layer_drift `p`→ps3 순번 대응(tick 시계 대조), reject 사각형 ∩ stale mask 포함 검사 추가) → `recalc_lap1084.json` `6cb8eecd…2d7b`, 표준 출력 `recalc_out.txt` `c2b724f2…e735`.
pair-result SHA 접두 5개는 ESCALATE 기재와 같다. **k6만 전사 오류**다: 기재 `368525917417`, 실제 `3685259174f001b6…`(아래 정정 1). stale_mask SHA는 6/6이 pair-result 기재 값과 같고, mask와 trace `stale_pixels` 불일치는 0이다. 기준: lap1081 hl3(save006 LEFT,RIGHT edge)·hl4(UP,DOWN edge)·hl5(save000 키 hold)·hl6(고정). hold 창 정의는 lap1072~1082와 같다(`down_input_tick`..`final_observation_tick`).

| 항목 | 사전등록(lap1082 §5) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| E-0 k1·k2·k6 | 두 lane 같은 칸·왕복 | UPLEFT 24칸 (158,101)→(110,101), 칸당 (−2,0)×24 / DOWNRIGHT (+2,0)×24 복귀, 두 lane 관측열 SHA 같음, 최종 (158,101) | 동일 | 일치 PASS |
| E-0 k3 | 같음 | UPRIGHT (0,−2)×24 (158,101)→(158,53)·DOWNLEFT 복귀 | 동일 | 일치 PASS |
| E-0 k5 | = hl3 | LEFT (−1,+1)×24·RIGHT 복귀, 관측열 SHA = hl3 | 동일 | 일치 PASS |
| E-0 k4 | clamp 기록 | UPLEFT 20칸 = (−2,0)×19 + (−1,+1)×1 → (39,53)→(0,54), `scroll_corner_clamp_free` false, DOWNRIGHT (+2,0)×24 → (48,54). 두 lane 같음 | 20칸·x=0·(48,54) | 일치 |
| E-1 | elapsed p95 ≤ 고정+16·tps ≈ 20 | hold elapsed p95 k1 7·k2 8·k3 7·k4 8·k5 7·k6 11(고정 8/7/8/7/7/10), tps 19.97~20.02, 간격 p95 52~56 | 동일 | 일치 PASS |
| E-2 k1·k2 | hold 합 0 | **240,703/240,703**, stale 열 SHA 같음(`17cd2063ae5f`), 비0 ord 126~133·137·140~145·221~225, 마지막40 0, 총합 532,085 = 고정 기준 291,382 + hold | 동일 | 일치 **FAIL** |
| E-2 k6 | 진단 | 241,094 = k1 + ord 147 158 + 219 233(진단 run만), 그 밖 ord 296·307·316~318도 진단 run만(hold 밖) | 241,094/22 | 일치 |
| E-2 k3·k5 | 0 | 0/0, 마지막40 0. k3은 hold 밖 ord 353 257 px 1회(tick 24923, 마지막40 밖) | 0/0 | 일치 PASS(관찰 추가) |
| E-2 k4 | 0 | 15,459,820·마지막40 51,680. 서술은 다름(정정 2) | 동일 수치 | 수치 일치 |
| 계수 | 새 reject 급증 없음 | `blend_467580_reject_size` k1·k2·k6 21 / k3·k5·hl3·hl4·hl6 16 / k4·hl5 0, `blend_467B00_reject_size` k1·k2·k6 89 / 나머지 0. `rect_fill_466070_reject_size` k4 40(save006 7~12, hl5 0) | 동일(466070은 미분류) | 일치 |
| 공통 | 안전 0·cleanup·source_unchanged | 6 run 안전 7종 최대 0, 12 lane `game_removed`·`cleanup.ok`·`source_unchanged` true, 원본 SHA 접두 `b56986e018b4` | 동일 | 일치 PASS |

**k6 귀속(독립):** layer_drift `p`는 ps3 순번과 같다(435 present 대응, 시계 차 최대 28 ms, 오프셋 0). `w` 기록의 `reject_size`는 **17건, 전부 330×200**이다: `467B00` 12(p126~129·141~144·222~225), `467580` 5(p130~133·140). clip 뒤 폭은 330(x=473만 327)으로 모두 320을 넘는다. 같은 present의 reject 사각형(화면 교집합) 안에 든 stale은 126~133·140~144·222~225에서 **100%**다. 인접 present 2개(145 2,421 px ⊂ p144 사각형, 221 2,304 px ⊂ p222 사각형)도 사각형 안이다. hold 창 stale 합집합 117,601 px 중 117,599 px가 reject 사각형 합집합 안에 있다. 밖의 2 px는 ord 137 (799,408..409)뿐이다. 표본 10/10은 마지막 writer `0x467CCF` 6·`0x467692` 4, tid 280, `val==scr` 10/10이고, 바로 앞 쓰기는 `0x4662DE`(snapshot 값)다. 코드: `mirror_blend_wrle`는 클립 뒤 `(x1−x0) > 320 || (y1−y0) > 160`이면 reject_size(4213행 부근)이고, `mirror_blend_clip`은 높이 band는 있으나 `(x1−x0) > 320`이면 reject_size다. work 귀속과 일치한다.

**D-0(독립):** `report.json` SHA `687a88ff…2e70`·`plan.json` `50012adc…1c92`·`archive.py` `08bf53e3…d660`이 기재와 같다. 31 항목 모두 `prefix` 부재, 같은 run의 `manifest.json` 존재, archive·json 존재(불일치 0). archive SHA를 첫·마지막 항목에서 다시 계산했고 기재와 같다. `restore_verification_000/010/020/030.json` 4개 모두 `full_content_metadata_match` true(각 1,069 entries). 보고 여유는 6.77→22.43 GB(= 6.30→20.89 GiB)다. **현재 여유는 12 GiB**다. k1~k6 run dir가 1.2~1.4 GiB씩 남아 있다(prefix 보존 상태). 다음 work는 20 GiB 미만에서 시작하므로 D-0를 다시 해야 한다.

## 2. 하네스 검토(`tools/g1_saved_scene_probe.py` 모서리 키)

- `_scroll_edge_point`: 모서리는 창 꼭짓점(오른쪽·아래쪽은 `800s−1`·`600s−1`)이고, release는 중앙이다. 기존 4방향 분기는 그대로다.
- `_scroll_edge_option_error`·`_scroll_edge_keys`: 반대 모서리 쌍 4종만 받고, 다른 조합(예: `UPLEFT,LEFT`)은 ValueError다. `_parse_scroll_keys`(키보드 hold)는 모서리 키를 계속 거부한다.
- `_scroll_camera_steps`: 부호가 0인 축은 검사하지 않고, 이동 칸 = `|d| // |sign|`다. `_scroll_corner_clamp_free`: 부호 0 축의 이동이 0일 때만 true다. k4(dx −39, dy +1)에서 false로 clamp를 올바르게 표시했다.
- 결함은 없다. 관찰(비차단): 홀수 이동은 나눗셈에서 내림 처리된다(k4 dx −39 → 19). 관측 변화 횟수(20)와 1 차이가 나지만 판정에는 쓰지 않는다.
- 테스트는 §6 focused로 확인한다.

## 3. 정정·관찰

1. **k6 pair-result SHA 전사 오류:** ESCALATE와 work 기록 표의 `368525917417`은 실제 `3685259174f0…`(전체 `3685259174f001b6bd…`, `sha256sum` 직접 계산)의 잘린 전사 오류다. 다른 다섯 개와 mask·trace SHA는 일치하고 내용은 k6 진단 run 그대로다. 기록만 바로잡는다.
2. **k4(save000) stale 서술:** work는 "clamp 뒤 ≈189k가 마지막40까지 남는다"고 했다. raw는 다르다:
   - (i) stale은 clamp 전인 ord 138(tick 50730, 카메라 (11,53))에서 시작한다. ord 145~221에서 ≈189k로 평탄하고(mask bbox x0..799·y0..458), DOWNRIGHT 복귀 중 ord 222~228(카메라 x ≈ 14 이상)에서 0으로 내려간다.
   - (ii) 마지막40(ord 261~300) 51,680은 다른 꼬리다. ord 261~275는 3,589→847로 감쇠하고, ord 290~300은 309→2,965로 **증가 중에** run이 끝난다(save000 ps3 301개).
   - 즉 평탄 구간은 "카메라 x ≲ 12, 맵 왼쪽 경계가 화면에 들어온 구간"과 겹친다. clamp 자체와는 맞지 않는다. 귀속은 UNKNOWN이다. `blend_*_reject_size`는 0이고, `rect_fill_466070_reject_size`가 40(save006 run 7~12)인 것이 다음 진단의 첫 후보다(미검증).
3. **고정 장면 `blend_467580_reject_size` 16:** k3·k5와 lap1081 hl3·hl4·hl6에 공통으로 있다. 고정 장면 로드 과도 stale(ord 6..299, 총합 291,382)과 관련이 있는지는 미측정이다. H-W330 뒤 그 총합이 변하면 함께 기록한다.
4. ord 137 (799,408..409) 2 px는 k1·k2·k6 공통이고 reject 사각형 밖이다. writer는 미귀속이며 별도 소잔여로 둔다.

## 4. 판정

- **D-0 PASS 수용.**
- **H-D2k:** save006 UPRIGHT,DOWNLEFT·LEFT,RIGHT는 E-0~E-2 PASS(비회귀)다. save006 UPLEFT,DOWNRIGHT는 **E-2 FAIL(귀속 완료: `0x467580`·`0x467B00` 330×200 reject_size)**이다. save000 UPLEFT,DOWNRIGHT는 **E-2 FAIL(귀속 UNKNOWN, 정정 2)**이다.
- 사전등록상 H-D2k는 PASS(partial)가 아니다. 이것을 **FAIL(귀속) 수용**으로 기록한다.
- 하네스 K-0 결함은 없다. 정정 1~2는 비차단이다. 제품 G1 마감이나 사용자 승인이 아니다.

## 5. 다음 work 사전등록(Sonnet) — D-0′ 디스크 → H-W330

**D-0′ (필수 선행):** 현재 여유는 12 GiB다. lap1083 D-0와 같은 절차로 여유 ≥ 20 GiB를 만든 뒤에만 게임을 실행한다.
- `local/maintenance/20261007_lap1083_prefix_archive/archive.py`를 새 디렉터리 `local/maintenance/<KST날짜>_lap<N>_prefix_archive/`에 **복사**해 쓴다.
- 대상: lap1083 plan의 미처리 `lap1057`~`lap1079` 종료 prefix를 오름차순으로 처리한다. lap1081·lap1083 run은 마지막 후보다.
- 조건(종료·cleanup·`source_unchanged`·참조 0·전 멤버 대조·batch마다 실제 full restore)과 `prefix`만 삭제하는 규칙은 같다. 미달이면 BLOCKED로 기록하고 실행하지 않는다.

**H-W330 가설:** `mirror_blend_wrle`(`0x467580`)·`mirror_blend_clip`(`0x467B00`)이 클립 뒤 폭 > 320(실측 330×200)을 reject_size로 버린다. 이 때문에 save006 UPLEFT,DOWNRIGHT hold 창 stale 240,703이 생긴다. 두 hook이 이 영역을 미러하면 그 stale은 0이 된다.

**W-0 구현(테스트 먼저 RED→GREEN):** 이미 검증된 tiled 경로를 재사용한다. **공유 상수 `G1_OVERLAY_MAX_WIDTH`/`HEIGHT`·scratch 크기는 바꾸지 않는다.**
- 두 hook의 before 버퍼를 `G1_OVERLAY_SCREEN_WIDTH × G1_OVERLAY_SCREEN_HEIGHT`로 바꾸고, hook별 tile 버퍼(`MAX_WIDTH × MAX_HEIGHT`)를 둔다.
- 적용은 `g1_overlay_blt_apply_tiled`로 한다(H-D2t·H-LB `mirror_rect_border`·H-L2 `mirror_flip_blend7`와 같은 패턴).
- 크기 검사 분기(`> MAX_WIDTH`/`> MAX_HEIGHT`)는 제거한다. 화면 교집합 [x0,x1)×[y0,y1) 계산·대상 검사·guard·`layer_drift_write_*`·원본 1회 호출·인자 전달은 그대로 둔다.
- 기존 계수 이름(`blend_467580_*`·`blend_467B00_*`)은 유지한다. `blend_467B00_band_calls`는 "타일 > 1 호출"로 뜻을 명시해 유지하거나, 새 `*_tile_calls`를 추가한다(택1, 테스트·기록에 명시).
- 테스트:
  - (a) 330×200을 (34,−126)·(473,98)·(9,294)에 두는 경우와 800×600 전체에서, tiled 결과 = 전체 프레임 Scale2x 기준이고 reject 0이다.
  - (b) hook 계약: tiled 호출, before 버퍼 크기, 원본 정확히 1회, 계수, bridge 문자열을 확인한다.
  - (c) 기존 `test_g1_rect_fill.py`의 `g_blend_wrle_before`/`g_blend_clip_before` 관련 단언은 의도에 맞게 갱신한다. 완화가 아니라 새 계약으로 바꾸고, 바꾼 단언 목록을 기록한다.
- `0x467580`은 클립이 없다. 화면 밖·stride 패딩 쓰기는 지금처럼 미러하지 않는다(새 범위 확장 금지).

**W-1 실행(순차, load ≤ 8, run마다 game 사본 삭제, launch 전 여유 ≥ 10 GiB):**
- w1·w2: save006 `--terrain-scroll-edge --terrain-scroll-keys UPLEFT,DOWNRIGHT`(= k1 옵션)
- w3: save006 `UPRIGHT,DOWNLEFT`(= k3)
- w4: save006 `LEFT,RIGHT` edge(= k5/hl3)
- w5: save006 고정(= hl6)
- stale mask는 hold 창(ord 120..300) 범위로 둔다.

**PASS / FAIL(사전등록):**
- **PASS(partial):** 아래를 모두 만족해야 한다.
  - w1·w2: ord 126~133·140~145·221~225 = 0/0, `blend_467580_reject_size` = `blend_467B00_reject_size` = 0.
  - w1·w2 hold 합: 0이거나, 남은 것이 ord 137 (799,408..409) ≤ 2 px뿐이어야 한다(§3-4 기존 소잔여). 그 밖 ord 증가는 0이어야 한다.
  - w1·w2: 마지막40 0, E-0 24칸 왕복 (158,101), E-1 elapsed p95 ≤ 고정+16·tps ≈ 20.
  - w3·w4: hold 0.
  - w5: 300..848 0, 고정 총합 ≤ 291,382. 줄면 값을 기록한다(§3-3).
  - 전 run: 안전 7종 0·cleanup·`source_unchanged`, `blend_*_mirrored_calls` 이상 감소 없음.
- **FAIL:**
  - w1·w2에서 reject 사각형 위치에 stale이 남으면 FAIL이다. 이때 같은 옵션 `--stale-mask <ord> --layer-drift --screen-watch` 진단을 1회 하고 귀속한다.
  - 안전 위반·크래시·성능 초과는 FAIL이다.
  - 실패 가설 2회면 BLOCKED다.
- 변경은 uncommitted로 두고, `make check`(lint·typecheck 먼저)를 기록 freeze 뒤 1회 돌린다.

**선택(시간 여유 시, 판정 분리):** H-D2k-s0 — save000 `UPLEFT,DOWNRIGHT` + `--stale-mask 140-221 --layer-drift --screen-watch` 진단 1회로 평탄 구간 ≈189k의 writer를 귀속한다(첫 후보 `rect_fill_466070` reject_size 40). 이것은 H-W330 판정에 넣지 않는다.

그다음 후보: save000 맵 경계 stale 수리(H-D2k-s0 귀속 뒤), HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: ord 137 2 px·throttle 전용 ord 123 writer 귀속, `0x467E60` wrap 계수, lane 위상 경합, lap1069 s2 117 px, 진단 동반 영역(k6 ord 147·219·296~318 포함), save000 overlay BltFast rejects, 다중 팝업 heal, lap1072 c·f·lap1056 r1 UNKNOWN.

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT와 focused 테스트(`test_g1_saved_scene_probe`·`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`)를 돌린다. 결과는 STATUS에만 보강한다.
- 전체 `make check`는 SKIP한다. 문서만 변경했고 source·하네스는 lap1083 그대로이며, lap1083 full PASS 1667이 있다. 다음 work가 변경 뒤 실행한다.

## 다음 한 가지

work(Sonnet): §5 D-0′(여유 ≥ 20 GiB) → H-W330 W-0 → W-1. G6/G7은 사용자 합격(APPROVALS lap989) 대기이며 루프를 막지 않는다.

## 부록: lap1083 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1083 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — D-0 디스크 회수 PASS + H-D2k(모서리 edge 스크롤) 실행·귀속 완료. work는 자기 결과를 승인하지 않으며 fresh Opus middle 독립 재계산과 수용·다음 work 사전등록(H-W330)이 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1083_work_hd2k 의 {k1..k6}/pair-result.json·candidate/trace_raw.jsonl·stale_mask.bin·(k6) layer_drift.jsonl·screen_watch.jsonl 을 work 스크립트(analyze_hk.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: k1 1739380b5cb6 k2 68b4b3909be7 k3 22d230b9b2cf k4 3856677be41d k5 5253bd49d2ff k6 368525917417. 기준: lap1081 hl3(save006 LEFT,RIGHT edge hold 0)·hl4.
2. 검증 항목: (a) E-0: k1·k2·k6 UPLEFT 24칸 (158,101)→(110,101)·DOWNRIGHT 복귀, k3 UPRIGHT (158,101)→(158,53)·DOWNLEFT 복귀, k5 LEFT,RIGHT 24칸 (134,125) 왕복, 두 lane 같음. (b) E-2: k1·k2 hold 창(ord 123..291) stale 합 240,703 동일·ord 126~133·137·140~145·221~225, k3·k5 0. (c) k6 귀속: layer_drift reject_size 17건 전부 w=330·h=200이고 stale present 집합 ⊇ 그 17 present, 표본 10/10 val==scr·writer 0x467CCF(∈0x467B00)/0x467692(∈0x467580). 계수 blend_467580_reject_size k1·k2·k6 21(k3·k5 16)·blend_467B00_reject_size 89(k3·k5 0). 코드: tools/inmm_stub/g1_mirror2x.c mirror_blend_wrle(0x467580)의 (x1-x0)>320||(y1-y0)>160 reject_size, mirror_blend_clip(0x467B00)의 x1-x0>320 reject_size 가 330 폭을 거절하는지. (d) k4 save000 UPLEFT: clamp(20칸·x=0)·최종 (48,54)·hold 합 15,459,820·마지막40 51,680, reject_size 계수 0 → 별개 원인 UNKNOWN. (e) 하네스: tools/g1_saved_scene_probe.py 모서리 키 변경(_EDGE_DIAGONAL_SIGNS·_scroll_edge_point·SCROLL_CAMERA_SIGNS_EDGE·_scroll_camera_steps 나눗셈·_scroll_corner_clamp_free)과 tests 4 추가 검토. (f) D-0: local/maintenance/20261007_lap1083_prefix_archive/ (report.json 687a88ff…, restore_verification_000/010/020/030.json, 31 archive) — prefix만 삭제·manifest/output/로그 보존 확인, 여유 20.89 GiB(현재 ≈13 GiB: k1..k6 prefix 6개 약 7.8 GiB 사용).
3. 수용 시 다음 work 사전등록 후보: H-W330(두 hook의 폭>320 reject 해소 — 폭 band 또는 G1_OVERLAY_MAX_WIDTH 확장, C 모델 테스트, k1 옵션 2회 hold 0), save000 UPLEFT clamp 뒤 stale ≈189k writer 귀속 진단 1회. 디스크 여유 부족 시 D-0 같은 절차 재실행(archive.py 복사본 사용, 대상 lap1056 이후).
기록 docs/history/laps/20261007_lap1083_work_g1_hd2k_corner_edge_scroll_330x200_blend_reject_size.md. 변경(uncommitted): tools/g1_saved_scene_probe.py·tests/test_g1_saved_scene_probe.py. 제품 C/bridge 불변. 원본 EXE b56986e0…08a8ac 불변.
```
