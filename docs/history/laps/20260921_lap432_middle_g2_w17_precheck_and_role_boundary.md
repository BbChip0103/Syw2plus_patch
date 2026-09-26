# 2026-09-21 | lap 432 | 목표 G2

- **실제 provider/model/effort / 지정 역할:** Claude Code `claude-opus-5` / high / **middle(진단·계획·확인)**.
  게임 미실행, 제품 코드 변경 0, 커밋 0, **이번 회차 source 미변경**.

- **가설 / 사용자 관찰:** 없음(새 가설을 세우지 않았다). 이번 lap은 두 가지만 했다 —
  (a) PROMPT ④.2에 따른 직전 바퀴(lap431 middle) 증거의 독립 재확인,
  (b) 아직 실행되지 않은 W17 카드가 **실행 전에** 판정식 결함을 갖고 있는지 확인.
  **역할/큐 불일치가 이번 lap의 1차 사실이다**: STATUS「다음 한 가지」는 W17 P-M을
  **work(Sonnet5/high) 동기 실행 1회**로 지정했는데 이번 세션은 middle로 지정됐다.
  PROMPT ④.3 / MODEL_ROUTING「계획·컨펌 역할은 직접 구현하지 않는다」에 따라 실행하지 않았다.

- **예상 PASS / FAIL 조건:**
  - PASS = lap430 원시 438표본을 lap430/431 코드를 쓰지 않고 새로 재계산했을 때 lap431이
    ACCEPT한 수치·정정 C1/C2/C3이 **불일치 0**으로 재현된다.
  - PASS = N45(`rep movsd` 567 / `mov ecx,3` 26 / 선행 16B 내 동반 0)가 핀된 바이너리에서 재현된다.
  - FAIL/보고 = W17의 (L1)~(L4)가 실제로 서로소가 아니거나, 카드가 수집하기로 한 데이터만으로는
    카드가 요구한 배제 규칙을 계산할 수 없다.

- **변경 파일 / source fingerprint / 커밋(없으면 uncommitted):** 전부 **uncommitted**
  (`LOOP_ALLOW_COMMITS` 미설정, 기본 0). 제품/패치 source는 **한 줄도 바꾸지 않았다**.
  - `docs/history/laps/20260921_lap432_middle_g2_w17_precheck_and_role_boundary.md` (이 파일, 신규)
  - `docs/work/active/G2_UNIT_700_WRITER_POOLWIDE_DIFF_LAP431.md` (**§9 추가만**, lap431 원문 무삭제)
  - `loop/ESCALATE_SOL` (**§19 추가만**)
  - `docs/STATUS.md` (갱신)
  - 검수 산출물 `temp/Syw2plus_patch/g2_capacity/20260921_lap432_middle_review/`
    - `recompute432.py` `f1bb83026836cb8ff2a1a61e03e2867ec5fcbc95714f6e92b29dd8c436e7ea9d`
    - `recompute432.out` `fbe8fd411c06c9db869ec60c24b8874719d17cc22e88b1b63568199cf99b0942`
    - `detail432.out` `527a90f4c22fb2c7c92ac7e3a3b2b56f210c6421729a7fb5f562567486d5b166`
    - `n45_432.out` `3e2d229df4f1ff4ab00a7b71fb01f2c33fc499351af4c625bba9380b5aaca4c8`

