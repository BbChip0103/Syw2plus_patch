# 2026-09-23 | lap 518 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / work(실무), 카드
  `docs/work/active/G2_BUILD_ORDER_FUNNEL_PROBE_LAP517.md`(W32, lap517 middle 발행, `ESCALATE_SOL`§75).
- 가설 / 사용자 관찰: lap517이 재무장 스케줄러(`0x43F5D0`, owner당 8 tick 1회·`+0xD32==0`이면
  `rand%20`으로 시작·100 tick 쿨다운)를 해독했으나 관측 건물 순증가 9~18채가 이론 시작 횟수(≈91/24k)의
  10~20%뿐인 이유(점유/시작부족/실행실패/완공실패 중 어느 단계인지)는 미판별이었다. W32는
  `+0xD32`(오더 종류)·`+0x33AC`(시작 tick)·`+0x3A70`(발부 tick) 3필드를 추가 표본해 카드 §3의 사전
  고정 판정식으로 손실 단계를 가른다.
- 예상 PASS / FAIL 조건: 카드 §3 5개 라벨(OCCUPANCY_BOUND/START_SHORTFALL/EXEC_FAIL_BOUND/
  COMPLETION_BOUND/CADENCE_BOUND) 중 하나 또는 반증조건 성립 시 `MODEL_REFUTED`(라벨 미부여, 원시 보고).
  게임실행 fault 0·원본 SHA 불변·소스 불변이 실행 성공 조건.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 source 변경 0(patches/·tools/·tests/
  전부 미변경). 신규 파일: `analysis/memory_maps/ai_build_order_funnel_probe_lap518_20260923.md`,
  이 lap 기록, `docs/work/active/G2_BUILD_ORDER_FUNNEL_PROBE_LAP517.md` §6 추기, `docs/feedback/INBOX.md`
  ·`docs/STATUS.md`·`loop/ESCALATE_SOL` 갱신(문서만). 레포 밖 산출물:
  `temp/Syw2plus_patch/g2_capacity/20260923_lap518_work_w32_build_funnel/`
  (`w32_build_funnel_run.py`=lap516 `w31_build_pace_run.py` 복사+M-1/M-2 추가, 원본 미수정). 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(전후 불변), 후보(N=4001 persistence
  compat) `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(W29/W31과 byte-identical),
  브리지 DLL `244c13265c925d7467d778cb9e8723995709ec08b941c3054507743663cdcc9a`. 격리 Wine prefix/Xvfb
  `:5032`(전용, 다른 프로세스 미접촉). 8 owner 전원 활성·nation 1(조선), 지도 140×140, op7 자원 각
  1,000,000, `+0x2010`=1,200(로스터 cap).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 w32_build_funnel_run.py --display :5032`(포그라운드
  동기, 세션 종료 없이 완주). 로그·산출물
  `temp/Syw2plus_patch/g2_capacity/20260923_lap518_work_w32_build_funnel/`(`orchestrator.log`,
  `samples.jsonl` SHA256 `b695365cd4416ec6a5256000327ada285bea46eef2f003a0a9bf9935f7c1a94f` 1,438줄,
  `build_funnel_summary.json` SHA256 `e473cc4f01df0c64e7969385b1c3464bd32ca51f04d73395ec2e38b48e5c7eb9`,
  `run_summary.json` SHA256 `13b4ccc280a80ca7515a8e60e1c0e3cff5c9f4c9e56cb879ce3240af29778b24`).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): tick 24,005 완주(`stop_tick_reached`), fault 0, `U3_pass`
  (live/count 불일치 0/1,438), `any_owner_used_over_5000=False`. owner별 `f_idle` 0.887~0.915(≥0.5,
  OCCUPANCY_BOUND 불성립) · `S`(시작) 83~102 vs `S_exp` 81~83(비율 1.02~1.25, <1.3배) · `S_short_gap_defects`
  8/8 전원 0건(쿨다운 위반 없음) · `C`(발부) 11~27, `C/S` 0.125~0.307(<0.5, EXEC_FAIL_BOUND 조건 성립) ·
  `B`(건물 순증가) 9~18·`D`(감소) 전원 0, `B/C` 0.519~0.818(≥0.5, COMPLETION_BOUND 불성립). **카드 §3
  반증조건②("`+0xD32==1`이 아닌 표본에서 `+0x33AC`가 바뀜")가 8/8 owner에서 성립**(시작의 26.6~44.3%,
  23~43/83~102건) ⇒ 정식 라벨 미부여, **판정 = `MODEL_REFUTED`(원시 보고, 방향성은 EXEC_FAIL 쪽)**.
  N144 결정성 대조: lap516과 max_used_by_owner·최종 건물 수 불일치 0/8 = **PASS**(같은 시드/fixture/후보가
  동일 궤적 재현). 원본 SHA·`control_executor.c` SHA 전후 불변, source_unchanged=True.
  `checks/safety.sh check` → `SAFETY_PASS`. `make check` 미재실행(제품 source 불변, 2026-09-20 21:58 지시
  면제 규칙 적용, 직전 819 passed 유지). 이번 회차에 source를 바꾸지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(원본/후보/제품 source 전부 불변).
  남은 위험: 반증표본이 스케줄러 8-tick 이하의 초고속 부지/일꾼 실패 때문인지, SCH §2 모델 자체의 결함
  때문인지 이 카드 범위로는 미판별(§5 "이 카드가 허가하지 않는 것"이 고빈도 재계측·로직 변경을 막음).
  이 lap은 work 자기 결과이며 독립(다음 middle) 검수 대기. Q9·Q8((ㄱ)/(ㄴ)/(ㄷ))·Q7-B·"8인" 정의는
  전부 사용자 전권 대기 불변, 이 lap이 고르지 않음.
- 다음 한 가지: middle(Opus5.5)이 `samples.jsonl`/`build_funnel_summary.json` 원시 비참조 재집계로
  반증표본·S/C/B 수치 재현 후, EXEC_FAIL 방향성만 기록하고 카드를 닫을지 추가 계측이 필요한지 판정한다.
