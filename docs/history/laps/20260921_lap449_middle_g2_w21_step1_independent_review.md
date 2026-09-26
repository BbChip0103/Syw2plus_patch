# lap449 middle — W21 Step1 cap 근접 soak 독립 검수

- 날짜: 2026-09-21 KST
- lap: 449 (`loop/.lap_counter` = 449)
- 역할: **middle / 컨펌** — Claude Code `claude-opus-5` / high. 게임 코드 hands-on 수정 없음.
- 목표: G2 (활성 8인 각각 전비 5000 안정성). G1/G4는 2026-09-21 00:20 사용자 지시로 잠정 중단,
  G3는 계속 포기 범위.
- 대상: lap448 work의 W21 Step1 (Root 동기 회수 실행).
  카드 `docs/work/active/G2_CAP_PROXIMITY_SEEDED_SOAK_LAP445.md` §1 (U1)~(U4), §10 (N59~N63).
- 입력 증거:
  `temp/Syw2plus_patch/g2_capacity/20260921_lap448_w21_step1_cap_proximity_soak_root_recovery/`
  (`samples.jsonl` 712표본, `step1_orchestrator.log`, `root_recovery_console.log`,
  `w21_step1_run.py`, `bridge_build/`) 및
  `temp/Syw2plus_patch/g2_capacity/20260921_lap448_w21_step1_cap_proximity_soak/`
  (`n60_result.json`, `n60_orchestrator.log`, `bridge_build_n60/`).
- 이번 회차 산출물:
  `temp/Syw2plus_patch/g2_capacity/20260921_lap449_middle_review/`
  (`recheck449.py`, `recheck449_output.json`, `u4_attribution.txt`).

## 0. 검수 방법 — 비참조 재계산

lap448의 `run_summary.json`과 Root 회수 INBOX 서술을 **판정 입력으로 쓰지 않았다.**
원시 `samples.jsonl` 712표본만 `recheck449.py`로 독립 재계산해 (U1)~(U4)를 먼저 확정한 뒤,
마지막에만 `run_summary.json`과 대조했다. 판정식은 카드 §1의 실행 전 고정값 그대로이며
**재채점하지 않았다.**

게임 실행 **0회**. 제품/도구 source 변경 **0**(repo에서 09:22 이후 바뀐 파일은 docs 5개뿐).
커밋 **0**.

## 1. 재계산 결과 — 불일치 0

| 축 | lap449 원시 재계산 | lap448 `run_summary.json` | 일치 |
|---|---|---|---|
| 표본 수 | 712 (sample 0..711 연속) | 712 | ✔ |
| 최종 tick | 24,029 (단조 비감소, 역행 0) | 24,029 | ✔ |
| `max_live` | 1,247 | 1,247 | ✔ |
| owner별 max `used` | `[5000,4995,5000,4995,4995,5000,4995,4995]` | 동일 | ✔ |
| live `used` > 5000 | **0표본** | `false` | ✔ |
| `live == Σ owner.count` 불일치 | **0표본** | 0 | ✔ |
| RSS max / min / final | 247,288 / 51,516 / 51,612 KB | 동일 (sample 328·670·711) | ✔ |
| 최대 RSS 하강 3건 | s331 −39,548 / s631 −33,496 / s330 −20,492 | 동일 | ✔ |
| `max_slot_index` | 전 표본 상수 4000 | 4000 | ✔ |

**불일치 0건.** 구조 무결성도 확인했다: 필수 필드 누락 0, owner 8명 미만 표본 0,
오류/실패 표식 키 0, `pid` 단일값 3371399, 표본 간격 1.000~1.026s.

## 2. 판정식 결과 (카드 §1, 실행 전 고정)

- **(U1) cap 근접 도달 — PASS (8/8).** 시딩 종료 직후 첫 표본(tick 312)에서 owner별 `used` =
  `{0:4945, 1:4900, 2:4910, 3:4910, 4:4910, 5:4900, 6:4910, 7:4900}` 전부 [4900, 5000] 안.
  soak 전 구간에서 4900 미만으로 떨어진 owner-표본 **0건**.
- **(U2) cap 근접 안정성 — PASS.** tick 24,029 ≥ 24,000 도달, `stop_reason=stop_tick_reached`,
  live `used` > 5000 표본 0건. fault/crash/read failure 0: 샘플러
  (`w21_step1_run.py:445-470`)는 `process_exit`·`tick/existence/owner read failed` 어느 하나라도
  발생하면 **즉시 루프를 끊고** `fault_or_crash`로 표시하는 구조이므로, 712표본이 끊김 없이
  `stop_tick_reached`로 끝났다는 사실 자체가 read failure 0의 구조적 증거다.
