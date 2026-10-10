# 2026-10-07 | lap1146 | G1 middle — H-SC0 독립 검수(PS20 브리핑 FAIL로 정정), H-SC1 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행·C·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1145 work → middle 검수 요청, `36d44d06…`, 원문 byte 일치 보존 `docs/history/laps/20261007_lap1146_preserved_lap1145_escalate_sol.txt` 뒤 삭제). INBOX 새 사용자 지시 없음(마지막 = lap1145 처리 메모), APPROVALS 새 반려·사용자 G1 시험 결과 없음(lap1136 재요청 대기), `loop/STOP` 없음.
- 목표: G1. 검수 대상 가설(lap1144 §4): 시나리오 제1장 시작하기 뒤 브리핑·로딩·인게임 화면도 정착 HD ≥98.6·안전 0.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- 후보 source SHA(기록과 일치): `tools/g1_saved_scene_probe.py` `751c78af093d`·`tests/test_g1_new_game_path.py` `1495fefcb8c9`. 전체 check 로그 `logs/gates/lap1145-work-full-check.log` `92a718293f50` 끝부분(typecheck Success·CONTEXT_PASS) 직접 확인. run exit 파일 r1=2·r2=0·r3=0(기록과 일치).
- fixture: 없음(lap1145 raw 재사용, 새 실행 없음).

## 1. raw 독립 재계산 (새 스크립트, 공유 temp `20261007_lap1146_middle_review/`)

`recalc_lap1146.py`(`69ac2f89…`) → `recalc_lap1146.json`(`b866752c…`). 연속 상태 구간으로 나누고 각 구간 첫 present(전환 프레임)를 뺀 정착 present만 센다. HD = (covered − stale)/480,000.

| 항목 | 기록(lap1145) | 재계산 |
|---|---|---|
| 결과 JSON SHA r1/r2/r3 | `b37fc269…`/`16035031…`/`35a930a9…` | 일치. status FAIL/PASS/PASS 일치 |
| candidate trace SHA | `cb00b28a…`/`6e9b1a86…`/`6da1b324…` | 일치 |
| dropped | r1 628·r2/r3 0 | 일치. r1 primary present 7,746 중 PS20 기록 5,931(마지막 present 82.5초, 기록 구간 안 100 ms 넘는 시간 공백 0 → 잘림은 꼬리만, 기록된 부분은 유효) |
| PS9·PS15 | PS15 100 | 두 상태 모두 세 run HD 100·stale 0 |
| PS20 r2(10초) | min 98.243·p50 99.113·<98.6 22.2% | 98.242(반올림)·99.113·22.2%·<90 0 |
| PS20 r3(50초) | min 92.815·p50 98.287·<98.6 58.3% | 92.815·98.288(반올림)·58.3%·<90 0 |
| PS20 r1(90초) | min 89.43·p50 98.152·<90 26.4% | 89.430·98.152·26.4%·<98.6 74.0% |
| PS20 첫 present | 463,592 | 세 run 463,592(다음 present 0) |
| PS20 covered | — | 정착 present 전부 480,000(stale은 미덮임이 아니라 덮였으나 화면과 어긋난 픽셀) |
| PS20 시간 대 stale(5초 구간 중앙값) | r1=r3 결정적 | r1/r3: 0/0·5,805/5,805·8,534/8,534·8,533/8,533·8,740/8,740·8,880/8,883·5,816/5,818·2,052/2,621·1,286/1,286·18,087/18,087·34,486/34,486, r1만 60초 50,735·70~80초 49,501 → **결정적 확인** |
| PS3 | 616/613 present·99.686·stale 0 | **정정: 620/620 present(정착 619/619)**, HD min=p50 99.686·stale 0·30.9초 |
| 안전 7종·fallback·success·hresult | 0·0·1 | 세 run max 0·0·min 1·hresult≠0 0 |
| present 경과 p95 | — | PS9 13·PS15 12·PS20 12~13·PS3 6 ms |

