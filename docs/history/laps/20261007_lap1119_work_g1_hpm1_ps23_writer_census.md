# 2026-10-07 | lap1119 | G1 work — H-PM1 PS23 전환 writer census (저장 창 닫힘 뒤 coverage 손실 귀속)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 제품 변경 = 진단 옵트인 2건(아래), 커밋 0.
- 입력: STATUS 다음 한 가지(lap1118 사전등록 §5 `20261007_lap1118_middle_g1_hpm0_attribution_hpm1_preregistration.md`). INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP`·`ESCALATE_SOL` 없음. 이전 바퀴 검수: lap1118 §1 수치(복귀 stale 95,366/95,336, 손실 44,040/44,005)를 이번 run 3개의 PM0 수치(첫 present HD 79.94~80.08%·정착 p50 90.765~90.771%)가 재현해 일치 확인.
- 가설(사전등록 H-PM1): PS23 하위 화면 전환 첫 present에서 미러 밖 writer가 사각형을 다시 써서 stale→coverage 해제.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` MATCH(읽기만, objdump 역어셈블 포함). 활성 플레이어 8 records(부하 증거 아님), 새 게임 경로(PS9→PS7→PS5→PS3→Esc PS23), 저장 실행 없음.

## 변경 파일(uncommitted)

- `tools/inmm_stub/g1_screen_watch.h`·`.c`: **PM1-0** 옵트인 `SYW2_G1_SCREEN_WATCH_STATE`(값 정확히 `23`만 PS23, 없으면/그 외 3 = 현행 동작 불변; `g1_screen_watch_state_parse`·`g1_screen_watch_present_ordinal` 순수 헬퍼 — PS23은 drift present 카운터가 안 올라가므로 watch 자체 present 카운터 사용). **PM1-1b** `g1_screen_watch_on_surface_call`: PS23 watch가 무장된 때만 ddraw `Blt`(kind 1)·`BltFast`(kind 2) 호출을 (kind·caller EIP·대상/원본 surface·rect·x/y·flags) 키로 최대 48행 표에 접고 첫/마지막 watch present·호출 수를 하트비트마다 `{"t":"q"}` 행으로 기록(읽기 전용, 게임 버퍼 쓰기 0, 꺼져 있으면 즉시 return).
- `tools/inmm_stub/direct_draw_trace.c`: `hook_blt`·`hook_blt_fast` 진입에서 위 함수 호출(반환 주소 포함), `#include "g1_screen_watch.h"`.
- `tools/g1_saved_scene_probe.py`: `--screen-watch-state {3,23}`(`--screen-watch` 필수, 후보 lane env `SYW2_G1_SCREEN_WATCH_STATE`), `--new-game-path` 분기가 후보 lane에만 `layer_drift`·`screen_watch`·`screen_watch_cache`·`screen_watch_state`·`drift_samples`를 넘기고 `new-game-path-result.json` lane 요약에 `screen_watch`(경로·SHA·bytes) 추가. 기존 NG3~PM0 경로 불변.
- `tests/test_g1_screen_watch.py`: 4건 추가(RED→GREEN: 상태 헬퍼·present 훅 게이트·harness 옵션/배선·surface call 표). `.venv/bin/python -m pytest` screen_watch+new_game_path+saved_scene_probe **261 passed**, `make lint`·`make typecheck` PASS. (시스템 `python3`는 PIL에 `get_flattened_data`가 없어 saved_scene_probe 8건이 환경 차로 실패 — 프로젝트 검사는 `.venv`.)
- 파일 SHA(앞 12자): probe `54c8abbbeebf`·test `0b6d92d01275`·watch.c `c59525803859`·watch.h `3470eff2c099`·direct_draw_trace.c `2cedc853f92f`.

## PM1-1 측정 (격리 run 3회, `--hd-source scale2x --new-game-path --new-game-start --new-game-menu --layer-drift --screen-watch --screen-watch-state 23 --drift-samples "260,250;530,250;400,380"`)

