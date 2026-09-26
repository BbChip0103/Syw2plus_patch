# 2026-09-12 | lap362 | G1 S1 원본 단일-load 결선 봉투 검수

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션, 정확한 모델 ID 미노출·미주장 / 사용자 지정 high / middle 진단·계획·확인. 저장소의 현재 middle 선택 Opus5-only와 차이를 공개했고 외부 모델 호출 0.
- 목표/가설: lap361의 trigger·전체 deadline·pre-slot 세 blocker를 독립 검수. pre slot1이 PS35 정상 진입에서 먼저 초기화되면 exact-once load trigger work 봉투를 만들 수 있고, 필수 검증 실패 시 미발효 STOP한다.
- 예상 PASS/FAIL: 원본 주소/old bytes와 현행 호출부가 세 조건을 비순환으로 닫고 targeted/lap354/Fast/safety가 fresh PASS하면 범위 ACCEPT. import/필수 gate 실패나 근거 충돌이면 현재 문서 보존 후 승격.
- 변경 파일: `docs/work/active/G1_S1_MIDDLE_EXECUTION_ENVELOPE_LAP362.md`, `docs/STATUS.md`, `loop/ESCALATE_SOL`, 이 기록. 게임 코드·하네스·tests·EXE/DLL/save/pin/baseline/golden 변경 0; uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본/후보 SHA: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음. 현행 `runtime_env.py=ba0a7beb657ce6c7a174d9323c4254f2d696b74277a974e15a5216d272b7372c`, `s1_load_evidence.py=fffc644495b442627a8166125365caa6270999ff06bead52d2b1e1a8ad90fa65`, test=`7508e5c1fe3b6110336d3b1457381f4d208d632f361ff8c842309b18ad6cb8c7`.
- 환경/fixture: 보호 private copy `local/runtime/20260912_191422_3558862_0`; save000 3,093,902 bytes / `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`. 실제 활성 플레이어/지도/군대=N/A, 게임/Wine/Xvfb/입력/PNG 실행 0.
- 실행 명령/근거: PROMPT→AGENTS/INBOX/APPROVALS→STATUS/DESIGN/MODEL_ROUTING→lap361/349/350/351/352/354/356; `sha256sum`; 보호 원본 `objdump -D -Mintel` 주소창 `0x4248E0`, `0x493C40`, `0x4D5CA0`, `0x4D5F10`, `0x4D5F80`, `0x4D6740`, `0x4D6930`, `0x4D6A00..0x4D6BA9`; 현행 source/helper read.
- 수치/정적 판정: `0x4D5CA0` old bytes `66c7819e0f00000100c3`이 selected WORD를 1로 초기화한 뒤 PS35가 기록됨. rect1 `[260,119,540,143]`, 후보점 `(400,131)` strict interior, unscaled root=`crop+(400,131)`. trigger 결선 MISSING, 현행 deadline은 trigger 뒤 PS3 wait만 포함. §3은 total150s=`60+40+20+2+5+10+3+10`, actual run 0.
- 검사: `python3 -m pytest -q tests/test_s1_load_evidence.py` rc0, **21 passed**. 다음 `python3 docs/history/laps/probes/20260912_lap354_middle_lap353_s1_reader_review_probe.py`는 rc1 ImportError; import 대상이 형제 `Syw2plus_re/tools/__init__.py`. `PYTHONPATH=<unset>`. 사용자 중단 규칙에 따라 다른 argv 재시도·`make check`·safety는 SKIP.
- 판정: 기술 work 범위는 ACCEPT 초안이나 필수 독립 probe의 예상 밖 환경 실패 때문에 **STOP / 미발효 / ESCALATE_SOL**. exit0인 targeted는 이를 상쇄하지 않는다.
- 회귀/남은 위험: 실제 pre slot1, input delivery, open/load, PS3, 8×6 변화, cleanup, 두 run 결정성, S1 (A)+(B), Stage B, WM_CLOSE, 제품 G1~G4 모두 UNKNOWN. implementation-unchanged-streak가 2가 되므로 blind 정적 반복 대신 import provenance 해결→work의 measurable orchestration change만 다음 후보로 둔다.
- 다음 한 가지: 새 middle/Sol이 lap360 canonical probe argv/environment와 현재 import shadowing을 대조해 repo-root provenance를 고정하고, 역사 probe 수정 없이 fresh 1회 rc0/`failures=[]`를 확인한 뒤 §3 work 봉투를 발효/반려한다.

## 종료 시 문서 보존 해시

- `docs/work/active/G1_S1_MIDDLE_EXECUTION_ENVELOPE_LAP362.md`: `fdd552536329ddbde2ff4a2fd775f91ed8f7a4fb50b30941a0ed4d803eec4a51`
- `docs/STATUS.md`: `34f504f3e947dd21d6b4e2e815f919d7632f1a99fa28f0ce7910f149913e219c` / 126줄 / Blockers 표제 1개
- `loop/ESCALATE_SOL`: `c7967e2815d3f0e5182ec0fcef791154f527560a588b832c1f0f21f97ffa029f`
