# INBOX lap519 압축 직전 원문 (SHA256 13d5325562b133b2efdd5f88c054fc5a57eb33e8dcf9cb5b6639fd8b2f2f0a60, 353줄) — 삭제·재해석 없음

# INBOX — 사용자 지시 원문과 처리 상태

체크는 문서 반영 여부이며 제품 구현 완료가 아니다. 체크된 상시 요구도 계속 유효하다.

## 처리 대기

- [ ] 2026-09-23 KST: 사용자 "opus 5.5 나왔는데, 한동안 fable 대신 opus 5.5 사용해보자. effort도 high로".
  **strategy 역할 모델을 `claude-fable-5`/medium → `claude-opus-5-5`/high로 교체**(`loop/env.local.sh`
  `LOOP_CLAUDE_STRATEGY_MODEL`·`LOOP_ASTRA_EFFORT`). `loopctl.sh models` 반영·CLI 응답 확인. middle(opus-5)·
  work(sonnet-5)는 불변. 임시 조치("한동안")라 `docs/MODEL_ROUTING.md`·CLAUDE.md의 Fable 기본값 문구는 고치지 않았다.
- [ ] 2026-09-23 KST: 사용자 "middle이랑 work도 각 모델 최신 버전으로 쓰도록 해". **middle을 `claude-opus-5`→
  `claude-opus-5-5`로 교체**(`LOOP_CLAUDE_MIDDLE_MODEL`). work는 CLI 확인 결과 `claude-sonnet-5-5`·`-5-1`이 카탈로그에
  없어 최신 Sonnet인 `claude-sonnet-5`를 유지한다(다른 세대 폴백 없음). effort는 둘 다 high로 변경 없음. `loopctl.sh models`로 반영 확인.


