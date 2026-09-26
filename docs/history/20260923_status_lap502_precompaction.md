# STATUS 압축 직전 전문 보존 (lap502, 2026-09-23)

원문 SHA256 `a2a12dad6c95e688f8290d783b1bc63e4ad3373090de81ffd4766b57d2f1a0ec` · 130줄. 삭제·재해석 없이 그대로 옮겼다.
이전 precompaction 스냅샷(`20260923_status_lap501_precompaction.md`) 포인터는 본문 안에 연쇄 보존된다.

---

# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**. 제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따른다.
과거 lap275~500 계보와 이번 압축 직전 STATUS 전문은 `docs/history/20260923_status_lap501_precompaction.md`(SHA `9ef8f6760cd61b99baff191a0ceee9d44ad73d0f67861574513355e45f2ee453`, 147줄)에 그대로 있다(그 안에 lap500·lap495 precompaction 스냅샷 포인터가 연쇄 보존됨).
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
| G2 | W26(144k) `CLOSED`·종합 판정 `CAP_PROXIMITY_STABLE_144K`(부분 증거), lap498 독립 재계산 불일치0, U0~U3 PASS, U4=(a)호스트 페이지 회수. **lap500이 N141을 강등**: 사전 고정식으로는 24k에서도 `N141_REPRODUCED`(전원정지 32.21%)지만 **두 run은 독립 복제가 아니라 같은 결정적 궤적**(N144)이고, **같은 궤적의 144k 연장에서 8인 중 5인이 24k 창 이후 재개**(owner3은 33,753tick 정지 후 재개)했다(N145) ⇒ **"정지 상태 생존"은 지지되지 않고 종단 여부 UNKNOWN(창 절단)**. 장부 지속성(최종 tick144,023에 8/8 owner `used`∈[4995,5000], fault·cap초과·장부불일치 0, 72분51초)은 실측 지지 유지. N146: 144k 전체 사망 9건/소실14기·생산116건(전투 축 미성립 N87 수치 재확인). **lap501: AI 생산 정지의 코드 경로를 원본 바이트로 확정 — 8게이트 중 자원을 보는 것이 0개라 "자원 96.8% 잔존+정지"는 정상 동작이고, 영구 정지 후보는 H-RATIO/H-TYPEMAX/H-CROWD 셋(전부 구성 동결 시 고정). 원인 특정은 런타임 값이 없어 `UNKNOWN`.** 제품 미완료 | lap356~500 계보는 precompaction 스냅샷과 `docs/history/laps/`에. 상세는 아래 「검증 상태」 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
## 다음 한 가지
**lap501이 정적 추적을 끝냈다(§아래). 다음 한 가지: work(Sonnet5)가 그 문서 §7의 읽기 전용
런타임 probe로 H-RATIO / H-TYPEMAX / H-AVAIL / H-CROWD / H-STATE를 가른다.**
메모리 **읽기만** 하므로 (ㄴ) 승인 대상이 아니고 AI/생산 로직을 건드리지 않는다. 설계는
`analysis/memory_maps/ai_production_decision_path_00406770_20260923.md` §7.
필수 조건: **판정식을 데이터 개봉 전에 고정**(lap500 선례) · lap500 N144의 **fixture 결정성**
때문에 같은 조건 새 run을 쌓지 말고 **기존 궤적에 관측 채널만 추가해 1회** 실행 ·
lap410 정정2대로 **`0x008990C8`·1200 하드코딩 진단 DLL 채널 사용 금지**(재배치 후보에서 0기 보고).
거부되지 않는 (건물,kind) 쌍이 남으면 **8게이트 밖에 원인이 있다**는 뜻이므로 그대로 보고한다.
원본/참고 저장소 **읽기 전용**, **AI/생산 로직 변경·패치 착수 금지**(여전히 (ㄴ) 대기).
**사용자 판정 완료 2건(2026-09-23 04:13, APPROVALS 기록):** lap404=**(가)** 일시 초과 표시 허용
·라이브 `used`≤5000만 강제 / F4=**(B)** 전비 장부 32-bit 확장 채택(저장포맷 동반). F4(B) 착수
범위·순서는 이 분석 뒤 strategy/middle이 카드로 정한다.
**미결(사용자 전권): Q7-A=(ㄴ) AI 변경 예외 · Q7-B 3단 마일스톤 · (ㄱ) · (ㄷ).**
## 지금 막힌 것 (Blockers)
- **F4(lap395 확정): 안전상한 UNKNOWN — 어떤 uniform cap도 랩을 막지 못한다.** donor 이전+gate-legal 재생산 펌프로 cap 1500/4095/5000 전부에서 수신 used가 32,785 도달, cap≤4095 안전상한·즉치2개 카드 착수 근거 상실. 실제 게임 도달성은 여전히 UNKNOWN. 상세는 precompaction 스냅샷. lap500 재계산에서도 무결성 위반 0 ⇒ **(C) 유지**.
- **N141/N145(lap498 제기·lap500 정정): fixture 내 G2 "실제 플레이" 경로가 소진됐다.** 자연도달
  `NOT_FEASIBLE`(W23 A1) + 전투 축 기하로 생성 불가(N87, lap500 N146이 수치 재확인) + 건물 계층 부재
  (W26 §0-3) + 시딩 축 장기 정체. **다만 "완전 정지"는 lap500에서 창 절단으로 강등됐다** — 같은
  결정적 궤적(N144)의 연장에서 5 owner가 재개했고 W26 종단 정지 40,484tick은 이미 재개된 최대 정지
  36,236tick의 1.12배뿐이다. **같은 조건 재실행은 결정성 때문에 새 정보를 주지 않는다(N144).**
  종단 여부를 가리려면 (ㄱ) 창 연장(≳200k) · (ㄴ) 다른 seed/구성 · (ㄷ) (ㄴ)-승인 AI/설정 변경 중
  하나가 필요하며 셋 다 모델 권한 밖이거나 사용자 전결이다. **(ㄴ) 자체는 사용자 전결 유지.**
