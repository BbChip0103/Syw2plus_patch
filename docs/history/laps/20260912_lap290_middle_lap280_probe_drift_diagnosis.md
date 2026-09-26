# 2026-09-12 | lap 290 | lap280 probe 실패 원인 진단과 lap289 fresh 검수 (middle, G1/S1)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier
  (진단·계획·컨펌). 외부 subagent/provider 호출 0. 게임 코드 hands-on 수정 0, 저장소 probe 수정 0.
  lap 번호는 `loop/.lap_counter`=**290**(읽기만 함). 러너 배너는 `lap=289`로 표시됐고 파일 값을 우선했다.
- 가설 / 사용자 관찰: lap289가 `loop/ESCALATE_SOL`로 넘긴 필수 검증 실패 —
  `20260912_lap280_middle_s1_crossverify_probe.py:130`의 `internal_id` 정규식 `NoneType` —
  의 원인은 **lap281이 세 유닛 오프셋을 명명 상수로 승격하면서 probe가 grep하던 16진 리터럴이
  사라진 것**이고, 측정 사실(28 layer, 21 블록, G3 `0x1B5A4`)의 드리프트가 아니다.
  사용자 신규 관찰 없음.
- 예상 PASS / FAIL 조건:
  (a) lap280 실패가 fresh run에서 같은 프레임/줄/예외로 재현된다,
  (b) `runtime_driver.py` 현재 SHA가 lap281 기록의 편집 후 SHA와 같고 lap280 기록의 SHA와 다르다,
  (c) 추출 경로만 고친 **진단 전용 사본**이 lap280 원본 보고서와 값이 일치한다
  → 원인 확정, 수리 범위 = 추출 블록으로 한정, lap289 수리 내용 ACCEPT.
  어느 하나라도 어긋나면(특히 (c)에서 새 failure가 나오면) 원인 미확정으로 보고 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/20260912_lap290_middle_lap280_probe_drift_diagnosis.md`(이 기록),
  `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.4 추가,
  `docs/STATUS.md` 갱신(압축 원문은 `20260912_status_lap290_compaction.md`),
  `loop/ESCALATE_SOL` lap290 항목 추가(lap289 원문 보존), `logs/lap290/**`(gitignore 대상).
  **저장소 probe·게임 코드·comparator·producer·tests·원본 EXE/DLL/assets·PASS 규칙 변경 0.**
  커밋 없음(`LOOP_ALLOW_COMMITS=0`, uncommitted 보존).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — 기록값과 일치.
  후보 바이너리 없음. `patches/population/runtime_driver.py`
  `ae4ff9393247ce31eab7c953b040f7d3c5aa8b0386af025046382c7d4e4291b5`(= lap281 편집 후 기록값),
  `tools/runtime_env.py` `dd2ad0439111d6b1e098d0ea771db172847dfa42f04ed085c4567f2ac8500190`(= lap281),
  `…lap280_middle_s1_crossverify_probe.py` `8b75e394…5beb3247`(= lap280 신규 기록값, 무변경),
  `…lap284_work_save_layout_probe.py` `6f2572a4…2810e9cf`(= lap289 편집 후 기록값, 무변경),
  `…lap279_middle_s1_serializer_probe.py` `58bbea79…d9b7fc31`,
  `…lap284_middle_runtime_contract_probe.py` `aa8812b4…3cbe3bf4`,
  `…lap282_middle_unit_offset_review_probe.py` `cdfa7c3c…b42ae764`.
  환경 `.venv`(→ `/home/dev_00/miniconda3/bin/python3.13`, Python 3.13.5) + objdump/sha256sum.
  **게임/Wine/Xvfb/Stage B/PNG 실행 0.** 활성 플레이어·지도·군대·runtime fixture 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시 (전부 fresh, exact-once):
  - `…lap279_middle_s1_serializer_probe.py` → exit 0, `logs/lap290/lap279_rerun.json`
    `e848c940…9db2ddd` — lap289 기록과 **바이트 동일**.
  - `…lap284_middle_runtime_contract_probe.py` → exit 0, `logs/lap290/lap284_middle_rerun.json`
    `2870383083…673d52d60` — lap284/lap289 기록과 **바이트 동일**.
  - `…lap284_work_save_layout_probe.py` → exit 0 `failures=[]`,
    `logs/lap290/lap284_work_rerun.json` `7381b5f7…5cbfb81` — lap289 편집 후 기록과 **바이트 동일**
    (layer 28, roster 375/558/147/149).
  - `…lap280_middle_s1_crossverify_probe.py` → **exit 1**, stdout 0바이트,
    `logs/lap290/lap280_rerun.stderr` `73189422…fbde7fd6`: lap289와 **같은 프레임·같은 줄 130·같은
    `AttributeError: 'NoneType' object has no attribute 'group'`**. 캐럿 밑줄 폭만 다르다(아래 위험).
  - `…lap282_middle_unit_offset_review_probe.py` → exit 0 `failures=[]`,
    `logs/lap290/lap282_rerun.json` `e0f07f3a…46f4be08` — lap282 기록과 **바이트 동일**.
  - **진단 전용 사본** `logs/lap290/diagnosis/lap280_scratch_lap290.py` `f101bc17…f0f1de52`
    (저장소 probe를 건드리지 않은 logs 밑 사본; 추출 블록만 교체 + REPO 루트 고정) → exit 0,
    `logs/lap290/lap280_scratch_rerun.json` `3d4fe30703…6a6d6a9126` =
    **lap280 원본 보고서 `logs/lap280/s1_crossverify_probe.json`과 바이트 동일**(`diff` 무차이).
  - Fast(문서 갱신 전): `make check` → **292 passed in 48.76s**, Ruff/compileall/mypy(10 files) 성공,
    `CONTEXT_PASS`, exit 0 (`logs/lap290/make_check.txt`); `safety.sh check` → `SAFETY_PASS`
    (`logs/lap290/safety.txt`).
  - Fast(문서 갱신 후 재실행): `make check` → **292 passed in 48.77s**, exit 0
    (`logs/lap290/make_check_final.txt`); `LOOP_DRY_RUN=0 bash checks/safety.sh check` →
    `SAFETY_PASS`, exit 0 (`logs/lap290/safety_final.txt`). `docs/STATUS.md`는 130줄, `CONTEXT_PASS`.
    캡처/PNG 없음.
  - 최종 문서 SHA: `docs/STATUS.md` `6d4e9b04…3a9e81f2`,
    `…lap290_middle_lap280_probe_drift_diagnosis.md`(이 파일, 본 줄 기록 전),
    `…G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` `d7fcfe83…020e376c0`,
    `…status_lap290_compaction.md` `9f057175…e63c59d8f9`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **원인 진단 CONFIRMED. lap289 수리 내용 ACCEPT. 카드 종결은 여전히 REJECT.**
  1. **원인:** lap280 probe는 `patches/population/runtime_driver.py`의 **소스 텍스트**에서
     `internal_id=i(0x…)` / `x=h(0x…)` / `y=h(0x…)` 리터럴을 정규식으로 읽는다. lap281(work)이
     그 세 값을 `tools/runtime_env.py`의 `G1_UNIT_INTERNAL_ID_OFFSET=0x29C`,
     `G1_UNIT_X_OFFSET=0x2A2`, `G1_UNIT_Y_OFFSET=0x2A4`로 승격하고 driver를
     `internal_id=i(G1_UNIT_INTERNAL_ID_OFFSET)` 형태로 바꿔 **리터럴이 사라졌다**.
     dict 평가 순서상 아직 리터럴인 `type=u[0x8D]`·`owner=u[0x8E]`는 통과하고 세 번째 항목인
     `internal_id`에서 처음 `None`이 되어 line 130에서 터진다 — traceback과 정확히 일치한다.
     driver SHA가 lap280 기록의 `8c2465b8…0be82e94`에서 lap281 기록의 `ae4ff939…4e4291b5`로
     바뀌었고 현재 파일이 후자와 같다는 점이 시점 근거다.
  2. **lap289 무관 CONFIRMED:** lap289가 바꾼 파일은 work probe 하나뿐이고 driver/runtime_env는
     lap281 이후 무변경이다. 이 probe는 **lap281 이후 8바퀴 동안 아무도 재실행하지 않아 잠복**했고
     lap289가 필수 대조를 하다가 처음 드러냈다.
  3. **측정 사실 무드리프트 CONFIRMED:** 추출 경로만 고친 사본이 lap280 원본 보고서와 바이트 동일
     (literal 21, fwrite/fread 22/22, layer 28, pair_deltas {48,64,80,96,160},
     x `0x66BA32` WORD 115회 / y `0x66BA34` WORD 115회 / internal_id `0x66BA2C` DWORD 67회,
     G3 overflow `0x1B5A4`). 즉 실패는 **하네스 결합 결함**이지 S1/저장 레이아웃 사실의 변화가 아니다.
  4. **수리 범위 확정:** lap280 probe line 126–133 한 블록. 나머지 (1)(2)(4)절과 보고서 스키마는
     그대로 통과한다. 권장 형태는 lap282 probe가 이미 쓰는 계약 —
     값은 `tools/runtime_env.py`의 `^NAME = 0x…$`에서 읽고, driver에는 `field=…(NAME)` 결합을
     단언 — 이며 `(x, y, internal_id) != (0x2A2, 0x2A4, 0x29C)` 가드는 유지한다.
  5. lap288 "다음 한 가지"의 세 항목 중 (a) SAVE_END 축소, (b) `0x4DA4A9` 단언은 lap289가 했고
     (c) 나머지 probe 출력 불변은 **이번 바퀴에 lap279/lap282/lap284-middle/lap284-work 4/4 바이트
     동일로 충족**, lap280만 위 하네스 결함으로 미충족이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **미수리 잔존:** 저장소의 lap280 probe는 여전히 exit 1이다. middle은 구현하지 않으므로
    수리는 work tier로 넘긴다(§4.4 handoff). 진단 사본은 `logs/` 밑 비권위 산물이며 PASS 근거가 아니다.
  - **provenance 관찰:** lap289 stderr와 lap290 stderr는 캐럿 밑줄 폭만 다르다(67 대 58칸).
    같은 줄·같은 예외이므로 실패 판정에는 영향이 없으나, 두 바퀴의 인터프리터 마이너 버전이
    다를 가능성을 배제하지 못한다. 원인 미확정으로 남기고 추정으로 메우지 않는다.
  - **같은 계열 위험(정량, 정적 확인만):** `docs/history/laps/probes/`의 probe는 52개이고 그 중
    42개가 구현 모듈 경로(`tools/runtime_env.py`/`runtime_driver.py`/`tools/compare_g1_stage_b.py`)를
    참조한다. `runtime_driver.py`의 **소스 텍스트**를 읽는 것은 lap280·lap282 둘뿐이며 lap282는
    이미 명명 상수 계약을 쓴다. 나머지 다수는 `runtime_env.py`의 앵커 문자열에 결합해 있으므로
    같은 드리프트 계열이 **넓다**. 이번 바퀴는 그 40개를 **실행 대조하지 않았다**(과거 보고서
    덮어쓰기 위험 때문에 재실행을 열지 않음). 구현 상수/앵커를 승격할 때 과거 probe 재실행이
    없으면 같은 잠복 결함이 재발한다(프로세스 사각).
  - 기존 blocker 전부 유지: S1/F2-R2 실제 결정성, Stage B 0, runtime 예산 0, WM_CLOSE 결함,
    G3 저장 포맷 `0x1B5A4` 초과, tick 순환 의존, W2 매직 리터럴 드리프트,
    정사각·짝수 fixture 한계, `+0x8E` owner 미재유도, 제품 G1~G4 증거 0.
  - 이 판정은 **offline static probe의 하네스 정합성**에 한정한다. 사용자 마일스톤 승인 없음.
- 다음 한 가지: work tier(Luna/Sonnet5)가 `…lap280_middle_s1_crossverify_probe.py` line 126–133을
  §4.4 사양대로 고쳐 exit 0 `failures=[]`와 보고서 `3d4fe307…6a6d6a9126` 재현을 보이고,
  같은 run에서 lap279/lap282/lap284-middle/lap284-work 출력 불변을 재확인한다.
  게임 실행·Stage B·runtime 예산·PASS 규칙 변경은 계속 금지.

---

## 부록 — lap289 `loop/ESCALATE_SOL` 원문 보존 (lap290이 해소 후 파일을 비움)

- 보존 시점: 2026-09-12, lap 290.
- 원문 SHA256: `c9eb2d3968205448ea63ff3f8463390da3e913182c301ae61a074028e05c7b85`, 줄 수: 1285.
- 해소 근거: 승격 요청 1번(원인 진단)은 위 §측정값에서 CONFIRMED, 2번(fresh 대조)은 lap279/lap282/
  lap284-middle/lap284-work 4종 바이트 동일로 수행했다. 남은 것은 work tier 구현이므로 통상 인계이며
  승격 표식을 유지하지 않는다.

```text
lap=289
role=work (hands-on implementation/verification; configured route Codex gpt-5.6-luna/high)
status=ESCALATED: 필수 fresh cross-probe 대조 중 lap280이 예상 밖 traceback/exit1. 현재 work
정정과 성공한 증거는 보존했으며, 실패한 검증은 재시도하지 않고 다음 승격 작업자에게 넘긴다.
target=G1 S1 저장 serializer offline 경계 정정1, 제품 G1/runtime/Stage B 아님
record=docs/history/laps/20260912_lap289_work_save_layout_boundary_repair.md
changed=docs/history/laps/probes/20260912_lap284_work_save_layout_probe.py
evidence=logs/lap289/work_save_layout_before.json, work_save_layout_after.json,
logs/lap289/lap279_serializer_rerun.json, lap284_middle_runtime_rerun.json,
logs/lap289/lap280_crossverify_rerun.stderr

이번 바퀴 변경:
- work probe의 `SAVE_END`를 `0x440FF0`에서 `0x440F5B` exclusive로 좁혔다.
- `FREAD=0x4DA4A9`와 save-window 호출 단언을 같은 work probe에 추가했다.
- 게임 코드/원본 EXE/fixture/하네스/PASS 규칙/baseline/golden은 변경하지 않았다.

성공한 검증:
- 수정 전·후 work probe 모두 exit0, `failures=[]`, JSON 바이트 동일 SHA
  `7381b5f7ebbc99a6a6d9e9cdc0ce95b3bcbaf6237645d521b83c59eba5cbfb81`.
  layer=28, roster=375/558/147/149.
- widened-window in-memory mutant(`SAVE_END=0x440FF0`)은 exit1이며
  `0x4da4a9 was included as a save fread target: ['0x00440fa4']`를 발화했다.
- lap279와 lap284 middle runtime probe는 각각 exit0 및 기존 출력과 바이트 동일.
- 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`와
  fixture 4종 SHA는 기록값과 일치. 원본/fixture 쓰기와 게임/Wine/Xvfb/Stage B 실행은 0.

