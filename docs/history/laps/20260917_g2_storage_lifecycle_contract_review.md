# G2 storage/lifecycle — 22:26 이후 읽기전용 조사

## 범위와 한계

원본 PE SHA `b56986e0…a8ac`. native 실행/빌드/패치/소스 수정 없음. 이전 STOP 실험의 추가 수리나 실행이 아니다. 첫 산출물의 오류를 발견해 원문을 외부 보존하고 최초15분 안에서 증거 erratum을 요청했다. 아래는 selected raw 검증이며 전체 참조/CFG 폐쇄가 아니다. 전체G2 미완료·00KST 상한 유지.

## 확인한 관계

- BULK `0x892410..0x975D8C`, 길이 `0xE397C`. 초기화4A3060의 bounded 세 호출자는 ECX892410을 주며 이 블록을 zero한다. old 존재/age 배열은 각각 bulk+6CB8/+7618에 있어 초기화·원본 raw 저장 블록에 포함된다.
- owner/type WORD matrix `0x89A388..0x89B008`=8×200×2B. categoryA/B는 각각1200개 DWORD fullID와 WORD count로 이어진다. 단순 uniform tail 이동만으로 배열 길이가 늘지는 않는다. absolute 주소와 ECX-relative alias를 함께 다뤄야 한다.
- categoryB 제거4A3690는 Bcount로 검색하지만 Acount(BP)로 copy source를 잡는다. 원본 raw 동작을 대칭적인 last-B compact로 바꾸어 해석하지 않는다. 수정v2의4A36DF annotation에는 여전히 generic count 표현이 남아 qualification이 필요하다.
- 441441는444140 함수가 아니라440FF0 load 내부의 `CMP BX,1200`. 기존 Unit import/export 및 post-load Unit 참조 loop1200 경계가 함께 변경돼야 한다.
- PlayerStruct `0x956770+p*0x3ABC`, p=0..7, 끝973D50. 이 블록이 rawBULK에 포함된다. 각 진영 roster는 **PlayerStruct+D4A..200A**의1200 DWORD이며 bulk+D4A가 아니다. COUNT200A/USED200C 등도 같은 진영 구조에 있다. 수정 persistence artifact의 base 불명확한 문구는 승인하지 않는다.
- 새 배열을 외부로 빼고 old writer 길이E397C를 그대로 두면 확장 데이터는 저절로 저장되지 않는다. 별도 stream 또는 coherent repacked/versioned bulk는 설계 선택이며 원본 EXE가 읽을 수 있다는 증거는 없다.
- allocator442FA0는 signed WORD age 비교·free age 증가를 한다. all-free 상태에서 등록 없이32768회 호출하는 CPU 입력모형의 false-exhaustion은 정상 gameplay 도달/OOM 증거가 아니다. register48BC00와 occupied removal442FE0는 age를0으로 reset한다. 실제 모든 생산/free 경로의 invariant와 fullID generation 계약은 미폐쇄다. unsigned age 패치 없음.

## 전비 초과 관측과 native transfer 정적 관계

Root가476ED0/43EE30의 원본 raw를 독립 확인했다. 이 경로는 old roster 제거, owner+8E 변경, new roster 등록/TYPE비용 USED+200C 증가 및 생산자+50C 예약량의 OLD/NEW+1C 이동을 수행한다. 43EE30의 직접 admission은 rosterCOUNT<1200이며 해당 함수에 supply-cap 비교가 없다. 이 정적 경로는 같은fullID owner3→1 및 USED+10 관측과 양립하지만 **실제 그 함수를 호출했다는 동적 증거는 아니다**. 원본 규칙 예외/패치버그를 단정하지 않고 강제 전비보정도 하지 않는다.

## 검증과 증거

외부 root `temp/Syw2plus_patch/g2_capacity/`:
- bulk v2 `20260917_bulk_relative_sidecar_contract_v1/bulk_relative_sidecar_contract_v2.json` SHA `9b0e4f98…926a`; Root16개 operand oldbytes/VA/length 독립 일치. 원문885e 보존.
- persistence erratum `20260917_native_persistence_contract_v1/contract.json` SHA `b84aa478…88e0d`; 원문1420 보존. source/annotation 일부 qualification은 Sol 별도 검수 대상.
- age erratum `20260917_allocator_age_contract_v1/allocator_age_contract_corrected.json` SHA `50906c22…d210`; 원문c001은 원래 오경로와 지정경로의 byte-identical copy 둘 다 보존.
- Root raw `20260917_root_static_contract_verification_v1/raw_ranges.json` SHA `d8d3d246…8395`, findings `d2a94e6e…d68f`.

보호 소스6efd/test722·공유DLL a538/native C e50a/0eed 그대로. Root context_limits PASS. fresh Sol/high 검수는 기술사실과 남은 통합 요구를 구분하며 implementation GO를 자동 부여하지 않는다.

## 22:39 Sol/high 검수 결과
외부 middle_review_v1.json SHA10574856931af4b5470f792682c989c6ff458a1512622892c859e0ff2ba41780. selected 사실만 조건부 채택, full storage integration/runtime GO 없음. 추가 annotation 오류: stream40F4B0/F4F0 RET4이므로 cdecl 표기 불채택; remove의66B94C는 Unit+1BC이지Unit+B94C 아님. age CPU40000 모델은 script/log 미제공이므로 조건부 수학모형으로만 해석한다. 원본32비트 불가능/OOM 주장 없음.

## 마지막 질문
Astra/medium 결정 remaining_capacity_question_decision_2242.json: zero-cost 출력 한 개의 원본 생산→반복/동시보유 연결을22:57KST까지 한 번 확인. 닫히지 않으면 UNKNOWN 그대로 종료. 이미중단한 실험과시간예산 재개 없음; 어떤결과도9904 용량/새게임 승인으로 쓰지 않는다.
