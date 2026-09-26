# 2026-09-12 | lap 292 | G1/S1 lap291 probe 수리 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 0, 구현 모듈 변경 0. 검수용 middle probe만 새로 썼다.
  `loop/.lap_counter`는 `292`이고 PROMPT 규칙대로 그 값을 lap 번호로 썼다. 러너가 주입한
  runtime evidence 블록은 `lap=291`이라 한 칸 어긋나 있다. 파일은 읽기만 했고 쓰지 않았다.
- 가설 / 사용자 관찰: lap291이 lap290 §4.4.3 사양대로 lap280 probe를 수리했다면,
  (a) 수리본이 보존된 lap280 보고서를 바이트 동일하게 재현하고 (b) 동행 4종이 불변이며
  (c) 상수 정의/이름 결합이 깨진 모든 경우에 예외가 아니라 명명된 failure로 exit 1이어야 한다.
- 예상 PASS / FAIL 조건: PASS = 다섯 SHA 일치 + fresh stdout이 `logs/lap280/s1_crossverify_probe.json`과
  바이트 동일 + 동행 4종 SHA 일치 + 자체 mutant 4종이 Traceback 없이 exit 1 + control이 exit 0.
  FAIL = 값 변화(→ 수리가 아니라 새 사실) 또는 예외로 죽는 경로 존재.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap292_middle_lap280_repair_review_probe.py`
  SHA `2aaac7a08619cc4135f4540582e611d07aa980e5380b5ec5255688cf33491335`.
  신규 `logs/lap292/middle_lap280_repair_review.json`
  SHA `b2f7b2174c2e54515baa5227987c34aa58c4d82d2898302c3458bd6b0faa2cfc`.
  갱신 `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.5 추가(middle 소유 파일),
  `docs/STATUS.md`. work 소유 파일·구현 모듈·원본·fixture·baseline·golden 변경 0.
  커밋 없음 (`LOOP_ALLOW_COMMITS=0`, 저장소에 커밋 자체가 아직 0건).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기 전용).
  후보 EXE 없음. Linux `.venv`, `objdump`, 정적 바이너리만. 활성 플레이어/지도/군대/save fixture
  없음. 게임/Wine/Xvfb/Stage B/runtime 예산/PNG 0. mutant는 임시 디렉터리 사본(EXE는 symlink).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`
  → exit 0, `failures=[]`, stdout SHA `3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126`,
  보존본 `logs/lap280/s1_crossverify_probe.json`과 **바이트 동일**.
  동행: lap279 `e848c940…c9db2ddd`, lap282 `e0f07f3a…46f4be08`,
  lap284-middle `2870383083…73d52d60`, lap284-work `7381b5f7…a5cbfb81` — 기록과 전부 일치.
  `.venv/bin/python …lap292_middle_lap280_repair_review_probe.py` → exit 1,
  보고서 `logs/lap292/middle_lap280_repair_review.json`(`b2f7b217…0faa2cfc`).
  `diff -u logs/lap290/diagnosis/lap280_scratch_lap290.py <수리본>` → `REPO` 한 줄 + 대상 블록만.
  `make check` **292 passed in 48.54s**, Ruff `All checks passed`, compileall,
  mypy 10 files `Success`, `CONTEXT_PASS`; `checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **ACCEPT-WITH-CORRECTION.** §4.4.3 여덟 항목 중 일곱은 ACCEPT, 항목6은 요구된 두 mutant에 한해
  ACCEPT. 측정 사실 무드리프트: literal blocks 21, non-literal 1, fwrite/fread 22/22,
  layer serializers 28(pair_deltas {48,64,80,96,160}), x `0x66BA32` WORD 115,
  y `0x66BA34` WORD 115, internal_id `0x66BA2C` DWORD 67, G3 overflow `0x1B5A4`.
  자체 mutant: control exit 0(저장소 run과 같은 SHA), 값 드리프트 exit 1, literal 회귀 exit 1,
  잘못된 상수 결합 exit 1. **정정 1건:** `G1_UNIT_Y_OFFSET` 정의를 지운 mutant는
  `KeyError: 'y'`(line 149)로 죽어 stdout 0바이트다 — 수리가 넣은 "definition missing" 분기가
  뒤따르는 튜플 가드의 무조건 인덱싱 때문에 도달 불가다. lap290이 고친 것과 같은 결함 계열
  (`NoneType.group` → `KeyError`). 현재 저장소 상태에서 수치 영향은 0이다.
  교차 확인: §4.4.3이 모델로 지목한 lap282 probe는 부분 문자열 대조라 같은 결함이 없다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  이 검수는 static probe 하네스의 건전성만 본다. S1 실제 결정성, 두 run의 값 동일성, Stage B,
  runtime 예산, WM_CLOSE, G3 저장 포맷 `0x1B5A4` 초과, 제품 G1~G4는 전부 미해결이고
  **S1 카드 종결은 REJECT 유지**다. 사용자 마일스톤 승인 없음.
  잔여 반증력 사각(수리 요구 아님): 이름 결합 단언이 reader 함수 이름을 보지 않아
  `x=i(G1_UNIT_X_OFFSET)`류 WORD/DWORD 폭 드리프트는 통과한다.
  lap290이 남긴 "probe 52개 중 42개가 구현 모듈 경로 참조, 실행 대조 미완" 사각은 그대로다.
  lap279/lap280/lap284-middle probe의 `0x440FF0` legacy window 사각도 그대로다(수치 영향 0).
- 다음 한 가지: work tier(Luna/Sonnet5)가 §4.5.3 정정 1건을 수리한다. 성공 조건은
  정상 run이 여전히 `3d4fe307…6a6d6a9126`·동행 4종 불변이고
  `…lap292_middle_lap280_repair_review_probe.py`가 exit 0이 되는 것이다.
  Stage B/runtime 예산/게임·Wine·Xvfb 실행/카드 종결/PASS 규칙 변경은 금지.

## 세션 종료 시 파일 해시 (uncommitted, `LOOP_ALLOW_COMMITS=0`)

- `docs/STATUS.md` `873b11008df6d55fc4ff7019c5cd3ea7fcbbd247644689014876a661da76e8e2` (130줄)
- `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` `4b10b7c355ba2bdabf6a6e3fde45014fe71fb3990bdffad9f4280d9f8c9cf7bf`
- `docs/history/laps/probes/20260912_lap292_middle_lap280_repair_review_probe.py` `2aaac7a08619cc4135f4540582e611d07aa980e5380b5ec5255688cf33491335`
- `logs/lap292/middle_lap280_repair_review.json` `b2f7b2174c2e54515baa5227987c34aa58c4d82d2898302c3458bd6b0faa2cfc`
- 무변경 확인: 대상 probe `100f991b…cb999f84`, `tools/runtime_env.py` `dd2ad043…8500190`,
  `patches/population/runtime_driver.py` `ae4ff939…4e4291b5`, 원본 EXE `b56986e0…c9c08a8ac`.
- STATUS는 130줄로 예산 안이라 압축 이벤트가 없다. 기존 항목을 지우지 않고 이번 lap 추가분만 줄였다.
- `loop/ESCALATE_SOL` 없음: 필수 게이트 전부 PASS, 증거 충돌 없음, 마일스톤 경계 아님,
  발견한 정정은 middle 권한 안에서 work tier 사양으로 인계했다.
