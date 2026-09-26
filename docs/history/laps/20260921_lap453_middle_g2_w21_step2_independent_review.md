# 2026-09-21 | lap 453 | 목표 G2 (W21 Step2 독립검수 + 카드 CLOSED 판정)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high — **middle(중간계획·컨펌)**.
  게임 코드 hands-on 수정 없음, 게임 실행 **0회**.
- 가설 / 사용자 관찰: lap452(work)가 W21 Step2 저장/로드 왕복을 실행해 **(U5) PASS를 자기판정**으로
  냈다. STATUS 「다음 한 가지」가 지시한 대로 ①원시 산출물 비참조 재계산으로 독립 검수하고,
  ②ACCEPT면 **W21 카드 CLOSED** 여부를 판정하며, ③다음 단계(144k 발행 조건)는 경계이므로
  strategy로 올린다.
- 예상 PASS / FAIL 조건: 카드 §1 **(U5)** 를 실행 전 고정된 문구 그대로 적용한다 —
  "저장 전후 owner별 `(count, used, reserved)` 와 슬롯 단위 `(slot, internal_id, type, owner)`
  **소실 0 · 불일치 0**". 재채점·완화 없음. 추가로 카드 §6-4의 **tick 역행 증거**가 원시 파일에서
  직접 재도출되지 않으면 "소실 0"을 "로드가 아무 일도 안 함"과 구분할 수 없으므로 FAIL로 본다.

## 변경 파일 / source fingerprint / 커밋

- **제품/도구 source 변경 0.** `patches/`, `tools/`, `tests/`, `docs/work/active/*.md` 무변경.
  (`docs/work/active/G2_CAP_PROXIMITY_SEEDED_SOAK_LAP445.md` mtime 09:51:26은 lap452 run 시작
  10:11:34보다 **앞서므로** lap452의 사후 편집이 아니다. lap452 자체 기록도 같은 취지로 적고 있다.)
- 이번 회차가 만든 파일은 전부 git 비추적 `temp/` 아래다:
  `temp/Syw2plus_patch/g2_capacity/20260921_lap453_middle_review/recheck453.py`(비참조 재계산기),
  `.../recheck453.json`(산출물).
- 문서 갱신: 이 기록 + `docs/STATUS.md` + `loop/ESCALATE_SOL` §32.
- 커밋 **0**(`LOOP_ALLOW_COMMITS=0`).

## 판정 입력에서 뺀 것 (비참조 원칙)

`run_summary.json`, `step2_orchestrator.log`의 서술, lap452 lap 기록 본문은 **판정 입력으로 쓰지
않았다**. 재계산기가 읽은 것은 `presave_snapshot.json` / `preload_snapshot.json` /
`postload_snapshot.json` / `trace.jsonl` / `seed_receipts.json` / `resource_receipts.json`,
그리고 `run.stdout` 중 **브리지가 돌려준 원시 응답 줄**(`save_result=` / `load_result=` /
`save file=`)뿐이다. 판정을 세운 뒤에 한해 `run_summary.json`을 열어 불일치 유무만 대조했다
(lap451이 N69를 찾은 방식과 같다).

## 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / fixture

