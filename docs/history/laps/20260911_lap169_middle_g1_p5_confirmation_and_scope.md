# 2026-09-11 | lap 169 | G1 P5 독립 검수와 수리 범위 판정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle tier(진단·계획·확인)**.
  게임 코드·하네스 hands-on 수정 없음. 이 바퀴의 산출물은 검수 판정과 승인된 카드다.

- 가설 / 사용자 관찰: lap168 work tier가 보고한 P5 builtin ddraw 대조군의 N 판정이
  산출물로 독립 재현되는가, 그리고 그 결과가 **DxWrapper close/finalization 수리 착수**를
  정당화하는가.

- 예상 PASS / FAIL 조건:
  - 검수 PASS = lap168이 기록한 산출물 SHA·`verdict.overall`·`process_exit`·`summary_count`·
    `winedlloverrides`·loaded ddraw module·tick 계열이 현물과 일치한다.
  - 수리 승인 = 결함의 **재시도 주체**(게임 vs DxWrapper 내부)가 증거로 확정돼 있다.
    확정돼 있지 않으면 수리는 승인하지 않고 판별 probe만 승인한다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  코드·테스트·바이너리·설정·좌표·timeout 변경 **0**. 문서만 추가/갱신:
  `docs/STATUS.md`, 본 이력, `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`(개정),
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`(신규), `loop/ESCALATE_SOL`(해소로 제거).
  모두 uncommitted (`LOOP_ALLOW_COMMITS` 기본0, 커밋/푸시 없음).
  `tools/runtime_env.py` = `69b0f16253a850e02537d0d5dddbc97e43b7755cff447860a81e66914fdf0571` (lap168과 동일, 무변경).
  커밋 불가 상태이므로 문서 해시로 이력을 보존한다(본 파일 자신의 해시는 이 줄 추가 전 값이라 생략):
  `docs/STATUS.md=6017a9e32a5e27f65f49ce0dc43ca98a3ca15a7521722794e9e32ff1459cb43e`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md=99e888a5ecfbf7421c3b757ccbb44e2251614950a606affa124c0ed1c898ec3c`,
  `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md=3fd5b8fe824a7edc2f06caa163ce32fa62c906deb00729ee91d3e571221e2877`.

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  후보 바이너리 없음. 이 바퀴는 게임을 실행하지 않았다(run 0). 기존 run 산출물만 읽었다.
  검수 대상 run `local/runtime/20260911_214253_1178505_0` (lap168 P5, builtin 대조군),
  교차 대조 run `local/runtime/20260911_212619_1018825_0` (lap166 후보, native ddraw).

