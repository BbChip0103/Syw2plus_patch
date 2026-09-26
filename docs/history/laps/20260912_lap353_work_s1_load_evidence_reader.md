# 2026-09-12 | lap 353 | G1 / S1 load-evidence reader work

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션 / 정확한 모델 ID 미주장 / high / work.
- 목표 / 가설: lap352 middle이 ACCEPT한 PlayerStruct 앞 6바이트 배치를 현행 주소 문서에 반영하고,
  기존 R1과 분리된 읽기 전용 S1 fixture/post-PS3 evidence reader가 open-failure·결측·불일치를
  제품 PASS로 승격하지 않는지 합성으로 검증한다.
- 예상 PASS / FAIL 조건: `+0x00..+0x05` 라벨이 nation/player_num/is_cpu/self_bit_mask/
  opponent_mask/team_num으로 정정되고, 8개 raw 6-byte record 일치만 PASS; SHA/slot/group/reader
  오류는 UNKNOWN 또는 FAIL로 보존한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `analysis/memory_maps/player_offsets.md`, `tools/runtime_env.py`,
  `tools/s1_load_evidence.py`, `tests/test_s1_load_evidence.py`, `docs/STATUS.md`;
  커밋 없음(`LOOP_ALLOW_COMMITS` 기본0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`;
  후보 없음; Python 합성 fixture만 사용, 실제 활성 인원·지도·군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python -m pytest -q tests/test_s1_load_evidence.py`;
  `.venv/bin/python -m ruff check tools/s1_load_evidence.py tests/test_s1_load_evidence.py`;
  `.venv/bin/python -m compileall -q tools/s1_load_evidence.py tests/test_s1_load_evidence.py`;
  `.venv/bin/python -m mypy tools/s1_load_evidence.py tests/test_s1_load_evidence.py --follow-imports=skip`;
  `make check`; `checks/safety.sh check`; 캡처/PNG 0.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): targeted `11 passed`; fresh `make check`
  `389 passed in 63.68s`, Ruff/compileall/mypy/`CONTEXT_PASS` PASS; safety `SAFETY_PASS` PASS.
  정상 8-slot + matching post-PS3는 PASS, open-failure는 UNKNOWN/`OPEN_FAILURE_PS3`, 잘못된
  slot은 UNKNOWN/`INVALID_SLOT`, SHA 불일치는 UNKNOWN/`FIXTURE_IDENTITY_MISMATCH`, reader
  결측/부분 read는 UNKNOWN으로 회귀 확인.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 lap284/lap286 probe/report와 R1 함수는
  수정하지 않았다. 실제 load 완료·파일 선택·두 run 결정성·WM_CLOSE·Stage B·제품 G1과 G2~G4는
  미검증. 다음 새 Sol/Opus5 middle이 변경 SHA·허용 diff·targeted/Fast/safety와 실패 분류를 독립 검수한다.
  사용자 마일스톤 승인 0.
- 검수 시점 파일 SHA256: `player_offsets.md`=`d1170abac5ba46d01d031a95a0017c22b6ca8605b9d1ede6931e6bb79e5b9dfc`,
  `tools/runtime_env.py`=`6eb291ed22efbc822fcbac0a2f83a138c7972db685202ad7112b7fc415971b16`,
  `tools/s1_load_evidence.py`=`a9704cd0f5d48f1328352f3c062045d87d0eb90ea362f2bb290191a87874f53c`,
  `tests/test_s1_load_evidence.py`=`4a5cf5e8c2df519aafd0cc997dee1de100ed85ae7bfb592d5a557214d0f62d94`.
- 다음 한 가지: 새 middle이 이 work 결과를 독립 검수하고, 승인 전 게임/Wine/Xvfb/클릭/PNG 실행은 0회 유지한다.
