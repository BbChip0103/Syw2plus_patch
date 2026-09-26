# 루프 제어 — 한 바퀴 = 새 세션

참고 Syw2plus_re_loop의 제어기/배관을 이관했다. 과거 세션·서비스는 별개다.
현재 자동 에이전트 비활성, 서비스 미설치, 최대1바퀴, 권한 우회 없음, 자동커밋 없음.

**현재는 환경·하네스 세팅만 한다. 별도 시작 요청 전에는 STOP을 해제하거나 실행하지 않는다.**

현재 안전하게 조회할 명령:
```sh
loop/loopctl.sh status     # 이 프로젝트 상태 조회
loop/loopctl.sh models     # 역할별 provider/model/effort 설정 조회, 모델 호출 없음
```

모델 계약은 `docs/MODEL_ROUTING.md`. strategy는 Astra/Fable 중 선택(기본 Astra/medium, 큰 분기·교착 전용,
필요 시 high), Opus5/high(중간 계획·컨펌), Luna/high(실무)다.
`make check`는 임시 프로젝트의 가짜 CLI로 라우팅·차단을 검증한다. 유료 모델을 부르지 않는다.
`dry [work|middle|astra]`도 CLI는 부르지 않지만 바퀴 로그/카운터를 만들므로
현재 루트에서는 실행하지 않는다. dry는 STOP을 해제하지 않는다.

### 추후 시작 요청 후 사용하는 제어 인터페이스 (지금 실행하지 않음)

- `strategy [N]`: `LOOP_STRATEGY_PROVIDER`로 선택한 Codex Astra 또는 Claude Code Fable 상위계획 세션.
- `plan [N]`, `review [N]`: 중간 모델 세션. 두 명령은 동일한 middle 역할이며
  현재 STATUS/요청에 따라 계획 또는 컨펌한다. 별도 자동 승인 판정은 아니다.
- `run [N]`: 실무 세션. `LOOP_ENABLE_AGENT=1`일 때만 STOP을 해제한다.
- `stop`: 다음 바퀴 금지, 현재 바퀴 보존. `resume`: STOP 해제만 하며 실행하지 않는다.
- strategy/plan/review는 비활성 차단과 STOP을 모두 존중한다.

`env.local.sh.example`은 자동으로 로드되지 않는 예제다. 실제 시작을 요청받은 뒤에만
로컬 설정과 실행 순서를 정한다. `LOOP_MAX_LAPS=0`은 명시적 무한루프 선택이며 기본은1이다.
자동 커밋은 별도 사용자 허용과 `LOOP_ALLOW_COMMITS=1`이 있어야 한다. PUSH는 별도 요청 필요.
`install/on/off/uninstall`은 **syw2plus-patch-loop.service**만 대상으로 하며 현재 실행하지 않았다.

`loop/FULL_TEST`는 다음 모델 세션 밖에서 tests/test_build.sh(make check)를 실행하도록 요청한다.
로그는 `logs/`, 실패 결과는`.result/.output`으로 보존. 소스 fingerprint가 바뀌면 이전 게이트는 무효다.
원본24k/144k/8인/16인 실행은 별도 후보·조건·증거가 필요하다.
안전 검사는 각 세션 전후 원본 EXE/고정 reference·golden/위험한 Git파일/컨텍스트 계약을 확인한다.
수동 에디터는 advisory git writer lock에 강제되지 않으므로 실행 중 같은 파일을 수정하지 않는다.
