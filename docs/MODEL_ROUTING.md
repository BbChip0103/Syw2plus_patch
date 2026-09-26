# 모델 역할 계약 — 2026-09-10 사용자 확정

| 역할 | 기본 | 사용자가 허용한 대안 | effort |
|---|---|---|---|
| 큰 방향·상위 계획(strategy) | Codex `gpt-6-astra` | Claude Code `claude-fable-5` | medium 기본, 필요 시 high |
| 중간 계획(plan)·검토/컨펌(review) | Claude Code `claude-opus-5` | 없음(현재 선택) | high |
| 실무(work) — 조사·코딩·테스트·수정 | Codex `gpt-5.6-luna` | Claude Code `claude-sonnet-5` | high |

## 역할 경계

- Astra 또는 Fable: G1~G4 전체 방향, 마일스톤/우선순위, 구조적 선택과 큰 재계획. 큰 분기나 반복 교착에서만 호출하며 대략 10개 work/middle lap당 1회 이하를 운영 기준으로 삼는다. 기본 medium이고 복수 경로의 고위험 선택이 남을 때만 high를 명시한다.
- Opus5: 상위 계획을 실행 가능한 작업/검증 단위로 분해하고 중간 판단 및 결과 컨펌.
  문제가 있으면 수정 범위와 검증 조건을 실무 모델에 넘긴다. 상위 계획을 임의 대체하지 않는다.
- Luna 또는 Sonnet5: 승인된 범위의 근거 조사, 파일 변경, 실제 진단/실행, 테스트와 수리.
  큰 방향 결정이나 자기 작업의 최종 승인까지 맡지 않는다.
- 계획/컨펌 역할도 문서·검증 근거는 읽고 기록할 수 있지만 게임 구현 수정은 실무 역할에 넘긴다.
- 다음 새 세션이라는 컨텍스트 독립성 외에 **실무와 컨펌 모델을 분리**한다.
- 모델 exit0은 계획 승인/제품 완료가 아니다. 컨펌은 범위·후보SHA·검사·남은 위험과 판정을 기록한다.
- 사용자 마일스톤 승인은 Sol/Opus의 기술적 컨펌과 별개다.

## 선택 및 실패 처리

현재 중간 provider는 Claude Code Opus5, 실무 provider는 Codex Luna다.
상위 역할은 설정된 Astra 또는 Fable만 사용하고 자동 폴백하지 않는다. `fable`/`opus`/`sonnet` 이동 별칭 대신5세대전체ID를 사용한다.
호출 실패/권한 부족/모델 미지원은 오류로 기록한다. 요청 모델 대신다른세대/낮은effort를 조용히 쓰지 않는다.
실무 실패 시 중간 모델로 보내는 것은 **진단·계획·컨펌 이관**이지 상위 모델에게 구현을 떠넘기는 것이 아니다.

설정은 작업자/판정자 모델의 CLI 인자로 전달한다. 현재 대화의 모델 자체를 바꿨다고 주장하지 않는다.
실제 유료 루프 실행과 모델 접근권한 검증은 세팅/argv 모의시험과 별개다.

## 설정 인터페이스 (실행 비활성 유지)

`loop/loopctl.sh models`로 현재 라우팅만 조회한다. 기본은 다음과 같다.

```sh
LOOP_WORKER=codex
LOOP_STRATEGY_PROVIDER=codex  # claude로 바꾸면 claude-fable-5
LOOP_MIDDLE_PROVIDER=claude
LOOP_JUDGE=claude
LOOP_ASTRA_EFFORT=medium
LOOP_ASTRA_REVIEW_INTERVAL=10
LOOP_ENABLE_AGENT=0
```

