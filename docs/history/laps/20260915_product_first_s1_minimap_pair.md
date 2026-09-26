# 2026-09-15 — G1 실제 저장 장면의 원본/1600×1200 입력 검증

목표: 화면 구성뿐 아니라 실제 게임 입력이 원본과 동일한지 빠르게 검증한다. protected original EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 런타임·게임·Wine prefix는 매번 새로운 private copy이고 원본/메모리/baseline/golden에 쓰기 없다. 각 fresh 실행 후 owned-only cleanup/residue0; 후보 ddraw loaded, dxwrapper.ini restored.

1. 첫 원본 시도 `(150,520)`은 PS3 load 8/8 PASS이나 camera `(39,53)→(39,53)` 5초, 입력 `FAIL_NO_EFFECT`, 전체 UNKNOWN. Run `20260915_130511_1857856_0`, artifact SHA `167ffbf4c6c9b5aed0de13b567c97c5462ec8f0771ad4f28068a7e2ff44676d7`. 다른 기본 랜덤 맵에 쓰던 좌표를 save000 장면에 적용했으므로 무효 근거로 보존하고 후보 실행은 생략했다.
2. 실제 save000 장면 미니맵 내부의 `(35,560)` 1회: fresh 원본 `20260915_130645_1868205_0` artifact SHA `99272a006bdeb0ab6666ea43e00089a5d03462f4496fb9af52500e24c10a906f` → PS35→PS3, 8/8 save fixture, camera `(39,53)→(49,159)` 0.166초, screenshot800×600 SHA `788176af66dea3e9d10b8f432294d27e676415e8639627a76e06a36f39a394b1`.
3. fresh 후보 `20260915_130721_1881143_0` artifact SHA `b72228ef2a2b55204bbcc9c2fb86366fb6d01a04fcb7641d3aa182aa957de993` → PS35→PS3, 8/8, 동일 주입 `(35,560)` 한 번으로 camera `(39,53)→(49,159)` 0.114초, screenshot1600×1200 SHA `96fa0be518c5883fe59ef61ff65a4fa1b2be6b33314ee627f59efeb5391355f9`; private ddraw module PASS, ini byte restore PASS. **후보 시각은 2배지만 입력 주입 좌표는 원본 그대로**여야 실제 camera effect가 동일하다.

두 PASS 실행은 동일 `tools/runtime_env.py` SHA `127e096c633399915eb928795aa422d5e9b5572f6cdadce75aed6ff2408eacc2`. 원본 PS3 캡처를 최근접 2배하여 후보와 비교하면 전 화면 99.017% exact, MAE 0.620/255; 상단 HUD 영역 exact100%. 움직이는 게임 프레임 영향이 있으므로 전체 픽셀 100% 동일성 주장 아님. 회귀 56 passed, `make check` 433 passed(마지막 1테스트는 직후 추가), Ruff/compileall/mypy/CONTEXT PASS. **G1 전체는 아직 미완료:** 드래그/유닛 선택/생산·다른 메뉴·WM_CLOSE/장기 안정성 별도 시험 필요. 커밋·push 없음.
