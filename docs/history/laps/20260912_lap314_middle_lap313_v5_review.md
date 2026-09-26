# 2026-09-12 | lap 314 | G1 — lap313 D1~D4 수리 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, 지정 **middle(진단·계획·컨펌)**.
  게임 코드 hands-on 수정 없음. lap313 코드를 import하지 않는 새 review probe/테스트·기록만 작성했다.
- 가설 / 사용자 관찰: lap313이 D1~D4를 수리했다면, lap313 코드를 전혀 쓰지 않는 **다른 알고리즘**
  (node-cut 지배 판정 + 원시 instruction 바이트)으로 R2 수치가 그대로 재유도되고, gate/실패 arm 사실이
  이름이 아니라 바이트로 성립해야 한다. 재유도가 어긋나면 lap313 판정은 FAIL이다.
- 예상 PASS / FAIL 조건: 원본 SHA·lap313 3개 산출물 SHA 불변; window 753·entry-reachable 753·실패 arm 7·
  성공 arm 724·unresolved 0; 직접 writer 정확히 `{0x431B79,0x431B7F,0x4324B8,0x4324C2}`; cut 지배로 계산한
  `pre_gate`가 lap313 dataflow 결과와 **동일**; gate `0x431AF2`=`75 0a`의 rel8에서 유도한 taken=`0x431AFE`;
  실패 arm 10바이트가 **연속**이고 `5f5e5d33c05b83c434c3`(eax=0 반환).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 probe `docs/history/laps/probes/20260912_lap314_middle_lap313_v5_review_probe.py`
    SHA `44a115e6fc960c3f44215c60da2dc5244e7d86d230e61311b967f463a7b75e49`.
  - 신규 테스트 `tests/test_lap314_middle_review_probe.py`
    SHA `bfcd4bc7fae8bc85333abcab928ee7e255e6277d23079983f94c86aca99039a5`.
  - 생성 report `logs/lap314/lap314_lap313_v5_review.json`
    SHA `a559e3317eed6b400e1f0a5e10e8296a7e6965bbf9c5acad4919058abe571201`.
  - `docs/STATUS.md` 갱신(압축 원문은 `20260912_status_lap314_compaction.md`).
  - 커밋 없음(`LOOP_ALLOW_COMMITS=0`). **lap305~313 산출물과 원본은 수정하지 않았다.**
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `Syw2plus/syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  검수 전후 **불변**. 후보 EXE·활성 플레이어·지도·군대 **없음**. Linux `.venv`, `objdump -d -Mintel -j .text`,
  PE 원시 instruction bytes. synthetic CFG fixture는 회귀 테스트 전용.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python docs/history/laps/probes/20260912_lap314_middle_lap313_v5_review_probe.py
    > logs/lap314/lap314_lap313_v5_review.json` → exit 0, verdict PASS, fresh 2회 stdout SHA 동일
    (`a559e331…be571201`).
  - lap313 probe 재실행 2회 → 두 stdout 모두 SHA `74976804…3ef9c3f`로 **저장된 report와 byte-identical**.
  - `.venv/bin/python -m pytest -q tests/test_lap314_middle_review_probe.py` → **6 passed**.
  - `make check` → **313 passed**, Ruff/compileall/mypy/CONTEXT_PASS. `bash checks/safety.sh check`
    → **SAFETY_PASS**. 게임/Wine/Xvfb/Stage B/runtime/PNG/click **0**, 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **lap313 = ACCEPT-WITH-CORRECTION (1단 정적).**
  독립 재유도 전부 일치 — window **753**, entry-reachable **753**, 실패 arm **7**
  (`0x431AF4,F5,F6,F7,F9,FA,FD`), 성공 arm **724**, unresolved **0**, 성공 ret 미도달.
  화면 전역 `e5bf1c/e5bf20` 언급 **4건 전부가 직접 dword store**
  = `{0x431B79,0x431B7F,0x4324B8,0x4324C2}`; 실패 arm writer **0**, 성공 arm writer **4**.
  reset 두 개가 쓰는 즉값은 `0x280`/`0x1E0` = **640×480** 재확인. node-cut 지배 결과
  `pre_gate = []`(cut 지배자 21개 + entry = lap313 dataflow의 22와 일치) → **다른 알고리즘으로 동일**.
  바이트: gate `750a`, rel8 유도 taken `0x431AFE`(=success join), 실패 arm 10바이트가 **연속**이고
  `5f5e5d33c05b83c434c3`.
  - **D2(주소순 불건전) REPAIRED** — cut 지배가 dataflow 결과를 정확히 재현.
  - **D3(fail-open anchor) REPAIRED** — taken target이 rel8에서 유도되고 실패 arm은 바이트 비교.
  - **D4(죽은 상수) REPAIRED** — `EXPECTED_RUNTIME_WRITERS` 0건, 두 tuple 모두 `EXPECTED_SCREEN_WRITERS`로 소비.
  - **D1(구조적 공허) PARTIAL — lap313의 "D1~D4 수리됨"은 이 항목에서 over-claim이다.** 건전성은 고쳐졌지만
    `pre_gate`는 여전히 `[]`라 `failure_preserves_pre_gate_screen_writer_set`은 사실상
    `failure_writers == set()`로 축약되고, lap313 report는 이 공허함을 **명시하지 않는다**.
    lap312 handoff의 "또는 공허함을 보고에 명시" 선택지가 미이행이다(수치 영향 0).
  - **신규 결함 E1(수치 영향 0, fail-open):** lap313 `build_cfg`의 `BRANCH_RE`는 직접 분기만 잡아
    `jmp DWORD PTR [...]`/`jmp eax`에 **없는 fall-through 간선을 만들고** `unresolved`에도 넣지 않는다.
    현재 window의 간접 분기/호출은 **0건**이라 수치 영향은 없으나, 이 저장소는 이미 jump table
    `0x464B68`(STATUS R6)을 알고 있어 드리프트 시 `unresolved_branches: []` PASS가 이를 못 잡는다.
    lap314 probe는 간접 분기를 `unresolved`로 기록하고 후계 간선을 만들지 않는다.
  - **신규 결함 E2(수치 영향 0, fail-open):** lap313 `gate_byte_facts`는 `address >= FAILURE_SEED`인 행의
    바이트를 **주소 연속성 확인 없이** 이어 붙인다. lap314가 연속성을 명시 검사했고 현재는 성립한다.
  - **테스트 품질 개선 기록:** lap313의 synthetic backward-jump 테스트 2건은 답이 독립 유도 가능한
    **진짜 알고리즘 테스트**로, lap311의 자기참조 약점보다 낫다. 다만 바이너리 사실 테스트는 여전히
    검증 대상을 import해 드리프트만 잡는다(lap314 테스트는 lap313 **report 파일**과 교차 대조해 이를 보완).
  - **provenance 정정(수치 영향 0):** STATUS(및 `20260912_status_lap312_compaction.md`)의 lap311 probe 약칭
    `a33f216a…c9c08a8`은 **꼬리가 틀렸다**. 실제 SHA는
    `a33f216a51a6f213543df8905e4b3ece19435316a71f44241761c543f8fd4524`(꼬리 `…8fd4524`)이며,
    적힌 `c9c08a8`은 원본 EXE SHA의 꼬리다. 원문 `20260912_lap311_work_v4_mode_writer_order.md`의
    전체 SHA가 정본이다. 과거 압축본은 고치지 않고 여기에 정정을 남긴다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 본 검수는 전부 **정적**이고 G1 제품 증거 **0**이다.
  call은 fall-through로 취급하므로 callee 쓰기·cross-function event/thread 순서는 여전히 **UNKNOWN**
  (lap308·lap310·lap312에 이어 lap314도 못 좁혔다). 계산/간접 포인터 쓰기, click-time mode, WM_CLOSE,
  실제 scene/input, G2~G4 증거도 0이다. 본 판정은 middle의 **기술 컨펌**이며 사용자 마일스톤 승인·
  Stage B 허가·제품 G1 합격이 **아니다**. 본 probe는 자기 출력 SHA를 단언하지 않아 W3 함정을 피한다.
- 다음 한 가지: 다음 work(Luna/Sonnet5/high)가 **E1과 D1-잔여를 최소 변경으로 수리**한다 —
  (a) 간접 분기를 `unresolved_branches`로 기록하고 가짜 fall-through 간선을 만들지 않는다,
  (b) `pre_gate`가 비면 report에 `pre_gate_is_vacuous: true`와 축약식을 **명시**한다,
  (c) 실패 arm 바이트 연속성을 검사한다. lap313 파일은 덮어쓰지 말고 새 probe로 만들며,
  lap305~314 산출물과 원본 SHA는 보존한다. 게임/Wine/Xvfb/Stage B/runtime/PNG/click은 계속 금지.
