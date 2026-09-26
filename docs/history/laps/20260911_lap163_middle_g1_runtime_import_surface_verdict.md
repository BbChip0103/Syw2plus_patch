# 2026-09-11 21:06 KST | lap 163 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle tier(진단·계획·컨펌)**.
  게임 코드 hands-on 수정 없음. lap162 work tier(Luna/Sonnet5) 결과의 독립 검수와 판정만 수행.
- 가설 / 사용자 관찰: `loop/ESCALATE_SOL`(lap162)의 두 미결 —
  (1) `tools/runtime_env.py:2602` package import가 왜 `patches`를 못 찾았는가, 계약에 맞는 실행 형식은 무엇인가.
  (2) cleanup `wineserver -k` 실패와 `dxwrapper_config_restored=false`가 실제 소유 잔류/config 오염인가.
- 예상 PASS / FAIL 조건:
  - PASS = 두 현상이 **단일 원인**으로 설명되고, 원본/후보 config 잔류가 0임을 실측으로 보이며,
    P3 재개 조건을 코드 수정 없이 확정할 수 있다.
  - FAIL = 원인이 갈리거나 config/프로세스 잔류가 실제로 남았다 → Astra 승격.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  게임/도구 코드 변경 **0**. 문서만 갱신(uncommitted):
  `docs/STATUS.md`, `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`,
  `docs/history/laps/20260911_lap163_middle_g1_runtime_import_surface_verdict.md`, `loop/ESCALATE_SOL` 해소(삭제).
  커밋 없음(`LOOP_ALLOW_COMMITS` 미설정, 저장소에 커밋 0건). 이번 lap이 쓴 파일 해시:
  `docs/STATUS.md` `42a41f32e4fbb5d6c9584f35b88b5794a74401e2adbf97d2d402044fa7fbeed6`,
  handoff `e9d1abc94982d623a23b21a95bb5104d10b1273f1b185fa7d8c3840b19abe6c2`,
  lap162 escalation 원문 사본 `d2ce2184287195ec03fa01acc4740688d7df545c35f1cf9f2705c27ee3677c82`.
  mtime 대조로 이번 세션이 `tools/`·`patches/`·`tests/`·원본/후보 binary를 **건드리지 않았음**을 확인했다.
  검수 대상 source는 lap162와 **바이트 동일**: `tools/runtime_env.py`
  `f05b4c1c8e77f07a2b90a8fb6c833444ca090691531c2f6d7a91fb9cbc1750c8`,
  `tests/test_runtime_env.py` `9de4d1e68f0e68e503474446c0a38575d963034136e164ae4eacd5830c616ebd`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(검수 run manifest에서 확인).
  dxwrapper.ini pinned SOURCE `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`,
  approved CANDIDATE `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`.
  **새 게임 실행 없음.** 이번 lap은 기존 보존 산출물과 저장소 정적 증거만 읽었다. fixture 소비 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 재현 확인(해시): `sha256sum tools/runtime_env.py tests/test_runtime_env.py` → 위 2/2 일치.
  - `sha256sum local/runtime/20260911_210036_823051_0/output/g1_presentation_trace/*.json` → 3/3 일치
    (`verdict` `0d500d6c...4a741`, `evidence` `f8255c66...4acbf5`, `provenance` `ca0683c4...49d9ec`; ESCALATE_SOL 기재와 동일).
  - `sha256sum local/runtime/20260911_210036_823051_0/game/dxwrapper.ini`
    → `918e7043...ea5a2` = **pinned SOURCE(원본)**. candidate 아님.
  - `ls -la .../game/` → `dxwrapper.ini.original-backup` 없음, `dxwrapper.ini.patch.json` 없음.
  - `.venv/lib/python3.*/site-packages/__editable__.syw2plus_patch-0.1.0.pth` 및 finder
    `MAPPING = {'patches': <repo>/patches, 'tools': <repo>/tools}` 확인.
  - `ls tools/__init__.py patches/__init__.py ...` → 전부 없음(namespace package).
  - `grep -n python Makefile` → `PYTHON ?= .venv/bin/python`.
  - 보존 로그 `local/runtime/20260911_210036_823051_0/output/g1-presentation-trace.log` = **0바이트**.
  - **SKIP(권한):** 이번 세션은 비대화형이라 `make check`, `pytest`, `.venv/bin/python -c` 실행이
    모두 승인 거부됐다. Fast 게이트를 직접 재실행하지 못했다. lap161과 동일한 제약이다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):

  **판정 1 — 실행 표면 (ESCALATE_SOL #1): 원인 확정, 코드 회귀 아님. PASS(진단).**
  `tools/runtime_env.py:2602`의 `from patches.resolution import dxwrapper_config`가
  `:2615~2616`의 `sys.path.insert(0, REPO_ROOT)` 보다 **13줄 앞**에 있다. script 모드에서
  `sys.path[0]`은 `tools/`이고 cwd는 경로에 들어가지 않으므로, `patches`는 다음 둘 중
  하나로만 해결된다: (a) `.venv`의 editable install finder, (b) module 실행(cwd=repo root).
  lap110/113/115/146/152/154/160의 fresh runtime은 **전부** `.venv/bin/python tools/runtime_env.py`였고
  `Makefile:1`도 `PYTHON ?= .venv/bin/python`이다. lap162만 `python3 tools/runtime_env.py`로 바꿨고,
  시스템 `python3`에는 그 `.pth`가 없어 `:2602`에서 즉사했다.
  → **계약 실행 형식은 `.venv/bin/python tools/runtime_env.py`로 고정한다.**
  `python3 -m tools.runtime_env`는 import는 통과하겠지만 과거 증거가 0건이므로 **승인하지 않는다**
  (한 바퀴에 변수 하나). 이번 lap에 `:2602`를 고치지 않는다.

  **판정 2 — cleanup (ESCALATE_SOL #2): 둘 다 거짓 경보. PASS(진단).**
  `evidence.elapsed_seconds = 0.024`, `screenshots=[]`, `inputs=[]`,
  `dxwrapper_config`에 `install` 키 **없음** → try 블록 **첫 문장**에서 죽었다.
  `_xvfb()`(`:2606`), `wine explorer`(`:2608`), 게임 프로세스(`:2612`)는 **한 번도 실행되지 않았다**.
  - `wineserver -k` rc1 = 그 prefix에 **죽일 서버가 없었다**는 뜻이다. 소유 정리 실패가 아니다.
    `prefix_processes_after=[]`, `global_kill_used=false`, `owned_launchers_stopped=true`(children 빈 리스트),
    `xvfb_stopped=true`(xvfb is None)가 모두 일관된다. 전역 정리·기존 Xvfb 종료는 없었다.
  - `dxwrapper_config_restored=false`는 **거짓 음성**이다. `:2805`의 식이
    `not dxwrapper_2x or dxwrapper_uninstall is not None`인데 install 자체가 없었으므로 uninstall도 None이다.
    실측으로 게임 copy의 `dxwrapper.ini`는 **pinned SOURCE 해시**이고 sidecar(`.original-backup`/`.patch.json`)도
    없다. **config 잔류 0.** 원본/참고 저장소 쓰기 없음.
  - 부수: `ModuleNotFoundError`는 `:2763`의 except 튜플에 없어 finally만 돌고 밖으로 전파됐다.
    그래서 `verdict.overall=BLOCKED`인데 `verdict.error=null`인 모순이 생겼다.

  **판정 3 — lap162 구현 검수: 계약 준수. PASS.**
  `:987~1001`의 tick 기록은 handoff 지시와 일치한다 — 같은 `program_state_reader()`, 같은 표본,
  같은 1초 주기, 같은 상한 120, `tick` 비정수 시 `tick_error`로 남기고 `ps` 기록은 유지,
  **새 reader/새 주소 없음**. 테스트 3케이스(`tick-increases`/`tick-stalls`/`tick-missing`,
  `tests/test_runtime_env.py:383~427`)도 지시대로 존재하며 기존 테스트를 느슨하게 바꾸지 않았다.
  Fast 재실행은 권한 SKIP이나, source 2/2가 lap162와 **바이트 동일**이므로 lap162의 `190 passed`는
  같은 바이트에 귀속된다. 이를 P3 결과로 승격하지 않는다.

  **P3 가설 자체: 여전히 UNKNOWN.** tick 표본 0건, PS3 표본 0건. 게임은 뜨지도 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 회귀 없음(코드 변경 0). 실패 run의 prefix/display/게임 copy는 보존만 하고 재사용 금지로 남긴다.
  - 남은 위험: `:2602` import 순서는 고쳐지지 않았으므로 인터프리터를 틀리면 **같은 방식으로 또 죽는다**.
    이번엔 문서/카드에서 커맨드를 고정하는 것으로만 막는다.
  - 관측 품질 결함 3건을 **지연 카드**로 기록했다(아래 handoff). P3 가설과 무관하므로 지금 끼워 넣지 않는다.
  - 독립 검수: 이 문서가 lap162에 대한 2단 독립 검수다. 3단 사용자 마일스톤 승인은 **없음**.
    G1 제품 완료 아님. 프로세스 exit/SKIP/과거 결과를 승인으로 쓰지 않았다.
- 다음 한 가지:
  work tier가 코드 변경 **0**으로 P3 fresh runtime을 **정확히 1회** 재개한다.
  인터프리터는 `.venv/bin/python`으로 고정하고, 새 parent/prefix/display/build를 쓰며
  `local/runtime/20260911_210036_823051_0`와 `/tmp/syw2plus_lap162_build.OHHsLU`는 재사용하지 않는다.
  나머지 변수(timeout 90, `--dxwrapper-2x`, 좌표, close 시퀀스, config)는 그대로 둔다.
