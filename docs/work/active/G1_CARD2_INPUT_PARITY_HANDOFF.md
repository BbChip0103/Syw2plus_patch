# HANDOFF — G1 카드2: 원본/후보 입력 패리티 증거 (middle → work tier)

작성: 2026-09-11 lap169 middle tier(Claude Code `claude-opus-5`, 진단·계획·확인).
근거: `docs/history/laps/20260911_lap169_middle_g1_p5_confirmation_and_scope.md`,
`docs/history/laps/20260911_lap167_middle_g1_close_causality_confirmation.md`(카드2 사전 예고),
`docs/history/laps/20260911_lap73_luna_g1a_private_baseline_evidence.md`(원본 입력 현황),
`docs/work/active/G1_INPUT_COORDINATE_CONTRACT_HANDOFF.md`(lap149 좌표 계약).
**이 카드는 구현 지시이며 작성자는 구현하지 않았다. 승인 범위 밖의 적층을 하지 마라.**

## 왜 이것이 다음 한 가지인가

`docs/DESIGN.md` §G1(21행)의 합격 조건은 **"같은 상태의 원본/후보 캡처와 실제 입력
(선택/드래그/미니맵/메뉴/생산)으로 판정"** 이다. lap148~168은 전부 close/finalization 결함에
쓰였고 그것은 §G1 합격 조건이 아니다. 그 결함은 실재하지만 **판별 probe 없이는 수리를 승인할 수
없다**(lap169 판정5). 그래서 §G1 합격 경로를 먼저 연다.

현재 결손 두 가지:

1. **후보 쪽에 인게임 입력이 없다.** `g1-presentation-trace`는 PS3 도달과 dwell 관측까지만 한다.
   PS3 이후 선택/드래그/미니맵 입력 주입 코드가 없다.
2. **원본 쪽도 미완이다.** 인게임 입력 시퀀스는 `g1_baseline`(`tools/runtime_env.py:2152~2601`)에
   이미 있다 — `unit_select(410,270)` → `production(670,490)` → `drag_select(350,180)` →
   `minimap(150,520)`. 그러나 `_g1_production_click_if_authorized`(`:1540`)가 미승인 primary
   mapping 때문에 **fail-closed로 예외를 던지고 run을 중단**시킨다. production이 순서상 앞에 있어
   `drag_select`/`minimap`은 **원본에서도 한 번도 실행된 적이 없다**(lap73: unit select까지 PASS).

## Stage A — 이번 바퀴에 할 것 (게임 run 금지)

허용 파일: `tools/runtime_env.py`, `tests/` 아래 해당 테스트 파일. **그 외 금지.**

### A-1. production fail-closed를 "중단"에서 "기록하고 계속"으로 바꾼다

- **클릭은 계속 금지다.** `production_click` 콜러블은 여전히 **호출되지 않는다.**
  이것은 게이트 완화가 아니라 제어흐름 변경이다.
- 변경: 예외로 run을 끝내는 대신 입력 레코드에 `status="BLOCKED"`와 기존 사유 문자열을 남기고
  다음 단계(`drag_select`, `minimap`)로 진행한다.
- **세탁 방지 불변식(반드시 테스트로 고정):** production이 BLOCKED인 동안
  `required_inputs`는 **FAIL로 유지되고 `g1_a`/후보 verdict의 overall은 PASS가 될 수 없다.**
  이 불변식을 깨는 구현은 반려다.

### A-2. `g1-presentation-trace`에 opt-in 인게임 입력 시퀀스를 추가한다

- 새 플래그 `--g1-input-sequence`(기본 off). off일 때 기존 거동은 **바이트 그대로** 유지한다.
- on일 때 PS3 도달 뒤, **WM_CLOSE 이전에** `unit_select` → `production`(BLOCKED 기록만) →
  `drag_select` → `minimap`을 `g1_baseline`과 **동일한 순서·동일한 논리 좌표**로 수행한다.
- **좌표는 논리좌표 그대로 쓴다**(`content_crop.x + X`, `content_crop.y + Y`).
  lap149 계약대로 **×2 선변환을 새로 넣지 마라.** `x11_mouse_click.py`에 스케일 인자를 추가하지 마라.
  후보의 client는 1600×1200, logical은 800×600이고 lap154~166이 선변환 없는 `(184,560)`으로
  이미 통과했다. 같은 규칙을 인게임 좌표에도 적용한다.
- 입력 시퀀스를 쓰면 dwell은 0으로 둘 수 있다. dwell과 입력을 같은 run에 겹쳐 넣지 마라.
- 구현 재사용을 우선한다. `g1_baseline`의 입력 단계를 **공용 헬퍼로 추출해 양쪽이 호출**하게 하고,
  두 번째 복사본을 만들지 마라(같은 시퀀스가 두 벌이면 패리티 비교의 의미가 사라진다).

### A-3. 단계별 대조 가능한 증거를 남긴다

