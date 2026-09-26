# 2026-09-18 | lap 387 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`/high, 실무(work) 역할.
  `docs/MODEL_ROUTING.md` 2026-09-18T17:56:55+09:00 override 준수. STATUS "다음 한 가지"의
  Astra `GO_FINISH_CURRENT_LAYOUT_CONTRACT_ONCE` 지정 범위(§3-5 Part A+B를 같은 module/tests에서
  한 번에 완료, 재작성/별도검수 회차 없음)를 이행. 원문
  `g2_capacity/20260918_post_layout_major_decision.json`(외부 temp) 직접 재확인.
- 가설 / 사용자 관찰: Part B(BULK start/length/end, PlayerStruct base/end/stride)는 Part A가 이미
  가진 `REGIONS` 테이블/`map_va`에서 **새 주소 추론 없이** 유도 가능하다 — Astra가 pin한
  `newBULKstart=0x892410+1880d`/`newBULKlength=0xE397C+14d`(`d=N-1200`)는 각각 `regions[0]`의
  성장(1880=`0x758`)과 `regions[1:5]`(existence/age/catA/catB/active_slot_list) 성장 합
  (2+2+4+4+2=14)과 정확히 같다. PlayerStruct(base `0x956770`, stride `0x3ABC`, 8명)는
  `gap_after_category_slot_list_b`(883,742B foreign block) 안에 완전히 들어가므로 `map_va`의
  기존 foreign-shift 경로로 그대로 사상된다.
- 예상 PASS / FAIL 조건: `bulk_length`/`bulk_end`가 N=1200에서 `0xE397C`/`0x975D8C`, N=4001에서
  `bulk_state_base==0xD97DE8`·`bulk_length==0xED2AA`(Astra 판정 원문의 고정 검산치와 바이트 일치).
  `player_struct_layout(n)`이 stride/count 불변(`0x3ABC`/8)을 유지하고 base/end가 매 N에서
  `bulk_state_base(n)`~`bulk_end(n)` 안에 들어간다. `mapped_offset`이 동일 foreign block 내부에서
  naive 차분과 일치하고 사상 불가 endpoint를 예외로 거부한다. `make check` rc0, `SAFETY_PASS`,
  원본/frozen 불변, 기존 82건(Part A까지) 회귀 0.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `patches/population/base_preserving_storage_layout_v1.py`
    (이전 `7fac1659…9f0ab6f2` → 이후 `1469752c…f0c1bd`): `BULK_OLD_LENGTH`/`PLAYER_STRUCT_BASE`/
    `PLAYER_STRUCT_STRIDE`/`PLAYER_STRUCT_COUNT` 상수(전부 이미 pin된 사실, 신규 추론 0),
    `LayoutResult.bulk_length`/`.bulk_end` property, `mapped_offset()`, `PlayerStructLayout`+
    `player_struct_layout()` 추가.
  - `patches/population/test_base_preserving_storage_layout_v1.py`
    (이전 `88672c65…c8ccee9a`[A2 이전]/`c1fc5bcf…9ce0523`[lap386] → 이후
    `5c220a73…f0bd70c70`): pytest 15건 추가(총 82 collect, 이전 56/Part A 3건 포함분 기준 증가분).
  - `patches/population/offline_storage_v1.py`: 무변경(frozen `e9d84513…9f8cc` 확인).
  - 외부 temp `g2_capacity/20260918_lap383_layout_artifact/g2_layout_n4001_mapping.json` 갱신
    (bulk/player_struct 절 추가, SHA `010224184bc9178de1bc809d91f68b55afe252ce93f4cb31e7183e7d02987f6d`);
    `g2_layout_n4001.pelayout`는 동일 SHA `38a7148e…36cbc808`(Astra 원문 "이전같은bytes는동일SHA일수있음"과
    합치 — geometry 계산 로직 자체는 변경이 없었다).
  - LOOP_ALLOW_COMMITS 미설정 — **uncommitted**로 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e0…c9c08a8ac`(불변, 재해시로 확인). 후보 EXE 생성/게임 실행 없음(범위 밖). fixture 없음
  — 순수 geometry 유닛테스트 + 외부 temp artifact 재생성(비실행 `.pelayout`).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 -m pytest patches/population/test_base_preserving_storage_layout_v1.py -q` → 82 passed.
  - `make check` → `715 passed in 119.39s` + Ruff all-checks-passed + compileall + mypy10파일
    success + `CONTEXT_PASS`.
  - `bash checks/safety.sh check` → `SAFETY_PASS`.
  - artifact 재생성: `write_layout_artifact(...,4001)` → 위 SHA.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): Part B PASS(단위 계산 수준) — N=1200 identity,
  N=4001 BULK start/length가 Astra pin과 바이트 일치, 5개 sidecar 영역/8-PlayerStruct 전부 매 공학
  테스트 N에서 mapped BULK 구간 안에 fit, launcher-rejection 회귀 유지. **work 자체판정이며
  다음 middle 독립검수 대기 — ACCEPT 아님.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 82건(Part A까지) 전부 유지, 이번 회차
  신규 포함 총 715 passed(전체 `make check`), 실패/스킵 없음. §3 계약 5번은 이번 lap으로 **모듈
  단위 구현 완료**(Part A+B 모두 산출)이나, code operand fixup·저장 포맷 변경·게임 실행·runtime
  승인은 **여전히 없음** — lap379 Sol의 integration/broad-patcher NO-GO는 유효, G2 8인5000
  lifecycle/economy/save/LAN 미완료. Astra의 stop 조건(30+10분 내 미완료 시 부분 모듈 보존 후 STOP)은
  발동하지 않음 — 이번 회차 내 완료.
- 다음 한 가지: 다음 새 middle(Opus5/high)이 이번 Part A+B 구현(전체)을 **독립 재유도**로 한 번에
  검수한다(재작성/별도검수 회차 금지 — Astra 지시대로 단일 검수). ACCEPT/REJECT 판정과, ACCEPT 시
  이 레이아웃 카드의 최종 결론(§3 계약 5번 CLOSED 여부, `lap379`/`native_route_judgment`가 이미
  명시한 "no credible bounded native slot>=1200 lifecycle/save milestone"과의 관계 — 이 카드
  ACCEPT는 그 판단을 뒤집지 않음을 재확인)을 middle/컨펌 역할이 정한다. 이 카드가 끝나도 G2는
  미완료이며 새 alias별 후속 카드는 금지(Astra `not_allowed`).
