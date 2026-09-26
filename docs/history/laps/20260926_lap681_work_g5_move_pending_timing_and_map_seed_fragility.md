# 2026-09-26 | lap 681 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work). (loop/env.local.sh 임시 전환 유지: Codex 401 이후 middle=opus-5, work=sonnet-5.)
- 가설 / 사용자 관찰: STATUS.md lap680 "다음 한 가지" 그대로 수행 — v3 크래시-수정 후보(`e5004764…bac3de6977`)의 MOVE `+0x384` pending 0/50 원인을 좁힌다: ① MOVE만 `command`(0x290) 필드로 재확인(pending이 안 맞는 것인지 먼저 배제), ② 안 되면 `FUN_0040C640` 진입-카운트로 MOVE/ATTACK 소비 경로 차이 확인, ③ 원인이 좁혀지면 최소 수정 후 원본20/후보50 paired 재검증.
- 예상 PASS/FAIL: pending 필드가 MOVE에 실제로 안 맞으면(타이밍 문제) 더 긴 대기로 50/50이 나오고 최소 수정 없이 paired PASS. 진짜 소비 경로 차이/회귀면 최소 수정 필요.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(LOOP_ALLOW_COMMITS=0). **제품 EXE 0 변경** — 이번 lap은 순수 read-only 진단 도구만 추가했다.
  - `tools/g5_v3_order_type_header_trace.py`(신규): hook site(`0x004AE550`, 이제 cave로 가는 5바이트 near jump) 진입 시점에 order-type 헤더(`word[esp+8]`)와 실시간 선택 카운트를 non-invasive breakpoint로 기록.
  - `tools/g5_v3_order_type_header_probe.py`(신규): 위 trace를 MOVE·ATTACK 클릭 각각에 걸고, MOVE 클릭 후 0.3s 대신 **3초** 대기 후 `command`/`pending` 필드를 재확인.
  - `tools/g5_move_attack_convergence_probe.py`(신규): 고정 지연 대신 0.5s 간격으로 최대 12초 **폴링**하며 MOVE(`command==3`)·ATTACK(`command==4`+target uid) 수렴 곡선을 기록하는 원본20/후보50 paired 도구.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `b56986e0…c9c08a8ac`(3회 실행 모두 불변, `source_unchanged=true`). 후보 `e5004764…bac3de6977`(lap680과 동일, 무변경). 격리 Wine/Xvfb 1600×1200, PS3 solo owner0, dense fixture worker(slot1198) 앵커 7×8 grid 55기 SEED_TYPE=2. **지도/시작 위치는 시드 고정 없음**(아래 §측정값 참고).

## 실행 명령 / 로그 / 캡처 경로

