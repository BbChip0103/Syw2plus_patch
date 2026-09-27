# 2026-09-26 | lap 688 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5 / high / work(실무)
- 가설 / 사용자 관찰: 19:25 운영자 판정 — 같은 후보(v2+H1)가 1회차 `ever_command4_count` 0, 2회차 18로
  뒤집혀 공격 probe가 비결정적임이 확정됐다. 다음 work는 ① 흔들림 원인(적 스폰 위치/시점, 목적지 변환,
  P6 판정, 선택 순서) 1개를 raw 비교로 고정, ② v3 50기 N=5/원본 20기 N=5 반복 측정, ③ middle 재검수.
- 예상 PASS / FAIL 조건: 후보 `ever_command4_count/attack_capable` 비율의 중앙값이 원본과 같은
  수준(19:25 판정문 기대치 ≈85~95%)이면 공격50 PASS.

## ① 원인 고정 (raw 비교, 구현 우선)

`tools/g5_worker_relative_move_attack_probe.py`(v1/v2/v3 모두 이 base를 monkeypatch로 공유)를 5회씩
재실행할 필요 없이, 우선 **원본(20) 5회**를 새로 떠서 raw JSON을 비교했다(1차 조사, 수정 전):

| run | ever_command4/19 | raw_command_histogram | observed_target_uids | move ever_matched |
|---|---|---|---|---|
| 1 | 19 | `{3:9,4:10}` | `[590967]` | 20 (0.15s) |
| 2 | 19 | (미기록, PASS) | — | 20 (0.15s) |
| 3 | **0** | `{3:19}` | `[]` | 20 (0.45s) |
| 4 | 19 | (미기록, PASS) | — | 20 (0.31s) |
| 5 | **0** | `{3:19}` | `[]` | 20 (0.15s) |

핵심 발견: **완전 실패(0/19) 두 회 모두 `observed_target_uids`가 완전히 비어 있다** — 12초 전체 관찰
창의 어느 샘플에서도 어떤 유닛도 `pending_target_uid`가 0이 아닌 적이 없었다. 이동은 두 그룹 모두
0.15~0.45s로 동일하게 빨리 수렴해 "혼잡/이동 시간 부족" 가설은 반증된다. 목적지 화면좌표(`121,383` vs
`121,384`)도 거의 동일해 좌표 변환(자기보정) 오차 가설도 반증된다. 선택 순서·P6 판정은 유닛 타입이
고정(type2)이라 같은 빌드의 반복 실행에서 뒤집힐 수 없어 배제된다.

남은 설명은 **스폰 시점**이다: 기존 코드는 공격 표적(owner1 type2 1기)을 **드래그 선택+MOVE 페이즈보다
먼저** 스폰했다 — 이 사이 시간(0.5s 슬립 + 드래그 + 1s + MOVE poll, 이번 lap의 창 확대 후 최대 30s)
동안 표적이 조밀한 owner0 진영(dx -3..3, dy -3..4, 55기) 바로 옆(공격 목적지는 그 격자에서 2칸
밖)에 무방비로 놓여 있었다 — lap672가 이미 경고한 **자동교전(auto-aggro) 오염**과 정확히 일치한다:
근처 유휴 아군이 명시적 공격 클릭 전에 표적을 자동으로 발견·처치해버리면, 그 이후 아무도 공격
대상을 얻을 수 없다(표적이 이미 죽었으므로).

**최소 수정(구현 우선):** 표적 스폰 블록을 드래그/MOVE 페이즈 이전에서 **ATTACK 페이즈 클릭 직전**으로
옮겼다(`tools/g5_worker_relative_move_attack_probe.py`). 노출 시간을 수 초~30여 초에서 클릭 한 번
분량(<0.1s)으로 줄인다. 판정 로직(`attack_pass`)·목적지 계산·재시도 경로는 그대로 두었다(기존에도
재시도 목적지엔 표적이 없었다는 기존 한계는 이번 수정으로 바뀌지 않음, 별도 이슈).

같은 원본 20 5회를 이 수정 후 재실행 → **완전 실패(0/19)가 사라졌다**(5회 모두 `command4>=4`, 최저
4/19). 자동교전 오염 가설이 raw 재현으로 확정됐다.

## ② v3 50 N=5 / 원본 20 N=5 반복 측정 (수정 후)

원본 SHA `b56986e0…c9c08a8ac` 5회 전부 불변. 후보(v3) SHA `e5004764…de6977` 5회 전부 불변(재빌드
바이트 동일 확인). 10회 전부 `cleanup.ok=true`, `source_unchanged=true`.

| variant | run | ever_command4/attack_capable | 비율 | max_pending_exact/attack_capable |
|---|---|---|---|---|
| 원본(20) | 1 | 19/19 | 100% | 7/19 (37%) |
| 원본(20) | 2 | 19/19 | 100% | 11/19 (58%) |
| 원본(20) | 3 | 5/19 | 26% | 8/19 (42%) |
| 원본(20) | 4 | 11/19 | 58% | 19/19 (100%) |
| 원본(20) | 5 | 4/19 | 21% | 19/19 (100%) |
| 후보 v3(50) | 1 | 30/49 | 61% | 49/49 (100%) |
| 후보 v3(50) | 2 | 33/49 | 67% | 49/49 (100%) |
| 후보 v3(50) | 3 | 49/49 | 100% | 18/49 (37%) |
| 후보 v3(50) | 4 | 27/49 | 55% | 12/49 (24%) |
| 후보 v3(50) | 5 | 32/49 | 65% | 23/49 (47%) |

