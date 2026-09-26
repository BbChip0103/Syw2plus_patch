# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

lap686(work)이 lap685 18:19 운영자 이분 탐색 지시를 실행했다. **① sparse(≤20) 방법 자체가
반증됐다(FALSIFIED):** v1/v2의 5개 편집 묶음을 원본에 각각 단독 적용(G1/G2/G3/G5) 또는
V1_FULL/V2_FULL(G4는 원본에 단독 적용 불가능함을 실측 확인 — v2 훅 사이트가 v1 재배치 오퍼랜드와
겹침)로 빌드해 20기 이하 드래그로 측정한 결과, 원본 17/19·V1_FULL 13/19·V2_FULL 12/19로 **모두 같은
구간(63~89%)** — 어느 묶음도 ≤20 규모에서는 원본과 구별될 만큼 깨지지 않는다. **② 대신 V1_FULL을
lap682/685와 같은 dense-50 규모로 실행해 회귀를 처음으로 부분 귀속했다: `ever_command4_count=18/49`
(37%)** — 같은 규모의 V2_FULL(=v2, lap685) `0/49`·v3 `≤1/49`보다 극적으로 낫다. **H1/H2/H3(G4) 훅이
지배적 원인**이며, v1 단독에도 100%→37%의 별개 잔여 결함이 남는다(원인 미확정). 상세
`docs/history/laps/20260926_lap686_work_g5_bisection_localizes_regression_to_control_group_hooks.md`.
이전(lap685) 요약: 청크드 빌더/디스패치 무관 확정(①③ 반증), 옛 선택배열 리터럴 잔여 0건(② 반증) —
원인을 "재배치 이후 하류"로 좁혔던 것을 이번 lap이 "H1/H2/H3 훅"으로 더 좁혔다.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 제품 미완료 | 1600×1200 원본 구도 외 사용자/제품 승인 |
| G2 | 전비5000 단계 사용자 판단으로 달성(2026-09-26). **새 목표 8인 각 전비10000** 제품 미완료 | 8인 전비10000 도달·교전/생산/저장·지원 동기화, 개인1200/풀 병목 측정, 사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 제품 미완료 | AI 개선 제품 비교·post-load·사용자 승인 |
| G5 | **v3 roundtrip·이동 paired PASS(lap682/684). 공격 브로드캐스트 FAIL — lap686이 원인을
H1/H2/H3(G4) 훅으로 대부분 귀속(V1_FULL 37% vs V2_FULL/v3 ≈0~2%), v1 단독 잔여 결함(100%→37%)은
별개 미확정** | H1/H2/H3 훅의 attack 간섭 지점 특정·수정, v1 잔여 결함 조사, 새 middle 재검수,
멀티 동기화 표시, 사용자 milestone 승인 |

## 지금 막힌 것 (Blockers)

G5 2단을 막는 단일 블로커는 **공격(type4) 주문이 곧 되돌려지는 것**이지만, lap686이 이를 두 겹으로
나눴다: (a) **H1/H2/H3(G4) 훅이 지배적 원인**(V1_FULL dense-50 `ever_command4_count=18/49`(37%) vs
V2_FULL/v3 ≈0~2/49) — 정확한 간섭 지점(PC)은 아직 gdb로 확인되지 않았다. (b) v1 단독에도 원본
100%→37%의 **별개 잔여 결함**이 있다(원인 미확정, G1/G2/G3/G5 중 하나 또는 조합). lap685가 이미 배제한
청크드 빌더/디스패치 경로와 옛 선택 배열 리터럴 잔여는 여전히 원인이 아니다.

## 검증 상태

lap686(work): 원본 SHA `b56986e0…c9c08a8ac` 불변. 신규 후보 SHA V1_FULL `6c8f73ba…`(=v1과 동치, 테스트로
고정)/V2_FULL `ae495fa5…`(=lap665/685의 v2와 정확히 일치, 교차검증). sparse probe 3회+dense probe 1회
전부 `source_unchanged=true`, `cleanup.ok=true`. targeted pytest 34 passed(신규 14, 3파일). `make check`
**994 passed(711.56s)**, ruff/compileall/mypy/`CONTEXT_PASS` 모두 PASS
(`logs/gates/20260926_lap686_make_check_run1.log`). `checks/safety.sh` → `SAFETY_PASS`. 디스크: 시작
107GB, 4회 실행분(각 ~2.7GB game 사본 즉시 정리) 후 107GB.

