# 2026-09-11 | lap 172 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex work tier, hands-on 구현 작업자, high 계약.
- 가설 / 사용자 관찰: production primary field/action mapping은 승인되지 않았으므로 클릭을
  허용하지 않고도 입력 증거 수집을 `drag_select`/`minimap`까지 진행할 수 있어야 한다. baseline과
  후보가 같은 메뉴 판정·논리 좌표·단계별 evidence schema를 쓰면 Stage B의 기계 대조 준비가 된다.
- 예상 PASS / FAIL 조건: production 콜러블 미호출, production 효과 대기/after 캡처 미진입,
  production `BLOCKED`와 overall PASS 불가를 유지하면서 후속 단계에 도달하면 PASS. 입력 좌표에
  scale을 곱하거나 장면 대조 필드가 승인되지 않은 주소를 사용하면 FAIL/중단.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py`, `tests/test_runtime_env.py`; runtime SHA256
  `7a0374e5259c7d6201fa634540658d223839cc12492894dca4b885b3b12fa1fb`, test SHA256
  `4d18c5d55f6ee9c3bd019b29db72d68fda44ed184d775b2cfb7f52d8ea9dfa51`; uncommitted, 커밋 없음.
  STATUS/이력은 루프 기억 갱신으로 별도 보존했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 변경 없음. Stage A는
  게임/후보 실행 0회, 활성 플레이어·지도·군대 수치 N/A. 단위 fixture는 synthetic memory/state
  callback으로만 사용했고 실제 게임 fixture/resource grant/memory write 없음. A-5는 기존 승인
  `0xB3DE34/0xB3DE36` map width/height와 기존 runtime_driver 상세 state를 읽는 코드만 사용했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `sha256sum`으로 lap168 P5 현물 6개를 재대조해 기록과 6/6 MATCH:
  `local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/`의
  `evidence.json=309028386476de06ced251686444e04b7c8e7d9c282f7f52e7ed1dbcf7fc7e59`,
  `provenance.json=1b8df1e86bd8956da2bc3d9410afc0cebea83371646ae4a1a720cdac475e1c1b`,
  `verdict.json=319474f8fbe1f5e6d52443a71c75894b581e8ed83299bba60eeee30701138d55`,
  `trace.jsonl=trace_raw.jsonl=aa3934044c5cfb1758d7330b3dab5b3f5a09c0468b5946a81f05d44ee62ceb1b`,
  `manifest.json=d59ad3242d4aeb0a8223edd24db3d690b5cab04694d46519d2597df17c7ccd66`.
  `make check`; `bash checks/safety.sh check`; `python3 -m ruff check tools/runtime_env.py tests/test_runtime_env.py`;
  `python3 -m mypy tools/runtime_env.py`; `python3 -m pytest -q tests/test_runtime_env.py -k g1_`;
  실제 캡처/게임 로그는 Stage A 금지로 생성하지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  선택 G1 회귀 `68 passed`; 전체 `make check` `196 passed in 33.52s`; Ruff PASS; compileall PASS;
  mypy `9 source files` PASS; `CONTEXT_PASS`; `SAFETY_PASS`; CLI help에 `--g1-input-sequence` 확인
  PASS. A-1~A-5 기계 구현 PASS. Stage B 실제 baseline/candidate 입력 비교 SKIP(다음 middle
  검수 전 금지). G1 제품·마일스톤 승인 없음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: production은 여전히 `BLOCKED`라 required
  inputs와 overall PASS를 통과시키지 않는다. 후보 close/teardown 결함은 수리하지 않았고 P6는
  보류다. 두 fresh run의 random scene 동일성은 아직 없으므로 Tier-2 입력 비교는 A-5 필드 일치
  전 UNKNOWN이다. 다음 middle이 schema·범위·원본 보호·Fast 결과를 독립 검수해야 하며 사용자
  마일스톤 승인은 없다.
- 다음 한 가지: middle tier가 Stage A 결과를 새 세션에서 독립 검수하고 승인/반려 근거를 기록한다.
  승인 전 Stage B 게임 실행, P6, G1 마감, G2 전환은 하지 않는다.
