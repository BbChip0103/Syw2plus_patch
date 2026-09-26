# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**. 제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따른다.
과거 lap275~501 계보와 이번 압축 직전 STATUS 전문은 `docs/history/20260923_status_lap502_precompaction.md`(SHA `a2a12dad6c95e688f8290d783b1bc63e4ad3373090de81ffd4766b57d2f1a0ec`, 130줄)에 그대로 있다(그 안에 lap501·lap500 precompaction 스냅샷 포인터가 연쇄 보존됨). lap511 압축 직전 전문은 `docs/history/20260923_status_lap511_precompaction.md`(SHA `d64990c025fb131a10f041f873d0a05303b49388d744cf92bb3084e0857ca805`, 125줄). lap519 압축 직전 전문은 `docs/history/20260923_status_lap519_precompaction.md`(SHA `6060035cf4d5da53e489d1e69d4850cddc44bb76049907b29f80d2942786c520`, 138줄).
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
| G2 | W26(144k) `CLOSED`·종합 `CAP_PROXIMITY_STABLE_144K`(부분 증거), Q7 3단 마일스톤 회부 대기. **lap507 W29 실행 + lap508 독립 재계산 `ACCEPT`(불일치 0/8) ⇒ 2단 성립: k=8 `NATURAL_ARRIVAL_ARITH_INFEASIBLE`. 자연 도달 불가는 owner 종단 스냅샷이 아니라 fixture 전체 AI 건설 레퍼토리(27종 중 9종만 건설, 합집합 천장 2,835)에서 온다(**lap515 N158 정정: 레퍼토리가 아니라 진영 블록+건설 속도**). H-CROWD UNKNOWN 유지. §67 예산 소진 ⇒ Q8 사용자 응답 대기 STOP.** F4(B) 장부 폭 확장 카드 W30은 **lap514 middle 독립 재계산 `ACCEPT` ⇒ `CLOSED`**(정적+단위+원복+원본 hole 런타임까지; 후보 EXE 실행 0·Q9 미결 ⇒ 제품 근거 아님). 제품 미완료 | lap356~502 계보는 precompaction 스냅샷과 `docs/history/laps/`에. 상세는 아래 「검증 상태」 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
## 다음 한 가지
**2026-09-23 12:55 사용자 지시로 Q8 대기를 풀고 두 트랙을 순서대로 진행한다(G2 자연도달 축은 계속 대기).**
트랙① F4(B) 카드 W30 `docs/work/active/G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md` **`CLOSED`(lap514, 카드 §9)**:
후보 SHA `1893ff50…`(15곳·diff 66B). 후보 EXE 실제 실행 0(Q9 미결) ⇒ 제품 근거 아님. 구세이브 미지원(신규 게임 전용).
트랙② W31 `CLOSED`(lap517) → W32 lap518 `PROBE_OK`·`MODEL_REFUTED` → **lap519 middle 독립 검수 ⇒ W32 `CLOSED`**:
재집계 불일치 0/8. 반증조건②는 카드 반증식 결함이다(N168: 표본이 시작+8 호출 뒤에 찍힘, 선택 직후 표본 352/354는 `+0xD32==1`).
**손실 단계 = 두 번째 호출의 상태2 `0x43E174`**(gap 8~15 334건 중 69.8% 종료·발부 0, N170). 종별 발부율은 1/66~12/14(N171).
lap520(work) W33 M-0/M-1 → **lap521(middle, Opus5.5) 독립 검수 ⇒ W33 `CLOSED`(라벨 미부여)**.
- M-0 뼈대는 ACCEPT다. EXIT_A는 종-무관이다.
- 정정 N172~N176: `0x4A4E70`이 kind를 받고 41/56/68 조선소 술어 `0x4A4BF0`가 있다. `+0x16/+0x18`은 footprint다.
  참고 캡처 `d7bf3e1f…`가 런타임과 152/152 일치하므로 M-1 "정적 불가" 전제는 REJECT다. `+0x3A74`는 sticky라 카운터로 쓸 수 없다.
