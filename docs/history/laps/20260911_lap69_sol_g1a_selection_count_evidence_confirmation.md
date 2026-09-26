# 2026-09-11 | lap 69 | 목표 G1-A selection count evidence 독립 검수

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier / diagnosis·plan·confirmation. 현재 세션 표면은 실제 provider/model ID/effort를 노출하지 않으므로 `gpt-5.6-sol` 실행으로 주장하지 않는다.
- 가설 / 사용자 관찰: lap68 work가 selection count DWORD를 identity 상세 read보다 먼저 분리해 count0/count2 모두 primary table과 selection detail을 읽기 전에 증거를 보존해 거부한다면 lap67 반려를 해소하고 제한된 game-run probe를 work tier에 넘길 수 있다.
- 예상 PASS / FAIL 조건: source/original SHA와 원본 count dispatch/old bytes가 일치하고, count0/count2가 각각 `required=1`, 관측 count, `before={count}`, `primary_read=false`를 보존한 non-retryable 거부이며 selection detail/primary read가 없어야 한다. count1, `1→2`, raw-change, stable-ineligible 회귀와 targeted/Fast/safety/doctor가 모두 새로 PASS해야 한다. 하나라도 실패·충돌하면 구현 없이 `loop/ESCALATE_SOL`에 후속 검증을 남기고 종료한다.
- 필요한 입력: lap68 source/test SHA, 고정 원본/private EXE SHA, `0x00498FBA` count0/count1/count&gt;1 dispatch 및 count1 전용 primary fill old bytes, count0/count2 직접 fixture call/evidence, 관련 targeted/Fast/safety/doctor 출력.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/helper/tests/binary/좌표/timeout/fixture 변경 없음. 판정 문서 `docs/STATUS.md`, `docs/work/active/G1_A_EXECUTION_CARD.md`, `analysis/memory_maps/player_offsets.md`, 본 이력만 갱신하고 기존 marker는 아래 원문 보존 후 제거한다. 검수 source SHA는 `tools/runtime_env.py=815e90e2e2ffe342eb24ad64135c7be802848a6197bb4ec766b53c023970bbad`, `tests/test_runtime_env.py=cc30931e4279ac25310eefa8c443cf260df4d21ffc1a147a3fcc78115d4dc5ad`, `tests/test_runtime_guards.py=93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`다. Git unborn/uncommitted, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본, 개인 입력 원본, lap60 private EXE SHA가 모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`다. 후보 EXE, 새 Wine/Xvfb/game run, 활성 인원/지도/군대는 없음. targeted와 직접 probe는 synthetic memory fixture다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `file`, `objdump -d -Mintel --start-address/--stop-address`, `objdump -s`, 독립 `.venv/bin/python` count0/count2 probe, `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py`, `make check`, `bash checks/safety.sh check`, `make doctor`를 실행했다. 첫 SHA 명령은 잘못 중복한 `../Syw2plus/Syw2plus/...` 경로로 뒤 명령 실행 전에 exit1하여 측정에서 제외하고 정확한 경로로 즉시 정정했다. 새 로그/PNG/runtime 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 원본 `0x498FBA`에서 count0→`0x498FC3`, count1→`0x498FDB` 및 `0x499201..0x49929E` fill, count&gt;1→`0x499336`, 공통 `0x499583` consumer와 writer old bytes가 일치했다. 독립 count0/count2 probe는 각각 calls=`[(0x00899024,4)]`, `retryable=false`, required/observed/before/primary_read evidence, `primary_snapshot=null`을 확인했다. targeted **54 passed**, 전체 **124 passed**, Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**, doctor `ok=true`/original verified다. lap68 count 수리는 **MIDDLE CONFIRM PASS**다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: game-run 허용은 보류한다. `g1-baseline` catch가 stable-ineligible 예외의 `primary_snapshot`을 output에 복사하지 않고, eligible이면 primary field/action·worker mapping이 UNKNOWN인데도 hard-coded `(670,490)` production click으로 진행한다. 실제 1600×1200 출력/입력/생산/drag/minimap, G2~G4, 제품/사용자 승인은 미완료다. binary patch/restore는 N/A다.
- 다음 한 가지: 새 Luna/Sonnet5/high work가 `tools/runtime_env.py`와 관련 runtime tests만 최소 수정해 예외 primary snapshot을 결과에 보존하고, 의미 연결 승인 전 eligible도 production click을 호출하지 않는 fail-closed gate와 두 직접 회귀를 추가한다. targeted/Fast/safety/doctor 뒤 새 middle 확인 전 game run은 금지한다.

## 소진 전 `loop/ESCALATE_SOL` 원문

제거 전 SHA256: `d3179fa8603100c94adb3209101c2e89ffeda4353e77744938d802f078b2f893`.

```text
# lap67 승격 요청 — count=0 evidence 계약 누락

