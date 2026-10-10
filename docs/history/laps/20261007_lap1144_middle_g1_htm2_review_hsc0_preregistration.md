# 2026-10-07 | lap1144 | G1 middle — H-TM2 독립 검수, 재스테이징 보류 유지, H-SC0 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행·C·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1143 work → middle 검수 요청, `1beaf6d1…`, 원문 byte 일치 보존 `docs/history/laps/20261007_lap1144_preserved_lap1143_escalate_sol.txt` 뒤 삭제). INBOX 새 사용자 지시 없음(마지막 = lap1143 처리 메모), APPROVALS 새 반려·사용자 시험 결과 없음(lap1136 재요청 대기), `loop/STOP` 없음.
- 목표: G1. 가설(검수 대상): 타이틀 종료하기 `(410,560)`는 확인 팝업 없이 종료 절차로 가며 HD 측정 대상 화면이 없다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- 후보 source SHA(기록과 일치): `tools/g1_saved_scene_probe.py` `7a42940ca5e4`·`tests/test_g1_new_game_path.py` `997cfe89e45a`. 전체 check 로그 `logs/gates/lap1143-work-full-check.log` `4ed8c9986581` = 1802 passed·5 skipped/772.06s, lint·typecheck·CONTEXT_PASS 직접 확인. run exit 파일 `logs/gates/lap1143-tm2-q1.exit` = 0.
- fixture: 없음(lap1143 raw 재사용, 새 실행 없음).

## 1. raw 독립 재계산 (새 스크립트, 공유 temp `20261007_lap1144_middle_review/`)

`recheck_lap1144.py` → `recheck_lap1144.json`, `window_lap1144.py` → `window_lap1144.out`.

| 항목 | 기록 | 재계산 |
|---|---|---|
| 결과 JSON SHA·status | `7ab0e4e4e19e…`·PASS | 일치 |
| candidate trace | 329줄 `465794525311…` | 일치 |
| baseline trace | (기록 없음) | 366줄 `b746f2a15764…` |
| 상태 열(trace) | 두 lane [9, 11] | 일치(baseline 원시 열의 9↔11 반복은 PS11 뒤에 기록되는 `aggregate` 줄의 program_state 9 때문, 상태 이동 아님) |
| PS11 사건 | surface_release 14·present 0 | 두 lane 모두 surface_release 14, present 계열 0. 후보는 그 뒤 metrics·summary·textout restore |
| 후보 관측 창(269~329줄) | PS9 14 present HD 100·stale 0 | 14 present 전부 PS9·covered 480,000·stale 0 |
| 캡처 | quit_3s=quit_8s 전부 검정 | baseline `0dd13199…` 800×600·candidate `49affa64…` 1600×1200 모두 비검정 픽셀 0, 메뉴 캡처는 정상(비검정 445,940 / 1,782,976) |
| dropped·cleanup | 0·ok | summary dropped 0, 두 lane cleanup ok·`game` 제거·`source_unchanged` true |
| 클릭 | 1회, 재클릭 0 | 두 lane `clicks` 길이 1 |

- **불일치 0, 정정 0.** 공개 1: `mirror_validator` BLOCKED(errors 69)는 기존 title-button run과 같은 PS9 전용 단축 검증 종류이며 게이트 아님. `scale2x_validator` PASS(hd_mask_outside 0·palette 0).
- 검수 질문 (2) `EXITED` 미발생: 두 lane 모두 15.07/15.19초 동안 PS11에 머물렀다(Wine에서 프로세스가 표면 해제 뒤 바로 끝나지 않음). 두 lane이 같으므로 후보 결함이 아니고, 판정은 사전등록 (b)의 "PS 이탈" 쪽에 해당한다. `EXITED` 분기는 단위 테스트로만 덮인 하네스 경로로 남긴다(backlog 아님, 실제 Windows 종료 동작은 사용자 시험 범위).

## 2. 판정

- **H-TM2 `PASS(관측, 확인 팝업 없음)` 수용.** 수리 대상 화면 없음, TM2-2 미실행 타당. 타이틀 메뉴(PS9) 버튼 분류 완료: 시나리오 PS15 100 · 사용자변경 팝업 99.819(H-TM1 수리) · 서장·캐릭오픈방 BLOCKED(환경) · 종료 검정(해당 없음) · HQNET 외부 접속 제외.

## 3. 시험판 재스테이징 결정 — 보류 유지

