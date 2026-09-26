# 2026-09-12 | lap 293 | G1/S1 missing-definition guard bounded repair

- 실제 provider/model/effort / 지정 역할: Codex work tier / hands-on 구현 작업자 / high.
- 가설 / 사용자 관찰: lap292의 `pinned["y"]` 예외를 `pinned.get` 기반 튜플 가드로 바꾸면
  정의 누락 mutant가 명명된 failure를 출력하고 exit 1이 된다.
- 예상 PASS / FAIL 조건: 정상 probe exit0 및 기존 JSON 바이트 동일, 동행 4종 SHA 불변,
  missing-definition mutant가 traceback 없이 `G1_UNIT_Y_OFFSET definition missing...`을
  출력하고 exit1. 범위 밖 추가 수정은 하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`의 튜플 가드만
  변경. 이전 SHA `100f991b…cb999f84` → 현재 `edefa0e4b82d39034ddd14055e09a651998d2a8c93e5d27ab0f168bc7b47f61d`.
  커밋 없음 (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 EXE 없음.
  Linux `.venv`와 정적 objdump, 임시 mutant sandbox; 게임 fixture/Wine/Xvfb/Stage B/runtime
  예산/원본·구현 모듈 쓰기 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 정상
  `.venv/bin/python docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`
  → exit0, JSON `3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126`, 보존
  report와 byte-identical. lap292 review probe fresh 실행 → exit1: 동행 4종은
  `e848c940…`, `e0f07f3a…`, `28703830…`, `7381b5f7…` 불변; missing-definition mutant는
  stdout 0바이트/traceback. 정확한 재현은 `line 156 pinned[name]`, `KeyError: 'y'`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 정상 정적 측정값은 literal 21, CRT 22/22,
  layer 28, 기존 보고서와 동일. 지정 수리의 정상 경로 PASS, 필수 mutant 게이트 FAIL.
  범위 밖 수리와 `make check`는 중단했다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 현재 변경과 근거를 보존하고
  `loop/ESCALATE_SOL`에 승격했다. `EXPECTED_SHA`도 아직 lap292 target SHA를 가리켜 fresh
  review provenance가 별도 mismatch를 내므로, 승격 작업자가 범위·검수 fixture를 먼저 판정해야
  한다. S1 카드 종결·Stage B·제품 G1~G4·사용자 승인은 없다.
- 다음 한 가지: Sol/승격 작업자가 `refs`의 `pinned[name]` 재인덱싱을 §4.5.3 범위에 포함할지
  독립 판정하고, 허용 시 최소 수리 후 fresh middle probe와 `make check`를 순서대로 재검증한다.