## 사유

lap66 source SHA, 고정 원본/private SHA와 count dispatch, targeted 52 PASS는 독립 재현됐다.
그러나 count=0 비변경 probe에서 helper는 primary table을 읽지 않은 채 거부하면서도
`_CommandCellSnapshotError("unsupported selected-unit count: 0")`, `branch_evidence=null`을 반환했다.
lap65가 승인한 모든 before count!=1의 관측 count evidence 보존 계약과 충돌하므로 예상 밖 필수
확인 실패로 중단했다. full Fast/safety/doctor와 game run은 실행하지 않았다.

## 승격 작업자가 이어서 검증할 것

1. `tools/runtime_env.py`의 `_read_g1_command_selection_identity`가 count 유효범위를 먼저 거부해
   `_read_g1_command_cell_provenance_once`의 exact-count guard에 count0이 도달하지 못한다는 진단을
   독립 확인한다. middle 역할은 직접 구현하지 않는다.
2. work-tier handoff는 selection count DWORD를 identity slot/unit reads와 분리하고, 모든 count!=1을
   `required=1`, `observed`, `before={count}`, `primary_read=false`와 함께 non-retryable 거부하도록
   `tools/runtime_env.py`와 관련 tests만 최소 수리하는 범위다. count0/count2 직접 회귀를 모두 요구한다.
3. count1의 phase당 단일 96-byte read, `1→2`, raw-change, stable-ineligible evidence를 유지하고
   targeted/Fast/safety를 새로 통과시킨 뒤 별도 middle 재검수 전 game run을 계속 금지한다.

## 보존된 근거

- original/private EXE SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- source SHA: `tools/runtime_env.py=fb19ae214f2d57f285d061019217ed618e3a200727e94ec94f44cb6fb01e464c`,
  `tests/test_runtime_env.py=c2b8ff3a1d59d779d8ceee79e03896896eadcb61da67ab3d11d7efa3ef7436fb`,
  `tests/test_runtime_guards.py=93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`.
- fresh targeted: **52 passed**. count0 probe: calls=`[(0x00899024,4)]`, primary_read=false,
  branch_evidence=null, primary_snapshot=null. 제품 G1~G4 및 사용자 승인은 모두 미완료다.

## lap68 work 처리 결과

위 승격 범위는 hands-on work에서 최소 수리되었다. selection count를 identity 상세 read와
분리해 count0/count2를 `required=1`, `observed`, `before={count}`, `primary_read=false`로
보존하는 회귀를 추가했다. source SHA는 `tools/runtime_env.py=815e90e2e2ffe342eb24ad64135c7be802848a6197bb4ec766b53c023970bbad`,
`tests/test_runtime_env.py=cc30931e4279ac25310eefa8c443cf260df4d21ffc1a147a3fcc78115d4dc5ad`다.
targeted **54 passed**, `make check` **124 passed**, Ruff/compileall/mypy/context/safety PASS,
doctor original verified다. 다음은 새 Sol/Opus5 middle 독립 검수이며, 그 전까지 game run은 계속
금지한다. 기존 lap67 반려 근거는 삭제하지 않는다.
```
