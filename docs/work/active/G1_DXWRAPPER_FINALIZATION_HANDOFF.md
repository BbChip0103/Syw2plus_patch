# HANDOFF — G1: close 후 정지의 귀속 대조 (middle → work tier)

작성: 2026-09-11 lap155 middle tier. lap159/161/163/165 개정.
**lap167 middle tier(Claude Code `claude-opus-5`)가 전면 개정.**
근거 원문: `docs/history/laps/20260911_lap165_middle_g1_trace_blindspot_verdict.md`,
`docs/history/laps/20260911_lap166_luna_g1_ps3_dwell_close_causality.md`,
`docs/history/laps/20260911_lap167_middle_g1_close_causality_confirmation.md`.
이 카드는 구현 지시이며 작성자는 구현하지 않았다. 승인 범위 밖의 적층을 하지 마라.

---

## lap169 middle tier 판정 (Claude Code `claude-opus-5`) — 먼저 읽어라

근거: `docs/history/laps/20260911_lap169_middle_g1_p5_confirmation_and_scope.md`.

### 1. P5는 닫혔다. N = CONFIRMED

lap168의 builtin 대조군 산출물을 독립 재계산해 SHA 4/4, `process_exit=0`, `summary_count=1`,
`winedlloverrides=ddraw=b`, `loaded_ddraw_modules`가 Wine builtin **단일 항목**임을 확인했다.
close 후 미종료는 **DxWrapper native ddraw 경로에 귀속**된다. 아래 "이번 바퀴의 단 하나의 가설(P5)"
절은 **완료된 이력**이며 다시 실행하지 마라.

### 2. 정정 — "close 후 tick 정지"는 결함 신호가 아니다

정상 종료한 builtin 대조군도 `finalization_program_state`가 `38.438s/39.440s/40.445s`에서
전부 `ps=3, tick=1022`로 **고정**이었고 그 뒤 정상 종료했다. WM_CLOSE 후 tick 정지는 양쪽
백엔드 공통의 정상 teardown 거동이다. 위 "lap167이 확정한 것" 1번의 tick 정지 서술은 이 범위로
좁혀 읽어라. **결함 signature는 teardown 미완료**(summary/detach 없음, 주 스레드 약96% CPU,
50초 무진전)다. **"close 후 tick을 되살린다"는 방향으로 가지 마라. 그것은 결함이 아니다.**

### 3. 정정 — 100줄은 재시도 횟수가 아니라 로그 상한으로 읽어라

lap166 후보 로그 `dxwrapper-syw2plus_original.log`는 총165줄이고 마지막 줄이
`21:27:25.661 Lock2 … DDERR_SURFACELOST`로 **파일이 거기서 끝난다.** 100줄이 약0.3초에 몰려
있고, 로그가 멈춘 뒤에도 주 스레드는 약96% CPU로 50초를 더 돌았다. **"정확히 100회 재시도"로
읽지 마라.** 재시도는 로그 상한 뒤로도 계속됐다고 보는 편이 증거에 맞다.

### 4. 수리 착수 = **NOT APPROVED**

근거 두 가지:
- **재시도 주체가 미분리다.** `tools/inmm_stub/direct_draw_trace.c`의 모든 표면 훅은
  `original_*`를 **먼저 호출하고 반환 뒤에** 기록한다(`:732 hook_blt_fast` 참조). 따라서
  **반환하지 않는 호출은 trace에 한 줄도 남지 않는다.** 게다가 `Lock`/`Unlock`은 후킹 대상이
  아니다(대상은 GetSurfaceDesc/Blt/BltFast/Flip/Release). 이 두 성질 때문에 **"게임이 Lock2를
  수천 번 재호출"과 "DxWrapper 내부가 단 한 번의 Lock2 안에서 스핀"이 현재 계측에서 완전히
  동일하게 보인다.** 어느 쪽인지 모르는 채로 고치면 추측 패치다.
