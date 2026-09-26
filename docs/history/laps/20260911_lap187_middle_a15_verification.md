# 2026-09-11 | lap 187 | 목표 G1 (카드2 Stage A / A-15 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle tier
  (진단·계획·확인). 구현은 하지 않았다. 게임/Wine/Xvfb/Stage B/P6 실행 0회.
- 가설 / 사용자 관찰: lap186 A-15가 lap185 요구 (1)~(4)를 모두 충족하는가.
  특히 요구 (2) "`truncation_exceeds_threshold`가 같은 레코드의 ratio/threshold와 항상 일치한다".
- 예상 PASS / FAIL 조건: source SHA 일치, 전체 게이트 재현, clamp 경로 독립 probe에서
  pre-poll 잘림과 run-deadline clamp가 분리되고 ratio/threshold/exceeds가 모든 조합에서 일치.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/STATUS.md`, `loop/ESCALATE_SOL`, 본 기록. 제품/도구 코드 변경 없음(middle은 구현하지 않는다).
  커밋 없음(`LOOP_ALLOW_COMMITS` 미설정).
  검수 대상 SHA — `tools/runtime_env.py`
  `f5f0abfd8e5c11bf4e5027e6655ec6303799ab0c17122ef5704ff727411028f8`(lap186 기록은 마지막
  한 글자 `8`이 누락된 63자로 적혔다. prefix 일치로 동일 파일 확인, 전사 오류만 정정한다),
  `tests/test_runtime_env.py`
  `e7b9e2817469846da0ddcc7c98010c1a4ca4f52b23729214c370ce8faf4c8f5a` (완전 일치).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변
  (`checks/safety.py:15`). 독립 probe는 synthetic monotonic clock만 사용; 플레이어/지도/군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `make check` → 208 passed (37.35s), Ruff clean, compileall, mypy 9 files clean,
  `CONTEXT_PASS`, `EXIT=0` (로그 `/tmp/lap187_makecheck.log`);
  `bash checks/safety.sh check` → `SAFETY_PASS`;
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'wait_state'` → 8 passed;
  `git diff --check` → PASS.
  독립 probe `/tmp/lap187_clamp_probe.py`
  (sha256 `5c35ce4a849bfa2d27dba2f4132554cdcbdb36a0c56fbb760f49cd59d0546a3d`,
  lap186 테스트를 쓰지 않고 `_wait_state`를 직접 호출). PNG/게임 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **A-15 부분 승인 — 요구 (2) 미충족으로 미승인.**

  | probe | pre-poll/timeout/budget | clamped | trunc_s | ratio | exceeds | 분류 | ratio>0.25와 일치? |
  |---|---|---|---|---|---|---|---|
  | P1 | 2.0 / 5.0 / 10.0 | true (5.0) | 2.0 | 0.2 | false | `UNKNOWN_BUDGET_EXHAUSTED` | 일치 |
  | P2 | 4.0 / 6.0 / 10.0 | true (4.0) | 4.0 | 0.4 | **false** | `UNKNOWN_BUDGET_EXHAUSTED` | **불일치** |
  | P3 | 4.0 / 30.0 / 10.0 | false | 4.0 | 0.4 | true | `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` | 일치 |
  | P4 | 0.0 / 30.0 / 10.0 | false | 0.0 | 0.0 | false | `FAIL_NO_EFFECT` | 일치 |
  | P5 | 1.0 / 10.0 / 10.0 | false(경계 등호) | 1.0 | 0.1 | false | `UNKNOWN_BUDGET_EXHAUSTED` | 일치 |

  - 요구 (1) **충족**: `truncation_seconds`는 이제 pre-poll(`wait_started - stage_started`)만
    측정하고, `run_deadline_clamped`/`run_deadline_clamp_seconds`가 clamp를 따로 기록한다
    (`tools/runtime_env.py:2718-2732`). lap185가 보고한 2.0초 pre-poll → 7.0초 오기록은 사라졌다(P1).
  - 요구 (2) **미충족**: `window_truncated`가 `stage_deadline == stage_started + stage_budget`
    조건을 포함하므로(`:2744`), clamp된 run에서는 pre-poll ratio가 임계값을 넘어도 항상
    `exceeds=false`다. P2가 재현한다: 같은 레코드에 ratio 0.4, threshold 0.25, exceeds false.
    lap185가 요구한 "항상 일치 또는 실제 의미에 맞게 rename" 중 어느 쪽도 되지 않았다.
  - 요구 (3) **부분**: clamp 회귀 테스트
    (`tests/test_runtime_env.py:1801-1826`)는 ratio 0.2(임계값 미만)만 고정한다.
    P2의 clamp+임계값 초과 조합은 테스트에 없다.
  - 요구 (4) **충족**: `G1_INPUT_MAX_TRUNCATION_RATIO = 0.25` 불변(`:1991`),
    `UNKNOWN_BUDGET_EXHAUSTED` 우선순위 불변(P1/P2), 비-clamp 경로의 기존 판정 불변(P3/P4).
  - 영향 범위: `truncation_*`/`run_deadline_clamp*` 필드의 소비자는 `tools/runtime_env.py`와
    `tests/test_runtime_env.py` 뿐이다(전 저장소 grep). 따라서 분류/PASS·FAIL은 바뀌지 않는
    **증거 품질 결함**이다. 다만 STATUS 블로커가 "Stage B 첫 run이 실제 잘림 분포를 기록하고
    2.5초 가정을 재평가한다"고 못박은 지점이 바로 이 필드이므로 Stage B 전에 고쳐야 한다.
  - 실제 run 도달 가능성: stage budget은 각 10초이고 run `timeout`은 전체 run 예산이므로,
    입력 phase가 늦게 시작해 `run_deadline < stage_started + 10`이 되고 그 stage의 pre-poll
    작업(캡처/클릭/PNG 저장)이 2.5초를 넘으면 P2가 그대로 발생한다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(게이트 208/8 모두 통과).
  본 판정은 모델 기술 컨펌이며 사용자 마일스톤 승인이 아니다. `APPROVALS.md`는 여전히 비어 있고
  Stage B/P6/실제 게임 run은 닫혀 있다. G1 실제 원본/후보 입력 비교 증거는 여전히 없다.
