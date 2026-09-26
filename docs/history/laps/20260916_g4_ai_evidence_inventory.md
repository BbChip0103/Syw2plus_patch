# G4 자유대전 AI 원본 evidence inventory (2026-09-16)

## 판정

- 앞선 "전략 AI 주소/fixture 부재"는 **패치 진입점에 대해서는 맞지만 원본 행동 metric 전체에는 과도한 표현**이었다.
- 보호된 `Syw2plus_re`에 원본 자유대전 장기 캡처가 이미 있다. 네 핵심 파일을 SHA로 고정해 읽기 전용 검증했으며 모두 일치했다.
- 따라서 G4 AI는 **`BASELINE_METRIC_AVAILABLE_PATCH_BLOCKED`**다. 원본에서 생산·접근·교전이 일어나는지 재는 oracle은 존재하지만, 이 patch repo의 fresh 반복 실행과 안전한 intervention point가 아직 없다.

## 원본 행동 metric

- 전투 장기 캡처 63 samples.
- slot disappearances 223.
- HP decrease 136, 같은 type/owner slot만 센 실제 피해 후보 125.
- low-HP disappearances 42, 두 진영 최소거리 0.
- 생산 series 17 samples, `t=240`에서 count 41.
- controller 206 samples, transitions 103.

## 산출물

- `tools/g4_ai_evidence_inventory.py`: 보호된 원본 evidence를 복사/수정하지 않고 SHA·schema·비공허 metric을 검증한다.
- `analysis/g4_ai_evidence_inventory.json`: 현행 SHA `db7c906823ee09340e56d2846ca411ccb22e0881096a2447da4c146c69074001`.
- G4 두 도구 targeted **4 passed**, Ruff PASS, mypy PASS.

## 패치 전 남은 게이트

1. ~~patch repo private harness에서 fresh 원본 상태 sample 재현~~ — 20초/10 sample로 충족.
2. ~~난이도 설정 identity와 최소 두 개의 고정 scenario/seed~~ — 원본 자유대전 난이도 selector 없음 직접 재확인; seed42/seed7 두 synthetic fixture 완료.
3. ~~fresh capture 2회 반복 동일성~~ — seed42 exact, seed7 30초 progress≤1 허용 PASS; 장기 접촉/피해 threshold는 미완료.
4. `FUN_0043F5D0` selector/dispatcher와 cadence threshold를 intervention boundary로 확인; rollback byte·후보별 행동 metric·LAN 결정성 분석은 미완료.

즉 AI 개선은 조사 대상이 없는 것이 아니라, **기준선은 있고 후보 패치만 아직 금지된 상태**다. 다음 작업은 이 보존 evidence를 첫 benchmark contract로 옮기는 것이다.
