# 2026-09-12 | lap 356 | G1 / lap355 S1 reader wiring middle review

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션 / 정확한 모델 ID 미주장 / high / middle(진단·계획·확인). 게임 코드 hands-on 수정 0.
- 번호: runtime 메시지 `lap=355`, `loop/.lap_counter=356`; PROMPT 계약대로 356 사용, counter 쓰기 0.
- 목표 / 가설: lap355가 lap354 F1~F4를 실제 production direct-reader 결선과 fail-closed provenance로 수리했는지 독립 판정한다. PASS는 reader/group/PS 결선, 외부 JSON 거부, pre/post 변화와 8×6 fixture 일치 강제가 모두 재현되는 경우다.
- 변경 파일 / source fingerprint / 커밋: `docs/work/active/G1_S1_READER_WIRING_MIDDLE_REVIEW_LAP356.md`, 이 기록, `docs/STATUS.md`, STATUS 원문 압축본. 제품 코드/tests/EXE/DLL/save/pin/baseline/golden 변경 0; 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 1,032,192 B / `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보·게임 실행 없음; Linux/Python 합성 검수; 활성 플레이어·지도·군대 N/A. save000 3,093,902 B / `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`.
- 이전 바퀴 검수: lap355의 세 SHA가 현행과 일치(`runtime_env.py=77aaf0de…a38b`, `s1_load_evidence.py=157778e6…0924`, test=`91bc9059…c30e`). 소스에서 private PID ownership 검사, `runtime_driver.read`, WORD 3곳·PlayerStruct 8×6 direct pre/post 결선을 독립 재유도했다.
- 실행 명령 / 수치: `make doctor` rc0/original verified; 대상 `15 passed`; lap354 probe `b08d0c7b…07a4` fresh rc0/`failures=[]`; `make check` rc0, 393 passed in 63.86s와 Ruff/compileall/mypy/`CONTEXT_PASS`; safety `SAFETY_PASS`. Wine/Xvfb/클릭/PNG/실제 load 0회.
- 측정값 / 판정: 기계/정적 **PASS**, 실제 runtime/load **SKIP(0회)**, 제품 **UNKNOWN**. **ACCEPT — lap354 F1~F4 repair scope only.** 외부 복사 payload는 `UNKNOWN/UNTRUSTED_READER_EVIDENCE`; direct 합성 pre PS35→post PS3·8개 fixture 일치만 `LOAD_RESTORED_PLAYER_STRUCTS`. exit0/Fast는 제품 승인 아님.
- 회귀 / 남은 위험 / 승인: N15 발견 — production `--pid`는 load trigger/wait 없이 pre/post를 즉시 연속 읽어 실제 load 인과 경계를 만들지 못한다. 실제 load/open·두 run 결정성·S1 (A)+(B)·F2-R2·WM_CLOSE·Stage B·G1~G4와 사용자 승인은 UNKNOWN.
- 다음 한 가지: Luna/high work가 실행 0회로 `pre→trigger exact-once→bounded PS3 wait→post` event-boundary adapter와 순서/timeout 회귀를 추가하고 다음 새 middle에 넘긴다. 실제 run 봉투는 lap349 Astra 권한을 유지한다.
