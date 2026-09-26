# lap339 middle — lap338 보존 정책 검수와 결합 probe 영향표 (보완 봉투)

2026-09-12 / lap339 / Claude Code `claude-opus-5` / high / middle(진단·계획·확인).
상위 문서: `G1_R1_PROVENANCE_DIRECTION_LAP338.md`(Astra 결정 초안),
`G1_CANDIDATE_R1_MIDDLE_REPAIR_SCOPE_LAP337.md`(R-a/R-b 범위),
`G1_CANDIDATE_R1_MIDDLE_ENVELOPE_LAP334.md`(후보 R1 봉투).
**이 문서는 제품 승인·마일스톤 종료·후보 실행 허가가 아니다. 실행 예산 0회 유지.**
게임 코드/하네스/테스트 수정 0. 이번 바퀴의 쓰기는 문서·기록·probe뿐이다.

## 1. 이번 바퀴가 독립 재현한 것

probe `docs/history/laps/probes/20260912_lap339_middle_lap338_provenance_policy_probe.py`
(`761aec2f…2f8018b`) rc0, stdout SHA256 `3b74cfe20c87a43a82d658e1362352b812a5b48602aa9c91a1975d047c7ad759`
— 연속 2회 + 두 인터프리터(`python3`, `.venv/bin/python`) byte-identical, Ruff PASS.

| 항목 | 결과 |
|---|---|
| `make check` | rc0, **376 passed(58.33s)**, Ruff/compileall/mypy OK, `CONTEXT_PASS` |
| `checks/safety.sh check` | `SAFETY_PASS` |
| 입력 소스 기준선 | `tools/runtime_env.py=922a267c…f8a2575`, `tests/test_lap326_r1_load_origin.py=c04a6265…d769823` — lap338 §3이 적은 값과 **일치**(lap338은 소스를 바꾸지 않았다) |
| lap337 probe 재현 | rc0, stdout `c38a73f1…8cdf46` 2회 동일 |
| lap336 probe 재현 | rc0, stdout `9295dfdf…d1593a0f` |
| N13 | 대상 테스트 **15 passed** 재확인(lap335 기록의 16은 부정확) |
| R-a | 후보 세 이름의 `tests/` 출현 **0/0/0** 재확인 |
| R-b | AST로 후보 `candidate_ps9`=`stage_started=launch_started`, 원본 `r1_ps9`=`stage_started=started` — **비대칭 확인** |
| STATUS 보존 | lap337 압축본 body **130줄**·`512abde1…8cd5a6` 독립 재계산 일치, 헤더 선언값과도 일치 |

**이번 바퀴가 자기 probe에서 잡은 결함(전이 단언 재발, 수치 영향 0):** 초안 probe는 STATUS가
**특정 압축본 파일명**(`…status_lap337_compaction.md`)을 명시하는지 단언했다. STATUS를 lap338 압축본으로
갱신하자 그 단언이 즉시 FAIL했다 — 바로 이 봉투가 금지하는 **전이 단언**이고 W3·lap332/334와 같은 형태다.
이름이 아니라 **연결 자체**(STATUS가 가리키는 압축본이 존재하고 헤더 SHA/줄 수가 자기 body와 일치)를
단언하도록 고쳤다. 최종 probe는 rc0이며 이 사례를 §7 N14와 함께 "계약을 손으로 재구현할 때의 비용"으로 남긴다.

**lap338의 STATUS 편집 감사(diff 전량):** 바뀐 구역은 `## 다음 한 가지`(4→3줄)와 `## 바퀴 기록`(5→5줄)
**둘뿐**이고, `## 지금 막힌 것 (Blockers)`와 `## 검증 상태`는 **byte-identical**이다. 삭제된 lap326~337
바퀴 기록 줄은 lap337 압축본 body에 **원문 그대로** 남아 있고 STATUS가 그 파일명을 명시한다.
⇒ **미결·반려 삭제 0건.** 현재 STATUS는 **129줄**, 다섯 표제 각 1개(`CONTEXT_PASS`).

## 2. lap338 §2~4 판정

### 2.1 §2.1 재pin 불허 — **ACCEPT**

lap337의 실패 분해를 이번 바퀴가 직접 재실행해 재현했다:
`…lap332…probe.py` rc1 / failures = {live harness SHA, live R1 test SHA} **2건**,
`…lap334…probe.py` rc1 / failures = {runtime_env.py drifted from the lap330-reviewed harness SHA} **1건**.
세 실패 전부 **살아 있는 소스 SHA 단언**이고, 두 probe는 `check()`가 예외를 던지지 않고 누적하는
구조라 나머지 단언(artifact exact-once, 표본 12건, `pending` 0→34, 사다리 35엔트리, 130줄 대조 등)은
**지금도 산출·통과**한다. 두 probe의 lap330 pin(`997ff15b…`, `81acc11e…`)은 **그대로 존재**한다(재pin 0).

