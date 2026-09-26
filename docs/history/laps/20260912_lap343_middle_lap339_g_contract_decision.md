# 2026-09-12 | lap 343 | 목표 G1 (lap339 G 계약 유효성 판정)

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션 / 정확한 모델 ID는 주장하지 않음 / high / middle(진단·계획·확인). 게임 코드·하네스·제품 테스트 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap342의 G rc1은 lap340 R-a/R-b 결함이 아니라, lap339 시점 STATUS 보존 감사를 이후 mutable STATUS에도 영구 강제한 역사적 전이 단언 2건이다.
- 예상 PASS / FAIL 조건: PASS=`PROMPT.md`·`AGENTS.md`·`DESIGN.md`에 live STATUS→과거 압축본 직접 포인터 계약이 없고, 기존 G 실패가 그 두 단언뿐이며 불변 압축본과 나머지 현재 계약은 통과. FAIL=직접 포인터 계약이 명시되거나 다른 G failure/압축본 불일치가 존재.
- 변경 파일 / source fingerprint / 커밋: 신규 adapter probe, 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` lap343 부록. 기존 G/기대값/STATUS 포인터/baseline/golden/게임·하네스·제품 테스트 수정 0. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본·후보 SHA / 환경 / fixture: 기존 G SHA `761aec2f…f8018b`; lap337 압축본 파일 SHA `e771b22c…2c842`, body SHA `512abde1…8cd5a6`, body/header 130줄 일치. Python 소스·문서·JSON subprocess만 사용한 오프라인 fixture; EXE/Wine/Xvfb/입력/활성 플레이어/지도/군대/PNG/후보 artifact 0.
- 실행 명령 / 수치: 기존 G `.venv/bin/python …lap339…probe.py` rc1, failures 정확히 2건(두 live-STATUS 포인터). 신규 `…lap343…adapter_probe.py` SHA `420e86cb…2c832`; `python3`·`.venv/bin/python` 모두 rc0, stdout SHA `3124aa94…d1fc1` byte-identical, `unexpected_contract_failures=[]`, Ruff rc0. 갱신 후 STATUS 130줄·Blockers 1개, adapter 출력 동일, safety `SAFETY_PASS`, `make check` rc0 **378 passed(57.51s)**·Ruff/compileall/mypy/`CONTEXT_PASS`.
- 판정: **ACCEPT — lap339 G의 live-STATUS 포인터 2건은 현재 계약이 아니라 lap339 시점 보존 감사에만 유효한 역사적 전이 단언이다.** `PROMPT.md`는 STATUS가 130줄을 넘을 때 원문 SHA/줄 수/전체 원문을 history에 먼저 보존하도록 요구할 뿐, 이후 STATUS가 그 파일명을 영구 유지하도록 요구하지 않는다. 기존 G도 특정 파일명 고정을 전이 단언으로 금지하면서 연결 자체를 영구 강제해 내부 충돌한다.
- 허가된 대체: 기존 G는 불변 이력으로 수정하지 않는다. 다음 fresh 검수에서는 lap343 adapter를 G 대체로 사용한다. adapter는 기존 G SHA와 실행을 보존하고 두 포인터 failure만 허용하며, 다른 failure는 전부 FAIL로 전파한다. 포인터를 STATUS에 삽입하거나 기대값을 고쳐 rc0로 만들지 않는다.
- 회귀 / 남은 위험: 이 판정은 lap340 수리 ACCEPT, 후보 실행 허가, 제품 G1 증거, Stage B/마일스톤/사람 승인이 아니다. lap342에서 SKIP한 snapshot/SHA/diff·review probe·대상 테스트·Fast/safety·E/F·A/C 분해는 새 세션에서 전부 fresh 재검증해야 한다. lap331 identity UNKNOWN, W3·N14·WM_CLOSE·동일상태 pair도 유지한다.
- 다음 한 가지: 다음 새 middle(Sol/Opus5 high)이 lap342의 전체 순서를 처음부터 재실행하되 G만 lap343 adapter로 대체한다. 전 항목 PASS와 별도 발효 판정 전 후보 fresh run은 0회이며, 실제 후보 run은 work tier로 넘긴다.
