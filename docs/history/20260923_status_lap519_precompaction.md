# STATUS lap519 압축 직전 원문 (SHA256 6060035cf4d5da53e489d1e69d4850cddc44bb76049907b29f80d2942786c520, 138줄) — 삭제·재해석 없음

# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**. 제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따른다.
과거 lap275~501 계보와 이번 압축 직전 STATUS 전문은 `docs/history/20260923_status_lap502_precompaction.md`(SHA `a2a12dad6c95e688f8290d783b1bc63e4ad3373090de81ffd4766b57d2f1a0ec`, 130줄)에 그대로 있다(그 안에 lap501·lap500 precompaction 스냅샷 포인터가 연쇄 보존됨). lap511 압축 직전 전문은 `docs/history/20260923_status_lap511_precompaction.md`(SHA `d64990c025fb131a10f041f873d0a05303b49388d744cf92bb3084e0857ca805`, 125줄).
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
트랙② W31 **`CLOSED`(lap517 middle 독립 검수, 라벨 `UNCLASSIFIED` 8/8 유지)** → **W32 lap518(work) 실행
`PROBE_OK`, 카드 §3 반증조건②가 8/8 owner에서 성립 ⇒ `MODEL_REFUTED`**(라벨 미부여, 원시 보고, 방향성
`EXEC_FAIL`: `C/S` 전원 0.125~0.307<0.5; 그러나 "`+0x33AC` 변화 표본에서 `+0xD32≠1`"이 시작의
26.6~44.3%에서 실측돼 정식 라벨 확정 불가). N144 결정성 lap516과 불일치 0/8=PASS. 원인(스케줄러 8-tick
이하 초고속 실패 vs SCH §2 모델 결함)은 이 카드 범위로 미판별, UNKNOWN 유지.
**다음 한 가지: middle(Opus5.5)이 lap518 W32 원시(`samples.jsonl`/`build_funnel_summary.json`) 비참조
재집계로 독립 검수한 뒤, `MODEL_REFUTED`/EXEC_FAIL 방향성으로 카드를 닫을지 추가 계측이 필요한지 판정한다.**
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
- G1/G4 개별 blocker(R1/S1 클릭·좌표 포렌식, AI runtime 실패 등)는 전문 그대로 precompaction 스냅샷과 `docs/history/laps/`에 보존되며 G2 성립 전까지 작업 대상이 아니다.
## 검증 상태
**2026-09-23 lap518(work, Sonnet5) — W32 M-1/M-2/M-3 실행 `PROBE_OK`, 카드 §3 반증조건② 8/8 owner 성립 ⇒ `MODEL_REFUTED`**
(전문 `docs/history/laps/20260923_lap518_work_w32_build_order_funnel_probe.md`, 근거
`analysis/memory_maps/ai_build_order_funnel_probe_lap518_20260923.md`, M-3은 lap517 probe 재실행으로 대체
exit0·16/16 PASS·산출 SHA `8802218b…` lap517과 동일). `f_idle` 0.887~0.915·`S/S_exp` 1.02~1.25(반증①
불성립)·`S_short_gap_defects` 8/8 0건·`C/S` 0.125~0.307(<0.5)·`B/C` 0.519~0.818. "`+0x33AC` 변화 표본에서
`+0xD32≠1`"이 시작의 26.6~44.3%(23~43/83~102건)에서 실측돼 반증조건②(카드 §3) 성립 ⇒ 정식 라벨 미부여,
원인은 스케줄러 8-tick 이하 초고속 실패/SCH §2 모델 결함 중 미판별(UNKNOWN). N144 결정성 대조: lap516과
max_used_by_owner·최종 건물 수 불일치 0/8=PASS. 게임실행1(24,005tick 완주)·source변경0·커밋0·`SAFETY_PASS`.
다음=middle 독립 검수.

