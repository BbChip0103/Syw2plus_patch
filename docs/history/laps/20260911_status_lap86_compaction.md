# 2026-09-11 | lap 86 이후 | STATUS compaction 기록

`docs/STATUS.md`가 179줄에 도달해 다음 검수 기록의 안전 여유가 없었다. 현재 판정과 lap86 최신 이력은 유지하고, 아래 lap81~85 상세를 이 파일로 이동했다.

- 이동 전 `docs/STATUS.md` SHA256: `015b8e849ead76819505990f24c97b3211b3339d4fa9ebee3a837fb5d1156b31`
- 각 lap 원문은 `docs/history/laps/`에도 보존된다.
- 코드, 하네스, 게임, EXE, DLL, 자산, runtime artifact는 변경하지 않았다.

## 이동한 원문

- lap81은 같은 원본 두 사본(SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`)에서
  `0x004A3CA0` write-set의 전체 exact offset xref와 primary caller를 재추출했다. `BF6/C22/C24`는
  `0x004A3CA0` 내부 reader/compare뿐이고 `C4E/C64`는 `0x004A3CA0` write 및 `0x004A31xx`
  initializer 외 reader가 없었다. old bytes `4A3CA0=53558b6c240c560fbfc5578bf150e88d`,
  caller `4998F7=e8a4a30000`가 일치했고, `make check` **127 passed**, Ruff/compileall/mypy/context PASS,
  safety **SAFETY_PASS**, doctor top `ok=true`/original verified다. static xref는 PASS이나 worker/action
  consumer는 UNKNOWN/CONCRETE BLOCKER이며 production/game/candidate/fixture/좌표/source/tests 변경은 SKIP이다.

- lap82는 원본 SHA/bytes/xref/caller/callee를 재추출해 lap81 내용에 **MIDDLE CONFIRM PASS**했다.
  기록 전 Fast는 **127 passed**였으나 문서 변경 뒤 최종 `make check`는 STATUS 183>180 때문에
  **114 passed/13 failed**, safety도 같은 overflow로 FAIL했다. 이후 STATUS는 180줄로 줄였지만
  지시대로 재실행하지 않았다. doctor PASS는 실패를 상쇄하지 않으며 game/source/tests 변경은 SKIP이다.

- lap83은 이동 전 STATUS SHA `fb1a6f...61f0`, lap73~80 원문 8개, 압축 기록과
  현재 포인터를 대조했고 검수 시 139줄/기록 후 145줄을 확인했다. `make check` **127 passed**,
  Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**로 lap82 gate를 회복했다. 구현·게임 실행은 SKIP이다.

- lap84는 원본 두 사본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`와
  `41E220/4217B0/41E60C/498F50/41EB75/4A3700` old bytes를 `xxd`로 확인하고,
  `objdump -d -Mintel` 전체 text에서 `41C81E→41E220`, `41E299→4217B0`, `41E60C→498F50`,
  `41EB7A→4A3700` direct xref를 재추출했다. input queue 소비·mouse state 갱신·command queue
  write/count 증가가 연결되어 STATIC CHAIN PASS이며 source/tests/binary/fixture/좌표·game run은 SKIP이다.
  최종 `make check`는 **127 passed**, Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**였고
  `make doctor`는 original verified/`ok=true`; runtime manifest는 없어 실행하지 않았다.

- lap85 middle은 동일 SHA/PE32 원본에서 `xxd`/`objdump -d -Mintel`로 lap84의
  지정 7개 old bytes와 four direct calls을 재확인했다. `0x004217B0`의 event record
  소비와 `0x004A3700`의 3 DWORD write/조건부 count 증가는 PASS, command/action/worker
  의미는 UNKNOWN/REVISE다. `make check` **127 passed**, Ruff/compileall/mypy/context PASS,
  safety **SAFETY_PASS**, doctor top `ok=true`/original verified다. runtime manifest는 없어 실행하지
  않았고 source/tests/binary/fixture/좌표·game run은 SKIP이다.

