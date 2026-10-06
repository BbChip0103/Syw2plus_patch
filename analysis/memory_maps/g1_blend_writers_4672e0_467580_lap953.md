# G1 — 미후킹 반투명 RLE writer 0x4672E0 / 0x467580 (lap953, 2026-10-04)

- 대상: 보호 원본 EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (image base `0x400000`, `.text` `0x401000..0x4E4AE5`). 읽기만 했다. 주소는 이 SHA에서만 유효하다.
- 방법: lap951 residual 장치 위에 opt-in 하드웨어 쓰기 watchpoint(`SYW2_G1_CENSUS_WATCH=x,y`)를 얹었다.
  PS3 첫 present(source Lock 구간)에서 render thread DR0(RW=01 쓰기, LEN=0 1바이트, DR7 `0x10001`)를
  present source buffer의 해당 픽셀 주소에 걸고, VEH가 hit마다 EIP·레지스터·EIP 앞 24바이트·스택 `.text`
  주소를 기록한다. Wine 9.0에서 DR 설정·hit 모두 동작(자체 시험 `selftest hits=1 PASS`, 전용 byte 사용·게임
  buffer 무기록). 데이터 breakpoint는 쓰기 **뒤** 트랩이라 EIP = 쓰기 명령 다음 주소.

## 1. 포획 결과 (공유 temp `20261004_lap953_watch_w2`, `…_w5`)

| 픽셀 | EIP | hook 안 | hit | 소속 함수 | 의미 |
|---|---|---|---|---|---|
| 로고 (782,380) | `0x4662DE` | block_copy `0x466280` 안 | 63 | hook writer | 지형 캐시 복사(기존 hook) |
| 로고 (782,380) | **`0x4673D3`** | 아니오 | 63 | **`0x4672E0`** | **미후킹 반투명 writer**, present 2~64 매 프레임 1회 |
| 과도 (223,279) | `0x4662DE` | block_copy 안 | 63 | hook writer | |
| 과도 (223,279) | **`0x467692`** | 아니오 | 5 (present 2~6) | **`0x467580`** | **미후킹 반투명 writer**, 초기 효과 구간만 |
| 과도 (223,279) | `0x46659F` | rle_tinted_clip 안 | 48 | hook writer | present 17~ |

각 픽셀의 미후킹 EIP는 위 한 곳씩(분산 없음). 로고 w2 run: 126 hit = 63 present × 2, distinct EIP 2.

## 2. 0x4672E0 (thiscall `ecx=renderer`, `ret 0x14`)

- 인자(스택 word 부호확장 `movsx`): `x`, `y`, `width`, `height`, RLE data 포인터. 호출자가 상위 word를 0으로
  두지 않는다(실측 args `[700,377,589924,75169856,0x047BF3A8]` = width `0x90064`→100, height `0x47B0040`→64).
- RLE: 제어 바이트 `0xFE`=건너뛰기(다음 바이트만큼 열 증가), 그 외 = 소스 팔레트 인덱스.
- 본체(`0x46734D..0x4673CF`): 목적지 픽셀 `dl=[dst]`와 소스 인덱스의 RGB 채널을 renderer 팔레트 표
  `renderer+0x419A0 + idx*3`(채널 3개, `0x2BBC0+0x15DE0`)에서 읽어 채널별 `(d>>1)+(s>>1)`(**50% 평균**),
  `<<6` 누적한 18비트 값을 renderer 역 LUT `renderer+0x19A0`(크기 `0x40000`, `0x419A0`에서 끝)에서 조회해
  `mov [edi+ecx-1], dl`(`0x4673CF`)로 목적지에 쓴다.
- 즉 **목적지 의존(destination read) 50% 반투명 RLE 스프라이트**다. 로고(x700, y377, 100×64)를 매 프레임 그린다.
- 프롤로그(핀): `51 53 56 8B F1 57` (`push ecx/ebx/esi`, `mov esi,ecx`, `push edi`) 6바이트.

## 3. 0x467580 (같은 계열, `ret 0x14`, 인자 순서 동일 추정)

- 프롤로그(핀): `51 0F BF 54 24 0C` (`push ecx`, `movsx edx,word [esp+0xC]`) 6바이트. `y`를 `[esp+0xC]`, `x`를
  `[esp+8]`에서 읽는 것까지 디스어셈블로 확인(인자 5개 `ret 0x14`).
- 본체는 채널별 평균 대신 renderer `+0x41CA0`의 16비트 가중표(`movsx word`)로 채널 값을 변환한 뒤 같은 LUT
  `renderer+0x19A0`을 조회하고 `mov [edi+edx-1], al`(`0x46768E`)로 쓴다 → **가중 반투명(톤/혼합) RLE 변형**.
- 포획된 호출은 PS3 present 2~6(초기 효과)뿐이다.
- 같은 군의 다른 함수 `0x467410`(`ret 0x1C`, 7인자 clip 변형 추정), `0x4676D0`은 이번 포획에서 hit가 없어
  후킹하지 않았다. 존재만 기록한다.

## 4. 한계

- 위 분석은 정적 디스어셈블(`objdump`)과 watchpoint hit 레지스터로 확인한 것이다. `0x467580`·`0x4672E0`의 모든
  호출자와 다른 translucent 변형(`0x467410`·`0x4676D0`)이 다른 장면에서 쓰이는지는 미확인이다.
- 한 픽셀당 watchpoint라 같은 present의 다른 미후킹 writer를 전수 증명하지 않는다. 전수 근거는 shadow 비교의
  잔여 수치(lap953 기록)다.

## 5. lap954 middle 독립 확인 (read-only objdump, 같은 EXE SHA)

- 프롤로그·쓰기 명령·`ret 0x14`·word `movsx` 인자 읽기를 다시 디스어셈블해 위 서술과 일치함을 확인했다.
- 보강: `0x467580`의 표 `renderer+0x41CA0`은 채널마다 `(목적지 채널<<6)+소스 채널`로 색인하는 **2차원 64×64 16비트 혼합표**다.
  세 채널 결과를 `(t0<<12)+(t1<<6)+t2`로 묶어 같은 역 LUT `renderer+0x19A0`을 조회한다.
- 기준1 분류: 두 writer 모두 명시 잔여 P6(혼합표/LUT). 근거 `docs/work/active/G1_MIDDLE_W70_BLEND_P6_ACCEPTANCE_HD_COVERAGE_P5MENU_HANDOFF_LAP954.md` §2.
