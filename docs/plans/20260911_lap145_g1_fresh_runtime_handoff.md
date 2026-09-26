# 2026-09-11 lap145 — G1 fresh runtime 실무 handoff

## 중간 판정

lap144의 bridge build 실패는 source나 compiler 결함이 아니라 출력 경로 생성 순서 오류다.
`build_runtime_bridge.py`는 `out.mkdir(parents=True, exist_ok=False)`를 실행하므로 parent만 먼저
만들고 helper/bridge child는 존재하지 않은 상태로 각 builder에 전달해야 한다. lap145 확인
build는 이 절차로 RC0/PE32였고 lap143과 source manifest가 byte-equal이며 Fast 173이 PASS했다.
이것은 runtime 재실행 승인일 뿐 actual game, G1/M1 또는 사용자 승인이 아니다.

## Luna/high work 한 가지

**완전히 새 격리 환경에서 G1 presentation trace를 정확히 1회 실행해 finalization을 측정한다.**

1. 저장소 밖에 새 parent 하나만 만든다. `<parent>/helper`와 `<parent>/bridge`는 미리 만들지 않고
   아래 builder가 각각 생성하게 한다. lap144 helper와 lap145 확인 bridge를 재사용하지 않는다.
   - `python3 -m tools.win32_close_fixture build --out-dir <parent>/helper`
   - `python3 patches/population/build_runtime_bridge.py --out-dir <parent>/bridge`
   두 명령의 RC/log와 helper/target/DLL PE32, imports, source/output SHA를 기록한다.
2. 어느 build든 실패하면 재시도·source 수정·`PYTHONPATH` 우회 없이 raw를 보존하고
   `loop/ESCALATE_SOL`을 만든 뒤 종료한다. 두 build가 모두 PASS한 경우에만 다음 단계로 간다.
3. 보호 원본은 읽기 입력으로만 사용한다. `runtime_env.py prepare`로 새 전체 game copy, 새 Win32
   Wine prefix, 미사용 Xvfb display를 만들고 manifest `check`와
   `make doctor-runtime MANIFEST=<manifest>`를 순서대로 통과시킨다.
4. `runtime_env.py g1-presentation-trace --manifest <manifest> --screen 1600x1200x24 --timeout 90
   --win32-close-helper <parent>/helper/win32_close_helper.exe`를 정확히 1회 실행한다. lap136 run,
   기존 prefix/display, validator, 좌표, timeout, fixture 또는 source를 바꾸지 않는다.
5. PASS는 같은 run의 PS9→PS3/input/capture, owned PID 단일 HWND/WM_CLOSE, process exit, DLL detach,
   exactly-one final summary, dropped/overflow 0, raw byte preservation, validator PASS, owned-only
   cleanup `ok=true`를 모두 요구한다. 어느 gate든 실패하면 반복·완화하지 말고 raw/log/evidence/
   provenance/verdict/PNG와 SHA를 보존해 `loop/ESCALATE_SOL`로 넘긴다.

게임 코드, 원본/참고 저장소, 제품 EXE/DLL/assets, baseline/golden은 수정하지 않고 커밋·푸시하지 않는다.
