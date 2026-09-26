# 2026-09-12 | lap 295 | G1/S1 missing-definition guard bounded repair

- 실제 provider/model/effort / 지정 역할: Codex work tier / hands-on 구현 작업자 / high.
- 가설 / 사용자 관찰: lap294 §4.6.4대로 `pinned`의 두 무방비 소비처를 가드하면 정의 삭제
  mutant가 traceback/0바이트 없이 명명 failure를 내고 정상 report는 보존된다.
- 예상 PASS / FAIL 조건: 정상 target probe exit0 및 기존 report 바이트 동일, lap292 동행 4종
  불변, x/y/internal_id 정의 삭제가 모두 exit1·명명 failure·비제로 stdout, `make check` PASS.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py` 두 소비처만
  변경. 이전 SHA `edefa0e4b82d39034ddd14055e09a651998d2a8c93e5d27ab0f168bc7b47f61d` →
  현재 `88d8628119cab28457fe32ce02e0be823e940e4a64a5f6b43da251daf2d9a18d`. 커밋 없음
  (`LOOP_ALLOW_COMMITS=0`); 두 review probe의 `EXPECTED_SHA`는 편집하지 않았다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변; 후보 EXE 없음.
  Linux `.venv` Python 3.13.5 + `/usr/bin/objdump` 정적 probe와 tempfile mutant sandbox.
  게임 fixture/활성 플레이어/지도/군대 없음; Wine/Xvfb/Stage B/runtime/PNG 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `.venv/bin/python docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`
     → exit0, stdout/report `3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126`,
     `logs/lap280/s1_crossverify_probe.json`과 바이트 동일.
  2. `.venv/bin/python docs/history/laps/probes/20260912_lap292_middle_lap280_repair_review_probe.py`
     → exit1; 유일한 top-level failure는 stale target SHA `88d86281… != 100f991b…`.
     동행 4종은 `e848c940…`, `e0f07f3a…`, `28703830…`, `7381b5f7…`; control exit0,
     4 mutant exit1·traceback false.
  3. `.venv/bin/python docs/history/laps/probes/20260912_lap294_middle_missing_definition_scope_probe.py`
     → exit1은 old-state assertion/target SHA mismatch. 현재 as_is의 removed_x/y/internal_id는
     각각 1,083/1,083/1,073 B 명명 failure, crash null; `scope_verdict=sufficient`.
  4. `make check` → 292 passed (46.36s), ruff/compileall/mypy/`CONTEXT_PASS`.
     `bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 지정 bounded repair와 기계 회귀 **PASS**.
  stale historical `EXPECTED_SHA`/old-state assertions는 예상된 **SKIP/기록된 mismatch**이며
  review fixture를 자동 갱신하지 않았다. 제품 G1~G4 실제 실행 증거는 **SKIP**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본 EXE, `tools/runtime_env.py`
  (`dd2ad043…8500190`), `patches/population/runtime_driver.py` (`ae4ff939…4e4291b5`)와
  보존 report는 불변. 다음 새 middle 세션이 target normal/mutants/companions를 독립 검수해야
  하며, S1 카드 종결·Stage B·제품 승인은 없다.
- 다음 한 가지: 다음 새 middle tier가 lap295 bounded repair를 독립 검수한다. 그 전에는
  `EXPECTED_SHA` 수정, Stage B/Wine/runtime 실행, G1~G4 승격을 하지 않는다.