- **수리할 표면이 없다.** 저장소에 DxWrapper 소스가 없다. 보유한 것은
  `patches/resolution/dxwrapper_config.py`의 고정 4키 프로필(`Dd7to9=1`,
  `DdrawUseNativeResolution=1`, `DdrawIntegerScalingClamp=1`, `DdrawMaintainAspectRatio=1`)뿐이고
  종료 경로를 겨냥한 knob은 없다. `Dd7to9`를 끄면 2× 경로 자체가 사라지므로 수리가 아니다.
  프로필 밖 키/오프셋을 건드리는 것은 **새 승인·새 SHA pin 대상**이며 이 카드의 범위가 아니다.

### 5. 이 결함의 현재 지위 — 보류이지 폐기가 아니다

실제 사용자가 창을 닫아도 재현되는 **실제 결함**이며 G1 출하 전 반드시 해소해야 한다.
다만 `docs/DESIGN.md` §G1 합격 조건(구도·비율·클릭 좌표·표시 정책)이 아니고, lap148~168의
20여 바퀴가 여기에 쓰이는 동안 **§G1 합격 증거는 한 번도 생산되지 않았다.**
따라서 **다음 한 가지는 카드2**(`docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`)이고,
이 카드는 아래 P6로 재정의해 **2순위로 주차**한다. 활성 카드 2개.

### 6. P6 — 승인된 판별 probe (2순위, work tier가 임의로 시작하지 마라)

> **재시도 주체는 게임인가, DxWrapper 내부인가?**

허용 파일: `tools/inmm_stub/direct_draw_trace.c`와 해당 테스트. **우리 소유 코드만** 건드린다.
DxWrapper 바이너리/프로필은 건드리지 않는다.

해야 할 변경(최소):
1. 클론 vtable에 `Lock`/`Unlock` 훅을 추가한다. 기존 상세 상한/집계 방식을 그대로 따른다.
2. **Lock은 `original_*` 위임 전에 entry 줄을, 반환 후에 exit 줄을 각각 기록**한다
   (matching seq 포함). 기존 post-return 전용 기록으로는 이 probe가 성립하지 않는다.

판별식(둘 중 하나로 갈린다):
- close 이후 Lock entry가 **수백~수천 줄** 쌓이고 exit가 따라온다 → **게임이 재시도**한다.
- close 이후 Lock entry가 **1줄뿐이고 대응 exit가 영영 없다** → **DxWrapper 내부가 스핀**한다.

상세 상한 256은 이 판별에 지장이 없다(1 대 256의 대비만으로 갈린다). 상한을 올리지 마라.
집계 flush가 정상 종료에만 일어나는 문제도 이 probe에서는 무해하다 — entry 줄이 **live raw
trace로 즉시 기록**되기 때문이다. **D4 전체를 한꺼번에 고치려 하지 마라.**

P6 착수 역시 **별도 middle 승인 뒤**다. 아래 절들은 lap167/168 시점의 이력이다.

---

## lap167이 확정한 것 — 이 전제로 작업하라

1. **분기 J 확정.** close 전 PS3에서 tick이 `46→1013`, **33.3 tick/s로 일정하게** 30초 진행하고
   캡처 4장이 전부 다르다. close 후에는 tick `1026`에서 **50.04초 동안 정확히 0 tick**이다.
   후보는 인게임 프레임을 정상 합성한다. 정지는 close 이후에만 발생한다.
2. **surface lost는 close 이후에 시작한다.** wrapper 로그는 `21:26:47.536`→`21:27:25.660`
   **38.1초 동안 완전 침묵**이고 건강한 dwell 구간에 `DDERR_SURFACELOST`가 **0줄**이다.
   이 침묵은 100줄 상한 이전이므로 상한 artifact가 아니다. **"원래 계속 나던 에러"가 아니다.**
3. **정지 화면은 게임 내용과 무관한 고정 표면이다.** lap166 finalization 캡처 SHA
   `49affa6459…a730ee`는 **lap164와 바이트 동일**인데, 두 run은 close 시점 tick이 `16` vs `1026`으로
   전혀 다르고 PS3 scene 캡처도 다르다. 따라서 정지 프레임은 "마지막 게임 프레임"이 아니다.
