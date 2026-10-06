# lap732 (work) — G5 체크리스트 (D) 잔여: Shift+숫자 추가·부대원 사망 후 호출

- 날짜: 2026-09-28
- lap: 732
- 역할: work tier (Claude Code Sonnet 5)
- 목표: STATUS/APPROVALS 2026-09-28 지시 — 체크리스트 (D)의 남은 두 항목(Shift+숫자 추가,
  부대원 사망 후 호출)을 한 fixture·한 실행(원본 1회·후보 v5 1회)으로 끝낸다. lap731이 이미
  Ctrl+숫자 지정/숫자 호출/저장로드는 lap724 `PASS_UI_ROUNDTRIP`(v5)으로 기완료임을 확인했으므로
  이 둘만 남았다.
- 가설: (1) Ctrl+숫자로 지정된 조에 Shift+같은숫자를 누르면 조 인원이 정확히 1 늘어난다. (2) 조에
  지정된 유닛 일부가 사망한 뒤 그 조 번호를 호출하면 생존자만 정확히 선택된다.

## 방법

신규 `tools/g5_group_shift_add_death_recall_probe.py`. STATUS 원문의 "Ctrl+1 지정 후 Shift+2로
추가"는 조 번호 표기가 부정확한 것으로 판단해(오케스트레이터 확인) **동일 조 번호**(그룹 1: Ctrl+1
지정, Shift+1 추가)로 통일했다.

1. 솔로 로비 부팅(원본 20 상한 / 후보 v5 50 상한), 기존 9점 어파인 보정(worker 기준)으로
   화면↔월드 좌표 확정.
2. 넓은 범위(worker 기준 dx −3..3 × dy −4..−1,1..5, 자기 타일 dy=0 제외, 63셀)에 SEED_TYPE 유닛을
   스폰 — **1차 시도에서 이 랜덤 국가의 맵에 worker 서북쪽(대략 dx∈{−3,−2,−1}, dy∈{−3,−2})에
   장애물(HQ 건물로 추정, 정적 확인 안 됨)이 있어 그 방향 요청이 엉뚱한 칸에 배치되는 것을
   발견**(브리지의 Place-then-raster-scan 폴백이 조용히 다른 칸에 배치) → 고정 사각형 드래그 대신,
   스폰 후 **실제 좌표로 diff 확인**(요청 좌표와 다르면 버림)과 **단독 클릭 격리 확인**(lap728
   기법)을 통과한 유닛만 사용하도록 설계를 바꿔, 특정 국가의 지형에 좌우되지 않게 했다.
3. 격리 확인을 통과한 후보 중 앞쪽 `bulk_n`개를 **plain 클릭 + 마우스 Shift+클릭 연속**(이미
   lap728에서 PASS 확정된 메커니즘)으로 다중 선택 → Ctrl+1로 그룹1 지정.
4. 이후 `add_steps`개를 한 번에 하나씩: 새 유닛 단독 클릭(plain) → **키보드 Shift+1** → 그룹1
   인원을 `unit+0x344`(유닛 자체 필드, `fixture_unit_group_snapshot`)로 직접 측정(리콜 없이 정면
   측정, R3의 `SELECTION_BASE`와는 다른 자료구조 — lap724가 이미 정적으로 확인한 사실).
5. (신규 발견 후 대응) 키보드 Shift+숫자가 무반응이면 대안 메커니즘 시도: "1"로 그룹 재호출 →
   여분 후보 1기를 **마우스 Shift+클릭**으로 현재 선택에 추가 → Ctrl+1로 재지정 → 그룹1 인원 재측정.
6. 최종 그룹 인원(front/middle/rear 섞어 일부)을 `patches/population/g5_r3_death_bridge.c`의
   op=10(원본 사망 핸들러 `FUN_00409C70` 직접 호출, R3 probe와 동일 기법, 사망 직전 미선택 상태로
   통제)으로 사망시킨 뒤 "1"로 그룹 재호출 → 생존자 수·슬롯 일치, 유령(죽은 슬롯) 미포함, 크래시
   없음, 브로드캐스트 이동 명령 수신까지 확인.

