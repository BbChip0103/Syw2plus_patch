# lap363 middle — lap354 probe import provenance 검수

2026-09-12 / 사용자 지정 middle(high), 진단·계획·확인 전용. 게임 코드·하네스·tests,
EXE/DLL/save/fixture/pin/baseline/golden은 수정하지 않으며 게임/Wine/Xvfb/입력/PNG를 실행하지 않는다.

## 1. 이번 한 가지와 가설

lap362의 필수 probe ImportError는 probe assertion이나 현행 S1 구현 결함이 아니라 인터프리터
선택 차이로 인한 top-level `tools` package shadowing이다. 시스템 `python3`의 전역 editable
install은 형제 `Syw2plus_re/tools/__init__.py`를 가리키지만, 프로젝트 `.venv`에는 이 저장소의
editable mapping이 있다. repo root를 명시한 단일 wrapper 실행에서 현재 `tools/runtime_env.py`
provenance를 먼저 출력하고 역사 probe를 수정 없이 정확히 한 번 실행해 판정한다.

## 2. 입력과 PASS/FAIL 식

- runtime lap: `363`; `loop/.lap_counter`는 읽기만 했고 쓰지 않는다.
- 보호 원본 EXE: 1,032,192 B,
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 보호 save000 fixture: 3,093,902 B,
  `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`.
- 원본 lap354 probe:
  `b08d0c7b97586a62904ef17a36150facf3897c25d6c128e921ef782b7c3d07a4`.
- 현행 SHA: `runtime_env.py=ba0a7beb657ce6c7a174d9323c4254f2d696b74277a974e15a5216d272b7372c`,
  `s1_load_evidence.py=fffc644495b442627a8166125365caa6270999ff06bead52d2b1e1a8ad90fa65`,
  `test_s1_load_evidence.py=7508e5c1fe3b6110336d3b1457381f4d208d632f361ff8c842309b18ad6cb8c7`.
- PASS: 위 입력 7개가 유지되고, wrapper가 import한 `runtime_env.__file__`이 현재 repo의
  `tools/runtime_env.py`이며, 원본 probe의 fresh exact-once 결과가 rc0/`failures=[]`다.
- FAIL/STOP: import origin이 형제/전역이거나, 입력 SHA가 다르거나, probe가 rc!=0 또는
  non-empty failures를 내거나, 필수 doctor/Fast/safety가 예상 밖 실패한다.

## 3. 범위와 후속 판정

probe PASS 뒤에만 lap362 §3의 Luna/high work 봉투를 발효한다. 이번 middle 세션은 구현하지
않고 work tier에 명시적으로 인계한다. 제품 S1·Stage B·G1 및 사용자 마일스톤은 계속 UNKNOWN이다.

## 4. 실행 결과와 판정

- 원인 **CONFIRMED**: 시스템 `python3`은 전역 editable finder의
  `Syw2plus_re/tools/__init__.py`를 선택할 수 있다. 프로젝트 `.venv`에는 현재 저장소의
  `tools` mapping이 있으며, repo root를 명시한 wrapper에서 current-repo provenance가 고정됐다.
- `make doctor`: rc0, 보호 원본 SHA `b56986e0…a8ac` verified. runtime manifest는 없고
  `runtime.ok=false`, `side_effects=false`; 실제 runtime 검증으로 세지 않는다.
- exact-once wrapper: `PYTHONPATH=<현재 repo root> ./.venv/bin/python -c <origin 출력 후
  runpy.run_path(원본 probe, run_name="__main__")>`; origin은 현재
  `tools/runtime_env.py`, probe rc0, `failures=[]`, fixture SHA 일치다. probe 편집 0회다.
- targeted: `./.venv/bin/python -m pytest -q tests/test_s1_load_evidence.py` → 21 passed.
- Fast: 기록 전 399 passed in 63.70s; 기록 반영 후 최종 현재 트리 399 passed in 64.15s,
  Ruff/compileall/mypy/`CONTEXT_PASS`.
- safety: `bash checks/safety.sh check` → `SAFETY_PASS`.

**ACCEPT / RELEASE:** lap362 §3의 Luna/high work 봉투를 발효한다. 다음 work는 그 세 파일만
수정하고 실제 게임 실행 0회로 회귀·probe·Fast·safety와 전후 SHA를 제출한다. 이번 판정은
import 환경 blocker 해소와 구현 범위 발효에 한정하며 실제 load, S1 결정성, Stage B, G1 제품
합격, 마일스톤 이동과 사용자 승인은 모두 UNKNOWN이다.
