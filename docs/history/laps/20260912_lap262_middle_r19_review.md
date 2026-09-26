# 2026-09-12 | lap 262 | 목표 G1 Stage B — R19 독립 검수 (middle tier)

- 실제 provider/model/effort / 지정 역할: Claude Code / `claude-opus-5` / high /
  middle tier(진단·계획·컨펌). 게임 코드 hands-on 수정 없음. lap261 work(R19) 독립 검수.
- 가설 / 사용자 관찰: lap260 escalation은 R17 회귀가 `drive_wait` 함수명에 고정돼 helper 개명이
  조기-거부 커버리지를 조용히 지운다고 지적했다. lap261 work는 회귀를 SUT AST에서 계산한
  top-level review-body 줄 집합과 `sys.settrace` 줄 추적으로 옮겼다고 주장한다. 검수 가설:
  (a) 개명은 더 이상 커버리지를 지우지 못한다, (b) "본문이 거부보다 먼저 실행되는" 결함은
  R17이 단독으로 사살한다, (c) 새 앵커 자체가 조용히 무효화될 수 없다.
- 예상 PASS / FAIL 조건: 개명 단독 변이는 생존(오탐 0), 늦은-거부 결함 변이는 R17 단독 사살,
  R17만 제거하면 그 변이가 부활(하중 확인), 기존 R7/R10/R11 커버리지 불변, 그리고 파생
  줄 집합이 비는 구조에서도 결함이 사살돼야 한다. 하나라도 어긋나면 범위 반려.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): SUT·테스트는 **읽기 전용**.
  신규 검수 산출물만 추가했다 —
  `docs/history/laps/probes/20260912_lap262_r19_review_probe.py` sha256
  `147abbe95a5dee65545ea21521ef222e77d19435018b953fc4cfee4d912b97b7`;
  `..._lap262_r19_review_report.json` sha256
  `fc6699048c12da546656b26facc30a83853af8915e9ba2d82dae3983bf5369dd`;
  round1 보존본 `..._lap262_r19_review_probe_round1.py` sha256
  `69a059f2bf8671d17f6539e22b22d114d1254096d5d395128490173720eebf45`,
  `..._lap262_r19_review_report_round1.json` sha256
  `866e01c6d0f9509e197c4ed8385c7dbcfc131653ca92b54b0afd3cb978b36b58`.
  모두 uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.
  검수 전후 동일: `tests/test_review_probe_output.py`
  `f5a0384eb31c637bd6c92c0142328fcd046b9a39eec3958d3eb9b846ab82c8f0`(lap261 work 기록값과 일치),
  `tools/runtime_env.py` `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`,
  검수 대상 SUT probe `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`
  `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`.
  Python 3.13.5. 게임 상태/플레이어/지도/군대 N/A. fixture는 `/tmp` 미러와 소스 변이뿐이고
  실저장소는 읽기 전용. 게임/Wine/Xvfb/PNG 0회.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python -m pytest -q tests/test_review_probe_output.py` → `8 passed`;
  `.venv/bin/python docs/history/laps/probes/20260912_lap262_r19_review_probe.py` → exit 0,
  report `..._lap262_r19_review_report.json`;
  `make check` → `279 passed`, Ruff/compileall/mypy 10 source files, `CONTEXT_PASS`;
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`. PNG/캡처 없음.

## 측정값 / 판정 — **R19 범위 반려 FAIL (커버리지). 기계 1단만 해당.**

lap261의 결론을 재실행한 것이 아니라 새 probe로 독립 재측정했다.

- **C0** 실저장소 targeted: `8 passed`, exit 0.
- **C1** 계약 독립 재유도(테스트 helper를 import하지 않고 자체 AST/추적 구현):
  preflight `if __name__` If의 end_lineno = **130**, review-body 줄 집합 = **137~426의 262줄**,
  비어 있지 않음, `drive_wait` def(326)과 report write(426)가 모두 포함된다.
  탐지기 생존 대조(positive control): 정상 성공 경로는 그 262줄 중 **205줄을 실제 실행**한다.
  거부 경로 대조(negative control): rc **2**, 본문 줄 **0줄** 실행, 메시지 일치, 파일 보존.
