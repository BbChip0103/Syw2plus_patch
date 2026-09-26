# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**. 제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따른다.
과거 lap275~501 계보와 이번 압축 직전 STATUS 전문은 `docs/history/20260923_status_lap502_precompaction.md`(SHA `a2a12dad6c95e688f8290d783b1bc63e4ad3373090de81ffd4766b57d2f1a0ec`, 130줄)에 그대로 있다(그 안에 lap501·lap500 precompaction 스냅샷 포인터가 연쇄 보존됨).
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
| G2 | W26(144k) `CLOSED`·종합 `CAP_PROXIMITY_STABLE_144K`(부분 증거), Q7 3단 마일스톤 회부 대기. **lap507 W29 실행 + lap508 독립 재계산 `ACCEPT`(불일치 0/8) ⇒ 2단 성립: k=8 `NATURAL_ARRIVAL_ARITH_INFEASIBLE`. 자연 도달 불가는 owner 종단 스냅샷이 아니라 fixture 전체 AI 건설 레퍼토리(27종 중 9종만 건설, 합집합 천장 2,835)에서 온다. H-CROWD UNKNOWN 유지. §67 예산 소진 ⇒ Q8 사용자 응답 대기 STOP.** 제품 미완료 | lap356~502 계보는 precompaction 스냅샷과 `docs/history/laps/`에. 상세는 아래 「검증 상태」 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
## 다음 한 가지
**2026-09-23 12:55 사용자 지시로 Q8 대기를 풀고 두 트랙을 순서대로 진행한다(G2 자연도달 축은 계속 대기).**
**lap509 middle이 트랙① F4(B) 카드 W30을 발행했다** — `docs/work/active/G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md`.
**다음 한 가지: work(Sonnet5)가 W30을 소비한다.** M-0(PlayerStruct `[0,0x3ABC)` 안 **4바이트 구멍 맵**:
정적 미참조 + 8 owner 런타임 상수성)을 먼저 끝내고 안 A(구멍으로 `used` 이전)/B(`+0x200e` 이사 후
제자리 확장)를 고른 뒤 `patches/population/supply_ledger_32bit.py` + 회귀 테스트로 M-b~M-h를 기계로
고정한다. **A·B 둘 다 실패하면 `BLOCKED` 보고이며 C(stride 변경)로 넘어가지 않는다**(lap385 blocker).
**카드 범위는 lap509가 원본 전수 스캔으로 정정했다 — 5곳이 아니라 9곳**(아래 「검증 상태」 N154).
원본 읽기 전용·새 복사본만 패치·정확한 원복·회귀 테스트는 AGENTS.md 그대로.
**그다음 트랙: 건설 선택 로직 분석**(읽기 전용, (ㄴ) 불필요) — 27종 중 18종 미건설 원인,
`FUN_00406C70` 추첨 로직 + H-CROWD 채널 주소 정정이 시작점.
**미결(사용자 전권): Q9(12:55 ③ 실행검증 제외가 F4 후보까지인가, §70) · Q8((ㄱ)/(ㄴ)/(ㄷ)) ·
Q7-B 3단 마일스톤 · "8인"이 사람인지 AI인지.**
## 지금 막힌 것 (Blockers)
- **F4 안전상한: lap509가 숫자로 닫았다(N156) ⇒ blocker 아님, W30으로 이관.** lap395는 donor
  이전 펌프로 cap 1500/4095/5000 전부에서 수신 `used` 32,785 도달을 실측하고 상한을 UNKNOWN으로
  남겼다. lap509가 `roster_add`(`0x43EE30`)가 cap을 안 보고 `cmp ax,0x4b0`(로스터 1,200칸)만
  건다는 것과 `c_max=65`(lap507)로 **구조적 최대 `used` = 1,200×65 = 78,000 > 32,767**을 확정
  ⇒ 16-bit 랩은 **구조적으로 가능**(32,785 실측과 정합), 32-bit에선 **구조적으로 불가능**.
  **실제 게임 도달성은 여전히 UNKNOWN**이며 이 수치는 산술 상한일 뿐이다.