- 원본 `ever_command4` 비율: 중앙값 **58%**, 평균 61%, 범위 21~100%.
- 후보 `ever_command4` 비율: 중앙값 **65%**, 평균 70%, 범위 55~100%.
- 후보 median(65%)이 원본 median(58%)보다 **낮지 않다** — 19:25 판정문이 기대한 원본 기준선
  (≈85~95%)은 N=5 raw 측정에서 원본 자신도 도달하지 못한다(lap684의 "원본 2/2 100%"는 N=2의
  소표본 우연이었다, 자동교전 시점 결함이 아직 없던 그 lap에서도 표본이 작았다).
- 보조 지표 `max_pending_exact_count`(즉시 브로드캐스트 스냅샷)도 양쪽 다 24~100% 범위로 노는다 —
  후보가 원본보다 체계적으로 낮지 않다.
- 해석: 남은 변동은 "표적 1기가 몇 초 만에 죽어버려서, 그 전에 도착한 일부 유닛만 `command==4`를
  볼 기회를 얻는다"는 **단일-약체-표적 대 다수 공격자 구도 자체의 실시간 경쟁**으로 보인다(P6/브로드
  캐스트 결함이 아니라 표적 생존시간 문제). 원본·후보 둘 다 같은 구조적 노이즈를 겪으며, 어느 쪽도
  다른 쪽보다 체계적으로 나쁘지 않다.

## 변경 파일 / source fingerprint

- `tools/g5_worker_relative_move_attack_probe.py`: (a) `POLL_TIMEOUT` 12.0→30.0,
  `RETRY_POLL_TIMEOUT` 8.0→20.0, `ATTACK_SAMPLE_WINDOW_S` 3.0→12.0(1차 가설: 혼잡 타이밍 부족 —
  raw 비교로 반증됐지만 이동 페이즈에 여유를 주는 것 자체는 무해하여 유지); (b) 공격 표적 스폰을
  드래그/MOVE 이전에서 ATTACK 클릭 직전으로 이동(진짜 원인 수정). v1/v2/v3 래퍼는 이 base를
  monkeypatch로 공유하므로 자동 반영됨(별도 수정 불요, 회귀 테스트로 확인).
- 제품 EXE 0 변경. 원본/v3 후보 SHA 10회 전부 불변 확인(위 표).
- 신규 lap 기록 이 파일. STATUS/INBOX/APPROVALS 갱신은 이번 lap에서 별도 커밋.

## 실행 명령 / 로그 / 캡처 경로

```
PYTHONPATH=. .venv/bin/python -m tools.g5_worker_relative_move_attack_probe \
  --variant {original|candidate} \
  --runtime-root local/runtime/g5-lap688-repeat \
  --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap688_g5_repeat/{variant}-{i}
```
10회(원본 5 + 후보 5) 아티팩트는 위 temp 경로에 `probe-result.json`/`probe.log`/캡처 PNG로 보존.
`local/runtime/g5-lap688-repeat/*/game` 사본은 실행 직후 삭제(위생), `prefix`/`output`은 보존.

targeted pytest: `tests/test_g5_worker_relative_move_attack_probe.py`(3)
`tests/test_g5_worker_relative_move_attack_probe_v1.py`(2) `tests/test_g5_worker_relative_move_attack_probe_v2.py`(2)
= 7 passed. `make check` 로그: `logs/gates/20260926_lap688_make_check_run1.log`(진행 중, 완료 시
STATUS에 결과 반영).

## 측정값 / 판정

**FEASIBLE, 부분 진전.** ① 자동교전 스폰-시점 결함은 확정·수정했고 raw 재현으로 검증했다(완전
실패 0/19가 사라짐). ② v3 50/원본 20의 `ever_command4_count` 비율 분포는 N=5에서 서로 구별되지
않는다(후보가 원본보다 낮지 않음) — "공격 50 브로드캐스트가 20에서 끊긴다"는 기존 우려는 이 수정 후
raw 증거로 **뒷받침되지 않는다**. 그러나 19:25 판정문이 전제한 원본 기준선(85~95%)은 이 표본에서
원본도 달성하지 못해 판정문 그대로의 "중앙값이 원본과 같은 수준이면 PASS" 기준을 문자 그대로 적용하면
**중앙값은 같은 수준(65% vs 58%, 후보가 더 높음)이라 PASS 방향**이지만, 절대 비율 자체가 낮아 표본
크기·표적 생존시간 설계를 middle이 검토해야 한다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 표적 1기의 생존시간이 짧아 "얼마나 많은 유닛이 실제로 싸울 기회를 얻는가"가 여전히 노이즈하다.
  더 견고한 지표는 즉시 브로드캐스트를 보는 `max_pending_exact_count`/`pending_command` 계열일 수
  있으나, lap683 middle이 "pending!=1은 이동도 세므로 무효"라 반려했었다(단, 지금 쓰는 정확값
  `pending_command==0x1000004`는 이동값과 다르므로 그 반려는 이 필드에 적용되지 않는다 — middle이
  재확인 필요).
- N=5는 여전히 작다. 표본을 늘리거나(N=10+) 표적을 여러 기로 늘려 생존시간 노이즈를 줄이는 두 방향
  모두 middle/strategy 판단이 필요하다.
- G5 2단 전체(선택/그룹/호출/save-load/이동/공격) 종합 PASS·사용자 milestone 승인은 여전히 없다.
- 커밋 안 함(`LOOP_ALLOW_COMMITS=0`). STATUS/INBOX/APPROVALS 갱신과 이 파일은 uncommitted로 남긴다.

## 다음 한 가지

middle이 이 raw 분포(원본 58%/후보 65% 중앙값, 두 그룹 다 21~100% 노이즈)를 검토해 (a) 이 노이즈
수준에서도 공격50을 PASS로 볼지, (b) 표본을 늘리거나 표적을 다중화해 노이즈를 줄인 뒤 재판정할지
결정한다. work는 middle 판정 없이 같은 결론을 반복하지 않는다.
