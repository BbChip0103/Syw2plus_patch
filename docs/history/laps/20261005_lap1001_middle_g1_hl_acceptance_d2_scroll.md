# 2026-10-05 | lap1001 | G1 H-L 독립 검수 + G6 H-G6f 재계산 → 다음 work D-2 스크롤 성능

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / 중간(middle) 1 lap. 게임 실행·source 변경·커밋 0.
- 가설 / 사용자 관찰: (1) lap1000 work H-L(`0x4672E0` 로고 반투명 RLE diff 미러)이 P6 로고 steady stale 2,102 px를 신규 stale 없이 제거했다. r1의 프레임 880 부재와 성분 D 24 px는 H-L과 무관하다. (2) lap991 H-G6f probe-result 3개(G6 최우선 목표의 남은 미검수 항목)가 기록대로다. (3) 수용 시 steady stale 0이 되므로 다음 G1 work 한 가지를 정한다.
- 예상 PASS / FAIL 조건: 제품 helper·`analyze_lap1000.py` 없이 새 스크립트(numpy+stdlib)로 raw를 재계산해 lap1000 기록 수치(L-1~L-4)와 lap991 기록(G6-1~G6-4, local, EXE)이 일치하면 수용. 불일치·raw 해시 불일치·source/bridge 불일치면 불수용.
- 변경 파일 / source fingerprint / 커밋: 문서만(이 기록, `docs/STATUS.md`), `loop/ESCALATE_SOL` 처리·삭제(원문 아래 부록). source 불변(`g1_mirror2x.c` `42245a20…a210`, `.h` `2ee0ff0f…675a`, `direct_draw_trace.c` `0669e798…c1c2`, `tests/test_g1_rect_fill.py` `34f804f9…7334` — 현재 파일 재해시 일치). uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE `b56986e0…08a8ac` 재해시 MATCH, 원본 `0x4672E0` 바이트 `51 53 56 8B F1 57`(hook 기대값과 일치). 기준 = lap998 r1/r2/r4(H-G 수용), 대상 = lap1000 r1~r3(fresh save006 scale2x pair). G6: lap991 fixed_start `port` seat2·`cand67` seat2/seat0(engine-seeded op5 synthetic fixture, owner=local). 활성8인 부하 증명 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시(공유 temp `20261005_lap1001_middle_review/`):
  - `.venv/bin/python recalc_lap1001.py` → `recalc_lap1001.json` SHA256 `37db64c625bada7278ed8013a9f1ba120cfac91ad66d837b75103593f171b165`(스크립트 `16e83081…2442`, stdout `8aacbd24…532b`).
  - `python3 recalc_g6f.py` → `recalc_g6f.json` `36632500cce0013dcc948cf408c8d205961ebf7a787d0810a6102d7628f6e450`(스크립트 `4e67fd23…38ad`).
  - 입력 raw 해시(앞8자, lap1000 기록과 일치): r1/r2/r3 stale_mask `cede6a3c`/`6c6338d7`/`879a00f0`, trace `45d86a51`/`b26d7a53`/`19c52f11`, pair `4e563934`/`035025b9`/`f2905276`. G6 probe-result `74e78f51…`/`646d26e7…`/`3ba0659c…`(lap991 기록 일치).
