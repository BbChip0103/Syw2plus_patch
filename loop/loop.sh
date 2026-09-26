#!/usr/bin/env bash
# 자율 개발 루프.
#
# 한 바퀴 = 헤드리스 작업자 세션 하나(필요하면 상위 모델 세션 하나 추가). 매번 "새로" 연다.
# 대화를 이어 붙이지 않는다 (--continue / --resume 을 쓰지 않는다). 이게 핵심이다.
# 기억은 대화가 아니라 docs/ 의 파일에 남는다.

set -uo pipefail

# ─── 위치 확정 ──────────────────────────────────────────────────
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

# shellcheck source=./env.sh
. "$SCRIPT_DIR/env.sh"
# 개인 오버라이드 (있으면)
[ -f "$SCRIPT_DIR/env.local.sh" ] && . "$SCRIPT_DIR/env.local.sh"

# --dry-run 플래그
for arg in "$@"; do
  case "$arg" in
    --dry-run) LOOP_DRY_RUN=1 ;;
    --laps=*)  LOOP_MAX_LAPS="${arg#--laps=}" ;;
    --sleep=*) LOOP_SLEEP_SECONDS="${arg#--sleep=}" ;;
    --role=*)  LOOP_ROLE="${arg#--role=}" ;;
    *) echo "알 수 없는 인자: $arg" >&2; exit 2 ;;
  esac
done

for name in LOOP_MAX_LAPS LOOP_SLEEP_SECONDS LOOP_LAP_TIMEOUT LOOP_MAX_FAIL_STREAK; do
  [[ "${!name}" =~ ^[0-9]+$ ]] || { echo "Invalid numeric setting: $name" >&2; exit 2; }
done
[ "$LOOP_LAP_TIMEOUT" -gt 0 ] && [ "$LOOP_MAX_FAIL_STREAK" -gt 0 ] || exit 2

case "$LOOP_ROLE" in
  work|middle|astra) ;;
  *) echo "Invalid role: $LOOP_ROLE (work | middle | astra)" >&2; exit 2 ;;
esac

# All linked worktrees share writer ownership. Ordinary editor sessions must
# still use an isolated worktree; advisory locks cannot police arbitrary writes.
if [ -f "$PROJECT_DIR/$LOOP_STOP_FILE" ]; then
  printf 'LOOP DOWN | 이유=stop-file-preexisting\n'
  exit 0
fi
common_dir="$(git rev-parse --path-format=absolute --git-common-dir)" || exit 1
exec 9>"$common_dir/syw2plus-patch-loop.lock" || exit 1
flock -n 9 || { echo 'Loop writer already running (shared Git lock)' >&2; exit 73; }

LAP_DIR="$PROJECT_DIR/$LOOP_LOG_DIR/laps"
COUNTER_FILE="$SCRIPT_DIR/.lap_counter"
ESCALATION_PATH="$PROJECT_DIR/$LOOP_ESCALATION_FILE"
WORKER_CMD=()
ESCALATION_CMD=()
CLAUDE_HAS_MAX_TURNS=0
FULL_TEST_REQUEST="$SCRIPT_DIR/FULL_TEST"
FULL_TEST_RESULT="$PROJECT_DIR/$LOOP_LOG_DIR/full-test-latest.result"
PROGRESS_RESULT="$PROJECT_DIR/$LOOP_LOG_DIR/loop-progress.result"
UNCHANGED_STREAK=0
IMPLEMENTATION_UNCHANGED_STREAK=0
mkdir -p "$PROJECT_DIR/$LOOP_LOG_DIR" "$LAP_DIR"

# ─── 로깅 ───────────────────────────────────────────────────────
daily_log() { echo "$PROJECT_DIR/$LOOP_LOG_DIR/loop-$(date +%F).log"; }

log() {
  local line
  line="$(date '+%F %T %Z') | $*"
  printf '%s\n' "$line" >> "$(daily_log)"
  [ "$LOOP_TEE_STDOUT" = "1" ] && printf '%s\n' "$line"
  return 0
}

# Resolve role models once, with explicit IDs. Legacy aliases are accepted only
# when they do not conflict with the role-specific setting; a conflict is a
# hard error instead of silently changing the model in argv.
role_codex_model() {
  case "$1" in
    work)
      if [ -n "${LOOP_CODEX_MODEL:-}" ] && [ -n "${LOOP_CODEX_WORK_MODEL:-}" ] \
        && [ "$LOOP_CODEX_MODEL" != "$LOOP_CODEX_WORK_MODEL" ]; then
        log "FATAL: LOOP_CODEX_MODEL conflicts with LOOP_CODEX_WORK_MODEL"
        return 2
      fi
      printf '%s' "${LOOP_CODEX_MODEL:-${LOOP_CODEX_WORK_MODEL}}" ;;
    middle) printf '%s' "$LOOP_CODEX_MIDDLE_MODEL" ;;
    astra) printf '%s' "$LOOP_CODEX_ASTRA_MODEL" ;;
    *) return 2 ;;
  esac
}

role_claude_model() {
  case "$1" in
    work)
      if [ -n "${LOOP_MODEL:-}" ] && [ -n "${LOOP_CLAUDE_WORK_MODEL:-}" ] \
        && [ "$LOOP_MODEL" != "$LOOP_CLAUDE_WORK_MODEL" ]; then
        log "FATAL: LOOP_MODEL conflicts with LOOP_CLAUDE_WORK_MODEL"
        return 2
      fi
      printf '%s' "${LOOP_MODEL:-${LOOP_CLAUDE_WORK_MODEL}}" ;;
    middle) printf '%s' "$LOOP_CLAUDE_MIDDLE_MODEL" ;;
    astra) printf '%s' "$LOOP_CLAUDE_STRATEGY_MODEL" ;;
    *) return 2 ;;
  esac
}