- lap1135판 뒤 바뀐 사용자 체감 요소는 H-TM1(사용자등록 팝업 화질)뿐이다. 이 팝업은 등록 사용자가 없을 때나 사용자변경을 눌렀을 때만 뜨고, 화질 차는 허용 범주다. 사용자는 lap1135판 결과를 아직 주지 않았다.
- 그래서 지금 새 폴더를 또 만들지 않는다. **다음 가시 수리(인게임·전투 화면 등)가 생기거나 사용자 결과가 오면** 그때 현재 트리 save006 full pair+스테이징 work로 묶는다. 사용자 결과가 오면 그것이 최우선이다.

## 4. 다음 work 사전등록(Sonnet) — H-SC0: 시나리오 제1장 시작 → 브리핑·로딩·인게임 HD 관측

**근거.** 타이틀 메뉴 분류가 끝났고, 시나리오 화면 PS15(lap1139 캡처 `scenario_8s.png`: "제 1 장 노량해전", 버튼 시작하기·나가기)는 HD 100이다. 그 너머(브리핑·로딩·시나리오 인게임)는 한 번도 측정하지 않았다. 지금까지 인게임 측정은 save006·save000과 새 게임(혼자하기) 지도뿐이라, 시나리오 지도(노량해전, 수군·시나리오 문구 가능)는 STATUS의 남은 항목 "두 번째 장면"을 넓히는 실제 제품 화면이다.

- **SC0-0 하네스(TDD):** 기존 `--title-button scenario` 흐름 뒤에 PS15에서 **시작하기 논리 좌표 (605,563)**(800×600 기준, 캡처 판독: 버튼 상자 약 x557..653·y547..579)를 1회 클릭하는 옵션 `--scenario-start`를 추가. 재시도 클릭은 PS15 유지가 2초 이상일 때 1회만. 그 뒤 상태 열·상태별 HD를 **최대 90초** 관측하고 상태가 바뀔 때·PS3 진입 10초·30초에 캡처. 나가기 `(722,563)` 클릭 금지. 테스트: 좌표·재시도 1회 제한·상태 요약 배선.
- **SC0-1 관측(격리, 현재 트리 기본 켬):** `--hd-source scale2x --title-button scenario --scenario-start` 1 run(+재현 1 run). 측정: 상태 열(브리핑/로딩/인게임 상태 번호), 각 상태 present 수·정착 HD min/p50·stale 최빈값, 안전 7~9종·fallback·dropped, 캡처 열람(UI/월드 비율·HUD 조각 분리·잘림 여부). 원본 lane과 상태 열 대조.
- **판정:** 모든 present 상태 정착 HD ≥98.6·안전 0 = `PASS(관측)`; 90~98.6 상태가 있으면 `PASS(partial)`+위치 판독(독자 Scale2x 대비 nearest 블록 bbox); <90 또는 HUD 소실·조각 분리 = `FAIL` → 다음 middle이 귀속. 영상 시도(640×480 모드 호출)만 있고 화면이 없으면 서장과 같은 BLOCKED로 기록하고, 영상 상태에서 60초 넘게 멈추면 Esc 1회까지 허용(기록).
- **SC0-2 조건부(같은 회차, 구현 우선):** 인게임 PS3에 들어가면 그 자리에서 기존 `--census-only`가 아닌 기본 측정만 30초 더 유지(입력 없음). 수리는 하지 않는다(위치·수치만).
- **금지·공통:** 시나리오 진행 저장 파일은 격리 game 사본 안에서만 바뀜(원본 비접촉). 원본/참고 쓰기·커밋·`260921_temp` 쓰기 금지. 각 run 뒤 `game` 사본 삭제·디스크 ≥20GiB(현재 89GiB). 긴 실행은 `setsid nohup`+생존 확인. 하네스 변경 시 lint·typecheck → 기록 freeze → `make check` 1회. **사용자 G1 시험 결과가 오면 그것이 최우선.**
- 연속 규칙: lap1143은 실행 증거가 있는 work. 이번 middle은 실행 증거 없음 1회째. 다음은 실행 증거를 남기는 work여야 한다.

backlog 유지: H-TM1 잔여 871, Wine 영상 재생 불가, victory-poke readback 경합, STATUS 목록.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS 검증 줄에만 쓴다.
- 전체 `make check` SKIP: 이번 회차 변경은 문서·공유 temp 스크립트뿐이고 C·하네스·테스트 source는 lap1143 full PASS(1802 passed, exit 0) 때와 같다.

## 다음 행동

work(Sonnet): §4 H-SC0(SC0-0 하네스 `--scenario-start` → SC0-1 관측 → 조건부 SC0-2). 그 뒤 middle 검수. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.
