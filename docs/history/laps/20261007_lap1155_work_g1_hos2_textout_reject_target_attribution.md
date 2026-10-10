# 2026-10-07 | lap1155 | G1 work — H-OS2 PS5·PS7 GDI 글자 대상 거부(TextOutA `reject_target`) 귀속 → 조건부 수리 1회

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 입력 = STATUS "다음 한 가지" + lap1154 middle 사전등록 §7. INBOX 새 사용자 지시 없음(마지막 = lap1154 처리 메모, 18:48 철회 항목은 루프 범위 밖), APPROVALS 새 반려·사용자 G1 시험 결과 없음, `loop/STOP`·`loop/ESCALATE_SOL` 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…8ac` 직접 재계산 MATCH, 모든 run의 baseline·candidate lane `source_unchanged: true`, pair `execution_source.unchanged true`. 원본/참고 쓰기 0, 커밋 0.
- 가설(사전등록): PS5·PS7 GDI 글자 stale은 TextOutA hook의 렌더러 대상 판정(`reject_target`)에서 거부된 호출 때문에 생기고, 거부 DC의 대상은 (i) 화면 메모리·(ii) 나중에 화면으로 1:1 복사되는 화면 밖 버퍼·(iii) 그 밖 중 하나로 귀속된다.
- fixture: `--new-game-path`(타이틀→PS7→PS5, 메뉴 화면, 부하 대표성 낮음), NG5 플래그, 비합성 save006 pair.

## OS2-0 진단 (TDD RED→GREEN, 옵트인)

- `tools/inmm_stub/g1_mirror2x.c`(`96e632a55e55`): `textout_reject_target_note`(거부 시 호출) — 프로그램 상태별 계수(`..._ps5/ps7/other`)와 DC 대상 분류 계수(`..._dc_screen`·`dc_buffer`·`dc_other`) 상시 집계, `layer_drift`가 켜졌을 때만 상태 5·7 각 최대 4,096줄 `{"t":"tx",…}` 로그(렌더러 buffer/stride/height + `GetCurrentObject(OBJ_BITMAP)`/`GetObjectA`로 얻은 DC bits·폭·높이·stride + 마지막 present 화면 포인터 `scr`). `g_last_present_screen`은 present의 소스 `Lock` 포인터. 기존 키 불변, 새 요약 키 `textout_iat_reject_target_{ps5,ps7,other,dc_screen,dc_buffer,dc_other}`(`direct_draw_trace.c` `b13c786827de`·`g1_mirror2x.h` `01960b2f0ffb`).
- 사전등록 이탈 1: 로그 상한을 64→**4,096줄/상태**로 올렸다. 첫 64줄이 전부 초기 PS7 호출로 소진돼 PS5를 못 봤다(d1), 512도 모자라(d2) 4,096으로 전수를 얻었다(d3). 옵트인 진단이라 기본 경로 영향 없음(d1~d3 모두 기준값 재현).
- 테스트: `tests/test_g1_rect_fill.py`(`e2c1ab413aa8`) `test_textout_reject_target_diagnostic_is_opt_in_and_state_split`·`test_textout_screen_dc_target_is_accepted_with_default_on_env_gate` RED(각 1 failed) → GREEN, 파일 34 passed.

## OS2-1 귀속 (격리 d1·d2·d3, 공유 temp `20261007_lap1155_work_hos2/`) — **FAIL(≥60% 미충족)**

- d3(전수 로그) 거부 계수: PS5 2,614·PS7 2,093(`other` 0). DC 분류: **`dc_buffer` 3,242(69%)** = DC bitmap bits가 렌더러 buffer(357×248, stride 360)와 같은 **화면 밖 버퍼**, **`dc_screen` 1,465(31%)** = DC bits가 마지막 present 화면 포인터와 같은 **화면 자체**(1600×1200, stride 1600), `dc_other` 0.
- `dc_screen` 사각형(x−1..x+cx+1, y−1..y+cy+1)과 캡처 stale(독자 Scale2x 판별, `scripts/os2_overlap.py`): **PS5 stale 2,426 px 중 277 px(11.4%)**·PS7 798 중 135(16.9%). 사전등록 기준 ≥60%에 크게 못 미친다. 고유 사각형은 PS5 7개(옵션 이름 `x215,y123/148/175/200/225/252/280`)·PS7 소수뿐이다.
- `dc_buffer` 사각형은 전부 원점 (0,0)/(1,1) 그림자 쌍 20개(PS5, 너비 21~140)다 — 지도 목록 한 줄씩을 357×248 스크래치에 그려 두는 패턴(줄당 89 present = 호출 수 일치). 화면 위치는 알 수 없어 스크래치 오프셋을 전수 탐색(`os2_panel_offset.py`)했으나 최대 겹침 PS5 9.1%(221 px)·PS7 38.2%(305 px)로 귀속되지 않았다.
- 화면에 보이는 PS5 stale 위치(캡처 `d3_ps5_stale_big.png`): 지도 목록 글자(x445~590,y110~285)·옵션 값 버튼 글자·자리 버튼 글자·사용자 줄·확인/취소 — `dc_screen` 사각형 밖이 대부분이다. 지도 목록은 스크래치에서 화면으로 **미식별 복사**로 옮겨진다: 같은 run에서 `keyed_copy_466480_invocations` 0이고 invocation이 있는 후킹은 `rect_solid_465E80` 1,872·`tinted_rle_466ea0` 568·`cache_fill_465FC0` 1뿐이라 복사 writer는 기존 후킹 밖(UNKNOWN). 따라서 (ii)로 확정하지 못했고 사전등록상 (iii) 쪽(BLOCKED 보고)이다.
- 판정: 가설 "stale ≈ 거부된 TextOutA" **반증** — 31% 거부는 화면 DC지만 그 사각형은 stale의 일부(11~17%)만 덮고, 69%는 화면 밖 스크래치다.

## OS2-2 수리 1회 — `dc_screen` 부분만(기본 켬, `SYW2_G1_TEXTOUT_SCREEN_DC=0` 끔)

- 귀속 기준은 못 채웠지만 `dc_screen`은 DC bits = 화면 포인터라는 직접 증거가 있어 (i)의 최소 확장만 구현했다(스크래치 쪽 (ii)는 복사 writer 미식별이라 시도하지 않음). `textout_screen_dc_target`: 렌더러 바인딩 검사가 거부했을 때만 DC bitmap bits가 마지막 present 화면과 같고 `bmWidthBytes`∈[800,2048]·`bmHeight`≥600이면 그 buffer·stride를 대상으로 받아들인다(`g_textout_screen_dc_calls` 계수, 요약 키 `textout_iat_screen_dc_calls`). 기존 바인딩 통과 경로는 그대로다.

## 측정 (공유 temp `os2_measure.json`, 정착 = present 후반부)

| run | env | PS5 정착 HD min / stale max | PS5 캡처 nearest | PS7 HD min / stale max | PS7 캡처 nearest | `dc_screen` rejects / `screen_dc_calls` |
|---|---|---|---|---|---|---|
| f1 | `=0`(끔) | 98.801 / 5,754 | 2,426 | 99.627 / 1,790 | 798 | 1,452 / 0 |
| e1 | 켬 | **98.949** / 5,044 | **2,305** | **99.709** / 1,398 | **744** | 0 / 1,482 |
| e2 | 켬 | **98.949** / 5,044 | **2,305** | **99.709** / 1,398 | **744** | 0 / 1,471 |

- 끔(f1)과 진단 d1~d3은 lap1153 기준값(PS5 98.801/2,426·PS7 99.627/798)을 정확히 재현한다. 켬은 PS5 nearest 블록 −121(**−5.0%**)·PS7 −54(−6.8%), PS5 stale/present −710 px, PS9 100(3 run). **판정: 사전등록 측정식 `FAIL`**(PS5 nearest ≥10% 감소 미달, ≥50%는 멀다; PS5 HD min 98.949 < 99.5). 수리 자체는 의도대로 동작한다(`dc_screen` 거부 0·화면 DC 호출 약 1,470개를 미러).
- 비회귀: save006 full pair 1 run(`pair`, exit 0, pair-result `06aa1a8a0597`) `status PASS`·`scene_state_equal true`·baseline·candidate·input_effect·minimap parity·loaded_capture·V2·V2s·V2q·Scale2x gate 전부 PASS·`execution_source.unchanged true`(lap1153 pair와 같은 판정). NG5 플래그 3 run(켬 ng5·ng5b, 끔 ng5off): PS3 present 2,978/3,050/2,977개, HD min 99.949/**100**/99.943, hresult 0·fallback 0, Scale2x PASS(mirror validator BLOCKED는 lap1115·1153과 같은 원인). ng5의 PS3 단발 stale 8개(16~247 px)는 다음 present에서 해소되는 일시 stale로, 끔 대조(ng5off)에도 1개(274)가 있고 같은 켬의 ng5b는 0개 → run 변동으로 판단, 이 수리와 무관(원인 미규명이므로 UNKNOWN을 숨기지 않고 공개).

## 공개 사항 / 한계

- 이 수리의 가시 효과는 매우 작다(PS5 −5%·PS7 −7%). 남은 PS5 stale 2,305의 주원인은 **화면 밖 스크래치에 그린 글자(지도 목록 20 고유 사각형 + 다른 버퍼 호출)가 미식별 writer로 화면에 옮겨지는 경로**다 — 다음 단계는 PS5 writer 귀속(screen watch를 PS5 진입 뒤 arm하는 하네스 수리, 또는 스크래치→화면 복사 함수 정적 식별)이다. 이 둘은 이번 work 범위를 넘는 새 가설이라 시작하지 않았다.
- `--screen-watch-state 5` 하네스 barrier 타임아웃(backlog)은 그대로다. 로그 상한 이탈 1건(위 OS2-0).
- 변경 파일(전부 uncommitted): `tools/inmm_stub/g1_mirror2x.c`·`g1_mirror2x.h`·`direct_draw_trace.c`, `tests/test_g1_rect_fill.py`. 스크립트(공유 temp `scripts/`): `run_ng.sh`·`run_ng5_pair.sh`·`os2_measure.py`·`os2_stale.py`·`os2_overlap.py`·`os2_panel_offset.py`.
- 실행·정리: 후보 DLL = 매 run harness가 현재 트리로 재빌드(e1 `70618a8280b1`·e2 `7acd260d0a6b`·f1 `c2a825565e37`·pair `62a0b5e88a8f`·ng5b `1f7eacf6e4d3`, PE 타임스탬프/체크섬만 달라지는 동일 소스). run 뒤 `local/runtime/lap1155*/game` 0개, 디스크 여유 51G(≥20G), 원본/참고 쓰기·`260921_temp`·APPROVALS 쓰기 0.
- 로그: `logs/gates/lap1155-os2-{d1,d2,d3,e1,e2,f1,pair,ng5,ng5off,ng5b}.log`/`.exit`(ng5 첫 시도는 인자 오류로 exit 2 → 올바른 인자로 재실행).

## 다음 행동

middle(Opus) 검수: raw 새 스크립트 재계산(특히 `dc_screen` 겹침 11.4%·스크래치 20 사각형 해석), 독립 재조립, 판정(OS2-1 FAIL·수리 PASS(partial 미달=FAIL 측정식, 기능 정상)) 확인과 다음 방향 결정 — (a) 스크래치→화면 복사 writer 귀속(PS5 screen watch arm 하네스 수리 또는 정적), (b) 이 방향 중단하고 다른 G1 잔여(backlog)로 이동. INBOX 2026-10-07 19:3x 사용자 지시(G1 HD 그림 경로, 순서 ①~⑥)는 "현재 H-OS2 뒤 다음 middle이 사전등록"이라 H-OS2가 끝난 이 시점의 다음 middle이 ① 원본 추출 도구를 사전등록한다(이 work는 그 지시 이전 사전등록을 그대로 수행했고 새 지시는 읽기만 했다). 사용자 G1 시험 결과가 오면 최우선.
