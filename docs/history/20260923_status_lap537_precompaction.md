# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**. 제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따른다.
압축 직전 STATUS 전문 연쇄: lap502 `docs/history/20260923_status_lap502_precompaction.md`(SHA `a2a12dad…`, lap275~501 계보와 lap500·501 포인터 포함) · lap511 `…status_lap511_precompaction.md`(SHA `d64990c0…`) · lap519 `…status_lap519_precompaction.md`(SHA `6060035c…`) · lap521 `…status_lap521_precompaction.md`(SHA `b05e5b60…`) · lap522 `docs/history/20260923_status_lap522_precompaction.md`(SHA `00bb7f0a8ee38ff9436b144b74d51d025ac3f70bd9961c2dfa2aa6c313922a67`, 129줄) · lap530 `docs/history/20260923_status_lap530_precompaction.md`(SHA `2628567a0d17188e865f84f70326b740b713bb747baecd91244a19bd2059f59d`, 52줄) · **lap534 `docs/history/20260923_status_lap534_precompaction.md`(원문 SHA `852d5c8d510f6184913b78ec3f5340747471b0e35cb9a8f65dc85c13d6bde5d2`, 130줄)**.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
| G2 | **2026-09-23 18:43 사용자 Q8=(ㄱ)** cap5000 도달은 gate-legal 시딩으로 대체 가능. lap522 strategy가 기준 A1~A8·순서 S0~S5·144k 조건부 사전 허가 고정. W35(S0) `CLOSED`(lap524~525, `FEASIBLE`). N182 허용목록 구조적 교전 불능 ⇒ lap526 (나) 채택·X=type2(lap527). W36 실행 2회 `ARM_FAIL`(lap528) → N187 확정·W37 발행(lap529). lap530 work W37 24k 1회 완주(N187 해소, A1·A8'·A5 PASS). lap531 middle 원시 재계산: 라벨 `CYCLE_UNSTABLE` 일치 ⇒ W37 `CLOSED`, 144k 닫힘. N191 = 로드 비인과. N192: op8 수락 1,872/1,872이지만 3/4짝이 39파동 내내 거리4·op8 사망0. **lap532 strategy: N192 경로 (a) W38 접근 진단 probe 채택(type110 양성 대조, 결과 분기 사전 고정), (c) 인접 배치 기각, A6→A6a/A6b(약화 거절), A3→A3'/A3r.** **lap533 work: W38 게임 1회 실행 완주. 자기판정 `PROMOTED_NO_MOVE`(S=144/144, promoted 98.6%·moved 15.3%·hit 0), H7 대조는 `CONTROL_NA`(N195: T0에 type110 생존0, 카드§3 표에 없는 조합).** **lap534 middle: 원시 재계산 라벨 일치. 단 §3 표 밖 조합이고 분기 전제와 원시가 충돌(N196 승격 즉시 철회 78%, N197 이동분도 접근 0, N198 유닛 점유로는 막힘 설명 안 됨, N195 정정 type110=AI 생산분) ⇒ strategy 회부(§88).** **lap535 strategy: 전열 배치 보류, R1을 런타임 gdb watchpoint 귀속 W39로 채택(철회 슬롯 결정적 확인), H7 폐기·H7' 정의, S1 종결 조건 고정(§89).** **lap536 work: W39 게임 1회 완주, gdb hw watchpoint 3개로 `+0x290` 철회 writer pc `0x40d544`(store `0x40d53d`) 확정, H13 바이트 대조(창1,280B) 원본↔후보 차이 0개 ⇒ 자기 라벨 `REVERT_ORIGINAL_LOGIC`(후보 결함 아님). 부가: owner3 소스가 실제 7칸 이동 후 원위치 복귀함을 직접 관측(N197 실증, §90).** 기존 부분 증거: W26 144k `CAP_PROXIMITY_STABLE_144K`(N141). F4(B) W30 `CLOSED`. 트랙② W31~W33 `CLOSED`. 제품 미완료 | 시딩 군대끼리 교전 지속(N192 원거리 접근)·사망/재생산 지속성(A2 0/8·A3 0/8)·A6 사망조건 판별력(N194)·건물 포함 구성(A8)·같은 후보 144k·멀티 동기화 미시험 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
## 다음 한 가지
**middle(Opus5.5): W39 원시 독립 재계산 + `E_rev` 직전 분기 조건 정적 판독**(사양 `docs/work/active/G2_STRATEGY_W38_REVERT_ATTRIBUTION_LAP535.md` §3 `REVERT_ORIGINAL_LOGIC` 행, `ESCALATE_SOL` §90).
- W39(lap536) 결과: `triggers.jsonl`(26건)·`trace.jsonl`·`h13_report.json`을 원시로 재계산해 자기 라벨 `REVERT_ORIGINAL_LOGIC`을 검수한다.
- 그다음 `E_rev`(store `0x40d53d`, pc `0x40d544`) 바로 앞의 분기 조건 하나만 정적으로 읽는다(문서 1회, 60분 또는 후보 2개 반증 뒤 `BLOCKED`).
- 조건이 fixture로 바꿀 수 있으면 그 fixture 변경 + §4 H7' 대조로 work 1회를 예약한다. strategy 재판정 없이 §3 표대로 진행.
- 참고(미조사, 강제 아님): `0x48e44c`(2→1 writer)·`0x40c766`(1→3 재발행 writer).
- S1 교전 트랙 종결 조건(lap535 J4, 불변): 이 경로 + 후속 work 1회 뒤에도 `hit` 짝 <2 ⇒ `BLOCKED`·사용자 보고(후보 결함 확정 시 수리 계보로 예외).

**미결(사용자 전권): Q9(F4 후보 실행 검증 제외 범위, S3에 영향) · Q7-B 3단 마일스톤 · "8인"이 사람인지 AI인지(S4 멀티 영향) ·
스크립트 교전 입력을 (ㄱ) 범위로 볼지(번복 시 이 트랙 정지).**
## 지금 막힌 것 (Blockers)
- **S1 교전 지속 불능(N192, lap531 확정 — W38 lap533 실행·lap534 검수: 승격 후 ≤25 tick 철회 113/144, 접근 0, 유닛 점유 막힘 불지지 ⇒ lap536 W39: 철회 writer pc `0x40d544` 확정, H13 대조 0건 ⇒ 원본 로직(후보 결함 아님), 다음은 middle의 `E_rev` 직전 분기 조건 정적 판독):** op8(`FUN_00415480`)은 1,872/1,872 수락되지만,
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

**2026-09-23 lap533(work, Sonnet5) — W38 게임 1회 실행: self_label `PROMOTED_NO_MOVE`, H7대조 `CONTROL_NA`(N195)**
- 전문: `docs/history/laps/20260923_lap533_work_w38_approach_probe.md`. 산출물
  `temp/Syw2plus_patch/g2_capacity/20260923_lap533_w38_approach_probe/`(`w38_run.py` SHA
  `408827562867dde2a9d81d4b3d8eca8a993ea245d19acc6cb390965bc20364aa`).
- 3파일 게이트 SHA 일치 확인 후 진입, `checks/safety.sh check` `SAFETY_PASS`, 표적 테스트 2개(14 passed).
  게임 1회 foreground 완주(약 128초, baseline 1000tick+파동1~3+H7대조+600tick). 원본 SHA 불변, 후보
  `a10024de…` 일치, 잔류 프로세스 0.
- op8 144/144 수락(전부 |S|). promoted 142/144(98.6%)·moved 22/144(15.3%)·hit 0/144 ⇒ 우선순위표대로
  `PROMOTED_NO_MOVE`. H7 대조 owner0→1·4→5 둘 다 `CONTROL_NA`(no_living_type110). **N195(신규):**
  H8 T0 위치표(1,656 living slot) 전체에 type110이 0기 — seed42 커스텀 게임 체인 goal이 stock 시작유닛을
  주지 않는다(원인 미조사). 카드§3 분기표는 이 조합(CONTROL_NA×PROMOTED_NO_MOVE)을 다루지 않는다.
  게임실행1(카드 최대2회 중 1회 소진, 하네스결함 아님)·source변경0·커밋0. work self-verdict, middle 미검수.

**2026-09-23 lap532(strategy, Opus5.5) — §86 회부 3건 판정: (a) W38 채택·(c) 기각·A6a/A6b·A3'/A3r**
- 전문: `docs/work/active/G2_STRATEGY_N192_APPROACH_PATH_LAP532.md`, 기록 `docs/history/laps/20260923_lap532_strategy_n192_approach_decision.md`, `ESCALATE_SOL` §87.
- 읽기만 한 신규 사실: op8 1,872건 전부 호출 시점 `+0x290`=1·`+0x390`=3. G4 probe 소스도 type2였고 stock 개방 지형에서 거리 63을 접근했다 ⇒ 차이는 재배치 후보·밀집 블록.
- 게임실행0·source변경0·커밋0. 원본 `b56986e0…` 불변(재확인), 3파일·`w37_run.py` SHA가 W37 핀과 일치. source 변경이 없어 `make check` 생략(N22).

**2026-09-23 lap531(middle, Opus5.5) — W37 원시 재계산 라벨 일치 ⇒ `CLOSED`, N191 로드 비인과, N192~N194**
- 전문: `docs/history/laps/20260923_lap531_middle_w37_independent_review.md`, `ESCALATE_SOL` §86. 재계산은
  `temp/Syw2plus_patch/g2_capacity/20260923_lap531_middle_w37_review/recompute_w37.{py,json}`(run_summary 미참조).
- 원시 SHA 9종이 lap530 기록과 일치한다. A1·A8'·A5 PASS, A2 0/8(D_o 합 18, C1=C3), A3 0/8(R_o 0), A6은 필드·로드 PASS이나 로드 뒤 사망 0.
  라벨 `CYCLE_UNSTABLE`(A6 사망 조건만, N194 라벨 문구 틈 — 보수 유지) 일치.
- 게임실행0·source변경0·커밋0. 원본 `b56986e0…` 불변(재확인). source 변경이 없어 `make check`는 생략했다(N22).

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
lap536(work, Sonnet5): W39 게임 1회 foreground 완주(약 93초, 45분 상자 내). gdb hw watchpoint 3개(op8 전 무장)로 `+0x290` 철회 writer pc `0x40d544`(store `0x40d53d`) 확정.
H13 바이트 대조(창1,280B) 원본↔후보 차이 0개 ⇒ 자기 라벨 `REVERT_ORIGINAL_LOGIC`(후보 결함 아님). 부가: B가 실제 7칸 이동 후 원위치 복귀함을 직접 관측(N197 실증).
게임실행1·source변경0·커밋0. `SAFETY_PASS`·표적14 passed(전체 make check는 source불변이라 생략, N22), 원본 불변·잔류0. 다음은 middle의 원시 재계산 + `E_rev` 직전 분기 조건 정적 판독.
lap535(strategy, Opus5.5): §88 판정 — §3 표 확장 안 함·전열 배치 보류, R1을 정적 문서 회차 대신 **W39 런타임 gdb watchpoint 귀속**(철회 writer pc → 그 함수만 원본·후보 대조)으로 채택,
H7 폐기·H7'(개방 구역 type2 1:1) 정의, S1 종결 조건 고정. 게임실행0·source변경0·커밋0. `SAFETY_PASS`·`CONTEXT_PASS`(STATUS 115·INBOX 299·APPROVALS 46줄), 원본 불변. 다음은 work W39 게임 1회(문서 연속 2회 — 실행 없으면 STOP).
lap534(middle, Opus5.5): W38 원시 독립 재계산 → `PROMOTED_NO_MOVE`·`CONTROL_NA` 일치. §3 표 밖이고 전열 배치 전제가 원시와 충돌
(N196 승격 즉시 철회 113/144, N197 이동분 접근0, N198 유닛 점유 BFS 경로 120/144, N195 정정 type110=AI 생산분) ⇒ strategy 회부 §88(권고 R1 철회 writer 정적 추적).
게임실행0·source변경0·커밋0. 원본 불변 재확인. `SAFETY_PASS`·`CONTEXT_PASS`(STATUS 108·INBOX 297·APPROVALS 46줄).
lap533(work, Sonnet5): W38 게임 1회 실행 완주. self_label `PROMOTED_NO_MOVE`(S=144/144, promoted98.6%·moved15.3%·hit0),
H7 대조 `CONTROL_NA`(N195: T0 type110 생존0, 카드§3 표 밖 조합). 게임실행1·source변경0·커밋0.
`SAFETY_PASS`·표적14 passed(전체`make check`는 source불변이라 생략, N22). 다음은 middle 원시 재계산.
lap532(strategy, Opus5.5): §86 회부 판정. N192 → (a) W38 접근 진단 probe(파동3 + type110 양성 대조, 원시 추적, 분기 사전 고정), (c) 인접 배치 기각(짝(2,3) 반증),
A6 약화 거절·A6a/A6b 분리(N194 틈 닫음), A3→A3'/A3r·op1 조건 `used+reserved+10≤5000`. 게임실행0·source변경0·커밋0. `SAFETY_PASS`·`CONTEXT_PASS`(STATUS 111·INBOX 295·APPROVALS 46줄), 판정 문서 SHA `9f055798…`. 다음은 work W38 실행.
lap531(middle, Opus5.5): W37 원시 독립 재계산 → 라벨 `CYCLE_UNSTABLE` 일치 `CLOSED`. N191 로드 비인과(op8 교전은 tick7,801에 끝남),
N192 op8 수락≠교전(3/4짝 거리4 고정·사망0), N193 A3 정의 위험, N194 라벨 문구 틈. strategy 회부 3건. 게임실행0·source변경0·커밋0.
`checks/safety.sh check` `SAFETY_PASS`·`checks/context_limits.py` `CONTEXT_PASS`(STATUS 104·INBOX 290·APPROVALS 46줄).
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
