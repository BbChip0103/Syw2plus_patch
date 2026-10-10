# 2026-10-07 | lap1154 | G1 middle — H-OS1 독립 검수·수용(PS7 partial·PS5 FAIL), H-OS2 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 게임 코드·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1153 work). 원문을 byte 일치로 `docs/history/laps/20261007_lap1154_preserved_lap1153_escalate_sol.txt`(SHA256 `7599ef3dddc3…`, cmp 일치)에 보존한 뒤 삭제했다. 그 밖 입력은 lap1153 기록과 lap1152 사전등록 §6이다. INBOX 새 사용자 지시 없음(마지막 = lap1153 처리 메모; 18:48 철회 항목은 루프 범위 밖), APPROVALS 새 반려·사용자 G1 시험 결과 없음(lap1152 요청 대기, 비차단), `loop/STOP` 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. pair `execution_source.unchanged == true`.
- fixture: 재실행 없음. lap1153 raw만 재계산했다(`--new-game-path` on1·on2·off1·a7, NG5 플래그 ng5, 비합성 save006 pair 1회).
- 가설(검수 대상): H-OS1 — PS7 접속방식 화면 stale은 기존 hook `0x465E80`(단색 사각형)이 폭>320 사각형을 `reject_size`로 거부해서 생기며, 폭 제한 해제(타일 적용, 기본 켬·`SYW2_G1_RECT_SOLID_WIDE=0` 끔)로 수리된다.

## 1. 출처

- source SHA 12자리: `g1_mirror2x.c` `8c924715ccbd`·`direct_draw_trace.c` `ee3f5d06fa25` = lap1153 기록. `tools`·`tests`·`checks`·`patches`·`Makefile` 아래에 `logs/gates/lap1153-work-full-check.log`보다 새 파일 0개 → lap1153 full PASS 뒤 source 변경 0.
- `lap1153-work-full-check.log` SHA256 `877417cb7acd…`, 끝줄 `1824 passed, 5 skipped in 846.03s`·`All checks passed!`·`CONTEXT_PASS`, `.exit` 0. safety 로그 `SAFETY_PASS`.
- run exit: on1·on2·off1·ng5·pair 0, a7 2(공개된 PS5 barrier 타임아웃). `local/runtime/lap1153*/game` 0개. 디스크 여유 60G.

## 2. 독립 재계산 (새 스크립트, work 스크립트 재사용·import 없음)

공유 temp `20261007_lap1154_middle_review/`:

| 파일 | SHA256 |
|---|---|
| `recalc_lap1154.py` | `de845763842b…` |
| `recalc_lap1154.json` | `1c90d4c85e9d…` |
| `rebuild_lap1154.py` | `dce8a63d2cf2…` |
| `rebuild_lap1154.json` | `b1c736c0ef27…` |
| `rebuild/_inmm.dll` | `40d2457ec108…` |

정착 구간은 세 가지로 잡았다(상태 present 후반부·마지막 40·10번째 이후). 세 정의 모두 같은 값이 나왔다. 캡처 판별은 독자 Scale2x(활성 조건 B≠H·D≠F를 먼저 계산하는 다른 구현)로 했다.

**판정 불일치 0, 정정 1(§3).**

| 항목 | 재계산 | work 값 | 판정 |
|---|---|---|---|
| PS7 정착 HD min / stale max (on1·on2·off1) | 99.627·99.627·98.166 / 1,790·1,790·8,803 | 동일 | 일치 |
| PS5 정착 HD min / stale max (on1·on2·off1) | 98.801 ×3 / 5,754 ×3 | 동일 | 일치 |
| PS9 정착 HD min | 100 ×3 | 동일 | 일치 |
| PS7 캡처 nearest 블록 (on1·on2·off1) | 798·798·799 | 동일 | 일치 |
| PS5 캡처 nearest 블록 (on1·on2·off1) | 2,426·2,427·2,426 | 동일 | 일치 |
| `rect_solid_465E80` off1 `reject_size` / on `wide_calls` | 149(= PS7 present 149) / 155·151(= PS7 present) | 동일 | 일치 |
| on1 `reject_target` / ng5 `reject_target` | 1,597/1,842 / 8,016/8,842 | 동일 | 일치 |
| ng5 PS3 present / HD min / ng5 `wide_calls` | 2,984 / 100 / 151(= ng5 PS7 present 151 → PS3 wide 0) | 동일 | 일치 |
| 후보 hresult≠0 / fallback / `covered_pixels`≠480,000 (5 run) | 0 / 0 / 0 | — | 확인 |
| a7 `layer_drift.jsonl` | 64줄 = `target`/stride 360 51 + `size`/stride 1600 13, size 13줄 전부 `(200,210)-(564,230)` 색 248 | 동일 | 일치 |
| a7 screen watch 슬롯0 마지막 writer | `0x465F01` 값 248(= 사각형 색), 스택 `0x40509B←0x4CB4D9←0x4B9102` | 동일 | 일치 |
| pair-result | `d28b3baa662e…` PASS·scene_state_equal·input_effect·minimap parity·V2/V2s/V2q/Scale2x PASS, trace_close FAIL·mirror_validator BLOCKED(기존 공개 2건과 같은 원인) | 동일 | 일치 |