각 입력 단계마다 `evidence`에 기록한다:
- 클릭 전/후 스크린샷 경로와 SHA256 (PNG는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/`에
  `YYYYMMDD_HHMMSS_` 접두사로 저장한다)
- `selection_count` 전/후, `camera` 전/후, `ps`/`tick` 전/후
- 사용한 **논리 좌표**와 실제 전송된 root 좌표, `content_crop`, `window.scale`

**BLOCKED로 끝나는 run에서도 증거가 남아야 한다.** 후보 run은 close 결함 때문에 90초 timeout
BLOCKED로 끝날 수 있다. 각 입력 단계의 evidence는 **WM_CLOSE 이전에 디스크로 flush**하라.
close 이후에만 기록되는 자리에 넣으면 이 카드는 실패한다.

### A-4. 회귀 테스트

- production BLOCKED 시 클릭 콜러블 **미호출** + 시퀀스 **계속 진행** + overall **PASS 불가**.
- `--g1-input-sequence` off일 때 기존 경로 불변.
- 논리 좌표가 `content_crop` 오프셋만 더해 전달되고 **스케일이 곱해지지 않음**을
  1600×1200 client / 800×600 logical 조건으로 고정한다(이게 이 카드의 핵심 회귀다).
- `make check`와 `bash checks/safety.sh check`를 통과시키고 **수치를 기록**한다.

Stage A는 여기서 끝난다. **게임을 실행하지 마라.** middle 확인 뒤 Stage B를 연다.
이 저장소의 선례(lap18→19→20→21)와 동일한 절차다.

## Stage B — 아직 착수 승인 아님 (middle 확인 뒤)

원본 run 1회 + 후보 run 1회, 각각 새 private copy / 새 prefix / 새 빈 display, 정확히 1회씩.

```sh
# 원본 (800x600 논리, builtin ddraw)
.venv/bin/python tools/runtime_env.py g1-baseline \
  --manifest <run-A>/manifest.json --screen 1600x1200x24 --timeout 90

# 후보 (1600x1200 client, 논리 800x600, DxWrapper native ddraw)
.venv/bin/python tools/runtime_env.py g1-presentation-trace \
  --manifest <run-B>/manifest.json --screen 1600x1200x24 --timeout 90 \
  --win32-close-helper <fresh-parent>/helper/win32_close_helper.exe \
  --dxwrapper-2x --g1-input-sequence
```

### Stage B 성공/실패 측정식 (미리 읽어라)

- **PASS** = `unit_select` / `drag_select` / `minimap` 세 단계 각각에서, **같은 논리 좌표**를 줬을 때
  후보의 상태 변화가 원본과 **같다**: `selection_count` 델타 일치, `camera` 이동 결과 일치.
  이것이 §G1의 "클릭 좌표 불일치 금지"를 만족시키는 실제 증거다.
- **FAIL** = 어느 한 단계라도 발산. 그 자리에서 **고치지 마라.** 수치와 캡처를 보존하고 승격한다.
- **production은 양쪽 모두 BLOCKED**이므로 §G1 다섯 입력 중 4/5까지만 덮는다.
  **이 카드는 §G1을 닫지 않는다.** production mapping은 별도 승인 대상으로 남는다.
- 픽셀 단위 이미지 동일성은 **판정 기준이 아니다**(`docs/DESIGN.md` §2: 단순 확대 화질 저하 허용).
  판정은 상태 델타와 구도/비율/좌표 대응이다.
- 후보 run이 close 단계에서 BLOCKED로 끝나는 것은 **이 카드의 실패가 아니다**(별도 결함, P6 소관).

## 금지

원본/후보 바이너리 수정, production 클릭 실행, 좌표 스케일 선변환 추가, `--timeout` 값 변경,
dxwrapper 프로필 값 변경, baseline/golden 갱신, 같은 run·prefix·display·build 재사용, 임의 retry,
`runtime_env.py:2602` import 수정, close 방식/순서 변경, Stage A에서의 게임 실행,
production BLOCKED 상태의 verdict를 PASS로 만드는 모든 변경.

---

# lap171 middle 보강 (Claude Code `claude-opus-5`, 진단·계획·확인)

근거: `loop/ESCALATE_SOL`(lap170 Astra)의 인계 1~3과
`docs/history/laps/20260911_lap170_astra_card2_verification_boundary.md` 상위 결정 1~6.
아래는 Astra가 middle에 넘긴 항목의 **결정**이다. 위 lap169 본문과 충돌하면 이 절이 우선한다.
작성자는 구현하지 않았다.

## L171-0. P5 증거 위치 — 해소 (현물 존재, 문서 경로 누락)

실제 경로는 `local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/`다.
lap170이 읽으려 한 `<run>/evidence.json`은 존재하지 않는 경로였다. **산출물 유실이 아니라
경로 기재 오류**다. 이번 바퀴에 `sha256sum`으로 독립 재계산했고 lap168 기록과 일치한다:

- `evidence.json` `309028386476de06ced251686444e04b7c8e7d9c282f7f52e7ed1dbcf7fc7e59`
- `provenance.json` `1b8df1e86bd8956da2bc3d9410afc0cebea83371646ae4a1a720cdac475e1c1b`
- `verdict.json` `319474f8fbe1f5e6d52443a71c75894b581e8ed83299bba60eeee30701138d55`
- `trace.jsonl` = `trace_raw.jsonl` = `aa3934044c5cfb1758d7330b3dab5b3f5a09c0468b5946a81f05d44ee62ceb1b`
  (= `verdict.validator.trace_sha256`)
- `manifest.json` `d59ad3242d4aeb0a8223edd24db3d690b5cab04694d46519d2597df17c7ccd66`

내용 대조도 일치: `overall=PASS`, `validator.status=PASS`, `event_count=651`, `errors=[]`,
`process_exit=0`, `summary_count=1`, `winedlloverrides="ddraw=b"`, 적재 ddraw는
`/usr/lib/i386-linux-gnu/wine/i386-windows/ddraw.dll` 하나이며 evidence 전체에서
`game/ddraw.dll`·`game/dxwrapper.dll` 문자열은 0건, run copy의 보호 EXE는
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`다.
⇒ lap169의 **N CONFIRMED는 현물로 재확인**된다. lap170의 재검증 BLOCKED는 해소한다.

## L171-1. A-1 정정 — BLOCKED면 **효과 대기도 건너뛴다** (필수)

lap169 본문의 A-1은 "예외 대신 BLOCKED 기록 후 계속"까지만 적었다. 그대로 구현하면 실패한다.

`_g1_production_click_if_authorized`(`tools/runtime_env.py:1540`) 바로 다음이
`_wait_state(state, production_changed, ...)`(`:2464`)다. 클릭을 보내지 않았으므로 술어는
영원히 거짓이고, `_wait_state`(`:2138`)에는 **단계별 마감시한이 없어 run 전체 timeout(최대 90초)까지**
0.25초 간격으로 돈다. 결국 production에서 남은 예산을 전부 태우고 timeout 예외로 끝나,
`drag_select`/`minimap`은 **여전히 한 번도 실행되지 않는다** — 이 카드의 목적이 통째로 무산된다.

**결정:** production이 BLOCKED이면 클릭 콜러블뿐 아니라 `production_changed` 대기와
`production_after` 캡처까지 건너뛰고 즉시 다음 단계로 간다. BLOCKED 레코드에는
`before` 상태/캡처와 기존 사유 문자열, `waited=false`를 남긴다.

회귀 테스트는 네 가지를 모두 고정한다: (a) 클릭 콜러블 미호출, (b) production 효과 대기
**미진입**, (c) `drag_select`·`minimap` 단계 도달, (d) production BLOCKED 동안 `required_inputs`
FAIL 유지 및 overall PASS 불가(`:2579~2580`의 5개 태그 전원 PASS 조건).

## L171-2. menu 현황 정정 — 미정의가 아니라 **비대칭**이다

Astra 결정 4는 "메뉴 측정식 없음"으로 봤으나 실제 코드는 다르다. menu는 **양쪽에 이미 있다**:
baseline `:2280~2296`, 후보 `:2772~2789`. 둘 다 논리 좌표 `(184,560)`, 둘 다 PS9→PS7을
`_wait_state`로 확인(미도달이면 예외)하고 전/후 캡처를 남긴다. 후보의 PS9→PS7 전이는
실제 관측된 효과다.

문제는 두 가지다.
1. 후보는 술어 없이 `result="PASS"`를 **무조건** 기록한다. baseline의 추가 조건
   (전/후 캡처 SHA 상이)을 검사하지 않는다.
2. 레코드 키가 비대칭이다 — baseline `content`/`x11`/`expected`/`actual`,
   후보 `logical_content`/`x11_sent`/`scale`. 기계 대조가 불가능하다.

**결정:** A-2의 공용 헬퍼는 **menu 레코드까지 포함**해 양쪽이 같은 필드·같은 술어
(PS9→PS7 **그리고** 전/후 캡처 SHA 상이)를 쓰게 한다. 그 전에는 "menu 포함 4/5" 주장을 하지 않는다.
STATUS의 4/5 표현도 이에 맞춰 정정했다.

## L171-3. A-5 신설 — Stage B **성립 조건**을 먼저 계측한다

`g1_baseline:2412~2416`은 장면을 `"default two-player random game; map name/seed not exposed by
approved read-only offsets"`, `replay_seed_observed=False`로 기록하고, 재현 식별자를
**same-run fingerprint**로 둔다. 즉 **서로 다른 두 run이 같은 시작 상태라는 근거가 현재 없다.**
고정 논리 좌표 `(410,270)`/`(350,180)`/`(150,520)`은 맵이 다르면 다른 대상을 친다.
이 상태로 Stage B를 돌리면 델타가 갈려도 "후보 결함"인지 "다른 맵"인지 분리할 수 없다.

**결정:** Stage A에 A-5를 추가한다. 양쪽 경로 모두 **PS3 직후·입력 이전에** 다음을 evidence에
남긴다 — owner별 nation/active_units, 유닛 슬롯 목록(owner·종류·world 좌표), owner0 HQ world 좌표,
초기 camera, 읽기 승인된 범위 내의 맵/월드 경계값, tick.
**새 오프셋이 필요하면 추측해 넣지 말고 blocker로 올린다**(`analysis/memory_maps/` 근거 없는 주소 금지).

## L171-4. Stage B 판정 — 2단 분리와 무반응 배제

lap169 본문의 "델타 일치 = PASS"는 이 절로 대체한다.

- **Tier-1 (장면 독립, 지금도 성립):** `menu`(PS9 타이틀 화면은 무작위 요소가 아니다)와
  좌표 불변식(논리좌표 + `content_crop` 오프셋만, ×2 곱 없음). 두 run 비교가 바로 가능하다.
- **Tier-2 (장면 의존):** `unit_select`/`drag_select`/`minimap`. **A-5 대조 필드가 두 run에서
  일치할 때만** 비교가 성립한다. 불일치면 판정은 **UNKNOWN**이며 PASS도, "발산 FAIL"도 아니다.
- **무반응 배제:** 각 입력은 **양쪽 각각에서 관측된 효과**가 있어야 한다. baseline은 이미
  `_wait_state`로 무반응 시 예외다(`:2432`, `:2482`, `:2502`). 후보 `--g1-input-sequence`도 같은
  술어를 쓰고 효과 미관측은 FAIL로 기록한다. **어느 쪽이든 변화 없음이면 그 입력은 PASS 불가.**
- **측정식과 허용오차:** `unit_select`·`drag_select`는 `selection.count` 전/후 **값 자체**가 양쪽
  동일해야 한다(임계 `>=1`/`>=2` 통과만으로는 부족). `minimap`은 `camera_before`가 장면 의존이므로
  **델타가 아니라 camera 절대 목적지**를 비교한다. 상태값은 정수이므로 **허용오차 0**.
  정착 시점은 `_wait_state` 0.25초 폴링에서 술어가 처음 참이 된 표본을 쓰고 그 표본의 tick을 함께
  기록한다. 양쪽 tick 차이는 허용하되 반드시 기록한다.
- **판정 분리:** 입력 비교 관측값 / production BLOCKED / teardown 실패를 각각 별도 필드로 남긴다.
  close 결함은 증거 보존 방식의 이유가 될 수 있으나 overall·validator·`process_exit`·summary 요구를
  완화하는 근거가 아니다. G1 출하 전 종료 결함 해소 요구는 유지한다.

## L171-5. A-3 보강 — 단계별 **즉시** flush

`--g1-input-sequence`는 timeout 예산을 추가로 쓰고 후보 run은 close에서 BLOCKED로 끝날 수 있다.
중간 단계에서 끊겨도 앞 단계 증거가 남아야 하므로 **각 입력 단계 직후 즉시** 디스크로 flush한다.
close 직전 일괄 flush는 이 카드의 요구를 충족하지 않는다.

## L171-6. 재확인한 Stage A 범위 (work tier 인계분)

A-1(정정판) · A-2(menu 포함 공용 헬퍼) · A-3(단계별 즉시 flush) · A-4(회귀 + `make check` +
safety 수치 기록) · A-5(장면 대조 필드). 허용 파일은 `tools/runtime_env.py`와 `tests/` 아래
해당 테스트뿐이다. **Stage A에서 게임을 실행하지 않는다.** Stage B는 다음 middle 독립 검수 뒤
별도로 연다. P6는 2순위 보류를 유지한다. 활성 카드 2개.

---

# lap173 middle 검수 결과 — Stage A **조건부 반려** (Claude Code `claude-opus-5`, 진단·계획·확인)

근거 전문: `docs/history/laps/20260911_lap173_middle_card2_stageA_verification.md`.
검수 대상 트리: `tools/runtime_env.py` `7a0374e5…3b12fa1fb`,
`tests/test_runtime_env.py` `4d18c5d5…8ea9dfa51`(lap172 기록과 2/2 MATCH).
작성자는 구현하지 않았다. **A-1(a)(b)(c)·A-2·A-3·A-5는 코드로 확인해 승인한다.**
아래 A-6·A-7·A-8만 work tier가 수리하고, 그 뒤 새 middle이 재검수한다. **Stage B는 열지 않는다.**

## A-6 (블로킹). 후보 verdict도 세탁 방지 불변식을 지켜야 한다

`runtime_env.py:3187~3188`의 후보 verdict `overall`은 `error`/`cleanup`/`validator`만 본다.
`--g1-input-sequence` on에서 production이 `BLOCKED`여도 close 결함만 사라지면
`overall="PASS"`가 된다. 지금 PASS가 안 나오는 유일한 이유는 **무관한 close 결함의 우연한 차폐**다.
A-1의 필수 불변식("후보 verdict의 overall은 PASS가 될 수 없다")은 아직 미충족이다.

**요구:** 후보 verdict에 baseline `checks["required_inputs"]`(`:2793~2794`)와 **같은 술어**를 넣는다.
`--g1-input-sequence` on이면 5개 태그(`menu`/`unit_select`/`production`/`drag_select`/`minimap`)가
모두 존재하고 모두 `PASS`일 때만 입력 체크가 참이며, 하나라도 아니면 `overall`은 PASS가 될 수 없다.
off면 입력 체크는 기존 거동대로 판정에 개입하지 않는다(기록만).
추가로 L171-4대로 verdict에 **입력 관측값 / production BLOCKED / teardown 실패를 별도 필드**로 남긴다.
baseline처럼 태그별 `result` 요약을 verdict에 포함하라. 어떤 경우에도 **PASS 조건을 완화하지 마라.**

## A-7 (블로킹). L171-1의 회귀 (d)를 테스트로 고정한다

`tests/test_runtime_env.py`에 `required_inputs`/`overall` 불변식 테스트가 **0건**이다.
(a)(b)(c)는 `test_g1_shared_input_sequence_blocks_production_but_reaches_later_stages`가 덮지만
(d)는 코드로만 성립한다 — A-6의 결손이 정확히 이 공백으로 통과했다.

**요구:** (1) production이 `BLOCKED`인 입력 목록에 대해 baseline `required_inputs`가 False이고
`overall != "PASS"`임을 고정한다. (2) 같은 입력 목록에 대해 **후보 verdict도** `overall != "PASS"`임을
고정한다(A-6 수리 후). (3) 5개 태그가 전부 `PASS`인 가상 목록에서는 입력 체크가 True가 되는
대조 케이스도 함께 넣어 술어가 항상 False인 공허한 테스트가 아님을 보인다.
verdict 조립 로직을 순수 함수로 추출해 게임 실행 없이 단위 테스트할 수 있게 하라.

## A-8 (비블로킹, 같은 바퀴에 처리). 시퀀스 수준에서 클릭 미전송을 고정한다

`tests/test_runtime_env.py:1194`는 `click=lambda _x, _y: None`이라 호출을 기록하지 않는다.
production 단계에서 `click(670, 490)`을 넣어도 현재 테스트는 통과한다.

**요구:** 시퀀스 테스트의 `click`/`drag`가 좌표를 기록하게 바꾸고, 전송된 좌표에 `(670, 490)`이
**한 번도 없음**을 단언한다. 동시에 `unit_select (410,270)`, `drag (350,180)->(550,350)`,
`minimap (150,520)`이 **스케일이 곱해지지 않은 논리 좌표 그대로** 전달되는지도 같은 테스트에서
단언한다(client 1600×1200 / logical 800×600 조건, lap149 계약).

## A-9 (기록 요구, 코드 변경 아님). Stage B 예산 판단을 명시하라

L171-1이 요구한 `_wait_state` 예산 판단이 lap172 기록에 없다. `--g1-input-sequence`는 PS3 이후
`_wait_state`를 3회 추가하며(`:2061`, `:2110`, `:2140`) 하나라도 무반응이면 run 전체 timeout(≤90초)을
소진해 close/finalization 증거까지 잃는다. 다음 work 기록에 (a) 단계별 마감시한 도입 여부와 근거,
(b) 90초 예산 안에서 단계별 소요를 어떻게 실측할지를 **명시**한다. Stage B는 이 판단 없이 열지 않는다.

## 승인된 채로 유지되는 것 (다시 건드리지 마라)

`_g1_run_input_sequence` 공용 헬퍼 구조, menu 대칭 술어 `_g1_menu_input_pass`, `_g1_input_geometry`의
무-선변환 좌표 계약, 단계별 즉시 flush(`_g1_flush_input_stage`), `_g1_scene_snapshot`의 A-5 필드와
승인 주소(`0xB3DE34/36`, camera `0xB42D7C`). **새 오프셋 추가 금지.**
`--g1-input-sequence` off 경로는 lap172에서 이미 엄격해졌다(menu 술어 실패 시 예외,
scene 상세 state 부재 시 예외) — 이는 L171-2/L171-3의 귀결로 승인하되, lap168 P5 대조군을
재실행하면 이전과 다른 지점에서 중단될 수 있음을 다음 바퀴가 새 회귀로 오독하지 않게 한다.

---

# lap175 middle 재검수 결과 — A-6·A-7·A-8 승인, **Stage A 승인 보류** (Claude Code `claude-opus-5`)

근거 전문: `docs/history/laps/20260911_lap175_middle_card2_stageA_reverification.md`.
검수 대상 SHA는 lap174 기록과 2/2 MATCH: `tools/runtime_env.py`
`8893761d…41bdc9c`, `tests/test_runtime_env.py` `81c34cc6…77ea3567`. 작성자는 구현하지 않았다.

## 승인 (다시 건드리지 마라)

- **A-6 승인.** `_g1_input_verdict`(`:1967`) 술어는 `not enabled or (len==5 and 집합일치 and
  all PASS)`로 의도대로 묶인다. `_g1_presentation_verdict`(`:2020`) overall이 이를 AND로 포함하고
  호출부 `:3282`가 `inputs`/`g1_input_sequence`를 전달한다. baseline `:2888`/`:2895`가 **같은 함수**를
  쓴다. 입력 관측·production BLOCKED·teardown은 `:2024~2033`의 별도 필드다. off 모드는 비개입.
- **A-7 승인.** `tests:1224`가 양쪽 `overall != "PASS"`를, `tests:1251`이 5개 전원 PASS 대조 케이스를
  고정한다. 공허한 테스트가 아니다.
- **A-8 승인.** `tests:1215~1221`이 전송 좌표 `[(410,270),(150,520)]` / drag `(350,180,550,350)`,
  production `(670,490)` 미전송, `scale=(2.0,2.0)`에서도 `x11 = crop + 논리좌표`(`[447,311]`,
  `[387,221]`, drag_to `[587,391]`, `[187,561]`)를 단언한다. lap149 무-선변환 계약 유지.

## A-9R (블로킹). A-9 기록을 **세 개의 실제 wait** 기준으로 보강한다

lap174의 근거는 production 한 건뿐이고 실제로 대기하는 세 wait의 예산 판단이 없다.
`_wait_state`(`:2502`)는 `started + timeout` 공용 마감시한만 갖는다. **이번 바퀴 실측**:
P5 evidence 총 `elapsed_seconds=40.712`에 dwell 30초 ⇒ 기동→PS3 **≈8.4초**, close+finalization
**≈2.3초**(builtin 대조군). lap166 P4의 후보 close 정체는 **≈50초**.
⇒ `--g1-input-sequence`(dwell 0) 후보 run은 PS3 이후 **약 81초**를 세 입력 wait와
close/finalization **전체가 공유**한다. 다음 work 기록이 반드시 다뤄야 할 귀결:

1. 한 단계라도 무반응이면 그 단계가 ~81초를 전부 태우고 예외를 던진다. `_wait_state`는
   `record()`/`flush()` **이전에** 던지므로 **그 단계와 이후 단계 증거가 전혀 남지 않는다.**
   1회·재시도 금지인 Stage B가 거의 무정보로 끝날 수 있다.
2. 입력이 ~30초를 넘기면 후보 close 정체 관측 구간이 잘린다.
3. `_wait_state` 예외 메시지는 "효과 없음"과 "예산 소진"이 **동일**하다. `elapsed_seconds`는
   run 전체분만 남으므로 **FAIL과 UNKNOWN을 기계적으로 분리할 수 없다.**

**요구:** 각 단계 진입 시각과 잔여 예산을 남겨 FAIL / UNKNOWN(예산 소진)을 분리하는 방법을
명시한다. 단계별 마감시한 도입 여부는 여전히 work tier의 결정이며, **도입을 강제하지 않는다.**
다만 도입하지 않는다면 위 1~3을 감수하는 근거를 기록해야 한다.

## A-10 (비블로킹, 같은 바퀴에 처리). off 모드 비개입 회귀 1건

`input_sequence=False` / `enabled=False` 회귀가 **0건**이다. 코드는 정적으로 옳고 실패 방향도
안전(거짓 BLOCKED)이지만, lap173이 반려한 "코드로만 성립하는 불변식"과 같은 부류다.
off 모드에서 production `BLOCKED` 입력 목록을 줘도 `required_inputs is True`이고 overall이
기존 거동대로 판정됨을 고정하라.

## 승인 보류 사유 — 필수 게이트 독립 재실행 SKIP(권한)

이 비대화형 세션은 `make check` / `pytest` / `bash checks/safety.sh check` 호출이 승인 대기로
차단돼 실행하지 못했다(lap171과 같은 제약). ⑥에 따라 lap174의 `198 passed` / `SAFETY_PASS`를
독립 검수 결과로 승격하지 않는다. **Stage A는 A-9R·A-10 처리 + 게이트 실제 재현 뒤에 승인한다.
그때까지 Stage B·P6·게임 실행은 열지 않는다.**

부수 확인: 후보 verdict `checks`가 `required_inputs` 하나로 좁아졌으나 소비자는 `tests:1245`뿐
(`tools/`·`checks/` 0건)이라 하위 호환 파손은 없다. P5 산출물은 재생성되지 않았다
(evidence `309028…fc7e59`, verdict `319474…1138d55` — lap171과 일치).

# lap176 work 결과 — A-9R 기록 보강 및 A-10 회귀

- **A-9R 결정:** 이번 바퀴에는 단계별 deadline이나 `_wait_state` 동작을 바꾸지 않았다. 현재
  `unit_select`·`drag_select`·`minimap`의 세 실제 wait가 `started + timeout` 공용 deadline을
  공유하므로, 단계별 deadline을 지금 도입하면 입력 효과 판정과 close-stall 관측을 동시에 바꾸는
  별도 가설이 된다. Stage A의 허용 범위와 기존 회귀를 보존하기 위해 기록·검증만 수행했다.
- **Stage B 전 필수 기록 방법:** 각 단계 진입 직전에 `stage`, `entered_elapsed`(run 시작부터의
  monotonic 경과초), `remaining_budget_before = max(0, timeout - (now - started))`를 evidence에
  flush한다. wait 종료/예외 직후에도 `finished_elapsed`, `remaining_budget_after`, 관측된
  before/after tick, predicate 관측 여부를 같은 단계 레코드에 flush한다. `remaining_budget_after`
  가 0인 공용 deadline 소진은 `UNKNOWN_BUDGET_EXHAUSTED`로, 단계별 deadline 안에서 효과가
  관측되지 않아 종료한 경우만 `FAIL_NO_EFFECT`로 분류한다. 즉 현재처럼 공용 deadline에서만
  예외를 내는 구현은 두 결과를 기계적으로 분리할 수 없으므로, Stage B 전에 단계 deadline 또는
  동등한 구조화 timeout 원인과 이 레코드를 구현·컨펌해야 한다. 그 전에는 무반응을 PASS로
  승격하지 않고 `UNKNOWN`으로 보류한다.
- **세 wait의 현재 위험:** 한 단계 무반응은 약 81초의 남은 공용 예산을 소진해 `record()`/
  `flush()` 전에 예외를 낼 수 있고, 그 단계와 이후 evidence를 잃는다. 입력이 약 30초를 넘으면
  후보 close-stall 관측 구간이 잘리며, 현재 예외 메시지와 run-wide `elapsed_seconds`만으로는
  FAIL/예산 소진 UNKNOWN을 구분할 수 없다. 위 기록 방식은 이 세 문제를 Stage B 착수 조건으로
  명시한다.
- **A-10 PASS:** `tests/test_runtime_env.py::test_g1_input_verdict_off_mode_does_not_block_existing_verdict`
  가 production `BLOCKED` 목록에서도 `enabled=False`의 `required_inputs=True`, baseline·후보
  기존 verdict `overall=PASS`, 별도 `production.blocked=True`를 고정한다.
- 게임 실행·Stage B·P6는 수행하지 않았다. Stage A는 중간 tier 독립 판정 전까지 닫힌다.

---

# lap177 middle 판정 — Stage A **내용 승인**, Stage B는 A-11까지 CLOSED (Claude Code `claude-opus-5`)

근거 전문: `docs/history/laps/20260911_lap177_middle_card2_stageA_decision.md`.
검수 대상 SHA는 lap176 기록과 2/2 MATCH: `tools/runtime_env.py`
`8893761d…41bdc9c`, `tests/test_runtime_env.py` `ab523a67…c565762`. 작성자는 구현하지 않았다.

## 승인 (다시 건드리지 마라)

- **A-9R 승인.** lap176의 세 구조적 주장을 코드로 독립 재확인했다. `_wait_state`(`:2502~2513`)는
  `started + timeout` 공용 마감시한만 갖고, 후보 `candidate_wait`(`:3162`)와 baseline(`:2811`)이
  같은 값을 넘긴다. `wait`(`:2162`/`:2211`/`:2241`)는 대응 `record`(`:2171`/`:2220`/`:2250`)
  **이전에** 예외를 던지므로 무반응 단계와 이후 증거가 모두 사라진다. `:2513` 예외 메시지는
  "효과 없음"과 "예산 소진"이 동일하다. production은 wait에 진입하지 않는다(`:2190~2204`).
  예산 산술도 재계산해 일치했다 — P5 evidence dwell 표본 `30.0` 직후 run 표본 `38.438`,
  마지막 `40.712` ⇒ 기동→PS3 `8.438초`, close+finalization `2.274초`, PS3 이후 공유 예산 `≈81.6초`.
- **A-10 승인.** `tests:1265~1288`이 off-mode에서 production `BLOCKED` 목록에 대해
  `required_inputs is True` / `production_blocked is True` / baseline·후보 overall `PASS` /
  `production.blocked is True`를 고정한다. on-mode 대조(`tests:1224`, `:1251`)가 있어 공허하지 않다.
- **Stage A 내용 승인.** A-1~A-5(lap173) · A-6~A-8(lap175) · A-9R·A-10(lap177)로 카드2 Stage A의
  요구 항목은 전부 충족됐다. **이 승인은 정적 코드 근거에 한한다.**

## Stage B가 아직 열리지 않는 두 가지 이유

1. **A-11 미구현(기술 선행조건).** 아래 새 카드.
2. **1단 게이트 독립 재현 UNMET(환경).** 이 비대화형 Claude 세션은 `make check` / `pytest` /
   `checks/safety.sh` / 인라인 `python3 -c`가 전부 "requires approval"로 거부된다. lap171·lap175에
   이어 **3회 연속**이며 work tier의 결함이 아니다. 우회 실행은 시도하지 않았다.
   ⑥에 따라 lap176의 `199 passed`/`SAFETY_PASS`를 독립 검수 결과로 승격하지 않는다.
   해소 경로는 `loop/ESCALATE_SOL` 참조. **Stage B 착수 전에 반드시 해소한다.**

---

## A-11 (Stage A2, 블로킹). 단계별 예산과 구조화 timeout 원인을 구현한다

lap176 A-9R이 "Stage B 전에 구현·컨펌해야 한다"고 적은 항목을 **정식 work 카드로 발부**한다.
허용 파일은 `tools/runtime_env.py`와 `tests/test_runtime_env.py`뿐이다. **게임 실행 금지.**

### A-11-1. 단계 진입 전 예산 레코드를 먼저 flush한다

현재 `_g1_run_input_sequence`의 `record()`(`:2145~2155`)는 wait **이후에만** 호출된다.
단계 진입 직전에 `stage`, `entered_elapsed`(run `started` 기준 monotonic 경과초),
`remaining_budget_before = max(0, timeout - (now - started))`, 진입 시 tick을 **먼저** 즉시 flush하라.
그래야 wait가 예외로 끝나도 그 단계의 진입 기록이 남는다. 기존 `record()`의 사후 필드는 유지한다.

### A-11-2. 단계별 마감시한을 도입하고 종료 원인을 구조화한다

`_wait_state`에 단계 예산을 넘길 수 있게 하고(기존 호출부의 거동은 바꾸지 말 것), 종료 시
`finished_elapsed`, `remaining_budget_after`, predicate 관측 여부, 종료 tick을 같은 단계 레코드에
flush한다. 분류는 lap176 기록대로 고정한다:
- 단계 마감시한 안에서 효과 미관측 → `FAIL_NO_EFFECT`
- 공용 `started + timeout` 소진(`remaining_budget_after == 0`) → `UNKNOWN_BUDGET_EXHAUSTED`
`UNKNOWN`은 **PASS로 승격하지 않는다.** 두 경우 모두 이후 단계로 진행할지 여부는 구현자가 정하되
근거를 기록한다.

### A-11-3. 단계 예산 상한은 계측된 수치에서 나온다 (근거 있는 제약)

`timeout=90`, 기동→PS3 `8.438초`, lap166 후보 close 정체 `50.04초`이므로
`8.438 + T + 50.04 <= 90` ⇒ **입력 세 단계 총 소요 `T <= 31.5초`** 여야 close 정체 관측이 잘리지
않는다. 단계 예산 합계가 이 상한을 넘지 않게 하라(예: 단계당 10초). 다른 값을 쓰려면 위 식으로
다시 계산한 근거를 기록한다. **`--timeout` 값 자체는 바꾸지 마라.**

### A-11-4. 회귀

- 단계 마감시한 소진 시 `FAIL_NO_EFFECT`가 기록되고 **진입 레코드가 이미 flush되어 있음**.
- 공용 deadline 소진 시 `UNKNOWN_BUDGET_EXHAUSTED`가 기록되고 `overall`이 PASS가 아님.
- `UNKNOWN` 단계가 있으면 `required_inputs`가 False(= A-6 불변식 유지).
- `--g1-input-sequence` off일 때 기존 거동 불변(A-10 회귀와 같은 계열).
- `make check` / `.venv/bin/python -m pytest -q` / `bash checks/safety.sh check` 수치를 기록한다.

### A-11 금지

원본/후보 바이너리 수정, production 클릭 실행, 좌표 스케일 선변환 추가, `--timeout` 값 변경,
dxwrapper 프로필 변경, baseline/golden 갱신, 게임 실행, Stage B, P6, 승인된 A-1~A-10 구조의 재작성,
새 메모리 오프셋 추가. **PASS 조건 완화는 어떤 형태로도 금지.**

---

## lap179 middle 판정 — A-11 승인, 신규 카드 A-12 (Stage A3)

**A-11 판정: 독립 승인.** A-11-1~A-11-4 전부 코드/회귀로 확인했고, 이 세션이 `make check`
**202 passed** 와 `bash checks/safety.sh check` **SAFETY_PASS** 를 직접 실행해 lap178 수치를
독립 재현했다. lap171·175·177의 3연속 권한 SKIP은 **해소**됐다. source SHA 2/2 MATCH:
`tools/runtime_env.py` `5b56e908…b740509`, `tests/test_runtime_env.py` `ebc38c0b…2a496fca`.
전체 근거: `docs/history/laps/20260911_lap179_middle_a11_verification.md`.

**Stage B는 계속 닫혀 있다.** 이유는 A-11 결손이 아니라, Stage B가 첫 실제 원본/후보 run이며
아래 두 결손이 바로 그 run의 증거를 오염시키는 지점이기 때문이다.

### A-12-1. 단계 예산의 실제 polling 창을 증거에 드러내라

`begin_stage`의 `stage_started`(`tools/runtime_env.py:2196`)는 `read_camera`/`read_selection`/
`capture(...)`/`click(...)` **이전**에 찍혀 그대로 `_wait_state(stage_started=...)`로 간다
(`:2233~2236`, `:2630~2634`). 그래서 predicate 실제 관측 창 = `stage_budget − 사전작업 시간`이다.
실측 probe(사전작업 8초 주입): 관측 창 `1.75초`, poll 8회인데 evidence는 `finished_elapsed: 10.0`,
`FAIL_NO_EFFECT`로만 남아 **"10초 무효과"와 "2초만 봤음"이 구분되지 않는다.**

요구사항:
- 단계 레코드에 wait 실제 시작 시각(예: `wait_started_elapsed`, run `started` 기준)과
  그로부터 파생되는 `effective_poll_window`를 기록한다. 진입 레코드 flush는 그대로 유지한다.
- `_wait_state`가 timeout으로 끝날 때 실제 poll 횟수/첫·마지막 poll 시각을 증거에 남긴다.
- 유효 관측 창이 단계 예산 대비 지나치게 짧으면(임계값은 구현자가 정하되 **근거를 기록**)
  `FAIL_NO_EFFECT`로 단정하지 말고 별도 원인으로 분류한다. 어느 분류도 **PASS가 아니다**.
- 회귀: 사전작업이 예산 대부분을 소비한 경우와 정상 경우가 evidence에서 구분되는지 단언한다.

### A-12-2. 입력 구간 벽시계를 계측하고 `T <= 31.5초`를 실제로 지켜라

lap177 유도식 `8.438 + T + 50.04 <= 90`의 `T`는 PS3 입력 구간 **전체 벽시계**다. 현재 예산 30초는
세 단계의 (사전작업+wait)만 덮고, 그 바깥의 `selection_after`·`production_before`·`drag_after`·
`minimap_after` **4회 scrot 캡처**와 `production`의 `read_production_cell →
_read_g1_command_cell_provenance(..., _sha256(game/ORIGINAL_EXE))`(**EXE 전체 해시**)는 예산 밖이다.
슬랙은 `1.5초`뿐이다.

요구사항:
- PS3 입력 구간 진입/종료 monotonic과 총 소요 `input_phase_elapsed`를 evidence에 기록한다.
- 그 값이 `31.5초`를 넘으면 close 정체 관측이 잘릴 수 있음을 구조화된 경고/원인으로 남긴다
  (조용히 통과시키지 말 것). PASS 조건 완화나 `--timeout` 변경으로 해결하지 **말 것**.
- 예산 밖 구간(4회 캡처 + production provenance)의 소요를 각각 기록해 다음 컨펌이 재계산할 수 있게 한다.
- 회귀: 입력 구간 총 소요가 상한을 넘는 합성 케이스에서 경고/원인이 기록되고 PASS가 아님을 단언한다.

### A-12 참고 (수정 대상 아님)

`menu` 단계 wait(`:2723`, `:3239` 계열)은 단계 예산 없이 공용 마감시한만 쓴다. PS3 이전 구간이라
이번 카드 범위 밖이지만, 여기서 정체하면 전체 예산을 소모한다는 사실을 기록으로만 남긴다.

### A-12 금지

원본/후보 바이너리 수정, production 클릭 실행, 좌표 스케일 선변환 추가, `--timeout` 값 변경,
dxwrapper 프로필 변경, baseline/golden 갱신, **게임 실행**, Stage B, P6,
승인된 A-1~A-11 구조의 재작성, 새 메모리 오프셋 추가. **PASS 조건 완화는 어떤 형태로도 금지.**
`make check` / `.venv/bin/python -m pytest -q` / `bash checks/safety.sh check` 수치를 기록한다.

---

## lap181 middle 판정 — A-12-2 승인, A-12-1 반려, 신규 카드 A-13

작성: 2026-09-11 lap181 middle tier(Claude Code `claude-opus-5`/high, `permission-mode=auto`).
전체 근거: `docs/history/laps/20260911_lap181_middle_a12_verification.md`.
**이 카드는 구현 지시이며 작성자는 구현하지 않았다.**

source SHA 2/2 MATCH: `tools/runtime_env.py` `8bab3131…79269def`,
`tests/test_runtime_env.py` `0c547d30…6f90d83aa6`.
1단 게이트 독립 재현: `make check` **204 passed**, runtime pytest **91**,
Ruff/compileall/mypy(9 files)/**CONTEXT_PASS**/**SAFETY_PASS**. 게임 run 0.

**A-12-2 판정: 승인.** 입력 phase 벽시계, 4회 캡처 + production provenance의 항목별 비용,
`INPUT_PHASE_WALL_CLOCK_EXCEEDED` 구조화 원인, 정상·예외·cleanup 3경로 finalize, 회귀까지 확인했다.

**A-12-1 판정: 반려.** 네 요구 중 셋(관측창 필드, poll 계측, 정상/잘림 회귀)은 충족한다.
미충족은 "**임계값은 구현자가 정하되 근거를 기록**"이다. `_wait_state`의 `window_truncated`가
임계값 없이 `잘림 > 0`에서 참이고, `begin_stage`가 `stage_started`를 사전작업 이전에 찍으므로
실제 run에서는 `wait_started > stage_started`가 항상 성립한다. 가짜 시계 probe(예산 10초):

| 사전작업 | effective_poll_window | classification |
|---|---|---|
| 0.00초 | 10.00 | `FAIL_NO_EFFECT` |
| 0.05초 | 9.95 | `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` |
| 0.30초 | 9.70 | `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` |
| 8.00초 | 2.00 | `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` |

⇒ `FAIL_NO_EFFECT`는 실제 run에서 도달 불가한 죽은 분류다. 9.95초를 관측한 진짜 무효과와
2.00초만 관측한 잘림이 **같은 라벨로 접힌다** — A-12-1이 없애려던 접힘이 방향만 바뀌어 남았다.
PASS 완화는 아니다(세 분류 전부 비-PASS, `_g1_input_verdict` 확인). 그러나 L171-4의 "무반응 배제"가
무효과를 FAIL로 기록하지 못해, Stage B에서 후보 결함과 관측 부족을 분리할 수 없다.

### A-13. 잘림 분류에 근거 있는 임계값을 넣는다

허용 파일: `tools/runtime_env.py`, `tests/test_runtime_env.py`. **그 외 금지.**

- `window_truncated`를 `잘림 > 0`이 아니라 **명시적 임계값**으로 판정한다. 임계값은 구현자가
  정하되 **코드 주석과 lap 기록에 산출 근거를 남긴다**(예: 사전작업 실측 상한, 또는
  `effective_poll_window / stage_budget` 비율). 임계값 상수는 이름 있는 모듈 수준 값으로 둔다.
- 임계값 **이내**의 잘림(사전작업이 예산의 소수만 먹은 정상 run)에서 무효과는 다시
  `FAIL_NO_EFFECT`로 분류돼야 한다. 임계값을 **넘는** 잘림만 `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`다.
- `UNKNOWN_BUDGET_EXHAUSTED`의 우선순위와 의미는 **그대로 유지**한다.
- `effective_poll_window`/`poll_count`/`observed_seconds`/`window_truncated` 등 기존 A-12-1
  증거 필드는 **삭제·개명하지 않는다**. 임계값과 실제 잘림량을 증거에 함께 남긴다.
- 부수(선택): `window_truncated`의 `stage_deadline - wait_started < stage_budget` 절은 앞선 두 절에
  의해 항상 참인 중복이다. 정리해도 되지만 거동을 바꾸지 마라.
- 회귀 4건을 고정한다: (a) 잘림 0 → `FAIL_NO_EFFECT`, (b) 임계값 이내 잘림(예: 0.3초) →
  `FAIL_NO_EFFECT`, (c) 임계값 초과 잘림(예: 8초) → `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`,
  (d) run 예산 소진 → `UNKNOWN_BUDGET_EXHAUSTED`. 각 분류가 **PASS가 아님**도 함께 단언한다.
- `make check` / `.venv/bin/python -m pytest -q` / `bash checks/safety.sh check` 수치를 기록한다.

### A-13 금지

원본/후보 바이너리 수정, production 클릭 실행, 좌표 스케일 선변환 추가, `--timeout` 값 변경,
`G1_INPUT_STAGE_BUDGETS`/`G1_INPUT_PHASE_WALL_CLOCK_BUDGET` 값 변경, `begin_stage`의
`stage_started` 위치 이동(A-12 검수에서 유지로 결정), dxwrapper 프로필 변경, baseline/golden 갱신,
**게임 실행**, Stage B, P6, 승인된 A-1~A-12-2 구조의 재작성, 새 메모리 오프셋 추가.
**PASS 조건 완화는 어떤 형태로도 금지.**

## lap183 middle 검수 (Claude Code claude-opus-5/high)

source SHA **2/2 MATCH**. 1단 게이트 독립 재현: `make check` **205 passed**,
runtime pytest **92**, Ruff/compileall/mypy(9 files)/**CONTEXT_PASS**/**SAFETY_PASS**. 게임 run 0.

**A-13 판정: 승인.** `G1_INPUT_MAX_TRUNCATION_RATIO = 0.25`(`tools/runtime_env.py:1990`)는
이름 있는 모듈 상수이고, A-13이 허용한 두 근거 형태 중 `effective_poll_window / stage_budget`
비율 형태를 채택했다. 독립 경계 probe(가짜 시계, 예산 10초 / run 여유 20초):

| 사전작업 | effective_poll_window | classification |
|---|---|---|
| 0.00초 | 10.00 | `FAIL_NO_EFFECT` |
| 0.05초 | 9.95 | `FAIL_NO_EFFECT` |
| 0.30초 | 9.70 | `FAIL_NO_EFFECT` |
| 2.5000초 | 7.50 | `FAIL_NO_EFFECT` |
| 2.5001초 | 7.50 | `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` |
| 8.00초 | 2.00 | `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` |

⇒ lap181이 지적한 죽은 분류(`FAIL_NO_EFFECT` 도달 불가)는 해소됐다. 경계는 엄격 부등호이며
단조롭다. `UNKNOWN_BUDGET_EXHAUSTED` 우선순위는 유지됐고, run 예산이 더 빡빡한 경우
`stage_deadline == stage_started + stage_budget`이 거짓이라 `window_truncated`가 참이 될 수 없어
BUDGET_EXHAUSTED로만 귀결된다. A-12 evidence 필드는 무삭제·무개명이며
`truncation_seconds`·`truncation_threshold_seconds`가 추가돼 timeout 경로에서 flush된다.
금지 항목(`G1_INPUT_STAGE_BUDGETS`, `G1_INPUT_PHASE_WALL_CLOCK_BUDGET`, `stage_started` 위치,
`ORIGINAL_SHA256`)은 전부 무변경이다.

### A-14. 임계값 근거 표기를 실제 provenance로 정정한다

허용 파일: `tools/runtime_env.py`(주석/evidence 정밀도만), `tests/test_runtime_env.py`,
`docs/history/laps/20260911_lap182_luna_a13_threshold.md`. **그 외 금지.**

- `tools/runtime_env.py:1987~1989` 주석의 "the **measured** normal pre-poll work was <=0.30s
  (lap181)"는 사실이 아니다. lap181 원문은 0.30초를 **가짜 시계 probe 입력**으로 명시했고,
  이 프로젝트의 실제 게임 run은 0회라 실측 사전작업 시간은 존재하지 않는다.
  주석을 **설계 가정**으로 정직하게 다시 쓴다: 채택 근거는
  `effective_poll_window / stage_budget >= 0.75` 비율이며, 실측 사전작업 분포는 **미측정**이고
  첫 실제 run에서 반드시 기록해 재평가한다는 점을 남긴다. 값 0.25는 바꾸지 마라.
- lap182 기록의 "lap181의 정상 사전작업 관측 상한 0.30초" 문장도 같은 이유로 정정한다.
  원문 삭제가 아니라 정정 주석을 덧붙이는 방식으로 provenance를 보존한다.
- `truncation_seconds`는 소수 3자리 반올림이라 2.4999초와 2.5001초가 evidence에서 똑같이
  `2.5`로 보이면서 `window_truncated`만 다르다. 경계 run의 evidence만으로 분류 이유를
  재구성할 수 있도록 판정에 쓰인 비교 결과를 명시적으로 남긴다(예: `truncation_ratio`를
  충분한 자리수로 추가). 기존 필드는 삭제·개명하지 않는다.
- 회귀: 경계 근처(임계값 바로 아래/바로 위) 두 run의 evidence가 **서로 구분 가능**함을 단언한다.
- `make check` / `.venv/bin/python -m pytest -q tests/test_runtime_env.py` /
  `bash checks/safety.sh check` 수치를 기록한다.

### A-14 금지

`G1_INPUT_MAX_TRUNCATION_RATIO` 값 변경, 분류 우선순위 변경, 기존 evidence 필드 삭제·개명,
원본/후보 바이너리 수정, production 클릭 실행, 좌표 스케일 선변환 추가, `--timeout` 변경,
`G1_INPUT_STAGE_BUDGETS`/`G1_INPUT_PHASE_WALL_CLOCK_BUDGET` 변경, `stage_started` 위치 이동,
dxwrapper 프로필 변경, baseline/golden 갱신, **게임 실행**, Stage B, P6,
승인된 A-1~A-13 구조의 재작성, 새 메모리 오프셋 추가. **PASS 조건 완화는 어떤 형태로도 금지.**

### Stage B 상태

계속 닫혀 있다. Stage B는 첫 실제 원본/후보 게임 run이며 마일스톤 경계다.
`docs/feedback/APPROVALS.md`에 사용자 승인은 없다. A-13은 lap183에서 승인됐지만 그것은
**모델 기술 컨펌**이며, Stage B 개시는 사용자 마일스톤 승인이 있어야 한다.
Stage B 첫 run은 실제 `truncation_seconds` 분포를 기록하고 2.5초 임계값을 재평가해야 한다.

---

## Stage B-R — lap191 middle 발행 수리 계약 (middle → work tier)

작성: 2026-09-12 lap191 middle tier(Claude Code `claude-opus-5`, 진단·계획·확인).
근거: `docs/history/laps/20260912_lap191_middle_g1_stageb_root_cause.md`,
검수 대상 `docs/history/laps/20260912_lap190_work_g1_stageb_baseline_block.md`,
선행 확정 `analysis/memory_maps/player_offsets.md`의 lap57(:536)·lap61(:558) 절.
**이 카드는 구현 지시이며 작성자는 구현하지 않았다.**

### 전제 정정 (먼저 읽어라)

lap190과 이전 `loop/ESCALATE_SOL`은 `49B6D0 ineligible`을 하네스 계약 불일치로 귀인했다.
**그 귀인은 기각됐다.** slot1199/type58에서 `0x009C21D4 & 0x08 == 0`인 것은 **원본의 정상·기대
분기**이고 lap57/lap61이 이미 독립 확인했다. 이 run의 `primary_command_table`
(`0x008930A6` = 1,10,14,17,115,190,72,329)이 비어 있지 않다는 사실이 lap61의
"12-slot table이 선행 경계"를 다시 확증한다.

따라서 **"예외를 BLOCKED로 세탁하고 넘어간다"는 표현으로 작업하지 마라.** 고칠 것은
정상 관측을 치명적 오류로 올리는 하네스 쪽 제어흐름이다. 원본 거동은 고칠 대상이 아니다.

### 허용 파일

`tools/runtime_env.py`, `tests/` 아래 해당 테스트 파일. **그 외 금지.**
**게임 run 금지. Stage B 재실행 금지(승인 소진).** 바이너리/baseline/golden 변경 금지.

### R1. production provenance를 판정 경로에서 분리한다

- `_g1_production_click_if_authorized`는 이미 인자를 `del`하고 무조건 BLOCKED를 반환한다.
  provenance는 **증거일 뿐 판정 입력이 아니다.** 따라서 `read_production_cell()` 실패는
  run을 끝내면 안 된다.
- `tools/runtime_env.py:2354` 호출을 감싸서, `_CommandCellSnapshotError`(및 그 하위 진단 필드)를
  잡으면 production 입력 레코드에 `status="BLOCKED"`, 기존 사유 문자열, 그리고
  `provenance_error`/`command_branch`/`alternate_ui_snapshot`/`primary_command_table`을
  **함께 남기고** `drag_select`, `minimap`으로 진행한다.
- **클릭은 여전히 호출되지 않는다.** 이것은 게이트 완화가 아니라 제어흐름 수리다.
- **세탁 방지 불변식(테스트로 고정):** production이 BLOCKED인 동안 `required_inputs`는
  FAIL로 유지되고 verdict `overall`은 PASS가 될 수 없다. A-1 불변식을 그대로 승계한다.
- 회귀 테스트는 반드시 **stable-ineligible 픽스처**(`_command_cell_reader_fixture(branch_type_flags=0)`)로
  `drag_select`/`minimap`이 실제로 실행되는지 단언한다. A-1 테스트가 이 경로를 덮지 않아
  H2 회귀가 생겼다는 점이 이 요구의 이유다.

### R2. 후보 경로 진단 비대칭을 없앤다

- baseline except(`:3156`)만 `_record_g1_command_cell_error`를 부르고 후보 except(`:3530`)는
  부르지 않는다. 후보에도 같은 호출을 추가한다.
- 후보 `read_production_cell`(`:3492`)은 baseline(`:3125`)과 달리 캐시하지 않는다.
  동작 차이를 만들 의도가 없다면 동일하게 맞춘다.

### R3. flush 산출물이 원인 재구성을 가능하게 한다

- 전체 evidence는 `output/g1_baseline.json`에만 있고 `g1_a/evidence.json`은 마지막 flush
  스냅샷이라 `error`/진단 필드가 없다. lap190 보고가 원인 데이터를 놓친 직접 원인이다.
- 종료 시 `g1_a/evidence.json`을 최종 evidence로 한 번 더 쓰거나, verdict에 진단 요약을
  포함시킨다. **기존 필드 삭제·개명 금지.**

### R4. HQ 식별을 fixture 사실에 맞춘다

- `tools/runtime_env.py:2190`의 `owner0_hq_type = 49` 하드코딩 때문에 이 fixture에서
  `owner0_hq_candidates=0`, `owner0_hq_world=null`이 나온다. 그러나 slot1199는
  `analysis/memory_maps/original_qhd_probe_0910.md:64`에서 원본 HQ 초상/스탯 패널로
  독립 확증된 HQ다. 관측된 HQ type은 fixture/nation에 따라 **49/58/70**으로 달라진다.
- type49 고정 술어는 **HQ를 식별할 수 없으므로 판정에 쓰지 마라.** 최소 수리는 관측값을
  그대로 보존하되(`owner0_hq_type`은 삭제하지 말고 provenance로 남긴다), 그것을 근거로
  "HQ 없음"을 주장하지 않는 것이다. **새 HQ 판별 술어를 추측해서 만들지 마라** — 근거 없는
  type 목록 하드코딩은 또 다른 추측이다. 필요하면 UNKNOWN으로 남기고 R5로 올린다.

### R5. 승인 경계 — work tier가 단독 결정하지 마라

`unit_select`/`drag_select`의 기대 문자열은 "owner0 HQ visible"(`:2336`), "HQ and worker"(`:2403`)인데
PASS 술어는 `count>=1` / `count>=2`뿐이라 type을 검사하지 않는다(H3). 이 단언 내용을 바꾸는 것은
**사용자가 승인한 Stage B 비교 run이 무엇을 증명하는지**를 바꾸는 일이다.
또한 승인 범위였던 원본 1회는 lap190에서 **소진**됐다. 따라서:

- R1~R4는 전부 **조이는 방향**이거나 증거 보존이므로 지금 진행해도 된다.
- R5(단언 내용 변경)와 Stage B 재실행은 **새 승인 없이는 금지**다.

### Stage B-R 금지

PASS 조건 완화, `required_inputs`/overall 불변식 완화, production 클릭 실행, 좌표 스케일
선변환 추가, `G1_COMMAND_CELL_TARGET`/예산/임계값 변경, 기존 evidence 필드 삭제·개명,
근거 없는 HQ type 목록 하드코딩, 원본/후보 바이너리 수정, baseline/golden 갱신,
**게임 실행**, Stage B 재실행, P6 착수, 승인된 A-1~A-16 구조의 재작성.

---

## lap193 middle 판정 — Stage B-R R1~R4 **독립 승인**, 신규 비블로킹 카드 N1/N2

판정: 2026-09-12 lap193 middle tier(Claude Code `claude-opus-5`/high, 진단·계획·확인).
근거: `docs/history/laps/20260912_lap193_middle_stagebr_verification.md`.
검수 대상: lap192 구현(`tools/runtime_env.py`
`8955789be2a8f39d221e09a0da1010e896f87b0f464106bcc928d5c372c40bd3`,
`tests/test_runtime_env.py` `7054d441f0ff5bf33e71d0c55397ee4da36f957efe7dd53459a96a03bed1d197`;
lap192 기록값과 2/2 일치). **게임 run 0회.** 이것은 모델 기술 컨펌이며 제품 G1 합격이 아니다.

- **R1 승인.** stable-ineligible fixture에서 4개 입력 태그가 모두 생성되고 production은
  `BLOCKED`/`waited=False`/진단 4필드 보존/클릭 미전송이다. **실제 생성된 inputs**를 그대로
  `_g1_input_verdict`에 넣어 `required_inputs=False`, 후보 `overall=BLOCKED`,
  baseline `overall=FAIL`을 재현했다(합성 리스트가 아니다). `_CommandCellSnapshotError`가 아닌
  예외는 여전히 run을 중단시키므로 catch 범위가 과대하지 않다. eligible fixture에서도 production은
  BLOCKED다 — 게이트가 아니라 제어흐름만 바뀌었다.
- **R2 승인.** 후보 except(`:3567`)가 baseline except(`:3183`)와 동일하게
  `_record_g1_command_cell_error`를 호출하고, 후보 `read_production_cell`(`:3522`)도
  baseline(`:3151`)과 같이 캐시한다.
- **R3 승인.** 두 경로 모두 `finally`에서 per-run `evidence.json`을 최종 기록한다
  (baseline `:3224`, 후보 `:3634`). flush 산출물만으로 원인 재구성이 된다.
- **R4 승인.** `owner0_hq_type`은 `UNKNOWN` provenance로 보존되고, owner0 type 49/58/70/123
  전부에서 HQ 존재·부재를 주장하지 않는다. 추측 type 목록 하드코딩 없음, 판정 소비자 0곳.
- **R5 미수행 확인.** `count>=1`/`count>=2` 술어는 그대로다. 승인 경계를 지켰다.

### N1 (비블로킹, work tier). top-level 진단 요약을 continue 경로에도 남긴다

R1로 run이 더 이상 중단되지 않으므로 이 경로에서는 except 블록이 실행되지 않고, 결과적으로
**top-level** `evidence["command_branch"]`/`["alternate_ui_snapshot"]`/`["primary_command_table"]`/
`["error"]`가 비어 있다(lap193 probe2에서 4/4 부재 확인). 진단은 `evidence["inputs"]`의 production
레코드 안에만 있다. 데이터는 온전하지만 **top-level만 읽는 보고자는 lap190과 같은 종류의 착시를
다시 겪는다**(H5와 같은 계열).

- 최소 수리: production provenance 실패 시 `evidence`에 **요약 한 개**(예:
  `evidence["production_provenance_error"]` 또는 verdict의 진단 요약)를 추가한다.
- **기존 필드 삭제·개명 금지. `inputs` 안의 진단은 그대로 둔다.**
- 이 값은 **판정 입력이 아니다.** `required_inputs`/`overall` 계산식을 건드리지 마라.
- 회귀 테스트는 continue 경로에서 top-level 요약이 존재하고, 그럼에도 `overall`이 PASS가 되지
  않음을 함께 단언한다.

### N2 (비블로킹, work tier). 후보 `evidence.json` 중복 write 정리

후보 경로가 `trace_dir/evidence.json`을 `:3634`와 `:3653`에서 두 번 쓴다(사이에 evidence 변형
없음). 결함은 아니고 중복이다. 하나만 남기되 **최종(cleanup·provenance 이후) write를 남긴다.**

### N1/N2 범위

허용 파일은 `tools/runtime_env.py`와 해당 `tests/`뿐이다. 둘 다 비블로킹이므로 단독 바퀴를
쓸 필요는 없다. **게임 run 금지, Stage B 재실행 금지, R5 금지.**

---

## lap196 middle 판정 — N1/N2 **독립 승인**, R1~R4 회귀 없음, 신규 비블로킹 카드 N3

판정: 2026-09-12 lap196 middle tier(Claude Code `claude-opus-5`/high, 진단·계획·확인).
근거: `docs/history/laps/20260912_lap196_middle_n1n2_verification.md`.
검수 대상: lap195 구현(`tools/runtime_env.py`
`e511ef39748098c8a21ae95255130c92c9355a72e39221f1b1adfe8c80736162`,
`tests/test_runtime_env.py` `7ff0bcd8add7ee02ae690e5daa9e1c27a81f9947b5498c57b77d646fdb15fbcd`;
lap195 기록값과 **2/2 일치**). **게임 run 0회.** 모델 기술 컨펌이며 제품 G1 합격이 아니다.

게이트 독립 재현: `make check` → 211 passed / exit 0, Ruff·compileall·mypy·`CONTEXT_PASS`;
`bash checks/safety.sh check` → `SAFETY_PASS`. 독립 probe 30단언 / 실패 0:
`temp/20260912_014338_lap196_probe_n1n2.py`
(`8bbf6c4e2768df7b2287cd5a3266b6316e1a4d5e06a5f05eb550c2d549c55548`).
probe는 lap192/lap195 테스트 본문을 재사용하지 않은 자체 드라이버이며, 실제
`_g1_flush_input_stage` 배선으로 tmpdir에 쓴 evidence.json을 **디스크에서 되읽어** 판정한다.

- **N1 승인.** stable-ineligible fixture에서 top-level `error`/`command_branch`/
  `alternate_ui_snapshot`/`primary_command_table`이 디스크 evidence에 보존되고, **production 입력
  레코드의 키집합과 동일**하다(이동·삭제 없음). top-level `error`는 레코드의 `provenance_error`와
  문자열이 같다(날조 없음). 기존 fatal `error`를 seed하면 `setdefault`가 덮지 않는다. provenance가
  성공하면 `error`·진단 키를 **만들지 않는다**(허위 오류 없음).
- **N1은 판정 입력이 아니다(확인).** 실제 생성된 inputs로 `required_inputs=False`이고,
  cleanup·validator가 모두 PASS인 상태에서도 `overall=BLOCKED`, verdict `error=None`이다.
  A-1 세탁 방지 불변식이 그대로 유지된다.
- **N2 승인.** 후보 `trace_dir/evidence.json` write는 cleanup·provenance 이후 **1회**뿐이고,
  baseline `g1_dir` 최종 write도 1회로 남아 R3가 회귀하지 않았다.
- **R1~R4 회귀 없음.** 4개 태그 전부 생성, production `BLOCKED`/`waited=False`, `(670,490)`
  미전송, 예외 뒤 drag 실제 실행, `_CommandCellSnapshotError` 외 예외는 여전히 run 중단(catch
  과대 아님), eligible 경로도 production BLOCKED, `owner0_hq_type`은 UNKNOWN provenance.
- **R5 미수행 확인.** `count>=1`/`count>=2` 술어 무변경. 승인 경계를 지켰다.

### 기록 정정 (결함 아님)

lap193/lap195의 "진단 4필드"는 `provenance_error` + 3개 스냅샷을 뜻한다.
`command_cell_diagnostics`는 `49B6D0 ineligible` 예외가 보유하지 않으므로 top-level과 입력 레코드
**양쪽 모두** 없다. N1의 누락이 아님을 키집합 동일성으로 확인했다. 이후 문서는 "4필드" 대신
`provenance_error + command_branch + alternate_ui_snapshot + primary_command_table`로 적는다.

### N3 (비블로킹, work tier). 비치명 진단과 fatal error를 구분 가능하게 한다

N1은 비치명 provenance 진단을 fatal except 블록(`:3198` baseline / `:3582` 후보)과 **같은**
top-level `error` 키에 넣는다. 그 결과 `evidence.json["error"]`는 non-null인데
`verdict.json["error"]`는 null인 상태가 **정상적으로** 발생한다(probe에서 재현). evidence만 읽는
보고자는 중단되지 않은 run을 fatal로 오독할 수 있다. 현재 유일한 구분자는 문자열 접두사
(`_CommandCellSnapshotError: ...` vs. fatal 경로의 `str(exc)`)뿐이다.

- 방향은 **과대보고**이므로 PASS 세탁 위험은 아니다. 그래서 비블로킹이고 단독 바퀴가 필요 없다.
- 최소 수리: 구조화된 구분자 하나를 추가한다(예: 승격된 진단에
  `evidence["error_fatal"] = False` 또는 별도 `evidence["production_provenance_error"]` 키 병행).
- **기존 필드 삭제·개명 금지.** `inputs` 안의 진단과 fatal 경로의 `error` 의미를 바꾸지 마라.
- **`required_inputs`/`overall` 계산식을 건드리지 마라.** 이 값은 판정 입력이 아니다.
- 회귀 테스트는 (a) 비치명 경로에서 구분자가 "비치명"을 가리키고, (b) fatal 경로에서 기존
  `error` 의미가 그대로이며, (c) 어느 쪽에서도 `overall`이 PASS가 되지 않음을 함께 단언한다.

### N3 범위

허용 파일은 `tools/runtime_env.py`와 해당 `tests/`뿐이다.
**게임 run 금지, Stage B 재실행 금지, R5 금지.**

## lap198 middle 판정 — N3 승인, 안전 작업 큐 소진

검수자: Claude Code `claude-opus-5`/high (middle, 진단·계획·확인). 이 바퀴는 **문서만** 바꿨고
source/tests/EXE/DLL/assets/baseline/golden 무변경, 게임 run 0회다.

검수 대상 해시 2/2 일치(검수 전후 동일): `tools/runtime_env.py` `fd28e3a1...`,
`tests/test_runtime_env.py` `9082d156...`.
게이트 독립 재현: `make check` → **213 passed / exit 0** (Ruff·compileall·mypy 9 files·CONTEXT_PASS);
`bash checks/safety.sh check` → **SAFETY_PASS**.
독립 probe **35단언 / 실패 0**, `tests/test_runtime_env.py` 본문을 재사용하지 않은 자체 드라이버로
실제 `_g1_flush_input_stage` 배선이 tmpdir에 쓴 `evidence.json`을 디스크에서 되읽어 판정한다.
사본: `temp/20260912_lap198_probe_n3.py` (`ea7fefb0...`).

- **N3 (a) 승인.** 비치명 경로에서 디스크 `evidence["production_provenance_error"]`가 production
  레코드의 `provenance_error`와 같고, 기존 top-level `error`도 같은 문자열로 남는다(호환 유지).
  레코드는 이동·삭제되지 않고 키집합 동일. 진단 스냅샷 3종도 함께 승격된다.
- **N3 (b) 승인.** production 레코드에 `provenance_error`가 없거나 레코드 자체가 없는 fatal-only
  flush는 표식을 **만들지 않고** fatal `error`를 그대로 둔다. 허위 표식 없음.
- **N3 (c) 승인.** provenance flush 뒤 outer except의 직접 대입(`:3203`/`:3587`)이 오면 `error`는
  fatal로 갱신되고 표식은 비치명 맥락으로 생존한다 → 두 값이 달라 소비자가 구별 가능하다.
  이미 표식이 있으면 덮어쓰지 않는다.
- **판정 불변식 유지(A-1 세탁 방지).** 표식은 verdict에 실리지 않으며 판정 입력이 아니다.
  production BLOCKED면 cleanup·validator PASS라도 `required_inputs=False`, 후보 `overall=BLOCKED`,
  verdict `error=None`, baseline `overall=FAIL`. 표식이 있어도 정당한 전원 PASS run은 PASS로
  남고, fatal `error`는 전원 PASS여도 `overall`을 BLOCKED로 만든다. 필수 태그(`menu`/`production`)
  누락도 fail-closed다.
- **N1/N2/R1~R4 무회귀.** 후보 최종 evidence write 1회(`:3671`), baseline 1회(`:3245`),
  `owner0_hq_type` UNKNOWN provenance 유지, type 49 고정 술어 없음.
- **R5 미수행 확인.** `count>=1`/`count>=2` 술어 무변경, Stage B 재실행 0회.

### 관측 (후속 카드 발행하지 않음)

`tools/check_runtime_evidence.py`, `tools/check_g1_presentation_trace.py`, `checks/*.py` 어디에도
`evidence["error"]`를 fatal로 읽는 **자동 소비자가 없다.** N3가 겨냥한 오독 위험은 사람/보고자
측에만 있으므로 기계 판독 가능한 표식으로 충분하고 체커 수정은 불필요하다. 새 카드 없음.

### 결과: 승인 없이 진행 가능한 안전 작업 큐가 비었다

lap196이 "승인 대기 중 진행 가능한 안전 작업은 N3뿐"이라고 못박았고 N3는 이 바퀴로 승인됐다.
남은 항목(R5, Stage B 재실행)은 전부 사용자 승인 경계다. loop/PROMPT.md ④.6에 따라 STOP한다.

---

## lap199 middle 판정 — 사용자 승인 범위 재확인, **R5 개봉**, Stage B 재개 인가 조건

판정: 2026-09-12 lap199 middle tier(Claude Code `claude-opus-5`/high, 진단·계획·확인).
근거: `docs/history/laps/20260912_lap199_middle_approval_scope_r5_contract.md`.
**작성자는 구현하지 않았고 게임을 실행하지 않았다.**

### 전제 정정 (먼저 읽어라 — 이 절이 위 「R5. 승인 경계」와 「Stage B 상태」를 대체한다)

위 R5 절과 Stage B 상태 절은 "R5와 Stage B 재실행은 새 승인 없이는 금지", "원본 1회 소진",
"`docs/feedback/APPROVALS.md`에 사용자 승인은 없다"라고 적었다. **그 전제는 더 이상 사실이
아니다.** `docs/feedback/APPROVALS.md`(mtime 2026-09-12 01:56:57, lap198 종료 01:56:11 이후,
lap199 시작 01:57:08 이전 — 즉 사람의 편집)의 현재 문면은 다음을 **명시적으로 포함**한다:

- 승인 범위 = "증거가 성립할 때까지 **bounded repair → fresh validation으로 계속**하는 것"과
  그 독립 검수. 즉 **회차 상한이 아니다. "원본 1회 소진" 논리는 폐기한다.**
- "**R5처럼 Stage B가 무엇을 증명하는지 조이는 변경은 포함한다.**" → **R5는 승인됐다.**
- 금지로 남는 것: "실패를 보존하지 않는 **무변경 blind retry**", 그리고
  **각 검증 run은 이 카드의 exact-once/fresh 규칙**(위 「Stage B」 절: 원본 1회 + 후보 1회,
  각각 새 private copy / 새 prefix / 새 빈 display, 정확히 1회씩; 「금지」 절: 같은
  run·prefix·display·build 재사용, 임의 retry)을 지킨다.
- **여전히 미승인:** 제품 G1 합격·출시 승인, P6 착수, G2~G4.

### 사전 게이트 (lap199에서 집행 완료 — work tier는 재확인만 하면 된다)

원본 EXE SHA256 = `b56986e0...a8ac` (= `checks/safety.py:15` 핀, 일치) ·
`LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS` ·
`make check` → **213 passed** · `tools/check_setup.py --require-game` → `ok:true`,
`original_status:"verified"`, wine/Xvfb/xdotool/scrot/xwininfo/wineserver 전부 present ·
디스크 free 277G, run 1회 ≈ 2.7G · 입력 예산 30.0s ≤ 31.5s(무변경).
**환경상 Stage B를 막는 사유 없음.**

### R5-A (블로킹, work tier). 선택된 개체의 slot/type을 증거로 남긴다

**허용 파일: `tools/runtime_env.py`와 해당 `tests/`뿐. 게임 실행 금지(이 카드 항목에서는).**

- `unit_select`와 `drag_select`의 `before`/`after` 레코드에 선택된 개체의 **`selected_slot`과
  `selected_type`**을 남긴다. 읽기 경로는 **이미 있는 것을 재사용**한다:
  `G1_UNIT_BASE_ADDRESS(0x0066B790) + slot*G1_UNIT_STRIDE(0x758) + G1_UNIT_TYPE_OFFSET(0x8D)`
  BYTE — `tools/runtime_env.py:181-183`, 사용처 `:1598-1610`.
  근거: `analysis/memory_maps/player_offsets.md` lap57(:536)·lap61(:558).
  **새 메모리 오프셋을 추가하거나 추측하지 마라. 새 주소가 필요하다고 판단되면 멈추고 승격하라.**
- **wait 술어·단계 예산·`--timeout`·`G1_INPUT_STAGE_BUDGETS`·
  `G1_INPUT_PHASE_WALL_CLOCK_BUDGET`을 바꾸지 마라.** `count>=1` / `count>=2` 술어는 **그대로**
  둔다. R5는 *기록되는 증거*를 조이는 것이지 in-run 대기 동작을 바꾸는 것이 아니다.
- **절대 type 술어를 만들지 마라.** R4가 확정했듯 HQ type은 fixture/nation에 따라 49/58/70이며
  절대 판별식은 UNKNOWN이다. `type==49` 류의 in-run 판정식은 **R4를 되돌리는 추측이므로 금지**다.
- **실패는 비치명이다.** slot 범위 밖 / 비활성 / `type==0` 등으로 읽기가 실패하면
  `selected_type: "UNKNOWN"` + `selected_type_provenance`(사유 문자열)로 **보존**하고 run을
  계속한다. 예외를 fatal로 올리지 마라 — 정상 원본 분기를 FAIL로 만든 lap190의 실수를
  반복하는 길이다. N3의 `production_provenance_error` 표식 관례를 그대로 따른다.
- **baseline·후보 양쪽 경로에 대칭으로** 적용한다(R2가 고친 비대칭을 재발시키지 마라).
- **세탁 방지 불변식 승계:** `required_inputs`/`overall` 계산식을 건드리지 마라. production이
  BLOCKED인 동안 `overall`은 PASS가 될 수 없다. `selected_type`은 verdict 입력이 아니다.
- 기존 evidence 필드 삭제·개명 금지.

#### R5-A 회귀 테스트 (전부 필수)

1. type 읽기가 성공하는 fixture에서 `unit_select`/`drag_select` 양쪽에, baseline·후보 양쪽
   경로에 `selected_slot`/`selected_type`이 디스크 evidence로 남는다.
2. 읽기 실패 fixture에서 `selected_type=="UNKNOWN"` + provenance가 남고, **run이 중단되지 않으며**
   `drag_select`/`minimap`이 실제로 실행된다(R1 회귀 방지).
3. `selected_type`이 있든 UNKNOWN이든 **`overall`이 PASS로 바뀌지 않는다**(stable-ineligible
   fixture에서 production BLOCKED → `required_inputs=False`, 후보 `overall=BLOCKED`,
   baseline `overall=FAIL`).
4. wait 술어/예산 상수가 값으로 불변임을 단언한다(`count>=1`, `count>=2`, 10.0/10.0/10.0, 31.5).
5. `make check`와 `bash checks/safety.sh check` 통과 + **수치 기록**.

### 다음 middle — R5-A 검수와 **Stage B run 인가**

R5-A를 독립 검수한다(자체 드라이버 probe, 테스트 본문 재사용 금지). 확인 항목:
새 오프셋 추가 여부, 절대 type 술어 혼입 여부, wait/예산 불변, 양쪽 경로 대칭,
UNKNOWN 비치명, `overall` 세탁 없음.

**R5-A가 승인되고 사전 게이트가 여전히 PASS면, 그 middle 바퀴가 Stage B 페어 run을
곧바로 인가한다. 추가 사용자 승인을 다시 기다리지 마라** — 위 승인 문면이 이미 덮는다.
인가 시 원본 run 1회 + 후보 run 1회를 명시 배정하고 각각 새 copy/prefix/display를 못박는다.

### R5-B (비블로킹, run 이후에도 가능). 원본↔후보 비교기

`tools/`에는 두 evidence를 맞대어 Stage B 측정식을 계산하는 도구가 **없다**
(`check_g1_presentation_trace.py`는 단일 trace 검증기다). 지금 상태로 run하면 "델타 일치"가
사람 눈대중이 된다. 다만 evidence는 디스크에 보존되므로 **비교기는 run에 소급 적용할 수 있고,
따라서 run을 막지 않는다.**

- 새 파일 `tools/compare_g1_stage_b.py`: 원본 evidence.json과 후보 evidence.json 두 경로를 받아
  `unit_select`/`drag_select`/`minimap` 각각에 대해 `selection_count` 델타 일치,
  `camera` 이동 결과 일치, `selected_slot`/`selected_type` 일치를 계산해 구조화 verdict를 낸다.
- **`INCONCLUSIVE`는 PASS가 아니다.** 어느 한쪽이 `UNKNOWN`이거나 필드가 없으면 그 차원은
  INCONCLUSIVE이며 전체 verdict를 PASS로 만들 수 없다. 발산은 FAIL이고 **그 자리에서 고치지
  마라** — 수치와 캡처를 보존하고 승격한다.
- production은 양쪽 BLOCKED이므로 5입력 중 4/5까지만 덮는다. **이 비교기도 §G1을 닫지 않는다.**
- 픽셀 동일성은 판정 기준이 아니다(`docs/DESIGN.md` §2).
- 오프라인 fixture로 테스트한다. 게임 실행 불필요.
- **범위 판단 고지:** 승인 문면은 "R5**처럼** 조이는 변경"을 포함한다. 비교기는 그 부류로
  읽었으나 R5 원문에 명시된 항목은 아니다. 다음 middle 또는 사용자가 이 확장을 기각하면
  R5-A만 진행한다.

### lap199 금지

PASS 조건 완화, `required_inputs`/`overall` 불변식 완화, production 클릭 실행,
좌표 스케일 선변환 추가, wait 술어/예산/임계값/`--timeout`/dxwrapper 프로필 변경,
**새 메모리 오프셋 추가·추측**, 근거 없는 HQ type 목록 하드코딩, 기존 evidence 필드 삭제·개명,
원본/후보 바이너리 수정, baseline/golden 갱신, 무변경 blind retry, 같은
run·prefix·display·build 재사용, P6 착수, 승인된 A-1~A-16·R1~R4·N1~N3 구조의 재작성.

---

## lap201 middle 판정 — R5-A 실체 승인, 회귀테스트 미충족으로 **인가 보류**, R5-C 발행

검수: Claude Code `claude-opus-5`/high (middle). 구현 0, 게임 run 0, Stage B 0.
증거: `docs/history/laps/20260912_lap201_middle_r5a_verification.md`,
probe `docs/history/laps/probes/20260912_lap201_r5a_probe.py` → **30 assertions PASS**.
게이트: `make check` **216 passed** / mypy Success / `CONTEXT_PASS`,
`LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.

**확인된 것:** 새 오프셋 0(읽힌 주소는 `0x899024`/`0x899028`/`0x8990D6`/`0x66EB85` 4개),
절대 type 술어 0, wait 술어·예산(10/10/10, 31.5) 불변, baseline·후보 대칭(`:3227`/`:3598`),
count==0이면 개체 상세 미읽음, 모델링된 실패는 UNKNOWN+provenance로 비치명,
end-to-end 4단계 전부 실행, `overall` 세탁 없음.

**승인하지 않은 이유:** 아래 D1(결함)과 D2(카드 필수 회귀테스트 3개 누락).
Stage B 페어 run 인가는 다음 middle로 이월한다. **새 사용자 승인을 기다리는 것이 아니다** —
APPROVALS의 "bounded repair → fresh validation으로 계속" 안의 1회 추가 수리 바퀴다.

### R5-C (블로킹, work tier). 읽기 실패 부류 확장 + 필수 회귀테스트 보충

**허용 파일: `tools/runtime_env.py`와 해당 `tests/`뿐. 이 항목에서 게임 실행 금지.**

**D1.** `_read_g1_selection_evidence`(`tools/runtime_env.py:1345-1362`)는
`_CommandCellSnapshotError`만 잡는다. 실제 reader `patches/population/runtime_driver.read`
(`:43`)는 부분/실패 읽기에서 **`OSError`**를 던지고, R5-A가 새로 추가한 두 읽기
(`G1_UNIT_EXISTS_BASE_ADDRESS + slot*2`, `unit_address + G1_UNIT_TYPE_OFFSET`)에서 그
`OSError`가 전파된다. 이 reader는 `unit_select`/`drag_select`의 **wait 폴링 reader**이므로
읽기 실패 1회가 단계와 이후 입력을 중단시킨다 — 카드 R5-A가 금지한 lap190 실패 모드다.
- 수리: 원시 읽기 오류(`OSError`, `struct.error`)도 **같은 UNKNOWN+provenance 경로**로
  보존한다. provenance 문자열은 기존 `f"{type(exc).__name__}: {exc}"` 관례를 유지한다.
- **`_CommandCellSnapshotError` 경로의 기존 동작·문구를 바꾸지 마라.** `except`를
  `Exception`으로 넓히지 마라(진짜 프로그래밍 오류를 삼킨다). 열거한 부류만 추가한다.
- `_read_selection`(`:1339`)·`_read_g1_command_selection_identity`(`:1623`)·
  `_read_g1_command_cell_provenance_once`의 **기존 예외 계약은 건드리지 마라.**
  production provenance 경로는 N1~N3 그대로 둔다.

**D2.** 카드 R5-A 「회귀 테스트(전부 필수)」 중 1·2·4가 저장소 테스트로 없다.
lap200이 추가한 `tests/test_runtime_env.py:899/911/921`은 전부 reader 단위다.
기존 시퀀스 테스트(`:1198`)는 합성 reader(`lambda: dict(selection)`)를 쓰므로
**실제 주입 reader를 통과하는 저장소 테스트가 0개**다. 다음을 추가한다:
1. 성공 fixture에서 `read_selection=_read_g1_selection_evidence(...)`를 실제로 주입한
   `_g1_run_input_sequence` 실행이 `unit_select.after`와 `drag_select.after`에
   `selected_slot`/`selected_type`을 남기고, `unit_select.before`는 UNKNOWN임을 단언한다.
   baseline·후보 주입 지점이 **동일 reader**임을 단언한다(소스 검사 또는 공용 헬퍼 단언).
2. 읽기 실패 fixture(**`_CommandCellSnapshotError` 1건 + `OSError` 1건 각각**)에서
   UNKNOWN+provenance가 남고 **`drag_select`/`minimap`이 실제로 실행**됨을 단언한다.
   (`OSError` 케이스는 D1 수리의 회귀 테스트이기도 하다.)
4. 상수 불변을 값으로 단언한다: `G1_INPUT_STAGE_BUDGETS == {"unit_select":10.0,
   "drag_select":10.0,"minimap":10.0}`, 합 30.0, `G1_INPUT_PHASE_WALL_CLOCK_BUDGET == 31.5`,
   그리고 wait 술어가 `count>=1`/`count>=2`로 유지됨.
5. `make check`와 `bash checks/safety.sh check`를 실행하고 **수치를 기록**한다.

**금지(lap199 금지 전부 승계).** PASS 조건 완화, `required_inputs`/`overall` 불변식 변경,
production 클릭 실행, 새 메모리 오프셋 추가·추측, 절대 type 술어 도입,
wait 술어/예산/`--timeout`/임계값 변경, 기존 evidence 필드 삭제·개명,
승인된 A-1~A-16·R1~R4·N1~N3·R5-A 구조의 재작성, 무변경 blind retry.

### 다음 middle — R5-A+R5-C 검수와 **Stage B run 인가**

자체 드라이버 probe로 재검수한다(테스트 본문 재사용 금지). 확인:
D1이 열거된 부류만 넓혔는지(`except Exception` 금지), `_CommandCellSnapshotError` 경로 무회귀,
D2 테스트 3종이 실제로 주입 reader/시퀀스를 통과하는지, 새 오프셋·절대 type 술어 부재,
예산·술어 불변, 대칭, `overall` 세탁 없음.

**통과하면 그 바퀴가 Stage B 페어 run을 인가한다. 추가 사용자 승인을 다시 기다리지 마라.**
인가 직전 **사전 게이트를 다시 건다**(경과 시간 때문): 원본 EXE SHA256 핀 일치,
`LOOP_DRY_RUN=0 bash checks/safety.sh check`, `make check`,
`tools/check_setup.py --require-game` `ok:true`/`original_status:verified`,
디스크 여유(run≈2.7G, 페어≈5.4G). 원본 run 1회 + 후보 run 1회를 명시 배정하고
각각 **새 copy/prefix/display**를 못박는다. 제품 G1 합격·출시 승인은 여전히 아니다.

### R5-B (비블로킹, 유지)

`tools/compare_g1_stage_b.py` 미구현. run을 막지 않는다(evidence 소급 적용 가능).
`selected_slot`/`selected_type` 비교 차원은 R5-A가 이미 채웠으므로 비교기 입력은 준비됐다.

---

## lap203 middle 판정 — R5-A+R5-C **독립 승인**, **Stage B 페어 run 인가**

검수: Claude Code `claude-opus-5`/high (middle, 진단·계획·확인). 구현 0, 게임 run 0, Stage B 0.
증거: `docs/history/laps/20260912_lap203_middle_r5ac_verification.md`,
probe `docs/history/laps/probes/20260912_lap203_r5c_probe.py`
(sha256 `2235b23cea86fa1f0a9c30f86cdf1f8327718f499206dde1b5877d9579c5dea8`)
→ **63 assertions PASS**. 테스트 본문은 재사용하지 않았다(AST 검사 + 자체 드라이버).

검수 대상 무변경 해시: `tools/runtime_env.py`
`3add9254f8df892292619940310a40cd38a95b1fd15605da5fd2c9d1f1f2f2c1`,
`tests/test_runtime_env.py` `aa2d2a4326dea1cda9ac866c0e621cf7f4d9c4aa9c8483b0810a88807127ae15`.

**D1 해소.** except 핸들러는 1개이고 catch 집합은 정확히
`{_CommandCellSnapshotError, OSError, struct.error}`다. `Exception`/`BaseException`/bare except
없음. 주입한 `TypeError`는 전파된다. exists/type 두 주소 × `OSError`/`struct.error` 네 조합이
모두 비치명 UNKNOWN+provenance이고 `first_slot`을 보존한다. `_read_selection`과
`_read_g1_command_selection_identity`에는 except 핸들러가 없다(기존 계약 불변).
count 주소 실패는 R5-A 이전과 동일하게 치명이다(폭발 반경 확대 없음).

**D2 해소.** 실제 `_read_g1_selection_evidence`를 주입한 end-to-end에서 4단계가 전부 실행되고,
성공 fixture는 `unit_select.before` UNKNOWN / `unit_select.after`·`drag_select.after` slot 7·type 58을
**flush된 디스크 JSON**에 남긴다. 실패 3종도 4단계 전부 실행하고 UNKNOWN+provenance를 남긴다.
네 경우 모두 `required_inputs=False`·`production_blocked=True`(세탁 없음).
저장소 테스트 `:1278`/`:1306`/`:1328`이 카드 필수 1·2·4를 덮고, 헬퍼 `:1199`가 합성 dict가 아닌
진짜 reader를 호출한다 — lap201이 지적한 "주입 reader 통과 저장소 테스트 0개" 구멍은 메워졌다.

**불변식 재확인.** 새 오프셋 0(읽힌 주소 `0x00899024`/`0x00899028`/`0x008990D6`/`0x0066EB85`),
절대 slot/type 술어 0(시퀀스·verdict 모두), 예산 10/10/10·합 30.0·phase 31.5 불변,
`count>=1`/`count>=2` 불변, `count==0`이면 개체 상세 미읽음,
`read_selection=` 주입 지점 2개가 문자열까지 동일.

### 사전 게이트 — lap203에서 **재집행 완료** (경과 시간 반영)

| 게이트 | 결과 |
|---|---|
| 원본 EXE SHA256 핀 | `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` **일치** |
| `LOOP_DRY_RUN=0 bash checks/safety.sh check` | **`SAFETY_PASS`** |
| `make check` | **221 passed** / Ruff / compileall / mypy **Success (9 files)** / `CONTEXT_PASS`, exit 0 |
| `tools/check_setup.py --require-game` | exit 0, `ok:true`, `original_status:"verified"`, `missing_tools:[]`, `missing_libraries:[]` |
| 디스크 여유 | **276G** avail (run≈2.7G, 페어≈5.4G) |
| 입력 예산 | 30.0s ≤ 31.5s, 무변경 |

**환경상 Stage B를 막는 사유 없음.**

### Stage B 인가 (work tier — 다음 바퀴의 한 가지)

승인 근거는 `docs/feedback/APPROVALS.md` 2026-09-12 01:03 KST 실행 승인이다.
**추가 사용자 승인을 기다리지 마라.** 인가 범위는 아래 **정확히 2회**다.

1. **원본 1회.** 새 `prepare` 산출물(새 private copy / 새 prefix / 새 빈 display)로
   `g1-baseline --screen 1600x1200x24 --timeout 90`.
2. **후보 1회.** **별도의** 새 `prepare` 산출물로
   `g1-presentation-trace --screen 1600x1200x24 --timeout 90 --win32-close-helper <fresh>/helper/win32_close_helper.exe --dxwrapper-2x --g1-input-sequence`.

명령 전문과 판정식은 위 「Stage B」 절과 「Stage B 성공/실패 측정식」을 그대로 쓴다.
run 직전에 `prepare`/`check`가 RC0인지 확인하고, 두 run은 copy·prefix·display·build를
공유하지 않는다. 실패해도 **그 자리에서 고치지 말고** 수치·캡처·evidence를 보존해 승격한다.
무변경 blind retry 금지. 기록에는 원본/후보 manifest·evidence·verdict 해시, 단계별
`selection_count` 델타와 `camera` 결과, `selected_slot`/`selected_type`,
입력 구간 벽시계, production BLOCKED 사유를 남긴다.

**이 인가가 바꾸지 않는 것:** 제품 G1 합격·출시 승인, P6 착수, G2~G4는 여전히 미승인이다.
production은 양쪽 모두 BLOCKED이므로 이 카드는 §G1을 닫지 않는다.

### R5-D (비블로킹, work tier). 주입 지점 대칭을 저장소 테스트로 고정한다

카드 D2-1의 하위 조항 "baseline·후보 주입 지점이 동일 reader임을 단언"은 **저장소 테스트로
여전히 없다.** `:1278`은 같은 헬퍼를 두 번 돌려 결과를 대조할 뿐 `tools/runtime_env.py`의 두
호출 지점을 검사하지 않는다. lap203 probe가 소스 수준에서 확인했으나 probe는 게이트가 아니다.
- 수리: `inspect.getsource(runtime_env)`(또는 파일 읽기)에서 `read_selection=` 주입 줄이
  정확히 2개이고 둘 다 `_read_g1_selection_evidence(read_for_process)`임을 단언하는 테스트 1건.
- **Stage B를 막지 않는다.** 이번 인가는 위 해시로 고정된 현재 소스에 대한 판정이며,
  이 항목이 막는 것은 미래의 편측 변경이다. Stage B run과 같은 바퀴에 넣지 마라(한 바퀴 한 가지).

### 비블로킹 관측 O2 (코드 변경 아님)

`struct.error.__name__`은 `"error"`이므로 provenance가 `"error: unpack requires ..."`로 남는다.
카드가 `f"{type(exc).__name__}: {exc}"` 형식을 못박았으므로 구현은 계약대로다.
Stage B evidence를 읽을 때 이 문자열을 `struct.error`로 해석하라.

---

## lap205 middle 판정 — lap204 원본 FAIL 독립 검수 PASS, 원인은 **판정식 결함**, R6-B 승격

판정: 2026-09-12 lap205 middle tier(Claude Code `claude-opus-5`/high, 진단·계획·확인).
근거: `docs/history/laps/20260912_lap205_middle_g1_stageb_drag_predicate.md`,
검수 대상 `docs/history/laps/20260912_lap204_work_g1_stageb_baseline_fail.md`,
run `local/runtime/20260912_022912_3830565_0`.
**이 절은 판정과 구현 지시이며 작성자는 구현하지 않았다.**

### 검수 결과 (lap204 = PASS, 기록 정확)

lap204의 manifest/evidence/verdict/provenance/inputs 해시 5종을 `sha256sum`으로 독립 재계산해
전부 일치했다. `tools/runtime_env.py` SHA는 lap204와 동일하고, 원본/copy EXE는 `ORIGINAL_SHA256`
핀과 일치한다. 게이트 재집행도 재현됐다: `make check` 221 passed / Ruff / compileall /
mypy Success(9) / `CONTEXT_PASS`, `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
lap204 work의 보존·중단·승격 처리는 계약대로였다. **work tier의 잘못이 아니다.**

### 전제 정정 1 — `FAIL_NO_EFFECT`는 "효과 없음"이 아니다

`tools/runtime_env.py:2898-2901`의 분류기는 예산이 남고 관측창이 잘리지 않은 **모든** 술어
미충족을 `FAIL_NO_EFFECT`로 찍는다. lap204에서 실제로는 **효과가 관측됐다**:
선택 identity가 `1199/type70` → `1198/type21`로 바뀌고 count만 1에 머물렀다.
드래그 입력은 게임에 도달했고 게임은 재선택으로 응답했다. **입력 경로 결함으로 읽지 마라.**

### 전제 정정 2 — 장면 의존성(고정 좌표 미포함) 가설은 기각됐다

`drag_before` 캡처(SHA `16b79b4bf55fe4674654d4469e22a74c15026e0692ed6942fddee744f0d5278a`)에서
본영(체력 4800/4800) 선택 타원 ≈(410,268), 이동 유닛 ≈(415,322)로 **둘 다 사각형
(350,180)-(550,350) 내부**이며 본영 스프라이트 전체(≈x355-470, y185-285)도 완전히 포함된다.
world 델타 (+2,+2) ↔ 화면 델타 ≈(+5,+54)는 isometric 투영과 수치적으로 일치한다.
더욱이 본영을 실제로 선택한 `unit_select` 클릭 (410,270)이 사각형 내부이므로 기하 포함은 자명하다.
**따라서 드래그 좌표를 옮기는 수리는 금지다.** 좌표를 메모리 관측에서 유도하는 것은 카드가 금지한
"좌표 스케일 선변환 추가"이며, 고정 논리 좌표는 이 실험의 전제 자체다.

### 판정 — 원인은 `count>=2` 술어가 근거 없이 절대값으로 박혀 있는 것

`analysis/memory_maps/`에 band-select가 건물을 포함하는지에 대한 역어셈블/관측 근거가 **없다**.
lap191 R5가 이미 기대문자열 "HQ and worker" ↔ type-blind `count>=2` 불일치(H3)를 지적해
승인 대기로 동결했다. `tests/test_runtime_env.py:1364`는 가짜 `wait`가 `count=2`를 주입하므로
이 술어는 **실게임 거동으로 검증된 적이 한 번도 없다**. owner0 fixture가 {본영 1, 이동 유닛 1}인
이상, 건물이 band-select 대상이 아니라면 `count>=2`는 좌표와 무관하게 달성 불가다.
**이 잔여(type70 band-select 가능 여부)는 UNKNOWN으로 남긴다. 추측으로 채우지 마라.**

### 신규 발견 (상위) — 현재 하네스는 페어를 전혀 판정하지 못한다

카드 「Stage B 성공/실패 측정식」(:95)의 PASS는 **원본↔후보 델타 일치**인데 그것을 계산하는
비교기가 없다(R5-B, :938 미구현). 즉 현 하네스는 **단일 원본 run은 과잉 구속**(절대 `>=2`)하고
**페어는 미구속**(parity 검사 0)한다. 두 run이 모두 완주해도 카드의 PASS는 산출되지 않는다.

### R6-A (블로킹 아님, 승인 — 다음 work 바퀴 중 하나에서 구현 가능). 분류기 오라벨 수리

- `wait()`가 관측한 상태가 **before와 달라진 적이 있는지**를 추적해, 변화가 있었으면
  `FAIL_NO_EFFECT`가 아니라 `FAIL_UNEXPECTED_STATE`로 분류한다. `_G1WaitTimeout`에
  `delta_observed: bool`과 **최초로 달라진 스냅샷**을 함께 싣고 evidence/verdict에 보존한다.
- **이것은 게이트 완화가 아니다. 해당 단계는 여전히 FAIL이고 `required_inputs`/`overall`
  불변식은 그대로다.** 진단 정확성만 조이는 변경이다.
- 기존 필드 삭제·개명 금지. `UNKNOWN_BUDGET_EXHAUSTED` /
  `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` 우선순위는 유지한다.
- 회귀: (a) 변화 없음 → `FAIL_NO_EFFECT` 유지, (b) 변화 있고 술어 미충족 →
  `FAIL_UNEXPECTED_STATE` + `delta_observed=True` + 최초 변화 스냅샷 보존,
  (c) 두 경우 모두 `overall`이 PASS가 되지 않음.

### R5-B (재발행, **지금 막히지 않은 유일한 실무 작업**). 원본↔후보 비교기

lap199 R5-B(:938) 내용을 그대로 유지한다. 새 파일 `tools/compare_g1_stage_b.py`.
**게임 실행 불필요, 오프라인 fixture로 테스트, 기존 evidence에 소급 적용 가능.**
`INCONCLUSIVE`는 PASS가 아니다. production은 양쪽 BLOCKED이므로 4/5만 덮고 §G1을 닫지 않는다.
비교 차원에 **장면 동등성 전제**를 추가하라: 두 run의 owner0/owner1 유닛 type 집합과 상대
world 오프셋, `world_bounds`가 다르면 그 페어는 `UNKNOWN_SCENE_MISMATCH`이며 **PASS도 FAIL도
아니다**(seed 미노출 Tier-2 위험의 직접 결과). 절대 slot id는 장면 간 비교 키로 쓰지 마라.

### R6-B (**승격. work tier는 구현하지 마라**). `drag_select` 게이트 재정의

제안 내용(다음 tier가 결정할 안): `drag_select` 게이트를
(a) **비퇴화 조건** — `(count, first_slot)`이 예산 내에 변해야 한다(변하지 않으면 계속 FAIL,
fail-closed), (b) **페어 parity** — 후보의 델타 서명이 원본 기록과 일치해야 한다,
로 바꾸고 `count>=2`는 **비게이팅 진단 기대치**(예: `MULTISELECT_NOT_OBSERVED`)로 강등해
evidence에 보존한다.

**승격 사유(정직한 고지):** 이 변경은 **페어 수준에서는 조이는 방향**이다(오늘은 원본 count=2,
후보 count=5여도 둘 다 통과하며 parity 검사가 0이다). 그러나 **단일 원본 run의 절대 상수를
푸는 방향**이기도 하다. 사용자 승인 문면은 "R5처럼 Stage B가 무엇을 증명하는지 **조이는** 변경"을
포함한다고 적혀 있으므로, 양방향이 섞인 이 변경은 middle 단독 판단 범위를 넘는다.
**Sol/Astra 또는 사용자가 재결하기 전까지 구현 금지.**

### R6-C (보류, run 예산 필요). 선택 스택 전체 판독과 결정적 probe

- `0x00899028`은 `analysis/memory_maps/player_offsets.md:403,:1145,:1152`에 4-byte × 20 slot
  배열(하위 WORD = slot)로 기록돼 있다. 선택 **집합** 전체를 증거로 남기면 "count만 1"과
  "무엇이 선택됐나"를 분리할 수 있다. 새 오프셋이 아니라 기존 배열의 확장 판독이다.
- H-A 잔여를 결정적으로 가르는 실험: 뷰 전체를 덮는 진단용 드래그 1회를 **비게이팅
  DIAGNOSTIC**으로 추가해, 여전히 `count=1`이면 "건물은 band-select 제외" 확정,
  `count=2`면 사각형 크기 문제 확정. **추가 게임 run이 필요하므로 승인된 exact-once 페어
  예산 밖이다.** R6-B와 함께 승격한다.

### lap205 금지

Stage B 후보 run(R6-B 재결 전), 원본 run 재실행·무변경 retry, 드래그/클릭 좌표 변경,
`count>=2`를 PASS로 바꾸는 어떤 단독 변경, `required_inputs`/`overall` 불변식 완화,
production 클릭 실행, `FAIL_NO_EFFECT` 기록을 사후에 덮어쓰기, 기존 evidence 필드 삭제·개명,
건물/HQ type 목록의 근거 없는 하드코딩, 바이너리/baseline/golden 변경, 같은 바퀴에 R5-B와 R6-A 동시 착수.

---

## lap206 work 결과 — R5-B comparator 구현, middle 독립 검수 대기

변경: `tools/compare_g1_stage_b.py`, `tests/test_compare_g1_stage_b.py`, `Makefile`.
게임 실행 0회, 기존 원본/후보 evidence 변경 0회, 바이너리·baseline·golden 변경 0회.

`compare_g1_stage_b.py`는 두 `evidence.json`을 읽기 전용으로 비교한다. 먼저 0·1번 owner의
unit type 집합, 절대 slot id를 사용하지 않은 translation-invariant 상대 world 오프셋, 정확한
`world_bounds`를 검사한다. 장면 불일치는 `UNKNOWN_SCENE_MISMATCH`(PASS/FAIL 아님)이고 장면
필드 누락은 `INCONCLUSIVE`다. 장면이 일치할 때만 `unit_select`/`drag_select`의 count delta와
after selected identity, `minimap`의 절대 camera destination 및 logical geometry를 비교한다.
누락/UNKNOWN은 `INCONCLUSIVE`, 발산/입력 단계 FAIL은 `FAIL`이며 production은
`NOT_COMPARED`로 명시한다.

독립 middle 검수 인계:

1. `tests/test_compare_g1_stage_b.py` 6개 fixture가 PASS/FAIL/INCONCLUSIVE/
   UNKNOWN_SCENE_MISMATCH와 slot-id 비사용을 실제로 고정하는지 확인한다.
2. comparator가 기존 evidence를 변경하거나 게임을 실행하지 않는지, `make check`의 mypy 대상과
   CLI 반환 계약(유일한 PASS만 exit 0)을 확인한다.
3. 실제 보존 pair 적용 결과 `INCONCLUSIVE`(후보 scene/input 부재), production `NOT_COMPARED`를
   확인한다. R6-B 재결 전에는 후보 Stage B run을 실행하지 않는다.

---

## lap207 middle 검수 — R5-B 조건부 반려, work tier로 F1/F4만 인계

검수자: Claude Code `claude-opus-5`/high, middle tier. 코드 변경 0줄, 게임 실행 0회, PNG 0장.
재현 확인: 파일 SHA256 3종 lap206 기록과 일치, 보존 pair `INCONCLUSIVE`/`production=NOT_COMPARED`
재현(exit 2), `pytest tests/test_compare_g1_stage_b.py` **6 passed**(lap206 기록의 "5 passed"는 오기),
`make check` 227 + Ruff + mypy 10 files + `CONTEXT_PASS`, `SAFETY_PASS`.
확인된 좋은 점: scene 키에 절대 slot id 미사용(후보 slot 1199→900 변경에도 장면 판정 불변),
production이 `STAGES` 밖에서 `NOT_COMPARED`, `content`는 논리 800×600 좌표(물리는 `x11`)라
2× 후보가 logical geometry에서 자동 FAIL되지 않음.

### 지금 고칠 것 (work tier, bounded repair — 둘 다 실패를 닫는 엄격화)

**F1 (치명, 부당 PASS).** `_stage_report` minimap 분기의 `camera_changed_baseline/candidate`가
`_camera(before) != _camera(after)`인데 `_camera`는 누락 시 `None`을 돌려준다. 후보 evidence에서
`minimap.before.camera`를 삭제한 probe에서 `camera_changed_candidate=True`가 되고 **overall `PASS`**가
나왔다. 수리: 원본·후보 양쪽의 `before`/`after` camera가 모두 정수쌍으로 읽히지 않으면
`INCONCLUSIVE`(reason은 어느 쪽 어느 필드인지 명시)로 닫고, 그 뒤에만 변화/목적지 술어를 평가한다.
회귀 fixture: 후보 `minimap.before.camera` 누락 → `stages.minimap.status == "INCONCLUSIVE"`이고
overall이 `PASS`가 아님.

**F4 (경미, fail-open).** `_inputs_by_tag`가 만드는 `input_errors`(중복 tag, 비객체 엔트리)가
`status` 산정에 전혀 쓰이지 않는다. 후보 `inputs`에 `unit_select`를 중복 추가한 probe에서
`input_errors`가 채워진 채 **overall `PASS`**가 나왔다. 수리: `input_errors`가 비지 않으면 overall은
`PASS`가 될 수 없다(최소 `INCONCLUSIVE`). 회귀 fixture: 중복 tag → overall != `PASS`.

수리 범위는 `tools/compare_g1_stage_b.py`와 `tests/test_compare_g1_stage_b.py`뿐이다. 기존 evidence,
runtime harness, 좌표, 예산, `required_inputs`/`overall` 불변식, 바이너리/baseline/golden은 건드리지 않는다.

### 지금 고치지 말 것 (승격, 재결 전 구현 금지)

**F2.** `selected_identity`가 `[selected_slot, selected_type]`을 절대 slot id 포함으로 원본↔후보
동일성 비교한다. 장면·count delta·type이 모두 같고 engine slot id만 1199→1100인 probe에서 단계
FAIL → overall FAIL이 나온다. 같은 도구가 장면 키에서는 slot id를 run 간 비교 불가로 배제하면서
판정 술어에서는 동일성을 요구하는 내부 모순이며, slot id의 프로세스 간 안정성 근거는 저장소에 없다.

**F3.** `_stage_report`가 `result != "PASS"`를 최초 검사해 `FAIL`을 낸다. 보존 baseline의
`drag_select.result`는 `FAIL_NO_EFFECT`이고 lap205가 이를 오라벨로 확정했으므로, 후보 evidence가
생기는 즉시 comparator는 한 번도 비교하지 않은 단계에 카드 `FAIL`을 낸다. 또한 timeout 단계의
실제 관측은 `after.last`(slot 1198/type 21)에 있는데 `_selection`은 `after.selection`만 읽어
분쟁 단계의 델타를 구조적으로 읽지 못한다.

F2/F3은 FAIL→UNKNOWN 판정 의미를 바꾸는 변경이므로 R6-B와 같은 승인 경계다. Sol/Astra 또는
사용자 재결 전까지 구현 금지. 후보 Stage B run, 원본 재실행, R6-A/R6-C 착수도 그대로 금지다.

## lap209 — middle 독립 검수 결과 (F1/F4 승인, F5 신규)

검수자: Claude Code `claude-opus-5`/high (middle tier). 코드 변경 0, 게임 실행 0회, PNG 0장.
대상 해시는 lap208 기록과 일치: `tools/compare_g1_stage_b.py`
`b6c78e20…b56f6b`, `tests/test_compare_g1_stage_b.py` `0bfa5fcf…28c06c8f`,
`Makefile` `789f0c8f…12419c92`.
probe 원본: `docs/history/laps/probes/20260912_lap209_r5b_fix_probe.py`
(sha256 `b736226400947bae62fd4486d51dc0cbeec0b61529d07f312868af2393f95ae6`) — 저장소 테스트를
import하지 않고 fixture를 새로 작성했다. 보존 pair 보고서 사본:
`docs/history/laps/probes/20260912_lap209_preserved_pair_report.json`.

**F1 = 승인.** 9종 probe 전부 `INCONCLUSIVE`: 후보 `before.camera` 삭제(`missing=['candidate_before']`),
후보 `after.camera` 삭제, camera `None`, float쌍, 문자열 `"UNKNOWN"`, bool쌍, 3원소, dict, 원본측
`before.camera` 삭제. `_is_int`가 bool을 정수로 오인하지 않는 점도 확인했다.
**F4 = 승인.** 후보 중복 tag, 원본 중복 tag, 비객체 엔트리, `inputs` 비-list 4종 모두 overall
`INCONCLUSIVE`이며 모든 stage가 PASS여도 `PASS`로 닫히지 않는다.
**과잉 차단 없음.** 평행이동 정상 pair는 여전히 `PASS`, camera 목적지 불일치/후보 camera 부동은
여전히 `FAIL`. 보존 pair는 `INCONCLUSIVE`/`NOT_COMPARED`/exit 2로 불변(증거 승격 없음).
기계 게이트: `make check` 229 + Ruff + compileall + mypy 10 files + `CONTEXT_PASS`, `SAFETY_PASS`,
`pytest tests/test_compare_g1_stage_b.py` 8 passed. 테스트 8건 본문을 읽어 가짜 주입 없이 실제
`compare_evidence` 결과를 검사함을 확인했다.

### 지금 고칠 것 (work tier, bounded repair — 실패를 닫는 엄격화)

**F5 (경미, fail-open 잔존).** `_inputs_by_tag`(`tools/compare_g1_stage_b.py:42-44`)가 `tag`가
문자열이 아니거나 없는 input 레코드를 `errors`에 남기지 않고 `continue`로 버린다. probe P4a
(`tag` 키 없는 추가 레코드)와 P4b(`tag: 7`)에서 `input_errors`가 빈 채 overall `PASS`가 나왔다.
필수 3 stage의 tag가 사라진 경우(P4c)는 stage 누락으로 `INCONCLUSIVE`가 되므로 영향은 "필수 3종
밖의 손상된 레코드가 조용히 무시된다"에 한정된다. 수리: 비문자열/누락 tag를 `errors`에 기록해
F4 경로로 overall `PASS`를 막는다. 회귀 fixture 2건(`tag` 키 없음 / 비문자열 `tag`)을 추가하고
기존 8건을 유지한다. 수리 범위는 `tools/compare_g1_stage_b.py`와
`tests/test_compare_g1_stage_b.py`뿐이며 evidence/runtime/좌표/예산/바이너리는 건드리지 않는다.

### 지금 고치지 말 것 (승격 유지)

F2(절대 slot id 동일성), F3(`FAIL_NO_EFFECT` 오라클 상속 + `after.last` 미판독), R6-B(`count>=2`)는
FAIL→UNKNOWN 판정 의미를 바꾸므로 Sol/Astra 또는 사용자 재결 전까지 구현 금지다.
lap209 probe에서 F2(slot만 1199→1100)와 F3(후보 `drag_select.result="FAIL_NO_EFFECT"`)이 여전히
overall `FAIL`임을 확인했다 — 의도된 미변경 상태다. 실제 후보 Stage B run, 원본 재실행,
R6-A/R6-C 착수도 그대로 금지다. 이 검수는 제품 G1 PASS가 아니다.

---

## lap211 — middle 독립 검수 결과 (F5 승인, 신규 F6 차단)

검수자: Claude Code `claude-opus-5`/high (middle tier). 코드 변경 0, 게임 실행 0회, PNG 0장.
대상 해시: `tools/compare_g1_stage_b.py` `7730170e…c729ca4`,
`tests/test_compare_g1_stage_b.py` `0f1ba547…39d68b52`, `Makefile` `789f0c8f…12419c92`,
`tools/runtime_env.py` `3add9254…f1f2f2c1`.
probe 원본: `docs/history/laps/probes/20260912_lap211_r5b_f5_probe.py` (`5e383c1c…25e6526f`),
`docs/history/laps/probes/20260912_lap211_f6_producer_conflict_probe.py` (`c0341561…ead52cfd`).
저장소 테스트를 import하지 않고 fixture를 새로 작성했다(slot 1401/1402/1403, type 70/33/12,
bounds 256×256). 보고서 3종은 같은 디렉터리의 `..._report.json`이다.

**F5 = 승인(ACCEPT).** 25 probe 전부 기대대로였다. 후보측 손상 9종(`tag` 키 누락, int, `None`,
`True`, `False`, float, list, dict, bytes)과 원본측 2종이 모두 정확한 index/문구로
`input_errors`에 남고 overall은 `INCONCLUSIVE`다. index 보고도 정확하다(맨 앞 삽입 → `inputs[0]`,
2건 → `inputs[4]`+`inputs[5]`). 과잉 차단은 없다: 정상 평행이동 pair는 `PASS`, 알 수 없는 문자열
tag와 빈 문자열 tag는 오류가 아니다. F1/F4 회귀는 유지되고, camera 목적지 불일치·후보 camera
부동·selection delta 불일치는 여전히 `FAIL`이며, 손상 레코드가 `FAIL`을 `INCONCLUSIVE`로
세탁하지 않는다. `make check` 231 + Ruff + compileall + mypy 10 files + `CONTEXT_PASS`,
`SAFETY_PASS`, `pytest tests/test_compare_g1_stage_b.py` 10 passed.

### 지금 고칠 것 (work tier, bounded repair) — F6

**F6 (차단).** 보존 pair에 F5를 적용하면 lap209에서 비어 있던 `input_errors.candidate`가
`inputs[1]`/`inputs[2]`의 `tag` 누락 2건으로 바뀐다. 후보 evidence의 `tag`는
`['menu', None, None]`이고 index 1~2는 `{"args": [...], "result": "OBSERVED"}`다.
출처는 `tools/runtime_env.py:3500-3502`의 `record_input()` stub이며, `:3529`에서
`_g1_selector_flow(...)`에 넘겨진다. 원본 경로는 `:3091`에서 같은 함수에 tagged
`input_record`(`_g1_record_input`)를 넘기므로 baseline 9건은 모두 문자열 tag를 갖는다.

그래서 **앞으로의 후보 run은 세 stage가 모두 PASS이고 scene이 일치해도 overall이
`INCONCLUSIVE`**가 된다. 생산자 형태를 본뜬 probe에서 확인했다:
`overall_status_with_observed_records=INCONCLUSIVE`,
untagged 2건만 제거한 대조군 `overall_status_without_observed_records=PASS` (`verdict=CONFIRMED`).
fail-open이 아니라 항상 닫히는 fail-closed이고, 승인된 fresh validation run 1회를 확정 낭비시킨다.

권장 수리(우선순위 순):
1. **후보 selector flow를 원본과 대칭으로 만든다.** `:3529`가 untagged stub 대신 원본 경로와
   같은 tagged recorder(`_g1_record_input` 기반)를 쓰게 해 `solo_mode_setup` 등에 고유한
   문자열 tag를 남긴다. Stage A의 "menu 대칭" 방향과 같고, STATUS의 "실제 후보 scene/input
   evidence 없음" blocker도 함께 줄인다. 중복 tag가 생기지 않도록 원본과 같은 tag 집합을 쓰고,
   F4의 중복 규칙으로 검증한다.
2. 1이 이번 범위에서 과하면, 최소한 `record_input()`이 고유 문자열 tag를 붙이도록만 고친다.
   `args`/`OBSERVED` 스키마는 그대로 두어도 F5/F4는 만족된다.
3. **comparator를 느슨하게 만드는 방향(예: "input처럼 생긴 레코드만 오류로 센다")은 반대한다.**
   lap209가 확인한 F5 fail-open을 다시 연다.

수리 범위는 `tools/runtime_env.py`의 후보 selector flow 기록 경로와 그에 대응하는 저장소 테스트에
한정한다. 좌표·예산·입력 시퀀스·판정식·comparator·evidence 보존본·바이너리는 건드리지 않는다.
회귀는 "후보 run 형태의 evidence에 untagged 레코드가 없다"와 "tag가 원본과 충돌하지 않는다"를
기계로 확인해야 한다. 수리 뒤 다음 middle이 독립 검수하기 전까지 후보 Stage B run은 금지다.

### 지금 고치지 말 것 (승격 유지)

F2(절대 slot id 동일성), F3(`FAIL_NO_EFFECT` 오라클 상속 + `after.last` 미판독),
R6-B(`count>=2`)는 판정 의미를 바꾸므로 Sol/Astra 또는 사용자 재결 전까지 구현 금지다.
원본 재실행, R6-A/R6-C 착수도 그대로 금지다. 이 검수는 제품 G1 PASS가 아니다.

부수 관찰(수리 대상 아님, 기록용): comparator의 장면 비교는 owner 0/1만 본다. 후보에만 있는
owner 2 이상의 추가 유닛은 장면 일치 판정에 영향을 주지 않는다. 현재 2인 fixture에서는 영향이
없지만 G3(9~16인)로 확장할 때 재검토해야 한다.

---

## lap212 — work tier F6 bounded repair 완료, middle 독립 검수 대기

수리 파일: `tools/runtime_env.py`, `tests/test_runtime_env.py`만 변경했다. 후보 selector flow의
untagged `record_input()` stub을 제거하고, 원본·후보가 공용 `_g1_record_selector_input()`을 통해
`_g1_record_input()`의 동일 schema를 사용하게 했다. 따라서 `solo_mode_setup` 같은 고유 문자열
tag, 논리 좌표/`x11` 좌표/scale, 단계 즉시 flush가 후보에도 남는다. comparator, 좌표 계산,
입력 시퀀스, 예산, 보존 evidence, 바이너리는 변경하지 않았다.

독립 재현 결과: F6 과거 probe는 보존 run의 `menu, null, null`을 확인하는 historical evidence라
수정 후에도 그대로 `CONFIRMED`를 재현한다. 이는 보존 evidence를 바꾸지 않았다는 증거이며 수리
실행의 PASS가 아니다. 새 producer helper 직접 검증은 `tag=['solo_mode_setup']`, flush 1회,
`content=[300,220]`, `x11=[337,261]`, `scale=[2.0,2.0]`였다. 보존 pair 비교는 여전히
`INCONCLUSIVE`/exit 2이고 과거 후보의 누락 scene 및 untagged tag 오류가 그대로 남았다.

다음 middle은 새 후보 run 없이 source/test를 독립 검수한다. F6 검수 전에는 Stage B 후보 실행,
원본 재실행, R6-A/R6-C 착수를 금지한다. F2/F3/R6-B 판정 의미 재결과 WM_CLOSE teardown도
여전히 승인 경계다.

---

## lap213 — middle tier F6 독립 검수 = 승인(PASS) + 회귀 공백 1건 인계

검수 방식(게임 실행 0회): `tools/runtime_env.py`/`tests/test_runtime_env.py`의 sha256이 lap212
기록과 일치함을 먼저 확인한 뒤, AST로 원본 `g1_baseline.input_record`와 후보
`g1_presentation_trace.record_input`의 **소스 본문**을 추출해 비교하고, 후보 closure 소스를
그대로 실행해 실제 `_g1_selector_flow`를 두 초기 분기로 구동했다. 마지막에 comparator의
`_inputs_by_tag()`로 F5/F4 관문을 통과시켰다. probe/리포트:
`docs/history/laps/probes/20260912_lap213_f6_producer_review_probe.py` 및 `..._report.json`.

결과: 두 recorder 본문이 closure 이름을 제외하고 동일. 초기 solo/multiplayer 분기 모두 tags
`['multiplayer_mode_normalize','solo_mode_setup']`, untagged 0, `input_errors []`, 기록당 flush
1회, `content=[462,169]`/`x11=[499,210]`/`scale=[2.0,2.0]`로 논리 800×600 좌표 + crop + 2× 계약
유지. 수리 전 stub 형태(`{"args":…,"result":"OBSERVED"}`)는 음성 대조에서 여전히 tag 오류로
잡히므로 probe는 F6을 판별할 수 있다. `make check` 232 passed / Ruff / compileall / mypy 10
files / `CONTEXT_PASS`, `SAFETY_PASS`를 재현했다. 따라서 **F6 bounded repair를 승인한다.**

반증한 가설: `begin_stage`가 append하는 stage 레코드가 같은 tag의 입력 레코드와 중복돼 F4를
상시 발동시키지 않는다. `_g1_run_input_sequence.record()`는 `stage_entry`를 in-place `update`할
뿐 재append하지 않고, `tests/test_runtime_env.py:1321`이 flush된 tag 목록을 4개로 고정한다.

### work tier 인계 — G1-F6-R1 (bounded, 판정 의미 변경 없음, 게임 실행 불필요)

lap212가 추가한 `test_g1_selector_input_recorder_writes_tagged_schema_and_flushes`는 공용
helper `_g1_record_selector_input()`만 검증한다. 그런데 F6의 실제 결함은 helper가 아니라
**helper를 우회한 후보 producer closure**였다. 지금 후보 closure를 다시 untagged stub으로
되돌려도 232개 테스트가 전부 통과한다. producer 수준 가드를 추가하라:
- 원본/후보 selector recorder가 `_g1_record_selector_input()`을 사용하고 `inputs`에 tag 없는
  레코드를 만들지 않음을 고정한다. 소스 수준 가드 선례는 `tests/test_runtime_env.py:1334`의
  `inspect.getsource(_g1_run_input_sequence)`이며, 구동 수준 가드는 위 lap213 probe 방식을 쓴다.
- comparator/좌표/예산/보존 evidence/바이너리는 건드리지 않는다. 실패가 닫히는 방향의 엄격화만이다.

### 기록용 관찰 (수리 대상 아님)

원본 경로는 `tools/runtime_env.py:3154`에서 `player0_ready_auto` 입력 레코드를 남기지만 후보
경로에는 대응 레코드가 없다. comparator `STAGES`는 `(unit_select, drag_select, minimap)`뿐이라
stage 판정과 `input_errors`에 영향이 없다. fresh pair 바퀴에서 "원본에만 있는 준비 상태 증거"로
인지하고, 대칭이 필요하다고 판단되면 그때 별도 카드로 다룬다.

### 지금 고치지 말 것 (승격 유지)

F2/F3/R6-B 재결, 원본 재실행, R6-A/R6-C, WM_CLOSE teardown은 그대로 승인 경계다. F6 승인은
후보 Stage B run을 열지 않으며 제품 G1 PASS나 마일스톤 승인이 아니다.

---

## lap214 — middle tier F2/F3/R6-B 재결 + 신규 S1(장면 통제) 차단

재결 근거와 fixture 대조표 전문은
`docs/history/laps/20260912_lap214_middle_oracle_readjudication.md`,
재현 probe는 `docs/history/laps/probes/20260912_lap214_oracle_readjudication_probe.py`
(저장소 테스트를 import하지 않음). 게임 실행 0회, 코드 변경 0, Fast 232 / `SAFETY_PASS`.

### 확정된 판정 계약 (work tier가 이대로 구현한다)

- **F2**: 절대 slot 동일성을 FAIL 술어에서 뺀다. `selected_slot`을 **그 run의**
  `scene.unit_slots`로 해소해 `(owner, type, anchor 기준 상대 world offset)`으로 바꾸고 그
  튜플을 pair 간에 비교한다. 좌표계는 `_unit_records()`가 이미 쓰는 것과 같게 한다. slot
  불일치는 관측으로만 기록하고 판정은 `UNKNOWN_SLOT_CORRESPONDENCE`. 선택 slot이 scene에
  없으면 `INCONCLUSIVE`. type 비교는 scene gate 통과 후에만 유효하므로 순서를 바꾸지 않는다.
  근거: 원본 두 run에서 slot 1196~1199는 동일했지만 type은 [31,58] ↔ [21,70]로 달랐다.
  slot 안정성은 **원본 n=2**에서만 관측됐고 G2/G3 패치가 정확히 그 가정을 깬다.
- **F3**: `tools/compare_g1_stage_b.py:173`의 `result != "PASS" → FAIL`을 없앤다. timeout
  레코드는 `UNKNOWN_DISPUTED_ORACLE`로 분리하고 overall은 `INCONCLUSIVE`다. 관측은
  `after.last`에서 읽되 shape가 다르다 — `unit_select`/`drag_select`는 `last`가 selection dict
  자체, `minimap`은 `{"camera":…, "tick":…}`. `last`가 없거나 Mapping이 아니면 `INCONCLUSIVE`.
  **불변 조건(반드시 회귀 테스트로 고정): `UNKNOWN_DISPUTED_ORACLE`은 어떤 경로로도 stage PASS
  또는 overall PASS를 만들지 못한다.** 이 수리는 FAIL을 푸는 방향이라 이 가드가 없으면 위험하다.
  상류 분류기(`tools/runtime_env.py:2914-2917`) 수리는 R6-A로 분리하고 같은 바퀴에 넣지 않는다.
- **R6-B**: `tools/runtime_env.py:2487` 부근의 `int(item.get("count", 0)) >= 2`와 뒤따르는
  `drag_pass = drag_after.get("count", 0) >= 2` / `RuntimeSafetyError`를 "선택 상태가 응답했다"
  로 바꾼다 = `count` 또는 `(selected_slot, selected_type)` 중 하나가 before와 다르다.
  응답이 없으면 그대로 FAIL로 닫는다. `expected` 문자열도 실제 술어와 일치하게 고친다.
  근거: `analysis/memory_maps/`에 band-select 의미 기록이 0건이고, 관측은 `count 1→1`,
  `first_slot 1199(type70)→1198(type21)`이었다. 건물 제외 여부는 여전히 UNKNOWN이지만
  재결은 거기에 의존하지 않는다.

### work tier 순서 (한 바퀴 한 건, 각각 다음 middle이 독립 검수)

1. ~~**G1-F6-R1 가드**~~ — lap215 구현, **lap216 middle 독립 검수 PASS(범위 한정)**. 종료.
2. **F3 comparator 수리** — 위 불변 조건 회귀 포함. ← 다음 한 가지
3. **F2 identity 재정의**.
4. **R6-B 런타임 술어 재정의**.
5. **G1-F6-R2 flush 배선 가드**(lap216 신규, 비차단, 큐 끝).

네 건 모두 게임 실행이 필요 없고 보존 evidence/바이너리/baseline/golden을 건드리지 않는다.
F1/F4/F5의 fail-closed 동작은 그대로 유지해야 한다.

### S1 — 승격 대상 (work가 손대지 않는다)

원본 binary **두 run**을 서로 비교해도 `UNKNOWN_SCENE_MISMATCH` / exit 2다.

| 항목 | run A `20260912_010714_2914723_0` | run B `20260912_022912_3830565_0` |
|---|---|---|
| owner0 / owner1 nation | 2 / 2 | 3 / 1 |
| owner0 unit types | [31, 58] | [21, 70] |
| owner1 unit types | [31, 58] | [7, 49] |
| owner1 상대 world offset | (-71,71), (-73,69) | (-21,-50), (-23,-52) |
| `replay_seed_observed` | false | false |

nation과 owner1 스폰이 run마다 랜덤이고 승인된 read-only 오프셋으로는 seed를 노출/고정할 수
없다. 따라서 승인된 fresh pair 1회는 판정 계약을 전부 고쳐도 비교 가능한 장면을 얻는다는
보장이 없다. **comparator scene gate를 완화해 통과시키는 것은 금지된 baseline 수정이다.**
상위 tier가 (a) 장면 통제 수단, (b) pair 재시도 예산, (c) 장면 불일치 시 무엇을 증거로 삼을지를
재결하기 전까지 후보 Stage B run·원본 재실행·R6-A/R6-C는 계속 금지한다.

## lap215 — work tier G1-F6-R1 producer 회귀 가드 완료

`tests/test_runtime_env.py`에 실제 `g1_baseline`/`g1_presentation_trace` producer의 중첩
selector recorder를 AST로 검사하는 회귀를 추가했다. 각 recorder가 `_g1_record_selector_input()`을
호출하고 `_g1_selector_flow`에 연결되며, 과거 untagged `OBSERVED` stub이 없는 조건을 양쪽에
고정한다. 공용 helper만 검사하던 lap212 테스트의 공백을 닫은 것이다.

targeted 6 passed, `make check` 234 passed, Ruff/compileall/mypy/CONTEXT_PASS,
`SAFETY_PASS`; 게임 실행·PNG·EXE/DLL/assets/baseline/golden/evidence 변경은 0이다.
이 결과는 F6-R1 한정이며 다음 middle 독립 검수 전에는 후보 Stage B run을 열지 않는다.
S1 장면 통제 차단은 그대로 유지한다.

다음 work 한 가지는 F3 comparator 수리다. F2 identity와 R6-B 런타임 술어는 lap214 재결대로
후속 바퀴에서 각각 처리하며, S1 재결·후보/원본 재실행·R6-A/R6-C·WM_CLOSE 수리는 이 범위가 아니다.


## lap216 — middle tier G1-F6-R1 독립 검수 결과 (PASS, 범위 한정) + 신규 G1-F6-R2

lap215 가드를 테스트 본문과 독립적으로 재구현해(probe
`docs/history/laps/probes/20260912_lap216_f6_r1_guard_review_probe.py`) 실제 producer 소스와
변이 소스 14 case를 돌렸다. 결과는 `…_report.json`에 있고 `unexpected: []`다.

- 실제 `g1_baseline`/`g1_presentation_trace` 소스: 위반 0. 후보 recorder를 실제
  `_g1_selector_flow`로 구동하면 tagged 2건, untagged 0, comparator `input_errors` 0, flush 2회.
- 회귀 변이 6/6 차단: 과거 `OBSERVED` stub, helper를 쓰지 않는 직접 `inputs.append`,
  `_g1_selector_flow` 인자에서 recorder 제거. **lap215의 주장은 재현된다.**
- 가드 공백 6/6 미차단. 그중 `conditional_bypass`와 `tag_laundered`는 comparator의 F5 tag
  검사가 fail-closed로 잡으므로 잔여 위험이 낮다.

### G1-F6-R2 (신규, 비차단, work tier 큐 끝)

recorder가 `_g1_record_selector_input(..., flush=lambda: None)`으로 바뀌면 **가드도 comparator도
아무것도 보지 못한다**(untagged 0 / `input_errors` 0 / flush 0회). `_g1_flush_input_stage`는 각
stage를 teardown 전에 영속화하는 장치이고 `_g1_selector_flow`는 solo 실패 시 예외를 던지므로,
이 회귀는 **실패한 selector stage의 기록을 유실**시킨다. 유실 stage 자체는 comparator에서
`required input stage is missing` → `INCONCLUSIVE`로 닫히므로 PASS 세탁은 아니다.

수리 범위(work tier): 두 producer의 recorder가 helper에 넘기는 `flush` 인자가 해당 producer의
`flush_input_stage`(즉 `_g1_flush_input_stage` 배선)임을 producer 수준에서 고정하는 회귀 1건.
판정 의미·좌표·예산·comparator는 건드리지 않는다. 게임 실행이 필요 없다.
F3 → F2 → R6-B 뒤에 처리하며, 순서를 앞당기려면 그 이유를 기록한다.

## lap217 — work tier F3 comparator 수리, middle 독립 검수 대기

`tools/compare_g1_stage_b.py`에서 PASS가 아닌 stage result를 카드 `FAIL`로 상속하지 않고
`UNKNOWN_DISPUTED_ORACLE`로 닫도록 변경했다. `unit_select`/`drag_select`의 timeout shape인
`after.last`를 selection 관측으로, `minimap`의 `after.last.camera`를 camera 관측으로 읽으며,
관측 누락·손상은 `INCONCLUSIVE`다. disputed stage가 실제 checks를 만족해도 overall은
`INCONCLUSIVE`이며, 기존 F1/F4/F5 fail-closed 동작은 유지했다. 상류 runtime 분류기와 R6-A,
F2 identity, R6-B, scene gate는 변경하지 않았다.

회귀는 timeout 양성 fixture 3종을 포함한다: 양쪽 동일 `FAIL_NO_EFFECT` + selection `last`는
stage `UNKNOWN_DISPUTED_ORACLE`/overall `INCONCLUSIVE`, `after.last` 누락은 `INCONCLUSIVE`,
minimap camera `last`도 읽지만 PASS로 승격하지 않는다. 저장소 targeted 12 passed, `make check`
236 passed + Ruff/compileall/mypy/CONTEXT_PASS, `SAFETY_PASS`다. 보존 원본↔후보 pair는 여전히
`INCONCLUSIVE`이며 후보의 historical untagged tag 오류가 그대로 남는다.

다음 middle은 새 게임 실행 없이 F3 변경을 독립 probe로 검수한다. S1 장면 통제 재결 전에는
후보 Stage B run·원본 재실행·R6-A/R6-C를 열지 않는다. 다음 work 한 가지는 F2 identity 재정의다.

## lap218 — middle tier F3 comparator 독립 검수 결과 (PASS, 범위 한정) + 신규 F3-R1/F3-R2

lap217의 F3 수리를 저장소 테스트 helper를 쓰지 않는 새 probe
(`docs/history/laps/probes/20260912_lap218_f3_comparator_review_probe.py`, 18 case)로 재검증했다.
결과는 `…_report.json`이고 `unexpected: []`, `disputed_pass_violations: []`다. 보고 해시·수치도
모두 재현됐다(targeted 12, Fast 236, `SAFETY_PASS`, 보존 pair `INCONCLUSIVE`/exit 2,
runtime producer 소스 해시 lap216과 동일). **F3 자체는 승인한다.**

재현된 lap217 주장: disputed stage는 `after.last`를 관측으로 읽고 `UNKNOWN_DISPUTED_ORACLE`로
닫히며 overall은 `INCONCLUSIVE`다. 관측이 서로 달라도 카드 FAIL로 상속하지 않고, 관측이 없거나
손상되면 `INCONCLUSIVE`다. scene gate·F1·F4·F5 fail-closed와 정상 pair PASS는 유지된다.
논리 geometry 불일치만이 disputed stage에서도 카드 FAIL로 남는다(입력 자체의 결함이므로 타당).

### G1-F3-R1 (신규, 비차단, 잠재 PASS 세탁) — work tier

`_selection`/`_camera`의 `after.last` 폴백이 source result와 무관하게 항상 적용된다.
probe B1(result `PASS` + timeout shape `after`)과 B2(result `PASS` + 손상된 비Mapping
`after.selection` + 정상 `after.last`)가 둘 다 overall `PASS`가 됐다. 현재 producer는
`after.last`를 `tools/runtime_env.py:2371`의 timeout 경로에서만 쓰고 그때 result는 항상 timeout
분류라 도달 불가지만, comparator는 producer 결합에 기대면 안 된다.

수리 범위: (a) `after.last` 폴백을 source result가 disputed 분류일 때만 켠다,
(b) `after.selection`/`after.camera` 키가 존재하되 형식이 깨졌으면 `last`로 대체하지 말고
`INCONCLUSIVE`로 닫는다. 회귀는 B1·B2 형태를 각각 고정한다. 판정 의미·좌표·scene gate·예산은
건드리지 않으며 게임 실행이 필요 없다.

### G1-F3-R2 (신규, 비차단, 판정력 침식) — middle 재결 완료, work tier 구현

`disputed = any(result != "PASS")`가 timeout이 아닌 하드 `FAIL`까지 흡수한다. minimap은
`tools/runtime_env.py:2556`에서 `"PASS" if minimap_pass else "FAIL"`을 flush하므로 도달 가능한
경로이고, probe B3에서 camera가 움직이지 않은 후보가 카드 FAIL이 아니라 `INCONCLUSIVE`가 됐다.
lap214가 재결한 대상은 `FAIL_NO_EFFECT`이지 모든 비PASS 결과가 아니었다.

**middle 재결(lap218):** disputed 집합을 명시 열거로 좁힌다 —
`FAIL_NO_EFFECT`, `UNKNOWN_BUDGET_EXHAUSTED`, `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`.
`PASS`는 기존대로 checks 판정, 하드 `FAIL`은 카드 `FAIL` 유지, **그 밖의 알 수 없는 result 문자열과
`result` 키 누락은 `INCONCLUSIVE`**로 닫는다(기본값이 PASS가 되지 않게 한다). 이 재결은 어떤
경우에도 새 PASS 경로를 만들지 않는다. 회귀는 세 분류 각각과 하드 FAIL, 미지 문자열을 고정한다.

### 순서

다음 work 한 가지는 예정대로 **F2 identity 재정의**다. 이후 R6-B → **G1-F3-R1** → **G1-F3-R2**
→ G1-F6-R2. F3-R1을 F6-R2 앞으로 올린 이유는 F3-R1만 잠재 PASS 경로이고 F6-R2의 유실 stage는
`INCONCLUSIVE`로 닫히기 때문이다. S1 장면 통제 재결 전에는 후보 Stage B run·원본 재실행·
R6-A/R6-C를 열지 않는다. 이 승인은 제품 G1 PASS/출시 승인이 아니다.

## lap220 — work tier F2 type-gate repair, middle independent review pending

lap219의 F2 구현은 `tools/compare_g1_stage_b.py:270`에서 `Any | None`을 `int`로 대입하는
mypy 오류로 필수 gate가 실패했다. 이번 work는 F2 의미 변경 없이 `slots[name] = cast(int, slot)`
으로 `_is_int` 검사 이후의 타입 경계를 명시했다. 비교기 판정, slot 대응 규칙, scene gate,
F3/R6-B는 변경하지 않았다.

검증:

- `.venv/bin/python -m pytest -q tests/test_compare_g1_stage_b.py` → 14 passed.
- 독립 synthetic probe `docs/history/laps/probes/20260912_lap220_f2_identity_probe.py` → 4/4
  expected statuses, report `..._f2_identity_probe_report.json`, status PASS.
- `make check` → pytest 238 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`.
- `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
- 보존 pair comparator → `INCONCLUSIVE`, `production=NOT_COMPARED`, exit 2; 후보 historical
  untagged input errors 2건은 그대로 보존됐다.

판정: **F2 work gate PASS, 제품/Stage B PASS 아님.** 다음 middle은 이 변경을 독립 검수해야
하며, S1 장면 통제 재결 전 후보 Stage B 실행·원본 재실행·R6-A/R6-C 및 R6-B 구현은 금지한다.
다음 work 카드는 F2 middle 검수 후에만 R6-B로 이동한다.

## lap221 — middle 독립 검수 결과: F2 **승인(범위 한정)**, 신규 비차단 2건

작성: Claude Code `claude-opus-5`/high, middle tier(진단·계획·컨펌). 구현하지 않았고 게임을
실행하지 않았다. 근거: `docs/history/laps/20260912_lap221_middle_f2_identity_review.md`,
probe `docs/history/laps/probes/20260912_lap221_f2_identity_review_{probe.py,report.json}`.

### 승인

lap219+lap220의 F2 identity 재정의를 **승인(PASS)** 한다. 범위는 `tools/compare_g1_stage_b.py`의
comparator semantics와 lap220 gate 수치 재현뿐이다. 제품 G1 PASS·마일스톤 승인·Stage B run
인가가 아니다. 근거:

- 저장소 fixture/테스트 helper를 쓰지 않는 독립 12 case가 전부 사전 예측과 일치했다.
- 일괄 slot 재번호는 stage `UNKNOWN_SLOT_CORRESPONDENCE` / overall `INCONCLUSIVE`이고 **FAIL이
  아니다.** 절대 slot 동일성은 FAIL 술어에서 빠졌다(lap214 재결 충족).
- slot·type이 같은데 같은 type 2기의 world 위치만 교환된 pair는 `FAIL`이다. 수리 전 절대-slot
  술어라면 `PASS`였다. 즉 이 수리는 FAIL 판정력을 **넓혔다**.
- 400 sample 무작위 sweep에서 overall `PASS` 74건 전부가 scene PASS·input_errors 0·slot 동일·
  정규화 identity 동일·count delta 동일·양측 `result == PASS`를 만족했다. 새 PASS 경로 0건.
- `cast(int, slot)`은 바로 위 `_is_int` 가드 뒤이고 `cast`는 런타임 무연산이라 의미 중립이다.
- 재현: targeted 14 passed, `make check` 238 passed/Ruff/compileall/mypy 10 files/`CONTEXT_PASS`,
  `SAFETY_PASS`, 보존 pair `INCONCLUSIVE`/`NOT_COMPARED`/exit 2, 소스 3종 SHA 무변경.

### G1-F2-R1 (비차단, work tier 수리 범위)

`tools/compare_g1_stage_b.py:271~281` — `baseline_evidence`/`candidate_evidence`가 `None`이면
identity가 절대 `[slot, unit_type]`로 되돌아간다. probe K에서 이 분기가 절대 slot/type만으로
stage `PASS`를 냈다. 오늘은 `compare_evidence`(`:357`)가 유일한 호출자이고 항상 evidence를
넘기므로 도달 불가지만, 코드 주석이 근거로 든 "timeout-oracle probe 직접 호출자"는 저장소
전체 grep에서 존재하지 않는다(probe 5종·tests 전부 `compare_evidence`만 호출).

수리 범위: evidence 두 인자를 **필수**로 만들거나, 없을 때 `INCONCLUSIVE`로 닫는다. 절대
slot/type 폴백은 제거한다. 회귀는 (a) evidence 없는 호출이 PASS를 만들지 못함, (b) 기존
`compare_evidence` 경로 판정 불변을 고정한다. **새 PASS 경로를 만들지 않는다.**
이것은 G1-F3-R1과 같은 부류(comparator가 호출자 결합에 판정을 기대는 문제)다.

### G1-F2-R2 (비차단, **work tier 범위 아님** — 상위 tier 재결 사항)

`UNKNOWN_SLOT_CORRESPONDENCE`는 stage를 PASS에서 끌어내리고 overall을 `INCONCLUSIVE`로 만든다
(`:335~341`, `:369~372`). 결과적으로 **카드 overall PASS는 원본 run과 후보 run이 동일한 엔진
slot id를 낼 때만 가능하다.** lap214는 run마다 nation/스폰이 랜덤이고 `replay_seed_observed=false`
임을 재현했다. 따라서 S1 "장면 통제"를 **장면 일치만으로** 푸는 해법은 카드 PASS에 충분하지 않다.

선택지는 두 가지뿐이며 둘 다 상위 tier(Astra/사용자) 소관이다: (a) S1 해법이 slot id 결정성까지
제공한다, (b) slot 강등 규칙 자체를 재결한다. **middle은 완화하지 않는다** — lap214 재결의
"PASS 경로를 절대 만들지 않는다"가 우선한다. work tier는 이 항목을 건드리지 마라.

### 순서

다음 work 한 가지는 **R6-B 런타임 술어 재정의**(게임 실행 없음)다. 이후 **G1-F2-R1** →
G1-F3-R1 → G1-F3-R2 → G1-F6-R2이며 각 건은 다음 middle이 독립 검수한다. S1과 G1-F2-R2 재결
전에는 후보 Stage B run·원본 재실행·R6-A/R6-C를 열지 않는다.

## lap222 — work tier R6-B 구현, 필수 gate 이력으로 승격

R6-B 재결에 따라 `tools/runtime_env.py`의 `drag_select` wait predicate와 최종 `drag_pass`를
공용 `_g1_selection_responded` 술어로 교체했다. 이 술어는 count 또는
`(selected_slot, selected_type)`가 before와 달라질 때만 응답으로 인정하며, 둘 다 같으면
무반응으로 남긴다. expected/timeout/error 문자열도 이 술어와 일치시켰다. `count>=2` 절대
게이트와 관련 문구는 실행 코드에서 제거했다.

회귀 fixture는 `count=1`을 유지하면서 선택 identity를 `1199/70→1198/21`로 바꾸는 응답을
검증하고, 별도 단위 검사는 count 변화·identity 변화·무변화를 각각 고정한다. 첫 `make check`는
최종 `drag_pass`의 잔여 `count>=2` 때문에 **238 passed / 1 failed**였고, 해당 한 곳을 같은
공용 술어로 수리했다. 수리 후 targeted 6 passed, `make check` 239 passed/Ruff/compileall/
mypy 10 files/`CONTEXT_PASS`, safety `SAFETY_PASS`다. 게임 실행·Stage B·PNG·바이너리 변경은
없다. 필수 gate 실패 이력 때문에 제품/카드 PASS로 닫지 않고 `loop/ESCALATE_SOL`에 승격한다.

다음 middle은 R6-B의 독립 probe에서 (a) count 1→1 identity 변화 PASS, (b) count/identity
무변화 FAIL/timeout, (c) 기존 count 변화 PASS, (d) 실행 코드에 `count>=2` 잔존 없음과 최종
gate 수치를 재현해야 한다. S1 장면 통제·G1-F2-R2·후보/원본 새 실행 금지는 유지한다.

## lap224 — middle 독립 검수: R6-B 조건부 반려, G1-R6-B-R1 수리 지시

전체 기록: `docs/history/laps/20260912_lap224_middle_r6b_review.md`.
probe: `docs/history/laps/probes/20260912_lap224_r6b_selection_response_review_probe.py`
(sha256 `713e15faab03c2aa3ff5add1ddd85868c380d7012691779ce44aa116a33e6705`).

재현 승인: 실행 경로에 `count>=2` 없음, count 변화·lap204형 identity 변화 PASS, 무변화 FAIL,
targeted 6 / `make check` 239 / mypy 10 / `CONTEXT_PASS` / `SAFETY_PASS`, 소스 해시 일치.

반려 사유: `_read_g1_selection_evidence`(`tools/runtime_env.py:1344`)가 읽기 실패와
`_CommandCellSnapshotError`를 `selected_type="UNKNOWN"`으로 삼키는데,
`_g1_selection_responded`(`:2039`)가 그 `UNKNOWN`을 변화로 인정한다. probe C4(일시 읽기 실패),
C5(선택 slot 비활성 = 풀 손상), C6(count 1→0 선택 상실), C7(손상 기준선의 회복) 4건이 모두
`responded=True`로 관측됐다. 같은 술어가 `stage_wait` 조건(`:2496~2500`)이므로 첫 손상 관측에서
대기가 잘리고 stage가 `UNKNOWN` evidence로 `PASS` 기록된다. 하류 comparator(`:266~268`)가
`INCONCLUSIVE`로 막아주지만 in-run fail-closed 자체가 깨진 것은 lap207 F1과 같은 부류다.

### G1-R6-B-R1 (차단, work tier 한 건)

`_g1_selection_responded`를 **양쪽 관측이 온전할 때만** 변화를 인정하도록 fail-close 한다.
온전성은 comparator와 같은 정의: `count`가 int이고, `count>0`이면 `selected_slot`이 int이며
`selected_type != "UNKNOWN"`. 한쪽이라도 손상이면 응답 아님 → `stage_wait`는 계속 폴링하고,
timeout 분류는 "무반응"이 아니라 관측 손상으로 provenance(`selected_type_provenance`)와 함께
기록한다. 회귀는 (a) C4·C5·C7 `responded=False`, (b) C1~C3 판정 불변, (c) 손상 timeout의
provenance 보존을 고정한다. **새 PASS 경로 금지**, baseline/golden/EXE/DLL/assets 변경 금지,
게임 실행 금지.

### G1-R6-B-R2 (비차단, **work tier 범위 아님** — 상위 tier 재결)

count 1→0(선택 상실)을 응답으로 셀 것인가. STATUS 사전 기준(비퇴행만 인정)과 lap223 구현
계약(모든 변화 인정)이 충돌한다. middle 권고는 이 고정 drag에서 빈 선택을 응답으로 세지 않는
것이지만, 판정 의미 변경이라 Astra/사용자 재결 전까지 건드리지 않는다. G1-F2-R2와 같은 취급이다.

### 순서

R6-B-R1 → (middle 검수) → G1-F2-R1 → G1-F3-R1 → G1-F3-R2 → G1-F6-R2. 한 바퀴 한 건.
S1과 G1-F2-R2/R6-B-R2 재결 전에는 후보 Stage B run·원본 재실행·R6-A/R6-C를 열지 않는다.

## lap226 middle 독립 검수 — R6-B-R1 범위 승인, 후속 3건

전체 기록: `docs/history/laps/20260912_lap226_middle_r6b_r1_review.md`.
probe: `docs/history/laps/probes/20260912_lap226_r6b_r1_review_probe.py`
(sha256 `11b7c62c140e01d513b1c6989368daede1426d17bfd6b9a6c8378bce892dc5f0`),
보고서 `..._review_report.json`
(sha256 `1d8faf16d29f35318bf58c195d1469db515a442a02aa10c8f7b4273839b02444`).

승인: lap224가 준 명세를 정확히 이행했다. 리더 기반 probe에서 C4(일시 읽기 실패)·
C5(slot 비활성)·C7(손상 기준선 회복)이 모두 `responded=False`+diagnostics `CORRUPTED`,
C1~C3 판정 불변, C6(count 1→0)은 의도대로 불변이다. 가짜 시계로 실제 `_wait_state`를 구동한
W1/W2에서 손상 poll이 대기 창을 자르지 않고(W1 poll 4회 소진 후
`UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`), 손상 뒤 늦게 온 실제 응답도 관측됐다(W2).
새 PASS 경로는 없다. 소스 해시 lap225 기록과 일치, targeted 16 / `make check` 243 /
mypy 10 / `CONTEXT_PASS` / `SAFETY_PASS` 재현.

### G1-R6-B-R3 (차단, work tier 한 건 — R6-B 종결 전 필수)

`observation_is_sound`(`tools/runtime_env.py:2045~2054`)가 `count <= 0`을 무조건 sound로 본다.
`_read_selection`(`:1338`)은 `count`를 **부호 있는** `<i`로 읽으므로 손상 시 `count=-1` 같은
불가능한 값이 나올 수 있고, 그때 identity가 `None/UNKNOWN`으로 접혀 **변화 = 응답**이 된다
(probe D1=after 손상, D2=before 손상, 둘 다 `responded=True`). 수리 범위는 `count < 0`을
손상으로 거부하는 것 하나뿐이다. **`count == 0`의 의미는 건드리지 않는다**(R6-B-R2 재결 대상).
회귀: D1/D2 `responded=False` + diagnostics `CORRUPTED`, C1~C7 판정 불변. 새 PASS 경로 금지,
baseline/golden/EXE/DLL/assets 변경 금지, 게임 실행 금지.

### G1-R6-B-R4 (비차단)

`diagnostics["selection_observation"]`은 손상 poll에서만 기록되고 온전한 poll에서 지워지지
않는다(`:2058~2066`). poll1만 일시 손상이고 이후가 전부 온전·무변화이면 실제 `FAIL_NO_EFFECT`가
`UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`로 흡수된다(probe W3). 성공 반환에도 낡은 `CORRUPTED`
딱지가 남는다(W2). 최종 관측 기준으로 `status`를 갱신하되 `corrupted_poll_count`와 첫/마지막
손상 provenance는 보존한다. F3의 `after.last` 선례와 정합한다. 회귀: W1 분류 유지, W3는
`FAIL_NO_EFFECT`, W2는 상태 `SOUND`+손상 이력 보존.

### G1-R6-B-R5 (비차단)

`tests/test_runtime_env.py:1386`의 손상 케이스는 여전히 손으로 쓴 dict다. C4·C5·C7·D1을
`_read_g1_selection_evidence`로 만든 관측으로 고정하는 회귀를 추가한다(기존 dict 케이스 유지).

## lap227 work — R6-B-R3 구현

`tools/runtime_env.py:_g1_selection_responded`의 `observation_is_sound`가 부호 있는 selection
count의 음수 값을 온전한 빈 선택처럼 처리하지 않도록 `count < 0`을 손상으로 거부했다.
`count == 0` 분기는 기존대로 유지해 R6-B-R2(count 1→0 의미)를 변경하지 않았다.

회귀는 D1(온전→음수 손상), D2(음수 손상→온전)에서 모두 `responded=False`와
`diagnostics.selection_observation.status == "CORRUPTED"`를 확인하고, 기존 C1~C7 판정 및
count 1→0 semantics를 유지한다. targeted 18, `make check` 245, Ruff/compileall/mypy 10 files,
`CONTEXT_PASS`, `SAFETY_PASS`; 게임 실행·PNG·EXE/DLL/assets/baseline/golden 변경은 0이다.

다음 새 middle 세션은 R6-B-R3을 독립 검수한다. R6-B-R2와 S1/F2-R2 재결 전 Stage B 원본/후보
실행, 원본 재실행, R6-A/R6-C는 계속 금지한다.

## lap228 middle — R6-B-R3 독립 검수 = 범위 승인

게임 없이 새 probe `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`로 검수했다.
결론 4가지:

1. **도달성 확인.** `_read_selection`은 `<i`(부호 있는) dword를 읽고(`tools/runtime_env.py:1340`),
   음수면 identity 리더가 던지는 `_CommandCellSnapshotError`를 `_read_g1_selection_evidence`의
   `except`가 삼켜(`:1361~1366`) `count=<음수>, selected_slot=None, selected_type="UNKNOWN"`을
   예외 없이 반환한다. 수리 전 이 관측은 `count <= 0`으로 "빈 선택" 취급됐다. 사문이 아니다.
2. **커버리지.** `0xFFFFFFFF`, `0x80000000`, torn dword, -2, 문자 바이트를 before/after 양쪽에
   넣은 7케이스 전부 `responded=False` + `status=CORRUPTED`, `before_sound`/`after_sound`가
   손상된 쪽만 False. 음수 + 그럴듯한 slot/type을 손으로 붙인 경우도 거부된다.
3. **수술성.** lap225 규칙을 독립 재구현해 13,689 케이스를 차분했다. 동작 변화 2,052건은 전부
   "음수 포함 + 이전 True → 현재 False"이고 그 외 변화는 0건이다. 비정수 count 거부도 불변.
4. **보존.** count 1→0(R6-B-R2), count 0 + 낡은 slot, 0→0, 0→1, identity-only, 무변화 6/6 불변.

대기 창은 W1(전부 음수) → `UNKNOWN_SELECTION_OBSERVATION_CORRUPTED` 타임아웃, W2(음수 후 실제
응답) → `RESPONDED`로 정상이다. **W3(음수 1회 후 온전·무변화)만 `FAIL_NO_EFFECT`가 아니라
UNKNOWN으로 흡수**되는데, 이는 기등록 R6-B-R4 그대로이며 새 결함이 아니다. 다만 R3이 손상 판정
집합을 넓혀 R4 발동 경로가 하나 늘었다(일시적 음수 1회로도 세탁). fail-safe 방향이라 R3 승인을
막지 않지만 R4 우선순위 근거다.

검증: targeted 18, `make check` 245 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`,
`SAFETY_PASS`, 원본 EXE SHA 일치, 게임 0회, PNG 0장, 제품 코드 변경 0.

### 다음 work tier에게 (R6-B-R4)

최종 관측 기준으로 `selection_observation.status`를 갱신하되 `corrupted_poll_count`와 첫/마지막
손상 provenance는 보존한다. 회귀 대조 장면은 lap228 probe의 W1~W3를 그대로 쓴다:
W1 분류 유지, **W3 → `FAIL_NO_EFFECT`**, W2 성공 반환 시 `status=SOUND` + 손상 이력 보존.

### 순서 (갱신)

R6-B-R3 → (middle 검수) → R6-B-R4 → R6-B-R5 → G1-F2-R1 → G1-F3-R1 → G1-F3-R2 → G1-F6-R2.
한 바퀴 한 건. S1과 G1-F2-R2/R6-B-R2 재결 전에는 후보 Stage B run·원본 재실행·R6-A/R6-C를
열지 않는다.

## lap229 — work tier R6-B-R4 구현

`tools/runtime_env.py:_g1_selection_responded`가 매 poll의 최종 관측 상태를
`selection_observation.status`에 반영하도록 수리했다. 손상 poll에서는
`corrupted_poll_count`를 증가시키고 첫/마지막 손상 provenance를 보존하며, 이후 온전한 poll에서는
현재 `before`/`after`를 `SOUND`로 기록한다. 따라서 일시 손상 뒤 온전한 무반응은
`FAIL_NO_EFFECT`로, 손상 뒤 실제 선택 응답은 `RESPONDED`로 분류되며 손상 이력은 남는다.

회귀로 W1/W2/W3 대조를 추가했다. W1의 영구 음수 관측은
`UNKNOWN_SELECTION_OBSERVATION_CORRUPTED` timeout, W3는 `FAIL_NO_EFFECT` timeout, W2는
성공 반환 및 `SOUND` 상태·손상 provenance 보존이다. 기존 count 1→0 semantics 및 음수
fail-close는 유지한다.

검증: targeted selection/wait 10 passed, `make check` 247 passed, `.venv/bin/python -m pytest -q`
247 passed, Ruff/compileall/mypy 10 files/`CONTEXT_PASS`, `LOOP_DRY_RUN=0 bash checks/safety.sh check`
`SAFETY_PASS`. lap228 probe는 W1~W3 wait defects 0을 확인했다. 게임 실행·PNG·원본/후보
EXE/DLL/assets/baseline/golden 변경은 0이다. source SHA: `tools/runtime_env.py`
`f39d26fc578c7a33379eb2556f588d4b56a5a24a9ae618ac590947cbfbc4c76e`,
`tests/test_runtime_env.py` `d030b04d70d72bd86d15fee6abf6fa6ead15f56691d23f08f2950b3a748de397`.

다음 새 middle tier는 R6-B-R4를 독립 검수한다. 승인 뒤 R6-B-R5를 진행한다. R6-B-R2
(count 1→0 의미)와 S1/F2-R2 결정성 재결 전 Stage B 및 원본 재실행은 금지한다.

## lap230 — middle tier R6-B-R4 독립 검수 = 범위 승인 + 후속 2건

Claude Opus5/high(middle)가 게임 없이 lap229 결과를 독립 검수했다. 자체 probe
`docs/history/laps/probes/20260912_lap230_r6b_r4_review_probe.py` 25케이스에서
**23 AGREES / 2 DEFECT**. R4 계약 케이스는 전부 AGREES다: 최종성이 양방향(C1a/C1c),
손상 계수와 first/last provenance 정확(C1d~C1f), `selection_observation` 키 8개로 유계(C1g),
count 1→0·음수·`bool`/`float` 거부·identity 응답 semantics 불변(C2a~C2e),
W1/W2/W3와 최종 poll 손상(C3a~C3h), `before` 오염 fail-closed(C4a),
오염된 이전 누적값 리셋(C6a/C6b). lap228 probe 재실행도 defect 0으로 독립 일치했다.

DEFECT 2건은 **R4 회귀가 아니라 선재 결함**이라 반려 사유로 쓰지 않고 후속으로 등록했다.

### R6-B-R6 (다음 work 한 건, R6-B 전체 승인 차단)

`_wait_state`는 `read_state` 예외를 `except (OSError, ValueError, struct.error): pass`로
삼킨다(`tools/runtime_env.py:2990`). 술어가 호출되지 않아 `selection_observation`이 갱신되지 않는데
분류 폴백은 `FAIL_NO_EFFECT`다. 실행 확인:

- C5a 모든 poll이 `OSError` → `selection_observation` **부재**인데 `FAIL_NO_EFFECT`.
- C5b 온전 poll 2회 뒤 tail 전부 `OSError` → stale `SOUND`가 최종 상태로 남아 `FAIL_NO_EFFECT`.
  `poll_count=4`인데 실제 관측은 2회라 증거가 관측 범위를 과대표시한다.

도달성: `read_selection` = `_read_g1_selection_evidence(read_for_process)`이고 내부
`_read_selection`은 예외를 잡지 않으므로 후보 프로세스 종료/언맵이 정확히 이 경로다.
관측 없이 하드 FAIL을 상속하는 형태라 lap214 Opus 재결이 기각한 계열과 같다.

기대 수리 방향(구현은 work tier 판단): 읽기 실패를 `wait_observation`에 별도 계수/provenance로
남기고, 관측이 0건이거나 마지막 성공 관측이 창 끝까지 이어지지 않으면 `FAIL_NO_EFFECT` 대신
`UNKNOWN_*`로 fail-close한다. **기존 PASS 조건과 R6-B-R2/R3/R4 semantics는 건드리지 않는다.**

### R6-B-R7 (경미)

검수 probe가 출력 경로를 하드코딩해 재실행이 과거 lap 보고서 JSON을 덮어쓴다. lap230에서
lap228 원본이 덮어써졌고, 고지(`..._report.PROVENANCE.md`)와 재실행본
(`20260912_lap230_lap228probe_rerun_report.json`)을 보존했다. 원본은 재구성하지 않았다.

### 범위 밖 관찰

`unit_select` 술어는 `int(item.get("count", 0)) >= 1`뿐이라 slot/type 온전성을 보지 않고
비정수 count의 `TypeError`는 위 `except`에 잡히지 않는다(`tools/runtime_env.py:2481`).
R6-A 계열이므로 상위 재결 전 진행하지 않는다.

### 순서 (갱신)

R6-B-R6 → R6-B-R5 → R6-B-R7 → G1-F2-R1 → G1-F3-R1 → G1-F3-R2 → G1-F6-R2. 한 바퀴 한 건.
S1과 G1-F2-R2/R6-B-R2 재결 전에는 후보 Stage B run·원본 재실행·R6-A/R6-C를 열지 않는다.

검증: targeted 20 passed, `make check` 247 passed, Ruff/compileall/mypy 10/`CONTEXT_PASS`,
`SAFETY_PASS`, 원본 EXE SHA 일치, 게임 0회, PNG 0장, 제품/도구 코드 변경 0.

## lap231 — work tier R6-B-R6 구현

`_wait_state`의 읽기 예외 poll을 더 이상 관측 없이 버리지 않는다. 전체 시도 횟수는
`poll_attempt_count`, 실제 읽기 성공 관측은 기존 `poll_count`로 분리하고, 읽기 오류는
`read_error_count`와 첫/마지막 `read_error_provenance`로 보존한다. 관측이 없거나 마지막 성공
관측 이후 읽기 실패가 대기 창 끝에 남으면 `UNKNOWN_STATE_READ_FAILURE`로 fail-close한다.
선택 진단이 이미 있으면 stale `SOUND`를 `UNAVAILABLE`로 바꿔 최종 읽기 상태를 정직하게 남긴다.
예산 소진·관측 창 잘림·선택 관측 손상 우선순위, R6-B-R2/R3/R4 semantics와 PASS 조건은
변경하지 않았다.

회귀는 모든 poll `OSError`(성공 관측 0 / 시도 4)와 sound 2회 뒤 unreadable tail
(성공 관측 2 / 시도 4)을 고정했다. 후자는 `read_error_count=2`, 최종 selection status
`UNAVAILABLE`, `UNKNOWN_STATE_READ_FAILURE`이며 `FAIL_NO_EFFECT`가 아니다.

검증: `tests/test_runtime_env.py -k 'selection or wait_state'` 34 passed; `.venv/bin/python -m pytest -q`
249 passed; `make check` 249 passed, Ruff/compileall/mypy 10 files/`CONTEXT_PASS`,
`LOOP_DRY_RUN=0 bash checks/safety.sh check` `SAFETY_PASS`; lap230 probe 25 AGREES/0 DEFECT.
게임 실행 0회, PNG 0장, EXE/DLL/assets/baseline/golden 변경 0. source SHA:
`tools/runtime_env.py` `103ec280b50ac658504b5263a200896c1b39d66244269bc373dcfd23225ce02b`,
`tests/test_runtime_env.py` `29ccf832bef53b1fc470efc54971df1e44935efbe137b1120bdfaba79b709684`.

다음 새 middle tier(Claude Code `claude-opus-5`/high)가 R6-B-R6를 독립 검수한다. 승인 전에는
R6-B-R5/R7, Stage B 원본·후보 실행, S1/F2-R2 및 R6-B-R2 재결을 진행하지 않는다.

## lap232 — middle tier R6-B-R6 독립 검수 (범위 승인)

게임 없이 lap231 수리를 독립 검수했다. 자체 probe
`docs/history/laps/probes/20260912_lap232_r6b_r6_review_probe.py` 18케이스 **18 AGREES / 0 DEFECT**.
probe는 출력 경로를 하드코딩하지 않고 기존 보고서가 있으면 `--force` 없이 덮어쓰기를 거부한다
(R6-B-R7 재발 방지). 확인한 것:

- C5a(모든 poll 읽기 실패)는 `poll_count=0 / attempts=4 / read_error_count=4`,
  `selection_observation` 부재, `UNKNOWN_STATE_READ_FAILURE`. C5b(sound 2회 뒤 unreadable tail)는
  최종 `status=UNAVAILABLE`이며 호출자 쪽 `wait_observation`에도 같은 값이 보인다
  (`_G1WaitTimeout`은 관측을 얕은 복사하므로 객체 동일성은 다르지만 내용은 같다).
- `OSError`/`ValueError`/`struct.error` 세 경로 모두 같은 분류로 닫힌다.
- 분류 우선순위는 예산 > 창 잘림 > 읽기 실패 > 선택 손상 > `FAIL_NO_EFFECT`이고, 상위 3개는 모두
  UNKNOWN이라 완화가 아니다. 손상 뒤 읽기 실패 tail에서도 `corrupted_poll_count`와 첫/마지막
  손상 provenance는 보존된다.
- poll 시도가 0회인 경우(창이 완전히 잘림)도 hard `FAIL_NO_EFFECT`가 아니다.
- `stage=None` 비-G1 호출자는 여전히 `RuntimeSafetyError`이고, PASS 경로는 읽기 오류가 있어도
  그대로 반환하며 status는 `SOUND`로 남는다.
- R6-B-R2(count 1→0 = 응답, 미결 분쟁) / R3(음수 손상) / R4(비정수 손상·최종성) 값 불변.
- 비교기 `_stage_report`는 읽기 실패 stage를 stale `last`가 변화처럼 보이는 경우에도
  `UNKNOWN_DISPUTED_ORACLE`로 닫아 PASS가 되지 않는다.

검증: lap230 probe 재실행 25 AGREES/0 DEFECT, 전체 `pytest -q` 249 passed, `make check` 249 passed +
Ruff/compileall/mypy 10 files/`CONTEXT_PASS`, `LOOP_DRY_RUN=0 bash checks/safety.sh check`
`SAFETY_PASS`. 원본 EXE SHA 핀 4개 파일 불변, 게임 0회, PNG 0장, 제품 코드 변경 0.

### lap232 신규 후속 — R6-B-R8 (비차단)

읽기 오류가 관측 창의 대부분이어도 마지막 poll만 성공하면 분류는 여전히 hard `FAIL_NO_EFFECT`다
(probe `readable_tail_keeps_hard_fail`). 최종 관측이 온전하므로 R4 불변식 자체는 지켜지지만,
관측 커버리지 비율에 대한 임계(`G1_INPUT_MAX_TRUNCATION_RATIO`에 해당하는 것)가 없어 사실상 1회
관측만으로 "입력이 무반응이었다"는 hard FAIL을 주장할 수 있다. lap214 재결 취지상 Stage B 실행
전에 임계 도입 여부를 결정해야 한다. 수리 주체는 work tier다.

기록 결함(코드 영향 없음): lap231 `loop/ESCALATE_SOL`의 `tests/test_runtime_env.py` sha256이
62자로 두 글자(`ef`)가 누락됐다. 본 문서 lap231 절의 digest와 실제 파일은 일치한다.

## lap233 — work tier R6-B-R5 회귀 보강

기존 손상 응답 테스트가 손으로 만든 dict만 사용하던 결손을 보강했다. 저장소 테스트가 실제
`_read_g1_selection_evidence` reader로 C4(OSError 읽기 실패), C5(비활성 selected slot),
C7(손상 기준선의 정상 관측 회복), D1(음수 selection count)을 생성한다. 네 관측 모두
`_g1_selection_responded=False`와 `selection_observation.status=CORRUPTED`를 확인하며,
UNKNOWN 및 provenance/음수 count 보존도 단언한다. 기존 dict 기반 회귀는 유지했다.

변경은 `tests/test_runtime_env.py` 한 파일이며 `tools/runtime_env.py`, EXE/DLL/assets,
baseline/golden은 변경하지 않았다. 게임 실행·PNG·커밋은 0이다. 검증은 targeted selection
18 passed, `make check` 253 passed, Ruff/compileall/mypy 10 files/`CONTEXT_PASS`,
`LOOP_DRY_RUN=0 bash checks/safety.sh check` `SAFETY_PASS`이다. 테스트 SHA는
`c8830c1277c8ab57ecfbddeecda3be22b63b21b6898fd8b4c4d889ce1691ce64`, runtime SHA는
`103ec280b50ac658504b5263a200896c1b39d66244269bc373dcfd23225ce02b`이다.

다음 한 가지는 새 middle tier(Claude Code `claude-opus-5`/high)의 **R6-B-R5 독립 검수**다.
범위 승인 뒤 새 work tier가 R6-B-R7을 처리한다. S1/F2-R2와 R6-B-R2는 상위/사용자 재결
전 금지다.

## lap234 — middle tier R6-B-R5 독립 검수 = 범위 승인

Claude Code `claude-opus-5`/high가 게임 없이 lap233 회귀를 독립 검수했다. 검수자는 저장소
테스트 헬퍼를 재사용하지 않고 핀된 주소 상수(`G1_SELECTION_COUNT_ADDRESS`,
`G1_SELECTION_FIRST_SLOT_ADDRESS`, `G1_UNIT_EXISTS_BASE_ADDRESS+slot*2`,
`G1_UNIT_BASE_ADDRESS+slot*G1_UNIT_STRIDE+G1_UNIT_TYPE_OFFSET`)만으로 최소 byte-level reader를
직접 만들어 세 축을 확인했다. probe는
`docs/history/laps/probes/20260912_lap234_r6b_r5_review_probe.py`, 보고서는 같은 디렉터리의
`..._report.json`(attempt1과 PROVENANCE도 보존)이다.

1. 도달성 12/12 AGREES. 실제 reader가 C4(OSError), C5(비활성 slot), D1(음수 count),
   type 0, slot 범위밖, count>pool(1201), struct.error, type 주소 읽기 실패를 모두 만들 수 있고
   전부 CORRUPTED로 닫힌다. count 0은 여전히 SOUND이므로 R6-B-R2 semantics는 불변이다.
2. fail-close 15/15 AGREES. 손상 관측 7종 × 양방향 14케이스가 `responded=False` +
   `status=CORRUPTED`이고 first/last corruption provenance가 보존된다. 건전한 식별자 변화는
   여전히 `responded=True` + `SOUND`로 PASS 경로가 열려 있다.
3. 비공허성 4/4 AGREES. `_g1_selection_responded`를 약화한 변이에서 lap233 테스트가 실제로
   실패한다: M1(UNKNOWN type 허용) → c4/c5/c7, M2(음수 count 허용) → d1,
   M3(항상 SOUND) → 4케이스 전부. 변이 없음(M0)에서는 4케이스 모두 통과한다.

설계 사실(결함 아님): `_read_selection`은 reader의 `try` 앞에서 실행되므로 selection
count/first-slot 주소의 읽기 실패는 CORRUPTED 관측이 아니라 예외로 reader를 빠져나간다.
`_wait_state`의 `read_error_count`→`UNKNOWN_STATE_READ_FAILURE`(R6-B-R6)와 `g1_baseline`의
OSError 처리가 한 단계 위에서 fail-close한다. 다만 `_g1_run_input_sequence`가 `_wait_state`
밖에서 직접 호출하는 `read_selection()` 5곳(`tools/runtime_env.py:2478/2516/2560/2607/2628`)은
그 경우 단계 분류 없이 run 전체 `evidence["error"]`로만 남는다. 정확성 구멍이 아니라 진단성
문제이므로 비차단 **R6-B-R9**로 등록한다.

검증: targeted selection 18 passed, `make check` 253 passed, Ruff/compileall/mypy 10 files +
`CONTEXT_PASS`, `LOOP_DRY_RUN=0 bash checks/safety.sh check` `SAFETY_PASS`, lap232 probe
재실행 18/18 AGREES(원본 보고서 미덮어씀, `--output /tmp/lap234_rerun_lap232.json`).
원본 EXE pin `b56986e0…c08a8ac`는 4개 pinning 파일에서 불변이고,
`tools/runtime_env.py` `103ec280…5ce02b` / `tests/test_runtime_env.py` `c8830c12…91ce64`는
lap233 기록과 일치한다. 게임 0회, PNG 0장, 제품/도구 코드 변경 0, 커밋 0.

다음 한 가지는 새 work tier의 **R6-B-R7** 수리다. lap234 probe가 기존 보고서가 있으면 쓰기를
거부하고 출력 경로 인자를 받는 형태를 구현 참고로 쓴다. 그 뒤 R6-B-R8 → R6-B-R9 →
F2-R1 → F3-R1 → F3-R2 → F6-R2다. S1/F2-R2와 R6-B-R2는 상위/사용자 재결 전 금지다.

## lap235 — work tier R6-B-R7 수리

lap228 middle review probe의 보고서 출력 경계를 수리했다. `--output`으로 새 경로를 지정할 수
있고, 기본 lap228 경로를 포함해 기존 파일은 먼저 거부한다. 마지막 쓰기도 `Path.open("x")`와
`FileExistsError` 처리로 수행해, 사전 확인과 실제 생성 사이에 다른 재실행이 끼어도 기존 증거를
덮어쓰지 않는다. 기존 lap228 JSON은 lap230 재실행 때 이미 소실됐으므로 복구하거나 재구성하지
않았다.

회귀 테스트 `tests/test_review_probe_output.py`는 기존 sentinel 파일이 byte-for-byte 보존되고
종료 코드 2가 반환되는지, 새 명시 경로에는 lap228 보고서가 생성되는지를 고정한다. targeted
2 passed, `make check` 255 passed, Ruff/compileall/mypy 10/`CONTEXT_PASS`,
`LOOP_DRY_RUN=0 bash checks/safety.sh check` `SAFETY_PASS`. 게임 실행·PNG·EXE/DLL/assets/
baseline/golden 변경·커밋은 0이며 `tools/runtime_env.py` SHA는
`103ec280b50ac658504b5263a200896c1b39d66244269bc373dcfd23225ce02b`로 불변이다.

다음 한 가지는 새 work tier의 **R6-B-R8** 수리다. 읽기 오류가 관측 창 대부분이어도 마지막
성공 poll 하나만으로 `FAIL_NO_EFFECT`가 되지 않도록 커버리지 임계의 필요·형태를 검토하고,
기존 R6-B-R2/R3/R4 semantics와 PASS 경로를 보존한다. S1/F2-R2 및 R6-B-R2 재결 전 게임·
Stage B 실행은 금지다.

## lap236 — middle tier R6-B-R7 독립 검수 (범위 승인)

Claude Code `claude-opus-5`/high, 게임 0회·PNG 0장·제품/도구 코드 변경 0으로 lap235 수리를
독립 검수했다. lap235가 기록한 probe `2d4f6b36…50e7eb`, 테스트 `9f1992e5…3b6f39b6`,
`tools/runtime_env.py` `103ec280…5ce02b`는 실제 파일 해시와 일치했고, `make check` 255 passed
(Ruff/compileall/mypy 10 files + `CONTEXT_PASS`)와 `SAFETY_PASS`를 재현했다. 원본 EXE pin
`b56986e0…c08a8ac`는 4개 pinning 파일에서 불변이다.

자체 probe(`docs/history/laps/probes/20260912_lap236_r6b_r7_review_probe.py`,
보고서 `…_review_report.json`) 13케이스 중 11 AGREES / 2 DEFECT다. 보존 7종 —
내용 있는 기존 파일, 0바이트 파일, 디렉터리, 기존 파일을 가리키는 심볼릭 링크, **dangling
심볼릭 링크**, 인자 없는 기본 경로, **import 실행(`__name__ != "__main__"`)** — 이 모두 exit 2로
fail-close하고 대상 바이트는 보존됐다. 뒤의 두 경우는 `exists()` 검사를 지나치므로
`open("x")` 배타 생성 분기만이 유일한 가드이며, 이로써 lap235가 주장한 경쟁 보호의 도달성이
실증됐다. 새 경로 보고서는 보존된 lap230 재실행본과 `source_sha256`(현재 `103ec280…`,
lap230 당시 `f39d26fc…`)만 다르고 reachability/preservation/wait/surgicality 판정은 전부 동일해
R6-B-R3 리뷰 결론이 현재 코드에서도 재현된다.

비공허성(`…_mutation_probe.py`, 보고서 `…_mutation_report.json`): 변이 없음 2 passed,
두 가드 동시 제거(M3)와 `--output` 무시(M4)에서 lap235 테스트가 실제로 1 failed가 된다.
사전 검사만 제거(M1) 또는 배타 생성만 제거(M2)는 잡히지 않는다 — 각 가드 단독으로도 관측 가능한
계약을 만족하기 때문이며 동작은 여전히 옳다. 경쟁 보호 분기에 독립 회귀가 없다는 커버리지
공백으로 비차단 **R6-B-R11**에 등록했다.

DEFECT 2건은 보존 결함이 아니다. `--output`은 존재만 검사하고 쓰기 가능성은 검사하지 않아,
부모 디렉터리가 없거나(C1) 쓰기 불가일 때(C2) exit 2 거부 대신 probe 전체 계산을 마친 뒤
미분류 traceback + exit 1로 끝난다. 파일은 생성되지 않으므로 증거는 보존되지만 실패 분류와
비용이 나쁘다 → 비차단 **R6-B-R10**.

다음 한 가지는 새 work tier의 **R6-B-R8**(관측 커버리지 임계)이다. 그 뒤 R6-B-R9 →
R6-B-R10 → R6-B-R11 → F2-R1 → F3-R1 → F3-R2 → F6-R2다. S1/F2-R2와 R6-B-R2는 상위/사용자
재결 전 금지이며, 그 전까지 게임 실행과 Stage B run도 금지다.

## lap237 — work tier R6-B-R8 수리

`_wait_state`의 timeout 증거에 `successful_poll_ratio`, `read_error_ratio`, 임계 비율,
초과 여부를 추가했다. 읽기 오류 비율이 `G1_INPUT_MAX_READ_ERROR_RATIO=0.25`를 **초과**하면
최종 poll이 성공했더라도 `UNKNOWN_STATE_READ_COVERAGE`로 fail-close하고, 선택 관측 상태도
`UNAVAILABLE`로 닫는다. 임계는 기존 pre-poll truncation의 보수적 25% 허용과 같은 값으로,
최소 75%의 poll이 읽혀야 hard `FAIL_NO_EFFECT`를 주장하도록 한 것이다. 모든 poll 실패와
마지막 poll 읽기 실패는 기존 `UNKNOWN_STATE_READ_FAILURE`가 우선하며, 효과가 실제 관측된
PASS 경로와 R6-B-R2/R3/R4 semantics는 변경하지 않았다.

회귀는 3회 오류+1회 성공(`UNKNOWN_STATE_READ_COVERAGE`), 정확히 1회 오류+3회 성공
(`FAIL_NO_EFFECT`), 기존 읽기 tail 증거를 실제 fake-clock reader로 고정한다. 게임 실행·PNG·
바이너리·baseline/golden 변경·커밋은 0이다. 다음 한 가지는 새 middle tier가 R6-B-R8을
독립 검수하는 것이며, 승인 뒤 R6-B-R9로 진행한다.

## lap238 — middle tier R6-B-R8 독립 검수 (범위 승인)

Opus5/high가 게임 없이 R6-B-R8을 검수해 **범위 승인**했다. 4-poll 창의 오류 마스크 16가지를
전수로 돌려 독립 재작성한 기대식과 대조했고 불일치 0건이다. 정확히 `read_error_ratio=0.25`
(오류1/성공3)와 오류 0건 무반응은 `FAIL_NO_EFFECT`로 남아 hard 경계가 보존되며, `0.5`/`0.75`는
`UNKNOWN_STATE_READ_COVERAGE`로 닫히고 selection은 `UNAVAILABLE`이 된다. 마지막 poll이 읽기
실패인 8개 마스크와 전체 실패는 전부 `UNKNOWN_STATE_READ_FAILURE`를 유지해 R6 우선순위가
퇴행하지 않았다.

새 PASS 경로는 없다. 무반응 행렬에 PASS가 0건이고, `record()`는 `predicate_observed = result ==
"PASS"`로 새 분류 문자열을 승격하지 않으며, `tools/compare_g1_stage_b.py`는 `result != "PASS"`를
모두 `UNKNOWN_DISPUTED_ORACLE` → 상위 `INCONCLUSIVE`로 닫는다. 즉 R8은 UNKNOWN 대역을 넓히고
hard FAIL 대역을 좁힐 뿐 comparator 판정을 완화하지 않는다. poll 0회 창도 truncation(ratio>=1.0)
또는 budget exhaustion UNKNOWN으로 닫히므로 관측 없는 hard FAIL은 도달 불가다. `errors/attempts
== 0.25`는 분모가 4의 배수일 때만 성립해 이진 표현이 정확하므로 경계 부동소수 위험도 없다.

비공허성은 변이 5종으로 확인했다(base targeted 13 passed): `>`→`>=`, 분류 분기 삭제,
selection `UNAVAILABLE` 커플링 제거, COVERAGE/READ_FAILURE 우선순위 교체, 임계 비교 상수화 —
전부 회귀가 깨졌고 각 변이 후 `tools/runtime_env.py`를 sha256 동일하게 원복했다. 검수 산출물은
`docs/history/laps/probes/20260912_lap238_r6b_r8_review_probe.py`(보고서
`…_review_report.json`, sha256 `e58b73b5…13792a54`)이며 재실행 시 기존 보고서를 덮지 않고
`FileExistsError`로 거부하는 것까지 확인했다.

lap237이 남긴 FINAL BLOCKER(문서 갱신 뒤 `make check` 13 failed, STATUS 188줄 안전 위반)는
이번 재실행에서 해소를 확인했다: STATUS 80줄, `make check` 257 passed, mypy 10 files,
`CONTEXT_PASS`, `SAFETY_PASS`, 원본 EXE pin 4개 파일 불변.

비차단 신규 발견 2건 — **R6-B-R12**: selection `CORRUPTED`와 커버리지 부족이 겹치면 `status`가
`UNAVAILABLE`로 덮여 CORRUPTED가 가려진다(`corrupted_poll_count`/provenance는 보존되고 양쪽 다
UNKNOWN이라 완화는 아니다). **R6-B-R13**: 효과가 관측된 return 경로는 커버리지로 gate하지 않는
의도된 비대칭인데, `read_error_ratio`를 읽는 소비자가 없어 PASS 증거에 커버리지가 노출되지 않는다.

다음 한 가지는 새 work tier의 **R6-B-R9**(reader 직접 실패의 단계 진단)이며, 그 뒤 R10 → R11 →
R12 → R13 → F2-R1 → F3-R1 → F3-R2 → F6-R2다. S1/F2-R2와 R6-B-R2는 상위/사용자 재결 전 금지이며
그 전까지 게임 실행과 Stage B run도 금지다. `UNKNOWN_STATE_READ_COVERAGE`는 blind retry 사유가
아니라 read error provenance로 원인을 좁혀야 하는 신호다.

## lap239 — work tier R6-B-R9 수리

`_g1_run_input_sequence`의 `_wait_state` 바깥 selection reader를
`_g1_read_selection_stage`로 감싸 직접 `OSError`/`ValueError`/`struct.error`를
`UNKNOWN_STATE_READ_FAILURE`로 fail-close했다. `before_click`, `before_drag`, `after_drag`,
`before_minimap`, `after_minimap`은 해당 입력 stage의 timeout record로 즉시 flush하며,
`direct_reader`, read point, attempt/error count, poll count 0, first/last exception provenance를
남긴다. production의 `before_production` reader 실패는 production을 여전히 클릭 없이
`BLOCKED`로 기록하되 selection reader 진단을 레코드에 보존하고 drag/minimap은 계속한다.
기존 `_wait_state` polling 분류, R6-B-R2/R3/R4/R6/R8 semantics, production click fail-close는
변경하지 않았다. direct failure 시 캡처가 아직 불가능한 단계에는 `NOT_CAPTURED`를 명시한다.

회귀는 다섯 direct stage 지점 + production direct path를 fake reader로 검증했다. targeted
`10 passed`; `make check` `263 passed` + Ruff/compileall/mypy 10 files/`CONTEXT_PASS`;
`LOOP_DRY_RUN=0 bash checks/safety.sh check` `SAFETY_PASS`. 원본 EXE pin
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 게임/Wine/Xvfb/PNG/
제품 자산 변경 0, 커밋 0. 현재 source SHA는 lap239 기록에 남긴다.

R6-B-R9는 새 middle tier의 독립 검수와 범위 승인 전이다. 검수 시 직접 실패가 stage record로
flush되는지, production 경로가 후속 입력을 유지하는지, polling UNKNOWN 우선순위와 PASS 경로가
불변인지 확인한다. 승인 전에는 R10 및 Stage B 실행을 진행하지 않는다.

## lap240 — middle tier R6-B-R9 독립 검수 (범위 승인)

work가 쓴 `tests/test_runtime_env.py` 하네스를 재사용하지 않고 새 fake selection/camera reader와
fake-clock으로 `_g1_run_input_sequence`를 직접 구동해 검수했다. 먼저 AST로 함수 안의 직접
`_g1_read_selection_stage` 호출점을 열거해 `before_click`/`before_production`/`before_drag`/
`after_drag`/`before_minimap`/`after_minimap` 6개와 정확히 일치하고 중복이 없음을 확인했다.
work가 주장한 "5지점"은 예외를 전파하는 지점이고 production은 여섯 번째 계속-진행 지점이다.

raising 15-case(5지점 × `OSError`/`ValueError`/`struct.error`) 불일치 0. 각 케이스에서 record
`result`·`timeout_cause`가 `UNKNOWN_STATE_READ_FAILURE`, `direct_reader=selection`,
`direct_reader_failure=True`, read point 일치, `poll_count`/`poll_attempt_count`=0,
`direct_read_error_count=1`, first==last provenance가 예외 타입과 일치, `predicate_observed=False`
였다. 특히 예외 전파 **전에** 해당 stage 레코드가 `evidence.json`에 이미 있는지를 메모리가 아니라
디스크에서 확인했다. production 3-case는 예외 탈출 0, `BLOCKED`/`waited=False` 유지,
`selection_read_failure`에 stage/read point/provenance 보존, 입력 순서와 클릭·드래그 좌표 불변,
후속 drag/minimap PASS였다. 무결 경로는 PASS/BLOCKED/PASS/PASS에 UNKNOWN 0건이고, 미모델링
`KeyError`는 read-failure로 위장되지 않고 그대로 전파됐다.

하네스가 실패를 놓치지 않는지 변이 5종으로 확인했고 5/5 검출했다 — catch를 `OSError`로 축소,
classification을 `FAIL_NO_EFFECT`로 완화, `direct_read_point` 제거, `after_drag` 실패를 가짜
성공으로 삼킴, production 실패가 후속 입력을 중단. 변이는 `tools/runtime_env.py` **사본**을 임시
디렉터리에 적재해 실행했고 원본은 `bb10cd84…918d2dab`로 해시 불변이다. 검수 산출물은
`docs/history/laps/probes/20260912_lap240_r6b_r9_review_probe.py`(보고서 `…_review_report.json`,
sha256 `647bdb1c…d74c7bbd`)이고 재실행 시 `FileExistsError`로 거부되는 것까지 확인했다.
첫 실행은 `verdict=FAIL`이었으나 원인은 minimap 카메라를 고정 call-index로 돌려준 **probe 결함**
이었고, 실패 산출물과 원인은 `…attempt1.json`/`…PROVENANCE.md`에 보존했다. 제품 코드·임계값·
baseline·golden은 통과를 위해 바꾸지 않았다. `make check` 263 passed, mypy 10 files,
`CONTEXT_PASS`, `SAFETY_PASS`, 원본 EXE pin 불변, 게임/Wine/Xvfb/PNG 0.

비차단 신규 발견 2건 — **R6-B-R14**: production 레코드의 `before/after.selection`이 read 실패
시에도 `{"status":"UNAVAILABLE","count":null}`이라 "읽지 않음"과 "읽기 실패"가 최상위에서 구별되지
않는다(provenance는 `selection_read_failure`에 보존, production은 어차피 `BLOCKED`라 완화 아님).
R6-B-R12와 같은 계열이다. **R6-B-R15**: `_g1_read_selection_stage`는 run budget이 이미 소진된
순간의 직접 실패도 무조건 `UNKNOWN_STATE_READ_FAILURE`로 닫는데(`remaining_budget_after=0.0`으로
재현), `_wait_state`는 같은 상황에 `UNKNOWN_BUDGET_EXHAUSTED`를 우선한다. 둘 다 UNKNOWN이라 PASS
완화는 아니나 분류 provenance가 갈리고, production 경로는 `remaining_budget_after`/
`finished_elapsed`가 레코드에 남지 않는다.

다음 한 가지는 새 work tier의 **R6-B-R10**(probe 쓰기 불가 경로 분류)이며, 그 뒤 R11 → R12 →
R13 → R14 → R15 → F2-R1 → F3-R1 → F3-R2 → F6-R2다. R14/R15는 provenance 정밀도 항목이라 R10을
막지 않는다. S1/F2-R2와 R6-B-R2는 상위/사용자 재결 전 금지이며 그 전까지 게임 실행과 Stage B run도
금지다. 이번 바퀴는 middle 범위 승인일 뿐 사용자 마일스톤 승인이 아니다.

## lap241 — work tier R6-B-R10 probe 쓰기 불가 경로 분류

R7 probe(`20260912_lap228_r6b_r3_review_probe.py`)의 `--output` 경계를 조기 검사하도록
수리했다. 기존 경로 거부와 `open("x")` 배타 생성은 유지하면서, 출력 부모가 없거나
디렉터리가 아니거나 `W_OK|X_OK`가 없으면 probe 본문을 실행하지 않고 명시적인 `exit 2`와
분류 메시지를 남긴다. preflight와 exclusive open 사이에 부모가 바뀌는 경우의 `OSError`도
raw traceback 대신 동일한 fail-close 분류로 닫는다. 보고서 계산·내용·기존 증거는 변경하지
않았다.

회귀 `tests/test_review_probe_output.py`는 정상 새 경로 작성, missing parent, non-directory
parent, read-only parent 및 stderr traceback 부재를 고정한다. targeted `5 passed`; `make check`
`266 passed`, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash
checks/safety.sh check` `SAFETY_PASS`. 게임/Wine 실행·PNG·원본 EXE pin·candidate/baseline/golden
변경은 0이다. 기존 Xvfb 프로세스는 관측만 하고 건드리지 않았다.

R6-B-R10 work 범위는 **PASS**이며 middle 독립 검수 전이다. 제품 G1/Stage B는 **SKIP**이고,
R6-B-R11~R15, S1/F2-R2, R6-B-R2, WM_CLOSE, G2~G4는 미해결이다. 다음은 새 middle tier가
게임 없이 R10 조기 분류·raw traceback 부재·기존 R7 보호/보고서 재현을 독립 검수하는 것이다.

## lap242 — middle tier R6-B-R10 독립 검수 (범위 승인 보류, FAIL)

lap241의 조기 출력-경계 분류를 게임 없이 독립 재도출했다. 하네스
`docs/history/laps/probes/20260912_lap242_r6b_r10_review_probe.py`(보고서 `…_review_report.json`)는
`tests/test_review_probe_output.py`를 import하지 않고 출하 probe를 subprocess로 구동한다.

확인된 것: 사용 불가 출력 11-case 중 10건이 `exit 2`+분류 메시지+stderr traceback 0으로 닫히고
fixture 11/11이 보존된다(missing·deep missing·regular file·symlink-to-file·dangling symlink 부모,
read-only 부모, 기존 파일·기존 디렉터리·기존 대상 symlink·dangling symlink 출력). 정상 3/3(새 경로,
symlink된 디렉터리 부모, 상대 경로)은 `exit 0`과 보고서 생성. 조기 실행은 AST 문장 순서(guard 120행
< 본문 134행)와 프로파일 추적(본문 함수 0회 실행)으로 확인했다. 신규 보고서는 저장된 lap228
보고서와 `source_sha256`만 다르고 측정 전 구간이 동일하다. 무변이 control `5 passed`, 변이 4/5 검출.

**막는 결함 (work tier로 이관):**
- **R6-B-R16** — 출력 부모가 `0o600`(쓰기 가능·탐색 불가)이면 `output_refusal`의 첫 절
  `path.exists()`가 `PermissionError`를 그대로 올려 raw traceback과 `exit 1`로 끝난다. R10이
  닫겠다고 한 실패 계열이 guard 자신에게 남아 있다. `output_refusal` 전체를 fail-close로 감싸
  `OSError`를 분류 메시지+`exit 2`로 닫아야 한다.
- **R6-B-R17** — 조기 `path.exists()` 절을 삭제한 변이 M3을 출하 회귀가 검출하지 못한다
  (`5 passed`). 늦은 `open("x")` FileExistsError 경로가 같은 메시지/exit를 내므로 조기 거부가
  고정돼 있지 않고, 삭제 시 O(1) 거부가 전체 예산 소모 후 거부로 조용히 퇴행한다. 조기 거부와
  늦은 대체 경로를 구분하는 회귀가 필요하다.
- **R6-B-R18 (비차단)** — lap241 기록의 `tools/runtime_env.py` 지문이 72자로 손상됐다.
  `loop/ESCALATE_SOL`의 64자 값이 실제 파일과 일치한다.

`make check` `266 passed`, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash
checks/safety.sh check` `SAFETY_PASS`. 게임/Wine/Xvfb 실행·PNG 0, 보호 소스·원본 EXE pin·저장된
lap228 보고서 해시 불변. 하네스 결함 2건은 attempt1/attempt2와 `…PROVENANCE.md`에 보존했다.
제품 G1/Stage B는 **SKIP**이고 Stage B·게임 실행은 계속 금지다.

## lap243 — work tier R6-B-R16/R17 수리

lap242 middle FAIL의 두 결함만 게임 없이 수리했다. `output_refusal()`의
`path.exists()`/`is_dir()`/`os.access()` 조회를 `OSError` fail-close로 감싸 탐색 불가 부모를
`output path unavailable` 분류와 `exit 2`로 닫았고, 기존 evidence 거부가 늦은
`open("x")` fallback으로 퇴행하지 않도록 subprocess 프로파일 회귀를 추가했다. R10 독립
probe의 mutation 문자열도 새 들여쓰기에 맞춰 M1~M3 검출을 유지했다.

변경 파일은 `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`,
`docs/history/laps/probes/20260912_lap242_r6b_r10_review_probe.py`,
`tests/test_review_probe_output.py`다. 최종 SHA는 각각
`16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`,
`7a4dfdff8067d76ef129a366caa558feffad69c5a94f3dbe22c04c93c71e9d6f`,
`c9671f6d93b498d2615af8531e39245cb1acabf6ba29842147f2a2d639b745eb`다.

검증: `.venv/bin/python -m pytest -q tests/test_review_probe_output.py` = **7 passed**;
`.venv/bin/python docs/history/laps/probes/20260912_lap242_r6b_r10_review_probe.py
--report docs/history/laps/probes/20260912_lap243_r10_repair_review_report.json` = classification 11/11, healthy 3/3,
mutation 5/5, `verdict=PASS` (report SHA
`94460e5410263c543b2afd34ab93f99972a117ab6abd5441eca23bb13c7805eb`); `make doctor` original
SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, side-effects false;
`make check` = **268 passed**, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`;
`LOOP_DRY_RUN=0 bash checks/safety.sh check` = **SAFETY_PASS**. `tools/runtime_env.py` SHA
`bb10cd84ddcb521b704318aeccb60125cec0abd89436e16b0b25d1ed918d2dab` unchanged. Game/Wine/
Xvfb/PNG 0, original EXE/assets/baseline/golden 0.

R6-B-R10 work 결과는 **PASS**, middle 독립 재검수 전이라 범위 승인 아님. 첫 targeted 실행의
프로파일 wrapper argv 오류와 첫 review probe mutation 들여쓰기 불일치는 수정 후 최종 결과에
포함되지 않으며, blind retry가 아니라 원인별 bounded repair로 보존했다. 다음은 새 middle tier가
R10을 독립 재검수하는 것이며, 승인 전 Stage B·게임 실행은 금지한다.

## lap244 — middle tier R6-B-R10 독립 재검수 (승인) 및 R19 handoff

lap243 work 결과를 게임 없이 독립 재검수했다. lap242/lap243 하네스·fixture·보고서를 재사용하지
않고 `docs/history/laps/probes/20260912_lap244_r6b_r10_reverify_probe.py`
(`b57c21825f7e79a348340b82bcd1e62dac88e2f792f39c2f58b5a83cb44b2f40`)를 새로 작성했다. 결과
보고서는 `...reverify_report.json`
(`635831909fbf17c2d0e938b24d5e748dd36778b30149f4b5a2b082f3b4cdec90`), `verdict=PASS`.

측정: 분류 14-case 전수 AGREES(거부 9건 `exit 2`·분류 문자열·traceback 0·fixture 보존·경로 존재
상태 불변, 정상 4건 신규 생성); 조기성은 call profiler가 아닌 **SUT 라인 트레이싱**으로 거부 5종
본문 라인 0줄(최대 실행 라인 128, `__main__` 가드 끝 130)·정상 대조군 205줄; 변이 M0~M5에서
control 7 passed·나머지 5/5 검출; 보고서는 fresh 경로 2회 바이트 동일·`source_sha256` 일치·
`game_executions=0`·재실행 거부 시 원본 불변. `make check` 268 passed, `SAFETY_PASS`.
검수 전후 `20260912_lap228_r6b_r3_review_probe.py`, `tests/test_review_probe_output.py`,
`tools/runtime_env.py` 해시 불변. 게임/Wine/Xvfb/PNG 0.

**판정: R6-B-R10(R7/R16/R17 포함) 범위 승인.** 사용자 마일스톤 승인 아니며 Stage B·게임 실행
금지는 유지한다.

### work tier로 넘기는 신규 카드 R19 (구현 금지 항목 아님, 큐 순서는 R15 뒤)

증상: `tests/test_review_probe_output.py::test_r6b_r17_existing_evidence_refusal_precedes_review_body`
가 감시하는 이름 집합 `{"reachability","surgicality","preservation","drive_wait"}` 중 앞 세 개는
모듈 **변수**라 프로파일러 `co_name` call 이벤트로 절대 나타나지 않는다. R17 보호는 사실상
함수명 `drive_wait` 하나에 걸려 있다.

lap244 실측: 미러 트리에서 `drive_wait`를 `run_wait_sequence`로 개명하고 조기 `path.exists()`
거부를 삭제하면 이 테스트는 **통과**한다(개명만 한 대조군은 7 passed). 즉 probe 본문을 흔드는
평범한 리팩터 뒤에는 조기 거부가 사라져도 회귀가 침묵한다.

요구: 이름에 의존하지 않는 증거로 바꾼다. 예) 프로파일 대신 SUT 파일의 **본문 라인 실행 수**가
0인지 측정하거나(가드 경계는 AST로 계산), 본문 진입을 나타내는 명시 마커를 관측한다. 수리 뒤
회귀는 "조기 거부 삭제" 변이를 이름 개명 여부와 무관하게 검출해야 한다. 제품 EXE/DLL/assets/
baseline/golden과 `tools/runtime_env.py`는 건드리지 않는다.

