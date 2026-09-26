# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**. 제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따른다.
과거 lap275~501 계보와 이번 압축 직전 STATUS 전문은 `docs/history/20260923_status_lap502_precompaction.md`(SHA `a2a12dad6c95e688f8290d783b1bc63e4ad3373090de81ffd4766b57d2f1a0ec`, 130줄)에 그대로 있다(그 안에 lap501·lap500 precompaction 스냅샷 포인터가 연쇄 보존됨). lap511 압축 직전 전문은 `docs/history/20260923_status_lap511_precompaction.md`(SHA `d64990c025fb131a10f041f873d0a05303b49388d744cf92bb3084e0857ca805`, 125줄).
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
| G2 | W26(144k) `CLOSED`·종합 `CAP_PROXIMITY_STABLE_144K`(부분 증거), Q7 3단 마일스톤 회부 대기. **lap507 W29 실행 + lap508 독립 재계산 `ACCEPT`(불일치 0/8) ⇒ 2단 성립: k=8 `NATURAL_ARRIVAL_ARITH_INFEASIBLE`. 자연 도달 불가는 owner 종단 스냅샷이 아니라 fixture 전체 AI 건설 레퍼토리(27종 중 9종만 건설, 합집합 천장 2,835)에서 온다. H-CROWD UNKNOWN 유지. §67 예산 소진 ⇒ Q8 사용자 응답 대기 STOP.** F4(B) 장부 폭 확장 카드 W30은 **lap514 middle 독립 재계산 `ACCEPT` ⇒ `CLOSED`**(정적+단위+원복+원본 hole 런타임까지; 후보 EXE 실행 0·Q9 미결 ⇒ 제품 근거 아님). 제품 미완료 | lap356~502 계보는 precompaction 스냅샷과 `docs/history/laps/`에. 상세는 아래 「검증 상태」 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
## 다음 한 가지
**2026-09-23 12:55 사용자 지시로 Q8 대기를 풀고 두 트랙을 순서대로 진행한다(G2 자연도달 축은 계속 대기).**
트랙① F4(B) 카드 W30 `docs/work/active/G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md` **`CLOSED`(lap514, 카드 §9)**:
lap510 안 A REJECT(lap511) → lap512 안 B source → lap513 24k soak `HOLE_CONSTANT` → lap514 독립 재계산 ACCEPT.
후보 SHA `1893ff50…`(15곳·diff 66B). 후보 EXE 실제 실행 0(Q9 미결) ⇒ 제품 근거 아님. 구세이브 미지원(신규 게임 전용).
트랙② **lap515 middle이 초안 측정식(18종 진입 조건)을 정적 probe로 닫았다: 18/18 = 진영 블록(N158)** —
건설 결정은 `FUN_00406C70`(유닛 생산)이 아니라 `FUN_0043E0E0`→`FUN_0043DBB0`, fixture 전원 조선. 남은 표적은 **건설 속도**.
**다음 한 가지: work(Sonnet5)가 카드 W31 `docs/work/active/G2_BUILD_PACE_STATE_PROBE_LAP515.md` 실행** — M-0 정적(호출
케이던스·상태2~4 대기 대상) + M-1 24k 런타임 표본(`+0xD34`/`+0xD36`/`+0x200E`/`+0x33B0` 등, 읽기 전용, 포그라운드 동기 완주)
→ 사전 고정 라벨 `SELECT_EMPTY`/`SELECT_OK_EXEC_WAIT`/`CADENCE_BOUND`/`UNCLASSIFIED`. 상한 한 회차/60분·실패 가설2.
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
- G1/G4 개별 blocker(R1/S1 클릭·좌표 포렌식, AI runtime 실패 등)는 전문 그대로 precompaction 스냅샷과 `docs/history/laps/`에 보존되며 G2 성립 전까지 작업 대상이 아니다.
## 검증 상태
**2026-09-23 lap515(middle, Opus5.5) — 트랙② 정적 probe 단언 18/18 PASS ⇒ 전제 정정 N158~N161 + W31 발행**
(전문 `docs/history/laps/20260923_lap515_middle_w31_build_faction_gate.md`, 근거 `analysis/memory_maps/ai_build_faction_gate_0043dbb0_lap515_20260923.md`,
산출 SHA `7acf03c9…`, 2회 결정적). 원본 바이트: 블록 jump table·4집합·생산 건물 27 서로소 분할·`FUN_0043DB00` 건물 게이트·종별 한도식.
W29 원시 nation 721표본 전원 1, lap513 원시 건물 시계열. 게임실행0·source변경0·커밋0. 2단 독립 검수 없음(W31 검수 회차가 재실행).

**2026-09-23 lap514(middle, Opus5.5) — lap513 W30 안 B 독립 재계산 = `ACCEPT` ⇒ W30 `CLOSED`**
(전문 `docs/history/laps/20260923_lap514_middle_w30_holeb_independent_recompute.md`, 근거
`analysis/memory_maps/g2_supply_ledger_holeb_acceptance_lap514_20260923.md`, 산출 SHA `0c0ed0d2…`).
원시 `window_hex` 5,768 owner-표본 재추출 `+0x2016` 위반0(tick 16→24,019), 입력 SHA `b8c3b452…`/`030f6a0e…` 일치.
**겹침 기준** 전수 스캔(306,187명령): `[0x200c,0x2010)` = used9+building4+`lea 0x444C63`(→`+0x200a` word 전용, 오탐),
`[0x2016,0x2018)` = `0x43F57F` 1곳(`esi≥1` ⇒ 최저 `+0x2018`). 후보 `1893ff50…` diff 66B 사이트 밖0·역디스어셈블15/15·원복 SHA.
9개 used 소비 전부 32-bit(16-bit 재절단0). 관찰: 단위 M-e/M-f는 Python 산술 모델이라 기계어 근거는 소비 폭 검토가 맡는다;
lap512 `MAX_WALL_S` 변경은 공개된 무해 편차. 게임실행0·제품source변경0·커밋0·`make check`819 passed·`SAFETY_PASS`.

