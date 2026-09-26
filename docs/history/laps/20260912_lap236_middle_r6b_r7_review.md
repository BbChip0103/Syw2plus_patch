# 2026-09-12 | lap 236 | 목표 G1 Stage B — R6-B-R7 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음. 제품/도구 코드 변경 0.
  lap 번호는 `loop/.lap_counter`=236을 따랐다. 러너 배너는 `lap=235`로 한 칸 뒤였고
  카운터 파일은 읽기만 했다(PROMPT.md ①/⑤ 규칙).
- 가설 / 사용자 관찰: lap235 work tier가 R6-B-R7(리뷰 probe 보고서 덮어쓰기)을 `--output`,
  사전 존재 거부, `Path.open("x")` 배타 생성으로 수리했다고 보고했다. 이 검수는 (a) 보고된
  파일·해시·게이트가 실제인지, (b) 보존 보장이 우회 경로(심볼릭 링크, 디렉터리, 기본 경로,
  import 실행)에서도 유지되는지, (c) lap235 회귀 테스트가 비공허한지를 게임 없이 확인한다.
- 예상 PASS / FAIL 조건: PASS = 모든 기존 경로가 exit 2로 거부되고 바이트가 보존되며,
  새 경로에만 보고서가 생성되고, R6-B-R3 리뷰 판정이 완화되지 않고, 회귀 테스트가 가드 제거
  변이에서 실제로 실패한다. FAIL = 어떤 우회 경로로든 기존 증거가 덮어써지거나, 보고서 판정이
  바뀌거나, 변이에서도 테스트가 통과한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap236_r6b_r7_review_probe.py`
  `700120855f8fb1e26d48412676627f685a523703d25f13df3bba5edbea1de48e`,
  `docs/history/laps/probes/20260912_lap236_r6b_r7_review_report.json`
  `76947d9dddea7152effedc690e5529e92b509071be16f8215ee8a7e23dd1286f`,
  `docs/history/laps/probes/20260912_lap236_r6b_r7_mutation_probe.py`
  `f9094d4dd38feb9375732859dead8eb6da9d401f3d49465c0b33277cc2f49874`,
  `docs/history/laps/probes/20260912_lap236_r6b_r7_mutation_report.json`
  `9d857289abc8995617979dfe4e9368639511c0e7437e6dfa4d385187efe94a47`.
  문서 갱신: `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  `loop/ESCALATE_SOL`, 이 기록. uncommitted; `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`가
  `tools/check_setup.py`, `tools/check_binary_contract.py`, `tools/runtime_env.py`,
  `patches/population/verification_0910/manifest.json` 4곳에서 불변. 후보 없음, 게임 실행 0회,
  PNG 0장, 활성 플레이어/지도/군대 N/A. fixture는 tmpdir sentinel 파일·심볼릭 링크·디렉터리와
  probe 내부 합성 reader이며 실제 프로세스 메모리는 읽지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. 보고 파일 대조: lap235가 적은 probe `2d4f6b36…50e7eb`, 테스트 `9f1992e5…3b6f39b6`,
     `tools/runtime_env.py` `103ec280…5ce02b`가 실제 파일 해시와 일치.
  2. `make check` → 255 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS` (lap235 주장과 일치).
  3. `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
  4. 자체 probe 13케이스 →
     `docs/history/laps/probes/20260912_lap236_r6b_r7_review_report.json`.
  5. 비공허성 변이 5케이스 →
     `docs/history/laps/probes/20260912_lap236_r6b_r7_mutation_report.json`.
  보존 대조: 실행 전후 `20260912_lap228_r6b_r3_review_report.json`과
  `20260912_lap230_lap228probe_rerun_report.json` 모두 sha256
  `739921763ca47cbc881dcb688cc909688ffddcb5c52f0e7620da4071921c6883`로 불변.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **R6-B-R7 범위 승인** — 13케이스 중
  11 AGREES / 2 DEFECT(둘 다 신규 비차단 후속, 보존 결함 아님).
  - 보존 7/7 AGREES: A1 내용 있는 기존 파일, A2 0바이트 파일, A3 디렉터리, A4 기존 파일을
    가리키는 심볼릭 링크, A5 **dangling 심볼릭 링크**(`exists()`가 False라 배타 생성만이
    유일한 가드인데 실제로 exit 2이고 링크 대상도 생성되지 않음), A6 인자 없는 기본 경로,
    A7 **import 실행**(`__name__ != "__main__"`이라 사전 검사를 건너뛰지만 `FileExistsError`
    분기가 exit 2로 fail-close). A5/A7은 lap235가 주장한 경쟁 보호 분기의 도달성을 실증한다.
  - 생성/충실도 4/4 AGREES: B1 새 경로에 lap 228·surgicality AGREES 보고서 생성,
    B2 두 번의 새 실행이 바이트 동일, B3 보존된 lap230 재실행 보고서와 `source_sha256`을
    제외한 전 필드 동일(현재 `103ec280…`, lap230 당시 `f39d26fc…` — lap231/lap233의
    runtime_env 변경 때문이며 판정은 불변), B4 reachability/preservation/wait defect 모두 [].
  - 비공허성: 변이 없음(M0) 2 passed, 두 가드 동시 제거(M3)와 `--output` 무시(M4)에서
    lap235 테스트가 실제로 실패(1 failed). 즉 회귀는 공허하지 않다.
  - DEFECT 2건(신규 등록): C1 부모 디렉터리 없음, C2 쓰기 불가 디렉터리에서 `--output`이
    exit 2 거부가 아니라 미분류 traceback + exit 1로 끝난다. 파일은 생성되지 않아 증거 보존은
    유지되지만, 존재 검사만 사전에 하고 쓰기 가능성은 검사하지 않아 오타 경로가 probe 전체
    계산을 마친 뒤에야 실패한다 → **R6-B-R10**(비차단).
  - 변이 M1(사전 검사만 제거), M2(`open("x")`만 제거)는 lap235 테스트가 잡지 못한다. 각 가드가
    단독으로도 관측 가능한 계약을 만족하기 때문이며 동작은 여전히 옳다. 다만 경쟁 보호 분기에
    독립 회귀가 없다 → **R6-B-R11**(비차단, 커버리지).
  - G1 제품, R6-B 전체, Stage B는 여전히 미승인·SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 검수는 게임 없이 수행했고 제품/도구
  코드를 바꾸지 않았다. lap228 원본 JSON 소실은 lap235 기록·PROVENANCE와 일치하며 재구성하지
  않았다. `source_sha256` 드리프트 때문에 현재 기본 경로 파일은 lap228 당시 결과가 아니라는 고지가
  계속 필요하다. S1/F2-R2, R6-B-R2, R6-B-R8/R9, WM_CLOSE teardown, G2~G4는 미해결이다.
  사용자 승인 범위(2026-09-12 01:03 KST bounded repair→fresh validation)는 유지되며 이번
  범위 승인은 제품 합격·마일스톤 이동이 아니다.
- 다음 한 가지: 새 work tier(Sonnet5/high 또는 Luna/high)가 **R6-B-R8**(관측 커버리지 임계)을
  한 건으로 다룬다. 그 뒤 R6-B-R9 → R6-B-R10 → R6-B-R11 → F2-R1 → F3-R1 → F3-R2 → F6-R2.
  S1/F2-R2·R6-B-R2 재결 전 게임 실행과 Stage B run은 계속 금지다.
