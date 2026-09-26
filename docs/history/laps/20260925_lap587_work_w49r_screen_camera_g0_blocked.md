# 2026-09-25 | lap 587 | 목표 G2

- 역할/모델: hands-on work, Codex native.
- 가설: receipt snapshot 수리 후 원본 입력만으로 local owner 화면을 맞추면 W49R의 V1 화면 gate가 성립한다.
- 변경파일: 제품 source·원본·parent·기존 raw는 변경하지 않았다. 새 파생 runner를 기존 lap584 디렉터리에서 복사해 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260925_lap587_w49r_screen_camera/w49r_run.py`로 만들고, 허용 범위의 새 display `:6560`·캡처 접두사만 적용했다. runner SHA `ee1a6dd5317c719277a31c90ca68ff71731d2b8fc90437804988ffe5e93d114a`.
- 원본/후보 SHA: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 전후 동일; base `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`; F4 결합 후보 `dfdc91adb88a732d96dff96f78648f03406003bffce1b22a7e5836317f963883`; reverse=`base` true; parent `82d08bd1a97737740ce1fe1559cc0a90a21ce2704b6dd188be3697e3985357d0`.
- fixture/환경: fresh copy·prefix·display `:6560`, 8 AI, map100×100, cap5000, W49R mixed fixture는 고정했으나 G0 실패로 seed/resource op는 0회; goal `_custom_game_chain_inject_g2_eight_ai_seed42`로 PS7→PS3 도달, local index0, target `[95.0,7.0]`, camera `[94,6]`.
- 실행명령: 사전 `py_compile`, lap583 criterion probe(canonical `82024e73c20eb01433793660df9cdf1ccd889be9ec5143329a5bf1fb20665a03`), 양성/음성 V1·V2 synthetic, op/source pin, `checks/safety.sh check`; 이후 `python3 .../lap587.../w49r_run.py` foreground 1회; 사후 `make check`.
- 측정: `g0_before` V1 `0.009159`; H1 방향키 0회, camera unchanged, V1 `0.009159`; H2 minimap click, camera unchanged, V1 `0.108307`; 모두 `<0.30`. 새 PNG 3장/manifest/run_summary 보존, manifest SHA `6d3c9956b9f5c7bbcce779f0ea89ad4992286926be35aad8793e1527`, summary SHA `d54dfdfed9894f78038da3a74e538b1a54142ef7fecf31a60776521c39ed5744`, samples 0B.
- 판정: `BLOCKED(capture_contract)` — 카드 고정 규칙에 따라 시딩·T0·+2000·+10000·미니맵 후속 캡처를 수행하지 않았고 재실행하지 않는다. V1/V2/V3/R·화면 PASS·G2 PASS는 미검증이다.
- 안전/검증: summary의 finally 직전 owned residual 목록은 기록됐으나 사후 `ps`/`pgrep`, display lock에서 게임·Xvfb·대상 잔류 0; 기존 lap584 디렉터리 raw는 별도 보존. 현재 `make check` **835 passed in 496.50s**, Ruff/compileall/mypy/`CONTEXT_PASS`, `checks/safety.sh check`=`SAFETY_PASS`. 커밋 0.
- 다음: 새 middle이 summary를 신뢰하지 않고 새 PNG/manifest/samples와 H1/H2 receipts를 독립 재계산·직접 확인한 뒤 추가 실행 없이 strategy S5′로 승격한다. 화면 축 재실행·새 Wine/DLL·카메라 메모리 쓰기·fixture/op 변경은 금지한다.
