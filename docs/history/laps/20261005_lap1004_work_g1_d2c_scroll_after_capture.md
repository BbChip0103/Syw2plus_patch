# 2026-10-05 | lap1004 | G1 H-D2c 스크롤 뒤 캡처 하네스 + 시각 진단 pair 2회

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work 1 lap. 제품 DLL·gate·validator·한도 변경 0(하네스만).
- 가설: `--terrain-scroll` 최종 관측 뒤 두 lane에서 `scroll_after` 를 캡처하고 pair에 진단 비교만 추가하면, 스크롤 뒤 화면이 원본과 맞는지(D2-4 UNKNOWN)를 gate 변경 없이 관측할 수 있다.
- 예상 PASS/FAIL: lap1003 handoff 사전등록 C-0~C-2 그대로(FAIL = 지형 띠 어긋남·잔상 2/2).
- 변경 파일: `tools/g1_saved_scene_probe.py`(SHA `aba7b1c76785…`: 최종 관측 직후 `captures["scroll_after"]`, candidate는 `_wait_for_mirror_present(program_state=3)` barrier 선행; `_diagnostic_capture_comparisons`; pair `scroll_after_comparison`), `tests/test_g1_saved_scene_probe.py`(SHA `80cd870adfb8…`: 테스트 3개 추가, RED 3 failed → GREEN 179 passed). `G1_CAPTURE_TAGS`·`required_tags`·세 gate·`_pair_status` 불변(테스트가 scroll_after FAIL이 gate에 안 새는 것 고정). `make lint`·`typecheck` PASS. uncommitted. 참고: 시스템 `python3`은 Pillow 구버전이라 기존 `_compare_images` 테스트 5개가 실패한다(`.venv/bin/python`은 179 PASS, 기존 현상).
- 원본/후보 SHA / fixture: 원본 EXE `b56986e0…08a8ac`, save006 `616b7997…a064`, synthetic false, 활성8인 부하 증명 아님. 후보 DLL은 lap1002와 동일 source(제품 파일 불변).
- 실행 명령: 러너 `logs/gates/lap1004_d2c_runner.sh`(lap1002 러너에서 이름만 치환, setsid) — `tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1004_d2c_s{1,2} --artifact-root …/temp/Syw2plus_patch/20261005_lap1004_work_d2c_scroll_after/s{1,2} --hd-source scale2x --terrain-scroll --p4b-s-snapshot --reference-completed-states …lap888…`. 순차 2회, 둘 다 exit 2(= V2s production raw 기존 gate HOLD, 예상). 로그 `logs/gates/lap1004_d2c_s{1,2}.log` SHA `2cb7e870…`/`3998e6f5…`. 산출물: pair-result `d4d06897…`/`027f1adf…`, `analysis_perf.json` `30daf5b0…`(lap1002 `analyze_d2.py` 경로 치환), `profile.json` `c233736f…`, `s1_side_by_side.png`(원본 nearest | 후보 | 차이 이진).
- 측정 / 판정(s1 / s2):
  - **C-0 PASS**: terrain_scroll_parity PASS·scene_state_equal true 2/2, 기존 5 tag 판정·required_tags 불변(V1 PASS·V2 PASS·V2q PASS, V2s FAIL은 production 2,816 raw로 lap1002와 동일), scale2x gate PASS, `scroll_after.png` 두 lane 존재·candidate barrier PASS. 캡처 시점 = 최종 관측 tick(24860) barrier 직후.
  - **C-1 PASS**: 스크롤 창 n=133 p95 6/6 max 8/7(고정 p95 6/6, 한도 +16 이내), ticks/s 비 1.0035/1.0026(≥0.95), hook reject 계수 0·`overlay_blt_rejects` 1,646/1,647·textout reject_target 5,586은 lap1002 수준(1,638/5,554), cleanup/게임 copy 잔존 0.
  - **C-2 PASS**: scroll_after 비교 s1=s2(PNG 4개 SHA 두 run 동일, 결정적): status PASS·V2 PASS(후보−원본 흑 +163)·V2q PASS(four 0)·V2s 단일 흑 1,824≤2,000·nearest_equal 0.9426. 월드 행/열 diff 프로파일: 30% 초과 행·열 0개(띠 어긋남 없음; `loaded` 대조는 s1 0, s2 열 4개 최대 10px — s2 loaded는 기존 timing 차), 행 최대 8.7%·열 최대 9.9%. side-by-side 육안: 지형 경계·건물·HUD 위치 일치, 격자/seam 없음, 차이는 전체에 흩어진 Scale2x 잡음뿐.
  - 한계: 스크롤은 여전히 1칸×2(연속 스크롤 미측정), 비교는 한 장면·한 시점, 캡처 후 유닛 애니메이션 차는 기존 tag와 같이 처리. input_effect HOLD(selection_target·drag_capture_binding false)는 lap1002와 동일한 기존 상태.
- 판정: **H-D2c PASS(partial)**(C-0~C-2 2/2). D-2의 D2-4 UNKNOWN → 관측 PASS(1 장면). 제품 마감·사용자 승인 아님.
- 남은: 연속 스크롤(D2-5, 키 유지 다칸), 두 번째 장면 pair, V2s raw 사용자 판단, PS35·P6/P7 HD 혼합, 성분 D, 사용자 승인.
- 다음 한 가지: middle 독립 검수(pair-result·PNG 직접 재계산) 후 D2-5 또는 두 번째 장면 선택.
