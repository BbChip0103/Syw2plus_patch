# PlayerStruct 필드 오프셋 매핑

> 분석일: 2026-03-21
> 대상: 조선의반격 오리지날 실행.exe v1.100KR
> 이미지 베이스: 0x400000

## PlayerStruct 배열 레이아웃
- Player 1 base: 0x00956770
- Stride: 0x3ABC (15036 bytes)
- Max players: 8

## 확인된 필드 목록

| 오프셋 | 크기 | 필드명 | 값/설명 | 확인 주소 |
|--------|------|--------|---------|-----------|
| +0x0000 | 1B | nation | 0=없음, 1=조선, 2=일본, 3=명, 6=관전 | 0x00956770 |
| +0x0001 | 1B | player_num | 0-7 | 0x00956771 |
| +0x0002 | 1B | is_cpu | 0=사람, 1=컴퓨터 | 0x00956772 |
| +0x0003 | 1B | self_bit_mask | `1 << player_num` 자기 비트 | 0x00956773 |
| +0x0004 | 1B | opponent_mask | 다른 team 플레이어의 비트 OR | 0x00956774 |
| +0x0005 | 1B | team_num | team 번호 | 0x00956775 |
| +0x000A | 4B | unit_building_count | 유닛수+건물수 합산 | 0x0095677A |
| +0x0014 | 4B | rice | 쌀 자원 | 0x00956784 |
| +0x0018 | 4B | wood | 나무 자원 | 0x00956788 |
| +0x001C | 4B | supply_in_production | 생산 중인 전비 | 0x0095678C |
| +0x0D4A | 4B×N | owner_unit_id_list | 소유 유닛 id 배열 (`+0x200A`가 인덱스) | 0x009574BA |
| +0x200A | 2B | owner_unit_count | 소유 유닛 **개수** (배열 길이, 상한 0x4AF) | 0x0095877A |
| +0x200C | 2B | supply_produced | 생산된 전비 (유닛 타입별 비용 누적) | 0x0095877C |
| +0x200E | 2B | building_count | 건물 수 (유닛 플래그 `&2` 인 것의 개수) | 0x0095877E |
| +0x2010 | 2B | **owner_unit_cap** ⚠ | **유닛 개수 상한** (초기값 250). ~~supply_current~~ 아님 | 0x00958780 |
| +0x2012 | 2B | supply_limit | 전비 한도 (초기값 1500) | 0x00958782 |
| +0x395C | 2B | auto_magic_off | 자동마법해제 플래그 — **0이면 자동시전, ≠0이면 수동만**. (`DAT_00959AF0` per-player stride 0x1d5e SHORT) | `[바이너리 확인 2026-04-26]` |
| +0x395E | 2B | raw_DAT_00959AF2 | 원본 SHORT 필드. `FUN_004AE800` 큐 입력으로 set/clear되고 `FUN_0040EC70` idle event-route가 소비함. 사용자 UI 명칭은 미확정 | `[주소/입출력 확인, 의미 미확정]` |
| +0x3962 | 2B | observation_post | 관측소(전망탑) 보유 플래그 — `FUN_0041C450` AI 정찰 게이트 (`DAT_00959AF6`) | `[바이너리 확인 2026-04-26]` |

## ⚠ 2026-07-26 정정 — `+0x2010`은 전비가 아니라 **유닛 개수 상한**

이 표는 오래 `+0x2010`을 `supply_current(현재 전비, 250)`으로 적어 왔고, 그 라벨이
`plan_c/src/game/economy.h`(`kInitialSupplyCurrent`, `Economy::supply_current`,
JSON `player_supply_current`)까지 그대로 전파됐다.  **틀렸다.**

원본 두 함수가 이 블록의 의미를 확정한다:

```c
// FUN_0043EE30 — 소유자 로스터에 유닛 push
if (0x4af < *(short*)(p1+0x200a)) { /* overflow */ }
*(int*)(p1 + 0xd4a + *(short*)(p1+0x200a)*4) = unit_id;      // +0xd4a 배열, +0x200a 가 인덱스
*(short*)(p1+0x200a) += 1;                                    // 개수 +1
*(short*)(p1+0x200c) += DAT_009b5238[unit_type];              // 타입별 비용 누적
if (unit_flags & 2) *(short*)(p1+0x200e) += 1;                // 건물 계열 수

// FUN_0043EDA0 — 스폰 직전 용량 게이트
if (param3==1) { if (*(short*)(p1+0x2010)     <= *(short*)(p1+0x200a)) return 0; }
else           { if (*(short*)(p1+0x2010) - 8 <= *(short*)(p1+0x200a)) return 0; }
if (cost && *(short*)(p1+0x2012) < *(short*)(p1+0x200c) + cost) return 0;
```

`+0x2010`은 **개수(`+0x200a`)와 비교**되고, `+0x2012`가 **전비(`+0x200c`)와 비교**된다.
디컴파일 전체에서 `+0x2010`이 등장하는 곳은 세 군데뿐이고 전부 개수와의 비교다
(`<= +0x200a`, `-8 <= +0x200a`, `/5 <= +0x200e`) — 감소/소비되는 자리가 하나도 없다.
flag8이 아닌 타입은 상한에서 **8칸을 예약**한다.

### 구조체 동일성 확인

`+0xd4a`/`+0x200a`는 race-AI owner unit list 로도 불려서 다른 구조체일 가능성을 먼저
배제했다.  `FUN_0043EDA0`은 `__thiscall`이라 호출부에 `this`가 안 보이므로 디스어셈블을 읽으면:

```asm
movsx ecx, BYTE PTR [esi+0x8e]   ; owner
... 3*o<<4-o = 47o ; (47o*5)<<4-o = 3759o ...
lea   ecx, [edx*4+0x956770]      ; 15036*owner + 0x956770  →  stride 0x3ABC
```

`15036 = 0x3ABC`이므로 이 표의 PlayerStruct가 맞다(`DAT_00956772` = `+0x02` is_cpu 와도 일치).

### 남은 조치

값은 원본과 같고 **이름만** 틀렸다.  `supply_current` 이름은 33곳에서 참조되고
save/load 필드명까지 걸려 있어 이번엔 개명하지 않았다 — 개명은 별도 lane.
잠금: `plan_c/tests/test_player_struct_field_labels_0726.py`
(값이 아니라 **라벨 근거**를 검사한다).
상세: `analysis/memory_maps/player_struct_2010_is_unit_cap_not_supply_0726.md`

## 미확인 범위
- +0x0020 ~ +0x0D49 / +0x0D4A 이후 ~ +0x2009: 대부분 미확인
  (`+0x0D4A` 유닛 id 배열이 이 구간을 크게 차지한다)
- +0x2014 ~ +0x395B: ~6.5KB 미확인 (연구 상태 비트, 생산 제어 필드 예상)

## 관련 로직 주소
- 건물별 생산 kind 테이블: 0x4EC970 (조선 본영 시작)
- 건설 로직: 0x4EDC18 근방
- AI 건설 속성: 0x49E04F

## Unit→Player 링크

UnitStruct의 `owner` 필드(+0x8E, 1B)를 기반으로 PlayerStruct 포인터를 계산하는 공식.

**계산 공식:**
```
player_ptr = 0x00956770 + owner * 0x3ABC
```

**예시:**
| owner | player_ptr |
|-------|-----------|
| 0 | `0x00956770` |
| 1 | `0x00959F2C` |
| 2 | `0x0095DBE8` |
| 7 | `0x009824D6` |

**근거:**

| 근거 | 확인 주소 | 태그 |
|------|-----------|------|
| PlayerStruct 배열 base = `0x00956770` — player_offsets.md 기반 | `0x00956770` | `[주소확인]` |
| stride = `0x3ABC` — player_offsets.md PlayerStruct 배열 레이아웃 | `0x00956770`+`0x3ABC` | `[주소확인]` |
| owner 필드로 PlayerStruct 인덱싱 — `unit+0x8E` xref | `0x00406B06` | `[행동확인]` |

> ⚠️ 공식(`owner * 0x3ABC` 배율)은 정적 분석 기반 추정 `[의미추정]` — x64dbg에서 `0x00406B06` BP 후 계산 확인 필요

**관련:** EVID-0004 (`unit+0x8E owner`), EVID-0005 (PlayerStruct base/stride)

---

## 장수 제한 관련
- 기본 전비 제한: 1500 (supply_limit 초기값)
- 장수 1명 생산 시 전비 제한 +200
- 전비 제한 최대값: 2500
- 기본 장수 상한: 5명
- 장수 수 확장 (ESL): 7명 가능
- 장수 제한 관련 4곳 주소: 추후 Ghidra 정밀 분석 필요 `[의미추정]`

## 글로벌 변수 추가 확정 (2026-04-26)

> 출처: docs/background/variables_list.md — variables_list 확정 (2026-04-26)

| 분류 | 변수명 | 주소 | 크기 | 설명 |
|------|--------|------|------|------|
| 글로벌 | game_mode | 0x00975914 | 4byte | 0=보통, 1=깃발뺏기, 2=시간제한, 3=일기토 |
| 글로벌 | ingame_mode | 0x009E1DD8 | 1byte | 시나리오 번호 (1~24), 임의게임=0 |
| 글로벌 | starting_pt_x | 0x00B3DE58 | 4byte array | 플레이어별 스타팅 포인트 x, stride=0x338 |
| 글로벌 | starting_pt_y | 0x00B3DE5C | 4byte array | 플레이어별 스타팅 포인트 y, stride=0x338 |

## 프로그램 상태(PS) 전체 값 (2026-04-26)

> PS 주소: 0x004ED818 (WORD)
> 출처: docs/background/from_3_doc/variables_01_program_flow_globals.md (2026-04-26),
> lap17 원본 정적 재검증(2026-09-11). 기존 4byte 표기는 아래 직접 명령 근거로 정정했다.

| PS 값 | 설명 |
|-------|------|
| 1 | 시나리오 인게임 전처리 |
| 2 | 시나리오 외 인게임 전처리 |
| 3 | 인게임 |
| 4 | 로비 전처리 |
| 5 | 로비 |
| 6 | 임의게임 전처리 |
| 7 | 임의게임 |
| 8 | 게임 타이틀 전처리 |
| 9 | 게임 타이틀 |
| 12 | 여럿이하기 전처리 |
| 13 | 여럿이하기 |
| 14 | 시나리오 선택 전처리 |
| 15 | 시나리오 선택 |
| 16 | 시나리오 브리핑 전처리 |
| 20 | 시나리오 브리핑 |
| 24 | 승리했습니다 전처리 |
| 25 | 승리했습니다 |
| 26 | 패배했습니다 전처리 |
| 27 | 패배했습니다 |
| 28 | 전투결과 리포트 전처리 |
| 29 | 전투결과 리포트 |
| 35 | 불러오기 |
| 314 | HQNET 전처리 |
| 315 | HQNET |

---

## 이슈 #79 추가 오프셋 (2026-03-29)

> ⚠️ **주의**: 아래 오프셋(+0x5E4, +0x5E6, +0x5E8)은 **PlayerStruct가 아닌 UnitStruct 소속**이다.
> PlayerStruct stride는 0x3ABC이므로 +0x5E4는 PlayerStruct 범위를 초과한다.
> player.c의 `japan_cart_transform()` 함수가 `UnitStruct *u` 포인터로 접근하는 필드임.
> 별도 `unit_offsets.md` 문서 생성 전 임시 기록 — 이슈 #87에서 정리 예정.

| 오프셋 | 크기 | 필드명 | 근거 | 증거 |
|--------|------|--------|------|------|
| +0x5E4 | 4B | build_progress (애니메이션 슬롯 0x11) | FUN_0040e900 case 0x11: *(param+0x5E4)=iVar3 | [정적분석 확인] |
| +0x5E8 | 4B | (애니메이션 슬롯 0x12) | FUN_0040b2c0 default, FUN_0040e900 case 0x12 | [정적분석 확인] |
| +0x5E6 | ? | is_building_complete (player.c 주장) | Ghidra 미발견 — +0x5E4와 +0x5E8 사이, short packed 가능성 | [미확인] |

---

## PlayerStruct 설정 필드 컨슈머 (2026-04-26 추가)

### `auto_magic_off` @ PlayerStruct +0x395C / `&DAT_00959AF0`

> **확정 폭: SHORT/WORD** (분석 합의: 단 한 곳도 DWORD 접근 없음 — 모두 short index)
>
> 시맨틱: **0이면 자동마법 시전 ON, 1이면 OFF**
>
> 컨슈머:
> - `analysis/ghidra_output/FUN_004755D0.c` — AI/유닛 자동시전 dispatcher (uVar3 = 1..0xF case 마다 `(&DAT_00959AF0)[owner * 0x1D5E] != 0` 게이트). 0이면 자동시전 비활성화.
> - `analysis/ghidra_output/FUN_0049B210.c` — UI 자동마법 토글 표시 갱신 (`uVar1 = (DAT_00959AF0 == 0 ? 0x21 : 0x22)`).

### raw `DAT_00959AF2` @ PlayerStruct +0x395E

> **확정 폭: SHORT/WORD** (분석 합의: `local_68 = &DAT_00959AF2` 가 short* 페어로 사용됨)

세 층을 혼합하지 않는다.

- 원본 주소/ID: `DAT_00959AF2`, PlayerStruct `+0x395E`, SHORT.
- 현재 확인된 동작: timer queue case `0x44/0x45`가 set/clear하고
  `FUN_0040EC70`의 idle event-route 분기가 읽는다.
- 사용자 UI 명칭: 미확정. 과거 `hero_priority_train`/`장수우선훈련` 표기는 가설이며
  runtime UI 입력→행동 변화가 증명되기 전까지 확정명으로 쓰지 않는다.
>
> 컨슈머:
> - `analysis/ghidra_output/FUN_004AE800.c` — 매 틱 production-queue 디스패처. `puVar9[3] + local_5c == DAT_008924B8` (예약시각 도달) 시 큐 항목 처리. 큐 슬롯 명령(case 0x42/0x43): `puVar12[-1] = 1/0` → `&DAT_00959AF0` 필드 set/clear. case 0x44/0x45: `*puVar12 = 1/0` → `&DAT_00959AF2` 필드 set/clear.
> - `analysis/ghidra_output/FUN_0040EC70.c` — 유닛 AI 메인 ((`(&DAT_00959AF2)[owner * 0x1D5E] != 1`) 분기로 행동 변경)

### `observation_post` @ PlayerStruct +0x3962 / `&DAT_00959AF6`

> **확정 폭: SHORT/WORD**
>
> 시맨틱: 1=관측소 보유, 그 외=미보유
>
> 컨슈머:
> - `analysis/ghidra_output/FUN_0041C450.c` — AI 정찰/시계 게이트. `*(short *)(&DAT_00959AF6 + DAT_00B63FC4 * 0x3ABC) != 1` 일 때 0 반환 (정찰 권한 없음).