role_provider() {
  case "$1" in
    work) printf '%s' "$LOOP_WORKER" ;;
    middle) printf '%s' "$LOOP_MIDDLE_PROVIDER" ;;
    astra) printf '%s' "$LOOP_STRATEGY_PROVIDER" ;;
    *) return 2 ;;
  esac
}

role_effort() {
  case "$1" in
    work) printf '%s' "$LOOP_WORK_EFFORT" ;;
    middle) printf '%s' "$LOOP_MIDDLE_EFFORT" ;;
    astra) printf '%s' "$LOOP_ASTRA_EFFORT" ;;
    *) return 2 ;;
  esac
}

middle_display_model() {
  if [ "$LOOP_MIDDLE_PROVIDER" = "codex" ]; then
    printf 'codex/%s' "$(role_codex_model middle)"
  else
    printf 'claude/%s' "$(role_claude_model middle)"
  fi
}

validate_codex_extra() {
  [ -n "${LOOP_CODEX_EXTRA:-}" ] || return 0
  # shellcheck disable=SC2206
  local extra=($LOOP_CODEX_EXTRA) i token next
  for ((i=0; i<${#extra[@]}; i++)); do
    token="${extra[$i]}"
    case "$token" in
      -m|--model|--effort)
        log "FATAL: LOOP_CODEX_EXTRA cannot override fixed role model/effort ($token)"
        return 2 ;;
      -m=*|--model=*|--effort=*)
        log "FATAL: LOOP_CODEX_EXTRA cannot override fixed role model/effort ($token)"
        return 2 ;;
      -m*)
        log "FATAL: LOOP_CODEX_EXTRA cannot override fixed role model/effort ($token)"
        return 2 ;;
      -c|--config)
        next="${extra[$((i + 1))]:-}"
        case "$next" in
          model=*|model_reasoning_effort=*)
            log "FATAL: LOOP_CODEX_EXTRA cannot override fixed role model/effort"
            return 2 ;;
        esac
        i=$((i + 1)) ;;
      -cmodel=*|-cmodel_reasoning_effort=*|--config=model=*|--config=model_reasoning_effort=*)
        log "FATAL: LOOP_CODEX_EXTRA cannot override fixed role model/effort"
        return 2 ;;
    esac
  done
}

# ─── 정상 종료 ──────────────────────────────────────────────────
GRACEFUL_STOP=0
on_signal() {
  GRACEFUL_STOP=1
  log "SIGNAL: 종료 신호 수신 — 현재 바퀴를 마치고 멈춘다"
}
trap on_signal TERM INT

stop_requested() {
  [ -f "$PROJECT_DIR/$LOOP_STOP_FILE" ] || [ "$GRACEFUL_STOP" = "1" ]
}

