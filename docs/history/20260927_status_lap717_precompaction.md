# STATUS — 매 바퀴 갱신하는 기억

lap676~707 상세(과거 압축 포인터 4단, G5 milestone 승인, G2 8인×10000 A/B 종료, G4 W2
post-load 종결, G4-P1 baseline)는 이 헤더 블록 22줄 SHA256
`040af76a408205aa53ff8472700899ee235c7b73b35715e078ceb6159534fb8d`으로
`docs/history/20260927_status_lap714_precompaction.md`에 원문 그대로 보존했다. 각 lap
전체 근거는 `docs/history/laps/20260926_lap67{6..9}_*.md`·`lap68{0..9}_*.md`·
`20260927_lap69{5..9}_*.md`·`lap70{0..7}_*.md`에 그대로 있다.

## 지금 상태

**G5는 2026-09-26 21:54 사용자 판단으로 단일플레이 milestone 승인, 최우선 지시 종료**(멀티 동기화는
`UNKNOWN` 메모 유지, 명령당 60B 레코드 최대3회 발행).

**G2는 2026-09-27 03:21 사용자 판단으로 전비10000 트랙 종료, 전비5000(달성 판단 유지)으로 복귀.**
10000 후보(lap691~699, `g2_supply10000_*`)와 근거는 보존만 하고 더 진행하지 않는다.

**G4 W2(post-load AI 유지 계측)는 lap702 non-vacuous `EXACT_POSTLOAD_EDGE_PASS`(save006 slot7,
`_g4_postload_contract` fail-closed 불변식) 달성 후 lap703 middle 독립 검수로 CONFIRMED·종결**
(제품 G4 PASS 아님 — candidate AI 정책 자체가 여전히 없다, `candidate_present=false`). 상세는 위
압축 포인터.

**lap704~711(work) G4-P1 길찾기 baseline→개선후보 v1/v2 FALSIFIED→v3 타임아웃 FALSIFIED,
길찾기 트랙 종료:** 원문 SHA256 보존 후 압축 —
`docs/history/20260927_status_lap712_precompaction.md`(원문 47줄, SHA256
`84dbd4ba962b641b787a94403cc937163fb1e22dc72329a2ee6d2bfd15bec211`). 각 lap 전체 근거는
`docs/history/laps/20260927_lap70{4,5,6,7,8,9}_work_*.md`,
`docs/history/laps/20260927_lap711_work_*.md`에 그대로 있다.

**lap712(work) G4 자유대전 AI 행동 baseline 요약**(원본 N=3 완전 재현, 가장 약한 지표
`idle_worker_count` owner0 0.679 대 owner1 0.129, `command==4` 0건): 전문은 이 문단이 아니라
처음부터 `docs/history/laps/20260927_lap712_work_g4_ai_freeforall_behavior_baseline.md`에
있다(별도 압축 불필요, STATUS는 요약만 유지).

**lap713(work) G4 AI 자유대전 생산 후보 v1(H-CROWD 밀집상한 7→14) FALSIFIED:** 기존
`analysis/memory_maps/ai_production_decision_path_00406770_20260923.md`(lap501)가 확정한
AI 생산 결정 경로 8게이트 중 EXE에 정적 즉치값으로 있는 유일한 생산 억제 상수(`FUN_00406B00`
@`0x406c44`, 동종·동소유 11×11 밀집 ≥7이면 그 kind 발주 중단)를 7→14로 올린 후보
(`patches/ai/g4_production_crowd_cap_v1.py`, named candidate-exe로 `runtime_env.py`
승인 메커니즘 재사용)를 lap712와 같은 seed1 fixture로 N=3 실행 — **owner0/1 종점
생산·군대·자원 지표가 lap712 원본 N=3과 완전히 동일**(효과 0). H-TYPEMAX/H-RATIO는 런타임
표 참조라 이 lap의 정적 상수 접근으로는 애초에 못 바꾼다. `make check` 1061 passed(868.47s)+
`SAFETY_PASS`. 상세
`docs/history/laps/20260927_lap713_work_g4_ai_production_crowd_cap_v1_falsified.md`.

