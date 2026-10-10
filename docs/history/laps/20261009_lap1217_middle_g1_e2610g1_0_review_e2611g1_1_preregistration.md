# 2026-10-09 | lap 1217 | G1 middle — H-E2610G1-0 독립 검수 + 2610 계열(2611) 전환 범위 결정 + H-E2611G1-1 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`/high, middle(중간계획·컨펌) 1 lap. 게임 run 0, 제품 C·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1216 work, 8줄 SHA256 앞16 `680270938b44e2a1`) → `docs/history/laps/20261009_lap1217_preserved_lap1216_escalate_sol.txt`에 byte 일치 보존 뒤 삭제. INBOX 새 사용자 지시 = 2026-10-09 18:25 2611 핫픽스 기준 이동(아래 §3 반영). APPROVALS 새 반려·사용자 시험/업스케일 결과 없음. `loop/STOP` 없음.
- 원본 SHA: HQ2002 `b56986e0…`(lap1216 lane `source_exe_sha256`), 2610 EXE `c5530cf4fd5f9429…`·2611 EXE `d9d6bb3dca11c229…` 직접 재계산 MATCH(읽기만).
- 검수 산출물(공유 temp `20261009_lap1217_middle_review/`): `recalc_lap1217.py`(`cba20439e40b`)→`recalc_lap1217.json`(`73a6bc9e8d9d`), `mutate_lap1217.py`(`e64d90a0dd6a`)→`mutations_lap1217.json`(`f7c25c3cafce`), `static_2611_kills_idle.py`(`5783bfa240a6`)→`.txt`(`a2192140a8bd`).

## 1. lap1216 독립 재계산 (새 스크립트, trace 직접)

raw SHA 앞16: result B0 `54dd6bfd0cb17795`·N0 `64bca5883db31455`·N1 `7bbeaafb88ffcab9`, candidate trace B0 `6190c6d3c0651137`·N0 `932b7f2c4f82e700`·N1 `ac87c34af51b2529`. 변경 파일 SHA 앞12(`b4936ce51a2d`·`0087623ba00e`·`281cfbb4bd3a`·`run.sh e1ed0a0eac28`·`ana.py 17f8d9a5400e`)는 기록과 일치.

| 항목 | 기록 | 재계산 | 판정 |
|---|---|---|---|
| 6 lane 실제 EXE | 2610 `c5530cf4…` | probe-result `private_exe_sha256` 6/6 `c5530cf4…` | 일치 |
| 상태 순서 | B0·N1 PS9→7→5→3, N0 …→3→27→29 | 같음 | 일치 |
| install | active·success 1, 훅 실패 0 | `mirror2x_install` active/1, `textout_iat_install_mismatch` 0 | 일치 |
| set_display_mode | 800×600×8→1600×1200 7회·640×480×32 5회, hresult 0 | 같음 | 일치 |
| B0 present | PS3 264·PS5 716·PS7 156·PS9 65, stale 0 | 같음, covered 480,000 전부 | 일치 |
| N1 present | PS3 4,305·PS5 684·PS7 156·PS9 62, stale 0 | 같음 | 일치 |
| N0 PS3 | 4,990 중 stale>0 2개(114·2 px) | seq 3594(PS3 77.5 s, 114 px)·4862(140.9 s, 2 px), 앞뒤 present 0 | 일치(위치 보강) |
| 안전 7종·hresult·success | 전부 0 | 세 run 전 상태 합계 0 | 일치 |
| panel 계수 | foreign/unbound/lock/pointer 0, bound B0 264·N1 4,305 | 같음 | 일치 |
| trace | N0 dropped 2,701(이벤트 8,191), B0·N1 0 | 같음; N0 `mirror2x_metrics` 줄 소실 | 일치 |
| p95(nearest-rank, `elapsed_ms`) | PS3 B0 7·N0 6·N1 9(max 83) | 같음, N1 p99 23·>30 ms 16개 | 일치 |
| 입력 효과 | N1 두 lane 같음(wood 차이 제외) | select·produce rice 5000→4200·used 20/20·drag·move 같음 | 일치 |

