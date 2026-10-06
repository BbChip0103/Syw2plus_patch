# STATUS 압축 보존 — 검증 상태 lap724~727 상세 (2026-09-28, lap728 압축)

lap728 압축 전 `docs/STATUS.md`의 '검증 상태' 절 lap724~727 상세 문단(43줄) 원문 그대로 보존.
SHA256(원문 블록): `73be8e5998838794bf8c953b5c1cde6fd359b0dbf7a18e61d94e15132b7f26ff`

**lap724(work, 자체 raw 관측):** lap723 미완결 3항목을 v5로 **직접 raw 재측정 — 전부 PASS**.
`g5_command_coverage_probe.py` 목적지 캘리브레이션에 fallback 오프셋 12개 추가(방어적, 이번 run은
미사용 — 월드(10,49) 착지) 후 재실행 → 이동·정지·홀드·순찰(버튼+단축키) 50/50, **ALT/Ctrl/Shift/
plain 드래그 50/50(최초 v5 직접측정)**. `g5_candidate_drag_probe.py --ui-roundtrip` v5 monkeypatch
→ **부대지정+저장/로드 7/7 checks True**. `g5_worker_relative_move_attack_probe.py` v5 monkeypatch
→ 이동 50/50·표적uid 1기 정확 일치·`ever_command4_count=32/49`(v3/v4 N=5 분포 24~65% 안, 회귀
신호 없음). 크래시0, `source_unchanged` 3/3. `make check` **1106 passed(929.16s)**, `SAFETY_PASS`.
**발견(제품 무관):** attack probe 종료 후 JSON `xvfb_stopped=true`였으나 실제 `Xvfb` 고아 2개가
남아 세션 안에서 발견·수동 정리(원인 미조사, 후순위). 상세
`docs/history/laps/20260928_lap724_work_g5_v5_direct_coverage_roundtrip_attack.md`.

**lap725(work, 이 세션):** 체크리스트 **(A) 완료** — 기존 lap627~723 근거를 통합한 정적 전수 표
`analysis/memory_maps/g5_selection_consumers_inventory_20260928.md`(옛 배열 리터럴 52건=잔여0,
로테이션/소비자프레임/hit-test/부대지정 20-전제 4그룹, `FUN_004AE550` 22호출자=21무해+1실제주문,
v3/v4/v5 게이트 차이와 R1/R2/R3 표). **(B) R3 일반화** — `g5_r3_sparse_selection_probe.py`에
`--scenario {front-death,middle-death,rear-death}` 추가(`front-death`=기존 lap723 동작, 단위
스모크로 산출 일치 확인). v5 middle-death(사망10~39, 생존0~9+40~49, count=20 경계) PASS, v5
rear-death(사망20~49, 생존0~19 전원 entries[0:20] 안 — 음성대조) PASS, 원본 대조 2회 PASS. 크래시0,
`source_unchanged` 4/4, 고아 프로세스 0. `make check` **1106 passed(903.49s)**, `SAFETY_PASS`. 상세
`docs/history/laps/20260928_lap725_work_g5_checklist_a_inventory_b_middle_rear_death.md`.

**lap726(work, 이 세션):** 체크리스트 **(B) Shift+클릭 제거 = PASS**(원본·v5 둘 다) — 이미 선택된
유닛을 Shift+클릭으로 다시 클릭하면 그 유닛만 선택에서 빠지고, 남은 선택 유닛은 유지되며 그 뒤
이동 명령이 남은 유닛에게만 가고 제거된 유닛은 받지 않음을 raw로 확인(`g5_command_coverage_probe.py`
확장, `step()`의 자동 재선택을 피해 `observe()` 직접 호출로 재설계). **51번째(21번째) 유닛 드래그
거부 = PASS**(원본·v5 둘 다) — 55기+일꾼 pool 56에서 원본은 정확히 20, v5는 정확히 50만 선택.
크래시0, `source_unchanged` 2/2, 고아 프로세스 0. `make check` **1106 passed(787.21s)**,
`SAFETY_PASS`. 상세 `docs/history/laps/20260928_lap726_work_g5_shift_toggle_51st_rejection.md`.

**lap727(work, 이 세션):** 체크리스트 **(B) 완료** — 더블클릭 같은 종류 전체 선택 = **지원함, PASS**
(원본 20/20·v5 50/50, 둘 다 `plain_fulldrag`과 정확히 같은 상한이라 51번째도 새지 않음). ALT/Ctrl
클릭 같은 종류 선택 = **이 게임에 없음**(원본·v5 둘 다 단일클릭과 동일 count=1, 회귀 아님). 포트레이트
클릭 해제 = **이 게임 UI에 다중 선택용 개별 초상화 행 자체가 없음**(원본·v5 다중 선택 캡처 모두 같은
원형 "타입" 배지 1개만 표시, 이름/스탯 없음 — 단일 선택 때만 캐릭터 얼굴+이름+스탯 표시). `make check`
**1106 passed(797.09s)**, `SAFETY_PASS`, targeted 44 passed, 크래시0, `source_unchanged` 2/2, 고아0.
상세 `docs/history/laps/20260928_lap727_work_g5_doubleclick_altctrl_portrait_checklist_b.md`.
**05:15 운영자 관찰 검토(같은 lap727 raw 재확인, 새 실행 없이):** 원본 `shift_click_unit`=2→
`shift_click_second_unit`=3, v5는 1→2 — 두 변형 모두 두 번째 Shift+클릭에서 **+1로 정확히 증가**해
추가 자체는 양쪽 다 작동한다. 차이는 첫 클릭의 시작값(2 vs 1)뿐이며, 이는 lap726이 이미 문서화한
"원본 800×600 렌더에서 조밀한 fixture 스프라이트가 화면상 겹쳐 단일 클릭이 겹친 2기를 동시에 선택"
아티팩트(이번엔 어느 run이 그 겹침 위치에 걸렸는지가 바뀌어 나타난 것)와 일치한다 — **결함 신호
아님**으로 잠정 판단하나, 원본/v5 공통 코드 경로이므로 다음 work가 겹치지 않는 고정 좌표로 격리
재확인해 확정한다(운영자 지시 유지, 아래 다음 한 가지).
