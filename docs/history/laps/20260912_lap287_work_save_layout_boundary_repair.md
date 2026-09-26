# 2026-09-12 | lap 287 | G1 S1 저장 레이아웃 boundary repair

- 실제 provider/model/effort / 지정 역할: Codex work tier, hands-on 구현·테스트·수정 / configured `gpt-5.6-luna`, high
- 목표: lap286 middle의 ACCEPT-WITH-CORRECTION 중 정정1을 최소 수정으로 반영하고 `0x4DA4A9` 오인 회귀를 닫는다.
- 가설 / 사용자 관찰: save entry의 exclusive 끝은 `0x440F5B`(마지막 `ret` `0x440F5A`)여야 하며, 이 범위에서는 인접 load 루틴의 `0x4DA4A9` 호출이 fwrite로 열거되지 않는다.
- 예상 PASS / FAIL 조건: PASS=probe가 exact boundary와 `fread_calls_in_save=[]`를 단언하고, `failures=[]`, 기존 모델·fixture 대조가 유지된다. FAIL=경계·호출 분류·수치 불일치.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `docs/history/laps/probes/20260912_lap286_middle_save_layout_review_probe.py` SHA `604e7f8ca8201c54685cd6b57af7286e3da6eafe1169b895be6dd6605080c9fd`; `docs/STATUS.md`; 이 기록. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `Syw2plus/syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 바이너리 없음. offline objdump + 보존 fixture 4개(save000/006/011/012), 게임/Wine/Xvfb 0, 활성 플레이어·군대 해당 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python docs/history/laps/probes/20260912_lap286_middle_save_layout_review_probe.py`; `logs/lap287/work_save_layout_boundary_repair_probe.json` SHA `f0568622b6f41907445f868bb2dacb7b90723f0fbc05e9f51e9bec1225008bc5`; PNG 0.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **PASS (offline repair 범위)** — `SAVE_END=0x00440F5B`, 마지막 명령 `0x00440F5A`, direct fwrite 22, layer 28, helper 3, roster 1, `fread_calls_in_save=[]`, constant `1,400,702`, area coefficient `30.5`, roster 375/558/147/149, `failures=[]`, exit 0. `make check` 292 passed(45.93s), Ruff/compileall/mypy, CONTEXT_PASS, `SAFETY_PASS`. 정정2는 roster를 재구성해 “정확히 맞춘” 것이 아니라 네 remainder의 `0x758` 정수배 검사로만 기록.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본·fixture SHA 불변. S1/F2-R2 결정성, Stage B, runtime 예산, WM_CLOSE, G2~G4 및 G3 저장 초과는 미해결. 새 middle 독립 검수 대기. 사용자 제품/출시 승인 없음.
- 다음 한 가지: 새 middle(Sol/Opus5)이 boundary repair probe/source/log와 SHA·수치를 독립 재실행해 ACCEPT/REJECT 판정.
