#!/usr/bin/env bash
# 루프 제어 — 켜기 / 끄기 / 상태 보기 를 한 곳에서.
#
#   loop/loopctl.sh install     systemd user unit 설치 (등록만, 켜지지 않음)
#   loop/loopctl.sh on          로그인 시 자동 시작 활성화 + 지금 시작
#   loop/loopctl.sh off         지금 멈춤 + 자동 시작 해제
#   loop/loopctl.sh status      상태 요약
#   loop/loopctl.sh logs [-f]   최근 로그 (‑f 면 실시간)
#   loop/loopctl.sh models      역할별 모델/effort 라우팅만 조회
#   loop/loopctl.sh strategy [N] 선택된 Astra/Fable 전략 세션을 N 바퀴 실행
#   loop/loopctl.sh plan [N]    중간 tier 계획/진단 세션
#   loop/loopctl.sh review [N]  중간 tier 확인 세션
#   loop/loopctl.sh stop        STOP 파일을 만들어 "현재 바퀴를 마치고" 멈춤
#   loop/loopctl.sh resume      STOP 파일 제거
#   loop/loopctl.sh run [N]     systemd 없이 hands-on work tier를 N 바퀴 돌림
#   loop/loopctl.sh dry [role|N] 작업자 CLI 없이 역할 argv/배관 점검
#   loop/loopctl.sh uninstall   unit 제거

set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
. "$SCRIPT_DIR/env.sh"
[ -f "$SCRIPT_DIR/env.local.sh" ] && . "$SCRIPT_DIR/env.local.sh"

UNIT="syw2plus-patch-loop.service"
UNIT_SRC="$SCRIPT_DIR/syw2plus-patch-loop.service"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
UNIT_DST="$UNIT_DIR/$UNIT"
STOP_PATH="$PROJECT_DIR/$LOOP_STOP_FILE"

c_ok()   { printf '\033[32m%s\033[0m\n' "$*"; }
c_warn() { printf '\033[33m%s\033[0m\n' "$*"; }
c_err()  { printf '\033[31m%s\033[0m\n' "$*"; }
head_()  { printf '\n\033[1m%s\033[0m\n' "$*"; }

need_systemd() {
  command -v systemctl >/dev/null 2>&1 || { c_err "systemctl 이 없다. 'run' 으로 직접 돌려라."; exit 1; }
}

cmd_install() {
  need_systemd
  mkdir -p "$UNIT_DIR"
  sed -e "s#__PROJECT_DIR__#$PROJECT_DIR#g" \
      -e "s#__LOOP_PATH__#$LOOP_PATH#g" \
      -e "s#__HOME__#$HOME#g" \
      "$UNIT_SRC" > "$UNIT_DST"
  systemctl --user daemon-reload
  c_ok "설치됨: $UNIT_DST"
  echo "  PATH= $LOOP_PATH"
  c_warn "등록만 됐다. 아직 켜지지 않았다. 켜려면: loop/loopctl.sh on"
}

cmd_on() {
  [ "$LOOP_ENABLE_AGENT" = "1" ] || { c_err "Agent execution disabled (LOOP_ENABLE_AGENT=0)"; exit 2; }
  need_systemd
  [ -f "$UNIT_DST" ] || cmd_install
  rm -f "$STOP_PATH"
  systemctl --user enable --now "$UNIT"
  c_ok "켜짐. 로그인하면 자동으로 시작한다."
  echo "  (로그인 없이 부팅 직후부터 돌리려면: sudo loginctl enable-linger $(id -un))"
  cmd_status
}

cmd_off() {
  need_systemd
  systemctl --user disable --now "$UNIT" 2>/dev/null
  c_ok "꺼짐. 자동 시작도 해제됐다."
}

cmd_stop() {
  : > "$STOP_PATH"
  c_ok "STOP 파일 생성: $STOP_PATH"
  echo "  현재 바퀴를 마친 뒤 멈춘다. 즉시 죽이려면: loop/loopctl.sh off"
}

cmd_resume() {
  rm -f "$STOP_PATH" && c_ok "STOP 해제. 다음 시작부터 다시 돈다."
}

