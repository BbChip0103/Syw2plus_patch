# 2026-09-18 | lap 386 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`/high, 실무(work) 역할.
  `docs/MODEL_ROUTING.md` 2026-09-18T17:56:55+09:00 override 준수.
- 가설 / 사용자 관찰: `G2_LAYOUT_ALIAS_EXPOSURE_HANDOFF_LAP385.md` §3-5 Part A만 구현하면
  `0x892410` 3중 alias가 새 상수 없이 `unit_pool.new_end`에서 유도 노출되고, 회귀 3종이
  N=1200 핀/확장 시프트/유도 항등을 고정한다.
- 예상 PASS / FAIL 조건: `LayoutResult.bulk_state_base`가 N=1200에서 정확히 `0x892410`,
  확장 N에서 `0x892410+0x758*(N-1200)`, 항상 `regions[0].new_end`와 동일. `make check` rc0,
  `SAFETY_PASS`, 원본/frozen 불변, 기존 회귀 0.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `patches/population/base_preserving_storage_layout_v1.py`
    (이전 `7ae85ef5…a136cb2` → 이후 `7fac1659…9f0ab6f2`): `LayoutResult.bulk_state_base`
    property 추가(A1), docstring에 3중 이름 명시 + 미모형화 blob 경고(A3).
  - `patches/population/test_base_preserving_storage_layout_v1.py`
    (이전 `88672c65…c8ccee9a` → 이후 `c1fc5bcf…9ce0523`): pytest 3건 추가(A2).
  - `patches/population/offline_storage_v1.py`: 무변경(frozen `e9d84513…9f8cc` 확인).
  - LOOP_ALLOW_COMMITS 미설정 — **uncommitted**로 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e0…c9c08a8ac`(불변, `../Syw2plus/syw2plus_original.exe` 재해시로 확인). 후보 EXE
  생성/게임 실행 없음(범위 밖). fixture 없음 — 순수 geometry 유닛테스트.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 -m pytest patches/population/test_base_preserving_storage_layout_v1.py -q` → 56 passed.
  - `make check` → `689 passed in 118.87s` + Ruff all-checks-passed + compileall + mypy10파일
    success + `CONTEXT_PASS`.
  - `bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): Part A **ACCEPT 대상**(work 자체판정 아님,
  다음 middle 독립검수 대기). A1/A2/A3 전부 구현. Part B(PlayerStruct span/bulk span 상대유도)는
  **의도적으로 미착수**(handoff 범위 밖 STOP 준수).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 48건+lap385까지의 681건 전부 유지,
  이번 회차 신규 8건(collect 기준) 포함 총 689 passed, 실패/스킵 없음(원본 fixture 존재 환경).
  §3 계약 5번은 Part B 미이행으로 **OPEN** 유지 — 이 카드로 완료 처리하지 않는다. G2 8인5000은
  lifecycle/economy/save/LAN 미완료. 독립 검수(Opus5/high middle)·사용자 마일스톤 승인 모두 미실시.
- 다음 한 가지: 다음 새 middle(Opus5/high)가 이번 Part A 구현(A1~A3)을 독립 재유도로 검수한다.
  ACCEPT 시 Part B(PlayerStruct span `0x956770`/stride `0x3ABC`, bulk span 상대유도) 착수 여부와
  카드 발행은 계획/컨펌 역할이 정한다. implementation-unchanged-streak는 이번 회차 제품코드
  변경으로 **0**.
