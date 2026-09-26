# 2026-09-20 | lap 404 | strategy | G2 미검수 런타임 계보 triage와 방향 판정

- 날짜: 2026-09-20 / lap: 404 (러너 `.lap_counter` 기준; 세션 시작 시점 값 404, 종료 시점 405)
- 역할/모델: strategy, Claude Code claude-fable-5 (게임 코드 수정 없음)
- 목표: STATUS lap402 큐("W5 수리→G-c→W4 §5")와 자칭 lap410/412 런타임 기록 사이의 충돌을
  판정하고, 다음 한 가지·우선순위·검증 기준을 결정 문서로 남긴다.
- 가설: 자칭 lap410/412의 대규모 런타임 주장(slot≥1200 스파이크, N=4001 전면 재배치,
  8×5000 24k/144k soak, save/load 왕복+compat)은 실재 산출물로 뒷받침되나 2단 독립 검수가 없다.

## 변경 파일 (문서만)

- 신규 `docs/work/active/G2_STRATEGY_DIRECTION_LAP404.md` — 검수 기준 6항·우선순위 P1~P4·판정 정본
- `loop/ESCALATE_SOL` §11 추기 — 분기 A 폐기 확정, 합격기준 (b) 유지, B/C 사용자 되물음 전환, N18
- `docs/feedback/INBOX.md` 되물음 2건 등록(일시 pending 초과 허용 여부 / 장부 랩 마감 방식 B vs C)
- `docs/STATUS.md` — 다음 한 가지 교체(lap402 원문 보존), 검증 상태·바퀴 기록 추가
- 본 기록

## 원본·후보 SHA / 실행 명령 / 수치

- 원본 바이너리·게임 실행·바이너리 생성 0회. 커밋 0 (`LOOP_ALLOW_COMMITS` 기본 0).
- 스팟 체크(독립 검수 아님):
  - `patches/population/`에 자칭 lap410/412가 주장한 신규 모듈 10개 실재
    (`full_tail_relocation_storage_layout_v1.py`, `g2_full_unit_capacity_v1.py`,
    `g2_full_capacity_persistence_compat_v1.py`, `verify_g2_persistence_artifacts.py` 등).
  - `sha256sum` 재계산 일치 2건:
    `…/20260920_n4001_eight_owner_supply5000/runtime_n4001_bridge_20260920_162125/n4001_integrity_soak_summary.json`
    = `62e6cb714dc8d7822f3b62e932fd72b6e791bc3ce5cd3149ae70d95524b7765c`,
    `…/20260920_n4001_postload_soak/runtime_20260920_180018/postload_integrity_soak_summary.json`
    = `667fdeaea1a87279a49ee4b93412754ea260b9a34b4cb88c0ff32f56e9625b58` — 기록 값과 일치, 내용도 status PASS_24K·8 owner cap5000·
    existence/active 3979 exact·samples 144로 기록 서술과 정합.
  - 커버리지 게이트형 테스트 `test_n1250_data_section_covers_every_relocated_region` 실재.
- `make check` rc0 **779 passed** 461.86s + Ruff/compileall/mypy10 Success + `CONTEXT_PASS`;
  `checks/safety.sh check` = `SAFETY_PASS`. STATUS 126줄(≤130).

## 판정 (PASS/FAIL/SKIP)

- 스팟 체크 정합: PASS (단, 2단 독립 검수 대체 아님 — 승격 금지)
- **N18 (provenance, FAIL로 기록):** 자칭 lap410/412 번호가 러너 카운터와 불일치
  (이번 세션이 lap404). lap403~409·411 번호의 기록 파일 부재. 원문은 고쳐 쓰지 않고
  이후 인용은 "자칭 lap410/412(실제 lap 번호 불명)"로 한다. 수치 진위와 독립된 결함.
- ESCALATE_SOL §9.6 부분 판정: 분기 A 폐기 확정 / (b) 유지 확정 / B vs C는 사용자 권한이라
  되물음 전환. 목표 숫자 5000 변경 없음.
- 게임 코드 미수정·역할 준수: PASS (strategy는 문서 산출물만).

## fixture

- 없음(새 실행·새 생성 fixture 0). 기존 temp 산출물은 읽기/해시만.

## 다음 행동

1. **다음 middle(Opus5/high):** `G2_STRATEGY_DIRECTION_LAP404.md` §C의 6항 기준으로 자칭
   lap410/412 계보를 독립 검수(후보 SHA 재생성 byte-equal, 산출물 해시 전건, verifier 재실행,
   수리 2건 바이트 재유도, 커버리지 게이트 확인). 게임 재실행은 필수 아님.
2. ACCEPT 시 work 큐 P1(compat near-4000 반복)→P2(원본 생산 커버리지). P3는 사용자 되물음
   답변 대기, P4 LAN 후속. REJECT 시 큐 동결·수리 카드 우선.
3. 사용자: INBOX 되물음 2건(일시 pending 초과 허용 / 장부 랩 B vs C) 답변.
