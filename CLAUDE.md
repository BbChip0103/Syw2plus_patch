# Claude Code 진입점

최상위 안전 계약은 AGENTS.md, 제품 계약은 docs/DESIGN.md다.
루프 세션은 loop/PROMPT.md의①~⑥을 따르고 매번 새 세션을 쓴다.

- 우선 입력: docs/feedback/INBOX.md, APPROVALS.md의 반려
- 현재 다음 한 가지: docs/STATUS.md
- 목표: docs/DESIGN.md의 최신 사용자 판단 순서를 따른다. 현재 최우선은 G1(G6·G7 2026-10-06 달성·종료) 원본 구성1600×1200
  (G2 전비 상한 5000 확정, G4·G5·G7은 2026-10-10 공식 ESL 지원으로 종결·중복 패치 없음, G8 전비1500–500–5000, G9 시작 자리 고정, G10 기지가 바뀐다(낮은 우선순위), 최대16인 G3는 중단)
- 기억: docs/history/laps/ + 후보SHA/가설/측정/실패/다음 작업
- 검증: make check, checks/safety.sh check; 실제 원본/부하/멀티는 별도
- 검증 과잉 방지: AGENTS.md의 해당 절을 따른다. 관련 회귀→요청 범위의 실제 게임 시험 우선(싱글에 멀티 자동 추가 금지); 보조 도구만 2회/60분이면 확장 중단·결과 보고. 같은 후보·같은 범위 증거는 재사용하고 종료 조건 충족 시 끝낸다. 도구 검사로 제품 완료를 대신하지 않는다.
- 제어: loop/loopctl.sh (다른 저장소 서비스와 분리, 현재 비활성)

전체 재현 엔진의 큐/상태/승인을 가져오지 않는다. 원본/참고 저장소 쓰기 금지.
커밋/푸시/유료 세션은 현재 설정 작업으로 허용된 것이 아니다.

모델 계약은 docs/MODEL_ROUTING.md. work·middle·judge·strategy의 provider는
Codex·Claude Code 사이에서 자유롭게 바꿀 수 있고 현재 선택은 그 문서와
loop/env.local.sh가 정한다. 루프 root도 Claude Code나 Codex 세션이 맡을 수 있다.
설정한 모델 실패 시 다른 모델/provider로 자동폴백 금지.