## lap245 — work tier R6-B-R11 배타 생성 단독 가드 회귀

R10 승인 뒤 큐의 첫 후속인 R11을 게임 없이 처리했다. `tests/test_review_probe_output.py`에
`exists()`가 false인 dangling output symlink fixture를 추가해 `Path.open("x")`의 배타 생성
경로를 단독으로 관측한다. 실행 결과는 exit 2, 기존 symlink 보존, symlink target 미생성이다.

비공허성은 저장소 밖 임시 미러에서 `open("x")`만 `open("w")`로 바꾼 뒤 같은 테스트를 실행해
확인했다. pytest는 8 failed였고 그 목록에 새
`test_r6b_r11_exclusive_create_rejects_dangling_output_symlink`가 포함됐다. 원본 probe SHA는
`16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`, 테스트 SHA는
`6ebf9e3248a8a494829d3dbfafd7e62d4308534158995069ba98c4d930755bb2`다.

targeted **8 passed**, `make check` **269 passed**(Ruff/compileall/mypy 10 files,
`CONTEXT_PASS`), safety **`SAFETY_PASS`**. 게임/Wine/Xvfb/PNG·제품 바이너리·자산·baseline/
golden 변경은 0이다. R11은 work PASS이나 middle 독립 검수와 제품 G1 승인은 없다. 다음은
새 middle의 R11 검수 후 R12이며, S1/F2-R2 재결 전 Stage B 실행 금지는 유지한다.

