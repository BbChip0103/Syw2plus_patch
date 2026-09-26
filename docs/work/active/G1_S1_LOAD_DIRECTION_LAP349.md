# lap349 Astra — S1 결정성 해소 방향 / 로드 진입 근거 봉투

2026-09-12 / Codex gpt-6-astra / high / major direction/master-plan.
이번 결정은 M1 내부 방향이며 M1 종료·M2 이동·제품 승인·middle 봉투 ACCEPT가 아니다.
현재 큐는 STATUS에만 둔다. 이 문서는 후속 역할의 범위와 수용 계약이다.

## 1. 선택과 근거

**S1/F2-R2 결정성 해소를 선택한다. 첫 범위는 PS35 이후 슬롯 선택·로드 경로의 근거 확정이다.**
lap348 후보 R1 ACCEPT를 연구 입력으로 수용한다. 원본과 후보 각 n=1의 origin 일치는
저장 슬롯 선택, 실제 로드 완료, 모든 engine slot 동일성, 두 run 결정성의 증거가 아니다.
즉시 Stage B는 lap277 §3 (A)+(B)를 충족할 fixture 실행 근거가 없으므로 보류한다.
P6는 APPROVALS 2026-09-12 01:03 승인 범위 밖이며 착수하지 않는다.
WM_CLOSE는 후속 Stage B 선행 차단으로 유지하고 이번 로드 근거 카드에 수리를 묶지 않는다.

선택의 반증 조건: 보존 원본의 PS35 슬롯 처리 경로가 fixture 로드에 연결되지 않거나,
필요한 관측을 금지된 쓰기/디버거/무근거 좌표 없이 얻을 수 없으면 BLOCKED로 상위 반환한다.
origin 정적 CFG 반복이나 R1 같은 클릭의 반복은 로드 진전으로 세지 않는다.

## 2. 입력과 middle 산출물

입력은 lap348 기록/불변 probe/후보 raw artifact, lap333 제한, lap277 §3~3.2,
lap284 §10.1·§14.1·§14.3~14.7 및 후속 R1에서 실제 해소된 항목이다.
lap284의 오래된 'PS35/로드 경로 없음'을 현행 소스 사실로 복사하지 말고 현행 함수와 대조한다.

middle은 다음 표를 하나의 봉투로 제출하고 ACCEPT 또는 구체 BLOCKED를 판정한다.

| 제출 항목 | 수용 조건 |
|---|---|
| 미결 목록 | origin 관측으로 해소된 부분과 슬롯 hitbox/파일 선택/로드 후 상태 미결을 분리 |
| 슬롯 근거 | 원본 SHA·주소/폭·old bytes·원본 sprite/handler 근거로 슬롯 번호와 좌표 계산 연결; Plan C 제외 |
| fixture | save000/save006의 실제 SHA·격리 복사 경로·선택 이유 및 lap284 §14.1 미결 대응; 추측 파싱 금지 |
| 로드 완료 관측 | PS35 도달과 실제 파일 로드/복원을 구별하는 독립 reader·사건·오류/미도달 분류 |
| 실무 변경 | 현행 파일/함수·별도 연구 artifact·허용 입력/예산·회귀/실패 테스트·원복을 특정 |
| 제품 경계 | 연구 PS35→로드 관측을 기존 PS5→PS3 제품 PASS에 합치지 않음; S1 (A)+(B) 불변 |

이 단계에서 슬롯 hitbox 근거를 확정할 수 없으면 임의 클릭을 승인하지 않는다.
부족한 사실 하나와 이를 읽을 원본 파일/주소 창을 명시하여 work 읽기 전용 1바퀴로 반환한다.
새 조사에는 60~90분 또는 실패 가설 2회 상한을 적용하고 결과 없는 같은 정적 탐색 재발행을 금지한다.

## 3. 실행 발효 경계와 측정 기준

**이번 상위 결정의 게임 실행/추가 클릭/PNG 허가는 0회다.**
middle 봉투 → work의 승인된 최소 하네스 변경/검사 → 다음 새 middle 독립 검수 순서로 분리한다.
향후 실행 봉투는 실제 load의 시간·입력·좌표·종료 근거를 제출해야 하며, R1의 n=1 시간으로
load 예산을 추측하지 않는다. 연구 run 제안이 완성되면 상위에서 횟수/예산을 별도로 결정한다.
따라서 문서 ACCEPT만으로 두 run·원본 재실행·Stage B pair를 자동 발효하지 않는다.

후속 측정 대상은 **선택한 fixture와 실제 로드 완료 사건의 연결 + 복원된 scene 원시 필드**다.
성공 수집과 결정성 PASS를 분리한다: 단일 run은 수집 유효성만 판정하며 두 run 같음은 UNKNOWN.
최종 S1은 lap277 §3의 (A) comparator overall PASS와 (B) 여섯 원시 대조를 모두 요구한다.
결측·slot 불일치·nation/개체/카메라 불일치는 UNKNOWN/FAIL을 유지하고 tolerance로 덮지 않는다.
제품 tick의 동일 기준 사건/delta 및 허용오차 미결은 유지하며 연구 report-only를 제품에 적용하지 않는다.
WM_CLOSE 해결 증거와 fresh pair 검수 전에는 Stage B 완료·G1 합격을 선언하지 않는다.

## 4. 보존·중단과 역할

원본/과거 probe/실행 artifact/pin/reference/golden 수정 0. W3·A/C identity UNKNOWN·N14는 별도 미결 유지.
새 의존성, 게임 바이너리 수정, ptrace/int3/쓰기 계측, G2~G4 확대, 자동 커밋/모델 호출 없음.
필수 검사 예상 밖 실패·구현 근거 충돌·마일스톤 경계에서는 현물 보존→ESCALATE_SOL→종료한다.
이 문서 작성은 구현 진전 0이며, 반복 정체의 다음 측정량은 §3에 한정한다.

Astra는 방향만 정했다. middle은 이번 사용자 지시의 Sol/high 승격 경로로 인계한다.
MODEL_ROUTING.md의 Opus5-only 현재 선택과 다른 점을 공개하며 실제 후속 모델을 실행했다고 주장하지 않는다.
runner는 요청 역할/실제 모델을 기록하고 설정 불일치 시 조용한 대체 없이 반환해야 한다.
work는 Luna/high 또는 Sonnet5/high, 최종 컨펌은 다음 새 middle 세션이다.

## 5. 이번 입력 검수의 한계

불변 lap348 probe를 1회 재실행해 rc0/failures=[]; raw SHA·12표본·origin (240,145,8),
후보 artifact/lock 각 1건을 재확인했다. logs/lap349/lap348_review.json에 보존했다.
이는 기존 검수 알고리즘 재현이며 새 독립 알고리즘/새 runtime/결정성 검증이 아니다.
원본 source/private EXE SHA b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac.
후보 artifact SHA dd8cd3502edb66e08a1d2514cd8b4b26622da73531ca503adf2f3a6e71b37634.
