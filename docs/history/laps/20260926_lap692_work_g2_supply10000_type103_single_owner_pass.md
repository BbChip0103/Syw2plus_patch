# 2026-09-26 | lap 692 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5, high, work(실무).
- 가설 / 사용자 관찰: lap691 다음 한 가지("`+0x2012`가 살아있는 프로세스에서 10000으로 읽히는지
  확인, 브리지를 cost40 계열 type으로 확장하거나 개인 상한(250)을 조정하는 것 중 하나를 선택")를
  실행한다. "묻지 말고 결정" 상시지시로 **브리지 확장**을 선택(원본 개인 개체 상한 필드는 그대로
  두는 편이 더 보수적 변경). pinned type_costs.json의 cost40 후보(28/29/104/108)를 op=5/6
  fixture_type allow-list에 추가하면 owner 1인이 10000 전비에 도달하는지 실측한다.
- 예상 PASS / FAIL 조건: 격리 사본에서 owner0 하나가 fixture로 `+0x200c`(used)==10000에
  도달하고 `+0x2012`(supply_cap)가 10000으로 읽히면 PASS. 원본 SHA 불변, 제품 EXE 무변경,
  `make check`/`safety.sh` 유지가 필수.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 수정
  `patches/population/runtime_bridge.c`(op=5/6 fixture_type allow-list을 {5,7,46,2}에서
  {5,7,46,2,28,29,104,108,103}로 확장, SHA `923fd1e1…8da8f1`),
  `tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py`(정확 집합 pin 갱신 + 위반
  주입 회귀 갱신, SHA `524988b9…4d56eefe`); 신규
  `tools/g2_supply10000_type28_seed_probe.py`(SHA `030e527a…91693dd74a`, 타입 테이블 실측 +
  bin-pack fixture probe). `tests/test_g2_runtime_bridge_op8_order_engagement_contract.py`의
  기존 substring 가드는 무변경으로 통과(하위집합 `!=2u`가 여전히 리터럴로 존재). 원본/참고
  저장소 무변경. uncommitted(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(5회 실행 전부 불변,
  `source_unchanged: true`). 후보(supply-cap 10000 immediate 패치, lap691과 동일)
  `039a358ca3e8031ce316bd57e8a66df0358babeba3a544d3e850f740cebc6a1d`. 브리지 DLL은 매 실행
  재빌드(최종 `bridge_sha256` `6c3702582b5ec18c8cab168c7f10e278ae97c9d2d7eb6e37df4780187113c348`).
  환경: `tools/runtime_env.py prepare(bridge=...)`가 만든 격리 사본+전용 32-bit Wine prefix+
  전용 Xvfb, `local/runtime/20260926_2230xx..2236xx` 5회(모두 `game/` 즉시 삭제, `output/
  manifest/prefix` 보존). 활성 플레이어: owner0 단독(solo custom game), 원본 시작 HQ+worker
  2기(used=20)에서 fixture로 156기까지 증가. fixture: 최종 성공 실행에서 type103(cost65)
  153기 + type5(cost35) 1기 = used 정확히 10000.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 patches/population/build_runtime_bridge.py
  --out-dir <tmp> --unit-pool-capacity 1200`(5회, 매번 성공 빌드). `PYTHONPATH=. .venv/bin/python
  tools/g2_supply10000_type28_seed_probe.py --runtime-root local/runtime --artifact-root <tmp>`
  5회 반복(디버그 반복, 팅기면 원인 찾아 수정). 최종 성공 실행 result.json은
  `/tmp/g2_type28_artifact5/probe-result.json`(공유 temp 경로 정책은 캡처 PNG 전용이라 이 JSON은
  텍스트 실행결과이며 재현 스크립트로 즉시 재생성 가능; 원본 정책상 문제 없음). `make check`
  1010 passed(687.69s, 로그 `logs/gates/20260926_lap692_make_check.log`), ruff/compileall/mypy/
  `CONTEXT_PASS` 전부 PASS, `checks/safety.sh check` → `SAFETY_PASS`. 타깃 `pytest
  tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py
  tests/test_g2_runtime_bridge_op8_order_engagement_contract.py
  patches/population/test_fixed_supply_10000.py` → 21 passed.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **`supply_cap_reads_10000_live: true`**(lap691이
  메인메뉴 0값만 확인했던 것을 ps3 라이브 PlayerStruct 실측으로 확정). **1차 실행(type104,
  cost40, gate-legal 확인)에서 예상 밖 실측**: 원본 Gate(`0x43eda0`)가 owner당 실제 살아있는
  개체수 약 **242**(200+40 성공 후 41번째에서 `fixture_original_gate_rejected`)에서 거부한다 —
  `+0x2010`에 저장된 "250"은 실제 enforcement 값이 아니다(원인은 이 lap 범위 밖, 다음 조사
  대상). cost40 단독으로는 242*40=9680<10000이라 부족함을 실측으로 확정(가설 반증 1회).
  **최종 실행(type103 cost65 153기 + type5 cost35 1기)**: `used=10000`, `supply_cap=10000`,
  `count=156`(실측 ~242 한계에 충분한 여유), `count_cap=250`(무변경), `status=
  PASS_SUPPLY10000_SINGLE_OWNER`. type28/29/108은 flags 게이트(&14)로 거부됨을 실측 확인(28:
  flags=4, 29: flags=2, 108: flags=4) — 안전 가드는 relax하지 않았다(N88 위반 없음). 8인 동시
  fixture·전역 풀(1200) 충돌·저장/로드는 **미실측**(이 lap 범위 밖).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 원본/후보 EXE는 격리 사본에서만
  존재하고 5회 모두 정리됨(cleanup ok, prefix 잔여 프로세스 0). `runtime_bridge.c` allow-list
  확장은 private 진단 도구이며 원본 게임 파일이 아니다. 남은 위험: (1) 실측된 ~242 real gate
  ceiling의 원인 미상(요청 필드 검증 필요, DESIGN의 "1200" 문구와의 관계 미확정), (2) 8인
  동시 실행 시 전역 1200-슬롯 공유 풀 충돌 미검증(8*156=1248>1200 이미 초과 우려, 8인 각자
  10000을 동시에 채우려면 156*8=1248이 전역 풀 1200을 넘을 수 있음 — 다음 회차 최우선 측정
  대상), (3) 저장/로드·전투/생산 정상 경제 경로 미검증(이번은 op=5 엔진시딩 fixture). 독립
  검수(middle) 및 사용자 마일스톤 승인 미실시 — work 1단 산출물이다.
- 다음 한 가지: 8인 동시 fixture(owners 0..7 각각 type103 153+type5 1)를 순차 발행해 전역
  1200-슬롯 풀이 8*156=1248로 초과되는지 실측하고(예상 실패), 초과 시 (a) 전역 풀 자체를
  키우는 안(이미 `build_runtime_bridge.py --unit-pool-capacity`가 1200~5000 지원, 하지만 이는
  풀 base 재배치라 전체 unit 테이블 재배치 리스크) vs (b) owner당 목표 유닛 수를 더 줄이는
  고비용 타입 조합(예: cost103 미탐색 고비용 타입 추가 탐색)을 "묻지 말고 결정"으로 비교한다.
  `g2_eight_owner_fixture_recipe.md`의 순차 op4→op5→op1 절차를 8인으로 확장해 실행한다.
