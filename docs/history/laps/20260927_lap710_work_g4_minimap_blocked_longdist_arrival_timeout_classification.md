# 2026-09-27 | lap 710 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 (claude-sonnet-5), 실무(work) 역할.
- 가설 / 사용자 관찰: 2026-09-27 10:45 운영자 판정 ①: world (93,56)에서 카메라 팬 원위치 복귀 실패
  (lap707 BLOCKED)를 **미니맵 우클릭**으로 우회해 원거리(≥20타일, 목표 33~35타일) 명령을 발행하고
  원본 N=3 baseline을 얻는다. H1: HUD 좌하단의 다이아몬드형 위젯이 미니맵이며 그 위 우클릭이
  선택 유닛에게 이동 명령(주문 좌표)을 내린다. H2: HUD의 나침반형 다이얼(이전 lap674
  `MINIMAP_CLICK=(235,555)`)이 실제 미니맵/카메라 위젯이다.
- 예상 PASS / FAIL 조건: 후보 위젯 우클릭 직후 선택된 워커의 `pending_xy`(디코드된 world 좌표)가
  0이 아닌 클릭 대응 좌표로 바뀌면 PASS(이동 명령 발행 확인); 좌클릭 시 메인 뷰포트 9점 캘리브레이션의
  `center_world`가 이동하면 카메라 점프로 PASS. 둘 다 불변이면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `docs/history/laps/probes/20260927_lap710_minimap_locate_probe.py`(1회성 진단 스크립트, `tools/`나
  `patches/`가 아니므로 `make check`의 lint/typecheck/pytest 대상 밖 — `pyproject.toml`
  `testpaths=["patches","tests"]`, `Makefile` ruff 대상은 `patches tools tests checks`만).
  게임 EXE/DLL/제품 코드 미변경. STATUS/APPROVALS만 갱신. uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(이 lap 신규 실행 3회 전부
  사전 확인, 실행 후 미확인 — 진단 스크립트가 `source_after` 비교를 생략함; **비차단 갭으로 기록**,
  다음 실행부터는 `sha256(source_exe)` 사후 재확인을 넣는다). 후보 없음(원본만). 환경 `[ESL]Syw2plus/`
  소스, 1600x1200x24 Xvfb, `SYW2_SUPPLY_PROBE=1`. 활성: 솔로(비고정 시드) 1인 × 3회(이 lap) — spawn
  world는 (93,56)×2, (10,49)×1(모두 lap706/707이 이미 확인한 두 world 중 하나, 회귀). fixture: 기존
  워커(슬롯1198)만, 다이아몬드/다이얼 우클릭 테스트에는 dense fixture 불필요.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. python3
  docs/history/laps/probes/20260927_lap710_minimap_locate_probe.py`(고정 인자 없음, 3회 반복 실행).
  캡처/결과 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260927_lap710_minimap_locate/`
  (1차, `full-window.png` sha256 `5938d689…9a675b`) 및
  `20260927_lap710_minimap_calibration/`(2·3차 반복 실행, 매번 덮어씀 — **비차단 갭: 3회 결과를 구분
  보존하지 않음**, 마지막 실행 결과만 남음). 시각 확인 크롭
  `hud-zoom.png`/`diamond-zoom.png`/`dial-zoom.png`(같은 디렉터리).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **H1 FALSIFIED.** 다이아몬드 위젯(화면 대략 x∈[0,176], y∈[511,598], 꼭짓점 top(88,511)
  right(176,550) bottom(88,598) left(0,550)) 9개 지점 우클릭(button=3) 전부 워커 `pending_xy`가
  클릭 전과 동일한 `(0,0)`으로 유지(2개 world, 총 18회 우클릭 — world(93,56) 9회 + world(10,49) 9회,
  실제로는 마지막 실행만 로그에 남았으나 본문에 인용된 수치는 그 실행의 것). 같은 지점 좌클릭
  (button=1) 후 메인 뷰포트 9점 재캘리브레이션의 `center_world`도 클릭 전후 **완전 동일**(`93.444,
  54.556` → `93.444, 54.556`, shift=0.0타일) — 카메라 점프도 없음.
  **H2 FALSIFIED.** 나침반형 다이얼(중심 약 (235,555), 화살표 바늘 + 8방위 점 + 상단 붉은 구체 —
  시각적으로 시간/방향 표시용 회전 다이얼로 확인, 미니맵 아님) 7개 지점 우클릭 전부 동일하게
  `pending_xy=(0,0)` 불변. 좌클릭도 뷰포트 `center_world` 불변(shift=0.0타일).
  **추가 확인(진짜 미니맵이 별도 토글로 존재하는지):** `Tab`/`m`/`M` 키 입력 후 캡처 diff는
  非zero(HUD 애니메이션·유닛 idle 이동 때문, 나침반 바늘 방향도 자체 회전) 이나 시각적으로 새 오버레이나
  위젯 등장 없음(다이아몬드 계속 완전 검정, 나침반 계속 같은 자리) — **키 토글 미니맵도 관측되지 않음**.
  **결론: 이 빌드/이 UI 배치에서 "미니맵 우클릭으로 원거리 이동 명령 발행"은 지금까지 시도한
  경로(다이아몬드 우클릭/좌클릭, 나침반 우클릭/좌클릭, Tab/m/M 토글) 전부에서 재현되지 않는다 —
  `BLOCKED`(실패 가설 2/2 + 추가 토글 확인 1회, 총 3가지 경로 소진).**
  **① 대안 채택(같은 lap, 재실행 없이 기존 raw 재사용):** lap707이 이미 world **(10,49)**에서
  같은 `--scenario long_distance_pan` 메커니즘(카메라 팬→9점 캘리브레이션→선택→재팬→클릭, 미니맵
  불필요)으로 **N=5**(run1/3/4/8/9) `ever_move_command_count=20/20`(전부 명령 도달 확인) raw를 이미
  gener했다 — `world (10,49)`가 "대표 baseline scene에서 제외"된 것은 **다른 probe**
  (`g5_worker_relative_move_attack_probe`의 짧은 상대offset 클릭 방식, lap706)에서 명령 도달 자체가
  0이었기 때문이지, `long_distance_pan` 자체의 결함이 아니다 — 이번 lap이 그 구분을 원본 raw로
  재확인했다(아래). N=3 요구를 이미 초과 충족(N=5).
  **② 미도착 유닛 원인 분류(raw 재분석, 원본 결과 JSON
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260927_lap707_g4_path_baseline_scenarios/longdist-run{1,3,4,8,9}/probe-result.json`
  직접 파싱, 게임 재실행 없음):** 5회 합산 `expected=100`, `arrived=49`, 미도착 `51`. **51/51(100%)이
  `stagnation_runs=[]`(정체 없음) + `path_ratio` 1.0~1.9(도착한 유닛과 동일 대역, 폭주 없음) +
  최종 위치가 목적지에서 **3.16~5.4타일**(트레이스 종료 시점, `ARRIVAL_RADIUS_TILES=3.0`을 아주 살짝
  넘음) — **정체/충돌/경로실패 사례 0건**. 즉 미도착의 지배 원인은 "여전히 정상 경로로 접근 중이었으나
  `TRACE_TIMEOUT_S=90.0`초 안에 3타일 반경에 못 들어간 것"(측정 타임아웃)이다, AI/경로탐색 결함이
  아니다.
  **③ v3 가설(구현은 다음 lap):** 위 100% 시간초과 소견이 맞다면 `TRACE_TIMEOUT_S`를 (예:
  150~180s로) 늘리기만 해도 도착률이 90%+ 수준으로 오를 것이다 — 코드/AI 변경 없이 측정 파라미터만
  조정하는 **반증 가능한 예측**. 다음 work: world (10,49) 또는 카메라 팬 복귀가 해결된 (93,56)에서
  동일 `long_distance_pan` 시나리오를 `TRACE_TIMEOUT_S` 확장판으로 N=3 재실행 → 미도착 유닛의 최종
  거리·정체 여부 재확인. 예상대로면 "G4 원거리 도착률 개선"은 게임 로직이 아니라 **probe 타임아웃
  파라미터 문제였다**로 판정하고 G4 다음 우선순위(예: obstacle_row 저도착 케이스 또는 candidate AI
  정책 자체의 부재)로 넘어간다; 예상과 다르면(시간 늘려도 도착 안 함) 그 잔여 미도착 사례만 정체/충돌로
  재분류한다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(제품 코드 미변경). 남은 위험: (1) 진단
  스크립트가 원본 SHA 사후 재확인·개별 실행 결과 보존을 생략함(위 명시, 다음 사용 시 수정). (2) 미니맵
  BLOCKED가 "이 3가지 위젯/입력 조합에서 관측 안 됨"이라는 negative 증거이며, UI 레이아웃이 해상도별로
  다를 가능성(이 probe는 1600x1200 데스크톱의 800x600 게임 콘텐츠 창만 사용, G1 1600x1200 프레젠테이션
  패치 미적용 상태)은 배제하지 못했다. (3) v3 가설(타임아웃 확장)은 아직 미검증(구현/실행 없음). middle
  독립 검수 요청 없음(정보 제공용 — 발견·재분류·차기 가설).
- 다음 한 가지: `③`에 적은 `TRACE_TIMEOUT_S` 확장 가설 검증(다음 work, 구현 우선). 미니맵 우클릭
  경로는 이 lap의 근거로 **중단**한다(같은 추측 반복 금지).
