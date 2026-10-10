# 2026-10-07 | lap1127 | G1 work — H-RS1 PS27·PS29 stale 위치·writer 귀속(수리 없음)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap.
- 입력: STATUS 다음 한 가지, lap1126 middle 사전등록 §3(H-RS1). INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- 원본 SHA: 읽기만(`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…`), 모든 run `source_unchanged` True, cleanup ok 10/10, game 사본 삭제(`local/runtime/lap1127_hrs1_*`에 `game` 없음).
- fixture: `g7defeat`(lap982 orig `save001.dat` `57872666…`, 타이틀 불러오기 → ps 3→27→29), 실제 저장 파일 사용, 합성 아님.
- 가설 H-RS1: PS27의 92,383 px와 PS29 막대(~7.9k px)는 각각 미러가 따라가지 않는 단일 writer 경로가 그린다.

## 변경 파일(모두 uncommitted, 옵트인 진단 + 하네스)

- `tools/inmm_stub/g1_stale_mask.h`(`eb0096894087`): `g1_stale_mask_state_parse`("23"·"27"·"29" 외 → 3).
- `tools/inmm_stub/g1_mirror2x.c`(`529429696de1`): `SYW2_G1_STALE_MASK_STATE`(기본 3)로 마스크 덤프·ordinal 대상 상태 선택. env가 없으면 PS3 동작 불변(`g_stale_mask_ps3_ordinal`→`g_stale_mask_ordinal`로 이름만 변경).
- `tools/inmm_stub/g1_screen_watch.h`(`dc9fa809882a`)·`g1_screen_watch.c`(`2cf4c2a248ff`): `SYW2_G1_SCREEN_WATCH_STATE` 27·29 허용(3·23 동작 불변), ddraw Blt/BltFast 호출 표를 PS3가 아닌 감시 상태 전반으로 일반화(이전 PS23 한정).
- `tools/g1_saved_scene_probe.py`(`884c5baeda03`): `--stale-mask-state {3,23,27,29}`(`--stale-mask` 필요)·`--screen-watch-state {3,23,27,29}`, `--result-screen` lane에 stale mask·layer drift·screen watch·drift samples 배선(candidate 전용), PS27 캡처 `ps27_early`(0.3초)·`ps27`(2초)·`ps27_late`(5초), 결과 요약에 `stale_mask`·`screen_watch`.
- 테스트(RED→GREEN): `tests/test_g1_mirror2x.py`(`ffb2f3a1ee12`)·`tests/test_g1_screen_watch.py`(`71b99a749202`)·`tests/test_g1_result_screen.py`(`9a2e50106a1a`) — parse 경계(미지정·잘못된 값→3), 3/23 불변, 하네스 배선·PS27 캡처 시점. 관련 3 파일 70+ passed, `make lint`·`make typecheck` PASS.

## RS1-1 위치(격리 run m27·m29, `--hd-source scale2x --fixture g7defeat --scene-actions none --result-screen --stale-mask … --stale-mask-state 27|29`)

공유 temp `20261007_lap1127_work_hrs1/{m27,m29}/`. 분석 스크립트 `rs1_mask.py`(`62a8d8b08957`)·`rs1_mask2.py`(`aeae999f9de9`) → `rs1_mask.json`(`195c4fc405ec`)·`rs1_mask2.json`(`892cf6ed8bfb`).

- 진단 켬이 HD 수치를 바꾸지 않음(2/2): PS27 HD 80.754%·stale 92,383, PS29 min 98.36%·stale 7,874, 탭 병사 98.36/건물 99.171/자원 99.171, 확인 뒤 PS9 100%, V1 outside·안전·fallback 0, trace dropped 0, scale2x PASS, `status` FAIL(기준 미달, lap1125와 같음).
- **PS29 (state 29, ordinal 5·60·150)**: stale 432 → 4,274 → 7,874, bbox x199..346 → 401 → 452·y189..244, **mask 100% 막대 상자(x199..452·y189..244) 안**, 행 36개(18행×2줄)·열 12 → 122 → 224(막대 길이 +1열/present, 72 = 4막대×18행 — lap1126 귀속 재확인).
- **PS27 (state 27, ordinal 0·1·200)**: ordinal 0 stale 92,383(전 화면 bbox x0..799·y4..599, 277행), **ordinal 1·200은 stale 0·covered 387,617** = 같은 92,383 px가 첫 PS27 present에서 stale 판정된 뒤 영구 uncovered(두 덤프의 uncovered 집합 동일, ord0 stale 집합 = 이후 uncovered 집합). 위치 = **하단 HUD 전체(패널·F1~F11 칸·미니맵·주민 상자)+우측 로고+손 커서+상단 자원 글자**(`m27_uncovered_ord1.png`).

