# 2026-09-12 | lap 203 | G1 R5-A+R5-C 독립 검수 및 Stage B 페어 run 인가

- 실제 provider/model/effort / 지정 역할: middle tier (진단·계획·확인).
  Claude Code `claude-opus-5` / high, `LOOP_PERMISSION_MODE=auto`.
  **구현 0. 게임 실행 0. Stage B 실행 0.** (`loop/.lap_counter`=203, 루프 배너 lap=202로
  lap201부터 이어진 1 어긋남을 그대로 기록한다.)
- 가설 / 사용자 관찰: lap200(R5-A)과 lap202(R5-C)가 남긴 선택 개체 identity reader는
  (a) 열거된 실패 부류만 비치명 UNKNOWN+provenance로 보존하고, (b) 실제 주입 reader가
  `_g1_run_input_sequence`를 통과해 디스크 evidence까지 도달하며, (c) 술어·예산·`overall`
  fail-closed 불변식을 바꾸지 않는다. 참이면 이 바퀴가 Stage B 페어 run을 인가한다.
- 예상 PASS / FAIL 조건:
  PASS = 자체 probe에서 `except Exception` 부재·열거 부류만 catch, 진짜 프로그래밍 오류 전파,
  `_CommandCellSnapshotError` 경로 무회귀, 4단계 전부 실행, slot/type이 flush된 파일에 존재,
  `required_inputs=False` 유지, 새 오프셋 0, 예산 10/10/10·31.5 불변, 양쪽 주입 지점 동일.
  FAIL = 위 중 하나라도 어긋나거나 필수 게이트 재현 실패.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`(lap203 판정·인가 추가),
  `loop/ESCALATE_SOL`(lap203 블록), 이 기록,
  `docs/history/laps/probes/20260912_lap203_r5c_probe.py`(신규, 검수 증거).
  **source/tests/EXE/DLL/assets/baseline/golden 변경 0.** 커밋 없음(`LOOP_ALLOW_COMMITS=0`), uncommitted.
  검수 대상 무변경 해시 (lap202 자기신고와 대조 목적):
  - `tools/runtime_env.py` `3add9254f8df892292619940310a40cd38a95b1fd15605da5fd2c9d1f1f2f2c1`
  - `tests/test_runtime_env.py` `aa2d2a4326dea1cda9ac866c0e621cf7f4d9c4aa9c8483b0810a88807127ae15`
  - probe `2235b23cea86fa1f0a9c30f86cdf1f8327718f499206dde1b5877d9579c5dea8`
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 핀 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 일치
  (`check_setup` 보고값 = `tools/runtime_env.py:159` = `tools/check_binary_contract.py:20`).
  게임 0회이므로 활성 플레이어·지도·군대 해당 없음. 오프라인 합성 주소 reader fixture만 사용
  (count/first_slot/exists/type 4개 주소, 실제 프로세스 메모리 접근 0).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `make check` → **221 passed**, Ruff PASS, compileall PASS, mypy **Success (9 source files)**,
    `CONTEXT_PASS`, exit 0.
  - `LOOP_DRY_RUN=0 bash checks/safety.sh check` → **`SAFETY_PASS`**.
  - `.venv/bin/python tools/check_setup.py --require-game` → exit 0,
    `ok:true`, `original_status:"verified"`, `missing_tools:[]`, `missing_libraries:[]`.
  - `df -h /home/dev_00/sharedfolder` → **276G avail** (run≈2.7G, 페어≈5.4G).
  - `.venv/bin/python docs/history/laps/probes/20260912_lap203_r5c_probe.py`
    → **PROBE PASS — 63 assertions**.
  PNG 0장, 게임 로그 0, Stage B 캡처 0.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **R5-A+R5-C 독립 검수 PASS. Stage B 페어 run 인가.**
  probe 근거(테스트 본문 재사용 없음, AST+행동 혼합):
  - D1: `_read_g1_selection_evidence`의 except 핸들러는 **1개**이고 catch 집합은 정확히
    `{_CommandCellSnapshotError, OSError, struct.error}`다. bare except·`Exception`·`BaseException`
    없음. 주입한 `TypeError`는 **그대로 전파**된다(삼킴 없음).
  - D1 무회귀: 비활성 slot은 여전히 `_CommandCellSnapshotError: ...` 문구로 UNKNOWN이 되고
    `first_slot`을 보존한다. `_read_selection`·`_read_g1_command_selection_identity`에는
    except 핸들러가 하나도 없다(기존 예외 계약 불변). count 주소 읽기 실패는 R5-A 이전과 같이
    치명으로 남는다(폭발 반경 확대 없음).
  - D1 수리 확인: exists 주소/type 주소 각각에서 `OSError`·`struct.error` 4조합 모두
    비치명 UNKNOWN+provenance이며 `first_slot`을 보존한다.
  - D2: 실제 `_read_g1_selection_evidence`를 `_g1_run_input_sequence`에 주입한 end-to-end에서
    `unit_select→production→drag_select→minimap` **4단계 전부 실행**. 성공 fixture는
    `unit_select.before` UNKNOWN/None, `unit_select.after`·`drag_select.after`에 slot 7/type 58,
    그리고 그 값이 **flush된 디스크 JSON에 존재**한다. 실패 3종(snapshot/OSError/struct.error)도
    4단계 전부 실행하고 UNKNOWN+provenance를 디스크에 남긴다.
  - 세탁 없음: 네 경우 모두 `_g1_input_verdict(..., enabled=True)`가
    `required_inputs=False`, `production_blocked=True`.
  - 새 오프셋 0: 성공 경로가 읽은 주소는 `0x00899024`/`0x00899028`/`0x008990D6`
    (=`G1_UNIT_EXISTS_BASE+7*2`)/`0x0066EB85` (=`0x0066B790+7*0x758+0x8D`) **4개뿐**이고
    상수는 lap57·lap61 문서값과 같다. `count==0`이면 개체 상세를 읽지 않는다.
  - 술어·예산 불변: `G1_INPUT_STAGE_BUDGETS == {10.0,10.0,10.0}`, 합 **30.0**,
    `G1_INPUT_PHASE_WALL_CLOCK_BUDGET == 31.5`, 시퀀스 소스에 `count>=1`/`count>=2` 각 1회,
    시퀀스·verdict 어디에도 `selected_slot`/`selected_type` 술어 없음.
  - 대칭: `read_selection=` 주입 지점은 파일 전체에 **2개**뿐이고 두 줄 모두
    `read_selection=lambda: _read_g1_selection_evidence(read_for_process),`로 **문자열 동일**.
  - lap201이 요구한 저장소 회귀테스트 1·2·4는 실제로 추가됐다:
    `tests/test_runtime_env.py:1278`(주입 reader→디스크 evidence, baseline/후보 2회 실행 후 대조),
    `:1306`(snapshot/oserror/struct_error 3-parametrize, 후속 drag/minimap 실제 실행 단언),
    `:1328`(상수·술어 값 고정). 헬퍼 `:1199`는 합성 dict가 아니라 진짜
    `runtime_env._read_g1_selection_evidence`를 호출한다 — lap201이 지적한 "주입 reader를
    통과하는 저장소 테스트 0개" 구멍은 메워졌다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **비블로킹 관측 O1 (R5-D로 발행).** 카드 D2-1의 하위 조항 "baseline·후보 주입 지점이
    동일 reader임을 단언"은 **저장소 테스트로는 여전히 없다**. `:1278`은 같은 헬퍼를 두 번
    돌려 결과를 대조할 뿐 `tools/runtime_env.py`의 두 호출 지점을 검사하지 않는다. 이번 바퀴
    probe가 소스 수준에서 확인했으나 probe는 게이트가 아니다. **Stage B를 막지 않는다** —
    이번 인가는 위 해시로 고정된 현재 소스에 대한 판정이고, 이 항목이 막는 것은 미래의 편측
    변경이다. lap201의 D2와 달리 주입 경로 자체는 이제 저장소 테스트가 덮는다.
  - **비블로킹 관측 O2.** `struct.error.__name__`은 `"error"`이므로 provenance가
    `"error: unpack requires ..."`로 남아 예외 종류가 한눈에 구분되지 않는다. 카드가
    `f"{type(exc).__name__}: {exc}"` 형식을 못박았으므로 구현은 계약대로다. Stage B evidence를
    읽을 때 이 문자열을 `struct.error`로 해석해야 한다.
  - 기존 위험 유지: R5-B 비교기 부재(비블로킹), WM_CLOSE teardown 결함, random seed 미노출,
    minimap camera 절대 목적지 비교 필요, 25% 잘림 임계값은 첫 실제 run으로 재평가할 가정.
  - 사용자 승인 상태: APPROVALS 2026-09-12 01:03 KST 실행 승인 범위 안이다. 제품 G1 합격·출시,
    P6, G2~G4는 여전히 미승인이며 이 인가로 바뀌지 않는다.
- 다음 한 가지: **work tier — Stage B 페어 run 1회.** 원본 1회 + 후보 1회, 각각 새
  copy/prefix/display, exact-once. 계약 전문은 카드의 「lap203 middle 판정 — Stage B 인가」.
