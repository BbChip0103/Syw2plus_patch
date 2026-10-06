# STATUS — 매 바퀴 갱신하는 기억

lap676~770 전문은 기존 압축 포인터와 `docs/history/laps/`에 보존했다. G5 v10은 2026-09-29 18:45
사용자 3단 승인·종료(제한부)했다. 최신 사용자 지시로 현재 활성 목표는 G2 ESL2608 두 EXE 점검이며,
G1 W60은 lap785 증거를 보존한 채 일시중단했다.

lap795~796 middle/work가 rally 입력 slot/action/writer를 고정하고 HQ 겹침을 확인했다.
lap797 work는 Phase-D 저장/로드를 normal/fixed_start × baseline/candidate **4/4 PASS**로 완주했다.
lap798 work는 목표를 `(450,300)→(600,300)`으로 최소 수정해 같은 live 경로를 fresh 4-way 실행했다.
네 조합 모두 HQ rally `(94,57)→(94,52)`·worker `2→3`·cleanup/source 보호는 PASS했으며, hero는
fixture에서 주문·counter `0→0`으로 UNKNOWN이다. 상세는 `docs/history/laps/20260930_lap798_work_g2_phase_c_rally_target_paired_pass_hero_unknown.md`다.
lap798 targeted 4 passed, `make lint`·`make typecheck` PASS; final `make check` **1164 passed, 5 skipped
in 729.06s**, Ruff/compileall/mypy/CONTEXT_PASS, `SAFETY_PASS`, log SHA `11a0837a…ea86a81`; 제품 EXE·원본·참고 저장소·커밋 없음.
lap799 middle은 lap798 raw/EXE를 독립 재해시해 rally/worker 4-way를 2단 PASS했다. hero는 nation1의
빈 live slot 고정 클릭과 prerequisite 없는 fixture 때문에 **`HOLD(harness contract)`**다. 환경 제한으로
닫지 않고 hero kind의 live flag·prerequisite·UI 주문을 고정하는 work handoff를 발행했다.
lap800 work는 live HQ type/TypeSpec hero flag/생산표를 연결하고, map dimensions 기반 native `op5`
prerequisite fixture와 live command-cell 탐색을 구현했다. normal baseline fresh r1~r5에서 prerequisite
unit은 생성됐지만 `PlayerStruct+0x315C[kind]`가 10초 후에도 `0`으로 남아 hero 주문/생성은 **`UNKNOWN(fixture contract)`**다.
UI 좌표·slot 누락·native fixture 좌표 결함은 raw로 추적해 수리했으며, r5 source/cleanup는 PASS다.
G1 lap784~785 및 G2 lap786~793 전환/주소수리/Phase-C raw 충돌 계보는 각 lap 기록에 보존했다.
lap790 Phase-A와 lap791 명령은 4-way PASS했으며, lap792~799 Phase-C rally/worker도 4-way·2단 PASS했다.

## 지금 상태

lap770 strategy가 G1 경로 **W60(논리800 유지 + 2배 미러 합성기, content-keyed present)**를 채택했다.
lap772~778의 메뉴 gate/correctness/input hold 계보는 각 lap 기록과 `loop/ESCALATE_SOL`에 보존했다.
lap779 work는 입력 전달 raw 계측·focus/root/down/up/hold 수리와 WndProc/GetCursorPos logical 수신 계측을
추가해 fresh ON을 PS3 tick≥300까지 완주했다. lap780 middle이 확정한 OFF summary capacity 결함은
lap781이 수리했고 lap782가 수용했다. lap783 production mapping 시도는 lap784가 근거 결함 2건으로 HOLD했다.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 제품 미완료, **W60 trace finalization PASS / overall HOLD·일시중단** | production raw-only N/A/paired의 middle 판정, S3, G1 승인 |
| G2 | **ESL2608 Phase A + B + Phase D 저장/로드 + Phase C rally/worker 4-way PASS; hero UNKNOWN(fixture contract)** | DxWnd·부하·멀티, 새 이름 배포본 2개, 사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 사용자 지시로 보류 | candidate AI 정책 없음, 사용자 승인 |
| G5 | **v10 종료·사용자 3단 승인** | 제한 수용(G 멀티 env 등) |

## 지금 막힌 것 (Blockers)

Phase A/B와 Phase D 저장/로드, Phase C rally/worker는 4-way PASS다. lap800 r5에서 HQ type49의
hero94/prereq37 후보를 live flag+생산표로 확인하고 prerequisite unit37을 native `op5`로 생성했지만,
live gate cache `PlayerStruct+0x315C[37]`가 10초 동안 0이었다. 따라서 hero는 제품 FAIL로 승격하지 않고
`UNKNOWN(fixture contract)`로 닫는다. DxWnd bundle/profile, 24k/144k 부하와 멀티는 아직 미검증이다.

## 검증 상태

