# 2026-10-03 | lap906 | G1 W70 P4c — 스크롤 뒤 우측 검은 쐐기 귀속(캐시 scratch clear 폭 800/832) / 수리 범위·V2q / P4c-W work 카드 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향·상위 계획) 역할, 일반 작업자.
  자동 폴백 아님. 게임 코드·하네스·validator 수정0, 게임 실행0, build0, subagent0, 커밋0. `loop/.lap_counter` 906 읽기만.
- 가설 / 사용자 관찰: lap905 middle이 B′ V2 4FAIL/3FAIL과 우측 4black 블록 2225/2164를 확인하고, "scratch clear는 폭 800, 캐시 compose는 폭 832"라는
  경로를 미검증 가설로 남긴 채 `HOLD_VISUAL_ATTRIBUTION_UNPROVEN`으로 승격했다. 이 세션의 질문은 (1) 그 경로가 실제 캡처의 검은 띠를 설명하는가,
  (2) 수리와 같은-present ROI 관측 중 무엇을 work에 넘길 것인가, (3) 최소 수리 범위와 합격식은 무엇인가다.
  사용자 상시 지시(2026-10-03 14:37 G1 자율 지속, 구현 우선, 묻지 말고 결정)를 적용했다.
- 예상 PASS / FAIL 조건: 판정 회차다. 사전 예측 — 경로가 맞다면 "원본 non-black 위, 후보 블록 네 subpixel 전부 검정"인 블록이 가로 64 이동 뒤에만,
  화면 x736..767(캐시 x800..831이 64px 밀린 자리)에만, 타일 변 기울기 2:1·32행 주기의 쐐기로 나타난다. 맞으면 수리 카드를, 아니면 ROI 관측 범위를 낸다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `docs/work/active/G1_STRATEGY_W70_P4C_W_CACHE_SCRATCH_WIDTH_LAP906.md`,
  이 기록, `docs/history/20261003_lap906_prior_lap905_escalate_sol_archive.md`, `docs/history/20261003_approvals_lap906_precompaction.md`.
  갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`. `loop/ESCALATE_SOL` 제거(보존본과 `cmp` 일치 확인 뒤).
  제품/하네스/test/validator/golden/안전핀/원본/save/기존 raw·PNG 변경0. uncommitted. HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는 provenance일 뿐이다.
  읽은 source SHA256: `g1_mirror2x.c` `d1052973aae53fe2e055ffcb5632e9368f0a84a746db459e15de040fb32de855`(lap904 기록·B′1 build 사본과 일치),
  `g1_hd_asset.c` `7833f32878c02944fbb02bc616192fe21d2860eb5f71781f16d74e69cd6feedf`,
  `g1_scratch_bounds.h` `779a63848975c15d361a20280fcf88b1592ae9e63f21fe38732b160f0c5e4670`,
  `g1_scale2x_core.h` `20a7583577c0fd1f0f5b1dc9e3e4f2e049ce032b38e84986e7d8fd11fb745466`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 새 실행 없음. 읽은 기존 증거는 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`
  한 장면(후보는 EXE 무변경 + 진단 DLL `--hd-source scale2x`)의 것이다. 8 player records는 활성 8인 부하 증명이 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap906_strategy_review/`.
  `.venv/bin/python 20261003_lap906_strategy_review/recalculate.py`.
  `recalculate.py` SHA256 `1424125459dbf662c257ce85596a8a242da06d19a35db2209d72964865230a69`,
  `recalculation.json` SHA256 `f1af6b0688a68f7eb889ef38763f6bdac0ed495e9604b99282b30d8b1308419f`.
  입력은 `captures/20261003_2047_lap904_p4cm_green_r4`, `20261003_lap904_p4bs_pair1`, `20261003_lap904_p4bs_pair2`,
  `captures/20261003_1945_lap901_p4c_green`, `_green_r2`, `captures/20261003_1955_lap901_p4c_origin_pair`의 원본·후보 PNG 60장과 pair-result 6개
  (읽기만, 계산 전후 SHA 변화 0, 저장 PNG SHA와 일치). `captures/lap854_p3c_gate1~3`은 `pair-result.json`이 없어 계산에서 빠졌다.

## 측정값 / 판정

**귀속 `RENDERER(캐시 대상 scratch clear 폭 800 → x800..831의 묵은 A==B를 compose가 읽음)` 확정 / 같은-present ROI 관측 회차 없음 /
수리 = W1 하나 / V2q 추가 / 다음 work = P4c-W / G1 HOLD.**

1. 소스 경로(정적, 이 세션이 직접 읽음): 사전 clear는 프레임 폭 800으로 영역을 구해 x≥800을 지우지 않는다(`g1_mirror2x.c:1024~1032`,
   helper는 빈 영역에도 TRUE라 전체 clear 분기 `:1033~1037`도 안 탄다). 캐시 compose는 폭 832로 `A==B`를 쓴 픽셀로 본다(`:548~558`).
   lookup은 mask 미기록 자리에도 블록을 주고(`g1_hd_asset.c:606~614`) 그 블록은 네 subpixel 모두 `0x00`이다(`g1_scale2x_core.h:27~43`).
   expected에는 실제 캐시 값이 들어가 present 값 검사와 V1 합계 상한을 통과한다(`:567`). 화면 전송은 x<800만 옮기므로(`:640~643`)
   왼쪽 64 이동(`0x432BD4`) 뒤에야 x736..767로 들어온다.
2. 기하 예측 대 실제(값은 `전체 / x736..767`):
   - GREEN r4(스크롤 없음) `0/0, 94/0, 636/0, 1348/0, 825/0`.
   - B′1 `120/0, 2434/2207, 2402/2225, 2708/2316, 2580/2261`. B′2 `308/0, 2179/2164, 2555/2288, 2950/2370, 2851/2330`.
   - lap901 3 pair(스크롤 없음) 15장 전체 43~1361, x736..767은 전부 0.
   - 가로 이동 없는 22장은 띠 0, RIGHT 뒤 8장은 2164~2370. 이웃 x768..799는 0~64, x720..735는 0~65. 띠 왼쪽 끝은 x=736.
   - B′2 selection 띠 2164블록 전부가 `y mod 32 ∈ [16,31]`, 행별 `206,208,213,209,202,191,178,169,147,125,99,82,62,41,24,8`.
     B′1은 2207 중 2194. 쐐기 안 행 폭은 x=736에 붙은 채 행마다 2px씩 준다(`22,22,23,21,19,…,3,1`).
   - lap905의 우측 80px 2225/2164와 일치(B′1 2207+18, B′2 2164+0).
3. 다른 설명 배제: 두 pair의 결정적 동일 분포와 캐시 폭 상수에 붙은 경계는 캡처 시점·입력 차이로 설명되지 않는다. 다시 그린 열(x768..799)은 0~64,
   상태 snapshot 5개는 두 lane 동일(lap905), 미러 이동은 연속 구간 복사라 쐐기를 만들지 않는다.
4. V2 공백: B′2 drag는 띠 2288블록이 있는 채 V2 초과 1863으로 PASS였다. V2s는 이 결함을 세지 않는다(97~131).
   **V2q(네 subpixel 전부 검정인 블록 ≤ 2000, 5 tag)**를 추가한다. 정상 22장 최대 1361, 결함 8장 최소 2179로 여유가 크지 않음을 카드에 적었다.
5. 수리 규칙 W1(clear와 compose가 한 정의의 프레임 폭 사용)·불변식 W2, work 순서(단위 RED → W1 → fresh scroll pair=B′ 1번째 → B′ 2번째 → C 3 pair),
   사전 예측 P-a~P-d와 반증 조건(수리 뒤 띠 ≥ 1500이면 mask-미기록 합성 카운터 1개)을 카드에 규범으로 적었다. V1·V2·V2s·V3·임계값 불변.
6. 같은 계열이지만 이번 수리에 넣지 않은 것: 비클립 bind 조건의 800 상한(`:1141`), 검증 함수의 800/600 상한, lookup의 mask 미확인.
   정독으로는 검정을 만들지 않는 coverage·방어 항목이라 D-1/coverage 단계로 미뤘다.
7. 입력 효과 UNKNOWN(selection·production·minimap, 두 lane 동일)은 pair 합격식 밖이며 PASS로 바꾸지 않았다. 스크롤 뒤 좌표 수리는 별도 work다.

- PASS/FAIL/SKIP: 귀속 판정 완료(재계산 재현 가능). 수리·V2q 구현·테스트는 work 몫이며 이 회차에서 실행되지 않았다.
  `make lint`·`make typecheck`·문서 연동 테스트·`checks/safety.sh check`·`checks/context_limits.py` 결과는 STATUS에 적는다.
  전체 `make check`와 새 runtime은 **SKIP** — 이 회차는 문서만 바꿨고, 다음 work가 source를 바꾼 뒤 전체 Fast를 돌린다.
  과거 full-test exit0(lap904 포함)은 현재 검증으로 쓰지 않는다.
- 승격 marker 처리: lap905 `loop/ESCALATE_SOL`(SHA256 `7a00401ec258813792aae4db1bfdcc7458e093292c845eeefac594b6285b1a38`)을
  `docs/history/20261003_lap906_prior_lap905_escalate_sol_archive.md`에 byte-exact 보존하고 `cmp` 일치 확인 뒤 제거했다. 판정으로 해소했으며
  다음 회차를 work로 보낸다. 이 세션에는 승격 조건(미설명 필수 검사 실패·근거 충돌·마일스톤 경계)이 없다. lap905의 "귀속 미증명"은 위 1~3으로 해소됐다.
- 문서 한도: APPROVALS 245줄 전문(SHA256 `7eb1be76a4131f50c546c6f663c93de2d07deaf92c1257a16eae36c924cd8ecd`)을
  `docs/history/20261003_approvals_lap906_precompaction.md`에 byte-exact 보존한 뒤 체크 완료 3항목(lap887·889·897)만 포인터로 바꿨다. 미결·반려 삭제0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 고친 빌드는 아직 없다. 프로세스 안 같은-호출 관측이 아니라 소스 정독과 캡처 기하의 일치로
  판정했다. 쐐기가 32행 주기의 아래 절반에만 생기는 이유(그리기 순서)와 블록 수의 정확한 모형은 유도하지 않았다. 스크롤 없는 캡처에도 띠 밖에
  네-검정 블록이 0~1361개 있고 원인은 분리하지 않았다(유닛·효과의 캡처 시점 차이로 보임). V2q 여유는 작다.
  B′/C 재측정·D-1 PS3 census·HUD/tinted/GDI·전체 HD coverage ≥ 90%·두 번째 장면·G1 사용자 승인은 미검증이다.
  계획 승인·G1 마일스톤 아님. 제품 코드·실행 증거가 늘지 않은 회차가 lap905·906 연속 2회이므로 다음은 반드시 work 구현이다.
- 다음 한 가지: work가 `G1_STRATEGY_W70_P4C_W_CACHE_SCRATCH_WIDTH_LAP906.md` §4.1을 수행한다 — 단위 RED(W2·V2q) → W1 수리 →
  fresh scroll pair GREEN(V1·V2·V2s·V2q, `selection.png` 우측 직접 확인) → B′ 2번째 → C 3 pair.
