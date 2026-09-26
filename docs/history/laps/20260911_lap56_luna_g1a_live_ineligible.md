# 2026-09-11 | lap 56 | 목표 G1-A live command-cell eligibility run

- 실제 provider/model/effort / 지정 역할: 사용자 지정 Codex `gpt-5.6-luna` / high / hands-on work.
  현재 세션 표면은 실제 model ID/effort를 별도 노출하지 않아 실행 증거로 주장하지 않는다.
- 가설 / 사용자 관찰: lap55가 확인한 selection identity coherence helper를 그대로 사용하면 새
  private 무수정 원본의 기본 2인 random game에서 selected HQ command branch와 group2..5
  production cell provenance를 관측할 수 있다.
- 예상 PASS / FAIL 조건: helper/current SHA와 원본 SHA를 대조하고 새 private copy/prefix/빈
  display의 고정 `g1-baseline` 1회가 stable eligible group2..5와 strict hit까지 도달하면 PASS.
  실제 predicate가 거짓이면 exact selection identity/predicate/raw pool/cleanup을 보존하고
  재시도 없이 Sol에 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/EXE/DLL/assets와 helper/test는
  변경하지 않았다. helper `tools/runtime_env.py` SHA `c43b20ccbd7bad3da4fa2d704bb36e73388ed9b2cb50709d8cc96f0aa321b2d4`,
  `tests/test_runtime_env.py` SHA `6a38c6b8b304edc31e23c71c65b8f8c3dc8b5042a97f93397ce671cea0d4bb4f`,
  `tests/test_runtime_guards.py` SHA `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`다.
  Git unborn, `LOOP_ALLOW_COMMITS=0`, commit/push 없음. 새 local runtime과 이력/STATUS/marker는
  uncommitted 보존 대상이다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본 및 private
  copy EXE 모두 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  manifest `local/runtime/20260911_063022_2078607_0/manifest.json` SHA
  `3d8d4f8d2a0f5cefd98e6a6d6fd6f3a964669cc4c4f56849f9c36738651e5de6`. 환경은 새 private win32
  Wine prefix, private Xvfb virtual desktop `1600x1200x24`, `LANG/LC_ALL=ko_KR.UTF-8`,
  `WINEDLLOVERRIDES=ddraw=b`; fixture는 memory write/control bridge/resource grant 없는
  기본 2인 random game이다. PS3에서 owner0/1 nation 2/3, active units 각 2, selected
  slot1199/type58이 관측됐다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor`; `.venv/bin/python tools/runtime_env.py
  prepare --timeout 60`; `.venv/bin/python tools/runtime_env.py check --manifest
  local/runtime/20260911_063022_2078607_0/manifest.json`; 고정 명령
  `.venv/bin/python tools/runtime_env.py g1-baseline --manifest local/runtime/20260911_063022_2078607_0/manifest.json
  --screen 1600x1200x24 --timeout 90`을 정확히 1회 실행했다. 이후 `make doctor-runtime
  MANIFEST=local/runtime/20260911_063022_2078607_0/manifest.json`, `make check`, `bash
  checks/safety.sh check`를 실행했다. `output/g1_baseline.json` SHA
  `cca12b7fa9aace138a891cd53d2309357749f196e3b751111885701af08aa63a`, verdict SHA
  `8dfddc65a78385e5eefa9266074bd33defd0c2030be16dc5fda4d108742397c3`, inputs SHA
  `73d76eca53170b425d467b1582c87ab5e6d4331c48fc874ba7c4a2961471f925`, provenance SHA
  `caffab39e58d06701b1ecf425dcf9134a22e014e53a14435e4e576fd2c636d40`이다. 800×600 PNG 8개는
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/`에 저장되었고 각 경로/해시는 baseline JSON에 있다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): private 1600×1200 root, 800×600 content,
  original hash, PS9→PS7, selector multiplayer→solo, confirm PS7→PS5, committed mode=1,
  auto-ready local0/value1, start PS5→PS3/tick6, selection 0→1/slot1199, module hashes와
  cleanup은 PASS. `command_branch`는 call `0x0049B6D0`, before/after identity stable,
  selected slot1199/type58, type predicate address `0x009C21D4` raw `16`, mask `0x08`, masked
  `0`, passes false; selected-unit predicate raw `0`, passes true. 따라서 stable but ineligible로
  `49B6D0 ineligible` 즉시 FAIL, `production_cell`/필수 입력 전체는 미도달이다. verdict overall
  **FAIL**, checks `original_hash/private_1600x1200_root/800x600_content_crop/surface_ps9_ps3/
  modules_hashed/cleanup/same_run_scene=true`, `required_inputs=false`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `make check` **114 passed**, Ruff/
  compileall/mypy/context PASS, safety **SAFETY_PASS**, `doctor-runtime ok=true`; run cleanup
  `owned_launchers_stopped=true`, `xvfb_stopped=true`, `prefix_processes_after=[]`,
  `global_kill_used=false`. 오류는 실제 장면의 raw predicate 관측이지 원본 메모리 손상/OOM이나
  제품 완료 판정이 아니다. G1 2배 제품 출력/입력, G2~G4 및 사용자 승인은 여전히 UNKNOWN/
  미완료. 재시도·좌표 보정·helper/binary 변경은 하지 않았다.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high middle이 위 artifact, current helper SHA, raw map
  `0x009C21D4`/`0x00891D4C`, call-site와 stable-ineligible fail-closed semantics를 독립
  검수하고, type58/slot1199가 실제 production target이 아닌지와 다음 좁은 probe 필요 여부를
  판정한다. 그 전에는 새 G1 runtime 실행이나 코드/바이너리 변경을 하지 않는다.
