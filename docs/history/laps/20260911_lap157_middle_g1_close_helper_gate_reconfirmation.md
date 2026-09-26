# 2026-09-11 | lap 157 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`(세션 표기), effort 표기 high.
  지정 역할 middle tier(진단·계획·확인). 게임 코드 hands-on 구현은 하지 않았다.
- 가설 / 사용자 관찰: lap156의 `ModuleNotFoundError: tools.win32_close_transport`는 새 결함이 아니라
  lap142에서 이미 발생하고 lap143에서 독립 재현·확정된 **호출 경계 오류의 재발**이며,
  helper source·MinGW·lap156 변경과 무관하다.
- 예상 PASS / FAIL 조건: (a) helper/transport source SHA가 lap143 확정치와 동일하고,
  (b) `tools/win32_close_fixture.py`가 sys.path bootstrap 없이 절대 package import를 쓰며
  `tools/__init__.py`가 없으면 direct script 실행 실패는 결정적이다 → 원인 확정 PASS.
  source SHA가 달라졌거나 bootstrap이 존재하면 새 원인으로 보고 재조사 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`(사전 빌드 명령 고정 + 진행 상태),
  `docs/STATUS.md`, 본 기록. `loop/ESCALATE_SOL` 제거(처리 완료).
  게임/원본/제품 EXE·DLL/assets/baseline/golden/후보 config/`tools/`/`tests/` 변경 없음.
  `LOOP_ALLOW_COMMITS=0`, uncommitted, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 원본 EXE 기대 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(이번 세션 미실행 검증).
  `tools/win32_close_fixture.py` `f7f567a10aed115a83c0337354a1863684bc9a837e6940e72bf37b06783e0456`,
  `tools/win32_close_transport.py` `c211d8e5e48339dcdcabb7da0c4205bd2b44503f3145bb109c048943dd768143`,
  `tools/win32_close_helper.c` `51f71d82912596abd8d938f0bcafaf2f6507ff88d4b4fee88e2af710dd68c4ff`,
  `tools/win32_close_target.c` `cda43cd28c9d77751fae28d3e14b40d801e26b974d1e06ea2a997a58424ade0c`
  — 네 값 모두 lap143 확정치와 **일치**(회귀 없음).
  `tools/runtime_env.py` `25fc64e65ee44896b5ae701bebde884aed623c44f1a5840d3182c0f82f3608a3`,
  `tests/test_runtime_env.py` `7654052e53b885d3cb4ab517d3b6432dabfbfd7d327b4c346f6ae4e3d5933074`
  — lap156이 기록한 fingerprint와 일치. 게임 fixture/prefix/display/활성 플레이어 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: **이번 세션은 명령 실행 권한이 없다.** 비대화형 harness가
  `python3`, `make`, `printenv` 등 실행을 거부(`This command requires approval`)해
  helper build/`make check`/pytest/runtime을 한 건도 실행하지 못했다. 근거는 read-only 도구
  (`sha256sum`, `grep`, `ls`, 파일 읽기)로 수집한 정적 증거와 lap143의 동일 SHA 실행 증거다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **원인 확정 PASS**: `tools/win32_close_fixture.py:16`은 `from tools.win32_close_transport import …`
     절대 package import이고, 같은 파일에 sys.path bootstrap이 없으며 `tools/__init__.py`도 없다
     (비교: `tools/check_setup.py:19`, `tools/runtime_env.py:2042/2518/2799`는 bootstrap을 가진다).
     direct script 실행은 sys.path[0]이 `<repo>/tools`가 되어 `tools` 패키지를 찾지 못한다.
     lap143이 동일 SHA에서 direct FAIL(RC1) / `python3 -m tools.win32_close_fixture` PASS를 실행으로 확인했다.
     → lap156 실패는 **도구/코드 결함이 아니라 호출 방식 오류의 2회차 재발**이다.
  2. **lap156 P1 관측 구현 정적 확인 PASS(코드 리뷰 한정)**:
     `_finalize_presentation_trace`가 close 결과를 대기 **전에**
     `evidence["trace_finalization"]["close_transport"]`에 넣고 예외 경로에서도 보존한다
     (`tools/runtime_env.py:963-981`). `_wait_for_clean_trace_close`는 소유 root pid 기준
     `_owned_runtime_process_snapshot`으로 즉시 1회 + 약 5초 뒤 1회를 남긴다(:924-941, 전역 스캔 없음).
     `_preserve_dxwrapper_logs`는 `game/dxwrapper-*.log`를 symlink 제외·복사만 하고 SHA/bytes를 남기며
     (:991-1005) 실패 경로를 포함한 cleanup 블록에서 호출된다(:2710).
     `uninstall_private`는 `dxwrapper.ini`와 sidecar만 건드려 로그를 지우지 않는다
     (`patches/resolution/dxwrapper_config.py:156-168`) → 복원 후 복사 순서 안전.
     테스트 4종 존재: `tests/test_runtime_env.py:302, 326, 356, 377`.
  3. **한계/미검증 SKIP**: pytest·`make check`·safety·helper build RC0/SHA·PE32 import·fresh runtime은
     이번 세션에서 실행하지 못했다. lap156의 `186 passed`/`SAFETY_PASS`는 재현하지 않았으므로
     기계 게이트는 여전히 **다음 work 세션이 재실행해 확인**해야 한다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 코드 변경 없음이므로 회귀 없음.
  남은 위험 (a) liveness 2번째 표본은 대기가 약 5초 이상 지속될 때만 생긴다 — lap154 재현 분기
  (미종료·timeout 90초)에서는 충족되나 분기 C(즉시 정상 종료)에서는 1개만 남는다. 허용한다.
  (b) 재발 방지용 `tools/win32_close_fixture.py` sys.path bootstrap 추가는 **이번 P1 범위 밖**이라
  승인하지 않았다. runtime 관측이 끝난 뒤 별도 단일 변경으로 제안한다.
  사용자 마일스톤 승인 없음. G1 제품 PASS 아님.
- 다음 한 가지: work tier(Luna/high 또는 Sonnet5/high)가 갱신된
  `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`의 "사전 빌드" 블록대로
  `python3 -m tools.win32_close_fixture build --out-dir <fresh-parent>/helper`로 helper를 1회 빌드해
  RC0/PE32/SHA를 기록하고, 그 게이트가 PASS한 뒤에만 새 copy/prefix/display에서
  `--dxwrapper-2x` runtime을 정확히 1회 실행한다.
