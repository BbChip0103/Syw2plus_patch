# G2 — 8人各전비5000: 현재 재배치 분기 종료 판정

판정 시각: 2026-09-17 18:32 KST. Astra/medium 큰 분기 판단; Sol/high 실제 raw 검수 CONFIRM. 전체 G2는 미완료다.

## 제품 목표와 확인된 부분
사용자 목표는 실제 8인 각각 전비 상한5000에서 임의의 합법 유닛 구성으로 안정 플레이하는 원본 기반 버전/패치다. 단일 프로세스 8슬롯이나 숫자 상한만 올리는 것은 완료가 아니다.
- 보조 생성한 고비용 구성: 실제 1160개체, 각 145개체/USED5000 관측.
- 같은 구성의 정상 저장 및 별도 fresh 프로세스 로드 관측. 기존 풀 범위의 부분 성공이다. owner4 예약10/생산progress100 대기는 남아 있어 정상 생산 완료 증명은 아니다.
- 저비용 다수 구성, 풀/owner 한계 확장, 자연 생산·전투·사망·재사용, 확장 저장, 지원 LAN, 24k/144k 장기 검증은 아직 미완료다.

## 마지막 실제 실행 — 실패를 성공으로 승격하지 않음
동결 소스에 fresh Fast 575 passed 및 Ruff/compileall/standard mypy/context/shell 검증 후 private 실제 실행 1회.
- DLL SHA256: 71244523c24dcfe5986929a1ccb580e377f895e5de1355ccdd91614b3cfd541f.
- 기존 47 + accessor/wrapper 73 = 고유 120 fixup 모두 적용 확인. 원본 8슬롯 초기 16개체의 ID 기록.
- six arena 복사/비교/zero tail 확인, native stage5. copy tick13→13.
- 첫 AV: PC 0x4178C1, read BYTE EA 0x88C526. 원본 PE/레지스터 계산상 old Unit[1187]+0x8E owner 읽기.
- progress POD 전부0: 재배치 후 256 advancing tick 증거 없음. 정체성 지속/정상 simulation 성공 없음.
- cleanup_ok=true/errors=[], 소유 prefix 잔류0, original/shared/canonical 입력 변경 없음.
- raw4096 SHA256: 5cd775f5b941ab13f1fc1346f3077c663bc8c92b3d96f8905c11e5356effbdaa.
- 실제 오류 주소의 해석은 확인됨. 독점 원인, 전 소비자 closure, 무결성/메모리 안전성은 증명되지 않음.

## 방향 판정
현재의 작은 주소/상수 패치를 순차 추가하는 binary 재배치 분기는 NO-GO로 종료한다. 다음 PC 수정, 새 getter군, 세 번째 guard 재실행은 승인하지 않는다.
전 코드의 명백한 slot×1880 참조를 typed 자동 변환하는 도구는 가능하나, 이미 전달된 포인터/다른 표현/alias/보조 인덱스/고정 직렬화/LAN 계약까지 닫는 충분조건은 아니다. 적용 뒤 첫 fault를 다시 잡는 방식으로 전환하지 않는다.
필요한 다음 수준은 Unit 저장소·소비자·인덱스·직렬화의 일관된 구조적 통합 구현이다. 현재 저장소에는 생성부터 정상 simulation까지 이를 닫는 구현 계약이 없으며, Astra는 60분 내 제품에 의미 있는 안전한 확장 실행 카드를 승인하지 않았다.

## 결론의 경계와 재개 조건
이는 현재 구현 경로의 blocker이며 게임 전체 불가능 판정이나 실제 OOM 관측이 아니다. 32비트 자체가 불가능 원인이라고 단정하지 않는다.
G2 우선순위와 목표는 유지한다. 실행 재개에는 전 소비자/alias 및 초기화·수명주기·인덱스·저장·지원 동기화가 연결된 구현 계약과 관측 계획이 필요하다. 보조 고비용 구성 제한을 완성품으로 제시하지 않는다.
목표 complete/blocked 상태는 변경하지 않는다. OMX mode discovery active_modes=[]; 취소할 활성 OMX 모드 없음. 마지막 소유 게임 실행은 이미 종료/정리됨.

원시 부산물: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260917_six_arena_closure/family_accessor_card_1800/official_family_owned_1825/
root_family_fault_observation_report.json 및 g2_relocation_fault.bin. 원본/메인 RE 레포에 캡처 부산물을 넣지 않음.

18:32KST Sol/high 최종 판단 검수: 결론 타당, 즉시 승인할 명백한 대안 없음. 구조통합 필요는 판단/추론으로 구분; 기존1200풀 save/load 관측 성공은 유지하며 확장 저장은 미완료로 구분한다.

## 18:38KST — 원본소스 재빌드 대안 실측: quick route NO-GO
Luna/high bounded read-only audit와 Sol/high 실제source독립검수 CONFIRM. 현재 decomp/cleaned에는 생성 및 배열 선언이 있지만 단순 재구성 로직과 sidecar scalar stubs가 남고, network_init/network_timeout/network_tick·multiplayer·load-state는 DEFERRED 빈stub다. 공개serializer는 재구성 전용SYW2이고 실제original save witness(first4c8a5c0da)와다르다. RawGhidra original40F4B0/40F4F0/440C20/440FF0분석은 존재하므로 원본serializer분석없음이라고하지않는다. 이들을coherentoriginalbuild로연결한source-ready 경로는미확인이다.
이번조사에서freshcompile/게임실행을하지않았으므로컴파일/원본동등성을claim하지않는다. savegame.h의'원본slot저장없음'주석은actualsave001와충돌하여근거에서제외한다.
외부evidence JSON source_feasibility_evidence.json SHA b6aed218177fb9f032f274e3cf83b58752167e28a1df8f337670469baf602875와현재sourcehash들을Root확인. 기존source를원본재빌드로오인하여배열크기만바꾸는선택을제거한새진전이다.
다음Astra큰분기판단은 runtime再배치가아닌pre-launchoffline whole-storageintegration이 coherent actualpatch 경로인지이다. 기존PC별patch/세번째guard는여전히금지; 새로운구현/실행승인을추정하지않는다. FullG2active/unfinished.

## 18:40KST — 후속 구조구현 GO (실행 GO 아님)
Astra/medium은 원본패치 목표를 유지하며 시작 전 offline PE storage integration을 승인했다. 현재 사용자권한은 충분하며 구현결손은 외부권한blocker가 아니다. 첫30min카드는 신규원본SHA-pinned PE 저장section/ABIv1-sixarenas/engineering4001과 이미검수된allocator+typed주소operands를실제private후보EXE에적용하고 정확한restore를검증한다. 기존initializer/consumer/owner/spatial/save/LAN은미완료로유지하고launcher가거부한다. Sol/highmiddleGO, native/parentLuna작성자분리. 이카드는이전getter/guard분기재개아니고 제품완료나전체가능성증명아니다.
