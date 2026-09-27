# 2026-09-26 | lap 693 | 목표 인프라(G2 선행 조건)

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5 / high / work(실무)
- 가설 / 사용자 관찰: 2026-09-26 22:52 사용자 결정 — 원본 게임 기준 경로를
  `/home/dev_00/sharedfolder/260320_Syw2plus/[ESL]Syw2plus/`로 전환(보호 원본 EXE는 그 안의
  `[HQ]Syw2plus 2002.exe`, SHA `b56986e0…c9c08a8ac`, 기존과 동일). G2 전비10000 8인 실측보다
  먼저 처리해야 하는 최우선 작업(APPROVALS.md 22:52 항목, STATUS.md "다음 한 가지").
- 예상 PASS / FAIL 조건: ① `tools/runtime_env.py` DEFAULT_SOURCE가 새 경로를 가리키고 원본
  EXE를 파일명이 아니라 SHA로 찾는다 ② check_setup.py/g4_path_fixture_preflight.py/checks/safety.*가
  새 경로도 원본 SHA/경로 불변 검사 대상에 포함 ③ 관련 테스트 갱신 후 `make check` 전부 PASS
  ④ `checks/safety.sh check` PASS ⑤ 새 경로 기준 `runtime_env.py prepare`+부팅 스모크 1회 성공.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): uncommitted(LOOP_ALLOW_COMMITS=0).
  - `tools/runtime_env.py`: `DEFAULT_SOURCE`를 `[ESL]Syw2plus/`로, 옛 경로는 `LEGACY_SOURCE`로 보존.
    `validate_original_source`를 고정 파일명(`syw2plus_original.exe`) 우선 + 못 찾으면 소스 최상위
    `*.exe` 전수를 SHA-256으로 스캔하는 방식으로 재작성(파일명이 다른 새 경로 대응). 심볼릭
    링크 판정·"SHA-256 mismatch"/"not found" 에러 문구는 기존 테스트 계약과 호환되게 분리 유지.
    `prepare()`는 복사 후 실제 원본 파일명과 `ORIGINAL_EXE`(`syw2plus_original.exe`)가 다르면
    사본 안에서 한 번 더 복사해 관례 이름으로 맞춘다(하위 `game / ORIGINAL_EXE` 참조 전부 무변경
    호환). manifest `source.exe` 필드는 실제 원본 파일명을 기록하도록 보정.
  - `tools/check_setup.py`: 로컬 캐시(`Syw2plus/syw2plus_original.exe`)가 없으면 새 경로에서
    SHA로 원본을 찾는 `_resolve_original_exe()` 추가.
  - `checks/safety.py`: 동일한 fallback `_resolve_original_exe(root)` 추가, `check()`가 사용.
  - `tools/g4_path_fixture_preflight.py`: `--exe` 기본값이 새 경로를 먼저 SHA로 찾고 없으면 옛
    `Syw2plus_re/Syw2plus/syw2plus_original.exe`로 fallback(`_resolve_default_exe`).
  - `patches/population/runtime_driver.py`: `validate_game_root`의 보호 원본 목록에
    `[ESL]Syw2plus`를 추가(이 경로를 실행 대상 game_root로 쓰는 것을 명시적으로 차단).
  - 테스트 갱신: `tests/test_g5_stock_selection_array_xrefs.py`(하드코딩된
    `DEFAULT_SOURCE/ORIGINAL_EXE` 대신 `validate_original_source()`로 실제 원본 경로 해석),
    `tests/test_project_setup.py`(새 경로도 `validate_game_root` 거부 목록에 있는지 확인).
    `patches/population/test_base_preserving_storage_layout_v1.py`는 무변경으로 통과(에러 문구
    분리 설계로 회귀 없음, 최초 1회 실패 후 원인 규명·수정).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(양쪽 경로 동일, 사전
  확인). 후보 = 원본 그대로(패치 없음, 순수 경로/조회 방식 변경). fixture 없음(부팅 스모크만).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `runtime_env.prepare(DEFAULT_SOURCE)` → run `20260926_230504_3910905_0`, 사본 exe
    `syw2plus_original.exe` SHA 일치 확인.
  - `runtime_env.smoke(manifest_path, timeout=60)` → 게임 창 "조선의반격"(0xe00001) 기동,
    PS9→PS7 메뉴 입력 반영(`input_effect_observed=true`, `screenshot_changed=true`), cleanup ok.
  - `runtime_env.check_runtime(manifest_path)` → `ok: true`(사후 재검증, 새 경로 source도 재확인).
  - `make check` 1차 995(정정 전) 아님: 1차 1009 passed+1 failed(에러 문구 회귀 발견) →
    수정 후 2차 `logs/gates/20260926_lap693_make_check_v2.log`: **1010 passed in 664.16s**.
  - `.venv/bin/python -m ruff check patches tools tests checks` → All checks passed.
  - `.venv/bin/python -m mypy ...(Makefile lint 대상 10개 파일)` → Success, no issues.
  - `checks/context_limits.py` → CONTEXT_PASS.
  - `checks/safety.sh check` → SAFETY_PASS.
  - local/runtime 위생: 부팅 스모크가 만든 `game/` 사본(810M) 삭제, `output/manifest.json/prefix`는
    보존. 디스크 여유 91GB(실행 전 92GB).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **PASS.** 새 경로 기준 prepare+부팅 스모크 성공,
  make check 1010 passed, ruff/mypy/CONTEXT_PASS/SAFETY_PASS 전부 통과. 옛 경로
  (`Syw2plus_re/Syw2plus`)는 `LEGACY_SOURCE`로 코드에 남아있고 실제 파일도 그대로 보존됨
  (읽기 전용, 이전 측정 재현 가능).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 EXE/원본 저장소 무변경(경로/조회 로직만
  변경). `tools/g4_ai_evidence_inventory.py:86`, `tools/g4_difficulty_absence.py:107`는 사용자
  지시 범위(①②③) 밖이라 옛 `Syw2plus_re` 참조를 그대로 뒀다(G4 관련, 이번 작업 스코프 아님).
  다수의 G5 lap 전용 probe 스크립트(`tools/g5_*_probe*.py`)는 `runtime_env.DEFAULT_SOURCE`를
  그대로 참조하므로 새 경로로 자동 전환되지만, 내부에서 `source / runtime_env.ORIGINAL_EXE`로
  고정 파일명을 직접 이어붙이는 다수 존재 — `--source`를 새 경로로 줘 재실행하면 실제 파일명이
  달라 깨질 수 있다(이번 make check에는 걸리지 않음, 실제 파일 읽기 없이 정적 로직만 테스트되는
  것들이라 통과). 이 스크립트들은 이미 종료된 과거 lap의 일회성 조사 도구라 이번 범위에서는
  손대지 않았고, 새 경로로 그중 하나를 다시 돌릴 필요가 생기면 `validate_original_source()`로
  실제 원본 경로를 구해 쓰도록 그때 개별 수정한다. 독립 검수/사용자 승인 대기 없음(2단/3단 대상
  아닌 인프라 작업).
- 다음 한 가지: STATUS.md 22:52 지시 잔여 — G2 전비10000 8인 동시 실측(개인 개체 상한1200·전역
  풀10,000 병목, `g2_eight_owner_fixture_recipe.md`를 8인으로 확장) 진행.