## lap246 — middle tier R6-B-R11 독립 검수 (회귀 승인 / lap245 증거 무효)

검수자: Claude Code `claude-opus-5`/high, middle tier. 게임/Wine/Xvfb/PNG 실행 0회.
독립 하네스 `docs/history/laps/probes/20260912_lap246_r11_reverify_probe.py`
(sha256 `06a1991a27babcee94a06f4367a54868a6dc1dd632b8e2e6d87c8ffa65a0be67`), 보고서
`...20260912_lap246_r11_reverify_report.json`
(sha256 `5b4cf4bf5fd0d35a596247d73f8a7c158e73f96fe439f074cb8487be60faef63`).

측정: C0 실제 probe **8 passed**. C1 lap245와 동일한 얕은 `/tmp` 재배치인데 **변이가 없는**
복사본도 **8 failed**이며 실패 목록이 lap245 보고서와 동일하다. 원인은 SUT probe의
`ROOT = Path(__file__).resolve().parents[4]`가 얕은 경로에서 `IndexError: 4`를 던져 import
단계에서 죽는 것이다. C2 `parents[4]` 깊이를 맞춘 미러(+`tools/runtime_env.py` 사본)는
**8 passed**. C3 같은 미러에서 `open("x")→open("w")`는 **1 failed, 7 passed**로
`test_r6b_r11_exclusive_create_rejects_dangling_output_symlink` 하나만 죽였고 preflight가
결정하는 R7/R10/R17 6건은 생존했다. 직접 관측은 `x`=exit 2·symlink 보존·target 미생성,
`w`=exit 0·target 생성이다.