- run a = PM1-0만 있는 DLL(표본 EIP만), run b·c = surface call 표 포함. 공유 temp `20261007_lap1119_work_hpm1/pm1_{a,b,c}/`(artifact `new-game-path-result.json` a `c7116544e35a…`·b `68347d032f6c…`·c `e5cf453b527b…`, `candidate/screen_watch.jsonl` a `a5ffeedca2f5…`·b `203de6d23e47…`·c `350683132301…`, `trace_raw.jsonl` a `88f8589b362a…`·b `d64d544614d3…`·c `d20f520bbd77…`, 로그 `logs/gates/lap1119-pm1-{a,b,c}.log` a `ca2d8e5e96e7…`·b `e3a00a317a3c…`·c `ec75d31304ab…`, 모두 exit 2 = 최상위 PM0 gate FAIL이 그대로 재현). 분석 스크립트 `<temp>/scripts/an1~an4.py`(`136ae8cef4ab`·`51437f1cf999`·`06c5d6b9876c`·`aecd33c88805`). 상관: watch `p` = trace `seq − (첫 PS23 mirror present seq) − 1`(저장 창 닫힘 present: a 4964→p2602, b 4651→p2329, c 4695→p2336).
- watch 자체 상태: selftest PASS 3/3, arm fail 0, raw dropped 0(run a만 raw 한도 20,000 근접, 닫힘 전환 구간은 포함), PM0 수치 재현(저장 창 열림 1 present HD 89.11~89.18%, 닫힘 첫 present HD 79.94~80.08%, 정착 PS23 p50 90.765~90.771%, V1/안전 7종/fallback 0·dropped 0·scale2x PASS).
- **writer(표본 A 왼쪽 띠 (260,250)·B 오른쪽 띠 (530,250)):** 3/3 run 모두 PS23 전 구간에서 **같은 두 곳만** 쓴다.
  1. 모든 present(저장 창 안팎·닫힘 전환 포함) 비-present 스레드 tid 288의 `ucrtbase.dll` memcpy `0x7AF3E6C9`(A)·`0x7AF3E6CE`(B,C) — 값은 항상 배경 값(A 242·B 244·C 98).
  2. 저장 창이 떠 있는 동안만(a p1137..2601·b p885..2328·c ~889..2335, 구간 길이 = 저장 창 window) present 스레드 tid 280의 `0x004662DE`(`0x466280` 패널 블록 복사, 반환 `0x466D50`←`0x404C6C`←`0x4D66A0`…) — A 208·B 243(저장 창 패널 값). **닫힘 전환 present(p2602/2329/2336) 및 그 뒤 정착 PS23에서는 A·B에 `0x4662DE` 쓰기 0**(마지막 present 번호에 몰린 ~215건은 PS3 복귀 뒤 월드 재그림).
  3. 표본 C(메뉴 패널 (400,380)): `0x4662DE`가 저장 창 열림 구간뿐 아니라 닫힘 **다음** present(p2603 등)부터 매 present 다시 쓰인다 — 닫힘 present 자체에는 C 쓰기도 tid 288 배경 쓰기뿐(메뉴 패널 복사가 그 present에는 일어나지 않음, trace `partial_copy_calls`도 그 present는 불변·다음 present +1).
- **ddraw 호출 표(run b·c 동일, PS23 전 present, distinct 2·overflow 0):**

| # | kind | caller | 대상 | 원본 | x,y | rect | flags | 호출 수 |
|---|---|---|---|---|---|---|---|---|
| 0 | BltFast | `0x00493CCB` | `0x01E6D560`(832×600 sysmem, 게임 화면 버퍼) | `0x01E6D8F0`(800×600 sysmem offscreen) | 0,0 | **원본 rect NULL(전면)** | 16(DDBLTFAST_WAIT) | 3200(b)·3450(c) = 매 present, p0..마지막 |
| 1 | BltFast | `0x00469379` | `0x01E71720`(primary) | `0x01E6D560` | 0,0 | [0,0,800,600] | 16 | 3200(b)·3450(c) = 매 present |

- **역어셈블(원본 EXE, 읽기 전용 `objdump -d -M intel --start-address=0x493C40`):** `0x493CA0`에서 시작하는 PS23 프레임 함수 — `[0x66976C]`≠0 가드 → `mov edx,[0x104FB30]`(원본 surface)·`mov eax,[0x104FB2C]`(대상 surface 객체)·`mov ecx,[eax]`(vtable) → `push 0x10; push 0; push edx; push 0; push 0; push eax; call [ecx+0x1C]`(vtable 7 = `IDirectDrawSurface7::BltFast(dest, x=0, y=0, src, rect=NULL, DDBLTFAST_WAIT)`), 반환 `0x493CCB`. 그 직후 `movsx eax, word [0x104FD38]`(PS23 하위 상태 1000..1009) → `eax -= 0x3E8`, `cmp eax,9; ja`, `jmp [eax*4+0x493F30]` 점프 테이블로 하위 상태별 패널 그리기(`0x493D05`의 `0x494390`·`0x494790` 등)로 분기. 하위 상태 0x3E9·0x3EB·0x3ED 등이 보이고, 저장 창 열고 닫기는 이 변수 전이다. `0x4662DE` 호출 스택에도 `0x493CCB`·`0x493D4A`·`0x493D05`가 나타난다(그 함수 안에서 패널 복사 호출).
- **writer 귀속 결론:** 닫힘 전환 present에서 띠 사각형을 다시 쓰는 것은 **전환 전용 writer가 아니라 PS23 프레임 함수 `0x493CA0`이 매 present 맨 앞에서 하는 전면 배경 복원 BltFast(`0x493CC8`, 원본 surface `0x01E6D8F0` → 화면 버퍼, wined3d CS 스레드가 `ucrtbase` memcpy로 수행)** 이다. 이 복원은 저장 창이 떠 있는 동안에도 매 present 같은 값(242/244/98)으로 먼저 쓰고, 저장 창 패널 블록 복사(`0x466280`)가 그 위에 덮는다. 저장 창이 닫히면 패널 복사가 그 띠에 더는 오지 않고 배경만 남아, 미러의 expected(저장 창 패널 값)와 어긋나 stale이 되고 coverage가 해제된다(사전등록 §3 후보 중 (iii)에 가깝다; **(ii) `0x466280` 조기 return은 배제** — 닫힘 present에 `0x4662DE` 쓰기 자체가 없고 다음 present에 정상 호출됨).

