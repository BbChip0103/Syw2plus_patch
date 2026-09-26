# 2026-09-23 | lap 525 | 목표 G2 (S0 독립 검수, middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, middle(중간계획·컨펌). 보조 읽기 전용 탐색 1건은
  native subagent(`explore`, sonnet)가 참고 저장소 decomp에서 했다. 판정에 쓴 핵심 사실은 모두 원본 바이트로 다시 확인했다.
- 가설 / 사용자 관찰: lap524 W35(S0) `FEASIBLE`(미검수)이 원시 산출물만으로 재현되는가. 거부 7쌍의 원인이라는 `+0x1D8 bit0x4`는 무엇인가.
- 예상 PASS / FAIL 조건: 카드 `G2_S0_ORIGINAL_ORDER_ENGAGEMENT_FEASIBILITY_LAP523.md` §3·§5. `run_summary.verdict`를 보지 않고
  `op8_results.json`·`observation_samples.jsonl`로 F1~F4를 재계산한다. 라벨이 일치하면 `CLOSED`, 불일치하면 반려한다.
- 변경 파일 / source fingerprint / 커밋: 제품 source·브리지·테스트 변경 0. 문서만 바꿨다. 신규
  `analysis/memory_maps/g2_unit_attack_domain_flags_1d8_lap525.md`·이 기록, 카드 §7 추가, STATUS·INBOX·`loop/ESCALATE_SOL` §82. 커밋 0.
- 원본 SHA / 후보 SHA / 환경: 원본 `b56986e0…c9c08a8ac` 재확인(불변). 후보 `a10024de…`는 재빌드하지 않았다(실행 없음).
  lap524 산출물 SHA256은 기록과 전부 일치했다(`op8_results.json` `d496355d…`, `run_summary.json` `dfe731d1…`, `selected_pairs.json` `c8aefc57…`,
  `verdict_corrected.json` `a7e5f879…`). `observation_samples.jsonl` `1e3fbd5b…`, `baseline_samples.jsonl` `36aff09a…`.
- 실행 명령: 게임 실행 0. `python3`로 원시 JSON/JSONL을 재계산했다. `objdump -Mintel -d -b pei-i386`로 원본 `.text`를 읽었다.
- 측정값 / 판정:
  - **F1 (재계산):** `op8.raw_return`==1은 owner0(src 2821→tgt 3439)뿐이다. 브리지 동기 필드 `src_0x384_before/after`=`0x10001→0x10004`로 변화가 있다.
    `src_cmd_left_tick`=1067(호출 tick 1066 + 1)이다. 나머지 7쌍은 `raw_return`=0이고 `+0x384`=1→1로 변화가 없다.
    **동기 필드를 쓰는 것은 사후 재채점이 아니다.** 카드 §1이 결과 JSON에 `+0x384` 전/후를 요구했고, 이 값이 호출을 감싸 직접 잰 측정이다.
    하네스의 별도 폴링(`pending_0x384_after`=`0x10001`)은 호출 뒤 다른 시점에 읽은 값이다.
  - **F2 (재계산):** owner0 소스 좌표 집합은 {(97,9),(94,6)}로 2개이다. 최소 Chebyshev는 1이다. **주의:** 좌표 변화는 목표 사망(tick 2461) 뒤 tick 2528의 이동이다.
    선택 시점부터 인접(거리 1)이라 "접근"은 필요 없었다. 카드 문구("좌표 2개 이상")는 충족하지만 **원거리 접근은 입증되지 않았다.**
  - **F3 (재계산):** 목표 HP는 O 시작 597에서 표본 단위로 감소해 4가 됐고, tick 2461에 소멸했다(작은 회복 진동 포함).
    기준창 B0=0·D_B=0(`baseline_samples.jsonl` 31줄 전부 0)이다. 소스 명령이 tick 1067에 1→4로 바뀌었다. 따라서 op8 귀속은 타당하다.
  - **F4:** tick 역행 0(재계산)이다. 결함 로그 0(orchestrator 48줄에 fault/crash/exception/error 없음). `live`==Σ`count`·`used`≤5000·int16은 **원시 표본에 저장되지 않았다.**
    그래서 하네스 코드(`w35_run.py:650-666`, 매 표본 검사)와 집계값으로만 확인했다. **카드의 "음수 0" 절은 하네스가 검사하지 않는다**(`used<-32768`만 봄). → S1 카드 요구사항으로 넘긴다.
  - **NF-a 배제 확인:** 8쌍 모두에서 `players[].b5`={0..7}로 서로 다르다.
  - **판정: 카드 §3 식 그대로 `FEASIBLE`이며 lap524 `verdict_corrected.json`과 일치한다 ⇒ W35 `CLOSED`.** `run_summary.verdict`(`NOT_FEASIBLE`)는 폴링 결함 산출이라 무효다.
  - **거부 원인 해석은 반려(정정)한다 — N181~N183**(`analysis/memory_maps/g2_unit_attack_domain_flags_1d8_lap525.md`).
    `+0x1D8`은 유닛 초기화 `0x411D2F`에서 타입 행 `+0x4C`를 복사한 **타입 고정값**이다. 원본 `.text`의 writer는 5개뿐이다.
    bit 0x4를 런타임에 바꾸는 곳은 타입 33·39 전용이다. type 5 = `0x4028401`(bit 0x4=0)이고, fixture 전 타입의 `+0x1BC`는 1이다.
    ⇒ **허용목록 {5,7,46} 시딩 유닛은 구조적으로 누구도 공격하지 못한다.** 자동공격도 같은 `FUN_00415880` 게이트를 쓴다.
    S0에서 수락된 소스는 **비시딩 type 110**(owner당 2기)이었다. 피격된 type 5는 반격하지 않았다.
- 회귀 / 남은 위험 / 검수 상태:
  - **strategy 전제와 실제 증거가 충돌한다 → S1 카드를 발행하지 않았다(PROMPT ④-3 예외 "서로 충돌하는 실제 증거").**
    strategy §4는 "FEASIBLE이면 곧바로 S1(A1~A8)"이라고 한다. 하지만 A8(허용목록 {5,7,46} 안에서만)과 §5(허용목록 확장 금지)를 지키면 공격 가능한 유닛은 owner당 type110 2기뿐이다.
    이 상태로는 A2(owner마다 전투 사망≥20)가 한쪽만 때리는 사냥이 되거나, `NO_ENGAGEMENT`로 미리 정해진다. §2 "무교전 원인=order 발부 공백"도 구성 원인을 빠뜨렸다.
    A8·§5 변경은 기준 완화이므로 middle 권한 밖이다 → `loop/ESCALATE_SOL` §82로 strategy에 회부한다.
  - W26 144k `CAP_PROXIMITY_STABLE_144K`는 **교전 불능 구성**의 정지 생존이었다는 점도 제출문에 적어야 한다(N141 정지 생존 해석 강화).
  - `make check`는 source 변경이 없어 생략했다(N22·lap523 선례). 문서 무결성 검사만 돌렸다(아래 STATUS 검증 줄).
- 다음 한 가지: **strategy(Opus5.5): S1 fixture 구성 판정(§82).** 선택지는 (가) 허용목록 유지 + type110 공격자 편측 S1,
  (나) bit0x4 전투 타입 1종을 허용목록에 추가(핀 변경, 사전 읽기 전용 비용/크기/`+0x24`가드 확인), (다) S1 보류 후 W26+S0로 Q7-B 제출이다.
  middle 권고는 (나)다. 판정 뒤 middle이 S1 카드를 발행하고 work가 실행한다.
