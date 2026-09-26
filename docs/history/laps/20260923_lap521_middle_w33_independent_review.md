# 2026-09-23 | lap 521 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / middle(중간계획·컨펌). `LOOP_ROLE=middle`.
- 가설 / 사용자 관찰: 이번 회차는 두 가지를 한다. 하나는 lap520 W33 M-0/M-1(X520)의 독립 검수다. 다른 하나는 PROMPT ③의 "실행 증거 무증가 3회째" 경계에서 트랙② 지속 여부를 판정하는 것이다.
  실행 전 가설: X520의 M-0 뼈대는 맞다. 다만 "종-의존 신호는 반경 하나뿐"이라는 부분은 callee를 덜 본 결과일 수 있다.
- 예상 PASS / FAIL 조건: probe 단언 B1~B7(데이터 개봉 전 고정)이 전부 성립하면 검수 입력이 성립한 것이다.
  B4가 성립하면 X520 §2 서술은 반증된다. B7이 불성립하면 참고 캡처를 쓰지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 파일: probe `docs/history/laps/probes/20260923_lap521_middle_w33_independent_review.py`, 근거 `analysis/memory_maps/ai_build_state2_footprint_review_lap521_20260923.md`, 이 기록.
  - 신규 스냅샷: `docs/history/20260923_status_lap521_precompaction.md`(STATUS 원문, SHA `b05e5b60…`, 124줄).
  - 갱신: W33 카드 §6, STATUS, INBOX, `loop/ESCALATE_SOL` §79.
  - 제품 source 변경 0, 커밋 0(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 `b56986e0…`는 전후 불변이다. 후보 EXE는 없다. 게임 실행은 0이다.
  - 참고 캡처(읽기 전용) `unit_templates_9b5228_394x152.raw`의 SHA는 `d7bf3e1f…`다.
  - lap518 런타임 `type_specs.json`(`a23ba1d7…`, fixture `_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`)과 대조했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 docs/history/laps/probes/20260923_lap521_middle_w33_independent_review.py`: exit 0. 2회 산출 SHA `00af62eb…`로 동일하다.
    1차 실행은 B6 스윕 도구 결함으로 0건이 나왔다. skipdata와 sanity를 추가한 뒤 재실행했다.
  - lap520 probe 재실행: exit 0, `899db3f9…` 재현.
  - 산출 경로: `temp/Syw2plus_patch/g2_capacity/20260923_lap521_middle_w33_review/`.
  - `make check`: exit 0, **819 passed**(8분42초), ruff·mypy 통과. 로그는 같은 폴더의 `make_check.log`다.
  - `checks/safety.sh check`는 `SAFETY_PASS`, `checks/context_limits.py`는 `CONTEXT_PASS`(STATUS 129·INBOX 343·APPROVALS 45줄)다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **X520 M-0 뼈대 ACCEPT.** F5A0 2곳, `+0x3A70` 쓰기 0, EXIT_A 종-무관(callee F4F0까지 확인).
  - **정정 N172~N176.**
    - N172: 타일 검사 `0x4A4E70`이 kind를 받는다. 41/56/68은 별도 술어 `0x4A4BF0`(조선소 추정)을 거친다. 따라서 X520 §2·§3의 해당 추론은 REJECT다.
    - N173: `+0x16`/`+0x18`은 footprint 폭/높이다.
    - N174: M-1 `UNRESOLVED_STATIC_ONLY`의 전제는 REJECT다. 참고 캡처가 런타임 표와 6필드 152/152 kind 일치하므로 정적으로 얻을 수 있다.
    - N175: `+0x3A74`는 sticky 플래그다. 초기화 `0x43ECAF`에서만 0이 되고 읽기는 0곳이라 카운터로 쓸 수 없다.
    - N176: 첫 루프의 두 번째 F4F0 경로가 X520에서 누락됐다.
  - **M-1 재계산(원시):** footprint 규칙 R1은 11/14, R2는 12/14다. 반례는 50·105다. 임계를 사후에 정했으므로 카드 §3 라벨은 **미부여**다.
  - W33은 `CLOSED`로 둔다. 추가 정적 해독으로는 라벨을 얻을 수 없다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 회귀는 없다(읽기 전용).
  - 남은 위험 1: footprint는 이 fixture에서 직접 읽은 값이 아니다(캡처 동일성 근거는 겹치는 6필드).
  - 남은 위험 2: EXIT_A/B 실측 비율, 50·105 예외, 선택 시점 교란은 모두 UNKNOWN이다.
  - 사용자 승인은 불필요하다(읽기 전용).
- **트랙② 지속 판정(middle, PROMPT ③ 3회째 경계): 진단 `CLOSED`, 자동 계속하지 않는다.**
  - 근거 ①: 사용자 질문 "18종을 왜 안 짓나"의 답은 진영 블록이다(N158). "왜 느리나"는 세 가지로 좁혀졌다. 스케줄러 천장(N164), 상태2 손실 약 70%(N170), 그리고 그 손실이 footprint·조선소 술어와 정합한다는 점(N172~N174)이다.
    (ㄴ) 로직 변경 여부를 사용자가 판단하기에는 충분하다.
  - 근거 ②: 남은 모호성은 하드웨어 breakpoint 분기 계수 24k 1회로 풀 수 있다(FEASIBLE, §79에 초안). 그 값은 사용자가 (ㄴ)을 고른 뒤에야 쓸모가 있다.
  - 근거 ③: 이번 회차는 실행 증거 무증가 3회째다. 네 번째 정적 회차는 금지다.
- 다음 한 가지: **STOP(사용자 응답 대기)** — Q9 · Q8((ㄱ)/(ㄴ)/(ㄷ)) · Q7-B · "8인" 정의.
  트랙②의 결과로 (ㄴ)을 고를 경우 W34 계수 probe를 발행할지도 함께 대기한다. 12:55 지시의 트랙①·② 모두 `CLOSED`이므로 `loop/ESCALATE_SOL` §79로 상위(strategy/사용자) 확인에 넘긴다.