cmd_status() {
  head_ "루프 상태"
  if command -v systemctl >/dev/null 2>&1 && [ -f "$UNIT_DST" ]; then
    printf '  unit      : %s\n' "$UNIT_DST"
    printf '  enabled   : %s\n' "$(systemctl --user is-enabled "$UNIT" 2>&1)"
    printf '  active    : %s\n' "$(systemctl --user is-active "$UNIT" 2>&1)"
  else
    printf '  unit      : %s\n' "(미설치 — loopctl.sh install)"
  fi
  local live
  live="$(pgrep -af "$SCRIPT_DIR/loop[.]sh" | grep -v loopctl | head -n3)"
  printf '  프로세스   : %s\n' "${live:-없음}"
  printf '  STOP 파일  : %s\n' "$([ -f "$STOP_PATH" ] && echo '있음 (다음 바퀴 안 돎)' || echo '없음')"
  printf '  바퀴 카운터: %s\n' "$(cat "$SCRIPT_DIR/.lap_counter" 2>/dev/null || echo 0)"

  # 사람이 처리해야 할 것 — 이게 쌓이면 마일스톤 경계에서 루프가 선다
  local apr="$PROJECT_DIR/docs/feedback/APPROVALS.md"
  local inb="$PROJECT_DIR/docs/feedback/INBOX.md"
  local pend=0 reject=0 todo=0
  [ -f "$apr" ] && pend=$(grep -c '^- \[ \]' "$apr" 2>/dev/null)
  [ -f "$apr" ] && reject=$(grep -c '^- \[!\]' "$apr" 2>/dev/null)
  [ -f "$inb" ] && todo=$(grep -c '^- \[ \]' "$inb" 2>/dev/null)
  if [ "$pend" -gt 0 ] || [ "$reject" -gt 0 ] || [ "$todo" -gt 0 ]; then
    head_ "사람이 볼 것"
    [ "$pend"   -gt 0 ] && c_warn "  승인 대기 : ${pend}건  → docs/feedback/APPROVALS.md"
    [ "$reject" -gt 0 ] && printf '  반려      : %s건 (루프가 처리 중)\n' "$reject"
    [ "$todo"   -gt 0 ] && printf '  INBOX 지시: %s건 (루프가 처리 중)\n' "$todo"
    [ "$pend"   -gt 0 ] && echo "  ※ 마일스톤 경계에서는 승인 대기가 빌 때까지 넘어가지 않는다"
  fi

  head_ "설정"
  if [ "$LOOP_STRATEGY_PROVIDER" = "codex" ]; then
    printf '  strategy : codex/%s effort=%s\n' "$LOOP_CODEX_ASTRA_MODEL" "$LOOP_ASTRA_EFFORT"
  else
    printf '  strategy : claude/%s effort=%s\n' "$LOOP_CLAUDE_STRATEGY_MODEL" "$LOOP_ASTRA_EFFORT"
  fi
  if [ "$LOOP_WORKER" = "codex" ]; then
    printf '  worker   : codex/%s effort=%s\n' "${LOOP_CODEX_MODEL:-$LOOP_CODEX_WORK_MODEL}" "$LOOP_WORK_EFFORT"
    if [ "$LOOP_JUDGE" = "codex" ]; then
      printf '  judge    : codex/%s (middle) effort=%s\n' "${LOOP_CODEX_JUDGE_MODEL:-$LOOP_CODEX_MIDDLE_MODEL}" "$LOOP_MIDDLE_EFFORT"
    else
      printf '  judge    : %s/%s (middle) effort=%s\n' "$LOOP_JUDGE" \
        "${LOOP_CLAUDE_JUDGE_MODEL:-$LOOP_CLAUDE_MIDDLE_MODEL}" "$LOOP_MIDDLE_EFFORT"
    fi
    printf '  middle   : %s\n' "$LOOP_MIDDLE_PROVIDER"
  else
    local turns_display="- (현재 CLI 미지원)"
    if command -v claude >/dev/null 2>&1 && claude --help 2>&1 | grep -q -- '--max-turns'; then
      turns_display="$LOOP_MAX_TURNS"
    fi
    printf '  worker   : claude/%s effort=%s max_turns=%s\n' \
      "${LOOP_MODEL:-$LOOP_CLAUDE_WORK_MODEL}" "$LOOP_WORK_EFFORT" "$turns_display"
    if [ "$LOOP_JUDGE" = "claude" ]; then
      printf '  judge    : claude/%s (middle) effort=%s\n' "${LOOP_CLAUDE_JUDGE_MODEL:-$LOOP_CLAUDE_MIDDLE_MODEL}" "$LOOP_MIDDLE_EFFORT"
    else
      printf '  judge    : codex/%s (middle) effort=%s\n' "${LOOP_CODEX_JUDGE_MODEL:-$LOOP_CODEX_MIDDLE_MODEL}" "$LOOP_MIDDLE_EFFORT"
    fi
    printf '  middle   : %s\n' "$LOOP_MIDDLE_PROVIDER"
  fi
  printf '  lap_timeout=%ss sleep=%ss max_laps=%s\n' \
    "$LOOP_LAP_TIMEOUT" "$LOOP_SLEEP_SECONDS" "$LOOP_MAX_LAPS"

  head_ "git"
  printf '  HEAD=%s  uncommitted=%s\n' \
    "$(git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo '-')" \
    "$(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null | wc -l)"

  head_ "최근 로그"
  local today="$PROJECT_DIR/$LOOP_LOG_DIR/loop-$(date +%F).log"
  if [ -f "$today" ]; then
    tail -n 12 "$today" | sed 's/^/  /'
  else
    echo "  (오늘 로그 없음: $today)"
  fi
  echo
}