## 실행 결과

- 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, v5 SHA
  `29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146`(lap723~731과 동일) — 둘 다
  실행 전후 `source_unchanged=true`.
- 실행 명령:
  - `PYTHONPATH=. .venv/bin/python -m tools.g5_group_shift_add_death_recall_probe --variant original
    --runtime-root local/runtime/lap732_group_orig --artifact-root
    .../20260928_lap732_group_shift_add_death_recall/group-original`
  - `--variant candidate --runtime-root local/runtime/lap732_group_v5 --artifact-root
    .../group-candidate-v5`
  - (1차 시도 2회는 방법론 수정으로 폐기: 첫 회는 고정 사각형 드래그가 위 장애물에 걸려
    `ProbeError`, 둘째 회는 별도 keydown/key/keyup 방식 Shift+1이 무반응이라 재설계.)

### (1) Shift+숫자 자체

**원본·v5 둘 다 무반응** — Ctrl+1(지정) 6/6 정상, 이후 매 단계 새 유닛 단독 클릭은 정상(단독
선택 count=1 확인) 상태에서 Shift+1을 눌러도 그룹1 인원이 전혀 늘지 않았다(원본 6회, v5 8회 모두
`new_member_present: false`, `members_now`가 매번 동일). 두 가지 입력 전달 방식(①별도
`keydown shift`/`key 1`/`keyup shift` 3콜, ②단일 chord `key shift+1`)을 각각 시도했고 결과가
동일했다 — PROMPT.md ③의 "실패 가설 2회" 기준 결론. 같은 세션에서 Ctrl+1과 "1"(호출)은 정상
동작해 입력 경로·메모리 판독 자체는 검증됐다. **판정: 원본·후보 v5 둘 다 이 게임의 번호-키
핸들러에 Shift 분기가 없는 것으로 판단(미지원, 회귀 아님 — lap727의 ALT/Ctrl 같은종류선택과
같은 종류의 결과).**

### (1-대안) 호출 → Shift+클릭 추가 → 재지정

**원본·v5 둘 다 PASS.** "1"로 그룹 재호출(원본 14명, v5 40명) → 여분 후보 1기를 마우스
Shift+클릭으로 현재 선택에 추가(count +1) → Ctrl+1 재지정 → `unit+0x344` 직접 측정 결과 그룹
인원이 정확히 +1(원본 14→15, v5 40→41), 새 유닛만 추가되고 기존 멤버 전원 유지 확인
(`grew_by_exactly_one: true`, `spare_now_member: true` 둘 다). **그룹 인원을 늘리는 것 자체는
가능하며, 키는 "Shift+숫자"가 아니라 "그룹 호출 → 마우스 Shift+클릭으로 선택 확장 → 같은 번호로
재지정"이다.**

### (2) 부대원 사망 후 호출

- **원본 PASS:** 15명 그룹(bulk 14 + 대안-추가 1)에서 앞(1)/중간(1)/뒤(1) 섞어 3명 사망(사망 직전
  전원 미선택, `op10.dead_flag_after=1`·`selected_before=0` 3/3) → "1" 호출 → 선택 12명, 생존자
  슬롯과 정확히 일치, 유령 없음(`death_recall_check.recall_ok=true`), 이동 브로드캐스트 12/12
  수신(`post_death_move_check.all_survivors_moved=true`).
- **후보 v5 FAIL(신규 발견):** 41명 그룹(bulk 40 + 대안-추가 1)에서 앞(3)/중간(4)/뒤(3) 섞어
  10명 사망(사망 직전 전원 미선택, `op10.dead_flag_after=1`·`selected_before=0` 10/10 — 사망
  처리 자체는 원본과 동일하게 성공) → "1" 호출 → **선택 37명(기대 31명)**. 죽은 10명 중
  **6명(앞 3명 전원 + 중간 4명 중 3명)이 유령처럼 재선택에 포함**되고, 나머지 4명(중간 1명 + 뒤
  3명 전원)만 정상적으로 제외됐다. 같은 실행에서 사망 없이 41명 전원을 호출했을 때는 정확히
  그 시점 그룹 크기(40명, 대안-추가 직전)가 재현돼(`recalled_after_shift_adds.count=40`) **호출
  메커니즘 자체는 생존 그룹에서는 정상**임이 함께 확인됐다 — 결함은 "사망 후"에만 나타난다.
