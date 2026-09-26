# 2026-09-12 | lap 339 | 목표 G1 (M1, 후보 R1 레인)

- **실제 provider/model/effort / 지정 역할:** Claude Code `claude-opus-5` / high / middle(진단·계획·확인).
  게임 코드 hands-on 수정 없음. 실무 구현은 work tier로 반환했다.
- **가설 / 사용자 관찰:** lap338 Astra의 보존 정책 초안(§2~4)이 lap337 §5 수리 범위와 충돌 없이
  실행 가능한가, 그리고 lap338의 STATUS 길이 FAIL이 미결·반려를 지우지 않았는가.
- **예상 PASS / FAIL 조건:** PASS=기존 pin 변경 0 + 모든 실패 단언의 적용 범위 명시 + 과거 identity
  UNKNOWN 보존 + 현재 계약 검사 누락 0 + 편집 전 원문 바이트/SHA 확인 절차 명시 + 실행 예산 0.
  FAIL=실패 원인이 SHA 드리프트 밖으로 확대되거나 필수 검증이 예상 밖으로 실패.
- **변경 파일 / source fingerprint / 커밋:** 커밋 0 (`LOOP_ALLOW_COMMITS=0`, uncommitted 보존).
  - `docs/work/active/G1_R1_MIDDLE_PROVENANCE_ENVELOPE_LAP339.md` `e5d4b26a…e8509a6a` (신규, 본문)
  - `docs/history/laps/probes/20260912_lap339_middle_lap338_provenance_policy_probe.py` `761aec2f…2f8018b` (신규)
  - `docs/history/laps/20260912_lap339_middle_lap338_provenance_policy_review.md` (이 파일, 신규)
  - `docs/history/laps/20260912_status_lap338_compaction.md` (신규, 직전 STATUS 원문 보존)
  - `loop/ESCALATE_SOL` (lap336 원문·lap337/lap338 부록 **보존**, lap339 부록 추가 — 소비 아님)
  - `docs/STATUS.md` (상태/다음/기록 갱신)
  - **게임 코드·하네스·테스트 변경 0.** `tools/runtime_env.py`와 `tests/test_lap326_r1_load_origin.py`는
    바퀴 시작과 끝 모두 `922a267c…f8a2575` / `c04a6265…d769823`.
- **원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:** 해당 없음.
  **게임 실행 0회, 입력 0회, 메모리 접근 0회, PNG 0장, 후보 artifact 0건.** Wine/Xvfb 미기동.
- **실행 명령 / 로그 / 캡처 경로 및 해시:**
  - `make check` → rc0, **376 passed(58.33s)**, Ruff/compileall/mypy OK, `CONTEXT_PASS`.
    로그 `logs/lap339_middle/make-check.log`(`MAKE_CHECK_RC=0`).
  - `bash checks/safety.sh check` → `SAFETY_PASS`.
  - `.venv/bin/python checks/context_limits.py` → `CONTEXT_PASS` (rc0).
  - `.venv/bin/python -m pytest tests/test_lap326_r1_load_origin.py -q` → **15 passed** (N13 재확인).
  - lap339 probe ×2 + `.venv/bin/python` 교차 → rc0, stdout `3b74cfe20c87a43a82d658e1362352b812a5b48602aa9c91a1975d047c7ad759` 3회 동일. Ruff PASS.
  - lap337 probe ×2 → rc0, stdout `c38a73f1…8cdf46` 동일. lap336 probe → rc0, stdout `9295dfdf…d1593a0f`.
  - `…lap332…probe.py` → **rc1**, failures 2건(둘 다 살아 있는 소스 SHA 단언).
    `…lap334…probe.py` → **rc1**, failures 1건(동일 종류). 재pin·편집 0.
