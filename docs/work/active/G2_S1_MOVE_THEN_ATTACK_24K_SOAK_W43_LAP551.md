# W43 — G2 S1 이동 후 공격 2단 입력 24k 순환 soak (lap551 middle 발행)

- 발행: lap551 middle (Codex native session, middle tier/high; session model ID는 노출되지 않아 미확인), 2026-09-24 KST. 상태: **발행, 미실행**.
- 실행: 다음 **work tier(Codex `gpt-5.6-luna`/high)**. 그다음 새 middle 세션이 원시 산출물만으로 독립 검수한다.
- 상위 근거: `G2_STRATEGY_W42_MOVE_THEN_ATTACK_LAP548.md` §3 첫 행, lap550 W42, lap551 독립 재계산 `ACCEPT`.
- 목표: gate-legal 시딩으로 8 owner를 `used=4,950`에 무장하고, 네 짝 모두 원본 이동(op9)→인접 도착→원본 공격(op8)을 반복해 tick 24,000까지 전투·사망·재생산·저장/로드 안정성을 측정한다.
- 이 카드는 G2 제품 합격이나 사용자 3단 승인이 아니다. 144k는 `DRIVEN_CYCLE_STABLE`의 다음 middle ACCEPT 전까지 닫혀 있다.

## 0. 안전·소스 경계

1. 제품 EXE/AI/생산/건설 코드 변경 0, op4 0회, 편 byte·설정 값 쓰기 0. 원본 SHA `b56986e0…c9c08a8ac` 전후 불변.
2. 격리된 전체 게임 복사본·fresh prefix·빈 Xvfb display에서 foreground 동기로 완주한다. 다른 세션/process/display/log를 건드리지 않는다.
3. **repo source 변경 0.** 시작 SHA가 아래와 하나라도 다르면 게임을 시작하지 않고 `BLOCKED(gate)`다.
   - `runtime_bridge.c` `9548de80c3c1367377fd21b9e3704ddbe40caae5a5bd64d071d7b7cdb5c01bfb`
   - op8 계약 `b0b89e0c927aa0b173ad893e0c85f2c7b2263281ab8d86fbc92eebb7866eb838`
   - op9 계약 `695631f160487c2db09cb86e154ab48b40345c321ec8796d88afbc72ce3dce5a`
   - 허용목록 핀 `2a8aa4f788ae35c869300726da65907ae0d82f28b69868c15c6212ae27605478`
4. lap551이 이 source로 `make check` 835 passed·ruff·compileall·mypy·`CONTEXT_PASS`와 `SAFETY_PASS`를 새로 완료했다. 다음 work가 source를 바꾸지 않으면 전체 gate를 반복하지 말고 위 3개 계약 테스트와 safety만 실행한다. source가 달라졌다면 실행하지 않고 middle로 돌려보낸다.
5. 후보 SHA는 `a10024de…a1bb2d68`, 브리지 재빌드 SHA는 lap550 `822c802e…31aed`와 같아야 한다. 다르면 `BLOCKED(gate)`다.
6. 게임 실행은 **최대 1회**다. 첫 op9 전 하네스 gate 실패도 이번 work에서 재시도하지 않는다. 원시를 보존하고 다음 middle/strategy가 판단한다.
7. 60분 상자. 시간이 부족하면 시작하지 않는다. 시작했으면 background로 넘기지 말고 종료·정리까지 기다린다.

## 1. 하네스 계보와 고정 fixture

- lap550 `w42_run.py` SHA `3c3e8b89…177c6`의 H21/H25/op9→op8·trace를 베이스로 한다.
- lap530 W37의 24k 표본·event·op1·save/load·A1~A8' 판정기를 가져오되, **직접 op8 파동은 이 카드 §3의 2단 파동으로 교체**한다.
- fixture는 시딩+스크립트 입력임을 모든 산출물에 명시한다.
- owner마다 op7 rice/wood 각 1,000,000 → type5×100 → type7×25 → type2×60 → type46×20(N187 순서). 허용목록 {5,7,46,2}; 기대 `used=4,950`, count=207, 8 owner live 합 1,656.
- type2 row preflight, 이동 issuer `0x4AEDE0` 12바이트, 공격 issuer `0x415480` 12바이트가 핀과 다르면 `ARM_FAIL`이다.

## 2. H29 — 네 짝 전열 배치 사전 탐색

type5·type7 시딩 뒤, type2·type46 시딩 전에 H21 식으로 현재 지형/점유 free mask를 읽는다. 주소 해독기는 lap546 H21a 실측 8/8로 이미 검증됐지만, 합성 mask 단위 테스트는 프로세스 연결 전에 다시 통과해야 한다.

1. 실제 map W/H와 현재 live snapshot을 입력으로, 네 짝 `(0,1)(2,3)(4,5)(6,7)`의 type2 60기 배치를 결정적으로 탐색한다.
2. 후보는 `(source_anchor_y, source_anchor_x, target_anchor_y=source_y+8, target_anchor_x)` 사전식 순서다. 실제 op5 행 우선 배치식으로 양쪽 60기를 모사하며 이미 예약한 셀은 점유로 넣는다.
3. source 쪽 60기는 자기 anchor 행 하나에, target 쪽은 자기 anchor 행 또는 gap 바깥쪽 다음 행에만 있어야 한다. 두 anchor 사이 7행에는 모사 type2와 현재 live가 0이어야 한다. 네 짝의 셀·gap은 서로 겹치지 않는다.
4. type46을 마지막에 넣어도 gap을 침범하지 않도록 기존 type46 anchor의 20기 배치를 같은 식으로 모사해 후보에서 제외한다. T0 실제 위치가 모사와 다르면 `ARM_FAIL(layout_mismatch)`다.
5. 첫 완전해를 `layout_plan.json`에 후보 수·탈락 이유·좌표와 함께 남긴다. 완전해가 없으면 시딩을 계속하지 않고 `BLOCKED(gate:no_four_pair_layout)`로 종료한다. 카드 밖 배치 완화나 두 번째 탐색 규칙을 즉석에서 만들지 않는다.
6. T0에는 A1·A8'와 함께 네 짝 모두 실제 gap 7행에 **모든 live unit 0**, type2 각 60기 배치 일치를 다시 확인한다.

