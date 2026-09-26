# STATUS pre-compaction snapshot — lap 194

Stage B baseline blocker R1~R4 독립 승인과 N1/N2 착수 직전 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `702f4bc0a4eee35f2506110ffa663c80ef9eceae2e299e62e682d684f596617f`
- line count: `152`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. 최우선 G1은 원본 800×600 논리 구도/UI를 유지한
1600×1200 정수 2배 출력이다. G2는 전비 5000 숫자 패치만 있고 8인 부하·개체 풀/메모리
확장 증명이 없다. G3 16인과 G4 길찾기·AI는 구현 전이다.

pinned DxWrapper 후보는 private install/uninstall, SHA 고정, byte-exact restore와 opt-in
`ddraw=n,b`를 갖췄다. 반복 fresh runtime에서 1600×1200 client/capture, 800×600 logical,
scale 2×2, 선변환 없는 입력, PS9→PS7→PS3와 30초 지속 렌더를 확인했다.

WM_CLOSE 뒤 후보는 tick 정지, `Lock2 DDERR_SURFACELOST` 100줄, teardown 미완료를 보인다.
builtin `ddraw=b` 대조군은 정상 exit/summary/validator를 통과해 종료 결함을 DxWrapper native
경로에 귀속했다. 이는 실제 결함이나 G1 표시 합격 증거의 선행조건은 아니다.

Astra/medium은 약 10회의 work/middle 뒤 큰 분기 lap170에서 한 번만 호출됐다. 방향은 소스 없는
DxWrapper 수리를 추측하지 않고 **G1 실제 표시·입력 합격 증거를 먼저 완성**하는 것이다. P6 Lock
계측은 종료 수리용 2순위 카드다.

카드2 Stage A는 원본/후보 공용 입력 시퀀스, production fail-closed, menu 대칭 판정, 즉시
flush, 승인 주소 evidence, `--g1-input-sequence`, 필수 입력 verdict와 off-mode 비개입을 갖췄다.

A-11~A-15는 입력 단계 예산과 원인을 fail-closed로 구조화한다. 각 wait는 10초, 합계 30초이며
전체 phase는 31.5초 상한을 별도 기록한다. `FAIL_NO_EFFECT`, `UNKNOWN_BUDGET_EXHAUSTED`,
`UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`를 분리하고 모두 PASS에서 제외한다.

A-13~A-16(잘림 임계값 0.25의 보수적 설계 가정, 9자리 ratio/threshold 경계, clamp와 pre-poll
분리, strict `>` 일관성)은 lap182~189에서 구현·독립 승인을 마쳤다. lap189 middle이 자체 probe
7+45건으로 위반 0을 확인했다. 상세 근거는 `docs/history/laps/`의 lap184~189 기록에 있다.
0.25는 여전히 **실측이 아닌 설계 가정**이며 Stage B 최초 run이 재평가 대상이다.

lap190 work가 사용자 승인 범위의 Stage B 첫 fresh 원본 run을 정확히 1회 실행했다. PS3와
`unit_select`까지는 PASS했지만 production provenance의 `49B6D0 ineligible` 예외로
`BLOCKED` 레코드·`drag_select`·`minimap`이 생성되지 않아 필수 검증 FAIL/BLOCKED가 됐다.
cleanup은 PASS했고 candidate run은 종속 실패 때문에 실행하지 않았다.

lap191 middle(Opus5)이 lap190 해시 6/6을 재계산 일치시킨 뒤, 그 **귀인을 기각**했다.
`49B6D0 ineligible`은 하네스 계약 불일치가 아니라 **원본의 정상·기대 분기**다. slot1199/type58의
`0x009C21D4 & 0x08 == 0`은 `analysis/memory_maps/player_offsets.md` lap57(:536)·lap61(:558)이
이미 독립 확인한 값과 동일하고, 이 run의 `primary_command_table`
(`0x008930A6`=1,10,14,17,115,190,72,329)이 비어 있지 않다는 사실이 lap61의 "group2..5는 HQ 생산의
필수 gate가 아니며 12-slot table이 선행 경계"를 재확증한다. 원본은 고칠 대상이 아니다.

lap192 work(Luna/high)는 Stage B-R R1~R4를 구현했다. stable-ineligible command-cell provenance
실패는 production 입력에 `BLOCKED`/기존 사유/diagnostic fields로 남기고 클릭은 계속 금지하면서
`drag_select`/`minimap`으로 진행한다. 후보 경로도 provenance를 캐시하고 command-cell 진단을
기록하며, baseline/candidate의 per-run `evidence.json`은 teardown 뒤 최종 error/진단/inputs를
보존한다. HQ type49 고정 술어는 제거하고 승인된 HQ 판별자가 없음을 `UNKNOWN` provenance로
기록한다. `production BLOCKED → required_inputs FAIL → overall PASS 불가` 불변식은 유지된다.

