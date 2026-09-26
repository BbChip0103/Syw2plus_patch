# 전비 상한 공식 `1500 + 200×장수` — **런타임 오라클로 확인** (2026-09-06)

## 요약

`supply_limit`(PlayerStruct `+0x2012`)은 상수가 아니라 **살아있는 장수 수의
함수**다.  레포는 이 공식을 지금까지 **개조판 EXE 의 상수 diff** 로만 유도해
왔는데(순환하지 않지만 간접적), 이번에 **기준판 원본 런타임 캡처**가 같은
공식을 직접 확인했다.

## 근거 ① 원본 함수 (기존, `[바이너리 확인]`)

`0x0043FE9E` / `0x0043FFD4` — 한 함수 안에서:

```
살아있는 장수 루프: add ecx, 200        ; 장수 1 기당 +200
루프 뒤          : add eax, 1500        ; 기본치 1500
                   mov WORD [ebp+0x2012], ax
```

## 근거 ② 개조판 상수 diff (기존, 간접)

`조선의반격 ESL 2503 (장수7명+최대2600).exe` 가 **정확히 그 두 자리**를
`100`/`1900` 으로, 장수 상한 비교 4 곳을 `7` 로 바꾼다
⇒ `1900 + 100×7 = 2600` (파일명과 일치).

## 근거 ③ ⭐**기준판 런타임 캡처** (신규, 이 문서)

캡처: `plan_c/verification/captures/original/`
`free_battle_player_resources_ming_joseon_0906/player_resources.json`
(`enter_custom_game + _custom_game_chain_inject_ming_joseon`, 명 vs 조선)

| t(s) | 명 `+0x2012` | 조선 `+0x2012` | ⇒ 유도 장수 수 |
|---:|---:|---:|---:|
| 0 | 1500 | 1500 | 0 |
| 30 | 1500 | 1500 | 0 |
| 60 | 1500 | 1500 | 0 |
| 120 | 1500 | 1500 | 0 |
| 300 | 1500 | 1500 | 0 |
| **600** | **2100** | **2100** | **3** |

`(limit - 1500) / 200` 이 **전 표본에서 음이 아닌 정수**로 떨어진다.
⇒ `kInitialSupplyLimit = 1500`, `kSupplyPerLivingHero = 200` 확인.

## ⭐부산물 — **장수 수 오라클**이 공짜로 생겼다

`+0x2012` 은 `+0x200E`(건물)·`+0x200A`(로스터)와 같은 캡처에 들어 있으므로,
**장수를 직접 세지 않고도** 진영별 살아있는 장수 수를 읽을 수 있다:

> 원본 명·조선 모두 **t=300s 에 0 기, t=600s 에 3 기**.

⇒ 장수는 **300~600 초 구간(frame ≈ 7,350~14,720)**에 처음 나타나고,
600 초까지 **양 진영 각각 3 기**다.  이는 기존 연구 오라클
([[original-research-completion-oracle]]: 「장수는 연구 완료 +550~1200 프레임」)과
독립적으로 얻은 값이며, 서로 모순되지 않는다.

⚠ `kMaximumSupplyLimit = 2500` 은 여전히 **유도값**(`1500 + 200×5`)이고
이 캡처는 3 기까지만 도달하므로 상한 자체를 확인하지는 못했다.

## 주의

* 캡처는 `forced_seed: false` — 절대 수치의 수용 기준으로 쓰지 말 것.
  공식의 **형태**(정수 배수 관계)와 **장수 출현 구간**만 읽는다.
* 시각축: 원본 600 초 ↔ plan_c 24,000 틱(40 tick/s).

## 관련

* `plan_c/src/game/economy.h` — `kInitialSupplyLimit` / `kSupplyPerLivingHero`
* `plan_c/tests/test_hero_supply_contract_located_0906.py` — 기존 회귀
* `analysis/memory_maps/player_offsets.md` — PlayerStruct 필드표
* [[building-census-axis-is-flag2-roster]] — 같은 캡처의 `+0x200A`/`+0x200E` 축
