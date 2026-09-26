# 2026-09-23 | lap 514 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 지정 역할 middle(진단·계획·컨펌).
  게임 코드 hands-on 수정 0, 게임 실행 0, 커밋 0.
- 가설 / 사용자 관찰: STATUS「다음 한 가지」= lap513(work) W30 안 B 결과(24k soak `HOLE_CONSTANT`, 단위 23,
  `make check` 819)를 원시에서 독립 재계산해 카드 W30 `CLOSED` 여부를 판정한다.
- 예상 PASS / FAIL 조건(착수 전 고정): ① 원시 `window_hex`에서 `+0x2016..+0x2018` 재추출 위반 0·tick≥24,000,
  ② 원본 전수 스캔에서 `[0x200c,0x2010)`·`[0x2016,0x2018)` **겹침** 접근이 카드 15곳+비도달 1곳 외 0,
  ③ 후보 생성→diff 사이트 밖 0→역디스어셈블 15/15→원복 원본 SHA, ④ 9개 used 사이트 소비가 전부 32-bit,
  ⑤ 단위 23 passed·`make check`·`SAFETY_PASS`. 하나라도 실패하면 REJECT/수리 범위 발행.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 probe
  `docs/history/laps/probes/20260923_lap514_middle_w30_holeb_independent_recompute.py`, 신규 근거
  `analysis/memory_maps/g2_supply_ledger_holeb_acceptance_lap514_20260923.md`, 이 기록, 카드 W30 §9, STATUS, INBOX 진행 메모,
  `loop/ESCALATE_SOL` §72 추가. 제품 source(`patches/`) 변경 0. uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e0…a8ac` 전후 불변.
  안 B 후보 SHA256 `1893ff508f5ef662e91e9500531108aaab680bab62866e324fe6fb517f353ae1`(probe 기계 산출, 임시 복사본 생성 후 원복).
  런타임 증거는 lap513 원본 EXE 실행(8 owner AI, `_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`, rice/wood 각 1,000,000,
  bridge `unit-pool-capacity=1200` `89e44c18…`) — 이번 회차 게임 실행 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 docs/history/laps/probes/20260923_lap514_middle_w30_holeb_independent_recompute.py`
  (exit 0, 2회 결정적) → `…/temp/Syw2plus_patch/g2_capacity/20260923_lap514_middle_w30_holeb_review/w30_holeb_independent_recompute.json`
  SHA256 `0c0ed0d22b9e522e2f97ef4f87212b4fbb961010b5389132b5bcb3d1c1712359`. 입력 `run_summary.json` `b8c3b452…`,
  `samples.jsonl` `030f6a0e…` 재해시 일치. `python3 -m pytest -q patches/population/test_supply_ledger_32bit.py` 23 passed.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  ① **PASS** — 721줄×8=5,768 owner-표본, 위반 0·비영 0, tick 16→24,019 단조, 요약 필드(`hole_hex`/`used`)=원시 전 표본 일치.
  이웃 필드 생존: `+0x2014` 최대 [9,9,11,55,9,9,9,11], used 최대 1,615, building 최대 20.
  ② **PASS** — 306,187 명령. 겹침 `[0x200c,0x2010)` = used 9 + building 4 + `lea 0x444C63`(→`+0x200a` word 전용, 오탐);
  `[0x2016,0x2018)` = `0x43F57F` 1곳(`esi≥1` 루프 ⇒ 최저 `+0x2018`, 원본 바이트 확인). `lea` 별칭 전수 5곳 무관.
  ③ **PASS** — 15 edits, diff 66B, 사이트 밖 0, 역디스어셈블 15/15 카드 §8 표와 일치, 원복 SHA=원본, 입력 불변.
  ④ **PASS** — 9곳 모두 32-bit `add`/`cmp`/`push`로 소비, 16-bit 재절단 0. writer 앞 `movzx` 2곳 확인.
  ⑤ **PASS** — 단위 23 passed. 문서 갱신 후 `make check` 동기 완주 exit 0: **819 passed**(504.93s)·ruff "All checks passed"·
  mypy "no issues in 10 source files"·`CONTEXT_PASS`. `checks/safety.sh check` `SAFETY_PASS`. 원본 재해시 `b56986e0…` 불변.
  **종합: W30 안 B = `ACCEPT` ⇒ 카드 W30 `CLOSED`(카드 §5 범위 = 정적+단위+원복+원본 hole 런타임).**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 관찰 1: `test_supply_ledger_32bit.py`의 M-e/M-f는 Python 산술 모델(동어반복)이라 패치 바이트와 독립이다. 기계어 수준 근거는
    `test_patched_bytes_match_new_encoding_exactly` + 이번 ④ 소비 폭 검토다. 실패는 아니며 기록만 한다.
  - 관찰 2(편차, 공개됨): lap512 스크립트는 카드 §8의 "세 상수만" 외에 `MAX_WALL_S` 400→1500도 바꿨다. wall 상한일 뿐이고
    실행은 `stop_tick_reached`로 끝났으므로 판정에 영향 없음. lap512 자체 lap 기록 파일은 없다(lap513 기록이 대신 서술).
  - 한계: 후보 EXE 실제 게임 실행 0(Q9 미결) ⇒ **G2 제품 합격 근거 아님**. 구세이브 재계산 훅 미구현 ⇒ 신규 게임 전용.
    `memcpy`류 필드 접근은 정적 배제 불가(전체 블록 복사는 무해).
  - 승격 조건(필수 검증 예상 밖 실패·근거 충돌·마일스톤 경계) 해당 없음: 트랙② 전환은 2026-09-23 12:55 사용자 지시가 정한 순서다.
- 다음 한 가지: 트랙② 건설 선택 로직 분석(읽기 전용, (ㄴ) 불필요) — 다음 middle이 W31 카드를 발행한다.
  입력: `FUN_00406C70` 추첨 로직, H-CROWD 채널 주소 정정(N147), N151(27종 중 9종만 건설)·N152(고가치 종 64·53·61·65·67 미건설).
  측정식 초안: 18개 미건설 종 각각에 대해 "추첨 후보 집합 진입 조건"을 원본 바이트로 확정 → 원인 분류(선행 건물/테크/자원/지형/가중치 0) 18/18.
