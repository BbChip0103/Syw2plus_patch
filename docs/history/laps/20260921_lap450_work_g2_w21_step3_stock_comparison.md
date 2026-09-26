# 2026-09-21 | lap 450 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / **work**(실무).
  세션 지시("일반 작업자")에 따라 구현/실측만 수행하고 계획·컨펌은 하지 않았다.
- 가설 / 사용자 관찰: 사용자 관찰 없음. INBOX·STATUS의 "다음 한 가지"를 그대로 따랐다 —
  `docs/work/active/G2_CAP_PROXIMITY_SEEDED_SOAK_LAP445.md` §11 순서①: Step2(저장/로드 왕복)
  전에 §7 Step3 `lap413_stock_comparison.md`를 **게임 실행 없이** 만든다(N66 — W19 Step4/W20
  Step3/W21 Step3로 3회 연속 누락, 이번이 없으면 다음 middle이 내용을 보지 않고 자동 REJECT).
- 예상 PASS / FAIL 조건: 카드 §7 최소 컬럼(축|lap413 구후보|lap413/stock 대조군|이번 신후보)과
  최소 행(fault tick 11,928 통과 여부·도달 tick·표본 수·max live·owner별 max used·
  fault/crash/read failure 수·fixture)을 전부 채운 파일이 새 run 디렉터리와 lap448 run
  디렉터리 양쪽에 동일 내용으로 존재하면 PASS. 값을 모르면 `UNKNOWN`으로 채우되 행을 비우지
  않는다(카드 명시).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **제품 코드/테스트/도구 source
  변경 0건.** 신규 파일만 추가:
  - `temp/Syw2plus_patch/g2_capacity/20260921_lap450_step3_stock_comparison/lap413_stock_comparison.md`
  - `temp/Syw2plus_patch/g2_capacity/20260921_lap448_w21_step1_cap_proximity_soak_root_recovery/lap413_stock_comparison.md`
    (위와 SHA256 동일 — `1a439f094f52ceccc904a01fc7169fc6fbc80533978984902b5bf787e6a7d577`)
  - `docs/STATUS.md` 압축·「검증 상태」·「다음 한 가지」·「바퀴 기록」 갱신(원문은
    `docs/history/laps/20260921_status_lap450_precompaction.md`, SHA
    `63be3a57b0b4ed48a1f58b13ef587731982ce9dedb51815b2f0854927ece4fbb`, 130줄, 보존)
  - 이 lap 기록 파일.
  커밋 없음(`LOOP_ALLOW_COMMITS=0` 기본 유지, 사용자 허용 없음).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: **이번 회차는 게임을
  실행하지 않았다.** 표에 인용한 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  구후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`,
  stock 대조군 `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`,
  수리후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`는
  전부 기존 `run_summary.json`/`progress.json`에서 인용했고 이번 회차에 재검증(rehash)하지
  않았다 — 재실행이 없어 변조 위험이 없기 때문이다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3`으로 기존 `samples.json`/`samples.jsonl`
  4개 파일(lap413 candidate run1·repro2, lap413 stock control, lap442, lap448
  root_recovery)을 읽어 `owner별 max used`/`max live`/`표본 수`를 전 표본 기준으로
  재계산했다(1회성 인라인 스크립트, 파일로 저장하지 않음 — 순수 집계라 재현은 이 lap 기록의
  수치와 원본 samples 파일 대조로 충분하다). `checks/safety.sh check` → `SAFETY_PASS`.
  통합 `make check`는 source 미변경(N22)이라 생략했다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **PASS** — 카드 §7 최소 컬럼/행을 전부 채운 `lap413_stock_comparison.md`를 두 디렉터리에
  동일 해시로 배치했다. 핵심 수치: lap413 구후보는 tick11,928에서 두 run 모두 동일 주소
  page fault(`read 0x00338400 @ 0x00414133`, FAIL, max live468, owner최대used1208) — stock
  대조군(N=1200)은 fault 없이 tick13,804 정상 종료(max live405, owner최대1006, 전 표본
  기준 재계산이라 통합 요약의 `best_owner` 스냅샷과 다름, 둘 다 표에 남김) — lap442
  수리후보(비시딩, 구식 goal이라 owner0 비활성)는 24k tick 통과하되 owner최대1698(T2,
  5000 미도달) — lap448 수리후보(gate-legal 시딩, 신goal 8인 전원 AI)는 24,029tick·
  owner최대5000·fault0(`CAP_PROXIMITY_STABLE`). fault/crash/read-failure 수 행 중
  "read failure"는 이 probe들에 전용 카운터가 없어 **UNKNOWN(미계측)**으로 명시하고 행을
  비우지 않았다(카드 지시 그대로).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **이 표는 서술 의무 이행이며 새 판정을
  만들지 않는다** — U0~U3은 lap449가 이미 ACCEPT했고 이번 lap은 그것을 뒤집거나 강화하지
  않는다. 다음 middle이 원시 samples 파일을 **비참조 재계산**해 표 수치를 독립 검수해야
  ACCEPT로 닫힌다(이번 lap의 수치를 그대로 신뢰하지 말 것). 사용자 승인 대상 아님(마일스톤
  아님). 남은 위험: lap442/lap413/stock 세 축이 구식 goal(owner0 비활성)이라 "8인" 비교가
  아니라 "7인 vs 8인(lap448만)" 비교라는 점을 표 본문에 명시했다 — 이후 인용 시 축약하지
  말 것.
- 다음 한 가지: 다음 middle이 이 표를 비참조 재계산으로 독립 검수(ACCEPT/REJECT). ACCEPT면
  카드 §11 순서②(Step2 — 신후보 `a10024de…` 저장/로드 왕복, tick 역행 증거 필수)로 진행하기
  전에 순서③ 계측 수리 2건(N65 verdict 식에 `U3_pass` 반영, `/proc/<pid>/smaps_rollup`
  `Private_Clean`/`Private_Dirty` 표본 추가)을 먼저 스크립트에 반영한다. 144k 카드 발행은
  (U5) 미실행으로 계속 금지.
