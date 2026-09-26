# STATUS pre-compaction snapshot — lap 168

P4 close 인과 확정 및 P5 대조군 승인 직후 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `810344f38fa5c4b59f1f108ae56a86528821c2a30a0f0642760404be2adcd587`
- line count: `217`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. 최우선 G1은 원본 800×600 논리 구도/UI를 유지한
1600×1200 정수 2배 출력이다. G2는 전비 5000 숫자 패치만 있고 8인 부하·개체 풀/메모리
확장 증명이 없다. G3 16인과 G4 길찾기·AI는 구현 전이다.

진단 하네스는 원본 800×600 경로의 입력·장면 전이·정상 종료와 cleanup을 통과했다. 이후 pinned
`ddraw.dll`/`dxwrapper.dll` config-only 후보, private install/uninstall, SHA 고정, byte-exact
restore, opt-in `ddraw=n,b`, module evidence를 구현했다.

lap154/158/160의 fresh 후보 runtime은 client/capture 1600×1200, logical DirectDraw 800×600,
scale 2×2, 선변환 없는 `(184,560)` 입력과 PS9→PS7→PS3 도달을 반복 확인했다. config 원복과
owned cleanup도 PASS했다. PS3 진입 뒤 close 후 process exit와 trace summary가 없어 90초 timeout으로
BLOCKED했지만, lap166의 close 전 30초 dwell에서는 tick/프레임이 진행해 정지의 close 상관관계를
확정했다. 정상 종료와 underlying `Lock2/DDERR_SURFACELOST` 원인 수리는 아직 성립하지 않았다.

lap160~163에서 확정돼 **되돌리지 않는 전제**(원문: `docs/history/laps/`의 lap160·161·163 기록):
가설 A(device-lost 폭주)·B(교착)·P2(PS2 정착)는 반증됐다. trace 꼬리의 PS2 30건은 close 이후
재초기화가 아니라 close 전 28ms짜리 PS3 장면 로드다. wrapper `DDERR_SURFACELOST`의 100줄 뒤
침묵은 per-callsite 로그 상한이지 호출 중단 증거가 아니다. finalization reader와 bridge는 같은
live 주소 `0x4ED818`을 읽는다. CPU 증가의 약 96%가 단일 스레드에 집중된다. lap162의 import 실패는
코드 회귀가 아니라 **실행 표면 이탈**이며(`:2602` import가 `:2615` bootstrap보다 앞, `__init__.py` 없음)
runtime_env는 반드시 `.venv/bin/python`으로 실행한다. lap162의 cleanup 경보 2건은 거짓 경보였고
tick 관측 구현은 검수 통과라 재구현 대상이 아니다.

**lap165가 반증한 전제:** lap161이 적었던 "PS3 구간 DirectDraw 이벤트 0건"은 성립하지 않는다.
아래 lap165 문단을 근거로 쓰고, 옛 문장을 다시 인용하지 마라.

lap164 work tier는 새 parent/bridge/helper와 `.venv/bin/python`으로 P3를 정확히 1회 실행했다.
1600×1200·800×600·2×2·입력·PS9→PS7→PS3·close 전달·cleanup/config 원복은 PASS했다. 그러나
finalization reader의 78개 표본이 `ps=3/tick=16`으로 9.341~89.583초 동안 불변했고 process는
살아 있어 timeout/BLOCKED됐다. 새 PS3 캡처는 실제 게임 장면/HUD인데 raw trace는 `program_state=3`
0건이라 의미 충돌로 `loop/ESCALATE_SOL`에 승격했다.

