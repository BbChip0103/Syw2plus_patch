# 2026-10-04 | lap944 | G1 W70 생산 입력 — queue type31 대 type7 승격 해소 / witness 계약 정정 / work 카드 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향·상위 계획) 역할, 일반 작업자. Fast 설정 없음.
  자동 폴백 아님. 게임 코드·하네스·test·validator 수정0, 게임 실행0, build0, subagent0, 커밋0. `loop/.lap_counter` 944 읽기만
  (러너 주입 문구의 lap=943보다 파일이 최신이다).
- 가설 / 사용자 관찰: lap943 work가 "사전 계약은 queue type7인데 fresh raw는 type31, 원본 control은 쌀 자연 변동으로 UNKNOWN"이라며 승격했다.
  이 세션의 질문은 (1) type31이 slot1199/타입58의 올바른 원본 witness인가, (2) `(668,540)`이 이 장면의 생산 칸인가,
  (3) 클릭 전 `31/100`이 기대 전이를 바꾸는가, (4) 자연 변동을 숨기지 않고 반증 가능한 control을 어떻게 얻는가다.
  사용자 상시 지시(2026-10-03 14:37 G1 자율 지속, 구현 우선, 묻지 말고 결정)를 적용했다.
- 예상 PASS / FAIL 조건: 판정 회차다. (1)의 반증은 "발행 코드가 `+0x320`에 고정값을 쓴다" 또는 "진영2 건물이 type7을 만든다" — 둘 다 아니었다.
  (2)의 반증은 "캡처의 그 칸이 다른 명령이다" — 툴팁이 `일본 농부 800/300/10`이었다. (3)은 raw의 클릭 전 값으로 갈린다 — 세 HQ 모두 `31/100`이었다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `docs/work/active/G1_STRATEGY_W70_PRODUCTION_QUEUE_WITNESS_LAP944.md`
  (SHA256 `55567941fa1c249159785a662ccab97d936e4d092919bd8745bd6f60fcad5dea`),
  `analysis/memory_maps/g1_production_issue_path_40df05_lap944.md`(SHA256 `c7405284addf7359a589b3cbd50f9b0349db604151dc7008e8d43c2148e5ef86`),
  이 기록, `docs/history/20261004_lap944_prior_lap943_escalate_sol_byte_exact.txt`(SHA256 `51a7d06cec5214a4a25e6112fa04b5322e00a582096d73a12ae2a3e87a1061f7`).
  갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`(판정 항목 추가), `docs/feedback/APPROVALS.md`(판정 항목 추가). `loop/ESCALATE_SOL` 제거(보존본과 `cmp` 일치 확인 뒤).
  제품/하네스/test/validator/golden/안전핀/원본/save/기존 raw·PNG 변경0. uncommitted. HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는 provenance일 뿐이다.
  읽은 source SHA256: `tools/g1_saved_scene_probe.py` `1f38b658be12bf837e74afd4821d8aed5138025169cf9ab736a96db4b9de4b01`,
  `tests/test_g1_saved_scene_probe.py` `278e8b5aa9955071c17bd8b6ff133e7278b73a9c3fb6cca2e69b905fcc12a053`(둘 다 lap943 기록·pair JSON과 일치).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 새 실행 없음. 읽은 기존 증거는 lap943 r4 한 pair다 —
  격리 Wine/Xvfb, 원본 800×600 대 1600×1200 Scale2x, save006(비합성 fixture), 시딩 없음. 이 세션에서 다시 해시한 값:
  보호 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006
  `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` MATCH. 8 player records는 활성 8인 부하 증명이 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap944_strategy_review/`.
  `.venv/bin/python scan.py <va:n>`·`around.py`(보호 EXE 읽기 전용 디스어셈블), `.venv/bin/python recount.py`(r4 pair·PNG 2장·source 2개·원본 EXE·save를
  실행 전후로 해시해 변화0, 제품 helper import 없음). SHA256: `recount.py` `458c89b0da50ec001667b4b6b30bad4704dc078d2c5624eab4d96d48897162ac`,
  `recalculation.json` `69f4d941437eb6ef40f8f1a4753544b4f4751da4b5b3273c41369f5515332073`,
  `scan.py` `b9c1cdfbc665cab38601db49a83c8d64d18c6701889cb2db231fac97c17ad2d7`, `around.py` `c9ce260f7269681a499beba863dd57dcd9d73c29ad578e95012482d098381808`,
  `production_issue_disassembly.txt` `e3dfbb261fb89384dd857d0b20e0d36d289b2205881e9c7bf771f6d0bcbe6e35`.
  읽은 raw: r4 `pair-result.json` SHA256 `431951368f032cb5cbdf39419240731c8a6694d5a9a073abbc05a4da0dd5e0f2`(lap943 기록과 일치).
  직접 본 PNG: r4 `baseline/production.png` `7b9622e32089399b344ce30355810f1313245630a7e8e3a110b94cecda0bc91f`,
  `candidate/production.png` `a8113bb439bd531611b840b1a8cf5968f07798576faa14c11a64298a13913ecd`(둘 다 pair JSON 기록값과 일치).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - 발행 코드: `mov word [reg+0x290], 0xF` 즉시값 패턴은 `.text`에 `0x40DF05` 1곳. 이어서 `0x40DF0E` progress=0,
    `0x40DF21` `[esi+0x320] = [descriptor*24 + 0x9E2F34]`. 비용은 `0x40DE43 call 0x43F0C0`(쌀 spec`+0x12`, 나무 `+0x14`, 인구 `+0x10`),
    `0x43F118` `[player+0x1C] += 인구`. **`+0x320`은 고정 7이 아니라 눌린 칸의 유닛 타입이다.**
  - type7 출처: r4의 command 15 건물(baseline 34개·candidate 35개) 중 type7을 만드는 것은 진영1 건물 타입49(owner5 slot628, candidate에서는 slot1189도)뿐이다.
    lap792(G2 ESL2608 Phase C)의 "owner0 신규 type7"이 lap815 handoff에서 save006 기대값으로 옮겨졌다. **fixture 상수의 오전사이며 제품 기준이 아니다.**
  - 진영2 HQ: owner0 타입58 건물 3개(slot 1163·1177·1199) 클릭 전 `command 1 / +0x320 31 / progress 100`(두 lane 동일), owner0 타입31 유닛 14개.
  - 칸: candidate 캡처에서 `(668,540)` 칸 툴팁 `일본 농부 800 / 300 / 10`, 생산 표시 `일본 농부 13%`. raw의 쌀 −800·나무 −300·progress 13과 일치.
  - `+0x1C`: HUD `1893/2300` = used 1470 + 423(baseline 캡처). r4 candidate의 423→403은 발행 +10과 5.09초 창의 다른 완료가 섞인 값(추정, 표본열 없음).
    candidate 캡처의 HUD `1923/2300`(+30)은 발행 +10만으로 설명되지 않는다 — **UNKNOWN**, 다음 work가 used를 함께 적는다.
  - control: baseline 1.008초 창에서 쌀 +640, 같은 창의 slot1199 `command/+0x320/progress` 변화 0. candidate 6.298초 창은 여섯 필드 변화 0.
    candidate 창 길이가 baseline의 6배인 이유는 raw로 알 수 없다(UNKNOWN).
  - 판정: **type31 = 올바른 원본 witness, `(668,540)` = 일꾼 생산 칸, type 전이 조건은 이 fixture에서 성립 불가.** 계약 K1~K6(카드 §2)로 바꾼다 —
    control은 건물 필드로 판정하고 자원 변화는 `control_global_delta`로 공개, 효과는 발행 단계 비용 정확 일치로 강화.
    **lap943 r4 production은 UNKNOWN/HOLD 그대로**(원본 lane 미클릭, 표본열 없음). production·G1 HOLD 유지, G1 계속.
  - SKIP: 전체 `make check`·새 runtime(문서만 변경, 다음 work가 source 변경 뒤 실행). lap943 Fast 1491 PASS는 과거 증거다.
  - UNKNOWN: 원본 lane의 클릭 결과, 타입31 spec 실제값, 발행 한 단계의 `+0x1C` 변화, 생산 완료, 정상 gate=0 미니맵.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기대 타입을 7→31로 고치는 것은 기대 ID 변경이다. 근거는 클릭 결과가 아니라
  발행 코드와 클릭 전 raw·툴팁이며, 원본 lane이 31이 아닌 타입을 내면 카드 §6대로 strategy로 되돌아온다. control에서 자원 필드를 판정에서 뺀 만큼
  K4(정확한 비용)가 깨지면 그 lane은 UNKNOWN이 된다 — 자연 변동이 발행 단계와 겹치면 재실행이 필요하다. baseline은 프로세스 안 입력 trace가 없다.
  이 판정은 strategy 범위 판정이며 2단 middle 수용·3단 사용자 승인이 아니다. 제품·실행 증거가 늘지 않은 회차 1회째다 — 다음은 work다.
  APPROVALS 249/250줄·INBOX 347/350줄이라 다음 회차는 기록 추가 **전에** 두 문서를 보존·압축해야 한다.
- 다음 한 가지: work **생산 witness 수리 + fresh pair** — 카드 §3. 회귀 RED(a~h) → K1~K6 → fresh save006 pair로 P-1~P-6 확인
  (귀속 가능한 결함은 같은 회차에서 수리·재실행) → Fast → 새 middle.
