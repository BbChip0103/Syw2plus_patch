# INBOX — 압축 포인터

원문 347줄·SHA256 `54cd5fadcb4bf25151e9cb855a60e098ba81f4d68a1e72038868e73f96a6dc19`를 `docs/history/20261004_inbox_lap945_precompaction.md`에 byte-exact 보존했다. 이전 포인터와 계보도 원문에 포함된다.

## 상시 미결 지시 요지
- 구현 우선: 최소 근거 뒤 구현·빌드·격리 실행, 추적 가능한 결함은 수리 후 재실행. 묻지 말고 안전한 절차를 결정한다.
- 원본/참고/raw/golden/안전핀 보호, 격리 게임/prefix/display만 사용, 커밋·게시·deploy 금지.
- G1 달성까지 work·fresh 실행·수리·독립검수 자동 연결. G2/G5 종료, G3 중단, G4 보류 유지.
- 현재 세부 큐는 `docs/STATUS.md`만 따른다.
- lap944 승인 계약: `docs/work/active/G1_STRATEGY_W70_PRODUCTION_QUEUE_WITNESS_LAP944.md`; 다음 work는 생산 witness/control 수리와 fresh save006 pair.

- [x] **2026-10-04 사용자 최신 모델 지시:** “이제 돌리는 모델들에서 fast는 빼자” → “큰 방향/계획은 클로드 오푸스로 하도록 하자” → “그리고 코덱스 -> 클로드로 스위치 하자”. 다음 fresh 호출부터 전체 Claude: work=최신 Sonnet, middle/judge=최신 Opus, strategy=최신 Opus. 모두high·모델 Fast OFF·자동폴백 금지. 기존 Codex lap945는 게임/cleanup/check를 안전 종료했다. 설정·세 역할 command assembly 검증 완료(`logs/gates/20261004_claude_switch_argv.txt`); 실제 resolved ID는 새 호출 로그로 확인한다. `docs/MODEL_ROUTING.md` 최신 계약 우선; 약10분 보고·G1 자율 지속·기존 안전/검증/커밋금지 유지. 모델 Fast 해제와 검사 Fast=`make check`는 구분한다.

- [ ] **2026-10-04 사용자 신규 목표 G6·G7:** 혼자하기 대기실에서 방향키로 1P가 아닌 자리로 옮긴 뒤 (G6) Shift+클릭 선택 추가 불가, (G7) 타이틀 화면 불러오기 시 즉시 패배 또는 1P를 조종. 빌드는 G2 ESL2608+G5 이식판. 정적 분석상 둘 다 원본 결함이다. 근거·해결 방향·런타임 확정 절차는 `analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`, 목표 정의는 DESIGN G6/G7. 우선순위 미지정으로 G1 최우선 유지.

- [x] **2026-10-05 00:20 KST 사용자 최신 중단 지시:** “루프는 현 루프까지만 하고 중단해봐”. 현재 lap963의 이미 진행 중인 검사·기록·cleanup까지만 마무리하고 lap964 이상은 시작하지 않는다. root가 `loop/STOP`을 생성했다. 사용자 명시 재개 전 자동연결/STOP 해제/새 worker·review·strategy 호출 금지. G1 미완료·미커밋/실패/provenance 보존; 진행 중인 검사를 강제종료하지 않는다.

- [ ] **2026-10-05 00:39 KST 사용자 명시 재개 지시:** “루프 재개하고 10분에 1번씩 진행상황 보고해, 보고할 때 한국 시간도 같이 말해주고”. 00:20 중단 지시를 해제한다. root가 STOP을 지우고 work를 기동했으나 lap964 work가 재개 기록 부재로 ESCALATE_SOL 승격 종료. 재개 의사는 이 항목으로 확정한다. 다음은 문서대로 Opus middle 1 lap(lap963 H-E 반증 독립 재계산·H-E2 정의·`g1_mirror_replay_viewport` 유지/되돌림 결정) 후 work 자동 연결. root가 약10분마다 KST 포함 진행 보고.

- [x] **2026-10-05 사용자 디스크 정리 요청 처리:** 오래된 재생성 가능 캐시 약2.8GiB 삭제, completed private Wine prefix18개를 lossless archive·전파일/metadata·각 batch 첫 actual full restore MATCH 뒤 prefix만 정리. 여유11.24→21.71GiB(약10.47GiB 회수). 원본EXE/save SHA MATCH, raw/PNG/로그/manifest/output 보존, live lap864 및 현재 다른 세션 loop 비접촉. audit/복원 위치: ignored `local/maintenance/20261005_disk_cleanup_user/summary.json`·`report.md`(summary SHA256 4c85ef02e1dc1e2053a2cbe72a0b90a785e5ad056f23fd43355ae5d3668f8746). 과거 prefix 내부 경로가 필요하면 해당 archive에서 exact restore 후 사용; 기존 JSON 경로 변경0. 이번 작업은 루프 중단/재개 지시가 아니다.

