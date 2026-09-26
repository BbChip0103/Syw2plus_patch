# 2026-09-23 | lap 543 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, work (지정: STATUS lap542 "다음 한 가지").
- 가설 / 사용자 관찰: 카드 `docs/work/active/G2_STRATEGY_W41_FRONT_LINE_LAP542.md` §2 — N199(lap542)에
  따르면 T0 시딩이 지도 전체를 채우는 가로 띠라서 W38 op8 선분 전부가 다른 띠를 가로질러 추격 포기(`0x472042`)를
  유발했다. 전투 유닛(type2)만 빈 들판에 두 줄로 마주 세우면(사이 7칸) 실제로 접근·교전(`hit_attr`)이
  일어나는지가 이번 probe의 가설이다.
- 예상 PASS/FAIL 조건: 카드 §2 판정표 — 전열 3짝 중 `hit_attr` 소스가 있는 짝 ≥2면 `ENGAGED_FRONT`,
  아니면 `EXIT_C`/`EXIT_V` 과반에 따라 `NO_ENGAGE_C`/`NO_ENGAGE_V`/`NO_ENGAGE_UNRESOLVED`. H20 배치 확인
  (전열 owner 6개 anchor 행 ±1행, 짝 사이 7행 유닛 0)을 어기면 `ARM_FAIL`/`PROBE_VOID`, 하네스·배치 결함일
  때만 1회 재시도(카드 §3, lap535 §2 경계 5).
