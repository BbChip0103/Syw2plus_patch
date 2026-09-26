# 2026-09-11 | lap 31 | G1-A selector contract middle 독립 확인

- 실제 provider/model/effort / 지정 역할: Codex 새 세션, 사용자 지정 middle 진단·계획·확인 역할.
  계약 대상은 `gpt-5.6-sol`/high이나 현재 런타임이 정확한 model ID/effort를 노출하지 않아 실제값은
  미확인. 게임 코드·하네스·EXE/DLL/assets hands-on 수정 및 게임 실행 없음.
- 가설 / 사용자 관찰: lap30 수리가 lap29의 확정 시간 경계대로 PS7의 두 control DWORD를
  one-hot으로 읽고, `0x004ED848` WORD는 연결 `확인` 뒤 committed solo mode로만 검사한다.
- 예상 PASS / FAIL 조건: 고정 원본과 lap30 source SHA가 일치하고, 정확한 주소/폭, 비 one-hot
  fail-closed, 양쪽 초기 분기, confirm-time WORD=1이 production 결선과 회귀에 있으며 targeted/Fast/
  safety가 모두 PASS하면 CONFIRMED. 필수 gate 실패나 근거 충돌이면 새 실행을 금지하고 승격한다.
- 변경 파일 / source fingerprint / 커밋: 구현 변경 없음. 검수 source SHA256은
  `tools/runtime_env.py` `e06c73a9d9602d1f036ab3f8ebcf306a3ee01e21945fd27b54daab502f6e5e49`,
  `tests/test_runtime_env.py` `5ea8ea87672577bde15dc67cf647a84e382fb1fe2c8f54e9645738546ea1f9fd`,
  `tests/test_runtime_guards.py` `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`.
  문서만 활성 카드, `docs/STATUS.md`, 이 기록을 갱신했다. Git unborn/uncommitted, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 일치. 구현 후보 바이너리와
  새 Wine/Xvfb/game run 없음. 테스트 fixture는 mock selector `(1,0)/(0,1)`과 비 one-hot 4종;
  활성 플레이어·지도·군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`으로 source/원본 확인; `objdump -h/-d -Mintel`
  로 constructor `0x004B8C16..0x004B8C70`, state reader/writer `0x00405540/0x00405550`, callback와
  confirm gate/write `0x004B91E0..0x004B9399` 재확인; `rg`로 production reader 호출 위치 확인.
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py` → 24 passed;
  `make check` → 94 passed, Ruff/compileall/mypy/context PASS; `bash checks/safety.sh check` → `SAFETY_PASS`.
  새 로그/PNG 없음.
- 측정값 / 판정: 두 selector object `0x0106A600/0x0106A7C8`의 `+0xA4` DWORD가 정확히
  `0x0106A6A4/0x0106A86C`; reader는 각 4byte를 읽고 `(1,0)/(0,1)` 외 상태를 거부한다.
  양쪽 초기 branch 회귀가 실제 selector flow를 호출하고, committed reader의 유일한 production 호출은
  connection confirm 뒤 PS5 도달 후이며 2byte WORD=1 endpoint 회귀가 있다. **CONFIRMED**.
  게임/패치 생성·old/new bytes·version reject·copy-only·non-overlap·restore는 후보/실행 없어 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap30 source와 Fast/safety에 회귀 없음.
  selector label의 실제 입력 전달, PS5→준비→PS3, 전투·필수 입력5종, 실제2배 출력은 새 runtime에서
  여전히 미검증이다. G1-A/G1~G4 및 사용자 마일스톤 승인 없음. `loop/ESCALATE_SOL` 생성 조건 없음.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 활성 카드 그대로 새 private manifest를 만들고
  원본 G1-A를 정확히 1회 실행한다. 어느 gate든 FAIL/UNKNOWN이면 재시도·패치 없이 artifact를 보존해
  Sol/high middle에 돌려보낸다.
