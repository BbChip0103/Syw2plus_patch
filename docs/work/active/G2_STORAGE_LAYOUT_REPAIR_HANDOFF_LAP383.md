# HANDOFF lap383 middle(Opus5/high) → work tier(Sonnet5/high) — lap382 layout 모듈 scoped 수리

발행: 2026-09-18 KST. 발행자 역할: 중간 tier 진단/검수/확인. **구현은 하지 않았다.**
대상: `patches/population/base_preserving_storage_layout_v1.py`
(현행 SHA256 `278a00135f9a0b9e7dc2774d9fb0a4d0b16033ca96f678ea84fed32af6ba3a65`)
및 `patches/population/test_base_preserving_storage_layout_v1.py`
(현행 SHA256 `7d0cfb40677985568f27799155bfb6c66b6dc1cb4154ade375cacf89f03a365f`).

`patches/population/offline_storage_v1.py`는 **frozen — 계속 수정 금지**
(`e9d84513f6a53e27135a7e19a546a8a72165804d1041f9a23719fc7cb249f8cc`, 이번 lap에서 무변경 확인).

## 판정 — REJECT (scoped 수리 1회, 재조사 아님)

lap382의 **핵심 기하는 독립 재유도로 옳다**(아래 §"독립 확인된 것"). 되돌릴 이유는 없다.
그러나 계획 `G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md` §3 공개계약 **2·3번**,
필수 회귀 "모든 새 VA < 2^32", lap381 정정의 **필수 산출물**이 각각 실측으로 깨졌다.
전부 **국소 수정**이며 새 조사·새 주소 추론·새 카드가 필요 없다.

근거 probe(읽기전용, 이번 lap 실행): `docs/history/laps/probes/20260918_lap383_middle_g2_layout_independent_review_probe.py`
→ `failures=['foreign_delta_field_equals_true_address_shift',
'va_guard_rejects_first_N_whose_new_end_reaches_2**32',
'shrink_discarded_slot_is_not_silently_mapped_outside_its_region',
'shrink_layout_is_rejected_outright',
'launcher_rejection_test_actually_invokes_a_launcher_entrypoint',
'private_pelayout_artifact_preserved_under_designated_temp']`.

## 수리 항목 (우선순위 순, 이 6개만. 범위 확대 금지)

### R1 — 조용한 오사상 (가장 심각, 계약 §3-3 위반)

`layout(n)`이 `n >= 1`이면 무엇이든 받는다. `n < 1200`이면 `running_delta`가 음수가 되고,
폐기된 slot 주소가 **자기 영역 밖으로 조용히 사상된다.**

실측(N=100): `map_va(0x0066B790 + 0x758*1199, 100)` → `kind="region"`,
`new_va=0x891CB8`. 그런데 `unit_pool` 새 범위는 `[0x66B790, 0x6995F0)`이고
`0x891CB8`은 **`gap_after_active_slot_list` 외래 블록 내부**다. 즉 "사상 불가를 0이나
항등으로 조용히 흘리지 않는다"는 계약이 축소 방향에서 무효다.

수리(권장, 최소): `layout()`이 `n < STOCK_CAPACITY`를 `ValueError`로 **거부**한다.
이 모듈은 Astra 범위상 확장 mapper다. (대안으로 `map_va`가 `local >= array_new_span`인
배열부 주소를 `"unmappable"`로 반환하게 해도 되지만, 두 가지를 동시에 하지는 말 것.)
회귀: `layout(1199)` 거부, 그리고 위 실측 주소가 더 이상 `"region"`으로 오지 않음.

### R2 — `ForeignLayout.delta` 가 lap381 정정을 거스른다 (계약 §3-2 위반)

계획 §3 계약 2번: "각 블록의 delta는 **자신보다 낮은 주소의 누적 삽입량**이다."
실측(N=4001): `delta` 필드는 gap 4개 전부 **0**인데 실제 이동량은
`gap_after_unit_pool=5,265,880` / `gap_after_unit_age=5,277,084` /
`gap_after_category_slot_list_b=5,299,492` / `gap_after_active_slot_list=5,305,094`다.
`rsrc`만 `delta`에 주소 이동량(5,308,416)을 담는다. 즉 **같은 필드가 세 가지 의미**
(RegionLayout=span 증가, gap=0, rsrc=주소 이동)로 쓰인다.

