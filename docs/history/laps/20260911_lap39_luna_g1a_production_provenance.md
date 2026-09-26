# 2026-09-11 | lap 39 | 목표 G1-A

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-luna` / high / hands-on work.
- 가설 / 사용자 관찰: lap36의 `(670,490)` 고정 입력은 selected type58 HQ의 실제 production
  command cell인지 정적으로 증명되지 않았다. 원본 PS3 command panel의 hit-test→cell/action
  table→callback을 먼저 추적하면 coordinate 의미와 worker cell의 확정 가능 여부를 판정할 수 있다.
- 예상 PASS / FAIL 조건: 원본 SHA가 고정되고 hit-test, cell geometry, callback, action id의
  VA/raw bytes가 연결되면 static provenance PASS; runtime table/global에 막혀 worker 의미가
  불명확하면 UNKNOWN으로 보존하고 Sol에 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `analysis/memory_maps/player_offsets.md` 장부 기록, `docs/STATUS.md` 상태/다음 한 가지,
  이 기록, `loop/ESCALATE_SOL` handoff만 변경. 커밋 없음/unborn HEAD.
  원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  기록 후 player map SHA `b5e745c1a2823e89c0e3a50a4bf0fbfec0969635c37bb97135f96de6aebb4e33`,
  STATUS SHA `3666fb745f1286645b9acac8bee3cefb7847a53802c8880746730e7e6d84e8fe`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA 고정·읽기 전용;
  후보 EXE SHA N/A(패치 없음); Wine/game run 및 runtime fixture 없음; lap36의 보존 fixture는
  과거 evidence로만 참조하고 새 성공 근거로 사용하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `objdump -D -Mintel` 원본의
  `0x0041F630/0x0041FA60/0x0041FBC0/0x0049B530/0x0049B640/0x0049B6D0/0x0049B9F0/0x004AE550`
  범위를 읽고 VA→raw bytes를 독립 추출했다. 새 게임 실행·캡처 없음.
  `make check` → **99 passed**, Ruff/compileall/mypy/context PASS;
  `bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): `0x0041FA60`가 input WORD
  `[0x004ED814]/[0x004ED816]`와 object `[+8,+C,+10,+14]`를 비교하고,
  `0x0041FBC0`가 hit 후 `object+0x58` callback을 호출하는 chain은 **PASS**.
  `0x0049B530` mapping은 `0x40000→0x19A`, `0x200→0x19C`, `0x80000→0x19E`,
  `0x100000→0x1A1`로 **PASS**. 그러나 `baseX=[0x009E2BAC]`, `baseY=[0x009E2BB0]`,
  `Δ=[0x009E2BB4]+[0x009E2BB8]`, size table `[0x0051EE94/98]`, type58 record
  `[0x0066BE88+58*0x758]`는 runtime/non-file-backed라 `(670,490)`의 실제 cell과
  action의 worker 의미는 **UNKNOWN**. G1/G2/G3/G4와 제품 milestone은 미완료.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본/게임/하네스 회귀 없음; 실행 금지
  계약은 지켰다. 좌표나 icon appearance로 worker cell을 추정하지 않았다. `loop/ESCALATE_SOL`
  기존 handoff를 lap39 blocker로 갱신했으며, 새 Sol/high 독립 검수와 사용자 milestone 승인은
  아직 없다.
- 다음 한 가지: 새 Sol/high가 동일 원본 SHA와 위 raw bytes/field mapping을 독립 재추출하고,
  별도 승인된 runtime read fixture 없이는 좌표 수정·새 game run·하네스/EXE 변경을 하지 않는다.
