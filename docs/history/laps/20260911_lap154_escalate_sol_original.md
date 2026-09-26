# 보존 원문 — lap154 `loop/ESCALATE_SOL`

lap155 middle tier가 판정을 마치고 `loop/ESCALATE_SOL`을 제거하면서 원문을 그대로 보존한다.
판정 결과는 `docs/history/laps/20260911_lap155_middle_g1_dxwrapper_finalization_verdict.md`.
아래는 lap154 work tier가 남긴 원문이며 편집하지 않는다.

---

# ESCALATE_SOL — lap 154 G1 dxwrapper 2x finalization blocked

## 승격 사유

필수 fresh `g1-presentation-trace --dxwrapper-2x`를 승인된 후보로 정확히 1회 실행했으나,
native dxwrapper 경로에서 finalization이 90초 deadline 안에 완료되지 않았다. 같은 run 재실행,
timeout 증가, 좌표 보정, validator 완화는 금지한다. 현재 구현·실행 근거와 산출물은 보존되어 있다.

## 다음 중간 검수자가 이어서 판정할 것

1. `trace_raw.jsonl`의 event 384 / summary 0 / process_exited=False와 이전 baseline의
   summary·detach 순서를 독립 대조해, PS3 이후 native dxwrapper가 종료/summary를 막은 것인지
   trace finalization 결선의 관측 결손인지 판정한다.
2. `evidence.json`의 `ddraw=n,b`, installed candidate SHA, private `game/ddraw.dll` 로드,
   1600x1200 client / 800x600 logical surface를 재계산한다. 이미 통과한 config 설치·원복을
   문제 원인으로 추측해 바꾸지 않는다.
3. 원인과 다음 단일 probe를 승인한 뒤에만 새 private copy/prefix/display에서 새 실행을 정한다.
   이 run 및 `/tmp/syw2plus_lap154.yqZjnb`는 재사용하지 않는다.

## 이번 run 증거

- Run: `local/runtime/20260911_200415_300054_0`; fixture는 새 private 전체 copy,
  diagnostic bridge, default two-player random game, memory/resource/control injection 없음.
- Command: `.venv/bin/python tools/runtime_env.py g1-presentation-trace --manifest local/runtime/20260911_200415_300054_0/manifest.json --screen 1600x1200x24 --timeout 90 --win32-close-helper /tmp/syw2plus_lap154.yqZjnb/helper/win32_close_helper.exe --dxwrapper-2x`
- Original EXE SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- Config: source/restore `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`,
  installed candidate `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`.
- Runtime evidence: logical `[800,600]`, physical/client `[1600,1200]`, scale `[2.0,2.0]`,
  input `(184,560)` unscaled, PS9→PS7→PS3, capture 1600x1200, private ddraw loaded
  (`3bc7230d1a6023a8fc0ea52b18d7edda94fcb4c0ae3d178f6e1577d68a62bd19`).
- Finalization: `event_count=384`, `summary_count=0`, `process_exited=False`; verdict BLOCKED.
  Cleanup is PASS (`owned_launchers_stopped`, private prefix empty, Xvfb stopped,
  `dxwrapper_config_restored=true`).
- Evidence hashes: `trace_install.jsonl` `b50f00327d9606124976d4c454416d96726b53fc491d9d98623282a9facf8c9a`,
  `trace_raw.jsonl` `8944ada695054034e748c14755d34f538efdde528300e2b2c6c6a040d1871d9f`,
  `evidence.json` `905effd1630ef9d555062dd2a5800f435476d3f879fd7854d1d11288e07c221e`,
  `provenance.json` `163cdb032c30368cc404cdf942e903b775d463b9a8a807e9174a554066808f5d`,
  `verdict.json` `5e9903a18231100c1d0b53fe389b7ef2df784c98c3c3f42d69407789bed709ca`.

## 구현·검증 상태

- Changed files are uncommitted (commit not authorized):
  `patches/resolution/dxwrapper_config.py` SHA `48d61a6c2e112bd608021483062172691f69c9b4dca096ca8a04d88a0437cbaa`,
  `patches/resolution/test_dxwrapper_config.py` SHA `e4cf7ae410a6a67df5cf81c92d9d86b1c8c846d677aca6e99d1f7ec2582e1d04`,
  `tools/runtime_env.py` SHA `05a6054ea6df1a8d0ba3b3aca23ecec44dd4f6465994ae37cdbe3f1f9901cf4b`,
  `tests/test_runtime_env.py` SHA `782f74ebdaa32e6d6bf9610778fe2d7d849ff1c68287d9ce8ecaeba03d82422f`.
- Targeted tests: 91 passed. `make check`: 182 passed, Ruff/compileall/mypy/context PASS.
  `bash checks/safety.sh check`: `SAFETY_PASS`. `runtime_env check` and `make doctor-runtime` PASS.
- G1 product completion, G2, G3, G4, second-tier confirmation, and user milestone approval remain
  unverified. Do not promote this run's output to baseline/golden or product PASS.