1. `PYTHONPATH=. .venv/bin/python -m tools.g5_v3_order_type_header_probe --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap681_order_type_header_061042` → exit 0.
2. `PYTHONPATH=. .venv/bin/python -m tools.g5_move_attack_convergence_probe --variant candidate --artifact-root .../20260926_lap681_convergence_candidate_061349` → exit 0 (측정 자체는 완주했으나 목적지 무효, 아래 참고).
3. `PYTHONPATH=. .venv/bin/python -m tools.g5_move_attack_convergence_probe --variant candidate --artifact-root .../20260926_lap681_convergence_candidate_retry_061631` → exit 0 (재실행도 목적지 무효).
   전체 artifact(JSON+캡처+probe.log)는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/`의 위 세 디렉터리에 보존.

## 측정값 / 판정

- **①(pending 필드가 MOVE에 안 맞는 것인지 먼저 배제): 배제됨 — 타이밍 아티팩트였다.** 실행1(`order_type_header_probe`, worker=(142,42) type31)에서 MOVE 클릭 후 3초 대기하자 `pending_written_count_after_3s=50/50`(lap680의 0.3s 스냅에서 0/50이었던 것과 동일 조건, 대기만 늘림) — **MOVE 브로드캐스트 자체는 완전히 성공한다.** 같은 실행에서 `command3_count_after_3s=20/50`(30기는 아직 `command==1` idle)로, pending→command 반영이 점진적임을 확인. ATTACK은 1초 대기로 `pending_written_count_after_1s=50/50`, `command==4` 41/50 도달(9기는 아직 반영 전) — MOVE와 동일한 "점진적 소비" 패턴이며 별도 회귀가 아니다.
- **hook site(`0x004AE550`) 자체는 클릭 이후 단 한 번도 히트하지 않았다**(`hits=1`이지만 `post_marker_hits=0` — 그 1회는 클릭 이전, 아마 lap676이 이미 확인한 22개 UI/알림 flush 호출 중 하나). 즉 이번에 관측된 실제 MOVE/ATTACK 클릭은 v3가 후킹한 레코드 빌더를 통해 관측되지 않았다 — v3 docstring의 "라이브 트레이스로 헤더 3/4 확인" 주장은 이번 두 클릭에서 재현되지 않았으나, 어차피 pending 전달 자체는 두 주문 모두 성공했으므로 이 경로 불일치는 이번 조사의 결론에 영향을 주지 않는다(별도 미해결 사실로만 기록).
- **②③(원본20/후보50 paired 재검증) 시도: 2회 연속 무효(목적지 좌표 문제) — 근본 원인을 새로 발견.** 실행2·3(`move_attack_convergence_probe`)에서 MOVE·ATTACK 둘 다 12초 내내 `matched_count=0`으로 전혀 수렴하지 않았다. 원인 조사 결과, **매 실행마다 슬롯1198 pre-existing worker의 unit_type과 world 좌표가 전부 달랐다**: 실행1 `type31 @ (142,42)`, 실행2 `type21 @ (92,21)`, 실행3 `type31 @ (42,42)`. `tools/runtime_env.py`를 확인하니 G2 진단 경로는 `_custom_game_chain_inject_..._seed42` 류의 **시드 고정 커스텀 게임 생성 체인**을 쓰는 반면, `tools/g5_candidate_drag_probe.py`를 비롯한 **모든 G5 확률 계열 probe는 시드 없는 평범한 "solo" 로비 플로우만 사용**한다(`click(462,169)` "solo" 선택 후 바로 ready). 즉 **G5 probe들은 애초부터 매 실행 지도/시작위치가 시드되지 않은 채였다.** 드래그 선택 사각형(`(200,170)→(730,445)`, 530×275px, worker 상대 픽셀로 fixture 자체가 배치됨)은 넓어서 worker 위치가 달라도 50/50 선택을 매번 성공했지만, **단일 픽셀 목적지(`(300,420)`)는 그 좌표의 실제 지형(빈 땅/건물/자원)이 지도마다 달라 무효한 목적지에 클릭하면 MOVE·ATTACK 모두 완전히 무반응(0/50, 12초 내내)**임이 실측으로 확인됐다. 이는 v3 코드의 버그가 아니라 **probe 방법론의 기존 취약점**이며, 오늘 우연히 2회 연속 재현됐다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 신규 도구 3개(전부 read-only 진단), 제품 EXE/원본 0 변경. `ruff check`(신규 파일 3개) 전부 PASS, `py_compile` PASS.
- 회귀/`make check`는 아래 §검증 상태에 기록.
- **핵심 결론(FEASIBLE):** MOVE `+0x384` pending 브로드캐스트는 **회귀가 아니다** — lap680의 0/50은 0.3s 스냅샷이 너무 일렀을 뿐이며, 3초 대기로 50/50(그리고 `command`도 점진적으로 20/50까지 반영)을 직접 관측했다. G5 MOVE·ATTACK 모두 "pending→command 반영은 즉시가 아니라 여러 틱에 걸쳐 점진적"이라는 동일한 정상 패턴을 보인다.
- **새 블로커(probe 방법론, 제품 아님):** G5 probe 계열이 지도 시드를 고정하지 않아 worker 시작 위치/지형이 매 실행 달라지고, 고정 픽셀 목적지(`(300,420)` 등)가 이번처럼 무효한 지형에 걸리면 원본20/후보50 paired 측정 자체가 통째로 실패한다(2회 연속). 다음 work가 이어서 검증할 한 가지: G2가 이미 쓰는 시드 고정 커스텀 게임 생성 체인(`tools/runtime_env.py`의 `_custom_game_chain_inject_*_seed*` 계열)을 G5 dense-fixture 플로우에 이식해 지도/시작위치를 고정한 뒤, **같은 3초+폴링 방법으로 원본20/후보50 paired MOVE·ATTACK 수렴**을 측정한다. 그것으로 G5 제품 milestone 남은 조건(멀티 동기화 표시 제외)의 마지막 실측 증거가 된다.
- 2단 독립 검수·3단 사용자 milestone 승인 없음(원래부터 없었음). G5 최우선·상시 지시는 미처리로 유지한다.

## 검증 상태

보호 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`는 3회 실행 전후 불변
(`source_unchanged=true` 전부). 후보 EXE는 lap680과 동일 SHA `e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977`
(무변경). 신규 파일 3개 `ruff check` PASS, `py_compile` PASS. 회귀
(`patches/selection/test_g5_selection_cap50_v{1,2,3}.py tests/test_g5_selection_inventory.py
tests/test_g5_pending_broadcast_snapshot_probe.py tests/test_g5_pending_broadcast_loop_probe.py
tests/test_g5_command_packer_xrefs.py`) → **30 passed**. `make check`(세션 내 포그라운드 완주, 로그
`logs/gates/20260926_lap681_make_check.log`) → **970 passed in 665.78s**,
ruff/compileall/mypy/`CONTEXT_PASS` 모두 PASS. `bash checks/safety.sh check` → `SAFETY_PASS`. 이 lap
실행 `game` 사본(2.7GB×2)은 각 실행 직후 삭제(디스크 33GB→38GB로 복구, manifest/output/prefix/로그는 보존).
- 다음 한 가지: G2의 시드 고정 커스텀 게임 생성 체인(`tools/runtime_env.py`
  `_custom_game_chain_inject_*_seed*`)을 G5 dense-fixture 플로우(`tools/g5_candidate_drag_probe.py`
  계열의 solo 로비 진입부)에 이식해 지도/시작위치를 고정하고, 이번 lap이 만든 3초+폴링 방법
  (`tools/g5_move_attack_convergence_probe.py`)으로 원본20/후보50 paired MOVE·ATTACK 수렴을
  재측정한다. 그것으로 G5 제품 milestone 남은 조건(멀티 동기화 표시 제외)의 마지막 실측 증거가
  된다.
