# W19 — **수리 카드**: 풀 재배치 fixup 의 immediate 오탐 제거

> **CLOSED (2026-09-21 lap441 middle, Opus5/high).** lap440 work 가 실행하고 lap441 이
> 비참조 재계산으로 **ACCEPT / (R1) 수리 성공** 판정했다. 근거
> `docs/history/laps/20260921_lap441_middle_g2_w19_independent_review.md`,
> `loop/ESCALATE_SOL` §26. 후속은 **W20**
> `docs/work/active/G2_REPAIRED_CANDIDATE_P2_LONG_SOAK_LAP441.md`.
> 검수 중 정정 1건(**N52** — `0x40F4E1`/`0x40F52F` 의 근거는 age base 가 아니라 existence
> 순회 end; 값은 맞아 판정 불변)과 산출물 보충 2건(**N54** — Step3 전량 diff 대조, Step4
> lap413 대조표)이 lap441 기록에 있다. 이 카드를 다시 실행하지 않는다.

- 발행자 / 역할: lap439 Claude Code `claude-opus-5` / high / **middle(검수·중간계획)**.
  근거 `docs/history/laps/20260921_lap439_middle_g2_w18_root_cause_imm_fixup.md`,
  `loop/ESCALATE_SOL` §25.
- 발행 권한: W18 카드 §5 **(M1) ⇒ 다음 카드는 수리 카드**(진단 아님). lap436 §23 준수.
- 수행 역할: **work (Sonnet5/high)**.
- 목표 연결: G2 P2. fault `0x00414133`(tick11,928)의 **근본 원인 제거**.

## 1. 선행 확정 사항 (재조사 금지)

lap439가 핀된 바이너리 두 개만으로 기계 재계산해 닫았다. 다시 재지 않는다.
재생성: `temp/Syw2plus_patch/g2_capacity/20260921_lap439_middle_review/recheck439.py`.

1. 범인 store 3곳은 **한 루프의 형제**다 — `0x0040EFC5`(`+0x6f8`) / `0x0040F002`(`+0x6fc`) /
   `0x0040F040`(`+0x700`), 전부 `mov [esi+<off>], **edx**`, 전부 **원본과 바이트 동일**.
2. `esi`는 언제나 정확한 유닛 base 다(실측 `0x016F0478` = unit3565). **주소 손상은 없다.
   값이 손상된다.** OOB/블록 write 계열 가설은 전부 닫혔다.
3. `edx`는 `0x0040EF5C` 루프의 **반복 인덱스**다(`inc edx` @ `0x0040F04A`).
4. 후보가 `0x0040F053`의 종료 즉치를 `0x0066B7B0` → `0x0108C020`으로 바꿨다
   (delta `0xA20870` = pool 재배치). 표 시작 `0x00669C58`은 불변.
   ⇒ 반복 **50회 → 75,900회**, `edx` 최대 **49 → 75,899**.
5. 실측 오염값 `16538`/`22432`는 원본 사거리(≤49) **밖**, 후보 사거리 **안**.
   `17`은 정상 값이다(watchpoint 가 잡은 첫 전이는 정상 동작이었다).
6. `0x0040EE00`~`0x0040F070` 구간의 원본↔후보 diff 는 **그 4바이트뿐**이다.

## 2. 결함의 위치 (코드)

`patches/population/g2_unit_pool_expansion_v1.py::_region_sites` (L180–226)

- **disp 분기는 안전하다** — base/index 레지스터 없으면 abort(L210–214),
  버킷0 이탈(`disp - base >= elem_size`)이면 abort(L215–220).
- **imm 분기(L222–225)에는 가드가 없다.** `base <= value < old_end` 이면 무조건 채택한다.
  docstring L196–199의 전제 *"an imm **is** the final literal address of one specific slot"* 이
  **거짓**이다 — 즉치는 비트마스크·루프 경계값·패킹 상수일 수 있다.
- 유일한 방어 `FO4_EXCLUDED_VAS = {0x00421349, 0x0048F4B4}`(L97–99)는 lap398이 손으로 찾은
  **"즉치 == POOL_BASE 인 cmp 2곳"** 이다. 규칙이 아니라 VA denylist 라서
  `POOL_BASE + 0x20`(`0x0066B7B0`)을 놓쳤다.