- **N141/N145(lap498 제기·lap500 정정): fixture 내 G2 "실제 플레이" 경로가 소진됐다.** 자연도달
  `NOT_FEASIBLE`(W23 A1) + 전투 축 기하로 생성 불가(N87) + 건물 계층 부재(W26 §0-3) + 시딩 축
  장기 정체. "완전 정지"는 lap500에서 창 절단으로 강등(같은 결정적 궤적의 연장에서 5 owner 재개).
  종단 여부를 가리려면 (ㄱ) 창 연장(≳200k)·(ㄴ) 다른 seed/구성·(ㄷ) (ㄴ)-승인 변경 중 하나 필요,
  셋 다 사용자/strategy 전결.
- **G2 구조통합 blocker(owner당1200 초과·저장호환 확장):** 저비용 다수 구성 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·저장/LAN 일관 계약이 미구현. 상세는 precompaction 스냅샷.
- **lap508 신규(lap504 blocker 대체, 전문 §69):** ① **N151** — 8 owner 보유 건물 종 **합집합**
  {41,44,45,46,47,49,50,51,105}(27종 중 **9종**)을 한 owner가 다 가져도 천장 **2,835<5,000**,
  18종은 이 fixture에서 **아무도 짓지 않았다** ⇒ 불가능의 근원은 **AI 건설 레퍼토리**.
  ② **N152** — 5,000 돌파엔 **7종이면 충분**(45→64→53→61→65→67→46=5,072)인데 관측 owner는 이미
  6~8종 보유 ⇒ 병목은 개수가 아니라 **고가치 종(64·53·61·65·67) 미건설**. ③ **N153** — tick
  18,000 이후 6/8이 생산 중(owner4는 최종표본 증가) ⇒ "전원 정지"는 owner5 국소현상 일반화였고
  lap501~504 "AI 생산 정지" 계보의 전제가 흔들린다. ④ **미설명 잔여**: owner7은 천장 대비
  **56.3%**에서 7,600틱 정지 — H-TYPEMAX 포화로 설명 안 됨. ⑤ **N147** H-CROWD는 주소 정정이
  지지될 뿐 게이트 연결 미해독 ⇒ **UNKNOWN 유지**. 이들이 Q8 선택지의 전제를 바꾼다(§69 5항).
- G1/G4 개별 blocker(R1/S1 클릭·좌표 포렌식, AI runtime 실패 등)는 전문 그대로 precompaction 스냅샷과 `docs/history/laps/`에 보존되며 G2 성립 전까지 작업 대상이 아니다.
## 검증 상태
**2026-09-23 lap509(middle, Opus5) — F4(B) 카드 W30 발행 + 착수 전 범위 정정 2건 + 안전상한 closure**
(전문 `docs/history/laps/20260923_lap509_middle_f4b_card_issue.md`, 근거
`analysis/memory_maps/g2_supply_ledger_200c_site_inventory_lap509_20260923.md`, 회부 §70).
원본 `b56986e0…`를 **직접 전수 디스어셈블**(306,187 명령)해 카드를 쓰기 전에 범위를 독립 확인했다.
**N154 — 범위는 5곳이 아니라 9곳이다.** `+0x200c`를 만지는 명령은 base+disp **5곳**(`0x43EDFC` read·
`0x43EE9B` **add**·`0x43EF8B` **sub**·`0x43F0E9` read·`0x43F3B3` HUD read) + 절대주소 별칭 `0x95877C`
**4곳**(`0x40DD12`·`0x40E03B`·`0x499767`·`0x499A0E`, 전부 게이트 read)이다. STATUS가 `+0x200c`
reader로 적었던 `0x43EE03`/`0x43F0F3`/`0x43F43F`는 **전부 `+0x2012`(supply_limit) 읽기**로,
`hero_limit_supply_patch_sites_20260921.md`의 정확한 원문이 STATUS 전사 중 필드가 뒤바뀐 것이다.
**절대주소 4곳은 어떤 기존 범위 서술에도 없었다** — 그대로 착수했으면 게이트 4곳이 16-bit로 남았다.
**N155 — "저장포맷 변경 동반"은 전제가 아니다.** bulk save/load는 고정 길이 raw span
`[0x892410,0x975D8C)`=**932,220B**를 통째로 다루고(save `0x440F02`/load `0x4412D2`, 즉시값 동일)
PlayerStruct 배열이 그 안에 포함된다 ⇒ **stride `0x3ABC` 보존 시 저장 파일 길이·레이아웃 불변**,
호환은 *포맷*이 아니라 **2바이트 값 해석** 문제. ⇒ lap393 D절의 "work 단독 착수 금지" **부분 해소**
(stride 변경 경로는 계속 금지). **N156**은 위 Blockers 참조.
재현 probe `…/probes/20260923_lap509_middle_supply_ledger_site_inventory.py` exit 0·단언 **7/7 PASS**,
산출물 `site_inventory.json` SHA `f9d05771…`. 게임실행0·제품source변경0·커밋0·**796 passed**·
`SAFETY_PASS`·`CONTEXT_PASS`. **middle 자기 결과 — W30 소비 결과는 다음 새 middle이 독립 검수한다.**