## 다음 한 가지
**2026-09-26 19:25 운영자 판정(lap687 관측 반영, 다음 work용):** 같은 후보(v2+H1)가 1회차 `ever_command4_count` 0, 2회차 18 ⇒ **공격 probe가 비결정적**이다. 단발 0/18로 원인을 가르는 이분 탐색·훅 추적은 중단한다. 다음 work: ① 공격 probe의 흔들림 원인(적 스폰 위치/시점, 목적지 변환, 공격 가능 판정 P6, 선택 순서)을 raw로 1회 비교해 가장 유력한 1개를 고정(구현 우선). ② 고정 후 **v3 50기 N=5, 원본 20기 N=5** 반복 측정해 `ever_command4_count/attack_capable` 비율 분포로 판정 — 후보 중앙값이 원본 비율(≈85~95%)과 같은 수준이면 공격 50 PASS. ③ 결과 들고 middle 재검수.
**2026-09-26 18:59 운영자 승인+힌트(lap686 다음 한 가지, 회부 없이 work):** H1/H2/H3(부대 그룹 훅) 간섭 지점을 좁힌다. 순서: ① **v3에서 H1/H2/H3를 하나씩 뺀 후보 3개**로 dense-50 공격(`ever_command4_count`) 1회씩 → 공격을 살리는 훅 1개 특정(싼 판별 먼저). ② 특정된 훅의 패치 지점이 공격 경로와 공유되는지 정적 확인 — 특히 H3의 `FUN_0040F790` 호출 뒤 3바이트 NOP(스택 이중 정리 수정)이 **다른 호출자(공격 명령 경로)에서도 실행되는 공유 코드**라면 그 경로의 스택 균형이 깨진다; 또 H1/H2가 unit `+0x344` 외 필드(공격 대상 `+0x38C` 인접 등)를 쓰는지 확인. ③ 훅을 호출자 한정(케이브 안에서만 정리)으로 고친 뒤 원본20/후보50 공격 paired 2회 + 그룹 roundtrip 재확인.
**2026-09-26 lap686(work, 자체 기록):** 다음 work는 middle 없이 H1/H2/H3(v2) 훅이 attack 유지를 깨는
정확한 지점을 gdb로 좁힌다 — 후보는 (i) H2/H3가 쓰는 unit `+0x344` 필드나 그 근처가 attack의
`+0x384`/`+0x290` 상태와 메모리를 공유/겹치는지, (ii) H3의 `FUN_0040F790`/`FUN_0040F7D0` 호출 경로가
lap677이 찾은 `FUN_0040C640`(pending 컨슈머)의 분기 조건에 영향을 주는지. 찾으면 H 훅을 최소 수정한 뒤
`tools/g5_worker_relative_move_attack_probe_v2.py`로 dense-50 재실행해 `ever_command4_count`가
V1_FULL의 18/49 수준 이상으로 회복되는지 확인한다. 그 다음에야 v1 단독의 잔여 결함(100%→37%)을 별도로
조사한다(우선순위 낮음). 상세 handoff는
`docs/history/laps/20260926_lap686_work_g5_bisection_localizes_regression_to_control_group_hooks.md`.

## 바퀴 기록

