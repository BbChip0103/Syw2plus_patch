# 2026-09-25 | lap 591 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`(effort 세션 비노출; 계약 모델 Fable/Astra 대체) / strategy 상위계획. 게임 코드·바이너리·runner·공유 temp raw는 수정하지 않았다.
- 가설 / 사용자 관찰: lap590 middle §140 `REJECT / BLOCKED(plan_contract)`가 맞는지 확인한다. W49S 카드가 Q12-2 `(나)`를 "AI 8명"으로 좁혔다는 주장과 "현행 canonical 활성8명=로컬 사람1+AI7"이라는 근거를 따로 검증한다.
- 예상 PASS / FAIL 조건: 원문·코드·기존 raw가 §140과 모두 맞으면 전면 동의 후 1+7로 정정한다. 근거 일부가 기존 raw와 어긋나면 부분 동의하고, 두 역할 구성을 모두 허용하는 계약으로 정정한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `docs/work/active/G2_STRATEGY_W49S_LOBBY_START_SCREEN_LAP589.md`(정정 전 SHA256 `9eed66d564c615045b320cbeb2768badb1869bf26d1b0fe8f992b8d1aaed2976`), 이 기록, `loop/ESCALATE_SOL` §141, `docs/feedback/INBOX.md`, `docs/STATUS.md`. 제품 source·runner 변경0, 커밋0. 최종 fingerprint와 Fast 결과는 STATUS에 기록한다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 실행0. 원본 `b56986e0…a8ac`, 결합 후보 `dfdc91ad…3883`, map100×100·cap5000·혼합 fixture는 그대로다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 읽기 전용 대조만 했다. `tools/runtime_env.py:5729` `_g2_initial_creation_gate`(owner0 `ai=0`, 1..7 `ai=1`, config seed42 검사). `:5133` `G2_CREATION_GOAL="_custom_game_chain_inject_g2_eight_seed42"`. `tools/inmm_stub/control_executor.c:457` `G2_EIGHT_AI_GOAL="…_g2_eight_ai_seed42"`. 공유 temp `g2_capacity/` 아래 lap570 W45R·lap573 W46·lap575 W47·lap581 W49·lap587 W49R 각 runner의 `NEW_GOAL`과 `ai_flags_at_ps3`를 확인했다. S5′ 제출문 57·73행도 대조했다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **N215(신규):** W45R/W46/W47/W49/W49R 다섯 run은 모두 `NEW_GOAL="_custom_game_chain_inject_g2_eight_ai_seed42"`, `ai_flags_at_ps3=[1,1,1,1,1,1,1,1]`이다. 즉 G2 안정성 증거 계보는 **AI 8명(R-AI8)**이다. `runtime_env`의 1+7 gate(`g2_eight_seed42`)는 이 계보 runner가 호출하지 않는다. 제출문 57행 "모든 증거가 로컬 8 AI다"와도 맞는다. 따라서 §140의 "지금까지의 canonical 활성8명 계약은 1+7"은 틀렸다. `runtime_env` 경로에서만 맞다.
  - §140의 본 결론은 **동의**한다. Q12-2 `(나)`는 "사람 1명+AI 또는 AI 8명"이다. UI 로비가 로컬 슬롯을 비울 수 없을 때 `NOT_FEASIBLE(ui_8ai)`로 닫으면 허용된 1+7 구성을 잘못 거부한다. `g1_baseline` 양성이 default two-player라 8명 설정 근거가 아니라는 지적도 코드(`runtime_env.py:7526`)로 확인했다.
  - §140 제안 2의 고정 vector `[0,1,1,1,1,1,1,1]` 단독 요구에는 **동의하지 않는다**. 그것만 요구하면 반대로 기존 raw와 같은 R-AI8을 배제한다.
  - 판정: **§140 부분 동의**. W49S를 정정했다. 활성 8명은 R-AI8(우선) 또는 R-1L7(`ai==0` 한 명=`local_index`, 나머지7 AI)이다. 실패 라벨은 `NOT_FEASIBLE(ui_8active)`다. PS3 역할 gate §3.5를 추가했다. goal-chain 전용 config/seed 검사는 UI 경로에서 보고 전용이다. R-1L7 결과는 R-AI8 안정성 raw를 대체하지 않는다.
  - **N216:** lap588~591은 네 회차 연속 새 실행 증거가 없다. PROMPT ③에 따라 strategy가 판정했다. 화면 축은 정확히 한 번 더 계속하고, 다음 회차는 반드시 W49S work다. 실패하면 "미검증 확정"으로 닫고 재정정·재계획은 없다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: UI 로비에서 7~8 AI와 100×100을 고를 수 있는지는 미확인이다. 이것이 S0 몫이다. cap5000은 결합 후보가 주는 값으로 보지만 UI 경로에서는 PS3 gate로 다시 확인한다. G2 PASS·사용자 승인·마일스톤 전환은 없다. Q12 A·나·iv는 유지한다.
- 다음 한 가지: work가 계획 회차 없이 정정된 W49S §3(S0 포함)→§3.5→§4를 fresh foreground 정확히 1회 수행한다. 그 뒤 middle이 raw/PNG를 재계산한다.
