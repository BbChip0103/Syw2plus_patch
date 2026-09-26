# 2026-09-25 직접 요청 — ESL 2606 두 종 × 개인 1200/공유 풀 10,000

- 사용자 요청: `260921_temp`의 2606 장수7/전비1600-200-3000 두 EXE(일반·시작자리고정)에
  전비 상한 변경 없이 개인 유닛 개수1200과 사용 가능한 공유 풀10,000을 적용한 별도 버전 생성.
- 참고 입력 SHA-256: 일반 `4a03895d8e6690080714fab7e851c3a0e9d44b7cac47fed78fc21a2f5210c6f8`,
  시작자리고정 `daf0b6a07f01d04397018924f9dd0c6ff414148c0547adc2d5c9e0b403a58523`.
  작업 후 동일 SHA 재확인. 핀된 stock `b56986e0…a8ac`.
- 변경: `patches/population/g2_esl2606_pool10000_owner1200.py`, 대응 회귀 테스트,
  `analysis/memory_maps/g2_esl2606_pool10000_compat_20260925.md`.
  G2 N=10001(0번 제외 10,000) 저장 호환 layout + 개인1200을 2606 고유 코드와 결합.
  G2의 고정전비5000 명령은 원 2606 명령으로 복원해 1600+200×장수(최대7=3000)를 유지.
  F4 used 32-bit 장부는 포함하지 않았다. 정확히 두 SHA만 지원하며 비분류 충돌 거부,
  복사본만 생성·정확한 원복 회귀 포함.
- 결과 폴더: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_esl2606_pool10000/20260925_185704/`.
  `MANIFEST.json`에 전체 경로·해시·검증 등급. 일반 후보 SHA
  `73977e34160caebdbaa7aedff6b50ed4d6a860c582ce74c3eb421829d3672387`,
  시작자리고정 `c29d34173dbc428a9dce88ba8c733ba03a18859121d684aebfcd14277efcb3e1`.
- 1단: `make doctor` 원본 검증 PASS, targeted 4 passed, `make check` **862 passed/591.59s**
  및 Ruff/compileall/mypy(10 files)/CONTEXT_PASS, `bash checks/safety.sh check` SAFETY_PASS.
  새 패처 단독 mypy `--follow-imports=skip` PASS. 일반/고정 variant의 변경 후 차이가
  정확히 기존 시작자리 4바이트뿐임을 테스트로 확인.
- 새 격리 Wine 기동(각각 별도 전체 게임 복사본·fresh prefix·빈 Xvfb): 둘 다
  `MENU_PS9_OBSERVED`, 캡처 `20260925_190224_g2_esl2606_pool10000_menu.png` 및
  `20260925_190426_g2_esl2606_fixedstart_pool10000_menu.png`(공유 temp/captures).
  raw `local/runtime/g2_esl2606_pool10000_smoke/20260925_190058_2789893_0/output/candidate_startup.json`,
  `local/runtime/g2_esl2606_fixedstart_pool10000_smoke/20260925_190311_2802973_0/output/candidate_startup.json`.
  둘 다 prefix residual `[]`, cleanup true; 다른 프로세스에 전역 kill 없음.
- **판정: EXPERIMENTAL / MENU BOOT ONLY.** 게임 내 1,200개 개인 개체 또는 공유 풀
  10,000개 근접을 이번 실행에서 만들지 않았다. 실제 생산/전투·CPU/메모리·저장/로드·LAN,
  특히 2606 고유 변경과 대용량 sidecar의 결합은 미검증. 기존 N=4001 후보의 24k/144k를
  이 두 새 후보의 합격 증거로 승격하지 않는다. 독립 2단·사용자 마일스톤 승인 없음.
