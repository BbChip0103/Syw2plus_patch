# 2026-09-23 | lap517 | 목표 G2 (트랙② 건설 속도)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / **middle(중간계획·컨펌)**.
  대상: lap516 work(Sonnet5) W31 산출 독립 검수. 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap516 M-0 바이트 주장과 M-2 원시 집계·라벨이 독립 재계산으로 재현되는가.
  특히 "`+0xD34` = 20종 AI 오더 공용 ID"(§1.2)와 "재무장 스케줄러 UNKNOWN"을 원본 바이트로 확인한다.
- 예상 PASS / FAIL 조건: 사전 고정 단언 A1~A9(정적)·B1~B6(원시 재집계) 전부 참이면 해당 주장 ACCEPT.
  A4가 참이면 lap516 §1.1/§1.2 해석은 기각된다(docstring에 실행 전 명시).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **제품 source 변경 0, 커밋 0.** 신규·갱신(전부 uncommitted):
  - `docs/history/laps/probes/20260923_lap517_middle_w31_independent_review.py`(신규, 읽기 전용 probe)
  - `analysis/memory_maps/ai_build_order_scheduler_0043f5d0_lap517_20260923.md`(신규, N162~N167)
  - `docs/work/active/G2_BUILD_ORDER_FUNNEL_PROBE_LAP517.md`(신규 카드 W32)
  - `docs/work/active/G2_BUILD_PACE_STATE_PROBE_LAP515.md` §6 추기(W31 `CLOSED`)
  - 본 파일, `docs/STATUS.md`, `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL` §75
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(A1, 읽기 전용).
  입력 lap516 원시 `samples.jsonl` SHA `9fa1073709c4048895dc2b0495a5332f089b5b20c14f72c8904a48a081808355`(B1) 외
  lap516 산출 10개 SHA를 기록값과 대조해 전부 일치. 후보 EXE 실행 0, 게임 실행 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 docs/history/laps/probes/20260923_lap517_middle_w31_independent_review.py`.
  **1차 실행 exit 1(A2 FAIL)** — 원인은 단언 작성 결함: 명령 목록 완전 일치를 요구했으나 실제 바이트에 무관한
  스택 저장 `mov [esp+0x2c],ebp`·`mov [esp+0x28],ebp`가 끼어 있고 범위가 `0x43E113`을 넘었다. 판정 명령
  (`movsx [edi+0xD34]`/`dec`/`cmp 3`/`ja 0x43E7C9`/`jmp [eax*4+0x43E7D8]`)은 동일 ⇒ 단언을 "스택 저장 제외 후 일치"로
  고치고 사유를 docstring에 남겼다. 2·3차 exit 0, 16/16 PASS, 산출
  `temp/Syw2plus_patch/g2_capacity/20260923_lap517_middle_w31_review/w31_independent_review.json`
  SHA `8802218b69d9a88cc7bc832e61b097e6ad8f949307b85687dd2d7bd10b54602c`(2회 동일).
- 측정값 / 판정:
  - **M-2 원시 재집계 ACCEPT(불일치 0/8):** 1,439표본, tick 17→24,013, 간격 최대 18. 상태 비율 |Δ|≤0.06pp,
    상태1·4 0표본, 건물 시작→끝·감소0·마스크 평균·max used 전원 일치. 기타 `+0xD34` 값 {101,5,6}.
  - **라벨 `UNCLASSIFIED` 8/8 ACCEPT**(고정식 적용 결과로서). 다만 전제 필드 `+0xD32`가 미기록이라 어느 라벨도
    평가 불가였다는 것이 실제 사유다.
  - **M-0 부분 기각:** A2/A3/A5/A9 ACCEPT. **N162** 오더 종류 = `+0xD32`(실행 switch `0x43FB62`, `cmp 0x1a` 27칸),
    `+0xD34` = 하위 상태, 20칸 표는 선택표 `0x43FD10` ⇒ §1.1 "20칸"·§1.2 "오더 ID" 기각. **N163** `FUN_0043F5A0`
    호출자 40곳, 명령 발부 직후 `0x43E7C4` 포함 ⇒ 성공·실패 공통 종료. **N164** 재무장 스케줄러 해독:
    `0x41CBE5`(유일 호출자)가 tick&7로 owner 1명 ⇒ owner당 8 tick 1회, `+0xD32==0`이면 `rand%20`, index2만 건설,
    `|tick−[+0x33AC]|>100` 쿨다운. **N165** `+0xD34==0` 85.6~87.9%는 "비활성"이 아니라 오더 없음+타 오더 하위상태0의 합.
    **N166** lap516 외삽식이 카드식과 다름 — 카드식(160채) 211,982~423,946 tick(24k의 8.8~17.7배).
    **N167** 늘 한가해도 건설 오더 시작 ≈91회/24k(쿨다운 무시 150) ⇒ 관측 9~18채는 10~20%, 케이던스 단독 설명 불가.
  - W31 `CLOSED`, 후속 W32 발행(`+0xD32`/`+0x33AC`/`+0x3A70` 계수기로 점유→시작→발부→완공 깔때기 판별).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 0(제품 source 변경 없음). `make check` exit 0
  **819 passed**(8m30s)·ruff/mypy 통과·`CONTEXT_PASS`, `checks/safety.sh check` `SAFETY_PASS`, probe ruff 통과.
  신규 파일 SHA: probe `573fd5e4…`, 근거 문서 `61518ec0…`, W32 카드 `5c57bf69…`, STATUS 압축 블록 `1d8f94df…`. 남은 위험: 다른 19개 오더의 의미·지속시간 미해독, 상태 5/101 소속 미검증,
  `+0xD34==2/3`의 건설 오더 소속 미확정(프록시 상태2 진입 36~49회). 사용자 미결 불변: Q9·Q8·Q7-B·"8인" 정의.
  이 회차는 실행 증거를 늘리지 않았다(middle 문서·정적 probe) — 다음 work 회차는 반드시 W32 실제 실행이어야 한다.
- 다음 한 가지: **work(Sonnet5)가 W32를 1회 포그라운드 실행**(24k, W31 스크립트 복사+필드 3개) → middle 독립 검수.
