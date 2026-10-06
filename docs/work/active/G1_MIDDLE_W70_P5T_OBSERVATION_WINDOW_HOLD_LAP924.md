# G1 P5-T observation-window conflict — lap924 middle

판정: **HOLD_OBSERVATION_WINDOW_CONFLICT / P5-T HOLD / G1 HOLD**.
일반 중간 tier 독립 검수이며 제품 구현·새 runtime·마일스톤 승인·commit은 0이다.
실제 API model/effort 메타데이터는 미노출이므로 Sol/high 호출을 추정하지 않는다.
사용자의 이번 세션 근거충돌 stop 조건에 따라 승격 작업자에게 인계한다.

## 입력·성공 조건

STATUS의 lap923 독립 검수 요청과 lap918 handoff §다음work4를 적용했다.
입력은 lap923 final GREEN/B′1/B′2/C1–C3의 immutable pair JSON·trace·build manifest와
snapshot binary다. 기존 30-present/observation tick 일정·264000·key-before×0.9 조건은 유지한다.
snapshot 뒤 이미 생성된 로그를 늦게 읽는 flush 대기와, snapshot 뒤 새로 생성된 present를
표본에 넣는 관측 연장을 구별한다. 후자는 lap918에서 명시적으로 금지했다.

## 독립 결과

공유 temp `20261004_lap924_middle_p5t_review/recalculation.json` SHA256
`baf36422eabd0447c096f246af4120c71a23f2394163ea56cf497bec695d48e4`.
같은 폴더의 `recalculate.py`로 재현한다. build48×6/current source·DLL6·trace12 SHA MATCH,
193개 입력 read-audit changed0·보호 EXE/save006 SHA MATCH·두 lane cleanup 기록 true.
PNG는 해시만 수집했다. 이번 stop 이후 시각 검수 완료를 주장하지 않는다.

| final scroll pair | DOWN 경계 안/뒤 표본 | RIGHT 경계 안/뒤 표본 |
|---|---|---|
| GREEN | 30 / 0 | 30 / 0 |
| B′1 | **26 / 4** | **18 / 12** |
| B′2 | 30 / 0 | 30 / 0 |

B′1 원본 pair SHA `31cffdcb7d67daf976376542f59bdc83ba49a820b13aa21ab1e465f0d0dff7cf`,
candidate trace SHA `6d070f5107b1a77757f93cec64a3e1d9675c6411a29f0517c91e83f399926e2d`.
30개 전체의 coverage 배열과 하위중앙값은 기록과 일치한다(DOWN406739, RIGHT395963).
따라서 숫자 전사 오류가 아니라 표본 구간의 충돌이다. 기존 raw의 PASS는 보존하며 독립 수용하지 않는다.

시계 확인: 각 보존 prefix의 ntdll과 설치된 Wine ntdll SHA가 일치한다
(`d1e55ecf33b31f052d5cc13d08fe092c86b3eecdcbce7f476a3e5e8630232d43`).
로컬 `RtlQueryPerformanceFrequency` disassembly는 `0x989680`=10,000,000Hz를 직접 기록한다.
frequency만으로 두 시계의 epoch 일치까지 증명하지 않으므로 별도 보수적 계산도 남겼다:
동일 thread의 input snapshot→observation snapshot QPC 차이를 keydown receipt의 GetTickCount에
더해 observation 상한을 잡고 16ms 여유를 더해도 DOWN4/RIGHT12가 그 뒤다.
마지막 표본은 이 상한보다 각각 **311.539/699.743ms 뒤**다.
absolute QPC/10000 비교의 마지막 차이는329.365/724.167ms이고 동일 late count를 얻는다.
모든 해당 snapshot/present의 pid276/thread280 일치; snapshot SHA·binary header QPC 재검산 MATCH.
Receipt가 input snapshot 이후라는 순서는 update-return hook·exact input tick·동일 main-thread 입력 처리와
관측된 QPC/receipt 순서에 근거한다. 승격 검수는 이 clock/ordering 근거를 함께 확인한다.

## 원인과 한계

`tools/g1_saved_scene_probe.py:3144`는 observation snapshot을 받은 뒤 최대8s 동안
`_wait_for_terrain_scroll_coverage`를 호출한다. helper는 첫 camera transition 뒤30개를 고르고
observation upper bound를 받지 않는다. lap923 tests는 이 wait 호출을 요구하지만 구간 종료를 검증하지 않는다.
B′1의 추가 표본은 timestamp가 경계 뒤여서 단순 flush 대기로 설명할 수 없다.
lap923 서술의 “기준 변경0·six-pair PASS”와 lap918의 명시적 금지 조건이 실질적으로 충돌한다.
금지 조건을 없애거나 과거 PASS를 수정해 해소하지 않는다. 주변 유지보수 I/O 중첩은 가능성만 보존하고
느린 present의 성능 원인으로 확정하지 않는다.

C1–C3 tick-window ratio는 raw 재계산 `1.000002672958/0.999998383215/0.999994194506`와 일치한다.
p95 histogram·전체 V1/V2/시각·snapshot 전체 state·stale writer attribution의 완전 독립 검수는 stop으로 미완료다.
`rle_tinted_clip` coverage0·stale 감소 미입증·coverage90% 미달·input-effect HOLD 및 GDI/두 번째장면/
최종입력/사용자승인은 유지한다. 이번 결과는 G1 마감이나 다음 마일스톤 전환이 아니다.

## 승격 확인 → work tier 한 가지

승격 작업자는 위 두 late-count와 clock/ordering·lap918 규범·현재 helper의 무상한 수집을 확인하고,
**30-present 관측 종료를 고정하는 최소 하네스 수리**를 work tier에 넘긴다. 새 상위 설계는 필요 없다.
work 단일 writer 범위는 `tools/g1_saved_scene_probe.py`와 관련 tests다(게임 구현 수정 불요).
snapshot 경계 이후 표본을 집계하지 않으며 그 이전 표본이30개 미만이면 INCOMPLETE/HOLD다.
늦게 flush된 경계 이전 표본만 수용하고, exact input tick 전에 diagnostics/arm을 끝내는 수리는 보존한다.
종료 근거를 raw에 남기되 epoch를 가정한 단순 clock 비교만으로 PASS하지 않는다.
보존 B′1 반례(26/18)·늦게 flush되는 경계 이전 표본·경계 뒤 신규표본·정상30개를 회귀로 검증한다.
기존 raw/validator/일정/임계값/golden/원본은 불변. current-source fresh GREEN→B′연속2→C3,
lint/typecheck/full Fast 완주 뒤 다음 새 middle이 독립 검수한다. 추적 가능한 하네스 결함은
원인 수리→재실행하며 임의 실행횟수로 멈추지 않는다. G2/G5종료·G3/G4보류·commit금지 유지.
