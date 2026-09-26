# 패치 프로젝트 분리 기록 — 2026-09-10

## 출처 / 이력 정직성

- 원본 프로젝트: `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re`.
- 출처 원격: `https://github.com/BbChip0103/Syw2plus_re.git` (새 저장소 origin이 아님).
- 출처 HEAD: `edd86cafdb83e29d6929bd9d3aba272e795f3f81`.
- **0910 전비/QHD 성공 실험 소스·보고서·증거는 당시 미커밋 작업 트리였다.**
  HEAD의 내용이라고 주장하지 않는다. `import_manifest.json`에 각 실제 원본 해시,
  tracked 여부와 이관 후 해시를 기록한다.
- 실제 기존 Git 이력은 `upstream_git_log.txt`로 별도 보존한다.
  새 저장소에는 원래 `.git`, 활성 agent state, 자격 증명, 원격 설정을 복사하지 않는다.
- 새 로컬 Git을 초기화하되 사용자 요청 없는 커밋/푸시/원격 생성은 수행하지 않는다.

## 가져온 범위

전비/QHD 패치 및 테스트/증거, 관련 주소 보고서, player_offsets 참고자료,
기존 inmm 진단 C 소스/헤더/def, X11 입력 Python 두 개. 전체 Plan C 엔진은 제외.
캡처 JSON과 패치 바이트는 원문을 유지한다. QHD 보고서/README에는 사용자 요구 미충족
정정 머리말을 추가했다. 원문 출처 해시는 import_manifest.json에 별도로 남는다.
문서 안의 `plan_c` 또는 옛 절대 경로는 **출처/과거 환경 설명**이며 새 실행 의존성이 아니다.
`analysis/ghidra_output` 등 더 넓은 연구 참조는 형제 원본 저장소에 남아 있다.

## 이관 시 변경한 실행 경계

- bridge builder: `plan_c/tools/inmm_stub` → `tools/inmm_stub`.
- runtime driver: 두 X11 helper 경로를 `tools/`로 변경.
- inmm Makefile: 원본 공유 경로를 향하던 자동deploy/restore 제거; 빌드만 허용.
- 실제 EXE 패치 알고리즘/명령 바이트/기존 캡처는 변경하지 않는다.
- runtime driver가 새 원본 경로뿐 아니라 형제 원본 설치/그 하위/심볼릭 링크도 거부하도록 보강.
- `run_qhd_probe.py`는 특정 과거 경로에 묶인 **이력용 launcher** 그대로 보관.
  새 실험은 명시적 경로 인자를 받는 population/runtime_driver.py를 사용한다.

## 로컬 전용 자료

`Syw2plus/`에는 정확한 원본 EXE만 독립 복사했다(전체 설치 아님, Git 제외).
`local/fixtures/20260910/`에는 사라질 수 있는 임시 실행 폴더의 save011/012를 보관했다.
원본 파일을 이동/변경하지 않았으며 모든 EXE/DLL/save는 커밋 금지다.
캡처 PNG는 기존 공유 temp의 타임스탬프 경로에 유지한다.

## 완료 검증

`SETUP_VERIFICATION.md` 및 `setup_environment.json`을 참조한다.
이관 회귀 확인은 기존24k를 다시 실행한 것으로 표시하지 않는다.

**이관 안전 보강:** 과거 `run_qhd_probe.py`의 직접 실행 진입점은 비활성화했다.
고정된 옛 Wine prefix의 로그 삭제/종료를 실수로 실행하지 않도록 기본 거부한다.