**판정: R11 회귀 자체는 범위 승인**(비공허성을 독립 증거로 재성립). **lap245가 제출한
비공허성 증거(`caught=true`, `verdict=PASS`)는 무효**이며 원문은 삭제하지 않고
`...20260912_lap245_r11_regression_report.PROVENANCE.md`에 사유를 붙였다. 사용자 마일스톤
승인 아니며 Stage B·게임 실행 금지는 유지한다. `make check` 269 passed, safety `SAFETY_PASS`.

### work tier로 넘기는 신규 카드 R20 (큐 순서는 R19 뒤)

증상: 저장소 밖 미러에서 SUT를 변이해 회귀의 비공허성을 증명하는 하네스에 **M0 대조군**
(변이 없는 같은 미러)이 없으면, 미러가 깨져 SUT가 실행조차 못 하는 경우를 "변이 검출"로
오독한다. lap244는 M0 대조군을 썼고 lap245가 그것을 빼면서 정확히 이 오독이 발생했다.

요구: 미러 기반 변이 하네스는 (a) 변이 없는 같은 미러가 **기준선과 동일하게 green**임을 먼저
기록하고, (b) 변이가 죽인 테스트 **목록**을 기록해 "전멸"과 "표적 사망"을 구분하며,
(c) 미러 배치가 SUT의 경로 가정(여기서는 `parents[4]`)을 만족하는지 검사한다. 셋 중 하나라도
없으면 비공허성 주장을 PASS로 적지 않는다. 제품 EXE/DLL/assets/baseline/golden과
`tools/runtime_env.py`는 건드리지 않는다.

