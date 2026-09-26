# 2026-09-23 | lap536 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 지정 역할 work.
  (세션 모델 라우팅: work=Sonnet5. `docs/work/active/G2_STRATEGY_W38_REVERT_ATTRIBUTION_LAP535.md` §2 실행.)
- 가설 / 사용자 관찰: lap535 strategy가 채택한 J2 — S1 교전에서 op8(`FUN_00415480`)로 승격된
  소스 유닛의 `+0x290`(cmd) 필드가 짧은 시간 안에 되돌아가는(N196) 원인이 되는 **런타임 writer pc**를
  gdb 하드웨어 write watchpoint로 직접 잡는다. W18(lap438) 선례와 같은 도구.
- 예상 PASS / FAIL 조건: 카드 §2 판정식(사전 고정) — `M0`(WA에 new==4 트리거 존재) 실패 시
  `BLOCKED`; `WA`에 4→(≠4) 트리거가 없으면 `NO_REVERT`; 있으면 그 함수를 원본·후보 바이트 대조해
  `REVERT_CANDIDATE_DIFF`(차이 있고 알려진 fixup 밖) 또는 `REVERT_ORIGINAL_LOGIC`(차이 없거나 전부
  알려진 fixup).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **repo 파일 변경 0**(비문서·문서 모두).
  하네스는 전량 `temp/Syw2plus_patch/g2_capacity/20260923_lap536_w39_revert_watch/`에만 생성
  (`w39_run.py`, W38에서 복사한 뒤 H10~H13만 추가, SHA는 최종본 기준 새로 계산됨 — 복사 직후
  원본 W38 SHA `40882756...0364aa`와 바이트 동일 확인 후 수정 시작).
  게이트 3파일은 손대지 않았고 source 변경이 없어 `make check` 전체는 생략했다(N22, 2026-09-20 lap410
  규칙 — 이번 회차 source를 바꾸지 않았음을 여기 명시). 대신 `checks/safety.sh check`(`SAFETY_PASS`)와
  표적 테스트 2개(`test_g2_runtime_bridge_fixture_type_allowlist_pin.py`,
  `test_g2_runtime_bridge_op8_order_engagement_contract.py`, 14 passed)를 실행 전에 돌렸다. 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 불변 확인),
  후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(lap524 pin과 일치).
  격리 Wine prefix/Xvfb `:6536`(새 display), 활성 8인(seed42 커스텀 체인), 지도 100×100.
  fixture: op7 자원만 → 시딩 op5/op6 type5×100·type7×25·type2×60·type46×20(순서 W37 N187 수정판)
  → 전원 `used`=4,950. 허용목록 {5,7,46,2} 그대로, AI/생산/건설/가드 변경 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 w39_run.py`(foreground, 45분 상자 중 실제 소요 약
  93초: 22:14:46 빌드 시작 → 22:16:19 완료). 산출물
  `temp/Syw2plus_patch/g2_capacity/20260923_lap536_w39_revert_watch/`
  (`run_summary.json`, `triggers.jsonl`, `trace.jsonl`, `waves.jsonl`, `t0_positions.json`,
  `h13_report.json`, `w39_orchestrator.log`, `watch.gdb.out`, `watch_summary.json`,
  `candidate.bin`/`original.bin` H13용 스냅샷). `w39_run.py` 최종 SHA는 산출물 폴더에 함께 있음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - H11 예측 A(owner0 첫 소스)=3800, B(owner3 첫 소스)=3185 — **W38과 완전히 동일**(결정성 재확인).
    실제 파동에서도 owner0 첫 op8 src=3800, owner3 첫 op8 src=3185로 하네스 불변식 통과.
  - `checks/safety.sh check` `SAFETY_PASS`, 표적 14 passed, 원본 불변, 잔류 프로세스 0,
    A5 무결성(초과5000·live/count 불일치·tick역행·범위이탈) 전부 0.
  - gdb hw watchpoint 3/3 무장(`hw_watchpoint_count=3`), op8 발행 **전** 무장 완료(22:15:51,
    첫 op8은 22:15:51 직후). 트리거 총 26건(WA=6, WB=6, WC=14). 상세 시퀀스(tick, pc):
    - **A(owner0, slot3800):** t1089 `1→4`(pc `0x40c8a9`, op8 승격) → t1105 `4→2`(pc **`0x40d544`**,
      = `E_rev`) → t1105 `2→1`(pc `0x48e44c`) → t1107 `1→3`(pc `0x40c766`) → t1114 `3→2`(pc `0x40d544`)
      → t1114 `2→1`(pc `0x48e44c`). 승격 후 철회까지 **16 tick**(N196 "≤25 tick" 범위 재확인).
    - **B(owner3, slot3185):** t1121 `1→4`(pc `0x40c8a9`) → **163 tick 동안 무변화** → t1284 `4→2`
      (pc `0x40d544`) → `2→1`(`0x48e44c`) → t1286 `1→3`(`0x40c766`) → t1473 `3→2`→`2→1`.
      B의 x좌표(`WC`)는 t1151~1221에 56→63으로 7칸 이동했다가 t1382~1447에 63→56으로 원위치
      (N197 "이동 뒤 복귀"의 직접 관측). 이동 창(1151~1221)은 첫 승격(1121)과 첫 cmd 철회(1284)
      **사이**에 있다 — 유닛이 실제로 걸어갔다가 되돌아온 뒤에 cmd도 idle로 수렴한다.
  - **H13 바이트 대조:** `E_rev` pc=`0x40d544`. 5개 anchor(pc-0x400~pc-0x40) 정방향 디스어셈블이
    모두 같은 명령 경계에 수렴(`pc_is_common_instruction_boundary`=true). 창
    `[0x40d144, 0x40d644]`(1280B, 여러 완결 함수/분기 포함) 안에서 원본·후보 **바이트 차이 0개**
    (`diff_byte_count=0`, `known_fixup_va_count`=28곳은 이 창에 없음). 즉 이 철회 경로는 **후보
    빌드가 건드리지 않은 원본 코드**다.
  - **자기 라벨: `REVERT_ORIGINAL_LOGIC`**(카드 §2 판정식, harness_ok=true, M0=true,
    E_rev 확정, H13 diff=0). `verdict=PROBE_OK`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이 라벨은 **work 자기판정**이며 다음 middle의
  원시 재계산(트리거 26건 전량·trace.jsonl·h13_report.json)이 아직 없다. 남은 위험: `E_rev` 직전
  분기 조건 자체(왜 4/3→2로 떨어지는지, 어떤 플래그를 보는지)는 아직 정적으로 안 읽었다 — 그것이
  카드 §3 `REVERT_ORIGINAL_LOGIC` 행이 지정한 middle의 다음 작업이다. `0x48e44c`(2→1)과 `0x40c766`
  (1→3, 반복 재발행원)의 정체도 안 읽었다(참고 데이터로만 trace에 보존). 144k는 닫힌 채, AI/생산
  로직 변경 0.
- 다음 한 가지: 카드 §3 표(`REVERT_ORIGINAL_LOGIC` 행) 그대로 — **middle(Opus5.5)**이
  `triggers.jsonl`/`trace.jsonl`/`h13_report.json`을 원시로 재계산해 이 라벨을 검수하고,
  `E_rev`(pc `0x40d544`, 정확한 store는 `0x40d53d`) 직전 분기 조건 하나만 정적으로 읽는다
  (문서 1회, 60분 또는 후보 2개 반증 뒤 `BLOCKED`). 조건이 fixture로 바꿀 수 있는 것이면 그 fixture
  변경 + §4 H7' 대조로 work 1회를 예약한다. strategy 재판정 없이 §3 표대로 진행.
