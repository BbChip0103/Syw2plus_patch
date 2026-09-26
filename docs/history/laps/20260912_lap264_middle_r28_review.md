# 2026-09-12 | lap 264 | 목표 G1 Stage A — R28 독립 검수 (middle tier)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high; middle(진단·계획·컨펌).
  게임 코드 hands-on 수정 없음. lap263 work(R28)의 결론을 재실행하지 않고 새 probe로 재측정했다.
- 가설 / 사용자 관찰: R28의 두 단언(비공허 집합 + `json.dump` late anchor)이 lap262 M6만이 아니라
  "review body가 existing-evidence 거부보다 먼저 실행된다"는 결함 계열 전체를 막는가.
- 예상 PASS / FAIL 조건: PASS = M0 대조군 일치, M1 개명-only 생존(오탐 0), M2/M3 R17 단독 사살,
  M6 사살이 R28에 귀속, 그리고 같은 결함 계열의 새 변이에 **생존자 0**.
  FAIL = 결함이 실재하는데 8 passed로 통과하는 변이가 하나라도 남는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): SUT/테스트 **무변경**.
  검수 전후 동일: `tests/test_review_probe_output.py`
  `df93939f87fdd86f207bb2da16f6300aa639cb1d1b857b1c3e23067b7bc218c2` (lap263 기록값과 일치),
  `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`
  `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`,
  `tools/runtime_env.py` `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`.
  신규 추가는 검수 산출물 2개뿐(아래). 모두 uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변(analysis/memory_maps 대조).
  Python 3.13.5 / pytest 9.0.2. 게임·Wine·Xvfb·PNG **0회**, 게임 fixture 없음.
  모든 변이는 `/tmp` throwaway depth-matched mirror(`docs/history/laps/probes/`, `tools/`,
  `tests/`, `pyproject.toml`)에서만 적용했다. 저장소는 읽기 전용.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python -m pytest -q tests/test_review_probe_output.py` (C0)
  - `.venv/bin/python docs/history/laps/probes/20260912_lap264_r28_review_probe.py` (C1~C4)
    probe sha256 `248c5db3129f4b433e752485cb69194343a2bb6663af4d4fc410c341d7e45a15`,
    report `docs/history/laps/probes/20260912_lap264_r28_review_report.json` sha256
    `8c6e4980f2c34b1e7465dbabc2e4c64517c430974151c174498f99e8c8d0c1dc`
  - `make check`; `LOOP_DRY_RUN=0 bash checks/safety.sh check`
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **R28 범위 승인 FAIL (커버리지). 기계 1단.**
  - **C0** 실저장소 8 passed.
  - **C1** 계약을 shipped helper를 import하지 않고 독립 재유도: 최초 top-level `__name__` If는
    1개뿐이고 123~130줄, review body는 137~426줄(262줄, 비공허), `json.dump` 보고서 write는
    412줄이며 body에 포함된다. 양성 대조(정상 run) rc 0, body 262줄 중 **205줄 실행**.
    음성 대조(거부 run) rc 2, body **0줄 실행**, 메시지 존재, 기존 증거 보존.
  - **C2** depth-matched mirror **M0 = 8 passed = 실저장소 8 passed**.
  - **C3** 변이 6종, **생존자 2종**(M1은 의도된 생존), 범위 밖 사살 0:
    - `M1` `drive_wait` 개명만 → 8 passed, 의도대로 생존(오탐 0)
    - `M2` 초기 exists() 거부만 무력화(`and False`로 분류 경로 보존) → 1 failed / 7 passed
    - `M3` M2 + 개명 → 1 failed / 7 passed
    - `M6` M2 + 최초 `__name__` If를 본문 아래로 이동(lap262 생존자) → **1 failed / 7 passed (사살)**
    - `M7` **신규**: `if __name__ ... else:` 블록(123~130) 전체를 보고서 write `try:`(410줄)
      **바로 위로 이동**. `output_refusal`은 그대로 두고 결함은 위치만으로 생긴다 →
      **8 passed, 생존**
  - **M7은 이론이 아니라 실측이다.** 거부 경로 직접 트레이스(변이 줄번호를 baseline으로 역매핑):
    rc 2, 거부 메시지 존재, 증거 보존이지만 baseline review body 262줄 중
    **198줄이 거부 이전에 실행**된다. 그런데 shipped `_review_body_lines()`는 **17줄**(비공허)을
    돌려주고 그 안에 412줄 `json.dump` anchor가 **포함**되므로 R28의 두 단언이 모두 통과하고,
    `not (body & seen)` 교집합은 비어 있어 R17이 침묵한다. 대조로 M6은 helper가 0줄을
    돌려주므로 R28 비공허 단언이 사살한다(196/262줄 실행).
  - **C4 하중**: R28 guard만 제거하면 M6/M7이 8 passed로 부활하고 M2/M3은 여전히 1 failed →
    **M6 사살은 R28 단독 귀속**이 맞다. R17 테스트만 제거하면 M2/M3/M6/M7 모두 7 passed →
    M2/M3 사살은 R17 단독이며 기존 R7/R10/R11 커버리지는 약화되지 않았다.
  - Fast: `make check` **279 passed**, Ruff 통과, compileall, mypy 10 source files,
    `CONTEXT_PASS`; 별도 `SAFETY_PASS`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: R28은 lap262가 지목한 M6 한 건은 실제로
  닫았지만(하중 귀속 확인), anchor가 여전히 **위치 기반**이라 "전처리 거부를 본문 아래로"가 아니라
  "본문 **안쪽**, 단 report write 위로" 옮기는 재구성에는 무력하다. 이는 lap254 M4, lap258 M5,
  lap262 M6와 같은 커버리지 실패 계열이다. R15/R25/R26/R27 및 R7/R10/R11은 약화되지 않았다.
  이것은 기계(1단) 반려이며 제품 G1 증거도 사용자 마일스톤 승인도 아니다.
  S1/F2-R2, R6-B-R2는 여전히 상위(Astra/사용자) 재결 대기이고 Stage B/게임/Wine/Xvfb는 금지다.
- 다음 한 가지: **R29(work tier)** — 아래 handoff. 승인 시 큐는 R20 → R21 → R22 → R23 → R24 →
  F2-R1 → F3-R1 → F3-R2 → F6-R2.

## work tier handoff (R29)

R17의 단언은 "거부 run에서 review body가 한 줄도 실행되지 않았다"이다. 현재는 body 집합을
**전처리 If의 위치**에서 유도하므로, 전처리 If를 아래로 옮기면 집합이 본문을 놓친다. R28은
"집합이 비었거나 report write를 잃었을 때"만 잡는다.

1. 본문 집합을 전처리 위치에 의존하지 않게 만든다. 예: **본문의 하한을 독립적으로 고정**한다 —
   `NEGATIVE_PATTERNS` 대입(현재 137줄)처럼 review 계산의 첫 top-level 문을 AST로 찾아
   `body_lines`가 그 줄부터 report write 줄까지를 **모두 포함**해야 한다고 단언한다. 그러면
   전처리 If를 본문 중간으로 옮겨도 집합이 줄어들 수 없다.
2. 또는 위치 대신 **관측**을 단언한다: 거부 run의 실행 줄 수가 전처리 If 이전 구간을 넘지
   않는다(예: `max(seen) <= preflight_end`)는 형태로, "얼마나 실행됐는가"를 직접 고정한다.
3. 출하 조건(측정으로 보일 것): **M7이 죽고**, M6도 계속 죽고, **M1 개명-only는 계속 생존**하며,
   M2/M3는 여전히 **R17 단독** 사살일 것. M0 대조군을 기록할 것.
4. R7/R10/R11/R15/R25/R26/R27을 약화·삭제하지 말 것. SUT(probe) 자체를 고쳐야 한다는 결론이면
   근거를 기록하고 middle로 되돌릴 것.

변이 하네스 주의(lap262에서 이어짐): `if path.exists():`를 통째로 지우면 0o600 부모의 OSError
분류까지 바뀌어 R10 테스트가 같이 죽고 귀속이 오염된다. `if path.exists() and False:`로
호출과 분류를 남긴 채 "본문이 거부보다 먼저 돈다"만 분리한다.
