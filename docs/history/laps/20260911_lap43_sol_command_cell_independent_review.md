# 2026-09-11 | lap 43 | 목표 G1-A command-cell 독립 검수

- 실제 provider/model/effort / 지정 역할: 사용자 지정 Codex `gpt-5.6-sol`/high middle.
  현재 세션 표면은 실제 model ID/effort를 별도로 노출하지 않는다. 게임 코드·하네스·원본·후보는
  수정하지 않고 lap42 결과의 독립 진단·확인과 다음 work 범위 판정만 수행한다.
- 가설 / 사용자 관찰: lap42의 최종 Fast 실패는 복사 fixture가 당시 181줄 STATUS를 받은
  bookkeeping 경계 문제이고, 현재 180줄 상태에서는 필수 gate가 복구된다. 동시에 lap42 helper가
  고정 원본의 type58 산술과 분리된 click/hit callback 경계를 코드·직접 회귀·실행 결선에 보존한다.
- 예상 PASS / FAIL 조건: 입력은 고정 원본 SHA, lap42의 세 source/map/test SHA, 현재 STATUS와
  `loop/ESCALATE_SOL`이다. 원본 SHA 및 `0x0066BE88 + 58*0x758 = 0x00686878`,
  `+0x54=0x0049B530` click/action과 `+0x58=0x0049B640` hit 경계, SHA fail-closed 선행,
  selection/unit/type/네 group/strict 단일 hit의 직접 fixture와 production 직전 호출 결선이 모두
  일치하고 `make doctor`, targeted runtime tests, `make check`, 별도 safety가 fresh PASS해야
  CONFIRMED다. 필수 gate 실패나 구현 근거·회귀 계약 충돌이면 재시도 없이 REVISE하고
  `loop/ESCALATE_SOL`에 work-tier handoff를 남긴다.
- 변경 파일 / source fingerprint / 커밋: 구현 파일 변경 없음. 판정 보존용으로
  `docs/STATUS.md`, `docs/work/active/G1_A_EXECUTION_CARD.md`, 이 기록과
  `loop/ESCALATE_SOL`만 갱신했다. 검수한 SHA256은 `tools/runtime_env.py`
  `9e82a19e2888c04701dca40baf22fa5391c13775e7e60b531671829342d84845`,
  `tests/test_runtime_env.py` `cc4ab409af4c6ac23c906cc52414f9072c2c64c96739e15dd8a201f4421b2060`,
  `analysis/memory_maps/player_offsets.md` `b2897bdecbb6e86de76f649073c230334b471ac28a911559347e1f3e164b59e5`.
  최종 STATUS SHA256 `9b04aa609390d332a2c417d07cd6532612c675397fa9aad9e288f22cb249857d`,
  active card `5572d9fba0c9721def1babe5c6bafbca6e351ad8f6e229cd2dd2ac9dbf4775ff`,
  새 handoff `d3d39db67957b8db5ff04cd6b08072c319aa4833f45bede658ca3245edfe4849`.
  Git unborn/uncommitted, `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 기대 원본 SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 binary 없음.
  활성 플레이어/지도/군대 N/A, 가상 read-memory fixture만 검수한다. 게임/runtime run은 금지한다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `wc -l`, `objdump -h`, `objdump -d
  -Mintel`, `xxd`, Python 정수 산술, source/test/map `sed`·`rg`; `make doctor`;
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py`;
  `make check`; `bash checks/safety.sh check`; bookkeeping 뒤 `wc -l`, `sha256sum`,
  `.venv/bin/python checks/context_limits.py`. 새 로그/PNG/game/runtime/patch 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 시작 STATUS 180줄, 원본 SHA 일치.
  type58 주소 `0x00686878`, four DWORD 주소 `+0/+4/+8/+C`, constructor의
  `+0x54=0x0049B530` click/action 및 `+0x58=0x0049B640` hit, SHA mismatch 시 memory read 0회,
  pool slot1~30/group2~5/strict-hit source와 production click 직전 호출 결선은 **CONFIRMED**.
  doctor top-level `ok=true`; targeted **35 passed**; Fast **105 passed**,
  Ruff/compileall/mypy/context PASS; 별도 safety **SAFETY_PASS**. 다만 test fixture의 x는 target
  group이면 600, 나머지는 `100+(group-2)*140`이라 `baseX+N*Δ` 배열이 아니며 이를 assert하지 않는다.
  중복 유효 group cell의 fail-closed 직접 회귀도 없다. 따라서 **SOURCE/MAP/WIRING CONFIRMED;
  TEST CONTRACT REVISE / GAME RUN BLOCKED**다. binary 후보가 없어 patch old/new, unsupported-version
  rejection, copy-only, non-overlap, restore는 SKIP. 실제 runtime cell·worker 의미와 G1-A/G1~G4는 UNKNOWN.
  bookkeeping 뒤 STATUS는 174줄이고 별도 context 검사와 최종 safety도 `CONTEXT_PASS`/
  `SAFETY_PASS`다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap42의 181줄 copy failure는 현재 최종
  상태의 fresh Fast/safety로 복구 확인했지만, exit0은 누락된 직접 회귀를 승인하지 않는다.
  원본/게임/하네스/테스트 구현은 수정하지 않았다. 제품 마일스톤 사용자 승인 없음.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 `tests/test_runtime_env.py`만 최소 수정해
  산술 x 배열과 중복 group cell 거부를 직접 고정하고 targeted/Fast/safety를 실행한 뒤 새 Sol/high
  독립 검수에 넘긴다. 그 전 runtime-read/game run은 금지한다.

