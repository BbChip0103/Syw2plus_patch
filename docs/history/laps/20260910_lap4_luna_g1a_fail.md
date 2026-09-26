# 2026-09-10 | lap 4 | G1-A 무패치 기준 장면·입력·출력 경계

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-luna` / high / hands-on work.
- 가설 / 사용자 관찰: 1600×1200 전용 display에서 원본의 800×600 surface와 X11 content/입력 경계를
  관측하면 후속 2배 출력 probe의 최소 변경 지점을 결정할 수 있다.
- 예상 PASS / FAIL: 새 격리 원본, 1600×1200 root, 800×600 crop, PS9→PS7→PS3, surface/module,
  scene 및 필수 입력 5종과 cleanup이 같은 run에서 관측되면 G1-A PASS; 하나라도 없으면 FAIL.
- 변경 파일 / source fingerprint / 커밋: `tools/runtime_env.py`, `tests/test_runtime_env.py`,
  `loop/ESCALATE_SOL`, 이 기록, `docs/STATUS.md`; uncommitted / unborn HEAD.
  harness SHA256: runtime_env `8c0aee8dc0ef1581593e8b57388c403dbbd9cfbc57a40d55451176f93cf6755d`,
  test_runtime_env `efc111e6260b52ca5267d014947c53458199abf91e43a1feef92dddc888de2d0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 및 격리 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음.
  `:91`, Wine win32, Xvfb 1600×1200×24, 새 무수정 원본 기본 2인 임의게임, 실제 활성 장면 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `prepare --timeout 60`; manifest check; 
  `g1-baseline --manifest local/runtime/20260910_234422_3307619_0/manifest.json --screen 1600x1200x24 --timeout 90`.
  run 산출물은 `local/runtime/20260910_234422_3307619_0/output/g1_a/`에 보존.
  메뉴 전 캡처 SHA `277a0b23b836e30508326efa0295aa0c35f09a6a9fc4f55fa2b121b09ce5b252`,
  PS7 캡처 SHA `c0154462e1df4e5f4bc6936b670fc15cc2de0eb0a964425bd04a3e14fbb15489`.
- 측정값 / 판정: root `[1600,1200]`, game/content `[800,600]`, menu `PS9→PS7` PASS;
  PS7 visible screen after menu is `여럿하기/혼자하기`. fixed `(608,564)` input led to `PS13,tick0`,
  not PS3. surface PS3/scene/selection/drag/minimap/production SKIP. cleanup PASS, no prefix PIDs.
  Overall **FAIL**; no product or G1 approval.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인: `make check` 80 PASS. 필수 actual gate failed;
  next Sol/high must independently determine PS7 visible transition and whether the card coordinates
  need a middle-tier revision. No binary changed; no old bytes/candidate patch exists.
- 다음 한 가지: Sol/high review of preserved G1-A run and PS7 transition; do not retry in this worker lap.
