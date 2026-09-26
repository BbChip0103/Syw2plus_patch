# 2026-09-12 | lap 206 | 목표 G1 Stage B — R5-B 원본↔후보 비교기

- 실제 provider/model/effort / 지정 역할: Codex work tier / project work routing high; hands-on 구현 작업자.
- 가설 / 사용자 관찰: 기존 Stage B 측정식은 원본↔후보 parity를 요구하지만 비교기가 없어 두 run의
  델타 일치를 기계적으로 산출할 수 없다. 장면 seed가 노출되지 않으므로 장면 불일치는 FAIL/PASS가
  아니라 `UNKNOWN_SCENE_MISMATCH`여야 한다.
- 예상 PASS / FAIL 조건: 동일 장면 fixture에서 세 입력 단계의 logical geometry, selection count delta,
  selected identity, minimap 절대 camera가 일치하면 PASS. 장면 불일치는 UNKNOWN_SCENE_MISMATCH,
  관측 필드 누락/UNKNOWN은 INCONCLUSIVE, 발산은 FAIL이며 어느 경우도 PASS로 세탁하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/compare_g1_stage_b.py`, `tests/test_compare_g1_stage_b.py`, `Makefile`.
  제품 `tools/runtime_env.py`, tests 기존 파일, EXE/DLL/assets/baseline/golden은 변경하지 않았다.
  모두 uncommitted (`LOOP_ALLOW_COMMITS=0`). 파일 SHA256: comparator
  `7bb7d89c24326e0de5cf2d35eee308169b7dc05bad7d82d935c28623ec837c26`, test
  `dcd8eacdee2e8ede8c8c8a676ac1ce06b0df820ff832aa7c187f53b7db3ac5ab`, Makefile
  `789f0c8ff7f24abe402ff504023cf80837028378bf1cebe72c130e4112419c92`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0회. 실제 보존
  baseline run `local/runtime/20260912_022912_3830565_0`의 원본/copy EXE SHA는
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 핀과 일치한다. 비교 대상
  후보는 과거 presentation trace run이며 이번 바퀴에 새 후보를 만들지 않았다. 실제 pair 적용은
  offline read-only이며 후보 scene/input evidence 부재로 INCONCLUSIVE. fixture는 synthetic owner0/1
  2-unit scene, translation offset, alternate type, missing/UNKNOWN, delta divergence다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `pytest -q tests/test_compare_g1_stage_b.py` → **5 passed**;
  `make check` → **227 passed**, Ruff PASS, compileall PASS, mypy **10 files Success**,
  `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash checks/safety.sh check` → **SAFETY_PASS**.
  `tools/compare_g1_stage_b.py <lap204 baseline evidence> <old candidate evidence>` 적용 결과
  `status=INCONCLUSIVE`, 각 세부 단계 INCONCLUSIVE, `production=NOT_COMPARED`. PNG 0장.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 코드/fixture Fast 검증 PASS. 실제 보존 pair parity는
  후보 `scene`/`inputs`가 없어 INCONCLUSIVE이며, 제품 G1 PASS로 승격하지 않는다. production은 fail-closed
  계약에 따라 비교 범위 밖 NOT_COMPARED다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 새 comparator는 오프라인 도구이며 기존 evidence를
  수정하지 않는다. scene equality의 상대 오프셋 정규화와 after selected identity 비교는 다음 middle이
  독립 검수해야 한다. R6-B `count>=2` 재정의는 여전히 승격 경계이고 후보 Stage B run은 금지다.
  제품 G1 합격/출시 및 G2~G4 승인은 없다. 사용자 실행 승인 범위 안에서 이번 바퀴의 작업은 comparator
  구현까지만 수행했다.
- 다음 한 가지: 새 middle tier가 R5-B 도구·fixture·실제 보존 pair의 INCONCLUSIVE 판정을 독립 검수하고,
  그 뒤에도 R6-B 재결 전까지 Stage B 후보 run을 실행하지 않는다.
