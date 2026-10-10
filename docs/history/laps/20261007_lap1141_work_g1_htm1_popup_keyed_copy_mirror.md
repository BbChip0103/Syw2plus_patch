# 2026-10-07 | lap1141 | G1 work — H-TM1: 사용자등록 팝업 바탕 writer 귀속 → `0x466480` 미러 수리

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. C·하네스·테스트 변경 있음, 커밋 0.
- 입력: STATUS "다음 한 가지"(work H-TM1), lap1140 기록 §4 사양. INBOX 새 사용자 지시 없음(마지막 = lap1140 처리 메모), APPROVALS 새 반려·사용자 시험 결과 없음(lap1136 재요청 대기), `loop/STOP`·`loop/ESCALATE_SOL` 없음(시작 시 확인).
- 가설: 팝업 바탕 writer는 미후킹 단일 함수이고 인자 형태가 분명해 diff 미러로 팝업 정착 HD를 ≥98.6%로 올릴 수 있다.
- 예상 PASS/FAIL: TM1-1 = 바탕 표본 3개 중 2개 이상 같은 writer. TM1-2 = 켬 2회·끔 1회, 정착 HD ≥98.6 PASS·90~98.6 partial·<90 FAIL, 비회귀 scenario 1회 + 기존 장면 1회(안전 0·dropped 0).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만), 모든 run `source_unchanged` true.
- fixture: 없음(타이틀에서 시작, 비합성). 팝업 안 ID 입력/변경/삭제/확인 버튼은 누르지 않았다(사용자 변경 클릭 1회 + 하네스 재시도 클릭은 팝업 밖 좌표).

## 0. 변경 파일

- `tools/inmm_stub/g1_screen_watch.h`(`3880b0025f58`): `G1_SCREEN_WATCH_STATE_PS9 9ul`, 파서에 한 자리 `"9"` 분기 1개(그 밖 값은 기존대로 PS3). TM1-0.
- `tools/g1_saved_scene_probe.py`(`a82a0308fa18`): `--screen-watch-state` choices에 9 추가, `--title-button` 분기가 `layer_drift`·`screen_watch`·`screen_watch_cache`·`screen_watch_state`·`drift_samples`를 후보 lane에 전달, 결과 요약 lane 키에 `layer_drift`·`screen_watch` 추가.
- `tools/inmm_stub/g1_mirror2x.c`(`1b056280f662`)·`g1_mirror2x.h`(`0fc9cc4b1edf`): TM1-2 `0x466480` 후킹(아래 §3). `tools/inmm_stub/direct_draw_trace.c`(`0de218aa84d6`): 트레이스 요약에 `keyed_copy_466480_*` 9개 키, `mirror_details` 버퍼 10240→12288(기존 키 합계가 한계에 가까워 한 줄 추가에 필요; 기존 테스트의 버퍼 크기 문자열 검사도 이 선례대로 갱신).
- `tests/test_g1_screen_watch.py`(`923dd9325397`): 파서 `"9"`·`"90"`·`"09"` 케이스, present ordinal, choices, `--title-button` 분기 배선 테스트 RED→GREEN. `tests/test_g1_rect_fill.py`(`d8e4430db905`): `0x466480` 후킹 표·래퍼 계약 테스트 1개 추가, `mirror_details[12288]` 문자열 갱신. 같은 파일들에 lap1099~1140 미커밋 변경이 이미 있다(이번 회차 변경은 위 구간).

## 1. TM1-0 진단 확장

TDD: 테스트 먼저 RED(3 failed) → 구현 → GREEN(`.venv` 기준 g1 관련 4개 파일 295 passed). 시스템 `python3`는 Pillow 버전 문제로 기존 8개가 실패하므로(`get_flattened_data`) `.venv`를 쓴다(이번 변경과 무관).

## 2. TM1-1 귀속 (격리 1 run, candidate lane screen watch PS9)

