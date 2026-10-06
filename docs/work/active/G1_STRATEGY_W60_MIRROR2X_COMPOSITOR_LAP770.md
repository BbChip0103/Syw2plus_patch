# G1 W60 — 논리800 유지 + 2배 미러 합성기(content-keyed present) (lap770 strategy 발행, 2026-09-29)

- 발행: lap770 strategy. 실제 모델 Claude Code `claude-opus-5-5`(effort 세션 비노출), 계약 strategy 모델
  Fable/Astra 자리를 공개 대행한다. 게임 실행0, 제품/하네스 source·binary 변경0, 커밋0.
- 근거: 2026-09-29 18:45 운영자 "G1 재착수 전략 1회", 18:4x 사용자 "G1 착수", DESIGN §2 G1,
  lap605~612 기록, 20260915/16 native1600 기록, 참고 `Syw2plus_re/analysis/disasm/rendering.md` §3.3·§4.6~4.7,
  `FUN_004332f0_blit_primitives.md`, `g5_minimap_click_router_lap762.md`(WndProc 마우스 경로).
- 수행 역할: **work**(Sonnet5 또는 Luna, high). 계획 회차를 끼우지 않는다. 그다음 새 middle이 raw 독립 검수.
- 상시 지시(구현 우선): 구현→빌드→격리 실행→오동작이면 원인 추적·수리→재실행을 반복한다. "fresh 정확히
  1회" 예산을 두지 않는다. 단 각 실행의 raw/캡처는 덮어쓰지 않고 run별로 보존한다.

## 0. 판정 — 무엇이 새로운가

과거 G1 계보가 멈춘 이유는 둘이다. (1) **귀속 오류:** W50C가 present를 caller 주소(`0x0049273F`, 실제로는
메뉴 PS5/7/9)로 골라 PS3 월드 present(`0x00469376` thunk, return `0x00469379`)를 한 번도 바꾸지 못했다(N224).
(2) **구조 한계(N223):** whole-frame 2배는 DESIGN상 프리뷰일 뿐이고 월드 스프라이트 HD 디테일에 닿지 않는다.
native1600 EXE 해상도 변경은 표면은 되지만 구도 FAIL(월드 시야 확대·HUD 800 좌표 잔류).

W60은 둘을 한 번에 넘는다.

- **(1) 해소 — content-keyed present:** 전환 조건을 caller가 아니라 내용으로 건다: `destination==primary`
  ∧ split 적용 ∧ source desc 832×600(또는 renderer 폭) ∧ src rect 800×600(또는 NULL=전체). 메뉴/PS3 구분 없이
  같은 규칙이 적용되므로 caller 핀이 필요 없다.
- **(2) 해소 — 미러 2배 렌더:** 게임 논리·레이아웃·입력은 원본 800×600 그대로 둔다(구도 동일성을 구조적으로
  보장). 렌더러 객체 `0xE5BF18`의 픽셀 프리미티브를 bridge에서 감싸, 원본 호출은 그대로 800 버퍼에 그리고
  **같은 호출을 1600×1200 미러 버퍼에 2배로 한 번 더** 그린다. present 때 미러를 primary로 올린다. 나중에
  2배 해상도 그림은 이 미러 단계에서 800 버퍼를 거치지 않고 들어간다 → DESIGN "800 최종 버퍼 축소→재확대
  금지" 조건을 만족하는 유일한 모델 권한 경로다.
- **정확성은 완결성에 의존하지 않는다:** 감싸지 않은(GDI 글자, 직접 쓰기, 읽기-수정-쓰기 반투명 등) 픽셀은
  `expected800` 대조로 자동 탐지해 그 칸만 800 픽셀 nearest 2배로 대체한다. 따라서 프리미티브를 0개 감싸면
  whole-frame 2배(프리뷰)와 같고, 감쌀수록 미러 커버리지가 올라간다. 커버리지 = 측정 지표.

이것은 lap611이 "사용자 판단 몫"으로 남긴 "offscreen 단계 2배 renderer"의 **점진·비파괴 판**이며, 새 외부
의존성이 아니라 기존 프로젝트 bridge(`tools/inmm_stub`, `_inmm.dll` 프록시)를 쓴다. DESIGN §5는 래퍼/모듈
교체를 허용한다. 사용자 "G1 착수" 지시로 착수 권한이 있다.

