# 2026-09-21 | lap 441 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  **middle(중간계획·컨펌)**. 게임 코드 hands-on 수정 없음, 게임 실행 0회.
- 가설 / 사용자 관찰: INBOX 2026-09-21 07:55 Root 회수 지시 — "다음 middle 은 W19 규칙 기반 imm
  분류의 보수성, 25개 오탐 제거/3개 실제 imm 유지, run2 실행 PASS 와 전체 check PASS 를 독립 검수한다."
- 예상 PASS / FAIL 조건: lap440 산출물을 **읽지 않고** 핀된 바이너리·현재 source 만으로 재계산해
  (a) 재빌드 SHA 일치, (b) 원본↔후보 diff 의 **추가 0 / 제거 정확히 25**, (c) 25곳 전부 원본
  바이트 복원, (d) 가드 fail-closed 와 역주입, (e) run2 원시 표본의 fault 부재가 모두 성립하면
  ACCEPT. 하나라도 어긋나면 REJECT.
- 변경 파일 / source fingerprint / 커밋: **제품 source 변경 0** (이번 회차 source 미변경 ⇒
  INBOX 2026-09-20 21:58 / N22 에 따라 통합 `make check` 생략, 표적 테스트만 수행).
  문서만 추가/갱신: 이 파일, `docs/work/active/G2_REPAIRED_CANDIDATE_P2_LONG_SOAK_LAP441.md`,
  `loop/ESCALATE_SOL` §26, `docs/STATUS.md`, `docs/feedback/INBOX.md`,
  `docs/history/laps/20260921_status_lap441_precompaction.md`. **커밋 0** (`LOOP_ALLOW_COMMITS` 미설정).
- 원본 SHA / 후보 SHA / 환경 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (**직접 재해시** 불변).
  구후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`(핀 유지, 미사용).
  신후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`.
  검수 대상 실행은 lap440 run2(Root 동기 회수, op7 resource-only / 8 owner / N=4001 / seed42).
- 실행 명령 / 로그 / 경로:
  `temp/Syw2plus_patch/g2_capacity/20260921_lap441_middle_review/recheck441.py`
  → `recheck441.json`, `candidate_new.bin`(독립 재빌드 산출물).
  검수 입력(읽기 전용): 핀된 원본, `…/20260921_lap439_middle_review/candidate.bin`,
  `…/20260921_lap440_imm_fixup_repair_run2/samples.jsonl`.
  커밋이 없으므로 이번 회차가 건드린 파일과 검수 대상 제품 모듈의 해시를
  `…/20260921_lap441_middle_review/lap441_file_hashes.sha256` 에 남겼다
  (`g2_unit_pool_expansion_v1.py` `ceef90d0…`, `g2_full_unit_capacity_v1.py` `3cfb0ac2…`,
  `runtime_driver.py` `71909440…`).

## 판정 — **W19 ACCEPT (불일치 0)**, (R1) 성립

### 1. 재빌드 결정성 — 일치

현재 source 로 `g2_full_capacity_persistence_compat_v1.build_candidate(original, 4001)` 를
다시 호출해 얻은 SHA 가 `a10024de…` 로 **정확히 일치**한다. lap440 이 주장한 신후보는
재현 가능한 빌드 산출물이며 손으로 만든 바이너리가 아니다.

### 2. 바이트 diff 전수 — 이것이 이번 검수의 본체

lap440 의 `byte_compare.md` 는 13개 사이트 **표본**만 대조했다. W19 Step 3 은
"원본↔새 후보 diff 를 **이전 후보와 비교**해 줄어든 변경이 정확히 위 목록임을 보인다"를
요구했으므로, lap441 이 전수로 다시 쟀다(연속 차이 run 단위):

| 항목 | 값 |
|---|---|
| 원본↔**구**후보 diff run | **1,415** |
| 원본↔**신**후보 diff run | **1,390** |
| 수리로 **추가된** 변경 | **0건** |
| 길이가 바뀐 변경 | **0건** |
| 수리로 **제거된** 변경 | **정확히 25건** |
| 제거된 25곳이 원본 바이트로 복원됐는가 | **전부 예** |

제거된 25개 명령 VA: `0x4010b7`, `0x4010e4`, `0x401bc2`, `0x40f051`, `0x41334e`, `0x420582`,
`0x420a5b`, `0x420cea`, `0x420db7`, `0x42152b`, `0x4720a0`, `0x4748ea`, `0x491723`, `0x49d37c`,
`0x4a3faf`, `0x4a8385`, `0x4a86f4`, `0x4a8724`, `0x4a8793`, `0x4a8801`, `0x4a886d`, `0x4a88a4`,
`0x4a88d9`, `0x4a9f8c`, `0x4a9f98`.
유지된 3개(`0x40f4b7`/`0x40f4f8`/`0x422dc2`, `mov reg, 0x66b790`)는 그대로 재배치돼 있다.
`0x421349`/`0x48f4b4`(lap398 FO-4)는 구후보에서도 재배치된 적이 없으므로 제거 목록에 없고,
신후보에서도 원본과 동일하다(추가 0 ⇒ 동일).

