# 날짜 | lap 648 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Codex native session / hands-on 구현 작업자 / high.
- 가설: lap647의 `ESP=0x31FA50`에서 반환주소 칸으로 판독된 `0x31FA4C`에 조건부 하드웨어 watchpoint를 걸면 20칸 스택 핸들 배열을 덮는 실제 writer PC와 함수를 귀속할 수 있다.
- 예상 PASS / FAIL 조건: watchpoint hit에서 쓰기 PC·명령·함수·스택이 기록되면 귀속; watchpoint 미발생 또는 필수 drag 실패면 BLOCKED.
- 변경 파일 / source fingerprint / 커밋: `tools/g5_selection_return_watch.gdb` 신규 추가. SHA `2bba7147b782a88a27e22a1dabba9a7e008631e4dc3e13c6f163683dff4da936`; 제품 바이너리·원본·참고 저장소·커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 `7c6e372a576b27843c79cb906d024a4aab044166c4ce4625f39f05475a2b1d4d`; Wine/Xvfb 1600×1200, solo owner0, synthetic type2×55 dense 7×8, PS3.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `G5_SELECTION_TRACE_CONTROL=<lap648 control> PYTHONPATH=. .venv/bin/python tools/g5_candidate_drag_probe.py --variant candidate --runtime-root local/runtime/g5-lap648-candidate-return-watch-b --artifact-root <lap648 artifact>`; `G5_SELECTION_TRACE_CONTROL=<lap648 control> gdb -p 2338974 -batch -nx -x tools/g5_selection_return_watch.gdb`. GDB raw SHA `b7bc46ac834f35d974ebbb1f1a0f16aafadfb9d36b4d1303d66ce8504ea14655`; probe-result SHA `451d89d0cb037b9d33b89d974124ddfdd67ebd1785dd926ad4deaa8c66e73e25`; before/after PNG SHA `b05699c8870f6be0a589ba6836e4786fceacc4658716a19c6fbb3d26dd9feaeb` / `8d2195428871f9aafd390e46e68b939172091b888b72bcd8fd8f1c5f60fd9a20`.
- 측정값 / 판정: GDB hardware watchpoint 1은 무장됐고 `armed.json`, `probe_ready.json`, `continue.flag`가 생성됐으나 `RETURN_SLOT_WATCH_HIT` 0회. 후보 `selection_after=0`, `drag produced no selection`, exit2; cleanup `ok=true`, source unchanged=true, private candidate SHA 일치. PASS/FAIL/SKIP: 필수 runtime **FAIL**, writer 귀속 **SKIP**, 50/51·command50·canary/save/load **SKIP**.
- 회귀 / 남은 위험 / 다음 행동: watchpoint 미발생과 selection0의 관계가 분리되지 않아 `0x31FA4C` writer PC/old bytes를 확정할 수 없다. 승격 작업자가 raw/probe/capture와 동일 fixture 입력 계약을 독립 검수한 뒤, 원인과 안전 범위가 성립할 때만 다음 fresh probe를 정한다. G5 PASS·마일스톤 승인은 주장하지 않는다.

판정: **`BLOCKED(candidate_return_watch_no_hit_and_selection_zero)`**.