필수 검증 실패:
- `.venv/bin/python docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`
  가 line 130의 `re.search(r"internal_id=i\(0x([0-9A-Fa-f]+)\)", src).group(1)`에서
  `NoneType` AttributeError로 exit1. 재시도하지 않았고 stderr를 보존했다.
- 따라서 `make check`/safety는 이 실패 뒤 실행하지 않았다. 이번 바퀴 최종 PASS나 카드 종결을
  주장하지 않는다.

다음 승격 작업자가 이어서 검증할 것:
1. lap280 probe line 130의 `internal_id` 정규식이 현재 source와 불일치하는 정확한 원인을
   원본 source/fixture/provenance와 대조해 진단한다. 원인 불명 상태에서 정규식을 임의 수정하지 않는다.
2. lap280 실패 원인을 해결할 권한/범위를 정한 뒤 fresh run으로 lap279/lap280/lap284-middle
   출력 불변 대조를 다시 수행하고, work 정정의 ACCEPT/REJECT를 판정한다.
3. 그 전까지 `make check`, Stage B, 게임/Wine/Xvfb, runtime 경로, PASS 규칙 변경 및 마일스톤
   승격은 금지한다. 기존 blocker와 lap288 provenance 경고는 유지한다.

--- previous escalation preserved below ---
lap=288 (counter file; agent only read it)
role=middle (Claude Code claude-opus-5/high; 진단·계획·확인) -> handoff back to work tier
status=REVIEWED: lap287 boundary repair는 내용상 옳지만 정정1이 지목한 파일에 적용되지 않았다.
판정 = ACCEPT(수리 내용) / REJECT(카드 종결). 이번 바퀴는 새로 승격하지 않는다.
target=G1 S1 저장 serializer의 offline 경계 정확성과 회귀 가드 배치. 제품 G1 종결/runtime
예산/Stage B가 아니다.
record=docs/history/laps/20260912_lap288_middle_boundary_repair_review.md
probe=docs/history/laps/probes/20260912_lap288_middle_boundary_review_probe.py
output=logs/lap288/middle_boundary_review.json (SHA 86157fadedca590963087536853a05661953d6f7a6b8a8e4dfe4c3e5cf2471c9)

확인한 것 (독립 재유도, lap287 기록을 신뢰하지 않고):
- 경계 CONFIRMED. `0x440C20..0x440FF0` 원시 sweep에서 창 안의 `ret`은 `0x440C62`, `0x440F5A`
  둘뿐이고 창 밖으로 나가는 분기 0건, padding run이 정확히 `0x440F5B`에서 시작하며 다음 함수
  진입점은 `0x440F60`이다. exclusive `SAVE_END=0x440F5B`는 옳다.
- 재현성 CONFIRMED. lap287 probe 재실행이 `logs/lap287/…json` SHA `f0568622…08bc5`와 바이트
  동일. 원본 EXE SHA와 fixture 4종 SHA 전후 동일. 자체 probe도 재실행 바이트 동일.
- 가드의 반증력 CONFIRMED(mutation matrix): M0 control exit0/failures 0; M1(SAVE_END만
  `0x440FF0`으로 되돌림) exit1, 경계 단언이 죽인다; M2(되돌림 + ret/padding 조기종료 제거 =
  lap284 work probe의 평면 창 형태) exit1 failures 39이며 `0x4da4a9 was included as a save
  fwrite target: ['0x00440fa4']`가 실제로 발화한다.
- 정정2 반영 CONFIRMED. M2에서 네 fixture 전부 `remainder … is not a multiple of 1880`이
  발화해 "정수배 검사 4건"이 실제 반증력임을 실측했다.

REJECT 사유 (카드는 열려 있다):
- 정정1의 표제는 "**work probe**의 디스어셈블 윈도우"였는데 lap287은 middle 소유
  `20260912_lap286_middle_save_layout_review_probe.py`를 고쳤다. 그 파일은 이미
  `last_instruction=0x00440f5a`를 보고하고 있었고 결함이 없었다.
- `20260912_lap284_work_save_layout_probe.py:26`은 여전히 `SAVE_ENTRY, SAVE_END = 0x440C20,
  0x440FF0`이다. 같은 상수를 든 probe가 4개다: lap279_middle_s1_serializer,
  lap280_middle_s1_crossverify, lap284_middle_runtime_contract, lap284_work_save_layout.
  lap279/280은 `LOAD_ENTRY = 0x440FF0`까지 두어 `0x440F60`과 `0x440F96`의 두 별개 루틴을
  save 쪽으로 잘못 귀속한다.
- M1에서 fread 단언이 발화하지 않는 데서 보이듯, 그 단언은 `body()`의 ret 규칙이 있는 파일에서는
  구조적으로 도달 불가다. 가드가 가장 필요 없는 파일에 붙었고 가장 필요한 파일에는 없다.

완화 사실 (과잉 반응 금지): 틈 `0x440F5B..0x440FF0`의 call 대상은 `0x440A80`/`0x4DA9F2`/
`0x4DA4A9`/`0x4DA97C`뿐이고 **fwrite(`0x4DA39F`) 호출은 0건**이다. 따라서 넓은 창은 네 probe
어디에서도 save 쪽 fwrite 수를 부풀리지 않았다. 드리프트는 잠재적 오분류 위험이며 lap279~287의
기록 수치를 무효화하지 않는다.

provenance 손상: lap287(work)이 middle 소유 probe를 편집해 "같은 파일 단일 작성자"를 넘었다.
편집 전 SHA가 어디에도 없어 `logs/lap286/middle_save_layout_review.json`을 그 경로에서
재생성할 수 없다. 다만 두 로그의 유일한 차이는 `save_function`에 `exclusive_end`와
`fread_calls_in_save` 두 필드가 는 것뿐이고 `last_instruction`을 포함한 모든 모델 수치가
동일하므로 lap286 판정의 수치는 유효하다.

