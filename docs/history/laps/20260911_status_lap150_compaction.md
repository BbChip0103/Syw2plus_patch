# STATUS pre-compaction snapshot — lap 150

Opus 입력 좌표 계약 검수 직후, 안전 상한 초과를 복구하기 전에 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `9cd56fef4d7ad75c961a96d0ad87e58e070554ad40d400969657c2a5f9bfb39c`
- line count: `186`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

2026-09-11 lap149 middle-tier(Opus5) 독립 검수는 lap148 증거 해시 5/5, 적용 config byte 대조,
원복/pin 4/4를 모두 재계산해 일치시켰다. raw trace는 게임 논리 surface가 800×600으로 불변인 채
1600×1200 client에 letterbox 없이 2.0×2.0으로 표시됐음을 보이고, PS9에서 `blt_fast` 256건이
끝까지 기록돼 렌더 루프는 살아 있었다. lap146(PASS)과 lap148(BLOCKED)은 둘 다 게임 창이 root
원점·border 0이라 root=client 좌표가 항등이며, 입력 경로의 차이는 **좌표 ×2 선변환 하나뿐**이다.
wrapper가 역변환하지 않으면 게임은 범위 밖 y=1120을, 역변환하면 이중 변환으로 (92,280)을 보므로
어느 해석이든 선변환이 틀렸다. 판정은 **MIDDLE CONFIRM PASS / FAST SKIP / DIRECTION=입력 좌표
계약 수리**다. 프로필 폐기와 Astra 상위 분기는 불필요하다. 결선 단절 지점 자체는 bridge에 입력
관측이 0건이라 **UNKNOWN**으로 남긴다. 처리한 `loop/ESCALATE_SOL`은 원문을 lap149 이력에 보존 후
제거했다. 제품 G1 승인 아님.

2026-09-11 lap148 Luna/high는 pinned `ddraw.dll`/`dxwrapper.dll`만 사용한 fresh private
config-only 정수2배 후보를 만들었다. config old `918e7043...a5a2`에서 `LoadCustomDllPath`
공백, integer scaling/aspect 1을 적용한 후보 `f0ce9e64...6785`는 exact old/new,
unsupported hash, distinct output, tamper 거부와 byte-exact restore를 통과했다. 새 copy/prefix/
display에서 root/client 1600×1200와 2.0×2.0은 관측했지만 scaled menu click 뒤 PS9에 머물러
PS7/PS3에 도달하지 못했다. runtime 후보는 **BLOCKED**, cleanup owned-only는 PASS이며
`loop/ESCALATE_SOL`에 raw trace/log 독립 검수 항목을 남겼다. 제품 G1 승인 아님.

2026-09-11 사용자 지시에 따라 실무는 Luna/high, 중간 계획·컨펌과 judge는 Opus5/high,
Astra는 medium 기본으로 변경했다. Astra는 큰 분기·반복 교착에서만 필요 시 high로 올리며,
정기 자동 호출 없이 대략 10개 work/middle lap당 1회 이하를 운영 기준으로 삼는다.

2026-09-11 lap147 middle-tier 독립 검수는 lap146 final hash 목록과 build source manifest
28/28, 원본/private EXE, helper/target/bridge PE32, 5 PNG를 재계산해 모두 일치시켰다. 단일
run/PID의 owned HWND close→process exit0→마지막 summary 1개, detach/flush, raw byte-equal,
651 events/dropped0/overflow0/집계 산술, cleanup과 standalone validator를 재확인했고 Fast 173도
PASS했다. 판정은 **MIDDLE CONFIRM PASS / DIAGNOSTIC RUNTIME·FINALIZATION READY**다. root만
1600×1200이고 실제 content/capture는 800×600이므로 제품 G1·M1·사람 승인은 여전히 미완료다.

