# STATUS pre-compaction snapshot — lap 162

P3 승인과 PS3 렌더/close 원인 프레이밍 교정 직후 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `ade649ca08d863b90cfccd36b6d26069d0332a7ac374a2f5e6d00303b03b8a85`
- line count: `181`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. 최우선 G1은 원본 800×600 논리 구도/UI를 유지한
1600×1200 정수 2배 출력이다. G2는 전비 5000 숫자 패치만 있고 8인 부하·개체 풀/메모리
확장 증명이 없다. G3 16인과 G4 길찾기·AI는 구현 전이다.

진단 하네스는 lap146~147에서 원본 800×600 경로의 PS9→PS3, owned close→process exit→DLL
detach, summary 1, validator와 cleanup을 통과했다. 이후 pinned `ddraw.dll`/`dxwrapper.dll`과
config-only 후보를 만들어 SHA 고정, 외부/linked 경로 거부, private install/uninstall,
byte-exact restore, opt-in `ddraw=n,b`, module evidence를 구현했다.

lap154의 fresh opt-in runtime은 **client/capture 1600×1200, 논리 DirectDraw surface 800×600,
선변환 없는 `(184,560)` 입력으로 PS9→PS7→PS3**를 같은 run에서 처음 통과했다. 표시·구도·입력
핵심 경로는 성립했다. 그러나 종료 시 helper가 단일 게임 HWND/thread에 WM_CLOSE를 성공적으로
보냈는데도 process가 끝나지 않아 summary 0/DLL detach 미관측으로 BLOCKED했다. private config
복원과 owned cleanup은 PASS했다.

lap155 Opus/high는 이를 trace 관측 누락이 아닌 실제 종료 실패로 판정했다. close 뒤
`DDERR_SURFACELOST` 100건 후 약 78초 무증가했고 surface_release는 25건뿐이라, 정상 baseline의
11,667건 teardown에 진입하지 않았다. 다음 P1은 spin과 lock 교착을 구분하는 관측 1회다.

lap156 work는 P1 관측 3종(close 선기록, owned process tree liveness 2회, dxwrapper 로그 복사/SHA)을
추가하고 회귀/Fast를 통과했다. 그러나 direct script invocation의 새 PE32 close helper 빌드가
`ModuleNotFoundError: tools.win32_close_transport`로 실패해 prepare/runtime은 실행하지 않았고,
`loop/ESCALATE_SOL`로 승격했다.

lap157 middle은 이 실패가 **lap142에서 발생하고 lap143에서 실행으로 확정된 호출 경계 오류의 재발**임을
확인했다. `tools/win32_close_fixture.py:16`은 절대 package import를 쓰는데 `tools/__init__.py`도
sys.path bootstrap도 없어 direct script 실행은 항상 실패하고, `python3 -m tools.win32_close_fixture`는
성공한다. helper/transport/target source SHA 4종이 lap143 확정치와 동일해 코드 회귀가 아니다.
lap156의 관측 3종 구현도 코드/테스트로 정적 확인했다. 재발 원인은 handoff 카드에 빌드 명령이
없던 것이므로 카드에 모듈 실행 명령을 고정했고 `loop/ESCALATE_SOL`은 해소 처리했다.
다만 lap157 세션은 명령 실행 권한이 없어 helper build RC0/SHA와 Fast를 재실행하지 못했다.

lap158 work는 고정된 모듈 실행으로 fresh helper/target PE32 build와 diagnostic bridge build를 각각
RC0으로 통과시켰고, `make check` 186 passed 및 `SAFETY_PASS`를 재확인했다. 새 private
copy/prefix/display에서 `--dxwrapper-2x` trace를 정확히 1회 실행한 결과 client/capture
1600×1200, logical 800×600, scale 2×2, `(184,560)` 선변환 입력은 PASS했다. close transport도
소유 HWND/thread에 PASS했지만 finalization은 event 384, summary 0, process exit false로 90초
timeout BLOCKED했다. lap158은 이를 **A(spin/device-lost 재시도 계열)**로 분류했다.

