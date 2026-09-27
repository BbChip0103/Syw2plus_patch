# Syw2plus_patch — 원본 확장 패치 루프

`../Syw2plus_re_loop`와 같은 **한 바퀴=새 세션, 기억은 파일** 구조를 사용한다.
전체 엔진 재구현이 아니라 원본 기반 버전/패치가 산출물이다.

## 목표

현재 최우선: **G1 — 원본 화면 구성을 유지한 1600×1200 고해상도화**.
G2는 전비5000 달성 판단을 유지하고, G3는 중단, G4는 보류, G5는 단일플레이 마일스톤을 승인했다.
[상세 계약](docs/DESIGN.md)

1. **원본과 같은 화면 구성의1600×1200** — 800×600의4:3/각축2배.
   UI/스프라이트 상대 크기/구도를 유지한다. 단순 확대 화질은 허용하며 그림 교체는 사용자 후속 작업.
2. **활성8인 각각 전비5000 상한에서 안정 플레이** — 5000 단계 달성 판단을 유지한다.
   전비10000 확장 트랙은 12비트 슬롯 한계를 수용해 2026-09-27 종료했고, 후보와 검증 근거만 보존한다.
3. ~~**최대16인**~~ — **중단**(2026-09-17 사용자 지시). 과거 근거는 보존한다.
4. **길찾기 및 자유대전 컴퓨터 AI/난이도 패치** — **보류**(2026-09-27 사용자 지시).
   기존 길찾기·AI 계측과 반증 근거는 보존한다.
5. **드래그 선택 상한 20→50** — **단일플레이 마일스톤 승인**(2026-09-26).
   50기 선택·이동·공격·부대지정·저장/로드 근거를 보존하며, 멀티 동기화는 `UNKNOWN`으로 남긴다.

**현재 구현 최우선은 G1이다.** 기존 QHD 시야 확장이나 800×600 최종 버퍼의 단순 2배 확대는
고해상도 스프라이트의 추가 디테일을 살리지 못하므로 G1 완성 경로가 아니다.
[상세 계약](docs/DESIGN.md) · [현재 상태](docs/STATUS.md)

## 모델 역할

- **큰 방향/상위 계획:** Codex `gpt-6-astra` 또는 Claude Code `claude-fable-5`; 기본 `medium`, 큰 분기·교착에서만 필요 시 `high` (대략 10개 lap당 1회 이하)
- **중간 계획/컨펌:** Claude Code `claude-opus-5/high`
- **실무:** Codex `gpt-5.6-luna/high` 또는 Claude Code `claude-sonnet-5/high`

현재 중간 tier는 Opus5/high로 고정한다. Strategy는 Astra/Fable 중 명시적으로 선택하며 정기 호출하지 않는다. [역할 계약](docs/MODEL_ROUTING.md).

## 루프의 기억과 판정

| 파일/폴더 | 역할 |
|---|---|
| `docs/DESIGN.md` | 사용자 확정 제품 계약 |
| `docs/STATUS.md` | 현재 상태/다음 한 가지/블로커/검증/최근 바퀴 |
| `docs/feedback/INBOX.md` | 최신 사용자 지시, 최우선 |
| `docs/feedback/APPROVALS.md` | 독립 검수/반려/마일스톤 사용자 판단 |
| `docs/baseline/{compare,traces,golden}/` | 기준/비교/승인 자료 색인과 해시 |
| `docs/reference/` | 고정 원본 프로필 |
| `docs/history/` | 이전 Git/미커밋 스냅샷/실험/요구 변경/lap 이력 |
| `loop/PROMPT.md` | 매 바퀴①~⑥ 지시서 |
| `loop/{env.sh,loop.sh,loopctl.sh}` | 설정/신규 세션/실행 제어 |
| `checks/` | 원본/고정근거/컨텍스트 안전 검사 |
| `patches/`, `tools/`, `tests/` | 패치/격리 진단/회귀 시험 |

1단 기계 검사 →2단 다음 새 세션 독립 검수 →3단 사용자 마일스톤 판단.
승인된 기준은 이후 기계 검사가 감시한다. 과거성공/skip/모델exit0은 승인 대신이 아니다.

## 개발과 제어

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
git config core.hooksPath .githooks
make doctor
make check
loop/loopctl.sh status
loop/loopctl.sh models      # 모델 설정 조회만; 실행하지 않음
```

현재 머신에는 기존 패키지를 재사용하는venv를 세팅했다. 실제 모델 세션/서비스는 켜지 않았다.
초기 안전 pin은 세팅에서 수행한다. 새 복제 환경에서는 원본/profile을 검토한 뒤
`checks/safety.sh pin`으로 한 번 고정한다. 자동 재pin은 금지다.
실제 실행 설정은 [loop/README.md](loop/README.md). 기본 비활성/최대1바퀴/자동커밋 없음이다.
서비스 이름은 **syw2plus-patch-loop.service**로 기존 루프와 충돌하지 않는다.

`loop/FULL_TEST` 요청은 세션 밖에서`tests/test_build.sh`→`make check`를 실행한다.
이 결과는Fast이지 원본 앱/8인/16인/24k/144k를 실제로 돌린 결과가 아니다.

## 기존 패치와 로컬 입력

- [전비 패치/원복](patches/population/README.md), [과거QHD 참고](patches/resolution/README.md).
- 진단 inmm/X11 도구만 가져왔고 Plan C 엔진 실행 의존은 제거했다.
- 로컬`Syw2plus/`는 검증용 원본EXE만 있으며 전체 게임 설치가 아니다. 게임 데이터는 배포하지 않는다.
- 실제 실행 환경은 `local/runtime/`에 격리하며 prepare/check/smoke·doctor와 증거 검사 CLI를 제공한다. [안내](docs/setup/README.md).
- 게임 없는CI에서는 원본 필요한 테스트가skip. 원격CI를 실행한 것으로 주장하지 않는다.
- EXE/DLL/save/local/logs/세션 상태는Git 제외. 원격은 `github.com/BbChip0103/Syw2plus_patch`; 루프 자체는 자동 커밋/푸시하지 않는다.
- 출처에 없는 라이선스를 임의 부여하지 않았다.

[초기 실험 이력](docs/history/20260910_EXPERIMENTS.md) ·
[이관 출처](docs/history/20260910_MIGRATION.md) ·
[루프 구조 출처](docs/history/loop_structure_manifest.json)
