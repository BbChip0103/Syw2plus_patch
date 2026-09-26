# 2026-09-12 | lap 327 | 목표 G1-R1

- 실제 provider/model/effort / 지정 역할: Codex work tier / hands-on 구현 작업자. 이번 세션은 지정 모델 argv를 조용히 대체하거나 상위 컨펌을 수행하지 않았다.
- 가설 / 사용자 관찰: lap326 middle 봉투의 PS35 도달 게이트와 순서 보장이 유효하므로, 기존 제품 입력 경로와 분리한 읽기 전용 R1 실행 경로를 추가하면 네 실패 모드를 재현 가능한 JSON으로 보존할 수 있다.
- 예상 PASS / FAIL 조건: `g1-r1-load-origin`이 고정 1600×1200×24 격리 런타임에서 PS9→pre→클릭 1회→PS35→origin 단일 6-byte read를 기록하고, 미도달/미변화/timeout/짧은 read를 PASS로 바꾸지 않는다. 이번 바퀴는 실행하지 않으므로 제품 PASS를 주장하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/runtime_env.py`(SHA256 `0d5a06063eae584540e310be10f82fe71527d8a6f52f005c0d6df8221f1698d3`), `tests/test_lap326_r1_load_origin.py`(SHA256 `ef2ab3968ad11ddf880372ab4783258762eb86bc32dc7a95f020363db9575c9a`), `docs/STATUS.md`(SHA256 `39a0dea329516433f90040bc6b551d4c8107b44bc74bc507bb254509f7b8b6b4`). 모두 uncommitted; 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 실행 SHA 없음(실행 0). Linux Python 3.13.5/.venv, 게임/Wine/Xvfb 0, 활성 플레이어·지도·군대 미측정. 합성 fixture는 메모리 read shape와 네 실패 레코드뿐이며 게임 메모리 write/resource grant 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_lap326_r1_load_origin.py` (6 passed), `make check` (367 passed, Ruff, compileall, mypy, CONTEXT_PASS). 실제 앱/Wine/클릭/PNG/Stage B는 실행하지 않음; R1 로그·캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 합성 4종은 `UNREACHED`, `REACHED_UNCHANGED`, `TIMEOUT`, `COLLECTION_ERROR` 각각 `status=UNKNOWN`; CLI forwarding·contiguous origin read·PS WORD signed 해석도 통과. 기계 검사 PASS, 제품/실행 증거 UNKNOWN/SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 `runtime_env` 테스트 포함 전체 check 통과. 기존 `{prepare,check,smoke,g1-baseline,g1-presentation-trace}`와 `_g1_flush_input_stage`를 수정하지 않았고 `process_vm_writev`/ptrace/int3/winedbg/gdb를 추가하지 않았다. 새 middle(Opus5/high)의 실행 전 독립 검수와 P1 실제 pre=(0,0,0), 클릭 도달, WM_CLOSE는 미검증. 사용자 승인 범위는 G1-R1 bounded repair/fresh validation뿐이며 제품/출시 승인은 없음.
- 다음 한 가지: 다른 새 middle이 `G1_R1_MIDDLE_ENVELOPE_LAP326.md` §5 구현과 `make check` 결과를 실행 전에 독립 검수한다. 검수 전 runtime/게임/Wine/Xvfb/클릭 예산은 0이다.
