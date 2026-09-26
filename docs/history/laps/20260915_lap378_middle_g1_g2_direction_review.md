# 2026-09-15 | lap 378 | 목표 G1 우선·G2 독립 조사 방향 검수

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션, 정확한 모델 ID 미노출·미주장 / 사용자 지정 high / middle 진단·계획·확인. 외부 provider 호출 0, 게임 코드·하네스·tests hands-on 수정 0.
- 가설 / 사용자 관찰: lap377 상위 방향이 G1 제품 증거로 가는 선행조건을 축소하고 G2를 공유 파일 없는 독립 조사로 분리했다면 work 범위를 승인할 수 있다. 구현 미변경 연속2회 뒤에는 또 재계획하지 않고 측정 가능한 artifact/work로 넘어가야 한다.
- 예상 PASS / FAIL 조건: DESIGN/INBOX/APPROVALS와 순서가 일치하고, lap376 source/log SHA 및 보호 원본/fixture pin이 맞으며, G1 provenance→독립 middle→Astra n=1 발효와 G2 단일 파일 조사 경계가 구체적이고 fresh doctor/Fast/safety가 통과하면 ACCEPT. 근거 충돌·필수 게이트 실패면 보존 후 승격.
- 변경 파일 / source fingerprint / 커밋: `docs/work/active/G1_G2_MIDDLE_HANDOFF_LAP378.md`, 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL`, `20260915_lap378_middle_artifact_hashes.json`만 문서 갱신. 현행 source/test SHA `2d4e478f...790e`/`44e8c1a7...4861`/`69e71404...755d` 불변; uncommitted, 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: private 보호 EXE 1,032,192 B / `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save000 3,093,902 B / `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`를 fresh 해시. 후보·활성 인원·지도·군대 N/A; game/Wine/Xvfb/input/PNG/fixture 생성 0회.
- 이전 바퀴 검수: lap377 방향/기록/snapshot manifest와 현행 SHA를 대조했다. 세 source/test SHA와 lap373 raw log `3ee03b31...d7fb0c`는 4/4 일치하고 로그에 lap372 endpoint SHA와 편집 원문/patch 출력이 존재한다. lap376 복원 가능성은 지지하지만 materialized artifact와 lap373 구현 ACCEPT는 여전히 UNKNOWN이다.
- 실행 명령 / 로그 / 캡처: PROMPT 첫 열람 후 AGENTS→INBOX→APPROVALS→STATUS→DESIGN §1~4→MODEL_ROUTING→patch-validation→lap376/377 및 lap361/362/363/366·G2 입력 문서 대조; `sha256sum`/`stat`/`rg`; `make doctor`; `make check`; safety 두 명령. 새 로그·캡처 없음.
- 측정값 / 판정: `make doctor` top `ok=true`, original verified, runtime manifest absent/side_effects=false; 문서 반영 뒤 최종 `make check` **430 passed in 81.48s**, Ruff/compileall/mypy/`CONTEXT_PASS`; safety 2/2 `SAFETY_PASS`. **lap377 방향 ACCEPT / G1 provenance work RELEASE / G2 read-only work RELEASE / 실제 실행 미발효.**
- 패치 안전 / 남은 위험 / 승인: 바이너리 patch 변경이 없어 old/new bytes·version rejection·copy-only·non-overlap·restore는 N/A/SKIP. 과거 캡처를 fresh 증거로 승격하지 않았다. S1/F2-R2 결정성, original/candidate pair, WM_CLOSE, G1~G4 제품 및 사용자 승인은 UNKNOWN.
- 다음 한 가지: Luna/high work가 `G1_G2_MIDDLE_HANDOFF_LAP378.md` §3의 lap372 exact pre-image·manifest·endpoint diff를 물질화하고 fresh 게이트를 제출한다. G2 §4는 RELEASED지만 현재 STATUS 큐가 아니며 별도 회차에만 수행한다.