## lap247 — work tier R6-B-R12 CORRUPTED 상태 보존

lap238 middle이 발견한 결함은 selection reader가 이미 `CORRUPTED`와 손상 provenance를 기록한
뒤 read-error tail 또는 read-error coverage 부족으로 timeout할 때, `_wait_state`의 공통 표기가
상태를 `UNAVAILABLE`로 덮어쓰는 것이었다. 양쪽 모두 UNKNOWN 분류여서 hard-fail 완화는 아니지만,
구체적인 손상 원인이 최종 evidence에서 가려졌다.

이번 work는 `tools/runtime_env.py`의 해당 덮어쓰기만 조건부로 바꿨다. selection 상태가
`CORRUPTED`이면 그대로 보존하고, `SOUND` 경로는 기존처럼 `UNAVAILABLE`로 닫는다. timeout
classification 우선순위와 R6-B-R2 semantics는 변경하지 않았다. 회귀는
`tests/test_runtime_env.py`에 읽을 수 있는 corrupted observation 뒤 3회 read error(coverage
분류), 그리고 corrupted observation 뒤 read-error tail(즉시 read-failure 분류)을 추가해 두
UNKNOWN 원인과 corruption provenance를 함께 확인한다. 기존 sound observation의
`UNAVAILABLE` 회귀도 유지된다.