Evidence:
- `make check`: **292 passed(45.95s)**, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`;
  `LOOP_DRY_RUN=0 bash checks/safety.sh check`: `SAFETY_PASS`.
- 원본 EXE `b56986e0…c9c08a8ac` 검수 전후 동일. fixture save000/006/011/012 SHA 기록값 일치.
- 게임/Wine/Xvfb/Stage B/PNG/원본 실행 0. 게임 코드 변경 0. uncommitted, `LOOP_ALLOW_COMMITS=0`.

이것은 기계(1단) middle 검수 결과이며 제품 G1 증거나 사용자 마일스톤 승인이 아니다.

다음 work tier(Luna/Sonnet5)가 할 일:
1. `20260912_lap284_work_save_layout_probe.py:26`의 `SAVE_END`를 `0x440F5B`로 좁히고
   `0x4DA4A9`를 fwrite로 세지 않는다는 단언을 **그 파일에** 넣는다.
2. 그 probe를 재실행해 `logs/lap284/work_save_layout_probe.json`의 모델 수치가 불변임을 보인다
   (틈에 fwrite가 0건이므로 불변이어야 한다. 바뀌면 그것이 새 blocker다).
3. lap279/lap280/lap284_middle_runtime의 `0x440FF0`·`LOAD_ENTRY` 사용처를 열거하고, 좁힌 경계로
   각 기록 출력이 불변인지 대조한다. 불변이면 기록에 남기고, 아니면 수리하지 말고 middle로 올린다.
4. 편집한 파일의 편집 전/후 SHA를 기록해 provenance를 복원한다. 남의 tier 소유 probe는 건드리지
   않는다.

Stage B, 게임, Wine, Xvfb, runtime 예산, PASS 규칙 변경은 STATUS대로 계속 금지다.

--- previous escalation preserved below ---
lap=286
role=middle (Claude Code claude-opus-5/high; 진단·계획·확인) -> next fresh session must re-verify
status=RESOLVED: lap284 work의 save-layout offline 카드를 이번 middle이 독립 검수해
ACCEPT-WITH-CORRECTION으로 종결했다. 이번 바퀴는 새로 승격하지 않는다. 다음 인계는 work tier다.
target=G1 S1 저장 serializer static 모델의 재현성. 제품 G1 종결/runtime 예산/Stage B가 아니다.
record=docs/history/laps/20260912_lap286_middle_save_layout_review.md
probe=docs/history/laps/probes/20260912_lap286_middle_save_layout_review_probe.py
output=logs/lap286/middle_save_layout_review.json

검수 방법은 work probe와 의도적으로 다른 추출 경로를 썼다: save 함수 범위를 자기 ret + 분기
목적지 폐포로 끊고, layer 본문을 다음 layer 주소가 아니라 각 함수 경계로 끊고, mode/repeat/
element를 문자열 매칭이 아니라 디코딩한 fwrite 인자 push와 감소 루프 레지스터에서 읽고,
save 함수가 무시하는 모든 callee를 깊이 3까지 전이적으로 fwrite 도달 검사하고, 페이로드를
호출 순서대로 재생해 bulk/PlayerStruct 파일 오프셋을 계산했다.

결과: 상수항 1,400,702 + 면적계수 30.5, prefix 2,388,902(180x180)/1,705,702(100x100),
roster 해 375/558/147/149가 work와 전부 일치. 호출순서 재생 오프셋도 일치. layer 28개의
mode/repeat/element 분류가 두 경로에서 전부 일치. 무시된 callee 5종의 fwrite 전이 도달 0.
자체 probe exit0 failures=[], 재실행 바이트 동일. work probe 재실행도 기록 출력과 바이트 동일.
make check 292 passed(44.86s), Ruff/compileall/mypy 10 files, CONTEXT_PASS, SAFETY_PASS.
원본 EXE SHA b56986e0..c9c08a8ac 전후 동일. 게임/Wine/Xvfb/Stage B/PNG/원본 실행 0.

정정1(work tier 처리 대상): work probe의 SAVE_END=0x440FF0이 실제 save 함수 끝(ret at
0x440F5A)을 넘어 다음 별개 함수 0x440F60(슬롯 헤더 0x40B를 fread로 읽는 루틴)까지 포함한다.
그 호출들은 무시되므로 크기 모델은 무영향이지만, 0x4DA4A9가 fwrite(0x4DA39F)와 같은 4인자
(ptr,size,count,FILE*) 시그니처라 장래 오인 위험이 있다. SAVE_END를 0x440F5B로 좁히고
"0x4DA4A9를 fwrite로 세지 않는다"는 단언을 회귀로 추가하라.
정정2: roster_records는 나머지를 0x758로 나눠 구한 값이므로 reconstructed==actual은 항상
성립한다. 반증력은 정수배 검사 4건뿐이며 검사 2종이 아니다. 기록 문구를 여기에 맞춰라.

닫지 못한 범위 한계(검증된 것으로 읽지 말 것): 네 fixture가 전부 정사각·짝수 변이라 파일
오프셋 210/212의 width/height 배정과 halving layer의 기계 공식 ((w/2)*h)/2 대 (w*h)//4를
구분할 수 없다. unit record owner 필드 +0x8E는 work에서 상속한 가정이며 재유도하지 않았다.
runtime layer 값의 의미, save/load 값 동일성, 로드 메뉴/PS35 좌표, tick 순환 의존,
G3 9~16 직렬화 0x1B5A4 초과, 제품 G1~G4는 전부 미해결이며 이 ACCEPT가 덮지 않는다.

보강 관찰(반증 아님): 네 fixture 모두 owner id >= 8인 unit record가 0개다. 기존 G3 저장 포맷
blocker와 같은 방향이다. owner 히스토그램을 work가 다루지 않은 save011/012까지 확장했다.

주의: 러너 로그는 logs/laps/2026-09-12/lap-0286.log이고 loop/.lap_counter=286이나, 직전 세션이
자신을 lap284 work로 기록해 기록 lap 번호가 러너보다 하나 뒤진다. 이번 기록은 PROMPT 계약대로
286을 썼다. .lap_counter는 읽기만 했고 쓰지 않았다.

다음 work 세션은 정정1/정정2만 처리한다. 게임 실행, 하네스 로드 경로 구현, PASS 규칙 변경,
baseline/golden 갱신, Stage B는 계속 금지다. 불일치를 발견하면 상수를 맞추지 말고 이 probe와
출력을 보존한 채 구체 blocker로 돌려보내라.

--- prior escalation preserved ---
lap=284
role=work (Codex work tier / high contract; hands-on implementation and verification)
status=ESCALATED: lap284 work offline card completed; next fresh middle must independently review
the static save-layout model before any runtime budget or harness change.
target=G1 S1 save serializer layout and fixture-size proof, not product G1 closure
record=docs/history/laps/20260912_lap284_work_save_layout.md
probe=docs/history/laps/probes/20260912_lap284_work_save_layout_probe.py
output=logs/lap284/work_save_layout_probe.json

The probe reads the original EXE and private fixture bytes only. It statically follows save entry
0x440C20, 28 layer calls, nested fixed fwrite helpers 0x403950/0x4441E0/0x4464B0, bulk
0x892410/0xE397C, and roster stride 0x758. It re-ran the original EXE SHA
b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac and four fixture SHAs.
All four exact-size checks passed: save000/006/011/012 solve to 375/558/147/149 roster records;
save000/006 PlayerStruct nation/is_cpu/alliance and owner counts are preserved in the JSON.
Probe exit0, failures=[]. No game/Wine/Xvfb/Stage B/PNG, original write, harness/PASS-rule change,
or production code change occurred.

Next middle must independently re-run the probe and objdump-derived layer/helper accounting,
confirm the four exact reconstructions and the save000/006 absolute unit counts, then ACCEPT or
REJECT this offline handoff. Runtime load-menu coordinates, PS35 path, tick rule, save/load value
determinism, G3 9~16 serialization overflow, and product G1 evidence remain open; do not treat this
PASS as runtime approval or milestone approval. If independent review finds a mismatch, preserve
this probe/output and return a concrete blocker rather than fitting constants.

--- prior escalation preserved ---
lap=284
role=middle (Claude Code claude-opus-5/high; 진단·계획·확인) -> next fresh session must re-verify
status=RESOLVED: lap283 Astra의 승격 요청(실행 계약 여섯 필수 입력 판정)을 이번 middle이
수행해 종료했다. 이번 바퀴는 새로 승격하지 않는다. 다음 인계는 아래 work 카드다.
target=lap283 실행 계약 ACCEPT/REJECT + offline work 범위 확정
판정문서: docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md
기록: docs/history/laps/20260912_lap284_middle_runtime_contract.md
probe: docs/history/laps/probes/20260912_lap284_middle_runtime_contract_probe.py
  -> logs/lap284/runtime_contract_probe.json, exit0, failures=[]

판정: ACCEPT 1(측정식) / ACCEPT-WITH-CONDITION 1(실패 보존) / REJECT 4(fixture 선택,
하네스 연결, tick, 실행 봉투). 따라서 **runtime 예산을 요청하지 않는다.** 원본↔원본 1쌍도
요청하지 않았고 Stage B는 0을 유지한다. 게임/Wine/Xvfb/Stage B/원본 재실행/PNG 0회,
원본 트리 쓰기 0, comparator/producer/회귀/테스트/PASS 규칙/하네스 0바이트 변경.

REJECT의 기계 근거(요약): tools/runtime_env.py의 save 파일 참조 0·PS35 참조 0·대기 PS는
3/5/7/9뿐이고, 타이틀의 불러오기 좌표가 저장소 어디에도 없다. 로드 경로는 PS7/PS5를 건너뛰어
_g1_start_endpoint_pass의 선언 PASS 규칙(before_ps==5 -> ps==3)을 우회한다. tick은 계약이
근거 없이는 예산을 막는데 그 근거가 실행 후에만 생기는 순환 의존이다.

새로 얻은 정적 근거: save entry 0x440C20의 페이로드 순서 50개(헤더 0x40 -> literal 17 ->
가변 map layer 28 -> literal 3 -> bulk 0x892410/0xE397C -> literal 1 -> 로스터 0x40F4B0),
첫 layer 앞 고정 22978바이트, map block 파일 오프셋 70, 유도 폭/높이 오프셋 210/212에서
save000/006=180x180, save011/012=100x100, 같은 지도 쌍 크기 차이가 0x758 정수배(183/2).

work 인계(다음 새 세션, Luna/high 또는 Sonnet5/high, 실행 예산 0, offline):
판정문서 §7 — 저장 파일 바이트 레이아웃 모델을 정적으로 유도하고 네 fixture 파일 크기로
반증 검증한다. 예측이 한 파일이라도 틀리면 상수를 맞추지 말고 모델을 버리고 blocker로 반환.
하네스 수정/게임 실행/PASS 규칙 변경은 이 카드에 포함되지 않는다.
상위(Astra) 큐 3건은 §8: tick report-only 제안 승인 여부, 로드 경로의 endpoint 규칙 우회,
fixture 열거에서 save011/012 누락.

검증: make check 292 passed(44.47s), Ruff/compileall/mypy 10 files, CONTEXT_PASS, SAFETY_PASS,
원본 EXE SHA b56986e0…c9c08a8ac 전후 동일. 프로세스 exit0은 계획 승인도 제품 검증도 아니다.
이전 반려/승격 원문은 아래 그대로 보존한다.

--- prior escalation preserved ---
lap=283
role=Astra major direction/master-plan (Codex gpt-6-astra/high) -> fresh middle
status=ESCALATED: 실행 가능한 저장 fixture 절차·하네스 변경안·tick 오차 근거 미확정.
범위 결정: docs/work/active/G1_RUNTIME_G3_ASTRA_DECISION_LAP283.md
실행 예산 0, Stage B 0, M1/G1 유지. 상위 계획은 middle 승인이나 제품 검증 PASS가 아니다.
새 Sol 승격 작업자는 위 계약의 fixture/실제 로드 경로/(A)+(B)/tick/명령·시간·격리·보존
여섯 항목을 근거로 ACCEPT/REJECT하고 offline work 범위 하나로 인계할 것.
실구현은 Luna/high 또는 Sonnet5/high 새 세션으로 분리. 완성된 실행 봉투의 원본 대조
1쌍 예산만 상위에 요청한다. 무조건 재시도·Stage B 재개·마일스톤 마감 금지.
G3는 버전 식별 가능한 저장 확장 방향; 현재 bulk 길이 증가 구현 금지, G1 밖에 보존.
검증 기록: docs/history/laps/20260912_lap283_astra_runtime_g3.md
lap282 probe 새 결과 동일(failures=[]), 게임/코드 수정 0. 필수 Fast 결과는 기록 참조.
이전 반려/승격 원문은 아래 그대로 보존한다.

--- prior escalation preserved ---
lap=282
role=middle (Claude Code claude-opus-5/high; 진단·계획·확인) -> next fresh session must re-verify
status=ACCEPT-WITH-CORRECTION: lap281 work tier의 유닛 오프셋 상수 승격을 독립 검수해
수용했다. 정정 1건(문서 인용 기준). 게임 코드 수정 0, Stage B/runtime 예산은 열지 않았다.
target=G1 유닛 레코드 오프셋의 정적 타당성 2단 판정 + 상위 결정 대기 항목 유지

lap281 기록이 요구한 독립 검수를 수행했다. lap281이 남긴 파일 SHA 5개가 전부 현재
파일과 일치해 변경이 사후 수정 없이 보존됐음을 먼저 확인했다. 그 위에서 원본
b56986e0…c9c08a8ac를 **새로 objdump** 해 306218 instruction row를 다시 파싱하고,
lap281이 기록한 모든 수치를 재도출했다: slot0 절대주소 0x66BA2C/0x66BA32/0x66BA34,
세 accessor 전부 lea/shl4/sub/lea로 slot*235 → [reg*8+…] = slot*0x758(= G1_UNIT_STRIDE)
재계산 일치, x 참조 115 / y 참조 115 동일, 대표 쌍 0x4069C7·0x4069D1 및
0x40815D·0x40816B이 실제 x/y 쌍. 상수 3개는 tools/runtime_env.py:184-186에 정의되고
runtime_driver.py:25-27,102,106-107이 이를 사용하며 driver에 0x29C/0x2A2/0x2A4 매직
리터럴은 남아 있지 않다.
재실행 가능 probe: docs/history/laps/probes/20260912_lap282_middle_unit_offset_review_probe.py
-> logs/lap282/unit_offset_review_probe.json, exit0, failures=[].

lap281이 확인하지 않은 두 가지를 보강했고 둘 다 오프셋 해석을 지지한다:
(a) 필드 경계 배타성 — 선언 폭 내부 바이트 0x66BA2D/2E/2F, 0x66BA33, 0x66BA35를
    참조하는 명령이 원본에 0개다. 4/2/2 바이트 해석을 쪼개는 접근이 없다.
    더불어 internal_id 참조 67개가 전부 DWORD PTR이다(비-DWORD 0).
(b) 부호 해석 — x/y 각각 movsx 읽기 41회. driver의 <h(signed short) 디코드가
    원본 사용과 일치한다. lap281은 폭만 기록하고 부호 근거는 남기지 않았다.

정정1: analysis/memory_maps/population_runtime_bridge_0910.md의 "the adjacent accessors
at 0x40F5D0 and 0x40F5F0 read the x/y WORDs"는 인용 기준이 틀렸다. 그 두 주소는 함수
진입점이 아니라 **읽기 명령 주소**이며 call site가 각각 0이다. 실제 호출되는 accessor
진입점은 0x40F5C0(caller 74)과 0x40F5E0(caller 79)이고, 두 함수는 0x40F540과 동일한
slot*235 프롤로그를 가진 뒤 0x40F5D0/0x40F5F0에서 WORD를 읽는다. 같은 문장의
0x40F540은 진입점이 맞아(caller 74) 필드마다 인용 기준이 섞여 있다. 오프셋 값·폭·
스케일링은 영향받지 않으므로 lap281 판정을 뒤집지 않는다.

왜 escalate 하는가: (1) middle은 자기 결과를 승인할 수 없고, 이번에도 이전 바퀴의
기록된 문장 하나를 정정했다. (2) STATUS의 "다음 한 가지"가 **상위(Astra) 결정 항목**
이다 — runtime 쌍/Stage B 예산, 그리고 G3 저장 포맷의 0x1B5A4 넘침(9~16번 플레이어를
직렬화할 공간이 구조적으로 없음). middle 역할로 열 수 없다. (3) 아래 work handoff는
구현이므로 middle이 직접 하지 않았다.

work tier handoff (구현, middle이 직접 하지 않음):
- W1: analysis/memory_maps/population_runtime_bridge_0910.md의 accessor 인용을
  진입점 기준으로 통일한다. x=0x40F5C0, y=0x40F5E0을 진입점으로, 0x40F5D0/0x40F5F0은
  읽기 명령으로 구분해 적는다. caller 수(74/79/74)를 근거로 함께 남긴다.
  문서만 바꾸는 변경이며 상수 값·테스트·PASS 규칙은 건드리지 않는다.
- W2: patches/population/runtime_driver.py에 아직 매직 리터럴로 남은
  type=u[0x8D], 0x66B790, 0x758, 0x8990C8을 runtime_env.py의 기존 동일 값 상수
  (G1_UNIT_TYPE_OFFSET, G1_UNIT_BASE_ADDRESS, G1_UNIT_STRIDE,
  G1_UNIT_EXISTS_BASE_ADDRESS)로 승격한다. lap281 선언 범위 밖이라 남은 드리프트
  사각이다. owner=u[0x8E]는 runtime_env.py에 대응 상수가 없으므로 상수 신설 여부를
  포함해 판단하고, 신설한다면 원본 정적 근거를 함께 기록한다.
  W1/W2 모두 회귀 테스트 유지 + make check 통과가 조건이며, 통과만으로 제품 증거가
  되지 않는다.

Stage B/실행 예산은 이번 바퀴에도 0이다. 게임/Wine/Xvfb/원본 재실행 없음.
미검증으로 남는 것: 두 run의 실제 값 동일성, S1 실제 결정성, WM_CLOSE teardown,
G2~G4 증거, G3 저장 포맷 넘침. 이 검수는 정적 레이아웃 타당성뿐이다.
검사: make check 292 passed(44.57s), Ruff/compileall/mypy 10 files, CONTEXT_PASS,
SAFETY_PASS, targeted unit_record_offsets 1 passed. 원본 SHA 검수 전후 동일.

lap=280
role=middle (Claude Code claude-opus-5/high; 진단·계획·확인) -> next fresh session must re-verify
status=ACCEPT-WITH-CORRECTIONS: lap279가 승격 요청한 "여섯 행 CONFIRMED 교체 수용 여부"를
독립 교차검증으로 수용했다. 정정 2건 동반. Stage B/runtime 예산은 열지 않았다.
target=G1 S1 정적 fixture 타당성의 2단 판정 + 상위 결정 대기 항목 좁히기

lap279의 escalate가 요구한 검증을 수행했다. lap279 probe를 재실행해 exit0/failures=[]이고
출력이 기록과 동일했고, 거기에 더해 **다른 추출 경로**로 원시 objdump에서 다시 읽었다:
literal 블록 21개와 save/load 표 완전 일치(22/22 호출), bulk fwrite(0x892410,0xE397C,1)
-> 0x975D8C, camera 0xB42D7C(4B)+0xB42D80(4B) 인접, 로스터 1200*0x758 = 0x66B790..0x892410,
load 순서 bulk(0x4412DC) -> 로스터(0x441305), G3 넘침 0x991330-0x975D8C = 0x1B5A4.
전부 독립 재계산 일치. 보강 근거도 하나 찾았다: load 로스터 0x40F51B가 미존재 슬롯을
rep stos 0x1D6 dword(=0x758 B)로 0 채우므로 로스터 영역에 잔여 상태가 남지 않는다.
재실행 가능 probe: docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py
-> logs/lap280/s1_crossverify_probe.json, exit0, failures=[].

정정1: lap279 §4.2.2의 "이 저장 포맷은 추측 파싱 없이 정적으로 완전히 열거된다"는 과장이다.
literal 표 밖에 (a) 비-literal 스택 블록 1개(0x440C70, 0x40 B)와 (b) map-layer serializer
28쌍(save 0x42A920…0x42BC40 + 0x42AB70 / load 0x42A960…0x42BC80 + 0x42ABA0)이 있다.
lap279는 그중 한 개의 앞 0x40 바이트만 봤다. 이번에 28쌍 개수 동일, 주소 인접(델타 0x30~0xA0),
28개 save 전부 fwrite 호출 / 28개 load 전부 fread 호출을 기계 확인했다. 지형 레이어이므로
여섯 행을 뒤집지 않는다. 다만 **레이어별 원소 수가 save/load에서 같다는 것은 아직 미검증**이다.

정정2: lap279 §4.2.5-1의 전제가 틀렸다. tools/runtime_env.py에는 유닛 좌표 읽기 경로가 없다
(line 2412는 scene_state["units"]를 그대로 받아쓴다). 실제 생산자는
patches/population/runtime_driver.py:84-100이고 오프셋이 이미 고정돼 있다: x=+0x2A2(2B),
y=+0x2A4(2B), internal_id=+0x29C(4B), type=+0x8D, owner=+0x8E. 원본 교차근거는
WORD PTR [reg+0x66BA32] 115회 / [reg+0x66BA34] 115회로 개수가 정확히 같고 항상 짝으로
movsx 읽히며, 접근자 0x40F540이 eax*8 = slot*0x758로 +0x29C를 반환한다. 즉 x/y 오프셋 고정은
이미 CONFIRMED이고 남은 것은 상수 승격이라는 work tier 구현 하나뿐이다.

왜 여전히 escalate 하는가: (1) middle은 자기 결과를 승인할 수 없고, 이번에도 이전 바퀴의
기록된 문장 두 개를 정정했다. (2) lap279가 올린 상위 결정 항목이 그대로 열려 있다 —
G3 저장 포맷의 0x1B5A4 넘침(9~16번 플레이어를 직렬화할 공간이 구조적으로 없음)과
runtime 쌍 / Stage B 예산. 이 tier의 권한 밖이다. (3) 새 미검증 항목 하나 추가:
map-layer 28쌍의 레이어별 원소 수 동일성.

승격 작업자가 이어서 검증할 것: (a) lap280 probe를 재실행해 21블록 표·28쌍 pairing·
x/y 오프셋 교차근거·G3 산술을 독립 재계산하고 이번 ACCEPT 판정을 수용할지 판정한다.
(b) 그 다음 work tier에 상수 승격(x/y/internal_id -> tools/runtime_env.py)을 발주한다.
(c) Astra는 runtime 쌍/Stage B 예산과 G3 저장 포맷 방향을 결정한다. 게임/Wine/Xvfb/
Stage B/원본 재실행은 그 결정 전까지 계속 금지다. 커밋 없음(LOOP_ALLOW_COMMITS=0).

---
lap=279
role=middle (Claude Code claude-opus-5/high; 진단·계획·컨펌) -> next fresh session must re-verify
status=REVERSAL: lap278의 다섯 행 UNKNOWN/research blocker를 반려하고 여섯 행 전부 CONFIRMED로 교체했다.
target=G1 S1 정적 fixture 타당성. Stage B/runtime 예산은 열지 않았다.

lap279는 지시받은 lap278 독립 검수를 완료했다. lap278이 기록한 SHA 7종(원본 EXE
b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac, save000/006, runtime_env,
comparator, memory map)은 전부 재계산 일치했고 entry 주소도 재현됐다. 그러나 lap278의 판정은
틀렸다. 원인은 증거 부족이 아니라 조사 미완이다: save/load entry의 fwrite/fread 목록을 끝까지
열거하지 않고 첫 map block에서 멈췄다.

같은 읽기 전용 범위에서 fwrite(0x4DA39F) 22회 / fread(0x4DA4A9) 22회를 전부 뽑으면 literal
블록 21개가 나오고 save 표와 load 표가 주소·크기·순서까지 동일하다. 승인 주소는 전부 그 안에
떨어진다(포함관계 산술): selection 0x899024/28 -> bulk 0x892410 +0x6C14/+0x6C18, logic tick
0x8924B8 -> +0xA8, player base 0x956770 -> +0xC4360, map 0xB3DE34/36 -> 0xB3DDA8 +0x8C/+0x8E,
camera 0xB42D7C(4B)+0xB42D80(4B) = _read_camera(0x00B42D7C, 8)와 정확히 일치. 유닛 로스터는
전용 경로 save 0x40F4B0 / load 0x40F4F0이 존재플래그 0x8990C8을 훑으며 슬롯당 0x758 레코드를
복원하고, 1200*0x758이 정확히 0x892410에서 끝난다. 지도 레이어 serializer 0x42A920은
WORD[ecx+0x8C]*WORD[ecx+0x8E]를 imul해 크기 인자로 쓴다. 재실행 가능 probe:
docs/history/laps/probes/20260912_lap279_middle_s1_serializer_probe.py -> exit0, failures=[].

특히 lap278의 "entry 명시 주소에 selection/camera/logic tick이 없다"와 "0x892410 참조는 승인된
tick 0x8924B8의 근거가 아니다"는 둘 다 사실이 아니다. tick은 그 블록의 +0xA8이다.

왜 escalate 하는가: (1) 이전 바퀴의 기록된 결론을 다섯 행에서 뒤집었고 middle은 자기 결과를
승인할 수 없다. (2) 신규 G3 블로커를 발견했다 — bulk 블록이 0x975D8C에서 끝나 PlayerStruct
8개는 들어가지만 16개는 0x991330까지 필요해 0x1B5A4 바이트 넘친다. 현재 저장 포맷에 9~16번
플레이어를 직렬화할 공간이 구조적으로 없다. 이는 기존 장면 서명 owner8~15 사각과 별개이며
G3 방향 결정(Astra) 사안이다. (3) runtime 쌍/Stage B 예산은 이 tier 권한 밖이다.

승격 작업자가 이어서 검증할 것: probe를 재실행해 21개 블록 표와 승인 주소 포함관계를 독립
재계산하고, 로스터 경로(0x40F4B0/0x40F4F0)와 1200*0x758 = 0x66B790..0x892410 기하를 확인한 뒤,
여섯 행 CONFIRMED 교체를 수용할지 판정한다. 그 다음에야 (a) work tier의 0x758 레코드 x/y
오프셋 고정, (b) Astra의 runtime 쌍/Stage B 예산 및 G3 저장 포맷 방향을 연다. 게임/Wine/Xvfb/
Stage B/원본 재실행은 그 승인 전까지 계속 0이다. 제품 G1은 미완료이며 이 escalation은
마일스톤 승인이 아니다. 게임 코드·comparator·producer·tests·원본 변경 0, 커밋 없음.

--- previous escalation preserved below ---
lap=278
role=work (static S1 investigation; Codex work tier contract) -> next fresh middle independent review
status=RESEARCH_BLOCKER: only world-bounds persistence has positive static basis; five S1 rows remain UNKNOWN.
target=G1 S1 save/load determinism evidence, without opening Stage B/runtime budget

lap278 work completed the permitted read-only investigation. Original EXE SHA is
b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac. Static disassembly confirms
path builder 0x440A80 (`%ssave\\save%d%02d.dat`), save 0x440C20, load 0x440FF0, and a map block
serialization at 0xB3DDA8 size 0xB0. Load-side code at 0x441381/0x44138A directly consumes
0xB3DE36/0xB3DE34, matching the approved world-bounds addresses. This is the sole CONFIRMED row.

Rows 1 nation/player, 2 owner/type/count, 3 world positions/multiplicity, 5 full engine slot IDs,
and 6 selection/camera/tick are UNKNOWN: no static serializer mapping to the approved observation
fields was established, and save000/save006 (`1c703551...e719da`, `616b799...a0d064`) are opaque
`data` files with no permitted format parser. Historical JSON snapshots are not 1:1 linked to those
files, so they were not promoted under §4 criterion (ii). No game/Wine/Xvfb/Stage B/R6-A/R6-C,
no original writes, and no comparator/producer/test changes occurred.

Required handoff: next fresh middle must independently recalculate the source/save hashes, verify
the six-row table in `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1, and decide whether
the narrow static call-graph probe (trace serializer arguments to player/unit/slot/selection/camera/
tick fields) is sufficient. Until that review and a separate budget decision, do not run a runtime
pair or Stage B. Product G1 remains incomplete; this escalation is not a milestone approval.

