# 2026-09-12 | lap337 | 목표 G1 (후보 R1 관측 레인)

- **실제 provider/model/effort / 지정 역할:** Claude Code `claude-opus-5` / high /
  **middle(진단·계획·확인)**. 게임 코드/하네스 hands-on 수정 0. `docs/MODEL_ROUTING.md` 준수.
  **lap 번호 주의:** 루프 런타임 배너는 `lap=336`을 찍었으나 `loop/.lap_counter` 파일 값은 **337**이고,
  `loop/PROMPT.md`는 "현재 파일 값이 이번 runtime lap 번호"라고 못박는다. 또 lap336 기록은 이미
  존재한다. 따라서 이 기록은 **lap337**이다. 에이전트는 카운터를 읽기만 했고 쓰지 않았다.

- **가설 / 사용자 관찰:** STATUS의 「다음 한 가지」는 lap336 §3의 R-a·R-b 수리이며 이는 **work tier**
  작업이다. 이번 세션은 middle이므로 구현하지 않는다. middle이 이 바퀴에 더할 수 있는 값은
  (i) ④2가 요구하는 직전 바퀴 증거의 독립 재현과 (ii) lap336이 **산문으로만** 남긴 R-a·R-b의
  수리 형태를 — 특히 R-b의 두 선택지 중 하나를 — **근거와 함께 확정**해 work tier의 모호성을
  제거하는 것이다. `loop/PROMPT.md` ④5의 "승인 필요 항목은 큐에 올리고 독립 작업을 진행한다"에 해당한다.

- **예상 PASS / FAIL 조건:** PASS = lap336 probe rc0·stdout SHA `9295dfdf…d1593a0f` 재현 +
  `make check` 376 passed + SAFETY_PASS + 검수 기준선 두 SHA 일치 + R-a·R-b 결함의 독립 재유도 성공.
  FAIL = 위 중 하나라도 불일치. 어느 쪽이든 후보 실행 예산은 0회를 유지한다.

- **변경 파일 / source fingerprint / 커밋(없으면 uncommitted):** 전부 **uncommitted**
  (`LOOP_ALLOW_COMMITS=0`, 저장소에 커밋 0건 상태 유지).
  - `docs/work/active/G1_CANDIDATE_R1_MIDDLE_REPAIR_SCOPE_LAP337.md`
    `df31b80721f668f1359de03a27b8511c161d5c47df7299b1cb2b87c83821bfc3` (신규, 본문)
  - `docs/history/laps/probes/20260912_lap337_middle_lap336_repair_scope_probe.py`
    `1dd47cd3ede36c03168ed5910ed71356488f227d18e3e78fe050c83cdcbbc545` (신규)
  - `docs/history/laps/20260912_status_lap336_compaction.md`
    `1a9607b73fe4a8022b94ee4383e9c0eb94c596bdcceba20220101e1c5ba0b5f7` (신규; lap336 종료 STATUS 원문
    `70e3c2ede2c8eca053621ca5fbdae5f7c2a781936cc3db1d3547e6f6834825ff`·130줄 보존, 왕복 재계산 일치)
  - `docs/history/laps/20260912_lap337_middle_repair_scope_and_lap336_verification.md` (이 파일)
  - `loop/ESCALATE_SOL` `520732ccd5fb1cc0e59b41c3b3276591480430d501e27c7e228ba1ae6d7674b8`
    (lap336 원문 1~44행 **그대로 보존**, 46행부터 lap337 부록 추가. **소비/삭제 아님**)
  - `docs/STATUS.md` `512abde1f83e4d8588c9c6aead9a70bebf9eb58444d447749fe401689b8cd5a6`, **130줄**,
    `## 지금 막힌 것 (Blockers)` 정확히 1개. 보존본과의 줄 단위 diff는 의도한 7개 구간뿐이며
    미결·반려·provenance 회귀 줄은 하나도 삭제되지 않았다.
  - **하네스 무변경 재확인(편집 후):** `tools/runtime_env.py` `922a267c…f8a2575`,
    `tests/test_lap326_r1_load_origin.py` `c04a6265…d769823` — 세션 시작 시점과 동일.
  **게임 코드·하네스(`tools/`, `patches/`, `tests/`, `checks/`) 변경 0.**

