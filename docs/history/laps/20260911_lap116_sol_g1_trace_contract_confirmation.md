# 2026-09-11 | lap 116 | G1 trace contract confirmation

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-sol`/high 중간 계획·컨펌 지정. 현재
  세션의 모델 ID는 별도 runtime 명령으로 재검증하지 않았으며, 게임 코드 hands-on 수정은 하지 않았다.
- 가설 / 사용자 관찰: lap115의 9개 Surface7 vtable 오류와 final summary 부재를 보존 trace와
  source/validator 계약으로 독립 분리하면 validator 오류인지 bridge/runner 오류인지 판정할 수 있다.
- 예상 PASS / FAIL 조건: helper source·테스트·fresh exact 좌표와 해시가 일치하고 두 validator 오류를
  원본/trace/source로 단일하게 설명하면 중간 판정 PASS다. 근거 충돌, 필수 gate 실패, 제품/마일스톤
  경계이면 변경을 보존하고 승격한다.
- 변경 파일 / source fingerprint / 커밋: 문서만 변경 — 이 lap 기록,
  `docs/plans/20260911_lap116_g1_trace_contract_repair_card.md`, `docs/STATUS.md`.
  구현 시작 SHA는 `tools/runtime_env.py=48b8aeee...`, `tests/test_runtime_env.py=37ee237f...`,
  `tools/inmm_stub/direct_draw_trace.c=906562e0...`, validator `541e8448...`; 커밋·push 없음
  (`LOOP_ALLOW_COMMITS=0`, uncommitted 보존).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본과 lap115 private EXE는
  모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp=0`, PE32.
  제품 후보 없음. 보존 run `local/runtime/20260911_141737_1611146_0`, 새 private copy/Win32
  prefix/Xvfb의 기본 two-player random game, synthetic=false, memory_writes=false,
  resource_grant=false, control_bridge=false, diagnostic_bridge=true. 새 runtime/game 실행은 SKIP했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `cmp -s`, `file`, `jq`로 manifest/raw/trace/
  evidence/provenance/verdict와 source를 재검산; `make doctor`; `make check`;
  `bash checks/safety.sh check`. 보존 processed trace `4ae51453...`, raw `e6fd4b48...`, evidence
  `8af4ed05...`, provenance `c9c98e5c...`, verdict `00033d09...`; PS3 PNG
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260911_141805_20260911_141737_1611146_0-presentation_1612610_ps3_scene_1789103885383780966.png`
  SHA `e3541185...`, 800x600을 해시·육안 대조했다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **MIDDLE CONFIRM PASS / HELPER CONFIRMED /
  TRACE CONTRACT REVISE / GAME RUN BLOCKED**. helper에는 `--sync`가 없고 회귀는 already-at-target,
  move/poll, bounded mismatch, malformed/query failure를 고정한다. fresh evidence는 root
  `(608,564)->(760,40)`, returncode0/polls1, PS9→PS3, tick3, capture 800x600이다. trace 100 events,
  `CreateSurface` 39/고유 surface30; `0x01E6D848`은 seq50=49 뒤 seq54..70 9회=0이다.
  bridge의 installed-slot 분기가 지역 count를 0으로 남기는 계측 버그이며 validator의 49 계약은
  맞다. summary는 0개/마지막 seq100 `blt_fast`; detach-only emitter보다 앞서 live trace를
  copy/validate하는 runner 수명주기 결함이다. doctor top `ok=true`/original verified,
  `make check` **153 passed**, Ruff/compileall/mypy/context PASS, safety `SAFETY_PASS`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: helper 확인은 G1 2배 출력/필수5입력,
  complete present, G1/M1 또는 사용자 승인이 아니다. patch generate/restore, 새 candidate, 실제
  runtime, G2~G4는 SKIP/미검증. trace가 bridge/runner 수리 뒤 새 middle 확인을 받기 전 재실행 금지.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가
  `docs/plans/20260911_lap116_g1_trace_contract_repair_card.md`의 허용 범위에서 재사용 surface와 clean
  finalization 계약을 source/tests로 수리하고, 기계 gate까지만 수행한 뒤 새 Sol/high에 넘긴다.
