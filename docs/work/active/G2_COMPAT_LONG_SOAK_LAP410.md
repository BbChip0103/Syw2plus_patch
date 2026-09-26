# W8 — marked compat 후보 장시간 soak (발행: lap410 middle, 수행: lap411 work)

> **2026-09-20 lap412 middle — 이 카드는 CLOSED.** lap411의 실행 결과를 원시 증거에서 독립
> 재계산(불일치 0건)해 §2 (a)~(f) 전부 ACCEPT, (e)만 조건부(3표본/727초는 누수 부재 증명 아님;
> 후반 기울기 외삽 약 18.8 MiB/시간 → P4에서 재측정). §3(정정1 반영)은 presave→save 간격 535tick
> → **5tick**으로 실제 개선 확인. §4는 **미이행(N21)** — 요구된 "stub 채널에 근거하지 않음" 명시
> 문장이 산출물에 없다. 실질 무해(이번 검수가 쓴 근거에 해당 채널 산출물 0건)이므로 재수행 없이
> 기록만 남기고 닫는다. §6은 lap411이 오면제했고(N22) lap412가 통합 경계 gate를 대신 실행했다.
> 검수 전문 `docs/history/laps/20260920_lap412_middle_g2_w8_soak_independent_review.md`.
> 후속은 W9(P2). **이 카드로 되돌아오지 않는다.**

- 발행자 / 역할: lap410 Claude Code claude-opus-5 / high / middle. 근거는
  `docs/history/laps/20260920_lap410_middle_g2_p1_independent_review.md`.
- 수행 역할: **work (Sonnet5/high)**. 이 카드는 실제 게임 실행 카드다. 계획/재검토 회차로 되돌리지 않는다.
- 선행 상태: lap409 P1 **ACCEPT**(lap410 독립 검수 완료). 단발 왕복은 닫혔고, 남은 것은 **지속 안정성**이다.
- 목표 연결: G2 = 활성 8인 각각 전비 5000 안정성. 이 카드는 그중 **안정성** 축을 실제 실행으로 만든다.

## 1. 대상 고정 (변경 금지)

- 후보: `g2_full_capacity_v1_n4001_persistence_compat`
  SHA `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`
  (`build_candidate(original, 4001)`로 재생성. lap410이 재현성 확인함.)
- 원본: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — 읽기 전용, 실행 전후 재해시.
- 브리지: `python3 -m patches.population.build_runtime_bridge --out-dir <tmp> --unit-pool-capacity 4001`
  **반드시 4001로 새로 빌드하고**, 배포 전에 `supply_bridge_build.json`의
  `unit_pool_base=0x0108C000` / `unit_existence_base=0x017B8658`를 눈으로 확인한다.
  (lap409는 stock 브리지를 재사용해 1차 프로세스를 통째로 날렸다. 재사용 금지.)
- 격리: `tools.runtime_env.prepare()`로 **신규** 게임 사본 + prefix + 빈 display. 기존 run 디렉터리 재사용 금지.

## 2. 성공 / 실패 측정식 (먼저 적고 시작한다)

부팅: title 클릭 → PS7 → goal `_custom_game_chain_inject_g2_eight_seed42` → PS3, 8 owner `cap=5000` 확인.
시딩: 진단 브리지 op=6(gate-legal) 로 8 owner 합계 **≥3,900 live** 도달.

그 뒤 **연속 24,000 tick 이상** 자연 simulation을 돌리며 아래를 측정한다.

PASS 조건 (전부 충족해야 PASS):
- (a) 프로세스 생존: 크래시/행 0회, 24k tick 완주.
- (b) 라이브 `used` ≤ 5000 위반 표본 **0건** (owner별 전 표본). `used+reserved` 일시 초과는
  N19/되물음 미결이므로 **표본 수·지속 tick·owner를 기록만** 하고 PASS/FAIL 판정에 쓰지 않는다.
- (c) 풀 무결성: 슬롯 중복 배정 0, `internal_id` 충돌 0, owner 필드 손상 0.
- (d) **사망 → 슬롯 재사용이 slot≥1200 구간에서 실제로 관측**된다(최소 1건, 재사용 후 필드 정상).
- (e) 메모리: RSS가 soak 구간에서 단조 증가로 발산하지 않는다(시작/중간/끝 3점 + 기울기 기록).
- (f) 저장/로드 왕복 1회를 soak **중간**에 수행하고 무손실.