2026-09-11 lap146 Luna/high fresh runtime은 새 helper/bridge/game copy/prefix/display에서
G1 presentation trace를 정확히 1회 실행했다. helper/bridge build, prepare/check/doctor-runtime,
`make check` 173, safety가 PASS했고, 같은 run의 PS9→PS3/input/capture, 단일 owned PID/HWND
WM_CLOSE, process exit, DLL detach, summary 1개, dropped/overflow 0, raw byte 보존, validator,
owned-only cleanup이 모두 PASS했다. 이것은 **MIDDLE 재검수 대기용 진단 runtime PASS**이며 제품
G1 승인이나 1600×1200 제품 패치가 아니다. 실제 content/capture는 여전히 800×600이다.

2026-09-11 lap145 middle-tier 독립 검수는 lap144의 bridge 실패 로그·helper/target SHA·원본
SHA를 재확인하고, 실패가 builder의 `exist_ok=False` 계약과 충돌한 호출 절차 때문임을 확인했다.
새 `/tmp` parent 아래 **존재하지 않는** bridge child를 전달한 확인 build는 RC0/PE32였고
lap143과 source manifest가 byte-equal이며 Fast 173도 PASS했다. **MIDDLE CONFIRM PASS / RETRY
AUTHORIZED**로 판정하고 처리된 `loop/ESCALATE_SOL`은 lap145 이력에 원문 보존 후 제거했다.
실제 game runtime/PNG/final summary/process exit/DLL detach/validator는 이번 lap에서 SKIP이다.

2026-09-11 lap143 사용자 지정 middle-tier 독립 검수는 lap142의 close-helper 실패를 같은
직접 실행 명령에서 RC1/동일 `ModuleNotFoundError`로 재현했다. 원인은 파일 직접 실행 시
저장소 루트가 Python import path에서 빠지는 호출 경계이며, source 수정 없이
`python3 -m tools.win32_close_fixture build`로 fresh helper/target PE32를 생성했다. helper
positive/세 negative fixture, targeted 14, Fast 173이 PASS했고 fresh bridge도 PE32로 확인해
**MIDDLE CONFIRM PASS / FRESH RUNTIME READY**로 판정한다. 실제 model ID/effort attestation은
현재 표면에서 확인할 수 없어 추정하지 않으며, 제품 G1~G4 판정은 변하지 않는다.

2026-09-11 lap141 Sol/high 독립 검수는 95-byte run_id native fixture, bounded serializer,
production write/failure 순서 mutation, targeted 12, Fast 173, fresh PE32/no-CRT import,
doctor/safety를 모두 재현해 **MIDDLE CONFIRM PASS / FRESH RUNTIME READY**로 판정했다.
이것은 진단 하네스 승인이지 G1/M1 제품 승인이 아니다.

직전 lap136 실제 trace는 PS9→PS3, input/capture, owned Win32 PID/HWND WM_CLOSE, cleanup까지
관측했지만 summary가 `wsprintfA` 1024-byte 한계에서 NUL로 잘려 BLOCKED였다. lap138 serializer
수리와 lap140 증거 보강은 이 원인을 native 회귀로 고정했고 두 차례 middle 검수를 통과했다.
현재 제품 화면은 여전히 원본 800×600 content이며 1600×1200 제품 패치는 없다.

| 목표 | 판정 | 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | lap149 검수로 config-only 후보의 **표시층 2배**(논리 800×600 불변 → client 1600×1200, scale 2.0)는 관측됐으나 입력 게이트 BLOCKED로 플레이 가능 증거·사람 승인 없음 |
| G2 8인 전비5000 안정성 | 미완료 | 8인 부하·유닛 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 상태/로비/통신/시뮬레이션 검증 없음 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

