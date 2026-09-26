# 2026-09-11 | lap 59 | 목표 G1-A alternate UI-list raw snapshot 독립 검수

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier Codex `gpt-5.6-sol` / high / review.
  현재 세션 표면은 실제 model ID/effort를 별도 노출하지 않아 실행 증거로 주장하지 않는다.
- 가설 / 사용자 관찰: lap58 helper가 원본 false branch의 alternate UI-list 필드를 정확한 폭과 범위로
  읽고 selection/predicate 전후의 coherent raw snapshot을 보존하며 모든 불일치를 fail-closed한다.
- 예상 PASS / FAIL 조건: 원본 SHA와 raw disassembly에서 count=`unit+0x6BE` WORD, records=
  `unit+0x6C2+4*i`의 WORD 쌍(첫10), flags=`0x00893118+2*i` WORD(10개), geometry=
  `0x009E2BA4..AA` WORD(4개)가 일치하고, source SHA가 lap58과 일치하며, zero/nonzero/bounds/
  identity·predicate·alternate-value-change 회귀와 목표 Fast가 새로 통과하면 CONFIRM PASS다.
  주소·폭·범위·실패 의미가 충돌하거나 필수 검사가 실패하면 FAIL로 보존하고 `loop/ESCALATE_SOL`에
  work-tier 수리 범위와 재검증 조건을 남긴다. 어떤 경우에도 production/G1 제품 PASS로 승격하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현 변경 없음. 본 이력과
  `docs/STATUS.md`만 갱신했다. 검수한 `tools/runtime_env.py` SHA
  `e605e041816856bc88458df8bfad85e2e77cdac40f4ba6cab1e6e7d4e3d32dd5`,
  `tests/test_runtime_env.py` SHA `58ea272f06d78f1edc672d4f569d7a7e3bd6ea0d644f3b68d6a6bd06931e024c`,
  `tests/test_runtime_guards.py` SHA `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`는
  lap58 기록과 일치한다. 게임 코드/helper/tests/원본/좌표/timeout/binary는 수정하지 않았다.
  Git unborn, `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본과 lap56
  private copy SHA가 모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`로
  일치한다. 후보 EXE, 새 Wine/Xvfb/game run, 활성 플레이어/지도/군대는 없음/SKIP이다. fixture는
  lap58의 virtual read-memory selected slot7/type58, count 0/3/11, record·flag·geometry WORD 및
  selection/predicate/alternate value-change 회귀를 독립 재실행했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `file`, 원본 `objdump -d -Mintel`을
  `0x40F770`, `0x413560`, `0x496380`, `0x40FE90`, `0x498E30`, `0x498DB0`,
  `0x4992BE..0x499331`, `0x499E2C..0x499ECF`에 대해 재실행했다.
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py` → **46 passed**;
  `make check` → **116 passed**, Ruff/compileall/mypy/context PASS; `bash checks/safety.sh check` →
  `SAFETY_PASS`. 새 캡처/로그 파일은 없고 binary patch 생성/원복과 actual runtime은 N/A/SKIP이다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): `0x40F770`은 unit base에 `0x6BA`를 더한 뒤
  `0x496380`에서 `+4` WORD를 읽어 count=`unit+0x6BE`다. `0x40FE90`은
  `0x0066BE52 + slot*0x758 + index*4`의 두 WORD, 즉 `unit+0x6C2+4*i`를 검사한다.
  `0x498E30`은 index<10만 `0x00893118+2*i` WORD에 쓰고, hover loop는
  `0x00893118..<0x0089312C` 10개를 순회한다. `0x498DB0`은 WORD
  `0x009E2BA4/BA6/BA8/BAA`를 base_x/base_y/x_pitch/height로 사용한다. helper는 위 고정 블록을
  raw_hex와 해석값으로 before/after 보존하고 count>10 및 selection/predicate/value 변화에서
  fail-closed하며 stable-ineligible은 pool 1회 뒤 즉시 중단한다. **INDEPENDENT CONFIRM PASS**다.
  실제 alternate 값, worker action/production, G1 제품 및 G2~G4는 UNKNOWN/미완료다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: synthetic 계약과 전체 Fast는 통과했으나
  실제 type58/slot1199 alternate snapshot은 아직 없다. raw record/flag는 UI-list 존재 근거일 뿐
  worker 생산 callback 의미가 아니며, 새 실제 run 결과와 사용자 마일스톤 승인은 없다. 이번 검수는
  마일스톤 경계가 아니고 제품 승인도 아니다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 새 `prepare` manifest와 unused private
  prefix/output에서 현재 helper의 고정 `g1-baseline --screen 1600x1200x24 --timeout 90`을 정확히
  1회 실행한다. stable-ineligible의 selection/predicate 및 alternate before/after raw snapshot과
  manifest/output/cleanup 해시를 보존한다. count 0..10/coherent 여부를 기록하되 production PASS로
  승격하지 않고, count>10·값/identity/predicate 변화·snapshot 누락·cleanup 실패는 재시도 없이
  Sol에 이관한다. 좌표/timeout/helper/tests/binary 변경은 금지한다.
