# 2026-09-12 | lap 310 | G1 — lap309 V3(R2/R3/R5) 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / effort=high / **middle(진단·계획·컨펌)**.
  러너 로그 `logs/laps/2026-09-12/lap-0310.log`, `loop/.lap_counter`=310. 게임 구현/hands-on 수정 없음.
- 가설 / 사용자 관찰: lap309 V3가 lap308의 R2(공허한 failure seed)·R3(호출 규약 무시)·R5(caller 단언 부재)를
  실제로 수리했다면, **lap309 코드를 전혀 쓰지 않는 다른 방법**으로도 같은 결론이 나와야 한다.
  특히 R3의 `{0, 4, 16}` cleanup 표는 lap309에서 **리터럴 가정**이므로, 가정하지 않고 **풀어서** 같은 값이
  나오는지가 핵심이다.
- 예상 PASS / FAIL 조건: (a) lap309 산출물 3개와 원본 EXE SHA 불변, (b) lap309 probe fresh 재실행이 저장된
  report와 byte-identical, (c) 독립 probe에서 failure seed `0x431AF4`가 `0x431AF2 jne`의 fall-through이고
  그 블록에 화면 전역 피연산자 0건, (d) join 단일성과 `ret` depth 0만으로 **V=4, I=16이 유일해**로 풀리고
  import 이름이 4인자 stdcall로 교차 확인, (e) entry offset `0x46526D`=4 / `0x465287`=8,
  (f) raw `E8 rel32` 스캔으로 map caller가 정확히 `0x48F538`. 하나라도 어긋나면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `docs/history/laps/probes/20260912_lap310_middle_lap309_v3_review_probe.py`
  (`cb4e6c51f3e59a21a8c7c796f04ba9a5ac0381ce3adaf40e9c24947869f5d933`), 신규
  `tests/test_lap310_middle_review_probe.py`
  (`24ed58d2e3a08850f9e46dae01affde77096b4c673973b964674193825e42497`), stdout report
  `logs/lap310/lap310_middle_lap309_v3_review.json`
  (`d0c8a2b75dad4394c5f7e50a2d077fe745004c25682a591b6f689bf4af3cddb8`), 본 기록, STATUS 압축.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`, uncommitted 보존). lap305/306/308/309 산출물은 **SHA 불변**으로 보존만 함.
  STATUS 압축: 원문 130줄·`c8f118c8…66655540`을 `docs/history/laps/20260912_status_lap310_compaction.md`
  (`d2d04225…8dbe4c4ca`)에 먼저 보존한 뒤 130줄로 재작성(`0f4bc4d8…6da684a514`), `## 지금 막힌 것` 1개 유지.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 검수 전후 불변(`Syw2plus/` 및 형제 원본
  경로 동일 해시). 후보 EXE·활성 플레이어·지도·군대·fixture **없음**(정적 검수). Linux `.venv`,
  PE 직접 파싱(struct) + 대조용 `/usr/bin/objdump` 1회. 게임/Wine/Xvfb/Stage B/runtime/PNG/click **0회**.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  (1) lap309 probe 재실행 → `/tmp/lap310_fresh_v3.json` = `7f2a876f…0d34a79` → 저장본과 `cmp` **byte-identical**.
  (2) `.venv/bin/python docs/history/laps/probes/20260912_lap310_middle_lap309_v3_review_probe.py`
      → `logs/lap310/lap310_middle_lap309_v3_review.json`, exit 0, 2회 fresh stdout **byte-identical**.
  (3) `.venv/bin/python -m pytest -q tests/test_lap310_middle_review_probe.py` → 3 passed.
  (4) `make check` → **297 passed**, Ruff/compileall/mypy/`CONTEXT_PASS`. (5) `bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **판정 = ACCEPT(lap309 V3 수리 CONFIRMED)**.
  - **R2 CONFIRMED(단, 저출력):** `0x431AF2 = 75 0a` → target `0x431AFE`, fall-through `0x431AF4` ✅ 실제 실패
    분기이며 lap308이 지적한 `ret` seed가 아니다. 실패 블록은 `5f5e5d33c05b83c434c3` **10 B**이고 화면 전역
    (`0xE5BF1C`/`0xE5BF20`) 피연산자 **0건**. **한계:** 이 10 B 에필로그에는 메모리 피연산자가 아예 없어
    "writer 없음" 단언 자체는 여전히 저출력이다. R2의 실질 근거는 **성공측 dominator**이며 그것은 lap308이
    이미 독립 재현했다(이번 probe는 재유도하지 않고 바이트 수준으로만 확인).
  - **R3 CONFIRMED(가정→증명으로 승격):** `0x465250..0x4652AE` 27개 명령을 이미지 바이트와 **완전 일치**로
    고정(연속 커버리지 단언 포함). je-경로(path A)는 간접 호출을 지나지 않아 join `0x465287`에서 depth
    `0x100` 고정, call-경로는 `0x104 - V` → **join 단일성이 V=4를 강제**. 이어서 `ret` depth는
    `0x14 - V - I` 이고 `ret`는 depth 0을 요구 → **I=16 강제**. 즉 lap309의 리터럴 `{0,4,16}`은 **유일해**다.
    교차 확인: import slot `0x4E51CC`를 PE import directory에서 직접 해석 → **`MessageBoxA`**(USER32,
    4인자 stdcall) → cleanup 16으로 **독립 일치**. entry offset `0x46526D`=**4**(arg1), `0x465287`=**8**(arg2),
    두 경로 offset도 V 적용 후 일치 → lap308의 `{4,8}`→`{8}` 교정과 lap309 수리 모두 **UPHELD**.
  - **R5 CONFIRMED(범위 확대):** raw `E8 rel32` 전수 스캔 결과 map entry `0x431AB0` 직접 caller **정확히
    `0x48F538` 1개**, dialog `0x4D60B0`는 `0x4D69E5`/`0x4D6A05` 2개. 추가로 **전 섹션 절대 dword 스캔**에서
    두 진입점 주소 리터럴 **0건** → 함수 포인터 테이블/간접 등록 경로가 없다는 근거를 lap309보다 넓게 확보.
  - 보조 대조(objdump): 구간 `0x431AB0..0x4324D6` `ret` **2개**(`0x431AFD`, `0x4324D5`), 앵커 12/12 바이트 일치.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **신규 지적 1 (감사 영향, 수치 영향 0):** `tests/test_lap309_mode_writer_probe.py::test_call_convention_cleanup_is_explicit`은
    `CALL_CLEANUP_BYTES`를 자기 자신과 대조하는 **동어반복 테스트**라 `4`/`16`에 대한 독립 증거를 주지 않는다.
    실질 증거는 같은 파일의 두 번째 테스트(불변식)와 이번 lap310 solver다. 규칙 완화가 아니라 테스트 성격 표기.
  - **신규 지적 2 (의미 정정, 수치 영향 0):** lap305/306이 `0x465250`을 "가변인자 **로깅** 헬퍼"로 불렀으나
    실제로는 `vsprintf`(`0x4DB933`, arg3=포맷) 후 **`MessageBoxA`를 띄우는 메시지박스 헬퍼**다. 291개 push
    site가 기하 writer를 운반하지 않는다는 lap306 R4 결론은 **오히려 강화**된다(문자열/캡션 인자).
  - 자체 결함 1건 수리 후 보고: 초안 probe의 `path_b_offsets_agree`가 V 부호를 반대로 써 `false`를 보고했다.
    부호 교정 후 `true`이며 실패 조건으로도 승격했다. 보고서는 교정본 기준 1종만 남겼다.
  - 남은 위험/UNKNOWN: 계산 포인터·visible body 밖 간접 dispatch, click 시점 실제 mode 값, map↔dialog
    event/thread 순서, WM_CLOSE teardown, 후보 scene/input 증거. **제품 G1 증거는 여전히 0**이며 G2~G4 무관.
  - 승인 상태: 사용자 제품 마일스톤 승인 **없음**. 2026-09-12 01:03 bounded repair→fresh validation 허가는
    제품/출시 승인이 아니다. 본 검수는 2단(다음 새 세션 독립 검수)에 해당하며 3단 사람 판정은 미실시.
- 다음 한 가지: **R2의 남은 저출력 구간을 닫는다** — 다음 work(Luna/Sonnet5/high)가 `0x431AB0` 성공 경로에서
  `0x4324B8`/`0x4324C2` reset writer가 성공 `ret`을 **지배**한다는 결론을 lap308/lap309와 다른 방법(예:
  역방향 post-dominator 또는 모든 성공 경로 열거)으로 재유도하고, 동시에 `0x431AF4` 저출력 단언을
  "실패 시 화면 전역 불변"이라는 **더 강한 단언**(실패 분기 진입 전후 writer 집합 비교)으로 교체한다.
  그 전까지 게임/Wine/Xvfb/Stage B/runtime/PNG/click 실행은 계속 금지.
