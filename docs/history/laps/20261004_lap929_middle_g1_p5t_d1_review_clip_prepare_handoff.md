# 2026-10-04 | lap929 | G1 P5-T D1 독립검수와 clip 준비 비용 인계

- provider/model/effort: Codex API, 지정 middle tier. 실제 모델ID/effort 조회 수단이 없어 특정 모델명·설정 성공을 주장하지 않는다. solo·subagent0.
- 가설: lap928 REP STOS는 byte 범위/값을 유지하며 clip 준비 비용을 줄였지만 B′ 연속2와 PT-d는 아직 만족하지 않는다.
- PASS/FAIL 식: 보호SHA/old bytes, build48/current·DLL/raw SHA, snapshot5tick 상태 parity, raw경계30개,
  PT-c(first30 span/29≤52.0ms), PT-d tinted≥11439, V1/V2/s/q/Scale2x, C ratio≥.95/p95Δ≤16ms.
- 이전 바퀴 검수: 10시도 중 최초D1/unroll은 historical, REP STOS 이후8build×48/current MATCH.
  DLL10/trace20·PNG/hash/manifest MATCH, snapshot70 decode 상태 parity PASS, 원문 입력790파일 보존.
- 변경: 이 기록·`docs/work/active/G1_MIDDLE_W70_P5T_CLIP_PREPARE_COST_HANDOFF_LAP929.md`·STATUS만 수정.
  제품/source/tests/probe/validator/바이너리0, 새 Wine/runtime0, counter929 읽기만, 커밋0·uncommitted 유지.
- 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006
  `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` MATCH.
  0x466EA0/0x466540 old bytes `83ec148b44241c`/`515356578b7c2418` read-only MATCH.
- 후보 구현 SHA: mirror `6c925a923ef0f7bae31b650d991abc83215c11542b0b942f104452a932696e82`,
  perfC/H `dea19cad12495b8c44f9f7311cfaeca902c895c60234c946501eb8202400547a` /
  `1e906d9ace98fa94856c79b1111eff86cafb87a3a39f09c3fb153432162ab5fd`,
  trace `f3981f86e9b0d6c25ade37c992453477f4a7d20f9d4eec9dfbfda87dbe8425d4`,
  회귀 `13134088d772bc206f7a2f43496f5501d5cfc0a13a311ce3e97db716f8a05fa6`는 이전 source와 동일.
- fixture/environment: 비합성save006, 원본800×600/후보1600×1200 Scale2x, 기존 private game/prefix/display.
  플레이어8record는8활성 부하증거 아님. 새 실행 없으며 기존 완료cleanup·game_removed·prefix process0만 검수.
- 명령: `make doctor`, `make lint`, `make typecheck`, `.venv/bin/python checks/safety.py`,
  `.venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap929_middle_review/recalculate.py`.
  로그 `logs/gates/lap929-middle-{doctor,lint,typecheck,safety,recalculate}.log`.
  재계산 helper의 잘못된 `_capture_visual_comparison` import는 실제 `_compare_images`로 수정해 완주했고,
  보호PE helper import-path는 tools 경로로 수정해 직접 SHA/bytes 확인했다. 추적 가능한 로컬 helper 오류이며 게임수정/필수검사 실패 아님.
- 측정: 첫D1 DOWN whole35.609248/clip33.649507/기존sections1.602690/residual0.357052ms.
  수리후 diagnostic DOWN26.579059/24.704238/1.530576/0.344245ms, RIGHT27.186614/25.507176/1.392572/0.286866ms.
  clip 준비는 여전히 큰 내부 구간, heap/fill/mask 세부 원인 UNKNOWN. coarse/whole 차이는 다른 계측의 차이로 보존.
- 비계측 PT-c: 첫GREEN52.103448/51.344828 FAIL, GREEN2 50.586207/50.413793 PASS,
  B′1 56.068966/52.482759 FAIL, B′2 50.344828/51.379310 PASS. 진단RIGHT53.965517FAIL은 acceptance에서 제외.
  연속2 FAIL 유지. B′1 tinted covered9229<11439로 PT-d 미달 추가확인(다른GREEN11949/11439, B′2 14414).
- V1 PS3 present9456 위반0, 최종8실행 PNG40쌍 V2/s/q 재계산 값 MATCH·PASS, 활성Scale2x PASS.
  old nearest BLOCKED는 별도 진단이며 새로운 화면결함으로 귀속하지 않는다. contact sheet 원본/후보 확인,
  캡처의 동일tick 최종입력 증명은 아님. C raw p95 histogram·tick ratio 재계산 PASS(+8/+9/+8ms; 1.002506194/.999996908/.999995720).
- 고정late20 effective395960.5/480000=82.4918%, stale74863.5·감소미입증, tinted_clip0.
  input-effect/최종입력/HD90%/GDI/두번째장면/API실패주입·강제rollback/사용자 승인 미검증 유지.
- 판정: D1 부분확인 PASS, P5-T HOLD(PT-c/PT-d), G1 HOLD. 제품/마일스톤 마감0.
  새로운 실질적 raw충돌·원인불명 필수실패3회·마일스톤 경계 없음: ESCALATE_SOL 생성 조건 없음.
- 증거: 공유temp `20261004_lap929_middle_review/recalculation.json` SHA256
  `5a462d9e36396fc747a6c01a54a23ce75712e17b74d08d270976aa90b38f2e8f`, script·supplement·pins·PNG 보존.
- 다음 행동: 인계 카드의 D2(임시할당/free·fill·mask exclusive QPC→같은work 최소수리→비계측 GREEN/B′2/C3).
  일정/경계/30개/임계값/미러범위/validator/과거raw를 그대로 두며 새 계획·사용자 재허가 대기 없음.
- 최종 검증: 문서/handoff 확정 뒤 `make check`를1회 완주하고 결과/불변감사는 STATUS에만 보강한다.
  그 전 doctor/lint/typecheck/safety PASS, fresh fullFast 및 새 runtime는 아직 검증 결과로 주장하지 않는다.
