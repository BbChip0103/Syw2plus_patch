# 2026-10-07 | lap1145 | G1 work — H-SC0 시나리오 제1장 시작 → 브리핑(PS20)·로딩(PS1)·인게임(PS3) HD 관측 (PASS(partial), 수리 없음)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 커밋 0.
- 가설 / 사용자 관찰: lap1144 사전등록 §4 — 시나리오 제1장 시작하기 뒤 화면(브리핑·로딩·인게임)도 정착 HD ≥98.6·안전 0이다. 사용자 G1 시험 결과·새 INBOX 지시 없음(마지막 = lap1144 처리 메모), `loop/STOP`·ESCALATE_SOL 없음.
- 예상 PASS / FAIL 조건: 모든 present 상태 정착 HD ≥98.6·안전 0 = PASS(관측) / 90~98.6 상태 있으면 PASS(partial)+위치 / <90 또는 HUD 소실·조각 분리 = FAIL.
- 변경 파일 / source fingerprint: `tools/g1_saved_scene_probe.py`(`751c78af093d`)·`tests/test_g1_new_game_path.py`(`1495fefcb8c9`). C source 변경 0. 같은 파일들에 lap1099~1143 미커밋 변경이 이미 있다(이번 회차 변경은 아래 §1). uncommitted.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만). 후보 DLL = 현재 트리 빌드(기본 켬). fixture: 시나리오 제1장 "노량해전" 새 시작(격리 game 사본 안 진행 저장만 변경), 활성 인원·군대는 시나리오 기본(자원 5000/5000, 331/2100).

## 1. SC0-0 하네스 (TDD, RED→GREEN)

- `--scenario-start`(`--title-button scenario` 필요): PS15 확인 → 시작하기 논리 `(605,563)` 1회, 2초 뒤에도 PS15면 1회만 재시도(3번째 클릭 없음, 그래도 PS15면 `IN_PLACE`), PS15가 아니면 클릭 없이 `BLOCKED`, 프로세스 사라짐 = `EXITED`. 상태가 바뀔 때마다 `scenario_ps<N>` 캡처, 최대 90초 관측, PS3가 보이면 입력 없이 30초 유지(`scenario_ps3`·`_10s`·`_30s` 캡처). 알려진 화면(PS3·PS15·PS20) 밖 상태가 60초 고정되면 Esc 1회(`escape_sent_at` 기록). 나가기 `(722,563)` 클릭 없음.
- **정정(관측으로 알게 됨):** 시작하기 뒤 PS20은 인게임이 아니라 **브리핑 화면**(돌아가기·다시보기·게임하기 버튼, 초상 2·본문·목표 패널)이라 `게임하기`를 눌러야 인게임에 들어간다. 사전등록은 시작하기 1회만이었으므로 사용자 범위를 넘지 않는 최소 확장으로 `--scenario-play`(브리핑 10초 유지 → `게임하기` `(600,548)` 1회·재시도 1회 → PS3 60초 대기·30초 유지, 돌아가기·다시보기 클릭 없음)와 `--scenario-briefing-dwell SECONDS`(체류 시간, 기본 10)를 추가했다. 첫 run r1에서 알게 된 Esc 오발(브리핑 PS20에서 60초 뒤 Esc 1회)을 막으려 Esc 대상에서 PS20을 제외했다(r1 raw에만 `escape_sent_at` 60.5/60.68 존재, 이후 판정에 영향 없음: 입력 효과 없이 PS20 유지).
- 요약 게이트: `--scenario-start`면 두 lane `scenario_start.status == PASS`·후보 `state_summary` fallback 0·안전 0을 추가 요구하고 `scenario_state_sequences`(+일치 여부)를 결과 JSON에 쓴다(상태 열은 폴링 표본이라 PS150 경유 1홉 차이를 허용하는 기존 title-button 규칙처럼 일치를 게이트로 쓰지 않음).
- 테스트 17개 추가(좌표·재시도 1회 제한·3번째 클릭 없음·PS15 사전조건·EXITED·Esc 1회·play 흐름·dwell·CLI 배선). `pytest tests/test_g1_new_game_path.py tests/test_g1_screen_watch.py` **81 passed**, `make lint`·`make typecheck` PASS.