## 1. 고정 사실 (이번 lap read-only 재확인, 원본 `[HQ]Syw2plus 2002.exe` SHA `b56986e0…a8ac`)

- `0x00469350..0x0046937B`: 인자 5개 전달 BltFast thunk, `0x00469376: ff 50 1c`, `0x00469379: c2 18 00`.
- `mov ecx,0xe5bf18` 직후 호출 773곳. 상위 대상: `0x464ec0`84 `0x465080`83 `0x463d30`70 `0x463d60`60
  `0x465190`42(클립 판정) `0x466d50`36 `0x465e80`31 `0x464e70`31 `0x464e20`31 `0x4652b0`23 `0x4664d0`19
  `0x465130`19(SetViewport) `0x466280`16 `0x465b30`12(DrawLine) `0x466070`7 `0x465fc0`7 `0x4663e0`6
  `0x466540`5 `0x466ea0`4 `0x4658e0`4(SetPixel) 등. 픽셀 프리미티브는 수십 개 이하의 유한 집합이다.
- 스프라이트 blit 4종(`0x466d50` 무색조·무클립, `0x4664d0` 무색조·클립, `0x466ea0` 색조·무클립,
  `0x466540` 색조·클립)과 `0x466280`/`0x465e80`/`0x465b30`은 **매 호출 `[ecx+0x1514]`(픽셀 버퍼)와
  `[ecx+0x10]`(stride)를 읽는다**(정적 grep: 각 1~4회/4~9회). → 호출 동안 버퍼 포인터만 바꿔 같은 프리미티브를
  다른 버퍼에 그릴 수 있다. 렌더러 필드: `+0x04` w, `+0x08` h, `+0x10` stride, `+0x4D0..0x4DC` viewport.
- PS3 offscreen 832×600, primary는 split 시 1600×1200×8(lap606/609 raw). 8bpp 팔레트 공유.
- 마우스: WndProc WM_L/RBUTTON 핸들러(`0x424204~0x424460` 부근) + `GetCursorPos` import. DirectInput 근거 없음.
- 기존 bridge `SYW2_G1_NATIVE_2X_STRETCH`는 `NATIVE_2X_PRESENT_RETURN 0x0049273F`에 묶여 있다(N224 원인).

## 2. 구현 (work, 모두 기본 OFF opt-in, EXE 파일 불변)

새 env `SYW2_G1_MIRROR2X=1`(+ 기존 split `SYW2_G1_NATIVE_2X_BLIT=1` 필요), CLI `--g1-mirror2x`.
`--dxwrapper-2x`·`--native-2x-stretch`와 상호 배타. 새 코드는 새 파일(예: `tools/inmm_stub/g1_mirror2x.c`)에
두고 `direct_draw_trace.c`는 연결만 한다(파일 800줄 한도).

### S1 — 섀시: content-keyed 2배 present + 입력 1/2
1. present: §0 content 조건을 만족하는 primary 대상 BltFast/Blt를 가로채 source를 Lock해 **nearest 2배**로
   primary 1600×1200에 쓴다(W60 S1은 미러 없이도 동작). 적용 건수·PS별 분포·caller를 개별 event로 남긴다.
2. 입력: WndProc 서브클래스로 마우스 메시지 lParam x,y를 1/2, `GetCursorPos` IAT 후킹으로 클라이언트 좌표
   1/2, `SetCursorPos`/`ClipCursor`는 2배. 게임이 보는 좌표는 원본 800 공간.
3. provenance `observational_only=false`, `intervention_scope`에 켜진 개입만 정확히 나열.
4. legacy validator(`_presentation_logical_surface_contract`, `validate_native_split`)는 **수정하지 않는다.**
   새 측정 스크립트(예: `tools/g1_mirror2x_probe.py`)가 raw를 직접 판정한다.

