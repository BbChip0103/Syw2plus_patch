# 2026-10-07 | lap1137 | G1 middle — H-TI0(타이틀 인트로) 기존 raw로 판정 종결, H-TM0(타이틀 메뉴 미측정 버튼 4개) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 게임 코드·하네스·테스트 변경 0, 커밋 0.
- 입력: STATUS "다음 한 가지"(work H-TI0, lap1136 기록 §7)를 확인했다. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1136 재요청 대기, 비차단), `loop/STOP` 없음.
- `loop/ESCALATE_SOL`: lap1136 middle이 **root**에게 보낸 전달문이다(lap1135 묶음 시험판을 `260921_temp` 새 폴더로 전달). middle이 처리할 대상이 아니므로 lap1105 선례대로 내용을 바꾸지도 지우지도 않았다. root 처리를 기다린다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 직접 재계산해 MATCH(읽기만).
- 출처: `tools`·`tests`·`checks`·`patches`·`Makefile` 아래에 `logs/gates/lap1133-work-full-check.log`보다 새 파일은 0개다(gitignore된 OMC hook 상태 파일만 있음). `g1_mirror2x.c` `1213c4abb660`, `direct_draw_trace.c` `5ee7c6e90021`, 하네스 `8c22de763922`는 lap1136 §1과 같다.
- fixture: 재실행 없음. lap1135 raw 4 lane(pair save006 비합성 baseline·candidate, vs `victory-poke` baseline·candidate 시도 2)만 다시 읽었다.

## 1. H-TI0 전제 검수 — 기존 raw로 답이 나온다

새 스크립트: 공유 temp `20261007_lap1137_middle_review/intro_lap1137.py`(`12a806091dd8…`) → `intro_lap1137.json`(`9819f4fbe25a…`). work 스크립트는 재사용하지도 import하지도 않았다.

| lane | 인트로 합계(PS40+60+180) | 모드 호출 | 640×480 구간 길이(ms) | 640×480 뒤 primary | 색 채움 외 Blt | mirror2x_present | GStreamer-CRITICAL |
|---|---|---|---|---|---|---|---|
| pair baseline | 1,730 ms | 11 | 59·44·33·33·43 | 640×480×16 | 0 | 0 | 24줄 |
| pair candidate | 1,833 ms | 11 | 63·47·37·39·46 | 640×480×16 | 0 | 0 | 24줄 |
| vs baseline | 1,738 ms | 11 | 58·43·31·31·43 | 640×480×16 | 0 | 0 | 24줄 |
| vs candidate | 1,821 ms | 11 | 66·49·39·40·48 | 640×480×16 | 0 | 0 | 24줄 |

- 모드 열은 네 lane이 같다: 800×600×8 → (640×480×16 → 800×600×8)×5. 후보는 800×600×8만 1600×1200×8로 바꿔 전달하고, 640×480×16은 그대로 전달한다(`native_2x_skip_reason = exact_800x600x8_call_gate_mismatch`, hresult 0). 640×480 동안 primary는 두 lane 모두 640×480×16(pitch 1,280)으로 다시 만들어진다.
- **인트로의 정체는 MPEG 영상 재생이다.** EXE에는 `movie\openplus.mpg`·`movie\hqteamlogo2.mpg`·`movie\endingplus.mpg`·`movie\open.mpeg`·`movie\samsunglogo.avi` 문자열과 `CLSID_AMMultiMediaStream`·`IID_IAMMultiMediaStream`·`IID_IDirectDrawMediaStream`·`MSPID_PrimaryVideo` GUID 바이트가 있다(`0xE67A8..0xE67E8`). 즉 DirectShow 멀티미디어 스트림으로 DirectDraw 표면에 디코드하는 구조다. 게임 폴더 `movie/`에는 `OPENPLUS.MPG`(24.5MB)·`hqteamlogo2.mpg`(8.1MB)·`ENDINGPLUS.MPG`가 있다. `open.mpeg`·`samsunglogo.avi`는 없다.
- **하네스에서는 영상이 재생되지 않는다(양 lane 공통).** 640×480 구간은 매번 31~66 ms이고, 그 안에 영상 프레임 Blt는 없으며 색 채움 Blt(`flags 0x01000400`, caller `0x4D1066`)만 있다. 네 lane `probe.log`에는 모두 winegstreamer `gst_element_set_state: assertion 'GST_IS_ELEMENT (element)' failed` 묶음 6개(24줄)가 인트로 시각(약 0.35초 폭)에 찍혀 있다. GStreamer 요소를 만들지 못해 스트림 열기가 실패하고, 게임은 곧바로 다음 상태로 넘어간다. 호스트에는 32비트 `libgstlibav`·`libgstmpeg2dec`가 있다. 그래서 실패 원인은 디코더 부재가 아니라 Wine 9.0 amstream/winegstreamer 쪽이다(상세 UNKNOWN).
- **후보 훅은 인트로에서 통과만 한다(정적).** `g1_present_gate_decide`는 목적지가 1600×1200 primary여야 한다(`g1_present_contract.h` 104행). stretch 경로는 `record->width == 1600`을 요구한다(`direct_draw_trace.c` 1429행). `hook_blt` 미러와 overlay는 `read_state(0x4ED818) == 3`일 때만 켜진다. `g_native_2x_split_applied`는 1로 남지만 위 크기 조건 때문에 640×480 primary에서는 쓰이지 않는다.

