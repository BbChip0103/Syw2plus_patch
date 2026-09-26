# 2026-09-24 | lap 554 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / 세션 effort 비노출 / strategy 지정(INBOX 2026-09-24 14:34 "strategy는 claude-opus-5-5 유지"). 게임 코드 수정 없음.
- 가설 / 사용자 관찰: lap552 W43 실패(lap553 `REJECT / BLOCKED(harness_contract)`)가 제품 결함이 아니라 하네스 계약·계측·기준 구조 문제라면, 수리 뒤 fresh 1회로 G2 S1 판정을 낼 수 있다.
- 예상 PASS / FAIL 조건: lap552 raw에서 제품 결함 신호(fault·풀 손상·저장 불일치)가 없고, 실패가 H29/H30/A3/A5 계측으로 설명되면 `FEASIBLE`로 예산을 연다. 제품 쪽 신호가 있으면 예산을 닫고 사용자에게 보고한다.
- 변경 파일 / source fingerprint / 커밋: 문서만. 신규 `docs/work/active/G2_STRATEGY_W43R_FRESH_BUDGET_LAP554.md`, 이 기록. 갱신: STATUS, INBOX(통지 2줄), handoff 상태 줄, `loop/ESCALATE_SOL`§108. 제품 source 변경 0. W43 핀 4건 재확인 일치(`runtime_bridge.c` `9548de80…`, op8 `b0b89e0c…`, op9 `695631f1…`, 허용목록 `2a8aa4f7…`). 커밋 0(uncommitted).
- 원본 / 후보 SHA / 환경 / fixture: 원본 `b56986e0…a8ac`, 후보 `a10024de…2d68`(lap552/553 기록 그대로, 이번 회차 게임 실행 0). fixture = gate-legal 시딩 + 스크립트 입력(op9→op8), 8 AI owner, 100×100.
- 실행 / 증거: lap552 raw 읽기만. `events.jsonl` `51458d6a…c885`, `waves.jsonl` `2102a90a…3ee3`, `samples.jsonl` `c38cd12e…8301`, `source_states.jsonl` `f8eb7cf8…cccc`는 §107 기록과 일치. `w43_run.py` `df599349…9477`. 계산은 python 인라인 읽기 전용이다.
- 측정값:
  - 파동 방향 집합 19/19 `{(0,1),(2,3),(4,5),(6,7)}`. H30 미구현을 확인했다.
  - death 394행 → 고유 `(slot,uid)` 210. 창 E owner `used` 4,385~5,000(표본 2,814).
  - op1: owner4는 19/19 `reserved_nonzero` skip. 다른 owner도 `used` 4,995/5,000에서 발주돼 `executed`인데 `reserved` 0→0(R7). 하네스 자기 A3 = `op1_accepted≥1`(lap532 A3′/A3r보다 약함).
  - **N205(가설):** 고유 출생 158의 슬롯이 2344(tick165)에서 2184(tick24,373)로 내려갔다. 이전 사망 슬롯과 겹친 29건은 전부 같은 uid였고, 다른 uid 재사용은 0이다. 할당 앞머리가 비워진 슬롯(2189~3989)에 닿지 않았다.
- 판정: **`FEASIBLE` → W43R fresh exact-once 게임 1회 허가.** handoff 6항 + R7(op1 `used+reserved+10≤5000`) + R8(A3 = lap532 A3′+A3r 복원) + R9(lifecycle 키에 load segment 포함). N205는 기준 완화 없이 하위 사유 `a3r_allocator_order`로 사전 등록했다. 144k는 닫혀 있다. H29 해 없음·NO_ENGAGEMENT·harness 누락이면 S1 트랙 예산을 닫고 사용자에게 (가)(나)(다)를 다시 여쭙는다.
- 회귀 / 남은 위험: `SAFETY_PASS`·`CONTEXT_PASS`는 문서 갱신 뒤 확인(아래 STATUS 검증 줄). 게임 실행 0. N205는 정적 판독이 없어 가설이다. H29 4짝 전열 해가 100×100 지형에 없을 위험이 있다(N202: owner2 60기 단일행은 y34~44 불가).
- 독립 검수 / 사용자 승인: 다음 work 결과는 새 middle이 raw만으로 검수한다. 사용자 마일스톤 승인 없음.
- 다음 한 가지: work(Codex `gpt-5.6-luna`/high) — W43R 하네스 수리 + 합성 회귀 → 핀·계약·`SAFETY_PASS` → 시간이 25분 이상 남으면 fresh 게임 1회. streak 2이므로 문서만으로 끝내지 않는다.
