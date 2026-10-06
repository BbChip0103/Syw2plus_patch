# 2026-10-05 | lap1005 | G1 H-D2c 스크롤 뒤 캡처 독립 검수 → 다음 work 연속 스크롤(D2-5)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(확인·계획) 1 lap. 게임 실행·source 변경·commit 0.
- 가설 / 검수 대상: lap1004 work H-D2c(하네스만, `tools/g1_saved_scene_probe.py` SHA `aba7b1c7…7d88`, `tests/test_g1_saved_scene_probe.py` `80cd870a…6f36`, 둘 다 untracked)의 C-0~C-2 판정이 raw로 재현되는가, gate 의미가 바뀌지 않았는가.
- 예상 PASS / FAIL 조건: lap1003 사전등록 C-0~C-2. 재계산 불일치·required_tags 변화·scroll_after가 gate에 섞이면 FAIL.
- 변경 파일: 이 기록, `docs/STATUS.md`. `loop/ESCALATE_SOL`(lap1004 work 요청) 처리 후 삭제, 원문은 아래 부록. source/test 변경 0.
- 원본 SHA / 후보 / fixture: 원본 EXE `b56986e0…08a8ac`, save006 `616b7997…a064`(synthetic false, 활성8인 부하 증명 아님). 후보 bridge source 파일(.c/.h/Makefile/def) 전부 lap1002 사본과 SHA 동일, `_inmm.dll`은 6바이트만 다름(PE TimeDateStamp·checksum·debug 타임스탬프 위치 137/138·217/218·271877/271878) → 같은 source 재빌드. build manifest SHA 차이(`c9550528…`→`d764d4ec…`)는 dll 경로·SHA 칸뿐.
- 재계산 방법(제품 helper·work `profile.py`/`analyze_perf.py` 미사용, 새 스크립트): 공유 temp `20261005_lap1005_middle_review/`
  - `recalc_lap1005.py`(SHA `4953e019…58f3`) → `recalc_lap1005.json` `17805454…8789`: PNG·pair-result·candidate trace_raw 직접 읽기, numpy로 V1/V2/V2s/V2q 재계산, **독자 Scale2x(AdvMAME2x 규칙) 구현**과 후보 대조, 스크롤 창 성능.
  - `recalc_lap1005_strip.py`(`c69bf501…e1f`) → `…_strip.json` `8315fea2…794`: 스크롤로 새로 드러난 띠(하단 base행 448..479, 우측 열 736..799) 대조·1칸 어긋남 검사.
  - `recalc_lap1005_unexplained.py`(`2436d872…6b78`) → `…_unexplained.json` `b47c23ce…a36`: V2s 단일 흑을 Scale2x 설명/비설명으로 분리.
  - 육안: `loaded_vs_scrollafter_base_cand.png`(`b19c5e67…eb7`, 원본 loaded | 원본 scroll_after | 후보 scroll_after nearest 축소), `hud_top_zoom.png`(`252f7d16…16b`).
