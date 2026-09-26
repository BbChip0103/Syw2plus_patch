# 2026-09-11 lap131 — G1 owned Win32 close transport handoff

## 중간 판정

lap130의 install/final raw 분리 수리는 **MIDDLE CONFIRM PASS**다. 116행 install snapshot과
617행 final failure raw가 byte-exact로 분리되고 clean finalization 전 validator가 호출되지 않는다.
이 판정은 실제 종료 transport, overflow 없는 trace, G1 2배 출력이나 M1 승인이 아니다.

## 다음 Luna/high work 한 가지

`xdotool windowclose <XID>`를 제거하고, diagnostic trace가 기록한 Win32 PID에 속한 정확한 top-level
Win32 HWND 하나에 `WM_CLOSE`를 전달하는 bounded helper/runner 경계를 구현한다. 새 게임 runtime은
실행하지 않고 self-contained PE32 fixture로 `owned PID/HWND 확인 → WM_CLOSE → client event loop 종료 →
process exit → final marker` 순서만 증명한다.

### 허용 범위

- 로컬 diagnostic harness와 그 빌드/테스트 파일, `tools/runtime_env.py`의 close 요청 경계만 최소 수정한다.
- 기존 MinGW/Wine/Xvfb를 사용하며 새 의존성은 추가하지 않는다.
- 제품 EXE/DLL/assets, 원본·private game copy, DirectDraw bridge C, trace validator/capacity 상수,
  좌표/timeout, baseline/golden은 변경하지 않는다.
- G1 게임 명령은 실행하지 않는다. lap128 prefix/display/run도 재사용하지 않는다.

### 필수 계약과 측정식

1. runner는 install trace의 단일 양의 Win32 `pid`를 읽고 helper에 명시적으로 전달한다. Unix launcher
   PID, X11 XID, 제목 부분 일치만으로 소유권을 추정하지 않는다.
2. helper는 `EnumWindows`와 `GetWindowThreadProcessId`로 후보를 열거하고, 닫을 top-level HWND가
   정확히 하나일 때만 `PostMessageA(hwnd, WM_CLOSE, 0, 0)`를 호출한다. 0개/복수/소유 PID 불일치/
   post 실패는 후보 PID·HWND 수치와 함께 fail-closed한다.
3. helper 결과에는 요청 PID, matched HWND/thread, match count, post 결과가 기계 판독 형태로 남아야 하며
   runner evidence가 이를 보존한다. 기존 `xdotool windowclose` 호출은 production close 경로에서 0회다.
4. 격리된 새 임시 Wine prefix와 빈 Xvfb에서 self-contained PE32 target/helper fixture를 실행한다.
   다른 Wine/X11 process를 검색·종료하지 않는다. target은 자신의 PID/HWND와 WM_CLOSE 수신, 정상 event
   loop 종료, final marker를 기록하고 helper의 기록과 exact-match해야 한다.
5. negative fixture는 잘못된 PID, 0개 창, 복수 소유창 또는 PID/HWND 불일치 중 최소 세 경계를
   fail-closed로 고정하고 어떤 비소유 창에도 WM_CLOSE가 전달되지 않았음을 증명한다.
6. Python runner 회귀는 `owned Win32 close → process exit → exactly one final summary → copy → validator`
   순서를 유지하고 helper 실패 시 live `trace_raw.jsonl` 보존/validator 0회를 유지한다.

### PASS / FAIL 및 종료

- PASS: fresh out-of-tree PE32 helper/target build, 격리 fixture의 exact PID/HWND와 정상 종료/final marker,
  negative fail-closed, targeted tests, `make check`, `make doctor`, safety가 모두 PASS한다.
- FAIL: helper가 XID/제목/Unix PID만 신뢰하거나, 0/복수 후보를 임의 선택하거나, terminate/kill을 정상
  종료 증거로 쓰거나, 비소유 창에 영향을 주거나, 필수 검사가 예상 밖 실패하면 재시도하지 않는다.
- 결과는 새 Sol/high 세션이 독립 검수한다. 그 전에는 게임 runtime을 실행하지 않으며, 다음 별도 카드는
  PS3 전 overflow 2개를 숨기지 않는 lossless bounded trace capacity/aggregation 계약이다.
