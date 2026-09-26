# 2026-09-12 | lap 244 | 목표 G1 Stage B — R6-B-R10/R16/R17 middle 독립 재검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음. 검수 대상은 lap243 work 결과다.
- 가설 / 예상 PASS·FAIL 조건: lap243이 R16(탐색 불가 부모의 `PermissionError` 누출)과
  R17(조기 기존-증거 거부 삭제 변이 미검출)을 실제로 닫았다면, (a) 모든 사용 불가 출력 경로가
  raw traceback 없이 `exit 2`로 분류되고, (b) 어떤 거부에서도 probe **본문 라인이 0줄** 실행되며,
  (c) 수리를 제거하는 각 변이를 shipped 회귀가 실패로 검출해야 한다. 하나라도 어기면 FAIL.
- 변경 파일 / source fingerprint / 커밋: 신규
  `docs/history/laps/probes/20260912_lap244_r6b_r10_reverify_probe.py`
  `b57c21825f7e79a348340b82bcd1e62dac88e2f792f39c2f58b5a83cb44b2f40`,
  보고서 `...reverify_report.json`
  `635831909fbf17c2d0e938b24d5e748dd36778b30149f4b5a2b082f3b4cdec90`,
  attempt1 + `...reverify_report.PROVENANCE.md`, 본 기록, `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`.
  uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 환경 / fixture: 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  및 `tools/runtime_env.py` `bb10cd84ddcb521b704318aeccb60125cec0abd89436e16b0b25d1ed918d2dab`
  불변(검수 전후 해시 동일). 검수 대상
  `20260912_lap228_r6b_r3_review_probe.py` `16f74629…06d12`,
  `tests/test_review_probe_output.py` `c9671f6d…745eb`도 전후 불변.
  Python 3.13.5, euid 900(root 아님 — 권한 케이스가 의미를 갖는 조건). fixture는 임시 트리의
  missing/deep-missing/file-parent/symlink-parent/dangling-symlink/read-only(0o500)/
  non-searchable(0o600)/write-only(0o300) 부모, 기존 파일·디렉터리·심볼릭 evidence, 정상 경로이며
  실제 게임 상태/플레이어/지도/군대는 N/A. 게임/Wine/Xvfb/PNG 0.
- 실행 명령: `.venv/bin/python docs/history/laps/probes/20260912_lap244_r6b_r10_reverify_probe.py
  --output docs/history/laps/probes/20260912_lap244_r6b_r10_reverify_report.json`;
  `make check`; `LOOP_DRY_RUN=0 bash checks/safety.sh check`.
  lap242/lap243 probe·fixture·보고서는 재사용하지 않고 하네스를 새로 작성했다.
- 측정값 / 판정: **PASS**.
  - Q1 분류 14-case 전수 AGREES: 거부 9건 모두 `exit 2`+고유 분류 문자열+traceback 0+fixture
    바이트 보존+경로 존재 상태 불변, 정상 3건과 write-only(0o300) 부모 1건은 `exit 0`으로 신규
    보고서 생성. lap243이 다루지 않은 deep-missing, symlink 부모, dangling symlink, 출력 경로가
    디렉터리, 심볼릭 evidence, write-only 부모까지 포함했다.
  - Q2 조기성: lap243의 call-profiler와 **다른 계측**(SUT 파일 라인 트레이싱 + AST로 계산한
    본문 라인 집합)으로 측정. 거부 5종 모두 본문 라인 **0줄**, 최대 실행 라인 128(`__main__`
    가드 끝 130) ; 정상 대조군은 본문 205줄·최대 426줄로 트레이서 자체의 검출력을 증명했다.
  - Q3 변이 6종: M0 control 7 passed, M1(OSError fail-close 제거)→R16 테스트 실패,
    M2(조기 `exists()` 제거)→R17 테스트 포함 2건 실패, M3(`exit 2`→`3`)→6건 실패,
    M4(`os.access` 제거)→read-only 테스트 실패, M5(`is_dir` 제거)→2건 실패. 변이는 저장소 밖
    임시 미러 트리에만 적용했고 원본 파일은 불변.
  - Q4 보고서 의미: 서로 다른 fresh 경로 2회 실행이 바이트 동일, `source_sha256`가 현재
    `tools/runtime_env.py`와 일치, `game_executions=0`, surgicality 13,689-case AGREES,
    재실행은 `exit 2`로 거부하고 기존 파일 불변.
  - Fast: `make check` **268 passed**(Ruff/compileall/mypy 10 files/`CONTEXT_PASS`),
    `checks/safety.sh check` **SAFETY_PASS**.
- 회귀 / 남은 위험: 신규 **R19**(회귀 내구성 결함, 동작 결함 아님). `test_r6b_r17_…`의
  `{"reachability","surgicality","preservation","drive_wait"}` 중 앞 3개는 모듈 **변수**여서
  프로파일러 `co_name`으로 절대 나타나지 않는다. 즉 R17 보호는 함수명 `drive_wait` 하나에만
  걸려 있다. 실측: `drive_wait`를 개명한 미러에서 조기 `exists()` 거부를 제거해도
  `test_r6b_r17_…`는 **통과**했다(개명만 한 대조군은 7 passed). 현재 shipped 코드에서는 변이가
  검출되므로 R10 범위는 승인하되, 이름 비의존 증거(본문 라인 실행 0 또는 명시적 마커)로
  바꾸는 작업을 work tier 큐에 등록한다.
  본 검수 하네스 자체의 결함 2건(earliness workdir `mkdir` 누락, 기존-evidence 케이스의
  `output_created` 채점 오류)은 attempt1 + `PROVENANCE.md`에 보존했고 제품 코드/테스트/임계값은
  바꾸지 않았다.
- 독립 검수 / 승인 상태: **R6-B-R10 범위 승인**(lap244 middle, Opus5/high 독립 검수).
  사용자 마일스톤 승인 아님. S1/F2-R2, R6-B-R2, WM_CLOSE, G2~G4는 미해결이며 Stage B 실행은
  상위 재결 전까지 계속 금지다.
- 다음 한 가지: work tier(Luna/Sonnet5, high)가 게임 없이 **R11**(배타 생성 단독 가드 회귀)을
  구현한다. R19는 R15 뒤 큐에 둔다.
