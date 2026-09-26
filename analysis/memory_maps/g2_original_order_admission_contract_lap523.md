# G2 S0 — 원본 target-order `FUN_00415480` 호출 규약·수락 술어 (lap523, 읽기 전용)

- 조사: lap523 middle (Claude Code `claude-opus-5-5` / high), 2026-09-23 KST. 게임 실행 0, 쓰기 0.
- 원본 `Syw2plus/syw2plus_original.exe` SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  `objdump -Mintel -D -b pei-i386`로 원본 바이트를 직접 읽었다. file offset = VA − `0x400000`.
- 후보 대조: 현재 source의 `g2_full_capacity_persistence_compat_v1.build_candidate(orig, 4001)`로 메모리 안에서
  다시 빌드했다. SHA `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(W26 핀과 일치, 파일 기록 없음).

## 1. 호출 규약 (원본 바이트에서 다시 유도)

`0x415480`: `53 56 8B F1 57 8A 86 1C 03 00 00 84` (`push ebx; push esi; mov esi,ecx; push edi; mov al,[esi+0x31c]; test`).
- `ECX` = 소스 Unit 레코드 포인터(`esi`). 모든 반환은 `ret 0x0C`이므로 **thiscall, stack DWORD 3개**다.
- push 3개 뒤라 `[esp+0x10]`=arg1, `[esp+0x14]`=arg2, `[esp+0x18]`=arg3.
  - arg3(`edi`) = 목표 id. `movsx eax,di`로 **하위 16비트를 슬롯 번호로 써서** `0x416FD0`에 넘긴다.
  - arg1·arg2는 검사 없이 `0x4AEE10(src_uid, arg1, arg2, target_id, 1)`로 넘어간다. 기존 G4 호출은 목표의 `+0x2A2`(x)·`+0x2A4`(y)를 넣었다.
- 반환 `EAX`: 수락 경로 1(`mov eax,ebx`, ebx=1), 거부 경로 0(`0x41562F`).
- 기존 typedef `int (thiscall*)(void *unit, DWORD x, DWORD y, DWORD target_id)`(`tools/inmm_stub/control_executor.c:2277`)와 일치한다.

## 2. 수락 술어 (거부하면 반환 0)

| 순서 | 위치 | 조건 |
|---|---|---|
| P1 | `0x415485` | 소스 `+0x31C` byte ≠ 0 |
| P2 | `0x41549B → 0x416FD0(slot16)` | 목표 존재배열 ≠ 0, 목표 `+0xB4`(HP) > 0, 목표 `+0x31C` ≠ 0 |
| P3 | `0x4154B4 → 0x417890(target16, src_uid16)` | 두 슬롯 존재. `0x4177A0(owner_t, owner_s)`가 **1이 아니어야** 통과 |
| P3a | `0x4177A0` | owner 둘 다 0..7이면 `PlayerStruct[o].+0x05` byte가 같을 때 1을 반환(= 같은 편) |
| P4 | `0x4154C9` | 소스 `+0x634`==1이면 `0x415640(target, +0x20C)`도 통과해야 한다(내부 미해독) |
| P5 | `0x4154EA` | 소스 명령 `+0x290`==1(idle): `0x415880(target)`==1 필요. 그다음 `+0x390`==1이면 `0x415940` 경유 |
| P5' | `0x41553C` | `+0x290`==4: `PlayerStruct[src_owner].+0x02`==1 또는 소스 `+0x294`==1, 그리고 `0x415880`·`0x415980`==1 |
| P5'' | `0x4155B4` | `+0x290`==3(`+0x294`==1 필요) 또는 0x23. **그 밖의 명령 값은 거부** |
| P6 | `0x415880` | 소스 `+0x31C`≠0, 목표 P2 재확인, 목표≠자기, 소스 `+0x1D8` bit `0x4`=0이면 목표 `+0x1BC`≠1, bit `0x400`=0이면 목표 `+0x1BC`≠2, 소스 `+0x1D4`≠1 |

**⇒ N177: 명령 수락의 적대 판정은 `PlayerStruct+0x05` byte(편 번호) 비교 하나다.**
8 owner가 서로 명령을 걸 수 있으려면 8개 byte(`0x956775 + o×0x3ABC`)가 쌍마다 달라야 한다.
이 byte가 N87 자동 교전에도 쓰이는지는 **확인하지 않았다**(자동 교전 경로는 미해독).

## 3. 재배치 후보(N=4001)에서의 참조 상태

| 명령 주소 | 역할 | 원본 | 후보 `a10024de…` |
|---|---|---|---|
| `0x416FD8` / `0x417899` / `0x4178AC` | 존재배열 | `0x008990C8` | `0x017B8658` |
| `0x416FF2` | 목표 HP `+0xB4` | `0x0066B844` | `0x0108C0B4` |
| `0x416FFF` | 목표 `+0x31C` | `0x0066BAAC` | `0x0108C31C` |
| `0x4178C5` / `0x4178D9` | owner `+0x8E` | `0x0066B81E` | `0x0108C08E` |
| `0x4158F6` / `0x415918` | 목표 `+0x1BC` | `0x0066B94C` | `0x0108C1BC` |
| `0x4177EC` / `0x4177F7` / `0x415563` | PlayerStruct `+5`/`+2` | `0x956775`/`0x956772` | 불변 |

수락 경로 안의 풀 참조 10건은 전부 재배치 풀 기준(`0x0108C000`)으로 fixup돼 있다. PlayerStruct는 재배치 대상이 아니다.
하위 경로 `0x4AEE10 → 0x4AED20 → 0x40FF90 → 0x412540 → 0x40C640`와 이동·공격 루틴은 이번에 대조하지 않았다.
이 부분은 S0 실행이 직접 드러낸다(lap414 `0x414133` fault 계열 재발 여부 포함).

## 4. 주의

- 목표 id는 하위 16비트가 슬롯 번호일 때만 맞는 슬롯을 가리킨다. G4 실측 `0x000D0498`의 하위값 `0x498`=1176=slot이었다.
  N=4001 후보의 slot≥1200 유닛에서도 이 관계가 성립하는지는 **미실측**이다(N178). 호출 전에 fail-closed로 확인한다.
- `tools/inmm_stub/control_executor.c`의 G4 op는 stock 풀(`0x0066B790`/`0x008990C8`/1200)을 하드코딩한다.
  재배치 후보에서는 유닛을 0기로 본다(INBOX lap410 정정2). **S0는 그 op를 재사용할 수 없다**(N179).
