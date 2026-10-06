# 2026-09-27 | lap 718 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work).
- 가설 / 사용자 관찰: lap717이 middle 검수 요청 항목 (d)로 남긴 "공격 N=5 반복 추가 여부"를 middle
  판단 전에 독립적으로 채워, 다음 middle 세션이 판단만 하면 되도록 한다(구현 우선, 승인 대기 중
  안전한 독립 작업). lap717 공격 단일측정(30/49)은 v3 lap688 N=5 분포 안에 들었으나 N=1이었다.
- 예상 PASS / FAIL 조건: v4 후보(50선택) N=5 `ever_command4_count` 비율의 중앙값이 원본(20선택)
  lap688 N=5 중앙값(58%)보다 체계적으로 낮지 않으면 공격 브로드캐스트 50 근거 유지, 낮으면 FAIL로
  기록하고 middle에 회부.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **제품 코드/패치 파일 0 변경.**
  `tools/g5_worker_relative_move_attack_probe.py`, `patches/selection/g5_selection_cap50_v4.py`
  모두 무수정(원문 그대로). lap717과 동일한 방식으로 모듈 전역 `g5`/`TARGET_SHA`를 v4로 monkeypatch한
  임시 러너(`/tmp/g5_v4_attack_n5_runner.py`, 저장소 밖, 커밋 대상 아님)로 기존 probe의 `run_probe()`를
  그대로 4회 추가 호출했다(run1=lap717 기존 결과 재사용, run2~5 신규).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(4회 실행 전부
  `source_unchanged=true`). v4 후보 `0e472792410ddc87eb5eee9809c99761da61d8afa23e73638db0fae5e10f9cbb`
  (lap717과 동일, 4회 재빌드 모두 `candidate_sha256` 일치). 격리 Wine/Xvfb 1600×1200, PS3 solo,
  owner0 dense fixture 55기(SEED_TYPE=2)+owner1 표적 1기(ATTACK 클릭 직전 스폰, lap688 수정 반영).

## 실행 명령 / 로그 / 캡처 경로

`PYTHONPATH=. .venv/bin/python /tmp/g5_v4_attack_n5_runner.py {2,3,4,5}` — 각 `runtime_env.prepare()`
+ `tools/g5_worker_relative_move_attack_probe.run_probe(..., variant="candidate")`(원문 무수정) 1회.
artifact: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260927_lap718_v4_attack_n5/candidate{2..5}/probe-result.json`
(run1은 lap717 기존 artifact `.../20260927_lap717_v4_regression/moveattack_candidate1/` 재사용).
각 실행 직후 `local/runtime/g5-v4-attack-n5-run{2..5}/*/game` 사본(~2.2GB)만 삭제, output/manifest/
prefix/로그는 보존(디스크 위생 규칙). 디스크 여유는 실행 전후 32~34GB로 20GB 미만 진입 없음.

## 측정값 / 판정

| run | ever_command4/attack_capable | 비율 | max_pending_exact | attack_pass | move_pass | 크래시 |
|---|---|---|---|---|---|---|
| 1(lap717 재사용) | 30/49 | 61% | 14/49(29%) | False | True | 0 |
| 2(신규) | 31/49 | 63% | 22/49(45%) | False | True | 0 |
| 3(신규) | 28/49 | 57% | 18/49(37%) | False | True | 0 |
| 4(신규) | 24/49 | 49% | 49/49(100%) | **True** | True | 0 |
| 5(신규) | 32/49 | 65% | 49/49(100%) | **True** | True | 0 |

- v4(50선택) `ever_command4` 비율: 중앙값 **61%**(24~65% 범위), `attack_pass` 2/5.
- 대조: 원본(20선택) lap688 N=5 — 19,19,5,11,4/19 = 100/100/26/58/21%, 중앙값 **58%**.
- 대조: v3(50선택) lap688 N=5 — 30,33,49,27,32/49 = 61/67/100/55/65%, 중앙값 **65%**.
- v4 중앙값(61%)은 원본 중앙값(58%)보다 낮지 않고, v3 중앙값(65%)과 4%p 차이로 같은 변동폭
  안에 있다(둘 다 24~100% 넓은 범위, 표적 1기 생존시간 경쟁에 기인한 것으로 lap688이 이미 귀속한
  구조적 잡음). **v4가 v3보다 체계적으로 나쁘다는 신호 없음 — 예상 PASS 조건 충족.**
  `attack_pass`(순간 피크 전원 동시 pending 기준)는 5회 중 2회 True로, v3/lap684~688에서도 흔했던
  표본잡음 패턴과 일치한다(단일 표적이 죽는 시점에 따라 관측 창을 놓칠 수 있음, 별도 결함 아님).
- 4회 전부 `status=CONVERGENCE_COMPLETE`, `cleanup.ok=true`(잔류 프로세스 0), `source_unchanged=true`,
  `candidate_sha256` 결정론적 일치, `move_pass=true`(이동 50/50 부수 확인). 크래시 0.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 제품 EXE/패치 파일 변경 없음 — 이 lap은 lap717이 이미 만든 v4 후보에 대한 **추가 측정**만 했다.
- middle 검수 요청 (d) "공격 N=5 반복 추가 필요 여부"에 답할 근거를 만들었을 뿐, middle의 (a)(b)(c)
  (게이트 opcode 대조, 22개 비명령 호출부 안전성, monkeypatch 재사용 유효성 판정)는 여전히 미해결
  — work tier가 대신 판정하지 않는다.
- 2단 독립 검수·3단 사용자 milestone 승인 없음. G5 최우선 지시는 미처리로 유지.

## 다음 한 가지

middle(Opus5/Sol)이 lap717+lap718을 합쳐 독립 검수한다: (a)(b)(c)는 lap717 그대로, (d)는 이 lap의
N=5 표(중앙값 61% vs 원본58%/v3 65%, 낮지 않음)로 답변됨 — 추가 반복 불요로 판단할지 확인 요청.
middle PASS 시 3단 사용자 milestone(G5 v4 최종 확정) 요청, HOLD/FAIL 시 원인 1개 특정해 다음 work가
수정. 승인 대기 중 이 work tier가 독립으로 진행 가능한 G5/G1/G4 추가 항목은 현재 없음(G1/G4는 사용자
지시로 G5 완료까지 보류).