lap159 middle은 이 run의 산출물을 독립 검수했다. 5/5 SHA 재현(verdict.json은 lap158 기록의
전사 오타 1문자), handoff 관측 3종 실재, close transport·cleanup·config 원복 모두 재확인 PASS다.
그러나 **A 라벨은 반증**했다. (1) `DDERR_SURFACELOST` 100줄은 전부 `20:28:42.737~.738`(약 1~2ms)에
몰려 있고 로그는 거기서 끝나 이후 약 55초간 wrapper 출력이 0줄이다 — "Lock 실패 지속"이 아니며
lap155·lap158이 둘 다 정확히 100줄인 것은 로그 상한 신호다. (2) close 이후 CPU는 315 jiffies/
5.045초 = 1코어 약 62%로, 자기 close 이전 평균(최소 약 69%) **이하**다. 폭주 spin이 아니다.
(3) thread 36→36으로 teardown 신호가 없다. (4) 이 run은 **PS3(인게임)에 실제 도달**했고
(`ps3_scene` 캡처 20:28:40; PS3는 종료가 아니라 live tick+active units 상태다) trace 마지막 16건은
teardown이 아니라 `surface_release(retire)`→`set_display_mode(800×600×8)`→`create_surface` 15건,
전부 `program_state=2`인 **재초기화**다. 즉 게임은 close에 반응해 PS3를 떠나 PS2로 재초기화한 뒤
평소 속도로 계속 돈다. 교착(B)도 아니다. 따라서 device-lost/reset config 옵션 승인은 **보류**하고,
설정 변경 없는 관측 probe P2를 승인했다.

lap160 work는 승인된 P2 관측을 새 private copy/prefix/display에서 정확히 1회 수행했다. helper/target
PE32와 diagnostic bridge build, `make check` 187 passed, safety는 PASS했다. 표시·논리 구도·입력은
같이 PASS했지만 finalization program_state 78표본이 모두 PS3였고, 두 finalization 캡처는 동일한
1600×1200 화면이었다. 프로세스는 36 threads로 살아 있었으며 close transport는 PASS,
summary 0/process exit false로 90초 timeout BLOCKED했다. 따라서 P2의 PS2 정착+살아 있는 화면
가설은 반증되었고, `loop/ESCALATE_SOL`로 승격했다.

lap161 middle은 lap160 산출물을 독립 검수했다. **5/5 산출물 SHA와 변경 source 2/2 SHA가 재현
일치**했고, P2 반증과 cleanup/config 원복은 확인 PASS다. 관측 코드도 건전하다: finalization
reader와 게임 내부 bridge는 **같은 주소 `0x4ED818`**을 읽고 전자는 `process_vm_readv`로 live
메모리를 읽는다. 그러나 lap161은 lap159가 붙인 두 해석을 **반증**했다. (1) trace 꼬리의
`program_state=2` 30건은 close 반응이 아니라 28ms짜리 **PS3 장면 로드**다(`set_display_mode`
800×600×8 + HUD/패널 `create_surface` 15건). 러너는 `ps==3 && tick>0`을 본 **뒤** close를 보내므로
이 구간은 close보다 앞이다. (2) wrapper 무출력 55초는 "Lock 실패 비지속"의 증거가 될 수 없다 —
`DDERR_SURFACELOST`는 lap155·158·160 **세 run 모두 정확히 100줄**인 per-callsite 로그 상한이며,
상한 이후의 침묵은 아무것도 말해주지 않는다. 그리고 두 가지 새 사실을 찾았다.
**A: PS3에서 DirectDraw 호출이 0건이다** — trace 384건 중 `program_state=3` 이벤트가 없고
`blt_fast` 256건은 PS7 로비에서 끝난다. 검은 화면은 "close 후 깨짐"이 아니라 **인게임 프레임이
한 번도 합성되지 않음**과 일치한다. **B: CPU는 분산이 아니라 단일 스레드 집중이다** — 5.066초
차분에서 tid 675202가 +306 jiffies(`S`→`R`), 나머지 35스레드 합계 +12 jiffies(프로세스 CPU의 약 96%).
따라서 누적된 "close→teardown 실패" 프레이밍 자체가 의심스럽고, 문제는 finalization이 아니라
**PS3 진입 직후의 렌더 경로**일 수 있다. lap161은 `loop/ESCALATE_SOL`을 해소하고 P3을 승인했다.

모델 라우팅은 Luna/high(work), Claude Opus5/high(middle/judge), Astra/medium(strategy)이다.
Astra는 큰 분기·반복 교착에서만 필요 시 high로 올리고 대략 10개 work/middle lap당 1회 이하로
운영한다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 메뉴/로비 2배 표시·논리 구도·입력·PS3 도달 PASS; PS3 렌더 미관측·정상 종료 FAIL |
| G2 8인 전비5000 안정성 | 미완료 | 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