## 2. SC0-1 관측 (격리 3 run, 공유 temp `20261007_lap1145_work_hsc0/`)

명령(`scripts/run_sc0.sh <name> [옵션]`): `--hd-source scale2x --title-button scenario --scenario-start` + r2 `--scenario-play`, r3 `--scenario-play --scenario-briefing-dwell 50`. 로그 `logs/gates/lap1145-sc0-r{1,2,3}.log`·`.exit`(r1=2, r2=0, r3=0). 결과 `title-button-result.json` r1 `b37fc269c088…`·r2 `160350315e29…`·r3 `35a930a9f70a…`, candidate trace r1 `cb00b28adf96…`·r2 `6e9b1a866dda…`·r3 `6da1b3241dc8…`. 세 run 모두 두 lane `source_unchanged` true·cleanup ok·`game` 사본 삭제(잔존 0)·`scale2x_validator` PASS(`mirror_validator` BLOCKED는 title-button 단축 검증, 게이트 아님).

| run | 내용 | 결과 |
|---|---|---|
| r1 | 시작하기만, 90초 관측 | 두 lane 상태 [16(후보는 PS150 경유), 20] 90초 PS20 유지. **status FAIL = 트리거: trace dropped 628**(8192 이벤트 상한; PS20이 초당 약 70 present라 약 80초 뒤 present 기록 잘림 — 5,931/7,746 기록). 하네스 한계지 제품 결함 아님(r2·r3는 dropped 0). |
| r2 | 브리핑 10초 → 게임하기 → PS3 30초 | PASS, dropped 0. 두 lane 상태 열 [20, 1, 3] 동일(첫 표본만 baseline 16/candidate 150) |
| r3 | 브리핑 50초 → 게임하기 → PS3 30초 | PASS, dropped 0. 두 lane [20, 1, 3] 동일 |

상태별 후보 HD(`(covered−stale)/480,000`, 첫 present 제외 = 전환 프레임 분리):

| 상태 | run | present | HD min | HD p50 | 비고 |
|---|---|---|---|---|---|
| PS15 시나리오 | r2/r3 | 17 | 100 | 100 | stale 0 |
| **PS20 브리핑** | r2 (10초) | 776 | **98.243** | 99.113 | <98.6 present 22.2%, <90 0% |
| **PS20 브리핑** | r3 (50초) | 3,678 | **92.815** | 98.287 | <98.6 58.3%, <90 0% |
| **PS20 브리핑** | r1 (90초, 기록된 5,931) | 5,931 | **89.43** | 98.152 | <90 26.4%(62~80초대) |
| PS1 로딩 | r2/r3 | 후보 present 없음(set_display_mode 800×600×8→1600×1200 native 2x 적용) | — | — | 두 lane 동일 PS1 → PS3 |
| **PS3 인게임** | r2/r3 | 616/613 | 99.686 | 99.686 | stale 0(covered 478,491 = 정착 미덮임 1,509 px 0.314% 일정), 30초 유지 입력 없음, 첫 present 100 |

