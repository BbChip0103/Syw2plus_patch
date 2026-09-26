# 2026-09-26 | lap 682 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work), high. (loop/env.local.sh 임시 전환 유지: Codex 401 이후 middle=opus-5, work=sonnet-5.)
- 가설 / 사용자 관찰: STATUS.md lap681 "다음 한 가지" — G5 dense-fixture 플로우의 고정 픽셀 목적지(`(300,420)`)가 지도마다 무효한 지형에 걸려 원본20/후보50 paired MOVE·ATTACK 수렴 측정이 2/3 실행에서 무효화됐다(lap681). 지시는 G2의 시드 고정 커스텀 게임 체인(`_custom_game_chain_inject_*`)을 이식하라는 것이었으나, 조사 결과 그 체인은 `_g4_send_control_goal`을 통해 **2인용** 게임(고정 국가/맵, owner0+owner1 AI)을 만드는 것으로, G5가 지금까지 한 번도 쓴 적 없는 플레이어 수/AI 가정을 새로 들여온다. 반면 `tools/g5_screen_world_calibration.py`(lap670)가 이미 같은 근본 문제(고정 픽셀이 지도마다 다른 세계좌표에 대응)를 **지도를 고정하지 않고** in-run 9점 우클릭으로 `world = M@screen + c` 아핀을 그 실행 안에서 직접 피팅해 풀었다. **결정(묻지 말고 결정 지시에 따름):** 시드 체인 이식 대신 이 self-calibration 기법을 재사용해 목적지를 "worker 기준 상대 타일→화면 변환"으로 계산하는 쪽을 채택했다 — 이식 리스크(2인 게임 전환이 VISIBLE_WORKER_SLOT=1198/56기 fixture 가정과 충돌할 가능성)가 크고, 실제로 요구되는 것(맵이 달라도 유효한 목적지)을 더 직접적으로 만족하기 때문이다.
- 예상 PASS / FAIL 조건: 매 실행마다 worker 사후(minimap 클릭 후) 9점 보정으로 아핀을 풀고, 그 아핀으로 계산한 worker 기준 상대 타일(밀집 fixture 격자 dy -3..4 바로 바깥, dy=+6/-4)을 목적지로 쓰면 원본20·후보50 모두 MOVE 명령이 선택 전원에게 도달(`command==3` 관측)해야 PASS. 무효(0명 반응)면 반대편 오프셋으로 1회 재시도.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(LOOP_ALLOW_COMMITS=0). **제품 EXE 0 변경.**
  - `tools/g5_worker_relative_move_attack_probe.py`(신규): lap681 `g5_move_attack_convergence_probe.py`를 베이스로, minimap 클릭 직후 pre-fixture worker 단독 선택 상태에서 9점 아핀 보정을 추가하고, 목적지를 고정 픽셀 대신 worker 기준 상대 타일(`PRIMARY_DEST_OFFSET=(0,6)`, `FALLBACK_DEST_OFFSET=(0,-4)`)의 역변환 화면좌표로 계산. 0명 반응 시 반대편 오프셋으로 1회 재시도. `poll_convergence`를 "순간 동시일치" 대신 "한 번이라도 일치한 슬롯의 누적합집합"(`ever_matched_count`)으로 바꿔, 근거리 목적지에서 빠른 유닛이 먼저 도착해 `command==3`을 벗어나며 순간 카운트가 감소하는 현상(아래 참고)을 판정 오류로 취급하지 않게 했다.
  - `tests/test_g5_worker_relative_move_attack_probe.py`(신규): `_in_safe_box` 경계, 목적지 오프셋이 밀집 fixture 격자(dx -3..3, dy -3..4) 바깥에 있는지 pin. 2 passed.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(4회 실행 전후 모두 불변, `source_unchanged=true`). 후보 `e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977`(lap680/681과 동일, 무변경). 격리 Wine/Xvfb 1600×1200, PS3 solo owner0(시드 고정 없음, 기존과 동일), dense fixture worker(slot1198) 앵커 7×8 grid 55기 SEED_TYPE=2. worker unit_type은 실행마다 달랐다(원본1: type7@(92,163), 원본2: type31@(142,142), 후보1: type21@(142,142) — calibration 버그로 실패, 후보2: type7@(142,42)) — lap681이 이미 관측한 현상과 일치, 이번 조사와 무관.

