# 2026-10-02 | lap886 work | G1 P4b raw identity 두 결함 수리

- 지정 역할: hands-on work. 실제 provider/model/effort의 세션 증명은 없음; 모델 폴백 주장은 하지 않는다. lap counter `886` 읽기만, commit 없음.
- 목표/가설: lap885가 재현한 raw seq gap과 taken pre-tick branch/no-update return PTID substitution을 parser 및 live pre-input gate가 거부한다. 정상 historical stream과 lane-local PID/PTID는 계속 수용한다.
- 입력 근거: `docs/history/laps/20261002_lap885_middle_g1_p4b_raw_identity_closure_hold.md`, `docs/history/laps/20261002_user_g1_raw_two_defects_repair_authorization.md`, 현재 STATUS의 두 파일 handoff. 기존 raw/deep-copy는 수정하지 않았다.
- 변경 파일: `tools/g1_saved_scene_probe.py`, `tests/test_g1_saved_scene_probe.py`. 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 및 save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 보호 기준 불변. 후보 EXE/build/game runtime 없음.
- 수정: 공통 raw identity 검사에서 run-local `seq=1..N` 연속성, expected inferior/PID와 thread PTID/global identity를 확인하고, taken branch와 no-update terminal의 attributed seq/address/tick/call/PID/global-thread/PTID를 exact match한다. offline phase parser와 live pause preflight가 같은 검사를 공유하므로 invalid prefix는 snapshot/key input 전에 거부된다.
- 회귀: 수정 전 신규 gap/PTID 테스트 2건 모두 `PASS`(잘못된 수용)로 실패 확인. 수정 후 targeted 8 passed; 전체 `tests/test_g1_saved_scene_probe.py` **123 passed**. orchestration regressions는 baseline A/B 각각 invalid raw summary에서 candidate 호출0/HOLD를 확인한다. live preflight 변이 2종은 snapshot/input 호출0을 확인한다.
- Historical 재생: lap885 replay를 새 디렉터리 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap886_raw_identity_repair/`에서 실행. 정상 raw는 baselineA/B 후 candidate 호출, pair `PASS_BOUNDED_SCROLL_DIAGNOSTIC`; seq gap 및 no-update PTID 변이는 각각 calls `[baselineA, baselineB]`, control/pair `HOLD`, exit2. 입력 raw/result/source/test/original/save SHA 전후 전부 동일. recalculation SHA `64c093af6f55641d1341d3538fbbb99a30376b5babe33df7b4828dd01a3a1754`.
- 추가 검사: `make doctor` exit0·원본 verified(선택적 root runtime manifest 없음은 `RuntimeSafetyError`, 격리 runtime을 시작하지 않아 미사용); `make lint` PASS; `make typecheck` PASS; `checks/safety.py` `SAFETY_PASS`; `checks/context_limits.py` `CONTEXT_PASS`.
- 격리 게임/runtime, build, B'/C/P5, 캡처는 미실행/미변경. 이는 오프라인 검증 수리이지 bounded diagnostic/B'/G1 PASS가 아니다. 새 middle 독립 검수 전까지 해당 판정 HOLD.
- `loop/ESCALATE_SOL` 보존 SHA `8fcd17fa4d71712b60f4cb6b547f4b32752e7d4e18afe474778b524a95068216`; 삭제/재작성하지 않았다. 구현 SHA `5c33daf2a5da708007c850f278ee106b743a6f781da9cabbf58167f51aeb3336`, 테스트 SHA `73d7ef923907def812d7ffade0a7cc6a467c3b09ef31afa24c8e9aea6aa049aa` (Fast 전).
- Fast: 변경/이력 기록 후 `make check` 실행 예정. 현재 full Fast fingerprint는 아직 PASS가 아니다. 실행결과는 STATUS에만 보강한다.
- 다음 한 가지: full Fast 결과 보강 후 새 Sol middle이 lap885 historical raw의 정상/변이 재생, parser/live gate와 baseline A/B candidate calls0을 오프라인 독립검수한다. 이 두 결함 승인 소진; 새 범위 밖 결함이면 중단·승격.
