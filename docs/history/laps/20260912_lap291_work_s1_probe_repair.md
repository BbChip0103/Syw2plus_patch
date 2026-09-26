# 2026-09-12 | lap 291 | G1/S1 lap280 교차검증 probe 하네스 수리

- 실제 provider/model/effort / 지정 역할: Codex work tier / hands-on 구현 작업자 / high.
  구현은 승인된 work 범위의 probe 한 블록에 한정했다. 게임 구현·게임 실행·middle 승인 0.
- 가설 / 사용자 관찰: lap280 probe의 `NoneType.group`은 lap281이
  `runtime_driver.py`의 세 16진 리터럴을 `runtime_env.py` 상수명으로 승격한 뒤 과거 probe가
  옛 소스 텍스트에 결합해 생긴 하네스 결함이다. 값을 중앙 정의에서 읽고 driver의 이름 결합을
  별도로 단언하면 측정값을 보존하면서 같은 드리프트를 검출할 수 있다.
- 예상 PASS / FAIL 조건: 세 상수 정의를 `^NAME = 0x…$`로 읽고 driver의
  `field=reader(NAME)` 결합을 확인한다. 정상 run은 exit0/`failures=[]` 및 기존 보고서 SHA를
  재현해야 하며, 환경값 mutant와 driver 이름 mutant는 각각 exit1이어야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`의 지정
  line 126-133 블록만 수정. 변경 SHA `100f991b3abfa6d075a35facf9a9e479c1d2092ebb4d6245688cfe73cb999f84`.
  `tools/runtime_env.py` SHA `dd2ad043…8500190`, `runtime_driver.py` SHA
  `ae4ff939…4e4291b5`는 변경하지 않았다. 커밋 없음 (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  후보 EXE 없음. Linux `.venv`, `objdump`, 정적 original binary; 활성 플레이어·지도·군대
  없음. 게임 fixture/Wine/Xvfb/Stage B/runtime 예산/원본 쓰기 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`
  → exit0, `failures=[]`, JSON SHA `3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126`.
  환경 상수를 in-memory `G1_UNIT_X_OFFSET=0x2A3`으로 바꾼 mutant → exit1
  (`runtime_driver unit offsets drifted`, `no base-relative reference`). Driver의
  `x=h(G1_UNIT_X_OFFSET)` 이름을 in-memory literal로 바꾼 mutant → exit1
  (`runtime_driver does not bind x to G1_UNIT_X_OFFSET`). 원본 보존 artifact와 동행한
  lap279/lap282/lap284-middle/lap284-work 출력은 각각
  `e848c940…`, `e0f07f3a…`, `2870383083…`, `7381b5f7…`로 바이트 동일.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  수리 범위 PASS. 정상 측정값은 literal blocks 21, CRT fwrite/fread 22/22,
  layer serializers 28, x/y `0x66BA32`/`0x66BA34` WORD 115회,
  internal_id `0x66BA2C` DWORD 67회, G3 overflow `0x1B5A4`로 기존과 동일하다.
  targeted `py_compile`/Ruff PASS. `make check`: **292 passed in 45.12s**, Ruff/compileall/
  mypy 10 files PASS, `CONTEXT_PASS`, `SAFETY_PASS`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  수리 대상은 static probe뿐이며 G1 제품 증거, 두 runtime 값 동일성, Stage B, WM_CLOSE,
  G2~G4를 증명하지 않는다. 창 상수·comparator·producer·PASS 규칙과 원본/fixture는 무변경.
  다음 새 middle이 파일 SHA, 정상/동행 출력, 두 mutant 반증력을 독립 검수해야 하며,
  사용자 마일스톤 승인과 S1 카드 종결은 없다.
- 다음 한 가지: 다음 새 middle 세션의 독립 검수. ACCEPT 전까지 Stage B/runtime 예산,
  게임/Wine/Xvfb 실행, 카드 종결을 금지한다.
