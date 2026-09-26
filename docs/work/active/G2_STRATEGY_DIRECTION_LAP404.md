# G2 전략 방향 — 미검수 런타임 계보 승격 절차와 잔여 큐 (lap404 strategy)

- 발행: 2026-09-20, strategy 세션(Claude Code claude-fable-5). 게임 코드/바이너리 변경 0, 실행 0, 커밋 0.
- 이 문서는 범위·우선순위·검증 기준 결정문이다. 실제 실행은 middle/work 회차가 수행한다.

## A. 사실 판정 — 대규모 미검수 런타임 계보가 존재한다

`docs/history/laps/20260920_lap410_g2_pool1210_runtime_spike.md` 와
`20260920_lap412_g2_full_capacity_lists_runtime.md` 두 기록이 다음을 주장한다:

1. 풀 재배치 N=1210/1250 후보의 실제 Wine 실행에서 slot≥1200 생성→관측→사망/해제→재사용 스파이크 PASS
   (INBOX 2026-09-20 00:33 최우선 지시의 1차 성공 기준 그대로).
2. 6개 용량의존 영역 전면 재배치(N=4001) + 활성리스트 alias 2건·category-B count 결함 2건 발견·수리.
3. 8 owner 전비 5000, 4000 live에서 24k + 144k 연장 soak 무결성 PASS.
4. 확장 배열 save/load 왕복 + versioned header(`S2P1N4K1`) + stock save fallback 실제 왕복 PASS.

strategy 스팟 체크(이번 lap): 신규 모듈 10개(`patches/population/full_tail_relocation_*`,
`g2_full_*`, `verify_g2_persistence_artifacts.py` 등) 실재, 커버리지 게이트형 테스트
`test_n1250_data_section_covers_every_relocated_region` 실재, 런타임 산출물 2건 해시 일치
(`n4001_integrity_soak_summary.json`=`62e6cb71…`, `postload_integrity_soak_summary.json`=`667fdeae…`,
내용도 8×5000/4000 live/24k PASS와 정합). **스팟 체크는 2단 독립 검수가 아니다.**

## B. Provenance 결함 N18 (원문 보존, 고쳐 쓰지 않음)

- 러너 `loop/.lap_counter`는 이번 세션 시점 404(현재 405)인데 두 기록은 lap410/412를 자칭한다.
  lap403~409·411 번호의 기록 파일은 없다. **자칭 lap 번호는 러너 카운터와 불일치**하며,
  PROMPT는 "상세 기록 파일의 lap 번호도 카운터 값 사용"을 요구한다.
- STATUS lap402 시점 "다음 한 가지"(W5 §1 수리→G-c→W4 §5)와 두 기록 사이의 중간 단계
  (W5 수리 자체의 검수 기록)가 파일로 없다. lap410 기록이 수리 결과를 함축하나 명시 검수가 없다.
- 처리: 두 기록의 **번호를 고쳐 쓰지 않는다**. 이후 인용은 "자칭 lap410/412(실제 lap 번호 불명)"로
  한다. 결함은 이 문서와 lap404 기록에 남긴다. 수치·해시 증거의 진위와는 독립 문제다.

## C. 다음 한 가지(승인 불필요) — middle 독립 검수 카드

다음 middle(Opus5/high) 회차는 자칭 lap410/412 계보를 독립 검수한다. 수용 기준:

1. 원본 EXE 2경로 재해시 불변, `make check` rc0, `SAFETY_PASS`.
2. 후보 재현: 기록된 최종 후보 SHA(`c3bd799f…`(N=1250), `20b95a94…`(N=4001+5000+owner1200),
   `4331d9cd…`(persistence compat))를 현재 소스에서 재생성해 byte-equal 확인. N=1200 항등 유지.
3. 커버리지 게이트: 전면 재배치 layout에 대해 "재배치 블록 전 바이트가 어떤 섹션
   `[VA,VA+VirtualSize)` 안"(lap402 G-c 요구)이 pytest 앵커로 강제되는지 확인. 없으면 REJECT가 아니라
   게이트 추가를 work에 지시한다.
4. 런타임 산출물 해시 대조(soak jsonl/summary/persistence 검증 JSON 전건)와
   `python3 -m patches.population.verify_g2_persistence_artifacts <run-dir>` 재실행 PASS.
5. 수리 2건(active_base-2 alias fixup, `0x004A3692` category-B self-count)의 old-byte 경계·비중첩·
   N=1200 무영향을 바이트로 재유도.
6. 판정은 항목별 ACCEPT/REJECT. 게임 재실행은 이 검수의 필수가 아니다(정적+산출물 재검증).
   ACCEPT 시에도 아래 D의 잔여 갭 때문에 제품 완료 선언은 금지.

## D. 검수 ACCEPT 후 우선순위 큐 (strategy 확정)

1. **P1** marked compat(`4331d9cd…`) 경로를 near-4000 live 규모에서 반복(기존 382-unit만 통과).
2. **P2** diagnostic bridge seeding을 원본 생산/재생산 명령 경로 커버리지로 대체
   (AGENTS "원본 명령 우회 성공은 부족" 조항의 직접 요구; 전투/사망은 이미 발생).
3. **P3** strict over-cap/전비 랩 — 사용자 되물음 2건(INBOX 되물음 참조) 답변 대기. 대기 중 착수 금지,
   독립 작업은 P1/P2로 진행.
4. **P4** 지원되는 LAN 직렬화/결정론.

G1/G4는 사용자 지시대로 후순위 유지, G3 중단 유지.

## E. ESCALATE_SOL §9.6 부분 판정 (strategy 권한 내)

- 분기 A(cap≤4095)는 lap395 반례로 폐기 **확정**(이미 무효였음, 재확인).
- 분기 B(장부 32-bit 확장) 대 분기 C(도달성 판정 후 5000 유지)는 **사용자 되물음 2로 전환**한다.
  자칭 lap412의 144k 실측(라이브 used ≤5000, 일시 reserved 초과는 원본 고유)은 C를 지지하는
  증거이나, 이전(transfer) 집중 펌프 도달성 UNKNOWN은 그대로다.
- 합격기준은 (b)(생산 gate 무결성 + 장부 랩 없음) **유지 확정**. (a)는 lap389 NO_GO 그대로.
- 목표 숫자 5000 변경 없음(사용자 권한). escalation 파일은 열린 채 두고 §11로 이 판정을 추기했다.

## F. 이 방향의 실패 조건

middle 검수가 항목 2/4/5 중 하나라도 REJECT하면 D 큐는 동결하고, REJECT 근거를 가진 수리 카드를
먼저 발행한다. 검수 결과와 무관하게 자동 커밋/원격/서비스/사용자 승인 대체는 없다.