### PS @ 0x004ED818 폭 재확인

- 기존 결론(WORD)와 모순되는 직접 DWORD 접근 디컴파일 미발견.
- 최신 PS 값 표(0~315) 중 `314/315` (HQNET)는 9-bit 이상이므로 WORD/DWORD 둘 다 가능. 강근거는 없음.
- 액션: 기존 WORD 결론 유지, 별도 검증 필요시 BP @ 분기 호출 사이트 (예: PS=29, PS=314 처리)에서 확인.

### 출처

- `analysis/ghidra_output/FUN_0049B210.c` — `&DAT_00959AF0` short 토글 UI
- `analysis/ghidra_output/FUN_004AE800.c` — `&DAT_00959AF2` short 페어 큐 처리
- `analysis/ghidra_output/FUN_0040EC70.c` — `&DAT_00959AF2` short 분기
- `analysis/ghidra_output/FUN_004755D0.c` — `&DAT_00959AF0` AI 자동마법 게이트
- `analysis/ghidra_output/FUN_0041C450.c` — `&DAT_00959AF6` short 정찰 게이트

---

## 프로그램 글로벌 변수 (from_3_doc/variables_01 반영 — 2026-04-26)

> 이 섹션은 PlayerStruct 소속이 아닌 전역 런타임 변수다.
> 출처: `docs/background/from_3_doc/variables_01_program_flow_globals.md`

### 프로그램 상태

| 역할 | 유형 | 주소 | 비고 |
|------|------|------|------|
| 프로그램 상태 (PS) | WORD | `0x004ED818` | 1=시나리오전처리 / 2=시나리오외인게임전처리 / 3=인게임 / 4=로비전처리 / 5=로비 / 6=임의게임전처리 / 7=임의게임 / 8=타이틀전처리 / 9=타이틀 / 12=여럿이하기전처리 / 13=여럿이하기 / 14~15=시나리오선택 / 16~20=브리핑 / 24~29=결과 / 35=불러오기 / 314~315=HQNET |
| 직전 프로그램 상태 (추정) | byte | `0x00B92CC0` | [추정] |
| 버전 문자열 | string | `0x004ED7F8` | ex) "V 1.100KR" |
| 조반 창 활성 상태 | 4byte | `0x0066976C` | 0=비활성 / 1=활성 |
| 설정 버튼 클릭 여부 | 4byte | `0x00B93984` | 0=기본 / 1=클릭 |
| 인게임 모드 (시나리오번호?) | byte | `0x009E1DD8` | 시나리오1=1 ~ 시나리오24=24 [추정] |
| 혼자/여럿이하기 관련 상태 | WORD | `0x004ED848` | 폭은 확인됨. `혼자=1/여럿=0` 및 PS7 버튼 클릭과의 직접 대응은 lap27에서 **미입증**으로 정정 |

#### lap17 원본 정적 재검증 — PS4→PS5와 필드 폭

- 입력: SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  PE32의 격리 복사본. 명령은 `objdump -d -Mintel --start-address=0x424b50
  --stop-address=0x424c10 <copy>` 및 전체 disassembly의 `4ed818|4ed848` 참조 검색이다.
- `0x424b50`의 로비 전처리 handler는 호출 뒤 `0x424b55`에서
  `66 c7 05 18 d8 4e 00 05 00` (`WORD [0x004ED818] = 5`)를 실행한다.
  `0x424b60`부터의 다음 handler는 PS5 로비 입력을 처리한다. 따라서 PS4 뒤 안정 PS5는
  정상 로비 endpoint이며 PS7 복귀를 요구할 근거가 아니다.
- `0x004ED848`의 원본 read/write는 `66` operand-size prefix를 사용한다. 예를 들어
  `0x4b9390`의 `66 c7 05 48 d8 4e 00 01 00`은 WORD 1을 기록한다. 런타임 reader도
  2byte로 맞춰야 하며, 4byte로 우연히 1을 읽은 관측은 정확한 필드 폭 증거가 아니다.

#### lap27 selector 의미 재검토 — 폭과 UI 의미를 분리

- 입력은 동일 SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  격리 복사본이다. 전체 `objdump -d -Mintel`의 `0x004ED848` literal 참조를 다시 열거했다.
- 직접 write는 `0x4219e8`, `0x43977a`, `0x4397c9`, `0x4b9341`의 WORD 0과
  `0x4b9390`의 WORD 1이다. `0x440c89`/`0x441059`는 2byte 크기와 함께 주소를 함수에
  넘긴다. 이들은 필드 폭은 지지하지만, 두 PS7 버튼 hit-test/callback과 각 write 사이의
  호출 관계는 현재 근거에 없다.
- lap26 보존 run은 content `(344,169)` 클릭 뒤 90초 전체 제한까지 `PS=7`, WORD=1만
  남겼다. selector 클릭은 wait 성공 뒤에만 `inputs.jsonl`에 기록되므로 클릭 직후 화면,
  helper 반환값, WORD 시계열이 모두 없다. 따라서 입력 전달 실패, 필드 의미 오류, 원본 UI
  동작을 이 run만으로 구분할 수 없다.
- **판정:** WORD 폭은 CONFIRMED, `혼자=1/여럿=0` 및 `1→0→1` UI gate는 UNKNOWN/REVISE다.
  다음 work probe가 두 보이는 버튼의 생성·hit-test·callback에서 실제 상태 write까지 정확한
  주소/바이트/호출 경로를 찾거나, 찾지 못한 경계를 기록하기 전 이 필드를 selector PASS로 쓰지 않는다.

#### lap28 PS7 버튼 정적 provenance — 생성부터 selector write까지

- 입력 원본은 SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`인 PE32
  격리 복사본이다. 새 실행·하네스 수정·바이너리 패치는 하지 않았다.
- PS dispatcher `0x00424A9F`는 `call 0x004B8A10` 뒤 `WORD [0x004ED818]=7`을 기록하고,
  `0x004B8A10`에서 두 PS7 control object를 만든다. 첫 생성 call의 old bytes는
  `0x004B8C16..0x004B8C3A`:
  `6a 01 6a 01 52 68 98 00 00 00 68 26 01 00 00 50 51 68 98 00 00 00 68 26 01 00
  b9 00 a6 06 01 e8 95 c2 f4 ff`이며, object `0x0106A600`을 `0x00404ED0`으로 구성한다.
  두 번째 old bytes는 `0x004B8C3B..0x004B8C70`:
  `8b 15 44 af b3 00 a1 c0 1f 07 01 8b 0d bc 1f 07 01 6a 01 6a 01 52 68 98 00 00 00
  68 9c 01 00 00 50 51 68 98 00 00 00 68 9c 01 00 00 b9 c8 a7 06 01 e8 5f c2 f4 ff`이며,
  object `0x0106A7C8`을 같은 constructor로 구성한다. 각 call의 `0x98`/`0x126`,
  `0x98`/`0x19C` literal과 별도 sprite/resource load(`0x004B8B0E`,
  `"yfnt\\SetMultiButton_Plus.spr"`)는 두 보이는 control의 생성 경계다. label 문자열 자체는
  이 바이너리 정적 자료에서 확인되지 않아 첫/둘째 object를 각각 `여럿이하기`/`혼자하기`로
  이름 붙이는 것은 아직 inference다.
- constructor `0x00404ED0`은 object field를 초기화하고 `66 89 86 a0 00 00 00`으로
  2-byte parameter를 저장한 뒤 `c7 86 a4 00 00 00 00 00 00 00`으로
  control state `[object+0xA4]=0`을 만든다. PS7 event loop `0x004B8D60`은
  `0x004B8E73`에서 `call 0x004B91E0`으로 poll/callback을 호출한다.
- `0x004B91E0`의 두 object poll은 `0x00405560`을 호출하고, 이 함수의 old bytes
  `8b 44 24 04 56 50 e8 b5 f6 ff ff`는 `0x00404C20`을 거친다. `0x00404C20`은
  `ff 50 54`로 object vtable `+0x54`를 호출하므로, hit-test/input callback의 실제
  전달 경계는 정적으로 확인된다. callback이 반환한 object state는
  `0x00405540`의 `8b 44 24 04 89 81 a4 00 00 00 c2 04 00`으로 `[object+0xA4]`에 쓰이고,
  `0x00405550`의 `8b 81 a4 00 00 00 c3`으로 읽힌다.
- callback 후 `0x004B9253`은 첫 object state를 읽어 `edi=1`, 두 번째 object state가
  active이면 `edi=0`으로 정규화한다. `0x004B92C8`의 old bytes `66 83 ff 01` 분기 뒤
  actual global write는 두 경로로 고정된다: 첫 경로 `0x004B9341` old bytes
  `66 89 1d 48 d8 4e 00` (`WORD [0x004ED848]=bx`, 여기서 `xor ebx,ebx`는
  `0x004B91F1`)와 둘째 경로 `0x004B9390` old bytes
  `66 c7 05 48 d8 4e 00 01 00` (`WORD [0x004ED848]=1`)이다. 따라서
  `0x004ED848`은 PS7 callback-derived selection branch/write와 실제로 연결되며 폭은 WORD다.
- **경계:** 위 chain은 두 PS7 control object와 `0x004ED848` write/branch를 증명하지만,
  `0x0106A600`/`0x0106A7C8` 중 어느 것이 한국어 `여럿이하기`/`혼자하기`인지는 sprite 내부
  시각 자료 또는 새 원본 UI 관측 없이는 정적으로 확정하지 않는다. 따라서 `혼자=1/여럿=0`
  label 의미와 lap26의 click gate는 UNKNOWN/REVISE로 유지하며 selector PASS로 승격하지 않는다.
- **다음 검수:** 새 Sol/high가 위 original SHA, addresses, old bytes, vtable edge, label 의미
  경계를 독립 대조한다. 그 전까지 게임 재실행·harness/game 변경·새 `g1-baseline`은 금지한다.

#### lap29 Sol 독립 확인 — selector state와 확정 mode write의 시간 경계

- 동일 원본과 lap26 private copy를 다시 해시해 둘 다 SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`임을 확인했다.
  lap28의 object 생성 두 범위, `0x00405560` → `0x00404C20` vtable `+0x54`,
  `[object+0xA4]` reader/writer, `0x004B9341`/`0x004B9390` WORD write의 raw bytes도
  file offset에서 독립 재추출해 일치했다. 정확히는 dispatcher entry `0x00424A9F`는 NOP이고
  `0x004B8A10` call은 `0x00424AA0`에서 시작한다.
- 두 selector constructor anchor는 첫 object `0x0106A600`이 `(0x126,0x98)` = `(294,152)`,
  둘째 `0x0106A7C8`이 `(0x19C,0x98)` = `(412,152)`다. lap26의 보존된 800×600 PNG
  `7f50c8b3203a3c9ca9053828566e931ef59e634f283afc876e4ccb9bd9b915ea`에서는 해당 위치가
  각각 왼쪽 `여럿이하기`, 오른쪽 `혼자하기`에 정렬된다. 이는 **과거 캡처와 정적 좌표를 합친
  위치 대응**이지, PE 문자열/SPR 자체만으로 label을 해독한 새 정적 증거 또는 새 runtime 성공은 아니다.
- `0x004B9249` 이후 첫 object state=1이면 `edi=1`, 둘째 state=1이면 `edi=0`이 된다.
  그러나 `0x004B92C8` 분기 뒤 각 global write 직전에는 별도 object `0x01071F18`을
  `0x00404C20`으로 검사하는 gate가 `0x004B9309`와 `0x004B9363`에 있다. 이 object는
  `0x004B8BC5`에서 `(0x22D,0x222)` = `(557,546)` anchor로 생성되어 보존 화면/카드의
  연결 `확인` control `(608,564)`과 정렬된다. 따라서 `0x004ED848`은 selector click 자체의
  즉시 state가 아니라 **선택을 확인할 때 commit되는 mode WORD**다.
- **판정:** lap28의 callback-derived branch/write provenance는 CONFIRMED하되 시간 의미를
  위와 같이 좁힌다. 과거 PNG를 결합하면 `여럿이하기→확인`은 WORD 0,
  `혼자하기→확인`은 WORD 1이라는 위치/분기 대응을 지지하지만, PS7에서 selector만 누른 뒤
  WORD `1→0→1`을 요구하는 lap18~26 harness gate는 원본 제어흐름과 충돌하므로
  **HARNESS CONTRACT REVISE**다. 새 실행 전 work tier가 `[0x0106A600+0xA4]`와
  `[0x0106A7C8+0xA4]`의 one-hot selector state를 직접 관측하고, `0x004ED848`은
  `확인` 뒤 committed mode로만 검사하도록 수리해야 한다.

#### lap33 Sol 독립 진단 — solo PS5의 자동 ready 경계

