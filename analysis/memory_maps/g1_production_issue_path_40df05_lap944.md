# G1 — 생산 발행 경로와 queue witness 필드 (lap944, 2026-10-04)

- 대상: 보호 원본 `Syw2plus_re/Syw2plus/syw2plus_original.exe`, SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, image base `0x00400000`. 읽기만 했다.
- Method: capstone 5.0.7 선형 디스어셈블(공유 temp `20261004_lap944_strategy_review/scan.py`·`around.py`,
  출력 `production_issue_disassembly.txt` SHA256 `e3dfbb261fb89384dd857d0b20e0d36d289b2205881e9c7bf771f6d0bcbe6e35`).
  `.text`에서 `mov word [reg+0x290], 0x000F` 즉시값 패턴(`66 C7 8x 90 02 00 00 0F 00`)은 `0x40DF05` **1곳**이다.
  레지스터로 15를 쓰는 다른 경로가 없다는 전수 증명은 아니다.
- 다른 버전 EXE(ESL 2606/2608 등)에는 적용하지 않는다. 주소는 이 SHA에서만 유효하다.

## 1. 발행 순서 (`esi`=생산 건물 UnitStruct, `edi`→명령 descriptor 번호 word)

| 주소 | 코드 요지 | 의미 |
|---|---|---|
| `0x40DC19..0x40DC44` | `0x43ED40(player)` < `word [type*0x394 + 0x9B523A]`이면 메시지 `[0xB3B024]` 뒤 반환 | 쌀 부족 거부 |
| `0x40DCBB..0x40DCC9` | `0x43ED50(player)` < `word [type*0x394 + 0x9B523C]`이면 거부 | 나무 부족 거부 |
| `0x40DCE5..0x40DD2A` | `used[+0x200C] + [+0x1C] + word [type*0x394 + 0x9B5238] > cap[+0x2012]`이면 메시지 `[0xB3B034]` | 인구 초과 거부 |
| `0x40DDF5..0x40DE43` | `0x43F0C0(player; rice=spec+0x12, wood=spec+0x14, pop=spec+0x10)`, 반환 1이 아니면 `0x40DF58` | 비용 차감 |
| `0x40DE6F..0x40DE77` | `[esi+0x50C] = word [type*0x394 + 0x9B5238]` | 건물에 인구 비용 보관 |
| `0x40DF05` | `mov word [esi+0x290], 0xF` | **command = 15** |
| `0x40DF0E` | `mov [esi+0x1F8], 0` (`ebp`=0) | **progress = 0** |
| `0x40DF14..0x40DF21` | `eax = [descriptor*24 + 0x9E2F34]`; `mov [esi+0x320], eax` | **queue type = descriptor 표의 유닛 타입** |

- `type`은 모두 `[descriptor*24 + 0x9E2F34]`에서 온다. 타입 spec 표는 base `0x9B5228`, stride `0x394`
  (`eax*916`: `0x40DDFB..0x40DE0A`), 단어 필드 `+0x10` 인구·`+0x12` 쌀·`+0x14` 나무.
- player는 `0x956770 + owner*0x3ABC`(`owner = byte [esi+0x8E]`).

## 2. 비용 함수 `0x43F0C0(this=player, a1, a2, a3)` (`ret 0xC`)

| 주소 | 코드 | 의미 |
|---|---|---|
| `0x43ED40` | `mov eax,[ecx+0x14]; ret` | 쌀 읽기 |
| `0x43ED50` | `mov eax,[ecx+0x18]; ret` | 나무 읽기 |
| `0x43F0C5..0x43F0DF` | 나무 ≥ a2, 쌀 ≥ a1 아니면 0 반환 | 잔액 검사 |
| `0x43F0E9..0x43F0FE` | a3≠0이고 `used + [+0x1C] + a3 > cap`이면 0 반환 | 인구 검사 |
| `0x43F100..0x43F116` | `0x43EFB0(a1)`: 쌀 −= a1, `0x43F020(a2)`: 나무 −= a2 | 차감 |
| `0x43F118..0x43F11E` | `[esi+0x1C] += a3` | **`+0x1C` = 대기 중 생산이 예약한 인구, 발행 때 증가** |

## 3. 런타임 대조 (lap943 r4, 새 실행 없음)

- `pair-result.json` SHA256 `431951368f032cb5cbdf39419240731c8a6694d5a9a073abbc05a4da0dd5e0f2`, 재계산
  `20261004_lap944_strategy_review/recalculation.json` SHA256 `69f4d941437eb6ef40f8f1a4753544b4f4751da4b5b3273c41369f5515332073`.
- command 15인 건물(baseline tick 24646에 34개, candidate tick 24665에 35개)의 `+0x320`은 그 owner 진영 유닛 타입이다. 진영별 (건물 타입→queue 타입):
  진영1 `49→7`·`46→6`·`45→9`·`44→11`·`47→10`·`50→4`, 진영2 `53→14/37`·`55→16/111`·`59→13`·`60→3`·`61→8/17`,
  진영3 `64→24`·`65→22/88/109`·`67→108`·`71→36`. **타입 7은 진영1 건물 타입49의 생산물이다**(owner5 slot628, candidate에서는 slot1189도).
- owner0(진영2)의 타입58 건물 3개(slot 1163·1177·1199)는 클릭 전 두 lane 모두 `command 1 / +0x320 31 / progress 100`,
  owner0의 타입31 유닛은 14개다. 완료 뒤에도 `+0x320`과 progress 100이 남는다.
- candidate 클릭 `(668,540)` 뒤 slot1199: command 15, `+0x320` 31, progress 13, 쌀 −800, 나무 −300.
  `candidate/production.png`의 그 칸 툴팁은 `일본 농부 800 / 300 / 10`, 생산 표시는 `일본 농부 13%`다.
- HUD 인구 표시는 baseline `1893/2300` = used 1470 + `+0x1C` 423.
- 같은 창에서 `+0x1C`는 423→403이다. §2대로면 발행 순간 +10이므로 5.09초 창 안에 다른 생산 완료(owner0 건물 여러 개가
  88~94%)가 섞인 값이다. 발행 단계 하나만의 `+0x1C` 변화는 아직 관측한 적이 없다.

## 4. 미확인

- 타입31 spec의 실제 단어값(표는 BSS라 정적으로 못 읽는다. 툴팁 `800/300/10`이 대조값).
- 원본 lane에서 같은 클릭의 결과(lap943 r4 baseline은 클릭하지 않았다).
- 생산 완료 때 `+0x1C`·used를 쓰는 지점, descriptor 표 `0x9E2F34`와 화면 칸의 결합 위치.
