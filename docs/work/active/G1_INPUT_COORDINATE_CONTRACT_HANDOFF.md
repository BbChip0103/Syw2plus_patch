# HANDOFF — G1 입력 좌표 계약 수리 (middle → work tier)

작성: 2026-09-11 lap149 middle tier(Claude Code `claude-opus-5`, 진단·계획·확인).
근거 원문: `docs/history/laps/20260911_lap149_middle_g1_config_2x_input_contract_confirmation.md`.
이 카드는 구현 지시이며, 작성자는 구현하지 않았다. 승인 범위 밖의 적층을 하지 마라.

## 판정 요약 (이미 확인된 것 — 다시 조사하지 마라)

- config-only 2× 프로필은 **표시층에서 목표대로 동작했다**. 게임 논리 surface는 800×600으로
  불변이고(`set_display_mode` 마지막 800×600×8bpp, primary 800×600), 그것이 1600×1200 client에
  letterbox 없이 2.0×2.0으로 표시됐다. 프로필을 폐기하지 마라.
- PS9 정체는 렌더 정지가 아니다. PS9에서 `blt_fast` 256건이 끝까지 기록됐다.
- lap146(PASS)과 lap148(BLOCKED) 모두 게임 창이 root 원점·border 0이라 **root 좌표 = client 좌표**다.
  두 run의 입력 경로 차이는 좌표 ×2 선변환 하나뿐이다.
- 게임 히트테스트는 800×600 공간이고 목표점은 (184,560)이다. wrapper가 좌표를 역변환하지 않으면
  게임은 y=1120(범위 밖)을 보고, 역변환하면 이중 변환으로 (92,280)을 본다. **어느 쪽이든 ×2 선변환은 틀렸다.**

## 이번 바퀴의 단 하나의 가설

> 하네스가 논리좌표를 물리좌표로 선변환하지 않고 **논리좌표 (184,560) 그대로** 보내면,
> 같은 config-only 2× 후보에서 PS9→PS7이 통과한다.

falsifiable: 선변환 없이도 PS7에 도달하지 못하면 좌표공간 가설은 **반증**되고, 용의자는
H2(입력이 게임 창에 도달하지 못함) / H4(동영상 등 비대화 구간에 클릭 투입)로 넘어간다.
그 경우 재시도하지 말고 관측 추가를 다음 바퀴로 올려라.

## 해야 할 변경 (1개, 최소)

`tools/runtime_env.py`의 `g1-presentation-trace` 경로만 고친다.

1. `tools/runtime_env.py:2372-2373`의 "content가 정확히 800×600" 단정을 **client 크기 가변**으로
   바꾸되, 안전을 낮추지 마라:
   - client(content) 크기는 `(800,600)` 또는 `(1600,1200)`만 허용한다. 그 외는 지금처럼 거부한다.
   - **논리 구성이 800×600이라는 단정은 유지·강화한다.** trace의 마지막 `set_display_mode`와
     primary surface descriptor가 800×600임을 evidence에 기록하고 검사하라. 이것이 "원본 구성 유지"의
     실제 계약이며, client 크기 단정이 대신하던 역할이다. 이 단정을 없애면 비원본 구성이 PASS로
     세탁될 수 있다.
   - `content_crop`과 `window.scale = client/logical`을 evidence에 남겨라.
2. 클릭 좌표는 **논리좌표를 그대로** 쓴다(`content_crop.x + 184`, `content_crop.y + 560`).
   `x11_mouse_click.py`에 스케일 인자를 추가하지 마라. 선변환 코드를 새로 넣지 마라.
3. `inputs[].result`는 효과 확인 전에 `"PASS"`로 적지 마라. lap148처럼 `"SENT"`만 남기고
   상태 전이가 확인된 뒤에 `"PASS"`로 기록하는 현재 규약을 지켜라.

**하지 말 것**: 좌표 미세 보정/스윕, 추가 dxwrapper 설정, 추가 DLL, 게임 EXE 패치, bridge 네이티브
코드 확장, 같은 프로필 반복 재실행, timeout 늘리기. 전부 이번 승인 범위 밖이다.

## 실행 계약

- lap148 런타임은 커밋되지 않은 inline 스크립트였고 **복원 불가**다. 이번에는 반드시 커밋된
  `tools/runtime_env.py`의 `g1-presentation-trace` 경로로 실행해 재현 가능하게 만들어라.
  provenance의 `command`와 `harness_sha256`이 실제 실행 코드와 일치해야 한다.
- 새 private copy / 새 prefix / 미사용 display / 새 helper·bridge 빌드. 기존 산출물 재사용 금지.
  builder `--out-dir`의 child는 미리 만들지 마라(lap144 실패 계약).
- 후보 config는 `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`,
  old는 `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`. exact old/new 확인,
  종료 시 byte-exact 원복.