- **측정값 / 판정:**
  - lap338 §2.1 재pin 불허 = **ACCEPT**. 새 근거: 필수 게이트 어느 것도 `docs/history/laps/probes`를
    실행하지 않는다(pytest testpaths=`["patches","tests"]`, ruff 대상 `patches tools tests checks`,
    mypy 명시 파일, safety.sh는 safety.py만). probe가 `gates_referencing_history_probes: []`로 확인.
    ⇒ 두 stale probe의 영구 rc1은 필수 게이트를 깨지도 가리지도 않는다.
  - lap338 §2.2 스냅샷 정책 = **ACCEPT + 5개 구체화 필수**(대상 한정, manifest `historical_identity:
    UNKNOWN`/`covers_execution: false`, 실행·import 금지, 덮어쓰기 금지, 편집 후 재대조). 본문 §2.2·§4.
  - lap338 §2.3 영향표 = **ACCEPT**, 산출물은 본문 §3(A~H 8행).
  - lap338 STATUS 편집 감사 = **PASS**. diff 전량이 `## 다음 한 가지`·`## 바퀴 기록` 두 구역뿐이고
    Blockers/검증 상태는 byte-identical, 삭제된 바퀴 기록 줄은 lap337 압축본 body(130줄,
    `512abde1…8cd5a6`, 독립 재계산 일치)에 원문 보존. **미결·반려 삭제 0건.**
  - R-a **CONFIRMED**(후보 세 이름 `tests/` 출현 0/0/0), R-b **CONFIRMED**(AST: 후보
    `stage_started=launch_started` vs 원본 `r1_ps9` `stage_started=started`, 봉투 §8 "준비/PS9 40초").
  - **N14 = FAIL 1건 (lap338 §3 "현재 계약 검사 누락 0"):** `checks/context_limits.py`의
    `CAPS["docs/STATUS.md"]`는 **180**이고 PROMPT의 **130줄** 계약을 검사하는 필수 게이트가 없다.
    lap338이 만난 131>130 FAIL은 저장소 게이트가 아니라 **스스로 쓴 사전 assert**였다.
    lap323·lap333·lap338 세 바퀴가 손수 길이 검사로 소모됐다. 제안(게이트 조이기)은 승인 대기.
- **회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:**
  - **D행 UNKNOWN 영구:** lap331 run의 "검수 SHA == 실행 SHA" 재확인은 원문 부재로 복구 불가.
    PASS로 승격하지 않는다. W3 재pin 결정도 여전히 미결.
  - **`STAGE_BUDGET_EXHAUSTED` 위험:** R-b 수리 후 40초가 dxwrapper 설치 구간을 포함한다. 설치 비용은
    **실측 전 UNKNOWN**이며, 초과 시 정당한 FAIL로 기록하고 예산 확대·재시도로 대응하지 않는다.
  - lap336이 올린 세 승격 질문 중 (1)은 lap338 §2.1 + 이번 §2.1 근거로 **좁혀졌으나 W3는 미결**,
    (2)(3)은 lap338 §2.2/§2.3 + 이번 §4로 **절차가 정의**됐다. 최종 Astra/사용자 확정은 대기.
  - **자기 probe 결함 공개(수치 영향 0):** 초안 probe가 STATUS의 **특정 압축본 파일명**을 단언해
    STATUS 갱신 직후 FAIL했다. 이 봉투가 금지한 **전이 단언**의 재발이므로 이름 대신 **연결 자체**
    (가리킨 압축본 존재 + 헤더 SHA/줄 수가 자기 body와 일치)를 단언하도록 고쳤다. 최종 probe는 rc0.
  - **이 문서는 자기 승인이 아니다.** 다음 새 세션이 독립 검수한다. 제품 G1/Stage B/마일스톤 승인 0.
- **다음 한 가지:** work tier(Luna/Sonnet5 high)가 본문 §4 스냅샷을 먼저 만들고 §6대로
  R-b 인자 한 곳 + R-a/R-b 오프라인 잠금만 수리한다. 후보 실행은 여전히 **0회**.
