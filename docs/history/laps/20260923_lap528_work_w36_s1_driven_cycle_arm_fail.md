# 2026-09-23 | lap528 | 목표 G2 (W36 S1)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 지정 역할 **work**(실무).
- 가설 / 사용자 관찰: 카드 `docs/work/active/G2_S1_DRIVEN_COMBAT_CYCLE_SOAK_LAP527.md`(W36)를 그대로 구현·실행하면
  시딩 {5,7,46,2}(A8')이 8/8 owner에서 T0에 `used`∈[4900,5000]으로 무장되고, 24k 순환 창에서 원본 명령
  `0x415480`으로 실제 교전(`DRIVEN_CYCLE_STABLE` 또는 그 이하 라벨)이 관측될 것으로 예상했다.
- 예상 PASS / FAIL 조건: 카드 §5 표 그대로(`ARM_FAIL`은 "후보 EXE SHA 불일치 · 시그니처 불일치 · type2 preflight
  불일치 · 시딩 receipt 실패 · A1 또는 A8' 미성립 · 첫 op8 전 fault").
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `patches/population/runtime_bridge.c` (op5/op6 allow-list {5,7,46}→{5,7,46,2}, 카드 §2-1)
  - `tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py` ({5,7,46,2} 핀으로 개정)
  - `tests/test_g2_runtime_bridge_op8_order_engagement_contract.py:129` (allow-list 문자열 갱신)
  - 하네스: `temp/Syw2plus_patch/g2_capacity/20260923_lap528_w36_s1_driven_cycle/w36_run.py` (신규, W35 파생)
  - 전부 uncommitted (`LOOP_ALLOW_COMMITS` 미설정, 기본 0).
  - `make check` 828 passed (repo 3파일 변경 뒤 1회, 이번 회차 source 변경 있었음, N22).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 SHA (전/후 불변): `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  - 후보 EXE SHA (재빌드 일치, lap524와 동일): `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`.
  - 브리지 DLL SHA (attempt1) `bc7a7b0ca17b992f27c9134316eaab876c95ae1522e713a3621ddc53af4a1c8c`,
    (attempt2) `bc7a7b0ca17b992f27c9134316eaab876c95ae1522e713a3621ddc53af4a1c8c` — 두 attempt 모두 wrapper `dll_sha256`은
    빌드시각 필드 때문에 달라 보이나 내부 `bridge_sha256`(스텁 포함 실제 DLL 해시)은 동일.
  - 격리 prefix/display: attempt1 `local/runtime/20260923_202023_2855300_0` display `:6528`,
    attempt2 `local/runtime/20260923_202314_2865084_0` display `:6528`(attempt1 정리 후 재사용, 락 없음 확인).
  - 활성 8 owner, cap 5000 확인(PS3). fixture: owner당 op7 rice/wood 1,000,000 +
    op5 type5×100 → op6 type7×25 → op6 type46×20 → op5 type2×60(X=type2, lap527 N184).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python temp/Syw2plus_patch/g2_capacity/20260923_lap528_w36_s1_driven_cycle/w36_run.py` (attempt1, attempt2 동일 명령, 코드 수정 후 재실행).
  - 원시: `temp/Syw2plus_patch/g2_capacity/20260923_lap528_w36_s1_driven_cycle/`
    - `attempt1_arm_fail/{run_summary.json,seed_receipts.json,resource_receipts.json,w36_orchestrator.log,bridge_build/}`
    - (attempt2, 현재 트리) `run_summary.json`, `seed_receipts.json`, `resource_receipts.json`, `w36_orchestrator.log`, `bridge_build/`.
  - `events.jsonl`/`samples.jsonl`은 두 attempt 모두 0바이트다 — Phase B(1000-tick 기준 창) 진입 전에
    T0 무장 판정에서 `ARM_FAIL`로 종료됐기 때문이다(카드 §4 게임 실행은 preflight→시딩→Phase B 순서).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **preflight PASS** (양 attempt): issuer `0x415480` 첫 12바이트 `53568bf1578a861c03000084` 일치,
    type2 행 런타임 값 `cost13,1×1,+0x24&14=0,+0x4C=0x410005` 일치(N185 조건대로).
  - **PS3 cap 확인 PASS**: 8/8 owner `cap=5000`.
  - **시딩 attempt1**: owner0~5 전량 성공(`used`=4950). owner6에서 type2(60기 요청) 도중
    `fixture_exceeds_unreserved_supply`로 46기만 추가되고 **하네스가 즉시 전체 중단**했다 — owner7은
    한 항목도 시도되지 않았다(A1=`[4950,4950,4950,4950,4950,4950,4768,20]`). `verdict=ARM_FAIL`.
  - **N187 (신규, 원인)**: 실패 시점 owner6 ledger `before`={"reserved":220,"used":4170,...}. 이 시점까지
    op5/op6 시딩 호출 32건(owner0~5 완료+owner6 앞 3종)이 전부 성공했고 tick은 겨우 62였다 — 즉 owner6의
    `reserved=220`은 **우리 fixture가 만든 값이 아니라 8인 AI가 시딩 도중(실시간 초 단위)에 스스로 낸
    생산 주문**이다(N81/N82 계열: AI는 시딩 중에도 멈추지 않는다). 시딩을 owner 순서로 직렬 처리하는
    하네스 설계상 뒤쪽 owner일수록 이 경합에 더 노출된다.
  - **하네스 수리(attempt2, N187 대응)**: 시딩 루프를 owner당 1회 고정 수량 요청에서 "부족분 최대 5회
    재요청" 방식으로 바꿨다(부분 성공 시 남은 수량만 재요청, 진행 없으면 그 타입만 포기하고 다음으로
    넘어가며 전체를 중단하지 않음). 측정식·가드·허용목록은 건드리지 않았다.
  - **시딩 attempt2**: owner0~5, owner7 전량 성공(`used`=4950). owner6은 재시도(46추가 후 재요청 14 →
    `no progress`, `reason=fixture_exceeds_unreserved_supply`)에도 **동일하게 46/60에서 멈췄다**
    (`reserved=220`으로 attempt1과 완전히 동일한 값·시점) ⇒ **A1=`[4950,4950,4950,4950,4950,4950,4768,4950]`,
    owner6만 4768<4900로 범위 밖**. A8'는 8/8 PASS(owner6도 type46 20기 생존 등 4종 보유·X≥10·비중≤85% 성립).
    `verdict=ARM_FAIL`(`A1_used_or_A8prime_failed`, 이번엔 A1만 원인).
  - **재현성**: attempt1·attempt2의 owner6 `reserved=220`·`fixture_added=46`이 완전히 일치한다. 목표
    문자열이 `_custom_game_chain_inject_g2_eight_ai_seed42`("seed42")로 고정돼 있어 AI 생산 타이밍이
    결정적으로 재현되는 것으로 보인다 — 즉 이 부족은 **일시적 노이즈가 아니라 이 seed·이 실시간 시딩
    순서 조합에서 구조적으로 재현되는 부족**이다. 카드 §0 항목5의 "하네스만 고쳤을 때 2회 허용" 조건에
    따라 하네스를 고쳐 attempt2를 실행했으나 같은 지점에서 재현됐으므로, **이 카드의 실행 예산(최대2회)을
    모두 소진했다.** 3번째 시도는 하지 않는다(카드 §0 위반).
  - `checks/safety.sh check` exit0 `SAFETY_PASS`, `checks/context_limits.py` exit0 `CONTEXT_PASS`.
    원본 SHA 전후 불변 확인(수동 `sha256sum`, 스크립트가 예외로 조기 종료해 `source_sha_after` 필드
    자체는 비어 있음). 잔류 wine/게임 프로세스 0(수동 `pgrep` 확인).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - Phase B/E/저장로드/op8 교전 측정은 **전혀 실행되지 않았다** — S1의 실제 교전 여부는 이번 lap으로
    아무것도 증명/반증되지 않는다(카드 §5 라벨 대상 데이터 0).
  - N187은 새 사실이다: G2 시딩 하네스가 실시간 순차 처리인 한, AI의 자율 생산이 후순위 owner의
    가용 supply를 갉아먹을 수 있다 — 이는 G2 자체의 "8인 각각 5000" 목표와 무관하게, **향후 모든
    다중-owner 시딩 카드가 겪을 수 있는 구조적 위험**이다.
  - 독립 검수 필요: 다음 middle이 이 판정(ARM_FAIL, N187, 하네스 수리의 타당성)을 원시
    `attempt1_arm_fail/`·현재 attempt2 산출물만으로 재계산해야 한다. 사용자 승인 사항 아님(모델 핀 실행
    실패 보고일 뿐, 목표·안전·배포 범위 변경 없음).
- 다음 한 가지: **middle이 이 ARM_FAIL을 독립 검수하고, N187에 대한 수리 방향(예: 시딩 순서를
  owner-outer 대신 type-outer로 바꿔 노출 시간을 줄이거나, 요청량에 여유 마진을 두거나, A1 판정에
  "재시도 후에도 소폭 부족 시 근접치 허용" 여지를 strategy에 묻는 것 등)을 담은 **새 카드**를 발행한다.
  이 lap은 W36 카드의 실행 예산(최대2회)을 소진했으므로, 같은 카드로 3번째 실행을 시도하지 않는다.
