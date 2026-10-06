# G1 — 미후킹 writer 0x466070 (클립 rect fill) / 0x466B50 (좌우반전 리맵 RLE) (lap974, 2026-10-05)

- 대상(lap975 middle이 `0x466B50` 반환을 `ret 0x18`로 정정, §3): 보호 원본 EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (image base `0x400000`). 읽기만 했다. 주소는 이 SHA에서만 유효하다.
- 방법: lap953 hardware 쓰기 watchpoint에 opt-in `SYW2_G1_CENSUS_SKIP_PRESENTS=300`(probe `--census-skip-presents 300`)을
  더해 census 64 present 창을 PS3 서수 301~364로 미뤘다(기본 0=byte 동일 경로). 두 run 모두
  `--census-only --census-residual`, selftest hits=1 PASS, `watch_armed present=301`, 창 끝까지 64 present.
  lap973이 지목한 두 stale 덩어리(서수 6~34에서 0px, 300부터 존재)의 픽셀을 각각 감시했다.

## 1. 포획 결과 (공유 temp `20261005_lap974_work_delayed_watch/{hp,unit}/census/census_raw.jsonl`)

| 픽셀 | 덩어리 | EIP | hook 안 | hit | 소속 함수 | 의미 |
|---|---|---|---|---|---|---|
| (442,155) | 선택 HP 바(423px) | `0x004662DE` | block_copy `0x466280` 안 | 63 | hook writer | 지형 캐시 복사(기존 hook) |
| (442,155) | 선택 HP 바 | **`0x00466114`** | 아니오 | 63 (50%) | **`0x466070`** | **미후킹 클립 rect fill**, present 302~364 매 프레임 1회 |
| (701,237) | 유닛 덩어리(961px) | `0x004662DE` | block_copy 안 | 63 | hook writer | |
| (701,237) | 유닛 덩어리 | **`0x00466BB3`** | 아니오 | 63 (50%) | **`0x466B50`** | **미후킹 좌우반전 리맵 RLE**, 매 프레임 1회 |

각 픽셀의 hook 밖 EIP는 한 곳씩(분산 0, distinct EIP 2, overflow 0). 두 run raw SHA256: hp
`61bb4a1db7df9f2c5ba01010cf6641421a00521dbba90741b5b7742f1ccc36a1`, unit
`70c29c80d1d58e0c73bc5702b343f832924606b9596fbe8db6f82764463e701f`. 데이터 breakpoint는 쓰기 **뒤** 트랩이라
EIP = 쓰기 명령 다음 주소.

## 2. 0x466070 (`ret 0x14`, thiscall `ecx=renderer`) — 클립 rect fill

- 진입 `0x466070`: `8B 44 24 04 53 55 56 57 8B 7C 24 1C`. 앞은 `ret 0x14`+nop(`0x466069..`), 끝 `ret 0x14` `0x466127`.
- 인자 5개: x1,y1,x2,y2(양끝 포함, 뒤집힌 쌍은 정렬)·색 1바이트(`[esp+0x24]`). 클립 사각형 `renderer+0x4D0/4D4/4D8/4DC`로 자른다.
- 쓰기 루프 `0x466100..0x466114`: `mov [ebx+ebp], dl`(`ebp=[renderer+0x1514]` 프레임 base, `ebx=y*pitch+x`)가 행마다 연속. 그 직후
  `jle`이 EIP `0x466114`다. 기존 hook `rect_fill 0x465E80`(`8B 41 10 53 55 …`)과는 **다른 함수**이고 census/mirror 대상이 아니다.
- HP 바 = 단색 상자(선택 유닛 체력 칸). census 표에서 이 픽셀이 block_copy로 귀속된 것은 last-writer 표가 이 함수를 못 봐서다.

## 3. 0x466B50 (**`ret 0x18`**, thiscall `ecx=renderer`) — 좌우반전 리맵 RLE

> **lap975 middle 정정(EXE 직접 역어셈블):** 이 함수의 끝은 `0x466BD4: C2 18 00`(`ret 0x18`, 인자 6개)이다.
> lap974가 적은 `ret 0x1c`·인자 7개는 **앞 함수**의 끝(`0x466B4A`)을 옮겨 적은 전사 오류다. 인자 순서(push 뒤
> `[esp+0x14..0x28]`): x, y, width(`ebx`), height(행 수), RLE source(`ebp`), 리맵 LUT(`ecx`) — 기존 tinted RLE
> `0x466EA0`/`0x466540`과 같은 6인자 배치. **클립 없음**: 대상은 `[x, x+width) × [y, y+height)`이고 각 행을 오른쪽 끝
> `x+width-1`부터 왼쪽으로 쓴다. prologue 8바이트 `51 53 56 57 8B 7C 24 18`은 `rle_tinted_clip 0x466540`과 byte 동일
> (5바이트 경계가 명령 중간이라 8바이트 steal 필요). 호출 지점 2곳 `0x419F50`·`0x41A4FA`(후자는 `0x41A4B0` 안,
> `mov ecx,0xE5BF18` 뒤 call → `ret`, 그 래퍼는 `0x478A07`·`0x47A66B`에서 호출).
> `0x466070` 쪽은 `ret 0x14`·5인자·5바이트 prologue `8B 44 24 04 53`(명령 경계 정확)로 lap974 기록과 일치하고,
> 호출 지점은 8곳 `0x403EC0`·`0x433E34`·`0x4367DE`·`0x43686E`·`0x47903F`·`0x47916C`·`0x479231`·`0x47936B`
> (HP 바 포획 스택 첫 값 `0x479044` = `0x47903F` call의 복귀 주소). 근거: 공유 temp `20261005_lap975_middle_review/`
> `disasm_lap975.py`·`xref_lap975.txt`.

- 진입 `0x466B50`: `51 53 56 57 8B 7C 24 18 0F AF 79 10`. 앞 함수의 끝이 `ret 0x1c`+nop(`0x466B4A..`).
- 인자 6개(`ret 0x18`, 위 정정). 본체: RLE 제어 바이트 `0xFE`=건너뛰기(다음 바이트만큼 `edx` 증가), 그 외 = 소스 인덱스,
  `al=[eax+ecx]`(`ecx`=인자 리맵 표)로 변환한 뒤 `ebp=edi-edx`(오른쪽→왼쪽)에 `mov [ebx+ebp-1], al`(EIP `0x466BB3` 직전 명령).
- 기존 hook `rle_clip 0x466D50`/`rle_plain 0x4664D0`/`rle_tinted_clip 0x466540`/`rle_tinted 0x466EA0`와 **다른 함수**,
  mirror 대상 아님. 팀 색 리맵 + 좌우반전 → 유닛 스프라이트(수레 한 개)로 보이는 유닛 덩어리와 일치한다.

## 4. 한계

- 픽셀 1개씩의 표본이다. 유닛 덩어리 961px 전체/HP 바 423px 전체가 이 두 함수만으로 설명되는지는 호출 사각형 기록
  (H-T 방식의 호출 전후 비교)으로 다음 work가 확인한다. 유닛은 애니메이션이라 다른 프레임·방향 변형 함수가 더 있을 수 있다.
- 두 hook 밖 EIP는 각각 정확히 63/126(=50%)이다. 사전등록은 ≥50%(같은 EIP 비율)이고 나머지 50%는 block_copy hook 안의 같은 present
  선행 쓰기다. 즉 present당 "캐시 복사 → 미후킹 writer 덮어쓰기" 한 쌍이다.
