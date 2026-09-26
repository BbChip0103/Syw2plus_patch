# lap317 Astra — F1 한정 수리와 정적 연구 종료 조건

상태: 상위 방향 RECORDED / middle 독립 수용 PENDING. 계획 승인·제품 검증 아님.
근거: DESIGN §1~4, STATUS(lap316 원문 보존본), lap315/lap316 기록과 lap317 fresh 재실행.
실제 역할: Codex gpt-6-astra, Astra 상위 계획. 게임 코드·probe·테스트 구현 변경 없음.

## 결정 가능한 범위

1. M1/G1을 유지하고 lap316 F1만 다음 실무 변경으로 제한한다. 새 CFG 방식으로 이미 확인된
   R2 수치를 또 증명하는 작업은 새 실패 근거 없이는 추가하지 않는다. 정적 연구는 제품 진척 0이다.
2. F1 목적은 reset store의 전체 바이트와 연속성 증거를 보고할 수 있게 하는 것이다.
   원본 PE 직접 읽기를 우선 선택한다. 텍스트 줄 너비와 바이트 출처를 분리하며 원본 SHA,
   VA→raw 범위, 실제 길이 및 명령 경계를 검증해야 한다. middle은 이 방법의 수용/반려를 기록한다.
   objdump 연속줄 재조립은 PE 직접 읽기의 구체 부적합 근거가 있을 때만 대안으로 제안한다.
3. 기존 lap313~316 probe/report/test와 pin은 보존하고 새 probe와 별도 회귀 테스트만 만든다.
   N1(실제 간접분기 0)·N2(call 31개 미추적)는 명시적 UNKNOWN으로 유지하며 이번 수리에 포함하지 않는다.
4. F1 수리와 다음 새 middle의 독립 검수가 끝나면, 같은 R2 수치 재검증을 반복하지 않고 기존
   runtime 계약의 미제출 봉투를 문서 검토 대상으로 되돌린다. 이것은 미래 분기 조건이지 두 번째 활성 카드나
   실행 허가가 아니다. 현재 큐는 STATUS만 따른다. 근거가 부족하면 관측 필요 항목과 연구 blocker를 기록한다.

## work 인계의 입력과 수용 기준 (middle 판정 후에만 실행)

입력 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
입력 산출물 SHA는 `logs/lap317/before_sha256.json`; lap316 검수 재실행은
`logs/lap317/previous_review_recheck.json`(기존 report와 byte-identical).

| 항목 | 수용 조건 | 거부/중단 조건 |
|---|---|---|
| reset 바이트 | 0x4324B8에서 10B `c7051cbfe50080020000`, 0x4324C2에서 10B `c70520bfe500e0010000`; 주소·길이·출처·연속성 명시 | 부분 읽기, 경계 검증 없는 예상 바이트 하드코딩, 잘못된 원본 |
| 기존 불변식 | window/entry/failure/success=753/753/7/724, unresolved=0, writer=4, 실패 writer=0; gate/실패 arm E2 유지 | 수치 변동을 자동 재pin하거나 기대값 완화 |
| 정상 fixture | 7B+3B로 접혀 표시된 정상 10B 명령은 전체 바이트로 성공; PE 경로도 동일 값과 명령 경계 확인 | 정상 접힘 자체를 오류로 유지하여 수리라고 보고 |
| 부정 fixture | 선택 경로에서 누락·절단·주소 gap/overlap·범위 밖 읽기는 명시적 FAIL; 손으로 예상 가능한 최소 예제 | 소스 상수끼리 비교하거나 저장 report만 대조하여 알고리즘 검증 대체 |
| 검증 | 관련 targeted 회귀, make check, safety, 입력 SHA 전후 불변; 다음 새 middle의 독립 바이트/경계 재유도 | 예상 밖 필수 실패 시 재시도/마감하지 않고 변경 보존 및 ESCALATE_SOL |

lap316의 “접힌 명령 synthetic fixture가 fail-closed”는 **손상되거나 불완전한 수집**의 거부로 해석한다.
정상 접힘도 무조건 거부하라는 뜻이면 F1 수리 목적과 충돌한다. 따라서 middle이 이 해석을 명시 수용하거나
반려하기 전에는 구현하지 않는다. PE 경로를 택해도 명령 경계 검사를 버리고 raw 10B만 읽어 성공 처리하면 불충분하다.

## 역할·보류·종료

- 다음 새 middle은 위 결정별 ACCEPT/REVISE와 정확한 work 파일 범위를 기록한다. work는 Luna/Sonnet5/high,
  그 결과의 최종 기술 컨펌은 다음 새 middle에 둔다. 이번 세션은 다른 모델을 실행하거나 그 승인을 대행하지 않았다.
- MODEL_ROUTING은 middle=Opus5 전용, 상위 AGENTS/세션 지시는 Sol/Opus5 및 high를 적고 있다.
  `ESCALATE_SOL`은 사용자 요청의 표식 이름이지 provider 변경이 아니다. 기본 인계는 현재 문서의 Opus5/high로
  두되 승격 세션이 유효 지시와 실제 모델을 확인해야 한다. 설정/역할 불일치 시 몰래 폴백하지 않는다.
- W3 과거 review의 stale pin은 역사 실패로 보존한다. 이번 결정은 재pin/수리 승인도, 필수 게이트 면제도 아니다.
  W3를 다시 필수 게이트로 쓰려면 별도 명시 판단이 필요하다. 현재 F1 검증에 자동 편입하지 않는다.
- runtime/load 봉투, map↔dialog 순서와 실제 좌표는 미확정. Stage B/runtime/Wine/Xvfb/게임/PNG/클릭 예산은 0.
  제품 EXE/DLL/assets/baseline/golden 변경 금지, S1 종결 REJECT, G1~G4 미완료를 유지한다.
- 사용자 중단 조건에 따라 구현 기준 해석과 실제 실행 근거의 미확정 사항을 보존하고 ESCALATE_SOL로 인계한다.
  마일스톤 마감/이동 없음. exit0/Fast PASS는 상위 계획의 독립 승인이나 제품 완료가 아니다.