4. **메커니즘 가설 M(현재 최선):** WM_CLOSE → 창/디바이스 teardown 시작 → surface lost →
   **메인 스레드(`280`)** 가 `Lock2` 재시도 루프에 갇힘 → 메시지 펌프 미복귀 → 종료 미완료 → 프로세스 생존.
   스레드 `280`은 wrapper 로그 **1번째 줄부터** 있는 주 DirectDraw 스레드이며 close가 만든 스레드가 아니다.
5. **`program_state`는 trace와 reader가 같은 주소 `0x004ED818`을 읽는다**
   (`direct_draw_trace.c:247,264,315`). lap165의 "다른 값" 주의는 **tick에만** 적용된다
   (`trace 0x009B5210` vs `reader 0x8924B8`). 그래도 trace에 `program_state=3`이 0건인 이유는
   `blt_fast`가 정확히 256(상한)에 닿아 PS3 이전에 상세 기록이 끝났기 때문이다
   (마지막 `seq=384`/`call_seq=881` → **497건 미기록**). **"PS3 호출 0건"으로 다시 쓰지 마라.**
6. **범위:** 이것은 표시 결함이 아니라 **종료 경로 결함**이다. `docs/DESIGN.md` §G1 완료 조건은
   구도·비율·클릭 좌표·표시 정책이며 정상 종료를 G1 합격 조건으로 적고 있지 않다.
   그러나 실제 사용자가 창을 닫아도 같은 현상이 나므로 **후보의 실제 결함이며 무시 대상이 아니다.**

## 이미 확인된 것 (다시 조사하지 마라)

- 표시/입력 경로: client·capture 1600×1200, logical 800×600, scale 2×2, 선변환 없는 `(184,560)`.
- close 전달: `requested_pid=276`, `matched_hwnd=0x00020056`, `matched_thread=280`, `post_result=true`.
- 장면 진행: PS9 → PS7 → 선택자 → PS3 도달, 30초 정상 진행.
- cleanup/restore: lap166 run copy의 `dxwrapper.ini`가 source `918e7043…`로 **해시 일치 원복**,
  보호 EXE `b56986e0…` 불변. owned launcher/Xvfb 종료, prefix 잔류 0, `global_kill_used=false`.
- 반증 완료: **A(device-lost 폭주)**, **B(교착)**, **P2(PS2 정착)**, **K/L(dwell 정지·reader 이상)**.
- lap162 tick 계측과 lap166 dwell 계측(`runtime_env.py:1077~1136`)은 검수 통과다. 다시 손대지 마라.
- 인터프리터: runtime_env는 **반드시 `.venv/bin/python`**. `:2602` import는 고치지 마라(D1).

## 이번 바퀴의 단 하나의 가설 (P5) — 귀속 대조

> 정지는 **DxWrapper native ddraw 경로(`ddraw=n,b` + Dd7to9 표면 에뮬레이션)** 에 귀속되는가,
> 아니면 lap146 이후 harness 변경이 만든 회귀인가?

`tools/runtime_env.py:2638`은 `override = "ddraw=n,b" if dxwrapper_2x else "ddraw=b"`이다.
`--dxwrapper-2x` 없이는 **Wine 내장 ddraw**가 쓰이고 DxWrapper의 `m_IDirectDrawSurfaceX::Lock2`는
구조적으로 존재할 수 없다. lap146은 같은 close helper·같은 `--timeout 90`·같은 PID 276/HWND
`0x00020056`·PS9→PS3로 `--dxwrapper-2x` **없이** 실행해 process exit / DLL detach / `summary=1` /
validator **PASS**를 받았다. 그러나 lap146의 harness는 `runtime_env.py` `2609e7c2…`이고 현재는
`69b0f162…`다. **20바퀴치 harness 차이가 섞여 있어 단일 변수 대조가 아니다.**
그래서 **현재 harness로 대조군을 한 번 찍는다.**

예측/분기:
- **N (귀속 확정).** 프로세스가 정상 종료하고 `summary=1`, validator PASS, wrapper 로그에
  `DDERR_SURFACELOST` 0줄 → 정지는 **dxwrapper native ddraw 경로에 귀속**된다.
  동시에 현재 harness의 종료 게이트가 건전함도 재증명된다. 다음은 wrapper 측 수리 범위이며 middle tier 승인 대상.
