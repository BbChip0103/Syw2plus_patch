# 2026-09-12 | lap 321 | 목표 G1 (M1, F1 이후 상위 방향)

- 실제 provider/model/effort / 지정 역할: Codex gpt-6-astra/high / Astra major direction/master-plan.
  게임 코드 직접 수정 0. 다른 모델 호출/대행 승인 0. 사용자 runtime lap=320이나 현재 counter=321을 사용(읽기만).
- 가설: lap317 결정4의 F1 종결 조건이 충족됐으므로 같은 R2 재증명보다 미제출 runtime 봉투 문서 심사가
  다음 의사결정에 필요한 결측을 드러낸다. N4/W3는 현재 심사의 선행 조건이 아니며 별도 수리하지 않는다.
- 예상 PASS/FAIL: lap320 원본 기반 probe fresh 출력이 저장 report와 동일하고 failures=[]; 입력 SHA 일치;
  make check/safety 정상; 문서에 심사 범위·반려 조건·역할 분리·실행 예산 0 명시. 불일치/필수 실패는 승격.
- 변경 파일: runtime 계약 `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §13 추가,
  `docs/STATUS.md`, `docs/history/laps/20260912_status_lap320_compaction.md`, 본 기록,
  `loop/ESCALATE_SOL`, `logs/lap321/` 검증 근거. 전부 uncommitted; 커밋/푸시 없음.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 일치.
  후보 없음. 환경=정적 읽기·문서·Fast. 활성 인원/지도/군대/게임 fixture=N/A.
  기존 probe의 합성 손상 fixture만 재행사. 게임/Wine/Xvfb/Stage B/PNG/실제 입력 0.
- 이전 바퀴 검수: lap320 probe 및 test/report SHA가 기록과 일치. 기존 검수 probe를 fresh 실행했고
  stdout=`logs/lap321/previous_review_recheck.json`, stderr=0 B, rc=0, failures=[].
  SHA `3d0022b88d694fd1a17c76073d47622c796bab2be188a90d83d325f0a24f60da`가 lap320 저장 report와
  byte-identical. 이는 재현성 확인이며 새로운 독립 방법의 검수라고 부르지 않는다.
- 실행 명령: `python3 docs/history/laps/probes/20260912_lap320_middle_lap319_f1_review_probe.py`;
  `make check`; `bash checks/safety.sh check`. stdout/stderr와 게이트 로그는 `logs/lap321/`에 보존.
- 측정/판정: 이전 검수 재현 PASS; 상위 분기 RECORDED; middle 계획 수용 PENDING;
  runtime/load 구현 근거 UNKNOWN; S1 종결 REJECT, G1~G4 제품 미완료 유지.
- 판단: §5(a)~(e), fixture 선택, 하네스/evidence 분리, 실패 보존을 표로 심사하도록 범위를 제한했다.
  정적 후보 A 우세를 실제 좌표 확정으로 바꾸지 않았고, runtime 금지 완화나 W3 재pin을 승인하지 않았다.
- 승격: 구현 근거 미확정(슬롯 절차·구성 시점 값·실행 봉투)에 따라 ESCALATE_SOL 생성 후 종료.
  middle은 §13 각 행의 근거와 ACCEPT/REVISE/REJECT를 기록하고 실행 관측이 필요한 부분은 최소 봉투로
  상위 반환한다. work 직접 착수 없음. 실제 인계 모델을 기록하고 provider 폴백 금지.
- 문서 조회 메모: 처음 `APPROVALS.md`를 루트에서 읽으려다 부재를 확인한 후 정본
  `docs/feedback/APPROVALS.md`를 읽었다. 필수 빌드/검증 실패가 아닌 경로 조회 오류다.
  MODEL_ROUTING과 상위 지시의 역할 차이는 기존 lap317 처리와 같이 명시 보존했고 설정은 수정하지 않았다.
- 다음 한 가지: STATUS 참조. 이 기록은 새 활성 큐를 만들지 않는다.

## 최종 검증과 보존

- `make check`: **361 passed in 56.31s**, Ruff/compileall/mypy/CONTEXT_PASS, rc=0.
- `bash checks/safety.sh check`: **SAFETY_PASS**, rc=0. 필수 게이트 예상 밖 실패 없음.
- STATUS 최종 127줄, Blockers 제목 1개. 갱신 전 130줄 원문과 SHA를 압축본에 보존했다.
- `logs/lap321/input_integrity.json`은 읽은 보호 입력 5개 SHA 불변 및 원본 SHA 일치를 기록한다.
- 변경 문서·인계 표식·검증 로그의 최종 SHA는 `logs/lap321/final_sha256.json`에 저장한다.
  해시 장부 자체의 자기 해시는 넣지 않는다. 계획 독립 수용·제품 실행은 미검증이며 승인으로 표기하지 않는다.
