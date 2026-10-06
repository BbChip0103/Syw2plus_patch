# 2026-10-04 | lap925 | G1 W70 P5-T — observation tick 경계 확정 / P5-T 스크롤 뒤 재호출 비용 확인 / P5-T-R work 카드 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향·상위 계획) 역할, 일반 작업자.
  자동 폴백 아님. 게임 코드·하네스·validator 수정0, 게임 실행0, build0, subagent0, 커밋0. `loop/.lap_counter` 925 읽기만
  (러너 주입 문구의 lap=924보다 파일이 최신이다).
- 가설 / 사용자 관찰: lap924 middle이 lap923 B′1의 30-present 표본 중 DOWN 4·RIGHT 12가 observation 경계 뒤라며
  `HOLD_OBSERVATION_WINDOW_CONFLICT`로 승격했다. 07:14 운영자 지시는 "충돌 근거 확인·최소 경계 수리 확정만 하고 바로 work로 연결"이다.
  이 세션의 질문은 (1) 늦은 표본이 사실인가, (2) 경계를 무엇으로 정확히 긋는가, (3) 30개가 왜 모자랐는가다.
  사용자 상시 지시(2026-10-03 14:37 G1 자율 지속, 구현 우선, 묻지 말고 결정)를 적용했다.
- 예상 PASS / FAIL 조건: 판정 회차다. lap924와 다른 스크립트로 raw를 다시 셌다. 반증 기준은 "B′1의 늦은 표본이 epoch 가정 없는 상한으로 0개"
  또는 "30개 값·p50이 기록과 다름". 둘 다 일어나지 않았다(4/12, 값 일치). (3)은 이전 단계 raw와 비교해 P5-T에서만 간격이 벌어지는지로 갈랐다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `docs/work/active/G1_STRATEGY_W70_P5T_R_OBSERVATION_TICK_BOUND_LAP925.md`, 이 기록,
  `docs/history/20261004_lap925_prior_lap924_escalate_sol_archive.md`, `docs/history/20261004_{status,inbox,approvals}_lap925_precompaction.md`.
  갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`. `loop/ESCALATE_SOL` 제거(보존본과 `cmp` 일치 확인 뒤).
  제품/하네스/test/validator/golden/안전핀/원본/save/기존 raw·PNG 변경0. uncommitted. HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는
  provenance일 뿐이다. 읽은 source SHA256: `tools/g1_saved_scene_probe.py` `15b0e0f712c813171263072a746c8bc25050c89493316214fe47b985ec749434`,
  `tests/test_g1_saved_scene_probe.py` `e3c71fe3d7ee5659805709ff02d9763ee8fd9294ce7b3abc4edc56c83dea8f14`(둘 다 lap923 기록과 일치),
  `tools/inmm_stub/direct_draw_trace.c` `20b86b25ab08a4530948839886dd09c4a35ac379e087a590ffd4ef271f17b1f5`,
  `tools/inmm_stub/g1_state_snapshot.c` `6f40eee01cc21063a87e92d79afb361e35186f041dbefac885efbfb318407658`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 새 실행 없음. 보호 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 비합성 save006
  `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 재해시 MATCH(읽기만). 읽은 기존 증거는 save006 한 장면(일본)의
  candidate lane trace다. 8 player records는 활성 8인 부하 증명이 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap925_strategy_review/`.
  `.venv/bin/python recalculate.py`(경계·표본), `trend.py`(창 안 개수), `cadence.py`(단계별 간격), `attribution.py`(present당 counter 증가분),
  `windows.py`(C 창·스크롤 전후 재호출 시간).
  SHA256: `recalculate.py` `6188e63adb97c2d8d25c9c68c2dba04b98283ca7a7296108e74182cf120014e5`,
  `recalculation.json` `4c67bd2fcb8c8dc5a80b9c9e3be3bce3f5f4c161d21bf04068f58eaa29ed60b6`,
  `trend.py` `9b2df184614e3baae349619b66edfd2642b154eef8d2a743396810b0a489b6ae`, `trend.json` `e65a7f2796a2b711b080b2a81b1b1d594c2095ca5d362ca1eb8162c4f7c40dd7`,
  `cadence.py` `47a48c354f773bc8633d851e73e29a956b0d70a40e8a92b8e2b125e1a6465291`, `cadence.json` `b5b7d3dc948ae6ac27669b9589001ca61960e73f429f1ec655e73b9856f4f223`,
  `attribution.py` `ffa1fa6da5f928e6db3d83ae0330f8d7b1aa0257e87bdf7d8d3c58386744e91b`, `attribution.json` `5f8911ad9e247eb700b76686f8f4452ae273040f7e2611565683ec625ab74938`.
  `windows.py` `0084ee9df4085b98ae9e8894d3e01496bedb38ab9bd22c639348ad209c676831`, `windows.json` `456c12f64469ca9cf7040ced6fcd8fa27bb0e6668adf1c8e0882b0c35cee7aad`.
  `recalculate.py` 입력 27개 read-audit changed0. 나머지 스크립트는 읽기만 하며 trace SHA를 pair 기록과 대조한다.
  입력: lap923 final GREEN/B′1/B′2 pair(SHA `40e63385…b0e5`/`31cffdcb…f7cf`/`71077e43…ef4f`)·trace·snapshot 12개, lap923 C1·C2, lap907 pair1·2, lap915 pair2·B′1·B′2,
  lap920 GREEN·B′1·B′2·C1의 pair JSON과 candidate trace. trace SHA는 각 pair 기록과 일치했다.

## 측정값 / 판정

**lap924 HOLD 확인 — B′1의 DOWN 4·RIGHT 12 표본은 경계 뒤 / 경계는 sim tick으로 확정(`sim_tick` 한 필드) /
P5-T는 스크롤 뒤 present가 느려졌다 / 다음 work = P5-T-R / P5-T·G1 HOLD.**

1. 경계 뒤 표본: `ts_ms > keydown 수신 + (observation QPC − input QPC)/10000 + 16`인 표본이 B′1 DOWN 4·RIGHT 12, GREEN·B′2는 0.
   마지막 표본은 그 상한보다 311.5/699.7ms 뒤다(lap924와 일치). 경계 안은 B′1 26(16ms 여유를 두면 25)/18, GREEN 30/30, B′2 30/30.
2. 값: 30개 값과 p50은 기록과 일치(GREEN 406778/395928, B′1 406739/395963, B′2 406778/395924). trace·snapshot SHA MATCH, 표본·snapshot 같은 스레드.
3. 시계: trace `ts_ms`=`GetTickCount()`(1ms 분해능으로 관측), snapshot=QPC. keydown 수신 − input snapshot은 6회 15.4~24.4ms.
   trace는 줄마다 `WriteFile`+`FlushFileBuffers`라 snapshot 파일이 보이면 경계 앞 행은 이미 파일에 있다.
4. 기존 필드의 한계: epoch 가정 없이 얻는 것은 경계의 상한뿐이라 "뒤"만 증명된다. 파일 순서는 host 읽기 지연 때문에 못 쓴다. present 행에 sim tick이 없다.
5. 경계 계약(카드 §2): O1 `mirror2x_present`에 `sim_tick`(`0x008924B8`) 한 필드, O2 `sim_tick ≤ observation tick`만 표본·없으면 INVALID,
   O3 대기는 경계 앞 행이 보일 때까지만, O4 30 미만은 INCOMPLETE→HOLD, O5 raw 필드와 시계 대조값(판정 미사용), O6 `terrain_redraw` 경로 불변, O7 pre-arm 수리 보존.
6. 여유: 깨끗한 실행의 30번째 표본은 경계 47.5~113.0ms 앞이다. 창 안 present는 lap907 35~36개, lap923 GREEN·B′2 30~31개.
7. 간격: 전환 뒤 30 present가 lap907·915·920 16회 48.97~49.83ms/present, lap923 GREEN·B′2 56.0~58.5ms, B′1 70.0/126.6ms(간격 최대 99/713ms, RIGHT 창 3053ms).
8. 재호출 시간(present당): lap920 고정 4.0~4.9·DOWN 뒤 4.0~6.1·RIGHT 뒤 10.6~12.7ms. lap923 고정 6.3~6.8·DOWN 뒤 26.1~27.1·RIGHT 뒤 26.1~27.5ms.
   lap923 C1·C2는 4~9ms → 13~19ms로 올라 유지(lap920 C1 2.9~6.1ms). present 호출 자체(`elapsed_ms`)는 그대로다.
9. I/O: 파일 시각으로 C1~C3(06:30~06:35)·GREEN(06:39:08)은 prefix 보관(06:39:48 시작) 전에 끝났고 B′1(06:41:59)이 겹쳤다. 느려짐 자체는 GREEN에도 있다.
10. 단서: tinted 호출 94.7/present 중 identity cache miss 증가분 86.7, `tinted_clip` 호출 15.3 = clip replay mismatch 증가분 15.3(DOWN 뒤 13.3/13.2, RIGHT 뒤 13.9/13.7).
    원인은 미확정이다.
11. lap924 handoff와 다른 점: 경계를 QPC 시각이 아니라 sim tick으로 긋는다(observation tick과 같은 tick의 present는 표본). 수리 범위에 DLL 한 필드가 든다.
    하네스 수리만으로 끝내지 않고 스크롤 뒤 비용 수리(R3)와 PT-c(전환 뒤 30 present ≤ 52.0ms)를 P5-T 2단 수용 조건에 넣었다.

- PASS/FAIL/SKIP: 판정 완료(재계산 재현 가능). 경계 수리·`sim_tick`·비용 수리·실행은 work 몫이며 이 회차에서 실행되지 않았다.
  `make lint`·`make typecheck`·문서 연동 테스트·`checks/safety.sh check`·`checks/context_limits.py` 결과는 STATUS에 적는다.
  전체 `make check`와 새 runtime은 **SKIP** — 이 회차는 문서만 바꿨고, 다음 work가 source를 바꾼 뒤 전체 Fast를 돌린다.
  과거 full-test exit0(lap923 포함)은 현재 검증으로 쓰지 않는다.
- 승격 marker 처리: lap924 `loop/ESCALATE_SOL`(SHA256 `375ddf2827dc3d53d50086e3ae51767c25fd2d74355834c86e29d7c5e00a69b0`)을
  `docs/history/20261004_lap925_prior_lap924_escalate_sol_archive.md`에 byte-exact 보존하고 `cmp` 일치 확인 뒤 제거했다. 판정으로 해소했으며
  다음 회차를 work로 보낸다. 이 세션에는 승격 조건(미설명 필수 검사 실패·근거 충돌·마일스톤 경계)이 없다 — 재계산은 lap924 수치와 일치했고,
  P단계 전환은 마일스톤 경계가 아니다(lap858 판정).
- 문서 한도: STATUS 126줄(SHA256 `c8f281ded63201c0502e1203c1e3dc9b13e2c88e8ca3d9e91971d783907cf302`), INBOX 348줄
  (SHA256 `85ee0ec2260db754e700aeb0d073e5000b6425ae231572718e55ccb30c6cfb2a`), APPROVALS 250줄
  (SHA256 `f50876a6e0289f105bee5be314a4b8a7c2ebcd9e86812bff8f77d8aef3b386ec`) 전문을 `docs/history/20261004_{status,inbox,approvals}_lap925_precompaction.md`에
  byte-exact 보존한 뒤 압축했다. INBOX는 체크 완료 G5 운영자 항목 3개(lap747~749 처리), APPROVALS는 종결된 P4b B′ 계보 6항목(lap865~877)만 포인터로 바꿨다.
  상시 지시·미결·반려 삭제0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: tick 기준 창 안 개수(31/31/32/31, B′1 26/19)는 추정이고 실측은 `sim_tick` 뒤에 나온다.
  두 시계의 epoch가 같다는 것은 전제라서 판정에 쓰지 않았다. 느려진 원인과 C 창에서 재호출 시간이 오르는 계기는 모른다.
  lap915·920의 재호출 시간은 lap920 GREEN·B′2·C1만 쟀다. lap924가 stop으로 못 끝낸 p95 histogram·전체 시각·snapshot 전체 상태·stale 귀속은 다음 middle 몫이다.
  `rle_tinted_clip` covered 0·stale 감소 미입증·coverage 90% 미달·input-effect HOLD·GDI·두 번째 장면·최종 입력·D-2·G1 사용자 승인은 미검증이다.
  계획 승인·G1 마일스톤 아님. 제품 코드·실행 증거가 늘지 않은 회차가 lap924·925 연속 2회이므로 다음은 반드시 work 실행이다.
- 다음 한 가지: work가 `G1_STRATEGY_W70_P5T_R_OBSERVATION_TICK_BOUND_LAP925.md` §5를 수행한다 — 경계 테스트 RED → O1~O7 → fresh GREEN으로 PT-a·PT-b 확인 →
  스크롤 뒤 비용 수리(≤3회) → GREEN→B′1→B′2→C1~C3 → 기록 → `make check` 1회 → 새 middle.
