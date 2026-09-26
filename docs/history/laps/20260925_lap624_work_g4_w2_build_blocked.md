# 날짜 | lap 624 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Codex native session / hands-on work / high; 지정 역할은 실무 구현자다.
- 가설 / 사용자 관찰: W2 허용 범위의 원본 load call wrapper와 기존 AI shadow를 한 opt-in bridge에서 같은 run/seq로 묶으면 exact post-load marker와 첫 edge를 판정할 수 있다.
- 예상 PASS / FAIL 조건: 두 call-site old-byte preverify, partial-install rollback, load success-only marker, bounded 17-row post-load window, bridge/env/run-id/provenance fail-closed, targeted/build/safety/Fast PASS. 필수 gate 예상 밖 실패 시 게임을 시작하지 않고 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/inmm_stub/ai_shadow.c` SHA256 `d4cf0eba313b94ccae7f273a177e8042a9bb2a96195fada9fc50fb51fa714bdd`; `tools/runtime_env.py` `d5ab8033f81803b0acf9a7fda084d639aa4821646a143dd915ccf7521961b0fb`; `tests/test_g4_ai_shadow.py` `be2635f9c012af8776e856820668ec38810f742b49f18f13c91905b52b954aaa`; `tests/test_runtime_env.py` `61ec8aae5e312863697d9695b139ce994a0eca1f9f10558a5758b90abe0aded8`; 커밋 없음/uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: pinned original EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`는 읽기 전용이며 게임 실행 없음. 후보 bridge는 build 실패로 설치/실행하지 않음. Python `.venv`; 활성 플레이어/지도/군대 N/A; fixture 실행 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_g4_ai_shadow.py tests/test_runtime_env.py tests/test_s1_load_evidence.py` → 231 passed/1.95s. `make -C tools/inmm_stub clean all` → exit2, `/tmp` linker diagnostic `undefined reference to g_load_original_target`; `.venv/bin/python -m compileall -q tools/runtime_env.py` PASS; `git diff --check` PASS. 캡처/게임 로그 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): Python 회귀 PASS; bridge build FAIL; 전체 Fast/Safety/fresh runtime SKIP. 최종 판정 `BLOCKED(build_link)`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 새 C wrapper의 external symbol이 링크되지 않았다. load wrapper ABI/rollback은 bridge binary로 검증되지 않았고, runtime provenance는 synthetic unit 회귀만 검증됐다. middle 독립 검수·사용자 승인 없음. 게임 실행/제품 AI 수정/원본·save 쓰기 0.
- 다음 한 가지: 승격 작업자가 `g_load_original_target`의 32-bit bridge symbol visibility/assembly reference를 독립 판정하고 W2 source 범위에서 최소 link 수리를 한 뒤 targeted 회귀→clean bridge build→safety→`make check`를 새로 수행한다. build 통과 전 fresh 실행은 금지한다.
