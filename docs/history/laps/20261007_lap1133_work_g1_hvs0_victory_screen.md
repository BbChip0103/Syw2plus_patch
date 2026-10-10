# 2026-10-07 | lap1133 | G1 work — H-VS0 승리 화면 HD(합성 트리거 `victory-poke`) 하네스·격리 실행

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap.
- 입력: STATUS 다음 한 가지, lap1132 middle 사전등록 §5(H-VS0). INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기, 비차단), `loop/STOP`·기존 `loop/ESCALATE_SOL` 없음.
- 원본 SHA: 후보·기준 lane 모두 `private_exe_sha256 == source_exe_sha256 = b56986e018b4…`, `source_unchanged` true(런 3개 6 lane). game 사본은 harness 종료 뒤 0(`local/runtime/lap1133_hvs0_*`에 `game` 없음), 디스크 여유 128GiB.
- fixture: **`victory-poke` = 합성 트리거, 승리 조건 미충족 상태에서의 강제 승리.** new-game 경로(`--new-game-path --new-game-start`)로 PS3에 들어간 뒤 `[0xB63238]` dword에 1을 1회 쓴다(readback 필수). 네이티브 입력(채팅 치트 문자열 표) 탐색은 하지 않았다(≤15분 선택 사항, 합성 트리거로 곧바로 진행 — 구현 우선). baseline·candidate 두 lane에 같은 poke.
- 가설 H-VS0: 승리 경로에서도 배너 화면과 결과 표가 H-RS2+H-RS3로 HD 100%를 유지하고, 수리를 끄면 패배 경로와 같은 결함(HUD 소실·막대 stale)이 재현된다.

## 변경 파일(모두 uncommitted, C 변경 0)

- `tools/g1_saved_scene_probe.py`(`8c22de763922…`): `--victory-poke`(요구: `--new-game-start`), 상수 `VICTORY_POKE_VA=0xB63238`·`VICTORY_READBACK_RETURN=0x4C7EEB`, `_victory_poke_window`(PS3에서 poke → readback 1 확인 못 하면 걷지 않고 FAIL → `_result_screen_window(track_states=True)`로 PS3 뒤 모든 상태를 `ps<N>` 창+`vs_ps<N>` 캡처(첫 관측 1초 뒤)로 추적, PS29 탭 3개·확인 클릭, 플래그가 0으로 돌아온 시점 `consumed`/`consumed_at_ps` 기록), `_summarize_victory`(기존 결과 화면 기준 + `poke_consumed`·`banner_reached`·`readback_mirrored`(calls ≥1, converted = calls − rejects, 반환 `0x4C7EEB`)·`bar_copy_mirrored`(calls >0, mirrored = calls − rejects), 마지막 present 행 누적 카운터), lane 결과 `victory_poke`·trace dropped 검사·`new-game-path-result.json` 키와 통과 조건에 편입. 기존 `_result_screen_window` 호출 의미(track_states 기본 False)는 불변.
- 테스트(RED→GREEN) `tests/test_g1_victory_poke.py`(`5d383d080cf0…`) 8 passed(RED 때 1 failed로 시작): 옵션·배선, 가짜 게임으로 poke 1회·상태 추적·탭 클릭·`consumed`, readback 불일치 시 걷지 않음, PS29 미도달 FAIL+상태 기록, 요약 PASS/배너 HD 하락/카운터 끔/배너 없음/플래그 미소비 FAIL. `tests/test_g1_victory_poke.py`+`test_g1_result_screen.py`+`test_g1_saved_scene_probe.py` 241 passed. `make lint`·`make typecheck` PASS.

## 정정(사전등록 §5 대비)

