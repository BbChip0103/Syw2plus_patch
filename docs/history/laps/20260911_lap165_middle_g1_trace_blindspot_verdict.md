# 2026-09-11 | lap 165 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle tier(진단·계획·컨펌)**.
  게임/도구 코드 hands-on 수정 없음. lap164 work tier 결과의 독립 검수와 판정, 다음 probe 승인만 수행.

- 가설 / 사용자 관찰: `loop/ESCALATE_SOL`(lap164)의 미결 —
  visible PS3 scene 캡처, finalization reader `ps=3/tick=16` 80초 고정, raw trace
  `program_state=3` 0건이 서로 모순된다(=의미 충돌). 이 셋이 **단일 설명으로 모순 없이**
  성립하는지, 아니면 실제 관측 모순인지 판정한다.

- 예상 PASS / FAIL 조건:
  - PASS = 세 관측이 계측 한계로 모두 설명되고, 충돌이 해소되며, 판별력 있는 probe 하나를 확정할 수 있다.
  - FAIL = 계측 한계로 설명되지 않는 실제 모순이 남는다 → Astra 승격.
  - 판정: **PASS**. 충돌은 관측 모순이 아니라 **계측기 3중 맹점**이었다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  게임/도구/테스트 코드 변경 **0**. 문서만 갱신(uncommitted):
  `docs/STATUS.md`, `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`,
  `docs/history/laps/20260911_lap165_middle_g1_trace_blindspot_verdict.md`(이 파일),
  `docs/history/laps/20260911_lap164_escalate_sol_original.md`(승격 원문 보존),
  `loop/ESCALATE_SOL` 해소(삭제).
  커밋 없음(`LOOP_ALLOW_COMMITS` 미설정, 저장소 커밋 0건). 이번 lap이 쓴 파일 해시:
  `docs/STATUS.md` `af5f03ebc19698584f502933c6348548ea42d9b2d21c99b54df31869fc99fa95`
  (lap160~163 서술을 전제 요약으로 압축하고 반증된 문장을 명시 정정, 131→149줄),
  handoff `1376540439cd7f414bb39b3f5facf88b35fcf26ca539447ac327316f597627c1`,
  lap164 escalation 원문 사본 `cb5eaeef2c4a25747ae1ce11c5e983c3ada5e03fed51dde2344f958a012e9e67`.
  (이 lap 기록 파일 자신의 해시는 이 줄을 쓰는 순간 바뀌므로 남기지 않는다.)
  검수 대상 source는 lap162~164와 **바이트 동일**:
  `tools/runtime_env.py` `f05b4c1c8e77f07a2b90a8fb6c833444ca090691531c2f6d7a91fb9cbc1750c8`,
  `tools/inmm_stub/direct_draw_trace.c` `533478e0ef886b4c82ad988d0c718c766ccc5a37b91012f76a4b641c0ab40419`,
  `patches/population/runtime_driver.py` `8c2465b8daa0a836168a92c8865c0f20e192ffd4a9ccbc7297511a3b0be82e94`.

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  dxwrapper pinned SOURCE `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`,
  approved CANDIDATE `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`.
  **새 게임 실행 없음. fixture 소비 없음.** lap164가 보존한 산출물과 저장소 정적 증거만 읽었다.

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `sha256sum` 으로 lap164 보존 산출물 **6/6 재현**(ESCALATE_SOL 기재와 일치):
    manifest `33686f12…8a4d6`, verdict `661cc7cec…5ce9d4e`,
    evidence `766111b1fd117f44e8d7d9a589e79dfaa8560767f4bd63f79e3d5087baa1e277`,
    provenance `85d0b1f60…9eba75f5`, raw trace `07e42ffa1…7d5ff5cbf`, install trace `bcea762e8…c4ac2056e3d`.
  - `sha256sum loop/ESCALATE_SOL` → `697997f5187a9c4e0a26966ec75dde263eb4de66cef0971acc511b9c0e185693`
    (해소 전 원문, 사본은 `docs/history/laps/20260911_lap164_escalate_sol_original.md`).
  - raw trace 이벤트별 상세 건수(`grep -c`): `install` 2, `direct_draw_create_ex` 1,
    `set_display_mode` 12, `create_surface` 39, `get_surface_desc` 39, `blt` 10,
    **`blt_fast` 256**, `flip` 0, `surface_release` 25, `overflow` 0, `aggregate` 0, `summary` 0.
    합계 384 = 기록된 `seq` 최대값. 마지막 줄의 `call_seq`는 **1047**이다.
  - 이번 후보 run의 wrapper 로그는 `wrapper_logs/dxwrapper-syw2plus_original.log`
    (mtime 2026-09-11 21:11, 165줄, SHA `039aaf81d4681d9886e178fccf7d897bcb4f5c7700565edfc2d2850c3b55bbde`).
    나머지 7개는 mtime 2025-05~2026-04의 source copy 잔재이며 이 run의 산출이 아니다.
  - PNG 재열람은 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/`가 이 세션의 허용 작업 디렉터리
    밖이라 **SKIP**. 대신 evidence.json에 기록된 캡처 해시를 대조했다.
  - `make check` / pytest 재실행은 비대화형 권한으로 **SKIP**. 이번 lap의 코드 변경이 0이고
    검수 대상 source 바이트가 lap164와 동일하므로 Fast 재측정 대상이 없다.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):

  **판정 1 — "PS3에서 DirectDraw 호출 0건"은 성립하지 않는다. (lap161 전제 2를 반증)**
  `tools/inmm_stub/direct_draw_trace.c`에는 세 가지 구조적 맹점이 있다.
  1. **per-method 상세 상한.** `:322`의 `g_method_detailed_counts[index] < TRACE_MAX_METHOD`,
     `:27`의 `TRACE_MAX_METHOD 256u`. 관측된 `blt_fast` 상세 건수는 **정확히 256**이다.
     상한 도달 후의 `blt_fast`는 줄로 기록되지 않고 `trace_method_aggregate`(`:271`)의
     메모리 집계 슬롯으로 들어간다.
  2. **집계는 정상 종료에서만 flush된다.** `trace_emit_aggregates()`/`trace_emit_summary()`는
     `:960~961`의 teardown(IAT 원복·vtable 원복 구간)에서만 호출된다. 이 run은 프로세스가
     끝나지 않았으므로(`process_exited=false`) 집계는 **한 번도 파일에 나오지 않았다**.
     실제로 `aggregate` 0줄, `summary` 0줄, `overflow` 0줄이다.
     집계 슬롯은 `program_state`를 키에 포함하므로(`:286`), PS3의 `blt_fast`가 있었다면
     그것은 **디스크가 아니라 프로세스 메모리 안에** 남아 있었다.
  3. **`Lock`/`Unlock`은 애초에 후킹 대상이 아니다.** `method_index`(`:178~188`)의 7개는
     `set_display_mode, create_surface, get_surface_desc, blt, blt_fast, flip, surface_release`뿐이다.
     즉 게임이 Lock에서 무한히 돌아도 이 trace에는 **한 줄도 남지 않는다**.
  마지막 기록 줄의 `seq=384` vs `call_seq=1047` 자체가 **663건이 기록되지 않았음**을 보여준다.
  따라서 `program_state=3` 0건은 "호출이 없었다"가 아니라 **"기록이 끝나 있었다"**로만 읽어야 한다.
  (같은 사실은 `docs/plans/20260911_lap129_g1_trace_finalization_repair_handoff.md:28`에
  이미 적혀 있었으나 lap159~161 해석 과정에서 유실됐다. 단, `blt`/`flip`은 상한에 여유가 있었고
  PS3 구간 기록이 0이므로 "**PS3의 표현 경로가 `blt`/`flip`을 쓰지는 않았다**"까지는 말할 수 있다.)

  **판정 2 — reader `tick`과 trace `game_tick`은 서로 다른 값이다. 비교하면 안 된다.**
  finalization reader의 `tick`은 `patches/population/runtime_driver.py:51`의 **`0x8924B8`**
  (게임 로직 tick / 생산큐 예약시각 기준, `analysis/memory_maps/original_qhd_probe_0910.md:59`)이고,
  raw trace의 `game_tick`은 `direct_draw_trace.c:316`의 **`0x009B5210`**
  (`inmm_stub.c:63` `GLOBAL_TICK`)이다. 후자의 마지막 관측값 `503019187`은 같은 줄의
  `ts_ms`(`GetTickCount`) `503019226`과 39ms 차이로, **밀리초 시계**에 가깝다.
  두 값을 같은 "tick"으로 놓고 모순을 논한 lap164 승격 문구는 **정정한다**.

  **판정 3 — 화면은 71초 동안 바이트 단위로 얼어 있었다. (lap164가 보고하지 않은 새 사실)**
  `evidence.json:1111~1130`의 finalization 캡처 2장은 SHA가 **완전히 동일**하다
  (`49affa6459ae21ecab2ba80e61b54f94400db56d407cde0e6f431e6751a730ee`,
  파일명 `…211125_…close_plus_5s…` / `…211236_…timeout_minus_5s…`, 71초 간격).
  그리고 이 해시는 PS3 scene 캡처(`af94e798…b294a`, `…211120…`)와 **다르다**.
  즉 PS3 장면 캡처 직후 화면이 한 번 바뀌고, 그 뒤 71초 동안 **단 1픽셀도 바뀌지 않았다**.

  **판정 4 — wrapper 로그에 정지 시점의 tight loop가 남아 있다.**
  이 run의 wrapper 로그는 165줄이고 마지막 100줄이 전부
  `m_IDirectDrawSurfaceX::Lock2 Error: failed to lock texture surface! DDERR_SURFACELOST`,
  **전부 같은 타임스탬프 `21:11:22.759`**(66~165줄)다. 직전 줄은 `21:11:14.955`이므로
  7.8초 공백 뒤 1ms 안에 100건이 터진 것이다. 100은 lap161이 확인한 per-callsite 로그 상한이므로
  그 뒤의 침묵은 여전히 증거가 아니다. 그러나 **1ms에 100건**은 상한과 무관하게
  **tight retry loop의 직접 증거**다. 로그는 21:11:22.759에서 멈추지만 프로세스는 21:12:4x까지 살아 있었다.
  같은 로그 21:11:14.3~14.9의 `ProxyQueryInterface … IID_IAMMediaStream` 5건은 run 로그의
  GStreamer-CRITICAL 5묶음과 같은 시각이다(미구현 미디어스트림 질의, 치명 아님).

  **종합 판정 — 충돌 해소(PASS).** 세 관측은 모순이 아니다.
  게임은 PS3 장면을 실제로 로드해 1600×1200으로 한 번 표시했고(캡처 `af94e798…`),
  로직 tick은 `2 → 16`까지만 오른 뒤 멈췄으며, 그 근방에서 wrapper가 `Lock2`/`DDERR_SURFACELOST`
  tight loop에 들어갔고, 화면은 그 뒤 71초 동안 바이트 동일했다. DirectDraw trace가 조용한 것은
  호출이 없어서가 아니라 상세 상한·미flush 집계·Lock 미후킹 때문이다.
  **분기 H(게임 루프가 진행하지 못함)가 성립한다. 분기 G(close 의미론)는 지지되지 않는다.**

  **남은 진짜 미결(UNKNOWN) — 인과 순서.** `finalization_program_state`의 `elapsed_seconds`는
  close가 아니라 **run `started` 기준**이다(`tools/runtime_env.py:982`, `:987`).
  캡처 파일명으로 역산하면 `started ≈ 21:11:11`, close ≈ `21:11:20.x`이므로
  첫 표본(9.341s, `tick=16`)은 close 직후, `Lock2` 폭주는 그보다 약 2.4초 뒤다.
  앵커 오차가 ±1초 수준이라 **"close가 정지를 유발했는가"와 "close와 무관하게 PS3에서 멈추는가"는
  아직 구분되지 않는다.** 이 후보 설정에서 게임이 인게임 프레임을 **연속으로** 합성할 수 있는지는
  지금까지 **한 번도 시험된 적이 없다**(러너가 `ps==3 && tick>0`을 보자마자 close를 보낸다,
  `tools/runtime_env.py:2738~2742`, `:2753`).

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 이번 lap은 실행/수정 0이므로 회귀 없음. cleanup/config 원복 PASS와 close 전달 PASS는 lap164 사실로 유지한다.
  - 위험: lap159~161이 만든 "PS3에서 DirectDraw 0건" 전제가 **두 바퀴 동안 후속 판단의 근거**였다.
    이 전제에 기대어 내려진 해석은 재검토 대상이다. 반증된 것은 전제이지 분기 H 자체가 아니다.
  - 위험: 계측기 맹점 3종은 코드 결함이 아니라 **설계된 상한**이다. 지금 상한을 올리는 것은
    이번 가설과 무관한 적층이므로 하지 않는다. 지연 카드 **D4**로 기록한다.
  - 사용자 마일스톤 승인 없음. G1~G4 전부 미완료. 프로세스 exit/skip/과거 PASS를 승인으로 쓰지 않는다.
  - `loop/ESCALATE_SOL`(lap164)은 이 판정으로 **해소**한다. 원문은 위 보존 파일에 남겼다.

- 다음 한 가지:
  work tier가 **P4 = PS3 dwell 관측**을 정확히 1회 수행한다. close를 보내기 **전에** PS3에서
  30초 머무르며 `ps`/`tick`을 1초 간격으로 표본하고 4장을 캡처해 해시로 프레임 변화를 측정한다.
  목적은 단 하나 — **정지가 close 때문인지, close와 무관한 렌더/시뮬레이션 정지인지 가른다.**
  범위·금지·성공식은 `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`가 기준이다.
  EIP/wchan probe는 이번에 승인하지 않는다(정지 callsite가 wrapper 로그로 이미 지목됐고,
  P4가 인과를 가른 뒤에 필요 여부가 정해진다).