## RS1-2 writer(격리 run w27·w29, `--layer-drift --screen-watch --screen-watch-state 27|29 --drift-samples …`)

공유 temp `{w27,w29}/candidate/screen_watch.jsonl`(`9e83cc59b18b`·`5d468385b815`), 분석 `rs1_watch.py`(`bd46fbe07cc3`). 표본: PS27 HUD 3점 (450,565)·(400,540)·(670,520)(모두 uncovered·baseline 비검정 확인), PS29 막대 3점 (230,197)·(370,235)·(260,235).

- **PS29**: 막대를 그리는 writer = **게임 미후킹 함수 `0x468BB0`(`ret 0x28`, 행 단위 `rep movsl/movsb` 사각형 복사 루프, EIP `0x468C01`·`0x468C03`·`0x468C08`·`0x468C0A`)**. 원본 EXE 바이트를 읽기 전용 디스어셈블로 확인. 배경 전면 복사는 기존 `0x4662DE`(G1_CACHE_COPY `0x466280` 안, 매 present 3슬롯 1,280회). 막대 EIP hit 1,685(raw 5,528의 30%)이고 (present, 슬롯)별 마지막 writer 중 막대 함수 비중은 55.5%(슬롯별 37~73%)로 **사전등록 ≥90%는 미달**(hardware watch가 같은 present의 두 writer 중 일부만 기록하는 것으로 보이며 hit 유실 원인은 미확정). 함수 정체(미후킹 사각형 복사)는 EIP·디스어셈블로 명확하다.
- **PS27**: 감시 상태 27에서 HUD 표본 3점에 대한 **hit 0**(k 요약 p=999까지 raw 0). hit은 PS27 맨 끝(p=1035, PS29 진입 직전)의 전면 재그림(`0x4662DE` 4,017·`0x466E67` 266·`0x465994` 3)뿐이다. 즉 **HUD가 사라지는 변화는 감시가 무장하는 첫 PS27 present 이전(PS3→PS26→PS27 전환 프레임)에 일어났거나 렌더러 버퍼 쓰기가 아니다 → writer UNKNOWN**. ddraw 호출 표: PS27에는 전면 BltFast(호출처 `0x469379`, 표면 한 쌍, 1,000회/999 present) 단 한 항목, HUD BltFast 없음.
- 추가 증거(candidate trace, m27): PS3 present는 원본 back buffer(`0x01E75330`, desc 832×600, caps 2112)를 쓰고 HUD는 매 프레임 `BltFast(src 0x01E75200 → back (0,440) 800×160)`로 그린다(호출처 `0x0041C60C`). **PS27 present는 다른 표면 `0x01E71788`(desc 1600×1200, caps 2076, source rect NULL, gate variant 2, PS9 타이틀과 같은 표면)**에서 온다. PS26 한 present에서 primary `0x01E6FF70`가 release(keep)된 뒤 PS27이 시작한다. PS3 마지막 present(seq 1067) → PS27 첫 present(seq 1070) 사이에 `create_surface`·`set_display_mode`는 없다(마지막 생성은 seq 903 PS35).

## 새 발견: PS27은 PS29 막대보다 훨씬 큰 가시 결함(lap1126 "시각 심각도 낮음" 판단은 PS29에 한정)

- 캡처 c27(`--result-screen`, 진단 없음, 공유 temp `c27/`; baseline 비교는 이 run 1회): 하단 HUD(y440..600 영역)의 비검정 픽셀(>16) 수 — baseline **72,277**(0.3·2·5초 모두 동일) vs candidate **164**(0.3·2·5초 모두). 후보 `ps27.png`와 `ps27_late.png` 해시 동일(`c658e289fdc1`), `ps27_early.png` `2b91ff4d9371`, baseline `ps27.png` `f8e0cd5e2bd5`.
- 즉 **후보(1600×1200)에서 패배 배너가 뜨는 약 8초(PS27) 내내 하단 HUD·미니맵·F키 칸·우측 로고·손 커서가 검게 사라지고**(상단 자원 글자와 배너는 보임), 원본은 HUD가 그대로 보인다. 원인은 HD vs nearest 화질이 아니라 **PS27 present의 소스 표면에 그 내용이 없는 것**(destination은 nearest(source)와 99.2% 일치). stale mask(첫 present 92,383 → uncovered)는 이 내용 변화를 보고하는 계기판이다.
- 판정 조치: 사전등록 기준(PS27 HD ≥98.6%)은 그대로 유지한다. 이번 증거는 PS27을 "측정 지표" 문제가 아니라 **실제 가시 결함(원본 대비 회귀)**으로 격상한다.

