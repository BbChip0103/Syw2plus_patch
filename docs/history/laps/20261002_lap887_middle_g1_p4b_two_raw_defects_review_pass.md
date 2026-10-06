# 2026-10-02 | lap887 middle | G1 P4b 두 raw 검증 결함 독립 offline 수용

- 지정 역할/provider: 중간 tier 진단·계획·확인, Codex 현재 새 세션. 실제 exact model ID/effort는 독립 증명하지 못했으며 Sol/Opus 실행 증명을 주장하지 않는다. 실무 lap886과 분리된 새 컨텍스트 검수다. counter887 읽기만, subagent/commit0.
- ①~⑥: PROMPT 먼저 → AGENTS/INBOX 최신 지시/APPROVALS 반려 → STATUS 전체 → DESIGN1~4·MODEL_ROUTING·lap885/886·사용자 한정승인 → 이전 source/raw 검수 → Fast/offline → 결과·다음 기록. 시작 STOP 없음, lap885 ESCALATE_SOL 존재. 최신 사용자 승인으로 두 결함 검수만 진행; G2 5000/G3 중단/G4 보류/G5 종료 유지.
- 목표/가설: lap886 raw seq gap 및 taken pre-tick branch/no-update return PTID substitution 수리가 정상 producer/history를 수용하고 변이 baselineA/B를 durable HOLD/candidate0, live snapshot/input0으로 거부하는가. PASS는 이 두 결함의 offline 수리 수용뿐이다. G1/B' milestone 경계 아님.
- 입력/보호 SHA: source `5c33daf2a5da708007c850f278ee106b743a6f781da9cabbf58167f51aeb3336`, tests `73d7ef923907def812d7ffade0a7cc6a467c3b09ef31afa24c8e9aea6aa049aa` = lap886 MATCH. 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 직접 재해시 MATCH. 원본·save·source/tests·historical3 lane result/raw 입력10개 SHA 전후불변.
- 변경: 이 기록, STATUS, APPROVALS, 과거 marker byte-exact archive, loop/ESCALATE_SOL 해소 및 loop/STOP 생성. 공유 temp에 신규 offline scripts/deep-copy JSONL/JSON·실행 불가능한 텍스트 DLL/EXE hash fixture만 생성. 게임/검증 구현/tests/EXE/DLL/HD/validator/임계값/golden/기존raw/원본/참고 변경0. 기존 dirty 작업 보존, uncommitted.

## 독립 확인 결과 — PASS_SCOPED_OFFLINE_REPAIR

- source `tools/g1_saved_scene_probe.py:610` 공통 checker가 run-local seq=1..N 연속성과 PID/global-thread/PTID envelope를 확인하고, taken branch↔no-update terminal의 attributed seq/address 및 PID/global-thread/PTID/call/tick을 비교한다. :655 parser 및 :855 live raw gate가 이를 호출한다. producer :1370 부근 add는 seq를 1씩 증가시키고 flush/fsync하며, no-update terminal은 같은 thread context의 taken branch seq/address를 기록한다. 따라서 기존 gap/PTID 누락의 추적 가능한 원인이 수리됐다.
- historical lap880 r2 원래3 lane raw를 deep-copy하여 baselineA/B 각각 false branch 한 행 삭제(재번호 없이 gap) 또는 첫 no-update return PTID의 두 번째 정수만 변경. 실제 `_scroll_phase_observation`→`_run_scroll_phase_orchestration` 재생 총5경우: 정상 parser/control PASS·candidate Python stub1·pair PASS_BOUNDED_SCROLL_DIAGNOSTIC, 변이4건 parser INVALID/control 및 durable baseline-control-acceptance.json HOLD·candidate SKIP/calls0·pair HOLD/exit2. 기존 raw 자체의 오류나 제품 divergence를 주장하지 않는다.
- live 확인은 complete future raw가 아닌 각 pause return seq까지의 historical prefix로 수행했다. baselineA/B ×5 checkpoint ×정상/gap/PTID =30건. 현재 `_run_lane`의 실제 AST :2621 preflight/초기화와 :2644 snapshot/input 조건문을 추출 실행했다. 정상10건 snapshot1/input1, 변이20건 snapshot0/input0·INVALID_CLEANUP. 정상 검수의 raw prefix를 false reject하지 않으며 invalid raw는 실제 조건문에서 key-down 전 차단됨을 독립 확인. snapshot/input 함수는 mocks이고 게임 실행/입력은0이다. release/ack live runtime 전체를 새로 실행한 증거는 아니다.
- 기존 회귀 `tests/test_g1_saved_scene_probe.py` **123 passed /1.86s**. generated GDB producer fake-thread handshake/branch/no-update→pause→release→ack 및 parser 정상 수용 회귀 포함. 해당 파일 새 변경 없음.
- 현재 수용 범위에서 서로 충돌하는 raw/구현 근거, 미설명 필수 게이트 실패3회, 새 범위 밖 결함을 발견하지 않았다. 추가 실무 수리 handoff는 불필요하다. scope 수용 후 G1/bounded diagnostic/B' HOLD는 유지한다.

