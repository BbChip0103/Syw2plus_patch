# 보존 — lap152 `loop/ESCALATE_SOL` 원문

lap153 middle tier(Claude Code `claude-opus-5`)가 요청된 판정을 내린 뒤 `loop/ESCALATE_SOL`을
제거했다. 아래는 제거 전 원문 그대로이며 근거로 보존한다. 판정은
`docs/history/laps/20260911_lap153_middle_g1_dxwrapper_config_apply_boundary_verdict.md`에 있다.

---

# ESCALATE_SOL — lap 152 G1 physical 2x runtime blocked

## 상태

이번 바퀴의 필수 fresh runtime은 정확히 1회 실행했다. 선변환 없는 논리좌표 입력과
종료/정리 경로는 통과했지만, 제품 G1의 1600×1200 물리 client가 관측되지 않았다.
재실행·좌표 보정·validator 완화·추가 설정 적층을 이 세션에서 하지 않는다. 아래
runtime과 `/tmp/syw2plus_lap152.8fFRM7` 산출물 및 해시는 다음 승격 작업자가 독립 검수한다.

## 근거

- 승인 source symlink 사전 점검: `find /home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus -type l -print` → 빈 출력.
- 원본 source/새 private copy EXE SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- fresh helper/target/bridge: `/tmp/syw2plus_lap152.8fFRM7`; PE32; SHA
  `c71a6b33aa442101ba0bc5eea87c46ecdc0b833eaef3fd9c1e72db3a8b300786`,
  `06a0dece904d22d6db165fd79b93d07655a37259afcc5fd59d418aa9fed878a0`,
  `24f81378601af56c53e47250ae2538579612190c534cf099c0ccc4a4ed513af4`.
- `make doctor`: PASS; `make check`: 179 passed, Ruff/compileall/mypy/CONTEXT PASS;
  `bash checks/safety.sh check`: `SAFETY_PASS`; manifest check와 `make doctor-runtime`: PASS.
- 실행 명령: `.venv/bin/python tools/runtime_env.py g1-presentation-trace --manifest local/runtime/20260911_194932_189255_0/manifest.json --screen 1600x1200x24 --timeout 90 --win32-close-helper /tmp/syw2plus_lap152.8fFRM7/helper/win32_close_helper.exe`
- manifest/source/candidate: `local/runtime/20260911_194932_189255_0/manifest.json`,
  manifest SHA `7e2970b698d2e5286fb989738317552001d8d84c979f02658e05b9cc58514747`.
  private `dxwrapper.ini`는 source와 `cmp=0`, old SHA
  `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`였다. 승인된
  2x candidate SHA `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`는
  이 run에 적용되지 않았다.
- 결과: requested screen/root는 1600×1200이지만 `content_child`, `physical_content_size`,
  캡처가 모두 800×600, scale `[1.0,1.0]`, `scaled_2x=false`. DirectDraw logical
  surface는 800×600으로 유지됐다.
- 입력/상태: `logical_content=[184,560]`, `x11_sent=[184,560]`, 선변환 없음;
  PS9→PS7→PS3, tick 10, 입력 효과 PASS.
- 종료/증거: process exit 0, DLL detach complete, summary 1건, event 651,
  dropped/overflow 0, validator PASS, owned-only cleanup PASS.
- 증거 경로/해시:
  `local/runtime/20260911_194932_189255_0/output/g1_presentation_trace/evidence.json`
  `fee75b439fb8e7861d7019026b38db72e43ae2c3b13ad99b5df0bfbf984d154f`,
  `trace.jsonl`/`trace_raw.jsonl` `790ef90869cc1776fdcff25fde7533b78586cc001cb8d7227b44cdf44f5366dd`,
  `trace_install.jsonl` `ff0944a34f30d52bc5fb438939a83c9ba4cb2751ed79e26049c93fc958ca226e`,
  `provenance.json` `0d02380725c707f5da988a129fe2bc43a64c0d6ef2287aa5d630fe6e7c2ba69e`,
  `verdict.json` `f2709ce81294d47ee8e5bb82cdcfe74d658998d0dce54489b9daeba2e9b540f9`.
  PNG는 `temp/20260911_195005_...ps9_before_menu...png`,
  `20260911_195006_...ps7_lobby...png`, `20260911_195007_...solo_mode_selected...png`,
  `20260911_195010_...ps3_scene...png`이며 모두 800×600이다.

## 판정

`verdict.json`의 validator PASS는 허용 client 크기 중 800×600도 허용하는 기계 판정이다.
제품 G1 합격식의 `client 1600×1200 + scale 2.0×2.0`은 FAIL/BLOCKED이며, 이번 결과를
G1 완료나 milestone 승인으로 승격하지 않는다. 입력 계약 자체와 finalization은 PASS로
기록하되, 2x 표시 후보의 실행 증거는 없다.

## 승격 작업자가 이어서 검증할 것

1. Sol/Opus 중간 tier가 `patches/resolution/dxwrapper_config.py`의 old/candidate
   바이트·offset·원복 계약과 private copy 적용 경계를 독립 판정한다. source/reference와
   원본 EXE/DLL/config는 쓰지 않는다.
2. 적용이 승인되면 다음 work가 새 helper/bridge, 새 private copy/prefix/display를 만들고
   candidate `f0ce...6785`가 실제 private `dxwrapper.ini`에 적용됐음을 manifest/byte hash로
   증명한 뒤, 별도 fresh run에서 trace를 정확히 1회 실행한다. 이 run의 PS9→PS3 성공과
   1600×1200 client를 함께 확인하기 전에는 G1을 닫지 않는다.
3. 이번 run의 `runtime_env.py` harness SHA는
   `69d0c54da7da06849ef8a6929ad7e6fec43bf12b87fefb6ba3e605cee240a296`이며, G2~G4와
   사용자 승인은 계속 미검증이다.