- 입력은 `V 1.100KR`, SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`인 lap32 private
  copy다. source 원본과 copy SHA가 일치한다. `.text` VMA와 file offset은 모두 `0x1000`에서
  시작하므로 아래 virtual address의 raw bytes를 같은 file offset에서 독립 추출했다.
- `0x004B7160..0x004B717E` old bytes
  `b8 01 00 00 00 66 39 05 48 d8 4e 00 74 10 b9 08 2c 63 00 e8 d8 2a f8 ff
  48 f7 d8 1b c0 40 c3`는 `WORD [0x004ED848] == 1`이면 즉시 1을 반환한다.
- `0x004B7C0D..0x004B7C50`에서 위 함수를 호출한 뒤 `0x004B7C14: 75 52`가 참이면
  `0x004B7C68`로 점프한다. 따라서 committed solo mode=1에서는 `0x01069BB8 +
  player*0xA0` ready control의 `0x00404C20` poll과 `DWORD [0x00632CF0 + local*4]`
  toggle을 수행하는 수동 경로를 건너뛴다. 분기부터 수동 toggle까지 old bytes는
  `e8 4e f5 ff ff 85 c0 75 52 33 ff be b8 9b 06 01 57 e8 5d f5 ff ff 83 c4 04
  85 c0 74 2d a1 b4 69 06 01 8b ce 50 e8 e9 cf f4 ff 85 c0 74 1c a1 c4 3f b6
  00 33 c9 89 6c 24 10 39 1c 85 f0 2c 63 00 0f 94 c1 89 0c 85 f0 2c 63 00`이다.
- `0x004B7C68..0x004B7CA5` old bytes
  `bf f0 2c 63 00 be c2 2c 63 00 8a 46 fe 84 c0 74 16 80 3e 01 74 0d 53 e8 fc
  f4 ff ff 83 c4 04 3b c5 75 0a 89 2f eb 06 c7 07 00 00 00 00 83 c6 06 43 83
  c7 04 81 fe f2 2c 63 00 7c ce 33 db`는 slot별 ready DWORD 배열
  `0x00632CF0 + player*4`을 산출한다. `0x004B7180..0x004B7194` old bytes
  `0f bf 44 24 04 8b 15 c4 3f b6 00 33 c9 3b d0 0f 94 c1 8b c1 c3`는 인자 player와
  local index DWORD `0x00B63FC4`를 비교하므로, 활성 local slot은 ready=1로 자동 설정된다.
- **판정:** lap32의 `(134,79)`은 constructor anchor `(112,66)`의 첫 ready control 안이지만,
  solo PS5에서는 원본이 이 control의 수동 poll을 의도적으로 우회한다. 동일한 전체/crop SHA는
  이 분기와 일치한다. lap32는 입력 미전달을 입증하지 않으며, manual click+visual-change를 요구한
  하네스 계약이 틀렸다. 다음 work는 local index를 `0..7`로 fail-closed 검증하고 해당 ready DWORD를
  4byte로 읽어 `committed_mode=1`, `PS=5`, `ready=1`을 setup gate로 기록해야 한다. 원본 바이너리
  패치나 old→new bytes는 필요 없고, source SHA가 다르면 수리를 거부한다.

### 카메라 / 뷰포트

| 역할 | 유형 | 주소 | 비고 |
|------|------|------|------|
| 카메라 좌표 x | 4byte | `0x00B42D7C` | |
| 카메라 좌표 y | 4byte | `0x00B42D80` | |
| 플레이어 권한 | 4byte | `0x00B63FC4` | |

### 선택/명령 상태

| 역할 | 유형 | 주소 | 비고 |
|------|------|------|------|
| 선택한 유닛 수 | 4byte | `0x00899024` | |
| 선택한 유닛 스택 | 4byte array | `0x00899028` | 4byte씩 unit_id |
| 명령 위치 맵 좌표 x | byte | `0x00898FAC` | |
| 명령 위치 맵 좌표 y | byte | `0x00898FB0` | |
| 명령 타겟 | 4byte | `0x00898FB4` | 공격/탑승 대상 unit_id |

### 인게임 환경

| 역할 | 유형 | 주소 | 비고 |
|------|------|------|------|
| 게임방식 | 4byte | `0x00975914` | 0=보통 / 1=깃발뺏기 / 2=시간제한 / 3=일기토 |
| 게임속도 | 2byte | `0x006695A4` | |
| 바람 방향 | 4byte | `0x00973F5C` | 남서=1 / 서북=4 / 서=5 / 동북=16 / 북=20 / 남동=64 / 남=65 / 남서복합=80 |
| 인게임 플레이 시간 (초) | 4byte | `0x0097591C` | |
| 플레이 시간 출력 문자열 | string | `0x00B65084` | "%s:%s:%s" 형태, 마우스오버 시 갱신 |
| 일기토 아이템 드랍 | 4byte | `0x00975988` | |
| 일기토 전용 시야 | 4byte | `0x00975B30` | 0/1 |

### 스타팅 포인트 배열

| 역할 | 유형 | 주소 | 비고 |
|------|------|------|------|
| 스타팅 포인트 x | 4byte array | `0x00B3DE58` | stride=0x338, 플레이어별 |
| 스타팅 포인트 y | 4byte array | `0x00B3DE5C` | stride=0x338, 플레이어별 |

### 병기창고 / 아이템

| 역할 | 유형 | 주소 | 비고 |
|------|------|------|------|
| 병기창고 창 on/off | 4byte | `0x0061DA10` | 0/1 |
| 병기창고 아이템 인덱스 | 4byte | `0x0061DA14` | |
| 장수 인벤 조회 시 아이템 인덱스 | 4byte | `0x0061DA18` | |
| 병기창고 아이템 종류 카운트 | 4byte | `0x0061DA28` | |

### 전투결과 리포트 구조체

- **베이스 주소**: `0x00892418`
- **stride**: 0x14 (플레이어별)
- **필드 구성** (순서대로): 병력훈련 2B / 건설 2B / 병력손실 2B / 병력처치 2B / 건물손실 2B / 건물처치 2B / 나무 4B / 곡물 4B

#### lap39 Luna 정적 PS3 command-cell provenance — hit-test/callback은 확정, worker 의미는 미확정

- 기준 원본 `Syw2plus/syw2plus_original.exe` SHA256는
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다. 원본은 읽기 전용으로
  두었고 EXE/DLL/게임 데이터/하네스는 변경하지 않았다. `.text`는 VA `0x00401000`/raw
  `0x1000`이므로 아래 `.text` 주소의 raw offset은 `VA-0x00400000`이다.
- **command-panel 생성:** `0x0049B6D0` (raw `0x9B6D0`, old entry bytes
  `53 55 56 8b 74 24 10 57 56 b9 6c e3 61 00 e8 bd 3e f7 ff`)가 선택 unit을
  `0x0040F5A0`으로 해석한 뒤 type stride `0x758`의 런타임 테이블
  `0x0066BE88 + type*0x758`에서 네 pointer/command record를 읽는다. type58이면
  런타임 주소는 `0x00686878,+0x4,+0x8,+0xC`이나 이 영역은 원본 PE file-backed section이
  아니므로 원본 raw bytes로 값(활성 flag/아이콘)을 확정할 수 없다.
- **cell 배치:** 같은 함수가 `0x0041FAF0`로 pool group `2,3,4,5`를 각각 예약하고,
  `0x0041F630` (raw `0x1F630`, old entry bytes
  `8b 44 24 04 8b 54 24 0c 53 8b 5c 24 38 56 57 8b 7c 24 1c 8b f1`)로
  `0x00B38A38 + slot*0x124` object를 만든다. 네 cell의 x는 각각
  `baseX`, `baseX+Δ`, `baseX+2Δ`, `baseX+3Δ`이고
  `baseX=[0x009E2BAC]`, `Δ=[0x009E2BB4]+[0x009E2BB8]`, y는
  `baseY=[0x009E2BB0]`이다. 폭/높이는 index `0x36`을 `0x00419D40`/`0x00419D60`이
  런타임 table `0x0051EE94/0x0051EE98`에서 읽는다. 이 네 global/table은 원본 file-backed
  section 밖이므로 `(670,490)`이 어느 column의 내부인지 정적 raw bytes만으로 계산할 수 없다.
- **hit-test:** `0x0041FA60` (raw `0x1FA60`, old bytes
  `83 39 00 74 36 0f bf 05 14 d8 4e 00 8b 51 08 3b d0 7d 28 ...`)는 active object의
  `[object+0x08,+0x0C,+0x10,+0x14]` 사각형과 file-backed input WORD
  `[0x004ED814]`/`[0x004ED816]`를 비교한다. 따라서 좌표 입력의 hit-test 함수와 field는
  확정되지만, lap36의 `(670,490)`은 이 사각형에 들어갔다는 runtime after 증거가 없다.
- **cell fields/callback boundary:** `0x0041F630`은 object의 active/group을 `+0x00/+0x04`,
  사각형을 `+0x08/+0x0C/+0x10/+0x14`, category/flag를 `+0x4C/+0x50`, callback을
  `+0x54/+0x58`에 저장한다. `0x0041FBC0` (raw `0x1FBC0`, old entry bytes
  `51 53 55 56 bd 01 00 00 00 57 ...`)가 `0x0041FA60` hit 후 `object+0x58`
  `0x0049B640`을 호출하고, 별도 click/action 경계에서 `object+0x54` `0x0049B530`을
  호출한다. 두 callback 의미를 하나로 합치지 않는다.
- **action mapping:** `0x0049B530` (raw `0x9B530`, old bytes
  `56 8b 74 24 08 57 56 e8 04 ba f7 ff ...`)는 flag별로
  `0x40000→action 0x19A`, `0x200→0x19C`, `0x80000→0x19E`,
  `0x100000→0x1A1`을 선택하고, 현재 player `0x00B63FC4`와 record pointer를
  `0x004AE550`에 전달한다. `0x004AE550` (raw `0xAE550`, old entry bytes
  `81 ec 94 00 00 00 8d 44 24 44 b9 14 00 00 00 ...`)는 두 번째 인자로 action WORD를
  받아 selected roster `0x00899028`를 포함한 command record를 구성한다. hit callback인
  `0x0049B640` (raw `0x9B640`, old entry bytes `56 8b 74 24 08 56 e8 85 b9 f7 ff ...`)는
  동일 flag의 type record pointer를 골라 `0x00421550`으로 전달한다.
- **worker 판정 경계:** 위 chain은 `(670,490)`이 네 command-cell 후보 중 어느 실제
  사각형을 눌렀는지, 그리고 해당 cell이 action `0x19A/0x19C/0x19E/0x1A1` 중 무엇인지까지
  정적으로 결정하는 근거다. 그러나 type58 record 값과 `baseX/baseY/Δ/size`는 runtime
  memory이며 action id의 worker/비-worker 의미를 PE의 고정 문자열·raw table만으로
  확정할 수 없다. 따라서 **worker 생산 cell은 UNKNOWN**, `(670,490)`의 실제 동작도
  **UNKNOWN**으로 유지한다. 아이콘 모양이나 lap36 PNG만으로 승격하지 않는다.
- **다음 검수:** 새 Sol/high가 동일 SHA와 위 raw bytes/field mapping을 독립 재추출하고,
  runtime read가 허용될 때만 type58 table 값·좌표 global·실제 click after-state를 별도
  fixture로 확인한다. 그 전에는 좌표 수정, 새 게임 실행, 하네스/EXE 변경을 금지한다.

#### lap47 Sol 독립 진단 — pool 경계 확정, live snapshot 계약 반려

- 고정 원본 SHA는 위와 같다. allocator `0x0041FAC0` (raw `0x1FAC0`, old bytes
  `b8 01 00 00 00 b9 5c 8b b3 00 83 39 00 74 11 81 c1 24 01 00 00 40 81 f9 70 ac b3 00 7c ec`)
  은 첫 object `0x00B38B5C`부터 `0x124`씩 증가하고 `<0x00B3AC70`에서만 검사한다. 따라서
  유효 allocator slot은 정확히 `1..29`이며 object 식 `0x00B38A38 + slot*0x124`는 맞다.
  lap42 helper의 slot1..30 범위는 마지막 비allocator slot 하나를 더 읽지만, slot1..29도 모두
  포함하므로 이 경계 오류만으로 lap46의 빈 결과를 설명할 수 없다.
- frame UI 경로 `0x0041E60C`는 `0x00498F50`을 호출한다. `0x00498F50` (raw `0x98F50`,
  old bytes `81 ec 98 01 00 00 53 55 56 33 db 57 89 5c 24 20 e8 7b ff ff ff e8 56 6b f8 ff`)
  은 먼저 `0x00498EE0`을 호출하고, 그 함수는 `0x0041FB60`을 호출해 모든 active pool object를
  초기화한 뒤 현재 선택에 맞는 command cells를 다시 만든다. lap46 helper는 slot마다 별도
  `process_vm_readv`를 호출하므로 이 reset/rebuild 수명주기와 일관된 단일 snapshot 계약이 없다.
- lap46 `selection_after` PNG에는 선택 HQ와 command panel이 보이지만 helper는 filter 전 raw
  active/group/callback을 저장하지 않았다. 따라서 **주소·stride·생성 field는 CONFIRMED**,
  **helper의 live snapshot/실패 진단 계약은 REVISE**다. 실제 빈 결과가 reset window였는지 특정
  predicate mismatch였는지는 보존 증거만으로 UNKNOWN이며, 시각 결과로 memory PASS를 만들지 않는다.

#### lap51 Sol 독립 진단 — group10 분리 및 group2..5 생성 predicate

- 고정 원본 SHA는 위와 같다. `0x00498F65`는 allocator 호출 뒤 새 object를 `0x0041F700`에
  group `10`, click `0x00498ED0`, hit `0`으로 넘긴다. raw `0x98F65`의 old bytes는
  `e8 56 6b f8 ff 3b c3 74 4c ... 6a 0a ... e8 46 67 f8 ff`다. lap50의 유일한
  slot1/group10 raw(`x=199,y=498,w=68,h=22`, click `0x00498ED0`, hit `0`)와 생성 인자가
  일치하므로 이 object는 `0x0049B6D0`의 group2..5 command cell이 아닌 별도 panel object다.
- `0x0049B6D0`의 유일한 call site는 `0x004992DF`다. 그 직전 old bytes(raw `0x992BE`)는
  `f6 04 95 4c 52 9b 00 08 74 24 8d 04 76 c1 e0 04 2b c6 8d 04 80 8b 0c c5 24 b8 66 00
  85 c9 75 0e 56 e8 ec 23 00 00`이다. 첫 조건은 BYTE
  `[0x009B524C + unit_type*0x394] & 0x08 != 0`, 둘째는 DWORD
  `[0x0066B824 + selected_slot*0x758] == 0`, 즉 selected unit base `0x0066B790 + slot*0x758`의
  `+0x94 == 0`이다. 두 조건을 모두 통과할 때만 group2..5 생성 함수가 호출된다.
- 조건이 거짓이면 `0x004992EC`의 `0x0040F770`/`0x0040FE90`/`0x00498E30` 기반
  `0x00892410` UI-list 경로로 진행한다. 이 대체 경로의 production icon/click 의미는 아직
  UNKNOWN이다. 화면에 icon grid가 보인다는 사실만으로 pool group2..5와 동일시하지 않는다.
- lap50 helper는 selected slot/type을 성공 결과에만 담고 두 predicate를 읽거나 실패 artifact에
  보존하지 않는다. 따라서 `group2..5 == []`를 무조건 transient reset으로 취급해 90초 polling하는
  계약은 원본 분기와 충돌한다. lap50에 두 runtime 값과 exact type이 없으므로 어느 predicate가
  거짓이었는지, 또는 비원자 frame reset 창이었는지는 UNKNOWN이다.
- 다음 work는 SHA fail-closed 뒤 selection/type/predicate를 pool 전후로 재확인하고, 같은 snapshot의
  두 predicate와 raw pool을 실패 evidence에 남겨 `49B6D0 eligible`과 `alternate path`를 구분해야 한다.
  predicate가 거짓이면 좌표를 클릭하거나 group2..5를 정상으로 완화하지 않고 명시적 필수 gate
  FAIL로 끝낸다. binary patch는 이 진단 범위에 없으며 원본 old/new/restore는 SKIP이다.

#### lap57 Sol 독립 검수 — type58은 49B6D0 대상이 아니며 alternate UI-list 계측 필요

- lap56 artifact/helper/원본 SHA와 raw `0x992BE`/`0x9B6D0`을 독립 대조했다. slot1199/type58의
  stable predicate는 type flags `0x009C21D4=0x10`, `&0x08=0`이고 selected state
  `0x00891D4C=0`이므로 원본은 `0x0049B6D0`이 아니라 `0x004992EC` false branch로 간다.
  따라서 type58은 선택된 HQ라는 시각·상태 근거가 있어도 **group2..5 command-cell 대상은 아니다**.
- false branch의 `0x0040F770`은 selected unit의 `+0x6BE` WORD를 반환한다. slot1199의 count 주소는
  `0x00892376`이다. caller는 index마다 `0x0040FE90`을 호출하며, 이 함수는 unit
  `+0x6C2+index*4`의 두 WORD가 모두 0일 때만 1을 반환한다. nonzero record일 때만
  `0x00498E30(index,1)`이 호출되어 index 0..9의 WORD flag `0x00893118+index*2`를 1로 만든다.
- `0x00499E2C..0x00499ECF`는 위 10개 flag를 훑고 `0x00498DB0` hit-test를 통과한 index를
  `0x00A90430`에 기록한다. hit geometry는 WORD globals `0x009E2BA4`(base x), `+0x2`(base y),
  `+0x4`(x pitch), `+0x6`(height)를 사용한다. 이는 alternate UI-list 표시/hover 경로의 raw
  근거지만, list record와 worker 생산 action의 연결은 아직 UNKNOWN이다.
- lap56은 alternate count/records/flags/geometry를 보존하지 않았으므로 화면 아이콘만으로
  `(670,490)` 또는 worker 생산을 승인할 수 없다. 다음 Luna work는 게임/바이너리를 건드리거나
  재실행하기 전에 stable-ineligible 진단에 위 alternate snapshot을 보존하는 helper/tests만 수리한다.

#### lap61 Sol 독립 진단 — group2..5는 HQ 생산의 필수 gate가 아니며 12-slot table이 선행 경계

- lap60 원본/private EXE SHA와 artifact SHA를 재계산했고, slot1199/type70의 stable
  `0x009C4CC4 & 0x08 == 0`, selected `+0x94 == 0`, alternate count/records/flags=0 및 cleanup을
  독립 확인했다. 따라서 lap60의 `49B6D0 ineligible` 관측 자체는 맞지만 이를 HQ 생산 실패로
  읽을 수는 없다.
- 원본 `0x00498EE0`은 frame UI 재구축 때 `0x00892410` object의 12-slot 네 WORD 배열을
  0으로 초기화한다. `0x004A3B5B` writer는 index `0..11`에 각각
  `0x008930A6`, `0x008930D6`, `0x008930BE`, `0x008930EE`를 stride 2로 쓴다.
  entry old bytes는 `66 8b 54 24 08 0f bf c0 66 89 94 41 96 0c 00 00`이다.
- 단일 선택 경로의 `0x00499201..0x00499297`은 선택 unit에서 최대12 record를 읽어
  `0x00498E60`을 통해 위 네 배열을 채운다. 이후 `0x00499583`은
  `0x008930BE`부터 순회하며 `0x004A3A40`으로 첫 배열을 조회한다. 이 primary 12-slot table은
  `0x004992BE` predicate보다 먼저 구성·소비된다.
- `0x004992BE` old bytes
  `f6 04 95 4c 52 9b 00 08 74 24`의 별도 predicate가 참일 때만
  `0x004992DF→0x0049B6D0`이 group2..5 네 cell을 추가한다. 그러므로 group2..5 eligible을
  일반 HQ 생산 입력의 필수 gate로 둔 현재 helper/card 계약은 원본 제어흐름과 충돌하며
  **HARNESS CONTRACT REVISE**다.
- 네 primary 배열의 field 의미와 실제 worker 생산 click/action 연결은 아직 UNKNOWN이다.
  다음 허용 변경은 의미를 추정하지 않고 네 24-byte raw block, 선택 identity, before/after coherence를
  보존하는 helper/tests뿐이다. 그 수리와 독립 확인 전에는 새 game run, 좌표·timeout·binary 변경을
  금지한다. binary old→new/restore는 이 source-only 진단에 N/A다.

#### lap62 Sol 승격 검수 — fill은 predicate 전, consume은 분기 합류 후

- 고정 원본 SHA와 lap60 artifact SHA를 다시 대조했고 모두 lap61 기록과 일치했다. 원본
  `0x00498EE0`은 index `0..11`마다 zero 4개를 `0x004A3B00`에 전달하고, writer
  `0x004A3B5B`는 `ecx=0x00892410` 기준 `+0xC96/+0xCC6/+0xCAE/+0xCDE`, 즉
  `0x008930A6/0x008930D6/0x008930BE/0x008930EE`에 WORD를 쓴다. 네 배열과 12-slot 경계는
  **CONFIRMED**다.
- `0x00499201..0x0049929E`의 index `0..11` fill은 `0x004992BE` predicate보다 앞선다.
  참 분기는 `0x004992DF→0x0049B6D0` 뒤 `0x00499583`으로 jump하고, 거짓/alternate 분기도
  `0x00499331` 등에서 같은 `0x00499583`으로 합류한다. 따라서 lap61의 “predicate보다 먼저
  구성·소비” 중 **구성만 맞고 소비는 틀리다**. consumer는 두 분기 뒤의 공통 후속 경계다.
- lap61 source-only 계약은 stable-ineligible 때 helper가 raw evidence를 붙여 기존처럼 fail-closed할지,
  성공 반환해 hard-coded production click으로 진행할지를 고정하지 않았다. 후자는 primary field/action과
  target mapping이 UNKNOWN인 상태에서 허용할 수 없으므로 계약은 **REVISE / GAME RUN BLOCKED**다.
- 다음 승격 검수 범위는 primary memory `0x008930A6..0x00893105`의 단일 96-byte read를 phase마다
  한 번 사용해 물리 순서 `A6/BE/D6/EE`를 각각 12 WORD로 분리하고, writer 인자 순서와 주소를 함께
  의미 중립적으로 기록하는 것이다. selection과 raw block 전후 값이 다르면 두 snapshot을 붙여
  fail-closed한다. stable-ineligible도 primary snapshot을 예외/diagnostics에 보존한 뒤 **기존처럼
  click 전에 중단**해야 하며, zero block은 raw 관측이지 생산 PASS/FAIL이 아니다. 새 Sol/Opus5가 이
  좁힌 계약을 확인하기 전 helper/tests 또는 game/binary/좌표/timeout 변경은 금지한다.

#### lap63 Sol 독립 재검수 — primary snapshot은 selected_count==1 전제가 추가로 필요

- 고정 원본에서 `0x00498FBA`가 selection count DWORD `0x00899024`를 읽는다. count `0`은
  `0x00498FC3` 경로, count `1`만 `0x00498FDB..0x0049929E`의 단일 선택/primary fill 경로,
  count `>1`은 `0x00498FD2→0x00499336`의 다중 선택 경로로 분기한 뒤 모두 `0x00499583`에
  합류한다. 따라서 primary 12-slot raw block을 현재 선택의 provenance로 보존하려면 snapshot
  시작 시 **selection count가 정확히 1**이어야 한다.
- lap62의 identity 안정성만으로는 부족하다. stable count `2`도 전후 identity가 같을 수 있지만 이때
  `0x00499201..0x0049929E` fill은 실행되지 않아 raw block이 reset/stale 값일 수 있다. 의미 중립
  기록이어도 현재 선택에 귀속해서는 안 되므로 lap62 handoff는 **REVISE / GAME RUN BLOCKED**다.
- 다음 계약은 SHA 확인 뒤 before selection count가 `1`이 아니면 primary 96-byte read와 click 전에
  count evidence를 붙여 fail-closed해야 한다. count `1`일 때만 lap62의 phase당 단일 contiguous
  96-byte before/after read와 selection/raw coherence를 수행한다. stable count `2` 조기 거부와
  primary read 미발생을 직접 회귀로 고정하고, `1→2` 전이는 두 raw snapshot 및 before/after identity와
  함께 fail-closed한다. 이 수정안을 새 Sol/Opus5가 확인하기 전 source/tests 변경은 보류한다.

#### lap65 Sol gate 회복 및 계약 확인

- Makefile의 정식 `.venv/bin/python -m pytest`로 targeted 46 PASS, 전체 Fast 116 PASS,
  safety PASS, doctor ok=true를 새로 확인했다. `.venv/bin/pytest` 부재는 의존성 부재가
  아니라 lap64의 invocation 오류였다.
- 고정 원본을 재추출해 lap63 count dispatch와 lap62 writer/consumer 경계가 일치함을
  확인했다. exact-single-selection source/test 계약은 **MIDDLE CONFIRM PASS / WORK READY**다.
  field/action 의미와 실제 worker click은 계속 UNKNOWN이며 이번 승인 범위가 아니다.

#### lap69 Sol selection-count 수리 확인과 호출부 경계

- 고정 원본/private SHA와 `0x00498FBA` count dispatch를 다시 대조했다. count0은 `0x00498FC3`,
  count1만 `0x00498FDB→0x00499201..0x0049929E` primary fill, count&gt;1은
  `0x00498FD2→0x00499336`으로 가며 모두 `0x00499583` consumer에 합류한다. writer
  `0x004A3B5B` old bytes도 `66 8b 54 24 08 0f bf c0 66 89 94 41 96 0c 00 00`으로 일치한다.
- lap68 source의 독립 count0/count2 probe는 각각 `0x00899024` DWORD 1회만 읽고 selection detail과
  primary table을 읽지 않았으며, required/observed/before/primary_read와 non-retryable 거부를
  보존했다. exact-single-selection 수리는 **MIDDLE CONFIRM PASS**다.
- 실제 run 권한은 별개다. helper의 stable-ineligible 예외에 포함된 primary snapshot을 현
  `g1-baseline` catch가 output evidence에 복사하지 않으며, eligible 반환 시에는 field/action·worker
  의미가 UNKNOWN인 hard-coded production click으로 진행한다. 이 두 호출부 경계를 fail-closed로
  수리하고 독립 확인하기 전 game run은 계속 금지한다.

#### lap71 Sol production fail-closed 부분 확인·gate 실패

- lap70은 stable-ineligible `_CommandCellSnapshotError.primary_snapshot`을
  `_record_g1_command_cell_error` 경유로 `primary_command_table` output에 복사하고, eligible raw
  evidence 반환 후에도 `_g1_production_click_if_authorized` 명시 gate가 항상
  `RuntimeSafetyError`를 내 mouse callback 전에 중단한다. ineligible은 reader 예외에서 더 먼저
  중단한다.
- 원본 SHA, count dispatch/fill/consumer, writer old bytes와 source/test SHA가 lap70 기록과
  일치했고 no-click/output evidence 3 PASS, targeted 57 PASS, Fast 127 PASS, safety/doctor PASS로
  source 계약은 부분 확인했다. 그러나 문서 기록 후 필수 Fast가 STATUS 183줄 제한
  위반으로 13 FAIL/114 PASS해 최종 **MIDDLE CONFIRM은 미완료**다. 승격 재검수 전
  game run은 BLOCKED이고 primary 네 field/action·worker 의미와 production click도 계속 UNKNOWN/미승인이다.

#### lap72 Sol overflow 복구 및 production fail-closed 확인

- lap71 상세를 history에 보존한 compaction 결과 STATUS 141줄을 확인했다. 고정 source/test/guard와
  원본·참고 EXE SHA, `0x00498FBA` count dispatch, `0x00499201..0x0049929E` count1 fill,
  `0x00499583` 공통 consumer, `0x004A3B5B` writer old bytes가 모두 일치했다.
- no-click/output 직접 3 PASS, targeted 57 PASS, 전체 Fast 127 PASS, safety/doctor PASS로 lap70
  fail-closed source 계약은 **MIDDLE CONFIRM PASS**다. 이는 네 primary field/action·worker 의미나
  production click 승인이 아니다. 다음 work에는 새 private live evidence-only run 1회만 허용한다.

#### lap74 Sol fresh private evidence 독립 확인

- lap73의 manifest/baseline/verdict/provenance/harness, 원본/private EXE와 8개 PNG SHA는 모두
  재계산 일치했다. root 1600x1200, game/content 및 PS9/PS3 surface 800x600, setup·selection 입력,
  stable-ineligible primary/alternate snapshot과 owned cleanup은 **MIDDLE CONFIRM PASS**다.
- 이 결과는 실제 2배 출력이나 production/drag/minimap 성공이 아니다. 다음 work는 고정 원본의
  `0x00499583→0x004A3A40` consumer 뒤 cell 생성 call을 정적으로 추적해 각 slot의 네 raw 인자,
  callback/action, strict rectangle을 주소/old bytes로 연결한다. 유일한 HQ worker 생산 연결을
  증명하지 못하면 UNKNOWN/blocker를 보존하며 game run·click·구현 변경은 하지 않는다.

#### lap75 Luna primary consumer 뒤 cell 생성 정적 추적 — primary-to-cell 연결 blocker

- 대상 원본 SHA는 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`로 재확인했다.
  `.text` VA `0x00401000`, raw `0x1000`이므로 아래 raw offset은 `VA-0x00400000`이다.
  확인한 entry old bytes는 `0x00499583: 33 f6 c7 44 24 10 be 30 89 00 6a 2b 56 b9 10 24`,
  `0x004A3A40: 66 8b 44 24 04 81 ec 80 00 00 00 66 85 c0 7d 49`,
  `0x004A3B5B: 66 8b 54 24 08 0f bf c0 66 89 94 41 96 0c 00 00`이다.
