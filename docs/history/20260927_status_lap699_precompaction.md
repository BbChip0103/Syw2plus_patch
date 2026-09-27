# STATUS — 매 바퀴 갱신하는 기억

이전(lap678~687) 상세 서술은 원문 SHA256 보존 후 압축했다:
`docs/history/20260926_status_lap688_precompaction.md`(원문 152줄, SHA256
`2b98e3b9e0b3757b7607efbf671a391fa89c504699e7d40cd33c5c52f6dab839`). 각 lap의 전체 근거는
`docs/history/laps/20260926_lap67{6,7,8,9}_*.md`·`lap68{0..8}_*.md`에 그대로 있다.

## 지금 상태

**G5는 2026-09-26 21:54 사용자 판단으로 단일플레이 milestone 승인, 최우선 지시 종료**(멀티 동기화는
`UNKNOWN` 메모 유지). 상세 근거는 `docs/history/laps/20260926_lap689_*.md`·`lap688_*.md`·`lap690_*.md`에
그대로 있다(2단 middle 조건부 PASS: 선택50·부대/호출/저장로드50·이동50·공격50 pending-word 근거·크래시0).

**lap691~694(work) G2 전비10000 준비(요약):** 전역 1200-슬롯 유닛 테이블 병목 확정(owner0~6 10000
도달, owner7만 6845에서 거부). 상세 `docs/history/laps/20260926_lap69{1,2,3,4}_work_*.md`.

**lap695(work) G2 8인×10000 PASS — 전역풀 4092로 확장:** 신규
`patches/population/g2_supply10000_pool4092_owner500.py`로 보호 원본(b56986e0) 위에 6-영역 tail
relocation(capacity=4093) + 전비10000 + 개인로스터500을 조합, **owner0~7 전원 `used=10000,
count=156, count_cap=500` 도달(PASS_ALL_EIGHT_SUPPLY10000)**, 크래시0. `make check` 1019
passed(769.54s). **알려진 한계(당시):** "detailed" 전역 유닛 열거가 0 반환. 상세
`docs/history/laps/20260927_lap695_work_g2_supply10000_pool4092_eight_owner_pass.md`.

**lap696(work) G2 저장→로드 1회 PASS:** native `op=2`/`op=3`로 저장→로드, **로드 후 owner0~7 전원
`used=10000, count=156, count_cap=500, cap=10000` 유지**. `make check` 1019 passed(828.01s).
전역 유닛 열거는 이번에도 0(도구 한계 지속). 상세
`docs/history/laps/20260927_lap696_work_g2_supply10000_saveload_pass.md`.

**lap697(work) G2 전역 유닛 열거 도구 수리 + raw 무결성 확인 PASS:** 근본원인 확정 —
`global_live_count`가 profile 인자 없이 호출돼 기본 STOCK_POOL(옛 주소)로 폴백해 항상 0이었다.
`g2_supply10000_pool4092_owner500` profile을 `POOL_PROFILE_LAYOUTS`에 등록하고 `active_slot_list`
(6번째 영역) 디코드를 추가. 8인×10000 fixture 재실행: **전역 live=1248(8×156)=owner합=
active_slot_list count, 중복0, existence bitmap 일치**, 저장→로드 후에도 동일 유지(`owners_ok_
after_load=8`). `make check` **1025 passed(755.05s)**, safety PASS, 신규 단위테스트6개 PASS.
**미확인 잔여:** category_slot_list_a/b(4·5번째 영역)는 범위 밖. 상세
`docs/history/laps/20260927_lap697_work_g2_pool4092_global_live_enumeration_pass.md`.

**lap698(middle, Opus 5.5) G2 독립 검수 — 2단 `CONDITIONAL PARTIAL PASS` / 제품 `HOLD`, 방향 승격:**
후보 독립 재빌드 `11aa9e79…` byte-identical, raw JSON(1248/중복0/로드 후 동일) 확인, targeted 22 passed,
SAFETY_PASS. 그러나 **fixture type103(cost65)은 게임에서 가장 비싼 단일 타입**(비용>0 83종 중앙값15,
<20이 59종)이고, 명령 wire가 슬롯을 하위 12비트로 압축해 풀 상한이 4095라 개인 cap을 올려도 1인 평균
~511기가 천장 → **평균 비용≥20 군대만 8×10000 가능**. 00:05 판정이 기각한 "고비용 우회"와 충돌해
`loop/ESCALATE_SOL`로 승격. 부가 결함: 전 구간 ~18 tick(안정성 미측정), 저장→즉시 로드(비판별),
bridge SHA 문서 불일치. 상세 `docs/history/laps/20260927_lap698_middle_g2_supply10000_independent_review_hold.md`.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 제품 미완료 | 1600×1200 원본 구도 외 사용자/제품 승인 |
| G2 | 전비5000 단계 달성. 8인×10000 **고비용(type103) fixture 한정** 회계·풀 무결성·저장/로드 raw PASS(lap695~697), middle 2단 조건부 부분 PASS(lap698) | **방향 판정(비용≥20 기준 수용 vs 12비트 wire 확장)**, 대표 혼합 구성, 판별형 저장/로드, tick 진행 안정성·전투/생산, 24k/144k, 멀티, 사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 제품 미완료 | AI 개선 제품 비교·post-load·사용자 승인 |
| G5 | **단일플레이 milestone 승인(2026-09-26 21:54 사용자)** | 멀티 동기화 `UNKNOWN`(별도 표시, 최우선 지시 종료) |

