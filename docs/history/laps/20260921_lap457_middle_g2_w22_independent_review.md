# 2026-09-21 | lap457 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, **중간(middle) 역할**
  — 진단·계획·확인만. 게임 코드 hands-on 수정 없음. 검수 대상은 lap456 work(Sonnet5/high)의 W22.
- 가설 / 사용자 관찰: lap456이 카드 `G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md`(W22)
  6 arm을 실행해 **`PARTIAL`**(work 자기판정)로 끝냈다. 이 판정과 수치가 **원시 산출물만으로**
  재계산했을 때 성립하는지, 그리고 카드 §5 판정식이 실제로 "(가) 자연 도달 가능성"을 재는지 검증한다.
- 예상 PASS / FAIL 조건: (a) 6 arm의 `U_min`/`U_med`/`r_slow`/도달 tick과 최종 한 단어가 비참조
  재계산과 일치하면 ACCEPT, 불일치하면 정정·REJECT. (b) 카드 경계 위반(AI/바이너리 변경, op4,
  시딩, 144k 발행, fail-closed 산출물 부재)이 하나라도 있으면 REJECT.

## 1. 검수 방법 — 비참조 재계산

판정 입력에서 **제외**한 것: `analysis_results.json`, 각 arm의 `run_summary.json`,
`w22_lever_matrix.md` 본문, lap456 lap 기록의 수치 서술. 판정 입력으로 **쓴** 것:
각 arm의 `samples.jsonl`(241표본×6)·`fingerprint.json`, 핀된 원본 EXE, 현재/과거 소스 스냅샷.

산출물: `temp/Syw2plus_patch/g2_capacity/20260921_lap457_middle_review/`
- `recheck457.py` / `recheck457_output.json` — 카드 §5 판정식 독립 구현 + 무결성 전수 검사
- `decay457.py` / `decay457_output.json` — §5 `r_slow` 기준의 **예측력 역검정**(아래 N77)

게임 실행 **0회** · 제품/도구 source 변경 **0** · 커밋 **0**.

## 2. 판정 — **ACCEPT (최종 한 단어 `PARTIAL` 일치, 불일치 0)**

재계산한 6 arm(활성 owner는 `ai_flags_at_ps3`에서 직접 도출):

| arm | 설정(실측) | map | 활성 | 도달 tick | U_min@8k | U_med@8k | r_slow | gate U≥718 | gate r≥0.0341 |
|---|---|---|---|---|---|---|---|---|---|
| A0 | d4a0 d44_2 d46_0 seed42 | 100×100 | 8 | 8021 | **334**(o4) | 643.5 | 0.0555 | NO | YES |
| A1 | **d4a=1** | **140×140** | 8 | 8019 | **661**(o5) | 789.0 | 0.1104 | NO | YES |
| A2 | **owner4-7 ai=0** | 100×100 | **4** | 8020 | **569**(o0) | 717.5 | 0.1084 | NO | YES |
| A3 | **d44=0** | 100×100 | 8 | 8021 | **531**(o4) | 665.0 | 0.0855 | NO | YES |
| A4 | **seed=99** | 100×100 | 8 | 8020 | **506**(o1) | 742.5 | 0.0880 | NO | YES |
| A5 | **d46=1** | 100×100 | 8 | 8015 | **462**(o2) | 574.0 | 0.0907 | NO | YES |

- 유효 8,000-tick 창 **6/6** ⇒ `BLOCKED` 아님. 두 조건 동시 충족 arm **0** ⇒ `FEASIBLE` 아님.
  두 조건 모두 미달 arm **0** ⇒ `NOT_FEASIBLE` 아님. 전 arm이 "정확히 하나만" ⇒ **`PARTIAL`**.
