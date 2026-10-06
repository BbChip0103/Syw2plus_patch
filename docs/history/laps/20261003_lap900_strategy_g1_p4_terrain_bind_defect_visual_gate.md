# 2026-10-03 | lap900 | G1 W70 P4 — 화면 결손 귀속(렌더러) / 화면 정합 gate V / P4c work 카드 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향·상위 계획) 역할, 일반 작업자.
  자동 폴백 아님. 게임 코드·하네스·validator 수정0, 게임 실행0, build0, subagent0, 커밋0. `loop/.lap_counter` 900 읽기만.
- 가설 / 사용자 관찰: lap899 middle이 lap898 C 수치 3/3 PASS와 후보 PNG의 대면적 검은 마름모 격자를 함께 보고
  `HOLD_VISUAL_OUTPUT_ATTRIBUTION`으로 승격했다. 이 세션의 질문은 (1) 렌더러인가 캡처인가, (2) 기존 gate가 왜 놓쳤는가,
  (3) 다음 work의 범위와 합격식은 무엇인가다. 사용자 상시 지시(2026-10-03 14:37 G1 자율 지속, 구현 우선, 묻지 말고 결정)를 적용했다.
- 예상 PASS / FAIL 조건: 이 회차는 판정 회차다. 귀속을 기존 raw로 확정할 수 있으면 work 카드를 내고, 없으면 최소 귀속 probe 범위를 낸다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `docs/work/active/G1_STRATEGY_W70_P4C_TERRAIN_BIND_VISUAL_GATE_LAP900.md`,
  이 기록, `docs/history/20261003_lap900_prior_lap899_escalate_sol_archive.md`, `docs/history/20261003_approvals_lap900_precompaction.md`.
  갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`. `loop/ESCALATE_SOL` 제거(보존본과 SHA 일치 확인 뒤).
  제품/하네스/test/validator/golden/안전핀/원본/save/기존 raw·PNG 변경0. uncommitted. HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는 provenance일 뿐이다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 새 실행 없음. 읽은 기존 증거는 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`
  한 장면(후보는 EXE 무변경 + 진단 DLL `--hd-source scale2x`)의 것이다. 8 player records는 활성 8인 부하 증명이 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap900_strategy_review/`.
  `recalculate.py` SHA256 `9b2aa077792d4917e0e569be315468f2d0e06bac81dcc0c6fad5074b794c7c2b`,
  `recalculation.json` SHA256 `de3a82b6991ac6885c6da89b4eae25d8d4b3b196324ae532a0fe4028e32eb307`,
  확대 대조 PNG `20261003_lap900_c1_loaded_crop_baseline_top_candidate_bottom.png` SHA256 `d2f9970ac50446c5d5b8766a8d6667b2cac627f6c8e6bfb252610f50c221b08e`.
  기존 raw·PNG는 읽기만 했다.

## 측정값 / 판정

**귀속 `RENDERER(HD compose)` 확정 / P4·P4b 단계 `HOLD(화면 정합)`로 환원 / C 수용 없음 / 다음 work = P4c / G1 HOLD.**

1. 캡처 계열(월드 384000 표본의 후보 검정 수): 지형 미러 이전 40개 9417~9751(원본 9411~9427), P4 첫 실행 `lap858_p4_blitter_pair`부터
   44개 전부 191950~195864. 캡처 경로는 그 사이 바뀌지 않았다.
2. 프로세스 안 동일 프레임 수치: Scale2x는 2×2 블록에서 최대 2 subpixel만 바꾸므로
   `hd_mask_inside_diff_subpixels ≤ 2×(covered_pixels−stale_pixels)`가 정확히 성립해야 한다(V1). P3·P3c trace 5개(scale2x present 5297개)는
   위반 0, 안쪽 차이 비율 p50 0.062. P4 이후 trace 8개는 PS3 present 전부 위반(888/888, 889/889, 813/813, 972/972, 978/978, 894/894, 888/888, 890/890),
   비율 0.83~0.90, nearest 일치율 p50 0.34~0.45. X11 캡처·표시 경로와 무관한 present 직전 값이다.
3. 원인 후보 H1(정적 + 카운터 정합, 실행 미검증): `clipped=FALSE`로 불리는 지형 writer 3종(`0x468C30`·`0x468CC0`·`0x468E10`)의 identity frame을
   `g1_hd_asset_bind_identity_frame`이 scratch 버퍼 (0,0)에서 복사한다(`g1_mirror2x.c:1090~1092`, `g1_hd_asset.c:524~528`).
   C1 마지막 PS3 present에서 refreshes 376, RLE 346 + SHADE 29 = 375, inserts 716 = misses 340 + refreshes 376.
4. gate 공백: Scale2x validator는 안쪽 차이의 상한이 없고(`inside > 0`만), 캡처 검사는 전부 검정만 거른다. coverage는 블록 내용을 세지 않는다.
5. 신규 gate V(강화, 기존 조건 대체 아님): V1 위 정확식 위반 0 / V2 캡처 5 tag 각각 `후보 검정 − 원본 검정 ≤ 2000`(정상 15쌍 최대 652,
   결손 15쌍 최소 185,824) / V3 middle이 PNG를 직접 열어 본 내용을 판정문에 기록.
6. 과거 판정 효력: P2·P3·P3c 전부 유지. lap897 B'의 상태·입력 parity와 lap898 C의 수치는 측정 사실로 남기되, coverage·Scale2x validator
   항목과 C 수용은 근거로 쓰지 않는다. 수리된 소스로 B' 2 pair·C 3 pair를 다시 잰다. 과거 기록·raw는 고치지 않았다.

- PASS/FAIL/SKIP: 귀속 판정 완료(재계산 재현 가능). V1 RED는 이 세션 재계산으로만 확인했고 validator 구현·테스트는 work 몫이다.
  `make lint`·`make typecheck`·문서 연동 테스트·`checks/safety.sh check`·`checks/context_limits.py` 결과는 STATUS에 적는다.
  전체 `make check`와 새 runtime은 **SKIP** — 이 회차는 문서만 바꿨고, 다음 work가 source를 바꾼 뒤 전체 Fast를 돌린다.
  과거 full-test exit0은 현재 검증으로 쓰지 않는다.
- 승격 marker 처리: lap899 `loop/ESCALATE_SOL`(SHA256 `bee9dd5c8add722dcb0ae0b2f454a72758e1d7b4a0d4a424e243f4f6a4835aec`)을
  `docs/history/20261003_lap900_prior_lap899_escalate_sol_archive.md`에 byte-exact 보존하고 SHA 일치 확인 뒤 제거했다. 판정으로 해소했으며
  다음 회차를 work로 보낸다. 이 세션에는 사용자 지정 승격 조건(미설명 필수 검사 실패·근거 충돌·마일스톤 경계)이 없다.
  lap899의 근거 충돌은 위 1~4로 설명됐다.
- APPROVALS 한도 처리: 기록 전 250줄(소프트 한도)이라 전문 250줄·SHA256 `8f71aaf8c83a595e50fcfd949726eec5919de4672f9525257f91ee2a7b58e421`을
  `docs/history/20261003_approvals_lap900_precompaction.md`에 byte-exact 보존한 뒤, 체크 완료·종결 계보 3항목(lap855 P3c validator 누락,
  lap839 P2 negative lookup HOLD, lap832 P2 identity 검수 완료)을 포인터 한 줄로 대체했다. 미결·반려·사용자 지시는 건드리지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: H1은 고친 빌드로 확인되지 않았다. CLIP 계열(578회)에 다른 결함이 겹쳤을 수 있어
  카드 §4.4에 관찰 3건을 미검증으로 남겼다. V1은 필요조건이므로 V3 육안 검수를 필수로 뒀다. 수리 뒤 C 성능은 캐시 hit 양상이 달라져
  다시 재야 한다. D-1 PS3 census·HUD/tinted/GDI·전체 HD coverage ≥ 90%·두 번째 장면·G1 사용자 승인은 미검증이다.
  계획 승인·G1 마일스톤 아님. 제품 코드·실행 증거가 늘지 않은 회차가 lap899·900 연속 2회이므로 다음은 반드시 work 구현이다.
- 다음 한 가지: work가 P4c 카드 §4.1을 수행한다 — V1·V2 RED 확인 → 지형 비클립 writer 바인딩 수리 → fresh pair GREEN → B' 2 pair → C 3 pair.
