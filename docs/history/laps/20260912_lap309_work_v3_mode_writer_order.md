# 2026-09-12 | lap 309 | G1 — lap308 R2·R3·R5 bounded repair

- 실제 provider/model/effort / 지정 역할: Codex hands-on work role. 이 세션에서 실제 런타임 모델 ID는 노출되지 않았으며, 프로젝트 라우팅 대상은 `gpt-5.6-luna/high`이다.
- 가설 / 사용자 관찰: lap308 middle이 지적한 V2의 공허한 failure seed, 호출 규약을 무시한 stack model, map caller 단언 누락을 새 probe에서 수리하면 정적 결론을 회귀 가능한 근거로 고정할 수 있다.
- 예상 PASS / FAIL 조건: 원본 SHA 일치, `0x431AF4` failure path에 runtime writer 0개, corrected join/ret depth가 각각 `{0x100}`/`{0}`, entry offsets가 `4`/`8`, map caller가 정확히 `0x48F538`이고 모든 불변식이 exit 0이어야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 새 `docs/history/laps/probes/20260912_lap309_work_v3_mode_writer_order_probe.py`, 새 `tests/test_lap309_mode_writer_probe.py`, stdout report `logs/lap309/lap309_v3_mode_writer_order.json`; 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `Syw2plus/syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 전후 불변. 후보 EXE·활성 플레이어·지도·군대·fixture 없음. Linux `.venv` + `/usr/bin/objdump` 정적 분석.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_lap309_mode_writer_probe.py` (2 passed); probe를 `logs/lap309/lap309_v3_mode_writer_order.json`으로 stdout redirect 후 fresh stdout과 `cmp` (byte-identical); `make check` (exit 0, 294 passed), `bash checks/safety.sh check` (`SAFETY_PASS`). PNG·게임·Wine·Xvfb·Stage B·runtime·click 실행 0.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): R2 PASS (`0x431AF4..0x431AFD`, runtime writer 0, success writer 2); R3 PASS (old ret `{0x10,0x14}` → corrected join `{0x100}`, ret `{0}`, offsets `0x46526D=4`, `0x465287=8`); R5 PASS (map caller `[0x48F538]`). anchors 15/15, map returns 2, unresolved branches 0, report verdict PASS.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본 정적 probe 회귀는 통과했지만 제품 G1 PASS가 아니다. 간접 writer, 실제 click-time mode, cross-function event/thread order, WM_CLOSE와 scene/input evidence는 UNKNOWN/미검증. 사용자 제품 마일스톤 승인 없음; 다음 새 middle 독립 검수 필요.
- 다음 한 가지: 새 middle(Sol/Opus5/high)이 lap309 V3 probe와 stdout report를 독립 재유도하고 R2·R3·R5 수리 및 SHA/provenance를 컨펌한다. 그 전까지 게임/Wine/Xvfb/Stage B/runtime/PNG/click 실행은 금지.