- [ ] **2026-10-05 03:01 KST 사용자 우선순위 변경:** “G6 G7을 최우선으로 진행해보자. G1보다 우선으로”. G6(1P 아닌 자리 Shift+클릭 추가)·G7(타이틀 불러오기 자리 복원)을 G1보다 먼저 진행한다. 진행 중인 G1 lap975 middle은 마무리하되, 그 결과(H-W 검수·0x466070 미러 가설)는 G1 재개 시점으로 보류·보존한다. 다음 middle은 `analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`와 DESIGN G6/G7 합격 기준으로 첫 work 가설·원본/후보 재현 절차·사전등록 PASS/FAIL을 정의한다. 기존 안전/격리/커밋금지·G5 50 상한·G2 sidecar 비회귀 유지. DESIGN/AGENTS/CLAUDE 우선순위 갱신 완료.

- [ ] **2026-10-05 04:45 KST 사용자 답(G6·G7 자리 이동 방법):** “혼자하기 대기실에서 키보드 화살표 위아래로 자리 움직일 수 있더라고”. lap978 APPROVALS 질문 답. H-G6s는 대기실에서 **↑/↓ 화살표**(X11 키 Up/Down; 좌우·번호칸 클릭 경로와 구분)로 실제 1P가 아닌 자리를 만들고 `[0xB63FC4]` 변화·자리 패널 캡처로 확인한 뒤 원본·이식판·후보를 그 자리에서 재측정한다. 여전히 안 되면 키 전달 방식(포커스·keydown 유지·XTest vs SendEvent)을 의심하고 대체 경로 `0x4B7700`은 그다음.
  - lap981 처리 메모(원문 유지): H-G6k 결과 = 키 전달 BLOCKED(채팅 EDIT 포커스 유지). 방향키 직전 포커스 조작 확인 질문을 APPROVALS에 올렸다. 사용자 경로 동일성은 UNKNOWN이며 이 항목은 답 전까지 미처리로 둔다.

- [ ] **2026-10-05 08:41 KST root: G6·G7 시험판 사용자 전달 완료.** lap989/990 ESCALATE_SOL 처리: `260921_temp`에 일반판(`fb7c2131…`)·시작자리고정판(`58b9b22a…`)·안내문(`2145f0a9…`) 복사, 배치 후 SHA MATCH, 기존 파일 덮어쓰기 0. 사용자 합격 판단은 APPROVALS lap989 항목 대기(비차단). ESCALATE_SOL 원문은 `docs/history/laps/20261005_lap990_root_escalate_sol_g6g7_delivery.txt`에 보존 후 삭제. 루프 재개: 다음 work = STATUS H-G6f(시작자리고정판 G6 3회), 그 뒤 G1 H-F.

- [ ] **2026-10-06 01:43 KST 사용자 결정: G1 V2s W-1 채택.** "Scale2x로 설명되지 않는 단일 흑색 블록 ≤2,000"을 V2s gate로 사용하고 raw V2s는 공개 진단으로 계속 기록한다(APPROVALS lap962 항목 해소). 다음 middle이 gate 코드/aggregate를 W-1로 바꾸는 work를 사전등록·구현하게 하고(과거 pair-result 불변, coverage 축소 금지, V1/V2/V2q·tag 불변), 이후 pair 판정을 W-1 기준으로 재집계한다. 진행 중 H-O(우측 stale)와 병행 가능.

