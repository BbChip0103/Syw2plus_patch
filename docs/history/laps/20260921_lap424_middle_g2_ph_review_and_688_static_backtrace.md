# 2026-09-21 | lap 424 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(중간계획·독립검수)**.
  게임 실행 0회, 제품 코드 변경 0, 커밋 0. 실무 구현은 하지 않았고 정적 역추적(읽기 전용)만 수행했다.
- 가설 / 사용자 관찰: INBOX 2026-09-21 02:58 KST — lap423 P-H를 Root가 동기 재실행(run3)해
  844표본·fault tick11928·전이경계 tick10400→10401을 얻었다. 그 회수분을 독립 검수하고,
  같은 지시의 후속("동일 장기 실행을 반복하지 말고 `0x48cba9` 경로/입력 계산을 **정적으로 역추적**")을 수행한다.
- 예상 PASS / FAIL 조건: (a) run3 원시 `samples.jsonl`만으로 INBOX 수치를 재계산해 전부 일치하면
  P-H ACCEPT. (b) `0x48cba9`의 입력을 바이트로 확정해 `+0x688=19679`의 산술 출처를 특정하면
  W13 종결·다음 표적 발행. 불일치 1건이라도 있으면 REJECT.

## 변경 파일 / source fingerprint / 커밋

- **제품 코드·패처·테스트 변경 0.** 이번 회차에 **source를 바꾸지 않았다**(INBOX 21:58 규칙/N22
  요건 충족) ⇒ 전체 `make check` 재실행하지 않고 표적 검사만 수행.
- 신규 문서: 이 기록, `docs/STATUS.md` 갱신, 신규 카드
  `docs/work/active/G2_STAT_RECOMPUTE_INPUT_700_LAP424.md`(W14).
- 검수 산출물(레포 밖 공유 temp):
  `temp/Syw2plus_patch/g2_capacity/20260921_lap424_middle_review/`
  (`recompute.py`, `cadence.py`, `cross421.py`, `scan424_68c.py`, `scan424_700.py`,
  `scan424_sites_68c.json`, `scan424_sites_700.json`, `chain424_disasm.txt`).
- 커밋: **없음(uncommitted)**. `LOOP_ALLOW_COMMITS` 미허용 기본값 유지.

## 원본 SHA / 후보 SHA / 환경 / fixture

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — 2경로
  (`syw2plus_original.exe`, `Syw2plus/조선의반격 오리지날 실행.exe`) 재해시 **불변**.
- 후보(run3) `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe` (lap413/414/419/420/421 핀과 동일).
- run3 fixture: op7 resource-only, 8 owner, N=4001, seed42, 격리 prefix+Xvfb :3844,
  `source_sha_before == source_sha_after == b56986e0…`(run_summary.json).
- 이번 lap 자체는 **게임을 실행하지 않았다**. 정적 분석 대상은 lap421이 보존한
  `original.bin`/`candidate.bin`(위 SHA와 일치 확인).

## 실행 명령 / 로그

- 재계산: `python3 recompute.py` / `cadence.py` / `cross421.py`
  (입력 `…/20260921_lap423_move_field_688_writer_run3/samples.jsonl`, 844줄).
- 정적: `objdump -D -b binary -m i386 -M intel --adjust-vma=0x400000`(lap422와 같은 독립
  디스어셈블러), 변위 스캔은 lap421 `scan421_pe.py`의 `DISP`만 바꿔 재사용.
- 검사: `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` → **6 passed**(기준선 동일),
  `bash checks/safety.sh check` → **SAFETY_PASS**.

## 측정값 / 판정

### 1. P-H(run3) 독립 재계산 — **ACCEPT (불일치 0)**

원시 `samples.jsonl`만으로 자체 재계산했다. INBOX 02:58 서술과 전항목 일치:

| 항목 | INBOX 서술 | 재계산 | 판정 |
|---|---|---|---|
| 표본 수 | 844 | 844 (인덱스 0~843 연속) | 일치 |
| fault tick | 11928 | 11928 (`move=19579`, slot3565/type76/owner4) | 일치 |
| 원본 해시 전후 | 불변 | `source_unchanged: true` | 일치 |
| `+0x688` 전이 | s657/tick10400=10 → s658/tick10401=19679 | 동일 | 일치 |
| 샘플 간격 | 20ms, tick당 대체로 2표본 | dense dt p50 **20.2ms**, tick당 1표본 174 / 2표본 157 | 일치 |

**검수자가 추가로 확인한 것(INBOX에 없던 강화 근거):**

- **N35 — dense 창 무결점 커버리지.** dense 488표본이 tick **10160~10490**을 덮고 그 331 tick 중
  **미샘플 tick 0개**다. 따라서 `+0x688`은 전 구간에서 정확히 **한 번만** 값이 바뀌었고(0→10→19679),
  전이경계 `(10400, 10401]`은 "샘플이 없어서 놓친 구간"이 아니다. 이것이 없으면 20ms 간격만으로는
  경계 주장을 지탱하지 못한다.
