# 2026-09-11 | lap 82 이후 | STATUS compaction 기록

`docs/STATUS.md`가 다시 180줄에 도달해 다음 검수의 안전 여유가 없었다. 현재 판정과 lap81 이후 최신 이력은 유지하고, 아래 lap73~80 상세를 이 파일로 이동했다.

- 이동 전 `docs/STATUS.md` SHA256: `fb1a6fb4cd1bb808ce669d3cb0fe3f7e513dd3135caa4540379e1809dd7861f0`
- 각 lap 원문은 `docs/history/laps/`에도 보존된다.
- 코드, 하네스, 게임, EXE, DLL, 자산, runtime artifact는 변경하지 않았다.

## 이동한 원문

- lap73은 새 private run `local/runtime/20260911_082430_2926029_0`를 prepare/check하고 fixed baseline을
  정확히 1회 수행했다. manifest `81455eeea2ab0a5c6c72f3904a2ea42e88192120d3acae7cd5790e39aacaecce`,
  baseline `a46f4c659c7e2482ca7371caa0478883b48fffa6bef42e743e6a7b275615198e`, verdict
  `210560e5992eee1e5666d95ad9ec8fb82c1e0f545e74e8d07771752bffba01be`, private/original EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`다. primary predicate false로
  production click은 차단됐고 cleanup PASS; `make check` **127 passed**, safety/doctor-runtime PASS다.
  제품 PASS가 아니며 middle 독립 검수 대기다.

- lap74는 lap73 manifest/baseline/verdict/provenance/harness와 원본·private EXE SHA, 8개 PNG SHA를
  재계산 일치시켰다. visual은 원본 800x600 장면과 selection 변화를 확인했으며 2배 출력 증거는 아니다.
  직접 no-click/output **3 passed**, 전체 `make check` **127 passed**, Ruff/compileall/mypy/context PASS,
  safety **SAFETY_PASS**, doctor와 manifest-required doctor `ok=true`다. lap73 evidence/cleanup/fail-closed
  경계는 **MIDDLE CONFIRM PASS**, G1-A overall과 제품 G1~G4 및 사용자 승인은 미완료다.

- lap75는 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`와
  `499583/4A3A40/4A3B5B/49B6D0/41F630/49B530/49B640/41FA60` old bytes를 독립 추출했다.
  primary field source와 12-slot 사용은 PASS지만 primary-to-cell/worker edge는 UNKNOWN,
  game run 및 구현은 SKIP이다. `make check`는 기록 전 **127 passed**다.

- lap76은 같은 원본 SHA와 8개 entry old bytes를 재계산 일치시키고 direct xref에서
  `0x0049B6D0` call 1개(`0x004992DF`), `0x0041F630` call 8개, primary consumer 범위의 관련 call
  0개를 확인했다. 기록 전·후 Fast 각각 **127 passed**, safety/doctor PASS; 구현·게임 실행은 SKIP이다.
- lap77은 A6/BE/D6/EE read→branch/callee 표와 old bytes를 기록했다. `make check` **127 passed**,
  Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**, doctor top `ok=true`/original verified;
  runtime manifest 없는 상태의 runtime `ok=false`는 새 게임 실행 없이 보존했다. 구현·게임 실행은 SKIP이다.

- lap78은 원본 SHA·8개 old bytes·direct xref와 지정 범위를 재추출해 대부분을 확인했지만 EE instruction
  site가 `0x0049AF28`임을 확인해 lap77 exact trace를 **REVISE / ESCALATE**했다. 기록 전·후
  `make check` 각각 **127 passed**, Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**, doctor
  top `ok=true`/original verified다. manifest 없는 runtime `ok=false`는 예상 경계로 보존했고
  코드/tests/binary/fixture/좌표/game run은 변경하지 않았다.

- lap79는 같은 원본 SHA에서 지정 6개 entry old bytes, relevant direct callsite, `0x00419D80/0x00419E40`
  의 `0x004664D0/0x00466540` write, `0x00465E80` bounded byte write, `0x004179D0`의 direct/indirect
  calls를 재추출했다. 기록 전 `make check` **127 passed**, safety **SAFETY_PASS**, doctor top
  `ok=true`/original verified다. game run·후보 binary·fixture·좌표·source/tests 변경은 SKIP이며,
  indirect sink 때문에 enqueue exclusion은 UNKNOWN으로 보존한다.

- lap80은 같은 원본에서 lap79를 독립 재추출해 buffer/render 흐름과 callsite를 확인하고
  `0x004E5190=KERNEL32!lstrlenA`로 해당 indirect enqueue를 배제했다. 그러나 `0x00419D80` 행은
  잘못 조합된 15B, `0x00419E40` 행은 15B 누락이라 **MIDDLE CONFIRM REVISE / ESCALATE**다.
  `make check` **127 passed**, Ruff/compileall/mypy/context, safety, doctor top `ok=true`/original verified;
  runtime/game/candidate/fixture/좌표/source/tests 변경은 SKIP이다.

