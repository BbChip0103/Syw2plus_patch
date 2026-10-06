# 2026-10-05 | lap1018 | G1 H-B `0x467580` 가중 반투명 RLE diff 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 자기 결과를 승인하지 않는다(독립 검수는 다음 middle).
- 가설 / 사용자 관찰: lap1017 middle 사전등록 — save000 B 사각형(및 구름 계열)의 stale writer는 미후킹 `0x467580`이다. H-L(`mirror_blend_rle`) 동형 diff 미러를 붙이면 B 표본 stale present가 0이 되고 전체 stale 마지막 40 중앙값(7,694.5)이 ≥50% 감소한다.
- 예상 PASS / FAIL 조건(lap1017 §4): B-0 유효(scene 동일·안전 7종 0·cleanup·source_unchanged·loaded PNG 비단색), **B-1** 표본 `cov==1 && scr≠snap` present 수 B 0 = PASS·stale ≥50% 감소 = PASS, 일부면 PASS(partial) + 남은 사각형 지목, B-2 계수 `invocations>0`·`reject_target` 0, B-3 save006 39프레임(또는 공통 38프레임 성분 D 24) 교집합 비회귀·신규 0·p95 ≤8ms·cov p50 ≥99%, B-4 save000 p95 ≤10ms·안전 0·크래시 0.
- 변경 파일 / source fingerprint / 커밋: **uncommitted**, 파일 SHA256(앞 16자) — `tools/inmm_stub/g1_mirror2x.c` `6932c3ac812c48b9`, `g1_mirror2x.h` `0a500cbfb3b2baf0`, `direct_draw_trace.c` `49e385b045ab8e76`, `tests/test_g1_rect_fill.py` `c4468fde2585bd8f`.
  - `g1_mirror2x.c`: hook `G1_BLEND_WRLE 0x00467580`(old bytes `51 0F BF 54 24 0C`, 6 B, 불일치면 설치 거부·원복), wrapper `mirror_blend_wrle`(H-L 동형: 인자 하위 16비트 부호확장·renderer `0xE5BF18`+화면 buffer 한정·전용 before 버퍼 `g_blend_wrle_before`·원본 호출 뒤 `g1_overlay_blt_apply` scale2x), 계수 9개 `blend_467580_{invocations,mirrored_calls,mirrored_pixels,changed_calls,clipped_calls,reject_target,reject_bounds,reject_size,reject_guard}`(사전등록 8개 + `clipped_calls` 1), install/detach/`primitives_installed` 연동.
  - **v2 변형(사전등록 허용 "부분 화면 밖 변형")**: v1(전체 사각형이 화면 안일 때만 미러)에서 save000 `reject_bounds` 921(호출의 ~26%)이 나와, 화면 교집합만 before/diff하도록 바꿨다(원본은 전체 사각형으로 그대로 호출, wrapper는 교집합 밖을 읽지 않음, 교집합 밖 wrap 쓰기는 미추적). `clipped_calls`가 부분 호출 수. 교집합이 비면 `reject_bounds`, 교집합이 320×128 초과면 `reject_size`.
  - `g1_mirror2x.h`·`direct_draw_trace.c`(metrics JSON 9개 키).
  - 테스트: `test_blend_weighted_rle_hook_table_and_wrapper_contract`(주소·old bytes·`ret 0x14` 주석·16비트 부호확장·before<original<apply 순서·H-L before 버퍼 비공유·교집합 계수·계수 이름/getter/metrics) RED(KeyError/AssertionError)→GREEN, 신규 변형도 RED→GREEN. `make lint`·`make typecheck` PASS(실행 후 최종 재확인 아래).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE `b56986e0…08a8ac`(`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`, `0x467580` 프롤로그 objdump로 `51 0F BF 54 24 0C`·인자 x·y·width·height·rle 재확인, read-only). 격리 Wine prefix/display/game 사본, 두 lane(baseline 원본/candidate). save000 `1c703551…19da`(index 1) = fixture, save006 `616b7997…a064` = 비회귀 fixture. 활성8인 부하 증명 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 공유 temp `20261005_lap1018_work_hb/`(`run.sh` `09573fb7…`, `run_v2.sh` `385f6f51…`), 모두 순차·exit 2(= 기존 pair HOLD: save000은 non-loaded capture tag BLOCKED(`--scene-actions none`), save006은 V2s production raw 기존 gate). 각 run game 사본은 프로브 cleanup으로 삭제(`cleanup.ok` true), prefix·로그·output 보존, 디스크 43G 여유.
  - v1(전체 안쪽만): `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1018_hb_s0_r{1,2} --artifact-root …/s0_r{1,2} --hd-source scale2x --fixture save000 --scene-actions none --performance-window --layer-drift`, save006 `…lap1018_hb_s6_r{1,2}` `--stale-mask 6-12,30-34,300-301,585-620,880`. 로그 `logs/gates/lap1018_hb_{s0,s6}_r{1,2}.log` SHA `f57dbaaf…`·`e8788c38…`·`e0f5110c…`·`9e5f36ca…`, pair-result `334a81f2…`·`afc77da3…`·`fc7d2afa…`·`492199cf…`.
  - v2(교집합): 동일 인자, `lap1018_hb2_*`·artifact `v2_s0_r{1,2}`·`v2_s6_r{1,2}`. 로그 `logs/gates/lap1018_hb2_{s0,s6}_r{1,2}.log` SHA `a438c743…`·`25808661…`·`44a7e60f…`·`2c90fff1…`, pair-result `2f5f6517…`·`7a103f4f…`·`c0cc3961…`·`4da0d619…`.
  - 추가: save000 `--stale-mask` run(`v2_s0_mask`, 로그 `8085da01…`)은 save000 경로에서 `stale_mask.bin`이 생성되지 않아 사용 불가(exit 2, 증거 0 — 잔여 위치 지목은 못 함).
  - 분석 `analyze_hb.py`(`f58e16e6…`)·`ff.py`(`22e99dbd…`)·`analyze_hb_s6.py`(`50580213…`)→`analysis_hb_v1.json`(`ee86bf4d…`)·`analysis_hb_v2.json`(`62133193…`)·`analysis_hb_s6.json`(`8fd907ed…`)·`analysis_hb_s6_v2.json`(`1a262226…`). `ff.py`는 layer_drift 표본을 present별 forward-fill해 lap1016 r1/r2에서 41/178/210을 재현한 같은 방법(lap1016 기록 41/180/210과 B만 2 차이)이다.
