# 2026-09-10 — 모델 역할/실행 차단 하네스 세팅

## 사용자 지시와 범위

- Astra/high: 큰 방향·상위 계획.
- Sol/high 또는 Claude Code Opus5/high: 중간 계획·컨펌.
- Luna/high 또는 Claude Code Sonnet5/high: 실무.
- 최신 재확인: 아직 루프를 돌리지 않고 환경·하네스만 세팅한다.

따라서 실제 모델/개발 루프, 게임, 서비스, 커밋/푸시는 실행하지 않았다.
원본/참고 저장소는 수정하지 않았다. 상위 계획을 생성·승인했다고 주장하지 않는다.

## 설정 변경

- `loop/env.sh`, `loop/env.local.sh.example`: 역할 모델/명시적 provider 선택, high.
- `loop/loop.sh`: 역할별 argv, 중간 진단/컨펌 handoff, override 검사.
- `loop/loopctl.sh`: 읽기 전용 models 및 미래 strategy/plan/review 진입점.
- `tests/test_model_routing.py`: 가짜 Codex/Claude로 명령 구성과 차단 검증.
- `AGENTS.md`, `CLAUDE.md`, `loop/PROMPT.md`, `loop/README.md`,
  `docs/MODEL_ROUTING.md`, STATUS/INBOX/README/CHANGELOG/lap template: 역할과 세팅 전용 경계 기록.

이관 시점 manifest는 역사적 출처 기록으로 보존했다. 이후 설정 수정을 최초 이관 내용으로 덮어쓰지 않았다.
실무 파일 변경은 사용자 요청 모델 Luna/high 하위 에이전트가 담당했다.

## 검증 경계

격리 임시 프로젝트에서 가짜 CLI를 실행했다. 테스트 내 enabled/run/stage는
실제 저장소나 실제 유료 CLI가 아닌 모의 실행이다. 루트에서는 models 조회만 했다.
루트 STOP과 기존 lap counter=1은 유지했다. counter=1은 앞선 세팅 dry 이력이며 이번 실행이 아니다.

CLI 버전/모델ID 근거는 `docs/MODEL_ROUTING.md`. 계정 접근권한·과금·쿼터는 검증하지 않았다.
Fast 성공은 모델의 의미적 승인, 게임 동작, G1~G4 완료 증거가 아니다.

## 최종 세팅 검증

- 부모 재실행 `make check`: **57 passed**, Ruff PASS, compileall PASS,
  mypy 지정6파일 PASS, context/Bash syntax PASS.
- `checks/safety.sh check`: **SAFETY_PASS**.
- `loopctl models`: Astra/Sol/Luna 기본 라우팅과 high 조회 확인.
- root `loop/STOP` 존재, `.lap_counter=1` 불변.
- 원본이 없는 환경의 새 dispatch 테스트3개는 명시적 skip 처리한다.
  이번 최종 전체 테스트는 원본 fixture가 있는 환경에서 수행했다.
- 원시 로그: `model_routing_checks.txt`.

잔여 검증: 실제 모델 접근/의미적 컨펌과 실제 게임 기능은 실행하지 않았으므로 미검증이다.
