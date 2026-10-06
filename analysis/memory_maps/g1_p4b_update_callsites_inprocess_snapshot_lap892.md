# G1 P4b — sim update 함수 `0x41C770`의 호출 지점 (in-process 완료-phase snapshot 경계, lap892 strategy)

## 고정 입력과 한계

- 보호 원본 `Syw2plus/syw2plus_original.exe` SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  PE32 image base `0x400000`. 읽기만 했다(패치·실행 0).
- 명령: `sha256sum`, `i686-w64-mingw32-objdump -d -Mintel --start-address=… --stop-address=…`, Python `pefile.get_offset_from_rva`로
  아래 바이트 교차 확인. 주소·바이트는 이 SHA 전용이다.
- 이 문서는 정적 판독이다. 아래 경계에서의 실행 관측은 lap874·lap888의 GDB 진단(`0x41C961` return)뿐이고,
  호출 지점 wrapper 자체는 아직 실행된 적이 없다.

## 정적 사실

| VA | file offset | old bytes | 의미 |
|---|---:|---|---|
| `0x41C770` | `0x1C770` | `83 ec 08 e8 78 9c ff ff` | update 함수 진입. 스택 인자 없음, 진입 직후 레지스터 인자 사용 없음(첫 `ecx` 사용은 `mov ecx,0xc4b468`). |
| `0x41C81D` / `0x41C8A2` / `0x41C8BF` | `0x1C81D` / `0x1C8A2` / `0x1C8BF` | `c3` | tick store에 닿기 전의 return 3곳. |
| `0x41C8C9` | `0x1C8C9` | `a3 b8 24 89 00` | tick `[0x8924B8]` 저장(이 함수 안 유일한 tick store, `g1_p4b_tick_rice_writer_readonly_20261002.md`와 일치). |
| `0x41C961` | `0x1C961` | `c3` | 공통 출구. tick을 올린 경로가 여기로 나오고, tick store 앞의 `je/jne 0x41C95B` 조기 탈출 5곳(`0x41C7CD`·`0x41C7FB`·`0x41C826`·`0x41C873`·`0x41C880`)도 tick을 올리지 않은 채 여기로 나온다. lap874·lap888이 GDB all-stop으로 관측한 지점. |
| `0x4245D2` | `0x245D2` | `e8 99 81 ff ff` | `0x4245D0` 안의 `call 0x41C770`. 반환 뒤 `[0xB93E00]==0`이면 `0x41BF20`(캐시→화면)으로 간다. |
| `0x4250F7` | `0x250F7` | `e8 74 76 ff ff` | 두 번째 `call 0x41C770`(`[0xB93960]==1` 또는 `[0xB93964]==1` 조건). 어떤 모드의 루프인지는 읽지 않았다. |

- 전체 `.text`에서 `call 0x41c770`은 위 두 곳뿐이다(objdump 전수 grep). 간접 호출 여부는 확인하지 않았다.
- tick을 올리는 경로는 `0x41C81E`에서 시작해 tick store 앞에서 `0x41E220`·`0x41C970`·`0x4324E0`을 부르고, 조건에 따라
  `0x41D020`·`0x41F5F0`·`0x48EC30`·`0x4AE800`도 부른다. 이 함수들이 sim 상태를 쓰는지는 읽지 않았다. tick store 뒤에는
  `0x41CB40`(player 처리) 등이 이어진다. 따라서 "tick 값이 바뀐 직후"는 update가 진행 중인 때이고, host가 tick을 보고 읽는
  방식으로는 호출이 끝난 시점을 잡을 수 없다.

## 결론과 증명되지 않은 것

- `call 0x41C770`이 반환했고 그 호출 동안 tick이 바뀌었다면, 그 시점은 tick을 올린 경로의 `0x41C961` return 직후와 같은 지점이다
  (ret과 호출 지점 다음 명령 사이에 실행되는 원본 코드가 없다). `0x41C961` 도달만으로는 tick이 올랐다고 볼 수 없으므로
  wrapper는 호출 전후 tick을 비교해야 한다.
- 미증명: 다른 스레드의 sim 상태 쓰기 부재(lap874는 owner6 쌀 write가 thread 1뿐임을, lap888은 all-stop census를 관측했을 뿐이다),
  `0x4250F7` 경로의 실제 사용 여부, wrapper 설치 뒤의 동작. 이 주소를 제품 동기화 경계로 승인한 것이 아니다.
- snapshot 대상(기존 `tools/g1_saved_scene_probe.py:_read_batched_scene`가 읽는 것과 같은 범위): program state `0x4ED818`(4),
  tick `0x8924B8`(4), camera `0xB42D7C`(8), player `0x956770`(8×`0x3ABC`), exists `0x8990C8`(1200×2), unit pool `0x66B790`(1200×`0x758`).
