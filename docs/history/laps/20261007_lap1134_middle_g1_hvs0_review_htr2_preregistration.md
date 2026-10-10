# 2026-10-07 | lap1134 | G1 middle — H-VS0 독립 검수·수용, H-TR2(묶음 시험판 재스테이징) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간 계획·컨펌) 1 lap. 게임 코드 hands-on 수정 0.
- 입력: `loop/ESCALATE_SOL`(lap1133 work). 원문은 byte 일치로 `docs/history/laps/20261007_lap1134_preserved_lap1133_escalate_sol.txt`(SHA256 `9df992147d33…`)에 보존한 뒤 삭제했다. 그 밖의 입력은 STATUS 다음 한 가지와 lap1132 사전등록 §5다. INBOX 새 사용자 지시 없음. APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기, 비차단). `loop/STOP` 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b4…` 직접 재계산 MATCH. 3 run 6 lane 모두 `private_exe_sha256 == source_exe_sha256`, `source_unchanged` true.
- fixture: 재실행 없음. lap1133 raw만 재계산했다. fixture = `victory-poke`(합성 트리거 `[0xB63238]=1` 1회, new-game PS3).
- 가설(검수 대상): H-VS0 — 승리 경로에서도 배너 화면과 결과 표가 H-RS2+H-RS3로 HD 100%를 유지하고, 수리를 끄면 패배 경로와 같은 결함이 재현된다.

## 1. 출처·바이트 확인

- source SHA는 lap1133 기록과 같다:
  - `tools/g1_saved_scene_probe.py` `8c22de763922`
  - `tests/test_g1_victory_poke.py` `5d383d080cf0`
- C·헤더는 lap1132 확인값 그대로다(`g1_bar_copy.h` `ff12d6299246`, `g1_mirror2x.c` `1213c4abb660`, `g1_mirror2x.h` `d3af97ed6adf`, `direct_draw_trace.c` `5ee7c6e90021`, `Makefile` `f6b0a382c75a`). lap1133의 C 변경은 0이다.
- 하네스 mtime은 10:00:50이다. 최종 run a·b·off는 그 뒤(종료 10:04/10:07/10:09)에 돌았고, 발견 run(10:00:06 종료)만 그 앞이다. 기록 설명과 맞다.
- `tools`·`tests`·`checks` 아래에 `logs/gates/lap1133-work-full-check.log`(10:23:54)보다 새 파일은 0개다. full PASS 1786 뒤 source 변경은 0이다.
- run 사본(a·b·off `bridge/`)의 C·헤더는 현재 source와 같다. `inmm_stub.c` 하나만 다른데, 하네스가 넣는 `supply_probe_poll` 두 줄 때문이다. 세 run의 사본 SHA `4ad87bf4d0c4…`는 lap1131 run 사본과 같다(정상 하네스 주입).
- trace raw SHA는 기록과 같다: a `2b34c1f26e01`, b `56955646878…`, off `bb7338043d57`.
- `local/runtime/lap1133_hvs0_*`에 `game` 사본 없음. 디스크 여유 127G.

## 2. 독립 재계산(새 스크립트, work 스크립트 미사용)

공유 temp `20261007_lap1134_middle_review/`:

| 파일 | SHA256 |
|---|---|
| `recheck_lap1134.py` | `66ceb3fdcfbb` |
| `recheck_lap1134.json` | `0baa432a4e09` |
| `caps_lap1134.py` | `43b350ca52bb` |
| `caps_lap1134.json` | `1dfe7d208c36` |

방법: work는 상태별로 묶어 계산했다. 이번에는 seq 순서의 **연속 상태 구간**으로 나누고, 누적 카운터 증가분을 처음 나타난 구간에 귀속했다.

| 항목 | a | b | off | work 값 | 판정 |
|---|---|---|---|---|---|
| 마지막 PS3 뒤 구간 열(present 수) | 3(263)→25(1,067)→29(1,157)→9(305) | 3(262)→25(1,066)→29(1,149)→9(300) | 3(263)→25(1,174)→29(1,165)→9(298) | 동일 | 일치 |
| PS24 present | 0 | 0 | 0 | 0 | 일치 |
| PS25 HD min / stale max / p95 | 100 / 0 / 7 | 100 / 0 / 6 | 22.0413 / 374,202 / 6 | 동일 | 일치 |
| PS25 구간 readback 증가(calls/converted), 반환 | 1/1, `0x4C7EEB` | 1/1, 동일 | 1/**0**, 동일 | 동일 | 일치 |
| PS29 본문(마지막 전환 present 제외) HD min / stale max / 증가 이벤트 | 100 / 0 / 0 | 100 / 0 / 0 | 98.3596 / 7,874 / **333** | off 334 | **정정 1** |
| PS29 첫 / 마지막 stale | 0 / 479,004 | 0 / 479,004 | 72 / 479,004 | 동일 | 일치 |
| PS29 구간 bar 증가 calls/mirrored | 2,732/2,732 | 2,704/2,704 | 2,752/**0** | 동일 | 일치 |
| bar 픽셀 합 | 4,092,480 | 4,042,080 | 0 | — | 기록 |
| PS29 p95 | 12 | 13 | 12 | 동일 | 일치 |
| PS9(결과 뒤) HD min | 100 | 100 | 100 | 동일 | 일치 |
| 안전 7종(fallback·outside·palette·clip replay·viewport mutation/restore·identity invalid)·hresult≠0 present | 0 | 0 | 0 | 0 | 일치 |
| dropped(event·present) | 0/0 | 0/0 | 0/0 | 0 | 일치 |
| poke before/readback/consumed(ps) | 0/1/true(3) | 동일 | 동일 | 동일 | 일치 |
| scale2x validator | PASS | PASS | PASS | PASS | 일치 |

- **정정 1(전사):** off PS29 본문 stale 증가 이벤트는 334가 아니라 **333**이다. lap1131 off(333)와 같은 값이다. 판정에는 영향이 없다(off는 결함 재현 대조).
- 발견 run(`a_discovery_ps24crit`)도 같은 구간 열을 보인다: PS25 1,101 present HD 100%, readback 1/1, bar 2,728/2,728, PS29 본문 100%. 하네스 판정만 `ps24_reached`로 FAIL이었다는 기록과 맞다. 근거에서는 제외하고 보존만 한다.

## 3. PS24→PS25 정정 검토

- 원본 lane(a·b·off의 baseline)과 off candidate trace에는 `program_state` 24인 레코드가 정확히 1개 있다. `surface_release` 집계 1건이고, present는 없다. 원본 lane의 상태 열 끝은 `…3→24→25→29→9`다.
- 따라서 **PS24는 실제로 지나가는 준비 상태**이고(`0x41CA47`의 `[0x4ED818]=0x18`과 맞음), present 없이 곧바로 PS25(배너 표시)로 넘어간다. 패배 경로의 준비 PS26 → 배너 PS27과 같은 짝이다.
- 그래서 work의 정정("배너 상태는 PS25, PS24 present 0")은 맞다. 기준을 `ps24_reached`에서 `banner_reached`로 바꾼 것도 기준 완화가 아니라 상태 번호 정정으로 **수용**한다.
- work가 "정적 미확인"으로 남긴 PS24 present 0의 이유는 위 trace 근거로 "준비 상태라 present 없이 지나감"으로 좁힌다. `[0x4ED818]` 값과 ps 판독 사이의 정적 대응은 여전히 확인하지 않았다(판정 영향 없음).

## 4. 캡처 직접 열람

- `a/candidate/vs_ps25.png`(1600×1200): 상단 자원 막대, 하단 HUD(미니맵 틀·F1~F11·명령 패널), 중앙 "승리했습니다!" 배너, "치트키가 사용되었습니다." 문구가 보인다.
- `off/candidate/vs_ps25.png`: HUD가 없다. 화면은 왼쪽 위 4분면을 2× 확대한 모양이고, 배너만 원래 크기로 겹쳐 있다. lap1127 PS27 결함과 같은 모양이다.
- `a/baseline/vs_ps25.png`(800×600): 같은 배너·HUD 구도다.
  - 맵은 new-game 무작위라 run마다 다르다. 그래서 2× 표본 대 baseline 차이(24.8만~35.4만 px)는 비교 지표가 아니다. 레이아웃만 비교한다.
- 하단 163행 비검정 비율: 켬 0.6906, baseline 0.636~0.684, 끔 0.8716(확대된 지형이 HUD 자리를 채움).
- `a/candidate/result_tab_soldiers.png`: 탭 4개, 행 8개, 파랑·빨강 막대 "1", "승리했습니다.", 확인 버튼이 baseline과 같은 위치다.
  - 2× 표본 대 baseline 채널 차 >8 픽셀은 a·b·off 모두 8,194로 같다. 즉 Scale2x 가장자리 차이다.
  - 켬과 끔의 캡처가 같은 것은 lap1132 공개(H-RS3 가시 효과 ≈0)와 맞다.

## 5. 판정

- **불일치 0, 정정 1(off 증가 이벤트 334→333).** VS0-a·b·c·d 모두 PASS이고, off에서 결함이 재현됐다(배너 22.04%·HUD 소실, 막대 +72/present).
- **H-VS0 `PASS(partial, 기술·격리)` 수용.** 합성 트리거로 강제한 승리 화면(배너 PS25·결과 표 PS29)은 H-RS2·H-RS3 범위 안에 있다. 사용자 합격도 G1 마감도 아니다.
- 공개 한계 유지:
  - 합성 트리거이며, 치트 문구가 함께 뜬다. 실전투 승리 경로는 UNKNOWN이다.
  - `[0xB63238]` 네이티브 입력은 탐색하지 않았다.
  - PS29→PS9 전환 마지막 present stale 479,004 1개(켬·끔 동일, writer 미귀속)
  - mirror validator new-game BLOCKED(기존 종류)
  - 부하 대표성 낮음

## 6. 시험판 재스테이징 판단: 지금 묶는다

- lap1104 판(`94213374…`, 00:21 KST 전달) 뒤 제품 C에 기본 켬 수리가 넷 들어갔다:
  - H-P35(lap1106, 불러오기 화면 화질)
  - H-PM2/PM3 R-a(lap1121, Esc 메뉴의 저장·불러오기·환경설정 창을 닫은 뒤 띠 화질)
  - H-RS2(lap1129, 패배·승리 배너 화면의 약 8초 HUD 소실)
  - H-RS3(lap1131, 결과 표 막대 계측)
- 이 가운데 H-RS2 HUD 소실은 사용자 눈에 바로 보이는 결함이다. 사용자가 이번 판으로 한 판을 끝까지 하면 반드시 마주친다.
- lap1107·1109의 보류 이유는 "판본 혼동 방지"였다. lap1132가 VS0 검수 뒤 묶음으로 시점을 정했다. 사용자 결과는 아직 없다. 지금 바꾸면 사용자가 옛 판으로 이미 고쳐진 결함을 보고하는 일이 줄어든다.
- 위치·입력 동작은 네 수리 모두 바꾸지 않는다. 화질·계측만 바꾼다.
- 네 수리는 모두 env가 없으면 켜진다(`SYW2_G1_PAUSE_SNAPSHOT`·`SYW2_G1_PRIMARY_READBACK`·`SYW2_G1_BAR_COPY`는 `0`일 때만 꺼짐, `g1_mirror2x.c` 초기화 코드 확인). 따라서 `.bat`은 바꿀 필요가 없다(H-P35는 env 없음).
- 역할 경계: 스테이징 산출물은 work가 만들고, 다음 middle이 독립 재조립·대조한 뒤 APPROVALS와 root 전달(ESCALATE_SOL)을 맡는다. lap1103/1104와 같은 절차다.

## 7. 다음 work 사전등록(Sonnet) — H-TR2: 묶음 시험판 재스테이징

**목표.** 현재 트리(아래 SHA)로 만든 단일 `_inmm.dll`을 실제 격리 실행으로 확인한 뒤 공유 temp에 스테이징한다. 이 판이 lap1104 판을 대체하는 사용자 시험 대상이다.

**TR2-0 출처.**

- 시작 때 source SHA가 §1 값과 같은지 확인한다(`g1_mirror2x.c` `1213c4abb660` 등). 다르면 차이를 기록하고 멈춘다.
- C·하네스 변경은 금지다. 스테이징 생성 스크립트는 공유 temp에만 둔다(repo 밖).

**TR2-1 save006 full pair 1회(사용자 시험 판정 경로, lap1103 UA2-3과 같은 플래그).**

```
PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1135_tr2_pair \
  --artifact-root <공유 temp>/20261007_lap1135_work_htr2/pair --hd-source scale2x \
  --candidate-no-present-trace --candidate-no-unit-ticks
