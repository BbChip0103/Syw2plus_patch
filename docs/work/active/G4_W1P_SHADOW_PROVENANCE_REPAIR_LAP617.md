# G4 W1P — shadow provenance 기록 계약 수리

- 발행: lap617 middle. lap616 보존 raw와 현행 source를 독립 대조한 결과다.
- 단일 가설: `g1-baseline` provenance의 고정 environment allowlist와 shadow 산출물 메타데이터를 수리하면, 다음 실행은 `INMM_AI_SHADOW=1`과 정확한 raw 경로/해시를 fail-closed로 증명할 수 있다.
- 역할: 다음 work(Luna/Sonnet5 high). 게임 코드·제품 EXE·bridge 동작은 수정하지 않는다.

## 1. 확정 진단

1. `g1_baseline()`은 `env = dict(os.environ, ...)`로 부모의 `INMM_AI_SHADOW=1`을 Wine 자식에 전달했다.
2. `ai_shadow_install()`은 그 값이 정확히 `1`일 때만 `C:\inmm_ai_shadow.jsonl`을 `CREATE_ALWAYS`로 만들고 `0x0041CBE5`를 설치한다. fresh prefix의 512개 정상 row는 shadow 활성화의 직접 증거다.
3. `provenance.json` 작성부는 environment를 `DISPLAY/WINEPREFIX/WINEARCH/LANG/LC_ALL/WINEDLLOVERRIDES` 6개로 제한해 `INMM_AI_SHADOW`를 항상 누락한다. 이는 실행 미설정이 아니라 재현 가능한 기록 스키마 결함이다.
4. 따라서 lap616 §4 raw 수치와 shadow 활성화는 ACCEPT하지만, 카드 §3·§164의 명시적 env/path provenance는 REJECT한다. 현재 판정은 `BLOCKED(harness_provenance_contract)`이며 `FEASIBLE_BASELINE`으로 승격하지 않는다.

## 2. work 변경 범위

1. `tools/runtime_env.py`의 `g1-baseline` provenance environment allowlist에 `INMM_AI_SHADOW`를 추가한다. 임의의 전체 환경 덤프나 비밀 값 기록은 금지한다.
2. provenance에 고정 shadow 경로, 존재 여부, SHA256, 행 수를 기록한다. 경로는 해당 manifest의 private prefix 아래로 resolve되어야 하며 symlink/외부 경로이면 fail-closed한다.
3. `INMM_AI_SHADOW=1`인데 raw가 없거나 비었거나 해시/행 수 계산이 실패하면 provenance 계약을 PASS로 쓰지 않는다. 비활성 실행은 `null/false`를 명시해 활성과 구분한다.
4. 기존 lap616 raw/provenance를 수정·backfill하지 않는다. 게임 실행, 기존 runtime 재사용, 제품 AI/issuer/pathfinding 변경, bridge 수정, 새 의존성은 금지한다.

## 3. 회귀와 종료 조건

1. `tests/test_runtime_env.py`에 활성 env가 provenance에 정확히 기록되고 private shadow 파일의 path/SHA/row count가 일치하는 회귀를 추가한다.
2. 비활성 또는 missing/empty/외부 경로가 활성 PASS로 오인되지 않는 음성 회귀를 추가한다.
3. targeted pytest, `bash checks/safety.sh check`, `make check`를 실행한다. 필수 검사가 예상 밖으로 실패하면 변경을 보존하고 `loop/ESCALATE_SOL`에 승격하며 수리 반복이나 게임 실행을 하지 않는다.
4. 다음 새 middle이 코드 diff와 회귀를 독립 검수한다. 새 fresh 게임 1회가 필요한지는 그 뒤 strategy가 별도 판정한다; work가 실행 예산을 열지 않는다.

