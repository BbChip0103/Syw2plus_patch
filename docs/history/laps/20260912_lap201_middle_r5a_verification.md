# lap201 middle — R5-A 독립 검수: 구현 승인, 회귀테스트 미충족으로 Stage B 인가 보류

- 날짜: 2026-09-12 02:08~ KST
- lap: 201 (`loop/.lap_counter`=201; 루프 배너 lap=200과 1 어긋남을 그대로 기록한다)
- 역할: middle tier (진단·계획·확인). 실제 모델 Claude Code `claude-opus-5`/high.
  **구현하지 않았다. 게임을 실행하지 않았다. Stage B를 실행하지 않았다.**
- 목표: lap200 work가 남긴 R5-A 변경을 독립 검수하고, 통과하면 카드 규정대로
  Stage B 페어 run을 인가한다.

## 입력 상태 (검수 대상)

lap200 work(`logs/laps/2026-09-12/lap-0200.log`, `loop/ESCALATE_SOL` lap=200 블록)는
`make check`가 mypy 오류로 실패해 세션 계약대로 중단했다고 보고했다. 보고 자체가
"mypy 오류는 수정했으나 재시도하지 않았다"이므로, 이번 바퀴의 첫 일은 **게이트 재현**이다.

- 검수 대상 해시 (lap200 자기신고와 **일치**, 무변경 확인):
  - `tools/runtime_env.py` `d18e81ce1ba758589e8c92bfd67ee5d446abd91c499b77732fdf4afae4f5423b`
  - `tests/test_runtime_env.py` `fa975b19a250f6c8120fd095f63fb62f83dcd699672ecaaf3d5fce33d81a4546`
- 참고: `docs/`·`tools/`·`tests/`는 git 미추적이므로 diff가 없다. 검수는 **현물 코드 읽기 +
  자체 드라이버 probe**로 했고 lap200 테스트 본문은 재사용하지 않았다.

## 판정 1 — 필수 게이트는 지금 전부 PASS (lap200의 FAIL은 해소된 상태다)

| 게이트 | 결과 |
|---|---|
| `make check` | **216 passed** / Ruff PASS / compileall PASS / mypy **Success (9 files)** / `CONTEXT_PASS`, exit 0 |
| `LOOP_DRY_RUN=0 bash checks/safety.sh check` | **`SAFETY_PASS`** |

lap200이 보고한 `tools/runtime_env.py:1349: No overload variant of "int" ...`는 재현되지 않는다.
lap200이 수정 후 재실행하지 않고 중단했기 때문이며, **중단 판단 자체는 세션 계약대로 옳았다.**
따라서 lap200의 "필수 게이트 FAIL"은 결함으로 이월하지 않는다.

## 판정 2 — R5-A 구현의 실체는 계약과 일치한다 (probe 30/30 PASS)

자체 드라이버 probe: `docs/history/laps/probes/20260912_lap201_r5a_probe.py`
(sha256 `ed56fc596c6b92b2b646191fa4a94ab6d30ecb844355296975733cd99a5e0a02`),
`.venv/bin/python` 실행 → **30 assertions PASS**.

- **새 오프셋 없음.** 성공 fixture에서 실제로 읽힌 주소는
  `0x899024`(count), `0x899028`(first slot), `0x8990D6`(=`G1_UNIT_EXISTS_BASE+slot*2`),
  `0x66EB85`(=`0x0066B790 + 7*0x758 + 0x8D`) **4개뿐**이다. 상수는
  `tools/runtime_env.py:181-183`의 lap57·lap61 문서 값과 동일하다.
- **절대 type 술어 없음.** `selected_type`은 어떤 wait 술어·`_g1_input_verdict`·verdict
  계산식에도 들어가지 않는다(`grep` 결과 소비처 0). 증거 필드일 뿐이다.
- **wait 술어·예산 불변.** `count>=1` / `count>=2` 그대로, `G1_INPUT_STAGE_BUDGETS`
  `{10.0,10.0,10.0}`(합 30.0 ≤ 31.5), `G1_INPUT_PHASE_WALL_CLOCK_BUDGET` 31.5 그대로.
- **baseline·후보 대칭.** 두 주입 지점(`:3227`, `:3598`)이 동일하게
  `_read_g1_selection_evidence(read_for_process)`로 전환됐다.
- **count==0이면 개체 상세를 아예 읽지 않는다**(불필요한 읽기·오탐 방지).
- **비치명 보존.** 비활성 slot / `type==0` / 범위 밖 slot은 `_CommandCellSnapshotError`로
  잡혀 `selected_type="UNKNOWN"` + provenance가 되고 예외가 올라가지 않는다.
- **end-to-end 확인.** 실제 reader를 `_g1_run_input_sequence`에 주입한 probe에서
  네 단계(`unit_select`→`production`→`drag_select`→`minimap`)가 전부 실행되고,
  `unit_select.before`는 UNKNOWN, `unit_select.after`/`drag_select.after`는
  `selected_slot=7`/`selected_type=58`을 담는다. production은 여전히 `BLOCKED`다.
- **세탁 없음.** production BLOCKED에서 `required_inputs=False`, baseline `overall!="PASS"`,
  후보 `overall!="PASS"`.

## 판정 3 — 그러나 **승인 보류**: 결함 1건 + 카드 필수 회귀테스트 미충족

### D1 (결함, 블로킹). 읽기 실패의 한 부류가 여전히 **치명적**이다

