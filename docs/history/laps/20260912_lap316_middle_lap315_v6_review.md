# 2026-09-12 | lap 316 | G1 — lap315 R2 fail-open 수리 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, middle(중간 계획·컨펌).
  진단·검증·계획만 수행했고 게임 코드/패치는 건드리지 않았다.
- 가설 / 사용자 관찰: lap315의 D1/E1/E2 수리가 진짜면, lap315 코드를 **import하지 않고**
  다른 disassembly flavor(AT&T)·다른 바이트 출처(원시 PE)·다른 그래프 알고리즘(FIFO BFS + witness path)으로
  재유도해도 753/753/7/724·unresolved 0·writer 4·게이트/실패 arm 바이트가 그대로 나와야 한다.
- 예상 PASS / FAIL 조건: 원본 SHA 불변; 독립 수치가 lap315 주장과 **전부 일치**; 화면 전역 언급 census가
  직접 dword store 4건뿐(moffs/비-dword 0); PE 이미지에서 게이트 `750a`→`0x431afe`, 실패 arm 10바이트 연속;
  writer 4개를 전부 제거해도 entry→gate 경로가 남아 pre-gate 공허성이 **증인 경로**로 성립;
  lap315 probe를 서브프로세스로 2회 재실행한 stdout SHA가 저장 report와 byte-identical.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `docs/history/laps/probes/20260912_lap316_middle_lap315_v6_review_probe.py`
    SHA `6bc0923a896603ec26cd02f60fb33ae3f0a845422d50152e2a411d7f6aedcb80`.
  - `tests/test_lap316_middle_review_probe.py`
    SHA `f9c8c0b602eeb0646f583fcdf2913ea4db5ad3879aa87c91f61d5acd02613920`.
  - `logs/lap316/lap316_lap315_v6_review.json`
    SHA `c91a238b8345f74d5f435fa99c872aef99cb54dcb27c4b5861cd97ef141f3af5`.
  - `docs/history/laps/20260912_status_lap315_compaction.md` — 직전(lap315 작성) STATUS 원문 129줄,
    SHA `be21896782646ff197b239414a9677b73e9c1e9d5ecc9991588c33cbf53b533b` 보존 후 압축했다.
  - `docs/STATUS.md` 갱신(130줄, Blockers 정확히 1개). 커밋 없음(`LOOP_ALLOW_COMMITS=0`). lap313/314/315 파일·report·로그는 수정하지 않았다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `Syw2plus/syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  검수 전후 불변(워크스페이스 사본 `../Syw2plus/syw2plus_original.exe`도 동일 SHA). 후보 EXE·활성 플레이어·지도·군대 없음.
  Linux `.venv`, binutils objdump 2.42(AT&T) + `struct` 기반 PE 파서. 그래프 fixture는 손으로 답을 유도할 수 있는
  합성 CFG이며 실제 게임 fixture가 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python docs/history/laps/probes/20260912_lap316_middle_lap315_v6_review_probe.py` → exit 0,
    fresh 2회 stdout SHA 동일(`c91a238b…141f3af5`), 저장 로그와 byte-identical.
  - `.venv/bin/python -m pytest -q tests/test_lap316_middle_review_probe.py` → **9 passed**.
  - `make check` → **328 passed**, Ruff/compileall/mypy/CONTEXT_PASS; `bash checks/safety.sh check` → **SAFETY_PASS**.
  - 게임/Wine/Xvfb/Stage B/runtime/PNG/click 실행 **0**.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **ACCEPT-WITH-NOTES (1단 정적)**.
  - 독립 수치 일치: window **753**, entry-reachable **753**, 실패 arm **7**, 성공 arm **724**, unresolved **0**.
  - 화면 전역 census(어떤 operand 형태든 `0xe5bf1c`/`0xe5bf20` 언급): **4건 전부 직접 dword store**
    = `{0x431b79 (89 2d …, ebp), 0x431b7f (89 3d …, edi), 0x4324b8 (c7 05 …, 0x280), 0x4324c2 (c7 05 …, 0x1e0)}`,
    **moffs store 0**, 비-store 언급 **0**. lap306 R5·lap312 재확인과 일치한다.
  - 실패 arm writer **0**, 성공 arm writer **4**, 실패 arm은 성공 ret `0x4324d5`에 **미도달**.
  - **D1 공허성 독립 확인(다른 방법):** writer 4개를 전부 제거해도 `0x431ab0`→`0x431af2`의 **22-노드 증인 경로**가
    남는다 → 어떤 writer도 게이트를 지배하지 않으므로 pre-gate 집합이 비는 것은 사실이며 비교는 **공허**하다.
    22는 lap314의 node-cut 지배자 수 22와 교차 일치한다.
  - **PE 이미지 직접 판독(objdump 무관):** `0x431af2` = `75 0a` → rel8 taken `0x431afe`(= success join);
    `0x431af4`부터 **연속 10바이트** `5f5e5d33c05b83c434c3`(7개 명령, eax=0 후 ret); `0x4324b8`/`0x4324c2`의
    즉값은 `0x280`/`0x1e0` = **640×480**.
  - **objdump 바이트 컬럼 교차검증:** 창의 753개 명령 전부에서 (연속줄 재조립한) objdump 바이트 = PE 이미지 바이트,
    **불일치 0**.
  - lap315 재현성: 서브프로세스 2회 stdout SHA 동일 = 저장 report `ac0e1b7e…fc2bfa31`, exit 0. import 없음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 판정은 **정적 1단**이며 제품 증거가 아니다. 신규 검수 노트 3건:
  - **N1 — E1 수리는 실제 대상에서 무효(inert):** 지도 창에 간접 분기가 **0개**라 `unresolved_branches: []`는
    자명하게 참이다. E1은 회귀 가드일 뿐 바이너리에 대한 새 사실이 아니며, 합성 fixture만 이를 실행한다.
    "간접 분기를 확인했다"로 승격하지 않는다.
  - **F1 — lap315 바이트 컬럼 절단(신규, 현재 수치 영향 0):** objdump는 7바이트를 넘는 명령의 바이트를 다음 줄로
    접고, lap315의 `INSN_RE`는 탭이 하나뿐인 연속줄을 버린다. 창 안에서 **27개 명령**이 이에 해당하고 그중
    **`0x4324b8`·`0x4324c2`(10바이트 reset writer 2개)가 포함**된다. 현재 수집 구간(`0x431af4`+10B)에는 접힌
    명령이 없어 영향이 0이고, 접힌 명령이 들어오면 `cursor` 부족으로 **비연속 FAIL**이 나므로 fail-closed다.
    그러나 reset writer 바이트를 E2 방식으로 증명하려는 다음 작업은 **먼저 이 파서를 고쳐야** 한다.
  - **N2 — call 31개는 여전히 fall-through:** 창 안 call `0x431ae1`…`0x4324b0` **31개**를 따라가지 않으므로
    callee 쓰기와 cross-function event/thread 순서는 **UNKNOWN**이다(lap308·310·312·314와 동일한 한계).
  - 그 외 계산/간접 writer, WM_CLOSE, 실제 scene/input, G1~G4 제품 증거는 **0/UNKNOWN** 그대로다.
  - 사용자 마일스톤 승인 대기. 본 컨펌은 기술 판정이며 제품 합격이 아니다.
- 다음 한 가지: work tier(Luna/Sonnet5/high) handoff — **F1** 수리. lap315 방식의 `INSN_RE` 대신 연속줄을
  재조립하거나 PE 이미지에서 직접 읽어, `0x4324b8`/`0x4324c2`의 10바이트 reset store를 연속성 계약 아래
  보고하는 probe를 새로 만든다. 성공 조건: 두 writer의 바이트가 `c7051cbfe50080020000`/`c70520bfe500e0010000`로
  연속 수집되고, 기존 753/753/7/724·unresolved 0·writer 4가 불변이며, 접힌 명령 synthetic fixture가 fail-closed로
  검출된다. N1/N2는 수리 대상이 아니라 **기록된 한계**이며 승격 금지. 게임/Wine/Xvfb/Stage B/runtime/PNG/click 계속 금지.
