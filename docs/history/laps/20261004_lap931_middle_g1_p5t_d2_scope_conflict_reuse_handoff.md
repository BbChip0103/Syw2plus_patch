# 2026-10-04 | lap931 | G1 P5-T D2 독립 검수·계측 범위 충돌 승격

- 실제 provider/model/effort / 지정 역할: Codex, 시스템 GPT-6; 정확한 model ID/effort 미노출.
  사용자 지정 중간 tier, solo 진단·계획·확인. 모델 전환·외부 모델 호출·게임 hands-on 수정 없음.
- 목표/가설: lap930 raw/current source를 독립 확인하고 full sentinel/viewport/visible/key/미러범위를
  보존하는 다음 실제 최소 수리를 정한다. D2 세 bucket이 상위 clip과 같은 측정 범위인지 확인한다.
- 예상 PASS/FAIL: build/source/SHA·snapshot/state·PNG 지표·sample seq/tick 재계산 일치;
  PT-c≤52.0ms·PT-d11439·B′연속2·현행source C1/C2/C3를 별도로 판정한다.
  구현/근거 충돌이면 사용자 지시대로 보존·ESCALATE_SOL·종료하며 임의 PASS/수리를 하지 않는다.
- 먼저 읽은 문서: loop/PROMPT.md→AGENTS/INBOX 최신/APPROVALS 반려→STATUS 전체→DESIGN1~4·
  MODEL_ROUTING→lap930 history/review card·lap929 handoff·lap925 strategy 범위, patch-validation skill.
  최신 DESIGN의 G2/G5 종료·G3중단·G4보류가 PROMPT의 과거 목표보다 우선한다.
- 변경파일(uncommitted): 이 lap 기록, `docs/work/active/G1_MIDDLE_W70_P5T_D2_SCOPE_HOLD_REUSE_HANDOFF_LAP931.md`,
  `docs/STATUS.md`, `loop/ESCALATE_SOL`. INBOX342/APPROVALS239는 압축·편집하지 않는다.
  소스/tests/probe/validator/binary/raw/baseline/원본·참고/카운터 변경·게임실행·커밋0.
- 원본SHA: EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` MATCH.
  hook0x466EA0 old `83ec148b44241c`,0x466540 old `515356578b7c2418` MATCH.
- sourceSHA: mirror `f27302c1633a00e911c668a2201bdb3d5d41380c61f6e40847f468d5f606fec1`,
  perf header `1c912f1b2b09803fc9dc8fc1c97fb4e52299fde9cdd57d30e15e0799120bce2f`,
  trace `8b61823e8a548ce6ac8cfdf514b19d78f389f53861ded3ba455b92c53b11b0f8`,
  tests `0fdabc3610a1e8c63f02c88c67b814d536560327d6f9a6f5fbfd8318e210bf32` MATCH.
- 후보/환경/fixture: 6 pair의 DLL SHA는 공유temp 재계산에 개별 기록했다. 5 build×48/current MATCH,
  원복한 stosb build는 mirror 한 파일만 달라 historical로 구분했다. 과거실행 wine9.0 격리
  game/prefix/display·비합성 save006·scene/카메라·snapshot parity를 확인했다.
  8 player records를 활성8인 부하증명으로 세지 않는다. 이번 회차 새로운 runtime 없음.
- 실행명령: `make doctor`, `make lint`, `make typecheck`,
  `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_g1_mirror2x.py`,
  `.venv/bin/python <공유temp>/20261004_lap931_middle_review/recalculate.py` 및 `supplement.py`.
  로그 `logs/gates/lap931-middle-{doctor,lint,typecheck,focused,recalculate}.log`.
- 독립 증거: 6DLL/12trace/manifest/PNG SHA MATCH, 입력502파일 SHA 기록,
  scroll5pair snapshot50개 각각5tick decoded state baseline/candidate 동일.
  PS3 V1 5755present 위반0, 현행5pair PNG25쌍 V2/s/q MATCH/PASS·activeScale2x PASS.
  B′2 drag 원본/후보 나란히 관찰, 단 캡처시간의 상태/animation 차이는 최종 입력효과 승인 아님.
- PT-c: GREEN DOWN52.551724/RIGHT51.379310, B′1 53.896552/52.379310,
  B′2 57.000000/50.620690ms. 각30sample seq/sim_tick/covered−stale MATCH·경계안.
  PT-c/B′연속2 FAIL, PT-d tinted11524/9569/9314(하한11439)에서 B′1/2 FAIL.
  effective p50 395960.5(82.4918%), stale74863.5, tinted_clip0·stale 감소 미입증.
- C: 이름C3는20초pair1회, histogram 중복0·count/meta 일치·drop0·ratio0.9974653168·p95Δ+11ms
  PASS(partial). 같은source C1/C2/C3 세 회의 대체가 아니다. old nearest BLOCKED는 기존 진단이다.
- QPC 값: fill82.9463%, alloc/free16.3846%, mask0.3306% 원문 MATCH. first30 DOWN
  fill20.777614/alloc4.149441/mask0.048690ms, RIGHT21.445948/4.283069/0.051928ms.
  fill 지배 단서는 수용, stosb normalized ticks/byte 약1.4583% 증가→원복 지지(인과/통계확정 아님).
- **FAIL_SCOPE_CONTRACT / ESCALATE**: 현재 mirror1343은 parent start=0,1348 clipped mask alloc의
  helper는 시간을 재지만 parent는1351 성공 뒤 재시작한다. 상위clip합에 이 alloc이 빠져
  "세 bucket이 상위와 같은 호출 경계" 전제와 구현이 어긋난다. 산술 residual0.34%를 exclusive
  remainder로 승인하지 않는다. 원인이 구체적인 계측 결함이고 raw 값 전사오류가 아니다.
  사용자 지정 근거충돌 중단으로 ESCALATE_SOL 생성. 손상/새 화면회귀/제품마감으로 재해석0.
- 진단·계획: capacity 재사용 FEASIBLE. 매 호출HeapAlloc 뒤 full fill 첫 쓰기는 first-touch 비용을
  포함할 수 있으나 실증은 없다. mask/identity를 자체copy하는 경로를 확인해 임시buffer 재사용 가능.
  full sentinel2개+mask·transactional growth/OOM·실패후 원복·소유권·visible/key/미러범위 회귀를
  구체화했다. 새로운 구현승인은 보류, 중간 tier가 직접 게임 수정하지 않는다.
- 검사: doctor(original verified)/lint/typecheck/focused25 PASS. full `make check` 및 fresh runtime
  **SKIP(user evidence-conflict stop)**. 과거1473passed를 현재fingerprint PASS로 승격하지 않는다.
  safety/context·최종파일SHA·현재fingerprint·입력불변감사는 STATUS에만 보강한다.
- 미검증: corrected timer/재사용 실제효과·B′2/C3회·PT-d/tinted_clip·stale·최종입력·HD≥90%·
  GDI·두번째장면·동적API실패/강제rollback·G1 사용자승인. G1/P5-T HOLD, milestone 전환/마감0.
- 다음 인계: 승격Sol이 parent/bucket 불일치와 제한부QPC 판정을 독립확인한 뒤 card§3의 work
  최소수리로 연결한다. 경계·52ms·하한·validator·미러범위 완화/새strategy계획은 하지 않는다.
  구현은 work tier, GREEN→B′연속2→C1/C2/C3→Fast→새middle 순서. 이번 session은 여기서 종료한다.
