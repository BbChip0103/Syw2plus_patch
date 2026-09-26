# 2026-09-12 | lap 205 | 목표 G1 Stage B — lap204 원본 FAIL 독립 검수 및 원인 판정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, middle tier
  (진단·계획·확인). 게임 실행 0회, Stage B 0회, 구현 0건. 이 세션은 직접 구현하지 않았다.
- 가설 / 사용자 관찰: lap204의 `drag_select` `FAIL_NO_EFFECT`가 (H-A) 하네스 판정식 결함인지,
  (H-B) seed 미노출 장면 의존성(고정 좌표가 유닛을 못 덮음)인지 독립 판정한다.
- 예상 PASS / FAIL 조건: lap204 evidence 해시 5종이 기록과 재현되고, `drag_select` 전후 관측이
  "효과 없음"과 "효과 있으나 술어 미충족" 중 어느 쪽인지 evidence·캡처로 구분되면 판정 성립.
  구분 불가면 UNKNOWN으로 남기고 추가 probe를 카드로 올린다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 source/tests/EXE/DLL/assets/
  baseline/golden 변경 0. `tools/runtime_env.py` SHA
  `3add9254f8df892292619940310a40cd38a95b1fd15605da5fd2c9d1f1f2f2c1` (lap204와 동일, 무변경).
  문서만 갱신: `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  이 기록, `loop/ESCALATE_SOL`. 모두 uncommitted (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 검수 대상 run
  `local/runtime/20260912_022912_3830565_0`. 원본/copy EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` = `ORIGINAL_SHA256` 핀 일치.
  후보 미생성. default two-player solo, seed 미노출. owner0 nation3 active2
  (slot1199 type70 world(161,90); slot1198 type21 world(163,92)), owner1 nation1 active2
  (slot1197 type49 (140,40); slot1196 type7 (142,42)). world_bounds 180×180, camera (161,90).
  rice/wood 5000/5000, used 20, count_cap 250, cap 1500.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 이번 바퀴는 **읽기 검수만** 했다.
  `sha256sum`으로 lap204 산출물 5종을 독립 재계산했고 전부 기록과 일치:
  manifest `7c08b771…19e1`, evidence `ec6ef7e0…7bbc`, verdict `940301af…4c53`,
  provenance `9a5fe61c…53`, inputs `29e32839…4e05b`.
  캡처 `…_drag_before_1789147784493061063.png` SHA `16b79b4bf55fe4674654d4469e22a74c15026e0692ed6942fddee744f0d5278a`
  (공유 temp)를 직접 열람했다. 게이트 재집행: `make check` → 221 passed / Ruff All checks passed /
  compileall / mypy Success(9 files) / `CONTEXT_PASS`, `LOOP_DRY_RUN=0 bash checks/safety.sh check`
  → `SAFETY_PASS`. 새 PNG 0장.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **lap204 기록 독립 검수 = PASS.** 해시 5종 재현, source SHA 무변경, 게이트 재현.
  - **H-B(장면 의존성) = 기각.** `drag_before` 캡처에서 본영(체력 4800/4800) 선택 타원 중심
    ≈(410,268), 이동 유닛 ≈(415,322)로 **둘 다 드래그 사각형 (350,180)-(550,350) 내부**다.
    본영 스프라이트 전체(≈x355-470, y185-285)도 사각형 안에 완전히 포함되므로 "완전 포함" 의미
    변형으로도 설명되지 않는다. 수치 대조: world 델타 (+2,+2) ↔ 화면 델타 ≈(+5,+54)는
    isometric `dx=(Δwx-Δwy)·w`, `dy=(Δwx+Δwy)·h` (h≈13.5)와 일치한다. 또한 본영을 실제로 선택한
    `unit_select` 클릭 (410,270) 자체가 사각형 내부이므로 기하학적 포함은 구성상 자명하다.
  - **H-A(하네스 판정식 결함) = 채택(높음, 미증명 잔여 있음).** 근거 셋:
    (1) **효과는 관측됐다.** 선택 identity가 `1199/type70` → `1198/type21`로 바뀌었고 count만 1로
    남았다. 즉 드래그 입력은 게임에 도달했고 게임은 재선택으로 응답했다.
    (2) **`FAIL_NO_EFFECT`는 오라벨이다.** `tools/runtime_env.py:2898-2901`의 분류기는 예산이
    남고 창이 잘리지 않은 **모든** 술어 미충족을 `FAIL_NO_EFFECT`로 찍는다. "효과 없음"을
    뜻하지 않는다.
    (3) **`count>=2`는 한 번도 근거를 가진 적이 없다.** `analysis/memory_maps/`에 band-select
    의미(건물 포함 여부) 역어셈블/관측 근거가 없고, lap191 R5가 이미 기대문자열
    "HQ and worker" ↔ type-blind `count>=2` 불일치(H3)를 지적해 승인 대기로 동결했다.
    저장소 테스트 `tests/test_runtime_env.py:1364`는 가짜 `wait`가 `count=2`를 주입하므로
    실게임 거동을 검증한 적이 없다.
    → 잔여 UNKNOWN: 본영(type70)이 band-select 대상에서 제외되는지 여부 자체는 **미증명**이다.
    다만 H-A 채택과 수리 범위는 이 잔여와 무관하게 동일하다(좌표는 고정 유지가 계약이므로).
  - **신규 발견(별건, 상위): 원본↔후보 비교기 부재로 Stage B는 현재 구조상 카드의 PASS를
    산출할 수 없다.** 카드 「Stage B 성공/실패 측정식」(:95)의 PASS는 **델타 일치(parity)**인데
    `tools/`에 비교기가 없다(R5-B, 카드:938 미구현). 즉 현 하네스는 단일 원본 run은
    **과잉 구속**(절대 `>=2`)하고 페어는 **미구속**(parity 검사 0)한다.
  - Fast/safety 재집행 PASS는 이 판정의 사전 게이트일 뿐 제품 G1 증거가 아니다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 코드 변경이 없으므로 회귀 없음.
  R6-A(분류기 오라벨 수리)와 R5-B(비교기)는 카드로 발행했고 work tier가 구현한다.
  **R6-B(`drag_select` 게이트 재정의)는 이번 바퀴에 발행하지 않고 승격했다** — 이는 승인된
  Stage B run이 무엇을 증명하는지 바꾸는 R5류 변경이며, 페어 수준에서는 조이는 방향이지만
  단일 run의 절대 상수를 푸는 방향이기도 해 middle 단독 판단 범위를 넘는다.
  H-A 잔여(건물 band-select 가능 여부)를 결정적으로 가르는 probe는 추가 게임 run이 필요하며
  승인된 exact-once 페어 예산 밖이다. 제품 G1 합격·출시, G2~G4, P6 승인 없음.
- 다음 한 가지: 승격 tier(Sol/Astra 또는 사용자)가 R6-B 범위를 재결하기 전까지 Stage B 후보 run은
  금지다. 그 사이 work tier는 **R5-B 비교기**를 오프라인 fixture로 구현한다(게임 실행 불필요,
  기존 evidence에 소급 적용 가능). R6-A는 같은 바퀴에 넣지 않는다(한 바퀴 한 가지).
