# G1 W50 — HD 최종 출력 acquisition 가능성 판정 (lap596 strategy 발행, 2026-09-25 KST)

- 발행: lap596 strategy. 실제 모델은 Claude Code `claude-opus-5-5`(effort 세션 비노출)이며 계약 모델 Fable/Astra를 대신한다. 게임 실행0, 제품 source·도구 변경0.
- 근거: INBOX 2026-09-25 09:52 운영자 결정, `loop/ESCALATE_SOL` §146, `docs/reports/20260917_THREE_GOAL_FEASIBILITY_UPDATE.md` §1, `docs/reports/20260917_G1_G2_G4_CURRENT_FINDINGS.md` §1.5, `analysis/memory_maps/g1_hud24_final_output_contract_20260916.md`, `tools/inmm_stub/final_d3d9_trace.c`.
- 수행 역할: **work**(Sonnet5 또는 Luna, high). 계획 회차를 끼우지 않는다. 그다음 middle이 독립 검수한다.

## 1. 왜 G1이고 왜 이 한 단계인가

- G2는 모델 권한 안에서 더 진행할 축이 없다. 교전은 사용자 `(다)`로 제외됐고, 멀티는 Q12-3 `(iv)`로 미검증 명시, 화면은 09:52 결정으로 미검증 확정됐다. 그래서 Q12-1 `(A)` 부분 합격 기록을 2026-09-21 00:20 지시의 "G2 성립"으로 보고 DESIGN §3 순서대로 **M1 G1**을 재개한다(번복 가능). G4는 W50 판정까지 계속 보류한다.
- G1에서 이미 된 것: DxWrapper 2배 프리뷰(원본/후보 구도 99.213% 일치, 미니맵·선택·드래그 PASS)와 native 1600×1200 표면. 둘 다 G1 완료 경로가 아니다(DESIGN §2 G1: 800 버퍼를 거친 확대는 합격 경로 아님).
- G1에서 막힌 것: 실제 HD 합성 경로의 첫 관문인 **최종 출력 acquisition**. 2026-09-17 1회 실행에서 header 검사는 통과했지만, 초기화 guard가 `0x8000001A`여서 hook이 skip됐다. factory/device/Present 관측은 0회였다(`BLOCKED_FINAL_OUTPUT_ACQUISITION`). 이 관문을 못 넘으면 HD 스프라이트 합성은 시작할 수 없다.

## 2. N219 — guard `0x8000001A`의 의미 (strategy 정적 판독, 미증명)

- `final_d3d9_trace.c` 464행 주석대로 이 guard는 MSVC thread-safe static의 `_Init_thread_header` guard다. 규칙은 0=미초기화, -1=초기화 중이다.
- MSVC CRT는 초기화가 끝나면 guard에 `_Init_global_epoch` 값을 쓴다. 이 값은 `INT_MIN`(`0x80000000`)에서 시작해 1씩 증가한다. 따라서 `0x8000001A`(= `INT_MIN+26`)는 손상이 아니라 **"이미 초기화 완료"**로 읽힌다.
- 뜻: hook이 `DirectDrawCreateEx` 뒤에 지연 설치되는데, 그 전에 DxWrapper가 `Direct3DCreate9` 해석 static을 이미 초기화했다. 설치 **시점**의 문제다. 기존 "세 번째 acquisition 가설 없음"(2026-09-16)을 다시 여는 새 근거다.
- 미증명이다. work가 §3 A0에서 DxWrapper `D3D9_CALLSITE_RVA 0xC18C3` 주변 역어셈블(`_Init_thread_header`/`_Init_thread_footer` 호출 패턴)과 런타임 slot 값으로 확인한다.

## 3. 순서 (한 work 회차, 60분 또는 실패 가설 2회 중 먼저 오는 쪽)

| 단계 | 내용 | 게임 실행 |
|---|---|---|
| A0 | 정적 확인: DxWrapper SHA `96c44319…e8fe`를 확인하고 callsite 주변을 역어셈블해 N219를 판정한다(`CONFIRMED`/`REFUTED`) | 0 |
| A1 | 관측 1회: 기존 audit-only 경로를 확장해 지연 설치 시점의 `*init`, `*cache`, `*source`, `*factory`, `*device` **값**을 기록한다(CAS·쓰기 없음). 현재 로그는 slot 주소만 남긴다 | fresh 1 |
| A2 | A1 결과로 설치 방식을 **하나** 고른다. (H1) factory·device가 0이고 cache가 native `Direct3DCreate9`와 같으면, 새 명시 플래그를 켰을 때만 **cache slot**을 CAS로 hook에 연결한다. (H2) factory나 device가 이미 채워졌으면, 설치 시점을 DxWrapper d3d9 static 초기화 **전**으로 옮긴다(예: DxWrapper 모듈 로드 직후). 고른 방식과 이유를 적는다 | 0 |
| A3 | 고른 방식으로 fresh 1회 실행 | fresh 1 |

