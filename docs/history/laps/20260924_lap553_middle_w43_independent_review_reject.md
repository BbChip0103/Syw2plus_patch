# 2026-09-24 | lap 553 | G2 W43 raw 독립검수

- 실제 provider/model/effort / 지정 역할: Codex native session / model ID 비노출 / high / middle 지정. 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap552 raw만으로 카드 `G2_S1_MOVE_THEN_ATTACK_24K_SOAK_W43_LAP551.md`의 H29~H31과 A1~A8′을 독립 재계산하면 work 판정의 유효 범위와 다음 수리 경계를 정할 수 있다.
- 예상 PASS / FAIL 조건: `run_summary.json`·`sources_summary.json`을 입력에서 제외하고 원시를 2회 동일 재계산한다. 카드 H29/H30/H31 또는 A1/A2/A3/A5/A6/A8′가 불완전하면 W43을 승인하지 않고 `BLOCKED`/FAIL 근거와 work handoff를 남긴다.
- 변경 파일 / source fingerprint / 커밋: 제품 source 변경 0. 검수 전 fingerprint `7f80f4a772b67723946177d7eb5357996e29bf5d`; 문서 4파일과 공유 temp 재계산기만 변경; commit 0(uncommitted).
- 원본 / 후보 SHA / 환경 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`; lap552 격리 Wine `:6552`, 8 AI owner, 100×100, gate-legal 시딩+스크립트 입력. 게임 재실행 0.
- 실행 / 증거: `temp/Syw2plus_patch/g2_capacity/20260924_lap553_middle_w43_review/recompute_w43.py` SHA `06f90b3936668d1e2446611b2935bb53d9f7495a2d428af4aabcba14ca0c2d95`; `recompute1.json`·`recompute2.json` SHA 둘 다 `ecc019c4714c0e7d3441bf06dd549c79e6553e53209130bf31bf82be4f129318`. 입력 SHA는 source_states `f8eb7cf8…cccc`, events `51458d6a…885`, samples `c38cd12e…301`, waves `2102a90a…3ee3`, save/load `176abfb5…862d`.
- 판정: **`REJECT` / `BLOCKED(harness_contract)`**. H29 `layout_plan.json`이 없고 네 짝 전열 사전탐색을 하지 않았다. H30은 홀수 파동도 뒤집지 않아 19/19 파동이 모두 `0→1,2→3,4→5,6→7`였다. A3 필수 `producer_change` 원시는 0건이다. 따라서 lap552 실행은 W43 카드의 fixture/입력 계약을 충족하지 않아 제품 라벨로 승인할 수 없다.
- 부수 raw 재계산(승인 근거 아님): A1 PASS(4,950×8), A8′ PASS(각 owner type2=60/type5=100/type7=26/type46=20, 최대비중70.7%), A6 PASS(save/load 3필드+live 일치, 고유 load 후 사망53). A2 FAIL: death 394행 중 같은 `(slot,uid)` 중복184, 고유210, owner별 `{0:32,1:55,2:0,3:5,4:31,5:82,6:2,7:3}`라 0/1/4/5만 기준 충족. A3 FAIL: op1 수락 `{0:4,1:3,2:18,3:16,4:0,5:2,6:18,7:18}`, 고유 사망 슬롯의 다른 UID 재사용은 전 owner 0. A5 형식상 FAIL: tick11559/13973/14002/17676 네 표본에서 `live=Σcount+1`; 모두 다음 7~8tick 표본에서 수렴했다.
- A5 원인 경계: `w43_run.py:1541~1557`이 pool snapshot을 먼저 읽고 owner counters를 뒤에 읽으므로, 전투 중 사망이 두 읽기 사이에 끼면 관측된 +1과 정확히 일치한다. 이는 **영속 풀 손상 증거가 아니라 비원자적 계측과 일치**하지만, 카드의 전 표본 일치 기준은 임의 완화하지 않아 FAIL을 유지한다.
- 후처리 결함: `w43_run.py:1681~1683`의 `item.get("receipt", {}).get("ok")`는 key가 존재하지만 값이 `None`인 정상 `reserved_nonzero` 항목에서 예외가 난다. raw 완주와 분리하되 반드시 수리 대상이다.
- 회귀 / Fast: 계약 핀 SHA 4건 일치. `make doctor` exit0(original verified; optional runtime manifest 없음), `make check` **835 passed in 498.16s** + ruff/compileall/mypy/`CONTEXT_PASS`, `checks/safety.sh check`=`SAFETY_PASS`. 원본/후보 raw SHA 일치, 제품 source 변경0, 커밋0.
- 미검증 / 승인: 카드 준수 W43 실제 실행, DRIVEN_CYCLE_STABLE, 144k, 멀티, 사용자 마일스톤 모두 미검증. lap552 수치는 비준수 실행의 진단 증거일 뿐이다.
- 다음 한 가지: strategy가 W43 fresh 실행 예산을 다시 열지 판정한다. 허가 시 work는 `G2_W43_HARNESS_CONTRACT_REPAIR_HANDOFF_LAP553.md`의 6개 수리를 테스트로 잠근 뒤 새 격리 게임 **최대 1회**를 실행한다. 자동 재실행 금지.
