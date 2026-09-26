# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**. 제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따른다.
압축 직전 STATUS 전문 연쇄: lap502 `docs/history/20260923_status_lap502_precompaction.md`(SHA `a2a12dad…`, lap275~501 계보와 lap500·501 포인터 포함) · lap511 `…status_lap511_precompaction.md`(SHA `d64990c0…`) · lap519 `…status_lap519_precompaction.md`(SHA `6060035c…`) · lap521 `…status_lap521_precompaction.md`(SHA `b05e5b60…`) · lap522 `docs/history/20260923_status_lap522_precompaction.md`(SHA `00bb7f0a8ee38ff9436b144b74d51d025ac3f70bd9961c2dfa2aa6c313922a67`, 129줄) · lap530 `docs/history/20260923_status_lap530_precompaction.md`(SHA `2628567a0d17188e865f84f70326b740b713bb747baecd91244a19bd2059f59d`, 52줄) · lap534 `docs/history/20260923_status_lap534_precompaction.md`(원문 SHA `852d5c8d510f6184913b78ec3f5340747471b0e35cb9a8f65dc85c13d6bde5d2`, 130줄) · **lap537 `docs/history/20260923_status_lap537_precompaction.md`(원문 SHA `7f69cde47398d29a7a6f4aa153513628634d2a6be4978e8aadafa381a7852ead`, 128줄)**.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
| G2 | **2026-09-23 18:43 사용자 Q8=(ㄱ)** cap5000 도달은 gate-legal 시딩으로 대체 가능. lap522 strategy가 기준 A1~A8·순서 S0~S5·144k 조건부 사전 허가 고정. W35(S0) `CLOSED`(lap524~525, `FEASIBLE`). N182 허용목록 구조적 교전 불능 ⇒ lap526 (나) 채택·X=type2(lap527). W36 실행 2회 `ARM_FAIL`(lap528) → N187 확정·W37 발행(lap529). lap530 work W37 24k 1회 완주(N187 해소, A1·A8'·A5 PASS). lap531 middle 원시 재계산: 라벨 `CYCLE_UNSTABLE` 일치 ⇒ W37 `CLOSED`, 144k 닫힘. N191 = 로드 비인과. N192: op8 수락 1,872/1,872이지만 3/4짝이 39파동 내내 거리4·op8 사망0. **lap532 strategy: N192 경로 (a) W38 접근 진단 probe 채택(type110 양성 대조, 결과 분기 사전 고정), (c) 인접 배치 기각, A6→A6a/A6b(약화 거절), A3→A3'/A3r.** **lap533 work: W38 게임 1회 실행 완주. 자기판정 `PROMOTED_NO_MOVE`(S=144/144, promoted 98.6%·moved 15.3%·hit 0), H7 대조는 `CONTROL_NA`(N195: T0에 type110 생존0, 카드§3 표에 없는 조합).** **lap534 middle: 원시 재계산 라벨 일치. 단 §3 표 밖 조합이고 분기 전제와 원시가 충돌(N196 승격 즉시 철회 78%, N197 이동분도 접근 0, N198 유닛 점유로는 막힘 설명 안 됨, N195 정정 type110=AI 생산분) ⇒ strategy 회부(§88).** **lap535 strategy: 전열 배치 보류, R1을 런타임 gdb watchpoint 귀속 W39로 채택(철회 슬롯 결정적 확인), H7 폐기·H7' 정의, S1 종결 조건 고정(§89).** **lap536 work: W39 게임 1회 완주, gdb hw watchpoint 3개로 `+0x290` 철회 writer pc `0x40d544`(store `0x40d53d`) 확정, H13 바이트 대조(창1,280B) 원본↔후보 차이 0개 ⇒ 자기 라벨 `REVERT_ORIGINAL_LOGIC`(후보 결함 아님). 부가: owner3 소스가 실제 7칸 이동 후 원위치 복귀함을 직접 관측(N197 실증, §90).** **lap537 middle: 원시 재계산 라벨 일치(창 밖 차이도 전부 풀 기준 재배치). `E_rev`는 대기 cmd2(CmdStop `FUN_004AEDA0`)의 무조건 커밋이라 fixture 분기 없음, 발행 지점 127곳 ⇒ `BLOCKED(static)`·§3 표 밖 strategy 회부(§91, 권고 W40 발행자 런타임 귀속).** **lap538 strategy: W40 채택(J4 즉시 적용 기각), W40 = J4 후속 work 1회, 예외 E2만, 분기·`BLOCKED` 선택지 사전 고정(§92).** 기존 부분 증거: W26 144k `CAP_PROXIMITY_STABLE_144K`(N141). F4(B) W30 `CLOSED`. 트랙② W31~W33 `CLOSED`. 제품 미완료 | 시딩 군대끼리 교전 지속(N192 원거리 접근)·사망/재생산 지속성(A2 0/8·A3 0/8)·A6 사망조건 판별력(N194)·건물 포함 구성(A8)·같은 후보 144k·멀티 동기화 미시험 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
## 다음 한 가지
**work(Sonnet5): W40 정지 명령 발행자 런타임 귀속 — 게임+gdb 1회 foreground 완주(45분 상자).** 사양 `docs/work/active/G2_STRATEGY_W40_STOP_ISSUER_LAP538.md` §2(middle 카드 없음).
- 3파일 SHA(lap535 §2 경계 1)·W39 하네스 SHA(`w39_run.py` `64a86d21…`, `gdb_watch.py` `f8a0ba33…`) 확인 → `SAFETY_PASS`·표적 테스트 2개 → `w40_run.py`(H14~H16) → 실행 → H16 대조 → 자기 라벨.
- watch: A·B `+0x384`(W39 `+0x290` 주소 +0xF4), B `+0x388`. `new`∈{2,3,4} 전체 기록(스택 128 DWORD). CmdStop 127곳/CmdMove 44곳 `call+5` 대조로 `ISSUER_FN`.
- 분기(§3 고정): A나 B가 `OWNER_AI` ⇒ S1 `BLOCKED`·사용자 보고 / 둘 다 유닛 로직 ⇒ middle 분기 1회 판독, 주소·필드·fixture 값 특정 시 E2 work 1회 / 그 외 `BLOCKED`.
- **문서 연속 2회째(lap537·538). W40 실행 없이 끝나면 STOP하고 사용자에게 보고한다.** W40 = J4 "후속 work 1회"(lap538 K2).

**미결(사용자 전권): Q9(F4 후보 실행 검증 제외 범위, S3에 영향) · Q7-B 3단 마일스톤 · "8인"이 사람인지 AI인지(S4 멀티 영향) ·
스크립트 교전 입력을 (ㄱ) 범위로 볼지(번복 시 이 트랙 정지).**
## 지금 막힌 것 (Blockers)
- **S1 교전 지속 불능(N192, lap531 확정 — W38 lap533 실행·lap534 검수: 승격 후 ≤25 tick 철회 113/144, 접근 0, 유닛 점유 막힘 불지지 ⇒ lap536 W39: 철회 writer pc `0x40d544` 확정, H13 대조 0건 ⇒ 원본 로직(후보 결함 아님) ⇒ lap537: 철회 = 대기 정지 명령(cmd2) 커밋, 발행자 127곳 중 미확정 ⇒ lap538 §92: W40 런타임 귀속, 이것이 J4 마지막 work):** op8(`FUN_00415480`)은 1,872/1,872 수락되지만,
  짝 (0,1)·(4,5)·(6,7)은 39파동 내내 선택 시점 최소 거리가 4이고 op8 기인 사망은 0이다. (2,3)만 시딩 인접분 7기가 죽었다(마지막 tick7,801).
  원거리 접근은 입증되지 않았다. x,y를 원시에 남기지 않아 "이동 0"은 미확정이다. N191 로드 비인과(로드 전 5파동·후 13파동 피해 0).
  (S1 무장은 lap530에서 해소됨 — N187 시딩순서 수정으로 8/8 owner `used`=4,950, `ARM_FAIL` 없음.)
- **허용목록 fixture 구조적 교전 불능(N181~N183) — lap526 §83 판정·lap527 X=type2 확정(N184)으로 해소, 실행 미검증.** 시딩 type5/7/46은 `+0x1D8`
  bit0x4가 없다(타입 행 `+0x4C` 고정, writer 5개는 lap526이 독립 재확인). 원본 28타입 중 bit0x10 보유가 0종이라 fixture 전 유닛은 `+0x1BC`=1이다.
  해소책은 bit0x4 전투 타입 X 1종 추가다. 남은 위험: type2 런타임 행 불일치(N185)나 Place/Gate 거부 시 `ARM_FAIL`이다. 사용자가 확장을 (ㄱ) 범위 밖으로 보고 번복할 수 있다.
- **F4 안전상한(lap509 N156, blocker 아님):** 구조적 최대 `used` 1,200×65=78,000 > 32,767 ⇒ 16-bit 랩은 구조적으로 가능하고 32-bit에서는 불가능하다.
  실제 도달성 UNKNOWN. W30 안 B `+0x2016` 채택·`CLOSED`. PlayerStruct 밖 배치는 middle/strategy 판정 필요.
- **(ㄱ)로 해제된 옛 blocker(근거로만 보존):** N141/N145 fixture 내 자연 경로 소진, lap508 N151~N153·lap515 N158~N161(진영 블록+건설 속도)·
  lap517~521(스케줄러 천장, 상태2 손실 약 70%, footprint·조선소 술어). 전문은 precompaction 스냅샷·§69~§79.
- **G2 구조통합 blocker(owner당1200 초과·저장호환 확장):** 저비용 다수 구성 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·저장/LAN 일관 계약이 미구현. 상세는 precompaction 스냅샷.
- G1/G4 개별 blocker(R1/S1 클릭·좌표 포렌식, AI runtime 실패 등)는 precompaction 스냅샷과 `docs/history/laps/`에 보존되며 G2 성립 전까지 작업 대상이 아니다.
## 검증 상태
**2026-09-23 lap538(strategy, Opus5.5) — §91 판정: W40 채택, J4 예산 해석·E2 예외·`BLOCKED` 선택지 고정(§92)**
- 판정 `docs/work/active/G2_STRATEGY_W40_STOP_ISSUER_LAP538.md`(SHA `542f45fa…04ef9`), 기록 `docs/history/laps/20260923_lap538_strategy_w40_stop_issuer_decision.md`.
- 검수: W39 원시·lap537 재계산 6파일 SHA 일치, CmdStop 127·CmdMove 44 재계산 일치, cmd2 무조건 커밋 확인. 정황: CmdStop 74곳이 `0x47` 대역(AI dispatcher `FUN_004755D0` 소재).
- 게임실행0·source변경0·커밋0. 원본 `b56986e0…` 불변. `SAFETY_PASS`·`CONTEXT_PASS`(STATUS 114·INBOX 302·APPROVALS 46줄). source 불변이라 `make check` 생략(N22).
**2026-09-23 lap537(middle, Opus5.5) — W39 원시 재계산 `REVERT_ORIGINAL_LOGIC` 일치, `E_rev` 정적 판독 `BLOCKED(static)` ⇒ strategy 회부 §91**
- 전문: `docs/history/laps/20260923_lap537_middle_w39_review_erev_static.md`. 재계산 `temp/Syw2plus_patch/g2_capacity/20260923_lap537_middle_w39_review/`
  (`recompute_w39.{py,json}`·`diff_windows.{py,json}`, run_summary·h13_report 미참조). 원시 SHA `triggers` `8f4735fa…`·`trace` `7017daa0…`.
- 26건·M0·`E_rev` `0x40d544`(eax=2, edi=esi+0x384) 일치. 창 밖 차이 9명령은 전부 풀 기준 `0x66b790→0x108c000` 재배치다.
- `FUN_0040C640` cmd2 case `0x40c727`→`0x40d53a`에는 조건이 없다. 정지 명령 경로는 CmdStop `FUN_004AEDA0`→`0x4AED20`→`0x40FF90`→SetPending `0x412540`이다. 호출 지점 127곳, 후보 2개는 미결이다.
- 게임실행0·source변경0·커밋0. 원본 `b56986e0…` 불변(재확인). source 불변이라 `make check` 생략(N22).
**2026-09-23 lap536(work, Sonnet5) — W39 게임 1회 완주: `E_rev` pc `0x40d544` 확정, H13 대조 0건, 자기 라벨 `REVERT_ORIGINAL_LOGIC`**
- 전문: `docs/history/laps/20260923_lap536_work_w39_revert_writer_runtime_attribution.md`, 산출물
  `temp/Syw2plus_patch/g2_capacity/20260923_lap536_w39_revert_watch/`, `ESCALATE_SOL` §90.
- 게이트 3파일 SHA 일치(W38과 동일) → `SAFETY_PASS` → 표적14 passed → `w39_run.py`(W38 원본 SHA와 바이트 동일 확인 뒤 H10~H13만 추가).
- H11: A=3800·B=3185(W38과 완전 일치, 결정성 재확인). gdb hw watchpoint 3개를 op8 **전** 무장, 트리거 26건(WA6·WB6·WC14) 전량 레지스터/스택 포함 기록.
- A: t1089 승격(`0x40c8a9`)→t1105 `4→2`(`0x40d544`=`E_rev`)→`2→1`(`0x48e44c`)→t1107 `1→3`(`0x40c766`)→반복. 승격→철회 16 tick.
- B: t1121 승격→163 tick 무변화→t1284 철회 시작. **B의 x가 t1151~1221에 56→63 이동했다가 t1382~1447에 63→56 원위치 복귀함을 직접 관측**(N197 실증, 이동은 승격과 첫 cmd철회 사이).
- H13: `E_rev` 함수 창 `[0x40d144,0x40d644]`(1,280B) 원본↔후보 바이트 차이 0개(알려진 fixup 28곳 밖). ⇒ 철회는 **원본 게임 로직**, 후보 결함 아님.
- 게임실행1·source변경0·커밋0. 원본 불변, 잔류 프로세스0, A5 무결성 위반 전부0. work 자기판정, middle 미검수.
**2026-09-23 lap535(strategy, Opus5.5) — §88 판정: 분기표 확장 안 함, R1 → W39 런타임 watchpoint 귀속, H7' 정의, 종결 조건**
- 전문: `docs/work/active/G2_STRATEGY_W38_REVERT_ATTRIBUTION_LAP535.md`(SHA `77f5de26…730c`), 기록 `docs/history/laps/20260923_lap535_strategy_w38_revert_attribution_decision.md`, `ESCALATE_SOL` §89.
- 원본·W38 원시 5종·`w38_run.py`·3파일 SHA 일치 재확인. lap534 `recompute_w38.py` 재실행 결과 바이트 동일(`4b1e350d…`). 파동 간 소스 슬롯 결정성 확인(독립 소스 48).
- W18 도구(lap438 gdb hw watchpoint) 존재·`ptrace_scope`=0·gdb 확인. 게임실행0·source변경0·커밋0. source 불변이라 `make check` 생략(N22).

**2026-09-23 lap534(middle, Opus5.5) — W38 원시 재계산 라벨 일치, §3 표 밖 ⇒ strategy 회부(§88), N195 정정·N196~N198**
- 전문: `docs/history/laps/20260923_lap534_middle_w38_independent_review.md`. 재계산
  `temp/Syw2plus_patch/g2_capacity/20260923_lap534_middle_w38_review/recompute_w38.{py,json}`·`blockage_w38.{py,json}`(run_summary 미참조).
- 원시 SHA 4종 lap533과 일치. |S|=144, promoted 142·moved 22·hit 0 ⇒ `PROMOTED_NO_MOVE`, `CONTROL_NA` 일치.
- N196 `+0x290` 1→4→1(≤25 tick, 변위0) 113/144. N197 이동 22기(owner3·7)는 출발점 복귀·최소거리 4 미만 0.
  N198 T0 유닛 점유 BFS로 120/144 경로 존재, 그중 98기 정지(지형 미측정). N195 정정: type110은 phase B AI 생산분(출생 3기).
- 게임실행0·source변경0·커밋0. 원본 `b56986e0…` 불변(재확인), 게이트 3파일 SHA 핀 일치. source 불변이라 `make check` 생략(N22).

**lap531~533 계보(lap537 압축, 원문 전량 `docs/history/20260923_status_lap537_precompaction.md` 원문 SHA256
`7f69cde47398d29a7a6f4aa153513628634d2a6be4978e8aadafa381a7852ead`, 128줄):** lap533(work) W38 게임 1회 `PROMOTED_NO_MOVE`·`CONTROL_NA`(N195) →
lap532(strategy) §86 판정 (a) W38·(c) 기각·A6a/A6b·A3'/A3r → lap531(middle) W37 `CYCLE_UNSTABLE` `CLOSED`·N191~N194. 게임실행 lap533(1)·source변경0·커밋0.

**lap528~530 계보(lap534 압축, 원문 전량 `docs/history/20260923_status_lap534_precompaction.md` 원문 SHA256
`852d5c8d510f6184913b78ec3f5340747471b0e35cb9a8f65dc85c13d6bde5d2`, 130줄):** lap530(work) W37 24k 1회 완주·N187 해소·`CYCLE_UNSTABLE`
(`make check` 828 passed) → lap529(middle) W36 `ARM_FAIL` `CLOSED`·N188~N190·W37 발행 → lap528(work) W36 2회 `ARM_FAIL`
(허용목록 {5,7,46,2}+핀2 개정, `make check` 828 passed). 게임실행 lap528(2)·530(1). source 변경은 lap528뿐·커밋0.

**lap521~527 계보(lap530 압축, 원문 전량 `docs/history/20260923_status_lap530_precompaction.md`
SHA256 `2628567a0d17188e865f84f70326b740b713bb747baecd91244a19bd2059f59d`, 52줄):** X=type2 정적
확정(lap527) → S1 fixture 확장 (나) 채택 K1~K7(lap526) → W35 독립검수 `CLOSED`(lap525, N181~N183) →
W35(S0) 실행 `FEASIBLE`(lap524) → W35 카드 발행(lap523) → Q8=(ㄱ) 반영 A1~A8·S0~S5(lap522) →
W33 `CLOSED`·트랙② STOP(lap521). 게임실행은 lap524뿐(1회). source 변경은 lap524 op8 진단 분기뿐·커밋0.

**lap496~520 계보(lap522 압축, 전문은 `…status_lap522_precompaction.md`·각 lap 기록·§59~§78에 그대로):**
W26 144k `CLOSED`(lap497 실행·lap498 ACCEPT·N141) → Q7(lap499) → N141 재현성(lap500) → AI 생산 정지 분석 lap501~504 → Q8 CONTINUE(lap505) →
W29 k=8(lap507·508) → W30 F4(B)(lap509~514 `CLOSED`) → W31~W33 트랙②(lap515~521 `CLOSED`). 게임실행은 lap497·507·510(2)·513·516·518. source 변경은 lap510 패처뿐·커밋0.

**lap356~495 계보(수치·판정 전문은 precompaction 스냅샷 연쇄와 각 원 lap 기록에 그대로):**
W8~W28-R soak/케이던스/판정기 수리/fixture축 소거, Step A~D rider 계보. 전 회차 제품코드/커밋 전부0.
## 바퀴 기록
lap538(strategy, Opus5.5): §91 판정 — W40(정지 명령 발행자 런타임 귀속) 채택, J4 즉시 적용 기각. W40 = J4 후속 work 1회, 예외는 E2(유닛 로직 fixture 원인 주소 특정 시 work 1회)뿐.
판정식·분류·분기·`BLOCKED` 선택지 (가)(ㄴ)예외/(나)사람 슬롯/(다)트랙 중단 사전 고정. 게임실행0·source변경0·커밋0. 다음은 work W40 게임 1회(문서 연속 2회 — 실행 없으면 STOP).
lap537(middle, Opus5.5): W39 원시 독립 재계산 → `REVERT_ORIGINAL_LOGIC` 일치(창 밖 차이 9명령도 전부 풀 기준 재배치). `E_rev` 직전 판독: cmd2 case에 조건 없음 = 대기 정지 명령 커밋,
CmdStop 발행 지점 127곳·후보 2개 미결 ⇒ `BLOCKED(static)`, §3 표 밖 strategy 회부 §91(권고 W40 발행자 런타임 귀속). 게임실행0·source변경0·커밋0, 원본 불변.
lap536(work, Sonnet5): W39 게임 1회 foreground 완주(약 93초, 45분 상자 내). gdb hw watchpoint 3개(op8 전 무장)로 `+0x290` 철회 writer pc `0x40d544`(store `0x40d53d`) 확정.
H13 바이트 대조(창1,280B) 원본↔후보 차이 0개 ⇒ 자기 라벨 `REVERT_ORIGINAL_LOGIC`(후보 결함 아님). 부가: B가 실제 7칸 이동 후 원위치 복귀함을 직접 관측(N197 실증).
게임실행1·source변경0·커밋0. `SAFETY_PASS`·표적14 passed(전체 make check는 source불변이라 생략, N22), 원본 불변·잔류0. 다음은 middle의 원시 재계산 + `E_rev` 직전 분기 조건 정적 판독.
lap535(strategy, Opus5.5): §88 판정 — §3 표 확장 안 함·전열 배치 보류, R1을 정적 문서 회차 대신 **W39 런타임 gdb watchpoint 귀속**(철회 writer pc → 그 함수만 원본·후보 대조)으로 채택,
H7 폐기·H7'(개방 구역 type2 1:1) 정의, S1 종결 조건 고정. 게임실행0·source변경0·커밋0. `SAFETY_PASS`·`CONTEXT_PASS`(STATUS 115·INBOX 299·APPROVALS 46줄), 원본 불변. 다음은 work W39 게임 1회(문서 연속 2회 — 실행 없으면 STOP).
lap534(middle, Opus5.5): W38 원시 독립 재계산 → `PROMOTED_NO_MOVE`·`CONTROL_NA` 일치. §3 표 밖이고 전열 배치 전제가 원시와 충돌
(N196 승격 즉시 철회 113/144, N197 이동분 접근0, N198 유닛 점유 BFS 경로 120/144, N195 정정 type110=AI 생산분) ⇒ strategy 회부 §88(권고 R1 철회 writer 정적 추적).
게임실행0·source변경0·커밋0. 원본 불변 재확인. `SAFETY_PASS`·`CONTEXT_PASS`(STATUS 108·INBOX 297·APPROVALS 46줄).
lap531~533(압축, 원문 `docs/history/20260923_status_lap537_precompaction.md` 원문 SHA256 `7f69cde4…a7852ead`): lap533(work) W38 `PROMOTED_NO_MOVE` ·
lap532(strategy) §86 판정 W38 채택 · lap531(middle) W37 `CLOSED`·N191~N194. 게임실행 lap533(1)·source변경0·커밋0.
lap528~530(압축, 원문 `docs/history/20260923_status_lap534_precompaction.md` 원문 SHA256 `852d5c8d…6bde5d2`): lap530(work) W37 24k·N187 해소·
`CYCLE_UNSTABLE` · lap529(middle) W36 `CLOSED`·W37 발행 · lap528(work) W36 2회 `ARM_FAIL`. `make check` 828 passed(lap528·530).
lap520~527 계보(lap530 압축, 원문 `docs/history/20260923_status_lap530_precompaction.md` SHA256
`2628567a0d17188e865f84f70326b740b713bb747baecd91244a19bd2059f59d`): lap527(middle) X=type2 확정,
W36 카드 발행 · lap526(strategy) §82 해소 (나) 채택 · lap525(middle) W35 `FEASIBLE` 일치 `CLOSED` ·
lap524(work) W35(S0) 실행 `FEASIBLE` · lap523(middle) W35 카드 발행 · lap522(strategy) Q8=(ㄱ) 반영 ·
lap521(middle) W33 `CLOSED` · lap520(work) W33 M-0 PASS. 게임실행은 lap524뿐(1회)·source변경 lap524뿐·커밋0.
lap509~519(압축, 전문 `…status_lap522_precompaction.md`와 각 원 lap 기록): lap519(middle) W32 `CLOSED`·N168~N171 · lap518(work) W32 `PROBE_OK` 24k ·
lap517(middle) W31 `CLOSED` · lap516(work) W31 24k · lap515(middle) N158~N161 · lap514(middle) W30 `CLOSED` · lap513(work) 안 B 24k ·
lap511(middle) N157 · lap510(work) 안 A · lap509(middle) W30 발행. `make check`는 819(lap514~521)·817(lap511) passed.
lap356~508 계보(압축, 전문은 precompaction 스냅샷 연쇄와 각 원 lap 기록에): lap508 W29 ACCEPT · lap507 W29 · lap505(strategy) Q8 ·
lap501~504 AI 생산 정지 분석 · lap500 N141 재현성 · lap499(strategy) Q7 · lap498 W26 ACCEPT · lap497 W26 144k · lap356~496(W8~W28-R).
