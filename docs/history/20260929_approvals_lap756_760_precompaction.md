# APPROVALS lap756~760 work tier 정보제공 계보 원문 보존 (2026-09-29, lap763 압축)

SHA256 `7d693378630c3b7d14d10e1a1ad6bd036cf60f0acd57eae909b763c2ebd6e864`(원문 72줄)

- [ ] **2026-09-29 lap760 work tier 정보제공(middle 독립 검수 아님): G5 사용자 항목(2) ① 수확(V)
  paired PASS, ② 미니맵 ddraw native override 부정 결과.** 11:25 지시 처리. **①**: 신규
  `tools/g5_worker_harvest_v_command_probe.py`(worker unit_type을 게이트-스폰하려던 op=5 fixture가
  로비 국가 랜덤화로 5회 `unsupported_army_fixture_type` FAIL — worker_type 21/21/21/31/31 관측,
  lap730이 이미 발견한 "국가 랜덤" 재확인일 뿐 새 결함 아님)를 `BRIDGE_SOURCE`를
  `patches/population/g5_c_repair_bridge.c`(lap730에서 이미 검증된, 고정 allow-list 대신 구조적
  게이트(flags bit1/2/3=0, width/height∈[1,8])만 쓰는 private fork, 공유 G2-pinned
  `runtime_bridge.c` 무변경)로 바꿔 해소 — **원본20 전원(20/20)·후보v10 50 전원(50/50) V-버튼+좌클릭
  채집 pending(`0x1000008`) 수신 PASS**. **②**(이전 세션 구간에서 이미 실행): 신규
  `tools/g5_minimap_ddraw_native_override_probe.py` 3변형(builtin control/native override/native+
  명시적 LoadLibrary) 전부 `minimap_render_signal=false`·`minimap_click_signal=false` — native
  ddraw.dll override가 검은 미니맵의 원인이 아님을 실측 반증(UNKNOWN 유지, 부정 결과지만 실행
  증거 확보). 크래시0, `source_unchanged` 전부 true, `cleanup.prefix_processes_after=[]` 전부.
  `pytest -ra` 1131 passed·5 skipped(662.41s), ruff/mypy/compileall/`CONTEXT_PASS`/`SAFETY_PASS`
  개별 실행 전부 PASS(제품 코드 무변경, 신규 진단 도구만 — lap758/759와 동일 판단으로 전체 `make
  check` 자동화 러너 생략). **다음 work가 미니맵 클릭 입력 핸들러 브레이크포인트 조사를 잇거나
  lap758 잔여(V 정확 대상·I 국가)로 진행, 그 다음 middle이 항목(1)+(2) 전체 독립 재검수.** 상세
  `../history/laps/20260929_lap760_work_g5_item2_harvest_v_pass_minimap_ddraw_negative.md`.
- [ ] **2026-09-29 lap759 work tier 정보제공(middle 독립 검수 아님): G5 사용자 항목(2), 미니맵
  하위질문① — 서브시스템 활성 여부를 정적+실시간으로 재확인.** lap758이 제안한 "카페 커뮤니티 주소
  `0x451C12`/`0x451C19` 실시간 읽기"를 objdump 정적 분석으로 먼저 검증 — **전제 반증**: 두 주소는
  `mov [ecx],0x0`/`mov [ecx+0x4],0x1fd` 명령의 imm32 피연산자 내부 바이트로, 실행 여부와 무관하게
  항상 상수값(읽어도 무의미). 전수 xref(0x400000~0x800000)로 진짜 타겟을 재구성: 이 leaf 함수
  (`0x451C10`)의 유일한 호출자는 `0x451138`(큰 구조체 초기화 함수 `0x451130` 내부), 호출 직전
  `ecx`=고정 정적 주소 `0x639350`. 신규 `tools/g5_minimap_init_breakpoint_probe.py` +
  `tools/g5_minimap_init_entry_trace.py`(non-invasive gdb 진입 카운트)로 원본 프로세스 시작
  (메인 메뉴 도달 전)부터 메뉴→솔로 로비→인게임→미니맵 좌/우클릭+m/Shift+M/Tab 키까지 전체 세션을
  관찰 — **`widget_ctor_FUN_00451130`/`xy_writer_FUN_00451C10` 둘 다 정확히 1회씩 호출 확인(PASS)**.
  호출 시 `ecx`=`esi`=`0x639350`(정적 분석과 일치), 복귀주소 `0x41b59f` 주변이 기존 G5
  새게임초기화(H-NEWGAME-INIT, `0x892410`/`0x4a3060`, lap752~754) 조사와 동일 코드 영역임을 확인해,
  미니맵 위젯 X/Y(0,509) 초기화가 "새 게임 시작" 경로의 일부로 1회 실행됨을 실증했다. **결론: 미니맵
  서브시스템은 완전 비활성이 아니라 위젯 구조체가 실제로 초기화된다** — lap758의 독립 negative 증거
  (참고 저장소도 렌더 함수를 못 찾음)와 모순되지 않는다("초기화됨"과 "렌더됨"은 별개 질문). 크래시0,
  `source_unchanged`·`cleanup.ok`, 제품 코드 0 변경(신규 조사 도구 2개+메모리맵 문서만). `checks/
  safety.sh check` → `SAFETY_PASS`, ruff PASS(`make check` 전체는 미실행 — 제품 코드 무변경, lap758과
  동일 판단). **다음 work가 `0x639350`/`0x639354`(런타임 위젯 X/Y)를 카메라 이동·미니맵 클릭 전후에
  재읽어 값 변화를 확인하거나, lap758 잔여 항목(a) "V" 대상·(b) "I" 국가로 진행한다.** 상세
  `../history/laps/20260929_lap759_work_g5_minimap_widget_ctor_live_trace.md`,
  `../../analysis/memory_maps/g5_minimap_widget_ctor_lap759.md`.