work tier(Luna/high 또는 Claude Code `claude-sonnet-5`/high)가 승인된 **P3 관측 1건**을 구현하고
새 private copy/prefix/display에서 정확히 1회 실행한다. P3 = finalization 표본에 이미 같은 reader가
반환하는 `tick`(`0x8924B8`)을 함께 기록한다(1줄 + 단위 테스트 3케이스). 기준선은 이 run의
`capture.tick_after=2`다. **tick이 오르면** 게임 루프는 살아 있고 close가 삼켜진 것(close 의미론),
**tick이 2 부근에 멈춘 채** 그 스레드가 `R`로 CPU를 태우면 게임 루프 아래(wrapper/driver 렌더
경로)에 갇힌 것이다. 이 한 번의 관측이 남은 두 후보를 가른다. 상세 범위·분기·금지사항은
`docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`. 설정/종료 방식/timeout/좌표/baseline/
close 이전 시퀀스는 바꾸지 않는다.

## 지금 막힌 것 (Blockers)

- G1은 1600×1200 표시·입력·PS3 도달(메모리 상태 기준)은 성립했지만 native dxwrapper 경로에서
  프로세스가 종료되지 않아 제품 PASS가 아니다. lap161 이후 원인 프레이밍은 "close→teardown 실패"가
  아니라 **PS3 진입 이후 DirectDraw 호출 0건 + 단일 스레드 CPU 집중**이다. 아직 원인 미확정이다.
- PS3 인게임 프레임이 이 후보 설정에서 실제로 합성되는지는 **한 번도 시험된 적이 없다**. 러너가
  `tick==2`에 close를 보내기 때문이다. 이 dwell probe는 P3 결과 후 middle tier가 승인 여부를 정한다.
- `DDERR_SURFACELOST` wrapper 로그는 per-callsite 100줄 상한이다. 상한 이후의 무출력을 "호출이
  멈췄다"는 증거로 쓰지 않는다(lap159의 추론 오류).
- 원본/제품 EXE·DLL/assets/baseline/golden 변경 금지. 보호 EXE SHA는
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다.
- 실패 run/prefix/display 재사용, runtime 재시도, validator 완화, summary 합성 금지.
- builder `--out-dir`은 fresh parent 아래 존재하지 않는 child여야 한다.
- P3은 표본에 `tick` 추가 외 코드/종료 전략/후보 설정/close 이전 시퀀스를 바꾸지 않는다. dxwrapper config 프로필
  (`DdrawEmulateSurface`/`EnableWindowMode`/`FullscreenWindowMode` 포함) 변경은 승인되지 않았다.
  이미 통과한 2× 표시 결과를 오염시키며, lap159가 device-lost 기전을 반증했기 때문이다.
- close helper는 `python3 -m tools.win32_close_fixture`(모듈 실행)로만 빌드한다. direct script 실행은
  구조상 항상 `ModuleNotFoundError`이며 lap142·lap156이 같은 방식으로 막혔다. source를 고쳐 우회하지 않는다.
- lap158에서 lap157이 남긴 helper/Fast 실행 공백을 해소했다: 모듈 helper/bridge build RC0·PE32,
  `make check` 186 passed, `SAFETY_PASS`를 직접 확인했다.
- G2~G4와 사용자 마일스톤 승인은 미검증이다.
- lap160의 `loop/ESCALATE_SOL`은 lap161 middle 검수 완료로 **해소**했다(근거는 lap160·lap161 기록에
  보존). 필수 runtime gate는 여전히 BLOCKED이며 P3 실행 전까지 retry하지 않는다.

## 검증 상태

- lap146/147: diagnostic 800×600 runtime/finalization 및 독립 확인 PASS; Fast 173.
- routing/console Wine: 관련 19, Fast 173, Ruff/compileall/mypy/context/safety PASS.
- lap148: client 1600×1200·logical 800×600 PASS, 잘못된 ×2 입력 FAIL; Fast 177.
- lap150: 입력 계약/validator 회귀 targeted 80, Fast 179 PASS; 잘못된 source root로 runtime SKIP.
- lap152: 논리 입력으로 PS9→PS7→PS3/finalization PASS했으나 config 미설치로 client 800×600.
- lap154: pinned private install + `ddraw=n,b`, private ddraw module, client/capture 1600×1200,
  logical 800×600, PS9→PS7→PS3 PASS. finalization summary0/process exit false BLOCKED;
  targeted 91, Fast 182, safety/doctor/doctor-runtime PASS, config restore/cleanup PASS.
- lap155 Opus: 산출물·변경 SHA 9/9, module/config/display/input 재확인 PASS; 실제 종료 실패 판정.
- lap156 work: observation code/tests PASS; `make check` 186 passed, safety PASS; fresh bridge build
  PASS; close helper build FAIL (`ModuleNotFoundError`), prepare/runtime SKIP.
- lap157 middle: helper/transport/target source SHA 4종이 lap143 확정치와 일치(회귀 없음);
  import 경계 원인 확정, 관측 3종 구현 정적 확인 PASS; 실행 권한 부재로 build/Fast/runtime SKIP.