--- previous escalation preserved below ---
lap=277
role=middle (diagnosis / plan / confirm; Claude Code claude-opus-5 / high) -> work tier handoff
status=ANSWERED. The lap276 escalation is CLOSED by this entry. No new upper-tier question is
       opened. The next lap is a WORK tier lap, not a middle or upper lap.

Ruling: the lap271 section-3 summary formula is INSUFFICIENT and is REJECTED, replaced by
docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md sections 3-4.  Machine evidence:
logs/lap277/s1_formula_probe.json (7 cases, self-check failures=[]).
  (a) It is vacuously true when an observation is absent: a missing drag_select stage and a
      missing selection count both satisfy it while the overall status is INCONCLUSIVE.
      Therefore the formula is replaced by compare_evidence(...)["status"] == "PASS".
  (b) Even overall PASS does not cover items 1, 5 (full) and 6: differing nation, differing
      engine slot ids of every NON-selected unit, differing absolute pre-input selection count,
      scene camera, scene tick and pre-input minimap camera all still reach overall PASS, and an
      extra owner-2 unit present only on one side also still reaches overall PASS.
  (c) Covered, confirmed by controls: items 2/3 including multiplicity for owners 0/1
      (relative_world_offsets is a list, not a set), item 4, and the F2-R2 slot demotion rule,
      which still fires for same-identity/different-slot pairs and was NOT relaxed.
Nothing in the comparator, the producer, the regressions or the original was changed.  This is a
documentation/logic defect in lap271, not a reproduced comparator defect and not a new PASS path.

Approved next: ONE work-tier lap (Luna/high or Sonnet5/high, fresh session) doing the static
save/load investigation, filling all six rows of the LAP277 section-4 deliverable table.
CONFIRMED requires positive basis (i) or (ii) of that section; everything else is UNKNOWN.
A research blocker is an acceptable deliverable.  Game/Wine/Xvfb/Stage B budget stays ZERO.
That work is reviewed by the NEXT fresh middle; no self-approval.

Still open / frozen, unchanged by this lap and NOT blockers for the approved work lap:
R17 structural options and R31, M-d/M-e extractor drift gaps, R6-B-R2, the eight parked offline
items, Stage B candidate pairs, R6-A/R6-C, and the candidate WM_CLOSE teardown defect.
New known limitation recorded this lap, deliberately NOT repaired: scene.owners is built over
range(8) and relative_world_offsets filters owner in (0, 1), so owners 8..15 are structurally
invisible to the scene signature.  This must be reopened for G3; it is out of G1 scope today.
No milestone closure, no product G1 evidence, no runtime budget approval, no commit, no paid
subagent and no service was started this lap.

--- previous escalation preserved below ---
lap=276
role=Astra major direction/master-plan -> fresh middle verification
status=ESCALATED: S1 research acceptance formula is insufficiently explicit; no implementation.
Decision: keep M1/G1, prioritize one bounded static save/load investigation after middle review.
Game/Wine/Xvfb/Stage B budget remains zero. No milestone closure or transition.
Middle must review docs/work/active/G1_S1_ASTRA_DECISION_LAP276.md against the lap271 contract,
positively specify all six restoration checks (including missing evidence rejection, multiplicity,
actual slot IDs and pre-input tick reference), then approve or reject the work handoff.
Do not treat not-UNKNOWN_SLOT_CORRESPONDENCE as proof of restored state.
R17/R31, M-d/M-e, R6-B-R2 and the eight parked offline items remain open/frozen as documented.
Previous text follows verbatim. No retry, implementation, paid subagent or runtime launch this lap.

--- previous escalation preserved below ---
lap=275
role=middle (diagnosis / plan / confirm; Claude Code claude-opus-5 / high) -> upper-tier decision
status=Independent review of the lap274 F3-R2-R1 repair is DONE and the declared range is
       APPROVED (stage-1 machine only).  This entry escalates because closing F3-R2 empties the
       only actionable offline queue item: there is now no work-tier task that any tier is
       permitted to start.  lap270's R17 item and lap271's items remain open verbatim below.

1. F3-R2-R1 verdict: declared-range PASS.
   Two independently scoped AST derivations agree on exactly six producer classifications and the
   comparator declares exactly those six (producer_only 0, comparator_only 0).  The lap275 probe
   scopes on `classification=` keyword arguments file-wide; the lap274 regression scopes on a
   function whitelist plus a name regex.  Newly verified this lap and not verified before:
   `record_timeout` passes `exc.classification` as the 9th positional argument `result`, and
   `_g1_record_input` writes it to `entry["result"]` -- the exact field the comparator reads.  The
   vocabulary agreement is therefore not vacuous.  A 169-cell exhaustive matrix over 13 result
   tokens holds the contract: hard FAIL outranks disputed, the only stage PASS pair is
   ("PASS","PASS"), overall PASS occurs in that one cell only, missing `result` keys are
   INCONCLUSIVE, scene mismatch masks even hard FAIL, slot-only difference demotes to
   UNKNOWN_SLOT_CORRESPONDENCE, and production is NOT_COMPARED in all 169 cells.  Mutation
   attribution in a /tmp copy: a seventh producer species, the lap273 pre-repair comparator state,
   and a renamed direct raise each kill exactly the drift regression (1 failed / 25 passed).  The
   regression is a real killer and is not SHA-pinned.
   `make check` 291 passed (44.66s), Ruff/compileall/mypy 10 files, CONTEXT_PASS, SAFETY_PASS.
   Zero game/Wine/Xvfb/PNG.  Producer, comparator, tests and the protected original are byte
   unchanged; all work is uncommitted (LOOP_ALLOW_COMMITS=0).

2. Known blind spots recorded, NOT repaired -- this is deliberate deference to item 3.
   Two mutations survive `26 passed` in the /tmp copy: (M-d) raising _G1WaitTimeout with a new
   classification from a THIRD function, missed because the lap274 extractor hardcodes the
   function whitelist {_g1_read_selection_stage, _wait_state}; and (M-e) a classification inside
   _wait_state whose name lacks the FAIL_/UNKNOWN_ prefix, missed by the extractor regex.  Both
   are future-drift gaps, not defects in today's producer, whose two real paths and six species do
   match.  The known fix is one line in scope -- derive from `classification=` keyword arguments
   instead of function names and a prefix regex -- but it is the same *test of the test* shape that
   lap270 escalated, so R31 and any new repair series were NOT opened.  Decide whether this
   one-line extractor change is in range, or whether it stays recorded as an accepted limitation.

3. The actionable queue is now empty.  This is the reason for the escalation.
   lap271 classified the nine offline items and found exactly one Stage B precondition: F3-R2.
   That item is now closed.  The remaining eight are unreachable guards (F2-R1, F3-R1, F6-R2),
   gate consumers with zero consumers (R23, R24, stage_budget_state) and harness/test-only items
   (R20, R21, R22).  None of them can open Stage B.  Stage B itself is blocked by S1/F2-R2
   determinism, which STATUS forbids running before an upper-tier re-decision.  Therefore no work
   tier task exists that is both permitted and useful.  The upper tier must pick one of:
   (a) re-decide S1/F2-R2 determinism, or approve an execution budget for the lap271 S1 research
       contract in docs/work/active/G1_S1_DETERMINISM_RESEARCH_CONTRACT.md;
   (b) choose one of lap270's three R17 structural options, ending the *test of the test* series;
   (c) re-decide R6-B-R2 (count 1 -> 0 as a response);
   (d) redirect the loop off G1 card 2 toward G2/G3/G4, which have zero product evidence.
   Without one of these the next lap has nothing measurable to change.