## 판정

- **RS1-0 PASS**(옵트인 진단+테스트+하네스). **RS1-1 PASS**(PS27·PS29 위치 확정, 진단 켬 HD 수치 재현, V1/안전/fallback/dropped 0).
- **RS1-2: PS29 PARTIAL**(미후킹 함수 `0x468BB0` 확정, ≥90% hit 귀속은 미달), **PS27 BLOCKED**(writer UNKNOWN, 감시 hit 0 — 변화가 무장 이전/비-write). 실패 가설 1회(PS27 writer 감시)·실행 시간 약 1시간.
- **RS1-3 수리 미실시**: PS29는 새 writer 함수 hook(`0x468BB0` 미러, 기존 block copy 계열과 유사한 사각형 복사 → FEASIBLE 후보)이 필요해 사전등록대로 귀속만 넘긴다. PS27은 원인이 확정되지 않았다.
- 미검증: PS27 소스 표면(`0x01E71788`)을 원본이 채우는 방식(baseline ddraw 호출 순서; baseline lane trace는 256 이벤트에서 끊겨 PS27 호출이 없음), 승리 화면, PS29 마지막 present stale 478,002(backlog).

## 공개 한계·정정

- lap1126 §2(2) "PS27 화면 정체 UNKNOWN"을 이번 캡처로 해소: HUD 소실. 후보 `ps27.png`의 하단 HUD 비검정 픽셀(>16)은 **5 run(m27·m29·w27·w29·c27) 모두 164**로 동일하게 재현(진단 켬/끔 무관), baseline은 c27 기준 72,277.
- 내 중간 가설("PS26 display mode 재생성으로 이전 프레임 소실")은 trace에 `set_display_mode`·`create_surface`가 전환 구간에 없어 **철회**했다. "원본이 primary 보존에 의존한다"는 미검증 가설로만 남긴다.
- PS29 hit 유실(막대 hit 비중 55%)의 원인은 미확정이다(hardware write watch의 같은 present 내 다중 writer 기록 한계로 추정). 함수 귀속은 디스어셈블+EIP로 확정이라 필요 시 ddraw 호출 표 없이도 된다.

## 실행·검사

- 명령(동기, 로그 `logs/gates/lap1127-hrs1-{m27,m29,w27,w29,c27}.log`·`.exit`=2(기준 미달 FAIL 판정 종료코드, lap1125와 같음)): `PYTHONPATH=. .venv/bin/python tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1127_hrs1_<n> --artifact-root <공유 temp>/<n> --hd-source scale2x --fixture g7defeat --scene-actions none --result-screen [--stale-mask <ord> --stale-mask-state <27|29>] [--layer-drift --screen-watch --screen-watch-state <27|29> --drift-samples "<X,Y;X,Y;X,Y>"]`. 스크립트 `run_mask.sh`·`run_watch.sh`·`run_cap.sh`(공유 temp). 결과 JSON `result-screen-result.json` 해시: m27 `63dc9b8c1833`·m29 `b5b2788ad533`·w27 `34f1a5f76f7d`·w29 `7a8d524a7004`·c27 `e6931c21d6d6`.
- 마스크 `m27/candidate/stale_mask.bin` `958d9835dfbd`·`m29/…` `995824ae2d1b`, trace `m27/candidate/trace_raw.jsonl` `64860af3f4c0`.
- 디스크 여유 145GiB. 커밋 0, 시험판 재스테이징 없음.
- 전체 `make check`는 기록 freeze 뒤 1회(결과는 STATUS).

## 다음 한 가지

middle(Opus): ① PS27을 PS29보다 우선하는 **가시 결함**으로 확정하고, 원인 후보(전환 프레임에서 `0x01E71788`로 가는 복사/채움 경로, baseline 호출 순서 대조)를 정해 work H-RS2(전환 구간 ddraw 호출 표·소스 표면 덤프)를 사전등록, ② PS29는 `0x468BB0` 미러 hook(FEASIBLE 후보)을 PS27 뒤로 둘지 결정.
