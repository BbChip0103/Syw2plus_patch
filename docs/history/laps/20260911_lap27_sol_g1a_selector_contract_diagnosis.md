# 2026-09-11 | lap 27 | G1-A selector 계약 middle 독립 진단

- 실제 provider/model/effort / 지정 역할: Codex 새 세션, 사용자 지정 middle 진단·계획·확인 역할.
  계약 대상은 `gpt-5.6-sol`/high이나 현재 런타임이 정확한 model ID/effort를 노출하지 않아 실제값은
  미확인. 게임 코드·하네스·EXE/DLL/asset 수정 및 게임 실행 없음.
- 가설 / 사용자 관찰: lap26의 `PS=7`, `0x004ED848` WORD `1→1`은 원본 버튼 실패를 입증하기보다,
  이 WORD를 PS7 두 버튼의 즉시 selector 상태로 간주한 하네스 계약이 미입증임을 드러낸다.
- 예상 PASS / FAIL 조건: lap26 SHA·manifest·화면·surface/module·cleanup을 재확인하고, 원본 WORD
  xref와 production/test 결선을 비교해 입력 delivery, reader timing/meaning, 원본 UI 중 근거가 지지하는
  범위만 판정하며 다음 read-only probe 하나를 고정하면 middle PASS. 근거 충돌이나 필수 Fast 실패면
  변경을 보존하고 `loop/ESCALATE_SOL`을 갱신한 뒤 중단한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현 변경 없음. 문서만
  `analysis/memory_maps/player_offsets.md`, `docs/work/active/G1_A_EXECUTION_CARD.md`,
  `docs/STATUS.md`, 이 기록과 `loop/ESCALATE_SOL`을 갱신. 검수 source SHA는
  `tools/runtime_env.py` `b091a8ae83e5332c1d5dc17cb979531fcafc19bdf3368f56b4c094d24560195c`,
  `tests/test_runtime_env.py` `d15a3580b2fd9d0bc209ca62015bc659f3a0d8982d33ea559b7645f1306baa75`.
  교체 전 marker SHA256 `21c2766265668797a5672c4e973bb8f6f1b24a243c905d2eb001ced15118339a`.
  커밋 없음, unborn HEAD, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본과 lap26 private copy
  SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 재계산 일치.
  lap26 manifest SHA256 `801bc9683cc82ccea2d061fa0089fdb31908a2defff7388666ecba294c16341c`;
  private win32 prefix, Xvfb `:91`, 1600×1200×24, 무수정 기본2인 fixture. selector gate 전이라 실제
  활성 플레이어·지도·군대는 미측정. 바이너리 후보 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `jq`, `sed`/`rg`, 원본 전체
  `objdump -d -Mintel` literal xref, 보존 PNG 원본 시각 대조,
  `.venv/bin/python tools/runtime_env.py check --manifest local/runtime/20260911_024939_418440_0/manifest.json`,
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py`, `make check`,
  `bash checks/safety.sh check`. 게임/`g1-baseline`/패치 생성·원복은 실행하지 않음. lap26 verdict SHA
  `9295be280f5623792a0cbec3794e6fbe0038cd3c2efe731b0e93ea3cc9af5514`, inputs SHA
  `5359a2daefbf02bade776b3bd2fd1d1a6c19e6f90e438bb4eb410c023ed8c365`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): manifest check PASS; targeted `19 passed in 0.04s`;
  Fast `89 passed in 11.11s`, Ruff/compileall/mypy 8 files/`CONTEXT_PASS`; safety `SAFETY_PASS`.
  lap26 original/copy SHA, root1600×1200, content800×600, PS9 surface, modules, owned cleanup은 PASS.
  **Evidence:** `_read_lobby_mode`는 WORD를 정확히 읽지만, 전체 literal xref는 폭/0·1 write만 보이고
  두 PS7 버튼 callback과 write의 연결을 입증하지 않는다. `_g1_selector_flow`는 click 뒤 WORD predicate가
  성공해야만 post-click PNG/입력 행을 남기며, 테스트는 click stub가 직접 mode를 바꾼다.
  **Inference:** 1순위 High는 잘못 고정된 harness selector 의미, 2순위 Medium은 미기록 input delivery,
  3순위 Low는 timing 단독 문제다. 실제 원본 UI 결함과 정확한 selector 상태는 UNKNOWN.
  패치/old-new bytes/version rejection/non-overlap/restore는 후보가 없어 SKIP(N/A).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: G1-A/G1~G4와 사용자 승인 변화 없음.
  현재 결과는 원본 실패가 아니라 관측 계약 REVISE다. 문서-only lap으로 implementation-unchanged-streak가
  2가 되므로, 다음을 추가 서술이나 재실행이 아닌 정확한 정적 research blocker로 고정한다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 동일 원본을 읽기 전용으로 두고 두 PS7 버튼의
  생성·hit-test·callback부터 실제 선택 상태 write/branch까지 주소·old bytes·호출 경로를 추적해
  `analysis/memory_maps/player_offsets.md`에 남긴다. 확인 불가하면 마지막 검증 주소와 이유를 기록한다.
  runtime/tests/game 수정과 새 run은 금지하고, 그 결과는 새 Sol/high가 독립 확인한다.

## 교체 전 `loop/ESCALATE_SOL` 원문

```text
reason=g1a_lap26_selector_gate_fail
role_requested=Fresh Codex gpt-5.6-sol/high middle diagnosis and scope decision; do not rerun g1-baseline and do not implement before diagnosis.
required=Independently inspect local/runtime/20260911_024939_418440_0/output/g1_a/verdict.json, output/g1_baseline.json, manifest, inputs, surface, window, modules, and preserved PNGs. Reconfirm original/copy SHA, the 1600x1200 display plus 800x600 content boundary, and cleanup. Determine whether the visible multiplayer click / WORD observation conflict is input delivery, reader timing/meaning, or original UI behavior. Define one narrow next probe or approved repair with exact version rejection, old bytes/range, non-overlap and rollback conditions if binary work is eventually justified.
observed=prepare PASS; check PASS; fixed g1-baseline completed once in a new private copy and prefix on DISPLAY=:91 with LANG/LC_ALL=ko_KR.UTF-8, WINEARCH=win32, WINEDLLOVERRIDES=ddraw=b. verdict overall FAIL after 90.395s: visible multiplayer selector did not normalize WORD 1->0; last={'ps': 7, 'lobby_mode': 1}. Menu PS9->PS7 PASS. PS9 renderer surface is mode3/800/600/8/800/600. PS3 was not reached; required inputs and same-run scene are not proven. Cleanup PASS; no global kill; no source/binary patch.
evidence=manifest local/runtime/20260911_024939_418440_0/manifest.json sha256 801bc9683cc82ccea2d061fa0089fdb31908a2defff7388666ecba294c16341c; verdict local/runtime/20260911_024939_418440_0/output/g1_a/verdict.json; aggregate local/runtime/20260911_024939_418440_0/output/g1_baseline.json; log local/runtime/20260911_024939_418440_0/output/g1-baseline.log; lap docs/history/laps/20260911_lap26_luna_g1a_run_fail.md.
candidate=tools/runtime_env.py sha256 b091a8ae83e5332c1d5dc17cb979531fcafc19bdf3368f56b4c094d24560195c; original and copied syw2plus_original.exe sha256 b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac. No candidate binary, old/new bytes, or restore was produced.
stop=No retry, no fixture change, no patch, no commit, no push. Preserve all local runtime and shared-temp artifacts. After Sol diagnosis, return only one bounded next action to the gpt-5.6-luna/high work tier or record a concrete blocker.
```
