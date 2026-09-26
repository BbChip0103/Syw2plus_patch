# 2026-09-12 | lap 266 | 목표 G1 Stage A — R29 독립 검수 (middle tier)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high; middle tier
  (진단·계획·컨펌). 게임 코드/SUT/출하 테스트 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap265 work의 R29(`_review_body_lines()`를 첫 top-level
  `NEGATIVE_PATTERNS` 대입 ~ AST로 찾은 `json.dump` 구간으로 재고정)가 lap264 M7 생존자를
  실제로 사살하는지, 그 사살이 R29에 귀속되는지, 기존 회귀를 약화하지 않는지 독립 확인한다.
  추가 가설: R17→R19→R28→R29는 모두 **이동 가능한 두 앵커 사이의 줄 구간**으로 본문을
  유도하므로, 앵커를 옮기는 새 변이가 매 바퀴 생존한다(lap262 M6, lap264 M7).
- 예상 PASS / FAIL 조건: PASS = M0 대조군 유지, M7/M6/M2/M3 사살, M1 개명-only만 생존,
  사살이 R29에 귀속, 기존 회귀 비약화, 새 생존자 0. FAIL = 같은 결함 계열의 새 생존자 존재.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 출하 코드/테스트 **무변경**.
  검수 산출물만 신규 추가(uncommitted):
  `docs/history/laps/probes/20260912_lap266_r29_review_probe.py`,
  `..._lap266_r29_review_report.json`,
  `..._lap266_r30_feasibility_probe.py`, `..._lap266_r30_feasibility_report.json`,
  `..._lap266_r30b_feasibility_probe.py`, `..._lap266_r30b_feasibility_report.json`,
  본 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`.
  검수 전후 지문 동일, lap265 기록값과 일치:
  `tests/test_review_probe_output.py` `59538c0e1778b9c09ff6e83207123a89229f3001d351a873af2b194e72ec8957`,
  SUT `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`
  `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`,
  `tools/runtime_env.py` `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 무변경. Python 3.13.5,
  pytest 9.0.2. 게임 fixture/활성 플레이어/지도/군대 없음. 모든 변이는 depth-matched `/tmp`
  throwaway mirror에서만 실행했고 저장소에는 변이를 쓰지 않았다. 게임/Wine/Xvfb/PNG 0회.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - C0 `.venv/bin/python -m pytest -q tests/test_review_probe_output.py` → `8 passed`.
  - C1~C4 `.venv/bin/python docs/history/laps/probes/20260912_lap266_r29_review_probe.py`
    → `..._lap266_r29_review_report.json`.
  - R30 후보 계약 타당성: `..._lap266_r30_feasibility_probe.py`(변이 A),
    `..._lap266_r30b_feasibility_probe.py`(변이 B) → 각 report JSON.
  - `make check` (exit 0), `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **FAIL (커버리지, 기계 1단)**.
  - **C0**: 실저장소 targeted `8 passed`.
  - **C1 계약 독립 재유도**(출하 helper를 import하지 않음): preflight If 1개 123~130,
    `NEGATIVE_PATTERNS` 대입 1개 137, `json.dump` Expr 1개 412 → helper body `[137,412]` 276줄.
    R28의 본문(전처리 아래 전 top-level, 131~426)보다 **413~426을 제외**하지만 그 구간에는
    거부 경로 밖 executable review 문이 없어 사살력 손실은 관측되지 않았다.
    대조 controls: 정상 run rc 0 · helper body 201줄 실행; 거부 run rc 2 · helper body
    **0줄** 실행 · 거부 메시지 존재 · 증거 보존 → R17 단언은 baseline에서 공허하지 않다.
  - **C2 미러 대조군**: depth-matched `/tmp` 미러 M0 `8 passed` = 실저장소 8.
  - **C3 변이 7종**: M1 개명-only `8 passed`(의도 생존, 오탐 0),
    M2/M3/M6/**M7** 각 `1 failed / 7 passed` → **R29는 lap264 M7을 실제로 사살한다**.
    **신규 M8(decoy anchor)** `8 passed` — **생존**.
  - **M8 결함 직접 트레이스**: M8은 M7(전처리 블록을 report write 바로 위로 이동)에
    `NEGATIVE_PATTERNS`를 `NEG_PATTERNS_SRC`로 개명하고 report write 직전에 별칭
    `NEGATIVE_PATTERNS = NEG_PATTERNS_SRC`를 두는 무해 refactor를 합성한 것이다. 거부 run은
    rc 2·거부 메시지·증거 보존이지만 **module-level review 문 171/231줄이 거부 전에 실행**된다
    (동일 척도의 baseline 거부 run은 15줄뿐이고, 그 15줄은 전처리보다 앞선 정상 설정문이다).
    출하 helper의 body는 **5줄**로 줄며 그중 **0줄**만 실행되어 `assert not (body & seen)`이
    다시 공허해진다. 개명 성분은 M1이 무해로 확정한 변환이므로 M8은 "무해 refactor ∘ 기존 결함"
    합성이고, R29의 사살이 refactor에 견디지 못한다는 뜻이다.
  - **C4 하중 귀속**: `with_R28_anchor`(R29의 앵커만 R28 방식으로 되돌림) → **M7 `8 passed`로
    부활**, M2/M3/M6은 계속 사살 ⇒ M7 사살은 R29의 **앵커 변경**에 귀속된다.
    `without_R29_assert`(주석+`assert review_start < report_write_line`만 제거) → M2/M3/M6/M7
    모두 계속 사살 ⇒ **R29의 단언 자체는 현재 행렬에서 하중이 0**이다(앵커 변경만 하중).
    lap265 work 기록의 C4는 guard만 제거했으므로 귀속 주장이 불완전했다.
    `without_R17_test` → 5종 모두 `7 passed` ⇒ 사살자는 여전히 R17 단독이고 다른 테스트가
    하중을 대신 지지 않는다. R7/R10/R11 및 R15/R25/R26/R27 약화 없음.
  - **회귀 전체**: `make check` `279 passed`, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`,
    `SAFETY_PASS`.
  - **R30 후보 계약 타당성(다음 work을 위한 계획 증거)**: 변이 A(구조적 "import/def/docstring/
    preflight를 뺀 모든 top-level 문")는 **M0 대조군이 `1 failed`** — 전처리보다 먼저 실행되는
    14개 모듈 설정문 15줄(ROOT/SOURCE/COUNT_ADDR/DEFAULT_OUTPUT …)을 포함해 오탐이므로 기각.
    변이 B(**named review result 대입의 합집합** + 모든 `json.dump` 줄, 이름 완전성 단언)는
    M0 `8 passed`, M1 생존, **M2/M3/M6/M7/M8 전부 `1 failed / 7 passed`**, 생존자 `[M1]`.
    합집합은 단조라서 전처리 이동으로 줄지 않고 decoy 대입은 줄을 더할 뿐이라 **이동/decoy
    계열 전체를 닫는다**. `next()`로 **첫 일치**를 앵커로 쓰는 것이 lap262~266 회귀의 공통 원인이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: R29는 lap264 M7을 닫았고 오탐·회귀를
  만들지 않았으므로 **되돌릴 필요는 없다**. 그러나 같은 결함 계열이 M8로 열려 있어 R17 커버리지
  계약은 아직 건전하지 않다 → **범위 승인 보류(FAIL)**. 이것은 기계 1단 판정이며 제품 G1 증거나
  사용자 마일스톤 승인이 아니다. S1/F2-R2와 R6-B-R2는 상위 재결 대기이고 Stage B/게임 실행은
  금지 상태를 유지한다.
  **상위 재결로 올릴 항목(Astra/사용자)**: lap262·264·266 3연속으로 lap228 역사 probe에 대한
  *테스트의 테스트* 강화에 바퀴를 쓰고 있고 G1~G4 제품 증거는 0이다. R30으로 이 계열을 한 번에
  닫은 뒤에도 R20~R24/F2-R1/F3-R1/F3-R2/F6-R2 offline 큐가 남는다. Stage B가 S1/F2-R2로 막힌
  동안 이 큐를 계속 소진할지, 아니면 S1 결정성 재결을 먼저 올릴지는 상위 역할의 판단이다.
- 다음 한 가지: **R30 (work tier)** — `_review_body_lines()`를 변이 B 계약으로 교체한다.
  출하 조건: M0 `8 passed`, M1 생존, M2/M3/M6/M7/**M8** 사살, 생존자 `[M1]`,
  R17 단독 하중 유지, `make check` 279 passed. 승인되면 큐는 R20 → R21 → R22 → R23 → R24 →
  F2-R1 → F3-R1 → F3-R2 → F6-R2.


## 산출물 SHA256 (uncommitted, LOOP_ALLOW_COMMITS=0)

- `docs/history/laps/probes/20260912_lap266_r29_review_probe.py` `55648ebd6b8cb153ce47b3db1ab982d96ef43cf91ebb84c1ed4edad1943d4b95`
- `docs/history/laps/probes/20260912_lap266_r29_review_report.json` `df45e4596ca229df32ecd0ba6aa7366fd587d0e8ae35d55706032cb9b5f88212`
- `docs/history/laps/probes/20260912_lap266_r30_feasibility_probe.py` `ac26578c52c61beaea1261df3d9feb9b8da3bad955f0d7589e618f3fb98b1972`
- `docs/history/laps/probes/20260912_lap266_r30_feasibility_report.json` `21d4eacae7f922709513b5cc8945a2d5e48433ac1fdd198005fff4511f5953cc`
- `docs/history/laps/probes/20260912_lap266_r30b_feasibility_probe.py` `5da857a7d7969802299d9bb75232e0e4eae81a4f1050c5dfd730ea34884ca8ca`
- `docs/history/laps/probes/20260912_lap266_r30b_feasibility_report.json` `3b69345a7e058be288ec2a4451cf70e54a083d80e67e6bc178cdf564a061074a`
- `docs/history/laps/20260912_status_lap266_compaction.md` `02ebd9338cf53530513b68074a0f1a81334141fa9ce1b8351b8b17dea9f0ae0b`
- `docs/STATUS.md` `cf80d21fd7493e04b41a8b10f2ab8d8c5e6d12d9d446eeba83d2be1f55e6ce22`

본 기록 파일 자신과 `loop/ESCALATE_SOL`, 위 handoff 문서는 이 목록 뒤에 갱신되므로
해시를 싣지 않는다. 커밋 허용이 없어 모든 산출물은 uncommitted로 보존한다.
