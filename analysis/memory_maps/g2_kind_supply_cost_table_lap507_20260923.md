# kind별 보급비(`used` 가산량) 표 + crowd 채널 주소 정정 — lap507 W29

- 작성: 2026-09-23, lap507, work(Claude Code claude-sonnet-5/high)
- 카드: `docs/work/active/G2_Q8_USED_CEILING_QUANTIFICATION_LAP505.md`(W29, lap505 strategy 발행,
  `ESCALATE_SOL` §67). 실행: lap506이 작성하고 background+세션종료로 죽은
  `w29_ceiling_run.py`를 **수정 없이** lap507이 실행(원본 script는 lap506 산출물 그대로,
  이 문서만 신규).
- 범위: **읽기 전용 런타임 read.** AI/생산 로직 변경 0 · 원본/후보 바이트 변경 0 · 게임 신규
  실행 1회(§0 조건: lap502가 owner5만 봤고 8 owner 전원의 건물 집합이 필요해 재생 허용).

## 1. 주소/스트라이드

- `TYPESPEC_BASE = 0x009B5228`, `stride = 0x394`(916, lap501이 `lea` 사슬 9→19→57→229·`shl 2`로
  바이트 확정).
- **보급비(`cost`, `used`에 가산되는 값) = `TYPESPEC_BASE + kind*0x394 + 0x10`**
  (`analysis/memory_maps/supply_200c_accumulation_rule_0726.md`가 이미 확정한 site와 동일 레코드).
- **`crowd_flat_flag` = `TYPESPEC_BASE + kind*0x394 + 0x4C`** (lap504 N147이 제기한 정정 후보,
  이 lap이 런타임 값으로 재확인 — 아래 §3).
- 참고: `+0x24` 플래그(dword, G-7 크라우드 검사 적용 여부 비트) · `+0x28` 진영 · `+0x32` 비율상한
  · `+0x34` typemax_default는 `ai_production_decision_path_00406770_20260923.md` §4 그대로.

## 2. 부분 실측 정합 확인 (카드 §1 채택 조건)

lap502 tick14,624에서 owner5 `used`가 1050→1070으로 **+20** 증가했고, 그 시점 발주된 kind는
27과 76 둘 중 하나였다(원시가 어느 것인지 특정하지 못했었다). 이번 lap이 읽은 값:

| kind | cost(보급비) |
|---|---|
| 27 | 20 |
| 76 | 0 |

**`cost[27] + cost[76] = 20`** — lap502 관측과 정확히 일치(`partial_evidence_check.json`,
`sum_27_76_matches_20: true`). 또한 lap504 N148의 tick16,794 kind80 생산이 `used` **불변**이었던
관측도 `cost[80] = 0`과 정확히 일치(`kind80_matches_0: true`). 두 조건 모두 채택 기준을 충족한다.

## 3. crowd 채널 주소 정정 결과 (카드 §2, N147 후속)

lap502가 읽은 `0x009B5274 + kind*4`(flat array 가정, stride 4)는 kind 0~199 **전부 0**이었다
(N147). 이번 lap이 같은 리터럴 `0x9B5274`를 `TYPESPEC_BASE(0x9B5228) + 0x4C`로 재해석해
**stride 0x394**로 다시 읽은 결과:

- 65개 생산 kind 중 **65개 전부 0이 아니다**(전체 200-kind 범위에서도 110/200 nonzero).
- 예: kind2=4259845, kind6=35783701, kind76=1114117, kind80=1114117 (전문은
  `temp/Syw2plus_patch/g2_capacity/20260923_lap506_w29_used_ceiling/type_specs.json`).

**결론(신중하게 기술): 주소 정정 자체는 지지된다** — flat-array 가정(전부 0)과 달리 이 주소는
kind마다 다른 비퇴화 값을 낸다. **그러나 이 dword가 `FUN_00406B00`의 G-7(11×11 밀집 검사)
적용 여부와 어떻게 연결되는지는 여전히 디코딩하지 못했다** — `ai_production_decision_path`
§3이 확정한 G-7 게이트는 **정적 표 조회가 아니라 매 dispatch마다 유닛 풀을 스캔하는 라이브
카운트**이고, `+0x24`의 비트(`0x4`/`0x400`)가 그 스캔을 실행할지만 결정한다. `+0x4C`의 값이
무엇을 인코딩하는지(플래그 비트 집합? 다른 표의 포인터/오프셋? 단순 미사용 패딩?) 이 lap은
밝히지 않았다. **H-CROWD는 여전히 UNKNOWN으로 유지한다** — 카드 §2가 명시한 대로 "정정 후에도
평가 불가면 UNKNOWN 유지"를 그대로 따른다. 이 dword는 이번 천장 계산(§4)에 쓰이지 않았다
(천장 공식은 `typemax_eff × cost`뿐이며 crowd와 무관).

