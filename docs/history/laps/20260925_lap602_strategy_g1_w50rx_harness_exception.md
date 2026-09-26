# 2026-09-25 | lap 602 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`(effort 세션 비노출), 계약 모델 Fable/Astra 대체 / strategy.
- 가설 / 사용자 관찰: lap600 `R4 / BLOCKED(harness_execution_surface)`는 인터프리터 이탈(system `python3`)이다. 제품 관측을 소비하지 않았으므로, 고정된 `.venv` 표면에서 W50R audit-only 1회를 실행하면 R1~R3 중 하나로 G1 acquisition 분기를 결론낼 수 있다.
- 예상 PASS / FAIL 조건: 이 회차는 판정만 한다. 산출물은 W50RX 카드이며, 실행 결과 분류는 W50R 카드 §4 R1~R4를 그대로 쓴다.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/work/active/G1_STRATEGY_W50RX_HARNESS_EXCEPTION_LAP602.md`, 이 기록, `loop/ESCALATE_SOL` §152 추가, `docs/STATUS.md`, `docs/feedback/INBOX.md` 통지 1줄. 제품/하네스 source·binary·raw 변경0. 커밋0(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE `b56986e0…a8ac`, DxWrapper `96c44319…e8fe`(lap600/601 기록 대조, 이번 회차 재해시 안 함). 후보 C `24a2ef66…d531`, test `684f4893…8241`, bridge `75c918b9…8fd0`은 이번 회차 `sha256sum`으로 lap600/601 값과 일치를 확인했다. close helper(lap600 `/tmp`) `92c1635e…9120`은 참고용이며 재사용하지 않는다. 게임 실행0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `grep` `logs/laps/2026-09-25/lap-0600.log`: 13170행 system `python3 tools/runtime_env.py g1-presentation-trace …`(audit env 3개), 13428행 `.venv/bin/python -m tools.runtime_env …`(audit env 없음). 둘 다 §151과 일치한다.
  - lap-0597.log: 성공한 A1/A3 표면은 `PYTHONPATH=. .venv/bin/python tools/runtime_env.py prepare|g1-presentation-trace …`이다.
  - import smoke: system `python3 -c "import patches"` → `ModuleNotFoundError`. `.venv/bin/python`(cwd `/tmp`, `sys.path[0]=tools`) → `patches/resolution/dxwrapper_config.py` import 성공. `PYTHONPATH=. .venv/bin/python -c "from patches.resolution import dxwrapper_config"` → `import ok`. `… tools/runtime_env.py --help` exit0. `g1-presentation-trace --help`에 `--win32-close-helper`·`--dxwrapper-2x`가 있다.
- 측정값 / 판정: §151 (A) 선택. **W50RX bounded harness exception 정확히 1회**를 허용한다. G-a~G-e pre-gate와 실행 명령을 고정했다. R4가 다시 나면 최종으로 닫고 재승격하지 않는다. R3/R4이면 G1 대안 경로(native 1600 표면 blit 2배) 가능성 work를 middle이 발행한다(사전 결정, 번복 가능). G4는 계속 보류한다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: W49SC처럼 하네스 예외가 또 실패할 위험이 있다. 그래서 "최종 예외"와 사후 방향을 미리 고정했다. 문서 반영 뒤 `make check` 840 passed/496.98s + Ruff/compileall/mypy/`CONTEXT_PASS`, `SAFETY_PASS`(Fast일 뿐). G1 PASS·사용자 승인 아님.
- 다음 한 가지: work가 W50RX 카드 §3대로 pre-gate를 통과시킨 뒤 fresh 동기 1회를 실행한다. 그다음 middle이 R1~R4를 raw로 재계산한다.