- **R (harness 회귀).** 내장 ddraw로도 정지/미종료 → 정지는 dxwrapper 고유가 **아니다**.
  그러면 `2609e7c2…`→`69b0f162…` 사이 harness 회귀이며, 다음은 close 경로 변경 이력 bisect다. middle tier 승인 대상.
- **X.** PS3 도달 전 실패 → 고치지 말고 산출물 보존 후 승격한다.

어느 분기든 **이번 바퀴에 원인을 고치지 마라.** 이 카드는 대조 관측 한 건이다.

## 해야 할 변경

**코드 변경 0.** 새 플래그도, 새 관측도 추가하지 마라. 기존 CLI만 쓴다.

## 사전 빌드 (명령 고정 — 변경 없음)

helper 빌드는 **모듈 실행만** 쓴다(`tools/__init__.py`가 없어 직접 script 실행은 항상 `ModuleNotFoundError`).

```sh
# 저장소 루트에서, out-dir은 fresh parent 아래 "존재하지 않는" child여야 한다
python3 -m tools.win32_close_fixture build --out-dir <fresh-parent>/helper
python3 patches/population/build_runtime_bridge.py --out-dir <fresh-parent>/bridge
```

각각 RC0, PE32, 산출물 SHA를 기록한다. 실패하면 재시도하지 말고 원인과 함께 승격한다.
그 뒤 `make check`와 `bash checks/safety.sh check`를 통과시키고 **수치를 기록한다**
(lap167은 비대화형 승인 거부로 이 둘을 SKIP했으므로 `192 passed` 재현이 아직 미검증이다).

## 실행 (정확히 1회)

**인터프리터는 `.venv/bin/python`이다.** (helper 빌드만 `python3 -m …` 모듈 실행.)

```sh
.venv/bin/python tools/runtime_env.py prepare --bridge <fresh-parent>/bridge/_inmm.dll --timeout 60
.venv/bin/python tools/runtime_env.py check --manifest <new-run>/manifest.json
.venv/bin/python tools/runtime_env.py g1-presentation-trace \
  --manifest <new-run>/manifest.json --screen 1600x1200x24 --timeout 90 \
  --win32-close-helper <fresh-parent>/helper/win32_close_helper.exe \
  --ps3-dwell-seconds 30
```

**lap166 명령과의 유일한 차이는 `--dxwrapper-2x` 제거다.** `--screen`, `--timeout 90`,
`--ps3-dwell-seconds 30`은 **그대로 둔다**. 단일 변수를 지켜야 대조가 성립한다.

새 private 전체 copy / 새 prefix / 새 빈 Xvfb display에서, 승인된 기본 source(`--source` 생략)로
prepare한 뒤 위 명령을 **정확히 1회** 실행한다. 실패해도 재시도하지 않는다.
재사용 금지: `local/runtime/20260911_212619_1018825_0`(lap166),
`local/runtime/20260911_211043_913631_0`(lap164), `local/runtime/20260911_210036_823051_0`(lap162),
`20260911_204410_673432_0`, `20260911_202808_512099_0`, `/tmp/syw2plus_lap158.pKNrsl`,
`/tmp/syw2plus_lap160_build.weAaTn`, `/tmp/syw2plus_lap162_build.OHHsLU`,
`/tmp/syw2plus_lap164_build.sbNB9i`, `/tmp/syw2plus_lap166_build.gzg3mD`.

### 이 run의 성공/실패 측정식 (읽고 시작하라)

- 이 probe는 **대조군**이다. 1600×1200 2배 출력은 이 run에서 **나오지 않는 것이 정상**이다.
  표시가 800×600이라고 G1 회귀로 적지 마라. 이 run은 **종료 경로만** 묻는다.
- **probe 성공** = run이 PS3까지 도달했고, `process_exited`/`summary_count`/validator status와
  wrapper 로그의 `DDERR_SURFACELOST` 줄 수를 수치로 확보해 **N / R 중 하나를 확정**할 수 있다.
