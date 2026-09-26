# 2026-09-11 | lap 63 | 목표 G1-A primary snapshot 단일 선택 재검수

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier Codex `gpt-5.6-sol` / high / diagnosis·plan·confirmation. 현재 세션 표면은 실제 model ID/effort를 별도 노출하지 않아 실행 증거로 주장하지 않는다.
- 가설 / 사용자 관찰: lap62의 fill→predicate/branch→consume 순서, phase당 single-read 96-byte 범위와 stable-ineligible fail-closed가 충분하면 work handoff를 승인한다. 원본 dispatch나 selection coherence에 빠진 전제가 있으면 구현 없이 REVISE하고 `loop/ESCALATE_SOL`로 넘긴다.
- 예상 PASS / FAIL 조건: 고정 원본 SHA와 보존 artifact/source SHA가 일치하고 `0x498EE0` reset, `0x4A3B5B` writer, `0x499201..0x49929E` fill, `0x4992BE` branch, `0x499583` consume 및 selection-count dispatch를 독립 확인한다. stable-ineligible가 click 전에 중단되고 stable 다중 선택을 현재 primary provenance로 허용하지 않아야 한다. 필수 doctor/Fast/safety 실패도 즉시 승격 조건이다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임 코드/helper/tests/binary 변경 없음. 진단·계획 문서 `analysis/memory_maps/player_offsets.md`, `docs/work/active/G1_A_EXECUTION_CARD.md`, `docs/STATUS.md`, 본 이력과 `loop/ESCALATE_SOL`만 갱신했다. 최종 SHA는 map `4abd10c2882f325b3acb09a13da38f2d9a26b9ba942721db05f61a539f4b8ab7`, card `d20194c6b75dc524765b42b856123b0f1156b3c1e5e6f4791286197a4661f7d7`, STATUS `527c1125ac526a615d69fe683e4679464b4ddabb4b46cccbc097348b6fe9811d`, marker `19a872e96b56e12809cf62446cdc79f842074e4251d29412e38fca1f250d3922`다. 수리 전 source SHA는 `tools/runtime_env.py=e605e041816856bc88458df8bfad85e2e77cdac40f4ba6cab1e6e7d4e3d32dd5`, `tests/test_runtime_env.py=58ea272f06d78f1edc672d4f569d7a7e3bd6ea0d644f3b68d6a6bd06931e024c`, `tests/test_runtime_guards.py=93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`. Git unborn, `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본 SHA는 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 EXE 없음. 새 Wine/Xvfb/game run 없음. lap60 보존 run `local/runtime/20260911_065344_2240721_0`, 기본 2인 random, owner0/1 active units 각2, synthetic/memory write/control/resource grant=false는 historical FAIL artifact로만 SHA 대조했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sed`/`rg`/`sha256sum`으로 지시·STATUS·lap61~62·map/card·source/tests·artifact를 대조했다. `objdump -d -Mintel`로 고정 PE32 원본 `0x498EE0..0x4995B0`, `0x4A3B00..0x4A3B92`를 재추출했다. `make doctor` top `ok=true`(기본 runtime manifest optional false), `make check` **116 passed**, Ruff/compileall/mypy/context PASS, 명시 manifest `make doctor-runtime ...` `ok=true`, `bash checks/safety.sh check` `SAFETY_PASS`. 새 캡처/실행은 N/A/SKIP이다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 원본/source와 lap60 manifest `be3023c43ebec7a76ec7bb09a99f0c9fd5c9cb27c93ab6af64d38d7836e1d5fe`, baseline `24c9656326482a5a21b294729c7ff840653c116693286f04c28b70ed761ac737`, verdict `8ae22317aaf77b161c36341bd0e0dd85363c23d507e54c17a4946d9e986e6825`, provenance `bbdafe049307a3f8d4fcd7b57aa9126e68eac006e46f3471d9538db141b82e7d`가 일치했다. lap62 분기 순서와 `0x008930A6..0x00893105`=96 bytes는 **CONFIRMED**다. 그러나 `0x498FBA` count dispatch상 `count==1`만 primary fill로 들어가며 lap62는 stable count>1을 거부하지 않으므로 handoff는 **FAIL/REVISE / GAME RUN BLOCKED**다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 Fast는 PASS지만 stable count2 primary 무-read 회귀가 없어 새 공백을 검출하지 못한다. binary patch가 없어 expected new bytes, unsupported-version rejection, copy-only/non-overlap/byte-exact restore는 N/A/SKIP이고 원본 쓰기는 없었다. writer old bytes `66 8b 54 24 08 0f bf c0 66 89 94 41 96 0c 00 00`은 일치한다. primary field/action·worker target, G1 실제 2배 출력/입력/생산/drag/minimap, G2~G4와 사용자 승인은 UNKNOWN/미완료다. implementation-unchanged-streak=2라 반복 run 대신 exact-single-selection blocker와 직접 회귀를 고정했다. `patch-validation` 지침에 따라 historical capture를 fresh runtime으로 승격하지 않았다.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high 또는 Claude Code `claude-opus-5`/high가 카드 lap63의 count1 전제, stable count2 primary 무-read 거부, `1→2` 전이 evidence 및 lap62의 나머지 96-byte/fail-closed 범위를 독립 확인한다. 승인 전 helper/tests와 game/binary/좌표/timeout/fixture를 변경하지 않으며, 승인 뒤에만 Luna/Sonnet5가 source/tests를 구현한다.

