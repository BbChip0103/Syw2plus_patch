# 세 목표 추가 실행 조사 — 2026-09-17 12:54 KST

## 결론부터

**세 목표 모두 완성됐거나 끝까지 가능하다고 입증된 상태는 아니다.**
이번에는 실제 게임/별도 Win32 프로세스를 실행했고, 성공·실패·미확정을 구별했다.
16인(G3)은 사용자 지시대로 제외한다. 활성 제품 완료는 여전히 **0/3**이다.

| 사용자 목표 | 확실해진 판단 | 아직 확정할 수 없는 것 |
|---|---|---|
| G1 원본 구도 + 1600×1200 + 차후 HD 이미지 디테일 | 단순 native 해상도 변경은 원본 구도를 깨뜨리고, 800→1600 확대는 HD 디테일 경로가 아니다. 현재 최종 출력 후킹 경로는 실제 초기화 상태에 막혔다. | 원본 구도·입력·가림을 보존하는 HD 자산 렌더링 경로의 실행 가능성 |
| G2 활성 8인 각각 전비 5000 | 원래 고정 풀/소유자 상한/저장 경계를 그대로 두고 상수만 바꾸는 방법으로는 요구 조건을 충족할 수 없다. | 별도 풀·관련 배열·전체 소비자·저장/LAN을 모두 수정한 버전의 안정성 |
| G4 AI·길찾기 개선 | 원본 명령 issuer를 이용한 국소 이동은 과거 실험에서 확인. 이번에는 정상 AI 호출 경계와 플레이어 연결도 실게임에서 관측했다. | 지속 명령 정책의 안전성과 실제 난이도 개선; 길찾기 알고리즘 교체는 별도 미검증 |

**32비트라서 세 목표가 원천적으로 불가능하다는 결론은 근거가 없다.**
반대로 “32비트 주소 공간에 여유가 있으니 된다”도 잘못이다. 현재 구체적 문제는
고정 배열·직렬화·실제 렌더링 순서·호출 시점이다. 부분 엔진 변경이 필요하다는
추론과 전체 목표의 실현 가능성이 입증됐다는 주장은 구별해야 한다.

## 1. G1 — 무엇이 실제로 막혔나

### 기존 증거

- 원본 800×600. Native 1600×1200 PS3 게임 진입과 해당 표면/pitch/viewport는 확인했다.
  그러나 월드 시야가 넓어지고 HUD/스프라이트가 기존 픽셀 크기에 머물러 구도 FAIL이다.
- DxWrapper 2×는 원본 화면 배치 프리뷰다. 최종 크기1600만으로 HD 자산을 지원한다고
  볼 수 없다. 원본 800 버퍼를 거친 그림은 디테일을 잃는다.

### 이번 새 실행

1. 첫 실행은 명시적 audit-only로 후킹/CAS 없이 실제 loaded header를 읽었다.
   DxWrapper file preferred base10000000과 달리 메모리 ImageBase는 실제 loaded base
   **76FA0000**이었다. Timestamp60B2E3C1/size23C000/e_lfanew296와 세 relocation operand는
   정확히 일치했다. 과거 header 검사 실패 원인을 추정이 아니라 실제 관측으로 확인했다.
2. 동일 파일 SHA에 대해 명시적 Wine-rebased flag일 때만 관측한 형태를 허용했다.
   Native 기본 검사와 나머지 PE32·29-byte·HIGHLOW·native-owner·CAS 경계는 유지했다.
3. 검수/전체 테스트 후 최종 출력 acquisition을 **한 번** 실행했다.
   Header 검사는 통과했지만 초기화 guard는 **8000001A**, 요구한 pristine0이 아니었다.
   안전하게 skip했고 native binding/factory/device/Present 관측은 **0회**다.

