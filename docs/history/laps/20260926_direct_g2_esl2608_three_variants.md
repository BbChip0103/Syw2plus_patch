# 2026-09-26 사용자 직접 요청: ESL2608 세 종 G2 시험용

- 요청: `../260921_temp/`의 AI상점개설, 장수7명/전비, 장수7명/전비/시작자리고정 세 EXE에 개인 유닛 초기 상한 500·공용 실사용 풀 4092·초상화 producer scan 수정을 적용한 사본 3개.
- 소스/주소/PE 근거: `analysis/memory_maps/g2_esl2608_pool4092_owner500_port_20260926.md` 및 SHA-고정 빌더 `patches/population/g2_esl2608_pool4092_owner500.py`. 원본·참고 EXE 무변경. 2606 바이너리의 코드 동굴을 그대로 쓰지 않고 2608 전용 세 섹션으로 재배치했다.
- 실패와 수정: 최초 v1은 원본 `save006.dat` 로드 시 load-wrapper `JNE rel8` 오버플로우로 `EIP 0x018952AF`에서 충돌했다. v1은 제공하지 않았다. v2는 `JNE rel32` 및 목적지 테스트로 수정했다.
- v2 SHA256: AI상점 `3c7f0af4ae5e066712dfbb0584a66df85e2371292ea561085e9a52be331588b1`; 장수7명 `2642b7f756312eefc7c5515465e1d67a1a10410976fc41e6dd390539ca99aa22`; 시작자리고정 `2f617567438952a6a765f3cccbf93190d9dca6b420a9c53937f79c2fa6225751`.
- v2 런타임: 세 종류 모두 전용 Wine 전체 게임 복사본에서 실제 클릭, 생산 대기 중 저장/로드, 300 tick 이상 경과, 생산 완료 `PENDING_PRODUCTION_ROUNDTRIP_PASS`. 장수7명판의 구형 원본 세이브 로드와 합성 slot4092 초상화 이동 `DONE`. 기록은 `local/runtime/g2_esl2608_*_v2/.../output/`에 있다.
- 검증: 전용 pytest 6개, Ruff, 단일 모듈 mypy, `checks/safety.py` 통과. 별도 최신 `make check` 903 passed/681.30s, Ruff·compileall·지정 mypy·context PASS. 로그 `../temp/Syw2plus_patch/g2_esl2608_20260926/make_check_v2.log`.
- 결과물: `../260921_temp/`에 세 원본과 다른 `*_G2_개인500_공용4092_시험용.exe` 이름으로 독점 생성(`xb`)했다. 배치 전후 원본 SHA와 배치 후 후보 SHA를 검증했고, 세 PE 모두 10섹션/파서 경고 0. 동봉 안내문 `G2_2608_개인500_공용4092_시험용_읽어주세요.txt`.
- 판정: G2 완료 아님. 8인×전비5000/LAN/자연 등용/장기 안정성 미검증; 시작자리고정판 nation1 장수 생산 완료 관측은 90초 내 미결. `N4K8` 세이브는 과거 G2 실험 EXE와 혼용 금지.