## 3. H30 — 24k 2단 순환

- T0 뒤 1,000 tick은 명령 없는 기준 창 B다. 이후 STOP_TICK=24,000까지 600 tick cadence로 파동을 시작한다. 이전 파동이 끝나지 않았으면 새 파동은 건너뛰고 기록한다.
- 매 파동 시작 때 W37과 같이 owner별 op1 type7 생산 양성 대조와 type2가 10기 미만일 때만 op5 보충을 먼저 수행한다.
- 짝별 방향은 파동 번호가 짝수면 짝의 첫 owner→둘째 owner, 홀수면 반대다. 이로써 8 owner 모두 번갈아 A2 사망 대상이 된다.
- 소스는 해당 owner의 살아 있고 idle인 type2 중 slot 오름차순 최대 **20기**다. H25를 현재 snapshot/free mask로 다시 계산해 서로 다른 적 인접 목적지를 배정한다.
- 소스마다 op9는 1회만 보낸다. 600 tick 안에 지정 표적 Chebyshev≤1이면 그 poll에서 op8을 1회 보낸다. op9/op8 재발행 없음. 표적 사망·uid 변경·도착 실패·조기 정지는 각각 terminal reason으로 남긴다.
- 파동마다 요청/receipt 원문, 시작·도착·공격 tick, walk, 소스/표적 uid·slot, HP 감소, 사망, terminal reason을 기록한다.
- tick≥16,000의 첫 완료 파동 직후 op2 save(slot92)→마커 확인→op3 load한다. 로드 전 pending 파동이 없어야 하며, 로드 뒤 fresh snapshot으로 다음 파동을 새로 만든다. tick은 로드 경계에서 분리해 계산한다.

## 4. H31 — 원시 재현성 강화

lap551에서 `move_stop_early`는 bulk snapshot의 cmd와 직후 개별 trace read 사이 경쟁 때문에 raw trace만으로 work의 4/4를 재현하지 못했다(라벨 영향 없음). W43은 다음을 필수로 한다.

- 각 poll의 **같은 bulk snapshot**에서 source별 `(tick,uid,x,y,hp,cmd)`를 `source_states.jsonl`에 기록한 뒤 상태전이·arrival을 계산한다.
- 요약 flag만 남기지 말고 `non_idle_seen`, `idle_after_non_idle`, `arrived`, `target_dead`, `uid_changed` 전이를 사건 JSONL로 append+flush한다.
- samples/events/source_states/receipts만으로 middle이 결과를 재계산할 수 있어야 한다. `run_summary`와 in-memory summary는 검수 입력이 아니다.

## 5. 측정식과 라벨

W37/W36의 A1·A2·A3·A5·A6·A8' 식과 우선순위를 그대로 쓴다.

- A1: T0 8/8 owner `used`∈[4900,5000].
- A2: owner별 창 E 사망 `D_o≥20`이고 창 3등분 중 2구간 이상에 존재. op8 목표 uid 여부로 driven/natural을 분리한다.
- A3: owner별 첫 op1 양성 대조 PASS 및 이전 사망 slot의 다른 uid 출생 `R_o≥1`.
- A5: live `used≤5000`, 음수/int16/`count>1200`/`live!=Σcount`/tick 역행/fault 0.
- A6: save 직후==load 직후(8 owner used/reserved/count+live), load 뒤 사망 합 증가.
- A8': T0 네 타입 보유, type2≥10, 단일 타입 비용 비중≤85%.

라벨 우선순위: `ARM_FAIL` > `BLOCKED` > `CYCLE_UNSTABLE` > `NO_ENGAGEMENT` > `CYCLE_PARTIAL` > `DRIVEN_CYCLE_STABLE`.
`DRIVEN_CYCLE_STABLE`은 A1·A2·A3·A5·A6·A8' 전부 PASS일 때만이다. 부분 수치는 숨기지 않는다.

보고 의무: owner별 D(op8/natural)·R·A4, 짝/방향별 op9 요청·수락·도착률·walk·op8 수락·hit_attr·kills·terminal reason, 파동/skip 수, A5 위반, save/load, RSS/VM/swap/tick/MemAvailable, 원본/후보/브리지 SHA, fixture, 잔류 프로세스.

## 6. 검수와 다음

- work는 `temp/Syw2plus_patch/g2_capacity/<date>_lap<lap>_w43_s1_2stage_24k/`에 하네스·원시·로그를 남기고 자기 라벨을 기록한다.
- 다음 새 middle은 summary를 보지 않고 §4 원시만으로 §5를 재계산한다.
- `ACCEPT`+`DRIVEN_CYCLE_STABLE`이면 같은 후보 144k 카드 1장을 발행한다. 그 외 라벨 또는 `no_four_pair_layout`이면 재실행하지 않고 strategy에 회부한다.

