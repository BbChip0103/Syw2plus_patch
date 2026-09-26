# W14 — 스탯 재계산 입력(`+0x700` / 표 `0x669c7c`) 실측 (발행: lap424 middle, 수행: 다음 work 회차)

- 발행자 / 역할: lap424 Claude Code `claude-opus-5` / high / **middle(검수·중간계획)**.
  근거 `docs/history/laps/20260921_lap424_middle_g2_ph_review_and_688_static_backtrace.md`.
- 수행 역할: **work (Sonnet5/high)**. 실행 probe 1회(읽기 주소 추가만).
- 선행 상태: **W13은 CLOSED**. P-H(run3) 독립 검수 ACCEPT, `+0x688` 기록자는 `0x48cba9`로
  확정됐고 그 값의 산술 출처까지 바이트로 닫혔다. 이 카드는 그 **한 단계 아래 입력**을 잰다.
- 목표 연결: G2 P2(원본 생산·AI 경로 안정성). fault `0x00414133`의 인과 사슬 최상류 확정.

## 1. lap424가 확정한 것 (재조사 금지)

**원본·후보 바이트 IDENTICAL**인 원본 코드의 폐쇄형 체인이다:

```
K   = DWORD [unit+0x700]                         ; 인덱스 필드
P   = DWORD [0x669c7c + 140*K]                   ; 140B 레코드 배열, 백분율로 보임
base= WORD  [0x9b5258 + 916*type]                ; 916B stride 유닛타입 스탯표 (type=76)
+0x68c = base * P / 100        (0x48c914; P==edi 면 0 → 0x48c91c)
+0x688 = base + [+0x68c]       (0x48cb51 → 0x48cba9)
생성 초기화: +0x688 = base     (0x411ec0, 보정 없음)
그 뒤: 0x40bc86~0x40bcfe 가 매 tick +0x688 을 +0x692 에 누산(mod 65536, lap421/422 유일해 확정)
그 뒤: 0x00414133 이 100칸 stack 배열을 ((경로점수-1)*|+0x692|)/100 로 인덱싱 → page fault
```

- 전이 경계는 **tick10400→10401**(run3 dense, 미샘플 tick 0). alive 전이는 **tick10201**
  (STATUS/카드의 "10,231"은 1초 샘플링 산물이었다 — 정정됨). 간격 정확히 200 tick.
- 전이 시점에 추적 18필드 중 **`f688`만** 변했다(구조체 통째 복사 가설 약화).
- `+0x700` 비상수 write는 **4곳뿐**: `0x40d733`, `0x40d79f`, `0x40f040`, `0x413120`.
  (`0x4c5854`는 상수 `0xb1bc` store = C++ 정적 초기화 계열, 제외.)
- `+0x68c` 실질 기록자는 `0x48c914`/`0x48c91c` **2곳뿐**. 전부 원본·후보 동일.
- **정적 경로는 여기서 끝난다** — `0x9b5258`과 `0x669c7c` 둘 다 `.data` raw 끝 `0x4F9000`
  바깥 **BSS**라 파일에 값이 없다(W2 기존 실측과 일치). 그래서 이 카드는 런타임 읽기다.

## 2. 수행 순서와 측정식

### P-I. 입력 4개 실측 (이 회차의 유일한 실행 증거)

lap423 `movement_state_probe_pf.py`를 복사해 **읽기 주소 4개만 추가**한다. 새 dense 창을
넓히지 말고 전이 tick이 이미 알려진 점을 쓴다(`DENSE_LO=10380`, `DENSE_HI=10420`이면 충분).
fault까지 갈 필요 없으므로 **tick 10500에서 정상 종료**해도 된다(약 52초 절약).

슬롯3565에 대해 매 표본 기록:

1. `K  = DWORD [unit+0x700]`
2. `m  = DWORD [unit+0x68c]`
3. `base = WORD [0x9b5258 + 916*type]`   (type은 이미 읽고 있음; 76이면 주소 `0x9C6248`)
4. `P  = DWORD [0x669c7c + 140*K]`  — **K가 0~48 범위 밖이면 이 읽기는 건너뛰고 `null`로
   기록한다**(probe 자신이 낯선 주소를 읽어 죽지 않게 한다). 대신 K 값을 그대로 남긴다.

추가로 **참조용 정상 슬롯 1개**를 같은 4필드로 함께 기록한다(같은 owner4의 다른 live 유닛
아무거나, band_scan이 이미 고슬롯을 훑으므로 거기서 하나 고정). 3565만 특이한지 판단하려면
같은 run 안의 대조가 필요하다.

### 판정식 (실행 전 고정)

- **(A) `base`가 전이 전후로 변한다** ⇒ 스탯표 자체가 런타임에 손상됐다는 뜻. 표
  `0x9b5258`(BSS)을 누가 쓰는지가 새 표적이 되고, 이것은 **풀 확장 회귀의 유력 후보**다.
  (lap422 §9.3이 배제한 것은 "재배치 영역이 스탯표와 **정적으로 겹친다**"뿐이며, **런타임
  OOB write**는 배제된 적이 없다 — 다른 주장이므로 재조사 금지 대상이 아니다.)