- **불일치 0(수치), 정정 1**(PS3 present 수 616/613→620/620, 판정 영향 없음).
- **stale의 화면 처리 확인(source 판독):** `tools/inmm_stub/g1_mirror2x.c:2037-2065` — covered 픽셀의 현재 원본 값이 기대 스냅샷과 다르면 stale로 세고 그 자리에 **현재 원본 픽셀을 nearest 2×로 출력**한다. 따라서 PS20 stale은 내용·색 오류가 아니라 Scale2x 대신 nearest 화질로 보이는 것이다.
- 캡처 직접 열람: r3 후보 `scenario_ps20_dwell.png`(제 1 장 노량해전, 김시민·김덕령 초상·본문·목표 노랑 글자·버튼 3개, 깨짐·조각 분리 없음), 후보 `scenario_ps3_30s.png`↔기준 `scenario_ps3_30s.png`(자원 5000/5000·331/2100, 건물·유닛·Lv 표시·미니맵·F1~F11·명령 패널 구도 일치, HUD 소실 없음).
- 귀속 단서(trace aggregate, 확정 아님): r3 PS20 동안 화면 밖 표면 `0x01E7F5C0`→`0x01E7F490` BltFast 45,022회(present당 약 12)가 약 39초에 끝나고 그 뒤 `0x01E7FCE0`·`0x01E7F6F0`·`0x01E7F820` 원본으로 바뀐다. stale 급증(45초~)이 이 전환과 겹친다. 미러 계수는 present당 menu_copy 1(전면 480,000, 5초 뒤 hash 고정)·bbox 4로 일정 → 화면 밖 합성 표면에서 뒤 버퍼로 옮기는 writer가 미러 밖일 가능성. 위치·writer는 측정으로 확정해야 한다.

## 2. 판정 — H-SC0 work 판정 정정

- **사전등록(lap1144 §4)은 "<90 = FAIL"이다.** r1 90초 체류의 기록 구간(유효)에서 정착 present 26.4%가 <90(60초 이후 50,735 stale = 89.43)이고, 이 계열은 r3와 50초까지 같은 값으로 재현되는 결정적 동작이다. 사용자 체류 시간이 대표적인지 모른다는 이유로 기준을 낮추지 않는다(기준·validator 무완화).
- **H-SC0 판정: PS9·PS15·PS3 인게임 `PASS(관측)`, PS20 브리핑 `FAIL(화질)` → 전체 `FAIL(PS20 화질, 내용 정상)`.** 시각 심각도는 낮다(nearest 화질, 내용·색·위치 정상, HUD 해당 없음). work의 PASS(partial) 판정은 이 기록으로 정정한다(수치는 일치).
- 원본 구성: 두 lane 상태 열 [16/150, 20, 1, 3] 동일·PS1 모드 800×600×8 → 후보 native 2x는 기존 구성과 같다(기록 §2 수용).
- 하네스 한계 수용: r1 dropped(8192 이벤트 상한)·PS150 1홉 표본 차·PS3 입력 없는 유지. 상한 때문에 다음 측정은 체류 65초로 묶는다(PS20 약 70 present/s × 65 + 앞뒤 약 1,800 ≈ 6,400 < 8,192).

## 3. 시험판 재스테이징 — 보류 유지

- 이번 회차 가시 수리 없음, 사용자 lap1135판 결과 없음. H-SC1이 PS20 수리에 성공하면 그 middle 검수에서 묶음 재스테이징(H-TM1+H-SC1)을 판단한다.

## 4. 다음 work 사전등록(Sonnet) — H-SC1: PS20 브리핑 stale 위치·writer 귀속 → 조건부 수리 (한 work 회차)

**근거.** PS20 stale은 결정적이고(r1=r3), 내용 오류가 아닌 미러 밖 writer 화질 손실이며, 기존 패턴(H-TM1 `0x466480`, H-B4 `0x467B00`, H-RS3 호출 지점 미러)으로 수리 가능성이 높다. 구현 우선 지시에 따라 귀속과 수리를 한 회차에 잇는다.