# ─── 사전 점검 ──────────────────────────────────────────────────
preflight() {
  local fail=0
  # 배역 이름부터 본다. 여기서 안 걸러내면 아래가 빈 이름을 찾다 헛말을 한다.
  case "$LOOP_WORKER" in
    claude|codex) ;;
    *) log "FATAL: LOOP_WORKER 값이 이상하다: '$LOOP_WORKER' (claude | codex)"; return 1 ;;
  esac
  case "$LOOP_JUDGE" in
    claude|codex) ;;
    *) log "FATAL: LOOP_JUDGE 값이 이상하다: '$LOOP_JUDGE' (claude | codex)"; return 1 ;;
  esac
  case "$LOOP_MIDDLE_PROVIDER" in
    claude|codex) ;;
    *) log "FATAL: LOOP_MIDDLE_PROVIDER 값이 이상하다: '$LOOP_MIDDLE_PROVIDER' (claude | codex)"; return 1 ;;
  esac
  case "$LOOP_STRATEGY_PROVIDER" in
    claude|codex) ;;
    *) log "FATAL: LOOP_STRATEGY_PROVIDER 값이 이상하다: '$LOOP_STRATEGY_PROVIDER' (claude | codex)"; return 1 ;;
  esac
  [ "$LOOP_WORK_EFFORT" = "high" ] || {
    log "FATAL: work effort는 high여야 한다 (LOOP_WORK_EFFORT=$LOOP_WORK_EFFORT)"
    return 1
  }
  [ "$LOOP_MIDDLE_EFFORT" = "high" ] || {
    log "FATAL: middle effort는 high여야 한다 (LOOP_MIDDLE_EFFORT=$LOOP_MIDDLE_EFFORT)"
    return 1
  }
  case "$LOOP_ASTRA_EFFORT" in
    medium|high) ;;
    *) log "FATAL: strategy effort는 medium 또는 high여야 한다 (LOOP_ASTRA_EFFORT=$LOOP_ASTRA_EFFORT)"; return 1 ;;
  esac
  [ -z "${LOOP_FALLBACK_MODEL:-}" ] || {
    log "FATAL: LOOP_FALLBACK_MODEL is unsupported; role routing has no fallback"
    return 1
  }
  validate_codex_extra || return 1
  # Resolve the selected stage before any command is started. Strategy provider
  # selection is explicit, and stale escalation aliases cannot replace the
  # middle tier silently.
  local selected_provider selected_model
  selected_provider="$(role_provider "$LOOP_ROLE")" || return 1
  if [ "$selected_provider" = "codex" ]; then
    selected_model="$(role_codex_model "$LOOP_ROLE")" || return 1
  else
    selected_model="$(role_claude_model "$LOOP_ROLE")" || return 1
  fi
  [ -n "$selected_model" ] || { log "FATAL: role=$LOOP_ROLE 모델이 비어 있다"; return 1; }
  if [ -n "${LOOP_CODEX_ESCALATION_MODEL:-}" ] && [ "$LOOP_MIDDLE_PROVIDER" = "codex" ] \
    && [ "$LOOP_CODEX_ESCALATION_MODEL" != "$LOOP_CODEX_MIDDLE_MODEL" ]; then
    log "FATAL: LOOP_CODEX_ESCALATION_MODEL conflicts with fixed middle model"
    return 1
  fi
  if [ -n "${LOOP_CLAUDE_ESCALATION_MODEL:-}" ] && [ "$LOOP_MIDDLE_PROVIDER" = "claude" ] \
    && [ "$LOOP_CLAUDE_ESCALATION_MODEL" != "$LOOP_CLAUDE_MIDDLE_MODEL" ]; then
    log "FATAL: LOOP_CLAUDE_ESCALATION_MODEL conflicts with fixed middle model"
    return 1
  fi

  # 작업자와 판정자가 둘 다 있어야 한다 — 판정자는 ⑥ 의 비주얼 갈림길에서 불린다.
  local bins=(git)
  if [ "$LOOP_DRY_RUN" != "1" ]; then
    [ "$LOOP_ENABLE_AGENT" = "1" ] || { log "FATAL: agent execution disabled"; return 1; }
    bins+=("$selected_provider" "$LOOP_JUDGE")
  fi
  for bin in "${bins[@]}"; do
    if ! command -v "$bin" >/dev/null 2>&1; then
      log "FATAL: '$bin' 을 PATH 에서 찾을 수 없다 (PATH=$PATH)"
      fail=1
    fi
  done

  # 공급자가 같아도 작업자와 판정자 모델이 다르면 모델 편향은 분리된다.
  if [ "$LOOP_WORKER" = "$LOOP_JUDGE" ]; then
    case "$LOOP_WORKER" in
      codex)
        local worker_codex_model judge_codex_model
        worker_codex_model="$(role_codex_model work)"
        judge_codex_model="${LOOP_CODEX_JUDGE_MODEL:-$LOOP_CODEX_MIDDLE_MODEL}"
        if [ "$worker_codex_model" != "$judge_codex_model" ]; then
          log "ROLE SPLIT: 같은 Codex 공급자, 다른 모델 | worker=$worker_codex_model judge=$judge_codex_model"
        else
          log "WARN: 작업자와 판정자가 같은 공급자/모델이다 ($LOOP_WORKER) — 비주얼 판정이 자기 맹점을 공유할 수 있다"
        fi
        ;;
      claude)
        local worker_claude_model judge_claude_model
        worker_claude_model="$(role_claude_model work)"
        judge_claude_model="${LOOP_CLAUDE_JUDGE_MODEL:-$LOOP_CLAUDE_MIDDLE_MODEL}"
        if [ "$worker_claude_model" != "$judge_claude_model" ]; then
          log "ROLE SPLIT: 같은 Claude 공급자, 다른 모델 | worker=$worker_claude_model judge=$judge_claude_model"
        else
          log "WARN: 작업자와 판정자가 같은 공급자/모델이다 ($LOOP_WORKER) — 비주얼 판정이 자기 맹점을 공유할 수 있다"
        fi
        ;;
    esac
  fi

  # codex 에는 턴 상한이 없다. 벽시계(timeout) 하나만 남는다는 것을 눈에 띄게 남긴다.
  if [ "$(role_provider "$LOOP_ROLE")" = "codex" ]; then
    log "WARN: 작업자가 codex 라 --max-turns($LOOP_MAX_TURNS) 가 안 걸린다 — 상한은 ${LOOP_LAP_TIMEOUT}s 뿐이다"
  fi
  if [ ! -f "$PROJECT_DIR/$LOOP_PROMPT_FILE" ]; then
    log "FATAL: 지시서가 없다: $LOOP_PROMPT_FILE"
    fail=1
  fi
  if ! git -C "$PROJECT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    log "FATAL: git 저장소가 아니다: $PROJECT_DIR"
    fail=1
  fi
  return $fail
}

next_lap_number() {
  local n=0
  [ -f "$COUNTER_FILE" ] && n="$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)"
  case "$n" in (''|*[!0-9]*) n=0 ;; esac
  n=$((n + 1))
  printf '%s' "$n" > "$COUNTER_FILE"
  printf '%s' "$n"
}

# ─── 안전 검사 (③ A1/A2/A3) ────────────────────────────────────
# 어기면 되돌릴 수 없는 것들. 규칙으로만 두지 않고 매 바퀴 전후로 잰다.
safety_check() {
  local when="$1" out rc
  [ -x "$PROJECT_DIR/checks/safety.sh" ] || {
    log "SAFETY $when | FATAL: 검사 스크립트 없음 또는 실행 불가 — 작업을 차단한다"
    return 1
  }
  out="$(LOOP_DRY_RUN="$LOOP_DRY_RUN" "$PROJECT_DIR/checks/safety.sh" check 2>&1)"; rc=$?
  if [ "$rc" -ne 0 ]; then
    log "SAFETY $when | ***** 위반 *****"
    printf '%s\n' "$out" | sed 's/^/    /' >> "$(daily_log)"
    [ "$LOOP_TEE_STDOUT" = "1" ] && printf '%s\n' "$out" | sed 's/^/    /'
    return 1
  fi
  log "SAFETY $when | ok"
  return 0
}

