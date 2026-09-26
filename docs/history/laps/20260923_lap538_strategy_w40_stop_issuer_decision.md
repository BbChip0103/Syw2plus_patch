# 2026-09-23 | lap538 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 지정 역할 strategy(상위 방향).
  INBOX 2026-09-23 strategy 모델 교체 지시(Fable → Opus5.5/high)에 따른다.
- 가설 / 사용자 관찰: §91 회부 — `E_rev`는 대기 정지 명령(cmd2)의 무조건 커밋이고 발행자 127곳이 정적으로 좁혀지지 않았다.
  W40 런타임 발행자 귀속 1회로 "fixture로 풀리는가 / AI 통제와 충돌하는가"를 가를 수 있는가, 아니면 J4를 지금 적용하는가.
- 예상 PASS / FAIL 조건: 판정 문서가 W40 사양·판정식·결과 분기·J4 예산 해석·`BLOCKED` 시 사용자 선택지를 실행 전에 고정하면 PASS.
  합격 기준을 약화하거나 문서 회차를 3회로 쌓으면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): repo 비문서 변경 0. 문서만:
  `docs/work/active/G2_STRATEGY_W40_STOP_ISSUER_LAP538.md`(SHA `542f45fa7cea7024946d60ed11e27d7081b337ef91181e8e65d2f3f26db04ef9`, 102줄),
  이 파일, `docs/STATUS.md`, `docs/feedback/INBOX.md`(처리 한 줄), `loop/ESCALATE_SOL` §92. 커밋 0(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 exe `b56986e0…c9c08a8ac` 불변(재확인).
  후보 `a10024de…`(W39 `candidate.bin`, 이번 회차 미사용). 게임 실행 0. fixture는 W39 그대로(owner0~7 전부 AI 차례를 받음, lap529).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`(W39 원시·lap537 재계산 6파일·W39 하네스 2파일·원본), lap537 `text_orig.objdump`에서
  `call 0x4aeda0`/`0x4aede0` 개수 재계산과 호출 함수별 묶음(임시 python, 산출 파일 없음).
  W39 하네스 SHA: `w39_run.py` `64a86d21…4f41`, `gdb_watch.py` `f8a0ba33…b8bb`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - 이전 바퀴 검수 PASS: 원시 `triggers` `8f4735fa…`·`trace` `7017daa0…`와 lap537 재계산 6파일 SHA가 기록과 일치한다. CmdStop 127곳·CmdMove 44곳이 같다.
    cmd2 case `0x40c727`→`jmp 0x40d53a`→store `0x40d53d`에 조건 분기가 없다.
  - 신규 정황(귀속 아님): CmdStop 127곳은 56개 함수에 있다. 그중 74곳이 `0x47` 대역이고, 알려진 AI 자동시전 dispatcher `FUN_004755D0`도 이 대역에 있다.
    CmdStop·CmdMove를 둘 다 부르는 함수는 `0x4407e0`·`0x47f400`·`0x4bd700`뿐이다.
  - 판정: **K1 W40 채택(J4 즉시 적용 기각)**, **K2 W40 = J4 "후속 work 1회"**. 예외는 E2(유닛 로직의 fixture 원인이 주소 수준으로 특정될 때 work 1회) 하나뿐이다.
    **K3 기준 불변.** W40 사양(H14~H16), 판정식(`M0'`·`I_A`·`I_B`·`R_B`, 분류 `UNIT_SELF`/`OWNER_AI`/`UNIT_OTHER`/`UNCLASSIFIED`), 결과 분기, `BLOCKED` 시 선택지 (가)~(다)를 고정했다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 게임실행0·source변경0·커밋0. source 불변이라 `make check`는 생략했다(N22).
  위험: `ISSUER_SITE`가 스택 128 DWORD 밖이면 `BLOCKED(harness)`다. `OWNER_AI`/`UNIT_OTHER` 분류는 middle의 1회 판독에 의존한다(60분, 못 가르면 `UNCLASSIFIED` ⇒ `BLOCKED`).
  문서 회차 연속 2회째(lap537·538)다. 사용자 승인 대상 아님(통지). Q9·Q7-B·"8인"·스크립트 교전 (ㄱ) 범위는 미결 그대로다.
- 다음 한 가지: **work(Sonnet5) W40 게임+gdb 1회 foreground 완주**(판정 문서 §2, 45분 상자). 실행 없이 끝나면 STOP하고 사용자에게 보고한다.