**판정: BLOCKED_FINAL_OUTPUT_ACQUISITION — 현재 후킹 위치/초기 상태 조건의 경로만.**
Guard를 느슨하게 만들거나 임의 그림을 덧씌워 성공으로 바꾸지 않았다.
HD resource.spr 실험은 하지 않았다. SPR identity/frame만으로 palette/clip/마스크/후속 가림
계약이 닫히지 않는다. 따라서 “HD 스프라이트를 넣으면 되는 버전”은 아직 아니다.

두 실행 모두 PS3 게임 진행은 관측했지만 WM_CLOSE clean-finalization은 timeout FAIL이다.
Owned prefix/display 강제 정리는 성공했고 잔류0/ini 원복을 확인했다. 정상 종료 PASS가 아니다.

근거: `analysis/memory_maps/g1_hud24_final_output_contract_20260916.md`,
`docs/history/laps/20260916_g1_native1600_ps3_stock_ui_nogo.md` 및 이번 raw 결과.

## 2. G2 — 메모리 용량과 고정 풀을 구별

- 본체 풀1200 slots, slot0 예약으로 allocator가 선택하는 범위는1..1199다.
- 기존 풀 끝892410은 다른 live state 시작이다. 원위치에 slot1200을 추가하는 방식은
  그 state와 충돌한다. Existence/age/active/category 배열과 소유자 count250도 별도 경계다.
- Cost10-only 산술이면 8×500=4000 live units, 예약slot0 포함4001 slots가 하한이다.
  본체 약7.17MiB는 주소 공간 부족의 증명이 아니며, zero-cost 객체/건물/부수 메모리와
  최종 용량을 포함한 계산도 아니다.
- 과거 실제 PASS는 **1인 전비5000 + 해당 save/load + 24,836 연속 ticks**다.
  활성8인 각각5000·확장 풀·8인 LAN PASS로 바꿔 말할 수 없다.

### 이번 독립 원본 기계어 실행 시도

원본 allocator442FA0의 실제61-byte 함수를 추출했다. 세 내부 branch 이외 외부 코드/PC
의존성이 없음을 검수했다. C/Python 재작성 allocator를 원본 증거로 쓰지 않았다.

- 첫 standalone 시도는 fixed mapping 선행조건에서 종료됐다. Allocator 실행 증거0.
- Astra 검수로 코드 PC만 OS 제공 위치에 옮기는 마지막 시도를 했다. 원본61 bytes와
  fixed data 주소는 유지하고, 확장 copy의 변경은 세 data operand로 제한했다.
- 마지막 시도도 data reservation **890000..8A0000**에서 실패했다. ERROR487,
  requested890000/returnedNULL. VirtualQuery는 allocation_base610000,
  state1000/protect2/type40000의 기존 mapped region을 보고했다. 해당 region의 정체는 UNKNOWN.
- 두 실패 모두 owned cleanup/잔류0/fixture 불변 확인. 더 이상의 data fallback/실행은 없다.

**판정: BLOCKED_ISOLATED_EXECUTION_BOUNDARY.**
이 실패는 시험 프로세스 주소 배치 문제다. **게임의4000-unit 확장 실패나 32비트 불가능을
입증한 것이 아니다. 원본 allocator의 확장 슬롯 실행도 이번에는 입증하지 못했다.**

단순 상수 패치는 NO-GO라는 기존 판단은 유지한다. 별도 풀 설계는 저장 포맷, reset,
객체 ID 소비자, 전체 참조, patched-peer LAN 결정성까지 닫혀야 제품으로 인정할 수 있다.
근거: `analysis/memory_maps/g2_capacity_boundaries.md`,
`analysis/memory_maps/population_5000_runtime_0910.md` 및 이번 두 attempt raw 기록.

## 3. G4 — 국소 AI 개입과 길찾기 교체를 구별

이번 신규 shadow는 CALL41CBE5→43F5D0에서 상태를 관측하고, 저장한 GPR/FLAGS를 복원한
뒤 원본 함수로 tail-jump한다. 실제 linked DWORD43F5D0/기계어를 확인했다.
기본 OFF이며, 추가 명령 issuer 호출/게임 데이터 변경은 없다. 관측 cap512다.