**2026-09-23 lap508(middle, Opus5) — W29 독립 재계산 = 집계 `ACCEPT`(2단 성립) · 단서 정정 3건**
(전문 `docs/history/laps/20260923_lap508_middle_w29_independent_recalculation.md`, §69).
`ceiling_table.json`의 `ceiling`/`per_kind`/`sum_typemax`/`k`/`theoretical_max`를 **쓰지 않고**
`type_specs.json`+`production_table.json`만으로 재계산 ⇒ **owner 8/8 불일치 0**(천장 벡터·
`per_kind` 전항목·Σtypemax·k=8·이론최대 8,077 전부 재현), 카드 §1 조건(`cost[27]+cost[76]=20`,
`cost[80]=0`) 일치, `samples.jsonl` 교차 대조 불일치 0. **신규 반증시험: 721표본×8owner에서
live `used`>재계산 천장 = 0건** ⇒ 천장 모델 미반증. 라벨 `NATURAL_ARRIVAL_ARITH_INFEASIBLE` 유지.
**정정:** **N151** 보유 건물 종 합집합(9/27)의 천장도 **2,835<5,000**, 18종 미건설 ⇒ 불가능은
"현 종단 구성"이 아니라 **fixture 전체 건설 레퍼토리**에서 온다(카드 단서는 보수적이었다).
**N152** 5,000엔 **7종이면 충분**한데 관측은 이미 6~8종 보유 ⇒ 병목은 개수가 아니라 **고가치
종 미건설**. **N153** tick18,000 이후 6/8 생산 중(owner4 최종표본 증가, 정지는 owner5·owner7뿐)
⇒ "전원 정지"는 **owner5 국소현상 일반화**(lap500 N145 창절단을 owner단위로 재확인). 부수:
`used`는 라이브 장부(owner0·6에서 −20/−2 감소) ⇒ 고정을 곧장 "생산 정지"로 읽으면 안 된다.
**잔여 UNKNOWN:** owner7 56.3%에서 정지(H-TYPEMAX로 설명 안 됨) · `building_kinds_owned`는
단일 출처(교차검증 불가, 단 `used_final` 8/8이 천장 이하라 정합). 게임실행0·source변경0·커밋0·
796 passed·`SAFETY_PASS`·`CONTEXT_PASS`.

**2026-09-23 lap507(work, Sonnet5) — W29 실행 = `PROBE_OK`**(lap508이 독립 재계산으로 검수 완료).
lap506이 남긴 스크립트(background+세션종료로 4회째 죽음)를 **수정 없이** 재실행, Monitor로 세션을
끝내지 않고 tick24,029 완주. 천장 [2445,1070,2445,2050,2445,1190,2050,2445]·k=8·이론최대 8,077·
`c_max=65`. 게임실행1·source변경0·커밋0·`SAFETY_PASS`. 전문 `…/20260923_lap507_work_w29_used_ceiling_probe.md`,
근거 `analysis/memory_maps/g2_kind_supply_cost_table_lap507_20260923.md`, §68.