- [ ] 2026-09-23 12:55 KST: 사용자 "3은 앞으로 말하지 말고, 1 2 바로 ㄱㄱ". **두 트랙을 이 순서로**
  진행한다. **① F4(B) 전비 장부 32-bit 확장** — 2026-09-23 04:13 사용자 승인(APPROVALS 기록) 이미
  받았고 선행조건이던 AI 생산 정지 분석은 lap501~508로 종료됐으므로 **지금 착수 가능**. middle이
  카드부터 발행한다(writer 2곳 `0x43EE9B`/`0x43EF8B`·reader 3곳·필드폭·bulk save/load 포맷,
  저장 호환 방침 포함). **② 건설 선택 로직 분석**(읽기 전용, (ㄴ) 불필요) — 27종 중 18종을 AI가
  왜 안 짓는지. `FUN_00406C70` 추첨 로직 해부 + H-CROWD 채널 주소 정정이 시작점이다.
  **③ 패치본(2601·2606) 실행 검증은 사용자가 제외했다 — 앞으로 제안하지 않는다.**

  **2026-09-23 lap509(middle, Opus5) 트랙① 수행 — F4(B) 카드 W30 발행 + 범위 정정 2건**
  (카드 `docs/work/active/G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md`, 근거
  `analysis/memory_maps/g2_supply_ledger_200c_site_inventory_lap509_20260923.md`, 회부 `ESCALATE_SOL` §70).
  원본 SHA `b56986e0…`를 **직접 전수 디스어셈블**(306,187 명령)해 카드를 쓰기 전에 범위를 재확인했고,
  **위 지시문의 범위 서술 2가지가 사실과 달랐다**(지시 자체가 아니라 모델이 STATUS에 전사한 근거가 틀렸다):
  **① 범위는 5곳이 아니라 9곳이다.** `+0x200c` reader로 적힌 `0x43EE03`/`0x43F0F3`/`0x43F43F`는
  실제로는 **`+0x2012`(supply_limit) 읽기**다(`hero_limit_supply_patch_sites_20260921.md` 원문은
  정확했고 STATUS 전사에서 필드가 뒤바뀌었다). 진짜 `+0x200c` 사이트는 base+disp 5곳
  (`0x43EDFC`·`0x43EE9B`+·`0x43EF8B`−·`0x43F0E9`·`0x43F3B3`) + **절대주소 별칭 `0x95877C` 4곳**
  (`0x40DD12`·`0x40E03B`·`0x499767`·`0x499A0E`)이며, 후자 4곳은 **기존 범위에 아예 없었다.**
  **② "저장포맷 변경 동반"은 전제가 아니다.** bulk save/load는 고정 길이 raw span
  `[0x892410,0x975D8C)`=932,220B를 통째로 읽고 쓰며(save `0x440F02`/load `0x4412D2` 즉시값 동일)
  PlayerStruct 배열이 그 안에 있다 ⇒ **stride `0x3ABC`를 보존하면 저장 파일 길이·레이아웃은 불변**이고
  호환 문제는 *포맷*이 아니라 **2바이트 값 해석** 문제로 축소된다. 이로써 lap393 D절의 "work 단독
  착수 금지" 근거가 부분 해소됐다(stride 변경 경로는 여전히 금지).
  **부수 성과 — F4 "안전상한 UNKNOWN"(lap395)을 숫자로 닫았다:** `roster_add`(`0x43EE30`)는 cap을
  보지 않고 `cmp ax,0x4b0`(로스터 1,200칸)만 걸며 `c_max=65`(lap507 W29) ⇒ 구조적 최대 `used`
  = **1,200×65 = 78,000 > 32,767** ⇒ 16-bit 랩은 구조적으로 **가능**(lap395 실측 32,785와 정합)하고,
  32-bit에서는 78,000 ≪ 2^31이라 **구조적으로 불가능**해진다. 도달성은 여전히 UNKNOWN이다.
  재현 probe `docs/history/laps/probes/20260923_lap509_middle_supply_ledger_site_inventory.py`
  (exit 0, 사전 고정 단언 7/7 PASS). 게임실행0·제품source변경0·커밋0·796 passed·`SAFETY_PASS`·`CONTEXT_PASS`.
  **미결(모델이 고르지 않음): 위 ③의 제외 범위가 커뮤니티 배포본(2601·2606)만인지, F4 후보 EXE의
  실행 검증까지인지 문서상 불명확하다.** 전자면 F4에 별도 실행 카드가 필요하고, 후자면 F4는 정적·단위
  증거까지만으로 끝나 DESIGN 4절이 요구하는 실행 증거가 없어 **G2 제품 합격 근거로는 쓸 수 없다.**
  **lap510(work)→lap511(middle, Opus5.5) 진행:** lap510이 안 A(`used`→`+0x2100`)로 패처를 구현했으나
  lap511 독립 검수가 **구멍 선택을 기각**했다 — `+0x2100`은 `+0x2014`/`+0x2018` **1,000칸 리스트의
  58번 칸**(짧은 실행에서 리스트가 9칸만 차 우연히 0이었다). 패치 기계부(11곳·원복·diff)는 ACCEPT.
  다음 work는 카드 §8의 **안 B**(building_count를 `+0x2016` 패딩으로 옮기고 `used` 제자리 확장)를 구현한다.
  근거 `analysis/memory_maps/g2_supply_ledger_hole_rejection_lap511_20260923.md`, `ESCALATE_SOL` §71.
  **lap512→lap513 진행:** lap512(work)가 `supply_ledger_32bit.py`·테스트를 안 B로 교체했으나 24k
  런타임 재확인을 background로 넘긴 채 세션이 끝나 미완주(orchestrator.log 2줄=bridge build 직후
  정지). **lap513(work)이 그 스크립트를 수정 없이 재사용, 포그라운드 동기 실행으로 완주**:
  `+0x2016` 24k soak `verdict=HOLE_CONSTANT`(tick24,019·721표본·위반0), 원본 SHA 전후 불변,
  단위 23 passed, `make check` 819 passed·`SAFETY_PASS`·`CONTEXT_PASS`. 카드 §8 M-a~M-h 전부
  기계/실행 증거로 닫혔다(work 자기승인 아님, 다음 middle 독립 재계산 대기). 전문
  `docs/history/laps/20260923_lap513_work_w30_holeb_runtime_reconfirm.md`.
  **lap514(middle, Opus5.5): 트랙① W30 독립 재계산 `ACCEPT` ⇒ `CLOSED`**(원시 5,768표본 위반0, 겹침 전수 스캔 누락0,
  후보 `1893ff50…` 원복 SHA 재현, used 소비 전부 32-bit). 후보 EXE 실행 0(Q9 미결) ⇒ G2 제품 근거 아님.
  **다음은 트랙②(건설 선택 로직 분석) W31 카드 발행.** 전문 `docs/history/laps/20260923_lap514_middle_w30_holeb_independent_recompute.md`.
  **lap515(middle, Opus5.5): 트랙② 착수 — "18종을 왜 안 짓나"의 답은 진영 블록이다(정적 probe 단언 18/18, 2단 검수 전).**
  **lap516(work, Sonnet5): W31 M-0/M-1/M-2 실행 `PROBE_OK`, 라벨 `UNCLASSIFIED` 8/8** — `+0xD34`가 건설
  전용이 아니라 20종 AI 오더 공용 필드이고 실패 시 `FUN_0043F5A0`이 0으로 리셋함을 신규 확인(재시도
  아닌 오더 종료, 재무장 스케줄러는 UNKNOWN). 24k 8owner 전원 상태0 지배 85.6~87.9%인데도 건물은
  순증가 9~18채. 상세 `docs/STATUS.md`·`loop/ESCALATE_SOL`§74·`docs/history/laps/20260923_lap516_*.md`.
  다음=middle 독립 검수.
  **lap517(middle, Opus5.5): W31 독립 검수 ⇒ `CLOSED`** — M-2 재집계 불일치 0/8, 단 오더 종류는 `+0xD32`(`+0xD34`는 하위 상태, N162).
  재무장 스케줄러 해독(N164: owner당 8 tick 1회·`rand%20` 한 칸·100 tick 쿨다운, 천장 ≈91/24k vs 관측 9~18채). 다음=work W32 실행.
  건물 건설 결정은 `FUN_00406C70`(유닛 생산 추첨)이 아니라 `FUN_0043E0E0`→`FUN_0043DBB0`이고, 후보는 로스터의 일꾼 종류
  (조선7·명21/70·일본75)로 진영 블록이 열린다. fixture 8 owner는 **전원 조선**(nation 1) ⇒ 미건설 18종 = 일본9+명9,
  "9/27"은 **조선 생산 건물 9/9 전부**다(N158). N152의 7종 경로는 3진영 혼합이라 단일 AI 불가(N159). 단일 진영 유닛 천장은
  조선 2,835·일본 2,527·명 2,715 — 모두 5,000 미만이지만 **건물도 전비에 들어가고 건물 수는 고정 상한이 아니라 보유 건물 수에
  비례해 자란다**(N160) ⇒ 조선 AI의 5,000 = 건물 약 160채 필요, 24k tick 관측 11~20채·건설 계속 중 ⇒ 병목은 **건설 속도**(N161).
  **Q8 설명 전제가 "건설 레퍼토리"에서 "진영 블록 + 건설 속도"로 바뀐다(모델은 선택지를 고르지 않음).** 다음 work가 카드 W31
  (`docs/work/active/G2_BUILD_PACE_STATE_PROBE_LAP515.md`, 읽기 전용 24k 표본)로 속도 병목을 판별한다. 근거
  `analysis/memory_maps/ai_build_faction_gate_0043dbb0_lap515_20260923.md`, `ESCALATE_SOL` §73.
  **lap518(work, Sonnet5): W32 M-1/M-2/M-3 실행 `PROBE_OK`, 카드 §3 반증조건②가 8/8 owner에서 성립 ⇒
  `MODEL_REFUTED`(라벨 미부여, 원시 보고).** 신규 3필드(`+0xD32` 오더종류·`+0x33AC` 시작tick·`+0x3A70`
  발부tick) 24,005tick 완주 채집: `f_idle` 0.887~0.915·`S/S_exp` 1.02~1.25(반증①불성립)·
  `S_short_gap_defects` 8/8 0건·`C/S` 0.125~0.307(<0.5)·`B/C` 0.519~0.818. 그런데 "`+0x33AC` 변화
  표본에서 `+0xD32≠1`"이 시작의 26.6~44.3%(23~43/83~102건)에서 실측돼 정식 라벨(`EXEC_FAIL_BOUND` 등)
  대신 원시만 보고한다(재해석 금지). 원인(스케줄러 8-tick 이하 초고속 실패 vs SCH §2 모델 결함)은 이
  카드 범위로 미판별, UNKNOWN 유지. N144 결정성 대조 PASS(lap516과 max_used·건물수 불일치 0/8).
  게임실행1(24,005tick)·source변경0·커밋0·`SAFETY_PASS`. 상세
  `docs/history/laps/20260923_lap518_work_w32_build_order_funnel_probe.md`, 근거
  `analysis/memory_maps/ai_build_order_funnel_probe_lap518_20260923.md`, `ESCALATE_SOL` §76.
  다음=middle 독립 검수.