- primary fill은 `0x00499201..0x0049929E`에서 writer `0x004A3B5B`를 통해 index `i=0..11`마다
  `A6+2i`, `D6+2i`, `BE+2i`, `EE+2i`에 각각 WORD를 쓴다. writer의 인자 old bytes와 주소는
  다음과 같다: `arg2→0x008930A6+2i`, `arg3→0x008930D6+2i`,
  `arg4→0x008930BE+2i`, `arg5→0x008930EE+2i`.

| slot `i` | writer arg2 / A6 | writer arg3 / D6 | writer arg4 / BE | writer arg5 / EE |
|---:|---:|---:|---:|---:|
| 0 | `0x008930A6` | `0x008930D6` | `0x008930BE` | `0x008930EE` |
| 1 | `0x008930A8` | `0x008930D8` | `0x008930C0` | `0x008930F0` |
| 2 | `0x008930AA` | `0x008930DA` | `0x008930C2` | `0x008930F2` |
| 3 | `0x008930AC` | `0x008930DC` | `0x008930C4` | `0x008930F4` |
| 4 | `0x008930AE` | `0x008930DE` | `0x008930C6` | `0x008930F6` |
| 5 | `0x008930B0` | `0x008930E0` | `0x008930C8` | `0x008930F8` |
| 6 | `0x008930B2` | `0x008930E2` | `0x008930CA` | `0x008930FA` |
| 7 | `0x008930B4` | `0x008930E4` | `0x008930CC` | `0x008930FC` |
| 8 | `0x008930B6` | `0x008930E6` | `0x008930CE` | `0x008930FE` |
| 9 | `0x008930B8` | `0x008930E8` | `0x008930D0` | `0x00893100` |
| 10 | `0x008930BA` | `0x008930EA` | `0x008930D2` | `0x00893102` |
| 11 | `0x008930BC` | `0x008930EC` | `0x008930D4` | `0x00893104` |
- `0x00499583`의 loop는 `esi=0`, `esp+0x10=0x008930BE`에서 시작해 `i<12`까지
  `0x004A3A40`을 호출한다. `0x004A3A40`은 `i<12`일 때 오직
  `[ecx+i*2+0xC96] = 0x008930A6+2i`를 반환한다. 즉 이 primary consumer 자체가
  D6/BE/EE 값을 callback/action 인자로 전달한다는 고정 원본 결선은 없다.