후보 `4331d9cd…` 빌드 사슬:
`runtime_driver` → `g2_full_capacity_persistence_compat_v1` → `g2_full_capacity_persistence_v1`
→ `g2_full_capacity_supply5000_owner1200_v1` → `g2_full_unit_capacity_supply5000_v1`
→ `g2_full_unit_capacity_v1.build_candidate`.

`g2_full_unit_capacity_v1.py`
- `_list_region_sites` (L104–129): **imm 분기 L120–122에 같은 결함**. 실제 사이트 생산자.
- `collect_fixup_sites` L145: 교차검증용으로 위 모듈의 `_region_sites`를 import 해 부른다
  ⇒ **두 스캐너가 같은 실수를 하므로 교차검증이 성립하지 않는다.** 이것도 수리 대상이다.

## 3. 오탐의 규모 (lap439 실측, `unit_pool` imm 28건 전수)

28건 **전부** `+0xA20870` 적용됨. 값별:

| 원본 즉치 | 건수 | lap439 판정 | 디스어셈블 증거 |
|---|---|---|---|
| `0x0066B790` | 3 | **정당해 보임**(진짜 pool base) | `0x40F4B7`, `0x40F4F8`, `0x422DC2` |
| `0x0066B7B0` | **8** | **오탐 확정**(50항목 표 end bound) | `cmp ebx,…`(`0x40F051`, 런타임 실증), `cmp edx,…`(`0x420582`), `cmp eax,…`(`0x4A3FAF`) |
| `0x00800000` | **11** | **오탐 확정**(비트 23 마스크) | `test eax,0x800000`(`0x401BC2`), `test esi,0x800000`(`0x4A8385`) |
| `0x00870087`, `0x00878700` | 2 | **오탐 확정**(push 상수) | `push`(`0x4A9F8C`, `0x4A9F98`) |
| `0x00800807`, `0x00801007`, `0x00800010` | 3 | **오탐 강력 의심** | 미분류 |
| `0x0067F6F8` | 1 | **미분류** | `push 0x67f6f8`(`0x491723`) |

`0x0066B7B0` 8곳 전체 VA:
`0x0040F051`, `0x0041334E`, `0x00420582`, `0x00420A5B`, `0x00420CEA`, `0x00420DB7`,
`0x0042152B`, `0x004A3FAF`.

`0x00800000` 11곳 전체 VA:
`0x00401BC2`, `0x004720A0`, `0x004748EA`, `0x004A8385`, `0x004A86F4`, `0x004A8724`,
`0x004A8793`, `0x004A8801`, `0x004A886D`, `0x004A88A4`, `0x004A88D9`.

`unit_existence` imm 2건(`0x40F4BC`/`0x40F4FD`, `0x008990C8`)·`unit_age` imm 2건
(`0x40F4E1`/`0x40F52F`, `0x00899A28`)은 배열 base 자체이고 성장 보정 delta 를 썼다 —
**이번 수리에서 건드리지 않되 §4 Step 1의 분류 대상에는 포함**한다.

## 4. 실행 순서

### Step 1 — 분류 (정적, 손으로 추측 금지)

imm 32건 **전부**를 핀된 원본에서 **정방향** 디스어셈블해 다음 표를 만든다.
산출: `imm_classification.json` — 각 항목에 `va / mnemonic / operand / verdict / 근거 1줄`.

`verdict`는 셋 중 하나다:
- `ADDRESS` — 즉치가 실제로 풀 내부 주소로 **역참조되거나** 주소로 전달된다.
- `NOT_ADDRESS` — 비트연산 피연산자(`test`/`and`/`or`/`xor`), 루프/범위 경계 비교(`cmp`),
  또는 주소로 쓰이지 않는 상수.
- `UNRESOLVED` — 위 둘 중 어느 쪽인지 **정적으로 단정할 수 없다**.

`UNRESOLVED`가 1건이라도 남으면 **빌드는 abort** 한다(§5 (R4)). 추측으로 분류하지 않는다.

### Step 2 — 규칙 기반 가드 구현 (VA denylist 금지)

`_region_sites`의 imm 분기와 `_list_region_sites`의 imm 분기 **양쪽**에 같은 규칙을 넣는다.
최소 요구:

1. **명령 종류 게이트.** `test`/`and`/`or`/`xor`/`cmp`/`push` 처럼 즉치가 주소로 역참조되지
   않는 명령의 즉치는 **자동 채택하지 않는다.** 채택하려면 `ADDRESS` 분류가 명시돼야 한다.