- **원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:**
  게임을 실행하지 않았으므로 원본/후보 run fixture **없음**. 검수 기준선(디스크 실측):
  `tools/runtime_env.py` `922a267c27f51fe47d7db69962dadbfdbbded9ff04c6350e8cb7a4c44f8a2575`,
  `tests/test_lap326_r1_load_origin.py` `c04a6265229f7e37cb9d4434f0e150c76e1e56d26f0e1c990cb938a06d769823`.
  둘 다 lap336 §4가 지정한 다음 기준선과 일치. lap330 값 `997ff15b…cc46eed`는 디스크에 없다.
  전 저장소 artifact: 원본 `r1_load_origin.json` **1건**(lap331 run `20260912_172722_2210599_0`),
  후보 `r1_load_origin_candidate.json` **0건** — 후보 실행 예산 미사용.

- **실행 명령 / 로그 / 캡처 경로 및 해시:**
  - `python3 docs/history/laps/probes/20260912_lap336_middle_lap335_candidate_implementation_probe.py`
    → rc0, `failures=[]`, stdout SHA256 `9295dfdfd9bee0b5dc298946f2348c2a7327961ce81cf4f78d43a6c7d1593a0f`
    (연속 2회 byte-identical). **lap336 기록과 일치.**
  - `python3 docs/history/laps/probes/20260912_lap337_middle_lap336_repair_scope_probe.py`
    → rc0, `failures=[]`, stdout SHA256 `c38a73f1220faf992155bc5a98fe814e9e8ded316b0935e5eb3f22f0738cdf46`
    (연속 2회 + `.venv/bin/python`·`/usr/bin/python3` 교차 실행 전부 동일).
    `.venv/bin/python -m ruff check <probe>` → `All checks passed!`
  - `python3 docs/history/laps/probes/20260912_lap332_middle_lap331_r1_artifact_probe.py` → **rc1**
  - `python3 docs/history/laps/probes/20260912_lap334_middle_candidate_r1_envelope_probe.py` → **rc1**
  - `make check` → rc0, **376 passed (57.26s)**, Ruff/compileall/mypy `All checks passed!`, `CONTEXT_PASS`
  - `bash checks/safety.sh check` → **SAFETY_PASS**
  - PNG 0장. 게임 실행 0회, 입력 0회, 메모리 읽기/쓰기 0회.

