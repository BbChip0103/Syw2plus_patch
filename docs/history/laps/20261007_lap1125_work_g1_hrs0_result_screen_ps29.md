# 2026-10-07 | lap 1125 | G1 work — H-RS0 결과 화면(PS29 "패배했습니다.") HD 측정 → FAIL(귀속)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무 구현·실행) 1 lap. 입력은 lap1124 middle 사전등록 `docs/history/laps/20261007_lap1124_middle_g1_hpm3_review_hrs0_preregistration.md` §4. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음, `loop/STOP` 없음.
- 가설 / 사용자 관찰: 결과 화면은 PS9·PS35처럼 전면 menu copy 경로로 그려져 PS29 HD ≥98.6%이다. 아니면 미러 밖 writer가 있어 귀속한다. 사용자 관찰 없음(기술·격리 측정).
- 예상 PASS / FAIL 조건(사전등록): PS29 present HD min ≥98.6%(첫 전환 present 1개는 공개만)·탭 전환 뒤 각 창 min ≥98.6%·확인 뒤 다음 상태 HD 비회귀(PS9이면 100)·V1/안전 7종/fallback/hresult 0·dropped 0·scale2x PASS·캡처 정상, 2/2. 미달 시 같은 회차 census 귀속·수리 없음.
- 변경 파일 / 커밋: 제품 C source 변경 0(이번 회차). 하네스 `tools/g1_saved_scene_probe.py`(SHA256 앞 16자 `b52c12d2d2c1bfa7`)·신규 `tests/test_g1_result_screen.py`(`843ab57aa00173d6`)·`tests/test_g1_new_game_path.py`·`tests/test_g1_census.py`·`tests/test_g1_saved_scene_probe.py`(소스 문자열 단언 5곳 갱신). 전부 uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE `b56986e0…` 프로브 `validate_original_source`·`source_unchanged` true(4 lane 모두). 후보 `_inmm.dll`은 프로브가 현 source로 빌드(제품 C 변경 0, lap1123 full check와 동일 C source). fixture `g7defeat` = lap982 H-G7o orig `save001.dat`(1,713,222 B, SHA256 `57872666b436a4620c21cc99ef7c22413809e49de80b401ae5f27aa2e14210b8`, 목록 index 2), 공유 temp `20261005_lap982_g7_hg7o/orig/save001.dat`에서 private game 사본으로만 복사, **참고 저장소에는 복사하지 않음**(확인: `Syw2plus_re/Syw2plus/save`에 save001.dat 없음). 활성 인원·군대 구성은 이 장면의 대상이 아니다(G7 원본 결함으로 만든 패배 화면, local 0 → ps 3→27→29, 컴퓨터 2명 표). 승리 화면은 별도 fixture 필요(UNKNOWN).

## RS0-0 하네스 (TDD: RED → GREEN)

- `SAVE_FIXTURES["g7defeat"]=("save001.dat", 57872666…, 2)`, `_fixture_path`(g7defeat은 env `SYW2_G7DEFEAT_FIXTURE` 또는 공유 temp 기본값, 참고 저장소 안이면 거부, save006/save000은 기존 `Syw2plus_re/Syw2plus/save/` 그대로), `_verify_fixture_file`(SHA 불일치·부재 시 `ProbeError`, 시작 거부), `_run_lane`은 `shutil.copy2(fixture_file, private_save)`로 private 사본에만 복사.
- `--result-screen`(`--fixture g7defeat --hd-source scale2x` 필수, census/new-game-path/terrain-scroll과 배타) → `_result_screen_window`: 로드 뒤 PS3/27/29 대기(60초) → `ps27`·`ps29`(dwell 6초) 창 → 탭 병사(500,57)·건물(606,57)·자원(713,57) 클릭(표시 전환만, 창당 3초) → 확인(712,561) → 다음 상태 창. PS29 미도달 시 `result_unreached` 캡처+states_seen 기록 FAIL, 확인이 PS29를 못 떠나면 FAIL. `_summarize_result_screen`: 창별 HD(`_summarize_play_presents` 재사용)·기준(PS29·탭 min ≥98.6, 첫 present 1개 공개 허용 / 확인 뒤 PS9는 ≥99.9 / 안전 카운터·fallback·V1 0). 후보 lane은 trace dropped 0 아니면 FAIL, mirror validator 필수 상태 (9,35,3,29).
- `--census-state 29`(census-only, g7defeat 로드 뒤 PS27/29 도달 허용) 추가 — C는 이미 `SYW2_G1_CENSUS_STATE`를 일반 상태로 읽는다.
- 테스트 RED(`KeyError: 'g7defeat'`) → GREEN: `tests/test_g1_result_screen.py` 14건, 관련 `test_g1_new_game_path/census/saved_scene_probe` 포함 273 passed. `make lint`·`make typecheck` PASS.

