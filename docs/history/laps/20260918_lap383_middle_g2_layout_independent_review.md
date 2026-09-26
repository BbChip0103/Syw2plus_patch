# 2026-09-18 | lap 383 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, 중간(middle) 역할 —
  진단·계획·확인. **게임 코드 hands-on 수정 0건.** `docs/MODEL_ROUTING.md` 2026-09-18 오버라이드.
  lap 번호는 `loop/.lap_counter`=**383**(러너 전용 상태, 읽기만 함)을 따른다. 런타임 주입
  헤더는 `lap=382`였으나 PROMPT 서두가 파일 값을 이번 runtime lap 번호로 규정한다.
- 가설 / 사용자 관찰: STATUS "다음 한 가지" — lap382 Sonnet5 산출물(신규 모듈 + 45 tests)을
  **같은 작성자의 산술·해시 자기증명이 아닌** 독립 PE/header/resource walk로 검수하고,
  필요하면 한 번의 scoped Sonnet 수정범위를 넘긴다.
- 예상 PASS / FAIL 조건: 계획 §4의 5개 검수 항목이 모두 채워지면 provenance 게이트 PASS.
  그와 별개로 STATUS가 지목한 readonly 관찰 6건을 실측해 계약 위반이 나오면 REJECT+scoped 수리.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `docs/history/laps/probes/20260918_lap383_middle_g2_layout_independent_review_probe.py` (신규, 읽기전용 probe)
  - `docs/work/active/G2_STORAGE_LAYOUT_REPAIR_HANDOFF_LAP383.md` (신규 handoff)
  - `docs/history/laps/20260918_lap383_middle_g2_layout_independent_review.md` (이 기록)
  - `docs/STATUS.md` (갱신)
  - **제품 코드 변경 0.** `patches/**` 무수정(모듈/테스트/frozen 전부 SHA 불변).
  - uncommitted. `LOOP_ALLOW_COMMITS` 기본0, 이번 lap에서 사용자 명시 허용 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 `Syw2plus/syw2plus_original.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
    — probe 실행 전/후 재확인, **무변경**.
  - 검수 대상 `base_preserving_storage_layout_v1.py` `278a00135f9a0b9e7dc2774d9fb0a4d0b16033ca96f678ea84fed32af6ba3a65`
    (lap382 기록값과 일치), 테스트 `7d0cfb40677985568f27799155bfb6c66b6dc1cb4154ade375cacf89f03a365f` (일치).
  - frozen `offline_storage_v1.py` `e9d84513f6a53e27135a7e19a546a8a72165804d1041f9a23719fc7cb249f8cc` — 무수정.
  - 후보 EXE 없음. 게임 실행/Wine/Xvfb 0. 활성 플레이어/지도/군대 fixture 없음(순수 바이트·헤더 계산).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 docs/history/laps/probes/20260918_lap383_middle_g2_layout_independent_review_probe.py`
    → **rc1**, `failures=['foreign_delta_field_equals_true_address_shift',
    'va_guard_rejects_first_N_whose_new_end_reaches_2**32',
    'shrink_discarded_slot_is_not_silently_mapped_outside_its_region',
    'shrink_layout_is_rejected_outright',
    'launcher_rejection_test_actually_invokes_a_launcher_entrypoint',
    'private_pelayout_artifact_preserved_under_designated_temp']` (rc1은 **의도된 검수 판정**이며
    게이트 파손이 아니다 — 필수 게이트는 `docs/history/laps/probes`를 실행하지 않는다, lap339 §확정).
  - `python3 docs/history/laps/probes/20260918_lap380_middle_g2_tail_layout_facts_probe.py` → **rc0 `failures=[]`**
  - `python3 docs/history/laps/probes/20260918_lap381_middle_g2_c1_h1_access_width_probe.py` → **rc0 `failures=[]`**
  - `python3 -m pytest patches/population/test_base_preserving_storage_layout_v1.py -q` → **45 passed**
  - `python3 -m pytest patches/population/ -q` → **90 passed**
  - `make check` → **rc0, 678 passed in 124.02s** + ruff `All checks passed!` + compileall +
    mypy 10파일 `Success: no issues found` + `CONTEXT_PASS` (로그 `/tmp/lap383_makecheck.log`)
  - `bash checks/safety.sh check` → **`SAFETY_PASS`**
  - 캡처 없음(화면/게임 실행 없음).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):

  **계획 §4 provenance 게이트 5항 — 전부 채워짐 (PASS)**
  1. lap380 tail probe rc0 — PASS(재실행 실측). 2. C1 바이트 증거(lap381 probe) rc0 — PASS(재실행).
  3. 모듈/테스트 현행 SHA 일치 + targeted 45 / dir 90 — PASS. 4. `make check` rc0 678 +
  `SAFETY_PASS`, 보호 anchor(`docs/reference`, `docs/baseline/golden` 4파일) 불변 — PASS.
  5. 원본 무변경, 공유 temp 쓰기 0, residue 0 — PASS.

  **독립 재유도로 확인한 lap382의 옳은 부분 (PASS)**
  - `build_layout_artifact(원본, 1200)` **바이트 완전 동일** — 항등 앵커 artifact 절반 성립.
  - `.rsrc` 리소스 디렉터리를 **직접 트리 walk**해 leaf **9개** 재유도 → 로컬 오프셋이 모듈
    `PAYLOAD_ENTRY_OFFSETS`와 정확히 일치(모듈 상수 미사용). 각 leaf `OffsetToData`가 stock에서
    `.rsrc` 범위 내부임도 확인. `SizeOfImage=0xC8F000`, `.rsrc` VA/raw/size 독립 일치.
  - N=4001/9601/9904 artifact의 변경 바이트가 **독립 유도한** 허용 필드 범위의 부분집합(차집합 **0**).
  - 확장 후 `.data` VirtualSize가 늘어난 tail을 여전히 덮고(예 N=9904: `0x2044638` ≥ `0x192E50A`),
    새 `.rsrc` RVA와 겹치지 않으며, `SizeOfImage`가 `.rsrc` 끝을 덮는다 — 3개 N 전부 PASS.
    stock `.data` 끝과 `.rsrc` 사이 slack **`0x5C8`** 실측(의미 UNKNOWN, lap382 위험 (2) 그대로).
  - N=1200 항등 probe 36개 중 항등 파손 **0건**. unmappable은 **정확히 1개**(`0x0066B78F`,
    최하위 영역 아래라 정당) ⇒ STATUS가 물은 "±1 항등 계약 vs unmappable 정책 충돌"은 **충돌 아님**.

  **계약 위반 4건 + 증거품질 2건 (FAIL → REJECT 사유)**
  - **R1 조용한 오사상(FAIL, 최우선).** `layout(n)`이 `n>=1`을 다 받는다. N=100에서
    `map_va(0x66B790+0x758*1199, 100)` → `kind="region"`, `new_va=0x891CB8`. `unit_pool` 새 범위는
    `[0x66B790,0x6995F0)`이고 `0x891CB8`은 **`gap_after_active_slot_list` 외래 블록 내부**다.
    계약 §3-3("사상 불가를 조용히 흘리지 않는다")이 축소 방향에서 무효.
  - **R2 `ForeignLayout.delta`(FAIL).** 계약 §3-2는 delta=누적 삽입량인데, N=4001에서 gap 4개의
    delta가 전부 **0**이고 실제 이동량은 5,265,880 / 5,277,084 / 5,299,492 / 5,305,094다.
    `rsrc`만 delta에 주소 이동량(5,308,416)을 담아 **같은 필드가 세 의미**로 쓰인다.
    수치 영향은 현재 0(`new_start`는 `running_delta`로 옳게 계산되고 artifact 빌더는 `.delta`를
    쓰지 않음)이나, **lap381이 명시적으로 정정한 오류를 공개 필드값이 재현**한다.
    lap382 테스트 이름은 이 정정을 지킨다고 주장하면서 정작 `.delta`가 아닌
    `new_start-old_start`를 단언한다.
  - **R3 32비트 VA 가드(FAIL).** `rsrc.new_end >= IMAGE_BASE + 2**32`는 VA 상한이 아니다.
    이분 탐색 실측 **N=2,259,703**에서 `rsrc.new_end=0x1000000F0`(>`2**32`)인데 `layout()`이 수락한다.
    공학 범위(≤9904)에서는 도달 불가지만 필수 회귀 "모든 새 VA < 2^32"는 문자 그대로 깨졌다.
  - **R4 필수 산출물 미완료(FAIL).** `temp/Syw2plus_patch/` 전체에 `.pelayout` **0개**,
    결정적 mapping 덤프 **0개**. `write_layout_artifact`는 pytest `tmp_path`에서만 호출돼 사라진다.
    lap381 정정("private non-launchable PE-layout artifact는 필수")이 실물로 남지 않았다.
  - **R5 launcher 거부 증거(FAIL).** `test_expanded_artifact_sha_would_be_rejected_by_the_repo_
    launcher_pin`은 AST 기준 실제 호출이 `build_layout_artifact`/`sha256`/`hexdigest`뿐,
    `check_runtime`/`prepare`/`Popen` **0건**. 상수 비교이지 "프로세스 시작 전 거부" 관측이 아니다.
    **자기 함정 기록:** 이 lap의 첫 검사는 단순 grep이라 테스트 **docstring**의 `subprocess.Popen`
    문구에 걸려 **거짓 PASS**를 냈다. AST 파싱으로 정정했다. 이후 grep식 호출 검수는 금지한다.
  - **R6 항등 앵커 blanket skip(경미).** unmappable이면 무조건 `continue`라, 지금은 결함이 아니지만
    향후 다수 probe가 unmappable이 돼도 조용히 통과한다. 허용 주소 1개를 명시 고정해야 한다.

  **계획 §3-5 미이행(수리 아님, 지정 필요).** 모듈에 `0x892410` 3중 alias도 PlayerStruct span도
  문자열/공개 심볼 **0건**. count/endpoint alias는 `count_bytes`로 접혀 충족. 이 카드에 넣을지
  다음 카드로 뺄지는 work tier가 임의로 정하지 말고 계획 문서에 명시한다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 회귀 없음. 이번 lap은 제품 코드를 건드리지 않았다(`patches/**` SHA 3종 불변).
  - **판정: REJECT — scoped 수리 1회.** lap382의 핵심 기하는 독립 재유도로 **옳다**. 되돌리지 않는다.
    수리 6건은 전부 국소이며 새 조사·새 주소 추론·새 카드가 필요 없다.
    handoff: `docs/work/active/G2_STORAGE_LAYOUT_REPAIR_HANDOFF_LAP383.md`.
  - 사용자 마일스톤 승인: 없음, 요청하지 않음(APPROVALS.md 갱신 없음).
    이 REJECT도 ACCEPT도 G2 제품 완료/런타임 승인이 아니다. lap379 Sol의
    integration/broad patcher/runtime NO-GO는 유효하고 17,584 linear 후보 부채도 그대로다.
  - `make check` rc0은 **Fast일 뿐** 실제 앱/24k/144k/멀티 증거가 아니다.
