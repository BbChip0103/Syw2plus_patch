# 2026-09-26 | lap 694 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5(claude-sonnet-5), 실무(work) 역할.
- 가설 / 사용자 관찰: STATUS lap693 "다음 한 가지" — lap692에서 owner1인 실측한 type103(cost65)x153+
  type5(cost35)x1 조합(개인 156기, used=10000)을 8인 전원에게 순서대로 적용했을 때, 전역 1200슬롯
  유닛 테이블이 8*156=1248을 감당하지 못해 병목이 되는지를 raw로 측정한다.
- 예상 PASS / FAIL 조건: 8인 전원이 used>=10000에 도달하면 병목 없음(PASS_ALL_EIGHT_SUPPLY10000).
  일부만 도달하고 나머지가 전역 풀 소진으로 거부되면 병목 확인(MEASURED_GLOBAL_POOL_BOTTLENECK,
  실패가 아니라 측정 결과). 크래시/계정 불일치(lock)가 나면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `tools/g2_supply10000_eight_owner_probe.py` 1개 추가(uncommitted, LOOP_ALLOW_COMMITS=0).
  기존 `patches/population/runtime_bridge.c`(lap692 allow-list 확장), `fixed_supply_10000.py`,
  `runtime_env.py`(lap693 경로 전환)는 무변경(이미 working tree에 uncommitted로 존재, 이번 lap은
  그 위에서 읽기만 함). 원본/참고 저장소 무변경.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 SHA `b56986e0…c9c08a8ac`(새 경로 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`, 5회 확인 전부 불변).
  후보 SHA `039a358c…cebc6a1d`(fixed_supply_10000, lap691/692와 동일). 브리지 SHA
  `a1a08626…08bc2d0`(op5/6 allow-list에 type103/104/108/28/29/2/46 포함, --unit-pool-capacity 1200
  기본값 무변경). 활성 8인(owner0=human 역할 슬롯이지만 이 probe는 UI 미조작, ai 필드만 확인),
  `_custom_game_chain_inject_g2_eight_seed42` 컨트롤 목표로 생성. 지도 100x100(런타임 실측).
  owner별 fixture: type103 x153 + type5 x1(목표 154기, 기존 HQ49+worker7 포함 총 156기/owner).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `PYTHONPATH=. .venv/bin/python tools/g2_supply10000_eight_owner_probe.py --runtime-root
  local/runtime --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/
  g2_capacity/20260926_lap694_eight_owner_supply10000`.
  결과 JSON: `<artifact-root>/probe-result.json`(schema
  `syw2plus.g2-supply10000-eight-owner-probe.v1`). 원본 wine/xvfb 로그 `<artifact-root>/probe.log`.
  make check 로그 `logs/gates/20260926_lap694_make_check.log`. safety 로그는 stdout(SAFETY_PASS)만.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **MEASURED_GLOBAL_POOL_BOTTLENECK.** 8인 전원 chain-inject 생성 성공(`chain_inject.ok=true`,
  `reason=chain_reached_ingame`, PS7->PS3, 8인 모두 nonzero nation/ai role 확인, pre-fixture 전역
  live=16(HQ+worker x8)). owner0~6(7인) 전원 **used=10000, count=156, cap=10000 도달**(순서대로
  global_live 158→298→...→1094까지 누적). owner7은 type103 153기 요청 중 105기만 배치되고
  106번째부터 `fixture_original_gate_rejected`로 **거부**(전역 live가 1199에 도달해 더 이상 빈
  슬롯 없음, 1200-슬롯 테이블의 슬롯0은 미사용이라 실사용 상한은 1199) — owner7 최종
  `used=6845, count=107`(목표 10000 미도달). `fixture_failed` 잠금(lock)은 트리거되지 않음(gate
  거부는 정상적인 "빈 슬롯 없음" 종료이지 accounting mismatch가 아님). 크래시 0, cleanup ok(prefix
  잔여 프로세스 0), 원본 SHA 실행 전후 불변. `make check` **1010 passed(766.52s)**,
  ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS, `checks/safety.sh check` **SAFETY_PASS**.
  이 결과는 STATUS lap693이 예측한 산술(8*156=1248>1200)을 **실측으로 확인**한다: 병목은 개인
  전비 장부(전원 gate-legal 250 이내 실측 156기로 10000 도달)가 아니라 **전역 1200-슬롯 유닛
  테이블**이다. DESIGN G2의 문자 그대로 "8인 각각 10000" 요구는 이 구성(1200-슬롯 풀, type103+type5
  156기/owner)으로는 **미충족**(7/8만 도달) — 제품 G2 PASS 아님, 이번 lap도 PASS를 주장하지 않는다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 신규 도구 1개만 추가, 기존 코드/패치 무변경이라
  회귀 위험 낮음(make check 카운트 lap693과 동일 1010). 이 결과는 아직 middle 독립 검수 전이다.
  멀티 동기화/저장·로드/24k·144k는 이번 lap 범위 밖(미실측). 8인 모두 human 활성 플레이 여부(owner0
  ai=0만 확인, 실제 human 세션 UI 조작은 안 함)는 별도 확인 필요.
- 다음 한 가지: 이 병목이 확정 사실이므로, 다음 work는 middle/strategy 판정으로 다음 중 하나를 좁힌다
  — (a) 실측 per-owner 개체 상한(~242, lap692) 이내에서 cost>65인 gate-legal 타입을 넓은 범위(0..200
  전수)로 재탐색해 owner당 150기 이하로 10000에 도달하는 조합을 찾는다(전역 풀 무변경으로 8*150=1200
  이내 시도), 또는 (b) 전역 1200-슬롯 풀 확장(`build_runtime_bridge.py --unit-pool-capacity`는 이미
  1200~5000 지원하나 구조체 relocation 별도 위험, lap678 G5 조사에서 유사 크기변경 크래시 이력 다수
  경고됨)의 타당성/승인 여부를 strategy에 회부한다. 둘 다 하지 않고 "달성"으로 기록하지 않는다.
