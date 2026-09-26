# 2026-09-10 | lap2 | G1 우선 상위 계획

- 실제 provider/model / 지정 역할: Codex gpt-6-astra / strategy. 프로젝트 effort 계약=high;
  세션 설정의 독립 CLI 증명은 수집하지 않았고 다른 모델은 호출하지 않았다.
- 목표: G1~G4 범위·우선순위·검증 게이트와 middle/work 역할 인계를 문서화한다.
- 가설: 원본800×600 렌더링 보존 및 최종2배 출력/입력 대응이 G1에 적합할 수 있다.
  DESIGN의 허용과 QHD 반려에 근거한 조사 우선순위이지 출력 경로 실증이 아니다.
- 예상 PASS: 제품 범위 유지, 실행 입력·측정식·중단 조건·역할 분리 명시, Fast/보호 해시 일치.
  FAIL/승격: 필수 게이트 실패·근거 충돌·마일스톤 경계. M0→M1 경계로 승격, 마감 미실시.
- 변경: docs/MASTER_PLAN.md, docs/STATUS.md, 이 기록, loop/ESCALATE_SOL 및 local 증거.
  uncommitted / unborn HEAD. 게임 코드·바이너리·golden·원본 변경 없음.
- 원본/격리 EXE SHA256: b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac.
  새 후보SHA: 없음. 기존 격리 manifest: local/runtime/20260910_222434_2612938_0/manifest.json.
- 환경/활성 인원/지도/군대: 새 게임 실행 없음, 해당 없음. fixture: Fast의 합성/모의 시험;
  원본/격리 EXE 해시는 실제 파일 읽기. 과거 제목 화면은 새 전투 기준으로 승격하지 않음.
- 이전 바퀴 검수 범위: runtime_environment_source_hashes.json의8개 소스와
  runtime_environment_manifest.json의 원본/격리 EXE2개 해시 재계산 일치(PASS).
  별도 lap1 상세 보고서는 읽기 색인에서 발견되지 않아 이전 세팅 기록만 대조했다.
  과거 캡처의 시각적 독립 검수/게임 재실행은 SKIP. 전체 M0 재승인 주장 없음.
- 실행: `make check > local/strategy/20260910_lap2/make_check.log 2>&1`.
  77 passed in8.14s, Ruff/compileall/mypy8파일/context/Bash PASS, exit0.
  Python hashlib로 기록된 소스8개와 원본/격리 EXE2개를 재계산, 각 JSON에 expected/actual 보존.
- 탐색 진단: 루트 APPROVALS.md는 없어 docs/feedback/APPROVALS.md를 읽었다.
  Git HEAD 조회 실패는 문서화된 unborn 상태다. STOP/loop/STOP은 관측 시 없었다.
  STATUS 교체를 포함한 첫 apply_patch는 중복 경로 연산으로 적용 전 거부되어 파일 쓰기로 처리했다.
  이는 빌드/검증 실패나 게임 구현 재시도가 아니다. 필수 Fast 실패 없음.
- 신규 PNG/24k/144k/멀티 실행: SKIP. 제품/상위 계획 독립 승인: UNKNOWN/미결.
- runtime 제공 streak=1/implementation-unchanged-streak=1; 이번 바퀴 구현 진척0.
  반복 서술을 구현 성과로 세지 않는다. 이후 실무의 측정 가능한 산출물은 MASTER_PLAN의
  기준 캡처/입력 효과/출력 경계 근거표다. 해상도 주소 추측으로 무변경을 해소하지 않는다.
- 다음 한 가지의 권위: docs/STATUS.md 참조. loop/ESCALATE_SOL로 Sol 검수에 이관했다.
  사용자 마일스톤 승인 및 계획 컨펌은 대기이며 이번 세션에서 통과로 바꾸지 않았다.

## 보존한 파일 해시

이 기록 자체의 해시는 local/strategy/20260910_lap2/final_hashes.json에 저장한다.

| 파일 | SHA256 |
|---|---|
| `docs/MASTER_PLAN.md` | `5dc83a3d8b86b92ad0a1c1020bc8870bb256be7c45468c86d8baf4e1721e5c4f` |
| `docs/STATUS.md` | `d20cecb1c59ca8baa290143a30eeecf4432fcdf3c7caa17db1d54e2dd14e28e9` |
| `loop/ESCALATE_SOL` | `6a17dd281c722c785c4d1170bbb508159f4d4fc5e1abe2cf10e12e0ff77a32ce` |
| `local/strategy/20260910_lap2/STATUS_before.md` | `eafd937e40203055b86b07bb214a04425e305a4ba465aa267c0d36ae59c6fa50` |
| `local/strategy/20260910_lap2/make_check.log` | `e053f053339dcb1e177ace9781bdab384959191d92bcf9154774a890454e8ccb` |
| `local/strategy/20260910_lap2/previous_source_audit.json` | `57f0f6f6cb1c9a27656b6a3a02033b630dd6ff325248f87f1845de9ee5760fb2` |
| `local/strategy/20260910_lap2/original_hash_audit.json` | `96cbca8c1f5f6ab9a27d18fbcde8e081c4f7c0a62636e49c54d6c08e1b044b79` |

