# 2026-09-27 | lap 711 | 목표 G4 (원거리 도착률 v3 가설 검증)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 (실무), STATUS "다음 한 가지"(lap710이
  기록한 v3 가설)를 그대로 수행.
- 가설 / 사용자 관찰: lap710은 world (10,49) `long_distance_pan`의 미도착 51/51(100%)이 전부
  `stagnation_runs=[]`+정상 `path_ratio`+최종거리 3.16~5.4타일로, 정체·충돌 없이 `TRACE_TIMEOUT_S=90s`
  근처에서 멈췄다고 관측했다. v3 가설: 타임아웃만 150~180s로 늘리면 도착률이 오를 것(반증 가능),
  안 오르면 잔여 미도착을 정체/충돌 관점으로 재분류한다.
- 예상 PASS / FAIL 조건: 늘린 타임아웃(165s)에서 arrival_rate가 눈에 띄게(예: 90%+) 오르면 "측정
  타임아웃 문제"로 판정하고 G4 우선순위를 다른 항목으로 옮긴다. 안 오르면(같은 51건 상당이 여전히
  미도착) 잔여 사례를 정체/충돌로 재분류.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/g4_path_baseline_probe.py`에
  `--trace-timeout-s`(기본값 기존 `TRACE_TIMEOUT_S=90.0` 그대로, 미지정 시 동작 불변) CLI
  옵션과 `run_probe(..., trace_timeout_s=...)` 매개변수 추가, 결과 JSON에 `trace_timeout_s` 필드
  기록. `tests/test_g4_path_baseline_probe.py`에 회귀 테스트 1개 추가(기본값이 기존 상수와 동일,
  override가 `main()`에서 `run_probe`까지 전달됨을 `monkeypatch`로 확인) — 총 8→9개. 게임
  EXE/DLL 미변경(이 lap은 `variant=original`만 사용, 후보 없음). uncommitted,
  `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(3회 실행 전후 전부
  `source_unchanged=true`). 후보 없음. 환경 `[ESL]Syw2plus/` 소스, Xvfb, `SYW2_SUPPLY_PROBE=1`.
  활성 플레이어: 솔로(비고정 시드) 1인. 지도: run1은 worker world (93,56)(기존에 이미 BLOCKED로
  분류된 카메라-복귀 결함 world), run2/run3은 목표 world (10,49)(둘 다 동일 좌표로 우연 재현).
  군대/fixture: 워커 + `dense_fixture_requests` owner0 type2/type7(fixture type은 run마다 랜덤,
  이동 로직과 무관) 55기, 원본 20-cap 드래그로 20기 선택. 시나리오 `long_distance_pan`(카메라 팬
  ≥20타일, run2/3 실측 거리 37.6~37.7타일).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `PYTHONPATH=. .venv/bin/python tools/g4_path_baseline_probe.py --runtime-root
     local/runtime/g4-lap711-v3-timeout-run{1,2,3} --artifact-root
     .../temp/Syw2plus_patch/20260927_023201_lap711_g4_v3_timeout/run{1,2,3}
     --scenario long_distance_pan --trace-timeout-s 165` → run1 exit2(ProbeError, 아래),
     run2/run3 exit0.
  결과 JSON SHA256: run1 `832f46e2d9deaa0dfa2fd88a3c449bcd543cf7f4861a6017a760af601738744e`,
  run2 `f52f25b308840b347aba35363be76954b44831ee98f887f8c3bc389b7eaa5a1c`,
  run3 `798abfc0c283cda02e4eddbb764315bb5ff20ac7b1936c7d45d5fa4a07f3ba40`(각
  `<artifact-root>/probe-result.json`). `make check` 로그
  `logs/gates/20260927_lap711_g4_v3_timeout_make_check_final.log`, 개별 실행 로그
  `logs/gates/20260927_lap711_g4_v3_timeout_run{1,2,3}.stdout.log`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **run1 (world 93,56, 기존 결함 재확인, 하네스 관점 정상 동작):** 카메라 팬 37.6타일 도달은
    성공했으나 복귀 3회 보정 후에도 drift 21.2~26.8타일로 수렴 실패, 복귀된 화면이 fixture와
    무관한 지점이라 드래그 선택 0/20(`ProbeError: drag did not select the original 20-unit cap`).
    `cleanup.ok=true`, `source_unchanged=true`, 크래시 없음 — STATUS가 이미 BLOCKED로 분류한 world
    (93,56) 카메라-복귀 결함의 새 raw 재현일 뿐, 새 결함 아님.
  - **run2/run3 (world 10,49, v3 가설 실제 검증):** 둘 다 `arrival_rate=0.65`(13/20, 90s였던
    lap707 기준 ≈49%보다는 높지만 90%+에는 크게 못 미침), `stagnating_slot_count=0`,
    `path_ratio_median≈1.174`. **핵심 관측: 미도착 7슬롯의 `final_xy`가 run2/run3에서 완전히
    동일**(슬롯별 좌표 1픽셀 오차 없이 일치, 도착한 슬롯들의 `arrival_tick`만 미세하게 다름
    [예: 954 vs 948] — 결정론적 길찾기 + 타이밍 잡음). 즉 **타임아웃을 90s→165s로(+75s, +83%)
    늘려도 미도착 유닛은 단 1틱도 더 목적지에 가까워지지 않았다** — 이미 90s 이내에 정상상태에
    도달해 있었다는 뜻이다. 미도착 7슬롯의 목적지까지 거리는 3.16~4.47타일로 `ARRIVAL_RADIUS_TILES
    =3.0` 바로 밖이며, 도착한 13슬롯과 미도착 7슬롯의 최종 좌표를 함께 보면 20기 전원이 **단일
    목적지 좌표 하나**를 중심으로 반경 ~4.5타일 안에 빽빽하게 모여 있다(예: 목적지 (34,71) 주변
    (31~36, 68~75)). **v3 가설(측정 타임아웃 문제) `FALSIFIED`** — 원인은 타임아웃이 아니라
    **probe가 20기 전원을 하나의 좌표로 우클릭시키고 반경 3타일이라는 좁은 '도착' 판정 기준을
    쓰는 것** 자체다: 실제 RTS 엔진에서 여러 유닛이 한 점으로 몰리면 먼저 도착한 유닛들이 뒤쪽
    유닛을 물리적으로 막아 그 점 반경 3타일 안에 전원이 들어갈 수 없다(이번 20기 중 13기만
    가능했다) — 이것은 원본 길찾기/AI 결함이 아니라 **측정 기준(단일 목적지+좁은 반경) 자체의
    한계**로 보인다.
  - `make check` **1050 passed(851.98s)**(이전 회차 1049 + 이번 lap 신규 테스트 1개),
    ruff/compileall/mypy/`CONTEXT_PASS`/`checks/safety.sh check`(`SAFETY_PASS`) 전부 PASS. 원본
    SHA 3회 전부 `cleanup.ok=true`(run1 포함 — 실패해도 정리는 성공)·`source_unchanged=true`,
    크래시 0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 신규 회귀 테스트 1개 PASS(CLI 기본값/override
  전달), 기존 8개 불변. 남은 위험: (a) 이 lap은 probe 하드웨어/측정 코드만 바꿨고 원본 게임
  EXE는 손대지 않았다 — "원거리 도착률 개선"은 여전히 미착수. (b) world (93,56)의 카메라-복귀
  결함은 여전히 미해결(우선순위 밖 보존, 이번 lap이 다시 우연히 마주쳤을 뿐). (c) 20기가 한 점에
  몰리는 구성이 실제 플레이 패턴을 대표하는지(사람이라면 넓은 지역에 우클릭하거나 진형을 유지)는
  검증하지 않았다. 독립 검수/사용자 승인 요청 없음(work tier 자체 raw 관측 보고, STATUS의 v3
  가설 검증이라는 기존 지시를 그대로 수행한 것).
- 다음 한 가지: **가설 2회 소진 규칙에 따라 v3(타임아웃)은 `NOT_FEASIBLE`로 결론.** v4 가설(제안,
  구현은 다음 work): "단일 목적지+좁은 반경"이 측정 인공물이라면, `ARRIVAL_RADIUS_TILES`를 20기
  밀집 대형이 물리적으로 들어갈 수 있는 넓이(예: 유닛 20기 원형 대형 반경에 맞춘 6~8타일)로 넓히거나,
  목적지를 단일 좌표 대신 작은 영역(예: 3x3)으로 정의해 같은 world (10,49)/165s로 재실행 —
  arrival_rate가 90%+로 오르면 "원거리 도착률" 미충족 항목은 측정 기준 문제였다고 최종 판정하고
  G4 우선순위를 obstacle_row 저도착 케이스나 candidate AI 정책 부재 쪽으로 옮긴다. 오르지 않으면
  그때 실제 길찾기/AI 결함으로 재분류한다. world (93,56) 카메라-복귀 결함 자체를 고치는 것은 계속
  후순위.
