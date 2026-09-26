# G2 W47 — F4 통합 후보 혼합 구성 144k 정확히 1회

- 발행: lap574 middle, W46 2단 `ACCEPT / STABLE_MIXED_24K_F4` 뒤.
- 상위 계약: `G2_STRATEGY_S3_F4_INTEGRATED_W46_LAP572.md` §5. strategy 재판정 없이 이미 허가된 다음 work 한 건이다.
- 목적: W46에서 저장/로드까지 확인한 결합 후보 `dfdc91ad…3883`를 같은 8-AI 혼합 fixture로 tick 144,000까지 유지해 장기 안정성과 F4 장부 폭을 측정한다. 이 카드 통과는 G2 PASS나 사용자 3단 승인이 아니다.

## 1. 고정 입력과 실행 예산

1. W46 raw 디렉터리의 `w46_run.py`(SHA256 `82d08bd1a97737740ce1fe1559cc0a90a21ce2704b6dd188be3697e3985357d0`)를 새 비중첩 공유 temp 디렉터리의 `w47_run.py`로 파생한다. 제품 source·브리지 source는 바꾸지 않는다.
2. 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` → `build_candidate(original,4001)` SHA `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68` → F4 15곳 적용 SHA `dfdc91adb88a732d96dff96f78648f03406003bffce1b22a7e5836317f963883`을 메모리에서 재현하고, 역적용이 base와 같아야 한다. 새 격리 게임 복사본에만 쓴다.
3. fixture는 W46과 같다: 8 AI, map 100×100, cap `[5000]*8`, owner별 type5×100 → type7×25 → type2×60 → type46×20, 같은 anchor·순서·gate-legal op5/op6/op7. 교전·AI/생산/건설 로직 변경은 0이다.
4. W47에는 저장/로드와 결정적 추가 주입을 넣지 않는다. 허용 op는 `{5,6,7}`뿐이며 op1/op2/op3/op4/op8/op9는 0회다. tick≥144,000에서 끝낸다.
5. 새 전체 게임 복사본·fresh prefix·사용 중이 아닌 새 Xvfb display를 쓴다. `MAX_WALL_S=7200`, 1초 간격 표본, foreground 정확히 1회다. 남은 시간이 100분 미만이면 게임을 시작하지 않고 `SKIP(time_budget)`로 기록한다. background 실행이나 무변경 재시도는 금지한다.

## 2. 실행 전 기계 gate

- `py_compile`, 파생 diff 검토, 허용 op 정적 검사, 원본·base·결합·역적용 SHA, `checks/safety.sh check=SAFETY_PASS`를 먼저 확인한다.
- W46의 원시 판독을 유지한다: 모든 표본에서 owner별 `used32=dword[PS+0x200c]`, `used_hi=word[PS+0x200e]`, `bldg=int16[PS+0x2016]`와 기존 bridge `used`를 함께 기록한다.
- 합성 음성 회귀에서 `used_hi!=0`, `used32!=bridge used`, `used32>5000`, 음수 `bldg`, tick 144,000 미달이 각각 PASS로 오인되지 않아야 한다.

## 3. 실행 전 고정 합격 기준

| ID | PASS | FAIL |
|---|---|---|
| F1 후보 | 실행 EXE=`dfdc91ad…3883`, 역적용=`a10024de…2d68`, 원본 전후 불변 | 하나라도 불일치 |
| B1 도달 | T0에서 8/8 owner 라이브 `used`∈[4900,5000], op5/op6 시딩·op7 자원 지급만 사용 | owner 누락·범위 이탈·금지 op |
| B2 구성 | owner마다 type5·7·46·2 보유, type2≥10, 단일 type 비중≤0.85 | 하나라도 위반 |
| B3 무결성 | 전 표본 `0≤used≤5000`, coherent `live==Σcount`, `0≤count≤count_cap`, fault/crash 0, tick 역행 0 | 하나라도 위반 |
| B5 기간 | 최종 tick≥144,000 | 미달 |
| B6 자원 | 전 표본 RSS/VM/swap/host available 존재; 단일 segment VM이 비감소이면서 시작 대비 끝이 5% 초과 증가하지 않음 | 필드 누락 또는 조건 위반 |
| F2 장부 폭 | 전 표본·전 owner `used_hi==0`, `used32==bridge used`, `0≤used32≤5000` | 하나라도 위반 |

- 보고 전용: `bldg` 범위, owner별 마지막 장부 변화 tick·동결 비율(N141), 자연 출생/사망, max live/pool, wall time, RSS/PSS/host available 최솟값. `bldg` 음수는 숨기지 않고 F4 위험으로 보고하지만 W47의 사전 승인 축은 F2이며 W46 F3 저장 복원 판정을 사후 재채점하지 않는다.
- 라벨 우선순위: `RUN_ERROR` > `ARM_FAIL(F1/B1/B2)` > `LEDGER_WIDTH_FAIL(F2)` > `LONG_SOAK_UNSTABLE(B3/B6)` > `WINDOW_SHORT(B5)` > `STABLE_MIXED_144K_F4`.

## 4. 종료와 handoff

- work는 게임을 정확히 1회만 실행하고 raw·하네스 SHA·원본/후보 SHA·격리 환경·fixture·수치·Fast 결과를 보존한다. 실패해도 재실행하거나 기준을 낮추지 않는다.
- 다음 새 middle이 summary를 제외하고 raw로 F1/B1/B2/B3/B5/B6/F2를 독립 재계산한다. 그 전에는 144k 통과나 G2 완료를 주장하지 않는다.
- ACCEPT 뒤에도 S4 지원 멀티/“8인” 정의, Q10 `(다)`로 제외된 전투·사망·재생산, N141 실제 플레이 성격, 화면 증거, 사용자 3단 승인은 남는다.

## 5. lap576 middle 독립 검수

- `run_summary.json`을 판정 입력에서 제외하고 lap575 raw와 보존 실행 EXE를
  `docs/history/laps/probes/20260925_lap576_middle_w47_independent_review.py`로 두 번 재계산했다.
  두 출력의 canonical SHA256은 모두 `b901cc0caf7a45bb44b8d34377a8c64c7eaca56cef63de3864effc9688812702`다.
- F1/B1/B2/B3/B5/B6/F2 전부 PASS: 원본 `b56986e0…a8ac`, base `a10024de…2d68`,
  보존 실행/재생성 결합 `dfdc91ad…3883`, 역적용=base, F4 15곳 exact old/new bytes·내부/기존 후보 diff 겹침0,
  잘못된 버전 거부·임시 copy/restore·원본 불변을 확인했다.
- raw 3,786표본, final tick144,030, max live1,692, op `{5,6,7}`만, B3 위반0,
  F2 30,288회 위반0, `bldg` 21~22/음수0, VM `3,463,216→3,463,216`KB다.
- 판정은 **`ACCEPT / STABLE_MIXED_144K_F4`**. G2 PASS·사용자 3단 승인이 아니며,
  다음 행동은 남은 S4/“8인” 정의·교전 제외 등을 strategy가 한 축으로 결정할 경계라 `loop/ESCALATE_SOL` §127로 넘긴다.