**lap699(work) A/B 판정 대기 중 비차단 하네스 확장 4건 완료(게임 EXE 무변경):**
① 중앙값-근접 혼합군(cost13/20) 1인·8인 실측 — `MEASURED_INDIVIDUAL_CAP_CEILING`, owner당
`count=492/500,used=7020/10000`(목표 대비 30% 부족), 엔진 Gate가 count_cap보다 항상 **-8**에서
거부(cap250 표본과 동일 오프셋, 신규 관찰). ② 판별형 저장/로드 PASS: 저장 후 owner0 `used`만
10000→1로 변조→로드→`restored_used=10000` 확인(no-op 로드가 아님을 최초로 판별). ③ 3000-tick
진행 후 전역 1248/중복0/bitmap 일치 유지 PASS(population 안정), 전투 시도는 `raw_return=0`으로
불발(type103/type5가 비전투형으로 추정, UNKNOWN 유지). ④ lap695/697 브리지 SHA "불일치"는
`bridge_sha256`이 서로 다른 두 대상(build_runtime_bridge.py 매니페스트=소스 해시, probe
provenance=컴파일된 DLL 해시)에 같은 이름으로 쓰인 명명 충돌임을 확인, 두 문서 정정. `make check`
1025 passed(761.95s), SAFETY_PASS. 상세
`docs/history/laps/20260927_lap699_work_g2_median_cost_ceiling_discriminative_saveload_tick_stability.md`.

## 지금 막힌 것 (Blockers)

**G2 방향 판정 대기(lap698 승격, `loop/ESCALATE_SOL`).** 명령 wire 슬롯 12비트(상한 4095) × 개인
cap 구조에서 8×10000은 평균 유닛 비용≥~20 군대만 가능하다(현 PASS는 최고가 type103 fixture). (A) 이
기준을 사용자에게 올려 현 후보로 안정성 단계를 진행할지, (B) wire 슬롯 확장(모든 생산자·소비자·저장·
멀티 호환)으로 풀 ≥8000~10000을 만들지 strategy/운영자가 정한다. safety/targeted 테스트는 PASS.

## 검증 상태

lap698(middle): 후보 재빌드 SHA 일치(`11aa9e79…`), lap697 JSON(SHA `95cb79cb…`) 직접 파싱 일치, targeted
pytest 22 passed(88.16s), `SAFETY_PASS`. 코드 무변경이라 전체 `make check` 미실행(lap697 1025 passed는 참조만).

lap697(work): `POOL_PROFILE_LAYOUTS`에 `g2_supply10000_pool4092_owner500` 등록 + `active_slot_list`
디코드 추가. 8인×10000 fixture 라이브: `final_global_live=1248`, `global_pool_integrity`
(owner_count_sum/active_slot_list_count/exists_bitmap_count 전부 1248, duplicate_count0,
matches_existence_bitmap true), 저장→로드 후 동일. `make check` **1025 passed(755.05s)**,
`checks/safety.sh check` `SAFETY_PASS`(`logs/gates/20260927_lap697_make_check.log`). 신규
단위테스트 `patches/population/test_runtime_driver_pool4092_global_live.py` 6 passed.

lap696(work): 기존 probe에 옵트인 `--save-load` 플래그 추가, native `op=2`(0x440c20)/`op=3`
(0x440ff0) 저장→로드 1회. 원본 SHA `b56986e0…c9c08a8ac` 실행 전후 불변. **로드 후 owner0~7 전원
`used=10000, count=156, count_cap=500, cap=10000` 유지**, cleanup ok. `make check` **1019
passed(828.01s)**, `checks/safety.sh check` `SAFETY_PASS`.