지금 당장 수치가 틀리는 곳은 없다 — `new_start`는 `running_delta`로 옳게 계산되고
`build_layout_artifact`는 `.delta`를 쓰지 않고 `new_start-old_start`를 다시 구한다.
문제는 **공개 계약이 lap381이 명시적으로 정정한 바로 그 오류를 필드값으로 재현**한다는
것이고, 다음 소비자(code-fixup 카드)가 `foreign.delta`를 읽으면 0을 얻는다.

수리: 모든 `ForeignLayout.delta = new_start - old_start`. 크기 불변은 별도 이름
(예: `size_invariant: bool` 또는 span 비교)으로 표현한다. `RegionLayout.delta`가
span 증가라는 점은 이름이나 docstring으로 **명시**한다.
회귀: `test_expansion_foreign_blocks_shift_by_cumulative_insertion_below_not_delta_zero`가
`new_start-old_start`가 아니라 **`.delta` 자체**를 단언하도록 고친다(현재 이름은 정정을
지킨다고 주장하면서 정작 그 필드를 보지 않는다).

### R3 — 32비트 VA 가드가 `IMAGE_BASE`만큼 느슨하다

`layout()`의 `rsrc.new_end >= IMAGE_BASE + 2**32`는 VA 상한이 아니다. VA는 `2**32` 미만
이어야 한다. 실측: 이분 탐색으로 찾은 **N=2,259,703**에서 `rsrc.new_end=0x1000000F0`
(> `2**32`)인데 `layout()`이 **그대로 수락**한다. `size_of_image`는 RVA 기반이라 걸리지 않는다.
공학 범위(≤9904)에서는 도달하지 않지만 계획의 필수 회귀 "모든 새 VA와 SizeOfImage < 2^32"는
문자 그대로 깨져 있다.

수리: 조건을 `rsrc.new_end >= 2**32`로 바꾼다.
회귀: `test_layout_rejects_32bit_overflow`의 `2**31`은 너무 커서 경계를 시험하지 못한다.
**N=2,259,703에서 raise, N=2,259,702에서는 통과**를 단언하는 경계 회귀를 추가한다.

### R4 — 필수 산출물 미완료 (lap381 정정: private `.pelayout`은 필수)

`temp/Syw2plus_patch/` 전체에 `.pelayout` 파일이 **0개**다. `write_layout_artifact`는 pytest
`tmp_path`에서만 호출돼 테스트 종료와 함께 사라진다. 결정적 mapping 산출물도 없다.

