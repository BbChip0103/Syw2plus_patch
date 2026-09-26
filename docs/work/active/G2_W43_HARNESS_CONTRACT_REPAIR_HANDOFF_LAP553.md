# W43 하네스 계약 수리 handoff — lap553 middle

상태: **strategy 승인 대기**. 이 문서는 work 구현 범위를 고정하지만 새 게임 실행 예산을 열지 않는다.
**lap554 strategy 추기:** W43R fresh exact-once 1회 허가. 아래 6항에 R7~R9와 N205 사전 등록이 더해진다. 판정 문서는 `G2_STRATEGY_W43R_FRESH_BUDGET_LAP554.md`다.

## 판정과 범위

lap553 독립검수는 lap552를 `REJECT / BLOCKED(harness_contract)`로 판정했다. 제품 브리지·EXE 수정 근거는 없으며 수리 대상은 공유 temp W43 하네스뿐이다. 기준 A1~A8′, fixture 허용목록, 제품 후보 SHA를 바꾸지 않는다.

## work가 수리할 것

1. H29: type5·type7 뒤/type2·type46 전에 네 짝 모두의 전열+7행 gap+type46 회피를 사전탐색하고 `layout_plan.json`을 기록한다. 완전해 없음은 시딩 전 `BLOCKED(gate:no_four_pair_layout)`다.
2. H30: 짝 방향을 wave parity로 뒤집는다. 짝수 `0→1,2→3,4→5,6→7`, 홀수 `1→0,3→2,5→4,7→6`; 합성 테스트가 2연속 파동의 여덟 방향을 고정해야 한다.
3. A3: owner별 첫 op1의 receipt/reserved 변화와 1,000tick 내 producer `production_type`/`progress` 변화를 raw event로 기록한다. `receipt=None`은 정상 skip으로 처리해 후처리 `.get()` 예외를 없앤다.
4. event 계보: 동일 `(kind,slot,uid)` lifecycle을 wave 종료 때 중복 append하지 않거나 판정기가 고유 lifecycle로만 센다. load 경계 전후 timeline을 분리하고 rewind 구간 tick을 합산하지 않는다.
5. A5: `pool snapshot → owner counters` 순차 읽기의 torn sample을 제품 불일치로 오인하지 않도록 같은 tick에서 두 번 동일한 `(live, owner counts)`을 얻은 표본만 판정 입력으로 채택하고 retry/폐기 이유를 raw로 남긴다. 기준 `live==Σcount` 자체는 완화하지 않는다.
6. 테스트: H29 완전해/없음, 홀수 방향 반전, `receipt=None`, lifecycle 중복, torn-sample retry를 게임 없는 합성 회귀로 먼저 잠근다. targeted PASS 뒤 현재 source에서 `make check`·`SAFETY_PASS`를 완료한다.

## 실행 경계

- strategy가 새 exact-once 예산을 명시하기 전에는 게임을 실행하지 않는다.
- 승인되면 새 temp 디렉터리·fresh prefix·빈 display에서 foreground 1회만 실행한다.
- H29/H30/A3 raw 계약 중 하나라도 실행 전/중 누락되면 그 run을 제품 판정하지 말고 즉시 `BLOCKED`로 보존한다.
- 통과하더라도 다음 새 middle이 raw만으로 검수하기 전 144k를 발행하지 않는다.