work tier가 `docs/work/active/G1_INPUT_COORDINATE_CONTRACT_HANDOFF.md`대로 `tools/runtime_env.py`
`g1-presentation-trace`의 입력 좌표 계약을 1개 변경으로 수리한다: client 크기를 800×600/1600×1200만
허용하도록 완화하되 **논리 구성 800×600 단정은 trace 기반으로 유지·강화**하고, 클릭은 선변환 없이
논리좌표 (184,560)을 그대로 보낸다. 같은 후보 프로필에서 커밋된 경로로 1회 실행해 PS9→PS7을
시험하고 `make check`/safety 수치를 기록한다. 좌표 보정 스윕·추가 설정/DLL·재실행은 범위 밖이다.
이 클릭으로도 PS7에 도달하지 못하면 좌표공간 가설은 반증이며, 재시도 없이 승격한다.

## 지금 막힌 것 (Blockers)

- 같은 run/prefix/display 재사용, raw 성공 승격, validator 완화, summary 합성 금지.
- 원본/제품 EXE·DLL/assets/baseline/golden은 변경하지 않는다. 원본 SHA256은
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다.
- DirectDrawCreateEx ABI `(GUID*, LPVOID*, REFIID, IUnknown*)`, IAT slot `0x004E5018`.
- Surface7 49 entries; Blt/BltFast/Flip/GetSurfaceDesc indices 5/7/11/22.
- Release refcount 0은 record retire/private clone free; 자동 vtable rebind/49 추정 금지.
- finalization은 owned close → process exit → DLL detach → one summary → raw copy → validator이며,
  lap146 fresh run에서 이 순서의 관측 gate가 PASS했다.
- aggregation은 detailed+aggregated+dropped=total, 정상 PASS는 dropped=0/overflow 없음.
- lap142 직접 실행 실패는 lap143에서 독립 재현됐다. `tools/win32_close_fixture.py`의 package
  import에는 `python3 -m tools.win32_close_fixture build`를 사용하며 source를 임시 수정하거나
  `PYTHONPATH`에 의존하지 않는다. lap142 실패 원문은 history에 보존한다.
- 두 builder의 `--out-dir`은 호출 전에 존재하면 안 된다. fresh parent만 만들고 그 아래
  helper/bridge child는 만들지 않은 채 전달한다. lap144/lap145 산출물은 다음 runtime에 재사용 금지다.
- G1 2배 출력, G2 8인5000, G3 16인, G4 AI/pathfinding 및 사용자 승인은 모두 미검증이다.
- lap148 runtime은 root/client 1600×1200만 확인했고 PS9→PS7 scaled input gate에서 BLOCKED다.
  raw trace/log와 적용 후보는 `local/runtime/20260911_191958_4086515_0/output/g1_config_2x/`에 보존했다.
- 진단 bridge는 DirectDraw만 계측하고 커서/윈도우 메시지/버튼 이벤트를 **0건** 기록한다. 그래서
  "물리→게임 입력 결선이 어디서 끊겼는가"는 현재 증거로 판정 불가(UNKNOWN)다. 좌표 가설이 반증되면
  다음 단일 변경은 입력 관측 추가이며 설계는 middle tier가 받는다.
- lap148 런타임은 커밋되지 않은 inline 스크립트였고 복원 불가다(provenance는 `tools/runtime_env.py`
  `2609e7c2...c896a2`만 pin하지만, 그 커밋된 경로는 `runtime_env.py:2372-2373`에서 content≠800×600을
  거부하므로 실행 코드일 수 없다). 앞으로 G1 run은 커밋된 경로로만 실행한다.
- lap149는 이번 세션의 실행 권한 제약으로 `make check`/`checks/safety.sh`/PNG 해시를 실행하지 못했다
  (SKIP). lap148의 177 passed를 현재 성공으로 승격하지 않는다. 다음 lap이 이 공백을 메운다.

## 검증 상태

- 모델 라우팅: Luna/high, Opus5/high, Astra/medium argv 회귀 17 PASS. console-only Wine
  serializer fixture는 상위 셸의 stale DISPLAY를 제거하도록 고정했다. 관련 19 PASS,
  전체 Fast **173 passed**, Ruff/compileall/mypy/context/safety PASS.