## RS0-1 격리 run (`--hd-source scale2x --fixture g7defeat --scene-actions none --result-screen`, 후보+baseline lane)

실행: `PYTHONPATH=. .venv/bin/python tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1125_hrs0_{a,b} --artifact-root ../temp/Syw2plus_patch/20261007_lap1125_work_hrs0/{a,b} …`(동기 실행, 로그 `logs/gates/lap1125-hrs0-{a,b}.log`·`.exit`=2(FAIL 판정 종료코드)). raw: 공유 temp `20261007_lap1125_work_hrs0/{a,b}/result-screen-result.json`(`87229984…`·`4054a569…`)·`candidate/trace_raw.jsonl`(`96f8e0cb…`·`88630c94…`)·캡처 `candidate/{ps29,result_tab_*,result_after_confirm}.png`. 요약 스크립트 `rs0_sum.py`(`1a325aeb…`).

| 창 | a presents / HD 첫·min·p50 / stale max / <98.6 | b presents / HD 첫·min·p50 / stale max / <98.6 |
|---|---|---|
| ps27(참고) | 1,174 / 80.754·80.754·80.754 / 92,383 / 전부 | 1,055 / 80.754·80.754·80.754 / 92,383 / 전부 |
| **ps29** | 417 / 99.925·**98.36**·98.36 / 7,874 / 326 | 404 / 99.955·**98.36**·98.36 / 7,874 / 311 |
| tab 병사 | 237 / 98.36·98.36·99.171 / 7,874 / 16 | 217 / 98.36·98.36·99.198 / 7,874 / 15 |
| tab 건물 | 237 / 99.171·99.171·99.171 / 3,980 / 0 | 230 / 99.171·99.171·99.171 / 3,980 / 0 |
| tab 자원 | 238 / 99.171·99.171·100 / 3,980 / 0 | 239 / 99.171·99.171·100 / 3,980 / 0 |
| 확인 뒤 PS9 | 272 / 100·100·100 / 0 / 0 | 275 / 100·100·100 / 0 / 0 |

- 두 run 공통: 상태 순서 `[3, 27, 29]`(baseline·candidate 모두 PS29 도달), 확인 클릭 뒤 candidate 다음 상태 9(baseline은 첫 폴에서 8을 읽음 = 전이 중 값 추정, 후보와 달라 보이는 것은 폴링 시점 차이로 UNKNOWN 공개), `trace_dropped_count` 0(2/2), V1 outside·안전 7종·fallback·success≠1 모두 0, `scale2x_validator` PASS, `mirror_validator` BLOCKED(nearest oracle 장면 불일치, 기존·게이트 아님), 캡처 정상(1600×1200 UI·표·탭·확인 버튼·"패배했습니다." 확인, 확대 화질 차이는 허용).
- **판정: H-RS0 `FAIL`(2/2 일관).** PS29 HD min 98.36% < 98.6%(`ps29_hd`·`tab_soldiers_hd` False). 첫 전환 present는 99.9%대로 높고, **stale이 매 present 정확히 +72 px씩 선형 증가해 7,874에서 정체**(약 110 present, a·b 동일 값 = 결정적). 탭 병사에서 7,874로 시작해 3,980까지 줄고, 건물·자원 탭에서 3,980 → 자원 p50 0, 확인 뒤 PS9는 100%로 회복(비회귀 PASS).
- 사전등록 밖 공개: (1) **PS27(떠남 화면) 1,055~1,174 present 내내 HD 80.754%(stale 92,383 고정)** — PS27 캡처를 남기지 않아 어떤 화면인지 UNKNOWN, 사전등록 PASS 항목에 없다. (2) PS29·탭 창의 경과 p95 12~13ms(PS27·PS9는 7·12ms; baseline lane은 trace가 없어 비교 불가 → 성능 증가 여부 UNKNOWN). (3) PS29 창 menu_copy_calls가 present마다 +1(전면 menu copy 경로가 도는 것은 가설대로), `partial_copy_calls`·`frame_copy_calls`는 변화 0.

