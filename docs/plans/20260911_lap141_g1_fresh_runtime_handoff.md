# 2026-09-11 lap141 — G1 serializer 확인 후 fresh runtime handoff

## 중간 판정

lap140의 evidence-only 수리는 **MIDDLE CONFIRM PASS**다. 변경된 fixture/test SHA가 기록과
일치하고, production-format prefix에 95-byte run_id를 실제 조합한 native fixture가 prefix
298 bytes, JSONL 1103 bytes, strict JSON/NUL0/one-line/`}\n`을 재현했다. production writer는
serialize와 exact single write/flush 성공 뒤에만 event count를 올리며, 두 순서 mutation은
회귀에서 거부된다. targeted 12, Fast 173, fresh PE32/no-CRT import, doctor/safety가 PASS했다.

이 판정은 actual Wine runtime, final summary, process exit/DLL detach, 1600x1200 2배 출력 또는
G1/M1 완료가 아니다.

## Luna/high work 한 가지

**새 격리 환경에서 수리된 G1 presentation trace를 정확히 1회 실행해 finalization을 측정한다.**

1. 저장소 밖 새 디렉터리에서 diagnostic bridge와 Win32 close helper를 fresh build하고 PE32,
   import, source/DLL SHA를 기록한다. 제품 EXE/DLL/assets와 저장소 산출물은 수정하지 않는다.
2. 보호 원본 전체 게임은 읽기 입력으로만 사용한다. `runtime_env.py prepare`로 새 전체 game copy,
   새 Win32 Wine prefix, 사용하지 않은 Xvfb display를 만들고 새 manifest의 `check`와
   `make doctor-runtime MANIFEST=<manifest>`를 먼저 통과시킨다.
3. `runtime_env.py g1-presentation-trace --manifest <manifest> --screen 1600x1200x24 --timeout 90
   --win32-close-helper <fresh-helper>`를 정확히 1회 실행한다. lap136 run/prefix/display를 재사용하거나
   좌표·timeout·validator·fixture·source를 바꾸지 않는다.
4. PASS 조건은 PS9→PS3/input/capture, owned PID의 단일 HWND/WM_CLOSE, process exit, DLL detach,
   exactly-one final summary, dropped/overflow 0, raw byte preservation, validator PASS, owned-only
   cleanup `ok=true`가 모두 같은 run에서 확인되는 것이다.
5. prepare/check/doctor-runtime/runtime/cleanup 중 하나라도 실패하면 같은 lap에서 재시도하거나
   완화하지 않는다. raw/log/evidence/provenance/verdict/PNG와 SHA를 보존하고 `loop/ESCALATE_SOL`로
   새 중간 tier에 넘긴다. PASS여도 다음 새 Sol/high 독립 검수와 사용자 판단 전 G1/M1로 승격하지 않는다.

게임 코드, 원본/참고 저장소, baseline/golden은 수정하지 않고 커밋·푸시하지 않는다.