cmd_logs() {
  local today="$PROJECT_DIR/$LOOP_LOG_DIR/loop-$(date +%F).log"
  if [ "${1:-}" = "-f" ]; then
    touch "$today"; tail -f "$today"
  else
    [ -f "$today" ] && tail -n 80 "$today" || echo "(오늘 로그 없음)"
  fi
}

cmd_models() {
  local strategy_model
  if [ "$LOOP_STRATEGY_PROVIDER" = "codex" ]; then
    strategy_model="codex/$LOOP_CODEX_ASTRA_MODEL"
  else
    strategy_model="claude/$LOOP_CLAUDE_STRATEGY_MODEL"
  fi
  cat <<EOF
role routing (process exit is not semantic approval):
  strategy -> ${strategy_model} effort=${LOOP_ASTRA_EFFORT}  major direction/master plan; branch/deadlock only, ~1/${LOOP_ASTRA_REVIEW_INTERVAL} laps
  middle -> ${LOOP_MIDDLE_PROVIDER}/$([ "$LOOP_MIDDLE_PROVIDER" = codex ] && printf '%s' "$LOOP_CODEX_MIDDLE_MODEL" || printf '%s' "$LOOP_CLAUDE_MIDDLE_MODEL") effort=${LOOP_MIDDLE_EFFORT}  diagnosis/plan/confirmation
  work   -> $([ "$LOOP_WORKER" = codex ] && printf 'codex/%s' "${LOOP_CODEX_MODEL:-$LOOP_CODEX_WORK_MODEL}" || printf 'claude/%s' "${LOOP_MODEL:-$LOOP_CLAUDE_WORK_MODEL}") effort=${LOOP_WORK_EFFORT}  hands-on implementation

commands: models (inspect), strategy (astra), plan (middle), review (middle), run (work), dry [role] (inspect argv)
strategy switch: LOOP_STRATEGY_PROVIDER=codex uses Astra; =claude uses Fable. No automatic fallback.
other Claude alternatives are explicit: LOOP_MIDDLE_PROVIDER=claude and/or LOOP_WORKER=claude.
EOF
}

cmd_stage() {
  local role="$1" n="${2:-$LOOP_MAX_LAPS}"
  [ "$LOOP_ENABLE_AGENT" = "1" ] || { c_err "Agent execution disabled (LOOP_ENABLE_AGENT=0)"; exit 2; }
  [[ "$n" =~ ^[0-9]+$ ]] || { c_err "invalid lap count: $n"; exit 2; }
  exec /bin/bash "$SCRIPT_DIR/loop.sh" "--role=$role" "--laps=$n"
}

cmd_run() {
  local n="${1:-$LOOP_MAX_LAPS}"
  [ "$LOOP_ENABLE_AGENT" = "1" ] || { c_err "Agent execution disabled (LOOP_ENABLE_AGENT=0)"; exit 2; }
  rm -f "$STOP_PATH"
  cmd_stage work "$n"
}

cmd_strategy() {
  cmd_stage astra "${1:-$LOOP_MAX_LAPS}"
}

cmd_dry() {
  local role=work n=1 arg="${1:-1}"
  case "$arg" in
    work|middle|astra) role="$arg" ;;
    '') ;;
    *) n="$arg" ;;
  esac
  # Dry inspection must respect STOP and never clear it as a side effect.
  exec /bin/bash "$SCRIPT_DIR/loop.sh" --dry-run "--role=$role" "--laps=$n" --sleep=1
}

cmd_uninstall() {
  need_systemd
  systemctl --user disable --now "$UNIT" 2>/dev/null
  rm -f "$UNIT_DST"
  systemctl --user daemon-reload
  c_ok "제거됨."
}

case "${1:-status}" in
  install)   cmd_install ;;
  on|start)  cmd_on ;;
  off)       cmd_off ;;
  stop)      cmd_stop ;;
  resume)    cmd_resume ;;
  status)    cmd_status ;;
  logs)      shift; cmd_logs "$@" ;;
  models)    cmd_models ;;
  strategy)  shift; cmd_strategy "$@" ;;
  plan)      shift; cmd_stage middle "${1:-$LOOP_MAX_LAPS}" ;;
  review)    shift; cmd_stage middle "${1:-$LOOP_MAX_LAPS}" ;;
  run)       shift; cmd_run "$@" ;;
  dry)       shift; cmd_dry "$@" ;;
  uninstall) cmd_uninstall ;;
  *) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