- 변경 파일 / source fingerprint / 커밋: repo 소스 변경 0(불변, N22 — 전체 `make check` 생략 근거).
  하네스만 `temp/.../20260923_lap543_w41_front_line/w41_run.py`(W40 `w40_run.py` SHA
  `6417a63ed3d0d459c62c968dc228828d4ecabfcf9236b81eb1a93207bf6c646e` 확인 후 파생, H17~H20 적용,
  최종 SHA `a6ea50fb02129af28af3bc22b6f341e418ee02eb26ab892ba105ff95bdce8ba8`). 커밋 없음(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / 활성 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(양 시도 전후 불변). 후보(N=4001
  persistence-compat) `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(lap524 핀과 일치).
  격리 Wine prefix, Xvfb `:6536`. 활성 8owner, 각 자원 100만/100만, cap5000. 지도 100×100.
  fixture: 허용목록 {5,7,46,2} 시딩(type5×100, type7×25, type2×60, type46×20/owner), 시딩순서 W37 확정
  (생산자 마지막). type2만 전열 anchor(H17): 짝(0,1) y24/32, 짝(4,5) y76/84는 카드 원문 그대로,
  짝(2,3)은 시도1에서 카드 원문 y40/48 사용, 시도2(재시도)에서 y42/50으로 조정(아래 판정 참고).
  A1 used=4,950×8(양 시도 모두 [4900,5000] 안), A8' 4종 보유·X≥10·최대비중 0.707 전부 PASS(양 시도).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=.../Syw2plus_patch timeout 2850 python3 w41_run.py`
  (foreground 동기, 각 시도 약 30~35초, 45분 상자 안, 2회 모두). gate 3파일 SHA(`runtime_bridge.c`
  `3555848d…`, 핀 테스트 `2a8aa4f7…`, op8 계약 테스트 `0939f5b6…`) W40 §0 값과 일치 확인 후
  `checks/safety.sh check` → `SAFETY_PASS`, 표적 14 passed, 이어서 실행.
  산출물: 시도1(카드 원문 anchor) `temp/Syw2plus_patch/g2_capacity/20260923_lap543_w41_front_line/attempt1_arm_fail/`
  (`run_summary.json`·`t0_positions.json`·`seed_receipts.json` 등). 시도2(재시도, anchor 행 조정)
  `temp/Syw2plus_patch/g2_capacity/20260923_lap543_w41_front_line/`(같은 파일명, 현재 위치).
- 측정값 / 판정: **양 시도 모두 `verdict=ARM_FAIL`, `self_label=PROBE_VOID`, `arm_fail_reason=["H20_front_placement_failed"]`.**
  두 시도 모두 실제 게임을 45분 상자 안에서 완주해 T0까지 도달했으나(시딩 `used`=4,950×8 전부 성공, A1/A8' 전부
  PASS), H20 배치 확인에서 pair(2,3)의 **자기 스필오버가 그 짝의 "사이 7행" 안으로 들어가** `ARM_FAIL`이 됐다:
  - 시도1(카드 원문 anchor y40/48): owner2의 type2 60기 중 47기만 row40(x 20~99)에 들어갔고 나머지 13기가
    row41(gap 41~47의 첫 행)로 스필오버. `t0_positions.json`(attempt1) 원시 확인: row24(owner0)·row48(owner3)·
    row76/84(owner4/5)는 60기 전원이 스필오버 없이 들어갔지만 row32(owner1, 52+8 스필오버, 짝 밖 방향이라
    무해)·row40(owner2, 47+13 스필오버, 짝 안쪽 방향이라 유해)만 부족했다.
  - **N200(신규, 시도2가 확정) — H20의 두 조건은 구조적으로 충돌한다.** 시도2에서 anchor를 y42/50으로
    2행 옮겼는데도(gap 43~49 재계산) 이번엔 owner2의 60기 중 **단 1기**만 row43(gap 첫 행)으로 스필오버해
    똑같이 `ARM_FAIL`이 났다. 스필오버가 13기→1기로 줄었어도 결과는 동일했다 — 이는 특정 행의 지형 문제가
    아니라, "자기 anchor 행 ±1행 허용"과 "사이 7행(=anchor+1부터)은 0이어야 함"이 **anchor+1 행에서 항상
    겹친다는 카드 §2 H20 자체의 구조적 긴장**이라는 뜻이다(pair의 "위쪽" 멤버 쪽에서만 발생 — 스필오버가
    관측된 방향은 두 시도 모두 +y뿐이었다. "아래쪽" 멤버(owner1, owner3, owner5)의 스필오버는 관측된 적 있어도
    (owner1, 시도1) 파트너 반대 방향이라 무해했다). 60기를 정확히 1행에 담는 것이 **완전히 성공하지 않는 한**
    이 조건들은 원리적으로 공존할 수 없다.
  - 카드 §3 경계대로 **1회 재시도(anchor 행 조정)를 소진**했고 두 번째도 같은 실패 계열이므로 **S1 op8
    교전 경로를 `BLOCKED`로 확정**한다(lap542 §1 L2 "예외 없이"). 전열 배치 자체(파동 issue)는 한 번도
    실행되지 못했다 — op8이 한 건도 발행되지 않아 `hit_attr`/`exit_class`/`band_entry` 등 §2 판정표의
    실측치는 **존재하지 않는다**(수집 대상 자체가 없음, 조작·은폐 아님).
  - A5 무결성(over5000·live/count 불일치·tick역행 등) 검사 항목은 T0 이전 중단이라 실행되지 않았다(N/A,
    실패 아님). 원본 두 시도 모두 불변, 잔류 프로세스 0.
- 회귀/남은 위험/독립 검수: middle 독립 재계산 아직 없음(다음 회차). N200은 이번 lap의 신규 관측이며
  이전 middle/strategy 판정(N181~N199)과 충돌하지 않는다 — N199(지형/띠 문제)와 N200(H20 규칙 자체의 구조적
  긴장)은 서로 다른 층위의 문제다. `w41_run.py`에 추가한 `compute_w41_label`/H20 검증 로직은 실행 전
  합성 트리거로 단위 검증했다(hit_attr·exit_class·band_entry 계산, `x_seed_anchor` 라우팅 — 세 케이스
  ENGAGED_FRONT 후보/EXIT_C/미해결 조합 확인, `NO_ENGAGE_C` 산출 확인). gdb 하드웨어 watchpoint(W40 H12/H14~H16
  기계)는 카드 H19 지시대로 이번 run에서 호출되지 않았다(`GDB_STEPS_ENABLED=False`, `result["H19_gdb_steps_enabled"]`
  로 기록). W41 자체가 op8 발행 전 단계에서 막혔으므로 N192(장거리 접근/추격 포기) 가설은 이번 lap으로
  검증도 반증도 되지 않았다 — 미해결로 남는다.
- 다음 한 가지: **middle(Opus5.5)**: 양 시도의 `t0_positions.json`/`seed_receipts.json`/`run_summary.json`을
  원시로 재계산해 H20 위반(시도1 13행 스필오버, 시도2 1기 스필오버)과 N200(구조적 충돌)을 독립 확인한다.
  카드 §3 `NO_ENGAGE_*`/`PROBE_VOID·BLOCKED` 재시도-소진 행과 §1 L2("예외 없이 BLOCKED")에 따라 **S1 op8
  교전 경로를 `BLOCKED` 확정**하고 §4 선택지((가) (ㄴ) AI 예외 / (나) "8인"=사람 슬롯 / (다) S1 트랙 중단 /
  (라) 이동 후 공격 2단 입력)로 사용자에게 보고한다. 이번 lap은 출구 분포·`band_entry` 실측치가 없다는 점을
  §4 보고에 명시해야 한다(전열 배치가 op8 발행 전 gate에서 막혀 교전 자체를 시도하지 못했다는 뜻).
  N200(H20 자체의 구조적 긴장)도 함께 고지한다.
