# 2026-09-11 | lap 92 | G1-A event-ring binary contract test

- 날짜/lap/목표: 2026-09-11 / lap 92 / G1-A `0x004AC420` guard의 정적 계약을 고정한다.
- 역할/가설: 지정 역할은 hands-on work-tier다. lap91의 REVISE를 고정 SHA 거부, guard 범위,
  상대 jump target, call/skip truth table로 기계화하면 문서 해석 오류의 재발을 막을 수 있다.
- 예상 PASS / FAIL 조건: 두 고정 원본 SHA/cmp/PE 매핑, guard bytes와 branch/call target이 일치하고,
  1-byte drift 후보가 거부되며 truth table 회귀가 통과하면 static PASS; 불일치면 REVISE/ESCALATE다.
- 변경 파일 / source fingerprint / 커밋: `tools/check_binary_contract.py`,
  `tests/test_binary_contract.py`, `analysis/memory_maps/player_offsets.md`, `docs/STATUS.md`,
  `loop/ESCALATE_SOL`, 본 이력. 원본/참고 EXE·후보·game source·fixture·좌표는 변경하지 않았다.
  source SHA는 tool `8c670156c8eaf92496b15382818ce1feb917e7939e2136738556c2ae5a1a95bf`, test
  `d453ae6aab5615686fff8e2d3895ccdbe191605a4ce547536ce3335353588fac`다(문서 최종 hash는 아래
  명령으로 재확인). `LOOP_ALLOW_COMMITS=0`, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본과
  `local/runtime/20260911_082430_2926029_0/game/syw2plus_original.exe` 모두 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp` PASS; PE32 i386
  `.text` VA/raw `0x00401000/0x1000`; 후보·플레이어·지도·군대·fixture N/A/SKIP.
- 실행 명령 / 근거: `sha256sum`, `cmp`, `file`, `objdump -h`, `objdump -d -Mintel`, `xxd`,
  read-only direct-E8 scan으로 `0x004AC420` caller와 `0x004AC4DA→0x004AA8D0`을 재추출했다.
  계약은 `0x004AC47F..0x004AC4DF` 97B 및 5개 relative branch target을 검사하고,
  임시 복사본의 branch 1-byte drift를 SHA mismatch로 거부한다.
- 측정값 / 판정: caller는 `0x004233AE` 1개, guard branch는
  `0x004AC48E/493/498→0x004AC4C4`, `0x004AC4AD/4C2→0x004AC4DF`, call target은
  `0x004AA8D0`이다. `make check` **134 passed**, Ruff/compileall/mypy/context PASS,
  `bash checks/safety.sh check` **SAFETY_PASS**, `make doctor` top `ok=true`/original verified.
- truth table / 한계: count<=0 skip; count>0에서 mode!=3 또는 field zero는 call; mode=3이고
  두 field가 nonzero일 때 거리 어느 하나 `>0x11`은 skip, 둘 다 `<=0x11`은 call이다.
  이는 machine branch 경로일 뿐 production record/field 의미가 아니다. 실제 입력/runtime·G1~G4·
  사용자 승인은 UNKNOWN/BLOCKED; 후보·game run·fixture는 SKIP이다.
- 다음 행동: 다음 새 Sol/Opus5/high middle이 원본 SHA, old bytes, contract test와 주소 정정을
  독립 검수한다. production direct edge가 확인되기 전 구현·game run·좌표 변경은 금지한다.
