# 2026-09-12 | lap 318 | 목표 G1 (M1, F1 범위 확정)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(진단·계획·확인)**.
  게임 코드·probe 구현 인계는 work(Luna 또는 Sonnet5/high). 다른 모델을 실행하거나 대행 승인하지 않았다.
- 가설 / 사용자 관찰: lap317 Astra의 F1 한정 범위와 수용표가 (i) 사실로 성립하고 (ii) work가 그대로
  구현 가능한지. 특히 "PE 직접 읽기 우선"과 "정상 접힘은 성공, 손상 수집은 fail-closed" 해석의 수용 여부.
- 예상 PASS / FAIL 조건: PASS = lap315/lap316 probe를 import하지 않고 창 753·접힘 27·두 reset 10B·gate·
  실패 arm을 재유도하고, 결정 4건과 해석 1건에 ACCEPT/REVISE를 근거와 함께 기록. FAIL = 수치 불일치,
  수용표가 구현 불가능(경계 출처 부재로 하드코딩 강제), 또는 필수 게이트 예상 밖 실패.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **전부 uncommitted**(LOOP_ALLOW_COMMITS=0).
  - `docs/history/laps/probes/20260912_lap318_middle_lap317_f1_scope_review_probe.py` `020f3fabb0503cd2a51ecd97a62286f0ac797fa4c5d9bd1ab1e16bd22a3d29b9`
  - `tests/test_lap318_middle_review_probe.py` `e97b5f30e93884e2af4381c16b8f77a8056d005be4206a77e8bba44399e2ca2d`
  - `logs/lap318/lap318_lap317_f1_scope_review.json` `f28b0e856a8d0f70b2833200cb040f72e16d50cf6a19884e8bc7ffb13263ba18`
  - `docs/work/active/G1_MIDDLE_F1_ACCEPTANCE_LAP318.md` `89359315fe8dea589c0cfe95bd9874bc5cea4adfb5da667ed83e9accbfc8866b`
  - `docs/history/laps/20260912_status_lap317_compaction.md` `65f5b2eb92cb6204715003c89e3c1fa58f14c0efa882fc410917bd5879931364`
  - `docs/STATUS.md`(갱신), 이 기록. lap313~316 산출물·pin·원본은 **무변경**.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 전후 불변. 후보 없음.
  환경 = 정적 분석만(objdump 2.42 + `struct` PE 파싱). 게임/Wine/Xvfb/Stage B/PNG/클릭 **0**,
  활성 플레이어·지도·군대·생성 fixture **해당 없음**(실행 증거 아님).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 docs/history/laps/probes/20260912_lap318_middle_lap317_f1_scope_review_probe.py` → exit 0,
  stdout SHA `f28b0e85…3263ba18`(연속 2회 동일) = 저장 report SHA.
  `.venv/bin/python -m pytest tests/test_lap318_middle_review_probe.py -q` → **14 passed**.
  `make check` → **342 passed** + Ruff/compileall/mypy/CONTEXT_PASS (`logs/lap318/make-check.log`, rc=0),
  `checks/safety.sh check` → **SAFETY_PASS** (`logs/lap318/safety.log`, rc=0). 캡처 없음.
  갱신 후 `docs/STATUS.md` = 130줄, SHA `f902d96e39fcce2d0bf31e38d03d267c41bb6c8186f38b3a4b3ac36feff1176d`.
  `loop/ESCALATE_SOL`은 요청된 middle 검수를 이번 바퀴가 수행했으므로 부록 A에 원문 보존 후 삭제했다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - 창 `0x431AB0..0x4324D6` 명령 **753** — lap316 주장과 일치 **PASS**.
  - gate `0x431AF2`=`750a`, taken `0x431AFE`; 실패 arm `0x431AF4` 연속 **10B** `5f5e5d33c05b83c434c3`
    (파일·objdump 두 출처 동일); 성공 ret `0x4324D5`=`c3` — **PASS**.
  - 창 안 접힌(>7B) 명령 **27개**, `0x4324B8`·`0x4324C2` 포함 — lap316 F1 주장과 일치 **PASS**.
  - reset 실제 바이트 `0x4324B8`=`c7051cbfe50080020000`, `0x4324C2`=`c70520bfe500e0010000`,
    주소 델타 길이 **10** 대 열 길이 **7** — lap317 수용표와 일치 **PASS**.
  - **신규:** 접힌 27행 열 바이트는 전부 파일 바이트의 **정확한 접두사**(손상 **0**) → "정상 접힘"이 이 대상에서
    검증 가능한 부류임 **PASS**. 연속줄 27개는 전부 접힌 명령 **내부 주소**이고 명령 행으로 파싱되지 않음
    (phantom row **0**) → lap315 결함은 행 발명이 아니라 **무징후 절단** **PASS**.
  - 판정: 결정1 **ACCEPT**, 결정2 **ACCEPT-WITH-REVISION**(경계 출처 미지정 → 주소 델타로 지정),
    결정3 **ACCEPT**, 결정4 **ACCEPT-AS-RECORDED**(큐 아님), fail-closed 해석 **ACCEPT**(단 현행 코드는 두
    부류를 구분 못 하므로 명령 단위 길이 불변식이 수리의 필요조건).
  - 제품 증거 **0**, runtime/Stage B **0**, S1 종결 **REJECT** 유지, G1~G4 **미완료** 유지.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  현재 수치 영향 **0**(유일한 바이트 수집인 실패 arm은 접힌 명령을 건드리지 않음 — 재확인).
  잔여 fail-open: 직접 `by_address` 조회는 접힌 명령에서 무징후 7B를 반환한다 → work가 길이 불변식으로 닫는다.
  UNKNOWN 유지: N1(실제 간접분기 0 → E1 inert), N2(call 31개 미추적), **N3 신규**(`0x432497`/`0x4324A6`이
  `ds:0xB3AC88`=`0x33F`, `ds:0xB3AC8C`=`0x1FF` 기록, 화면 전역 아님, 의미 UNKNOWN, F1 범위 밖).
  이번 판정은 middle 기술 컨펌이며 **사용자 마일스톤 승인이 아니다**. work 결과의 최종 컨펌은 다음 새 middle.
- 다음 한 가지: work(Luna 또는 Sonnet5/high)가 `G1_MIDDLE_F1_ACCEPTANCE_LAP318.md` §4 범위로
  신규 probe/test/report만 만들어 reset store 전체 바이트와 경계·연속성을 보고한다. 기존 파일·pin 무변경.

## 부록 A — lap317 `loop/ESCALATE_SOL` 원문 보존 (SHA `37cb58d7e0a0851bbd58e206d8d09d4ea2337abb7312145d983c6bb4a3a7e6e4`)

lap318 middle이 요청된 검수를 수행했으므로 이 바퀴에서 파일을 소비한다(원문은 아래 보존).

```
lap=317
role=Astra major direction/master-plan
reason=F1 수용 기준 해석 미확정; runtime/load 실행 근거 UNKNOWN 유지
handoff=docs/work/active/G1_ASTRA_F1_SCOPE_LAP317.md
Middle must independently ACCEPT/REVISE PE-direct byte collection, normal wrapped-instruction success versus damaged collection fail-closed, and unchanged E2/CFG acceptance criteria before work implementation.
Confirm actual middle model against MODEL_ROUTING and applicable session instructions; this filename is not a provider override. Do not launch or silently substitute a model from this session.
Preserve lap313-316 inputs and lap317 evidence. No game/code implementation, runtime/Stage B, milestone closure, pin rewrite, or blind retry is authorized by this handoff.
```