- 별도 12-slot loop `0x0049AD3F..0x0049AFA8`는 `ptr=0x008930EE+2i`를 유지하면서
  `0x004A3A40`의 A6 반환값, `[ptr-0x30]=BE+2i`, `[ptr-0x18]=D6+2i`, `[ptr]=EE+2i`를
  읽는다. 이 값들은 `0x00419D80/0x00419E40` 및 `0x00465E80` 호출에 쓰이며
  `0x0041F630` cell constructor 호출이나 `0x0049B530/0x0049B640` callback 호출이 아니다.
  `0x004A3CA0` 경로도 command record 갱신이며 cell constructor가 아니다.

| 경계 | 고정 원본 결선 | old bytes / 판정 |
|---|---|---|
| primary consumer | `0x00499583→0x004A3A40`; A6만 반환, 12회 | `4A3A40: 66 8b 44 24 04 81 ec 80 00 00 00 66 85 c0 7d 49`; PASS |
| 조건부 cell entry | `0x004992BE` flag `0x08` → `0x004992DF→0x0049B6D0` | `49B6D0: 53 55 56 8b 74 24 10 57 56 b9 6c e3 61 00 e8 bd`; PASS, primary 뒤 아님 |
| cell constructor | `0x0049B6D0→0x0041F630`, group `2,3,4,5` | `41F630: 8b 44 24 04 8b 54 24 0c 53 8b 5c 24 38 56 57 8b`; PASS |
| cell callbacks | `+0x54=0x0049B530`, `+0x58=0x0049B640` | `49B530: 56 8b 74 24 08 57 56 e8 04 ba f7 ff 83 c4 04 85`; `49B640: 56 8b 74 24 08 56 e8 85 b9 f7 ff 83 c4 04 85`; group path only |
| strict rectangle | `0x0041FA60`: active and `x≤input<x+w`, `y≤input<y+h` | `41FA60: 83 39 00 74 36 0f bf 05 14 d8 4e 00 8b 51 08 3b`; group path only |
- `0x0049B6D0` 네 cell은 runtime type record `0x0066BE88+type*0x758`와 globals
  `0x009E2BAC/0x009E2BB0/0x009E2BB4/0x009E2BB8`로 geometry를 만들고, flags
  `0x40000/0x200/0x80000/0x100000`를 `0x0049B530`에 전달한다. `49B530`은 이를
  action `0x19A/0x19C/0x19E/0x1A1`로 매핑하고 `49B640`은 같은 flag의 type record를
  `0x00421550`에 전달하지만, 이 action 중 HQ worker 생산을 뜻하는 근거는 없다.
- 결론: primary 12-slot의 네 raw field source는 확정했지만 primary D6/BE/EE→cell
  callback/action/strict rectangle의 직접 edge가 없고, 유일한 HQ worker 생산 후보도 증명할 수 없다.
  따라서 worker 의미와 primary-to-cell mapping은 **UNKNOWN / CONCRETE BLOCKER**이며,
  좌표·fixture·harness·tests·binary·game run은 변경하지 않는다.

#### lap76 middle 독립 확인 — primary cell 가정 반려, dispatch probe 승인

- 고정 원본 SHA와 `0x00499583`, `0x004A3A40`, `0x004A3B5B`, `0x0049B6D0`, `0x0041F630`,
  `0x0049B530`, `0x0049B640`, `0x0041FA60`의 16-byte old bytes가 lap75 기록과 모두 일치했다.
- 전체 direct xref에서 `0x0049B6D0` call은 `0x004992DF` 하나뿐이고 `0x0041F630` call은 8개다.
  `0x00499583..0x00499BCF` 안에는 `0x0041F630/0x0049B530/0x0049B640/0x0049B6D0`
  direct call이 없다. 따라서 lap75의 primary-to-cell 단절/worker UNKNOWN은 **MIDDLE CONFIRM PASS**다.
- 다음 work는 cell object를 계속 가정하지 않고 primary panel 자체 dispatch를 좁게 추적한다.
  `0x00499583..0x00499BB8`과 draw/state loop `0x0049AD33..0x0049AFB8`에서 A6/BE/D6/EE의
  각 read, branch, immediate/action, callee, input-state 사용을 표로 만든다. 유일한 production
  dispatch가 증명되지 않으면 UNKNOWN/blocker로 끝내며 game run과 source/tests 변경은 금지한다.

#### lap77 Luna primary-panel dispatch dataflow — static trace complete, worker UNKNOWN

- 대상은 동일한 읽기 전용 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`다.
  `.text`의 VA/raw 관계는 VA `0x00401000`, raw `0x1000`, file offset `VA-0x00400000`로
  lap75/76과 같다. 이번 probe는 `0x00499583..0x00499BB8` 및 `0x0049AD33..0x0049AFB8`에
  한정했고, 코드/tests/binary/fixture/좌표/game run은 변경하지 않았다.
- `0x004A3A40`의 `0x004A3AEC` read는 `WORD [ecx+edx*2+0xC96]`이다. 호출 시 `ecx=0x00892410`
  이므로 `edx=i=0..11`일 때 source는 `0x008930A6+2*i`다. primary consumer 범위의
  `0x004A3A40` call sites는 `0x0049959F/0x004995C5/0x004995EB/0x0049961C/0x00499646/
  0x00499688/0x004997AE/0x004997DC/0x0049990C/0x00499AAD/0x00499AE2/0x00499B10`이며,
  반환값은 주변 `0x00496360/0x00496390` lookup·predicate와 상태 갱신에 쓰인다.

| field | read / range | branch·callee와 dataflow | 판정 |
|---|---|---|---|
| A6 | `0x004A3A40`의 12회 table read; 직접 `0x004998E8`도 `WORD [edx*2+0x008930A6]`를 읽음 | 직접 read는 `0x004998F7→0x004A3CA0`; 이 callee는 `0x00416F40/0x00496360`와 command-record 내부 write를 수행하며 `0x0043EDA0/0x00443190` 또는 cell constructor 호출이 없다. | A6 consumer/record update는 PASS; worker/action 의미 UNKNOWN |
| BE | `p=0x008930BE+2*i`; `0x0049978B` 및 `0x00499A43`의 `cmp WORD [p],0` | zero면 `0x00499B9E`로 loop continue/end boundary; nonzero path는 `0x004AC3E0`와 `0x004A3A40/0x00496360` 상태·표시 lookup으로 이어진다. | read→branch PASS; production edge 없음 |
| D6 | first loop에서는 `0x00499BA6`의 `cmp p,0x008930D6`만 존재 | `p`를 2씩 올려 `0x008930BE..0x008930D4` 12개 entry를 순회하는 sentinel이며 D6 table value read가 아니다. | boundary PASS; action 의미 없음 |
| EE | first range에는 raw EE read 없음 | 없음. | 범위 내 미사용 |

- 두 번째 draw/state loop에서 `ebx=i=0..11`, `p=0x008930EE+2*i`다. 따라서
  `[p-0x30]=BE+2*i`, `[p-0x18]=D6+2*i`, `[p]=EE+2*i`로 물리 table과 정확히 대응한다.
  A6는 아래 `0x004A3A40` call이 같은 `A6+2*i` accessor를 호출한다.

| field | read site | branch / callee | input·action 경계 |
|---|---|---|---|
| A6 | `0x0049AD47`, `0x0049AD60`, `0x0049AE71`, `0x0049AE98`의 `0x004A3A40` 반환 | `0x00496370/0x00496390` lookup·test 뒤 `0x00419D80` 또는 상태 표시 경로 | `0x004A3CA0` 및 production call 없음; 의미 UNKNOWN |
| BE | `0x0049AE05`: `cmp WORD [p-0x30],1` | not-equal `0x0049AE45→0x00419E40`; equal은 `bp==1` 조건 뒤 `0x00419D80` 및 공통 `0x00419D80` | draw/state helper로 관측; worker/action 아님을 직접 증명할 callee 없음 |
| D6 | `0x0049AED8`: `cmp WORD [p-0x18],0` | positive면 count loop에서 `0x0049AF03→0x00465E80`; zero/non-positive면 `0x0049AF24`로 건너뜀 | renderer memory write helper; production edge 없음 |
| EE | `0x0049AF28`: `mov cx,[p]`, `test cx,cx` | zero면 `0x0049AF8F`; nonzero면 `0x00419D40` lookup과 `0x004179D0` 호출 | draw/state arithmetic; worker 의미 UNKNOWN |

- 두 번째 loop의 `p`는 `0x0049AF9F`에서 `0x00893106`과 비교되어 `0x008930EE..0x00893104`
  12개를 순회한다. `0x0049AD76/0x0049ADDD/0x0049AE01` 주변의 `0x669918`, `0x1057958`,
  `0x4F3D10` 상태값과 첫 loop의 `0x899024/0x899028` selection state는 input/state
  provenance이지만, raw field를 유일한 production action으로 연결하지 않는다.
- direct xref 보강: `0x004A3CA0`의 call site는 `0x004998F7` 하나다. `0x0041F630`,
  `0x0049B530`, `0x0049B640`, `0x0049B6D0`은 두 지정 범위에서 direct call이 없다.
  따라서 이번 표는 read→branch/callee의 **STATIC TRACE PASS**이나 primary worker/action
  연결은 **UNKNOWN / CONCRETE BLOCKER**다. 기존처럼 추정 구현·game run·좌표/fixture/harness/
  tests/binary 변경을 금지한다.

#### lap78 Sol 독립 검수 — EE read-site 정정, 전체 판정 REVISE/ESCALATE

- 고정 원본 SHA와 lap77의 8개 entry old bytes, primary의 `0x004A3A40` 12개 call site,
  `0x004998F7→0x004A3CA0` 유일 direct call, 두 지정 범위의 cell constructor/callback direct call
  부재는 독립 재추출과 일치했다.
- lap77 history와 위 표가 EE raw read를 `0x0049AE28`로 기록한 것은 주소 오류다. 실제 instruction은
  `0x0049AF28: 66 8b 0a` (`mov cx,[edx]`)이고, `0x0049AE28`은 앞선 `add esp,0x10`의 마지막
  바이트라 instruction entry가 아니다. canonical 표는 `0x0049AF28`로 정정했으며 lap77 원문은
  provenance 보존을 위해 수정하지 않았다.
- 따라서 worker/action UNKNOWN이라는 넓은 결론은 유지되지만 lap77의 exact-address trace는
  **MIDDLE CONFIRM REVISE / ESCALATE**다. 다음 work는 고정 원본에서 `0x00419D80→0x004664D0`,
  `0x00419E40→0x00466540`, `0x00465E80`, `0x0049AF28→0x00419D40/0x004179D0`의 한 단계 side-effect와
  call boundary를 표로 만들어 rendering/state와 command enqueue를 근거로 구분한다.

#### lap79 Luna render-helper side-effect probe — rendering/state 분리, enqueue는 미확정

- 대상은 읽기 전용 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`다.
  `.text` VA `0x00401000`, file raw offset `VA-0x00400000` 관계를 유지했고, 게임 실행·후보 바이너리·fixture·좌표·소스/tests는 변경하지 않았다.
- entry old bytes는 다음과 같다. 호출 instruction도 직접 xref에서 재추출했다.

| entry | old bytes (16B) | relevant direct callsite / old bytes |
|---|---|---|
| `0x00419D80` | `8b 4c 24 0c 8d 04 49 8d 14 49 c1 e0 07 2b c1` | `0x0049ADF9/AE21/AE3B/AEC4 → 0x00419D80`; `49ADF9: e8 82 ef f7 ff` |
| `0x00419E40` | `8b 4c 24 0c 8b 54 24 14 52 8d 04 49 8d 14 49` | `0x0049AE5C → 0x00419E40`; `49AE5C: e8 df ef f7 ff` |
| `0x00465E80` | `8b 41 10 53 55 8b 6c 24 0c 56 3b e8 57 7d 7d 85` | `0x0049AF03 → 0x00465E80`; `49AF03: e8 78 af fc ff` |
| `0x004664D0` | `55 56 8b 74 24 10 8b e9 8b 54 24 0c 57 0f af 75` | `0x00419DCB → 0x004664D0`; `419DCB: e8 00 c7 04 00` |
| `0x00466540` | `51 53 56 57 8b 7c 24 18 0f af 79 10 8b 99 14 15` | `0x00419E90 → 0x00466540`; `419E90: e8 ab c6 04 00` |
| `0x0049AF28` | `66 8b 0a 66 85 c9 74 5f 0f bf e9 b8 1f 85 eb 51` | `0x0049AF76 → 0x00419D40`; `49AF76: e8 c5 ed f7 ff`; `0x0049AF87 → 0x004179D0`; `49AF87: e8 44 ca f7 ff` |

| edge | one-step call/write evidence | classification / command boundary |
|---|---|---|
| `0x00419D80 → 0x004664D0` | caller computes table-derived coordinates and calls once; callee has no calls and writes `BYTE PTR [edx+esi]` while `esi` is based on `[ecx+0x1514]` and stride `[ecx+0x10]` | bounded byte-buffer/raster write; no direct command-record enqueue in this edge |
| `0x00419E40 → 0x00466540` | caller passes the extra source argument; callee has no calls and copies source bytes into the same object-relative stride buffer via `BYTE PTR [esi+edi-1]` | bounded byte-buffer/raster write; no direct command-record enqueue in this edge |
| `0x00465E80` | validates both coordinates against `[ecx+0x10/+0x14]`, color `& 0xff < 0x100`, then writes `BYTE PTR [eax+ebp-1]`; no calls | direct bounded buffer write; no command enqueue evidence |
| `0x0049AF28 → 0x00419D40` | `mov cx,[edx]`/`test`; nonzero path computes a scale and calls pure lookup `0x00419D40`, which only reads `[0x0051EE94 + index*8]` and returns | state/layout arithmetic lookup; no write or enqueue |
| `0x0049AF28 → 0x004179D0` | same nonzero path calls `0x004179D0`; target uses local stack state, direct-calls `0x00419D40/60`, `0x004650C0`, `0x00465130`, `0x004A98D0`, `0x0041A3C0`, `0x0041A370`, `0x004E4146`, and performs indirect `call DWORD PTR [0x004E5190]` twice | text/glyph/render path is supported by the immediate calls and raster helpers; the indirect sink is unresolved, so deeper enqueue absence is not proven |