⇒ **"25개 오탐 제거 / 3개 실제 imm 유지"는 전수 기준으로 참이다.** 그리고 수리가 다른 무엇도
건드리지 않았다는 사실(추가 0·길이변화 0)은 lap440 이 보이지 않았던 더 강한 사실이다.

### 3. imm 전수 재스캔과 **독립 재분류** — 표의 완전성 확인, 근거 1건 정정

lap440 의 `imm_classification.json` 을 읽지 않고 `.text` 를 독립 capstone 패스로 다시 훑어
세 region 사거리 안의 imm 사이트를 **35건** 찾았다. 제품 표 `IMM_SITE_CLASSIFICATION` 은 34건이며
차이 1건은 `0x00442fac`(`mov ecx, 0x899a2a`) — `B2_EXCLUDED_VAS` 로 imm 분기 진입 전에 제외되고
자체 공식으로 패치되는 사이트다. **누락도 과잉도 없다.**

판정은 33/35 일치, **2건 근거 불일치**:

- `0x0040F4E1` / `0x0040F52F` (`cmp esi|ebx, 0x899a28`). 제품 표·lap440 = `ADDRESS`(unit_age,
  bucket 0). lap441 의 독립 규칙(루프 **초기화값**까지 확인)으로는 `init=0x008990C8`,
  `stride=2` ⇒ 이것은 **unit_existence 배열 순회의 exclusive end** 이지 unit_age 의 base 로드가
  아니다. 즉 **맞는 값에 맞지 않는 이유가 붙어 있다.**
- 결과는 다행히 같다: `layout(n)` 을 직접 계산해 **existence 배열의 새 끝 == age 의 new_start**
  가 N=1210·N=4001 양쪽에서 성립함을 확인했다(각각 `0x12b7f64`, `0x17ba59a`). 두 region 의
  `elem_size` 가 우연히 둘 다 2 라서 구조규칙의 stride 게이트도 통과한다.
- ⇒ **현재 산출물은 정확하다. 판정을 뒤집지 않는다.** 다만 근거가 우연 2개(동일 elem_size,
  레이아웃 인접)에 의존하므로 **N52** 로 등록한다(§4).

나머지 33건은 독립 판정이 제품 표와 일치했다. 특히 `0x66b7b0` 계열 8곳 중 4곳은
루프 초기화 `mov reg, 0x00669C58`(+`0x48f4b4`는 `0x00669C38`)와 `add reg, 0x8c` 를 직접 찾아
**pool 과 무관한 표의 순회**임을 역방향 추측 없이 확인했다 — lap439 의 근본원인 서술과 일치한다.

### 4. 가드의 보수성 — fail-closed 실증 (독립)

| 실험 | 결과 |
|---|---|
| 가드 정상 | `0x40F051`·`0x401BC2` 바이트가 원본과 동일 |
| `_classify_imm_operand` 를 항상 `ADDRESS` 로 강제(역주입) | `0x40F051`: `81fbb0b76600`→`81fb20c00801`(= `0x0108C020`), `0x401BC2`: `a90000800074`→`a97008220174` ⇒ **두 회귀 모두 재주입됨** |
| 표에서 `0x401BC2` 삭제 | `BuildAbortedError: unclassified imm site …` |
| 표의 `0x40F4B7` 를 `NOT_ADDRESS` 로 위조 | `BuildAbortedError: structural rule says ADDRESS, Step1 classification says NOT_ADDRESS` |
| `FO4_EXCLUDED_VAS` 잔존 여부 | **없음**(W19 Step2 ④ 이행) |

⇒ 규칙이 결정하고 표는 **동의 아니면 abort** 하는 오라클이다. VA denylist 로 되돌아가지 않았다.
보수성 방향도 옳다: 구조규칙은 `bucket == 0`(정확히 region base)만 주소로 인정하므로
`base + k*stride` 형태의 슬롯 즉치가 새로 나타나면 채택이 아니라 **abort** 한다.

**한계(정직하게):** 오라클의 독립성은 완전하지 않다. 구조규칙과 표가 **둘 다 lap440 의 같은
판독**에서 나왔으므로, 규칙이 틀린 방식으로 표와 **동의**하면 abort 가 걸리지 않는다 —
§3 의 2건이 정확히 그 사례다. 이번에는 lap441 의 외부 재분류가 그것을 잡았다.