- 실행 명령 / 로그 / 캡처 경로 및 해시: 읽기 전용 확인만 수행.
  - `sha256sum` 대조 4/4 일치:
    `evidence.json=309028386476de06ced251686444e04b7c8e7d9c282f7f52e7ed1dbcf7fc7e59`,
    `provenance.json=1b8df1e86bd8956da2bc3d9410afc0cebea83371646ae4a1a720cdac475e1c1b`,
    `verdict.json=319474f8fbe1f5e6d52443a71c75894b581e8ed83299bba60eeee30701138d55`,
    run game copy `dxwrapper.ini=918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`.
  - `verdict.json`: `overall=PASS`, `validator.status=PASS`, `event_count=651`, `errors=[]`,
    `cleanup.prefix_processes_after=[]`, `global_kill_used=false`.
  - `evidence.json`: `dxwrapper_config.enabled=false`, `winedlloverrides="ddraw=b"`,
    `loaded_ddraw_modules=["/usr/lib/i386-linux-gnu/wine/i386-windows/ddraw.dll"]` (**단일 항목;
    private DxWrapper 모듈 없음**), `trace_finalization.status=PASS`, `process_exit=0`,
    `summary_count=1`, summary `seq=651`/`call_seq=19786`/`thread_id=280`/`detach=complete`/`flush=complete`.
  - dwell tick 30개 `45…1012` 기록과 현물 일치. `trace_raw.jsonl` 줄 수 651 일치.
  - lap166 후보 로그 `dxwrapper-syw2plus_original.log`: 총165줄 중 `DDERR_SURFACELOST` 100줄 직접 재확인.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **lap168 P5 검수 = CONFIRMED.** 기록된 수치가 산출물과 일치하고, 단일 로드 모듈이
     Wine builtin ddraw임이 확인되므로 **N(귀속 확정)** 판정을 유지한다. close 후 미종료는
     DxWrapper native ddraw 경로에 귀속된다.
  2. **신규 정정 — "close 후 tick 정지"는 결함 신호가 아니다.** 정상 종료한 builtin 대조군도
     `finalization_program_state`가 `38.438s/39.440s/40.445s`에서 전부 `ps=3, tick=1022`로
     **고정**이고, 그 뒤 `process_exit=0`으로 정상 종료했다. 즉 WM_CLOSE 후 tick 정지는 양쪽
     백엔드 공통의 정상 teardown 거동이다. lap166/167이 정지 자체를 이상 신호로 기술한 부분은
     좁혀야 한다. **결함 signature는 tick 정지가 아니라 teardown 미완료**(summary/detach 없음,
     주 스레드 약96% CPU, 50초 무진전)다. 이 구분을 하지 않으면 work tier가 "close 후 tick을
     되살리는" 잘못된 방향으로 간다.
  3. **신규 관측 — 100줄은 상한일 가능성이 높다.** lap166 후보 wrapper 로그는 `21:27:25.661`
     `Lock2 … DDERR_SURFACELOST` 줄에서 **파일이 끝난다**(마지막 줄). 100줄이 약0.3초,
     마지막 여러 줄은 1ms 안에 몰려 있다. 로그가 스스로 멈춘 뒤에도 주 스레드는 약96% CPU로
     50초를 더 돌았다. 따라서 재시도는 100회로 끝난 것이 아니라 **로그 상한 뒤로 계속됐다고
     보는 편이 증거에 맞다.** "정확히 100회 재시도"로 읽으면 안 된다.
  4. **신규 관측 — 현재 trace 훅으로는 M을 반증도 입증도 할 수 없다.**
     `tools/inmm_stub/direct_draw_trace.c:732` `hook_blt_fast`를 포함한 모든 표면 훅은
     `record->original_*(...)`를 **먼저 호출하고 반환 뒤에** 기록한다. 그러므로 **반환하지 않는
     호출은 trace에 한 줄도 남지 않는다.** 게다가 `Lock`/`Unlock`은 아예 후킹 대상이 아니다
     (훅 대상은 GetSurfaceDesc/Blt/BltFast/Flip/Release). 이 두 성질 때문에 "게임이 Lock2를
     수천 번 재호출" 과 "DxWrapper 내부가 한 번의 Lock2 안에서 스핀"이 현재 계측에서
     **완전히 동일하게 보인다**(둘 다 trace 무음).
  5. **수리 범위 판정 = 수리 착수 NOT APPROVED.** 근거: (a) 재시도 주체가 4번 때문에 아직
     미분리다. (b) 저장소에 DxWrapper 소스가 없다. 보유한 것은 `patches/resolution/dxwrapper_config.py`의
     **고정 4키 프로필**(`Dd7to9=1`, `DdrawUseNativeResolution=1`, `DdrawIntegerScalingClamp=1`,
     `DdrawMaintainAspectRatio=1`)뿐이고, 이 중 종료 경로를 겨냥한 knob은 없다. `Dd7to9`를 끄면
     2× 경로 자체가 사라지므로 수리가 아니다. 즉 지금 "수리"를 승인하면 근거 없는 추측 패치이거나
     승인되지 않은 프로필/바이너리 확장이 된다. → **AGENTS.md의 "무단 전제 금지"에 걸린다.**
  6. `make check` / `checks/safety.sh check` = **SKIP(권한)**. 비대화형 세션에서 승인 요구로
     실행이 거부됐다(lap167과 동일 제약). 이 바퀴는 코드 변경이 0이고 `tools/runtime_env.py`
     SHA가 lap168과 동일하므로, lap168의 `192 passed` / `SAFETY_PASS`가 현재 트리의 마지막 유효
     Fast 근거다. **이 SKIP을 PASS로 승격하지 않는다.**

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 이 판정은 2단 기술 검수이며 **G1 제품 합격도 마일스톤 승인도 아니다.** 사용자 승인 없음.
  - 남은 위험: close/finalization 결함은 실제 사용자 창 닫기에서도 재현되는 **실제 결함**이며
    보류일 뿐 폐기가 아니다. G1 출하 전 반드시 해소돼야 한다.
  - 남은 위험: `docs/DESIGN.md` §G1(21행)이 요구하는 원본/후보 나란히 캡처 + 실제 입력 증거는
    lap148~168 사이 **한 번도 생산되지 않았다.** 원본 쪽 입력 증거조차 lap73에서 production
    fail-closed로 중단돼 `drag_select`/`minimap`까지 도달한 적이 없다.
  - 검수자 한계: 이 바퀴는 기존 산출물 재계산만 했고 새 게임 run으로 재현하지 않았다.