- [ ] 2026-09-23 04:14 KST: 사용자 "AI 생산 정지 원인 분석부터 ㄱㄱ". **N81/N82가 배제만 하고
  코드 원인을 찾지 않은 지점을 먼저 판다.** 실측 사실: 8 AI가 자원 96.8%를 쥔 채 정지하고
  (`used` 최대 1,708/cap 5,000=34%, `count` 108/1,200, `live` 774/4,001) 감쇠가 아니라 **완전 정지**
  (owner5 tick14,641 이후 9,371tick=39% 무증가, `r_late` 정확히 0.0). 즉 자원·count_cap·supply cap·
  풀 **넷 다 원인이 아니다**. 이번 작업은 **읽기 전용 정적 분석**이라 (ㄴ) 승인이 필요 없다 —
  AI 생산 결정 경로(참고 저장소가 `production_pick_context 0x406D15`로 부르는 지점 등)를 추적해
  owner5를 tick14,641에 멈춘 조건을 특정한다. **AI/생산 로직 변경·패치 착수는 금지**(여전히 (ㄴ) 대기).
  `analysis/`에 AI 생산 결정 로직 문서가 **0건**이라 새 근거 문서를 남긴다.
  **lap501~507 진행 추기(lap509 압축 — 원문 전량 보존, 삭제 없음):** 이 지시에 lap501·502·504·505·
  506→507이 덧붙인 추기 77줄은 `docs/history/20260923_inbox_lap509_ai_production_lineage_archive.md`
  (SHA256 `02e057116931a157b0e71dc14b466c96e45fc023e8c1582ba946d32eb8f47db4`, 77줄)에 그대로 있다.
  요지: lap501 정적 추적으로 `FUN_00406770`→`FUN_00406B00`→`FUN_0043E7F0`/`FUN_00406C70` 경로를
  바이트 확정(자원 게이트 0개 ⇒ "자원 잔존+정지"는 정상 동작) → lap502 §7 런타임 probe `UNKNOWN`
  → lap504 독립 재계산 ACCEPT + 해석 반증 N147~N150 → lap505 strategy Q8 = CONTINUE·예산 한정
  + W29 발행 → lap507 W29 실행 `PROBE_OK`·k=8 → **lap508 독립 재계산 ACCEPT ⇒ 라벨
  `NATURAL_ARRIVAL_ARITH_INFEASIBLE` 확정, 단서 정정 N151~N153**(전문 `ESCALATE_SOL`§64~§69,
  `docs/history/laps/20260923_lap50{1,2,4,5,7,8}_*.md`). 이 계보는 **종결**이며, 2026-09-23 12:55
  사용자 지시가 다음 트랙(F4(B) → 건설 선택 로직)을 지정했다. AI/생산 로직 변경은 여전히 0건이고
  (ㄴ)·Q8((ㄱ)/(ㄷ))은 사용자 전권 대기 불변이다.


- [ ] 2026-09-23 lap501 운영 보고 2건 (숨기지 않고 남긴다, 사용자 판정 불필요하면 그대로 둬도 됨):
  **① 연속 3회차 제품 증거 무증가 경계.** lap499(strategy 문서)·lap500(middle 문서)·lap501(middle
  문서)로 **제품 코드/바이너리/실제 실행 증거가 늘지 않은 회차가 연속 3회**다. PROMPT ③은 연속 최대
  2회이고 세 번째는 strategy/Sol이 목표 계속 여부를 먼저 판정하도록 한다. **다만 lap501은
  2026-09-23 04:14 사용자 지시가 "읽기 전용 정적 분석"으로 명시 지정한 작업**이므로 루프 내부 규칙이
  아니라 사용자 지시를 따랐다. **다음 회차는 실제 관측 증거를 만드는 §7 probe여야 하며**, 그것도
  문서로 끝나면 strategy 판정 없이 더 쌓지 않는다(`ESCALATE_SOL` §64 handoff 1).
  **② 참고 저장소에 하네스 scratch 쓰기가 발생한다.** `Syw2plus_re/.omc/` 아래에 세션 state 파일이
  생성된다(이번 세션분 1건, `.omc/state/sessions/eed5d653…/pre-tool-advisory-throttle.json`,
  `analysis/ghidra_output/.omc/`도 동일 계열). AGENTS.md는 참고 저장소를 **읽기 전용**으로 규정하므로
  보고한다. 완화 사실: 해당 경로는 그 저장소 `.gitignore`가 덮고 있어 **추적 대상이 아니고**,
  세션 디렉터리가 386개로 **2026-07-30부터 누적된 기존 패턴**이며, **이번 세션이 추적 파일을 하나도
  변경하지 않았음을 확인**했다(`git status --untracked-files=no` 목록 전체가 2026-09-23 이전 mtime).
  분석 자체는 읽기 전용이었다. 정리·차단이 필요하면 사용자 판정 사항으로 남긴다.

