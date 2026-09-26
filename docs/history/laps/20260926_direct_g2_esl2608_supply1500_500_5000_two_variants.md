# 2026-09-26 사용자 직접 요청: 2608 G2 전비1500-500-5000 두 종

- 요청: AI상점개설·장수7명 G2 4092/500 일반 및 시작자리고정 EXE를 전비 공식 1500+500×장수(7명=5000)로 별도 생성. 사용자는 이전 1600-200-3000판을 플레이해 정상 동작했다고 보고했으나 이는 새 전비판의 검증으로 자동 승격하지 않는다.
- 입력: 기존 G2 1600-200-3000 일반 SHA `2642b7f756312eefc7c5515465e1d67a1a10410976fc41e6dd390539ca99aa22`, 고정 SHA `2f617567438952a6a765f3cccbf93190d9dca6b420a9c53937f79c2fa6225751`. 별도의 미패치 1500-500-5000 EXE는 공유 폴더에서 발견되지 않아 검증된 G2 사본의 전비 operand 두 곳만 변경한다.
- 변경: `patches/population/g2_esl2608_supply1500_500_5000.py`, 전용 테스트, 주소 문서 `analysis/memory_maps/g2_esl2608_supply1500_500_5000_20260926.md`. 원본·기존 G2 입력 무변경; 커밋 없음.
- 초기 후보 SHA: 일반 `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60`, 고정 `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f`.
- 정적 게이트: 전용 pytest 4 passed, Ruff, 단일 모듈 mypy PASS. 기존 2608 G2 모듈 회귀 6 passed.
- 격리 실게임 실행: `tools/runtime_env.py prepare`의 별도 전체 게임 복사본/Win32 prefix, 2608 Data·타일 등 사본 overlay, 사적 Xvfb/실제 X11 클릭. 전용 probe `../temp/Syw2plus_patch/g2_esl2608_20260926/high_slot_normal_production_roundtrip_probe.py`를 두 후보 각각에 실행했다. `local/runtime/g2_esl2608_supply1500_{seven,fixed}/*/output/g2_ingame_probe.json` 둘 다 `PENDING_PRODUCTION_ROUNDTRIP_PASS`, cleanup true. 시작 player `count=2, used=20, count_cap=500, cap=1500`, HQ slot4092. 생산 대기 중 저장→300 tick 이상→로드 후 tick 되감김·예약 유지→count3/used30. 종료 후 해당 사적 게임 사본만 정리하고 증거·manifest·캡처 보존.
- `make doctor` 성공(기본 runtime manifest 부재는 optional; 각 실게임 run은 자체 manifest 사용). `make check` 909 passed/729.27s, Ruff·compileall·지정 mypy·CONTEXT_PASS. `checks/safety.py` SAFETY_PASS. 로그 `../temp/Syw2plus_patch/g2_esl2608_supply1500_500_5000_20260926/make_check.log`.
- 사용자 요청 `../260921_temp/`에 두 EXE를 기존 파일과 다른 이름으로 독점 생성(`xb`)하고 SHA 재검증. 안내문 `G2_2608_전비1500-500-5000_개인500_공용4092_읽어주세요.txt` 동봉. PE 10섹션/파서 경고0, 두 immediate와 장수상한 7 확인.
- 판정: 두 종 단일플레이 시작·입력·생산·저장로드는 PASS. 장수 7명 실제 도달/8인×5000·LAN·장기 안정성은 미검증; G2 마일스톤 완료 아님.