- footprint 예측은 11/14·12/14이고 반례는 50·105다. 임계가 사후라 라벨을 부여하지 않았다.
**트랙② 지속 판정(무증가 3회째 경계, middle): 진단 `CLOSED`, 자동 계속하지 않는다.**
- 두 트랙이 모두 `CLOSED`라 남은 G2 진행은 전부 사용자 전결이다. 따라서 **STOP**(PROMPT ④6)이며 상위 확인은 `ESCALATE_SOL` §79에서 받는다.
- (ㄴ)을 고르면 W34(하드웨어 breakpoint 분기 계수 24k 1회) 초안을 쓸 수 있다. §79에 있으며 아직 발행하지 않았다.
- 근거: `analysis/memory_maps/ai_build_state2_footprint_review_lap521_20260923.md`.
**미결(사용자 전권): Q9(12:55 ③ 실행검증 제외가 F4 후보까지인가, §70) · Q8((ㄱ)/(ㄴ)/(ㄷ)) ·
Q7-B 3단 마일스톤 · "8인"이 사람인지 AI인지.**
## 지금 막힌 것 (Blockers)
- **F4 안전상한: lap509가 숫자로 닫았다(N156) ⇒ blocker 아님, W30으로 이관.** lap395는 donor
  이전 펌프로 cap 1500/4095/5000 전부에서 수신 `used` 32,785 도달을 실측하고 상한을 UNKNOWN으로
  남겼다. lap509가 `roster_add`(`0x43EE30`)가 cap을 안 보고 `cmp ax,0x4b0`(로스터 1,200칸)만
  건다는 것과 `c_max=65`(lap507)로 **구조적 최대 `used` = 1,200×65 = 78,000 > 32,767**을 확정
  ⇒ 16-bit 랩은 **구조적으로 가능**(32,785 실측과 정합), 32-bit에선 **구조적으로 불가능**.
  **실제 게임 도달성은 여전히 UNKNOWN**이며 이 수치는 산술 상한일 뿐이다.
  **lap511 N157:** W30 안 A 구멍(`+0x2100`)은 1,000칸 리스트 안이라 기각 — 안 B(`+0x2016`)가 마지막
  PlayerStruct 내 경로이며, 실패 시 `BLOCKED`(C 금지, PlayerStruct 밖 배치는 middle/strategy 판정 필요).
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
  **lap515 정정(N158~N161, §73, 2단 검수 전):** ①의 18종은 일본9+명9 **진영 블록**(fixture 전원 조선) ⇒ "레퍼토리"가 아니라
  조선 생산 건물 9/9 전부 건설. ②의 7종 경로는 3진영 혼합이라 단일 AI 불가. 단일 진영 유닛 천장 조선2,835·일본2,527·명2,715.
  건물도 `used`에 들고 건물 수는 typemax×N/6로 자라 조선 5,000 = 건물 ≈160채 필요, 관측 11~20채·건설 진행 중 ⇒ 병목은 **건설 속도**.
  **lap517(N164/N167):** 건설 오더는 스케줄러 `0x43F5D0`의 1/20 롤·100 tick 쿨다운으로만 시작(천장 ≈91/24k), 관측은 그 10~20% ⇒
  손실 단계(타 오더 점유/부지·일꾼 실패/완공 전 소실)는 W32 판별 전까지 UNKNOWN.
  **lap519(N170/N171):** 손실은 상태2 `0x43E174`에서 약 70%(점유·쿨다운·완공 아님)다.
  **lap521(N172~N174):** 두 종료 분기가 갈린다. EXIT_A는 사이트 후보 0개로 종-무관이고, EXIT_B는 footprint·조선소 술어에 걸린 배치 실패로 종-의존이다. 실측 비율은 UNKNOWN이다.
- G1/G4 개별 blocker(R1/S1 클릭·좌표 포렌식, AI runtime 실패 등)는 전문 그대로 precompaction 스냅샷과 `docs/history/laps/`에 보존되며 G2 성립 전까지 작업 대상이 아니다.
## 검증 상태
**2026-09-23 lap521(middle, Opus5.5) — lap520 W33 독립 검수: M-0 ACCEPT·N172~N176·M-1 전제 REJECT ⇒ W33 `CLOSED`, 트랙② 진단 종료·STOP**
- 전문: `docs/history/laps/20260923_lap521_middle_w33_independent_review.md`.
- probe: B1~B7 PASS, 산출 `00af62eb…` 2회 동일. lap520 probe `899db3f9…`를 재현했다.
- 게임실행0·source변경0·커밋0. `make check` exit0 **819 passed**·`SAFETY_PASS`·`CONTEXT_PASS`.

