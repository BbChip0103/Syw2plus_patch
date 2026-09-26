# 2026-09-12 | lap 315 | G1 — R2 D1/E1/E2 정적 probe 수리

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션, hands-on work, high; 실무 조사·코딩·테스트·수정.
- 가설 / 사용자 관찰: lap314가 확인한 세 가지 fail-open을 새 probe에서 닫으면 기존 원본 수치는 유지하면서
  간접 분기와 비연속 실패 arm의 회귀를 검출하고, 빈 pre-gate 비교를 과장 없이 보고할 수 있다.
- 예상 PASS / FAIL 조건: 원본 SHA 불변; window/entry/failure/success가 753/753/7/724; unresolved branches 0;
  writer 4개·failure writer 0개; `pre_gate_is_vacuous: true`와 `failure_writers == set()`; gate `750a`→`0x431afe`;
  실패 arm 10바이트 연속 `5f5e5d33c05b83c434c3`; indirect jump와 주소 gap synthetic fixture는 fail-closed.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `docs/history/laps/probes/20260912_lap315_work_v6_mode_writer_order_probe.py` SHA `839372aa3683dd99849ef00e27d034e6c6c1784c04180bda30e1f419e19784c6`.
  - `tests/test_lap315_mode_writer_probe.py` SHA `22aa2219ce3fc6828aa62e15f83bebd0f169dd2748c5fae1eb23dab97a72274a`.
  - `logs/lap315/lap315_v6_mode_writer_order.json` SHA `ac0e1b7e3e2008bbb2850096811f4abfdfefbca933f067fb3d4a93dafc2bfa31`.
  - `docs/STATUS.md` 갱신. 커밋 없음(`LOOP_ALLOW_COMMITS=0`). lap313/314 파일·report는 수정하지 않았다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `Syw2plus/syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`;
  검수 전후 불변. 후보 EXE·활성 플레이어·지도·군대 없음. Linux `.venv`, objdump `.text`; synthetic CFG/gap fixture는
  회귀 테스트 전용이며 실제 게임 fixture가 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python -m pytest -q tests/test_lap315_mode_writer_probe.py` → **6 passed**.
  - `.venv/bin/python docs/history/laps/probes/20260912_lap315_work_v6_mode_writer_order_probe.py > logs/lap315/lap315_v6_mode_writer_order.json` → exit 0, fresh 2회 stdout SHA 동일.
  - `make check` → **319 passed**, Ruff/compileall/mypy/CONTEXT_PASS; `bash checks/safety.sh check` → **SAFETY_PASS**.
  - 게임/Wine/Xvfb/Stage B/runtime/PNG/click 실행 **0**.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **PASS (1단 정적)**. report는 `pre_gate_is_vacuous: true`,
  `pre_gate_reduction: failure_writers == set()`, gate `750a`→`0x431afe`, contiguous failure arm 10바이트,
  writer 수치 753/753/7/724와 unresolved `[]`를 기록했다. lap313/314와 원본 SHA 대조도 불변이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: synthetic indirect `jmp [table]`/`jmp eax`는 edge 없이
  unresolved로 남고 gap arm은 불연속으로 판정된다. 정적 probe일 뿐 계산/간접 writer, cross-function event/thread 순서,
  WM_CLOSE, 실제 scene/input 및 G1 제품 증거는 여전히 UNKNOWN/0. middle 독립 검수와 사용자 마일스톤 승인은 대기.
- 다음 한 가지: 다음 middle(Sol/Opus5/high)이 lap315 새 probe·report·6개 회귀 테스트와 원본/기존 산출물 불변을 독립 검수한다.