```

PASS 조건:

- pair `status` PASS(V2s는 W-1 gate)
- `scene_state_equal` true, input_effect 7/7, minimap parity PASS
- V2·V2q·Scale2x·loaded gate PASS
- 두 lane EXE SHA `b56986e0…`, `source_unchanged` true
- cleanup ok, `game_removed` true
- 후보 창 1600×1200 scale 2
- 후보 prefix에 `inmm_unit_ticks.jsonl` 없음

**TR2-2 같은 트리 수리 경로 확인 1회(present trace 켬).**

```
… --runtime-root local/runtime/lap1135_tr2_vs --artifact-root <공유 temp>/20261007_lap1135_work_htr2/vs \
  --hd-source scale2x --new-game-path --new-game-start --victory-poke
```

PASS 조건:

- lap1133 켬 run과 같은 기준 12/12
- readback 1/1(반환 `0x4C7EEB`)
- bar calls = mirrored > 0
- PS25·PS29 본문 HD 100%
- 안전·dropped 0

**TR2-3 DLL 동일성.**

- 스테이징 DLL = TR2-1 `pair/bridge/_inmm.dll` 그대로다.
- TR2-2 bridge DLL과 비교해 PE TimeDateStamp·CheckSum 등 타임스탬프 영역 밖 바이트 차이가 0인지 확인하고, 다른 오프셋을 기록한다.
- lap1104 판(`94213374…`)과는 source 변경 때문에 크기·바이트가 다른 것이 정상이다. 크기만 기록한다.
- 문자열 확인: `INMM_STUB_NO_UNIT_TICKS` 1회. 새 env 이름(`SYW2_G1_PRIMARY_READBACK`·`SYW2_G1_BAR_COPY`·`SYW2_G1_PAUSE_SNAPSHOT`) 존재.

**TR2-4 스테이징**(`<공유 temp>/20261007_lap1135_work_htr2/user_test_staging/`, `260921_temp` 배치·APPROVALS 수정 금지):

- `_inmm.dll`(TR2-3)
- `g1_trial_direct.bat`·`g1_trial_via_dxwnd.bat`: lap1103 스테이징에서 byte 그대로 복사하고 SHA `2da323e8…`·`29a35d2e…` 일치를 확인한다.
- 안내문 `G1_1600x1200_시험판_읽어주세요_20261007_lap1135.txt`: lap1103판에서 생성하고 `diff`를 기록한다. 바꿀 것은 다음뿐이다.
  - ① DLL SHA·개정 표기
  - ② "이 판은 2026-10-07 00:21에 전달한 판(`94213374…`)을 대체한다. 옛 판으로 본 결과가 있으면 어느 판인지 적어 알려 달라."
  - ③ 추가 수리 4개를 쉬운 말로 적는다. 불러오기 화면 화질 / Esc 메뉴의 저장·불러오기·환경설정 창을 닫은 뒤 화질 / 패배·승리 배너 화면에서 하단 HUD가 몇 초 사라지던 문제 / 결과 표 막대(눈에 띄는 변화 거의 없음). 위치·입력 동작은 바뀌지 않는다고 적는다.
  - ④ lap1104가 공개한 사소한 표현 2개를 고친다(파일 목록의 "환경변수 3개" → 4개, "이번 개정본(lap1101)" 과거 표기).
  - ⑤ 확인 절차에 "한 판을 끝내 승리/패배 배너와 결과 표를 볼 수 있으면 HUD가 유지되는지" 한 줄을 넣는다(선택 사항).
- 스테이징 디렉터리는 정확히 4파일이다. 각 SHA를 기록한다.

**FAIL/BLOCKED.**

- TR2-1 pair FAIL이면 스테이징하지 않는다. 원인 lane·gate를 기록하고 middle에 넘긴다(수리 금지, 가설 1개 규칙).
- TR2-2 기준 미달이나 DLL 비타임스탬프 차이가 있으면 스테이징하지 않고 보고한다.
- 실패 가설 2회 또는 60분이면 BLOCKED.

**공통.**

- C·하네스·테스트 변경이 없으면 전체 `make check`는 SKIP할 수 있다(lap1133 full PASS 1786 트리 그대로). 대신 `checks/safety.sh check`와 context 검사를 돌린다.
- 디스크 ≥20GiB(현재 127G), 각 run 뒤 game 사본을 삭제한다.
- 원본/참고 쓰기·커밋·`260921_temp` 배치는 금지다. 사용자 G1 시험 결과가 오면 최우선이다.

**다음 middle(lap1136 예정).**

- 새 스크립트로 TR2-1 pair-result·TR2-2 raw 재계산
- 현재 트리 독립 재조립(타임스탬프 마스크) → 스테이징 DLL 대조
- 안내문 열람
- 수용 시: APPROVALS lap1104 항목에 "lap1135 판으로 대체" 메모 + 새 사용자 시험 요청, root 전달 `loop/ESCALATE_SOL`

## 8. 검사

- 결과는 STATUS 검증 줄에 보강한다(safety·context·focused 테스트).
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. C·하네스·테스트 source SHA는 lap1133 full PASS 1786 그대로다.

## 다음 행동

work(Sonnet) H-TR2: save006 full pair + victory-poke 확인 → DLL 동일성 → 4파일 스테이징(§7) → middle(Opus) 독립 재조립 뒤 APPROVALS·root 전달.