## 4. 8 owner 천장 표 (카드 §3, 종단 tick 24,029)

원시: `temp/Syw2plus_patch/g2_capacity/20260923_lap506_w29_used_ceiling/ceiling_table.json`,
`run_summary.json`. 후보 SHA `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`,
원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(불변, 실행 전후 확인).

| owner | 건물 수 | 건물 종 수 | 생산 kind 수 | Σtypemax_eff | 천장(Σtypemax×보급비) | 천장/5000 | `used`(종단) |
|---|---|---|---|---|---|---|---|
| 0 | 10 | 8 | 19 | 181 | 2445 | 48.9% | 1708 |
| 1 | 8 | 6 | 15 | 132 | 1070 | 21.4% | 1035 |
| 2 | 11 | 8 | 19 | 181 | 2445 | 48.9% | 1583 |
| 3 | 9 | 7 | 17 | 168 | 2050 | 41.0% | 1536 |
| 4 | 10 | 8 | 19 | 181 | 2445 | 48.9% | 1523 |
| 5 | 7 | 7 | 17 | 150 | 1190 | 23.8% | 1070 |
| 6 | 10 | 7 | 17 | 168 | 2050 | 41.0% | 1386 |
| 7 | 10 | 8 | 19 | 181 | 2445 | 48.9% | 1376 |

(전문 kind별 기여도는 `ceiling_table.json`의 `per_kind` 배열에 owner별로 그대로 있다.
owner5는 lap504 추정 ≈2,030(평균 보급비 13.5 기반)과 대조해 **실측 1,190** — 추정 대비
**−41%**, 평균 보급비 가정이 실제(kind0~39는 10~65, kind75~111 다수는 0)보다 과대추정이었다.)

- **k(천장<5,000인 owner 수) = 8/8.**
- 전체 65종(현재 owner가 못 지은 건물 포함) Σtypemax=568, 이론 최대 = **8,077**
  (`typemax_default × cost` 전 kind 합, override_selector=0이라 override 미적용).

## 5. 사전 고정 판정식 적용

카드 §3: k=8 ⇒ `NATURAL_ARRIVAL_ARITH_INFEASIBLE`(현 종단 건물 구성 기준) + 이론 최대 병기 필수.

**k=8 확정.** 단, 명시할 단서(카드가 요구):
- 이것은 **이 fixture의 tick24,029 종단 건물 구성** 기준이다. 8 owner 전원이 실제로 지은
  건물(7~11채, 8~19종 kind)만으로 계산했다.
- **건물을 더 지을 수 있었다면?** 이론 최대(전체 65종 다 지음)는 **8,077 > 5,000** —
  즉 "표 값이 절대적으로 5,000 도달을 막는다"는 아니다. 현재 각 owner는 27종 생산건물 중
  7~11종만 보유해 이론 최대의 15~30%만 도달했다. **AI가 이 fixture(24k tick, 140×140,
  8 AI)에서 스스로 더 많은 생산건물을 짓지 않는 것**(건물 계층 부재 또는 건설 AI의 별도
  판단)이 실제 병목이지, "표 값 자체가 수학적으로 5,000을 불가능하게 만든다"는 과대해석이다.
  이 구분은 `docs/work/active/G2_Q8_USED_CEILING_QUANTIFICATION_LAP505.md` §3이 요구한 것과
  같다.

## 6. 이 문서가 주장하지 않는 것

- H-CROWD 게이트의 실제 동작 여부(§3, UNKNOWN 유지).
- "건물을 더 지었다면 5,000에 닿았을 것"이라는 것 — 이론 최대가 5,000을 넘는다는 산술적 사실만
  보인다. AI가 실제로 더 지을 수 있는지(길찾기/자원/AI 판단)는 이 lap이 조사하지 않았다.
- 어떤 AI/생산 로직 변경도 착수·제안하지 않는다 — (ㄴ)은 여전히 사용자 전결이다.
