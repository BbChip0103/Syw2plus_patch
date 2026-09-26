# 2026-09-26 | lap 671 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high (Codex 401로 임시 전환, `loop/env.local.sh`); 지정 역할 work, middle 없이 STATUS lap670 승격 지시 ①②③ 수행.
- 가설 / 사용자 관찰: STATUS/INBOX 08:15 지시: ① op8을 UI 공격 클릭 전 첫 명령으로 실행해 깨끗한 `raw_return`/`+0x38C` 확인, ② `command=8` 관측이 `FUN_0048DDD0` 점프표(`0x48ea5c`)의 어떤 분기인지 정적 확인, ③ 등각 스프라이트 오프셋을 감안해 공격 클릭 y좌표를 위로 스윕. 세 가지 모두 좁게 확인하고 candidate50/`FUN_004AE550`은 보류.
- 예상 PASS / FAIL 조건: 세 가지 중 하나가 원인을 좁히면 다음 work에 넘길 구체적 다음 한 가지가 나온다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `tools/g5_attack_hit_offset_probe.py`, `tools/g5_attack_type2_domain_probe.py`, `tests/test_g5_attack_hit_offset_probe.py`(제품 EXE 미변경, read-only 진단). 커밋 0(LOOP_ALLOW_COMMITS=0, 전체 저장소 uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `b56986e0…c9c08a8ac` 3회 실행(run1 원본-only, run2 원본-only, type2-domain 원본-only) 모두 불변. 후보 미실행(이번 lap 범위 밖). 격리 Wine/Xvfb 1600×1200, PS3 solo owner0; run1/run2는 기존 worker(slot1198, type31)+owner1 SEED_TYPE=2 fixture; type2-domain run은 owner0/owner1 각각 신규 SEED_TYPE=2 1기.

## ① 깨끗한 op8 (UI 공격 클릭 이전)

`tools/g5_attack_hit_offset_probe.py` run1: 9점 보정(잔차 1.33, lap670과 동일 정밀도) 뒤, **UI 'A'키를 한 번도 누르지 않은 상태**에서 bridge op8(`FUN_00415480`)을 직접 호출. 결과: `raw_return=0`, `+0x38C=0` — 오염 없이도 여전히 거부. run2(같은 스크립트, idle-wait 추가 후): 소스 `command=1`(idle)까지 기다린 뒤 호출해도 `raw_return=0` 그대로. ⇒ UI 오염 가설은 완전히 배제되고, idle 상태 자체도 충분조건이 아니었다(②③에서 원인 특정).

## ② `command=8` 정적 확인 + `FUN_00415480`/`FUN_00415880` 전체 재디스어셈블

capstone+pefile로 원본 `.text`를 직접 읽었다(원본 SHA 재확인 후, 읽기 전용).
- `FUN_0048DDD0` 점프표 `0x48ea5c`: index=value−1이며 **값8→인덱스7→`0x48e7f9`**는 `push 7; call FUN_00410660`로, case값4(공격, `0x48e815`)와 무관한 완전히 다른 상태다. `command=8`은 공격 오염이 아니라 그냥 다른 정상 상태(경로 재계산/이동 서브상태로 추정)였다.
- `FUN_00415480`(발부자)과 `FUN_00415880`(P6 게이트)을 전체 디스어셈블해 `analysis/memory_maps/g2_original_order_admission_contract_lap523.md`·`g2_unit_attack_domain_flags_1d8_lap525.md`(기존 G2 문서, 이번에 원본 바이트로 독립 재현·일치 확인)의 P1~P6 술어를 그대로 재확인했다: **P6 = 소스 `+0x1D8` bit `0x4`가 0이면 목표 `+0x1BC`==1을 무조건 거부**(소스의 idle/이동/공격 상태와 무관하게 적용되는 공통 게이트).
- run1/run2 raw 계측: 소스(worker, type31) `+0x1D8=0x10001`(bit `0x4`=0), 목표(SEED_TYPE=2) `+0x1BC=1`. ⇒ **worker는 애초에 이 목표를 공격할 수 없는 타입이다.** lap666~671의 모든 실패는 UI 클릭 정밀도나 좌표 변환과 무관하게 이 타입 불일치가 원인이었다.

## ③ y-offset 스윕 (idle-wait 포함)

`Y_SWEEP_OFFSETS=[0,-8,…,-72]`, 각 시도 전 idle 대기로 개선했지만 **소스가 worker인 한 ②의 게이트로 항상 거부**되므로 전원 미스(`y_sweep_hit=null`). 스윕 자체는 정상 동작했다(idle 도달 확인, 클릭 주입 확인) — 클릭 정밀도 가설은 이것으로 배제된다.

## 결정적 확인 (②의 가설을 실제로 검증)

`tools/g5_attack_type2_domain_probe.py`: worker 대신 **owner0 SEED_TYPE=2 신규 유닛**을 공격자로 소환해 같은 op8을 호출. 결과 **`status=PASS_TYPE2_DOMAIN_ATTACK`, `raw_return=1`, `command=4`(공격), `pending_target_uid=394410`이 목표 handle과 완전히 일치**. `source_unchanged=true`, `cleanup.ok=true`.
⇒ **G5 공격 게이트 미달성의 근본 원인은 엔진 결함도 UI 좌표 문제도 아니라, 테스트가 공격 능력이 없는 타입(worker, type31)을 공격자로 써 왔기 때문이다.** SEED_TYPE=2(= G5 55기 fixture 자체의 타입)는 이미 domain 공격 권한(bit `0x4`)을 갖고 있어 서로 공격할 수 있다.

- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. python3 tools/g5_attack_hit_offset_probe.py --runtime-root local/runtime/g5-lap671-attack-offset[-run2] --artifact-root .../g5_lap671_attack_offset/run{1,2}`; `PYTHONPATH=. python3 tools/g5_attack_type2_domain_probe.py --runtime-root local/runtime/g5-lap671-type2-domain --artifact-root .../g5_lap671_attack_offset/type2_domain`. 결과 JSON 3건 모두 위 경로에 보존(`probe-result.json`). 회귀 `PYTHONPATH=. pytest -q tests/test_g5_attack_hit_offset_probe.py tests/test_g5_screen_world_calibration.py tests/test_g5_candidate_drag_probe.py` → 9 passed. `make check`(`.venv`) → **922 passed in 635.85s**, ruff/compileall/mypy/`CONTEXT_PASS` 모두 PASS(로그 `/tmp/lap671_make_check.log`, 세션 내 완주 대기). `checks/safety.sh check` → `SAFETY_PASS`. 각 회차 game 사본(2.2~2.7GB×3)은 즉시 삭제.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): ①②③ 개별 조사는 원인 배제/좁히기 목적으로 각각 완료(FAIL이지만 진단적으로 유효). **결정타는 별도 확인 실행(type2-domain)에서 PASS** — 근본 원인 확정. G5 제품 공격50/사용자 승인은 여전히 미달성(candidate50·실제 UI 경로는 이번 lap 범위 밖).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 새 진단 도구 3개만 추가, 제품 EXE/보호 원본 0 변경. `source_unchanged=true`(3회 모두). G5 제품 PASS·2단 검수·사용자 승인은 여전히 없음. `FUN_004AE550` 수정과 candidate50 paired 실행은 이번 lap에서 착수하지 않았다(범위 밖으로 유지).
- 다음 한 가지: G5 공격 서브테스트를 **worker가 아니라 candidate50 드래그로 선택된 army 유닛(SEED_TYPE=2) 중 하나를 공격자로** 재실행한다. (a) 먼저 원본에서 fixture 55기 중 1기를 공격자로 선택→우클릭/`A`+좌클릭으로 실제 UI 경로 공격50 확인(이번 lap의 좌표 변환·idle-wait 로직 재사용), (b) 원본 PASS 확인 후에만 candidate50 동일 절차로 paired 실행. `FUN_004AE550`(20칸 전제 명령 패커)은 공격50이 실제로 막힐 때만 손댄다.
