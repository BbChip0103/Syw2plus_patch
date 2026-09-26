# 2026-09-11 lap123 — G1 fresh presentation trace work-tier handoff

## 중간 판정

lap122의 shared surface decision 수리는 **MIDDLE CONFIRM PASS**다. 기록된 세 source SHA와
보호 원본 SHA가 일치하고, production `surface_record_reusable`가 shared C helper에 실제 record,
object/vtable, 네 wrapper와 네 original method를 전달한다. native harness는 성공 시
`reusable=1/method_count=49/reason=OK`, production 재사용 분기에서 도달 가능한 16개 실패 입력은
`reusable=0/method_count=0/해당 reason`을 실행한다. `NOT_INSTALLED` 기본값은
`slot->installed || slot->object`가 거짓인 신규 설치 경로라 재사용 helper 호출 대상이 아니다.

targeted 75 passed, `make doctor` top `ok=true`/original verified, `make check` 162 passed,
safety `SAFETY_PASS`다. lap122 bridge SHA `0683156b...`도 보존 경로에서 일치했고, 새 독립 bridge는
PE32 i386/SHA `1b729514...`로 빌드됐다. 빌드 시각 때문에 DLL SHA는 달라질 수 있으나 manifest의
shared header/source SHA는 lap122와 일치한다. 이 판정은 actual Wine trace나 G1/M1 PASS가 아니다.

## Luna/high work 한 가지

**새 격리 환경에서 G1 presentation trace를 정확히 1회 실행하고 raw/result를 보존한다.**

1. 저장소 밖 새 디렉터리에 diagnostic bridge를 다시 build하고 source/DLL SHA를 기록한다.
2. 보호 원본 전체 게임 디렉터리를 읽기 입력으로만 사용해 새 `local/runtime/<run-id>` 전체 복사본,
   새 Win32 Wine prefix, 사용하지 않은 Xvfb display를 `runtime_env.py prepare --bridge <fresh DLL>`로
   만든다. 기존 runtime/prefix/display는 재사용·정리하지 않는다.
3. 새 manifest에 `runtime_env.py check`와 `make doctor-runtime MANIFEST=<manifest>`를 통과시킨다.
   실패하면 재시도·완화·게임 실행 없이 raw와 SHA를 보존하고 `loop/ESCALATE_SOL`로 끝낸다.
4. `g1-presentation-trace --manifest <manifest> --screen 1600x1200x24 --timeout 90`을 정확히 1회
   실행한다. 좌표·timeout·validator 30/49·fixture·source를 바꾸지 않는다.
5. process 종료 뒤 정확히 하나인 final summary, raw trace copy, validator 결과, IID→DD→surface→
   actual desc→non-clear present, PS3 장면, owned-only cleanup을 기록한다. 실패하면 같은 lap 재실행하지
   않는다. PASS여도 다음 새 Sol/high 독립 검수와 사용자 판단 전 G1/M1로 승격하지 않는다.

게임 EXE/DLL/assets, 원본/참고 저장소, baseline/golden은 수정하지 않고 커밋·푸시하지 않는다.
