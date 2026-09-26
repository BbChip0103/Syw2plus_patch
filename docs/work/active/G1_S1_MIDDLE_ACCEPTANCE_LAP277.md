# G1-S1 수용 계약 확정 — lap277 middle 판정

역할: Claude Code `claude-opus-5`/high, middle tier(진단·계획·컨펌). 게임 구현 없음.
수신: lap276 Astra 결정(`G1_S1_ASTRA_DECISION_LAP276.md`)과 lap271 연구 계약
(`G1_S1_DETERMINISM_RESEARCH_CONTRACT.md`)의 §3 측정식.
이 문서는 **연구 수용 기준 확정과 work 인계 판정**이다. 제품 G1 증거도, Stage B 실행 허가도,
마일스톤 승인도 아니다. comparator/producer/회귀/테스트/원본은 한 바이트도 바꾸지 않았다.

## 0. 판정 요약

- lap271 §3 **측정식은 불충분하다 → 반려하고 아래 §3으로 대체한다.**
  Astra의 승격 사유는 문서 논리 결함으로 **확인**되었고, 기계 증거로 재현했다.
- lap276이 정의한 **work 인계 범위(정적 저장/불러오기 조사 1바퀴, 실행 예산0)는 승인한다.**
  단 §4의 산출물 표를 그대로 채우는 조건부 승인이다.
- 이 승인은 1단(기계·문서) 승인이다. work 결과는 다음 새 middle이 독립 검수한다.

## 1. 이전 바퀴(lap276) 독립 검수

- lap276 기록의 10개 SHA를 재계산했고 **전부 일치**한다(runtime_env, comparator, 회귀,
  lap275 probe, f3_review.json, 결정문서, STATUS 압축본, ESCALATE_SOL, STATUS, make-check 로그).
- lap275 probe를 이 세션에서 재실행한 출력이 lap276 출력과 **바이트 동일**하다
  (`logs/lap277/f3_review_recheck.json` = `4672c78c34d6f8d083fc00ca66ce31fa0b04541bd361a0d18cf8e8f80fb9d770`).
  failures=[] 재확인. 새 독립 검수기를 다시 작성하지는 않았다(lap275 범위 승인은 그대로 유효).
- 재검증하지 **않은** 것: M-a~M-e 변이 재실행, R17/R6-B-R2, 나머지 offline 8건. 전부 주차 유지.
- 필수 게이트 예상 밖 실패 없음. 마일스톤 경계 아님. 따라서 이번 세션은 승격 없이 판정한다.

## 2. 왜 lap271 §3 측정식이 불충분한가 (기계 증거)

probe: `docs/history/laps/probes/20260912_lap277_middle_s1_formula_probe.py`
(offline 합성 JSON만 사용, 게임/Wine/Xvfb/PNG 0회).
출력: `logs/lap277/s1_formula_probe.json`, 7케이스 자체검사 failures=[].

측정식 `scene.status=="PASS" AND 세 stage 모두 != UNKNOWN_SLOT_CORRESPONDENCE`는 두 가지로 샌다.

**(가) 공허하게 참이 된다.** 관측이 아예 없으면 부정 조건은 자동 성립한다.
- `vacuous_missing_stage`: 후보에서 drag_select 입력을 통째로 제거 → 측정식 **참**, overall INCONCLUSIVE.
- `vacuous_missing_selection_count`: after selection count 결측 → 측정식 **참**, overall INCONCLUSIVE.

**(나) overall PASS로 조여도 여섯 항목 중 1·5·6은 덮이지 않는다.**
- `blind_to_items_1_5_6`: nation(1→4), 비선택 개체의 engine slot id(11,20→111,120),
  첫 입력 직전 절대 selection count(0→5, delta 동일), scene.camera([0,0]→[50,50]),
  scene.tick(1000→987654), minimap 직전 camera([0,0]→[3,3])가 전부 달라도 **overall PASS**.
- `blind_to_foreign_owner`: 후보에만 owner=2 개체를 추가해도 **overall PASS**.

**덮이는 것(대조군).**
- `multiplicity_owner01_control`: owner0에 동일좌표 중복 개체 1개 추가 → UNKNOWN_SCENE_MISMATCH.
  즉 항목2·3의 **중복/개수는 `relative_world_offsets`가 리스트라 실제로 잡힌다**(owner 0/1 한정).
- `slot_demotion_control`: 정규화 identity가 같고 engine slot id만 다른 쌍
  → 두 stage가 UNKNOWN_SLOT_CORRESPONDENCE, overall INCONCLUSIVE. **F2-R2 강등 규칙은 그대로 살아있다.**

근거 코드(읽기만 함): `tools/compare_g1_stage_b.py`의 `_scene_signature`(:111-131)가 만드는 키는
`owner0_unit_types`/`owner1_unit_types`/`relative_world_offsets`/`world_bounds` **네 개뿐**이고,
`_scene_report`(:134-159)가 검사하는 것도 그 네 개뿐이다. `scene.owners`/`scene.camera`/
`scene.tick`은 comparator가 **한 번도 읽지 않는다**. `_unit_records`(:98-110)는 offsets를
`if owner in (0, 1)`로 거르고 type은 `sorted(set(...))`로 집합화한다. slot 동등성은
`_stage_report`(:363-370)에서 **선택된 1개 slot**에만, unit_select/drag_select에만 적용된다.

이것은 comparator 결함 주장이 아니다. comparator는 선언된 네 장면 축과 입력 패리티만
주장하도록 설계돼 있다. 결함은 **"comparator PASS면 여섯 항목이 복원됐다"고 읽은 lap271 §3 문장**이다.

## 3. 대체 측정식 (lap271 §3 요약식을 이것으로 교체한다)

같은 fixture로 얻은 두 evidence가 **S1 충분**하려면 (A)와 (B)를 **동시에** 만족해야 한다.
새 PASS 경로를 만들지 않는다. comparator의 PASS는 **필요조건일 뿐 충분조건이 아니다.**

**(A) 기계 조건** — `compare_g1_stage_b.compare_evidence(...)["status"] == "PASS"`.
부정식이 아니라 overall PASS를 쓴다. 이것이 (가)의 공허한 참을 닫는다.
overall PASS는 scene 4축 일치 + 세 stage 전부 PASS(양측 source result PASS, 정수 selection count,
해소 가능한 identity, 선택 slot 동등, minimap 카메라 이동·목적지 일치) + input_errors 없음을 요구한다.

**(B) 원시 필드 대조 기록** — comparator가 읽지 않는 축을 work/검수 tier가 **직접 나란히 기록**한다.
어느 한쪽이라도 결측/None/비정수면 그 항목은 **UNKNOWN이며 절대 PASS로 쓰지 않는다.**

| 항목 | 관측 출처(파일:필드) | 양성 일치 조건 | 결측 시 |
|---|---|---|---|
| 1 nation/player | `scene.owners["0".."7"].nation`, `.active_units` (`tools/runtime_env.py:_g1_scene_snapshot` :2399-2430) | 8개 키 전부 nation·active_units 동일 | UNKNOWN |
| 2 owner별 type·개수 | `scene.unit_slots[].owner/.type` | owner별 type **다중집합**(집합 아님) 동일 | UNKNOWN |
| 3 상대 world 위치·중복 | `scene.unit_slots[].world.x/.y` | anchor 기준 `(owner,type,dx,dy)` 정렬 **리스트** 동일(중복 보존) | UNKNOWN |
| 4 world bounds | `scene.world_bounds.width/height` (`read_memory(0x00B3DE34,4)` `<2h`, 1..180 가드) | width·height 동일 | UNKNOWN |
| 5 engine slot id | `scene.unit_slots[].slot` 전부 + stage `after.selection.selected_slot` | **모든** 개체의 `(slot,owner,type,x,y)` 정렬 리스트 동일. 선택 slot만 같은 것으로 대체 불가 | UNKNOWN |
| 6 첫 입력 직전 기준점 | `inputs[].before.selection.count` (`G1_SELECTION_COUNT_ADDRESS=0x00899024`, `<i`, :1340/:1620), `inputs[].before.camera`·`scene.camera`(`_read_camera` :1966), `scene.tick`·`inputs[].*.tick` | 절대 selection count 동일, 절대 camera 동일, tick은 아래 §3.1 | UNKNOWN |