## FAIL 귀속 (같은 회차, 수리 없음)

- **census(`--census-only --census-state 29 --fixture g7defeat --scene-actions none`, 로그 `logs/gates/lap1125-hrs0-census29.log` exit 0, census_gate PASS, 64 present)**: raw `census29/census/census_raw.jsonl` `6067e5e2…`. PS29 최종 프레임 writer 지도 = `rle_clip`(0x466D50) **18,274 px** + `block_copy`(0x466280) **461,726 px**, 나머지 writer 0, unknown 0, attribution 100%, 64 present 모두 동일(`rect_fill` 0x465E80은 PS29에서 1회 호출(158,135,477,258,254)이나 최종 지도 0 px). → **미러 밖(미후킹) writer는 census에서 관측되지 않는다.**
- 후보 trace: 같은 구간에서 `menu_copy_hash_changes`=1(첫 present 이후 hash 불변 = menu copy 원본 정적), `primitive_stale_pixels_total` 증가 약 +6,000~6,300/present(PS29 구간 4.5M까지), `identity_lookup_misses` 0. 즉 stale +72 px/present는 **menu copy 원본 변화가 아니라 rle 프리미티브 호출 쪽 누적**으로 보이나 어느 스프라이트인지는 미귀속.
- 위치 추정(보조, 증거 약함): 후보 `ps29.png`를 baseline `ps29.png`로 만든 완전 Scale2x 기준(`rs0_stale_loc.py` `2853fdb3…`)과 비교하면 논리 픽셀 1,170(0.24%)만 다르고(nearest 평면 509·기타 661, 분포는 글자·버튼 모서리 등에 흩어짐) 7,874 px 군집은 보이지 않는다. 평면 영역에서는 nearest와 Scale2x가 같아 **stale 7,874의 상당 부분이 화면에 보이는 결함이 아닌 평면 영역 bookkeeping일 가능성**이 있다(UNKNOWN). 숫자 7,874·+72/present·결정성은 막대 애니메이션(전체 탭 병사 3/건물 19 등 4개 그라데이션 막대, 탭마다 값 변경)과 정합하나 추정이다.
- 못한 것: PS29 stale 위치 지도(`--stale-mask`는 C가 PS3만 덤프)·screen watch(C가 PS3/PS23만 허용) → PS29 전용 위치 귀속에는 C source 변경이 필요하다. 이번 회차는 사전등록대로 수리·C 변경 없이 중단.

## 검사 / 회귀 / 남은 위험

- 이번 회차 제품 C 변경 0, 기존 경로 불변(새 옵션은 옵트인, save006/save000/new-game 경로 문자열 단언만 갱신). 전체 `make check`는 문서 freeze 뒤 1회(결과는 STATUS).
- partial/한계: 결과 화면은 G7 결함으로 만든 패배 화면(승리 화면 UNKNOWN), 탭은 3개만 클릭(전체 탭 복귀 미측정), PS27 캡처 없음, 부하 대표성 낮음, 성능 비교 없음. 사용자 합격·G1 마감 아님.
- 독립 검수: 이 FAIL 판정·귀속은 work 단독이며 middle 검수 필요(`loop/ESCALATE_SOL`). 사용자 G1 시험 요청(APPROVALS lap1104)은 계속 대기.

## 다음 한 가지

middle(Opus): (1) a·b raw 독립 재계산(PS29 stale 7,874·+72/present·탭별 stale), (2) PS29 HD ≥98.6 기준을 유지할지(귀속 필요) 보지 않는 평면 stale로 보고 기준·측정(stale 대신 화면 비교 지표)을 재정의할지 결정, (3) PS29 stale 위치 귀속용 최소 C 변경(PS29 stale mask 또는 screen watch state 29) 사전등록 또는 PS27 80.754%·승리 화면 우선순위 결정.
