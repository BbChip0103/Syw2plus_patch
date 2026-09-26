# G2 원본 전비5000+개인 개체1200 — cap-only 공학 검증

2026-09-17 20:43 KST. **공학 GO만, 게임 실행/8인 안정성 승인 아님.**

## 변경
새 `patches/population/fixed_owner_count_1200.py`는 기존 fixed_supply_5000 유틸을 재사용하고 원본b569에서만 복사본을 만든다.41B56D MOV EDX,250의imm32를1200으로 바꾼다. 총7 actual changed bytes(개인 개체2+전비5), 동일 크기1,032,192B. Unit/allocator/roster/headers/나머지 원본 bytes는 전부 그대로다. 새로운 생성기/Unit relocation/데이터 구조 재작성/의존성 없음.

## 검증
- Root 독립 literal3개 명령/7byte whitelist/전체 나머지 동일/원본 backup 확인.
- source74fcd15d413c9ec01429a10cad33d1c7692a365475f09f96bd5df3020eeb37ad.
- test86b7ab834d7b8bd09afef09aff8fa4ba05817513664688bd18fba95b92af06c5.
- candidate607485871d6e112354e97d49c96d419a6486d52bcef52617cfd76bda13e2f49b.
- fresh전체621 PASS/115.09초·Ruff/compileall/표준mypy10+명시1/context/shell 및6소스 전후/4보호입력해시 PASS.
- Sol 독립10개 갱신 테스트 및 실제 후보의 canonical/legacy 실행차단 0subprocess/0output 확인.
- RAWvalid100×100 경로에서 EDX 낮은16bit는4513B0 첫 명령에 덮어써지며 높은16bit는 이전/후보 모두0이다.451C10 및451130 선행 경로도 검수. 크기오류465250·다른모드 제외, 포괄 ABI 증명 아님.
- 선택한 정상 생산47F400:43EDA0 selector결과0이면47F5B5TESTDI/JE47F7E2 epilogue로 가서 자원/예약 감소와 생성443190를 건너뛴다. 생성443190 자체에slot0 guard가 있다고 말하지 않는다.
- 외부 `reviewer_cap_engineering_preflight.json` SHA8c87a65d7a44aeb5aeab4fb4a9182fa1de81bd7522531ea0d7ddc66f7c453410.

## 외부 재현/보존
`/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260917_owner_count_capacity_policy_v1/candidate_v1/`에 실제 EXE/원본backup/manifest/recipe/전체로그/6source frozen bundles v1,v2/Rootaudit 및 `root_cap_engineering_verification_v2.json`을 보존했다. 테스트 갱신으로 이전 manifest test SHA가 바뀐 후 원본4600 hash 바이트를 정확히 복원·검증했으며, 사전 복사가 아닌 복구였다는 receipt를 명시했다. 모든 전체 G2 contract false.

## 위험/다음 단계
- 기존 global pool은1199 usable 그대로. 이 후보로8인 저비용 대군을 생성하지 않는다.
- count1200→normal1192는 예외 count headroom8을 유지한다; 특수유닛 최대8이라는 뜻 아님. CPU building threshold50→240 행동/성능 부작용 있음.
- reset/load/다른모드 및 확장 저장/LAN 미검증. oldsave 로드시 저장된250 제한이 복구될 수 있다.
- 별도 TYPE7-only private fixture가 actual baseline→count240을 원본 생성으로 보조 구성하고 HQ49 정상 생산241→242→243을 관측할 계획. 보조 구성은 organic 생산 증거가 아니다. Train4AF5E0의return1은 queue admission 증거가 아니므로 다음원본tick의동일HQ/fullID/type7pending/reserved 원가 확인 필요.
- private C/DLL/runner의 literalpins/profile100map/poolbudget/원가배치/ID경제/소유prefix cleanup 및 최종 검수 후에만 해당 부분 검증 실행을 고려한다. 준비부터 cleanup까지20:40→21:10/가설2회 한도. 현재 게임 실행0회.

전체 목표8인 각각 전비5000 안정 플레이는 ACTIVE/미완료; 큰 UnitStorage 수명주기/owner-spatial/allaccess/직렬화 통합 및24k144k/지원LAN이 남았다.
