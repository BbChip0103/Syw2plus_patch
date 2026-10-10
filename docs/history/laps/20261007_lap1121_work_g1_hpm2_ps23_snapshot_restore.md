# 2026-10-07 | lap1121 | G1 work — H-PM2 PS23 정지 화면 스냅샷 복원(R-a) 구현·격리 실행

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 커밋 0.
- 입력: STATUS 다음 한 가지(lap1120 사전등록 §3 `20261007_lap1120_middle_g1_hpm1_review_hpm2_preregistration.md`). INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP`·`ESCALATE_SOL` 없음.
- 원본 SHA: 프로브가 매 run 시작 시 원본 EXE SHA를 검증(불일치 시 SystemExit)하고 세 run 모두 두 lane `source_unchanged=true`. 원본/참고 쓰기 0.
- 가설: PS23 진입 present의 유효 HD 스냅샷으로 정지 화면 동안 가려졌다 드러난 픽셀을 복원하면 저장 창 닫힘 뒤 띠 HD가 같은 present에 돌아온다.

## 변경 (전부 uncommitted)
- `tools/inmm_stub/g1_pause_snapshot.h`(신규, 순수 헬퍼): `g1_pause_restore_pick`(기존 HD > 스냅샷 일치 복원 > nearest)·`g1_pause_snapshot_action`(23 진입 CAPTURE·23 이탈 INVALIDATE)·`g1_pause_restore_active`.
- `tools/inmm_stub/g1_mirror2x.c`: `g1_mirror2x_copy_present`가 present마다 `G1_PROGRAM_STATE_VA`를 읽어 진입 present 루프에서 기존 판정 HD 픽셀(expected·`g_mirror` 2×2)을 스냅샷, PS23 동안 기존 경로가 HD가 아닌 픽셀 중 스냅샷 expected == pixel이면 `g_covered`·`g_expected_snapshot`·`g_mirror`를 복원해 HD로 출력, 이탈 present에 무효화. 버퍼 3개(`g_pause_valid`·`g_pause_expected`·`g_pause_hd`)는 `HeapAlloc` 실패 시 기능만 끄고 훅 설치는 막지 않음. env `SYW2_G1_PAUSE_SNAPSHOT=0`으로 끔(기본 켜짐).
- `tools/inmm_stub/g1_mirror2x.h`: `G1MirrorPresentMetrics`에 `pause_snapshot_pixels`·`pause_restore_pixels`, 접근자 `g1_mirror2x_pause_restore_total()`. `tools/inmm_stub/direct_draw_trace.c`: `mirror2x_present`에 `pause_snapshot_pixels`·`pause_restore_pixels`·`pause_restore_total` 추가(기존 필드 의미 불변). `tools/inmm_stub/Makefile`: 헤더 의존성.
- `tests/test_g1_pause_snapshot.py`(신규 3개): RED 3 failed → GREEN 3 passed(헬퍼 pick/transition 단위, present 루프·trace·버퍼 배선 소스 계약). 하네스 변경 0.

## 실행 (격리 run 3회, 각 `.venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1121_pm2_<r> --artifact-root <공유 temp>/20261007_lap1121_work_hpm2/pm2_<r> --hd-source scale2x --new-game-path --new-game-start --new-game-act --new-game-menu`)
- a·b = 수리 켬, off = 같은 명령에 `SYW2_G1_PAUSE_SNAPSHOT=0`(비회귀 대조). exit a 0·b 0·off **2(FAIL)**. game 사본은 하네스가 run 끝에 지움(run 디렉터리에 `game` 0).
- 새 스크립트 재계산 `recalc_lap1121.py`(공유 temp `20261007_lap1121_work_hpm2/`, SHA `10901863e524…`, 출력 `recalc_{a,b,off}.json`): HD = (covered − stale)/480,000.

| 창(candidate) | a present / HD first·min·p50 / <98.6% / restore 합 | b | off(수리 끔) |
|---|---|---|---|
| pause | 1,253 / 100·99.939·99.939 / 0 / 0 | 1,258 / 100·99.939·99.939 / 0 / 0 | 1,263 / 100·99.939·99.939 / 0 / 0 |
| save_window | 1,644 / 99.939·**99.876**·99.974 / 0 / **51,703** | 1,693 / 99.939·**99.876**·99.974 / 0 / **51,704** | 1,692 / 99.939·**89.105**·99.974 / 1 / 0 |
| pause_return | 1,246 / 99.974·99.879·99.879 / 0 / **96,162** | 1,279 / 99.974·99.879·99.879 / 0 / **96,160** | 1,289 / 99.974·**79.845**·**90.669** / 1,263 / 0 |
| resume | 238 / 99.879·99.879·100 / 0 / 101 | 238 / 같음 / 0 / 101 | 240 / 90.669·90.648·100 / 29 / 0 |

- PS3 행만: resume 창 PS3 211 present min·p50 100%(a·b·off), act 창(select·produce·drag_move·dwell) min 100%·stale 0(a·b·off), pause 창 PS3 1 present 100%.
- 닫힘(저장 창 → 메뉴 복귀) present: PM0 80.0% → **99.876%**(a·b, stale 0), 그 뒤 PS23 정착(a 2,898·b 2,980 present) min 99.876·p50 99.974. 저장 창 열림 present: 89.11% → 99.876%(열림 present에 `pause_restore_pixels` 51,703/51,704).
- V1 outside 0·안전 7종 0·fallback 0·success_min 1·hresult 0·`trace_dropped_count` 0·scale2x validator PASS(a·b), 경과 p95 6~8ms(대조 6~8ms, 증가 0ms), 클릭 3/3·상태 전이 23→23→23→3(a·b·off 동일). 캡처 `pause_return.png` 열람 정상(메뉴 8버튼·띠 지형 HD·깨짐·흑색 띠 0).
- **띠 2×2 균일 비율**(x240..313·x486..559 × y100..409, 완전 균일 2×2 블록 %): pause_return a 76.72·b 77.37, 같은 run의 pause.png 76.72·77.36(= 수리 정상 상태), 수리 끔 99.36. 픽셀 일치율(pause.png ↔ pause_return.png 띠): 수리 켬 99.109%, 끔 93.305%.
- 대조의 공통 기준선: 진입 present(첫 PS23)에 `stale_pixels` 291이 있고 이후 `covered` 479,709 유지 — 수리 끔 run에도 동일(3618: 480000/0 → 3619: 480000/**291** → 479,709). 즉 291 px(0.061%)는 이번 변경 원인이 아닌 act 뒤 PS23 진입의 기존 현상(lap1117 PM0 b는 100%여서 lap1117과 상태가 다름 — 원인 미조사, 이번 수리와 무관한 별건). pause 창 p50 99.939는 이 291 때문이다.

## 판정 — 사전등록 대비(이탈 2건 공개, 판정은 middle)
- **PASS(2/2)**: 닫힘 present HD ≥98.6%(99.876)·정착 PS23 HD min ≥98.6%(99.876)·PS3 복귀 뒤 HD 100%·PS3(act) HD min 100%(≥99.9%)·V1/안전 7종/fallback/hresult 0·dropped 0·scale2x PASS·p95 증가 ≤2ms(0)·저장 창 열림 present HD ≥89%(99.876)·수리 끔 대조가 PM0 결함(79.8%/90.67%/89.1%) 그대로 재현.
- **이탈 1 — `pause_restore_pixels` 닫힘 present 40k~46k**: 관측 **96,162/96,160**(a/b). 사전등록은 띠 약 44k만 예상했으나 복원에는 같은 사유로 가려졌던 **메뉴 패널 영역 약 51.7k**(저장 창 열림 present에서 복원된 값과 같은 크기 51,703/51,704)가 포함된다(96,162 − 51,703 ≈ 44.4k = 띠). 엄격히 읽으면 범위 밖 = FAIL, 원인은 예측 범위 산정 누락으로 보임(추정 — 열림·닫힘 두 present의 51.7k 일치가 근거, 위치 캡처 확인은 안 함).
- **이탈 2 — 거짓 복원 공개(열림·메뉴 구간 합계 0 기대)**: pause 창 0(기대 일치), save_window 창 **51,703/51,704**(전부 저장 창 열림 present 1회, 메뉴 패널 영역 추정, 그 present의 대조 stale 51,704와 일치 → 대조에서 stale이던 픽셀이 복원된 것이므로 값은 스냅샷과 같고 "거짓"일 가능성은 낮음) · resume 창 101(PS23 → PS3 전환 구간, 위치 미확인).
- **띠 균일 ≤10% 판정 불가**: 기준 자체가 달성 불가(수리 정상 상태인 pause.png도 76.7%, 평지·단색 영역은 Scale2x에서도 균일 블록). 같은 run의 pause.png와 pause_return.png 띠가 동률(76.72 vs 76.72 / 77.36 vs 77.37)이고 수리 끔은 99.36이므로 "복귀가 pause 수준"으로 대체 근거만 남긴다. 판정은 middle.
- 공개 한계: 스냅샷 크기 479,709 px(진입 present의 기존 HD 전부, 메뉴 패널 값 포함); 복원은 PS23 한정이고 PS3 경로 바이트 동작 불변(PS3 act·resume 100%); 저장 창 열림 구간 전환 present 일시 stale은 복원으로 사라졌으나 이는 원인(미러 밖 열림 그리기)이 아니라 결과 가림이다. `0x01E6D8F0` writer UNKNOWN 유지. 저장 실행·불러오기 창·옵션 하위 창은 미측정, 부하 대표성 낮음.

## 다음 행동 (middle 검수 요청, `loop/ESCALATE_SOL`)
middle(Opus)이 a·b raw(`trace_raw.jsonl`)에서 닫힘 present의 복원 위치(띠 vs 메뉴 패널 영역)를 독립 재계산해 이탈 1(96k 복원 구성)과 이탈 2(51.7k·101)를 확정하고, 띠 균일 기준을 폐기하거나 다른 기준(픽셀 일치율 99.1%)으로 바꿀지 결정한다. 수용되면 H-PM2 PASS(partial, 기술·격리)로 닫고 다음 남은 HD coverage(승패 화면·타이틀·혼자하기 대기실·옵션 하위 창·PS2 로딩)를 사전등록한다. 위 291 px 진입 stale은 별건 backlog.
