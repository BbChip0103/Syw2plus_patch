# G4 자유대전 난이도 selector 부재 재검증 (2026-09-16)

사용자가 말한 "컴퓨터 난이도 개선"을 Easy/Normal/Hard 값 패치로 오해하지 않도록 원본
바이너리와 데이터에서 직접 재검증했다.

- 원본 EXE SHA `b56986e0…8ac` pin PASS.
- `FUN_004165C0`은 `DAT_006695A4` 0..4와 frame budget을 쓰는 게임 속도 함수다.
- 자유대전 commit `0x004B763C..0x004B76AE`의 WORD 목적지는 정확히
  `632D54, 632D46, 632D44, 632D4A, 632D48, 632D4C, 632D42` 일곱 개다.
- 별도 AI 난이도 write는 없다.
- 한국어 registry 네 개에 자원/맵/지형/모드/게임속도 label은 있지만
  `난이도/쉬움/어려움`은 없다.

판정은 `NO_FREE_BATTLE_DIFFICULTY_SELECTOR`다. 따라서 G4는 난이도 숫자를 찾아 배율을
바꾸는 작업이 아니라, 동일 fixture에서 생산·경제·이동·공격·방어 전략 자체를 개선하는
작업으로 정의한다.

- 도구: `tools/g4_difficulty_absence.py`
- 테스트: `tests/test_g4_difficulty_absence.py` 2 PASS.
- evidence: `analysis/g4_difficulty_absence.json`
- evidence SHA: `1c383322ac56683bd5addad4f18e5dcbe646ab14763bccbf74ff5cbb145e3b39`.
