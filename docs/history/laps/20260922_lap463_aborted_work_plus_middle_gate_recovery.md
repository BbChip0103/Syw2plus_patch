# 2026-09-22 | lap 463 | W24 Step D 착수 실패 + middle 게이트 회수

- 역할: work(Sonnet5/high) 회차가 중도 실패했고, 같은 날 interactive middle(Opus5/high) 세션이
  실패한 필수 게이트만 회수했다. **Step D는 여전히 미실행이며 §7 최종 verdict는 미확정이다.**
- 목표: STATUS 「다음 한 가지」 = W24 Step D(혼합구성 24k soak) 즉시 실행(§9 재계획 금지).
- 결과: **FAIL(회차) / 게이트만 PASS(회수)**.

## 1. work 회차가 실제로 한 것과 실패 지점

러너 로그(`logs/laps/2026-09-22/lap-0463.log`, `logs/loop-2026-09-22.log`):

```
11:30:58  LAP 463 START | worker=claude-sonnet-5 effort=high timeout=5400s
11:35     patches/population/runtime_bridge.c 수정
11:40:53  LAP 463 END | FAIL | 598s | exit=75
          ROUTE: middle review pending | reason=worker-request
          TAIL: "I'll wait for this to notify me when `make check` finishes."
11:40:55  LOOP DOWN | 이유=middle-review-pending
```

worker가 `make check`를 셸 background로 띄운 뒤 **회차를 종료**했다. loop cleanup이 자식을
정리해 게이트는 완주하지 못했다(회수 시점 `make`/`pytest`/`wine` 잔류 프로세스 0).
**이는 INBOX 2026-09-21 01:01 운영 규칙 위반이다** — "장기 probe는 모델 세션이 직접 기다리거나
root가 소유한 exec 세션으로 실행·회수한다". 규칙이 INBOX에 이미 있는데도 반복됐다.
lap 기록 파일도 남기지 않았다(N64 계열 재발).

## 2. 변경 파일 / source fingerprint

- `patches/population/runtime_bridge.c` — sha256 `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`
  (lap462 시점에는 불변으로 기록돼 있었다). 커밋 0(`LOOP_ALLOW_COMMITS=0`).
- 변경 실체는 op5/op6 fixture allow-list **{5,7} → {5,7,46}** 한 조건항과 근거 주석뿐이다:

```c
} else if ((fixture_type != 5u && fixture_type != 7u && fixture_type != 46u) ||
    (U32(0x9b524cu+type_offset)&14u) != 0 ||
    width<1 || width>8 || height<1 || height>8) {
```

- **N88이 완화 금지라고 못박은 가드는 전부 그대로다**: `(flags&14)!=0`, width/height 1..8,
  `fixture_exceeds_unreserved_supply` cap 게이트, Place→Gate→Spawn 개체별 회계 검사,
  `fixture_failed` 래치. 대표 t=46은 Step A 실측 cost20/w3/h3/**f0**이라 `(flags&14)==0`을 만족한다.

## 3. middle이 회수한 게이트 (PROMPT ④-0)

같은 트리에서 세션이 직접 완주시켰다.

| 검사 | 결과 |
|---|---|
| `make check` | **791 passed, 529.00s** |
| Ruff / compileall / mypy(10 files) | All checks passed / Success |
| `checks/context_limits.py` | `CONTEXT_PASS` |
| `checks/safety.sh check` | `SAFETY_PASS` |
| 원본 직접 재해시 `/home/dev_00/syw2plus-run/game.exe` | `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변 |

게임 실행 0회, 제품 코드 추가 변경 0, 커밋 0.

## 4. 신규 발견 N90 — 이 source 변경에는 회귀 테스트가 0건이다

`make check` 수는 **791로 lap456과 동일**하다 ⇒ lap463은 테스트를 하나도 더하지 않았다.
`tests/` 전수 검색에서 `unsupported_army_fixture_type`·fixture type allow-list·
`0x9b5238`/`0x9b524c`/`0x43eda0`/`0x443190`을 고정하는 테스트는 **없다**
(`test_g2_offline_storage_launch_gate.py`의 allowlist는 파일명 allowlist로 별개다).
즉 allow-list를 {5,7,46}에서 임의로 더 넓히거나 가드를 지워도 **게이트가 잡지 못한다.**
이는 N80(3)("신규 회귀테스트가 C 소스를 읽지 않아 C 변경으로 실패할 수 없다")과 같은 계열이다.
**791 통과는 "이 변경이 안전하다"는 증거가 아니라 "기존 테스트가 이 변경을 보지 못한다"는 뜻이다.**

## 5. 다음 행동

1. **다음 work 회차가 Step D를 즉시 실행한다**(§9 유지, 재계획·새 카드 금지).
   통합경계 `make check`는 이 회차가 이미 회수했으므로 **동일 source면 재실행 불필요**
   (INBOX 2026-09-20 21:58 규칙: 이 회차는 제품 source를 바꾸지 않았다).
   장기 실행은 **세션이 직접 대기**한다 — background 후 회차 종료 금지.
2. N90에 따라 그 회차는 allow-list/가드를 고정하는 회귀 테스트를 함께 넣는다(역주입으로 포착 확인).
3. middle 대기 2건은 그대로다: Step C `RIDER_NO_REPRO`가 연 **lap404(가) 재심**과
   **producer-선택 방법론 유보**(op1 Train의 producer가 실제 생산건물이 아니라 방금 배치된
   유닛이었고 호출 전후 그 유닛 상태가 불변 ⇒ 주문이 큐에 들어갔다는 확증 없음).

## 6. 이 회차가 하지 않은 것

Step D 미실행, 게임 실행 0, verdict(`CYCLE_STABLE`/`NO_ENGAGEMENT`/`CYCLE_UNSTABLE`/`ARM_FAIL`)
미산출, lap404(가) 재심 미판정, 144k 발행 금지 유지. 제품 완료·마일스톤 승인 아님.
