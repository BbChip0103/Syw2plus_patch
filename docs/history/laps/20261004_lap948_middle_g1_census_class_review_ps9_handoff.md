# 2026-10-04 | lap 948 | G1 W70 census 수리·writer 분류표 독립 검수 / PS9 두 번째 장면 인계

- 실제 provider/model/effort / 지정 역할: middle(Claude Code `claude-opus-5-5`, 최신 Opus 별칭, high), 진단·계획·확인. 게임 구현·실행 권한 없음.
- 가설 / 사용자 관찰: lap947 work가 고친 census 계측(present surface 포인터, blt captured 계수)과 save006 PS3 writer 분류표가 raw·source로 독립 재현되면 lap819 §3 기준1의 첫 장면 입력으로 수용할 수 있다.
- 예상 PASS / FAIL 조건: PASS = source/raw/log SHA MATCH, 제품 helper 없는 재계산이 64 present 전부 JSON과 일치, surface≠buffer, captured==calls, source 수리가 의도대로 읽힘. FAIL = 불일치·근거 충돌.
- 변경 파일 / source fingerprint / 커밋: 문서만, commit0. 새 카드 `docs/work/active/G1_MIDDLE_W70_CENSUS_CLASS_ACCEPTANCE_PS9_HANDOFF_LAP948.md`, 이 기록, STATUS. 게임·하네스·source·test·DLL·validator 변경0.
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 EXE `[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` read-only 재해시 MATCH. lap947 source SHA 5개(`g1_census.c/.h`·`direct_draw_trace.c`·`test_g1_census.py`·`_inmm.dll`) 재해시 = 기록. 진단 bridge DLL `f6dc569e…28b3`의 build json 입력 `g1_census.c` SHA 동일. 새 게임 실행0.
- 실행 명령 / 로그: `.venv/bin/python temp/Syw2plus_patch/20261004_lap948_middle_review/recalc_lap948.py`(공유 temp, 스크립트 SHA `a125c41a3d0ec517b24e8c5bb9721d037302a7e9e642f8d2d26bff118004f8fb`, 결과 `recalc_lap948.json` SHA `52b92e219626d054200b0aaecf92a417bd50177337fb3128321706e25ef070f9`). focused 검사는 STATUS에 보강.
- 측정값 / 판정:
  - 64 present map header·offset·writer_pixels·unknown 불일치 0, 9/9 install active, blt `64/64/0`, context dropped0, surface `0x01E75FD0`≠buffer `0x0233C7B0`(64/64).
  - 마지막 present 표 lap947과 동일: HD 후보 6 writer 472,619=98.46%, 원천 그림 없음 221=0.046%, unknown 7,160=1.49%. rle_tinted 6.795%는 반올림 6.80%(lap947 6.79는 절사 전사, 판정 영향 없음).
  - unknown 단조 감소 10,513→7,160(새 unknown 0), 전부 y512..599 HUD 띠, 인게임 PNG 4장에서 7,160px 전부 RGB(0,0,0). → "미배정 상수 검정" 잠정 분류(지지된 가설, 직접 증명 아님).
  - 판정: census 결함 수리 **PASS(partial)**(정적 회귀·정상 실행만, Lock 실패 주입 없음). save006 분류표 **기준1 첫 장면 입력으로 수용**. 기준1 완료·기준2 coverage·G1 제품 PASS 아님. G1 HOLD.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 두 번째 장면(PS9) 분류, GDI/P6 명시 잔여 비율, unknown 직접 증명, HD 후보 writer별 실제 미러 coverage, D-2, 사용자 승인 미완. `save000.dat` provenance 미확인으로 두 번째 장면 후보에서 제외. ESCALATE 조건 없음. 사용자 승인 없음.
- 다음 한 가지: work(Sonnet)가 lap948 카드 §3대로 census 상태 선택 env + probe `--census-state 9` + `unknown_index_top`을 구현하고 fresh PS9 메뉴 census와 PS3 재현 census를 실행한다.
