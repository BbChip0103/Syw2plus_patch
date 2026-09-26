# 2026-09-12 | lap 242 | 목표 G1 Stage B — R6-B-R10 middle tier 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code / claude-opus-5 / high / middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음. 검수 하네스만 작성했다.
- 가설 / 사용자 관찰: lap241은 review probe의 `--output` 부모가 없거나 디렉터리가 아니거나
  쓰기 불가하면 probe 본문 전에 `exit 2`로 분류하고 raw traceback을 남기지 않는다고 주장했다.
  이 검수는 (a) 분류가 모든 사용 불가 출력 형태를 닫는지, (b) guard가 본문보다 정말 먼저
  실행되는지, (c) R6-B-R7 보호와 보고서 의미가 보존되는지, (d) 출하 회귀가 guard 절 제거를
  실제로 검출하는지를 독립적으로 재도출했다.
- 예상 PASS / FAIL 조건: 사용 불가 출력 전 형태가 `exit 2`+분류 메시지+traceback 부재로 닫히고,
  정상 경로가 `exit 0`과 기존과 동일한 측정값을 내고, guard 절 변이가 모두 검출되면 PASS.
  raw traceback·미분류 exit·측정값 변화·미검출 변이가 하나라도 있으면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/history/laps/probes/20260912_lap242_r6b_r10_review_probe.py`
  `85cc09e4fc25618767d39d16329462eae9b4984b63b6e7a95b081e67a2b72f0e`,
  `docs/history/laps/probes/20260912_lap242_r6b_r10_review_report.json`
  `38efce5cd496ccf8445f370990440bd05352bcd87c53f8bb0671d58ce83939f0`,
  `…_review_report.attempt1.json`
  `174b7a703bb8ececbfbe6aa84c3e96d2a87840e773cf03630c2858708981e373`,
  `…_review_report.attempt2.json`
  `9800aaaad1d3f2cb8bc2a3647d8579edba222ee7995206d24fc5b4784bd3845c`,
  `…_review_report.PROVENANCE.md`, 본 기록, `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`.
  uncommitted; `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 후보 없음,
  활성 플레이어·지도·군대 N/A. 검수 대상 `20260912_lap228_r6b_r3_review_probe.py`
  `4b3a41f4e9f8c2a28153d02c6eab0d7da7c6088b9b9e1e170be5006f1fb23021`,
  `tests/test_review_probe_output.py`
  `4351cc576ef3857296eb60eab518d60f7d5247575e33a4539aa7d3d9e7f953ee`. 보호 소스
  `tools/runtime_env.py` `bb10cd84ddcb521b704318aeccb60125cec0abd89436e16b0b25d1ed918d2dab`,
  `tests/test_runtime_env.py` `a2454b94c366b0dae9549d6369f520aabdc849ecb3e3cba98671bc6a0cedc372`
  는 읽기만 했고 검수 후 해시 동일. 저장된 lap228 보고서
  `739921763ca47cbc881dcb688cc909688ffddcb5c52f0e7620da4071921c6883`도 실행 전후 동일하다.
  fixture는 `tempfile.TemporaryDirectory`의 출력 부모 11종·정상 경로 3종과 변이 mirror
  트리이며 실제 게임 프로세스 메모리는 읽지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap242_r6b_r10_review_probe.py`
  → `verdict=FAIL`, 보고서 위 경로. `make check` → `266 passed`, Ruff/compileall/
  mypy 10 files, `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
  게임/Wine/Xvfb 실행 0회, PNG 0, 패치 생성/원복 N/A.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): R6-B-R10 **범위 승인 보류(FAIL)**.
  - 분류 11-case 중 10건 PASS: missing/deep-missing/regular-file/symlink-to-file/dangling-symlink
    부모는 `not a directory`, read-only 부모는 `not writable`, 기존 파일/디렉터리/기존 대상
    symlink/dangling symlink 출력은 `refusing to overwrite existing evidence`로 모두 `exit 2`,
    stderr traceback 0, fixture 보존 11/11.
  - **C07 DEFECT (신규 R6-B-R16)**: 출력 부모가 `0o600`(쓰기 가능·탐색 불가)이면
    `output_refusal`의 첫 절 `path.exists()`가 `PermissionError`를 그대로 올려 raw traceback과
    `exit 1`로 끝난다. R6-B-R10이 닫겠다고 선언한 실패 계열이 guard 자신에게 남아 있다.
    재현: `chmod 600 <dir>` 후 `--output <dir>/report.json`.
  - 정상 경로 3/3 PASS: 새 경로·symlink된 디렉터리 부모·상대 경로 모두 `exit 0`, 보고서 생성.
  - 조기 실행 근거 2종 PASS: AST 문장 순서(guard 120행 < 본문 첫 문장 134행)와 프로파일 훅
    추적(`output_refusal` 실행, 본문 함수 `observe/observe_raw/make_reader/legacy_predicate`
    0회 실행, exit 2). 벽시계 비율 0.748은 인터프리터 기동이 지배해 판별력이 없어 판정 입력에서
    제외하고 관측값으로만 남겼다.
  - 보고서 의미 PASS: 신규 보고서와 저장된 lap228 보고서는 `source_sha256` 한 키만 다르고
    (lap241이 probe 소스를 바꿨으니 당연) 측정 전 구간이 동일하다.
  - **변이 4/5 검출, M3 미검출 (신규 R6-B-R17)**: 무변이 control은 `5 passed`, M1 `2 failed`,
    M2 `1 failed`, M4 `4 failed`, M5 `4 failed`로 검출된다. 그러나 조기 `path.exists()` 절을
    통째로 삭제한 M3은 출하 회귀가 그대로 `5 passed`다. 늦은 `open("x")` FileExistsError
    대체 경로가 같은 메시지와 exit 2를 내므로 **조기** 기존-증거 거부가 테스트로 고정돼 있지
    않고, 삭제 시 O(1) 거부가 전체 예산 소모 후 거부로 조용히 퇴행한다.
  - **신규 R6-B-R18 (비차단 provenance)**: lap241 기록의 `tools/runtime_env.py` 지문이
    `bb10cd84…e16e3cba98671bc6a0cedc372`(72자)로 손상돼 있다. `loop/ESCALATE_SOL`의
    64자 값이 실제 파일과 일치하므로 기록 쪽 오타다.
  - 제품 G1/Stage B는 **SKIP**. 게임 실행 0회.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 첫 두 실행은 검수 하네스 결함으로 FAIL했고
  attempt1/attempt2 원문과 `…PROVENANCE.md`에 보존했다. attempt1은 (i) 벽시계 임계값이
  판별력 없음, (ii) `source_sha256` 차이를 측정 변화로 오판한 문제였다. attempt2는 변이 사본을
  평평한 임시 경로에 둬서 probe의 `parents[4]`가 IndexError로 죽는 바람에 5/5가 "검출"로
  보였다 — 잘못된 이유의 검출이었다. 최종 실행은 depth를 재현한 mirror 트리와 무변이 control로
  이를 고쳤다. 제품 코드·임계값·기존 증거는 어느 보정에서도 바꾸지 않았다. middle tier는
  R6-B-R16/R17을 직접 수리하지 않고 work tier로 넘긴다. 사용자 마일스톤 승인 없음.
  S1/F2-R2, R6-B-R2, R6-B-R11~R15, WM_CLOSE, G2~G4는 미해결이다.
- 다음 한 가지: work tier(Luna/Sonnet5 high)가 게임 없이 **R6-B-R16**을 수리한다. `output_refusal`
  전체를 fail-close로 감싸 `path.exists()`/`is_dir()`/`os.access`의 `OSError`를 분류 메시지와
  `exit 2`로 닫고, **R6-B-R17**로 조기 기존-증거 거부를 늦은 대체 경로와 구분해 고정하는 회귀를
  추가한다. 그 뒤 middle 재검수 → R11 → R12 → R13 → R14 → R15 → F2-R1 → F3-R1 → F3-R2 → F6-R2.