허용한 Claude 대안은 strategy `LOOP_STRATEGY_PROVIDER=claude`, 실무 `LOOP_WORKER=claude`, 중간 `LOOP_MIDDLE_PROVIDER=claude`로
각각 독립 선택한다. 역할별 전체 모델ID는 `loop/env.sh`에 지정한다.
실제 호출 인자는 work Codex `-m <model> -c model_reasoning_effort=high`,
middle Claude `--model claude-opus-5 --effort high`, strategy는 Codex
`-m gpt-6-astra -c model_reasoning_effort=medium` 또는 Claude
`--model claude-fable-5 --effort medium`이다. strategy high는 분기·교착 근거를 남기고
`LOOP_ASTRA_EFFORT=high`로 명시한다. 이 문서는 실행 허가가 아니다.

현재 STOP을 유지한다. stage 명령과 모의 검증 범위는 `loop/README.md` 참고.

## 증거

- 설치 CLI 확인: `codex-cli 0.153.4`, `Claude Code 2.1.267`.
- Codex 로컬 `exec --help`의 `--model/-m`, `--config/-c`와 기존 로컬
  `model_reasoning_effort=high` 설정 경로를 사용한다.
- Claude Code는 전체 모델명과 `--effort medium|high`를 지원한다. 로컬 CLI 2.1.278의
  `--help`가 `fable` 별칭과 전체 예시 `claude-fable-5`를 명시한다.
  [공식 모델 설정](https://code.claude.com/docs/en/model-config),
  [공식 모델ID](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions).
- `claude-fable-5`, `claude-opus-5`, `claude-sonnet-5`로 고정한다. 별칭의 provider별세대 차이를 피한다.
- CLI 설정/공식ID 확인은 계정의 실제접근/쿼터 검증이 아니다. 이를 확인하기위해 유료세션을 자동호출하지 않는다.

## 최신 사용자 override — 2026-09-16 현재 세션

앞의 Opus 고정 선택은 이후 사용자 지시 “중간 계획 검수 다시 gpt-5.6-sol/high로 다시 변경”으로 대체한다. 현재 중간 계획/검수는 Codex `gpt-5.6-sol/high`, 실무는 `gpt-5.6-luna/high`, 큰 분기/교착만 Astra medium(필요 시 high)이다. CLI legacy 기본값과 현재 native agent 실행 모델을 혼동하지 않는다. 이 기록은 CLI/서비스를 시작하거나 실행 중 대화 모델을 변경하는 명령이 아니다.

## 최신 사용자 override — 2026-09-18T17:56:55.515225+09:00
이전Sol/Luna선택은사용자의Claude옵션동의+루프재개지시로대체한다. 중간계획/검수ClaudeCode`claude-opus-5`/high, 실무`claude-sonnet-5`/high. AstraCodexmedium큰분기전용유지. mainCodexSol대화는조율/운영검증만담당하며Claude모델이됐다고주장하지않는다. ClaudeCodeCLI2.1.275/firstParty Max로그인확인,모델유료호출성공은실제stage결과로별도판정. 새사용자재개허가가어제자정중지를대체하나실패카드자동재시는금지.

## 최신 사용자 override — 2026-09-20

큰 방향 strategy는 Codex `gpt-6-astra`와 Claude Code `claude-fable-5`를 명시적으로 전환할 수 있다. 내장 기본값은 Astra이고 `LOOP_STRATEGY_PROVIDER=claude` 한 항목으로 Fable을 선택한다. 실패 시 상대 모델로 자동 폴백하지 않는다. 모델 접근권한은 실제 유료 호출 전까지 미검증이며, 로컬 Claude Code 2.1.278 CLI의 모델 인자 지원만 확인했다.

## 최신 사용자 override — 2026-09-20 18:45 KST

현재 프로젝트 로컬 strategy 선택을 Astra에서 Fable로 전환했다. `loop/env.local.sh`의
`LOOP_STRATEGY_PROVIDER=claude`가 다음 `loopctl strategy`부터 적용된다. Astra 설정과 명령
배관은 되돌릴 수 있는 대안으로 유지하지만 자동 폴백은 하지 않는다.
