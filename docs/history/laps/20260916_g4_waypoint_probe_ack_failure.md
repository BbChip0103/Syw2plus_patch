# G4 waypoint reinforcement first run — evidence failure (2026-09-16)

## 실행

private seed1 180초/0.25초 실행, 170초 intervention:
`_g4_idle_waypoint_reinforcement_probe`.

AI만, 원본 AI current waypoint, full-ID roster 제외, owner당 최대 한 기, main-loop slot,
원본 movement issuer `0x4AEDE0`를 사용하는 진단이다. 제품 패치나 지속 정책은 아니다.

bridge는 두 AI에게 한 개씩 pending order를 staged했다.

| owner | source slot/full id | target | pending | packed xy |
|---:|---|---|---|---|
| 0 | 1164 / 656524 | (9,31) | 1→65539 | 0x001F0009 |
| 1 | 1165 / 525453 | (10,75) | 1→65539 | 0x004B000A |

mainthread callback은 5ms에 완료됐고 cleanup 잔류 process는 0이었다.

## 실패와 판정

`BLOCKED_EVIDENCE`, movement/AI improvement **UNKNOWN**.

1. control result `fallback_chain`의 Windows path `C:\inmm_g4_waypoint_probe.json`가
   JSON writer에서 escape되지 않았다. `json.loads`는 `Invalid \\escape`를 반환했고 Python
   controller는 정상 접수 결과를 읽지 못해 timeout으로 종료했다.
2. C probe의 tick 상수가 simulation tick `0x8924B8`이 아니라 walltime `0x9B5210`을 읽어
   `918582258`을 기록했다. movement trace와 시간 결합에 사용할 수 없다.
3. runtime sampling loop는 intervention exception에서 선행 samples/metadata를 쓰기 전에
   탈출했다. 170초 이전 표본도 최종 runtime JSON에 없으며, 현재 자료로 movement PASS를
   판정할 수 없다. 별도 bridge tick logs는 원시 증거로 보존하되 승인된 runtime samples로
   고쳐 쓰지 않는다.

pending staging 두 건을 실제 이동 성공이나 제품 AI 개선으로 승격하지 않는다. 다음
bounded repair는 path 없는 result summary, 올바른 simulation tick, exception-safe partial
sample/metadata 보존이며, 실패/timeout을 PASS로 바꾸지 않는다.

## 보존

`temp/Syw2plus_patch/g4_ai/20260916_seed1_waypoint_probe180_ack_failure/`

- bridge SHA `2ef5c2398b4d57a6c965c9c0d827b87212603107f6857249c1c1f98ae36617ab`
- runtime SHA `3dd8edb72e61c7e59a26df691da60194e6cbebbf7fd0794a89e2caff9f83d223`
- invalid acknowledgement SHA `85e2ed74f28b42ef86e8b181a34a26d3d539b907c84d02ddfa1648fa8e1f5353`
- waypoint JSON SHA `59bdfa839468ea51c4d18131fef4b5aeea019488381aac0a44954d8e03560eda`
- 원시 control events, unit tick/watch logs도 같은 외부 폴더에 보존
- 실행 전 fresh targeted158/Ruff/mypy PASS였지만 이 정적 회귀는 actual acknowledgement
  serialization과 tick 의미/exception preservation을 잠그지 못했다.

## Bounded repair / fresh 재실행 시작

Luna/high는 tick=`0x008924B8`, 경로 없는 fallback summary, sampling try/finally와 intervention metadata 선기록을 반영했다. Root Sol/high fresh targeted **167 passed**(bridge/runtime159 + analyzer8), Ruff PASS, protected original SHA 불변. Bridge SHA `2f7fc703fb92fc24bc9fd73f8e5961d29a1595461329838f9bfbb42a4bce62df`.

새 private manifest `local/runtime/20260916_164148_3970772_0/manifest.json` check PASS 후 동일 seed1 180초/0.25초, intervention170초 단일 실행을 시작했다. 이 시점 결과는 **PENDING**. Partial trace의 실제 예외 경로 behavioral regression은 static C 회귀와 별개로 Luna tests-only followup 중이다. 기존 실패 runtime/ack/tick artifacts는 그대로 보존한다.