FAIL 조건: 위 중 하나라도 위반. FAIL이면 **baseline을 고쳐 통과시키지 않고** 수치와 함께 보고한다.

## 3. lap410 정정 1 반영 — 필수 절차

lap409의 대조는 저장 시점보다 ~535 tick 앞선 스냅샷을 기준선으로 써서 4기가 id-미검증으로 남았다.
이번에는 **저장 직전에 `runtime_driver` 스냅샷을 찍고, 그 직후 즉시 op=2 저장**한다.
저장과 스냅샷 사이 tick 간격을 산출물에 기록하고, 가능하면 0에 가깝게 만든다.
로드 후 스냅샷과 대조할 때 **저장 시점 tick과 로드 복원 tick을 함께 기록**한다
(`trace.jsonl`의 tick 역행이 로드가 실제 일어났다는 유일한 직접 증거다 — 반드시 보존).

## 4. lap410 정정 2 반영 — bounded, 시간 상자 20분

배포되는 `_inmm.dll`에는 `runtime_bridge.c` 외의 stub 모듈이 stock 주소 `0x008990C8` / 1200 경계를
하드코딩한 채 남아 있다(`inmm_stub.c:331`, `ai_shadow.c:30`, `sfx_hook.c:158`,
`control_executor.c:1576,2538`). 재배치 후보에서 이들은 **유닛 0기로 관측**한다(이번에 `C:\inmm_unit_ticks.jsonl`
0바이트로 실증됨). 읽기 전용이라 손상 위험은 없다.

- 해야 할 것: 이 soak의 **어떤 결론도 위 채널 산출물에 근거하지 않는다**는 것을 산출물에 명시한다.
  근거는 `runtime_driver` 외부 스냅샷과 `runtime_bridge.c` 경로만 쓴다.
- 여유가 있으면(20분 이내): `build_runtime_bridge.py`가 재배치 빌드일 때 위 4개 모듈의 stock VA도
  함께 치환하거나, 해당 덤프를 비활성화한다. **20분을 넘기면 중단하고 문서화만 하고 soak으로 넘어간다.**
  이 항목 때문에 soak을 미루지 않는다(INBOX 2026-09-20 21:58: 하네스 작업으로 실제 실행을 늦추지 말 것).

## 5. 범위 밖 (건드리지 말 것)

- P2(원본 UI/명령 생산 경로로 시딩 대체) — soak PASS 뒤 별도 카드.
- strict cap / 전비 장부 32bit 확장(N19·F4·되물음) — 사용자 답변 대기.
- LAN(P4), G1, G4, G3(중단).
- 후보 바이트·wrapper 배치·`RSRC_COMPAT_END_OFFSET`·핀 SHA 변경 — 전부 금지.
- 목표 숫자(8인/5000/4001) 임의 조정 금지.

## 6. 검사

- 표적: `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py -q` (현재 5 passed).
- source를 바꿨을 때만 통합 경계에서 `make check` 1회. 안 바꿨으면 재실행하지 않는다
  (INBOX 2026-09-20 21:58).
- 매회 `checks/safety.sh check` → `SAFETY_PASS`, 원본 2경로 재해시 불변, 종료 후 잔류 프로세스 0.

## 7. 산출물

증거는 `temp/Syw2plus_patch/g2_capacity/<날짜>_lap<N>_compat_soak/`에 두고
`docs/history/laps/`에 lap 기록(날짜/lap/목표/가설/변경파일/원본·후보SHA/실행명령/수치/PASS·FAIL·SKIP/
fixture/다음행동)을 남긴다. STATUS의 「다음 한 가지」를 갱신한다.

## 8. 중단 조건

- 실패 가설 2회 또는 60분 안에 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED` 판정.
- 크래시/포인터 손상/저장 이상이 나오면 숨기지 말고 그 수치로 보고하고 멈춘다.
- 자기 결과를 자기가 최종 승인하지 않는다. 다음 middle 회차가 독립 검수한다.