- **SC1-0 진단 옵트인(TDD, 기본 동작 불변):** `g1_stale_mask_state_parse`(`tools/inmm_stub/g1_stale_mask.h`)·`g1_screen_watch_state_parse`(`g1_screen_watch.h`)에 정확한 값 `"20"`→PS20 추가(그 밖 값은 기존과 같음), 하네스 `--stale-mask-state`·`--screen-watch-state` choices에 20 추가. 테스트: 파서 20→20·기존 23/27/29/9 불변·임의 값 PS3, env 없음 = 기존 동작, CLI 배선.
- **SC1-1 위치(격리 1 run):** `--hd-source scale2x --title-button scenario --scenario-start --scenario-play --scenario-briefing-dwell 65 --stale-mask <PS20 ordinal 약 700·1750·2650·3350·4350> --stale-mask-state 20`. 각 dump의 stale 연결 성분 bbox·면적, 후보 캡처 위 표시. dropped>0이면 체류 60초로 1회 재실행.
- **SC1-2 writer(같은 회차):** SC1-1 stale bbox 안 표본점으로 `--screen-watch --screen-watch-state 20` 1 run → 쓰기 EIP·호출처·반환 주소 귀속, objdump로 함수 경계·`ret` 크기·인자·호출처 확인. §1 단서(화면 밖 표면 `0x01E7F490` 합성 → 뒤 버퍼 복사)를 확인하거나 반증한다.
- **SC1-3 조건부 수리(같은 회차):** writer가 단일 미후킹 게임 함수 또는 기존 미러 계열 DDraw 호출이면 기존 diff 미러 방식으로 수리(기본 켬, 끔 env 대조). 원본 호출 그래프로 그 hook이 PS20 밖에서도 도는지 확인하고, 돈다면 save006 짧은 pair 비회귀 1회를 더한다.
- **측정·판정:** 켬 2 run + 끔 1 run(체류 65초): PS20 정착 HD min ≥98.6·<90 0%·p50, 끔은 <90 재현, PS9/PS15 100·PS3 99.686 비회귀, 안전 7종·fallback·dropped 0, present 경과 p95 비교, 캡처 열람. 켬 min ≥98.6 & 끔 재현 = `PASS(partial, 기술·격리)`; 개선됐으나 <98.6 = `PASS(partial)`+잔여 위치; writer가 여러 개·wined3d 스레드·귀속 불가 = `BLOCKED`(위치·후보만 남기고 수리 없음) → middle.
- **금지·공통:** 원본/참고 쓰기·커밋·`260921_temp` 쓰기 금지. 각 run 뒤 `game` 사본 삭제·디스크 ≥20GiB(현재 86GiB). 긴 실행은 `setsid nohup`+생존 확인, 끝까지 대기. C·하네스 변경 시 lint·typecheck → 기록 freeze → `make check` 1회. **사용자 G1 시험 결과가 오면 그것이 최우선.**
- 연속 규칙: lap1145는 실행 증거가 있는 work. 이번 middle은 실행 증거 없음 1회째. 다음은 실행 증거를 남기는 work여야 한다.

backlog 유지: H-TM1 잔여 871, Wine 영상 재생 불가, victory-poke readback 경합, 하네스 trace 8192 상한(장기 체류), STATUS 목록.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS 검증 줄에만 쓴다.
- 전체 `make check` SKIP: 이번 회차 변경은 문서·공유 temp 스크립트뿐이고 C·하네스·테스트 source는 lap1145 full PASS(1817 passed, exit 0) 때와 같다.

## 다음 행동

work(Sonnet): §4 H-SC1(SC1-0 진단 옵트인 → SC1-1 위치 → SC1-2 writer → 조건부 SC1-3 수리·켬2/끔1 측정). 그 뒤 middle 검수. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.