- [ ] **2026-09-29 lap758 work tier 정보제공(middle 독립 검수 아님): G5 사용자 항목(2) "v"/"f" 능력
  명칭·부분조건 확정, 미니맵 원본 미발견의 독립 provenance.** 신규 `tools/g5_command_menu_slot_probe.py`
  (읽기 전용, 제품 코드 0 변경). worker 커맨드 메뉴 슬롯 배열(`+0x532..+0x57A`)을 직접 읽어
  `btn=[0x1,0x2,0x5,0x6]`을 확인(slot0/1=Stop/Move와 일치, 참고 저장소 `command_menu.h` 2026-08-24
  정정본과 부합 — 오프셋 유효성 검증 PASS). 버튼 클릭 시 게임이 슬롯 라벨을 한글 텍스트로 바꿔
  보여주는 것을 캡처로 확인: **"V"=수확(0x05), "F"=옮기기(0x06)**. F는 밭 타일 우클릭 시 `+0x290`
  1→3(이동중) 실제 변화 2/2 확인. V는 밭 타일 4곳×좌/우클릭 5회 전부 무반응(정확 대상 미확정).
  "I"는 이 국가 fixture에 없었음(다른 국가 필요, 미확인). 미니맵: 참고 저장소 `Syw2plus_re`(read-only)의
  독자 disassembly도 원본 미니맵 렌더 VA를 끝내 못 찾았음을 확인 — 이 프로젝트의 lap677/lap710(위젯
  3종 전부 무반응) 결론과 독립적으로 부합, 실행 증거 추가는 없음(cafe 커뮤니티 실측 주소
  `0x451C12`/`0x451C19`/`0x4F2E8B` 실측은 다음 work). `checks/safety.sh check` → `SAFETY_PASS`,
  ruff/compileall PASS(`make check` 전체는 미실행 — 제품 코드 무변경, 신규 probe만, lap737과 동일
  판단). 크래시 0, `source_unchanged` 3/3. **다음 work가 V 정확 대상·I 국가·미니맵 주소 실측을 이어간다.**
  상세 `../history/laps/20260929_lap758_work_g5_ability_v_identified_minimap_provenance.md`.
- [ ] **2026-09-29 lap757 work tier 정보제공(middle 독립 검수 아님): G5 v10 항목(1) 보완 측정
  — 중간값(25/35) 미지정 선택·부대(Ctrl+1) 혼합 save/load.** 신규
  `tools/g5_v10_partial_and_squad_saveload_probe.py`. Round A(25기, 부대없음) 저장/로드
  count/슬롯 25/25 정확 일치 PASS. Round B(부대1=15기 Ctrl+1 지정 후 겹치지 않는 별도 35기를
  부대 재지정 없이 라이브 선택해 저장) 로드 후 라이브35/35 정확 일치 PASS + "1" 소환 시 원부대1
  15명 정확 복원 PASS(라이브 선택 사이드카와 원본 엔진 부대 저장소 간 간섭 없음 확인). 크래시0,
  `source_unchanged`·`cleanup.ok`. `make check` 1131 passed·5 skipped(757.84s), `SAFETY_PASS`.
  **v10 "핵심 회귀 1회"(드래그4종·공격·그룹·사망후호출·R3·Shift)는 work 판단으로 이 lap에서
  미착수** — v9→v10 diff가 저장/로드 hook 2곳+cave로 pytest 범위 고정돼 있고 v9가 이미 A~H
  2단 통과했다는 근거; middle이 필요하다고 판단하면 다음 work lap에서 보강. **middle이 (1)
  전체(lap756 50기+이 lap 25/35/부대혼합)를 독립 재검수할 차례, 또는 work가 ②(미니맵/능력v)로
  진행.** 상세 `../history/laps/20260929_lap757_work_g5_v10_partial_squad_saveload_pass.md`.
- [ ] **2026-09-29 lap756 work tier 정보제공(middle 독립 검수 아님): G5 v10 항목(1) save/load
  전부50 복원 구현+런타임 3-way PASS.** 후보 v10 `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`
  (v9 + hook 2곳: 각 save/load 루프의 진짜 마지막 block-transfer 호출 `0x00440F1E`/`0x004412EE`에
  magic+전체50배열 트레일러). 자체 save→load count 50/50 전부 복원, 원본EXE↔v10 양방향 크래시0(원본→v10:
  레거시20 정상, v10→원본: 앞20+21~50zero 기존과 동일). `make check` 1131 passed·5 skipped, `SAFETY_PASS`.
  **middle이 (1)을 독립 재검수할 차례**(v10 재빌드 SHA·hook이 정말 마지막 호출인지·scratch 위치
  재확인). 상세 `../history/laps/20260929_lap756_work_g5_v10_saveload_full50_restore_confirmed.md`.
