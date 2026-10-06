# 2026-10-04 | lap932 | G1 P5-T 기존 계측 충돌 확인·승격 인계 유지

- 지정 역할: 사용자 명시 **일반 middle**(진단·계획·확인). 실제 provider Codex/GPT-6,
  정확한 model ID/effort는 세션에 미노출. 승격 역할/모델 전환/외부 모델 호출을 주장하지 않는다.
- 지시 순서: PROMPT① 합격 기준 → ② AGENTS·INBOX 최신·APPROVALS 반려·STATUS 전체·DESIGN1~4·
  MODEL_ROUTING → ③ 안전/역할/중단 조건 → ④ 이전 lap931 범위 근거 확인 → ⑤ 보존 → ⑥ 종료 안전검사.
  patch-validation의 원본 보호/증거 구분을 적용하되 사용자 근거충돌 중단이 전체Fast보다 우선한다.
- 목표/가설: STATUS가 요구하는 승격 확인의 입력인 lap931 timer 결함이 현재 source에도 존재하는지
  좁게 확인한다. 새 비용 가설·장기 계획·게임 구현은 하지 않는다.
- 예상 판정: source/pin SHA·정확한 old bytes·parent/helper 순서가 lap931과 같으면
  HOLD_SCOPE_CONTRACT와 기존 승격 인계 유지. 재실행/성능/제품 PASS로 해석하지 않는다.
- 현재 lap: runner 소유 `loop/.lap_counter` 실제 값 **932**. 사용자 첨부 runtime의 lap931은 이전
  증거로 구분한다. counter를 쓰거나 복원하지 않는다. STOP 파일은 시작 시 없었다.
- 독립 확인: parent는 `g1_mirror2x.c:1343`에서 start=0, clipped mask alloc은1348,
  parent 재시작은 성공 뒤1351. helper1165~1169는 alloc을 QPC bucket에 누적한다.
  성공/NULL 실패 모두 이 할당이 parent clip 합에서 누락된다(NULL은1395에서 다음 timer 시작).
  따라서 D2 review의 동일 호출 경계 전제와 구현은 충돌하며 단순 해시/서술 전사 오류가 아니다.
- 판정: **HOLD_SCOPE_CONTRACT / ESCALATE 유지**. 일반 middle 지정이므로 STATUS의
  "승격Sol"을 맡았다고 가정하거나 이전 marker를 처리 완료로 제거하지 않는다.
  fill 지배 단서는 기존 제한부 근거로 보존하되 residual의 exclusive 분해 승인은 보류한다.
- 변경(uncommitted): 이 lap 기록·docs/STATUS.md·loop/ESCALATE_SOL 및 이전 marker byte-exact 보존본
  `docs/history/20261004_lap932_prior_escalate_sol_byte_exact.txt`.
  보존본 SHA256 `6ac2e72c28297818cd2870f1c3a5e3f6f0c73d451adcf47b5f2de19be951dea9`.
  INBOX342/APPROVALS239/STATUS85는 기록 전 soft limit 이내여서 압축하지 않았다.
  source/tests/probe/validator/게임binary/원본·참고/raw/golden 변경·게임실행·커밋0.
- source SHA: mirror `f27302c1633a00e911c668a2201bdb3d5d41380c61f6e40847f468d5f606fec1`.
  lap931 original_pins의 구현6개 SHA MATCH. build/후보 DLL을 이번 회차에 생성하지 않았다.
- 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  비합성 save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` MATCH.
  PE section에서 old bytes0x466EA0=`83ec148b44241c`,0x466540=`515356578b7c2418` 재판독 MATCH.
- 실행/증거: 공유temp `20261004_lap932_middle_scope/verify_scope.py` 실행,
  `scope_confirmation.json` SHA256 `2c8e95c7cc350b93ad06c5c4ddad7d709940cbae72e5eaaae1204eb661dc2f86`.
  선정 입력15파일 읽기 전후 변화0, lap931 재계산 JSON SHA도 MATCH.
  기존502파일 전체/raw runtime/state/PNG 재검수는 반복하지 않았으며 이를 새 PASS로 세지 않는다.
- fixture/수치 한계: 이번 runtime/활성인원/군대 측정 없음. 이전 save006·Wine 격리 pair의
  B′ PT-c FAIL·tinted9569/9314<11439·tinted_clip0·C20초1pair 한정 결과를 그대로 보존한다.
- 검사: fresh fullFast·DLL build·patch/restore·격리runtime **SKIP(user evidence-conflict stop)**.
  과거 lap930 Fast1473 PASS는 현재fingerprint Fast/제품 승인 아님. doctor·종료safety/context 및
  입력불변 확인 결과는 STATUS에만 보강한다. 손상/성능 원인을 first-touch로 확정하지 않는다.
- 다음 한 가지: **실제 승격Sol이 lap931 §2와 이번 범위 근거를 확인하고 기존 §3 work 계약으로 연결**.
  새 work는 timer 범위복구+full sentinel2개/mask capacity 재사용을 최소 구현하고 OOM/partial/growth/
  잔존byte/원복 회귀→같은source GREEN→B′연속2→C1/C2/C3→Fast→새middle을 수행한다.
  52ms/하한/validator/mirror 범위 불변. 이미 발행된 FEASIBLE 수리를 재계획으로 되돌리지 않는다.
- 미검증: 수리 효과·정확한QPC분해·PT-c/PT-d·stale 감소·HD≥90%·GDI·최종입력·두번째장면·
  G1 사용자승인. 마일스톤/단계 마감 없음, G2/G5 종료·G3중단·G4보류 유지. 사용자 stop 조건으로 종료한다.