- [ ] 2026-09-23 04:13 KST: 사용자 "전비가 일시적으로 5000을 넘어 보이는 표시를 허용하고, 32비트도 괜찮아".
  **되물음 2건이 사용자 전결로 마감됐다.** ① lap404 = **(가) 채택** — 일시 `used+reserved` 초과
  표시를 허용하고 **라이브 `used` ≤5000만 강제**한다((나) strict 5000 기각). ② F4 = **(B) 채택** —
  전비 장부를 **32-bit로 확장**한다(저장포맷 동반, 큰 작업). (C) 도달성 실측 선행은 기각.
  **두 건 모두 lap404 strategy 권고((가) 권고·F4는 (C) 선행 권고)와 ①은 일치, ②는 반대다.**
  모델이 사용자에게 고지한 단서 원문: (가)는 N19대로 "한 tick 창"이 아니라 owner당 수 분
  (owner6 16,213tick≈490초·owner5 19,904tick≈600초, 초과 owner-표본 216건, 값은 전부
  `used=5000·reserved=10`)이고, "원본 1200-slot 대조군에서도 동일"이라는 귀속은 **미증명**이다.
  F4(B)는 5 사이트+필드폭+bulk save/load 포맷 변경이라 기존 통합 blocker와 동일 성격이다.
  **미결로 남은 판정: Q7-A=(ㄴ) AI 변경 허용 여부 · Q7-B 3단 마일스톤 · (ㄱ)/(ㄷ).**