- 측정 / 판정(s1 / s2; 입력 pair-result `d4d06897…`/`027f1adf…`):
  - **C-0 재현**: pair 키 집합 = lap1002 + `scroll_after_comparison` 하나뿐. 세 gate `required_tags` = `[loaded, selection, drag, minimap, production]` lap1002와 동일, `capture_visual_comparisons` tag 5개(scroll_after 없음). 코드 확인: `_v2/_v2s/_v2q_capture_gate`는 `G1_CAPTURE_TAGS`만 순회, `_pair_status`는 scroll_after를 읽지 않음, `scale2x_validator`는 trace만 사용 → gate 의미 불변. terrain_scroll_parity PASS·scene_state_equal true·scale2x gate PASS·pair status HOLD(V2s production) 2/2. candidate barrier PASS(program_state 3), baseline은 barrier 없음(원본 lane, 설계대로).
  - **C-1 재현**: 고정 n=123 p95 6/6, 스크롤 창(tick 24692..24824) n=133 p95 6/6·max 8/7, ticks/s 비 **1.0035/1.0026**, 안전 7종 max 0, hook reject 계수 0, `overlay_blt_rejects` 1,646/1,647·textout reject_target **5,575/5,586**(work 기록의 5,586은 s2 값), cleanup ok 2/2.
  - **C-2 재현**: scroll_after 수치 전부 보고값과 일치(불일치 0): nearest diff 110,127(일치율 0.94264)·V2 흑 9,559→9,722(+163)·**V2s 1,824**·V2q 0. 4 PNG SHA 두 run 동일(baseline `362bd048…fbf`, candidate `c77d0080…005`) → 결정적. 독자 Scale2x 대비 후보 subpixel 일치율 **99.28%**(loaded 99.01%보다 낮지 않음). V2s 1,824 중 Scale2x 설명 1,816·**비설명 8**(loaded 20/56, production 189 — lap962 80~254 범위). 완벽 Scale2x 기준 V2s: scroll_after 2,193·production 3,566/3,564(lap962 3,547과 같은 결론: raw gate는 coverage 축소 없이 통과 불가).
  - 실제 스크롤 확인: 원본 loaded→scroll_after 최적 평행이동 **(dy 32, dx 64)** = 등각 1칸 대각(카메라 (158,101)→(160,101)), 그 이동에서 불일치 9.8%(이동 0이면 64.7%) → 캡처는 스크롤된 화면이다.
  - 새로 드러난 띠: Scale2x 비설명 블록 비율 하단 0.75%·우측 1.44%·기존 내부 0.83%, 32행 띠/64열 띠 최대 1.71%/1.47%. 하단 띠 1칸 어긋남 검사: 이동 0 불일치 2.75%, ±16/±32행 59.8~88.4% → **띠 어긋남·잔상 없음**. 육안: 지형 경계·건물·HUD(`96807 30031 1893/2300`) 일치.
  - 전사 정정: work 기록 "V2s FAIL은 production 2,816 raw로 lap1002와 동일"은 판정(FAIL)만 같다. 값은 lap1002 2,857 → lap1004 **2,816**(selection 1,800→1,804, minimap 453→442). scroll_after 캡처가 이후 캡처 시점을 조금 늦춘 영향으로 보이며 판정은 바뀌지 않았다.
- 판정: **H-D2c PASS(partial) 수용**. D-2의 D2-4(스크롤 뒤 시각)는 1칸×2·한 장면 관측 PASS. 제품 마감·사용자 승인 아님. G1 pair HOLD(V2s production raw, 사용자 판단 큐) 유지.
- 회귀 / 남은 위험: 회귀 0. 남은 G1: 연속 스크롤 성능(D2-5), 두 번째 장면, 성분 D, PS35·P6/P7 HD 혼합, burst UNKNOWN, V2s raw 사용자 판단, 사용자 승인. 마일스톤 경계 아님 → 일반 middle→work 연결.
- 다음 한 가지: **work H-D2h(키 유지 연속 스크롤)** — 아래 handoff. 두 번째 장면보다 먼저 고른 이유: 실제 플레이에서 가장 흔한 조작이고, 지금까지 스크롤은 terrain RLE 증분 16·30회뿐이라 화면 대부분 재그리기 부하가 측정된 적이 없다. 같은 하네스·같은 save라 변수 하나만 바뀐다.

## Handoff — work H-D2h (키 유지 연속 스크롤, FEASIBLE)