- **G2 구조통합 blocker(owner당1200 초과·저장호환 확장):** 저비용 다수 구성 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·저장/LAN 일관 계약이 미구현. 현재 동결된 fixture 축과는 별도 축이며 그대로 남아 있다. 상세는 precompaction 스냅샷.
- G1/G4 개별 blocker(R1/S1 클릭·좌표 포렌식, AI runtime 실패 등)는 전문 그대로 precompaction 스냅샷과 `docs/history/laps/`에 보존되며 G2 성립 전까지 작업 대상이 아니다.
## 검증 상태
**2026-09-23 lap501(middle, Opus5) — AI 생산 정지 원인 정적 추적 = 경로 확정 PASS·원인 특정 `UNKNOWN`**
(전문 `analysis/memory_maps/ai_production_decision_path_00406770_20260923.md`, lap 기록
`docs/history/laps/20260923_lap501_middle_ai_production_static_trace.md`, 회부 `ESCALATE_SOL` §64).
원본 `b56986e0…`를 **직접 디스어셈블**(참고 저장소 Ghidra는 대조용): `FUN_00406770`(진입, G-1 상태100·
G-2 tick≥50·G-3 `+0x1D8&0x80000`·G-4 20tick 케이던스) → `FUN_00406B00`(G-5 per-owner AI 활성
`0x956772+owner*0x3ABC`, 추첨 `FUN_00406C70(0)` LCG PC `0x406D15`) → `FUN_0043E7F0`(G-6 유효성) →
G-7 밀집 검사 → G-8 발주 `0x4AF5E0`. **결론: 8게이트 중 자원을 보는 것이 0개** ⇒ "자원 96.8% 잔존 +
완전 정지"는 이상이 아니라 정상 동작이고 N81의 자원 배제는 옳았다. **영구 정지 후보 3(구성이
동결되면 판정도 동결 — lap500 N146의 144k 소실14기와 정합):** **H-RATIO** `cur*100/(ctrl+0x200A) >
type_spec+0x32`(참고 저장소의 `ai_production_ratio_cap`과 오프셋 일치) · **H-TYPEMAX** `cur >=`
`type_spec+0x34` 또는 시나리오 override `0xB3DE70+(kind+owner*0x19C)*2`, `cur`=`0x89A388+(kind+owner*200)*2` ·
**H-CROWD** 건물 타일 ±5의 11×11=121셀에 **동종·동소유 7기 이상**이면 발주 안 함.
타입스펙 스트라이드 **`0x394`**(lea 사슬 9→19→57→229 후 `shl 2`=916) 베이스 `0x9B5228` 확정.
G-7의 `0x66B81D/1E`는 이 저장소가 독립 확정한 풀 `0x66B790`+`0x8D/0x8E`와 **정확히 일치**(교차 확인).
**생산표 `DAT_004EC514` 원본 파일 직독:** 종료는 고정143이 아니라 **다음 레코드 `+0x00` flag==`0xFFFE`**
sentinel ⇒ **143엔트리=생산65+연구78**(참고 저장소 문서와 독립 일치), flag 143건 전부 `0x000F`(진영 마스크),
**생산 건물 27종·건물당 kind {1:5, 2:10, 3:8, 4:4}** ⇒ 건물 하나를 영구히 벙어리로 만드는 데 kind 최대 4개
(5종 건물은 **1개**)면 충분. **자체 결함 정정:** 표 덤프 초판이 종료 워드를 `+0x0E`로 오인(바이트로 정정, 무영향).
**한계:** 세 후보가 읽는 표(`0x9B5228`·`0x89A388`·`0xB3DE70`/`0xB3E000`·`0x956770`·풀 `0x66B790`)는
전부 rva `0xF9000` **바깥**이라 파일에 초기값이 없다 ⇒ **정적으로 값을 알 수 없고 원인 특정 불가**.
"농부60·나머지30"도 참고 저장소 주석 출처이며 **미검증**. **참고 저장소 오염 주의:** `ai_strategy.c`는
“바이너리 미발견” 재현 전용(미사용), “bprod owner1 전용”은 **재현 엔진 결함**이고
원본 `FUN_00406B00`엔 소유자 고정 게이트가 없다(디스어셈블 재확인). **부수(F4(B) 범위 입력):**
이 경로에서만 16-bit 필드 3곳 추가 — `0x89A388`·`ctrl+0x200A`·`0xB3DE70`/`0xB3E000`.
게임실행**0**·제품 source 변경**0**·커밋**0**·work 카드 발행**0**·598 passed·`SAFETY_PASS`·`CONTEXT_PASS`.
**독립 검수 없음**(middle 자기 결과) — 다음 새 세션이 원시에서 재계산해야 2단이 선다.