**lap513(work, Sonnet5)** lap512 스크립트 무수정 포그라운드 완주: `HOLE_CONSTANT`·tick24,019·721표본·위반0, 단위23·
`make check`819·`SAFETY_PASS`. 전문 `docs/history/laps/20260923_lap513_work_w30_holeb_runtime_reconfirm.md`.

**2026-09-23 lap511(middle, Opus5.5) — lap510 W30 소비 독립 검수 = 구멍 `REJECT` · 패치 기계부 ACCEPT**
(전문 `docs/history/laps/20260923_lap511_middle_w30_independent_review.md`, 근거
`analysis/memory_maps/g2_supply_ledger_hole_rejection_lap511_20260923.md`, 카드 §8, 회부 §71).
**N157 — `+0x2100`은 구멍이 아니다.** `+0x2014`(count word)/`+0x2018`(dword 원소) 리스트의 추가 함수
`0x43F4C0`/`0x43F4F0`이 `cmp ax,0x3e8`로 **용량 1,000** ⇒ 원소 영역 `[0x2018,0x2FB8)`(끝이 다음 인덱스
배열 시작과 맞물림). `+0x2100`=**58번 칸**, lap510 시도1 `+0x201c`=**1번 칸**(같은 리스트). lap510
런타임 0 위반(tick6,018)은 리스트가 최대 **9칸**만 찼기 때문(원시 재계산) ⇒ 안 A 기각(실패 2/2).
**재계산 PASS:** 카드 원문 11곳 old-bytes 11/11 · 후보 SHA `7cb0faf3…` 재현 · diff 62B 사이트 밖 0 ·
역디스어셈블 11/11 · create→restore 원본 SHA 재현 · `+0x200c` 전수 9곳(N154 독립 재확인).
**안 B 입력:** `+0x2016`(count↔배열 정렬 패딩)을 덮는 명령은 `0x43F57F` 1곳(esi≥1로 비도달), lap510 원시
**2,896** owner-표본 전부 0 · `+0x200e` 접근 4곳 별칭 없음. 정정: lap510 "1,440"표본은 원시 1,448.
lap510은 background `make check` 대기 중 종료돼 STATUS 미갱신 — 이번 회차가 대신 기록.
probe `…/probes/20260923_lap511_middle_w30_independent_review.py` exit 0, 산출 SHA `f3e9dcbd…`.
게임실행0·제품source변경0·커밋0 · make check·safety 결과는 아래 「바퀴 기록」 lap511.

**2026-09-23 lap510(work, Sonnet5) — W30 안 A 구현**(lap511이 구멍 REJECT). M-0 정적 스캔 707후보 →
런타임 시도1 `+0x201c` 위반1,425(기각)·시도2 `+0x2100` 위반0(tick6,018) → 11곳 동일길이 치환 패처+
단위 21 passed·`SAFETY_PASS`. 게임실행2(원본 패치0)·커밋0. 전문 `20260923_lap510_work_f4b_ledger_32bit_hole_relocation.md`.

**lap507~509 계보(lap511 압축, 전문은 precompaction 스냅샷 `…lap511…`·각 원 lap 기록·§68~§70에 그대로):**
lap507(work) W29 `PROBE_OK`(tick24,029, 천장 [2445,1070,2445,2050,2445,1190,2050,2445]·k=8·이론최대 8,077·
`c_max=65`) → lap508(middle) 독립 재계산 **ACCEPT**(불일치 0/8, 반증시험 0건) + **N151**(보유 종 합집합
9/27 천장 2,835<5,000 ⇒ 근원은 AI 건설 레퍼토리)·**N152**(7종이면 충분, 병목은 고가치 종 미건설)·
**N153**(tick18,000 이후 6/8 생산 중) → lap509(middle) W30 발행 + **N154**(`+0x200c` 범위 9곳, 절대주소
별칭 `0x95877C` 4곳 포함; `0x43EE03`/`0x43F0F3`/`0x43F43F`는 `+0x2012` 읽기)·**N155**(bulk span
`[0x892410,0x975D8C)`=932,220B 고정 ⇒ stride 보존 시 저장 길이·레이아웃 불변, 호환은 값 해석 문제)·
**N156**(구조적 최대 `used` 78,000). 잔여 UNKNOWN: owner7 56.3% 정지, H-CROWD. 전 회차 source변경0·커밋0.

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
lap515(middle, Opus5.5) 트랙② 정적 probe 18/18 PASS: 18종 미건설=진영 블록(N158)·병목=건설 속도(N161) ⇒ W31 발행(§73).
게임실행0·source변경0·커밋0. 검사 결과는 아래 lap515 검사 줄. 전문 `20260923_lap515_middle_w31_build_faction_gate.md`.
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
