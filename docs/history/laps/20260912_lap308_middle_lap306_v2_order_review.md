# 2026-09-12 | lap 308 | G1 — lap306 work V2 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`, effort high, 지정 역할 **middle
  (진단·계획·확인)**. 게임 코드 hands-on 수정 없음. 정적 probe 작성·검증과 판정만 수행했다.
- 가설 / 사용자 관찰: lap306 work V2가 선언한 (a) `0x431AB0` allocator gate, (b) `0x431B79/7F` runtime
  writer의 성공 경로 한정, (c) `0x4324B8/C2` 640×480 reset의 `ret=1` 지배, (d) dialog `0x4D6312/1C` reader와
  `0x4D632A/48` origin store, (e) R3 `raw - depth` 회귀가 **V2 코드를 신뢰하지 않고** 원본에서 독립 재유도된다.
  V2의 게이트가 구조적으로 fail-open이거나 내부 모순이면 수치와 분리해 적시한다.
- 예상 PASS / FAIL 조건: 원본 SHA·V2 probe SHA·V2 report SHA가 고정값과 일치하고, 앵커 15개·caller 집합·
  return 집합·지배 관계가 자체 disassembly로 재현되며, 지적한 결함이 probe로 **재현 가능**하면 검수 PASS.
  cross-function 순서는 좁히지 않고 UNKNOWN으로 보존한다. 결함 발견은 수치 반증과 구분해 기록한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 새 probe
  `docs/history/laps/probes/20260912_lap308_middle_lap306_v2_order_review_probe.py` SHA
  `6718fbe100edc445f8a42207934c3ff5631ec09e93060a86691b72d7477f0bdb`; 새 report
  `logs/lap308/lap308_v2_order_review.json` SHA
  `c6c14a94ab82cd590a499742f87d91c1068341e745cc9e59bebac9bb1494c0d4` (= probe stdout 바이트 동일);
  이 이력 파일; STATUS 갱신. **커밋 없음**(`LOOP_ALLOW_COMMITS=0`). lap305/lap306 산출물은 **수정하지 않았다**.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `Syw2plus/syw2plus_original.exe`
  SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (검수 전후 불변).
  후보 EXE·활성 인원·지도·군대·fixture **없음**(정적 검수라 해당 없음). Linux `.venv` + `/usr/bin/objdump`.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap308_middle_lap306_v2_order_review_probe.py`
  fresh 2회, 두 exit `0`, stdout 4,999 B `cmp` **byte-identical**. V2 probe 독립 재실행도 exit `0`,
  stdout 4,739 B로 lap306 선언과 일치. `make check` → **292 passed**, Ruff/compileall/mypy/CONTEXT_PASS,
  `bash checks/safety.sh check` → **SAFETY_PASS**. PNG·게임·Wine·Xvfb·Stage B·runtime·클릭 실행 **0**.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **middle 판정 = ACCEPT-WITH-CORRECTION.**
  - **R1 재유도 CONFIRMED:** 앵커 15/15 일치(`0x431AE1/AEB/AF2/AF7/AFD`, `0x431B79/7F`,
    `0x4324B8/C2/CC/D5`, `0x4D6312/1C`, `0x4D632A/48`). `0x431AB0` direct caller = `0x48F538` 1개,
    `0x4D60B0` direct caller = `0x4D69E5/0x4D6A05` 2개, map 범위 `0x431AB0..0x4324D5` 내 ret 정확히 2개
    (`0x431AFD`, `0x4324D5`). 640×480 writer 2개 모두 성공 return `0x4324D5`를 **지배**(독립 dominator 구현).
  - **R2 FAIL-OPEN (수치 영향 0):** V2의 `runtime_on_failure`는 `reachable(map_graph, 0x431AFD)`로 계산하는데
    `0x431AFD`는 **`ret` 자체**라 successor가 공집합이고 결과는 **항상 `{0x431AFD}`** — 어떤 바이너리에서도
    `absent_on_failure_path=true`가 나오는 **공허한 게이트**다(probe가 재현). 올바른 seed는 `0x431AF2 jne`의
    fall-through `0x431AF4`이며, 실제 실패 경로는 `0x431AF4/F5/F6/F7/F9/FA/FD` 7개 명령뿐이고 runtime writer는
    **0개** → **V2의 결론 자체는 UPHELD**, 게이트만 무효.
  - **R3 ARTIFACT (수치 영향 0):** V2의 `stack_adjustment`는 **모든 `call`을 스택 중립**으로 본다. 그 모델에서
    join `0x465287` 깊이는 `{0x100, 0x104}`이고, 이 두 값은 join→ret가 직선 코드라 **유일한 ret `0x4652AE`에
    서로 다른 두 esp**로 도달한다(`{0x10, 0x14}`) — cdecl `ret` 하나가 가질 수 없는 상태다. 따라서
    `0x465284 call DWORD PTR [ecx+0x28]`은 **callee-clean(4바이트)**이어야 하고, 교정 모델에서 join 깊이는
    **`{0x100}` 단일**, ret 깊이도 단일(`{0x10}`, 잔여분은 이 probe가 모델링하지 않는 `0x46529D` import의
    stdcall 정리분이며 절대 0 주장은 하지 않는다). 결과적으로 V2가 고정한 PASS 값
    `depths={0x100,0x104}` / `entry_offsets(0x465287)={4,8}`은 **모델 산물**이고, 그중 `4`(arg1)는 join에서
    **허위 귀속**이다. **lap306 middle의 실질 결론 "`0x465250`이 arg1과 arg2를 읽는다"는 UPHELD** —
    arg1은 `0x46526D`(raw `0x110` − depth `0x10C` = 4)로 가상 호출과 무관하고, arg2는 교정 모델에서
    `0x465287` → `{8}`로 그대로 남는다. `[esp+reg*n]`류 미매칭 형식은 이 callee 범위에 **0건**(수치 영향 없음).
  - **R4 PROVENANCE GAP (수치 영향 0):** `logs/lap306/lap306_v2_mode_writer_order.json`(1,825 B)은 probe
    stdout(4,739 B)이 **아니라 손으로 옮겨 쓴 요약**이다 — V2 probe는 `print`만 하고 파일을 쓰지 않으며,
    report의 `fresh_runs`/`byte_compare`/`output_bytes` 키는 probe 소스에 **존재하지 않는다**. 즉 그 SHA는
    재현 가능한 생성기 출력이 아니라 전사본을 고정한다. 전사된 값은 이번에 전부 독립 재유도와 **일치**했다.
    이번 lap308 report는 이 함정을 피하려고 **probe stdout 그대로** 저장했고 해시가 동일함을 확인했다.
  - **R5 FAIL-OPEN (감사 한정):** V2는 dialog caller 집합에는 실패 단언이 있으나 **map entry caller 집합에는
    없다** — `0x431AB0` 호출자가 드리프트해도 V2 probe는 exit 0을 낸다.
  - **R6 provenance 표기 드리프트:** 러너 로그 `logs/laps/2026-09-12/lap-0307.log`(14:03, 1.4 MB)가 "lap306
    work V2" 세션이고 `lap-0308.log`(14:04, 0 B)가 이번 세션이다. 즉 V2의 report/probe/JSON이 자칭한
    `lap 306`은 **실제 러너 lap 307**이다. lap301의 `"lap": 299` 오기와 같은 계열이며 **고쳐 쓰지 않고
    보존**한다. 이번 lap 번호는 PROMPT.md ⓪ 규칙대로 `loop/.lap_counter` 값 **308**을 쓴다(주입된 runtime
    evidence 헤더의 `lap=307`과 불일치하므로 근거를 여기 남긴다).
  - **UNKNOWN 유지:** `0x48F538`(map caller)와 `0x4D69E5/0x4D6A05`(dialog caller) 사이 실제 event/thread
    순서는 direct call graph로 정해지지 않는다. 이번 검수는 이 경계를 **좁히지 않았다**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 정적 결과는 **G1 제품 PASS가 아니다**. 간접/virtual writer,
  실제 click-time mode, WM_CLOSE, scene/input 쌍은 여전히 미검증이고 G2~G4 증거는 0이다. `make check`/
  safety는 PASS지만 exit 0을 승인으로 쓰지 않는다. 사용자 마일스톤 승인 **없음**. middle은 수리 범위만 정하고
  구현은 work tier로 돌려보낸다.
- 다음 한 가지: **work tier(Luna/Sonnet5/high)에게 handoff** — R2·R3·R5를 **새 파일**에서 수리한다(lap305/
  lap306 산출물은 SHA 불변으로 보존). (1) 실패 경로 게이트를 `0x431AF4` seed로 재작성, (2) `stack_adjustment`
  에 호출 규약별 정리량을 넣고 "단일 ret에서 깊이 단일값" 불변식을 회귀로 추가한 뒤 `0x465287` 기대값을
  `{8}`로 재고정, (3) map entry caller 집합에 실패 단언 추가, (4) report를 손 전사 대신 probe stdout으로 생성.
  그 전까지 게임/Wine/Xvfb/Stage B/runtime/PNG/클릭 실행과 기존 산출물 수정은 계속 **금지**.

## 부록 — 이번 바퀴 파일 해시 (uncommitted, `LOOP_ALLOW_COMMITS=0`)

| 파일 | SHA256 | 상태 |
|---|---|---|
| `Syw2plus/syw2plus_original.exe` | `b56986e0…c9c08a8ac` | 불변(검수 전후 동일) |
| `docs/history/laps/probes/20260912_lap308_middle_lap306_v2_order_review_probe.py` | `6718fbe1…477f0bdb` | 신규 |
| `logs/lap308/lap308_v2_order_review.json` | `c6c14a94…1494c0d4` | 신규(= probe stdout 바이트 동일) |
| `docs/history/laps/20260912_lap308_middle_lap306_v2_order_review.md` | 이 파일 | 신규 |
| `docs/history/laps/20260912_status_lap308_compaction.md` | `abe14417…614d35d3d4` | 신규(STATUS 원문 `0045e732…a2750773`, 127줄 보존) |
| `docs/STATUS.md` | `0b6dcc07…087aeff7` | 압축 갱신(130줄, Blockers 섹션 1개) |
| `docs/history/laps/probes/20260912_lap306_work_v2_mode_writer_order_probe.py` | `c8ada3f9…ca5ca0c44` | **불변(수정 안 함)** |
| `logs/lap306/lap306_v2_mode_writer_order.json` | `9eb6913e…ba02014d` | **불변(수정 안 함)** |
| `docs/history/laps/probes/20260912_lap305_work_stack_argument_writer_probe.py` | `c151cc40…43e57b21` | **불변(수정 안 함)** |

압축 후 재검증: `make check` **292 passed** / Ruff / compileall / mypy 10 files / **CONTEXT_PASS**,
`bash checks/safety.sh check` **SAFETY_PASS**. exit 0을 승인으로 쓰지 않는다.
