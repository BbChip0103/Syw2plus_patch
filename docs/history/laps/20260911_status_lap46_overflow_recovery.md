# 2026-09-11 | lap 46 이후 | STATUS overflow 복구 기록

lap46 종료 기록으로 `docs/STATUS.md`가 188줄이 되어 180줄 safety gate를 넘었다.
현재 판정과 최신 이력은 유지하고, 아래 과거 요약만 이 파일로 이동했다.

- setup/lap2~4: M0 완료, Astra 계획, Sol G1-A 카드, Luna 첫 G1-A FAIL.
- lap5~6: PS13 원인 검토와 loop 반환코드 회귀 진단.
- lap7~10: Luna 수리와 Sol 의미 검수 두 차례; Fast 최대83 PASS.
- lap11: Opus5가 exit75 계약 provenance 해결.
- lap12: Luna 회귀 추가, 부모 환경 상속으로 targeted 1 FAIL.
- lap13: Opus5가 테스트 격리 결함 확정; STATUS 길이 safety STOP.
- lap14: Luna가 `tests/conftest.py` 추가; targeted/combined/Fast/safety PASS, middle 검수 대기.
- lap15: Sol 독립 검수 PASS; controller 수리 닫고 G1-A를 Luna work에 반환.
- lap16~21: 원본 run FAIL→middle 진단→work 수리→middle REVISE→work 의미 회귀 수리→middle CONFIRMED.

이 이동은 다음 Sol/high 진단 세션을 시작하기 위한 문서 safety 복구이며 코드, 하네스,
게임, EXE, DLL, 자산 또는 보존된 runtime 증거를 변경하지 않는다.
