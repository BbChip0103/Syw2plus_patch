# 2026-09-20 | lap 409 | 목표 G2 (P1)

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5 / high / work(실무). loop/PROMPT.md ①~⑥, ESCALATE_SOL §13 조건(다음 회차는 반드시 work tier이고 P1 실제 실행 착수)에 따라 진행.
- 가설 / 사용자 관찰: `docs/work/active/G2_RSRC_WRAPPER_CONTAINMENT_GATE_LAP408.md`(W7)를 닫은 뒤 `G2_STRATEGY_DIRECTION_LAP404.md` §D P1 — marked compat(`4331d9cd…`) 경로를 near-4000 live 규모에서 실제 게임 실행으로 반복(기존 382-unit만 통과). 이번 세션 이전에는 이 조합(마킹된 compat 헤더 + near-4000 스케일)의 실제 실행 증거가 전혀 없었다(자칭 lap410/412는 non-compat N=4001 후보만 near-4000 스케일로 실행했고, compat 후보는 382유닛 legacy-load 스모크만 실행).

## W7 (선행, 완료)

- 변경 파일: `patches/population/test_g2_full_capacity_persistence_compat_v1.py` (신규 테스트 1건 추가, 다른 파일 무변경).
- 신규 `test_compat_wrappers_are_contained_in_rsrc_cave_without_overlap`: N=4001 기준 4개 wrapper(LOAD_WRAPPER/SAVE_HEADER/LOAD_HEADER/LEGACY_COPY)의 실제 emit 함수 산출물 길이로 (1) cave 내 컨테인먼트, (2) 상호 비중첩, (3) 시작/끝 VA가 후보 자신의 `.rsrc [VA,VA+VirtualSize)` 안, (4) 실행 속성 플래그를 pytest로 강제.
- 역주입 확인(카드 §3.1, `/tmp`에서만 in-memory로 수행·보존 안 함): `RSRC_COMPAT_END_OFFSET`를 1바이트 축소한 한계값으로 같은 검사 로직을 재실행 → `LEGACY_COPY overflows: end=0x26cf limit=0x26ce`로 정확히 FAIL 확인. 새 단언이 실제로 회귀를 잡는다.
- `make check` rc0 **784 passed** (lap408 CLOSED 시점 783 + 신규 1건, 510.63s), Ruff/compileall/mypy10 Success, `CONTEXT_PASS`. 별도 `checks/safety.sh check` → `SAFETY_PASS`(W7 직후 1회, P1 실행 완료 후 1회 재확인). 원본 2경로 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 재해시 불변.
- 카드 §4 범위 밖 항목(wrapper 배치/오프셋/`RSRC_COMPAT_END_OFFSET`/후보 SHA 변경, persistence 비compat 앵커 중복) 없음. 후보 SHA 4건 pin 무갱신.

## P1 — 실제 게임 실행 (신규, 이번 lap의 핵심)

- 변경 파일: 없음(게임 코드/패치 모듈 무변경). 격리된 실행 환경과 진단 브리지만 새로 빌드.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (재해시 확인, 두 참고 경로 동일).
- 후보 SHA: `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`
  (`patches.population.g2_full_capacity_persistence_compat_v1.build_candidate(original, 4001)`로 재생성,
  `runtime_driver.py`의 `SUPPORTED_EXECUTABLES["syw2plus_original.exe"]` 핀과 정확히 일치 확인).
- 격리 환경: `tools.runtime_env.prepare()`로 신규 전용 복사본+Wine prefix 생성
  (`run_id=20260920_215245_1236080_0`, source `Syw2plus_re/Syw2plus`, 원본 사본 해시 사후 검증 PASS).
  진단 DLL은 처음에 기존 재사용 `_inmm.dll`(SHA `f13d50fb…`)을 넣었으나, 이것이 **STOCK(1200칸) 주소로
  빌드된 브리지**임을 발견(바이트 검색: 재배치 주소 0건, stock existence 주소 12회, 리터럴1200 9회) —
  N=4001 재배치 후보와 섞어 쓰면 ledger `live`가 0으로 읽히고(주소 불일치) op=6 seeding이
  `fixture_original_gate_rejected`로 전멸(엔진의 새 allocator가 slot≥1200을 정상 반환하는데 브리지가
  `allocated>=1200`을 오류로 오판). **수리:** `python3 -m patches.population.build_runtime_bridge
  --out-dir /tmp/p1_bridge4001 --unit-pool-capacity 4001`로 재배치 주소 정확히 일치하는 브리지 재빌드
  (`unit_pool_base=0x0108C000`, `unit_existence_base=0x017B8658` — `tail_relocation_storage_layout_v1`과
  `full_tail_relocation_storage_layout_v1`이 N=4001에서 앞 3영역 베이스가 동일함을 먼저 확인), 게임 프로세스를
  안전 종료(`op:"stop"`, wineserver/xvfb 정리 확인, display 회수 확인) 후 올바른 브리지로 재기동.
  두 시도 모두 원본 파일 무변경, 잔류 프로세스 0(`ps aux`/디스플레이 lock 확인).
- 실행 명령: `python3 patches/population/runtime_driver.py --game-root <run>/game --prefix <run>/prefix
  --out <out> --display :300 --exe syw2plus_original.exe --screen 1024x768` (SYW2_SUPPLY_PROBE=1 자동 설정).
