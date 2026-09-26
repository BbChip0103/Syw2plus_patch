# 2026-09-11 | lap 33 | G1-A ready FAIL middle 독립 진단

- 날짜/lap/목표: 2026-09-11 KST / lap33 / 보존된 lap32 G1-A `ready` 입력 효과 실패의 원인 분류
- 실제 provider/model/effort / 지정 역할: Codex 중간 tier/high 지정. 현재 호출의 실제 model ID/effort는 노출되지 않아 미확인. 게임 코드·EXE·DLL·assets 수정 및 새 게임 실행 금지.
- 가설 / 사용자 관찰: lap32의 ready before/after 전체 화면과 local control crop이 모두 동일한 원인은 (A) 고정 좌표 click이 실제 준비 control에 전달되지 않았거나 (B) 준비 상태는 바뀌었지만 현재 화면/crop·reader 계약이 그 변화를 관측하지 못한 것이다. 보존 artifact와 production 결선만으로 둘을 구분할 수 있어야 한다.
- 예상 PASS / FAIL 조건: manifest·원본/copy SHA와 lap32 기록을 재확인하고, `inputs.jsonl`의 click 좌표·before/after 상태·PNG/crop 및 production click/capture/reader 경로를 대조해 A/B를 직접 근거로 분류하며 최소 work-tier 수리 범위와 정확한 version/old bytes/fail-closed·원복 조건을 정하면 middle 진단 PASS. 두 원인이 충돌하거나 artifact가 전달 여부를 입증하지 못하거나 필수 doctor/Fast/safety가 예상 밖 실패하면 UNKNOWN/REVISE로 보존하고 `loop/ESCALATE_SOL`에 후속 검증을 명시한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현·게임 파일 변경 없음. 검수 source SHA256은 `tools/runtime_env.py` `e06c73a9d9602d1f036ab3f8ebcf306a3ee01e21945fd27b54daab502f6e5e49`, `tests/test_runtime_env.py` `5ea8ea87672577bde15dc67cf647a84e382fb1fe2c8f54e9645738546ea1f9fd`, `tests/test_runtime_guards.py` `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`. 진단 문서로 `analysis/memory_maps/player_offsets.md`, 활성 카드, `docs/STATUS.md`, 이 기록을 갱신하고 소진 marker `loop/ESCALATE_SOL` SHA256 `ce2865f49fb3b725e726161179251a4a68c05c017fa2687420dc9b0b495bc43e`을 아래 원문 보존 후 제거한다. Git unborn/uncommitted, `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: source 원본과 lap32 private copy EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 내장 version `V 1.100KR`, PE32가 일치했다. manifest SHA256 `057cf32ae1fe7a32929a4cbd68e5e005dced72258d612b6a3b495cc886664ded`. 새 후보·Wine/Xvfb/game run 없음. lap32의 무수정 원본 기본 2인 임의게임 artifact는 historical captured evidence이며 ready 실패 전에 실제 전투 활성 인원·지도·군대는 미측정이다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `jq`/`sha256sum`으로 lap32 manifest/verdict/inputs/log와 원본/copy를 재확인하고, 보존 800×600 lobby PNG를 시각 대조했다. ready before/after 전체 PNG SHA는 `b69e6b6c...e03a3b`, crop SHA는 `7d2f1f3f...b5832f9`로 각각 동일했다. `objdump -h/-p/-d -Mintel`과 `.text` VMA=file offset raw 추출로 `0x004B7160..0x004B717E`, `0x004B7C0D..0x004B7CA5`, `0x004B7180..0x004B7194`를 확인했다. `make doctor`; targeted runtime tests; `make check`; safety를 실행했다. 게임/`g1-baseline`/새 PNG/patch 생성·적용·원복은 실행하지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): lap32 artifact/hash/cleanup **PASS**. `(134,79)`는 원본 constructor의 첫 ready control anchor `(112,66)` 안이지만, `WORD [0x004ED848]==1`이면 `0x004B7160`이 1을 반환하고 `0x004B7C14: 75 52`가 수동 control poll/toggle `0x004B7C18..50`을 건너뛰어 `0x004B7C68`로 간다. 이 자동 경로는 local index `0x00B63FC4`와 ready DWORD 배열 `0x00632CF0 + player*4`을 사용해 활성 local slot을 ready=1로 만든다. 따라서 lap32 FAIL은 **HARNESS CONTRACT REVISE CONFIRMED**이며 실제 입력 미전달은 입증되지 않았다. old bytes 전문은 주소 문서에 기록했다. `make doctor` top-level `ok=true`/원본 verified; canonical manifest 없음은 새 runtime 금지 범위에서 SKIP. targeted **24 passed**, Fast **94 passed**와 Ruff/compileall/mypy/context PASS, safety `SAFETY_PASS`. PE patch old→new/version reject/copy-only/non-overlap/restore는 후보가 없어 SKIP(N/A).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: exit 0이 아니라 보존 artifact SHA·실제 화면 좌표·고정 원본 raw 분기와 fresh gate를 함께 판정했다. 입력 helper는 정상 종료했으나 ready event가 대상 control까지 전달됐는지는 artifact에 없고, solo 원본은 그 poll 자체를 우회하므로 전달 실패로 주장하지 않는다. PS3·전투·필수 입력5종·실제2배 출력과 G1~G4 제품 판정/사용자 승인은 미완료다. implementation-unchanged-streak=2이므로 다음은 추가 서술이 아닌 측정 가능한 work-tier 코드 수리다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 `tools/runtime_env.py`와 관련 runtime tests만 수정해 local index `0..7`, 해당 ready DWORD 4byte read, confirm 뒤 `mode=1/PS5/ready=1` gate와 evidence를 연결하고 수동 ready click/crop gate를 제거한다. 기존 selector/start/필수입력 계약은 유지한다. targeted/Fast/safety만 실행하며 새 게임 run은 다음 Sol 독립 확인 전 금지한다.

## 소진 전 `loop/ESCALATE_SOL` 원문

```text
# lap32 → Sol/high handoff