lap165 middle tier(Opus5/high)가 그 승격을 **해소**했다. 보존 산출물 6/6 SHA를 재현했고,
충돌은 관측 모순이 아니라 **계측기 맹점 3종**이었다. (1) DirectDraw trace의 상세 기록은
method마다 `TRACE_MAX_METHOD 256`에서 끊기고 `blt_fast`가 정확히 256으로 상한에 닿았다.
상한 이후 호출은 메모리 집계로 들어가는데 집계 flush는 정상 종료에서만 일어나므로
(`direct_draw_trace.c:960~961`) 이 run에서는 한 번도 파일에 나오지 않았다. 마지막 줄이
`seq=384`/`call_seq=1047`인 것 자체가 663건 미기록을 뜻한다. (2) `Lock`/`Unlock`은 애초에
후킹 대상이 아니라 Lock 무한 반복은 trace에 한 줄도 남지 않는다. (3) reader `tick`(`0x8924B8`,
게임 로직 tick)과 trace `game_tick`(`0x009B5210`, 밀리초 시계)은 **서로 다른 값**이다.
따라서 "PS3에서 DirectDraw 호출 0건"이라는 lap161 전제는 **반증**한다.

lap165는 lap164가 보고하지 않은 두 사실도 찾았다. finalization 캡처 2장(`close_plus_5s`,
`timeout_minus_5s`)은 SHA가 **완전히 동일**해 화면이 71초 동안 1픽셀도 바뀌지 않았고, PS3 scene
캡처와는 다르다. 그리고 이 run의 wrapper 로그 165줄 중 마지막 100줄이 전부
`Lock2 … DDERR_SURFACELOST`이며 **전부 같은 타임스탬프 `21:11:22.759`** — 1ms에 100건인
tight retry loop다. 종합하면 분기 H(게임 루프가 진행하지 못함)가 성립하고 분기 G(close 의미론)는
지지되지 않는다. 다만 러너가 `ps==3 && tick>0` 직후 close를 보내므로 **정지가 close 때문인지
close와 무관한지는 아직 갈리지 않았다**. 코드 변경 0.

lap166 work tier는 새 helper/bridge와 `.venv/bin/python`으로 P4를 정확히 1회 실행했다. 30개
dwell 표본은 `ps=3`, tick `46→1013` 단조 증가, +1/+10/+20/+30 캡처 SHA는 모두 상이했고,
close 후 finalization tick은 `1026`으로 고정됐다. 분기 **J(close 상관)** 를 확정했으며, 기존
finalization은 summary0/process alive로 BLOCKED됐다. close 전달/cleanup/config 원복은 PASS했고
원인 수정은 하지 않았다. 상세는 `docs/history/laps/20260911_lap166_luna_g1_ps3_dwell_close_causality.md`.

lap167 middle tier(Opus5/high)가 그 승격을 **해소**했다. source 2/2 + 산출물 4/4 SHA를 재현하고
dwell tick 계열·캡처 SHA·close 전달·finalization 49건·wrapper 165줄/100줄·trace 384 events를
전부 대조해 **분기 J를 확정(CONFIRMED)** 했다. 근거는 lap166 보고보다 강하다: close 전 **33.3 tick/s
로 일정**하게 30초 진행 → close 후 **50.04초 동안 정확히 0 tick**이다.
lap166이 보고하지 않은 신규 사실 3건을 찾았다. (1) wrapper 로그는 `21:26:47.536`→`21:27:25.660`
**38.1초 침묵**이고 건강한 dwell 전 구간에 `DDERR_SURFACELOST`가 **0줄**이다 — 100줄 상한 이전의
침묵이므로 surface lost는 **close 이후에 시작**한다. (2) lap166 finalization 캡처 SHA
`49affa6459…a730ee`는 **lap164와 바이트 동일**인데 두 run은 close 시점 tick이 `16` vs `1026`으로
전혀 다르다 → 정지 프레임은 "마지막 게임 프레임"이 아니라 **내용과 무관한 고정 표면**이다.
(3) tight loop 스레드 `280`은 wrapper 로그 1번째 줄부터 있는 **주 DirectDraw 스레드**다.
→ 메커니즘 가설 **M**: 메인 스레드가 `Lock2` 재시도에 갇혀 메시지 펌프가 복귀하지 못하고,
그래서 WM_CLOSE 종료가 완료되지 않으며 프로세스가 생존한다. 게임 실행 0회, 코드 변경 0.

