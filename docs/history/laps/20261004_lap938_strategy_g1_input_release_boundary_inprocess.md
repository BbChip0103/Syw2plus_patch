# 2026-10-04 | lap938 | G1 W70 입력 캡처 — post-release present 승격 해소 / 게임 프로세스 안 release 행으로 경계 확정 / work 카드 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향·상위 계획) 역할, 일반 작업자.
  자동 폴백 아님. 게임 코드·하네스·test·validator 수정0, 게임 실행0, build0, subagent0, 커밋0. `loop/.lap_counter` 938 읽기만
  (러너 주입 문구의 lap=937보다 파일이 최신이다).
- 가설 / 사용자 관찰: lap937 ordinary middle이 "candidate의 seq1052/1056이 button-up 뒤라는 증명이 없고 binding이 present `UNKNOWN`도 통과시킨다"며
  `HOLD_POST_RELEASE_PRESENT_UNPROVEN`으로 승격했다. 13:30 운영자 메모는 strategy가 그 결함과 반례만 좁게 확인하고 work 최소수리 계약을 확정하라고 했다.
  이 세션의 질문은 (1) 두 source 결함이 사실인가, (2) r3의 두 present는 실제로 release 앞인가 뒤인가, (3) lap937이 낸 경계(주입 반환 뒤 호스트가 읽은 seq)가
  충분한가다. 사용자 상시 지시(2026-10-03 14:37 G1 자율 지속, 구현 우선, 묻지 말고 결정)를 적용했다.