- 역할: Codex `gpt-5.6-sol` / high middle 독립 진단·컨펌. 이번 work는 제품 구현이나 재실행을 하지 않는다.
- 필수 런타임 gate가 FAIL했다. 새 run `local/runtime/20260911_033834_765190_0`에서
  `g1-baseline --screen 1600x1200x24 --timeout 90`은
  `player-0 ready setup input effect was not observed`로 중단됐다.
- 보존 근거: `output/g1_a/inputs.jsonl`에서 PS9→PS7, selector `(1,0)→(0,1)`,
  confirm `PS7→PS5`, committed mode `1`은 PASS. ready는 PS5→PS5이나 전체 화면 SHA와
  `player0_ready_control` crop SHA가 before/after 동일하여 FAIL; PS3/전투/필수 후속 입력은
  실행되지 않았다. `output/g1_a/verdict.json`의 `cleanup.ok=true`, `prefix_processes_after=[]`,
  `global_kill_used=false`도 확인됐다.
- 무결성: manifest SHA256 `057cf32ae1fe7a32929a4cbd68e5e005dced72258d612b6a3b495cc886664ded`;
  원본·새 복사본 EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`;
  private win32 prefix/display `:91`; root `1600×1200`, content `800×600`; modules rehash PASS.
- 기계 검증: `make check` 94 passed, Ruff/compileall/mypy/context PASS,
  `bash checks/safety.sh check` → `SAFETY_PASS`. 이는 런타임 G1-A FAIL을 상쇄하지 않는다.
- Sol이 이어서 할 일: 보존 run의 ready 입력 전달·보이는 control 상태·reader/expected transition을
  독립 대조하여 원인이 실제 입력 미전달인지 UI/메모리 관측 계약인지 분류하고, 재실행이 아니라
  최소 진단/수리 범위와 정확한 원본 버전·old bytes·fail-closed/원복 조건을 판정한다.
  근거 충돌이면 추가 실행·패치 없이 다시 승격한다. 새 `g1-baseline` 재실행은 별도 승인 전 금지.
```
