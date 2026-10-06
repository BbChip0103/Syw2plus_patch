# 2026-10-05 | lap1009 | G1 H-D2i 맵 안쪽 왕복 hold 독립 검수 → 다음 work 두 번째 장면(save000, H-S2)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(확인·계획) 1 lap. 게임 실행·source 변경·commit 0.
- 가설 / 검수 대상: lap1008 work H-D2i(하네스만, `tools/g1_saved_scene_probe.py` SHA `ef47ce5b…2b05`, `tests/test_g1_saved_scene_probe.py` `ac8e1701…11d8`; 현재 파일 SHA = 4 run `execution_source.after` 일치·`unchanged` true)의 I-0~I-3 판정과 s1 불일치 분류가 raw로 재현되는가.
- 예상 PASS / FAIL 조건: lap1007 사전등록 I-0~I-3. 재계산 불일치·required_tags 변화·제품 원인 lane 불일치면 FAIL.
- 변경 파일: 이 기록, `docs/STATUS.md`. `loop/ESCALATE_SOL`(lap1008 work 요청) 처리 후 삭제, 원문은 아래 부록. source/test 변경 0.
- 원본 SHA / 후보 / fixture: 원본 EXE `b56986e0…08a8ac`, save006 `616b7997…a064`(직접 재해시 MATCH, synthetic false, 활성8인 부하 증명 아님). bridge 사본 source는 s1=s2=s3=s4, `inmm_stub.c`·`Makefile`도 lap1006 r2 사본과 SHA 동일; 현재 저장소와의 차이는 G2 `runtime_bridge.c`(`supply_probe_poll`) 빌드 주입분뿐 → 제품 source 불변.
- 재계산 방법(제품 helper·work `analyze_d2i.py` 미사용, 새 스크립트): 공유 temp `20261005_lap1009_middle_review/`
  - `recalc_lap1009.py`(SHA `78b2e757…59aa`) → `recalc_lap1009.json` `8619eb15…2acc`(stdout `3dc72a44…442e`): pair-result·camera_observations(monotonic ns)·key_emission·candidate trace_raw·scroll_after/loaded PNG 직접 읽기, numpy V2/V2s/V2q·독자 Scale2x(AdvMAME2x)·행/열 shift(lag), 성능 창, lap1002~1006 pair의 input_effect/minimap 대조.
