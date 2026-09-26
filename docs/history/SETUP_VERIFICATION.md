# 저장소 세팅 검증 — 2026-09-10

이 문서는 최초 이관 단계 기록이다. 최신 루프 구조 검증은
[20260910_LOOP_SETUP.md](20260910_LOOP_SETUP.md)를 참조한다.

## 결과

- 새 경로: `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch`.
- Git main 초기화, `.githooks` 활성화. 커밋/원격/푸시/실제 GitHub CI 실행 없음.
- Python 가상환경(기존 시스템 패키지 재사용), editable 로컬 패키지 설치 완료.
- `make check`: **24 passed**, ruff PASS, compileall PASS, mypy4개 파일 PASS.
- 원본 없는 별도 임시 복사본: **15 passed, 9 skipped**. skip=원본 필요 테스트.
  GitHub workflow는 작성했지만 원격 실행된 것으로 주장하지 않는다.
- 새 `tools/inmm_stub`만으로 외부 임시 경로에서 진단 DLL 빌드 PASS. 자동 배포 없음.
  기존 inmm C 코드의 컴파일 경고는 남아 있으며 전체 C lint 무경고를 주장하지 않는다.
- import manifest74파일: 출처 원본 해시 미변경, 새 경로 해시 일치 확인.
- 원본 EXE와 새 로컬 EXE fixture의 정확한 SHA 일치. 게임/소스 원본 변경 없음.
- 로컬 save011/012와 기존 검증 manifest 해시 일치. EXE/save/venv Git ignore 확인.
- 커밋 훅: 정상소스 허용, 로컬파일/DLL(대문자 포함)/save/.env.secret 거부 테스트 PASS.
- runtime driver: 새 원본/형제 원본/공유 원본/심볼릭 링크 거부, private경로 허용 테스트 PASS.

## 요구사항 갱신

최종 목표는 원본800×600 구도를 유지하는1600×1200(4:3/각축2배) 출력이다.
기존QHD 기술 실험은 현재 요구 미충족으로 분류했다. 이 세팅 작업은
1600×1200 화면 패치를 구현하거나 실제 게임에서 검증한 작업이 아니다.

## 로그 / 재실행

- `setup_check.txt`, `setup_no_game_tests.txt`, `setup_environment.json`.
- `setup_bridge_build.json`은 빌드된 진단DLL/입력소스 해시. DLL 파일 자체는 Git 제외.
- `import_manifest.json`, `local_artifact_index.json`은 출처/로컬 보존 자료 색인.
- 재실행: `make check`, `.venv/bin/python tools/check_setup.py --require-game`.
- 과거 게임24k는 이전 후보의 이력이며 새 런타임 검증으로 재명명하지 않았다.

## 다음 작업

`PATCH_ROADMAP.md`의 PATCH-001: 원본 기준 캡처와 2배 출력 경로 비교.
1600×1200은1080p 화면의 세로를 넘으므로 실제 대상 출력/창 모드의 표시 정책도 검증한다.
