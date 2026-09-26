# 2026-09-20 | lap 411 | G2 marked compat 장시간 soak

- 역할: Claude Code Sonnet5/high work 회차에서 시작했고, 백그라운드 실행이 남은 뒤 leader가 직접 회수·완주·집계했다.
- 대상: `g2_full_capacity_v1_n4001_persistence_compat`, SHA
  `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`.
- 원본 SHA: 실행 전후 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 원시 증거: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260920_lap411_compat_soak_retry2/`.
- 집계: 위 경로 `soak_summary.json`.

## 첫 시도와 수리

첫 시도(`20260920_lap411_compat_soak/`)는 게임이 PS9에 도달하기 전에 메뉴 클릭을 보내 PS9에 남았고,
`runtime_driver.py`가 control protocol의 문자열 `request_id` 요구와 달리 JSON 숫자를 써서
`missing=request_id` parse error 뒤 90초 timeout이 났다. 게임/후보 결함이 아니라 하네스 결함이다.

수리:
1. PS9를 실제 판독한 뒤 `(184,560)` 클릭, PS7 확인 뒤 goal을 보낸다.
2. `runtime_driver.control_goal_payload()`가 `request_id`를 문자열로 직렬화하고 결과도 문자열 ID로 대조한다.
3. 회귀 테스트 `test_runtime_driver_control_goal_uses_protocol_string_request_id`를 추가했다.

재시도에서는 PS9→PS7→goal `chain_reached_ingame`→PS3가 1초 이내 성공했다.

## 실제 실행 결과

- 신규 격리 환경: `local/runtime/20260920_223253_1458431_0`, private display `:3128`.
- N=4001 브리지 주소: pool `0x0108C000`, existence `0x017B8658`.
- 8 owner 모두 `cap=5000`; gate-legal op=6 시딩 후 tick145에 live 3,993.
- 자연 simulation: tick145→24,325, **Δ24,180 tick**; PS3 trace 728표본; crash/hang 0.
- live: 3,993→중간 4,000→최종 3,959. 사망/생산이 실제 발생했다.
- 상세 스냅샷 10개 모두 슬롯중복 0, internal_id 중복 0, owner 범위손상 0.
- slot≥1200의 사망→재사용 **8건**(2066, 2814, 2972, 2975, 3738, 3739, 3818, 3819), 재사용 후 ID 정상.
- 저장/로드: slot92, 마커 `S2P1N4K1` 1회 @ `0x38`, 파일 9,281,722B,
  SHA `9bfe52cf8f1c31c1828359e796fed2fa8dba3e560afba9b6916cc2c870c1efbe`.
  save tick12,257; load tick12,295→12,257 역행. 저장 직전 snapshot tick12,252와 로드 직후 tick12,262의
  4,000 슬롯 대조에서 lost 0 / internal_id mismatch 0 / new 0.
- `used > 5000`: 728×8 owner 표본에서 **0건**. owner별 최대 used는 4,990~5,000.
- strict-cap 별도 caveat: `used+reserved=5010`은 owner3/4/5/7에서 2,053 owner-sample 관측,
  owner7은 tick158→24,298까지 지속했다. W8 계약상 기록만 하고 PASS/FAIL에서 제외하지만 제품의 엄격한
  전비 의미는 아직 미해결이다.
- RSS: 245,248→252,072→254,024 KiB, 총 +8,776 KiB/~727초. 전반 기울기 18.799 KiB/s,
  후반 5.358 KiB/s(71.5% 감속)라 가속 발산은 관측되지 않았다. 더 긴 soak 없이는 완전한 누수 부재 증명은 아니다.
- 정상 종료 rc0, display/process 잔류 0, `SAFETY_PASS`.

## 판정

**W8 PASS, 단 strict-cap caveat 유지.** marked compat 후보는 약 4,000 live의 실제 전투/생산 상태에서
24k tick, 중간 저장/로드, slot≥1200 수명주기를 데이터 손상·크래시 없이 통과했다. 이는 “확장 풀 자체가
단시간에 깨진다”는 우려를 상당히 낮춘다. 그러나 제품 목표인 “8인 각각 전비 5000 안정 플레이” 전체 완료는
아니다. 남은 핵심은 (1) diagnostic seeding 대신 원본 UI/생산 명령 경로(P2), (2) `used+reserved=5010`
엄격상한 의미/정책(P3), (3) 더 긴 반복 soak와 LAN(P4)이다.

## 검증

- `pytest tests/test_runtime_env.py::test_runtime_driver_control_goal_uses_protocol_string_request_id patches/population/test_g2_full_capacity_persistence_compat_v1.py -q` → **6 passed**.
- `ruff` 변경 파일 PASS.
- 프로젝트 표준 mypy 10개 대상 → **Success: no issues found**.
- `checks/safety.sh check` → `SAFETY_PASS`.
- 동일 source에 대해 직전 784 full gate가 PASS였으므로 INBOX 지시대로 전체 suite는 반복하지 않았다.

## 다음 한 가지

middle(Opus5/high)이 원시 증거와 이 판정을 독립 검수한다. ACCEPT 시 P2(원본 생산 명령 경로를 통한
near-cap 도달/유지)로 바로 넘어가며, 전체 suite 반복보다 실제 실행을 우선한다.
