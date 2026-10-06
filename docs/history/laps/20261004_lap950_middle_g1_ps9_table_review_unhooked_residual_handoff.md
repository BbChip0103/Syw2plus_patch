# 2026-10-04 | lap 950 | G1 W70 lap949 census PS9/PS3 독립 검수 + 미후킹 잔여 측정 인계

- 실제 provider/model/effort / 지정 역할: middle(Claude Code `claude-opus-5-5`, high, Fast OFF), 진단·계획·확인. 게임·source·test·DLL·validator 변경0, 새 게임 실행0, commit0. `loop/.lap_counter` 950 읽기만.
- 가설 / 사용자 관찰: lap949의 PS9 표·PS3 재현·unknown index 측정은 raw로 재현되고, 기준1 완료에 남은 것은 GDI/P6 잔여 측정이다.
- 예상 PASS / FAIL 조건: PASS = 제품 helper 없는 재계산이 세 run 64 present 모두 JSON과 일치, PS3 ±0.5%p, unknown 사전 등록 기준 충족, source SHA = 기록. FAIL = 불일치·SHA 불일치·근거 충돌.
- 변경 파일 / source fingerprint / 커밋: 새 문서 `docs/work/active/G1_MIDDLE_W70_PS9_TABLE_ACCEPTANCE_UNHOOKED_RESIDUAL_HANDOFF_LAP950.md`, 이 기록, STATUS. uncommitted. source 7파일 SHA는 lap949 기록과 동일(카드 §1).
- 원본 SHA / 후보 SHA / 환경 / fixture: 보호 원본 EXE `b56986e0…a8ac` 재해시 MATCH. 세 run probe-result의 private EXE·fixture save006 `616b7997…0d064`·`source_unchanged`·`game_removed` true 확인. census-only 800×600. 8 player records는 활성8인 부하증명 아님.
- 실행 명령 / 로그: `.venv/bin/python temp/Syw2plus_patch/20261004_lap950_middle_review/recalc_lap950.py` → `recalc_lap950.json` SHA `f92d45acf6a4759e754dae050435b36f86dbd7ac8cf92feac2a2157220d6ed65`(스크립트 SHA `2805c1dd5ea485de05d2bc3b17a9d35512d6a7725c63efee7dfe2245c7f37e0a`). EXE import 표·`call [reg+0x44]` 패턴 정적 계수(read-only).
- 측정값 / 판정:
  - 재계산 불일치 0(세 run×64 present, header state 9/9/3), 재unknown 0, index top 합 ≤ unknown. PS9 r1=r2 block_copy 93.966%·rle_clip 6.034%·unknown0; block_copy 인자 단일 `(0,0,800,600,0x0531F2E8)`, rle_clip은 버튼 8개·커서 사각형 밖 0px. PS3 lap947 대비 최대 편차 dd_blt +0.081%p → 재현 PASS.
  - PS3 unknown 7,182 = index 0 상수 검정 **확정 수용**(사전 등록 기준 충족). → 기준1 "원천 그림 없음".
  - lap949 census 상태 선택 **PASS(partial)** (Lock 실패 주입 없음).
  - **새 한계:** block_copy·rect_fill은 `semantic_write`로 bbox 전체를 무조건 배정하고, map은 hook 시점에만 갱신된다 → PS9 unknown0은 구조적이고, hook 밖 writer(TextOutA 직접 call 49곳 등)는 직전 hook writer로 오귀속된다. 기준1 명시 잔여(GDI/P7) 비율은 현재 map으로 유도 불가 → UNKNOWN.
  - block_copy(src≠terrain cache) 분류: "원천 그림 없음" 아님 → **원천 이미지 전사, HD 후보(조건부)**; 현 미러 coverage 0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 lap 문서만 변경. 미검증: 미후킹 잔여 실측, block_copy 원천 버퍼 진위·P5 메뉴 미러, 기준2 coverage, D-2, 사용자 승인. G1 HOLD, ESCALATE 조건 없음.
- 다음 한 가지: work(Sonnet)가 카드 §4대로 opt-in shadow 비교(`unhooked_pixels`)와 TextOutA/GetDC 귀속을 새 파일에 구현하고 PS3 save006·PS9 fresh run으로 미후킹 잔여 비율을 공개한다.
