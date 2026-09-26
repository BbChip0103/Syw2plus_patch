# 2026-09-24 | lap 548 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, strategy(상위 방향). INBOX 2026-09-23 strategy 모델 교체 지시(Fable→Opus5.5)에 따름.
- 가설 / 사용자 관찰: 사용자 2026-09-24 03:15 **(라) 이동 후 공격** 선택. 가설: W35~W41R 교전 불능의 기전은 공격 명령의 추격 포기(`0x472042`, 셀 경계 `r`>0 두 번)인데,
  원본 이동 명령(kind 3)은 그 계수가 없어(N204, 정적) 인접까지 걸어간 뒤 op8을 걸면 교전이 성립한다.
- 예상 PASS / FAIL 조건: 이 회차는 판정 문서 회차다. W42 라벨 표(`ENGAGED_2STAGE`/`NO_ARRIVAL`/`NO_ENGAGE_ADJ`/`PROBE_VOID`/`BLOCKED`)와 분기를 실행 전에 고정했다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `docs/work/active/G2_STRATEGY_W42_MOVE_THEN_ATTACK_LAP548.md`(`a49a539f…`), 이 기록,
  `docs/STATUS.md`·`docs/feedback/INBOX.md`(처리 추기)·`loop/ESCALATE_SOL` §102 추기. 제품 source·브리지·테스트·하네스 변경 0. 커밋 0(LOOP_ALLOW_COMMITS 미설정).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(lap543 사본, 읽기만).
  핀 일치: `runtime_bridge.c` `3555848d…`, 허용목록 핀 테스트 `2a8aa4f7…`, op8 계약 테스트 `0939f5b6…`, `w41_run.py` `a6ea50fb…`, `t0_positions.json` `ffdb070e…`/`064681fb…`, `w41r_run.py` `ca6ccf1a…`, `prescan.json` `0343d4fa…`.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 move_issuer_read.py`(cwd `temp/Syw2plus_patch/g2_capacity/20260924_lap548_strategy_w42/`, 2회, 산출 동일).
  `move_issuer_read.py` `62351fb3052eba33afe57486b818b371149a739b2fc73fe236e5497868eaf156`, `move_issuer_read.json` `3bad3555a0c062537e5fc83c91acb402815de3099b55e3ac8e334b0a41cd9366`,
  `pe_text.py` `34031da42793e1af0d8ce4ae3180847a6d46efcc3bd51827222d1cf6bc5870bb`(lap540 도구 복사, SRC 경로만 변경). 게임 실행 0.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **N203:** 원본 이동 명령 = `FUN_004AEDE0(uid, x, y, a4)` cdecl → `FUN_004AED20(3, uid, (y<<16)|x, tick, a4, 0)` → 큐 `0x61e36c` `FUN_0040FF90`(op8의 `0x4AEE10` kind4와 같은 큐). 호출처 44, 원본 복귀 이동 `0x48bba3`은 a4=1.
    시그니처 `8B 44 24 10 8B 0D 78 5C 9E 00 8B 54`. `0x4AEDE0`/`0x4AED20`/`0x40C390` 창 원본=후보(`windows_identical=true`).
  - **N204(정적):** case 3 `0x48e6fd` → `FUN_0040C390`: `FUN_0040B7E0(4,0)`==1일 때만 CmdStop. 막힘·경로 없음(0)은 정지시키지 않는다. 공격 추격 포기 계수 없음. 조기 정지 경로 `+0x682`≥2는 남는다. 런타임 미확인.
  - 교차: CmdStop `0x4AEDA0` 호출처 127 = lap537 발행자 127과 같다.
  - 판정: P1 (라)=W42 1회 · P2 기준 불변 · P3 게임 최대 1회(첫 op9 전 하네스 결함만 +1) · P4 다음 회차 실행 필수 · P5 전열 (0,1)(4,5) + 띠 (2,3)(6,7).
  - `checks/safety.sh check`·`checks/context_limits.py`: 아래 STATUS 검증 상태에 기록.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: N204는 정적 판독이라 이동 중 조기 정지(`+0x682`)·다른 유닛과의 충돌 우회는 미확인이다(W42가 `move_stop_early`로 잰다).
  a4 인자의 의미는 미확인이다(원본 복귀 이동과 같은 1 사용). op9 추가는 source 변경이라 전체 `make check`와 middle의 source 재검수가 필요하다.
  사용자 결정은 (라) 경로 선택까지이며 G2 합격·3단 승인 아님. 미결: Q9·Q7-B·"8인" 정의.
- 다음 한 가지: work(Sonnet5) W42 구현(op9+계약 테스트)과 게임 1회 foreground 실행(카드 §2·§5). 실행 없이 끝나면 STOP·사용자 보고.
