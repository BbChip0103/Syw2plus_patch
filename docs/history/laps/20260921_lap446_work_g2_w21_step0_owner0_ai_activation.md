# 2026-09-21 | lap 446 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 역할 **work**
  (`docs/MODEL_ROUTING.md` 실무 역할, 이번 세션은 loop runtime이 아닌 일반 세션이나 동일 역할 계약 적용).
- 가설 / 사용자 관찰: W21 카드(`docs/work/active/G2_CAP_PROXIMITY_SEEDED_SOAK_LAP445.md`) Step0.
  lap445 middle이 §2-1로 **소스 한 줄**(`tools/inmm_stub/control_executor.c:913`
  `record[2] = (BYTE)(owner == 0 ? 0 : 1);`)까지 정적으로 좁힌 N56을 **런타임 대조 1회**로 실증한다:
  owner0만 `record[2]=0`(비-AI)이라 자유대전 AI가 붙지 않아 lap442 soak 내내 `(used,count)=(20,2)`
  로 고정됐다는 가설.
- 예상 PASS / FAIL 조건: 카드 (U0) — owner0의 `(used,count)`가 baseline `(20,2)`에서 벗어나 **증가**하면
  PASS. 실패 시 이후 Step은 "7인+미활성1"로만 기재(중단하지 않음).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `tools/inmm_stub/control_executor.c` — 새 opt-in 골 `G2_EIGHT_AI_GOAL`
    (`_custom_game_chain_inject_g2_eight_ai_seed42`) 추가. **기존 `G2_EIGHT_GOAL`의 동작은
    바이트 단위로 그대로 유지**(`owner0_ai` 지역변수가 `FALSE`일 때 `record[2]`식이 기존과
    동일하게 계산됨) — lap419~442 증거 의미 불변, 카드 §3-2 "새 goal 추가" 권고 이행.
  - `tests/test_g2_eight_owner_setup.py` — 새 정적 가드 1개 추가
    (`test_g2_eight_ai_goal_only_changes_owner0_record2`) + 기존 2개 테스트의 pinned 문자열을
    새 소스와 일치하도록 갱신(`is_g2_eight_goal` 두 goal 비교, `record[2]` 3항 조건식).
  - 커밋 없음(`LOOP_ALLOW_COMMITS=0` 기본, uncommitted 상태 유지).
  - source fingerprint(변경 파일 read-time sha256, git 미사용 — repo가 unborn HEAD):
    `control_executor.c` 변경 후 read-time 확인은 아래 원본 EXE와 별개(이 파일은 EXE가 아니라 진단
    DLL 소스이며 게임 원본과 무관). 게임 원본 EXE는 전 구간 불변(아래).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — Step0 실행
    전/후 모두 직접 재해시로 불변 확인(아래 검증 로그).
  - 이번 Step0은 **후보 EXE 패치 없음** — 설치된 `syw2plus_original.exe`가 원본과 byte-identical임을
    스크립트 자체가 실행 중 재확인(`installed_exe sha256 == ORIGINAL_SHA256` 아님이면 즉시 abort).
    검증 대상은 진단 DLL(`_inmm.dll`, `bridge_sha256=15aa1715…`, capacity=1200 stock)뿐이다.
  - 환경: 격리 복사본 `local/runtime/20260921_085544_3103469_0`, 전용 wine prefix, 빈 Xvfb
    `:3950`, `WINEDLLOVERRIDES=ddraw=b`, `SYW2_SUPPLY_PROBE=1`.
  - fixture: 골 `_custom_game_chain_inject_g2_eight_ai_seed42` → PS7→PS3 체인 → 8 owner 전원에
    op7(resource-only, rice/wood 각 1,000,000) 적용(lap442와 동일 축, AI 플래그 효과를 자원
    부족과 분리하기 위해 owner0뿐 아니라 8명 전원에 동일 적용).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 스크립트:
    `temp/Syw2plus_patch/g2_capacity/20260921_lap446_w21_step0_owner0_ai_activation/step0_owner0_ai.py`
    (동기 실행, 셸 background로 넘기고 끝내지 않음 — 도구가 120s 뒤 자동으로 백그라운드 전환했으나
    이번 세션이 완료까지 직접 대기·회수했다).
  - 원시 표본: `.../samples.jsonl`(91표본), 요약: `.../run_summary.json`,
    orchestrator 로그: `.../step0_orchestrator.log`, 자원 receipts: `.../resource_receipts.json`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - PS3 진입 직후(op7 이전) `players_at_ps3`: **owner0 `ai=1`, owner1 `ai=1`** (8명 전원 `ai=1`).
    기존 goal이었다면 owner0만 `ai=0`이었을 자리다 ⇒ `record2_verified=true`.
  - owner0가 baseline `(used=20,count=2)`을 벗어난 시점: **tick=284**
    (`{owner0: count=3, used=30}`) — 카드가 요구한 ≤3,000 tick 안에서 즉시 이탈.
  - STOP_TICK=3,000 도달(`final_tick=2986`, `stop_reason=stop_tick_reached`), fault/crash 0.
  - 종료 시 8 owner `count`=`[13,13,13,14,13,11,11,11]`, `used`=`[150,145,145,160,145,120,120,115]`
    — owner0이 다른 7명과 **동일 규모**로 성장(더 이상 이상치가 아님).
  - **⇒ (U0) PASS.** N56이 추정→소스 귀속(lap445)→**런타임 실증**(이번 lap)으로 닫혔다:
    owner0 비활동의 원인은 `record[2]`(AI 컨트롤러 플래그)였고, 새 goal로 owner0도 정상 AI
    경제 성장을 보인다.
  - 통합 게이트: `make check` **790 passed**(789+신규1, 546.88s), Ruff/compileall/mypy/
    `CONTEXT_PASS` 전부 통과. `checks/safety.sh check` → `SAFETY_PASS`. 원본 EXE 직접 재해시
    `b56986e0…c9c08a8ac` 실행 전/후 불변(스크립트 자체 검증 + 별도 독립 재해시 둘 다 일치).
    이번 회차 **source 변경 있음**(위 파일 2개) ⇒ INBOX 21:58 규칙대로 통합 `make check` 전체
    1회 실행함(면제 미적용, 명시).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 이 lap의 결과는 **work 자기 결과이며 독립(다음 middle) 검수 없음.**
  - `record[2]`가 "1=AI/컴퓨터"라는 의미 자체는 여전히 원본 바이트(`FUN_0041B9B0`)의 정적
    역추적으로 확정된 것이 아니라 **이번 런타임 대조 1회**로 실증된 것이다(카드가 요구한 범위와
    정확히 일치 — "원본 `FUN_0041B9B0`의 정적 역추적을 새로 시작하지 않는다").
  - 카드 §0 경계 그대로 유지: 이 결과 하나로 G2 완료를 주장하지 않음, 건물 계층 미포함, 144k
    카드 발행 금지 유지.
  - Step1(cap 근접 시딩 + 24k soak + RSS 계측), Step2(신후보 저장/로드 왕복), Step3(대조표
    fail-closed)는 **이번 lap에서 미착수**다 — PROMPT ③의 "한 바퀴 한 가지" 원칙에 따라 Step0만
    닫고 다음 회차로 넘긴다(Step1은 24k tick 규모라 별도 회차가 필요).
  - `local/runtime/20260921_085544_3103469_0`은 정리하지 않았다(디스크 여유 287G, N56 실증
    증거의 run_dir이라 이 lap 범위에서 삭제하지 않음).
- 다음 한 가지: 카드 §3-2 권고대로 새 goal을 **유지**한 채(기존 goal 미변경 확인됨),
  다음 work 회차가 Step1을 실행한다 — Step0에서 검증된 `_custom_game_chain_inject_g2_eight_ai_seed42`
  goal로 N=4001 신후보(`a10024de…`, 재빌드로 SHA 확인) 위에서 8 owner disjoint anchor로
  op5(type5,cost35)+op6(type7,cost10) 혼합 시딩 → `used∈[4900,5000]` 도달 → STOP_TICK≥24,000
  soak + `rss_kb`/`vm_size_kb`/`vm_swap_kb`/`host_mem_available_kb` 계측(N57) → Step3 대조표
  fail-closed 작성(카드 §3~§7 그대로, 이번 lap이 바꾼 것은 없음).
