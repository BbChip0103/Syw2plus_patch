# 2026-10-04 | lap927 | G1 P5-T-R 비용 계측 범위 독립 검수

- 실제 provider/model/effort / 지정 역할: 중간 tier 진단·계획·컨펌, solo. API 표면에서 실제 model/effort를
  확인할 수 없어 특정 Sol/high 호출을 주장하지 않는다. source/tests/validator/게임수정0·runtime0·subagent0·commit0.
  `loop/.lap_counter` 현재927을 읽기만 했다. 시작 HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는 provenance일 뿐이다.
- 읽기 순서: PROMPT①~⑥ → AGENTS/최신INBOX/APPROVALS → STATUS전체 → DESIGN1~4/MODEL_ROUTING →
  lap925 카드·lap926 history/ESCALATE·해당소스/검사. G1 최우선, G2/G5 종료·G3 중단·G4 보류 적용.
- 한 가지 가설: QPC section 합과 coarse 재호출 합의 큰 차이가 raw 충돌인지 측정 범위 누락인지 판정한다.
  성공식: immutable pair/trace/build/snapshot SHA·현재 source·경계 표본을 독립 재계산하고,
  다음 work가 바로 실행할 최소 비용 수리 또는 짧은 판별 진단을 하나 확정한다. PT-c/경계/일정/미러/validator 완화0.
- 변경파일(uncommitted): 이 기록, `docs/work/active/G1_MIDDLE_W70_P5T_QPC_SCOPE_DIAGNOSTIC_LAP927.md`,
  `docs/history/20261004_lap927_prior_lap926_escalate_sol_archive.md`, STATUS 및 처리한 `loop/ESCALATE_SOL` 제거.
  원문 승격은 byte-exact 보존한 뒤 제거한다. 미처리 사용자 지시·반려 삭제0, INBOX342/APPROVALS239 그대로,
  STATUS130줄 이하·Blockers1. source fingerprint는 마지막 검사 전후 별도 감사로 남긴다.

## 이전 work 독립 검수 / 수치

- 원본 EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  비합성 save006 SHA256 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` read-only MATCH.
  각 lane source/private EXE SHA MATCH·cleanup game_removed=true/no-prefix-process，원본/참고/개인세션 미접촉.
  일본 save006·원본800×600/후보1600×1200·Scale2x. owner records8은 활성8인 부하증거 아니다.
- GREEN pair SHA `cb5606f14fbed216d5501f61a2e70ee6132c9196e5cdedaaf610f7a4a6bdcf29`,
  진단 pair SHA `69462752c45f3bc41927b6e24a79737bc0685ddc2ed73da832bed66c40d843a1` MATCH.
  각 build 입력48개/current SHA·변환된 stub/Makefile·bridge·DLL·trace4개/snapshot20개 SHA MATCH.
  각 pair snapshot5×2는 header tick/body/current decoder 상태가 baseline/candidate 전필드 동일하다.
  binary payload 전체 byte 동일은 false여서 raw-byte parity로 과장하지 않았다.
- **R1 PASS(partial):** sim_tick 단조, 경계 안 표본값/seq/tick 배열 모두 saved/current raw MATCH.
  GREEN DOWN24/RIGHT26, 첫 뒤 seq1367/tick24730·seq1445/tick24825; 진단28/28.
  INCOMPLETE·p50없음·pair HOLD는 올바른 거부다. observation tick24728/24824 snapshot이 존재한다.
- **PT-c FAIL/HOLD:** lap925 규범(first30 span/29) GREEN74.758621/65.344828ms, 진단64.965517/63.827586ms.
  lap92671/61은 경계 안 interval 중앙값이고 이번 수치와 모순 아니다. 경계 안 평균73.913043/64.4ms도 따로 보존.
- 진단: 기존 section 합 DOWN1.644956/RIGHT1.476389ms/present, coarse28.925926/28.555556ms/present.
  재호출198.148148/166.518519회/present. 같은 양 끝 cumulative 차분·N-1·frequency10MHz로 계산했다.
  기존 section은 clip 임시 할당·full byte 초기화·mask/복원 등 caller 비용을 덮지 않으며
  marker 첫 reset 이후 차분이라 reset 누락이라는 추측은 지지하지 않는다.
  **scope gap 확정 / 실제 병목 UNKNOWN**, coarse 양자화만 탓하거나 L1/L2 저비용이라고 확정하지 않는다.
- perf env는 전체 실행 계측을 켜며 marker는 emission/reset만 제한한다. 따라서 진단을 비계측 PASS로 승격0.
  source-defined scope 차이로 기존 승격의 모순 여부를 판정했으며 새 불명확한 구현수리를 시도하지 않았다.

## 검증 / 결과 / work 인계

- 명령: `make doctor`, `make lint`, `make typecheck`,
  `.venv/bin/python -m pytest -q tests/test_g1_saved_scene_probe.py -k 'scroll_coverage or scroll_trace_adds_sim_tick or gdb_free_scroll_lane or opt_in_perf_sections'`,
  `.venv/bin/python checks/safety.py`, `.venv/bin/python checks/context_limits.py`.
  doctor top-level ok=true/original verified(기본 optional runtime manifest 없음), lint/typecheck PASS,
  focused **11 passed·143 deselected/0.06s**, SAFETY_PASS·CONTEXT_PASS. 이전 fullFast 로그 SHA 재확인 MATCH(1470/5).
  과거Fast는 현재 전체Fast로 재사용하지 않는다. 새 fullFast는 모든 lap/handoff/archive 작성 뒤 완주하고 결과는 STATUS만 보강한다.
- 재현 명령: `.venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap927_middle_review/recalculate.py`.
  결과 SHA256 `3a0ff9fcfa5f309f2fdae9a6bc410d3ef883fa2f31ee2df901c4e1852a617fb7`, 입력182파일 SHA inventory 포함.
  스크립트/최종 불변 감사는 같은 공유temp에 보존한다. 새 이미지/실행/제품 증거는 없다.
- 판정: **R1 부분수용, P5-T/G1 HOLD 유지**. 원인 진단 범위 확정으로 lap926 내부 승격 요청을 처리한다.
  새 근거 충돌/원인불명 필수검사3회 실패/마일스톤 경계 없음. 루프 일반 허가 질문·strategy 재상정0.
- **work 인계 D1:** 기존 opt-in에 whole reinvoke QPC(writer별)+exclusive clip_prepare를 추가하여
  같은 save/schedule의 짧은 격리 diagnostic pair로 내부/외부·clip준비/나머지를 가른다.
  계측 상세·회귀·수치식·귀속 후 즉시 최소수리→비계측GREEN 반복·R4 조건은 위 handoff에 명시했다.
  중간 tier는 renderer를 고치지 않았다. 비용귀속은 FEASIBLE(기존 QPC 배관 재사용), 비용수리 효과는 아직 미검증이다.
- 남은 것: PT-c·30표본·B′연속2/C3, tinted_clip covered0·stale 감소·HD90%·input-effect·GDI/두 번째 장면·사용자승인,
  과거 lap918 성능FAIL/입력HOLD 그대로. 제품/다음 마일스톤 마감0, 프로세스exit0을 승인으로 사용하지 않는다.
