# 2026-09-11 lap129 — G1 trace finalization/recovery handoff

## 중간 판정

lap128의 fresh runtime 실패는 **RUNTIME BLOCK CONFIRMED / TRACE CONTRACT REVISE /
GAME RUN BLOCKED**다. 제품 EXE/DLL/assets나 G1 후보의 실패가 아니라 diagnostic runner/bridge의
종료·증거 보존 계약이 실제 Wine 경계를 통과하지 못했다. 같은 run/prefix/display 재실행은 금지한다.

## 독립 근거와 원인 순위

1. **High — 정상 종료 요청이 증명되지 않았다.** `tools/runtime_env.py:842-885`는
   `xdotool windowclose <XID>`를 Win32 `WM_DELETE_WINDOW` 요청이라고 설명하지만 설치된 xdotool
   문서는 이 명령이 X window를 destroy하되 client를 kill하지 않는다고 명시한다. 실제 lap128은
   명령 성공 뒤에도 `proc.poll() is None`으로 90초까지 살아 있었다. bridge summary는
   `tools/inmm_stub/inmm_stub.c:552-553`의 `DLL_PROCESS_DETACH`에서만
   `g1_direct_draw_trace_detach()`를 호출해 생성되므로, process 미종료와 summary 0은 같은 경계다.
   고정 원본 WndProc `0x00423DC0`는 WM_CLOSE를 default `DefWindowProcA` IAT `0x004E5208`로 보내고,
   WM_DESTROY 분기는 `PostQuitMessage` IAT `0x004E51FC`를 호출한다. 따라서 원본 종료 분기는 있으나
   현재 X11 명령이 그 Win32 분기를 호출했다는 증거가 없다.
2. **High — output raw 116과 live 617은 서로 다른 시점이다.** install gate가
   `tools/runtime_env.py:783-812`에서 `trace_raw.jsonl`을 116행 시점에 먼저 쓰고, 실패 보존은
   `:888-892`에서 목적 파일이 없을 때만 복사한다. 보존 prefix의 live trace는 617행/SHA256
   `b105fc3452dc1650aab58cd7c66aa79e97656964a121ab18d80713f6469d8539`이며 output raw는 그
   첫 116행과 byte-for-byte 일치한다. 따라서 lap128의 raw SHA는 최종 실패 trace SHA가 아니다.
3. **High — clean exit만 고쳐도 validator는 PASS하지 않는다.** live 617행을 같은 capture로 새로
   검증하면 schema error는 0이고 capture는 true지만, `surface_release=256`, `blt_fast=256`,
   overflow event 2개(seq453/454)라 `trace contains overflow`와 final summary 누락으로 BLOCKED다.
   첫 overflow는 PS7에서 발생해 PS3 도달 전 이미 현재 `method_limit=256`이 소진됐다.
4. **High — 현재 회귀는 실제 close transport를 증명하지 않는다.** `tests/test_runtime_env.py:218-355`
   는 summary가 이미 있고 process가 이미 종료된 fixture 또는 mocked `subprocess.run`을 사용한다.
   close 뒤 실제 client exit/DLL detach가 발생하는지와 growing trace의 최종 raw 보존은 실행하지 않는다.

## 다음 Luna/high work 한 가지

implementation-unchanged-streak가 이번 문서-only lap으로 2가 되므로 다음은 서술 추가가 아니라
**growing trace의 install snapshot과 최종 failure raw를 분리 보존하는 최소 코드/회귀 수리**다.

- 허용 파일: `tools/runtime_env.py`, `tests/test_runtime_env.py` 최소 집합. 게임/원본/후보 EXE/DLL,
  bridge C, validator 상수, 좌표, timeout, fixture, baseline/golden은 변경하지 않는다.
- install gate snapshot은 별도 이름(예: `trace_install.jsonl`)과 SHA로 보존한다.
  finalization 실패 시에는 그 시점의 live trace exact bytes를 `trace_raw.jsonl`에 반드시 보존하고,
  기존 install snapshot 때문에 복사를 건너뛰지 않는다. source가 없거나 read 자체가 실패하면 빈 파일로
  기존 근거를 덮지 말고 오류와 두 경로 상태를 남긴다.
- 직접 회귀는 trace가 116행 install snapshot 뒤 617행으로 자란 fixture에서 finalization 실패를
  발생시켜 install snapshot=116, final raw=617, validator 미호출을 증명한다. final raw copy 실패도
  fail-closed하며 이전 snapshot을 최종 raw라고 표시하지 않아야 한다.
- targeted runtime tests, `make check`, `make doctor`, `bash checks/safety.sh check`를 실행한다.
  새 게임/runtime/PNG는 실행하지 않는다. 예상 밖 실패는 변경·로그·SHA와 함께 다시 승격한다.

## 후속 blocker와 runtime 재개 조건

raw 보존 수리의 새 Sol/high 독립 확인 뒤에도 runtime은 금지한다. 그 다음 별도 middle/work 카드는
(a) exact owned Win32 HWND/PID를 확인하고 WM_CLOSE→process exit→DLL detach를 bounded하게 증명하는
종료 transport, (b) PS3 전 overflow를 숨기거나 임의 상수 확대하지 않고 필요한 provenance를
loss 없이 담는 bounded trace 용량/집계 계약을 각각 정해야 한다. 최종 fresh runtime은 두 계약의
native/runner 회귀와 새 middle 확인 뒤 정확히 1회만 허용하며, final live raw·summary 1개·overflow 0·
validator PASS·cleanup PASS를 모두 요구한다.
