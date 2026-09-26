# 2026-09-21 | lap 414 | G2 — lap413 P2 FAIL 독립 검수 + fault root-cause 범위 확정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(진단·계획·확인)**.
  게임 실행 0회, 제품 코드 변경 0, 커밋 0. 하네스/게임 코드는 손대지 않았다.
- 가설 / 사용자 관찰: lap413이 보고한 P2 FAIL(`0x00414133` read `0x00338400`)이 원시 산출물만으로
  재현 검증되는가, 그리고 **선행 손상**의 범위를 바이트 수준으로 좁힐 수 있는가.
- 예상 PASS / FAIL 조건: PASS = 요약 JSON을 쓰지 않고 raw(trace/samples/wine.log/manifest/실행 파일
  재해시)만으로 lap413 수치를 재계산해 불일치 0. FAIL = 하나라도 어긋나면 REJECT.

## 변경 파일 / source fingerprint / 커밋

- 제품 소스 변경 **0**(이번 회차에 source를 바꾸지 않았다 — INBOX 21:58 규칙 적용 근거).
- 신규 문서: `docs/work/active/G2_POOL_SCOPE_1200_FAULT_ROOT_CAUSE_LAP414.md`(W10), 이 기록,
  `docs/STATUS.md` 갱신.
- 검수 스크립트/산출물(공유 temp, 제품 아님):
  `temp/Syw2plus_patch/g2_capacity/20260921_lap414_middle_review/`
  — `recompute_lap413.py` / `recompute_lap413.json` / `disasm_fault_site.py` /
  `fault_site_disasm.json` / `find_fault_callers.py` / `fault_callers.json`.
- 커밋: 없음(LOOP_ALLOW_COMMITS=0). uncommitted 보존.

## 원본 SHA / 후보 SHA / 환경 / fixture

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — 검수 후 2경로 재해시 불변
  (`syw2plus_original.exe`, `조선의반격 오리지날 실행.exe`).