### S2 — 미러: 스프라이트 blit 2종부터
1. 1600×1200(+stride 여유) 미러 버퍼, 800 논리 크기 `expected800`·`scratchA/B` 버퍼(renderer stride와 동일).
2. 대상 프리미티브 진입부에 detour(bridge가 런타임에 메모리에서만, **old bytes 대조 후** 설치; 불일치면 설치
   안 하고 skip 기록). 첫 대상: `0x466d50`, `0x4664d0`(무색조 2종).
3. 래퍼 동작: 원본 호출(실제 800 버퍼) → `+0x1514`를 scratchA(값 0x00 채움)로 바꿔 같은 인자로 재호출 →
   scratchB(0xFF 채움)로 재호출 → `+0x1514` 원복. 픽셀 p가 쓰였다 ⇔ `A[p]!=0x00 ∨ B[p]!=0xFF`, 값 = 센티널이 아닌
   쪽. 쓰인 p마다 미러 2×2 블록 = 그 값, `expected800[p]` = 실제 800[p]. 클립·viewport는 원본 코드가 그대로
   처리한다(재구현 금지). 목적지를 읽는 프리미티브(색조·반투명)는 이 방식이 틀리므로 S2에서 감싸지 않는다.
4. present 합성: 논리 p마다 `expected800[p]==800[p]`이면 미러 2×2, 아니면 800[p] nearest 2배(stale 대체).
   PS3 외(메뉴)는 S1 경로 그대로.

### S3 — (다음 lap) 디테일 경로 증명
한 스프라이트(id/frame 확정 후)를 **명시 라벨된 합성 2배 패턴**(원본 실루엣 마스크 2배 안의 체커 등)으로 미러에서
교체해, 최종 1600 캡처에서 마스크 안 인접 픽셀 디테일(2×2 복제 아님)·마스크 밖 불변을 보인다. 실제 HD 그림
제작은 사용자 몫이며 합성 패턴을 실제 교체 그림으로 표시하지 않는다. S3는 S1+S2 PASS 뒤 착수.

## 3. 측정·판정식 (사전 고정)

공통: fresh private 게임 사본/32bit prefix/Xvfb 1600×1200, 원본 EXE `cmp=0`, 메모리 쓰기는 bridge 렌더/입력
래퍼만(게임 상태 쓰기0), default two-player random, synthetic=false, cleanup/prefix residue0, game 사본 삭제.
기준 run: 같은 bridge, `SYW2_G1_MIRROR2X` OFF(원본 800 표시) — 입력·상태 대조용.

- **S1 PASS:** ① 전환 present ≥1건이 PS3와 메뉴(PS9/7/5) 각각에 존재, HRESULT0. ② 같은 프레임의 800 source
  덤프(전환 직전 Lock 복사)와 primary 캡처의 nearest-2배 일치율 ≥0.999(커서 bbox 제외 가능, 제외 픽셀 수 기록).
  ③ 입력 parity: 메뉴 버튼 `(184,560)→(462,169)→(608,564)→(608,564)`을 물리 2배 좌표로 눌러 PS9→PS7→PS5→PS3
  도달(원본 800 기준 run과 같은 순서), PS3에서 유닛 클릭 선택 1기·드래그 선택 수·미니맵 좌클릭 카메라 이동이
  기준 run과 같은 결과(선택 수·카메라 좌표 동일). ④ crash0, tick ≥300.
- **S2 PASS:** ① 두 프리미티브 detour 설치(old bytes 일치) 및 호출 수 >0. ② **오라클:** S2 최종 캡처 = 같은
  프레임 800 덤프의 nearest 2배, 일치율 ≥0.999(미러가 nearest 2배이므로 같아야 한다 — 다르면 painter order/
  클립/센티널 결함). ③ 미러 제공 픽셀 비율(월드 viewport 안)과 stale 대체 픽셀 수를 보고, 월드 영역 미러 비율
  >0. ④ S1 ③ 입력 parity 유지, crash0, tick ≥300, 프레임 시간 기록(느려짐 배수).
- **판정:** S1+S2 PASS → `FEASIBLE`(다음 work가 S3·프리미티브 확장). 구조 반증(예: 프리미티브가 `+0x1514`
  외 캐시 포인터로 쓰기, 재호출이 게임 상태를 바꿈 — 난수/카운터 부작용)만 `NOT_FEASIBLE`. 하네스/환경은
  원인 추적·수리 후 재실행(구현 우선); 60분 또는 서로 다른 실패 가설 2회에도 원인 미상이면 `BLOCKED(구체 사유)`.
