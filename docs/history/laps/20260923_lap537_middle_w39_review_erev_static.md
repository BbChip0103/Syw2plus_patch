# 2026-09-23 | lap537 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 지정 역할 middle(진단·계획·확인).
  사양 `docs/work/active/G2_STRATEGY_W38_REVERT_ATTRIBUTION_LAP535.md` §3 `REVERT_ORIGINAL_LOGIC` 행.
- 가설 / 사용자 관찰: (1) lap536 W39 자기 라벨 `REVERT_ORIGINAL_LOGIC`이 원시로 재현되는가.
  (2) `E_rev`(store `0x40d53d`, pc `0x40d544`) 바로 앞 분기 조건이 fixture로 바꿀 수 있는 것인가.
- 예상 PASS / FAIL 조건: (1) 트리거 원시에서 M0 참, `WA` 첫 4→(≠4) pc가 `0x40d544`, 그 함수 창의 원본↔후보 차이가
  0이거나 전부 풀/존재배열 fixup이면 라벨 일치. (2) 카드 §3: 문서 1회, 60분 또는 후보 2개 반증 뒤 `BLOCKED`.
  조건이 fixture로 바꿀 수 있으면 fixture 변경 + H7' work 1회 예약.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): repo 비문서 변경 0. 문서만: 이 파일, `docs/STATUS.md`,
  `docs/feedback/INBOX.md`(처리 한 줄), `loop/ESCALATE_SOL` §91, STATUS 압축 전문
  `docs/history/20260923_status_lap537_precompaction.md`. 커밋 0(uncommitted).
  재계산 도구는 temp에만: `temp/Syw2plus_patch/g2_capacity/20260923_lap537_middle_w39_review/`
  (`recompute_w39.py` `f4405a3f…`, `recompute_w39.json` `02b01e57…`, `diff_windows.py` `2ac4a6cf…`,
  `diff_windows.json` `fd2b17e3…`, `pe_disasm.py` `aefd7b32…`, `fun_40c640_orig.asm` `b2d5c8a3…`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 exe
  `Syw2plus_re/Syw2plus/syw2plus_original.exe` `b56986e0…c9c08a8ac`(읽기만, W39 스냅샷 `original.bin`과 바이트 동일),
  후보 `candidate.bin` `a10024de…bb2d68`(lap524 핀 일치). 게임 실행 0. fixture는 W39 그대로(재실행 없음).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 recompute_w39.py`, `python3 diff_windows.py`, `python3 pe_disasm.py <va> <va>`.
  입력 원시 SHA: `triggers.jsonl` `8f4735fa…`, `trace.jsonl` `7017daa0…`. `run_summary.json`·`h13_report.json`은 참조하지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **(1) 라벨 재현 PASS.** 트리거 26건(WA6·WB6·WC14), 전이·pc 분포가 lap536 기록과 일치한다. M0 참(t1089 `1→4` @`0x40c8a9`).
    `E_rev` = t1105 `4→2` @`0x40d544`, 레지스터 eax=2, `edi−esi`=`0x384`. 승격→철회 A 16 tick, B 163 tick.
    `E_x` = `0x40bced`. `NO_REVERT` 아님. 4/3→2 전이 4건이 전부 `0x40d544`다.
    바이트 대조를 넓혔다: H13 창 0, `FUN_00412540` 0, `FUN_004AEC60..4AEE0C` 0, `FUN_0040C390` 0, `0x48e44c`±0x80 0.
    창 밖 차이는 `FUN_0040C640` 2명령·`FUN_0040FF90` 1명령·이동 실행부 6명령이다. **전부 유닛 풀 기준주소 재배치**
    (`0x66b790+off` → `0x108c000+off`, off 동일)다 ⇒ `REVERT_ORIGINAL_LOGIC` 일치이며 근거가 더 강해졌다.
    카드의 `E_mv` 정의(WB 4→3 또는 3→1)는 해당 전이가 없어 null이다. B의 실제 전이는 4→2→1→3→2→1이다(판정 영향 없음).
  - **(2) 정적 판독: 직전 분기 = fixture 조건 아님 ⇒ `BLOCKED(static fan-out)`.**
    - `0x40d53d`는 `FUN_0040C640`(대기 명령 적용) 안에 있다. `+0x384` word=대기 cmd, `+0x386` byte=flag,
      `+0x388`=목표 xy(x|y<<16), `+0x38c`=목표 uid다(trace: A `+0x388`=0x00080022=(34,8)=목표 위치, `+0x38c`=921139=목표 uid).
    - 진입 조건: 대기 cmd≠1, `+0x31d`≠1, (`+0x370`==0 또는 대기 cmd==2), 우선순위표 `0x9e2f40`(stride 24, BSS라 런타임 값) 게이트.
      게이트는 우선순위가 같고 flag bit2가 없고 bit4가 있을 때만 대기 cmd를 버린다. 그 밖에는 적용한다.
    - 스위치(`0x40e74c` 인덱스 → `0x40e720` 표): cmd2 → `0x40c727` → `+0x292`=0 → `call 0x40c600` → `call 0x412700` →
      `jmp 0x40d53a` → `mov [esi+0x290], [edi]`. **cmd2 경로에는 조건 분기가 하나도 없다.** 철회는 대기 cmd 2(정지)의 커밋이다.
    - cmd2를 `+0x384`에 쓰는 곳: `FUN_00412540`(SetPending, store `0x4125da`, 인자 12바이트 명령+2) ← `FUN_0040FF90` ←
      `FUN_004AED20` ← `FUN_004AEDA0`(**CmdStop**: `push 2`). `FUN_004AEDA0` 직접 호출 지점은 선형 디스어셈블 기준 **127곳**이다(절대주소 참조 0).
      cmd3(이동) 래퍼 `FUN_004AEDE0` 호출은 44곳이다. `+0x384` 직접 쓰기는 `0x4125da`·`0x4522ae`·`0x45523f`뿐이다.
    - 후보 2개를 읽었다. (c1) `FUN_0040C390`: `FUN_0040B7E0(4,0)`==1이면 CmdStop(`+0x29c`,1). (c2) 이동 실행 함수
      `0x40a4xx~0x40b276`: 10개 분기(`0x40a485~0x40a4a8` 좌표 경계 비교 포함)가 `0x40b276` CmdStop(`+0x29c`,1)으로 간다.
      둘 다 정적으로 확증도 반증도 못 했다. A는 x=37 그대로(이동 0)라 c1 "도착 정지"와는 잘 맞지 않는다.
    - 관측 사실(트레이스): B는 (56,17)→(58,20)→(63,19)로 움직였다. 목표 (61,12)와의 Chebyshev 거리는 5~8이었고 인접하지 못했다.
      정지 뒤 cmd3으로 **출발점 (56,17)에 정확히 복귀**했다. A도 정지 7 tick 뒤 cmd3을 받았다.
      출발점 복귀는 "자기 위치 귀환" 계열(소유 AI 또는 유닛 자체 귀환) 지시를 시사하지만, 발행자는 **미확정**이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 게임실행0·source변경0·커밋0, 원본 불변.
  카드 §3 표에는 "조건이 fixture로 바꿀 수 없음/미확정" 행이 없다 ⇒ **표 밖이라 strategy 회부**(`ESCALATE_SOL` §91).
  S1 종결 조건(lap535 J4/§5: W39+후속 work 1회 뒤 hit<2 ⇒ `BLOCKED`·사용자 보고)은 아직 발동 전이다. 후속 work가 아직 없다.
  위험: 127개 발행 지점 중 소유 AI 제어 코드가 원인이면 스크립트 교전 입력이 AI 자체 통제와 충돌한다.
  그 경우 fixture로 풀 수 없고 (ㄴ)/"8인" 정의 판단으로 넘어간다.
- 다음 한 가지: **strategy(Opus5.5)** §91 판정. middle 권고 = W40 런타임 발행자 귀속 1회(§5의 후속 work 1회로 계산).
  W39 하네스에서 watch 주소만 A·B의 `+0x384`(new word==2 필터)로 바꾸고 스택 64 DWORD를 기록한다.
  반환주소를 CmdStop 127곳의 `call+5`와 대조해 발행 함수를 특정한다. 사전 분기안은 §91에 있다.
  대안은 J4를 지금 적용해 S1을 `BLOCKED`로 닫고 사용자에게 보고하는 것이다.
