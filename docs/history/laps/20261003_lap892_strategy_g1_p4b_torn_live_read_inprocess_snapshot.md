# 2026-10-03 | lap 892 | G1 W70 P4b — B' final 차이는 찢어진 live 읽기, 표본을 in-process 완료-phase로 옮기는 P4b-S 카드 발행

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향/master-plan) 역할,
  `loop/env.local.sh`의 `LOOP_ASTRA_EFFORT=high`(세션 안에서 effort 값 자체는 비노출). 자동 폴백 아님. `loop/.lap_counter`는
  892를 읽기만 했다(러너 evidence 블록은 lap=891 표기, PROMPT 규칙대로 파일 값 사용). 게임 코드/하네스/validator/바이너리 수정0,
  게임 실행0, 빌드0, subagent0, 커밋0.
- 가설 / 사용자 관찰: lap890 work는 gdb 없는 B' pair의 final tick24861에서 player 2명·unit 1개 차이로 HOLD했고, lap891 middle은
  완료 phase 미증명으로 `HOLD_PHASE_ATTRIBUTION_UNPROVEN`·승격했다. 이 세션의 가설: (1) 차이는 host가 실행 중인 프로세스를 읽는
  표본 방식의 산물이고, (2) 기존 raw만으로 그 여부를 가릴 수 있으며, (3) 맞다면 고칠 것은 진단 일정이 아니라 표본 시점이다.
- 예상 PASS / FAIL 조건(이 판정의; (a)는 재계산 전에, (b)는 tick별 표를 본 뒤 전수 검사로 정함): (a) lap890 두 lane의 서로 다른 필드 값이 인접 tick의 완료-phase 상태
  (24860 lap888, 24862 lap874)로 설명되면 "표본 시점" 귀속을 지지, 어느 완료 상태에도 없는 구조적 차이(유닛 생성/삭제 불일치,
  AI/group 변화)가 있으면 기각하고 lap891 제안을 채택. (b) 완료-phase snapshot 전부에서 성립하는 불변식을 lap890 live snapshot이
  깨면 "찢어진 읽기" 확정, 못 찾으면 가설로만 둔다.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/work/active/G1_STRATEGY_W70_P4B_S_INPROCESS_SNAPSHOT_LAP892.md`
  (SHA256 `205424284e6f438be91c4a656e51734f2128c4e1c173350fb3f3b39eaa87a895`), 신규
  `analysis/memory_maps/g1_p4b_update_callsites_inprocess_snapshot_lap892.md`
  (`1ada92e3f84ddbe0095a73bba72b971f466f1f705e86a4192b2caa0e523fae7f`), 이 기록, 신규 보존본
  `docs/history/20261003_lap892_prior_lap891_escalate_sol_archive.md`(lap891 `loop/ESCALATE_SOL` 그대로, SHA256
  `0a5d89eaaee96fb2da677b08e54da7841bcf78e01d3722fd3bd674aac4517823`), `docs/STATUS.md`, `docs/feedback/INBOX.md`,
  `docs/feedback/APPROVALS.md`. `loop/ESCALATE_SOL`은 보존본과 SHA 일치 확인 뒤 제거했다(판정으로 해소, 다음 회차를 work로
  보내기 위함 — lap853·858·863 선례). uncommitted(`LOOP_ALLOW_COMMITS=0`). G1 source 불변(열람만, lap890 기록 값과 일치):
  `tools/g1_saved_scene_probe.py` `5c33daf2…51aeb3336`, `tests/test_g1_saved_scene_probe.py` `73d7ef92…aa049aa`,
  `g1_mirror2x.c` `76e70af3…edc4a63`, `g1_census.c` `0d8c9143…291f1f`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 비합성 save006
  `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 재해시 MATCH(읽기만). 새 후보 없음. 분석한 raw는 모두 과거
  회차의 Xvfb/Wine·save006 한 장면이며 8 player records·572~573 units는 활성8인 부하 증거가 아니다.
