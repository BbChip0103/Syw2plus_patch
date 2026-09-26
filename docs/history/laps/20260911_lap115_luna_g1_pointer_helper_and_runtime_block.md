# 2026-09-11 | lap 115 | G1 neutral-pointer helper and fresh runtime block

- 실제 provider/model/effort / 지정 역할: Codex 실무 작업자 lane (Luna/high 지정). 게임 구현·상위
  방향·중간 컨펌은 수행하지 않았다. 이번 바퀴는 lap114 Sol 카드의 허용 범위만 수행했다.
- 목표 / 가설 / 예상 판정: `xdotool mousemove --sync`의 불투명 timeout을 제거하고, 이동 전 좌표와
  bounded `getmouselocation --shell` 결과가 정확히 목표 root 좌표와 일치할 때만 neutral capture를
  허용한다. helper targeted/Fast/doctor/safety가 PASS하고 새 trace의 전체 identity chain과 summary가
  있으면 runtime 증거를 갱신하고, 아니면 원인과 raw를 보존한 BLOCKED/ESCALATE_SOL이다.
- 변경 파일 / fingerprint / 커밋: `tools/runtime_env.py` 최종 SHA
  `48b8aeee07ae02a96f1211ffc29f9a93f461f4afceac5b13f584cb568ccf62b9`;
  `tests/test_runtime_env.py` 최종 SHA
  `37ee237f32b107580bdf61b22415bd96143a9a5b5377d421a1bb6ac15d6d7e3f`.
  시작 SHA는 각각 `c417b9f0...`, `ab344efc...`였고, 이 두 파일만 구현/회귀 변경했다. 커밋·push 없음
  (`LOOP_ALLOW_COMMITS=0`). runtime/local와 temp 산출물은 실행 증거이며 제품 바이너리 후보가 아니다.
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본과 새 private game EXE 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp=0`, PE32.
  bridge는 저장소 밖 임시 build SHA `f2dfad3d996f9952b5d1c2f3dd7209ad2f09d45765683298507ce22cc68f3936`.
  fresh run은 `local/runtime/20260911_141737_1611146_0`, 새 전체 복사본/새 Win32 prefix/새 private
  Xvfb, 기본 two-player random game fixture, synthetic=false/memory_writes=false/resource_grant=false/
  control_bridge=false/diagnostic_bridge=true다. 기존 lap114 run/prefix는 재사용하지 않았다.
- 실행 명령 / 로그 / 캡처: 
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py`;
  `make check`; `make doctor`; `bash checks/safety.sh check`;
  저장소 밖 `.venv/bin/python patches/population/build_runtime_bridge.py --out-dir /tmp/syw2_g1_lap115.VqlrNZ/bridge`;
  `.venv/bin/python tools/runtime_env.py prepare --source /home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus --runtime-root $PWD/local/runtime --bridge /tmp/syw2_g1_lap115.VqlrNZ/bridge/_inmm.dll`;
  `.venv/bin/python tools/runtime_env.py g1-presentation-trace --manifest local/runtime/20260911_141737_1611146_0/manifest.json --screen 1600x1200x24 --timeout 90`.
  run manifest SHA `c541f88b...`, raw trace SHA `e6fd4b48...`, trace SHA `4ae51453...`, evidence SHA
  `8af4ed05...`, provenance SHA `c9c98e5c...`, verdict SHA `00033d09...`; PS3 screenshot은
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260911_141805_20260911_141737_1611146_0-presentation_1612610_ps3_scene_1789103885383780966.png`,
  SHA `e3541185...`, dimensions `800×600`이다.
- 측정값 / 판정: helper 회귀 **58 passed**, `make check` **153 passed**, doctor exit0/top `ok=true`,
  safety `SAFETY_PASS`, runtime manifest check PASS. fresh trace는 100 events:
  install2, DirectDrawCreateEx1, SetDisplayMode12, CreateSurface39, GetSurfaceDesc30, Blt2,
  BltFast14. exact pointer는 requested/last observed root `(760,40)` 및 move returncode 0/polls 1,
  PS9→PS3, tick3, 800×600 capture, cleanup `ok=true`, prefix residual 없음이었다.
  최종 판정은 **BLOCKED**: validator가 `CreateSurface Surface7 vtable method count is invalid`
  9건과 `exactly one final summary event is required`를 보고했다. 따라서 complete
  expected-IID→DD→surface→actual-desc→non-clear-present identity, G1 2배 출력/필수 입력, G1/M1,
  G2~G4, 사용자 승인은 미검증/SKIP다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인: `--sync` timeout은 새 run에서 발생하지 않았고,
  기존 `cursor_content=[760,40]` 계약도 유지됐다. 그러나 Surface7 계측 contract와 summary 부재의
  원인은 이 실무 카드 범위를 넘으며 bridge/validator/게임 수정 및 재실행은 금지한다. 새 Sol/high가
  helper와 fresh raw/evidence/verdict를 독립 검수해야 하며, 사용자 마일스톤 승인은 없다.
- 다음 한 가지: `loop/ESCALATE_SOL`에 기록한 대로 새 Sol/high가 Surface7 vtable 오류와 final
  summary 부재가 bridge 계측 계약인지 validator 계약인지 원본/trace 근거로 판정하고, 필요한 경우에만
  별도 실무 카드를 발행한다. 재실행·timeout 완화·G1 승격은 하지 않는다.
