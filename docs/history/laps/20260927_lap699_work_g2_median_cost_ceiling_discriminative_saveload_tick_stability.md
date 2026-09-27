# 2026-09-27 | lap 699 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5(claude-sonnet-5), 실무(work) 역할.
- 가설 / 사용자 관찰: STATUS/APPROVALS 2026-09-27 01:39 운영자 지시(lap698 수용, A/B 판정 대기 중
  EXE 무변경 하네스 확장): ① 비용 섞인 현실적 군대(중앙값 비용 근처 구성)로 1인·8인 상한 실측, ②
  저장 후 상태 변경→로드→복원 확인, ③ 수천 tick 진행 후 전역 1248기·중복0 재확인(가능하면 전투
  포함), ④ lap695/697 브리지 SHA 기록 불일치 정정. A(비용≥20 기준 수용)/B(wire 슬롯 확장) 판정
  자체는 사용자 전권이라 이번 lap은 손대지 않는다.
- 예상 PASS / FAIL 조건: ①은 raw 실행으로 실제 `used` 천장을 측정하면 목적 달성(PASS/FAIL 판정
  대상이 아니라 측정값 자체가 산출물). ②는 저장 시점 값과 다르게 변조한 뒤 로드가 변조를 무시하고
  저장 시점 값을 복원해야 판별 성공. ③은 3000 tick 경과 후에도 `duplicate_count==0`·
  `owner_count_sum==active_slot_list_count==exists_bitmap_count`가 유지돼야 PASS. ④는 두 문서의
  구체적 수치를 실제 보존 아티팩트와 대조해 맞는 설명으로 고치면 완료.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(LOOP_ALLOW_COMMITS=0).
  - `tools/g2_supply10000_pool4092_eight_owner_probe.py` (SHA256
    `3661d154881dd7581df9b0b8b86fc28096d500d9959093e0960480c4a5ea5063`): `FIXTURE_PLAN`을
    `HIGH_COST_FIXTURE_PLAN`(기존 type103x153+type5x1)으로 이름만 바꾸고 `MIXED_FIXTURE_PLAN`
    (type2/cost13 x400 + type46/cost20 x400, 둘 다 `runtime_bridge.c` op5/6 allow-list의
    게이트-합법 타입)을 추가, `--fixture {high_cost,mixed}`/`--owners N`/
    `--discriminative-save-load`/`--run-ticks N` CLI를 추가했다. 기존 인자 없는 호출(`--fixture`
    미지정, `--owners` 미지정)은 이전과 완전히 동일한 `high_cost`/`owners=8` 경로를 타므로 lap691~698
    결과와의 비교 가능성은 유지된다. 두 곳에 서로 다른 원인의 request-id 충돌 버그를 발견·수정했다
    (아래 측정값 참고) — `_g2_lifecycle_native_op`(op2/3)는 시각 기반 큰 id를, `SupplyProbe.call`
    (op4/5/8)은 프로세스 내 작은 순차 id를 쓰는데 브리지가 `request[0] <= last_id`인 요청을 조용히
    버리므로, 네이티브 op 다음에 `supply.call`을 쓰려면 `supply.next_id`를 그 네이티브 id + 1로
    강제 전진시켜야 한다(저장 직후, 로드 직후 두 지점 모두).
  - `docs/history/laps/20260927_lap695_work_g2_supply10000_pool4092_eight_owner_pass.md`,
    `docs/history/laps/20260927_lap697_work_g2_pool4092_global_live_enumeration_pass.md`: lap698
    결함4(브리지 SHA 불일치) 재조사 결과로 정정. 실제 근본 원인은 "라운드마다 브리지가 바뀐다"가
    아니라, 코드베이스에 `bridge_sha256`이라는 같은 이름이 서로 다른 두 대상(①
    `build_runtime_bridge.py`의 `supply_bridge_build.json`이 적는 **`runtime_bridge.c` 소스 해시**,
    ② 이 probe들의 `provenance.bridge_sha256` = **컴파일된 `_inmm.dll` 바이너리 해시**, gcc/ld가
    PE에 남기는 빌드시점 비결정적 바이트 때문에 소스 불변이어도 매 빌드 달라짐)에 쓰이는 명명
    충돌이었다. 이 lap이 lap695/696/697/699 네 lap의 보존 아티팩트(`eight_owner_bridge/
    runtime_bridge.c`와 `_inmm.dll` 원본 파일 자체)를 직접 재해시해 확인: `.c` 해시는 네 lap 전부
    `28980e42274f15eb56a81a5b201b0e66ca9dad2688d706d59610ee8fcbcca440`로 동일(문서 원문이 맞았다),
    `.dll` 해시는 네 lap 전부 다르다(lap695 `51168d40…`/696 `bb3ae221…`/697 `42d2eda1…`/699
    `0d848884…`, 컴파일러 비결정성). 문서를 이 구분을 명시하도록 고쳤다(수치 자체를 삭제하지 않고
    올바른 대상으로 재귀속).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`, 세 실행 전후 모두 불변, `source_unchanged: true`).
  high_cost 실행의 후보는 lap695/696/697과 byte-identical
  (`candidate_sha256 11aa9e796805d3e0c29b55de957d003c521e74f9aeddf4e3478bd743842e5b53`) — 이번
  lap은 후보 코드를 전혀 건드리지 않았다(probe/하네스만 확장). mixed 실행도 같은
  `g2_supply10000_pool4092_owner500.create_copy` 후보(동일 SHA)를 재사용했다. 활성 8인
  (`_custom_game_chain_inject_g2_eight_seed42`), 지도 100x100.
  - mixed fixture: type2(cost13) 400 + type46(cost20) 400 wanted/owner(의도적으로 count_cap을
    넘는 큰 wanted — Gate가 실제로 거부하는 지점을 raw로 재게 하기 위함).
  - high_cost fixture: type103(cost65) x153 + type5(cost35) x1, lap692/694~698과 완전히 동일.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `PYTHONPATH=. .venv/bin/python tools/g2_supply10000_pool4092_eight_owner_probe.py
     --runtime-root local/runtime/lap699_mixed_owner1 --artifact-root
     .../20260927_lap699_mixed_owner1 --fixture mixed --owners 1` → exit0, SHA256
     `6b5d43ae1a28e04e5e966a0118ef433624fa26a9572f5bd3c814489073536f8d`.
  2. `... --fixture mixed --owners 8 --runtime-root local/runtime/lap699_mixed_owner8
     --artifact-root .../20260927_lap699_mixed_owner8` → exit0, SHA256
     `61fe4a2e561ee3fe2ee58ed721b7a5b5324cb33353ba60c01b6a1c39534b305f`.
  3. `... --fixture high_cost --owners 8 --save-load --discriminative-save-load --run-ticks 3000
     --runtime-root local/runtime/lap699_highcost_saveload_ticks --artifact-root
     .../20260927_lap699_highcost_saveload_ticks` → 최초 2회는 위 request-id 버그로
     `ProbeError`(exit2, id=17 그리고 id=1228954401 타임아웃)로 실패, 수정 후 3번째 실행 exit0,
     SHA256 `27fd39f70e922749a914623c1eb43069fdd7867a5e74f91ac2da2a14c45d30a2`(01:57~02:03 KST, 약
     185초). 실패한 두 시도의 stdout/stderr는 `/tmp/lap699_highcost.{stdout.json,stderr.log}`에
     남겼으나 재실행으로 덮였다(재현 가능, 코드에 원인 주석으로 남김).
     `checks/safety.sh check` → `SAFETY_PASS`. `make check` → **1025 passed(761.95s)**,
     로그 `logs/gates/20260927_lap699_make_check.log`, ruff/mypy/compileall/`CONTEXT_PASS` 전부
     PASS.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **① 중앙값-근접 혼합군 상한 실측 — MEASURED_INDIVIDUAL_CAP_CEILING.** 1인(owner0 단독):
    wanted 800(400+400) 중 490만 배치 성공(`fixture_original_gate_rejected`), `count=492`
    (count_cap=500), **`used=7020`**(목표10000 대비 **30% 부족**). 8인 동시: owner0~5는 1인
    결과와 완전히 동일(각 `count=492,used=7020`) — Gate가 owner별 독립임을 실측 확인. owner6/7은
    `fixture_placement_budget_exhausted`로 각각 420/192만 배치됐는데, 이는 **probe 자체의 한계**다
    (지도 100x100=10000칸을 순차 스캔하는 배치 알고리즘이 owner0~5가 이미 채운 근처 칸들 때문에
    owner6/7 차례에 빈 칸을 못 찾은 것 — 원본 엔진 Gate 한계가 아니라 이 probe의 배치 스캔 아티팩트,
    owner0~5의 결과가 신뢰 가능한 측정값이다). **부가 발견(신규):** 엔진 Gate가 패치된 count_cap
    (500)보다 8기 낮은 count=492에서 거부한다 — lap692가 stock cap250에서 목격한 "실제 거부는
    ~242(250-8)"과 **정확히 같은 -8 오프셋**이다. 이전엔 "원인 미상"으로 남았던 것이 이번 lap으로
    **cap 크기와 무관한 고정 오프셋**이라는 재현 가능한 패턴으로 좁혀졌다(근본 원인은 미조사, 다음
    work 후보).
  - **② 판별형 저장/로드 — PASS(discriminative).** 저장 직후 owner0의 `used`만(unit 레코드는
    불변) op=4로 `10000→1`로 변조, 변조 확인(`mutated_used=1`) 후 op=3 로드 → **`restored_used=
    10000`, `restore_confirmed=true`**(저장 시점 값으로 정확히 복원, 변조값이 아님) — lap698 결함3
    ("no-op 로드와 구별 불가")을 해소하는 최초의 판별 증거. 나머지 owner1~7도 `owners_ok_after_
    load=8/8`, `loaded_global_pool_integrity`(1248/1248/1248, 중복0, bitmap 일치, `active_slots_
    unchanged_by_load=true`) 전부 PASS.
  - **③ 3000-tick 진행 후 무결성 — PASS(안정, 전투는 UNKNOWN).** `pre_run_tick=20 → post_run_tick=
    3021`(3001 tick 경과, 목표 달성). `population_unchanged=true`(1248 그대로), `duplicate_count=0`,
    `matches_existence_bitmap=true`, owner합=active_slot_list=existence bitmap 전부 1248로 일치.
    전투 시도(owner0 type103 유닛 → owner1 type5 유닛, op8): `raw_return=0`(엔진이 거부, 공격
    명령이 실제로 발효되지 않음 — `src_0x384_before==after==1`, 상태 불변). type103/type5는 G5
    조사에서 이미 확인된 "공격 가능 플래그가 있는 전투형"이 아닐 가능성이 높다(worker/생산 유닛
    계열) — "가능하면 전투 포함"은 이번 fixture로는 달성 못 했고, 정직하게 UNKNOWN으로 남긴다.
    population 무결성 자체는 전투 유무와 무관하게 3000 tick 동안 안정적임이 확인됐다.
  - **④ 브리지 SHA 문서 정정 — 완료.** 위 "변경 파일" 절 참고. lap695/697 원문의 `28980e42…`는
    올바른 값(소스 해시, 안정적)이었고, lap698이 발견한 "불일치"는 probe의 `provenance.
    bridge_sha256`(컴파일된 DLL 해시, 비결정적)과의 명명 충돌이 원인이었다. 두 문서를 이 구분이
    드러나도록 고쳤다.
  - `make check` 1025 passed(761.95s), `checks/safety.sh check` SAFETY_PASS, 후보/원본 SHA 3회
    실행 모두 불변, cleanup 전부 ok(3회 모두 `prefix_processes_after: []`), 실패했던 2회 시도도
    프로세스/Wine 잔여물을 남기지 않도록 수동 `wineserver -k/-w`로 즉시 정리했다(중간 결과 참고).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 게임 EXE/후보 패치는 이번 lap에서 전혀 안
  건드렸다(probe/하네스 코드와 두 문서만 변경) — G2 8인×10000 후보 자체의 middle `CONDITIONAL
  PARTIAL PASS`/제품 `HOLD` 판정(lap698)은 그대로 유효하며 이번 lap이 바꾸지 않는다. A/B 방향
  판정은 여전히 사용자 전권으로 대기 중이다. 새로 열린 질문: 엔진 Gate의 "-8 고정 오프셋"(count_cap
  대비 항상 8 낮은 지점에서 거부)의 근본 원인 — cap500/250 두 표본만으로는 상수인지 다른 비례식인지
  확정 불가.
- 다음 한 가지: A/B 판정은 여전히 strategy/사용자 대기. 판정 대기 중 비차단 work가 남아 있다면: (a)
  엔진 Gate "-8 오프셋"을 cap 값을 다르게(예: 100, 1000) 바꿔 재현해 상수/비례 여부를 확정하는 저비용
  probe, (b) 이번에 발견한 "혼합군은 count_cap에 먼저 막혀 7020/10000"이라는 raw 수치를 A/B 판정
  자료로 STATUS/ESCALATE_SOL에 반영, (c) type103/type5가 아닌 확인된 전투형 유닛(G5 type2/type46)
  으로 fixture를 구성해 전투 포함 tick-안정성 재확인(③의 UNKNOWN 해소). EXE 변경은 여전히 A/B
  판정 이후로 미룬다.
