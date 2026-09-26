# 2026-09-11 | lap 71 이후 | STATUS overflow 복구 기록

lap71 종료 기록으로 `docs/STATUS.md`가 184줄이 되어 180줄 safety gate를 넘었다. 현재 판정과 lap66 이후 최신 이력은 유지하고, 아래 lap57~65 상세를 이 파일로 이동했다.

- 이동 전 `docs/STATUS.md` SHA256: `7801a17cea52e01b8464d6673f3b2e2cd1a92b87848382f519777606adf4e875`
- 이동 범위: 기존 검증 상태의 lap57~65 상세. 각 lap 원문은 `docs/history/laps/`에도 보존된다.
- 코드, 하네스, 게임, EXE, DLL, 자산, runtime artifact는 변경하지 않았다.

## 이동한 원문

- 원본/private EXE SHA는 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; lap57에서 재대조했다.
  guard SHA는 lap56 기록과 일치하며 helper/test SHA는 lap58 변경 기록에 남겼다.
- lap57 raw 재추출: `0x992BE` predicate/call과 `0x9B6D0` entry가 player map old bytes와 일치한다.
  false branch count=`unit+0x6BE`, records=`unit+0x6C2+4*i`, flags=`0x00893118+2*i`, hover
  `0x00A90430`을 확인했다. slot1199 count/record base는 `0x00892376`/`0x0089237A`다.
- lap58 helper는 false branch에서 count WORD(최대10), 첫10 record WORD쌍, flag WORD 10개,
  geometry WORD 4개를 bounded raw block으로 저장하고 selection/predicate 전후 값 변화를 거부한다.
  stable-ineligible 예외/diagnostics에도 before·after snapshot을 보존한다.
- lap59 원본 재추출은 `0x40F770→0x413560→0x496380`의 `unit+0x6BE` WORD count,
  `0x40FE90`의 `unit+0x6C2+4*i` WORD쌍, `0x498E30`의 10개 WORD flags,
  `0x498DB0`의 `0x009E2BA4..AA` WORD geometry와 helper 상수가 일치함을 확인했다.
- lap56 manifest/baseline/verdict/inputs/provenance SHA와 PNG8개 SHA/800×600은 JSON과 일치한다.
  selection-after를 직접 확인했고 HQ 선택/아이콘 표시는 보이나 worker 생산 의미는 승인하지 않았다.
- lap59 새 검수에서 targeted runtime/guards **46 passed**, 전체 `make check` **116 passed**,
  Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**. exit0은 제품/계획 승인 아님.

- lap61은 원본 SHA와 lap60 manifest/baseline/verdict/provenance 및 PNG8개 SHA를 재계산 일치시켰다.
  원본 `0x498EE0` reset, `0x4A3B5B` 네-array writer, `0x499201..0x499297` primary fill,
  `0x499583` consume, `0x4992BE→0x49B6D0` 조건부 추가 경로를 재추출했다. `make doctor` ok=true
  (기본 runtime manifest는 optional false), 명시 manifest doctor-runtime ok=true, `make check`
  **116 passed**, Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**다. 제품 PASS는 아니다.

- lap62는 원본/private 및 lap60 manifest/baseline/verdict/provenance SHA를 재계산 일치시켰다.
  원본에서 `0x498EE0` 12회 reset, `0x4A3B5B` 네 WORD writer, `0x499201..0x49929E` fill,
  `0x4992BE→0x4992DF→0x49B6D0` 조건부 경로와 두 분기 뒤 `0x499583` consume을 재추출했다.
  `make doctor` top ok=true, 명시 manifest doctor-runtime ok=true, targeted **46 passed**, 전체
  `make check` **116 passed**, Ruff/compileall/mypy/context 및 safety **PASS**다. 계획/제품 PASS는 아니다.

- lap63은 원본 SHA를 재계산 일치시키고 `0x498FBA` selection count dispatch에서 count1만
  `0x499201..0x49929E` primary fill로, count0/2+는 별도 경로로 간 뒤 `0x499583`에서 합류함을
  재추출했다. 96-byte 물리 범위와 lap62 분기 순서는 확인했지만 count1 precondition 누락으로 계약은
  REVISE다. `make doctor` top ok=true, 명시 manifest doctor-runtime ok=true, `make check`
  **116 passed**, Ruff/compileall/mypy/context 및 safety **PASS**다. 새 runtime/제품 PASS는 아니다.

- lap64는 원본/private SHA와 `0x498FBA` count0/count1/count>1 dispatch, count1 전용 fill 및 공통
  `0x499583` consumer, reset/writer/96-byte 범위를 독립 재확인했다. `make doctor` top ok=true,
  명시 manifest doctor-runtime ok=true였지만 targeted 명령은 `.venv/bin/pytest` 부재로 exit127했다.
  필수 Fast/safety는 중단 규칙에 따라 SKIP이며 계약/제품 PASS가 아니다.

- lap65는 Makefile에서 정식 targeted invocation을 확인했고 `.venv/bin/python -m pytest -q
  tests/test_runtime_env.py tests/test_runtime_guards.py` **46 passed**, `make check` **116 passed**,
  Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**, `make doctor` top `ok=true`/original verified다.
  원본/private SHA, count dispatch, count1 fill, 공통 consumer, reset/writer old bytes가 일치해
  exact-single-selection 계약을 work-ready로 승인했다. 구현/실제 runtime/제품 PASS는 아니다.