- **원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:**
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — `checks/safety.sh`
  결과에 기대지 않고 `sha256sum Syw2plus/syw2plus_original.exe`로 **직접 재해시**해 불변 확인.
  후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`.
  이번 lap은 **게임을 실행하지 않았다** — 재계산 대상은 lap430이 남긴 원시
  `samples.jsonl`(op7 resource-only / 8 owner / N=4001 / seed42)뿐이다.
  정적 대조 대상은 lap424가 핀한 `original.bin`/`candidate.bin`(각 1,032,192B)이고 두 파일의
  sha256 앞자리가 위 원본/후보 SHA와 일치함을 이번 lap이 직접 확인했다.

- **실행 명령 / 로그 / 캡처 경로 및 해시:**
  - `python3 20260921_lap432_middle_review/recompute432.py 20260921_lap429_unit_700_corruption_extent_prep/samples.jsonl`
    (lap430 산출물은 lap429 prep 디렉터리에 기록됐다 — 경로 주의)
  - 인라인 파이썬 2건(창 내용/band 커버리지, N45 재유도) → `detail432.out`, `n45_432.out`
  - `checks/safety.sh check` → `SAFETY_PASS`
  - `python3 -m pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
    patches/population/test_runtime_bridge_contract.py -q` → **6 passed in 51.67s**
  - 통합 `make check`는 **생략**했다. 근거: **이번 회차에 source를 바꾸지 않았다**(INBOX 2026-09-20
    21:58 규칙 + lap412 N22 단서). 디스크 여유 306G.

- **측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):**

  **① lap431 독립 재확인 = ACCEPT(불일치 0).** 438표본, tick 17~10527.
  - 슬롯3565 창 `[0x6e0,0x720)` 변화점은 **정확히 2개**: `s305/t10233 +0x70c 0→0xFFFFFFFF`(스폰),
    `s354/t10400`의 idx6·7·8 = `+0x6f8`/`+0x6fc`/`+0x700`가 `0→{17,16538,22432}`.
    양옆 idx5(`+0x6f4`)·idx9(`+0x704`)는 전 구간 **변화 0회**.
  - `win[8]==K` 불일치 **0/438**, `win[7]==sib` 불일치 **0/438**, `src(+0x388)` 비0 **0/438**.
  - 가드-스킵 **84건**, `s354..s437` **연속**(빈틈 없음) — lap431 수치 그대로.
  - `m`은 `s355/t10400`에 `0→347349` 단 1회, `f688`은 `s305`에 `0→10`, `s355`에 `10→19679`.
    `(10+347349) mod 65536 = 19679` 일치.
  - **C1 재확인(강화):** 대조 슬롯3562는 129표본 내내 **distinct window 1개**,
    `[0]*11+[0xFFFFFFFF]+[0]*4`, 변화 0회. 그리고 3565의 `s353`(전이 직전) 창과
    **완전히 동일한 리스트**임을 직접 비교로 확인 — lap431의 "바이트 동일" 서술 PASS.
  - **C3 재확인:** `run_summary.final_tick=10493` ≠ 마지막 표본 tick **10527**.

  **② N45 독립 재유도 = ACCEPT.** 핀된 바이너리에서 직접 계수 —
  후보 `rep movsd`(`f3 a5`) **567** site / `mov ecx,3`(`b9 03 00 00 00`) 즉치 **26** site /
  movsd 앞 16B 안에 그 즉치가 있는 것 **0**. 원본은 **562 / 26 / 0**.
  lap431이 이를 "정적 후보 없음"으로만 쓰고 반증으로 과장하지 않은 것도 원문 대조로 확인
  (`ecx` 동적 계산 가능성을 §2에 명시) — **ESCALATE_SOL §18 3번째 확인 요청 = 충족**.

  **③ 신규 정정 N46 — "band anomaly 0"은 전이 구간을 덮지 않는다(FAIL of coverage, 측정은 무효 아님).**
  lap430/431/STATUS가 모두 "band anomaly 0"을 보고했으나 커버리지가 세 겹으로 제한된다.
  - `BAND_SCAN_INTERVAL_S = 1.0`(벽시계)인데 dense 표본 간격은 `DENSE_INTERVAL_S = 0.02`다.
    ⇒ dense 표본 **126개 중 123개에 `band_scan` 레코드가 아예 없다**(전체 438 중 124개 없음).
    전이 이웃 `s347..s355`(tick 10395~10400)는 **전부 band_scan 없음**이고, 재개는 `s356/t10402`다.
  - `band_scan`은 슬롯을 `range(1, CAPACITY, 4)`로 **1/4만** 훑는다. 3565는 포함되지만
    **대조 슬롯 3562는 스캔 집합에 없다**.
  - `band_scan`이 읽는 것은 `MOVE_OFFSET=0x692`의 **2바이트 move 필드 하나뿐**이고 판정은
    `|move|>100`이다 — **`[0x6e0,0x720)` 창은 한 번도 보지 않는다.**
  ⇒ **"현상은 슬롯3565에 국한된다"를 지탱하는 증거는 사실상 대조 슬롯 3562 하나뿐이다.**
  이는 W17을 무효화하지 않고 오히려 **정당화**한다. 다만 갈래 **(L3)("창이 애초에 조용하지
  않다")은 '먼 가능성'이 아니라 현재 데이터로 전혀 배제되지 않은 살아 있는 갈래**이며,
  W17 §8이 (L3)에 붙인 "수리 전 보고" 조건은 **실제로 발동할 수 있다**.

  **④ W17 실행 전 결함 2건(카드 수리 필요, §9로 발행).**
  - **D-A: (L1)과 (L3)이 서로소가 아니다.** 둘 다 `|S|>=2`를 허용하는데 카드는 "차분이
    일정하거나 작은 집합"(L1)과 "많은 슬롯에서 상시 바뀐다"(L3)를 가르는 **수치 문턱을 주지
    않았다**. 예컨대 전이 tick에 stride 4로 300슬롯이 바뀌면 두 갈래 모두에 해당한다.
    덧붙여 (L1)의 조건 자체가 서로 다른 둘의 OR("차분 일정" ∨ "작은 집합")이고, 카드가 약속한
    산출물(`stride`=범인의 인덱싱 서명)은 **앞쪽에서만 정의된다**.
  - **D-B: 스폰 배제 규칙이 P-M 수집 데이터만으로는 계산 불가능하다.** §3은 C2에 따라
    `alive` false→true 표본의 `+0x70c=-1` 변화를 집합 `S`에서 빼라고 하지만, P-M은 슬롯당
    **창 64B만** 자르므로 diff 항목에 `alive`가 없다. 다행히 probe는 이미 매 표본
    `read_existence(pid)`로 존재배열 전체를 읽고 있다 ⇒ 수리는 **diff 항목에 그 배열의
    `alive[slot]`을 함께 적는 한 줄**이다. 반영하지 않으면 스폰 잡음이 `S`를 오염시킨다.

  **판정 요약:** ① PASS(ACCEPT) / ② PASS(ACCEPT) / ③ 신규 정정 N46 / ④ 카드 수리 2건 발행.
  **G2 제품 판정은 변화 없음 — 여전히 미완료다.** 이번 lap은 실행 증거를 **0** 늘렸다.

- **회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:**
  - 회귀 없음(제품 source 무변경, targeted 6 passed, 원본 직접 재해시 불변, `SAFETY_PASS`).
  - **남은 위험 1 — 진행 정체가 규칙 경계에 닿았다.** lap431(middle, 실행0)에 이어 lap432도
    실행 0이다 ⇒ PROMPT ③ "제품/바이너리/실제 실행 증거가 하나도 늘지 않는 회차 연속 최대 2회"의
    **2회째를 소진**했다. 다음 회차가 또 실행 없이 끝나면 3회째이며, 그 전에
    **strategy(Astra/Fable) 판정이 선행 조건**이다. 그런데 그 판정은 ESCALATE_SOL §18 항목1로
    이미 요청됐고 **아직 답이 없다**. 이번 lap이 그 요청을 §19로 승격·재확인한다.
  - **남은 위험 2 — 진단 사슬 길이.** W10(lap414)부터 lap432까지 제품 코드 변경 **0**이다.
    W17 §8은 스스로를 "진단 사슬의 마지막 한 장"으로 규정했다.
  - 독립 검수: 이번 lap 자체는 **lap431에 대한 독립 검수**다(작성자 분리 충족: lap430 work →
    lap431 middle → lap432 middle, 서로 다른 세션/컨텍스트). 이번 lap의 ③④는 다음 세션이 검수한다.
  - 사용자 마일스톤 승인: **없음**. 어떤 목표도 PASS로 승격하지 않았다.

- **다음 한 가지:**
  **work(Sonnet5/high)가 W17 §9 정정을 반영한 P-M+rider를 동기 1회 실행한다.**
  이번 회차는 **반드시 실행 증거 회차**다(연속 2회 경계 소진). 다만 그 work 회차를 배정하기
  전에, 또 다른 non-execution 회차가 필요해지면 **strategy 판정이 선행**한다(`ESCALATE_SOL` §19).