- lap686(work): lap685 18:19 이분 탐색 지시 실행. **① sparse(≤20) 방법 자체가 반증됐다**: G1/G2/G3/G5
  단독 + V1_FULL/V2_FULL(G4는 원본에 단독 적용 불가 — 훅 사이트가 v1 오퍼랜드와 겹침, 실측 확인)을
  20기 이하 드래그로 측정 → 원본17/19·V1_FULL13/19·V2_FULL12/19로 모두 같은 구간, 어느 묶음도 ≤20에서
  구별되게 깨지지 않음. **② V1_FULL을 dense-50 규모로 실행해 회귀를 처음 부분 귀속**:
  `ever_command4_count=18/49`(37%), 같은 규모 V2_FULL(lap685) 0/49·v3 ≤1/49보다 극적으로 나음 —
  H1/H2/H3(G4) 훅이 지배적 원인, v1 단독도 100%→37% 잔여 결함 있음(별개, 미확정). 신규 도구 3개+테스트
  3개(14 assert), 제품 EXE 0 변경. `make check`994 passed(711s), SAFETY_PASS. 상세
  `20260926_lap686_work_g5_bisection_localizes_regression_to_control_group_hooks.md`.
- lap685(work): lap684 핸드오프 가설("청크 재호출 사이 필드 손실")과 17:55 운영자 가설("옛 선택 배열
  리터럴 잔여")을 gdb 트레이스 3종+v2 대조군+정적 전수 xref 스캔으로 **모두 반증**. 빌더/디스패치
  경로는 move·attack 동일(50/50), v2(청킹 없음)도 v3처럼 `ever_command4_count=0/49`로 실패해 청킹
  무관·재배치 이후 공통 회귀로 확정. 옛 배열(`0x899024/28/2A/78`) 리터럴 참조는 원본 전체(raw 52건)가
  전부 v1 표로 이미 설명되어 잔여 0건. 신규 read-only 진단 도구 5개+테스트 4개, 제품 EXE 0 변경. 과거
  lap들의 미정리 디스크(108GB) 정리. `make check`980 passed(683s), SAFETY_PASS. 상세
  `20260926_lap685_work_g5_attack_broadcast_field_loss_falsified_relocated_downstream.md`.
- lap684(work): v3 roundtrip 도구를 v2→v3로 갱신해 **PASS**(후보50/50/50, 원본20/20/20, crash 0) 확정.
  공격 판정을 `command==4` 살아있는 상태로 시도했으나 원본에서도 0이 나와 판정 필드 결함을 발견,
  16:35 지시대로 `+0x384==0x1000004`+3초 누적 `ever_command4_count`로 교체해 원본 2/2 100%(19/19) 대비
  **후보 2/2 ≤1/49**의 재현 가능한 실제 결함으로 좁혔다(이동 청크분할50/50은 이미 PASS와 대조). 신규
  테스트 1개, 제품 EXE 0 변경, `make check`973 passed(648s), SAFETY_PASS. 상세
  `20260926_lap684_work_g5_v3_roundtrip_pass_attack_command4_blocked.md`.
- lap683(middle): G5 v3 `e5004764…` 독립 검수 → **HOLD**. 크래시 수정·이동 paired 50/20은 승인.
  공격 "pending 50/50"은 `pending!=1` 판정식 결함이다(raw `command==4` 0/50). lap681 41/50은 원본 paired가 없고
  재현되지 않았다. v3 roundtrip은 미실행. 제품 0 변경, targeted 17 passed. 상세
  `20260926_lap683_middle_g5_v3_independent_review_hold.md`.

- lap682(work): lap681의 "지도 시드 고정" 지시를 self-calibration 방식으로 대체 구현해 **원본20/
  후보50 paired MOVE 수렴 PASS**를 재현 2/2로 확정. calibration 배열 버그 1건, 순간-동시-일치
  판정 결함 1건을 같은 lap 안에서 발견·수정. ATTACK은 UI 클릭 한계 6번째 재확인(좌표 문제 배제
  완료). 신규 도구 1개+테스트 1개, 제품 EXE 0 변경. `make check`972 PASS. 상세
  `20260926_lap682_work_g5_worker_relative_move_convergence_pass.md`.
- lap681(work): lap680의 "이동 pending 0/50"을 3초 재대기로 재확인해 **타이밍 아티팩트임을
  확정**(50/50 재현, `command`도 점진 반영). 이어서 시도한 원본20/후보50 paired 재측정 2회가
  **지도 시드 미고정으로 인한 probe 결함**(worker 시작위치/지형이 실행마다 달라 고정 픽셀
  목적지가 무효해짐)으로 무효 판정됨을 실측으로 확인, G2식 시드 고정 이식을 다음 한 가지로
  제시. 신규 read-only 진단 도구 3개, 제품 EXE 0 변경. `make check`970 PASS. 상세
  `20260926_lap681_work_g5_move_pending_timing_and_map_seed_fragility.md`.
- lap680(work): v3 분할발행 크래시의 근본 원인을 바이트 단위로 확정 — wrapper 백업 버퍼
  `[ebp-0x50,ebp)`가 청크 호출의 인자+반환주소 저장 영역과 겹쳐 청크2의 반환주소(`0x004E4E1C`)가
  entries[14]로 복사되고, 그 하위워드(19996)가 미확인 소비자(`0x499336`)의 무경계 accessor
  (`0x40FED0`)에 전달되어 실측 크래시 주소(`0x2a45aaa`)를 그대로 재현함을 라이브로 증명. `sub
  esp,0x50` 1줄로 수정(SHA `e5004764…`), v2 대조군(청킹 없음, 이상값 0건)으로 원인을 청킹에 확정
  귀속. 재검증: 크래시 없음, 공격 paired50 PASS(이번 조사 전체 최초), 이동은 pending 0/50으로 별개
  미해결. `make check`970 PASS. 상세
  `20260926_lap680_work_g5_v3_chunk_backup_overlap_fixed.md`.
- lap679(work): gdb 하드웨어 watchpoint 상관(단일세션·단일·첫주문·하드코딩 스택주소)으로 G5 20-상한
  루트코즈를 `0x004AE550`(`mov ebp,0x14` at `0x4AE5F4`)로 확정. 22개 정적 호출지점은 전부 무관 UI
  opcode임을 재확인(실제 호출은 간접, 경로 미확정). 13:09 지시대로 분할발행(최대3회) 코드케이브 `v3`
  구현·빌드(SHA `a698a8f9…`, `make check`968 PASS) — 그러나 실런타임 크래시(`0x40FEE0` 슬롯 accessor,
  page fault). 부수적으로 "2번째 주문은 기존 레코드 in-place 갱신이라 재복사가 없다"는 별도 원인을
  메모리 diff만으로(gdb 불필요) 확정해 이전 lap678의 미해결 질문("스택 빌더 특정")을 완전히 해소.
  제품 원본 0 변경, 신규 진단 도구 5개+신규 후보 패치 모듈 1개(uncommitted). 상세
  `20260926_lap679_work_g5_order_builder_found_chunked_dispatch_crash.md`.
- lap678(work): 신규 gdb 원자 스냅샷으로 MOVE·ATTACK 둘 다 정확히 20/50만 pending 수신(선택 배열
  처음 20개, 순서 상한)을 확정. hardware watchpoint+`[esp]` 반환주소 읽기 체인으로 20-상한이 60바이트
  "주문 레코드" 구조체의 unit-list 하위배열 자체(20-word 고정) 하드캡임을 확정. 스택 빌더는 미도달
  (→ lap679가 해소). 상세 `20260926_lap678_work_g5_pending_broadcast_writer_found.md`.
- lap677(work): gdb 진입-카운트 트레이스로 `FUN_0040C640`(전체 유닛 매틱 순회 컨슈머)을 발견,
  raw 호출횟수가 "몇 명이 명령 받았는지"의 증거가 아님을 확인. harness 결함 3종 발견·수리. 상세
  `20260926_lap677_work_g5_order_issuer_dynamic_trace.md`.
lap676 이전 요약은 `docs/history/laps/`에 원문 보존(포인터: `20260926_lap676_work_g5_command_packer_xref_falsified.md`).

G5의 선택/호출/이동/save-load 부분 runtime 증거와 과거 실패 provenance는 `docs/history/laps/` 및
공유 `temp/Syw2plus_patch/`에 보존한다. 공격50·크래시 없는 분할발행이 없어 전체 2단은 미완료이며
제품 G5 PASS·사용자 milestone 승인은 없다.
