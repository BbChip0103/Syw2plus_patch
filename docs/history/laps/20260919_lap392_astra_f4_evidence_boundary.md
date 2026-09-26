# 2026-09-19 KST | lap392 | G2 F4 근거 경계 / Astra handoff

- 실제 역할: Codex gpt-6-astra, 상위 방향/계획. 게임 코드 직접 수정 없음. effort는 이 세션에서 별도 측정하지 않음.
- 번호: 읽은 loop/.lap_counter=392. 사용자 runtime 헤더391보다 PROMPT의 파일값 규칙 우선; counter 쓰기0.
- 날짜: 실행 환경 date=2026-09-19T23:52:30+09:00. 이전 파일의 20260920 이름은 원문대로 보존.
- 목표/가설: lap391의 표본 음성 관측이 연속 시간의 흡수 불가능성까지 입증하는가.
- 합격식: 간격 내 사건 배제에는 (1) 패배 판정의 정확한 조건, (2) 패배 후 roster 양수 복귀 불가 불변식,
  (3) 해당 기간/모든 관련 owner에 그 불변식이 적용된다는 근거가 필요하다. 표본 최솟값만으로는 부족하다.
- 판정: **BLOCKED — 구현 근거 불명확. 사용자 중단 조건 발동, 재시도/제품 마감 없음.**

## 이전 바퀴 독립 문서/소스 검수

검수 대상 `20260920_lap391_middle_g2_ledger_wrap_review_acceptance.md`와 같은 이름의 `_probe.py`.
probe 149~158행은 표본 roster 최소가 0이 아닌지를 검사한 뒤 `cannot have fired between samples`를 출력한다.
169~177행은 같은 자료의 표본 간 사각을 인정하면서 D1이 배제한다고 주장한다.
이 소스에는 패배 판정/복귀 불가/흡수 발화 조건의 검사가 없다. 따라서 **수치 재현과 gap-proof 주장은 별개**다.
이는 실제 간격 내 패배나 랩을 재현했다는 뜻도 아니다. 해당 불변식이 원본에 있다면 별도 근거로 입증 가능하다.
과거 M1=0/M2=5003/전역합40000/위반7 수치는 이번에 재계산하지 않았고 원문 관측으로 보존한다.
W1 분석카드의 소비/종결을 되돌리지는 않되, NOT_FEASIBLE을 런타임 불가능성으로 사용하지 않는다.
F4 실제 도달성은 UNKNOWN이다. 전역합40000은 한 owner로 이전 가능한 경로의 존재증명이 아니다.
원본 cap1500×8=12000 역시 원본 생산/흡수/재생산을 모두 포함한 전역 불변량이라는 증명 없이
원본 랩이 원리적으로 불가능하다는 근거로 사용할 수 없다. 이 항목도 검수 대상으로 제한한다.

## 상위 방향과 middle/work 경계

G2 최우선, G1/G4 후순위, G3 중단 유지. DESIGN의 군대 혼합/풀/저장/지원동기화/24k/144k 조건을 줄이지 않는다.
F4는 전체 G2 합격기준의 대체물이 아니라 추가 안전 항목이다. (b) 생산 gate·장부 무결성을 검증하는
방향을 권고하되, (a) 초과 전비를 강제로 막는 정책변경과 장부 폭 확장 구현은 승인하지 않는다.
제품/마일스톤 승인과 기술 판정은 모두 미완료다. 통합 저장포맷/broad-patcher NO_GO 유지.

승격 middle(현재 MODEL_ROUTING의 Opus5/high; ESCALATE_SOL은 호환 파일명)은 다음을 한 번에 판정한다:
1. 원본 패배/흡수 조건과 패배 후 복귀 불가 근거를 주소/바이트/경로로 제시하거나 V2를 UNKNOWN으로 정정.
2. 원본cap1500 전역12000 상한 주장을 불변식으로 증명하거나 조건부 산술 예시로만 제한.
3. 기존 W1 재분석을 반복하지 말고, 안전한 정상 명령으로 원본 transfer/흡수를 유발하는 work probe의
   실행 봉투를 결정한다. 실제 run/새 fixture 자체는 INBOX의 G2 조사·재개 허가 범위이며 새 사람 허가를
   자동 요구할 사유가 아니다. 단 새 쓰기/직접 함수호출/기존 금지 계측은 자동 허용하지 않는다.
4. 다음 work는 원본 명령 경로·명시된 fixture·격리 복사본/prefix/display에서 실행하고,
   wide 비용합과 signed16 장부·원시word·소유자/roster·생산gate 전후·tick·풀/메모리·cleanup을 대조한다.
   장부값 직접 대입으로 랩을 만들거나 샘플 주기 단축만으로 연속 증명을 주장하지 않는다.
5. 한 work회차/60분/실패2회 중 먼저 도달하면 FEASIBLE/NOT_FEASIBLE/BLOCKED(적용 범위 명시).
   실제 이벤트 경로를 안전하게 만들 수 없으면 정확히 부족한 trigger/관측 수단을 blocker로 보고하고 끝낸다.
   FEASIBLE이면 다음 work는 곧바로 최소 제품 probe; 문서 회차 연쇄/동일 trace 재검수 금지.

본 세션은 충돌 발견으로 중단하므로 middle 호출·work 실행·게임/바이너리 변경을 하지 않는다.
현재 큐는 STATUS에만 둔다. 위 항목은 인계의 합격조건이며 병렬 활성 카드가 아니다.

## 보존 / 검증 / 한계

- STATUS 원문: `20260919_lap392_status_before_escalation.md`, 129줄, SHA256 `c6d5e691900bc0dd9c8efc05ec7b9028b002ff6c40638598e10d20246ad0b3a4`.
- source SHA: 원본 EXE는 과거 기록 b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac;
  이번 재해시 SKIP. 후보 없음. 환경/활성 인원/지도/군대/fixture: 신규 실행 없음, 과거9/19 trace 문서만 검수.
- 명령: cat/sed/nl로 PROMPT→INBOX/APPROVALS→STATUS 전체→DESIGN1~4→역할/이전기록/probe/주소문서 읽기.
- 루트 APPROVALS.md 조회는 경로 없음; 실제 docs/feedback/APPROVALS.md 읽음. 필수 게이트 실패가 아니다.
- 변경파일: 본 기록, STATUS, 보존 원문, loop/ESCALATE_SOL 추가, loop/FULL_TEST 요청.
- Fast: PROMPT④4에 따라 loop/FULL_TEST로 러너에 요청; 현재 미실행/미통과. 실제 앱 검증 SKIP.
- 문서 길이/섹션 확인은 별도 실행 결과를 아래 기록한다. 과거 make check715 PASS는 fresh 근거로 사용하지 않는다.
- 커밋0, 모두 uncommitted. 제품 변화0/새 실행0이므로 implementation streak를 리셋하지 않는다.
- 다음 행동의 유일한 큐는 STATUS 참조. 승격 후 위 근거 경계 검수 필요; 세션 STOP.

문서 구조 확인: STATUS 130줄(130 이하), Blockers 정확히1개 PASS. 초안 출력131줄은 검증 전 편집 중 길이이며 빈 줄 정리 후 확인.