- **측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):**
  1. **lap336 재현 = PASS.** probe rc0/stdout SHA, 376 passed, SAFETY_PASS, 기준선 두 SHA 전부 일치.
  2. **N13 = CONFIRMED.** `make check` 출력의 `tests/test_lap326_r1_load_origin.py`는 점 **15개**.
     lap335 기록의 "16 passed"는 부정확하고 lap336의 정정이 옳다. 수치 영향 0.
  3. **lap336 STATUS 보존 = PASS.** `20260912_status_lap335_compaction.md` fenced body SHA를 독립
     계산하면 `bba77d09…c0fc1954`·130줄로 기록과 일치.
  4. **R-a = CONFIRMED(독립 재유도).** 후보 세 이름 문자열이 테스트 파일에 **0건**
     (`r_a_name_assertions_present` 3항 전부 `false`).
     `test_candidate_cli_forwards_separate_artifact_lane`은 CLI 디스패치만 단언한다.
  5. **R-b = CONFIRMED(AST 재유도).** `_wait_state` 호출의 stage 결합을 소스에서 직접 읽으면
     원본 `r1_ps9`는 `stage_started=started`, 후보 `candidate_ps9`는 `stage_started=launch_started`이고
     `launch_started`는 `install_private` **뒤**에 찍힌다. 봉투 §8 "준비/PS9 40초" 미충족.
  6. **신규 사실 — 두 stale probe 실패의 분해.** lap332/lap334 probe의 `failures`는 **살아 있는 SHA
     단언이 전부**이고(각각 2건·1건) 그 밖의 모든 단언은 지금도 통과한다. 따라서 기계적으로 복구
     불가인 것은 "lap331 run의 실행 SHA == 검수된 원문"이라는 **동일성 재확인 한 가지**뿐이며,
     승격 질문 1은 "probe를 버릴지"가 아니라 "죽은 SHA 단언 2~3줄을 어떻게 처리할지"로 좁혀진다.
     **이 좁힘은 결정이 아니다. 재pin은 여전히 금지이고 middle 단독으로 하지 않는다.**
  7. **R-b 수리안 확정 = (a) `stage_started=started`.** (b) "설치 구간 별도 상한"은 준비 합계 상한을
     40초 위로 올려 봉투 §12 **예산 확대 금지**에 저촉되므로 기각. (a)는 원본과 같은 결합이 되어
     §11.1 대칭성을 회복한다. `install_private`는 ini 1개의 read/sha256/write + sidecar 2개뿐이라
     (`patches/resolution/dxwrapper_config.py:115-153`) 40초 예산 압박이 실질적으로 없다.
     변경 범위는 **인자 하나**이고 `stage_timeline` 기록은 그대로 둔다.
  8. **R-a 수리안 확정 = 오프라인 AST 단언만 추가, 프로덕션 코드 변경 0.** 이름을 모듈 상수로
     승격하는 대안은 기각 — 커밋 0 탓에 이미 바이트 diff가 불가능한 원본 경로를 또 건드리게 된다.
  9. **후보 실행 = 0회 (SKIP, 권한 없음).** 발효 조건(수리 + 다음 새 middle 재검수) 미충족.
  10. **제품 G1/G2/G3/G4 = 변화 없음.** 게임 증거 0. 이 바퀴는 제품 진전이 아니다.

- **회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:**
  - 이 바퀴의 판정은 **정적/문서 수준**이다. 후보가 실제 1600×1200에서 원본과 같이 동작한다는 증거는 0건.
  - lap336 §4의 승격 질문 셋은 **미해결**이며 `loop/ESCALATE_SOL`에 lap336 원문 + lap337 부록으로 보존.
  - 위험: 이번에 확정한 R-a 테스트 형태(AST 소스 단언)는 함수 본문 구조에 의존한다. 본문이 크게
    재구성되면 테스트를 손봐야 한다. 다만 **이름 계약**만 보므로 SHA pin류의 영구 실패 함정은 아니다.
  - 범위 밖으로 남긴 것: "관측 15초/종료 15초 확보 미강제"(원본 R1 상속 성질, 별도 카드),
    WM_CLOSE·S1/F2-R2 결정성·G2~G4.
  - 독립 검수: 이 문서는 **미검수**다. 다음 새 세션이 §1의 재현 명령으로 직접 확인해야 한다.
  - 사용자 마일스톤 승인: **없음.** 이 바퀴는 마일스톤을 종료하거나 이동하지 않았다.

- **다음 한 가지:** **work tier(Luna/Sonnet5 high)가
  `G1_CANDIDATE_R1_MIDDLE_REPAIR_SCOPE_LAP337.md` §5 핸드오프대로 R-a·R-b만 수리한다 — 실행 0회.**
  R-b는 인자 한 곳(`stage_started=launch_started`→`started`), R-a는 오프라인 이름 단언 추가,
  둘 다 회귀 잠금을 함께 넣는다. 테스트 수를 정확히 기록한다(N13 재발 금지).
  수리 뒤 다음 새 middle이 재검수해야 후보 fresh 1 run이 발효한다.