- 후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`(N=4001 marked compat),
  stock 대조 `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`(N=1200, supply5000).
- **실행 파일 신원은 lap413 보고를 믿지 않고 직접 재해시했다**: 세 run 모두 `session.json`이 지목한
  `game/syw2plus_original.exe`의 실제 SHA가 주장값과 일치. (같은 디렉터리의 `game.exe`는 stock이며
  실행되지 않았다 — lap412가 지적한 함정을 다시 확인.)
- fixture: op7(원본 SetResource `0x43ED60/0x43ED80`) 자원만. 8인, 동일 seed/goal, 격리 prefix/display.

## 실행 명령 / 로그 경로

- `python3 recompute_lap413.py`, `python3 disasm_fault_site.py`, `python3 find_fault_callers.py`
  (모두 위 검수 디렉터리).
- 원시 입력: `local/runtime/{20260920_231852_1903351_0, 20260920_234044_2001774_0,
  20260920_233057_1948800_0}/driver_out/{trace.jsonl,wine.log,session.json,exit.json}` +
  각 run의 `manifest.json` + `temp/.../20260921_lap413_*/{samples,progress,resource_receipts,
  baseline_snapshot,final_snapshot}.json`.
- 검사: `checks/safety.sh check` → `SAFETY_PASS`.
  `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` → **6 passed in 48.63s**.
  전체 `make check`는 **재실행하지 않았다**(이번 회차 source 변경 0, 직전 lap413이 통합 경계에서
  786 passed로 실행함).

## 측정값 / 판정

**판정: lap413 P2 FAIL — ACCEPT(불일치 0건).** 요약 JSON은 근거로 쓰지 않았다.

| 항목 | 후보 run1 | 후보 run2 | stock 대조 |
|---|---|---|---|
| 마지막 생존 샘플 | tick 11,928 / 468기 | tick 11,928 / 468기 | tick 13,116 / 405기 |
| 최고 owner | 5: used1208 / count84 / reserved25 | 동일 | 6: used966 / count70 |
| wine page fault | read `0x00338400` @ `0x00414133` | **동일** | **0건** |
| 종료 상태 | ps3 정지(11,928) | ps3 정지(11,928) | ps29 / 13,804에서 0기 |
| op7 영수증 장부 변화 | 7건·21필드 중 **0** | 동일 | 동일 |

- **N25(신규, 결정성 강화):** 두 후보 run은 신규 prefix·신규 브리지 DLL(SHA 다름)임에도
  **공유 tick 46개 전부에서 owner별 `used/count/reserved`가 완전히 일치**(불일치 0). lap413은
  "정확히 같은 진행"이라고만 적었으나, 실제로는 시뮬레이션 상태 수준의 결정성이며 tick bisect가 유효하다.
- **N26(신규, fault 기전 확정):** `0x00414000`은 Bresenham 경로점 생성 후 샘플링하는 함수이고
  호출자는 `0x0040be55` **단 하나**다. fault 명령은 **100칸 stack 배열**을 `edx = ((점수-1) ×
  |unit.word[+0x692]|)/100`로 읽는다. `+0x692`는 `0x0040bc86~0x0040bcff`가 누적하는 타일 간
  이동 진행도로 50에서 다음 타일로 넘기며 100을 빼므로 정상 범위는 약 `[-100,100)`이고 그 경우
  `edx ≤ 99`다. ⇒ **fault는 이 필드(또는 그것을 담은 구조체 포인터)가 망가져야만 성립**하며,
  fault 지점 ±0x180 바이트는 원본·후보 **완전 동일**이다. 명령 자체 패치는 금지 대상이다.
- **N27(신규, 잔존 1200-bound):** 후보는 `.text`의 `0x4B0` 즉치 **54곳 중 2곳만** `0xFA1`로 바꿨다
  (`0x00441444`, `0x0044317f`). 남은 곳 중 풀을 실제로 순회하는 site 최소 3개를 확인했다 —
  `0x00422dc0`(풀 base는 `0x66b790→0x0108c000`으로 재배치됐는데 `mov edi,0x4B0` 루프 카운트는
  그대로 ⇒ 4001칸 중 0~1199만 슬롯당 `0x48aff0` 처리), `0x004183a0`(필드 4곳은 재배치됐는데
  `idiv 0x4B0` 2곳·`cmp bx,0x4B0` 경계는 그대로), `0x00444efe`(`cmp esi,0x4B0`, 주소 즉치가 없고
  매니저 `0x61e36c` 경유라 **주소 기반 fixup이 원리적으로 못 보는 부류**). 무관 오탐도 분류했다:
  `0x004a8843/48`(1200×1200 표면), `0x004c470f`(900~1300 표), `0x00491911`/`0x004922b9`
  (실제 값은 주소 `0x0104b010`). `roster_add 0x0043ee39`의 `cmp ax,0x4B0`은 lap397대로
  **owner당 개수 상한**이므로 유지 대상이다.
- **N28(신규, 슬롯 분포):** 원본 할당기는 풀을 **위에서 아래로** 채운다 — 매치 시작 시 후보는
  slot 3985~4000, stock은 1184~1199(둘 다 16기, `internal_id == slot`). crash tick의 후보 live
  468기는 **전부 3533~4000**이고 슬롯 0~1199에는 0기다. owner별 유닛 수는 엔진 자신의 `count`와
  8/8 정확히 일치(중복 id/슬롯 0, hp 400~4800, 좌표 1~99) ⇒ reader 왜곡이 아니다.
  ⇒ N27의 1200-bound 순회들은 후보에서 **살아있는 유닛이 0기인 구간만** 훑고, stock에서는 전 유닛을
  훑는다. 후보 고유 발산의 구조적 설명이며 P-A/P-B로 직접 시험 가능하다.
- **정정1(무해, 출처 구분):** 통합 요약 JSON은 run2/stock의 `driver_exit`를 0으로 적었으나 원시
  `exit.json`은 세 run 모두 `returncode: null`이다. 또 run1의 `stalled`는 `null`로 적혔지만 run1의
  samples는 tick 11,928에 9개 샘플이 고정(602.2초)되어 **run2와 같은 정지**다 — 탐지 임계값 차이일 뿐
  거동 차이가 아니다. run1 `progress.json`은 `status=FAILED / TimeoutError: (7,1)`, run2는 `COMPLETE`.
  판정에는 영향이 없다.
- **한계(lap413 서술 유지):** stock 대조군은 **다른 바이너리·다른 풀 크기**이며 전투 전개도 후보와
  같지 않다. 따라서 "그 tick의 일반 엔진 버그가 아니다"까지만 경계 짓고, 후보 고유 명령 결함을
  단독으로 증명하지 않는다. 이번 검수는 그 경계를 넓히지 않는다.

## 회귀 / 남은 위험 / 독립 검수·승인 상태

- 이 회차 결론은 `inmm_stub.c`/`ai_shadow.c`/`sfx_hook.c`/`control_executor.c` stub 채널 산출물에
  **근거하지 않는다**(N21 규칙). 전부 `trace.jsonl`/samples/snapshot/wine.log/PE 바이트다.
- N27의 site 목록은 **정적 분류이며 아직 런타임 인과 증명이 아니다.** 수리 착수 전에 W10 §3 P-A
  probe로 H1/H2를 먼저 갈라야 한다. 지금 상태에서 1200을 4001로 바꾸는 즉석 패치는 금지한다.
- 제품 마일스톤 승인 없음. W8 ACCEPT를 일반 플레이 안정성으로 승격하지 않는다(P2 FAIL 유지).
- 안전: 원본 불변, 게임 미실행, 생성 프로세스 0, 다른 저장소/프로세스 미개입.

## 다음 한 가지

work(Sonnet5/high)가 **W10 `docs/work/active/G2_POOL_SCOPE_1200_FAULT_ROOT_CAUSE_LAP414.md`**의
P-A(읽기 전용 이동상태 샘플러)로 H1/H2를 가른 뒤, 지목된 **단 하나의** 원인만 최소 수리하고
동일 fixture로 재실행한다. PASS 기준은 tick 11,928 통과 + page fault 0건이며 `used≥4900`은 아니다.
