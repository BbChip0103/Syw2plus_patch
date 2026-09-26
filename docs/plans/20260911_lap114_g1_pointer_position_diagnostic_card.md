# lap114 work-tier card — G1 neutral-pointer automation diagnosis

## 판정과 단일 범위

Sol/high 중간 독립 검수는 lap113의 `DirectDrawCreateEx` ABI 수리를 **ACCEPT**한다. 그러나 같은
run의 PS3 capture와 complete DD→surface→actual-desc→present identity가 없으므로 runtime/G1은
**BLOCKED**다. 다음 Luna/high는 `xdotool mousemove --sync 760 40`의 불투명한 timeout을 없애되
neutral cursor가 실제 목표 좌표에 있다는 검증을 약화하지 않는 입력 하네스 수리만 수행한다.
게임/bridge/validator/좌표/timeout/원본/후보/baseline/golden은 변경하지 않는다.

## 고정 근거와 미확정 경계

- lap113 raw SHA `891f4eafeef8cccaeeee3f6f00b51431d3f87314983333622e6c2d1682ccb1f6`는
  install 2, DirectDrawCreateEx 1, CreateSurface 25, GetSurfaceDesc 29, SetDisplayMode 11,
  초기 clear형 Blt 2건을 남겼다. expected IID와 DD object는 각각
  `15E65EC0-3B9C-11D2-B92F-00609797EA5B`, `0x01E6D080`로 분리되어 ABI 수리와 일치한다.
- PS9→PS7 입력과 첫 neutral capture는 PASS했다. 그 직후 `_g1_selector_flow`의
  `lobby_selector_before` capture가 같은 `(760,40)` 이동 명령에서 10초 timeout이 났고,
  selector click·PS5·PS3·최종 validator에는 도달하지 않았다.
- installed xdotool `3.20160805.1` 도움말은 `--sync`가 포인터가 실제 움직일 때까지 기다린다고
  설명한다. 보존 evidence에는 timeout 직전/직후 실제 포인터 좌표가 없어 동일좌표 no-op,
  pointer confinement, XTest 전달 실패 중 어느 것인지 확정할 수 없다. 게임 crash로 분류하지 않는다.

## 허용 구현

1. `tools/runtime_env.py`에 private display용 bounded pointer-position helper 하나를 둔다.
   기존 xdotool 의존성만 사용해 이동 요청 전 좌표를 읽고, `mousemove` 요청 뒤
   `getmouselocation --shell`을 bounded polling하여 목표 root 좌표와 정확히 같은지 확인한다.
   시작부터 목표 좌표면 즉시 PASS다. 실패는 requested/before/last-observed/명령 결과를 포함해
   `RuntimeSafetyError`로 fail-closed한다.
2. `g1_baseline`과 `g1_presentation_trace`의 중복된 `capture_neutral`이 모두 이 helper를 사용하게
   한다. 캡처에는 기존 `cursor_content=[760,40]` 계약을 유지하고, 검증된 root 좌표 진단을
   추가할 수 있다. sleep, neutral point, screenshot crop, selector 조건은 바꾸지 않는다.
3. `tests/test_runtime_env.py`에 최소 회귀를 추가한다: 이미 목표 좌표, 한 번 이동 뒤 목표 도달,
   끝까지 좌표 불일치, malformed/failed query. unit test는 Xvfb/Wine을 시작하지 않는다.

## 검증과 stop condition

1. 시작 SHA를 확인한다: `tools/runtime_env.py=c417b9f0a60d7a0ef422657534f90ce51796173d3f8781a365ae71e070a7bfa1`,
   `tests/test_runtime_env.py=ab344efc0925ac8a67de4ea9bf8292c4c37cf82cc65e22a342ee341d5492ea6b`.
2. 새 helper targeted tests, 전체 `make check`, `make doctor`, `bash checks/safety.sh check`가 모두
   PASS해야 한다. 하나라도 예상 밖 실패하면 재시도하지 말고 변경/로그/SHA를 보존해
   `loop/ESCALATE_SOL`로 돌려보낸다.
3. 위 게이트가 모두 PASS한 뒤에만 새 whole game copy/new Win32 prefix/unused display에서
   기존 90초 `g1-presentation-trace`를 정확히 1회 실행한다. lap113 run/prefix는 재사용하지 않는다.
4. runtime PASS는 exact neutral pointer proof, PS9→PS3, expected IID→DD→surface→actual desc→
   non-clear present identity, 같은 run PS3 capture, final summary, cleanup `ok=true`가 전부 필요하다.
   실패하면 재시도·좌표/timeout 완화 없이 raw/game log/evidence/SHA를 보존하고 승격한다.
5. 성공해도 다음 새 Sol/high 독립 컨펌 및 사용자 마일스톤 판단 전 G1/M1 PASS가 아니다.
