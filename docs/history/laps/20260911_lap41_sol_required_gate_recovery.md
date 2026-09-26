# 2026-09-11 | lap 41 | 목표 G1-A 필수 gate 복구

- 실제 provider/model/effort / 지정 역할: 호출 지정은 Codex `gpt-5.6-sol`/high middle;
  현재 세션이 노출하는 정확한 model ID/effort는 미확인. 게임 코드·하네스·EXE/DLL/assets는
  수정하지 않고 문서 safety gate만 독립 복구·확인한다.
- 가설 / 사용자 관찰: lap40 편집 뒤 필수 Fast 실패는 `docs/STATUS.md`가 181줄이 된 단일
  startup safety 위반과 그 파생 실패이며, 과거 중복을 provenance 이력에 보존해 180줄 이하로
  유지하면 다른 변경 없이 필수 gate가 복구된다.
- 예상 PASS / FAIL 조건: 입력은 lap40 이력, `loop/ESCALATE_SOL`, 현재 STATUS다. STATUS가
  180줄 이하이고 `make check`와 `bash checks/safety.sh check`를 각각 정확히 1회 실행해 모두
  PASS하면 gate 복구 CONFIRMED. 어느 하나라도 FAIL하면 재시도하지 않고 현재 변경과 출력을
  보존해 `loop/ESCALATE_SOL`을 갱신한다.
- 변경 파일 / source fingerprint / 커밋: `docs/STATUS.md`, 이 기록을 갱신하고 소진된
  `loop/ESCALATE_SOL`을 원문 보존 뒤 제거했다. 검수 전 SHA256은 STATUS
  `1ddc3779ef41096703b14a0409e8ae24a7f24ea70d558ddbf3b4b44a1af7c65b`, lap40 이력
  `5a427d7cfcdf10645e9d47ab55dd02310fbb0381e7b291662ebedf9d46b47f67`, 승격문
  `3aefc9446371e73179f2a228940d3707eab4e4bb8ab680edf3d60d8b997ae87e`; Git unborn/uncommitted,
  `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본
  `../Syw2plus/syw2plus_original.exe` SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보/run/runtime
  fixture/active-player/map/army는 N/A. lap40 고정 원본과 과거 run을 새 성공 근거로 승격하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `wc -l`, `sha256sum`, `rg`, `objdump -d -Mintel
  --start-address=0x0041fc20 --stop-address=0x0041fc80`, type58 산술, `make check`,
  `bash checks/safety.sh check`. 새 로그/캡처/게임/패치 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 시작 STATUS 178줄. 원본 SHA 일치,
  `0x0066BE88 + 58*0x758 = 0x00686878`; disassembly에서 `0x0041FC38`은 `[esi-0xc8]`
  (`object+0x58`), `0x0041FC6F`은 `[esi-0xcc]` (`object+0x54`) 호출을 독립 확인했다.
  `make check`는 **99 passed**, Ruff/compileall/mypy/context PASS; 별도 safety는
  **SAFETY_PASS**. **REQUIRED GATE RECOVERY CONFIRMED**. game/patch old-new/version reject/
  copy-only/non-overlap/restore는 후보·실행이 없어 SKIP했다. 최종 bookkeeping 뒤 STATUS는
  177줄/SHA256 `ee083a288473b7f9f4fca41e63e5d3ab4a1ca3ecc4beebaa4878a45a6d045f4d`이고,
  단독 context 검사는 `CONTEXT_PASS`였다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: gate만 복구했다. player map의 잘못된
  type58 base와 합쳐진 callback 서술, runtime helper/test는 아직 미수리다. runtime cell/worker
  의미, `(670,490)` membership, G1-A/G1~G4와 사용자 승인은 미완료다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 active G1-A card의 lap40 계약대로
  player map, SHA fail-closed read-only helper, 직접 회귀만 최소 수리한다. 게임 실행과 원본/좌표/
  click 순서/timeout 변경은 금지하고, 이후 새 Sol/high 독립 검수를 받는다.

## 소진한 `loop/ESCALATE_SOL` 원문

```text
# lap40 middle -> Sol/high required-gate recovery escalation

reason=Post-documentation required make check unexpectedly failed because docs/STATUS.md reached 181 lines and violated the 180-line startup safety gate; 86 passed and 13 loop tests failed as derivatives. Static review also found the lap39 type58 base and callback-boundary conflicts.
role_requested=Fresh Codex gpt-5.6-sol/high middle recovery; only after the gate is independently restored may the planned Codex gpt-5.6-luna/high work proceed.
required=Preserve the lap40 files and this handoff. Move only duplicated historical STATUS detail into docs/history/laps/20260911_lap40_sol_g1a_production_provenance_review.md with provenance so STATUS is at most 180 lines; do not alter the current static verdict or the pending lap40 read-only helper contract. Run make check and bash checks/safety.sh check exactly once. If both pass, set STATUS next one back to the Luna/high static-ledger/read-only-helper repair contract already recorded in the active card. If either fails, do not retry; preserve output and refresh this escalation.
evidence=Before documentation edits, make check had 99 passed and Ruff/compileall/mypy/context PASS; safety was SAFETY_PASS. After edits, make check failed with 86 passed/13 failed because every affected loop test stopped at `docs/STATUS.md: 181 lines exceeds 180; archive with provenance`; the chained standalone safety command was not reached. Original SHA256 remains b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac. Static evidence: type58 base is 0x00686878, not 0x006868B8; 0x0041FC38 calls +0x58=0x0049B640 while gated 0x0041FC6F calls +0x54=0x0049B530.
classification=REQUIRED_FAST_UNEXPECTED_FAIL_STATIC_CHAIN_REVISE_GAME_RUN_BLOCKED
stop=Do not retry in lap40. No work implementation, g1-baseline/game run, coordinate/click-flow/timeout/game/EXE/DLL/assets change, patch, commit, or push. Runtime cell/worker meaning, G1/G1-A, and user milestone approval remain incomplete.
```