- Known command-record callee `0x004A3CA0` still has only direct callsite `0x004998F7`; none of the traced helper edges calls it. This is a static separation only, not proof that the unresolved `0x004E5190` indirect target cannot enqueue a command.
- 판정: render/state side-effect 표와 direct/indirect call boundary는 **STATIC TRACE PASS**. primary worker/action mapping과 complete command-enqueue exclusion은 **UNKNOWN / CONCRETE BLOCKER**다. 추정 구현·game run·좌표/fixture/harness/tests/binary 변경을 계속 금지한다.

#### lap80 middle 독립 검수 — indirect sink 해소, lap79 old-byte 표 정정

- 읽기 전용 원본 두 사본의 SHA는 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`다. `.text`의
  VA/raw 관계 `VA-0x00400000`를 독립 확인하고 `xxd`와 `objdump -d -Mintel`로 entry와
  callsite를 다시 추출했다.
- lap79의 `0x00419D80` 16B 값은 잘못됐다. 실제 값은
  `8b 4c 24 0c 8d 04 49 8d 14 49 c1 e0 07 c1 e2 07`이며, lap79 값은 두 번째
  shift `c1 e2 07`을 건너뛰고 뒤의 `2b c1`을 붙인 15B다. `0x00419E40` 실제 16B는
  `8b 4c 24 0c 8b 54 24 14 52 8d 04 49 8d 14 49 c1`이며 lap79에는 첫 15B만 적혔다.
  나머지 `0x00465E80/0x004664D0/0x00466540/0x0049AF28` 16B와 모든 지정 5B callsite는
  일치한다. lap79 원문은 provenance 보존을 위해 수정하지 않는다.
- PE import directory에서 KERNEL32 FirstThunk는 RVA `0x000E5080`이다. IAT slot
  `0x004E5190`은 `(0x110/4)=68`번째 zero-based thunk이고 raw DWORD가 import-by-name RVA
  `0x000EB3A0`을 가리키며 그 hint/name은 `lstrlenA`다. `0x00417B07/0x00417B82`의 두 간접
  호출은 stack string 주소를 넘기고 반환 길이를 빈 문자열 분기와 digit loop bound에 사용한다.
  따라서 이 두 indirect edge의 command enqueue 가능성은 **EXCLUDED / PASS**다.
- `0x00419D80→0x004664D0`, `0x00419E40→0x00466540`, `0x00465E80`의 stride-buffer byte
  write와 `0x0049AF28→0x00419D40/0x004179D0` render/text 흐름은 독립 재추출과 일치한다.
  그러나 두 literal old-byte 행 오류 때문에 lap79 전체 판정은 **MIDDLE CONFIRM REVISE /
  ESCALATE**다. 이 정정은 primary field의 worker/action 의미를 제공하지 않으므로 구현 근거는
  계속 **UNKNOWN / CONCRETE BLOCKER**다.
- 구현 미변경이 두 바퀴 연속이므로 다음 work는 이미 확인한 draw helper를 반복하지 않는다.
  고정 원본 `0x004A3CA0`의 write-set `object+0xBF6/+0xC22/+0xC24/+0xC4E/+0xC64`를 읽는
  xref를 좁게 열거하고, 그중 실제 input hit/action dispatch로 이어지는 consumer 하나를 old bytes와
  branch/callee 표로 증명하거나 구체적인 indirect/data-xref blocker로 끝낸다. 그 전에는 production
  click, game run, source/tests/binary/fixture/좌표 변경을 금지한다.

#### lap81 Luna `0x004A3CA0` record reader/data-xref probe — consumer concrete blocker

- 대상은 읽기 전용 원본 두 사본이며 SHA는 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다. `.text`의
  VA/raw 관계는 `VA-0x00400000`이고, 이번 probe는 `0x004A3CA0` write-set과 primary
  caller/인접 input 경계에만 한정했다. 후보 바이너리·게임 실행·fixture·좌표·source/tests는 없다.
- 고정 원본에서 `objdump -d -Mintel` 전체 `.text`의 정확한 object-offset xref를 열거했다.

| field | reader / compare | writer / initializer | 판정 |
|---|---|---|---|
| `object+0xBF6` | `0x004A3CED` `WORD [esi+eax*2+0xBF6]` | `0x004A3D32`; init `0x004A3186` | `0x004A3CA0` 내부 cache/update만 |
| `object+0xC22` | `0x004A3CFF` `WORD [esi+eax*4+0xC22]` | `0x004A3D3A`; init `0x004A318A` | `0x004A3CA0` 내부 cache/update만 |
| `object+0xC24` | `0x004A3D0E` `WORD [esi+eax*4+0xC24]` | init `0x004A318D` | record match compare만 |
| `object+0xC4E` | 전체 `.text`에 reader 없음 | `0x004A3D41`; init `0x004A3191` | reader 미확인 |
| `object+0xC64` | 전체 `.text`에 reader 없음 | `0x004A3D51`; init `0x004A3194` | reader 미확인 |

- `0x004A3CA0` old bytes는 `53 55 8b 6c 24 0c 56 0f bf c5 57 8b f1 50 e8 8d`이고,
  전체 direct xref는 `0x004998F7: e8 a4 a3 00 00` 하나다. 함수는 `0x004A3CAE→0x00416F40`,
  `0x004A3CD2→0x00496360` 두 callee와 12-slot loop의 zero/equality branch를 수행한 뒤,
  새 record에서 `BF6/C22/C4E/C64`를 쓰고 `0x004A3D5C`에서 반환한다. 성공적인 record write
  뒤 input hit-test, callback, action enqueue callee는 없다.
- 따라서 이 write-set을 읽어 실제 input hit/action consumer로 이어지는 data edge는 이번
  고정 원본에서 증명되지 않았다. `0x004A3CA0`은 command-record cache/update로 분류할 수
  있지만 worker/action 의미는 **UNKNOWN / CONCRETE BLOCKER**다. 기존 group2..5의
  `0x0041FA60→object+0x58→0x0049B640` hit 경계 및 `0x0049B530` action 경계와 이 record를
  동일시하지 않는다. 추정 구현·production click·game run은 계속 금지한다.

#### lap82 middle 독립 검수 — record xref 확인, 상위 input/dispatch probe로 이관

- 읽기 전용 원본 두 사본의 SHA는 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이고 `.text`는
  VA/raw `0x00401000/0x1000`이므로 file offset은 `VA-0x00400000`이다.
- `0x004A3CA0` 16B `53 55 8b 6c 24 0c 56 0f bf c5 57 8b f1 50 e8 8d`와
  `0x004998F7` call 5B `e8 a4 a3 00 00`가 두 사본에서 일치했다. 전체 `.text` direct call은
  `0x004998F7→0x004A3CA0` 하나이고, callee 내부 call은 `0x004A3CAE→0x00416F40`과
  `0x004A3CD2→0x00496360`뿐이다.
- exact displacement 재검색은 lap81과 일치했다. `BF6/C22/C24` reader는 각각
  `0x004A3CED/0x004A3CFF/0x004A3D0E`의 동일 함수 내부 compare뿐이다. `C4E/C64`에는
  direct reader가 없고, write는 `0x004A3D41/0x004A3D51`; initializer는
  `0x004A3175/0x004A317B`에서 만든 포인터를 사용하는 `0x004A3186/8A/8D/91/94` loop다.
  record write 뒤 `0x004A3D58..5C`는 pop/return이고 caller는 `0x004998FC`에서 공통 loop
  tail `0x00499B9E`로 분기하므로 이 좁은 경계에 hit-test/callback/action callee가 없다.
- 판정은 lap81 정적 추출에 대한 **MIDDLE CONFIRM PASS**다. 이는 worker/action 의미나 G1 제품
  합격이 아니며, field 자체에는 외부 reader가 없어 이를 반복 추적할 근거가 없다. 구현은 계속
  금지한다. 다음 work-tier 단일 probe는 확인된 상위 chain
  `0x0041C81E→0x0041E220→0x0041E60C→0x00498F50`에서 `0x0041E220`의 실제 input-state
  read/branch와 action-dispatch sibling callee를 old bytes·xref·side-effect로 연결하거나,
  direct edge 부재를 새 concrete blocker로 남긴다. 시작 bytes는
  `41E220=83ec205355bd0100000033db66392d88`,
  `41E60C=e83fa90700a0fc2f890084c00f855601`,
  `498F50=81ec9801000053555633db57895c2420`이다.

#### lap84 Luna `0x0041E220` input/dispatch chain probe — static edge and queue sink PASS

- 고정 원본 두 사본의 SHA는 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이며 PE32 i386이다.
  `.text` VA/raw는 `0x00401000/0x1000`이고 file offset은 `VA-0x00400000`이다. 후보 바이너리,
  게임 실행, production click, fixture/좌표/source/tests 변경은 없었다.
- exact old bytes와 direct edge는 다음과 같이 고정 원본에서 재추출했다.

| entry | old bytes (16B) | direct edge / 관측된 side-effect |
|---|---|---|
| `0x0041E220` | `83 ec 20 53 55 bd 01 00 00 00 33 db 66 39 2d 88` | `0x0041C81E→0x0041E220`; `0x0041E269→0x0041D310`, `0x0041E270→0x0041D360`, `0x0041E299→0x004217B0` |
| `0x004217B0` | `a1 70 e2 61 00 85 c0 0f 84 93 00 00 00 8b 44 24` | `[0x61E270]` queue count를 검사하고 event state `[0x61DA30..0x61DA3C]`를 caller buffer로 복사·shift·decrement한 뒤 `1` 반환 |
| `0x0041E60C` | `e8 3f a9 07 00 a0 fc 2f 89 00 84 c0 0f 85 56 01` | `0x0041E60C→0x00498F50`; 반환 뒤 `[0x892FFC]` action-state branch |
| `0x00498F50` | `81 ec 98 01 00 00 53 55 56 33 db 57 89 5c 24 20` | selection-count 분기와 primary 12-slot/table 처리; action-state를 후속 branch에 넘김 |
| `0x0041EB75` | `b9 10 24 89 00 e8 81 4b 08 00 a1 6c cb c0 00 be` | `0x0041EB7A→0x004A3700`, `ecx=0x00892410`으로 호출 |
| `0x004A3700` | `0f bf 81 9a 6b 00 00 0f bf 54 24 04 8d 04 40 89` | count `[ecx+0x6B9A]` 기준 세 인자를 `+0x6B9C`, `+(count+0x8F8)*12`, `+0x6BA4`에 기록하고 count를 최대10까지 증가 |

- 따라서 `0x0041E220`의 실제 input-state read/branch와 `0x004A3700`의 action/command queue
  append side-effect는 직접 edge와 old bytes로 연결됐다. 판정은 **STATIC INPUT/DISPATCH CHAIN PASS**다.
  다만 `0x0041D310`의 간접 poll target, table field의 worker/production 의미, 실제 사용자 입력과
  게임 runtime 결과는 **UNKNOWN**이며 G1 합격이나 구현 승인으로 승격하지 않는다.

#### lap85 Sol 독립 검수 — static facts PASS, queue semantic label REVISE

- 두 원본 SHA/PE 매핑과 lap84의 7개 old-byte entry, four direct calls,
  `0x004217B0`의 event record 복사·shift·count 감소는 독립 재추출과 일치했다.
- `0x004A3700`은 `[ecx+0x6B9A]` index로 `+0x6B9C/+0x6BA0/+0x6BA4` 3 DWORD를
  기록하고 count가 `10` 미만일 때만 증가한다. 이 append형 write-set은 **CONFIRMED**다.
- 다만 현재 근거에는 이 record의 reader/consumer가 없으므로 `command/action queue`,
  worker production 또는 primary table dispatch로의 의미 승격은 **REVISE / UNKNOWN**이다.
- 다음 work-tier는 `0x00892410+0x6B9A/+0x6B9C/+0x6BA0/+0x6BA4` reader/consumer를
  완전 열거하고 production callback/command sender 연결을 증명하거나 부재를 blocker로 남긴다.

#### lap86 Luna `0x004A3700` exact record consumer enumeration — readers complete, production meaning blocked

- 고정 원본 두 사본의 SHA는 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다. PE32 i386의
  `.text` VA/raw는 `0x00401000/0x1000`이고, file offset은 `VA-0x00400000`이다. 후보
  바이너리·게임 실행·production click·fixture/좌표·source/tests 변경은 없었다.
- `0x004A3700`의 유일한 direct caller는 `0x0041EB7A: e8 81 4b 08 00`이다.
  `ecx=0x00892410`이며 writer는 count `+0x6B9A`를 읽어 12-byte stride로
  `+0x6B9C/+0x6BA0/+0x6BA4`를 쓰고, count가 `10` 미만이면 `+0x6B9A`를 증가시킨다.
- exact data xref는 다음과 같다. `+0x6B9A`는 writer 내부 read/write와 reset
  `0x00412ED9/0x0041F0CF` 외 read가 없다. `+0x6B9C`는 writer와
  `0x0041ED34/0x0041EFCC/0x0041EFF9` read, `0x004AEC2F`의 end-pointer compare가
  전부다. `+0x6BA0`는 writer와 `0x0041ED2D/0x0041EFC6/0x0041EFF4` read가 전부다.
  `+0x6BA4`는 writer와 `0x0041EC47/0x0041EC8E/0x0041EE0B/0x0041EF7C/0x0041EFD2/
  0x0041EFFF` read가 전부다.
- consumer는 `0x0041EBF4..0x0041F0CF`의 event-dispatch branches다. code `0x08` 경로는
  `+0x6B9C/+0x6BA0`를 `0x00436B10`(경계 검사 후 map byte lookup)에 넘기고,
  `0x00427B80` type-flag predicate를 거친다. 다른 branches는 `+0x6BA4`를
  `0x0040FB50/0x004A4860/0x00438820`으로 넘기며, 최종 경로는 세 field를
  `0x004AE550`으로 넘긴다.
- `0x004AC3E0`은 고정 `0x0105AAE0`의 5-slot/3-word generic event ring에 쓰고
  `0x004AA820`으로 복사한다. `0x004AE550→0x004A3C10`은 object `+0xDD4`의
  최대3개 15-DWORD bounded queue에 복사/count 증가만 수행한다. 이 side-effect에는
  production callback, unit spawn, worker queue, primary command sender의 직접 edge가 없다.
- 판정: exact field reader/consumer enumeration **STATIC PASS**; generic event/state queue
  소비 경계는 확인했지만 production/worker 의미와 실제 사용자 입력/runtime 결과는
  **UNKNOWN / CONCRETE BLOCKER**다. 추정 구현·game run·좌표/fixture/source/tests/binary
  변경은 계속 금지한다.

#### lap87 Sol 독립 검수 — exact enumeration 누락으로 REVISE

- 두 고정 원본은 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  및 byte identity가 일치하고 `.text` VA/raw `0x00401000/0x1000`도 동일하다.
- 전체 `objdump -d -Mintel` 재검색에서 lap86이 세지 않은 `0x004A31F2:
  66 89 9e 9a 6b 00 00` (`[esi+0x6B9A]` reset/write)와 `0x0041EFA5:
  66 a1 b4 8f 89 00` (`0x00898FB4`, 즉 base `+0x6BA4` direct read)가 확인됐다.
  따라서 reset/write 2개 및 `+0x6BA4` read 6개라는 완전성 판정은 **REVISE**다.
- `+0x6B9C` direct read 3개와 end-pointer compare 1개, `+0x6BA0` read 3개,
  `0x004AC3E0→0x004AA820` 5-slot/3-WORD event ring 및
  `0x004AE550→0x004A3C10` 최대3개/15-DWORD queue 경계는 재현됐다. 이는 누락을
  상쇄하지 않으며 production callback/worker/command sender 의미는 계속 UNKNOWN이다.
- 다음 work-tier는 누락 2개를 포함해 네 field의 read/write/reset 전체 표와 branch coverage를
  다시 만들고, 다음 새 middle이 독립 검수하기 전 구현·실행을 금지한다.

#### lap88 Luna `0x00892410+0x6B9A..0x6BA4` exact xref correction — static enumeration PASS, production meaning blocked

- 고정 원본 `Syw2plus/syw2plus_original.exe`와 private copy
  `local/runtime/20260911_082430_2926029_0/game/syw2plus_original.exe`는 `cmp`가 일치하고,
  두 SHA는 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다. PE32 i386
  `.text` VA/raw는 `0x00401000/0x1000`, file offset은 `VA-0x00400000`이다. 후보·게임 실행·
  fixture·좌표·source/tests 변경은 없었다.
- 전체 `.text`의 `objdump -d -Mintel` 절대주소 검색과 base-relative 검색을 다시 대조한
  정정 표는 다음과 같다. writer `0x004A3700`의 동적 slot write는 해당 field의 write로
  표시하고, direct absolute access와 분리했다.

| field | write/reset | direct read / compare | consumer branch coverage |
|---|---|---|---|
| `+0x6B9A` (`0x00898FAA`) | reset `0x00412ED9`, `0x0041F0CF`, **`0x004A31F2`**; writer count write `0x004A3750` | writer count reads `0x004A3700/0x004A3716/0x004A372D/0x004A3742` | writer index/count; reset paths only, external consumer 없음 |
| `+0x6B9C` (`0x00898FAC`) | writer slot write `0x004A370F` | `0x0041ED34/0x0041EFCC/0x0041EFF9` read; `0x004AEC2F` end-pointer compare | code `0x08`: `0x0041ED34→0x00436B10`; common pack `0x0041EFCC/0x0041EFF9→0x004AE550`; loop bound compare `0x004AEC2F→0x004AE8BE` |
| `+0x6BA0` (`0x00898FB0`) | writer slot write `0x004A372A` | `0x0041ED2D/0x0041EFC6/0x0041EFF4` read | code `0x08`: `0x0041ED2D→0x00436B10→0x00427B80`; common pack `0x0041EFC6/0x0041EFF4→0x004AE550` |
| `+0x6BA4` (`0x00898FB4`) | writer slot write `0x004A373B` | compare `0x0041EC47`; reads `0x0041EC8E/0x0041EE0B/0x0041EF7C/0x0041EFA5/0x0041EFD2/0x0041EFFF` | code `0x04`: `0x0041EC47/0x0041EC8E→0x0040FB50→0x004AC3E0`; code `0x15`/common: `0x0041EE0B/0x0041EF7C/0x0041EFA5→0x004A4860/0x00438820/0x00416F40/0x0040FB80`; common pack `0x0041EFD2/0x0041EFFF→0x004AE550` |

- `0x004A3700` direct caller는 `0x0041EB7A` 하나이며, caller bytes는 `e8 81 4b 08 00`,
  직전 `ecx=0x00892410` 설정은 `0x0041EB75`에서 확인된다. 정정된 direct xref 수는
  `+0x6B9A` reset 3개(+ writer count write 1), `+0x6B9C` read 3/compare 1,
  `+0x6BA0` read 3, `+0x6BA4` read 7/compare 1이다. 이는 lap86의 `reset 2/read 6`
  완전성 주장을 **REVISE→STATIC ENUMERATION PASS**로 정정한다.
- consumer는 `0x0041EBF4..0x0041F0CF` dispatch와 `0x004AEC2F` bounded-loop compare에
  한정된다. 확인된 `0x004AC3E0→0x004AA820` generic event ring 및
  `0x004AE550→0x004A3C10` bounded queue 경계에는 production callback, unit spawn,
  worker queue, primary command sender의 직접 edge가 없다. 따라서 field/action의
  production 의미, 실제 click/runtime, G1 합격과 구현 근거는 계속 **UNKNOWN / BLOCKED**다.

#### lap89 Sol 독립 검수 — 정적 표 CONFIRM, production 의미 BLOCKED

- 두 원본 SHA/byte identity와 PE 매핑, `0x0041EB75/7A→0x004A3700`, 모든 absolute 및
  base-relative raw occurrence와 old bytes를 독립 재추출해 lap88 표와 일치함을 확인했다.
- 정확한 분류는 `+0x6B9A` reset 3/write 1/reader 4, `+0x6B9C` 일반 read 3/compare 1,
  `+0x6BA0` 일반 read 3, `+0x6BA4` 일반 read 6/compare 1(총 참조 7)이다. 따라서 lap88의
  `read 7/compare 1` 요약은 새 site 누락이 아니라 **총 참조 7 중 compare 1**로 정밀화한다.
- event-dispatch branch와 `0x004AC3E0→0x004AA820` 5-slot/3-WORD ring,
  `0x004AE550→0x004A3C10` 최대3개/15-DWORD queue side-effect는 **MIDDLE CONFIRM PASS**다.
  production/worker/unit spawn/primary sender 의미는 직접 edge가 없어 계속 UNKNOWN이다.
- 구현 미변경 lap88~89 연속 2바퀴이므로 동일 xref 재열거를 중단한다. 다음 work-tier는
  generic ring 후보 dequeue `0x004AC420` 하나의 direct caller와 downstream side-effect를
  열거해 production edge를 증명하거나 정확한 direct-edge 부재를 blocker로 남긴다.

#### lap90 work-tier `0x004AC420` generic event-ring dequeue probe — static PASS, semantic BLOCKED

- 고정 원본 `Syw2plus/syw2plus_original.exe`, 루트 원본 및 private copy
  `local/runtime/20260911_082430_2926029_0/game/syw2plus_original.exe`는 모두 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이고 `cmp`가
  일치한다. PE32 i386 `.text`는 VA `0x00401000`, raw `0x1000`, size `0xE3AE5`이며
  file offset은 `VA-0x00400000`이다.
- `0x004AC420` raw `0xAC420`의 37-byte old bytes는
  `66 8b 15 fe aa 05 01 83 ec 08 66 85 d2 55 56 0f 8e aa 00 00 00 a1 e0 aa 05 01
  8b 0d e4 aa 05 01 66 8b 35 e2 aa`이다. 전체 파일의 direct `E8` xref는
  `0x004233AE: e8 6d 90 08 00` 하나이며, caller는 `[0x0066976C]==1` 조건 뒤 dequeue를
  호출하고 반환 직후 `0x004233B3→0x00493550`을 무조건 호출한다.
- dequeue 내부는 count `[0x0105AAFE]`/head 3-WORD record `[0x0105AAE0]`를 읽고,
  count>1이면 6-byte stride로 후속 slot을 앞쪽으로 shift한 뒤 count를 1 감소시킨다.
  count>0 뒤 mode `[0x004ED818] != 3`이면 call block으로 진행한다. mode가 3이면 두
  field가 zero인 경우에도 call block으로 진행하며, 두 field가 nonzero일 때만 두 좌표와
  기준점의 거리를 검사한다. 이때 어느 한 거리라도 `0x11` 초과이면 return block으로
  skip하고, 둘 다 `0x11` 이하이면 `0x004AC4DA: e8 f1 e3 ff ff`로 `0x004AA8D0`을
  호출한다. 함수 내부 direct call은 이 1개뿐이며, 직접 관측된 write는 ring shift와
  `[0x0105AAFE]` count 갱신이다.
- `0x004AA8D0`의 old bytes(raw `0xAA8D0`, 32B)는
  `83 ec 08 53 55 8b e9 33 db 8b 0d 74 39 b9 00 3b cb 75 0a 5d 33 c0 5b 83 c4 08 c2 08 00
  66 8b 45`이며, 이 후보 경로의 direct downstream calls는
  `0x0046EE10/0x0046EE60/0x0046EE90/0x0046EDB0/0x0046EF80`이다. 이 direct chain에서
  production callback, worker queue, unit spawn, primary command sender로 식별되는 직접
  edge는 확인되지 않았다. `0x004AA8D0` 자체의 의미도 이 정적 probe만으로 승격하지 않는다.
- 판정: 두 원본의 direct caller/old bytes/function downstream enumeration은 **STATIC PASS**;
  3-WORD record가 production 동작인지, 실제 입력·runtime과 연결되는지는 **UNKNOWN /
  CONCRETE BLOCKER**다. 구현·game run·fixture·좌표 변경의 근거로 사용할 수 없다.

#### lap91 Sol 독립 검수 — xref PASS, guard 의미 REVISE

- 두 고정 원본의 SHA/cmp/PE mapping, `0x004233AE` 유일 caller, ring shift/count 감소,
  `0x004AC4DA→0x004AA8D0` 및 helper 5개는 독립 재추출과 일치한다.
- lap90의 mode/좌표 guard 의미는 반대다. `0x004AC48E jne`, `0x004AC493 je`,
  `0x004AC498 je`는 모두 call block `0x004AC4C4`로 향한다. call을 건너뛰는 branch는
  mode=3이고 두 field가 nonzero일 때 거리 비교가 `0x11`을 초과하여
  `0x004AC4AD/0x004AC4C2 jg 0x004AC4DF`로 향하는 경우뿐이다.
- 따라서 caller/downstream enumeration은 STATIC PASS지만 lap90의 “mode=3/nonzero/
  거리<=0x11일 때만 call” 해석은 **MIDDLE REVISE**다. production 의미는 계속 UNKNOWN이며,
  다음 work-tier가 최소 read-only binary contract test로 branch truth table을 고정하기 전
  구현·game run·fixture·좌표 변경을 금지한다.

#### lap92 contract / lap93 middle 독립 검수 — binary contract CONFIRM, production meaning blocked

- lap92의 read-only 계약은 고정 SHA를 거부 조건으로 삼고 `0x004AC47F..0x004AC4DF`
  97-byte old bytes, `0x004AC48E/493/498→0x004AC4C4`, `0x004AC4AD/4C2→0x004AC4DF`,
  `0x004AC4DA→0x004AA8D0`과 `0x004233AE` 유일 caller를 검사한다.
- lap93 middle은 두 원본 SHA/cmp, PE32 `.text` 매핑, guard 97B, 분기/call target,
  callee entry를 `sha256sum`/`cmp`/`file`/`objdump`/`xxd`로 독립 재추출했다.
  count<=0 skip; mode!=3 또는 두 field 중 하나가 zero이면 call; mode=3·두 field nonzero에서
  어느 거리든 `>0x11`이면 skip, 둘 다 `<=0x11`이면 call이 맞다. **MIDDLE CONFIRM PASS**.
- 이 계약은 branch 기계 경로만 고정한다. generic ring producer→consumer field 매핑,
  primary worker/production direct edge, 실제 입력/runtime·G1은 **UNKNOWN / CONCRETE BLOCKER**이므로
  구현·game run·fixture·좌표 변경의 근거가 아니다.

#### lap94 Luna generic ring producer/consumer boundary probe — chain conflict, implementation blocked

- 고정 원본 `Syw2plus/syw2plus_original.exe`와 private copy
  `local/runtime/20260911_082430_2926029_0/game/syw2plus_original.exe`는 각각 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이고 `cmp`가 일치한다.
  PE32 i386 `.text`는 VA `0x00401000`, raw `0x1000`, size `0xE3AE5`이며 file offset은
  `VA-0x00400000`이다. 후보 바이너리·게임 실행·fixture·좌표는 변경하지 않았다.
- `0x0040FB50` raw `0xFB50` old bytes는
  `0f bf 4c 24 04 8b 44 24 08 50 8d 04 49 c1 e0 04 2b c1 8d 0c 80 8d 0c cd 90 b7 66 00
  e8 0f 5d 00 00 c2 08 00`이다. 전체 direct `E8` xref는 `0x0041EC9A` 하나이고,
  함수 내부 direct call은 `0x0040FB6C→0x00415880` 하나다. `0x0040FB50`에서
  `0x004AC3E0`으로 가는 direct edge는 없다.
- `0x004AC3E0` raw `0xAC3E0`의 old bytes는 64B이며 count
  `[0x0105AAFE]`를 검사·증가하고 slot base `0x0105AAE0 + index*6`을 만든다.
  `[esp+0xC]`, `[esp+0x8]`, `[esp+0x8]`(push 후 재참조)를 `0x004AC415`에서
  `0x004AA820`으로 넘기는 direct call은 하나이며, 전체 direct caller는 134개다.
- `0x004AA820` raw `0xAA820` old bytes는 `66 8b 44 24 04 66 8b 54 24 08 66 89 01
  66 8b 44 24 0c 66 89 51 02 66 89 41 04 c2 0c 00`이고, 세 WORD를 각각
  `arg1→[ecx+0x0]`, `arg2→[ecx+0x2]`, `arg3→[ecx+0x4]`에 기록한다. writer의 유일 caller는
  `0x004AC415`다. 이는 byte/argument order의 기계 계약이지 arg 의미나 production 성공이 아니다.
- `0x004AC420→0x004AA8D0` dequeue 계약은 lap92/93과 동일하다. 따라서 STATUS가 지정한
  `0x0040FB50→0x004AC3E0→0x004AA820`는 직접 producer chain으로 고정할 수 없고,
  `0x004AC3E0`의 134개 caller 중 어떤 호출이 목표 production producer인지도 이 probe로는
  판정할 수 없다. 정적 boundary test는 PASS, STATUS chain은 **REVISE / ESCALATE**,
  production field 의미·worker direct edge·실제 입력/runtime·G1은 **UNKNOWN / BLOCKED**다.

#### lap95 Sol middle 독립 검수 — contract CONFIRM, exact caller-block probe 지정

- 두 고정 원본의 SHA/cmp, PE32 `.text` 매핑과 세 함수 old bytes를 재확인했다.
  objdump의 instruction-decoded direct call 수는 `0x0040FB50` 1개(`0x0041EC9A`),
  `0x004AC3E0` 134개, `0x004AA820` 1개(`0x004AC415`)로 raw contract과 일치한다.
  `0x0040FB50`의 유일 내부 call은 `0x0040FB6C→0x00415880`이므로 enqueue direct edge는
  없다. lap94의 기계 계약은 **MIDDLE CONFIRM PASS**, direct-chain 해석은 **REVISE**다.
- 그러나 `0x0041EC3D..0x0041ED0C` 같은 code `0x04` dispatch block에서
  `0x0041EC9A→0x0040FB50` 호출·반환값 검사 뒤 `0x0041ED07→0x004AC3E0`이 나타난다.
  따라서 134개를 다시 광범위 열거하지 말고, 다음 work-tier는 이 단일 block의
  branch reachability와 `0x0041ECD2/DE/EA` helper 반환값에서 온 세 stack argument만
  old bytes 계약으로 고정한다. production/worker 의미는 계속 **UNKNOWN / BLOCKED**다.

#### lap96 Luna `0x0041EC3D..0x0041ED0C` dispatch-block contract — static PASS, production 의미 BLOCKED

- 고정 원본 `Syw2plus/syw2plus_original.exe`와 private copy
  `local/runtime/20260911_082430_2926029_0/game/syw2plus_original.exe`는 각각 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이고 `cmp`가 일치한다.
  PE32 i386 `.text`는 VA/raw `0x00401000/0x1000`, size `0xE3AE5`이며 file offset은
  `VA-0x00400000`이다. 후보 바이너리·게임 실행·fixture·좌표는 변경하지 않았다.
- `0x0041EC3D..0x0041ED0B`의 207-byte old-byte window를
  `tools/check_binary_contract.py:DISPATCH_BYTES`로 고정했다. 지정 branch target은
  `0x0041EC41→0x0041ED23`, `0x0041EC4E→0x0041EC5D`, `0x0041EC57→0x0041EE9B`,
  `0x0041EC88→0x0041ED14`, `0x0041ECA2/0x0041ECA6/0x0041ECCA→0x0041ED14`다.
- block의 direct call은 `0x0041EC7D→0x00416FD0`, `0x0041EC9A→0x0040FB50`,
  `0x0041ECAE→0x0040F5A0`, `0x0041ECD2→0x0040F5E0`,
  `0x0041ECDE→0x0040F5C0`, `0x0041ECEA→0x0040F5A0`,
  `0x0041ED07→0x004AC3E0`으로 고정했다. 세 helper는 모두 `ret 0x4` old bytes로 확인했다.
- `0x0041ED07`은 CX==4, `0x00416FD0` 반환==1, `0x0040FB50` 반환==1, EBP==0,
  첫 `0x0040F5A0(ESI)`-derived table WORD가 nonzero인 경로에서 reachable하다.
  enqueue 호출 시 stack provenance는 `[esp+0x4] = WORD[0x009B529A + 4*(109*sign_extend(WORD return of final 0x0040F5A0(ESI)))]`,
  `[esp+0x8] = WORD return of 0x0040F5C0(ESI)`, `[esp+0xC] = WORD return of
  0x0040F5E0(ESI)`다. 이는 인자/분기 기계 계약이지 field/action 의미가 아니다.
- 새 read-only contract/test는 SHA 불일치·window/call/branch/helper drift를 거부한다.
  targeted **11 passed**. static dispatch/reachability/provenance는 **PASS**지만
  production worker/unit/primary command 의미, 실제 입력/runtime 및 G1은 **UNKNOWN / BLOCKED**다.
  다음 새 Sol/Opus5 middle 독립 검수 전 구현·game run·fixture·좌표 변경은 금지한다.

#### lap98 Luna `0x0041EC3D` CX/ESI upstream provenance probe — mechanical PASS, production edge BLOCKED

- 입력은 고정 원본 `Syw2plus/syw2plus_original.exe`와 private copy
  `local/runtime/20260911_082430_2926029_0/game/syw2plus_original.exe`다. 두 SHA는
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp` PASS,
  PE32 i386 `.text` VA/raw `0x00401000/0x1000`, file offset는 `VA-0x00400000`이다.
