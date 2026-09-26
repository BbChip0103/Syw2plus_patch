# 2026-09-20 KST | lap394 | G2 cap 상위 판단 / 근거 충돌 STOP

- 실제 역할: Codex gpt-6-astra, 상위 방향/master-plan. 게임 구현·바이너리 수정·게임실행·커밋 0.
- lap 번호는 loop/.lap_counter=394를 읽음; 사용자 런타임 헤더 lap393과 구분하며 카운터 쓰기 0.
- 목표: G2 활성8인 각각 전비5000 유지. G1/G4 후순위, G3 중단. 마일스톤 이동/제품 승인 없음.
- 가설/판정식: lap393 P1~P4가 모든 허용 전이에서 Σused≤Σcap을 보존하는가.
  전제들을 지키는 추상 반례 하나면 증명 REJECT; 게임 도달성/실제 랩 재현과 구분한다.

## 독립 검수 결과 — P9의 논리적 귀결 REJECT

lap393 probe 원문 P3/P4/P9를 읽었다. P9는 32767//8의 나눗셈 두 개와
8×1500/5000 비교를 검사할 뿐, 이전 뒤 생산을 포함한 귀납적 전이 보존을 검사하지 않는다.
따라서 그 probe의 failures=[]는 전역합 불변식의 증명이 아니다.

8명 cap=C, 초기 U=[C,C,C,C,C,C,C,C]를 두자. 비용 d(0<d≤C)의 개체를
owner0→owner1로 이전하면 [C-d,C+d,C,…]이며 합은 8C로 보존된다.
owner0가 비용 d만큼 다시 생산하면 gate (C-d)+d≤C를 만족하지만
U=[C,C+d,C,…], 합=8C+d>8C다. 두 단계 모두 lap393의 P2/P3 전제를 만족한다.
이 반례는 type 변경/부호 랩/TOCTOU/우회 writer를 가정하지 않는다.
이전받은 owner의 초과분이 남아 있는 동안 다른 owner가 생산 가능하다는 점을 P9가 놓쳤다.

python3 인라인 산술 확인(d=1) 결과:
| cap | 이전 후 재생산 합 | 주장 상한 | 판정 |
|---|---|---|---|
|1500|12001|12000|추상 전이 반례 PASS|
|4095|32761|32760|추상 전이 반례 PASS|
|5000|40001|40000|추상 전이 반례 PASS|

재현 명령(제품/게임 테스트가 아님):
```python
for cap in (1500, 4095, 5000):
    used = [cap] * 8
    used[0] -= 1
    used[1] += 1
    assert sum(used) == 8 * cap
    assert used[0] + 1 <= cap
    used[0] += 1
    assert sum(used) == 8 * cap + 1
    assert max(used) < 32768
```
fixture=추상 정수 상태/8 owner/d=1. 게임에 비용1 개체가 있다는 주장 아님.
일반식은 양의 d로 성립하나 실제 unit 비용·roster/pool 여유·이전 가능성·생산자 생존은 미검증이다.
따라서 이것은 증명 반박이지 원본/4095/5000의 실제 랩 재현 또는 불가능성 판정이 아니다.

## 상위 결정 / 한계

1. G2 5000을 유지한다. 4095로 목표를 축소할 권한을 행사하지 않으며 lap393 §C 착수를 보류한다.
2. '원본1500/4095는 랩 불가능 증명', '5000은 양립 불가', '32-bit 확장만이 유일 해법',
   '남은 결정은 A/B뿐'은 현재 증거로 승인하지 않는다. 4095 산술 자체는 맞지만 안전 상한은 UNKNOWN.
3. 합격 방향은 정상 생산 gate·정확한 전비 장부·랩 없음·원본 이전 semantics 보존이다.
   used>cap만으로 FAIL 처리하거나 clamp/이전 사전거부로 숨기지 않는다. DESIGN 전체 기준은 유지한다.
4. broad-patcher/구조통합 NO_GO 유지. 32-bit 또는 별도 장부 등 구현 방식을 확정하지 않는다.
   랩 fixture 불필요 결론도 불변식에 의존한 부분은 철회 대상; 이 세션은 새 실행을 시작하지 않는다.
5. 제품 변화 없는 회차를 계속 소비할 이유는 문서 보강이 아니라 이 구체적 논리 충돌의 해소뿐이다.
   9/19 trace 재분석·기존 전체 스윕 반복으로 이 질문을 대체하지 않는다.

## middle → work handoff (독립 세션; 현재 큐는 STATUS만)

middle(현재 MODEL_ROUTING의 Opus5/high; 파일명 ESCALATE_SOL은 기존 인터페이스):
- 위 반례를 독립 검수하고 P9/카드 §B·C·D·E의 어떤 결론이 무효인지 명시한다.
- 직접 변위 검색 5건과 모든 alias/bulk writer 완전성은 구분한다. 원시 증거를 삭제하지 않는다.
- 반복 이전+생산을 실제로 배제하는 다른 상한이 있다면 그 근거를 제시하고, 없으면 안전 상한 UNKNOWN으로 확정한다.
- 실제 검증에 필요한 최소 제품 probe 하나를 work에 인계한다: 지원 자유대전의 정상 이전 뒤
  원 소유자의 정상 재생산, 장부와 실소유 비용합/roster/pool을 비교한다. 비용·자원 fixture를 명시한다.
  실행은 기존 격리/원본SHA/old bytes/원복 계약 안에서만; 필요한 경로가 없으면 BLOCKED와 누락 입력을 적는다.
work(Luna/Sonnet5 high)는 middle이 범위를 확정한 다음 회차에서 한 work/60분/실패가설2개 상한으로
probe한다. FEASIBLE이면 추가 계획 회차 없이 실행하며 불가능/차단이면 근거로 종료한다.
결과는 다음 새 middle이 독립 검수한다. 본 문서는 work 실행 성공이나 NO_GO 해제 승인이 아니다.

## 검증 / 보존

- 읽기: PROMPT→AGENTS/INBOX/APPROVALS→STATUS 전체→DESIGN→lap393 기록/카드/probe.
- 주소 참고 supply_200c_accumulation_rule_0726.md는 과거 외부 출처 포함; 현재 실행 증거로 승격하지 않았다.
- 이전 full-test result source=40e0651031d4d130e6cdf753f47fe0783da5e782,
  사용자 current_source=f458719b43b6b12350737fb1f7df460d3de486e3로 불일치.
  정확한 로그 logs/gates/full-test-20260919T235413-XF5Kjn.output는 715 passed/CONTEXT_PASS이나 과거 Fast뿐이다.
- 원본 SHA는 lap393 기록 b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac;
  이번 원본 재해시/바이트 실행 검수 SKIP, 후보 없음. 실제 환경/지도/군대/24k/144k/LAN 모두 신규 검증 SKIP.
- Fast 전체는 loop/FULL_TEST 요청으로 위임(현재 PASS 아님). 문서 구조 검사만 별도 실행한다.
- 근거 충돌로 ESCALATE_SOL §8을 보존하고 종료. 실패 재시도/구현/마일스톤 마감 없음.
- 직전 STATUS 전문: 20260920_lap394_status_before_edit.md, SHA256 424bd6e0e6b3bd815e6f344ffde9ef61c9b9a9de9130c51bc504bed6d29ee5f7, 130줄.
- 최종 문서 확인: STATUS 130줄·Blockers 1개 PASS; `python3 checks/context_limits.py` rc0 CONTEXT_PASS. 전체 Fast는 요청 상태이며 통과 주장 없음.
