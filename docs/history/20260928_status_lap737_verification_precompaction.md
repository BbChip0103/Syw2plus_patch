## 검증 상태

**lap717~723(원문 50줄 SHA256 `e6facd6ead26c5496d270a4e4acabed8f336925d6a6b7812d1f6c9cc00d25f63`,
`docs/history/20260928_status_lap717_723_verification_precompaction.md`에 보존):** v4 정지·홀드·순찰
50/50 PASS(lap717), 공격 N=5 중앙값61%(lap718), v4 2단 CONDITIONAL PASS(lap719, middle), R1 확정
FALSIFIED·R3 발견(lap721, middle), R3 raw CONFIRMED(FAIL)·v5로 PASS(lap723) — 단 lap723은
ALT/Ctrl/Shift 드래그·공격·부대저장로드를 `g5_command_coverage_probe.py` 캘리브레이션 실패로 v5
직접 재측정 못함(byte-identical 추론에만 의존).

**lap724~727(원문 43줄, SHA256 `73be8e5998838794bf8c953b5c1cde6fd359b0dbf7a18e61d94e15132b7f26ff`, `docs/history/20260928_status_lap724_727_verification_precompaction.md`에 보존):** v5를 coverage/roundtrip/attack 3개 도구에 직접 raw 연결해 lap723 미완결(ALT/Ctrl/Shift 드래그·부대저장로드·공격) 전부 PASS(lap724). 체크리스트 (A) 정적 전수 표 작성 + (B) R3 middle/rear 사망 시나리오 PASS(lap725). (B) Shift+클릭 제거·51번째 거부 PASS(lap726). (B) 더블클릭 같은종류선택 PASS(원본20/v5 50)·ALT/Ctrl 같은종류선택과 포트레이트 클릭 해제는 원본·v5 둘 다 이 게임에 없는 기능으로 확인, 회귀 아님(lap727). 매 lap `make check` 1106 passed·`SAFETY_PASS`·크래시0·`source_unchanged`.

**lap728(work):** 05:36 운영자 판정(Shift+클릭 개별 추가 격리 재확인)을 수행. 신규 `tools/g5_shift_click_add_probe.py`가 worker 기준 맨해튼거리≥3 희소 오프셋에 유닛을 스폰하고 단독 plain 클릭으로 겹침 없음을 먼저 확인(원본·v5 둘 다 9/9 격리 PASS)한 뒤, plain 클릭 1회+Shift+클릭 5회 순서를 실행 — **원본·v5 둘 다 6단계 전부 PASS**(count 1→2→3→4→5→6, 매 단계 새 슬롯 포함·이전 슬롯 유지, 최종 6기 전원 이동 명령 수신). **lap727 05:15 관찰(원본 2→3, v5 1→2)은 조밀 fixture 스프라이트 겹침 아티팩트였음이 확정됐다(v5 결함 아님).** 크래시0, `source_unchanged` 2/2, `make check` 1106 passed(764.94s), `SAFETY_PASS`. 상세 `docs/history/laps/20260928_lap728_work_g5_shift_click_add_isolated_pass.md`.

**lap729(work, 이 세션):** 체크리스트 (C) 명령 전부의 첫 항목 **일꾼 채집(gather)**을 측정. 신규 `tools/g5_worker_gather_command_probe.py`가 런타임에 읽은 실제 일꾼 unit_type(=7)으로 worker 기준 7x8 격자(55기)를 스폰하고, 라이브 일꾼 우클릭 탐색으로 채집 pending word(`0x1000008`)를 내는 목적지(오프셋 (0,6))를 고정한 뒤, 전체 드래그 선택 후 그 목적지 우클릭 결과를 관측 — **원본 20/20·v5 50/50 전원 채집 명령 수신 PASS**(`0x41F0A4` 공용 opcode 게이트가 이동/공격/정지류/부대지정에 이어 채집에도 일반화됨을 확인). 후보 1회차는 `unsupported_army_fixture_type` 일회성 flake로 FAIL했으나 원본이 같은 type=7로 55/55 성공했으므로 브리지 게이트 결함이 아니라 판단, 재실행(v5_r2)으로 COMPLETE·PASS 확보. 크래시0, `source_unchanged` 3/3(FAIL 포함), `cleanup.prefix_processes_after=[]` 3/3. `make check` 1106 passed(787.50s), `SAFETY_PASS`. 상세 `docs/history/laps/20260928_lap729_work_g5_worker_gather_command_pass.md`.

**lap732(work, 이 세션):** (D) 잔여 Shift+숫자 추가·부대원 사망 후 호출을 신규
`tools/g5_group_shift_add_death_recall_probe.py`(원본1회·v5 1회)로 측정. Shift+숫자 자체는
원본·v5 둘 다 무반응(미지원 판정), 대안("호출→Shift+클릭 추가→재지정")은 둘 다 PASS(+1 정확).
**부대원 사망 후 호출은 원본 PASS(15명 중 3명 사망→12명 정확), 후보 v5 FAIL(41명 중 10명
사망→37명 선택, 6명 유령 재선택)** — R3-유사 신규 결함, `loop/ESCALATE_SOL` lap732 승격.
크래시0, `source_unchanged` 2/2, `cleanup.prefix_processes_after=[]` 2/2. `make check`
1106 passed(780.08s), `SAFETY_PASS`. 상세
`docs/history/laps/20260928_lap732_work_g5_checklist_d_shift_add_death_recall.md`.
