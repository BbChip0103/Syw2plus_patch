# 2026-09-27 | lap 713 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / work tier(실무).
- 가설 / 사용자 관찰: 2026-09-27 13:05 운영자 판정(lap712 v1 목표 조정) 수행 — owner1(nation2)이
  280초 동안 자원 23,068을 쌓으며(+1,734/분) 생산 12·군대 10으로 owner0(생산 21·군대 16)보다
  약한 lap712 baseline에 대해, **AI 자원 소비(생산 결정) 개선** v1을 정적으로 찾은 상수 1개로
  구현·측정한다. `analysis/memory_maps/ai_production_decision_path_00406770_20260923.md`(lap501
  middle)가 이미 AI 생산 결정 경로(`FUN_00406770`→`FUN_00406B00`→`FUN_0043E7F0`)의 8개 게이트를
  원본 바이트로 확정해 두었다 — 그 중 자원 임계값 게이트는 **0건**(§1 결론), H-TYPEMAX/H-RATIO는
  런타임/Data 파일에서만 채워지는 표를 읽어 EXE에 정적 값이 없다(§5), **H-CROWD만 EXE 코드에
  즉치값으로 박혀 있다**(`FUN_00406B00` @ `0x406c44`: 생산 건물 중심 11×11=121칸 안 동종·동소유
  유닛 ≥7이면 그 kind 발주 안 함). v1 가설: 이 밀집 상한을 7→14로 올리면 밀집 게이트에 걸려
  일찍 멈추는 owner(가설: owner1류)가 더 오래/많이 생산한다.