- `0x0041EC3D` 진입 직전 CX의 가장 가까운 지배 정의는
  `0x0041EBF6: 66 8b 0d fe 2f 89 00` 즉 `CX=WORD [0x00892FFE]`다. ESI는 같은 루프에서
  `0x0041EC61: a1 c8 24 89 00`으로 읽은 `DWORD [0x008924C8] + EDI`를 `0x14`로 나눈
  나머지 EDX를 사용해 `0x0041EC71: 66 8b 34 95 28 90 89 00`, 즉
  `WORD [0x00899028 + 4*EDX]`로 갱신된다. 직전 `0x0041EB84: ESI=1` 때문에 이
  `mov si` 뒤 ESI 상위 16비트는 0이며, 이는 **값의 기계적 provenance**이지 unit/action 라벨이 아니다.
- CX state의 static upstream은 `0x0041CEE0` mapping helper다. 이 함수는
  `DWORD [0x009E1DCC]` bit-state를 읽어 `0x00892FFE`에 0x3/0x4/0x20/0x25/0x4A/0x9 등의
  code를 기록한다. direct caller는 `0x0041DCFA/0x0041E64E/0x0041E6FE` 세 곳이다.
  그 bit-state updater `0x00437E90`의 direct caller는 `0x0041E635` 하나이며, reset/write와
  branch는 확인됐지만 이 값이 code `0x04`의 생산/입력 의미라는 직접 label은 없다.
