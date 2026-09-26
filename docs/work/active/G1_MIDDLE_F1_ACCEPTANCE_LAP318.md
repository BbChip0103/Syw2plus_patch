# lap318 middle — lap317 Astra F1 범위의 독립 검수와 work 인계

상태: middle 독립 검수 **ACCEPT-WITH-REVISION**. 계획 승인이지 제품 검증/마일스톤 종료가 아니다.
실제 역할/모델: Claude Code `claude-opus-5` (middle, effort=high). 게임 코드·EXE·DLL·assets 변경 0.
입력: `docs/work/active/G1_ASTRA_F1_SCOPE_LAP317.md`, lap315/lap316 산출물, 원본 PE.
산출: probe `docs/history/laps/probes/20260912_lap318_middle_lap317_f1_scope_review_probe.py`
(`020f3fab…2a3d29b9`), report `logs/lap318/lap318_lap317_f1_scope_review.json`(`f28b0e85…3263ba18`,
stdout SHA와 동일, 연속 2회 byte-identical), test `tests/test_lap318_middle_review_probe.py`.

## 0. 독립 재유도 (lap315/lap316 probe를 import하지 않음)

원본 SHA `b56986e0…c9c08a8ac` 불변. 입력 6개 산출물 SHA는 `logs/lap317/before_sha256.json`과 전부 일치.
PE 헤더를 `struct`로 직접 걸어 imagebase `0x400000`, `.text` VA `0x401000`/raw `0x1000`/rsz `0xE4000`을 얻고,
값은 **파일**에서, 명령 경계는 **디스어셈블리 주소 열**에서 따로 얻어 교차 확인했다.

| 재유도 항목 | 값 | lap316/lap317 주장과 |
|---|---|---|
| 창 `0x431AB0..0x4324D6` 명령 수 | 753 | 일치 |
| gate `0x431AF2` 바이트 / taken | `750a` / `0x431AFE` | 일치 |
| 실패 arm `0x431AF4` 연속 10B | `5f5e5d33c05b83c434c3` (파일·열 두 출처 동일) | 일치 |
| 성공 ret `0x4324D5` | `c3` | 일치 |
| 창 안 접힌(7B 초과) 명령 | **27개**, `0x4324B8`·`0x4324C2` 포함 | 일치 |
| `0x4324B8` / `0x4324C2` 실제 바이트 | `c7051cbfe50080020000` / `c70520bfe500e0010000` | 수용표와 일치 |
| 두 reset의 주소 델타 길이 / 열 길이 | 10 / **7** | F1 전제 성립 |

추가로 **새로 측정한 두 사실**(lap316이 적지 않았다):
- 접힌 27행의 열 바이트는 전부 파일 바이트의 **정확한 접두사**이고 손상 0건이다 → "정상 접힘"은 이 대상에서
  **정의 가능하고 검증 가능한 부류**다(추측이 아니다).
- 접힘 연속줄 27개는 전부 접힌 명령 **내부 주소**이며 명령 행으로 파싱되지 않는다(phantom row 0건).
  즉 lap315의 결함은 **행 발명이 아니라 무징후 절단**이다.

## 1. 결정별 판정

| lap317 결정 | 판정 | 근거·조건 |
|---|---|---|
| 1. M1/G1 유지, 다음 실무 변경을 F1로 한정, 같은 R2 수치 재증명 금지 | **ACCEPT** | R2는 lap314·lap316 2회 독립 ACCEPT. 네 번째 CFG 방식은 제품 진척 0 |
| 2. F1 목적=reset store 전체 바이트·연속성 보고, PE 직접 읽기 우선, 줄 너비와 바이트 출처 분리 | **ACCEPT-WITH-REVISION** (§2) | 목적·우선순위 수용. 단 "PE 직접"만으로는 **명령 경계 정보가 0**이라 경계 출처를 명시해야 한다 |
| 3. lap313~316 산출물/pin 보존, 새 probe와 별도 회귀 테스트만, N1·N2는 UNKNOWN 유지 | **ACCEPT** | 이번 lap도 기존 파일 무변경으로 재현했다(§0) |
| 4. F1 종료 후 runtime 계약 미제출 봉투를 문서 검토로 되돌린다(미래 분기) | **ACCEPT-AS-RECORDED** | 큐 아님. 현재 큐는 STATUS만. 실행/Stage B/runtime 예산 0 유지 |
| 해석: lap316 fail-closed = **손상·불완전 수집** 거부이지 정상 접힘 거부가 아니다 | **ACCEPT** (§3) | 정상 접힘 27건이 전부 접두사 손상 0으로 확인돼 두 부류가 실제로 구분된다 |

## 2. REVISE — 경계 출처를 명시한다 (결정 2)

lap317은 "raw 10B만 읽어 성공 처리하면 불충분"이라고 옳게 적었지만, 그 대안인 명령 경계 검사의 **출처를
지정하지 않았다**. 파일만 읽으면 길이 10은 기대값 하드코딩이 되고, 이는 같은 표의 거부 조건에 걸린다.
middle이 지정하는 최소 방법(이번 probe가 실제로 수행해 하한을 증명했다):

