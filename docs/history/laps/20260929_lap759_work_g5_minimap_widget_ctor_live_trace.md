# 2026-09-29 | lap 759 | 목표 G5 (사용자 항목(2), 미니맵 하위 질문 ① — 서브시스템 활성 여부)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, high effort; 지정 역할 work(실무) —
  승인된 범위의 실측/코드/실행만 수행, milestone 판정이나 G5 종료 선언은 하지 않음.
- 가설 / 사용자 관찰: lap758이 다음 후보로 제안한 (c) — 카페 커뮤니티 참고 주소 `0x451C12`/`0x451C19`
  (미니맵 X/Y)·`0x4F2E8B`(점 IFF)를 격리 실행 중 실시간으로 읽어 "값이 초기화되는지(서브시스템이
  살아있는지)"를 확인하라는 핸드오프. 이 lap의 가설: 착수 전 objdump 정적 확인으로 그 전제가 맞는지
  먼저 검증한다(정적 상수 바이트라면 실시간 읽기 자체가 무의미하므로 "긴 정적 조사"가 아니라 실행
  낭비를 막는 최소 선행 확인). 확인 결과에 따라 실제로 유의미한 실행 증거(라이브 breakpoint 진입
  카운트)로 전환한다.
- 예상 PASS / FAIL 조건: (정적) 두 주소가 코드 섹션의 `mov [reg+off],imm32` 명령 피연산자 내부면
  "읽기 무의미" 확정, 데이터 섹션의 독립 변수면 "읽기 유의미"로 원래 계획 유지. (실행) 새로 찾은 진짜
  타겟 함수가 격리 세션(프로세스 시작→메뉴→솔로 로비→인게임→미니맵 클릭/키) 동안 최소 1회 호출되면
  "위젯 초기화 코드는 살아있음"(PASS), 0회면 "이 경로 자체가 죽어있음"이라는 훨씬 강한 BLOCKED 근거.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `tools/g5_minimap_init_entry_trace.py`(SHA256
  `1eac9f74b19505a5f88934e22288228343620f04724da8f6754969febb1db095`, gdb 배치 스크립트,
  non-invasive 진입 카운트만),
  `tools/g5_minimap_init_breakpoint_probe.py`(SHA256
  `86d8e3aa41d5f77fc3655c14729c736c0a0b794db482b4c4a47fafac7537332d`, 구동 하네스),
  `analysis/memory_maps/g5_minimap_widget_ctor_lap759.md`(정적+실측 주소 근거) — 전부 조사용
  read-only 도구/문서, 제품 코드(EXE 패치) 0 변경. uncommitted(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 `source_unchanged=true`).
  후보 없음(원본만, 순정 EXE 읽기 전용 조사 — 이 코드 경로는 G5 선택 상한 relocate와 무관하므로
  candidate 별도 실행 불필요). 격리 Wine prefix/Xvfb 1600x1200, 솔로 로비 새 게임 1회, 별도 fixture
  스폰 없음(op=5 브릿지 미사용, 순정 진단 DLL만).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 정적 확인은 `objdump -d -M intel --start-address=0x400000
  --stop-address=0x800000 "[ESL]Syw2plus/[HQ]Syw2plus 2002.exe"`(전수 저장 `/tmp/full_disasm.txt`,
  311563줄) + `grep "call.*451c10"`로 단일 호출자 확정. 실행:
  `PYTHONPATH=. .venv/bin/python -m tools.g5_minimap_init_breakpoint_probe --runtime-root
  local/runtime/lap759_minimap_init_trace --artifact-root
  /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260929_lap759_minimap_init_trace`
  (1회, 재시도 없이 COMPLETE). 최종 `probe-result.json` SHA256
  `52fc85ba064c50fb80b2c68559a2587bf893f3b6d616b425c370c2884430a065`. gdb 이벤트 로그
  `gdb_control/entry-events.jsonl`(2건). 캡처: `00-in-game.png`, `01-after-minimap-interactions.png`.
  게임 사본(~810MB)은 실행 직후 삭제(output/manifest/prefix/log는
  `local/runtime/lap759_minimap_init_trace/`에 보존).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **정적: 전제 반증(FALSIFIED, 예상대로).** `0x451C10`은 14바이트 leaf 함수
    (`mov [ecx],0x0` / `mov [ecx+0x4],0x1fd` / `ret`) 이며, `0x451C12`/`0x451C19`는 그 두
    `imm32` 피연산자 내부 바이트다 — 실행 여부와 무관하게 항상 `0x00000000`/`0x000001fd`.
    실시간으로 읽어도 서브시스템 활성 여부를 알 수 없다(lap758 핸드오프의 전제 오류를 실행 전에
    발견해 헛수고를 막음). 전수 xref: 직접 호출자 **`0x451138` 단 한 곳**뿐(0x400000~0x800000 전체
    스캔), `0x451130`에서 시작하는 큰(약 0x1c000바이트) 구조체 초기화 함수 내부. 호출 직전 `ecx`가
    **고정 정적 주소 `0x639350`**(힙 아님)로 세팅됨을 확인.
  - **실행: PASS(위젯 초기화 경로는 이 환경에서 살아있음).** 프로세스 시작 직후(메인 메뉴 도달
    전)부터 non-invasive gdb breakpoint를 걸고 메뉴→솔로 로비→인게임→미니맵 좌/우클릭+m/Shift+M/Tab
    키까지 전체 세션을 관찰한 결과, `widget_ctor_FUN_00451130`/`xy_writer_FUN_00451C10` **둘 다
    정확히 1회씩 호출됨**. 호출 시 `ecx`=`esi`=`0x639350`(정적 분석과 일치), `widget_ctor`의 복귀
    주소는 `0x41b59f` — 그 주변(`0x41b590`~)이 `ecx=0x892410`으로 `0x4a4090`을 호출하는, **기존
    G5 새게임초기화(H-NEWGAME-INIT, lap752~754) 조사와 동일한 코드 영역**이라 이 위젯 초기화가
    "솔로 로비→인게임 전환"(새 게임 시작) 경로의 일부로 1회 실행됨을 확인했다(프로세스 시작이나
    미니맵 토글마다 반복되는 것이 아님).
  - **새 결론(2026-09-29 10:35 지시 ①에 대한 답):** 미니맵 위젯은 "완전 비활성"이 아니라
    **구조체가 실제로 생성/초기화된다**(X=0, Y=509를 정적 주소 `0x639350`에 실측 확인) — lap758의
    독립 negative 증거(참고 저장소도 렌더 함수를 못 찾음)와 모순되지 않는다. "위젯 존재/초기화"와
    "렌더 진입점 발견"은 별개 질문이며, 이번 lap은 전자만 답했다.
  - 크래시 0, `alive_at_end=true`, `trace_armed=true`, `reached_ps9`/`reached_ps3=true`,
    `cleanup.ok=true`, `source_unchanged=true`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(제품 코드 0 변경, 순정 EXE만 실행,
  `source_unchanged=true`). 남은 위험: (1) `0x639350`이 그 뒤로도 살아있는 live state인지(값이
  변하는지)는 아직 미확인 — 이번 lap은 "한 번 초기화됨"만 확인했다. (2) 렌더 함수 자체는 여전히
  미발견(참고 저장소 독립 negative와 함께, lap677/710 UI 무반응 관측 그대로 유효) — "초기화됨"이
  "렌더됨"을 뜻하지 않는다. (3) "V" 정확 대상·"I" 국가 확인(lap758 남은 항목 a/b)은 이번 lap에서
  미착수. middle 독립 검수 요청 없음(work tier, 정보 제공용). 사용자 승인 대기 없음.
- 다음 한 가지: (①-계속) `0x639350`(X)/`0x639354`(Y)를 게임 진행 중 다른 시점(카메라 이동, 미니맵
  클릭 시도 전후)에 실시간으로 재읽어 값이 (0,509)에서 변하는지 확인 — 변하면 "갱신은 되는데 렌더만
  실패", 안 변하면 "초기화 후 방치"로 더 좁힐 수 있다. 또는 (a) "V"(수확) 정확 발주 대상 특정, (b)
  다른 국가로 "I" 버튼 확인으로 전환해도 된다(lap758이 남긴 두 항목, 아직 미착수).
