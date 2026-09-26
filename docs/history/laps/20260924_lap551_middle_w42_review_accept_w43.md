# 2026-09-24 | lap 551 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Codex native session / session model ID 비노출 / high 요청, 지정 역할 middle(진단·계획·확인). 게임 코드 hands-on 수정 0.
- 가설 / 사용자 관찰: lap550 W42의 work 자기 라벨 `ENGAGED_2STAGE`가 work summary를 보지 않고 raw assignment/trace/events/samples/T0에서 재현되면 ACCEPT하고, 고정 분기대로 W43 24k 카드를 발행한다.
- 예상 PASS / FAIL 조건: 전열 (0,1)(4,5) 모두 `hit_attr≥1`, 각 전열 walk 중앙≥7, A5 위반0이면 PASS/`ENGAGED_2STAGE`; 핵심 수치 불일치·게이트 실패는 REJECT/승격.
- 변경 파일 / source fingerprint / 커밋: 제품 source 변경 0, 커밋0(unborn HEAD, 기본 `LOOP_ALLOW_COMMITS=0`). 문서 `G2_S1_MOVE_THEN_ATTACK_24K_SOAK_W43_LAP551.md`, 이 lap 기록, STATUS/INBOX/ESCALATE 갱신. temp 검수기 `recompute_w42.py` SHA `9933733b…cb6f`. 세션 입력 source fingerprint `0f9ff885…371a64dd14bd`.
- 원본·후보 SHA / 환경 / 활성 플레이어 / fixture: lap550 보존 사본 원본 `b56986e0…c9c08a8ac`, 후보 `a10024de…a1bb2d68`, DLL `822c802e…31aed`; 8 AI, 100×100, gate-legal 시딩 type5×100/type7×25/type2×60/type46×20, owner별 used4,950. 이번 middle은 새 게임 실행0이며 lap550 현재 캡처를 검수했다.
- 실행 명령 / 근거: `make doctor`; `make check`; `checks/safety.sh check`; `recompute_w42.py` 2회. 현재 source에서 835 passed(511.37s)+ruff+compileall+mypy+`CONTEXT_PASS`, `SAFETY_PASS`. 재계산 stdout SHA가 두 번 모두 `4f50f11d…5d462`; 입력 SHA trace `c5bd3e6d…a8f4`, events `68b5a807…68ec`, samples `27390c24…026c`, assignment `d7e162aa…273`, T0 `f3451bc7…fa0`.
- 측정값 / 판정: **PASS / ACCEPT / `ENGAGED_2STAGE` 일치.** A1 4,950×8, A8' PASS, H20 위반0, A5 7종 위반0. (0,1) 도착33/60·hit_attr33·walk 7/7/23·kills9·EXIT_C9/OTHER24; (4,5) 도착55/60·hit_attr55·walk7/7/9·kills5·EXIT_C7/OTHER48. 합산88/120=0.7333, `band_engaged=0`.
- 정정/한계: 보고 전용 `move_stop_early`는 work in-memory/bulk snapshot 요약 4(0,1)+4(6,7)이나 개별 raw trace 재계산은 2+0 하한이다. 같은 offset을 서로 다른 read 시점에 읽어 전이가 trace에서 빠질 수 있다. 라벨 입력이 아니므로 ACCEPT를 바꾸지 않되 W43 H31에 same-snapshot 상태전이 JSONL을 의무화했다. fresh runtime 재실행은 W42 1회 예산 때문에 SKIP했고 과거 실행을 새 실행으로 주장하지 않는다.
- 다음 한 가지: work tier가 W43 카드대로 네 짝 전열을 사전 탐색한 뒤 이동→공격 2단 입력 24k 게임 1회를 foreground 완주한다. `DRIVEN_CYCLE_STABLE`만 다음 middle의 144k 발행 조건이다.
