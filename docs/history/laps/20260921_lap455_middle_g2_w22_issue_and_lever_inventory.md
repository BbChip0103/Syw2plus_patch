# 2026-09-21 | lap 455 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high — **middle(중간 계획·컨펌)**.
  게임 코드 hands-on 수정 없음. 이번 회차 산출물은 실행 카드 1장 + 정적/재계산 확정 4건이다.
- 가설 / 사용자 관찰: lap454 strategy가 §33-3으로 "다음 middle이 W22 카드를 발행한다"를
  지정했다(카드 §「다음 카드(W22)」 필수 5항목). 이번 회차가 그 발행이다. 가설은
  "lap454가 나열한 레버 목록을 그대로 카드로 옮기기 전에, 각 레버가 **실제로 존재하고
  구속 조건일 수 있는지**를 middle이 정적으로 먼저 걸러야 work 한 바퀴가 낭비되지 않는다".
- 예상 PASS / FAIL 조건: (a) W22 카드가 lap454 필수 5항목을 전부 담고 (b) 판정식이 실행 전
  고정 수치로 적히고 (c) 이전 바퀴(lap454) 핵심 수치의 독립 확인이 불일치 0이며
  (d) 게임 실행 0회·제품 코드 변경 0이면 PASS.

## 1. 이전 바퀴 검수 (PROMPT ④-2)

lap454는 strategy 판정 회차라 새 실행 증거가 없다. 검수 대상은 **판정 문서의 정합성**과
lap454가 스팟체크했다고 주장한 수치다.

- lap454 산출물 2건이 실재하고 내용이 서로 일치한다: 카드
  `G2_STRATEGY_MILESTONE_DIRECTION_LAP454.md`(판정 ①~④)와 lap 기록
  `20260921_lap454_strategy_g2_w21_closure_direction.md`, `loop/ESCALATE_SOL` §33.
  §33-3의 handoff("W22 카드 발행 / W23은 W22 판정 후 / STATUS 「다음 한 가지」는 W22")가
  카드 §「다음 카드(W22)」와 모순 없다.
- **정정 1건(이번 회차가 발견):** lap454 판정①과 §33-1이 레버로 명시한 **「난이도」는 원본에
  존재하지 않는다**(아래 §2-1). 판정의 방향(= bounded probe로 선판정)은 유효하지만 레버
  목록의 한 항목이 무효이므로 W22 카드가 이를 제거하고 근거를 박았다. **판정을 뒤집지 않는다.**