lap167의 전제 정정: trace `program_state`는 reader와 **같은 주소 `0x004ED818`** 을 읽는다
(`direct_draw_trace.c:247,264,315`). lap165의 "서로 다른 값" 주의는 **tick에만** 해당한다.
trace에 `program_state=3`이 0건인 이유는 여전히 `blt_fast`가 256 상한에 닿아 PS3 이전에 상세 기록이
끝났기 때문이다(마지막 `seq=384`/`call_seq=881` → 497건 미기록). lap165 결론은 유지된다.

**범위 판정(lap167):** 이 정지는 표시 결함이 아니라 **종료 경로 결함**이다. `docs/DESIGN.md` §G1
완료 조건(16~22행)은 구도·비율·클릭 좌표·표시 정책이며 정상 종료를 G1 합격 조건으로 적고 있지 않다.
그러나 실제 사용자가 창을 닫아도 같은 현상이 나므로 **후보의 실제 결함이며 무시 대상이 아니다.**

모델 라우팅은 Luna/high(work), Claude Opus5/high(middle/judge), Astra/medium(strategy)이다.
Astra는 자동/정기 호출하지 않고 **큰 분기·반복 교착에서만**, 대략 work/middle 10 lap당 1회
이하로 사용한다. high는 medium으로 고위험 복수 경로를 결정할 수 없을 때만 명시한다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 메뉴/로비·입력·PS3 도달·1600×1200/800×600/2×2 및 30초 정상 진행(33.3 tick/s) PASS. **§G1 합격 증거(원본/후보 나란히 캡처 + 선택·드래그·미니맵·메뉴·생산 실제 입력) 미생산 — 이것이 G1의 실제 미충족분이다.** 별건으로 종료 경로 결함(close 후 0 tick·summary0·`Lock2/DDERR_SURFACELOST`) 미수리 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

work tier가 **P5 귀속 대조 probe**를 정확히 1회 실행한다. lap166 명령에서 **`--dxwrapper-2x`만
제거**하고 `--screen 1600x1200x24 --timeout 90 --ps3-dwell-seconds 30`은 그대로 둔다. 코드 변경 0.
`runtime_env.py:2638`이 `override = "ddraw=n,b" if dxwrapper_2x else "ddraw=b"`이므로 2x가 꺼지면
Wine 내장 ddraw가 쓰이고 DxWrapper의 `Lock2`는 존재할 수 없다. 분기 **N**(정상 종료·summary1·
`DDERR_SURFACELOST` 0줄 → 정지는 dxwrapper native ddraw 경로 귀속) 대 **R**(내장 ddraw로도 정지 →
lap146 harness `2609e7c2…`→현재 `69b0f162…` 사이의 회귀)을 가른다. 지시는
`docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`. 이 run에서 1600×1200이 안 나오는 것은
**정상**이며 G1 회귀로 적지 않는다. 원인 수정은 P5 결과 뒤 middle tier 승인 대상이다.
제품 G1 완료·마일스톤 승인으로 승격하지 않는다.

**병행 카드 2(아직 착수 승인 아님):** `docs/DESIGN.md` §G1(21행)이 요구하는 원본/후보 나란히 캡처
+ 실제 입력(선택·드래그·미니맵·메뉴·생산) 증거는 **한 번도 생산된 적이 없다**. lap148~166은 전부
종료 blocker에 쓰였는데 그것은 §G1 합격 조건이 아니다. lap166이 후보의 30초 정상 인게임 진행을
증명했으므로 이 증거는 **종료 수리를 기다릴 필요가 없다**. dwell 중 입력 주입이 현재 금지이므로
카드 2는 P5 결과 뒤 middle tier가 별도로 착수 승인한다. work tier는 임의로 시작하지 마라.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경 금지. 보호 EXE SHA:
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 실패 run/prefix/display 재사용, 임의 retry, validator/summary/exit 요구 완화 금지.
- P5는 **코드 변경 0**이다. `--dxwrapper-2x` 제거 외에 dxwrapper config 값, `--timeout`, 종료 방식,
  좌표, close 순서/방식 변경 금지. PS3 dwell은 **관측만** 허용된 예외이며 입력 주입·클릭·좌표
  보정을 포함하지 않는다. 원인 수리는 P5 결과에 대한 middle tier 승인 전까지 금지한다.