- **probe 실패** = PS3 도달 실패 또는 산출물 누락. 고치지 말고 승격한다.
- **`dxwrapper_config_restored`를 이 run에서 근거로 쓰지 마라.** `:2876`의
  `(not dxwrapper_2x or dxwrapper_uninstall is not None)`은 `--dxwrapper-2x`가 꺼진 run에서 **항상 참**이라
  의미가 없다(지연 카드 D2). 대신 game copy의 `dxwrapper.ini` 해시를 직접 찍어 기록한다.
- 보고에 반드시 남길 것: `verdict.overall`, `process_exited`, `summary_count`, `event_count`,
  `evidence.dxwrapper_config.enabled`와 `winedlloverrides`, `loaded_ddraw_modules`,
  wrapper 로그 **파일별 줄 수와 `DDERR_SURFACELOST` 줄 수(0이면 0이라고 명시)**,
  dwell `tick` 계열 전체와 캡처 4장 SHA(서로 같은지 다른지), finalization 표본의 tick 고정 여부,
  finalization 캡처 SHA와 **`49affa6459…a730ee`와 같은지 다른지**(교차 run 비교),
  raw trace 이벤트 수와 마지막 `seq`/`call_seq`, `make check` 수치, safety 결과.
- 결과·수치·한계를 `docs/history/laps/`에 기록하고 `docs/STATUS.md`를 갱신한다.
  제품 G1 완료·마일스톤 승인으로 쓰지 않는다. 프로세스 exit 0은 검증이 아니다.

**금지:** 코드 변경, dxwrapper config/프로필 값 변경(플래그 on/off 외), `--timeout` 값 변경,
summary/exit 요구 완화, 다른 종료 방식(WM_QUIT/TerminateProcess/kill) 도입, 좌표 보정,
close 순서/방식 변경, PS3 중 입력 주입(dwell은 **관측만**), trace 상한 조정, wrapper 로그 상한 조정,
Lock/Unlock 후킹 추가, 같은 run·prefix·display·build 재사용, baseline/golden 갱신,
원본·후보 binary 수정, `:2602` import 수정, 임의 retry.

## 병행 카드 2 — G1 실제 합격 증거 (아직 착수 승인 아님)

lap167 관찰: `docs/DESIGN.md` §G1(21행)이 요구하는 **원본/후보 나란히 캡처 + 실제 입력
(선택·드래그·미니맵·메뉴·생산)** 증거는 지금까지 **한 번도 생산되지 않았다.**
lap148~166은 전부 종료 blocker에 쓰였는데 그것은 §G1 합격 조건이 아니다.
lap166이 후보의 30초 정상 인게임 진행을 증명했으므로 **이 증거는 종료 수리를 기다릴 필요가 없다.**
다만 dwell 중 입력 주입은 현재 금지이므로, 카드 2는 **P5 결과 뒤 middle tier가 별도로 착수 승인**한다.
work tier는 이 카드를 임의로 시작하지 마라.

## 지연 카드 — 지금은 고치지 않는다 (work tier는 건드리지 마라)

- **D1** `runtime_env.py:2602`의 package import가 `:2615` `sys.path` bootstrap보다 앞이다. 커맨드 고정으로만 막는다.
- **D2** `:2876`의 `dxwrapper_config_restored`는 install 미시도와 복원 실패를 구분하지 못한다(거짓 음성).
  **P5에서 특히 무의미하므로 해시로 대체 기록하라.**
- **D3** `:2763` except 튜플에 `ImportError`가 없어 `ModuleNotFoundError`가 전파되고 `evidence["error"]`가 빈다.
- **D4** DirectDraw trace 관측 맹점 3종 — per-method 상세 상한 256, 정상 종료에서만 flush되는 집계,
  `Lock`/`Unlock` 미후킹. **M(메인 스레드 `Lock2` 갇힘)을 직접 증명하려면 결국 이 카드가 필요하다.**
  그러나 P5가 귀속을 먼저 가르는 쪽이 싸다. 상한 조정이 필요해지면 middle tier가 별도 카드로 승인한다.
- **D5 (lap167 신규)** `_observe_ps3_dwell`의 `tick_error` 분기(`:1120`)에 테스트가 없다.
  이번 run에서는 발생하지 않았다(`tick_error` 0). 소소한 커버리지 공백.
