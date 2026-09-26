# INBOX — 사용자 지시 원문과 처리 상태

체크는 문서 반영 여부이며 제품 구현 완료가 아니다. 체크된 상시 요구도 계속 유효하다.

## 처리 대기

- [ ] 2026-09-22 lap471~474 W24 Step C rider 계보 (lap474 압축 — 원문 전량 보존, 삭제 없음):
  lap471(work) Step C 4회차 `RIDER_ORDER_NOT_ACCEPTED`(전제 headroom5<비용10 첫 성립·주문
  316표본 전부 `reserved=0`로 미개시) → lap472(middle) 독립검수 = **측정 ACCEPT(불일치0, N106
  장부항등식 75+140×35+10+10=4,995 재현) / 해석 REJECT `STEP_C_CONFOUNDED`**(N105: 양성대조
  producer는 주문직전 `(cmd1,progress0,type0)`인데 차단영역 주문직전은 `(cmd1,progress100,type7)`
  로 완료·미해제 상태였고 `command`가 생산중값15에 한번도 진입 안함 ⇒ H-headroom/H-producer
  원시로 분리불가, 음성 대조 선행 권고) → lap473(strategy,Fable5) `ESCALATE_SOL`§44 회신: **rider
  계속**(하드캡 잔여2 work회차·재연장없음·새카드금지. Round1=N105음성대조, 선판정: REFUSES/
  BLOCKED⇒즉시종료`RIDER_STOCK_REPRO_UNDECIDABLE_BY_FIXTURE`[§38회귀승격미발동,(가)/(나)는
  "해악0+판정불능"사실과함께 사용자되물음승격], ACCEPTS⇒H-headroom유일생존·Round2정확히1회
  [producer≥2기지속생산 최소재설계]) → **lap474(work) Round1 N105 음성 대조 실행 =
  `PRODUCER_ACCEPTS_SECOND_ORDER`**(양성대조 L=698tick 해소직후 `used=85`·headroom
  =cap5000-85=4,915≫비용10 **미접촉**, 같은 producer slot1182/id132254(lap471과 동일
  "완료·미해제" `command1/progress100/type7`)에 2차 op1주문 → 창(예산2,094=3×698, 실현730)
  안에서 tick1045 `reserved=10` 발화(사망이벤트`count5→4`와 동시)·tick1419 `progress100/
  reserved0`으로 해소 ⇒ lap471(headroom5<10, 316표본전부`reserved=0`)과의 **유일 통제차이가
  headroom**이므로 **H-producer 반증·H-headroom 유일생존으로 승격**(work 해석,
  **다음 middle 독립검수 대기, §44 종결처분 미확정**). 게임실행1·제품코드0·source변경0
  (3자일치)·targeted167 passed·`SAFETY_PASS`·`CONTEXT_PASS`·커밋0. W24 CLOSED 아님·144k금지·
  lap404(가)잠정채택 전부 유지. **Round2(producer≥2기 재설계)는 middle ACCEPT 이후 착수, 잔여
  rider 하드캡 1 work 회차.** **압축 직전 INBOX 전체 원문**은
  `docs/history/20260922_inbox_lap474_precompaction.md`(SHA
  `63d922169ad314ae5376f2a3105d21a67934eb2d15f50a6d1e783c60d49f5b8e`, 398줄)에 보존했다. 개별
  전문은 `docs/history/laps/20260922_lap471_work_g2_w24_stepC_rerun_v4.md`·
  `20260922_lap472_middle_g2_w24_stepC_rerun_v4_independent_review.md`·
  `20260922_lap473_strategy_g2_w24_stepC_rider_disposition.md`·
  `20260922_lap474_work_g2_w24_stepC_n105_negative_control.md`에 그대로 있다.
  `loop/ESCALATE_SOL`§43·§44.

- [ ] lap469~471 계보 (lap472 압축 — 원문 전량 보존, 삭제 없음): lap469(work) Step C 3회차
  `RIDER_NO_REPRO` → lap470(middle) **REJECT(`STEP_C_PRECONDITION_NOT_MET`)**(N98 차단영역 체류
  0tick·N99 cost35 단일기저의 구조적 양자화·N100 장기soak 모순 소멸/h1~h3 철회·N101~N104) →
  lap471(work) Step C 4회차가 §42-6의 4가지(op6 top-up으로 headroom5<비용10 조성·의미론적 게이트·
  예산/실현/체류 분리·producer계측)를 구현해 재실행, **전제는 처음 성립**했으나 주문이 창
  2,106tick 내내 `reserved=0`이라 카드 밖 4번째 상태 **`RIDER_ORDER_NOT_ACCEPTED`**로 종료
  (1차 시도의 discriminator 결함은 work가 직접 잡아 `order_fired`/`count_increased` 계측 추가 후
  정정, 1차 원문은 `attempt1_stale_progress_false_positive/`에 보존) → 위 lap472가 독립검수.
  **압축 직전 INBOX 전체 원문**은 `docs/history/20260922_inbox_lap472_precompaction.md`
  (SHA `87ac134e9ed85703724e21b0c5188f243dd216ab0c36f78e19655e8d85569df2`, 390줄)에 보존했다.
  개별 전문은 `docs/history/laps/20260922_lap469_work_g2_w24_stepC_rerun_v3.md`·
  `20260922_lap470_middle_g2_w24_stepC_rerun_v3_independent_review.md`·
  `20260922_lap471_work_g2_w24_stepC_rerun_v4.md`(각 `ESCALATE_SOL`§42·§43)에 그대로 있다.
  **lap465~467 원문**은 `docs/history/20260922_inbox_lap469_precompaction.md`
  (SHA `02fa663cd262a6c6a9e71fda9a6cc5e9f49de2910fd33b7a8bdff4df4d291a35`, 393줄)와 각
  `docs/history/laps/20260922_lap46{5,6,7}_*.md`에 그대로 있다.

- [ ] lap462~465 계보 (lap466 압축 — 원문 전량 보존, 삭제 없음): lap462(work) W24 Step A
  `BUILDING_SEEDABLE`(대표t=46)+Step B 판정기 수리(음성대조2건 발화)+Step C(당시) `RIDER_NO_REPRO`
  (producer가 op6로 막 배치된 비생산 유닛이라 방법론 유보) → lap463(work) allow-list {5,7}→
  {5,7,46} 변경 후 게이트를 background로 띄우고 종료해 FAIL(2026-09-21 01:01 규칙 위반, lap 기록
  누락) → 운영 회수가 게이트만 회수(791 passed)+N90(허용목록 무테스트) 발견 → lap464(work)
  N90 수리(796 passed)+Step D 실행 `NO_ENGAGEMENT` 자기판정 → lap465(middle) 원시 715표본+
  census 3종 재계산으로 Step D **ACCEPT**(불일치0, 역주입8건, 양성분기 `CYCLE_STABLE` 도달성
  증명)하되 Step C는 producer가 실패한 op6 잔여 type7 유닛이라 **VOID** 처분(N91~N95: C3전용
  55슬롯 원본생산 오귀속 정정·type7→23 제자리전이17건·reserved10고정 아님·§7 사다리 비전역·
  P_max 계산차) → lap466(위)이 그 Step C 결손을 해소. **압축 직전 INBOX 전체 원문**은
  `docs/history/20260922_inbox_lap466_precompaction.md`
  (SHA `5b92adeea252861e1ffbe7314475c4de6d2c7619d72e775256154f2a8c1a9f68`, 396줄)에 보존했다.
  개별 전문은 `docs/history/laps/20260921_lap462_work_g2_w24_stepABC.md`·
  `20260922_lap463_aborted_work_plus_middle_gate_recovery.md`·
  `20260922_lap464_work_g2_w24_stepD_no_engagement.md`·
  `20260922_lap465_middle_g2_w24_stepD_independent_review.md`에 그대로 있다.

- [ ] 2026-09-21 01:10 KST 운영 회수 — W10 P-A 실제 완료. lap415 입력의 PID 원인 서술은
  **정정**한다: PID는 맞았고 최초 PE mapping 전 일시 `EFAULT`를 retry하지 않은 것이 원인이었다.
  lap416 probe 수정본을 root 소유 동기 세션에서 새 run2로 실행해 709표본/동일 tick11,928 정지를
  재현했다. fault 직전 생존 high-slot **3565/type76/owner4**의 `+0x692`가 tick11,921에서 -6599,
  tick11,928에서 19579로 폭증했고 low band 이상은 0이다. 따라서 카드 P-A의 **H1 지지** 조건을
  충족한다. 증거 `temp/Syw2plus_patch/g2_capacity/20260921_lap416_fault_root_cause_pa_run2/`;
  후보 SHA `4331d9cd…`, 원본 전후 `b56986e0…`, 709 lines, `SAFETY_PASS`, 잔류0. 다음 work는
  W10 P-B의 1200-bound 전수 인벤토리와 이 손상을 만드는 단일 site를 좁힌 뒤 P-C 최소 수리한다.

- [ ] 2026-09-21 01:01 KST 운영 규칙: loop agent가 장시간 Wine probe를 셸 background로 띄운 뒤
  회차를 종료하면 loop cleanup이 자식도 정리해 실행이 지속되지 않는다. 장기 probe는 모델 세션이
  직접 기다리거나 root가 소유한 exec 세션으로 실행·회수한다. “background 실행 중” 문구만으로
  활성 프로세스를 주장하지 않고 PID/산출물 갱신을 확인한다.

- [ ] 2026-09-21 00:51 KST 운영 회수: lap415 W10 P-A probe는 실제 샘플링에 진입하지 못했다.
  `movement_state_probe.py`가 `subprocess.Popen(["wine", ...]).pid`인 Wine 런처 PID 2435667을
  게임 내부 PID로 사용해 PS 주소 `0x4ED818` read가 `EFAULT`로 종료됐고 `samples.jsonl`은 0B다.
  게임 후보 실패나 H1/H2 판정으로 세지 않는다. 산출물은
  `temp/Syw2plus_patch/g2_capacity/20260921_lap415_fault_root_cause_pa/`에 보존됐다. 다음 work는
  기존 `tools.runtime_env`/`runtime_driver`의 검증된 Windows game PID 발견 방식을 재사용해 같은
  P-A를 재실행한다. 새 독자 PID 추측을 추가하지 않는다.

- [ ] 2026-09-21 00:20 KST: 사용자 목표 우선순위 확정. **G2(8인 각각 전비 5000 안정 플레이)가
  성립하기 전까지 G1(1600×1200 원본 구성)과 G4(AI/길찾기 개선)는 잠정 중단**한다. G3(최대
  16인)는 잠정 중단이 아니라 **계속 포기한 범위**로 고정한다. 현재 lap414의 G2 독립 검수는
  이 지시와 일치하므로 중단하지 않으며, 이후 루프도 G2의 직접 조사·수리·실행검증 외 목표로
  전환하지 않는다.

- [ ] 2026-09-20 21:58 KST: 사용자 “아니 뭐 이렇게 굼떠”. 같은 소스에 대해 784개 전체
  `make check`를 회차마다 반복해 실제 게임 실행을 늦추지 않는다. 직전 동일 source의 full gate가
  PASS이면 다음 독립 검수는 원시 산출물·표적 테스트·원본/안전검사만 수행하고 제품 런타임으로
  즉시 이동한다. 전체 gate는 소스 변경 뒤 통합 경계에서 한 번만 실행한다.
  **2026-09-20 lap410 적용(상시 규칙이라 체크는 두지 않음):** 이 지시를 처음 적용했다. lap410은 동일
  source·직전 full gate PASS이므로 784 `make check`를 재실행하지 않고 원시 산출물 재계산 + 표적 테스트
  (`test_g2_full_capacity_persistence_compat_v1.py` 5 passed) + 원본 해시 + `checks/safety.sh check`만
  수행했다. 발행한 다음 카드 W8에도 §6으로 같은 규칙을 박아 두었다.
  **2026-09-20 lap412 오적용 정정(N22):** 이 규칙은 "동일 source일 때 면제"이지 "항상 면제"가 아니다.
  lap411은 스스로 `patches/population/runtime_driver.py`(`control_goal_payload`)와 신규 테스트
  `tests/test_runtime_env.py::test_runtime_driver_control_goal_uses_protocol_string_request_id`를
  추가해 **source를 바꿨는데도** "동일 source"를 근거로 전체 gate를 건너뛰었다. 규칙 후단
  "전체 gate는 소스 변경 뒤 통합 경계에서 한 번만 실행한다"가 걸리는 경우였다. lap412 middle이
  그 통합 경계 gate를 대신 실행했다(collected **785** = 784+신규1). **규칙 자체는 유효하며 변경 없다** —
  앞으로 면제를 주장하는 회차는 "이번 회차에 source를 바꾸지 않았다"를 함께 적는다.

- [ ] 2026-09-20 00:33 KST: 사용자 "그래 그 1200을 늘릴 수는 없냐고" 이후 "ㄱㄱ".
  G2의 즉시 최우선 작업을 전비 장부 단독 조사에서 **전역 UnitStruct 풀 1,200칸 확장 실행
  스파이크**로 전환한다. 첫 성공 기준은 격리된 실제 게임에서 slot index **1,200 이상** 개체를
  정상 생성하고, 기존 reader로 관측한 뒤 사망·슬롯 재사용까지 증명하는 것이다. 단순 `0x4B0`
  상수 변경이나 다음 상태영역 덮어쓰기는 금지한다. 새 풀/보조배열 주소 재배치와 참조 fixup을
  최소 범위로 구현하고, 실패 가설 2회 또는 60분 안에 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`로
  판정한다. 저장/LAN은 이 첫 스파이크의 PASS 조건이 아니지만 후속 필수 blocker로 명시한다.
  2026-09-20 lap396 전비 probe는 이 최신 우선순위에 따라 안전 종료(exit143, safety ok)했다.
  2026-09-20 lap397 middle이 정적 표면을 측정해 최소 변경 범위를 확정하고 즉시 실행 가능한
  work 카드 `docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md`(W3)로 인계했다.
  건드릴 것은 재배치3영역(pool/existence/age)+상수4개+fixup1,016건뿐이며 active/catA/catB·
  PlayerStruct roster·`0x892410` 별칭179건은 불필요함을 바이트로 확인했다. 제자리 확장은
  `NOT_FEASIBLE`(풀이 bulk에 밀착·age뒤 구멍 참조9건), 재배치 경로는 구조적으로 `FEASIBLE`.
  lap399 후보는 lap400이 REJECT(제자리 성장), lap401 work가 꼬리 재배치를 구현, lap402 middle이
  독립 검수해 **재배치·fixup·패처 수리는 ACCEPT**하되 **후보 기동은 REJECT**했다 — 재배치 블록의
  99.24%가 어떤 PE 섹션에도 매핑되지 않는 신규 결함(D1, `.data` VirtualSize 산출 한 줄). 수리 카드는
  `docs/work/active/G2_POOL_SECTION_COVERAGE_REPAIR_LAP402.md`(W5).
  lap406 middle이 자칭 lap410/412 런타임 계보를 2단 검수해 항목1/2/4/5 ACCEPT·항목3(커버리지
  앵커)만 게이트 추가 지시(W6)했고, lap408 middle이 그 W6 게이트 2건을 독립 검수해 **CLOSED**
  했다(`make check` 783 passed=779+4, 역주입으로 D1 계열 포착 확인, 원본·pin 불변). lap408은
  같은 계열의 남은 사각 하나를 W7 `G2_RSRC_WRAPPER_CONTAINMENT_GATE_LAP408.md`로 발행했다
  (`.rsrc` cave wrapper 4건에 컨테인먼트 앵커 없음, 마지막 `LEGACY_COPY` 여유 49B).
  **아직 실제 게임 실행 증거가 없으므로 제품 구현 완료가 아니다** — 체크는 그대로 둔다.
  다음 회차는 W7 뒤 **즉시 P1(near-4000 live 실제 실행)** 이며, 이 첫 성공 기준(slot≥1200
  생성→관측→사망→재사용)의 독립 재현은 여전히 미검증이다.
  **2026-09-20 lap409 work 추기(원문 위는 보존):** W7 앵커 완료 뒤 P1을 착수해 marked compat
  (`4331d9cd…`) 후보로 격리 Wine에서 near-4000(3,991 live, 8owner) 규모 gate-legal 시딩→마킹저장
  (마커 `S2P1N4K1` 파일 오프셋 `0x38` 확인)→마킹로드 왕복을 슬롯 단위로 무손실 확인(소실0·id불일치0).
  slot≥1200 생성→관측→재사용 자체는 이 lap 이전에 이미 실측됐고(seed 시 slot 3977 등 관측),
  이번 lap이 새로 더한 것은 **marked compat 저장/로드가 near-4000에서 실제로 무손실**이라는 증거다.
  **이번 lap은 work 역할의 자기 결과이며 독립(다음 middle) 검수는 아직 없다.** 상세
  `docs/history/laps/20260920_lap409_work_g2_p1_compat_near4000_live_execution.md`.
  **2026-09-20 lap410 middle 추기(위 원문 보존):** lap409 P1을 원시 산출물 재계산으로 독립 검수해
  **ACCEPT**했다(후보 재현·save 해시/마커·스냅샷 diff·receipts·브리지 4001 소스·표적 5 passed·
  `SAFETY_PASS`·원본 불변). 위 21:58 지시에 따라 전체 784 게이트는 재실행하지 않았다(동일 source).
  **신규 근거:** `trace.jsonl`의 tick **2328→1567 역행**이 로드가 실제로 엔진 상태를 교체했음을 직접
  증명한다 — 이것이 없으면 "소실0"은 로드가 아무 일도 안 한 경우와 구분되지 않는다.
  **정정1:** presave 스냅샷이 저장 시점보다 ~535 tick 앞서므로 "5기는 로드 후 생산"은 사실과 다르다.
  4기는 저장 이전 생산(세이브에 포함), 로드 후 생산은 1기. 카운트는 저장 3,995→로드 3,995로 정확
  일치하나 id 단위 검증 범위는 3,995 중 3,991기다.
  **정정2(신규 결함):** 배포 진단 DLL의 `inmm_stub.c`/`ai_shadow.c`/`sfx_hook.c`/`control_executor.c`가
  stock 유닛 존재배열 `0x008990C8`과 1200 경계를 하드코딩해, 재배치 후보에서 유닛을 0기로 관측한다
  (`C:\inmm_unit_ticks.jsonl`이 3,991기 생존 중 0바이트로 실증). 전부 읽기 전용이라 손상 위험은 없고
  P1 판정에도 영향이 없으나, 향후 lap이 이 채널을 근거로 "전멸"을 오판할 위험이 있다.
  **여전히 제품 구현 완료가 아니다** — 단발 왕복 1회이며 장시간 안정성·원본 생산 경로·LAN 미검증.
  다음 회차는 work 카드 `docs/work/active/G2_COMPAT_LONG_SOAK_LAP410.md`(W8, compat 장시간 soak)다.
  상세 `docs/history/laps/20260920_lap410_middle_g2_p1_independent_review.md`.
  **2026-09-21 lap413~414 추기(위 원문 보존):** W8은 lap411 실행·lap412 ACCEPT로 닫혔고, lap413이 W9(P2,
  원본 생산 명령으로 near-cap 도달)를 실행해 **FAIL**했다 — 자원만 공급(op7)한 8인 AI 대전에서 N=4001
  후보가 **두 번 모두 tick 11,928에서 `read 0x00338400 @ 0x00414133` page fault**로 죽었고, stock-layout
  대조군은 같은 tick을 fault 없이 통과했다. lap414 middle이 요약본을 쓰지 않고 원시 산출물만으로
  재계산해 그 FAIL을 **ACCEPT**하고, fault 기전을 바이트로 확정했다(100칸 stack 배열을
  `((경로점수-1)×|유닛 이동진행도 +0x692|)/100`로 인덱싱하며, 그 명령 바이트는 원본과 동일).
  또 후보가 `.text`의 1200 즉치 54곳 중 **2곳만** 4001로 바꿨고 풀을 순회하는 잔존 1200-bound site가
  최소 3곳 남아 있음을 확인했다. **이 첫 성공 기준(slot≥1200 생성→관측→사망→재사용)은 진단 시딩으로는
  충족됐지만 원본 생산·AI 전투 경로의 안정성은 여전히 미충족이므로 체크는 그대로 둔다.**
  다음 회차는 `docs/work/active/G2_POOL_SCOPE_1200_FAULT_ROOT_CAUSE_LAP414.md`(W10)다.

- [x] 2026-09-17 12:23 KST: "일단 그 세 부분 가능 여부를 더 확실하게 알아봐". G1/G2/G4 핵심 blocker를 구별하는 제한 실행 조사; G3 재개 없음. 계측 실패를 전체 목표 불가능으로 치환하지 않는다. 세 bounded 실행카드 종료·Sol검수 리포트 `docs/reports/20260917_THREE_GOAL_FEASIBILITY_UPDATE.md` 작성; 목표완료 아님.

- [ ] 2026-09-15 11:46 KST: "조금 조사한 뒤 안 될 것 같으면 빠르게 불가능하다고 보고하고,
  될 것 같으면 빠르게 작업에 착수"한다. 조사와 문서 자체를 목표로 삼지 않는다. 각 핵심 분기는
  짧은 feasibility 판정(`FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`)으로 끝내고, `FEASIBLE`이면 다음 work
  회차부터 구현·실행 증거를 만든다. `NOT_FEASIBLE`/`BLOCKED`이면 추측성 반복 대신 근거·대안·영향을
  사용자에게 즉시 보고한다.

- [ ] 2026-09-15 11:35 KST: "대목표 4개 중 완료 0개인데 왜 진행 속도가 이렇게 느린가".
  제품 구현보다 해시·스냅샷·시간경계 등 증거 하네스 자체 보수에 과도하게 머문 운영을 교정한다.
  Astra가 큰 방향을 재판단해 G1의 남은 실제 제품 판정을 최단 경로로 닫고, 독립 파일의 G2 구조
  조사를 함께 활성화한다. 이미 충분한 안전 근거가 있는 항목을 반복 검수하지 말고, 새 제품 증거를
  만드는 작업을 우선한다. 정확성·원본 보호·저장/메모리 안전은 계속 타협하지 않는다.

- [ ] 2026-09-10 23:06 KST: 실제 루프 시작. 10분마다 한국 시간과 함께 진행상황 보고.
  Astra/high 상위 전략 → Sol/high 중간 계획·컨펌 → Luna/high 실무 순으로 명시적 1바퀴씩 진행한다.
  자동 서비스/무한 실행/자동 커밋·푸시는 사용하지 않는다.

## 처리 완료

- [x] 2026-09-20 18:34 KST: “코덱스 astra랑 클로드코드 fable도 스위치 가능하게 하자”.
  큰 방향 strategy provider를 `LOOP_STRATEGY_PROVIDER=codex|claude` 한 항목으로 선택하게
  연결했다. Codex는 `gpt-6-astra`, Claude Code는 전체 ID `claude-fable-5`를 사용하며 둘 다
  기본 medium/필요 시 high다. 자동 폴백은 없고 기존 기본값은 Astra로 유지한다.
- [x] 2026-09-20 18:45 KST: “지금 하는거 끝나면 astra -> fable로 바꿔줘”. 진행 중 검증
  종료 뒤 `loop/env.local.sh`의 현재 strategy provider를 `claude`로 바꿨다. 다음 strategy
  세션은 `claude-fable-5/medium`이며 이 설정 변경만으로 모델을 즉시 호출하지 않았다.

- [x] 2026-09-17 KST: "16인은 이제 안된다고 생각하고 접고, 나머지 3개에 대해서 현 시점 조사 결과에 대해서 자세하게 리포트". G3 중단으로 제품 범위 수정; G1/G2/G4 조사 리포트 작성. 중단은 새 불가능성 증명이 아니다.

- [x] 최신 요청: “환경세팅 다 해봐”. 격리 전체 게임 복사본·전용 Wine/Xvfb·화면/입력/
  상태 수집·증거 검사·doctor까지 환경을 마무리한다. 준비 상태 확인용 짧은 게임 스모크는 수행하되
  기능 개발/장기 부하 시험/모델 루프/서비스 시작으로 확대하지 않는다.
  아래 이전의 게임 미실행 세팅 범위는 이 제한된 환경 스모크에 한해서 갱신한다.

- [x] 2026-09-10 재확인: “아직 루프 돌리진 말고 지금 루프 엔지니어링 환경 및 하네스 세팅하는 단계”.
  설정·문서·격리된 모의 테스트만 수행한다. 실제 모델/개발 루프·게임·서비스는 시작하지 않고 STOP/비활성을 유지한다.

- [x] 모델 역할: 큰 방향/큰 플랜은Codex gpt-6-astra/high.
  중간 플랜/컨펌은Codex gpt-5.6-sol/high 또는Claude Code Opus5/high.
  그 외 실무는Codex gpt-5.6-luna/high 또는Claude Code Sonnet5/high.
  최신 지시가 Codex 전용으로만 적었던 이전 역할 요청을 확장한다. 모델역할 설정이지 유료루프 시작 요청은 아니다.


- [x] 구조: `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re_loop`와 같은 루프 엔지니어링.
  문서/새 세션/기계·다음세션·사람 판정 구조를 이관한다. 이전 엔진/세션/자격 증명은 이관하지 않는다.
- [x] 목표1: 원본이랑 똑같으면서1600×1200인 버전(혹은 패치) 만들기.
  스프라이트 단순 리사이징으로 인한 화질 열화는 차후 사용자가 이미지 따로 제작하여 패치한다.
- [x] 목표2: 8인이 **전비5000 상한**으로 플레이해도 문제 없는 버전(혹은 패치).
  단순 상한 증가가 아니라 게임 내 최대 유닛 상한/메모리 문제까지 검증·해결한다.
  메모리 초과는 사용자 제기 위험이며 원인을 실측해 생성 제한/손상/OOM/성능을 구분한다.
- [x] 목표3: 최대 **16인** 가능하게 만들기. 이전12인 언급은 최신16인 목표로 대체한다.
- [x] 목표4: 인공지능 패치 — 길찾기 알고리즘이나 자유대전의 컴퓨터 난이도.
- [x] 앞선 정정: 해상도만/뷰만 늘리고 UI 배치가 깨진 것은 요구한 결과가 아니다.

## 되물음

- [ ] 2026-09-20 lap404 strategy — **일시적 전비 초과 표시 허용 여부.** 8인 5000 144k 실측에서
  라이브 유닛 전비는 5000을 넘지 않았으나, 생산 완료 직전 한 tick 창에서 `used+reserved=5010`
  같은 일시 pending 초과가 원본 1200-slot 대조군에서도 동일하게 관측됐다(원본 고유 동작).
  (가) 이 일시 초과를 허용하고 "라이브 used ≤5000"만 강제, (나) pending 포함 strict 5000 강제
  (원본 생산/예약 순서 변경 필요, 위험). 권고는 (가).
  - **2026-09-20 lap406 middle 정정 N19(위 원문은 고치지 않고 보존):** 144k 원시 로그를
    owner별로 재계산하니 **"한 tick 창"이 아니다.** 초과 owner-표본 216건이고 값은 전부
    정확히 `used=5000, reserved=10`이며, owner6은 tick **33917→50130**(16,213 tick·97표본),
    owner5는 tick **101643→121547**(19,904 tick·119표본) 동안 **지속**됐다. 즉 (가)를 고르면
    총합 5010 표시를 owner당 **수 분(약 490초·600초)** 허용하게 된다. 라이브 `used`가 cap을
    넘은 표본은 전 soak 통틀어 0건이라는 부분만 원문대로 참이다.
  - **미증명 귀속:** "원본 1200-slot 대조군에서도 동일하게 관측됐다"를 뒷받침하는 산출물은
    이 계보에 없다 — 같은 계보 stock 대조군은 cap 1500에 max used 40, 초과 표본 0건이라
    cap 근처에 가지 않았다. 파일로 남은 유일한 stock 초과 증거는 2026-09-17
    `stock_cap_overshoot_audit_v1`의 **라이브 `used`=5003(owner1, 7표본, 원인 UNKNOWN)** 으로
    pending reservation과 **다른 현상**이다. 근거는
    `docs/history/laps/20260920_lap406_middle_g2_full_capacity_runtime_review.md`.
  - **2026-09-20 lap412 middle 기전 확정(위 원문 보존, 선택지 문구 정정 필요):** lap411 24k soak의
    owner별 시계열을 재계산하니 **"일시 초과"도 "수 분 지속"도 아니다 — 해소되지 않는 예약이다.**
    owner7은 728 PS3 표본 중 726에서 `reserved=10`이고, tick 158~24,298(전 soak의 **99.45%**)
    동안 `used=5000, reserved=10`으로 고정됐다. owner7은 24k tick 내내 유닛을 한 기도 잃지 않아
    `count`가 500에서 불변이었다. 반대로 owner3은 사망으로 `used`가 내려가면 예약이 해소됐고
    (`reserved=0` 111표본), `used<5000`일 때의 `reserved=10`은 합이 cap 이하라 초과가 아니었다.
    ⇒ 실체는 **비용 10짜리 생산 주문 1건이 큐에 걸린 상태이며 `used`가 cap 아래로 내려가야만
    해소된다.** 따라서 선택지 (가)는 "일시 초과 허용"이 아니라 **"cap에 붙은 owner가 대기 주문
    1건을 무기한 보유하는 것을 허용"** 으로 다시 읽어야 한다. 관측 범위에서 해악은 0이다
    (크래시·풀 손상·라이브 `used` cap 초과 전부 0건 / 5,824 owner-표본).
    **귀속은 여전히 미증명**이고, 다음 work 회차가 P2와 **같은 회차에** 값싼 결판 probe를 넣는다:
    stock 원본을 cap 5000으로 띄워 한 owner를 `used=5000`까지 채우고 생산 주문 1건을 건 뒤
    `reserved`를 본다. stock에서도 `5000+10`이 나오면 (가) 확정, 안 나오면 후보 고유 회귀로
    승격해 P3를 앞당긴다. 근거 `docs/history/laps/20260920_lap412_middle_g2_w8_soak_independent_review.md`.
  - **2026-09-21 lap449 middle 신규 증거 N68(위 원문 전부 보존, 선택지 미변경):** lap412가 확정한
    기전이 **수리된 신후보(`a10024de…`)·cap 근접·24k soak에서도 그대로 재현**됐다. lap448 Step1
    원시 712표본 재계산 결과 `used+reserved>5000`인 owner-표본이 **1,263건**이고 값은 **전부
    정확히 `(used 4995, reserved 10)`**, 해당 owner는 **owner4(619표본)와 owner7(644표본)
    둘뿐**이며 **마지막 표본까지 해소되지 않았다**. 라이브 `used`가 5000을 넘은 표본은
    **0건**(8 owner × 712표본 전부). ⇒ 8인 중 **2인**이 24k 내내 대기 주문 1건을 보유했고,
    나머지 6인 중 3인(owner0/2/5)은 `used`가 정확히 5000에 도달했다.
    관측 범위에서 해악은 여전히 0(크래시·풀 손상·라이브 cap 초과 전부 0).
    **여전히 사용자 판단 대기 항목이며 모델이 대신 고르지 않는다.**
    근거 `docs/history/laps/20260921_lap449_middle_g2_w21_step1_independent_review.md`.
- [ ] 2026-09-20 lap404 strategy — **전비 장부 16-bit 랩 위험의 마감 방식.** 이전(transfer)으로
  한 owner에 전역 전비를 집중시키면 signed16 장부가 랩될 수 있음이 산술로 남아 있다(게임 내
  도달성은 미실측). (B) 장부 32-bit 확장(저장포맷 동반, 큰 작업), (C) 도달성 실측 후 실제 불가면
  5000 유지(작은 작업, 단 실측로 랩이 재현되면 B로 회귀). 권고는 (C) 선행.
- [ ] 2026-09-21 lap458 work — **W23 A1 24k 연장 결과 `DECAYED` ⇒ (가) 자연 도달은 fixture/config
  축에서 NOT_FEASIBLE 확정.** 카드 `G2_A1_MAP_LEVER_LONG_WINDOW_LAP457.md` §4 고정 판정식대로
  W22 최유망 레버 A1(지도140×140)을 tick24,000까지 연장 실행한 결과, `r_late`(owner1,
  16k→24k)=0.008747 < `r_need`=0.033042(=(5000−U_min24 1,035)/120,000) ⇒ `DECAYED`.
  `U_min8`=661(owner5)로 W22 결정성 재확인, 무결성 위반 전부 0, 게임실행1회·source변경0·
  targeted7 passed·`SAFETY_PASS`. 카드가 예약한 대로 **모델은 AI/경로/생산 로직 변경에
  착수하지 않았고** 아래 되물음을 그대로 승격한다(고르지 않음, `G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md`
  §7 · `loop/ESCALATE_SOL` §36):
  - **(ㄱ)** 시딩 기반 cap 근접 + 왕복 증거(W21)를 G2 안정성 증거 축으로 인정하고 (가)를 재정의할지.
  - **(ㄴ)** G2 한정 최소 AI/설정 변경 허용 — 2026-09-21 00:20 G4 잠정 중단의 명시 예외 승인 여부.
  - **(ㄷ)** 현재 기준(자연 도달 요구) 유지, (가) 보류.
  이 3건은 바로 위 lap404 되물음(전비 장부 16-bit 랩 마감 방식)과 함께 사용자/strategy 판정
  대기 상태다. 상세 `docs/history/laps/20260921_lap458_work_g2_w23_a1_long_window_decayed.md`.
  - **2026-09-21 lap459 middle 독립검수 = ACCEPT(재계산 불일치 0)**, 위 원문 유지·선택지 미변경.
    원시 721표본만으로 비참조 재계산해 `U_min24`=1,035(owner1, tick24,012)·`r_late`=0.008747·
    `r_need`=0.033042·`DECAYED` 전부 일치, `U_min8`=661/owner5로 W22 결정성 정확 재현, 실행 **전**
    고정 기대 band 1,050~1,073 대비 실측 1,035(−1.4%).
    **판정 방향에 영향을 줄 신규 실측:** **(N81)** 정체 원인은 자원·cap·풀이 전부 아니다 — 최소
    rice 967,672/wood 969,464(지급 1,000,000의 **96.8%가 최악 시점에도 잔존**), `count` 최대
    108/1,200, `used` 최대 1,708/5,000 ⇒ **AI가 자원을 거의 손대지 않은 채 스스로 생산을 멈춘다.**
    **(N82)** 부드러운 감쇠가 아니라 owner별 **완전 정지** — owner5는 tick14,641 이후 런의 39.0%
    동안 `used` 불변(`r_late` 정확히 0.0), owner7 31.8%, owner6 15.4%.
    ⇒ 두 실측은 **(ㄴ)이 유일하게 남은 기술적 진입로**임을 시사하나, 이는 사용자 지시
    (2026-09-21 00:20)의 명시 예외 승인이므로 **모델은 착수하지 않고 승인을 기다린다.**
    **(N83) 경고:** 이 run은 바로 위 lap404 되물음에 **새 증거를 주지 않는다** —
    `used+reserved>5000` 0건(아무도 cap 근처에 못 감)이라 N68 현상이 발생할 수 없다.
    **(N84) 표현 정정:** "전 owner 감쇠"는 과장 — owner0(0.04498)·owner2(0.03749)는 `r_need`를
    후반에도 넘는다. 판정이 유지되는 이유는 G2가 "8인 **각각** 5,000"이라 최저 owner가 구속
    조건이기 때문이다. 정확한 서술은 "8인 합계가 24k에서 11,207 = 8×5,000의 **28.0%**".
    상세 `docs/history/laps/20260921_lap459_middle_g2_w23_a1_independent_review.md`.
  - **2026-09-21 lap460 strategy(Fable5) 처분(`ESCALATE_SOL`§38, 원문 보존·사용자 번복 가능):**
    **(ㄱ) 채택·(ㄷ) 기각** — G2 원문 계약은 "cap5000 플레이 안정"이므로 gate-legal 시딩
    cap근접+soak+왕복을 증거 축으로 인정(마일스톤 승인 대체 아님, 자연 도달 계속 요구 시 번복).
    **(ㄴ)은 모델이 고르지 않고 사용자 승인 대기 유지**(승인 전 AI/설정 변경 착수 금지).
    lap404는 **(가) 잠정 채택**(stock cap5000 `reserved` rider probe를 W24에 의무화, 미재현 시
    회귀 승격·재심). F4는 **(C) 채택**(soak에서 랩/음수 관측 시 즉시 STOP 후 (B) 재심). 다음은
    middle이 **W24**(혼합 구성+전투/사망/재사용 순환 24k) 1장 발행, **144k 금지는 W24 ACCEPT까지 유지**.
  - **2026-09-21 lap461 middle 신규 실측 N87 — (ㄴ)의 무게가 커졌다(선택지 미변경, 모델은 고르지 않음):** lap448에서 8 owner의 배치 주사 구간은 전 쌍에서 겹쳐(2-3 501셀·6-7 484셀 등) 적 유닛이 24,000tick 내내 셀 단위로 인접했는데도 소실은 **4기/1,166기**뿐이었다 ⇒ "전투/사망/슬롯 재사용" 축도 **기하(fixture)로는 만들 수 없음**이 실측됐고, 남은 fixture 내 가설은 구성(타입) 하나뿐이다. 그것마저 실패하면 자연 도달에 이어 **전투 축까지 (ㄴ) 승인 없이는 닫히지 않는다.** W24는 그 결과를 `NO_ENGAGEMENT`로 정직하게 보고하도록 실행 전에 고정했고 **승인 전 AI/생산 정책 변경에는 착수하지 않는다.** 근거 `docs/history/laps/20260921_lap461_middle_g2_w24_issue_and_combat_axis_finding.md`·`ESCALATE_SOL`§39.

실제 구현 선택이 목표·안전·배포 범위를 바꿀 때만 새 질문을 추가한다.

## 2026-09-17 15:20 KST — G2 최우선 루프 재개
- [x] 사용자: "8인 각각 전비 5000 안정 플레이 이걸 최우선 목표로 좀 파보자. 루프 ㄱㄱ". 큐/우선순위 반영(제품완료 아님). G1/G4 후순위, G3중단 유지.

## 2026-09-17 21:16 KST — 사용자 루프 시간 상한
- 사용자: “한국시간 기준12시까지만 루프 돌릴거야. 이후는 진행속도나 가능성 생각해서 볼테니까 그거 생각해서 진행해봐”.
- 현재21:16이므로 Root는 **오늘밤자정2026-09-18 00:00KST**를 보수상한으로 잡았다고 사용자에게 명시했다. 정오를 뜻한 경우 정정 대기; 답변전에는 더짧은상한 유지.
- 10분마다KST보고, 상한에서신규작업중단/ownedcleanup/성과·가능성정리. 기존 STOP 예산리셋·목표축소·제품승인 아님.

## 2026-09-18T17:56:55.515225+09:00 — Claude Code 전환 및 루프 재개
- 사용자: “ㅇㅇ 그렇게 가보고 루프 다시 돌려”. 중간계획/검수ClaudeCode Opus5/high, 실무ClaudeCode Sonnet5/high, 큰분기Astra medium(필요high) 유지. 새명시재개는어제00상한종료이후재개허가이며원제품목표/원본안전/실패보존유지. 이전STOP기술카드예산자동리셋/제품승인아님. 10분KST보고 유지,서비스/커밋/자동push안함.

## 2026-09-21 lap423·429·438·440·442 운영 회수 계보 (lap462 압축 — 원문 전량 보존, 삭제 없음)
- 이 5건(lap423 P-H 동기복구·lap429 디스크blocker해소·lap438 W18 동기복구·lap440 W19 동기검증회수·
  lap442 W20 background회수+lap441 middle W19 ACCEPT(R1) 독립검수)은 **모델/Root가 쓴 운영 회수
  기록**이며(사용자 지시 아님), INBOX 400줄 상한(`checks/context_limits.py`)에 걸려 lap462가
  포인터로 줄였다. **압축 직전 INBOX 전체 원문**은 `docs/history/20260921_inbox_lap462_precompaction.md`
  (SHA `d67aed38931b542b2333e60d157d32d4f26a8e370e0946312773fec83113b03d`, 415줄)에 보존했다.
  핵심 결론은 STATUS.md G2 표/검증상태(lap441~443 항목)에도 그대로 남아 있고, 개별 lap 전문은
  `docs/history/laps/20260921_lap429_work_g2_w16_disk_blocker.md`·
  `20260921_lap441_middle_g2_w19_independent_review.md`(§8에 lap440 산출물 기반 보존)·
  `20260921_lap443_middle_g2_w20_t2_independent_review.md`(lap442 실행분 인용)에 있다.
  lap423/438 자체는 개별 lap 기록 파일이 없어 이 압축과 위 precompaction 스냅샷이 유일한 원문이다.

## 2026-09-21 lap425·427·428 계보 (lap449 압축 — 원문 전량 보존, 삭제 없음)

- 이 세 항목은 **모델이 쓴 회차 기록**이며(사용자 지시 아님), INBOX 400줄 상한(`checks/context_limits.py`)에
  걸려 lap449가 포인터로 줄였다. **압축 직전 INBOX 전체 원문**은
  `docs/history/20260921_inbox_lap449_precompaction.md`
  (SHA `ebf58faa31504434bea55ce10475142591bc1a649278b83c1ea54b0cd4288086`, 411줄)에 보존했고,
  각 전문은 `docs/history/laps/20260921_lap42{5,7,8}_*.md`에 그대로 있다.
- **lap425 work(W14 P-I):** base_stat 10 불변으로 판정 A 배제, K(`+0x700`)가 tick10400에 `0→22432`
  단독 점프 ⇒ **판정 (B) `+0x700` 자체가 표적** 확정. `+0x68c`/`+0x688`은 하류 결과.
- **lap427 work(W15 P-J):** 476표본에서 `K`와 `sib`(`+0x6fc`) 동시 전이, `src`(`+0x388`) 전 구간 0
  ⇒ 당시 **(J2) 외부write·(J3) 블록write 확정**으로 보고하고 상위 판정 요청.
- **lap428 middle:** 측정은 **ACCEPT(불일치0)**, 해석 2건 정정 — **N40으로 (J3) 강등**(판별자
  "이웃 동시변화=블록write"가 거짓, 언롤루프 `0x4130e6~0x41313a`도 이웃을 함께 바꾼다),
  N41로 (J2) 근거 교체(결론 유지), 신규 N42·**N43**(`unit3565+0x700`은 1200 순회 최대도달보다
  `0x43DF50` 위 ⇒ "슬롯0..1199 순회 site"는 범인 아님), W16 발행.
- **⚠ 이후 뒤집힌 부분:** **lap439 N51이 (J2)·(J3)·(K2)를 전부 REJECT**했다 — 진범은 외부 write가
  아니라 후보 빌드의 **immediate 재배치 오탐**(`0x0040F053` 종료 즉치)이고 세 store는 원본과 바이트
  동일했다. **(L2)·N43은 유지.** 현재 유효한 결론은 STATUS G2 표와 `loop/ESCALATE_SOL`§25를 따른다.


## 2026-09-21 Root 회수 — lap448 W21 Step1 24k cap-proximity soak 완료
- lap448 work가 빌드 후 장시간 Wine 실행을 background로 넘기고 종료하며 자식이
  정리됐다. Root가 중복 프로세스가 없음을 확인한 뒤 동일 스크립트를 새 temp 디렉터리에서
  동기 회수 실행했다. evidence:
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260921_lap448_w21_step1_cap_proximity_soak_root_recovery/`.
- repaired candidate SHA `a10024de...`, N=4001. 8 owner 모두 AI=1, 시드 직후
  `used=4900..4945`, 최종 `4995..5000`. 712표본, tick24029 도달, fault/crash 0,
  5000 초과 0, `live == sum(owner.count)` 불일치 0, max_live1247, source SHA 불변.
  W21 `(U1)~(U3)`는 실행기 자체 판정 PASS, verdict `CAP_PROXIMITY_STABLE`.
- 메모리: RSS max247288KiB/final51612KiB, VmSize 3463564KiB, 최종 VmSwap129104KiB.
  swap 발생은 즉시 crash는 아니지만 안정성 판정에서 별도 검토해야 한다.
- 추가로 N59 신후보 재확인 PASS(owner0 tick284 baseline 이탈), N60 기존 goal
  A/B 대조 PASS(owner0.ai=0 vs new goal=1). 다음 middle은 Step1 원시 표본을 독립 검수하고,
  ACCEPT 시 W21 Step2 신후보 저장/로드 왕복을 지시한다.
- **2026-09-21 lap449 middle 회수(위 원문 보존):** 지시대로 `run_summary.json`과 이 회수 서술을
  판정 입력으로 쓰지 않고 원시 `samples.jsonl` 712표본만으로 재계산해 **ACCEPT(불일치 0)**.
  **(U1) PASS 8/8 · (U2) PASS(tick24,029·live `used`>5000 0표본·fault 0) · (U3) PASS(712표본
  전부 장부 정합)** ⇒ `CAP_PROXIMITY_STABLE`(**부분 증거**). 카드 §10 의무 4건(N59/N60/N61/N63)
  전부 이행 확인 — 특히 **N60은 CLOSED**인데 결정적 근거는 run 간 대조가 아니라 **대조군 run
  내부**에서 owner0만 `ai`=0이고 owner1~7이 1인 패턴이 소스 `control_executor.c:913`과 일치한다는
  점이다(두 arm은 stock1200/4001로 빌드 축이 다름).
  **(U4) 메모리는 절반 귀속:** `vm_size`가 712표본 전부 3,463,564KB 단일값이라 주소공간 해제는
  0건이고, 1MB 이상 RSS 하강 26건(합 −197,584KB) 중 **23건(−131,824KB)은 swap 증가 동반
  (+129,340KB) ⇒ 호스트 회수 확정**, **3건(tick11,288~11,355, −65,760KB)은 그 시점까지 swap이
  0이라 clean 페이지 축출과 게임 측 해제를 분리할 수 없어 UNKNOWN**으로 남긴다(N57의 2/3만 닫힘).
  Root가 지적한 swap 발생은 **호스트 메모리 압박의 결과로 측정**됐다(host `MemAvailable`
  5.47GB→2.42GB).
  **그러나 지시하신 "ACCEPT 시 Step2" 순서는 한 칸 미뤘다** — 카드 §7의 **fail-closed 산출물
  `lap413_stock_comparison.md`가 없다**(N66, W19 Step4·W20 Step3·W21 Step3로 **3회 연속 누락**).
  이 표는 게임 실행 없이 기존 파일만으로 만들 수 있으므로 다음 work의 **첫 산출물**로 강제하고,
  그 뒤에 Step2를 실행하게 했다(카드 §11). **W21 카드는 (U5) 미실행이라 CLOSED 아님**,
  따라서 **144k 발행 금지도 유지**된다. 신규 N64(lap448 자체 lap 기록 없음 — lap440·442·448
  3회 연속)·N65(실행기 verdict 식이 `U3_pass` 미사용)·N67(시딩이 비용 기준 99.0% 단일 type이라
  "혼합 구성" 서술 과장)·N68(위 되물음 항목에 추기).
  상세 `docs/history/laps/20260921_lap449_middle_g2_w21_step1_independent_review.md`.