- lap797: Phase-D final fresh **4/4 PASS**(normal/fixed_start × baseline/candidate), 자체 왕복과 protected
  `save000.dat` load 모두 PS3 복귀, owner signature `2→2`, crash/timeout/residue0, source unchanged.
  raw는 외부 temp `g2_esl2608_lap797/`에 보존했고, baseline N4K8 absent/candidate offset60을 구분했다.
- lap790: 주소 pin/거부 targeted pytest **12 passed**, normal/fixed_start × baseline/candidate Phase A **4/4 PASS**;
  100 active fixture, counts `1→19→20`, recall20, reject20, remove19, re-add20. 결과 raw는
  `temp/Syw2plus_patch/g2_esl2608_lap790/`에 보존했고 source unchanged/cleanup PASS다. `make check`는
  **1157 passed, 5 skipped** in 689.05s, Ruff/compileall/mypy/context PASS, exit0; log SHA
  `8dcde3d83f7033a329cdc542ac56750e891179a1614a124cb6818eba38410da5`.
- lap791: Phase-B targeted pytest **3 passed**, Ruff clean; 명령 probe normal/fixed_start × baseline/candidate
  **4/4 PASS**, 각 MOVE/ATTACK/STOP/HOLD/PATROL selected `20/20`, sentinel 변경 `0`, source unchanged/cleanup PASS.
  raw는 `temp/Syw2plus_patch/g2_esl2608_lap791/`에 보존했다. 최종 `make lint`/`make typecheck`/`make check` PASS;
  `make check`는 **1160 passed, 5 skipped** in 719.81s, Ruff/compileall/mypy/CONTEXT_PASS, exit0, log SHA
  `06bcc158124f064084a3123697db787e432bf2bd4e4498ad7e1f529cc06d4095`.
- lap792/793 review: 네 raw SHA는 기록과 일치하나 첫 raw는 worker `2→2`·구형 checks/stages이고 후속 3개만
  worker `2→3`·신규 type7/7/21 cmd3이다. 후속 3개는 rally 필드 불변·hero `0→0`; 네 raw 모두 source unchanged/
  cleanup PASS다. 현 probe mtime은 마지막 raw 뒤라 raw 생성 source identity는 미고정이다. Phase C는 HOLD/ESCALATE다.
  최종 `make check`는 **1162 passed, 5 skipped** in 723.90s, Ruff/compileall/mypy/CONTEXT_PASS, exit0이며
  `checks/safety.py`도 `SAFETY_PASS`다. 로그 `logs/gates/full-test-20260930-lap792-r2.output`.
- lap793 final Fast fingerprint `8f638c20160a1d38287098d553bf193fa412bbcf`: `make check` **1162 passed,
  5 skipped** in 728.30s, Ruff/compileall/mypy/CONTEXT_PASS, exit0; log SHA `73a66a38…3e4d`. 선행 `SAFETY_PASS`.
- lap794: static UI contract pytest **3 passed**. r2/r3/r4 raw SHA는 각각
  `bf53ae19…6c0834`, `9e15c7bd…2e84c`, `366d52bc…e40fe3`; source unchanged/cleanup PASS.
  r4 worker `2→3` then hero-cell reserve/count `3→4`, rally unchanged. Final nation-indexed hero-counter
  edit is not runtime-verified; final `make check` **1163 passed, 5 skipped** in 726.76s, Ruff/compileall/
  mypy/CONTEXT_PASS and `checks/safety.py` `SAFETY_PASS`, exit0. Phase-C remains runtime HOLD.
- lap795 middle: baseline `cade60b2…b176a3`와 r2/r3/r4 raw SHA를 재계산해 기록과 일치했다. 정적
  disassembly에서 descriptor `0x11`=action `0x15`·shortcut `T/t`, live slot `0x8930A6+2*i`,
  좌클릭 발행 `0x41EBF6..0x41F0A4 -> 0x4AE550 -> 0x4AEC60 -> 0x40FF90 -> 0x412540`을 확인했다.
  r2 `R` 셀+좌클릭은 선택 `1→0`, r3/r4 우클릭도 계약 밖이다. 새 runtime·제품/하네스 변경 없음.
  final fingerprint `d62ee34d53b52ea0bc29f0758653f2d878349622`: `make check` **1163 passed,
  5 skipped** in 720.05s, Ruff/compileall/mypy/CONTEXT_PASS, `SAFETY_PASS`, exit0; log SHA `022756f1…227fc`.
- lap798 work: rally target을 HQ 동쪽 `(600,300)`으로 최소 수정하고 normal/fixed_start × baseline/candidate
  fresh 4-way를 수행했다. 네 조합 rally `(94,57)→(94,52)`·worker `2→3` PASS, hero 주문/counter `0→0`
  UNKNOWN; raw/source/cleanup는 전부 보존·PASS다.
- lap799 middle: 네 raw/EXE SHA와 rally/worker 수치를 독립 재계산해 2단 PASS했다. hero는 HQ 생산표상
  kind94/98/100/102가 각각 prereq37/46/53/45를 요구하는데 현 fixture가 없고 nation1 클릭 slot은
  descriptor0임을 확인해 `HOLD(harness contract)`로 판정했다. 제품/하네스/runtime 변경 없음. `make doctor`
  `ok=true`; targeted **4 passed**; final `make check` **1164 passed, 5 skipped in 731.74s**, lint/compileall/
  mypy/CONTEXT/SAFETY PASS, exit0, log SHA `323b58f0…1d71ec0`.
