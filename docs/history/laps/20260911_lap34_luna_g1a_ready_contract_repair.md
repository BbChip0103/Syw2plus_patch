# 2026-09-11 | lap 34 | 목표 G1-A ready 관측 계약 수리

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-luna`/high work 지정. 현재 호출의 실제 model ID/effort는 노출되지 않아 미확인.
- 가설 / 사용자 관찰: lap33이 확인한 원본 solo PS5 경로는 수동 ready control poll을 건너뛰고 활성 local slot의 ready DWORD를 자동 설정한다. 따라서 화면 crop 변화를 요구하지 않고 원본 메모리 상태를 읽으면 고정된 setup gate를 얻을 수 있다.
- 예상 PASS / FAIL 조건: `0x00B63FC4`를 정확히 4byte로 읽어 `0..7`만 허용하고, `0x00632CF0 + local*4`를 정확히 4byte로 읽어 값 `1`만 ready로 인정한다. confirm 뒤 mode=1/PS5/ready=1과 기존 PS5→PS3 start 계약을 유지한다. 잘못된 index/ready 값은 fail-closed한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/runtime_env.py` SHA256 `8de1b9f449d9c28fc3e996c9d393013f5c36c06f8ddf6634f1152678a9964bc3`; `tests/test_runtime_env.py` SHA256 `1bde26444fe62aebb06c0e6f5d0832740c9f543597ebaacdcd21af76cd696621`; `docs/STATUS.md`와 이 lap 기록 추가. Git unborn/uncommitted, `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본/후보 EXE 변경 없음. 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`는 lap32 private copy에서 보존 확인된 값. 새 후보·Wine/Xvfb/game run 없음; 기존 증거를 현재 성공으로 승격하지 않음. fixture는 메모리 reader 단위 fixture이며 실제 플레이어/지도/군대 수치는 미측정.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 -m pytest -q tests/test_runtime_env.py` → **25 passed**; `make check` → **99 passed**, Ruff PASS, compileall PASS, mypy 8 files PASS, `CONTEXT_PASS`; `bash checks/safety.sh check` → `SAFETY_PASS`. 새 PNG/게임 로그/패치 생성·적용·원복은 실행하지 않음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): local index 주소/폭과 slot 주소 산술, `0..7` 경계 및 unknown ready 값 거부 회귀 **PASS**. confirm mode=1/PS5/auto-ready gate와 기존 start gate 회귀 **PASS**. 수동 ready click/crop gate **제거 PASS**. 실제 PS3·전투·필수 입력·2배 출력·G1 제품 판정 **SKIP**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 구현은 원본 EXE/DLL/assets를 수정하지 않았다. 새 Sol/high가 source SHA·주소·reader 결선·fail-closed 의미를 독립 검수해야 하며 사용자 마일스톤 승인 없음. G2~G4와 실제 G1 출력/입력 증거는 미완료.
- 다음 한 가지: 새 Sol/high middle이 lap34 source/test SHA와 `0x00B63FC4`/`0x00632CF0` 결선 및 기존 start gate를 독립 검수하고 판정한다. 그 전까지 새 게임 run은 금지한다.
