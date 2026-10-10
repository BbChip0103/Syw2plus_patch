# 2026-10-09 | lap 1219 | G1 work — H-E2611G1-1: 2611 부팅 재확인 + `.kills`/`.idle` 전투 장면 관측

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`/high, work(실무) 1 lap. 제품 C는 lap1218(중단 세션)이 남긴 진단 변경만 있고 이 회차에서 C 추가 변경 0. 커밋 0.
- 입력: STATUS "다음 한 가지"(work H-E2611G1-1), lap1217 middle 사양 §4. INBOX 최신 = 18:53 root 메모(lap1218 work SIGTERM 중단, "처음부터 다시"), 새 사용자 지시·APPROVALS 반려·사용자 시험 결과 없음, `loop/STOP`·`loop/ESCALATE_SOL` 없음.
- lap1218 잔여 검수: 중단된 lap1218이 18:44~18:45에 남긴 변경(C `SYW2_G1_RET_RANGE_DIAG` 계수 4개·`direct_draw_trace.c` `ret_range_diag` 이벤트·하네스 `--ret-range-diag`·E1-0 lane `private_exe_sha256` 요약 키·테스트 3개)을 사양 §4 E1-0/E1-1과 대조 → 일치. focused 4파일 278 passed 확인 뒤 그대로 사용(수정 없음).
- 가설: 현재 트리 G1 DLL(팩 끔·기본 env)은 2611에서도 lap1216과 같게 동작하고 `.kills` 배지 `0x4664D0`·`.kills`/`.idle` `TextOutA`는 기존 미러로 덮여 PS3 stale 0·안전 0.
- 사전등록 PASS/FAIL: E1-0 두 lane private EXE = 2611 `d9d6bb3d…`·PS3 도달·install 1·훅 실패 0·안전 0·stale 0 / E1-1 계수 호스트 테스트 RED→GREEN·끔 동작 동일 / E1-2 `.kills` B 호출 >0·PS3 stale 0·안전 0·dropped 0·캡처 배지 육안.

## 0. 변경 파일(모두 uncommitted; 같은 파일들에 lap1099~1218 미커밋 변경이 이미 있다)

- 이 회차 새 변경(하네스·테스트만): `tools/g1_saved_scene_probe.py`(`84444549c4ab`) — `--new-game-play-dwell-captures N`(dwell을 N등분해 `ps3_dwell_1..N` 캡처, 0/미지정 = 기존 동작·한 dwell 창 유지), `--new-game-play-keys none`(스크롤 없이 시작 카메라 체류; 기존 `keys or default`를 `keys if keys is not None`로). `tests/test_g1_saved_scene_probe.py`(`66142c6af2c8`) 새 테스트 2개(둘 다 구현 전 RED 확인 → GREEN): dwell 캡처 분할·창 이름 불변·미지정 동작, keys none 무스크롤.
- lap1218 잔여 정리: 미추적 `tests/test_g1_new_game_path.py`에 lap1218이 먼저 써 둔 RED 테스트 2개(`--new-game-play-capture-every`, 이름 `ps3_play_020s` 설계)는 구현이 없었고 내가 실행에 쓴 `--new-game-play-dwell-captures`(위 새 테스트로 고정)와 중복이라 첫 `make test`(2 failed·2218 passed)에서 실패했다 → 그 2개를 삭제하고 구현이 있는 설계만 남겼다(runs C2·C3는 `dwell-captures` 명령 그대로 재현 가능).
- lap1218 잔여(검수만): `tools/inmm_stub/g1_mirror2x.c`(`649b1e0fc0a5`)·`g1_mirror2x.h`(`0a38a335b80b`)·`direct_draw_trace.c`(`09ab6b3d63ab`)·`tests/test_g1_mirror2x.py`(`b3989c19a6e2`).
- 실행 스크립트(공유 temp `20261009_lap1219_work_e2611g1/scripts/`): `run.sh`(`d2599e2c6313`)·`ana.py`(`c60dbcf6f95d`).

## 1. 실행(모두 `--esl2610`(=2611 `d9d6bb3d…`)·`--hd-source scale2x`·팩 끔·새 게임·`--ret-range-diag`·격리 game 사본·prefix·빈 Xvfb)

공유 temp `20261009_lap1219_work_e2611g1/`. 원본 HQ2002 `b56986e0…` `source_unchanged` 전 run true, 2611 EXE SHA 직접 재계산 MATCH. `game` 사본은 run마다 삭제(잔존 0), 디스크 여유 174 GB.

| run | 명령 차이 | 결과 |
|---|---|---|
| B0 (E1-0) | `--new-game-start` | exit 0 PASS, result `20207dbcea20`. 두 lane `private_exe_sha256` = `d9d6bb3d…`. PS3 266·PS5 631·PS7 145·PS9 61 present stale 0, 안전 9종(fallback·hd_mask_outside·팔레트·viewport 복원·cache clip·clip replay·identity key·hresult·viewport 변경) 0, success 1, panel foreign 0, dropped 0, `scale2x_validator` PASS. `ret_range_diag` 이벤트: b_kills 0·b_idle 0·textout_kills 0·textout_idle 492 |
| C1 | `--new-game-play --new-game-play-dwell 205 --new-game-play-dwell-captures 6` | candidate lane FAIL(`new-game PS3 timeout`): 확인 클릭 1회가 입력 트레이스에 도착(WndProc 513/514 transformed)했으나 candidate만 PS5에 머무름(baseline PASS). B0·C2·C3 candidate는 같은 경로가 정상 → **미귀속 단발 실패**(하네스·로비 타이밍 추정, 재현 0/3). result `35a704428141` |
| C2 | 같은 명령 재실행 | exit 0 PASS, result `a245ddd7b5cb`. PS3 4,577 present stale 0·안전 0·dropped 0·p95 12. 그러나 방향키 4개(RIGHT/DOWN/LEFT/UP) 뒤 candidate 카메라가 `[0,57]`(맵 가장자리, 본진은 시작 카메라 `[91,54]` 쪽)이라 dwell 캡처 6장이 전부 검은 화면(미탐색 구역) → 전투 관측 부적합. b_kills 0·textout_idle 9,112 |
| C3 | `--new-game-play-keys none`(시작 카메라 체류) + 같은 dwell | exit 0 PASS, result `cc1474f89d5e`. PS3 4,409 present stale 0·안전 0·dropped 0·covered 480,000 전부·p95 8·trace 이벤트 6,394(상한 8,192 미만). 캡처 `ps3_dwell_1..6`(약 PS3 +45~225 s): 본진 건물·일꾼·`대기 일꾼: 1` 글자·미니맵 정상, 전투·패배 화면 없음. `ret_range_diag`: **b_kills 0**·b_idle 0·textout_kills 0·**textout_idle 8,778** |

## 2. 판정

- **E1-0 PASS:** 현재 DLL이 2611 EXE에서 부팅(두 lane private EXE `d9d6bb3d…`)·PS9→7→5→3, 훅 설치 실패 0·안전 0·stale 0. 위험 ①②(MessageBoxW·창모드)는 2611에서도 비발현.
- **E1-1 PASS(진단 계수):** 옵트인 env `SYW2_G1_RET_RANGE_DIAG=1`, 끔일 때 `ret_range_diag` 이벤트 자체가 trace에 없음(호스트 테스트로 고정). 계수는 `.idle` TextOutA 호출이 실제로 잡히는 것으로 동작 확인(textout_idle 492→8,778).
- **E1-2 `INCONCLUSIVE`(`.kills` 배지):** 2개 run(C2 부적합 카메라·C3 시작 카메라) 모두 `.kills` 반환주소 B 호출 0 = 유닛 킬 기록이 생길 전투가 약 225 s 안에 일어나지 않았다(본진 정지, 패배 화면도 없음; lap1216 N0은 무입력 ~250 s에서 패배). 사양 §결론 규칙대로 같은 회차 2 run 뒤 그대로 보고하고 추가 추측 없음.
- **관측된 것(partial 근거):** `.idle` 글자(`대기 일꾼: N` 등, TextOutA 반환주소 `.idle` 8,778 호출)는 켬 상태에서 PS3 4,409 present stale 0 → `.idle` 글자 경로는 기존 H-G TextOutA 미러로 덮임. `.kills` 배지·`.kills` 글자(TextOutA kills 0)는 미관측 UNKNOWN.
- **종합: `PASS(partial, 기술·격리)` — E1-0·E1-1 PASS, `.idle` 관측 PASS, `.kills` UNKNOWN(INCONCLUSIVE).** 제품 C 변경 0·validator·gate 변경 0.

## 3. 한계·미귀속

- C1 candidate PS5 정체 1회(재현 0/3): 하네스 확인 클릭 위상 또는 로비 상태 추정, 원인 UNKNOWN. 재현되면 위치 진단.
- 전투를 일으키려면 (a) 약 230 s 근처까지 더 기다려 AI 공격(방치 시 패배) 직전·직후를 캡처하거나 (b) 선택·이동으로 유닛을 적과 마주치게 하는 입력이 필요하다 — 모두 이 사양 밖(다음 middle 판단). 패배 화면(PS27/29)은 별도 장면.
- 2611 세이브 로드·pair 기준선(H-E2611G1-2)·사용자 시험판은 미착수.

## 4. 검증

- 호스트: focused `test_g1_mirror2x.py`·`test_g1_saved_scene_probe.py`·`test_g1_scratch_bltfast.py`·`test_esl2610_runtime.py` 새 테스트 포함 통과(수치는 STATUS), 변경 파일 `ruff` 통과. `make lint` = 별도 2610 세션 untracked 파일 F401 2건(`patches/esl2610/g2_scan.py:32`·`tools/g2_esl2610_spike_probe.py:37`)으로 FAIL(이 루프 파일 아님, 수정 금지).

## 5. 다음 한 가지

middle 독립 검수(새 스크립트로 B0·C2·C3 trace의 `ret_range_diag`·stale·안전·p95 재계산, C1 정체 판정) 뒤 (1) `.kills` 전투 장면을 한 번 더 시도할지(AI 공격 시점·유닛 입력) 또는 UNKNOWN으로 두고 (2) H-E2611G1-2(2611 세이브 로드·pair 기준선)로 넘어갈지 결정.