- 클릭은 1회. 실패하면 재시도하지 말고 증거를 보존한 채 승격하라.

## PASS / FAIL 판정식

- PASS: 논리 surface 800×600 불변 + client 1600×1200 + scale 2.0×2.0 + **선변환 없는 (184,560)
  클릭으로 PS9→PS7** + 이후 기존 finalization(owned close → process exit → DLL detach →
  summary 1건 → raw copy → validator, dropped 0 / overflow 없음) + owned-only cleanup.
- FAIL/반증: 위 클릭으로도 PS7 미도달. 이 경우 좌표공간 가설은 반증이며 H2/H4로 넘긴다.
- 어느 쪽이든 `make check`와 `checks/safety.sh check`를 실행해 수치를 기록하라.
  **lap149는 이번 세션의 실행 권한 제약으로 Fast를 돌리지 못했다(SKIP). 이 공백은 네가 메워야 한다.**

## 부록 — lap151 middle tier: source 입력 승인 (lap150 blocker 해소)

작성: 2026-09-11 lap151 middle tier(Claude Code `claude-opus-5`).
근거 원문: `docs/history/laps/20260911_lap151_middle_g1_source_root_contract_confirmation.md`.
lap150은 위 "해야 할 변경"을 이미 구현했고 Fast까지 통과했다. **코드를 다시 고치지 마라.**
막힌 곳은 실행 단계의 `prepare` 입력 하나뿐이며, 그것을 여기서 확정한다.

- **판정: `runtime_env.prepare`의 source 계약에는 결함이 없다.** 계약은 "source root가
  `syw2plus_original.exe`를 직접 포함하는 게임 설치 디렉터리"이고, 커밋된 `DEFAULT_SOURCE`
  (`tools/runtime_env.py:155`)가 이미 그 경로다. lap150의 RC2는 호출 입력 오류였다.
- **승인된 입력: `--source`를 생략하고 커밋된 기본값을 쓴다.**
  이는 `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus`와 같다.
  기본값에 의존하는 편이 명령 문자열 복사 오류를 반복하지 않는다. 명시하고 싶으면 정확히 이 경로만
  쓰고, 다른 경로를 탐색하거나 repo root(`.../Syw2plus_re`)를 재시도하지 마라.
- **실행 전 단 하나의 사전 점검**: `find /home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus -type l`
  이 비어 있는지 확인한다. `prepare`는 source 트리의 symlink를 거부하므로 이것이 남은 RC2 후보다.
  middle 세션은 작업 디렉터리 밖 `find` 권한이 없어 이 한 가지를 확인하지 못했다. 비어 있지 않으면
  **임의로 제외/복사하지 말고** 경로 목록을 근거로 남기고 승격하라.
- 그 외 실행 계약(새 copy/prefix/display, builder `--out-dir` 미리 생성 금지, 후보 config old/new
  해시, byte-exact 원복, 클릭 1회, 실패 시 재시도 금지)은 위 본문 그대로다. 변경 없음.
- `make check`와 `bash checks/safety.sh check`는 **네가 실행한다.** lap151도 실행 권한 거부로
  SKIP했다. lap150이 동일 bytes에서 179 PASS를 기록했으나 그것을 이번 실행의 근거로 쓰지 마라.

## 부록 — lap153 middle tier: config 적용 경계 판정 (lap152 blocker 해소)

작성: 2026-09-11 lap153 middle tier(Claude Code `claude-opus-5`).
근거 원문: `docs/history/laps/20260911_lap153_middle_g1_dxwrapper_config_apply_boundary_verdict.md`.
lap152는 위 입력 계약을 커밋된 경로로 실행해 PS9→PS7→PS3를 통과시켰다. **입력 계약 코드를 다시
고치지 마라.** 남은 문제는 "2x 후보가 실제로 적용된 적이 없다"는 것 하나이며, 원인은 둘이다.

- **판정 1: lap152의 미적용은 호출 오류가 아니라 하네스 결손이다(lap151과 반대).**
  `dxwrapper_config.apply()`는 존재하는 target을 거부하므로 게임이 읽는 `game/dxwrapper.ini`에
  원리적으로 적용할 수 없고, 커밋된 코드 어디에도 후보를 private copy에 설치하는 경로가 없다.
- **판정 2: 설치했더라도 이번 경로에서는 효과가 없다.** 커밋된 4개 런타임 경로가
  `WINEDLLOVERRIDES=ddraw=b`(builtin 전용)를 고정하고, lap152 module map에는 Wine builtin
  `ddraw.dll`만 매핑돼 있다. private `game/ddraw.dll`(dxwrapper)은 로드되지 않았다.
  1600×1200을 본 유일한 run(lap148)은 inline `ddraw=n,b`였다.
