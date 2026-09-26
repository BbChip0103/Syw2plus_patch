# G2 work 카드 W3 — 전역 UnitStruct 풀 확장 실행 스파이크

> **SUPERSEDED (lap400 middle, 2026-09-20): 후속 카드는
> `docs/work/active/G2_UNIT_POOL_RELOCATION_SPIKE_LAP400.md`(W4)다.**
> §A 합격식·§C 봉투·§D 산출물·§E 범위경계는 **그대로 유효**하다. 정정된 것은 §B-1 하나다:
> 이 카드가 지목한 `base_preserving_storage_layout_v1`은 이름대로 unit_pool의 base를
> **움직이지 않는** 계산기라, 같은 §B-1이 요구한 "재배치 필수·새 공간은 이미지 꼬리"와
> 서로 모순된다. lap399가 그 계산기에 B-1을 위임한 결과 풀 fixup **0건 적용**·풀이 제자리에서
> live state를 18,800 B 침범했다(리터럴 1,311건 충돌). 근거는
> `docs/history/laps/20260920_lap400_middle_g2_pool_overrun_reject.md`.
> **이 카드의 §B를 그대로 다시 수행하지 말 것.**

발행: lap397 middle (Claude Code `claude-opus-5` / high), 2026-09-20 KST
수행: work tier (`claude-sonnet-5` / high 또는 Luna/high), **다음 work 회차**
상한: **한 work 회차 또는 60분 중 먼저 도달하는 시점, 실패 가설 2개**
승인: **불필요** — 기존 격리 사본 + 기존 save000 fixture. 새 생성 fixture·새 시나리오 없음.

> **이 회차는 반드시 제품 코드/바이너리/실행 증거를 늘려야 한다.**
> lap397로 implementation-unchanged-streak가 **2**가 됐다. 세 번째 무변화 회차는
> PROMPT ③에 따라 Astra/Sol의 계속·중단 판정이 선행해야 한다. **추가 계획 회차를 쌓지 말 것.**

## 0. 무엇이 이미 닫혔는가 (lap397 정적 측정, 재조사 금지)

probe `docs/history/laps/probes/20260920_lap397_middle_g2_unit_pool_expansion_probe.py`
(rc0 `failures=[]`, SHA `b0761f19…aebe27f`), 산출물 SHA `dd726966…e79dd41`.
상세 `docs/history/laps/20260920_lap397_middle_g2_unit_pool_expansion_surface.md`.

| 사실 | 값 | 함의 |
|---|---|---|
| slot-id로 색인되는 영역 | **pool / existence / age 3개뿐** | 나머지는 건드릴 필요 없음 |
| active·catA·catB | **count 색인** (`inc [0x975908]`/`[0x89c2c8]`/`[0x89d58a]`) | 살아있는 유닛<1200이면 안 넘침 |
| PlayerStruct roster | `cmp ax,0x4B0`는 **owner 유닛 개수** 제한 | 저장 레이아웃은 임계경로 **아님** |
| `0x892410` 참조 179건 | `mov ecx` 177 + `push` 2, **bound 꼴 0건** | 재배치해도 **1건도 수정 불필요** |
| 풀 변위 후보 986건 | **전부 stride 버킷0**, 이상치 0 | 균일 +delta가 전부 번역 |
| 풀 base 정확값 115건 | `lea` 109 / `mov` 4 / **`cmp` 2** | 개별 판단은 `cmp` 2건뿐 |
| 할당자 상수 | **3개** + 전멸 루프 1개 | 아래 §B 표 |
| 제자리 확장 | **불가** — 풀은 bulk에 밀착, age 뒤 구멍은 참조 9건 | **재배치 필수** |

## A. 합격/실패 측정식 (먼저 적는다)

사용자 2026-09-20 00:33 KST 지시의 첫 성공 기준을 그대로 쓴다.

| ID | 측정 | PASS | FAIL / BLOCKED |
|---|---|---|---|
| S-1 | 패치본이 원본과 **같은 지점까지 정상 구동**(save000 로드, PS35→PS3) | 기존 S1 경로 그대로 통과 | 통과 못하면 즉시 원복·FAIL |
| S-2 | 기존 reader로 **slot index ≥ 1200** 개체를 관측 | `existence[slot]!=0` 이고 `unit+0x29c == slot` 인 slot ≥ 1200 이 1개 이상 | 0개 → 도달성 미달(BLOCKED, 유도 조건 기록) |
| S-3 | 그 개체가 **정상 필드**를 갖는다 | `unit+0x8d`(type)·`+0x8e`(owner)가 fixture의 유효 범위 | 쓰레기값 → 재배치 결함 |
| S-4 | **사망** | 해당 slot의 `existence`가 0으로 돌아감 | 남으면 제거 경로 결함 |
| S-5 | **슬롯 재사용** | 사망한 slot ≥1200 이 다시 `existence!=0`로 재할당됨 | 재할당 안 되면 할당자 결함 |
| S-6 | **인접 상태영역 무손상** | bulk `[0x892410, 0x975D8C)` 안에서 관측 중인 owner 장부·roster·active count가 정상 범위 유지 | 손상 → 즉시 STOP·보존·FAIL |

