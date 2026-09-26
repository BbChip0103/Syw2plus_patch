# 2026-09-16 — G3 16인 빠른 가능성 판정

- 대상 original SHA `b56986e0…08a8ac`; 새 `tools/g3_player16_boundaries.py`는 PE32 `.text` decoded operand와 exact bytes만 읽고 binary writer/game run이 없다.
- PlayerStruct base `0x956770`, stride `0x3ABC`, 기존8개 end `0x973D50`;16개 end `0x991330`. 원본 bulk save `[0x892410,0x975D8C)`보다 **`0x1B5A4`=112,036B 초과**하므로 table count/loop만16으로 바꿔도 9~16번 PlayerStruct는 현재 bulk format에 저장되지 않는다.
- `FUN_0043EBC0` exact bytes는 player index를 byte `+1/+5`에 저장하고 `mov dl,1; shl dl,cl; mov byte ptr [eax+3],dl`로 self mask를 만든다. owner8..15에서 8-bit 결과는0. `+4` opponent mask도 기존 정적 근거상 byte이며 다른 team player의 `1<<index` OR라 같은 폭을 넓히고 모든 consumer를 수리해야 한다.
- decoded 후보는 player base191, stride30, original-end8, target-end0. immediate8은2795개로 stack size/flag 등 noise가 대량 포함돼 player loop 증거로 사용할 수 없다. table relocation, mask widening consumers, lobby/start/win/AI, save version, LAN protocol 모두 UNRESOLVED.
- **판정:** 16인은 PlayerStruct 추가 메모리 약0.115MiB 때문에32-bit에서 절대 불가능한 것이 아니다. 그러나 **상수-only/로비 슬롯-only patch는 NO-GO**이며 table relocation+mask schema+저장/LAN을 함께 바꾸는 침습 확장만 조건부 후보다. 현재 실행 활성화/제품 가능 주장은 금지한다.
- evidence `tools/g3_player16_boundaries_evidence.json` SHA `ba6fa0faf0c5d5a6333a7ec0c123db35fca550ce0d3c10d198e9a3d66b3d4500`; targeted4/Ruff/mypy PASS, original SHA 무변경.
