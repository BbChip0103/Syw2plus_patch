# G1 W50RX — W50R bounded harness exception 정확히 1회 (lap602 strategy 판정, 2026-09-25 KST)

- 발행: lap602 strategy. 실제 모델은 Claude Code `claude-opus-5-5`(effort 세션 비노출)이며 계약 모델 Fable/Astra를 대신한다. 게임 실행0, 제품/하네스 source·binary·raw 변경0, 커밋0.
- 근거: `loop/ESCALATE_SOL` §150·§151, W50R 카드 `docs/work/active/G1_STRATEGY_W50R_INNER_SLOT_AUDIT_LAP599.md` §3~§6, W50 카드 `docs/work/active/G1_STRATEGY_W50_HD_FINAL_OUTPUT_ACQUISITION_LAP596.md` §5~§6, 이 회차 독립 확인(§2).
- 수행 역할: **work**(Sonnet5 또는 Luna, high). 계획 회차를 끼우지 않는다. 그다음 middle이 독립 검수한다.

## 1. 판정

§151의 선택지 중 **(A) bounded harness exception 정확히 1회**를 택한다. W50R 카드 §3 실행 계약과 §4 R1~R4 분류는 **그대로** 쓴다. 이 카드는 실행 표면만 고정한다.

이유:
1. lap600의 두 명령은 모두 게임을 띄우지 못했다(evidence elapsed `0.042s`, `display=""`, screenshots/inputs 0). 따라서 소비된 제품 관측은 0이다. W50 fresh 예산 3회 중 3번째(W50R)는 아직 한 번도 관측하지 못했다.
2. 원인은 코드 결함이 아니라 인터프리터 선택이다. system `python3` direct-script 표면에서만 `patches` import가 실패하고, 승인된 `.venv` 표면에서는 성공한다(§2). 그래서 source 수정이 필요 없다. 이 점이 runner 코드 결함(`TypeError`)을 고쳐야 했던 W49SC 예외(lap594/595)와 다르다.
3. 구현은 lap601에서 정적 ACCEPT됐다(C `24a2ef66…d531`, test `684f4893…8241`, bridge `75c918b9…8fd0`, 이번 회차에도 SHA 일치). 실행 비용은 게임 ≤15분이다. R1/R2/R3 중 하나만 나와도 G1 acquisition 분기의 결론이 정해진다.
4. 제품/실행 증거가 늘지 않은 회차가 lap601·lap602로 2회 연속이다(PROMPT ③). (B)를 고르면 G1 대안 카드를 쓰는 계획 회차가 또 필요하다. 그러면 세 번째 무증거 회차가 된다.

## 2. strategy 독립 확인 (이 회차, 읽기/import smoke만)

- `logs/laps/2026-09-25/lap-0600.log` 13170행: 실패 명령은 `INMM_FINAL_D3D9_TRACE=1 INMM_FINAL_D3D9_AUDIT_ONLY=1 INMM_FINAL_D3D9_WINE_REBASED_HEADER=1 python3 tools/runtime_env.py g1-presentation-trace …`이다. 13428행: 후속 `.venv/bin/python -m tools.runtime_env …`에는 audit env가 없다. §151 provenance 판정과 일치한다.
- `runtime_env.py:7945`는 `--dxwrapper-2x`일 때의 지연 import `from patches.resolution import dxwrapper_config`다.
- system `python3 -c "import patches"` → `ModuleNotFoundError`. `.venv/bin/python`은 cwd `/tmp`에서 `sys.path[0]=tools`로 script 모드를 흉내 내도 `patches/resolution/dxwrapper_config.py`를 import한다(editable `.pth`가 있다).
- lap597 A1/A3가 실제로 성공한 표면은 `PYTHONPATH=. .venv/bin/python tools/runtime_env.py prepare …` / `… g1-presentation-trace …`였다(lap-0597.log). 이번 카드는 이 표면을 고정한다.

## 3. W50RX 실행 표면 (고정, 변경 금지)