**S-2 + S-4 + S-5 가 전부 PASS여야 `FEASIBLE`이다.** 하나라도 미달이면 억지로 만들지 말고
`NOT_FEASIBLE` 또는 `BLOCKED` + 누락 입력을 적는다.

## B. 최소 변경 명세 (이 이상으로 넓히지 않는다)

`N`은 **작게** 잡는다 — 권고 **N = 1300**. 목표는 "slot index ≥1200이 살아 움직인다"를
보이는 것이지 최종 용량을 정하는 것이 아니다.

### B-1. 재배치 (3영역)

새 공간은 이미지 꼬리를 늘려 확보한다(`.rsrc` 위, `0x0108BA38` 초과). `.data`는 가상 12,188,216 B /
raw 53,248 B라 대부분 BSS이며, bulk 위 구간에는 다른 전역들이 살고 있어 **비어 있지 않다**.
lap382~388이 만든 `base_preserving_storage_layout_v1.py` / `.pelayout` 계산기가 이 용도다.

| 영역 | 원본 | 새 크기(N) | delta |
|---|---|---|---|
| unit_pool | `0x0066B790`, 1880 B × 1200 | 1880 × N | 새 base − `0x66B790` |
| existence | `0x008990C8`, 2 B × 1200 | 2 × N | 새 base − `0x8990C8` |
| age | `0x00899A28`, 2 B × 1200 | 2 × N | 새 base − `0x899A28` |

**existence 와 age 는 반드시 `새_age_base == 새_existence_base + 2N` 으로 인접 배치한다** —
할당자가 그 인접성을 `[ecx-0x960]` 변위로 쓰기 때문이다(§B-2).

### B-2. 상수 4개 (old bytes 확인 후 교체, 정확한 원복 스크립트 동반)

| 주소 | old bytes | 의미 | 새 값 |
|---|---|---|---|
| `0x00442FAC` | `b9 2a 9a 89 00` | 스캔 시작 | `새_age_base + 2` |
| `0x00442FB1` | `66 83 b9 a0 f6 ff ff 00` | existence 상대 변위 `-0x960` | **`-2N`** |
| `0x00442FD1` | `81 f9 88 a3 89 00` | 스캔 배타적 끝 | `새_age_base + 2N` |
| `0x0044317D` | `81 fe b0 04 00 00` | 전멸 루프 상한 `0x4B0` | **`N`** |

`0x0044317D` 단독 변경은 **금지**다(사용자 명시). 반드시 B-1 재배치와 한 묶음으로만 바꾼다.

### B-3. fixup

- 풀: 변위 **986건**(전부 버킷0 ⇒ `disp += delta_pool`) + 범위내 즉시값 **30건**.
  **`cmp` 2건 `0x00421349` / `0x0048F4B4` 은 하드 제외**(lap398 FO-4 확정: pool과 무관한 선행
  정적 테이블 `0x00669c38..0x66b790`의 자기 루프 종료조건, 적용하면 무한/조기루프 결함).
- existence / age: 기존 인벤토리 `tools/g2_unit_pool_xrefs_evidence.json` 의
  `unit_existence`(즉시 2 / 변위 32 / endpoint 34+4) · `unit_age`(즉시 3 / 변위 2 / endpoint 1+6)를
  기준으로 삼되 **패처가 스스로 재수집**한다(핀 손 전사 금지).
- **`0x892410` 179건은 건드리지 않는다**(A8).
- **active / catA / catB / PlayerStruct 는 건드리지 않는다**(A2·A7).

### B-4. 먼저 닫아야 할 fail-open (착수 첫 20분, 실패 시 여기서 BLOCKED)

**lap398 work가 아래 세 건을 전부 바이트로 닫았다(재조사 금지, 상세는
`docs/history/laps/20260920_lap398_work_g2_unit_pool_fo_closure.md`):**

