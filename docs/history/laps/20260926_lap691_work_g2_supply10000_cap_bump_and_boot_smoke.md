# 2026-09-26 | lap 691 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5, high, work(실무).
- 가설 / 사용자 관찰: 2026-09-26 21:54 사용자 판단(G5 승인, 다음 우선순위 G2 전비10000)의
  첫 구현 단계로, `fixed_supply_5000.py`의 두 immediate-패치 사이트를 5000→10000으로
  일반화해도 (a) 정적으로 안전(16-bit 필드, 65535 이내)하고 (b) 실제 격리 부팅에서
  크래시 없이 뜨는지, 그리고 (c) 개인 개체 상한1200·전역 풀10,000이 전비10000에서
  병목이 되는지(DESIGN.md G2)를 산술로 먼저 좁힐 수 있는지를 확인한다.
- 예상 PASS / FAIL 조건: 패치 preimage/postimage 바이트 정확 일치 + 원본 SHA 불변이면 정적
  PASS. 격리 사본 부팅이 크래시 없이 뜨고 요청한 exe SHA와 실행 중 세션의 exe SHA가
  일치하면 부팅 스모크 PASS. 병목은 실행 없이 기존 확정 상수(원본 개인상한250, 전역
  풀1200, 브리지 type5/cost35 전용)로 계산해 후속 실측이 필요한 지점만 특정한다(제품
  전투/저장 fixture는 이번 lap 범위 밖, PASS/FAIL 주장 없음).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `patches/population/fixed_supply_10000.py`,
  `patches/population/test_fixed_supply_10000.py`,
  `tools/g2_supply10000_cap_smoke_probe.py`,
  `analysis/memory_maps/g2_supply10000_cap_bump_20260926.md`; 수정
  `patches/population/runtime_driver.py`(SUPPORTED_EXECUTABLES 2건 + SYW2_SUPPLY_PROBE
  프로필 목록 1건 추가). 원본/참고 저장소 무변경. uncommitted(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(불변, 부팅 스모크
  전후 재해시). 후보 SHA
  `039a358ca3e8031ce316bd57e8a66df0358babeba3a544d3e850f740cebc6a1d`. 환경:
  `tools/runtime_env.py prepare()`가 만든 격리 사본(`Syw2plus_re/Syw2plus` 참고 원본에서
  copytree)+전용 32-bit Wine prefix+전용 Xvfb(`:150`, 기존 세션과 무관). 활성 플레이어:
  전투 미시작(메인 메뉴), fixture 없음(이번 lap은 전투/자원 fixture를 만들지 않았다).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 -m pytest patches/population/
  test_fixed_supply_10000.py patches/population/test_fixed_supply_5000.py -q`(17 passed).
  `.venv/bin/python -m ruff check ...`(All checks passed), `mypy runtime_driver.py
  --follow-imports=skip`(Success). `.venv/bin/python tools/g2_supply10000_cap_smoke_probe.py
  --timeout 90` → run_dir `local/runtime/20260926_220548_3407064_0`(부팅 후 `game/` 사본
  즉시 삭제, `output/manifest.json/prefix/로그` 보존). `make check` 로그
  `logs/gates/20260926_lap691_make_check.log`(결과는 아래 참조).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 정적 바이트 패치 **PASS**(17/17 테스트,
  원본 SHA 불변, 후보 SHA 재현). 부팅 스모크 **PASS**(driver clean exit 0, 실행 중 세션
  exe_sha256이 방금 빌드한 후보 SHA와 일치, 좀비/wine 프로세스 없음; 메인메뉴 스냅샷은
  8명 PlayerStruct 전부 0으로 기대대로임 — 전투 미시작 상태의 정상값이지 결함이 아니다).
  병목 산술 **UNKNOWN(실측 필요, 분석만 완료)**: cost35 전용 기존 브리지+개인상한250 조합은
  최대 전비8750으로 10000 미도달(브리지 확장 또는 상한 조정 필요), 전역풀1200은 8인×250
  동시 점유(2000)에도 못 미쳐 개인상한보다 먼저 막힌다. DESIGN.md의 "개인 개체 상한1200"
  문구는 원본 실측값(250)과 다르며 미착륙 실험(owner_count_1200)을 가리키는 것으로
  보인다 — 이 lap에서 임의로 해석을 확정하지 않고 기록만 남겼다. G2 제품 PASS·마일스톤
  주장 없음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 원본 EXE 무변경(0바이트), 새
  후보는 실제 게임 파일이 아닌 격리 사본 안에만 존재하고 이번 회차 종료 시 삭제됨.
  `make check`(전체 스위트, 아래 결과)로 회귀 확인. 독립 검수(middle) 및 사용자 마일스톤
  승인 모두 미실시 — 이번 lap은 work 1단 산출물이다.
- 다음 한 가지: `g2_eight_owner_fixture_recipe.md`의 단일/8인 fixture 절차로 실제 전투를
  시작해 `+0x2012`가 살아있는 프로세스에서 10000으로 읽히는지 확인하고, 브리지(`runtime_
  bridge.c`)를 cost40 계열 type(28/29/104/108) 허용으로 확장하거나 개인 상한(250)을
  조정하는 것 중 하나를 선택해 실제 개체수/전비 상한 충돌을 관측한다(구현 우선, 1가설).