- 측정값 / 판정:
  - **프레임 집합**: 기준 3개·r2·r3 덤프 51개(300..880 중 39개), r1 50개(마지막 620, 880 없음). r1 PS3 present 868 < 880이라 present 순번 880 덤프가 생길 수 없다 — 장면 길이(present 수) 문제이며 hook 무관(lap998 r3와 같은 형태).
  - **L-1 PASS**: 로고 교집합(39프레임) 기준 2,102×3 → r2/r3 **0/0**; 공통 38프레임(r1 포함) r1/r2/r3 **0/0/0**, 제거 2,102 전부 로고 안.
  - **L-2 PASS**: 신규 stale(어느 기준에도 없던 것) 0/0/0. 39프레임 전체 교집합 r2/r3 **0**(성분 0개). 38프레임에서는 6개 run 모두 같은 성분 D `y515..520×x616..619` 24 px뿐(기준 3개도 24).
  - **성분 D 판정**: 6개 run 모두 프레임 300·301·585..620(38개)에서 D 24 px 전부 stale, 880에서는 0. 기준(H-L 이전)과 동일한 기존 일시 stale → **H-L 무관, 신규 아님**(정체는 별개 미조사 유지).
  - **L-3 PASS**: `blend_4672E0` invocations 892/892/892 = mirrored_calls = changed_calls, mirrored_pixels 1,874,066/1,874,048/1,874,048, reject_target·bounds·size·guard 모두 0. flip_rle 946/947/947 = mirrored(H-F3 유지).
  - **L-4 PASS(partial)**: 안전 7종 max 0(6/6 run), PS3 present 868/886/886, elapsed p50 5·p95 7ms(max 9/16/10), cov p50 99.295%/99.299%/99.299%(기준 98.86%), Scale2x·V2·V2q·input_effect·minimap PASS. V2s FAIL = production `v2s_single_black_blocks` **2,852/2,856/2,856**>2,000(기존 gate, 사용자 판단 큐), 나머지 4 tag PASS → pair HOLD. gate/validator 불변 확인.
  - **source/bridge**: 현재 source 4개 SHA = lap1000 기록, r1~r3 `bridge/`의 C/H 3개 byte 동일.
  - → **H-L PASS(partial) 수용.** fresh save006 고정 카메라 장면의 steady stale 교집합이 0이 됐다(lap953 이후 지목된 성분 전부 제거). 단 8비트 결과의 변경 픽셀만 Scale2x 미러하므로 P6/P7 HD 혼합 화질은 명시 잔여로 남는다.
  - **G6 H-G6f 재계산(불일치 0)**: stage raw에서 직접 유도 — `port` seat2 G6-1 `[1,1,1,1,1,1]`(결함 재현)·cap 미충족, `cand67` seat2 `[1..6]`(각 클릭 대상=isolated fixture 슬롯이며 선택에 포함)·G6-2 1→8(pair 포함, rect 안 다른 유닛 4기)·G6-3 8→7(victim만 정확히 제거)·G6-4 drag 50·추가 클릭 뒤 50 유지, local 2·60초 `[2]`, `cand67` seat0 `[1..6]`·1→3·3→2·cap 50. EXE `703deaf4…`/`58b9b22a…` 기대 일치, game 사본 삭제·prefix 프로세스 0. probe `checks`와 유도값 일치 → **H-G6f PASS(partial, 기술) 수용**. G6·G7 사용자 합격(APPROVALS lap989)은 별개로 대기.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 0. 남은 G1 항목: pair HOLD(V2s raw 사용자 판단), **D-2 스크롤 성능(한 번도 측정 안 됨, lap863 §169)**, 스크롤/두 번째 장면에서의 새 미러(H-T·H-F~H-L) 동작, 성분 D 정체, PS35·P6/P7 HD 화질, burst UNKNOWN, 사용자 승인. 마일스톤 경계 아님(G1 미완료, 사용자 합격 요청 없음) → 일반 middle→work 연결. 디스크 여유 83GiB.
- 다음 한 가지: **work D-2(현재 source 그대로 `--terrain-scroll` pair로 스크롤 중 성능·안전 측정)** — 아래 handoff.

## Handoff — work D-2 (스크롤 성능, FEASIBLE)

- 왜 지금: 고정 카메라 steady stale은 0이 됐고, 이후 추가된 hook 6개(H-T·H-F·H-F2·H-F3·H-G·H-L)는 스크롤 상태에서 한 번도 실행되지 않았다(마지막 `--terrain-scroll` 실행 lap934). D-2는 G1 사용자 제출 전 필수(lap908 handoff)이며 하네스가 이미 있다(`--terrain-scroll`, DOWN→RIGHT 같은 키·공통 tick 계획, `--p4b-s-snapshot` 상태 gate). 제품 코드 변경 없이 측정만 하는 첫 work다.
- 명령(순차 2회, 병렬 금지): `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap{N}_d2_s{K} --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/{YYYYMMDD}_lap{N}_work_d2_scroll/s{K} --hd-source scale2x --terrain-scroll --p4b-s-snapshot --reference-completed-states /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap888_p4b_scroll_phase/scroll-phase-diagnostic-result.json`. `--stale-mask`은 쓰지 않는다(고정 카메라 순번 전용). 실행 전 PROMPT ③ 장기 실행 규칙(setsid+exit 파일, 끝까지 대기).
- 분석(사후, 제품 변경 없음): 결과 `common_tick_plan`의 `down_input_tick`..`right_observation_tick`을 스크롤 창으로, 그 이전 PS3 present를 고정 창으로 나눠 candidate `mirror2x_present`의 `elapsed_ms`와 `game_tick`/`ts_ms`를 집계한다.
- 사전등록 PASS(2/2 pair):
  - D2-0 하네스: 두 lane `terrain_scroll_parity` PASS·`scene_state_equal` true·DOWN/RIGHT 카메라 이동 동일. scroll coverage DOWN/RIGHT 값을 보고(참고 lap908 346,526/335,727; 이후 hook 변화로 gate 아님).
  - D2-1 성능: 스크롤 창 candidate PS3 present ≥20개, `elapsed_ms` p95 ≤ **같은 run 고정 창 p95 + 16 ms**(P4 카드 C 규칙; 현재 고정 p95 7 → 약 23 ms 이하), max 보고.
  - D2-2 진행률: 스크롤 창 game_tick 진행/host 시간(ts_ms) 비 candidate ÷ baseline ≥ **0.95**. baseline lane trace에 같은 필드가 없으면 candidate 스크롤 창 ÷ candidate 고정 창 ≥0.95로 대체하고 그 사실을 기록.
  - D2-3 안전: 안전 7종 max 0, 모든 hook의 reject/clip mismatch 계수 보고(새 hook 6개 포함), 크래시 0, cleanup PASS.
  - D2-4 진단(gate 아님): 스크롤 뒤 `stale_after_scroll`·스크롤 후 캡처의 원본/후보 비교(격자·seam·잔상 유무), V1/V2/V2q/Scale2x 결과와 V2s raw 기록.