수리: 지정 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/
20260918_lap383_layout_artifact/` 아래에
(a) 공학값 N 하나 이상의 `.pelayout` 실제 파일, (b) `layout(n)`/`map_va` 결과의 결정적
mapping 덤프(JSON)를 **실제로 남기고**, lap 기록에 **경로와 SHA256**을 적는다.
메인 레포에 두지 않는다. 실행/배포하지 않는다(AGENTS.md).

### R5 — launcher 거부 증거가 launcher를 부르지 않는다

`test_expanded_artifact_sha_would_be_rejected_by_the_repo_launcher_pin`은 AST 기준 호출이
`build_layout_artifact`/`sha256`/`hexdigest`뿐이다. `check_runtime`/`prepare`/`Popen` 호출 **0건**.
즉 상수 비교이지 "프로세스 시작 전 거부" 관측이 아니다.
(주의: 이 테스트의 **docstring이** `subprocess.Popen`을 서술해서 단순 grep 검수는 **거짓 PASS**를
낸다. 이번 lap이 실제로 한 번 걸렸다가 AST 파싱으로 정정했다.)

수리(둘 중 하나만, 확대 금지):
(a) 지정 temp 사본에 대해 `tools/runtime_env.py`의 실제 진입점을 호출해 `RuntimeSafetyError`
   계열 거부를 관측하고 **Popen이 0회**임을 보인다(게임 실행 아님, 거부 경로만).
(b) (a)가 안전하게 불가능하면 테스트 이름과 docstring에서 launcher 주장 자체를 내리고
   "pin 동일성 + 확장 artifact digest 불일치"라는 **실제로 증명한 것만** 남긴다.

### R6 — ±1 항등 앵커의 blanket skip (경미)

`test_n1200_map_va_is_identity_at_every_boundary_and_its_neighbors`는 `unmappable`이면
무조건 `continue`한다. 실측상 36개 probe 중 **정확히 1개**(`unit_pool` base−1 =
`0x0066B78F`, 최하위 영역 아래라 정당)만 unmappable이다. 즉 **지금은 결함이 아니다.**
다만 blanket skip이라 향후 변경이 다수 probe를 unmappable로 만들어도 조용히 통과한다.

수리: 허용되는 unmappable probe를 그 한 주소로 **명시 고정**하고 나머지는 항등을 단언한다.

## 독립 확인된 것 (재조사 금지 — 이번 lap이 바이트로 재유도했다)

1. 원본 `b56986e0…c9c08a8ac` 불변, 빌드 전/후 동일. 모듈/테스트 SHA는 lap382 기록과 일치.
2. `build_layout_artifact(원본, 1200)` **바이트 완전 동일** — 항등 앵커의 artifact 절반 성립.
3. `.rsrc` 리소스 디렉터리를 **직접 트리 walk**해 leaf 9개를 재유도했고, 그 로컬 오프셋이
   모듈의 `PAYLOAD_ENTRY_OFFSETS`와 **정확히 일치**한다(모듈 상수를 쓰지 않은 독립 유도).
   각 leaf의 `OffsetToData`가 stock에서 `.rsrc` 범위 안임도 확인.
4. N=4001/9601/9904 artifact의 변경 바이트 집합이 **독립 유도한** 허용 필드 범위의
   부분집합(차집합 0). `.data` VirtualSize가 확장된 tail을 **여전히 덮고**, 새 `.rsrc` RVA와
   겹치지 않으며, `SizeOfImage`가 `.rsrc` 끝을 덮는다(3개 N 전부 PASS).
   stock `.data` 끝과 `.rsrc` 사이 slack은 `0x5C8`로 실측됐다(의미는 여전히 UNKNOWN).
5. lap380 tail probe `failures=[]`, lap381 C1/H1 probe `failures=[]` 재실행 rc0.
6. targeted 45 passed / `patches/population/` 90 passed, `checks/safety.sh check` `SAFETY_PASS`.

## 계획 §3-5 미이행 (수리 아님 — 다음 중간/Astra가 지정하거나 명시적으로 descope)

계약 5번은 "bulk-relative span·count/endpoint alias·**PlayerStruct span**을 기준점 상대값으로
유도"를 요구한다. count/endpoint alias는 `count_bytes`로 접혀 있어 충족한다. 그러나 모듈은
`0x892410` 3중 alias(unit_pool 끝 = bulk save 시작 = live state base)도 PlayerStruct span도
**전혀 언급/노출하지 않는다**(문자열/공개 심볼 0건). 이 카드에 넣을지 다음 카드로 뺄지는
work tier가 임의로 정하지 말고 **계획 문서에 명시**한다.

## 범위 밖 (STOP, 그대로 유지)

게임 실행, code operand fixup, 후보 EXE 생성/배포, `offline_storage_v1` 변경, frozen pin 갱신,
커밋/push, 새 의존성, slot>=1200 lifecycle/save smoke, LAN, 주소 추론 generator,
전면 linear fixup generator. 기존 STOP 카드 재시도 금지.
`4001/9601/9904`는 공학 테스트 값이며 최종 용량이 아니다.

## 이 수리가 끝나도 남는 것

lap379 Sol의 **integration / automatic broad patcher / runtime NO-GO는 유효**하다.
**G2는 여전히 미완료**이고 tail 참조 이전 부채(17,584 linear 후보)도 그대로다.
이 카드 ACCEPT는 제품 승인도 런타임 승인도 아니다.
