# 2026-10-07 | lap1139 | G1 work — H-TM0: 타이틀 메뉴 미측정 버튼 4개(시나리오·사용자변경·캐릭오픈방·서장) 화면 HD 관측

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 하네스·테스트 변경 있음(C 변경 0, 수리 0).
- 입력: STATUS "다음 한 가지"(work H-TM0), lap1137 기록 §3 사양 + lap1138 기록 §3 보강(캐릭오픈방 마지막·외부 접속 가드·좌표 캡처 확인). INBOX 새 사용자 지시 없음(마지막 항목 = root 12:53 전달 완료·루프 재개), APPROVALS 새 반려 없음, `loop/STOP`·`loop/ESCALATE_SOL` 없음(시작 시 확인).
- 가설: 타이틀 메뉴 네 버튼 화면 중 일부는 미러 경로 밖이다(PS35 9.4% 선례). 관측만 한다.
- 예상 PASS/FAIL: lap1137 §3 — 네 버튼 모두 두 lane에서 상태 변화·같은 상태 열·lane별 캡처 2장 이상·안전 0, 새 상태를 HD OK(≥90%)/수리 후보로 분류. 수리 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만), 모든 run `source_unchanged` true. 후보 DLL = 현재 트리 빌드(C·Makefile 변경 0, lap1133 full PASS 1786 이후 C source 불변), 시험판 DLL `6cbb12ac…`과 별개 산출.
- fixture: 없음(타이틀에서 시작, 비합성). 같은 저장 파일은 run마다 private game 사본에만 복사. 활성 플레이어·지도·군대 해당 없음.

## 0. 변경 파일

- `tools/g1_saved_scene_probe.py`(최종 `b8fa67498b0c`; 최종 4 run은 `1227e1f99fea` 소스, 아래 §6): 옵트인 `--title-button {scenario,user,charroom,prologue}`(`--hd-source scale2x` 필요, `--census-only`·`--new-game-path`·`--result-screen`·`--terrain-scroll`과 병용 불가). `TITLE_BUTTONS`(논리 좌표 시나리오 `(75,505)`·사용자변경 `(190,505)`·캐릭오픈방 `(410,505)`·서장 `(75,560)`), `_title_button_window`(1회 클릭 → 첫 1초 0.05 s 폴링 → 상태 열·캡처 +3 s/+8 s·관측 15 s, 안 떠나면 20 s 뒤 `IN_PLACE`), `_trace_program_states`, `_summarize_state_runs`(연속 상태 구간별 HD 첫 present·나머지 min/p50·stale max·안전·모드 호출), 레인 배선·`dropped_count` 검사·요약 `title-button-result.json`(스키마 `syw2plus.g1-title-button.v1`).
- `tests/test_g1_new_game_path.py`(최종 `6d970743391d`): RED→GREEN 12개 추가(좌표·클릭 1회·상태 열·재시도 1회·IN_PLACE·트레이스 일시 상태·빠른 폴링·상태 구간 요약·옵션 배선). `make lint typecheck` PASS.
- 같은 파일에 lap1099~1138 미커밋 변경이 이미 있다(이번 회차 변경은 위 두 파일의 TM0 구간만).

## 1. 하네스 결함 4건과 수리(반복 원칙)

실행 순서: prelim(v1) → attempt2 → attempt3 → attempt4 → **최종**. 이전 산출물은 공유 temp `20261007_lap1139_work_htm0/{prelim_harness_v1,attempt2_gate_defect,attempt3_slow_poll,attempt4_final_state_gate}/`에 보존했다(결과 판정에는 최종만 사용).

1. (prelim) 사용자변경은 PS9 안 팝업이라 상태가 안 바뀌어 `BLOCKED`로 오분류 → `IN_PLACE`(두 캡처, 상태 변화 없는 정상 결과)로 분리.
2. (prelim) 서장·캐릭오픈방은 PS9를 약 1초 떠났다 돌아오는 일시 상태(영상·방 열기 시도)라 0.3 s 폴이 놓치고 **재시도 클릭이 시도를 두 번 만들었다**(prologue 후보 lane 모드 호출 4개 = 시도 2회) → 트레이스 `program_state`(집계·요약 이벤트 제외)로 이탈을 판정하고, 이후 첫 1초를 0.05 s로 폴링해 재시도는 둘 다 못 본 경우에만 1회.
3. (attempt2) baseline 트레이스는 늦게 flush돼 상태 열을 비교할 수 없음 → 게이트는 폴 열로 비교, 트레이스 열은 공개만.
4. (attempt3·4) 빠른 폴링 뒤 일시 사슬(PS150 → 대상)의 샘플 한 단계가 lane마다 달라(시나리오 baseline `[14,15]` vs 후보 `[150,14,15]`) 열 전체 비교가 샘플링에 민감 → 게이트 = 각 lane이 마지막에 도달한 상태 일치(`final_states_match`), 전체 열은 공개.