## 교체 전 `loop/ESCALATE_SOL` 원문

SHA256 `d416d8caebd12a8fcf4f78c146ca9fbf300e67969a9246fe231e0fde6b5883d8`.

```text
# lap42 Luna work -> Sol/high recovery and independent review

reason=Final post-bookkeeping make check unexpectedly failed in subprocess loop fixtures because copied docs/STATUS.md had 181 lines and startup safety stopped every affected loop test.
role_requested=Fresh Codex gpt-5.6-sol/high middle. Do not treat the pre-bookkeeping PASS as final gate approval.
classification=REQUIRED_FAST_UNEXPECTED_FAIL_STATUS_COPY_PROVENANCE_REVIEW
stop=Preserve current implementation, tests, memory map, lap42 history, and this escalation. Do not retry this lap, do not run standalone safety after the failed make check, do not run g1-baseline/game/patch/old-new/restore, and do not commit or push.

evidence=
- Before final documentation bookkeeping: targeted runtime/guard tests 35 passed; make check 105 passed; Ruff/compileall/mypy/context PASS; bash checks/safety.sh check SAFETY_PASS.
- After bookkeeping: make check collected 105, with 92 passed and 13 failed. All 13 failures stopped before their intended assertions with `docs/STATUS.md: 181 lines exceeds 180; archive with provenance` in copied temporary projects. No implementation test failure was observed in tests/test_runtime_env.py or tests/test_runtime_guards.py during that run.
- The working-tree STATUS was then reduced to 180 lines without rerunning any gate. Its current SHA256 is `3c7b0a0febede0e66782f2349817eee88e27431df0345bdf085e2cde5435d3f3`. Sol must independently verify why the fixture observed 181 and run the required gate from this final state exactly as appropriate.
- Original read-only EXE SHA256 remains `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- Current changed-source SHA256: `tools/runtime_env.py`=`9e82a19e2888c04701dca40baf22fa5391c13775e7e60b531671829342d84845`; `tests/test_runtime_env.py`=`cc4ab409af4c6ac23c906cc52414f9072c2c64c96739e15dd8a201f4421b2060`; `analysis/memory_maps/player_offsets.md`=`b2897bdecbb6e86de76f649073c230334b471ac28a911559347e1f3e164b59e5`.

required_review=
1. Preserve the current source/test/map changes and this evidence; inspect the STATUS copy/safety boundary and the final STATUS line count.
2. Independently verify the fixed original SHA, type58 arithmetic `0x0066BE88 + 58*0x758 = 0x00686878`, separate `+0x54`/`+0x58` callback mapping, and direct runtime fixture coverage.
3. Run the required Fast and safety gates only from the corrected final state; if either fails, preserve output and keep the escalation active.
4. Only after independent confirmation decide whether one new runtime-read fixture is allowed. Game execution, coordinate changes, binary patches, and product G1 approval remain blocked.
```