## 판정

- **PM1-0 PASS**(진단 게이트, 기본 경로 불변·테스트 GREEN), **PM1-1 PASS(귀속) 3/3(a는 EIP만, b·c는 호출 표 포함)** — 사전등록 "2/2 run에서 닫힘 전환의 A·B writer EIP가 같다" 충족(tid 288 `0x7AF3E6C9/CE`, 둘 다 매 present 동일). **단 사전등록 가설 H-PM1의 문장("전환 첫 present에서 미러 밖 writer가 사각형을 다시 쓴다")은 부분 반증:** 새 writer는 없고 매 present 같은 BltFast 배경 복원이 계속되며 바뀐 것은 저장 창 패널 복사의 중단이다. 같은 회차 수리 조건(ii) 해당 없음 → **수리하지 않음**(사전등록 규칙), 제품 C 동작 변경 0(진단 옵트인뿐, env 없으면 기존과 동일).
- 수리 방향 후보(middle 판단 요청, 구현 아님): (R-a) PS23 프레임 함수의 전면 BltFast(`0x493CC8`: 화면 버퍼 ← 원본 surface 전체)를 `hook_blt_fast`에서 "배경 복원"으로 인식해 두 가지를 보존/복원 — 일시정지 진입 시점의 화면 버퍼·expected·covered(HD 출력 포함) 스냅샷을 두고, 저장 창 사각형에서 화면 픽셀이 스냅샷 값으로 돌아오면 expected·covered를 스냅샷으로 되돌림(저장 창이 닫힌 뒤 띠 복구). (R-b) 반대로 저장 창 패널 복사 직전 그 사각형의 expected/covered를 save-under로 보관했다가 패널 복사가 사라지는 present에 복원. 두 방식 모두 HD 출력 버퍼 보존 여부와 `g_covered` 해제 시점(`g1_mirror2x.c` 1820~1831)을 건드리므로 middle이 방식을 정해야 한다. 원본 surface `0x01E6D8F0`을 채우는 writer(일시정지 진입 시 화면 캡처로 추정)는 PS23 안 호출이 없어 이번 표 밖이며 **UNKNOWN**이다.
- 부수 관찰(귀속 의무 없음): 저장 창 열림 1 present 일시 stale 51.8k는 닫힘과 별개(열림 present에 메뉴 패널 → 저장 창 패널로 바뀌는 순간 한 번), 이번에도 재현(89.11~89.18%).
- 공개 한계: PS23 watch는 표본 3점뿐(띠 두 곳·메뉴 패널 한 곳); 호출 표는 PS23 한정; ddraw 호출은 게임 스레드, 실제 픽셀 쓰기는 wined3d 스레드라 Blt 호출 인자(전면 rect NULL)로 사각형을 추정; 부하 대표성 낮음; 캡처(pause_return.png run c) 열람 정상(메뉴 8버튼·배경 정상, 띠 화질 차이만).

## 정리·보존

- 원본 EXE SHA MATCH(읽기만). game 사본은 harness가 종료 때 이미 지웠고(`local/runtime/lap1119_pm1_{a,b,c}`에는 prefix·manifest·output만 보존, 각 ~600MB prefix 2개씩은 provenance라 삭제하지 않음), 디스크 여유 ≥ 150GiB. 전부 uncommitted.

## 다음 한 가지

- middle(Opus): 위 writer 귀속과 R-a/R-b 중 수리 방식을 정하고 work H-PM2 사전등록(원본 surface 채우는 writer·스냅샷/복원 기준·PASS = 복귀 뒤 PS23 HD ≥98.6%·전체 창 ≥90%·V1/안전 0·dropped 0·PS3 비회귀).
