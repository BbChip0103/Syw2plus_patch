# 원본 덮어쓰기 고지 — 20260912_lap228_r6b_r3_review_report.json

`20260912_lap228_r6b_r3_review_probe.py`는 출력 경로를 하드코딩해서 재실행하면
lap228 원본 JSON을 같은 자리에 덮어쓴다. 그 결과 현재 파일은 lap228 당시(R6-B-R4 수리 전)
결과가 아니라 **R6-B-R4 수리 후 재실행 결과**다.

- 현재 파일의 `source_sha256` = `f39d26fc578c7a33379eb2556f588d4b56a5a24a9ae618ac590947cbfbc4c76e`
  (lap229 수리 후 `tools/runtime_env.py`). `lap` 필드 228은 스크립트 상수일 뿐이다.
- lap229(work)와 lap230(middle)이 검증 목적으로 각각 재실행했고, lap230 실행에서
  `wait_defects=[]`(W1/W2/W3 모두 AGREES)였다. 같은 내용을
  `20260912_lap230_lap228probe_rerun_report.json`으로 별도 보존한다.
- lap228 원본 결과(대기 3케이스 중 W3가 DEFECT, 그래서 R6-B-R4로 등록)는
  `docs/history/laps/20260912_lap228_middle_r6b_r3_review.md` 본문에 그대로 남아 있다.
  JSON 원본은 복구 불가이며 재구성하지 않는다(날조 금지).
- 후속: 이 probe를 다시 돌릴 때는 출력 경로를 lap별로 분리해야 한다. R6-B-R7로 등록.