- lap128 runtime: PS9→PS3/capture PASS, content 800×600, process 미종료/summary 0 BLOCKED.
- lap129~131: final raw 분리 수리와 Sol 확인, Fast 164 PASS.
- lap132~133: owned Win32 PID/HWND close fixture 및 Sol 확인, Fast 166 PASS.
- lap134~135: lossless bounded aggregation/validator 및 Sol 확인, Fast 169 PASS.
- lap136 runtime: run `local/runtime/20260911_172631_3142585_0`; PS9→PS3/input/WM_CLOSE/cleanup
  PASS, raw 651 lines; summary NUL@1023로 validator BLOCKED. 재실행하지 않음.
- lap137 diagnosis: expected 1046-byte summary vs wsprintfA 1024 limit 확정; Fast 169 PASS.
- lap138 serializer: native 1046-byte JSONL, 4095/4096 경계, old-1024 mutation; Fast 172 PASS.
- lap139 middle은 max run_id/failure-order 회귀 공백을 찾아 runtime 승인을 보류했다.
- lap140 Luna: 95-byte run_id/1103-byte JSONL과 failure-order mutations; Fast 173 PASS.
- lap141 Sol: targeted 12, Fast 173, fresh PE32/no-CRT, doctor/safety PASS;
  **MIDDLE CONFIRM PASS / FRESH RUNTIME READY**.
- lap142 Luna: fresh bridge build PASS (`/tmp/syw2plus_lap142_bridge.aXyhCY/build/_inmm.dll`,
  SHA `809fadaef1116f9f378628c77cff7358ed5006a8e5b2d86decdf8cf775462e68`); close-helper build
  failed before output (`ModuleNotFoundError: tools.win32_close_transport`). prepare/check/
  doctor-runtime/runtime/Fast were not run; **WORKER BLOCKED / SOL ESCALATION**.
- lap143 middle: direct invocation failure RC1 reproduced; module invocation fresh helper/target PE32
  SHA `76348519...`/`695fac86...`, fresh bridge PE32 SHA `c62fb858...`; helper fixture positive PASS와
  wrong-PID/0-window/multi-window fail-closed PASS. targeted **14 passed**, Fast **173 passed**;
  doctor original verified/no-side-effect와 safety PASS. actual game runtime/PNG/final summary/process
  exit/DLL detach는 SKIP. **MIDDLE CONFIRM PASS**.
- lap144 Luna: fresh helper/target PE32 SHA `31237342...`/`14dca5e0...`; 미리 만든 bridge out-dir로
  builder RC1/`FileExistsError`. 후속 runtime gate와 Fast는 SKIP. **WORKER BLOCKED / SOL ESCALATION**.
- lap145 middle: lap144 log/SHA와 builder 계약 확인; 비존재 child 확인 build RC0, PE32 DLL SHA
  `391c57a4...`, lap143 source manifest byte-equal; Fast **173 passed**. actual runtime은 SKIP.
  **MIDDLE CONFIRM PASS / RETRY AUTHORIZED**.
- lap146 Luna: 저장소 밖 fresh parent `/tmp/syw2plus_lap146.UeR2Kc`에서 helper/target PE32와
  bridge PE32를 새로 빌드하고, 새 run `local/runtime/20260911_184524_3746509_0`의
  `g1-presentation-trace`를 정확히 1회 실행했다. `prepare/check/doctor-runtime`, `make check`
  **173 passed**, safety **PASS**, runtime exit **0**, validator **PASS**. raw/normalized trace
  **byte-identical**, 651 events/summary 1/dropped 0/overflow 0, aggregation arithmetic PASS,
  owned WM_CLOSE/process exit/DLL detach/cleanup PASS. 진단 fixture는 default two-player random,
  synthetic=false·memory_writes=false·control_bridge=false·resource_grant=false이며, content와
  capture는 800×600이다. **WORK PASS / MIDDLE INDEPENDENT REVIEW REQUIRED**.
