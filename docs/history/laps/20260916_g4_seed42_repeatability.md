# G4 seed42 repeatability fixture (2026-09-16)

## 결과

공식 PS9→PS7 UI 진입 뒤 diagnostic bridge의 승인된
`_custom_game_chain_inject_seed42`만 사용해 고정 국가/맵/seed fixture를 만들었다.
독립된 새 private runtime 두 개에서 각각 10초/5 sample을 수집했다.

두 실행은 다음 normalized gameplay 상태가 완전히 같았다.

- 국가: player0 조선(1), player1 일본(2).
- 맵: 100×100.
- 최초 네 유닛의 slot/type/owner/HP/command/생산 상태/좌표.
- sample summary: tick `12→279`, units `4→4`, 최소 진영 거리 81,
  HP 감소 0, slot 소멸 0.

전체 sample series 비교 signature는 양쪽 모두
`d0167b2c8f8dcb37af76781efb2bf0fb00b9afb08c7975f585e6fd227009b3b9`다.
pid/time, same-run fingerprint, runtime별 internal id는 comparator에서 의도적으로 제외한다.

## 경계

이 fixture는 `synthetic=true`, `memory_writes=true`, `control_bridge=true`다. 원본 메뉴를 통한
자연 발생 random game의 분포를 증명하지 않는다. 목적은 AI 후보 전후를 동일한 시작 상태로
비교하는 것이다. 일반 UI 두 런은 국가 `[3,2]` 대 `[2,1]`, 최소 거리 44 대 116으로 달라
exact comparison에 부적합하다는 것도 별도 확인했다.

## 산출물

- `tools/g4_ai_repeatability.py`
- `tests/test_g4_ai_repeatability.py`
- report SHA `00b294a33bb2e76613f3dbc7aae3f9f1ff2229808fe203f746e27b20682da504`
- report: `temp/Syw2plus_patch/g4_ai/20260916_seed42_repeatability.json`
- run1/run2: `temp/Syw2plus_patch/g4_ai/*_seed42_sample10_run{1,2}/`

다음 게이트는 두 번째 고정 scenario, 30초 이상 생산 결과 비교, 장기 접촉/피해 threshold,
그리고 rollback 가능한 intervention point다.