- **N36 — lap421과의 교차 일관성.** lap421(1초 간격, ~33tick 간격)은 tick10399에 `+0x688=10`,
  tick10432에 19679였다 ⇒ 경계 `(10399, 10432]`. run3의 `(10400, 10401]`은 그 안에 **완전히
  포함**된다. 두 독립 run이 모순되지 않는다.
- **N37 — STATUS/카드의 "alive 전이 tick10,231"은 샘플링 해상도 산물이므로 정정한다.**
  lap421은 1초 간격이라 10197(alive=false)→10231(alive=true)만 보았다. run3의 무결점 dense는
  **alive 전이를 tick10201로 확정**한다(`+0x688=10` 동반). ⇒ 활성화부터 오염까지의 간격은
  "약 200 tick"이며 정확히 **10401−10201 = 200 tick**이다. (숫자가 정확히 200인 것은 관측이며
  의미 부여는 하지 않는다.)
- **N38 — 전이 시점에 인접 추적 필드는 전부 불변.** s657→s658에서 `f674/f676/f2a2/f2a4/f2b8/
  f2ba/f2bc/f2be/f2b0/f2b2/f2d8/f690/f1d8/type/owner/move`가 **모두 동일**하고 오직 `f688`만
  변했다. 카드 §9.4가 열어둔 "`memcpy`/`rep stos` 류 구조체 통째 복사" 사각에 대한 **음성 증거**다
  (구조체 통째 복사였다면 이웃 필드도 함께 변했을 가능성이 높다).
  **한계:** 추적 필드는 18개뿐이고 1,880B 구조체 전체 덤프가 아니므로 *배제*가 아니라 *약화*다.

### 2. `0x48cba9` 정적 역추적 — **FEASIBLE·완결. `+0x688`은 "복사"가 아니라 "계산"이다**

INBOX 지시대로 실행 반복 없이 정적으로 역추적했다. **원본·후보 바이트 IDENTICAL**(세 창
`0x48c880..0x48c930`, `0x48ca60..0x48cb28`, `0x411e80..0x411ee0` 전부 `diff` 무차이) ⇒
**이 경로는 패치되지 않은 원본 코드다.**

**확정된 폐쇄형 체인 (전부 바이트 근거):**

```
; --- 인덱스 산출: edx = 916 * type ---
48cae6  xor ecx,ecx ; mov cl,[esi+0x8d]      ecx = unit type (byte @ +0x8d)
48cb00  lea edx,[ecx+ecx*8]                  9t
48cb0a  lea edx,[ecx+edx*2]                  19t
48cb14  lea edx,[edx+edx*2]                  57t
48cb1e  lea edx,[ecx+edx*4]                  229t
48cb21  shl edx,0x2                          916t        <= 스탯표 stride = 916 B

; --- +0x688 = 기본스탯[type] + (+0x68c) ---
48cb40  mov dx, WORD [edx+0x9b5258]          dx = base_stat[type]
48cb51  add dx, WORD [esi+0x68c]             dx += 보정치
48cba9  mov WORD [esi+0x688], dx             <= 관측된 write site

; --- 그 보정치 자체의 계산 (같은 함수, 약 0x295 앞) ---
48c8c7  mov ecx,[esi+0x700]                  K = 인덱스 필드 +0x700
48c8cd  lea eax,[ecx*8+0] ; sub eax,ecx      7K
48c8d6  lea edx,[eax+eax*4]                  35K
48c8d9  mov edx, DWORD [edx*4+0x669c7c]      P = 표[0x669c7c + 140*K]   <= stride 140 B
48c8e0  cmp edx,edi ; je 48c91c              P==edi 이면 보정치 0
48c8f8  movsx ecx, WORD [eax*4+0x9b5258]     ecx = base_stat[type] (같은 표)
48c900  imul ecx,edx                         base_stat * P
48c903..48c912                               /100  (0x51eb851f, sar 5 = 상수 100 나눗셈)
48c914  mov DWORD [esi+0x68c], edx           +0x68c = base_stat[type] * P / 100
48c91c  mov DWORD [esi+0x68c], edi           (else 분기)
```

그리고 생성 초기화 쪽:

```
411eb9  mov dx, WORD [eax+0x9b5258]
411ec0  mov WORD [ebp+0x688], dx             생성 시에는 base_stat[type] '그대로' 복사
```

⇒ **`+0x688` = base_stat[type] × (1 + P/100)**, 즉 이 함수는 **기본 스탯에 백분율 보정을 다시
먹이는 "스탯 재계산" 루틴**이다. `0x411ec0`이 생성 시 `+0x688=10`을 넣었다는 관측과
`0x48cba9`가 수명 중간에 19679로 덮었다는 관측이 **하나의 기전으로 통합**된다.

**산술 귀결(조건부):** 생성 시 관측 `+0x688=10`이 `base_stat[type76]=10`을 뜻한다면,
`+0x688=19679` ⇒ `+0x68c = 19669` ⇒ `10 × P / 100 = 19669` ⇒ **P ≈ 196,690**.
백분율 표의 값으로는 터무니없는 크기다. (이 한 줄만 **조건부 추론**이고 나머지는 바이트 확정이다.)