**2026-09-23 lap517(middle, Opus5.5) — lap516 W31 독립 검수: M-2 ACCEPT(불일치 0/8)·M-0 부분 기각 ⇒ W31 `CLOSED`**
(전문 `docs/history/laps/20260923_lap517_middle_w31_independent_review.md`, 근거
`analysis/memory_maps/ai_build_order_scheduler_0043f5d0_lap517_20260923.md`, probe 단언 16/16 PASS·산출 SHA `8802218b…` 2회 동일;
1차 실행은 A2 단언 작성 결함으로 exit1, 사유 기록). N162~N167. 게임실행0·source변경0·커밋0. `make check`/safety는 바퀴 기록 참조.

**2026-09-23 lap516(work, Sonnet5) — W31 M-0/M-1/M-2 `PROBE_OK`, 라벨 `UNCLASSIFIED` 8/8**
(전문 `docs/history/laps/20260923_lap516_work_w31_build_pace_state_probe.md`, 근거
`analysis/memory_maps/ai_build_pace_state_probe_lap516_20260923.md`). M-0 신규: `+0xD34`는 건설
전용이 아니라 20종 AI 오더 공용 필드(`.text` 전수 스캔 41건), 실패 시 `FUN_0043F5A0`이 0으로 리셋
(재시도 아닌 오더 종료) — 재무장 스케줄러는 UNKNOWN. M-1/M-2(24,013tick·1,439표본·8owner): 상태0
지배 85.6~87.9%, 상태1~4 합계 3.5~5.1%(상태1 0회 포착)인데도 건물 순증가 9~18채(감소0). 후보 SHA
`a10024de…` W29와 byte-identical, source_unchanged, fault0. 다음=middle 독립 검수. 2단 독립 검수 없음.

**2026-09-23 lap515(middle, Opus5.5) — 트랙② 정적 probe 단언 18/18 PASS ⇒ 전제 정정 N158~N161 + W31 발행**
(전문 `docs/history/laps/20260923_lap515_middle_w31_build_faction_gate.md`, 근거 `analysis/memory_maps/ai_build_faction_gate_0043dbb0_lap515_20260923.md`,
산출 SHA `7acf03c9…`, 2회 결정적). 원본 바이트: 블록 jump table·4집합·생산 건물 27 서로소 분할·`FUN_0043DB00` 건물 게이트·종별 한도식.
W29 원시 nation 721표본 전원 1, lap513 원시 건물 시계열. 게임실행0·source변경0·커밋0. 2단 독립 검수 없음(W31 검수 회차가 재실행).

