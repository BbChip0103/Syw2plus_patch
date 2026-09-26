# lap106 — G1 presentation 조사 범위 재설정

상태: Astra 상위 방향 결정 / middle 검토 대기. 계획 승인·실구현·G1 검증 통과가 아니다.
근거: `docs/DESIGN.md` §1~4, `docs/MODEL_ROUTING.md`, lap73/104/105 원문.
현재 실행 큐는 `docs/STATUS.md`만 따른다. 아래 단계는 조건부 handoff 계약이다.

## 판단과 우선순위

M1/G1을 유지하고 M2로 넘기지 않는다. 한 가지 가설은 “원본의 실제 최종 출력 경계와
그 입력 좌표 관계를 관측하면, 원본 구도 보존 정수 2배 출력의 최소 변경 위치를 결정할 수 있다”다.
G2~G4 요구는 유지하며 이번 범위에서 새 작업을 활성화하지 않는다.

lap105는 주소·개수에 대한 정적 관측과 presentation 의미 미확정을 보고했다.
이번 세션은 원문 간 계약을 독립 대조했으며 바이너리·49/14 개수·runtime을 재현하지 않았다.
따라서 기존 수치는 역사적 보고이며 새 CONFIRM PASS가 아니다. lap73도 desktop 1600×1200과
content/surface 800×600을 구분하고 required_inputs FAIL을 기록했다.

기존 handoff에는 두 문제가 있다. 첫째, 실무 runtime trace를 Astra에게 맡기는 것은 역할 계약과
충돌한다. 둘째, 원본에 이미 목표 destination 1600×1200 경계가 존재해야만 조사 PASS라는 기준은
목표 변경과 현재 동작 식별을 혼합한다. 원본에서 그 경계를 찾지 못했다는 사실만으로 2배 출력이
불가능하거나 외부 wrapper가 필수라고 결론 내릴 수 없다. 대안 구현을 지금 확정하지 않는다.

## Middle — Sol/high 검토 산출물

새 중간 세션은 위 판단을 ACCEPT/REVISE/BLOCKED로 명시하고, 근거와 남은 위험을 기록한다.
ACCEPT는 아래 work 조사 카드 허용만 뜻하며 patch·M1 승인과 구분한다.

- 입력: 두 고정 원본 경로와 SHA, lap73 manifest/모듈/scene 증거, lap105 후보 주소 원문.
  경로·SHA·실제 모델 확인 실패는 BLOCKED다. 과거 prefix/display에 붙지 않는다.
- work 카드에는 사용할 기존 계측 도구/명령, 읽을 surface·rectangle·호출자 필드,
  실행 상한, 로그 스키마, cleanup 증거를 먼저 고정한다. 계측 가능성을 근거 없이 가정하지 않는다.
- 기존 도구로 관측할 수 없으면 누락 기능과 필요한 최소 하네스 변경을 별도 work 범위로 적는다.
  관측 도구가 없는 채로 게임 실행부터 반복하거나 새 의존성을 전제하지 않는다.
- 원본 주소는 검증 후 `analysis/memory_maps/`에 SHA·old bytes·출처로 고정한다.
  vtable offset 숫자만으로 interface나 최종 출력 의미를 확정하지 않는다.

## Work — Luna/high 단일 관측 카드의 성공·실패 기준

middle 검토 후 새 work 세션에서만 수행한다. 게임 패치·후보 생성은 별도 후속 승인 카드다.
두 고정 원본 SHA는 역사적 기준
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이며 재검증해야 한다.
입력 위치는 lap105 원문을 사용한다. 필요한 경우 새 전체 복사본/private prefix/빈 display에서
한 번의 제한된 scene을 관측한다. 최초 조사 60~90분 또는 실패 가설 2회 이전에 재평가하며,
필수 게이트의 예상 밖 실패는 첫 실패에서 중단하고 ESCALATE_SOL로 보존한다.

측정 기록은 동일 run ID/frame 또는 timestamp로 다음을 연결해야 한다.

1. 실제 interface/object identity, 생성/보관 위치, surface 역할·크기, 선택된 출력 mode.
2. 실행된 호출 주소/호출자와 source/destination rectangle의 실제 값 또는 생략 여부,
   관련 writer/argument provenance. 복수 출력 단계라면 각 역할과 최종 표시까지의 관계.
3. 해당 scene 캡처와 실제 client/output 크기. desktop 크기를 content 크기로 세지 않는다.
4. 관측 방식·계측 부작용·fixture 여부·명령·로그 해시·프로세스 종료/cleanup.

조사 PASS는 관측한 mode/scene에서 실제 최종 출력 경로와 인자 provenance를 구분할 수 있는 것.
원본 출력값이 800×600이어도 가능하다. 선택된 mode의 복수 단계를 설명할 수 있으면 전역적으로
단 하나의 호출이어야 한다는 조건을 부과하지 않는다. 이를 다른 mode 지원으로 확대하지 않는다.
주소와 실제 화면을 연결하지 못하거나 도구가 값을 수집하지 못하면 UNKNOWN/BLOCKED로 남긴다.
단순 generic 후보 개수 재집계는 측정 진전으로 세지 않는다.

## 후속 결정과 제품 검증 경계

work 결과는 다음 새 Sol/high 세션이 원시 증거로 독립 검수한다. 확정된 출력 경로에 따라
정수 2배 적용 위치·입력 역변환·창/전체화면 정책·old bytes/원복/버전거부/범위 회귀를
별도 최소 변경 카드로 작성한다. 외부 wrapper나 여러 mode 변경이 필요하면 Astra로 범위를 재이관한다.

G1 합격 기준은 계속 동일 상태 800×600 기준 대비 실제 1600×1200 content, UI/월드 구도와
클릭 대응, 선택/드래그/미니맵/메뉴/정상 생산 5입력이다. 현재 primary production 의미 blocker는
별개로 유지한다. 우회 명령·fixture로 정상 생산을 대신하지 않는다. PNG는 지정 공유 temp에
시간 접두사로 두고 SHA를 기록한다. Fast와 실행 증거, 모델 컨펌과 사용자 마일스톤 판단을 분리한다.
이 문서 작성은 implementation progress가 아니다. 다음 실무 진전은 위 provenance trace 또는
그 수집을 막는 구체적 도구/권한/경계 증거로 측정한다. 같은 후보 나열만 반복하지 않는다.