- **승리 배너 상태는 PS24가 아니라 PS25다.** 사전등록은 `0x41CA47`의 `[0x4ED818]=0x18`(PS24)을 승리 상태로 읽었으나 실제 관측 상태열은 3 → **25** → 29이고 PS24 present는 한 번도 없다(발견 run과 3 run 모두 trace 상태 구간 3→25→29→9). 패배에서 준비 상태 `0x1A`(26)가 보이지 않고 PS27이 보였던 것과 같은 +1 짝이다. `[0x4ED818]` 값을 쓰는 곳과 `ps` 판독 상태 사이 대응은 이번에도 정적으로 확인하지 않았다(UNKNOWN, 관측만).
- 그래서 사전등록 PASS 항목 VS0-b의 "배너 상태"는 PS25로 읽는다. 하네스 기준은 처음에 `ps24_reached`로 썼다가 발견 run(`a_discovery_ps24crit`, 같은 코드·같은 결과: HD 100%·readback 1/1·bar 2,728/2,728, 하네스 판정만 `ps24_reached` 하나로 FAIL)에서 상태 번호를 특정하지 않는 `banner_reached`(PS29·탭·확인 뒤 상태 외 창 중 present >0)로 바꿨다. 이것은 기준 완화가 아니라 상태 번호 정정이다: 같은 두 수리 카운터·HD ≥98.6·안전 조건은 그대로다. 발견 run은 근거에서 제외하고 보존만 한다.

## 격리 실행(수정 뒤 최종 하네스)

`tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1133_hvs0_<r> --artifact-root <공유 temp>/20261007_lap1133_work_hvs0/<r> --hd-source scale2x --new-game-path --new-game-start --victory-poke`(a·b 켬, off = `SYW2_G1_PRIMARY_READBACK=0 SYW2_G1_BAR_COPY=0`; 스크립트 `run_vs0.sh` `06394b8abe29…`·`run_all.sh` `54eaa7989843…`, 로그 `logs/gates/lap1133-hvs0-{a,b,off}.log`, 종료 코드 0/0/**2**(끔은 기준 미달로 FAIL 판정, 의도한 대조)). 발견 run은 `logs/gates/lap1133-hvs0-a_discovery.{log,exit}`(exit 2).

새 스크립트 `recalc_lap1133.py`(공유 temp `7f7500792ec1…`) → `recalc_lap1133.json`(`36d9ed454f30…`), 후보 `trace_raw.jsonl`(a `2b34c1f26e01…`·b `56955646878…`·off `bb7338043d57…`) raw에서 직접 계산:

| 항목 | a(켬) | b(켬) | off(끔) |
|---|---|---|---|
| poke before/readback/consumed(소비 시 ps) | 0/1/true(PS3) | 0/1/true(PS3) | 0/1/true(PS3) |
| 상태열(trace) | …3(263)→**25(1,067)**→29(1,157)→9(305) | …3(262)→25(1,066)→29(1,149)→9(300) | …3(263)→25(1,174)→29(1,165)→9(298) |
| 배너 PS25 HD min / stale max / p95 | **100% / 0 / 7ms** | **100% / 0 / 6ms** | **22.0413% / 374,202** / 6ms |
| 결과 PS29 HD min(마지막 전환 present 제외) / stale max / 증가 이벤트 | **100% / 0 / 0** | **100% / 0 / 0** | 98.3596% / 7,874 / 334 |
| PS29 첫 / 마지막(→PS9 전환) present stale | 0 / 479,004 | 0 / 479,004 | 72 / 479,004 |
| PS25 이후 PS9 HD min | 100% | 100% | 100% |
| 읽기 호출 calls/converted/rejects, 반환 주소 | 1/1/0, 5,013,227(=`0x4C7EEB`) | 1/1/0, 동일 | 1/**0**/0, 동일 |
| 막대 `0x468BB0` calls/mirrored/rejects | 2,732/2,732/0 | 2,704/2,704/0 | 2,752/**0**/0 |
| 호출이 처음 늘어난 상태 | 읽기 PS25·막대 PS29 | 동일 | 동일 |
| 안전 7종·fallback present 수 / hresult≠0 / dropped | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| PS29 경과 p95 | 12ms | 13ms | 12ms |

- harness 판정(`victory_poke.present_summary.criteria`): 켬 a·b 12/12 true(`ps25_hd`·`ps29_hd`·탭 3·`after_confirm_hd`·`safety_clean`·`ps29_reached`·`poke_consumed`·`banner_reached`·`readback_mirrored`·`bar_copy_mirrored`), scale2x validator PASS(전 lane), cleanup ok. 끔: `ps25_hd`·`ps29_hd`·`tab_soldiers_hd`·`readback_mirrored`·`bar_copy_mirrored` false.
- 캡처 열람: 켬 후보 `vs_ps25.png`(1600×1200)는 상단 자원 막대·하단 HUD(미니맵·명령 패널)·중앙 "승리했습니다!" 배너·"치트키가 사용되었습니다." 문구가 보인다. 끔 후보 `vs_ps25.png`는 HUD가 완전히 사라지고 화면 왼쪽 위 4분면이 2× 확대된 모습(lap1127 PS27 결함과 같은 모양)이다. baseline `vs_ps25.png`(800×600)는 같은 배너·HUD 구도(맵은 new-game 무작위라 run마다 다름, 비교 대상은 레이아웃). 결과 표 `result_tab_soldiers.png`는 켬 후보와 baseline의 탭·행·막대·"승리했습니다."·확인 버튼 위치가 같다.

## 판정

- **VS0-a PASS**(poke readback 1, 게임이 소비해 0으로 복귀, 승리 상태 도달 — 단 승리 배너는 PS25), **VS0-b PASS**(배너 PS25 HD min 100%·읽기 calls 1 = converted 1, 반환 `0x4C7EEB`), **VS0-c PASS**(결과 PS29 HD min 100%·막대 calls = mirrored·본문 stale 증가 0·탭 전환 뒤도 stale 0), **VS0-d PASS**(안전·fallback·hresult·dropped 0, scale2x PASS, PS25/PS29 p95 증가 0~1ms, 캡처 열람). 끔 run은 배너 22.04%(HUD 소실)·막대 +72/present를 재현했다.
- **H-VS0 `PASS(partial, 기술·격리)`**: 합성 트리거로 강제한 승리 화면(배너·결과 표)은 H-RS2·H-RS3로 HD 100%이고 결함은 수리를 끄면 재현된다.
- 공개 한계(수리 대상 아님): **합성 트리거**이며 승리 조건 미충족·치트 문구("치트키가 사용되었습니다.")가 동반되는 경로다. 실제 전투로 이긴 승리는 같은 `0x4C4040` 판정 결과 이후 경로를 쓸 것으로 정적 추정하지만 런타임 UNKNOWN · 네이티브 입력 경로(`[0xB63238]` 쓰기) 미탐색 · PS29→PS9 전환 마지막 present stale 479,004 1개(패배 경로 478,002와 같은 종류, writer 미귀속, 켬·끔 동일) · 승리 경로의 PS25 이전 PS24 present 0 이유 정적 미확인 · mirror validator는 new-game 경로의 기존 BLOCKED(oracle 0.776, lap1131 ng 7,005 errors와 같은 종류, lane 판정 영향 없음) · 부하 대표성 낮음(전투/다수 유닛 없음).
- 원본 SHA 불변·game 사본 삭제·전부 uncommitted. 시험판 재스테이징 없음(묶음 판단은 middle).

## 다음 한 가지

middle(Opus): H-VS0 독립 검수(source SHA 2개 재확인·`recalc_lap1133.py` 대신 별도 스크립트로 VS0-a~d 재계산·캡처 열람·PS24→PS25 상태 번호 정정 수용 여부) → 수용 시 RS2+RS3+VS0(+보류 H-P35)를 한 판본으로 묶어 재스테이징할지 판단하거나 남은 HD coverage(타이틀 인트로) 다음 가설 사전등록.
