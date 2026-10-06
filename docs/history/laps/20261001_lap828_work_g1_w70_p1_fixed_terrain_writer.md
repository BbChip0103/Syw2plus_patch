# 2026-10-01 | lap 828 | G1 W70 P1 fixed-terrain writer work

- 날짜/lap/목표: 2026-10-01 / 828 / fixed terrain buffer writer→asset-key 계보 귀속.
- 가설/합격식: `0x00BA3D30..0x00C0BD30` 3지점 write와 `0x4324E0/0x433019/0x4332F0` entry를 자연 camera redraw에서 연결한다. writer EIP/source/destination이 asset key까지 소급되면 PASS; source/cache copy만이면 `BLOCKED/strategy`.
- 변경파일: `tools/g1_terrain_writer_trace.py`, `tools/g1_saved_scene_probe.py`, `tests/test_g1_terrain_writer_trace.py`; 제품 EXE/원본/참고 저장소/게임 로직 변경 없음; 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본·fixture SHA: original `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`.
- 환경/fixture: non-synthetic save006, private Wine32/prefix, private Xvfb, logical 800x600 baseline, census-only original lane; `RIGHT` 실제 키 입력.
- 실행명령: `PYTHONPATH="$PWD" python3 tools/g1_saved_scene_probe.py --runtime-root local/runtime/g1_w70_lap828_p1_fixed_terrain_r5 --artifact-root ../temp/Syw2plus_patch/g1_w70_lap828_p1_fixed_terrain_r5 --census-only --terrain-trace`.
- 반복/수리: r1/r2는 새 breakpoint 카운터·trace key 삽입 결함으로 FAIL(raw/cleanup 보존); state entry 등록과 `_poll_observation` 배치를 수정했다. r3/r4는 probe/camera PASS이나 GDB summary 종료 경계를 확인했다. 반복 breakpoint를 16 sample로 bounded하고 r5 fresh 실행을 완주했다.
- 수치/PASS: r5 exit0, source unchanged, cleanup PASS, camera `[158,101]→[160,99]`, fixed watchpoint 3/3 arm·3/3 hit, writer EIP `0x468c93/0x468c9c`, 세 terrain entry 관측.
- raw provenance: writer-events `b7e9fc9c5d1e5c71ac64ac1e5747bef631c1f6536fc962d2e65287a88aa45178`; census `53c2d3bf5fff852ec549746e1fa92e9f92509038a15555c18a062ae88541d957`; present trace `b32f7bc5e33a680dde370bf090e69163d46641af54a419230aa9bf0f5ac5e0cc`. GDB summary는 미생성되어 raw를 사용한다.
- static 대조: original disassembly `0x468C60..0x468CB7`의 `rep movsd/movsb`와 wrapper `0x468C30`, callers `0x435593/0x435910`을 대조했다. source pointer는 관측됐지만 stable resource/tile key는 없다.
- 판정: fixed-buffer writer/natural redraw PASS(partial), writer→asset-key `BLOCKED/strategy`, G1 HOLD. W70/Scale2x/GDI SKIP.
- 다음행동: 승격 strategy가 caller/source-table 추적 지속 또는 P1 폐기를 판정한다. 이번 세션은 종료한다.
