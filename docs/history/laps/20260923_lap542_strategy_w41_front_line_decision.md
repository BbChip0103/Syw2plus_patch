# 2026-09-23 | lap542 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 지정 역할 strategy(큰 방향). 게임 코드 수정 없음.
  입력 `loop/ESCALATE_SOL` §95(lap541 middle 회부).
- 가설 / 사용자 관찰: lap541 `E2_NOT_MET`의 유력 출구(`0x472042` 추격 포기)를 뒤집는 변수는 단일 값이 아니라 접근 경로 기하다.
  현재 fixture 기하가 모든 op8 선분을 막고 있다면 §4 (가)/(나)/(다) 보고는 원인을 잘못 짚은 보고가 된다.
- 예상 PASS / FAIL 조건(판정 전 고정): W38 op8 선분 전부가 출발·표적 행 사이에 다른 owner 띠를 끼고 있으면 전열 배치(lap532 §3.1) 재개 근거로 쓴다.
  일부만 끼고 있으면 (a) `BLOCKED` 보고를 확정한다.
- 이전 바퀴 검수(lap541): temp 8파일 SHA 앞자리(`1782ec3d`·`78d13c7d`·`337c73d7`·`c9594fca`·`2c2a6639`·`9cf118a8`·`cd7108d5`·`bd1854e7`)가 기록과 일치한다.
  W40 원시 `triggers.jsonl` `bd8836f1…`·`trace.jsonl` `24e871e6…` 일치, 원본 `b56986e0…` 불변(두 사본).
  `fun_471af0.dis` `0x472021`~`0x472049`를 다시 읽었다. `+0x216` word inc → `+0x218` word 비교 → 0 반환이다. 리셋은 칸 사이일 때만이다(`0x471e79`·`0x471f4c`). lap541과 같다.
- 변경 파일 / source fingerprint / 커밋: repo 비문서 변경 0. 문서만:
  `docs/work/active/G2_STRATEGY_W41_FRONT_LINE_LAP542.md`(신규, SHA `70d06e934954fbbdcfcf6298f346b86e6d697cf67d71909ff69a8a758cbcb9f5`), 이 파일, `docs/STATUS.md`, `docs/feedback/INBOX.md`(통지 추기), `loop/ESCALATE_SOL` §96. 커밋 0(uncommitted).
  도구·산출(temp) `temp/Syw2plus_patch/g2_capacity/20260923_lap542_strategy_w41/`: `band_crossing.py` `4960d817db…`, `band_crossing.json` `7e2b9bc759…`.
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기만). 게임 실행 0. W38·W40 T0 위치표를 읽기만 했다.
- 실행 명령: `python3 band_crossing.py`(W38 `t0_positions.json`·`waves.jsonl` 읽기), W40 T0 행 점유 집계(인라인 python, 읽기만).
- 측정값 / 판정:
  - **N199(신규):** T0 시딩은 anchor에서 행 우선으로 채워져 owner마다 x 0~99 전폭 가로 띠가 된다. 4 owner가 y2~19, 4 owner가 y52~72에 쌓인다.
    W38 op8 선분 49종(144건) **전부** 사이 행에 다른 띠가 있고, 사이 행 유닛은 최소 109기다(1×1 anchor 기준, footprint 제외라 과소). y20~51·y73~88은 T0 유닛 0이다.
  - N198과 충돌 없음: N198은 정적 BFS 경로 **존재**다. lap541 기전은 매 경계 틱의 **칸 진척**을 요구한다.
  - **판정 (c) 채택:** 전열 배치 W41 1회(짝 (0,1)·(2,3)·(4,5)를 빈 들판 두 줄로, 사이 7행, 짝 (6,7)은 같은 실행 대조). 출구 판별 필드 `+0x708`·`+0x216`·`+0x1f0` 등을 기록한다.
    W41은 S1 교전 경로의 마지막 실행이다. `ENGAGED_FRONT`가 아니면 예외 없이 `BLOCKED` 확정, 사용자 보고((가)~(다) + 신규 (라) 이동 후 공격 2단 입력).
  - streak 판정: lap540·541·542 연속 문서 → **계속**. 다음 회차는 W41 게임 실행이며, 실행 없이 끝나면 STOP.
- 회귀 / 남은 위험 / 독립 검수·사용자 승인 상태: 게임 실행 0, source 변경 0, 커밋 0. source 불변이라 `make check` 생략(N22). `SAFETY_PASS`·`CONTEXT_PASS`는 STATUS 검증 상태에 적는다.
  위험: 빈 행의 지형 통행성은 원시에 없다(`band_entry`로 정황만 본다). op5가 anchor 행에 60기를 한 줄로 놓는다는 것은 T0 관측 기반 추정이다(H20이 `ARM_FAIL`로 잡는다).
  N199는 W38 T0 기준이고 W40 T0 행 점유도 같은 구조였다. 사용자 승인 없음(통지, 번복 가능).
- 다음 한 가지: **work(Sonnet5)** — 판정 문서 §2 W41 게임 1회 foreground 완주 → 자기 라벨. 그다음 middle이 원시 재계산 후 §3 분기.
