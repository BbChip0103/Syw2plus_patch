# 2026-09-11 | lap 38 | G1-A production FAIL middle 독립 진단

- 날짜/lap/목표: 2026-09-11 KST / lap38 / 보존된 lap36 G1-A production 입력 실패의 원인 범위 판정
- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-sol`/high middle 지정. 현재 호출의 실제 model ID/effort는 노출되지 않아 미확인. 게임 코드·하네스·EXE/DLL/assets 수정 및 새 게임 실행 금지.
- 가설 / 사용자 관찰: lap36의 `(670,490)` 클릭이 원본 생산을 거부한 것이 아니라, 고정 좌표가 선택된 HQ의 실제 생산 command cell이라는 근거와 실패 증거 보존이 하네스에 없어서 효과를 관측하지 못했다.
- 예상 PASS / FAIL 조건: 같은-run manifest/입력/장면/화면/모듈/cleanup과 selection/production reader 결선을 재확인하고, 원본 문제와 harness/scene 계약 문제를 근거 범위 안에서 분류해 다음 검증 가능한 probe 하나를 고정하면 middle PASS. 좌표 의미가 직접 확인되지 않거나 필수 Fast가 실패하면 게임 실행을 막고 구체 research blocker와 `loop/ESCALATE_SOL`을 보존한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현·게임 변경 없음. 진단 문서로 `docs/STATUS.md`, 활성 카드, 이 기록, `loop/ESCALATE_SOL`만 갱신. 검수 source SHA256은 `tools/runtime_env.py` `8de1b9f449d9c28fc3e996c9d393013f5c36c06f8ddf6634f1152678a9964bc3`, `tests/test_runtime_env.py` `1bde26444fe62aebb06c0e6f5d0832740c9f543597ebaacdcd21af76cd696621`, `tests/test_runtime_guards.py` `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`; 교체 전 marker SHA256 `ab2b4e85a785b1872acbb0b23f130de77953d30a766bda2a1921fba442886f62`. Git unborn/uncommitted, `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: source 원본과 lap36 private copy EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; manifest SHA256 `dd54515436fe637bc634d8970d40c7d5b8f341c9c8575bc1597005bd013fab13`. lap36 private win32 prefix/display `:91`, root1600×1200/content800×600, 무수정 기본2인 임의게임, owner0/1 nation2/3 active units2/2, synthetic/resource/control fixture 없음. 새 후보/run 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`/`jq`/`sed`/`rg`로 lap36 manifest, `inputs.jsonl`, `scene.json`, `surface.json`, `window.json`, `provenance.json`, `modules.json`, verdict/log, source/tests와 원본/copy를 재확인했다. 보존 selection before/after 및 production-before PNG를 원본 크기로 직접 대조했다. `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py`; `make check`; `bash checks/safety.sh check`를 실행했다. 게임/patch 생성·적용·원복은 실행하지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): artifact/hash/cleanup **PASS**. `inputs.jsonl`은 같은 PID972882 run에서 selection count `0→1`, first slot1199를 기록하고 final detailed state는 slot1199 type58/owner0를 보여 HQ 선택을 지지한다. player0은 tick2746까지 rice5000/reserved0/count2/used20으로 불변인 반면 owner1은 생산·자원이 진행되어 state reader가 live였음은 확인된다. 그러나 source는 production-before 뒤 `(670,490)`을 무조건 클릭하고, 카드가 요구한 active production icon 의미를 검증하지 않는다. 테스트 29개 중 production 좌표/flow를 실행하는 회귀가 없으며 `_wait_state` 예외가 `input_click`/after capture보다 먼저라 `inputs.jsonl`에는 production 행 자체가 없다. 보존 PNG에는 선택된 HQ와 여러 command cell이 보이지만 각 cell 의미는 정적 provenance 없이 확정할 수 없다. 따라서 **HARNESS CONTRACT REVISE / GAME RUN BLOCKED**; 실제 click delivery와 원본 생산 결함은 UNKNOWN. targeted **29 passed**, Fast **99 passed**, Ruff/compileall/mypy/context PASS, safety `SAFETY_PASS`. 이는 runtime FAIL을 상쇄하지 않는다. PE patch old→new/version reject/copy-only/non-overlap/restore는 후보가 없어 SKIP(N/A).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: exit2는 실패 보존 근거일 뿐 원인 판정이 아니다. G1-A/G1~G4와 사용자 승인 변화 없음. production cell 의미가 불명확하므로 좌표 추정 수정이나 재실행을 금지한다. implementation-unchanged-streak가 2가 되어 다음은 서술 추가가 아닌 주소·raw-byte 기반의 측정 가능한 work probe로 고정했다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 고정 원본을 읽기 전용으로 두고 selected type58 HQ의 PS3 command-panel hit-test→cell/action table→callback을 추적해 `(670,490)`의 실제 동작과 worker 생산 cell을 VA/raw bytes로 기록한다. runtime/tests/game 수정과 새 run은 금지하고, 결과는 새 Sol/high가 독립 확인한다.

## 교체 전 `loop/ESCALATE_SOL` 원문

```text
# lap36 work -> Sol/high middle escalation

## Blocker

The single authorized G1-A run failed at the fixed production input. `g1-baseline` exited 2 with:
`fixed HQ production icon produced no observable state effect`.
Do not retry, change coordinates, loosen the effect reader, or patch the game in this escalation.

## Run and evidence

- Run: `local/runtime/20260911_040529_959579_0`
- Manifest SHA256: `dd54515436fe637bc634d8970d40c7d5b8f341c9c8575bc1597005bd013fab13`
- Original and isolated EXE SHA256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- Command: `.venv/bin/python tools/runtime_env.py g1-baseline --manifest local/runtime/20260911_040529_959579_0/manifest.json --screen 1600x1200x24 --timeout 90`
- Verdict: `local/runtime/20260911_040529_959579_0/output/g1_a/verdict.json`, SHA256 `a94b4d7eb3dd052e4f8b11cfa4655a36a7733be92030039cb657f4dc305a3987`, overall `FAIL`.

## What passed / failed

`prepare`/`check`, original hash, private 1600×1200 root, 800×600 content crop, PS9/PS3 surface, modules, menu, solo selector, confirm, auto-ready local=0 ready=1, PS5→PS3 tick=6, unit select, same-run scene, and cleanup passed. Initial multiplayer normalization was an allowed SKIP. The fixed production click at content `(670,490)` produced no observable production/progress/reserved/count effect; `required_inputs=false`. Drag selection and minimap were not attempted after the first required-input failure.

## Sol must independently verify

1. Read the preserved `inputs.jsonl`, `scene.json`, `surface.json`, `window.json`, `provenance.json`, `modules.json`, log, and PNGs; confirm the production before/after and selection state are from this run and not synthetic.
2. Trace the fixed HQ/production coordinate `(670,490)` against the actual selected owner-0 HQ and production reader. Decide whether this is a harness/scene contract defect or a genuine original-input/product blocker; do not infer from exit status alone.
3. Confirm cleanup and the original/copy SHA. Define exactly one minimal reversible, version-rejected probe if justified, or leave the run blocked. A new runtime run requires an explicit updated STATUS/contract after Sol's diagnosis.

Fast evidence before run: targeted runtime/guards 29 passed; `make check` 99 passed; Ruff, compileall, mypy, context and `bash checks/safety.sh check` passed. No code, binary, asset, commit, or push was made this lap.
```
