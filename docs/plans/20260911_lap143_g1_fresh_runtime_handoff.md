# 2026-09-11 lap143 — G1 fresh runtime 재개 handoff

## 중간 판정

lap142의 close-helper 실패는 helper source/MinGW 결함이 아니라 Python 호출 경계 오류다.
`python3 tools/win32_close_fixture.py ...`는 script directory만 import path 선두에 두어
`tools.win32_close_transport`를 찾지 못하지만, 저장소 루트에서 아래 모듈 실행은 fresh PE32
helper/target을 생성한다.

```sh
python3 -m tools.win32_close_fixture build --out-dir <fresh-empty-out-dir>
```

lap133과 동일한 네 source SHA, helper의 KERNEL32/USER32-only import, fresh fixture의 positive
단일 PID/HWND/WM_CLOSE/exit와 wrong PID·0창·복수창 fail-closed, targeted 14와 Fast 173을 확인했다.
fresh diagnostic bridge도 PE32로 빌드됐다. 이 판정은 actual game runtime이나 G1/M1 PASS가 아니다.

## Luna/high work 한 가지

**새 격리 환경에서 수리된 G1 presentation trace를 정확히 1회 실행해 finalization을 측정한다.**

1. 저장소 밖 서로 다른 새 빈 디렉터리에 helper/target은 위 모듈 명령으로, diagnostic bridge는
   `python3 patches/population/build_runtime_bridge.py --out-dir <fresh-bridge-dir>`로 빌드한다.
   각각 PE32, import, source/output SHA를 기록하며 lap142/lap143 산출물을 재사용하지 않는다.
2. 보호 원본은 읽기 입력으로만 사용한다. `runtime_env.py prepare`로 새 전체 game copy, 새 Win32
   Wine prefix, 미사용 Xvfb display를 만들고 manifest `check`와
   `make doctor-runtime MANIFEST=<manifest>`를 먼저 통과시킨다.
3. `runtime_env.py g1-presentation-trace --manifest <manifest> --screen 1600x1200x24 --timeout 90
   --win32-close-helper <fresh-helper>`를 정확히 1회 실행한다. lap136 run/prefix/display, validator,
   좌표, timeout, fixture 또는 source를 바꾸지 않는다.
4. PASS는 같은 run의 PS9→PS3/input/capture, owned PID 단일 HWND/WM_CLOSE, process exit, DLL detach,
   exactly-one final summary, dropped/overflow 0, raw byte preservation, validator PASS, owned-only
   cleanup `ok=true`를 모두 요구한다.
5. prepare/check/doctor-runtime/runtime/cleanup 중 하나라도 실패하면 재시도·완화하지 않는다.
   raw/log/evidence/provenance/verdict/PNG와 SHA를 보존하고 `loop/ESCALATE_SOL`로 넘긴다. PASS여도
   새 middle-tier 독립 검수와 사용자 판단 전 G1/M1로 승격하지 않는다.

게임 코드, 원본/참고 저장소, 제품 EXE/DLL/assets, baseline/golden은 수정하지 않고 커밋·푸시하지 않는다.