**분류를 안전하게 만드는 새 근거(이번 바퀴 추가):** 현재 **필수 게이트 어느 것도 과거 probe를 실행하지
않는다.** `Makefile`의 `check`는 `pytest`(testpaths=`["patches","tests"]`) + `ruff/compileall`(대상
`patches tools tests checks`) + `mypy`(명시 파일) + `checks/context_limits.py`이고, `checks/safety.sh`도
`checks/safety.py`만 부른다. probe가 `gates_referencing_history_probes: []`로 기계 확인했다.
⇒ 두 stale probe의 영구 rc1은 **필수 게이트를 깨지도, 가리지도 않는다.** "역사적 검수 전용" 분류는
검증 의무를 제거하는 것이 아니라 **이미 게이트 밖에 있던 사실을 명시하는 것**이다. W3는 별도 미결 유지.

### 2.2 §2.2 편집 전 원문 보존 — **ACCEPT, 단 아래 5개 구체화가 필수**

정책 자체는 옳다. 다만 초안대로 두면 work가 해석할 여지가 남아 §3/§4로 못 박는다.

1. **대상은 "이번 봉투가 편집을 허가한 파일"뿐이다.** 결합된 전체 집합을 뜨지 않는다.
   `tools/runtime_env.py`는 248,099 B이므로 lap마다 전량 복사하면 이력이 비대해진다.
2. **manifest는 `historical_identity: UNKNOWN`과 `covers_execution: false`를 명시**해야 한다.
   이 스냅샷은 **lap339 이후 비교용**이며 lap330/331 실행 원문이 **아니다**. 라벨을 바꾸는 순간
   Astra가 금지한 "과거 실행 소스 역추정 인증"이 된다.
3. **스냅샷은 실행·import 대상이 아니다.** `docs/` 는 pytest testpaths·lint 대상 밖이므로
   `.py` 원본 바이트를 그대로 두어도 게이트에 편입되지 않는다(§2.1 근거와 동일). `__pycache__` 생성 금지.
4. **덮어쓰기 금지·경로 고정:** `docs/history/laps/snapshots/lap<N>_pre_edit/`, 기존 lap 디렉터리 불변.
5. **실행 직전 재대조:** 스냅샷 SHA가 아니라 **편집 후 살아 있는 소스 SHA**를 middle 승인 묶음과
   다시 대조한다(§5의 필수 명령).

### 2.3 §2.3 결합 probe 영향표 — **ACCEPT, 산출물은 아래 §3**

§3이 편집 대상별로 과거 probe·가변 소스 SHA 단언·불변 artifact 단언·현행 계약 단언을 분리한다.
과거 identity는 UNKNOWN으로 남기고 PASS와 합치지 않는다.

### 2.4 §3 PASS 조건 대조

| lap338 §3 PASS 조건 | 판정 | 근거 |
|---|---|---|
| 기존 pin 변경 0 | PASS | 두 stale probe의 lap330 pin 존재, 파일 SHA 기록(§3) |
| 모든 실패 단언의 적용 범위 명시 | PASS | §3 영향표 |
| 과거 identity UNKNOWN 보존 | PASS | §3 D행, §4 manifest 필수 필드 |
| 현재 계약 검사 누락 0 | **FAIL(1건, N14)** | §7 — 130줄 계약에 대응하는 기계 게이트가 **없다** |
| 편집 전 원문 복원 가능성의 바이트/SHA 확인 절차 | PASS | §4·§5 |
| 실행 예산 0 | PASS | 이번 바퀴 실행/입력/메모리 접근/PNG/후보 artifact 0 |

N14는 R-a/R-b 수리를 막지 않는다(서로 다른 파일·서로 다른 계약). §7에서 별도 카드로 승격한다.

## 3. 결합 probe 영향표 (lap338 §2.3 필수 산출물)

편집 대상: **(E1)** `tools/runtime_env.py` — R-b 인자 한 곳.
**(E2)** `tests/test_lap326_r1_load_origin.py` — R-a/R-b 오프라인 잠금.

