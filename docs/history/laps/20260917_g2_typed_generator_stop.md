# G2 typed generator — REJECT / STOP

2026-09-17 20:15 KST. 전체8인 각각 전비5000 목표는 ACTIVE/미완료다.

## 경계 및 결론
- 19:46 시작한 45분 실험은 20:32까지 결과 없으면 중단하기로 했다. 한 번 수리한 생성기에도 핵심 증명 오류가 남아 기한 전 중단한다.
- 첫 버전5de8: 실제 x86 음성 반례7개를 승인했다. 수리4751: 이전7개는 거절하지만 새로운3개를 승인한다.
- 알 수 없는 추가 LEA base를0으로 취급하며, 16비트 AX 연산을32비트 전체 EAX 연산처럼 취급한다. 풀4001 안에서도 slot1366 이상에서 부분 shift의 carry 손실이 발생할 수 있다.
- 두 실제 주소4178C1/D5 값이 맞고 후보 PE가 생성되었다는 사실은 범용 생성 규칙의 정확성이 아니다.
- 새 PC별 예외나 세 번째 생성기 수리는 하지 않는다. 실패한 접근일 뿐 전체 G2 불가능 판정은 아니다.

## 증거
외부 기준 경로: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260917_offline_unit_consumers_v1/`.
- `reviewer_adversarial_repaired4751/frozen_generator.py`: SHA2564751686b1d4f05fd091b512e300262269f0573126e473ac0632d616d670a2f36.
- 같은 폴더 `results.json`: 실제 fixture hex/진입점/종료/잘못 방출된 레코드3개, 게임 실행 없음.
- `candidate_v2/root_rejected_generator_v2_verification.json`: Root 독립 재현3개 및 fresh619 tests/128.79초 기록.
- `candidate_v2/paired_fast.log`, `paired_fast_before.sha256`, `paired_fast_post_pins.log`: 전체 검사 및 소스/보호 입력 해시.
- 전체619 tests, Ruff, compileall, 표준mypy10+명시적mypy2, context/shell, CLI 도움말 PASS. 그러나 누락된 음성 사례 때문에 생성기 승인 근거가 되지 못한다.

## 복구 및 다음 분기
Luna는 정확한 실패 소스7개 보존 후 이전 승인된 owner919e 기반 builder/test를 바이트 그대로 복구한다. 새 생성기/테스트2개만 외부 보존하며 launcher는 유지한다. Root는 복구 후 전체 검사를 다시 실행한다. Astra/medium은 큰 교착 분기에서 다음 유한 접근을 재선정한다. 복구/검사 자체를 안정 플레이의 성과로 올리지 않는다.

## 미충족 제품 계약
임의 합법적 저전비 구성, 개인242/roster1200 확장, 공간 버킷169×225, 개체ID/사망/재사용/경제, 확장 저장·새 프로세스 로드·지원LAN, 실제24k/144k 모두 아직 미완료다. 원본/공유DLL/bridge/control 소스 불변, 게임 실행0회.

복구 검증 완료: fresh 전체611 PASS/112.82초·Ruff/compileall/표준mypy10+명시mypy1/context/shell 및 5소스 전후/4보호 입력 pins PASS. 정확7 archive·새2 inactive 이동·이전 소스 byte equality·owner919e EXE equality를 Root 독립 검증. 외부 `root_generator_rollback_verification.json` 참조. 619→611은 실패 구현/시험의 전체 복구이며 관련 소스·반례는 외부 보존되고 실패 판정 유지. 게임 실행/제품 승인 없음.
