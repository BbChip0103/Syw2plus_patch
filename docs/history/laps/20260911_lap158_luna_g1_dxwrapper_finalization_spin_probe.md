# 2026-09-11 | lap 158 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex work tier `gpt-5.6-luna` / high / hands-on 구현 작업자.
  이번 바퀴는 승인된 P1 실행·증거 수집만 수행했으며, 중간-tier 판정이나 제품 마일스톤 승인은 하지 않았다.
- 가설 / 사용자 관찰: close 이후 native dxwrapper 경로의 게임 프로세스가 살아서 device-lost 재시도
  루프에 갇혀 있다. close 직후와 약 5초 뒤 소유 process tree의 state/CPU 표본 및 wrapper log가
  각각 `R`/CPU 증가와 `DDERR_SURFACELOST` 반복을 보이면 spin(A), CPU 정지와 `S`/`D`면 교착(B)으로
  분기한다.
- 예상 PASS / FAIL 조건: 모듈 실행 helper build RC0·PE32·SHA, bridge build RC0·PE32·SHA,
  `make check`와 safety PASS 후 새 private copy/prefix/display에서 승인된 `--dxwrapper-2x` 실행 1회.
  실행 결과는 정상 종료(C), spin(A), 차단/교착(B) 중 하나로 분류하되 G1 제품 PASS로 승격하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/원본/후보 EXE·DLL/assets,
  `tools/`, `tests/`, baseline/golden은 변경하지 않았다. 이번 바퀴의 저장소 문서 변경은
  `docs/STATUS.md`와 본 기록이며 commit/push 없음(`LOOP_ALLOW_COMMITS=0`).
  관측 harness SHA: `tools/runtime_env.py`
  `25fc64e65ee44896b5ae701bebde884aed623c44f1a5840d3182c0f82f3608a3`,
  `tests/test_runtime_env.py`
  `7654052e53b885d3cb4ab517d3b6432dabfbfd7d327b4c346f6ae4e3d5933074`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; dxwrapper candidate
  `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785` (private install only),
  source ini old `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`.
  Helper/target were freshly built under `/tmp/syw2plus_lap158.pKNrsl/helper`:
  helper PE32 SHA `d61f8ee44a4a291a781a544172eadf9589df46cf38f0a8066fb60e76a33d19f`,
  target PE32 SHA `e607196945202d1c1e751b73a88b407f18fce5ecadca69f7d75ace546250f572`.
  Fresh bridge `/tmp/syw2plus_lap158.pKNrsl/bridge/_inmm.dll`, PE32 DLL SHA
  `6c2168fb329ec6cd8fa31b3a5de1d66db4152994b7c3a4cd6c35fdf09f05fb3c`. Runtime run
  `20260911_202808_512099_0`, new private copy/prefix/display `:91`, default two-player random game,
  no memory writes/resource grants, no G2~G4 fixture.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 -m tools.win32_close_fixture build --out-dir
  /tmp/syw2plus_lap158.pKNrsl/helper` → RC0; `python3 patches/population/build_runtime_bridge.py
  --out-dir /tmp/syw2plus_lap158.pKNrsl/bridge` → RC0; `make check` → 186 passed, Ruff/compileall/
  mypy/context PASS; `bash checks/safety.sh check` → `SAFETY_PASS`.
  `.venv/bin/python tools/runtime_env.py prepare --bridge /tmp/syw2plus_lap158.pKNrsl/bridge/_inmm.dll
  --timeout 60` → RC0. 정확히 1회 실행한 trace 명령은 manifest
  `local/runtime/20260911_202808_512099_0/manifest.json`, screen `1600x1200x24`, timeout 90,
  helper `/tmp/syw2plus_lap158.pKNrsl/helper/win32_close_helper.exe`, `--dxwrapper-2x`였다.
  Evidence root는 `local/runtime/20260911_202808_512099_0/output/g1_presentation_trace/`이며
  `evidence.json` SHA `bb6892d8cd47e2f7e38d8e1c979d6ee27246fff40e03ab23084be1999c40c503`,
  `verdict.json` SHA `5c54c25b05976edb4652c18703a7b47d922c1698df44ce8a79078175736261c`,
  `provenance.json` SHA `fc754f1fa55f775aee59756acdc226ca150346a740084e6f9929fe85a2e71eac`,
  `trace_raw.jsonl` SHA `96ca0f41f65b28fa6cd4249bece0d800af577ad76b0f5e49714ba8b8519ae121`,
  `trace_install.jsonl` SHA `fa03ab8f777a3d448f226eff9c11db80c1774db01111416e61988053d365574b`,
  `g1-presentation-trace.log` SHA `0f91ea7e9b8d1feb5efa16a7e37d51c4e8c33ee5d1c68bb5067e00a7db5f0cbf`다. 1600×1200 capture와 논리
  800×600, scale `[2,2]`, `(184,560)` 선변환 입력 PS9→PS7은 PASS했다.
  close 직후 wrapper 핵심 log `dxwrapper-syw2plus_original.log`는 15,900 bytes,
  SHA `509abf67f7380d26efd0357239092c9bb885532f6b02f4d3c7fa79187ef33c5a`이며 8개
  `dxwrapper-*.log`가 모두 output `wrapper_logs/`에 복사·해시 기록됐다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): helper/bridge build PASS(각 RC0, PE32), Fast PASS,
  safety PASS, prepare PASS. close transport는 `requested_pid=276`, `matched_hwnd=0x00020056`,
  `matched_thread=280`, `match_count=1`, `post_result=true`로 PASS했다. 그러나 trace는 RC2,
  `event_count=384`, `summary_count=0`, `process_exited=False`, 90.183초 후 finalization
  timeout으로 BLOCKED했다. liveness 표본은 약 5초 간격으로 (1) pid 513547, state `S`,
  utime 2650/stime 382, threads 36 → (2) state `R`, utime 2962/stime 385, threads 36으로
  총 CPU jiffies 3032→3347 증가했다. wrapper log에는 close 직후 `Lock2 Error: failed to
  lock texture surface! DDERR_SURFACELOST`가 반복됐다. 따라서 **A: 살아서 spin/device-lost
  재시도 계열**로 판정한다. private config는 old SHA로 원복, sidecars 제거, owned launchers/
  Xvfb 종료, prefix 잔류 프로세스 0, `global_kill_used=false`, cleanup PASS.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본/제품 binary와 baseline/golden 변경 없음.
  timeout·summary 요구·좌표·wrapper profile은 바꾸지 않았다. G1 제품 PASS가 아니며 정상 teardown,
  summary 1, DLL detach, validator는 여전히 미충족이다. 이번 1단 기계/실행 evidence는 다음 새
  중간-tier가 독립 검수해야 하고 사용자 마일스톤 승인은 없다.
- 다음 한 가지: 중간 tier(Sol/Opus5)가 분기 A와 raw/wrapper/liveness evidence를 독립 확인한 뒤,
  wrapper의 device-lost/reset 처리 옵션 **한 개**를 선택·승인한다. 다음 work 바퀴는 그 승인 범위
  밖의 설정·종료 방식·재실행을 추가하지 않는다.