## 다음 한 가지
**2026-09-27 03:21 사용자 판단(AskUserQuestion 응답):** "현 한계 인정. 전비 상한 10000은 포기하고 기존 전비 상한 5000으로 만족". **G2 목표를 전비5000(달성 판단 유지)으로 되돌리고 10000 트랙 종료.** 10000 후보(lap691~699, `g2_supply10000_*`)와 증거는 보존만 하고 더 진행하지 않는다. A/B 판정 대기 해소. **다음 우선순위(운영자 결정): G4 — 길찾기/자유대전 AI**(STATUS 표: AI 개선 제품 비교·post-load·사용자 승인 미충족). 다음 work는 G4의 마지막 미충족 항목 중 post-load(저장/로드 후 AI 개선 유지) 확인부터 구현 우선으로 진행. G1은 그 다음.
**lap699 완료로 01:39 지시 ①~④ 전부 raw 증거 확보(위 "지금 상태" 참고).** A/B 판정은 여전히
strategy/사용자 전권 대기 — **G2 방향(A: 평균 비용≥20 기준 수용 / B: 12비트 wire 슬롯 확장)을
판정한다.** lap699이 A/B 판정에 새로 보탠 자료: 혼합군 1인 천장 실측(7020/10000, -30%), 엔진 Gate
"-8 고정 오프셋" 관찰(cap250/500 두 표본 일치, 근본원인 미상). 판정 대기 중 비차단 work 후보(선택):
(a) Gate -8 오프셋을 다른 cap 값으로 재현해 상수/비례 확정, (b) 확인된 전투형(G5 type2/type46)으로
fixture를 바꿔 tick-안정성 중 전투 포함 재확인(lap699 ③의 UNKNOWN 해소). 게임 EXE 변경은 A/B
판정 이후로 미룬다.

## 바퀴 기록

- lap699(work): A/B 판정 대기 중 비차단 하네스 확장 4건(혼합군 1인·8인 천장 실측, 판별형 저장/로드,
  3000-tick 무결성, 브리지 SHA 명명충돌 정정) 전부 완료, 게임 EXE 무변경. make check 1025 passed.
  상세 `docs/history/laps/20260927_lap699_work_g2_median_cost_ceiling_discriminative_saveload_tick_stability.md`.
- lap698(middle): G2 8인×10000 독립 검수 — 재빌드·raw·테스트 일치, 그러나 최고가 fixture 한정·12비트
  풀 천장으로 대표 구성 불가 → 조건부 부분 PASS/제품 HOLD, `loop/ESCALATE_SOL` 승격. 상세
  `docs/history/laps/20260927_lap698_middle_g2_supply10000_independent_review_hold.md`.
- lap697(work): G2 전역 유닛 열거 도구 근본원인 수리(profile 누락) + raw 무결성 확인 PASS
  (live=1248, 중복0, bitmap 일치, 저장/로드 전후 동일). make check 1025 passed. 상세
  `docs/history/laps/20260927_lap697_work_g2_pool4092_global_live_enumeration_pass.md`.
- lap696(work): G2 8인×10000 저장→로드 1회 PASS(native op2/op3, UI 좌표 미사용). make check
  1019 passed. 전역 유닛 열거 도구 한계는 lap697이 수리. 상세
  `docs/history/laps/20260927_lap696_work_g2_supply10000_saveload_pass.md`.
- lap695(work): G2 8인×10000 PASS(전역풀 1200→4092 확장, owner0~7 전원 used=10000). make check
  1019 passed. 상세
  `docs/history/laps/20260927_lap695_work_g2_supply10000_pool4092_eight_owner_pass.md`.
- lap691~694(work): G2 전비10000 패치 구현·owner1인 실측 PASS·경로전환·8인 전역풀1200 병목 확정.
  상세 `docs/history/laps/20260926_lap69{1,2,3,4}_work_*.md`.
- lap690(work): G5 probe 주석 1건 정정, 코드 변경 없음. 상세
  `docs/history/laps/20260926_lap690_work_g5_probe_comment_correction.md`.
- lap689(middle): G5 전체 독립 재검수 단일플레이 조건부 PASS(사용자 21:54 최종 승인). 상세
  `docs/history/laps/20260926_lap689_middle_g5_full_independent_review_conditional_pass.md`.
- lap682~688(G5): self-calibration MOVE 수렴 PASS(682) → v3 HOLD(683) → roundtrip PASS·공격판정
  결함 발견(684) → 재배치 회귀 반증(685) → bisection 비결정성 확정(686/687) → 공격 스폰-타이밍
  레이스 확정·N=5 측정(688). 각 상세는 `docs/history/laps/20260926_lap68{2..8}_*.md`.
- lap681 이전 요약은 `docs/history/laps/`에 원문 보존(포인터:
  `20260926_lap676_work_g5_command_packer_xref_falsified.md` 및 각 lap 파일).

G5의 선택/호출/이동/save-load 부분 runtime 증거와 과거 실패 provenance는 `docs/history/laps/` 및
공유 `temp/Syw2plus_patch/`에 보존한다. G5는 사용자 milestone 승인 완료, 멀티 동기화만 `UNKNOWN`이다.