2. **슬롯 정렬 게이트.** `ADDRESS` 후보는 `(value - base) % elem_size` 가 실제 존재하는
   필드 오프셋이어야 하고 `(value - base) // elem_size < STOCK_CAPACITY` 여야 한다.
   (참고: `0x0066B7B0`은 slot0/field `0x20`이라 이 게이트만으로는 안 걸린다 —
   그래서 게이트 1이 **필수**다. 게이트 2 단독으로 끝내지 않는다.)
3. **분류 대조.** 최종 적용 목록은 Step 1의 `imm_classification.json` 과 **정확히 일치**
   해야 한다. 불일치 시 `BuildAbortedError`.
4. `FO4_EXCLUDED_VAS` 는 규칙이 흡수하므로 **denylist 로 남기지 않는다.**
   제거하되 그 2개 VA가 새 규칙으로도 배제되는지 테스트로 고정한다.
5. `g2_full_unit_capacity_v1.collect_fixup_sites` L145의 교차검증이 **독립**이 되도록
   고친다(같은 함수를 부르는 한 무의미하다). 독립화가 어려우면 교차검증이 아님을 명시하고
   Step 1 분류표를 진짜 교차검증으로 세운다.

**주의: 상수를 손으로 4바이트 패치하지 않는다.** 결함은 스캐너에 있다. 후보는 스캐너를 고친
뒤 **재빌드**해서 얻는다. `0x0040F053`만 되돌리는 것은 나머지 오탐 24건을 남기므로 금지다.

### Step 3 — 재빌드와 바이트 대조

같은 파라미터(N=4001, compat)로 후보를 재빌드하고 **새 SHA를 기록**한다.
- `0x0040F053` = `cmp ebx,0x0066B7B0` (원본과 동일) 확인.
- `0x0066B7B0` 8곳·`0x00800000` 11곳·`push` 상수 3곳이 **전부 원본과 동일**함을 확인.
- `0x0066B790` 3곳은 `0x0108C000`으로 재배치돼 **있어야** 한다.
- 원본↔새 후보 diff 를 **이전 후보와 비교**해 "줄어든 변경"이 정확히 위 목록임을 보인다.

### Step 4 — 실행 재검증 (이 카드의 PASS 조건)

lap413 P2와 **동일 fixture**(op7 resource-only / 8 owner / N=4001 / seed42, 격리 사본 +
전용 prefix + 빈 display)로 새 후보를 실행한다.

- tick **11,928 을 fault 없이 통과**해야 한다. `STOP_TICK` 은 **13,000**.
- 슬롯3565 의 `+0x6f8/+0x6fc/+0x700` 을 기존 probe 방식으로 관측해 **전부 ≤49** 임을 기록한다.
- lap413 stock 대조군 수치와 나란히 남긴다.

## 5. 판정식 (실행 **전** 고정 — 사후 재채점 불허, 갈래 서로소)

- **(R1) 수리 성공.** Step 3 바이트 대조 전부 일치 + Step 4에서 tick 11,928 통과 +
  3필드 전부 ≤49. ⇒ **P2 재실행(장시간/원본 생산 경로)으로 진행**, 다음 카드는 middle 독립검수.
- **(R2) 부분 성공.** Step 3은 통과했으나 Step 4에서 **다른 tick/다른 주소**의 새 fault 가
  난다. ⇒ 그 fault 는 **별개 결함**이다. 수치와 함께 보고하고 **STOP**. 그 자리에서 새 진단을
  이어붙이지 않는다(§1 계보의 반복 금지).
- **(R3) 수리 실패.** Step 4에서 **같은** tick 11,928 / `0x00414133` fault 가 재현된다.
  ⇒ lap439의 귀속이 틀렸거나 불완전하다. 재시도 없이 보고하고 **strategy 판정**으로 올린다.
- **(R4) 분류 미결.** Step 1에서 `UNRESOLVED`가 남는다. ⇒ 빌드하지 말고 그 목록과 근거를
  보고하고 **STOP**. 추측 분류로 넘어가지 않는다.
- **(R5) 기술 불가.** 재빌드 불가/환경 문제. ⇒ 사유를 정확히 적고 `BLOCKED`.