명령(`scripts/run_tm1.sh r1 "300,250;270,300;480,400"`, 공유 temp `20261007_lap1141_work_htm1/`): `--hd-source scale2x --title-button user --layer-drift --screen-watch --screen-watch-state 9 --drift-samples "300,250;270,300;480,400"` — 표본 3개 = 팝업 바탕 초상화·왼쪽 띠·오른쪽 아래. 결과 `PASS`(exit 0, 팝업 정착 HD 84.1·stale 76,319, lap1139와 동일).

- screen watch(`r1/candidate/screen_watch.jsonl`, 요약 스크립트 `scripts/tm1_summary.py`): 표본 3개 모두 **같은 두 EIP**만 기록. ① `0x004662DE`(캐시→화면 `0x466280`, 기존 미러 영역) 전 present(0..1548) 표본당 1,549회, ② **`0x004664BF`** 팝업이 열린 present 60부터 매 present 표본당 1,489회, 호출 스택 상단 `0x004C8773 → 0x00495093 → 0x004248C5`(1,515행 전부 동일), 스레드 1개(present 스레드).
- 역어셈블(`i686-w64-mingw32-objdump`, 원본 EXE `0x466480`): thiscall, `ret 0x14`, 인자 5개 `(x, y, w, h, src)`. 목적지 = `[this+0x1514] + y*[this+0x10] + x`, 행 `h`개 × `w`바이트를 `src`에서 연속으로 읽어 `0xFE`면 건너뛰고 나머지를 씀. 클리핑 없음, 인자는 부호 있는 32비트. EIP `0x4664BF`는 `0x4664BD`(`mov [eax],cl`) 쓰기 직후 명령이다. 어느 기존 hook(`0x466070`·`0x465B30`·`0x465E80`·`0x466B50`·`0x4672E0`·`0x467B00` 등) 주소와도 겹치지 않는다.
- **TM1-1 PASS**: 바탕 표본 3/3(기준 2/3)이 단일 writer `0x466480`(호출처 `0x4C8773`, 팝업 프레임 함수 `0x495093` 경유)으로 귀속. 이 함수가 기존 hook에 없었다는 것이 stale의 원인(미후킹).
- 경계 공개: 표본은 바탕 3점뿐이며 팝업 안 다른 writer가 더 있을 가능성은 아래 잔여 871 px로만 상한이 걸린다.

## 3. TM1-2 수리 구현

`mirror_keyed_copy`(`g1_mirror2x.c`, `mirror_flip_blend7` 선례 그대로): 프롤로그 `8B 51 10 / 53 / 8B C2` 6바이트(상대 분기 없음, `install_one`이 기대 바이트 검증 뒤 트램펄린), 인자 5개를 그대로 한 번만 원본에 전달. 화면 교집합(`g1_flip_rle_region`, 32비트 인자·wrap 처리)을 화면 크기 before 복사 → 원본 호출 → `g1_overlay_blt_apply_tiled`로 바뀐 픽셀만 HD로 미러. 목적지가 캐시·패널 바인딩 버퍼면 reject_target, 가드·크기·경계 reject 계수. env `SYW2_G1_KEYED_COPY=0`이면 원본만 호출(기본 켬). 크기 상한은 타일 방식이라 팝업(288×310)도 받는다.

명령: 켬 `scripts/run_tm1_fix.sh on_a|on_b user`, 끔 `SYW2_G1_KEYED_COPY=0 scripts/run_tm1_fix.sh off user`, 비회귀 `scripts/run_tm1_fix.sh scn scenario`·`scripts/run_tm1_ng.sh`(`--new-game-path --new-game-start --new-game-act --new-game-play`, lap1115 NG5와 같은 플래그).