- 원본 EXE **직접 재해시**: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  — 핀 값과 일치, 불변.
- 후보: `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
  (lap452 run.stdout: "rebuilding … from current source" 뒤 재빌드 SHA 일치 ⇒ **N53 준수**,
  핀 복사 아님). 진단 DLL `dll_sha256=41839d97…`(capacity 4001), `bridge_sha256=9881388d…`
  — N62대로 둘을 구분해 적는다.
- 활성 플레이어: PS3 진입 시 `ai` 플래그 **8/8 = 1** ⇒ **N59(신후보 기준 (U0) 재확인) 이행됨**.
  owner0 포함 8인 전원이 이번 신후보에서도 활성이다.
- fixture: N=4001, seed42, map 100×100, owner당 disjoint 앵커
  `[(2,2),(27,2),(52,2),(77,2),(2,52),(27,52),(52,52),(77,52)]`, 자원 op7×8, 시딩 op5/op6만.
  **op4(장부 직접 write) 사용 0건** — 카드 §0-2 준수를 receipt 전수로 확인했다.

## 실행 명령 / 산출물

- `python3 temp/Syw2plus_patch/g2_capacity/20260921_lap453_middle_review/recheck453.py`
- 검사: `python3 -m pytest tests/test_g2_eight_owner_setup.py -q` → **6 passed**,
  `bash checks/safety.sh check` → **SAFETY_PASS**, 원본 직접 재해시 불변.
  이번 회차 **source 변경 0**이므로 N22에 따라 통합 `make check`는 생략했다.

## 측정값 / 판정

### 1. (U5) 슬롯 전수 대조 — **PASS (재계산 불일치 0)**

- presave 1,161 슬롯 vs postload 1,161 슬롯: **lost 0 · mismatched 0 · new 0**.
  `(slot, internal_id, type, owner)` 4-튜플 전수 비교이며 `internal_id` 1,161개가 **전부 고유**하다.
- 두 스냅샷의 **텍스트 차이는 `"tick": 45 → 48` 단 한 줄**이다(파일 해시는 서로 다름:
  presave `b06c6919…`, postload `4d517219…` ⇒ 복사본이 아니라 각각 새로 읽은 것).
- owner 장부 `(count, used, reserved)` **8/8 완전 일치**:
  owner0 `(146, 4935, 0)`, owner1~7 각 `(145, 4900, 0)`.
- **스캔 범위에 사각 없음:** 리더가 `EXISTENCE_BASE`에서 `CAPACITY×2 = 4001×2` 바이트를 읽어
  슬롯 **0~4000 전수**를 순회한다(`w21_step2_run.py:195-196`). 따라서 lost/new 판정이 풀 일부만
  본 결과가 아니다.

### 2. 로드가 실제로 상태를 교체했는가 — **PASS(원시 파일에서 직접 재도출)**

- `trace.jsonl` 자체에 **tick 역행이 1회, 정확히 한 지점**에 있다:
  record46 `wait_after_save tick=1524` → record47 `postload tick=48`. 그 외 두 창
  (`wait_after_save` 45표본 47→1524, `post_load_window` 30표본 48→1022)은 각각 **단조 비감소**다.
- 브리지 op3 **단일 호출의 원시 응답**(`run.stdout` load_result): `tick_before=1557`,
  `tick_after=46`, `before={used 4965, count 149, reserved 10}`,
  `after={used 4935, count 146, reserved 0}`. 같은 브리지가 op2에서는
  `tick_before=46, tick_after=46`을 돌려주므로, 두 필드는 **호출 내부에서 읽힌 값**이다.
  ⇒ STATUS의 "단일 load 호출 자체에서 tick 역행" 서술은 원시 응답으로 뒷받침된다.
- 상태 교체의 독립 증거: preload(tick1557, live1186)에 있던 **25기가 로드 후 사라졌고**
  (postload에만 있는 유닛은 0기), 8 owner **전원**의 장부가 preload `(147~149, 4920~4965, 10)`
  → postload `(145~146, 4900~4935, 0)`로 되돌아갔다. "로드가 아무 일도 안 함"은 배제된다.
- 저장 파일도 직접 확인했다: `save092.dat`, 3,944,402 B,
  SHA `76680017eb8f9e695036ab6629d9b7de8ca74520549ab77f3a66f6f13b8553e1`,
  **오프셋 `0x38`의 8바이트를 직접 읽어 `S2P1N4K1`** 임을 재확인(로그 문구 인용 아님).

### 3. 부수 재계산 (전부 일치)

- `live == Σ owner.count`: `sum_count`가 있는 **75표본 전부 일치, 불일치 0**.
- 라이브 `used > cap(5000)` 표본 **0건**. `used+reserved > 5000` 표본도 **0건**
  (이번 창은 `reserved`가 대부분 0 또는 10이고 `used ≤ 4965`라 N68 상황에 닿지 않았다).
- 시딩 receipt 전수: op5 ×8(`fixture_added` 합 1,104) + op6 ×8(합 40), **실패 receipt 0**,
  앵커 8개 서로 다름, 카드 §5 함정1의 op5 `wanted=1` 스모크가 시딩 **전에** `ok=true`.

### 4. **신규 N75 — 장부·인벤토리·receipt 3자 산술이 오차 0으로 닫힌다** (긍정)

raw receipt → raw 스냅샷 인벤토리 → raw 장부가 슬랙 없이 맞는다:

- 유닛 수: 초기 16(8 owner × 2) + op5 1,104 + op6 40 + 스모크 op5 1 = **1,161** = `live` = Σcount.
- 타입 분포(presave 실측): `{type5: 1,105, type7: 48, type49: 8}` = 1,161.
- 전비: 초기 16기 × 10 = 160, type5 1,105 × 35 = 38,675, 시딩 type7 40 × 10 = 400
  ⇒ 합 **39,235** = 실측 Σ`used` (4,935 + 4,900×7) **정확히 일치**.
- owner0만 `count`가 1 많은 이유도 이 산술이 설명한다 — **스모크 op5 1기**가 owner0에 갔다.
⇒ owner 장부가 슬롯 인벤토리와 독립적으로 표류하는 카운터가 아니며, 이번 상태가 **gate-legal
op5/op6만으로** 만들어졌음이 파일 수준에서 닫힌다.

### 5. **신규 N74 — post-load 1,000tick 동역학이 pre-load 창과 완전히 동일** (긍정, 단 해석 주의)

`post_load_window` 30표본의 `live` 시계열이 `wait_after_save` 첫 30표본의 `live` 시계열과
**30/30 완전히 동일**하고(1161,1161,1161,1161,1163,…,1180), tick은 +1~+2만 어긋난다.
⇒ 복원된 상태는 관측 필드가 같을 뿐 아니라 **약 1,000 tick 앞으로의 진행까지 재현**한다.
**해석 주의:** 이 게임이 상태+seed에 대해 결정적으로 보이므로 이것은 상태 동일성의 *확증*이지
독립 축이 아니다. 그러나 "스냅샷 필드만 같고 내부 상태는 깨졌다"는 갈래를 크게 좁힌다.

### 6. (U4) — 이번 run은 **새 정보 0**, lap448의 UNKNOWN 그대로

카드 §11-3이 요구한 `smaps_rollup` 필드(`private_clean_kb`/`private_dirty_kb`/`referenced_kb`)는
**실제로 표본에 들어와 있다**(75표본 전부). 그러나 이번 60초 창에는 **1MB 이상 RSS 하강이 0건**
(RSS 239,356~246,056 KB), `vm_size` 단일값 3,463,800 KB, `vm_swap` 전 표본 **0**, PID 단일
(3578071)이다. ⇒ lap448의 3건(−65,760 KB) UNKNOWN은 **여전히 UNKNOWN**이고, 계측만 준비됐다.
STATUS의 서술과 일치하며 과대 주장 없음.

### 7. 신규 결함·관찰 (판정은 뒤집지 않음)

- **N71 (계측 라벨 위험, N55/N66과 같은 계열).** `run_summary.json`의
  `post_load_window_verdict = "CAP_PROXIMITY_STABLE"` 은 `w21_step2_run.py:648-652`에서
  **`u1_pass=True`를 하드코딩**하고 `u2`를 **30초/1,022 tick 창**으로 계산해 얻은 값이다.
  카드의 공식 (U2)는 `STOP_TICK ≥ 24,000`을 요구하므로 **같은 문자열이지만 다른 것**이다.
  stdout 한 줄에는 단서가 붙어 있으나 **JSON 필드에는 없다** ⇒ 나중 lap이 이 필드를 24k 결과로
  인용할 위험이 있다. 재사용 시 필드명을 바꾸거나 `window_ticks`/`not_card_u2`를 함께 적을 것.
  (이번 ACCEPT는 이 필드를 쓰지 않는다.)
- **N72 (판정식-코드 간극, 이번 run 무영향).** 실행기의 `U5_pass`는
  `lost==0 ∧ mismatched==0 ∧ owner_ledger_mismatch==0`만 보고 **`new_after_load`는 보고만 하고
  게이트하지 않는다**(`w21_step2_run.py:613-614`). 카드 §1 (U5)가 "소실 0·불일치 0"만 요구하므로
  카드 위반은 아니고 이번 run은 new=0이라 무영향이지만, 재사용 시 new>0이어도 PASS가 찍힌다.
- **N73 (대조 경계가 카드 §6-3의 "같은 표본 경계"와 정확히 같지는 않다).** presave는 **tick 45**,
  save 실행은 브리지 응답 기준 **tick 46**, postload는 **tick 48**(복원 tick 46 + 2)이다.
  따라서 "저장 1 tick 전" vs "로드 2 tick 후"를 비교한 것이고, **정확히 tick 46에 태어나 세이브에
  들어갔다가 로드에서 사라진 유닛**은 양쪽 모두에 없어 이 대조로는 보이지 않는다. 이번 창은
  live가 tick 47~148 내내 1,161로 정지해 있어 위험이 실현되지 않았지만, 재사용 시에는
  op2 응답의 `tick_after` 직후에 presave 스냅샷을 찍는 편이 낫다.
- **N76 (N67 재확인, 이번 run 수치).** 비용 기준 단일 type 비중은
  38,675 / 39,235 = **98.57%** (type5)다. 2계층 요구(카드 §3)는 형식상 충족이나 "혼합 구성"은
  이 숫자와 함께만 쓴다. **건물 계층은 여전히 없다**(카드 §0-3이 (가)의 몫으로 명시).
- **관찰(결함 아님).** `run_summary.cmdline`이 `/bin/sh -e /usr/bin/wine syw2plus_original.exe`라
  형태만 보면 lap415/416의 런처 PID 혼동과 닮았다. 그러나 같은 PID에서 PS/존재배열/유닛 필드
  read가 전부 성공하고 값이 게임 진행에 따라 변했으므로 **게임 이미지를 담은 프로세스가 맞다**
  (카드 §5-3과 같은 근거). cmdline 문자열만으로 PID 정당성을 주장하지 말 것.

### 8. 종합 — **(U5) ACCEPT** 그리고 **W21 카드 CLOSED**

| 판정식 | 상태 | 근거(검수 lap) |
|---|---|---|
| (U0) | PASS | lap446 실행 / lap447 ACCEPT + 이번 신후보에서 `ai` 8/8 재확인(N59) |
| (U1) | PASS 8/8 | lap448 실행 / lap449 ACCEPT + 이번 run 자체 시딩도 4,900~4,935 |
| (U2) | PASS | lap448 tick 24,029 / lap449 ACCEPT |
| (U3) | PASS | lap449 ACCEPT(712표본) + 이번 75표본 불일치 0 |
| (U4) | **PARTIAL(UNKNOWN 잔존)** | 카드 §1이 "FAIL로 세지 않되 해명됐다고 쓰지 않는다"로 규정 |
| (U5) | **PASS** | **이번 lap453 비참조 재계산, 불일치 0** |
| §7 Step3 | 충족 | lap450 발행 / lap451 ACCEPT, N66 CLOSED. 두 사본 SHA `f733d46e…d8e3d0` **직접 재해시 동일** |

⇒ 카드의 모든 Step이 실행됐고, **각 Step을 실행자와 다른 middle이 독립 검수**했다.
(U4)만 규정대로 PARTIAL이며 이는 CLOSED를 막지 않는다. **W21 카드 CLOSED로 판정한다.**

**CLOSED가 뜻하지 않는 것(카드 §9 그대로):** G2 제품 완료 아님. 얻은 것은
**"cap 근접(4,900~5,000) 상태에서 24k tick 안정 + 저장/로드 1왕복 무손실"** 이라는 **부분 증거**다.
미검증: (가) 원본 생산 경로 자연 도달 · 144k · LAN/지원 동기화 · 건물 포함 구성 ·
전투/사망/재생산 순환.

**부수로 이번 검수가 새로 굳힌 것:** 왕복이 보존한 1,161기는 **전부 슬롯 2,840~4,000**,
즉 **100%가 stock 천장 1200 이상**이다. 재배치 풀의 개체가 저장/로드를 넘어 살아남는다는
직접 증거이며, 2026-09-20 00:33 사용자 지시의 "slot 1200 이상" 축을 **신후보 + 저장 지속성**까지
확장한다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 회귀 0. 원본 불변, 커밋 0, 게임 실행 0회, 제품 코드 변경 0.
- 남은 위험은 위 N71~N73·N76과 (U4) UNKNOWN이며 **전부 계측/서술 측 위험**이지 제품 결함 근거가
  아니다. 어느 것도 (U5) 판정을 뒤집지 않는다.
- 사용자 마일스톤 승인은 **없다**. 카드 CLOSED는 모델의 기술 컨펌이며 제품 승인이 아니다.

## 다음 한 가지

**strategy(Astra 또는 Fable) 판정이 먼저다 — 이번 middle은 여기서 멈춘다.**
144k 발행 조건은 lap444 §1-4로 "카드 ACCEPT **그리고** (가) 자연 도달 fixture 성립"인데,
전자는 이번에 충족됐고 **후자는 아직 착수조차 안 됐다**. (가)로 가는 길은 lap413에서 원본 생산
경로가 FAIL한 바로 그 축이고, lap444 §2가 "AI 코드/바이너리를 바꿔야 하는 순간 즉시 strategy
재에스컬레이션"으로 못박아 둔 경계다. 따라서 **다음 카드를 middle이 직접 발행하지 않고**
`loop/ESCALATE_SOL` §32로 올린다. 판정 요청 내용은 §32 참조.

