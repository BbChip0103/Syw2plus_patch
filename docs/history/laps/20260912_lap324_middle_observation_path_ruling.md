# 2026-09-12 | lap324 | G1/M1 — lap323 실행 경로 양립성 판정

- 실제 provider/model/effort / 지정 역할: Claude Code claude-opus-5 / high / 중간계획·컨펌(middle).
  게임 구현 0, 게임 실행 0, hands-on 게임 코드 수정 0.
- 번호: 읽기 전용 `loop/.lap_counter`=324. counter 변경/복원 0.
- 가설 / 사용자 관찰: §14.7 "입력 0 + exact-site 계측 + 하네스 수정 금지" 봉투가 현재 하네스·원본
  증거와 양립하는가. lap323 Astra가 반려하며 middle에 여섯 행 판정을 인계했다.
- 예상 PASS / FAIL 조건: 시작·도달·계측·예산·판정식·work 경계의 근거가 금지와 양립하면
  ACCEPT-WITH-REVISION, 누락/충돌이면 BLOCKED + 필요한 권한·구체 blocker 반환.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 **uncommitted**, 커밋/푸시 0.
  - `docs/work/active/G1_MIDDLE_OBSERVATION_PATH_LAP324.md` (신규 판정 문서)
  - `docs/history/laps/probes/20260912_lap324_middle_observation_path_probe.py` `0ed6692b0f1aae911d3cb043286fafff7566308fa69668dff069fa716b2fa7d2`
  - `docs/history/laps/20260912_status_lap323_compaction.md` `2dfce3c8…e9e0e73b9d` (직전 STATUS 130줄, 원문 SHA `7f5cc20b…1e1354c88759`)
  - `docs/STATUS.md`, 본 기록, `loop/ESCALATE_SOL`, `logs/lap324/`
  - **무변경 장부:** `tools tests checks patches docs/baseline`의 90개 파일 SHA가 pre/post 동일
    (`logs/lap324/hash_ledger_pre.txt` = `post` diff 없음, ledger SHA `1837f343…9c2a489b`).
    lap323 정정대로 "테스트 수 불변"을 무변경 증거로 쓰지 않는다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `syw2plus_original.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 후보 없음.
  Wine/Xvfb/Stage B/클릭/PNG **0**. 활성 인원·지도·군대 N/A(정적 읽기 전용).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 docs/history/laps/probes/20260912_lap324_middle_observation_path_probe.py` ×2 →
  `logs/lap324/probe_run1.json` = `run2.json` **byte-identical**, SHA `c00eed094885334ecc2fb072defb543ac43e4cd2e32105919518859fbb1e21cf`, rc0, `failures=[]`.
  `bash checks/safety.sh check` → **SAFETY_PASS** rc0. `make check` → rc0, **361 passed**, Ruff/compileall 통과,
  mypy 10 files 무이슈, **CONTEXT_PASS**. 로그는 `logs/lap324/`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **제출 봉투 BLOCKED**, 개정안 R1 상위 반환.
  1. **계측 기구 부재(신규, 결정적):** 읽기는 `process_vm_readv` 폴링뿐이고
     `process_vm_writev`/`ptrace`/`PTRACE`/`int3`/`0xCC`/`winedbg`/`gdb` **전부 0회**.
     exact-site를 증명할 수단이 없으며 만드는 것 자체가 "하네스 수정 금지" 위반이다 → 제출 형태 자기모순.
  2. **개정 R1 성립(신규 핵심 증거):** 0x4D6312의 결과는 휘발되지 않고 영속 전역에 저장된다.
     `.text`(0x401000–0x4E4AE5) 절대 operand 전수 스캔 — `ds:0x1088B5C` 출현 10, **직접 store 1**(`0x4D632A`
     `66890d5c8b0801`), 읽기 9(전부 `movsx`), 미분류 0; `ds:0x1088B5E` 출현 11, **직접 store 1**(`0x4D6348`
     `66893d5e8b0801`), 읽기 10, 미분류 0. 직접 writer가 각각 하나이므로 **폴링으로 A/B를 가릴 수 있다**.
     잔여 fail-open: 계산/간접 writer는 배제 불가(N2 계열) — 결론을 "직접 writer 범위 유일"로만 쓴다.
  3. **도달 BLOCKED:** 하네스 대기 가능 상태는 형태 무관 AST로 `ps ∈ {3,4,5,6,7,9}`뿐, `35` 리터럴 0,
     `save` 토큰 0, `0x1088B5C/5E` 참조 0. PS9(타이틀)는 입력 0으로 도달하나 다이얼로그가 아니다.
     `FUN_004D60B0` 직접 caller는 `0x4D69E5`,`0x4D6A05` 2개뿐이고 입력 없이 도는 근거 0 →
     구성은 **최소 1클릭**(`(296,505)`, 결과 미관측)을 요구한다. "입력 0 도달"은 증거와 **충돌**.
  4. **"한 줄만 변경" 반증:** 최소 3건(runtime 예산·하네스 수정·입력 1클릭)이 필요하다.
     Stage B·쌍·PNG 비교·W3 재pin·baseline/golden·원본 실행 이미지 변경(INT3)은 **유지(금지)**.
  5. 예산·보존 ACCEPT-WITH-CONDITION(90초 안 배분은 전부 **가정**, 첫 run이 실측해 재평가; 실패 4모드 선언),
     판정식은 관측 대상 교체로 재작성(pre/post 원시값, 그 외 값→두 후보 폐기, 미변화/수집 실패→UNKNOWN).
  6. 독립 재유도 부수 확인: 화면 전역 직접 store 4건 `{0x431B79,0x431B7F,0x4324B8,0x4324C2}` 재유도 일치
     (과거 결과의 재현이며 게임 검증으로 승격하지 않는다).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 0(보호 트리 해시 불변). 위험은 R1이
  **클릭 1회를 요구**한다는 점이며 이는 상위/사용자 권한이다. 본 판정은 **middle 기술 판정**이고
  사용자 마일스톤 승인도 제품 증거도 아니다. G1~G4 미완료, S1 종결 REJECT 등 기존 미결 전부 유지.
