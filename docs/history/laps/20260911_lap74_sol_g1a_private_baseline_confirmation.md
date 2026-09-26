# 2026-09-11 | lap 74 | 목표 G1-A fresh private baseline 독립 확인

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier / 진단·계획·확인. 현재 세션 표면은 실제 provider/model ID/effort를 노출하지 않으므로 `gpt-5.6-sol` 실행으로 주장하지 않는다.
- 가설 / 사용자 관찰: lap73 artifact가 고정 원본의 fresh private 1회 run과 1600x1200 root·800x600 원본 surface/input, expected fail-closed와 owned cleanup을 일관되게 보존했다면 좁은 evidence 계약만 middle 확인할 수 있다.
- 예상 PASS / FAIL 조건: 기록된 artifact/원본/private/harness/PNG SHA 일치, 실제 입력 전이, stable-ineligible primary/alternate evidence, production callback 미호출, cleanup, doctor/Fast/safety/runtime doctor가 모두 PASS. 실제 2배 출력이나 누락된 필수 입력은 제품 PASS로 승격하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/helper/tests/binary/fixture/좌표/timeout 변경 없음. 최종 SHA는 `docs/STATUS.md=e1e4a1c04f52fecf42c3271c4a4e8ccca27d7dba1e4d4f11c35239db184c69a9`, active card `2a18ed6802ade6d2ca9e3247fa6fa0e6b4f15e00b95958596bc61984370f84f2`, address map `46de3c7267a130cccb2e1fd25fd77bc05a01343e067fa4d2f47f04e2d2101f8e`다. 소진 marker `loop/ESCALATE_SOL` SHA `c8207e757780b108649b03ada88a2df4554b189e7f78648e43c2242804e578f2`를 아래에 보존 후 제거했고 commit/push 없음. source/test/guards SHA는 `89fddc...813`/`ab344e...ea6b`/`93e3af...8e3`로 lap72~73과 동일하다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본/private EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 binary 없음. 보존 run은 private win32 prefix/Xvfb `:91`, root 1600x1200, game/content 800x600, 기본 2인 임의게임, owner0/1 각 active 2, synthetic/memory writes/control bridge/resource grant 모두 false다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`과 `jq`로 manifest `81455e...ecce`, baseline `a46f4c...198e`, verdict `210560...1be`, provenance `0873e2...4d7`, harness `89fddc...813`, 8개 PNG를 재검산. `make doctor`; `make check`; no-click/output 직접 3 tests; `bash checks/safety.sh check`; `make doctor-runtime MANIFEST=local/runtime/20260911_082430_2926029_0/manifest.json`; 장면·selection 전후 PNG original-detail 시각 점검.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): SHA/PNG 8개 PASS; menu/solo/confirm/auto-ready/start/unit-select PASS, multiplayer normalize SKIP; 1600x1200 root와 800x600 game/content 및 PS9/PS3 PASS; `49B6D0` predicate false/stable, primary/alternate stable, callback 미호출, cleanup `ok=true`/global kill false/prefix processes after 빈 배열. 직접 **3 passed**, 전체 Fast **127 passed**, Ruff/compileall/mypy/context PASS, safety **SAFETY_PASS**, doctor와 runtime doctor `ok=true`. lap73 narrow evidence는 **MIDDLE CONFIRM PASS**; `verdict.overall=FAIL`/`required_inputs=false` 유지.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 실제 2배 출력·입력 역변환, production/drag/minimap, primary field/action·worker 의미, G1-A/G1~G4 및 사용자 승인은 UNKNOWN/미완료다. 새 run은 실행하지 않았다. candidate가 없어 expected new bytes/copy-only/non-overlap/restore/unsupported-version patch 판정은 N/A/SKIP이다.
- 다음 한 가지: 새 Luna/Sonnet5/high work가 고정 원본 `0x00499583→0x004A3A40` 이후 primary cell 생성 경로를 정적으로 추적해 12-slot별 `A6/BE/D6/EE` 인자 provenance·callback/action·strict rectangle·old bytes 표를 완성하고 HQ worker 생산 후보를 유일하게 증명하거나 concrete blocker를 남긴다. game run·harness/tests/binary/fixture/좌표/timeout 변경은 금지한다.

## 소진 전 `loop/ESCALATE_SOL` 원문

# lap73 승격 요청 — G1 fresh private evidence-only run 결과

## 사유

STATUS가 지정한 새 private manifest prepare/check와 고정 원본 `g1-baseline` 1회를 수행했다.
실행은 예상된 fail-closed 경계에서 `49B6D0 ineligible: original command-cell creation predicates are false`로
종료했으며, production mouse callback은 호출되지 않았다. 이는 구현/제품 PASS가 아니고, primary field/action과
worker 생산 연결의 의미가 아직 불명확해 middle 독립 판정이 필요하다는 뜻이다.

## 승격 작업자가 이어서 검증할 것

1. 아래 fresh run 산출물의 manifest·private EXE·harness SHA와 `g1_a`의 primary/alternate/selection evidence를
   독립적으로 재계산하고, `cleanup.ok=true`, `prefix_processes_after=[]`, `global_kill_used=false`를 확인한다.
2. 실제 1600x1200 private Xvfb, 원본 PS9/PS3 800x600 surface, 실제 입력 PASS와 production callback 미호출을
   2단 컨펌으로 판정한다. `49B6D0` predicate false를 eligible production evidence로 해석하지 않는다.
3. primary field/action·worker 생산 의미가 승인되기 전에는 production click, binary patch, 새 fixture 또는
   재실행을 하지 않는다. 필요 변경은 Sol/Opus5가 범위·검증 조건을 정해 Luna/Sonnet5에 이관한다.

## 보존된 근거

- run: `local/runtime/20260911_082430_2926029_0/`
- manifest SHA: `81455eeea2ab0a5c6c72f3904a2ea42e88192120d3acae7cd5790e39aacaecce`
- `output/g1_baseline.json` SHA: `a46f4c659c7e2482ca7371caa0478883b48fffa6bef42e743e6a7b275615198e`
- `output/g1_a/verdict.json` SHA: `210560e5992eee1e5666d95ad9ec8fb82c1e0f545e74e8d07771752bffba01be`
- private/original EXE SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- harness `tools/runtime_env.py` SHA: `89fddce79899fc8cd7b6f1472ab4aefc775605031439726695d45713701d8813`
- command: `.venv/bin/python tools/runtime_env.py g1-baseline --manifest local/runtime/20260911_082430_2926029_0/manifest.json --screen 1600x1200x24 --timeout 90`
- result: exit 2 / expected safety block; `g1_a` verdict `FAIL`, cleanup `PASS`; `make check` 127 passed, `SAFETY_PASS`, `make doctor-runtime MANIFEST=...` `ok=true`.
- no code/tests/binary/fixture/coordinate/timeout changes; no commit/push; product G1~G4 and user approval remain incomplete.
