# Syw2plus_patch — 원본 확장 패치 루프 계약

## 제품 / 기억

상세 목표는 **docs/DESIGN.md**가 유일한 제품 계약이다. 현재 활성 목표는 G1 원본 구성1600×1200(단순확대 화질 열화 허용), G2 활성8인 각각 전비5000 안정성,
G4 길찾기/자유대전AI 난이도 개선이다. G3 최대16인은 2026-09-17 사용자 지시로 중단한다. 기존 단일플레이어/QHD 증거를 완료로 쓰지 않는다.

구조는 형제 Syw2plus_re_loop의 **매 바퀴 새 세션, 기억은 파일** 방식을 따른다.
`loop/PROMPT.md` → `docs/feedback/INBOX.md` 최신 지시/APPROVALS 반려 → STATUS → 해당 DESIGN절.
루프가 아닌 일반 세션도 같은 최신 지시와 목표를 먼저 읽는다.
현재 다음 한 가지는 **docs/STATUS.md**뿐이다. roadmap/history에 현재 큐를 복제하지 않는다.
상세 lap 이력/가설/수치/실패는 docs/history/laps/, 확정한 기준은 baseline/golden 메타데이터에 남긴다.
기존 재현 엔진/원격/과거 세션의 INBOX·state를 이 프로젝트 지시로 가져오지 않는다.

## 모델 역할 (사용자 확정)

`docs/MODEL_ROUTING.md`를 따른다.
- 큰 방향/상위 계획: **Codex gpt-6-astra** 또는 **Claude Code claude-fable-5**. 기본 medium, 필요 시 high.
- 중간 계획/컨펌: **Codex gpt-5.6-sol** 또는 **Claude Code claude-opus-5**.
- 실무 조사/코딩/테스트/수정: **Codex gpt-5.6-luna** 또는 **Claude Code claude-sonnet-5**.
기본은 Codex. native subagent에도 같은 역할별 모델/effort를 적용한다.
컨펌 모델이 직접 구현을 대신하거나 실무 모델이 자기 결과를 최종 승인하지 않는다.
마일스톤 사용자 승인은 모델의 기술 컨펌과 구분한다. 설정 실패 시 다른 모델로 몰래 대체하지 않는다.

## 안전 불변 규칙

- 원본/참고 저장소는 읽기 전용 취급. 정확한 SHA/old bytes 확인 후 새 복사본만 패치한다.
- 패치는 명시적 원복/버전 거부/비중첩·범위 확인/회귀 테스트를 포함한다.
- 주소는 analysis/memory_maps/에 근거와 함께 기록한다. 다른 버전 오프셋을 추측 적용하지 않는다.
- EXE/DLL/게임 데이터/save/자격 증명을 커밋하지 않는다. 원본 자동deploy 금지.
- Wine은 별도 전체 게임 복사본/prefix/빈 Xvfb display에서만. 기존 세션에 붙거나 전역pkill 금지.
- 원본 디렉토리/개인 입력 Syw2plus/는 실행 대상 아님. local/·logs/·loop state는 Git 제외.
- 새 캡처 PNG는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/`에 YYYYMMDD_HHMMSS_접두사로 저장한다. 보여주기용/이미지 중간결과도 같은 공유 `temp/Syw2plus_patch/` 아래 별도 폴더에 두며 메인 레포에는 두지 않는다. 기존 JSON이 가리키는 과거 공유 temp 캡처는 경로를 깨지 않도록 보존한다.
- 생성/자원/상태 fixture는 명시한다. 장부 값만 바꾼 성공, 빈 플레이어를 활성으로 세는 것 금지.
- 개체 제한/풀 손상/OOM/CPU정체를 실제 증거로 구분한다. 사용자 위험 제기를 재현된 사실로 쓰지 않는다.
- 안전 pin/reference/golden을 자동 갱신해서 검사를 통과시키지 않는다. 변경 필요는 원인과 승인 기록을 남긴다.

## 작업 / 검증 / 종료

- 명확하고 안전한 로컬 작업은 자동 수행. 파괴/외부 게시/권한/범위 변경만 질문한다.
- 한 바퀴 한 가지 가설/변경. 첫 조사60~90분 또는 실패2회 뒤 재평가/구체 blocker.
- 독립 조사/구현/검증은 native subagent 분리 가능. 활성 카드 최대3개, 같은 파일 단일 작성자.
- OMX가 설치돼 있으면 설치 skill/prompt를 따른다. 다른 세션 state는 복사하지 않는다.
- Fast=`make check`; loop/FULL_TEST도 Fast일 뿐이다. 실제 앱/24k/144k/멀티는 별도 실행 증거다.
- 1단 기계→2단 다음 새 세션 독립 검수→3단 사용자 마일스톤 확인. skip/exit0/과거결과를 승인으로 쓰지 않는다.
- G2는8명 동시 활성/전비5000/풀·메모리/저장·지원동기화를 확인한다. G3는중단이므로현재검증대상이아니다.
- G4는 원본과 개선판의 도착/정체/시간/전략 행동을 반복 측정한다. 치트 보정은 공개한다.
- 기록이 길면 provenance를 보존해history로 옮기고 현재 STATUS는 작게 유지한다. 미결/반려를 삭제하지 않는다.
- 커밋은 별도 사용자 허용 및 LOOP_ALLOW_COMMITS=1일 때만 경로 명시하여 수행한다.
  git add -A/자동push/강제리셋 금지. 기본0에서는 uncommitted와 파일 해시로 이력을 보존한다.
- 세팅만으로 유료/무한 세션이나 systemd를 켜지 않는다. 기본 LOOP_ENABLE_AGENT=0, 최대1바퀴.
- STOP/취소/안전 위반이면 멈춘다. 타임아웃의 미커밋 파일은 보존하고 다음 바퀴가 검수한다.