- ESI table `0x00899028`은 20개 4-byte slot이다. add writer는
  `0x00412E61: 89 14 8d 28 90 89 00`에서 object `[EBP+0x29C]`의 DWORD를 기록하고,
  clear writer는 `0x00412EBC: 66 89 3c 8d 28 90 89 00`에서 slot WORD pair를 지운다.
  두 writer가 속한 helper `0x00412D90`의 direct caller는 11개
  (`0x00407192/0x00409C8E/0x00409FB9/0x0040F7F1/0x00412A1E/0x004170B5/
  0x0044302D/0x00476EDC/0x0047B5B9/0x0048E209/0x0048E7E0`)로, 특정 primary sender 하나로
  수렴하지 않는다. table 초기화 `0x00499040/0x0049906E`도 별도다.
- 따라서 `0x00437E90→0x009E1DCC→0x0041CEE0→0x00892FFE` state chain과
  `0x00412D90→0x00899028→0x0041EC71` record chain은 각각 기계적으로 고정됐지만,
  `input→active-record writer`, `state mapper→0x0041ED07/0x004AC3E0`, 또는
  worker/unit/primary production sender direct edge는 **증명되지 않았다**. lap98은
  `tools/check_binary_contract.py`/`tests/test_binary_contract.py`에 SHA-gated upstream
  old-byte/xref contract를 추가했고 targeted **12 passed**다. 실제 게임·fixture·좌표·후보
  실행은 하지 않았다. 이 정확한 단절은 Sol/Opus5 독립 검수 전 구현 근거가 될 수 없다.

#### lap99 Sol middle 독립 검수 — upstream contract CONFIRM, production meaning BLOCKED

- 두 고정 원본의 SHA/cmp/PE를 다시 확인하고 contract 출력과 분리한 `xxd`/`objdump`로
  `0x0041EBF6/0x0041EC61/0x0041EC71`, `0x00412E61/0x00412EBC`, mapper/updater 진입
  old bytes를 재추출했다. 두 원본의 7개 window가 모두 lap98과 일치했다.
- instruction-decoded direct caller는 mapper `0x0041CEE0` 3개, updater `0x00437E90` 1개,
  active-record helper `0x00412D90` 11개, enqueue `0x004AC3E0` 134개로 일치했다.
  mapper 내부에는 direct call이 없으며 active helper는 특정 sender 하나로 수렴하지 않는다.
- 따라서 lap98 기계 계약은 **MIDDLE CONFIRM PASS**이나, shared state/table을 production
  input/worker/action으로 라벨하는 직접 근거는 없다. 구현·runtime·G1은 **UNKNOWN/BLOCKED**다.

#### lap100 Luna `0x0041E635` 상위 CFG / 전역 writer probe — mechanical PASS, production edge BLOCKED

- 고정 원본 `Syw2plus/syw2plus_original.exe`와 `/home/dev_00/sharedfolder/260320_Syw2plus/
  syw2plus_original.exe`는 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  `cmp` PASS, PE32 i386 `.text` VA/raw `0x00401000/0x1000`, size `0xE3AE5`다. 원본과
  참고 저장소, 후보 EXE, 게임, fixture, 좌표는 변경하지 않았다.
- `0x0041E635`의 old bytes `e8 56 98 01 00`는 `0x00437E90`의 유일 direct caller다.
  호출 전 gate는 `0x0041E624 jne 0x0041E63D`; 별도 mapper 호출은
  `0x0041E64E/0x0041E6FE`이며, `0x0041E77B→0x0041EB7F` 및
  `0x0041EB8B/0x0041EB9C/0x0041EBA5/0x0041EBAD` 조건을 거쳐
  `0x0041EBF6`의 `WORD [0x00892FFE]` load에 도달한다. 해당 branch opcode/target은
  `tools/check_binary_contract.py:UPSTREAM_BRANCHES`로 고정했다.
- `0x00437E90`은 시작 시 `0x00437EA5`에서 `DWORD [0x009E1DCC]=0`으로 초기화하고,
  검증된 updater 내부 writer `0x00437F92/0x00438106/0x00438179/0x004382ED/
  0x00438315/0x0043836A/0x0043847B/0x00438498`를 가진다. 전체 direct writer는
  기존 `0x0041E392`를 포함해 10개다. `0x0041CEFC`가 이 mask를 읽고,
  `0x0041CEE0`가 `0x00892FFE`에 state code를 기록한다.
- `0x00892FFE`의 전체 direct writer는 18개로 확인됐다
  (`0x00412EE7`, mapper의 `0x0041CF16/39/5F/85/AB/D1/F7`,
  `0x0041EA14/0x0041EBC0/0x0041F0AC`, `0x004997D6/0x00499A61/0x00499B0A/
  0x00499C22/0x00499CF2/0x00499D82/0x00499E75`). 각 writer old bytes는
  `DATA_WRITER_BYTES`로 SHA-gated 검사한다.
- 따라서 `0x0041E635→0x00437E90→0x009E1DCC→0x0041CEE0→0x00892FFE→0x0041EBF6`는
  정적 data/branch chain으로는 고정됐다. 그러나 updater 입력의 production/action 의미,
  `0x0041ED07` enqueue와의 direct edge, worker/unit/primary sender 연결은 증명되지 않았다.
  판정은 **STATIC CONTRACT PASS**, production 의미와 G1은 **UNKNOWN / BLOCKED**로 유지한다.

#### lap101 middle lap100 독립 검수 — MIDDLE CONFIRM PASS, production edge BLOCKED

- 두 고정 원본의 SHA/cmp, PE32 i386 `.text` VA/raw/size를 다시 확인했고
  raw-byte 단일 디코드로 branch 10개의 opcode/target과 writer `10/18`의 old bytes가
  두 원본에서 모두 같음을 재현했다.
- `objdump -D -Mintel`의 instruction boundary로 updater `0x00437E90` caller 1개,
  mapper `0x0041CEE0` caller 3개, enqueue `0x004AC3E0` caller 134개와 writer 주소
  `10/18`을 독립 대조했다. mapper `0x0041CEE0..0x0041D010` 본체에는 call 및
  `0x0041ED07`/`0x004AC3E0` direct transfer가 없다.
- 첫 Capstone full-linear probe는 `.text` 중간의 비명령 byte에서 디코드가 멈춰
  `0x0041E624` instruction map을 만들지 못했으며, 이 FAIL 결과는 폐기하고
  주소별 raw decode/`objdump`로 교체했다.
- lap100의 machine contract는 **MIDDLE CONFIRM PASS**지만 production action 의미와
  updater/state mapper→`0x0041ED07` enqueue direct edge는 증명되지 않았다. 다음 work-tier는
  `0x00669C24` bit-state 또는 `0x00637734/0x00637736` 좌표의 한 경로를 OS input/message
  handler까지 추적해 production 기원을 증명하거나 정확한 단절을 남겨야 한다.

#### lap102 Luna coordinate input provenance probe — static OS-input path PASS, gameplay meaning BLOCKED

- 입력은 `Syw2plus/syw2plus_original.exe`와 `/home/dev_00/sharedfolder/260320_Syw2plus/
  syw2plus_original.exe`다. 두 파일 SHA는
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp`는 PASS이며,
  원본은 PE32 i386이다. 원본·참고 EXE·후보·게임·fixture·좌표는 변경하지 않았다.
- `0x00423C34`의 old bytes는 WndProc `0x00423DC0`를 등록 구조체에 기록하고,
  `0x00423C8B`의 `RegisterClassA` IAT call 및 main loop `0x004232FC`의 `DispatchMessageA`
  IAT call을 고정했다. 이는 OS message handler까지의 정적 연결이다.
- WM_MOUSEMOVE handler `0x0042434B`는 `lParam` low/high를
  `0x00C0CB58/0x00C0CB5C`에 저장하고, `0x0042436F→0x004216B0` event-ring writer로
  전달한다. game tick의 `0x0041E299→0x004217B0` reader와 caller chain
  `0x00423FE8→0x0041C740→0x0041E220`도 old bytes/direct target으로 고정했다.
- 변환 경로 `0x0041E45F→0x004516A0` 뒤 `0x0041E4AF/0x0041E4B6`가
  `0x00637734/0x00637736`을 쓰고, `0x0041E626/0x0041E62C`가 이를 읽어
  `0x0041E635→0x00437E90`으로 넘긴다. 이 연결은 `tools/check_binary_contract.py`의
  `INPUT_PROVENANCE_BYTES`/`INPUT_PROVENANCE_CALLS`로 SHA-gated 검사한다.
- targeted binary contract는 **13 passed**, `make check`는 **140 passed**다. 이 결과는
  OS input origin의 기계적 provenance일 뿐 gameplay action/field 의미, 1600×1200 출력,
  실제 입력·runtime·G1 PASS를 증명하지 않는다. 다음 Sol/Opus5/high middle이 두 원본에서
  contract와 OS/input chain을 독립 검수해야 하며, 그 전에는 구현·game run·fixture·좌표 변경을 금지한다.
