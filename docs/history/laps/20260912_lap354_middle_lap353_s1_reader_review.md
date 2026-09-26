# 2026-09-12 | lap 354 | G1 / lap353 S1 reader middle 검수

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션 / 정확한 모델 ID 미주장 / high / middle(진단·계획·확인). 게임 코드 hands-on 수정 0.
- 가설 / 사용자 관찰: lap353 reader/CLI가 lap352 봉투대로 post-PS3 원시 필드를 직접 읽고 무근거 payload를 PASS로 승격하지 않는지 독립 판정한다.
- 예상 PASS / FAIL 조건: 생산 CLI가 PS/group/slot/8×6 collector에 결선되고 open-failure·결측·부분 read·무근거 외부 JSON이 PASS가 아니면 ACCEPT; 하나라도 caller assertion만 신뢰하면 REJECT/승격.
- 변경 파일 / source fingerprint / 커밋: 신규 독립 probe, active review, 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` append. 제품 코드/tests/EXE/DLL/save/pin/baseline/golden 변경 0; 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 pin `b56986e0…a8ac`; 후보 없음; Linux/Python 정적·합성 검수; 활성 플레이어·지도·군대 N/A. save000 3,093,902 B / `1c703551…719da`.
- 이전 바퀴 검수: lap353 네 SHA가 기록과 일치. 실제 파일 8×6 raw가 nation/index/is_cpu/self-bit/opponent-bit/team 배치와 일치. targeted `11 passed`, Ruff/compileall/mypy PASS.
- 실행 명령: `sha256sum` 네 파일; `rg` 생산 caller; fixture `sha256sum`/`xxd`; `.venv/bin/python -m pytest -q tests/test_s1_load_evidence.py`; Ruff/compileall/mypy; 독립 lap354 probe 1회. 게임/Wine/Xvfb/클릭/PNG 0.
- 측정값 / 판정: 독립 probe SHA `b08d0c7b97586a62904ef17a36150facf3897c25d6c128e921ef782b7c3d07a4`, rc1/F1~F4. `read_post_player_structs` 생산 호출 0, group/PS address read 결선 0, 복사 raw + caller `ps=3/open_succeeded=true`가 `PASS/LOAD_RESTORED_PLAYER_STRUCTS`. **lap353 work REJECT — REQUIRED WORK REPAIR.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 전체 Fast/safety는 필수 독립 검증 실패 중단 조건으로 SKIP. 실제 load/S1/F2-R2/Stage B/WM_CLOSE/G1~G4 미검증, 사용자 승인 0.
- 다음 한 가지: Luna/high work가 실제 read 주입 collector/CLI 결선과 pre→post 변화·pinned fixture 일치를 요구하도록 fail-closed 수리하고 lap354 F1~F4 회귀를 추가한다. 실행 예산 0.
