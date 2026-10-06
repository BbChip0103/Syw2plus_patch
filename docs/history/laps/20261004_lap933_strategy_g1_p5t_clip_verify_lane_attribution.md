# 2026-10-04 | lap933 | G1 W70 P5-T — timer 범위 승격 해소 / 클립 바인딩 두 번째 검증 lane 불일치 귀속 / P5-T-V work 카드 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향·상위 계획) 역할, 일반 작업자.
  자동 폴백 아님. 게임 코드·하네스·validator 수정0, 게임 실행0, build0, subagent0, 커밋0. `loop/.lap_counter` 933 읽기만
  (러너 주입 문구의 lap=932보다 파일이 최신이다).
- 가설 / 사용자 관찰: lap931·932 middle이 "clipped mask 할당이 parent clip timer에서 빠진다"며 `HOLD_SCOPE_CONTRACT`로 승격했고,
  11:18 운영자 메모는 strategy가 timer 결함과 capacity 재사용 계약을 판정하고 G1 계속 여부를 밝히라고 했다. 이 세션의 질문은
  (1) timer 결함이 사실인가, (2) capacity 재사용이 PT-c를 회복시킬 수리인가, (3) PT-d 하한 미달은 무엇을 뜻하는가다.
  사용자 상시 지시(2026-10-03 14:37 G1 자율 지속, 구현 우선, 묻지 말고 결정)를 적용했다.