- 측정 / 판정(s1 / s2 / s3 / s4; 로그 `42b4cec4`/`e53479c5`/`d56c0244`/`cff04a06` 일치):
  - **I-0 재현**: s2·s3·s4 두 lane 카메라 샘플 열 **완전 동일**, UP (158,101)→(134,77)·DOWN (134,77)→(158,101) 각 24칸, 모든 전이가 (±1,±1) 단위(clamp 없음 |dx|==|dy| 재계산 일치), 최종 snapshot 카메라 (158,101), parity 세부 bool 전부 true·action/final full-state diff 비어 있음. s1: baseline UP 23칸→(135,78), DOWN 24칸→최종 **(159,102)**, candidate 24/24→(158,101) → `same_camera_after_each_key` false·parity HOLD(보고값과 일치). 게임 상태 자체는 같다(`end_game_state_equal` true, full-state diff 0 — 카메라만 다름).
  - **s1 원인 분류(work보다 강한 raw 근거)**: 키 누름 송출(down_monotonic_ns)→첫 카메라 변화 지연이 s1 baseline UP만 **47.1ms**(= 전이 간격 중앙값 50.2ms, 정확히 1 tick)이고, 나머지 baseline 키 7건은 **5.7~14.4ms**, candidate 키 8건은 26.6~39.0ms. 마지막 변화 1148.1ms = 47.1+22×50 → 첫 tick(24693)만 잃고 keyup(release tick 24716, 다른 run과 동일)은 정상. 즉 키다운이 **다음 tick의 입력 확인 직후에 도착해 한 tick을 놓친** 것이다. baseline lane은 tick 관측→송출 뒤 다음 tick까지 여유가 원래 6~14ms뿐이라(candidate는 27~39ms) 송출 지연이 조금만 커져도 같은 경합이 난다. 하네스가 게임을 멈추지 않는 1ms 폴링 barrier에서 keydown을 보내는 구조의 **입력 위상 경합**이며, 이상이 난 쪽은 후보 DLL 미러 코드가 없는 baseline(원본) lane이므로 제품과 무관하다. work가 근거로 든 수신 `hold_ms` 12는 판별력이 없다(s2 candidate UP도 12인데 24칸).
  - **I-0 3/4 수용 타당**: 사전등록 "1/2만 실패면 3번째 실행"에 따라 추가 2회(s3·s4) 모두 PASS, 실패 1회는 위 기전으로 설명되는 기준 lane 입력 경합이고 candidate lane은 4/4 정확. 단, 하네스가 이 경우를 INVALID가 아닌 parity HOLD로만 남기는 점은 아래 backlog.
  - **I-1 재현**: 고정 n=123 p95 **6/7/6/10**, hold 창(24692..24824) n=133 p95(nearest-rank) **6/7/8/7**·max 7/17/12/12, ticks/s 비 **1.0028/1.0037/1.0014/1.0048**(일치). 전사 정정: s3 hold p95는 nearest-rank 8(선형 보간 7.4; work 7) — 한도(고정+16=22) 판정 불변. 두 키 candidate `scroll_gate` PASS 8/8, coverage p50 UP 463,204·DOWN 473,069, key_before 472,838~472,839/463,076~463,093. 안전 7종 max 0(4/4), mirror reject 비0은 `overlay_blt_rejects` 1,245/1,244/1,242/1,260·`panel_transfer_mismatch_cleared` 3.96M~3.99M(기존 계수), cleanup ok 8/8.
  - **I-2 재현**: s2/s3/s4 scroll_after 보고값 전부 일치(불일치 0): nearest diff 109,042(94.32%)·V2 9,202→9,334(+132)·**V2s 1,784**·V2q 0, 독자 Scale2x 대비 99.23%·V2s 중 Scale2x 비설명 **19**, 행/열 30% 초과 0, lag 검사 (0,0) 0.0598 최선(1칸 이동 0.76~0.86) → 스크롤 잔상·띠 어긋남 없음. PNG SHA s2=s3=s4(두 lane). s1은 baseline이 한 칸 어긋난 화면이라 V2q 7,711·lag 전부 0.77+ (보고값 일치, 비교 무효). lane별 loaded→scroll_after 차이 baseline 40,800/40,800/40,539 of 480,000(8.50/8.50/8.45%)·candidate 160,728/163,316/162,275 of 1,920,000(8.37/8.51/8.45%) → 후보 차이가 원본보다 늘지 않음(work 일치).
  - **I-3 재현 + 보강**: s2~s4 `minimap_diagnostic_parity` PASS·`input_effect_comparison` PASS(false check 0). 보강: input_effect는 lap1002·1004·1006 스크롤 pair 전부 HOLD(`selection_target`·`drag_capture_binding` false), lap1000 무스크롤 pair 3/3 PASS → 그 HOLD는 스크롤이 카메라를 시작점에 돌려놓지 않아 생긴 장면 오프셋 파생이었고, 왕복으로 카메라가 복귀하자 PASS. work 표현 "lap1004 수준/PASS 복귀"의 기준선은 lap1004가 아니라 lap1000이다(정정).
  - gate: required_tags 5개(scroll_after 없음) lap1004와 동일, 4 run status HOLD = `v2s_capture_gate` production 하나(production V2s raw 2,819~2,829, 기존 사용자 판단 큐). s1은 V2q selection/drag FAIL 추가(카메라 어긋남 파생).
- 판정: **H-D2i PASS(partial) 수용**(D2-5 연속 스크롤: 맵 안쪽 clamp 없는 24칸 왕복 1 장면, 3/4 run 전부 충족 + 1/4 기준 lane 입력 위상 경합 설명됨). 제품 마감·사용자 승인 아님. G1 pair HOLD(V2s production raw, 사용자 판단 큐) 유지.
- 회귀 / 남은 위험: 제품 회귀 0. 하네스 hold keydown 위상 경합(baseline 여유 6~14ms, 4 run 중 1회) — 이후 hold 측정을 다시 쓰면 lane 간 step 수 불일치를 INVALID+자동 재시도로 올리는 수리 필요(backlog, 이번 다음 일 아님). 마우스 가장자리 스크롤 미측정, 한 장면(save006).
- 다음 한 가지: **work H-S2(두 번째 인게임 장면 save000, loaded·고정 카메라 pair)** — 아래 handoff. D-2 스크롤은 1칸×2·가장자리 hold·안쪽 왕복으로 save006에서 충분히 덮였고, H-F~H-L hook 6종은 save006 PS3 한 장면에서만 검증됐으므로(PS9 메뉴는 lap956 별도) 다른 지형/유닛 구성의 일반성이 G1 남은 항목 중 가장 큰 공백이다.

## Handoff — work H-S2 (두 번째 인게임 장면 save000, 최초 가능성 조사 겸 최소 probe)

