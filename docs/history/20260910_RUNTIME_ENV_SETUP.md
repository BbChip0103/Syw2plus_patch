# 2026-09-10 — 남은 실행 환경·하네스 세팅

## 범위

사용자 “환경세팅 다 해봐”에 따른 M0 작업이다. 실제 개발/모델 루프, 서비스,
기능 패치, 장기 부하 시험, 커밋/푸시는 수행하지 않는다. 원본 EXE와 참조 저장소는 읽기 전용이다.
환경 준비 상태를 확인하는 짧은 격리 게임 실행만 수행한다.

## 구성

- `tools/runtime_env.py`: 전체 복사본·전용 prefix 준비, 경로/해시 검사, 제한된 시작/캡처/입력/상태 스모크.
- `tools/check_setup.py`, `make doctor-runtime MANIFEST=...`: 실행 없는 필수 도구/격리 manifest 검사.
- `tools/check_runtime_evidence.py`: session SHA와 상태/trace 구조, 틱 되감김, 슬롯/전비/메모리 증거 한계 검사.
- `tests/test_runtime_env.py`, `test_setup_diagnostics.py`, `test_runtime_evidence.py`: 합성 fixture/모의 테스트.
- `local/runtime/`: 별도 게임 복사본과32비트 Wine prefix, 출력 로그. 배포/Git 대상 아님.
- `local/toolchain/bridge_current.json`: 진단 DLL 빌드 출처 포인터. 게임에 자동 배포하지 않음.

실무는 Luna/high 하위 에이전트, 중간 안전 검수는 Sol/high 하위 에이전트가 맡았다.
파일 소유권 혼선이 있었으며 최종 연결은 알려진 runtime 검사 함수 직접 호출로 제한한다.

## 발견·수정 이력

첫 실행은 프로세스가 살아 있었지만 실제 화면은 `_inmm` 레지스트리 오류였다.
따라서 초기 smoke의 정상 종료를 게임 시작 성공으로 인정하지 않았다.
전용 prefix의 레지스트리 초기화와 실제 게임 창/상태 확인이 필요함을 반영했다.
부모가 직접 캡처를 확인한 첫 실패 화면:
`/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260910_222102_runtime_after_enter.png`.

안전 검수에서는 경로·prefix 소유권/동시 실행 잠금, prepare의 전용 화면,
실제 종료 확인, 타임아웃과 성공 판정 경계를 점검했다. 과거 실패 로그는 새 성공으로 덮어쓰지 않는다.

## 진단 빌드

- 외부 빌드 디렉토리: `/tmp/syw2_patch_bridge_setup_20260910_222607_2655647`.
- 로컬 보존: `local/toolchain/runtime_bridge/20260910_222607/`.
- DLL SHA256: `f44090a324428bb1628751014507c6f2e3bd5bbfab3d0c333641e8f9b1adac4b`.
- 소스 bridge SHA256: `0eedffedd9fcaa38be3b63c068ff1cb9199d4476ca0856368a558d4099917cea`.
- 빌드 exit0. 기존 unused parameter/function pointer cast/stdcall fixup 경고는 남아 있다.
- 바이너리는 원본/실행 복사본에 자동 설치하지 않았다.

## 검증 경계

스크린샷/메뉴 스모크는 G1~G4 완료가 아니다. 8인/16인/길찾기/장기 안정성은 아직 검증하지 않았다.
전체 게임 데이터의 기존 지원 DLL과 원본 EXE의 동일성은 구분한다.
모델 CLI는 버전만 조회했으며 접근권한/쿼터/모델 세션 성공은 확인하지 않았다.

## 최종 현재 환경과 재현

```sh
MANIFEST=local/runtime/20260910_222434_2612938_0/manifest.json
make doctor-runtime MANIFEST="$MANIFEST"
# 아래는 필요할 때만 실행하는 짧은 스모크 (개발 루프 아님)
.venv/bin/python tools/runtime_env.py smoke --manifest "$MANIFEST" --timeout 60
```

- 실제 메뉴 도달: PS9, 타이틀 창 `조선의반격`800×600, 가상 화면1024×768.
- 한글 메뉴 표시 정상 확인. `LANG/LC_ALL=ko_KR.UTF-8`, `WINEDLLOVERRIDES=ddraw=b`.
  원본 게임 데이터의 custom syw2x 경로 대신 Wine builtin DirectDraw를 명시한다.
- 포커스를 준 메뉴(184,560) 클릭 → **PS9→7**, 입력 효과 관측.
  확인/로비/게임시작 클릭은 하지 않았다. 후속 캡처는 전환 프레임이며 완전히 그려진 대화상자 기준 승인이 아니다.
- RSS237,797,376→239,230,976 bytes 관측. OOM/전투 성능 증거 아님.
- 60초 제한 스모크 실제5.163초, 정리성공/잔류prefix프로세스0. 부모도 종료 후 재확인했다.
- 원본 EXE SHA256은 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 유지.

최종 자동 검사: **77 passed**, Ruff/compileall/mypy8파일/Bash/context/safety PASS.
`doctor-runtime` PASS, 실제2샘플 trace의 smoke 구조/해시 검사 PASS.
이 검사는 제목 화면에서 tick0인2개 관측이며 장기 틱 진행 검증이 아니다.

기록: `runtime_environment_{manifest,smoke,session,evidence,bridge}.json`,
`runtime_environment_checks.txt`, `runtime_environment_doctor.txt`.
스크린샷 경로와 SHA256은 smoke JSON에 있고 PNG는 지정 공유 temp에 보존했다.
root STOP 존재, counter=1 유지. 실제 개발/모델 루프는 시작하지 않았다.

## 중간 독립 컨펌

Sol/high 검수: **M0 환경·하네스 범위 APPROVE**, CRITICAL/HIGH 잔여0.
실제 원본/복사본 EXE 해시를 독립 재계산하고 PS9→7/화면/정리 결과를 확인했다.
증거 CLI 자체는 session에 기록된 SHA를 신뢰하는 구조 검사다. CLI exit0만으로 실행파일 동일성을 증명하지 않는다.
최종 코드의 캡처 tag가 after_enter→after_random_game으로 정리된 것은 이름만의 변경이며
동일 동작을 재실행한 것처럼 기록하지 않는다. 다중 악의적 변조의 모든 조합을 테스트한 것은 아니다.
