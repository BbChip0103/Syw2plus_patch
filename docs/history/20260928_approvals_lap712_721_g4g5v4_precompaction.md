# APPROVALS 압축 보존 — lap712~721 (G4 생산 계측/G5 v4 middle·work tier 요청)

원문 140줄, SHA256 `4077e7d84cee6ea3fbeb62d4ac168c7dee7899d25eadeb0f8d9cbf21d81dbeb2`.
`docs/feedback/APPROVALS.md`의 2026-09-28 lap731 압축(체크리스트 (C) 건설/능력/승선
조사, disk hygiene 시점)에서 옮겼다. 원문·판정을 재해석하지 않고 그대로 보존한다.

이 계보의 결론: G4 생산 게이트/크라우드캡 히스토그램(lap712~714)은 2026-09-27 12:05
운영자 판정으로 길찾기·자유대전 AI 트랙 자체가 보류되며 더 진행되지 않았다(STATUS
참고). G5 v4(lap717~721, 선택축소 R1/R3 조사 포함)는 2026-09-28 02:35 운영자 지시로
v5(R3 수정)로 교체됐고, v4에 대한 middle 검수 요청(lap717/719 등)은 v5 직접 재측정
(lap723/724)으로 해소됐다(APPROVALS의 lap723/724 압축 포인터 참고). 즉 아래 원문은
모두 종결된 계보이며 현재 작업에 열려 있는 middle 검수 요청은 없다.

---

- [ ] **2026-09-27 lap721 middle 독립 검수(Claude Code Opus 5.5) — G5 v4 R1 확정 FALSIFIED, 새 R3로 CONDITIONAL
  PASS 유지:** lap720 raw 3개 SHA·재계산 일치(누출0·누락0), v4 재빌드 `0e472792…` 일치, pytest 4 passed, `SAFETY_PASS`.
  원본 disasm: 제거 루틴 `0x412E9F`는 칸 제자리 0화(압축 없음), 명령 본문은 고정20칸+`0x416F70` 검사 → R1 확정 반증.
  같은 근거로 **R3(PLAUSIBLE, v3·v4 공통)**: 50선택 후 사망 등으로 count≤20이 되면 래퍼가 `entries[0:20]`만 쓰는
  본문으로 가 인덱스≥20 생존 유닛이 명령 누락. 확정 승격 불가, 사용자 교체 확인은 R3 결과 후 권고. 원본/후보 run
  scene 불일치(10,49 vs 93,56) 기록 누락 지적. 다음 work: R3 probe, FAIL이면 v5(게이트를 `entries[20:50]` 비0 검사로).
  근거 `../history/laps/20260927_lap721_middle_g5_v4_r1_confirmed_falsified_r3_sparse_gap.md`, `loop/ESCALATE_SOL` lap721.
