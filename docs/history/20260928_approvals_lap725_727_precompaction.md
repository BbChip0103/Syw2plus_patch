# APPROVALS 압축 보존 — lap725~727 (2026-09-28)

lap728 압축 전 `docs/feedback/APPROVALS.md` 11~61줄(51줄) 원문 그대로 보존.
SHA256(이 파일의 원문 블록): `6ac0a16048bac604fac3ab99e788310a2453f4bbf9e83cb0be8f5acf79b3c580`

- [ ] **2026-09-28 lap727 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** G5 완료
  체크리스트 **(B) 잠정 완료**. lap726 다음 한 가지(더블클릭/ALT·Ctrl 같은종류선택/포트레이트 해제)를
  `tools/g5_command_coverage_probe.py`에 라이브 실측 추가해 측정 — 더블클릭 같은 종류 전체 선택은
  **지원함, PASS**(원본 20/20·v5 50/50, 둘 다 기존 `plain_fulldrag` 상한과 정확히 일치, 51번째도 새지
  않음). ALT/Ctrl 클릭 같은 종류 선택은 원본·v5 둘 다 단일클릭과 동일(`count=1`)해 **이 게임에 그 기능
  자체가 없음**(회귀 아님). 포트레이트 클릭 해제는 다중 선택 캡처(원본·v5 둘 다, 이번 lap+lap726 재확인)에서
  개별 유닛 초상화 행이 아니라 단일 원형 "타입" 배지만 보여 **이 게임 UI에 해당 기능이 없음**(단일
  선택시만 캐릭터 얼굴+이름+스탯 표시). 크래시0, `source_unchanged` 2/2, 고아 프로세스 0. `make check`
  **1106 passed(797.09s)**, ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS, targeted pytest 44
  passed(제품 코드 무변경). **05:15 운영자 관찰 검토(같은 raw, 새 실행 없이):** Shift+클릭 개별 추가가
  원본 `shift_click_unit`=2→`second`=3, v5는 1→2로 시작값이 다르다는 관찰에 대해, 두 값 모두 두 번째
  클릭에서 정확히 +1 증가함을 재확인 — 시작값 차이는 lap726이 이미 문서화한 조밀 fixture 스프라이트
  겹침 아티팩트(어느 run이 겹침 위치에 걸렸는지의 차이)와 일치하며 추가 자체의 결함 신호는 아니라고
  잠정 판단했으나, 겹치지 않는 고정 좌표로 격리 재확인 전까지 (B)를 최종 확정하지 않는다(다음 work).
  **work tier 판단으로 다음 middle 독립 검수를 요청하지 않는다**(운영자 판정대로 체크리스트 전체 완료
  후 한 번에). 근거 `../history/laps/20260928_lap727_work_g5_doubleclick_altctrl_portrait_checklist_b.md`.
- [ ] **2026-09-28 lap726 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** G5 완료
  체크리스트 (B) 잔여 중 **Shift+클릭 제거**와 **51번째(21번째) 유닛 드래그 거부**를 v5/원본 raw로
  측정. `tools/g5_command_coverage_probe.py`에 두 블록을 추가했다(제품 EXE/원본 무접촉, 이 파일을
  참조하는 pytest 없음). Shift 토글-제거: 이미 선택된 유닛을 Shift+클릭으로 다시 클릭하면 그 유닛만
  선택에서 빠지고(`removed_anchor1=true`), 남은 선택 유닛은 유지되며(`kept_anchor2=true`), `step()`의
  자동 재선택을 피해 `observe()`를 직접 호출해 toggle 직후 이동 명령이 남은 유닛에게만 가고
  (`command_changed_to={'3':1}`, 관찰 2슬롯 중 1개) 제거된 유닛은 받지 않음(`anchor1_excluded_
  from_move=true`)을 원본·v5 각 1회 확인(1차 시도는 `step()` 재선택 실수로 무의미했음을 같은 lap
  안에서 발견·재설계). 51번째 거부: 55기+일꾼 pool 56에서 원본은 정확히 20(`matches_capacity=true`),
  v5는 정확히 50(`matches_capacity=true`)만 선택. 크래시0, `source_unchanged` 2/2,
  `cleanup.prefix_processes_after=[]` 2/2. `make check` **1106 passed(787.21s)**, ruff/mypy/
  `CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. **다음 work**: (B) 잔여(더블클릭 같은 종류 선택/ALT·Ctrl
  클릭 같은 종류 선택/포트레이트 클릭 해제 — 이 게임이 실제로 지원하는지부터 라이브 확인) → (C) 명령
  전부. 근거 `../history/laps/20260928_lap726_work_g5_shift_toggle_51st_rejection.md`.
- [ ] **2026-09-28 lap725 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** G5 완료
  체크리스트 (A) 정적 전수 표와 (B) 중간/뒤 엔트리 사망 일반화를 수행. (A)는 새 정적 스캔 없이
  lap627/640/657/661/676/685/717/719/721/723의 기존 raw 근거를 `analysis/memory_maps/
  g5_selection_consumers_inventory_20260928.md` 한 문서로 통합 — 옛 선택배열 리터럴 참조 52건(=
  `DIRECT_SITES`38+`END_SITES`14, 잔여0, lap685 재확인), 로테이션/소비자프레임/hit-test/부대지정
  20-전제 4그룹(전부 v1·v2에서 재배치 완료, 소비자프레임의 lap679 크래시·lap680 수정 이력 포함),
  `FUN_004AE550` 22개 직접 호출자(21 무해 고정opcode+1 실제주문 `0x41F0A4`, lap676/719 분류), v3/v4/v5
  게이트 차이와 R1(FALSIFIED)/R2(미실측, 열림)/R3(CONFIRMED→v5로 수정) 표. 간접 호출 부재는 정적으로는
  미증명(경험적 반증만 존재)으로 §5에 명시. (B)는 `tools/g5_r3_sparse_selection_probe.py`에
  `--scenario {front-death,middle-death,rear-death}`를 추가(lap723의 원래 "앞쪽 K개 사망" 로직은
  `front-death` 기본값으로 보존, 함수 단위 스모크로 산출 일치 확인)해 v5 candidate로 middle-death(사망
  인덱스10~39, 생존0~9+40~49 분산 20기, count=20 정확히 경계값) PASS, rear-death(사망20~49, 생존0~19
  전원 `entries[0:20]` 안 — sparse-scan 음성대조) PASS를 raw 측정, 원본 대조 2건도 PASS(방법론이 사망
  위치 무관 유효). 크래시 0, `source_unchanged` 4/4, `prefix_processes_after=[]`(고아 없음, lap724가
  본 Xvfb 고아는 이번 4회에서 재현 안 됨). `make check` **1106 passed(903.49s)**, ruff/mypy/
  `CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS(신규 pytest 0개 — probe 도구 일반화+문서, 제품 코드 무변경).
  **다음 work**: (B) 잔여(Shift 제거/더블클릭/포트레이트 해제/51번째 거부) → (C) 명령 전부. 근거
  `../history/laps/20260928_lap725_work_g5_checklist_a_inventory_b_middle_rear_death.md`.