### 3. 다음 표적은 `+0x688`이 아니라 **`+0x700`(인덱스) 또는 표 `0x669c7c`의 내용**

- 변위 `0x700` 스캔: 접근 17건, **비상수 write 4곳뿐** — `0x40d733`, `0x40d79f`, `0x40f040`,
  `0x413120`. (`0x4c5854`는 `mov dword [ebx+0x700],0xb1bc` 상수 store로 `0x4c582c`와 같은
  C++ 정적 초기화 계열이며 관측값을 만들지 않는다.) **원본·후보 IDENTICAL.**
- 변위 `0x68c` 스캔: 접근 6건, write 3곳(`0x46a0b1`, `0x48c914`, `0x48c91c`), read 1곳(`0x48cb51`).
  **원본·후보 IDENTICAL.** 실질 기록자는 위 체인의 `0x48c914`/`0x48c91c` 두 곳이다.
- **표 경계 관측(미확정 상한):** `0x669c7c`(=6,724,732)부터 다음으로 알려진 객체인 **구 unit_pool
  시작 `0x66B790`(=6,731,664)** 까지 6,932 B이므로 140 B 레코드가 **약 49개**만 들어간다.
  `K = [+0x700]`이 49 이상이면 표 밖(=낯선 메모리)을 읽게 된다. **다만 이 배열의 실제 길이는
  증명되지 않았다** — 인접 객체 추정일 뿐이므로 상한으로 단정하지 않는다.

### 4. **정적 역추적은 여기서 원리적으로 끝난다 (그래서 다음은 런타임 읽기다)**

`0x9b5258`(스탯표)도 `0x669c7c`(보정표)도 `.data` raw 끝 `0x4F9000` **바깥 BSS**라 파일에
값이 없다(W2가 이미 실측한 사실과 일치). 즉 `base_stat[76]`과 `P`는 **정적으로 읽을 수 없다.**
INBOX 02:58의 "꼭 필요할 때만 직접 계측한다"는 단서가 **여기서 충족된다** — 게으름이 아니라
정적 경로가 BSS에서 닫혔기 때문이다.

### 5. 판정

- P-H(run3) 독립 검수: **ACCEPT (불일치 0)**.
- W13(`+0x688` write site 특정): **CLOSED**. 기록자는 `0x48cba9`이며, 그 값은 외부 wild write가
  아니라 **원본 코드의 스탯 재계산 산술 결과**다. 카드 §9.4의 "둘 다 아님" 분기는 N38 + 체인
  확정으로 **불필요해졌다**.
- `+0x688=19679`의 **"오염" 단정은 계속 보류**한다(사용자·카드 §9.4 지시 유지). 이제 질문은
  "누가 `+0x688`을 망쳤나"가 아니라 **"`P`(또는 `K=+0x700`)가 왜 그런 값인가"** 로 한 단계
  더 내려갔다. H3 분기(정상 스탯인데 소비 측이 못 견딤)는 여전히 열려 있다.
- G2 P2: **FAIL 유지**. 제품 미완료.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 표적 6 passed(기준선과 동일), `SAFETY_PASS`, 원본 2경로 재해시 불변, source 변경 0.
- 이번 lap은 **middle 역할의 검수·정적 진단**이며 자기 승인이 아니다. §2~§3의 체인은 다음
  work 회차의 런타임 실측으로 확증되어야 한다(아래 W14).
- **남은 위험 / 살아있는 한계:**
  1. `base_stat[type76]=10`은 생성 시 관측으로부터의 **추론**이다. 런타임으로 직접 읽어야 한다.
  2. N38은 구조체 통째 복사 가설을 **약화**할 뿐 배제하지 않는다(추적 18필드 한정).
  3. `0x669c7c` 배열의 실제 길이는 미증명이다(약 49개는 인접 객체 추정).
  4. `edi`가 `0x48c8e0` 시점에 0이라는 것은 **미검증**이다(주변 용법상 유력할 뿐).
  5. `0x48cba9` 경로가 **원본과 동일**하다는 사실은 "후보 고유 결함 아님"을 시사하지만,
     후보만 여기서 죽는다는 관측(stock 대조군은 tick13,116까지 무사고)과 아직 화해되지 않았다.
     → 그 화해가 W14의 핵심이다.
- 사용자 마일스톤 승인: 없음. APPROVALS 변동 없음.

## 다음 한 가지

**work(Sonnet5/high)가 `docs/work/active/G2_STAT_RECOMPUTE_INPUT_700_LAP424.md`(W14)를 수행한다.**
tick10401이 정확히 특정됐으므로 광범위 dense 재실행 없이, 기존 probe의 **읽기 주소 4개만 추가**해
`+0x700`(K), `+0x68c`, `WORD[0x9b5258+916*type]`(base_stat), `DWORD[0x669c7c+140*K]`(P)를 전이 전후로
읽는다. 이것이 "K가 범위 밖(진짜 손상)"과 "K는 정상인데 표/스탯이 크다(H3, 원본 고유)"를 가른다.
