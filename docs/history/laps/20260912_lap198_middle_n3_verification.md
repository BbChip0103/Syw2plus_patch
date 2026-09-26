# 2026-09-12 | lap 198 | 목표 G1

- 실제 provider/model/효과 / 지정 역할: 지정 middle(진단·계획·확인); 실제 Claude Code
  `claude-opus-5`/high, `LOOP_PERMISSION_MODE=auto`. hands-on 게임/하네스 구현은 하지 않았다.
- 가설 / 사용자 관찰: lap197 work가 구현한 N3(`production_provenance_error` 구조화 표식)가
  (a) 비치명 경로에서 실제 flush 산출물에 보존되고, (b) fatal-only 경로에는 생성되지 않으며,
  (c) 기존 `error` 의미와 `required_inputs`/`overall` 계산을 바꾸지 않는지 독립 검수한다.
- 예상 PASS / FAIL 조건: PASS = 검수 대상 해시 일치 + `make check`/safety 독립 재현 +
  자체 드라이버 probe가 (a)(b)(c)와 R1~R4/N1/N2 무회귀를 전부 만족. 하나라도 어긋나면 FAIL로
  적고 work tier에 되돌린다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **문서만 변경** —
  `docs/STATUS.md`, 이 lap 기록, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  `loop/ESCALATE_SOL`. source/tests/EXE/DLL/assets/baseline/golden 무변경.
  검수 전후 동일: `tools/runtime_env.py` SHA256
  `fd28e3a1aab1d4be65beeb18ba09f01a2ae3a72cc229c8db1f9ab6b66d73a92f`,
  `tests/test_runtime_env.py` SHA256
  `9082d1567b46a83e4e7c1ff74ccdd295a48cf79687f50be23a6da3bfd0cf536f`.
  전부 uncommitted(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE/DLL/assets
  무변경·미실행. **게임 run 0회, Stage B 재실행 0회, R5 0회, PNG 0장.** fixture는 tmpdir에
  구성한 synthetic input/evidence dictionary이며 활성 플레이어·지도·군대는 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `make check` → **213 passed / exit 0**, Ruff `All checks passed!`, compileall, mypy 9 files
  `Success`, `CONTEXT_PASS` (로그 `/tmp/lap198_makecheck.log`).
  `bash checks/safety.sh check` → **SAFETY_PASS / exit 0**.
  독립 probe `.venv/bin/python temp/20260912_lap198_probe_n3.py` → **assertions=35 failures=0 / exit 0**.
  사본: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260912_lap198_probe_n3.py` SHA256
  `ea7fefb0538c5df28ce07998fe544b80ff8a75647246b31c77f6c74f4fb39278`.
  probe는 `tests/test_runtime_env.py` 본문을 import·재사용하지 않은 자체 드라이버이며, 실제
  `_g1_flush_input_stage` 배선으로 tmpdir에 쓴 `evidence.json`/`inputs.jsonl`을 **디스크에서
  되읽어** 판정한다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **N3 독립 승인 (모델 기술 컨펌, 제품 G1 합격 아님).**
  - (a) 비치명 경로: stable-ineligible fixture에서 디스크 `evidence["production_provenance_error"]`
    == `evidence["error"]` == production 레코드의 `provenance_error`. 레코드는 이동·삭제되지 않고
    키집합이 그대로다. `command_branch`/`alternate_ui_snapshot`/`primary_command_table`도 함께
    승격된다. `command_cell_diagnostics`는 이 예외가 보유하지 않아 양쪽 모두 없다(누락 아님).
  - (b) fatal-only 경로: production 레코드에 `provenance_error`가 없거나 production 레코드 자체가
    없으면 `production_provenance_error` 키가 **생기지 않고** fatal `error` 문자열이 그대로 남는다.
  - (c) 순서 검증: provenance flush로 `error`가 채워진 뒤 outer except의 직접 대입(`:3203`/`:3587`)이
    오면 `error`는 fatal로 **갱신되고** `production_provenance_error`는 비치명 맥락으로 **생존**한다.
    두 값이 달라져 소비자가 fatal과 비치명을 구별할 수 있다. 이미 표식이 있으면 덮어쓰지 않는다.
  - 허위 오류 없음: provenance가 성공한 eligible fixture에서는 `error`·표식 어느 쪽도 만들지 않는다.
  - **판정 불변식 유지:** production BLOCKED에서 cleanup·validator가 PASS여도 `required_inputs=False`,
    후보 `overall=BLOCKED`, verdict `error=None`, baseline `overall=FAIL`. 표식은 verdict에 실리지
    않으며(`production_provenance_error` 미등장) 판정 입력이 아니다. 표식이 있어도 정당한 전원 PASS
    run의 `overall=PASS`를 막지 않고, fatal `error`는 전원 PASS여도 `overall`을 BLOCKED로 만든다.
  - **fail-closed 추가 확인:** 필수 태그 `menu` 또는 `production`이 빠지면 `required_inputs=False`,
    `overall=BLOCKED`. (probe 1차 실행에서 `menu` 누락으로 예상 PASS 단언이 실패했고, 원인은
    probe의 fixture 결함이었다. 소스 결함이 아니며 오히려 fail-closed 술어를 재확인했다.)
  - **N1/N2/R1~R4 무회귀:** 후보 `trace_dir/evidence.json` 최종 write 1회(`:3671`), baseline
    `g1_dir/evidence.json` 최종 write 1회(`:3245`), `owner0_hq_type`은 UNKNOWN provenance이고
    type 49 고정 술어 없음, R5 술어 `count>=1`/`count>=2` 무변경.
  - **추가 관측(결함 아님, 후속 카드 불필요):** `tools/check_runtime_evidence.py`,
    `tools/check_g1_presentation_trace.py`, `checks/*.py` 어디에도 `evidence["error"]`를 fatal로
    읽는 자동 소비자가 없다. N3가 겨냥한 오독 위험은 **사람/보고자 측에만** 존재하며, 따라서
    기계 판독 가능한 표식 추가로 충분하고 체커 수정은 필요 없다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 1단 기계 게이트와 2단 독립 검수는 이 바퀴로
  통과했다. 남은 위험은 전부 제품 측이다 — G1 실제 원본/후보 비교 증거 없음, WM_CLOSE teardown
  결함, random seed 미노출, minimap 절대 목적지 미비교, G2~G4 제품 증거 없음.
  **R5와 Stage B 재실행(승인 소진)은 새 사용자 승인이 필요하며 모델이 결정하지 않는다.**
  N3 완료로 **승인 없이 진행 가능한 안전 작업 큐가 비었다.** loop/PROMPT.md ④.6에 따라 STOP한다.
- 다음 한 가지: 사용자 승인 대기. 승인이 오면 Stage B 재실행 **전에** 사전 게이트(원본 해시,
  safety, fresh prefix/display, 예산)를 먼저 걸고 R5 적용 여부를 승인 문구대로 확정한다.