- **재호출 부작용 검사(필수):** S2 run의 게임 상태 해시(선택·유닛 좌표 샘플·tick)가 S1 run과 같은 입력에서
  일치하는지, 프리미티브가 전역 상태를 쓰는지 raw로 확인. 부작용이 있으면 해당 프리미티브는 제외하고 기록.

## 4. 회귀·안전

- 회귀 테스트: env 없으면 기존 동작 byte-identical(기존 trace 테스트 전부), 상호 배타 CLI 거부, old bytes
  불일치 시 detour 미설치, 센티널 판정 단위 테스트, 합성 규칙(expected800 일치/불일치) 단위 테스트, 입력 1/2
  변환 단위 테스트. `make check`, `bash checks/safety.sh check`.
- 금지: 원본/참고 저장소 쓰기, EXE 파일 패치, legacy validator 완화, 기존 raw 재사용을 현재 증거로 사용,
  G2/G5 패치 소스·`local/runtime/g2_*`·`g2shift*` 변경, 커밋.
- 게임 실행은 동기 또는 setsid+pidfile로 완주까지 대기(PROMPT ③). 끝나면 game 사본 삭제.

## 5. 남은 위험 (보고용)

- 창/전체화면 정책: 1080p 모니터에서 1200 높이 표시 정책은 미정(DESIGN §2). Wine Xvfb에서만 측정한다.
- 커서가 하드웨어 커서면 1/2 좌표계와 표시 위치가 어긋날 수 있다 — S1 ③에서 캡처로 확인.
- GDI 글자(`GetDC` 58곳)는 당분간 stale 대체(800 nearest 2배)로 남는다. 스프라이트가 아니므로 DESIGN 허용
  범위로 보되 한계로 기록한다.
- 성능: 감싼 프리미티브는 3회 그린다. 8bpp 800×600이라 여유가 있을 것으로 보나 측정으로 판정한다.
- 이 카드의 `FEASIBLE`은 G1 완료가 아니다. G1 합격은 S3 디테일 경로 + 프리미티브 확장 + 원본/후보 나란히
  실제 입력(선택/드래그/미니맵/메뉴/생산) + 사용자 3단 승인이 필요하다.

## 6. lap772 middle 독립 검수 — `HOLD/BLOCKED(candidate correctness)`

- S1 FAIL: r4 raw를 program_state별 재계산하면 PS3 converted 236/236, PS9/7/5 converted 0이다. 메뉴는
  1600×1200 표면 좌상단 800×600에만 보이며, tick 233<300, same-frame nearest oracle도 없다.
- minimap `(150,520)`은 하네스가 물리 `(300,1040)`으로 보냈고 캡처상 실제 미니맵 내부다. no-effect는
  lap763/764의 원본 gate `0x97597c=0`과 같으므로 W60 회귀로 세지 말고, gate=1·baked target `(90,553)`을
  W60 off/on 양쪽에 동일 적용한 camera paired로만 판정한다.
- S2 FAIL·미계측: primitive 성공 설치/call/covered/stale/state-hash raw가 없고 counter도 trace에서 읽지 않는다.
  `g_covered` 미초기화, stride mask index와 logical present index 불일치, expected snapshot 미보존, 부분 설치
  rollback/byte restore 부재가 카드 §2/§4와 충돌한다. 하단 HUD 파편 visual-verdict 15/100 `fail`.
- 다음 work는 먼저 동작 회귀 테스트(mask 초기값, stride=832 logical mask, painter-order stale fallback,
  unsupported old-byte 부분설치 rollback)를 추가한 뒤 최소 수정한다. 그 후 primitive call>0, covered>0,
  stale 수, source/present hash·nearest≥0.999, 동일 입력 state hash, crash0, tick≥300을 raw로 남긴다.
- 위 PASS 전 S3 착수·`FEASIBLE` 승격 금지. 상세 `docs/history/laps/
  20260929_lap772_middle_g1_w60_r4_independent_review_hold.md`와 `loop/ESCALATE_SOL`.