- **(U3) 장부 정합 — PASS.** 712표본 전부 `live == Σ owner.count` (`sum_count` 필드와
  재계산값도 전부 일치).
- **(U4) 메모리 해명 — PARTIAL (1건 확정 + 1건 UNKNOWN).** §3 참조.
- (U5) 저장/로드 왕복 — **미실행**(Step2 미착수).

**종합: U1 ∧ U2 ∧ U3 ⇒ `CAP_PROXIMITY_STABLE`(부분 증거).** lap448 실행기 판정과 일치.
카드 §0-1·§9대로 이것은 **부분 증거이며 G2 제품 완료가 아니다.**

## 3. (U4) 메모리 — N57을 절반 닫았다

카드 §4-4의 판정 규칙(`vm_size` 동반 감소 ⇒ 게임 측 해제 / `vm_size` 불변 + `rss` 감소 +
`host_mem_available` 낮음 ⇒ 호스트 회수 / 둘 다 아니면 UNKNOWN)을 그대로 적용했다.

- `vm_size_kb`는 712표본 **전부 3,463,564 KB 단일값**이다. 감소가 한 번도 없다
  ⇒ **주소공간 해제(munmap/MEM_RELEASE)는 0건**. "게임이 풀을 반납했다"는 해석은 배제된다.
- 1MB 이상 RSS 하강은 **26건, 합계 −197,584 KB**. 이 중
  - **23건 (합계 −131,824 KB)** 은 같은 표본에서 `vm_swap_kb`가 증가했고, 그 구간 swap 증가
    합은 **+129,340 KB** ⇒ **(a) 호스트 페이지 회수(swap-out) 확정.**
  - **3건 (s329/t11,288 −5,720, s330/t11,321 −20,492, s331/t11,355 −39,548, 합계 −65,760 KB)** 은
    `vm_swap_kb`가 **0이고 그 시점까지 swap이 한 번도 발생하지 않았다**(최초 nonzero는
    s515/t17,491). `vm_size`도 불변이다.
- `host_mem_available_kb`는 5,468,928 → 최저 2,422,712 KB로 떨어졌다(시작 대비 −56%).

**귀속:** 후반 −129MB는 **(a) 호스트 회수로 확정**한다. 그러나 tick 11,288~11,355의 **−65,760 KB는
(a) clean file-backed 페이지 축출과 (b) 게임 측 `madvise(MADV_DONTNEED)`류 해제를
`vm_size`만으로 분리할 수 없다** — 둘 다 `vm_size` 불변 + swap 0을 만든다. 카드 §1 (U4)
후단대로 이 몫은 **UNKNOWN으로 남기며 "해명됐다"고 쓰지 않는다.**

⇒ **N57(“RSS 미해명·요약에 필드조차 없음”)은 이번 run 범위에서 2/3이 닫혔다.** 남은 것은 위
−65,760 KB 한 구간뿐이고, 다음 Step2에서 **표본에 `/proc/<pid>/smaps_rollup`의
`Private_Clean`/`Private_Dirty`를 추가하면 새 게임 실행 없이 분리된다**(§6-3 지시).

**주의(과대해석 금지):** lap442·lap443이 본 RSS 역상관은 **그 run에 `vm_swap` 필드가 없었다.**
이번 결론을 그 run에 소급 적용하는 것은 유추이며 측정이 아니다.

## 4. 카드 §10 의무 4건 이행 검수

1. **(N59) 신후보 기준 (U0) 재확인 — PASS.** `step1_orchestrator.log` 09:34:41~09:34:49:
   N=4001 신후보(`a10024de…`)·새 goal에서 PS3 진입 시 8 owner 전원 `ai=1`이고,
   **시딩 이전** 90초 관찰 창에서 owner0이 tick **284**에 baseline `(20,2)`를 이탈해
   `(used 30, count 3)`이 됐다. ⇒ "7인 + 미활성 1" 기재 조건 미발동, **실질 8인**.
   **증거 등급 주의:** 이 항목만은 `samples.jsonl`(시딩 후 tick 312부터 시작)로 재계산할 수 없어
   **로그/요약에 의존**한다. 712표본 재계산보다 한 단계 약한 증거다.