## 2. 실행(최종 하네스, 동기 순차·로그 `logs/gates/lap1139-tm0-<버튼>.{log,exit}` 전부 exit 0)

명령(`scripts/run_tm0.sh <버튼>`, 공유 temp): `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1139_tm0_<버튼> --artifact-root <공유 temp>/20261007_lap1139_work_htm0/<버튼> --hd-source scale2x --title-button <버튼>`. 캐릭오픈방은 마지막에 `scripts/run_charroom_guarded.sh`(호스트 소켓 `ss -tuanp` 0.5 s 표본, 127회, 약 69초, 두 lane 실행 구간 전체)로 실행했다. 디스크 여유 101 GiB(> 20), 각 run `game` 사본은 하네스가 삭제(cleanup ok).

해시: 결과 JSON scenario `0ac4393d0b2e`·user `9ebbdf2da1a2`·prologue `cd35a5819ce5`·charroom `fe793fa01895`, 로그 `1388b285fc05`·`e78a60eff55e`·`e2b260f6f543`·`7f173d2dc633`, 소켓 표본 `fca3a3182578`, 재계산 스크립트 `recalc_tm0.py` `92af141fe128`(하네스를 import하지 않고 raw 트레이스·PNG에서 다시 계산)·결과 `recalc_tm0.json` `5e35e700d6fd`.

## 3. 결과

| 버튼 | 도달 상태(두 lane) | 전환 | 후보 HD(PS 구간) | 판정 |
|---|---|---|---|---|
| 시나리오 `(75,505)` | PS15(서장 지도 "제1장 노량해전", 시작하기·나가기 버튼) | 폴 열 baseline `[14,15]`·후보 `[150,14,15]`(일시 사슬), 최종 둘 다 15 | PS15 1,076 present: 첫 100·나머지 min/p50 100/100·stale 0, 모드 호출 0, 캡처 레이아웃 = baseline nearest-2x 대비 5.41% 픽셀 차(Scale2x 기대 차) | **HD OK** |
| 사용자변경 `(190,505)` | **PS9 유지** — 사용자등록 팝업(ID 입력·ID 변경·ID 삭제·확인)이 PS9 위에 열림 | 상태 변화 없음(두 lane IN_PLACE, 클릭 2회: 팝업이 모달이라 재시도 무해) | PS9 1,793 present: 첫 100 → **나머지 min/p50 84.1/84.1·stale max 76,319**(정착, 5 run 동일), 팝업 변화 영역 후보 캡처 bbox x380..1087·y290..1049(HD 1600×1200) | **수리 후보(<90%)** |
| 서장 `(75,560)` | 일시 상태(baseline `[30,9]`·후보 `[150,9]`) 뒤 PS9 복귀 | 후보 모드 호출 `640×480×16 → 640×480×16`·`800×600×8 → 1600×1200×8`(영상 시도 1회, lap1137과 같음) | PS9 1,101 present 100/100 | **BLOCKED(영상 재생 불가, 화면 없음)** |
| 캐릭오픈방 `(410,505)` | 일시 상태(baseline `[8,9]`·후보 `[150,9]`) 뒤 PS9 복귀, 화면 변화 = 버튼 hover뿐(변경 픽셀 0.46%) | 모드 호출 0 | PS9 1,045 present 100/100 | **BLOCKED(방이 열리지 않음, 화면 없음)** |

- 네 run 공통: V1 outside 0·안전 7종 max 0·fallback 0·success min 1·`trace_dropped_count` 0·`scale2x_validator` PASS·cleanup ok·EXE SHA 불변. `mirror_validator`는 `BLOCKED`("nearest oracle 0.775994 < 0.999", 첫 PS9 present seq 106~118 등)로 네 run 모두 같은 종류 — 원인 미조사(이 하네스는 validator를 게이트에 쓰지 않고 상태 구간 HD·안전 카운터로 판정; `scale2x_validator`는 PASS).
- 외부 접속 가드(캐릭오픈방): 소켓 표본 127회에서 wine·`.exe`·`Syw2plus` 프로세스의 소켓 0(0.5 s 표본이라 매우 짧은 시도는 못 볼 수 있음), 여덟 lane `probe.log`의 socket/connect/dplay 줄 0. 외부 접속 근거 없음(BLOCKED 사유는 화면 없음이지 외부 접속이 아님). 추가 입력은 보내지 않았다.
- 좌표 확인: 네 좌표 모두 클릭 뒤 hover 하이라이트·상태 반응으로 버튼 안쪽임을 확인(캡처 열람: 시나리오 PS15, 사용자변경 팝업, 서장·캐릭오픈방의 hover 모습). 하네스 `LOAD_MENU (296,505)` vs lap1137 표 `(302,505)` 6 px 차이는 불러오기 버튼 안쪽이라 그대로 둠(범위 밖).
- 사용자변경 팝업의 ID 입력/변경/삭제/확인은 누르지 않았다(파일·설정 변경 0). 팝업이 열린 뒤의 재시도 클릭(190,505)은 팝업 밖 좌표이며 상태·화면 변화가 없었다.
- `--stale-mask-state`는 3/23/27/29만 지원해 PS9 팝업의 stale 위치를 마스크로 확정하지 못했다(UNKNOWN). 근거: stale 76,319 ≈ 팝업 논리 창(약 x256..543·y145..455, 면적 약 89k)의 86%.