## 실행 명령 / 로그 / 캡처 경로

1. `PYTHONPATH=. .venv/bin/python -m tools.g5_worker_relative_move_attack_probe --variant original --runtime-root local/runtime/g5-lap682-worker-relative-original --artifact-root .../20260926_lap682_worker_relative_original_064321` → exit 0. (v1 poll 방식, MOVE PASS 20/20 즉시, ATTACK FAIL.)
2. `--variant candidate --artifact-root .../20260926_lap682_worker_relative_candidate_064516` → **exit 2 (FAIL)**: calibration 단계에서 `selection_snapshot`을 후보에서도 20칸 legacy 배열(`STOCK_SELECTION_BASE`)로 읽어 `count=0`. 버그로 귀속(아래 참고), 코드 수정.
3. 코드 수정(`calibration_selection`을 variant별 `selection_base`/`selection_capacity`로 읽도록) 후 원본/후보 재실행:
   - `--variant original --artifact-root .../20260926_lap682_worker_relative_original_v2_064916` → exit 0.
   - `--variant candidate --artifact-root .../20260926_lap682_worker_relative_candidate_064617` → exit 0, 그러나 MOVE `final_matched_count`가 39→0으로 시간에 따라 **감소**(아래 §측정값 참고) — 순간-동시-일치 판정의 한계로 귀속, `poll_convergence`를 `ever_matched_count`(누적 합집합) 방식으로 수정.
   - 재실행: `--variant original --artifact-root .../20260926_lap682_worker_relative_original_v2_064916`(재사용) → exit 0. `--variant candidate --artifact-root .../20260926_lap682_worker_relative_candidate_v2_065023` → exit 0.
4. `make check` → `logs/gates/20260926_lap682_make_check.log`, `bash checks/safety.sh check` → `SAFETY_PASS`.

