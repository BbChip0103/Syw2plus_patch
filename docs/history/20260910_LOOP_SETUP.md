# 2026-09-10 — 루프 엔지니어링 구조 이관 완료

## 사용자 확정 범위

G1 원본구성1600×1200(단순확대 화질저하 허용·이미지교체는 사용자 후속),
G2 활성8인 각각 전비5000의개체풀/메모리/성능/저장/지원동기화,
G3 최대16인, G4 길찾기/자유대전 컴퓨터AI 개선. 상세는 DESIGN.md.

## 참고 구조와 의도적 차이

- 출처: `Syw2plus_re_loop`, HEAD/파일 원문 해시는 loop_structure_manifest.json.
- 재사용: loop제어기·설정·서비스 틀·INBOX 읽기색인과 그 회귀시험.
- DESIGN/STATUS/INBOX/APPROVALS/baseline/reference/PROMPT6절/과거이력 구조를 패치용으로 구성.
- 서비스/잠금은 syw2plus-patch-loop로 분리. 기존 루프와 서비스/프로세스 공유 없음.
- env.local/카운터/STOP/로그/자격증명/기존골든승인/전체 재현 엔진을 복사하지 않음.
- 기본유료실행비활성, 최대1바퀴, 권한우회없음, 자동커밋없음. 무한모드/실행은 명시 선택.
- HEAD없는초기Git을 지원; 커밋을몰래만들어전제조건을맞추지않음.
- 패치용안전검사: 정확한원본SHA, 명시pin한reference/golden메타데이터,
  위험한Git입력, 컨텍스트문서필수절·크기. 기본핀을매바퀴자동갱신하지않음.
- 보호검사는 변경탐지이지OS권한장벽이아님. 원본/참고저장소읽기전용정책을별도로유지.
- FULL_TEST는Fast make check. 원본앱·8인/16인·24k/144k는별도증거필수.
- 타임아웃은검증중단이며미커밋파일자동삭제가아니라는문구로정정.

## 검증 결과

- **42 pytest PASS**, ruff/compileall/mypy6파일/Bash구문/컨텍스트 검사 PASS.
- 실제로 이새저장소에서 **dry1바퀴 PASS**. 유료CLI 호출/게임실행 없음. 이후STOP생성.
- 격리테스트: dry신규2바퀴/CLI미호출/unbornGit/STOP·resume/원본참고변경차단/
  잘못된수치거부/유료실행기본차단/공유writerlock PASS.
- **mock** 작업자+Fast게이트 시험: 게이트exit7→failed, 검사중소스변경→invalidated/exit65.
  모델exit0을게이트성공으로승격하지않는것을검증. 실제모델을부르지않음.
- 게임없는임시복사본: **31 PASS,11 SKIP**. 원본필요9개+mock실행경계의원본guard2개skip.
- explicitpin및원본SHA안전검사PASS. 서비스미설치/미활성,원격·커밋·푸시없음.
- 독립읽기검토: 목표4개/설정/안전모순없음. 구주석·기본값문구정리반영.

로그: loop_setup_checks.txt / loop_setup_no_game.txt / loop_setup_dry.txt.
원본진단DLL 빌드는이전이관단계PASS(setup_bridge_build.json), 새루프가게임을검증한것은아님.

## 현재 미완료

G1~G4제품구현·통합검증은모두미완료. 지금완료한것은구조/작업기억/제어/검사배관이다.
다음한가지는STATUS에서관리한다. 원본기준캡처·1600×1200출력경로부터시작한다.
실제픽셀/부하시나리오검사와사용자승인golden은각마일스톤에서추가한다.