### 5. run2 실행 증거 재계산 — fault 부재 확인

lap440 의 `run_summary.json` 을 믿지 않고 원시 `samples.jsonl` 로 다시 셌다.

- 표본 **391**건, `tick` **16 → 13,019** 단조 증가, read failure/`error` 키 **0**.
- tick **11,919** 와 **11,952** 표본이 기존 fault tick **11,928** 을 양쪽에서 감싸며
  그 뒤로도 정상 진행 ⇒ **fault 통과가 표본으로 직접 확인된다.**
- 슬롯3565 `+0x6f8`/`+0x6fc`/`+0x700` **391표본 전부 0**(nonzero 0건). 카드 조건 "≤49" 충족.
- `live` 16 → **491**.

**lap413 대조(카드 Step4 가 요구했으나 lap440 이 남기지 않은 표, 여기서 보충):**

| run | tick 11,928 부근 | 결말 |
|---|---|---|
| 구후보 `4331d9cd…` run1/run2 (lap413) | live 468, owner5 `used=1208/count=84` | **tick 11,928 page fault** `read 0x00338400 @ 0x00414133`, 2회 재현 |
| stock-layout `0a1da226…` (lap413) | tick 12,112 live 383 | tick 13,804 match 종료성 정지, fault 없음 |
| **신후보 `a10024de…` (lap440 run2)** | tick 11,919/11,952 live **478** | tick **13,019** STOP_TICK 도달, **fault 없음** |

신후보의 인구 궤적(478→491)이 stock(383→405)보다 구후보(468)에 가깝다 ⇒ 전투 전개가
비교 가능한 범위에 있다. 다만 **(a) 신후보는 1 run** 이고, **(b) STOP_TICK 13,000 은 stock
대조군이 자연 종료한 13,804 에 못 미친다.** 둘 다 이 카드의 PASS 조건은 아니었다.

### 6. 전체 `make check` / 표적 검사

- 통합 `make check` 는 Root 가 lap440 source 에 대해 이미 실행했다:
  **789 passed**(534.01s) + Ruff + compileall + mypy + `CONTEXT_PASS`
  (`…/20260921_lap440_imm_fixup_repair_run2/make_check_after_ruff_fix.log` 로 확인).
  **lap441 은 source 를 한 줄도 바꾸지 않았으므로** 재실행하지 않는다(N22 규칙 후단 미해당).
- lap441 표적 재실행: `test_g2_full_capacity_persistence_compat_v1.py`,
  `test_runtime_bridge_contract.py`, `test_g2_unit_pool_expansion_v1.py`,
  `test_g2_full_unit_capacity_v1.py`, `tests/test_g2_relocation_manifest.py`
  → **46 passed in 256.23s**(신규 회귀 3건 포함).
- `checks/safety.sh check` → **SAFETY_PASS**. 원본 **직접 재해시**
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.

### 7. 절차 관찰 (판정을 바꾸지 않음)

- **lap440 의 lap 기록이 없다**(`docs/history/laps/20260921_lap440_*.md` 부재). worker 가
  검증을 background 로 넘기고 종료해 Root 가 회수한 결과 PROMPT ⑤ 의 기록 의무가 비었다.
  아래 §8 에 산출물 기반으로 사실만 보존한다(lap440 자신의 주장이 아니라 lap441 의 재구성이다).
- lap440 이 `patches/population/runtime_driver.py` 를 함께 바꿨다. 내용은 신후보 4종의 SHA 핀
  **추가**이며 **구 핀을 지우지 않았다** — W19 §6 준수, 범위 내. 다만 같은 profile 이름 아래
  결함이 알려진 `4331d9cd…` 가 계속 허용되므로, 실행 스크립트가 SHA 를 명시하지 않으면 구후보를
  띄워도 게이트가 막지 않는다(**N53**).

## 신규 노트

- **N52 — imm 경계 판정의 근거가 우연 2개에 기대고 있다.** `_find_matching_stride_add` 는
  **스캔 중인 region 의** `elem_size` 와 비교하는데, `0x40F4E1`/`0x40F52F` 를 지키는
  `add reg, 2` 는 **다른 region(existence)** 의 stride 다. 값이 맞는 이유는
  (i) existence/age 의 `elem_size` 가 둘 다 2이고 (ii) 새 레이아웃에서 두 배열이 인접하기
  때문이다(N=1210·4001 실측). 둘 중 하나라도 깨지면 규칙이 **조용히** 틀린 값을 쓴다.
  지금 고칠 필요는 없다(산출물 정확). 레이아웃이나 elem_size 를 건드리는 카드가 나오면 먼저 본다.
