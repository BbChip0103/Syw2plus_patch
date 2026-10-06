# 2026-10-05 | lap 990 | 목표 G6·G7 (사용자 합격 요청 대기 — 전달물 재확인 + H-G6f handoff 구체화)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 중간(middle) 1 lap. lap989가 root 전달용으로 남긴 `loop/ESCALATE_SOL`(마일스톤 경계)이 그대로 있는 상태에서 일반 작업자 경로로 기동됨.
- 가설 / 사용자 관찰: lap989 스테이징 EXE 2개와 안내문이 그 뒤 바뀌지 않았고, 현재 source(G6·G7 patch 모듈)가 같은 SHA를 다시 만든다. H-G6f(fixed_start G6)는 g6 probe의 설치 경로 한 곳만 바꾸면 실행할 수 있다(FEASIBLE).
- 예상 PASS / FAIL 조건: 스테이징 SHA = `fb7c2131…`/`58b9b22a…`, 입력 이식판 SHA = `0e28ef57…`/`703deaf4…`, 메모리 재조립 SHA 일치, lap989에 기록된 하네스 해시 4개 불변. 하나라도 어긋나면 전달 보류 + ESCALATE 사유 갱신.
- 변경 파일 / source fingerprint / 커밋: 문서만 — 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL`(lap990 확인 줄 추가). 게임/patch/tool/test source 0, commit 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 입력 이식판 normal `0e28ef57f8eb1f67…`·fixed_start `703deaf4c07b4497…`(`260921_temp`, read-only 재해시). 게임 실행 0. `260921_temp`에 `G6G7` 파일 0개(사용자 폴더 배치 아직 없음).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `sha256sum ../temp/Syw2plus_patch/20261005_lap989_middle_review/user_test_staging/*` → 일반판 `fb7c21319414b13517c7f8fdeeef3ca6b04c61953e592733e1ed3cc5bc65c56a`, 시작자리고정판 `58b9b22a650a647fe7ddf43dcf2ae58d5c943d02448ac20fc36b2032f3c2f078`(각 1,085,440 B), 안내문 `2145f0a98a9ac1748a617f848113a824e3c31a6d5031c5b9d6eecc3b6f63b76a`(4,432 B).
  - 메모리 재조립(`PYTHONPATH=. .venv/bin/python`, `g6.build_candidate` → `g7.build_candidate`, 디스크 기록 0): normal G6만 `b50af2a615354fc9…` → cand67 `fb7c2131…c56a`, fixed_start G6만 `7c891658a58d3f83…` → cand67 `58b9b22a…f078`. **스테이징과 일치.**
  - 하네스 해시 재확인: `tools/g6_shift_click_probe.py` `5b0ffb7f90d59d58`·`tools/g7_save_load_probe.py` `601a93f10728ac32`·`tests/test_g6_shift_click_probe.py` `0245845592115ff0`·`tests/test_g7_save_load_probe.py` `4fbb804a18829f8a` — lap989 기록과 같음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - 전달물 재확인 **PASS**(SHA 3개·입력 2개·재조립 2개 일치). 사용자 합격은 여전히 **대기**(모델이 PASS 처리하지 않음).
  - H-G6f 가능성 **FEASIBLE**(정적): g6/g7 patch 모듈 둘 다 `PORT_SHA256`에 fixed_start를 가지고, g7 probe는 이미 `PORT_EXES`·`_install(variant, port)`·`--port`를 가지며 lap988 f1에서 fixed_start에 같은 `build_lobby_snapshot`(g6 probe에서 import)으로 A 단계 local 2가 나왔다. 막힌 곳은 g6 probe `_install(variant)`(`tools/g6_shift_click_probe.py:195`)이 `PORT_EXE`(normal)와 `PORT_SHA256["normal"]`을 하드코딩한다는 것뿐이다. `LAYOUTS`(선택 base `G5BSS_VA`·50·풀)는 두 이식판에 같은 port 모듈 상수다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: DESIGN G6/G7 사용자 합격 아님(APPROVALS lap989 요청 열림). lap981 ↑/↓ 포커스 질문 열림. 이 회차와 lap989 둘 다 제품/실행 증거 0 → 다음 회차는 문서만 회차가 될 수 없다(PROMPT ③ 연속 최대 2회). `loop/ESCALATE_SOL`은 root 전달 몫이라 지우지 않는다.
- 다음 한 가지:
  - (root) `loop/ESCALATE_SOL` 그대로: 스테이징 2개+안내문을 사용자에게 전달(배치 전 위 SHA 재확인)·G6/G7 합격 판단 요청.
  - (루프 재개 시 work, Sonnet) **H-G6f handoff**:
    1. `tools/g6_shift_click_probe.py`: g7 probe와 같은 방식으로 `PORT_EXES`(normal/fixed_start, g7 probe의 정의를 재사용하거나 g6 probe로 옮기고 g7이 import)와 `_install(variant, port="normal")`; `run_probe(..., port="normal")`, CLI `--port {normal,fixed_start}` 기본 normal, 결과 JSON `port` 필드. `orig`는 port 무시. 기본 normal 동작·기존 테스트 불변.
    2. 테스트 RED→GREEN: fixed_start `_install("port")` SHA `703deaf4…`, `_install("cand")` `7c891658a58d3f83…`, `_install("cand67")` `58b9b22a…`; 기본 port 생략 시 기존 normal SHA; 알 수 없는 port ProbeError.
    3. 격리 실행 3회(`--seat-method lobby-snapshot`): fixed_start `port` seat 2(기대 G6-1 `[1×6]` stuck_at_one), `cand67` seat 2(G6-1 `[1..6]`·G6-2 1→3·G6-3 3→2·G6-4 cap 50·local 2 60초), `cand67` seat 0 대조(같은 G6-1~4, local 0).
    4. 사전등록 PASS: private EXE SHA 위 값, 세 run 위 기대 일치. 반증: fixed_start에서 lobby-snapshot 뒤 local≠2면 BLOCKED 기록 + g7 probe A 단계 경로 대안. 게임 사본 정리·`make lint`/`typecheck` 뒤 `make check` 1회.
  - 그 뒤 G1 H-F 재개(STATUS G1 보류 항목).