- 실행 명령 / 로그 / 산출물 경로 및 해시: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap892_strategy_review/`.
  `python3 timeline.py` → `timeline.json`(스크립트 SHA `8f0e46d0…d5816e`, 결과 `658f6dc3…aa4141`),
  `python3 bracket.py` → `bracket.json`(스크립트 `8304b8d4…1de303`, 결과 `3d1d865c…2d1be0`). 입력 raw SHA는 두 JSON의
  `inputs_sha256`에 있다(lap890 pair `e441dc34…7a81d21`은 lap890·891 기록과 일치, lap888 결과
  `02b5e67762b4bb260fa800f121af7628c03d56687374c9eed524200ebc2fbb72`). 원본 정적 판독은 `i686-w64-mingw32-objdump`·`pefile`.
  입력 raw·원본·참고 저장소에 쓴 것 없음.
- 측정값 / 판정:
  1. (a) 성립. 완료 24860(lap888 3 lane 동일)과 완료 24862(lap874 r9·r10·r11 동일) 사이에 바뀌는 필드 33개에 대해 lap890
     baseline은 6개가 24860 값·27개가 24862 값, candidate는 10개·23개, 어느 쪽도 아닌 값 0. 유닛 생성/삭제·AI/group 차이 없음.
     그 밖에 양 lane이 똑같이 24860과 다른 유닛 필드 14개(7 유닛의 command 15·production_type)와, 양쪽 완료값과 다른 쌀 일시값
     3개(baseline owner2 300430·owner6 230207, candidate owner6 230607)가 있다.
  2. (b) 성립. `player.count == 그 owner의 살아 있는 유닛 수`는 완료-phase 22개 snapshot·8 owner 전부에서 성립하고, live 30개 중
     lap890 candidate tick24861의 owner2(count 95 / 유닛 96, 새 유닛 slot24)만 깨진다. **candidate snapshot은 찢어진 읽기로 확정.**
  3. 정적: `_wait_for_exact_tick`은 목표 tick을 본 직후 읽기를 시작하고, 원본은 tick store `0x41C8C9` 뒤에 player 처리를 한다.
     update 함수 `0x41C770`의 호출 지점은 `0x4245D2`·`0x4250F7` 두 곳이다.
  4. 판정: lap890 차이는 시뮬레이션 발산의 증거로 쓰지 않는다. 단 lap890 pair는 `HOLD` 그대로다(tick24861 완료 상태의 lane 간
     일치는 직접 재지 않았고 baseline lane 읽기의 phase도 미증명). lap891의 "lap890 일정 전용 GDB 진단"은 채택하지 않고, 표본을
     in-process update 반환 지점으로 옮기는 **P4b-S**를 다음 work로 정했다. B'/G1 HOLD, C/D/P5 전환 없음. 기준·validator·임계값 불변.
  5. PROMPT ③의 "실행 증거가 늘지 않는 회차 연속 최대 2회": lap891(middle)·lap892(이 판정)가 그 2회다. 다음 회차는 빌드·격리
     실행이 있는 work여야 하며, 이 판정이 그 목표(P4b)를 계속하기로 한 strategy 판정이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이 판정은 실행 미검증인 범위 결정이다. in-process 표본이 맞는지는 카드 §3
  E2(불변식)·E3(lap888 완료 상태와 대조)로 다음 work가 시험한다. 다른 스레드의 sim 쓰기 부재와 실행 간 결정성은 과거 관측에
  기댄 가정이다(카드 §6). 2단 middle 검수·3단 사용자 승인 아님. 검사 결과는 STATUS에 적는다(이 기록은 검사 전에 닫는다).
- 다음 한 가지: work가 `G1_STRATEGY_W70_P4B_S_INPROCESS_SNAPSHOT_LAP892.md` §2를 구현·빌드하고 fresh pair를 실행해 §3 E1~E4를
  잰다(구현→실행→수리 최대 3회, B' PASS는 연속 2 pair).