- 다음 한 가지: 상위(Astra/사용자)가 R1의 금지 변경 3건을 허가/거부한다. 허가 시 work(Luna/Sonnet5)가
  연구 전용 관측 경로를 구현하고, 이어서 **새 middle**이 독립 검수한다. 거부 시 §5(c)/A·B는 UNKNOWN 유지이며
  실행 예산 0으로 가능한 유일한 독립 진행분은 §14.1 fixture 모델 반증뿐이다(이번 바퀴에 열지 않았다).

## 수신 lap323 ESCALATE_SOL 원문 보존 (부록 A — 소비)

SHA256: a1026fce584b3d6ddecbe66778b0c67c5994ef104176375a80b96e0856217008

```text
lap=323
role=Codex gpt-6-astra/high major direction/master-plan
reason=§14.7 실행 경로 미제출/금지 조건 충돌; STATUS 초안 길이 필수 검사 FAIL(131>130, AssertionError, rc1).
handoff=docs/work/active/G1_OBSERVATION_DIRECTION_LAP323.md
record=docs/history/laps/20260912_lap323_astra_observation_boundary.md
next=새 middle이 새 격리 시작·입력 없는 0x4D6312 도달·exact-site 계측 근거와 금지별 변경 필요를 판정. 문서 제한 및 make check 검증을 이어 수행한다.
constraints=실행 봉투 REJECT; runtime/게임/Wine/Xvfb/Stage B/클릭 0; work 카드 0; N4/W3 보류. 재시도/강제 마감 없음.
approval=상위 반려 기록이며 middle 수용·제품 완료 아님. process exit0은 검증 통과 아님.
```

## 부록 B — 최종 산출물 해시 (lap323 정정에 따른 장부)

- `docs/STATUS.md` (130줄) `5b1191304f2978c946ff1fff7e33b55c62d98e7fe972a51a1c6d947a87296795`
- `loop/ESCALATE_SOL` `52f522a24e74ea8b5eac27ae542bbb4785a60e9bf7ba78fc272fd3ef3ddddea2`
- 보호 트리 90파일 해시 장부: `logs/lap324/hash_ledger_pre.txt` = `…_post.txt` (diff 없음),
  STATUS 갱신 후 재실행한 `make check` rc0 **361 passed** / CONTEXT_PASS / SAFETY_PASS
  (`logs/lap324/make_check_final.stdout`). 전부 uncommitted, 커밋/푸시 0.