## 3. 정정 1 — "사각형 7,665 px ≈ 정착 stale 8,793의 87%"는 면적 비율이지 수리 효과가 아님

- `0x465E80`은 포함 경계(`g1_mirror2x.c:4099-4103` sorted inclusive)라 사각형 면적은 365×21 = 7,665가 맞다.
- 그러나 수리로 실제 줄어든 정착 stale은 off1 8,803→on 1,790(max), 8,793→1,780(마지막 present) = **7,013 px(79.7%)**다. 면적의 나머지 652 px은 수리 없이도 다른 미러가 덮는 부분이다. 판정 영향 없음.

## 4. 추가 공개 — 가시 효과 ≈ 0 (H-RS3와 같은 coverage 계측 수리 성격)

- on1↔off1 PS7 캡처 stale 마스크 차이는 **1 블록**(off에만 1, on에만 0, 공통 798)이다. 사각형 안 캡처 stale은 on 305·off 306 블록이고, 전부 막대 위 글자다.
- 이유: stale 화소는 present 때 현재 논리 프레임의 nearest 2×로 채워지고(lap1146 확인), 단색 사각형은 nearest = Scale2x다. 그래서 이 수리는 화면 모양을 거의 바꾸지 않고 coverage 계측을 바로잡는다. 사용자 시험판 재스테이징 사유가 아니다.
- ng5 PS5는 체류 674 present에서 HD min 98.719·stale 6,147로, 짧은 run(88~89 present) 98.801·5,754보다 낮다. 같은 run의 끔 대조가 없어 수리 영향은 판단하지 않는다(PS5 경로는 `wide_calls` 0, 공개 관측).

## 5. 독립 재조립 → bridge DLL 대조: 타임스탬프 마스크 일치

- lap1152 방식 그대로: manifest 원본 입력 62개 SHA = 트리, `runtime_bridge.c` = manifest = bridge, 그 밖 소스 62개 = bridge, Makefile `SRCS`·`inmm_stub.c` `supply_probe` 2줄 변환 일치 → mingw `make` rc 0.
- 재빌드 457,946 B, on1 bridge DLL(`9a131267be21…`)과 다른 바이트 6개(136·137 COFF TimeDateStamp, 216·217 CheckSum, 347652·347653 export TimeDateStamp) → **타임스탬프·체크섬 외 동일**. on2·off1·ng5·pair bridge도 같은 마스크 안(on2 5바이트). off1은 같은 DLL에 env만 끈 대조다.
- a7 bridge(457,256 B)는 수리 전 DLL(귀속 run)이라 대조 대상이 아니다.
- 문자열: `SYW2_G1_RECT_SOLID_WIDE` 1회. `g1_mirror2x.c:731` 정확히 `"0"`일 때만 끔 → 기본 켬.
- 코드 검토(`g1_mirror2x.c:4104-4181`): `g_rect_solid_before`를 800×600으로 키우고 폭>320 또는 높이>160이면 기존 `g1_overlay_blt_apply_tiled`(H-D2t 선례)를, 작은 사각형은 기존 경로를 쓴다. 끔이면 이전 `reject_size`와 같다. 대상 판정(`reject_target`)은 바뀌지 않았다. 결함 없음.

## 6. 판정

- **H-OS1 수용: PS7 `PASS(partial, 기술·격리)` — coverage 계측 수리, 가시 효과 ≈ 0. PS5 `FAIL(무변화)`.** 사전등록 측정식(HD min ≥99.5 그리고 nearest 블록 ≥80% 감소)대로다.
- OS1-1 "표본 3개 중 2개 같은 writer" 미충족은 공개대로 수용한다. 슬롯0은 reject 로그라는 직접 근거로 귀속됐고, 슬롯1(마지막 writer = 미러된 `0x4662DE` 전면 메뉴 복사)·슬롯2(wined3d tid 288 후행 쓰기)는 UNKNOWN으로 남긴다.
- 하네스 결함(backlog): `--screen-watch-state 5`를 켜면 PS7→PS5 전환 barrier가 타임아웃한다(a7).
- 이것은 G1 사용자 합격도 G1 마감도 아니다. 재스테이징은 하지 않는다(가시 변화 없음).

## 7. 다음 work 사전등록(Sonnet) — H-OS2: PS5·PS7 GDI 글자 대상 거부 귀속 → 조건부 수리

