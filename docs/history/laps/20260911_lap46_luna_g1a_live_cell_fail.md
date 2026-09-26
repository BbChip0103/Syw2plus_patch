# 2026-09-11 | lap 46 | 목표 G1-A live command-cell/production probe

- 실제 provider/model/effort / 지정 역할: 지정 Codex `gpt-5.6-luna` / high / hands-on work.
  현재 세션 표면에는 실제 model ID/effort가 별도 노출되지 않았다.
- 가설 / 사용자 관찰: lap45에서 확인된 read-only command-cell 테스트 계약이 새 고정 원본의
  실제 PS3 live process에서 group 2..5 cell을 찾아 production 입력까지 연결할 수 있다.
- 예상 PASS / FAIL 조건: 새 private manifest의 원본 SHA·격리·1600×1200 root·800×600 crop,
  setup/PS5→PS3/tick, surface/modules, live cell, 필수 입력 및 cleanup을 같은 run에서
  기록한다. 필수 live cell이 비거나 입력 효과가 UNKNOWN이면 FAIL하고 재시도하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/EXE/DLL/assets와 source는
  변경하지 않았다. 현재 source SHA는 `tools/runtime_env.py`
  `9e82a19e2888c04701dca40baf22fa5391c13775e7e60b531671829342d84845`,
  `tests/test_runtime_env.py`
  `0d02e81cc50e230813c63e0b2275aa1988a2237b6499a91501130dff41e0df84`,
  `tests/test_runtime_guards.py`
  `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`, map
  `b2897bdecbb6e86de76f649073c230334b471ac28a911559347e1f3e164b59e5`다. docs와
  `loop/ESCALATE_SOL`만 이번 기록으로 추가했으며 Git unborn/uncommitted, commit 없음이다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본과 private copy
  EXE 모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다. run
  `local/runtime/20260911_052013_1474139_0`, manifest SHA
  `766ba1e6283fa598e1dbaa0f49271e3e9115a7873887b8901b798d0ec56e2bdf`, display `:91`,
  private win32 prefix, `LANG/LC_ALL=ko_KR.UTF-8`, `WINEDLLOVERRIDES=ddraw=b`를 사용했다.
  fixture는 새 private copy의 합성하지 않은 기본 2인 random game이며 memory write/control
  bridge/resource grant는 없었다. PS3/tick=6, owner0 nation2 active2, owner1 nation3 active2다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor`; targeted pytest; `make check`;
  `bash checks/safety.sh check`; `prepare --timeout 60`; manifest `check`; 그리고 정확히 1회의
  `g1-baseline --screen 1600x1200x24 --timeout 90`. 주요 artifact는
  `output/g1_baseline.json` SHA `7a57635316c41f72b1bb90b60b177960feb660fcd594397492c46c5d1df5212e`,
  `output/g1_a/verdict.json` SHA `9492bcc4b99b2b19c7b2e1d6da9f5b4e48a78f399a9aa4ea61d48f40ff62bc9f`,
  `inputs.jsonl` SHA `5160ffb0f66b1e2687435a8430b4f7687991712d34d1a31ffe0fb4089e187ecd`다.
  PNG 8개는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/`에 보존됐다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): doctor 원본/runtime 도구 PASS, targeted **36
  passed**, Fast **106 passed**, Ruff/compileall/mypy/context **PASS**, safety **SAFETY_PASS**.
  runtime은 1600×1200 root, 800×600 content, PS9→PS7, solo selector, PS5/committed=1,
  local=0 ready=1, PS5→PS3/tick6, unit selection 0→1 first slot1199, surface/modules/cleanup
  PASS. 그러나 `_read_g1_command_cell_provenance`가 `expected one command cell for each
  group 2..5, got []`로 중단해 `production_cell=null`, required_inputs=false, overall **FAIL**;
  production/drag/minimap은 SKIP/미실행이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `verdict.json`의 cleanup은
  `ok=true`, owned launcher/Xvfb 중지, prefix processes empty, global kill false다. 별도
  기존 Xvfb(:78/:186/:187)는 건드리지 않았다. G1 제품 patch/2x output, live worker cell 의미,
  production 효과, drag/minimap, G2~G4는 미검증이다. 사용자 승인 없음. 이 FAIL은 실제 생산
  실패가 아니라 production 입력 전 live cell 관측 실패이며, Sol/high 독립 검수가 필요하다.
- 기록 후 게이트: `make check`는 **93 passed / 13 failed**로 종료했다. 실패들은 이번 STATUS
  갱신으로 188줄이 되어 loop safety 180줄 상한을 넘은 startup gate에서 발생했으며, 별도
  `bash checks/safety.sh check`도 같은 제한 위반을 보고했다. 이 문서로 상세 provenance를
  보존하고, 다음 middle이 STATUS를 180줄 이하로 archive/reduce하기 전에는 green gate로
  주장하지 않는다. 이 절차 실패를 고치기 위한 재실행은 하지 않았다.
- 다음 한 가지: Sol/high가 같은 run의 manifest/verdict와 현재 helper/map/test/source SHA를
  독립 대조하여 빈 live cell이 주소·stride·pool layout 문제인지 판정하고, 필요한 경우에만
  정확한 work 수리 범위와 old bytes/version reject/원복 근거를 반환한다. 새 게임 run·좌표 변경·
  바이너리 패치는 그 판정 전 금지한다.
