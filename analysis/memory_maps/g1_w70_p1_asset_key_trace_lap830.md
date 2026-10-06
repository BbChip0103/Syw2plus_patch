# G1 W70 P1 asset-key runtime trace — lap 830

- 목표: protected original의 `FUN_00435400` `(tile file, frame)`가 실제
  `FUN_00468C30` 계열 source pointer와 같은 table 식을 쓰는지 fresh runtime에서 확인한다.
- 원본 SHA-256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- fixture: 비합성 `save006.dat`, SHA-256
  `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`.
- 격리: private full game copy, private Wine32 prefix, private Xvfb `1600x1200x24`;
  실행 후 game copy와 prefix processes를 정리했다. 원본/EXE는 쓰지 않았다.

## Static contract

원본 disassembly의 `0x435568..0x435593` 및 clipped/fog branches를 기준으로

```text
index  = file * 0x2FE + frame
source = u32(0xB65E8C + file * 0xBF8)
         + u32(0xB65758 + index * 4)
```

을 trace에서 독립 계산했다. `0x435593`, `0x4355D7`, `0x43561E`, `0x435662`의
source push도 기록했다.

## Fresh runtime result

명령:

```text
PYTHONPATH="$PWD" python3 tools/g1_saved_scene_probe.py \
  --runtime-root local/runtime/g1_w70_lap830_asset_key \
  --artifact-root ../temp/Syw2plus_patch/g1_w70_lap830_asset_key \
  --census-only --terrain-trace
```

원본 key event 256건(고유 `(file,frame)` 25, 비0 key 247), blitter call 1061건을
관측했다. 모든 call이 `table_equality=true`였고 false/unknown은 0건이다. 동일 key/source의
반복 digest 변형은 0건이며, 모든 이벤트는 PS3에서 실행됐다. renderer buffer는 전부
`0xBA3D30`(stride 832, height 600)으로 관측됐다. fixed terrain watchpoint write는
3건이며 원본 buffer와 연결됐다.

`RIGHT` 실제 키 입력은 수행됐으나 save006의 해당 위치에서 카메라가 변하지 않았다.
probe의 기존 fallback인 `DOWN`이 `[158,101] -> [159,102]`를 만들었다. 따라서 카메라 변화는
확인했지만 RIGHT 단독 이동 성공으로 주장하지 않는다.

raw:

- writer events: `../temp/Syw2plus_patch/g1_w70_lap830_asset_key/census/terrain-trace/writer-events.jsonl`
  SHA-256 `95376b920c09200e261af60aff31db7fc101dac0f8e1b1d6796233cb7bc02f2a`
- census: `../temp/Syw2plus_patch/g1_w70_lap830_asset_key/census/census_raw.jsonl`
  SHA-256 `ebf43a1dc51e96935d1db614f553a171afec7441c728f600c589fd4f5dd15fd2`
- probe result: `../temp/Syw2plus_patch/g1_w70_lap830_asset_key/census/probe-result.json`
  SHA-256 `5de9c0cd84335d45768f9ebc8307d90a3ca594f30a9e686a31c8c9ca7f0d6455`

판정: `P1 asset-key mapping PASS(partial)`. 이 결과만으로 W70/Scale2x/GDI 구현이나 G1
완료를 선언하지 않는다.