불일치 0. 정정·보강:
- **정정 1(하네스 provenance, 판정 영향 0):** `--esl2610` run의 디스크 `local/runtime/<run>/manifest.json`은 `game.exe_sha256 = b56986e0…`(HQ2002)로 남는다. `esl2610_runtime.prepare`가 `runtime_env.prepare`(manifest 기록) **뒤에** 2610 EXE를 덮어쓰고, `esl2610_overlays`도 메모리 manifest에만 붙어 디스크 파일에 없기 때문이다. 실제 EXE는 probe-result `private_exe_sha256`(실행 시 사본 재계산)로 확정된다. 다음 work는 lane 결과 JSON에 실제 EXE SHA를 명시해 남긴다(§4 E1-0, `esl2610_runtime.py`는 수정 금지).
- **정정 2(work `ana.py`):** `present_elapsed_ms` 필드를 읽는데 trace 필드는 `elapsed_ms`라 그 스크립트의 p95 출력은 None이다. 기록의 p95 숫자는 결과 JSON에서 온 것으로 재계산과 같다. 판정 영향 0.
- **(1) N1 p95 9:** 느린 present(>20 ms 48개)가 PS3 29~35 s·64~70 s 두 창에 몰려 있고, 입력(0~25 s, 512 상한) 구간과 겹치지 않는다. 같은 명령에 입력이 더 많은 N0은 >20 ms 0개다. 후반 십분위 p95는 6 ms. → **호스트 부하 변동으로 수용**(병행 2610 세션 run, 기록의 load 3.7~6과 부합). 제품 비용 회귀 근거 없음.
- **(2) N0 일시 stale 114·2 px:** 각 1 present, 다음 present에서 0, AI 공격(약 200 s 이후) 전 시점이고 다른 run(N1 0/4,305·B0 0/264) 재현 0. 기존 backlog "단발 primitive stale"(lap1116 162 px 등)과 같은 계열로 **미귀속 일시 stale**로 둔다. 재현되면 위치 진단.
- **(3) 2610 AI 방치 패배·trace 상한:** 두 lane 공통의 게임 동작(제품 무관). 긴 장면 probe는 PS3 약 230 s 안에 끝내거나(N1 217 s = 6,334 이벤트) 상한을 넘기면 `dropped_count`를 판정 실패 요인으로 따로 표기한다.
- **(4) wood 차이:** 시작 국가 `players[0].nation`과 일치한다 — nation 2 → wood 5000→4700(N0 두 lane·N1 baseline), nation 1 → 5000(N1 candidate). 국가별 생산 비용 차이로 설명되며 G1 입력 효과(선택·생산 발생·이동) 동일성 판정에 영향 없음.

## 2. 독립 변이 (저장소 밖 `/tmp/lap1217_mut`, work m2·m3과 다른 6종)

사본 기준선은 환경 의존 실패 70개(저장소 경로·local 의존)가 있어, **기준선 대비 새로 실패한 테스트**로 판정했다. 새 `--esl2610` 테스트들은 사본 기준선에서 통과한다.

| 변이 | 결과 |
|---|---|
| M1 리다이렉트 제거 | RED `test_esl2610_selection_memory_redirects_only_the_stock_entries` |
| M2 EXE SHA 검사 제거 | RED `test_esl2610_flag_refuses_a_wrong_executable` |
| M3 2610 용량을 옛 용량으로 | RED `test_esl2610_flag_switches_game_preparation_and_selection_array` |
| M4 플래그 기본 켬 | RED `test_esl2610_flag_is_off_by_default_and_needs_new_game_path` |
| M5 count(`0x899024`)까지 리다이렉트 | RED (M1과 같은 테스트) |
| M6 manifest `esl2610_overlays` 누락 | RED (M3과 같은 테스트) |
| 복원 | 새 실패 0 |

저장소 focused `.venv` pytest `test_g1_saved_scene_probe.py`·`test_g1_scratch_bltfast.py`·`test_esl2610_runtime.py` **230 passed/12.47 s**(로그 `logs/gates/lap1217-middle-focused.log` `7e8048dd3bc98ef6`). bridge 소스 65개는 현재 트리와 같고 차이는 하네스 bridge 주입(`supply_probe_poll`·`runtime_bridge.c`)뿐이며 lap1214 NON bridge 소스와 byte 동일.

**판정: lap1216 H-E2610G1-0 `FEASIBLE`(partial, 기술·격리, 2610 EXE `c5530cf4…` 기준) 수용.**

## 3. 2610 계열 전환 범위 결정

INBOX 2026-10-09 18:25: 기준 EXE는 **2611**(`d9d6bb3d…`, 2610 대비 `.a16code` imm32 1곳·버전 문자열·체크섬만 다름). `tools/esl2610_runtime.py`도 이미 2611로 고정돼 있어 `--esl2610`은 이제 2611로 부팅한다.