lap190이 인용한 `g1_a/evidence.json`은 마지막 flush 스냅샷일 뿐이며, 전체 evidence와 진단 필드는
`output/g1_baseline.json`에 **처음부터 보존돼 있었다**. 실제 결함은 하네스 5건이다: H1 증거 수집
실패가 무관한 `drag_select`/`minimap`을 중단시킴(provenance는 판정 입력이 아닌데도 무방비 호출),
H2 카드2 A-1 불변식이 나중 추가로 회귀, H3 `unit_select` PASS가 type을 안 봐서 기대 문자열을
증명하지 못함, H4 후보 경로 진단 비대칭, H5 flush 산출물 불완전. 수리 계약은
`docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`의 **Stage B-R**(R1~R5)이다.

lap193 middle(Opus5)이 R1~R4를 **독립 승인**했다. lap192 테스트를 재사용하지 않은 자체 드라이버로
stable-ineligible fixture에서 입력 4단계가 모두 생성되고 production만 `BLOCKED`임을 재현했고,
**실제 생성된 inputs**를 그대로 verdict에 넣어 `required_inputs=False` / 후보 `overall=BLOCKED` /
baseline `overall=FAIL`을 확인했다. `_CommandCellSnapshotError`가 아닌 예외는 여전히 run을
중단시키고 eligible fixture에서도 production은 BLOCKED이므로, 게이트가 아니라 제어흐름만 바뀌었다.
R4는 owner0 type 49/58/70/123 전부에서 `UNKNOWN`을 유지하며 HQ 존재·부재를 주장하지 않는다.
R5 술어(`count>=1`/`count>=2`)는 그대로이고 Stage B 재실행은 0회다.

lap193이 남긴 비블로킹 2건: **N1** run이 중단되지 않으므로 이 경로에서 top-level
`command_branch`/`alternate_ui_snapshot`/`primary_command_table`/`error`가 비어 있고 진단은
`inputs[production]` 안에만 있다 — 데이터는 온전하나 top-level만 읽는 보고자는 lap190과 같은
착시를 겪는다. **N2** 후보가 `trace_dir/evidence.json`을 두 번 쓴다.

모델 라우팅은 Luna/high(work), Claude Opus5/high(middle/judge), Astra/medium(strategy)이다.
Opus 검수는 독립 게이트 실행을 위해 `LOOP_PERMISSION_MODE=auto`를 일회 적용한다. Astra는
자동/정기 호출하지 않고 큰 분기·반복 교착에서만 약 10 lap당 1회 이하로 쓴다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 후보 2배 표시·논리 구도·입력·30초 지속 렌더 PASS; Stage A A-1~A-16 기계 검수 완료(lap189 독립 승인); Stage B 원본 1회는 하네스 H1 결함으로 중단(lap191 근본원인 확정, 원본 정상), Stage B-R R1~R4 수리 lap193 독립 승인; 실제 원본/후보 입력 비교 없음; WM_CLOSE 종료 결함 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

**다음 한 가지: 사용자 승인 대기.** lap193 middle이 Stage B-R R1~R4를 **독립 승인**했고, 승인
없이 진행할 수 있는 G1 카드2 후속은 비블로킹 카드 N1/N2뿐이다. 모델이 결정하지 않는 두 가지는
(a) **R5** — `unit_select`/`drag_select` 단언을 type 검증까지 조이는 변경(승인된 비교 run이
무엇을 증명하는지를 바꾼다), (b) **Stage B 재실행** — 2026-09-12 승인분 원본 1회는 lap190에서
소진됐다. 둘 다 새 사용자 승인 전까지 닫혀 있다. `loop/ESCALATE_SOL` 참조.

승인이 늦어지면 work tier가 N1(continue 경로의 top-level 진단 요약 보강)과 N2(후보 evidence.json
중복 write 정리)를 처리할 수 있다. 둘 다 판정식을 건드리지 않으며 게임 run이 필요 없다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경 금지. 보호 EXE SHA:
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 실패 run/prefix/display/build 재사용, 임의 retry, PASS 조건 완화 금지.
- Stage B baseline은 승인 후 열렸으나 production provenance 예외가 발생했다. 예외를
  required input PASS로 만들지 않는다. lap191 정정: 이 예외의 관측 자체는 **원본 정상 분기**이므로
  "세탁"이 아니라 하네스 제어흐름을 고친다. 원본 거동을 결함으로 기록하지 않는다.
