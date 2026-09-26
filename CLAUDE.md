# Claude Code 진입점

최상위 안전 계약은 AGENTS.md, 제품 계약은 docs/DESIGN.md다.
루프 세션은 loop/PROMPT.md의①~⑥을 따르고 매번 새 세션을 쓴다.

- 우선 입력: docs/feedback/INBOX.md, APPROVALS.md의 반려
- 현재 다음 한 가지: docs/STATUS.md
- 목표: G5 드래그 선택 20→50(최우선), 원본 구성1600×1200, 활성8인 전비5000 안정성,
  길찾기/자유대전AI (최대16인 G3는 중단)
- 기억: docs/history/laps/ + 후보SHA/가설/측정/실패/다음 작업
- 검증: make check, checks/safety.sh check; 실제 원본/부하/멀티는 별도
- 제어: loop/loopctl.sh (다른 저장소 서비스와 분리, 현재 비활성)

전체 재현 엔진의 큐/상태/승인을 가져오지 않는다. 원본/참고 저장소 쓰기 금지.
커밋/푸시/유료 세션은 현재 설정 작업으로 허용된 것이 아니다.

모델 계약은 docs/MODEL_ROUTING.md. Claude Code는Opus5/high로 중간계획·컨펌,
Sonnet5/high로 실무를 맡는다. 큰방향/상위계획은선택에 따라Codex Astra 또는
Claude Code Fable이 맡으며 기본 effort는medium, 필요 시high다.
전체ID claude-opus-5/claude-sonnet-5 사용, 다른세대자동폴백금지.