**2026-09-23 lap500(middle, Opus5) — 항1 N141 재현성 = `N141_REPRODUCED`(사전 고정식)이나 **독립 재현 아님**,
항2 rider = owner2형은 144k 고유 분기** (전문 `docs/history/laps/20260923_lap500_middle_n141_reproducibility.md`,
회부 `loop/ESCALATE_SOL` §63, 사전 고정식 `temp/…/20260923_lap500_middle_n141_reproducibility/PREREGISTRATION.md`).
§62가 허용한 middle 1회차 예외. **판정식을 데이터 개봉 전에 고정**하고 lap448 24k 원시 712표본
(SHA `c3cf99a5…`)만으로 재계산했다(`run_summary.json`·lap449 수치는 사후 대조 전용).
**항1:** owner별 `last_change_tick`은 owner7 2,582 ~ owner0 16,290(전문은 lap 기록에) ⇒ 전원동결
**7,739tick(32.21%)**, `live`1,247 고정, 리더 아티팩트 배제 충족 ⇒ **`N141_REPRODUCED`**(W26 0.281 초과).
**N144(중대·방법론):** lap448과 W26의 `(used,count)` 변화열이 **8/8 owner 모두 tick24,029까지 동일**
(tick 편차 ≤29 = 표집간격 ≈33tick 이내)이고 fixture도 전부 SAME(후보 `a10024de…`·원본 `b56986e0…`·
지도100×100·anchors 8종·시딩 16 op·시딩 후 상태) ⇒ **같은 결정적 궤적을 짧은 창으로 본 것**이라
N141을 독립 확증하지 않는다. 확증된 것은 **fixture 결정성**이며 재실행 무의미를 뜻한다.
**N145(중대·해석 정정):** 같은 궤적의 144k 연장에서 **8인 중 5인이 24k 창 이후 재개** — owner3
**33,753tick** 정지 후 재개·owner1 **36,236**·owner4 27,210·owner2 19,471·owner0 14,325. 전원동결 꼬리
7,739tick은 같은 run이 이미 재개해 보인 최대 간극 9,406tick보다 **짧고**, W26 종단 정지 40,484tick도
재개된 최대 36,236tick의 **1.12배**뿐 ⇒ **종단 정지와 더 긴 소강을 구분 불가.** ⇒ **N141을 '중대·확정'
에서 '해석 경고 + 미결'로 강등**(보수적 부분은 유지, 강등은 종국성에 한정). 상세는 lap 기록에.
**N146:** W26 144k 사망 9건/소실**14기**·생산116건/117기(`live` 1,166→1,269), 사망 9건 중 **7건이
tick24,029 이후**. lap448 24k는 사망 2건/**4기**로 **lap461 N87의 "4기/1,166기"와 정확 일치**(독립 재확인)
⇒ 엔진은 죽지 않았고 장부도 드물게 움직였으나 **전투 축 미성립은 수치로 재확인**.
**항2 rider:** lap448 `used+reserved>cap` owner-표본 **1,263건 전부 정확히 `(4995,10)`**,
owner4(619)·owner7(644) 둘뿐, episode 2건 **둘 다 Class A(차단·N68 동형, `count`154 불변, run 끝까지 열림)**,
**Class B(생산 계속) 0건** ⇒ **W26 owner2형은 144k 고유 분기**이며 차단이 아니라 **cap 도달 상태에서
생산이 계속 도는 별개 기전**(lap404 (가)/(나) 입력).
**무결성:** `used`음수0·int16이탈0·라이브 `used`>cap **0**·`count`>`count_cap`0·`live`==Σ`count` 712표본
불일치 **0** ⇒ F4 (C) 유지. **자체 결함 정정:** 초판 검사의 `sample` 1-기반 가정 off-by-one(판정 무영향).
**사후 대조:** lap448 `run_summary.json`·lap449 수치(1,263건/`(4995,10)`/owner4·7)와 **전부 일치**.
게임실행**0**·product source 변경**0**·커밋**0**·work 카드 발행**0**.

**2026-09-23 lap497~499 (계보 종결, lap501 압축 — 전문은 각 lap 기록과 precompaction 스냅샷에):**
lap497(work) W26 144k soak 완주 ⇒ `CAP_PROXIMITY_STABLE_144K`(부분 증거), U0~U3 PASS, U6 신규
자연발생 관측, U4 UNKNOWN, 게임실행1(72분51초) → lap498(middle) `run_summary.json`을 열지 않고
`samples.jsonl`(4,287행)만으로 재계산 ⇒ **측정 ACCEPT(불일치0)**, **W26 `CLOSED`**, U4=(a) 호스트
페이지 회수, **N141 제기**·N142·N143, 최종 tick144,023에 8/8 owner `used`∈[4995,5000] 72분51초 유지
(fault·cap초과·장부불일치 0) → lap499(strategy) **Q7-B 잠정 채택·Q7-C 기각·Q7-A 사용자 전결**,
fixture 축 G2 work 동결(예외 middle 1회차는 lap500이 소진). 전 회차 제품 source 변경0·커밋0.
전문 `docs/history/laps/20260923_lap49{7,8,9}_*.md`, 회부 `ESCALATE_SOL` §61·§62. lap356~496 계보는
precompaction 스냅샷 연쇄와 `docs/history/laps/`에.
## 바퀴 기록
lap501(middle, Opus5) AI 생산 정지 원인 정적 추적(2026-09-23 04:14 사용자 지시): 원본 SHA `b56986e0…`
직접 디스어셈블로 `FUN_00406770`→`FUN_00406B00`→`FUN_0043E7F0`/`FUN_00406C70` 경로 **바이트 확정**,
`analysis/`의 AI 생산 로직 문서 0건 공백을 메웠다. **8게이트 중 자원 게이트 0개** ⇒ N81의 자원 배제
재확인. 영구 정지 후보 **H-RATIO·H-TYPEMAX·H-CROWD**(구성 동결 시 고정, lap500 N146과 정합).
생산표 원본 직독 **143=생산65+연구78**·**건물27종, 건물당 kind {1:5,2:10,3:8,4:4}**. 표 읽기가
전부 런타임 전용이라 **원인 특정 `UNKNOWN`** — §7 읽기전용 probe를 다음 work로 인계.
게임실행0·source변경0·커밋0·카드발행0·598 passed·`SAFETY_PASS`·`CONTEXT_PASS`.
전문 `analysis/memory_maps/ai_production_decision_path_00406770_20260923.md` ·
`20260923_lap501_middle_ai_production_static_trace.md`, 회부 `ESCALATE_SOL` §64.
lap500(middle, Opus5) N141 재현성 + N142 rider: 사전 고정식 **`N141_REPRODUCED`**(24k 전원동결 32.21%)
이나 **N144로 독립 재현 부정**(두 run은 같은 결정적 궤적, `(used,count)` 8/8 동일), **N145로 N141 강등**
(5 owner가 24k 창 이후 재개, 최대 33,753tick 정지 후 재개 ⇒ 종단 여부 UNKNOWN), **N146**(144k 사망14기).
rider: **owner2형은 144k 고유 분기**, 24k는 Class A 2건뿐. 게임실행0·source변경0·커밋0·카드발행0.
전문 `20260923_lap500_middle_n141_reproducibility.md`, 회부 `ESCALATE_SOL` §63.
lap499(strategy, Fable5) Q7 처분: **Q7-B 잠정 채택**(3단 마일스톤 회부), **Q7-C 기각**,
**Q7-A=(ㄴ) 사용자 전결 유지+권고 첨부**. fixture 축 work 동결, 예외 middle 1회차 허용.
게임실행0·source변경0·커밋0. 전문 `20260923_lap499_strategy_q7_disposition.md`, 처분 `ESCALATE_SOL` §62.
lap498(middle, Opus5) W26 원시 독립검수: 측정 **ACCEPT**(불일치0) ⇒ **W26 `CLOSED`**. U0~U3 재현 PASS.
**N141 제기**·N142·N143, **U4 UNKNOWN → (a) 호스트 페이지 회수**. 후속 work 카드 미발행,
`ESCALATE_SOL` §61 **Q7**으로 회부. 전문 `20260923_lap498_middle_w26_independent_recheck.md`.
lap497(work, Sonnet5) W26 144k soak 완주: `CAP_PROXIMITY_STABLE_144K`(부분 증거), U0~U3 PASS,
U6 신규 자연발생 관측, U4 UNKNOWN. 게임실행1(72분51초)·source변경0·커밋0.
전문 `20260923_lap497_work_w26_144k_soak.md`.
lap356~496 계보(압축, 수치·판정 전문은 precompaction 스냅샷 연쇄와 각 원 lap 기록에 그대로):
lap496(middle) W28-R 독립검수 ACCEPT·라벨확정 ⇒ W28-R `CLOSED`·W26 발행(신규 N136~N140) →
lap495(work) W28-R §4 실행(610/610 완주, resume_delay 2tick) → lap494(middle) W28-R 발행 →
lap493(strategy) Q6-C 채택 → lap492(middle) W28 측정ACCEPT·라벨보류 → lap491(work) W28 §4 실행 →
lap356~490(W8~W27 soak/케이던스/판정기 수리/fixture축 소거, Step A~D rider 계보 포함).
전 회차 제품코드/커밋 전부0(lap491·lap495·lap497만 게임실행1, source변경0).