**2026-09-23 lap519(middle, Opus5.5) — lap518 W32 독립 검수: 재집계 ACCEPT(0/8)·반증조건② 카드 결함(N168)·손실=상태2(N170) ⇒ W32 `CLOSED`, W33 발행**
(전문 `docs/history/laps/20260923_lap519_middle_w32_independent_review.md`, 근거 `analysis/memory_maps/ai_build_order_state2_loss_lap519_20260923.md`,
probe 12/12 PASS·산출 SHA `8f22385b…` 2회 동일, P5·P6·O3·O4는 사후 항목으로 명시). 자기 실행 전 가설(같은 호출 선택 실패)은 2/354라 기각(N169).
게임실행0·source변경0·커밋0. `make check`/safety는 바퀴 기록 참조.

**lap518(work) W32 `PROBE_OK`·`MODEL_REFUTED`(lap521 압축).** 전문은 `docs/history/20260923_status_lap521_precompaction.md`(SHA `b05e5b60…`, 124줄)와 lap518 기록에 그대로 있다.
게임실행1(24,005tick)이다. 반증조건②는 lap519 N168로 카드 결함임이 판정됐다.

**lap513~517 계보(lap519 압축, 전문은 `docs/history/20260923_status_lap519_precompaction.md`(SHA `6060035c…`)·각 lap 기록·§72~§75에 그대로):**
lap513(work) W30 안 B 24k `HOLE_CONSTANT` → lap514(middle) ACCEPT ⇒ W30 `CLOSED` → lap515(middle) 진영 블록 N158~N161·W31 발행 →
lap516(work) W31 `UNCLASSIFIED` 8/8 → lap517(middle) M-2 ACCEPT(0/8)·N162~N167(스케줄러 `0x43F5D0` 해독) ⇒ W31 `CLOSED`, W32 발행.
근거 `analysis/memory_maps/`의 `g2_supply_ledger_holeb_acceptance_lap514`·`ai_build_faction_gate_0043dbb0_lap515`·`ai_build_pace_state_probe_lap516`·
`ai_build_order_scheduler_0043f5d0_lap517`. 게임실행은 lap513·516 각 1, source변경0·커밋0.

**lap510~511 W30 안 A 계보(lap515 압축, 전문은 `docs/history/20260923_status_lap515_precompaction.md`
(SHA `eee576e00739e1476fd37e45902b7de9845f139027d65715394dccbc16d4ad45`, 132줄)과 각 원 lap 기록·§71에 그대로):** lap510(work)
안 A `+0x2100` 패처 → lap511(middle) **N157** 구멍 REJECT(`+0x2018` 1,000칸 리스트 58번 칸)·기계부 ACCEPT·안 B 입력(`+0x2016`) 발행.

**lap507~509 계보(lap511 압축, 전문은 precompaction 스냅샷 `…lap511…`·각 원 lap 기록·§68~§70에 그대로):**
lap507(work) W29 `PROBE_OK`(tick24,029, 천장 [2445,1070,2445,2050,2445,1190,2050,2445]·k=8·이론최대 8,077·
`c_max=65`) → lap508(middle) 독립 재계산 **ACCEPT**(불일치 0/8, 반증시험 0건) + **N151**(보유 종 합집합
9/27 천장 2,835<5,000 ⇒ 근원은 AI 건설 레퍼토리)·**N152**(7종이면 충분, 병목은 고가치 종 미건설)·
**N153**(tick18,000 이후 6/8 생산 중) → lap509(middle) W30 발행 + **N154**(`+0x200c` 범위 9곳, 절대주소
별칭 `0x95877C` 4곳 포함; `0x43EE03`/`0x43F0F3`/`0x43F43F`는 `+0x2012` 읽기)·**N155**(bulk span
`[0x892410,0x975D8C)`=932,220B 고정 ⇒ stride 보존 시 저장 길이·레이아웃 불변, 호환은 값 해석 문제)·
**N156**(구조적 최대 `used` 78,000). 잔여 UNKNOWN: owner7 56.3% 정지, H-CROWD. 전 회차 source변경0·커밋0.

**lap501~504 계보(lap509 압축, 전문은 각 원 lap 기록과 §64~§66에 그대로):** 정적 경로 확정(자원
게이트 0개) → 런타임 §7 probe UNKNOWN → 독립 재계산 ACCEPT + N147~N150(평균 기반 추정). lap508
N151~N153이 이 추정을 실측으로 대체. 전 회차 게임신규실행0·source변경0·커밋0.