- 부트스트랩: title 클릭 `(184,560)` → PS9→PS7(확인), `goal="_custom_game_chain_inject_g2_eight_seed42"` →
  `chain_reached_ingame`, PS9→(7,140,150,2,3) 경로로 PS3, 8 owner 전원 `cap=5000` 확인(엔진 자체 supply cap
  패치가 실제 실행에서 유효함을 재확인).
- 시딩: 진단 브리지 op=6("bounded engine-seeded roster" — 실제 엔진 `Place 0x42ecb0`/`Gate 0x43eda0`/
  `Spawn 0x443190`를 호출하는 gate-legal 경로, 메모리 직접 조작 아님) 24회(owner당 195+200+100),
  owner0는 cap 도달로 마지막 호출이 `fixture_exceeds_unreserved_supply`(예상된 정지, ok=false는 정상).
  결과: 8 owner 합계 **3,991 live 유닛**(owner별 500/498/497/498/499/499/497/500,
  `used`=cap 근접 4,970~5,000). `runtime_driver.py` 자체의 독립 `snapshot`(process_vm_readv, 브리지와
  무관한 경로)이 동일 총합 3,991과 유닛별 slot 목록을 확인 — 두 독립 판독 경로 일치.
- 저장: op=2(slot 90) → `game/save/save090.dat` 생성(9,272,322 B, SHA
  `814e7f05aa8a9ba5d59801448739ed197c2d5c4c3bbdb9efdfb92dab86a88460`). **마커 `S2P1N4K1`이 파일 오프셋
  `0x38`에서 정확히 발견됨** — compat의 SAVE_HEADER wrapper가 실제로 새 포맷 헤더를 썼음을 파일 바이트로
  확인(legacy fallback이 아님).
- 재적재: op=3(slot 90) → `ok:true`, 즉시 ledger(owner0) `used=5000,count=500,live=500`로 저장 시점과
  일치. 이어서 `runtime_driver.py` 독립 snapshot으로 8 owner 전체 재확인: 합계 3,996(저장 후 로드 사이
  320 tick 동안 생산이 계속되어 5기 증가 — 정상 게임플레이, 손실 아님). slot 단위 대조:
  **저장 시점 3,991 슬롯 중 소실 0, 같은 슬롯의 internal_id 불일치 0**, 신규 생산 슬롯 5건만 추가.
  ⇒ **near-4000 규모에서 marked compat save/load 왕복이 무손실임을 실제 실행으로 확인.**
- 정리: `op:"stop"` → wine/wineserver/xvfb 잔류 프로세스 0, display `:300` 회수 확인. 원본 2경로 재해시
  불변(`b56986e0…08a8ac`). `checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정: **PASS** — compat(marked) 경로가 near-4000 live(3,991~3,996)에서 gate-legal 생산 시딩 +
  마킹된 저장 + 마킹된 로드 전 구간에서 무손실로 실행됨을 실제 Wine 프로세스로 확인. 기존 "382-unit만
  통과" 갭이 닫혔다.
- fixture: 새로 생성한 `local/runtime/20260920_215245_1236080_0`(격리 사본+prefix, 커밋 대상 아님) 및
  임시 빌드 `/tmp/p1_compat_build/`, `/tmp/p1_bridge4001/`(진단 브리지 소스/빌드, `/tmp`뿐이라 보존 안 됨 —
  재현하려면 위 `build_runtime_bridge` 명령을 다시 실행). 증거 사본은
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260920_lap409_p1_compat_near4000/`
  (`p1_summary.json`, `seed_receipts.json`, `presave_snapshot.json`, `postload_snapshot.json`, `trace.jsonl`,
  `wine.log`, `session.json` 등).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **독립(다음 새 세션) 검수 미완료** — 이 lap은 work
  역할이므로 자기 결과의 최종 컨펌이 아니다. 남은 위험: (1) 이번 시딩은 진단 브리지의 gate-legal 경로이지
  원본 명령/실제 UI 생산 경로 전체는 아니다(P2, 기존에 알려진 갭, 새 문제 아님). (2) 24k/144k 같은 장시간
  soak은 이번에 하지 않았다 — non-compat 후보는 이미 soak PASS가 있으나(자칭 lap412, 미검수) compat
  후보 자체의 장시간 soak은 아직 없다. (3) strict over-cap/전비 랩 판정(N19/되물음)은 이 lap이 다루지
  않았다(사용자 답변 대기, P3). (4) LAN/P4 미착수. 목표 숫자·범위·승인 변경 없음. 커밋 없음
  (LOOP_ALLOW_COMMITS 기본0).
- 다음 한 가지: 다음 새 세션(middle, Opus5/high)이 이 lap의 원시 증거(`p1_summary.json`,
  `seed_receipts.json`, save090.dat 해시, presave/postload snapshot diff)를 독립 재확인한다. ACCEPT 시
  P2(진단 브리지 시딩을 원본 생산 명령 경로로 대체) 또는 compat 후보 자체의 장시간 soak 착수를 다음
  work 카드로 발행한다. strict cap(N19/되물음)은 여전히 사용자 답변 대기.