- 측정값 / 판정:

| 항목 | lap1016 기준(H-L) | v1 r1/r2 | **v2 r1/r2** |
|---|---|---|---|
| save000 stale 마지막40 중앙값 | 7,694.5 | 452.5/452.5 | **424.5/424.5**(−94.5%) |
| 표본 stale present A | 41 | 41 | 41 |
| 표본 stale present B | 178(기록 180) | 135 | **135** |
| 표본 stale present C | 210 | 210 | 210 |
| `blend_467580` invocations / mirrored | — | 3583·3589 / 2634·2638 | 3583·3589 / **3555·3561** |
| `reject_bounds` / `reject_size` / `clipped` | — | 921·923 / 28 | 0 / 28 / 921·923 |
| `reject_target`·`reject_guard` | — | 0·0 | 0·0 |
| p95 present (cand) | 7 | 7/6 | 6/7 |
| 안전 7종·cleanup·source_unchanged | 0·ok | 0·ok | 0·ok(4/4) |
| scene_state_equal / loaded PNG 색 | true / 226 | true / 226 | true / 221·226 |
| `blend_4672E0`(H-L) | — | 411 invocations 전부 mirrored | 동일 |

  - **B-0 PASS**. **B-1: PASS(partial)** — 전체 stale ≥50% 감소는 충족(−94.5%), 그러나 **B 표본은 0이 아니라 135**(178에서 −24%), A 41·C 210은 변화 없음. 즉 `0x467580`이 save000 stale 면적의 대부분(7,270 px)을 만들었지만, **세 표본 점의 램프 writer는 `0x467580`이 아니다**(v2에서 호출의 99.2%가 미러되는데도 동일). 후보: `0x467410`(`ret 0x1C`)·`0x4676D0` 형제 또는 다른 미후킹 writer(B 일부·A·C). 표본 3점 `max_snl`(B 6,702·C 159·A 4)·`max_stale`(layer vs cache) 0·`unc` 0은 lap1016과 동일.
  - **B-2 PASS**: invocations > 0, `reject_target` 0, `reject_size` 28(교집합 > 320×128인 큰 호출 — 사각형 교차는 미측정), v2 `reject_bounds` 0.
  - **B-3 save006 PASS**(v1·v2 각 2회): lap1000 H-L r1/r2/r3 대비 공통 38프레임 교집합 = 성분 D 24(`y515..520×x616..619`) = 기준 동일, 신규 stale 0·제거 0, p50 5·p95 7·max 11/14/12, cov p50 99.30%, 안전 0, V1/V2/V2q/Scale2x/input/minimap PASS, V2s production raw FAIL(기존 gate, 변경 없음). save006에서 `0x467580`은 invocations 16·전부 `reject_size`(미러 0, 영향 없음).
  - **B-4 PASS**: save000 candidate p95 6~7ms(≤10)·`performance_comparison` PASS(v1 r1/r2 ticks 비 1.000005/1.000001, v2 r1/r2 1.000001/0.999976; ≥0.95)·안전 0·크래시 0.
  - 분기 판정: 지시서의 "B가 남으면 hook 설치·호출 경로 의심" → hook은 호출 수(3583)와 mirrored(3555)로 **정상 동작이 확인**돼 설치/호출 경로 의심은 배제(전체 stale 94.5% 감소가 hook 효과의 증거). 남은 stale는 별도 writer.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 교집합 밖 wrap 쓰기 미추적(원본이 비클립이라 x<0이면 앞 행 끝을 쓸 수 있음; 잔여 424 px에 그 몫이 있는지는 UNKNOWN). 잔여 424.5 px의 위치는 save000 stale mask 부재로 UNKNOWN. 표본 A/C가 `0x467580` 비소속이면 lap1017 §3.1 "C 긴장"은 해소되지 않았다. 독립 검수 미실시, 사용자 승인 아님, 기술 부분 결과일 뿐.
- 다음 한 가지(work→middle 제안): middle이 raw를 새 스크립트로 재계산한 뒤, 잔여(전체 424.5 px, 표본 A 41·B 135·C 210 present)의 writer를 좁힌다 — (a) 원본 lane census watch를 candidate 램프 시각에 맞춰 A(112,126)·C(302,9)에 걸거나(skip 100~150, `--census-watch-presents`), (b) 호출 수 기준으로 형제 `0x467410`·`0x4676D0` 후킹 여부를 정적으로 결정, (c) save000 stale mask 경로 확보(하네스: `--stale-mask`가 save000에서 파일을 못 만드는 원인). work는 가능성 판정 전 구현을 추측하지 않는다.