`_read_g1_selection_evidence`(`:1345-1362`)는 `_CommandCellSnapshotError`**만** 잡는다.
그런데 실제 reader인 `patches/population/runtime_driver.read`(`:43`)는 부분/실패 읽기에서
**`OSError`**를 던진다. R5-A가 **새로 추가한** 두 읽기
(`G1_UNIT_EXISTS_BASE_ADDRESS + slot*2`, `unit_address + 0x8D`)에서 `OSError`가 나면 그대로
전파된다. 이 reader는 `unit_select`/`drag_select`의 **wait 폴링 reader로 주입**되므로,
읽기 실패 1회가 해당 단계를 중단시키고 이후 입력까지 날린다.

probe 증거(ok 13~15): type 주소 실패 → `OSError` 전파, exists 주소 실패 → `OSError` 전파,
**같은 실패에서 R5-A 이전 `_read_selection`은 정상 반환**한다(= 폭발 반경이 넓어졌다).

카드 R5-A는 "읽기가 실패하면 `UNKNOWN`+provenance로 **보존하고 run을 계속한다.
예외를 fatal로 올리지 마라 — 정상 원본 분기를 FAIL로 만든 lap190의 실수"라고 못박았다.
현재 코드는 **모델링된 실패(_CommandCellSnapshotError)에 대해서만** 그 계약을 지킨다.
발생 확률은 낮다(정상 프로세스에서 해당 주소는 매핑돼 있다). 그러나 Stage B run은
fresh/exact-once로 희소하고, 수리는 `except` 한 줄 확장이므로 **run 전에 고치는 것이 싸다.**

### D2 (미충족). 카드가 **필수**로 지정한 회귀테스트 5개 중 3개가 없다

lap200이 추가한 테스트는 `tests/test_runtime_env.py:899/911/921` 3개이며 전부 **reader 단위**다.

| 카드 필수 | 상태 |
|---|---|
| 1. 성공 fixture에서 `unit_select`/`drag_select` 양쪽, baseline·후보 양쪽 경로에 slot/type이 **디스크 evidence로** 남는다 | **없음** (reader 단위만 있음; 시퀀스/evidence 경로 미커버) |
| 2. 읽기 실패 fixture에서 UNKNOWN+provenance, run 미중단, `drag_select`/`minimap` 실제 실행 | **부분** (:911은 reader만; 시퀀스 계속 실행 단언 없음) |
| 3. slot/type 유무가 `overall`을 PASS로 바꾸지 않는다 | **간접** (기존 verdict 테스트가 덮지만 R5-A와 연결되지 않음) |
| 4. wait 술어·예산 상수 값 불변 단언(`count>=1`,`count>=2`,10/10/10,31.5) | **없음** (`stage_budget == 10.0` 한 줄뿐) |
| 5. `make check` + `safety.sh` 통과 및 수치 기록 | **이번 바퀴에 충족** (216 passed / `SAFETY_PASS`) |

이 항목들은 내 probe로 **현재 시점에는** 확인했지만, probe는 저장소 게이트가 아니다.
다음 회귀에서 자동으로 잡히지 않으므로 카드 요구를 충족한 것으로 셀 수 없다
(A-1 불변식이 "테스트가 그 경로를 덮지 않아" 회귀했던 H2 사례가 정확히 이것이다).

## 판정 4 — Stage B 페어 run 인가는 **다음 middle로 이월**

카드 lap199는 "R5-A가 승인되고 사전 게이트가 PASS면 그 middle이 곧바로 인가한다"고 적었다.
**나는 R5-A를 승인하지 않았다**(D1·D2). 따라서 인가 조건이 성립하지 않는다.
이는 새 사용자 승인을 기다리는 것이 **아니다** — APPROVALS의 "bounded repair → fresh
validation으로 계속" 범위 안의 **1회 추가 수리 바퀴**다. R5-C가 들어오고 다음 middle이
승인하면 그 자리에서 인가한다.

사전 게이트는 이번에도 재확인했다(위 판정 1). lap199가 확인한 원본 SHA 핀·
`check_setup --require-game`·디스크 여유는 이번 바퀴에 재실행하지 않았고,
**Stage B 인가 바퀴에서 run 직전에 다시 걸어야 한다**(경과 시간 때문).

## 비블로킹 관측

- `tests/test_runtime_env.py:1198`의 기존 시퀀스 테스트는 `read_selection=lambda: dict(selection)`
  이라는 합성 reader를 쓴다. 즉 **실제 주입된 reader를 통과하는 저장소 테스트가 0개**다.
  D2-1이 이 구멍을 정확히 메운다.
- R5-B(원본↔후보 비교기 `tools/compare_g1_stage_b.py`)는 여전히 미구현·비블로킹이다.
- 루프 배너 `lap=200`과 `loop/.lap_counter`=201이 어긋난다. 기록은 counter를 따랐다.

## 이번 바퀴 변경 파일

- `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`(lap201 판정 추가),
  `loop/ESCALATE_SOL`(lap201 블록 추가), 이 기록,
  `docs/history/laps/probes/20260912_lap201_r5a_probe.py`(신규, 검수 증거).
- **source/tests/EXE/DLL/assets/baseline/golden 변경 0.** 게임 run 0회. Stage B 0회. PNG 0장.
- 커밋 0회 (`LOOP_ALLOW_COMMITS=0`). 무변경 확인 해시는 위 "검수 대상 해시"와 같다.

## 다음 한 가지

**work tier — R5-C.** `_read_g1_selection_evidence`의 읽기 실패 처리를 원시 읽기 오류까지
넓히고, 카드 R5-A 필수 회귀테스트 1·2·4를 저장소 테스트로 추가한다.
허용 파일 `tools/runtime_env.py` + 해당 `tests/`. 게임 실행 금지. 계약 전문은 카드의
「lap201 middle 판정」.