# Full tests belong to the loop, never to a waiting model session. Evidence files
# use .output/.result so ordinary *.log retention cannot erase a failed gate.
run_requested_full_gate() {
  [ -f "$FULL_TEST_REQUEST" ] || return 0
  stop_requested && return 0
  [ "$LOOP_DRY_RUN" = "1" ] && return 0
  safety_check "full-test 이전" || return 1
  local dir result output head head_after rc test_rc source_before source_after validation
  dir="$PROJECT_DIR/$LOOP_LOG_DIR/gates"
  mkdir -p "$dir" || return 1
  result="$(mktemp "$dir/full-test-$(date +%Y%m%dT%H%M%S)-XXXXXX.result")" || return 1
  output="${result%.result}.output"
  head="$(head_identity)" || return 1
  source_before="$(validation_fingerprint)" || return 1
  log "FULL TEST START | head=$head | source=$source_before | timeout=${LOOP_LAP_TIMEOUT}s | log=$output"
  timeout --signal=TERM --kill-after=60 "$LOOP_LAP_TIMEOUT" \
    bash "$PROJECT_DIR/tests/test_build.sh" > "$output" 2>&1
  test_rc=$?
  rc=$test_rc
  head_after="$(head_identity)"
  source_after="$(validation_fingerprint)" || source_after=unknown
  validation=failed
  [ "$rc" -ne 0 ] || validation=passed
  if [ "$source_before" != "$source_after" ]; then
    validation=invalidated
    [ "$rc" -ne 0 ] || rc=65
  fi
  {
    printf 'head=%s\nhead_after=%s\nexit=%s\nlog=%s\n' "$head" "$head_after" "$rc" "$output"
    printf 'source_before=%s\nsource_after=%s\n' "$source_before" "$source_after"
    printf 'test_exit=%s\nvalidation=%s\n' "$test_rc" "$validation"
    printf 'finished=%s\n' "$(date -u +%FT%TZ)"
  } > "$result" || return 1
  cp "$result" "$FULL_TEST_RESULT.tmp" && mv "$FULL_TEST_RESULT.tmp" "$FULL_TEST_RESULT" || return 1
  rm -f "$FULL_TEST_REQUEST" || return 1
  log "FULL TEST END | head=$head | exit=$rc | result=$result | log=$output"
  [ "$rc" -eq 0 ] || log "FULL TEST FAILED | 다음 작업자에게 실패 근거를 전달한다. 통과로 간주하지 않는다."
  if ! safety_check "full-test 이후"; then
    : > "$PROJECT_DIR/$LOOP_STOP_FILE"
    return 1
  fi
  # A failed test is durable worker input, not permission to repeat the gate.
  return 0
}

runtime_context() {
  printf '\n[Loop runtime evidence — process exit is not verification]\n'
  if [ -f "$FULL_TEST_RESULT" ]; then
    local current_source tested_source tested_source_after current_head tested_head
    current_source="$(validation_fingerprint)" || current_source=unknown
    tested_source="$(sed -n 's/^source_before=//p' "$FULL_TEST_RESULT")"
    tested_source_after="$(sed -n 's/^source_after=//p' "$FULL_TEST_RESULT")"
    current_head="$(head_identity)"
    tested_head="$(sed -n 's/^head=//p' "$FULL_TEST_RESULT")"
    printf 'current_head=%s\ncurrent_source=%s\n' "$current_head" "$current_source"
    if [ "$current_head" = "$tested_head" ]; then
      printf 'head_match=yes\n'
    else
      printf 'head_match=no\nHEAD is provenance; unchanged implementation may reuse its source-matched result after narrative-only changes.\n'
    fi
    if [ -n "$tested_source" ] && [ "$current_source" = "$tested_source" ] \
      && [ "$tested_source" = "$tested_source_after" ] && [ "$current_source" != unknown ]; then
      printf 'source_match=yes\n'
    else
      printf 'source_match=no\nOld success is not current verification; source identity differs or is unknown.\n'
    fi
    printf 'Gate scope: FAST source checks only; not a runtime/24k/144k proof.\n'
    printf 'Latest full-test result: %s\n' "$FULL_TEST_RESULT"
    cat "$FULL_TEST_RESULT"
    printf 'Nonzero exit means FAILED; inspect the exact log path before claiming success.\n'
    if ! grep -qx 'exit=0' "$FULL_TEST_RESULT"; then
      printf 'repair_required=yes\nNext task is failure diagnosis/repair, not feature expansion. Request a full gate after repair; a successful model exit does not clear this requirement.\n'
    fi
  fi
  if [ -f "$PROGRESS_RESULT" ]; then
    cat "$PROGRESS_RESULT"
    printf 'Narrative-only commits are not implementation progress. At implementation-unchanged-streak >= 2, reassess the next measurable change or record a concrete research blocker.\n'
    printf 'Repeated unchanged state is a warning, not a failed task. Preserve useful research in docs; do not spend a session waiting for tests.\n'
  fi
}

head_identity() {
  git rev-parse --verify HEAD 2>/dev/null || printf "unborn\n"
}

validation_fingerprint() {
  # Hash working content, not HEAD/diff identity: committing the same tested source
  # or updating live status must not require another full GUI run. Everything
  # nonignored is included except these narrative files; baseline/reference/history,
  # loop scripts, .gitignore, staged and new source files remain validation inputs.
  local path
  {
    while IFS= read -r -d '' path; do
      printf '%s\0' "$path"
      if [ -L "$path" ]; then
        printf 'symlink\0'; readlink -- "$path"
      elif [ -f "$path" ]; then
        if [ -x "$path" ]; then printf 'executable\0'; else printf 'file\0'; fi
        git hash-object --no-filters -- "$path" || return 1
      else
        printf 'missing\0'
      fi
    done < <(git ls-files --cached --others --exclude-standard -z -- . \
      ':(exclude)README.md' ':(exclude)loop/PROMPT.md' \
      ':(exclude)docs/STATUS.md' ':(exclude)docs/feedback/APPROVALS.md' \
      ':(exclude)docs/feedback/INBOX.md' "$@" | LC_ALL=C sort -zu)
  } | git hash-object --stdin
}