2. **(N60) 같은 바이너리 A/B 대조 — CLOSED.** `n60_result.json`: 기존 goal
   `_custom_game_chain_inject_g2_eight_seed42`로 PS3 진입 시 **owner0 `ai`=0, owner1~7 `ai`=1**.
   **결정적인 것은 run 간 대조가 아니라 run 내부 대조다** — 같은 바이너리·같은 run 안에서
   owner0만 0이고 나머지 7명이 1인 패턴이 소스
   `tools/inmm_stub/control_executor.c:913` `record[2] = (owner == 0 ? 0 : 1)`와 정확히 일치한다.
   ⇒ `record[2]`가 AI 플래그라는 귀속은 이제 **소스 + run 내부 대조 + 교차 goal 대조** 3중이다.
   **단, 대조군 arm은 stock capacity=1200 DLL(`06b8b959…`), 처치군은 4001 DLL(`90c73e9d…`)로
   빌드 축이 다르다** — 그래서 위처럼 run 내부 대조를 1차 근거로 삼았다.
3. **(N61) 샘플러 `final_tick` 결함 — 수리 확인.** `w21_step1_run.py:455-457`이 STOP_TICK 검사
   **이전에** `final_tick_seen = tick`을 기록한다. 독립 재계산한 마지막 표본 tick 24,029와
   `run_summary.final_tick` 24,029가 일치하므로 과소보고가 재발하지 않았다.
4. **(N63) 표본 필드 lap442 합집합 — 충족.** 표본에 `live`/`max_slot_index`/`rss_kb`/`reserved`/
   `cap`/`count_cap`(lap442) ∪ `ai` ∪ `vm_size_kb`/`vm_swap_kb`/`host_mem_available_kb`/`pid`가
   모두 있다. `cmdline`은 표본이 아닌 `run_summary.cmdline`
   (`/bin/sh -e /usr/bin/wine syw2plus_original.exe`)에 1회 기록 — 카드 "최초 1회" 요구 충족.

함정 검수: **함정1(`fixture_failed` 영구 잠금) 회피 확인** — 본 시딩 전 op5 `wanted=1` 스모크
1건이 `ok=true/reason=executed`로 통과했다(`fixture_attempts=101`). **함정2** 위반 없음 —
`C:\inmm_unit_ticks.jsonl` 등 stock 하드코딩 채널을 판정 근거로 쓴 흔적이 산출물에 없다.
**N55 준수** — `max_slot_index`(전 표본 4000 상수)를 점유/확장 근거로 쓰지 않았다.

## 5. 신규 발행 — N64~N68

- **N64 (관찰 결함, 3회 연속): lap448의 자체 lap 기록이 없다.** `docs/history/laps/`에
  lap448 파일 0건. 카드 §8이 "work는 자체 lap 기록을 남긴다. 기록이 없으면 다음 middle이
  관찰 결함으로 기재한다"를 명시했고, 누락은 **lap440 · lap442 · lap448로 3회 연속**이다.
  또한 lap448은 장시간 실행을 셸 background로 넘기고 종료해 **Root가 동기 회수**했다
  (카드 §8·INBOX 01:01 운영 규칙 위반, 같은 유형 lap423·438·440·442에 이어 반복).
  이번 lap 기록은 산출물 기반으로 §1~§4에 보존했다.
- **N65 (판정식 구현 결함, 이번 run 무영향): 실행기 verdict 식이 (U3)를 포함하지 않는다.**
  `w21_step1_run.py:551-558`은 `fault` / `any_owner_over_5000` / `U1_pass` /
  `stop_reason`만으로 verdict를 정하고 `U3_pass`를 **쓰지 않는다.** 카드 §1 종합판정은
  `U1 ∧ U2 ∧ U3`이므로, U3가 깨진 run에서도 이 스크립트는 `CAP_PROXIMITY_STABLE`을 출력한다.
  이번 run은 U3가 통과해 결과에 영향이 없으나 **같은 스크립트를 Step2에 재사용하므로
  재사용 전 수리 대상**이다.
- **N66 (절차 결함, N54/N58 3회차): Step3 fail-closed 산출물이 없다.**
  카드 §7이 요구한 `<run 디렉터리>/lap413_stock_comparison.md`가 run 디렉터리에도
  `g2_capacity/` 어디에도 **존재하지 않는다**(find 0건). W19 Step4 → W20 Step3 → W21 Step3로
  **3회 연속 누락**이며, 이 fail-closed 조항은 정확히 그 재발을 막으려고 lap445가 승격시킨 것이다.
  ⇒ §6대로 **W21 카드 전체 ACCEPT는 보류**하고, 다음 work 회차의 **첫 산출물**로 강제한다.
- **N67 (범위 정직성): 혼합 구성이 형식만 2계층이다.** 시딩은 owner당
  op5(type 5, cost 35) **×138** + op6(type 7, cost 10) **×5** = 143기다. 개체 수 기준 96.5%,
  비용 기준 4,830/4,880 = **99.0%가 단일 type 5**다. 카드 §0-3의 "최소 2계층"은 형식적으로
  충족하나 **"혼합 구성"이라고 뭉뚱그려 쓰면 과장**이다. 수치를 함께 적는다.
  건물 계층 부재는 카드 §0-3이 이미 선언한 기지(旣知) 한계이며 (가) 경로의 몫이다.
