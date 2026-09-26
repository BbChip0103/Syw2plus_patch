# 2026-09-12 | lap 217 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-luna`/high / work hands-on 구현.
- 가설 / 사용자 관찰: `FAIL_NO_EFFECT`는 실제 입력 효과를 반증할 수 있는 분쟁 라벨이므로
  comparator가 카드 `FAIL`로 상속하면 안 된다. timeout의 `after.last`를 관측값으로 읽되
  disputed stage와 overall을 PASS로 승격하지 않아야 한다.
- 예상 PASS / FAIL 조건: selection timeout의 `after.last`는 selection으로, minimap timeout의
  `after.last.camera`는 camera로 읽는다. 관측 누락은 `INCONCLUSIVE`; 관측이 서로 같아도
  `UNKNOWN_DISPUTED_ORACLE`/overall `INCONCLUSIVE`; 정상 PASS fixture와 F1/F4/F5 회귀는 유지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/compare_g1_stage_b.py` SHA256
  `fa83f781269d70db2bcca10f12c866e20be45ab7c48d2c38527d14686e453d1f`,
  `tests/test_compare_g1_stage_b.py` SHA256
  `d66f901a48d7e867723119199962e44e3808f84dc538b766882b1e4f83b4ab87`;
  `Makefile`/`tools/runtime_env.py`/`tests/test_runtime_env.py` 변경 없음.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`), 로컬 uncommitted 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 바이너리·원본·후보
  실행 없음; EXE/DLL/assets/baseline/golden/evidence/PNG 0 변경·0 생성. 저장소 synthetic
  fixture 3종(양쪽 동일 disputed selection, after.last 누락, minimap camera last)을 사용.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q
  tests/test_compare_g1_stage_b.py` → 12 passed; `make check` → 236 passed, Ruff,
  compileall, mypy 10 files, CONTEXT_PASS; `bash checks/safety.sh check` → `SAFETY_PASS`.
  보존 pair comparator → `INCONCLUSIVE`, production `NOT_COMPARED`, 후보 historical
  untagged tag 오류 2건 유지, 실제 CLI expected exit 2.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): F3 구현 기계 검증 PASS, 다음 middle 독립 검수
  대기. 제품 G1/G2/G3/G4 및 마일스톤 승인 아님. 게임 실행 SKIP(금지된 fresh pair를 열지 않음).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `UNKNOWN_DISPUTED_ORACLE`가 overall
  PASS를 만들지 않는 회귀를 고정했다. S1 장면 통제, F2 identity, R6-B, G1-F6-R2,
  WM_CLOSE teardown은 미해결이다. 다음 middle이 F3를 독립 probe로 검수해야 하며,
  사용자 Stage B 실행 승인은 아직 제품 승인이 아니다.
- 다음 한 가지: 다음 work tier는 게임 실행 없이 F2 identity를 run별 scene 해소
  `(owner, type, 상대 world offset)`로 재정의하고, 그 결과를 다음 middle이 독립 검수한다.