implementation_fingerprint() {
  # Research/baseline docs still invalidate full-gate evidence, but do not count
  # as a code change. Runtime, harness and build inputs count as implementation.
  validation_fingerprint ':(exclude)docs/**' ':(exclude)*.md'
}

work_fingerprint() {
  # Count content changes, not merely status lines; ignore generated/ignored files.
  {
    head_identity
    if git rev-parse --verify HEAD >/dev/null 2>&1; then
      git diff HEAD --binary --no-ext-diff
    else
      git diff --cached --binary --no-ext-diff
    fi
    while IFS= read -r -d '' path; do
      printf '%s\0' "$path"
      git hash-object -- "$path" 2>/dev/null || printf 'unreadable\n'
    done < <(git ls-files --others --exclude-standard -z)
  } | git hash-object --stdin
}

# ─── 로그 정리 ──────────────────────────────────────────────────
prune_logs() {
  [ "${LOOP_LOG_KEEP_DAYS:-14}" -gt 0 ] || return 0
  find "$PROJECT_DIR/$LOOP_LOG_DIR" -type f -name '*.log' \
       -mtime "+${LOOP_LOG_KEEP_DAYS}" -delete 2>/dev/null
  find "$LAP_DIR" -mindepth 1 -type d -empty -delete 2>/dev/null
  return 0
}

# ─── 한 바퀴 ────────────────────────────────────────────────────
BOOTSTRAP_PROMPT=$(cat <<'EOP'
이 저장소의 `loop/PROMPT.md` 를 먼저 읽어라. 그 문서가 이번 세션의 지시서다.
거기 적힌 ①~⑥을 순서대로 그대로 수행하고, 이번 바퀴에서 한 일을 마지막에 5줄 이내로 요약하라.

너는 이 프로젝트에서 방금 열린 새 세션이며, 이전 대화 기록은 없다.
문서에 적히지 않은 것은 존재하지 않는 것으로 취급하라.
EOP
)

GENERAL_ROUTING_PROMPT=$(cat <<'EOP'

이번 세션은 일반 작업자다. 다음 중 하나라도 해당하면 억지로 재시도하거나 마감하지 마라.
- 필수 빌드·테스트·검증이 예상 밖으로 실패했다.
- 구현 근거가 불명확하거나 서로 충돌한다.
- 현재 작업이 마일스톤을 마감하거나 다음 마일스톤으로 넘기는 경계다.

그 경우 현재 변경과 근거를 보존하고 `loop/ESCALATE_SOL` 파일을 만든 뒤,
무엇을 승격 작업자가 이어서 검증해야 하는지 마지막 요약에 적고 세션을 끝내라.
EOP
)

ESCALATED_ROUTING_PROMPT=$(cat <<'EOP'

이번 세션은 승격된 상위 모델 작업자다. 현재 worktree, 문서, 테스트 근거를 직접 점검해
일반 작업자가 멈춘 같은 바퀴를 복구·검증·마감하라. `loop/ESCALATE_SOL` 파일을 다시
만들지 마라. 해결하지 못하면 실패를 숨기지 말고 명확한 비정상 종료 또는 실패 근거를 남겨라.
EOP
)

STAGE_ROUTING_PROMPT=""
case "$LOOP_ROLE" in
  work)
    STAGE_ROUTING_PROMPT=$(cat <<'EOP'

역할은 hands-on 구현 작업자다. 실제 코드/테스트 변경은 이 역할에서만 한다.
큰 방향, 마스터 계획, 중간 확인이 필요하면 구현을 추측하지 말고 중간 tier로 넘긴다.
EOP
)
    ;;
  middle)
    STAGE_ROUTING_PROMPT=$(cat <<'EOP'

역할은 중간 tier(진단·계획·확인)다. 게임 코드의 hands-on 수정은 하지 않는다.
문제의 원인과 검증 가능한 계획 또는 확인 결과를 남기고, 수정이 필요하면 work tier
작업자에게 넘길 명시적 handoff를 남긴다. 프로세스 exit 0은 계획 승인/검증 통과가 아니다.
EOP
)
    ;;
  astra)
    STAGE_ROUTING_PROMPT=$(cat <<'EOP'

역할은 strategy major direction/master-plan 세션이다. 선택된 공급자는 Codex Astra 또는
Claude Code Fable이다. 게임 코드를 직접 수정하지 않는다.
범위·우선순위·검증 기준을 결정 가능한 문서 산출물로 남기고, 실제 실행은 middle/work
handoff로 분리한다. 프로세스 exit 0은 계획 승인/검증 통과가 아니다.
EOP
)
    ;;
esac

run_agent_session() {
  local prompt="$1" lapfile="$2" write_mode="$3" cmd_name="$4"
  local -n cmd_ref="$cmd_name"
  local rc
  safety_check "agent 이전" || return 90
  run_requested_full_gate || return 90
  stop_requested && return 0
  prompt="$prompt$(runtime_context)"
  if [ "$write_mode" = "append" ]; then
    printf '%s\n' "$prompt" \
      | timeout --signal=TERM --kill-after=60 "$LOOP_LAP_TIMEOUT" \
          "${cmd_ref[@]}" >> "$lapfile" 2>&1
  else
    printf '%s\n' "$prompt" \
      | timeout --signal=TERM --kill-after=60 "$LOOP_LAP_TIMEOUT" \
          "${cmd_ref[@]}" > "$lapfile" 2>&1
  fi
  rc=$?
  if ! safety_check "agent 이후"; then
    : > "$PROJECT_DIR/$LOOP_STOP_FILE"
    return 90
  fi
  run_requested_full_gate || return 90
  return "$rc"
}

