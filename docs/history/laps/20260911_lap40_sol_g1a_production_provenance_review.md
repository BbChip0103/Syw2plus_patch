# 2026-09-11 | lap 40 | 목표 G1-A

- 실제 provider/model/effort / 지정 역할: 호출 지정은 Codex `gpt-5.6-sol`/high middle;
  현재 세션이 노출하는 정확한 model ID/effort는 미확인. 게임 코드·하네스·EXE/DLL/assets는
  수정하지 않았고 새 게임을 실행하지 않았다.
- 가설 / 사용자 관찰: lap39의 PS3 command-cell 생성→hit-test→callback→action chain과
  runtime-only 경계가 동일 SHA 원본에서 독립 재추출해도 일치하는지 확인한다.
- 예상 PASS / FAIL 조건: 지정 5개 함수의 raw bytes, `type*0x758`, cell
  `baseX+N*Δ`, callback field, flag→action이 일치하면 static confirmation PASS. 주소 산술/호출
  의미가 충돌하거나 runtime-only cell/worker 의미를 정적으로 결정할 수 없으면 REVISE/승격한다.
- 변경 파일 / source fingerprint / 커밋: 구현 변경 없음. 판정/계약으로
  `docs/STATUS.md`, `docs/work/active/G1_A_EXECUTION_CARD.md`, 이 기록,
  `loop/ESCALATE_SOL`만 갱신. 검수 전 player map SHA256
  `b5e745c1a2823e89c0e3a50a4bf0fbfec0969635c37bb97135f96de6aebb4e33`, lap39 기록 SHA256
  `71da6271f31a2b88f1047347e436fc0c80f233b0e1aa05acf29061dc05d8baeb`; Git unborn/uncommitted,
  `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용
  `Syw2plus/syw2plus_original.exe` SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보/patch/run/runtime
  fixture/active-player/map/army는 N/A. lap36 artifact는 과거 실패 근거로만 보존했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `objdump -h`, `objdump -d -Mintel
  --start-address/--stop-address`, `xxd`로 PE section과
  `0x0041F630/0x0041FA60/0x0041FBC0/0x0049B530/0x0049B640/0x0049B6D0/0x004AE550`를
  재추출. 초기 shell 산술식 1회는 괄호 오기로 exit2였고 파일 변경 없이 수정 명령으로
  재계산했다. 편집 전 `make check`/safety는 PASS. 편집 후 `make check &&
  bash checks/safety.sh check`는 STATUS 181>180 safety 위반으로 예상 밖 FAIL했고 후속 safety는
  실행되지 않았다. 지시대로 재시도하지 않았으며 새 캡처/게임/패치 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 원본 SHA, `.text/.data` file-backed 경계,
  four-cell group `2..5`, x=`baseX+N*Δ`, `0x0041FA60` strict rectangle,
  `0x0049B530`의 `0x40000→0x19A`, `0x200→0x19C`, `0x80000→0x19E`,
  `0x100000→0x1A1`, `0x004AE550` 두 번째 action WORD 경계는 PASS. 그러나
  `0x0066BE88 + 58*0x758 = 0x00686878`로 lap39의 `0x006868B8`과 `0x40` 충돌하며,
  `0x0041FBC0`은 `0x0041FC38` hit/hover `+0x58=0x0049B640`과 `0x0041FC6F`
  click/action `+0x54=0x0049B530`을 별도 호출한다. **STATIC CHAIN REVISE /
  GAME RUN BLOCKED**. `(670,490)` membership·worker 의미는 UNKNOWN. 편집 전 Fast
  **99 passed**, Ruff/compileall/mypy/context/safety PASS였으나 편집 후 필수 Fast는
  **86 passed/13 failed**; 모두 STATUS 181>180 startup safety 차단의 파생 실패다.
  후속 safety와 patch old/new/restore는 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 정적 충돌에 이어 편집 후
  필수 Fast도 예상 밖 FAIL했으므로 **ESCALATE/STOP**. 현재 변경을 보존하고
  `loop/ESCALATE_SOL`을 안전 복구 우선으로 갱신했다. implementation-unchanged-streak=2의
  후속 측정 가능 work 계약은 gate 복구 후에만 유효하다. G1-A/G1~G4와 사용자 승인은 미완료.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high middle이 현재 변경/handoff를 보존하고
  STATUS의 과거 중복만 이 이력 provenance로 옮겨 180줄 이하로 축소한 뒤 Fast/safety를
  독립 1회 검증한다. PASS 후에만 lap40 read-only helper 계약을 Luna/high work에 반환한다.

## 교체 전 `loop/ESCALATE_SOL` 원문

```text
# lap38 middle -> work static provenance handoff
reason=g1a_lap36_production_coordinate_and_failure_evidence_contract_unproven
role_requested=Fresh Codex gpt-5.6-luna/high work read-only provenance probe, followed by fresh Codex gpt-5.6-sol/high independent confirmation.
classification=HARNESS_CONTRACT_REVISE_GAME_RUN_BLOCKED
stop=No g1-baseline or other game run; no coordinate change; no runtime/tests/game/EXE/DLL/assets modification; no patch, commit, or push. Preserve lap36 artifacts. After this one static probe, require a new Sol/high confirmation before any repair or rerun.

--- lap39 Luna work handoff ---
reason=static command-cell chain is proven but worker semantics and target-coordinate membership remain runtime-only
role_requested=Fresh Codex gpt-5.6-sol/high independent reviewer
evidence=Original SHA256 b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac. Static raw-byte chain recorded in analysis/memory_maps/player_offsets.md: 0x0049B6D0 creates four cells; 0x0041F630 writes geometry; 0x0041FA60 tests input WORD 0x004ED814/816 against object +8/+C/+10/+14; 0x0041FBC0 invokes object +0x58; 0x0049B530 maps 0x40000->0x19A, 0x200->0x19C, 0x80000->0x19E, 0x100000->0x1A1; 0x004AE550 receives the action record. Fast 99 passed, Ruff/compileall/mypy/context PASS, safety SAFETY_PASS. Runtime globals 0x009E2BAC/0x009E2BB0/0x009E2BB4/0x009E2BB8, size table 0x0051EE94/98, and type58 record 0x0066BE88+58*0x758 are not file-backed; no raw proof identifies (670,490) membership or which action is worker production.
classification=STATIC_CHAIN_PASS_WORKER_CELL_UNKNOWN_GAME_RUN_BLOCKED
stop=Do not infer from icon/PNG; do not modify tools/tests/game/EXE/DLL/assets; do not run g1-baseline. Sol must independently verify the raw bytes and decide whether an explicitly approved runtime-read fixture can resolve the boundary. User milestone approval remains absent.
```
