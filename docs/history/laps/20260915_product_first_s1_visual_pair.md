# 2026-09-15 | G1 product-first original/candidate visual pair

- 변경: 원본 S1 load-button `(316,372)` 입력 수리, DxWrapper 2× 후보 S1 명령 추가, private DirectDraw module 확인, PS3 실제 이미지 캡처. 원본 EXE/save/기존 goldens/pins 수정 없음.
- 원본 fresh run `20260915_125411_1759192_0`: PS35→3, 8/8 save000 PlayerStruct 일치, PS3 PNG 800×600 SHA `a221cd1bd526d468cd0b5f25288255ef95698c53acf3bfa061e617b814f8ab0b`, cleanup PASS/residue0.
- 후보 fresh run `20260915_125500_1763562_0`: DxWrapper 2×, private `ddraw.dll` SHA `3bc7230d…62bd19`·syw2x 미로드, content 1600×1200, PS35→3, 8/8 save000 PlayerStruct 일치, PS3 PNG 1600×1200 SHA `7017b09ff7a725c3dd95f07ea5160d1b0f90f937bb294da627d5fe65568e11ba`, cleanup PASS/residue0/ini 원복.
- 비교: 원본 PNG를 Pillow nearest로 정확히 2× 후 동일 후보 PNG와 1,920,000픽셀 비교; identical pixel 99.21313%, 채널 MAE 0.46984/255, 화면 상단 HUD `(0,0,1600,120)` exact. 차이는 PS3 직후 2회 별도 run 사이 동적 화면 요소이며 원본 동일 구도를 부정하는 정적 오차로 단정하지 않는다. 두 이미지는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/`에 있다.
- 검증: 대상 `tests/test_s1_load_evidence.py` 53 passed, Ruff/mypy PASS. 후보 명령을 추가한 뒤 전체 Fast 431 passed/safety2 PASS; 이후 이미지·module gate 수정의 새 전체 Fast는 진행 대기.
- 판정: G1의 2× 원본 구성·save load는 FEASIBLE/실측 PASS. 선택/드래그/미니맵/메뉴/생산 입력·WM_CLOSE·장기 플레이/실제 원본과 대조하는 사람 확인은 아직 UNKNOWN이므로 G1 제품 완료가 아니다.