**lap714(work) G4 AI 생산 게이트 라이브 히스토그램(신규 `tools/g4_ai_production_table.py`+
`tools/g4_ai_gate_histogram_probe.py`):** lap713 13:45 지시(어느 게이트가 owner1 발주를
막는지 계측)를 실행. `FUN_00406C70` 디스어셈블로 생산표 레코드 레이아웃을 새로 해독(건물타입/
생산kind/선행유닛kind·count/기술kind, lap501이 미해독으로 남긴 부분)하고, seed1 fixture 280초
동안 owner0/1이 보유한 모든 생산건물×생산레코드 조합을 매 tick 분류했다(`process_vm_readv`
읽기 전용, 새 breakpoint/EXE 패치 없음). **결과: 278개 표본에서 H-TYPEMAX·H-RATIO·H-CROWD는
owner0/1 전부 0회. 100%가 H_AVAIL(가용 플래그=0: owner0 772회/owner1 620회)과
PREREQ_OWN(선행유닛 미보유: owner0 398회/owner1 692회) 둘로만 갈린다** — owner0(HQ type49:
kind7/110→H_AVAIL, kind94→PREREQ_OWN)·owner1(HQ type58: kind31/75→H_AVAIL, kind102/98→
PREREQ_OWN) 모두 최초 건물의 전 생산레코드가 280초 내내 100% 거부, `WOULD_ACCEPT` 0건. 이후
지은 건물(owner0 type50/51, owner1 type60)도 같은 두 사유로 100% 거부. lap712/713이 전제한
"owner1만 약하다"가 아니라 **두 owner 모두 이 두 게이트로 구조적으로 막혀 있음**을 새로 확인.
`make check` 1079 passed(835.61s)+`SAFETY_PASS`, 신규 테스트 18개, 원본 SHA 3회(스모크+
전체런1+전체런2) `source_unchanged=true`, EXE/원본 미변경(순수 메모리 읽기). work tier 다음
middle 검수 요청. 상세
`docs/history/laps/20260927_lap714_work_g4_ai_production_gate_histogram_h_avail_prereq_own.md`.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 제품 미완료 | 1600×1200 원본 구도 외 사용자/제품 승인 |
| G2 | 전비5000 단계 달성(복귀). 8인×10000 트랙 종료(10000 후보 근거는 보존) | 사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 제품 미완료. 길찾기 트랙 종료. 생산후보 v1(H-CROWD) FALSIFIED. 라이브 게이트 계측 완료: H_AVAIL·PREREQ_OWN이 100%, H-TYPEMAX/RATIO/CROWD 0회(lap714) | 가용 플래그·선행조건 표가 이 시나리오에서 생산을 원천 차단하는 이유 미조사, candidate AI 정책 채택된 것 없음, 사용자 승인 |
| G5 | **단일플레이 milestone 승인(2026-09-26 21:54 사용자)** | 멀티 동기화 `UNKNOWN`(별도 표시, 최우선 지시 종료) |

## 지금 막힌 것 (Blockers)

**world (93,56)의 `long_distance_pan` 카메라-복귀 결함은 여전히 후순위 미해결**(lap711 run1이 raw로
재확인 — 카메라 팬 37.6타일 도달은 성공하나 복귀 보정 3회 후에도 drift 21~27타일, 드래그 선택
0/20). world (10,49)를 baseline으로 계속 쓴다. 그 world의 미도착 문제는 lap711로 원인이 좁혀졌다
— 아래 "다음 한 가지" 참고(v3 FALSIFIED, v4 가설 제시).

## 검증 상태

lap714(work, 자체 raw 관측): `make check` **1079 passed(835.61s)** 전부 PASS, 신규 테스트
18개(생산표 디코드 5+게이트 분류기 13), 원본 SHA 3회(스모크20s+전체280s×2) `source_unchanged=true`,
cleanup 매회 ok, EXE/원본 미변경.
lap713: `make check` 1061 passed(868.47s) PASS, 신규 patch 회귀 7개, 원본 SHA 3회 불변.
lap711/709/703 상세는 위 압축 포인터에 원문 그대로 있다.