## 실행/산출물 및 검증 한계

- artifact root `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap887_middle_raw_review/`.
- 명령 `PYTHONPATH=. .venv/bin/python <artifact-root>/replay.py`; script SHA `dff4a2408f20992ac21f1404fe2924d73cd98eb2f409f8ae1cc7cada193fdc2f`, recalculation.json SHA `a9fc0ccf22abcc8714587d63a4207ba23996598fe62ddb63173a917c5ecb85f5`. JSON에 10입력 전후 SHA 및 normal/4변이 parser/control/live 결과 보존.
- 명령 `PYTHONPATH=. .venv/bin/python <artifact-root>/live_ast.py`; script SHA `85b56f2e937b147a35dbed7204e06255296c13d6564b4d1391dac0101e16d26f`, live_ast.json SHA `7f844e21bf383c3612a43e8393815b27fd7a72f6b964b82d7d30223b4ce1f18d`. 각30경우 snapshot/input 수·reason·release 상태 보존.
- `make doctor` exit0·original verified. optional root runtime manifest absent/RuntimeSafetyError는 알려진 부가검사 한계이며 이번 runtime 미실행과 구분한다. `make lint` ruff/compileall PASS, `make typecheck` mypy10files PASS. safety/context 및 마지막 full `make check`는 모든 fingerprint-bearing 기록을 쓴 후 수행, 수치/최종fingerprint는 STATUS에만 보강한다.
- 직전 lap886 full Fast 원로그/exit 열람: 1427 passed·5 skipped/936.93s 및 ruff/compileall/mypy/context PASS. 전역 full-test-latest.result는 stale로 현재 승인에 사용하지 않는다. 이번 기록 이후 현재 full Fast는 아직 미검증이다.
- game/build/24k/144k/UI 캡처/패치 생성·원복 SKIP: 이번 승인·변경은 offline observer 검증에 한정하고 바이너리 변경은 없다. 활성인원/군대/지도 수치·새 후보 EXE 없음; historical save fixture 및 mock calls를 fresh runtime 증거로 쓰지 않는다. B' 전체 gate/C fresh3 성능/D-1 PS3 census/HUD/coverage/두번째장면/사용자 승인 여전히 미충족.
- lap885 marker 원문1871 bytes SHA `8fcd17fa4d71712b60f4cb6b547f4b32752e7d4e18afe474778b524a95068216`는 `docs/history/20261002_lap887_prior_lap885_escalate_sol_archive.md`에 byte-exact 보존 후 이번 독립 수용에 따라 제거한다. 과거 HOLD/STOP/반례/사용자 승인 삭제·재해석 없음.
- loop/STOP은 두 결함 수리·독립검수 승인 소진으로 추가 자동 work/runtime를 막는다. 이번 마지막 Fast까지 기다린 뒤 종료하며 유료/CLI/team/service 추가 호출 없음.
- 다음 한 가지: 두 결함 offline 독립 수용 결과를 사용자/운영자에게 보고하고 **새 범위 결정 전 STOP 유지**. runtime/B'/C/P5/G1 확대를 이 수리 승인으로 자동 재개하지 않는다. 새 제품 승인/마일스톤 마감 아님.
