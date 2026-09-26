# G2 strategy — W43R fresh exact-once 예산 판정 (lap554)

- 판정: lap554 strategy (Claude Code `claude-opus-5-5`, INBOX 2026-09-24 14:34 라우팅 "strategy는 claude-opus-5-5 유지"), 2026-09-24 KST.
- 입력: lap553 middle `REJECT / BLOCKED(harness_contract)`(`ESCALATE_SOL`§107), 수리 handoff `G2_W43_HARNESS_CONTRACT_REPAIR_HANDOFF_LAP553.md`, W43 카드 `G2_S1_MOVE_THEN_ATTACK_24K_SOAK_W43_LAP551.md`, lap532 A3 정의(`G2_STRATEGY_N192_APPROACH_PATH_LAP532.md` §4(3)), lap552 raw.
- 이 문서는 게임 코드를 바꾸지 않는다. 기준 A1~A8′·허용목록 {5,7,46,2}·후보 SHA는 그대로다. G2 제품 합격이나 사용자 마일스톤 승인이 아니다.

## 1. 판정

**`FEASIBLE` — W43R fresh exact-once 게임 1회를 허가한다.** 다음 회차는 work이며 계획 회차를 더 끼우지 않는다.

근거(lap554 독립 raw 대조, `events.jsonl`/`waves.jsonl` SHA가 §107 기록과 일치):
1. lap552 실패는 전부 하네스 계약 누락·계측·기준 구조 쪽이다. 제품 결함 증거는 없다. tick 24,373까지 fault 0, 창 E 표본 2,814개에서 owner `used` 4,385~5,000, 고유 사망 210·고유 출생 158, 교전 중 저장/로드 필드 일치(A6), A1/A8′ PASS.
2. H30 미구현을 직접 확인했다. 19/19 파동의 방향 집합이 모두 `{(0,1),(2,3),(4,5),(6,7)}`이다. 사망이 목표 owner(1·5)와 전열 owner(0·4)에 몰리고 띠 owner(2·3·6·7)는 0~5인 것은 H29(띠 짝 재배치)·H30 누락으로 설명된다.
3. A5 +1 네 건은 pool snapshot 뒤 owner counter를 읽는 순차 읽기(`w43_run.py:1541~1543`)와 맞는다. 계측을 고치고 기준은 그대로 둔다.

## 2. work 수리 범위 = handoff 6항 + 아래 3항

handoff 1~6(H29 `layout_plan.json`, H30 parity 반전, A3 producer raw·`receipt=None`, lifecycle dedupe·load 경계 분리, coherent A5 표본, 합성 회귀)은 원문대로 한다. 추가:

- **R7 op1 발주 조건 복원.** lap532가 정한 조건은 `used + reserved + 10 ≤ 5000`이다. lap552 하네스(`w43_run.py:898`)는 `reserved`와 type46만 보고 `used` 4,995·5,000에서도 op1을 보냈다. 그 결과 receipt는 `executed`인데 `reserved`가 0→0이었다(owner0 wave0 등). 이 상태에서 양성 대조는 구조적으로 성립할 수 없다. 여유가 없으면 `skip_reason="no_headroom"`을 raw로 남긴다.
- **R8 A3 정의 복원.** W43 카드 §5는 A3를 "R_o≥1"로 줄였고, 하네스 자기판정은 `op1_accepted≥1`이었다. 둘 다 쓰지 않는다. 판정은 lap532 원문대로 **A3′**(owner마다 양성 대조 PASS ∧ 창 E 첫 사망 뒤 op1 귀속 type7 새 uid 출생≥1)와 **A3r**(창 E 사망으로 비워진 슬롯 ≥1이 다른 uid로 다시 채워짐, owner 무관, 채워진 뒤 A5 위반 0)로 한다. AI 자체 출생은 따로 세어 보고만 한다.
- **R9 lifecycle 키.** 고유 사망/출생 키는 `(timeline_segment, kind, slot, uid)`다. segment는 load 전/후다. load가 되돌린 유닛이 load 뒤 다시 죽는 것은 새 사건으로 센다. 같은 segment 안 중복은 한 번만 센다(handoff 4의 구체화).

## 3. 사전 등록 — N205 (A3r 할당 순서 위험, 가설)

lap552 raw에서 고유 출생 158건의 슬롯은 tick 165의 2344에서 tick 24,373의 2184까지 **거의 한 방향으로 내려갔다**(같은 tick 안 묶음만 오름차순). 창 E 사망 슬롯은 2189~3989였다. 출생이 들어간 슬롯 중 이전 사망 슬롯과 같은 것 29건은 **전부 같은 uid**였다. 즉 먼저 태어나 나중에 죽은 같은 유닛이고, 재사용은 0건이다.
그래서 풀(4,001칸)에 빈칸이 많은 동안에는 할당 앞머리가 비워진 슬롯에 닿지 않아 A3r이 구조적으로 0일 수 있다. lap532가 owner 단위 A3를 버린 이유(N193)와 같은 종류의 위험이다. 할당기를 정적으로 읽어 확인하지 않았으므로 **가설**이다.

