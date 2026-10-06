# 2026-10-03 | lap911 | G1 W70 D-1 — present 버퍼 결합 판정(맵 64장은 메인 메뉴 화면) / P5 순서 확정 / D-1R work 카드 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향·상위 계획) 역할, 일반 작업자.
  자동 폴백 아님. 게임 코드·하네스·validator 수정0, 게임 실행0, build0, subagent0, 커밋0. `loop/.lap_counter` 911 읽기만
  (러너 주입 문구의 lap=910보다 파일이 최신이다).
- 가설 / 사용자 관찰: lap910 middle이 lap909 census 맵 64장의 버퍼 `0x0236BEA0`/stride 800이 PS9 표본에만 나오고 actual present source(폭 832)와
  결합이 없다는 것, gate가 `selected_buffer` 변이를 받아들인다는 것을 확인하고 `HOLD_PRESENT_BUFFER_IDENTITY`로 승격했다.
  이 세션의 질문은 (1) 그 맵이 실제로 무엇의 맵인가, (2) D-1이 정하려던 P5 순서를 고친 census 없이 정할 수 있는가,
  (3) 수리 범위와 합격식은 무엇인가다. 사용자 상시 지시(2026-10-03 14:37 G1 자율 지속, 구현 우선, 묻지 말고 결정)를 적용했다.