## 2. H-TI0 판정 — 종결, work로 보내지 않음

- **판정: (A) 원본 구성 그대로(정적·trace 근거) + 영상 표시 런타임 관측 BLOCKED(하네스 환경).** 원본도 영상을 640×480×16 전체화면으로 보여 준다. 후보도 같은 모드·같은 primary 크기로 같은 경로를 탄다. 영상은 800×600 UI가 아니므로 G1 HD 대상이 아니다.
- lap1136 §7 사양("각 구간 2장 이상 캡처")은 현재 하네스에서 지킬 수 없다. 관측할 영상 프레임 자체가 두 lane 모두 없기 때문이다. work 회차를 쓰면 §7의 BLOCKED 조항으로 끝난다는 것을 미리 알 수 있으므로 dispatch하지 않는다. 같은 관측을 반복하지 않는다.
- Wine 영상 재생을 고치는 일(winegstreamer/패키지)은 새 의존성이고 G1 이득도 없으므로 하지 않는다. backlog에만 둔다.
- 남는 위험(실제 Windows): 인트로 동안 모드가 1600×1200×8 ↔ 640×480×16으로 바뀐다. 원본은 800×600 ↔ 640×480이다. 실제 모니터·DxWnd에서 1600×1200 모드 전환이 되는지는 이미 사용자 시험 미검증 항목("실제 Windows 1600×1200 모드")에 들어 있다. 새 질문은 만들지 않는다.

## 3. 다음 work 사전등록(Sonnet) — H-TM0: 타이틀 메뉴 미측정 버튼 4개의 화면 HD 관측

**근거.** 타이틀 메뉴(`menu.png`, 800×600 논리 좌표)에는 버튼 8개가 있다. 측정한 경로는 불러오기(PS35, H-P35)와 임의게임(PS7→PS5→PS2→PS3, NG 계열)뿐이다. 사용자가 누를 수 있는 시나리오·사용자변경·캐릭오픈방·서장 화면은 HD coverage를 한 번도 측정하지 않았다. EXE가 `[0x4ED818]`에 쓰는 상태 상수는 40종 이상이다(이번 정적 열거: 0x10·0x14·0x32·0x46·0x50·0x5A·0x64·0x6E·0x8C(25곳)·0x96·0xA0·0xAA·0xBE·0xC8·0xD2·0xDC·0xE6·0x13A 등). 이 중 무엇이 위 버튼에 해당하는지는 모른다.

**가설.** 네 버튼 화면 중 일부는 미러 경로 밖이다(PS35 9.4% 선례). 측정하면 다음 수리 대상(HD min <90% 상태)이 정해진다. 이번 work는 관측만 한다(수리 없음).

