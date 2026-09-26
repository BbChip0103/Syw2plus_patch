# lap84 Luna G1-A input/dispatch chain probe

- date: 2026-09-11
- lap: 84
- goal: G1-A primary panel의 input-state read/branch와 action-dispatch sibling callee를 고정 원본에서 연결
- hypothesis: `0x0041E220`은 event queue를 소비한 뒤 input 좌표를 갱신하고, `0x00498F50`의 상태 처리와
  후속 `0x004A3700` queue sink가 같은 dispatch 흐름에 있을 것이다.
- changed files: `analysis/memory_maps/player_offsets.md`, `docs/STATUS.md`, 이 history 파일
- original/candidate: 원본 두 사본 SHA 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; candidate binary 없음
- fixture/input: 없음. production click, game run, source/tests/binary/fixture/좌표 변경 모두 SKIP.

## Evidence

원본은 PE32 Intel 80386이며 `.text` VA/raw는 `0x00401000/0x1000`, file offset 관계는
`VA-0x00400000`이다. 사용한 명령은 다음과 같다.

```text
sha256sum Syw2plus/syw2plus_original.exe /home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus/syw2plus_original.exe
file Syw2plus/syw2plus_original.exe
xxd -g1 -l16 -s $((VA-0x400000)) Syw2plus/syw2plus_original.exe
objdump -d -Mintel --start-address=... --stop-address=... Syw2plus/syw2plus_original.exe
objdump -d -Mintel Syw2plus/syw2plus_original.exe | rg 'call\s+0x(41e220|4217b0|498f50|4a3700)'
```

| entry / edge | exact evidence | interpretation boundary |
|---|---|---|
| `0x0041C81E→0x0041E220` | call bytes `e8 fd 19 00 00`; `41E220` old bytes `83 ec 20 53 55 bd 01 00 00 00 33 db 66 39 2d 88` | fixed outer input handler edge |
| `0x0041E220→0x004217B0` | callsite `41E299` bytes `e8 12 35 00 00`; `4217B0` old bytes `a1 70 e2 61 00 85 c0 0f 84 93 00 00 00 8b 44 24` | `[0x61E270]` count를 검사하고 `[0x61DA30..0x61DA3C]` event state를 caller buffer로 복사, ring shift/decrement, success `1` 반환 |
| `0x0041E220` state branch | `41E269→41D310`, `41E270→41D360`; `41D310`은 `[0x004E51DC]` 간접 poll에 codes `0x11/0x10/0x12`를 전달해 flags를 기록하고, `41E2A1` success branch 뒤 `41E2C7/41E2CE`가 `[0x004ED814]/[0x004ED816]`를 갱신 | input-state/coordinate flow는 확인. 간접 poll target의 더 좁은 의미는 미확정 |
| `0x0041E60C→0x00498F50` | `41E60C` old bytes `e8 3f a9 07 00 a0 fc 2f 89 00 84 c0 0f 85 56 01`; call 뒤 `[0x00892FFC]` test/branch | selection/table state 처리의 direct edge |
| `0x0041EB7A→0x004A3700` | `41EB75` bytes `b9 10 24 89 00 e8 81 4b 08 00`; `ecx=0x00892410`; `4A3700` old bytes `0f bf 81 9a 6b 00 00 0f bf 54 24 04 8d 04 40 89` | count `[ecx+0x6B9A]` 기준 세 인자를 queue record `+0x6B9C`, `+(count+0x8F8)*12`, `+0x6BA4`에 기록하고 count를 `<10`일 때 증가; command queue append side-effect |

## Result

- PASS: `0x0041E220`의 input queue read/branch와 좌표 갱신, `0x00498F50` 후속 state branch,
  `0x004A3700` command queue write/count 증가가 old bytes와 direct xref로 연결됐다.
- UNKNOWN/BLOCKER: `0x004E51DC` 간접 poll target, `0x008930A6/D6/BE/EE` field의 worker/production
  의미, 실제 사용자 입력과 runtime 결과는 증명하지 못했다. 이 결과는 G1 제품 합격·구현 승인·production
  dispatch 의미로 승격하지 않는다.
- 판정: **STATIC INPUT/DISPATCH CHAIN PASS; WORKER/PRODUCTION SEMANTICS UNKNOWN**.

## Next action

다음 새 Sol/Opus5/high가 이 문서와 원본 두 사본에서 old bytes, direct xref, queue write-set을
독립 재추출하고 worker/production 의미의 미확정 범위를 판정한다. 그 전에는 source/tests/binary,
fixture/좌표 변경과 game/production 실행을 하지 않는다.

## Validation

- `make check`: **127 passed**; Ruff, compileall, mypy, context check PASS.
- `bash checks/safety.sh check`: **SAFETY_PASS**.
- `make doctor`: setup `ok=true`, original `verified`; optional runtime은 manifest가 없어 실행하지 않았다.