- 근거(정적, 이번 회차 확인): `--terrain-scroll` 흐름(`tools/g1_saved_scene_probe.py` L3344~3440)은 입력 checkpoint에서 게임을 멈춘 채 `_send_key_edge(down=True)`를 보내고, 풀어 준 뒤 **카메라가 처음 바뀌면 바로 keyup**한다(1칸). checkpoint는 `down_input/down_observation/right_input/right_observation/final_observation` 5개(`phase_target_ticks`)이고 각 checkpoint는 게임을 멈춘 상태다. 그러므로 keyup을 "카메라 첫 변화"가 아니라 **다음 observation checkpoint에서 멈춘 상태로** 보내면 두 lane 모두 같은 tick 구간(36 tick) 동안 키를 누른 셈이 된다 → FEASIBLE.
- 최소 변경(제품 DLL·gate·validator·한도 변경 0, 하네스만):
  1. 새 옵트인 `--terrain-scroll-hold`(기본 off, 기존 1칸 흐름 바이트 단위 불변). `--terrain-scroll` 필요.
  2. hold 모드: input checkpoint에서 keydown(기존과 같음), 카메라 첫 변화에서 keyup하지 않고 짝 observation checkpoint(멈춘 상태)에서 keyup. 카메라 샘플은 계속 기록. `_expected_scroll_camera` 1칸 검사는 hold 모드에서 "같은 방향 ≥1칸 이동 + 두 lane 최종 카메라 동일"로 대체(진단 필드에 칸 수 기록).
  3. 회귀 테스트 RED→GREEN: hold 모드 keyup이 observation checkpoint에서 나가는지, 기본 모드 경로 불변인지.
- 실행: lap1004와 같은 명령 + `--terrain-scroll-hold`, fresh runtime-root·공유 temp 새 폴더, 순차 2회. exit 2(V2s production raw 기존 gate)는 예상.
- 사전등록 PASS/FAIL:
  - H-0 하네스: 키당 카메라 이동 **≥3칸**(미만이면 연속 스크롤이 아니므로 "hold 부족" 기록, 한도 안에서 observation tick 간격만 늘려 1회 재시도), 두 lane `camera_after_sequence` 동일·terrain_scroll_parity·scene_state_equal(2/2). lane 간 카메라가 다르면(키 반복이 wall-time 의존) 시각 비교는 UNKNOWN으로 두고 성능만 판정.
  - H-1 성능: hold 창(down_input..right_observation) PS3 p95 ≤ 고정 p95+16·ticks/s 비 ≥0.95, 안전 7종 0, hook reject 0, cleanup ok. terrain RLE 호출 증분(lap1002 16·30)과 present당 stale/coverage를 함께 기록.
  - H-2 시각(진단, H-0 lane 카메라 동일일 때): scroll_after V1/V2/V2q PASS, V2s raw·비설명 값 기록, 새로 드러난 띠 1칸 어긋남 없음(이번 회차 `recalc_lap1005_strip.py` 방식).
  - FAIL: H-1이 2/2 초과 → 성능 결함. `g1_perf_sections` 구간으로 원인 함수 지목 후 다음 work 수리. 1/2만이면 3번째 실행으로 판정(다른 저장소 부하 정황 기록).
- 이후 후보(이번 범위 아님): 가장자리 마우스 스크롤, 두 번째 장면 pair.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문

```
lap1004 work(claude-sonnet-5-5) -> middle(Opus) 독립 검수 요청: G1 H-D2c(하네스만, 제품 변경 0).
기록: docs/history/laps/20261005_lap1004_work_g1_d2c_scroll_after_capture.md (uncommitted)
결과: scroll_after 캡처+진단 비교 추가, 테스트 3개 RED->GREEN, fresh pair 2회(exit 2=V2s raw 기존 HOLD) C-0/C-1/C-2 PASS(scroll_after V1/V2/V2q PASS, V2s 1,824, 띠 어긋남 0, PNG 두 run 동일).
middle이 확인할 것: 1) s1/s2 pair-result·scroll_after PNG를 helper 없이 재계산(diff 프로파일, 4 PNG SHA), 2) required_tags/gate 불변, 3) 수용 시 D2-5 연속 스크롤 vs 두 번째 장면 선택.
```
