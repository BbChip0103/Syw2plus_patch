# 2026-09-21 | lap 444 | 목표 G2 — §27 fixture 범위 strategy 판정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5` / strategy(큰 방향).
  게임 코드 미변경, 문서 산출물만.
- 가설 / 사용자 관찰: lap443 (T2) ACCEPT 이후 "144k 연장은 전비5000 도달 근거와 충돌" —
  fixture 범위((가) 원본 생산 vs (나) 직접 시딩)를 strategy가 정해야 함(`ESCALATE_SOL` §27).
- 예상 PASS / FAIL 조건: 판정 전 lap442 원시 표본 재계산이 lap443 수치와 일치할 것(불일치 시
  판정 보류·재검수 지시).
- 변경 파일 / source fingerprint / 커밋: `docs/work/active/G2_STRATEGY_FIXTURE_SCOPE_LAP444.md`(신규),
  `loop/ESCALATE_SOL`(§28 추가), `docs/STATUS.md`, 본 기록. 제품 source 변경 0(N22 — 이번 회차
  source를 바꾸지 않았다). 커밋 0(LOOP_ALLOW_COMMITS 기본0).
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `b56986e0…c9c08a8ac`(lap442 summary 전후 불변 확인),
  신후보 `a10024de…`(lap442 재빌드). 이번 회차 게임 실행 0.
- 실행 명령 / 로그: lap442 `samples.jsonl` 721표본 직접 재계산(인라인 python, 요약본 비참조) —
  samples 721 / tick 16→24,030 단조 / max used `[20,570,1183,1111,620,1333,1698,1466]` /
  owner0 단일값 `(20,2)`. `checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정: **재확인 PASS(불일치 0)** → §27 판정 확정: **(나) 시딩 선행, (가) 합격 경로**.
  경계: (나)는 부분 증거 한정·gate-legal·혼합 구성 의무, 144k 카드 금지 유지(해제 = (나) ACCEPT
  ∧ (가) fixture 성립), (가)는 설정 조정만이며 AI 코드 변경 필요 시 재에스컬레이션. W21 필수
  Step: owner0 N56 선행 확인 / cap 근처 시딩 soak + RSS(N57) / 신후보 저장·로드 왕복(구후보 증거
  대체) / lap413·stock 대조표 **fail-closed**(N58 두 번 재발로 판정 조건 승격) / 동기 실행·자체
  lap 기록 의무.
- 회귀 / 남은 위험 / 검수 상태: 게임 실행 0이라 새 런타임 위험 없음. 이번 회차 포함
  implementation-unchanged 연속 2회(lap443 middle→lap444 strategy)이나, 이 회차 자체가 PROMPT ③이
  요구하는 strategy 판정이므로 규칙 내이며 다음 회차부터 실행 증거 경로가 열린다. 다음 middle이
  W21 발행 시 이 카드 경계 준수를 검수한다.
- 다음 한 가지: middle이 `G2_STRATEGY_FIXTURE_SCOPE_LAP444.md` §3대로 W21 카드를 발행한다.
