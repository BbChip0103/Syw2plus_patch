# 2026-09-11 모델 라우팅 사용자 변경

- 실무: Codex `gpt-5.6-luna/high` 유지.
- 중간 계획·진단·컨펌 및 judge: Claude Code `claude-opus-5/high`로 전환.
- 큰 방향: Codex `gpt-6-astra/medium`을 기본으로 사용하고, 큰 분기나 반복 교착에서만 필요 시 `high`로 올린다.
- Astra 호출은 정기 자동 실행이 아니다. 운영 cadence는 대략 10개 work/middle lap당 1회 이하이며 실제 분기·교착 근거가 우선한다.
- `loop/env.local.sh`에 현재 선택을 고정했고, tracked 설정 인터페이스는 역할별 effort를 CLI argv에 명시한다.
- 검증: `tests/test_model_routing.py` 17 passed. 최초 전체 Fast는 상위 셸의 응답 없는 `DISPLAY=:10`을 console-only Wine fixture가 상속해 `wineboot` 두 건이 timeout 됐다. `DISPLAY` 제거 후 두 대상 2 passed, 전체 173 passed와 safety PASS를 확인했고 fixture 자체도 DISPLAY를 제거하도록 고정했다.
