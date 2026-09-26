# 2026-09-11 | lap 159 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle tier
  (진단·계획·컨펌). 게임 코드/하네스 코드는 수정하지 않았고 runtime도 실행하지 않았다.
  제품 마일스톤 승인은 하지 않았다.
- 가설 / 사용자 관찰: STATUS "다음 한 가지"에 따라 lap158의 새 private runtime evidence를 독립
  검수하고, 분기 **A(spin/device-lost 재시도 계열)** 판정이 산출물로 실제 성립하는지 확인한 뒤
  device-lost/reset 처리 옵션 한 개의 다음 probe 범위를 승인할지 결정한다.
- 예상 PASS / FAIL 조건: lap158이 기록한 산출물 SHA가 재현되고, handoff 관측 3종이 evidence.json에
  실재하며, liveness/wrapper log/raw trace가 A 분기의 두 기준(① 살아서 CPU 시간 증가,
  ② Lock 실패 계열 **지속**)을 모두 만족하면 A를 확인하고 config 옵션 1개를 승인한다.
  둘 중 하나라도 불성립이면 승인하지 않고 원인을 재분류한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 코드/테스트/baseline/golden/원본·후보
  binary·config 무변경. 이번 바퀴 변경은 문서 3개뿐이다 — `docs/STATUS.md`,
  `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`, 본 기록.
  commit/push 없음(`LOOP_ALLOW_COMMITS=0`, uncommitted 보존).
  검수 대상 하네스 fingerprint는 lap158 기록치를 그대로 인용한다(`tools/runtime_env.py`
  `25fc64e6…`, `tests/test_runtime_env.py` `7654052e…`). 본 세션은 재해시하지 않았다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 검수 대상 run
  `20260911_202808_512099_0`의 `manifest.exe_sha256`는
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`로 STATUS 보호 pin과 일치
  확인. screen `1600x1200x24`, timeout 90, `diagnostic_bridge_overridden=true`,
  fixture `new private copy; default two-player random game`,
  `synthetic=false / memory_writes=false / control_bridge=false / resource_grant=false`.
  G2~G4 fixture 없음. 본 바퀴는 새 runtime을 실행하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 읽기 전용 검수만 수행했다.
  `sha256sum`으로 `local/runtime/20260911_202808_512099_0/output/g1_presentation_trace/`의 5개
  산출물을 재계산한 결과 `evidence.json bb6892d8…`, `provenance.json fc754f1f…`,
  `trace_raw.jsonl 96ca0f41…`, `trace_install.jsonl fa03ab8f…`는 lap158 기록과 **정확히 일치**했다.
  `verdict.json` 실측은 `5c54c25b05976edb4652c18703a7b47d922c1698df44ce8a79078175736261c3`이고
  lap158 기록은 마지막 1문자가 누락된 63자였다 — 전사 오타이며 prefix 일치, 내용 회귀 아님.
  `wrapper_logs/` 8개 파일 존재·해시 확인, 핵심 로그
  `dxwrapper-syw2plus_original.log` `509abf67…` 일치(165줄).
  `make check`와 `checks/safety.sh check`는 **SKIP** — 이번 세션에 명령 실행 권한이 없다
  (lap157과 동일 제약). 본 바퀴는 코드 무변경이므로 Fast 위험 없음이나 근거로 쓰지 않는다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **산출물 무결성 PASS.** 5/5 SHA 재현(verdict.json은 전사 오타 1문자).
  - **handoff 관측 3종 구현 PASS.** `evidence["trace_finalization"]["close_transport"]`가 대기 전에
    기록되고(`tools/runtime_env.py:963-968`), `finalization_liveness` 2표본
    (`:924-941`), `wrapper_logs` 복사(`:991-1005`)가 모두 실재한다.
  - **close transport PASS 재확인.** `requested_pid=276`, `matched_hwnd=0x00020056`,
    `matched_thread=280`, `match_count=1`, `post_result=true`, `post_error=0`, RC0, 0.077초.
  - **cleanup/restore PASS 독립 확인.** `verdict.cleanup.ok=true`,
    `dxwrapper_config_restored=true`, `global_kill_used=false`, `prefix_processes_after=[]`.
    private `game/dxwrapper.ini`를 직접 읽어 stock 원본 내용(`Dd7to9=1`,
    `DdrawUseNativeResolution=1`, override 전부 0)임을 확인했다.
  - **A 분기 기준 ①(살아있음 + CPU 증가) 확인.** sample1 t=9.354s `S` utime2650/stime382,
    sample2 t=14.399s `R` utime2962/stime385. 5.045초에 315 jiffies = CPU 3.15초
    ≈ **1코어의 약 62%**. 교착(B)은 반증된다.
  - **A 분기 기준 ②(Lock 실패 계열 지속) FAIL — 반증.** wrapper log의 `DDERR_SURFACELOST`
    100줄은 전부 `20:28:42.737`~`.738`, 즉 약 1~2ms 구간에 몰려 있고 로그는 거기서 끝난다
    (165줄, 마지막 줄 `20:28:42.738`). 이후 timeout까지 약 55초 동안 wrapper 출력이 **0줄**이다.
    lap155와 lap158 모두 정확히 100줄이라는 사실은 반복 메시지의 **per-callsite 로그 상한**
    신호이지 "루프가 두 번 다 정확히 100회 돌았다"는 뜻이 아니다. 따라서 로그는 close 이후
    재시도 루프가 **계속된다는 근거가 되지 못한다**.
  - **CPU 강도 반증 보강.** 3032 jiffies(=CPU 30.3초)가 sample1 시점까지 누적됐다. 프로세스가
    run 시작(20:28:08)보다 일찍 시작할 수 없으므로 close 이전 평균은 **최소** 1코어의 약 69%이며
    실제 기동이 더 늦었다면 그보다 높다. 즉 close 이후의 62%는 자기 평소 소비율 **이하**다.
    폭주 재시도 spin이라면 1코어 100% 이상을 기대해야 하므로, 관측은 "평소처럼 돌고 있다"에
    가깝지 "device-lost 재시도로 폭주한다"에 부합하지 않는다.
  - **thread 수 36→36 무변화.** 두 표본 모두 36 스레드다. 실제 teardown 진입이었다면 스레드가
    줄기 시작할 것으로 기대되나 전혀 줄지 않았다.
  - **핵심 신규 사실 — PS3(인게임)에 실제 도달했다.** evidence.json screenshot 목록에
    `…_ps3_scene_1789126120490103518.png`(20:28:40, 1600×1200)가 존재한다.
    `runtime_env.py:1923/2252`가 PS3를 "live tick + active units"로 검증하므로 **PS3는 종료
    상태가 아니라 인게임 상태**다. lap158 기록과 STATUS가 이 run을 "PS9→PS7"로만 적은 것은
    **과소기록**이며 정정한다(PS9→PS7→lobby selector→solo→PS3).
  - **핵심 신규 사실 — 마지막 trace 16건은 teardown이 아니라 재초기화다.** `trace_raw.jsonl`
    seq368~384는 `surface_release(lifetime_action=retire)` → `set_display_mode(800×600×8)` →
    `create_surface` 15건(800×600 backbuffer, 832×600, 800×203, 800×20, 170×128×4, 300×100,
    357×248, 640×480, 212×62)이고 전부 `program_state=2`다. 즉 게임은 close에 **반응해서**
    PS3를 떠나 display mode를 다시 세팅하고 surface 세트를 **새로 만들었다**.
    `DDERR_SURFACELOST` 버스트는 이 display mode 변경/device reset의 **정상적 귀결**이다.
  - **종합 판정:** B(교착)는 반증, A의 "살아있다"는 성립, 그러나 A가 지목한 **기전
    (device-lost 재시도 루프)은 근거 불충분**이다. 증거가 가리키는 것은
    "WM_CLOSE가 애플리케이션 종료가 아니라 **상태 전이**(PS3 이탈 → PS2 재초기화)로 처리됐고,
    게임이 PS2에서 평소 속도로 계속 돌며 teardown에 들어가지 않는다"이다.
  - 그러므로 **device-lost/reset config 옵션 승인은 보류(거부)한다.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본/제품 binary, baseline/golden, 하네스
  코드 무변경. validator/timeout/summary 요구/좌표/wrapper profile 무변경. G1 제품 PASS 아니며
  정상 teardown·summary 1·DLL detach·validator는 여전히 미충족이다.
  남은 불확실성: (a) 로그 100줄 상한은 dxwrapper 동작에서 직접 확인한 것이 아니라 lap155·lap158의
  동일 관측과 1~2ms 집중이라는 정황으로 추론했다 — P2가 이를 관측으로 대체한다.
  (b) close 이후 trace event가 0인 것은 bridge가 호출을 전량 기록하지 않으므로(seq384 대비
  call_seq986) "DirectDraw 호출이 없다"의 증거로 쓸 수 없다. (c) PS2의 의미는 아직 미확정이다.
  본 판정 자체도 다음 새 세션이 독립 검수 대상이며 사용자 마일스톤 승인은 없다.
  `loop/ESCALATE_SOL`은 만들지 않았다 — 이 충돌은 STATUS가 본 middle tier에게 배정한 검수
  과제 자체이고 증거로 해소했으며, 마일스톤 경계도 아니다.
- 다음 한 가지: 승인한 **P2 관측 1회**를 work tier(Luna/Sonnet5)가 수행한다. 가설은
  "WM_CLOSE는 종료가 아니라 PS3 이탈 → PS2 재초기화로 처리되고 프로세스는 PS2에서 평소대로
  계속 돌아 teardown에 진입하지 않는다"이며, 관측 3종(finalization 구간 program_state 주기
  기록, 대기 중 캡처 2장, `/proc/<pid>/task/*` 스레드별 CPU 귀속)만 추가한다. 설정/종료 방식/
  timeout/판정 기준은 바꾸지 않는다. 상세는
  `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`.
