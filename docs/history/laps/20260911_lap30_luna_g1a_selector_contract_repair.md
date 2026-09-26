# 2026-09-11 | lap 30 | G1-A selector 관측 계약 수리

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션, 사용자 지정 hands-on 실무 작업자
  (Luna/high 계약). 런타임은 실제 model ID/effort를 노출하지 않아 실제값은 미확인.
- 가설 / 사용자 관찰: lap29가 확인한 원본 control callback 시간 경계에 맞추면 PS7 selector는
  두 control object의 `[+0xA4]` DWORD one-hot 상태로 검사하고, `0x004ED848` WORD는
  연결 `확인` 뒤 committed mode로만 검사해야 한다.
- 예상 PASS / FAIL 조건: 두 selector 주소를 DWORD로 정확히 읽고 `(1,0)/(0,1)`만 허용,
  비 one-hot은 fail-closed, 양쪽 초기 분기를 회귀하며, confirm endpoint가 committed WORD=1을
  요구하면 PASS. 이전 global `1->0->1` selector gate와 early WORD read는 제거한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA256 `e06c73a9d9602d1f036ab3f8ebcf306a3ee01e21945fd27b54daab502f6e5e49`,
  `tests/test_runtime_env.py` SHA256 `5ea8ea87672577bde15dc67cf647a84e382fb1fe2c8f54e9645738546ea1f9fd`.
  selector DWORD reader/one-hot validator와 confirm-time WORD 검사를 구현하고 회귀를 갱신했다.
  Git unborn/uncommitted, commit/push 없음. 이력과 STATUS는 별도 기록.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 일치 확인.
  구현 후보 바이너리/게임/EXE/DLL/assets 없음. Wine/Xvfb/실제 게임 실행 없음; fixture는
  Python mock selector states `(1,0)/(0,1)` 및 비 one-hot 4종뿐. 활성 플레이어·지도·군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_runtime_env.py`
  (20 passed), `make check` (94 passed; Ruff/compileall/mypy/context PASS),
  `bash checks/safety.sh check` (`SAFETY_PASS`), `sha256sum ../Syw2plus_re/Syw2plus/syw2plus_original.exe`.
  새 실행 로그/PNG 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 주소/폭, one-hot reader와 거부, 양쪽 초기 분기,
  confirm-time committed WORD 회귀 PASS. Fast/safety PASS. 패치 생성·old/new bytes·원복·실제
  게임 실행·2배 출력·PS5→PS3·필수 입력5종은 후보/실행 없어 SKIP. G1~G4 제품 판정은 미완료.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 하네스가 더 이상 PS7 click 직후
  `0x004ED848` 변화를 요구하지 않는다. 실제 원본 입력 전달과 selector label 의미, 출력/UI,
  전투 및 G2~G4는 미검증. 다음 새 Sol/high 세션의 독립 검수 전 게임 실행 금지. 사용자 승인 없음.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high middle이 이 두 파일의 selector contract와 Fast/safety를
  독립 검수하고, 그 뒤에만 새 격리 원본 G1-A 실행 여부를 판정한다.