항목2·3은 `sorted(set(...))`가 아니라 **다중집합/리스트**로 비교해야 한다. 근거: comparator의
owner type 축은 집합이라 개수를 잃지만 offsets 축은 리스트라 개수를 지킨다(대조군 4).
(B)에서는 애매함이 남지 않도록 두 축 모두 개수를 보존해 기록한다.

### 3.1 tick 판정 (Astra가 middle에 명문화를 요구한 항목)

**절대 tick 일치는 요구하지 않으며 요구해서도 안 된다. 공통 기준점 대비 비교로 확정한다.**
근거: (a) `scene.tick`은 program state reader가 주는 진행 카운터이고, 현재 계약이 그것에
거는 유일한 조건은 PS5→PS3 경계의 **생존성 `tick > 0`**이다(`tools/runtime_env.py:3030-3033`, `:3910`).
(b) comparator는 tick을 어떤 경로에서도 읽지 않는다(§2). (c) 두 run의 절대 tick을 맞추려면
정지/시드 개입이 필요한데 lap271 §5가 seed 오프셋 추측과 바이너리 패치를 금지한다.
따라서 요구 사항은: 두 run 모두 **선언된 동일 기준 사건**(scene snapshot, 각 stage before/after)에서
tick을 기록하고, 패리티는 scene snapshot tick을 0으로 둔 **delta**로 보고한다.
허용 오차 숫자는 이 tier의 권한이 아니다. runtime 쌍을 승인받기 전에 근거와 함께 상위에 제출한다.
저장 파일이 turn/tick 카운터를 담는지는 이번 정적 조사의 산출물이며, 못 읽으면 UNKNOWN이다.

### 3.2 이번에 발견한 알려진 한계 (기록만, 수리 계열 열지 않음)

- `scene.owners`는 `range(8)`로 owner 0~7만 만든다(`:2402`, `:2405`). `relative_world_offsets`는
  owner 0/1만 본다. **owner 8~15는 현재 장면 서명에서 구조적으로 보이지 않는다.** G3 작업 때
  반드시 다시 꺼내야 할 항목이다. 지금은 G1 범위가 아니므로 수리하지 않는다.
- lap275가 남긴 M-d/M-e 추출기 사각, R17, R6-B-R2, 나머지 offline 8건은 **그대로 미결 주차**다.

## 4. work 인계 판정 — 조건부 승인

**승인한다:** lap276이 정한 정적 저장/불러오기 조사 **1바퀴**. 수행 tier는 work
(Luna/high 또는 Sonnet5/high)의 **새 세션**이다. middle/상위가 대신 구현하지 않는다.

산출물은 아래 표를 **여섯 행 모두** 채운 것이다. 빈 칸은 UNKNOWN으로 채우고 지우지 않는다.

| 열 | 채울 내용 |
|---|---|
| 항목 | §3 (B)의 1~6 |
| 본 것 | 파일 경로 + SHA256, 오프셋/구조, 읽은 근거(정적 문자열·임포트·과거 evidence JSON) |
| 판정 | CONFIRMED / UNKNOWN 둘 중 하나. PARTIAL은 UNKNOWN으로 적는다 |
| 왜 | CONFIRMED는 아래 양성 기준 중 어느 것을 만족했는지 명시 |
| 남은 probe | UNKNOWN이면 그것을 풀 **좁은** 다음 probe 1개 |

**CONFIRMED 양성 기준(둘 중 하나. 그 외는 전부 UNKNOWN).**
(i) 저장 파일을 읽어 **승인된 읽기 전용 주소**(`G1_SELECTION_COUNT_ADDRESS`,
`G1_MAP_WIDTH_ADDRESS/HEIGHT`, `_read_camera` 대상)에 쓰는 정적 코드 경로를 제시했다.
(ii) 저장 파일 안의 자기일관적 구조가 과거 evidence JSON의 관측값과 **1:1로 대응**함을 보였다.
"저장 파일이 존재한다", "메뉴에 불러오기가 보인다"는 **CONFIRMED가 아니다**(lap271 §5 재확인).

**경계(위반 시 STOP).** 게임/Wine/Xvfb/Stage B/원본 재실행/R6-A/R6-C **예산0**.
원본 트리 쓰기 금지, seed 주소 추측 금지, 저장 포맷 추측 파싱 금지.
comparator/producer/회귀/PASS 규칙/slot 강등 규칙 변경 금지. 맵 갈래(b)는 기록만 하고 열지 않는다.
최대 60분 또는 실패 가설 2회. **(B) research blocker도 합격 산출물이다.**
결과는 다음 새 middle이 독립 검수한다. 자기 승인 금지. 커밋은 LOOP_ALLOW_COMMITS=1에서만.

## 4.1 lap278 work 결과 — 정적 저장/불러오기 조사

조사 범위는 원본 EXE와 상위 원본 디렉터리의 저장 파일을 읽기 전용으로 확인하는 한
갈래였다. 게임/Wine/Xvfb/Stage B/원본 재실행은 0회이며, 저장 포맷을 추측 파싱하지
않았다. `CONFIRMED`는 이 문서 §4의 (i)/(ii)만 사용했다.

