#!/usr/bin/env bash
# 루프 설정. loop.sh 가 매 실행마다 source 한다.
# 개인 설정은 이 파일을 고치지 말고 loop/env.local.sh 를 만들어라 (.gitignore 됨).

# ─── 배역 ───────────────────────────────────────────────────────
# 이 루프에는 자리가 둘이다. 지시서(loop/PROMPT.md)는 모델 이름을 모르고
# **둘이 서로 다르다**는 것만 요구한다 (⑥).
#
#   작업자  한 바퀴를 도는 에이전트.
#   판정자  별도 비주얼 검수에 사용할 모델 설정(자동 호출 아님).
#
# 왜 달라야 하나 — 독립이 두 종류이기 때문이다.
#   컨텍스트 독립: 세션을 새로 열면 얻는다. 매 바퀴 자동이다.
#   모델 편향 독립: 다른 모델을 불러야 얻는다.
# 코드 검수는 앞의 것만으로 서지만, 비주얼 판정은 뒤의 것이 필요하다 —
# "두 화면이 같아 보인다" 는 지각의 실패라, 같은 모델이면 세션을 새로 열어도
# 같은 자리에서 똑같이 못 본다.
: "${LOOP_WORKER:=codex}"          # hands-on provider: claude | codex
# Requested stage for loop.sh; loopctl selects this explicitly.
: "${LOOP_ROLE:=work}"             # work | middle | astra

# Major-direction provider.  The internal role name remains `astra` for log and
# command compatibility, but the strategy session can be either Codex Astra or
# Claude Code Fable.  Selection is explicit; there is no automatic fallback.
: "${LOOP_STRATEGY_PROVIDER:=codex}" # codex | claude

# Middle tier is diagnosis/planning/confirmation only. Codex is the default;
# selecting Claude is an explicit alternative, never a silent fallback.
: "${LOOP_MIDDLE_PROVIDER:=codex}"

# 비우면 작업자의 반대쪽을 자동으로 고른다.
: "${LOOP_JUDGE:=}"
if [ -z "$LOOP_JUDGE" ]; then
  # The judge is a middle-tier confirmation role, so follow its provider by
  # default. An explicit LOOP_JUDGE remains an allowed visual-review split.
  LOOP_JUDGE="${LOOP_MIDDLE_PROVIDER:-codex}"
fi
export LOOP_JUDGE

# ─── 모델 ───────────────────────────────────────────────────────
# LOOP_WORKER=claude 일 때. opus / sonnet / haiku 또는 전체 모델명
: "${LOOP_MODEL:=}"              # legacy work-model alias; prefer LOOP_CLAUDE_WORK_MODEL

# LOOP_WORKER=codex 일 때. 비우면 codex 의 기본값을 쓴다.
# (모델 이름 체계가 서로 달라서 LOOP_MODEL 을 같이 쓸 수 없다)
: "${LOOP_CODEX_MODEL:=}"        # legacy work-model alias; prefer LOOP_CODEX_WORK_MODEL

# Explicit role models. Defaults are fixed, verified IDs; do not rely on CLI defaults.
: "${LOOP_CODEX_WORK_MODEL:=gpt-5.6-luna}"
: "${LOOP_CODEX_MIDDLE_MODEL:=gpt-5.6-sol}"
: "${LOOP_CODEX_ASTRA_MODEL:=gpt-6-astra}"
: "${LOOP_CLAUDE_WORK_MODEL:=claude-sonnet-5}"
: "${LOOP_CLAUDE_MIDDLE_MODEL:=claude-opus-5}"
: "${LOOP_CLAUDE_STRATEGY_MODEL:=claude-fable-5}"

# LOOP_JUDGE=codex 일 때 비주얼 판정에 쓸 middle-tier 모델.
# 작업자와 같은 공급자여도 모델을 달리 지정하면 모델 편향을 분리할 수 있다.
: "${LOOP_CODEX_JUDGE_MODEL:=}"

# LOOP_JUDGE=claude 일 때 비주얼 판정에 쓸 middle-tier 모델.
: "${LOOP_CLAUDE_JUDGE_MODEL:=}"

# 구 legacy 이름. 자동 승격은 비워도 항상 선택한 middle tier로 간다.
: "${LOOP_CODEX_ESCALATION_MODEL:=}" # legacy alias; middle tier is authoritative

# 구 legacy 이름. 자동 승격은 비워도 항상 선택한 middle tier로 간다.
: "${LOOP_CLAUDE_ESCALATION_MODEL:=}" # legacy alias; middle tier is authoritative

# 일반 작업자가 승격이 필요하다고 알리는 일회성 표식. git 에는 들어가지 않는다.
: "${LOOP_ESCALATION_FILE:=loop/ESCALATE_SOL}"
export LOOP_CODEX_JUDGE_MODEL LOOP_CLAUDE_JUDGE_MODEL
export LOOP_CODEX_ESCALATION_MODEL LOOP_CLAUDE_ESCALATION_MODEL LOOP_ESCALATION_FILE
export LOOP_ROLE LOOP_MIDDLE_PROVIDER LOOP_STRATEGY_PROVIDER
export LOOP_CODEX_WORK_MODEL LOOP_CODEX_MIDDLE_MODEL LOOP_CODEX_ASTRA_MODEL
export LOOP_CLAUDE_WORK_MODEL LOOP_CLAUDE_MIDDLE_MODEL LOOP_CLAUDE_STRATEGY_MODEL

# codex 에 그대로 넘길 여분 인자 (공백 구분). 모델/추론 강도 override는 금지한다.
# model/effort는 각 role의 고정 argv로만 전달한다.
: "${LOOP_CODEX_EXTRA:=}"