- 예상 PASS / FAIL 조건: 후보 N=3가 원본 N=3(=lap712 baseline, 재사용) 대비 owner1
  `resource_stock_last`↓·`production_count_proxy`↑·`army_unit_count_last`↑, crash 0이면 진전.
  세 지표가 lap712 baseline과 (오차 범위 내) 동일하면 **FALSIFIED**(이 게이트가 이 fixture에서
  안 걸렸거나 걸려도 두 owner 모두에 무해).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `patches/ai/g4_production_crowd_cap_v1.py`(+`test_g4_production_crowd_cap_v1.py`, 7 tests) —
  `create_copy`/`restore`/`patched_bytes`, 원본 SHA 가드, 단일 EDIT
  (`0x6C44`: `66837c241007`→`66837c24100e`, `cmp word ptr [esp+0x10],7`→`,14`).
  `tools/runtime_env.py`: `G4_CANDIDATE_EXES`에 `"g4_production_crowd_cap_14.exe"` 추가,
  `g1_baseline()`의 candidate-exe import 분기에 elif 1개 추가(기존 controller_cadence_probe/
  gather_cooldown_probe와 같은 승인된 named-candidate-exe 메커니즘 재사용, private
  `ORIGINAL_EXE`는 건드리지 않음). `tools/g4_ai_behavior_probe.py`: `run_one`/`main`에
  `--variant {original,candidate}` 추가 — candidate 경로는 `create_copy`로 이름 붙은 후보 exe를
  private game 디렉터리에 **추가**하고 `g1-baseline --g4-candidate-exe`로 그 파일을 실행한다
  (private `ORIGINAL_EXE`는 SHA 그대로, `check_runtime`의 원본 검증을 우회하지 않음). 첫 시도는
  `private_exe.write_bytes()`로 private 원본 사본을 직접 덮어썼다가 `g1-baseline` 자체의
  `check_runtime`(원본 SHA 강제)이 거부해 실패했고, 위 named-candidate-exe 방식으로 수정했다.
  게임 EXE/DLL/원본/참고 저장소 미변경. uncommitted(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(3회 실행 전후 6/6 불변,
  실제 exe 재확인 완료). 후보 `g4_production_crowd_cap_14.exe` SHA
  `11589f9e6c1deb29132291050b5fb703f5d525ebd8a0d79dd3da29f964ebce96`(3회 동일). 소스 루트
  `/home/dev_00/sharedfolder/260320_Syw2plus/[ESL]Syw2plus`. `--g4-chain-goal
  _custom_game_chain_inject_seed1`(lap712와 동일 고정시드 2인 자유대전 fixture,
  owner0=nation1/HQ49/worker7, owner1=nation2/HQ58/worker31, 시작 rice=wood=7500). N=3(후보),
  원본 N=3은 lap712 baseline 재사용(같은 fixture, 게임 로직 미변경이므로 재실행 불필요).
  `--sample-seconds 280 --sample-period 1.0`.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python tools/g4_ai_behavior_probe.py
  --chain-goal _custom_game_chain_inject_seed1 --sample-seconds 280 --sample-period 1.0
  --repeats N --variant candidate --artifact-root <temp>/g4_ai/20260927_lap713_g4_production_crowd_cap_v1
  --out .../candidate_run*.json`(1회 단독 + 2회 반복, CLI 종료코드 무관 — lap712와 동일한
  post-sampling tail 코드 경로, `g1_baseline_cli_exit=2`/`FAIL_NO_EFFECT: fixed minimap click`은
  샘플링 이후 무관한 미니맵 클릭 확인 실패로 evidence 파일은 정상 기록됨, lap712와 동일 패턴).
  산출물
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g4_ai/20260927_lap713_g4_production_crowd_cap_v1/`
  아래 `candidate_run0.json`(단독 1회), `candidate_run12.json`(반복 2회, index0/1). 각 run의
  `output`/`prefix` 보존, `game` 사본은 코드 내장 `shutil.rmtree`로 회차 종료 직후 자동 삭제(3/3
  `cleanup_ok=true` 확인, `local/runtime/g4-ai-behavior-baseline/` 아래 `game` 잔존 0건, 디스크
  여유 42GB).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **`FALSIFIED`.** 후보 N=3 전부(run0, run12 index0,
  index1) owner별 종점 지표가 lap712 원본 N=3 baseline과 **완전히 동일**했다:
  owner0 `production_count_proxy`=21·`army_unit_count_last`=16·`resource_stock_last`=9792,
  owner1 `production_count_proxy`=12·`army_unit_count_last`=10·`resource_stock_last`=23068
  (3/3 후보 = lap712 3/3 원본, 소수점 자리의 `idle_worker_count_mean`/`income_per_min`만 tick
  샘플링 위상 차이로 lap712 내부 run-to-run 변동폭과 같은 크기로 흔들림 — lap712도 3/3
  "완전 재현"이라 함은 이 정도 위상 잡음까지 완전 고정은 아니었을 수 있어 표현을 "종점 정수
  지표 3/3 동일"로 좁혀 기록한다). **밀집 상한 7→14는 이 fixture에서 owner0·owner1 모두에
  측정 가능한 효과가 0이다** — H-CROWD 게이트가 이 두 owner의 생산 경로에서 실제로 걸리지
  않았거나(더 유력, §1 문서가 예측한 대로 H-TYPEMAX/H-RATIO 쪽이 먼저 막을 수 있음), 걸렸어도
  7~14 구간에서는 무관한 kind였다는 뜻이다. crash 0, `source_unchanged` 3/3 true, `cleanup_ok`
  3/3 true.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 신규 patch 회귀 테스트 7개(원본 바이트
  일치·단일 명령어만 변경·SHA 가드·copy/restore round-trip) 전부 PASS. `make check`
  **1061 passed(868.47s)**, ruff/compileall/mypy/`CONTEXT_PASS`/`checks/safety.sh check`
  (`SAFETY_PASS`) 전부 PASS. work tier 판단으로 다음 middle 검수를 요청한다(신규
  `tools/runtime_env.py` candidate-exe 분기가 기존 두 candidate와 같은 안전 경계를 지키는지,
  `patches/ai/g4_production_crowd_cap_v1.py` 단일 EDIT의 바이트 근거 재확인). 남은 위험:
  (1) H-CROWD가 실제로 이 fixture에서 발동했는지 자체를 §1 문서 §7이 제안한 읽기 전용 런타임
  probe(`0x00956772`/`0x0089A388`/`0x009B5228` 등 직접 읽기)로 아직 확인하지 않았다 — 이번 lap은
  종점 상태 비교만 했다. (2) 이 fixture 1개(owner0=nation1/owner1=nation2)만 측정했으므로 다른
  matchup에서 H-CROWD가 걸릴 가능성은 배제하지 않는다. (3) H-TYPEMAX/H-RATIO는 런타임 표라
  이 lap의 정적 접근으로는 애초에 상수를 못 바꾼다 — 다음 후보가 필요하면 그 표를 읽는 §7 probe
  선행이 더 저렴하다.
- 다음 한 가지: **v1(H-CROWD 7→14) FALSIFIED로 종결.** 같은 추측을 반복하지 않는다(가설 2회
  소진 규칙 — 이번이 1회, 재시도보다 진단 우선). 다음 work는 §1 문서 §7의 읽기 전용 런타임
  probe(정적 확인 아님, 실제 실행 중 메모리 읽기)를 이 owner1/owner0 조합에서 1회 실행해
  **어느 게이트가 owner1의 생산을 12에서 멈췄는지**(H-TYPEMAX/H-RATIO/H-AVAIL/H-STATE 중)를
  raw로 특정한 뒤, 그 특정된 게이트에 맞는 v2 후보(런타임 표 값이면 §7이 읽은 실제 주소를
  대상으로, 아직 EXE 정적 상수가 있다면 그 상수)를 만든다. idle_worker_count는 보조 지표로
  계속 기록(이번 lap 3/3 owner0 0.678~0.680, owner1 0.129~0.132로 lap712와 정합).
