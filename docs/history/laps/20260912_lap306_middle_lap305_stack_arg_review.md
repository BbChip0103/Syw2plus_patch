# 2026-09-12 | lap 306 | G1/S1 lap305 V1 독립 검수 — stack-argument 정규화 감사

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle(진단·계획·확인). 게임 코드 hands-on 수정 없음, 실행 없음.
- 가설 / 사용자 관찰: lap305 V1-B의 "shared callee가 entry arg1/arg2를 전혀 읽지 않는다"는 결론은
  `sub esp` 뒤 stack 정규화에 의존한다. 그 정규화를 독립 부호로 재유도하면 결론이 유지되는지 검증한다.
- 예상 PASS / FAIL 조건: 291 site·단일 callee·writer 0·하한 20이 신규 objdump에서 재현되면 수치 ACCEPT.
  정규화를 올바른 부호로 돌렸을 때 arg 접근이 0이 아니면 근거 주장 REJECT.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 probe `docs/history/laps/probes/20260912_lap306_middle_lap305_stack_arg_review_probe.py`
  SHA `8d62ee6ae1eb2d8af4e0950847bf00081d2d5f904263e98c2f62b49e7df1c58a`;
  report `logs/lap306/lap305_stack_arg_review.json`
  SHA `fe97e73215c89e94aed72dfed153380d7b57e3c4dc76f8e2b1254ea3fa50c747`(attempt2 byte 동일).
  lap305 probe/report와 원본 EXE는 **수정하지 않았다**(SHA 불변 확인). 커밋 없음(`LOOP_ALLOW_COMMITS=0`).

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 읽기 전용.
  후보/활성 플레이어/지도/군대/fixture 없음. offline Linux `.venv` + `/usr/bin/objdump`.

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap306_middle_lap305_stack_arg_review_probe.py`
  두 fresh run exit0, `cmp` 일치, `failures=[]`. `make check` 292 passed / Ruff / compileall / mypy /
  `CONTEXT_PASS`. `bash checks/safety.sh check` = `SAFETY_PASS`. 신규 probe도 Ruff 통과.
  PNG·게임·Wine·Xvfb·Stage B·runtime 실행 0.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **R1 CONFIRMED:** `push 0xE5BF18` **291개**, first call **291/291 → `0x465250`**, unresolved 0.
    신규 사실: 3개 site(`0x4130a6`/`0x418c0e`/`0x4d748e`)는 push와 call 사이에 명령이 끼지만
    전부 esp 불변(`mov edi,0x1`, `movsx`, `rep movs`, 절대 저장)이라 **291/291 모두 arg1 유지**.
  - **R2 REFUTED (lap305 근거 주장):** 올바른 부호로 보면 callee는 arg1을 `0x46526d`
    (`mov eax,[esp+0x110]`, depth `0x10c` → entry `+4`), arg2를 `0x465287`
    (`mov edx,[esp+0x108]`, depth `0x100` → entry `+8`)에서 **읽는다**. lap305 report의
    `entry_relative_arg_4_or_8_accesses={}`와 `object_arg1_is_consumed_by_shared_callee=false`는
    **거짓 음성**이다. `0x465287` depth는 `0x46527f`의 `je` 선행자로 고정된다
    (`call DWORD PTR [ecx+0x28]`의 인자 정리는 정적으로 미상).
  - **R3 결함 원인:** lap305 line 104 `entry_offset = raw_offset + delta`. esp는 아래로 움직이므로
    entry 오프셋은 `raw - delta`다. lap305는 1차 run의 위양성(local `[esp+4]`)을 **부호를 뒤집어**
    막았고, 그 결과 `sub esp` 이후의 **모든 실제 인자 읽기**가 탐지 범위 밖으로 밀려났다.
  - **R4 신규(정체 확정):** `0x465250`은 **가변인자 로깅 헬퍼**다. arg3=포맷(`[esp+0xc]` → `0x4db933`
    vsprintf), `0x46525a lea eax,[esp+0x110]`=`&arg4`(vararg 포인터), arg1=싱크 객체.
    표본 site 인자 문자열 `0x4ec348='12974'`, `0x4ec350='kind:%d sx:%d dy:%d'`.
    → 291 site는 화면 기하 writer를 **의미적으로도** 운반할 수 없다.
  - **R5 CONFIRMED:** 절대 writer **4** (`0x431b79`/`0x431b7f`/`0x4324b8`=0x280/`0x4324c2`=0x1e0),
    mode-table immediate writer **16**, **하한 20 유지**. jump table `0x464B68`=
    [`0x4644c8`,`0x4644db`,`0x464502`,`0x464529`,`0x464550`,`0x4644eb`,`0x464512`,`0x464539`],
    `ds:0x4ED810` 초기값 **3**, 참조 6건 전부 읽기·쓰기 0 → `table[2]=0x464502` → **800×600**
    (lap304 R6 독립 재현). 5해상도 320×200/640×480/800×600/1024×768/1280×1024도 재확인.
  - **R5 신규 정정:** moffs 짧은 저장(`a2`/`a3`)은 **이 이미지에 실재한다**(예: `0x401db3`
    `mov ds:0x8924c4,eax`). STATUS의 "a3 형태 … 이 이미지엔 없음"은 부정확하다. 정확한 사실은
    **화면 전역 `0xE5BF1C`/`0xE5BF20`을 대상으로 하는 moffs 저장이 0건**이라는 것이며,
    이 probe는 modrm과 moffs 두 인코딩을 모두 매칭해 4를 재확인했다. V3의 해당 항목은 여기서 닫힌다.

  **종합 판정: lap305 V1 = ACCEPT-WITH-CORRECTION.** 수치 결론(291/단일 callee/추가 writer 0/하한 20)은
  독립적으로 재현돼 **유효**하다. 이를 뒷받침한다고 적힌 "arg1/arg2 미접근·객체 미소비" 주장은 **REJECT**이며,
  근거는 R4의 의미적 분류(로깅 헬퍼)로 교체해야 한다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  `0x465284`의 가상 호출은 `[obj+0x1518]` 멤버로 디스패치하므로 그래픽 객체 자체를 forwarding하지
  않지만 **여전히 fail-open**이며, lap305는 이 경로를 "도달하지 않음"으로 잘못 분류했다.
  `callee_body`의 first-`ret` 절단은 구조적 fail-open이다 — 이번엔 `0x465250`(다음 함수 `0x4652b0`,
  본문 밖 분기 없음)과 `0x4644A0`(첫 `ret`=`0x464826`, 16 writer는 그보다 앞)에서만 적정함을 확인했다.
  computed pointer / 간접 디스패치 / visible body 밖 경로는 미해결. 제품 G1~G4 PASS, Stage B,
  마일스톤 승인은 **없다**. 20은 확인된 하한일 뿐 제품 완료가 아니다.

- 다음 한 가지: 다음 새 work(Luna/Sonnet5/high)가 V2를 **새 파일**에서 수행한다 —
  `FUN_00431AB0`의 `0x4324B8`(640×480 고정)·`0x431B79`(런타임 값) writer 실행 조건과
  다이얼로그 구성(`0x4D6312`) 대비 순서를 정적으로 유도한다. 같은 probe에 R3 부호 수정
  (`raw - depth` + 분기 join depth)을 회귀로 포함한다. lap305 산출물은 보존하고 고치지 않는다.
  V3는 그 다음 별도 work이며 moffs 항목은 lap306 R5가 이미 닫았다.
  게임/Wine/Xvfb/Stage B/runtime/PNG/클릭 실행과 기존 산출물 수정은 계속 금지.
