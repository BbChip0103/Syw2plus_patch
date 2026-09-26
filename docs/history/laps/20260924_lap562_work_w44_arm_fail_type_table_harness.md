# 2026-09-24 | lap 562 | G2 W44 혼합 구성 안정 동작 24k + 저장/로드

- 실제 provider/model/effort / 지정 역할: Codex hands-on work / 현재 세션 모델; W44 구현·실행 작업자.
- 가설 / 사용자 관찰: type5→type7→type2→type46을 8 owner에 시딩하면 B1/B2를 통과하고 AI 자연 동작·tick≥16k 저장/로드·24k를 관찰한다.
- 예상 PASS / FAIL 조건: B1 `used∈[4900,5000]` 8/8, B2 네 타입 보유·type2≥10·단일 타입 비용 비중≤0.85; 이후 B3~B6. 재시도 0.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): temp 파생 하네스 `.../20260924_lap562_w44_stable_mixed_24k/w44_run.py`(SHA `314bb6e846dc627f7d7c574ed173420bacc121cdbfbbce541a33c7259a3f8b1f`); 제품 source 0; 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`; fresh Wine prefix/display `:6553`; PS3 8 AI, cap `[5000]*8`; gate-legal resource + `{type5:100,type7:25,type2:60,type46:20}` per owner.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 .../20260924_lap562_w44_stable_mixed_24k/w44_run.py`; raw dir `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260924_lap562_w44_stable_mixed_24k/`; `run_summary.json` SHA `5d1d587a46a9840ea329b74c61a1461f6f1422de9ddb143b9c9fcf5c0ccdb2d5`; `seed_receipts.json` SHA `75a38eebabdbbd6211f06e3f9dc992f958d3b1cbbcb119d66db297247fb05b1d`; `t0_positions.json` SHA `04653a7c418a2edf7a8ac424a7d7e73d9bbc4201ed92c1670cf79fb06815e014`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): PS3/cap/8 AI PASS; seed shortfall 0; T0 `used=4950×8`, live=1656, 실제 타입별 owner `{5:100,7:26,2:60,46:20}`(초기 type7 1기 포함). 하네스가 잘못된 type-table 주소 `0x004F4C00 + type*0xA4`를 사용해 비용을 깨뜨려 B2를 `False`로 오판하고 `ARM_FAIL`로 종료. **`BLOCKED(harness_contract)`**, B3~B6 SKIP, 저장/로드·24k 0회.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 사전 `py_compile`, import 합성, forbidden-order static, `SAFETY_PASS`; `make check` 835 passed/501.20s, Ruff/compileall/mypy/CONTEXT_PASS. source after 동일, residual process 0. type-table 주소를 고쳐도 재실행은 하지 않음. G2 PASS·사용자 승인은 없음.
- 다음 한 가지: middle이 새 게임 없이 raw와 W43 주소 근거를 독립 대조해 B2 오판을 `harness_contract`로 확정하고, strategy가 재실행 여부를 별도 판정한다.
