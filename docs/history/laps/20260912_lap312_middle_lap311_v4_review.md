# 2026-09-12 | lap 312 | G1 — lap311 V4(R2) 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, 지정 역할 **middle(진단·계획·확인)**.
  게임 코드 hands-on 수정 없음. 검수 probe/test/문서만 작성했다.
- 가설 / 사용자 관찰: lap311의 R2 주장(실패 arm writer 집합 `∅`, reset writer가 성공 return을 post-dominate)이
  참이라면, lap311 코드를 전혀 쓰지 않는 두 가지 다른 방법 — (a) PE 원시 `.text` 바이트에서 절대 참조를
  opcode로 분류한 writer 전수 census, (b) dataflow fixpoint 대신 **cut 판정**(노드 삭제 시 entry→성공 ret
  단절 여부) — 으로도 같은 수치가 나와야 한다. 나오지 않으면 lap311은 FAIL이다.
- 예상 PASS / FAIL 조건: 원본 SHA 불변; lap311 세 산출물 SHA 불변; `.text` 전체 절대 참조에서 store가
  정확히 `{0x431B79,0x431B7F,0x4324B8,0x4324C2}`이고 전부 map window 안; moffs store 0; 미분류 0;
  `0x431AF2` 바이트가 `75 0a`이고 taken target이 `0x431AFE`; fall-through arm 바이트가
  `5f5e5d33c05b83c434c3`(eax=0 반환); cut 판정으로 reset writer 2개가 entry→`0x4324D5`와 join→`0x4324D5`를
  각각 단절; **반증 대조군**(off-path 노드 `0x431AFD`) 삭제는 단절하지 **않음**; 실패 arm이 성공 ret 미도달.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `docs/history/laps/probes/20260912_lap312_middle_lap311_v4_review_probe.py`
  SHA `34835a278b3fe2a9fae65b8ba25b2d14e508c7ffa015f51e16c28c0178f53e17`; 신규
  `tests/test_lap312_lap311_review_probe.py`
  SHA `f0142fc0193f7e4d40bc34027c98934cc822be10008ef112dc2cfc3dc051aaa3`; 생성 report
  `logs/lap312/lap312_middle_lap311_v4_review.json`
  SHA `46b693f061dc6e0ecf86395535e98dc7186daf52f0fcc33e2a24048398650e9f`; `docs/STATUS.md` 갱신과
  `docs/history/laps/20260912_status_lap312_compaction.md` 원문 보존. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
  lap305/306/308/309/310/**311** 산출물은 읽기만 했고 수정하지 않았다(위 SHA 재확인 일치).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `Syw2plus/syw2plus_original.exe` SHA `b56986e0…c9c08a8ac` 실행 전후 불변. 후보 EXE·활성 플레이어·지도·
  군대·fixture 없음(정적 검수). Linux `.venv`, PE 헤더 직접 파싱 + `objdump` 명령 경계.
  게임/Wine/Xvfb/Stage B/runtime/PNG/click 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap312_middle_lap311_v4_review_probe.py >
  logs/lap312/lap312_middle_lap311_v4_review.json` → exit 0, `"verdict": "PASS"`, `failures` 빈 배열.
  같은 probe fresh 2회 stdout `cmp` byte-identical(5,146 B), 저장 report와도 byte-identical.
  `.venv/bin/python -m pytest -q tests/test_lap312_lap311_review_probe.py` → **4 passed**.
  `make check` → **303 passed**, Ruff/compileall/mypy/`CONTEXT_PASS`.
  `bash checks/safety.sh check` → `SAFETY_PASS`. 캡처/PNG 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **lap311 V4 = ACCEPT-WITH-STRENGTHENING (1단 기계 검수만).**
  - A1 writer census(원시 바이트): `.text` `0x401000`, 932,581 B, `0xE5BF1C`/`0xE5BF20` 절대 참조 **111건**
    = load 107(mov r32 59, mov eax,moffs32 45, imul 3) + **store 4**. store 집합
    `{0x431B79,0x431B7F,0x4324B8,0x4324C2}` — lap311과 일치하고 4개 **전부 map window 안**.
    **moffs store 0건**(lap306 R5 독립 재확인). 미분류 0건.
  - A2 gate 바이트: `0x431AF2` = `75 0a` → taken `0x431AFE`(성공 join), fall-through `0x431AF4` 바이트
    `5f5e5d33c05b83c434c3` = `pop edi/esi/ebp; xor eax,eax; pop ebx; add esp,0x34; ret` → **실패 arm은 0 반환**.
    lap311이 이름으로만 단언했던 두 사실을 바이트로 확인했다.
  - A3 cut 판정: window 753 instruction, unresolved branch 0, entry-reachable 753, join-reachable 724,
    실패 arm 정확히 7개(`0x431AF4,F5,F6,F7,F9,FA,FD`)이고 성공 ret 미도달 → lap311의 746 = 753−7과 일치.
    reset writer 2개가 entry→성공 ret와 join→성공 ret를 **모두 단절** → lap311 post-dominator 주장 **재현**.
    반증 대조군 `0x431AFD` 삭제는 단절하지 않음 → 판정기가 무조건 PASS가 아님을 증명.
  - **lap311을 넘어선 신규 사실(강화):** ① runtime writer `0x431B79`/`0x431B7F`도 entry→성공 ret를 단절한다
    (즉 **네 writer 전부**가 성공 경로 필수). ② reset writer 2개는 `0x431B79` **이후에도** 필수다(순서 확정).
    ③ `0x4324C2` 이후 도달 명령은 `0x4324CC,0x4324D1,0x4324D2,0x4324D5` 넷뿐이고 그 안에 화면 writer **0개**
    → 이 함수가 성공 반환 시 남기는 **마지막 직접 쓰기는 640×480 reset**이다. post-dominance만으로는
    이 결론이 나오지 않으므로 lap311 주장은 참이지만 under-claim이었다.
  - **lap311 잔여 결함 5건(전부 수치 영향 0, PASS 유지):**
    D1 `pre_gate_screen_writers`는 네 writer가 모두 gate 주소보다 위라 **구조적으로 공허**하다 →
    비교식이 `failure_writers == set()`로 축약된다. lap310의 "R2 공허 게이트" 지적은 **부분 수리**이며
    실제 신규 정보는 success-arm 집합과 post-dominator다.
    D2 "gate 이전"을 **주소 순서**(`address < MAP_GATE_BRANCH`)로 근사해 backward jump가 있으면 불건전하다.
    D3 anchor 가드가 `failure_seed == gate + 2`만 확인하고 taken target·반환값을 보지 않는다(fail-open).
    D4 `EXPECTED_RUNTIME_WRITERS`(line 33)는 정의만 되고 한 번도 읽히지 않는 죽은 상수다.
    D5 위 under-claim.
    추가로 `tests/test_lap311_mode_writer_probe.py`는 `PROBE.parse_text/build_cfg/dominators`를
    **자기 검증 대상에서 import**하므로 상수·앵커 드리프트는 잡아도 알고리즘 결함은 못 잡는다
    (lap310이 lap309에 지적한 동어반복보다 약한 같은 계열). 본 lap312 테스트는 cut 판정과 원시 바이트로
    이 사각을 덮는다.
  - 이 결과는 전부 **정적**이며 G1 제품 증거 **0**이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: A3는 lap311과 `objdump` 명령 경계를 공유하고 call을
  fall-through로 취급하므로 callee 쓰기·cross-function event/thread 순서는 여전히 UNKNOWN이다.
  A1은 절대 displacement 피연산자만 덮으므로 계산/간접 포인터 쓰기는 UNKNOWN(lap306 fail-open 유지).
  click-time mode, WM_CLOSE, 실제 scene/input, G1~G4 제품 증거는 0. 본 검수는 middle의 **기술 컨펌**이며
  사용자 마일스톤 승인·Stage B 허가·제품 G1 합격이 아니다. 본 probe는 자기 출력 SHA를 단언하지 않아 W3 함정을 피한다.
- 다음 한 가지: 다음 work(Luna/Sonnet5/high)가 **D1~D4를 최소 변경으로 수리**한다 — `pre_gate` 비교를
  주소 순서 대신 **CFG 상 gate 지배 관계**로 재정의(또는 공허함을 보고에 명시), gate taken target과
  실패 arm 반환값을 probe 가드로 승격, 죽은 상수 제거. lap311 산출물은 **덮어쓰지 말고**(lap301 provenance
  회귀 재발 금지) 새 파일로 남긴다. 게임/Wine/Xvfb/Stage B/runtime/PNG/click 실행과 lap305~312 산출물
  수정은 계속 금지.
