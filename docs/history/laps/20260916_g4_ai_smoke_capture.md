# G4 AI fresh smoke capture (2026-09-16)

## 결과

legacy control-bridge launcher를 더 복구하지 않고, 이미 PS3 진입이 검증된
`tools/runtime_env.py g1-baseline`에 opt-in `--g4-sample-seconds`를 추가했다.
새 private runtime에서 20초 observational capture가 성공했다.

- PS3 sample 10개, tick `16 → 616`.
- unit count `4 → 4`; 두 진영 최소 거리 44.
- AI(owner 1) 자원 `7500/7500 → 7000/7000`, reserved `0 → 10`.
- AI 생산 command가 `1 → 15`, production type `75`, progress `0 → 99`로 진행했다.
- 같은 유닛 HP 감소 0, slot 소멸 0: 20초 smoke는 전투 판정 시간이 아니라 캡처 경로 검증이다.
- PS3 뒤 기존 고정 미니맵 입력만 `FAIL_NO_EFFECT`; sample 수집과 cleanup은 완료됐다.

따라서 patch repo에서 fresh AI 상태를 읽지 못한다는 blocker는 해소됐다. 다음 게이트는
고정 scenario/seed, 2회 반복 동일성, 장기 생산·접촉·피해 threshold다.

## 변경

- `runtime_driver.state(detailed=True)`에 기존 원본 offset `+0x0B4` HP를 포함.
- G4 metric은 slot의 `(internal_id,type,owner)`가 같은 경우만 HP 감소로 센다.
- runtime driver Wine 환경을 공식 harness와 맞추고 1600×1200 mode를 허용했다.
- 런타임 driver screenshot은 `temp/Syw2plus_patch/captures/` 밖으로 나갈 수 없다.

## 증거

- capture JSON SHA: `8e475123e11ea241288b6a0bb4cdd62c08e578b8b47e72ba43863c0e92faa5e3`
- capture: `temp/Syw2plus_patch/g4_ai/20260916_132946_1866168_0_official_g4_sample20/`
- `tools/runtime_env.py` SHA(실행 시점): `11986fac44754ac634ebc48f963a8669fa0bfc17021517da4c67b9435070d467`
- `runtime_driver.py` SHA(실행 시점): `02551faabeca40f67410cbe51d0ebbe01efaa3c422a7a2b096bae1bf2f55d36e`
- 변경 후 targeted: 158 passed; Ruff PASS.

실행 후 private runtime은 삭제했고 원본 repo/게임 파일은 수정하지 않았다.
