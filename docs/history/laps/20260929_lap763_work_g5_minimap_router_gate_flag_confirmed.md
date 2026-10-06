# 2026-09-29 | lap 763 | 목표 G5 (사용자 항목(2), 미니맵 — lap762 3-필터 브레이크포인트 지시 처리)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, high effort; 지정 역할
  work(실무) — 승인된 범위의 실측/코드/실행만 수행, milestone 판정이나 G5 종료 선언은 하지 않음.
- 가설 / 사용자 관찰: 2026-09-29 12:57 운영자 판정(lap762, "미니맵 1 lap 연장") — 필터 3지점
  (`0x41e332` 버튼타입, `0x41e365` 좌표 sentinel, `0x41e43d call 0x41c450` 게이트)에 개별
  브레이크포인트로 어느 분기에서 클릭이 떨어지는지 확정. 격리 환경 탓(창 포커스/미니맵 표시
  플래그 요구)이면 그 플래그를 브리지로 켜서 원본 미니맵 우클릭 이동을 성립시킨 뒤 원본20/v10 50
  paired. 성립 못 하면 UNKNOWN 확정하고 middle로 넘어간다(추가 연장 없음).
- 예상 PASS / FAIL 조건: 세 지점 중 실제 게이트를 objdump 정적 분석 + gdb 레지스터 캡처로 확정하면
  최소 성공(코드 위치를 넘어 "왜 막히는지"까지 새 정보 확보). 게이트가 격리 환경/포커스 문제로
  드러나고 강제로 열어 `FUN_004516A0`이 호출되면 추가 성공(그 다음 명령효과 paired는 다음 lap으로
  이월 가능). 세 지점 모두 결정적 원인을 못 찾으면 UNKNOWN 확정 후 middle 이관.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/g5_minimap_hittest_entry_trace.py`
  (SHA256 `b34ac491352c8c397d181ad97bfebca548fcc7b568f0ae0067e5db5dfed428ec`, 브레이크포인트
  4개 추가: `router_button_type_filter_0x41e332`, `router_coord_sentinel_filter_0x41e365`,
  `router_gate_entry_0x41c450`, `router_gate_return_check_0x41e442`, 기존 5개 무변경),
  `tools/g5_minimap_click_hittest_probe.py`(SHA256
  `0f3d9cd21407c82e21ccf6a3d13e490a204ae322047e028103c83933fb7039cc`, 신규 `--force-gate-flag`
  진단 옵션 — ps==3 도달 직후 `runtime_driver.write()`로 `0x97597c`에 1을 씀, 기존 실행 경로는
  플래그 없으면 완전히 동일), `analysis/memory_maps/g5_minimap_router_gate_lap763.md`(신규,
  정적+실측 근거) — 전부 조사용 read-only/진단 전용 도구·문서. 제품 코드(EXE 패치) 0 변경.
  uncommitted(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(2회 실행 전후
  `source_unchanged=true`). 후보 없음(순정 UI/입력 경로 조사, G5 선택 상한 relocate와 무관).
  격리 Wine prefix/Xvfb 1600x1200, 솔로 로비 새 게임 각 1회, fixture 유닛 스폰 없음(이 lap은
  게이트 도달성만 측정, 명령효과는 다음 lap 과제로 명시).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 정적 확인은 기존 `/tmp/full_disasm_lap762.txt`(lap762가
  만든 전수 objdump, 재사용) + `grep`/`sed`로 라우터 코드(`0x41e260`-`0x41e4c1`), 게이트 함수
  `0x41c450`, setter/xref(`0x97597c`, `0x975914`, `0x632d42`, `0xb63fc4`, `0xb631ec`) 재확인.
  실행 1(3-filter 브레이크포인트, 강제 플래그 없음):
  `PYTHONPATH=. .venv/bin/python -m tools.g5_minimap_click_hittest_probe --runtime-root
  local/runtime/g5-lap763-minimap-router-filter --artifact-root
  /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260929_lap763_minimap_router_filter`
  (COMPLETE, `probe-result.json` SHA256
  `3d6f7e85977cd6c495b63d5390818ccf9421bdaafc8a6b72960e059161d7386a`). 실행 2(`--force-gate-flag`):
  `--runtime-root local/runtime/g5-lap763-minimap-gate-forced --artifact-root
  .../20260929_lap763_minimap_gate_forced` (COMPLETE, `probe-result.json` SHA256
  `5a2ea2cc77ac302d04c340de4ab91529935da1c7b4cf6e342ed17d9db4fd4ceb`). 두 실행 모두 게임 사본
  (각 1.4GB→cleanup 후 581MB)은 실행 직후 `game/` 서브폴더만 삭제(output/manifest/prefix/log 보존).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **정적: 세 필터 지점의 실제 역할을 확정.** `0x41e332`(버튼타입)와 `0x41e365`(좌표 sentinel)는
    라우터 내부에서 화면 가장자리 스크롤-커서 아이콘 코드를 계산하는 두 갈래일 뿐이고, 두 갈래
    모두 무조건 다음 명령(`call 0x437510`)으로 수렴 — `FUN_004516A0` 호출 여부와 무관함을
    디스어셈블로 확인. **유일한 실제 게이트는 `0x41e43d`의 `call 0x41c450`**
    (`test eax,eax; je 0x41e4c1`, 0이면 `FUN_004516A0` 자체를 건너뛰고 폴백 뷰포트 히트테스트로
    직행).
  - **실측(실행1, gdb 9-breakpoint): 게이트 호출(`0x41e442` 반환값 체크) 9430회 중 관측된 전부
    (80건 캡, 포함 전수 일치)에서 eax=0x0.** `FUN_004516A0` 여전히 0회. `router_button_type_filter
    _0x41e332`는 8회, `router_coord_sentinel_filter_0x41e365`는 9430회(라우터 tick과 거의 동일) —
    정적 예측과 정확히 일치, 둘 다 게이트가 아님을 실측으로도 확인.
  - **정적: 게이트 함수 `0x41c450` 자체의 3-way OR 조건 확정 및 setter 추적.** `0x97597c`(세
    조건 중 하나)의 유일한 두 setter는 새 게임 초기화 함수 내부(`0x41b9c0`/`0x41bc4f`가 호출하는
    `0x4a3060`과 같은 코드 영역, lap753/754 H-NEWGAME-INIT과 동일 새게임 초기화 경로)에 있고,
    **`WORD PTR ds:0x975914 == 3`일 때만 `0x97597c=1`을 쓴다.** `0x975914`는 로비 설정 전역
    `0x632d42`에서 새 게임 시작 시 그대로 복사되며, `0x632d42`는 로비 다이얼로그 접근자
    (`call 0x4ced40`, `this=0x1065d10`)의 반환값 — **렌더링/포커스/DirectDraw 상태가 아니라
    로비 UI의 "게임 종류" 계열 선택값**임을 확정.
  - **실측(실행2, `--force-gate-flag`로 `0x97597c`를 격리 사본 안에서 진단 write로 1로 강제):
    `FUN_004516A0` 호출 수 0 → 6232회(성공 4195, 실패 2037)로 급증.** 이는 미니맵 렌더/좌표
    서브시스템이 죽은 게 아니라 **이 게이트 플래그 하나가 잠가놓고 있었을 뿐**임을 직접 실증한다
    (이전 세션들의 "완전히 죽어있다"는 결론을 더 좁고 더 구체적으로 뒤집는 lap762의 LUT 50%
    베이킹 발견과 정합적으로 이어짐).
  - 크래시 0, `alive_at_end=true` 2/2, `source_unchanged=true` 2/2, `cleanup.ok=true` 2/2.
    `ruff check`/`python -m compileall` 신규·변경 파일 2개 PASS, `checks/safety.sh check` →
    `SAFETY_PASS`, `checks/context_limits.py` → `CONTEXT_PASS`. 제품 코드/EXE 0 변경이므로
    lap758~762와 동일 판단으로 전체 `make check`(pytest 스위트)는 이번 lap에서 생략(신규/변경
    진단 도구는 기존 pytest 대상 경로에 대응 테스트가 없는 read-only/진단전용 조사 스크립트 계열).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(제품 코드 0 변경, 순정 EXE만 실행,
  `source_unchanged=true` 2/2). 남은 위험: (1) 이번 lap은 게이트를 강제로 열면 히트테스트 함수가
  "도달 가능"함만 실증했다 — 유닛을 선택한 상태로 실제 미니맵 우클릭이 그 좌표로 이동 명령을
  내는지(`pending_xy` 변화)는 아직 fixture 없이 측정하지 않았다(다음 work 과제로 명시). (2)
  `0x632d42`가 정확히 어떤 로비 UI 위젯에 대응하는지, `game_type==3`이 사람이 실제로 고를 수 있는
  정상 옵션인지, 아니면 우리 자동화 로비 클릭 시퀀스가 그 옵션을 우회하고 있는 것인지는 미확인 —
  "원본에서도 항상 이 상태"라는 결론과 "우리 로비 자동화가 잘못된 옵션을 고른다"는 결론이 갈리는
  분기점이라 다음 probe의 전제조건이다. (3) `0xb631ec`/모드-테이블(`0x959af6`)의 writer는 이
  코드범위(0x400000~0x800000)에 없음 — 비차단 갭(게이트가 이미 `0x97597c` 경로로 열렸으므로 이
  lap 결론에 영향 없음). 독립 검수 요청 없음(work tier, 정보 제공용) — 이 lap 자체는 12:37/12:57
  지시가 요구한 "어느 분기에서 떨어지는지 확정"과 "성립하면 강제로 열어보라"는 두 조항을 모두
  실측으로 충족했으므로, 12:37 지시의 "성립하지 않으면 UNKNOWN 확정" 조항은 적용되지 않는다 —
  **성립했다(게이트를 강제로 열자 히트테스트가 실제로 호출됨)**, UNKNOWN을 그대로 재확정하지 않고
  middle/운영자가 다음 단계(명령효과 paired 측정 우선순위)를 정하도록 넘긴다.
- 다음 한 가지: 다음 work가 (a) fixture 유닛을 스폰·선택한 뒤 `--force-gate-flag` + 실제 베이킹된
  (비-0xFF) 미니맵 픽셀 우클릭으로 원본20/v10 50 명령효과(`pending_xy`) paired를 측정해 사용자
  항목(2) 미니맵을 완전히 닫거나, (b) 원본 로비 UI에서 `0x632d42`/`game_type` 옵션이 사람이 실제로
  고를 수 있는 경로인지 좌표 스윕/캡처로 먼저 확인한다. 그 다음 middle이 사용자 항목(1)+(2)와
  v10 전체 재검수(v10 핵심 회귀 1회 포함)를 진행한다.
