# 2026-09-12 | lap 281 | G1 정적 유닛 레코드 오프셋 상수 승격

- 실제 provider/model/effort / 지정 역할: Codex work tier / hands-on 구현 작업자 / high.
- 가설 / 사용자 관찰: lap280이 원본 정적으로 확정한 `internal_id=+0x29C`,
  `x=+0x2A2`, `y=+0x2A4`를 중앙 runtime 상수로 승격하면 reader의 매직 오프셋을
  제거하면서 기존 레코드 해석을 보존한다. 사용자 신규 관찰 없음.
- 예상 PASS / FAIL 조건: 원본 SHA가 기준과 일치하고, 세 상수가 정확한 값/폭으로
  정의되며 runtime driver가 이를 사용하고, targeted/Fast 정적 검사가 통과하면 PASS.
  주소 근거 불일치나 필수 검사 실패면 변경을 보존하고 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` `dd2ad0439111d6b1e098d0ea771db172847dfa42f04ed085c4567f2ac8500190`,
  `patches/population/runtime_driver.py` `ae4ff9393247ce31eab7c953b040f7d3c5aa8b0386af025046382c7d4e4291b5`,
  `tests/test_runtime_env.py` `26e544b37b7d062c9f7ac28170a8cc8acf8340c1135c72a089e2f3202ec4963e`,
  `analysis/memory_maps/population_runtime_bridge_0910.md`
  `bc6252065e591f4c27ec8f807893866b000f3f1b49d6c017d42d717f22e68889`,
  `docs/STATUS.md` `d04de55eb4cec190c2eb2cba358187625dae1bc3a71d9c9394afcb0d8093c3d3`.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`); 미커밋 상태 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  읽기 전용 원본 `syw2plus_original.exe` SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  후보 EXE/DLL 없음. Linux 정적 도구와 저장소 `.venv`; 활성 플레이어·지도·군대·fixture는
  N/A. 게임/Wine/Xvfb/원본 재실행/Stage B는 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `objdump -D -Mintel -j .text` 및 `sha256sum`으로 원본 accessor/좌표 참조를 확인했고,
  좌표 참조는 `0x66BA32` 115회, `0x66BA34` 115회였다. targeted
  `pytest -q tests/test_runtime_env.py -k unit_record_offsets` → 1 passed;
  driver `--help` 정상; `make check` → **292 passed in 44.06s**, Ruff/compileall/mypy
  10 files 성공, `CONTEXT_PASS`, `SAFETY_PASS`. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **PASS (정적 구현 범위).**
  `G1_UNIT_INTERNAL_ID_OFFSET=0x29C`, `G1_UNIT_X_OFFSET=0x2A2`,
  `G1_UNIT_Y_OFFSET=0x2A4`를 `tools/runtime_env.py`에 정의하고
  `runtime_driver.py`의 3개 reader 접근이 이를 사용하도록 연결했다. 원본 `0x40F540`
  의 `DWORD [eax*8+0x66BA2C]`와 `0x40F5D0/0x40F5F0`의 x/y WORD accessor 근거를
  memory map에 기록했다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 검사 PASS. 다음 새 middle이
  상수 연결과 memory-map 인용을 독립 검수해야 하며, 이 work는 자기 승인하지 않는다.
  S1 실제 결정성, Stage B, WM_CLOSE, G2~G4, G3 저장 포맷 넘침은 그대로 미해결이다.
  제품·마일스톤 사용자 승인 없음.
- 다음 한 가지: 상위(Astra)가 runtime 쌍/Stage B 예산과 G3 저장 포맷 방향을 결정한다.

