# INBOX 압축 보존 — 2026-09-23 12:55 지시의 lap509~lap521 진행 추기 (lap522 strategy)

- 원본: `docs/feedback/INBOX.md` 28~110행(압축 직전 INBOX 전체 SHA256 `9da47ddf39f7b8a454adb78d92eac1d9b5eeb2d5ee4075b0cfda8f2e3e68b871`, 347줄).
- 발췌 SHA256 `71400fe35cb4d8768bbd2ac66fcff673345ff72d07846adb68cf3dad9e80ab5b`, 83줄. 아래 구분선 사이가 발췌 원문 그대로다(삭제·재해석 없음).
- 압축 사유: 두 트랙(① F4(B) W30, ② 건설 선택 로직 W31~W33)이 모두 `CLOSED`(lap514·lap521)인 종결 계보. 지시 원문(12:55)은 INBOX에 남겼다.

----- BEGIN EXCERPT -----
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
  **lap519(middle, Opus5.5): W32 독립 검수 ⇒ `CLOSED`.** 재집계 불일치는 0/8이다. 반증조건②는 카드 반증식의 결함이었다(N168).
  건설 오더는 두 번째 호출의 **상태2 `0x43E174`**에서 약 70%가 발부 없이 끝난다(N170). 실패율은 선택 종에 따라 1/66~12/14로 갈린다(N171).
  **"왜 느리나"의 답은 "상태2에서 대부분 실패"로 좁혀졌다.** 다음 work는 W33(`G2_BUILD_STATE2_EXIT_PROBE_LAP519.md`)으로
  두 종료 분기(`0x43E252`/`0x43E2D8`)를 가린다. 로직 변경 여부는 사용자 전결이다. 근거
  `analysis/memory_maps/ai_build_order_state2_loss_lap519_20260923.md`, `ESCALATE_SOL` §77.
  **lap520(work, Sonnet5): W33 M-0 완료(8/8 PASS, S2L §3 미반증)·M-1 `UNRESOLVED_STATIC_ONLY`.**
  EXIT_A(`0x43E252`)는 사이트 소유권 맵+랜덤으로 **종-무관**, EXIT_B(`0x43E2D8`)는 `AFDD0(edi,kind,...)` 후보 평가로
  **종-의존**임을 바이트로 확정했으나, 그 종-의존 파라미터(`0x9B5228+kind*0x394+0x16/+0x18`)가 원본 `.exe`의 `.data`
  raw 범위 밖(런타임 전용)이라 순수 정적 신호는 kind41 반경 오버라이드 1종뿐 ⇒ 카드 기준(≥12/14) 정적만으로 도달 불가.
  신규 필드 `+0x3A74`(EXIT_B 전용 마커) 발견. 경량 M-2(24k 소크 아닌 `read_type_specs()` 확장 PS3 단발 스냅샷)로
  충분함을 확인했으나 이번 라운드는 미실행(시간 확신 부족). **실행 증거 무증가 lap519·520 연속 2회째 ⇒ 카드 §5대로
  다음은 strategy/middle이 트랙② 지속 여부를 먼저 판정한다.** 게임실행0·source변경0·커밋0. 근거
  `analysis/memory_maps/ai_build_state2_exit_decode_lap520_20260923.md`, `ESCALATE_SOL` §78.
  **lap521(middle, Opus5.5): W33 `CLOSED`, 트랙② 진단 종료 ⇒ STOP(사용자 응답 대기).**
  - 배치 실패는 건물 크기(footprint 3×3)와 조선소 전용 배치 검사(41/56/68)로 대부분 설명된다(11~12/14, 사후 임계라 라벨 없음).
  - 참고 캡처로 정적 확인했고 "런타임에만 있다"는 lap520 전제는 정정했다(N172~N176).
  - 두 트랙이 모두 끝나 남은 G2 진행은 전부 사용자 전결이다. (ㄴ)을 고르면 분기 계수 probe(W34 초안)를 먼저 할지도 함께 정한다. 근거 `ESCALATE_SOL` §79.
----- END EXCERPT -----
