# 2026-10-03 | lap903 | G1 W70 P4c — 타일 경계 검은 격자 귀속(write mask 누락) / 수리 범위·V2s / P4c-M work 카드 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향·상위 계획) 역할, 일반 작업자.
  자동 폴백 아님. 게임 코드·하네스·validator 수정0, 게임 실행0, build0, subagent0, 커밋0. `loop/.lap_counter` 903 읽기만.
- 가설 / 사용자 관찰: lap902 middle이 V1 위반0·V2 4FAIL·V3 HOLD와 함께 "미기록 0이 Scale2x로 들어온다"는 경로를 유력 가설로 남기고
  `HOLD_SEAM_ATTRIBUTION_UNPROVEN`으로 승격했다. 이 세션의 질문은 (1) 그 경로가 실제 캡처의 격자를 설명하는가, (2) 같은-call 관측을
  선행 조건으로 둘 것인가, (3) 최소 수리 범위와 합격식은 무엇인가다. 사용자 상시 지시(2026-10-03 14:37 G1 자율 지속, 구현 우선, 묻지 말고 결정)를 적용했다.
- 예상 PASS / FAIL 조건: 판정 회차다. 사전 예측 — 경로가 맞다면 "원본 non-black 위, 블록당 검정 1개"인 블록이 TL·BR은 `x+2y`, TR·BL은
  `x−2y`의 한 잔여류에 몰리고 지형 미러 이전 캡처에는 그런 집중이 없다. 맞으면 수리 카드를 내고, 아니면 같은-call 관측 범위를 낸다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `docs/work/active/G1_STRATEGY_W70_P4C_M_WRITE_MASK_SEAM_LAP903.md`,
  이 기록, `docs/history/20261003_lap903_prior_lap902_escalate_sol_archive.md`. 갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`,
  `docs/feedback/APPROVALS.md`. `loop/ESCALATE_SOL` 제거(보존본과 SHA 일치 확인 뒤). 제품/하네스/test/validator/golden/안전핀/원본/save/
  기존 raw·PNG 변경0. uncommitted. HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는 provenance일 뿐이다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 새 실행 없음. 읽은 기존 증거는 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`
  한 장면(후보는 EXE 무변경 + 진단 DLL `--hd-source scale2x`)의 것이다. 8 player records는 활성 8인 부하 증명이 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap903_strategy_review/`.
  `.venv/bin/python 20261003_lap903_strategy_review/recalculate.py`(11.6초).
  `recalculate.py` SHA256 `049a41b128cbd1a73aa2be3e966b5e36124fb82a503b602d872450b61b7883b0`,
  `recalculation.json` SHA256 `2bfdfb259ad4460d28808a41f6194af19bbd6c6956f2f9a94bc0a166692ce378`.
  입력은 `captures/20261003_1945_lap901_p4c_green`, `_green_r2`, `20261003_1955_lap901_p4c_origin_pair`, `captures/lap854_p3c_gate1~3`의
  원본·후보 PNG 60장(읽기만, 계산 전후 SHA 변화 0)과 origin pair 후보 `trace_raw.jsonl`의 마지막 scale2x present.

## 측정값 / 판정

**귀속 `RENDERER(write mask 누락 → Scale2x)` 확정 / 같은-call 관측 회차 없음 / 수리 범위 = 두 바인딩 경로 / V2s 추가 / 다음 work = P4c-M / G1 HOLD.**

1. 소스 경로(정적, 이 세션이 직접 읽음): scratch A/B에는 mask가 있으나(`g1_mirror2x.c:1015~1044`) bind가 A 값만 저장하고
   (`:1056~1097`, `g1_hd_asset.c:524~529`), `build_scale2x`가 미기록 0을 이웃 색으로 비교하며(`:391~409`), 합성은 중심 픽셀만 확인한다
   (`g1_mirror2x.c:546~555`). 마름모 변의 픽셀은 바깥을 향한 subpixel 하나가 0이 된다.
2. 기하 예측 대 실제(5 tag × 3 pair, 월드 384000 블록): P4c 15쌍의 단일 검정 블록 18,882~20,056개, 예측 축 mod 64 인접 2칸 점유율
   0.956~0.974(균등 0.031), 반대 축 0.063~0.068. 지형 미러 이전 15쌍은 476~614개, 점유율 0.07~0.16.
   origin loaded TL 4566 중 4370이 `(x+2y) mod 64 = 31`, TR 4621 중 4425가 `(x−2y) mod 64 = 32`. 위치별 수 4566/4621/4867/4828.
3. 수량: histogram `355689/18884/0/59/9368`로 추가분이 전부 "1개" 칸, 2개 블록 0. V2(TL만 계수) 초과 4.4k~4.9k는 TL 수와 같은 양.
   돌바닥 ROI 잔차 1367은 15쌍 동일, 이전 15쌍은 0~1. lap902 수치(V2·ROI·histogram)와 전부 일치.
4. 클립 경로: origin 마지막 present 누적 RLE 346·SHADE 29·CLIP 173·CLIP_SHADE 356·CHECKER 0. dispatcher `0x435400`이 viewport에 걸친
   같은 타일을 CLIP 계열로 보낸다. 그 identity frame은 0 채움 버퍼 1회 replay라 mask를 만들 수 없다 → 두 번째 replay 필요.
5. V2 공백: origin minimap은 원본 검정 14042(다른 tag 9413~9937) 때문에 초과 634로 PASS했으나 단일 검정 블록은 19,714개다. r2의 742도 같다.
6. 수리 규칙 M1~M5와 V2s(단일 검정 블록 ≤ 2000, 5 tag)를 카드에 규범으로 적었다. V1·V2·V3·임계값 불변.
7. lap902가 지적한 저장 aggregate `BLOCKED` 대 현재 `FAIL` 차이는 둘 다 non-PASS이며 과거 raw는 고치지 않는다. 현재 함수의 FAIL 집계·JSON 왕복을
   work가 회귀로 고정한다(카드 §4.1).

- PASS/FAIL/SKIP: 귀속 판정 완료(재계산 재현 가능). 수리·V2s 구현·테스트는 work 몫이며 이 회차에서 실행되지 않았다.
  `make lint`·`make typecheck`·문서 연동 테스트·`checks/safety.sh check`·`checks/context_limits.py` 결과는 STATUS에 적는다.
  전체 `make check`와 새 runtime은 **SKIP** — 이 회차는 문서만 바꿨고, 다음 work가 source를 바꾼 뒤 전체 Fast를 돌린다.
  과거 full-test exit0은 현재 검증으로 쓰지 않는다.
- 승격 marker 처리: lap902 `loop/ESCALATE_SOL`(SHA256 `adf548cffa36f8ec5c9dc9a2dfb6e6e6faab1561d7a274dd0336fc18cddc743a`)을
  `docs/history/20261003_lap903_prior_lap902_escalate_sol_archive.md`에 byte-exact 보존하고 `cmp` 일치 확인 뒤 제거했다. 판정으로 해소했으며
  다음 회차를 work로 보낸다. 이 세션에는 승격 조건(미설명 필수 검사 실패·근거 충돌·마일스톤 경계)이 없다. lap902의 "귀속 미증명"은 위 1~4로 해소됐다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 고친 빌드는 아직 없다. 프로세스 안 같은-call 관측이 아니라 캡처 기하와 소스의 일치로
  판정했으므로, 수리 뒤 격자가 남으면(카드 §4.2 반증) 그때 타일 한 장 dump로 가른다. 스프라이트 윤곽에도 같은 유입이 있을 수 있고 규모는
  미분리다(이전 15쌍 단일 블록 476~614 안). mask 규칙은 전 writer에 같게 적용되므로 스프라이트 윤곽 subpixel이 바뀌며 C 성능은 다시 잰다.
  B'/C 재측정·D-1 PS3 census·HUD/tinted/GDI·전체 HD coverage ≥ 90%·두 번째 장면·G1 사용자 승인은 미검증이다.
  계획 승인·G1 마일스톤 아님. 제품 코드·실행 증거가 늘지 않은 회차가 lap902·903 연속 2회이므로 다음은 반드시 work 구현이다.
- 다음 한 가지: work가 `G1_STRATEGY_W70_P4C_M_WRITE_MASK_SEAM_LAP903.md` §4.1을 수행한다 — 단위 RED → mask 보존 수리(M1~M5) →
  fresh pair GREEN(V1·V2·V2s, PNG 직접 확인) → B' 2 pair → C 3 pair.