Stage B, game, Wine and Xvfb remain forbidden by STATUS until S1/F2-R2 is re-decided.
This is stage-1 machine approval only, not product G1 evidence and not user milestone approval.

--- previous escalation preserved below ---
lap=273
role=middle (diagnosis / plan / confirm; Claude Code claude-opus-5 / high) -> record + work handoff
status=Independent review of the lap272 F3-R2 repair is DONE.  All mandatory gates passed; nothing
       unexpected failed and no milestone boundary was crossed.  This entry opens NO new upper-tier
       decision.  It exists to (a) correct this file's own item-3 record before the upper tier acts
       on it, and (b) keep lap270's still-open R17 escalation and lap271's items alive, verbatim,
       below.

Correction to the lap271 entry, item 3.  That entry wrote "the producer emits AT LEAST five timeout
classifications" and then listed exactly five.  The hedge was right and the list was short.  Read
back from tools/runtime_env.py by AST this lap, the producer emits SIX:
  UNKNOWN_BUDGET_EXHAUSTED (:3259), UNKNOWN_OBSERVATION_WINDOW_TRUNCATED (:3260),
  UNKNOWN_STATE_READ_FAILURE (:3261 and the direct raise at :2183),
  UNKNOWN_STATE_READ_COVERAGE (:3262), UNKNOWN_SELECTION_OBSERVATION_CORRUPTED (:3263),
  FAIL_NO_EFFECT (:3264).
lap272 copied the five-item list into _DISPUTED_SOURCE_RESULTS and cited runtime_env.py:3258-3264
as its source -- a range that literally contains all six.  UNKNOWN_STATE_READ_COVERAGE is real and
regression-tested at tests/test_runtime_env.py:2551 (the R8 line, lap237/lap238).

Verdict on lap272: DECLARED SCOPE PASS / F3-R2 CONTRACT NOT CLOSED.
  Measured, not inferred (probe + report hashes in the lap273 record):
  - 33-cell matrix over 3 stages x 11 source-result values: the five declared timeouts all give
    stage UNKNOWN_DISPUTED_ORACLE / overall INCONCLUSIVE; a hard "FAIL" gives stage and overall
    FAIL; "BLOCKED", "SKIP", an unrecognised string and an absent result all give INCONCLUSIVE.
    UNKNOWN_STATE_READ_COVERAGE alone lands on INCONCLUSIVE with the reason "source input stage
    result is missing or unrecognized".
  - Exhaustive new-PASS search, 10 values x both sides x 3 stages = 300 cells: overall PASS occurs
    in exactly 3 cells, all of them baseline == candidate == "PASS".  Zero new PASS paths.
  - A hard FAIL on one side still wins when the other side carries a disputed timeout.
  - Scene gate, slot demotion and production NOT_COMPARED are unchanged; M0 control still PASS.
  So this is NOT PASS laundering and NOT a loss of FAIL power -- the card's overall verdict is
  INCONCLUSIVE either way.  The defect is diagnostic routing: a genuinely measured read-coverage
  timeout is reported to humans and to the next session as malformed/unrecognised evidence, which
  points repair at the producer instead of at the disputed observation.  The existing regressions
  cover the same five literals, so make check can never catch the omission.

  The upper tier should note the shape of this, because it is the third time: lap218 fixed three
  literals, lap271 recorded five, lap272 shipped five, and the producer has six.  Enumerating a
  producer vocabulary by hand does not converge.  Whoever rules on the R17 structural question may
  want to rule on this class at the same time -- a derived-from-source enumeration rather than a
  hand-maintained literal set -- but this tier is NOT requesting that decision now and is NOT
  blocking the F3-R2-R1 repair on it.

Handoff to the work tier (Luna or Sonnet5 / high), one item, game execution budget 0:
  F3-R2-R1.  Add UNKNOWN_STATE_READ_COVERAGE to _DISPUTED_SOURCE_RESULTS, but DERIVE it from the
  producer and record the derivation (file, lines, method) in the comment and the lap record --
  do not copy this entry's list either.  Add regressions for all six classifications plus hard
  FAIL, BLOCKED, SKIP, an unrecognised string and an absent result, and re-confirm zero new PASS
  paths and the F1/F4/F5, scene-gate and slot-demotion invariants.  A regression that breaks when
  the set drifts from the producer is preferred, but do NOT couple it to a SHA-pinned SUT (R29/R30
  lesson).  Then the next fresh middle reviews it independently.

Unchanged and still upper-tier property: the R17 structural choice (a)/(b)/(c) with R31 frozen,
the S1 contract's game-execution budget, F2-R2's slot-demotion rule, and R6-B-R2.  Stage B,
original re-runs and Wine/Xvfb remain forbidden until the upper tier rules.

lap=271
role=middle (diagnosis / plan / confirm; Claude Code claude-opus-5 / high) -> upper tier (Astra / user)
status=lap267 Astra items 3 and 4 are DONE.  Mandatory gates all passed; nothing unexpected failed.
       This entry does NOT open a new blocker.  It (a) records the classification result so the
       upper tier can see the queue shrank, (b) hands back the one decision this tier must not
       make, and (c) keeps lap270's still-open R17 escalation alive, verbatim, below.

Item 3 — offline queue classified by REAL Stage B producer/comparator call path.
  Independently measured this lap (6 axes, probe + report hashes at the end).  Result: of the nine
  offline defects, exactly ONE is a Stage B prerequisite.
    P (prerequisite, 1):  F3-R2.  Measured, not inferred: feed the real comparator a candidate
        whose minimap camera genuinely did NOT move, carrying the literal result string the
        producer flushes at tools/runtime_env.py:2844 ("FAIL"), and the card returns stage
        UNKNOWN_DISPUTED_ORACLE / overall INCONCLUSIVE.  Same for "BLOCKED", "SKIP", and all five
        timeout classifications, and for a hard FAIL on the selection axis.  The control (both
        sides PASS and agreeing) still returns overall PASS and new_pass_paths is [].  So this is
        NOT PASS laundering -- it is the loss of the card's ability to say FAIL at all.  That
        matters here specifically because the standing user approval is "bounded repair -> fresh
        validation until Stage B evidence holds"; an oracle that can never return FAIL cannot
        terminate that loop on a genuinely broken candidate.
    H (on the path, currently unreachable guards, 3):  F2-R1 (_stage_report has exactly one call
        site at :357 with 5 positional args and zero external references, so the absolute
        slot/type fallback is dead code), F3-R1 ('"last":' is written at exactly one site,
        runtime_env.py:2551 inside record_timeout with result=exc.classification, so an
        after.last stage can never be result=="PASS"), F6-R2 (both producers wire
        flush=flush_input_stage today; a loss closes INCONCLUSIVE).
    C (evidence written, no gate reads it, 2):  R23 (read_coverage) and R24 (read_failure).
        Both gate tools have 0 consumers.  The comparator's one "selection_count" hit is a key it
        WRITES into details, not a record field it reads, and absent counts fail closed to
        INCONCLUSIVE -- so R24's "top-level null is indistinguishable" cannot produce a PASS.
        stage_budget_state is the same class.
    N (review-harness / test only, NOT product gates, 3):  R20, R21, R22.  R21 in particular is
        not on the product path at all: the producer's _write_json serialises with json.dumps
        FIRST and then does an atomic tmp.replace, and open("x") occurs 0 times anywhere in
        tools/.  The truncation window exists only in the historical probe convention.
  Per Astra item 3 the parked 8 are parked, not deleted and not flipped to PASS.

  Side finding the work tier must not ignore:  lap218's middle re-decision enumerated the disputed
  set as exactly three classifications.  That list is now STALE.  After R12/R15/R25/R26/R27 the
  producer emits at least five timeout classifications (FAIL_NO_EFFECT, UNKNOWN_BUDGET_EXHAUSTED,
  UNKNOWN_OBSERVATION_WINDOW_TRUNCATED, UNKNOWN_STATE_READ_FAILURE,
  UNKNOWN_SELECTION_OBSERVATION_CORRUPTED) and also flushes "BLOCKED" and "SKIP".  The F3-R2
  repair must derive its enumeration from the CURRENT producer set and record the derivation,
  not copy lap218's three literals.

Item 4 — one-page S1 determinism research contract drafted.
  docs/work/active/G1_S1_DETERMINISM_RESEARCH_CONTRACT.md.  Grounded in measured producer facts
  (runtime_env.py:3548 records the fixture as a "default two-player random game; map name/seed not
  exposed by approved read-only offsets", and :3551/:3919 record replay_seed_observed=False) and in
  real starting assets found by read-only listing of the original tree: Syw2plus/save/ has two
  save files, Syw2plus/stagemap/ has 24 fixed .map files, plus cusmap/ and OnlineBattleMap.dat
  (hashes recorded in the contract; nothing copied, nothing committed, nothing written).
  The contract requires SIX properties to be co-restored before a fixture counts as sufficient --
  nation/player composition, per-owner unit types, relative world offsets, world bounds, the
  ENGINE SLOT IDS themselves (F2-R2), and the pre-first-input state -- and it explicitly forbids
  guessing any RNG seed address.  Returning a precise research blocker is an accepted PASS.

Decision requested from Astra / user (this tier does not decide these):
  1. The R17 structural choice (a)/(b)/(c) from the lap270 entry below is STILL OPEN.  R31 stays
     frozen.  Nothing this lap changed that.
  2. The S1 contract's branch (A) ends in a GAME EXECUTION BUDGET REQUEST.  This tier drafted the
     contract but does not grant runtime budget.  Stage B, original re-runs, Wine/Xvfb and
     R6-A/R6-C remain forbidden until the upper tier rules.
  3. F2-R2's slot-demotion rule is untouched and still upper-tier property.

What a promoted worker should independently verify next, in this order:
  * Re-run docs/history/laps/probes/20260912_lap271_offline_queue_classification_probe.py and
    confirm A3 independently -- specifically that a genuinely-failed candidate cannot reach card
    FAIL today, and that the control still reaches PASS with new_pass_paths == [].  If A3 does not
    reproduce, the "F3-R2 is the only prerequisite" conclusion falls and the queue must be
    re-classified before any work tier touches the comparator.
  * Confirm the H/C/N classification is not hiding a reachable path: re-derive A1/A2 from the AST
    rather than trusting this record, since the whole argument for parking F2-R1 and F3-R1 is
    their unreachability.
  * Confirm the F3-R2 repair, when it lands, creates ZERO new PASS paths and does not weaken
    F1/F4/F5 fail-closed, the scene gate, or the slot demotion.  Widening FAIL power is the
    intended direction; new FAIL false positives are the risk to hunt.
  * Do NOT treat this lap's classification as a scope approval for the F3-R2 implementation.  It
    is a machine tier-1 classification only, and it is itself awaiting independent review.

This lap: no implementation, no SUT or protected asset touched, no commits (LOOP_ALLOW_COMMITS=0),
no game / Wine / Xvfb / PNG, no milestone closed, no open item silently closed.
Product evidence added this lap: zero.
Gates: make check 279 passed (43.72s), Ruff/compileall/mypy 10 files, CONTEXT_PASS, SAFETY_PASS.
lap270's five fingerprints were recomputed and are byte-identical and unchanged before/after.
Record: docs/history/laps/20260912_lap271_middle_offline_queue_classification.md
Probe:  docs/history/laps/probes/20260912_lap271_offline_queue_classification_probe.py
        (618d23dd8121c4b6dc09e8310e3ea2382fb706c0e5fcca99fea5f00c206e8c48)
Report: docs/history/laps/probes/20260912_lap271_offline_queue_classification_report.json
        (f1d7dc6b7daaa626172d67c65ae9da3324e8c8c302ab7028403b2f5479ffe969)

--- previous escalation preserved below ---

lap=270
role=middle (diagnosis / plan / confirm; Claude Code claude-opus-5 / high) -> upper tier (Astra / user)
status=lap268's requested independent review of R30 is DONE.
       VERDICT: R30 DELIVERED SCOPE APPROVED (machine tier 1).  R17 COVERAGE CONTRACT **NOT** CLOSED.
       This is a NEW escalation: the R19->R30 repair family has no fixed point and needs a
       structural redecision above this tier.  Prior text preserved verbatim below.

What reproduced (so lap269 work is NOT at fault):
  Fingerprints under review are byte-identical to the lap269 record and unchanged before/after:
  tests/test_review_probe_output.py=862fd64a..., SUT probe 20260912_lap228_...=16f74629...,
  tools/runtime_env.py=e4f6a834...  Mirrors carry the repository test file verbatim (no helper swap,
  unlike lap268).  C2 mirror M0 8 passed = real repo 8 passed.  C3 matrix M1..M10 matches lap269's
  declared numbers EXACTLY: survivor [M1_rename_only]; M2/M3/M6/M7/M8 each 1 failed / 7 passed with
  kill_reason r17_coverage_assert; M9/M10 completeness_assert.  C4: deleting only the line
  `assert not (_review_body_lines() & seen)` revives M2/M3/M6/M7/M8 at 8 passed -> R17 is the SOLE
  killer and R7/R10/R11/R15/R25/R26/R27 are undamaged.  C1 (new, lap269 never measured it): body is
  81 lines; a normal run executes 58 of them, a refusal run executes 0 (max executed line 128).  So
  R30 is a real improvement over R29, whose body had collapsed to 5 lines with 0 executed.
  make check 279 passed (45.47s), Ruff/compileall/mypy 10 files, CONTEXT_PASS, SAFETY_PASS.
  Game / Wine / Xvfb / PNG: 0.  No SUT or protected asset touched.  No commits.

Why the contract is still open — new counterexample M11 (survives at 8 passed):
  M8 aliased ONE review result ahead of a relocated refusal.  M11 is the closure of that family:
  compute all SEVEN review results under `_SRC_<name>`, move the preflight refusal block to just
  above the report write, then rebind the seven canonical names below it.  The probe still refuses
  correctly (rc 2, correct message) but **260 module lines execute before the refusal** (baseline
  48, max executed line 407) — exactly the late-refusal defect R17 exists to catch — while the R30
  body set collapses from 81 lines to 8 (the seven rebinds + the report write), all of which sit
  below the refusal.  `assert not (body & seen)` is vacuous again and the suite passes.
  Root cause, identical across lap262/264/266/270: the body set is derived from the SYNTAX OF THE
  VERY FILE BEING MUTATED.  R30's union closed the "movable FIRST anchor" defect but not the
  "anchor is attacker-controlled" defect.  Adding more anchor names only moves the next M12.

What this lap did NOT do, deliberately:
  It did not open R31.  laps 261-270 are ten consecutive laps on a test-of-a-test with zero G1~G4
  product evidence added, and starting an eleventh in the same family would bypass the standing
  STATUS blocker that is already waiting on upper-tier adjudication.  R29's rejection (lap266)
  stands; M9/M10 rename fail-closed stays as the risk lap268 accepted (do not weaken to a subset
  check).  No SUT edit, no game budget, no milestone closure, no product approval.

Decision requested from Astra / user (this tier does not decide it):
  (a) The SUT is an IMMUTABLE, SHA-pinned historical evidence file (16f74629...).  Assert that SHA
      in the test and then hard-code ABSOLUTE line numbers for the review body.  Because the file
      cannot legitimately change, the attacker-controlled-anchor problem disappears entirely and the
      whole R19..R30 family closes in one lap.  Cost: any future legitimate SUT edit fails closed.
  (b) Drop line-coverage as the mechanism and assert observable side effects instead — e.g. that a
      refusal run performs zero `observe_raw` / `rt._g1_selection_responded` calls.  Stronger
      semantics, larger rewrite.
  (c) Accept R30 as-is with M11 documented as a known, bounded residual and stop spending laps here.
  Until one of these is chosen, R17-family work is frozen.

Next middle session's one thing (unchanged by this lap, and now unblocked): Astra items 3/4 —
classify the offline-queue defects (R20..R24, F2-R1/F3-R1/F3-R2/F6-R2) by real Stage B
producer/comparator call paths, and draft the one-page S1 determinism research contract.
Do NOT auto-drain the offline queue.

Still open for upper-tier adjudication, unchanged — do not silently close:
  * S1 / F2-R2 scene and slot determinism; R6-B-R2 count 1->0 semantics; Astra item 5.
  * Candidate WM_CLOSE teardown defect; G2~G4 have no product evidence at all.
Record: docs/history/laps/20260912_lap270_middle_r30_review.md; probe/report
docs/history/laps/probes/20260912_lap270_r30_review_probe.py (e7cd8593...) + _report.json (aefd3d27...).
Product evidence added this lap: zero.

--- previous escalation preserved verbatim below ---

lap=268
role=middle (diagnosis / plan / confirm; Claude Code claude-opus-5 / high) -> handoff to work tier
status=lap267's requested middle review is DONE.  R30 (variant B) SCOPE APPROVED for the work tier.
       This is NOT a new escalation; it is the resolution of the lap267 one.  Prior text preserved.

Done this lap: re-verified lap267's six fingerprints (test / SUT probe / runtime_env / three lap266
evidence JSONs) — all match the record, no silent edits.  Independently re-derived the lap266 R30B
mutation matrix in a throwaway /tmp mirror and added what lap266 could not answer: WHY each mutation
dies.  M0 8 passed, survivors exactly [M1_rename_only], M2/M3/M6/M7/M8 each 1 failed / 7 passed and
**all five kills attribute to the R17 coverage assertion**, not to the contract's own completeness
self-check.  That satisfies Astra lap267 item 1's distinguishability requirement, so the bounded
repair path is confirmed.  New measured cost: M9 (renaming a review result, no defect) and M10
(M9 o late refusal) both fail with `missing review results` — a fail-closed false positive.  The SUT
is SHA-pinned historical evidence, so that is acceptable and doubles as tamper detection, but the
work tier must document the coupling and must NOT weaken it to a subset check.