- lap158 work: module helper build RC0/PE32/SHA, bridge build RC0/PE32/SHA, `make check` 186 passed,
  safety PASS. fresh private `--dxwrapper-2x` runtime 1회는 1600×1200/800×600/2×2/input/close
  PASS, finalization summary0/process exit false BLOCKED; liveness CPU 3032→3347 및 `S`→`R`,
  `DDERR_SURFACELOST` wrapper evidence로 A(spin) 판정; config restore/cleanup PASS.
- lap159 middle: lap158 산출물 5/5 SHA 재현(verdict.json 기록은 전사 오타 1문자), 관측 3종 실재,
  close transport/cleanup/config 원복 재확인 PASS. A 라벨은 로그 시간분포·CPU 강도·thread 무변화·
  PS3 도달·재초기화 trace로 반증. 명령 실행 권한 부재로 `make check`/safety는 SKIP(코드 무변경).
- lap160 work: 승인된 P2 관측 코드와 단위 회귀를 추가했다. fresh helper/target PE32 및 bridge
  build RC0, `make check` 187 passed, `SAFETY_PASS`; 새 run `20260911_204410_673432_0`에서
  1600×1200/client·800×600/logical·2×2/input·close transport PASS. finalization PS 78회 모두
  PS3, 두 캡처 동일 완전 검은 화면, 36 threads 생존, summary 0/process exit false로 timeout
  BLOCKED. cleanup/config 원복 PASS. P2 가설 반증으로 `loop/ESCALATE_SOL` 생성.
- lap161 middle: lap160 산출물 5/5 SHA + 변경 source 2/2 SHA 재현 일치; P2 반증·cleanup/config
  원복 확인 PASS; 관측 reader가 bridge와 동일 주소 `0x4ED818`의 live 메모리를 읽음을 코드로 확인.
  lap159의 "close→PS2 재초기화"와 "wrapper 무출력=Lock 실패 비지속" 두 해석은 반증. 새 사실:
  PS3 구간 DirectDraw 이벤트 0건, CPU의 약 96%가 단일 스레드(+306 vs +12 jiffies/5.066s).
  명령 실행 권한 부재로 `make check`/safety/build는 SKIP(변경 source SHA가 lap160과 동일).
  공유 temp 권한 밖이라 PNG 재해시/열람 SKIP — 캡처 동일성은 evidence 기록 SHA로만 확인.
- lap161 uncommitted 문서 해시(`LOOP_ALLOW_COMMITS=0`): `docs/STATUS.md`는 본 갱신 후 값이라
  자기참조로 생략하고, `docs/history/laps/20260911_lap161_middle_g1_finalization_p2_recheck.md`
  `ef380ca5cb8d19a354c2e283ecfd93203a98d07849cf57c4293cef799e75bab3`,
  `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`
  `c544315e155de2e2de7d5ed09bd838d54568d439f4ba04e2a481f3d2471a8dec`.
  코드/바이너리/baseline/golden 변경 없음. `loop/ESCALATE_SOL`은 삭제(해소).
- pre-compaction snapshot SHA `16794f485dd9eeb44b6e072f91011b74be5217da8840fe8667a37dd4d3905086`.

## 바퀴 기록

- lap2~153: `docs/history/laps/`와 STATUS compaction 원문.
- latest snapshot: `docs/history/laps/20260911_status_lap156_compaction.md`.
- lap154 work: `docs/history/laps/20260911_lap154_luna_g1_dxwrapper_install_finalization_block.md`.
- lap155 review: `docs/history/laps/20260911_lap155_middle_g1_dxwrapper_finalization_verdict.md`.
- lap156 work: `docs/history/laps/20260911_lap156_luna_g1_finalization_observation_build_block.md`.
- lap157 middle: `docs/history/laps/20260911_lap157_middle_g1_close_helper_gate_reconfirmation.md`.
- lap158 work: `docs/history/laps/20260911_lap158_luna_g1_dxwrapper_finalization_spin_probe.md`.
- lap159 middle: `docs/history/laps/20260911_lap159_middle_g1_finalization_spin_verdict_recheck.md`.
- lap160 work: `docs/history/laps/20260911_lap160_luna_g1_finalization_observation_probe.md`.
- lap161 middle: `docs/history/laps/20260911_lap161_middle_g1_finalization_p2_recheck.md`.
- current escalation: 없음. lap160 `loop/ESCALATE_SOL`은 lap161 검수 완료로 해소.
- current handoff: `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`.
- model routing: `docs/history/20260911_model_routing_update.md`.
