# G2 첫 가능성 판정 — 2026-09-15

프로필: original EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
근거는 `Syw2plus_re/analysis/ghidra_output/FUN_0043eda0.c`, `FUN_0043ee30.c` 원문을 읽기 전용으로 대조하고 기존 실제 1인5000 실행 보고 `population_5000_runtime_0910.md`를 분리한 것이다. 아래 결과는 이번 fresh 8인 게임 시험이 아니다.

| 제약 | 원본 관계 | 판정 |
|---|---|---|
| PlayerStruct `+0x200a` | owner roster 개수, 16-bit | CONFIRMED static |
| `+0x200c`, `+0x2012` | 사용 전비/상한, 비용 테이블 `0x9B5238 + type*0x394`, 16-bit | CONFIRMED static |
| `+0x2010` | owner 개수 상한, 원본 시작250; 일반 유닛은 8칸 예약 | CONFIRMED static + 이전 runtime |
| roster `+0xd4a` | 4-byte 유닛 slot 목록, `FUN_0043EE30`에서 개수 `>0x4AF`면 overflow | CONFIRMED static |
| `FUN_00442FA0`, existence `0x8990C8`, slot1–1199 | 공용 슬롯과 id/다른 개체 수명 범위 | PREVIOUS runtime/static; fresh 8인 측정 필요 |
| 저장/네트워크의 개체 슬롯 | 범위 확장이 기존 포맷·멀티와 호환되는지 | UNKNOWN |

**즉시 판정:** 전비 상한 숫자만 5000으로 올려도 8인 모두가 임의의 유닛 구성으로 5000에 도달한다는 주장은 **NOT_FEASIBLE**이다. 비용10 유닛만이면 1인 500기, 8인 4000기가 필요해 기존 개인 250/공용1199 상한을 모두 넘는다. 비용35만이면 상한을 넘지 않는 최대가 각142기(4970), 8인1136기이며 여기에 건물/전비0 개체가 같은 풀을 쓴다. 이는 G2 전체가 절대 불가능하다는 뜻은 아니며, owner count와 공용 slot, ID/보조배열, 저장/지원 직렬화를 실제 확장할 수 있는지는 **BLOCKED**다.

**즉시 활성화 NO-GO:** Ghidra `FUN_0040f4b0/f0`는 existence 1200항목에서 저장/복원을 멈추며 `FUN_00442fa0`는 별도 age/existence sidecar를 사용한다. UnitStruct 풀 `0x66b790 + 1200×0x758 = 0x892410`은 **그대로 저장되는 bulk game-state 시작**과 일치한다. 단지 할당기나 루프의 상한을 1201로 올리면 slot1200은 원본 live state를 덮는다. 원본 EXE SHA에 대한 .text 리틀엔디언 패턴 검사에서 정확한 base `0x66b790` 115건, 첫 UnitStruct 0x758B 내 even 필드주소 raw 패턴943건(명령 경계 미확정·오탐 가능), existence `0x8990c8` 34건; 이는 qhd의 새 PE section 선례만으로 새 슬롯의 모든 생성/파괴/틱/명령/저장 참조가 자동 재배치된다는 주장을 반증한다. 풀 확장 자체의 절대 불가능 판정은 아니다.

32-bit PE 헤더를 직접 읽으면 `Characteristics=0x010f`, LargeAddressAware 비트 `0x20`은 **unset**이다. 그렇더라도 필요한 UnitStruct 본체의 단순 크기는 `0x758`(1880 B)×4000 = 7,520,000 B(7.17 MiB), 추가 8 PlayerStruct는 `0x3abc`×8 = 120,288 B(0.115 MiB)다. 이는 전체 게임/길찾기/저장/드라이버 사용량을 포함하지 않으므로 OOM 안전증명은 아니지만, **32비트 자체가 8인5000의 절대 불가능 조건이라는 주장도 뒷받침하지 않는다**. 원본의 고정 슬롯·게이트·직렬화가 먼저 확인되는 제약이다.

**다음 판정 한 가지:** protected SHA-pinned read-only xref inventory에서 생성/파괴/틱/명령과 existence/age/ID auxiliary 배열, owner roster와 save/load의 **새 slot1200 모든 실제 reachable 경로**를 정리한다. 위 raw-pattern 수치는 완전한 함수/명령 목록이 아니므로 실행 허가가 아니다. 완전한 private translation·저장 byte-order/호환 계획 없이는 slot1200 game probe를 시작하지 않는다. 조사 60–90분·실패 가설2회 내 닫히지 않으면 풀 확장 경로는 명시적 BLOCKED로 보고한다. 현재 보호 save000/006 및 기존 GUI harness는 활성8인 fixture를 즉시 제공하지 않아 8인×5000 측정도 별도 준비가 필요하다. 현재 1인5000 런타임은 존재증명일 뿐 8인5000을 대체하지 않는다.

**이번 bounded 코드 slice:** `tools/g2_unit_pool_xrefs.py`는 protected original SHA를 확인하고 PE32 Capstone operand만 수집한다; 현 `tools/g2_unit_pool_xrefs_evidence.json` SHA `b074781394d9bcab6570d51c60ca046ce06bf108a4c6d20eb9e5bb3d4043b54c`. direct calls allocator18/spawn29/destruction13/save1/load1 및 endpoint operand unit base115/existence base34/bulk start179를 보존한다. half-open region은 pool/existence/age/active-slot-list/category-list A/B 여섯 개다. direct absolute-memory ref는 모두0; in-range immediate 후보는30/2/3/72/0/0, base/index displacement 후보는986/32/2/17/6/1이다. immediate는 큰 pool 범위에 우연히 든 숫자일 수 있고 base/index는 effective address가 런타임 의존이므로 모두 **후보**일 뿐이다. 텍스트 함수 경계·간접 호출·data pointer·초기화/reset·저장/LAN 완전 경로는 **INCOMPLETE**, 출력 `activation=NO-GO`; targeted3/Ruff/mypy PASS. 이 조사는 제품 풀 확장이나 슬롯1200 실제 생성 근거가 아니다. 최초 exact-endpoint evidence SHA `eda12307…11a65`는 2026-09-15 역사 기록에만 보존한다.