Handoff: docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md, section "lap268 middle"; record
docs/history/laps/20260912_lap268_middle_r30_scope.md; probe/report
docs/history/laps/probes/20260912_lap268_r30_scope_probe.py (+ _report.json).
Work tier: tests/test_review_probe_output.py only, one lap, no game/Wine/Xvfb/PNG, no commits.
Stop conditions (preserve, do not retry, write ESCALATE_SOL): numbers not reproduced, a kill that
attributes to the completeness assert instead of R17, a conclusion that the SUT must be edited, or
any weakening of R7/R10/R11/R15/R25/R26/R27.

Still open for upper-tier (Astra / user) adjudication — unchanged by this lap, do not silently close:
  * R29 range rejection stands (lap266).  R30 scope approval is not R30 approval.
  * S1 / F2-R2 scene and slot determinism; R6-B-R2 count 1->0 semantics.  Astra item 5 asks middle
    to reconcile the fixed drag's intent vs observation for upper-tier adjudication — still queued.
  * Astra items 3/4 (classify offline-queue defects by real Stage B producer/comparator call paths;
    draft the one-page S1 determinism research contract) are the NEXT middle session's one thing,
    after R30 implementation and its independent review.  Do not auto-drain R20..F6-R2.
Product evidence added this lap: zero.  laps 261-268 have all gone to the historical probe's
test-of-a-test; that warning in STATUS remains valid and items 3/4 are the way out.

--- previous escalation preserved verbatim below ---

lap=267
role=Astra major direction / master-plan -> fresh middle Sol/high escalation
status=BLOCKED_PENDING_MIDDLE_REVIEW; R29 FAIL and R6-B-R2 contract conflict preserved.

Review docs/history/laps/20260912_lap267_astra_priority_handoff.md and docs/STATUS.md.
Verify R30B evidence scope (known mutations only), confirm bounded test-only work handoff,
and preserve R29 rejection until fresh work and independent next-session review succeed.
After bounded repair, prioritize S1/F2-R2 research design over automatic offline queue draining.
Reconcile count 1->0 evidence for upper-tier adjudication; do not silently change semantics.
No game/runtime authorization, no milestone closure, no implementation by this strategy session.
User explicitly requested ESCALATE_SOL on failed verification/conflicting implementation grounds.
Existing documents select Opus5 middle; this session's explicit Sol escalation takes precedence
for this handoff only. No provider configuration or model was silently substituted or launched.

--- previous escalation preserved verbatim below ---

lap=266 (counter file `loop/.lap_counter`; agent only read it.  This lap ran the queued middle-tier
independent review of R29.)
role=middle (diagnosis / plan / confirm) -> handoff to work tier, plus one open question for strategy
status=R29 range approval REFUSED (FAIL, coverage).  R29 is a real improvement and need not be
reverted, but the defect class it was meant to close is still open.

Verdict: R29 (anchoring `_review_body_lines()` at the first top-level `NEGATIVE_PATTERNS` assign
through the AST-located `json.dump`) does kill the lap264 M7 survivor, and C4 attributes that kill
to the anchor change specifically: reverting only the anchor to R28's preflight-relative form brings
M7 back to 8 passed.  Two secondary findings:
- R29's own `assert review_start < report_write_line` carries zero load in the current matrix -
  removing just that assert still kills M2/M3/M6/M7.  lap265's C4 stripped only the guard, so its
  attribution claim was incomplete.
- A new mutant M8 survives at 8 passed.  M8 = M7 composed with a benign refactor (rename
  `NEGATIVE_PATTERNS` -> `NEG_PATTERNS_SRC`, add a decoy alias just above the report write).  The
  shipped helper's body shrinks to 5 lines of which 0 execute, so `assert not (body & seen)` is
  vacuous again, while 171/231 module-level review lines run before the refusal (baseline refusal
  runs 15).  Renames alone are an accepted survivor class (M1), so this is a genuine coverage gap.

Root cause of lap262/264/266: the body is derived as a line interval between two *movable* anchors
and the start anchor takes `next()` (first match), which a decoy can capture.

Next work item R30 - already measured in throwaway mirrors this lap so the work tier does not have
to guess:
- REJECTED variant A: "every top-level statement that is not import/def/class/docstring/preflight
  If".  M0 control is 1 failed - the probe legitimately runs 14 module setup statements (15 lines)
  before the preflight, so this is a false positive.
- ADOPT variant B: body = union of **all** top-level statements assigning any named review result
  (`NEGATIVE_PATTERNS`, `both_negative`, `synthetic`, `grid_total`, `surgicality`, `waits`,
  `report`) plus **all** `json.dump` lines, with an assertion that every name was found.  A union is
  monotone: relocating the preflight cannot remove a member and a decoy can only add one.
  Measured: M0 8 passed, survivors `[M1_rename_only]`, M2/M3/M6/M7/M8 each 1 failed / 7 passed.
Ship condition for R30: those exact numbers, R17 remains the sole killer, `make check` 279 passed,
and no change to the SUT probe or protected assets.

Open question for strategy (Astra / user), not decided here: lap262, lap264 and lap266 have all
gone to hardening a test-of-a-test over the lap228 historical probe while G1~G4 product evidence
stays at zero and Stage B is blocked by S1/F2-R2.  After R30 the offline queue still holds
R20~R24 and F2-R1/F3-R1/F3-R2/F6-R2.  Whether to keep draining that queue or to escalate the S1
scene/slot determinism adjudication first is a strategy-tier call.

Validation this lap: `make check` 279 passed; Ruff/compileall/mypy 10 files; `CONTEXT_PASS`;
`SAFETY_PASS`.  No game, Wine, Xvfb or PNG.  Shipped code and tests were NOT modified: test SHA
`59538c0e1778b9c09ff6e83207123a89229f3001d351a873af2b194e72ec8957`, SUT probe SHA
`16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`, `tools/runtime_env.py` SHA
`e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`, original EXE pin
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` - all unchanged and matching
lap265's recorded values.  New review artifacts are uncommitted:
`docs/history/laps/20260912_lap266_middle_r29_review.md`,
`docs/history/laps/probes/20260912_lap266_r29_review_probe.py` (+ `_report.json`),
`..._lap266_r30_feasibility_probe.py` (+ `_report.json`),
`..._lap266_r30b_feasibility_probe.py` (+ `_report.json`),
`docs/history/laps/20260912_status_lap266_compaction.md`.

This is machine stage-1 evidence, not product G1 evidence or user approval.  Stage B / game remains
blocked by S1/F2-R2 and R6-B-R2.

--- previous escalation preserved below ---

lap=265 (counter file `loop/.lap_counter`; agent only read it.  This lap completed the queued R29 work.)
role=work (hands-on implementation) -> handoff to middle tier
status=R29 implemented and fresh machine validation passed; independent middle range review is required.

Result: the test-only R29 repair anchors `_review_body_lines()` from the first review computation
(`NEGATIVE_PATTERNS`) through the independently located `json.dump` write, removing dependence on
the preflight If position.  Targeted C0 is 8 passed.  Fresh depth-matched throwaway mutation results:
- M0 control: 8 passed.
- M1 rename-only: 8 passed, survives as intended.
- M2 late-refusal, M3 late-refusal+rename, M6 relocated-preflight, M7 preflight-inside-body:
  each 1 failed / 7 passed; survivors are only M1.
- C4: removing R17 makes all four defect mutants 7 passed; removing the R29 guard leaves each
  defect mutant at 1 failed / 7 passed.  Existing R7/R10/R11/R15/R25/R26/R27 were not changed.

Validation: `make check` 279 passed; Ruff/compileall/mypy 10 files; `CONTEXT_PASS`; safety
`SAFETY_PASS`.  SUT probe SHA `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`,
runtime SHA `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`, original EXE pin
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` unchanged.  Only
`tests/test_review_probe_output.py` changed (SHA `59538c0e1778b9c09ff6e83207123a89229f3001d351a873af2b194e72ec8957`),
uncommitted; no game/Wine/Xvfb/PNG.

This is machine stage-1 evidence, not product G1 evidence or user approval.  Next middle tier must
independently review R29's M0/kill attribution and regression non-weakening; if approved, proceed to
R20.  Stage B/game remains blocked by S1/F2-R2 and R6-B-R2.

--- previous escalation preserved below ---

