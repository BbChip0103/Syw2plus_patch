# 2026-09-24 | lap 555 | G2 W43R 하네스 수리 후 fresh 실행 게이트

- 실제 provider/model/effort / 지정 역할: Codex native session / hands-on work / high
- 가설 / 사용자 관찰: lap552의 W43 실패는 하네스 계약 누락이므로 H29/H30/A3/lifecycle/A5/R7~R9을 고치면 fresh exact-once 실행이 가능해야 한다.
- 예상 PASS / FAIL 조건: 합성 회귀·W43 계약 pin·SAFETY_PASS 후 새 격리 게임 1회가 시작되어야 한다. 필수 bridge build 실패 시 `BLOCKED(gate)`로 승격하고 재시도하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 공유 temp `g2_capacity/20260924_lap552_w43_s1_2stage_24k/w43_run.py`만 수정, SHA `43be0aa8f96f20429d6e6cd77b3aeac7b71bdd0e7f09550959e02cd3ed8fd14f`; repo 제품 source 변경 0; 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 후보 expected `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`; 게임 미기동; 8 owner·지도/군대 미도달; gate-legal fixture 예정.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 temp/.../w43_run.py`, 2026-09-24 16:26:05 KST. `w43_orchestrator.log` SHA `68af5ebf8bd51e1df35eafed41f8a558f0279a3d96ea50b9a862e1c7245cccda`; `run_summary.json` SHA `40653b5635e0dcd6febb5259c8aa26f68d5b0a6d87eee483c82bc91dc485356f`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 합성 `SYNTHETIC_PASS`; 계약 22 passed; `SAFETY_PASS`; pin 4건 PASS. bridge build가 기존 `.../bridge_build`에 `exist_ok=False`로 `FileExistsError` exit1. 게임 0회; **BLOCKED(gate)**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 lap552 raw는 보존. 새 하네스는 아직 middle 독립검수 전. H29 layout 실제 실행, H30 양방향, A3′/A3r, coherent A5, 24k/144k/멀티 및 사용자 승인 미검증.
- 다음 한 가지: 승격 작업자가 기존 raw와 이번 build 충돌을 구분한 뒤, 비중첩 새 temp 실행 디렉터리에서 동일 수리 스크립트를 대조하고 fresh foreground 게임 1회를 판정한다. 기존 bridge_build 삭제/덮어쓰기로 실패를 숨기지 않는다.
