# 2026-09-12 | lap 336 | 목표 G1-R1 후보

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle(진단·계획·확인).
  lap335 work 구현을 독립 검수만 했고 게임 코드/하네스를 고치지 않았다. 상위 방향·제품 승인도 대신하지 않았다.
- 가설 / 사용자 관찰: lap335 후보 구현이 lap334 봉투 §11의 계약(이름 분리·무배율 클릭·기하/모듈 게이트·
  다섯 실패 분류·원복)을 실제로 만족하면 후보 fresh 1 run이 발효한다. 만족하지 않는 항목은 수리로 돌려보낸다.
- 예상 PASS / FAIL 조건: PASS = 검수 SHA가 lap335 기록과 일치하고, 후보 계약을 새 probe로 독립 재유도하며,
  원본 R1 경로가 불변이고, `make check`/safety가 재현된다. FAIL = 계약 위반, 원본 경로 오염,
  실패의 PASS 승격, 봉투 필수 항목 누락, 또는 middle 권한 밖 충돌.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/work/active/G1_CANDIDATE_R1_MIDDLE_IMPLEMENTATION_REVIEW_LAP336.md`,
  신규 probe `docs/history/laps/probes/20260912_lap336_middle_lap335_candidate_implementation_probe.py`
  SHA `2e1481b845e787fe1bd228c247d4dfa992d2dd2bf00b29b1db2f3e1505f8e25d`,
  이 기록, `docs/STATUS.md`, 신규 `loop/ESCALATE_SOL`. 게임 코드/하네스/테스트 변경 0.
  커밋 0(`LOOP_ALLOW_COMMITS=0`), uncommitted 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE 계약
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 유지. 검수한 현물
  `tools/runtime_env.py=922a267c…f8a2575`, `tests/test_lap326_r1_load_origin.py=c04a6265…d769823`
  (둘 다 lap335 기록과 일치). 후보 실행 0회이므로 환경·활성 플레이어·지도·군대는 미측정.
  fixture는 순수 합성(임시 디렉터리 ddraw 파일, 합성 window/모듈/타임아웃 객체)이며 Wine·메모리·PNG 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap336_middle_lap335_candidate_implementation_probe.py`
  → rc0, `failures=[]`, stdout SHA256 `9295dfdfd9bee0b5dc298946f2348c2a7327961ce81cf4f78d43a6c7d1593a0f`
  (연속 2회 byte-identical), Ruff PASS.
  `make check` → **376 passed**(57.16s)·Ruff/compileall/mypy/`CONTEXT_PASS`·rc0.
  `bash checks/safety.sh check` → `SAFETY_PASS`.
  `.venv/bin/python -m pytest -q tests/test_lap326_r1_load_origin.py` → **15 passed**.
  재실행한 과거 probe: lap332 artifact probe **rc1**, lap334 envelope probe **rc1**(사유는 아래).
  게임 실행·입력·메모리 접근·PNG·후보 artifact 0.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **ACCEPT-WITH-REQUIRED-REPAIR.**
  PASS: 이름 분리(원본 artifact 전 저장소 1건·후보 0건), 무배율 클릭 `[396,705]`·`scale_applied=[1,1]`,
  기하 게이트 2종 거부, 모듈 게이트 **6종 fail-closed**, 다섯 실패 분류 전부 `status=UNKNOWN`,
  cleanup 4종 위반 `ok=False`, 원본 경로 정적 불변(기본 `allowed_sizes=((800,600),)`·`ddraw=b` 유지),
  클릭 사이트 1곳·게이트 전부 선행.
  FAIL(수리 요구): **R-a** 봉투 §11.3 필수 "artifact 이름 분리 단언" 테스트 부재,
  **R-b** PS9 stage 예산이 dxwrapper 설치 뒤에 시작해 §8 "준비/PS9 40초" 상한을 설치 구간에 적용하지 못함.
  **N13(수치 영향 0):** lap335 기록의 "16 passed"는 같은 SHA 파일에서 실제 **15 passed**다.
  SKIP/UNKNOWN: 후보 실행·입력·쓰기·PNG·제품 G1 증거는 전부 0이며 이번 바퀴도 만들지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  **회귀 발견:** lap335의 (봉투가 허가한) 하네스 편집으로 lap332·lap334 probe가 **둘 다 rc1**이 됐다.
  두 probe가 살아 있는 `tools/runtime_env.py`의 SHA를 lap330 값으로 단언하기 때문이며, 이는 W3(lap300)과
  같은 형태이자 lap334가 STATUS에 대해 스스로 진단한 **N12의 재발**이다. 재pin은 금지이므로 고치지 않았다.
  **회복 불가:** 커밋 0·스냅샷 없음이라 lap330~334가 검수한 하네스 원문(`997ff15b…cc46eed`)은 디스크에
  없다. lap331 artifact의 `provenance.harness_sha256`은 그 값을 가리키므로 그 run의 "검수 SHA == 실행 SHA"
  재확인은 더 이상 기계적으로 재현할 수 없다(lap332 ACCEPT는 당시 판정으로 이력에 남는다).
  다음 검수 기준선은 `922a267c…f8a2575`이며 lap336 검수 문서가 그것을 기록한다.
  사용자 마일스톤 승인 없음. 제품 G1/Stage B/G2~G4 증거 0. 후보 실행 예산은 여전히 0회다.
- 다음 한 가지: work tier(Luna/Sonnet5 high)가 R-a·R-b만 수리하고(실행 0회) 다음 새 middle이 그 수리를
  재검수한 뒤에야 후보 fresh 1 run이 발효한다. probe 재pin/스냅샷 정책은 `loop/ESCALATE_SOL`로 승격했다.
