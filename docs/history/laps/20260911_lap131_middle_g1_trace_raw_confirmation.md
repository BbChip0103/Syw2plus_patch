# 2026-09-11 | lap 131 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier(진단·계획·확인). 저장소 계약의 기본은 Codex `gpt-5.6-sol`/high이나 현재 대화 표면이 실제 model ID/effort attestation을 제공하지 않아 추정하지 않았다. 게임 코드·하네스·원본·후보는 수정하지 않았다.
- 가설 / 사용자 관찰: lap130의 raw 분리 수리는 기록된 세 source/test SHA와 일치하고, 116행 install snapshot 뒤 live trace가 617행으로 자라 clean finalization이 실패하면 install은 그대로이며 final raw만 live bytes로 갱신되고 validator는 호출되지 않는다.
- 예상 PASS / FAIL 조건: 세 SHA 일치, install/final 경로와 helper 호출 순서 정적 대조, 116→617 byte-exact/validator 0회 회귀, targeted/Fast/doctor/safety PASS면 컨펌 PASS다. 불일치·예상 밖 필수 실패면 runtime 재시도 없이 `loop/ESCALATE_SOL`을 유지/갱신한다. 실제 게임/runtime/G1/M1은 SKIP한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 검수 SHA는 `tools/runtime_env.py=e9eb7f445ac9b94d2618c2d5d7d470e79779270417a67e6f7dd5fd07542c6f0e`, `tests/test_runtime_env.py=319eabe0c829c71f034eb0666adda5c0d4289c09fc988ded73d64209bcb4211a`, `tests/test_g1_presentation_trace.py=0830895fdc8de1b3f62f5636ea9c0b3cdeeddd4dd7d6c99669f1c1ff30de2a14`로 lap130과 모두 일치했다. 이번 변경 SHA는 `docs/STATUS.md=69c3aa6bfbc651e839ed5cc986507891fa9aebbce7ec52b2e1fb0fa36e377c0c`, work handoff `641333a037cdd196c54179e58dac553c86cbc153f9374c9673b4cb436658d1fa`이며 본 self-referential 기록은 생략한다. 소진 marker `loop/ESCALATE_SOL` SHA `6ea1a884ed2ec4324218967402cc646faed0e9f264b375f00055e731e34f86d8`은 아래 원문 보존 후 제거했다. `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, doctor `verified`; 제품 후보/EXE/DLL/assets 변경 없음. synthetic 116→617 JSONL, process poll growing trace, validator spy만 사용했다. 게임/Wine/Xvfb/PNG, 활성 플레이어/지도/군대는 SKIP/N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sed`/`rg`/`sha256sum`으로 lap129~130, source와 호출 경계를 대조; targeted 두 파일 **71 passed**; 핵심 `test_g1_trace_pipeline_separates_install_snapshot_from_growing_final_raw` 별도 **1 passed**; `make check` **164 passed**, Ruff/compileall/mypy/context PASS; `make doctor` top `ok=true`/original verified(미생성 runtime manifest는 optional 진단); safety `SAFETY_PASS`. 새 runtime/PNG는 실행하지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): install gate는 `trace_install.jsonl`과 `install_trace_sha256`만 기록한다. finalization 예외는 live trace를 `trace_raw.jsonl`에 덮어써 stale install snapshot을 최종 raw로 쓰지 않는다. fixture에서 install 116행 exact, final raw 617행 exact, clean `trace.jsonl` 없음, validator 0회다. **RAW SEPARATION MIDDLE CONFIRM PASS / RUNTIME BLOCKED / G1·M1 BLOCKED**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: actual owned Win32 HWND/PID에 WM_CLOSE가 전달되어 process exit와 DLL detach가 생기는 증거, PS3 전 overflow 2개의 lossless bounded capacity, 실제 2배 출력/필수 입력은 미검증이다. 제품·마일스톤·사용자 승인 없음.
- 다음 한 가지: 새 Luna/high work tier가 `docs/plans/20260911_lap131_g1_owned_win32_close_transport_handoff.md` 범위에서 actual owned Win32 close helper/runner와 격리 PE32 fixture를 구현·검증한다. 게임 runtime은 실행하지 않으며 결과는 새 Sol/high 세션이 독립 검수한다.

## 소진 전 `loop/ESCALATE_SOL` 원문

```text
lap=130
role=middle confirmation pending after Luna/high work
target=G1 diagnostic presentation trace finalization and evidence preservation
status=IMPLEMENTED; Sol/high independent confirmation required; game runtime remains blocked

lap128의 raw/provenance/evidence/verdict와 보존 prefix live trace를 독립 대조했다. 기록된 artifact
SHA는 일치하고 원본/private-copy EXE SHA는 모두
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다.

확정 원인:
1. `tools/runtime_env.py`는 `xdotool windowclose` 성공을 owned game의 정상 Win32 종료 요청으로
   간주하지만 실제 process는 90초까지 살아 있었다. bridge summary는 DLL_PROCESS_DETACH에서만
   생성되므로 process 미종료가 summary_count=0의 직접 경계다. 설치 xdotool 문서도 windowclose가
   X window를 destroy하되 client를 kill하지 않는다고 한다. 원본 WndProc의 WM_CLOSE default/
   WM_DESTROY→PostQuitMessage 분기는 정적으로 존재하지만 현재 명령이 그 분기를 호출했다는 증거는 없다.
2. output `trace_raw.jsonl` 116행은 install gate가 미리 쓴 snapshot이다. 실패 보존 함수는 목적 파일이
   이미 있으면 복사를 건너뛰므로, prefix live trace 617행/SHA
   `b105fc3452dc1650aab58cd7c66aa79e97656964a121ab18d80713f6469d8539`를 output에 보존하지 못했다.
   116행 파일은 live의 첫 116행과 byte-for-byte 일치한다.
3. live 617행 validator는 schema errors 0/capture true지만 SurfaceRelease/BltFast 각 256회,
   overflow 2개와 summary 누락으로 BLOCKED다. 첫 overflow는 PS7이므로 close만 수리해도 PASS하지 않는다.

완료한 Luna/high work 한 가지:
- `docs/plans/20260911_lap129_g1_trace_finalization_repair_handoff.md`의 첫 단계만 수행했다.
- `tools/runtime_env.py`와 관련 회귀 테스트 최소 변경으로 install snapshot과 final failure raw를
  분리하고, 116→617 growing trace fixture에서 최종 raw exact copy/validator 미호출을 직접 고정했다.
- targeted/Fast/doctor/safety만 실행했고 게임/runtime/PNG는 실행하지 않았다.

실제 work 결과: install snapshot은 `trace_install.jsonl`, final failure raw는 `trace_raw.jsonl`에 분리
보존되며 116→617 회귀와 validator 미호출이 PASS했다. 다음 Sol/high 검수에서 두 후보 파일 SHA와
helper 경계를 독립 확인하고, actual close transport와 overflow capacity는 별도 카드로 유지한다.

후속 검증자는 raw 수리 뒤 별도 카드로 actual Win32 close transport와 overflow 없는 bounded trace
계약을 확정해야 한다. X11 destroy, process terminate/kill, summary 합성, overflow 은폐, 근거 없는
limit 확대, validator 완화, 같은 run 재실행, G1/M1 승격은 금지한다.
```