- P5 run에서 `dxwrapper_config_restored`를 근거로 쓰지 마라. `:2876`의 식은 `--dxwrapper-2x`가 꺼진
  run에서 **항상 참**이라 의미가 없다(D2). game copy `dxwrapper.ini` 해시를 직접 찍어 기록한다.
- trace 상한(`TRACE_MAX_METHOD`/`TRACE_MAX_EVENTS`/`TRACE_MAX_AGGREGATES`), wrapper 로그 상한,
  `Lock`/`Unlock` 후킹 추가는 지연 카드 D4이며 지금 손대지 않는다.
- helper는 `python3 -m tools.win32_close_fixture`로만 fresh out-dir에 빌드한다.
- builder 두 개의 `--out-dir`은 fresh parent 아래 존재하지 않는 child여야 한다.
- 현재 후보는 close 전 PS3에서 30초 동안 33.3 tick/s로 진행한다(J 확정). close 후에는 tick `1026`
  고정·50.04초 0 tick, process alive/summary0으로 finalization이 BLOCKED다. 원인 수리 금지.
- `DDERR_SURFACELOST`를 "원래 계속 나던 배경 에러"로 쓰지 마라. lap167 확인: 건강한 30초 dwell
  구간에 0줄이고, wrapper 로그는 그 앞뒤로 38.1초 침묵하다가 close 이후에만 100줄이 터진다.
- finalization 캡처 `49affa6459…a730ee`를 "마지막 게임 프레임"으로 쓰지 마라. lap164(close@tick16)와
  lap166(close@tick1026)이 **바이트 동일**이므로 내용과 무관한 고정 표면이다.
- lap166 재사용 금지 run/build: `local/runtime/20260911_212619_1018825_0`,
  `/tmp/syw2plus_lap166_build.gzg3mD`.
- lap167은 `make check`/`checks/safety.sh`를 **비대화형 승인 거부로 SKIP**했다. lap166의
  `192 passed`는 아직 독립 재현되지 않았다. P5 work tier가 수치를 다시 기록한다.
- DirectDraw raw trace를 "PS3 호출 0건"의 근거로 다시 쓰지 마라. 상세 상한 256·미flush 집계·
  `Lock`/`Unlock` 미후킹 때문에 구조적으로 조용하다(lap165 판정).
- EIP/wchan probe는 이번에 승인하지 않았다. 정지 callsite가 wrapper 로그로 이미 지목됐고,
  P4가 인과를 가른 뒤 필요 여부를 middle tier가 정한다.
- G2~G4 및 사용자 마일스톤 완료를 과거 PASS/SKIP/timeout으로 승격하지 않는다.
- lap162 fresh run은 import 실패로 P3 표본 0건이다. `loop/ESCALATE_SOL`은 lap163이 해소했다.
  실패 run/prefix/display/build 재사용 금지: `local/runtime/20260911_210036_823051_0`,
  `/tmp/syw2plus_lap162_build.OHHsLU`.
- runtime_env는 반드시 `.venv/bin/python`으로 실행한다. 시스템 `python3` script 실행은 `:2602`에서 죽는다.
  `:2602` import 순서는 **아직 고치지 않았다**(지연 카드 D1). 커맨드 고정으로만 막고 있다.
- lap162 run의 `wrapper_logs/` 8개는 source copy의 기존 로그이며 그 run의 wrapper 활동이 아니다.
- lap164 fresh run은 `local/runtime/20260911_211043_913631_0`에 보존했다. verdict는 summary 0/
  process exit false로 BLOCKED이며 임의 retry 금지. `loop/ESCALATE_SOL`은 lap165가 해소했다.
  재사용 금지 build: `/tmp/syw2plus_lap164_build.sbNB9i`.