변경 파일 / SHA: `tools/runtime_env.py` sha256
`2f59bbbd14c177119117a9435df0426a66142d4ed1d8cb1b19105a4b3a8025c4`,
`tests/test_runtime_env.py` sha256
`d75c75b43a0e32d72882361a2ac80a700825895ecb9cbae24a63a42732f5f842`; uncommitted,
`LOOP_ALLOW_COMMITS=0`. 원본 EXE pin
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
`tools/runtime_env.py` pre-change sha256
`bb10cd84ddcb521b704318aeccb60125cec0abd89436e16b0b25d1ed918d2dab`; product EXE/DLL/assets/
baseline/golden 변경 0.

검증: targeted R12 regression = **4 passed**; `make check` = **271 passed**, Ruff/compileall/
mypy 10 files, `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash checks/safety.sh check` = **SAFETY_PASS**;
`make doctor` = `ok: true`, original verified, side effects false. Fresh runtime manifest는
없어 실행 검증은 하지 않았으며 이번 게임 금지 범위에서 N/A다.
Fixture는 fake-clock/fake-reader 구성이고 실제 게임 상태·플레이어·지도·군대·Wine/Xvfb/PNG는
N/A/0.

판정: R12 work **PASS**, 아직 middle 독립 검수 전. 사용자 마일스톤 승인 없음. S1/F2-R2,
R6-B-R2, R13~R15, R19/R20, F2/F3/F6 및 제품 G1은 미해결이다. 다음 한 가지는 새 middle
세션이 이 변경을 독립 probe로 검수하는 것; 그 전 Stage B·게임/Wine 실행 금지는 유지한다.

## lap248 — middle tier R6-B-R12 독립 검수 (PASS / 범위 승인)

lap247 work의 R12 변경을 게임 없이 독립 probe로 재측정했다. probe는 lap247 하네스를 하나도
재사용하지 않았고 네 구간으로 나뉜다.

- **C0 BASELINE**: 실제 저장소에서 R12 2-param + 기존 UNAVAILABLE 2건 + 경계 FAIL_NO_EFFECT +
  corruption provenance 2건 = 7 passed, 129 deselected.
- **C1 MATRIX**: 구현을 보지 않고 계약에서 직접 쓴 기대 모델과 `{SOUND, CORRUPTED, ERROR}^4`
  81 케이스 전수 대조 — **불일치 0**. read error와 겹치면서 `CORRUPTED`가 보존된 32건 전부에서
  `first_corruption_provenance`가 살아 있고, SOUND는 20건 모두 `UNAVAILABLE`로 내려간다.
  분류 우선순위(read failure > coverage > selection corrupted > no effect)도 81/81 일치.
- **C2 MIRROR CONTROL (M0)**: 깊이를 맞춘 무변이 미러에서 `tests/test_runtime_env.py`
  136 passed로 실제 저장소와 동일. lap246 R20 교훈대로 변이 측정 전에 대조군을 세웠다.
- **C3 MUTATIONS**: M1 가드 삭제 → R12 케이스만 2 failed(기타 0). M2 가드 무조건 보존
  (`if False:`) → 기존 UNAVAILABLE 2건만 failed(R12 0). M3 가드 역전 → 4 failed(양쪽).
  가드가 load-bearing이면서 과하게 강하지 않음을 M1/M2가 각각 보여준다.

지문 교차 확인: 검수 시점 `tools/runtime_env.py` `2f59bbbd…8025c4`,
`tests/test_runtime_env.py` `d75c75b4…32f5f842`로 lap247 기록과 일치한다. lap247이 적은
pre-change `bb10cd84…d2bab`는 lap246 middle이 독립적으로 "불변"으로 남긴 값과 같아,
lap246 이후 유일한 델타가 R12 변경임이 확인된다. SUT는 이번 lap에 바꾸지 않았다.

승인 **범위**는 `_wait_state`의 최종 selection 표기 한 곳뿐이다. R6-B-R2 semantics, timeout
분류 우선순위, 제품 G1 증거는 승인 대상이 아니다. 남은 위험: 보존된 `CORRUPTED`는 마지막
성공 poll의 상태라 read-error tail과 겹치면 stale일 수 있고, 그 불확실성은 status가 아니라
classification과 상위 관측 필드가 담는다(현재 `tools/runtime_env.py` 밖에 이 status를 읽는
코드는 0개). 또 하네스 규약 결함 **R21**을 새로 올렸다: probe 출력 규약이 직렬화 전에
`open("x")`로 파일을 만들어, 쓰기 실패가 절단 증거를 남기고 R7 가드 때문에 재시도까지 막는다.

`make check` = 271 passed, `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash checks/safety.sh check` =
`SAFETY_PASS`; 게임/Wine/Xvfb/PNG 실행 0.

**다음 work tier에게**: R13(PASS 경로에서 read coverage가 관측에 노출되지 않는 결함)을 게임
없이 한 건만 구현한다. 회귀는 반드시 (a) 변이 전 무변이 대조군, (b) 변이가 죽인 테스트 목록,
(c) 미러 깊이 검사를 포함해 비공허성을 보인다. 제품 EXE/DLL/assets/baseline/golden과
S1/F2-R2 관련 Stage B·게임 실행은 계속 금지다.

## lap249 — work tier R6-B-R13 PASS coverage 노출

`_wait_state`가 성공 predicate를 반환할 때도 계산하는 poll/read-error coverage를 실제 Stage B
입력 기록과 최종 `input_checks` verdict에 노출하도록 `tools/runtime_env.py`를 수리했다.
`read_coverage`는 9개 관측 필드(`poll_count`, `poll_attempt_count`, `read_error_count`, 성공/오류
비율, 임계 비율·초과 여부, 첫/마지막 오류 provenance)를 안정된 형태로 투영한다. 성공 반환은
coverage 부족을 이유로 사후 UNKNOWN으로 바꾸지 않으며, timeout 분류와 R12 CORRUPTED 보존은
변경하지 않았다. `tests/test_runtime_env.py`에 transient read error가 있는 성공 경로와 verdict
노출 회귀를 추가했다.

변경 파일 / SHA: `tools/runtime_env.py`
`302c246e3637959c03a32b349befa0640cff72b1f1b5f1a349ad274b88421817`,
`tests/test_runtime_env.py`
`9a120a1ce1783bb605e21dc856cf64cdb4d289d5174bc9cbe328ba61735c8f8d`; uncommitted,
`LOOP_ALLOW_COMMITS=0`. 원본 EXE pin
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 제품 EXE/DLL/
assets/baseline/golden 변경 0.

검증: 사전 wait/selection targeted 17 passed. 변경 후 targeted **21 passed**; `make check`
**272 passed**, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash
checks/safety.sh check` = **SAFETY_PASS**. Fixture는 Python 3.13.5/.venv fake-clock +
fake-reader이며 실제 게임/Wine/Xvfb/PNG 실행은 0이다. transient sequence는 2 polls 중 성공
1/read error 1(`read_error_ratio=0.5`, threshold 초과)에서도 성공 반환했고 verdict에 동일
coverage가 노출됐다.

판정: R13 work **PASS**, 새 middle(Opus5/high) 독립 검수 전, 사용자 마일스톤 승인 없음.
S1/F2-R2, R6-B-R2, R14/R15/R19/R20/R21 및 제품 G1~G4는 미해결이다.

**다음 middle tier에게**: 게임 없이 R13을 독립 검수한다. 무변이 대조군, 변이가 죽인 테스트
목록, 깊이 일치 미러를 포함하고, Stage B·게임/Wine/Xvfb 실행은 S1/F2-R2 상위 재결 전
금지한다.

## lap250 middle (Claude Opus5/high) — R6-B-R13 독립 검수: PASS / 범위 승인

lap249 work의 R13을 게임 없이 독립 하네스로 재검수했다. SUT는 손대지 않았고 검수 전후
`tools/runtime_env.py` sha256 `302c246e3637959c03a32b349befa0640cff72b1f1b5f1a349ad274b88421817`,
`tests/test_runtime_env.py` sha256
`9a120a1ce1783bb605e21dc856cf64cdb4d289d5174bc9cbe328ba61735c8f8d`로 동일하다. 원본 EXE pin
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 제품 EXE/DLL/assets/
baseline/golden 변경 0, 게임/Wine/Xvfb/PNG 실행 0.

- **C0** 출하 회귀 6 passed / 131 deselected.
- **C1** 성공 시퀀스 `{read-error, 미일치 성공}^0..3 + 일치 poll` **15 케이스 전수** 불일치 0.
  반환값, 9개 coverage 필드, `attempts = poll + error` 정합, `_g1_read_coverage` 투영,
  verdict의 stage-record/`wait_observation` 두 경로를 모두 대조했다. 그중 **8 케이스**는
  `read_error_ratio > 0.25`인데도 성공 응답과 `required_inputs=True`를 유지했다.
- **C1b** timeout `{error, 미일치}^4` **16 케이스 전수** 불일치 0 — R13이 분류 경로를
  건드리지 않았음을 독립 확인했다.
- **C2** 깊이 일치 무변이 미러(M0) **137 passed**, 실제 저장소와 동일.
- **C3** 변이 4종 각 **1건만** 사살, R13 범위 밖 0건. M1 성공경로 coverage 미확정 /
  M2 성공경로를 coverage로 gate / M4 verdict 폴백 삭제 →
  `test_g1_wait_state_pass_exposes_read_coverage_without_gating_response`.
  M3 stage record 투영 삭제 → `test_g1_shared_input_sequence_blocks_production_but_reaches_later_stages`.

probe/report: `docs/history/laps/probes/20260912_lap250_r13_review_probe.py` sha256
`c226752f17c10885598f5cee8b7c067ee085e91dd9a589cf658965dc6347b3e2`,
`..._report.json` sha256 `20daf15a6c70754266dbf98aa0152b51216344a1b1f36e28aac11a75d15dcb32`.
`make check` 272 passed / `CONTEXT_PASS`, `LOOP_DRY_RUN=0 bash checks/safety.sh check` =
SAFETY_PASS. 이번 승인은 기계 1단이며 사용자 마일스톤 승인이 아니다.

신규 큐 2건(제품 영향 없음): **R22** — M1/M2/M4가 모두 같은 테스트 하나에만 걸려 R13의 세 성질이
단일 테스트에 얹혀 있다(R19와 같은 종류). **R23** — `read_coverage`를 읽는 코드가
`tools/runtime_env.py` 밖에 0개이며 `check_runtime_evidence.py`/`compare_g1_stage_b.py`는 아직
이 필드를 보지 않는다. 즉 R13은 증거를 **적는** 단계이지 증거 게이트가 **읽는** 단계가 아니다.

**다음 work tier에게**: 게임 없이 **R14**(production 레코드가 읽기 실패를 UNAVAILABLE로 표기)를
구현한다. Stage B·게임/Wine/Xvfb 실행은 S1/F2-R2 상위 재결 전까지 계속 금지한다.

## lap251 — work tier R6-B-R14 production read-failure 표기

production 단계의 직접 selection reader가 실패하면 기존에는 별도
`selection_read_failure` provenance만 남고 `before/after.selection`의
`{"status":"UNAVAILABLE","count":null}`가 초기 미관측 기본값과 구별되지 않았다. 이번
수리는 읽기 실패 경로에만 nested selection의 `read_failure=true`를 추가했다. 상태는 계속
`UNAVAILABLE`, production 결과는 `BLOCKED`, production click 및 effect wait는 계속 금지되고
drag/minimap 후속 단계는 그대로 실행된다. 정상 selection read에는 표식을 추가하지 않는다.

변경 파일 / SHA: `tools/runtime_env.py`
`2819da727c11acf360c89dff8792abbb62a96f8d5a2a8b554aa9991c1e204bf3`,
`tests/test_runtime_env.py`
`adac1297571a0b62ccd7d5c606a5855d386b15e25ad423e95208df018223f1f4`; uncommitted,
`LOOP_ALLOW_COMMITS=0`. 원본 EXE pin
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 제품 EXE/DLL/assets/
baseline/golden 변경 0.

회귀: `test_g1_production_selection_snapshots_mark_direct_read_failure_unavailable`와
`test_g1_production_selection_snapshot_has_no_failure_marker_on_success`를 추가했다. targeted
production/후속 입력 4 passed. `make check` = **274 passed**, Ruff/compileall/mypy 10 files,
`CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash checks/safety.sh check` = **SAFETY_PASS**. fixture는
Python 3.13.5/.venv fake-clock + injected direct reader이며 실제 게임/Wine/Xvfb/PNG 실행은 0이다.

판정: R14 work **PASS**, 새 middle(Opus5/high) 독립 검수 전, 사용자 마일스톤 승인 없음. 제품 G1~G4,
S1/F2-R2, R6-B-R2, R15/R19~R23, WM_CLOSE은 미해결이다.

**다음 middle tier에게**: 게임 없이 R14를 독립 검수한다. direct read failure와 정상 read의 nested
selection schema를 대조하고, production BLOCKED/click 미호출/후속 stage 진행 및 기존 provenance를
확인한다. Stage B·게임/Wine/Xvfb 실행은 S1/F2-R2 상위 재결 전까지 금지한다.

## lap252 — middle tier R6-B-R14 독립 검수 **범위 승인**

lap251의 R14를 SUT 무변경으로 독립 검수했다. lap251 테스트 헬퍼를 재사용하지 않고, 선택 상태를
read 카운터가 아니라 click/drag 스텁이 전진시키는 새 하네스로 `_g1_run_input_sequence`를 구동했다.

- C0: 출하 R14 4건 = 4 passed / 135 deselected.
- C1: 9-case 행렬(무결1 + 직접 read point6 + poll2) 불일치 0. `production/before_production`
  에서만 before/after 양쪽이 `{"status":"UNAVAILABLE","count":null,"read_failure":true}`이고
  `selection_read_failure.direct_read_point="before_production"`, result `BLOCKED`,
  waited `False`, (670,490) 클릭 0회, 후속 stage/clicks/drags는 무결 run과 동일했다.
  나머지 8 case에서 표식은 전 단계 0건이고, poll 지점 읽기 실패는 wait가 흡수했다.
- C2: 깊이 일치 미러 M0 대조군 139 passed = 실제 저장소 139 passed.
- C3: 변이 5종(M1 표식 제거 / M2 무조건 표식 / M3 count=0 / M4 stage provenance 제거 /
  M5 실패 재-raise)이 각각 출하 테스트를 1~2건 죽였고 R14 범위 밖은 0건이다.

SUT 지문은 검수 전후 동일하다: `tools/runtime_env.py`
`2819da727c11acf360c89dff8792abbb62a96f8d5a2a8b554aa9991c1e204bf3`,
`tests/test_runtime_env.py`
`adac1297571a0b62ccd7d5c606a5855d386b15e25ad423e95208df018223f1f4`.
`make check` = 274 passed, `CONTEXT_PASS`, `SAFETY_PASS`, 게임/Wine/Xvfb/PNG 0회.
전체 기록: `docs/history/laps/20260912_lap252_middle_r14_review.md`.

신규 큐 **R24**: `read_failure`를 읽는 소비자가 `tools/runtime_env.py` 밖에 0개이고, record
최상위 `selection_count`는 실패/미관측 모두 `null`이라 표식을 읽지 않는 소비자에게는 여전히
구별되지 않는다. R23과 동종이며 제품 영향은 없다.

**다음 work tier에게**: 게임 없이 **R15**를 구현한다 — 직접 selection reader 실패가 stage budget
소진(타임아웃)보다 **우선** 분류되도록 고정하고, 우선순위가 뒤집히면 죽는 회귀를 추가한다.
기존 R9/R14 provenance와 production BLOCKED/후속 입력 진행은 그대로 보존해야 한다.
Stage B·게임/Wine/Xvfb 실행은 S1/F2-R2 상위 재결 전까지 금지한다.

## lap254 — middle tier R6-B-R15 독립 검수 **FAIL(커버리지)** / 구현은 검증됨

lap253의 R15를 SUT 무변경으로 독립 검수했다. lap253 테스트 헬퍼를 재사용하지 않고
`_g1_read_selection_stage`를 직접 구동하는 fake-clock 행렬과, 계약만 보고 여기서 새로 쓴 기대
모델로 대조했다.

- C0: 출하 직접-reader 케이스 12 passed / 128 deselected.
- C1: 독립 행렬 74 case(stage 6종 × 종료시각 2.5/9.999/10.0/12.5s × 예외 OSError/ValueError/
  struct.error + 성공 대조 N0 + 미포획 예외 대조 N1) **불일치 0**. 실패 72건 전부
  `UNKNOWN_STATE_READ_FAILURE`이고 timing/budget/provenance 필드가 모두 모델과 일치했다.
- C1b: 같은 소진 조건에서 `_wait_state`는 실제로 `UNKNOWN_BUDGET_EXHAUSTED`를 답한다. 비대칭은
  실재하므로 R15의 우선순위 주장은 공허하지 않다.
- C2: 깊이 일치 미러 M0 대조군 140 passed = 실제 저장소 140 passed.
- C3: **변이 M4 생존**. `stage_budget_exhausted`를 무조건 `True`로 고정해도 미러 전체가 140
  passed다. M1(우선순위 반전)/M2(timing 필드 제거)/M3(`run_budget_exhausted` false 고정)/
  M5(예외 timing 0)는 각각 R15 테스트 1건만 사살하고 범위 밖 0건이었다.

따라서 **구현은 정확하되(74-case 실측) R15는 범위 승인하지 않는다**. 네 필드 중
`stage_budget_exhausted`만 회귀가 없다. 출하 assertion은 `tests/test_runtime_env.py:1412`
한 줄이고 그 fixture의 기대값이 True라, 상수 True 구현과 구별되지 않는다.

SUT 지문은 검수 전후 동일하다: `tools/runtime_env.py`
`0e3bf38220e8b762b2ba3b38d2151cfb51a6e8d4a6b85fd03fba6c41b89cb83c`,
`tests/test_runtime_env.py`
`d7778430c156f0c4493891e0cd8adc2d21166602c594f5537dee2a84359606e3`.
`make check` = 275 passed, `CONTEXT_PASS`, `SAFETY_PASS`, 게임/Wine/Xvfb/PNG 0회.
전체 기록: `docs/history/laps/20260912_lap254_middle_r15_review.md`.

신규 큐 **R25**(`stage_budget_exhausted` 음성 회귀 부재 — M4 생존), **R26**(
`stage_budget_exhausted=false`가 "예산 내부"/"budget 없음"/"`stage_started` 미상"을 구별하지
못함; `stage_budget`·`stage_started_elapsed` null 여부를 함께 읽어야 한다 — R23/R24 동종).

**다음 work tier에게**: 게임 없이 **R25**를 수리한다 — `stage_budget_exhausted`에 음성/경계
회귀를 추가해 상수 True와 상수 False가 **둘 다** 죽게 한다: 예산 내부 false, 경계
`finished == stage_started + stage_budget` true, `stage_started=None` false, production처럼
`stage_budget=None` false. SUT 로직은 관측상 정확하므로 변경할 이유가 없다. 변경이 필요하다고
판단되면 근거를 남기고 middle로 되돌린다. Stage B·게임/Wine/Xvfb 실행은 S1/F2-R2 상위 재결
전까지 금지한다.

## lap256 middle (Claude Opus5/high) — R25 독립 검수와 R15 범위 재결

lap255(R25)는 `tools/runtime_env.py`를 건드리지 않고 `tests/test_runtime_env.py`에 4-case
parameterized 회귀만 추가했다. 본 세션은 lap254 probe를 재사용하지 않고 새 probe
`docs/history/laps/probes/20260912_lap256_r25_review_probe.py`로 재구성해 측정했다
(리포트 `..._r25_review_report.json`, exit 0).

- C0: R25 + R15 + direct-reader 인접 테스트 `16 passed, 128 deselected`.
- C1: 계약에서 독립적으로 작성한 기대 모델 대 실측 **105 case 불일치 0**
  (stage 5종 × `stage_started` {None, 100.0, 104.25} × finish offset {0, 5, 9.999, 10.0,
  10.001, 25, 40}; `stage_budget`/`stage_started_elapsed`/`finished_elapsed`/
  `remaining_budget_after`/`stage_budget_exhausted`/`run_budget_exhausted`/classification).
  비-0 stage start(104.25)에서도 경계는 `stage_started + stage_budget`에 붙는다.
- C2: 깊이 일치 미러 M0 `144 passed` = 실제 저장소 해당 파일 결과.
- C3: 변이 9종 **생존 0, 범위 밖 사살 0**. lap254 생존자 **M4(상수 True)는 3건 사살**
  (inside 9.999 / `stage_started=None` / production). 신규 M6(상수 False)·M7(`>=`→`>`)는
  경계 case만, M8(미상 start→run start)은 미상 case만, M9(budget None→0)는 production
  case만 사살한다. 즉 네 case가 각각 개별 하중을 받는다. M1/M2/M3/M5는 여전히 R15 테스트를
  사살하므로 R15의 네 필드 + 우선순위가 전부 회귀로 덮인다.

따라서 **R25 PASS, R15 범위 승인(기계 1단)**. 제품 G1 증거도 사용자 마일스톤 승인도 아니다.
`make check` 279 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, `SAFETY_PASS`,
게임/Wine/Xvfb/PNG 0회. 검수 전후 지문 동일: `tools/runtime_env.py`
`0e3bf38220e8b762b2ba3b38d2151cfb51a6e8d4a6b85fd03fba6c41b89cb83c`, `tests/test_runtime_env.py`
`40c91b76e59c9f23b7256a0cb7b591deb028d78c9bf8d67793566a44d292a7df`.

R26 근거는 본 lap의 truth table로 재확인했다: `stage_budget_exhausted=false`가
(i) 예산 내부(stage_started=100.0, offset 9.999), (ii) `stage_started` 미상(offset 10.001),
(iii) stage budget 없음(`production`, offset 10.001) 세 상태에서 동일하다.

**다음 work tier에게**: 게임 없이 **R26**을 수리한다 — 위 세 상태를 소비자가 단일 필드로
구별할 수 있게 provenance를 명시하고(예: `stage_budget_state` 3-값 필드, 또는 `stage_budget`·
`stage_started_elapsed` null 조합을 읽는 계약을 문서화), 상수 고정·상태 축약 변이가 모두 죽는
회귀를 함께 넣는다. SUT 변경이 필요하면 근거를 남기고 middle로 되돌린다. Stage B·게임/Wine/
Xvfb 실행은 S1/F2-R2 상위 재결 전까지 금지한다.

## lap257 work (Codex hands-on) — R26 구현, middle 검수 대기

`tools/runtime_env.py:_g1_read_selection_stage`의 직접 reader failure observation에
`stage_budget_state`를 추가했다. 기존 `stage_budget_exhausted` boolean과
`stage_budget`/`stage_started_elapsed`/timing 필드는 보존한다. 상태 값은
`WITHIN_STAGE_BUDGET`, `STAGE_BUDGET_EXHAUSTED`, `STAGE_START_UNKNOWN`,
`STAGE_BUDGET_UNAVAILABLE`이며, 예산 내부·정확한 경계·시작시각 미상·budget 없음의 의미를
각각 명시한다. 4-case parameterized regression은 네 상태를 모두 직접 검증한다.

- targeted direct-reader/R15 = 5 passed / 139 deselected.
- 깊이 일치 임시 mirror M0 = 5 passed.
- `stage_budget_state` 상수 고정 변이 = 3 failed; `STAGE_BUDGET_UNAVAILABLE`를
  `STAGE_START_UNKNOWN`으로 축약한 변이 = 3 failed.
- `make check` = 279 passed; Ruff/compileall/mypy 10 source files; `CONTEXT_PASS`.
- safety = `SAFETY_PASS`; 게임/Wine/Xvfb/PNG 0회; 원본 EXE pin 및 보호 자산 불변.

판정은 **R26 work PASS, machine stage-1 only**이며 middle의 새 세션 독립 검수 전이다.
다음은 R26 범위 승인/재반려이고, 승인 뒤 offline 큐는 R19다. S1/F2-R2 재결 전 Stage B와
게임 실행은 계속 금지한다.

## lap258 middle (Claude Opus5/high) — R26 범위 승인 **FAIL(커버리지)**

독립 재측정(probe `docs/history/laps/probes/20260912_lap258_r26_review_probe.py`, exit 0,
리포트 `..._report.json`)이며 lap257 결론의 재실행이 아니다.

- C0 = 14 passed / 130 deselected (R26 + R15 + 직접 reader 인접).
- C1 = 계약에서 독립 작성한 기대 모델 대비 160-case 불일치 0. 네 상태 모두 관측.
- C2 = 깊이 일치 미러 M0 144 passed = 실저장소 144 passed.
- C3 = 변이 8종 중 **M5 생존**, 범위 밖 사살 0건. M1/M2(상태 상수 고정), M3/M4/M8(상태 축약),
  M6(`>=`→`>`), M7(boolean 상수)은 모두 R26 4-case 회귀가 사살한다.
- `make check` 279 passed, Ruff/compileall/mypy 10 source files, `CONTEXT_PASS`, `SAFETY_PASS`.
  게임/Wine/Xvfb/PNG 0회. SUT 지문은 검수 전후 lap257 기록값과 동일.

**결함(제품 동작 아님, 증거 강도):** `stage_budget`과 `stage_started`가 **둘 다 없는** 조합의
우선순위가 계약으로도 회귀로도 고정돼 있지 않다. 그런데 그 조합이 바로 production에서 실제로
발생하는 유일한 형태다 — `tools/runtime_env.py:2636`의 production stage 호출은 `stage_started`를
넘기지 않고, `production`은 `G1_INPUT_STAGE_BUDGETS`에 없다. 실측으로 현재 출력은
`STAGE_BUDGET_UNAVAILABLE`이고, `stage_started is None`을 먼저 검사하도록 순서만 바꾸면
`STAGE_START_UNKNOWN`으로 바뀌는데 144개 테스트가 전부 통과한다. R26의 production case 회귀는
실제로는 발생하지 않는 `stage_started=0.0`을 고정하고 있다.

**다음 work tier에게 — R27 (게임 없이):**
1. production 호출과 같은 `(stage=budget 없음, stage_started=None)` 조합을 회귀로 고정해
   `STAGE_BUDGET_UNAVAILABLE`을 pin하고 우선순위 역전 변이가 죽게 한다.
2. `UNAVAILABLE`이 `START_UNKNOWN`보다 우선한다는 계약을 코드 주석/문서에 명시한다.
3. SUT 로직 변경이 필요하다고 판단하면 근거를 남기고 middle로 되돌린다. R26의 나머지 네 상태
   회귀와 R25/R15 회귀는 유효하므로 삭제하거나 약화하지 않는다.

승인 뒤 offline 큐는 R19다. `stage_budget_state`/`stage_budget_exhausted` 소비자는 여전히
`tools/runtime_env.py` 밖 0개이고, 이는 R23/R24와 같은 계열의 미해결 항목이다.
Stage B·게임/Wine/Xvfb는 S1/F2-R2 상위 재결 전까지 계속 금지한다.

## lap258 work tier (Codex hands-on) — R27 production shape 회귀

lap258 middle의 R26 범위 승인 FAIL 원인은 production 호출의 실제 shape가 회귀에 없었던
증거 강도 결손이었다. `tools/runtime_env.py:2636`은 production 직접 reader 호출에서
`stage_started`를 넘기지 않고, production은 `G1_INPUT_STAGE_BUDGETS`에 없으므로
`(stage_budget=None, stage_started=None)`이 된다. 이 shape의 직접 reader `OSError`를 실제
`_g1_run_input_sequence` fixture로 구동하는 assertion을 `tests/test_runtime_env.py`에 추가해
`stage_budget_state == "STAGE_BUDGET_UNAVAILABLE"`, `stage_budget is None`,
`stage_started_elapsed is None`을 고정했다. `_g1_read_selection_stage`에는 budget 없음이
unknown start보다 우선한다는 이유를 주석으로 명시했다. SUT 로직과 기존 R26/R25/R15 회귀는
변경하지 않았다.

- targeted R27/R26/R15 = **6 passed / 138 deselected**.
- `make check` = **279 passed**, Ruff/compileall/mypy 10 source files, `CONTEXT_PASS`;
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` = **SAFETY_PASS**.
- 현재 SHA: `tools/runtime_env.py`
  `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`,
  `tests/test_runtime_env.py`
  `eaa50b919e42dd051044d4551cb2df923dd455035214200e741745e9bc15eae3`.
  원본 EXE pin `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 및 보호 자산은
  불변, uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 실제 게임/Wine/Xvfb/PNG 0회. 제품 G1 증거와 사용자 마일스톤 승인은 없다.

### 다음 middle tier 검수 요구

1. 새 production shape assertion이 `stage_started is None`을 먼저 검사하는 우선순위 역전 변이를
   사살하는지 독립 probe/mirror로 확인한다.
2. R26의 네 상태 회귀와 R25/R15 회귀를 삭제·약화하지 않았는지 확인하고, M0 대조군과 전체 Fast를
   새 세션에서 재측정한다.
3. R27 범위 승인 뒤에만 offline 큐 R19로 이동한다. S1/F2-R2 상위 재결 전 Stage B·게임/Wine/
   Xvfb는 계속 금지한다.

## lap260 middle — R27 독립 검수 PASS (기계 1단), 다음은 R19

lap258 work의 R27을 새 probe(`docs/history/laps/probes/20260912_lap260_r27_review_probe.py`,
리포트 `..._report.json`, exit 0)로 독립 재측정했다. lap258 결론을 재실행하지 않았다.

- C0 `14 passed / 130 deselected`.
- C1 독립 행렬 160-case 불일치 0, 네 상태 모두 관측. production 기본 호출(= `stage_started`
  생략)의 실측 shape는 `stage_budget=None`, `stage_started_elapsed=None`,
  `stage_budget_state="STAGE_BUDGET_UNAVAILABLE"`이고, 호출부는 여전히 `stage_started`를 넘기지
  않으며 `G1_INPUT_STAGE_BUDGETS`에 production 항목이 없다.
- C2 depth-matched mirror M0 `144 passed` = 실저장소 `144 passed`.
- C3 변이 12종 중 적용 가능한 11종 **전부 사살 / 생존 0 / 범위 밖 사살 0**. lap258 생존자
  **M5(우선순위 역전)의 유일한 사살자가 R27 회귀**다. M12(production budget 10.0)는 31.5초
  상한 가드가 import에서 거부하는 비가용 변이여서 상한 내 등가 M12b(`"production": 1.5`)로
  `3 failed / 141 passed` 사살을 확인했다.
- C4 하중 확인: R27 회귀만 제거하면 M5/M6/M10/M11이 되살아나고, M1~M4·M7~M9는 R27 없이도 R26
  회귀가 계속 사살한다 → R26/R25/R15 커버리지는 약화되지 않았다.
- `make check` `279 passed`, Ruff/compileall/mypy 10 source files, `CONTEXT_PASS`,
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` = `SAFETY_PASS`.
- 검수 전후 SHA 동일: `tools/runtime_env.py`
  `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`,
  `tests/test_runtime_env.py`
  `eaa50b919e42dd051044d4551cb2df923dd455035214200e741745e9bc15eae3`.
  원본 EXE pin `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`와 보호 자산
  불변, uncommitted, `LOOP_ALLOW_COMMITS=0`. 실제 게임/Wine/Xvfb/PNG 0회.

