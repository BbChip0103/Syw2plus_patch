# 2026-09-11 | lap 92 이후 | STATUS compaction 기록

`docs/STATUS.md`가 175줄에 도달해 다음 검수 기록의 안전 여유가 부족했다. 현재 판정과 lap92 최신 이력은 유지하고, 아래 lap87~91 상세를 이 파일로 이동했다.

- 이동 전 `docs/STATUS.md` SHA256: `f867068941519f1ec5d2267bb77d06e0adab833728a89beafae55ca289c50cb8`
- 각 lap 원문은 `docs/history/laps/`에도 보존된다.
- 코드, 하네스, 게임, EXE, DLL, 자산, runtime artifact는 변경하지 않았다.

## 이동한 원문

- lap87은 원본 두 사본의 동일 SHA/byte identity와 `.text` 매핑, 유일 caller,
  `+0x6B9C` read 3/경계 compare 1, `+0x6BA0` read 3 및 generic callee 경계를 확인했다.
  반면 `+0x6B9A` reset/write는 기존 2개 외 `0x004A31F2`, `+0x6BA4` read는 기존 6개 외
  `0x0041EFA5`가 확인되어 lap86 completeness는 FAIL/REVISE다. `make check` 127 passed,
  Ruff/compileall/mypy/context와 safety PASS, doctor `ok=true`/original verified다;
  후보/game/fixture는 SKIP이다.

- lap88은 동일 원본 SHA/cmp와 `.text` 매핑을 재확인하고, `+0x6B9A` reset 3개(+ writer
  count write 1), `+0x6B9C` read 3/compare 1, `+0x6BA0` read 3, `+0x6BA4` read 7/compare 1을
  확인했다. `0x004AC3E0→0x004AA820`, `0x004AE550→0x004A3C10`, `0x004AEC2F` 경계는
  재분류했지만 production edge는 없어 static PASS / semantic UNKNOWN이다. `make check` 127
  passed, Ruff/compileall/mypy/context와 safety PASS, `make doctor` top `ok=true`/original
  verified다. 후보·game·fixture는 SKIP이며 상세는
  `docs/history/laps/20260911_lap88_luna_g1a_exact_record_consumer_correction.md`다.

- lap89 middle은 동일 SHA/cmp/PE 매핑, 유일 caller, raw occurrence/old bytes와 branch/callee
  경계를 독립 재추출했다. lap88 표는 PASS이고 `+0x6BA4`는 일반 read6+compare1=총 참조7로
  정밀화했다. 후보·game·fixture는 SKIP이며 production 의미는 UNKNOWN/BLOCKED다. `make doctor`
  top `ok=true`/original verified, `make check` 127 passed와 safety `SAFETY_PASS`다. 상세는
  `docs/history/laps/20260911_lap89_sol_g1a_exact_record_consumer_confirmation.md`다.