## 검증 상태

- lap146~147: diagnostic 800×600, PS9→PS3, process exit/DLL detach/summary/cleanup PASS.
- lap148~154: config patch·private 적용·논리 입력 계약 수립; lap154에서 1600×1200/800×600/2×2/
  입력/PS3 PASS, finalization BLOCKED, Fast 182와 safety PASS.
- lap155~159: 종료 blocker 관측 P1 및 독립 검수. direct helper script 실패는 module invocation으로
  해소. Fast 186 및 fresh runtime 재확인. device-lost 폭주/PS2 재정착 해석은 후속 증거로 반증.
- lap160: P2 관측, fresh runtime 1회, Fast 187/safety/build PASS; PS3 78회·동일 검은 캡처 2장·
  단일 프로세스 생존·summary0/process exit false.
- lap161: Opus 독립 검수. SHA 7/7 재현, P2 반증/cleanup/config 원복 PASS; 명령 실행·PNG 재열람은
  권한상 SKIP. 코드 변경 없음. `loop/ESCALATE_SOL` 해소, P3 승인.
- lap162: P3 tick 계측/3케이스와 Fast 190 PASS; fresh build/prepare/doctor PASS. 정확히 1회 runtime은
  `ModuleNotFoundError: No module named 'patches'`로 게임 전 BLOCKED, cleanup의 `wineserver -k`도 실패.
  tick/PS3 표본 없음. `loop/ESCALATE_SOL` 생성.
- lap163: Opus5 middle 독립 검수. source 2/2 + 산출물 3/3 SHA 재현, tick 구현이 handoff 지시와 일치 PASS.
  import 실패=실행 표면 이탈로 확정, cleanup 경보 2건은 거짓 경보로 반증(게임 copy `dxwrapper.ini`가
  pinned SOURCE 해시, sidecar 없음, 잔류 0). 코드 변경 0. 관측 결함 D1~D3은 지연 카드로 기록.
  `make check`/pytest 재실행은 비대화형 권한으로 SKIP(바이트가 lap162와 동일).
  `loop/ESCALATE_SOL` 해소, 코드 변경 없는 P3 재개 승인.
- lap164: fresh helper/bridge PE32, prepare/check, `make check` 190 passed, safety PASS. 정확히 1회
  P3는 timeout/BLOCKED; reader 78개 `ps=3/tick=16` 불변, close/cleanup/config 원복 PASS. 캡처는
  visible PS3 scene이지만 raw trace는 PS3 state 0건이라 의미 충돌. 코드 변경 없음, middle 승격.
- lap165: Opus5 middle 독립 검수. 보존 산출물 6/6 SHA 재현, source 3/3 바이트 동일 확인.
  의미 충돌을 계측기 맹점 3종(상세 상한 256·미flush 집계·`Lock` 미후킹)으로 해소하고
  "PS3 DirectDraw 0건" 전제를 반증. 새 사실 2건: finalization 캡처 2장 SHA 동일(71초 프레임 동결),
  wrapper 로그 마지막 100줄이 동일 타임스탬프 `21:11:22.759`의 `Lock2 DDERR_SURFACELOST`.
  분기 H 성립/분기 G 미지지. 게임 실행 0회, 코드 변경 0. PNG 재열람과 `make check` 재실행은
  경로·비대화형 권한으로 SKIP(코드 변경이 없어 Fast 재측정 대상 없음).
  `loop/ESCALATE_SOL` 해소, P4(PS3 dwell) 승인.