### 실제 fresh 자유대전

- Tick1..512의 연속512 records. 각 owner64 records, tick&7/ECX-player 연결 모두 일치.
- Live sampled source는 owner0(사람)·owner1(AI)뿐이다. Owner2..7의 AI flag1은 활성8인 증거가 아니다.
- Same-tick reentry/rewind는 이 표본에서0. 정책 verdict는128 UNTESTED/384 no-live-source rejection.
  UNTESTED에는 사람 records도 포함되므로 인간 배제나 would-issue 승인으로 해석하지 않는다.
- 게임 tick1044까지 진행했다. 전체 harness는 고정 minimap 입력 FAIL_NO_EFFECT로 실패했고,
  요청한20초 sampler 완료는 UNKNOWN이다. AI 정상 호출 관측과 전체 입력 PASS는 별개다.

### 실제 기존 save000 load

- 원본/fixture SHA 검증, fresh private copy/prefix, 메뉴1회+load1회로 PS35→PS3.
- S1 결과 **PASS / LOAD_RESTORED_PLAYER_STRUCTS**. 새로운 save를 만들고 reload한 실험이 아니다.
- 해당 세션의 AI trace11 records, tick50591..50601. Owner/ECX 연결 모두 일치,
  live sampled source owner0/1/2/3/5. UNTESTED7/rejection4. Owned cleanup/잔류0.
- 동기화된 load-completion marker가 없으므로 **정확한 완료 직후 첫 step/reset 처리 PASS는 아니다.**
  Raw postload도 UNOBSERVED다. Pending snapshot은low16 관측이며 완전한 정책 검증이 아니다.

**판정: 정상 AI 관측 경계는 실행 확인. 지속 AI 정책은 BLOCKED/UNTESTED.**
비지원 LAN/replay/campaign 배제는 실제로 검증하지 못했다. 발행 활성화하지 않는다.
과거 waypoint 국소 이동2회는 유지하되 실제 전략/난이도 개선·결정성·장기/8AI 증거는 아니다.
Pathfinding entry는 찾았지만 알고리즘 변경/병목 개선 실험은 없으므로 별도 UNKNOWN이다.

## 검증·이력·산출물

- Combined Fast: **523 passed /95.70s**, Ruff/compileall/mypy10files/context/shell PASS.
- 최종 G2 C 변경 뒤 targeted5PASS 및 GCC/Ruff/mypy 확인. 테스트 성공은 runtime 성공을 대신하지 않는다.
- Sol이 소스/실행 경계와 실제 G4 raw 결과를 독립 검수했다. Astra는 최초 세 카드와 G2 교착 분기만 담당했다.
- 초기 준비 중 shared DLL 중간 build가 발생해 별도 보존 후 조사 전 SHA(a538ab09…0f80)로 복구했다.
  실제 게임은 외부 pinned DLL(5d445a65…4906b)로만 시험했으며 새 hook을 배포하지 않았다. 원본 SHA는 불변이다.
- 코드: `tools/inmm_stub/final_d3d9_trace.c`, `ai_shadow.c/.h`, 최소 `inmm_stub.c/Makefile`,
  `tools/g2_allocator_slice_probe.py`, `g2_allocator_slice_fixture.c` 및 전용 tests.
- 이력: `docs/history/laps/20260917_three_goal_feasibility_spikes.md`.
- Raw/캡처/시험 binaries: **/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/**
  - `g1_hud_detail/20260917_header_audit/`, `20260917_final_acquisition/`
  - `g2_capacity/20260917_allocator_slice/attempt1/`, `attempt2_final/`
  - `g4_ai/20260917_shadow_feasibility/fresh_game/`, `run_artifacts/`, `driver_report.json`

세 bounded 카드의 허용 실행을 종료했다. 막힌 경계를 숨기거나 완료 선언하지 않는다.
