# 2026-09-11 | lap 161 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, middle tier(진단·계획·확인).
  hands-on 게임/도구 구현은 하지 않았다. `loop/ESCALATE_SOL`(lap160)이 요청한 독립 검수다.
- 가설 / 사용자 관찰: 검수 가설은 "lap160의 P2 반증 판정과 그 근거가 산출물로 재현되는가"이다.
  부차 가설은 lap159가 lap158 trace 꼬리를 해석한 "close 반응 → PS3 이탈 → PS2 재초기화"가
  lap160 산출물에서도 성립하는가이다.
- 예상 PASS / FAIL 조건: 5종 산출물 + 변경 source SHA가 lap160 기록과 일치하고, finalization
  표본이 PS2 정착/살아 있는 화면을 보이지 않으면 P2 반증 확인. 관측 코드가 다른 주소나 캐시된
  값을 읽고 있으면 lap160 판정 자체를 무효로 돌린다. 어느 쪽도 G1 제품 PASS로 승격하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/도구 코드 무변경. 문서만 갱신:
  `docs/STATUS.md`, `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`, 본 파일.
  `loop/ESCALATE_SOL`은 검수 완료로 해소(내용은 lap160 기록과 본 문서에 보존). commit 없음
  (`LOOP_ALLOW_COMMITS=0`). 원본/후보 binary·assets·baseline/golden 미변경.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: lap160 run
  `20260911_204410_673432_0` 산출물만 읽었다. 새 run·prefix·display를 만들지 않았고 게임을
  실행하지 않았다. 보호 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  dxwrapper candidate `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`.
  G2~G4 fixture 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`(저장소 내부), `jq`, `grep`, 소스 정독만 수행.
  **5/5 SHA 재현 일치**: `evidence.json` `2bd4dec9…6f40`, `verdict.json` `1f909b63…9b48`,
  `provenance.json` `8eae90da…20f6`, `trace_raw.jsonl` `07b00fe8…4a23f`,
  `wrapper_logs/dxwrapper-syw2plus_original.log` `63cf81b9…284a6`.
  변경 source 2/2 일치: `tools/runtime_env.py` `fc875f2e…4de4`, `tests/test_runtime_env.py`
  `44c7376b…f888a`. 캡처 2장은 `evidence.finalization_screenshots` 기록상 동일 SHA
  `49affa64…a730ee`, `[1600,1200]`. 공유 temp는 이 세션 권한 밖이라 PNG 재해시/열람은 SKIP.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **P2 반증 확인 (PASS)**. `finalization_program_state` 78표본, `ps` unique=`[3]`, `error` 0건,
     구간 elapsed 9.602s→89.988s(표본 상한 120 미도달 = timeout이 끊은 것). PS2 정착 없음.
     캡처 2장은 서로 byte-identical이고 `ps3_scene`(`c1db93bf…`)과는 다르다 → close 이후
     약 71초간 **화면이 전혀 바뀌지 않았다**. 살아 있는 화면 아님.
  2. **관측 구현 해석 오류 없음 (PASS)**. `program_state_reader=lambda: state(False)`
     (`tools/runtime_env.py:2752`) → `patches.population.runtime_driver.state`
     (`:47`, `:51`)가 `process_vm_readv`로 **live** 메모리 `0x4ED818`을 읽는다. 게임 내부
     bridge도 같은 주소 `0x004ED818`을 읽는다(`tools/inmm_stub/direct_draw_trace.c:315`).
     두 수치는 직접 비교 가능하며 캐시/스텁이 아니다. `_owned_runtime_process_snapshot`
     (`:747`)은 owned root의 자손만 순회하고 전역 스캔/`pkill`이 없다. 상한 120/64 정상.
  3. **lap159의 "close→PS2 재초기화" 해석은 반증 (FAIL)**. trace 꼬리 30건(`program_state=2`,
     ts 501419487~501419515 = **28ms**)은 `set_display_mode(800×600×8)` + HUD/패널 계열
     `create_surface` 15건(832×600, 800×203, 800×20, 170×128, 300×100, 357×248, 640×480,
     212×62)이다. 이는 **PS3 장면 로드**이지 close 반응 teardown이 아니다. 프로그램 순서가
     이를 확정한다: 러너는 `ps==3 && tick>0`을 기다려(`:2733`) `ps3_scene`을 찍은 **뒤**에야
     close를 보낸다(`:2748`). PS3 진입에 필요한 800×600 backbuffer 생성이 이 30건뿐이므로
     이 구간은 close보다 앞이다. 그리고 78/78 표본이 3이므로 close 후 PS2 정착도 없다.
  4. **새 사실 A — PS3에서 DirectDraw 호출이 0건 (UNKNOWN 원인)**. trace 384건 중
     `program_state=3` 이벤트는 **하나도 없다**. `blt_fast` 256건은 PS7(로비)에서 끝나고
     (max ts 501416025) PS3 진입 이후 timeout까지 blt/blt_fast/flip이 전무하다.
     검은 화면은 "close 후 깨졌다"가 아니라 **인게임 프레임이 한 번도 합성된 적 없음**과 일치한다.
  5. **새 사실 B — CPU는 분산이 아니라 단일 스레드 집중 (FAIL for D)**. liveness 2표본
     (elapsed 9.601→14.667, 5.066s) per-thread 차분: tid 675202 `S`→`R` **+306 jiffies**,
     나머지 35스레드 합계 **+12 jiffies**. 즉 프로세스 CPU의 **약 96%가 한 스레드**이며
     1코어의 약 60%다. handoff 분기표의 D(분산 CPU)는 성립하지 않고 E(단일 스레드 + 정지 화면)
     쪽이다. 다만 close **이전** per-thread 표본이 없어 "이 집중이 평소와 다른가"는 미검증이다.
     단일 스레드 렌더 게임에서는 정상일 수도 있다.
  6. **lap159의 "wrapper 무출력 55초 = Lock 실패 비지속" 추론은 불건전 (FAIL)**.
     이 run도 `DDERR_SURFACELOST`가 **정확히 100줄**(20:44:42.999~43.000)이고 거기서 끝난다.
     lap155·lap158·lap160 세 run 모두 정확히 100줄인 것은 lap159 자신이 지적한 per-callsite
     로그 상한이다. 상한에 걸린 뒤의 침묵은 **호출이 멈춘 증거가 될 수 없다**. 따라서 "Lock 실패가
     지속되는가"는 지금도 **미결**이며, 이것이 남은 두 후보를 가르는 핵심이다.
  7. `make check` 187 passed / `SAFETY_PASS` / helper·bridge build RC0: **SKIP**. 이 세션은 명령
     실행 권한이 없다. 다만 두 변경 source SHA가 lap160 기록과 byte 단위로 일치하므로 lap160의
     기계 결과는 동일 입력에 대한 것이다. 재실행으로 확인한 것은 아니다.
  8. `verdict.json` 원문 재확인: `overall=BLOCKED`, `summary_count=0`, `event_count=384`,
     `process_exited=False`, cleanup `ok=true`, `global_kill_used=false`,
     `dxwrapper_config_restored=true`, `prefix_processes_after=[]` → cleanup/원복 PASS.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap160의 **결론(P2 반증)은 지지**하되 그
  근거는 lap160/lap159가 적은 것보다 강하고 방향이 다르다. 누적된 "close→teardown 실패" 프레이밍
  자체가 의심스럽다. 새 사실 A는 문제가 finalization이 아니라 **PS3 진입 직후의 렌더 경로**일
  가능성을 연다. 또한 러너는 `tick==2`에 close를 보내므로 이 후보 설정에서 게임이 인게임 프레임을
  그릴 수 있는지는 **한 번도 시험된 적이 없다**. G1~G4 제품 PASS, 마일스톤 승인 모두 없음.
  실제 원본/부하/멀티 증거 없음.
- 다음 한 가지: work tier에 **P3 관측 1건만** 승인한다 — finalization 표본에 이미 같은 reader가
  반환하는 `tick`(`0x8924B8`)을 함께 기록한다(1줄 + 단위 테스트). 기준선은 이 run의
  `capture.tick_after=2`다. tick이 오르면 게임 루프는 살아 있고 close가 무시된 것(=close 의미론),
  tick이 2 부근에 멈춘 채 그 스레드가 CPU를 태우면 게임 루프 아래(wrapper/driver)에 갇힌 것이다.
  이 한 번의 관측이 escalation이 남긴 두 후보를 **가른다**. 상세 범위·금지사항은
  `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`.