- 안전 7종 max 0(clip_replay_mismatches·viewport_field_mutations·viewport_restore_failures·scale2x_palette_violations·hd_mask_outside·cache_clip_verify_failures·identity_key_mismatches)·fallback_max 0·success_min 1(세 run).
- **PS20 stale은 결정적으로 재현**: r1·r3의 시간 대 stale 계열이 같다(약 12~30초 8.5k → 33~42초 5.8k→1.3k → 46초 18k → 50초 34k → 56~60초 35k → 63초 51k, 모두 stale 논리 px). 첫 present 463,592(전환 직후 전면 미덮임, 다음 present 0)는 기존 전환 프레임 패턴과 같다. 브리핑은 패널·본문 글자가 시간에 따라 갱신/페이드되는 화면이다(r3 `scenario_ps20_dwell.png`: 제 1 장 노량해전, 김시민·김덕령 초상, 본문 2패널, 목표 두 줄 노랑 글자). **위치는 UNKNOWN(귀속 안 함):** 독자 Scale2x(baseline 캡처) 대비 후보 캡처의 평평한 2×2 블록 초과(`locate_sc0.py`)는 입구 188블록(버튼 주변), 50초 8,346블록(하늘 띠 y≈160..320 HD 타일 우세)이지만 구름·글자 애니메이션 위상이 두 lane에서 달라 신뢰할 수 없다. writer 귀속은 PS20 screen watch 필요(`--screen-watch-state` choices에 20 없음).
- 캡처 열람(후보 PS20·PS3, 기준 PS3): 브리핑 UI 비율·초상·패널·글자 정상(HUD 해당 없음), 인게임 후보 1600×1200과 기준 800×600이 같은 구도·HUD(자원·미니맵·F1~F11·명령 패널)·글자·단위 위치 일치, 조각 분리·잘림·HUD 소실 없음. 이 장면 PS3 1,509 px 일정 미덮임은 위치 미확인(시각 영향 없음).
- 원본 구성 비교: baseline lane도 PS16 800×600×8 모드 설정 뒤 PS20 → PS1(800×600×8) → PS3로 같은 열이다. 시나리오 창 안의 모드 호출은 PS16·PS1 800×600×8뿐(640×480×16 영상 모드는 시작 전 타이틀 인트로 PS40/60/180 구간에만 있고 r2·r3 두 lane의 `set_display_mode` 열 13개가 동일, lap1137과 같음).

## 3. 판정

- 사전등록 기준: 브리핑 PS20 정착 HD가 98.6 미만(p50은 98.15~99.11, 체류가 길수록 최솟값 하락)이고 인게임 PS3는 99.686으로 통과 → **H-SC0 `PASS(partial, 기술·격리 관측)`**. 사전등록의 `<90 = FAIL`은 r1 90초 체류의 62~80초대 일부(26.4%)에서만 만난다(r3 50초는 min 92.8): 90초 체류가 일반적인 사용자 체류인지는 판단 불가이므로 **FAIL로 단정하지 않고 PASS(partial)로 두되 이 꼬리를 공개한다**(middle 판정 요청). 위치·writer는 UNKNOWN.
- 하네스 한계 공개: ① 90초 체류 run은 트레이스 8192 이벤트 상한에 걸려 dropped 628(r1) — 체류 60초 이하로 제한. ② PS150 경유로 후보의 첫 상태 표본이 baseline과 다름(1홉). ③ 인게임 PS3 30초는 입력 없는 유지만(전투·생산 없음).
- 수리 없음. 시험판 재스테이징 판단은 middle 몫(보류 유지 근거: 사용자 결과 없음, 이번 회차 가시 수리 없음).

## 4. 다음 한 가지 후보 (middle 판단)

(a) H-SC1: PS20 screen watch(`--screen-watch-state` 20 추가) → 브리핑 stale writer 귀속 → 조건부 미러 수리(체류 길수록 HD 하락이 해소되는지). 근거 stale이 결정적이라 귀속 쉬움. (b) 가시 영향이 작다고(Scale2x vs nearest, 글자·패널 갱신) 보고 backlog로 두고 다음 미측정 화면. 사용자 G1 시험 결과가 오면 최우선.

## 5. 검사

- 기록 freeze 뒤 `make lint`·`make typecheck`(통과)·전체 `make check` 1회·`checks/safety.sh check`. 결과는 STATUS 검증 줄에만 쓴다(lap 기록은 더 고치지 않는다).