| # | 결합 probe/검사 | 단언 종류 | 현재 | E1/E2 편집 후 예상 | 처리 |
|---|---|---|---|---|---|
| A | `…lap332…artifact_probe.py` (`e8dc8c75…a1f9c367`) | **가변 소스 SHA**(harness, test) ×2 | rc1 | rc1 유지(메시지 동일) | **편집 금지·재pin 금지.** 역사적 검수 전용, 필수 게이트 밖 |
| B | 〃 나머지 단언(artifact exact-once·표본 12건·`pending` 0→34·사다리 35) | **불변 artifact** | 통과 | 통과 | 그대로 유효. rc1이 이 PASS들을 무효화하지 않는다 |
| C | `…lap334…envelope_probe.py` (`698993b8…a55f7e2c`) | **가변 소스 SHA** ×1 | rc1 | rc1 유지 | A와 동일 |
| D | lap331 run의 "검수 SHA == 실행 SHA" | **과거 identity** | 복구 불가(원문 없음) | 복구 불가 | **UNKNOWN 영구 보존.** PASS로 승격 금지 |
| E | `…lap336…implementation_probe.py` (`2e1481b8…505f8e25d`) | 현행 계약(살아 있는 SHA 미단언) | rc0 | **rc0 유지 필수** | work가 재실행해 rc0·stdout `9295dfdf…d1593a0f` 확인 |
| F | `…lap337…repair_scope_probe.py` (`1dd47cd3…c545`) | 현행 계약 | rc0 | **rc0 유지 필수**, stdout은 R-b 수리로 **변할 수 있다** | rc0만 필수. stdout SHA 변화는 결함이 아니라 수리 반영 |
| G | `…lap339…provenance_policy_probe.py` (`761aec2f…2f8018b`) | 현행 계약 | rc0 | **rc0 유지 필수**, stdout 변함 | F와 동일 |
| H | `make check` / `checks/safety.sh check` | 현행 필수 게이트 | 376 passed / SAFETY_PASS | **377~379 passed 예상** | 정확한 수를 기록(N13 재발 금지) |

**A·C를 통과시키려는 어떤 편집도 금지다.** 새 현재 계약 검사는 E/F/G와 `tests/`에만 추가한다.
A~D의 UNKNOWN/FAIL을 E~H의 PASS와 종합 exit0으로 합치지 않는다.

## 4. 스냅샷 요건과 work 파일 목록

편집 **전에** 다음을 만든다. 기존 경로를 덮어쓰지 않는다.

```
docs/history/laps/snapshots/lap<N>_pre_edit/
  manifest.json
  tools/runtime_env.py                    (편집 전 바이트 그대로)
  tests/test_lap326_r1_load_origin.py     (편집 전 바이트 그대로)
```

`manifest.json` 필수 필드(하나라도 빠지면 FAIL):
`lap`, `role`, `collected_at`(KST), `reviewing_document`(이 파일 경로),
`scope`("R-a/R-b repair only"), `historical_identity`: `"UNKNOWN"`,
`covers_execution`: `false`, 그리고 파일별 `{relative_path, sha256, bytes}`.
대상은 **소스 텍스트만**. EXE/DLL/게임 데이터/save/자격 증명/PNG는 제외(`.gitignore`와 AGENTS 불변 규칙).
`patches/resolution/dxwrapper_config.py`는 **편집 대상이 아니므로 스냅샷 대상도 아니다**(pin 불변).

수집 시점 기대값(이번 바퀴 실측):
`tools/runtime_env.py` = `922a267c27f51fe47d7db69962dadbfdbbded9ff04c6350e8cb7a4c44f8a2575`, 248099 B.
`tests/test_lap326_r1_load_origin.py` = `c04a6265229f7e37cb9d4434f0e150c76e1e56d26f0e1c990cb938a06d769823`, 9367 B.
**둘 중 하나라도 다르면 편집하지 말고 중단한다**(누군가 사이에 소스를 바꿨다는 뜻).

## 5. 필수 명령과 실패 분류

순서대로 실행하고 **전량**을 기록한다(exit0을 승인으로 쓰지 않는다).

1. `sha256sum tools/runtime_env.py tests/test_lap326_r1_load_origin.py` → §4 기대값과 대조.
2. 스냅샷 + `manifest.json` 생성 → `sha256sum` 재계산으로 **바이트 동일** 확인.
3. R-b 편집(인자 한 곳) → R-a/R-b 오프라인 잠금 추가.
4. `make check`(정확한 테스트 수), `checks/safety.sh check`,
   `.venv/bin/python -m pytest tests/test_lap326_r1_load_origin.py -q`(정확한 수).
5. 영향표 E·F·G probe 재실행 → **셋 다 rc0**(F·G의 stdout SHA 변화는 정상, 값을 기록).
6. A·C는 **재실행해 rc1과 실패 메시지를 기록만** 한다. 고치지 않는다.
7. `sha256sum` 편집 후 소스 → 기록(다음 middle의 검수 기준선).