**lap501~504 계보(lap509 압축, 전문은 각 원 lap 기록과 §64~§66에 그대로):** lap501(middle) 정적
추적으로 `FUN_00406770`→`FUN_00406B00`→`FUN_0043E7F0`/`FUN_00406C70` 경로 바이트 확정(자원 게이트
**0개** ⇒ "자원 96.8% 잔존+정지"는 정상 동작) → lap502(work) §7 런타임 probe = UNEXPLAINED 8/17쌍
`UNKNOWN` → lap504(middle) 독립 재계산 **집계 ACCEPT(불일치 0/1,258)** + 해석 반증 **N147**(H-CROWD
채널 전부 0 ⇒ 실질 5게이트)·**N148**(UNEXPLAINED 2쌍이 tick14,624/16,794에 실제 생산 ⇒ "9번째 영구
게이트" 반증, `FUN_00406C70` 카드 미발행)·**N149**(`used` 동결은 H-TYPEMAX 포화의 착시)·**N150**
(구속조건은 typemax×보유 건물 종 수, `used` 천장 ≈2,030 **평균 기반 추정**). lap508 N151~N153이
N150의 추정을 실측으로 대체하고 lap502의 전제(owner5=전체 대표)를 반증했다. 전 회차 게임신규실행0·
source변경0·커밋0.

**lap356~500 계보(수치·판정 전문은 precompaction 스냅샷 연쇄와 각 원 lap 기록에 그대로):**
W26 144k soak `CLOSED`(lap497~499) → N141 재현성 판정(lap500, `N141_REPRODUCED`이나 N144로
독립재현 부정·N145로 종단여부 UNKNOWN 강등) → Q7 strategy 처분(lap499: Q7-B 잠정채택·Q7-A
사용자전결) → lap356~496(W8~W27 soak/케이던스/판정기 수리/fixture축 소거, Step A~D rider 계보).
전 회차 제품코드/커밋 전부0.
## 바퀴 기록
lap509(middle, Opus5) F4(B) 카드 W30 발행 + 착수 전 범위 정정 **N154**(5곳→**9곳**, 절대주소 별칭
4곳 누락)·**N155**(stride 보존 시 저장포맷 변경 불필요)·**N156**(안전상한 78,000으로 closure).
제품증거 무증가 회차 ⇒ **다음은 반드시 work 구현 회차**. 게임실행0·source변경0·커밋0·796 passed·
`SAFETY_PASS`·`CONTEXT_PASS`. 전문 `20260923_lap509_middle_f4b_card_issue.md`, 회부 §70.
lap508(middle, Opus5) W29 독립 재계산: 집계 **ACCEPT**(owner 8/8 불일치 0, 2단 성립)·라벨
`NATURAL_ARRIVAL_ARITH_INFEASIBLE` 유지 + 신규 반증시험 0건 + **단서 정정 N151~N153**(합집합
천장 2,835·7종이면 충분·6/8 아직 생산 중). **§67 예산 소진 ⇒ STOP**(Q8 사용자 응답 대기).
게임실행0·source변경0·커밋0·796 passed·`SAFETY_PASS`·`CONTEXT_PASS`. 전문
`20260923_lap508_middle_w29_independent_recalculation.md`, 회부 `ESCALATE_SOL`§69.
lap507(work, Sonnet5) W29 실행: lap506 스크립트 수정없이 재실행(Monitor로 완주까지 대기, 4연속
background-kill 패턴 미재현) → `PROBE_OK`·k=8. 게임실행1·source변경0·커밋0·`SAFETY_PASS`.
전문 `20260923_lap507_work_w29_used_ceiling_probe.md`, §68.
lap505(strategy, Fable5) Q8 처분: **CONTINUE·예산 한정** + **W29 발행** + INBOX 압축. §67.
lap501·502·504 계보(lap509 압축): 정적 추적(§64) → §7 런타임 probe `UNKNOWN`(§65) → 독립 재계산
**ACCEPT**+반증 N147~N150·Q8 회부(§66). 전문은 각 `20260923_lap50{1,2,4}_*.md`.
(lap501~509 전 회차 제품코드/커밋 0, 게임실행은 lap507만 1.)
lap356~500 계보(압축, 전문은 precompaction 스냅샷 연쇄와 각 원 lap 기록에): lap500(middle) N141
재현성+N144/N145/N146 → lap499(strategy) Q7 처분 → lap498(middle) W26 독립검수 ACCEPT·`CLOSED`
→ lap497(work) W26 144k soak 완주 → lap356~490(W8~W27 soak/케이던스/판정기 수리 계보).
전 회차 제품코드/커밋 전부0(lap491·495·497만 게임실행1, source변경0).
