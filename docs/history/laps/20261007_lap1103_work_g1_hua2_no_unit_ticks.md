# 2026-10-07 | lap1103 | G1 work — H-UA2: 사용자 `.bat`에서 `inmm_unit_ticks.jsonl` 끄기

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 커밋 0.
- 입력: lap1102 middle 사전등록 `docs/history/laps/20261007_lap1102_middle_g1_hua1_review_hua2_preregistration.md` §4. INBOX 새 지시 없음, APPROVALS 새 반려 없음, `loop/ESCALATE_SOL`·`loop/STOP` 없음.
- 원본 SHA: 원본 EXE `b56986e0…a8ac` — pair 결과의 baseline·candidate `private_exe_sha256`·`source_unchanged` 모두 일치. 원본/참고 저장소 쓰기 0.
- fixture: 비합성 save006(`616b7997…`, index 7) full pair. 활성 8인 증명이 아니다.
- 가설: env `INMM_STUB_NO_UNIT_TICKS`가 있으면 PS3 유닛 덤프 파일을 만들지도 쓰지도 않고, env가 없으면 기존과 같은 동작이다. `.bat` 두 개가 이 env를 넣으면 시험판의 상시 디스크 쓰기가 시간당 약 4.6GB에서 수십 MB로 줄어든다.

## 1. 변경 (TDD, 전부 uncommitted)

| 파일 | 내용 | SHA256 |
|---|---|---|
| `tools/inmm_stub/inmm_stub.c` | `dump_units_at_tick` 맨 앞에서 env를 1회 읽어 캐시(`static int g_no_unit_ticks = -1`), 설정돼 있으면 `CreateFileA` **전에** 반환. 다른 상시 로그·기본 경로 무변경 | `6d312824…` |
| `tools/g1_saved_scene_probe.py` | 후보 lane 전용 `--candidate-no-unit-ticks`(`--hd-source scale2x` 필요) → 후보 env에만 `INMM_STUB_NO_UNIT_TICKS=1`. baseline lane·기본값 불변 | `0f5ab722…` |
| `tests/test_g1_mirror2x.py` | 소스 계약 2개(+2): UA2-1 env 이름 1회·캐시·반환이 파일 열기 앞·기본 경로 `CreateFileA` 1개 유지 / UA2-2 후보 전용 flag·baseline env에 없음 | `ce88cb6b…` |

- RED: 새 테스트 2개 FAIL(`"--candidate-no-unit-ticks"` 없음 등) → 구현 → `tests/test_g1_mirror2x.py` 43 passed. `make lint`·`make typecheck` PASS.

## 2. UA2-3 런타임 (save006 full pair 1회)

명령: `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1103_ua2_3 --artifact-root <공유 temp>/20261007_lap1103_work_hua2/ua2_3 --hd-source scale2x --candidate-no-present-trace --candidate-no-unit-ticks` (스크립트 `run_ua2_3.sh` `3ed3ef3a…`, 로그 `logs/gates/lap1103_ua2_3.log` `910a8ad3…`, exit 0).

| 조건 | 결과 |
|---|---|
| (a) 후보 prefix `drive_c`에 `inmm_unit_ticks.jsonl` 없음 | **PASS** — 후보 `drive_c` 루트 목록 직접 확인(asset·control_events·input_trace·present_trace 4.38MB·mci·sfx 0.49MB·state·stub.log·watch 0.36MB뿐) |
| (b) baseline prefix에는 있고 ≥1MB | **PASS** — 52,784,966 B(env 미설정 기본 동작 유지) |
| (c) pair `status` | **PASS**, `scene_state_equal` true, input_effect **7/7**, minimap parity PASS, V2·V2s·V2q·Scale2x·loaded gate PASS(UA1-3과 동일 판정), EXE SHA baseline·candidate 모두 `b56986e0…`, `source_unchanged` true, cleanup ok·`game_removed` true·prefix 프로세스 0, 후보 창 1600×1200 scale 2 |
| (d) 후보 `menu.png`·`loaded.png` vs lap1101 UA1-3 | `menu.png` **0 px**. `loaded.png` **99,878 px 다름**(bbox x8..745·y0..1065). 같은 비교를 env를 건드리지 않은 **baseline lane**에도 했더니 `loaded.png` 16,633 px 다름(bbox x175..653·y0..380), `selection`·`production`은 baseline 0 px. 후보 `selection` 110,882·`production` 42,816 px도 다름 |

(d) 판정: 기준을 "다르면 차이 영역과 원인을 기록한다. 동적 프레임 차이는 공개한 뒤 판정"으로 사전등록했다. opt-out이 닿지 않는 baseline lane에서도 같은 종류의 `loaded.png` 차이가 나므로 opt-out이 만든 차이로 볼 근거가 없다. 장면(save006 월드)이 실행마다 캡처 시점에 따라 달라지는 동적 프레임으로 본다. 다만 lap1099~1101 후보 `loaded.png`가 0 px로 일치했던 이력과는 다르므로, 원인 확정이 아니라 **공개한 UNKNOWN**이다(예: 하네스 입력 타이밍, 유닛 덤프 부하 제거가 게임 tick과 캡처 시점 위상에 준 영향). 같은 pair 안의 baseline↔candidate 판정은 모두 PASS이고 loaded gate도 PASS다.