- lap166: fresh helper/bridge, prepare/check, `make check` 192 passed 및 safety PASS. 정확히 1회
  P4 dwell은 30개 `ps=3` 표본과 tick `46→1013` 단조 증가, 4장 상이 캡처로 J(close 상관)을 확정했다.
  close 전달/cleanup/config 원복 PASS, 이후 finalization은 tick `1026` 고정·summary0/process alive로
  BLOCKED. 원인 수정 없음. 중간-tier 독립 컨펌을 위해 `loop/ESCALATE_SOL` 생성.
- lap167: Opus5 middle 독립 검수. source 2/2 + 산출물 4/4 SHA 재현, dwell 30표본/tick 계열/캡처 4장
  상이/close 전달/finalization 49건 tick `1026` 고정/wrapper 165줄·100줄/trace 384 events·`blt_fast=256`·
  마지막 `seq=384`/`call_seq=881`을 전부 대조해 **J 확정**. 보호 EXE `b56986e0…`와 run copy
  `dxwrapper.ini` `918e7043…`를 해시로 직접 재확인(원복 플래그가 아니라 바이트로 확인).
  신규 3건: dwell 구간 `DDERR_SURFACELOST` 0줄·38.1초 침묵(close 이후 시작), finalization 캡처가
  lap164와 바이트 동일(내용 무관 고정 표면), tight loop 스레드 `280`이 주 DirectDraw 스레드 →
  메커니즘 가설 **M**. 전제 정정: `program_state`는 trace/reader 동일 주소 `0x004ED818`.
  범위 판정: 종료 경로 결함이며 §G1 합격 조건이 아니다(그러나 후보의 실제 결함). 게임 실행 0회,
  코드 변경 0. `make check`/safety 재실행은 비대화형 승인 거부로 **SKIP**(코드 변경 0이라 재측정 대상 없음,
  다만 `192 passed`는 미재현으로 남김). `loop/ESCALATE_SOL` 해소, **P5 귀속 대조 probe 승인**.
- pre-compaction snapshot SHA `ade649ca08d863b90cfccd36b6d26069d0332a7ac374a2f5e6d00303b03b8a85`;
  원문은 `docs/history/laps/20260911_status_lap162_compaction.md`에 보존했다.
- **정비 필요(lap167 기록):** STATUS가 213줄로 커졌다. lap160~166 서술은 전부
  `docs/history/laps/`에 보존돼 있으므로 다음 middle tier가 스냅샷을 남기고 압축한다.
  단 "되돌리지 않는 전제"와 Blockers의 금지 항목은 **삭제하지 말고 유지**한다.
  이번 lap은 "한 바퀴 한 가지" 규칙에 따라 압축을 수행하지 않았다.

## 바퀴 기록

- lap2~160 및 이전 STATUS 원문: `docs/history/laps/`.
- latest snapshot: `docs/history/laps/20260911_status_lap162_compaction.md`.
- lap160 work: `docs/history/laps/20260911_lap160_luna_g1_finalization_observation_probe.md`.
- lap161 middle: `docs/history/laps/20260911_lap161_middle_g1_finalization_p2_recheck.md`.
- lap162 work: `docs/history/laps/20260911_lap162_luna_g1_p3_tick_observation_build_runtime_block.md`.
- lap163 middle: `docs/history/laps/20260911_lap163_middle_g1_runtime_import_surface_verdict.md`.
- lap165 middle: `docs/history/laps/20260911_lap165_middle_g1_trace_blindspot_verdict.md`.
- lap166 work: `docs/history/laps/20260911_lap166_luna_g1_ps3_dwell_close_causality.md`.
- lap167 middle: `docs/history/laps/20260911_lap167_middle_g1_close_causality_confirmation.md`.
- current escalation: 없음. lap166의 `loop/ESCALATE_SOL`은 lap167이 해소했다.
  승격 원문 보존: `docs/history/laps/20260911_lap166_escalate_sol_original.md`,
  `docs/history/laps/20260911_lap164_escalate_sol_original.md`,
  `docs/history/laps/20260911_lap162_escalate_sol_original.md`.
- current handoff: `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`.
- model routing: `docs/history/20260911_model_routing_update.md`.