## 4. 판정

**H-TM0 = `PASS(partial, 기술·격리 관측)`** — 카드 PASS 조건(네 버튼 모두 상태 변화·같은 열)은 일부만 충족한다: 시나리오 PASS(HD OK), 사용자변경은 상태가 아니라 PS9 팝업(수리 후보), 서장·캐릭오픈방은 화면 자체가 없다(BLOCKED, 환경 한계). 새 수리 후보 1개: **PS9 사용자등록 팝업 HD 84.1%(<90%, 정착)**. 사용자 시험(실제 Windows)에서는 서장 영상·캐릭오픈방이 정상 동작할 수 있으나 이 하네스에서는 관측 수단이 없다(backlog 유지).

## 5. 공개·한계

- 사용자변경 stale 위치·writer UNKNOWN(PS9용 stale mask·census는 C 변경 필요 — 수리는 middle이 정한다). 같은 PS9의 다른 팝업(종료하기 확인 `(410,560)`, HQNET 제외)은 미측정.
- 서장·캐릭오픈방의 화면 HD는 이 환경에서 측정 불가. 일시 상태 번호(150·8·30·14)는 샘플링 순서에 따라 lane별로 다르며 최종 상태만 비교했다.
- 5 run(prelim·attempt2·attempt3·attempt4·최종) 모두 사용자변경 PS9 나머지 min 84.1·stale max 76,319로 동일해 재현성은 충분하다(raw JSON 5개 직접 대조).
- 전체 `make check`는 기록 freeze 뒤 실행한다(§6, 결과는 STATUS 검증 줄).


## 6. 전체 `make check` 첫 실행 FAIL → 수리 → 최종 소스 확인 run

- 첫 실행(로그 `logs/gates/lap1139-work-full-check.log`·`.exit`=2): **2 failed·1794 passed·5 skipped/791.26s** — 기존 소스 문자열 검사 2건이 내 변경으로 깨짐: `tests/test_g1_result_screen.py`(`required_states=(9, 35, 3, 29) if result_screen` 문자열)·`tests/test_g1_saved_scene_probe.py`(`fixture=args.fixture, scene_actions=args.scene_actions` 출현 6회 → 7회). 기존 테스트·baseline은 고치지 않고 구현을 맞췄다: 검증기 호출을 `... if not title_button else validate_trace(trace_copy, required_states=(9,))`로, 새 레인 호출의 인자 줄을 나눔(동작 동일, 내 테스트 한 줄만 새 문자열로 갱신). 집중 3파일 `.venv` pytest **285 passed**·lint·typecheck PASS(시스템 `python3`는 Pillow 차이로 8 failed가 보이므로 `.venv`로만 판정).
- 소스가 바뀌었으므로 최종 소스(`b8fa67498b0c`)로 사용자변경 run 1회 재확인(`scripts/run_tm0_srccheck.sh user`, 공유 temp `srccheck/user/`, 결과 JSON `dd8bc80405e9`, exit 0): IN_PLACE·PS9 나머지 min/p50 84.1/84.1·stale max 76,319·안전 0·dropped 0 = 최종 4 run과 동일. 나머지 세 버튼은 소스 문자열 리팩터 전 run이며 검증기 인자는 같은 `(9,)`.
- 최종 `make check`는 이 수정 뒤 1회 더 실행했다(결과는 STATUS 검증 줄·기록 변경 없음).

## 다음 행동

middle(Opus): lap1139 raw 독립 재계산(사용자변경 84.1%·시나리오 PS15 100%·서장/캐릭오픈방 BLOCKED 판정·하네스 결함 4건 수리 타당성) → 수용하면 사용자변경 PS9 팝업 수리 work(H-TM1: PS9 stale 위치 귀속 → writer 미러) 사전등록. 사용자 G1 시험 결과가 오면 최우선.