**lap356~500 계보(수치·판정 전문은 precompaction 스냅샷 연쇄와 각 원 lap 기록에 그대로):**
W26 144k soak `CLOSED`(lap497~499) → N141 재현성 판정(lap500, `N141_REPRODUCED`이나 N144로
독립재현 부정·N145로 종단여부 UNKNOWN 강등) → Q7 strategy 처분(lap499: Q7-B 잠정채택·Q7-A
사용자전결) → lap356~496(W8~W27 soak/케이던스/판정기 수리/fixture축 소거, Step A~D rider 계보).
전 회차 제품코드/커밋 전부0.
## 바퀴 기록
lap521(middle, Opus5.5): lap520 W33 독립 검수 결과 W33 `CLOSED`(라벨 미부여).
- M-0 ACCEPT, N172~N176, M-1 전제 REJECT. footprint 예측은 11~12/14로 사후 임계다.
- 트랙② 진단을 종료하고 STOP한다(§79). 게임실행0·source변경0·커밋0.
- STATUS 압축 원문: `…status_lap521_precompaction.md`. 전문: `20260923_lap521_middle_w33_independent_review.md`.
lap520(work, Sonnet5) W33 M-0 완료(8/8 PASS)·M-1 `UNRESOLVED_STATIC_ONLY`(종-의존 파라미터 런타임 전용, 정적으론
14종 중 13종 판별 불가). EXIT_A=종-무관/EXIT_B=`AFDD0` 종-의존 특정, 신규 필드 `+0x3A74` 발견. 경량 M-2(PS3 단발
스냅샷) 필요성만 선언, 미실행. 게임실행0·source변경0·커밋0·`SAFETY_PASS`·`CONTEXT_PASS`(`make check` 미재실행,
동일 source 면제, 직전819 유지). **실행 증거 무증가 2회째 ⇒ 다음 strategy/middle 판정 요청(§78)**.
전문 `20260923_lap520_work_w33_state2_exit_decode.md`.
lap519(middle, Opus5.5) lap518 W32 독립 검수: 재집계 ACCEPT(0/8)·N168(반증식 결함)·N169(자기 가설 기각)·N170(손실=상태2 69.8%)·N171(종별)
⇒ W32 `CLOSED`, W33 발행(§77). 게임실행0·source변경0·커밋0. `make check` exit0 **819 passed**·`SAFETY_PASS`·`CONTEXT_PASS`.
STATUS(138→)·INBOX(353→) 압축, 원문 `docs/history/20260923_{status,inbox}_lap519_precompaction.md`. 전문 `20260923_lap519_middle_w32_independent_review.md`.
lap518(work, Sonnet5) W32 M-1/M-2/M-3 실행 `PROBE_OK`: 반증조건② 8/8 owner 성립 ⇒ `MODEL_REFUTED`(방향성 EXEC_FAIL,
`C/S` 0.125~0.307). N144 결정성 lap516과 불일치0/8. 게임실행1(24,005tick 완주)·source변경0·커밋0·`SAFETY_PASS`·
`make check` 미재실행(source불변 면제, 직전819 유지). 전문 `20260923_lap518_work_w32_build_order_funnel_probe.md`.
lap517(middle, Opus5.5) lap516 W31 독립 검수: M-2 ACCEPT(0/8)·M-0 부분 기각(N162~N166)·스케줄러 `0x43F5D0` 해독(N164/N167)
⇒ W31 `CLOSED`, W32 발행(§75). 게임실행0·source변경0·커밋0·`make check` exit0 **819 passed**·`SAFETY_PASS`·`CONTEXT_PASS`.
전문 `20260923_lap517_middle_w31_independent_review.md`.
lap509~516(압축, 전문 `…status_lap519_precompaction.md`와 각 원 lap 기록): lap516(work) W31 `UNCLASSIFIED` · lap515(middle) 18/18 N158~N161 ·
lap514(middle) W30 `CLOSED` · lap513(work) 안 B 24k · lap511(middle) N157 · lap510(work) 안 A · lap509(middle) W30 발행 ·
lap508 W29 ACCEPT · lap507 W29 · lap505(strategy) Q8 · lap501·502·504. 각 회차 `make check`는 819(lap514~517)·817(lap511) passed.
(lap501~511 제품 source 변경은 lap510 신규 패처뿐·커밋 0, 게임실행은 lap507 1·lap510 2.)
lap356~500 계보(압축, 전문은 precompaction 스냅샷 연쇄와 각 원 lap 기록에): lap500(middle) N141
재현성+N144/N145/N146 → lap499(strategy) Q7 처분 → lap498(middle) W26 독립검수 ACCEPT·`CLOSED`
→ lap497(work) W26 144k soak 완주 → lap356~490(W8~W27 soak/케이던스/판정기 수리 계보).
전 회차 제품코드/커밋 전부0(lap491·495·497만 게임실행1, source변경0).
