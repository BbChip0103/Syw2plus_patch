# 2026-10-01 | lap 830 | G1 W70 P1 asset-key runtime trace

- 날짜/lap: 2026-10-01 / 830
- 목표: `0x435400` `(tile file,frame)`와 실제 YTL source pointer table equality fresh proof
- 가설: 원본 `base[file*0xBF8] + offset[file*0x2FE+frame]`가 0x435400과 blitter push source를 연결한다.
- 변경파일: `tools/g1_terrain_writer_trace.py`, `tests/test_g1_terrain_writer_trace.py`,
  `analysis/memory_maps/g1_w70_p1_asset_key_trace_lap830.md`, 이 lap 기록,
  `docs/STATUS.md`.
- 원본/fixture SHA: EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`.
- 실행: `PYTHONPATH="$PWD" python3 tools/g1_saved_scene_probe.py --runtime-root
  local/runtime/g1_w70_lap830_asset_key --artifact-root
  ../temp/Syw2plus_patch/g1_w70_lap830_asset_key --census-only --terrain-trace`.
- 수치: key 256건/고유 key 25/비0 247; blitter 1061건; equality true 1061,
  false 0, unknown 0; digest 변형 0; PS3 100%; renderer `0xBA3D30`; watch write 3.
- 결과: runtime `PASS`, source unchanged `true`, cleanup `ok=true`; P1 mapping `PASS(partial)`.
- 한계: `RIGHT`는 save006 위치에서 camera no-change였고 기존 fallback `DOWN`이 camera를
  `[158,101]→[159,102]`로 이동했다. `RIGHT` 단독 이동 성공은 주장하지 않는다.
- raw: writer events SHA `95376b920c09200e261af60aff31db7fc101dac0f8e1b1d6796233cb7bc02f2a`,
  census SHA `ebf43a1dc51e96935d1db614f553a171afec7441c728f600c589fd4f5dd15fd2`,
  probe result SHA `5de9c0cd84335d45768f9ebc8307d90a3ca594f30a9e686a31c8c9ca7f0d6455`.
- fixture: non-synthetic save006; private game/prefix/display; no product EXE patch.
- 다음행동: 새 middle이 이 raw와 테스트를 독립 재검수한 뒤 P2 identity asset mapping으로
  넘어갈지 판정한다. W70/Scale2x/GDI 구현은 그 전까지 보류한다.
- Fast: 이 기록 작성 시점에는 pending; 최종 수치는 `docs/STATUS.md`에 보강한다.
