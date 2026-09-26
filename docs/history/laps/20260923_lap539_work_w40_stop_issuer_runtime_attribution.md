# 2026-09-23 | lap 539 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, work (지정: STATUS lap538 "다음 한 가지").
- 가설 / 사용자 관찰: 카드 `docs/work/active/G2_STRATEGY_W40_STOP_ISSUER_LAP538.md` §2 — op8(CmdAttack)이 수락되어도
  누군가 그 유닛에 CmdStop을 다시 걸어 철회시킨다(lap535~538 계보). 그 CmdStop/CmdMove 발행 함수를 gdb
  하드웨어 watchpoint로 런타임 귀속한다.
- 예상 PASS/FAIL 조건: 카드 §2 판정식 — `M0'`(WA'에 new==4 트리거) 확인 후 `ISSUER_SITE`(스택128 안에서
  CmdStop call+5 127곳/CmdMove call+5 44곳과 대조, esp에 가장 가까운 값)를 찾으면 `ISSUER_FOUND`,
  실패 조건별로 `BLOCKED`/`PROBE_VOID`/`NO_STOP`.
- 변경 파일 / source fingerprint / 커밋: repo 소스 변경 0(불변, N22 — 전체 `make check` 생략 근거).
  하네스만 `temp/.../20260923_lap539_w40_stop_issuer/w40_run.py`(SHA `6417a63ed3d0d459c62c968dc228828d4ecabfcf9236b81eb1a93207bf6c646e`)를
  새로 작성(W39 `w39_run.py` 파생, H14~H16만 교체). 커밋 없음(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / 활성 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (실행 전후 불변). 후보(N=4001 persistence-compat) `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
  (lap524 핀과 일치). 격리 Wine prefix, Xvfb `:6536`. 활성 8owner, 각 자원 100만/100만, cap5000.
  fixture: 허용목록 {5,7,46,2} 시딩(type5×100, type7×25, type2×60, type46×20/owner), 시딩순서 W37 확정(생산자 마지막).
  A1 used=4,950×8(전부 [4900,5000] 안), A8' 4종 보유·X≥10·최대비중 0.707 전부 PASS.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=.../Syw2plus_patch timeout 2850 python3 w40_run.py`
  (foreground 동기, 실제 소요 약 108초, 45분 상자 안). 산출물
  `temp/Syw2plus_patch/g2_capacity/20260923_lap539_w40_stop_issuer/`
  (`run_summary.json`·`triggers.jsonl`(20건)·`trace.jsonl`·`waves.jsonl`·`h16_report_{A,B,RB}.json`·
  `watch_summary.json`·`w40_orchestrator.log`). gate 3파일 SHA(`runtime_bridge.c` `3555848d…`,
  핀 테스트 `2a8aa4f7…`, op8 계약 테스트 `0939f5b6…`) §0 값과 일치 확인 후 `checks/safety.sh check` → `SAFETY_PASS`,
  표적 14 passed, 이어서 실행. W39 하네스 SHA(`w39_run.py` `64a86d21…`, `gdb_watch.py` `f8a0ba33…`)도 §0 값과 일치 확인.
- 측정값 / 판정: `verdict=PROBE_OK`, `harness_ok_for_label=True`, `M0_prime_watch_fires=True`.
  트리거 20건(WA8·WB8·WC4), `watch_stop_reason=exited`(정상 detach). H11 A=3800·B=3185 W38·W39와 완전 일치(결정성 재확인).
  A5 무결성 위반 전부 0(over5000·live/count 불일치·tick역행·used/reserved/count 범위 이탈 전부 0). 잔류 프로세스 0.
  **`I_A`·`I_B`(둘 다 발견)**: `ISSUER_SITE`가 **동일**하다 — call 명령 `0x48e83c`(call+5 `0x48e841`),
  CmdStop(uid, 1) 호출. 직접 디스어셈블 확인(원본 고정, 게임 불필요):
  ```
  48e823: cmp eax,0x1 / jne 48e844      ; call 471600 결과 게이트
  48e828: call 471af0 / test eax,eax / jne 48e844  ; 두 번째 게이트
  48e833: mov edx,[esi+0x29c]           ; uid (TRACE_FIELDS uid offset와 일치)
  48e839: push 1 / push edx / call 0x4aeda0(CmdStop) / add esp,8
  48e844: (게이트 실패 시 여기로) call 0x48bd10 ...
  ```
  이 창(`0x48e43c`~`0x48e93c`)은 후보↔원본 **바이트 차이 0개**(H16, h13_analyze 재사용) — 후보 결함 아님, 순수 원본 로직.
  UNIT_SELF c1(FUN_0040C390, 자신의 CmdStop 호출 `0x40c3ae`) 대조: **불일치**(`unit_self_c1_match=False`).
  즉 lap537의 두 후보(c1=FUN_0040C390, c2=이동실행부 0x40a4xx~0x40b276) **둘 다 아닌 제3의 발행 함수**를
  런타임으로 처음 확정했다. c2는 이번 회차 범위 밖(단일 주소로 안 좁혀져 미시도, lap537도 동일).
  **`R_B`(WB'의 정지 뒤 첫 new==3, 복귀이동)**: 발행 site call `0x48bba3`(call+5 `0x48bba8`), CmdMove(uid, [ecx+0x394], y-word) 호출.
  ```
  48bb90: mov ax,[ecx+0x394]            ; 목표 값(비-xy 필드! lap537이 말한 +0x388과 다른 +0x394)
  48bb97: mov ecx,[ecx+0x29c] / shr edx,0x10  ; uid, 그리고 어떤 dword의 상위16비트(y로 추정, 미확정)
  48bba3: push edx / push eax / push ecx / call 0x4aede0(CmdMove) / ret
  ```
  이 함수는 이 호출 하나로 끝나는 짧은 단일 블록(재사용 유틸리티로 보임, 미해석). 창(`0x48b7a3`~`0x48bca3`)은
  56바이트 차이가 있으나 **전부 14묶음×4바이트 32-bit immediate이고, 값을 직접 디코드하면 전부 이미 알려진
  풀/존재배열 재배치 패턴**이다(예: `0x66ba32→0x108c2a2`=pool+0x2a2, `0x8990c8→0x17b8658`=EXISTENCE_BASE 그대로).
  `collect_fixup_sites()` 정적 스캐너가 이 창을 인덱싱하지 않아 "알려진 fixup 밖"으로 잡혔을 뿐 —
  값 대조로는 REVERT_ORIGINAL_LOGIC과 같은 안전한 재배치이며 후보 신규 결함은 아니다(2026-09-20 lap402 D1과
  같은 계열의 **커버리지 도구 사각**으로 보이나, 이 판정 자체는 middle 몫이라 여기서는 raw 증거만 남긴다).
  **자기 라벨: `ISSUER_FOUND(A=UNCLASSIFIED_pending_middle_read,B=UNCLASSIFIED_pending_middle_read)`.**
  카드 §2가 OWNER_AI/UNIT_OTHER/UNCLASSIFIED 분류를 middle의 "한 번 읽고 정한다" 몫으로 명시 위임했으므로
  work는 분류하지 않았다(UNIT_SELF c1만 기계적으로 확인·기각). PROMPT_VOID 아님, BLOCKED 아님, NO_STOP 아님.
- 회귀/남은 위험/독립 검수: middle 독립 재계산 아직 없음(다음 회차). 이번 lap이 새로 도입한
  `find_calls_in_range`/`resolve_issuer`/`compute_w40_label`은 실행 전 합성 트리거로 단위 검증했고
  (원본 SHA 핀 대조, c1 앵커 0x40c390→0x40c3ae 왕복 확인), 실제 게임 산출물에서도 c1 앵커 계산이
  재확인됐다(`c1_cmdstop_call_plus5_sites=['0x40c3ae']`). **중요 negative finding**: `push ebp; mov ebp,esp`
  prologue-scan으로 "ISSUER_FN(함수 시작점)"을 일반적으로 구하려던 최초 설계는 실행 전 자체 반증됐다 —
  FUN_0040C390 자체가 `56 6a 00 8b f1`(push esi; push 0; mov esi,ecx)로 시작해 프레임포인터 프롤로그가 없다
  (objdump로 원본에서 직접 확인). 그래서 일반 ISSUER_FN 해석은 구현하지 않았고, c1 단일 주소만 정적으로
  검증해 사용했다. **후속 lap(middle 이후)이 이 방식을 다시 쓸 경우 이 negative finding을 재확인하고
  진행한다.**
- 다음 한 가지: **middle(Opus5.5)**: `triggers.jsonl`(20건)·`trace.jsonl`·`h16_report_{A,B,RB}.json`을
  원시로 재계산하고, `0x48e83c`(CmdStop 발행, A·B 공통)와 `0x48bba3`(CmdMove 재발행, R_B)의 **ISSUER_FN과
  바로 위 호출자 1단을 한 번 읽어**(카드 §2, 60분) OWNER_AI/UNIT_OTHER/UNCLASSIFIED를 정한다. 위 디스어셈블
  스니펫이 출발점이다(`call 471600`·`call 471af0` 게이트의 정체가 관건). 카드 §3 분기표대로 다음 한 가지를
  정한다 — A 또는 B가 OWNER_AI면 S1 `BLOCKED`·사용자 보고(§4 선택지), 둘 다 UNIT_SELF/UNIT_OTHER면 그
  분기 읽고 E2 work 가능성, UNCLASSIFIED면 BLOCKED·사용자 보고. 새 질문은 만들지 않는다(카드 §5 통지 유지).