- 예상 PASS / FAIL 조건: 판정 회차다. 사전 예측(`recalculate.py` 머리에 적고 실행) — P1: 메뉴 맵이라면 payload 64개가 한 가지이고 그 버퍼가
  PS3 표본에 없으며 그림이 메뉴 배치다. P2: gate는 JSON과 header가 달라도 PASS한다. P3: 후보 PS3 유효 coverage가 80% 아래이고 HUD 행이 화면의
  20%라, HUD 표면 경로 없이는 어떤 순서로도 90%가 안 된다. 셋 다 성립했다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `docs/work/active/G1_STRATEGY_W70_D1R_PRESENT_BINDING_P5_ORDER_LAP911.md`
  (SHA256 `468076dd0199ea875b216247f1c3880d98603999987c5f8b6808725b9b5ed1cd`), 이 기록,
  `docs/history/20261003_lap911_prior_lap910_escalate_sol_archive.md`, `docs/history/20261003_inbox_lap911_precompaction.md`,
  `docs/history/20261003_approvals_lap911_precompaction.md`. 갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`.
  `loop/ESCALATE_SOL` 제거(보존본과 `cmp` 일치 확인 뒤). 제품/하네스/test/validator/golden/안전핀/원본/save/기존 raw·map·PNG 변경0. uncommitted.
  HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는 provenance일 뿐이다.
  읽은 source SHA256: `g1_census.c` `7b448e1953284682e70b7a2acf3d164632c2f93a5445488566757126a8677905`,
  `tools/g1_saved_scene_probe.py` `a5357765081d920fd7fb0fc8d7b1a6283bcbcb91884b33019201f567e30806ae`,
  `tests/test_g1_census.py` `9470677540bbf02c4d80ddff161d4079264c4b8b7532b65eca3cd9c9ce36c335`(셋 다 lap909 기록과 일치),
  `direct_draw_trace.c` `e0690d8c71a4ec30b808ebe86dae3ff68fb84275e1cfadb28b662a82a42dec75`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 새 실행 없음. 읽은 기존 증거는 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`
  한 장면의 것이다(census는 원본 lane, coverage는 EXE 무변경 + 진단 DLL `--hd-source scale2x` 후보 lane). 8 player records는 활성 8인 부하 증명이 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap911_strategy_review/`.
  `.venv/bin/python 20261003_lap911_strategy_review/recalculate.py`.
  `recalculate.py` SHA256 `5a3c8052f7571776acc06f012a8c7817b1f117123dd0a1f71d1d9e42a49eaf24`,
  `recalculation.json` SHA256 `e1d259c82761b58c1bc63f6140de1537f27b88aa317e251351605170594249e9`,
  `lap909_map_present1_writers.png` SHA256 `34d6138f39a4590d3d81c4d3459b07203db61d9fb24a18c331d968b1db6fc56a`.
  입력 37개: `20261003_lap909_d1_ps3_census_final/artifacts/census/`의 raw·map·context map·probe-result·`menu.png`·`selection.png`,
  `20261003_lap909_d1_ps3_census_r2`의 후보 trace, `captures/20261003_21{52,54,58}_…`·`22{02,06}_lap907_p4cw_{pair1,pair2,c1,c2,c3}`의 후보 trace 5개와
  원본 PNG 25장(읽기만, 계산 전후 SHA 변화 0). gate 반례용 변이 사본은 review 폴더 안 `selected_buffer_mutated.jsonl`이다.

## 측정값 / 판정

**lap910 HOLD 확인 — 맵 64장은 메인 메뉴(PS9) 화면의 맵 / lap909 화면 비율·전사 덮임 문장 불수용 / P5 순서 = P5-H → P5-T 확정 /
수리 B1~B5·gate G1~G4 / 다음 work = D-1R / G1 HOLD.**

1. 맵의 정체: 64 present의 map payload는 한 가지(SHA256 `e40210e0b188ca5a9cadca3dcc2e93dd66895a05a7570896ccc80c8aa66345c9`), 범주는
   `block_copy` 451,346 + `rle_clip` 28,654뿐이다. `rle_clip`은 y 488..577의 4×2 사각형 여덟 개다. 색으로 그린 맵과 같은 실행의 `menu.png`를
   나란히 직접 봤다. 메뉴 버튼 여덟 개의 자리와 같고, `selection.png`(월드 + 하단 HUD)와는 닮은 데가 없다.
2. 버퍼: 64개 전부 `selected_buffer=0x0236BEA0`·header stride 800·state 3, present source 폭 832. 그 버퍼의 primitive 표본 59개는 전부 PS9.
   PS3 표본은 `0x0223DC20`/832가 96개(`rle_tinted_clip`·`rect_fill`·`rect_border` 각 32), `0x020D0CD0`/800이 32개(`set_pixel`). lap910 수치와 일치한다.
3. gate: 원본 lane `PASS`, `selected_buffer`를 `0xDEADBEEF`로 바꾼 사본도 `PASS`. header와 JSON buffer는 원본에서 서로 같다
   (잘못 고른 버퍼를 둘 다 일관되게 적었을 뿐이다).
4. 소스 경로: 면적 최댓값 선택(`g1_census.c:507~519`), PS3 검사는 present만 거름(`:535~541`), census는 source 표면 포인터를 받지 않음
   (`direct_draw_trace.c:1349`). gate는 binary header를 읽지 않음(`tools/g1_saved_scene_probe.py:3610~3656`).
5. PS3 표본에서 보인 구성(수용): present `BltFast(0x01E75F60 ← 0x01E758F8 832×600)` caller `0x00469379` 4개, HUD
   `BltFast(0x01E758F8 ← 0x01E757C8 800×203)` caller `0x0041C60C` 5개. HUD 패널은 프리미티브 밖의 writer이며 census 9 범주에 없다.
6. P5 순서 근거: 후보 PS3 유효 coverage `(covered − stale)/480000` p50은 B′1 0.6920(981 present)·B′2 0.6920(974)·C1 0.6923(904)·C2 0.6923(903)·
   C3 0.6923(899)·lap909 r2 0.6908(498). 미충족 147,675.5~148,395, stale p50 74,116~80,586. HUD 행(y≥480)이 96,000(20%)이라 월드 384,000을 전부
   덮어도 80%다. HUD 행을 전부 더해도 89.2%다. 그래서 P5-H(HUD 패널 표면)를 먼저, P5-T(tinted RLE 2종)를 다음에 한다. 둘 다 필요하다.
7. D-1의 역할: 순서 결정 기능은 6으로 끝낸다. D-1R은 HUD 패널 표면의 구성(P5-H 설계 입력)과 W70 §3.1 분류표 비율을 낸다.
8. 수리 규칙(카드 §3): B1 present source를 읽기 전용으로 잠가 얻은 포인터·pitch와 같은 버퍼의 맵만 사용(추정 선택 삭제), B2 `program_state`별 세대,
   B3 JSON·header 동일 필드, B4 DD 표면 blt를 범주 10으로(앞뒤 바이트 비교), B5 버퍼 요약·`calls_ps3`·slot drop 수. gate G1~G4는 강화이며
   기존 조건을 지우지 않는다. 사전 예측 P-a~P-f와 반증 조건(payload 64장 동일이면 HOLD, 월드 범주 9가 0이면 전사 인자 표본 추가)을 카드에 적었다.
9. lap910 handoff와 다른 점: 2번(전사→후속 block_copy 순서 관측)은 열지 않는다(메뉴 맵에서 나온 의문). 범주 10과 패널 표면 버퍼 요약을 더했다.
   "D-1 뒤 middle이 P5 순서를 정한다"는 이 카드 §2로 대체했다.
10. 순환 방지: D-1R이 다시 막히면 strategy로 올리지 않고 다음 work가 P5-T를 먼저 한다(카드 §5). 계측기의 수리 대상이 분명한 결함은 근거 충돌이
    아니므로 middle이 work로 직접 돌린다(카드 §6).

- PASS/FAIL/SKIP: 판정 완료(재계산 재현 가능). 수리·gate 구현·census 재실행은 work 몫이며 이 회차에서 실행되지 않았다.
  `make lint`·`make typecheck`·문서 연동 테스트·`checks/safety.sh check`·`checks/context_limits.py` 결과는 STATUS에 적는다.
  전체 `make check`와 새 runtime은 **SKIP** — 이 회차는 문서만 바꿨고, 다음 work가 source를 바꾼 뒤 전체 Fast를 돌린다.
  과거 full-test exit0(lap909 포함)은 현재 검증으로 쓰지 않는다.
- 승격 marker 처리: lap910 `loop/ESCALATE_SOL`(SHA256 `3599bdc094df28630ab6319a21f2c5ed61f1cfde4a8c6ae337cc3b105376e614`)을
  `docs/history/20261003_lap911_prior_lap910_escalate_sol_archive.md`에 byte-exact 보존하고 `cmp` 일치 확인 뒤 제거했다. 판정으로 해소했으며
  다음 회차를 work로 보낸다. 이 세션에는 승격 조건(미설명 필수 검사 실패·근거 충돌·마일스톤 경계)이 없다 — 재계산은 lap910과 일치했고
  P단계 전환은 마일스톤 경계가 아니다(lap858 판정).
- 문서 한도: INBOX 345줄 전문(SHA256 `03363aa81a0ae8c277e5b17dae24aaf3b7e6bf7bdcc5f5846d27aea14805ef2c`)과 APPROVALS 250줄 전문
  (SHA256 `74589f54175c57e539e198a60cc7b5f4206744abb5958c3923d5a1671551d931`)을 각각 `docs/history/20261003_inbox_lap911_precompaction.md`·
  `docs/history/20261003_approvals_lap911_precompaction.md`에 byte-exact 보존한 뒤, INBOX는 체크 완료 2항목(lap851·853 strategy 판정),
  APPROVALS는 lap841 수용으로 종결된 P2 HOLD 3항목(lap833·835·837)만 포인터로 바꿨다. 상시 지시·미결·반려 삭제0.
  APPROVALS에 빠져 있던 lap910 middle 색인 한 줄을 더했다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 고친 census는 아직 없다. 6의 20%는 화면 배치 상한이지 HUD 패널이 실제로 쓰는 픽셀 수가
  아니다. tinted RLE의 PS3 월드 면적은 모른다(`rle_tinted` 표본은 PS35에서 소진). `set_pixel` 버퍼 `0x020D0CD0`이 패널 표면이라는 것은 가설이다.
  B4의 추가 Lock이 원본 lane의 타이밍에 주는 영향은 재지 않았다(후보 lane은 present마다 같은 Lock을 하고도 상태 parity PASS였다).
  원본 PNG의 스크롤 전후 정적 비율(월드 0.205, HUD 행 0.70~0.71)은 경계가 선명하지 않아 근거로 쓰지 않았다.
  D-1R·P5-H·P5-T·D-2 스크롤 성능·최종 입력·전체 HD coverage ≥ 90%·두 번째 장면·G1 사용자 승인은 미검증이다.
  계획 승인·G1 마일스톤 아님. 제품 코드·실행 증거가 늘지 않은 회차가 lap910·911 연속 2회이므로 다음은 반드시 work 실행이다.
- 다음 한 가지: work가 `G1_STRATEGY_W70_D1R_PRESENT_BINDING_P5_ORDER_LAP911.md` §4.1을 수행한다 — 단위 RED(선택·세대·gate) → B1~B5 수리 →
  원본 census-only fresh 실행 → 분모 셋의 범주 표와 패널 표면 버퍼 요약, 맵 그림을 PS3 PNG와 나란히 확인.
