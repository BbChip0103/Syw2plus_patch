# lap913 middle — D-1R partial acceptance / P5-H panel origin HOLD

- 지정 역할: 중간 tier 진단·계획·확인. 현재 API는 실제 model ID/effort를 노출하지 않는다. Sol/high 호출이나 strategy 권한을 주장하지 않는다. 게임 구현/하네스/테스트 수정0, 새 게임 실행0, commit0.
- D-1R의 64-present 관측은 `PASS(partial)`로 수용한다. source47/current 일치·DLL/SHA·9 pins·raw/header·G1~G4·P-a~P-f·cleanup 확인. G1 HOLD, 제품/마일스톤/다음 큰 방향 승인은 아니다.
- **범위 결정 미확인:** 패널 표면 `0x01E75790`, backing `0x020D16E0`, pitch800, 800×203의 PS3 세대에서 분류된 픽셀은 set_pixel522뿐이다. 나머지161878/162400(99.6786%)의 writer/원천은 unknown이다. 19개 보존 trace의 visible source rect `[0,0,800,143]`에는522가 모두 들어가며 미분류113878/114400(99.5437%). 이것은 실제 검정 픽셀 수나 writer가 존재하지 않는다는 뜻이 아니다.
- 최종화면 HUD-row의 category10 p50=68536.5는 패널→present 전사의 destination 변경 픽셀이다. **패널 내부를 만든 writer/HD asset identity를 증명하지 않는다.** 패널을 PS3 이전에 초기화했는지, 직접 메모리/GDI/프리미티브 밖에서 썼는지 이 raw는 구분하지 못한다. 초기화 원인/구체 함수/HD layer 방식은 UNKNOWN이다.
- lap911 카드 §2/§7의 "패널 표면의 주 writer가 unknown이라 층 미러로 설명되지 않을 때" 재판정 대상으로 보존한다. 층 미러 불가능을 판정하지 않으며 충분한 입력이라고 가정해 P5-H 게임 구현을 지시하지 않는다. 사용자 stop 조건(구현 근거 불명확)에 따라 ESCALATE_SOL 생성, 추가 runtime/full Fast SKIP.

## 승격 작업자가 확인할 것

1. 기존 source/raw와 독립 검산에서 panel source와 present destination을 구분하고, 미분류 패널 픽셀이 초기화된 정적 패널/자산인지 다른 writer인지 확인한다. D-1R 맵 수치는 폐기하지 않는다.
2. P5-H 층 미러에 필요한 최소 원천/색상키/표면 생성·재사용·유효 rect 계약을 확정할 수 있는지 판정한다. raw에 없는 원천 주소를 추측하지 않는다. 게임 수정은 work tier가 한다.
3. 근거가 부족하면 동일 census 전수 조사 반복 대신 다음 work의 **패널 초기화/전사 지점 한정 probe** 또는 lap911 §5의 **P5-T 우선 fallback** 중 한 가지를 명시한다. fallback 순서 선택은 승격 판정자에게 남기며 이 세션은 상위 순서를 바꾸지 않는다.

## 조건부 work handoff (승격 범위 확인 뒤)

- 관측 probe를 고르면 기존 설치 가능한 tracer를 이용해 패널 표면의 최초 생성/채움과 PS3 전사 source rect/색상키·실제 pitch를 한정 기록한다. sentinel/Scale2x/층 미러 수리가 필요하면 old bytes/SHA·copy-only·원복·회귀를 포함해 work가 구현→격리 실행→추적 가능한 결함 수리→재실행한다. 명령 성공이나 빈 writer표만으로 수용하지 않는다.
- P5-H 구현 합격은 기존 V1/V2/V2s/V2q·Scale2x·B′2pair/C3pair와 기존 성능 한도, 동일 구도/색상키/패널 업데이트 parity를 유지한다. 초기화된 완성800 화면 확대를 HD asset 구현으로 바꾸어 부르지 않는다. 새 임계값/관측기 전수검사를 선행조건으로 만들지 않는다.
- 별도 명확한 계측 결함 두 건(근거충돌 사유가 아님): `g1_census.c:653`의 `present_source_surface`는 surface COM 포인터 대신 backing buffer를 직렬화한다(첫 present raw0x0223DC00, 같은 game_tick trace source0x01E758C0). 실제 pointer+pitch bind는 맞다. `surface_blt_captured`는 begin에서 증가하므로 post-Lock 실패가 missed0에 숨을 수 있다. 실제 이 실행의 destination writer_calls10=64로 완료 관측이 뒷받침되지만 일반 실패경로 검증은 아니다. 이를 수리하면 work가 actual surface 인자 전달/완료 후 카운트·관련 좁은 회귀만 추가하며 기존 raw를 수정하지 않는다.

- 근거: `docs/history/laps/20261004_lap913_middle_g1_d1r_panel_origin_hold.md`; shared-temp `20261004_lap913_middle_d1r_review/recalculation.json`.
- 사용자 질문/재허가 대기 없음. 내부 승격 세션 인계이며 G2/G5 종료·G3중단·G4보류, 원본/기존raw/golden/기준 보호 유지.
