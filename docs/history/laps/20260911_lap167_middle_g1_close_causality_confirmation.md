# 2026-09-11 | lap 167 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / 중간 tier(진단·계획·확인).
  게임 코드 hands-on 수정 없음. 게임 실행 0회, 코드 변경 0.
- 가설 / 사용자 관찰: lap166이 승격한 **J(close 상관)** 판정과 fresh 산출물을 독립 재검수하고,
  다음 close-path probe 또는 수리 범위를 확정한다.
- 예상 PASS / FAIL 조건: 보존 산출물 SHA가 재현되고 dwell tick 계열·캡처 SHA·close 전달·finalization
  표본이 lap166 보고와 일치하면 J 확정. 불일치/의미 충돌이 남으면 승격 유지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 코드 변경 없음.
  `tools/runtime_env.py` `69b0f16253a850e02537d0d5dddbc97e43b7755cff447860a81e66914fdf0571`,
  `tests/test_runtime_env.py` `0a36a3d2096808884660740ca0c9c81d85a9e9b60af318a6c1f97742530e9bc1`
  — 둘 다 lap166 보고 값과 **바이트 동일**(2/2 재현). 문서만 갱신: 이 기록,
  `docs/STATUS.md`, `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`, `loop/ESCALATE_SOL` 해소.
  `LOOP_ALLOW_COMMITS` 미설정 → 커밋 없음, uncommitted 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — lap166 run copy
  `local/runtime/20260911_212619_1018825_0/game/syw2plus_original.exe`에서 **직접 재확인 일치**.
  dxwrapper source `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`,
  private candidate `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`.
  run copy의 현재 `dxwrapper.ini`는 `918e7043…` — **byte-exact 원복을 플래그가 아니라 해시로 확인**했다.
  환경: display `:91`, 1600x1200x24 / logical 800x600 / scale 2x2, default two-player random game,
  resource grant·control bridge·memory writes 모두 false. G2~G4 부하는 이 lap 범위 밖 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 게임 실행 없음. 보존 산출물 읽기/해시만 수행.
  `sha256sum`, `jq`, `grep`, `wc`로 `local/runtime/20260911_212619_1018825_0/output/g1_presentation_trace/`를 검수.
  재현 4/4: evidence `92d24f3066950d9360e01d8fcb0ecbe749954dc8fae63bdb76e7e2b34056fd5d`,
  provenance `c8352782091f1cdcc4737662adfaa2b60e2e90b019af4cd7a998ab58ce2dee9a`,
  verdict `a464b1386a56fc8aa8c5df510e558f306a0023920c86631ba0b1e2b7eacc3176`,
  raw trace `9fc3449827f8b2f19a5a3f7a3c032c3e958b520de2f4ccec55a9e962bb6ddbdd`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **재현 PASS**: dwell 표본 30건 전부 `ps=3`, tick `46…1013` 계열이 lap166 보고와 **완전 일치**,
    단조 비감소 true, `tick_error` 0, reader error 0, 간격 `elapsed 1.0…30.0`.
    tick 증가율은 `(1013-46)/29 ≈ 33.3 tick/s`로 **일정**하다(정체·불규칙 없음).
  - **재현 PASS**: dwell 캡처 4장 SHA 모두 상이(unique=4)하고 PS3 scene `09e69652…f394a16`과도 상이.
    close 전달 PASS(`requested_pid=276`, `matched_hwnd=0x00020056`, `matched_thread=280`, `post_result=true`).
    finalization 49건 전부 `ps=3`/tick `1026` 고정, `elapsed 39.368 → 89.412` = **50.04초 완전 정지**.
  - **재현 PASS**: wrapper 로그 165줄·`DDERR_SURFACELOST` 100줄·첫 `21:27:25.660`·끝 `21:27:25.661`.
    raw trace 384 events, `install=2/direct_draw_create_ex=1/set_display_mode=12/create_surface=39/`
    `get_surface_desc=39/surface_release=25/blt=10/blt_fast=256`, 마지막 `seq=384`/`call_seq=881`.
  - **판정: 분기 J 확정(CONFIRMED).** close 전 33.3 tick/s로 30초 진행 → close 후 50초간 정확히 0 tick.
    lap166 보고보다 강한 근거는 아래 신규 사실 3건이다.
  - **신규①(lap166 미보고)**: wrapper 로그는 `21:26:47.536`→`21:27:25.660` **38.1초 동안 완전 침묵**이다.
    건강한 30초 dwell 전 구간에 `DDERR_SURFACELOST`가 **0줄**이다. 즉 surface lost는 배경 상시 조건이
    아니라 **close 이후에 시작**한다. 100줄 상한 이전의 침묵이므로 이 침묵은 상한 artifact가 아니다.
  - **신규②(lap166 미보고, 교차 run)**: lap166 finalization 캡처 2장 SHA
    `49affa6459ae21ecab2ba80e61b54f94400db56d407cde0e6f431e6751a730ee`는 **lap164의 값과 바이트 동일**이다
    (`local/runtime/20260911_211043_913631_0/output/.../evidence.json`에서 직접 확인).
    lap164는 tick 16에서, lap166은 tick 1026에서 close했고 PS3 scene 캡처도 서로 다르다
    (`af94e798…b294a` vs `09e69652…f394a16`). **게임 상태가 전혀 다른데 정지 화면이 바이트 동일**이므로
    정지 프레임은 "마지막 게임 프레임"이 아니라 **내용과 무관한 고정(빈/클리어) 표면**이다.
    덧붙여 두 run의 메뉴/로비 캡처 4장(`d95c923e`,`be3a7556`×2,`f749183a`)도 교차 run 바이트 동일이다.
  - **신규③**: tight loop 스레드 `280`은 wrapper 로그 **1번째 줄부터** 등장하는 프로세스의 주
    DirectDraw 스레드다(close가 만든 스레드가 아니다). close helper가 잡은 `matched_thread=280`과 동일.
    → **메인 스레드가 `Lock2` 재시도에 갇히면 메시지 펌프가 돌아오지 못하고, 그래서 WM_CLOSE 종료가
    완료되지 않으며 프로세스가 계속 살아 있다.** 네 관측(tick 정지·화면 고정·retry 폭주·미종료)이
    하나의 메커니즘으로 묶인다.
  - **lap165 전제 재확인/정정**: trace의 `program_state`는 `direct_draw_trace.c:247,264,315`에서
    **reader와 같은 주소 `0x004ED818`**을 읽는다. lap165의 "서로 다른 값" 주의는 **tick에만** 해당하고
    (`trace 0x009B5210` vs `reader 0x8924B8`) `program_state`에는 해당하지 않는다.
    그럼에도 trace에 `program_state=3`이 0건인 것은 `blt_fast`가 정확히 256(상한)에 닿아 상세 기록이
    PS3 이전에 끝났기 때문이다. 마지막 이벤트는 `ps=2`/`seq=384`/`call_seq=881`로 **497건 미기록**이다.
    lap165의 결론(상한·미flush·Lock 미후킹)은 **유지**된다.
  - **신규④ — 대조군이 이미 이력에 있다**: `tools/runtime_env.py:2638`은
    `override = "ddraw=n,b" if dxwrapper_2x else "ddraw=b"`이다. 즉 `--dxwrapper-2x` 없이는 Wine 내장
    ddraw가 쓰이고 DxWrapper의 `m_IDirectDrawSurfaceX::Lock2`는 **존재할 수 없다**. lap146은 같은 close
    helper·같은 `--timeout 90`·같은 PID 276/HWND `0x00020056`·PS9→PS3로 `--dxwrapper-2x` **없이** 실행해
    process exit PASS / DLL detach PASS / `summary=1` / validator PASS를 받았다. 정지는 `--dxwrapper-2x`
    도입(lap148~) 이후에만 나타난다. 다만 lap146의 harness는 `runtime_env.py` `2609e7c2…`이고 현재는
    `69b0f162…`라 **단일 변수 대조가 아니다** → 그래서 P5를 현재 harness로 승인한다(아래).
  - **범위 판정**: 이 정지는 **표시(presentation) 결함이 아니라 종료(shutdown) 경로 결함**이다.
    `docs/DESIGN.md` §G1 완료 조건(16~22행)은 구도·비율·클릭 좌표·표시 정책이며 정상 종료를
    G1 합격 조건으로 적고 있지 않다. 동시에 실제 사용자가 창을 닫아도 같은 현상이 나므로
    **후보의 실제 결함이 맞고 무시 대상이 아니다.**
  - **SKIP**: `make check`와 `bash checks/safety.sh check` 재실행은 비대화형 승인 거부로 SKIP.
    이 lap은 코드 변경이 0이고 source 2/2가 lap166과 바이트 동일이므로 Fast 재측정 대상이 없다.
    lap166이 보고한 `192 passed`는 **이 lap에서 독립 재실행으로 확인하지 못했다**(미검증으로 남긴다).
  - **정정(lap166 보고)**: "3개 회귀 테스트"는 정확히는 **테스트 함수 2개**
    (`test_ps3_dwell_zero_does_not_read_or_capture`, `test_ps3_dwell_records_tick_samples_and_capture_failure`)
    이며 handoff의 3개 케이스(①기본0 비실행 ②tick 표본 ③캡처 실패 격리)를 모두 덮는다. 기능 결함 아님.
    미검 분기 1건: `tick`이 정수가 아닐 때의 `tick_error` 경로(`runtime_env.py:1120`)는 테스트가 없다.
    이번 run에서는 발생하지 않았다(`tick_error` 0). 소소한 커버리지 공백으로만 기록한다.
  - 제품 G1 완료 / 사용자 마일스톤 승인: **NO**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 게임 실행 0회, 코드 변경 0, 원본/제품/baseline/golden
  변경 없음. 보호 EXE·config 해시 직접 재확인. 남은 위험: (a) `Lock2` 무한 재시도의 주체가 게임 루프인지
  DxWrapper 내부인지 아직 안 갈렸다, (b) lap146 대조군이 구버전 harness라 단일 변수가 아니다,
  (c) `192 passed`가 이 lap에서 미재현이다. 사람 마일스톤 승인 없음.
- 다음 한 가지: **P5 대조 probe**(현재 harness, lap166 명령에서 `--dxwrapper-2x`만 제거)를 work tier가
  정확히 1회 실행해 정지가 dxwrapper native ddraw 경로에 귀속되는지 아니면 harness 회귀인지 가른다.
  상세 지시는 `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`.
  병행 카드 2(차단되지 않음): G1 실제 합격 증거(원본/후보 나란히 캡처 + 실제 입력)는 종료 수리를
  기다릴 필요가 없다 — dwell 창에서 수집 가능하다. 카드 2는 P5 결과 후 middle tier가 착수 승인한다.