- [ ] **2026-09-27 lap720 work tier(Claude Code Sonnet, 다음 middle 검수 요청 — G5 v4 R1 선택축소
  누출 FALSIFIED):** 17:25 운영자 판정(lap719 조건부 PASS, R1 미측정)을 수행. 신규 `tools/
  g5_selection_shrink_leak_probe.py`(전체드래그로 최대선택 확립 → 좌측고정·우측폭만 줄이는
  부분드래그를 목표 대역까지 탐색 → STOP → `unit+0x384` 20ms×2.5s per-slot 샘플)로 원본20→15
  (대조, 완전 재선택·겹침0)·후보v4 50→47(겹침41/47)·후보v4 50→27(겹침21/27, 청크2·3 창을 깊게
  관통) 3회 paired 실행 — **전부 `PASS_NO_LEAK`**(선택에서 빠진 유닛이 `0x1000002`를 한 번도
  받지 않음, 새로 선택된 유닛은 전원 수신). 50→27 실행에서 전체 선택-버퍼(용량50칸, count 필드와
  무관하게 read) 축소 전/후 diff를 진단 근거로 추가 확인: 축소 후 `slots_all[27:50]`이 전부 0
  (이전 핸들 잔존 없음) — 게임의 재선택 루틴이 매번 버퍼 전체를 지운다는 구조적 확인이며, R1이
  가정한 "count만 줄고 꼬리 칸은 이전 값 그대로"라는 전제가 저장 동작 자체에서 성립하지 않는다.
  **R1 = FALSIFIED, v5 불필요.** 같은 lap에서 `patches/selection/g5_selection_cap50_v4.py`
  docstring 42~55행(위험 서술)과 `analysis/memory_maps/g5_command_packer_xref_falsification_lap676.md`
  (opcode 집합·`0x41F0A4` 분류)를 lap719 (a)/(b) 근거로 정정했다(원문 보존, 별도 절 추가).
  원본 SHA 3회 `source_unchanged=true`, cleanup 3/3 ok(잔류 0), 크래시 0. `make check`
  1101 passed(880.01s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. **work tier 판단으로
  다음 middle 독립 검수를 요청한다**(원본 20→15 재선택이 진짜 "축소"가 아니라 완전 재선택으로 나온
  것이 유효한 대조인지, 50→27 실행의 버퍼 zero-fill 근거가 R1을 확정 반증하기 충분한지, R1이
  확정 FALSIFIED면 v4의 lap719 CONDITIONAL PASS를 확정 PASS로 올릴 수 있는지, 남은 R2·사용자
  milestone 확인 절차). 근거
  `../history/laps/20260927_lap720_work_g5_v4_selection_shrink_r1_falsified.md`.
- [ ] **2026-09-27 lap719 middle 독립 검수(Claude Code Opus 5.5) — G5 v4 2단 CONDITIONAL PASS, 후보 교체
  경계:** 원본 재해시 `b56986e0…` 일치, v4 원본 재빌드 `0e472792…f9cbb` 일치, pytest 9 passed, 후보 raw 전부
  `private_exe_sha256`=v4·`source_unchanged`. 아래 lap717/718 요청 판정: (a) PARTIAL — v4 게이트는 lap676 문서
  집합과 동일하나 lap676 도구 재실행 raw는 `{0x52,0x56,0x1a0,0x1a1,0x1ae..0x1bc}`(21곳)+`0x41F0A4` 런타임
  `word [0x892ffe]`(실제 명령 발행 호출부)이며 `0x19b/0x19d~0x19f`는 없다(범위 누락 위험만), (b) CONFIRMED 안전
  (즉치 21곳 v3·원본과 동일 동작, 포인터 참조 0), (c) CONFIRMED 유효, (d) lap689 인정 지표(t=0
  `pending==0x1000004`)로 v4 2/5회 49/49 = v3 2/5·원본 2/5 → 추가 N 불요(lap718의 `ever_command4` 근거는 불인정
  유지). 잔여 R1: 50 선택 후 21~49로 선택을 줄였을 때 청크 꼬리 칸 잔존 핸들로 미선택 유닛이 명령을 받는지
  미측정. 사용자 승인은 v3 대상이므로 **v4 교체·G1 재개는 운영자/사용자 판단**(`loop/ESCALATE_SOL` lap719). 근거
  `../history/laps/20260927_lap719_middle_g5_v4_independent_review_conditional_pass.md`.
- [ ] **2026-09-27 lap718 work tier(Claude Code Sonnet, lap717 middle 요청 (d) 보강 — 정보제공,
  새 검수요청 아님):** lap717이 예산상 생략한 v4 후보 공격 N=5를 제품코드 0변경(monkeypatch만)으로
  채웠다. v4(50선택) `ever_command4/49` 5회=30,31,28,24,32(중앙값61%, 24~65%), 원본(20선택)
  lap688 중앙값58%보다 낮지 않고 v3(50선택) lap688 중앙값65%와 같은 변동폭 — v4가 v3보다
  체계적으로 나쁘다는 신호 없음. `attack_pass` 5회 중 2회True(표본잡음, v3 패턴과 동일). 크래시0,
  `source_unchanged` 4회 전부true, `candidate_sha256` 결정론 일치. 아래 lap717 요청의 (a)(b)(c)는
  여전히 미해결 — 이 lap은 (d)만 답했다. 근거 `../history/laps/20260927_lap718_work_g5_v4_attack_n5.md`.
- [ ] **2026-09-27 lap717 work tier(Claude Code Sonnet, 다음 middle 검수 요청 — G5 v3 명령범위
  FAIL 수정, v4 반전게이트+전체 회귀):** 15:49 운영자 판정(v3 후보 정지·홀드·순찰 20/50 FAIL) +
  16:45 후속 지시(회귀 선행)를 수행. ① gdb hook-site(`0x004AE550`) `word[esp+8]` 실측은 4회
  재시도(단일선택→목적지검증→20기그룹선택) 모두 `post_marker_hits=0`으로 **BLOCKED**(lap681이 이미
  발견한 "확인된 실제 MOVE 클릭조차 hook site가 한 번도 안 잡힘" 현상의 재확인·확장 — 방법론 자체
  한계로 판단, 재시도 중단). ② 신규 `patches/selection/g5_selection_cap50_v4.py`: v3 청크 래퍼의
  게이트를 반전(화이트리스트 `{1,3,4,7,8,9}` 대신 lap676이 정적으로 확정한 알려진 비명령/UI알림
  opcode 집합 `{0x52,0x56,0x19b,[0x19d-0x1a1],[0x1ae-0x1bc]}`이면 원본 그대로, 아니면 20초과 선택시
  분할). 청크 본체는 v3와 call-site 재배치를 제외하고 바이트 동일(`test_gate_reproduces_v3_body_
  modulo_call_site_relocation`로 검증), cave 여유 153바이트. 신규 pytest 4/4(결정론+SHA고정
  `0e472792…f9cbb`+cave여유+게이트 opcode/분기 구조를 capstone으로 재확인). ③ 원본20/v4후보50
  paired 행동결과 실측(헤더값 불필요) — **정지(`0x1000002`)·홀드(`0x1000027`)·순찰(`0x1000023`)
  전부 50/50**(v3는 20/50). 16:45 지시로 추가: **이동 50/50**(lap682 도구 재사용, `converged_at_
  s=0.15`), **부대지정+저장/로드 `PASS_UI_ROUNDTRIP`**(lap684 도구 재사용, 7개 check 전부 True —
  `selected_50`·`group_stored_stock20_plus_overflow49`·`deselected`·`recalled_50`·`save_created`·
  `group_retained_after_load`·`recalled_50_after_load`), **공격 단일측정**
  `ever_command4_count=30/49`(61%, lap688의 v3 N=5 분포 27~49·중앙값32 안 — N=5 반복은 시간예산상
  생략). lap682/684 도구는 파일을 수정하지 않고 모듈 전역 `g5`/`TARGET_SHA`를 v4로 monkeypatch해
  재사용(두 파일 자체는 v3 SHA 그대로 무수정). **추가로 direct session이 15:49 FAIL을 낸 도구
  `tools/g5_command_coverage_probe.py` 자체를 같은 방식으로 v4에 연결해 원문 그대로 전체 1회
  재실행** — 정지/홀드/순찰 버튼·단축키 8항목 전부 50/50, ALT/Ctrl/Shift/일반 드래그 전부 50/50,
  미니맵은 원본도 무반응(회귀 아님), `status=COMPLETE`. 원본 SHA `b56986e0…` 전 실행 불변, 후보 SHA
  결정론적 일치, cleanup 매회 프로세스 잔류 0, 크래시 0(5개 probe 전부: 정지/홀드/순찰·이동·
  roundtrip·공격·전체coverage). `make check` 1101 passed(890.28s), ruff/mypy/`CONTEXT_PASS`/
  `SAFETY_PASS` 전부 PASS. **work tier
  판단으로 다음 middle 독립 검수를 요청한다**(v4 게이트 opcode 집합이 lap676 원문과 정확히 일치하는지
  코드 대조, 반전 게이트가 22개 비명령 호출부를 20초과 선택 상태에서 실제로 건드리지 않는지 판단,
  monkeypatch로 얻은 이동/부대지정/저장로드 결과가 유효한 재검증인지, 공격 N=5 반복 추가 필요 여부).
  근거 `../history/laps/20260927_lap717_work_g5_v4_stop_hold_patrol_inverted_gate_pass.md`.
- [ ] **2026-09-27 lap714 work tier(Claude Code Sonnet, 다음 middle 검수 요청 — G4 AI 생산
  게이트 라이브 히스토그램):** 13:45 지시("라이브로 어느 게이트가 owner1 발주를 막는지 계측")를
  수행. 신규 `tools/g4_ai_production_table.py`(`FUN_00406C70` 생산표 레코드 레이아웃 해독 —
  건물타입/생산kind/선행유닛kind·count/기술kind, lap501이 미해독으로 남긴 부분; 143행=생산65+
  연구78·건물타입27종, lap501 수치와 일치)와 신규 `tools/g4_ai_gate_histogram_probe.py`(읽기전용
  `process_vm_readv`, `patches.population.runtime_driver.read` 재사용, 새 EXE 패치/breakpoint
  없이 owner0/1이 보유한 모든 생산건물×생산레코드 조합을 매 tick 분류)로 lap712와 동일 seed1
  fixture 280초를 실행. **결과(278 표본, 3회 실행 — 스모크20s 1회+전체280s 2회 모두 재현):
  H-TYPEMAX/H-RATIO/H-CROWD는 owner0/1 전부 0회. 100%가 H_AVAIL(가용 플래그=0: owner0
  772/owner1 620)과 PREREQ_OWN(선행유닛 미보유: owner0 398/owner1 692) 둘로만 갈리고,
  `WOULD_ACCEPT`는 두 owner 모두 0건.** owner0(HQ type49: kind7/110→H_AVAIL, kind94→
  PREREQ_OWN)·owner1(HQ type58: kind31/75→H_AVAIL, kind102/98→PREREQ_OWN) 모두 최초 건물의
  전 생산레코드가 280초 내내 100% 거부되며, 이후 지은 건물(owner0 type50/51, owner1 type60)도
  같은 두 사유로 100% 거부된다 — **lap712/713이 전제한 "owner1만 약하다"가 아니라 두 owner
  모두 이 두 게이트로 구조적으로 막혀 있다.** 원본 SHA 3회 `source_unchanged=true`, cleanup
  매회 ok, EXE/원본 미변경(순수 메모리 읽기, breakpoint/detour 없음). `make check`
  1079 passed(835.61s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS, 신규 테스트 18개
  (생산표 디코드 5+게이트 분류기 13, synthetic 데이터로 REASONS 전 분기 pin). **work tier
  판단으로 다음 middle 독립 검수를 요청한다**(`FUN_00406C70` 필드 오프셋 해독의 디스어셈블
  재추적, 분류기의 게이트 순서/주소가 lap501·기존 offset 상수와 일치하는지, `by_record` 집계가
  샘플별 중복 계수 없이 정확한지). 운영자가 14:45에 이 결과를 반영해 다음 v2 방향(AI 건설 결정
  히스토그램)을 이미 지시했다(STATUS/INBOX 참고) — 이 work tier 요청은 lap714 계측 자체의
  방법론 검수이며, v2 구현은 다음 work의 몫이다. 근거
  `../history/laps/20260927_lap714_work_g4_ai_production_gate_histogram_h_avail_prereq_own.md`.
- [ ] **2026-09-27 lap713 work tier(Claude Code Sonnet, 다음 middle 검수 요청 — G4 생산 후보
  v1 H-CROWD FALSIFIED):** 13:05 판정("AI 자원 소비(생산 결정) 개선... 상수 1~2개")을 수행.
  `analysis/memory_maps/ai_production_decision_path_00406770_20260923.md`(lap501)가 확정한
  AI 생산 결정 경로 8게이트 중 EXE에 정적 즉치값으로 있는 유일한 상수(H-CROWD, `FUN_00406B00`
  @`0x406c44` 동종·동소유 11×11 밀집 ≥7 발주중단)를 7→14로 올린 후보
  `patches/ai/g4_production_crowd_cap_v1.py`(단일 EDIT, 원본 SHA 가드·copy/restore 회귀
  테스트 7개)를 만들고, `tools/runtime_env.py`의 기존 승인된 named-candidate-exe 메커니즘
  (`G4_CANDIDATE_EXES`, `controller_cadence_probe`/`gather_cooldown_probe`와 동일 패턴)에
  `"g4_production_crowd_cap_14.exe"` 1건을 추가해 `tools/g4_ai_behavior_probe.py --variant
  candidate`로 연결(private `ORIGINAL_EXE`는 건드리지 않음 — 최초 시도는 private 원본을
  직접 덮어써 `g1-baseline`의 `check_runtime` 원본 검증에 막혀 실패, named-candidate 방식으로
  정정). lap712와 동일 seed1 fixture로 후보 N=3(단독 1회+반복 2회) 실행 — **owner0/1 종점
  생산(21/12)·군대(16/10)·자원(9792/23068) 지표가 lap712 원본 N=3과 완전히 동일**,
  **`FALSIFIED`**(H-CROWD가 이 fixture 두 owner 모두에서 안 걸림). H-TYPEMAX/H-RATIO는
  런타임/Data 표 참조라 정적 상수로는 애초에 못 바꾼다(문서 §5). 원본 SHA 3회
  `source_unchanged=true`, cleanup 3/3 ok, 후보 SHA 3회 동일, crash 0. `make check`
  1061 passed(868.47s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. **work tier 판단으로
  다음 middle 독립 검수를 요청한다**(신규 `runtime_env.py` candidate-exe 분기가 기존 두
  candidate와 같은 안전 경계를 지키는지, 단일 EDIT의 바이트 근거 재확인, private `ORIGINAL_EXE`
  미접촉 확인). 다음 work: STATUS가 지정한 라이브 게이트 계측(어느 게이트가 owner1 생산을
  실제로 막는지 breakpoint/counter로 특정) 근거
  `../history/laps/20260927_lap713_work_g4_ai_production_crowd_cap_v1_falsified.md`.
- [ ] **2026-09-27 lap712 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님):**
  12:05 운영자 판정 다음 work ①②(자유대전 AI baseline 원본 N=3, 가장 약한 지표 STATUS 기록)를
  수행. 신규 `tools/g4_ai_behavior_probe.py`가 `runtime_env.py g1-baseline
  --g4-chain-goal _custom_game_chain_inject_seed1 --g4-sample-seconds 280`을 감싸 owner별
  자원수입/생산량(내부 id 신규 관측 근사)/군대규모(초기 HQ·worker 타입 제외 근사)/첫공격시각
  (`command==4` 최초 시각)/유휴일꾼수(worker 타입&`command==1`)를 산출한다. 원본 SHA 3회 전부
  `source_unchanged=true`, cleanup 3/3 ok, EXE/원본 미변경(읽기 전용 관측). 3/3 완전 재현
  (owner0 nation1/HQ49/worker7, owner1 nation2/HQ58/worker31). **owner0
  `idle_worker_count_mean`=0.679(owner1 0.129의 약5.3배)가 owner0 자원 순감소
  (`income_per_min`≈-1119, owner1은 ≈+1734)와 동행 — 가장 약한 지표로 채택.** 단 국가 조합
  1개만 측정했으므로 2026-09-16 lap의 `NO_GO_GENERIC_AI_IMPROVEMENT`(matchup 의존 편향)
  선례와 같은 함정 가능성을 명시하고 범용 결함으로 승격하지 않았다. 280초 내 양쪽 모두
  `command==4`(공격) 0건, `hp_decrease`/`slot_disappearances` 0건 — 2026-09-16 lap의 동일
  `seed1`(옛 소스 경로 `Syw2plus/`)이 240초 내 첫 피해(146~198초)를 재현했던 것과 불일치,
  새 소스 경로(`[ESL]Syw2plus`, 2026-09-26 22:52 전환) 이후 Data/맵 차이 가능성을 원인 미상
  관찰로 기록(조사하지 않음, 후순위). v1 후보는 구현하지 않았다 — 2026-09-16 lap이 같은
  selector(`FUN_0043F5D0`)의 cooldown 상수를 blind로 낮춰 두 번 반려됐으므로, 다음 work는
  그 case3가 호출하는 `FUN_004B03D0`(채집지 순환 상태기)의 완료/실패 조건을 먼저 정적으로
  특정한다. 회귀 신규 4개, `make check` 1054 passed(867.50s), ruff/mypy/`CONTEXT_PASS`/
  `SAFETY_PASS` 전부 PASS. 근거
  `../history/laps/20260927_lap712_work_g4_ai_freeforall_behavior_baseline.md`.