- **버튼 좌표(논리, `menu.png` 버튼 중심 판독):** 시나리오 `(75,505)`, 사용자변경 `(190,505)`, 캐릭오픈방 `(410,505)`, 서장 `(75,560)`. 대조로 쓰는 기존 상수는 `NEW_GAME_MENU = (184,560)`(임의게임)이다. 제외: 불러오기 `(302,505)`(측정 완료), 임의게임(측정 완료), HQNET `(302,560)`(외부 접속), 종료하기 `(410,560)`.
- **TM0-0 하네스(TDD):** 옵트인 `--title-button {scenario,user,charroom,prologue}`를 추가한다. 동작은 PS9 도달 → 해당 좌표 1회 클릭 → `program_state` ≠ 9가 될 때까지 최대 20초 대기 → 첫 비-9 상태에서 +3초·+8초에 캡처 2장(lane별) → 최대 15초 관측 → 종료다. 추가 클릭은 하지 않는다(게임 시작·파일 변경 버튼을 누르지 않음). 테스트 RED→GREEN. 기존 경로·C는 불변이다.
- **TM0-1 격리 실행:** 버튼마다 새 pair(baseline·candidate lane) 1회, 총 4회. save fixture는 필요 없다(타이틀에서 시작). 디스크 ≥20GiB(현재 123G)를 확인하고, 각 run 뒤 `game` 사본을 삭제한다.
- **측정식(lap1105 §1과 같음):** lane별 상태 열 {상태, 지속 ms, present 수}. 후보 상태별 HD = `(covered − stale) / 480,000`으로 min·p50을 낸다. 상태 첫 present(전환)는 따로 공개한다. stale max, V1 outside, 안전 7종, dropped, 모드 호출 열도 기록한다. 캡처 레이아웃은 후보 PNG와 baseline PNG nearest-2x의 차이 픽셀 비율을 기록만 한다.
- **PASS(관측):** 네 버튼 모두 두 lane에서 상태 변화가 관측되고, 두 lane의 상태 열이 같고, lane별 캡처가 2장 이상이고, 안전·크래시가 0이다. 새 상태마다 "HD OK(min ≥90%, 전환 present 제외)" 또는 "수리 후보(<90%)"로 분류한다. 수리 후보는 위치(가능하면 `--stale-mask-state`)만 적고 수리는 다음 middle이 정한다.
- **FAIL/BLOCKED:** 클릭 뒤 20초 안에 상태가 바뀌지 않으면 캡처로 좌표를 한 번 고쳐 다시 실행한다(하네스 결함이므로 반복 원칙 적용). 그래도 안 되면 그 버튼만 BLOCKED로 둔다. 사용자변경이 Windows 대화상자(GDI EDIT 등)를 띄우면 그대로 기록한다. 서장이 영상(위 §1처럼 하네스에서 재생 안 됨)이나 게임 로드(PS2→PS3)로 넘어가면 상태 열과 처음 15초의 HD만 기록한다. 60분 또는 실패 가설 2회면 멈춘다.
- 판정 밖으로 기록만 할 것: 각 버튼 상태의 `[0x4ED818]` 값과 위 정적 상수의 대응, 상태 전환 시 `set_display_mode` 호출.
- 공통: 하네스·테스트를 바꾸므로 lint·typecheck → 기록 freeze → `make check` 1회. 원본/참고 쓰기·커밋·`260921_temp` 쓰기는 금지다. **사용자 G1 시험 결과가 오면 그것이 최우선이다.**
- 연속 규칙: lap1136·lap1137 middle은 둘 다 실행 증거가 없는 회차다(연속 2회). 그래서 다음 회차는 반드시 실행 증거를 남기는 work여야 한다(PROMPT ③).

backlog 추가: Wine 영상 재생 불가(winegstreamer 요소 생성 실패) — 인트로·엔딩 영상 관측 수단 없음. 기존 backlog(STATUS, 하네스 victory-poke readback 경합 포함)는 유지한다.

## 4. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`를 돌린다. 결과는 STATUS 검증 줄에만 쓴다.
- 전체 `make check`는 SKIP한다. 이번 회차에 바뀐 것은 문서와 공유 temp 스크립트뿐이고, C·하네스·테스트 source는 lap1133 full PASS 1786 그대로다(머리말 "출처" 줄).

## 다음 행동

root: `loop/ESCALATE_SOL`(lap1136)을 처리한다(묶음 시험판 전달). work(Sonnet): §3 H-TM0. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.