## 다음 한 가지
**2026-09-27 16:45 운영자 지시(lap717 후속, G5 최우선 유지):** v4(분할 조건 반전) 정지·홀드·순찰 50/50 PASS 수용. lap717이 시간 예산으로 미실행한 **v4 회귀를 다음 work가 먼저 수행**: lap682 이동 paired(원본20/v4 50), lap684 부대지정·호출·저장로드 50/50/50·51번째 미선택, lap688/689 공격(클릭 직후 공격 pending 0x1000004 동시 수신 수), `tools/g5_command_coverage_probe.py` 전체(ALT/Ctrl/Shift 드래그 포함) v4 1회, 크래시 0. 전부 PASS면 middle 재검수 요청, FAIL이면 같은 lap에서 원인 수정.
**2026-09-27 15:49 운영자 판정(G5 명령 범위 결과, 최우선 수정):** `docs/history/laps/20260927_direct_g5_v3_command_coverage.md` — 지면 이동 50/50·ALT/Ctrl/Shift 드래그 PASS, **정지(pending 0x1000002)·홀드(0x1000027)·순찰(0x1000023)이 후보에서 50 중 정확히 20만 수신(FAIL, 매회 재현)**, 미니맵 우클릭은 원본도 무반응(UNKNOWN), 크래시 0. 추정 원인: v3 청크 래퍼(`0x004AE550`→cave `0x004E4D50`, `_WRAPPER_ASM`)가 `word [esp+8]` ∈ {{1,3,4,7,8,9}}일 때만 분할하고 그 외는 원본 20칸 본문(`mov ebp,0x14`@`0x4AE5F4`)으로 보냄. **다음 work(구현 우선):** ① gdb로 정지/홀드/순찰의 `word [esp+8]` 실측(1회), ② **v4**: 분할 조건을 '알려진 비명령 opcode(lap676 목록 0x52,0x56,0x19b,0x19d~0x1a1,0x1ae~0x1bc)가 아니면 분할'로 뒤집거나 실측 값을 목록에 추가 — 전자 권장, ③ `tools/g5_command_coverage_probe.py`로 원본 대 v4 paired 재측정(정지·홀드·순찰·이동 50/50), ④ 회귀: lap682 이동 paired, lap684 그룹/저장로드 50/50/50, lap688/689 공격, 크래시 0, `make check`. 끝나면 middle 재검수.
**2026-09-27 15:20 사용자 지시:** "G1 진행하기 전에 G5 그거 최우선으로 해야겠다". **G5 명령 범위 검증을 G1보다 우선.** 대상: 50기 선택 상태에서 무브(지면 우클릭)·미니맵 우클릭·패트롤·홀드(·스톱)·ALT+드래그·Ctrl+드래그가 원본 20기 대비 후보 v3 50기 전원에 적용되고 크래시가 없는지. 운영자가 별도 세션으로 원본/후보 paired 커버리지 테스트를 진행 중(산출물 `../temp/Syw2plus_patch/20260927_g5_command_coverage/`, 기록 `docs/history/laps/20260927_direct_g5_v3_command_coverage.md`). 루프 work는 그 결과가 나온 뒤 FAIL/UNKNOWN 항목의 원인 수정·재검증을 맡는다. G1(lap716 중단)은 G5 완료 후 재개.
**2026-09-27 15:12 사용자 지시:** "4번 - 길찾기 및 AI는 일단 보류하자. 지금까지 작업분 커밋해서 리모트 깃헙에 푸시하고, 1번 - 원본과 같은 화면 구성인데 고해상도인 것을 최우선으로 해봐". **G4(길찾기·자유대전 AI) 보류**(lap715 건설 게이트 계측은 중단, 도구·기록 보존). 작업분은 운영자가 커밋·푸시(루프의 `LOOP_ALLOW_COMMITS=0`은 유지). **G1 최우선: 원본과 같은 화면 구성(UI 배치·비율·보이는 범위의 구도)을 유지하면서 1600×1200 고해상도로 렌더.** 다음 work는 기존 G1 기록(`docs/history/laps/*g1*`, `analysis/memory_maps/*g1*|*resolution*`)으로 현재 상태·막힌 지점을 먼저 요약하고, 구현 우선으로 가장 작은 다음 후보를 만들어 격리 실행 캡처로 원본(800×600) 대비 구도 동일성·HUD 배치·깨짐 여부를 확인한다.
**2026-09-27 14:45 운영자 방향(lap714 거부 히스토그램 반영, 다음 work — 최신·우선):** 280s
원본에서 H_CROWD/H_TYPEMAX/H_RATIO=0, owner1 거부는 **PREREQ_OWN 692**(선행 건물 미보유; HQ
type58의 kind102/98 등)와 H_AVAIL 620이 전부. ⇒ 병목은 유닛 발주 게이트가 아니라 **AI가 선행
건물을 짓지 않는 것(건설/테크 진행)**. v2: ① AI 건설 결정 루틴(건물 발주 함수·건설 우선순위
표/조건)을 정적으로 특정하고 같은 방식으로 **건설 거부 사유 히스토그램**을 owner별 raw 수집,
② owner1이 선행 건물(PREREQ 대상)을 못 짓는 최다 사유 1개를 상수 1~2개로 완화한 후보 v2,
③ 원본 N=3 대 v2 N=3 paired(지표: owner1 선행건물 보유 시각, PREREQ_OWN 거부 수↓, 생산·
군대↑, 쌓인 자원↓, 크래시 0). 보조: `WOULD_ACCEPT=0` 기록이 샘플 시점 문제인지 확인해 계측
신뢰성 한 줄 기록. H_AVAIL(가용 플래그) 자체가 시나리오 정적 데이터인지도 v2 부산물로 확인.
idle_worker_count·matchup·world(93,56) 팬 복귀는 계속 후순위 보존.