- uncommitted 파일 해시 (`LOOP_ALLOW_COMMITS=0`, PROMPT ⑤):
  - `docs/history/laps/probes/20260918_lap383_middle_g2_layout_independent_review_probe.py`
    `3bfea6356184208a107d26b1844283c03f3fa514e25b5282738180faae7c28d0`
  - `docs/work/active/G2_STORAGE_LAYOUT_REPAIR_HANDOFF_LAP383.md`
    `8597603a01f40674308143991bf1bf0937f6a9c8a05a8c42ca1ba84729f606a4`
  - `docs/STATUS.md` `16d5a1f1940056b1b0e3d450c4f7b23aab2c90ea9cb74693b7995b6c22277c11` (123줄, `CONTEXT_PASS`)
  - `docs/work/active/G2_STORAGE_LAYOUT_SONNET_HANDOFF_LAP381.md` — "소비됨" 배너만 추가.
  - 문서 편집 후 `make check` **rc0 678 passed 123.65s** + `SAFETY_PASS` 재실측.
  - 공유 temp 쓰기 0 (이번 lap 신규 파일 없음), 공유/원본/참고 저장소 무변경.
- 다음 한 가지: work tier(Sonnet5/high)가 위 handoff의 **R1~R6만** 수리하고 각 항목에 회귀를
  붙인다. R4는 지정 temp에 실물 `.pelayout` + mapping 덤프를 남기고 경로·SHA를 기록한다.
  범위 확대 금지. 완료 후 다음 중간 lap이 재검수한다.