- **(B) `base`는 10으로 불변인데 `K`가 전이 tick에 바뀐다** ⇒ `+0x700`이 표적. 위 4개 write
  site 중 어느 것이 그 tick에 도는지 좁힌다. `K`가 0~48 밖이면 **표 밖 읽기 = 실제 손상**으로
  승격하고, 그때 비로소 "오염"이라 부를 근거가 생긴다.
- **(C) `base`·`K` 모두 정상 범위인데 `P`가 거대하다** ⇒ 보정표 `0x669c7c`의 내용 문제.
  표를 채우는 쪽(연구/업그레이드 적용 경로)이 표적이 된다.
- **(D) 셋 다 정상인데 `+0x68c`만 19669** ⇒ 이 체인 밖의 경로가 `+0x68c`를 쓴 것이다.
  `0x46a0b1`(`mov [edi+0x68c],eax`, edi는 `0x469db0`의 `lea edi,[esi+0x68c]`에서 옴)을
  먼저 본다. 추측 수리 없이 근거를 올린다.
- **정정 의무:** `+0x688=19679`를 **아직 "오염"으로 단정하지 않는다.** (C)가 나오면 이것은
  **원본 고유 엣지 케이스(H3)** 이며 "정상 스탯인데 소비 측(누산기/`0x414133`)이 못 견딘다"가
  참이 된다. 그 경우 수리 지점은 `+0x688`이 아니라 **소비 측 경계**다 — 단, `0x00414133`과
  `0x0040bc86~0x40bcfe`는 계속 **패치 금지**이므로 수리안은 다음 카드로 넘기고 이 회차에서
  직접 고치지 않는다.
- K가 전 구간 불변이고 base도 불변이고 P도 작다면 **측정 실패가 아니라 결과**다 — 그대로
  기록하고 (D)로 간다.

### 실패 예산

실패 가설 2회 또는 60분 안에 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`로 판정한다.

## 3. 대상 고정 (변경 금지)

- 후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`,
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기 전용).
- fixture는 lap421/423과 **동일**: op7 resource-only, 8 owner, N=4001, seed42, 새 prefix/display.
  (결정성은 N25 + lap424 N36으로 뒷받침된다 — 전이 tick이 두 run에서 모순 없다.)
- `0x00414133` / `roster_add 0x0043ee39` / `0x00422dc7` / `0x0040bc86~0x40bcfe` / `0x0040c1c2` /
  `0x48cba9` / `0x48c914` / `0x411ec0` **전부 패치 금지**. 이 회차는 **읽기 전용 계측만** 한다.
- 격리: `tools.runtime_env.prepare()` 신규 사본 + prefix + 빈 display. 자기 실행분 잔류 0.
- **장기 probe는 모델 세션이 직접 동기로 기다린다**(INBOX 2026-09-21 01:01 운영 규칙,
  lap423이 이걸 어겨 run이 끊겼다 — 셸 background 금지).

## 4. 범위 밖

- strict cap 정책 / 전비 장부 32bit(F4·되물음) — 사용자 답변 대기.
- LAN, G1, G4, G3(중단). G1/G4는 INBOX 2026-09-21 00:20 지시로 G2 성립 전까지 잠정 중단.
- W12가 닫은 H5 vs H6 재론, W13이 닫은 `+0x688` write site 재탐색.
- 어떤 명령 바이트 패치도 이 카드 범위 밖이다(계측 전용).

## 5. 검사

- 표적: `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q`(기준선 **6 passed**).
- source를 바꿨으면 통합 경계에서 `make check`를 한 번 실행한다. 안 바꿨으면
  **"이번 회차에 source를 바꾸지 않았다"를 기록**하고 생략한다(N22).
- 매회 `checks/safety.sh check` → `SAFETY_PASS`, 원본 2경로 재해시 불변.
- `docs/history/laps/`에 LAP_TEMPLATE 필드로 기록하고 `docs/STATUS.md` 갱신.

## 6. 산출물

`temp/Syw2plus_patch/g2_capacity/<날짜>_lap<N>_stat_recompute_input_700/`.
재사용 선행 산출물: lap423 `movement_state_probe_pf.py`(읽기 주소만 추가),
lap424 `scan424_68c.py`/`scan424_700.py`/`chain424_disasm.txt`
(`temp/Syw2plus_patch/g2_capacity/20260921_lap424_middle_review/`).

## 7. 중단 조건

- 포인터 손상/저장 이상/원본 변조가 보이면 숨기지 말고 수치와 함께 보고하고 멈춘다.
- baseline·핀·golden을 고쳐 통과시키지 않는다. 자기 결과를 자기가 최종 승인하지 않는다.
- probe가 낯선 주소를 읽어 죽는 일이 없도록 K 범위 가드를 반드시 넣는다(§2 항목 4).
- 판정이 (A)로 나오면 그것은 **풀 확장 회귀의 구조적 원인 후보**이므로 즉시 STATUS·
  `loop/ESCALATE_SOL`에 올리고 다음 상위 판정을 받는다.