- 다음 한 가지: work tier가 새 카드 A-16(아래 `loop/ESCALATE_SOL`)을 구현하고,
  이후 새 middle 세션이 독립 검수한다. 작업 tier의 자기 승인 금지.

## 재현용 독립 probe (원문 보존)

`/tmp`는 휘발성이므로 probe 본문을 여기에 보존한다. lap186 테스트를 사용하지 않는다.

```python
import sys, json
sys.path.insert(0, "/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch")
from tools import runtime_env

def probe(label, *, clock0, started, timeout, stage_budget, stage_started):
    clock = [clock0]
    real_mono, real_sleep = runtime_env.time.monotonic, runtime_env.time.sleep
    runtime_env.time.monotonic = lambda: clock[0]
    runtime_env.time.sleep = lambda s: clock.__setitem__(0, clock[0] + s)
    try:
        runtime_env._wait_state(
            lambda _d: {"tick": 1}, lambda _i: False,
            started=started, timeout=timeout, message="probe",
            stage="probe_stage", stage_budget=stage_budget, stage_started=stage_started,
        )
    except runtime_env._G1WaitTimeout as exc:
        o = exc.observation
        print(json.dumps({
            "label": label, "classification": exc.classification,
            "run_deadline_clamped": o["run_deadline_clamped"],
            "run_deadline_clamp_seconds": o["run_deadline_clamp_seconds"],
            "truncation_seconds": o["truncation_seconds"],
            "truncation_ratio": o["truncation_ratio"],
            "truncation_threshold_ratio": o["truncation_threshold_ratio"],
            "truncation_exceeds_threshold": o["truncation_exceeds_threshold"],
            "AGREES": (o["truncation_ratio"] > o["truncation_threshold_ratio"])
                      == bool(o["truncation_exceeds_threshold"]),
        }, ensure_ascii=False))
    finally:
        runtime_env.time.monotonic, runtime_env.time.sleep = real_mono, real_sleep

probe("P1_clamped_below_threshold", clock0=2.0, started=0.0, timeout=5.0,  stage_budget=10.0, stage_started=0.0)
probe("P2_clamped_above_threshold", clock0=4.0, started=0.0, timeout=6.0,  stage_budget=10.0, stage_started=0.0)
probe("P3_unclamped_above_threshold", clock0=4.0, started=0.0, timeout=30.0, stage_budget=10.0, stage_started=0.0)
probe("P4_unclamped_no_prepoll", clock0=0.0, started=0.0, timeout=30.0, stage_budget=10.0, stage_started=0.0)
probe("P5_exact_boundary", clock0=1.0, started=0.0, timeout=10.0, stage_budget=10.0, stage_started=0.0)
```

## 이번 바퀴 uncommitted 파일 해시 (커밋 없음)

- `docs/STATUS.md` `c1f4a3851b1e8741d8348bdf07511d940292af818d5a10d20d9b6924420d5a05`
- `loop/ESCALATE_SOL` `b62cf7fec4f186b03c92e30755c20129dd35cf023053e29e0edb0e195f699cce`
- `tools/runtime_env.py`, `tests/test_runtime_env.py`는 lap186 상태 그대로 변경하지 않았다.