run_lap() {
  local lap="$1"
  local day lapfile started ended rc dur direct_escalation=0 escalation_reason=""
  day="$(date +%F)"
  mkdir -p "$LAP_DIR/$day"
  lapfile="$(printf '%s/%s/lap-%04d.log' "$LAP_DIR" "$day" "$lap")"
  started="$(date +%s)"
  local before after implementation_before implementation_after
  before="$(work_fingerprint)"
  implementation_before="$(implementation_fingerprint)"

  # Middle review is always a separate explicit plan/review stage. Never let
  # a pending marker turn a work lap into a middle-model implementation lap.

  # 안 걸리는 상한을 걸린 것처럼 적지 않는다 (③ B5) — codex 에는 effort·turns 가 없다.
  local shown_model shown_limits role_effort_name
  local role_provider_name role_model_name
  role_provider_name="$(role_provider "$LOOP_ROLE")"
  role_effort_name="$(role_effort "$LOOP_ROLE")"
  if [ "$role_provider_name" = "codex" ]; then
    role_model_name="$(role_codex_model "$LOOP_ROLE")"
    if [ "$direct_escalation" -eq 1 ]; then
      shown_model="$(middle_display_model) (승격 이어받기)"
    else
      shown_model="$role_model_name"
    fi
    shown_limits="effort=$role_effort_name max_turns=-"
  else
    role_model_name="$(role_claude_model "$LOOP_ROLE")"
    if [ "$direct_escalation" -eq 1 ]; then
      shown_model="$(middle_display_model) (승격 이어받기)"
    else
      shown_model="$role_model_name"
    fi
    if [ "$CLAUDE_HAS_MAX_TURNS" -eq 1 ]; then
      shown_limits="effort=$role_effort_name max_turns=$LOOP_MAX_TURNS"
    else
      shown_limits="effort=$role_effort_name max_turns=-"
    fi
  fi
  log "LAP $lap START | worker=$role_provider_name judge=$LOOP_JUDGE model=$shown_model $shown_limits timeout=${LOOP_LAP_TIMEOUT}s | log=$lapfile"

  if [ "$LOOP_DRY_RUN" = "1" ]; then
    {
      echo "=== DRY RUN — 작업자를 부르지 않는다 ==="
      echo "cwd:      $PROJECT_DIR"
      echo "prompt:   $LOOP_PROMPT_FILE"
      echo "role:     $LOOP_ROLE"
      echo "worker:   $LOOP_WORKER"
      echo "judge:    $LOOP_JUDGE"
      if [ "$LOOP_JUDGE" = "codex" ]; then
        echo "judge-model: ${LOOP_CODEX_JUDGE_MODEL:-$LOOP_CODEX_MIDDLE_MODEL} (middle tier)"
      else
        echo "judge-model: ${LOOP_CLAUDE_JUDGE_MODEL:-$LOOP_CLAUDE_MIDDLE_MODEL} (middle tier)"
      fi
      echo "escalate: $(middle_display_model)"
      if [ "$role_provider_name" = "codex" ]; then
        echo "model:    $shown_model"
        echo "argv-model-effort: -m $(role_codex_model "$LOOP_ROLE") -c model_reasoning_effort=$role_effort_name"
        echo "turns:    - (codex 에 --max-turns 가 없다)"
      else
        echo "model:    $shown_model"
        echo "argv-model-effort: --model $(role_claude_model "$LOOP_ROLE") --effort $role_effort_name"
        if [ "$CLAUDE_HAS_MAX_TURNS" -eq 1 ]; then
          echo "turns:    $LOOP_MAX_TURNS"
        else
          echo "turns:    - (현재 claude CLI 에 --max-turns 가 없다)"
        fi
      fi
      echo "timeout:  ${LOOP_LAP_TIMEOUT}s"
      echo "PATH:     $PATH"
      echo "--- 실행되었을 명령 (지시는 stdin) ---"
      printf '%q ' "${WORKER_CMD[@]}"; echo
      if [ "${#ESCALATION_CMD[@]}" -gt 0 ]; then
        echo "--- 중간 tier 승격 명령 (진단/계획/확인 전용) ---"
        printf '%q ' "${ESCALATION_CMD[@]}"; echo
      fi
    } > "$lapfile" 2>&1
    rc=0
  else
    if [ "$direct_escalation" -eq 1 ]; then
      rm -f "$ESCALATION_PATH"
      log "LAP $lap ROUTE | 이전 승격 표식을 상위 모델이 직접 이어받는다 | model=$shown_model"
      run_agent_session "$BOOTSTRAP_PROMPT$ESCALATED_ROUTING_PROMPT$STAGE_ROUTING_PROMPT" "$lapfile" truncate ESCALATION_CMD
      rc=$?
      [ -f "$ESCALATION_PATH" ] && rc=75
    else
      # 지시는 stdin 으로 넣는다. 인자로 붙이면 가변 인자 옵션이 삼킬 수 있다.
      run_agent_session "$BOOTSTRAP_PROMPT$GENERAL_ROUTING_PROMPT$STAGE_ROUTING_PROMPT" "$lapfile" truncate WORKER_CMD
      rc=$?

      if [ "$rc" -ne 0 ]; then
        escalation_reason="worker-exit=$rc"
      elif [ -f "$ESCALATION_PATH" ]; then
        escalation_reason="worker-request"
      fi

      if [ -n "$escalation_reason" ]; then
        log "LAP $lap ROUTE | middle review pending | reason=$escalation_reason; run plan/review explicitly"
        [ "$rc" -eq 0 ] && rc=75
      fi
    fi
  fi

  ended="$(date +%s)"
  dur=$((ended - started))

  case "$rc" in
    0)   log "LAP $lap END   | PROCESS_OK | ${dur}s — 작업 진척/검증 통과와 별개" ;;
    124) log "LAP $lap END   | TIMEOUT | ${dur}s — ${LOOP_LAP_TIMEOUT}s 초과로 잘렸다. 미커밋 파일은 남지만 검증이 중단됐다 (⑤ 참조)" ;;
    *)   log "LAP $lap END   | FAIL    | ${dur}s | exit=$rc" ;;
  esac

  # 요약: 마지막 몇 줄을 일별 로그에도 남겨서, 로그만 봐도 흐름이 읽히게 한다
  if [ -s "$lapfile" ]; then
    log "LAP $lap TAIL  |"
    tail -n 8 "$lapfile" | sed 's/^/    /' >> "$(daily_log)"
    [ "$LOOP_TEE_STDOUT" = "1" ] && tail -n 8 "$lapfile" | sed 's/^/    /'
  else
    log "LAP $lap TAIL  | (출력 없음)"
  fi

  after="$(work_fingerprint)"
  if [ "$before" = "$after" ]; then
    UNCHANGED_STREAK=$((UNCHANGED_STREAK + 1))
  else
    UNCHANGED_STREAK=0
  fi
  implementation_after="$(implementation_fingerprint)"
  if [ "$implementation_before" = "$implementation_after" ]; then
    IMPLEMENTATION_UNCHANGED_STREAK=$((IMPLEMENTATION_UNCHANGED_STREAK + 1))
  else
    IMPLEMENTATION_UNCHANGED_STREAK=0
  fi
  printf 'lap=%s\nunchanged-streak=%s\nimplementation-unchanged-streak=%s\n' \
    "$lap" "$UNCHANGED_STREAK" "$IMPLEMENTATION_UNCHANGED_STREAK" > "$PROGRESS_RESULT"
  if [ "$UNCHANGED_STREAK" -ge 2 ]; then
    log "LAP $lap WARN | unchanged-streak=$UNCHANGED_STREAK | HEAD와 worktree 내용이 반복해서 같다 (실패 판정 아님)"
  fi

  # git 상태 한 줄 — 커밋 없이 지나간 바퀴를 눈에 띄게 한다
  local dirty head_short
  dirty="$(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null | wc -l)"
  head_short="$(git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo '-')"
  log "LAP $lap GIT   | HEAD=$head_short | uncommitted=$dirty"
  [ "$dirty" -gt 0 ] && log "LAP $lap WARN  | 커밋되지 않은 변경 $dirty 건이 남았다"

  return $rc
}