- lap454 스팟체크 수치(live 1,161 / lost0·mismatched0·new0 / owner 장부 8/8)는 lap453과 동일
  주장이며, lap453이 이미 비참조 재계산으로 ACCEPT했다. 이번 회차는 **같은 것을 세 번째로
  재계산하지 않았다**(PROMPT ③ "이미 확인한 증거의 문서 형식 보강만으로 제품 작업을 반복
  차단하지 않는다"). 대신 아직 아무도 계산하지 않은 baseline 궤적을 계산했다(§2-4).

## 2. 이번 회차가 확정한 것 (전부 게임 실행 0회)

### 2-1. 「난이도」 레버 부재 — lap454 레버 목록 1건 무효

`tools/g4_difficulty_absence.py`가 핀된 원본 `b56986e0…c9c08a8ac`에 대해 검사하는 내용:
- 로비 commit 함수 `[0x004B763C, 0x004B76AE)`의 `66 A3` word store 대상이 정확히
  `0x632D54 / D46 / D44 / D4A / D48 / D4C / D42` **7개**(`LOBBY_WORD_TARGETS`).
- 4개 텍스트 레지스트리(`Text_kor.dat`/`TexJ_kor.dat`/`TexR_kor.dat`/`TeJM_kor.dat`)에
  `REQUIRED_LABELS`(전장지도·자동생성·많은 자원·큰 지도·복잡 지형·기본 배경·보통 게임·
  깃발뺏기·시간제한·느리게·보통·빠르게)가 전부 있고 `FORBIDDEN_LABELS`(난이도·쉬움·어려움)는
  **전부 없다**.
- 도구 자신의 결론 문구: *"Original free battle has game-speed and seven lobby settings, but no
  AI difficulty field. Do not invent or search for an Easy/Normal/Hard runtime value."*

⇒ **판정: lap454가 나열한 레버 중 「난이도」는 존재하지 않는다.** W22는 이 레버를 빼고,
work가 정적 역추적을 새로 시작하는 것을 금지했다(카드 §2-1).

### 2-2. 「많은 자원」 레버는 이미 포화 — 최우선 후보가 아니다

lap442 `resource_receipts.json` 원문: op7이 tick 3~8에 8 owner 전원의 rice/wood를
`5000/7500` → **`1,000,000 / 1,000,000`** 으로 올렸다(op7 상한이 1,000,000,
`patches/population/runtime_bridge.c:166-174`). 그런데 24,030 tick 뒤 최고 owner는
`used` **1,698** / `count` **107**(평균 단위비용 15.87)이다.

⇒ 소비된 자원은 1M 예산의 한 자릿수 %이며, 자동생성 「많은 자원」을 올려도 **op7이 이미 지배**한다.

**정직하게 남긴 한계:** lap442 표본 필드는 `live/max_slot_index/owners{cap,count,count_cap,
owner,reserved,used}/rss_kb/sample/t/tick`뿐이고 **rice/wood 시계열이 없다.** 따라서 "자원이
고갈된 적 없다"는 현재 **1M 지급 + 소비량으로부터의 추론**이지 직접 측정이 아니다. 카드 §4-3이
이 구멍을 싸게 막는다 — `ledger()`가 이미 `U32(p+0x14)`/`U32(p+0x18)`로 rice/wood를 읽어
JSON에 넣고 있고(`runtime_bridge.c:99-102`) 샘플러가 버릴 뿐이다.

### 2-3. 시드 고정 시 시뮬레이션은 결정적 — arm 간 잡음 바닥 0

lap413 `20260921_lap413_original_ai_production`과 `..._repro2`의 `used` 8-벡터를 tick별로 대조:

| tick | used (o0..o7) |
|---|---|
| 1076/1079 | `[20,50,50,40,50,40,50,50]` (양쪽 동일) |
| 4087/4089 | `[20,158,198,185,195,260,260,225]` (양쪽 동일) |
| 8102/8102 | `[20,359,523,710,532,878,868,851]` (양쪽 동일) |
| 11928 | `[20,495,593,1010,608,1208,1208,1176]` (양쪽 동일) |

일치하는 모든 tick에서 **바이트 단위 동일**하며, 유일한 차이는 서로 다른 tick에서 찍힌
7098 vs 7099 표본의 owner5(740 vs 750)다.

⇒ **arm 간 차이는 전부 레버에 귀속 가능**하고 임계값에 잡음 여유가 필요 없다.
동시에 **변동성의 유일한 출처는 시드**이므로 시드가 독립 레버(A4)로 남아야 한다.

### 2-4. baseline은 정체가 아니라 감속 — 단순 soak 연장으로 닫히지 않는다

lap442 원시 721표본을 이번 회차에 재계산했다(owner0은 구식 goal이라 `(20,2)` 고정 — N56,
그래서 owner 1~7만 쓴다).

| tick | live | o1 | o2 | o3 | o4 | o5 | o6 | o7 |
|---|---|---|---|---|---|---|---|---|
| 7,986 | 359 | 359 | 550 | 696 | 502 | 863 | 858 | 866 |
| 12,022 | 479 | 510 | 683 | 1001 | 580 | 1193 | 1208 | 1261 |
| 24,030 | 583 | 570 | 1183 | 1111 | 620 | 1333 | 1698 | 1466 |

후반 창(tick 18,026 → 24,030, 181표본) 증가율 `used/tick`:
o4 **0.0033**, o5 0.0083, o1 0.0100, o3 0.0108, o7 0.0133, o6 0.0483, o2 0.0600.
그 증가율로 5,000까지 외삽하면 **63,659 ~ 1,314,876 tick**이 더 필요하고 7명 중 **5명이
265,000 tick 초과**다.

부수: wall-clock 환산 **33.33 tick/초**(24,014 tick / 720.5초) ⇒ 8,000 tick ≈ **4.0분**.
`cap=5000`·`count_cap=1200`은 전 표본에서 구속 조건이 아니다(도달값 `used`1,698/`count`107).

## 3. 발행한 카드

`docs/work/active/G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md` (**W22**).

lap454 §「다음 카드(W22)」 필수 5항목 대응:

| 요구 | 카드 위치 |
|---|---|
| 1. 레버 목록 + 확인 방법 + 레버당 짧은 창 1회 | §3 표(A0~A5, 확인 방법 열) |
| 2. 실행 전 고정 판정식(수치) | §5 (`U_min≥718` ∧ `r_slow≥0.0341 used/tick`) |
| 3. 재빌드 SHA / gate-legal / op4 금지 / 원본 재해시 | §1-4, §9 |
| 4. N71 / N72 / N73 수리 | §8 (각 파일 L648-652 / L613-614 / L495-499) |
| 5. 동기·root 실행, work 자체 lap 기록(N64), 활성 카드 3개 | §9 |

카드가 추가로 박은 것: fail-closed 산출물 `w22_lever_matrix.md`(§6, N66 선례),
`NOT_FEASIBLE` 시 되물음 (ㄱ)/(ㄴ)/(ㄷ) 승격(§7), 게임 속도는 레버가 아님(tick당 경제 불변),
`runtime_env.py:5802-5809` 검증기 파라미터화하되 **기대값 수정/삭제 금지**(§2-7),
`d4a≠0`이 PS=140 dispatch를 깨면 그것이 산출물이고 즉흥 패치 금지(§2-10).

**A0(baseline 재수립)을 필수로 만든 이유:** lap442 baseline은 **구식 goal**(owner0 비활성,
실질 7인)에서 나왔고 W22 arm은 8-AI goal에서 돈다. A0 없이 비교하면 레버 효과와 goal 차이가
섞인다.

**A2(AI 슬롯 8→4)의 역할:** 구속 조건이 지도 공간/경쟁인지 AI 자체 행동인지 가르는 판별자다.
A2 결과로 "4인 합격"을 주장하는 것은 금지했다.

- 변경 파일 / source fingerprint / 커밋: 신규
  `docs/work/active/G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md`,
  `docs/history/laps/20260921_status_lap455_precompaction.md`(STATUS 원문 보존, SHA
  `4d1573eb037ef05941b499980c34a56810e7fdbd4eedc9820a20d3336921b230`, 130줄),
  본 기록, `loop/ESCALATE_SOL` §34 추기, `docs/STATUS.md` 갱신(130→121줄).
  **제품/도구 source 변경 0(N22 충족 — 이번 회차 source를 한 줄도 바꾸지 않았다).**
  커밋 0(`LOOP_ALLOW_COMMITS` 기본 0), 전부 uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재해시 **불변**.
  **게임 실행 0회** — 후보 빌드/ fixture 없음. 분석 입력은 기존 원시 산출물
  (`temp/Syw2plus_patch/g2_capacity/20260921_lap442_repaired_p2_long_soak/`,
  `..._lap413_original_ai_production{,_repro2}`, `..._lap413_stock_ai_control`,
  `..._lap452_w21_step2_save_load_roundtrip/w21_step2_run.py`)과 repo 소스다.
- 실행 명령 / 로그: ① lap442 `samples.jsonl` 721표본 python3 인라인 재계산(궤적·증가율·
  wall-clock) ② lap413 3개 run `samples.json` 인라인 대조(결정성) ③ `resource_receipts.json`
  직독 ④ `python3 checks/context_limits.py` → `CONTEXT_PASS` ⑤ 회차 말 기계 검사(아래).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **W22 카드 발행 PASS** — lap454 필수 5항목 전부 반영(위 표).
  - **정정 1건 PASS(근거 있음)**: 「난이도」 레버 부재 ⇒ lap454 레버 목록에서 제거.
  - **신규 근거 3건**: 자원 포화(추론, §4-3이 측정으로 승격 예정) / 결정성(바이트 동일) /
    baseline 감속(외삽 63,659~1,314,876 tick).
  - **(가) 자체는 판정하지 않았다 — UNKNOWN 유지.** 이 회차는 판정이 아니라 판정 장치를
    만든 회차다. `FEASIBLE`/`NOT_FEASIBLE`은 W22를 실행한 work 회차가 §5 식으로 낸다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **middle의 사전 확정이 틀릴 위험**: §2-2는 rice/wood 시계열 부재로 **추론**이다.
    카드 §4-3이 측정으로 바꾸게 했고, 만약 측정 결과 자원이 실제로 고갈되면 §2-2는
    **폐기되고 「많은 자원」이 유력 레버로 복귀**한다. work는 이 가능성을 그대로 보고한다.
  - §2-4의 외삽은 "후반 증가율이 유지된다"는 가정이며, 실제로는 감속 중이므로
    **낙관적 상한**이다(진짜 도달 tick은 더 크거나 무한).
  - W21 CLOSED는 모델 기술 컨펌이며 **사용자 마일스톤 승인이 아니다**(3단 미완).
  - 이 카드 자체는 다음 회차(work 실행 → 그 다음 middle 독립 검수)가 검수한다.
    **middle인 이번 회차는 자기 카드를 스스로 승인하지 않았다.**
- 다음 한 가지: **work(Luna/Sonnet5)가 W22를 실행한다** —
  `docs/work/active/G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md`.
  A0~A5 여섯 arm × tick 8,000 창, §5 고정 판정식,
  fail-closed 산출물 `w22_lever_matrix.md`, 자체 lap 기록 필수(N64).

## 4. 회차 말 기계 검사

이번 회차는 **source를 바꾸지 않았으므로**(N22, INBOX 2026-09-20 21:58 규칙) 통합 `make check`
전체를 재실행하지 않고 표적 테스트 + 안전 검사 + 원본 직접 재해시만 수행했다.

| 검사 | 명령 | 결과 |
|---|---|---|
| 표적 테스트 | `python3 -m pytest tests/test_g2_eight_owner_setup.py -q` | **6 passed** |
| 안전 | `bash checks/safety.sh check` | **SAFETY_PASS** |
| 원본 무결성 | `sha256sum ../Syw2plus_re/Syw2plus/syw2plus_original.exe` | `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` **불변(직접 재해시)** |
| 문서 상한 | `python3 checks/context_limits.py` | **CONTEXT_PASS** (STATUS 121줄 ≤130) |
| §2-1 근거 실증 | `python3 tools/g4_difficulty_absence.py` | exit 0, `NO_FREE_BATTLE_DIFFICULTY_SELECTOR`, `exe.pinned=True`, lobby word target **7개** 일치, 4개 레지스트리 전부 `forbidden_present=[]` |

마지막 항목은 **읽기만 하지 않고 실제로 실행**해 §2-1의 「난이도 부재」 주장을 핀된 원본
바이트에 대해 확인한 것이다. exit 0은 그 자체로 제품 판정이 아니며(PROMPT ⑥), 이 도구가
인증하는 범위는 "원본 자유대전에 AI 난이도 선택자가 없다"뿐이다.

게임 실행 **0회**, 제품/도구 source 변경 **0**, 커밋 **0**.