## 바퀴 기록

- lap714(work, 이 세션): 13:45 방향(라이브 게이트 히스토그램)을 실행 — 신규
  `tools/g4_ai_production_table.py`(`FUN_00406C70` 생산표 레코드 레이아웃 해독, 143행=생산65+
  연구78, lap501 수치와 일치)와 `tools/g4_ai_gate_histogram_probe.py`(읽기전용 `process_vm_readv`
  분류기, 새 EXE 패치 없음)로 lap712 seed1 fixture 280초를 owner0/1 전 생산건물×생산레코드
  단위로 매 tick 분류 — **H-TYPEMAX/H-RATIO/H-CROWD 0회, 전량 H_AVAIL+PREREQ_OWN**(owner0
  772+398, owner1 620+692), `WOULD_ACCEPT` 0건. 상세는 위 "지금 상태". `make check`
  1079 passed(835.61s)+`SAFETY_PASS`, 신규 테스트 18개, 원본 SHA 3회 불변. work tier 다음
  middle 검수 요청. 상세
  `docs/history/laps/20260927_lap714_work_g4_ai_production_gate_histogram_h_avail_prereq_own.md`.
- lap713(work, 이 세션): 13:05 판정(AI 자원 소비 개선)을 수행 — `ai_production_decision_path_...md`
  (lap501)가 확정한 8게이트 중 EXE 정적 즉치값인 유일한 생산 억제 상수 H-CROWD(밀집상한, 원래 7)를
  14로 올린 후보(`patches/ai/g4_production_crowd_cap_v1.py`, named candidate-exe로
  `runtime_env.py` 승인 메커니즘 확장)를 만들어 lap712 seed1 fixture로 N=3 실행. 후보 3/3의
  owner0/1 종점 생산·군대·자원 지표가 lap712 원본 N=3과 완전히 동일 — **`FALSIFIED`**(밀집
  게이트가 이 fixture의 두 owner 모두에서 안 걸림). 신규 patch 회귀 테스트 7개,
  `make check` 1061 passed(868.47s)+`SAFETY_PASS`, 원본 SHA 3회 불변, EXE/원본 미변경. work tier
  다음 middle 검수 요청. 상세
  `docs/history/laps/20260927_lap713_work_g4_ai_production_crowd_cap_v1_falsified.md`.
- lap712(work, 이 세션): 12:05 운영자 판정 다음 work ①②를 수행 — 신규
  `tools/g4_ai_behavior_probe.py`(+ 순수 함수 회귀 테스트 4개)로 `g1-baseline
  --g4-chain-goal _custom_game_chain_inject_seed1 --g4-sample-seconds 280`을 원본 N=3 fresh
  실행(3/3 완전 재현). owner별 자원수입/생산/군대규모/첫공격시각/유휴일꾼 5개 지표 산출,
  `idle_worker_count`를 가장 약한 지표로 선정(owner0 0.679 대 owner1 0.129, 자원 순증감 방향과
  일치) — matchup 의존 가능성 명시, 범용 결함 미승격. 280초 내 공격 0건(옛 소스 경로 대비 불일치,
  원인 미조사). v1 구현은 하지 않음(다음 work가 `FUN_004B03D0` 완료조건 특정부터). `make check`
  1054 passed(867.50s)+`SAFETY_PASS`, 원본 SHA 3회 전부 불변, EXE/원본 미변경. 상세
  `docs/history/laps/20260927_lap712_work_g4_ai_freeforall_behavior_baseline.md`.
- lap691~711(work/middle) 요약: G2 8인×10000 트랙 종료(691~699) → G4 W2
  `EXACT_POSTLOAD_EDGE_PASS` 확정·종결(700~703) → G4-P1 baseline·world 양분(704~707) →
  개선후보 v1/v2 FALSIFIED(708~709) → 미니맵 우회 BLOCKED(710) → v3 타임아웃 FALSIFIED·길찾기
  트랙 종료(711). 상세는 `docs/history/20260927_status_lap699_precompaction.md`,
  `docs/history/20260927_status_lap705_precompaction.md`,
  `docs/history/20260927_status_lap709_precompaction.md`,
  `docs/history/20260927_status_lap710_precompaction.md`,
  `docs/history/20260927_status_lap712_precompaction.md`와 각
  `docs/history/laps/20260927_lap{691..711}_*.md`.

G5의 선택/호출/이동/save-load 부분 runtime 증거와 과거 실패 provenance는 `docs/history/laps/` 및
공유 `temp/Syw2plus_patch/`에 보존한다. G5는 사용자 milestone 승인 완료, 멀티 동기화만 `UNKNOWN`이다.