- 기준은 완화하지 않는다. A3r=0이면 A3는 FAIL이고 `DRIVEN_CYCLE_STABLE`이 아니다.
- middle은 raw에서 출생마다 "그 시점까지 창 E에서 비워진 슬롯 집합에 속하는가"와 "그 시점 비워진 슬롯의 최솟값보다 작은가"를 계산한다. A3r=0이면서 모든 고유 출생이 그 최솟값보다 작으면 하위 사유를 `a3r_allocator_order`로 적는다.
- 그 경우 144k를 자동으로 열지 않는다. 다음 strategy가 (i) 할당기 정적 판독 (ii) 할당 앞머리가 닿을 만큼 긴 실행 중 하나를 고른다.

## 4. 실행 경계·예산

1. 시작 전 W43 §0.3 핀 4건이 일치해야 한다. lap554에서 다시 확인했다: `runtime_bridge.c` `9548de80…`, op8 계약 `b0b89e0c…`, op9 계약 `695631f1…`, 허용목록 핀 `2a8aa4f7…`. repo 제품 source를 바꾸지 않으면 W43 §0.4대로 전체 `make check`를 반복하지 않는다. 계약 테스트 3개·하네스 합성 회귀·`SAFETY_PASS`만 한다. 제품 source가 달라졌으면 실행하지 않고 middle로 돌려보낸다.
2. 수리는 공유 temp 새 디렉터리 `g2_capacity/<date>_lap<lap>_w43r_s1_2stage_24k/`에 한다. lap552 `w43_run.py`(SHA `df599349…9477`)에서 파생하고 파생 원본 SHA를 기록한다.
3. 게임은 **최대 1회**, fresh prefix·빈 display·foreground다. lap552 실행은 약 13분이 걸렸다. 수리·테스트 뒤 남은 시간이 25분 미만이면 **시작하지 않는다.** 그 사실을 기록하면 다음 work가 스크립트를 카드와 대조하고 수정 없이 실행한다(PROMPT ③).
4. H29 완전해가 없으면 시딩 없이 `BLOCKED(gate:no_four_pair_layout)`로 끝낸다. 첫 op9 뒤 H29/H30/A3 raw 계약이 하나라도 빠지면 `BLOCKED(harness_contract)`로 보존한다. 어느 경우에도 재시도는 0회다.
5. 라벨 우선순위와 A1·A2·A5·A6a/b·A8′ 식은 바꾸지 않는다. 다음 새 middle이 raw만으로 재계산한다. 그 ACCEPT와 `DRIVEN_CYCLE_STABLE` 전에는 144k를 열지 않는다.

## 5. 종료 규칙 (S1 트랙 예산)

- W43R이 `BLOCKED(no_four_pair_layout)`·`NO_ENGAGEMENT`·`BLOCKED(harness_contract)`로 끝나면 S1 스크립트 교전 트랙은 **예산을 닫는다.** 사용자에게 남은 (가) AI 최소 변경 예외 · (나) "8인"을 사람 슬롯으로 · (다) 교전 트랙 중단을 다시 여쭙는다(STATUS 미결 약속).
- `CYCLE_PARTIAL`·`CYCLE_UNSTABLE`이면 middle 재계산 뒤 strategy가 하위 사유별로 판정한다. N205(`a3r_allocator_order`)만 남은 경우는 §3을 따른다.
- streak: lap553(middle)·lap554(strategy) 두 회차 연속 문서다. **다음 회차는 반드시 work 실행(하네스 수리 코드+합성 회귀, 가능하면 게임 1회)이다.**

## 6. 사용자 통지 (질문 아님, 번복 가능)

W43 재실행 1회를 허가했다. 이유는 lap552 실패가 우리 시험 도구의 누락 탓이고 게임 쪽 결함 증거가 없어서다. 도구를 먼저 고친다.
합격 기준은 그대로다. 재생산 기준(A3)은 W43 카드가 모르게 줄였던 것을 lap532 원래 정의로 되돌렸다.
새로 본 위험도 있다(N205). 게임이 새 유닛을 빈 슬롯의 한쪽 끝부터 채우는 것으로 보인다. 그렇다면 "죽은 유닛 자리 재사용"은 24k 안에 안 나올 수 있다. 그래도 기준은 낮추지 않았다.
