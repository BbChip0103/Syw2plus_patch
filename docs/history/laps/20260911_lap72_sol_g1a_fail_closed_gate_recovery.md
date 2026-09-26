# 2026-09-11 | lap 72 | 목표 G1-A fail-closed gate 복구 확인

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier / diagnosis·plan·confirmation. 현재 세션 표면은 실제 provider/model ID/effort를 노출하지 않으므로 `gpt-5.6-sol` 실행으로 주장하지 않는다.
- 가설 / 사용자 관찰: lap71 상세가 history에 보존되고 STATUS가 180줄 이하로 정리된 뒤 lap70 source/SHA/old bytes/no-click 및 전체 필수 gate가 모두 새로 PASS하면 fail-closed source 계약을 middle 확인하고 새 private evidence-only run 1회를 work tier에 허용할 수 있다.
- 예상 PASS / FAIL 조건: STATUS≤180, source/test/guard와 원본·참고 SHA 일치, count dispatch/fill/consumer/writer old bytes 일치, 직접 3·targeted 57·Fast 127·safety·doctor 모두 PASS해야 한다. 하나라도 실패·충돌하면 판정 없이 `loop/ESCALATE_SOL`로 중단한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/helper/tests/binary/fixture/좌표/timeout 변경 없음. 판정 문서 `docs/STATUS.md`, 활성 G1-A 카드, `analysis/memory_maps/player_offsets.md`, 본 이력만 갱신하고 소진 marker `loop/ESCALATE_SOL` SHA `209b6e0138d0554f91bd6db55e893377a8ff613ca0288e7a2f983a10ef279a8c`를 아래에 보존 후 제거한다. source SHA는 `tools/runtime_env.py=89fddce79899fc8cd7b6f1472ab4aefc775605031439726695d45713701d8813`, `tests/test_runtime_env.py=ab344efc0925ac8a67de4ea9bf8292c4c37cf82cc65e22a342ee341d5492ea6b`, `tests/test_runtime_guards.py=93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`; Git unborn/uncommitted, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본·참고 PE32 EXE SHA 모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. 후보 EXE·새 runtime·PNG·game run은 없고 직접/targeted만 virtual read-memory synthetic fixture와 recorder callback을 사용했다. 활성 플레이어/지도/군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor`; `make check`; `sha256sum`/`file`; `objdump -d -Mintel`의 `0x498FBA`, `0x499201..0x499336`, `0x499583`; `objdump -s`의 `0x4A3B5B`; no-click/output 직접 3 tests; `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py`; `bash checks/safety.sh check`; 최종 문서 후 `make check`/safety/doctor/`git diff --check`. 새 로그·캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 검수 시작 STATUS **141줄**, 판정 기록 후 **145줄**. doctor top `ok=true`/original verified(기본 runtime manifest optional false); count0→`0x498FC3`, count1→`0x498FDB`·`0x499201..0x49929E`, count&gt;1→`0x499336`, 공통 `0x499583`, writer old bytes `66 8b 54 24 08 0f bf c0 66 89 94 41 96 0c 00 00`; 직접 **3 passed**, targeted **57 passed**, 기록 전·후 Fast 각각 **127 passed**, Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**, 최종 doctor PASS. 최종 문서 SHA는 STATUS `b00fa88242b096132d32a1fb4430413423c26bf9a65c51665698775d7cba4c8d`, card `d8ae18b6239c0b6b833fa719f486b21c5d20ce1384ddbe9f58e92d3da7e9f4a3`, map `6e7a2a38b0363918784ac16c7b15360640c1fed7c1e3ce225607de61726d8cdb`이며 marker는 제거됐다. lap70 source 계약 **MIDDLE CONFIRM PASS**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: binary patch가 없어 new bytes/copy-only/non-overlap/restore는 N/A/SKIP이고 unsupported SHA rejection은 targeted에 포함된다. primary field/action·worker 의미, 실제 1600×1200 출력/입력, G2~G4와 사용자 승인은 UNKNOWN/미완료다. 과거 캡처를 fresh runtime으로 승격하지 않았다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high 또는 Claude Code `claude-sonnet-5`/high work가 새 private manifest를 prepare/check하고 고정 원본 `g1-baseline --screen 1600x1200x24 --timeout 90`을 정확히 1회 evidence-only 실행한다. 코드/tests/binary/fixture/좌표/timeout 변경과 실패 재시도 없이 live evidence·callback 미호출·owned cleanup을 보존하고 새 `loop/ESCALATE_SOL`로 middle에 돌려보낸다.

## 소진 전 `loop/ESCALATE_SOL` 원문

# lap71 승격 요청 — 문서 line-limit로 필수 Fast 실패

## 사유

lap70 source/original SHA·old bytes, stable-ineligible primary output 보존, eligible/ineligible
mouse callback 0회는 독립 재현됐다. 직접 3 PASS, targeted 57 PASS, 기록 전
`make check` 127 PASS, safety/doctor PASS였다. 그러나 lap71 판정을 문서에 기록한 후
재실행한 필수 `make check`가 `docs/STATUS.md: 183 lines exceeds 180`으로
13 FAIL/114 PASS했다. 예상 밖 필수 gate 실패이므로 재시도·마감하지 않았다.

## 승격 작업자가 이어서 검증할 것

1. lap71 상세·명령·수치·반려는
   `docs/history/laps/20260911_lap71_sol_g1a_production_fail_closed_confirmation.md`에 보존하고,
   `docs/STATUS.md`의 과거 세부를 provenance를 유지한 채 history로 옮겨 180줄 이하로 복구한다.
2. source/test/guards SHA, 원본´참고 EXE SHA, count dispatch/fill/consumer/writer old bytes,
   no-click/output evidence 직접 3 tests, targeted 57, `make check`, safety, doctor를 새로 재검증한다.
3. 전체 gate가 모두 PASS한 뒤에만 lap70 `MIDDLE CONFIRM` 및 격리 1회 evidence-only
   game run 허용 여부를 재판정한다. 그 전 game run·코드/binary/fixture 변경은 금지한다.

## 보존된 근거

- source SHA: `tools/runtime_env.py=89fddce79899fc8cd7b6f1472ab4aefc775605031439726695d45713701d8813`,
  `tests/test_runtime_env.py=ab344efc0925ac8a67de4ea9bf8292c4c37cf82cc65e22a342ee341d5492ea6b`,
  `tests/test_runtime_guards.py=93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`.
- original/reference EXE SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- writer old bytes: `66 8b 54 24 08 0f bf c0 66 89 94 41 96 0c 00 00`.
- 후보 EXE·새 runtime·PNG·game run·commit/push는 없다. 제품 G1~G4와 사용자 승인은 미완료다.