- 예상 PASS / FAIL 조건: 판정 회차다. (1)의 반증은 "1348 할당이 parent 구간 안에 있다" — 아니었다(1343에서 0, 1351에서 재시작).
  (2)는 "replay 횟수가 같은 두 창에서 fill 단가가 같으면 재사용으로 얻을 것이 없다"로 갈랐다 — 단가는 28.5~32.2배 달랐다.
  그런데 replay 자체가 present당 147~149회 반복되는 이유를 보다가 두 번째 검증의 lane 불일치를 찾았다. 반증 기준 "마지막 mismatch 값이 `[0,255]`가 아닌 실행이 있다",
  "replay ÷ mismatch가 2에서 멀다"는 9회에서 일어나지 않았다. (3)은 "고정 카메라에서 tinted covered가 변하면 창 지표로 쓸 수 있다" — 8회 전부 변화점 0이었다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `docs/work/active/G1_STRATEGY_W70_P5T_V_CLIP_VERIFY_LANE_LAP933.md`, 이 기록,
  `docs/history/20261004_lap933_prior_lap932_escalate_sol_byte_exact.txt`(SHA256 `047674d7b8a496f0f566977b9c70846e90a886dacd23896e86c8cd1860665895`),
  `docs/history/20261004_inbox_lap933_precompaction.md`(342줄, SHA256 `a89aa567951c03017fedce91ba9778885479dcf2f0b5fc3a80ad70cd7df68e16`).
  갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`(종결된 lap742 처리 11줄을 포인터 2줄로, 판정 항목 추가), `docs/feedback/APPROVALS.md`.
  `loop/ESCALATE_SOL` 제거(보존본과 `cmp` 일치 확인 뒤). 제품/하네스/test/validator/golden/안전핀/원본/save/기존 raw·PNG 변경0. uncommitted.
  HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는 provenance일 뿐이다. 읽은 source SHA256(lap930·932 기록과 일치):
  `tools/inmm_stub/g1_mirror2x.c` `f27302c1633a00e911c668a2201bdb3d5d41380c61f6e40847f468d5f606fec1`,
  `tools/inmm_stub/g1_hd_asset.c` `7833f32878c02944fbb02bc616192fe21d2860eb5f71781f16d74e69cd6feedf`,
  `tools/inmm_stub/direct_draw_trace.c` `8b61823e8a548ce6ac8cfdf514b19d78f389f53861ded3ba455b92c53b11b0f8`,
  `tools/inmm_stub/g1_perf_sections.h` `1c912f1b2b09803fc9dc8fc1c97fb4e52299fde9cdd57d30e15e0799120bce2f`,
  `tests/test_g1_mirror2x.py` `0fdabc3610a1e8c63f02c88c67b814d536560327d6f9a6f5fbfd8318e210bf32`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 새 실행 없음. 읽은 기존 증거는 save006 한 장면(비합성 fixture)의 candidate lane trace다.
  보호 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`·save006
  `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`는 종료 검사의 doctor로 확인한다(결과는 STATUS). 8 player records는 활성 8인 부하 증명이 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap933_strategy_review/`.
  `python3 recalc.py`(창별 counter 증가분·PT-d), `recalc_windows.py`(창별 fill·alloc 단가), `recalc_mismatch.py <실행 디렉터리…>`(mismatch 구조·창 안 정확한 증가분).
  세 스크립트 모두 trace SHA를 probe-result와 대조한 뒤 읽기만 한다. SHA256:
  `recalc.py` `2cd6ba2ae3b218641940f1f55ce135ca67281a3473b2981a1b78cec84ae5c313`, `recalculation.json` `2429d6ab6302bbf7ab15e731c8f6d1a7f6e48a6ee0aa822aeb1f7d7c2962b576`,
  `recalc_windows.py` `9f996eef24c28fc899773d84bf4eecc94a554124d987b756abea2f5be54b5f64`, `recalculation_windows.json` `d098146414982fdb5a9097f1a2599d5673d6f3baba44f052dbbb081155836a34`,
  `recalc_mismatch.py` `72ad71d2a54e9cdd62ec3221026f2136c6338c8e904444a6bb0396b79ac2204a`,
  `recalculation_mismatch_lap930.json` `d4dbed48b0c6b9285e2f365f41f6d5cf41627d88f94dbd1fb60ecb0ad1d25d24`(lap930 6회),
  `recalculation_mismatch_older.json` `4992624e8a4562e1f31cafadc04203aeac6627ee6fc00e25fc61f2a080847d84`(lap923 final 3회).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - timer 범위: lap931·932 판독 **확인**. `clip − 세 bucket` 잔차 승인 보류 유지. 아래 수치는 helper 자체 timer와 호출 counter라 이 결함의 영향을 받지 않는다.
  - mismatch 구조(9회): replay ÷ mismatch 2.0080~2.0104, 마지막 mismatch 값 전부 `[0, 255]`(8회 `0x466D50` 32×32 (93,553), C3 `0x466540` 76×98 (666,366)).
    고정 late20 present당 클립 호출 82.35·mismatch 74.1·replay 148.7. writer별 나머지 = `tinted_clip` 호출 수(8회 정확, C3 10 이내).
    코드: 첫 검증 `scratch_a` 대 `unclipped`(00 lane), 두 번째 `scratch_a` 대 `unclipped_ff`(lane 섞임, `g1_mirror2x.c:1381~1383`). **귀속: 렌더러 결함(코드 판독 + raw 서명), 고친 빌드 미실행.**
  - 창별 단가(진단 stosl / stosb): fill 고정 4.90 / 4.57µs, DOWN 뒤 139.8 / 146.7µs, RIGHT 뒤 147.0 / 147.1µs(호출당 499,200바이트 동일).
    alloc·free 0.155 / 0.134 → 9.30~9.81µs. coarse 재호출 고정 0.4~1.75, 스크롤 뒤 19.1~22.7ms/present. 새 페이지 첫 쓰기는 크기가 맞는 **가설**(직접 측정 없음).
  - PT-d: tinted covered는 "처음 덮인 픽셀" 누적(`g1_mirror2x.c:601~602`, `1924~1925`). PS3 첫 present 값 lap930 11524 / 9569 / 9314 / 10589 / 12714,
    lap923 final 12544 / 11439 / 12969, 스크롤 전 변화점 8회 전부 0. 창 안 증가분 DOWN 3741·RIGHT 129(lap930 5회 동일). **하한 11439 폐기 → PT-d′.**
    lap928 B′1 9229·lap930 B′1 9569·B′2 9314는 "지표 무효"이며 PASS 아님.
  - 판정: **P5-T HOLD·G1 HOLD 유지, G1 계속.** lap931 §3 capacity 재사용은 조건부 2순위(V5). 임계값·미러 범위·full sentinel fill·validator 완화 0.
  - SKIP: 전체 `make check`·새 runtime(문서만 변경, 다음 work가 source 변경 뒤 실행). lap930 Fast 1473 PASS는 과거 증거다.
  - UNKNOWN: V1 뒤 실제 mismatch·PT-c·coverage, tinted writer의 대상 픽셀 의존 여부, 스크롤 뒤 단가 상승의 계기.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: V1이 통하면 지금까지 nearest로 남던 클립 스프라이트가 HD로 그려져 화면 정합 gate가 새 픽셀을 본다
  (FAIL이 나면 숨기지 않는다). identity cache key·pixel 수가 늘 수 있다. 이 판정은 strategy 범위 판정이며 2단 middle 수용·3단 사용자 승인이 아니다.
  lap931~933은 제품·실행 증거가 늘지 않은 연속 3회다 — 다음은 반드시 work다.
- 다음 한 가지: work **P5-T-V** — 카드 §5. 회귀 RED → V1(두 번째 검증 FF lane)·V2(parent timer 경계) → fresh GREEN으로 §3 예측 확인 →
  조건이 서면 V5 → GREEN → B′ 연속 2 → C1~C3 → Fast → 새 middle.
