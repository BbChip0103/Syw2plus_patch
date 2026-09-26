# 2026-09-25 | lap 630 | 목표 G5

- 날짜/lap/목표: 2026-09-25 / 630 / G5 W2a runtime 경로 검증
- 가설: 검증된 `tools.runtime_env prepare → 격리 prefix → bridge chain`을 쓰면 lap629의 direct-Wine 공통 fault를 분리하고 원본 PS3 도달을 먼저 확인할 수 있다.
- 변경파일: `docs/STATUS.md`, `loop/ESCALATE_SOL`, `docs/history/laps/20260925_lap630_work_runtime_prepare_no_space.md`; 제품 코드·패치·테스트 변경 0.
- 원본/후보 SHA: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; lap629 후보 `ebd46050cb061a4793bcf9dbc86e196bd71ab45050d881bb13c64258a8c83e8c`.
- 실행명령: `.venv/bin/python tools/runtime_env.py prepare --runtime-root local/runtime/g5-lap630-original`.
- 수치/환경: `df -B1` available `13,378,916,352`B; `du -sh local/runtime` `269G`; inode use 12%. `_new_run()`의 새 디렉터리 생성 단계에서 `OSError: [Errno 28] No space left on device`.
- PASS/FAIL/SKIP: prepare **FAIL(environment)**; 원본/후보 게임 실행 **SKIP**; 드래그·명령·save/load **SKIP**; `make check` **SKIP**.
- fixture: 생성 전 중단, 활성 인원/지도/군대 없음. 기존 런타임/공유 temp 산출물은 삭제하지 않음.
- 다음행동: §178 승격 작업자가 보존·공간 정책을 확정한 뒤 원본 prepare/PS3 도달을 새 증거로 검증하고, 성립할 때만 G5 후보 허용·55기 fixture 드래그를 진행한다.