제품 G1 증거와 사용자 마일스톤 승인은 여전히 없다.

### 다음 work tier 요구 — R19

1. R17 회귀가 함수명 `drive_wait` 하나에만 걸려 있다(lap244). 식별자가 아니라 동작에 회귀를
   고정해 helper 개명이 조기-거부 커버리지를 조용히 지우지 못하게 한다.
2. R25/R27처럼 변이를 사살하는 회귀와 M0 대조군 근거를 남긴다.
3. 기존 R27/R26/R25/R15 회귀를 삭제·약화하지 않는다. SUT 로직 변경이 필요하다고 판단되면
   근거를 기록하고 middle로 되돌린다.

R23/R24 참고: `stage_budget_state`도 `tools/runtime_env.py` 밖 소비자가 0개다. R27 범위 밖이며
반려 사유가 아니고, `read_coverage`/`read_failure`와 같은 계열로 큐에 남긴다.

## lap262 middle 독립 검수 — R19 **범위 반려 FAIL(커버리지)**, 기계 1단

독립 probe `docs/history/laps/probes/20260912_lap262_r19_review_probe.py`(report
`..._lap262_r19_review_report.json`, exit 0)로 lap261 결론을 재실행하지 않고 재측정했다.

- C0 실저장소 targeted `8 passed`. C2 depth-matched 미러 M0 `8 passed` = 실저장소 `8 passed`.
- C1 계약 독립 재유도(테스트 helper 미import): preflight `__name__` If end_lineno **130**,
  review-body 줄 집합 **137~426의 262줄**(비공허, `drive_wait` def 326과 report write 426 포함).
  탐지기 생존 대조 = 성공 경로가 262줄 중 **205줄 실행**. 거부 경로 = rc 2, 본문 **0줄**, 파일 보존.
- C3 변이 6종(범위 = R17 회귀 1건): M1 개명만 → `8 passed` **생존(정답, 오탐 0)**;
  M2 조기 `exists()` 거부만 무력화 → **R17 단독 사살**; M3 = M2+개명 → **R17 단독 사살**;
  M4 조기 거부 블록 삭제 → 사살(범위 밖 4); M5 조기 거부 exit 0 → 사살(범위 밖 5);
  **M6 = M2 + 최초 top-level `__name__` If를 본문 아래로 이동 → `8 passed` 생존**.
- C4 하중: R17만 삭제하면 M2/M3 부활(각 `7 passed`), M4/M5는 R10/R7이 계속 사살
  → 기존 R7/R10/R11 커버리지 약화 없음.

**R19가 달성한 것(되돌리지 말 것):** M3가 결정적이다. `drive_wait`를 개명해도 늦은-거부 결함을
R17이 단독 사살한다. lap244 이름 앵커로는 빠져나갔을 변이다. M1은 오탐 없이 생존한다.

**반려 사유:** 앵커가 함수명에서 AST 위치로 옮겨졌을 뿐 무효화 가드가 없다.
`_review_body_lines()`는 **최초** top-level `__name__` If를 경계로 삼아 그 뒤 줄만 반환하므로,
그 If가 본문 아래로 내려가면 집합이 빈 집합이 되고 `assert not (... & seen)`가 공허하게 참이 된다.
실측: 미러 baseline 거부 경로는 본문 **0/262줄**, **M6는 본문 196/262줄을 실행한 뒤** 거부하는데
shipped helper는 M6에서 **0줄**을 반환하고 스위트는 `8 passed`. lap254 M4·lap258 M5와 같은 계열.

- `make check` `279 passed`, Ruff/compileall/mypy 10 source files, `CONTEXT_PASS`, `SAFETY_PASS`.
- 검수 전후 SHA 동일: `tests/test_review_probe_output.py`
  `f5a0384eb31c637bd6c92c0142328fcd046b9a39eec3958d3eb9b846ab82c8f0`(lap261 기록값 일치),
  SUT probe `20260912_lap228_r6b_r3_review_probe.py`
  `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`,
  `tools/runtime_env.py` `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`.
  원본 EXE pin `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`와 보호 자산
  불변, uncommitted, `LOOP_ALLOW_COMMITS=0`. 게임/Wine/Xvfb/PNG 0회.

### 다음 work tier 요구 — R28

1. 파생 review-body 줄 집합을 구조적으로 비공허하게 만든다. 비어 있지 않음을 단언하고,
   독립적으로 아는 late anchor(예: report write 문 또는 마지막 top-level 문)를 집합에 고정해
   구조 재배치가 조용히 통과하지 못하게 한다.
2. **M6는 죽고 M1은 계속 생존**하며 **M2/M3는 여전히 R17 단독 사살**이 되도록 출하하고
   M0 대조군을 기록한다.
3. 기존 R7/R10/R11/R27/R26/R25/R15 회귀를 삭제·약화하지 않는다. SUT probe 변경이 필요하다고
   판단되면 근거를 기록하고 middle로 되돌린다. 이후 큐는 R20 → R21 → … → F6-R2.

변이 하네스 주의(round1 오염, `..._probe_round1.py`/`..._report_round1.json`로 보존):
`if path.exists():`를 **삭제**하면 탐색 불가 부모(0o600)의 OSError 분류까지 바뀌어 R10 테스트가
같이 죽고 사살 귀속이 오염된다. `if path.exists() and False:`로 호출과 분류를 보존하라.

## lap263 work — R28 구현, middle 독립 검수 대기

`tests/test_review_probe_output.py`의 `_review_body_lines()`에 두 개의 구조 guard를 추가했다.
파생 집합이 비공허해야 하고, AST에서 독립 식별한 `json.dump` report-write statement가 그
집합 안에 있어야 한다. SUT probe와 원본/보호 자산은 변경하지 않았다.

- targeted/M0 `8 passed`; fresh `/tmp` mirror mutation 결과: M1 rename-only `8 passed` 생존,
  M2/M3 late-refusal 각 `1 failed / 7 passed`(R17 단독 사살), M6 relocated-preflight
  `1 failed / 7 passed`(R28 guard 사살).
- R17만 제거한 C4에서 M2/M3/M6는 각 `7 passed`로 복귀했다. `make check` `279 passed`,
  Ruff/compileall/mypy/`CONTEXT_PASS`, 별도 safety `SAFETY_PASS`; 게임/Wine/Xvfb/PNG 0회.
- work 결과는 기계 1단 PASS일 뿐 제품 G1 증거나 사용자 승인 아님. 다음 middle 세션은 M0,
  변이 귀속과 R7/R10/R11/R15/R25/R26/R27 비약화를 독립 검수한다. 승인 뒤 다음 큐는 R20이다.

## lap264 middle — R28 **반려(커버리지)**, work tier로 R29 이관

R28은 lap262가 지목한 M6 한 건을 실제로 닫았다(C4에서 R28만 제거하면 M6 부활 → 사살 귀속 확인).
그러나 anchor가 여전히 **전처리 If의 위치**에서 유도되므로, 전처리 블록을 본문 **아래**가 아니라
본문 **안쪽 · report write `try:` 바로 위**로 옮기면 결함이 그대로 통과한다.

- 신규 변이 **M7**: `if __name__ == "__main__": … else: …` 블록(123~130줄) 전체를 410줄
  `try:` 바로 위로 이동. `output_refusal` 자체는 무변경이며 결함은 **위치만으로** 생긴다.
- 실측(변이 줄번호를 baseline으로 역매핑한 직접 트레이스): 거부 run은 rc 2·거부 메시지·증거
  보존이지만 baseline review body 262줄 중 **198줄이 거부 전에 실행**된다. 그런데 shipped
  `_review_body_lines()`는 **17줄**(비공허)을 돌려주고 그 안에 412줄 `json.dump` anchor가
  포함되므로 R28의 두 단언이 모두 통과하고 `not (body & seen)`이 공허하게 참이 된다 →
  **8 passed 생존**. (대조: M6은 helper가 0줄 → R28 비공허 단언이 사살.)
- C0 8 passed, C2 미러 M0 8 = 실저장소 8, M1 개명-only 의도 생존(오탐 0), M2/M3 R17 단독 사살.
  C4에서 R17만 제거하면 M2/M3/M6/M7 모두 `7 passed` → R7/R10/R11 및 R15/R25/R26/R27 약화 없음.
- `make check` 279 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, `SAFETY_PASS`;
  게임/Wine/Xvfb/PNG 0회. SUT/테스트 지문은 검수 전후 동일(lap263 기록값과 일치), 전부 uncommitted.
- 상세/증거: `docs/history/laps/20260912_lap264_middle_r28_review.md`,
  `docs/history/laps/probes/20260912_lap264_r28_review_probe.py`,
  `..._lap264_r28_review_report.json`.

### R29 (work tier — 다음 한 가지)

1. 본문 집합을 전처리 위치에 의존하지 않게 만든다. 예: review 계산의 **첫 top-level 문**
   (현재 137줄 `NEGATIVE_PATTERNS` 대입)을 AST로 독립 식별해, `body_lines`가 그 줄부터 report
   write 줄까지를 **모두 포함**해야 한다고 단언한다.
2. 또는 위치 대신 **관측**을 단언한다: 거부 run에서 실행된 줄이 전처리 구간을 넘지 않는다
   (예: `max(seen) <= preflight_end`)는 형태로 "얼마나 실행됐는가"를 직접 고정한다.
3. 출하 조건(측정으로 보일 것): **M7이 죽고**, M6도 계속 죽고, **M1 개명-only는 생존**,
   M2/M3는 여전히 **R17 단독** 사살. M0 대조군을 기록한다.
4. 기존 R7/R10/R11/R15/R25/R26/R27을 삭제·약화하지 않는다. SUT probe 자체를 고쳐야 한다는
   결론이면 근거를 기록하고 middle로 되돌린다. 이후 큐는 R20 → R21 → … → F6-R2.

## lap265 work — R29 구현, middle 독립 검수 대기

`tests/test_review_probe_output.py`의 `_review_body_lines()`가 preflight If의 위치 대신 첫 review
계산 `NEGATIVE_PATTERNS`부터 AST로 찾은 `json.dump` report write까지를 review body로 고정한다.
SUT probe와 보호 자산은 변경하지 않았다.

- targeted `8 passed`; fresh throwaway mutation matrix: M0 `8 passed`, M1 rename-only 생존,
  M2/M3/M6/M7 각 `1 failed / 7 passed`; C4에서 R17 제거 시 변이 모두 `7 passed`, R29 guard
  제거 시 각 결함 변이는 계속 사살되어 하중 귀속과 기존 회귀 보존을 확인했다.
- `make check` `279 passed`, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, safety `SAFETY_PASS`;
  게임/Wine/Xvfb/PNG 0회. 테스트 SHA `59538c0e1778b9c09ff6e83207123a89229f3001d351a873af2b194e72ec8957`,
  SUT probe SHA `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`.
- 이것은 machine stage-1 결과이며 제품 G1 증거나 사용자 승인 아님. 다음 새 middle 세션은 R29
  범위를 독립 검수하고, 승인 시 R20을 수행한다.

## lap266 middle — R29 독립 검수 FAIL, 다음 한 가지는 R30

R29는 lap264 M7을 실제로 사살했고(C4: R29 **앵커만** R28 방식으로 되돌리면 M7 `8 passed`로 부활)
오탐·회귀도 없다. 되돌릴 필요는 없다. 다만 신규 **M8**이 `8 passed`로 생존해 R17 커버리지 계약이
아직 건전하지 않으므로 **범위 승인은 보류한다**.

- **M8** = M7(전처리 블록을 report write 바로 위로 이동) ∘ 무해 refactor(`NEGATIVE_PATTERNS`를
  `NEG_PATTERNS_SRC`로 개명 + report write 직전에 별칭 `NEGATIVE_PATTERNS = NEG_PATTERNS_SRC`).
  거부 run은 rc 2·메시지·증거 보존이지만 module-level review 문 **171/231줄**이 거부 전에
  실행된다(baseline 거부는 15줄). 출하 helper body는 **5줄**로 줄고 그중 **0줄**만 실행되어
  `assert not (body & seen)`이 다시 공허하다. 개명 단독은 M1이 무해로 확정한 계열이다.
- 부수 발견: `assert review_start < report_write_line`만 제거해도 M2/M3/M6/M7은 계속 사살된다.
  **그 단언 자체는 현재 행렬에서 하중 0**이고, 하중은 앵커 변경에 있다. lap265 기록의 C4는 guard만
  제거했으므로 귀속 주장이 불완전했다.
- **근본 원인(lap262/264/266 공통)**: 본문을 **이동 가능한 두 앵커 사이의 줄 구간**으로 유도하고
  시작 앵커를 `next()`로 **첫 일치**만 잡는다. decoy가 그 첫 일치를 가로챌 수 있다.

### R30 (work tier — 다음 한 가지). lap266이 미러에서 선측정했으므로 추측하지 않는다

1. **기각된 변이 A**: "import/def/class/docstring/전처리 If를 뺀 모든 top-level 문". **M0 대조군이
   `1 failed`** — 전처리보다 먼저 실행되는 모듈 설정문 14개(15줄: ROOT/SOURCE/COUNT_ADDR/
   DEFAULT_OUTPUT …)를 포함하는 오탐이다. 이 형태를 다시 시도하지 말 것.
2. **채택할 변이 B**: `body` = **named review result 대입의 합집합** + **모든** `json.dump` 줄.
   이름 집합은 `NEGATIVE_PATTERNS, both_negative, synthetic, grid_total, surgicality, waits, report`.
   `next()`(첫 일치) 대신 **모든 일치의 합집합**을 쓰고, 이름 전부를 찾았는지 단언한다.
   합집합은 단조라 전처리 이동으로 줄지 않고 decoy 대입은 줄을 더할 뿐이다.
3. **출하 조건(측정으로 보일 것)**: M0 `8 passed`, M1 개명-only 생존, **M2/M3/M6/M7/M8 전부 사살**,
   생존자 `[M1]`, R17 단독 하중 유지(R17 제거 시 전부 생존), `make check` `279 passed`.
   lap266 미러 실측이 이미 이 값을 보여준다 — 재현되지 않으면 근거를 기록하고 middle로 되돌린다.
4. SUT probe와 보호 자산은 변경하지 않는다. 기존 R7/R10/R11/R15/R25/R26/R27을 삭제·약화하지
   않는다. 이후 큐는 R20 → R21 → R22 → R23 → R24 → F2-R1 → F3-R1 → F3-R2 → F6-R2.
- 상세/증거: `docs/history/laps/20260912_lap266_middle_r29_review.md`,
  `docs/history/laps/probes/20260912_lap266_r29_review_probe.py` (+ `_report.json`),
  `..._lap266_r30_feasibility_probe.py`, `..._lap266_r30b_feasibility_probe.py` (+ 각 `_report.json`).

## lap267 Astra — 실패 보존 및 우선순위 재결

최신 상위 계약: `docs/history/laps/20260912_lap267_astra_priority_handoff.md`.
이전 자동 offline 큐 소진 지시는 이 계약으로 대체한다. 현재 다음 한 가지는 STATUS만 따른다.
R29 반려와 S1/F2-R2/R6-B-R2 미결은 유지한다. middle의 범위 확정과 work 구현/새 세션 검수를
분리한다. Stage B 실행·제품 마감 승인 없음.

## lap268 middle — R30(변이 B) **범위 승인**. work tier 실행 계약

근거: `docs/history/laps/20260912_lap268_middle_r30_scope.md`,
probe `docs/history/laps/probes/20260912_lap268_r30_scope_probe.py` (+ `_report.json`).
middle이 lap266 R30B 행렬을 폐기 미러에서 **독립 재현**했고(생존자 `[M1]` 동일), lap266이
남기지 못했던 **사살 귀속**을 추가 측정해 M2/M3/M6/M7/M8 사살이 모두 R17 커버리지 단언
(`assert not (_review_body_lines() & seen)`)에 의한 것임을 확인했다. 완전성 self-check가
대신 죽인 것이 아니다. 따라서 **수리 범위와 종료 기준을 승인한다. 구현은 work tier가 한다.**

1. 허용 파일은 `tests/test_review_probe_output.py` **하나뿐**이다. SUT probe
   (`…lap228_r6b_r3_review_probe.py`), 보호 자산, 다른 테스트를 바꾸지 않는다.
   작업 전후로 SUT/`tools/runtime_env.py` SHA256이 불변임을 기록한다.
2. 구현 형태는 lap266이 선측정한 **변이 B**다: `_review_body_lines()`가 named review result
   대입의 **합집합**(`NEGATIVE_PATTERNS, both_negative, synthetic, grid_total, surgicality,
   waits, report`) + **모든** `json.dump` 줄을 반환하고, 이름을 전부 찾았는지 단언한다.
   `next()`(첫 일치) 형태로 되돌리지 않는다. **변이 A(top-level 문 차집합)는 M0 대조군이
   `1 failed`인 오탐으로 기각 확정이니 다시 시도하지 않는다.**
3. 이름 튜플은 SHA로 고정된 SUT에 의도적으로 결합돼 있다. 이 결합과 그 이유를 테스트 주석에
   남긴다. 이름 **부분집합만** 확인하는 완화형은 공허성을 되살리므로 금지한다.
4. 출하 조건(측정으로 보일 것, 카운트만으로 마감 금지):
   - M0 대조군 `8 passed`, 생존자 **정확히 `[M1]`**(개명-only는 무해로 생존),
     M2/M3/M6/M7/M8 각 `1 failed / 7 passed`.
   - 각 사살의 **이유를 함께 기록**한다. 실패 텍스트가 R17 커버리지 단언을 가리켜야 한다.
   - M9(review result 개명, 결함 없음)과 M10(M9 ∘ late refusal)은 `missing review results`로
     실패하는 것이 **정상 fail-closed**다. 이 오탐 비용을 기록에 명시한다.
   - R17 테스트 제거 시 전 변이 생존(단독 하중 유지). helper 소비자는 `:227` 1개뿐이다.
   - `make check` `279 passed`, Ruff/compileall/mypy/`CONTEXT_PASS`/`SAFETY_PASS`.
5. 중단 조건 — **재시도하지 말고 변경을 보존한 뒤 `loop/ESCALATE_SOL`로 종료한다**: 위 수치가
   재현되지 않음 / 사살자가 완전성 단언으로 바뀜 / SUT probe를 고쳐야 한다는 결론 /
   기존 R7/R10/R11/R15/R25/R26/R27이 삭제·약화됨.
6. 예산은 1바퀴, 게임·Wine·Xvfb·PNG 0회, 커밋 0. 결과는 **다음 새 middle 세션이 독립 검수**한다.
   승인 뒤에도 offline 큐(R20~R24/F2-R1/F3-R1/F3-R2/F6-R2)를 자동 소진하지 않는다.
   다음 middle의 한 가지는 Astra 항목3(Stage B producer/comparator 호출 경로로 선행조건 분류)과
   항목4(S1 결정성 조사 계약 1장)다. R29 반려와 R6-B-R2/S1/F2-R2 미결은 그대로 보존한다.

## lap271 — middle tier: offline 큐 분류 완료(Astra 항목3) + F3-R2를 유일 선행조건으로 지정

작성: Claude Code `claude-opus-5`/high, middle tier. 구현하지 않았고 게임을 실행하지 않았다.
근거: `docs/history/laps/20260912_lap271_middle_offline_queue_classification.md`,
probe/report `docs/history/laps/probes/20260912_lap271_offline_queue_classification_{probe.py,report.json}`
(`618d23dd…` / `f1d7dc6b…`).

### 분류 결과 (6축 독립 측정)

offline 큐 9건 중 **Stage B 선행조건은 F3-R2 하나뿐**이다.

- **P — F3-R2**: 후보 카메라가 **실제로 움직이지 않은** 상태에서 producer가 실제로 flush 하는
  `"FAIL"`(`tools/runtime_env.py:2844`)을 넣으면 stage `UNKNOWN_DISPUTED_ORACLE` / overall
  `INCONCLUSIVE`다. `"BLOCKED"`/`"SKIP"`과 timeout 5종, 선택 축 하드 `FAIL`도 같다. 대조군만
  overall `PASS`이고 `new_pass_paths: []`. 즉 **PASS 세탁이 아니라 카드가 FAIL을 말할 능력의 상실**.
- **H — F2-R1 / F3-R1 / F6-R2**(경로 위, 현재 도달 불가): `_stage_report` 호출 1건(`:357`,
  위치 인자 5), 외부 참조 0 / `"last":` 기록 1곳(`runtime_env.py:2551`, `record_timeout`,
  result=`exc.classification`) / flush 배선은 두 producer 모두 정상이고 유실 시 `INCONCLUSIVE`.
- **C — R23 / R24**(게이트 소비자 0): `read_coverage`·`read_failure`·`stage_budget_state` 모두
  두 게이트 도구에서 0건. comparator의 `selection_count`는 **자기가 쓰는 키**이며 count 결측은
  fail-closed(`INCONCLUSIVE`). 최상위 null 모호성은 PASS를 만들지 못한다.
- **N — R20 / R21 / R22**(하네스·테스트 전용): producer `_write_json`은 직렬화 선행 + 원자
  replace이고 `tools/`에 `open("x")` 0건. 절단 창은 probe 규약에만 있다.

주차한 8건은 **삭제하거나 PASS로 바꾸지 않는다**(Astra 항목3 문구).

### 다음 work 한 가지 — F3-R2 수리(게임 실행 없음)

1. `tools/compare_g1_stage_b.py:326`의 `disputed = any(result != "PASS")`를 **명시 열거**로 좁힌다.
2. 열거 집합은 **lap218의 3종 리터럴이 아니라** 현재 producer가 실제로 flush 하는 classification
   집합에서 유도하고 유도 근거를 기록한다. lap271 실측: `FAIL_NO_EFFECT`,
   `UNKNOWN_BUDGET_EXHAUSTED`, `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`,
   `UNKNOWN_STATE_READ_FAILURE`, `UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`.
   **lap218 목록은 낡았다**(R12/R15/R25/R26/R27 이후 늘었고 `BLOCKED`/`SKIP`도 flush 된다).
3. 하드 `"FAIL"` → 카드 `FAIL` 복원. `"BLOCKED"`/`"SKIP"`/미지 문자열/`result` 키 누락 →
   `INCONCLUSIVE`(기본값이 PASS가 되지 않게).
4. **새 PASS 경로 0개.** 회귀는 분류별 1건 + 하드 FAIL→FAIL + 미지 문자열→INCONCLUSIVE +
   F1/F4/F5 fail-closed·scene gate·slot 강등 불변을 고정하고 **M0 대조군**을 남긴다.
5. 건드리지 않는다: F2-R1/F3-R1/F6-R2/R20~R24, SUT probe, 보호 자산, R31(계속 동결).
6. 중단 조건 — 재시도하지 말고 변경을 보존한 뒤 `loop/ESCALATE_SOL`로 종료한다: 위 수치가
   재현되지 않음 / 새 PASS 경로가 생김 / 기존 회귀가 약화됨 / comparator 밖을 고쳐야 한다는 결론.
7. 예산 1바퀴, 게임·Wine·Xvfb·PNG 0회, 커밋 0. 결과는 **다음 새 middle 세션이 독립 검수**한다.

S1은 별도다: Astra 항목4 연구 계약을
`docs/work/active/G1_S1_DETERMINISM_RESEARCH_CONTRACT.md`에 초안했고, 그 실행 예산은
상위(Astra/사용자) 재결 사항이다. S1/F2-R2 재결 전 Stage B·원본 재실행·R6-A/R6-C는 계속 금지다.