**근거.** on1 PS5 캡처 stale 마스크(2,426 블록, `20261007_lap1153_work_hos1/on1/ps5_stale_mask.png`)를 원본 캡처와 겹쳐 보면 거의 전부가 **GDI 글자**(지도 목록 9줄, 옵션 이름 7개와 값 버튼 글자, 자리 버튼 글자, 사용자 줄)와 **버튼 얇은 테두리**(자리 버튼, 확인·취소)다. PS7 잔여 798도 글자다. 같은 run에서 TextOutA hook은 호출을 보지만 `reject_target`(렌더러 버퍼가 화면 800×600이 아님)으로 많이 거부한다(lap1109 run 누계 11,950 중 4,699). PS3에서는 같은 hook이 정상 미러한다. 그래서 가설은 **메뉴 화면 글자는 렌더러가 화면이 아닌 버퍼에 묶여 있을 때 그려지는 GDI DC로 그려져 대상 판정에서 거부된다**이다. 사용자 판정 2026-09-30 22:2x(G1 완료 = HD 그림, nearest 2×만으로는 미완)에 따라 매 새 게임에 거치는 두 화면 글자는 G1 범위다. 가시 효과는 글자 가장자리라 작다는 점을 미리 공개한다.

- **OS2-0 진단(TDD, 옵트인):** `mirror_textout`의 `reject_target` 분기에 `layer_drift`가 켜졌을 때만 쓰는 로그(상한 64줄, `rect_solid_reject_log` 형식 따름)를 추가한다. 필드 = program state, x·y·length·extent, 렌더러 buffer·stride·height, 그리고 DC의 대상 정보(`GetCurrentObject(hdc, OBJ_BITMAP)` + `GetObject`로 bits 포인터·폭·높이·stride; 실패하면 0). 상태별(5·7·그 밖) `textout_iat_reject_target` 분리 계수를 새 요약 키로 추가한다(기존 키 불변). 테스트 RED→GREEN.
- **OS2-1 귀속(격리 1~2 run, screen watch 없이):** `--new-game-path --layer-drift`. **PASS(귀속)** = PS5 거부 TextOutA 사각형(x−1..x+cx+1)이 PS5 캡처 stale 블록의 ≥60%와 겹치고, 그 DC 대상이 다음 중 하나로 정해짐: (i) 화면(present 원본) 메모리와 같은 bits이지만 렌더러 바인딩만 다름, (ii) 나중에 알려진 복사 호출로 화면에 1:1로 옮겨지는 화면 밖 버퍼, (iii) 그 밖(GDI 전용 표면 등).
- **OS2-2 조건부 수리(1회 한도):** (i)이면 `mirror_textout`이 DC bits가 화면 메모리와 1:1(stride·높이 일치)일 때 대상을 받아들이는 최소 확장. (ii)이면 그 복사 호출의 기존 미러가 글자가 들어간 원본 영역을 Scale2x하도록 하는 최소 확장. (iii)이면 수리하지 않고 BLOCKED 보고. 기본 켬 + 정확히 `=0`이면 끔 env(이름은 구현자 재량, 기존 형식). 버튼 테두리(`0x465E80`/`0x465B30` stride 360 `reject_target` 후보)는 이번에는 계수·위치만 보고한다.
- **측정식:** 켬 2 run·끔 1 run에서 PS5·PS7 정착 HD min(현재 98.801/99.627)과 캡처 독자 Scale2x 판별 nearest 블록(현재 2,426/798). **PASS** = PS5 nearest 블록 ≥50% 감소(≤1,213) 그리고 PS5 HD min ≥99.5. **partial** = PS5 nearest ≥10% 감소, 회귀 없음. **FAIL** = 그 밖. 끔은 현재 값을 재현해야 한다.
- **비회귀:** PS9 HD 100, NG5 플래그 PS3 HD min ≥99.9·안전 7종 0·dropped 0. TextOutA 대상 판정은 PS3에서도 실행되므로 **save006 full pair 1회 필수**(gate가 lap1153 pair와 같아야 함).
- **중단:** 실패 가설 2회 또는 60분이면 멈추고 근거를 남긴다. 공통: 디스크 ≥20GiB(현재 60G), run 뒤 game 사본 삭제, 원본/참고 쓰기·커밋·`260921_temp` 금지. 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).

backlog 추가: `--screen-watch-state 5` PS5 barrier 타임아웃(하네스). 기존 backlog(STATUS)는 유지한다.

## 8. 검사

- 결과는 STATUS 검증 줄에 보강한다(safety·context·focused).
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. C·하네스·테스트 source는 lap1153 full PASS 1824 그대로다(§1).

## 다음 행동

work(Sonnet) H-OS2(§7). 사용자 G1 시험 결과가 오면 최우선이다.
