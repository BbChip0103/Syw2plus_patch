# 2026-09-27 APPROVALS lap695~699 G2 8인×10000 항목 압축 (원문 44줄, 세션 lap710)

SHA256(원문): 2eea22c0c4af8101915dc323a6f4d829371ea155d82f8f01adcffb8fae99a824

```
- [ ] **2026-09-27 lap699 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님):**
  01:39 지시(lap698 수용, A/B 판정 대기 중 EXE 무변경 하네스 확장) ①~④ 전부 raw 증거로 완료.
  ① 중앙값-근접 혼합군(cost13/20) 1인·8인 천장 실측: `count=492/500,used=7020/10000`(목표 대비
  -30%), 엔진 Gate가 count_cap보다 항상 **-8**에서 거부(cap250 표본과 동일 오프셋, 신규 관찰·원인
  미상). ② 판별형 저장/로드 PASS: 저장 후 owner0 `used`를 10000→1로 변조→로드→
  `restored_used=10000` 확인. ③ 3000-tick 진행 후 전역 1248/중복0/bitmap 일치 유지, 전투 시도는
  엔진이 `raw_return=0`으로 거부(비전투형 fixture 추정, UNKNOWN 유지). ④ lap695/697 "브리지 SHA
  불일치"는 `bridge_sha256`이 서로 다른 두 대상(빌드 매니페스트=소스 해시 vs probe provenance=
  컴파일된 DLL 해시)에 같은 이름으로 쓰인 명명 충돌이었음을 확인·정정(원문 수치는 실제로 맞았다).
  게임 EXE/후보 코드 무변경, `make check` 1025 passed(761.95s), SAFETY_PASS. **G2 방향(A/B) 판정은
  여전히 사용자 전권 대기 — 이 lap은 그 판정 자료를 보탰을 뿐이다.** 근거
  `../history/laps/20260927_lap699_work_g2_median_cost_ceiling_discriminative_saveload_tick_stability.md`.
- [ ] **2026-09-27 lap697 work tier(Claude Code Sonnet, 다음 middle 검수 대기, G2 8인×10000
  누적 후보를 middle 승격 요청):** STATUS/INBOX 2026-09-27 01:05 지시(전역 유닛 열거 도구 수리)를
  완료. 근본원인은 `global_live_count`가 profile 없이 호출돼 STOCK_POOL(옛 주소)로 폴백한 것 —
  `g2_supply10000_pool4092_owner500` profile을 `POOL_PROFILE_LAYOUTS`에 등록하고 `active_slot_list`
  (6번째 영역) 디코드를 추가했다. 8인×10000 fixture(save-load 포함) 라이브 재실행: **`final_global_
  live=1248`(8×156) == `owner_count_sum` == `active_slot_list_count` == `exists_bitmap_count`,
  `duplicate_count=0`, `matches_existence_bitmap=true`**, 저장→로드 후에도 동일(`owners_ok_after_
  load=8`). `make check` 1025 passed(755.05s), ruff/mypy/CONTEXT_PASS/safety 전부 PASS, 신규 단위
  테스트 6개 PASS(gdb/Wine 불필요, fake-memory). 원본 SHA 실행 전후 불변, cleanup ok, 크래시0.
  **미해결:** category_slot_list_a/b(6-영역 중 4·5번째)는 이번 교차검증 범위 밖. 근거
  `../history/laps/20260927_lap697_work_g2_pool4092_global_live_enumeration_pass.md`. **work tier
  판단으로 G2 8인×10000 누적 후보(lap691~697: 전비10000·4092풀·개인500·저장로드·전역열거 무결성)를
  middle 독립 검수로 승격 요청한다.**
- [ ] 2026-09-27 lap696 work tier(Claude Code Sonnet, 다음 middle 검수 대기): lap695 handoff ①
  저장→로드 1회 실행. 기존 `tools/g2_supply10000_pool4092_eight_owner_probe.py`에 옵트인
  `--save-load` 플래그만 추가(기본 동작 무변경)해 브리지 native `op=2`(0x440c20 저장)/`op=3`
  (0x440ff0 로드)를 직접 호출(UI pause-menu 좌표는 G5가 다른 해상도에서 캘리브레이션한 값이라
  이식 근거가 없어 기각). **로드 후 owner0~7 전원 `used=10000, count=156, count_cap=500,
  cap=10000` 유지 확인(PASS_ALL_EIGHT_SUPPLY10000_SAVE_LOAD)**, 원본 SHA 실행 전후 불변, cleanup
  ok, 크래시 0. `make check` 1019 passed(828.01s), ruff/mypy/CONTEXT_PASS/safety 전부 PASS.
  **미해결(lap695와 동일 한계 지속):** "detailed" 전역 유닛 열거(`global_live_count`)가 이번에도 0
  반환 — 전역 풀 중복/손상 없음은 별도 도구 수리 없이 미확인. 근거
  `../history/laps/20260927_lap696_work_g2_supply10000_saveload_pass.md`.
- [ ] 2026-09-27 lap695 work tier(Claude Code Sonnet, 다음 middle 검수 대기): 00:05 운영자 판정(전역
  풀 확장 채택)에 따라 신규 `patches/population/g2_supply10000_pool4092_owner500.py`로 보호 원본
  위에서 ESL 계열에서 이미 검증된 4092-슬롯 풀 재배치(개인500)를 이식하고 전비10000을 조합, lap694
  8인 probe를 새 풀 용량으로 재실행 — **owner0~7 전원 `used=10000, count=156, count_cap=500` 도달
  (PASS_ALL_EIGHT_SUPPLY10000)**, 크래시0·잠금0·cleanup ok·원본SHA 불변. `make check` 1019
  passed(769.54s), ruff/mypy/CONTEXT_PASS/safety 전부 PASS. **미해결:** "detailed" 전역 유닛 열거
  도구가 0을 반환(브리지가 6-영역 중 3영역 주소만 아는 것으로 추정, 미검증) — 전역 풀 중복/손상 없음은
  이 lap이 별도로 확인하지 못했다. 저장/로드 1회(운영자 지시 마지막 단계)도 미실행. 근거
  `../history/laps/20260927_lap695_work_g2_supply10000_pool4092_eight_owner_pass.md`.
```
