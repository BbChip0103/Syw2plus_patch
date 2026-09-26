# 2026-09-12 | lap 322 | 목표 G1 (M1) — §13 실행 봉투 문서 심사

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  middle tier(중간계획·컨펌). 게임 코드 직접 수정 0, work 구현 대행 0, 다른 모델 호출 0.
  사용자 runtime 표기 lap=321이나 읽기 전용 `loop/.lap_counter`는 **322**다. counter에 쓰거나
  복원하지 않았다(PROMPT 규칙). MODEL_ROUTING의 middle=Opus5/high와 상위 지시의 Sol/Opus5 허용
  차이는 이전 lap 처리와 같이 명시 보존했고 설정은 수정하지 않았다.
- 가설 / 사용자 관찰: §13의 여섯 제출 행은 이전 lap probe를 **재사용하지 않고** 독립 재유도하면
  판정이 갈리는 행과 측정 방법 자체의 결함이 함께 드러난다. 사용자 신규 관찰 없음
  (INBOX 처리 대기 1건은 보고 주기 지시이며 이 바퀴 범위를 바꾸지 않는다).
- 예상 PASS / FAIL 조건: PASS = 여섯 행 전부에 근거 파일·확정 사실·UNKNOWN·판정·해소 조건이
  붙고, 새 probe가 failures=[]로 두 번 동일 출력을 내며, 필수 게이트가 정상이고, 상위 반환분이
  **관측만 하는 최소 봉투**로 한정된다. FAIL = 후보 A/B를 절대 좌표로 승격하거나, 과거 새 게임
  소요를 save 로드 실측으로 쓰거나, PS5→PS3를 PS35→PS3로 넓히거나, runtime 예산을 요청하는 것.
