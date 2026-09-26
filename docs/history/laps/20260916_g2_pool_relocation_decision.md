# 2026-09-16 — G2 8인 전비5000: 단순 상수 패치 NO-GO, 풀 재배치 조건부 GO

## 결론

큰 분기 Astra/medium 검수는 **C: 경로 수정 후 static manifest spike만 허용**으로 판정했다. 별도 arena는 engineering-plausible이나 현재 inventory로 제품 가능성을 증명하지 못하며, 제품이 original-based patch로 정의된 상태에서 조사 blocker만으로 source recreation에 자동 전환하지 않는다.

- **이미 되는 범위:** 원본 PE32에서 전비 상한을5000으로 바꾸고 1인145개 개체/실전비5000, save/load 뒤 생산 재개, 24,836연속 tick은 기존 실제 런타임 증거로 PASS다.
- **안 되는 범위:** 위 두 전비 상수와 개인 count만 올려서 8인이 임의 구성으로5000을 쓰게 하는 방식은 NO-GO다. 비용10 구성은 최대4000개가 필요하지만 원본 공용 UnitStruct는1200 slot이다.
- **근본 판정:** 32-bit 메모리 양 때문에 불가능한 것은 아니다. 비용10 유닛만 계산하면 live4000개이며 원본처럼 slot0을 예약할 때 index1..4000, 즉 최소4001 slot=`7,521,880`B(약7.17MiB)다. 단 건물·전비0 오브젝트도 같은 풀을 쓰므로4001은 최종 용량이 아니라 **산술 하한**이다. 원본 고정 풀을 제자리에서 늘리면 정확히 다음 live-state `0x892410`을 덮는다. **별도 zero-filled RW PE section/고정주소 arena로 풀과 sidecar를 재배치하고, 모든 실제 참조·상한·저장·LAN을 함께 고치는 침습 패치라면 조건부로 가능하다.** 현재는 구현 GO가 아니라 fail-closed relocation manifest 작성 GO이며 slot1200 실행은 계속 금지한다.

## 새 근거

- SHA-pinned 원본에서 풀 `[0x66b790,0x892410)`, stride `0x758`,1200개; existence `[0x8990c8,0x899a28)`는 2B×1200. age 배열은 같은 `0x899a28`에서 시작해 `[0x899a28,0x89a388)` 2B×1200이고 allocator가 slot1 주소 `0x899a2a`부터 `age[-0x4b0]`으로 existence와 결합한다. 즉 `0x899a28`은 existence end이자 age base라 endpoint 이름만 기계적으로 바꾸면 안 된다.
- 별도 active-unit slot list `[0x974fa8,0x975908)`도 정확히 short×1200이고 count가 바로 다음 `0x975908`이다. `FUN_0048BC00`은 `list[count]`에 추가한 뒤 count를 증가시키며, `FUN_00442FE0`은 swap-remove한다. 보호 Ghidra 출력에서 base를 언급하는 파일은39개다. 따라서 pool/existence만 재배치해도 1201번째 active 항목이 count와 후속 live state를 덮는다.
- 같은 `FUN_0048BC00`은 분류별 slot list A `[0x89b008,0x89c2c8)` 및 B `[0x89c2ca,0x89d58a)`에 `dword slot_id`를 추가한다. 각각 정확히1200항목이며 word count가 각 exclusive end에 바로 놓인다. 이 두 목록도 풀 확장 시 함께 재배치/경계수리하지 않으면 1201번째가 count/후속 state를 덮는다.
- save `FUN_0040F4B0`/load `FUN_0040F4F0`는 existence 포인터가 `0x899a28`에 닿을 때까지 돌며 live slot마다 `0x758`B를 기록/복원한다. 따라서 풀만 옮기고 이 범위와 save 주변 레코드를 그대로 두는 방식은 불충분하다.
- 더 바깥 save/load는 `0x892410`부터 `0xe397c`B bulk state를 unit record보다 먼저 기록/복원한다(`FUN_00440C20`/`FUN_00440FF0`). 현재 existence/age도 이 span 안이다. 따라서 roster loop만 늘릴 수 없고 새 authoritative sidecar의 버전·순서·구버전 migration 또는 명시적 거부가 필요하다.
- decoded direct-call/endpoint 기존 inventory는 pool base115, bulk boundary179, existence base34, allocator18/spawn29/destruction13/save1/load1이다. 이는 exact endpoints만 센 불완전 목록이다.
- 확장된 region inventory SHA `b0747813…43b54c`은 pool/existence/age/active-list/category-list A/B의 direct absolute-memory ref를 각0으로 두고, in-range immediate 후보30/2/3/72/0/0와 base/index displacement 후보986/32/2/17/6/1을 분리한다. 큰 pool 범위 안의 immediate에는 `test eax,0x800000` 같은 숫자 noise가 실제 포함돼 semantic ref로 승격할 수 없다. Capstone linear decode 자체도 embedded data/alignment·reachability를 보증하지 않는다.
- `.text` decoded immediate 전수의 별도 bounded inventory(`temp/Syw2plus_patch/intermediate/g2_pool_bound_immediates_20260916.json`, SHA `ac52ff0c9f4086a952a1844fb3687c6ae7a59246289ff989eab0cdb588f948ff`)에는 값1200이36회, stride1880이5회, stride-dword470이4회, existence-byte-size2400이22회다. 공통 숫자 오탐을 포함하므로 전부 유닛 상한이라고 주장하지 않지만, 두 숫자만 바꾸는 패치가 아님을 보여준다.

## 구현 가능 조건

1. 원본과 겹치지 않는 고정 RVA에 non-executable RW/BSS arena를 만들고 UnitStruct 최소4001개, existence/age, 전체 active-slot list 및 두 category list를 분리 배치한다.
2. 주소가 같아도 의미를 분리한다. `0x892410`은 pool exclusive-end와 unrelated bulk-start, `0x899a28`은 existence exclusive-end와 age-base다. immediate 숫자·absolute memory·base/index displacement를 후보로 분리하고 containing function/원본 bytes/old→new 식/count·end 의미를 기록한다. 단순 주소 일괄 치환 금지다.
3. allocator/파괴/틱/선택/렌더/AI의1200 경계를 분류해 실제 unit-slot 경계만4000으로 바꾼다. owner roster는 1인500개 요구를 담는지 실제 entry 폭/상한과 함께 확인한다.
4. save는 구버전1200 reader와 새4000 writer/version marker를 설계하거나 명시적으로 비호환 처리한다. 기존 save 순서에 새 existence/sidecar가 어디 들어가는지도 확정한다.
5. LAN은 모든 peer가 같은 패치를 써야 한다. unit id/packet/명령 결정성 및 disconnect/save sync를 실제2-client→8-client 순으로 검증하기 전 지원 주장 금지다.
6. 최소 fixture:8 owner 활성, owner당 비용10 기준500개 또는 비용 혼합으로 used5000, 총4000 live, 생산/사망/재할당/save-load와24k→144k. 실행 전 relocation manifest가 정적 참조를 닫아야 한다.

## 중단 조건

relocation manifest 뒤에도 base/index-dependent·data pointer·초기화/reset·active-list·간접 reference를 함수 단위로 닫지 못하거나 save/LAN slot 폭·버전 거부 경계를 확정하지 못하면 원본 엔진 패치 레인은 BLOCKED로 종료한다. 제품 정의 변경 없이 source recreation으로 자동 전환하지 않는다. 1200 바로 다음 slot을 시험 생성하거나 현재 save를 새 golden으로 승격하지 않는다.
