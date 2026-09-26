# 2026-09-12 | lap 335 | 목표 G1-R1 후보

- 실제 provider/model/effort / 지정 역할: Codex work tier / hands-on 구현 작업자 / high.
  후보 R1 봉투(lap334) §11만 구현했고, 중간 컨펌·상위 방향·제품 승인을 대신하지 않았다.
- 가설 / 사용자 관찰: 후보는 원본 EXE를 바꾸지 않고 고정 dxwrapper 2x profile만 적용하므로, 원본
  `g1-r1-load-origin`을 건드리지 않는 별도 실행 경로로 1600×1200 physical content와 무배율 입력을
  관측할 수 있다. 실패는 성공으로 승격하지 않고 봉투의 분류와 artifact에 보존해야 한다.
- 예상 PASS / FAIL 조건: PASS = 후보 서브커맨드가 private `ddraw.dll`/금지된 `syw2x.dll` 부재와
  root/content 1600×1200 게이트, logical `(296,505)` 무배율 클릭, PS9→PS35 수집, 분리 artifact,
  dxwrapper 원복을 구현하고 오프라인 회귀가 통과한다. FAIL = 원본 경로 변경, artifact/lock 혼용,
  게이트 우회, cleanup 원복 실패 은폐, 필수 정적 검증 실패.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA `922a267c27f51fe47d7db69962dadbfdbbded9ff04c6350e8cb7a4c44f8a2575`,
  `tests/test_lap326_r1_load_origin.py` SHA `c04a6265229f7e37cb9d4434f0e150c76e1e56d26f0e1c990cb938a06d769823`.
  후보 helper·서브커맨드·테스트만 추가했으며 `patches/resolution/dxwrapper_config.py` pin은 변경하지 않았다.
  커밋 0(`LOOP_ALLOW_COMMITS=0`), uncommitted 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE SHA는
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 계약을 유지한다. 후보 실행 0회라
  후보 runtime SHA·환경·활성 플레이어·지도·군대는 미측정. fixture는 geometry/module/failure/cleanup
  순수 합성 테스트이며 Wine, 메모리 쓰기, resource grant, PNG 모두 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_lap326_r1_load_origin.py`
  → 16 passed. `make check` → pytest **376 passed**(56.05s), Ruff PASS, compileall PASS, mypy PASS,
  `CONTEXT_PASS`. `bash checks/safety.sh check` → `SAFETY_PASS`. 후보 실행 명령·로그·artifact·입력·PNG 0.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **기계 구현 PASS; 실행/제품 증거 SKIP/UNKNOWN.**
  후보 artifact 이름 `r1_load_origin_candidate.json`, 후보 lock `.r1-load-origin-candidate.lock`, 후보 log를
  원본 R1과 분리했다. `BLOCKED_PRECONDITION`, `NOT_REACHED`, `NO_CHANGE`, `TIMEOUT`,
  `COLLECTION_ERROR`와 cleanup `ok=false` 원복 실패를 오프라인 단언했다. 현재 후보 artifact 0건.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본 R1 함수·artifact·lock·timeout 동작을 직접
  변경하지 않았다. 다음 새 middle이 후보 구현과 SHA/정적 계약을 독립 검수하기 전까지 1 run은 발효하지
  않는다. 아직 fresh 후보 실행, 결정성 n>1, 동일상태 원본/후보 pair, WM_CLOSE, S1/F2-R2, G1 제품 승인은 없다.
- 다음 한 가지: 새 middle(Opus5/high)이 lap334 §11 구현을 독립 검수하고 ACCEPT/수리/반려를 기록한다.
  검수 전 실행 예산은 계속 0회이며, 실패·충돌이면 현재 변경과 이 기록을 보존하고 `ESCALATE_SOL`로 반환한다.
