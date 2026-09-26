# G4 AI controller live observation (2026-09-16)

## 런타임 관측

`PlayerStruct +0xD32/+0xD34`를 각각 controller opcode/argument로 fresh sample에 추가했다.
seed7 고정 fixture 30초/15 sample에서 owner1은 다음 nonzero 상태를 보였다.

- tick 412: opcode 18, argument 101.
- tick 545: opcode 18, argument 101.
- tick 812: opcode 1, argument 3.
- nonzero samples 3, sampled transitions 6, observed opcodes `[1,18]`.

raw/summary는
`temp/Syw2plus_patch/g4_ai/20260916_135558_2145300_0_seed7_opcode30/`에 있고,
summary SHA는 `8031abc00be17a25ae8538e5c1175c4d8b1a23cf245f80bfc75cb099e15accb5`다.

## 정적 경계

원본 `FUN_0043F5D0`은 `+0xD32`가 0일 때 RNG `%20`으로 opcode를 선택하고 같은 함수
후반 switch에서 handler를 dispatch한다. 원본 PE에 cadence compare가 직접 존재한다.

| VA | bytes | threshold |
|---|---|---:|
| `0x43F7F7` | `3D E8 03 00 00` | 1000 |
| `0x43F880` | `83 F8 64` | 100 |
| `0x43F8B6` | `3D C8 00 00 00` | 200 |
| `0x43F922` | `3D D0 07 00 00` | 2000 |
| `0x43F9CC` | `3D C8 00 00 00` | 200 |
| `0x43FA94` | `3D D0 07 00 00` | 2000 |
| `0x43FAF6` | `3D DC 05 00 00` | 1500 |

따라서 AI intervention point가 전혀 없다는 blocker는 해소됐다. 다만 임계값 하나를 낮추면
LCG draw/cadence와 handler 빈도가 바뀌어 LAN 결정성 및 경제/공격 전반을 동시에 흔든다.
현 단계에서는 byte patch를 활성화하지 않는다. 다음 gate는 동일 seed에서 opcode full trace를
두 번 비교하고, 단일 threshold 후보마다 rollback byte·행동 metric·LAN 위험을 명시하는 것이다.
