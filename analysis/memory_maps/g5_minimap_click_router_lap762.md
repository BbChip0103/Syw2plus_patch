# 미니맵 클릭 라우팅 체인 (lap762, 정적 + 실측)

원본 `[HQ]Syw2plus 2002.exe`(SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`)
기준. lap759가 확정한 미니맵 위젯 생성자(`this=0x00639350`, X/Y=(0,509), 새 게임 시작 시 1회
초기화)를 출발점으로, 2026-09-29 12:37 운영자 지시("마우스 좌표→미니맵 영역 판정→월드 좌표
변환→이동/카메라" 함수를 브레이크포인트로 찾아라)에 따라 objdump 전수 xref로 실제 클릭 라우팅
체인을 특정했다.

## 체인 개요

```
WM_LBUTTONDOWN/UP, WM_RBUTTONDOWN/UP 핸들러 (0x424204~0x424460 부근, WndProc)
  -> FUN_004216B0 (마우스 이벤트 링버퍼 enqueue, this 없음, ds:0x61da20[count*0x10])
       가드: ds:0x8924b8>=0xA, ds:0xb93984/0xb93982 두 워드 플래그==0, 큐 깊이(ds:0x61e270)<0x64

매 틱 클릭 라우터 (0x41e269~0x41e60c)
  -> FUN_004217B0 (같은 링버퍼 dequeue, 호출 0x0041E299)
  -> (dequeue 성공 시) 버튼종류/최근좌표 여러 단계 필터(0x41e2a1~0x41e3a5, 0x41e332 등)
  -> call 0x41c450(게이트, "test eax,eax;je 스킵") 통과 시에만
  -> **FUN_004516A0(this=0x00639350 위젯, mouse_x, mouse_y, &out_tile_x, &out_tile_y)**
       = 미니맵 위젯 자체의 히트테스트/좌표변환 메서드
     실패(0) 시에만 폴백: FUN_00417DB0(메인 뷰포트 히트테스트, tools/g5_screen_world_calibration.py가
     이미 특성화한 그 함수)
```

## FUN_004516A0 (미니맵 히트테스트, 신규 특정)

```
4516a0: push ebx
4516a1: mov ebx,[ecx]            ; widget.x  (this+0x0)
4516a5: movsx esi,[esp+0x10]     ; arg1 mouse_x
4516aa: cmp esi,ebx ; jl fail    ; mouse_x < widget.x -> fail
4516ae: lea eax,[ebx+0xb4]       ; widget.x + 180
4516b4: cmp esi,eax ; jg fail    ; mouse_x > widget.x+180 -> fail
4516b8: movsx edx,[esp+0x14]     ; arg2 mouse_y
4516bd: mov edi,[ecx+4]          ; widget.y (this+0x4)
4516c0: cmp edx,edi ; jle fail   ; mouse_y <= widget.y -> fail
4516c4: lea eax,[edi+0x5a]       ; widget.y + 90
4516c7: cmp edx,eax ; jge fail   ; mouse_y >= widget.y+90 -> fail
  ; in bounds: dy=mouse_y-widget.y (1..89); index=dy*180-widget.x+mouse_x
4516e0: movzx ax,[ecx+index*2+0x13eea]   ; out_tile_x_delta byte
451700: movzx ax,[ecx+index*2+0x13eeb]   ; out_tile_y_delta byte (같은 인덱스, +1 byte)
451710: cmp WORD[out_x_ptr],0xff ; je fail
451717: cmp ax,0xff ; je fail
451725: return eax=1 (성공)
451728: xor eax,eax; return eax=0 (실패)
```

실측(lap762, 원본 실행 중 위젯 X/Y 직접 읽기): `x=0, y=509` — lap759 정적/실측과 일치.
즉 이 세션의 위젯 판정 범위는 **화면 x∈[0,180], y∈(509,599]** — lap710이 이미 클릭-테스트한
"다이아몬드" HUD 영역(x∈[0,176], y∈[511,598], 9개 지점)과 거의 완전히 겹친다. **lap710의 관측
("9개 지점 전부 pending_xy 무변화")은 이 바운딩박스 판정 자체가 실패해서가 아니라, 그 안쪽의
LUT 조회가 실패(sentinel)했거나 라우터가 이 함수 자체에 도달하지 못했기 때문일 수 있다** — 이번
lap이 실측으로 후자로 확정했다(아래).

## LUT 베이킹 (신규 발견: 위젯 생성자가 아니라 그 안의 후속 루프가 실제 지형을 굽는다)

`FUN_00451130`(위젯 생성자, lap759가 1회 호출 확정) 디스어셈블:

```
451172: xor eax,eax; rep stos [esi+0xa], count 0x1015 dword   ; 일반 필드 0-clear
45117c: or eax,0xffffffff
451184: lea edi,[esi+0x13eea]; rep stos, count 0x1fa4 dword   ; LUT-A 전체를 0xFF로 채움 (sentinel)
45118c: or eax,0xffffffff
451194: lea edi,[esi+0x1bd7a]; rep stos, count 0x3f48 dword   ; LUT-B도 0xFF
4511a4: lea edi,[esi+0x4061];  rep stos, count 0x3f48 dword   ; LUT-C도 0xFF
...
4511ff: mov eax,[esi+0x2baa0]; cmp eax,edi; jle 0x45135f       ; 맵 타일 수 <=0 이면 베이킹 루프 스킵
451213~4512e6: 루프 본문 — 각 타일의 화면 투영(call 0x4514e0)을 계산해
  [esi+ebp*2+0x1bd7a]/[+0x1bd7b] (LUT-B) 와
  [esi+ecx*2+0x13eea]/[+0x13eeb] (LUT-A) 에 실제 (0xFF가 아닌) 델타 바이트를 쓴다.
```

**실측(lap762, 원본 실행 중 LUT-A 0x13eea~+0x7e90 전체 32400바이트 직접 읽기): 정확히 16200/32400
바이트(50%)가 0xFF가 아니다.** 즉 이 베이킹 루프는 이 환경에서 **실제로 실행되며 실제 맵 데이터로
LUT-A를 채운다** — "미니맵 렌더 서브시스템 자체가 완전히 죽어있다"는 이전 가설(lap677/710/758/760의
누적 negative 증거)을 이 좁은 지점(좌표 LUT)에서는 반증한다. 첫 비-FF 바이트는 offset 178(픽셀
인덱스 89, row_dy=1, col_dx=89, 화면좌표 (89,510) 추정)이다.

## 실측(gdb 진입 트레이스, lap762, 2회 격리 실행)

`tools/g5_minimap_hittest_entry_trace.py` + `tools/g5_minimap_click_hittest_probe.py`로 non-invasive
entry-count breakpoint를 새 게임 진입 직후 arm하고, lap710 다이아몬드 5지점(button=3) + 기존
`MINIMAP_CLICK`/`MINIMAP_CENTER` + LUT에서 찾은 비-FF 픽셀 좌표(89,510)까지 총 8개 지점을
우클릭했다.

| 후보 | 주소 | run1 hit | run2 hit |
|---|---|---|---|
| `FUN_004216B0` (WM 핸들러의 링버퍼 enqueue) | 0x004216B0 | (미계측) | **24** |
| 라우터의 dequeue 호출 (매 틱) | 0x0041E299 | (미계측) | **19086** |
| `FUN_004516A0` (미니맵 히트테스트 진입) | 0x004516A0 | **0** | **0** |
| 히트테스트 성공 리턴 | 0x0045171D | 0 | 0 |
| 히트테스트 실패 리턴 | 0x00451728 | 0 | 0 |

**결론: 입력은 저수준 WM 핸들러(enqueue 24회, 클릭 8회×다운/업 등에 부합)까지는 확실히 도달하고,
라우터도 매 틱 dequeue를 시도하지만(19086회), `FUN_004516A0`(미니맵 위젯 히트테스트)는 단 한 번도
호출되지 않았다.** 즉 병목은 "미니맵 렌더/좌표계산이 죽어있다"가 아니라 — LUT은 절반이 실제로
베이킹되어 있으므로 — **라우터의 enqueue↔dequeue 사이, 또는 dequeue 성공 후 히트테스트 분기
(`0x41e332`의 버튼타입 바이트 검사, `0x41e3a5`의 좌표 sentinel 검사, `0x41e43d`의 `call 0x41c450`
게이트 등 다중 분기) 어딘가에서 이 세션의 클릭들이 전부 걸러지고 있다**는, 훨씬 좁고 코드 위치가
특정된 새 사실이다. 정확히 어느 분기가 매번 걸리는지는 이 lap의 범위를 넘는다(추가 브레이크포인트
2~4개, 또는 각 분기 조건 레지스터 실측 필요).

## 다음 probe 후보 (미착수, 다음 lap)

`0x41e332`(버튼타입==1 분기), `0x41e3a5`가 참조하는 `cmp si,bx`(0x41e365, "새 좌표가 sentinel인지"),
`0x41e43d`의 `call 0x41c450` 반환값에 개별 브레이크포인트/레지스터 캡처를 걸어 세 갈래 중 실제로
클릭을 떨어뜨리는 지점을 좁힌다. 그 지점이 확정되면 원본에서 그 조건을 만족시키는 실제 조작(다른
버튼조합, 다른 좌표, 다른 게임 상태)을 찾아 재시도할 근거가 생긴다.

전문(probe-result.json, gdb 이벤트 로그, 캡처)은
`docs/history/laps/20260929_lap762_work_g5_minimap_click_router_hittest_blocked_upstream.md` 참고.