- 실제 `inmm_unit_ticks.jsonl` 쓰기 부하가 캡처 위상에 영향을 줬는지는 이번 1회로는 가를 수 없다. middle이 필요하다고 보면 후보 lane을 `--candidate-no-unit-ticks` 있음/없음으로 한 번씩 더 돌려 `loaded.png` 위상을 비교하면 된다.
- 하네스 bridge DLL `ua2_3/bridge/_inmm.dll` = `942133740dc10f92…`(436,267 B). `grep`으로 새 DLL에는 `INMM_STUB_NO_UNIT_TICKS` 문자열 1회, lap1101 스테이징 DLL(`34a9c777…`)에는 0회임을 확인했다. UA1-3 DLL과 바이트가 340,061개 달라 보이는 것은 PE 전체 정렬이 아니라 소스 변경(`inmm_stub.c` 삽입)으로 이후 코드·섹션이 밀린 결과이며(436,230→436,267 B, +37 B), 독립 재조립·비교는 middle 몫이다.

## 3. UA2-4 재스테이징 (공유 temp `20261007_lap1103_work_hua2/user_test_staging/`, `260921_temp` 배치 안 함)

| 파일 | SHA256 | 변경 |
|---|---|---|
| `_inmm.dll` | `942133740dc10f92fc666b0d76462c1afc9dde6289afb4bc9cc20fa87f7e2adf` | ua2_3 하네스 산출물 그대로 |
| `g1_trial_direct.bat` | `2da323e8bf53a984c612a282414ff33dbb15783b6505202e632206d87a026c19` | lap1101판에 `set INMM_STUB_NO_UNIT_TICKS=1` **한 줄만** 추가(`diff` 확인, CRLF 유지) |
| `g1_trial_via_dxwnd.bat` | `29a35d2edf41dae2f7ac1b09a52d2c12bd301860733ca8cb70ce43c9e85d886c` | 같음 |
| `G1_1600x1200_시험판_읽어주세요_20261007_lap1103.txt` | `97f4bd75b7b32248f221499ad6863d8bcc9ea5d2039ec183ce38700a8d788437` | 아래 개정 |

안내문 개정(스크립트 `make_staging.py` `9f8602c2…`로 lap1101판에서 생성, `diff` 확인): ① DLL SHA·개정 표기, ② `.bat`이 env 4개를 설정한다는 것과 `.bat` 없이 직접 실행하면 G1이 꺼지고(800×600) 유닛 기록도 켜진다는 것, ③ unit_ticks 크기 정정(상한 없음·실측 약 1.3MB/초·시간당 약 4.6GB, 이전 "1~2분 50MB"는 2~3배 과소 기재) 및 끈 뒤 남는 상시 로그 크기(sfx 시간당 약 36MB·watch 약 25MB·나머지 1MB 미만), ④ ESL 2606 문구를 "SHA 고정 안전장치로 꺼지도록 만들어져 있음(직접 실행 확인은 안 함)"으로, ⑤ present trace 상한 8,192 이벤트·실측 4,767 이벤트 약 12MB(UA1-2 b 사본 12,093,540 B)와 "C:\·%TEMP% 둘 다 실패 경로는 코드로만 확인" 명시.

## 4. 판정

- **H-UA2 `PASS(partial, 기술·격리)`** — UA2-1 TDD·UA2-2 하네스·UA2-3 (a)(b)(c) PASS, (d)는 동적 프레임 차이를 공개하고(baseline lane 동반 발생) 판정 보류 없이 partial로 둔다·UA2-4 재스테이징 완료. 사전등록 이탈 없음(안내문 외 기능 변경 0).
- 한계(유지·공개): 실제 Windows·DxWnd에서 `.bat`이 env를 넘기는지 미실행, `C:\`·`%TEMP%` 동시 실패 런타임 미확인, (d) `loaded.png` 위상 원인 UNKNOWN, 실제 사용자 PC의 `ddraw.dll`·1600×1200 모드·BGM, G2/G5/G6G7 EXE 조합 미측정.
- 디스크: `local/runtime/lap1103_ua2_3/{baseline,candidate}/…/game` 삭제(prefix·manifest·output 보존), 여유 약 99GB. 원본/참고 쓰기 0, 게임/wine 프로세스 잔존 0.

## 5. 역할 경계·다음

work는 자기 결과를 승인하지 않는다. `loop/ESCALATE_SOL`로 middle(fresh Opus) 검수를 요청한다. middle이 할 일: ① 새 스크립트로 pair-result·SHA·(a)(b)(c) 독립 재계산, ② 현재 트리에서 DLL 독립 재조립(타임스탬프 마스크) 후 스테이징 SHA 대조, ③ (d) `loaded.png` 차이를 UNKNOWN으로 둘지 추가 1회 pair로 가를지 결정, ④ 수용 시 APPROVALS에 G1 사용자 시험 요청을 올리고 root 전달 ESCALATE_SOL을 만든다. 검사 결과는 STATUS에만 쓴다.

다음 한 가지: middle — H-UA2 독립 검수 → 수용 시 G1 사용자 시험 요청·root 전달.