- lap800 work: `tools/g2_esl2608_phase_c_production_probe.py`에 live HQ type/TypeSpec flag/생산표 기반
  hero 계약, map-size 기반 prerequisite native fixture, 12-slot UI cell 계산과 gate-cache 관측을 추가했다.
  normal baseline r1은 좌표 범위 오류, r2는 slot7 누락, r3는 UI row y 오차를 각각 raw로 확인·수리했고,
  r4/r5는 HQ type49→hero94/prereq37, native row 생성, `prereq_owned_cache=0`, hero order/generation0을
  보였다. r5 raw SHA `97d6ebf3…b0a97c6`, baseline SHA `cade60b2…b176a3`, source unchanged,
  private game removed/prefix residue0. targeted **4 passed**, `make lint`/`make typecheck` PASS; final
  `make check` **1164 passed, 5 skipped in 732.47s**, exit0, Ruff/compileall/mypy/CONTEXT_PASS,
  `SAFETY_PASS`, log SHA `6175c42f…209cd21`. 다음은 DxWnd/profile 단계이며 hero는 UNKNOWN 유지한다.

## 다음 한 가지
- **work handoff:** hero `UNKNOWN(fixture contract)`를 유지하고, 새 fixture 추측을 반복하지 않는다. 다음은
  두 새 EXE의 DxWnd bundle/profile 창모드·스크롤 paired 점검이며, 이후 부하·멀티·새 이름 수정판 순서로 간다.

금지: 기존 temp EXE 덮어쓰기, 원본/참고 저장소 쓰기, `local/runtime/g2_*`·`*g2shift*` 디렉터리 접근,
G1/G5 변경, 커밋.

## 바퀴 기록

- lap789(middle): lap788 raw가 스스로 ESL2608 pool `0x0112E000`을 보존하지만 probe/bridge/fallback은
  generic `0x0108C000`을 사용했음을 독립 확정했다. 제품 초기화 blocker를 기각하고 work 하네스 수리와
  fresh 4-way 재실행 조건을 발행했다. 게임/EXE/하네스 변경 없음.
- lap790(work): ESL2608 pool/existence 단일 계약과 generic 주소 거부 테스트를 추가했다. 순차 fresh 실행에서
  normal/fixed_start baseline/candidate Phase A 4/4 PASS; 동시 UI timeout은 환경 timing으로 분리했다.
- lap791(work): Phase-B 명령 probe를 추가해 네 조합에서 이동·공격·정지·홀드·순찰을 selected20/20,
  sentinel0으로 PASS했다. startup type 변동·이동 후 stale selection은 하네스 문제로 최소 수리했고 제품 EXE는 변경하지 않았다.
- lap793(middle): lap792 raw를 독립 재계산해 첫 raw `2→2`·구형 판정과 후속 3개 `2→3`을 분리했다.
  4/4 서술과 raw/source identity 충돌로 Phase C를 HOLD하고 `loop/ESCALATE_SOL`을 갱신했다. 구현·게임 실행 없음.
- lap794(work): baseline `.text`에서 rally writer/command `0x15`와 hero eligibility/callers를 정적 고정했다.
  r2 좌클릭→r3 R+우클릭→r4 direct 우클릭으로 최소 수리했으나 rally field는 계속 `-1,-1`이었다.
  r4 nation2 hero cell `(704,540)`은 worker count `3→4`를 만들었고, player stride counter 수리를 남긴 채
  세 번 실행 한도로 `loop/ESCALATE_SOL`을 만들었다. 제품 EXE·커밋 없음.
- lap795(middle): baseline/raw/capture를 독립 재검수해 lap794 rally 입력이 전부 계약 밖임을 확정했다.
  descriptor `0x11`·action `0x15`·지도 좌클릭 writer 경로를 고정하고 work fresh 1회 handoff를 남겼다.
  게임 코드·하네스·EXE·runtime 변경 없음.
- lap796(work): live slot/action/queue/writer trace와 HQ `ecx` 일치를 fresh 확인했다. target이 HQ와
  겹쳐 rally effect는 UNKNOWN, worker `2→3` PASS·hero UI `3→4`/counter `0→0` unresolved; Phase D로 넘긴다.
- lap798(work): HQ 동쪽 `(600,300)` 목표로 rally `(94,57)→(94,52)`와 worker `2→3`을 네 조합에서
  fresh PASS했다. hero 주문/counter `0→0`은 fixture UNKNOWN으로 남겼고, 제품 EXE·원본은 불변이다.
- lap799(middle): lap798 raw를 독립 검수해 rally/worker 2단 PASS, hero `HOLD(harness contract)`로
  판정하고 live hero flag·prerequisite·UI 주문 기반 work handoff를 남겼다. 게임/코드 수정 없음.