**실패 분류(어느 것이든 발생하면 그 자리에서 보존·중단, 재시도 금지):**

- `SOURCE_DRIFT` — 1번이 §4 기대값과 다르다 ⇒ 편집 금지, `loop/ESCALATE_SOL` 반환.
- `SNAPSHOT_MISMATCH` — 2번 재계산이 원본과 다르다 ⇒ 스냅샷 폐기 후 재수집 1회, 또 다르면 중단.
- `GATE_REGRESSION` — 4번의 `make check`/safety가 실패하거나 테스트 수가 **감소** ⇒ 수리 철회 후 보존.
- `CONTRACT_PROBE_BROKEN` — 5번의 E/F/G 중 rc≠0 ⇒ 수리가 현행 계약을 깼다. probe를 고치지 말고 수리를 고친다.
- `SCOPE_CREEP` — 허용 파일 밖 변경, 새 의존성, 새 공통 추상화, A/C 편집 ⇒ 즉시 중단.
- `STAGE_BUDGET_EXHAUSTED` — **향후 후보 run에서만** 발생 가능. R-b 수리로 40초가 설치 구간을 포함하게
  되므로 설치가 느리면 PS9가 예산 안에 안 들어올 수 있다. 이는 **정당한 FAIL**이며 예산 확대·재시도로
  대응하지 않는다. 설치 비용/여유는 **실측 전 UNKNOWN**이고 lap337의 "예산 압박 없음" 추론을
  실행 증거로 쓰지 않는다(lap338 §4 유지).

## 6. work handoff (Luna/Sonnet5 high, 실행 0회)

`G1_CANDIDATE_R1_MIDDLE_REPAIR_SCOPE_LAP337.md` §5를 **그대로 유지**하되 앞에 §4 스냅샷을 선행시키고
§5의 명령/분류를 적용한다. 허용 파일은 §3의 E1·E2 **둘뿐**이다.
R-b는 `g1_r1_candidate_load_origin`의 `stage="candidate_ps9"` `_wait_state` 호출에서
`stage_started=launch_started` → `stage_started=started` **한 곳**. 이 수리는 lap334 §8의
"준비/PS9 40초" 문언과 원본 `r1_ps9`(=`started`)와의 대칭을 **동시에** 만족한다(§1 표의 AST 근거).
R-a는 오프라인 이름 분리 단언 추가, 프로덕션 코드 변경 0.
**자기 결과를 자기가 승인하지 않는다.** 기록은 `docs/history/LAP_TEMPLATE.md` 형식.
후보 1 run은 수리 + **다음 새 middle의 독립 재검수** 뒤에만 발효한다. 지금은 0회.

## 7. 새 발견 N14 — 130줄 계약에 기계 게이트가 없다 (승격)

`checks/context_limits.py`의 `CAPS["docs/STATUS.md"]`는 **180**이다. `loop/PROMPT.md`가 요구하는
**130줄**을 검사하는 필수 게이트는 **존재하지 않는다.** 그래서 각 바퀴가 130줄 검사를 **손으로 다시
구현**하고, lap323·lap333·lap338이 그 손수 검사의 FAIL로 바퀴를 소모했다(lap338은 131줄).

- lap338이 만난 "131>130 FAIL"은 **저장소의 필수 게이트가 아니라 자신이 쓴 사전 assert**였다.
  같은 초안으로 `make check`를 돌렸다면 `CONTEXT_PASS`였다. lap338의 중단 자체는 근거를 전부 보존했고
  아무 것도 소비하지 않았으므로 **절차상 문제는 아니다.** 문제는 계약이 기계화되지 않은 것이다.
- **제안(승인 필요, 이번 바퀴에서 실행하지 않음):** `CAPS["docs/STATUS.md"]`를 130으로 좁혀
  `make check`가 계약을 직접 강제한다. 이것은 게이트를 **조이는** 변경이라 "검사를 고쳐 통과시키기"의
  반대지만, 검사 파일을 바꾸는 일이므로 middle 단독으로 착수하지 않는다.
- **R-a/R-b와 묶지 않는다**(한 바퀴 한 가지, 다른 파일·다른 계약). 별도 카드로 Astra/사용자 판정 대기.

## 8. 금지 (유지, 변경 없음)

W3 재pin, A/C probe 편집, 기대 SHA/건수 자동 수정, 원본 n>1, 재클릭, 예산 확대, Stage B, PNG,
baseline/golden/안전 pin 갱신, ptrace/int3/winedbg/gdb, 새 의존성, G2~G4 확대, WM_CLOSE/P6 착수,
커밋(`LOOP_ALLOW_COMMITS=0`). 마일스톤 종료/이동·제품 승인 0.
