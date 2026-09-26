# 2026-09-11 | lap 100 | 목표 G1-A

- 실제 provider/model/effort / 지정 역할: Codex / 실제 model ID는 현재 표면에 노출되지 않음 / high / Luna work-tier hands-on 정적 조사·계약 수정.
- 가설 / 사용자 관찰: `0x0041E635` updater와 `0x0041EBF6` state load 사이의 상위 CFG와 두 전역의 writer 범위를 고정하면 code `0x04` 입력의 기계적 provenance와 production 의미의 단절을 분리할 수 있다.
- 예상 PASS / FAIL 조건: 두 고정 원본의 SHA/cmp/PE, 지정 branch target, `0x009E1DCC` writer 10개와 `0x00892FFE` writer 18개의 old bytes가 일치하면 mechanical PASS; production sender/action direct edge가 없거나 의미가 불명확하면 UNKNOWN/BLOCKED 유지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/check_binary_contract.py`, `tests/test_binary_contract.py`, `analysis/memory_maps/player_offsets.md`, `docs/STATUS.md`, `loop/ESCALATE_SOL`, 본 history; 원본/참고 EXE·후보·게임 데이터 미변경; `LOOP_ALLOW_COMMITS=0`, uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: `Syw2plus/syw2plus_original.exe`와 `/home/dev_00/sharedfolder/260320_Syw2plus/syw2plus_original.exe` 모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp` PASS; PE32 i386 `.text` VA/raw `0x00401000/0x1000`, size `0xE3AE5`; candidate/player/map/army/fixture N/A/SKIP.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `cmp -s`, `file`, `objdump -D -Mintel`, `xxd`, Capstone x86 read-only xref script, `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_binary_contract.py`; 신규 log/PNG/game run 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): `0x0041E635→0x00437E90` unique direct call, upstream branch 10개, mask writer 10개, state writer 18개 old bytes PASS; targeted **12 passed**, `make check` **139 passed**, Ruff/compileall/mypy/context PASS, safety `SAFETY_PASS`, doctor top-level `ok=true`/original verified; 정적 chain PASS, production 의미/direct edge UNKNOWN/BLOCKED. runtime manifest/game/fixture/candidate는 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 계약은 SHA-gated이고 원본을 쓰지 않는다. `0x0041CEE0`가 mask를 읽어 `0x00892FFE`에 state code를 쓰고 `0x0041EBF6`가 읽는 chain은 기계적으로 고정됐지만 production input/action, enqueue, worker/unit/primary sender는 미증명. 다음 새 Sol/Opus5 middle 독립 검수 및 사용자 승인은 없음.
- 다음 한 가지: Sol/Opus5/high middle이 두 고정 원본에서 lap100 branch/writer contract와 production-edge blocker를 독립 재검수한다. 그 전에는 G1 구현·실행·fixture·좌표 변경 금지.
