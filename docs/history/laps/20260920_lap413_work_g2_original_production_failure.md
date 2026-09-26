# 2026-09-20 | lap 413 | G2 P2 원본 생산 경로 실제 실행 — FAIL

- 역할: Sonnet5/high work 회차가 시작했고, 백그라운드 런을 leader가 회수해 두 가설과 대조군까지 완주했다.
- 후보: marked compat N=4001 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`.
- 원본: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 사후 불변.
- 통합 요약: `temp/Syw2plus_patch/g2_capacity/20260921_lap413_p2_comparison_summary.json`.

## 측정식과 fixture

`op=6` 직접 유닛 시딩은 사용하지 않았다. 명시적 생산은 진단 브리지 `op=1`이 원본 Train
`0x004AF5E0`을 호출하는 경로이고, 정상 완료는 생산 gate `0x0043EDA0`을 거쳐 roster add
`0x0043EE30`으로 이어지는 기존 정적 계약에 근거한다. 실제로 owner0 HQ(type49)가 type7 worker를
새 slot3951에 생산해 `used 20→30` 및 새 internal_id가 관측됐다(slot≥1200 조건 충족).

AI 실험의 유일한 fixture는 신규 `op=7`: 원본 SetResource `0x43ED60/0x43ED80`으로 rice/wood만
1,000,000으로 설정한다. `used/reserved/count`와 유닛 배열을 쓰지 않는다. 모든 영수증에서 세 장부 필드가
호출 전후 동일했고, `test_runtime_bridge_contract.py`가 해당 branch에 장부/유닛 주소가 없음을 고정한다.
이 회차 결론은 lap410에서 경고한 stock-address stub 관측 채널에 근거하지 않고,
`runtime_driver` 외부 snapshot/trace와 Wine 로그에만 근거한다.

## 가설 1 — 단일 HQ 원본 생산

- 105.41초 동안 실제 완료 5기, used 30→80, 평균 **21.08초/기**.
- used 30→4,900은 같은 HQ 하나로 약 **10,267초(2.85시간)** 예상.
- 경로 성립은 확인했지만 60분 카드 안에서 near-cap 도달 불가. 두 번째 가설로 전환했다.

## 가설 2 — 자원만 공급한 AI 원본 생산

### N=4001 후보 run 1

- resource-only 공급 후 7 AI가 자연 생산/건설/전투.
- tick 11,928, live 468, 최고 owner5 `used=1208/count=84`에서 tick 정지.
- Wine 로그: **`Unhandled page fault on read access to 00338400 at address 00414133`**.

### N=4001 후보 run 2 (독립 신규 prefix/bridge/display)

- run1과 정확히 같은 진행: tick 11,928, live 468, 최고 owner5 `used=1208/count=84`.
- 같은 fault: **read `0x00338400`, instruction `0x00414133`**.
- 신규 유닛 452기 전부 slot≥1200. 즉 원본 생산이 확장 슬롯을 실제로 소비하는 경로에서 재현됐다.
- 정상 정리 후 driver rc0, 잔류 0, 원본 불변.

### stock-layout 전비5000 대조군

- EXE `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`, 풀 N=1200,
  동일 seed/goal/resource-only fixture.
- 후보 crash tick 11,928을 통과: tick12,112 live383, tick13,116 live405까지 정상 진행.
- 이후 tick13,804에서 유닛/장부가 0으로 정리되며 match 종료성 정지; **Wine page fault 없음**.
- combat 전개가 후보와 완전히 같지는 않으므로 이것만으로 root-cause instruction을 확정하지는 않지만,
  같은 setup에서 후보만 동일 tick/동일 주소로 두 번 죽은 것은 후보 경로 회귀의 강한 증거다.

## 판정

**P2 FAIL / G2 제품 목표 미완료.** 원본 생산 경로 자체와 slot≥1200 생성은 성립했지만, 카드 PASS 조건
`used≥4900` 전에 후보가 두 번 모두 468 live에서 재현성 있게 crash했다. 따라서 W8의 진단 시딩 4,000기
soak PASS를 일반 플레이 안정성으로 승격하면 안 된다. 다음 임계경로는 `0x00414133` fault의 선행 메모리
손상 원인을 찾고, 원본 생산·AI 전투 경로에서 수리한 뒤 같은 deterministic fixture를 재실행하는 것이다.

`0x00414133` 자체는 큰 stack-local 배열을 `mov 0x14(%esp,%edx,8),%cx`로 읽는 지점이며 원본과 후보의
해당 명령 바이트는 동일하다. 따라서 그 instruction을 바로 패치하는 것이 아니라, 잘못된 `edx`/stack 상태를
만든 앞선 확장 배열 또는 수명주기 참조를 추적해야 한다.

## 변경/검사

- 변경: `patches/population/runtime_bridge.c` resource-only op7,
  `patches/population/test_runtime_bridge_contract.py` 회귀 앵커.
- N=1200/N=4001 DLL 실제 컴파일 성공.
- 표적 테스트 1 passed, `SAFETY_PASS`, 모든 소유 runtime/display 정리, 원본 불변.
- 통합 `make check` rc0: **786 passed in 500.62s**, Ruff/compileall/mypy/CONTEXT/shell syntax PASS.
- 종료 후 `checks/safety.py` 재실행도 `SAFETY_PASS`; 원본 불변과 runtime 정리를 유지했다.

## 다음 한 가지

middle(Opus5/high)가 이 FAIL과 대조군을 독립 검수하고, 다음 카드를 `0x00414133` fault root-cause로
한정한다. 후보 숫자/기준선을 바꾸거나 진단 시딩 성공으로 덮지 않는다.