| 단계 | 내용 | 불성립 시 |
|---|---|---|
| G-a SHA | C `24a2ef669d5b3bef29cc39d5332d3dac880b412aa35923e686997ccc776cd531`, test `684f4893506c527dc97140dd565018208377f2640b7abd621fa1d4857ddb8241`, bridge `tools/inmm_stub/_inmm.dll` `75c918b96e692bbedcf479eb03d142c41460edc278f90316651f66e100428fd0`, 원본 EXE `b56986e0…a8ac`, DxWrapper `96c44319…e8fe`, ini `918e7043…a5a2` | 시작하지 않음 |
| G-b import smoke | 같은 셸에서 `PYTHONPATH=. .venv/bin/python -c "from patches.resolution import dxwrapper_config"` exit0 **그리고** `PYTHONPATH=. .venv/bin/python tools/runtime_env.py --help` exit0 | 시작하지 않음 |
| G-c 새 private | 새 `mktemp -d` 작업 폴더와 새 runtime root(예: `local/runtime/w50rx_lap603/`)에 `PYTHONPATH=. .venv/bin/python tools/runtime_env.py prepare --source <원본 Syw2plus> --runtime-root <새 root> --bridge <G-a bridge> --timeout 60`. manifest/prefix/output/display 모두 미사용. lap600 `local/runtime/w50r_lap600_runtime_final/`은 **보존만** 하고 읽기 외 접근 금지 | 시작하지 않음 |
| G-d close helper | 새 작업 폴더에 `PYTHONPATH=. python3 tools/win32_close_fixture.py build --out-dir <새 close 폴더>`로 만들고 SHA를 기록한다 | 시작하지 않음 |
| G-e env receipt | 실행과 **같은** `bash -lc` 안에서 `env \| grep '^INMM_'` 출력을 파일로 남긴다. 정확히 `INMM_FINAL_D3D9_TRACE=1`, `INMM_FINAL_D3D9_AUDIT_ONLY=1`, `INMM_FINAL_D3D9_WINE_REBASED_HEADER=1`만 있고 `INMM_FINAL_D3D9_CACHE_CAS`는 없어야 한다 | 시작하지 않음 |
| 실행 | `INMM_FINAL_D3D9_TRACE=1 INMM_FINAL_D3D9_AUDIT_ONLY=1 INMM_FINAL_D3D9_WINE_REBASED_HEADER=1 PYTHONPATH=. .venv/bin/python tools/runtime_env.py g1-presentation-trace --manifest <G-c manifest> --screen 1600x1200x24 --timeout 90 --win32-close-helper <G-d helper> --dxwrapper-2x`, **동기 foreground 정확히 1회**, 게임 ≤15분, 회차 ≤60분 | — |

- G-a~G-e 중 하나라도 불성립하면 게임을 띄우지 않는다. 그 사실만 기록하고 middle로 넘긴다. 이 경우는 예외 사용으로 치지 않지만, 표면 수리는 이 카드 범위 밖이다.
- 시간이 60분 안에 끝나지 않을 것 같으면 시작하지 않고 기록한다(PROMPT ③ 장기 실행 규칙). background 실행 금지.
- 보존·분류·금지는 W50R 카드 §3 표의 "보존" 행과 §4·§6을 그대로 따른다. PS3 캡처 1장은 공유 temp `captures/`에 `YYYYMMDD_HHMMSS_` 접두사로 둔다.

## 4. 결과별 다음 (실행 전 고정, 재승격 없음)

- **R1/R2:** middle이 raw로 재계산해 ACCEPT하면 W50R 카드 §5의 사전 허가 W50S(1회)로 간다.
- **R3:** acquisition 분기를 `BLOCKED(acquisition:inner_not_native)`로 닫는다.
- **R4(어떤 원인이든):** 이것이 W50R의 **최종 예외**다. 다시 예외를 열지 않고 `BLOCKED(harness)`로 닫는다. strategy에 재승격하지 않는다.
- **R3/R4에서 방향(lap602 strategy 사전 결정, 번복 가능):** G1을 계속하고 W50 카드 §6의 **대안 경로**(native 1600 표면에서 게임 blit을 2배로 그리는 방식)로 간다. middle이 그 경로의 최초 가능성 조사 work 카드 1장(≤60분 또는 실패 가설 2회 뒤 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`)을 W50 §5 금지 범위 안에서 발행한다. strategy 회차를 끼우지 않는다. G4는 그 대안 경로 판정까지 계속 보류한다. 대안 경로도 `NOT_FEASIBLE`/`BLOCKED`이면 그때 strategy가 G1 종료 또는 G4 전환을 판정한다.

## 5. 금지

W50 카드 §5와 W50R 카드 §6의 금지를 전부 유지한다. 추가로 다음을 금지한다.
- lap600 run/prefix/output을 재사용하거나 삭제하는 것.
- system `python3`로 `runtime_env.py`를 실행하는 것. G-d의 fixture build만 예외다.
- `-m tools.runtime_env` 표면을 쓰는 것.
- C/test/bridge를 수정하거나 다시 빌드하는 것. G-a SHA가 바뀌면 시작하지 않는다.
- 두 번째 fresh 실행.
- R 분류를 바꾸는 것.
- G1 PASS 주장, 사용자 승인 대리, 커밋.
