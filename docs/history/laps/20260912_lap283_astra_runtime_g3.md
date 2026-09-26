# 2026-09-12 | lap 283 | G1 실행 연구 / G3 저장 포맷 상위 결정

- 실제 provider/model/effort / 지정 역할: Codex gpt-6-astra / high / major direction/master-plan.
  게임 코드 구현 없음. 하위 모델/유료 세션 호출 없음. `plan` direct 스킬을 사용했다.
- lap 출처: 사용자 첨부 runtime 표기는 282이나 `loop/.lap_counter`는 283이었다.
  PROMPT 규칙대로 283을 사용했고 counter를 쓰거나 복원하지 않았다. loop/STOP 파일 없음.
- 목표/가설: 정적으로 수용된 저장 복원 경로를 원본 대조 연구의 하네스 변경으로 연결하고,
  G3 저장 확장을 G1에서 분리하면 무변경 정적 재확인 반복을 피할 수 있다. 실행 가설은 미검증.
- 예상 PASS/FAIL: 계획 근거는 lap282 probe/출력 fingerprint 일치·fresh 결과 동일·failures=[];
  문서 검증은 Fast/safety와 STATUS 130줄 이하/Blockers 1개·구현 SHA 보존.
  runtime 실행 가능성은 fixture/load 절차·tick·실행 봉투가 없으면 UNKNOWN, 예산 해제 불가.
- 변경 파일: `docs/work/active/G1_RUNTIME_G3_ASTRA_DECISION_LAP283.md`,
  `.omx/plans/lap283-astra-runtime-g3.md`(정본 안내), `docs/STATUS.md`, `loop/ESCALATE_SOL`, 본 기록.
  신규 검증 로그만 `logs/lap283/`에 남겼다. uncommitted, 커밋/배포/원본 변경 없음.
- 원본 SHA: `Syw2plus/syw2plus_original.exe`
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 전후 동일.
  후보 SHA: N/A(생성 없음). 환경 Linux/.venv/정적 objdump. 활성 인원·지도·군대·fixture N/A.
  save 선택/적용 없음, 합성 게임 성공 없음, 게임/Wine/Xvfb/Stage B/원본 실행/PNG 전부 0.
- 이전 바퀴 검수: lap282 probe SHA `cdfa7c3c921cf4070150e2b6bc0361c8022700c463b24dc6c41900e7b42ae764`,
  과거 출력 SHA `e0f07f3a4352c51959919fc0b5eb6bc1f907a09596ae3e5d5d8c5e46f4be08` 일치.
  `.venv/bin/python docs/history/laps/probes/20260912_lap282_middle_unit_offset_review_probe.py`
  → `logs/lap283/unit_offset_review_recheck.json`, exit0/내용 이전과 동일/failures=[].
  306218행, x/y 115/115, movsx 41/41, accessor entry와 read instruction 차이 재현.
  기존 probe를 재실행했으며 새 독립 검수기를 만들거나 제품 검증으로 승격하지 않았다.
- G3 재계산: 현재 bulk 끝 0x975D8C, 현재 stride로 16개 끝 0x991330, 초과 0x1B5A4.
  이는 현재 배치의 한계이며 확장 포맷 자체가 불가능하다는 결론은 아니다.
- 실행 명령/수치: `make check > logs/lap283/make-check.log 2>&1` → **292 passed in 45.47s**,
  Ruff/compileall/mypy 10 files/CONTEXT_PASS. `LOOP_DRY_RUN=0 bash checks/safety.sh check`
  → `logs/lap283/safety.log`, **SAFETY_PASS**. 필수 게이트 예상 밖 실패 없음, 재시도 없음.
  최초 탐색에서 루트 APPROVALS.md는 없어서 실제 `docs/feedback/APPROVALS.md`를 읽었다.
  loop/STOP 부재 조회도 비제로였으나 빌드/테스트/검증 실패가 아니라 파일 존재 탐색이다.
- 판정: **상위 범위 결정 완료 / middle 승인 대기 / runtime UNKNOWN·예산0 / 제품 미완료**.
  원본↔원본 1쌍을 최소 요청 단위로 제한, Stage B는 별도 재결. G3 버전 식별 저장 계약 방향,
  bulk 길이만 증가하는 수리 배제. W1/W2는 S1 필수 선행조건으로 만들지 않았다.
- 회귀/남은 위험: 필수 Fast PASS는 계획 승인/실행 검증이 아니다. S1/F2-R2 실제 결정성,
  load 하네스 경로, tick 오차 근거, R6-B-R2, WM_CLOSE, G2~G4는 미결이다.
  기존 반려/승격 원문 보존. implementation progress=0, narrative-only를 구현 진척으로 세지 않는다.
- 승격 이유: 구체 실행 계약의 누락/불명확함. 사용자 중단 조건에 따라 ESCALATE_SOL 갱신 후 종료.
  라우팅 문서의 Opus 전용과 Sol 허용 차이는 최신 사용자 지시를 우선했으며 실제 모델 대체 없음.
- 다음 행동 참조: 현재 큐는 `docs/STATUS.md`만 사용한다. 승격 작업자의 검수 대상은 결정문서의
  여섯 필수 입력이며 구현은 별도 work 세션으로 분리한다. 마일스톤 이동/종결 없음.

## 파일 fingerprint

최종 파일과 로그의 SHA는 아래에 기록했다. 본 기록 자체 SHA는
`logs/lap283/final_sha256.json`에 둔다(자기 참조 해시를 만들지 않음).

- `docs/work/active/G1_RUNTIME_G3_ASTRA_DECISION_LAP283.md`: `b231386b27d34d65819250de8185fa6c1f9365c911ca4d1ea5ad09160bd6a06d`

- `.omx/plans/lap283-astra-runtime-g3.md`: `0c610778b2ec07e2084613cc65b5bb788c1f1f2c70c6898abfa7056363ee258b`

- `docs/STATUS.md`: `9087185915dcf8cebd962e79974da65c9e7995d43241cae0a6af920d2075063d`

- `loop/ESCALATE_SOL`: `c5ca3e61823b9087a1db0a71199bc2331236d7b5c8a24f9fbdc00574fe5a10ed`

- `logs/lap283/unit_offset_review_recheck.json`: `e0f07f3a4352c51959919fc0b5eb6bc1f907a09596ae3e5d5d8d8c5e46f4be08`

- `logs/lap283/make-check.log`: `60637b761685953461e982d07d2ef8f0edaa160eaaa9cf4d22a089c2c2c407b3`

- `logs/lap283/safety.log`: `4ae1cfe7183430cfef7225f54e2a6444b042294b0b6a9a50ec1c50f43217d192`

- `logs/lap283/before_sha256.json`: `f6d28fa39f931813a8be3a13b380fe1a4a78abe14ef641a21d6f425738b4bbac`

- `logs/lap283/status_before.md`: `32b61714a28e6314983229131369f1aaf6cb3bd027dc375e78e35e7ff365306d`
