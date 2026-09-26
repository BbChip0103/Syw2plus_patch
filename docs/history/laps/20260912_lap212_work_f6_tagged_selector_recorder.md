# 2026-09-12 | lap 212 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex work tier; 저장소 라우팅은 Codex `gpt-5.6-luna`/high.
  이번 바퀴는 hands-on 구현이며 최종 독립 컨펌은 다음 middle tier에 남겼다.
- 가설 / 사용자 관찰: 후보 selector flow의 untagged `OBSERVED` producer를 원본과 같은 tagged
  recorder로 바꾸면 F5/F4가 정상 후보 evidence를 구조적으로 막는 비대칭이 제거된다. 보존
  evidence는 변경하지 않는다.
- 예상 PASS / FAIL 조건: PASS = 후보 selector 기록이 고유 문자열 `tag`와 공용 input schema를
  갖고 단계 flush를 유지하며, helper/좌표 회귀와 Fast/safety가 통과한다. FAIL = untagged
  selector record가 계속 생성되거나 comparator/좌표/예산/보존 evidence 범위가 바뀐다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` sha256 `398c2b8ae4980a5c2ddd44bffba2e5330701341a575b5ad4cc519e8ad790322f`,
  `tests/test_runtime_env.py` sha256 `97d8ee154391a533677fe37dc04ee868bef39b2f6244ee3508fdac9d25818def`,
  `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, 이 기록.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`); EXE/DLL/assets/baseline/golden/evidence는 변경하지 않았다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0회, PNG 0장,
  원본·후보 바이너리 SHA 해당 없음. helper fixture는 in-memory selector record
  (`tag=solo_mode_setup`, content `[300,220]`, crop `(37,41,1600,1200)`, scale `[2,2]`)이며
  실제 플레이어·지도·군대는 해당 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'g1_selector_input_recorder or g1_input_verdict or g1_selection_sequence or g1_selector_flow'` → 9 passed.
  `make check` → **232 passed in 38.16s**, Ruff PASS, compileall PASS, mypy 10 files PASS,
  `CONTEXT_PASS`; `bash checks/safety.sh check` → `SAFETY_PASS`.
  수정 후 helper 직접 검증 → tag 1개, flush 1회, content/x11/scale `[300,220]`/`[337,261]`/`[2,2]`.
  과거 F6 probe는 보존 후보의 `menu,null,null`을 재현해 `CONFIRMED`(historical evidence)했고,
  보존 pair comparator는 `INCONCLUSIVE`, exit 2로 유지됐다. 첫 동적 import smoke는 검증
  스크립트의 모듈 등록 오류로 폐기하고 정상 `from tools import runtime_env` 경로로 재검증했다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): F6 bounded repair의 기계 구현·회귀·Fast·안전
  검증은 PASS. 과거 후보 evidence 승격은 SKIP/금지이며 제품 G1은 미완료. F2/F3/R6-B 재결,
  fresh pair, WM_CLOSE teardown은 미검증이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: candidate local recorder가 공용
  `_g1_record_selector_input`을 호출하고 원본 local recorder도 같은 helper를 사용한다.
  사용자가 승인한 bounded repair 범위 안이며 제품/마일스톤 승인은 아니다. 다음 middle이 새
  게임 실행 없이 source/test와 selector evidence schema를 독립 검수해야 한다.
- 다음 한 가지: middle tier가 F6 수리를 독립 검수한다. 그 전에는 후보 Stage B run, 원본 재실행,
  R6-A/R6-C를 하지 않는다.