- 예상 PASS / FAIL 조건: 판정 회차다. (1)의 반증은 "caller가 주입 뒤 값을 넘긴다" 또는 "binding이 present 상태를 본다" — 둘 다 아니었다.
  (2)는 같은 프로세스 시계로 쓴 release 행이 있으면 갈린다 — 있었고, 두 present는 그보다 88ms·39ms 앞이었다.
  (3)의 반증은 "호스트 반환 시점이 게임 수신 뒤임을 raw로 보일 수 있다" — 보일 수 없었다(helper 읽기 시점은 …499와 …559 사이, 게임 수신은 …538).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `docs/work/active/G1_STRATEGY_W70_INPUT_RELEASE_BOUNDARY_LAP938.md`, 이 기록,
  `docs/history/20261004_lap938_prior_lap937_escalate_sol_byte_exact.txt`(SHA256 `67dd81b0fd3452597c3f3223b135b2670b7fd2e5547c782305ab012a82ae7e50`),
  `docs/history/20261004_inbox_lap938_precompaction.md`(345줄, SHA256 `ec258fbd4a4a02f9d4fa4e6ad5964c1e936620fcc8dfdf71f9f6b5a29a17dddc`),
  `docs/history/20261004_approvals_lap938_precompaction.md`(249줄, SHA256 `7b20a743485a9b60269da8fb3d0d2090350c86116e12325b15df0779c3a91af5`).
  갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`(체크 완료된 lap743·745·746 처리 21줄을 포인터 3줄로, 판정 항목 추가),
  `docs/feedback/APPROVALS.md`(종결된 lap860·861 11줄과 lap847·848 9줄을 포인터 5줄로, 현재 판정 줄 교체, lap937·938 판정 항목 추가). `loop/ESCALATE_SOL` 제거(보존본과 `cmp` 일치 확인 뒤).
  제품/하네스/test/validator/golden/안전핀/원본/save/기존 raw·PNG 변경0. uncommitted. HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는 provenance일 뿐이다.
  읽은 source SHA256: `tools/g1_saved_scene_probe.py` `28ef2deab769c5d373be1fb3ba6ae51b87c4bcea16ea6dc45ff07b153d133164`,
  `tests/test_g1_saved_scene_probe.py` `d7a879d2db2072c04ee0188a4f5b18f7e46315411704923191ac59998ac7c3d4`(둘 다 lap936·937 기록과 일치),
  `tools/x11_mouse_click.py` `eab6e2648ab437d8b70f29223d469765a9408b477537059b7ef8d4f9266b81c0`,
  `tools/inmm_stub/direct_draw_trace.c` `8b61823e8a548ce6ac8cfdf514b19d78f389f53861ded3ba455b92c53b11b0f8`,
  `tools/inmm_stub/g1_mirror2x.c` `b70d044acb18842ee68a418539ae0f974e1652a615ace8cfa8faa019cb011804`(lap934 기록과 일치).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 새 실행 없음. 읽은 기존 증거는 lap936 r3 한 pair다 —
  격리 Wine/Xvfb, 원본 800×600 대 1600×1200 Scale2x, save006(비합성 fixture) 카메라 `[158,101]`, 시딩 없음.
  보호 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`·save006
  `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`는 종료 검사에서 다시 확인한다(결과는 STATUS). 8 player records는 활성 8인 부하 증명이 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap938_strategy_review/`.
  `.venv/bin/python recount.py`(저장소 루트에서 실행, 읽기만 한다. r3 산출물 73개·prefix의 input/present trace·source 5개·lap937 재계산을 실행 전후로 해시해 변화0).
  SHA256: `recount.py` `1768cc50e1c16598828225ea848ae8c6eda1261b1a06f7c47da0ad1fb54cd391`,
  `recalculation.json` `a4b49c27ef2589f63e132495d92c871a1b06697290fc47d4c57121232a783163`.
  새로 읽은 raw: `local/runtime/lap936_input_pair_r3/candidate/20261004_130230_2981400_0/prefix/drive_c/inmm_g1_input_trace.jsonl`
  (512행 = GetCursorPos 494 + WndProc 버튼 18, SHA256 `e639b5257c73f8e5069702c604a23208fe2e7c43f4a3ae64c6128f5ec2d4fc64`).
  같은 prefix의 present trace와 공유 temp `trace_raw.jsonl`은 SHA `81f7e8b76638c82cba04e3bbabb8ef916f99f766d1970b8f91b8dc33ebd617a6`으로 같다.
  직접 본 PNG: `20261004_lap936_input_pair_r3/candidate/drag.png`(SHA `a3419c83610b2d83b036c99cc93219922a56700430080e042a53b351db50d9cc`, probe-result 기록값).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - source 결함: lap937 판독 **확인**. `g1_saved_scene_probe.py:3484~3488`(주입 전 seq) → 3491(`after_seq`) → 2227 helper. 3516 binding은 present 상태를 보지 않는다.
  - release 순서: 드래그 `WM_LBUTTONDOWN` ts `2460854263`(logical `[100,40]`, input seq 41), `WM_LBUTTONUP` ts `2460854538`(logical `[400,220]`, input seq 47), 간격 275ms.
    gate 기록 seq1052 ts `…450`(−88ms), seq1056 ts `…499`(−39ms). present·WndProc 모두 pid 276·thread 280. **lap936의 "button-up 뒤 present 2건"은 반증(FAIL), lap937의 UNKNOWN은 "release 전"으로 확정.**
  - gate 동작: helper elapsed 0.0107초, 첫 읽기에 `seq > 1028`인 present 7개(1032~1056), 전부 release 전. down~up 사이 present 5개, ts 동률 0.
  - release 뒤 present: 1060(+21ms)·1064(+65)·1068(+115)·1072(+164)·1076(+214)·1080(+266)… 정착 대기 300.6ms로 본 캡처 시작 하한 `…798` 이전이 5개.
    epoch 대조(MONOTONIC_RAW) 캡처 `…785.7`(release +247.7ms)에서도 5개. **대조값이며 r3 binding `PASS`를 수용하는 근거로 쓰지 않는다.**
  - 경계 세 가지를 r3에 대입: 주입 전 seq(지금 코드) → 1052/1056(둘 다 release 전). 호스트 반환 seq(lap937 인계 1번) → 1060/1064(이 실행에서는 release 뒤, 첫 행 여유 21ms,
    그러나 호스트 반환이 게임 수신 뒤라는 보장 없음). 프로세스 안 release 행 → 1060/1064(구조상 release 뒤).
  - minimap(r3 사실 확인만): 두 lane gate `00000000→01000000→00000000`, `(182,548)` 클릭 도달(input seq 61/64), 카메라 `[158,101]` 불변. pair `input_effect_comparison` HOLD
    (`minimap_gate_restore`·`production_effect` false, 나머지 true). 원본 parity이며 회귀 증거 아님.
  - 판정: **선택 의미 PASS(partial) 유지 / r3 capture binding 불수용 / 입력 캡처 HOLD·G1 HOLD 유지 / G1 계속.** 경계 = 게임 WndProc의 `WM_LBUTTONUP` 행(R1~R5).
  - SKIP: 전체 `make check`·새 runtime(문서만 변경, 다음 work가 source 변경 뒤 실행). lap936 Fast 1476 PASS는 과거 증거다.
  - UNKNOWN: 고친 gate의 실제 동작, release 뒤 첫 present가 release를 반영한 프레임인지(2개 요구로 덮는다), baseline의 present 시점, minimap 유효좌표.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: release 행 조건(정확히 down 1·up 1, logical 일치)이 엄격해 다른 버튼 메시지가 끼면 `UNKNOWN`→`HOLD`가 난다(숨기지 않는다).
  `GetTickCount`는 부팅 49.7일에 돈다(지금 28.5일) — 돌면 `UNKNOWN`으로 닫힌다. baseline은 계측이 없어 `PASS_WITH_LIMITS` 그대로다.
  이 판정은 strategy 범위 판정이며 2단 middle 수용·3단 사용자 승인이 아니다. lap937·938은 제품·실행 증거가 늘지 않은 연속 2회다 — 다음은 반드시 work다.
- 다음 한 가지: work **입력 경계 수리** — 카드 §2~§4. 회귀 RED → R1~R5 → fresh unscrolled pair로 P-1~P-6 확인(귀속 가능한 결함은 같은 회차에서 수리·재실행) →
  한 번에 GREEN이면 §6 minimap 유효좌표 pair → Fast → 새 middle.
