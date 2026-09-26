# 2026-09-24 | lap 555 (fresh continuation) | 목표 G2

- 실제 provider/model/effort / 지정 역할: Codex native session / hands-on work / high.
- 가설 / 사용자 관찰: lap555의 기존 `bridge_build` 충돌을 피한 비중첩 디렉터리에서 W43R fresh 1회가 T0 이후 24k로 진행되어야 한다.
- 예상 PASS / FAIL 조건: 핀·합성 회귀·계약·안전 PASS 후 H29 실제 배치와 H20을 통과해 op9/op8 순환을 시작해야 한다. T0 H20 실패는 제품 합격이 아닌 BLOCKED/ESCALATE다.
- 변경 파일 / source fingerprint / 커밋: 제품 소스 변경 0. 실행용 temp에 `w43_run.py`를 복사했으며 SHA `43be0aa8f96f20429d6e6cd77b3aeac7b71bdd0e7f09550959e02cd3ed8fd14f`. 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`, 새 bridge `_inmm.dll` `eecb6637f06f085f94808d761d71c0813963c44b1fa2e2b222bd18f0785ad58`. fresh prefix/display `:6552`, 8 owners, 100×100 지도, type5/7/46 및 type2(60) gate-legal fixture.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 temp/Syw2plus_patch/g2_capacity/20260924_lap555_w43r_fresh_s1_2stage_24k/w43_run.py`, foreground 2026-09-24 16:30:03~16:30:39 KST. `run_summary.json` `acea400f3c64c2c2e57a14b79b79f9280253b7fe2496a618a9dc026743003938`, `w43_orchestrator.log` `28d8894dbafce8fc7af6883324289a77c15e4315f38cfcc03eafdfc626e9e515`, `layout_plan.json` `a05934d5b59d4879e7d760f2a5051d45c00a4c1bbd03145f86341581a0c7dd70`.
- 측정값 / 판정: bridge/candidate build PASS; PS3 진입 PASS; cap `[5000]*8` PASS; H21a 8/8 PASS; H29 planner `complete=true`, 735 candidates. 실제 T0는 `H20_front_placement_failed`: pair(0,1) gap rows 15~19 점유, pair(2,3) row25 점유, pair(6,7) rows60~66 점유, owner6/7 type2 layout mismatch. `A1=4950×8`, `A8'` PASS이나 `H20_pass=false`; op9/op8/24k/save-load/생산·사망 0. 판정 `ARM_FAIL`, 자기 라벨 `PROBE_VOID`, 재시도 0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `checks/safety.sh check`=`SAFETY_PASS`; 잔류 게임/Xvfb 0; source SHA 전후 동일. H29 계획과 실제 op5/op6 배치 결과의 불일치 원인은 미판정이며 middle/strategy 독립 검수가 필요하다. 24k/144k·G2 제품 PASS·사용자 승인은 미검증.
- 다음 한 가지: 승격 middle이 summary를 제품 결과로 쓰지 말고 `layout_plan.json`, `seed_receipts.json`, `t0_positions.json` 및 원시 배치/fixture 규칙을 대조해 H29 planner-실제 배치 불일치를 분류한다. 재실행·anchor 추측 수정·144k 발행은 하지 않는다.
