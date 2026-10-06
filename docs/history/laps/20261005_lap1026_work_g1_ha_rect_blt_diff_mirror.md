# 2026-10-05 | lap1026 | G1 work — H-A: back buffer `IDirectDrawSurface7::Blt`(KEYSRC 확대) diff 미러 (+H-A2 present 재검증)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 승격·폴백 없음.
- 가설: lap1025 middle 사전등록 — 남은 save000 stale 71.6%(p298..338)와 표본 A writer는 미러 경로가 없는 back buffer 대상 KEYSRC `Blt`다. BltFast overlay 동형 diff 미러(`g1_overlay_blt_apply` 재사용)로 A·p298..338을 없앨 수 있다.
- 예상 PASS / FAIL 조건: lap1025 §5.3 A-0~A-4 그대로(A-1 표본 A 41→≤2·B/C ≤2, A-2 p298..338 중앙값 16,261→≤1,000 및 다른 창 +10% 이내, A-3 p95≤16ms·ticks 비≥0.95, A-4 save006 38프레임 24 px·신규 0·880 포함 39프레임 0).
- 변경 파일 / source fingerprint / 커밋: uncommitted.
  - `tools/inmm_stub/g1_mirror2x.c` `0243f543…b0db0`: `g1_mirror2x_overlay_rect_blt_begin/end`(전용 before 버퍼 `g_rect_blt_before`, 계수 14개), `rect_blt_heal_at_present`(H-A2), 진단 `layer_drift.jsonl` `b` 레코드(`SYW2_G1_LAYER_DRIFT=1`일 때만).
  - `tools/inmm_stub/g1_mirror2x.h` `633ff485…762c`: 선언·getter 14개.
  - `tools/inmm_stub/direct_draw_trace.c` `c89df117…5902`: `hook_blt`가 PS3·non-primary일 때 begin→원본→end로 감쌈, metrics `overlay_rect_blt_*`(`rect_blt_details[800]`; `mirror_details[5000]` 불변·기존 pin 유지).
  - `tests/test_g1_rect_fill.py` `2300333d…9c4f`: 계약 테스트 `test_rect_blt_back_buffer_diff_mirror_contract` 1개(처음 RED: 헤더 선언 부재 → GREEN). H-A2 heal 검사는 구현과 같은 편집에서 추가돼 별도 RED는 없다.
- 원본 SHA / fixture: 원본 EXE `b56986e0…8ac`(pair-result `source_unchanged` true), save000 `1c703551…19da`(index 1)·save006 `616b7997…a064`, `--hd-source scale2x`. 활성8인 부하 증명 아님.
- 실행 명령(공유 temp `20261005_lap1026_work_ha/`): `run.sh`(v1) = lap1024 s0/s6 인자 그대로(`--fixture save000 --scene-actions none --performance-window --layer-drift` ×2, save006 `--stale-mask 6-12,30-34,300-301,585-620,880` ×2), `run2.sh`(v2, 아티팩트 root `v2_*`). 로그 `logs/gates/lap1026_ha_*`·`lap1026_ha2_*`. 전부 exit 2 = 기존 pair HOLD(save000 `--scene-actions none` non-loaded tag, 하네스 무변경). `game` 사본은 하네스가 삭제(`game_removed` true).

## 측정값 / 판정

### v1(Blt 미러만, 4 run: s0 r1·r2 + 진단 s0 r3·r4)
- A-0 유효: `overlay_rect_blt_invocations` 5 = mirrored 5(KEYSRC 5, reject 전부 0), mirrored_pixels 50,705, 안전 0, cleanup·source true.
- **A-1 FAIL(부분)**: 표본 A stale present 41→**36**(298~302만 해소, 303..338 잔존), B 0·C 0. **A-2 FAIL**: p298..338 중앙값 16,261→**16,391**.
- 진단(r3·r4 `layer_drift.jsonl` `b` 레코드): Blt 5회 = p298·299·300·301·302(마지막 170×128 두 번, `ch` 1405/5550/12668/15541/15541). 표본 A bf 85→af 187, 적용 직후 `ex`=187 → 미러 자체는 정상 동작. 그러나 p303 표본에서 `snap`=85·`scr`=187이 p338까지 유지(p339에서 scr 85). lap1022 screen watch 근거(`0x004662DE` 캐시 전송이 **매 present** A를 85로 쓰고, `wined3d.dll` 별도 스레드가 **매 present(41회 p298..338)** 187로 되돌림)와 함께 읽으면: 5번째 Blt 이후에는 게임이 호출하는 Blt가 없는데도 wined3d가 present마다 팝업 영역을 sysmem에 재기록하고, 후보 캐시 전송 hook이 같은 present에서 `expected`를 85로 되돌려 stale가 된다. wined3d 내부 동기화로 추정(UNKNOWN: 호출 경로 미확정, hook_blt 호출은 5회뿐).
- 수리(1회, H-A2): 마지막으로 mirror된 Blt 사각형을 기억하고 present 직전(`layer_drift_present` 앞)에 `expected`를 before, 화면을 after로 두고 같은 diff(`g1_overlay_blt_apply`)를 재적용한다. 3 present 연속 차이 0이면 해제. 계수 `overlay_rect_blt_heal_{presents,pixels}`.

