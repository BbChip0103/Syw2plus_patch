# G2 원본 서브시스템 통합 체크포인트

2026-09-17 20:19 KST, Sol/high 중간 검토 기록. 전체8인 전비5000 목표 ACTIVE/미완료.

## 현재 판정
바로 실행 가능한 일관된 서브시스템 구현 계약은 아직 확보되지 않았다. 원본 기반 서브시스템 통합은 방향이지 작동 후보/납기/실현 가능성 증명이 아니다. 빠른 주소 패치·생성기·fault/PC 예외는 중단한다. 원본919e 기반은 복구되었지만 launcher에서 차단 유지.

## 첫 일관된 산출물 — UnitStorage와 수명주기를 함께 통합
1. allocator442FA0, 생성443190→48B000, 등록48BC00, 제거/리셋442FE0/443170. 원본 ID generation·age 선택/wrap·active-last-slot 교환/backpointer·원가/owner bookkeeping를 보존한다.
2. owner43EE30/43EEC0 및 category add/remove, sector producer/reset/normal consumers. 실제 용량 정책과 원본 배열/WORD 폭에 근거한 geometry가 필요하다.
3. 모든 Unit 읽기/쓰기/포인터 생성 및 cached alias. 새로운 추론 주소 생성기나 관측된 getter만의 변경은 대체물이 아니다.
4. 버전 저장: BULK440C20/440FF0의 고정E397C 스트림과 Unit40F4B0/40F4F0의exists 기반758B 스트림을 함께 처리하며 load/rebuild 순서와 포인터 필드를 증명한다. Unit 바이트를 덧붙이기만 해서는 bulk index/counter가 복구되지 않는다.

## 열려 있는 위험
- 생성자의 TYPE별/다른 callee 연결과 제거 함수의 전체 부작용.
- 제거의active-list swap/backpointer, owner/자원/type 회계, category4A3620/3690, owner43EEC0와48C3E0/412D90/445A90 연결.
- spatial eligibility/225 bucket 및 pointer serialization semantics.
- 따라서 newgame41B9C0→4A3060 prefix-init hook이나 저장 wrapper 하나가 완성된 integration boundary가 아니다.

## 실제 게임 실행 승인 조건
검수된 원본 ABI adapter, 관련 모든 access/index transition, fresh/reset/load invariants, legacy-save 회귀, failclosed candidate gate가 필요하다. 그 후 소유한 원본/후보 비교, 확장 lifecycle/save/load 및24k/144k·지원LAN을 검증한다. 현재는 실행 승인 없음.

## 과도한 요구를 추가하지 않기
사용자 목표는8인 전비5000 안정 플레이이지 무료 객체 무제한 생성이 아니다. 원본 스타일의 명시적인 비전비 객체 제한을 유지하는 용량 정책이 적절한지 Sol이 별도 확인 중이다. 후보 정책은 기존owner1200 DWORD roster 및special8 headroom 유지, count_cap1200/ordinary1192, global9601(9600usable=8×1200). 아직 정책 승인/구현/실행 증거가 아니며 실제 초기화 writer·CPU building cap/5 sideeffect·zero-cost/reserved objects를 검수해야 한다. signedSHORT 및 memory geometry만 맞아도 전체 접근/저장/LAN의 정확성을 대체하지 않는다.

## 현재 검증
복구 wholeFast611 PASS/112.82초 및 모든 게이트·해시 통과. 실패 생성기619 PASS는 여전히 REJECT. 외부 TEMP/Syw2plus_patch에 정확한 소스·후보·로그·반례 보존. 원본/공유 DLL/control/bridge 입력 불변. 새 실제 gameplay0회.