## 부록 — 해소된 `loop/ESCALATE_SOL` 원문 (lap168 work → middle)

lap169 middle 판정으로 해소했으므로 파일은 제거하되 원문은 아래에 보존한다.
요청 3건에 대한 답: (1) N 독립 확인 = CONFIRMED. (2) wrapper 수리 카드 = **NOT APPROVED**,
대신 P6 판별 probe를 정의해 2순위 주차. (3) 카드2 = **Stage A 착수 승인**, Stage B는 다음 middle 확인 뒤.

```
# lap168 work → middle-tier escalation

## reason

P5의 단일 관측은 N으로 확정되었고, 다음은 DxWrapper native ddraw close/finalization 수리 범위를 정하는 middle-tier 경계다. 일반 work tier가 임의로 수리하거나 G1 카드2를 시작하면 handoff 범위를 넘는다.

## evidence

- Run: `local/runtime/20260911_214253_1178505_0`
- Fresh build parent: `/tmp/syw2plus_lap168_p5.1DTtph`
- `--dxwrapper-2x` 제거, `ddraw=b`, loaded module `/usr/lib/i386-linux-gnu/wine/i386-windows/ddraw.dll`
- PS3 dwell 30초: 30/30 samples, tick `45→1012`, 캡처 4/4 unique
- owned WM_CLOSE: RC0, PID276, HWND `0x00020056`, thread280, `post_result=true`
- finalization: `process_exit=0`, `summary_count=1`, validator PASS, raw trace 651, last `seq=651`/`call_seq=19786`, detach/flush complete, prefix processes `[]`
- `DDERR_SURFACELOST` lines: 0 across copied `dxwrapper*.log` files; direct DxWrapper module was not loaded
- Fast: `make check` 192 passed; `bash checks/safety.sh check` SAFETY_PASS
- Detailed record: `docs/history/laps/20260911_lap168_luna_g1_p5_builtin_ddraw_control.md`

## requested middle-tier handoff

1. Independently review the P5 artifacts and confirm N / DxWrapper attribution.
2. Define and approve one bounded next card for the DxWrapper close/finalization defect, including exact old-byte/source SHA, allowed files, rollback, and regression/dual-backend validation.
3. Decide separately when G1 card2 (original/candidate side-by-side plus real input evidence) may start.

## stop condition

Work tier stops here. No retry, code/binary/config change, G1 milestone PASS, or user approval is claimed.
```

- 다음 한 가지: **G1 카드2 Stage A 착수를 승인한다** —
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`. work tier는 하네스/테스트만 바꾸고
  게임 run은 하지 않는다(Stage B는 다음 middle 확인 뒤). close/finalization은 **P6 판별 probe**로
  재정의해 2순위로 주차했다(`G1_DXWRAPPER_FINALIZATION_HANDOFF.md` lap169 절). 활성 카드 2개.