- A3가 실패하고 시간이 남으면, 다른 쪽 방식을 한 번 더 시도할 수 있다. **실패 가설은 2회까지만** 허용하고, fresh 실행은 A1 포함 **최대 3회**다. 한 번에 ≤15분, 원본 입력(stock UI PS9→PS7→PS5→PS3)만 쓴다. 시간이 부족하면 시작하지 않고 기록한다.
- 셸 background로 띄우고 끝내지 않는다. 동기 실행으로 끝까지 기다린다(PROMPT ③).

## 4. 판정식 (실행 전 고정)

**`FEASIBLE(acquisition)`** — 같은 fresh 1회 안에서 아래가 모두 raw로 성립할 때:
1. `native_binding status=active` 1건. 이 hook이 원래 native `Direct3DCreate9` owner로 전달한다.
2. factory ≥1, device 정확히 1, `Present` 성공(HRESULT 0) ≥1.
3. 같은 generation의 backbuffer 설명이 `1600×1200`(format 기록)이다.
4. 같은 시점의 1600×1200 캡처 1장 SHA가 있고 PS3 월드가 보인다(비검정). 캡처는 공유 temp `captures/`에 둔다.
5. 원본 SHA `b56986e0…a8ac`, DxWrapper SHA, ini 원문 `918e7043…a5a2` 원복이 전후로 일치한다. owned prefix/display 잔류는 0이다.

**`BLOCKED(acquisition: <이유>)`** — 가설 2회를 쓰고도 1~3 중 하나라도 성립하지 않을 때. 관측값과 남은 가설을 적는다.
**`NOT_FEASIBLE`** — 구조적으로 불가능함을 raw로 보인 경우만 쓴다. 예: DxWrapper가 d3d9를 쓰지 않는 경로로 출력함을 실측한 경우.

`FEASIBLE(acquisition)`은 G1 PASS가 아니다. HD 자산이 보인다는 뜻도 아니다. 알려진 WM_CLOSE 정상 종료 FAIL은 별도 위험으로 그대로 기록한다.

## 5. 변경 범위와 금지

- 허용: `tools/inmm_stub/final_d3d9_trace.c`에 A1 값 기록과 A2의 **새 opt-in 플래그 경로**를 추가한다. `tests/test_final_d3d9_trace.py`에 회귀를 추가한다. **기본 경로(플래그 없음)는 지금처럼 guard≠0이면 skip**해야 하고, 테스트로 이를 잠근다. 격리 prefix에서 빌드하고 실행한다.
- 금지:
  - 기본 guard 조건 완화, guard 값 강제 기록, 임의 그림 덧씌우기를 성공으로 보기.
  - HD `resource.spr` 합성. 이것은 W51이다.
  - 원본/참고 저장소 쓰기, 원본 EXE 패치, 새 Wine/DLL/의존성.
  - G2 산출물(결합 후보 `dfdc91ad…3883`, W4x raw) 변경.
  - G1 PASS 주장, 사용자 승인 대리, 커밋.

## 6. 그다음

- 결과와 무관하게 다음 회차는 **middle 독립 검수**다. raw 로그와 캡처로 §4를 summary 없이 재계산한다.
- **사전 허가 W51 (W50 middle ACCEPT `FEASIBLE`일 때만):** HUD 자원 SPR `0x24` frame0(`0x0043F270` call, x=10·y=3, 20×24)을 40×48 교체본으로 최종 1600 출력에 **직접** 합성한다. ON/OFF 캡처 한 쌍으로 판정한다. 합격선은 세 가지다: 40×48 안의 인접 출력 픽셀이 2×2 복제가 아니다, 대상 밖 화면은 OFF와 같다, 메뉴·커서 가림과 잔상이 없다. 카드는 middle이 W50 검수 때 이 절을 근거로 낸다.
- `BLOCKED`/`NOT_FEASIBLE`이면 strategy가 G1 대안 경로와 G4 전환 중 하나를 판정한다. 대안 경로는 native 1600 표면에서 게임 blit을 2배로 그리는 방식이다. 같은 acquisition 추측을 반복하지 않는다.