| 항목 | 본 것 | 판정 | 왜 | 남은 probe |
|---|---|---|---|---|
| 1 nation/player 구성 | `Syw2plus/syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; save entry `0x440C20`, load entry `0x440FF0`; 과거 JSON `run2_*`, `run4_*`의 `state.players` | UNKNOWN | 저장/불러오기 함수의 명시 인자가 승인된 player base `0x956770` 또는 nation/active 구성 필드로 연결되지 않았고, 과거 JSON에는 save000/006과의 1:1 파일 매핑이 없다. | 두 entry에서 호출하는 serializer의 destination/source를 `0x956770 + owner*0x3ABC` 및 nation 필드까지 정적으로 끝까지 추적한다. |
| 2 owner별 type·개수 | 같은 EXE/entry; `tools/runtime_env.py`의 `scene.unit_slots[].owner/type`; 과거 evidence JSON의 `state.units` | UNKNOWN | 과거 unit 목록은 관측 증거일 뿐 저장 파일 내부 구조와 대응하지 않는다. 저장/로드 entry에서 전체 unit roster의 serializer mapping이 확인되지 않았다. | load call graph에서 roster loop가 `0x66B790 + slot*0x758`의 type/owner/count를 채우는 serializer 인자를 확인한다. |
| 3 상대 world 위치·중복 | 같은 EXE/entry; `scene.unit_slots[].world.x/y`; `tools/runtime_env.py`의 승인된 scene snapshot | UNKNOWN | `state.units`의 좌표는 save 파일과 1:1로 묶이지 않았고, 저장 포맷을 해석할 구조 근거가 없다. | 위 roster serializer에서 각 unit의 x/y 필드와 중복 slot 보존 여부를 함께 정적으로 매핑한다. |
| 4 world bounds | save `0x440C20`의 map block `base=0xB3DDA8,size=0xB0`; load `0x440FF0`의 대응 read call; load 후 `0x441381`이 `WORD [0xB3DE36]`, `0x44138A`가 `WORD [0xB3DE34]`를 사용; `runtime_env.py:241-242` | CONFIRMED | (i): load serializer가 저장 데이터를 `0xB3DDA8`에 읽고, 승인 주소 `0xB3DE34`/`0xB3DE36`는 그 map block의 `+0x8C/+0x8E`이며 바로 뒤 로드 후 경로에서 직접 참조된다. | 없음(두 파일 간 실제 값 동일성은 별도 runtime 대조 전까지 제품 증거가 아님). |
| 5 engine slot id | 과거 JSON `state.units[].slot`; comparator의 선택 slot 판정; load entry와 호출 목록 | UNKNOWN | 과거 slot 관측은 파일 내부 slot field와 연결되지 않았고, entry에서 전체 `(slot,owner,type,x,y)` serializer mapping이 확인되지 않았다. 선택 slot만 비교하는 것은 충분조건이 아니다. | load roster serializer가 slot index/engine slot id를 어느 필드에 복원하는지 정적으로 확인한다. |
| 6 첫 입력 직전 selection/camera/tick | `runtime_env.py`: selection `0x00899024/28`, camera `0x00B42D7C`, logic tick 문서 `0x008924B8`; save/load 함수 disassembly | UNKNOWN | save/load entry의 명시 주소에는 selection/camera/logic tick이 없으며, `0x00892410` 참조는 승인된 tick `0x008924B8`의 근거가 아니다. 과거 JSON tick은 서로 다른 시점의 관측이고 save 파일과 1:1 매핑되지 않는다. | serializer call graph에서 세 승인 주소의 read/write 도달성을 정적으로 확인한다. 미확인 시 상위 승인 후 동일 save/load pair의 before/after runtime probe가 필요하다. |

### lap278 결론

원본은 저장 경로와 map bounds 직렬화 경로를 정적으로 확인할 수 있지만, 현재 허용된
읽기 전용 근거만으로 여섯 항목을 함께 복원하는 실행 가능한 fixture를 증명하지 못했다.
이는 저장 파일이 존재하지 않는다는 뜻이 아니라 **파일 포맷/필드 대응이 확인 불가한
research blocker**다. 과거 `save011/012` 실행 기록은 실제 load 후 상태 변화의 역사적
근거지만, 현재 S1의 (ii)인 저장 파일 내부 구조와 evidence JSON의 1:1 대응으로 승격하지
않는다. comparator/producer/회귀/PASS/slot 강등 규칙은 변경하지 않았다.

## 5. 이 판정이 아닌 것

제품 G1 합격, Stage B 실행 허가, runtime 쌍 예산 승인, 마일스톤 종료, G2~G4 전환이 아니다.
`make check` 291 passed와 probe exit0은 계획 승인도 제품 검증도 아니다.
R17/R31 금지, R29 범위 승인 거부, R30 M11 생존은 전부 이전 판정 그대로 유효하다.

## 4.2 lap279 middle 독립 검수 — lap278 §4.1 판정을 **부분 반려하고 교체한다**

역할: Claude Code `claude-opus-5`/high, middle tier(진단·계획·컨펌). 게임 구현 없음.
게임/Wine/Xvfb/Stage B/원본 재실행 **0회**, 원본 트리 쓰기 0, 저장 포맷 추측 파싱 0.
근거 probe(읽기 전용, 재실행 가능): `docs/history/laps/probes/20260912_lap279_middle_s1_serializer_probe.py`
→ `logs/lap279/s1_serializer_probe.json`, **failures=[]**.

### 4.2.1 재계산한 해시 (전부 lap278 기록과 일치)

| 대상 | SHA256 | 판정 |
|---|---|---|
| `Syw2plus/syw2plus_original.exe` | `b56986e0…c9c08a8ac` | 일치 |
| 상위 `../syw2plus_original.exe` | 동일 SHA | 일치(두 사본 동일) |
| `../Syw2plus/save/save000.dat` (3,093,902 B) | `1c703551…629e719da` | 일치 |
| `../Syw2plus/save/save006.dat` (3,437,942 B) | `616b7997…9289a0d064` | 일치 |
| `tools/runtime_env.py` | `e4f6a834…22455837` | 일치 |
| `tools/compare_g1_stage_b.py` | `9b684cec…f32e426efdb` | 일치 |
| `analysis/memory_maps/population_runtime_bridge_0910.md` | `96eb29ab…fa1d1fb68` | 일치 |

lap278의 entry 주소(path builder `0x440A80`의 `%ssave\save%d%02d.dat`, save `0x440C20`,
load `0x440FF0`, map block `0xB3DDA8+0xB0`)도 전부 재현했다.

### 4.2.2 lap278이 보지 않은 것 — 블록 표 전체

lap278은 entry를 열고 map block 한 개만 확인한 뒤 나머지를 UNKNOWN으로 닫았다.
같은 두 함수에서 **`fwrite`(`0x4DA39F`) 22회 / `fread`(`0x4DA4A9`) 22회**를 전부 뽑으면
literal 블록 21개가 나오고, **save 표와 load 표가 주소·크기·순서까지 바이트 단위로 동일**하다
(`block_table_identical=true`). 즉 이 저장 포맷은 추측 파싱 없이 정적으로 완전히 열거된다.
승인된 읽기 전용 주소가 이 표의 어디에 떨어지는지는 **산술 포함관계일 뿐 해석이 아니다.**

### 4.2.3 교체된 여섯 행

| 항목 | 본 것 | 판정 | 왜 |
|---|---|---|---|
| 1 nation/player | load `0x4412DC` `fread(0x892410, 0xE397C, 1)` → `0x00892410..0x00975D8C`. 승인 player base `0x956770`(offset **+0xC4360**), nation=PlayerStruct`+0x00`, stride `0x3ABC`(`analysis/memory_maps/player_offsets.md:8,9,16`) | **CONFIRMED** | (i). 8개 PlayerStruct `0x956770..0x973D50`이 이 블록 안에 **전부** 들어간다. nation/active 구성은 저장 파일에서 그 주소로 직접 복원된다. |
| 2 owner별 type·개수 | save `0x40F4B0` / load `0x40F4F0`: `edi=0x66B790`, 존재 플래그 `esi=0x8990C8`, `WORD[esi]!=0`이면 `fread(edi,0x758,1,file)`, `esi+=2; edi+=0x758`, `esi<0x899A28`까지 | **CONFIRMED** | (i). 존재하는 슬롯마다 **0x758 레코드 전체**를 복원한다. `G1_UNIT_TYPE_OFFSET=0x8D`가 그 안이므로 owner별 type·개수는 슬롯 단위로 보존된다(집합화 손실 없음). |
| 3 상대 world 위치·중복 | 같은 `0x40F4B0`/`0x40F4F0` 경로 | **CONFIRMED** | (i). 위치는 같은 0x758 레코드 안이며 슬롯별로 개별 복원되므로 **동일 좌표 중복도 보존**된다. 단 x/y의 레코드 내 오프셋은 아직 미고정(§4.2.5). |
| 4 world bounds | save `0x440CA0`/load `0x441070` `0xB3DDA8+0xB0`; `0xB3DE34`=+0x8C, `0xB3DE36`=+0x8E | **CONFIRMED (근거 강화)** | (i). lap278보다 강하다: 지도 레이어 serializer `0x42A920`이 `WORD[ecx+0x8C]`×`WORD[ecx+0x8E]`를 `imul`해 원소 수를 만든다. bounds는 저장만 되는 게 아니라 **역직렬화의 크기 인자**다. |
| 5 engine slot id | 존재 배열 `0x8990C8..0x899A28` = **1200 슬롯**, 로스터 `0x66B790 + slot*0x758`, span이 `0x00892410`에서 **정확히 끝난다**(bulk 블록 시작과 일치) | **CONFIRMED** | (i). slot id는 값이 아니라 **위치**로 보존된다. load는 존재 배열을 같은 순서로 훑고 미존재 슬롯은 `rep stos`로 0으로 채워, 인덱스↔슬롯 대응이 1:1 유지된다. |
| 6 selection/camera/tick | selection `0x899024`(+0x6C14)·`0x899028`(+0x6C18), tick `0x8924B8`(**+0xA8**)가 bulk 블록 안. camera는 `0x440D15`/`0x4410E5`의 `0xB42D7C`(4B)와 `0x440D24`/`0x4410F4`의 `0xB42D80`(4B) **인접 2블록** = `_read_camera`가 읽는 `(0x00B42D7C, 8)` 정확히 일치 | **CONFIRMED** | (i). 세 축 모두 저장/복원 경로에 있다. lap278의 "entry 명시 주소에 selection/camera/logic tick이 없다"와 "`0x892410` 참조는 tick `0x8924B8`의 근거가 아니다"는 **둘 다 사실과 다르다** — `0x8924B8`은 그 블록의 +0xA8이다. |

### 4.2.4 판정

**lap278의 항목 1·2·3·5·6 UNKNOWN과 research blocker 결론을 반려한다.** 항목 4 CONFIRMED는
유지하되 근거를 강화한다. 새 게임 실행·새 권한·새 도구 없이, lap278과 **동일한 읽기 전용 범위**에서
여섯 행 전부가 §4 (i) 기준으로 CONFIRMED가 된다. lap278의 오류는 증거 부족이 아니라
**조사 미완**이다: entry의 fwrite/fread 목록을 끝까지 열거하지 않고 첫 블록에서 멈췄다.

「저 §4 (i)의 좁은 static call-graph probe로 충분한가?」에 대한 이 tier의 답은 **충분하다, 그리고
이미 수행했다**이다. 추가 probe 발주는 불필요하다.

이것은 **S1 fixture의 정적 타당성**에 대한 1단 판정이다. 제품 G1 증거도, 두 run의 실제 값이
같다는 주장도 아니다. 그것은 여전히 runtime 쌍을 요구하며 이 tier의 예산 권한 밖이다.

### 4.2.5 남은 좁은 작업 (work tier 인계, 실행 예산 0)

1. 0x758 유닛 레코드 안의 **x/y 필드 오프셋 고정**. `tools/runtime_env.py`가 좌표를 읽는 경로를
   역추적해 `G1_UNIT_TYPE_OFFSET=0x8D`처럼 상수로 확정한다. (B) 항목3 기록에 필요하다.
2. PlayerStruct에서 (B) 항목1이 요구하는 `active_units` 대응 필드 확인. nation(+0x00)은 확정.
3. §3.1 tick: bulk 블록이 `0x8924B8`을 담으므로 **저장 파일은 tick을 보존한다**. 같은 save에서
   출발한 두 run은 load 직후 tick이 같아야 한다. 이 사실은 §3.1의 delta 규칙을 **완화하지 않는다**
   (허용 오차 확정은 여전히 상위 권한). 기록만 하고 규칙은 그대로 둔다.

### 4.2.6 새로 발견한 G3 구조 경계 (기록만, 수리 계열 열지 않음)

bulk 블록은 `0x00975D8C`에서 끝난다. PlayerStruct 8개는 `0x00973D50`에서 끝나 **들어가지만**,
16개는 `0x00991330`까지 필요해 **블록 밖으로 0x1B5A4 바이트 넘친다**(`fits_16=false`).
즉 현재 저장 포맷은 **9~16번 플레이어를 직렬화할 공간이 구조적으로 없다.** 이것은 STATUS의
기존 `owner8~15` 사각(장면 서명 한정)과 **별개의, 더 깊은 저장 포맷 차원의 G3 블로커**다.
G1 범위가 아니므로 지금 수리하지 않으며, G3 착수 시 최우선으로 다시 꺼낸다.

### 4.2.7 이 검수가 바꾸지 않은 것

comparator/producer/회귀/테스트/PASS 규칙/slot 강등 규칙/원본 **전부 무변경**.
§3 (A)+(B) 측정식, §3.1 tick delta 규칙, §3.2 한계, §4 경계는 그대로 유효하다.
`make check` 291 passed(44.49s), Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, `SAFETY_PASS`.
제품 G1 합격·Stage B 허가·runtime 쌍 예산·마일스톤 종료·G2~G4 전환은 **아니다**.

## 4.3 lap280 middle 독립 검수 — §4.2를 **수용하고 두 곳을 정정한다**

역할: Claude Code `claude-opus-5`/high, middle tier(진단·계획·컨펌). 게임 구현 없음.
게임/Wine/Xvfb/Stage B/원본 재실행 **0회**, 원본 트리 쓰기 0, 저장 파일 파싱 0.
근거 probe(읽기 전용, 재실행 가능, lap279 probe와 **다른 추출 경로**):
`docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`
→ `logs/lap280/s1_crossverify_probe.json`, **failures=[]**.

### 4.3.1 재현한 것 (lap279 주장 전부 독립 확인)

lap279 probe를 그대로 재실행해 **exit 0 / failures=[]** 이고 출력이 lap279 기록과 동일했다.
추가로 원시 `objdump` 출력에서 직접 다시 읽어 아래를 확인했다 — probe 재실행에만 기대지 않았다.

| lap279 주장 | lap280 독립 확인 | 판정 |
|---|---|---|
| literal 블록 21개, save/load 주소·크기·순서 동일 | 별도 추출기로 22/22 호출 → 21블록, 표 동일 | 일치 |
| bulk `fwrite(0x892410,0xE397C,1)` `0x440F0C` / `fread` `0x4412DC` | 원시 바이트에서 확인 | 일치 |
| camera = `0xB42D7C`(4B)+`0xB42D80`(4B) 인접 2블록 | `0x440D15`/`0x440D24` 원시 확인, 합 8B | 일치 |
| 로스터 `0x40F4B0`/`0x40F4F0`, 1200슬롯×`0x758`이 `0x892410`에서 끝남 | 원시 확인 | 일치 |
| bulk 이후 로스터 순서(load `0x441305`) | 원시 확인 | 일치 |
| G3: 16 PlayerStruct가 `0x1B5A4` 넘침 | probe 자체 상수로 재계산 | 일치 |

**lap279가 말하지 않은 보강 근거:** load 로스터(`0x40F51B`)는 미존재 슬롯을
`rep stos` `0x1D6` dword = `0x758` 바이트 **0으로 채운다**. 즉 로스터 영역은 슬롯마다
읽히거나 0으로 덮이며 **잔여 상태가 남지 않는다.** 이는 lap279가 적은 것보다 강한 결정성 근거다.

### 4.3.2 정정 1 — §4.2.2 문장은 과장이다

§4.2.2의 "이 저장 포맷은 추측 파싱 없이 정적으로 완전히 열거된다"는 **성립하지 않는다.**
21개 literal 블록 **밖에** 최소 두 종류의 페이로드가 더 있다.

1. 비-literal 블록 1개: `0x440C70`의 `fwrite(esp+0x8C, 0x40, 1)` — 스택 버퍼(저장 헤더).
   주소가 상수가 아니므로 표에 잡히지 않는다.
2. **map-layer serializer 28쌍.** literal 표와 로스터 사이에서 save는
   `0x42A920`…`0x42BC40`(+`0x42AB70`) **28개**를, load는 `0x42A960`…`0x42BC80`
   (+`0x42ABA0`) **28개**를 호출한다. lap279는 이 중 `0x42A920` 한 개의 앞 `0x40`
   바이트만 봤다. 크기가 지도 bounds에서 파생되는 가변 페이로드다.

lap280이 새로 기계 확인한 것: 개수가 28로 같고, 짝은 주소 인접(델타 0x30~0xA0)이며,
**28개 save 함수 전부가 `fwrite`를, 28개 load 함수 전부가 `fread`를 호출한다.**
그러므로 이 정정은 §4.2.3 여섯 행을 **약화시키지 않는다** — 28쌍은 지형 레이어이고
여섯 행의 관측 축(player/unit/bounds/slot/selection/camera/tick)은 literal 표와 로스터
경로 안에 있다. 다만 **레이어별 원소 수가 save/load에서 같다는 것은 아직 미검증**이며,
"포맷이 완전히 열거됐다"는 표현은 이 문서에서 쓰지 않는다.

### 4.3.3 정정 2 — §4.2.5 항목1은 전제가 틀렸고 이미 사실상 해결돼 있다

§4.2.5-1은 "`tools/runtime_env.py`가 좌표를 읽는 경로를 역추적"하라고 적었다.
**`tools/runtime_env.py`에는 유닛 좌표를 메모리에서 읽는 경로가 없다.** `_g1_scene_snapshot`
(line 2384~)은 `scene_state["units"]`의 `x`/`y`를 **그대로 받아쓴다**(line 2412).
그 값을 실제로 만드는 곳은 `patches/population/runtime_driver.py` `state(detailed=True)`이며
오프셋은 이미 고정돼 있다(line 84~100):

| 필드 | 레코드 내 오프셋 | 폭 | 절대 주소(slot 0) | 원본 교차근거 |
|---|---|---|---|---|
| type | `+0x8D` | 1B | — | `tools/runtime_env.py:183` `G1_UNIT_TYPE_OFFSET` 와 일치 |
| owner | `+0x8E` | 1B | — | 위와 인접 |
| internal_id | `+0x29C` | 4B | `0x0066BA2C` | 접근자 `0x40F540`: `DWORD[eax*8+0x66BA2C]`, `eax=slot*235` |
| **x** | `+0x2A2` | 2B(부호) | `0x0066BA32` | `WORD PTR [reg+0x66ba32]` **115회, 전부 WORD** |
| **y** | `+0x2A4` | 2B(부호) | `0x0066BA34` | `WORD PTR [reg+0x66ba34]` **115회, 전부 WORD** |

x/y 참조 수가 115로 **정확히 같고** `0x4069C7`/`0x4069D1`, `0x40815D`/`0x40816B` 처럼 **항상
짝으로 읽히며**, `movsx`로 부호 확장된다 — 좌표쌍 해석과 일관된다. 접근자 `0x40F540`의
`eax*8` 배율 계산이 `slot*0x758`임도 원시 확인했다(`(ecx*3<<4 - ecx)*5*8 = 1880*ecx`).

따라서 §4.2.5-1이 요구한 "x/y 오프셋 고정"은 **CONFIRMED**다. 남은 것은 구현 작업 하나뿐이다:
그 상수를 `tools/runtime_env.py`에 이름 있는 상수로 승격하고 위 정적 근거를
`analysis/memory_maps/`에 인용으로 남기는 것. **이 tier는 구현하지 않고 work tier로 넘긴다.**

### 4.3.4 §4.2.5 항목2에 대한 정정 방향 (구현하지 않음)

(B) 항목1의 `active_units`는 **PlayerStruct 필드에서 오지 않는다.** `_g1_scene_snapshot`은
`units` 리스트를 owner별로 세어 만든다(`tools/runtime_env.py:2398-2401`). PlayerStruct 쪽
후보 필드는 `runtime_driver.py:71-73`의 `count=+0x200A` / `used=+0x200C` / `count_cap=+0x2010`
이며 `analysis/memory_maps/player_struct_2010_is_unit_cap_not_supply_0726.md`에 근거가 있다.
둘은 **다른 양**이므로(집계 vs 장부) 같다고 전제하지 않는다. 대조는 work tier 작업이다.

### 4.3.5 이번 검수의 판정

**§4.2.3 여섯 행 CONFIRMED 교체를 수용한다.** §4.2.2 문장과 §4.2.5-1 전제는 위와 같이
정정한다. 이는 **S1 fixture의 정적 타당성** 2단 판정이며, 두 run의 실제 값 동일성·제품 G1
증거·Stage B 허가·runtime 쌍 예산·마일스톤 종료가 **아니다.** comparator/producer/회귀/
테스트/PASS 규칙/slot 강등 규칙/원본 **전부 무변경**.
`make check` 291 passed(44.24s), Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, `SAFETY_PASS`.

## 4.4 lap290 middle 진단 — §4.3 probe가 lap281 상수 승격으로 깨졌다 (work 인계 사양)

lap289(work)가 lap288 지시대로 세 probe 대조를 하다가 §4.3의 lap280 probe에서 예상 밖
traceback으로 멈추고 승격했다. 이번 tier는 **원인만 확정하고 구현하지 않는다.**

### 4.4.1 원인 (CONFIRMED)

`docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py:126-133`은
`patches/population/runtime_driver.py`의 **소스 텍스트**에서 16진 리터럴을 정규식으로 읽는다:

```python
"internal_id": int(re.search(r"internal_id=i\(0x([0-9A-Fa-f]+)\)", src).group(1), 16),
```

§4.3.3이 "남은 것은 구현 작업 하나뿐"이라고 인계한 그 작업 — lap281의 상수 승격 — 이
바로 이 리터럴을 없앴다. 현재 driver는 `internal_id=i(G1_UNIT_INTERNAL_ID_OFFSET)`,
`x=h(G1_UNIT_X_OFFSET)`, `y=h(G1_UNIT_Y_OFFSET)`이고 값은
`tools/runtime_env.py:184-186`에 `0x29C`/`0x2A2`/`0x2A4`로 있다. 아직 리터럴인
`type=u[0x8D]`·`owner=u[0x8E]`는 통과하므로 dict의 **세 번째 항목(line 130)**에서 처음
`None`이 되어 `AttributeError`가 난다 — 관측된 traceback과 정확히 일치한다.
시점 근거: driver SHA가 lap280 기록 `8c2465b8…0be82e94` → lap281 기록 `ae4ff939…4e4291b5`로
바뀌었고 현재 파일이 후자다. **lap289의 변경(work probe 한 개)과는 무관하며**, 이 결함은
lap281 이후 8바퀴 동안 아무도 그 probe를 재실행하지 않아 잠복해 있었다.

### 4.4.2 측정 사실은 드리프트하지 않았다 (CONFIRMED)

추출 블록만 교체한 **진단 전용 사본**(`logs/lap290/diagnosis/lap280_scratch_lap290.py`,
저장소 probe 무변경)은 exit 0 `failures=[]`이고 그 보고서가 lap280 원본
`logs/lap280/s1_crossverify_probe.json`과 **바이트 동일**(`3d4fe30703…6a6d6a9126`)하다.
literal 21 / fwrite·fread 22·22 / layer 28 / pair_deltas {48,64,80,96,160} /
x `0x66BA32` WORD 115 · y `0x66BA34` WORD 115 · internal_id `0x66BA2C` DWORD 67 /
G3 overflow `0x1B5A4` 전부 그대로다. 이 사본은 `logs/` 밑 **비권위 산물**이며 PASS 근거가 아니다.

### 4.4.3 work tier 수리 사양 (범위: 이 블록만)

1. 대상은 `…lap280_middle_s1_crossverify_probe.py`의 **line 126-133 한 블록**뿐이다.
   보고서 스키마·(1)(2)(4)절·`failures` 규칙·창 상수는 건드리지 않는다.
2. `internal_id`/`x`/`y` 값은 `tools/runtime_env.py`의 `^NAME = 0x…$` 정의에서 읽는다
   (`G1_UNIT_INTERNAL_ID_OFFSET`, `G1_UNIT_X_OFFSET`, `G1_UNIT_Y_OFFSET`).
3. driver 결합은 값이 아니라 **이름으로** 단언한다: `field=…(NAME)` 패턴이 없으면 `failures`에
   넣는다(§4.3.3이 요구한 드리프트 가드를 잃지 않기 위해서다). `type`/`owner`는 아직 리터럴이므로
   기존 정규식을 유지한다. 형식은 `…lap282_middle_unit_offset_review_probe.py:89-105`가
   이미 쓰는 계약과 맞춘다.
4. `(x, y, internal_id) != (0x2A2, 0x2A4, 0x29C)` 가드는 그대로 둔다.
5. **성공 조건:** 수정된 probe가 exit 0 `failures=[]`이고 보고서 SHA가
   `3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126`로 재현된다. 값이 하나라도
   다르면 수리가 아니라 새 사실이므로 멈추고 middle로 되돌린다.
6. **반증력 확인:** `G1_UNIT_X_OFFSET` 정의를 in-memory로 바꾼 mutant에서 `(0x2A2,0x2A4,0x29C)`
   가드가, driver 결합 문자열을 지운 mutant에서 이름 단언이 각각 exit 1을 내는지 보인다.
7. 같은 run에서 lap279 / lap282 / lap284-middle / lap284-work 재실행 출력이
   `e848c940…`, `e0f07f3a…`, `2870383083…`, `7381b5f7…`로 불변임을 다시 보인다.
8. **금지:** 게임/Wine/Xvfb/Stage B 실행, runtime 예산 사용, `SAVE_END`/`LOAD_ENTRY` 등 창 상수
   변경, comparator/producer/PASS 규칙 변경, 원본·fixture 쓰기, 값 불일치 시의 정규식 땜질.

### 4.4.4 이 진단이 바꾸지 않은 것

lap289의 work 수리 **내용**은 이번 fresh 대조로 ACCEPT다(work probe 출력 바이트 동일,
동행 probe 3종도 바이트 동일). 그러나 lap288이 요구한 대조가 lap280에서 아직 미충족이므로
**카드 종결은 REJECT**로 남는다. S1 실제 결정성, Stage B, runtime 예산, WM_CLOSE, G3 저장
포맷 `0x1B5A4` 초과, 제품 G1~G4는 전부 미해결이고 사용자 마일스톤 승인도 없다.
`make check` 292 passed(48.76s), Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, `SAFETY_PASS`.

## 4.5 lap292 middle 독립 검수 — lap291 수리를 **ACCEPT-WITH-CORRECTION**

검수자는 lap291 기록을 신뢰하지 않고 자체 probe
`docs/history/laps/probes/20260912_lap292_middle_lap280_repair_review_probe.py`
(SHA `2aaac7a08619cc4135f4540582e611d07aa980e5380b5ec5255688cf33491335`)로 다시 측정했다.
보고서 `logs/lap292/middle_lap280_repair_review.json` SHA
`b2f7b2174c2e54515baa5227987c34aa58c4d82d2898302c3458bd6b0faa2cfc`, exit 1(아래 §4.5.3 때문).

### 4.5.1 §4.4.3 항목별 판정

| 항목 | 판정 | 근거 |
|---|---|---|
| 1 대상 블록 한정 | ACCEPT | lap290 진단 사본과의 diff가 `REPO` 한 줄(사본 전용 개조의 원복)과 line 126-133 블록뿐 |
| 2 `^NAME = 0x…$`에서 값 읽기 | ACCEPT | 세 상수 모두 `tools/runtime_env.py:184-186`에서 해석 |
| 3 이름 결합 단언 | ACCEPT | literal 회귀·다른 상수 결합 mutant 둘 다 exit 1 |
| 4 `(0x2A2,0x2A4,0x29C)` 가드 유지 | ACCEPT | 원문 유지, 값 mutant가 이 가드로 잡힘 |
| 5 보고서 SHA 재현 | ACCEPT | fresh stdout이 `logs/lap280/s1_crossverify_probe.json`과 **바이트 동일**(`3d4fe307…6a6d6a9126`) |
| 6 반증력 | ACCEPT(부분) | 요구된 두 mutant는 성립. 요구 밖 세 번째 경우는 §4.5.3 |
| 7 동행 4종 불변 | ACCEPT | `e848c940…`/`e0f07f3a…`/`2870383083…`/`7381b5f7…` 전부 일치 |
| 8 금지 준수 | ACCEPT | 창 상수·comparator·producer·PASS 규칙·원본·fixture 변경 0, 실행 0 |

provenance도 복원됐다: 수리 전 `8b75e394…5beb3247`(lap290 기록) → 수리 후
`100f991b…cb999f84`(lap291 기록, 이번 검수 재계산 일치). `tools/runtime_env.py`
`dd2ad043…8500190`, `patches/population/runtime_driver.py` `ae4ff939…4e4291b5`,
원본 EXE `b56986e0…c9c08a8ac` 무변경.

### 4.5.2 이번 검수가 자체로 만든 mutant (lap291의 두 개를 재사용하지 않는다)

사본 트리(임시 디렉터리, EXE는 symlink)에서 다섯 변형을 돌렸다.

| mutant | exit | 결과 |
|---|---|---|
| `control_unmutated` | 0 | 보고서 SHA가 저장소 run과 동일 — 샌드박스 자체는 실패를 만들지 않는다 |
| `env_value_drifted` (`G1_UNIT_X_OFFSET=0x2A3`) | 1 | `unit offsets drifted` + `no base-relative reference to x at 0x66ba33` |
| `driver_relapsed_to_literal` (`x=h(0x2A2)`) | 1 | `does not bind x to G1_UNIT_X_OFFSET` |
| `driver_bound_to_wrong_constant` (`x=h(G1_UNIT_Y_OFFSET)`) | 1 | 같은 단언이 잡음 — 이름 결합이 실제로 이름을 본다 |
| `env_definition_removed` (`G1_UNIT_Y_OFFSET` 정의 삭제) | 1 | **stdout 0바이트 + Traceback** — §4.5.3 |

### 4.5.3 정정 1건 (work tier 인계, 범위: 이 블록만)

`G1_UNIT_Y_OFFSET` 정의가 `tools/runtime_env.py`에서 사라진 사본에서 수리된 probe는
`KeyError: 'y'`로 죽는다(line 149 `pinned["y"]`). 수리가 추가한
`"{name} definition missing from tools/runtime_env.py"` 분기는 `failures`에 넣고 `continue`하지만,
그 다음 튜플 가드가 없는 키를 무조건 인덱싱하기 때문에 **그 분기는 사실상 도달 불가**다.

이것은 lap290이 진단한 것과 **같은 결함 계열**이다(상수가 옮겨지면 probe가 보고 대신 예외로 죽는다).
`NoneType.group`이 `KeyError`로 바뀌었을 뿐이다. lap281류의 상수 이동/개명이 다시 일어나면
lap280 probe는 또 stdout 0바이트로 죽고 다음 세션이 원인을 다시 파야 한다.

- **범위:** `…lap280_middle_s1_crossverify_probe.py`의 정의 누락 분기와 그 직후 튜플 가드뿐.
  값·측정·스키마·창 상수·(1)(2)(4)절·`failures` 규칙은 건드리지 않는다.
- **사양:** 정의가 하나라도 없으면 튜플 가드를 그 필드에 대해 건너뛰거나 `pinned.get(field)`로
  비교해 `failures`가 **출력된 뒤** exit 1이 되게 한다. 형식은 §4.4.3 항목3이 모델로 지목한
  `…lap282_middle_unit_offset_review_probe.py:90-107`이 이미 쓰는 부분 문자열 대조와 맞춘다.
  (이번 검수 확인: lap282 probe는 없는 키를 인덱싱하지 않아 같은 결함이 없다.)
- **성공 조건:** 정상 run은 여전히 exit 0 `failures=[]`에 보고서 SHA `3d4fe307…6a6d6a9126`,
  동행 4종도 불변. 그리고 `…lap292_middle_lap280_repair_review_probe.py`가 exit 0이 된다
  (= `env_definition_removed` mutant가 Traceback 없이 exit 1 + 명명된 failure).
- **금지:** §4.4.3 항목8과 동일. 값이 바뀌면 수리가 아니라 새 사실이므로 멈추고 middle로 되돌린다.

### 4.5.4 이 판정이 바꾸지 않은 것

측정 사실은 드리프트하지 않았다(literal 21 / fwrite·fread 22·22 / layer 28 / x·y WORD 115 /
internal_id DWORD 67 / G3 overflow `0x1B5A4`). 그러나 **S1 카드 종결은 REJECT 유지**다.
이 검수는 static probe 하네스의 건전성만 본 것이고 S1 실제 결정성, 두 run의 값 동일성,
Stage B, runtime 예산, WM_CLOSE, G3 저장 포맷 초과, 제품 G1~G4는 전부 미해결이며
사용자 마일스톤 승인도 없다. 게임/Wine/Xvfb/PNG/원본 쓰기 0.

**남은 반증력 한계(수리 요구 아님, 기록만):** 이름 결합 단언은 reader 함수 이름을 보지 않는다.
`x=i(G1_UNIT_X_OFFSET)`처럼 WORD 필드를 DWORD reader로 읽는 드리프트는 통과한다.
binary 증거는 `x`/`y`가 WORD임을 115회 확인하므로 사각은 실재한다. §4.4.3이 요구한 범위 밖이다.

## 4.6 lap294 middle 범위 재판정 — lap293 승격을 **ACCEPT, §4.5.3 범위 정정**

lap293(work)은 §4.5.3 수리를 하다 정의 누락 mutant가 `refs` 생성부에서 다시 `KeyError`로 죽는
것을 보고, 그 재인덱싱이 지시된 범위 밖이라는 이유로 확장을 거부하고 `loop/ESCALATE_SOL`로
승격했다. **그 판단은 옳다.** 이번 판정은 lap293 기록을 신뢰하지 않고 자체 probe
`docs/history/laps/probes/20260912_lap294_middle_missing_definition_scope_probe.py`
(SHA `8fe0d2575005b4d647e85c0c4377a2d132fc872a30a1e939e8b78171671ec469`)로 다시 측정했다.
보고서 `logs/lap294/middle_missing_definition_scope.json` SHA
`3b1acbddb82591962a04e94f10eae73f6839304622daf391a7e99097ffd2a756`, exit 0(`failures` 0).

### 4.6.1 측정 — 정의 누락은 세 상수 전부에서 같은 방식으로 죽는다

| 사본 | mutant | exit | stdout | 죽는 자리 |
|---|---|---|---|---|
| lap293 그대로 | control | 0 | 1,139 B, `3d4fe307…6a6d6a9126` | 없음 |
| lap293 그대로 | `G1_UNIT_X_OFFSET` 삭제 | 1 | **0 B** | `line 156` `KeyError: 'x'` |
| lap293 그대로 | `G1_UNIT_Y_OFFSET` 삭제 | 1 | **0 B** | `line 156` `KeyError: 'y'` |
| lap293 그대로 | `G1_UNIT_INTERNAL_ID_OFFSET` 삭제 | 1 | **0 B** | `line 156` `KeyError: 'internal_id'` |

lap292가 본 것은 `y` 하나였지만 결함은 상수별이 아니다. 세 경우 모두 stdout 0바이트다.

### 4.6.2 측정 — §4.5.3이 글자 그대로 허용하는 최소 수리는 **불충분**하다

임시 사본에만 `refs` 루프 가드(`if name not in pinned: continue`)를 넣고 다시 돌렸다.

| mutant | exit | stdout | 결과 |
|---|---|---|---|
| control | 0 | 1,139 B | 보고서 SHA `3d4fe307…6a6d6a9126` **바이트 동일** — 정상 경로 무영향 |
| `G1_UNIT_X_OFFSET` 삭제 | 1 | 1,083 B | `G1_UNIT_X_OFFSET definition missing…` 명명 failure |
| `G1_UNIT_Y_OFFSET` 삭제 | 1 | 1,083 B | `G1_UNIT_Y_OFFSET definition missing…` 명명 failure |
| `G1_UNIT_INTERNAL_ID_OFFSET` 삭제 | 1 | **0 B** | `line 169`(저장소 파일 기준 **line 167**) `KeyError: 'internal_id'` |

`probe_verdict = "refs guard alone is INSUFFICIENT; unguarded consumers remain"`.

### 4.6.3 판정

`pinned`를 정의 누락 분기 뒤에 인덱싱하는 자리는 **정확히 두 곳**이다(저장소 SHA
`edefa0e4…7b47f61d` 기준): line 156 `refs` 루프의 `pinned[name]`과 line 167 accessor 검사의
`pinned['internal_id']`. line 189 `unit_record_offsets` 는 `pinned.items()` 순회라 안전하다.

§4.5.3의 "정의 누락 분기와 그 직후 튜플 가드뿐"이라는 문장은 **사실 오류**다. 소비처가 하나뿐이라고
가정했으나 셋이고 둘이 무방비다. 동시에 §4.5.3의 성공 조건(lap292 review probe exit 0)은 그
범위 안에서 달성 불가능하므로 사양이 자기모순이다. 따라서 lap293은 모순을 눈치채고 멈춘 것이
맞고, 억지 확장을 하지 않은 것도 맞다.

**의도 기준으로 범위를 정정한다.** §4.5.3이 막으려던 것은 "상수가 옮겨지면 probe가 보고 대신
예외로 죽는다"이며, 그 불변식은 "정의 누락 분기 이후 `pinned`의 무방비 인덱싱이 하나도 남지
않는다"이다. line 156만 고치면 lap292 review probe(=`y`만 mutate)는 통과하는데 `internal_id`는
여전히 0바이트로 죽는다. 즉 **글자 범위를 지키면 lap290이 진단한 결함 계열이 그대로 재발한다.**

### 4.6.4 work tier 수리 사양 (§4.5.3을 대체한다, 범위: 이 블록만)

1. 대상은 `…lap280_middle_s1_crossverify_probe.py`의 **line 156과 line 167 두 자리**뿐이다.
   lap293의 `pinned.get` 튜플 가드(line 149-151)는 이미 옳으므로 **그대로 보존**한다.
2. 수리 형태는 두 자리 모두 "정의가 없으면 그 필드 검사를 건너뛴다"이다. 새 failure 문구를
   만들지 않는다 — 정의 누락은 이미 line 143에서 명명된 failure로 기록된다. `accessor` 검사는
   `internal_id`가 없으면 건너뛴다.
3. 값·측정·스키마·창 상수·(1)(2)(4)절·`failures` 규칙·comparator·producer·PASS 규칙은 건드리지
   않는다. `unit_record_offsets`/`unit_record_refs`가 mutant에서 키를 잃는 것은 허용한다
   (exit 1 + 명명 failure가 이미 그 run을 무효로 표시한다).
4. **성공 조건(세 가지 전부):**
   - 정상 run이 exit 0 `failures=[]`이고 보고서 SHA `3d4fe307…6a6d6a9126` 바이트 동일.
   - 동행 4종 `e848c940…`/`e0f07f3a…`/`28703830…`/`7381b5f7…` 불변.
   - `…lap294_middle_missing_definition_scope_probe.py`의 `as_is` 열에서 **세 mutant 전부**
     `crash=null`, `stdout_bytes>0`, 각자의 `definition missing` failure, exit 1.
     (그 probe의 `EXPECTED_SHA["target_probe"]`는 `edefa0e4…`를 가리키므로 수리 후에는 그
     한 줄만 mismatch로 보고된다. 아래 5항을 따른다.)
5. **provenance 고정:** lap292 review probe의 `EXPECTED_SHA["target_probe"]`
   (`100f991b…cb999f84`)와 lap294 scope probe의 같은 항목(`edefa0e4…7b47f61d`)은 **각 검수가
   본 상태의 기록**이다. 어느 쪽도 편집하지 않는다(lap287이 middle 소유 파일을 편집해 지적받은
   것과 같은 이유). 수리 후 두 probe가 내는 `target_probe sha mismatch` 한 줄은 **예상된
   결과**이며, work tier는 새 SHA를 lap 기록에 적는 것으로 계보를 잇는다. 따라서 §4.5.3의
   "lap292 review probe exit 0" 조건은 **철회**하고, "lap292 review probe의 failures가
   `target_probe sha mismatch` 단 하나"로 대체한다.
6. **금지:** §4.4.3 항목8과 동일(게임/Wine/Xvfb/Stage B 실행, runtime 예산, 창 상수 변경,
   comparator/producer/PASS 규칙 변경, 원본·fixture 쓰기, 값 불일치 시의 정규식 땜질).
   값이 하나라도 바뀌면 수리가 아니라 새 사실이므로 멈추고 middle로 되돌린다.

### 4.6.5 이 판정이 바꾸지 않은 것

측정 사실은 드리프트하지 않았다(control 보고서가 저장소 run과 바이트 동일). **S1 카드 종결은
REJECT 유지**다. 이 판정은 static probe 하네스의 건전성 범위만 정한 것이고 S1 실제 결정성,
두 run의 값 동일성, Stage B, runtime 예산, WM_CLOSE, G3 저장 포맷 `0x1B5A4` 초과, 제품 G1~G4는
전부 미해결이며 사용자 마일스톤 승인도 없다. §4.5.4의 reader 이름 사각(`x=i(G1_UNIT_X_OFFSET)`)도
여전히 열려 있고 이번 범위 밖이다. 게임/Wine/Xvfb/PNG/원본·구현 모듈 쓰기 0.

## 4.7 lap296 middle 독립 검수 — lap295 수리를 **ACCEPT**, §4.4.3 계열을 **종결**한다

lap295(work)의 기록을 신뢰하지 않고 자체 probe
`docs/history/laps/probes/20260912_lap296_middle_lap295_guard_review_probe.py`
(SHA `ba1f23b8769f0daf22e027b42310b6abbe6e24b2bad83a20ac746e7015babea2`)로 다시 측정했다.
보고서 `logs/lap296/middle_lap295_guard_review.json` SHA
`a690843f9c4222a8dadd1af18f6b7b89a9eae70728f40ab0249948bd7e0b584d`, exit 0(`failures` 0).
mutant 6종은 lap292/lap294의 것을 재사용하지 않고 이 검수가 새로 만들었다.

### 4.7.1 §4.6.4 성공 조건 3가지 — 전부 CONFIRMED

| 조건 | 측정 | 판정 |
|---|---|---|
| 정상 run exit0·`failures=[]`·SHA `3d4fe307…6a6d6a9126` 바이트 동일 | exit0, 1,139 B, stderr 0 B, `logs/lap280/…json`과 `cmp` 일치 | CONFIRMED |
| 동행 4종 불변 | `e848c940…`/`e0f07f3a…`/`28703830…`/`7381b5f7…` 전부 일치, exit0 | CONFIRMED |
| 세 mutant가 `crash=null`·`stdout_bytes>0`·명명 failure·exit1 | x 1,083 B / y 1,083 B / internal_id 1,073 B, traceback 0 | CONFIRMED |

lap292 review probe는 fresh run에서 top-level failure가 `target_probe sha mismatch`
(`88d86281… != 100f991b…`) **단 하나**였고 나머지(정상 run·동행 4종·mutant 5종)는 전부 통과했다.
§4.6.4 5항이 예고한 그대로다. 두 review probe의 `EXPECTED_SHA`는 편집되지 않았다
(`2aaac7a0…33491335`, `8fe0d257…671ec469` 현재도 일치).

### 4.7.2 범위 증명 — lap295 diff는 **정확히 지시된 두 자리뿐**이다 (새 증거)

이전 검수들은 "다른 곳을 안 건드렸다"를 정상 report 바이트 동일성으로 간접 추정했다. 이번에는
직접 증명한다. 현재 파일에서 §4.6.4가 지시한 두 가드만 되돌리면(`if name not in pinned: continue`
2줄 제거, accessor의 `"internal_id" in pinned and ` 제거, 합계 **80 B**) SHA가

`edefa0e4b82d39034ddd14055e09a651998d2a8c93e5d27ab0f168bc7b47f61d`

즉 lap293/lap294가 본 수리 전 상태와 **바이트 단위로 일치**한다. 따라서 lap295는 값·측정·스키마·
창 상수·(1)(2)(4)절·`failures` 규칙에 단 1바이트도 쓰지 않았다. §4.6.4 1·3항 CONFIRMED.

### 4.7.3 가드가 반증력을 깎지 않았다 (§4.6.4가 요구하지 않은 추가 확인)

`in pinned` 가드는 "정의가 있으면 예전과 같다"여야 하고 조용한 skip이 되면 안 된다.

| mutant | exit | stdout | 보고한 failure |
|---|---|---|---|
| `G1_UNIT_INTERNAL_ID_OFFSET` 값 `0x29C`→`0x298` | 1 | 1,351 B | offsets drifted + base-relative 참조 없음 + accessor 불일치 **3건** |
| driver `internal_id=i(…)` → `i(0x29C)` 리터럴 회귀 | 1 | 1,219 B | `does not bind internal_id to G1_UNIT_INTERNAL_ID_OFFSET` |
| control | 0 | 1,139 B | 없음, 보고서 SHA 저장소 run과 동일 |

가드된 accessor 검사도 정의가 있을 때는 여전히 반증한다. skip으로 퇴화하지 않았다.

### 4.7.4 새 측정 — W2 상수 승격은 **지금 하면 lap290 결함이 재발한다**

STATUS의 W2 블로커는 `runtime_driver.py`가 `0x8D`/`0x66B790`/`0x758`/`0x8990C8`을 매직
리터럴로 읽는 것을 수리 대상으로 남겨 뒀다. 그런데 lap280 probe의 line 129-130은 driver 원문을
`re.search(r"type=u\[0x…\]").group(1)`로 **가드 없이** 긁는다. 그 승격을 실제로 넣어 봤다.

| W2 승격 mutant | exit | stdout | 결과 |
|---|---|---|---|
| `type=u[0x8D]` → `type=u[G1_UNIT_TYPE_OFFSET]` | 1 | **0 B** | `AttributeError: 'NoneType' … 'group'` |
| `owner=u[0x8E]` → `owner=u[G1_UNIT_OWNER_OFFSET]` | 1 | **0 B** | `AttributeError: 'NoneType' … 'group'` |

`blind_spot_verdict = "unguarded"`. §4.6.3의 불변식은 `pinned`를 **인덱싱**하는 자리만 덮었고
`pinned`를 **만드는** 두 줄은 그대로 남았다. lap290이 진단한 결함 계열("상수가 옮겨지면 probe가
보고 대신 예외로 죽는다")은 따라서 아직 닫히지 않았다. 이것은 lap295 수리의 결함이 아니라
§4.6.4가 정한 범위 밖이며, 이번 검수가 새로 측정한 사실이다.

세 부류로 갈린다(측정·대조 근거 포함):

- **(a) 지금 승격해도 안전:** line 84 `0x8990C8`, line 89 `0x66B790`·`0x758`. 동일 값 상수가
  `tools/runtime_env.py`에 이미 있고(`G1_UNIT_EXISTS_BASE_ADDRESS`/`G1_UNIT_BASE_ADDRESS`/
  `G1_UNIT_STRIDE`), 저장소 probe 중 이 세 리터럴을 원문 정규식으로 긁는 것은 **0개**다.
- **(b) probe 가드가 선행돼야 함:** line 100 `0x8D`. `G1_UNIT_TYPE_OFFSET = 0x8D`는 이미
  있으나 위 표대로 probe가 먼저 죽는다.
- **(c) 승격이 아니라 새 증거가 필요함:** line 101 `0x8E`. `G1_UNIT_OWNER_OFFSET`은 존재하지
  않고, STATUS가 owner `+0x8E`를 "상속 가정 미재유도"로 기록했다. 이름만 붙이는 것은 미검증
  값을 승격된 상수로 격상시키는 것이므로 **금지**한다.

### 4.7.5 기록 주의 — lap294 probe의 `scope_verdict`는 이제 stale이다

수리 후 lap294 scope probe를 다시 돌리면 `scope_verdict`가 `"refs guard alone is sufficient"`로
**뒤집혀 보인다**. 이것은 새 사실이 아니라 앵커 소멸 artifact다: 그 probe는 수리 전 refs 루프
원문을 앵커로 찾아 `refs_guard_only` 사본을 만드는데, 앵커가 사라져 `patched == as_is`가 되고
두 열이 같아진다(같은 run이 `refs loop anchor not found exactly once` failure를 함께 낸다).
**§4.6.2의 "refs 가드만으로는 불충분" 판정은 유효하며 뒤집히지 않았다.** 그 probe의 exit1과
세 개의 `expected a 0-byte crash, got …` failure도 수리 성공을 뒤집어 적은 stale 기대값이다.

### 4.7.6 work tier 인계 사양 (§4.6.4 계열의 후속, 범위: 이 블록만)

1. 대상은 `…lap280_middle_s1_crossverify_probe.py` **line 129-130 두 줄**뿐이다. `type`/`owner`
   정규식이 실패하면 `.group(1)` 대신 `{name} literal missing from runtime_driver.py` 형태의
   명명 failure를 남기고 그 필드를 `pinned`에 넣지 않는다. 기존 failure 문구·값·스키마·창 상수·
   (1)(2)(4)절·comparator/producer/PASS 규칙은 건드리지 않는다.
2. 이미 있는 두 가드(line 156·167)와 lap293 튜플 가드는 그대로 보존한다.
3. **성공 조건(전부):** 정상 run exit0·`failures=[]`·보고서 SHA `3d4fe307…6a6d6a9126` 바이트
   동일. 동행 4종 불변. 기존 세 정의 삭제 mutant가 계속 명명 failure·비제로 stdout. 그리고
   §4.7.4 (b)의 `type=u[G1_UNIT_TYPE_OFFSET]` mutant가 `crash=null`·`stdout_bytes>0`·exit1.
4. **provenance:** lap292·lap294·lap296 세 review probe의 `EXPECTED_SHA`는 각 검수가 본 상태의
   기록이다. 편집 금지. 수리 후 세 probe가 내는 `target_probe sha mismatch` 한 줄씩은 예상된
   결과이며 새 SHA는 lap 기록에 적어 계보를 잇는다(§4.6.4 5항과 같은 규칙).
5. W2 (a)(b)(c) 중 **(a)만** 별도 카드로 열 수 있고, (b)는 위 1항 수리 뒤에, (c)는 `0x8E`의
   독립 재유도 증거가 생긴 뒤에만 연다. 셋을 한 바퀴에 묶지 않는다.
6. **금지:** §4.6.4 6항과 동일(게임/Wine/Xvfb/Stage B 실행, runtime 예산, 창 상수 변경,
   comparator/producer/PASS 규칙 변경, 원본·fixture 쓰기, 값 불일치 시의 정규식 땜질).

### 4.7.7 이 판정이 바꾸지 않은 것

**S1 카드 종결은 REJECT 유지.** 이번 검수는 static probe 하네스의 건전성만 다뤘다. S1 실제
결정성, 두 run의 값 동일성, Stage B, runtime 예산, WM_CLOSE, G3 저장 포맷 `0x1B5A4` 초과,
제품 G1~G4 증거는 전부 미해결이고 사용자 마일스톤 승인도 없다. §4.5.4 reader 이름 사각도
여전히 열려 있고 이번 범위 밖이다. 게임·Wine·Xvfb·PNG·원본·구현 모듈 쓰기 0
(`b56986e0…c9c08a8ac`/`dd2ad043…8500190`/`ae4ff939…4e4291b5` 불변). `make check` 292 passed,
`SAFETY_PASS`.
