# 2026-10-14 KST | lap1291 middle | H-G1ON2614 raw 충돌 확인

- 역할: 사용자 지정 middle(진단·계획·독립 확인), Codex App fresh 세션. 실제 모델/effort는 호출 표면에서 확인할 수 없어 추측하지 않음. 게임·하네스 구현, 빌드, 새 게임 실행, 전달, 커밋 0.
- 읽기 순서: loop/PROMPT → AGENTS/최신 INBOX·APPROVALS → STATUS 전체 → DESIGN1~4/MODEL_ROUTING → lap1289/1290 인계·대상 구현/raw. STOP 없음. runtime lap 파일1291은 읽기만 했다.
- 목표/가설: lap1289 WINMM export·원본/후보 SHA·4 lane·480초 주장을 독립 확인한다. raw가 실질 충돌하면 수용을 HOLD하고 원시 근거와 work 수리 계획을 남긴다. G1 완료/전달 승인 경계는 넘지 않는다.
- 최신 범위: INBOX00:29에 따라 G5는 다른 세션 담당이며 이 루프에서 재개하지 않는다. 별도 ESL2614 두 조합 섹션과 타 세션 변경은 비접촉.

## 독립 확인 결과

- 원본 EXE SHA `ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf`, 후보 WINMM DLL SHA `d2ce1637574340dbd306fa4a41a591461c899cc03c987568ee018b576ec65c53` 재계산 MATCH. 189개 export name/ordinal은 설치된 Wine system WINMM과 exact MATCH; hook ordinal MCI52/begin145/end146/time149. Windows 시스템 export/API 동작의 승인 아님.
- retry1의 new-game/save006 × off/on 네 lane: 기존 manifest·capture SHA/크기·raw trace SHA 일치, off800×600/on1600×1200, 게임 사본 부재 확인. candidate 종료 summary 각각 drop0/detached/flush complete. 당시 cleanup는 prefix process0이며 이번 회차 새 실행/프로세스 검증은 하지 않았다. save006은 이전 버전 fixture이고2614 자체 생성 save roundtrip이 아니다.
- **480초 안정성 주장은 HOLD(실질 raw 충돌).** soak result 최상위/lane/play는 PASS이나 같은 result의 trace_summary는 FAIL. raw8192행 마지막 summary는 install_status=failed, dropped_count=10932, aggregate_output_dropped_count=42; overflow2개는 scope=event_limit. detach/flush complete는 기록 손실을 해소하지 않는다.
- raw의 PS3 dwell presents3623개, HD min100%·stale/fallback0은 **관측된183.474초 구간만**의 결과다. 최초 PS3→PS27은196.834초, →PS29은205.037초. 마지막 present→final summary 사이257.971초는 기록이 끊겼다. 끝난 경기/누락 구간을480초 실플레이로 세지 않는다.
- 기존 `ps3_dwell_3.png`를 직접 보니 결과 표와 “패배했습니다.”가 보인다. dwell2/dwell3/ps3_play SHA가 같다(`5a81d9f32cbf510307eef0d7726766238bf0c5799291c9fe47a1a70c8a693ec5`). 이는 승패 종료 근거이며 제품 크래시 재현이 아니다. 기록 손실 이후 안전/잔상0·crash0의 전구간 주장은 미검증.
- candidate 기본/soak/force-music prefix MCI log는 모두0 B. 음악/효과음 UNKNOWN 유지. 60초 force-music run의 drop0는480초 run의 실패를 대체하지 않는다. 실제 Windows·사용자 입력·2614 자체 저장 재로드·G1 마일스톤은 SKIP/미확인.

## 추적 가능한 원인 / 구현 인계(work만 수정)

1. `tools/inmm_stub/direct_draw_trace.c:40`의 TRACE_MAX_EVENTS8192와 trace_event의 event_limit 분기가 관측된 로그 소진 원인이다. raw overflow/summary가 이를 직접 뒷받침한다. 단순 해시 오타/전사 오류가 아니다.
2. `tools/g1_saved_scene_probe.py:2804`의 `_summarize_play_presents`는 PS3 rows만 필터링하고 존재/화질·안전계수로 PASS한다. 전체480초 상태·시간 coverage 또는 중간 승패 종료를 검증하지 않는다. lane PASS는 finally의 trace_summary FAIL로 내려가지 않고 `g1_esl2614_display_probe.py`가 lane PASS/사본제거만으로 최상위 PASS를 만든다. 정확한 수리 범위는2614 전용 결과 결합과 soak 시간/상태 판정으로 좁힌다.
3. 입력 경로가 검수 중 재배치된 사실도 확인: 기대 `../[ESL]Syw2plus - ESL2614/[ESL]Syw2plus 2614.exe`는 현재 없고 실제는 그 아래 `[ESL]Syw2plus/`다. 이동 주체는 확인하지 못했다. 그 EXE SHA는 동일하다. 진단 스크립트 초회 FileNotFoundError는 명시적 두 경로 기록으로 수정해 재실행 성공(게임 하네스 변경 아님). work는 실제 입력 위치를 확인하고 **SHA 거부 유지한 채** 자기2614 adapter 경로만 대응한다; 원본을 되돌려 옮기지 않는다.
4. work 회귀: 보존 soak raw를 넣으면 nested trace_summary FAIL/시간 부족·PS29 전환이 상위 성공이 될 수 없음을 검증한다. 정상 short lane의 drop0/시작·표시 통과는 유지한다. sampler/로그 예산은 같은480초 시험의 직접 관측을 막는 범위만 최소 대응한다; 안전pin/기존 raw/기준을 바꾸거나 다른 도구 제품으로 확장하지 않는다.
5. 수정 후 관련 회귀→격리 실제 시험. PS3 이탈은 승패 종료와 crash를 구분해 중단/부분 결과로 남긴다.480초 합격은 명시된 장면에서 실제 게임 상태/관측 coverage480초를 확인해야 한다. 현재4 lane·DLL 동일 SHA 증거는 재사용하고, 실패한soak 경로만 재실행한다. middle은 게임 코드 수정하지 않는다. 오디오0-call은 별도 남은 실제 시험이며 이번 수리로 PASS하지 않는다.

