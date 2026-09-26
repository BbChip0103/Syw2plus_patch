# 개발·실행 환경 안내

## 기본 개발 / 루프 비활성

```sh
make doctor
make check
loop/loopctl.sh models
loop/loopctl.sh status
```

venv/원본 SHA/바이너리 커밋 방지 훅/역할 모델 설정은 세팅돼 있다.
`loop/STOP`, `LOOP_ENABLE_AGENT=0`을 유지한다. 위 명령은 개발 루프를 시작하지 않는다.
모델 CLI 버전 조회는 계정의 실제 모델 접근/쿼터 검증이 아니다.

## 격리 게임 환경

`tools/runtime_env.py`의 명시적 `prepare`만 전체 게임 데이터를 복사하고 전용 prefix를 만든다.
`check`와 doctor는 실행 없이 검사하며, `smoke`만 짧게 게임을 실행한 뒤 정리한다.
기존 Wine prefix/display/원본 게임 폴더를 실행 대상으로 쓰지 않는다.

```sh
# 새 환경을 만들 때만: 자동 복사, 원본 EXE 해시 확인, 전용 Wine 초기화
.venv/bin/python tools/runtime_env.py prepare

# prepare가 출력한 전용 manifest 경로를 사용
MANIFEST=local/runtime/RUN_ID/manifest.json
.venv/bin/python tools/runtime_env.py check --manifest "$MANIFEST"
make doctor-runtime MANIFEST="$MANIFEST"

# 환경 확인이 필요할 때만: 제한된 원본 시작/화면·입력·상태 확인
.venv/bin/python tools/runtime_env.py smoke --manifest "$MANIFEST" --timeout 60
```

`RUN_ID`는 실제 출력값으로 대체한다. 현재 머신 경로와 검증 결과는
`docs/history/20260910_RUNTIME_ENV_SETUP.md`에 기록한다.
전체 게임 데이터와 prefix는 `local/runtime/` 아래에 있고 Git에 넣지 않는다.
`Syw2plus/`에는 여전히 회귀 시험용 EXE fixture만 둔다.
지원 DLL/레지스트리/진단 모드의 출처를 manifest로 구분한다.
원본 EXE가 같다는 사실만으로 모든 DLL이 무수정이거나 실제 제품 검증이 끝났다고 하지 않는다.

## 상태 증거 검사

기존 `runtime_driver.py` 형식의 trace/state와 session의 실행 해시를 검사한다.

```sh
.venv/bin/python tools/check_runtime_evidence.py \
  --trace "$TRACE" --session "$SESSION" \
  --expected-sha256 "$EXE_SHA256" --goal smoke --pretty
```

`--state`로 단일 상태 입력도 가능하다. 틱 되감김·필수 필드 누락·기록된 후보 해시 불일치를 거부한다.
이 CLI는 session에 기록된 해시를 신뢰한다. 실제 EXE 재해시는 runtime check/독립 검수에서 수행한다.
`--goal g2`/`g3`는 현재 포맷의 미충족·관측 한계를 표시하며 제품 합격을 발급하지 않는다.
빈 슬롯/국가 설정만으로 실제 활성 플레이어를 세지 않는다. RSS는 OOM 증명이 아니다.
실제 8인/16인/AI·24k/144k 시험은 기능 개발 후 별도 수행한다.

## 진단 도구 빌드

`local/toolchain/bridge_current.json`에 로컬 진단 DLL과 빌드 출처 경로를 기록한다.
게임에 자동 배포하지 않는다. 필요 시 새 외부 빌드 디렉토리를 사용한다.

```sh
.venv/bin/python patches/population/build_runtime_bridge.py \
  --out-dir /tmp/syw2_patch_bridge_NEW
```

옛 `patches/population/runtime_driver.py`는 별도 실험용 request/response 진단 도구다.
read/snapshot/click/key/goal/shot/stop을 지원하지만 실행 후보·목적·계측 변경을 별도 기록한다.
과거 고정 경로의 `resolution/run_qhd_probe.py` 직접 실행은 차단되어 있다.

[검증 범위와 제품 경계](HARNESS_SCOPE.md). PNG는 지정 공유 temp에 저장하고,
사용자 승인 없는 결과를 `baseline/golden/`에 자동 승격하지 않는다.