## 교체 전 `loop/ESCALATE_SOL` 원문

교체 전 SHA256: `dee2485bd70d4910826737c29348073e91af219010d006747d1fe514a11efc1e`.

```text
# lap62 승격 요청 — primary consume 순서 및 fail-closed handoff 재검수 필요

## 사유

lap61의 네 primary 배열과 fill-before-predicate는 확인됐지만, “primary table이 predicate보다 먼저
구성·소비된다”는 기록은 원본 제어흐름과 충돌한다. fill은 `0x4992BE` 전이지만 consumer
`0x499583`은 참 `0x4992DF→0x49B6D0`과 거짓/alternate 분기가 합류한 뒤다. 또한 lap61 계약은
stable-ineligible에서 primary evidence를 붙인 뒤 예외로 중단할지 성공 반환할지 고정하지 않아,
UNKNOWN인 field/action으로 hard-coded production click을 열 수 있다. 구현 없이 REVISE로 보존한다.

## 이어서 검증할 것

1. 고정 원본 SHA에서 `0x499201..0x49929E` fill → `0x4992BE` predicate → true/false branch →
   공통 `0x499583` consume 순서를 독립 재확인하고 lap61의 consume-before-predicate 표현을 반려한다.
2. 카드 lap62처럼 primary `0x8930A6..0x893105`를 phase당 한 번의 contiguous 96-byte read로 읽고
   물리 주소 `A6/BE/D6/EE`를 각각 12 WORD로 분리하는 범위가 충분한지 판정한다.
3. stable-ineligible도 primary before/after를 예외/diagnostics에 보존한 뒤 기존처럼 production click
   전에 fail-closed하고, 성공 반환/field 의미/worker action을 추가하지 않는 계약을 확인한다.
   승인 뒤에만 Luna/Sonnet5가 helper/tests를 수정한다. 새 game run과 좌표/timeout/binary 변경은 금지다.

## 보존된 근거

- run: `local/runtime/20260911_065344_2240721_0/`
- manifest SHA: `be3023c43ebec7a76ec7bb09a99f0c9fd5c9cb27c93ab6af64d38d7836e1d5fe`
- `output/g1_baseline.json` SHA: `24c9656326482a5a21b294729c7ff840653c116693286f04c28b70ed761ac737`
- `output/g1_a/verdict.json` SHA: `8ae22317aaf77b161c36341bd0e0dd85363c23d507e54c17a4946d9e986e6825`
- private/original EXE SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- source SHA: `tools/runtime_env.py=e605e041816856bc88458df8bfad85e2e77cdac40f4ba6cab1e6e7d4e3d32dd5`,
  `tests/test_runtime_env.py=58ea272f06d78f1edc672d4f569d7a7e3bd6ea0d644f3b68d6a6bd06931e024c`,
  `tests/test_runtime_guards.py=93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`.
- lap62 fresh gates: `make doctor` top ok=true, manifest 명시 doctor-runtime `ok=true`, targeted
  runtime/guards 46 passed, `make check` 116 passed, Ruff/compileall/mypy/context 및 safety PASS.

제품 G1~G4 완료/사용자 승인은 아직 없다.
```
