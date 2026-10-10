# 모델 역할 계약 — 2026-10-04 사용자 최신 전환

사용자 지시: “큰 방향/계획은 클로드 오푸스로 하도록 하자”, 이어 “코덱스 -> 클로드로 스위치 하자”.
이 계약은 이전 Codex/Fable 역할 지정과 충돌하는 부분을 대체한다. G1 목표·검증·안전 범위는 바꾸지 않는다.

| 역할 | 선택된 provider/model | effort |
|---|---|---|
| 큰 방향·상위 계획(strategy) | Claude Code `opus`(최신) | high |
| 중간 계획·독립 검토/컨펌(middle) | Claude Code `opus`(최신), 별도 fresh 세션 | high |
| 실무 조사·코딩·테스트·수정(work) | Claude Code `sonnet`(최신) | high |
| 시각 판정(judge) | Claude Code `opus`(최신) | high |

## 역할 경계 / 실행

- 실제 hands-on 게임/하네스 구현은 Sonnet work, 독립 최종 기술 컨펌은 fresh Opus middle이다.
- Opus strategy는 큰 분기·구조적 선택·반복 교착에서만 호출한다. 중간 검수와 같은 모델이어도 별도 fresh 세션과 별도 역할이다.
- work가 자기 결과를 최종 승인하지 않는다. 컨펌 모델은 직접 구현을 대신하지 않는다.
- CLI의 내부 `astra` 역할/명령 이름은 strategy 호환 이름일 뿐, 실제 모델은 `--model opus`다.
- 이전 CLI 안내의 Astra/Fable 전용 문구보다 이 최신 사용자 계약과 실제 launch argv가 우선한다.
- `opus`/`sonnet`은 Claude CLI의 최신 별칭이다. 실제 resolved ID는 해당 호출의 로그에 기록하며 미실행 모델 ID를 추측하지 않는다.
- 모델 미지원/접근 실패는 근거를 남긴다. Codex/Fable/다른 세대 또는 낮은 effort로 자동 폴백하지 않는다.
- 매 stage 새 세션, 최대1lap을 leader가 연결한다. 무한 유료 daemon/systemd를 새로 켜지 않는다.
- 이전부터 실행 중이던 Codex lap945는 격리 게임/cleanup/검사를 안전하게 마무리했다. 이후 호출은 Claude다.
- 모델 Fast OFF 유지. 기존 `/fast` 지시보다 2026-10-04 해제 지시가 우선하며 `make check` 검사명 Fast는 계속 유효하다.
- G1 달성까지 안전한 구현→실행→수리→독립검수를 자율 연결하고 약10분마다 보고한다.
- exit0은 계획 승인·제품 완료가 아니다. 사용자 마일스톤 승인과 모델 기술 컨펌은 구분한다.
- 이 파일은 루프 역할 설정 계약이며 현재 채팅 세션 모델 자체를 바꿨다고 주장하지 않는다.

## 이전 계약 provenance

전환 전 전문은 `docs/history/20261004_model_routing_before_claude_switch.md`에 byte-exact 보존했다. SHA256 `40c76a7f6e656ff32c1c89d7caf1ebc96beb25065cd5529546de03e6eff435c2`.