- **승인 소진:** 사용자가 승인한 원본 1회는 lap190에서 썼다. Stage B 재실행과 입력 단언 내용
  변경(R5)은 새 사용자 승인 없이는 금지다.
- 이번 run은 `drag_select`/`minimap` 전에 중단됐고 candidate를 실행하지 않았다. 실패 run/prefix/
  display/build 재사용, 임의 retry, PASS 조건 완화 금지.
- random seed 미노출로 동일 시작 상태는 미증명; Tier-1/Tier-2로 분리한다.
- minimap은 camera 절대 목적지 비교가 필요하다.
- G1 실제 비교/입력 증거와 G2~G4 제품 증거는 아직 없다.

## 검증 상태

- lap146~169: 후보 2배 표시·입력·지속 렌더 PASS, DxWrapper close 결함 builtin 대조로 귀속.
- lap170 Astra/medium: G1 합격 증거 우선, P6 주차.
- lap171~181: Stage A A-1~A-12 구현·독립 검수; Opus/auto가 게이트 직접 재현.
- lap182~185: A-13/A-14 구현·독립 승인; Fast 207, runtime 94, safety PASS.
- lap186 work: A-15 구현; Fast 208, targeted 8, safety/static PASS, game 0.
- lap187 middle: A-15 부분 승인(요구2 미충족, 카드 A-16 발행); Fast 208, targeted 8,
  SAFETY_PASS, 독립 clamp probe 5건, game 0.
- lap188 work: A-16 구현; Fast 209, targeted 5, safety/static PASS, game 0; middle 검수 대기.
- lap189 middle: A-16 독립 승인; Fast 209, `SAFETY_PASS`, 독립 probe 7+45건 위반 0,
  소스 SHA 대조 일치, game 0.
- lap190 work: fresh baseline 1회; pre-gates Fast 209/SAFETY_PASS, PS3·unit_select PASS 후
  `49B6D0 ineligible` 예외로 Stage B FAIL/BLOCKED, cleanup PASS, candidate 0회; 상세는
  `docs/history/laps/20260912_lap190_work_g1_stageb_baseline_block.md`.
- lap191 middle: lap190 해시 6/6 일치, `49B6D0` 하네스귀인 **기각**(원본 정상 분기, lap57/lap61
  재확증), 하네스 결함 H1~H5 확인, Stage B-R 발행; Fast 209, `SAFETY_PASS`, game 0, source 무변경;
  상세는 `docs/history/laps/20260912_lap191_middle_g1_stageb_root_cause.md`.
- lap193 middle: R1~R4 **독립 승인**; `make check` 210 passed/exit 0, `SAFETY_PASS`,
  자체 probe 2건 25단언 위반 0(lap192 테스트 미재사용), source SHA 2/2 일치, game 0,
  비블로킹 카드 N1/N2 발행; 상세는
  `docs/history/laps/20260912_lap193_middle_stagebr_verification.md`.
- lap192 work: Stage B-R R1~R4 구현; targeted 7 passed, `make check` 210 passed,
  Ruff/compileall/mypy/CONTEXT_PASS, `SAFETY_PASS`, game 0; 원본 source/EXE/DLL/assets/
  baseline/golden 무변경(하네스 source만 변경);
  상세는 `docs/history/laps/20260912_lap192_work_g1_stageb_repair.md`.
- latest snapshot: `docs/history/laps/20260911_status_lap187_compaction.md`.

## 바퀴 기록

- lap2~183 및 이전 STATUS 원문: `docs/history/laps/`.
- lap184 work: `docs/history/laps/20260911_lap184_luna_a14_threshold_provenance.md`.
- lap185 middle: `docs/history/laps/20260911_lap185_middle_a14_verification.md`.
- lap186 work: `docs/history/laps/20260911_lap186_luna_a15_clamp_separation.md`.
- lap187 middle: `docs/history/laps/20260911_lap187_middle_a15_verification.md`.
- lap188 work: `docs/history/laps/20260911_lap188_luna_a16_threshold_consistency.md`.
- lap189 middle: `docs/history/laps/20260912_lap189_middle_a16_verification.md`.
- lap190 work: `docs/history/laps/20260912_lap190_work_g1_stageb_baseline_block.md`.
- lap191 middle: `docs/history/laps/20260912_lap191_middle_g1_stageb_root_cause.md`.
- lap192 work: `docs/history/laps/20260912_lap192_work_g1_stageb_repair.md`.
- lap193 middle: `docs/history/laps/20260912_lap193_middle_stagebr_verification.md`.
- current escalation: `loop/ESCALATE_SOL`.
- current handoff: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`.