- 근거: 보호 fixture `Syw2plus_re/Syw2plus/save/save000.dat` 3,093,902 B, SHA256 `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`(lap363 pin과 이번 직접 재해시 일치). provenance는 사용자 실제 플레이 save로 보이나 synthetic 여부는 UNKNOWN으로 기록(lap948 미확인 그대로; 시각 G1 검증에는 지장 없고 활성8인 부하 증명으로 쓰지 않는다). 하네스는 `SAVE_NAME`/`SAVE_SHA256`/`SAVE_INDEX=7`과 save006 전용 장면 동작(HQ slot1199·selection/drag/minimap/production·lap888 reference states)에 묶여 있다.
- 최소 변경(제품 DLL·gate·validator·한도 변경 0, 하네스만):
  1. 옵트인 `--fixture save000`(기본 save006 불변). save000은 SHA pin 검사·read-only 원본·private 사본 사용. 불러오기 목록 index는 **추측하지 말고** 기존 save 목록 navigation 기록/캡처로 확정해 상수와 근거를 남긴다(save006=7).
  2. save000에서는 save006 전용 장면 동작·`--terrain-scroll`·`--p4b-s-snapshot`·reference states를 끄고 `loaded` 캡처 + 고정 카메라 present trace(PS3, ≥120 present)만 수행하는 경로(예: `--scene-actions none`). 두 lane 같은 tick/카메라에서 캡처.
  3. 테스트 RED→GREEN: 옵션 기본 불변(save006·기존 action 목록 그대로), save000 SHA 불일치 거부, save000일 때 save006 전용 동작 비활성.
- 실행: fresh runtime-root·공유 temp 새 폴더, `--hd-source scale2x --fixture save000 …`, 순차 2회. 끝나면 game 사본 삭제(output·manifest·prefix·로그 보존).
- 사전등록 PASS/FAIL:
  - S-0 로드: 두 lane PS3 진입·같은 sim_tick/카메라에서 loaded 캡처·scene_state_equal true, save000/save006/원본 EXE SHA 실행 전후 MATCH, 크래시 0, cleanup ok.
  - S-1 stale: candidate 고정 카메라 마지막 40 present `stale_pixels` 중앙값과 덤프 교집합 기록. save006 기준은 0(H-L 뒤). >0이면 FAIL이 아니라 **새 잔여**로 기록하고 다음 work는 `--census-only` save000으로 writer 지목.
  - S-2 시각: loaded V1/V2/V2q PASS, V2s raw·Scale2x 비설명 기록(gate 의미 변경 금지).
  - S-3 성능·안전: 고정 창 p95 ≤ save006 고정 p95(6~10)+16, 안전 7종 0, hook reject 수준 기록, ticks/s 정상.
  - BLOCKED: save000을 격리 UI 불러오기로 열 수 없거나 목록 index를 증거로 확정 못 하면 캡처·navigation 기록과 함께 BLOCKED, 다른 save 추정 금지. FAIL: candidate 크래시/안전 위반 → 원인 지목 후 다음 work 수리.
  - 1/2만 실패면 3번째 실행.
- 이후 후보(이번 범위 아님): save000 장면 동작(선택/드래그) 확장, hold keydown 위상 경합 INVALID+재시도 수리, 가장자리 마우스 스크롤, 가장자리 stale fallback writer.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문

```
lap1008 work(claude-sonnet-5-5) -> middle(Opus) 독립 검수 요청: G1 H-D2i(맵 안쪽 UP→DOWN 왕복 hold, 하네스만·제품 변경 0).
기록: docs/history/laps/20261005_lap1008_work_g1_d2i_roundtrip_hold.md (uncommitted)
결과: 옵트인 `--terrain-scroll-keys UP,DOWN`(기본 DOWN,RIGHT 불변, 테스트 5개 RED->GREEN, 189 passed), fresh pair 4회(전부 exit 2=V2s production raw 기존 HOLD). s2/s3/s4: UP/DOWN 24칸·clamp 없음·두 lane 카메라 열 동일·최종 (158,101) 복귀·parity PASS·hold p95 7·ratio 1.0014~1.0048·안전0·두 키 scroll_gate PASS·V2q 0·V2s 1,784·minimap/input_effect PASS 복귀. s1 FAIL 보존: baseline lane UP 23칸으로 최종 (159,102), candidate는 24/24 (원인 baseline 입력 타이밍 지터 정황, 미입증).
middle이 확인할 것: 1) s1~s4 raw 재계산(helper/analyze_d2i.py 없이), 2) s1 불일치 분류와 I-0 3/4 수용 타당성, 3) 다음 work 선택(두 번째 장면 pair / 하네스 lane 카메라 불일치 INVALID 수리 / 가장자리 stale writer).
```

- 1) 위 재계산 불일치 0(s3 hold p95 정의 차이 1건 정정). 2) 첫 변화 지연 47.1ms=1 tick으로 기전 설명 → 타당. 3) 두 번째 장면(H-S2) 선택, 나머지는 backlog.