- **C2** depth-matched 미러 M0 = `8 passed` = 실저장소 `8 passed`(대조군 성립).
- **C3** 변이 6종, 범위 = R17 회귀 1건:

  | 변이 | 결함 | 결과 | R17 사살 | 범위 밖 사살 |
  |---|---|---|---|---|
  | M1 `drive_wait` 개명만 | 없음 | `8 passed` **생존(정답)** | - | 0 |
  | M2 조기 `exists()` 거부만 무력화(O_EXCL이 같은 메시지·exit 2로 여전히 거부) | 있음 | `1 failed / 7 passed` | **단독 사살** | 0 |
  | M3 = M2 + `drive_wait` 개명 | 있음 | `1 failed / 7 passed` | **단독 사살** | 0 |
  | M4 조기 거부 블록 전체 삭제 | 있음 | `5 failed / 3 passed` | 사살 | 4 (R10 계열) |
  | M5 조기 거부가 exit 0 | 있음 | `6 failed / 2 passed` | 사살 | 5 |
  | **M6 = M2 + 최초 top-level `__name__` If를 본문 아래로 이동** | **있음** | **`8 passed` 생존** | **없음** | 0 |

- **C4** 하중 확인: R17 회귀만 삭제하면 baseline `7 passed`이고 **M2/M3가 부활**한다(각 `7 passed`).
  M4/M5는 R17 없이도 R10/R7이 계속 사살한다 → R19는 기존 R7/R10/R11 커버리지를 약화하지 않았다.

### R19가 실제로 달성한 것 (work tier가 되돌리면 안 되는 부분)

M3가 결정적이다. `drive_wait`를 개명한 상태에서도 늦은-거부 결함을 **R17이 단독으로** 사살한다.
lap244의 함수명 앵커에서는 빠져나갔을 변이다. M1(개명만)은 오탐 없이 생존한다.
즉 escalation이 요구한 “식별자가 아니라 동작에 고정” 자체는 성립한다.

### 반려 사유 — 앵커가 이름에서 AST 위치로 옮겨졌을 뿐 무효화 가드가 없다

`_review_body_lines()`는 **최초** top-level `ast.If`(`__name__` 비교)를 경계로 쓰고, 그 뒤 줄만
반환한다. 그 If가 본문 아래로 내려가면 집합이 **빈 집합**이 되고
`assert not (_review_body_lines() & seen)`는 **공허하게 참**이 된다. 테스트에는 비어 있지 않음을
확인하는 단언이 없다.

M6로 실측했다. `if __name__ == "__main__":`를 `_IS_MAIN = __name__ == "__main__"` /
`if _IS_MAIN:`로 바꾸고(조기 거부 분류 경로는 그대로 유지) 파일 끝에 관용적인
`if __name__ == "__main__":` 꼬리를 붙인 뒤 M2와 같은 늦은-거부 결함을 넣었다. 직접 추적 결과:

- 미러 baseline(무변이) 거부 경로: 본문 **0 / 262줄** 실행, rc 2.
- **M6 거부 경로: 본문 196 / 262줄을 실행한 뒤 거부**한다. rc 2, 메시지 동일, 파일 보존.
- 그런데도 shipped `_review_body_lines()`는 M6에서 **0줄**을 돌려주고 전체 스위트는 `8 passed`.

즉 R17이 존재 이유로 삼는 결함이 그대로 있는데 회귀가 통과한다. lap254의 M4 생존, lap258의
M5 생존과 같은 커버리지 결함 계열이므로 같은 기준으로 반려한다.

- **Fast 게이트**: `make check` `279 passed`, Ruff/compileall/mypy 10 source files,
  `CONTEXT_PASS`, `SAFETY_PASS`. 게임/Wine/Xvfb/PNG 0회.
- 판정: **FAIL(커버리지)**. 기계 1단 판정이며 제품 G1 증거도 사용자 마일스톤 승인도 아니다.

### round1 오염 변이 기록 (삭제하지 않고 보존)

첫 실행의 M2는 `if path.exists():` 두 줄을 **삭제**했는데, 그러면 탐색 불가 부모(0o600)에서
`path.exists()`가 더 이상 `PermissionError`를 던지지 않아 분류가
`output path unavailable` → `output parent is not writable`로 바뀐다. R10 테스트 1건이 함께
죽어 사살 귀속이 오염됐다(round1: M2/M3가 범위 밖 1건 동반, M6도 그 테스트로만 사살).
round2는 `if path.exists() and False:`로 바꿔 `exists()` 호출과 OSError 분류를 보존하고
“본문이 거부보다 먼저 실행된다”만 남겼다. 위 표는 round2 수치다. round1 산출물은
`..._probe_round1.py` / `..._report_round1.json`으로 보존했다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: SUT·테스트·원본·보호 자산·baseline/golden
  무변경. R19는 기계 1단 **반려**. S1/F2-R2, R6-B-R2, WM_CLOSE 후보 teardown, G2~G4는 미해결.
- 다음 한 가지: work tier(Luna 또는 Sonnet5/high)가 **R28**을 구현한다 — 파생 줄 집합의
  비공허성과 앵커를 단언해 M6가 죽게 하고, M1 생존·M2/M3 단독 사살·C4 하중을 유지한다.
