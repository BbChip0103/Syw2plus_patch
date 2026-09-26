# 2026-09-12 | lap 319 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex work, `gpt-5.6-luna`, high; hands-on static probe/test implementation.
- 가설 / 사용자 관찰: lap318 middle이 지정한 F1 수리대로 objdump 접힌 명령은 정상 연속줄을 재구성하고, 명령 경계는 다음 디스어셈블리 주소 델타로 검증하면 무징후 절단을 fail-closed할 수 있다.
- 예상 PASS / FAIL 조건: 두 reset store에서 PE 값·주소 델타·재구성 열 바이트가 각각 10B로 일치하면 PASS. 연속줄 누락, 무경계 절단, gap, overlap, 섹션 범위 밖 읽기는 명시적 FAIL. 기존 R2 수치 변동·원본 SHA 변동은 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `docs/history/laps/probes/20260912_lap319_work_v7_reset_store_bytes_probe.py` SHA `eeed0913ff2c9d041890315f99775aefef9ea098a24024bfed0244af1671e6d3`
  - `tests/test_lap319_reset_store_bytes_probe.py` SHA `4a246d15882d00f046f1fef1dbbe55821c9cd0614dfbf233ac10581e2248522b`
  - generated `logs/lap319/lap319_reset_store_bytes.json` SHA `09e012dcd536dfd9c81af469e0fd4de16cbede02567e9fdc0aa00bf8f4161def`
  - `docs/STATUS.md` updated; commit 없음 (`LOOP_ALLOW_COMMITS` 기본 0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `Syw2plus/syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (make doctor 전후 동일). 후보 EXE/DLL/assets 없음. 정적 synthetic fixture 6종: 정상 folded 1, continuation 누락, next-address 경계 누락, continuation gap, overlap, PE section 범위 밖. 활성 플레이어/지도/군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor`; `python3 docs/history/laps/probes/20260912_lap319_work_v7_reset_store_bytes_probe.py > logs/lap319/lap319_reset_store_bytes.json`; 같은 probe 2회 stdout `09e012dc…f4161def` byte-identical; `python3 -m pytest -q tests/test_lap319_reset_store_bytes_probe.py`; `make check`; `bash checks/safety.sh check`. 게임/Wine/Xvfb/Stage B/PNG/click 실행 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): probe checks **21/21 PASS**. window/entry/failure/success **753/753/7/724**, unresolved **0**, screen writers **4**, failure-arm writers **0**. `0x4324B8`: PE/column/boundary `c7051cbfe50080020000`/10/10; `0x4324C2`: `c70520bfe500e0010000`/10/10. targeted **8 passed**, `make check` **350 passed**, Ruff/compileall/mypy/CONTEXT_PASS, safety **SAFETY_PASS**. 제품 G1~G4 증거는 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap313~318 probe/test/report, pin, `tools/`, `patches/`, 원본 PE는 변경하지 않았다. F1 수리는 정적 증거이며 실제 scene/input, WM_CLOSE, Stage B, runtime, 제품 마일스톤 승인이 아니다. 다음 새 middle이 값과 경계를 독립 재유도해야 한다. 사용자 승인 범위는 bounded repair→fresh validation이며 제품/출시 승인은 없음.
- 다음 한 가지: 다음 새 middle이 lap319 probe/report를 import하지 않고 원본 PE와 fresh objdump에서 reset 바이트·주소 델타·fixture fail-closed 동작을 독립 검수한다. 그 전에는 runtime/Stage B/Wine/Xvfb/제품 EXE 변경을 시작하지 않는다.