### v2(Blt 미러+H-A2 heal) — save000 pair 2회, save006 pair 3회(r2는 환경 outlier)
| 판정 | 기준 | r1 | r2 | 결과 |
|---|---|---|---|---|
| A-0 유효 | 안전 7종 0·cleanup/source true·`scene_state_equal`·invocations>0·keysrc≥4·항등식 | inv 5 = mirrored 5(keysrc 5)·reject 전부 0·heal 44 present/559,476 px·tick 50596/50596 | 같음·tick 50597/50595 | **PASS** |
| A-1 표본 | A 41→≤2, B·C ≤2 | A **0**·B 0·C 0(u A5/B1/C1 불변) | 같음 | **PASS** |
| A-2 화면 stale | p298..338 ≤1,000, p0..83 ≤722, p84..297 ≤348, p339..365 ≤651, 마지막40 ≤456 | **858**·656·316·591·414.5 | **858**·656·316·591·414.5 | **PASS**(p298..338 16,261→858, −94.7%) |
| A-3 성능 | p95≤16 ms·ticks 비≥0.95 | p95 7 ms·비 1.0000028 | p95 7 ms·비 1.0000038 | **PASS** |
| A-4 save006 | 38프레임 r1∩r2=24 px·신규 0·880 포함 39프레임 0·p95≤16·안전 0 | 아래 | 아래 | **PASS(r1·r3)**, r2는 outlier |

- save006(v2): r1 p50/p95/max 5/8/17 ms·cov p50 99.30%·lap1000 기준 3 run 대비 신규 0·제거 0·성분 D 24 px. **r3**(재실행) 5/7/9 ms·신규 0. **r1∩r3: 38프레임(≥300, 880 제외) 24 px(성분 D `y515..520×x616..619`), 880 포함 39프레임 0 px**. 안전 7종 0. `overlay_rect_blt`: r1 invocations 800 = mirrored 5 + reject_target 795(작은 non-screen 표면, Lock 전 거름), heal 55 present/799,235 px; r3 invocations 792 전부 reject_target. 5개 KEYSRC Blt 유무는 run마다 다르다(r1 있음·r3 없음).
- save006 r2: ps3 396·p50 23/p95 50/max 116 ms·프레임 14개(301까지)·minimap parity HOLD. 같은 시각 시스템 load average 28(다른 프로젝트 `Syw2plus_re_loop` 실행 중, `/proc/loadavg` 28.47→5.2로 하락 확인) → 환경 변동으로 판정(lap995 선례)하고 load 하락 뒤 r3를 재실행했다. r2 기록은 보존하되 판정에는 쓰지 않는다. 이 outlier가 이 변경과 무관한지는 r2의 계수(mirrored 0·reject_target 341·heal 0)가 설명한다(rect Blt 경로 비활성 상태에서도 발생).
- 요약: **H-A PASS(partial)**(v2 기준). 한계: (1) 표본 A의 직접 writer 호출 경로는 wined3d 안쪽이라 미확정이고 H-A2는 현상(매 present 재기록)에 대한 재검증이다. (2) 팝업 영역 HD는 1x 결과의 Scale2x(P6 범주). (3) H-A2는 mirror된 Blt 사각형 하나(≤320×128)만 감시한다. 다른 영역의 wined3d 재기록은 해당 없음.

## 회귀 / 남은 위험 / 독립 검수
- 제품 변경은 hook_blt 호출 감싸기·present 직전 소형 재검증(≤320×128, 팝업이 있는 동안만)뿐이다. 기존 mirror·gate·기준 줄 변경 0. `tests/test_g1_panel_layer.py` pin 불변.
- 미검증: 다른 save·장면의 Blt(save006에서 KEYSRC Blt 유무가 run마다 다름), 활성8인 부하, 사용자 승인(G1 마일스톤 아님). p24..58 일시 덩어리 3,444(불변), save000 `--stale-mask` 부재.
- backlog: p24..58 3,444·바닥 192~656, save006 짧은 run 꼬리·r2 같은 load outlier, 성분 D, hold keydown 위상, 가장자리 마우스 스크롤, wrap 쓰기 미추적, save000 overlay BltFast rejects 451. 환경: 다른 저장소 루프가 load 28까지 올린다 — 성능 gate run은 load 확인 뒤 실행이 안전하다.
- 독립 검수(다음 fresh Opus middle) 대기: v2 4 run 재계산(특히 A 표본·p298..338 창), heal 코드 검수(감시 사각형 수명·`expected` 덮어쓰기가 다른 writer의 정당한 갱신을 지우지 않는지), 호출 경로 UNKNOWN 정리.
- 다음 한 가지: middle H-A 독립 재계산·수용 후, 남은 save000 stale(p24..58 3,444·p0..83/p207..365 656·p366.. 414) 중 하나를 사전등록(trace 기반 귀속).
