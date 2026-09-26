# 2026-09-11 | lap 118 | G1 trace contract independent review

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-sol`/high 중간 컨펌 역할 지정. lap117의
  source/tests와 machine evidence만 독립 검수했으며 게임 구현 수정이나 새 runtime은 수행하지 않았다.
- 가설 / 사용자 관찰: lap117 source가 재사용 surface를 fail-closed로 처리하고 clean finalization 뒤에만
  validator를 호출하더라도, lap116 카드가 요구한 행동 회귀가 직접 고정되지 않았다면 fresh runtime을
  허용할 수 없다.
- 예상 PASS / FAIL 조건: source fingerprint·분기·호출 순서와 fresh build/Fast/safety가 일치하고,
  surface 성공/불일치와 close→exit→summary→copy→validator 순서가 실행 가능한 회귀로 고정되면 ACCEPT;
  문자열 존재 검사나 helper 단독 fixture만 있으면 REVISE다.
- 변경 파일 / source fingerprint / 커밋: 구현 파일은 변경하지 않았다. 검수 시작/종료 SHA는
  `direct_draw_trace.c=2b0bd730da5199f86b9efe1097cdee5aa57ccc2ceef47272db786c04dc8a147c`,
  `runtime_env.py=85e9b1af6978c6a860f1b12cc98fb8520e7765a13c17d3f8a35b79b44773f7f0`,
  `test_direct_draw_abi.py=2b2a49449e2d472defe66c20733d7d8dae708529340ebde6397fc5fb27812c1e`,
  `test_runtime_env.py=5a579685f234ef9f16f920028e141a5743d7bda36dbe8f7d5a4ab48206af68db`,
  `test_g1_presentation_trace.py=3ab4bb24f1c0c7c434080b354cdfbdc72544967ed58e74b54f49111b9f423d66`,
  validator `541e8448...`다. 이 lap은 STATUS/history와 Luna handoff만 uncommitted로 추가했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, PE32 보호 PASS.
  제품 후보·게임 실행 없음. 저장소 밖 fresh diagnostic bridge
  `/tmp/syw2_g1_lap118_bridge.8uGfY0/bridge/_inmm.dll` SHA
  `e87cf71673f4f5c226a4cee72f296b70e3af16cf67ff01e299f959b9304810c7`; synthetic/native build와
  unit-test fixture만 사용했고 활성 플레이어·지도·군대 N/A, runtime SKIP다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum ...`, `make doctor`, `make check`, 저장소 밖
  `.venv/bin/python patches/population/build_runtime_bridge.py --out-dir
  /tmp/syw2_g1_lap118_bridge.8uGfY0/bridge`, `bash checks/safety.sh check`, source/test 좁은 대조를
  실행했다. `make check` **156 passed**, Ruff/compileall/mypy/context PASS; doctor top `ok=true`,
  original `verified`; safety `SAFETY_PASS`; PNG와 runtime manifest는 만들지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): source fingerprint, guard 분기, source상 finalization 순서,
  fresh build, Fast, 원본 보호는 PASS다. surface 테스트 1건은 source 문자열 assertion뿐이고
  stale-uninstalled 실행 검사가 없으며, finalization PASS fixture는 summary 사전 존재+process 사전
  종료 상태다. summary 부재 검사는 helper만 호출해 최종 runner의 raw-copy/validator 미호출을
  증명하지 않는다. 판정은 **SOURCE INTENT CONFIRMED / REGRESSION REVISE / GAME RUN BLOCKED**다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 새 runtime으로 두 결함이 실제 해소됐는지는
  미검증이며 G1 2배 출력/입력, G1/M1, G2~G4, 사용자 승인은 모두 미승인이다. 필수 기계 게이트의
  예상 밖 실패나 근거 충돌은 없어서 `loop/ESCALATE_SOL`은 만들지 않았다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high가
  `docs/plans/20260911_lap118_g1_trace_regression_handoff.md` 범위에서 행동 회귀만 강화하고 게임을
  실행하지 않은 채 machine evidence를 남긴다.