- 변경 파일 / source fingerprint / 커밋: 전부 **uncommitted**(`LOOP_ALLOW_COMMITS` 미설정, 커밋/푸시 0).
  - `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §14 추가 (539→740줄)
  - `docs/history/laps/probes/20260912_lap322_middle_runtime_envelope_review_probe.py` (신규)
    `14dd9768a6bc36077d0c0748408a12a003b2847b4968edf2f02584d294b051a3`
  - `docs/STATUS.md`, `docs/history/laps/20260912_status_lap321_compaction.md`, 본 기록,
    `loop/ESCALATE_SOL`, `logs/lap322/` 검증 근거
  - **수정하지 않은 것:** `tools/`, `patches/`, `tests/`, 기존 probe, EXE/DLL/assets,
    pin/baseline/golden, comparator/producer/endpoint/PASS 규칙, 하네스.
    `make check` 테스트 수가 361로 불변인 것이 이 무변경의 기계 증거다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `game.exe` = `syw2plus_original.exe` =
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` **불변**.
  후보 없음. 환경 = 정적 읽기·문서·Fast. 활성 인원/지도/군대 = **N/A**(게임 실행 0).
  읽은 fixture: `save000.dat` 3,093,902 B `1c703551…629e719da`,
  `save006.dat` 3,437,942 B `616b7997…9289a0d064`,
  `save011.dat` 1,982,062 B, `save012.dat` 1,985,822 B,
  `yfnt/saveloadtitle.spr` 102,260 B `7d154cdb…c08a5c5`,
  공유 temp `*title_before_menu*.png` 14장(단일 SHA `277a0b23…9ce5b252`, 전부 800×600).
  전부 읽기 전용 접근이며 원본·참고 트리 쓰기 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 docs/history/laps/probes/20260912_lap320_middle_lap319_f1_review_probe.py`
    → `logs/lap322/lap320_probe_recheck.json`
    `3d0022b88d694fd1a17c76073d47622c796bab2be188a90d83d325f0a24f60da`, rc=0, stderr 0 B,
    failures=[] — lap320 저장 report 및 lap321 recheck와 **byte-identical**.
  - `python3 docs/history/laps/probes/20260912_lap322_middle_runtime_envelope_review_probe.py`
    → 저장 report `logs/lap322/runtime_envelope_review.json`
    `7d04b9b2ceaace6f29c09f615476cb95491020e3a476b048a2783514e35757ac`, rc=0, stderr 0 B, failures=[].
    **provenance(숨기지 않음):** §14 추가 **전** 실행분의 stdout SHA는
    `bcf4f0a9b719c17579a9737cf34c16d2ccd83056a54f96e86d7cf6f67f3c3674`였고 그때도 연속 2회 동일했다.
    §14를 계약 문서에 덧붙인 뒤 재실행하면 probe가 보고하는 `contract_sha256`만
    `5d51a73f…47f7460e`→`b5b54f56…83df1e95`로 바뀐다. **두 출력의 차이는 이 한 키뿐이고**
    측정된 모든 사실과 `failures=[]`는 동일하다(JSON 키 단위 대조로 확인). 최종 트리 상태와 일치하도록
    나중 실행분을 저장 report로 두고, 앞선 SHA는 이 줄에 보존한다.
  - `make check` → `logs/lap322/make-check.log`, **361 passed in 63.92s**,
    Ruff/compileall/mypy/CONTEXT_PASS, rc=0.
  - `bash checks/safety.sh check` → `logs/lap322/safety.log`, **SAFETY_PASS**, rc=0.
  - 새 캡처/PNG 생성 **0**. 게임/Wine/Xvfb/Stage B/클릭/runtime 예산 **0**.
- 측정값 / 판정:
  - **행별 판정(§14.0):** fixture **REJECT** / §5(a) **부분 ACCEPT**(위치·라벨 한정) ·
    §5(c) **REJECT** / 하네스 경계 **REJECT** / §5(b),(e) 예산 **REJECT** /
    §5(d),§6 실패 보존 **ACCEPT-WITH-CONDITION** / 수용 패키지 **REJECT(패키지)**.
  - **새 확정 1 (§14.3):** `saveloadtitle.spr` 헤더 `[9, 320, 310, 1]`. 같은 중심식을 두 화면
    전역 쌍에 대입하면 `((800-320)//2,(600-310)//2)` = **(240,145)** = 후보 A,
    `((640-320)//2,(480-310)//2)` = **(160,85)** = 후보 B. 즉 **A/B는 두 가설이 아니라 하나의
    식을 두 전역값에 대입한 결과**이고, 선택은 구성 시점 `ds:0xE5BF1C/0xE5BF20` 값과 동치다.
    후보 A를 절대 좌표로 승격하지 **않았다**.
  - **정정 N6 (§14.4, 수치 영향 0, 판정 불변, 규칙 완화 아님):** lap284 probe의 두 가드가
    fail-open이다. `ps_states_waited`의 `get("ps") == N` 정규식은 **집합 소속 대기**를 못 봐,
    하네스가 line **3466·3902**에서 실제로 `item.get("ps") in {4,5,6}`을 대기하는 것을 놓친다
    → "PS 대기값 {3,5,7,9}뿐"은 **불완전**하고 형태 무관 AST 비교 집합은 **{3,4,5,6,7,9}**다.
    같은 이유로 `ps35_references`는 `item.get("ps") in {35, ...}` 형태를 **탐지하지 못한다**
    (probe `guard_fail_open`이 실제 줄과 가상 PS35 줄로 시연). **결론은 살아남는다** —
    "PS35 참조 0"은 이 바퀴가 형태 무관 스캔 `bare_35_occurrences=0`으로 재성립시켰다.
    값은 옳았고 근거가 약했다. lap284/lap298 원문은 고치지 않는다.
  - **정정 2 (§14.6, 수치 영향 0):** §5(d)의 "현 flush는 stage 단위로 묶여 있다"는 과소 표기다.
    `_g1_flush_input_stage` 호출 지점은 **9개**(2024, 2523, 2545, 3383, 3392, 3562, 3874, 3895,
    3930)이고 매 입력 기록마다 불린다 → flush 주기는 **레코드 단위**. 필요한 것은 새 flush
    주기가 아니라 **새 필드**다.
  - **새 확정 2 (§14.5):** 단계 예산 기구가 **이미 존재**한다 —
    `G1_INPUT_STAGE_BUDGETS={unit_select:10.0, drag_select:10.0, minimap:10.0}`,
    4값 `stage_budget_state`, `G1_INPUT_MAX_TRUNCATION_RATIO=0.25`. `runtime_env.py:2202-2205`가
    그 25%를 "측정이 아니라 설계 가정이며 첫 Stage B run이 실측해 재평가해야 한다"고 스스로
    선언해 둔다. 따라서 §5(e)는 예산 **발명**이 아니라 기존 표에 로드 단계 키를 더하고 그 값이
    가정임을 선언하는 문제로 다시 써야 한다. (b)의 3 MB 로드 소요는 **측정치 0**이며 과거
    8.4~19.1초는 **새 게임** run이라 대체로 쓰지 않았다.
  - **하네스 미배선:** `(296,505)`는 `runtime_env.py`에 **0회** 등장. 문서 전용 후보 유지.
    새 probe는 이것이 배선되면 FAIL하도록 단언을 걸었다.
  - **이전 바퀴 검수(PROMPT ④.2):** lap321이 주장한 lap320 fresh 재현을 **직접 재실행**해
    stdout SHA `3d0022b8…a24f60da`가 byte-identical임을 확인했다. 이는 재현성 확인이며
    새 독립 알고리즘 검수가 아니다(lap320 middle이 이미 수행한 것을 반복하지 않았다).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 회귀 0. `make check` 361 passed·SAFETY_PASS·원본 SHA 불변. 테스트 수 불변이 하네스/테스트
    무변경의 기계 증거다.
  - **남은 위험 (전부 보존, 고쳐 쓰지 않음):** §14.3의 **정적 지렛대 소진** — 이 tier는 대화상자
    origin을 더 좁힐 남은 정적 수단을 특정하지 못했다. N2(call 31개 fall-through)가 유지되는 한
    cross-function writer와 실행 순서는 원리적으로 미증명이고 lap310이 포인터 테이블 경유 근거를
    이미 0건으로 닫았다. 이것을 정적 CFG 무기한 재개 사유로 쓰지 않는다.
  - N6와 flush 표기 정정은 어떤 과거 수치도 바꾸지 않으며 어떤 판정도 뒤집지 않는다.
    두 정정 모두 **가드를 조이는 방향**이고 PASS를 완화하지 않는다.
  - N4 수리 **선행 조건으로 지정하지 않음**(lap319/320 probe를 실행 게이트로 채택하지 않았으므로
    §13.2 조건 미충족). W3 재pin **승인하지 않음**(§13.3 유지). pin/baseline/golden 무변경.
  - 독립 검수: **미완**. 이 절은 다음 새 middle이 독립 검수한다. 자기 승인 없음.
  - 사용자 마일스톤 승인: **없음**. `make check` 361 passed와 probe exit0은 계획 승인도 제품
    검증도 아니다. G1~G4 제품 미완료, S1 종결 REJECT 유지.
- 다음 한 가지: `docs/STATUS.md` 참조. 이 기록은 새 활성 큐를 만들지 않는다.

## 부록 A — lap321 `loop/ESCALATE_SOL` 원문 (소비)

수신 시 SHA `761275fb17a814ab2003c272399e887a57ae6e7159d12986ba97c587f01297dd`.

```
lap=321
role=Astra major direction/master-plan
reason=로드 절차·구성 시점 좌표·실행 봉투의 구현 근거 미확정; 계획 인계이며 마일스톤 마감 아님.
handoff=docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md §13
next=새 middle이 §5(a)~(e), fixture 선택, 연구 evidence 분리, 실패 flush/종료와 예산을 행별 판정. 관측 필수 항목은 최소 봉투로 상위 반환.
constraints=게임 코드 변경 0; runtime/Stage B/Wine/Xvfb/클릭 0; N4 수리 및 W3 재pin 보류; 기존 미결 유지.
approval=상위 방향 RECORDED, middle 수용 PENDING; process exit0은 승인/제품 검증 아님.
```

이 요청은 §14로 **소비됐다**. 여섯 행 전부 판정했고, 관측이 필요한 1건은 §14.7의 최소 봉투로
상위 반환한다. 이번 바퀴의 새 `loop/ESCALATE_SOL`은 그 반환 표식이다.


## 최종 검증과 보존

- `make check`: **361 passed in 59.09s**, Ruff/compileall/mypy/CONTEXT_PASS, rc=0 (문서 변경 후 재실행).
  테스트 수가 lap320·lap321과 같은 **361로 불변**인 것이 tools/tests/probe 무변경의 기계 증거다.
- `bash checks/safety.sh check`: **SAFETY_PASS**, rc=0. 필수 게이트 예상 밖 실패 **없음**.
- `tools/runtime_env.py` SHA `dd2ad043…2ac8500190` 불변, 원본 `game.exe` `b56986e0…c9c08a8ac` 불변.
- STATUS 최종 **130줄**, `## 지금 막힌 것 (Blockers)` 제목 정확히 **1개**. 갱신 전 127줄 원문과 SHA는
  `20260912_status_lap321_compaction.md`(`95763bc2…7bc4cba09`)에 보존했다.
- 변경 문서·인계 표식·검증 로그의 최종 SHA는 `logs/lap322/final_sha256.json`에 저장한다.
  해시 장부 자체의 자기 해시는 넣지 않는다.
- 커밋/푸시 **0**(`LOOP_ALLOW_COMMITS` 미설정). 전부 uncommitted로 남겨 다음 세션이 검수한다.
- **이 바퀴가 승인한 것은 없다.** 계획 독립 수용, runtime 실행, 제품 G1 합격은 전부 미검증이다.