# ─── 명령 조립 ──────────────────────────────────────────────────
# 작업자는 LOOP_WORKER 가 정한다 (claude | codex). 지시서는 모델 이름을 모른다.
# 어느 쪽이든 **세션을 이어 붙이지 않는다** — claude 의 --continue/--resume,
# codex 의 `exec resume` 은 의도적으로 없다. 기억은 대화가 아니라 docs/ 에 남는다.
build_codex_cmd() {
  local target_name="$1" model="$2" effort="$3"
  local -n target="$target_name"
  target=(codex exec -C "$PROJECT_DIR" --skip-git-repo-check)
  if [ -n "${LOOP_EXTRA_DIRS:-}" ]; then
    local d
    for d in $LOOP_EXTRA_DIRS; do target+=(--add-dir "$d"); done
  fi
  [ -n "$model" ] && target+=(-m "$model")
  # Codex uses config for reasoning effort; this is deliberately not left to
  # the installed CLI default.
  target+=(-c "model_reasoning_effort=$effort")
  if [ "$LOOP_SKIP_PERMISSIONS" = "1" ]; then
    target+=(--dangerously-bypass-approvals-and-sandbox)
  else
    target+=(--sandbox "$LOOP_CODEX_SANDBOX")
  fi
  if [ -n "$LOOP_CODEX_EXTRA" ]; then
    # shellcheck disable=SC2206
    local extra_codex=($LOOP_CODEX_EXTRA)
    target+=("${extra_codex[@]}")
  fi
}

build_claude_cmd() {
  local target_name="$1" model="$2" effort="$3"
  local -n target="$target_name"
  target=(claude --print)
  # 가변 인자 옵션(--add-dir)은 반드시 다른 옵션보다 앞에 둔다.
  if [ -n "${LOOP_EXTRA_DIRS:-}" ]; then
    # shellcheck disable=SC2206
    local extra=($LOOP_EXTRA_DIRS)
    target+=(--add-dir "${extra[@]}")
  fi
  target+=(--model "$model")
  target+=(--effort "$effort")
  [ "$CLAUDE_HAS_MAX_TURNS" -eq 1 ] && target+=(--max-turns "$LOOP_MAX_TURNS")
  [ -n "$LOOP_MAX_BUDGET_USD" ] && target+=(--max-budget-usd "$LOOP_MAX_BUDGET_USD")
  if [ "$LOOP_SKIP_PERMISSIONS" = "1" ]; then
    target+=(--dangerously-skip-permissions)
  else
    target+=(--permission-mode "$LOOP_PERMISSION_MODE")
  fi
}