문서 작성 후 `.venv/bin/python checks/context_limits.py`: CONTEXT_PASS.

## 승격 복구·마감 — 2026-09-10 23:15 KST

- 실제 provider/model/effort / 지정 역할: Codex `gpt-6-astra` / high / strategy.
  게임 구현은 수행하지 않았고 middle/work 역할을 대신하지 않았다.
- 목표/가설: M0는 이미 Sol/high 기술 APPROVE였으므로 M0→M1 승인 대기가 아니라,
  G1의 첫 관측 카드를 상위 범위로 확정하면 same-lap 중단을 안전하게 마감할 수 있다.
- 예상 PASS/FAIL: G1-A의 입력·산출물·고정 측정식·중단 조건·역할 인계가 결정 가능하고
  Fast/보호 해시가 일치하면 PASS. 범위 충돌·원본SHA 불일치·필수 Fast 실패면 FAIL.
- 변경 파일: `docs/MASTER_PLAN.md`, `docs/STATUS.md`, 이 lap 기록 및 local Fast 로그/해시 manifest.
  uncommitted / unborn HEAD. 게임 코드·EXE/DLL·게임 데이터·baseline/golden 변경 없음.
- 원본/후보SHA: 원본과 격리 EXE 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`;
  후보 없음. 환경/활성 플레이어/지도/군대: 게임 미실행으로 해당 없음.
- 이전 바퀴 독립 검수: 소스8개를 `sha256sum`으로 재계산해
  `previous_source_audit.json`과 전부 일치, 원본/격리 EXE2개도 manifest와 일치(PASS).
  기존 MASTER_PLAN/STATUS/lap 기록 해시는 `final_hashes.json`의 당시 값과 일치(PASS).
  M0 Sol/high APPROVE는 `docs/history/20260910_RUNTIME_ENV_SETUP.md`에서 확인했다.
- 상위 결정: 유일 활성 목표 G1, 첫 Luna 카드는 **G1-A 무패치 기준 장면·입력 효과·출력 경계 조사**.
  최소1600×1200 전용 display, 메뉴+전투, 입력5종, surface/module/좌표 chain을 필수화했다.
  관측 전 해상도/DLL/입력 패치를 금지하고 60~90분 또는 실패 가설2회 중단을 고정했다.
- G1-B 사전 합격식: content1600×1200, 양축2배, 정적 기준점 축별±1px,
  잘림·왜곡·누락0, 동일 camera/tile 범위, `floor(candidate/2)` 입력 효과 일치.
  동적 mask/scaler/오차는 Sol이 실행 전에 고정하고 사후 완화하지 않는다.
- 실행/수치: `make check 2>&1 | tee local/strategy/20260910_lap2/make_check_escalated.log`;
  pytest **77 PASS**, Ruff PASS, compileall PASS, mypy8파일 PASS, context PASS.
- fixture/PASS·FAIL·SKIP: Fast의 합성/모의 fixture만 사용. 상위 계획 복구 PASS.
  새 게임 실행·PNG·G1 실제 출력/입력·24k/144k·멀티·제품 마일스톤은 SKIP/미검증.
  프로세스 exit0만이 아니라 검사 항목과 보호 해시를 판정 근거로 사용했다.
- `loop/ESCALATE_SOL`은 승격 진입 시 이미 없었고 다시 만들지 않았다. 최초 기록의 marker/hash는
  승격 전 역사값이며 현재 파일 상태가 아니다. 구현 무변경 streak는2가 되었지만 이번 역할은
  구현자가 아니므로 서술 반복 대신 다음 측정 가능 산출물을 G1-A 증거5종으로 좁혔다.
- 다음 한 가지: `docs/STATUS.md`의 권위대로 새 Sol/high가 G1-A 명령·새 run/증거 경로·fixture·
  입력 기대값·실패 정리를 단일 실행 카드로 만들고 사전 컨펌하여 Luna/high에 인계한다.
  Sol 기술 컨펌과 사용자 마일스톤 승인은 별개다.