새 정적 근거(2611 읽기만, `static_2611_kills_idle.txt`):
- `.kills`(`0x115B000`)는 `0x4664D0`을 4곳(`0x115BBB9`·`0x115BC3A`·`0x115BD8A`·`0x115BDC5`)에서 부르고, 모두 renderer `ecx=0xE5BF18`이다. `.text`의 `0x4664D0` 호출 19곳도 전부 같은 renderer다. 그림은 `fnt\text1.spr`(문자열 `0x1A11EC4`, 로더 `0x463D60`)이고, 진입은 유닛 그리기 경로 `0x479865→0x115BA40`(그 밖 `0x47982F`·`0x479873`) 등이다. 유닛의 킬 기록(`0x115B01D` 조회)이 있을 때만 그린다 → **전투가 있어야 나타나는 맵 위 유닛 배지**.
- 현재 DLL에서 `0x4664D0`은 primitive B 훅(`mirror_primitive_b` → 일반 `mirror_reinvoke`)이고 **반환주소 화이트리스트가 없다.** 화이트리스트(`g1_panel_writer_return`: `0x41B78C`·`0x41C5A5`·`0x42496A`·`0x441538`)는 패널 RLE `0x4663E0`에만 쓰인다. 따라서 INBOX 위험 ③("패널 반환주소 화이트리스트 밖")은 **분류 정정**: `.kills` 호출은 일반 미러 경로로 간다(거부는 패널 버퍼 대상 foreign writer일 때뿐). 실제 장면 런타임은 미검증.
- `.kills`·`.idle`은 둘 다 GDI 글자(`CreateFontA`·`TextOutA` IAT `0x4E502C`·`SetTextColor`·`SetBkMode`·`SelectObject`·`wsprintfA`)를 쓴다. `TextOutA`는 H-G가 이미 IAT 미러한다. `.idle`은 프레임 경로 `0x41C383`·AI selector 부근 `0x40685B/0x406868/0x4068DE`·`0x48DDD0`에서 들어온다.

결정:
1. **(c) 먼저 — H-E2611G1-1**: 2611 부팅 재확인 + 2610 계열 고유 그리기(`.kills` 배지·`.idle`/`.kills` 글자)를 실제 전투 장면에서 관측. 사용자 플레이 EXE에만 있는 유일한 새 그리기 경로이고 lap1216 범위(전투 없음) 밖이다.
2. **(b) 그다음 — H-E2611G1-2(다음 middle이 사전등록)**: 2611에서 세이브 로드 가능성(save006 HQ2002 세이브 타이틀 로드, 안 되면 2611 안에서 만든 세이브 fixture) → 2611 기준 pair 기준선. 현재 시험판 스테이징 기준(save006 full pair PASS)을 2611에서 대신할 기준이 필요하다.
3. **(a) 마지막 — 2611 사용자 시험판**: (c)·(b) PASS 뒤 묶는다. 스테이징 때 확인할 것: 사용자 2611 폴더의 `_inmm.dll`을 우리 DLL로 바꿀 때 `_inmmserv.exe` 동작(2610 진입점 MessageBoxW 대기 경로), `ai_shadow`(G4 `0x415480`, 2610에서 입구 바이트 변경)는 env 게이트로 꺼져 있는지. 그 전까지 현행 APPROVALS lap1152 시험판(HQ2002용)은 그대로 유효하다. 이 회차 중 INBOX에 들어온 G8·G9(루프 밖 세션) 전달 변형은 2611+G2+G6+G8(+G9) EXE다 — 시험판 단계에서는 공식 2611뿐 아니라 이 변형들(추가 섹션·G2 유닛 풀 재배치)과의 DLL 공존도 확인 대상이다(지금 범위 밖, 기록만).
4. HQ2002 기준선·과거 판정은 바꾸지 않는다. 2611 결과는 별도 증거로 쌓는다.

## 4. 다음 work 사전등록 — H-E2611G1-1: 2611 부팅 재확인 + `.kills`/`.idle` 전투 장면 관측

**가설:** 현재 트리 G1 DLL(팩 끔·기본 env)은 2611에서도 lap1216과 같게 동작하고, 2610 계열 고유 그리기(`.kills` 배지 `0x4664D0`, `.kills`/`.idle` `TextOutA` 글자)는 기존 primitive B·H-G 미러로 덮여 PS3 stale 0·안전 0이다.