build_cmd() {
  local provider model effort
  provider="$(role_provider "$LOOP_ROLE")" || return 1
  effort="$(role_effort "$LOOP_ROLE")" || return 1
  if [ "$provider" = "codex" ]; then
    model="$(role_codex_model "$LOOP_ROLE")" || return 1
    build_codex_cmd WORKER_CMD "$model" "$effort"
  else
    model="$(role_claude_model "$LOOP_ROLE")" || return 1
    # A dry inspection must not invoke even `claude --help`.
    if [ "$LOOP_DRY_RUN" != "1" ] && claude --help 2>&1 | grep -q -- '--max-turns'; then
      CLAUDE_HAS_MAX_TURNS=1
    fi
    build_claude_cmd WORKER_CMD "$model" "$effort"
  fi

  # Existing automatic escalation is intentionally the intermediate tier:
  # diagnosis/planning/confirmation only. It is never a replacement worker.
  local middle_model
  if [ "$LOOP_MIDDLE_PROVIDER" = "codex" ]; then
    middle_model="$(role_codex_model middle)" || return 1
    build_codex_cmd ESCALATION_CMD "$middle_model" "$LOOP_MIDDLE_EFFORT"
  else
    middle_model="$(role_claude_model middle)" || return 1
    build_claude_cmd ESCALATION_CMD "$middle_model" "$LOOP_MIDDLE_EFFORT"
  fi
  return 0
}

# ─── 본체 ───────────────────────────────────────────────────────
main() {
  local startup_provider startup_worker_model startup_judge_model startup_escalation_model
  startup_provider="$(role_provider "$LOOP_ROLE")"
  if [ "$startup_provider" = "codex" ]; then
    startup_worker_model="$(role_codex_model "$LOOP_ROLE")"
  else
    startup_worker_model="$(role_claude_model "$LOOP_ROLE")"
  fi
  if [ "$LOOP_JUDGE" = "codex" ]; then
    startup_judge_model="${LOOP_CODEX_JUDGE_MODEL:-$LOOP_CODEX_MIDDLE_MODEL}"
  else
    startup_judge_model="${LOOP_CLAUDE_JUDGE_MODEL:-$LOOP_CLAUDE_MIDDLE_MODEL}"
  fi
  startup_escalation_model="$(middle_display_model)"
  log "=================================================================="
  log "LOOP UP | pid=$$ | dir=$PROJECT_DIR | worker=$startup_provider/$startup_worker_model | judge=$LOOP_JUDGE/$startup_judge_model | escalate=$startup_escalation_model | dry_run=$LOOP_DRY_RUN"

  preflight || { log "사전 점검 실패 — 멈춘다"; exit 1; }
  build_cmd || { log "명령 조립 실패 — 멈춘다"; exit 1; }

  if [ -f "$PROJECT_DIR/$LOOP_STOP_FILE" ]; then
    log "STOP 파일이 이미 있다 ($LOOP_STOP_FILE) — 한 바퀴도 돌지 않는다"
    log "LOOP DOWN | 이유=stop-file-preexisting"
    exit 0
  fi

  if ! safety_check "기동"; then
    log "LOOP DOWN | 이유=safety-violation-at-startup — 한 바퀴도 돌지 않는다"
    exit 1
  fi

  local laps_done=0 lap rc fail_streak=0
  while :; do
    prune_logs
    lap="$(next_lap_number)"
    run_lap "$lap"; rc=$?
    laps_done=$((laps_done + 1))

    # 안전 위반은 즉시 정지. 되돌리지 않는다 — 사람이 봐야 한다.
    if ! safety_check "lap $lap 이후"; then
      : > "$PROJECT_DIR/$LOOP_STOP_FILE"
      log "LOOP DOWN | 이유=safety-violation | STOP 파일을 만들었다. 사람이 확인해야 한다"
      exit 1
    fi

    # An explicit middle review is terminal. Preserve ESCALATE_SOL and do not
    # let fail-streak, retry, or max-laps turn the handoff into a false success.
    if [ "$rc" -eq 75 ] && [ -f "$ESCALATION_PATH" ]; then
      log "LOOP DOWN | 이유=middle-review-pending | ESCALATE_SOL을 보존하고 상위 검수로 넘긴다"
      exit 75
    fi

    # 같은 실패가 반복되면 선다. 백오프만으로는 영원히 돈다.
    if [ "$rc" -ne 0 ]; then
      fail_streak=$((fail_streak + 1))
      log "LAP $lap | 연속 실패 $fail_streak/${LOOP_MAX_FAIL_STREAK}"
      if [ "$fail_streak" -ge "${LOOP_MAX_FAIL_STREAK:-5}" ]; then
        : > "$PROJECT_DIR/$LOOP_STOP_FILE"
        log "LOOP DOWN | 이유=fail-streak | ${fail_streak}회 연속 실패 — 스스로 못 빠져나온다"
        exit 1
      fi
    else
      fail_streak=0
    fi

    if stop_requested; then
      log "LOOP DOWN | 이유=stop-requested | 이번 세션에서 $laps_done 바퀴 완료"
      exit 0
    fi

    if [ "$LOOP_MAX_LAPS" -gt 0 ] && [ "$laps_done" -ge "$LOOP_MAX_LAPS" ]; then
      log "LOOP DOWN | 이유=max-laps($LOOP_MAX_LAPS) | $laps_done 바퀴 완료"
      exit 0
    fi

    local nap="$LOOP_SLEEP_SECONDS"
    [ "$rc" -ne 0 ] && nap=$((LOOP_SLEEP_SECONDS + LOOP_FAIL_BACKOFF_SECONDS))
    if [ "$nap" -gt 0 ]; then
      log "SLEEP ${nap}s"
      sleep "$nap" &
      wait $! 2>/dev/null   # 신호를 즉시 받기 위해 background + wait
    fi

    if stop_requested; then
      log "LOOP DOWN | 이유=stop-requested(sleep 중) | $laps_done 바퀴 완료"
      exit 0
    fi
  done
}

main