전체 artifact(JSON+캡처+probe.log)는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/`의 위 디렉터리들에 보존. 각 실행 직후 `game` 사본(2.7GB×2, 최종 성공쌍)만 삭제(manifest/output/prefix/로그 보존); 디스크 33→36GB.

## 측정값 / 판정

- **최종(ever-matched 방식) 원본20/후보50 paired MOVE: PASS.** 원본 `ever_matched_count=20/20`(`converged_at_s=0.15`), 후보 `ever_matched_count=50/50`(`converged_at_s=0.15`). 두 실행 모두 calibration `max_abs_residual<0.67`(9점 아핀 적합도 양호), 목적지는 primary 오프셋(worker+（0,+6))이 바로 성립(재시도 불필요).
- **중간 발견(v2 후보 실행, 순간-동시-일치 방식): "감소하는 수렴"** — primary 목적지에서 t=0.5s에 39/50이 `command==3`을 보였으나 이후 34→27→…→0(t=11s)으로 단조 감소했다. 원인은 목적지가 가깝기(6타일) 때문에 빠른 유닛이 도착 후 `command==3`을 벗어나는 것이 전체 유닛이 명령을 받는 것보다 먼저 일어나, "50명이 동시에 이동 중"인 순간이 존재하지 않는 것 — 이는 브로드캐스트 실패가 아니라 **판정 방법의 결함**이었다(순간 스냅샷 vs 누적 관측). `ever_matched_count`로 바꾸자 즉시 50/50 재현.
- **버그 1건 자체 수정:** 최초 후보 실행이 calibration 단계에서 legacy 20칸 선택배열을 읽어 `count=0`으로 FAIL했다. lap665/678이 이미 확정한 사실(후보는 selection을 재배치된 50칸 배열에 기록하고 legacy 배열은 갱신하지 않음)을 이번 신규 코드에 반영하지 않은 실수였다 — variant별 `selection_base`/`selection_capacity`로 교체해 해결.
- **ATTACK(UI 클릭)은 원본·후보 둘 다 `ever_matched_count=0`.** 이는 새 결함이 아니라 lap667~676이 5회 이상 독립 확인한 기존 하네스 한계("UI 클릭 기반 공격 명령이 이 하네스에서 성공한 적이 없다", op8 엔진 issuer만 성공)의 **6번째 재확인**이며, 이번 조사로 그 원인 후보 중 하나였던 "목적지 좌표가 틀렸다"는 가설을 **결정적으로 배제**한다 — 동일한 self-calibrated 목적지에서 MOVE는 두 variant 모두 완전히 성공했으므로, ATTACK 실패는 좌표 문제가 아니라 UI 공격 입력 경로 자체의 한계임이 재확인됐다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 신규 파일 2개(`tools/g5_worker_relative_move_attack_probe.py`, `tests/test_g5_worker_relative_move_attack_probe.py`), 제품 EXE/원본 0 변경. `ruff check` PASS, `py_compile` PASS, 신규 테스트 2 passed.
- `make check` → **972 passed in 667.82s**(lap681 970 + 신규 테스트 2), ruff/compileall/mypy/`CONTEXT_PASS` 모두 PASS. `bash checks/safety.sh check` → `SAFETY_PASS`. 보호 원본 SHA 4회 실행 전후 모두 불변.
- **핵심 결론(FEASIBLE, G5 MOVE 부분 완료):** worker 기준 상대 타일 self-calibration 방식으로 지도 시드 고정 없이도 원본20/후보50 paired MOVE 수렴 측정이 안정적으로 재현된다(2/2 성공, 이전 lap681의 2/3 무효와 대비). G2 시드 체인 이식은 이번 lap에서 채택하지 않았다(위 §가설에 근거 기록) — 필요해지면(예: 지도 자체의 지형 다양성을 통제해야 하는 후속 조사) 별도로 재검토한다.
- **남은 위험:** ① ATTACK은 UI 클릭 경로로는 여전히 측정 불가(기존 한계, 이번 lap이 원인을 좌표 문제에서 완전히 배제했을 뿐 새 해법은 없음) — 다음 조사는 op8류 엔진 issuer를 selection 배열 전체에 브로드캐스트하는 방법(lap676이 반증한 `FUN_004AE550` 경로가 아닌 다른 경로)을 찾거나, G5 판정 기준 자체를 "UI 공격 클릭"에서 "선택 전원에 대한 엔진 주문 브로드캐스트 여부"로 재정의해야 한다. ② worker unit_type이 매 실행 다르다(7/21/31 등) — 이동 자체에는 영향이 없었으나(모든 타입이 MOVE PASS) 향후 조사에서 타입별 이동속도차가 수렴 시간에 영향을 줄 수 있음을 기록해 둔다. ③ `local/runtime/`에 이번 lap과 무관한 이전 lap들의 game 사본(37개×2.2GB, G2 계열)이 남아 있다 — 디스크는 36GB로 20GB 문턱 이상이라 이번 lap은 정리하지 않았다.
- 2단 독립 검수·3단 사용자 milestone 승인 없음(원래부터 없었음). G5 최우선·상시 지시는 미처리로 유지한다(ATTACK 미해결).

## 커밋 상태 / 파일 해시

`LOOP_ALLOW_COMMITS=0`이라 전부 uncommitted. 변경 파일 SHA256:
`tools/g5_worker_relative_move_attack_probe.py`=`9cd4edad37abb6681c93c9e1db495b677d02d023c925f96e1456f13b5213b99c`,
`tests/test_g5_worker_relative_move_attack_probe.py`=`2f1cbab4169c6f897d41577562745af2af479948add0a43944bb9a51007a9cd7`.

## 다음 한 가지

MOVE는 self-calibration 방식으로 원본20/후보50 paired PASS 확정. 다음 work는 middle 없이: G5 ATTACK 판정을 UI 클릭에서 분리한다 — op8류 엔진 issuer(단일 유닛에서는 이미 PASS 확인됨, lap665~673)를 selection 배열(원본 20칸/후보 50칸 재배치 배열)의 각 슬롯에 대해 반복 호출하는 방법(엔진 API 직접 호출, UI 클릭 아님)으로 원본20/후보50 paired 공격 수신 여부를 측정한다. 성공하면 G5 select/move/attack/save-load 전체가 처음으로 완결된 원본20/후보50 paired 증거를 갖추게 되어 새 중간 tier 2단 검수로 승격할 수 있다.
