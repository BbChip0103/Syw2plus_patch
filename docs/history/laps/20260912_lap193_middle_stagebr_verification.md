# 2026-09-12 | lap 193 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 지정 middle(진단·계획·확인); 실제 Claude Code
  `claude-opus-5`/high. hands-on 게임 코드 구현 없음. 게임 run 0회.
- 가설 / 사용자 관찰: lap192가 구현한 Stage B-R R1~R4가 (a) 관측을 PASS로 세탁하지 않고,
  (b) stable-ineligible fixture에서 `drag_select`/`minimap`을 실제로 실행하며, (c) baseline/후보
  진단·flush가 대칭이고, (d) 근거 없는 HQ type 목록을 추가하지 않았는지를 **lap192 테스트를
  재사용하지 않은 자체 probe**로 확인한다.
- 예상 PASS / FAIL 조건: 위 4항 전부 만족 + `production BLOCKED → required_inputs FAIL →
  overall PASS 불가` 불변식 유지 + R5(단언 내용 변경)/Stage B 재실행 미수행이면 승인.
  하나라도 어긋나면 카드 발행 후 반려.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 검수 대상 무변경 확인 —
  `tools/runtime_env.py` SHA256 `8955789be2a8f39d221e09a0da1010e896f87b0f464106bcc928d5c372c40bd3`,
  `tests/test_runtime_env.py` SHA256
  `7054d441f0ff5bf33e71d0c55397ee4da36f957efe7dd53459a96a03bed1d197`
  (둘 다 lap192 기록값과 2/2 일치). 이번 바퀴 변경은 문서뿐이다: `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`, 이 기록.
  uncommitted, 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(무변경). 후보 run 없음,
  Wine/Xvfb 미기동. fixture는 `_command_cell_reader_fixture(branch_type_flags=0)`
  (stable-ineligible)와 기본(eligible), 그리고 owner0 type 49/58/70/123 합성 scene이다.
  실제 플레이어/지도/군대 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `make check` → **210 passed**, Ruff/compileall/mypy/`CONTEXT_PASS`, exit 0 (lap192 수치 재현).
  `bash checks/safety.sh check` → `SAFETY_PASS`.
  독립 probe 2건(총 25개 단언, 실패 0):
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260912_013327_lap193_probe_r1r4.py`
  SHA256 `0d3ab4b47de9fdbaaf3f967fefcb0608149feee98c5f5c5c690cc5579976493d`,
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260912_013327_lap193_probe_r3_artifacts.py`
  SHA256 `5ef37a5c1ce45b7e5bcf7185b0fc4a5cdc4e5be3d77c1d5eda36e4739ddfa17f`.
  두 probe 모두 `_g1_run_input_sequence`를 자체 드라이버로 호출하며 lap192 테스트 본문을
  재사용하지 않는다. 새 스크린샷 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):

  **R1 PASS(독립 승인).** stable-ineligible provenance에서 입력 태그가
  `unit_select, production, drag_select, minimap` 4개 전부 생성된다(H1 회귀 해소).
  production은 `result=BLOCKED`, `waited=False`, `(670,490)` 클릭 미전송,
  `provenance_error`/`command_branch`/`alternate_ui_snapshot`/`primary_command_table` 4필드 보존,
  `command_branch.stable=True`, `eligible=False`. 비-production 3단계는 PASS로 남아
  관측이 격하되지도 세탁되지도 않았다. `phase_metrics.items.production_provenance.status="ERROR"`로
  실패 자체가 예산 레코드에 남는다.
  **세탁 방지 불변식:** probe가 합성 리스트가 아니라 **실제 생성된 inputs**(+PASS menu)를
  `_g1_input_verdict`에 넣어 `required_inputs=False`, 후보 `overall=BLOCKED`,
  baseline `overall=FAIL`을 재현했다. A-1 불변식 그대로 승계.
  **catch 범위 과대 아님:** `read_production_cell`이 `_CommandCellSnapshotError`가 아닌 예외를
  던지면 run은 여전히 중단된다(probe P2, `Boom` 전파). eligible fixture에서도 production은
  BLOCKED이고 `provenance_error`가 없다(P3) — 즉 게이트가 아니라 제어흐름만 바뀌었다.

  **R2 PASS.** 후보 except(`:3567`)가 baseline except(`:3183`)와 **바이트 동일한 4줄**로
  `_record_g1_command_cell_error(evidence, exc)`를 호출한다. 후보
  `read_production_cell`(`:3522`)도 baseline(`:3151`)과 같이 `evidence["production_cell"]`에
  캐시한다. 진단 비대칭(H4) 해소.

  **R3 PASS.** 두 경로 모두 `finally`에서 cleanup 뒤 per-run `evidence.json`을 최종 기록한다
  (baseline `:3224`, 후보 `:3634`). probe2가 flush 산출물만으로 원인 재구성 가능함을 확인했다:
  `evidence.json`의 `inputs[production]`에 `provenance_error`(문자열 `"_CommandCellSnapshotError:
  49B6D0 ineligible: original command-cell creation predicates are false"`)와 진단 3필드가 있고
  `inputs.jsonl`도 동일하다. 기존 필드 삭제·개명 없음.

  **R4 PASS.** `owner0_hq_type`은 삭제되지 않고
  `{status:"UNKNOWN", observed_owner0_types:[...], reason:"no approved HQ discriminator; type 49 is
  fixture-specific"}` provenance로 보존된다. owner0 type 49/58/70/**123(미지)** 네 fixture 전부에서
  `status=UNKNOWN`, `owner0_hq_world=None`, `owner0_hq_candidates=None`으로 **HQ 존재/부재를 전혀
  주장하지 않는다.** 소스에 `49, 58, 70` 형태의 추측 type 목록 하드코딩 없음. 이 값을 판정에
  쓰는 소비자도 없다(repo grep: 생성 3곳·소비 0곳).

  **R5 미수행(SKIP, 올바름).** `unit_select`/`drag_select` PASS 술어는 여전히
  `count>=1`/`count>=2`로 type을 검사하지 않는다. work tier가 승인 경계를 넘지 않았다.
  Stage B 재실행 0회.

  **비블로킹 관측 2건(카드 N1/N2로 발행, 단독 바퀴 불필요):**
  N1 — run이 더 이상 중단되지 않으므로 이 경로에서는 except 블록이 돌지 않아
  **top-level** `evidence["command_branch"]/["alternate_ui_snapshot"]/["primary_command_table"]/
  ["error"]`가 비어 있다(probe2로 4/4 부재 확인). 진단은 `inputs[production]` 안에만 있다.
  데이터는 보존되지만, top-level만 읽는 보고자는 lap190과 **같은 종류의 착시**를 다시 겪는다.
  N2 — 후보 경로가 `trace_dir/evidence.json`을 `:3634`와 `:3653`에서 두 번 쓴다(사이에 evidence
  변형 없음). 중복일 뿐 결함은 아니다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 판정은 **모델 기술 컨펌**이며 제품 G1
  합격이 아니다. 실제 원본/후보 비교 입력 증거, WM_CLOSE 종료 결함, random seed 동일성,
  minimap 절대 목적지 비교, G2~G4 제품 증거는 여전히 미검증이다.
  R5와 Stage B 재실행은 **새 사용자 승인 없이는 금지**이며, 2026-09-12 승인분 원본 1회는
  lap190에서 소진됐다. 현재 승인 없이 진행할 수 있는 G1 카드2 후속 작업은 N1/N2뿐이다.
- 다음 한 가지: **사용자 승인 대기.** 승인이 필요한 것은 (a) R5 단언 강화, (b) Stage B
  원본1회+후보1회 재실행 승인이다. 승인 전 안전한 대안 작업은 work tier의 N1(top-level 진단
  요약 보강)과 N2(중복 write 정리)뿐이며 둘 다 비블로킹이다.

## 종료 시점 파일 해시 (uncommitted 보존용)

- `docs/STATUS.md` `702f4bc0a4eee35f2506110ffa663c80ef9eceae2e299e62e682d684f596617f`
- `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`
  `6757c1e19b8b4f414804b2b220d585459a124e8c100987f33c4f9a37ede3e408`
- `loop/ESCALATE_SOL` `8d6ed94457a6a901c4019e7bbd23ebcd9fe4a3c76e89ab1ea51d165f907b5171`
- `tools/runtime_env.py` `8955789be2a8f39d221e09a0da1010e896f87b0f464106bcc928d5c372c40bd3` (무변경)
- `tests/test_runtime_env.py` `7054d441f0ff5bf33e71d0c55397ee4da36f957efe7dd53459a96a03bed1d197` (무변경)
- 이 기록 파일 자체의 해시는 이 절 추가 전 값이므로 재계산이 필요하다.
- 문서 갱신 후 재실행: `make check` → 210 passed / exit 0, `CONTEXT_PASS`;
  `bash checks/safety.sh check` → `SAFETY_PASS`.
