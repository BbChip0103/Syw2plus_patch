# G2 W45R — 판별 가능한 저장/로드를 위한 결정적 상태 변화 1회 handoff

## 1. 판정과 범위

- lap569 middle은 lap568 W45 raw를 `run_summary.json` 없이 재계산해 B1/B2/B3/B5/B6 PASS, B4 FAIL을 재현했다.
- B4의 여덟 항 중 실패는 `pre_load.pool != pre_save.pool` 하나다. 저장/로드 receipt, marker, 305 tick 대기, tick 순서, post-load 풀·장부 복원은 모두 성립했다.
- W45는 저장 뒤 자연 변화를 기다렸을 뿐 상태 변화를 일으키는 명령을 발행하지 않았다. 따라서 결과는 제품 저장 결함이 아니라 **판별 전제 미성립**이다.
- 이 카드는 제품/게임 코드 변경이 아닌 공유 temp 파생 하네스 작업이다. 원본·후보·기존 raw는 읽기 전용이며 S1/144k/Q9/S4를 열지 않는다.

## 2. work가 수행할 최소 변경

새 비중첩 공유 temp 디렉터리에서 lap568 `w45_run.py`를 `w45r_run.py`로 파생한다. 저장/로드 구간만 아래처럼 바꾼다.

1. 기존 B1~B3·B5·B6, 후보 SHA, 8 AI/map100×100/혼합 fixture, save tick≥16000, 최종 tick≥24000을 유지한다.
2. 저장 성공 뒤 **최소 300 tick을 먼저 기다린다**.
3. 300tick 대기 직후 장부에서 `used + 10 <= cap`인 owner 중 `used`가 가장 낮고 owner 번호가 가장 작은 한 명을 고른다. lap568 기준 예상 후보는 owner0이지만 하드코딩하지 않는다.
4. 그 owner의 기존 anchor에 op6으로 type7(cost10) **정확히 1기**를 gate-legal 주입한다. receipt `ok`, `fixture_added==1`, `used +10`, `count +1`, 전체 live `+1`을 요구한다. 실패하면 게임 재실행 없이 `BLOCKED(gate: mutation_not_armed)`다.
5. 주입 직후 새 `(slot,uid,type=7,owner)`를 raw에 기록하고 pre-load snapshot에 존재함을 확인한 뒤 op3 load를 한 번만 발행한다.
6. post-load에서 그 `(slot,uid)`가 사라지고, 전체 pool 4-tuple과 8 owner `(used,reserved,count)`가 pre-save와 정확히 같아야 한다.

## 3. 실행 전 회귀

- 합성 정상: save → 300tick → type7 1기 추가 → load → pre-save 복원은 PASS.
- 음성 1: mutation receipt 성공이어도 pre-load pool 불변이면 FAIL.
- 음성 2: 주입 UID가 post-load에 남거나 풀/장부가 pre-save와 다르면 FAIL.
- 음성 3: `load.after <= save.after < load.before` 또는 300tick 조건이 깨지면 FAIL.
- `py_compile`, 허용 op 정적 검사, 원본/후보 SHA, `checks/safety.sh check`를 게임 전에 통과한다.

## 4. 실행 예산과 종료

- foreground fresh prefix/display **정확히 1회**, background 금지. 필수 preflight 실패는 게임 0회로 종료한다.
- 성공은 B1~B6 전부 PASS와 위 주입 UID 소멸/전체 복원을 동시에 요구한다. 기준 완화 금지.
- 결과와 무관하게 다음 새 middle이 summary를 제외한 raw로 독립 검수한다. 실패 시 추가 재실행 없이 승격한다.
- G2 PASS·사용자 마일스톤 승인·혼합144k·S1 재개를 주장하지 않는다.