- **N68 (열린 되물음에 대한 신규 직접 증거): pending 초과가 신후보 cap 근접에서 재현됐다.**
  `used + reserved > 5000`인 owner-표본이 **1,263건**이고, 값은 **전부 정확히
  `(used 4995, reserved 10)`**, owner는 **owner4(619표본)와 owner7(644표본) 둘뿐**이며
  **마지막 표본까지 해소되지 않았다.** live `used`가 5000을 넘은 표본은 0건이다.
  이는 lap412가 확정한 기전("비용 10짜리 생산 주문 1건이 큐에 걸려 `used`가 cap 아래로
  내려가야만 해소")과 정확히 일치하며, 이번에 **수리된 신후보 + cap 근접 + 24k**에서도
  같은 현상임을 보인다. 열린 되물음(2026-09-20 lap404 (가)/(나))의 판단 재료이며
  **모델이 대신 결정하지 않는다.** INBOX 해당 항목에 원문 보존하고 추기했다.

## 6. 다음 지시 (middle 권한, 카드 §11 addendum으로 발행)

1. **Step3 대조표를 먼저, 게임 실행 없이 만든다.** 입력(lap413 구후보 / stock 대조군 /
   lap442 구 soak / 이번 lap448 신후보)은 **전부 이미 파일로 존재**하므로 추가 run이 필요 없다.
   이 파일이 생기기 전에는 Step2를 시작하지 않는다(N66 fail-closed 집행).
2. **그 다음 Step2**(신후보 저장/로드 왕복, 카드 §6). tick 역행 증거 필수.
3. **Step2 스크립트 재사용 전 2건 수리:** (a) N65 — verdict 식에 `U3_pass`를 넣는다.
   (b) (U4) 잔여 UNKNOWN 분리를 위해 표본에 `/proc/<pid>/smaps_rollup`의
   `Private_Clean`/`Private_Dirty`(가능하면 `Referenced`)를 추가한다. 둘 다 계측 수리이며
   **판정식 변경이 아니다.**
4. **work는 자체 lap 기록을 남긴다**(N64 4회차 금지). 장기 실행은 동기 또는 root 소유 세션.
5. 경계 불변: 144k 카드 발행 금지 유지, op4 금지, (나) 단독으로 G2 완료 주장 금지,
   AI 코드/바이너리 변경 필요 시 즉시 strategy 재에스컬레이션.

## 7. 이번 회차 검사

- 이번 회차 **source 미변경** ⇒ INBOX 2026-09-20 21:58 규칙 + N22에 따라 통합 `make check`를
  실행하지 않고 아래만 수행했다.
- 표적 `tests/test_g2_eight_owner_setup.py` → **6 passed**.
- `checks/safety.sh check` → **SAFETY_PASS**.
- 원본 `Syw2plus/syw2plus_original.exe` **직접 재해시** →
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` **불변**
  (safety 결과에 기대지 않고 `sha256sum`으로 별도 확인).
- 후보 identity: `step1_orchestrator.log`가 **현재 source에서 재빌드**해
  `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`을 얻었다(N53 준수, 핀 복사 아님).
  브리지 DLL `90c73e9d02d5c27f252c25a601c1764809f3c4160a26b63deff90ae3367a44e0`(capacity=4001),
  N60 대조군 DLL `06b8b9593c49e8d81781d563d7fa90f360a49ea7aed644add0a665110947a0c9`(stock 1200).
  (N62 준수 — DLL 인용은 `dll_sha256` 축이며 `bridge_sha256`과 구분한다.)
- 게임 실행 0회, 제품 코드 변경 0, 커밋 0(`LOOP_ALLOW_COMMITS=0`).

## 8. 아직 아닌 것

G2 제품 완료 **아님**. 이번 회차가 늘린 것은 "수리된 신후보가 **8 owner 전원 AI 활성 + cap
근접(4,900~5,000) 상태에서 24,029 tick을 fault 0 · 장부 불일치 0으로 버텼다**"는 **부분 증거**
하나뿐이다. 미검증으로 남는 것: **(U5) 저장/로드 왕복(신후보)**, 원본 생산 경로로의 자연
도달((가)), 144k, LAN/지원 동기화, 건물 포함 혼합 구성, 전투/사망/재생산 순환,
그리고 (U4)의 −65,760 KB 구간.
