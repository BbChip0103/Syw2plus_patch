# 2026-09-11 | lap 107 | G1 presentation 계획 중간 검토

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier, 저장소 routing은
  `codex/gpt-5.6-sol`, high로 조회됐다. 세션 표면의 별도 backend attestation은 없으며 모델
  exit0을 판정 근거로 쓰지 않았다. 게임 구현/trace/유료 하위 세션은 실행하지 않았다.
- 가설 / 사용자 관찰: lap106이 원본 출력 경로 식별과 후보1600×1200 검증을 분리한 것은
  타당하지만, 기존 하네스가 COM object/surface/rectangle/caller를 수집하지 못하므로 최소
  관측 hook과 검증기를 먼저 정의해야 실제 work trace가 측정 가능한 한 카드가 된다.
- 예상 PASS / FAIL 조건: 두 원본·lap73 raw artifact·lap105 static 값을 독립 대조하고,
  기존 도구의 수집 가능/불가능 필드와 새 카드의 명령·로그·상한·cleanup·중단 기준이 근거에
  맞으면 계획 검토 완료. 근거 충돌, 필수 gate 실패, 마일스톤 경계면 ESCALATE_SOL 보존.
- 변경 파일 / source fingerprint / 커밋: 게임/helper/tests/binary/dependency/fixture/baseline/golden
  변경 없음. `docs/plans/20260911_lap107_g1_presentation_trace_card.md`, `docs/STATUS.md`, 본 기록만
  문서 변경하고, 소진된 `loop/ESCALATE_SOL` SHA
  `8a80e685e4b394920beb34843f8c99f81d135a5505df278a9b6478a401b22e23`는 아래에 원문 보존 후 제거.
  최종 plan SHA는 `b87a6d0df6501e2e3fc8b4d3aef081962c25a3fdb8a6075dec6f3b0c2006a31`,
  STATUS SHA는 `9d1fc532fa4561848c842b5eb7c9546e7467e158e38649fbb8dbadea6c9f4dde`다.
  `LOOP_ALLOW_COMMITS=0`, uncommitted; 전체 기존 untracked 작업을 보존했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: source와 lap73 private copy
  SHA가 모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp=0`, PE32임을
  재확인했다. 후보/runtime/game/플레이어/지도/군대/새 fixture/capture는 SKIP.
- 실행 명령 / 로그 / 캡처: `loopctl models`, `sha256sum`, `cmp`, `file`, `objdump -h/-p/-d`,
  read-only Python byte scan, `jq`, `rg`로 문서·원본·lap73 artifact·runtime/bridge 구현을 대조했다.
  첫 Python scan은 `.text` file offset을 `0x400`으로 잘못 입력해 45/14와 엉뚱한 old bytes를 냈고 즉시
  폐기했다. `objdump -h`의 정확한 `0x1000` mapping으로 한 번 정정했다. 새 runtime/log/PNG 없음.
- 측정값 / 판정: corrected scan에서 `+0x14` call-form 49개, `+0x2c` 14개와 lap105의 8개 old
  bytes가 전부 일치했다. lap73 manifest/baseline/verdict/provenance SHA도 원문과 일치했고,
  cleanup=true, builtin ddraw hash 존재, 1600×1200 root/800×600 content, required_inputs=false를
  확인했다. 현재 `g1_baseline.json.boundary=null`; runtime helper는 memory read만 하며 DirectDraw
  trace hook은 없다. lap106 boundary 분리는 ACCEPT, 전체 work 카드는 **REVISE**. 문서 변경 뒤
  `make check` **140 passed**, Ruff/compileall/mypy(8 files)/context PASS, safety `SAFETY_PASS`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인: static 49/14는 interface 의미가 아니며
  diagnostic `_inmm.dll` 자체의 side effect, actual present/rectangle/2배 출력/5입력/G1 및 사용자
  승인은 UNKNOWN/BLOCKED다. Fast exit0은 계획·제품 승인으로 승격하지 않는다. 이번 문서-only
  lap으로 구현 미변경 연속 경고에 도달하므로 generic 재집계를 중단하고 다음 측정 가능 변경을
  SHA-gated trace harness+1회 scene으로 고정했다.
- 다음 한 가지: 새 Luna/high가
  `docs/plans/20260911_lap107_g1_presentation_trace_card.md`만 수행한다. hook/validator를 최소 구현해
  targeted/Fast/safety/doctor-runtime 후 fresh private trace 1회를 수집한다. 실패 시 재시도 없이
  변경·로그를 보존하고 `loop/ESCALATE_SOL`로 새 중간 검수에 돌려보낸다.

## 소진 전 `loop/ESCALATE_SOL` 원문

```text
# lap106 escalation — G1 presentation 계획 중간 검토 대기

## 상태 / 보존

구현 근거 불명확 및 역할 충돌 때문에 일반 실행을 중단한다. 게임 코드·binary·runtime은
수정/실행하지 않았다. lap105 원문은
`docs/history/laps/20260911_lap106_predecessor_escalation.md`에 byte-for-byte 보존했다
(SHA256 d619e0d0c8a91cbc01deedcdf56796c8e774046af281bdff9ac90b892aa415f0).
이전 STATUS는 `docs/history/laps/20260911_lap106_predecessor_status.md`에 보존했다.

## 승격 작업자가 이어서 검증할 것

새 Sol/high 세션은 `docs/STATUS.md`의 다음 한 가지와
`docs/plans/20260911_lap106_g1_presentation_handoff.md`를 읽고 계획을
ACCEPT/REVISE/BLOCKED로 판정한다. 실제 모델·근거·남은 위험을 기록한다.
원본 경로 식별과 후보 2배 출력 검증의 분리가 타당한지, 기존 계측 도구가 object/surface/
rectangle/caller를 같은 run에 연결할 수 있는지 확인하고 work 카드의 명령·필드·중단 기준을 정한다.
실제 원본 출력 경로 trace는 새 Luna/high에 인계한다. 직접 게임 구현으로 대체하지 않는다.
기존 바이트/후보 개수는 역사적 보고이며 새 독립 검수로 승인되지 않았다.

## 종료 / 승인 경계

Astra 상위 방향 문서만 작성했다. Fast 결과는 lap106 이력에 기록하며 process exit 0을
계획 승인·runtime 검증·제품 PASS로 쓰지 않는다. 구현·G1 승격·M2 진입·사용자 승인 없음.
필수 게이트 예상 밖 실패는 재시도하지 않고 그 실패도 승격 검토 대상으로 남긴다.
```