- **추정(정적 미확인, 추측 표시):** 관찰 패턴(일부만 유령, 나머지는 정상 제외)이 R3와 형태가
  유사하다. lap724가 정적으로 확인한 사실(추측 아님)은 그룹이 레거시 20슬롯
  struct(`GROUP1_BASE_ADDRESS`, `control_group_snapshot`)와 유닛 자체 필드(`unit+0x344`,
  `fixture_unit_group_snapshot`) 이중 저장이라는 것이다. 이번 lap의 추정(미확인)은: 호출 시
  레거시 20슬롯 struct 경로는 사망 여부를 재확인하지 않고 지정 당시 스냅샷을 그대로 재선택하고,
  `unit+0x344` 오버플로 스캔 경로만 생존 여부(existence/hp/dead-flag)를 걸러내는 것이 아닐까
  하는 것이다 — disasm으로 확인하지 않았으므로 추측으로만 남긴다.
- R3(선택 배열, `SELECTION_BASE`, lap720~723)와 이번 그룹 호출 결함(`GROUP1_BASE_ADDRESS`/
  `unit+0x344`)은 **서로 다른 메모리 구조**임은 lap724가 이미 정적으로 확인했다(추측 아님). 다만
  "20개 한정 경로 vs 확장 경로가 사망/제거를 다르게 처리한다"는 같은 종류의 버그 패턴을 공유하는
  것으로 보인다는 점은 이번 lap의 추정이다.

## 판정 종합

- (D) **Shift+숫자 추가 = 완료로 판단**(미지원 기능 확인, 대안 메커니즘 PASS, 원본·v5 동일 — 더
  조사할 필요 없음).
- (D) **부대원 사망 후 호출 = 미완료(FAIL, 후보 v5 한정 신규 R3-유사 결함).** 원본은 PASS이므로
  이 결함은 v5의 50-cap 확장이 만든 신규 버그로 보인다(원본 자체 상한 내에서는 재현 안 됨).
- **(D) 체크리스트 전체는 이 결함 때문에 미완료다.** middle/strategy 승인 없이 v6를 임의로
  만들지 않는다(마일스톤 경계, `loop/ESCALATE_SOL` lap732 섹션 추가).

## 안전/검증

- 원본 SHA `source_unchanged` 2/2. 크래시 0(두 실행 모두 `game not alive` 예외 없이 완주).
- `cleanup.prefix_processes_after=[]` 2/2(격리 prefix에 잔여 프로세스 없음).
- 실행 후 `local/runtime/lap732_group_orig/*/game`, `local/runtime/lap732_group_v5/*/game`(각
  ~830MB) 삭제 완료 — output/manifest/log/prefix는 보존.
- 제품 코드(EXE/패치) 무변경. 신규 파일은 `tools/g5_group_shift_add_death_recall_probe.py`(조사용
  도구, pytest 없음, `ruff check` PASS).
- `make check`: **1106 passed(780.08s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS(로그
  `logs/gates/20260928_lap732_make_check.log`). `checks/safety.sh check`: `SAFETY_PASS`.
- 캡처: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap732_group_shift_add_death_recall/{group-original,group-candidate-v5}/`.

## 다음 행동

middle/strategy가 이 신규 결함의 우선순위를 판단한다(다른 (E)~(H)보다 먼저 고칠지 여부).
승인되면: disasm으로 그룹 호출 루틴(추정 `FUN_0040F7D0` 계열)의 20슬롯 struct/오버플로 스캔 두
경로 분기 조건을 정적으로 특정 → 정확한 인덱스 패턴 재현 → v6 후보로 수정 → 이번 probe
(`tools/g5_group_shift_add_death_recall_probe.py`)로 원본·v5 동일 시나리오 재측정. 승인 전에는
G5 (D)를 완료로 선언하지 않는다.