- **판정 3: 바이트 계약 자체는 승인이다.** old pin `918e…a5a2`는 기계 강제되고, 3개 변경 라인은
  각 1회·비중첩이며, `restore()`는 fail-closed다. 프로필을 폐기하지 마라.

### 이번 바퀴의 단 하나의 가설

> 승인 candidate `f0ce…6785`가 private `dxwrapper.ini`에 **실제로 설치되고** private
> `game/ddraw.dll`(dxwrapper)이 **실제로 로드되면**, 논리 surface 800×600을 유지한 채
> client 1600×1200/scale 2.0×2.0이 나오고 lap150의 선변환 없는 (184,560) 입력이 PS9→PS7→PS3에
> 도달한다.

### 해야 할 변경 (최소 3개, 이 범위 밖 적층 금지)

1. `patches/resolution/dxwrapper_config.py`
   - `CANDIDATE_SHA256 = "f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785"` pin 추가.
   - `install_private(game_root)` / `uninstall_private(game_root)` 추가:
     game_root가 `local/runtime/<run>/game` 아래인지 **positive allow-list로 확인**(아니면 거부),
     symlink 거부, 현재 ini SHA == `SOURCE_SHA256` 확인 → `.original-backup` 기록 →
     `build()` 결과가 `CANDIDATE_SHA256`과 **일치할 때만** in-place 설치 → 설치 후 재해시로 증명.
     `uninstall_private`은 기존 `restore()` 검사(backup/candidate 양쪽 SHA)를 그대로 쓴다.
   - targeted 테스트에 candidate SHA pin과 보호경로/비-private target 거부 케이스를 추가한다.
   - **재계산값이 pin과 다르면 STOP하고 승격하라. pin을 새 값으로 갱신해 통과시키지 마라.**
2. `tools/runtime_env.py` — `g1-presentation-trace`에 opt-in 플래그 1개(예 `--dxwrapper-2x`).
   켜졌을 때만 (a) 위 install 호출과 종료 시 uninstall, (b) **그 실행의 `WINEDLLOVERRIDES`만**
   `ddraw=n,b`, (c) evidence/provenance에 ini old/candidate SHA, override 값, 실제 로드된 ddraw
   모듈 경로를 기록. **기본값은 `ddraw=b` 그대로 두어 기존 baseline을 바꾸지 마라.**
3. 입력 계약(lap150)은 손대지 마라. 선변환·좌표 스윕·timeout 증가·추가 설정/DLL 금지.

### 실행 계약

기존 본문과 같다(새 helper/bridge, 새 private copy/prefix/미사용 display, builder `--out-dir`
child 미리 생성 금지, 클릭 1회, 실패 시 재시도 금지). 순서는 `make check` →
`bash checks/safety.sh check` → prepare(`--source` 생략) → trace 정확히 1회.
**lap153도 실행 권한 거부로 Fast/safety/candidate 재계산을 SKIP했다. 이 공백은 네가 메운다.**

### PASS / FAIL 판정식

- PASS: 설치된 ini SHA `f0ce…6785` + 로드된 ddraw가 private `game/ddraw.dll`
  (`3bc7230d…bd19`) + 논리 surface 800×600 불변 + client 1600×1200 + scale 2.0×2.0 +
  선변환 없는 (184,560) 클릭으로 PS9→PS7→PS3 + 기존 finalization/validator/owned-only cleanup +
  private copy ini byte-exact 원복. 이것도 G1 완료가 아니다(UI 구도·클릭 대응 검수와 사용자
  마일스톤이 남는다).
- FAIL-A: 설치·로드는 증명됐는데 client가 여전히 800×600 → 표시 가설이 반증된다.
  설정을 더 쌓지 말고 증거 보존 후 middle 재판정으로 승격하라.
- FAIL-B: client 1600×1200인데 PS7 미도달 → 선변환 없는 논리좌표 가설이 반증된다.
  다음 단일 변경은 **입력 관측 추가**(bridge가 커서/메시지 좌표를 기록)이며 좌표 보정이 아니다.
- 어느 경우든 `ddraw=n,b`에서는 DirectDraw 구현이 바뀌어 event 수/surface identity가 lap152와
  1:1 비교되지 않을 수 있다. 이는 기대된 차이이며 숨기지 말고 수치로 기록하라.

## 다음 바퀴를 위해 남겨둘 것 (이번엔 구현하지 마라)

좌표 가설이 반증되면, 그때의 단일 변경은 **입력 관측 추가**다. 현재 진단 bridge는 DirectDraw만
계측하고 커서·메시지·버튼 이벤트를 0건 기록하므로, 게임이 실제로 받은 좌표를 아무도 볼 수 없다.
그 상태로는 "결선이 어디서 끊겼는가"에 영원히 답할 수 없다. 관측 설계는 middle tier가 다시 받는다.