- 무결성 전수(6 arm × 241표본): `live == Σ owner.count` 불일치 **0**, 표본 필드 `sum_count`와의
  불일치 **0**, `used > 5000` 표본 **0**, tick 역행 **0**, 최소 `rice` **966,760** / 최소 `wood`
  969,000대(1,000,000 지급분) ⇒ 카드 §4-3이 요구한 **자원 직접 측정** 충족(§2-2의 "자원은 구속
  조건이 아니다"가 추론 → 측정으로 승격). owner0이 `(20,2)`를 이탈한 arm **6/6**(N59 재확인 PASS).
- 카드 경계 준수 확인: op4 사용 0, 시딩(op5/op6) 0, 게임 EXE/DLL AI·경로·생산 로직 변경 0,
  144k 카드 발행 0, fail-closed 산출물 `w22_lever_matrix.md` 존재(6 arm 전행·최종 한 단어 포함),
  **work 자체 lap 기록 존재** ⇒ lap440·442·448 3회 연속이던 **N64 누락 연쇄가 끊겼다**.
- 후보 SHA `a10024de…` 6 arm 전부 일치, 원본 `b56986e018…c9c08a8ac` **직접 재해시 불변**,
  `checks/safety.sh check` → `SAFETY_PASS`, 표적 `tests/test_g2_eight_owner_setup.py` **7 passed**.

### 긍정 근거 1건 (arm 간 비교 가능성의 실증)

`control_executor.c`의 **arm별 빌드 스냅샷 6개가 전부 바이트 동일**(sha `6d2ff139…`)이고,
`_inmm.dll`은 A0↔A1이 **6바이트만** 다르다 ⇒ DLL SHA가 arm마다 다른 것은 lap456 서술대로
빌드 비결정 요소이며, **arm 간 차이는 런타임 goal 문자열 하나뿐**이다. 카드 §2-3(같은 시드
결정성)과 합쳐, arm 간 `U_min` 차이를 레버에 귀속하는 것은 정당하다.

### 부수 확인: cap도 count_cap도 이번 창에서 구속하지 않는다

최종 표본 최대 `count`는 A0 56 / A1 66 / A2 58 (count_cap 1200). 평균 유닛 비용 약 13.4이므로
`used`5,000은 owner당 약 373기이며 8인 합계 약 2,985기로 풀 4,001 안이다. ⇒ gap의 원인은
상한이 아니라는 카드 §2-4가 이번 창에서도 유지된다.

## 3. 신규 발견

### N77 (결정적 · 방법론) — `r_slow` 기준은 이 지평에서 예측력이 없다

카드 §5의 `r_slow`(tick 6,000→8,000)를 **lap442의 24k baseline soak 원시표본에 그대로 역적용**했다
(`decay457.py`, 게임 실행 0).

- tick 7,986 시점 최소 owner는 owner1 `used`=**359** ⇒ 카드 고정상수 `U_min(base)=359`는
  **독립 재계산으로 정확**하다.
- 그 owner의 `r_slow`(6k→8k) = **0.0545** ⇒ `r_req`=0.0341을 **1.6배로 통과**한다.
- 선형 외삽은 tick **93,185**(144k 안)에 5,000 도달을 예측한다.
- **그러나 같은 run에서 그 owner가 tick 24,030에 실제 도달한 값은 570이다**(선형 예측 1,233의 46%).
- 같은 owner의 구간 증가율: 0.0371(2k→4k) → 0.0460 → **0.0545(6k→8k, 정점)** → **0.0189(8k→16k)**
  → **0.0075(16k→24k)**. 즉 **증가율은 8k 부근에서 정점을 찍고 이후 7.3배 감쇠**한다.

⇒ 카드 §2-5가 "감속"이라고 이미 적은 그 baseline이 **`r_slow` 조건을 통과한다.** 따라서
**"6 arm 전부 `r_slow`를 넘겼다"는 사실은 판별력이 없으며**, `PARTIAL`을 "FEASIBLE에 절반 도달"로
읽으면 안 된다. W22 6 arm의 `r_slow`도 전부 2k→4k<4k→6k<6k→8k로 **아직 정점 이전 구간**이다
(A1 0.0815→0.0935→0.1104). 이 회차의 실제 신호는 `r_slow`가 아니라 **`U_min`의 수준차**다.

**판정 자체는 바뀌지 않는다.** §5는 실행 전 고정 판정식이고 사후 재채점은 금지(W17 선례)다.
N77은 판정을 뒤집는 근거가 아니라 **후속 회차의 판정식을 무엇으로 잡아야 하는가**의 근거다.

### N78 (계측 지점 이탈, 판정 불변)

lap456은 `U_min`/`U_med`를 카드가 말한 "tick 8,000 시점"이 아니라 **각 run의 최종 표본**
(tick 8,015~8,021)에서 계산했다. 최종 표본 기준으로는 lap456 수치와 **6 arm 전부 정확히 일치**
하지만(A0 334/655.0 … A5 462/574.0), tick 8,000 최근접 표본 기준으로는 **A1 `U_min` 661(676 아님)**,
**A0 `U_med` 643.5(655.0 아님)** 이다. `r_slow`도 lap456은 "6,000 최근접 → 최종 표본"으로 계산해
(내 재현값과 소수 4자리까지 일치) 카드 문구의 "6,000→8,000"과 미세하게 다르다. 매트릭스는
`r_slow`에 대해서만 이 사실을 공개했고 `U_min`/`U_med`에 대해서는 공개하지 않았다.
**두 읽기 모두에서 718을 넘는 arm은 0개라 최종 한 단어는 불변**이므로 정정으로만 기록한다.

### N79 (경계값 관찰 — 재채점 아님)

고정상수 `U_min(base)=359`는 **구식 goal(실질 7인) 빌드**인 lap442/lap413에서 나왔다. 이번
8-AI goal의 **in-run baseline(A0) 바닥은 334**다. in-run 바닥의 2배는 **668**이고 A1은 lap456
계측점 기준 **676**(넘음) / tick 8,000 기준 **661**(못 넘음)이다. 즉 A1은 "2배 기준"의 **경계에
정확히 걸쳐 있다.** 카드 §5는 사후 재채점을 금지하므로 **판정은 `PARTIAL`로 유지**하며, 이
관찰은 strategy가 후속 1 arm의 가치를 판단할 때 쓰라고만 남긴다.

### N80 (source/테스트 provenance 3건)

1. **as-run 소스 ≠ 현재 repo 소스.** 6 arm DLL에 실제로 들어간 `control_executor.c`는
   `6d2ff139c4777ad8…`이고 현재 repo 파일은 `40003d06f43a3c14…`다. 두 파일을 직접 diff한 결과
   **차이는 주석 한 블록뿐**(`roster/save`→`roster/persistence`, `§`→`section`, 줄바꿈)이고
   **코드 토큰 변화 0**이다. lap456이 이 사실을 스스로 공개했고 최종 소스로 `make check`를 다시
   돌렸다고 적었다 ⇒ **증거와 게이트 대상 소스는 동작상 동일**하다. 재-full-gate는 정보가 없다
   (INBOX 2026-09-20 21:58 규칙).
2. **"additive only"는 부정확한 표현이다.** lap452→lap456 diff는 추가 47줄 외에 **기존 7줄을
   수정**했다(`owner0_ai` 정의, `record[2]`, `d44`/`d46`/`d4a`). **다만 레거시 두 goal에 대한
   동치는 참이다** — 내가 diff에서 직접 진리표를 확인했다: `owner0_ai = (goal != G2_EIGHT_GOAL)`는
   `G2_EIGHT_GOAL`→FALSE·`G2_EIGHT_AI_GOAL`→TRUE로 구식 `== G2_EIGHT_AI_GOAL`과 같고,
   `owner_ai = (owner==0)?owner0_ai:TRUE`는 구식 `record[2]`를 그대로 재현하며, 세 config
   필드의 `want_*`는 두 레거시 리터럴에서 전부 FALSE라 `(2,0,0)`로 복귀한다.
3. **신규 회귀 테스트는 이름값을 못 한다.** `test_g2_legacy_goals_compute_identical_config_to_pre_w22_source`는
   C 소스를 **읽지 않는다** — 새 C 표현식을 Python으로 다시 쓰고 `want_* = False`를 하드코딩한 뒤
   손으로 적은 기대값과 비교한다. 즉 **C가 바뀌어도 이 테스트는 실패할 수 없다**(docstring의
   "a future edit that actually changes legacy behavior still fails a test"는 과장). 레거시 동치
   보장은 사실상 이웃 두 테스트의 **문자열 핀**에만 걸려 있고, 핀은 C 수정과 함께 갱신되면 같이
   통과한다. **잠재 위험:** `owner0_ai`의 기본값이 opt-in(`== AI_GOAL`)에서 opt-out
   (`!= EIGHT_GOAL`)으로 **뒤집혔다** ⇒ 앞으로 `is_g2_eight_goal()`에 리터럴을 추가하는 회차는
   owner0 AI=1을 **자동으로** 얻는다. 이번 5개 arm goal에는 의도된 동작이지만, 다음에 owner0을
   사람 슬롯으로 두려는 goal을 추가하면 조용히 깨진다.

## 4. 발행 카드 — W23

`docs/work/active/G2_A1_MAP_LEVER_LONG_WINDOW_LAP457.md`.
카드 §5 `PARTIAL` 조항이 허용한 **후속 1 arm·1 회차**를 그대로 쓴다: **A1만**, 동일 설정,
창을 tick 24,000으로 연장. 새 레버값 추가 금지(`d4a=2` 포함). 재계획 아님.
핵심은 N77이 강제한 **판정식 교체**다 — 8k 구간 증가율이 아니라 **후반(16k→24k) 증가율**을
그 지평에 필요한 값과 비교하고, 비교 대상 baseline 수치(lap442 owner1: 24,030에 570,
`r_late` 0.0075, 필요값 0.0369)와 "감쇠가 같은 모양이면 A1은 약 1,073"이라는 기대값을
**실행 전에** 박아 사후 서사를 막는다.

## 5. 이번 회차 검사

게임 실행 **0** · 제품/도구 source 변경 **0**(N22 — 한 줄도 바꾸지 않았다) · 커밋 **0**.
표적 `tests/test_g2_eight_owner_setup.py` **7 passed** · `checks/safety.sh check` → `SAFETY_PASS` ·
원본 **직접 재해시** `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.
STATUS 압축 전 원문 `20260921_status_lap457_precompaction.md`
(SHA `66af3ecceb1467c98f02dae0188cf41aeb5576a3091a7fcdb10ebcc35df0698c`, 129줄).
`loop/ESCALATE_SOL` §35 추기.

## 6. 남은 위험 / 다음 한 가지

- **G2 제품 완료 아님.** 이번 회차가 더한 것은 판정 하나(`PARTIAL` 확정)와 그 판정을 어떻게
  읽으면 안 되는지(N77)뿐이다. 실제 5,000 자연 도달·144k·건물 포함 구성·전투/사망/재생산
  순환·LAN은 전부 미검증이다.
- **144k 발행 금지 유지.** W23도 24,000 tick까지만이다.
- 되물음 3건((ㄱ)/(ㄴ)/(ㄷ))은 W23이 `DECAYED`로 끝날 때 승격한다. 모델이 대신 고르지 않는다.
  기존 되물음 2건(lap404 (가)/(나), F4 (B)/(C))도 사용자 대기 상태 그대로다.
- **다음 한 가지:** work(Sonnet5/high)가 W23 A1 24k 연장 1 arm을 동기 실행한다.