- FAIL/반증: D2-1이 2/2 초과면 FAIL — 다음은 같은 명령 + `--perf-sections`로 미러·합성·전사 구간 귀속. 1/2만 초과면 같은 명령 3번째 실행으로 환경 변동 판정(lap995 방식). D2-3 >0이면 해당 hook 지목 후 work 수리. 하네스가 새 hook과 충돌해 실행이 안 되면(추적 가능한 결함) 고쳐서 재실행(구현 우선), 원인 설명 불가 3회면 ESCALATE.
- 범위 밖: 제품 hook 추가/변경, gate·validator·기준 변경, 성분 D 조사, V2s 의미 변경, G6/G7 추가 수정, 커밋.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1000 work, SHA256 `55d28d42c80504b68708813e00956031c4d100e2797e12bc9bcf7ffd09dd00fe`, 10줄)

```
lap1000 work(Claude Code claude-sonnet-5-5) → middle(Opus) 독립 검수 요청: G1 H-L(`0x4672E0` 로고 반투명 RLE diff 미러) 구현·실행 완료, 판정은 middle 몫(일반 work→middle 인계; 단 steady stale 0 도달로 다음 G1 방향 재선택 필요).
기록: docs/history/laps/20261005_lap1000_work_g1_blend_rle_diff_mirror_hl.md (uncommitted)
결과: hook 0x4672E0(6B 51 53 56 8B F1 57, 인자 하위16비트 부호확장, 화면 밖 reject·자르지 않음) 호출 전후 diff 미러. fresh save006 scale2x pair 3회(공유 temp 20261005_lap1000_work_blend/r1..r3, 전부 exit 2 = V2s production raw 기존 gate HOLD):
 L-1 로고 교집합 2,102→0/0/0, L-2 신규 stale 0·로고 밖 r2/r3 0(r1은 프레임 880 부재로 공통 38프레임 성분 D 24 = 기준도 동일 24, 신규 0)·39프레임 전체 교집합 r2/r3 0,
 L-3 blend invocations 892×3=mirrored·changed 892·reject 4종 0, L-4 안전 0·present 868/886/886·p95 7ms·cov p50 99.30%·V2s production raw 2,852/2,856/2,856(기존 gate, 사용자 판단 큐).
middle이 확인할 것:
 1) r1~r3 raw(stale_mask/trace/pair-result)를 제품 helper 없이 재계산(analyze_lap1000.py·analysis_lap1000.json 대조) — 로고 0·신규 0·blend 계수·안전.
 2) r1만 프레임 880 없음(present 868, lap998 r3와 같은 형태)과 성분 D(24px)가 H-L 무관임을 판정.
 3) source SHA(g1_mirror2x.c 42245a20…, .h 2ee0ff0f…, direct_draw_trace.c 0669e798…, tests/test_g1_rect_fill.py 34f804f9…)·bridge 사본 일치.
 4) 수용 시 다음 가설: steady stale 0 도달 → 남은 G1 항목(V2s raw 사용자 판단, D-2 scroll 성능, 두 번째 장면, 성분 D 정체, P6/P7 HD 혼합 화질) 중 다음 work 한 가지 선택.
```
