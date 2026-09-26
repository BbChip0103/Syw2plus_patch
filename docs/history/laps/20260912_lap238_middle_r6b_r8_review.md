# 2026-09-12 | lap 238 | 목표 G1 Stage B — R6-B-R8 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high,
  middle tier(진단·계획·컨펌). 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap237 work가 넣은 읽기 오류 커버리지 임계가 (a)선언한 계약대로
  분류하고 (b)기존 우선순위와 hard FAIL 경계를 보존하며 (c)새 PASS 경로를 만들지 않는지
  게임 없이 독립 확인한다. 커버리지 부족이 무반응 FAIL을 UNKNOWN으로 바꾸는 변경이므로
  "완화로 승인 경로가 생기는가"가 핵심 위험이다.
- 예상 PASS / FAIL 조건: PASS = 4-poll 16가지 오류 마스크 전수에서 실제 분류가 독립 재작성한
  기대식과 전부 일치하고, 무반응 행렬에 PASS가 0건이며, 소비자(record/comparator)가 새 문자열을
  PASS로 승격하지 않고, 변이 주입 시 회귀가 실제로 깨진다. FAIL = 불일치 1건 이상, PASS 승격
  경로 발견, 또는 변이가 잡히지 않는 공허한 회귀.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap238_r6b_r8_review_probe.py`
  `f2b1721ac60716a4e6bcb577e2b573b9b2ad29638a927b35024597964d36cdc3`,
  신규 `docs/history/laps/probes/20260912_lap238_r6b_r8_review_report.json`
  `e58b73b516668d0049c73159809628329069cad66a1727675085d8f713792a54`,
  `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`,
  본 기록. 검수 대상 `tools/runtime_env.py`/`tests/test_runtime_env.py`는 **변경하지 않았다**
  (lap237 fingerprint `528f6319...19bd7c` / `69f49985...9b7c7f051`와 바이트 동일 재확인).
  uncommitted; `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`가 4개 pinning 파일
  (`tools/check_setup.py`, `tools/check_binary_contract.py`, `tools/runtime_env.py`,
  `patches/population/verification_0910/manifest.json`)에서 불변. 후보 없음, 게임 실행 0회,
  Wine/Xvfb 0회, PNG 0장, 활성 플레이어/지도/군대 N/A. fixture는 fake-clock reader 시퀀스이며
  실제 프로세스 메모리는 읽지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `make check` → 257 passed(41.37s), Ruff 통과, compileall, mypy 10 files, `CONTEXT_PASS`;
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`;
  targeted `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'wait_state or
  selection_unavailable'` → 13 passed;
  `.venv/bin/python docs/history/laps/probes/20260912_lap238_r6b_r8_review_probe.py --output
  docs/history/laps/probes/20260912_lap238_r6b_r8_review_report.json` → `AGREES` exit 0.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **R6-B-R8 범위 승인(SCOPE APPROVED)**.
  1) 전수 16-case 행렬 불일치 0. 정확히 `0.25`(오류1/성공3, 읽기 tail)는 `FAIL_NO_EFFECT`,
     오류 0건 무반응도 `FAIL_NO_EFFECT`로 hard 경계가 보존된다. `0.5`/`0.75`는
     `UNKNOWN_STATE_READ_COVERAGE`이고 selection은 `UNAVAILABLE`로 닫힌다.
  2) 마지막 poll이 읽기 실패인 8개 마스크와 전체 실패(1111)는 전부
     `UNKNOWN_STATE_READ_FAILURE`를 유지해 R6(lap232) 우선순위가 퇴행하지 않았다.
  3) 새 PASS 경로 0건. 무반응 16-case에 PASS가 없고, `record()`는
     `predicate_observed = result == "PASS"`로 새 문자열을 PASS로 승격하지 않으며,
     `tools/compare_g1_stage_b.py`는 `result != "PASS"`를 전부
     `UNKNOWN_DISPUTED_ORACLE`→상위 `INCONCLUSIVE`로 닫는다(fail-close 확인).
  4) 부동소수 경계 위험 없음: `errors/attempts == 0.25`는 분모가 4의 배수일 때만 성립하고
     그 몫은 이진수로 정확히 표현된다.
  5) poll 0회 창(pre-poll 작업이 stage 예산을 모두 소모)도 hard FAIL로 새지 않는다.
     truncation ratio >= 1.0 > 0.25 → `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`,
     run deadline clamp 시에는 remaining 0 → `UNKNOWN_BUDGET_EXHAUSTED`.
  6) 비공허성: 5개 변이 전부 targeted 회귀에서 검출(base 13 passed). M1 `>`→`>=` 1 failed,
     M2 분류 분기 삭제 1 failed, M3 selection `UNAVAILABLE` 커플링 제거 1 failed,
     M4 COVERAGE/READ_FAILURE 우선순위 교체 2 failed, M5 임계 비교 상수 False 2 failed.
     각 변이 후 `tools/runtime_env.py`를 백업본으로 원복하고 sha256 동일을 확인했다.
  제품 G1/G2~G4, R6-B 전체, Stage B는 여전히 미승인·SKIP다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap237이 남긴 FINAL BLOCKER(문서 갱신 뒤
  `make check`가 STATUS 188줄 안전 위반으로 13 failed)는 이번 바퀴 재실행에서 해소를 확인했다
  (STATUS 80줄, 257 passed, SAFETY_PASS). baseline/golden/pin/제품 자산 변경 0.
  신규 비차단 발견 2건을 아래 큐에 등록한다.
  - **R6-B-R12**: selection이 `CORRUPTED`이면서 커버리지도 부족하면 `status`가 `UNAVAILABLE`로
    덮여 `CORRUPTED`가 status 필드에서 가려진다. `corrupted_poll_count`와 first/last corruption
    provenance는 남으므로 증거 손실은 아니고 양쪽 다 UNKNOWN이라 완화도 아니다. 상태 결합
    표현(또는 별도 필드)이 필요하다.
  - **R6-B-R13**: 효과가 실제 관측된 return 경로는 커버리지로 gate하지 않는다(의도된 비대칭).
    `read_error_ratio=0.75`에서도 성공 반환이며 비율은 observation에 기록되지만, 이 필드를 읽는
    소비자가 아직 없다. Stage B 보고가 PASS에도 커버리지를 노출하도록 고정할 필요가 있다.
  남은 위험: `UNKNOWN_STATE_READ_COVERAGE`를 blind retry 사유로 쓰면 안 된다. 매 발생마다
  first/last read error provenance를 근거로 남기고 원인을 좁혀야 한다.
  S1/F2-R2, R6-B-R2, WM_CLOSE teardown, 실제 후보 scene/input evidence, G2~G4는 미해결.
- 다음 한 가지: 새 work tier(Luna/Sonnet5 high)가 **R6-B-R9**(reader 직접 실패의 단계 진단)을
  한 건만 구현하고, 그 뒤 R10 → R11 → R12 → R13 → F2-R1 → F3-R1 → F3-R2 → F6-R2 순으로
  한 바퀴 한 건씩 처리한다. 상위/사용자 재결 전 게임 실행, Stage B run, R6-A/R6-C는 계속 금지다.