- **N53 — 결함 후보의 핀이 같은 profile 이름으로 살아 있다.** `runtime_driver.SUPPORTED_EXECUTABLES`
  의 `g2_full_capacity_v1_n4001_persistence_compat` 에 `4331d9cd…`(결함)와 `a10024de…`(수리)가
  **둘 다** 등록돼 있다. 대조 보존 목적이라 제거하지 않되, 이후 실행 카드는 **후보를 재빌드해
  SHA 를 확인**하고 핀 파일을 복사해 쓰지 않는다(W20 §4 Step1 에 박음).
- **N54 — W19 Step3/Step4 의 산출물 2건이 카드보다 약했다.** Step3 "이전 후보와 비교한 diff 축소
  전량"은 표본 13건만, Step4 "lap413 stock 대조군과 나란히"는 미작성. 결론은 바뀌지 않았고
  lap441 이 둘 다 보충했다(§2·§5). W20 §4 Step3 에 대조표를 명시 요구로 넣었다.

## §8 — lap440 미기록분 보존 (산출물 기반 재구성, lap441 작성)

- 역할/모델: work(Claude Code `claude-sonnet-5`/high), 카드 W19
  `G2_IMM_FIXUP_FALSE_POSITIVE_REPAIR_LAP439.md`.
- Step1: `imm_classification.json` — region imm 34건 전수 분류, `UNRESOLVED` **0**
  ⇒ (R4) 미발동. list-region 은 값 기준 1종(`0x974fa8`) `ADDRESS`.
- Step2: `g2_unit_pool_expansion_v1.py` 에 `_classify_imm_operand`/`IMM_SITE_CLASSIFICATION`
  신설, `FO4_EXCLUDED_VAS` 제거; `g2_full_unit_capacity_v1._list_region_sites` 에 같은 가드 +
  `LIST_REGION_IMM_VALUE_CLASSIFICATION`; `collect_fixup_sites` 의 "교차검증"이 실제로는
  교차검증이 아님을 docstring 에 명시(W19 §2 ⑤ 후단 선택지).
- Step3: `rebuild_report.json`/`byte_compare.md` — `unit_pool` fixup 1,014→989(-25), 나머지 region 불변.
- Step4: run1 은 worker 가 검증을 background 로 넘겨 끊겼고, Root 가
  `…_run2/` 에서 동기 회수 — tick 13,019 도달, fault 0.
- 검사: 첫 `make check` 는 pytest 789 passed 뒤 Ruff unused import 1건으로 실패 →
  Root 가 `g2_full_unit_capacity_v1.py` 의 미사용 import 1줄 제거 → 재실행 **PASS**.
- 신규 회귀 테스트 3건(`test_0x0040f051_immediate_is_never_relocated`,
  `test_0x800000_bitmask_immediate_is_never_relocated`,
  `test_guard_disabled_reintroduces_both_regressions`). 역주입은 lap441 이 독립 재실증(§4).

## 측정값 / 판정

**W19 ACCEPT — (R1) 수리 성공.** Step3 바이트 대조 전수 일치(추가 0/제거 정확히 25/전부 원본
복원), Step4 tick 11,928 통과, 3필드 391표본 전부 0(≤49). 불일치 0, 근거 정정 2건(N52),
절차 관찰 3건(N53·N54·lap440 기록 부재).

**승격하지 않는 것:** G2 제품 완료 아님. 24k/144k 안정성·전비 5000 도달·저장/LAN·메모리 전부
미검증이며, lap409/411/412 의 왕복·soak 증거는 **구후보** 의 것이라 신후보로 재확인되지 않았다.

## 회귀 / 남은 위험 / 독립 검수 상태

- 위험1: 신후보 1 run, STOP_TICK 13,000(구 fault +1,072 tick). 장시간은 미검증.
- 위험2: 신후보 저장/로드 왕복 미재확인(구후보 증거만 존재).
- 위험3: `_region_sites` 의 **disp** 분기 bucket0 가정(창 0x758)은 imm 과 같은 계열의 잔여 노출.
  현재 런타임 반증 없음, 별도 카드 사안(W20 §7-5).
- 위험4: N52 의 우연 의존.
- 이번 회차는 게임 실행 0 ⇒ PROMPT ③ "실행 증거가 늘지 않는 회차" 카운터 **1**. 다음은 실행 회차다.

## 다음 한 가지

work(Sonnet5/high)가 `docs/work/active/G2_REPAIRED_CANDIDATE_P2_LONG_SOAK_LAP441.md`(**W20**)를
실행한다 — 수리 후보로 동일 fixture 를 `STOP_TICK=24,000` 까지 돌리고 **owner 0~7 각각의
`used`/`reserved`/`count`** 를 표본마다 남긴다. 판정식 (T1)~(T5) 는 실행 전 고정, 사후 재채점 불허.
