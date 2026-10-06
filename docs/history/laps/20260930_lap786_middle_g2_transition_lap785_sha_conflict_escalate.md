# 2026-09-30 | lap 786 | 목표 G2 전환 / lap785 독립 검수

- 실제 provider/model/effort / 지정 역할: Codex native 세션(실제 model ID·effort 비노출) / middle tier 진단·계획·확인; 게임 코드·EXE hands-on 수정 금지.
- 가설 / 사용자 관찰: 최신 지시는 G1을 보존·일시중단하고 ESL2608 G2 두 EXE의 paired 체크리스트 점검·수리·새 이름 배포를 앞당긴다. 먼저 이전 lap785 G1 raw/source를 독립 확인해야 한다.
- 예상 PASS / FAIL 조건: lap785 기록의 raw SHA·validator 수치가 실제 파일과 일치하면 G1을 paused/HOLD로 보존하고 G2 work 카드로 전환. 기록과 raw가 다르면 즉시 `loop/ESCALATE_SOL`을 만들고 G2 실행 승인을 보류.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 이 기록, `loop/ESCALATE_SOL`, `docs/STATUS.md`만; 검사 전 fingerprint `f4b21aadc5ee92089f9b4cd09dca3c884d161d19`; 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: lap785 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; preserved OFF/ON fresh private evidence only. G2는 파일 해시만 읽기 확인했으며 실행하지 않음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`으로 lap785 raw와 G2 baseline/candidate를 재확인; ON 보존 verdict/trace를 `jq`와 validator source로 대조. 수동 validator에 PNG를 capture JSON 대신 준 첫 호출은 UTF-8 거부되어 폐기했고, 보존 verdict의 validator PASS를 사용했다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **FAIL(record provenance)** — OFF raw 실제 SHA `8798fafb8e199b8d7c553f4a42d505d9b60c02551b3a6a737a27cb05414b133b`, lap785/STATUS 기록 `...133`(마지막 `b` 누락). ON raw SHA `d3bc54cfae9d04edca2569a04af54e7700ea809854b5d06f91f4229350be74cc`는 일치하며 preserved validator는 PASS(1672 events, converted246 PS3/5/7/9, mirror546, oracle1.0, dropped0, cleanup PASS), production UNKNOWN으로 overall BLOCKED.
- G2 입력 확인: baseline 일반 `cade60b2…b176a3`/고정 `f5f816ee…ee1973`, 후보 일반 `83c7df80…1fad60`/고정 `1bdcadf9…49262f`가 사용자 지정 경로에서 재확인됨. 과거 Shift 단일추가와 생산·save/load PASS는 이번 전체 체크리스트 완료로 승격하지 않음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: raw 본문 변화보다 1글자 전사 누락이 유력하나, 명시적 raw-vs-record 충돌 중단 조건 때문에 G2 work 실행·G1 production 판정·마일스톤 승격을 하지 않았다. 제품/하네스/EXE 변경 없음.
- 다음 한 가지: 승격 작업자가 OFF raw를 재해시해 전사 오류만인지 확정·기록 정정한 뒤, `loop/ESCALATE_SOL`의 단일 G2 work 카드를 Luna/Sonnet tier에 넘긴다.
