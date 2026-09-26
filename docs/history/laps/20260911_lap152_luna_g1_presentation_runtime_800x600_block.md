# 2026-09-11 | lap 152 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex hands-on work tier / high.
- 가설 / 사용자 관찰: 승인된 기본 source와 새 private runtime에서 lap150의 선변환 없는
  `(184,560)` 입력 계약을 적용하면 1600×1200 physical client에서도 PS9→PS7→PS3와
  기존 finalization이 통과한다.
- 예상 PASS / FAIL 조건: logical surface 800×600, client 1600×1200, scale 2×2,
  입력 PS9→PS7→PS3, capture/final summary/validator/cleanup PASS. client가 800×600이면
  입력 경로와 무관하게 G1 runtime FAIL/BLOCKED이며 재실행하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 코드 변경 없음.
  `loop/ESCALATE_SOL`, `docs/STATUS.md`, 본 기록만 uncommitted로 갱신.
  harness `tools/runtime_env.py` SHA `69d0c54da7da06849ef8a6929ad7e6fec43bf12b87fefb6ba3e605cee240a296`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: source 및 private
  EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; source symlink
  목록 빈 출력; fresh `/tmp/syw2plus_lap152.8fFRM7` helper/target/bridge PE32.
  `local/runtime/20260911_194932_189255_0`; 새 private copy/prefix/display `:91`,
  기본 2-player random game, synthetic/memory_writes/control_bridge/resource_grant=false,
  diagnostic_bridge=true. G2~G4 N/A/SKIP.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor` PASS; `make check` 179 passed,
  Ruff/compileall/mypy/CONTEXT PASS; `bash checks/safety.sh check` PASS; manifest check 및
  `make doctor-runtime` PASS. `runtime_env.py prepare --bridge ...`는 기본 source로 PASS.
  `g1-presentation-trace`는 지정 명령으로 정확히 1회 실행. evidence
  `fee75b439fb8e7861d7019026b38db72e43ae2c3b13ad99b5df0bfbf984d154f`, trace
  `790ef90869cc1776fdcff25fde7533b78586cc001cb8d7227b44cdf44f5366dd`, install
  `ff0944a34f30d52bc5fb438939a83c9ba4cb2751ed79e26049c93fc958ca226e`, provenance
  `0d02380725c707f5da988a129fe2bc43a64c0d6ef2287aa5d630fe6e7c2ba69e`; 캡처 PNG 4개는
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/`에 보존되고 모두 800×600.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): input `logical_content=[184,560]`,
  `x11_sent=[184,560]`, scale 1×1, PS9→PS7→PS3, tick 10 PASS. root 1600×1200이나
  content child/physical client 800×600, `scaled_2x=false`, `dxwrapper.ini`는 old
  `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`와 byte-identical.
  summary 1/event 651/dropped 0/process exit 0/DLL detach/validator/owned cleanup PASS.
  제품 G1 physical 2x는 FAIL/BLOCKED. validator의 overall PASS는 제품 판정이 아니다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: Fast/safety/doctor PASS. 원본·참고
  저장소 및 EXE/DLL/assets는 변경하지 않았다. approved candidate
  `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`가 이번 private copy에
  적용되지 않았으므로 2x 후보 실행은 미검증. 중간 tier 독립 검수 및 사용자 승인 없음.
- 다음 한 가지: 승격 작업자가 config helper의 private-copy 적용 경계를 old/candidate/
  원복 SHA로 독립 판정하고, 승인 후 새 fresh runtime 1회에서 1600×1200 client와 입력을
  함께 검증한다. 이번 run은 재사용하지 않는다.