- [ ] 2026-09-22~23 lap471~498 W24~W28-R settlement-blockage + W26 144k soak 계보 **종결**
  (lap501 압축 — 원문 전량 보존, 삭제 없음): lap471~498 전문은
  `docs/history/20260923_inbox_lap501_precompaction.md`(SHA `771f32491e8f179ef5f576df469d5c8fb4926f8d0c5143834616b0a6c3c09201`, 65줄, 이전
  precompaction 스냅샷 포인터 연쇄 보존)와 각 `docs/history/laps/20260923_lap49{1..8}_*.md`에
  그대로 있다. 요지: W28-R `CLOSED`(lap496 ACCEPT·라벨 `SETTLEMENT_RESUMED_AFTER_HEADROOM`) →
  W26 발행 → lap497 144k soak 완주 → lap498 원시 독립검수 ACCEPT ⇒ W26 `CLOSED`,
  종합 `CAP_PROXIMITY_STABLE_144K`(부분 증거), U4=(a) 호스트 페이지 회수, N141 제기.
  **lap500이 N141을 강등**(N144 결정성·N145 창 절단·N146). 후속 work 카드 미발행, `ESCALATE_SOL` §61 Q7 회부.
  (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 마일스톤 승인은 전부 사용자 전권 대기 불변.

- [ ] lap469~471 계보 (lap472 압축·lap486 재압축 — 원문 전량 보존, 삭제 없음): lap469(work) Step C
  3회차 `RIDER_NO_REPRO` → lap470(middle) **REJECT(`STEP_C_PRECONDITION_NOT_MET`)**(N98~N104) →
  lap471(work) 4회차는 §42-6의 4가지를 구현해 전제를 처음 성립시켰으나 주문이 창 2,106tick 내내
  `reserved=0`이라 4번째 상태 **`RIDER_ORDER_NOT_ACCEPTED`**로 종료(1차 discriminator 결함은 work가
  직접 정정, 원문 `attempt1_stale_progress_false_positive/`) → lap472 독립검수.
  전문은 `docs/history/20260922_inbox_lap472_precompaction.md`(SHA `87ac134e…`, 390줄)·
  `20260922_inbox_lap486_precompaction.md`(SHA `f1054f35…`, 404줄)와 각
  `docs/history/laps/20260922_lap4{69,70,71}_*.md`(`ESCALATE_SOL`§42·§43)에 그대로 있다.
  **lap465~467 원문**은 `docs/history/20260922_inbox_lap469_precompaction.md`
  (SHA `02fa663c…`, 393줄)와 각 `docs/history/laps/20260922_lap46{5,6,7}_*.md`에 그대로 있다.

- [ ] lap462~465 계보 (lap466 압축·lap485 재압축 — 원문 전량 보존, 삭제 없음): Step A
  `BUILDING_SEEDABLE`+Step B 수리 → lap463 background 방치 FAIL(01:01 규칙 위반)+N90 →
  lap464 N90 수리+Step D `NO_ENGAGEMENT` → lap465(middle) Step D **ACCEPT**·Step C **VOID**
  (N91~N95) → lap466이 Step C 결손 해소. 전문은
  `docs/history/20260922_inbox_lap466_precompaction.md`(SHA `5b92adeea252861e1ffbe7314475c4de6d2c7619d72e775256154f2a8c1a9f68`, 396줄)·
  `docs/history/20260922_inbox_lap485_precompaction.md`(400줄)와
  `docs/history/laps/20260921_lap462_*.md`·`20260922_lap46{3,4,5}_*.md`에 그대로 있다.

- [ ] 2026-09-21 01:10 KST 운영 회수 — W10 P-A 실제 완료. lap415 입력의 PID 원인 서술은
  **정정**한다: PID는 맞았고 최초 PE mapping 전 일시 `EFAULT`를 retry하지 않은 것이 원인이었다.
  lap416 probe 수정본을 root 소유 동기 세션에서 새 run2로 실행해 709표본/동일 tick11,928 정지를
  재현했다. fault 직전 생존 high-slot **3565/type76/owner4**의 `+0x692`가 tick11,921에서 -6599,
  tick11,928에서 19579로 폭증했고 low band 이상은 0이다. 따라서 카드 P-A의 **H1 지지** 조건을
  충족한다. 증거 `temp/Syw2plus_patch/g2_capacity/20260921_lap416_fault_root_cause_pa_run2/`;
  후보 SHA `4331d9cd…`, 원본 전후 `b56986e0…`, 709 lines, `SAFETY_PASS`, 잔류0. 다음 work는
  W10 P-B의 1200-bound 전수 인벤토리와 이 손상을 만드는 단일 site를 좁힌 뒤 P-C 최소 수리한다.

- [ ] 2026-09-21 01:01 KST 운영 규칙: loop agent가 장시간 Wine probe를 셸 background로 띄운 뒤
  회차를 종료하면 loop cleanup이 자식도 정리해 실행이 지속되지 않는다. 장기 probe는 모델 세션이
  직접 기다리거나 root가 소유한 exec 세션으로 실행·회수한다. “background 실행 중” 문구만으로
  활성 프로세스를 주장하지 않고 PID/산출물 갱신을 확인한다.

- [ ] 2026-09-21 00:51 KST 운영 회수: lap415 W10 P-A probe는 실제 샘플링에 진입하지 못했다.
  `movement_state_probe.py`가 `subprocess.Popen(["wine", ...]).pid`인 Wine 런처 PID 2435667을
  게임 내부 PID로 사용해 PS 주소 `0x4ED818` read가 `EFAULT`로 종료됐고 `samples.jsonl`은 0B다.
  게임 후보 실패나 H1/H2 판정으로 세지 않는다. 산출물은
  `temp/Syw2plus_patch/g2_capacity/20260921_lap415_fault_root_cause_pa/`에 보존됐다. 다음 work는
  기존 `tools.runtime_env`/`runtime_driver`의 검증된 Windows game PID 발견 방식을 재사용해 같은
  P-A를 재실행한다. 새 독자 PID 추측을 추가하지 않는다.

- [ ] 2026-09-21 00:20 KST: 사용자 목표 우선순위 확정. **G2(8인 각각 전비 5000 안정 플레이)가
  성립하기 전까지 G1(1600×1200 원본 구성)과 G4(AI/길찾기 개선)는 잠정 중단**한다. G3(최대
  16인)는 잠정 중단이 아니라 **계속 포기한 범위**로 고정한다. 현재 lap414의 G2 독립 검수는
  이 지시와 일치하므로 중단하지 않으며, 이후 루프도 G2의 직접 조사·수리·실행검증 외 목표로
  전환하지 않는다.

- [ ] 2026-09-20 21:58 KST: 사용자 “아니 뭐 이렇게 굼떠”. 같은 소스에 대해 784개 전체
  `make check`를 회차마다 반복해 실제 게임 실행을 늦추지 않는다. 직전 동일 source의 full gate가
  PASS이면 다음 독립 검수는 원시 산출물·표적 테스트·원본/안전검사만 수행하고 제품 런타임으로
  즉시 이동한다. 전체 gate는 소스 변경 뒤 통합 경계에서 한 번만 실행한다.
  **2026-09-20 lap410 적용(상시 규칙이라 체크는 두지 않음):** 이 지시를 처음 적용했다. lap410은 동일
  source·직전 full gate PASS이므로 784 `make check`를 재실행하지 않고 원시 산출물 재계산 + 표적 테스트
  (`test_g2_full_capacity_persistence_compat_v1.py` 5 passed) + 원본 해시 + `checks/safety.sh check`만
  수행했다. 발행한 다음 카드 W8에도 §6으로 같은 규칙을 박아 두었다.
  **2026-09-20 lap412 오적용 정정(N22):** 이 규칙은 "동일 source일 때 면제"이지 "항상 면제"가 아니다.
  lap411은 스스로 `patches/population/runtime_driver.py`(`control_goal_payload`)와 신규 테스트
  `tests/test_runtime_env.py::test_runtime_driver_control_goal_uses_protocol_string_request_id`를
  추가해 **source를 바꿨는데도** "동일 source"를 근거로 전체 gate를 건너뛰었다. 규칙 후단
  "전체 gate는 소스 변경 뒤 통합 경계에서 한 번만 실행한다"가 걸리는 경우였다. lap412 middle이
  그 통합 경계 gate를 대신 실행했다(collected **785** = 784+신규1). **규칙 자체는 유효하며 변경 없다** —
  앞으로 면제를 주장하는 회차는 "이번 회차에 source를 바꾸지 않았다"를 함께 적는다.

- [ ] 2026-09-20 00:33 KST: 사용자 "그래 그 1200을 늘릴 수는 없냐고" 이후 "ㄱㄱ".
  G2의 즉시 최우선 작업을 전비 장부 단독 조사에서 **전역 UnitStruct 풀 1,200칸 확장 실행
  스파이크**로 전환한다. 첫 성공 기준은 격리된 실제 게임에서 slot index **1,200 이상** 개체를
  정상 생성하고, 기존 reader로 관측한 뒤 사망·슬롯 재사용까지 증명하는 것이다. 단순 `0x4B0`
  상수 변경이나 다음 상태영역 덮어쓰기는 금지한다. 새 풀/보조배열 주소 재배치와 참조 fixup을
  최소 범위로 구현하고, 실패 가설 2회 또는 60분 안에 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`로
  판정한다. 저장/LAN은 이 첫 스파이크의 PASS 조건이 아니지만 후속 필수 blocker로 명시한다.
  2026-09-20 lap396 전비 probe는 이 최신 우선순위에 따라 안전 종료(exit143, safety ok)했다.
  2026-09-20 lap397 middle이 정적 표면을 측정해 최소 변경 범위를 확정하고 즉시 실행 가능한
  work 카드 `docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md`(W3)로 인계했다.
  건드릴 것은 재배치3영역(pool/existence/age)+상수4개+fixup1,016건뿐이며 active/catA/catB·
  PlayerStruct roster·`0x892410` 별칭179건은 불필요함을 바이트로 확인했다. 제자리 확장은
  `NOT_FEASIBLE`(풀이 bulk에 밀착·age뒤 구멍 참조9건), 재배치 경로는 구조적으로 `FEASIBLE`.
  lap399 후보는 lap400이 REJECT(제자리 성장), lap401 work가 꼬리 재배치를 구현, lap402 middle이
  독립 검수해 **재배치·fixup·패처 수리는 ACCEPT**하되 **후보 기동은 REJECT**했다 — 재배치 블록의
  99.24%가 어떤 PE 섹션에도 매핑되지 않는 신규 결함(D1, `.data` VirtualSize 산출 한 줄). 수리 카드는
  `docs/work/active/G2_POOL_SECTION_COVERAGE_REPAIR_LAP402.md`(W5).
  lap406 middle이 자칭 lap410/412 런타임 계보를 2단 검수해 항목1/2/4/5 ACCEPT·항목3(커버리지
  앵커)만 게이트 추가 지시(W6)했고, lap408 middle이 그 W6 게이트 2건을 독립 검수해 **CLOSED**
  했다(`make check` 783 passed=779+4, 역주입으로 D1 계열 포착 확인, 원본·pin 불변). lap408은
  같은 계열의 남은 사각 하나를 W7 `G2_RSRC_WRAPPER_CONTAINMENT_GATE_LAP408.md`로 발행했다
  (`.rsrc` cave wrapper 4건에 컨테인먼트 앵커 없음, 마지막 `LEGACY_COPY` 여유 49B).
  **아직 실제 게임 실행 증거가 없으므로 제품 구현 완료가 아니다** — 체크는 그대로 둔다.
  다음 회차는 W7 뒤 **즉시 P1(near-4000 live 실제 실행)** 이며, 이 첫 성공 기준(slot≥1200
  생성→관측→사망→재사용)의 독립 재현은 여전히 미검증이다.
  **2026-09-20 lap409 work 추기(원문 위는 보존):** W7 앵커 완료 뒤 P1을 착수해 marked compat
  (`4331d9cd…`) 후보로 격리 Wine에서 near-4000(3,991 live, 8owner) 규모 gate-legal 시딩→마킹저장
  (마커 `S2P1N4K1` 파일 오프셋 `0x38` 확인)→마킹로드 왕복을 슬롯 단위로 무손실 확인(소실0·id불일치0).
  slot≥1200 생성→관측→재사용 자체는 이 lap 이전에 이미 실측됐고(seed 시 slot 3977 등 관측),
  이번 lap이 새로 더한 것은 **marked compat 저장/로드가 near-4000에서 실제로 무손실**이라는 증거다.
  **이번 lap은 work 역할의 자기 결과이며 독립(다음 middle) 검수는 아직 없다.** 상세
  `docs/history/laps/20260920_lap409_work_g2_p1_compat_near4000_live_execution.md`.
  **2026-09-20 lap410 middle 추기(위 원문 보존):** lap409 P1을 원시 산출물 재계산으로 독립 검수해
  **ACCEPT**했다(후보 재현·save 해시/마커·스냅샷 diff·receipts·브리지 4001 소스·표적 5 passed·
  `SAFETY_PASS`·원본 불변). 위 21:58 지시에 따라 전체 784 게이트는 재실행하지 않았다(동일 source).
  **신규 근거:** `trace.jsonl`의 tick **2328→1567 역행**이 로드가 실제로 엔진 상태를 교체했음을 직접
  증명한다 — 이것이 없으면 "소실0"은 로드가 아무 일도 안 한 경우와 구분되지 않는다.
  **정정1:** presave 스냅샷이 저장 시점보다 ~535 tick 앞서므로 "5기는 로드 후 생산"은 사실과 다르다.
  4기는 저장 이전 생산(세이브에 포함), 로드 후 생산은 1기. 카운트는 저장 3,995→로드 3,995로 정확
  일치하나 id 단위 검증 범위는 3,995 중 3,991기다.
  **정정2(신규 결함):** 배포 진단 DLL의 `inmm_stub.c`/`ai_shadow.c`/`sfx_hook.c`/`control_executor.c`가
  stock 유닛 존재배열 `0x008990C8`과 1200 경계를 하드코딩해, 재배치 후보에서 유닛을 0기로 관측한다
  (`C:\inmm_unit_ticks.jsonl`이 3,991기 생존 중 0바이트로 실증). 전부 읽기 전용이라 손상 위험은 없고
  P1 판정에도 영향이 없으나, 향후 lap이 이 채널을 근거로 "전멸"을 오판할 위험이 있다.
  **여전히 제품 구현 완료가 아니다** — 단발 왕복 1회이며 장시간 안정성·원본 생산 경로·LAN 미검증.
  다음 회차는 work 카드 `docs/work/active/G2_COMPAT_LONG_SOAK_LAP410.md`(W8, compat 장시간 soak)다.
  상세 `docs/history/laps/20260920_lap410_middle_g2_p1_independent_review.md`.
  **2026-09-21 lap413~414 추기(위 원문 보존):** W8은 lap411 실행·lap412 ACCEPT로 닫혔고, lap413이 W9(P2,
  원본 생산 명령으로 near-cap 도달)를 실행해 **FAIL**했다 — 자원만 공급(op7)한 8인 AI 대전에서 N=4001
  후보가 **두 번 모두 tick 11,928에서 `read 0x00338400 @ 0x00414133` page fault**로 죽었고, stock-layout
  대조군은 같은 tick을 fault 없이 통과했다. lap414 middle이 요약본을 쓰지 않고 원시 산출물만으로
  재계산해 그 FAIL을 **ACCEPT**하고, fault 기전을 바이트로 확정했다(100칸 stack 배열을
  `((경로점수-1)×|유닛 이동진행도 +0x692|)/100`로 인덱싱하며, 그 명령 바이트는 원본과 동일).
  또 후보가 `.text`의 1200 즉치 54곳 중 **2곳만** 4001로 바꿨고 풀을 순회하는 잔존 1200-bound site가
  최소 3곳 남아 있음을 확인했다. **이 첫 성공 기준(slot≥1200 생성→관측→사망→재사용)은 진단 시딩으로는
  충족됐지만 원본 생산·AI 전투 경로의 안정성은 여전히 미충족이므로 체크는 그대로 둔다.**
  다음 회차는 `docs/work/active/G2_POOL_SCOPE_1200_FAULT_ROOT_CAUSE_LAP414.md`(W10)다.

- [x] 2026-09-17 12:23 KST: "일단 그 세 부분 가능 여부를 더 확실하게 알아봐". G1/G2/G4 핵심 blocker를 구별하는 제한 실행 조사; G3 재개 없음. 계측 실패를 전체 목표 불가능으로 치환하지 않는다. 세 bounded 실행카드 종료·Sol검수 리포트 `docs/reports/20260917_THREE_GOAL_FEASIBILITY_UPDATE.md` 작성; 목표완료 아님.

- [ ] 2026-09-15 11:46 KST: "조금 조사한 뒤 안 될 것 같으면 빠르게 불가능하다고 보고하고,
  될 것 같으면 빠르게 작업에 착수"한다. 조사와 문서 자체를 목표로 삼지 않는다. 각 핵심 분기는
  짧은 feasibility 판정(`FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`)으로 끝내고, `FEASIBLE`이면 다음 work
  회차부터 구현·실행 증거를 만든다. `NOT_FEASIBLE`/`BLOCKED`이면 추측성 반복 대신 근거·대안·영향을
  사용자에게 즉시 보고한다.

- [ ] 2026-09-15 11:35 KST: "대목표 4개 중 완료 0개인데 왜 진행 속도가 이렇게 느린가".
  제품 구현보다 해시·스냅샷·시간경계 등 증거 하네스 자체 보수에 과도하게 머문 운영을 교정한다.
  Astra가 큰 방향을 재판단해 G1의 남은 실제 제품 판정을 최단 경로로 닫고, 독립 파일의 G2 구조
  조사를 함께 활성화한다. 이미 충분한 안전 근거가 있는 항목을 반복 검수하지 말고, 새 제품 증거를
  만드는 작업을 우선한다. 정확성·원본 보호·저장/메모리 안전은 계속 타협하지 않는다.

- [ ] 2026-09-10 23:06 KST: 실제 루프 시작. 10분마다 한국 시간과 함께 진행상황 보고.
  Astra/high 상위 전략 → Sol/high 중간 계획·컨펌 → Luna/high 실무 순으로 명시적 1바퀴씩 진행한다.
  자동 서비스/무한 실행/자동 커밋·푸시는 사용하지 않는다.

## 처리 완료

- [x] **2026-09-22 lap487 압축:** 이 섹션의 체크 완료 항목 전량(목표1~4 원문, 모델 역할, 환경세팅, 구조 이관, G3 중단 리포트, astra→fable 전환 2건)은 `docs/history/20260922_inbox_completed_section_lap487_archive.md`(SHA256 `ce6f8daeeda7f235d199dec62350614d2f2458b7ff2a8bd7b678b1eb7e1f8b90`, 34줄)에 **원문 그대로** 보존했다. 삭제 없음. 체크된 상시 요구는 계속 유효하며, 재참조가 필요하면 그 파일을 읽는다.

## 되물음

- [x] 2026-09-20 lap404 되물음 2건(일시 초과 표시 허용 / 전비 장부 16-bit 랩 마감) — **사용자
  2026-09-23 04:13 판정으로 종결**(lap404=(가)·F4=(B), APPROVALS 기록). N19·lap412 기전 확정·
  N68 재현 등 원문 45줄은 `docs/history/20260923_inbox_resolved_questions_lap505_archive.md`
  (발췌 SHA256 `329114042fbffe088b2a237182e52e5448b1376d75f5d5e5bfce102fb20c6077`)에 그대로 있다.
- [ ] 2026-09-21 lap458 work — **W23 A1 24k 연장 결과 `DECAYED` ⇒ (가) 자연 도달은 fixture/config
  축에서 NOT_FEASIBLE 확정.** 카드 `G2_A1_MAP_LEVER_LONG_WINDOW_LAP457.md` §4 고정 판정식대로
  W22 최유망 레버 A1(지도140×140)을 tick24,000까지 연장 실행한 결과, `r_late`(owner1,
  16k→24k)=0.008747 < `r_need`=0.033042(=(5000−U_min24 1,035)/120,000) ⇒ `DECAYED`.
  `U_min8`=661(owner5)로 W22 결정성 재확인, 무결성 위반 전부 0, 게임실행1회·source변경0·
  targeted7 passed·`SAFETY_PASS`. 카드가 예약한 대로 **모델은 AI/경로/생산 로직 변경에
  착수하지 않았고** 아래 되물음을 그대로 승격한다(고르지 않음, `G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md`
  §7 · `loop/ESCALATE_SOL` §36):
  - **(ㄱ)** 시딩 기반 cap 근접 + 왕복 증거(W21)를 G2 안정성 증거 축으로 인정하고 (가)를 재정의할지.
  - **(ㄴ)** G2 한정 최소 AI/설정 변경 허용 — 2026-09-21 00:20 G4 잠정 중단의 명시 예외 승인 여부.
  - **(ㄷ)** 현재 기준(자연 도달 요구) 유지, (가) 보류.
  이 3건은 바로 위 lap404 되물음(전비 장부 16-bit 랩 마감 방식)과 함께 사용자/strategy 판정
  대기 상태다. 상세 `docs/history/laps/20260921_lap458_work_g2_w23_a1_long_window_decayed.md`.
  - **2026-09-21 lap459 middle 독립검수 = ACCEPT(재계산 불일치 0)**, 위 원문 유지·선택지 미변경.
    원시 721표본만으로 비참조 재계산해 `U_min24`=1,035(owner1, tick24,012)·`r_late`=0.008747·
    `r_need`=0.033042·`DECAYED` 전부 일치, `U_min8`=661/owner5로 W22 결정성 정확 재현, 실행 **전**
    고정 기대 band 1,050~1,073 대비 실측 1,035(−1.4%).
    **판정 방향에 영향을 줄 신규 실측:** **(N81)** 정체 원인은 자원·cap·풀이 전부 아니다 — 최소
    rice 967,672/wood 969,464(지급 1,000,000의 **96.8%가 최악 시점에도 잔존**), `count` 최대
    108/1,200, `used` 최대 1,708/5,000 ⇒ **AI가 자원을 거의 손대지 않은 채 스스로 생산을 멈춘다.**
    **(N82)** 부드러운 감쇠가 아니라 owner별 **완전 정지** — owner5는 tick14,641 이후 런의 39.0%
    동안 `used` 불변(`r_late` 정확히 0.0), owner7 31.8%, owner6 15.4%.
    ⇒ 두 실측은 **(ㄴ)이 유일하게 남은 기술적 진입로**임을 시사하나, 이는 사용자 지시
    (2026-09-21 00:20)의 명시 예외 승인이므로 **모델은 착수하지 않고 승인을 기다린다.**
    **(N83) 경고:** 이 run은 바로 위 lap404 되물음에 **새 증거를 주지 않는다** —
    `used+reserved>5000` 0건(아무도 cap 근처에 못 감)이라 N68 현상이 발생할 수 없다.
    **(N84) 표현 정정:** "전 owner 감쇠"는 과장 — owner0(0.04498)·owner2(0.03749)는 `r_need`를
    후반에도 넘는다. 판정이 유지되는 이유는 G2가 "8인 **각각** 5,000"이라 최저 owner가 구속
    조건이기 때문이다. 정확한 서술은 "8인 합계가 24k에서 11,207 = 8×5,000의 **28.0%**".
    상세 `docs/history/laps/20260921_lap459_middle_g2_w23_a1_independent_review.md`.
  - **2026-09-21 lap460 strategy(Fable5) 처분(`ESCALATE_SOL`§38, 원문 보존·사용자 번복 가능):**
    **(ㄱ) 채택·(ㄷ) 기각** — G2 원문 계약은 "cap5000 플레이 안정"이므로 gate-legal 시딩
    cap근접+soak+왕복을 증거 축으로 인정(마일스톤 승인 대체 아님, 자연 도달 계속 요구 시 번복).
    **(ㄴ)은 모델이 고르지 않고 사용자 승인 대기 유지**(승인 전 AI/설정 변경 착수 금지).
    lap404는 **(가) 잠정 채택**(stock cap5000 `reserved` rider probe를 W24에 의무화, 미재현 시
    회귀 승격·재심). F4는 **(C) 채택**(soak에서 랩/음수 관측 시 즉시 STOP 후 (B) 재심). 다음은
    middle이 **W24**(혼합 구성+전투/사망/재사용 순환 24k) 1장 발행, **144k 금지는 W24 ACCEPT까지 유지**.
  - **2026-09-21 lap461 middle 신규 실측 N87 — (ㄴ)의 무게가 커졌다(선택지 미변경, 모델은 고르지 않음):** lap448에서 8 owner의 배치 주사 구간은 전 쌍에서 겹쳐(2-3 501셀·6-7 484셀 등) 적 유닛이 24,000tick 내내 셀 단위로 인접했는데도 소실은 **4기/1,166기**뿐이었다 ⇒ "전투/사망/슬롯 재사용" 축도 **기하(fixture)로는 만들 수 없음**이 실측됐고, 남은 fixture 내 가설은 구성(타입) 하나뿐이다. 그것마저 실패하면 자연 도달에 이어 **전투 축까지 (ㄴ) 승인 없이는 닫히지 않는다.** W24는 그 결과를 `NO_ENGAGEMENT`로 정직하게 보고하도록 실행 전에 고정했고 **승인 전 AI/생산 정책 변경에는 착수하지 않는다.** 근거 `docs/history/laps/20260921_lap461_middle_g2_w24_issue_and_combat_axis_finding.md`·`ESCALATE_SOL`§39.

실제 구현 선택이 목표·안전·배포 범위를 바꿀 때만 새 질문을 추가한다.

## 2026-09-17 15:20 KST — G2 최우선 루프 재개
- [x] 사용자: "8인 각각 전비 5000 안정 플레이 이걸 최우선 목표로 좀 파보자. 루프 ㄱㄱ". 큐/우선순위 반영(제품완료 아님). G1/G4 후순위, G3중단 유지.

## 2026-09-17 21:16 KST — 사용자 루프 시간 상한
- 사용자: “한국시간 기준12시까지만 루프 돌릴거야. 이후는 진행속도나 가능성 생각해서 볼테니까 그거 생각해서 진행해봐”.
- 현재21:16이므로 Root는 **오늘밤자정2026-09-18 00:00KST**를 보수상한으로 잡았다고 사용자에게 명시했다. 정오를 뜻한 경우 정정 대기; 답변전에는 더짧은상한 유지.
- 10분마다KST보고, 상한에서신규작업중단/ownedcleanup/성과·가능성정리. 기존 STOP 예산리셋·목표축소·제품승인 아님.

## 2026-09-18T17:56:55.515225+09:00 — Claude Code 전환 및 루프 재개
- 사용자: “ㅇㅇ 그렇게 가보고 루프 다시 돌려”. 중간계획/검수ClaudeCode Opus5/high, 실무ClaudeCode Sonnet5/high, 큰분기Astra medium(필요high) 유지. 새명시재개는어제00상한종료이후재개허가이며원제품목표/원본안전/실패보존유지. 이전STOP기술카드예산자동리셋/제품승인아님. 10분KST보고 유지,서비스/커밋/자동push안함.

## 2026-09-21 종결 계보 3건 (2026-09-23 압축 — 원문 전량 보존, 삭제 없음)

lap423·429·438·440·442 운영 회수 계보 / lap425·427·428 계보 / Root 회수 lap448 W21 Step1 24k soak —
세 섹션 전문은 `docs/history/20260923_inbox_closed_lineages_lap500_archive.md`
(SHA256 `5f62ae8d7922d393f0bb6211719dbce8b7f192363bb93e30259f8cbf053d3e50`, 36줄)에 그대로 있다. 전부 종결된 계보이며 재참조 시 그 파일을 읽는다.
