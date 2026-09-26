# G2 저전비 정상 생산 fixture — REJECT / STOP

2026-09-17 20:59 KST. 두 버전 모두 미실행이며 전체 G2 목표는 ACTIVE/미완료다.

## 실행하지 않은 이유
v1은 연결되지 않은 callback abstraction/항상profile_pending handler였다. 배치 전 Spawn·고정xy·snapshotcount240상한·원본tick 없는Train loop·EXE/DLL pin혼동 및 미획득 검수true가 있었다. Root/Sol가 실제 소스로 거절했다.

한 번 수정한v2는 real poll의op7을 구현했지만, blocked Place시 fixture_added가 바뀌지 않아 같은xy를 무제한 다시 시도한다. 따라서 original mainthread hang 가능성을 정적으로 확인했다. 기존op6 relocation/ops2,3 save-load/op4ledger writes도 남아 제한된fixture 계약 밖이었다. prelaunch는 prepare-only였고 실제 ownedlauncher/숫자8필드request/원본tick collector/cleanup pair가 없었다. witness validator는 가짜level241..250을tick/원가/신규ID 없이 승인하면서 정상Trainreturn1은 거절했다. Root호스트 반례로 직접 재현했다.

## 판정
- private fixture 분기 STOP, 세 번째 수정/다른 모델 재시작/가설 예산 리셋/21:10 연장/추가 진단 게임 없음.
- 두 실패는 하네스 구현의 실패이며 게임에서5000 안정 플레이가 실패했다는 실측 결과가 아니다.
- 원본cap-only 후보6074/7byte621Fast 공학 검증은 유효하지만242 경계 통과조차 아직 게임에서 관측하지 못했다.
- 전체8인5000 가능/불가능 판정은 여전히 미확정.32bit/OOM 불가능 주장은 없다.

## 증거 보존
외부 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260917_owner_count_capacity_policy_v1/`:
- `cheap_fixture_v1/root_rejected_private_fixture_v1.json` 및 원본source/DLL/manifest.
- `cheap_fixture_v2/root_rejected_private_fixture_v2.json`: actual pins·정적위험·호스트 validator 반례.
- `root_private_fixture_stop_receipt.json`: 두 버전 전체source/DLL pin 목록, 실행/소유prefix deployment없음, cleanup필요없음.
- 최종원본/sharedDLL/controlC/popbridge4핀 불변; cap74fc/test86b7/offlinebasee9d845/051bf도 확인.

## 큰 방향 판정
Astra/medium `20260917_g2_post_fixture_provider_decision.md`: 새 자동 구현 카드 NO-GO. Sonnet5는 사용자가 이미 허용했지만 모델 변경이 종료된카드 예산이나 미확정통합 경계를 초기화하지 않는다. 실제 첫 UnitStorage 통합은 생성/등록→실패복구→첫정상simulation소비→제거/재사용을 함께 닫아야 하며 현재 닫히지 않았다. 성공 가능성/기간/당장 구현GO를 꾸며내지 않는다. 더 긴 원본 서브시스템 재구현은 가능성 미확정의 장기 방향이지 새 엔진으로 슬쩍 바꾸는 허가가 아니다.

현재 빠른 자동코딩 루프는 중단한다. 제품 목표는 완료하지 않고 내부 구현 미해결로 유지한다. 외부 권한 blocker로 바꾸지 않는다.
