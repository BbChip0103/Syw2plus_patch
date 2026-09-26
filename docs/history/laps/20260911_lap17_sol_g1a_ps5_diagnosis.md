# 2026-09-11 | lap 17 | G1-A PS5 endpoint middle 독립 진단

- 실제 provider/model/effort / 지정 역할: Codex; 런타임이 정확한 모델 ID/effort를 노출하지 않아
  `gpt-5.6-sol/high` 실제값은 미확인 / 사용자 지정 middle 진단·계획·확인 역할만 수행.
- 가설 / 사용자 관찰: lap16의 안정 PS5는 원본 UI 정체가 아니라 정상 로비 endpoint이며,
  `lobby_mode=1→1`을 선택 성공으로 허용한 것과 PS7 복귀를 기다린 것이 결합된 하네스 결함이다.
- 예상 PASS / FAIL 조건: 보존된 동일 run의 SHA·격리·화면·PS/selector와 원본 정적 전이가 일치하고
  원인을 harness/original/both 중 하나로 분류하며 재실행 없는 최소 work repair를 고정하면 middle PASS.
  증거 충돌이나 필수 gate 실패면 FAIL/UNKNOWN으로 보존하고 재시도 없이 `ESCALATE_SOL` 유지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 문서만
  `analysis/memory_maps/player_offsets.md`, `docs/work/active/G1_A_EXECUTION_CARD.md`,
  `docs/STATUS.md`, 이 기록을 갱신하고 소진된 `loop/ESCALATE_SOL`을 아래 원문 보존 후 제거한다.
  게임 코드/EXE/DLL/asset 및 `tools/runtime_env.py`/tests 변경 없음; uncommitted/unborn HEAD.
  시작 SHA: runtime_env `7aa1859ccf2c0173c6740f154262c83200c5786c6296edf6a59a5b5d978d71c8`,
  test_runtime_env `a5143fa1d011fc1d9899ad5537ac6d2eec1b08b7fbbc30241a94b930d4f7794f`,
  lap16 `cd2e45a2ace150343bd3c2d8866c3668eb983b9a8c1191628b3478a160874c48`,
  제거 전 marker `afb13fb7c7d9210eaa611a0e67d8a6103e9ddc7c4168dfb874a8553e91e79498`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본·private copy·mapped EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 패치 후보 없음.
  lap16의 Wine win32/private Xvfb `:91`/1600×1200×24/무수정 기본2인 fixture를 과거 실패 증거로만
  검수했다. PS5 마지막 상태는 players0~7 nation=0, units=[]로 전투/활성 플레이 증거가 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`으로 manifest
  `9b6b94bc9cdbec79c781b1f4777790ee02a03efe395d6b753e2d4ad9ff13c416`, verdict
  `4c5ba201918301bb014fa43f8f38f2df05a706561f9fa2bfe921ecd5192d02c5`, inputs
  `d39839b9fa521a840a7010471e1f60c9eee6e6f8d4aaa82944d221711f363ce3` 일치 확인.
  세 PNG의 실제 SHA도 JSON과 일치. `objdump -d -Mintel`로 원본 `0x424b50..0x424c10` 및
  `0x004ED818/0x004ED848` 참조를 검사했다. Pillow read-only diff는 selector 전후 2,981 pixels,
  bbox `(184,152)..(511,579)`로 이전/현재 커서와 button hover 영역을 함께 포함했다.
  `make doctor` → setup/original/tools PASS(기본 optional runtime manifest 없음은 비필수),
  `make check` → 84 PASS, Ruff/compileall/mypy8/context PASS; `checks/safety.sh check` → `SAFETY_PASS`;
  `runtime_env.py check --manifest local/runtime/20260911_012103_3997655_0/manifest.json` → ok.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): root1600×1200/content800×600, mapped EXE와 ddraw,
  PS9→PS7, cleanup 및 보존 SHA는 **PASS**. selector는 클릭 전후 `1→1`이라 입력 효과 **FAIL**;
  PNG 변화도 커서/hover와 분리되지 않아 선택 표시 증거 **UNKNOWN**. 원본 bytes
  `0x424b55: 66 c7 05 18 d8 4e 00 05 00`은 PS4 handler가 WORD PS5를 쓰고 다음 PS5 handler가
  로비를 처리함을 보여 하네스 PS7 endpoint는 **FAIL / HARNESS DEFECT CONFIRMED**.
  원본 UI/fixture 정체는 **NOT DEMONSTRATED**. 패치 후보가 없어 old/new bytes·버전 거부·중첩·원복은
  **SKIP(N/A)**이고, copy-only 원본/실행 SHA 동일성은 PASS다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: G1-A/G1 제품 판정과 사용자 승인은 없음.
  실제 PS5 화면은 lap16이 timeout 전에 캡처하지 않아 다음 새 run에서 확인해야 한다. selector WORD 의미는
  정적 0/1 write와 기존 주소표에 부합하지만, 실제 UI 효과는 조건부 `1→0` 후 필수 `0→1`로 검증한다.
  이번 문서-only lap으로 implementation-unchanged-streak는 2가 되므로 다음 lap을 측정 가능한
  하네스 코드·회귀 수정으로 고정했으며 추가 서술/대기 lap으로 넘기지 않는다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high가 `tools/runtime_env.py`와 관련 runtime tests만 수정해
  selector 2byte read, 초기1일 때 `(344,169)` 1→0 정규화, `(462,169)` 필수0→1, 중립 cursor capture,
  confirm/ready PS5 endpoint를 구현한다. targeted Fast·`make check`·safety만 실행하고 게임은 재실행하지
  않으며, 새 middle 독립 확인 뒤에만 G1-A 새 run 1회를 허용한다.

## 소진 전 `loop/ESCALATE_SOL` 원문

```text
lap=16
reason=g1a_original_run_failed_at_local_lobby_ps5_and_solo_initial_mode_contract_is_unclear
role_requested=Fresh Codex gpt-5.6-sol/high middle independent diagnosis; do not retry the game or claim G1-A completion
required=Review the preserved run local/runtime/20260911_012103_3997655_0 and determine whether the PS7->PS5 stall is an original UI/fixture transition failure, harness input/observation defect, or both. Independently reconcile the card's expected lobby_mode 0 before the solo click with the observed lobby_mode 1 before that click. Verify the recorded root/content geometry, original EXE and mapped EXE hashes, PS9->PS7 menu effect, PS5 last state, and cleanup. Decide the minimum reversible probe or implementation repair needed before any further G1-A run; preserve the one-run limit and do not weaken expectations.
evidence=targeted `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py` -> 14 passed; `make check` -> 84 passed, Ruff/compileall/mypy/CONTEXT_PASS. New manifest `local/runtime/20260911_012103_3997655_0/manifest.json` SHA256 9b6b94bc9cdbec79c781b1f4777790ee02a03efe395d6b753e2d4ad9ff13c416; source/copy/mapped EXE SHA256 b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac. `g1-baseline` exit2 with error `local random-game lobby did not return to PS=7`, last state ps=5,tick=0, no units/nations. `output/g1_a/verdict.json` SHA256 4c5ba201918301bb014fa43f8f38f2df05a706561f9fa2bfe921ecd5192d02c5; `inputs.jsonl` SHA256 d39839b9fa521a840a7010471e1f60c9eee6e6f8d4aaa82944d221711f363ce3; log SHA256 76e7fc2ca6c05aa3921e50b0a6e0ffffc12250719924095209584b23e6fdb0fa. Solo input records lobby_mode 1 before and after; menu is PS9->PS7 PASS. Cleanup is true, prefix_processes_after=[], global_kill_used=false. PNGs are in shared temp and referenced by inputs.jsonl.
preserve=Do not delete or overwrite the run, its output/g1_a artifacts, or referenced PNGs. Do not modify original/reference repositories, EXE/DLL/assets, or rerun g1-baseline in this lap. Current harness hashes: tools/runtime_env.py 7aa1859ccf2c0173c6740f154262c83200c5786c6296edf6a59a5b5d978d71c8 and tests/test_runtime_env.py a5143fa1d011fc1d9899ad5537ac6d2eec1b08b7fbbc30241a94b930d4f7794f.
```