- [ ] **2026-10-06 19:31 KST 사용자 G6·G7 플레이 결과(최우선):** “G6 G7 해봤는데 선택 문제는 해결된 것 같아. 근데 세이브 로드 시에 제대로 안되는 것 같아. 첫 번째 자리 이외 자리를 고르고 시작했을 때 세이브 후 로드하면 또 첫 번째 자리에 있었던 컴퓨터 유닛/건물로 로드가 돼”. 추가 확인: **타이틀 로드·게임 중 로드 둘 다**, **일반판(fb7c2131…)·시작자리고정판(58b9b22a…) 둘 다**. 판정: G6 사용자 PASS, **G7 사용자 FAIL**. G1 큐보다 G7 재작업 우선.
  - 격리 측정(lap982~988)은 실제 ↑/↓ 경로가 아닌 lobby-snapshot 우회로 seat 2를 만들었다(↑/↓는 채팅 EDIT 포커스로 BLOCKED). 사용자 실경로에서는 세이브 스냅샷 `0x632F7C` 표에 사용자 자리가 없거나 다르게 기록돼 R4b가 local을 0으로 비운 뒤 1P로 귀결하는 것으로 의심된다. 특히 **게임 중 로드도 실패**한 것은 R4b(로드 시 local=0 후 재계산)가 원래 정상이던 인게임 로드를 회귀시켰을 가능성이 크다.
  - lap1090 middle 처리 메모(원문 유지, 미처리 유지): R4b를 사용자 실경로 FAIL로 철회하고, 실제 자리 결정 방식에 의존하지 않는 R5(저장 때 local·live 로비 표를 세이브 꼬리에 기록 → 로드 때 그대로 복원, 꼬리 없으면 무변화 → 인게임 로드 원래 동작 유지)를 사전등록했다. 다음 work H-G7s가 구현·격리 실행, 그 뒤 middle 검수 → 사용자 재시험. 카드 `docs/work/active/G7_MIDDLE_LAP1090_USER_FAIL_R5_SAVE_TRAILER_HANDOFF.md`.
  - 다음 middle: (1) 실제 ↑/↓ 자리 이동 경로를 재현(채팅 EDIT 포커스 해제 방법 재조사 또는 대기실 ↑/↓ 처리기 정적 분석으로 ↑/↓가 쓰는 표/필드 확정), (2) 그 경로로 만든 세이브의 스냅샷 표·플레이어 블록 파싱, (3) R4b 재설계(인게임 로드 무회귀가 필수, 표에서 못 찾으면 local을 바꾸지 않는 등) 사전등록. 시험판은 수정 전까지 사용자 합격 대상 아님.
  - lap1091 work 처리 메모(원문 유지, 미처리 유지 — middle 검수·사용자 재시험 전): H-G7s R5 구현·격리 실행 완료. W-1 진단이 R4b에서 사용자 증상(local 0·ps 27/29)을 재현했고 cand-r5(G6+R5)는 같은 주입 저장을 타이틀·인게임 로드 모두 저장 자리로 복원(S-1~S-8·fixed_start PASS, 기술). 실제 ↑/↓ 경로 재현은 W-3에서 BLOCKED 유지. 기록 `docs/history/laps/20261007_lap1091_work_g7_r5_save_trailer_hg7s.md`. 사용자 시험판은 middle 수용 뒤 스테이징.
  - lap1093 middle 처리 메모(원문 유지, 미처리 유지 — 사용자 재시험 전): H-G7s 독립 재계산 불일치 0·후보 SHA 4개 재조립 일치 → PASS(partial, 기술) 수용. 시험판 G6+R5 일반판 `b582fb19…`·시작자리고정판 `acf5bd3d…`를 공유 temp `20261007_lap1093_middle_review/user_test_staging/`에 스테이징, APPROVALS lap1093 재합격 요청, root 전달은 ESCALATE_SOL. 기록 `docs/history/laps/20261007_lap1093_middle_g7_hg7s_acceptance_user_retest_request.md`.

- [ ] **2026-10-06 21:11 KST root: G7 R5 시험판 사용자 전달 완료.** lap1093/1094 ESCALATE_SOL 처리: `260921_temp`에 일반판(`b582fb19…`)·시작자리고정판(`acf5bd3d…`)·안내문(`3f5622c9…`) 복사, SHA MATCH, 덮어쓰기 0. 사용자 재시험은 APPROVALS lap1093 항목 대기(비차단). 원문 보존 `docs/history/laps/20261006_lap1094_root_escalate_sol_g7_r5_delivery.txt`. 루프 재개.

- [ ] **2026-10-06 21:21 KST 사용자 결정: G6·G7 달성·종료.** “해보니까 G6 G7 해결된 것 같아. README.md 도 업데이트 하고 이 시점에서 푸시 함 날리자”. R5 시험판 기준 사용자 합격. G6·G7 작업 큐 종료, **G1이 다시 최우선**. root가 README 갱신·커밋·푸시를 수행했다(사용자 명시 지시; 루프 자체의 커밋 금지는 유지). G6·G7 새 결함 보고 없이 자동 재개하지 않는다.
