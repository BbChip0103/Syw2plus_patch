# 2026-09-27 | lap 704 | 목표 G4 (G4-P1 원본 길찾기 baseline)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 (실무), STATUS "다음 한 가지" 그대로 수행.
- 가설 / 사용자 관찰: STATUS 2026-09-27 lap703 handoff — 새 `tools/g4_path_baseline_probe.py`가
  `tools/g5_worker_relative_move_attack_probe.py`의 in-run 화면→월드 보정·선택+우클릭·
  `read_unit_full`/`poll_convergence` 패턴을 import 재사용(G5 파일 수정 없음)해, 보호 원본 EXE에서
  원본 20기 선택 → 워커 기준 ≥20타일 목적지 우클릭 1회 → 슬롯별 `(tick,x,y,command,hp)` raw trace를
  만들 수 있는지 확인한다.
- 예상 PASS / FAIL 조건: `FEASIBLE_PATH_BASELINE`=fresh 원본 3회 모두 선택20·명령도달20·trace
  완주·cleanup ok·원본 SHA 불변. `NOT_FEASIBLE`=명령도달<20 또는 추적불가 2회 반복. `BLOCKED`=크래시/
  cleanup/SHA 실패.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `tools/g4_path_baseline_probe.py`(uncommitted, `LOOP_ALLOW_COMMITS=0`). 게임 EXE/DLL 미변경.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 3회 모두 불변, 후보
  없음 — 원본 전용). 환경 `[ESL]Syw2plus/` 소스, 1600x1200x24 Xvfb, `SYW2_SUPPLY_PROBE=1` 진단
  브리지(`patches/population/build_runtime_bridge.py`). 활성 플레이어: 솔로(비고정 시드) 1인.
  지도: 미고정(unseeded solo 로비 — 매 실행 절대좌표/지형 상이, 스크립트 docstring에 명시).
  군대/fixture: 기존 워커(슬롯1198) + `dense_fixture_requests`로 워커 중심 7x8(-3..3,-3..4 제외 자기칸)
  격자에 owner0 type2 유닛 55기 생성, 원본 20-cap 드래그로 20기 선택(워커 포함 여부는 런마다 다름).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. run1(목적지 ≥20타일, 워커 기준 오프셋 자동탐색 (15,-15)→world(25,34)):
     `PYTHONPATH=. .venv/bin/python tools/g4_path_baseline_probe.py --runtime-root
     local/runtime/g4-lap704-path-baseline-run1 --artifact-root
     /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260927_lap704_g4_path_baseline_run1`
     → exit0, `status=PATH_TRACE_COMPLETE`, `cleanup.ok=true`, `source_unchanged=true`.
  2. run2(근접 대조군, 목적지 오프셋 (0,-6), `MIN_DESTINATION_DISTANCE_TILES`/후보 목록을 진단
     스크립트로 일시 오버라이드 — 제품 스크립트 상수는 미변경, `/tmp/g4_near_control_diag.py`는
     저장소 밖 1회성 진단): 같은 하네스, `local/runtime/g4-lap704-near-control` /
     `temp/Syw2plus_patch/20260927_lap704_g4_near_control` → exit0, 동일 `PATH_TRACE_COMPLETE`,
     `cleanup.ok=true`, `source_unchanged=true`.
  로그 `<artifact-root>/probe.log`, 결과 JSON `<artifact-root>/probe-result.json`(raw
  `(tick,x,y,command,hp)` 샘플 598개/실행, 스키마 `syw2plus.g4-path-baseline-probe.v1`), 캡처
  `after-minimap.png`/`after-fixture.png`/`after-drag.png`/`after-move-click.png`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  하네스 자체는 두 실행 모두 **PASS**(선택20/20, 캡처·정리·SHA 전부 정상, 90초/598틱 trace 완주).
  그러나 이동 명령 도달은 두 실행 모두 **FAIL** — `ever_move_command_count=0`(20기 중
  `command==3`를 관측한 슬롯 0개), `arrival_rate`는 run1 0.0, run2(근접) 0.1이나 그 1기(슬롯1195)는
  실제 이동 없이 드래그 시점 이미 도착반경(3타일) 안에 있던 우연 일치였다(전 슬롯 `path_length=0.0`).
  **유일하게 실제로 이동한 것은 선택에 포함된 기존 워커(슬롯1198, run2에서 (18,48)→(8,43) 이동,
  `arrived=true`)뿐**이고 새로 생성한 fixture 유닛 19기는 근접(6타일)·원거리(21타일) 두 목적지 모두
  단 1틱도 좌표가 바뀌지 않았다. STATUS 판정식 그대로 적용하면 "명령도달<20"이 2회 반복 →
  **`NOT_FEASIBLE`(현재 조밀 1타일-간격 fixture로는)**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 코드/EXE 무변경이므로 회귀 위험 없음.
  가장 유력한 원인 가설(미검증, 다음 work가 확인할 것): 워커는 보정 단계(9회 순차 우클릭)에서
  이미 실제 이동 명령을 여러 번 받아 조밀 격자 밖으로 빠져나온 상태로 최종 클릭을 받은 반면, 19기
  fixture 유닛은 1타일 간격으로 서로 바로 인접해 있어(자기 칸 제외 7x8 격자) 동시에 같은 방향으로
  이동을 시도할 때 서로가 서로의 유일한 탈출 경로를 막는 **상호 교착(dense single-tile 인접 집단
  자기차단)**일 가능성이 크다 — 이것이 사실이면 "명령이 전달 안 됨"이 아니라 "명령은 전달됐으나
  충돌 회피가 즉시 0진행으로 교착"인 것이고, 그 자체로 G4 대규모 군집 병목의 실제 raw 관측일 수
  있다. 대안 가설(미배제): 드래그가 워커만 실제로 "이동 가능"한 상태로 잡고 fixture 유닛은 디버그
  주입 경로상 이동 커맨드 디스패치에서 제외되는 다른 플래그 문제일 수 있음 — 이번 lap에서는
  구분하지 못했다. 독립 검수/사용자 승인 없음(work tier 자체 실행 보고).
