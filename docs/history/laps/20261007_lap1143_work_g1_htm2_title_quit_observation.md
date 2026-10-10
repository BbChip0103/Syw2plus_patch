# 2026-10-07 | lap1143 | G1 work — H-TM2 종료하기 `(410,560)` 관측 (확인 팝업 없음, 수리 불필요)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 커밋 0.
- 가설 / 사용자 관찰: lap1142 사전등록 §5 — 종료하기가 in-place 확인 팝업이면 사용자등록 팝업(`0x466480`)과 다른 writer일 수 있다.
- 예상 PASS / FAIL 조건: (a) in-place 팝업 정착 HD ≥98.6 PASS·90~98.6 partial·<90 FAIL→TM2-2 / (b) 확인 없이 종료·PS 이탈 = `PASS(관측, 확인 팝업 없음)`.
- 변경 파일: `tools/g1_saved_scene_probe.py`(`7a42940ca5e4`)·`tests/test_g1_new_game_path.py`(`997cfe89e45a`). C source 변경 0. 같은 파일들에 lap1099~1142 미커밋 변경이 이미 있다(이번 회차 변경은 아래 구간). uncommitted.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만). 후보 DLL = 현재 트리 빌드(기본 켬). fixture 없음, 활성 인원 해당 없음(타이틀).

## 1. TM2-0 하네스 (TDD, RED→GREEN)

- `TITLE_BUTTONS["quit"] = (410, 560)`, 상수 `TITLE_BUTTON_SINGLE_CLICK = {"quit"}`. HQNET `(302,560)`·확인 팝업 안 버튼은 계속 제외.
- `_title_button_window`: SINGLE_CLICK 버튼은 **재시도 클릭 없음**(첫 1초 안 PS9 이탈이 없어도 두 번째 클릭 안 함), 상태 읽기가 `OSError`(프로세스 사라짐)이면 `EXITED`(실패 아님, 관측 결과·캡처 없음). 다른 버튼은 기존대로 `OSError`를 올린다.
- 요약 게이트: window 상태 `PASS/IN_PLACE/EXITED` 허용, `EXITED`면 lane 캡처 ≥1(그 밖 ≥3).
- 테스트 4개 추가·1개 갱신(`test_title_button_points_are_the_unmeasured_menu_buttons`: HQNET 제외·quit 포함·SINGLE_CLICK): quit in-place 재클릭 없음·EXITED 분류·타 버튼 OSError 전파·요약 게이트 배선. `pytest tests/test_g1_new_game_path.py tests/test_g1_screen_watch.py` 66 passed, `make lint`·`make typecheck` PASS.

## 2. TM2-1 관측 (격리 1 run)

명령(`scripts/run_tm2.sh q1`, 공유 temp `20261007_lap1143_work_htm2/`, 로그 `logs/gates/lap1143-tm2-q1.log`·`.exit`=0): `--hd-source scale2x --title-button quit`. 결과 `PASS`(exit 0, `title-button-result.json` `7ab0e4e4e19e…`), 두 lane `source_unchanged` true·cleanup ok·`game` 사본 잔존 0.

| lane | 클릭 | 첫 상태 | 상태 열 | 캡처 |
|---|---|---|---|---|
| baseline | 1회 `(410,560)` | PS11 (0.26 s) | [11] | quit_3s=quit_8s `0dd13199…` 800×600 **전부 검정** |
| candidate | 1회 | PS150(0.05 s 폴링 포착)→PS11 (0.3 s) | [150, 11] | quit_3s=quit_8s `49affa64…` 1600×1200 **전부 검정** |

- trace 상태 열 두 lane 모두 [9, 11]. **확인 팝업 없음**(PS9 유지 0, in-place 0, 재클릭 0).
- candidate trace(`trace_raw.jsonl` `465794525311…`, 329줄): PS9 마지막 present 직후 `blt`(310) → PS11 `surface_release` 14건 → `mirror2x_metrics`·`summary`·`textout_iat_restore`. PS11에서 present 0 → HD 측정 대상 화면 없음. dropped 0, 안전 7종 max 0, fallback 0, success_min 1(PS9 14 present HD 100·stale 0). 캡처 두 장 모두 RGB extrema (0,0)(완전 검정).
- 해석: 종료하기는 확인 없이 종료 절차(PS11: DirectDraw 표면 해제)로 들어가며, 15초 관찰 동안 Wine 프로세스는 상태 읽기가 계속 성공(= `EXITED`가 아님)하나 화면은 검다. 두 lane 동일 동작이라 후보 고유 결함 없음.
- `mirror_validator` BLOCKED는 기존 title-button run과 같은 종류(PS9만 요구하는 단축 검증)이며 게이트에 쓰지 않는다. `scale2x_validator` PASS.

## 3. 판정

- **H-TM2 `PASS(관측, 확인 팝업 없음)`.** TM2-2(귀속·수리)는 조건 불충족이라 실행하지 않았다(수리 대상 화면 없음). 타이틀 메뉴 버튼 중 HD 측정 가능한 것은 시나리오(PS15 100)·사용자변경(PS9 팝업 99.819 수리 후)·서장·캐릭오픈방(BLOCKED)·종료(검정, 해당 없음)로 모두 분류 완료. HQNET은 외부 접속이라 계속 제외.
- 공개 한계: 실제 Windows 종료 동작 미검증(Wine 15초 관찰만), 종료 뒤 프로세스 소멸은 하네스 cleanup이 끝냄, 서장·캐릭오픈방은 lap1140 BLOCKED 유지. 하네스 `EXITED` 경로는 단위 테스트만(실 run 미발생).

## 4. 검사

기록 freeze 뒤 전체 `make check` 1회. 결과는 STATUS 검증 줄에만 쓴다.

## 다음 행동

middle(Opus): H-TM1+H-TM2 묶음 재스테이징 여부 결정(현재 트리 save006 full pair+스테이징 work → root 전달) 또는 G1 다음 미측정 화면 사전등록. 사용자 G1 시험 결과가 오면 최우선.