**lap513~514 W30 안 B 계보(lap517 압축, STATUS 원문은 `docs/history/20260923_status_lap517_compacted_block.md`(SHA `1d8f94df…`)·각 lap 기록·`ESCALATE_SOL`§72에 그대로):** lap513(work) `HOLE_CONSTANT`
24k 완주(위반0) → lap514(middle) 독립 재계산 **ACCEPT ⇒ W30 `CLOSED`**(원시 5,768표본 위반0, 겹침 전수 스캔 누락0,
후보 `1893ff50…` 원복 SHA 재현, used 소비 전부 32-bit). 근거 `analysis/memory_maps/g2_supply_ledger_holeb_acceptance_lap514_20260923.md`.

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
lap518(work, Sonnet5) W32 M-1/M-2/M-3 실행 `PROBE_OK`: 반증조건② 8/8 owner 성립 ⇒ `MODEL_REFUTED`(방향성 EXEC_FAIL,
`C/S` 0.125~0.307). N144 결정성 lap516과 불일치0/8. 게임실행1(24,005tick 완주)·source변경0·커밋0·`SAFETY_PASS`·
`make check` 미재실행(source불변 면제, 직전819 유지). 전문 `20260923_lap518_work_w32_build_order_funnel_probe.md`.
lap517(middle, Opus5.5) lap516 W31 독립 검수: M-2 ACCEPT(0/8)·M-0 부분 기각(N162~N166)·스케줄러 `0x43F5D0` 해독(N164/N167)
⇒ W31 `CLOSED`, W32 발행(§75). 게임실행0·source변경0·커밋0·`make check` exit0 **819 passed**·`SAFETY_PASS`·`CONTEXT_PASS`.
전문 `20260923_lap517_middle_w31_independent_review.md`.
lap516(work, Sonnet5) W31 M-0/M-1/M-2 실행 `PROBE_OK`: `+0xD34` 20종 오더 공용 필드 신규 발견(§74),
라벨 `UNCLASSIFIED` 8/8. 게임실행1(24,013tick 완주)·source변경0·커밋0·`make check` 미재실행(source불변
면제, 직전819 유지). 전문 `20260923_lap516_work_w31_build_pace_state_probe.md`.
lap515(middle, Opus5.5) 트랙② 정적 probe 18/18 PASS: 18종 미건설=진영 블록(N158)·병목=건설 속도(N161) ⇒ W31 발행(§73).
게임실행0·source변경0·커밋0·`make check` exit0 **819 passed**·`SAFETY_PASS`·`CONTEXT_PASS`. 전문 `20260923_lap515_middle_w31_build_faction_gate.md`.
lap514(middle, Opus5.5) lap513 W30 안 B 독립 재계산 **ACCEPT ⇒ W30 `CLOSED`**(카드 §9, 회부 §72). 게임실행0·source변경0·커밋0·
단위23 passed·`make check` exit0 **819 passed**·`SAFETY_PASS`·`CONTEXT_PASS`. 다음=트랙② W31 카드 발행. 전문 `20260923_lap514_middle_w30_holeb_independent_recompute.md`.
lap513(work, Sonnet5) 카드§8 안 B M-a 24k soak 완주(lap512 미완주 스크립트 재사용, 수정 없음): tick24,019·
721표본·위반0·`HOLE_CONSTANT`. 단위23 passed·`make check`819 passed·`SAFETY_PASS`·`CONTEXT_PASS`.
게임실행1(원본 패치0)·source변경0·커밋0. 전문 `20260923_lap513_work_w30_holeb_runtime_reconfirm.md`.
lap511(middle, Opus5.5) lap510 W30 독립 검수: 구멍 `+0x2100` **REJECT**(N157, `+0x2018` 1,000칸 리스트 58번 칸)
· 패치 기계부 ACCEPT · 카드 §8로 안 B 수리 범위 발행(`+0x2016`). 게임실행0·source변경0·커밋0·`make check` exit0·**817 passed**·`SAFETY_PASS`·`CONTEXT_PASS`.
전문 `20260923_lap511_middle_w30_independent_review.md`, 회부 §71.
lap510(work, Sonnet5) W30 안 A 구현: `+0x2100` 이전 패처+단위21 passed·게임실행2(원본 패치0)·커밋0. background
`make check` 대기 중 세션 종료로 STATUS 미갱신(lap511이 기록). 전문 `20260923_lap510_work_*.md`.
lap509(middle) W30 발행+N154~N156(§70) · lap508(middle) W29 ACCEPT+N151~N153·§67 예산 소진(§69) ·
lap507(work) W29 `PROBE_OK`(§68) · lap505(strategy, Fable5) Q8 CONTINUE·예산 한정(§67) ·
lap501·502·504 정적 추적→런타임 `UNKNOWN`→ACCEPT+N147~N150(§64~§66). 전문은 각 `20260923_lap50*_*.md`.
(lap501~511 제품 source 변경은 lap510 신규 패처뿐·커밋 0, 게임실행은 lap507 1·lap510 2.)
lap356~500 계보(압축, 전문은 precompaction 스냅샷 연쇄와 각 원 lap 기록에): lap500(middle) N141
재현성+N144/N145/N146 → lap499(strategy) Q7 처분 → lap498(middle) W26 독립검수 ACCEPT·`CLOSED`
→ lap497(work) W26 144k soak 완주 → lap356~490(W8~W27 soak/케이던스/판정기 수리 계보).
전 회차 제품코드/커밋 전부0(lap491·495·497만 게임실행1, source변경0).