- 다음 한 가지: **동일 하네스를 sparse fixture(예: 유닛 간 2~3타일 간격, 또는 목적지 방향 반대편에
  격리된 단일 유닛 1기)로 한 번 더 실행**해 "이동 도달"이 회복되는지 확인한다. 회복되면
  (자기차단 확정) 조밀 포메이션 자체가 G4 관찰 대상이 되므로 다음은 조밀도를 낮춰가며 임계
  밀도를 찾는 단계로 진행; 회복 안 되면(디스패치 배제 확정) fixture 생성 경로(`SupplyProbe op=5`)와
  일반 드래그로 만든 유닛의 차이를 직접 비교(예: 생산 큐로 만든 유닛 vs op5 fixture 유닛)해야 한다.
  `tools/g4_path_baseline_probe.py`의 `DESTINATION_OFFSET_CANDIDATES`/`MIN_DESTINATION_DISTANCE_TILES`
  상수는 실제 ≥20타일 요건을 위해 그대로 두고, sparse 대조군은 별도 임시 오버라이드로 먼저 확인한다.

## 추가 관측 (같은 lap 내, 동시 실행 중이던 다른 세션의 STATUS 갱신과 교차 확인)

이 lap 진행 중 `docs/STATUS.md`가 이 세션이 쓰지 않은 시각(06:05Z)에 갱신된 것을 발견했다 —
같은 저장소 경로에서 **다른 `claude --print` 프로세스(PID 2926284, 05:35Z 시작)가 동시에 같은
lap704를 작업 중**이었다(정확히 같은 run1 목적지 화면좌표 `[1375,337]`을 인용). 그 세션이 남긴
관찰: "게임 화면은 1600×1200 프레임 좌상단 800×600(HUD y≥480)에 그려지므로 x>800 클릭은 게임
밖일 가능성이 크다." 이 세션이 독립적으로 재확인: run1/run2에서 실제로 계산된
`destination_candidates` 12개 전부를 `(40, 760, 40, 460)`(가정 800×600 native client, HUD
y≥480 제외) 기준으로 재검사하면 **12개 전부 탈락**한다(x>760 또는 y>460). 즉 이 화면·카메라
줌 레벨에서는 워커 기준 카메라를 고정한 채 우클릭만으로 ≥20타일 목적지에 도달하는 것이
근본적으로 불가능하다 — 카메라를 목적지 쪽으로 옮긴 뒤(미니맵 클릭 또는 방향키 스크롤) 클릭하는
2단계 절차가 필요하다. `SAFE_SCREEN_BOX`를 `(40, 760, 40, 460)`으로 보수적으로 좁혀 이후 실행이
화면 밖 클릭을 "성공"으로 오인하지 않게 했다(이 변경만으로는 ≥20타일 목적지에 도달하지 못하며,
카메라 이동 없이 재실행하면 `ProbeError`로 명확히 실패한다 — 실측은 하지 않고 좌표 재계산으로
확인). 카메라 재배치 구현은 동시 실행 중이던 세션과의 중복 작업을 피하기 위해 이 lap에서는
시도하지 않았다. **다음 한 가지(갱신, STATUS.md와 합의):** ① 조밀 fixture 자기차단 여부(sparse
대조군, 위 원안)와 ② 카메라 재배치 후 클릭(미니맵 또는 스크롤) 중 최소 하나로 ≥20타일 이동을
실제로 성립시켜야 baseline 3회 측정을 시작할 수 있다 — 두 원인은 서로 배타적이지 않다(run1은
(a)만으로 전원 0이동 설명 가능, near-control은 목적지가 화면 안이었음에도 워커 1기만 이동해
(b)가 별도로 존재함을 시사).
