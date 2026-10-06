# G1 P5-H H2 독립 검수와 gate/성능 수리 인계 — lap918 middle

- 판정: **H2 `PASS(partial)` / P5-H `HOLD_BPRIME_AND_PERFORMANCE` / G1 HOLD**.
- 지정 중간 tier. 실제 API model/effort 메타데이터는 미노출이며 Sol/high 호출을 추정하지 않는다.
- lap914 H1~H5·PH-a~d와 lap916 H2 수리 계약 그대로 검수했다. 게임/source/하네스/tests/runtime/commit 변경0.
- 재계산·563입력 SHA audit: 공유 temp `20261004_lap918_middle_review/recalculation.json`.

## 수용 범위

GREEN2/B′1/B′2/C1/C2/C3/pack2의 build48 입력은 모두 현재 source와 일치한다. 생성된 bridge source 변형,
DLL·trace·PNG·snapshot·보호 원본/save SHA, private game 제거 및 cleanup을 독립 확인했다.
`0x4663E0` old6 bytes `51 53 8b 5c 24 10`은 보호 EXE에서 재확인했다.
PH-b는 `[ESL]` pannelj(831×143) RLE를 독립 해독해 앞800열 SHA
`f649fe68a8f9a71b9e451c01cb5b0a1d79fbb06607cc8d566d3d30d108b66000`과 일치한다.
PH-a unbound/Lock/pointer/pitch 오류와 PH-d key subpixel은 7실행 모두0.
V1 6,747present 위반0, Scale2x 7실행 PASS, V2/V2s/V2q 35tag 모두PASS(최대150/173/1368).
전체 PS3 coverage p50은 0.82518~0.83453로 PH-c 범위 안이나 제품90%는 미달이다.

H2는 source 첫128byte FNV-1a `5939fabc`·writer·source pointer·831×143 key를 만들며,
동일 key의 정확한457600byte idx8을 읽어 key transparency를 검증한 뒤 전사한다. 파일 부재/크기·키 오류는
원래 Scale2x fallback이다. 원천800×143 identity SHA는 pack 사용 여부와 무관하게 유지됐다.
두 fixture 슬롯 SHA·FE/비FE 네 subpixel 규칙도 독립 확인했고 pack2만 loaded=1이다.
host GCC regression164 PASS. 반환주소/binding helper의 실행 테스트와 실제 wrapper 전체 분기 검증은 구분한다.

pack2 loaded PNG에서 baseline 모달 RGB와 독립 디코드 frame을 대조한 보조 계산:
원천일치69230칸, fixture 변형54445칸 중 네 subpixel fixture일치49438칸,
그 중 nearest와 다른 결과49359칸. 이는 fixture 디테일 전달의 제한된 증거이며 사용자 그림 품질/전체 coverage 증명이 아니다.
서로 다른 process의 캡처·모달 palette·후속 overlay 한계를 보존한다. lap917의42500/113084 차이는
정확한 같은-frame oracle로 수용하지 않는다. 재계산 보조 스크립트의 초기 nearest=0 가정 실패는
index/RGB 차이 및 overlay를 허용하지 않은 검사 가정 오류로 기록했으며 기존 제품 gate는 변경하지 않았다.

## 남은 실패와 확정한 하네스 결함

| 실행 | 독립 결과 |
|---|---|
| GREEN2 | snapshot5×2·기준/양lane 전필드 diff0, DOWN/RIGHT30 PASS |
| B′1 | 같은 snapshot 상태·입력 PASS, RIGHT25/30 INCOMPLETE·HOLD |
| B′2 | 같은 snapshot 상태·입력 PASS, DOWN/RIGHT30 PASS |
| C1 | ratio0.9999964374654481·p95Δ13ms PASS |
| C2 | ratio0.9175002925914916·p95Δ37ms **유효 측정 FAIL** |
| C3 | ratio0.9999997959054109·p95Δ10ms PASS |

연속 B′2회·C3회 조건은 충족하지 않았다. C2를 환경 이상치로 제외하거나 2/3 PASS를 전체 PASS로 바꾸지 않는다.
C2 candidate20.000459초에서367tick·present201회, >16ms71회·max63ms(원본400tick·399present·max3ms).
C1/C3 candidate는400tick·384/389present다. 비계측 C raw만으로 C2 저하의 원인은 확정할 수 없다.
HUD 직접 대조에서 패널 키 얼룩/구멍/분리·위치변형 결함은 보이지 않았으나 pack2 선택 초상화/내용은 양lane이 달라
입력효과 HOLD는 유지한다. V3는 배치/패널 화면 한정이다.

**확정 결함:** `tools/g1_saved_scene_probe.py:4292`의 pair_status 식과 return은
`performance_comparison`을 누락한다. 실제 C2는 하위 performance FAIL인데 pair PASS·프로세스exit0이다.
성능 수치는 올바르게 산출됐으므로 과거 raw는 그대로 두고 소비자 판정을 보수적으로 적용한다.
원인/수리 위치가 명확한 하네스 결함이므로 lap914 §5→lap911 §6에 따라 바로 work에 돌린다.
3회 원인불명 수리 실패·새 원천 귀속 충돌·마일스톤 경계는 발견되지 않아 ESCALATE_SOL은 만들지 않는다.

## 다음 work 한 가지 — P5-H gate/성능 수리 후 같은 조건 재검증

1. `tools/g1_saved_scene_probe.py`와 관련 tests 단일 writer로 최소 수리한다. performance-window 요청 시
   performance_comparison이 PASS가 아니면 pair PASS/exit0이 불가능하게 한다. 미요청 실행의 의미는 보존한다.
   실제 C2 보존 raw를 읽거나 복사 fixture로 FAIL/INVALID/누락/PASS를 검증한다. 기존 raw 파일은 수정하지 않는다.
2. H2·PH-a~d·V1/V2/V2s/V2q·snapshot·원본/fixture·입력 tick 일정·30present 표본과 C20초/ratio≥0.95/p95Δ≤16ms를 유지한다.
   단순 재시도 성공만으로 C2 원인을 단정하지 않는다. 새 source identity로 GREEN→B′연속2→C3을 완주하고 모든 실패도 보존한다.
3. C2형 저하가 재현되면 lap914 §4.3대로 패널 전사 비용부터 조사한다(`g1_mirror2x.c:890`, `g1_panel_apply_transfer`).
   이 위치는 조사 후보이며 확인된 병목이 아니다. 필요 시 관측 진단은 별도 실행하고 C 합격 측정은 비계측으로 한다.
   내용 대조/결과가 같은 범위의 최소 수리만 하고 구현→실행→수리 반복을 적용한다. row가 같다는 이유만으로
   screen 층이 매frame 초기화/다른writer에 덮일 수 있는 계약을 무시하고 복사를 생략하지 않는다.
4. 30개 미충족은 HOLD 그대로 둔다. 기존 observation tick 뒤의 표본을 섞어 B′1을 PASS로 고치지 않는다.
   비용/수신/trace 관측을 raw로 가르고, 분명한 하네스 결함만 수리한다. 일정/임계값 완화 금지.
5. 기록 먼저→lint/typecheck/full Fast 완주→새 middle 검수. 이 수리/검수 전 P5-T 전환은 보류한다.

일반 작업 재허가는 필요하지 않다. G2/G5 종료·G3 중단·G4 보류, 기준/기존raw/golden/안전핀/원본 보호와 커밋금지는 유지한다.
