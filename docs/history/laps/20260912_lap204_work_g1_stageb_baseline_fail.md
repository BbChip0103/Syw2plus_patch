# 2026-09-12 | lap 204 | 목표 G1 Stage B 원본 실행 — FAIL 승격

- 실제 provider/model/effort / 지정 역할: work tier. 이 세션에서 모델의 전체 식별자는 노출되지 않으며,
  라우팅 계약상 Codex `gpt-5.6-luna` / high 작업 범위로 수행했다.
- 가설 / 사용자 관찰: 새 private 원본의 800×600 논리 입력이 1600×1200 실행 환경에서
  `unit_select`와 fixed-coordinate `drag_select`에 대해 재현 가능한 상태 효과를 보인다.
- 예상 PASS / FAIL 조건: `unit_select` count 0→1, `drag_select` count 1→2, minimap camera 절대 결과와
  단계별 evidence가 남으면 원본 측 PASS; 단계 효과 미관측은 FAIL로 보존하고 후보/수리를 중단한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 source/tests/EXE/DLL/assets/baseline/golden
  변경 0. 새 runtime evidence만 생성. `tools/runtime_env.py` SHA
  `3add9254f8df892292619940310a40cd38a95b1fd15605da5fd2c9d1f1f2f2c1`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 및 fresh copy
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 미생성/미실행.
  manifest `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch/local/runtime/20260912_022912_3830565_0/manifest.json`
  SHA `7c08b7716a98158513074c1d33e72ea9be6953fda764194cdfcd063ff37019e1`.
  새 private Wine prefix, 빈 Xvfb `:91`, root `1600×1200×24`, game/content `800×600`, logical scale `[1.0,1.0]`.
  default two-player random game; seed 미노출. 관측 active units owner0=2/owner1=2; resource grant·memory write 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python tools/runtime_env.py g1-baseline --manifest
  <run>/manifest.json --screen 1600x1200x24 --timeout 90` (process exit 2).
  evidence `output/g1_a/evidence.json` SHA `ec6ef7e00ca7c2e33d0fdb9f056dcf905425b57c7f559d05edb3b3349a7bbc12`,
  verdict SHA `940301af5ab797c532f2bc3676e61d9e7f63adb7b052e799ab8a70359a644ac9`,
  provenance SHA `9a5fe61cf032b1b8cf0962de73a17fad7f8746b1bc783735b7c75ab738113c53`,
  inputs SHA `29e328394ba57f367d7cbd91a33885fb6c70ba1cdbb641925e6c3da699e4e05b`.
  PNG는 공유 temp에 보존됐고 evidence의 각 경로/SHA를 원문으로 유지한다. 대표 캡처:
  `selection_after` `ab8549cc55fb39cb80357ddb12bdbe306765026d1eae41e8aaf46b33d70e59db`,
  `drag_before` `16b79b4bf55fe4674654d4469e22a74c15026e0692ed6942fddee744f0d5278a`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): menu PASS; `unit_select` PASS count `0→1`, selected
  slot/type `1199/70`; production은 승인된 mapping 부재로 click 미전송 `BLOCKED`, `waited=false`;
  `drag_select`는 logical `(350,180)→(550,350)`, crop offset `(0,0)`, scale `(1,1)`에서 count가
  `1→2`로 되지 않고 마지막 관측 count `1`, slot/type `1198/21`이라
  `FAIL_NO_EFFECT` (`FAIL_NO_EFFECT: fixed owner0 HQ/worker drag did not select >=2`).
  drag wait `9.757s`, input phase `10.604s/31.5s`, `minimap` 미실행. cleanup `ok=true`, prefix 잔류
  process 없음. Overall `FAIL`, required_inputs `false`; candidate run `SKIP`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 코드 회귀 테스트/Fast는 이 runtime FAIL 뒤
  재집행하지 않았고 lap203의 `make check` 221/safety/setup PASS를 현재 run의 승격 근거로 재사용하지 않는다.
  이 실패는 두 fresh run의 scene seed가 노출되지 않는 fixed-coordinate 장면 의존성인지, 원본 입력/검증
  결함인지 middle이 독립 판정해야 한다. G1 제품 승인·출시 승인 없음; 사용자 실행 승인 범위 안이지만
  bounded repair와 fresh validation이 필요하다.
- 다음 한 가지: 승격된 middle이 새 run을 재사용하지 않고 원인·수리 범위·검증식을 확정한다. 그 전에는
  후보 `g1-presentation-trace --dxwrapper-2x --g1-input-sequence`를 실행하지 않는다.
