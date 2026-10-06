# 미니맵 클릭 라우터 게이트 체인 (lap763, 정적 + 강제-플래그 실측)

원본 `[HQ]Syw2plus 2002.exe`(SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`)
기준. lap762가 "라우터 필터 체인 3곳(`0x41e332`/`0x41e365`/`0x41e43d call 0x41c450`) 중 하나가
`FUN_004516A0`(미니맵 히트테스트) 호출을 막는다"까지 좁혔다. 2026-09-29 12:57 운영자 지시대로
이 3곳에 개별 브레이크포인트+레지스터 캡처를 걸어 정확한 분기를 확정했다.

## 결론 요약

**세 후보 중 실제로 게이트 역할을 하는 것은 `0x41e43d`의 `call 0x41c450` 하나뿐이다.**
`0x41e332`(버튼타입 검사)와 `0x41e365`(좌표 sentinel 검사)는 둘 다 라우터 내부의 **커서 아이콘
계산**(화면 가장자리 스크롤 방향 코드를 만들어 `call 0x437510`에 넘기는 로직) 갈래일 뿐이며, 두
갈래 모두 무조건 같은 다음 명령으로 수렴한다 — 즉 이 두 지점의 결과는 `FUN_004516A0` 호출 여부에
전혀 영향을 주지 않는다(정적 확인 + 실측 hit count로 이중 확인, 아래).

`call 0x41c450`(라우터가 그 반환값으로 `test eax,eax; je 0x41e4c1`을 하는 지점, 0=스킵)은
**이번 세션에서 관찰된 9430회 호출 전부(100%)가 0을 반환**했다 — `FUN_004516A0`가 lap762에서도
이번 lap 1차 실행에서도 0회 호출인 이유의 직접 원인이다.

**`0x41c450`이 왜 0을 반환하는지도 이번 lap이 실측으로 확정했다:** 그 함수는 세 조건의 OR이다
(모드 인덱스 테이블 워드==1, 또는 `0xb631ec`==1, 또는 `0x97597c`!=0). 실측 결과 셋 다 항상
`0`이었다. `0x97597c`의 유일한 두 setter(둘 다 새 게임 초기화 함수, `0x4a3060`의 호출자와 같은
코드 영역)는 `WORD PTR ds:0x975914 == 3`일 때만 `0x97597c=1`을 쓴다. `0x975914`는 새 게임
초기화 시 로비 설정 전역 `0x632d42`에서 그대로 복사된 값이고, `0x632d42`는 로비 다이얼로그
접근자(`call 0x4ced40`, `this=0x1065d10`)의 반환값이다 — 즉 **"게임 타입" 계열의 로비 UI 선택값이지,
렌더링/포커스/DirectDraw 상태가 아니다.**

**실측(강제 플래그 실행, 이번 lap):** `0x97597c`를 게임 진입 직후 진단 전용 write(격리 사본,
`patches/population/runtime_driver.write`, 기존 stale-tail fixture와 같은 범위)로 `1`을 직접
써넣자, 같은 세션 안에서 `FUN_004516A0`가 **6232회 호출**(성공 4195회, 실패 2037회)로 뛰었다 —
0회 → 수천 회. 이는 미니맵 렌더/좌표 서브시스템이 죽어있는 게 아니라 **이 게이트 플래그
하나가 잠가놓고 있었을 뿐**임을 직접 실증한다.

## 라우터 코드 (objdump, `0x41e260`~`0x41e4c1`)

```
0x41e299: call FUN_004217B0        ; dequeue(마우스 이벤트 링버퍼)
0x41e2a3: jne 0x41e354             ; 실패 시 마지막 좌표만 재사용
0x41e2a9..0x41e330: 버튼 코드별 분기(이동명령 좌표 기록/드래그 앵커 갱신) -> 전부 jmp 0x41e362로 수렴
0x41e332: cmp byte[esp+0x13],1     ; (조사 대상 ①) -- 오직 위 0x41e2d5 "jl 0x41e332" 분기로만 도달,
                                     실행돼도 jmp 0x41e362로 수렴. FUN_004516A0 호출과 무관.
0x41e354: (dequeue 실패) 마지막 좌표 재로드 -> 그대로 0x41e362로 흐름
0x41e362: (수렴점) edi=-1; 여러 전역 0-클리어
0x41e365: cmp si,bx                ; (조사 대상 ②) -- 두 갈래 다 같은 "커서 스크롤 영역 코드 계산 후
                                     call 0x437510"으로 수렴. FUN_004516A0 호출과 무관.
0x41e3a5..0x41e41d: 화면 가장자리 스크롤 커서 영역 코드 계산(0x2/0x7~0xe/0x12) -> call 0x437510
0x41e43d: call 0x41c450            ; (조사 대상 ③, 실제 게이트) 반환값 eax
0x41e442: test eax,eax; je 0x41e4c1  ; **0이면 FUN_004516A0을 아예 건너뛰고 폴백(0x417db0)으로 감**
0x41e45f..0x41e464: (eax!=0인 경우만) ecx=0x639350(위젯); call FUN_004516A0
0x41e469: cmp eax,ebp; jne 0x41e4c1  ; 히트테스트 실패 시에도 폴백 경로로 수렴
```

## `FUN_00 41C450` (게이트 함수) 디스어셈블

```
41c450: mov ecx,[0xb63fc4]                  ; mode_index (읽기 전용, 이 범위에서 writer 없음)
41c456..41c469: edx = mode_index*3759       ; 테이블 stride 계산
41c46b: cmp WORD PTR [edx*4+0x959af6],1     ; mode_index별 per-mode 테이블 워드 == 1 ?
41c473: je 0x41c48a (return eax=1)
41c475: cmp WORD PTR ds:0xb631ec,1          ; == 1 ? (이 주소, 이 코드범위에서 writer 전무 -- 상시 0 추정)
41c47c: je 0x41c48a (return eax=1)
41c47e: mov ecx,[0x97597c]
41c484: test ecx,ecx
41c486: jne 0x41c48a (return eax=1)
41c488: xor eax,eax                          ; 셋 다 거짓 -> return eax=0  (실측: 이번 세션 100%)
41c48a: ret
```

## `0x97597c`(게이트 플래그) setter 두 곳

둘 다 새 게임 초기화 함수 내부(호출자는 `0x41b9c0`/`0x41bc4f` — lap753/754 H-NEWGAME-INIT이 이미
분석한 `0x4a3060`의 호출자들과 같은 코드 영역, `ecx=0x892410`):

```
0x41b590 함수: ... call FUN_00451130(미니맵 위젯 ctor, lap759 확인) ...
  0x41b5a9: cmp WORD PTR ds:0x975914,3
  0x41b5b1: jne 0x41b611               ; != 3 이면 아래 esi=1 대입 블록을 건너뜀
  0x41b5c0: mov ds:0x97597c,esi(=1)    ; game_type==3 일 때만 게이트 플래그 set
0x41b8a3 (다른 새게임 초기화 갈래):
  cmp BYTE PTR [edx*4+0x956770],6      ; (플레이어 구조체의 다른 바이트 조건)
  jne 0x41b8b3
  0x41b8ad: mov ds:0x97597c,edi(=1)
```

## `0x975914`("game_type") 의 출처

```
0x41b9fd / 0x41bc91: mov ds:0x975914, ax     ; ax <- WORD PTR ds:0x632d42 (새 게임 시작 시 복사)
0x41f0e0: cmp WORD PTR ds:0x975914,3         ; 다른 곳(생산/AI 관련 함수)에서도 ==3 분기 있음
0x41f13f: cmp WORD PTR ds:0x975914,1
0x4a9bcf: cmp WORD PTR ds:0x975914,2
```

`0x632d42`는 로비 다이얼로그 접근자의 반환값(`0x4b76a2: mov ds:0x632d42,ax`, 직전
`call 0x4ced40` with `ecx=this=0x1065d10`, 인접한 `0x4cecc0..0x4ced40` 시리즈 호출들이 같은
로비 오브젝트에서 여러 필드를 순서대로 읽어 `0x632d44/46/48/4a/4c/54/42`에 채움) — **로비 UI에서
사용자가 고르는 게임 종류/모드 선택값**으로 읽힌다(정확한 라벨은 미확인 — 이 lap의 자동화 로비
클릭 시퀀스는 항상 "솔로" 셀렉터만 고르고 이 필드는 건드리지 않으며, 그 결과 `0x975914`가
`3`이 아닌 값(실측 0)으로 세팅된다).

## 실측 (gdb, 이번 lap, 2회 실행)

`tools/g5_minimap_hittest_entry_trace.py`(9-breakpoint, lap763에 4개 추가:
`router_button_type_filter_0x41e332`, `router_coord_sentinel_filter_0x41e365`,
`router_gate_entry_0x41c450`, `router_gate_return_check_0x41e442`) +
`tools/g5_minimap_click_hittest_probe.py`(신규 `--force-gate-flag` 옵션).

| 실행 | force_gate_flag | `0x41e442`의 eax (게이트 반환값) | `FUN_004516A0` 호출 수 | 성공/실패 리턴 |
|---|---|---|---|---|
| 1 (`20260929_lap763_minimap_router_filter`) | false | 관측 80건 전부 `0x0` | **0** | 0 / 0 |
| 2 (`20260929_lap763_minimap_gate_forced`) | true (`0x97597c`를 write로 1로 강제) | (강제 이후 자연 경로도 이미 `test`를 통과) | **6232** | 4195 / 2037 |

실행1의 `router_gate_entry_0x41c450`(라우터 호출부, `return_address==0x41e442`인 것만 필터)의
`gate_inputs`는 관측된 모든 이벤트에서 동일:
`{"flag_0x97597c": 0, "flag_0xb631ec": 0, "mode_index_0xb63fc4": 0, "mode_table_word": 0}`.

`router_button_type_filter_0x41e332`(8회)와 `router_coord_sentinel_filter_0x41e365`(9430회,
매 라우터 tick과 거의 일치)의 hit count는 정적으로 예측한 그대로였다 — 후자는 사실상 매 tick
도달하는 무해한 코드이고, 전자는 특정 버튼 분기로만 가는 무해한 분기라는 것을 실측으로도 확인.

강제 실행에서 `source_unchanged=true`, `alive_at_end=true`, `cleanup.ok=true`, 크래시 0.
`patches/population/runtime_driver.write()`로 이번 lap이 쓴 4바이트(`0x97597c=1`)는 격리된
스폰 자식 프로세스 안에서만 유효하고, 원본 EXE 파일은 두 실행 모두 SHA 불변으로 확인됐다.

## 남은 것 (다음 work)

1. **명령 효과 검증(operator 요청 핵심):** 이번 lap은 `FUN_004516A0`이 "도달 가능"함만 강제
   플래그로 실증했다 — 유닛을 선택한 상태로 미니맵을 우클릭했을 때 실제 이동 명령(`pending_xy`)이
   그 클릭이 가리키는 좌표로 나가는지는 아직 측정하지 않았다(이번 lap은 fixture 없이 진행). 다음
   lap은 fixture 유닛을 스폰·선택한 뒤 강제 플래그 + 실제 베이킹된(비-0xFF) 미니맵 픽셀 우클릭으로
   원본20/v10 50 paired 명령 효과를 측정해야 (2)를 완전히 닫을 수 있다.
2. `0x632d42`/로비 접근자 `0x4ced40`가 정확히 어떤 로비 UI 위젯(라디오버튼/콤보박스)에 대응하는지는
   미확인 — 값 3이 실제 로비에서 사람이 고를 수 있는 옵션인지, 아니면 디자이너/시나리오 전용
   내부값인지에 따라 "원본에서도 항상 이 상태"라는 결론과 "우리 자동화 로비 클릭이 잘못된 옵션을
   고른다"는 결론이 갈린다 — 원본 게임의 실제 로비 UI(사람이 직접, 또는 좌표를 넓게 스윕하며)에서
   `0x632d42`/`0x975914` 값을 관찰해 game_type==3이 사람이 선택 가능한 정상 경로인지 확인하는 것이
   다음 probe의 전제 조건이다.
3. `0xb631ec`, mode-indexed 테이블(`0x959af6` 기준)은 이 코드 범위에서 writer가 없다 — 다른 DLL/
   초기화 코드(0x800000 이후 등)에 있을 가능성, 미확인(비차단 갭, 게이트는 이미 `0x97597c` 경로로
   충분히 열렸으므로 이 lap의 결론에 영향 없음).

전문(probe-result.json, gdb 이벤트 로그, 캡처)은
`docs/history/laps/20260929_lap763_work_g5_minimap_router_gate_flag_confirmed.md` 참고.