lap=264 (counter file `loop/.lap_counter`; agent only read it.  The loop header said lap=263 and
lap263 is already recorded as the work lap, so loop/PROMPT.md's counter-file rule makes this 264.)
role=middle (diagnosis/plan/confirm) -> handoff to work tier
status=lap263 work's escalation to the middle tier is RESOLVED.  R28 is REJECTED; R29 is queued.

Result: **R28 range approval FAIL (coverage).  Machine stage-1 only.**  Independently re-measured
with a new probe (`docs/history/laps/probes/20260912_lap264_r28_review_probe.py`, report
`..._lap264_r28_review_report.json`), not by re-running lap263's conclusions:
- C0 8 passed in the real repository.
- C1 contract re-derived without importing the shipped test helper: exactly one top-level
  `__name__` If, lines 123-130; review body = lines 137-426 (262 lines); the `json.dump` report
  write is line 412 and is inside that set.  Live positive control: the successful run executes
  205 of the 262 body lines.  Negative control: refusal run rc 2, 0 body lines, message present,
  evidence preserved.
- C2 depth-matched mirror M0 = 8 passed = the real repository result.
- C3 six mutations, scope = R17/R28:
    M1 rename `drive_wait` only (no defect)            -> 8 passed, SURVIVES as intended, 0 kills
    M2 neuter only the early exists() refusal          -> killed by R17 ALONE (1 failed / 7 passed)
    M3 = M2 + rename `drive_wait`                      -> killed by R17 ALONE (1 failed / 7 passed)
    M6 = M2 + move the first `__name__` If below body  -> **killed (R28 works on this one)**
    M7 = move the WHOLE preflight block to just ABOVE the report write -> **8 passed, SURVIVES**
- C4 load-bearing: deleting only the R28 guard revives M6 and M7 while M2/M3 still die; deleting
  only the R17 test revives M2/M3/M6/M7.  R7/R10/R11 and R15/R25/R26/R27 were not weakened.

What R28 genuinely achieved and R29 MUST NOT regress: the lap262 survivor M6 now dies, and C4
attributes that kill to R28 alone.  M1 (rename only) still survives with no false alarm.

Why it is still rejected: the anchor is still POSITIONAL.  `_review_body_lines()` derives the body
from wherever the first top-level `__name__` If happens to sit.  R28 only detects the case where
that move leaves the set empty or drops the `json.dump` line.  Moving the preflight INTO the body
-- below the review computation but ABOVE the report write -- keeps the set non-empty AND keeps
the anchor inside it, so both new assertions pass and `not (body & seen)` is vacuous again.

Measured, not argued.  M7 relocates lines 123-130 (`if __name__ == "__main__": args = parse_args();
refusal = output_refusal(...)` plus its `else`) to immediately above the line-410 `try:` that writes
the report.  `output_refusal` itself is untouched; the defect is created by position alone -- which
is also the most natural refactor a developer would make ("check the output path right before
writing it").  Direct trace of the refusal path, mutant line numbers mapped back to baseline:
  M7 refusal path -> **198 of 262 baseline review-body lines executed before refusing**, rc 2
  shipped `_review_body_lines()` on M7 -> **17 lines, non-empty, containing the 412 anchor**
  full suite -> **8 passed**
  (contrast M6: helper returns 0 lines -> the R28 non-empty assertion kills it.)
The exact defect R17 exists to catch is present and the regression stays silent.  This is the same
coverage-failure class rejected at lap254 (M4), lap258 (M5) and lap262 (M6).

- `make check` 279 passed; Ruff/compileall/mypy 10 files; `CONTEXT_PASS`; `SAFETY_PASS`.
- No game, Wine, Xvfb or PNG.  Every mutation ran in a throwaway /tmp depth-matched mirror.
  SUT/test unchanged across the review: `tests/test_review_probe_output.py` sha256
  `df93939f87fdd86f207bb2da16f6300aa639cb1d1b857b1c3e23067b7bc218c2` (matches lap263's recorded
  value); `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py` sha256
  `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`; `tools/runtime_env.py` sha256
  `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`; original EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` unchanged.  Uncommitted,
  `LOOP_ALLOW_COMMITS=0`.

This is a machine (stage-1) rejection.  It is not G1 product evidence and not a user milestone
approval.

What the next work tier (Luna or Sonnet5/high) must do, without the game -- **R29**:
1. Stop deriving the body set from the preflight's position.  Either (a) independently identify the
   FIRST top-level statement of the review computation (currently the `NEGATIVE_PATTERNS`
   assignment at line 137) and assert `body_lines` covers everything from there through the report
   write, so relocating the preflight cannot shrink the set; or (b) assert the observation directly
   -- e.g. no traced line above `preflight_end` may execute on the refusal path.
2. Ship it so that **M7 dies**, **M6 still dies**, **M1 still survives** (rename alone stays a
   non-event) and **M2/M3 are still killed by R17 alone**, with an M0 control recorded.
3. Do not weaken or delete the existing R7/R10/R11/R15/R25/R26/R27 regressions.  If you conclude
   the SUT probe (not just the test) must change, record the justification and hand back to middle.
Then the queue is R20 -> R21 -> R22 -> R23 -> R24 -> F2-R1 -> F3-R1 -> F3-R2 -> F6-R2.

Method note (unchanged, still applies): deleting the `if path.exists():` lines outright also changes
the OSError classification for a non-searchable parent (0o600), so an R10 test dies too and kill
attribution is contaminated.  Use `if path.exists() and False:` to keep the call and the
classification while isolating the "body runs before the refusal" defect.

Still escalated above this tier (unchanged, needs Astra/user): S1/F2-R2 scene and slot
determinism, and R6-B-R2.  Stage B, game, Wine and Xvfb stay forbidden until that is re-decided.

--- previous escalation preserved below ---

lap=262 (counter file `loop/.lap_counter`; agent only read it. The loop header said lap=261 and
lap261 is already recorded as the work lap, so loop/PROMPT.md's counter-file rule makes this 262.)
role=middle (diagnosis/plan/confirm) -> handoff to work tier
status=lap261 work's escalation to the middle tier is RESOLVED. R19 is REJECTED; R28 is queued.

Result: **R19 range approval FAIL (coverage). Machine stage-1 only.** Independently re-measured
with a new probe (`docs/history/laps/probes/20260912_lap262_r19_review_probe.py`, report
`..._lap262_r19_review_report.json`, exit 0), not by re-running lap261's conclusions:
- C0 8 passed in the real repository.
- C1 contract re-derived without importing the shipped test helper: the `__name__` preflight If
  ends at line 130, the review-body set is lines 137-426 (262 lines, non-empty, containing both
  the `drive_wait` def at 326 and the report write at 426).  Live-detector positive control: the
  successful path really executes 205 of those 262 lines.  Refusal negative control: rc 2, 0 body
  lines executed, message present, file preserved.
- C2 depth-matched mirror M0 = 8 passed = the real repository result.
- C3 six mutations, scope = the single R17 regression:
    M1 rename `drive_wait` only (no defect)      -> 8 passed, SURVIVES as it should, 0 kills
    M2 neuter only the early exists() refusal    -> killed by R17 ALONE (1 failed / 7 passed)
    M3 = M2 + rename `drive_wait`                -> killed by R17 ALONE (1 failed / 7 passed)
    M4 delete the whole early refusal block      -> killed, 4 out-of-scope (R10 family)
    M5 early refusal exits 0                     -> killed, 5 out-of-scope
    M6 = M2 + move the first top-level `__name__` If below the review body -> **8 passed, SURVIVES**
- C4 load-bearing: deleting only the R17 regression revives M2 and M3 (7 passed each); M4/M5 still
  die on R10/R7.  R19 did not weaken the existing R7/R10/R11 coverage.

What R19 genuinely achieved and the next work tier MUST NOT regress: M3 is decisive.  With
`drive_wait` renamed, the late-refusal defect is still killed by R17 alone -- a mutant the lap244
name-set anchor would have let through.  M1 (rename only) survives with no false alarm.  The
"anchor to behaviour, not to the identifier" requirement itself is met.

Why it is still rejected: the anchor moved from a function name to an AST position, and nothing
asserts that position is still meaningful.  `_review_body_lines()` takes the FIRST top-level
`ast.If` comparing `__name__` as its boundary and returns the lines after it.  Move that If below
the body and the set becomes EMPTY, so `assert not (_review_body_lines() & seen)` is vacuously
true.  The test never asserts the set is non-empty.

Measured, not argued.  M6 rewrites `if __name__ == "__main__":` as `_IS_MAIN = __name__ ==
"__main__"` / `if _IS_MAIN:` (keeping the early classification path intact), appends an idiomatic
`if __name__ == "__main__":` tail, and injects the same late-refusal defect as M2.  Direct trace:
  mirror baseline refusal path -> 0 of 262 review-body lines executed, rc 2
  M6 refusal path              -> **196 of 262 review-body lines executed before refusing**, rc 2
  shipped `_review_body_lines()` on M6 -> **0 lines**; full suite -> **8 passed**
The exact defect R17 exists to catch is present and the regression passes.  This is the same
coverage-failure class rejected at lap254 (M4 survivor) and lap258 (M5 survivor).

- `make check` 279 passed; Ruff/compileall/mypy 10 files; `CONTEXT_PASS`; `SAFETY_PASS`.
- No game, Wine, Xvfb or PNG.  SUT unchanged across the review:
  `tests/test_review_probe_output.py` sha256
  `f5a0384eb31c637bd6c92c0142328fcd046b9a39eec3958d3eb9b846ab82c8f0` (matches lap261's recorded
  value); `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py` sha256
  `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`; `tools/runtime_env.py` sha256
  `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`; original EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` unchanged.  Uncommitted,
  `LOOP_ALLOW_COMMITS=0`.

This is a machine (stage-1) rejection.  It is not G1 product evidence and not a user milestone
approval.

What the next work tier (Luna or Sonnet5/high) must do, without the game -- **R28**:
1. Make the derived review-body set non-vacuous by construction.  Assert it is non-empty AND pin
   at least one independently known late anchor into it (for example the report-write statement,
   or the last top-level statement line), so a restructure that empties the set fails loudly
   instead of silently passing.
2. Ship it so that **M6 dies** while **M1 still survives** (renaming alone must stay a non-event)
   and **M2/M3 are still killed by the R17 regression alone**, with an M0 control recorded.
3. Do not weaken or delete the existing R7/R10/R11/R27/R26/R25/R15 regressions.  If you conclude
   the SUT probe (not just the test) must change, record the justification and hand back to middle.
Then the queue is R20 -> R21 -> R22 -> R23 -> R24 -> F2-R1 -> F3-R1 -> F3-R2 -> F6-R2.

Method note for the next mutation harness (round-1 contamination, preserved as
`..._lap262_r19_review_probe_round1.py` / `..._report_round1.json`): deleting the
`if path.exists():` lines outright also changes the OSError classification for a non-searchable
parent (0o600), so an R10 test dies too and kill attribution is contaminated.  Use
`if path.exists() and False:` to keep the call and the classification while isolating the
"body runs before the refusal" defect.

Still escalated above this tier (unchanged, needs Astra/user): S1/F2-R2 scene and slot
determinism, and R6-B-R2.  Stage B, game, Wine and Xvfb stay forbidden until that is re-decided.

--- previous escalation preserved below ---

lap=260 (counter file; agent only read it. Loop header said lap=259; loop/PROMPT.md makes the
counter file authoritative. lap258 is already used by both a middle and a work record, so 259 is
empty and this lap is 260.)
role=middle (diagnosis/plan/confirm) -> handoff to work tier
status=lap258 work's escalation to the middle tier is RESOLVED. R27 is APPROVED (machine stage 1).
R19 is the next work item.

Result: **R27 range approval PASS, machine stage-1 only.** Independently re-measured with a new
probe (`docs/history/laps/probes/20260912_lap260_r27_review_probe.py`, report `..._report.json`,
exit 0), not by re-running lap258's conclusions:
- C0 14 passed / 130 deselected.
- C1 160-case independent matrix (stage x5, stage_started {None,0.0,4.25,100.0}, offset x8),
  0 mismatches, expectation model written from the contract, all four states observed, all 160
  classified UNKNOWN_STATE_READ_FAILURE.  Calling the reader with the production defaults
  (stage="production", stage_started omitted) measures `stage_budget=None`,
  `stage_started_elapsed=None`, `stage_budget_state=STAGE_BUDGET_UNAVAILABLE`.  The call site
  still passes no `stage_started` and `G1_INPUT_STAGE_BUDGETS` still has no production entry, so
  lap258's reachable-shape claim holds.
- C2 depth-matched mirror M0 = 144 passed = the real repository result.
- C3 twelve mutations; all eleven viable ones die, **0 survivors, 0 out-of-range kills**.  The
  lap258 survivor **M5 (priority reorder) now dies, and its only killer is the R27 regression**.
  M12 (give production a 10.0s budget) is not a viable mutant: the 31.5s
  `G1_INPUT_STAGE_BUDGET_TOTAL` guard rejects it at import, so an equivalent within-cap variant
  M12b (`"production": 1.5`) was run instead and killed 3 tests.
- C4 load-bearing check: deleting **only** the R27 regression revives M5, M6, M10 and M11, while
  M1/M2/M3/M4/M7/M8/M9 still die on the R26 regression.  R27 carries new weight and the
  R26/R25/R15 coverage was not weakened.
- `make check` 279 passed; Ruff/compileall/mypy 10 files; `CONTEXT_PASS`; `SAFETY_PASS`.
- No game, Wine, Xvfb or PNG. SUT unchanged across the review: `tools/runtime_env.py` sha256
  `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`; `tests/test_runtime_env.py`
  sha256 `eaa50b919e42dd051044d4551cb2df923dd455035214200e741745e9bc15eae3`; original EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` unchanged. Uncommitted,
  `LOOP_ALLOW_COMMITS=0`.

This is a machine (stage-1) range approval only. It is not G1 product evidence and not a user
milestone approval.

What the next work tier (Luna or Sonnet5/high) must do, without the game -- **R19**:
1. R17's regression is anchored to the single function name `drive_wait` (lap244).  Renaming that
   helper would silently drop the early-rejection coverage.  Anchor the regression to behaviour,
   not to the identifier, so a rename cannot delete the check.
2. Ship mutations-killing regressions the way R25/R27 did, and record an M0 control.
3. Do not weaken or delete the existing R27/R26/R25/R15 regressions.  If you conclude SUT logic
   (not just the tests) must change, record the justification and hand back to middle.
Then the queue is R20 -> R21 -> R22 -> R23 -> R24 -> F2-R1 -> F3-R1 -> F3-R2 -> F6-R2.

Noted for R23/R24: `stage_budget_state` has zero consumers outside `tools/runtime_env.py`, the
same unconsumed-provenance risk already queued for `read_coverage` and `read_failure`.  It is out
of R27's scope and is not a rejection reason.

Still escalated above this tier (unchanged, needs Astra/user): S1/F2-R2 scene and slot
determinism, and R6-B-R2. Stage B, game, Wine and Xvfb stay forbidden until that is re-decided.

--- previous escalation preserved below ---

lap=258 (counter file; agent only read it. Loop header said lap=257; loop/PROMPT.md makes the
counter file authoritative and lap257 is already recorded, so this lap is 258.)
role=middle (diagnosis/plan/confirm) -> handoff to work tier
status=lap257's escalation to the middle tier is RESOLVED. R26 is REJECTED; R27 is queued.

Result: **R26 range approval FAIL (coverage). Machine stage 1 only.** Independently re-measured
with a new probe (`docs/history/laps/probes/20260912_lap258_r26_review_probe.py`, report
`..._report.json`, exit 0), not by re-running lap257's conclusions:
- C0 14 passed / 130 deselected.
- C1 160-case independent matrix, 0 mismatches, expectation model written from the contract; all
  four states observed; classification is UNKNOWN_STATE_READ_FAILURE in all 160 cases.
- C2 depth-matched mirror M0 = 144 passed = the real repository result.
- C3 eight mutations, **one survivor (M5)**, 0 out-of-range kills. Constant-pinned states,
  state collapses and the `>=` boundary all die on the new R26 regression; reordering the
  priority so `stage_started is None` is checked before `stage_budget is None` does not.
- M5 is not theoretical. `tools/runtime_env.py:2636` calls the production stage without
  `stage_started`, and `production` has no configured budget, so `(budget None, start None)` is
  the only production-reachable shape. Measured: it currently reports
  `STAGE_BUDGET_UNAVAILABLE`; under M5 it reports `STAGE_START_UNKNOWN` with all 144 tests green.
  R26's only production case pins `stage_started=0.0`, which never occurs at that call site.
- `make check` 279 passed; Ruff/compileall/mypy 10 files; `CONTEXT_PASS`; `SAFETY_PASS`.
- No game, Wine, Xvfb or PNG. SUT unchanged across the review: `tools/runtime_env.py` sha256
  `f54932b50c6de5c575699ade11947fcea93219ab7a8b2a69e845137b301dfec4`; `tests/test_runtime_env.py`
  sha256 `96e4c0916dc4c1ac1565615cd6a5ba2ae709a2ca5d8ebbb1fdeef6890e552838`; original EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` unchanged. Uncommitted,
  `LOOP_ALLOW_COMMITS=0`.

This is a machine (stage-1) rejection. No product G1 evidence and no user milestone approval.

What the next work tier (Luna or Sonnet5/high) must do, without the game -- **R27**:
1. Add a regression for the production-reachable `(no stage budget, stage_started=None)` shape
   pinning `STAGE_BUDGET_UNAVAILABLE`, so the priority-reorder mutation dies.
2. Record the contract that `STAGE_BUDGET_UNAVAILABLE` outranks `STAGE_START_UNKNOWN`.
3. Do not weaken or delete the existing R26/R25/R15 regressions. If you conclude the SUT logic
   (not just the tests) must change, record the justification and hand back to middle.
Then the queue is R19 -> R20 -> R21 -> R22 -> R23 -> R24 -> F2-R1 -> F3-R1 -> F3-R2 -> F6-R2.

Still escalated above this tier (unchanged, needs Astra/user): S1/F2-R2 scene and slot
determinism, and R6-B-R2. Stage B, game, Wine and Xvfb stay forbidden until that is re-decided.

--- previous escalation preserved below ---

lap=257 work result (counter file; agent only read it)
role=work (hands-on implementation) -> handoff to middle tier
status=R26 implementation is complete; independent middle review is required.

Result: **R26 work PASS, machine stage 1 only.** `_g1_read_selection_stage` now emits the explicit
`stage_budget_state` values `WITHIN_STAGE_BUDGET`, `STAGE_BUDGET_EXHAUSTED`, `STAGE_START_UNKNOWN`,
and `STAGE_BUDGET_UNAVAILABLE`, while preserving the legacy boolean and timing/null provenance.
Targeted regression: 5 passed; depth-matched mirror M0: 5 passed; a constant state mutation and an
unknown-state-collapsing mutation each failed 3 tests. `make check` 279 passed, Ruff/compileall/mypy
10 source files, `CONTEXT_PASS`, and `SAFETY_PASS`. No game/Wine/Xvfb/PNG; original EXE pin and
protected assets are unchanged; uncommitted because `LOOP_ALLOW_COMMITS=0`.

The next middle tier (Claude Code `claude-opus-5`/high) must independently verify the R26 semantic
cases, M0 control, and mutation kills, then approve or reject the range. Product G1 evidence and
user milestone approval remain absent. After approval, the next queue item is R19. S1/F2-R2 and
R6-B-R2 remain escalated to Astra/user; Stage B and game execution remain forbidden until re-decided.

--- previous escalation preserved below ---

lap=256 (counter file; agent only read it. Loop header said lap=255; loop/PROMPT.md makes the
counter file authoritative, and lap255 is already recorded, so this lap is 256.)
role=middle (diagnosis/plan/confirm) -> handoff to work tier
status=lap255's escalation to the middle tier is RESOLVED. Its original text is preserved verbatim
in the appendix of `docs/history/laps/20260912_lap256_middle_r25_review.md`.

Result: **R25 independently verified PASS; the R15 range is APPROVED (machine, stage 1).**
Independently re-measured with a new probe
(`docs/history/laps/probes/20260912_lap256_r25_review_probe.py`, report `..._report.json`,
exit 0), not by re-running the lap254/lap255 probe conclusions:
- C0 16 passed / 128 deselected (R25 + R15 + direct-reader-adjacent tests).
- C1 105-case independent matrix, 0 mismatches, expectation model written from the contract.
- C2 depth-matched mirror M0 = 144 passed (equals the real repository result).
- C3 nine mutations, 0 survivors, 0 out-of-range kills. The lap254 survivor M4 (stage flag pinned
  True) now dies on 3 cases; new M6/M7 kill only the exact-boundary case, M8 only the unknown
  `stage_started` case, M9 only the unknown-budget case; M1/M2/M3/M5 still kill the R15 test.
  All four R25 cases are individually load-bearing and all four R15 provenance fields plus the
  classification priority are now covered.
- `make check` 279 passed; Ruff/compileall/mypy 10 files; `CONTEXT_PASS`; `SAFETY_PASS`.
- No game, Wine, Xvfb or PNG. SUT unchanged: `tools/runtime_env.py` sha256
  `0e3bf38220e8b762b2ba3b38d2151cfb51a6e8d4a6b85fd03fba6c41b89cb83c`; `tests/test_runtime_env.py`
  sha256 `40c91b76e59c9f23b7256a0cb7b591deb028d78c9bf8d67793566a44d292a7df`; original EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` unchanged. Uncommitted,
  `LOOP_ALLOW_COMMITS=0`.

This is a machine (stage-1) range approval only. It is not G1 product evidence and not a user
milestone approval.

What the next work tier (Luna or Sonnet5/high) must do, without the game:
1. Repair **R26**: `stage_budget_exhausted=false` still collapses three distinct states -- inside
   budget, unknown `stage_started`, and no stage budget. lap256 truth table reconfirms it. Give the
   consumer a single field (or a documented contract) that distinguishes them.
2. Ship regressions that kill constant-pinned and state-collapsing mutations for the new field, the
   way R25 did for `stage_budget_exhausted`.
3. Do not change SUT logic without recorded justification; hand back to middle if you conclude a
   logic change is needed. Then the queue is R19 -> R20 -> R21 -> R22 -> R23 -> R24 -> F2-R1 ->
   F3-R1 -> F3-R2 -> F6-R2.

Still escalated above this tier (unchanged, needs Astra/user): S1/F2-R2 scene and slot determinism,
and R6-B-R2. Stage B, game, Wine and Xvfb stay forbidden until that is re-decided.
lap=258
role=work (hands-on implementation) -> handoff to middle tier
status=R27 implementation complete; independent middle review required.

Result: **R27 work PASS, machine stage-1 only.** Added a regression exercising the actual production
call shape `(stage_budget=None, stage_started=None)` and pinning
`stage_budget_state="STAGE_BUDGET_UNAVAILABLE"`. Added an implementation comment documenting that
configured-budget unavailability outranks unknown stage start. SUT logic and existing R26/R25/R15
regressions were not changed or weakened.

Evidence:
- targeted R27/R26/R15: `6 passed, 138 deselected`.
- `make check`: `279 passed`; Ruff/compileall/mypy 10 source files; `CONTEXT_PASS`.
- `LOOP_DRY_RUN=0 bash checks/safety.sh check`: `SAFETY_PASS`.
- no game/Wine/Xvfb/PNG; original EXE pin and protected assets unchanged; uncommitted,
  `LOOP_ALLOW_COMMITS=0`.

The next middle tier (Claude Code `claude-opus-5`/high) must independently verify the production-shape
regression kills the priority-reorder mutation, preserve R26/R25/R15 coverage, run an M0 control and
fresh Fast checks, then approve or reject R27. Product G1 evidence and user milestone approval remain
absent. S1/F2-R2 and R6-B-R2 remain escalated above this tier; Stage B/game/Wine/Xvfb stay forbidden.

--- prior escalation preserved below ---
lap=261 (counter file; agent only read it. loop/PROMPT.md makes the counter file authoritative.)
role=work (hands-on implementation) -> handoff to middle tier
status=R19 implementation is complete; independent middle review is required.

Result: **R19 work PASS, machine stage-1 only.** The shipped regression no longer depends on the
`drive_wait` helper name. It derives top-level review-body lines from the SUT AST and uses a fresh
line-trace run to assert that an existing-evidence refusal exits before any such line executes.

Evidence:
- targeted `tests/test_review_probe_output.py`: **8 passed**.
- Existing lap244 R10 reverify harness, with fresh output, reports classification/earliness/
  mutation/semantics defects 0 and `verdict=PASS`; its M0 control remains green.
- New probe `docs/history/laps/probes/20260912_lap261_r19_work_probe.py`: M0 **8 passed**;
  M1 (rename `drive_wait` and remove the early refusal) **5 failed**, including the R17 regression.
- `make check`: **279 passed**, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`;
  `LOOP_DRY_RUN=0 bash checks/safety.sh check`: `SAFETY_PASS`.
- `tools/runtime_env.py` sha256 `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`
  and original EXE pin `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` unchanged.
  No game/Wine/Xvfb/PNG; uncommitted, `LOOP_ALLOW_COMMITS=0`.

This is a machine (stage-1) work result, not G1 product evidence or user milestone approval.

What the next middle tier (Claude Code `claude-opus-5`/high) must do:
1. Independently inspect the AST/line-trace contract and confirm the guard is behavior-anchored,
   not helper-name anchored.
2. Re-run fresh M0 and the combined rename+early-refusal deletion mutation; preserve existing
   R27/R26/R25/R15 coverage and reject any weakened range.
3. Record range approval or a concrete blocker. If approved, the next work item is R20.

Stage B, game, Wine and Xvfb remain forbidden by STATUS until S1/F2-R2 is re-decided.

--- previous escalation preserved below ---
lap=263 (counter file; agent only read it)
role=work (hands-on implementation) -> handoff to middle tier
status=R28 implementation complete; independent middle review is required.

Result: **R28 machine stage-1 PASS.** `tests/test_review_probe_output.py` now asserts that the
AST-derived review-body line set is non-empty and contains the independently identified
`json.dump` report-write anchor. This prevents R19's vacuous pass if the `__name__` preflight is
moved below the review body.
- targeted C0/M0: 8 passed
- mutation checks in a fresh `/tmp` mirror including `tools/`: M1 rename-only 8 passed (survives);
  M2/M3 late-refusal each 1 failed/7 passed (R17-only kills); M6 relocated-preflight 1 failed/7
  passed (R28 guard kill). Removing only R17 makes M2/M3/M6 each 7 passed.
- `make check`: 279 passed; Ruff, compileall, mypy 10 files, `CONTEXT_PASS`; separate safety
  check `SAFETY_PASS`. No game/Wine/Xvfb/PNG. SUT/protected original SHA unchanged and all work
  is uncommitted (`LOOP_ALLOW_COMMITS=0`).
lap=289
role=work (hands-on implementation/verification; configured route Codex gpt-5.6-luna/high)
status=ESCALATED: 필수 fresh cross-probe 대조 중 lap280이 예상 밖 traceback/exit1. 현재 work
정정과 성공한 증거는 보존했으며, 실패한 검증은 재시도하지 않고 다음 승격 작업자에게 넘긴다.
target=G1 S1 저장 serializer offline 경계 정정1, 제품 G1/runtime/Stage B 아님
record=docs/history/laps/20260912_lap289_work_save_layout_boundary_repair.md
changed=docs/history/laps/probes/20260912_lap284_work_save_layout_probe.py
evidence=logs/lap289/work_save_layout_before.json, work_save_layout_after.json,
logs/lap289/lap279_serializer_rerun.json, lap284_middle_runtime_rerun.json,
logs/lap289/lap280_crossverify_rerun.stderr

이번 바퀴 변경:
- work probe의 `SAVE_END`를 `0x440FF0`에서 `0x440F5B` exclusive로 좁혔다.
- `FREAD=0x4DA4A9`와 save-window 호출 단언을 같은 work probe에 추가했다.
- 게임 코드/원본 EXE/fixture/하네스/PASS 규칙/baseline/golden은 변경하지 않았다.

성공한 검증:
- 수정 전·후 work probe 모두 exit0, `failures=[]`, JSON 바이트 동일 SHA
  `7381b5f7ebbc99a6a6d9e9cdc0ce95b3bcbaf6237645d521b83c59eba5cbfb81`.
  layer=28, roster=375/558/147/149.
- widened-window in-memory mutant(`SAVE_END=0x440FF0`)은 exit1이며
  `0x4da4a9 was included as a save fread target: ['0x00440fa4']`를 발화했다.
- lap279와 lap284 middle runtime probe는 각각 exit0 및 기존 출력과 바이트 동일.
- 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`와
  fixture 4종 SHA는 기록값과 일치. 원본/fixture 쓰기와 게임/Wine/Xvfb/Stage B 실행은 0.

필수 검증 실패:
- `.venv/bin/python docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`
  가 line 130의 `re.search(r"internal_id=i\(0x([0-9A-Fa-f]+)\)", src).group(1)`에서
  `NoneType` AttributeError로 exit1. 재시도하지 않았고 stderr를 보존했다.
- 따라서 `make check`/safety는 이 실패 뒤 실행하지 않았다. 이번 바퀴 최종 PASS나 카드 종결을
  주장하지 않는다.

다음 승격 작업자가 이어서 검증할 것:
1. lap280 probe line 130의 `internal_id` 정규식이 현재 source와 불일치하는 정확한 원인을
   원본 source/fixture/provenance와 대조해 진단한다. 원인 불명 상태에서 정규식을 임의 수정하지 않는다.
2. lap280 실패 원인을 해결할 권한/범위를 정한 뒤 fresh run으로 lap279/lap280/lap284-middle
   출력 불변 대조를 다시 수행하고, work 정정의 ACCEPT/REJECT를 판정한다.
3. 그 전까지 `make check`, Stage B, 게임/Wine/Xvfb, runtime 경로, PASS 규칙 변경 및 마일스톤
   승격은 금지한다. 기존 blocker와 lap288 provenance 경고는 유지한다.
```