**구성:** `--esl2610`(현재 `esl2610_runtime` = 2611 `d9d6bb3d…`, SHA 검사), `--hd-source scale2x`, 팩 끔, 새 게임, 격리 game 사본·prefix·빈 Xvfb, run마다 `game` 사본만 삭제.

| 단계 | 할 일 | PASS 조건 |
|---|---|---|
| E1-0 2611 부팅 | lap1216 B0과 같은 명령 1 run. 하네스가 lane 결과(`new-game-path-result.json`)에 실제 private EXE SHA를 명시해 남기게 한다(정정 1, `esl2610_runtime.py` 수정 금지, 테스트 RED→GREEN). | 두 lane private EXE = `d9d6bb3d…`, PS3 도달, install success 1·훅 실패 0, 안전 7종 0, stale 0 |
| E1-1 진단 계수 | 옵트인 env(예: `SYW2_G1_RET_RANGE_DIAG=1`, 기본 끔 = 동작·출력 byte 동일)로 (i) primitive B(`0x4664D0`) 호출 중 반환주소 ∈ `.kills [0x115B000,0x115C000)`·`.idle [0x1157000,0x1158000)` 수 (ii) `TextOutA` IAT 훅 호출 중 같은 범위 수를 `mirror2x_metrics`(또는 present 줄)에 낸다. 미러 로직·validator·gate 변경 금지. | 호스트 테스트 RED→GREEN, 끔일 때 기존 필드·동작 동일 |
| E1-2 전투 장면 | `--esl2610 --new-game-path --new-game-start --new-game-play`, 입력 없이 시작 카메라 체류 약 230 s(패배 전 종료; trace 이벤트 상한 고려), 150 s 이후 candidate 캡처 3장 이상(하네스에 없으면 최소 옵션 추가·테스트). E1-1 계수 켬. | `.kills` B 호출 >0(배지 실제로 그려짐)·PS3 stale 0(단발 1 present ≤200 px는 위치·시각 기록 뒤 허용)·안전 7종 0·panel foreign 0·trace dropped 0·캡처에 배지 육안 확인 |

**결론 규칙:**
- E1-0·E1-2 PASS → `PASS(partial, 기술·격리)`, 다음 middle이 H-E2611G1-2(세이브 로드·pair 기준선) 사전등록.
- `.kills` B 호출 0(카메라 밖 전투 등) → `INCONCLUSIVE`, 같은 회차에 카메라를 본진 쪽에 두거나 체류를 조정해 1회 더(최대 2 run). 그래도 0이면 그대로 보고.
- 배지·글자 위치에서 stale이 반복되면 `FAIL(귀속)` — 위치·계수·캡처만 기록, 수리는 다음 회차.
- 2611 부팅이 깨지면 lap1216 2610 결과와 비교해 원인만 귀속(`.a16code` 변경 외 차이 없음이 정적 전제).

**하지 않는 것:** G1 미러 로직·validator·gate 변경, 팩 켬, 시험판 재스테이징, G2/G5/G6/G7 접촉, 별도 2610 세션 파일(`tools/esl2610_runtime.py`·`patches/esl2610/`·`tools/g2_esl2610_*`) 수정, 2610/2611/원본 EXE·`patch_history`·`260921_temp` 쓰기.

**검사:** 테스트 RED→GREEN, `make typecheck`, `make test`(별도 세션 untracked 파일의 lint F401 2건 — `patches/esl2610/g2_scan.py:32`·`tools/g2_esl2610_spike_probe.py:37` — 때문에 `make check`는 계속 실패할 수 있다; 그 파일은 고치지 않고 기록), 변경 파일 ruff, SAFETY. 장기 run은 PID·`.exit` 파일로 끝까지 기다린다(`pgrep -f` 자기 일치 금지).

**우선순위 예외:** 사용자 업스케일 결과나 G1 시험 결과가 INBOX에 오면 그것이 최우선이다.

## 5. 검증

- 이번 회차 변경: 문서(이 기록·STATUS·INBOX 메모·ESCALATE_SOL 보존본)와 공유 temp 검수 스크립트·결과뿐.
- 전체 `make check` SKIP(source 변경 0; 현재 `make lint`는 별도 세션 untracked 파일 F401 2건으로 exit 2 — lap1216 기록의 4건에서 2건으로 줄었다, 이 루프 파일 아님). focused 230 passed. SAFETY·CONTEXT 결과는 STATUS에 보강.

## 6. 다음 한 가지

work H-E2611G1-1(위 §4). 사용자 업스케일·G1 시험 결과가 오면 그것이 최우선.