## 6. 대상 고정 (변경 금지)

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (읽기 전용).
- 기존 후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`
  (대조용 보존 — **핀을 지우지 않는다**. 새 후보는 새 핀으로 추가한다).
- image base `0x400000`, `va - 0x400000 = 파일 오프셋`.
- 게임 코드 직접 패치 금지: `0x00414133` / `0x0043ee39` / `0x00422dc7` / `0x0040bc86~0x40bcfe` /
  `0x0040c1c2` / `0x48cba9` / `0x48c914` / `0x411ec0` / `0x413103` / `0x413120` /
  **`0x0040efc5` / `0x0040f002` / `0x0040f040`**(이번에 무죄로 확정됨).

## 7. 안전

- 원본 실행/수정 금지, **직접 재해시**로 전후 불변 확인. `checks/safety.sh check` → `SAFETY_PASS`.
- 새 격리 전체 게임 복사본 / 전용 prefix / 빈 display(비중첩 번호). 전역 `pkill` 금지.
- **셸 background 금지.** 모델 세션이 동기로 기다린다(INBOX 2026-09-21 01:01).
  "background 실행 중" 문구로 활성 프로세스를 주장하지 않는다.
- PID 발견은 lap434 `movement_state_probe_pm.py`의 **검증된 방식**을 재사용한다
  (INBOX 2026-09-21 00:51 정정 — 새 PID 추측 금지).
- 실행 전 `df -h /` 확인(lap429 선례). 대용량 스냅샷 금지.
- baseline·핀·golden 을 고쳐 통과시키지 않는다. 자기 결과를 자기가 최종 승인하지 않는다.
- 커밋은 `LOOP_ALLOW_COMMITS=1` 없이는 하지 않는다. 기본 0 ⇒ uncommitted + 파일 해시로 남긴다.

## 8. 예산과 중단 조건

- Step 1~3(정적·빌드) + Step 4(실행 1회 + 재시도 1회). 총 **90분**.
- Step 4는 **반드시 게임을 실행한다.** 실행 불가 사유가 곧 (R5).
- 즉석 가설 추가·감시 확대·다른 슬롯 추가 금지. 결과는 (R1)~(R5) 중 하나로만 간다.
- 포인터 손상/저장 이상/원본 변조가 보이면 숨기지 말고 수치와 함께 보고하고 멈춘다.

## 9. 검사

- **source 를 바꾸므로** 통합 경계에서 `make check` 를 **한 번** 실행한다
  (INBOX 2026-09-20 21:58 규칙 후단 / N22 — 면제 주장 금지).
- 표적: `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` (기준선 6 passed) +
  `patches/population/test_g2_unit_pool_expansion_v1.py` + `tests/test_g2_relocation_manifest.py`.
- **회귀 테스트 신규 필수 2건**(카드 PASS 조건):
  1. `0x0040F053`의 즉치가 재배치되지 **않음**을 고정하는 테스트.
  2. `test eax, 0x800000` 계열(`0x00401BC2` 등)의 즉치가 재배치되지 **않음**을 고정하는 테스트.
  둘 다 **역주입**(가드를 끄면 실패)을 확인한다(lap408 W6 선례).
- 매회 `checks/safety.sh check` → `SAFETY_PASS`, 원본 **직접 재해시** 불변.
- `docs/history/laps/`에 LAP_TEMPLATE 필드로 기록, `docs/STATUS.md` 갱신(130줄 이하).

## 10. 산출물

`temp/Syw2plus_patch/g2_capacity/<날짜>_lap<N>_imm_fixup_repair/`
- `imm_classification.json` (Step 1 전수 분류 + 근거)
- `rebuild_report.json` (새 후보 SHA, 적용/비적용 사이트, 이전 후보 대비 diff 축소 목록)
- `byte_compare.md` (Step 3 대조표)
- `run_summary.json` + probe 산출물 (Step 4, 판정 (R1)~(R5))

## 11. 범위 밖

- strict cap 정책 / 전비 장부 32bit(F4 · 사용자 되물음 2건) — 사용자 답변 대기.
- LAN, G1, G4, G3(중단). G1/G4는 INBOX 2026-09-21 00:20 지시로 G2 성립 전까지 잠정 중단.
- W10~W18 재론(§1이 확정 목록이다).
- **disp 사이트 986건** — 버킷0 가드가 이미 막고 있다. 이번 수리는 **imm 만** 건드린다.
- 저장/LAN 호환 재검증 — (R1) 이후 별도 카드.