# 역할별 추론 강도. work/middle은 high로 고정하고 strategy만 기본 medium,
# 큰 분기나 교착에서 명시적으로 high로 올린다. LOOP_ASTRA_EFFORT라는
# 이름은 기존 설정 호환을 위해 유지하며 Fable strategy에도 동일하게 적용한다.
: "${LOOP_EFFORT:=high}"          # legacy fallback for work/middle
: "${LOOP_WORK_EFFORT:=$LOOP_EFFORT}"
: "${LOOP_MIDDLE_EFFORT:=$LOOP_EFFORT}"
: "${LOOP_ASTRA_EFFORT:=medium}"
: "${LOOP_ASTRA_REVIEW_INTERVAL:=10}" # 운영 cadence 힌트; 자동 호출하지 않는다.
export LOOP_EFFORT LOOP_WORK_EFFORT LOOP_MIDDLE_EFFORT LOOP_ASTRA_EFFORT
export LOOP_ASTRA_REVIEW_INTERVAL

# ─── 한 바퀴의 상한 ─────────────────────────────────────────────
# Claude 한 바퀴 최대 턴 수. Codex는 벽시계 제한만 적용한다.
# 매 바퀴 파일 기록을 남긴다. 커밋은 사용자 허용이 있을 때만 한다.
# Claude CLI 버전에 따라 없을 수 있다. loop.sh 는 `claude --help` 로 지원 여부를
# 확인하고, 없으면 거짓 상한을 넘기지 않고 LOOP_LAP_TIMEOUT 만 적용한다.
# codex exec 에는 대응 플래그가 없다.
: "${LOOP_MAX_TURNS:=180}"

# 한 바퀴의 최대 벽시계 시간(초). 턴 수와 무관하게 여기서도 자른다.
: "${LOOP_LAP_TIMEOUT:=5400}"

# claude --print 는 백그라운드 작업을 기본 600초까지만 기다린 뒤 세션을 끊는다.
# 참고 루프의 장기 tests/test_build.sh 는 lap331에서 이 상한에 잘린 이력이 있다.
# 패치 루프의 FULL_TEST는 Fast이며 같은 장기 실행이라고 주장하지 않는다.
# 0 이면 무한정 기다린다. 한 바퀴의 실제 상한은 LOOP_LAP_TIMEOUT 이 잡는다.
: "${CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS:=0}"
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS

# 한 바퀴의 최대 비용(USD). 비우면 무제한.
# 비워두면 무제한. 실제 소모를 본 뒤 정하는 편이 낫다.
: "${LOOP_MAX_BUDGET_USD:=}"

# ─── 바퀴 사이 ──────────────────────────────────────────────────
# 다음 바퀴까지 대기(초). 0 이면 바로 다음 바퀴.
: "${LOOP_SLEEP_SECONDS:=30}"

# 최대 바퀴 수. 0 이면 무한.
: "${LOOP_MAX_LAPS:=1}"

# 바퀴가 실패(비정상 종료)했을 때 추가로 쉬는 시간(초).
: "${LOOP_FAIL_BACKOFF_SECONDS:=120}"

# 연속 실패가 이 횟수에 닿으면 루프를 세운다.
# 백오프만으로는 같은 실패를 영원히 반복한다.
: "${LOOP_MAX_FAIL_STREAK:=5}"

# ─── 권한 ───────────────────────────────────────────────────────
# 이 프로젝트의 기본은 권한 우회 없음이다. 원본/참고 경로는 쓰지 않는다.
# 1 이면 claude 는 --dangerously-skip-permissions,
#        codex 는 --dangerously-bypass-approvals-and-sandbox 를 붙인다.
: "${LOOP_SKIP_PERMISSIONS:=0}"
# LOOP_SKIP_PERMISSIONS=0 일 때 claude 가 쓸 모드: acceptEdits | auto | plan | manual
: "${LOOP_PERMISSION_MODE:=acceptEdits}"
# LOOP_SKIP_PERMISSIONS=0 일 때 codex 가 쓸 샌드박스: read-only | workspace-write
: "${LOOP_CODEX_SANDBOX:=workspace-write}"

# ─── 경로 ───────────────────────────────────────────────────────
: "${LOOP_PROMPT_FILE:=loop/PROMPT.md}"

# 프로젝트 밖에서 읽어야 할 참고 디렉토리 (공백 구분).
# 예: 이전 레포 / 원본 자산.  비우면 현재 폴더만 본다.
#   LOOP_EXTRA_DIRS="/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re"
: "${LOOP_EXTRA_DIRS:=}"
: "${LOOP_LOG_DIR:=logs}"
: "${LOOP_STOP_FILE:=loop/STOP}"

# ─── 동작 ───────────────────────────────────────────────────────
# 1 이면 claude 를 부르지 않고 배관(로그·카운터·STOP)만 점검한다.
: "${LOOP_DRY_RUN:=0}"

# 로그 보관 일수. 0 이면 안 지운다.
: "${LOOP_LOG_KEEP_DAYS:=0}"

# 라이브 로그를 화면에도 흘릴지. systemd 아래서는 journald 로 간다.
: "${LOOP_TEE_STDOUT:=1}"

# ─── PATH ───────────────────────────────────────────────────────
# 자동 실행(systemd)은 평소 터미널 환경을 물려받지 않는다.
# 여기서 명시하지 않으면 claude / git / node 를 못 찾고 조용히 죽는다.
: "${LOOP_PATH:=$PATH}"
export PATH="$LOOP_PATH"

# Explicit operator opt-ins; setup never launches a paid agent or commits.
: "${LOOP_ENABLE_AGENT:=0}"
: "${LOOP_ALLOW_COMMITS:=0}"
export LOOP_ENABLE_AGENT LOOP_ALLOW_COMMITS
