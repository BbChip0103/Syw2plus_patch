# 2026-09-18 | lap 384 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`/high, 실무(work) tier.
  `docs/MODEL_ROUTING.md` 2026-09-18T17:56 override와 일치.
- 가설 / 사용자 관찰: `G2_STORAGE_LAYOUT_REPAIR_HANDOFF_LAP383.md`의 R1~R6(lap383 middle REJECT
  근거)만 scoped 수리하면 독립 검수 probe의 6개 FAIL이 해소된다. 새 조사/새 주소 추론 없음.
- 예상 PASS / FAIL 조건: R1~R6 각 항목 회귀 추가 + `make check`/`checks/safety.sh check` PASS +
  원본 SHA 불변 + frozen `offline_storage_v1.py` 무수정 + 게임실행/커밋 0.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `patches/population/base_preserving_storage_layout_v1.py`
    (신규 SHA256 `7ae85ef50ae324a42a16f8cb251b05498f22f18a7d9f84d20cd361bf1a136cb2`,
    이전 lap382 SHA `278a00135f9a0b9e7dc2774d9fb0a4d0b16033ca96f678ea84fed32af6ba3a65`)
  - `patches/population/test_base_preserving_storage_layout_v1.py`
    (신규 SHA256 `88672c65a91185526296a81e25008b352756eda2bf6569ba8d3a4b3fc8ccee9a`,
    이전 lap382 SHA `7d0cfb40677985568f27799155bfb6c66b6dc1cb4154ade375cacf89f03a365f`)
  - `patches/population/offline_storage_v1.py` **무변경**(SHA256
    `e9d84513f6a53e27135a7e19a546a8a72165804d1041f9a23719fc7cb249f8cc`, 확인 완료).
  - uncommitted (LOOP_ALLOW_COMMITS 기본0, 커밋 없음).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(빌드 전/후 재확인, 불변).
  게임 실행/활성 플레이어/지도 없음 — 이 카드는 순수 PE 레이아웃 계산기 수리, 런타임 fixture 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 -m pytest patches/population/test_base_preserving_storage_layout_v1.py -q` → 48 passed
    (기존45 + 신규3).
  - `make check` → `681 passed 117.37s` + Ruff/compileall/mypy10파일 `Success` + `CONTEXT_PASS`.
  - `bash checks/safety.sh check` → `SAFETY_PASS`.
  - R4 산출물(지정 temp, 메인레포 아님):
    `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260918_lap383_layout_artifact/g2_layout_n4001.pelayout`
    SHA256 `38a7148ed7395de74c144329ec43f14ec3b0fefe394a5f2ab01d8ca436cbc808`
    (N=4001, 공학값. `write_layout_artifact` 경유, `.pelayout` 확장자만, 실행/배포 없음) 및
    `g2_layout_n4001_mapping.json`(결정적 `layout(4001)`/`map_va` 덤프) SHA256
    `fb7f9e833f0d66985d4fbf814b7af89bd62c205216a75d10b650d11c91605b18`.
  - 독립 검수 probe 재실행(읽기전용, `docs/history/laps/probes/20260918_lap383_middle_g2_layout_independent_review_probe.py`,
    **수정 안 함**): `module_sha_matches_lap382_record` FAIL은 **예상됨**(모듈이 이번에 바뀌었으므로).
    R1~R3 관련 항목은 모두 **PASS**로 반전(`foreign_delta_field_equals_true_address_shift` PASS,
    `va_guard_rejects_first_N_whose_new_end_reaches_2**32` PASS). R1 항목
    (`shrink_discarded_slot_is_not_silently_mapped_outside_its_region`)은 probe가 `layout(n<1200)`이
    **값을 반환**한다고 가정한 옛 스크립트라 새 `ValueError`에서 **Traceback으로 중단**함 — 이는
    회귀가 아니라 R1 수리가 정확히 요구한 거부 동작이 옛 진단 스크립트의 가정을 깬 것.
    이 옛 probe는 진단 증거이지 게이트가 아니며(수정 금지), 실제 회귀는 pytest 신규 3건과
    `make check` 681건이 담당한다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - R1 PASS: `layout(n<1200)` → `ValueError`; `map_va(0x66B790+0x758*1199, 1199)` → 같은 `ValueError`
    (더 이상 `gap_after_active_slot_list` 내부로 조용히 사상되지 않음).
  - R2 PASS: 모든 `ForeignLayout.delta == new_start-old_start`(N=4001 gap 4개 실측
    5,265,880/5,277,084/5,299,492/5,305,094, rsrc 5,308,416 — 전부 일치). 회귀는 `.delta` 필드
    자체를 단언(재계산 아님).
  - R3 PASS: 가드를 `rsrc.new_end >= 2**32`로 수정. 경계 회귀 N=2,259,702(accept)/2,259,703(raise)
    양쪽 확인.
  - R4 PASS: 지정 temp에 실물 `.pelayout` + JSON mapping 덤프 생성, 경로/SHA 위 기록.
  - R5 PASS: `test_expanded_artifact_is_actually_rejected_by_the_repo_launcher_entrypoint_with_zero_popen`가
    `tools/runtime_env.validate_original_source`(실제 진입점)를 확장 artifact가 든 소스 디렉터리로
    호출해 `RuntimeSafetyError`(SHA-256 mismatch)를 관측하고 `subprocess.Popen` monkeypatch로 0회
    호출을 단언(호출 시 AssertionError). AST 검수 아님, 실제 실행 검수로 대체.
  - R6 PASS: blanket `unmappable` skip을 `0x0066B78F` 1개로 고정, 그 외 unmappable이면 즉시 FAIL.
  - 계획§3-5(0x892410 3중alias/PlayerStruct span) 미이행 — **의도적으로 손대지 않음**(아래 참고).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 신규 pytest 5건 추가
  (`test_layout_rejects_shrink_below_stock_capacity`,
  `test_map_va_rejects_shrink_instead_of_silently_mapping_outside_its_region`,
  `test_layout_va_guard_boundary_is_the_true_32bit_limit`,
  `test_n1200_map_va_is_identity_at_every_boundary_and_its_neighbors`의 R6 강화,
  `test_expanded_artifact_is_actually_rejected_by_the_repo_launcher_entrypoint_with_zero_popen`).
  `test_expansion_foreign_blocks_shift_by_cumulative_insertion_below_not_delta_zero`는 기존 이름 유지,
  본문만 `.delta` 필드 직접 단언으로 교체. 독립 검수(다음 새 middle/Opus5 세션) 대기 — 이 세션은
  자기 결과를 최종 승인하지 않는다. §3-5는 계획 문서(`G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md`)
  §3-5 자체가 "이 카드 포함/다음 카드 이관을 work tier가 임의로 정하지 않는다"고 명시했으므로
  **의도적으로 미착수**; 다음 middle/Astra가 범위를 판정해야 한다. G2 8인5000 전체는 여전히 미완료
  (integration/lifecycle/economy/save/LAN 없음), 이 카드는 lap382 layout 계산기의 계약 위반 6건만
  닫는다.
- 다음 한 가지: 다음 새 middle(Opus5/high) 세션이 이번 R1~R6 수리를 독립 재유도로 검수하고
  (a) `make check`/`safety.sh` 재실행, (b) R1~R6 각 항목의 실측 재확인, (c) §3-5(0x892410 3중alias/
  PlayerStruct span)를 이 카드에 넣을지 별도 카드로 뺄지 계획 문서에 명시하는 판정을 내린다.
  ACCEPT 시에도 이는 layout 계산기 단위 승인일 뿐 G2 8인5000 제품 완료나 통합/lifecycle/economy/
  save/LAN 승인이 아니다.