- **값**: 원본 PE에서 VA→raw로 읽는다. 섹션 raw 범위를 벗어나거나 부분 읽기면 `None`으로 거부한다.
- **경계**: 디스어셈블리 **주소 열의 다음 명령 행 주소 − 현재 주소**로 길이를 구한다. 접힘 연속줄은 니모닉이
  없어 명령 행이 아니므로 이 델타는 접혀도 옳다(`0x4324C2 − 0x4324B8 = 10`).
- **교차 조건**: 파일에서 읽은 길이와 델타가 같고, 열 바이트가 파일 바이트의 접두사여야 한다.
  이 세 조건이 맞을 때만 "전체 바이트"로 보고한다. 어긋나면 FAIL이고 값을 채우지 않는다.
- 대안으로 objdump 연속줄 재조립을 택하려면, 재조립 결과가 위 델타·파일 바이트와 일치함을 함께 보여야 한다.
  lap317의 "구체 부적합 근거가 있을 때만"은 그대로 유효하다.

## 3. 해석 확정 — 정상 접힘 대 손상 수집

lap315 현행 코드에서 두 부류는 **구분되지 않는다**. 직접 조회(`by_address`)는 무징후 7B를 돌려주고(fail-open),
다중 명령 수집(`collect_contiguous_bytes`)만 주소 gap으로 FAIL한다(fail-closed). 그래서 해석을 수용하되
수리는 **명령 단위 길이 불변식**(열 바이트 수 == 주소 델타)을 넣어야 성립한다. 이 불변식 하나가 접힌 27행을
전부 잡고, 정상 접힘은 파일 바이트로 복구 가능해지며, 손상은 여전히 FAIL로 남는다.
현재 수치 영향은 0이다(유일한 바이트 수집인 실패 arm은 접힌 명령을 건드리지 않음 — §0에서 재확인).

## 4. work 인계 (Luna 또는 Sonnet5, effort=high) — 파일 범위와 수용 기준

**만들 것(신규 2개):** `docs/history/laps/probes/20260912_lap319_work_v7_reset_store_bytes_probe.py`,
`tests/test_lap319_reset_store_bytes_probe.py`, 보고서 `logs/lap319/…json`.
**건드리지 말 것:** lap313~316 probe/test/report, 기존 pin, `tools/`·`patches/`·baseline/golden, 원본 EXE.

| 항목 | 수용 조건 | 거부/중단 |
|---|---|---|
| reset 바이트 | `0x4324B8`=`c7051cbfe50080020000`, `0x4324C2`=`c70520bfe500e0010000`; 주소·길이 10·출처(파일)·경계(주소 델타)·연속성을 각각 보고 | 부분 읽기, 길이 하드코딩, 경계 출처 미기재 |
| 기존 불변식 | 753/753/7/724, unresolved 0, writer 4, 실패 arm writer 0, gate/실패 arm E2 유지 | 수치 변동 자동 재pin, 기대값 완화 |
| 정상 fixture | 합성 listing **과** 실제 대상 두 곳에서 접힌 10B가 전체 바이트로 성공해야 한다. 실제 대상에서 행사되지 않는 수리는 lap316 N1과 같은 inert 수리다 | 합성 fixture만으로 "접힘을 처리했다" 선언 |
| 부정 fixture | 최소 5종을 손으로 답을 유도 가능한 예제로: (a) 연속줄 누락 → 짧은 읽기, (b) 길이 신호 없는 절단, (c) 주소 gap, (d) overlap(다음 주소 < 시작+길이), (e) 섹션 raw 범위 밖 읽기. 전부 명시적 FAIL | 상수끼리 비교, 저장 report만 대조 |
| 검증 | targeted 회귀 + `make check` + `checks/safety.sh check`, 입력 SHA 전후 불변, 2회 실행 stdout byte-identical | 예상 밖 필수 실패 시 재시도/마감 금지 → 변경 보존 + `ESCALATE_SOL` |

최종 기술 컨펌은 **다음 새 middle**이 바이트·경계를 독립 재유도해서 한다. work는 자기 결과를 승인하지 않는다.

## 5. 보류·UNKNOWN (이번 수리에 포함하지 않는다)

- **N1**(실제 간접분기 0 → E1 수리 inert), **N2**(창 안 call 31개 미추적, cross-function 순서 UNKNOWN) 유지.
- **N3(lap318 신규, 수치 영향 0):** 접힌 27행 중 `0x432497`·`0x4324A6`은 성공 꼬리에서 `ds:0xB3AC88`=`0x33F`,
  `ds:0xB3AC8C`=`0x1FF`를 쓴다. 화면 전역(`0xE5BF1C/20`)이 아니며 의미 **UNKNOWN**이다. F1 범위 밖이고
  화면 writer 수(직접 4)를 바꾸지 않는다. 필요하면 별도 좁은 probe로만 다룬다.
- W3 stale pin은 역사 실패로 보존하고 F1 검증에 편입하지 않는다(lap317과 동일). 재pin은 Astra/사용자 결정.
- runtime/load 봉투, map↔dialog 순서, 실제 좌표, Stage B/Wine/Xvfb/게임/PNG/클릭 예산 0. S1 종결 REJECT,
  G1~G4 미완료 유지. exit0/Fast PASS는 제품 완료가 아니다.