| run | 후보 PS9/PS15 정착 HD(전환 present 제외) | stale | 비고 |
|---|---|---|---|
| 켬 on_a | **99.819** (PS9 1,570 present, 첫 100) | 871 | `0x466480` 호출 1,570 = present 수·mirrored 1,570·reject 0 |
| 켬 on_b | **99.819** (PS9 1,467 present) | 871 | on_a와 동일 |
| 끔 off | 84.100 (PS9 1,713 present) | 76,319 | mirrored 0(호출 1,714) = lap1139와 같은 결함 재현 |
| scenario(비회귀) | PS9 14 present 100·PS15 1,002 present **100** | 0 | 안전 0 |
| new-game(비회귀, PS3) | select/produce/drag_move/dwell 100·scroll_RIGHT 99.998(stale 12)·DOWN/LEFT/UP 100·dwell 100 | ≤12 | NG5 최저 99.966보다 낫다, act 효과 true·쌀 5000→4200 |

- 켬·끔 모두: 안전 7종 max 0·fallback 0·success min 1·`trace_dropped_count` 0·cleanup ok·`source_unchanged` true. scenario 외 켬 2 run의 `state_summary`는 PS9 단일 구간.
- **판정: TM1-2 `PASS`** (정착 HD 84.10 → 99.819 ≥ 98.6, 켬 2/2·끔 대조 재현). 캡처 열람(`on_a/candidate/user_inplace_a.png`): 팝업 바탕·초상화·버튼·글자 정상, 색·위치 오류 없음.
- 잔여 stale 871 px(켬 2/2 동일 상수, 0.18%): 위치·writer 미조사(UNKNOWN). 팝업 안 버튼 hover·커서 모서리로 추정하나 근거 없음 → 기록만.
- DLL: 하네스가 run마다 `build_runtime_bridge.py`로 재조립(r1 `2c5c052acdc3`은 수리 전 빌드, on_a `5e12422bd397`·on_b `24689a19c05c`·off `887e04b94abe`·scn `a4bd5a8729ac`·ng `9d1015ab565f`는 수리 포함, 차이는 PE 타임스탬프). 결과 JSON SHA: r1 `5cfdd2b26812`·on_a `9c557ec3c23e`·on_b `0d47e43e10ef`·off `1013ff705124`·scn `0d9e033653eb`·ng `c41f6c75ddd3`, 로그는 `logs/gates/lap1141-tm1-<run>.{log,exit}`.

## 4. 사건·정정

- off 첫 실행은 Bash 도구 기본 타임아웃(2분)에 걸려 baseline lane에서 중단됐다(exit 143). 산출물은 `off_interrupted_tool_timeout/`·`local/runtime/lap1141_tm1_off_interrupted/`에 보존(그 안 `game` 사본만 삭제), 이후 off·scenario·ng는 `setsid nohup`으로 끝까지 실행했다. 중단 run은 판정에 쓰지 않는다.
- 사전등록의 "표본 run 2 (`450,190`·`460,240`)"는 run 1에서 3/3이 귀속돼 불필요했다.

## 5. 한계·공개

- 사용자 시험(실제 Windows)·종료하기 확인 팝업 `(410,560)`·HQNET·서장 영상·캐릭오픈방은 미측정/BLOCKED(기존 backlog). 팝업 안 ID 버튼은 누르지 않았다.
- `mirror_validator`는 기존 title-button run과 같은 종류의 BLOCKED를 보이며 이 하네스는 게이트에 쓰지 않는다(lap1139 §3 공개와 동일).
- 새 훅이 PS3 등 다른 상태에서 `0x466480` 호출을 새로 미러하게 된다: new-game PS3 구간 HD가 악화되지 않았음(최저 99.998)만 확인했다. save006 pair 비교·24k/144k·장시간 성능은 미측정(다음 시험판 묶음 전 middle이 정한다).

## 다음 행동

middle(Opus): 위 raw 독립 재계산(켬/끔 HD·`0x466480` 호출 수·EIP 귀속·역어셈블)·`0x466480` 훅이 다른 상태 화질/성능에 영향이 없는지 판정 → H-TM1 수용 여부. 수용 시 시험판 묶음에 포함할지(재스테이징은 root 전달 필요) 및 다음 work(종료하기 확인 팝업 `(410,560)` 측정) 결정. 사용자 G1 시험 결과가 오면 최우선.