## 명령 / 증거 / 보존

- 실행: `python3 /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261014_lap1291_middle_g1_winmm_review/recalculate.py` → `HOLD_RAW_CONFLICT` 진단 생성(exit0은 수용 아님). 독립계산·hash·manifest·capture 대조는 옛 실행 근거 검수이며 fresh runtime 아니다. 결과 `review.json`은 같은 공유temp 폴더에 있다.
- soak result SHA `a2e5b7b384a1fc2af32a6f91fb12104b5a8632d4e00a10adda1173dc3de381fa`; raw trace SHA `86ba52c4b19c634f7363113346aee68bd482d5507750528a315505d1bda57541`. retry1 result SHA `c877ba48020ac130db335705167e699250c77a898371cc18bfde902ac0bfe311`; mci result SHA `fcc236ab02ece887fc901853da493a17a1a72761c407b450a02a0f09d78ff7d3`.
- 최초 독립계산 시 현재 implementation fingerprint `02d2127dda4474a85278cf15b089b6f5ff00233c`(loop/loop.sh 함수로 계산). 사용자 runtime 입력의01ff08e3…와 다르다. source snapshot11개 SHA는review.json에 기록. 현재 소스가 lap1289의 빌드source와 같다는 주장은 하지 않는다; export는 실제 기존DLL 바이트로 확인했다. 이 세션은 제품 source를 쓰지 않았다.
- 변경 파일: STATUS/INBOX/APPROVALS, 본 lap 기록, 이전 인계·STATUS의 byte-exact 보존, `loop/ESCALATE_SOL`; 공유temp 진단 스크립트/JSON. 이전 미커밋 변경·원본·raw·후보·게임/prefix는 수정/삭제하지 않음.
- lap1290 ESCALATE 원문3326 B SHA `c9c72b294f8112027aba663fced57cb105e0da13eb29452c8e3e46006c768901`는 `20261014_lap1291_preserved_lap1290_escalate_sol.md`에 보존. 전 STATUS58줄 SHA `7e662c864586c2ae0143e7eccc2d0bfbe59293fa8129fd2718d5b7f32e5b3fd5`는 `20261014_lap1291_status_before_raw_review.md`에 byte-exact 보존.
- 새 게임/빌드/pytest/lint/typecheck/전체make check SKIP: 실질 raw 충돌로 사용자 지정 승격 종료이며 제품 소스 변경 없음. 전체check는 전달 직전만 수행한다. 문서 한도·안전·구현 불변 검사를 최종 기록한다.
- 다음 한 가지: root/Sol이 충돌·입력 위치를 확인하여 **위 최소 수리를 work에 명시적으로 배정**한다. 수리 전 현재480초 후보를 기술/사용자 PASS로 마감하거나 전달하지 않는다. 추가 계획 회차를 쌓지 말고 추적 가능한 결함은 work가 고쳐 실제 게임으로 돌아간다.

## 최종 문서·안전 확인

- `python3 checks/context_limits.py` → CONTEXT_PASS; `python3 checks/safety.py check --require-game` → SAFETY_PASS; `git diff --check` → exit0. 종료 전 STATUS63/INBOX310/APPROVALS90줄로각130/350/250이하이며Blockers절정확히1개. 다른세션의동시문서추가는보존했다.
- review.json SHA `9549375e79a39d1c41274cc2b6013e9ea471f37d27717747582da2d536a42dbe`;독립계산에기록한대상11개소스SHA재대조변경0·후보DLL비접촉·lap파일1291불변. 전체implementation fingerprint는최종 `5b9101e1572972ec9f125ad4e221940a7a1511cb`로달라졌으므로전체source불변은주장하지않는다. 다른세션변경은회수/수정하지않았다.
- 판정: 정적export/기존짧은lane근거국소확인PASS,480초안정성기술수용HOLD,오디오UNKNOWN. 원시충돌로중단·승격하며새실행/전체검사/마일스톤마감을강행하지않는다.
