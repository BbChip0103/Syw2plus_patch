# 2026-09-15 — 제품우선 G1 PS35 실제 메뉴 + 선택해제 대칭

원본 기반 원본800×600 대 후보1600×1200; protected EXE/save 동일 SHA, fresh 복사본/독립 Wine prefix, read-only 메모리, owned-only cleanup0잔류, 후보 private ddraw module PASS/ini 원복. 실제 모델 ID/effort attestation은 이번 CLI 산출물에 노출되지 않으므로 주장하지 않는다. commit/push 없음.

| 검증 | fresh 원본 | fresh 후보 | 결과 |
|---|---|---|---|
| PS3 선택해제 `(400,220)` 1회 | `20260915_131314_2023376_0`, artifact SHA `a7b06ca8d9aae74721d3a82a896fa6f90d52342cb33a5f4e1385c6dce58f86a2` | `20260915_131353_2044862_0`, artifact SHA `85d795d13fd1666fdc26ff09181dea082881604bd56c3a29566dd06273f9eadf` | 둘 다 count `1→0`, first_slot `1174→0`, code SHA `4fb9cd3a0333cdcf94804b4d1dbc17c9b08ee01ec586f4e40b0423d829e92970`, S1 load8/8 PASS |
| PS35 로드 메뉴 시각 | `20260915_131546_2131103_0`, artifact SHA `c544ee62805504345cf2aac075b6a6a43abf8be3483ab88f882c26552ca51da9`, PNG SHA `ebbe0a155df948cc62636081c1f7378564d20fb6011eff0182948ba29f896608` | `20260915_131627_2164289_0`, artifact SHA `0a21ebcaf4e945670b7ba8a0be7ddc35a15232be9fb14e8bc4cb4d111936f0eb`, PNG SHA `746551240d68e89dab07a1df3d5853c664e4377dd59dcc518c1174024dd162ce` | 두 화면을 원본800×600 최근접2배 vs 후보1600×1200로 비교 **1,920,000/1,920,000 pixels exact, MAE0**, code SHA `5c10117fe128a5e16bd6ec0cc58854aba9c6340ff01558bbe6b044d2aa1ae94c`, menu→PS3/load8/8 PASS |

PS35 모달 창 중심·모든 버튼/행/문구와 검은 주변/마우스 아이콘까지 2배 동일, **단순 확대 비주얼의 허용된 화질 열화**만 있다. 실제 게임의 메뉴 클릭 좌표는 후보 화면이 2배여도 원본 논리 좌표 그대로 주입했을 때 원본과 동일하게 PS3로 전이된다. PS3 시각/입력은 이전 fresh pair 검증 참고. `--ps35-screenshot` opt-in은 게임·원본 변경이 아닌 private 캡처이며 캡처 크기 틀리면 trigger0/UNKNOWN을 회귀로 잠갔다. 최신 `make check`: 438 PASS, Ruff/compileall/mypy10/CONTEXT PASS, targeted60; safety2 PASS. **제품 G1 미완료:** 다른 메뉴·드래그·생산·정상 종료/장기 안정성 별도 검증 필요.