- **FO-1 — PASS.** 986건 중 30건 균등샘플 검사, 반례 0건. 단 원가설("전부 slot 색인")은 정정된다:
  `0x66b81d`/`0x66b81e`(필드오프셋 `0x8d`/`0x8e`, S-3의 type/owner와 동일 오프셋) 등은 실제로는
  **type_id×40 색인 정적 룩업테이블**이 slot0의 1880B 공간을 점유한 것이며(A3 "slot 0 never
  allocated"의 이유), slot 색인이 아니다. **그래도 결론은 그대로다:** `[POOL_BASE,POOL_END)`
  전체를 슬롯0 포함 통짜 바이트블록으로 복사·이동하고 그 구간 안 모든 리터럴에 +delta를 적용하면
  정적 테이블·동적 슬롯 구분 없이 안전하게 번역된다(§B-1/§B-3 설계 변경 불필요).
- **FO-3 — PASS.** `0x0089A388`은 WORD×1600(3200B) 배열 시작이며 `[0x89a388,0x89b008)`
  구간에 배타적으로 존재, pool/existence/age와 겹치지 않는다. 옮기지 않는다(그대로 둔다).
- **FO-4 — PASS, 신규 결론(설계에 반영 필요).** `cmp 0x00421349`/`0x0048f4b4` 두 사이트는
  **pool과 무관한 선행 정적 테이블**(`0x00669c38`에서 시작, 요소당140B×50개, 끝값이 우연히
  `POOL_BASE`와 같음)의 자기 루프 종료조건이다. 이 테이블은 재배치 대상이 아니므로 두 `cmp`의
  리터럴 `0x66b790`은 **손대지 않는다**. **⇒ §B-3 fixup 수집 시 이 두 주소를 하드 제외 목록에
  추가할 것.** 넣으면 이 두 루프가 무한/조기 종료로 깨진다.

**다음 회차는 위 결론을 재검증하지 않고 그대로 사용해 §B-1~§B-3 구현에 착수한다.**

## C. fixture / 실행 봉투 (명시 — 임의 축소 금지)

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 **읽기만** 하고
  **새 복사본**에 패치한다. 원본/참고 저장소 쓰기 금지. 패치 전후 원본 재해시 기록.
- 기존 격리 전체 게임 복사본 / 전용 Wine prefix / 빈 Xvfb display. 기존 세션 접속·전역 pkill·
  다른 로그 정리 **금지**. 종료 후 잔류 0 확인.
- 상태: 기존 `save000` 8 PlayerStruct 로드 경로(logical load-button `(316,372)` 1회, PS35→PS3) 재사용.
  **새 생성 fixture를 만들지 않는다.**
- 읽기 수단은 기존 `process_vm_readv` 폴링 **그대로**.
  `process_vm_writev`/`ptrace`/`int3`/디버거 **금지**(lap324 확정).
- **메모리 쓰기 0.** 변경은 디스크 상의 패치 사본 바이트뿐이다.

## D. 산출물

- 패치/원복 스크립트 + 신규 reader probe, 공유 temp
  `…/temp/Syw2plus_patch/g2_capacity/20260920_unit_pool_expansion/lap<N>_work_spike/` 에 저장.
  경로와 SHA256을 lap 기록에 남긴다. 캡처 PNG는 지정 temp에 `YYYYMMDD_HHMMSS_` 접두사.
- 매 회차 `make check` + `checks/safety.sh check` + 원본 재해시 불변 기록.
- lap 기록은 `docs/history/LAP_TEMPLATE.md` 필드 전부.
  **fixture SHA는 기계 산출물 필드를 인용**한다(손 전사 금지 — N16 재발 방지).

## E. 범위 경계

- **저장/LAN은 이 스파이크의 PASS 조건이 아니다**(사용자 명시). 그러나 **후속 필수 blocker**로
  기록한다: 풀 이동은 save_roster `0x40F4B0` / load_roster `0x40F4F0` 의 즉시값이 따라가므로
  동작은 하나 **저장 파일 호환성은 깨진다**.
- lap385/388의 저장포맷 통합 blocker와 lap389 A NO_GO를 **뒤집지 않는다**. 이 스파이크는
  그 blocker를 우회하는 것이 아니라 **그 blocker가 걸리지 않는 부분집합**임을 A7이 보였을 뿐이다.
- `loop/ESCALATE_SOL` §9의 F4 cap 판정은 **여전히 열려 있다**. 사용자 우선순위 변경으로
  후순위가 됐을 뿐이며 work가 그 숫자나 합격 기준을 바꾸지 않는다.
- baseline/golden/안전 pin을 고쳐 통과시키지 않는다. 실패는 보존한다.
- 결과는 **다음 새 middle 세션이 독립 검수**한다. work는 자기 결과를 최종 승인하지 않는다.
