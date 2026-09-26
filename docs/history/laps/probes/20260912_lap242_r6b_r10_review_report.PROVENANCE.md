# lap242 R6-B-R10 review — attempt1 보존 근거

`20260912_lap242_r6b_r10_review_report.attempt1.json`은 첫 실행 원문이며 삭제하지 않는다.
verdict=FAIL이었고 원인은 세 가지로 분리된다.

1. **제품측 실제 결함 (보존, 수리 안 함)** — `C07_non_executable_parent`.
   출력 부모가 `0o600`(쓰기 가능, 탐색 불가)일 때 `output_refusal`의 첫 절 `path.exists()`가
   `PermissionError`를 그대로 올려 raw traceback과 `exit 1`로 끝난다. R6-B-R10이 닫겠다고
   한 실패 계열 그 자체다. 새 결함 **R6-B-R16**으로 등록하고 work tier에 넘긴다.
   middle tier는 진단·검수 역할이므로 수리하지 않는다.

2. **검수 하네스 보정 (attempt2에서 수정)** — `earliness_dynamic`.
   refusal/healthy 실행 시간 비율 0.706은 인터프리터 기동 시간이 지배해서 본문 실행 여부의
   판별자가 되지 못한다. attempt2는 이 수치를 관측값으로만 남기고 판정 입력에서 제외했다.
   조기 실행 여부의 근거는 `earliness_traced`(프로파일 훅으로 본문 함수 0회 실행)와
   `earliness_structural`(AST 문장 순서)이다.

3. **검수 하네스 보정 (attempt2에서 수정)** — `report_semantics`.
   저장된 lap228 보고서와 신규 보고서는 `source_sha256` 한 키만 다르다. 이 키는 probe 자기
   소스 해시이므로 lap241이 guard를 추가한 이상 달라지는 것이 정상이다. attempt2는 이 키를
   provenance로 분리하고 나머지 측정 전 구간의 동일성을 판정한다.

제품 코드/임계값/기존 증거는 이 보정으로 변경하지 않았다.
