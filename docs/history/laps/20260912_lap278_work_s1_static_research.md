# 2026-09-12 | lap 278 | G1 S1 저장/불러오기 정적 조사

- 실제 provider/model/effort / 지정 역할: Codex work tier 계약(Luna/high 지정). 현재 세션에서
  외부 subagent/provider를 호출하지 않았다. hands-on 범위는 읽기 전용 조사와 연구 산출물
  문서화이며 게임 구현은 하지 않았다.
- 가설 / 사용자 관찰: 원본 저장/불러오기 경로가 S1 여섯 항목을 함께 복원할 정적 근거를
  제공하는지 확인한다. 사용자 신규 관찰 없음. lap 파일 값 `loop/.lap_counter=278`을 사용했다.
- 예상 PASS / FAIL 조건: §4 양성 기준 (i)/(ii)를 항목별 적용. 결측·포맷 불명·과거 evidence의
  비연결은 UNKNOWN이며 PASS로 승격하지 않는다. 여섯 항목 전체를 입증하지 못하면 research
  blocker를 남긴다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md`에 §4.1 결과표 추가,
  `docs/STATUS.md` 갱신, 본 기록, `loop/ESCALATE_SOL` lap278 항목 추가. 게임 코드,
  comparator, producer, tests, 원본 EXE/DLL/assets는 변경 0. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
  조사 당시 SHA: original EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  `tools/runtime_env.py` `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`,
  `tools/compare_g1_stage_b.py` `9b684cec7b9fd284aed88e9c063e903c6fcd7322946bee6644541f32e426efdb`,
  `analysis/memory_maps/population_runtime_bridge_0910.md` `96eb29ab93515293fd0d097ecd0b85bddbdd0c4e8e7ddfbf68cfaf1da1d1fb68`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE SHA 위와
  동일, 후보 없음. 상위 원본 읽기 전용 저장 자산 `.../Syw2plus/save/save000.dat`
  SHA `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`, 3,093,902 bytes;
  `save006.dat` SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`,
  3,437,942 bytes. 둘 다 `file: data`, 헤더와 날짜 문자열만 확인했고 파싱하지 않았다.
  환경 `.venv`/Linux 정적 도구, 게임 실행 0. 활성 플레이어·지도·군대·runtime fixture 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `objdump -D -Mintel -j .text --start-address=0x440c20 --stop-address=0x440ff0 Syw2plus/syw2plus_original.exe`
  및 load 범위 `0x440ff0..0x442e00`; `strings -a -n 4 ... | rg -i 'save|load|dat|slot'`;
  `sha256sum`/`file`/`xxd`는 읽기 전용. 확인된 path builder `0x440A80`의
  `%ssave\\save%d%02d.dat`, save `0x440C20`, load `0x440FF0`, map block
  `0xB3DDA8 + 0xB0`; load 후 `0x441381/0x44138A`의 bounds 참조. Fast:
  `make check` → **291 passed in 44.39s**, Ruff/compileall/mypy(10 files) 성공,
  `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
  PNG/capture 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): §4.1 여섯 행을 채움. item 1 nation/player,
  2 type/count, 3 relative position/multiplicity, 5 engine slot, 6 selection/camera/tick은
  UNKNOWN. item 4 world bounds만 CONFIRMED: load serializer가 map block을 읽고 승인 주소
  `0xB3DE34/0xB3DE36`가 그 block의 `+0x8C/+0x8E`이며 후속 load code가 직접 참조한다.
  저장 파일 내부 구조와 과거 `patches/population/verification_0910/*.json`의 1:1 대응은
  확인되지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(코드·검사 규칙 무변경).
  연구 blocker는 expected contract output이며 제품 G1 PASS, Stage B 허가, runtime pair,
  milestone 승인이 아니다. 다음 새 middle이 original SHA, entry disassembly, save hashes,
  six-row 판정을 독립 재계산해야 한다. owner8~15 blind spot, WM_CLOSE, G2~G4 등 이전 위험
  유지. 사용자 마일스톤 승인 없음.
- 다음 한 가지: next fresh middle independent review. 승인 전에는 serializer call-graph
  static probe 또는 별도 상위 승인된 runtime pair 외의 실행을 열지 않는다.
