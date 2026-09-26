# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**. 제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따른다.
압축 직전 STATUS 전문 연쇄: lap502 `docs/history/20260923_status_lap502_precompaction.md`(SHA `a2a12dad…`, lap275~501 계보와 lap500·501 포인터 포함) · lap511 `…status_lap511_precompaction.md`(SHA `d64990c0…`) · lap519 `…status_lap519_precompaction.md`(SHA `6060035c…`) · lap521 `…status_lap521_precompaction.md`(SHA `b05e5b60…`) · lap522 `docs/history/20260923_status_lap522_precompaction.md`(SHA `00bb7f0a8ee38ff9436b144b74d51d025ac3f70bd9961c2dfa2aa6c313922a67`, 129줄) · lap530 `docs/history/20260923_status_lap530_precompaction.md`(SHA `2628567a0d17188e865f84f70326b740b713bb747baecd91244a19bd2059f59d`, 52줄) · lap534 `docs/history/20260923_status_lap534_precompaction.md`(원문 SHA `852d5c8d510f6184913b78ec3f5340747471b0e35cb9a8f65dc85c13d6bde5d2`, 130줄) · lap537 `docs/history/20260923_status_lap537_precompaction.md`(원문 SHA `7f69cde47398d29a7a6f4aa153513628634d2a6be4978e8aadafa381a7852ead`, 128줄) · **lap539 `docs/history/20260923_status_lap539_precompaction.md`(원문 SHA `7493289bc36544911075d4f8cdb6965e0cea78491b6b213b272c066eb1419c9a`, 114줄)**.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
| G2 | **2026-09-23 18:43 사용자 Q8=(ㄱ)** cap5000 도달은 gate-legal 시딩으로 대체 가능. lap522 strategy가 기준 A1~A8·순서 S0~S5·144k 조건부 사전 허가 고정. W35(S0) `CLOSED`(lap524~525, `FEASIBLE`). N182 허용목록 구조적 교전 불능 ⇒ lap526 (나) 채택·X=type2(lap527). W36 실행 2회 `ARM_FAIL`(lap528) → N187 확정·W37 발행(lap529). lap530 work W37 24k 1회 완주(N187 해소, A1·A8'·A5 PASS). lap531 middle 원시 재계산: 라벨 `CYCLE_UNSTABLE` 일치 ⇒ W37 `CLOSED`, 144k 닫힘. N191 = 로드 비인과. N192: op8 수락 1,872/1,872이지만 3/4짝이 39파동 내내 거리4·op8 사망0. **lap532~536 계보(lap539 압축, 원문 `docs/history/20260923_status_lap539_precompaction.md`):** lap532 strategy N192 경로 (a) W38 채택 → lap533 work W38 `PROMOTED_NO_MOVE` → lap534 middle 원시 재계산 일치·strategy 회부(§88) → lap535 strategy R1→W39 런타임 귀속 채택(§89) → lap536 work W39 완주, 철회 writer pc `0x40d544` 확정·H13 대조 0개 ⇒ `REVERT_ORIGINAL_LOGIC`(§90). **lap537 middle: 원시 재계산 라벨 일치(창 밖 차이도 전부 풀 기준 재배치). `E_rev`는 대기 cmd2(CmdStop `FUN_004AEDA0`)의 무조건 커밋이라 fixture 분기 없음, 발행 지점 127곳 ⇒ `BLOCKED(static)`·§3 표 밖 strategy 회부(§91, 권고 W40 발행자 런타임 귀속).** **lap538 strategy: W40 채택(J4 즉시 적용 기각), W40 = J4 후속 work 1회, 예외 E2만, 분기·`BLOCKED` 선택지 사전 고정(§92).** **lap539 work: W40 게임 1회 완주(108초). I_A·I_B의 ISSUER_SITE가 동일 — call `0x48e83c`(uid 로드 후 CmdStop, 게이트 2개 `0x471600`/`0x471af0` 통과 시만 도달), lap537의 두 후보(c1=FUN_0040C390·c2=이동실행부) 둘 다 아님을 c1 기계 대조로 확정. 해당 창 바이트차0(후보 결함 아님). R_B(CmdMove 재발행) site `0x48bba3`, 창 56바이트차는 디코드 결과 전부 이미 알려진 풀/존재배열 재배치 값과 일치(커버리지 도구 사각으로 판단, lap402 D1 계열). 자기 라벨 `ISSUER_FOUND(A=UNCLASSIFIED_pending_middle_read,B=UNCLASSIFIED_pending_middle_read)` — OWNER_AI/UNIT_OTHER 분류는 카드가 middle 몫으로 명시(§93).** **lap540 middle: 원시 재계산 일치, 분류 `ISSUER_FOUND(A=UNIT_OTHER,B=UNIT_OTHER)`(§94) ⇒ 카드 §3 2행.** **lap541 middle: 0 출구 판독 `E2_NOT_MET` — 유력 `0x472042` 추격 포기(`+0x216`>`+0x218`), 상한은 원본 전투 타입 공통 1이라 fixture 값 없음, A·B 실제 출구 미확정 ⇒ S1 `BLOCKED` 대상, 전열 배치 재개 여부 strategy 회부(§95).** **lap542 strategy: (c) 채택 — N199(T0 전폭 가로 띠 적층, W38 op8 선분 전부 다른 띠 횡단)로 전열 배치 W41 1회를 S1 교전 경로의 마지막 실행으로 연다(§96).** 기존 부분 증거: W26 144k `CAP_PROXIMITY_STABLE_144K`(N141). F4(B) W30 `CLOSED`. 트랙② W31~W33 `CLOSED`. 제품 미완료 | 시딩 군대끼리 교전 지속(N192 원거리 접근)·사망/재생산 지속성(A2 0/8·A3 0/8)·A6 사망조건 판별력(N194)·건물 포함 구성(A8)·같은 후보 144k·멀티 동기화 미시험 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
## 다음 한 가지
**work(Sonnet5): W41 전열 배치 교전 + 출구 판별 게임 1회 foreground 완주 → 자기 라벨.** 사양 `docs/work/active/G2_STRATEGY_W41_FRONT_LINE_LAP542.md` §2(middle 카드 없음), `ESCALATE_SOL` §96.
- 순서: W40 `w40_run.py` SHA `6417a63e…` 확인 → `SAFETY_PASS`·표적 테스트 → `w41_run.py`(H17 type2만 전열 anchor · H18 `+0x1f0/+0x216/+0x218/+0x708/+0x31c/+0x1d4/+0x692/+0x682` + 모든 소스 촘촘 추적 · H19 gdb 끔 · H20 배치 확인) → 게임 1회(45분 상자).
- 전열: 짝 (0,1) y24/32 · (2,3) y40/48 · (4,5) y76/84, x=20, 사이 빈 7행. 짝 (6,7)은 기존 띠 기하 그대로(같은 실행 대조, 라벨 계산 제외).
- 라벨: `ENGAGED_FRONT`(전열 3짝 중 `hit_attr` 짝 ≥2) ⇒ middle이 전열 fixture로 S1 24k 재발행 / `NO_ENGAGE_C|V|UNRESOLVED` ⇒ S1 `BLOCKED` 확정·사용자 보고 (가)~(라) / `PROBE_VOID`·`BLOCKED` ⇒ 결함일 때만 1회 재시도.
- **W41은 S1 교전 경로의 마지막 실행이다(§96 L2).** streak: lap540·541·542 연속 문서 → lap542가 **계속** 판정. 이번 회차가 게임 실행 없이 끝나면 STOP·사용자 보고.
- 근거 N199(lap542): T0 시딩이 행 우선이라 owner마다 전폭 가로 띠가 된다. W38 op8 선분 49종 전부 다른 띠를 가로지른다(사이 ≥109기). y20~51·y73~88은 빈 행이다.
- 확정(lap541): 포기 출구 `0x472042`는 칸 진척 없는 경계 틱 2회에서 발동한다. 복귀 모드 writer = op8 `0x415535`. 공격 뒤 출발점 복귀는 원본 설계다.

**미결(사용자 전권): Q9(F4 후보 실행 검증 제외 범위, S3에 영향) · Q7-B 3단 마일스톤 · "8인"이 사람인지 AI인지(S4 멀티 영향) ·
스크립트 교전 입력을 (ㄱ) 범위로 볼지(번복 시 이 트랙 정지).**
## 지금 막힌 것 (Blockers)
- **S1 교전 지속 불능(N192, lap531 확정 — W38 lap533 실행·lap534 검수: 승격 후 ≤25 tick 철회 113/144, 접근 0, 유닛 점유 막힘 불지지 ⇒ lap536 W39: 철회 writer pc `0x40d544` 확정, H13 대조 0건 ⇒ 원본 로직(후보 결함 아님) ⇒ lap537: 철회 = 대기 정지 명령(cmd2) 커밋, 발행자 127곳 중 미확정 ⇒ lap538 §92: W40 런타임 귀속 ⇒ lap539 work: 발행 site `0x48e83c` 확정(c1/c2 후보 둘 다 아님, 창 바이트차0) ⇒ lap540 middle: 발행 = 유닛 공격 case `FUN_0048DDD0`/게이트 `FUN_00471AF0`==0, A·B `UNIT_OTHER` ⇒ lap541 middle: `E2_NOT_MET`(유력 추격 포기 `0x472042`, 상한 공통 1, 출구 미확정), strategy 회부 §95 ⇒ lap542 strategy: N199 시험 배치 자체가 모든 경로를 띠로 막음 ⇒ 전열 배치 W41 마지막 1회, 실패 시 `BLOCKED` 확정 §96):** op8(`FUN_00415480`)은 1,872/1,872 수락되지만,
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
**2026-09-23 lap542(strategy, Opus5.5) — §95 판정 (c): 전열 배치 W41 1회(마지막), N199 근거(§96)**
- 판정 `docs/work/active/G2_STRATEGY_W41_FRONT_LINE_LAP542.md`(SHA `70d06e93…cbcb9f5`), 기록 `docs/history/laps/20260923_lap542_strategy_w41_front_line_decision.md`, 도구 `temp/…/20260923_lap542_strategy_w41/band_crossing.{py,json}`.
- 이전 바퀴 검수: lap541 temp 8파일·W40 원시 SHA 일치, `0x472021`~`0x472049` 재판독 일치, 원본 `b56986e0…` 불변. 게임실행0·source변경0·커밋0. source 불변이라 `make check` 생략(N22).
- 문서 반영 후 `checks/safety.sh check` `SAFETY_PASS`, `checks/context_limits.py` `CONTEXT_PASS`(STATUS 117·INBOX 311·APPROVALS 46줄).
**2026-09-23 lap541(middle, Opus5.5) — `FUN_00471AF0` 0 출구 판독 `E2_NOT_MET`, strategy 회부(§95)**
- 전문: `docs/history/laps/20260923_lap541_middle_w40_exit_read.md`, 도구 `temp/Syw2plus_patch/g2_capacity/20260923_lap541_middle_w40_exit/`.
- 이전 바퀴 검수: lap540 도구·산출 7파일과 W40 원시·bin SHA 일치, 원본 `b56986e0…` 불변. 게임실행0·source변경0·커밋0. source 불변이라 `make check` 생략(N22).
- 문서 반영 후 `checks/safety.sh check` `SAFETY_PASS`, `checks/context_limits.py` `CONTEXT_PASS`(STATUS 111·INBOX 308·APPROVALS 46줄).
**2026-09-23 lap540(middle, Opus5.5) — W40 원시 재계산 일치 + 분류 `ISSUER_FOUND(A=UNIT_OTHER,B=UNIT_OTHER)`(§94)**
- 전문: `docs/history/laps/20260923_lap540_middle_w40_review_issuer_classification.md`, 도구 `temp/Syw2plus_patch/g2_capacity/20260923_lap540_middle_w40_review/`.
- 재계산: CmdStop 127·CmdMove 44 일치, I_A t1103·I_B t1281 site `0x48e83c`, R_B t1283 `0x48bba3`, B 복귀 좌표 (56,17). 두 번째 정지(t1112·t1470)는 도착 정지 c1 `0x40c3a9`.
- 판독: `FUN_0048DDD0`(유닛 갱신, `switch(+0x290)` 값4) ← `FUN_0040FC70` ← `FUN_0041CB40` 슬롯 순회. AI owner 스텝 경로 아님. 창 차이는 전부 풀 재배치(후보 결함 아님).
- 게임실행0·source변경0·커밋0. 원본 `b56986e0…` 불변. `SAFETY_PASS`·`CONTEXT_PASS`. source 불변이라 `make check` 생략(N22).
**2026-09-23 lap539(work, Sonnet5) — W40 게임 1회 완주: I_A·I_B 공통 site `0x48e83c` 확정(c1/c2 후보 둘 다 아님), R_B site `0x48bba3`, 자기 라벨 `ISSUER_FOUND(UNCLASSIFIED_pending_middle_read)`**
- 전문: `docs/history/laps/20260923_lap539_work_w40_stop_issuer_runtime_attribution.md`, 산출물 `temp/Syw2plus_patch/g2_capacity/20260923_lap539_w40_stop_issuer/`, `ESCALATE_SOL` §93.
- 게이트 3파일 SHA 일치·W39 하네스 SHA 일치 → `SAFETY_PASS` → 표적14 passed → `w40_run.py`(W39 파생, H14~H16만 교체) 작성·구문검증·합성트리거 단위검증 후 실행.
- negative finding(실행 전 자체 반증): ISSUER_FN 일반 해석용 push-ebp/mov-ebp,esp prologue-scan 휴리스틱을 시도했으나 c1 후보 `FUN_0040C390` 자체가 `56 6a 00 8b f1`(push esi 관례)로 시작함을 원본 objdump로 확인해 기각. c1 앵커(`0x40c390`→ call `0x40c3a9`→call+5 `0x40c3ae`)만 기계적으로 확정해 사용, 일반 ISSUER_FN·c2는 middle 몫으로 유보.
- 게임 1회(108초): M0'=True, 트리거20건(WA8·WB8·WC4), H11 A=3800·B=3185 W38·W39와 일치(결정성 재확인), A5 무결성 위반 전부0, 원본 불변, 잔류0.
- I_A·I_B ISSUER_SITE 동일: call `0x48e83c`(uid로드→CmdStop, 게이트 `call 0x471600`==1 & `call 0x471af0`==0). c1 불일치(제3의 발행 함수, 런타임 최초 확정). 창(`0x48e43c`~`0x48e93c`) 바이트차0(후보 결함 아님).
- R_B site `0x48bba3`(CmdMove 재발행). 창(`0x48b7a3`~`0x48bca3`) 56바이트차는 14묶음×4B 32-bit immediate, 값 디코드 결과 전부 이미 알려진 풀/존재배열 재배치(`0x66b7xx→0x108cxxx`, `0x8990c8→0x17b8658`)와 일치 — `collect_fixup_sites()` 커버리지 사각으로 판단(확정은 middle 몫, lap402 D1 계열).
- 게임실행1·source변경0·커밋0. `SAFETY_PASS`·표적14 passed(전체 make check는 source불변이라 생략, N22), 원본 불변·잔류0. work 자기판정, middle 미검수.
**2026-09-23 lap538(strategy, Opus5.5) — §91 판정: W40 채택, J4 예산 해석·E2 예외·`BLOCKED` 선택지 고정(§92)**
- 판정 `docs/work/active/G2_STRATEGY_W40_STOP_ISSUER_LAP538.md`(SHA `542f45fa…04ef9`), 기록 `docs/history/laps/20260923_lap538_strategy_w40_stop_issuer_decision.md`.
- 검수: W39 원시·lap537 재계산 6파일 SHA 일치, CmdStop 127·CmdMove 44 재계산 일치, cmd2 무조건 커밋 확인. 정황: CmdStop 74곳이 `0x47` 대역(AI dispatcher `FUN_004755D0` 소재).
- 게임실행0·source변경0·커밋0. 원본 `b56986e0…` 불변. `SAFETY_PASS`·`CONTEXT_PASS`(STATUS 114·INBOX 302·APPROVALS 46줄). source 불변이라 `make check` 생략(N22).
**lap534~537 계보(lap539 압축, 원문 전량 `docs/history/20260923_status_lap539_precompaction.md` 원문 SHA256
`7493289bc36544911075d4f8cdb6965e0cea78491b6b213b272c066eb1419c9a`, 114줄):** lap537(middle) W39 원시 재계산 `REVERT_ORIGINAL_LOGIC` 일치·`E_rev` 정적판독 `BLOCKED(static)`⇒strategy회부(§91) →
lap536(work) W39 완주, 철회 writer pc `0x40d544` 확정·H13대조0건⇒`REVERT_ORIGINAL_LOGIC` → lap535(strategy) R1→W39런타임귀속채택(§89) →
lap534(middle) W38원시재계산일치·strategy회부(§88, N195정정·N196~N198). 게임실행 lap536(1)·source변경0·커밋0.

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
lap542(strategy, Opus5.5): §95 판정 (c) — T0 시딩이 행 우선이라 전 owner가 전폭 가로 띠로 쌓여 W38 op8 선분 49종 전부가 다른 띠를 가로지름을 확인(N199). (가)~(다) 보고 전제가 흔들려 전열 배치 W41 1회를 연다.
W41 = S1 교전 경로 마지막 실행(실패 시 `BLOCKED` 확정, (라) 이동 후 공격 선택지 추가). streak 3회째 계속 판정. 게임실행0·source변경0·커밋0.
lap541(middle, Opus5.5): `FUN_00471AF0` 0 출구를 정적으로 좁혔다 — (V) 표적 무효 계열 / (C) `0x472042` 추격 포기. `+0x218`(행 `+0x4A`)은 type 2·후보 6종·type 110 모두 1이라 fixture 값이 아니다.
A·B 실제 출구 미확정 ⇒ `E2_NOT_MET`, S1 `BLOCKED` 대상. 전열 배치 재개 여부는 strategy 회부(§95). 복귀 모드 writer = op8 `0x415535` 확정. 게임실행0·source변경0·커밋0.
lap540(middle, Opus5.5): W40 원시 재계산 라벨 일치. `0x48e83c` 발행 함수는 유닛 갱신 상태기계 `FUN_0048DDD0`의 공격 case, 게이트는 `FUN_00471AF0`(공격 1틱 처리)==0이다.
owner 루프가 아닌 슬롯 순회에서 불린다 ⇒ A·B `UNIT_OTHER`(ai 필드 읽기는 같은 편 표적 분기에만 있음, §94 명시). 카드 §3 2행 → 다음 middle이 출구 1개 판독 후 E2/`BLOCKED`. 게임실행0·source변경0·커밋0.
lap539(work, Sonnet5): W40 게임 1회 foreground 완주(108초, 45분 상자 내). I_A·I_B ISSUER_SITE가 동일 — call `0x48e83c`(uid로드→CmdStop, 게이트 2개 통과 시만), lap537 두 후보(c1/c2) 둘 다 아님을
c1 기계 대조로 확정. 해당 창 바이트차0(후보 결함 아님). R_B site `0x48bba3`(CmdMove 재발행), 창 56바이트차는 디코드 결과 전부 이미 알려진 풀/존재배열 재배치 값과 일치(커버리지 사각, lap402 D1 계열).
자기 라벨 `ISSUER_FOUND(A=UNCLASSIFIED_pending_middle_read,B=UNCLASSIFIED_pending_middle_read)` — OWNER_AI/UNIT_OTHER 분류는 카드가 middle 몫으로 명시, work는 시도하지 않음.
negative finding: ISSUER_FN 일반 해석용 prologue-scan 휴리스틱은 c1 후보 자체가 `push esi`로 시작함을 실행 전 objdump로 반증해 기각, c1 단일 앵커 기계 대조만 사용.
게임실행1·source변경0·커밋0. `SAFETY_PASS`·표적14 passed(전체 make check는 source불변이라 생략, N22), 원본 불변·잔류0. 다음은 middle의 원시 재계산 + ISSUER_FN 1회 판독(§93).
lap538(strategy, Opus5.5): §91 판정 — W40(정지 명령 발행자 런타임 귀속) 채택, J4 즉시 적용 기각. W40 = J4 후속 work 1회, 예외는 E2(유닛 로직 fixture 원인 주소 특정 시 work 1회)뿐.
판정식·분류·분기·`BLOCKED` 선택지 (가)(ㄴ)예외/(나)사람 슬롯/(다)트랙 중단 사전 고정. 게임실행0·source변경0·커밋0.
lap534~537(압축, 원문 `docs/history/20260923_status_lap539_precompaction.md` 원문 SHA256 `7493289b…19bd419c9a`): lap537(middle) W39 `REVERT_ORIGINAL_LOGIC`일치·`BLOCKED(static)`⇒strategy회부(§91) ·
lap536(work) W39 완주·철회writer`0x40d544`확정·H13대조0건 · lap535(strategy) R1→W39런타임귀속채택(§89) · lap534(middle) W38원시재계산일치·strategy회부(§88). 게임실행 lap536(1)·source변경0·커밋0.
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
