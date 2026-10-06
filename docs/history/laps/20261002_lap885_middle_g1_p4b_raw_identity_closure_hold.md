# 2026-10-02 | lap885 middle | G1 P4b raw identity closure 독립 검수 HOLD

- 지정 역할: 일반 middle(진단·계획·확인), provider Codex 현재 새 세션. 실제 모델 ID/effort의 독립 증명은 없어 Sol/Opus 실행을 가정하지 않는다. `loop/.lap_counter` 실제885 읽기만. 게임/source/tests/build/runtime/subagent/commit 변경0; 기존 dirty/untracked 작업 보존.
- ①~⑥: PROMPT 먼저 → AGENTS/INBOX 최신 지시/APPROVALS 반려 → STATUS 전체 → DESIGN1~4와 최신 override/MODEL_ROUTING → lap884 및 Astra 한정승인 검수 → offline 검사 → 결과·승격 보존. STOP/ESCALATE_SOL은 시작 때 없음. G1 현재, G2 5000·G3 중단·G4 보류·G5 종료 유지. 마일스톤 경계 아님.
- 목표/가설: lap884 최종 두 파일이 Astra 수용표의 exact raw identity와 gap/unknown/unresolved context 거부를 충족하는가. 정상 lane-local PID/PTID/call/nonce 차이는 허용하되 잘못된 baseline raw는 durable HOLD·candidate SKIP/calls0이어야 한다. PASS는 offline 수리 수용에 한정, B'/G1 수용 아님.
- 입력: lap884 work 기록, `docs/history/laps/20261002_strategy_g1_p4b_exact_identity_one_work_decision.md`의 normative gate, 현재 source/tests, lap880 r2 standalone3 및 원시 phase stream. source SHA `d868939c4b982b07aa72c902d04bbbe8ca21ca10d62dc446b5465c270102ee1d`, test SHA `7b5f8fb0638982525edd3e4985b2b974c4f0fdd6d42b0b71da11f4882b06b058`: lap884 MATCH. 보호 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 비합성 save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`: 직접 재계산 MATCH. 새 후보 EXE 없음.
- 수정파일: 이 lap 기록, STATUS, APPROVALS, `loop/ESCALATE_SOL`만. 공유 temp에 신규 offline script/JSON·raw deep-copy·stub fixture 보존. 원본/참고/golden/validator/임계값/EXE/DLL/HD/G2/G5/기존raw 수정0. stub DLL/EXE는 실행 불가능한 텍스트 해시 fixture이며 실제 runtime binary 증거 아님.

## 독립 확인 및 실질 충돌

- 기존 수리 확인: baseline A/B 수용 기록 게시 후 candidate 순서, completed phase↔pause PID/global-thread/PTID/call, pause/release/ack nonce, census inferior·stopped 상태 및 disk input SHA freeze/drift 경로를 읽었다. 현재 targeted115 PASS, 서로 다른 baseline lane-local identity를 가진 historical 정상 replay는 control PASS·candidate stub1회로 수용된다. 기존 phase-call/hash/release 누락 수리와 이번 잔여 결함을 구분한다.
- **raw seq gap 거부 미구현**: `tools/g1_saved_scene_probe.py:621`은 seq가 증가하는지만 검사한다. producer는 :1312 `add()`에서 1씩 증가시켜 모든 행을 flush한다. historical baselineB의 seq2(실제 `pre_tick_branch`, branch_taken=false) 한 행만 deep-copy에서 삭제하여 `1→3` gap을 만들었는데 parser PASS/invalid_reasons=[] 및 actual orchestration control PASS/candidate stub1회/pair PASS/exit0. normative gate의 “reject ... gap”과 충돌한다.
- **no-update terminal exact PTID 누락**: :643~649 no-update return 귀속은 call/branch seq/address/tick/global-thread만 대조한다. baselineB seq15의 `simulation_update_no_update_return` PTID를 `[3394319,3394319,0]→[3394319,3406664,0]`으로 바꾸되 PID/global-thread/call/tick은 보존했다. branch의 PTID는 원래 그대로인데 parser PASS와 control PASS/candidate stub1회/pair PASS/exit0. completed update entry/return에는 PTID 대조가 있으나 known no-update branch/return 경로는 빠져 있다.
- `_scroll_pause_matches_completed_phase`(:805)는 target call entry/return만 필터링하므로 위 두 raw 반례 모두 각5 checkpoint에서 `(True, PASS)`였다. 실제 host는 :2567/:2597에 이 함수를 호출한 뒤 snapshot/input에 들어간다. 이번 재현은 함수의 offline 호출이며 실제 게임 입력을 보내지 않았다. 잘못된 raw가 사후 parser에서도 거부되지 않는다는 점은 직접 재현했다.
- historical 정상 stream 전체를 현재 parser에 재입력하고, baselineB만 해당 반례로 바꾼 뒤 실제 `_run_scroll_phase_orchestration`을 호출했다. 원래 정상 raw 자체가 잘못됐거나 제품 simulation divergence가 재현됐다는 뜻은 아니다. 거부해야 할 corrupted/missing raw를 수용하는 검증 누락이다. historical 정상·변이2 모두 정상 source 상태의 control을 사용하고 candidate는 Python stub만 호출했다.
- 판정 **HOLD_RAW_IDENTITY_CLOSURE**, bounded diagnostic·B'/G1 HOLD. Astra 한정 gate/구현 근거 사이 실질 충돌이므로 사용자 즉시 중단 조건 적용. 추가 game/probe/full Fast 재시도 또는 새 work 허가를 임의로 하지 않는다. 근본 원인은 추적 가능한 parser/consumer 누락이며 middle은 게임·검증 코드 수리를 하지 않았다.

## 검사와 provenance

- `make doctor`: exit0, original verified. optional root runtime manifest absence는 알려진 subcheck 한계이고 새 필수 gate 실패 아님.
- `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_g1_saved_scene_probe.py`: **115 passed /1.90s**. `make lint`: ruff/compileall PASS. `make typecheck`: mypy10files PASS. 기존 tests에는 이번 raw gap/no-update PTID 반례가 없어 이 결과를 exact closure 승인으로 쓰지 않는다.
- 직전 `logs/gates/lap884-work-full-fast.log/.exit` 열람: exit0·1419passed/5skipped/964.07s·ruff/compileall/mypy/context PASS. 과거 source-matched Fast 확인이며 이번 history/marker 이후의 현재 fingerprint PASS가 아니다. 글로벌 latest 결과는 stale로 수용하지 않는다.
- **이번 full make check/FULL_TEST/build/runtime/24k/144k/patch 생성·원복 SKIP**: 사용자 실질충돌 중단 조건이 스킬의 full 검사보다 우선. 예약 파일로 검사를 넘기거나 과정exit0을 승인으로 쓰지 않는다. UI 변경0이라 새 캡처/입력·활성 인원/군대/지도/시간 측정 없음. 과거8player records는 활성8인 부하증거 아님.
- artifact root `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap885_middle_identity_review/`; 명령 `PYTHONPATH=. .venv/bin/python <artifact-root>/replay.py`. script SHA `e55237f5f14191ed9eaccfdc907080dde1390138ffd4d47626c2213c5c540f59`, `recalculation.json` SHA `da397769daa9ff69d1eb3a6740a55d47a9a61168394f46fd9799b526bfe795fe`. JSON에 source/tests/원본/save/3 lane result+raw SHA 전후 및 반례 출력을 기록; 입력10개 전후 모두불변. baselineB 원래 raw2161행 SHA `00e7b4e86caf324a96e2c78a12eb87fec0a82af84298de680a51af413238278a` 보존, gap deep-copy2160행.
- 검수 script 최초 실행은 존재하지 않는 `runtime_env.ORIGINAL_NAME` 조회 AttributeError로 반례 실행 전 실패했다. 현재 공식 `validate_original_source(SOURCE)[1]` 경로로 고친 뒤 정상 실행하여 위 증거를 얻었다. 프로젝트 코드 수리/원인불명 필수 실패3회에 해당하지 않는다.
- 종료 safety/context/scoped whitespace·문서크기·기록 SHA는 STATUS에 보강한다. lapcounter885 불변, commit0/uncommitted 유지.

## 승격 확인과 조건부 work handoff

- 승격 Sol/Astra는 현재 source 및 공유 temp 정상/변이 raw 재계산을 독립 확인해 수용 거부를 판정한다. 이전 Astra “딱1 work/60분”은 lap884에서 소비됐다. 기존 승인으로 추가 work 회차를 자동 연장하지 말고 continue/stop과 좁은 수리 허가를 명시한다. runtime/B'/C/P5/G1 완료 허가와 분리한다.
- 수리 허가 시 work Luna/Sonnet에 같은 두 파일만 넘긴다: producer run-local raw seq 시작/연속성과 full invocation identity를 raw parser·live consumer의 공통 조건으로 검사한다. taken pre-tick branch↔no-update return의 PID/global-thread/PTID/call/tick/seq/address·terminal 귀속을 exact하게 검증하고 prefix의 gap/duplicate/unresolved/unknown context를 snapshot/key-down 전에 거부한다. valid producer branch/no-update 및 서로 다른 lane-local identity를 false reject하지 않는다. 고정 r1 일정·baseline barrier·file freeze·rice/gdb-free/제품·validator·임계값/기존 raw 불변.
- 회귀 먼저: 정상 역사raw/producer handshake는 PASS, 위2변이와 누락/malformed identity를 baselineA/B 각각 raw부터 재파싱해 actual orchestration HOLD·durable reason·candidate calls0을 확인한다. live consumer는 invalid prefix일 때 snapshot/input0이고 cleanup만 가능해야 한다. 수리 targeted→lint/typecheck→기록완료후fullFast→새middle offline 수용 뒤에만 승인된 관측전용 격리진단 가능. 판정 필요 전 추가runtime 금지. 현재 운영 큐는 STATUS만 따른다.