- lap147 middle: lap146 final/source/artifact/PNG SHA 전부 일치, raw/normalized byte-equal,
  단일 run/PID, owned WM_CLOSE→exit0→final summary/detach/flush, 651 events/dropped0/overflow0,
  집계 산술과 cleanup 재확인. standalone validator, doctor-runtime, safety, Fast **173 passed**.
  **MIDDLE CONFIRM PASS**; 제품 2배 출력과 사용자 승인은 미검증.
- lap148 Luna: fresh pinned wrapper/config-only profile candidate `f0ce9e64...6785`를 새 copy/
  prefix/display에서 1회 실행. root/client 1600×1200·2.0×2.0은 PASS, scaled menu 입력은
  PS9→PS7에 도달하지 못해 runtime BLOCKED. config restore, owned cleanup, Fast **177 passed**,
  safety/doctor PASS; `loop/ESCALATE_SOL` 승격 대기.
- lap149 middle: lap148 증거 해시 5/5 재계산 일치(`evidence df460618...`, `verdict e2855f17...`,
  `provenance df2599d6...`, `trace_raw 4b8bb4a0...`, `trace_install 2ffdd4a6...`), 적용
  `dxwrapper.ini`가 후보 `f0ce9e64...6785`와 byte 일치, 변경 3개(offset 211/1590/1622) 확인,
  원복 `918e7043...a5a2`와 pin `ddraw 3bc7230d...`/`dxwrapper 96c44319...`/원본 `b56986e0...` 일치.
  trace 354 events: `set_display_mode` 11건의 마지막이 800×600×8bpp, primary 800×600, PS9에서
  `blt_fast` 256건 연속. X11 client 1600×1200·scale 2.0×2.0·letterbox 없음. 입력은 1회
  `logical [184,560] → physical_root [368,1120]`, `result:"SENT"`. 대조군 lap146은 content child
  (0,0) 800×600에 클릭 (184,560)으로 PS7 PASS. wrapper 로그에 `Hooking mouse cursor!`와
  `GetDeviceCaps` hot-patch 실패 1건. **MIDDLE CONFIRM PASS / FAST SKIP / DIRECTION=입력 좌표 계약
  수리**; 결선 단절 지점은 UNKNOWN. `make check`/safety/PNG 해시는 실행 권한 없어 SKIP.

## 바퀴 기록

- lap2~118 상세는 기존 compaction 파일과 `docs/history/laps/` 원문에 보존한다.
- lap119~141 상세는 각 `docs/history/laps/20260911_lap*.md` 원문에 보존한다.
- 이전 current snapshot: `docs/history/laps/20260911_status_lap129_compaction.md`.
- 이번 pre-runtime snapshot: `docs/history/laps/20260911_status_lap142_compaction.md`.
- lap142 상세: `docs/history/laps/20260911_lap142_luna_g1_runtime_helper_build_block.md`.
- lap143 상세: `docs/history/laps/20260911_lap143_middle_g1_close_helper_import_confirmation.md`.
- lap144 상세: `docs/history/laps/20260911_lap144_luna_g1_fresh_build_block.md`.
- lap145 상세: `docs/history/laps/20260911_lap145_middle_g1_bridge_build_confirmation.md`.
- lap146 상세: `docs/history/laps/20260911_lap146_luna_g1_fresh_runtime_pass.md`.
- lap147 상세: `docs/history/laps/20260911_lap147_middle_g1_runtime_confirmation.md`.
- lap148 상세: `docs/history/laps/20260911_lap148_luna_g1_config_2x_block.md`.
- lap149 상세: `docs/history/laps/20260911_lap149_middle_g1_config_2x_input_contract_confirmation.md`
  (처리한 `loop/ESCALATE_SOL` 원문 보존 포함).
- work tier handoff: `docs/work/active/G1_INPUT_COORDINATE_CONTRACT_HANDOFF.md`.
- 모델 라우팅 변경: `docs/history/20260911_model_routing_update.md`.
